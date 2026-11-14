/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 ********************************************************************************/

#include "ViewportFog.h"

#include <algorithm>

void ViewportFog::set(int mode, float near, float far, float density,
                      float r, float g, float b) {
    mode_ = static_cast<ViewportFogMode>(std::clamp(mode, 0, 2));
    // Three.js Fog defaults near=1; keep a small floor so smoothstep is stable.
    near_     = std::max(near, 1e-3f);
    far_      = std::max(far, near_ + 1e-3f);
    density_  = std::max(density, 0.0f);
    color_    = {r, g, b, 1.0f};
}

void ViewportFog::writeUniformTail(float camera_pos[4],
                                   float view_forward[4],
                                   float fog_color[4],
                                   float fog_params[4],
                                   const Eigen::Vector3f& eye,
                                   const Eigen::Vector3f& forward) const {
    camera_pos[0] = eye.x();
    camera_pos[1] = eye.y();
    camera_pos[2] = eye.z();
    camera_pos[3] = 0.0f;

    view_forward[0] = forward.x();
    view_forward[1] = forward.y();
    view_forward[2] = forward.z();
    view_forward[3] = 0.0f;

    fog_color[0] = color_.x();
    fog_color[1] = color_.y();
    fog_color[2] = color_.z();
    fog_color[3] = 0.0f;

    fog_params[0] = near_;
    fog_params[1] = far_;
    fog_params[2] = density_;
    fog_params[3] = float(int(mode_));
}
