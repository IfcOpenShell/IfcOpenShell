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

#ifdef IFOPSH_WITH_OPENCASCADE

#include "geometry_serializer_plugin.h"
#include "IgesSerializer.h"

#include <boost/dll/alias.hpp>
#include <boost/make_shared.hpp>

#include <Standard_Version.hxx>

#if OCC_VERSION_HEX < 0x60900
#include <IGESControl_Controller.hxx>
#endif

namespace ifcopenshell {
namespace serializers {
namespace geometry_igs_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return geometry_serializer_plugin_metadata("igs");
}

boost::shared_ptr<GeometrySerializer> create_serializer(const geometry_serializer_context& context) {
#if OCC_VERSION_HEX < 0x60900
	IGESControl_Controller::Init();
#endif
	return boost::make_shared<IgesSerializer>(context.output_temp_filename, context.geometry_settings, context.serializer_settings);
}

void configure_serializer(geometry_serializer_context& context) {
	context.geometry_settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = true;
	context.geometry_settings.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
}

void register_plugin(geometry_serializer_registry& registry, const plugin::module& module) {
	geometry_serializer_info info;
	info.format = "igs";
	info.extensions = { ".igs" };
	info.kernel_ids = { "opencascade" };
	info.supports_brep = true;
	info.requires_ascii_temp_file = true;
	registry.bind(info, create_serializer, configure_serializer, module);
}

}
}
}

BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_igs_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_igs_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::geometry_igs_plugin::register_plugin, ifcopenshell_register_geometry_serializer_plugin_v1)

#endif
