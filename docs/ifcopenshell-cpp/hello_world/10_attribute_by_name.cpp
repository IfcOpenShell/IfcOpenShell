// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): reading attributes by their name.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 10_attribute_by_name <model.ifc>" << std::endl;
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
    // Knowing the order of attributes is not necessary: the generated classes
    // have accessors named after the attribute, strongly typed and wrapped in
    // std::optional when the attribute is optional.
    auto wall = walls.front();
    std::cout << wall.GlobalId() << std::endl;
    std::cout << wall.Name().value_or("<unnamed>") << std::endl;
    // end::example

    return 0;
}
