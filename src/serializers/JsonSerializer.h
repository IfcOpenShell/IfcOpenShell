#ifndef JSONSERIALIZER_H
#define JSONSERIALIZER_H

#ifdef WITH_GLTF

#include "../ifcgeom/Serializer.h"
#include "../ifcparse/file.h"
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
    JsonSerializer(ifcopenshell::file* file, const std::string& json_filename, Dialect dialect = Dialect::JSON_DIALECT_CREOOX);

    virtual ~JsonSerializer() {}

    bool ready() { return true; }
    void writeHeader() {}

    void finalize() { implementation_->finalize(); }
    void setFile(ifcopenshell::file*) { throw ifcopenshell::exception("Should be supplied on construction"); }
};

struct SERIALIZERS_API JsonSerializerFactory {
    typedef boost::function3<JsonSerializer*, ifcopenshell::file*, std::string, JsonSerializer::Dialect> fn;

    class Factory : public std::map<std::string, fn> {
      public:
        Factory();
        void bind(const std::string& schema_name, fn);
        JsonSerializer* construct(const std::string& schema_name, ifcopenshell::file*, std::string, JsonSerializer::Dialect);
    };

    static Factory& implementations();
};

#endif

#endif
