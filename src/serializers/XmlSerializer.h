#ifndef XMLSERIALIZER_H
#define XMLSERIALIZER_H

#define SCHEMA_METHOD

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Serializer.h"
#include "../ifcparse/file.h"
#include "../plugin/plugin.h"
#include "../serializers/document_serializer_plugin.h"

#include <boost/shared_ptr.hpp>

class XmlSerializer : public Serializer {
private:
	boost::shared_ptr<Serializer> implementation_;

protected:
	std::string xml_filename;

public:
	XmlSerializer(ifcopenshell::file* file, const std::string& xml_filename, ::logger& logger = ::logger::root())
		: xml_filename(xml_filename)
	{
		if (!file) {
			return;
		}

		ifcopenshell::serializers::document_serializer_context context;
		context.file = file;
		context.output_filename = xml_filename;
		context.schema_name = file->schema()->name();
		implementation_ = ifcopenshell::serializers::document_serializer_registry_instance().create("xml", context);
	}

	virtual ~XmlSerializer() {}

	bool ready() { return true; }
	void writeHeader() {}

	void finalize() {
		if (!implementation_) {
			throw ifcopenshell::exception("No XML serializer implementation constructed");
		}
		implementation_->finalize();
	}
	void setFile(ifcopenshell::file&) { throw ifcopenshell::exception("Should be supplied on construction"); }
};

#endif
