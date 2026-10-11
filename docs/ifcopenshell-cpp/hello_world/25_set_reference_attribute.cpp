// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): setting an attribute that references another instance.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 25_set_reference_attribute <model.ifc>" << std::endl;
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
    // Some attributes are not text but a reference to another instance. The
    // generated setters take the instance directly, so all that is needed is
    // another instance in the same file.
    auto wall = walls.front();
    auto owner_history = model.create<Ifc4::IfcOwnerHistory>();
    wall.setOwnerHistory(owner_history);
    wall.to_string(std::cout);
    std::cout << std::endl;
    // end::example

    return 0;
}
