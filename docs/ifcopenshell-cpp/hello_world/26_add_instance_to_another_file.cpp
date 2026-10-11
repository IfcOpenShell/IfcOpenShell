// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): copying an instance into another file.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 26_add_instance_to_another_file <model.ifc>" << std::endl;
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
    // Instances can be copied from one file into another. The forward
    // references of the instance are copied along with it, and the copy is
    // created in the target schema, so both files have to use the same one.
    auto wall = walls.front();
    ifcopenshell::file new_model(model.schema());
    new_model.add_entity(wall);
    for (auto& instance : new_model.instances_by_type<Ifc4::IfcWall>()) {
        instance.to_string(std::cout);
        std::cout << std::endl;
    }
    // end::example

    return 0;
}
