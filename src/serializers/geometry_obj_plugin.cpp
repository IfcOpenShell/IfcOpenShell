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
#include "WavefrontObjSerializer.h"

#include "../ifcparse/utils.h"

#include <boost/dll/alias.hpp>
#include <boost/make_shared.hpp>

#include <filesystem>

namespace {

std::string obj_mtl_filename(const std::string& output_filename) {
	std::filesystem::path path(ifcopenshell::path::from_utf8(output_filename));
	path.replace_extension(ifcopenshell::path::from_utf8(".mtl"));
	return ifcopenshell::path::to_utf8(path.native());
}

}

namespace ifcopenshell {
namespace serializers {
namespace geometry_obj_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return geometry_serializer_plugin_metadata("obj");
}

boost::shared_ptr<GeometrySerializer> create_serializer(const geometry_serializer_context& context) {
	return boost::make_shared<WaveFrontOBJSerializer>(context.output_temp_filename, obj_mtl_filename(context.output_filename), context.geometry_settings, context.serializer_settings);
}

void configure_serializer(geometry_serializer_context& context) {
	context.geometry_settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = true;
}

void register_plugin(geometry_serializer_registry& registry, const plugin::module& module) {
	geometry_serializer_info info;
	info.format = "obj";
	info.name = "WaveFront OBJ";
	info.description = "A .mtl file is also created.";
	info.extensions = { ".obj" };
	info.supports_triangulation = true;
	registry.bind(info, create_serializer, configure_serializer, module);
}

}
}
}

BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_obj_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_obj_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_obj_plugin::register_plugin, ifcopenshell_register_geometry_serializer_plugin_v1)
