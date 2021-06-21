#include "XmlSerializer.h"

#ifdef HAS_SCHEMA_2x3
extern void init_XmlSerializerIfc2x3(XmlSerializerFactory::Factory*);
#endif
#ifdef HAS_SCHEMA_4
extern void init_XmlSerializerIfc4(XmlSerializerFactory::Factory*);
#endif
#ifdef HAS_SCHEMA_4x1
extern void init_XmlSerializerIfc4x1(XmlSerializerFactory::Factory*);
#endif
#ifdef HAS_SCHEMA_4x2
extern void init_XmlSerializerIfc4x2(XmlSerializerFactory::Factory*);
#endif
#ifdef HAS_SCHEMA_4x3_rc1
extern void init_XmlSerializerIfc4x3_rc1(XmlSerializerFactory::Factory*);
#endif
#ifdef HAS_SCHEMA_4x3_rc2
extern void init_XmlSerializerIfc4x3_rc2(XmlSerializerFactory::Factory*);
#endif

XmlSerializerFactory::Factory::Factory() {
#ifdef HAS_SCHEMA_2x3
	init_XmlSerializerIfc2x3(this);
#endif
#ifdef HAS_SCHEMA_4
	init_XmlSerializerIfc4(this);
#endif
#ifdef HAS_SCHEMA_4x1
	init_XmlSerializerIfc4x1(this);
#endif
#ifdef HAS_SCHEMA_4x2
	init_XmlSerializerIfc4x2(this);
#endif
#ifdef HAS_SCHEMA_4x3_rc1
	init_XmlSerializerIfc4x3_rc1(this);
#endif
#ifdef HAS_SCHEMA_4x3_rc2
	init_XmlSerializerIfc4x3_rc2(this);
#endif
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
