// This file was generated with the assistance of an AI coding tool.
//
// Code examples and mechanisms: reading out attributes of an IfcProduct.

#include <ifcparse/express.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 03_read_attributes <model.ifc>" << std::endl;
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
    // The properties of an IfcProduct, and by extension of any derived class,
    // are read by calling the accessor of the same name: GlobalId(), Name(),
    // and so on. Optional attributes, such as Name and Description, are wrapped
    // in a std::optional. Attributes which reference another instance report as
    // empty - their operator bool returns false - when they are not set.
    auto wall = walls.front();
    std::cout << wall.GlobalId() << std::endl;
    std::cout << wall.Name().value_or("<unnamed>") << std::endl;
    std::cout << wall.Description().value_or("<no description>") << std::endl;
    if (!wall.ObjectPlacement()) {
        std::cout << "<no object placement>" << std::endl;
    }
    // end::example

    // tag::agnostic-example
    // The same values are available without the schema classes, by attribute
    // index, in the order in which the attributes appear in the IFC schema,
    // or by name.
    std::cout << static_cast<std::string>(wall.get_attribute_value(0)) << std::endl;
    if (auto product = wall.as<express::entity>()) {
        std::cout << product.get_value<std::string>("Name", "<unnamed>") << std::endl;
    }
    // end::agnostic-example

    return 0;
}
