// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): traversing the instances an instance references.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 15_traverse <model.ifc>" << std::endl;
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
    // The opposite of get_inverse(): a depth first traversal of everything
    // our wall references. Note that the root instance itself is included.
    auto wall = walls.front();
    for (auto& instance : ifcopenshell::file::traverse(wall)) {
        instance.to_string(std::cout);
        std::cout << std::endl;
    }
    // Or, let's just go down one level deep. A max_depth of 1 gives the
    // instances that are referenced by the wall itself.
    for (auto& instance : ifcopenshell::file::traverse(wall, 1)) {
        instance.to_string(std::cout);
        std::cout << std::endl;
    }
    // end::example

    return 0;
}
