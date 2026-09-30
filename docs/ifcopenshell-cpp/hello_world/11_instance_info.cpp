// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): printing everything an instance holds.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 11_instance_info <model.ifc>" << std::endl;
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
    // Printing an instance gives the line as it appears in the IFC file,
    // which is the equivalent of Python's entity_instance.get_info().
    auto wall = walls.front();
    wall.to_string(std::cout);
    std::cout << std::endl;
    // end::example

    return 0;
}
