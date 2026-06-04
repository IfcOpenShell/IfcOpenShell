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

#ifndef CAMERAMATH_H
#define CAMERAMATH_H

// Camera-matrix helpers. Eigen ships no lookAt/perspective/ortho out of
// the box (it's a math library, not a graphics one); QMatrix4x4 used to
// supply them. These functions reproduce QMatrix4x4's behaviour for the
// cases the viewport actually uses (right-handed lookAt, GL-clip
// perspective + ortho), expressed in column-major Eigen::Matrix4f so the
// result lands directly in u.view_proj for the GPU. Note both projection
// matrices target GL clip space [-1, 1] — callers pre-multiply by a
// z-remap matrix to land WebGPU's [0, 1].

#include <Eigen/Dense>

#include <cmath>

inline Eigen::Matrix4f lookAtRH(const Eigen::Vector3f& eye,
                                const Eigen::Vector3f& target,
                                const Eigen::Vector3f& up) {
    const Eigen::Vector3f f = (target - eye).normalized();
    const Eigen::Vector3f s = f.cross(up).normalized();
    const Eigen::Vector3f u = s.cross(f);
    Eigen::Matrix4f m = Eigen::Matrix4f::Identity();
    m(0, 0) =  s.x(); m(0, 1) =  s.y(); m(0, 2) =  s.z(); m(0, 3) = -s.dot(eye);
    m(1, 0) =  u.x(); m(1, 1) =  u.y(); m(1, 2) =  u.z(); m(1, 3) = -u.dot(eye);
    m(2, 0) = -f.x(); m(2, 1) = -f.y(); m(2, 2) = -f.z(); m(2, 3) =  f.dot(eye);
    return m;
}

inline Eigen::Matrix4f perspectiveYFovGL(float fovy_deg, float aspect,
                                         float near_plane, float far_plane) {
    const float fovy_rad = fovy_deg * float(M_PI) / 180.0f;
    const float t = std::tan(fovy_rad * 0.5f);
    Eigen::Matrix4f m = Eigen::Matrix4f::Zero();
    m(0, 0) = 1.0f / (aspect * t);
    m(1, 1) = 1.0f / t;
    m(2, 2) = -(far_plane + near_plane) / (far_plane - near_plane);
    m(2, 3) = -(2.0f * far_plane * near_plane) / (far_plane - near_plane);
    m(3, 2) = -1.0f;
    return m;
}

inline Eigen::Matrix4f orthoGL(float left, float right,
                               float bottom, float top,
                               float near_plane, float far_plane) {
    Eigen::Matrix4f m = Eigen::Matrix4f::Identity();
    m(0, 0) =  2.0f / (right - left);
    m(1, 1) =  2.0f / (top - bottom);
    m(2, 2) = -2.0f / (far_plane - near_plane);
    m(0, 3) = -(right + left) / (right - left);
    m(1, 3) = -(top + bottom) / (top - bottom);
    m(2, 3) = -(far_plane + near_plane) / (far_plane - near_plane);
    return m;
}

// Inverse-with-invertibility-check. QMatrix4x4::inverted(bool*)
// returned identity (silently) on a singular matrix and flipped the
// `ok` out-parameter; Eigen's .inverse() always runs even on singular
// input. computeInverseWithCheck is the safe equivalent.
inline bool tryInvert4f(const Eigen::Matrix4f& M, Eigen::Matrix4f& out) {
    bool invertible = false;
    M.computeInverseWithCheck(out, invertible, /*absDetThreshold=*/0);
    return invertible;
}

#endif  // CAMERAMATH_H
