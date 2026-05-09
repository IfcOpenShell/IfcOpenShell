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

#include <cstddef>
#include "ViewportWindow.h"
#include <QString>
#include <array>
#include <cstdint>
#include <unordered_map>
#include <vector>

// Sum of mesh-local volumes (m³) of every instance whose object_id is in
// `object_ids`.  Groups by (model, mesh) so each unique mesh is read back
// from the GPU at most once per call; instances of the same mesh are scaled
// by |det(placement_3x3)| to pick up mapped-item scale/mirror.  Volume is
// taken as the absolute value of the signed-tetrahedra sum, so winding
// convention does not matter.  Returns 0.0 for empty input or when nothing
// resolves.  Recomputes from scratch on every call — no cache.
double volumeOfObjects(ViewportWindow& vp,
                       const std::vector<uint32_t>& object_ids);

// Per-object volumes (m³).  Same algorithm as volumeOfObjects but
// attributed per id rather than summed.  Skips ids that don't resolve
// to a live instance, so the result may be shorter than the input.
// Used by MainWindow's volume readout to drive both the total HUD and
// the per-object overlay labels.
std::vector<std::pair<uint32_t, double>>
volumesPerObject(ViewportWindow& vp,
                 const std::vector<uint32_t>& object_ids);

// Click-to-accumulate area measurement.  Each pick resolves the screen
// click to a (instance, triangle) using ViewportWindow's primitives,
// expands it into the connected coplanar patch (BFS over shared edges,
// dot(normal, seed_normal) > 0.9999), then either adds or removes that
// patch from the running set depending on whether the seed triangle was
// already in.  Alt-click skips the BFS expansion (single-triangle).
// Picks on different instances (even of the same mesh) are kept as
// separate patches and their areas are summed.
//
// On every pick the world-space triangles of the running set are pushed
// to ViewportWindow::setHighlightTriangles for in-viewport shading.
// State is cleared on construction, on clear(), and is expected to be
// reset by the host (e.g. when the viewport's area tool toggles off).
class AreaMeasurement {
public:
    AreaMeasurement();

    // Main entry point: handle one click in area-tool mode.  alt = true
    // suppresses BFS expansion.  Logs the per-click delta and running total
    // via qInfo.  Misses are silent.
    void onPick(ViewportWindow& vp, int x, int y, bool alt);

    // Wipe all accumulated triangles, per-mesh adjacency caches, and the
    // viewport overlay.
    void clear(ViewportWindow& vp);

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

    // Per-selected-triangle record.  The composed transform is captured at
    // pick time so the overlay rebuild doesn't have to re-query the
    // viewport for it (and so the overlay keeps working if the picked
    // instance later goes hidden).
    struct SelectedTri {
        uint32_t model_id;
        uint32_t mesh_id;
        uint32_t tri;
        float    composed_transform[16];
    };

    // Selection key: object_id (high 32) | tri index (low 32).  Packing
    // by object_id rather than mesh_id means two distinct instances of
    // the same mesh contribute independently, as the user spec'd.
    static uint64_t triKey(uint32_t object_id, uint32_t tri) {
        return (uint64_t(object_id) << 32) | uint64_t(tri);
    }

    void rebuildHighlight(ViewportWindow& vp);

    std::unordered_map<uint64_t, MeshCache>    mesh_cache_;
    std::unordered_map<uint64_t, SelectedTri>  selected_;
    double                                     total_area_m2_ = 0.0;
};

// Click-to-place length / angle / area measurement.  Each pick appends a
// world-space point.  The readout adapts to the point count:
//
//   1 point  → "laser-measure" mode: 6 rays (±surface-normal, ±tangent₁,
//              ±tangent₂ in the surface's own basis) trace into the scene.
//              On a wall this gives thickness + floor-to-ceiling height +
//              length-along-wall in one click.  Tangent₁ is world up
//              projected onto the surface plane (Gram-Schmidt against the
//              normal); tangent₂ = normal × tangent₁.
//   2 points → straight-line distance plus axis-aligned ΔX/ΔY/ΔZ
//   3 points → angle at the middle vertex plus the triangle's area
//   4+       → polygon area: best-fit-plane shoelace if the points are
//              near-coplanar (RMS plane distance < 1e-3 of the bounding
//              box), else fan-triangulated from the first point
//
// Clicked points are pushed to the viewport overlay as small dots and
// the connecting polyline (or the laser rays for 1-point); readouts
// go to the multi-line HUD.
class LengthMeasurement {
public:
    LengthMeasurement();

    void onPick(ViewportWindow& vp, int x, int y, bool alt);
    void removeLastPoint(ViewportWindow& vp);
    void clear(ViewportWindow& vp);

    size_t pointCount() const { return points_.size(); }

private:
    void rebuildOverlay(ViewportWindow& vp);
    void rebuildLaserOverlay(ViewportWindow& vp);
    QString formatReadout() const;

    std::vector<std::array<float, 3>> points_;
    std::vector<std::array<float, 3>> normals_;  // surface normal at each pick

    // Captured at the very first pick of a fresh sequence and never
    // updated afterwards.  Used by the 1-pt laser BFS to re-locate the
    // mesh-local position of points_[0] without re-picking.  Stays valid
    // while points_[0] does (pop_back never touches the first element).
    ViewportWindow::MeshLocalPick first_pick_{};
};

#endif // IFCVIEWER_FULL_MEASUREMENT_H
