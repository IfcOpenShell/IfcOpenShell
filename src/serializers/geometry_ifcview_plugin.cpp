// This file was generated with the assistance of an AI coding tool.
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

#include "geometry_serializer_plugin.h"
#include "../ifcviewer/IfcViewSerializer.h"

#include <boost/dll/alias.hpp>
#include <memory>

namespace ifcopenshell {
namespace serializers {
namespace geometry_ifcview_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return geometry_serializer_plugin_metadata("ifcview");
}

std::shared_ptr<geometry_serializer> create_serializer(const geometry_serializer_context& context) {
	// writes_final_output is set below, so output_filename is the final
	// <stem>.ifcview path (writeSidecar normalises the stem itself).
	return std::make_shared<IfcViewSerializer>(context.output_filename, context.settings);
}

void register_plugin(geometry_serializer_registry& registry, const plugin::module& module) {
	geometry_serializer_info info;
	info.format = "ifcview";
	info.name = "IfcView sidecar";
	info.description = "Instanced viewer cache (.ifcview) consumed by the IfcOpenShell viewer.";
	info.extensions = { ".ifcview" };
	info.supports_triangulation = true;
	info.bypass_properties = true;
	// The serializer writes the final file itself via writeSidecar(), so
	// IfcConvert must not rename a temp output over it.
	info.writes_final_output = true;
	registry.bind(info, create_serializer, geometry_serializer_registry::configure_fn(), module);
}

}
}
}

BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_ifcview_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_ifcview_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_ifcview_plugin::register_plugin, ifcopenshell_register_geometry_serializer_plugin_v1)
