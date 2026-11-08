// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): modifying an attribute.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 16_set_attribute <model.ifc>" << std::endl;
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
    // To modify data, assign it to the relevant attribute. Changes are made
    // in memory only, until the file is written out again.
    auto wall = walls.front();
    wall.setName(std::string("My new wall name"));
    std::cout << wall.Name().value_or("<unnamed>") << std::endl;
    // end::example

    return 0;
}
