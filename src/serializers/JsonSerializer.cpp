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

#include <boost/algorithm/string/case_conv.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <boost/preprocessor/stringize.hpp>

#define EXTERNAL_DEFS(r, data, elem) \
    extern void BOOST_PP_CAT(init_JsonSerializer_Ifc, elem)(JsonSerializerFactory::Factory*);

#define CALL_DEFS(r, data, elem) \
    BOOST_PP_CAT(init_JsonSerializer_Ifc, elem)(this);

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS, , SCHEMA_SEQ)

JsonSerializerFactory::Factory::Factory() {
    BOOST_PP_SEQ_FOR_EACH(CALL_DEFS, , SCHEMA_SEQ)
}

void JsonSerializerFactory::Factory::bind(const std::string& schema_name, fn f) {
    const std::string schema_name_lower = boost::to_lower_copy(schema_name);
    this->insert(std::make_pair(schema_name_lower, f));
}

JsonSerializer* JsonSerializerFactory::Factory::construct(const std::string& schema_name, IfcParse::IfcFile* file, std::string json_filename, JsonSerializer::Dialect dialect, Logger& logger) {
    const std::string schema_name_lower = boost::to_lower_copy(schema_name);
    auto it = this->find(schema_name_lower);
    if (it == this->end()) {
        throw IfcParse::IfcException("No Json serializer registered for " + schema_name);
    }
    return it->second(file, json_filename, dialect, logger);
}

JsonSerializer::JsonSerializer(IfcParse::IfcFile* file, const std::string& json_filename, JsonSerializer::Dialect dialect, Logger& logger)
    : Serializer(logger) {
    if (file) {
        implementation_ = JsonSerializerFactory::implementations().construct(file->schema()->name(), file, json_filename, dialect, logger_);
    }
}

JsonSerializerFactory::Factory& JsonSerializerFactory::implementations() {
    static JsonSerializerFactory::Factory impl;
    return impl;
}

#endif
