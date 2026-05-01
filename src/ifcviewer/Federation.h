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

// Federation-level transformation data model and compose helpers.
//
// A federation is the user's working scene, composed of one or more IFC
// models.  Each model lives at:
//
//     stage3 · stage4 · stage2 · placement_stage1
//
// where:
//   - stage1 is per-mesh vertex rebasing (applied to the geometry buffers)
//   - stage2 is the per-model georef matrix (immutable, derived from the IFC)
//   - stage3 is the federation-wide false origin (mutable, this header)
//   - stage4 is the per-model placement within the federation (mutable, this header)
//
// All composed matrices are in metres.  The user-authored intent is stored
// in source units (model project unit / model map unit / federation unit) to
// preserve precision; conversion to metres happens in the compose helpers.

#ifndef FEDERATION_H
#define FEDERATION_H

#include <Eigen/Dense>

#include <string>

// Federation-wide settings persisted in .ifcfed.
struct FederationConfig {
    // IfcSIUnit name ("METRE") or IfcConversionBasedUnit name ("foot", "inch", ...).
    std::string unit_name   = "METRE";
    // SI prefix ("MILLI", "KILO", ...) — empty for unprefixed or for
    // conversion-based units.
    std::string unit_prefix = "";
};

// Stage 3 — the federation false origin.  Authoring intent is "nominate this
// XYZ as the new origin, with optional Z-axis heading rotation".  Composed as
//
//     stage3 = R_z(rz_deg) · T(-xyz_in_metres)
//
// i.e. translate the federation so the nominated point lands at the origin,
// then rotate around the new origin.  Translation is given in federation unit;
// rotation is in degrees.
struct FederationOrigin {
    Eigen::Vector3d xyz    = Eigen::Vector3d::Zero();   // federation unit
    double          rz_deg = 0.0;                       // degrees
};

// Frame in which ModelTransform.a is expressed.
//   ModelLocal  — pre-stage2 model coordinates, in the model's project length unit
//   ModelGlobal — post-stage2 model coordinates, in the model's map unit
enum class AFrame { ModelLocal, ModelGlobal };

// Stage 4 — the per-model placement within the federation.  Authoring intent
// is "rotate the model around `pivot`, then translate so that point `a` lands
// at point `b`".  Composed as
//
//     R_local    = R_z(rz) · R_y(ry) · R_x(rx)            [intrinsic XYZ]
//     R_at_pivot = T(pivot_m) · R_local · T(-pivot_m)
//     stage4     = T(b_m - R_at_pivot · a_m) · R_at_pivot
//
// Numbers are stored in their original input unit (a in model project or map
// unit per a_frame, b/pivot in federation unit) so that the user's typed
// values round-trip without precision loss.
struct ModelTransform {
    AFrame          a_frame  = AFrame::ModelGlobal;
    Eigen::Vector3d a        = Eigen::Vector3d::Zero();   // model project / map unit
    Eigen::Vector3d b        = Eigen::Vector3d::Zero();   // federation unit
    Eigen::Vector3d rxyz_deg = Eigen::Vector3d::Zero();   // degrees, intrinsic XYZ
    Eigen::Vector3d pivot    = Eigen::Vector3d::Zero();   // federation unit
};

// Per-model unit scales captured at load time.  project_length_to_meters
// comes from calculateUnitScale(file, "LENGTHUNIT"); map_unit_to_meters from
// siScaleFromNamedUnit(getMapUnit(file)) and falls back to the project length
// scale when the model has no MapUnit.
struct ModelUnits {
    double project_length_to_meters = 1.0;
    double map_unit_to_meters       = 1.0;
};

// 1 federation_unit -> N metres.  Cached at the call site if needed.
double federationUnitToMeters(const FederationConfig&);

// Compose stage 3 (federation false origin) into a 4x4 matrix in metres.
Eigen::Matrix4d composeFederationOrigin(const FederationOrigin&,
                                        const FederationConfig&);

// Compose stage 4 (per-model placement within the federation) into a 4x4
// matrix in metres.  `stage2_meters` is the model's georef matrix (e.g.
// helmertMetersFromParameters · inv(wcs_meters)) — needed to lift `a` into
// metres when a_frame == ModelLocal.  Pass identity when stage 2 is disabled
// or absent.
Eigen::Matrix4d composeModelTransform(const ModelTransform&,
                                      const FederationConfig& fed_cfg,
                                      const ModelUnits& model_units,
                                      const Eigen::Matrix4d& stage2_meters);

#endif // FEDERATION_H
