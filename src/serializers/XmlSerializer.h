#ifndef XMLSERIALIZER_H
#define XMLSERIALIZER_H

#define SCHEMA_METHOD

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Serializer.h"
#include "../ifcparse/file.h"
#include "../plugin/plugin.h"

#include <boost/function.hpp>

#include <map>

class SERIALIZERS_API XmlSerializer : public Serializer {
private:
	XmlSerializer* implementation_ = nullptr;

protected:
	std::string xml_filename;

public:
	XmlSerializer(ifcopenshell::file* file, const std::string& xml_filename);

	virtual ~XmlSerializer() {}

	bool ready() { return true; }
	void writeHeader() {}

	void finalize() { implementation_->finalize(); }
	void setFile(ifcopenshell::file*) { throw ifcopenshell::exception("Should be supplied on construction"); }
};

struct SERIALIZERS_API XmlSerializerFactory {
	typedef boost::function2<XmlSerializer*, ifcopenshell::file*, std::string> fn;

	class SERIALIZERS_API Factory {
	public:
		Factory();
		void bind(const std::string& schema_name, fn, const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
		XmlSerializer* construct(const std::string& schema_name, ifcopenshell::file*, std::string);

	private:
		struct entry {
			fn fn_;
			ifcopenshell::plugin::module module_;
		};

		std::map<std::string, entry> entries_;
	};

	static Factory& implementations();
};

#endif
