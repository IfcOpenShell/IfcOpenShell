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

// Qt-free half of the federation transformation pipeline: the value types and
// the pure compose math over them.
//
// Lives apart from Federation.h so IfcViewerCore — and through it the
// Emscripten build — can compose federated transforms without linking Qt or
// IfcParse.  What stays in Federation.h is everything that genuinely needs
// them: computeModelGeoref (reads an ifcopenshell::file) and the Federation
// document model (a QObject that persists .ifcfed).
//
// The pipeline comment in Federation.h describes how these compose.

#ifndef FEDERATIONMATH_H
#define FEDERATIONMATH_H

#include <Eigen/Dense>

#include <string>

// Federation-wide unit; the value space for FederatedFalseOrigin.xyz and
// ModelTransformation::{b, pivot}.
struct FederationConfig {
    // IfcSIUnit name ("METRE") or IfcConversionBasedUnit name ("foot", "inch").
    std::string unit_name   = "METRE";
    // SI prefix ("MILLI", "KILO", ...) — empty for unprefixed or for
    // conversion-based units.
    std::string unit_prefix = "";
};

// FederatedFalseOrigin — the user-nominated federation origin.  Authoring
// intent is "nominate this XYZ as the new origin, with optional Z-axis
// heading rotation".  Composed as R_z(rz_deg) · T(-xyz_in_metres).
struct FederatedFalseOrigin {
    Eigen::Vector3d xyz    = Eigen::Vector3d::Zero();   // federation unit
    double          rz_deg = 0.0;
};

// Frame in which ModelTransformation.a is expressed.
//   ModelLocal  — pre-CoordinateOperation model coordinates, in the model's
//                 project length unit
//   ModelGlobal — post-CoordinateOperation model coordinates, in the model's
//                 map unit
enum class AFrame { ModelLocal, ModelGlobal };

// ModelTransformation — the per-model placement within the federation.
// Authoring intent is "rotate the model around `pivot`, then translate so
// that point `a` lands at point `b`".  Composed as
//
//     R_local    = R_z(rz) · R_y(ry) · R_x(rx)            [intrinsic XYZ]
//     R_at_pivot = T(pivot_m) · R_local · T(-pivot_m)
//     result     = T(b_m - R_at_pivot · a_m) · R_at_pivot
struct ModelTransformation {
    AFrame          a_frame  = AFrame::ModelGlobal;
    Eigen::Vector3d a        = Eigen::Vector3d::Zero();   // model project / map unit
    Eigen::Vector3d b        = Eigen::Vector3d::Zero();   // federation unit
    Eigen::Vector3d rxyz_deg = Eigen::Vector3d::Zero();   // degrees, intrinsic XYZ
    Eigen::Vector3d pivot    = Eigen::Vector3d::Zero();   // federation unit
};

// Per-model unit scales captured at load time.  project_length_to_meters comes
// from calculate_unit_scale(file, "LENGTHUNIT").  map_unit_to_meters is derived
// from IfcMapConversion.Scale as project_length_to_meters / Scale; the
// IfcProjectedCRS.MapUnit named unit is metadata and does not affect the
// transform composition.
struct ModelUnits {
    double project_length_to_meters = 1.0;
    double map_unit_to_meters       = 1.0;
};

// Per-model georeferencing data derived from the IFC.
// `coordinate_operation_meters` is the helmert · inv(wcs) matrix in metres
// representing the IfcCoordinateOperation; consumers compose it before
// FederatedFalseOrigin / ModelTransformation at upload time.  When the
// model has no map conversion, `has_coordinate_operation == false` and the
// matrix is identity.
struct ModelGeoref {
    ModelUnits      units;
    Eigen::Matrix4d coordinate_operation_meters = Eigen::Matrix4d::Identity();
    bool            has_coordinate_operation    = false;
};

// computeModelGeoref, which fills a ModelGeoref from an ifcopenshell::file,
// stays in Federation.h — it needs IfcParse and the geolocation helpers.

// Build a FederatedFalseOrigin guess so that a model lands near the
// federation origin instead of out at its surveyor coordinates.  Designed
// to work without an open IFC file so it's usable from sidecar-only loads
// (the inputs are all derivable from the resident MeshInfo + InstanceInfo
// data + ModelGeoref).
//
// Position: `first_geometry_point_m` is a point that actually lies on the
// model's first instance's geometry, in metres, pre-CoordinateOperation —
// typically the world-space centre of the first instance's mesh AABB
// (instance0.placement_transformation * mesh.local_aabb_center).  We use
// a real geometry point rather than the instance's placement translation
// because IFC placements often live far from the actual geometry (long
// ObjectPlacement chains, intermediate local coordinate systems).  The
// point is lifted through `georef.coordinate_operation_meters` when one
// is present, then expressed in the federation unit.
//
// Rotation: read directly from `georef.coordinate_operation_meters`
// when `has_coordinate_operation` (this is the helmert grid-north
// angle); otherwise zero.  Anticlockwise positive.
FederatedFalseOrigin
guessFederatedFalseOrigin(const Eigen::Vector3d& first_geometry_point_m,
                          const ModelGeoref& georef,
                          const FederationConfig& fed_cfg);

// 1 federation_unit -> N metres.
double federationUnitToMeters(const FederationConfig&);

// Compose FederatedFalseOrigin into a 4x4 matrix in metres.
Eigen::Matrix4d composeFederatedFalseOrigin(const FederatedFalseOrigin&,
                                            const FederationConfig&);

// Compose ModelTransformation into a 4x4 matrix in metres.
// `coordinate_operation_meters` is the model's CoordinateOperation matrix
// (e.g. helmert_meters_from_parameters · inv(wcs_meters)) — needed to lift
// `a` into metres when a_frame == ModelLocal.  Pass identity when the
// CoordinateOperation is disabled or absent.
Eigen::Matrix4d composeModelTransformation(const ModelTransformation&,
                                           const FederationConfig& fed_cfg,
                                           const ModelUnits& model_units,
                                           const Eigen::Matrix4d& coordinate_operation_meters);

#endif // FEDERATIONMATH_H
