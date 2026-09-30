// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): asking an instance what IFC class it is.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 06_instance_type <model.ifc>" << std::endl;
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
    // Returns 'IfcWall'
    std::cout << wall.declaration().name() << std::endl;
    // end::example

    return 0;
}
