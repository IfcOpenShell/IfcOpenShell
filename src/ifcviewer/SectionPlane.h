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

#ifndef IFCVIEWER_SECTIONPLANE_H
#define IFCVIEWER_SECTIONPLANE_H

#include <Eigen/Dense>

// One section plane as the renderer + overlay visualiser consume it. Lives
// in its own Qt-free header so ViewportCore can include it without
// dragging in OverlayRenderer's QString / QHash dependencies.
//
// The viewport owns the authoritative state vector (the section tool
// mutates it; the per-frame uniform packs it for the WGSL shader; the
// overlay reads from a non-owning span every frame). Held by value
// because the struct is small and copies happen at most six times per
// frame (kMaxSectionPlanes).
struct SectionPlane {
    Eigen::Vector3f n      = Eigen::Vector3f::UnitZ(); // unit normal
    float           d      = 0.0f;                     // -dot(n, origin)
    Eigen::Vector3f origin = Eigen::Vector3f::Zero();  // surface point at the
                                                       // moment the plane was added
    float    visual_radius = 0.0f;
};

#endif
