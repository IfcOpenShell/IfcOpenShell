// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): reading the property sets of an instance.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 12_property_sets <model.ifc>" << std::endl;
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
    // Unlike ifcopenshell.util.element.get_psets() in Python, the C++ core
    // does not ship a ready made property set helper, so the relationships are
    // walked by hand. IsDefinedBy() lists the relationships, and the property
    // set itself is reached with RelatingPropertyDefinition().
    auto wall = walls.front();
    for (auto& relationship : wall.IsDefinedBy()) {
        auto definition = relationship.RelatingPropertyDefinition();
        if (auto pset = definition.as<Ifc4::IfcPropertySet>()) {
            pset.to_string(std::cout);
            std::cout << std::endl;
            for (auto& property : pset.HasProperties()) {
                property.to_string(std::cout);
                std::cout << std::endl;
            }
        }
        // beware: definition can also be a Quantity Set, or a Predefined Property Set, or
        // from IFC4 onwards a IfcPropertySetDefinitionSet (a set of the above)
    }
    // end::example

    return 0;
}
