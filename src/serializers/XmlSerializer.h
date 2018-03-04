#define SCHEMA_METHOD

#include "../ifcparse/IfcFile.h"

#include <boost/function.hpp>

#include <map>

template <typename T>
class schema_delegate {

};

class XmlSerializer : public schema_delegate<> {

};

struct XmlSerializerFactory {
	typedef boost::function1<XmlSerializer*, IfcParse::IfcFile*> fn;

	class Factory : public std::map<std::string, fn> {
	public:
		Factory();
		void bind(const std::string& schema_name, fn);
		XmlSerializer* construct(const std::string& schema_name, IfcParse::IfcFile*);
	};

	Factory& implementations();
};
