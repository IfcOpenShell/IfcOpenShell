// This file was generated with the assistance of an AI coding tool.
//
// Code examples and mechanisms: defensive programming with IfcOpenShell.

#include <ifcparse/express.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 06_defensive_programming <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // Casting is where things go wrong. A reference attribute holds whatever
    // the file references, which is not necessarily what the schema requires,
    // and an attribute of a supertype only holds what one of its subtypes
    // defines. as<>() returns an empty value when the instance is not of the
    // requested type, and an empty value converts to false, so the cast and its
    // check are a single expression. Never use the result of a cast that was
    // not checked. A reference which never resolved - a STEP ID pointing at an
    // instance which does not exist - is empty as well, and does not throw.
    std::size_t property_sets = 0;
    for (auto& instance : model.instances_by_type("IfcRelationship")) {
        if (auto relationship = instance.as<Ifc4::IfcRelDefinesByProperties>()) {
            auto definition = relationship.RelatingPropertyDefinition();
            // A definition is not always an IfcPropertySet: it can also be an
            // IfcElementQuantity, or a group of definitions.
            if (auto property_set = definition.as<Ifc4::IfcPropertySet>()) {
                ++property_sets;
            }
        }
    }
    // end::example

    std::cout << property_sets << " property sets assigned by relationship" << std::endl;
    return 0;
}
