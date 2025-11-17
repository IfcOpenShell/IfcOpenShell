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

JsonSerializer* JsonSerializerFactory::Factory::construct(const std::string& schema_name, IfcParse::IfcFile* file, std::string json_filename, JsonSerializer::Dialect dialect) {
    const std::string schema_name_lower = boost::to_lower_copy(schema_name);
    auto it = this->find(schema_name_lower);
    if (it == this->end()) {
        throw IfcParse::IfcException("No Json serializer registered for " + schema_name);
    }
    return it->second(file, json_filename, dialect);
}

JsonSerializer::JsonSerializer(IfcParse::IfcFile* file, const std::string& json_filename, JsonSerializer::Dialect dialect) {
    if (file) {
        implementation_ = JsonSerializerFactory::implementations().construct(file->schema()->name(), file, json_filename, dialect);
    }
}

JsonSerializerFactory::Factory& JsonSerializerFactory::implementations() {
    static JsonSerializerFactory::Factory impl;
    return impl;
}
