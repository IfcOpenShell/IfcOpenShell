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

#ifndef IFCOPENSHELL_DOCUMENT_SERIALIZER_PLUGIN_H
#define IFCOPENSHELL_DOCUMENT_SERIALIZER_PLUGIN_H

#include "XmlSerializer.h"

#ifdef WITH_GLTF
#include "JsonSerializer.h"
#endif

#include <filesystem>
#include <string>

namespace ifcopenshell {
namespace serializers {

typedef void register_xml_document_serializer_plugin_fn(XmlSerializerFactory::Factory&, const ifcopenshell::plugin::module&);

SERIALIZERS_API const char* document_serializer_plugin_registration_symbol();
SERIALIZERS_API ifcopenshell::plugin::metadata document_serializer_plugin_metadata(const std::string& format, const std::string& schema_name);
SERIALIZERS_API std::filesystem::path document_serializer_plugin_directory();
SERIALIZERS_API void load_document_serializer_plugins(XmlSerializerFactory::Factory& registry, const std::string& format);

#ifdef WITH_GLTF
typedef void register_json_document_serializer_plugin_fn(JsonSerializerFactory::Factory&, const ifcopenshell::plugin::module&);

SERIALIZERS_API void load_document_serializer_plugins(JsonSerializerFactory::Factory& registry, const std::string& format);
#endif

}
}

#endif
