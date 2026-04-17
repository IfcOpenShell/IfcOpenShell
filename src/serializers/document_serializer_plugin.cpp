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

#include <boost/algorithm/string/case_conv.hpp>

namespace {

std::string document_serializer_plugin_prefix(const std::string& format) {
	return "document." + boost::to_lower_copy(format) + ".";
}

template <typename registry_t, typename register_plugin_t>
void load_document_serializer_plugins_impl(registry_t& registry, const std::string& format) {
	ifcopenshell::plugin::manager manager;
	manager.add_search_path(ifcopenshell::serializers::document_serializer_plugin_directory());

	const auto format_lower = boost::to_lower_copy(format);
	const auto prefix = document_serializer_plugin_prefix(format_lower);
	for (const auto& path : manager.discover(prefix)) {
		auto module = manager.load(path);
		if (module.meta().kind_ != ifcopenshell::plugin::kind::document_serializer) {
			continue;
		}
		if (boost::to_lower_copy(module.meta().format) != format_lower) {
			continue;
		}

		auto register_plugin = module.get_alias<register_plugin_t>(ifcopenshell::serializers::document_serializer_plugin_registration_symbol());
		register_plugin(registry, module);
	}
}

}

const char* ifcopenshell::serializers::document_serializer_plugin_registration_symbol() {
	return "ifcopenshell_register_document_serializer_plugin_v1";
}

ifcopenshell::plugin::metadata ifcopenshell::serializers::document_serializer_plugin_metadata(const std::string& format, const std::string& schema_name) {
	plugin::metadata metadata;
	metadata.kind_ = plugin::kind::document_serializer;
	metadata.id = document_serializer_plugin_prefix(format) + boost::to_lower_copy(schema_name);
	metadata.schema = boost::to_upper_copy(schema_name);
	metadata.format = boost::to_lower_copy(format);
	return metadata;
}

std::filesystem::path ifcopenshell::serializers::document_serializer_plugin_directory() {
	return plugin::module_directory(reinterpret_cast<const void*>(&ifcopenshell::serializers::document_serializer_plugin_directory));
}

void ifcopenshell::serializers::load_document_serializer_plugins(XmlSerializerFactory::Factory& registry, const std::string& format) {
	load_document_serializer_plugins_impl<XmlSerializerFactory::Factory, register_xml_document_serializer_plugin_fn>(registry, format);
}

#ifdef WITH_GLTF
void ifcopenshell::serializers::load_document_serializer_plugins(JsonSerializerFactory::Factory& registry, const std::string& format) {
	load_document_serializer_plugins_impl<JsonSerializerFactory::Factory, register_json_document_serializer_plugin_fn>(registry, format);
}
#endif
