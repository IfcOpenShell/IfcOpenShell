// This file was generated with the assistance of an AI coding tool.
//
// Code examples and mechanisms: navigating relationships in IFC.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <vector>

// tag::example
// While a building is naturally read as a tree of spatial elements (project >
// site > building > storey > element), the rest of the information in an IFC
// file is a graph: relationships join objects to the meta data describing them.
// The following function shows how the property sets of a given IfcObject are
// extracted. IsDefinedBy() lists the relationships which point at the object,
// and the property set itself is reached through RelatingPropertyDefinition().
void extract_property_sets(const Ifc4::IfcObject& object, std::vector<Ifc4::IfcPropertySet>& property_sets) {
    for (auto& relationship : object.IsDefinedBy()) {
        auto definition = relationship.RelatingPropertyDefinition();
        // The definition is a select, and is only an IfcPropertySet when the
        // values were assigned as a property set rather than as a quantity set.
        if (auto property_set = definition.as<Ifc4::IfcPropertySet>()) {
            property_sets.push_back(property_set);
        }
    }
}
// end::example

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 04_navigate_relationships <model.ifc>" << std::endl;
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

    std::vector<Ifc4::IfcPropertySet> property_sets;
    extract_property_sets(walls.front(), property_sets);
    for (auto& property_set : property_sets) {
        std::cout << property_set.Name().value_or("<unnamed>") << std::endl;
    }

    return 0;
}
