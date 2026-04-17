#include "XmlSerializer.h"
#include "document_serializer_plugin.h"

#include <boost/algorithm/string/case_conv.hpp>

XmlSerializerFactory::Factory::Factory() {
	ifcopenshell::serializers::load_document_serializer_plugins(*this, "xml");
}

void XmlSerializerFactory::Factory::bind(const std::string& schema_name, fn f, const ifcopenshell::plugin::module& module) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	entries_[schema_name_lower] = { f, module };
}

XmlSerializer* XmlSerializerFactory::Factory::construct(const std::string& schema_name, ifcopenshell::file* file, std::string xml_filename) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	auto it = entries_.find(schema_name_lower);
	if (it == entries_.end()) {
		throw ifcopenshell::exception("No XML serializer registered for " + schema_name);
	}
	return it->second.fn_(file, xml_filename);
}

XmlSerializer::XmlSerializer(ifcopenshell::file* file, const std::string& xml_filename) {
	if (file) {
		implementation_ = XmlSerializerFactory::implementations().construct(file->schema()->name(), file, xml_filename);
	}
}

XmlSerializerFactory::Factory& XmlSerializerFactory::implementations() {
	static XmlSerializerFactory::Factory impl;
	return impl;
}
