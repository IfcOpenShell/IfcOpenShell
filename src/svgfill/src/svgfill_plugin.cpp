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

#include "linework_processing_plugin.h"

#include "../../plugin/plugin.h"

#include <boost/dll/alias.hpp>

namespace svgfill {
namespace linework_processing_plugin {

ifcopenshell::plugin::abi_info plugin_abi() {
	return ifcopenshell::plugin::host_abi();
}

ifcopenshell::plugin::metadata plugin_metadata() {
	ifcopenshell::plugin::metadata metadata;
	metadata.kind_ = ifcopenshell::plugin::kind::linework_processing;
	metadata.id = id;
	return metadata;
}

void register_plugin(api& api) {
	api.svg_to_line_segments = &svgfill::svg_to_line_segments;
	api.line_segments_to_polygons = static_cast<bool (*)(
		solver,
		double,
		const std::vector<std::vector<line_segment_2>>&,
		std::vector<std::vector<polygon_2>>&)>(&svgfill::line_segments_to_polygons);
	api.line_segments_to_polygons_with_progress = static_cast<bool (*)(
		solver,
		double,
		const std::vector<std::vector<line_segment_2>>&,
		std::vector<std::vector<polygon_2>>&,
		std::function<void(float)>&)>(&svgfill::line_segments_to_polygons);
	api.polygons_to_svg_groups = static_cast<std::string (*)(const std::vector<std::vector<polygon_2>>&, bool)>(&svgfill::polygons_to_svg);
	api.polygons_to_svg = static_cast<std::string (*)(const std::vector<polygon_2>&, bool)>(&svgfill::polygons_to_svg);
	api.svg_to_polygons = &svgfill::svg_to_polygons;
	api.arrange_polygons = &svgfill::arrange_polygons;
	api.create_arrangement = &svgfill::create_arrangement;
	api.destroy_arrangement = &svgfill::destroy_arrangement;
}

}
}

BOOST_DLL_ALIAS(svgfill::linework_processing_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(svgfill::linework_processing_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(svgfill::linework_processing_plugin::register_plugin, ifcopenshell_register_linework_processing_plugin_v1)
