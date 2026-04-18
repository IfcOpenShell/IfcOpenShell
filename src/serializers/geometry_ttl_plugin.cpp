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
#include "TtlWktSerializer.h"

#include <boost/dll/alias.hpp>
#include <boost/make_shared.hpp>

namespace ifcopenshell {
namespace serializers {
namespace geometry_ttl_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return geometry_serializer_plugin_metadata("ttl");
}

boost::shared_ptr<GeometrySerializer> create_serializer(const geometry_serializer_context& context) {
	return boost::make_shared<TtlWktSerializer>(context.output_temp_filename, context.geometry_settings, context.serializer_settings);
}

void configure_serializer(geometry_serializer_context& context) {
	context.geometry_settings.get<ifcopenshell::geometry::settings::TriangulationType>().value = ifcopenshell::geometry::settings::POLYHEDRON_WITH_HOLES;
	if (context.serializer_settings.get<ifcopenshell::geometry::settings::WktUseSection>().get()) {
		context.geometry_settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
	}
}

void register_plugin(geometry_serializer_registry& registry, const plugin::module& module) {
	geometry_serializer_info info;
	info.format = "ttl";
	info.extensions = { ".ttl" };
	info.supports_triangulation = true;
	info.supports_brep = true;
	registry.bind(info, create_serializer, configure_serializer, module);
}

}
}
}

BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_ttl_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_ttl_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_ttl_plugin::register_plugin, ifcopenshell_register_geometry_serializer_plugin_v1)
