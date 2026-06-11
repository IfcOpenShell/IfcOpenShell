#ifndef JSONSERIALIZER_H
#define JSONSERIALIZER_H

#ifdef WITH_GLTF

#include "../ifcgeom/Serializer.h"
#include "../ifcparse/IfcFile.h"
#include "../serializers/serializers_api.h"

#include <boost/function.hpp>
#include <map>

class SERIALIZERS_API JsonSerializer : public Serializer {
  public:
    enum Dialect {
        JSON_DIALECT_CREOOX
    };
  private:
    JsonSerializer* implementation_;

  protected:
    std::string json_filename;
    Dialect dialect_;

  public:
    JsonSerializer(IfcParse::IfcFile* file, const std::string& json_filename, Dialect dialect = Dialect::JSON_DIALECT_CREOOX, Logger& logger = Logger::Root());

    virtual ~JsonSerializer() {}

    bool ready() { return true; }
    void writeHeader() {}

    void finalize() { implementation_->finalize(); }
    void setFile(IfcParse::IfcFile*) { throw IfcParse::IfcException("Should be supplied on construction"); }
};

struct SERIALIZERS_API JsonSerializerFactory {
    typedef boost::function4<JsonSerializer*, IfcParse::IfcFile*, std::string, JsonSerializer::Dialect, Logger&> fn;

    class Factory : public std::map<std::string, fn> {
      public:
        Factory();
        void bind(const std::string& schema_name, fn);
        JsonSerializer* construct(const std::string& schema_name, IfcParse::IfcFile*, std::string, JsonSerializer::Dialect, Logger& logger = Logger::Root());
    };

    static Factory& implementations();
};

#endif

#endif
