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
#include "RocksDbSerializer.h"

#ifdef IFOPSH_WITH_ROCKSDB

#include <boost/dll/alias.hpp>
#include <boost/make_shared.hpp>

namespace {

boost::shared_ptr<Serializer> create_serializer(const ifcopenshell::serializers::document_serializer_context& context) {
	if (!context.stream || context.input_filename.empty()) {
		throw ifcopenshell::exception("RocksDB document serializer requires --stream input");
	}
	return boost::make_shared<RocksDbSerializer>(context.input_filename, context.output_filename, true);
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

#endif
