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

// Frustum-plane extraction from a column-major view-projection matrix
// (Qt convention: element [c*4 + r] is column c, row r). Plane format
// is (a, b, c, d) with `a*x + b*y + c*z + d >= 0` meaning the point is
// inside. The clip-space convention is WebGPU's z ∈ [0, 1] (near is
// `r2`, not `r3 + r2`); matches the projection matrices produced by
// the GL-clip → WebGPU z-remap further down the pipeline.
inline void extractFrustumPlanes(const float vp[16], float planes[6][4]) {
    auto rowVec = [&](int row, float out[4]) {
        out[0] = vp[0 * 4 + row];
        out[1] = vp[1 * 4 + row];
        out[2] = vp[2 * 4 + row];
        out[3] = vp[3 * 4 + row];
    };
    auto normalize = [](float p[4]) {
        const float len = std::sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
        if (len > 0.0f) {
            const float inv = 1.0f / len;
            p[0] *= inv; p[1] *= inv; p[2] *= inv; p[3] *= inv;
        }
    };
    float r0[4], r1[4], r2[4], r3[4];
    rowVec(0, r0); rowVec(1, r1); rowVec(2, r2); rowVec(3, r3);
    // left, right, bottom, top, near (z >= 0), far
    for (int i = 0; i < 4; ++i) {
        planes[0][i] = r3[i] + r0[i];
        planes[1][i] = r3[i] - r0[i];
        planes[2][i] = r3[i] + r1[i];
        planes[3][i] = r3[i] - r1[i];
        planes[4][i] = r2[i];
        planes[5][i] = r3[i] - r2[i];
    }
    for (int p = 0; p < 6; ++p) normalize(planes[p]);
}

// Returns false iff the AABB is fully outside any one plane (early-
// rejects trivially-invisible instances). May return true for boxes
// that straddle the frustum — those still need to draw.
inline bool aabbInFrustum(const float mn[3], const float mx[3],
                          const float planes[6][4]) {
    for (int p = 0; p < 6; ++p) {
        const float a = planes[p][0], b = planes[p][1];
        const float c = planes[p][2], d = planes[p][3];
        // p-vertex: the AABB corner furthest along the plane normal.
        const float px = (a >= 0.0f) ? mx[0] : mn[0];
        const float py = (b >= 0.0f) ? mx[1] : mn[1];
        const float pz = (c >= 0.0f) ? mx[2] : mn[2];
        if (a * px + b * py + c * pz + d < 0.0f) return false;
    }
    return true;
}

#endif  // CAMERAMATH_H
