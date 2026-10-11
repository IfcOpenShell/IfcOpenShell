// This file was generated with the assistance of an AI coding tool.
//
// Code examples and mechanisms: schema-agnostic parsing of IFCs.

#include <ifcparse/express.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <string>

// tag::runtime-example
// The runtime part of the API is not tied to a schema: instances are
// express::base values which know their own declaration, and instances_by_type()
// also accepts the name of an entity as it appears in the IFC schema. Code
// written this way processes IFC2x3, IFC4 and IFC4x3 input alike.
void process_agnostically(ifcopenshell::file& model) {
    for (auto& instance : model.instances_by_type("IfcProduct")) {
        std::cout << instance.declaration().name() << " #" << instance.id();
        // Attributes are read by name, and the value is converted on the fly.
        // get_value() also takes a default for attributes which are optional
        // or which hold something else than what you ask for.
        if (auto product = instance.as<express::entity>()) {
            std::cout << " " << product.get_value<std::string>("GlobalId", "<no guid>");
        }
        std::cout << std::endl;
    }
}
// end::runtime-example

// tag::typed-example
// If you do want the strongly typed accessors, the shared logic can be
// templated over the schema, and the schema dispatched on once. Note that the
// generated classes are schema specific, so Ifc4::IfcProduct and
// Ifc2x3::IfcProduct are unrelated types, and that the schema libraries you
// want to support have to be linked, see the installation instructions.
template <typename Schema>
void process_typed(ifcopenshell::file& model) {
    for (auto& product : model.instances_by_type<typename Schema::IfcProduct>()) {
        std::cout << product.GlobalId() << std::endl;
    }
}
// end::typed-example

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 02_schema_agnostic <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    process_agnostically(model);

    // The schema is only known at compile time when the generated classes are
    // used, so dispatch on the schema name once, and keep everything below it
    // independent of the schema.
    const std::string schema_name = model.schema()->name();
    if (schema_name == "IFC4") {
        process_typed<Ifc4>(model);
    } else {
        std::cerr << "No typed processing implemented for schema " << schema_name << std::endl;
    }

    return 0;
}
