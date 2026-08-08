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

#ifdef WITH_OPENCOLLADA

#include "ColladaSerializer.h"
#include "geometry_serializer_plugin.h"

#include <boost/dll/alias.hpp>
#include <boost/make_shared.hpp>

namespace ifcopenshell {
namespace serializers {
namespace geometry_dae_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return geometry_serializer_plugin_metadata("dae");
}

boost::shared_ptr<geometry_serializer> create_serializer(const geometry_serializer_context& context) {
	return boost::make_shared<collada_serializer>(context.output_temp_filename, context.settings);
}

void register_plugin(geometry_serializer_registry& registry, const plugin::module& module) {
	geometry_serializer_info info;
	info.format = "dae";
	info.name = "Collada";
	info.description = "Digital Assets Exchange.";
	info.extensions = { ".dae" };
	info.supports_triangulation = true;
	info.supports_user_element_hierarchy = true;
	info.requires_ascii_temp_file = true;
	registry.bind(info, create_serializer, geometry_serializer_registry::configure_fn(), module);
}

}
}
}

BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_dae_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_dae_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_dae_plugin::register_plugin, ifcopenshell_register_geometry_serializer_plugin_v1)

#endif
