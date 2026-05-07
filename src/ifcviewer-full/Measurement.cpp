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

void AreaMeasurement::clear() {
    mesh_cache_.clear();
    selected_.clear();
    total_area_m2_ = 0.0;
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
    const uint64_t seed_key = triKey(pick.model_id, pick.mesh_id, seed);
    const bool removing = selected_.count(seed_key) > 0;
    double delta = 0.0;
    for (uint32_t t : patch) {
        const uint64_t k = triKey(pick.model_id, pick.mesh_id, t);
        if (removing) {
            if (selected_.erase(k) > 0) delta -= cache->tri_areas[t];
        } else {
            if (selected_.insert(k).second) delta += cache->tri_areas[t];
        }
    }
    total_area_m2_ += delta;

    qInfo("Area %s%.6f m^2  (total: %.6f m^2, %zu tris)",
          delta >= 0.0 ? "+" : "", delta,
          total_area_m2_, selected_.size());
}
