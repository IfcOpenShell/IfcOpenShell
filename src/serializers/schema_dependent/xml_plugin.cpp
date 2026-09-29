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

#include "../document_serializer_plugin.h"
#include "xml_serializer.h"

#include "../../ifcparse/macros.h"

#include <boost/dll/alias.hpp>
#include <memory>

namespace {

std::shared_ptr<ifcopenshell::geom::serializer> create_serializer(const ifcopenshell::serializers::document_serializer_context& context) {
	return std::make_shared<POSTFIX_SCHEMA(xml_serializer)>(context.file, context.output_filename);
}

}

namespace ifcopenshell {
namespace serializers {
namespace xml_document_serializer_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return document_serializer_plugin_metadata("xml", STRINGIFY(IfcSchema));
}

void register_plugin(document_serializer_registry& registry, const plugin::module& module) {
	document_serializer_info info;
	info.format = "xml";
	info.name = "XML";
	info.description = "Property definitions and decomposition tree.";
	info.schema_name = STRINGIFY(IfcSchema);
	registry.bind(info, create_serializer, module);
}

}
}
}

BOOST_DLL_ALIAS(ifcopenshell::serializers::xml_document_serializer_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::xml_document_serializer_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::xml_document_serializer_plugin::register_plugin, ifcopenshell_register_document_serializer_plugin_v1)
