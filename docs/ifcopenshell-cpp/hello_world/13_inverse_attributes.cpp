// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): inverse attributes.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 13_inverse_attributes <model.ifc>" << std::endl;
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
    // Inverse attributes are attributes that other instances point at, for
    // example to define a relationship, to void our wall, or to add a
    // quantity take-off value to it. Just treat them like regular attributes.
    auto wall = walls.front();
    for (auto& relationship : wall.IsDefinedBy()) {
        relationship.to_string(std::cout);
        std::cout << std::endl;
    }
    // end::example

    return 0;
}
