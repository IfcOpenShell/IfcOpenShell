#include "JsonSerializer.h"

extern void init_JsonSerializerIfc2x3(JsonSerializerFactory::Factory*);
extern void init_JsonSerializerIfc4(JsonSerializerFactory::Factory*);
extern void init_JsonSerializerIfc4x1(JsonSerializerFactory::Factory*);
extern void init_JsonSerializerIfc4x2(JsonSerializerFactory::Factory*);

JsonSerializerFactory::Factory::Factory() {
	init_JsonSerializerIfc2x3(this);
	init_JsonSerializerIfc4(this);
	init_JsonSerializerIfc4x1(this);
	init_JsonSerializerIfc4x2(this);
}

void JsonSerializerFactory::Factory::bind(const std::string& schema_name, fn f) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, f));
}

JsonSerializer* JsonSerializerFactory::Factory::construct(const std::string& schema_name, IfcParse::IfcFile* file, std::string json_filename) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	typename std::map<std::string, fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == this->end()) {
		throw IfcParse::IfcException("No JSON serializer registered for " + schema_name);
	}
	return it->second(file, json_filename);
}

JsonSerializer::JsonSerializer(IfcParse::IfcFile* file, const std::string& json_filename) {
	if (file) {
		implementation_ = JsonSerializerFactory::implementations().construct(file->schema()->name(), file, json_filename);
	}
}

JsonSerializerFactory::Factory& JsonSerializerFactory::implementations() {
	static JsonSerializerFactory::Factory impl;
	return impl;
}
