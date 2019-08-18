#include "XmlSerializer.h"

extern void init_XmlSerializer_Ifc2x3(XmlSerializerFactory::Factory*);
extern void init_XmlSerializer_Ifc4(XmlSerializerFactory::Factory*);
extern void init_XmlSerializer_Ifc4x1(XmlSerializerFactory::Factory*);
extern void init_XmlSerializer_Ifc4x2(XmlSerializerFactory::Factory*);

XmlSerializerFactory::Factory::Factory() {
	init_XmlSerializer_Ifc2x3(this);
	init_XmlSerializer_Ifc4(this);
	init_XmlSerializer_Ifc4x1(this);
	init_XmlSerializer_Ifc4x2(this);
}

void XmlSerializerFactory::Factory::bind(const std::string& schema_name, fn f) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, f));
}

XmlSerializer* XmlSerializerFactory::Factory::construct(const std::string& schema_name, IfcParse::IfcFile* file, std::string xml_filename) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	typename std::map<std::string, fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == this->end()) {
		throw IfcParse::IfcException("No XML serializer registered for " + schema_name);
	}
	return it->second(file, xml_filename);
}

XmlSerializer::XmlSerializer(IfcParse::IfcFile* file, const std::string& xml_filename) {
	if (file) {
		implementation_ = XmlSerializerFactory::implementations().construct(file->schema()->name(), file, xml_filename);
	}
}

XmlSerializerFactory::Factory& XmlSerializerFactory::implementations() {
	static XmlSerializerFactory::Factory impl;
	return impl;
}
