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

#include "Measurement.h"

#include "ViewportWindow.h"

#include <QtGlobal>
#include <Eigen/Dense>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace {

double meshLocalVolume(const ViewportWindow::MeshTriangles& tris) {
    // Signed tetrahedra from the origin: V = sum( a · (b × c) ) / 6.
    // Absolute value at the end so winding convention doesn't matter.
    double sum = 0.0;
    const size_t n = tris.indices.size();
    for (size_t i = 0; i + 2 < n; i += 3) {
        const uint32_t ia = tris.indices[i + 0];
        const uint32_t ib = tris.indices[i + 1];
        const uint32_t ic = tris.indices[i + 2];
        const float* a = &tris.positions[3 * ia];
        const float* b = &tris.positions[3 * ib];
        const float* c = &tris.positions[3 * ic];
        const double cx = double(b[1]) * c[2] - double(b[2]) * c[1];
        const double cy = double(b[2]) * c[0] - double(b[0]) * c[2];
        const double cz = double(b[0]) * c[1] - double(b[1]) * c[0];
        sum += double(a[0]) * cx + double(a[1]) * cy + double(a[2]) * cz;
    }
    return std::abs(sum) / 6.0;
}

double det3(const float M[16]) {
    // Upper-left 3x3 of a column-major 4x4: M[col * 4 + row].
    const double m00 = M[0],  m10 = M[1],  m20 = M[2];
    const double m01 = M[4],  m11 = M[5],  m21 = M[6];
    const double m02 = M[8],  m12 = M[9],  m22 = M[10];
    return m00 * (m11 * m22 - m12 * m21)
         - m01 * (m10 * m22 - m12 * m20)
         + m02 * (m10 * m21 - m11 * m20);
}

} // namespace

double volumeOfObjects(ViewportWindow& vp,
                       const std::vector<uint32_t>& object_ids) {
    if (object_ids.empty()) return 0.0;

    // Group selected instances by (model_id, mesh_id) so each unique mesh
    // is read back at most once per call.  Each entry stores the |det| of
    // every instance of that mesh in the request.
    std::unordered_map<uint64_t, std::vector<double>> by_mesh;
    by_mesh.reserve(object_ids.size());
    for (uint32_t oid : object_ids) {
        ViewportWindow::InstanceLookup lk;
        if (!vp.findInstance(oid, lk)) continue;
        const uint64_t key = (uint64_t(lk.model_id) << 32) | lk.mesh_id;
        by_mesh[key].push_back(std::abs(det3(lk.placement_transformation)));
    }

    double total = 0.0;
    ViewportWindow::MeshTriangles tris;
    for (const auto& [key, dets] : by_mesh) {
        const uint32_t model_id = uint32_t(key >> 32);
        const uint32_t mesh_id  = uint32_t(key & 0xffffffffu);
        if (!vp.readbackMeshTriangles(model_id, mesh_id, tris)) continue;
        const double v = meshLocalVolume(tris);
        for (double d : dets) total += v * d;
    }
    return total;
}

std::vector<std::pair<uint32_t, double>>
volumesPerObject(ViewportWindow& vp,
                 const std::vector<uint32_t>& object_ids) {
    std::vector<std::pair<uint32_t, double>> out;
    if (object_ids.empty()) return out;
    out.reserve(object_ids.size());

    // Cache the local-frame volume per unique (model_id, mesh_id) so each
    // mesh is read back at most once even when many instances share it
    // (common for repeated families like windows / columns).
    std::unordered_map<uint64_t, double> mesh_vol_local;
    mesh_vol_local.reserve(object_ids.size());

    ViewportWindow::MeshTriangles tris;
    for (uint32_t oid : object_ids) {
        ViewportWindow::InstanceLookup lk;
        if (!vp.findInstance(oid, lk)) continue;

        const uint64_t key = (uint64_t(lk.model_id) << 32) | lk.mesh_id;
        auto it = mesh_vol_local.find(key);
        double v_local = 0.0;
        if (it == mesh_vol_local.end()) {
            if (vp.readbackMeshTriangles(lk.model_id, lk.mesh_id, tris)) {
                v_local = meshLocalVolume(tris);
            }
            mesh_vol_local.emplace(key, v_local);
        } else {
            v_local = it->second;
        }
        const double det = std::abs(det3(lk.placement_transformation));
        out.emplace_back(oid, v_local * det);
    }
    return out;
}

namespace {

// edge_key: undirected edge between two mesh-local vertex indices.
uint64_t edgeKey(uint32_t a, uint32_t b) {
    if (a > b) std::swap(a, b);
    return (uint64_t(a) << 32) | uint64_t(b);
}

// Triangle area = 0.5 * |(b - a) × (c - a)|.  Also returns the unit normal
// (zeroed for degenerate tris).
double triAreaAndNormal(const float* a, const float* b, const float* c,
                        float n_out[3]) {
    const double bax = double(b[0]) - a[0];
    const double bay = double(b[1]) - a[1];
    const double baz = double(b[2]) - a[2];
    const double cax = double(c[0]) - a[0];
    const double cay = double(c[1]) - a[1];
    const double caz = double(c[2]) - a[2];
    const double nx = bay * caz - baz * cay;
    const double ny = baz * cax - bax * caz;
    const double nz = bax * cay - bay * cax;
    const double len = std::sqrt(nx * nx + ny * ny + nz * nz);
    if (len > 0.0) {
        n_out[0] = float(nx / len);
        n_out[1] = float(ny / len);
        n_out[2] = float(nz / len);
    } else {
        n_out[0] = n_out[1] = n_out[2] = 0.0f;
    }
    return 0.5 * len;
}

// Squared distance from `p` to triangle (a, b, c) — clipped to the
// triangle's interior or boundary, whichever is closest.  Standard
// implementation (Ericson, "Real-Time Collision Detection").
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
    // Inside the triangle — return perpendicular distance to its plane.
    const double denom = 1.0 / (va + vb + vc);
    const double v = vb * denom;
    const double w = vc * denom;
    const double qx = double(a[0]) + v * ab[0] + w * ac[0] - p[0];
    const double qy = double(a[1]) + v * ab[1] + w * ac[1] - p[1];
    const double qz = double(a[2]) + v * ab[2] + w * ac[2] - p[2];
    return qx*qx + qy*qy + qz*qz;
}

constexpr double kCoplanarDot = 0.9999;  // ~0.81° tolerance

} // namespace

AreaMeasurement::AreaMeasurement() = default;

void AreaMeasurement::clear(ViewportWindow& vp) {
    mesh_cache_.clear();
    selected_.clear();
    total_area_m2_ = 0.0;
    vp.setHighlightTriangles({}, 0, 0, 0, 0);
    vp.setOverlayLabels({});
}

void AreaMeasurement::rebuildHighlight(ViewportWindow& vp) {
    // Push every selected triangle's three world-space vertices to the
    // overlay.  Mesh-local positions × per-instance composed transform.
    std::vector<float> world_xyz;
    world_xyz.reserve(selected_.size() * 9);
    for (const auto& [key, sel] : selected_) {
        const uint64_t cache_key = (uint64_t(sel.model_id) << 32)
                                 | uint64_t(sel.mesh_id);
        auto cit = mesh_cache_.find(cache_key);
        if (cit == mesh_cache_.end()) continue;
        const MeshCache& c = cit->second;
        if (size_t(sel.tri) * 3 + 2 >= c.indices.size()) continue;
        const float* M = sel.composed_transform;  // column-major
        for (int e = 0; e < 3; ++e) {
            const uint32_t vi = c.indices[3 * sel.tri + e];
            const float* p = &c.positions[3 * vi];
            // World = M * (p, 1).  Column-major: M[col*4 + row].
            const float wx = M[0]*p[0] + M[4]*p[1] + M[8]*p[2]  + M[12];
            const float wy = M[1]*p[0] + M[5]*p[1] + M[9]*p[2]  + M[13];
            const float wz = M[2]*p[0] + M[6]*p[1] + M[10]*p[2] + M[14];
            world_xyz.push_back(wx);
            world_xyz.push_back(wy);
            world_xyz.push_back(wz);
        }
    }
    // Translucent cyan-ish tint — readable on both light and dark surfaces.
    vp.setHighlightTriangles(world_xyz, 0.20f, 0.85f, 1.00f, 0.45f);

    // Per-patch labels: connected-components sweep over the selected
    // triangles (using the mesh's full edge adjacency, restricted to
    // edges where both incident tris are in the selection).  Each
    // component → one label at its area-weighted centroid in world
    // space, with the patch area in m².  Two clicks on different walls
    // → two distinct components → two labels; one click that BFS-grew
    // 200 tris of one wall face → one label.
    std::unordered_map<uint32_t, std::vector<const SelectedTri*>> by_object;
    for (const auto& [key, sel] : selected_) {
        const uint32_t object_id = uint32_t(key >> 32);
        by_object[object_id].push_back(&sel);
    }

    std::vector<OverlayRenderer::Label> labels;
    for (const auto& [obj_id, sels] : by_object) {
        if (sels.empty()) continue;
        // All tris belonging to one object share its mesh + transform.
        const SelectedTri& any = *sels[0];
        const uint64_t cache_key = (uint64_t(any.model_id) << 32)
                                 | uint64_t(any.mesh_id);
        auto cit = mesh_cache_.find(cache_key);
        if (cit == mesh_cache_.end()) continue;
        const MeshCache& c = cit->second;

        // Selected-tri set restricted to this object.
        std::unordered_set<uint32_t> remaining;
        remaining.reserve(sels.size());
        for (const SelectedTri* s : sels) remaining.insert(s->tri);

        // Find each connected component via BFS over shared edges,
        // accepting only neighbours that are themselves selected.
        while (!remaining.empty()) {
            const uint32_t start = *remaining.begin();
            std::unordered_set<uint32_t> in_comp{start};
            std::queue<uint32_t> frontier;
            frontier.push(start);
            std::vector<uint32_t> component;
            while (!frontier.empty()) {
                const uint32_t t = frontier.front(); frontier.pop();
                component.push_back(t);
                if (size_t(t) * 3 + 2 >= c.indices.size()) continue;
                for (int e = 0; e < 3; ++e) {
                    const uint32_t ia = c.indices[3 * t + e];
                    const uint32_t ib = c.indices[3 * t + (e + 1) % 3];
                    auto it = c.edges.find(edgeKey(ia, ib));
                    if (it == c.edges.end()) continue;
                    for (uint32_t nt : it->second) {
                        if (in_comp.count(nt) || remaining.count(nt) == 0) continue;
                        in_comp.insert(nt);
                        frontier.push(nt);
                    }
                }
            }
            for (uint32_t t : component) remaining.erase(t);

            // Area + area-weighted centroid (mesh-local).
            double area = 0.0, cx = 0.0, cy = 0.0, cz = 0.0;
            for (uint32_t t : component) {
                if (size_t(t) >= c.tri_areas.size()) continue;
                const double a = c.tri_areas[t];
                area += a;
                const uint32_t ia = c.indices[3 * t + 0];
                const uint32_t ib = c.indices[3 * t + 1];
                const uint32_t ic = c.indices[3 * t + 2];
                const float* va = &c.positions[3 * ia];
                const float* vb = &c.positions[3 * ib];
                const float* vc = &c.positions[3 * ic];
                cx += a * (double(va[0]) + vb[0] + vc[0]) / 3.0;
                cy += a * (double(va[1]) + vb[1] + vc[1]) / 3.0;
                cz += a * (double(va[2]) + vb[2] + vc[2]) / 3.0;
            }
            if (area <= 0.0) continue;
            cx /= area; cy /= area; cz /= area;

            // Centroid → world via the instance's composed transform.
            const float* M = any.composed_transform;
            OverlayRenderer::Label lbl;
            lbl.world_pos[0] = float(M[0]*cx + M[4]*cy + M[8]*cz  + M[12]);
            lbl.world_pos[1] = float(M[1]*cx + M[5]*cy + M[9]*cz  + M[13]);
            lbl.world_pos[2] = float(M[2]*cx + M[6]*cy + M[10]*cz + M[14]);
            lbl.text = QString::number(area, 'f', 4) + " m²";
            labels.push_back(std::move(lbl));
        }
    }
    vp.setOverlayLabels(labels);
}

AreaMeasurement::MeshCache* AreaMeasurement::meshCache(ViewportWindow& vp,
                                                       uint32_t model_id,
                                                       uint32_t mesh_id) {
    const uint64_t key = (uint64_t(model_id) << 32) | uint64_t(mesh_id);
    auto it = mesh_cache_.find(key);
    if (it != mesh_cache_.end()) return &it->second;

    ViewportWindow::MeshTriangles tris;
    if (!vp.readbackMeshTriangles(model_id, mesh_id, tris)) return nullptr;

    MeshCache c;
    c.positions = std::move(tris.positions);
    c.indices   = std::move(tris.indices);
    const size_t n_tris = c.indices.size() / 3;
    c.tri_normals.resize(n_tris * 3);
    c.tri_areas.resize(n_tris);
    c.edges.reserve(n_tris * 3);
    for (size_t t = 0; t < n_tris; ++t) {
        const uint32_t ia = c.indices[3 * t + 0];
        const uint32_t ib = c.indices[3 * t + 1];
        const uint32_t ic = c.indices[3 * t + 2];
        const float* a = &c.positions[3 * ia];
        const float* b = &c.positions[3 * ib];
        const float* cc = &c.positions[3 * ic];
        float n[3];
        c.tri_areas[t] = triAreaAndNormal(a, b, cc, n);
        c.tri_normals[3 * t + 0] = n[0];
        c.tri_normals[3 * t + 1] = n[1];
        c.tri_normals[3 * t + 2] = n[2];
        c.edges[edgeKey(ia, ib)].push_back(uint32_t(t));
        c.edges[edgeKey(ib, ic)].push_back(uint32_t(t));
        c.edges[edgeKey(ic, ia)].push_back(uint32_t(t));
    }
    return &mesh_cache_.emplace(key, std::move(c)).first->second;
}

void AreaMeasurement::onPick(ViewportWindow& vp, int x, int y, bool alt) {
    ViewportWindow::MeshLocalPick pick;
    if (!vp.pickMeshLocalAt(x, y, pick)) return;

    MeshCache* cache = meshCache(vp, pick.model_id, pick.mesh_id);
    if (!cache) return;
    const size_t n_tris = cache->indices.size() / 3;
    if (n_tris == 0) return;

    // Find the seed triangle: the one whose interior (or boundary) is
    // closest to the pick's mesh-local point.
    uint32_t seed = 0;
    double best = std::numeric_limits<double>::infinity();
    for (size_t t = 0; t < n_tris; ++t) {
        const uint32_t ia = cache->indices[3 * t + 0];
        const uint32_t ib = cache->indices[3 * t + 1];
        const uint32_t ic = cache->indices[3 * t + 2];
        const double d = pointTriangleDistSq(pick.mesh_local,
                                             &cache->positions[3 * ia],
                                             &cache->positions[3 * ib],
                                             &cache->positions[3 * ic]);
        if (d < best) {
            best = d;
            seed = uint32_t(t);
        }
    }

    // Expand to coplanar patch (BFS over shared edges).  Alt skips it.
    std::vector<uint32_t> patch;
    if (alt) {
        patch.push_back(seed);
    } else {
        const float* sn = &cache->tri_normals[3 * seed];
        std::unordered_set<uint32_t> visited;
        visited.insert(seed);
        std::queue<uint32_t> frontier;
        frontier.push(seed);
        while (!frontier.empty()) {
            const uint32_t t = frontier.front(); frontier.pop();
            patch.push_back(t);
            for (int e = 0; e < 3; ++e) {
                const uint32_t ia = cache->indices[3 * t + e];
                const uint32_t ib = cache->indices[3 * t + (e + 1) % 3];
                auto it = cache->edges.find(edgeKey(ia, ib));
                if (it == cache->edges.end()) continue;
                for (uint32_t nt : it->second) {
                    if (nt == t || visited.count(nt)) continue;
                    const float* nn = &cache->tri_normals[3 * nt];
                    const double dot = double(sn[0]) * nn[0]
                                     + double(sn[1]) * nn[1]
                                     + double(sn[2]) * nn[2];
                    if (dot < kCoplanarDot) continue;
                    visited.insert(nt);
                    frontier.push(nt);
                }
            }
        }
    }

    // Toggle: if the seed was already in the set, remove the patch;
    // otherwise add it.
    const uint64_t seed_key = triKey(pick.object_id, seed);
    const bool removing = selected_.count(seed_key) > 0;
    double delta = 0.0;
    for (uint32_t t : patch) {
        const uint64_t k = triKey(pick.object_id, t);
        if (removing) {
            auto it = selected_.find(k);
            if (it != selected_.end()) {
                delta -= cache->tri_areas[t];
                selected_.erase(it);
            }
        } else {
            SelectedTri sel;
            sel.model_id = pick.model_id;
            sel.mesh_id  = pick.mesh_id;
            sel.tri      = t;
            std::memcpy(sel.composed_transform, pick.composed_transform,
                        sizeof(sel.composed_transform));
            if (selected_.emplace(k, sel).second) {
                delta += cache->tri_areas[t];
            }
        }
    }
    total_area_m2_ += delta;

    rebuildHighlight(vp);

    qInfo("Area %s%.6f m^2  (total: %.6f m^2, %zu tris)",
          delta >= 0.0 ? "+" : "", delta,
          total_area_m2_, selected_.size());
}

// ----- LengthMeasurement -----------------------------------------------------

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

// Polygon area via best-fit plane + shoelace, falling back to fan
// triangulation when the points stray off the plane.  Returns the
// resulting area and a label naming which path was taken.
struct PolygonAreaResult {
    double      area_m2;
    const char* method;
};

PolygonAreaResult polygonArea(const std::vector<std::array<float, 3>>& pts) {
    using Vec3d = Eigen::Vector3d;
    using Mat3d = Eigen::Matrix3d;
    const size_t n = pts.size();

    // Centroid + bounding box (for the planarity threshold).
    Vec3d centroid = Vec3d::Zero();
    Vec3d bbox_min = Vec3d::Constant(std::numeric_limits<double>::infinity());
    Vec3d bbox_max = Vec3d::Constant(-std::numeric_limits<double>::infinity());
    for (const auto& p : pts) {
        const Vec3d v(p[0], p[1], p[2]);
        centroid += v;
        bbox_min = bbox_min.cwiseMin(v);
        bbox_max = bbox_max.cwiseMax(v);
    }
    centroid /= double(n);
    const double bbox_diag = (bbox_max - bbox_min).norm();

    // 3x3 covariance.  Smallest eigenvector of this is the plane normal.
    Mat3d cov = Mat3d::Zero();
    for (const auto& p : pts) {
        const Vec3d d = Vec3d(p[0], p[1], p[2]) - centroid;
        cov += d * d.transpose();
    }

    Eigen::SelfAdjointEigenSolver<Mat3d> es(cov);
    const Vec3d normal = es.eigenvectors().col(0);  // smallest eigenvalue

    // RMS plane distance, normalised against the bounding-box diagonal.
    double sq_sum = 0.0;
    for (const auto& p : pts) {
        const double d = (Vec3d(p[0], p[1], p[2]) - centroid).dot(normal);
        sq_sum += d * d;
    }
    const double rms = std::sqrt(sq_sum / double(n));
    const bool planar = bbox_diag > 0.0 && (rms / bbox_diag) < 1e-3;

    if (planar) {
        // Build an in-plane orthonormal basis.
        Vec3d u = normal.cross(Vec3d::UnitX());
        if (u.squaredNorm() < 1e-6) u = normal.cross(Vec3d::UnitY());
        u.normalize();
        const Vec3d v = normal.cross(u);

        // Project + shoelace.
        std::vector<std::array<double, 2>> uv(n);
        for (size_t i = 0; i < n; ++i) {
            const Vec3d d = Vec3d(pts[i][0], pts[i][1], pts[i][2]) - centroid;
            uv[i][0] = d.dot(u);
            uv[i][1] = d.dot(v);
        }
        double s = 0.0;
        for (size_t i = 0; i < n; ++i) {
            const auto& a = uv[i];
            const auto& b = uv[(i + 1) % n];
            s += a[0] * b[1] - b[0] * a[1];
        }
        return { 0.5 * std::abs(s), "planar" };
    }

    // Fan from p0.  Works for star-shaped polygons; for genuinely twisted
    // 3D point sets it's a heuristic — flagged in the method label.
    double area = 0.0;
    for (size_t i = 1; i + 1 < n; ++i) {
        area += triArea3(pts[0], pts[i], pts[i + 1]);
    }
    return { area, "fan-triangulated (non-planar)" };
}

} // namespace

LengthMeasurement::LengthMeasurement() = default;

namespace {

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
    xyz.push_back(p[0]);
    xyz.push_back(p[1]);
    xyz.push_back(p[2]);
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

} // namespace

void LengthMeasurement::clear(ViewportWindow& vp) {
    points_.clear();
    normals_.clear();
    vp.setOverlayPoints({}, 0,0,0,0, 0, 0,0,0,0, 0);
    vp.setOverlayLines({});
    vp.setOverlayLabels({});
    vp.setHudText(QString());
}

void LengthMeasurement::onPick(ViewportWindow& vp, int x, int y, bool /*alt*/) {
    ViewportWindow::MeshLocalPick pick;
    if (!vp.pickMeshLocalAt(x, y, pick)) return;
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
        // Direct line A→B (white) + total-length label.
        const auto& a = points_[0];
        const auto& b = points_[1];
        groups.push_back(makeGroup({a[0], a[1], a[2], b[0], b[1], b[2]},
                                   1.0f, 1.0f, 1.0f));
        labels.push_back(makeLabel(a, b,
            QString::number(dist3(a, b), 'f', 3) + " m"));

        // Axis-coloured stair-step A → (Bx,Ay,Az) → (Bx,By,Az) → B.
        // Each leg gets its delta label (omit zero legs to keep the
        // overlay clean when the points are axis-aligned).
        const std::array<float, 3> kx = {b[0], a[1], a[2]};
        const std::array<float, 3> ky = {b[0], b[1], a[2]};
        const double dx = std::abs(double(b[0]) - a[0]);
        const double dy = std::abs(double(b[1]) - a[1]);
        const double dz = std::abs(double(b[2]) - a[2]);
        if (dx > 1e-6) {
            groups.push_back(makeGroup({a[0],a[1],a[2], kx[0],kx[1],kx[2]},
                                       1.00f, 0.30f, 0.30f));
            labels.push_back(makeLabel(a, kx,
                "ΔX: " + QString::number(dx, 'f', 3) + " m"));
        }
        if (dy > 1e-6) {
            groups.push_back(makeGroup({kx[0],kx[1],kx[2], ky[0],ky[1],ky[2]},
                                       0.30f, 0.90f, 0.30f));
            labels.push_back(makeLabel(kx, ky,
                "ΔY: " + QString::number(dy, 'f', 3) + " m"));
        }
        if (dz > 1e-6) {
            groups.push_back(makeGroup({ky[0],ky[1],ky[2], b[0],b[1],b[2]},
                                       0.30f, 0.55f, 1.00f));
            labels.push_back(makeLabel(ky, b,
                "ΔZ: " + QString::number(dz, 'f', 3) + " m"));
        }

        // Perpendicular projection: only when both picks landed on
        // surfaces with near-parallel normals (|n_a · n_b| > 0.95).  We
        // pick the average normal (flipped to agree with n_a if needed)
        // and project AB onto it.  Drawn dashed from A to A + perp·n.
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
                // Skip the perpendicular dimension when it collapses onto
                // an existing axis-aligned leg — happens when the surface
                // normal lines up with a world axis, in which case
                // ΔX / ΔY / ΔZ already shows the same number.
                constexpr double kAxisCollapseTol = 1e-3;  // 1mm
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
                        "perp: " + QString::number(abs_perp, 'f', 3) + " m"));
                }
            }
        }
    } else if (n >= 3) {
        // 3-pt and 4+pt: white connecting polyline (closed for 4+) with
        // per-segment length labels.  HUD carries the angle/area readout.
        std::vector<float> seg_xyz;
        seg_xyz.reserve(n * 6);
        labels.reserve(n);
        auto addSeg = [&](const std::array<float, 3>& a,
                          const std::array<float, 3>& b) {
            pushSeg(seg_xyz, a, b);
            labels.push_back(makeLabel(a, b,
                QString::number(dist3(a, b), 'f', 3) + " m"));
        };
        for (size_t i = 0; i + 1 < n; ++i) addSeg(points_[i], points_[i + 1]);
        if (n >= 4) addSeg(points_[n - 1], points_[0]);
        groups.push_back(makeGroup(std::move(seg_xyz), 1.0f, 1.0f, 1.0f));
    }

    vp.setOverlayLines(groups);
    vp.setOverlayLabels(labels);
    vp.setHudText(formatReadout());
}

namespace {

// Which world axis is `v` closest to?  Used to label the BFS extent
// bars (X/Y/Z) without hard-coding wall vs floor convention.
const char* dominantAxisLabel(const float v[3]) {
    const float ax = std::abs(v[0]);
    const float ay = std::abs(v[1]);
    const float az = std::abs(v[2]);
    if (az >= ax && az >= ay) return "Z";
    if (ax >= ay) return "X";
    return "Y";
}

} // namespace

void LengthMeasurement::rebuildLaserOverlay(ViewportWindow& vp) {
    const auto& wp = first_pick_.world_pos;       // float[3] world click
    const auto& n  = first_pick_.world_normal;    // float[3] world normal

    // ---------- Tangent basis in world ----------
    // t1 = world-up Gram-Schmidt'd against n; fall back to world-X for
    // near-horizontal surfaces so the basis never degenerates.
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

    // ---------- Coplanar-patch BFS for face extent ----------
    // Read back the seed mesh, transform every vertex into world space,
    // build edge adjacency, BFS from the seed triangle keeping only
    // co-normal neighbours, then project each patch vertex into the
    // (t1, t2) basis to get the bounding extent of the face.  Stops
    // exactly at the face edge (no overshoot into adjacent geometry).
    ViewportWindow::MeshTriangles tris;
    bool have_extent = false;
    double min_t1 = 0.0, max_t1 = 0.0, min_t2 = 0.0, max_t2 = 0.0;
    if (vp.readbackMeshTriangles(first_pick_.model_id, first_pick_.mesh_id, tris)) {
        const size_t n_verts = tris.positions.size() / 3;
        const size_t n_tris  = tris.indices.size() / 3;
        if (n_tris > 0) {
            // Vertices → world.
            std::vector<float> wv(n_verts * 3);
            const float* M = first_pick_.composed_transform;
            for (size_t i = 0; i < n_verts; ++i) {
                const float* p = &tris.positions[i * 3];
                wv[i*3 + 0] = M[0]*p[0] + M[4]*p[1] + M[8]*p[2]  + M[12];
                wv[i*3 + 1] = M[1]*p[0] + M[5]*p[1] + M[9]*p[2]  + M[13];
                wv[i*3 + 2] = M[2]*p[0] + M[6]*p[1] + M[10]*p[2] + M[14];
            }
            // Per-tri world normals + edge adjacency.
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
            // Seed = nearest triangle to world click.
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
            // BFS coplanar.
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
            // Project unique patch vertices → tangent coords.
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
            QString("%1 extent: %2 m").arg(axis).arg(extent, 0, 'f', 3)));
        hud_lines << QString("%1 extent: %2 m").arg(axis).arg(extent, 0, 'f', 3);
    };
    if (have_extent && (max_t1 - min_t1) > 1e-6) pushBar(t1, min_t1, max_t1);
    if (have_extent && (max_t2 - min_t2) > 1e-6) pushBar(t2, min_t2, max_t2);

    // ---------- Hybrid: vertical raycast for horizontal surfaces ----------
    // For floors / ceilings (|n.z| close to 1) the BFS extents give the
    // floor footprint; the *useful* extra dimension is the room height,
    // which a single raycast in +n finds.  Skip on walls (|n.z| < 0.85)
    // — there the BFS already covers the user's intent.
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
                QString("%1: %2 m").arg(tag).arg(dist, 0, 'f', 3)));
            hud_lines << QString("%1: %2 m").arg(tag).arg(dist, 0, 'f', 3);
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
        return QString("Length: %1 m\nΔX: %2  ΔY: %3  ΔZ: %4 m")
            .arg(d, 0, 'f', 4)
            .arg(dx, 0, 'f', 4)
            .arg(dy, 0, 'f', 4)
            .arg(dz, 0, 'f', 4);
    }

    if (n == 3) {
        const auto& a = points_[0];
        const auto& b = points_[1];
        const auto& c = points_[2];
        // Angle at b (the middle-clicked vertex).
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
        return QString("Angle at pt 2: %1°\nTriangle area: %2 m²\nPerimeter: %3 m")
            .arg(angle_deg, 0, 'f', 2)
            .arg(triArea3(a, b, c), 0, 'f', 4)
            .arg(dist3(a, b) + dist3(b, c) + dist3(c, a), 0, 'f', 4);
    }

    // 4+ points: polygon area.
    const PolygonAreaResult r = polygonArea(points_);
    double perimeter = 0.0;
    for (size_t i = 0; i < n; ++i) {
        perimeter += dist3(points_[i], points_[(i + 1) % n]);
    }
    return QString("Polygon (%1 pts, %2)\nArea: %3 m²\nPerimeter: %4 m")
        .arg(n)
        .arg(r.method)
        .arg(r.area_m2, 0, 'f', 4)
        .arg(perimeter, 0, 'f', 4);
}
