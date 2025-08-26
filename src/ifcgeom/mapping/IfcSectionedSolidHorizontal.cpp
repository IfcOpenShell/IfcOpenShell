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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#include "../../ifcgeom/profile_helper.h"
#include "../../ifcgeom/infra_sweep_helper.h"

#ifdef SCHEMA_HAS_IfcSectionedSolidHorizontal


taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSectionedSolidHorizontal* inst) {
	std::vector<cross_section> cross_sections;

	auto dir = map(inst->Directrix());
	auto fn = taxonomy::dcast<taxonomy::function_item>(dir);
	if (!fn) {
		// Only implement on alignment curves
        Logger::Warning("IfcSectionedSolidHorizontal is only implemented for Directrix curves based on taxonomy::function_item", inst);
        return nullptr;
	}

	{	
	auto css = inst->CrossSections();
	auto csps = inst->CrossSectionPositions();
	std::vector<taxonomy::face::ptr> faces;

	// The PointByDistanceExpressions are factored out into (a) a cartesian offset relative to the
	// reference frame along a certain curve location (b) the longitude.

	// The longitudes determine the range of the sweep and the offsets are interpolated in between
	// sweep segments. 
	std::vector<Eigen::Vector3d> profile_offsets;
	std::vector<boost::optional<Eigen::Matrix3d>> profile_rotations;
	std::vector<double> longitudes;

	for (auto& cs : *css) {
		faces.push_back(std::move(taxonomy::cast<taxonomy::face>(map(cs))));
	}
#if defined(SCHEMA_HAS_IfcPointByDistanceExpression) && !defined(SCHEMA_IfcSectionedSurface_HAS_FixedAxisVertical)
	for (auto& csp : *csps) {
		auto pbde = csp->Location()->as<IfcSchema::IfcPointByDistanceExpression>(true);

		longitudes.push_back(*pbde->DistanceAlong()->as<IfcSchema::IfcLengthMeasure>(true) * length_unit_);

		// Corresponds to the profile X, Y directions (hopefully).
		Eigen::Vector3d po(
			pbde->OffsetLateral().get_value_or(0.),
			// @todo I don't understand whether vertical is an offset relative to the tangent plane or to the global XY plane
			pbde->OffsetVertical().get_value_or(0.),
			0.
		);

		profile_offsets.push_back(po);

		boost::optional<Eigen::Matrix3d> rot;
		if (csp->Axis() && csp->RefDirection()) {
			rot = taxonomy::matrix4(
				Eigen::Vector3d(0, 0, 0),
				taxonomy::cast<taxonomy::direction3>(map(csp->Axis()))->ccomponents(),
				taxonomy::cast<taxonomy::direction3>(map(csp->RefDirection()))->ccomponents()).ccomponents().block<3,3>(0,0);
		} else if (csp->Axis()) {
			rot = taxonomy::matrix4(
				Eigen::Vector3d(0, 0, 0),
				taxonomy::cast<taxonomy::direction3>(map(csp->Axis()))->ccomponents()).ccomponents().block<3, 3>(0, 0);
		}
		profile_rotations.push_back(rot);
	}
	if (faces.size() != profile_offsets.size()) {
		Logger::Warning("Expected CrossSections and CrossSectionPositions to be equal length, but got " + std::to_string(faces.size()) + " and " + std::to_string(profile_offsets.size()) + " respectively", inst);
		return nullptr;
	}
	if (faces.size() < 2) {
		Logger::Warning("Expected at least two cross sections, but got " + std::to_string(faces.size()), inst);
		return nullptr;
	}

	for (size_t i = 0; i < faces.size(); ++i) {
		cross_sections.push_back({ longitudes[i], faces[i], profile_offsets[i], profile_rotations[i]});
	}
#else
    return nullptr;
#endif
   }

	return make_loft(settings_, inst, fn, cross_sections);
}

#endif
