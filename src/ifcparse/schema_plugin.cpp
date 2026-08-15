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

#include "schema.h"

#include "hierarchy_helper.h"
#include "macros.h"
#include "si_prefix.h"

#include INCLUDE_SCHEMA(schemas, IfcSchema)

#define CAT(a, b) a##b
#define EXPAND_AND_CAT(a, b) CAT(a, b)
#define schema_plugin EXPAND_AND_CAT(schema_plugin_, IfcSchema)
#define emscripten_register_schema_plugin EXPAND_AND_CAT(ifcopenshell_emscripten_register_schema_, IFCOPENSHELL_WASM_PLUGIN_ID)

#include <boost/dll/alias.hpp>

namespace ifcopenshell {
namespace schema_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return schema_plugin_metadata(IfcSchema::Identifier);
}

void register_plugin(schema_registry& registry, const plugin::module& module) {
	registry.bind(IfcSchema::Identifier, &IfcSchema::get_schema, &IfcSchema::clear_schema, module);
}

}
}

template IFC_SCHEMA_API double ifcopenshell::get_SI_equivalent<IfcSchema>(const IfcSchema::IfcNamedUnit&);

#include "hierarchy_helper.i"

BOOST_DLL_ALIAS(ifcopenshell::schema_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::schema_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::schema_plugin::register_plugin, ifcopenshell_register_schema_plugin_v1)

#ifdef __EMSCRIPTEN__
extern "C" void emscripten_register_schema_plugin() {
	ifcopenshell::schema_plugin::register_plugin(
		ifcopenshell::schema_registry_instance(),
		ifcopenshell::plugin::module::builtin(ifcopenshell::schema_plugin::plugin_metadata()));
}
#endif
