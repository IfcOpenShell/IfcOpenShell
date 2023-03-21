#include "XmlSerializer.h"

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <boost/algorithm/string/case_conv.hpp>

#define EXTERNAL_DEFS(r, data, elem) \
	extern void BOOST_PP_CAT(init_XmlSerializer_Ifc, elem)(XmlSerializerFactory::Factory*);

#define CALL_DEFS(r, data, elem) \
	BOOST_PP_CAT(init_XmlSerializer_Ifc, elem)(this);

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS, , SCHEMA_SEQ)

XmlSerializerFactory::Factory::Factory() {
	BOOST_PP_SEQ_FOR_EACH(CALL_DEFS, , SCHEMA_SEQ)
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
