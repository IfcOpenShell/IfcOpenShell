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

#include "geolocation_transform.h"

#include <cmath>

Eigen::Matrix4d local_to_global(const Eigen::Matrix4d& matrix,
                                const HelmertTransformation& p) {
    const double theta = std::atan2(p.xao, p.xaa);
    const double c = std::cos(theta);
    const double s = std::sin(theta);

    Eigen::Matrix4d S = Eigen::Matrix4d::Identity();
    S(0, 0) = p.scale * p.factor_x;
    S(1, 1) = p.scale * p.factor_y;
    S(2, 2) = p.scale * p.factor_z;

    Eigen::Matrix4d R = Eigen::Matrix4d::Identity();
    R(0, 0) = c;
    R(0, 1) = -s;
    R(1, 0) = s;
    R(1, 1) = c;

    Eigen::Matrix4d result = R * S * matrix;
    // The scale was baked into the rotation+scale matrix so each axis column
    // ended up scaled.  Renormalise so the rotation part is pure orientation
    // and the translation alone carries the scaled offsets.
    for (int col = 0; col < 3; ++col) {
        Eigen::Vector3d v = result.block<3, 1>(0, col);
        const double n = v.norm();
        if (n > 0.0) {
            result.block<3, 1>(0, col) = v / n;
        }
    }
    result(0, 3) += p.e;
    result(1, 3) += p.n;
    result(2, 3) += p.h;
    return result;
}

Eigen::Matrix4d helmert_meters_from_parameters(const HelmertTransformation& p,
                                               double map_unit_to_meters) {
    const double theta = std::atan2(p.xao, p.xaa);
    const double c = std::cos(theta);
    const double s = std::sin(theta);

    Eigen::Matrix4d M = Eigen::Matrix4d::Identity();
    // R_z(theta) · diag(fx, fy, fz).  Factors stay in the rotation block so
    // they apply to placement translations on compose; this is the behaviour
    // IfcMapConversionScaled actually wants ("grid distance ≠ ground
    // distance" — buildings on the grid should appear scaled by f).
    M(0, 0) = c * p.factor_x;
    M(0, 1) = -s * p.factor_y;
    M(0, 2) = 0.0;
    M(1, 0) = s * p.factor_x;
    M(1, 1) = c * p.factor_y;
    M(1, 2) = 0.0;
    M(2, 0) = 0.0;
    M(2, 1) = 0.0;
    M(2, 2) = p.factor_z;
    M(0, 3) = p.e * map_unit_to_meters;
    M(1, 3) = p.n * map_unit_to_meters;
    M(2, 3) = p.h * map_unit_to_meters;
    return M;
}

double x_axis_to_angle_deg(double xaa, double xao) {
    constexpr double PI = 3.14159265358979323846;
    return -std::atan2(xao, xaa) * (180.0 / PI);
}
