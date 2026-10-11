// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): generating a new GlobalId.

#include <ifcparse/file.h>
#include <ifcparse/global_id.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 17_new_global_id <model.ifc>" << std::endl;
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
    // A default constructed IfcOpenShell::global_id is a new, random,
    // compressed GlobalId, and converts to a std::string.
    auto wall = walls.front();
    ifcopenshell::global_id new_global_id;
    wall.setGlobalId(new_global_id);
    std::cout << wall.GlobalId() << std::endl;
    // end::example

    return 0;
}
