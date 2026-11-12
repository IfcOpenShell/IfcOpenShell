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

#ifndef IFCVIEWER_OVERLAYFRAME_H
#define IFCVIEWER_OVERLAYFRAME_H

#include <Eigen/Dense>

// Per-frame snapshot of viewport state that every overlay needs. Built
// once at the top of render() and passed by const-ref to each encodeX()
// call so the overlay renderer never reaches back into the viewport.
// Qt-free so ViewportHost can carry it as a callback param.
struct OverlayFrame {
    Eigen::Matrix4f view_proj      = Eigen::Matrix4f::Identity();
    Eigen::Vector3f camera_target  = Eigen::Vector3f::Zero();
    float      camera_distance     = 5.0f;
    float      camera_yaw_deg      = 0.0f;
    float      camera_pitch_deg    = 0.0f;
    float      camera_fov_y_deg    = 45.0f;
    int        viewport_w_px       = 0;
    int        viewport_h_px       = 0;
    int        device_pixel_ratio  = 1;
};

#endif  // IFCVIEWER_OVERLAYFRAME_H
