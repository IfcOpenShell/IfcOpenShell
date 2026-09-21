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

#include "document_serializer_plugin.h"
#include "rocks_db_serializer.h"

#ifdef IFOPSH_WITH_ROCKSDB

#include <boost/dll/alias.hpp>
#include <memory>

namespace {

std::shared_ptr<ifcopenshell::geom::serializer> create_serializer(const ifcopenshell::serializers::document_serializer_context& context) {
	if (context.input_filename.empty()) {
		throw ifcopenshell::exception("RocksDB document serializer requires an input filename");
	}
	return std::make_shared<RocksDbSerializer>(context.input_filename, context.output_filename, context.skip_supertypes);
}

}

namespace ifcopenshell {
namespace serializers {
namespace rdb_document_serializer_plugin {

plugin::abi_info plugin_abi() {
	return plugin::host_abi();
}

plugin::metadata plugin_metadata() {
	return document_serializer_plugin_metadata("rdb");
}

void register_plugin(document_serializer_registry& registry, const plugin::module& module) {
	document_serializer_info info;
	info.format = "rdb";
	info.name = "RocksDB";
	info.description = "RocksDB key-value store serialization of IFC data.";
	info.supports_ifc_file = false;
	info.supports_input_filename = true;
	info.writes_final_output = true;
	registry.bind(info, create_serializer, module);
}

}
}
}

BOOST_DLL_ALIAS(ifcopenshell::serializers::rdb_document_serializer_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::rdb_document_serializer_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::serializers::rdb_document_serializer_plugin::register_plugin, ifcopenshell_register_document_serializer_plugin_v1)

#ifdef __EMSCRIPTEN__
#define CAT(a, b) a##b
#define EXPAND_AND_CAT(a, b) CAT(a, b)
#define emscripten_register_document_serializer_plugin EXPAND_AND_CAT(ifcopenshell_emscripten_register_document_serializer_, IFCOPENSHELL_WASM_PLUGIN_ID)

extern "C" void emscripten_register_document_serializer_plugin(ifcopenshell::serializers::document_serializer_registry* registry) {
	ifcopenshell::serializers::rdb_document_serializer_plugin::register_plugin(
		*registry,
		ifcopenshell::plugin::module::builtin(ifcopenshell::serializers::rdb_document_serializer_plugin::plugin_metadata()));
}
#endif

#endif
