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

#ifdef WITH_GLTF

#include "JsonSerializer.h"
#include "document_serializer_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

JsonSerializerFactory::Factory::Factory() {
    ifcopenshell::serializers::load_document_serializer_plugins(*this, "json");
}

void JsonSerializerFactory::Factory::bind(const std::string& schema_name, fn f, const ifcopenshell::plugin::module& module) {
    const std::string schema_name_lower = boost::to_lower_copy(schema_name);
    entries_[schema_name_lower] = { f, module };
}

JsonSerializer* JsonSerializerFactory::Factory::construct(const std::string& schema_name, ifcopenshell::file* file, std::string json_filename, JsonSerializer::Dialect dialect) {
    const std::string schema_name_lower = boost::to_lower_copy(schema_name);
    auto it = entries_.find(schema_name_lower);
    if (it == entries_.end()) {
        throw ifcopenshell::exception("No Json serializer registered for " + schema_name);
    }
    return it->second.fn_(file, json_filename, dialect);
}

JsonSerializer::JsonSerializer(ifcopenshell::file* file, const std::string& json_filename, JsonSerializer::Dialect dialect) {
    if (file) {
        implementation_ = JsonSerializerFactory::implementations().construct(file->schema()->name(), file, json_filename, dialect);
    }
}

JsonSerializerFactory::Factory& JsonSerializerFactory::implementations() {
    static JsonSerializerFactory::Factory impl;
    return impl;
}

#endif
