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

// This file was generated with the assistance of an AI coding tool.

#ifndef IFCOPENSHELL_LINEWORK_PROCESSING_PLUGIN_H
#define IFCOPENSHELL_LINEWORK_PROCESSING_PLUGIN_H

#include "svgfill.h"

namespace svgfill {

abstract_arrangement* create_arrangement(solver s);
void destroy_arrangement(abstract_arrangement* arrangement);

namespace linework_processing_plugin {

constexpr const char* id = "geometry.svgfill";
constexpr const char* registration_symbol = "ifcopenshell_register_linework_processing_plugin_v1";

struct api {
	bool (*svg_to_line_segments)(
		const std::string&,
		const std::optional<std::string>&,
		std::vector<std::vector<line_segment_2>>&) = nullptr;
	bool (*line_segments_to_polygons)(
		solver,
		double,
		const std::vector<std::vector<line_segment_2>>&,
		std::vector<std::vector<polygon_2>>&) = nullptr;
	bool (*line_segments_to_polygons_with_progress)(
		solver,
		double,
		const std::vector<std::vector<line_segment_2>>&,
		std::vector<std::vector<polygon_2>>&,
		std::function<void(float)>&) = nullptr;
	std::string (*polygons_to_svg_groups)(const std::vector<std::vector<polygon_2>>&, bool) = nullptr;
	std::string (*polygons_to_svg)(const std::vector<polygon_2>&, bool) = nullptr;
	bool (*svg_to_polygons)(
		const std::string&,
		const std::optional<std::string>&,
		std::vector<polygon_2>&) = nullptr;
	bool (*arrange_polygons)(arrange_polygon_settings, const std::vector<polygon_2>&, std::vector<polygon_2>&, logger&) = nullptr;
	abstract_arrangement* (*create_arrangement)(solver) = nullptr;
	void (*destroy_arrangement)(abstract_arrangement*) = nullptr;
};

using register_linework_processing_plugin_fn = void(api&);

}
}

#endif
