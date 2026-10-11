// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): filling in attributes by name as an instance is created.

#include <ifcparse/file.h>
#include <ifcparse/global_id.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 23_create_instance_attribute_names <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // Knowing the order of attributes is not necessary: they can also be
    // assigned by name, using the name from the IFC schema.
    auto new_wall = model.create(model.schema()->declaration_by_name("IfcWall"));
    ifcopenshell::global_id new_global_id;
    new_wall.set_attribute_value("GlobalId", static_cast<const std::string&>(new_global_id));
    new_wall.set_attribute_value("Name", std::string("Wall Name"));
    new_wall.to_string(std::cout);
    std::cout << std::endl;
    // end::example

    return 0;
}
