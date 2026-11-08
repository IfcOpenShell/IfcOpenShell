// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): assigning a table of attributes onto a new instance.

#include <ifcparse/file.h>
#include <ifcparse/global_id.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 24_create_instance_from_table <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // Sometimes it is easier to collect the attributes in a table first, and
    // assign them in a loop. This is the equivalent of expanding a Python
    // dictionary into create_entity().
    std::vector<std::pair<std::string, std::string>> attributes = {
        {"GlobalId", static_cast<const std::string&>(ifcopenshell::global_id())},
        {"Name", "Wall Name"},
    };
    auto new_wall = model.create(model.schema()->declaration_by_name("IfcWall"));
    for (auto& attribute : attributes) {
        new_wall.set_attribute_value(attribute.first, attribute.second);
    }
    new_wall.to_string(std::cout);
    std::cout << std::endl;
    // end::example

    return 0;
}
