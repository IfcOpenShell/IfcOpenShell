/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "LengthMeasurement.h"

#include "OverlayRenderer.h"

#include <QDebug>
#include <QStringList>
#include <QtGlobal>
#include <QtMath>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <limits>
#include <queue>
#include <unordered_map>
#include <unordered_set>

namespace {

double dist3(const std::array<float, 3>& a, const std::array<float, 3>& b) {
    const double dx = double(b[0]) - a[0];
    const double dy = double(b[1]) - a[1];
    const double dz = double(b[2]) - a[2];
    return std::sqrt(dx*dx + dy*dy + dz*dz);
}

double triArea3(const std::array<float, 3>& a,
                const std::array<float, 3>& b,
                const std::array<float, 3>& c) {
    const double bax = double(b[0]) - a[0];
    const double bay = double(b[1]) - a[1];
    const double baz = double(b[2]) - a[2];
    const double cax = double(c[0]) - a[0];
    const double cay = double(c[1]) - a[1];
    const double caz = double(c[2]) - a[2];
    const double nx = bay * caz - baz * cay;
    const double ny = baz * cax - bax * caz;
    const double nz = bax * cay - bay * cax;
    return 0.5 * std::sqrt(nx*nx + ny*ny + nz*nz);
}

// Symmetric 3×3 eigendecomposition via Jacobi rotations. Tiny inline
// alternative to pulling Eigen into the wgpu module for the single
// polygon-planarity check. Converges in <10 sweeps for 3×3.
void jacobiEigen3(double m00, double m01, double m02,
                  double m11, double m12, double m22,
                  double eigvals[3], double eigvecs[3][3]) {
    double a[3][3] = {{m00, m01, m02},
                      {m01, m11, m12},
                      {m02, m12, m22}};
    double v[3][3] = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
    for (int iter = 0; iter < 50; ++iter) {
        // Pick largest off-diagonal magnitude.
        int p = 0, q = 1;
        double off = std::abs(a[0][1]);
        if (std::abs(a[0][2]) > off) { p = 0; q = 2; off = std::abs(a[0][2]); }
        if (std::abs(a[1][2]) > off) { p = 1; q = 2; off = std::abs(a[1][2]); }
        if (off < 1e-12) break;
        const double app = a[p][p], aqq = a[q][q], apq = a[p][q];
        const double theta = (aqq - app) / (2.0 * apq);
        double t = (theta >= 0.0) ? 1.0 / (theta + std::sqrt(1.0 + theta*theta))
                                  : 1.0 / (theta - std::sqrt(1.0 + theta*theta));
        const double c = 1.0 / std::sqrt(1.0 + t*t);
        const double s = t * c;
        a[p][p] = app - t * apq;
        a[q][q] = aqq + t * apq;
        a[p][q] = a[q][p] = 0.0;
        for (int k = 0; k < 3; ++k) {
            if (k == p || k == q) continue;
            const double akp = a[k][p], akq = a[k][q];
            a[k][p] = a[p][k] = c * akp - s * akq;
            a[k][q] = a[q][k] = s * akp + c * akq;
        }
        for (int k = 0; k < 3; ++k) {
            const double vkp = v[k][p], vkq = v[k][q];
            v[k][p] = c * vkp - s * vkq;
            v[k][q] = s * vkp + c * vkq;
        }
    }
    eigvals[0] = a[0][0];
    eigvals[1] = a[1][1];
    eigvals[2] = a[2][2];
    std::memcpy(eigvecs, v, sizeof(v));
}

struct PolygonAreaResult {
    double      area_m2;
    const char* method;
};

PolygonAreaResult polygonArea(const std::vector<std::array<float, 3>>& pts) {
    const size_t n = pts.size();

    // Centroid + bounding box (for the planarity threshold).
    double centroid[3] = {0, 0, 0};
    double bbox_min[3] = { std::numeric_limits<double>::infinity(),
                           std::numeric_limits<double>::infinity(),
                           std::numeric_limits<double>::infinity() };
    double bbox_max[3] = {-std::numeric_limits<double>::infinity(),
                          -std::numeric_limits<double>::infinity(),
                          -std::numeric_limits<double>::infinity() };
    for (const auto& p : pts) {
        centroid[0] += p[0]; centroid[1] += p[1]; centroid[2] += p[2];
        bbox_min[0] = std::min(bbox_min[0], double(p[0]));
        bbox_min[1] = std::min(bbox_min[1], double(p[1]));
        bbox_min[2] = std::min(bbox_min[2], double(p[2]));
        bbox_max[0] = std::max(bbox_max[0], double(p[0]));
        bbox_max[1] = std::max(bbox_max[1], double(p[1]));
        bbox_max[2] = std::max(bbox_max[2], double(p[2]));
    }
    centroid[0] /= double(n);
    centroid[1] /= double(n);
    centroid[2] /= double(n);
    const double bbx = bbox_max[0] - bbox_min[0];
    const double bby = bbox_max[1] - bbox_min[1];
    const double bbz = bbox_max[2] - bbox_min[2];
    const double bbox_diag = std::sqrt(bbx*bbx + bby*bby + bbz*bbz);

    // 3×3 symmetric covariance. Smallest eigenvector → plane normal.
    double c00 = 0, c01 = 0, c02 = 0, c11 = 0, c12 = 0, c22 = 0;
    for (const auto& p : pts) {
        const double dx = double(p[0]) - centroid[0];
        const double dy = double(p[1]) - centroid[1];
        const double dz = double(p[2]) - centroid[2];
        c00 += dx*dx; c01 += dx*dy; c02 += dx*dz;
        c11 += dy*dy; c12 += dy*dz; c22 += dz*dz;
    }
    double eigvals[3];
    double eigvecs[3][3];
    jacobiEigen3(c00, c01, c02, c11, c12, c22, eigvals, eigvecs);
    int min_i = 0;
    if (eigvals[1] < eigvals[min_i]) min_i = 1;
    if (eigvals[2] < eigvals[min_i]) min_i = 2;
    const double normal[3] = { eigvecs[0][min_i],
                               eigvecs[1][min_i],
                               eigvecs[2][min_i] };

    double sq_sum = 0.0;
    for (const auto& p : pts) {
        const double d = (double(p[0]) - centroid[0]) * normal[0]
                       + (double(p[1]) - centroid[1]) * normal[1]
                       + (double(p[2]) - centroid[2]) * normal[2];
        sq_sum += d * d;
    }
    const double rms = std::sqrt(sq_sum / double(n));
    const bool planar = bbox_diag > 0.0 && (rms / bbox_diag) < 1e-3;

    if (planar) {
        // In-plane orthonormal basis. Cross with whichever world axis is
        // least parallel to the normal so u doesn't collapse.
        double u[3];
        u[0] = normal[1] * 0.0 - normal[2] * 0.0;  // normal × X
        u[1] = normal[2] * 1.0 - normal[0] * 0.0;
        u[2] = normal[0] * 0.0 - normal[1] * 1.0;
        double ul2 = u[0]*u[0] + u[1]*u[1] + u[2]*u[2];
        if (ul2 < 1e-6) {
            u[0] = normal[1] * 0.0 - normal[2] * 1.0;  // normal × Y
            u[1] = normal[2] * 0.0 - normal[0] * 0.0;
            u[2] = normal[0] * 1.0 - normal[1] * 0.0;
            ul2 = u[0]*u[0] + u[1]*u[1] + u[2]*u[2];
        }
        const double ul = std::sqrt(ul2);
        u[0] /= ul; u[1] /= ul; u[2] /= ul;
        const double v[3] = {
            normal[1]*u[2] - normal[2]*u[1],
            normal[2]*u[0] - normal[0]*u[2],
            normal[0]*u[1] - normal[1]*u[0]
        };
        // Project + shoelace.
        std::vector<std::array<double, 2>> uv(n);
        for (size_t i = 0; i < n; ++i) {
            const double dx = double(pts[i][0]) - centroid[0];
            const double dy = double(pts[i][1]) - centroid[1];
            const double dz = double(pts[i][2]) - centroid[2];
            uv[i][0] = dx*u[0] + dy*u[1] + dz*u[2];
            uv[i][1] = dx*v[0] + dy*v[1] + dz*v[2];
        }
        double s = 0.0;
        for (size_t i = 0; i < n; ++i) {
            const auto& a = uv[i];
            const auto& b = uv[(i + 1) % n];
            s += a[0] * b[1] - b[0] * a[1];
        }
        return { 0.5 * std::abs(s), "planar" };
    }

    // Fan from p0 — heuristic for non-planar / star-shaped 3D loops.
    double area = 0.0;
    for (size_t i = 1; i + 1 < n; ++i) {
        area += triArea3(pts[0], pts[i], pts[i + 1]);
    }
    return { area, "fan-triangulated (non-planar)" };
}

uint64_t edgeKey(uint32_t a, uint32_t b) {
    if (a > b) std::swap(a, b);
    return (uint64_t(a) << 32) | uint64_t(b);
}

double pointTriangleDistSq(const float p[3],
                           const float a[3], const float b[3], const float c[3]) {
    auto sub = [](const float u[3], const float v[3], double r[3]) {
        r[0] = double(u[0]) - v[0];
        r[1] = double(u[1]) - v[1];
        r[2] = double(u[2]) - v[2];
    };
    auto dot = [](const double u[3], const double v[3]) {
        return u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
    };
    double ab[3], ac[3], ap[3];
    sub(b, a, ab);
    sub(c, a, ac);
    sub(p, a, ap);
    const double d1 = dot(ab, ap);
    const double d2 = dot(ac, ap);
    if (d1 <= 0.0 && d2 <= 0.0) {
        return ap[0]*ap[0] + ap[1]*ap[1] + ap[2]*ap[2];
    }
    double bp[3];
    sub(p, b, bp);
    const double d3 = dot(ab, bp);
    const double d4 = dot(ac, bp);
    if (d3 >= 0.0 && d4 <= d3) {
        return bp[0]*bp[0] + bp[1]*bp[1] + bp[2]*bp[2];
    }
    const double vc = d1 * d4 - d3 * d2;
    if (vc <= 0.0 && d1 >= 0.0 && d3 <= 0.0) {
        const double v = d1 / (d1 - d3);
        const double qx = ap[0] - v * ab[0];
        const double qy = ap[1] - v * ab[1];
        const double qz = ap[2] - v * ab[2];
        return qx*qx + qy*qy + qz*qz;
    }
    double cp[3];
    sub(p, c, cp);
    const double d5 = dot(ab, cp);
    const double d6 = dot(ac, cp);
    if (d6 >= 0.0 && d5 <= d6) {
        return cp[0]*cp[0] + cp[1]*cp[1] + cp[2]*cp[2];
    }
    const double vb = d5 * d2 - d1 * d6;
    if (vb <= 0.0 && d2 >= 0.0 && d6 <= 0.0) {
        const double w = d2 / (d2 - d6);
        const double qx = ap[0] - w * ac[0];
        const double qy = ap[1] - w * ac[1];
        const double qz = ap[2] - w * ac[2];
        return qx*qx + qy*qy + qz*qz;
    }
    const double va = d3 * d6 - d5 * d4;
    if (va <= 0.0 && (d4 - d3) >= 0.0 && (d5 - d6) >= 0.0) {
        const double w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        const double qx = double(b[0]) + w * (double(c[0]) - b[0]) - p[0];
        const double qy = double(b[1]) + w * (double(c[1]) - b[1]) - p[1];
        const double qz = double(b[2]) + w * (double(c[2]) - b[2]) - p[2];
        return qx*qx + qy*qy + qz*qz;
    }
    const double denom = 1.0 / (va + vb + vc);
    const double v = vb * denom;
    const double w = vc * denom;
    const double qx = double(a[0]) + v * ab[0] + w * ac[0] - p[0];
    const double qy = double(a[1]) + v * ab[1] + w * ac[1] - p[1];
    const double qz = double(a[2]) + v * ab[2] + w * ac[2] - p[2];
    return qx*qx + qy*qy + qz*qz;
}

constexpr double kCoplanarDot = 0.9999;  // ~0.81° tolerance

// Visual style — reused across all length-tool overlay paths.
constexpr float LINE_WIDTH    = 1.5f;
constexpr float LINE_HALO     = 0.5f;
constexpr float DOT_SIZE      = 6.0f;
constexpr float DOT_HALO      = 1.0f;
constexpr float DASH_PERIOD   = 9.0f;   // px
constexpr float DASH_ON_RATIO = 0.55f;  // 5 on, 4 off

OverlayRenderer::LineGroup makeGroup(std::vector<float> xyz,
                                         float r, float g, float b,
                                         bool dashed = false) {
    OverlayRenderer::LineGroup gp;
    gp.world_xyz = std::move(xyz);
    gp.color[0] = r; gp.color[1] = g; gp.color[2] = b; gp.color[3] = 1.0f;
    gp.stroke_color[0] = 0.0f; gp.stroke_color[1] = 0.0f;
    gp.stroke_color[2] = 0.0f; gp.stroke_color[3] = 1.0f;
    gp.line_width      = LINE_WIDTH;
    gp.stroke_extra    = LINE_HALO;
    gp.dash_period_px  = dashed ? DASH_PERIOD : 0.0f;
    gp.dash_on_ratio   = DASH_ON_RATIO;
    return gp;
}

void pushDot(std::vector<float>& xyz, const std::array<float, 3>& p) {
    xyz.push_back(p[0]); xyz.push_back(p[1]); xyz.push_back(p[2]);
}

void pushSeg(std::vector<float>& xyz,
             const std::array<float, 3>& a,
             const std::array<float, 3>& b) {
    xyz.insert(xyz.end(), a.begin(), a.end());
    xyz.insert(xyz.end(), b.begin(), b.end());
}

OverlayRenderer::Label makeLabel(const std::array<float, 3>& a,
                                     const std::array<float, 3>& b,
                                     const QString& text) {
    OverlayRenderer::Label lbl;
    lbl.world_pos[0] = 0.5f * (a[0] + b[0]);
    lbl.world_pos[1] = 0.5f * (a[1] + b[1]);
    lbl.world_pos[2] = 0.5f * (a[2] + b[2]);
    lbl.text = text;
    return lbl;
}

void pushDots(ViewportWindow& vp, const std::vector<float>& xyz) {
    vp.setOverlayPoints(xyz,
                        /*inner*/  1.0f, 1.0f, 1.0f, 1.0f,
                        /*size*/   DOT_SIZE,
                        /*stroke*/ 0.0f, 0.0f, 0.0f, 1.0f,
                        /*extra*/  DOT_HALO);
}

const char* dominantAxisLabel(const float v[3]) {
    const float ax = std::abs(v[0]);
    const float ay = std::abs(v[1]);
    const float az = std::abs(v[2]);
    if (az >= ax && az >= ay) return "Z";
    if (ax >= ay) return "X";
    return "Y";
}

}  // namespace

LengthMeasurement::LengthMeasurement() = default;

void LengthMeasurement::clear(ViewportWindow& vp) {
    points_.clear();
    normals_.clear();
    vp.setOverlayPoints({}, 0,0,0,0, 0, 0,0,0,0, 0);
    vp.setOverlayLines({});
    vp.setOverlayLabels({});
    vp.setHudText(QString());
}

void LengthMeasurement::onPick(ViewportWindow& vp,
                                   int x_phys, int y_phys, bool /*alt*/) {
    ViewportWindow::MeshLocalPick pick;
    if (!vp.pickMeshLocalAt(x_phys, y_phys, pick)) return;
    points_.push_back({pick.world_pos[0], pick.world_pos[1], pick.world_pos[2]});
    normals_.push_back({pick.world_normal[0], pick.world_normal[1], pick.world_normal[2]});
    if (points_.size() == 1) {
        first_pick_ = pick;  // record info the laser BFS needs
    }
    rebuildOverlay(vp);
}

void LengthMeasurement::removeLastPoint(ViewportWindow& vp) {
    if (points_.empty()) return;
    points_.pop_back();
    if (!normals_.empty()) normals_.pop_back();
    rebuildOverlay(vp);
}

void LengthMeasurement::rebuildOverlay(ViewportWindow& vp) {
    if (points_.size() == 1 && normals_.size() == 1) {
        rebuildLaserOverlay(vp);
        return;
    }

    std::vector<float> pts_xyz;
    pts_xyz.reserve(points_.size() * 3);
    for (const auto& p : points_) pushDot(pts_xyz, p);
    pushDots(vp, pts_xyz);

    std::vector<OverlayRenderer::LineGroup> groups;
    std::vector<OverlayRenderer::Label> labels;
    const size_t n = points_.size();

    if (n == 2) {
        const auto& a = points_[0];
        const auto& b = points_[1];
        groups.push_back(makeGroup({a[0], a[1], a[2], b[0], b[1], b[2]},
                                   1.0f, 1.0f, 1.0f));
        labels.push_back(makeLabel(a, b,
            QString::number(dist3(a, b), 'f', 3) + QStringLiteral(" m")));

        const std::array<float, 3> kx = {b[0], a[1], a[2]};
        const std::array<float, 3> ky = {b[0], b[1], a[2]};
        const double dx = std::abs(double(b[0]) - a[0]);
        const double dy = std::abs(double(b[1]) - a[1]);
        const double dz = std::abs(double(b[2]) - a[2]);
        if (dx > 1e-6) {
            groups.push_back(makeGroup({a[0],a[1],a[2], kx[0],kx[1],kx[2]},
                                       1.00f, 0.30f, 0.30f));
            labels.push_back(makeLabel(a, kx,
                QStringLiteral("ΔX: ") + QString::number(dx, 'f', 3) + QStringLiteral(" m")));
        }
        if (dy > 1e-6) {
            groups.push_back(makeGroup({kx[0],kx[1],kx[2], ky[0],ky[1],ky[2]},
                                       0.30f, 0.90f, 0.30f));
            labels.push_back(makeLabel(kx, ky,
                QStringLiteral("ΔY: ") + QString::number(dy, 'f', 3) + QStringLiteral(" m")));
        }
        if (dz > 1e-6) {
            groups.push_back(makeGroup({ky[0],ky[1],ky[2], b[0],b[1],b[2]},
                                       0.30f, 0.55f, 1.00f));
            labels.push_back(makeLabel(ky, b,
                QStringLiteral("ΔZ: ") + QString::number(dz, 'f', 3) + QStringLiteral(" m")));
        }

        if (normals_.size() == 2) {
            const auto& na = normals_[0];
            const auto& nb = normals_[1];
            const double dot_nn = double(na[0])*nb[0]
                                + double(na[1])*nb[1]
                                + double(na[2])*nb[2];
            if (std::abs(dot_nn) > 0.95) {
                const float sign = dot_nn >= 0.0 ? 1.0f : -1.0f;
                float n_avg[3] = {
                    0.5f * (na[0] + sign * nb[0]),
                    0.5f * (na[1] + sign * nb[1]),
                    0.5f * (na[2] + sign * nb[2]),
                };
                const float len = std::sqrt(n_avg[0]*n_avg[0]
                                           + n_avg[1]*n_avg[1]
                                           + n_avg[2]*n_avg[2]);
                if (len > 1e-6f) {
                    n_avg[0] /= len; n_avg[1] /= len; n_avg[2] /= len;
                }
                const double abx = double(b[0]) - a[0];
                const double aby = double(b[1]) - a[1];
                const double abz = double(b[2]) - a[2];
                const double perp = abx*n_avg[0] + aby*n_avg[1] + abz*n_avg[2];
                const double abs_perp = std::abs(perp);
                constexpr double kAxisCollapseTol = 1e-3;
                const bool redundant =
                       std::abs(abs_perp - dx) < kAxisCollapseTol
                    || std::abs(abs_perp - dy) < kAxisCollapseTol
                    || std::abs(abs_perp - dz) < kAxisCollapseTol;
                if (abs_perp > 1e-6 && !redundant) {
                    const std::array<float, 3> tip = {
                        float(a[0] + perp * n_avg[0]),
                        float(a[1] + perp * n_avg[1]),
                        float(a[2] + perp * n_avg[2]),
                    };
                    auto perp_grp = makeGroup(
                        {a[0],a[1],a[2], tip[0],tip[1],tip[2]},
                        1.0f, 1.0f, 1.0f, /*dashed*/ true);
                    groups.push_back(perp_grp);
                    labels.push_back(makeLabel(a, tip,
                        QStringLiteral("perp: ") + QString::number(abs_perp, 'f', 3) + QStringLiteral(" m")));
                }
            }
        }
    } else if (n >= 3) {
        std::vector<float> seg_xyz;
        seg_xyz.reserve(n * 6);
        labels.reserve(n);
        auto addSeg = [&](const std::array<float, 3>& a,
                          const std::array<float, 3>& b) {
            pushSeg(seg_xyz, a, b);
            labels.push_back(makeLabel(a, b,
                QString::number(dist3(a, b), 'f', 3) + QStringLiteral(" m")));
        };
        for (size_t i = 0; i + 1 < n; ++i) addSeg(points_[i], points_[i + 1]);
        if (n >= 4) addSeg(points_[n - 1], points_[0]);
        groups.push_back(makeGroup(std::move(seg_xyz), 1.0f, 1.0f, 1.0f));
    }

    vp.setOverlayLines(groups);
    vp.setOverlayLabels(labels);
    vp.setHudText(formatReadout());
}

void LengthMeasurement::rebuildLaserOverlay(ViewportWindow& vp) {
    const auto& wp = first_pick_.world_pos;
    const auto& n  = first_pick_.world_normal;

    // Tangent basis in world space.
    constexpr float WORLD_UP[3] = {0.0f, 0.0f, 1.0f};
    const float dot_un = WORLD_UP[0]*n[0] + WORLD_UP[1]*n[1] + WORLD_UP[2]*n[2];
    float t1[3] = {
        WORLD_UP[0] - dot_un * n[0],
        WORLD_UP[1] - dot_un * n[1],
        WORLD_UP[2] - dot_un * n[2],
    };
    float t1_len = std::sqrt(t1[0]*t1[0] + t1[1]*t1[1] + t1[2]*t1[2]);
    if (t1_len < 0.1f) {
        constexpr float WORLD_X[3] = {1.0f, 0.0f, 0.0f};
        const float dot_xn = WORLD_X[0]*n[0] + WORLD_X[1]*n[1] + WORLD_X[2]*n[2];
        t1[0] = WORLD_X[0] - dot_xn * n[0];
        t1[1] = WORLD_X[1] - dot_xn * n[1];
        t1[2] = WORLD_X[2] - dot_xn * n[2];
        t1_len = std::sqrt(t1[0]*t1[0] + t1[1]*t1[1] + t1[2]*t1[2]);
    }
    if (t1_len > 1e-6f) {
        t1[0] /= t1_len; t1[1] /= t1_len; t1[2] /= t1_len;
    }
    const float t2[3] = {
        n[1]*t1[2] - n[2]*t1[1],
        n[2]*t1[0] - n[0]*t1[2],
        n[0]*t1[1] - n[1]*t1[0],
    };

    std::vector<OverlayRenderer::LineGroup> groups;
    std::vector<OverlayRenderer::Label> labels;
    QStringList hud_lines;
    hud_lines << QStringLiteral("Laser measure (click another point for distance)");
    double enh[3] = {0.0, 0.0, 0.0};
    if (vp.meshLocalToGlobal(first_pick_.object_id, first_pick_.mesh_local, enh)) {
        hud_lines << QStringLiteral("ENH: %1, %2, %3")
                         .arg(enh[0], 0, 'f', 3)
                         .arg(enh[1], 0, 'f', 3)
                         .arg(enh[2], 0, 'f', 3);
    }

    // Coplanar-patch BFS for face extent.
    ViewportWindow::MeshTriangles tris;
    bool have_extent = false;
    double min_t1 = 0.0, max_t1 = 0.0, min_t2 = 0.0, max_t2 = 0.0;
    if (vp.readbackMeshTriangles(first_pick_.model_id, first_pick_.mesh_id, tris)) {
        const size_t n_verts = tris.positions.size() / 3;
        const size_t n_tris  = tris.indices.size() / 3;
        if (n_tris > 0) {
            std::vector<float> wv(n_verts * 3);
            const float* M = first_pick_.composed_transform;
            for (size_t i = 0; i < n_verts; ++i) {
                const float* p = &tris.positions[i * 3];
                wv[i*3 + 0] = M[0]*p[0] + M[4]*p[1] + M[8]*p[2]  + M[12];
                wv[i*3 + 1] = M[1]*p[0] + M[5]*p[1] + M[9]*p[2]  + M[13];
                wv[i*3 + 2] = M[2]*p[0] + M[6]*p[1] + M[10]*p[2] + M[14];
            }
            std::vector<std::array<float, 3>> tri_n(n_tris);
            std::unordered_map<uint64_t, std::vector<uint32_t>> edges;
            edges.reserve(n_tris * 3);
            for (size_t t = 0; t < n_tris; ++t) {
                const uint32_t ia = tris.indices[3*t + 0];
                const uint32_t ib = tris.indices[3*t + 1];
                const uint32_t ic = tris.indices[3*t + 2];
                const float* a = &wv[3*ia];
                const float* b = &wv[3*ib];
                const float* c = &wv[3*ic];
                const float bax = b[0]-a[0], bay = b[1]-a[1], baz = b[2]-a[2];
                const float cax = c[0]-a[0], cay = c[1]-a[1], caz = c[2]-a[2];
                float nx = bay*caz - baz*cay;
                float ny = baz*cax - bax*caz;
                float nz = bax*cay - bay*cax;
                const float nl = std::sqrt(nx*nx + ny*ny + nz*nz);
                if (nl > 0.0f) { nx /= nl; ny /= nl; nz /= nl; }
                tri_n[t] = {nx, ny, nz};
                edges[edgeKey(ia, ib)].push_back(uint32_t(t));
                edges[edgeKey(ib, ic)].push_back(uint32_t(t));
                edges[edgeKey(ic, ia)].push_back(uint32_t(t));
            }
            uint32_t seed = 0;
            double best = std::numeric_limits<double>::infinity();
            for (size_t t = 0; t < n_tris; ++t) {
                const uint32_t ia = tris.indices[3*t + 0];
                const uint32_t ib = tris.indices[3*t + 1];
                const uint32_t ic = tris.indices[3*t + 2];
                const double d = pointTriangleDistSq(
                    wp, &wv[3*ia], &wv[3*ib], &wv[3*ic]);
                if (d < best) { best = d; seed = uint32_t(t); }
            }
            const auto& sn = tri_n[seed];
            std::unordered_set<uint32_t> in_patch;
            in_patch.insert(seed);
            std::queue<uint32_t> frontier;
            frontier.push(seed);
            while (!frontier.empty()) {
                const uint32_t t = frontier.front(); frontier.pop();
                for (int e = 0; e < 3; ++e) {
                    const uint32_t ia = tris.indices[3*t + e];
                    const uint32_t ib = tris.indices[3*t + (e + 1) % 3];
                    auto it = edges.find(edgeKey(ia, ib));
                    if (it == edges.end()) continue;
                    for (uint32_t nt : it->second) {
                        if (nt == t || in_patch.count(nt)) continue;
                        const auto& nn = tri_n[nt];
                        const double dot = double(sn[0])*nn[0]
                                         + double(sn[1])*nn[1]
                                         + double(sn[2])*nn[2];
                        if (dot < kCoplanarDot) continue;
                        in_patch.insert(nt);
                        frontier.push(nt);
                    }
                }
            }
            std::unordered_set<uint32_t> patch_verts;
            for (uint32_t t : in_patch) {
                patch_verts.insert(tris.indices[3*t + 0]);
                patch_verts.insert(tris.indices[3*t + 1]);
                patch_verts.insert(tris.indices[3*t + 2]);
            }
            for (uint32_t vi : patch_verts) {
                const float* v = &wv[3 * vi];
                const double dx = double(v[0]) - wp[0];
                const double dy = double(v[1]) - wp[1];
                const double dz = double(v[2]) - wp[2];
                const double a1 = dx*t1[0] + dy*t1[1] + dz*t1[2];
                const double a2 = dx*t2[0] + dy*t2[1] + dz*t2[2];
                if (!have_extent) {
                    min_t1 = max_t1 = a1;
                    min_t2 = max_t2 = a2;
                    have_extent = true;
                } else {
                    min_t1 = std::min(min_t1, a1); max_t1 = std::max(max_t1, a1);
                    min_t2 = std::min(min_t2, a2); max_t2 = std::max(max_t2, a2);
                }
            }
        }
    }

    auto pushBar = [&](const float t[3], double mn, double mx) {
        const std::array<float, 3> a = {
            float(wp[0] + mn * t[0]),
            float(wp[1] + mn * t[1]),
            float(wp[2] + mn * t[2]),
        };
        const std::array<float, 3> b = {
            float(wp[0] + mx * t[0]),
            float(wp[1] + mx * t[1]),
            float(wp[2] + mx * t[2]),
        };
        const double extent = mx - mn;
        const QString axis = QString::fromLatin1(dominantAxisLabel(t));
        groups.push_back(makeGroup({a[0],a[1],a[2], b[0],b[1],b[2]},
                                   1.0f, 1.0f, 1.0f, /*dashed*/ true));
        labels.push_back(makeLabel(a, b,
            QStringLiteral("%1 extent: %2 m").arg(axis).arg(extent, 0, 'f', 3)));
        hud_lines << QStringLiteral("%1 extent: %2 m").arg(axis).arg(extent, 0, 'f', 3);
    };
    if (have_extent && (max_t1 - min_t1) > 1e-6) pushBar(t1, min_t1, max_t1);
    if (have_extent && (max_t2 - min_t2) > 1e-6) pushBar(t2, min_t2, max_t2);

    // Hybrid vertical raycast for floors / ceilings.
    if (std::abs(n[2]) > 0.85f) {
        constexpr float NUDGE = 1e-3f;
        const float ro[3] = {
            wp[0] + NUDGE * n[0],
            wp[1] + NUDGE * n[1],
            wp[2] + NUDGE * n[2],
        };
        ViewportWindow::RaycastHit hit;
        if (vp.raycast(ro, n, hit)) {
            const double dist = double(hit.distance) + double(NUDGE);
            const std::array<float, 3> a = {wp[0], wp[1], wp[2]};
            const std::array<float, 3> b = {hit.world_pos[0],
                                             hit.world_pos[1],
                                             hit.world_pos[2]};
            const QString tag = (n[2] > 0.0f)
                ? QStringLiteral("ceiling height")
                : QStringLiteral("floor distance");
            groups.push_back(makeGroup({a[0],a[1],a[2], b[0],b[1],b[2]},
                                       1.0f, 1.0f, 1.0f, /*dashed*/ true));
            labels.push_back(makeLabel(a, b,
                QStringLiteral("%1: %2 m").arg(tag).arg(dist, 0, 'f', 3)));
            hud_lines << QStringLiteral("%1: %2 m").arg(tag).arg(dist, 0, 'f', 3);
        }
    }

    pushDots(vp, std::vector<float>(wp, wp + 3));
    vp.setOverlayLines(groups);
    vp.setOverlayLabels(labels);
    vp.setHudText(hud_lines.join('\n'));
}

QString LengthMeasurement::formatReadout() const {
    const size_t n = points_.size();
    if (n == 0) return QStringLiteral("Length tool: click first point");
    if (n == 1) return QStringLiteral("1 point  (click another)");

    if (n == 2) {
        const auto& a = points_[0];
        const auto& b = points_[1];
        const double d  = dist3(a, b);
        const double dx = std::abs(double(b[0]) - a[0]);
        const double dy = std::abs(double(b[1]) - a[1]);
        const double dz = std::abs(double(b[2]) - a[2]);
        return QStringLiteral("Length: %1 m\nΔX: %2  ΔY: %3  ΔZ: %4 m")
            .arg(d, 0, 'f', 4)
            .arg(dx, 0, 'f', 4)
            .arg(dy, 0, 'f', 4)
            .arg(dz, 0, 'f', 4);
    }

    if (n == 3) {
        const auto& a = points_[0];
        const auto& b = points_[1];
        const auto& c = points_[2];
        const double bax = double(a[0]) - b[0];
        const double bay = double(a[1]) - b[1];
        const double baz = double(a[2]) - b[2];
        const double bcx = double(c[0]) - b[0];
        const double bcy = double(c[1]) - b[1];
        const double bcz = double(c[2]) - b[2];
        const double la = std::sqrt(bax*bax + bay*bay + baz*baz);
        const double lc = std::sqrt(bcx*bcx + bcy*bcy + bcz*bcz);
        double angle_deg = 0.0;
        if (la > 0.0 && lc > 0.0) {
            const double cosang = std::clamp(
                (bax*bcx + bay*bcy + baz*bcz) / (la * lc), -1.0, 1.0);
            angle_deg = std::acos(cosang) * 180.0 / M_PI;
        }
        return QStringLiteral("Angle at pt 2: %1°\nTriangle area: %2 m²\nPerimeter: %3 m")
            .arg(angle_deg, 0, 'f', 2)
            .arg(triArea3(a, b, c), 0, 'f', 4)
            .arg(dist3(a, b) + dist3(b, c) + dist3(c, a), 0, 'f', 4);
    }

    const PolygonAreaResult r = polygonArea(points_);
    double perimeter = 0.0;
    for (size_t i = 0; i < n; ++i) {
        perimeter += dist3(points_[i], points_[(i + 1) % n]);
    }
    return QStringLiteral("Polygon (%1 pts, %2)\nArea: %3 m²\nPerimeter: %4 m")
        .arg(n)
        .arg(r.method)
        .arg(r.area_m2, 0, 'f', 4)
        .arg(perimeter, 0, 'f', 4);
}
