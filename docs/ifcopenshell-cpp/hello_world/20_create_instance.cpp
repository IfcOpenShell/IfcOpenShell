// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): creating a new instance.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 20_create_instance <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // New instances are created by the file that owns them, and are added to
    // it straight away. Note how all of the attributes are blank.
    auto new_wall = model.create<Ifc4::IfcWall>();
    new_wall.to_string(std::cout);
    std::cout << std::endl;
    // ... and the file now contains it.
    std::cout << model.instances_by_type<Ifc4::IfcWall>().size() << std::endl;
    // end::example

    return 0;
}
