// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): everything that references an instance.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 14_get_inverse <model.ifc>" << std::endl;
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
    // Perhaps we want to see all instances which are referencing our wall,
    // regardless of which attribute they use to do so. This is the equivalent
    // of Python's file.get_inverse() and takes a STEP ID.
    auto wall = walls.front();
    for (auto& instance : model.instances_by_reference(static_cast<int>(wall.id()))) {
        instance.to_string(std::cout);
        std::cout << std::endl;
    }
    // end::example

    return 0;
}
