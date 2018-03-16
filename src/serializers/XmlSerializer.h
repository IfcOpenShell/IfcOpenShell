#define SCHEMA_METHOD

#include "../serializers/Serializer.h"
#include "../ifcparse/IfcFile.h"

#include <boost/function.hpp>

#include <map>

class XmlSerializer : public Serializer {
private:
	XmlSerializer* implementation_;

protected:
	std::string xml_filename;

public:
	XmlSerializer(IfcParse::IfcFile* file, const std::string& xml_filename);

	virtual ~XmlSerializer() {}

	bool ready() { return true; }
	void writeHeader() {}

	void finalize() { implementation_->finalize(); }
	void setFile(IfcParse::IfcFile*) { throw IfcParse::IfcException("Should be supplied on construction"); }
};

struct XmlSerializerFactory {
	typedef boost::function2<XmlSerializer*, IfcParse::IfcFile*, std::string> fn;

	class Factory : public std::map<std::string, fn> {
	public:
		Factory();
		void bind(const std::string& schema_name, fn);
		XmlSerializer* construct(const std::string& schema_name, IfcParse::IfcFile*, std::string);
	};

	static Factory& implementations();
};
