#ifndef JSONSERIALIZER_H
#define JSONSERIALIZER_H

#ifdef WITH_GLTF

#include "../ifcgeom/serializer.h"
#include "../ifcparse/file.h"
#include "../plugin/plugin.h"
#include "../serializers/serializers_api.h"
#include "../serializers/document_serializer_plugin.h"

#include <boost/shared_ptr.hpp>

class json_serializer : public ifcopenshell::geom::serializer {
  public:
    enum Dialect {
        JSON_DIALECT_CREOOX
    };
  private:
    boost::shared_ptr<ifcopenshell::geom::serializer> implementation_;

  protected:
    std::string json_filename;
    Dialect dialect_;

  public:
    json_serializer(ifcopenshell::file* file, const std::string& json_filename, Dialect dialect = Dialect::JSON_DIALECT_CREOOX, ifcopenshell::logger& logger = ifcopenshell::logger::root())
        : json_filename(json_filename)
        , dialect_(dialect)
    {
        if (!file) {
            return;
        }

        ifcopenshell::serializers::document_serializer_context context;
        context.file = file;
        context.output_filename = json_filename;
        context.schema_name = file->schema()->name();
        context.dialect = static_cast<int>(dialect);
        implementation_ = ifcopenshell::serializers::document_serializer_registry_instance().create("json", context);
    }

    virtual ~json_serializer() {}

    bool ready() { return true; }
    void writeHeader() {}

    void finalize() {
        if (!implementation_) {
            throw ifcopenshell::exception("No JSON serializer implementation constructed");
        }
        implementation_->finalize();
    }
    void setFile(ifcopenshell::file&) { throw ifcopenshell::exception("Should be supplied on construction"); }
};

#endif

#endif
