// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): removing an instance.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 27_remove_instance <model.ifc>" << std::endl;
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
    // Instances that are no longer needed can be removed. Attributes of other
    // instances that point at the removed instance are unset, so that the
    // file stays consistent.
    auto wall = walls.front();
    model.remove_entity(wall);
    std::cout << model.instances_by_type<Ifc4::IfcWall>().size() << std::endl;
    // end::example

    return 0;
}
