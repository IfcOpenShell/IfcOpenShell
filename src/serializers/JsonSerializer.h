#define SCHEMA_METHOD

#include "../serializers/Serializer.h"
#include "../ifcparse/IfcFile.h"

#include <boost/function.hpp>

#include <map>

class JsonSerializer : public Serializer {
private:
	JsonSerializer* implementation_;

protected:
	std::string json_filename;

public:
	JsonSerializer(IfcParse::IfcFile* file, const std::string& json_filename);

	virtual ~JsonSerializer() {}

	bool ready() { return true; }
    void writeHeader() {}

	void finalize() { implementation_->finalize(); }
	void setFile(IfcParse::IfcFile*) { throw IfcParse::IfcException("Should be supplied on construction"); }
};

struct JsonSerializerFactory {
	typedef boost::function2<JsonSerializer*, IfcParse::IfcFile*, std::string> fn;

	class Factory : public std::map<std::string, fn> {
	public:
		Factory();
		void bind(const std::string& schema_name, fn);
		JsonSerializer* construct(const std::string& schema_name, IfcParse::IfcFile*, std::string);
	};

	static Factory& implementations();
};
