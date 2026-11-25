// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): creating a new instance by the name of its entity.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 21_create_instance_by_name <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // Alternatively, an instance can be created from the name of the entity as
    // it appears in the IFC schema. This is the equivalent of Python's
    // file.create_entity() and, unlike the previous example, does not require
    // the schema to be known at compile time.
    auto new_wall = model.create(model.schema()->declaration_by_name("IfcWall"));
    new_wall.to_string(std::cout);
    std::cout << std::endl;
    // end::example

    return 0;
}
