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

#ifndef WGPULENGTHMEASUREMENT_H
#define WGPULENGTHMEASUREMENT_H

#include "WgpuViewportWindow.h"

#include <QString>

#include <array>
#include <vector>

// Click-to-place length / angle / area measurement for the wgpu viewport.
// Mirrors src/bonsaiviewer/Measurement.h's LengthMeasurement — the
// readout adapts to the running point count:
//
//   1 point  → laser-measure: BFS the coplanar surface patch the click
//              landed on, project its vertices into the surface's own
//              tangent basis to get the face extent, plus a vertical
//              raycast for floor/ceiling distance on horizontal surfaces.
//   2 points → straight-line distance + ΔX/ΔY/ΔZ stair-step + optional
//              perpendicular projection when both picks landed on
//              near-parallel surfaces.
//   3 points → angle at the middle vertex + triangle area + perimeter.
//   4+ pts   → polygon area via best-fit-plane shoelace if near-planar,
//              fan-triangulated otherwise; perimeter on the closed loop.
//
// Pushes the running set as overlay points + the connecting polyline +
// per-segment labels to the viewport; the multi-line HUD carries the
// adaptive readout.
class WgpuLengthMeasurement {
public:
    WgpuLengthMeasurement();

    // Pixel coords are physical (post-DPR). `alt` is currently unused
    // (kept for API symmetry with the Area tool).
    void onPick(WgpuViewportWindow& vp, int x_phys, int y_phys, bool alt);
    void removeLastPoint(WgpuViewportWindow& vp);
    void clear(WgpuViewportWindow& vp);

    size_t pointCount() const { return points_.size(); }

private:
    void rebuildOverlay(WgpuViewportWindow& vp);
    void rebuildLaserOverlay(WgpuViewportWindow& vp);
    QString formatReadout() const;

    std::vector<std::array<float, 3>> points_;
    std::vector<std::array<float, 3>> normals_;   // surface normal at each pick

    // Captured at the very first pick of a fresh sequence and never
    // updated afterwards. Used by the 1-pt laser BFS to locate the
    // mesh-local position of points_[0] without re-picking. Stays valid
    // while points_[0] does (pop_back never touches the first element).
    WgpuViewportWindow::MeshLocalPick first_pick_{};
};

#endif  // WGPULENGTHMEASUREMENT_H
