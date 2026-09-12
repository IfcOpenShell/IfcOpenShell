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
#include "ttl_wkt_serializer.h"

#include <boost/dll/alias.hpp>
#include <memory>

namespace ifcopenshell {
namespace serializers {
namespace geometry_ttl_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return geometry_serializer_plugin_metadata("ttl");
}

std::shared_ptr<geometry_serializer> create_serializer(const geometry_serializer_context& context) {
	if (context.output_temp_stream) {
		return std::make_shared<ttl_wkt_serializer>(
			*context.output_temp_stream, context.settings);
	}
	return std::make_shared<ttl_wkt_serializer>(context.output_temp_filename, context.settings);
}

void configure_serializer(geometry_serializer_context& context) {
	context.settings.get<ifcopenshell::geom::settings::TriangulationType>().value = ifcopenshell::geom::settings::POLYHEDRON_WITH_HOLES;
	if (context.settings.get<ifcopenshell::geom::settings::WktUseSection>().get()) {
		context.settings.get<ifcopenshell::geom::settings::IteratorOutput>().value = ifcopenshell::geom::settings::NATIVE;
	}
}

void register_plugin(geometry_serializer_registry& registry, const plugin::module& module) {
	geometry_serializer_info info;
	info.format = "ttl";
	info.name = "TTL/WKT";
	info.description = "RDF Turtle with Well-Known Text geometry.";
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

#ifdef __EMSCRIPTEN__
#define CAT(a, b) a##b
#define EXPAND_AND_CAT(a, b) CAT(a, b)
#define emscripten_register_geometry_serializer_plugin EXPAND_AND_CAT(ifcopenshell_emscripten_register_geometry_serializer_, IFCOPENSHELL_WASM_PLUGIN_ID)

extern "C" void emscripten_register_geometry_serializer_plugin(ifcopenshell::serializers::geometry_serializer_registry* registry) {
	ifcopenshell::serializers::geometry_ttl_plugin::register_plugin(
		*registry,
		ifcopenshell::plugin::module::builtin(ifcopenshell::serializers::geometry_ttl_plugin::plugin_metadata()));
}
#endif
