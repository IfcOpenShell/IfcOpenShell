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

#ifndef IFCVIEWER_FULL_MEASUREMENT_H
#define IFCVIEWER_FULL_MEASUREMENT_H

#include <cstdint>
#include <unordered_map>
#include <unordered_set>
#include <vector>

class ViewportWindow;

// Sum of mesh-local volumes (m³) of every instance whose object_id is in
// `object_ids`.  Groups by (model, mesh) so each unique mesh is read back
// from the GPU at most once per call; instances of the same mesh are scaled
// by |det(placement_3x3)| to pick up mapped-item scale/mirror.  Volume is
// taken as the absolute value of the signed-tetrahedra sum, so winding
// convention does not matter.  Returns 0.0 for empty input or when nothing
// resolves.  Recomputes from scratch on every call — no cache.
double volumeOfObjects(ViewportWindow& vp,
                       const std::vector<uint32_t>& object_ids);

// Click-to-accumulate area measurement.  Each pick resolves the screen
// click to a (model, mesh, triangle) using ViewportWindow's primitives,
// expands it into the connected coplanar patch (BFS over shared edges,
// dot(normal, seed_normal) > 0.9999), then either adds or removes that
// patch from the running set depending on whether the seed triangle was
// already in.  Alt-click skips the BFS expansion (single-triangle).
// Picks across different meshes are kept as separate patches and their
// areas are summed.
//
// State is cleared on construction, on clear(), and is expected to be
// reset by the host (e.g. when the viewport's area tool toggles off).
class AreaMeasurement {
public:
    AreaMeasurement();

    // Main entry point: handle one click in area-tool mode.  alt = true
    // suppresses BFS expansion.  Logs the per-click delta and running total
    // via qInfo.  Misses are silent.
    void onPick(ViewportWindow& vp, int x, int y, bool alt);

    // Wipe all accumulated triangles and per-mesh adjacency caches.
    void clear();

    double totalArea() const { return total_area_m2_; }
    size_t triangleCount() const { return selected_.size(); }

private:
    // Cached per-mesh data: triangles + edge→triangles adjacency.  Keyed
    // by (model_id << 32) | mesh_id.  Filled lazily on first pick of that
    // mesh, dropped on clear().
    struct MeshCache {
        std::vector<float>    positions;     // 3 * N_verts
        std::vector<uint32_t> indices;       // 3 * N_tris
        std::vector<float>    tri_normals;   // 3 * N_tris (unit, mesh-local)
        std::vector<float>    tri_areas;     // N_tris
        // edge_key (min<<32 | max) → list of triangle indices touching it.
        std::unordered_map<uint64_t, std::vector<uint32_t>> edges;
    };
    MeshCache* meshCache(ViewportWindow& vp, uint32_t model_id, uint32_t mesh_id);

    // Selection key: (uint64) packing model_id (high 24), mesh_id (mid 24),
    // triangle index (low 16).  16 bits is enough — meshes with > 65k tris
    // are rare and the streamer chunks them anyway.
    static uint64_t triKey(uint32_t model_id, uint32_t mesh_id, uint32_t tri) {
        return (uint64_t(model_id) << 40) | (uint64_t(mesh_id) << 16) | uint64_t(tri);
    }

    std::unordered_map<uint64_t, MeshCache> mesh_cache_;
    std::unordered_set<uint64_t>            selected_;
    double                                  total_area_m2_ = 0.0;
};

#endif // IFCVIEWER_FULL_MEASUREMENT_H
