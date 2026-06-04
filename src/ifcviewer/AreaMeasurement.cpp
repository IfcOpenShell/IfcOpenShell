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

#include "AreaMeasurement.h"

#include "OverlayRenderer.h"
#include "ViewportWindow.h"

#include <cstdio>
#include <QString>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <limits>
#include <queue>
#include <unordered_set>

namespace {

// Undirected edge key between two mesh-local vertex indices.
uint64_t edgeKey(uint32_t a, uint32_t b) {
    if (a > b) std::swap(a, b);
    return (uint64_t(a) << 32) | uint64_t(b);
}

// Triangle area = 0.5 * |(b - a) × (c - a)|. Also returns the unit
// normal (zeroed for degenerate tris).
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

// Squared distance from point `p` to triangle (a, b, c) — clipped to
// the triangle's interior or boundary, whichever is closest. Standard
// Ericson "Real-Time Collision Detection" implementation; identical to
// the GL AreaMeasurement helper.
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

constexpr double kCoplanarDot = 0.9999;  // ~0.81° tolerance, matches GL

}  // namespace

AreaMeasurement::AreaMeasurement() = default;

void AreaMeasurement::clear(ViewportWindow& vp) {
    mesh_cache_.clear();
    selected_.clear();
    total_area_m2_ = 0.0;
    vp.setHighlightTriangles({}, 0, 0, 0, 0);
    vp.setOverlayLabels({});
}

AreaMeasurement::MeshAdj*
AreaMeasurement::meshAdj(ViewportWindow& vp,
                             uint32_t model_id, uint32_t mesh_id) {
    const uint64_t key = (uint64_t(model_id) << 32) | uint64_t(mesh_id);
    auto it = mesh_cache_.find(key);
    if (it != mesh_cache_.end()) return &it->second;

    // Need the raw positions + indices for adjacency. We never store
    // them in the per-mesh cache (positions can be hundreds of KB each
    // and live in the viewport already), so just look them up freshly
    // each time the user picks a brand-new mesh.
    ViewportWindow::MeshTriangles tris;
    if (!vp.readbackMeshTriangles(model_id, mesh_id, tris)) return nullptr;
    if (tris.indices.size() < 3) return nullptr;

    MeshAdj a;
    const size_t n_tris = tris.indices.size() / 3;
    a.tri_normals.resize(n_tris * 3);
    a.tri_areas.resize(n_tris);
    a.edges.reserve(n_tris * 3);
    for (size_t t = 0; t < n_tris; ++t) {
        const uint32_t ia = tris.indices[3 * t + 0];
        const uint32_t ib = tris.indices[3 * t + 1];
        const uint32_t ic = tris.indices[3 * t + 2];
        if (3 * ia + 2 >= tris.positions.size()
         || 3 * ib + 2 >= tris.positions.size()
         || 3 * ic + 2 >= tris.positions.size()) continue;
        const float* pa = &tris.positions[3 * ia];
        const float* pb = &tris.positions[3 * ib];
        const float* pc = &tris.positions[3 * ic];
        float n[3];
        a.tri_areas[t] = triAreaAndNormal(pa, pb, pc, n);
        a.tri_normals[3 * t + 0] = n[0];
        a.tri_normals[3 * t + 1] = n[1];
        a.tri_normals[3 * t + 2] = n[2];
        a.edges[edgeKey(ia, ib)].push_back(uint32_t(t));
        a.edges[edgeKey(ib, ic)].push_back(uint32_t(t));
        a.edges[edgeKey(ic, ia)].push_back(uint32_t(t));
    }
    return &mesh_cache_.emplace(key, std::move(a)).first->second;
}

void AreaMeasurement::onPick(ViewportWindow& vp,
                                 int x_phys, int y_phys, bool alt) {
    ViewportWindow::MeshLocalPick pick;
    if (!vp.pickMeshLocalAt(x_phys, y_phys, pick)) return;

    ViewportWindow::MeshTriangles tris;
    if (!vp.readbackMeshTriangles(pick.model_id, pick.mesh_id, tris)) return;
    const size_t n_tris = tris.indices.size() / 3;
    if (n_tris == 0) return;

    MeshAdj* adj = meshAdj(vp, pick.model_id, pick.mesh_id);
    if (!adj) return;

    // Seed: the triangle whose interior (or boundary) is closest to the
    // mesh-local pick point.
    uint32_t seed = 0;
    double best = std::numeric_limits<double>::infinity();
    for (size_t t = 0; t < n_tris; ++t) {
        const uint32_t ia = tris.indices[3 * t + 0];
        const uint32_t ib = tris.indices[3 * t + 1];
        const uint32_t ic = tris.indices[3 * t + 2];
        const double d = pointTriangleDistSq(pick.mesh_local,
                                             &tris.positions[3 * ia],
                                             &tris.positions[3 * ib],
                                             &tris.positions[3 * ic]);
        if (d < best) { best = d; seed = uint32_t(t); }
    }

    // Coplanar patch via BFS over shared edges. Alt skips the expand
    // (single-triangle accumulate).
    std::vector<uint32_t> patch;
    if (alt) {
        patch.push_back(seed);
    } else {
        const float* sn = &adj->tri_normals[3 * seed];
        std::unordered_set<uint32_t> visited;
        visited.insert(seed);
        std::queue<uint32_t> frontier;
        frontier.push(seed);
        while (!frontier.empty()) {
            const uint32_t t = frontier.front(); frontier.pop();
            patch.push_back(t);
            for (int e = 0; e < 3; ++e) {
                const uint32_t ia = tris.indices[3 * t + e];
                const uint32_t ib = tris.indices[3 * t + (e + 1) % 3];
                auto eit = adj->edges.find(edgeKey(ia, ib));
                if (eit == adj->edges.end()) continue;
                for (uint32_t nt : eit->second) {
                    if (nt == t || visited.count(nt)) continue;
                    const float* nn = &adj->tri_normals[3 * nt];
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
                if (t < adj->tri_areas.size()) delta -= adj->tri_areas[t];
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
                if (t < adj->tri_areas.size()) delta += adj->tri_areas[t];
            }
        }
    }
    total_area_m2_ += delta;

    rebuildHighlightAndLabels(vp);

    std::fprintf(stderr,
        "[info] [wgpu area] %s%.6f m^2  (total: %.6f m^2, %zu tris)\n",
        delta >= 0.0 ? "+" : "", delta,
        total_area_m2_, selected_.size());
}

void AreaMeasurement::rebuildHighlightAndLabels(ViewportWindow& vp) {
    // 1) Highlight triangle list — each selected tri's three vertices
    //    transformed by its captured composed_transform. Push as a
    //    flat world-space tri list; the overlay tints them translucent
    //    cyan to match GL.
    std::vector<float> world_xyz;
    world_xyz.reserve(selected_.size() * 9);

    // Cache the latest MeshTriangles per (model,mesh) for this rebuild
    // to avoid repeated viewport lookups when many tris share a mesh.
    std::unordered_map<uint64_t, ViewportWindow::MeshTriangles> tris_cache;

    auto get_tris = [&](uint32_t model_id, uint32_t mesh_id)
                       -> ViewportWindow::MeshTriangles* {
        const uint64_t k = (uint64_t(model_id) << 32) | uint64_t(mesh_id);
        auto it = tris_cache.find(k);
        if (it != tris_cache.end()) return &it->second;
        ViewportWindow::MeshTriangles t;
        if (!vp.readbackMeshTriangles(model_id, mesh_id, t)) return nullptr;
        return &tris_cache.emplace(k, std::move(t)).first->second;
    };

    for (const auto& [key, sel] : selected_) {
        ViewportWindow::MeshTriangles* t = get_tris(sel.model_id, sel.mesh_id);
        if (!t) continue;
        if (size_t(sel.tri) * 3 + 2 >= t->indices.size()) continue;
        const float* M = sel.composed_transform;  // column-major
        for (int e = 0; e < 3; ++e) {
            const uint32_t vi = t->indices[3 * sel.tri + e];
            if (3 * vi + 2 >= t->positions.size()) continue;
            const float* p = &t->positions[3 * vi];
            // World = M * (p, 1). Column-major: M[col*4 + row].
            const float wx = M[0]*p[0] + M[4]*p[1] + M[8]*p[2]  + M[12];
            const float wy = M[1]*p[0] + M[5]*p[1] + M[9]*p[2]  + M[13];
            const float wz = M[2]*p[0] + M[6]*p[1] + M[10]*p[2] + M[14];
            world_xyz.push_back(wx);
            world_xyz.push_back(wy);
            world_xyz.push_back(wz);
        }
    }
    // Bonsai's area-tool cyan tint: 0.20, 0.85, 1.00 @ 0.45 alpha.
    vp.setHighlightTriangles(world_xyz, 0.20f, 0.85f, 1.00f, 0.45f);

    // 2) Per-patch labels via connected-components sweep restricted to
    //    selected tris, one label per component at its area-weighted
    //    centroid (mesh-local → world via the captured transform).
    std::unordered_map<uint32_t, std::vector<const SelectedTri*>> by_object;
    for (const auto& [key, sel] : selected_) {
        const uint32_t object_id = uint32_t(key >> 32);
        by_object[object_id].push_back(&sel);
    }

    std::vector<OverlayRenderer::Label> labels;
    for (const auto& [obj_id, sels] : by_object) {
        if (sels.empty()) continue;
        const SelectedTri& any = *sels[0];
        ViewportWindow::MeshTriangles* t = get_tris(any.model_id, any.mesh_id);
        if (!t) continue;
        MeshAdj* adj = meshAdj(vp, any.model_id, any.mesh_id);
        if (!adj) continue;

        std::unordered_set<uint32_t> remaining;
        remaining.reserve(sels.size());
        for (const SelectedTri* s : sels) remaining.insert(s->tri);

        while (!remaining.empty()) {
            const uint32_t start = *remaining.begin();
            std::unordered_set<uint32_t> in_comp{start};
            std::queue<uint32_t> frontier;
            frontier.push(start);
            std::vector<uint32_t> component;
            while (!frontier.empty()) {
                const uint32_t tri = frontier.front(); frontier.pop();
                component.push_back(tri);
                if (size_t(tri) * 3 + 2 >= t->indices.size()) continue;
                for (int e = 0; e < 3; ++e) {
                    const uint32_t ia = t->indices[3 * tri + e];
                    const uint32_t ib = t->indices[3 * tri + (e + 1) % 3];
                    auto eit = adj->edges.find(edgeKey(ia, ib));
                    if (eit == adj->edges.end()) continue;
                    for (uint32_t nt : eit->second) {
                        if (in_comp.count(nt) || remaining.count(nt) == 0) continue;
                        in_comp.insert(nt);
                        frontier.push(nt);
                    }
                }
            }
            for (uint32_t tri : component) remaining.erase(tri);

            double area = 0.0, cx = 0.0, cy = 0.0, cz = 0.0;
            for (uint32_t tri : component) {
                if (size_t(tri) >= adj->tri_areas.size()) continue;
                const double a = adj->tri_areas[tri];
                area += a;
                const uint32_t ia = t->indices[3 * tri + 0];
                const uint32_t ib = t->indices[3 * tri + 1];
                const uint32_t ic = t->indices[3 * tri + 2];
                const float* va = &t->positions[3 * ia];
                const float* vb = &t->positions[3 * ib];
                const float* vc = &t->positions[3 * ic];
                cx += a * (double(va[0]) + vb[0] + vc[0]) / 3.0;
                cy += a * (double(va[1]) + vb[1] + vc[1]) / 3.0;
                cz += a * (double(va[2]) + vb[2] + vc[2]) / 3.0;
            }
            if (area <= 0.0) continue;
            cx /= area; cy /= area; cz /= area;

            const float* M = any.composed_transform;
            OverlayRenderer::Label lbl;
            lbl.world_pos[0] = float(M[0]*cx + M[4]*cy + M[8]*cz  + M[12]);
            lbl.world_pos[1] = float(M[1]*cx + M[5]*cy + M[9]*cz  + M[13]);
            lbl.world_pos[2] = float(M[2]*cx + M[6]*cy + M[10]*cz + M[14]);
            lbl.text = QString::number(area, 'f', 4) + QStringLiteral(" m²");
            labels.push_back(std::move(lbl));
        }
    }
    vp.setOverlayLabels(labels);
}
