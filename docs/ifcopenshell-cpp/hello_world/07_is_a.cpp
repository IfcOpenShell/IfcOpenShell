// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): testing the class of an instance, including supertypes.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 07_is_a <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }
    auto walls = model.instances_by_type<Ifc4::IfcWall>();
    if (walls.empty()) {
        std::cerr << "No IfcWall instances found" << std::endl;
        return 1;
    }

    // tag::example
    auto wall = walls.front();
    // An instance is also an instance of all of its supertypes, so a wall is
    // an IfcElement, but not an IfcWindow. Note how this works against the
    // declarations, which is what makes it usable for any schema version.
    const ifcopenshell::declaration& type = wall.declaration();
    std::cout << (type.is("IfcWall") ? "true" : "false") << std::endl;
    std::cout << (type.is("IfcElement") ? "true" : "false") << std::endl;
    std::cout << (type.is("IfcWindow") ? "true" : "false") << std::endl;
    // end::example

    return 0;
}
