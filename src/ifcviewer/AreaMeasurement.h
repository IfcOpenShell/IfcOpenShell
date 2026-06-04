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

#ifndef WGPUAREAMEASUREMENT_H
#define WGPUAREAMEASUREMENT_H

#include <cstddef>
#include <cstdint>
#include <unordered_map>
#include <vector>

class ViewportWindow;

// Click-to-accumulate area measurement for the wgpu viewport. Mirrors
// src/bonsaiviewer/Measurement.h's AreaMeasurement: each pick resolves
// to (instance, triangle) via ViewportWindow::pickMeshLocalAt, then
// either adds or removes the connected coplanar patch (BFS over shared
// edges, dot(normal, seed_normal) > 0.9999) depending on whether the
// seed triangle was already in the running set. Alt-click skips the BFS.
// Picks on different instances (even of the same mesh) are kept as
// separate patches.
//
// On every mutation the world-space triangles of the running set are
// pushed to ViewportWindow::setHighlightTriangles for the
// translucent cyan patch shading, and per-component "X.XXXX m²" labels
// are pushed to setOverlayLabels at each connected component's
// area-weighted centroid.
class AreaMeasurement {
public:
    AreaMeasurement();

    // Pixel coords are physical (post-DPR), to match
    // ViewportWindow::pickMeshLocalAt's convention.
    void onPick(ViewportWindow& vp, int x_phys, int y_phys, bool alt);
    void clear(ViewportWindow& vp);

    double totalArea() const { return total_area_m2_; }
    size_t triangleCount() const { return selected_.size(); }

private:
    // Cached per-mesh derived data: triangle normals + areas + edge
    // adjacency. Computed once per (model, mesh) on first pick; the
    // raw positions + indices live in
    // ViewportWindow::readbackMeshTriangles' CPU shadow.
    struct MeshAdj {
        std::vector<float>    tri_normals;  // 3 floats per tri (unit, mesh-local)
        std::vector<float>    tri_areas;    // mesh-local area per tri
        // edge_key (min<<32 | max) → list of triangle indices touching it.
        std::unordered_map<uint64_t, std::vector<uint32_t>> edges;
    };
    // Keyed by (model_id << 32) | mesh_id.
    MeshAdj* meshAdj(ViewportWindow& vp,
                     uint32_t model_id, uint32_t mesh_id);

    // Per-selected-triangle record. The composed transform is captured
    // at pick time so highlight rebuilds don't have to re-query the
    // viewport for it (and so the overlay keeps working if the picked
    // instance later goes hidden).
    struct SelectedTri {
        uint32_t model_id;
        uint32_t mesh_id;
        uint32_t tri;
        float    composed_transform[16];
    };

    // Selection key: object_id (high 32) | tri index (low 32). Packing
    // by object_id rather than mesh_id keeps two distinct instances of
    // the same mesh contributing independently — matches the GL impl.
    static uint64_t triKey(uint32_t object_id, uint32_t tri) {
        return (uint64_t(object_id) << 32) | uint64_t(tri);
    }

    void rebuildHighlightAndLabels(ViewportWindow& vp);

    std::unordered_map<uint64_t, MeshAdj>     mesh_cache_;
    std::unordered_map<uint64_t, SelectedTri> selected_;
    double                                    total_area_m2_ = 0.0;
};

#endif  // WGPUAREAMEASUREMENT_H
