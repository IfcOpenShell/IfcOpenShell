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

#include "FederationMath.h"

#include "geolocation_transform.h"   // x_axis_to_angle_deg
#include "unit_convert.h"            // convert

#include <cmath>

namespace {

constexpr double kPi       = 3.14159265358979323846;
constexpr double kDegToRad = kPi / 180.0;

Eigen::Matrix4d translation4(const Eigen::Vector3d& t) {
    Eigen::Matrix4d M = Eigen::Matrix4d::Identity();
    M(0, 3) = t.x();
    M(1, 3) = t.y();
    M(2, 3) = t.z();
    return M;
}

// Intrinsic XYZ Euler: R = R_z · R_y · R_x.
Eigen::Matrix4d eulerXYZ(const Eigen::Vector3d& rxyz_rad) {
    const Eigen::Matrix3d R3 =
        (Eigen::AngleAxisd(rxyz_rad.z(), Eigen::Vector3d::UnitZ()) *
         Eigen::AngleAxisd(rxyz_rad.y(), Eigen::Vector3d::UnitY()) *
         Eigen::AngleAxisd(rxyz_rad.x(), Eigen::Vector3d::UnitX())).matrix();
    Eigen::Matrix4d R = Eigen::Matrix4d::Identity();
    R.block<3, 3>(0, 0) = R3;
    return R;
}

}  // namespace

double federationUnitToMeters(const FederationConfig& cfg) {
    return convert(1.0, cfg.unit_prefix, cfg.unit_name, "", "METRE");
}

Eigen::Matrix4d composeFederatedFalseOrigin(const FederatedFalseOrigin& origin,
                                            const FederationConfig& cfg) {
    const double u = federationUnitToMeters(cfg);
    const Eigen::Vector3d xyz_m = origin.xyz * u;
    const double rz_rad = origin.rz_deg * kDegToRad;
    const Eigen::Matrix3d Rz =
        Eigen::AngleAxisd(rz_rad, Eigen::Vector3d::UnitZ()).matrix();
    Eigen::Matrix4d Rz4 = Eigen::Matrix4d::Identity();
    Rz4.block<3, 3>(0, 0) = Rz;
    return Rz4 * translation4(-xyz_m);
}

FederatedFalseOrigin
guessFederatedFalseOrigin(const Eigen::Vector3d& first_geometry_point_m,
                          const ModelGeoref& georef,
                          const FederationConfig& fed_cfg) {
    Eigen::Vector3d t_m = first_geometry_point_m;

    const bool use_coord_op = georef.has_coordinate_operation;
    if (use_coord_op) {
        const Eigen::Vector4d th(t_m.x(), t_m.y(), t_m.z(), 1.0);
        t_m = (georef.coordinate_operation_meters * th).head<3>();
    }

    const double u_fed = federationUnitToMeters(fed_cfg);
    const double u_fed_inv = (u_fed != 0.0) ? (1.0 / u_fed) : 1.0;

    FederatedFalseOrigin out;
    out.xyz = t_m * u_fed_inv;

    // Rotation: helmert grid-north baked into coordinate_operation_meters.
    // helmert_meters_from_parameters built that block as R_z(theta)·diag(fx,fy,fz)
    // with theta = atan2(xao, xaa); x_axis_to_angle_deg is `-theta` in degrees.
    if (use_coord_op) {
        const Eigen::Matrix4d& M = georef.coordinate_operation_meters;
        out.rz_deg = x_axis_to_angle_deg(M(0, 0), M(1, 0));
    }
    return out;
}

Eigen::Matrix4d composeModelTransformation(const ModelTransformation& xf,
                                           const FederationConfig& fed_cfg,
                                           const ModelUnits& model_units,
                                           const Eigen::Matrix4d& coordinate_operation_meters) {
    const double u_fed = federationUnitToMeters(fed_cfg);

    Eigen::Vector3d A_m;
    if (xf.a_frame == AFrame::ModelLocal) {
        // a is in the model's project length unit, expressed in the
        // pre-CoordinateOperation frame.  Convert to metres, then lift
        // through the CoordinateOperation.
        const Eigen::Vector4d a_h(
            xf.a.x() * model_units.project_length_to_meters,
            xf.a.y() * model_units.project_length_to_meters,
            xf.a.z() * model_units.project_length_to_meters,
            1.0);
        A_m = (coordinate_operation_meters * a_h).head<3>();
    } else {
        // a is in the model's map unit, expressed in the
        // post-CoordinateOperation frame.
        A_m = xf.a * model_units.map_unit_to_meters;
    }

    const Eigen::Vector3d B_m     = xf.b     * u_fed;
    const Eigen::Vector3d pivot_m = xf.pivot * u_fed;

    const Eigen::Matrix4d R_local = eulerXYZ(xf.rxyz_deg * kDegToRad);
    const Eigen::Matrix4d R_at_pivot =
        translation4(pivot_m) * R_local * translation4(-pivot_m);

    const Eigen::Vector4d Ah(A_m.x(), A_m.y(), A_m.z(), 1.0);
    const Eigen::Vector3d RA = (R_at_pivot * Ah).head<3>();
    const Eigen::Matrix4d T  = translation4(B_m - RA);

    return T * R_at_pivot;
}
