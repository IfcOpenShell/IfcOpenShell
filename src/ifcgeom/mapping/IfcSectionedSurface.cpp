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

#ifdef SCHEMA_HAS_IfcSectionedSurface


taxonomy::ptr mapping::map_impl(const IfcSchema::IfcSectionedSurface* inst) {
	std::vector<cross_section> cross_sections;

	auto dir = map(inst->Directrix());
	auto pwf = taxonomy::dcast<taxonomy::piecewise_function>(dir);
	if (!pwf) {
		// Only implement on alignment curves
        Logger::Warning("IfcSectionedSurface is only implemented for piecewise function Directrix curves", inst);
        return nullptr;
	}

	{	
	auto css = inst->CrossSections();
	auto csps = inst->CrossSectionPositions();
	std::vector<taxonomy::geom_item::ptr> faces;

	// The PointByDistanceExpressesions are factored out into (a) a cartesian offset relative to the
	// reference frame along a certain curve location (b) the longitude.

	// The longitudes determine the range of the sweep and the offsets are interpolated in between
	// sweep segments. 
	std::vector<Eigen::Vector3d> profile_offsets;
	std::vector<double> longitudes;

	for (auto& cs : *css) {
		faces.push_back(std::move(taxonomy::cast<taxonomy::geom_item>(map(cs))));
	}
#ifdef SCHEMA_HAS_IfcPointByDistanceExpression
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
	}
#else
	return nullptr;
#endif
	if (faces.size() != profile_offsets.size()) {
		Logger::Warning("Expected CrossSections and CrossSectionPositions to be equal length, but got " + std::to_string(faces.size()) + " and " + std::to_string(profile_offsets.size()) + " respectively", inst);
		return nullptr;
	}
	if (faces.size() < 2) {
		Logger::Warning("Expected at least two cross sections, but got " + std::to_string(faces.size()), inst);
		return nullptr;
	}

	for (size_t i = 0; i < faces.size(); ++i) {
		cross_sections.push_back({ longitudes[i], faces[i], profile_offsets[i] });
	}
	}

	return make_loft(settings_, inst, pwf, cross_sections);
}

#endif
