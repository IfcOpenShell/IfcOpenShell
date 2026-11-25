// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): reading attributes by their position.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 09_attribute_by_index <model.ifc>" << std::endl;
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
    // IFC attributes have a particular order and can be read positionally.
    // Both indices below are known to hold a string, other attribute types
    // are converted to their C++ equivalent, such as int64_t or double.
    auto wall = walls.front();
    // The first attribute is the GlobalId.
    std::cout << static_cast<std::string>(wall.get_attribute_value(0)) << std::endl;
    // The third attribute is the Name - note that this will fail when the attribute is unset!
    std::cout << static_cast<std::string>(wall.get_attribute_value(2)) << std::endl;
    // end::example

    return 0;
}
