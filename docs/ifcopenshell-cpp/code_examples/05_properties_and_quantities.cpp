// This file was generated with the assistance of an AI coding tool.
//
// Code examples and mechanisms: reading properties and quantities from an
// element.

#include <ifcparse/express.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <boost/logic/tribool.hpp>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

// The values of an IfcPropertySingleValue are a select over the measure and
// simple value types, so they are cast to whatever concrete type they hold.
// Note that the cast is tested with declaration().is() rather than with the
// value in a condition, because the conversion operators of the value types -
// such as IfcBoolean's operator bool - hide the operator which tells you whether
// the cast applied at all.
// tag::value-casts
void print_value(const Ifc4::IfcPropertySingleValue& property) {
    const auto value = property.NominalValue();
    const auto& declaration = value.declaration();
    if (declaration.is(Ifc4::IfcLabel::Class())) {
        std::cout << static_cast<std::string>(value.as<Ifc4::IfcLabel>());
    } else if (declaration.is(Ifc4::IfcIdentifier::Class())) {
        std::cout << static_cast<std::string>(value.as<Ifc4::IfcIdentifier>());
    } else if (declaration.is(Ifc4::IfcReal::Class())) {
        std::cout << static_cast<double>(value.as<Ifc4::IfcReal>());
    } else if (declaration.is(Ifc4::IfcInteger::Class())) {
        std::cout << static_cast<int64_t>(value.as<Ifc4::IfcInteger>());
    } else if (declaration.is(Ifc4::IfcBoolean::Class())) {
        std::cout << (static_cast<bool>(value.as<Ifc4::IfcBoolean>()) ? ".T." : ".F.");
    } else {
        // Measures with a unit, such as IfcThermalTransmittanceMeasure, are
        // defined types over one of the values above, and are printed here as
        // the instance they are.
        property.to_string(std::cout);
    }
}
// end::value-casts

// tag::value-visitor
// A value can also be read without knowing any of the schema level value types.
// get_attribute_value() returns an attribute in the type it is stored in, and
// apply_visitor() calls the matching overload of the visitor. A value of
// IfcThermalTransmittanceMeasure arrives as a double here, and the select the
// schema puts around it never enters into it.
struct print_attribute {
    void operator()(bool value) const { std::cout << (value ? ".T." : ".F."); }
    void operator()(boost::logic::tribool value) const {
        // The three valued LOGICAL of the IFC schema, which is unknown when the
        // value is indeterminate.
        std::cout << (boost::logic::indeterminate(value) ? ".U." : (value ? ".T." : ".F."));
    }
    void operator()(int64_t value) const { std::cout << value; }
    void operator()(double value) const { std::cout << value; }
    void operator()(const std::string& value) const { std::cout << value; }
    void operator()(const express::base& value) const {
        // An attribute which holds a value type, such as the
        // IfcThermalTransmittanceMeasure above, is stored as the instance of that
        // type, and the value itself is its first attribute. Anything else, such
        // as a reference to another instance, is printed the way it appears in
        // the file.
        if (value.declaration().as_type_declaration() != nullptr) {
            value.get_attribute_value(0).apply_visitor(*this);
        } else {
            value.to_string(std::cout);
        }
    }
    // Aggregates, binary values, and the placeholders of an incomplete file are
    // not handled here.
    template <typename T>
    void operator()(const T&) const {
        std::cout << "<not a simple value>";
    }
};

void print_stored_value(const Ifc4::IfcPropertySingleValue& property) {
    // NominalValue is the third attribute of an IfcPropertySingleValue.
    property.get_attribute_value(2).apply_visitor(print_attribute{});
}
// end::value-visitor

// tag::print-definitions
// Both IfcPropertySet (regular properties) and IfcElementQuantity (physical
// quantities such as length, area, or volume) are IfcPropertySetDefinition, so
// a single cast tells you which one you got. They are handled separately here
// because their values are reached in different ways.
void print_definitions(const std::vector<Ifc4::IfcPropertySetDefinition>& definitions) {
    for (auto& definition : definitions) {
        if (auto property_set = definition.as<Ifc4::IfcPropertySet>()) {
            std::cout << "  " << property_set.Name().value_or("<unnamed>") << std::endl;
            for (auto& property : property_set.HasProperties()) {
                if (auto single = property.as<Ifc4::IfcPropertySingleValue>()) {
                    // Unlike the optional Name of an IfcRoot, the name of a
                    // property is mandatory.
                    std::cout << "    " << single.Name() << " = ";
                    print_value(single);
                    std::cout << std::endl;
                }
            }
        } else if (auto quantities = definition.as<Ifc4::IfcElementQuantity>()) {
            std::cout << "  " << quantities.Name().value_or("<unnamed>") << std::endl;
            for (auto& quantity : quantities.Quantities()) {
                // Quantity values are in the units of the project, they are not
                // converted to SI units here.
                if (auto length = quantity.as<Ifc4::IfcQuantityLength>()) {
                    std::cout << "    " << length.Name() << " = " << length.LengthValue() << std::endl;
                } else if (auto area = quantity.as<Ifc4::IfcQuantityArea>()) {
                    std::cout << "    " << area.Name() << " = " << area.AreaValue() << std::endl;
                } else if (auto volume = quantity.as<Ifc4::IfcQuantityVolume>()) {
                    std::cout << "    " << volume.Name() << " = " << volume.VolumeValue() << std::endl;
                }
                // IfcQuantityWeight, IfcQuantityCount and IfcQuantityTime follow
                // exactly the same pattern.
            }
        } else {
            // Not every definition is a named set of values: the property
            // definitions of a window or a door type, for example an
            // IfcWindowLiningProperties, are entities with attributes of their
            // own instead.
            definition.to_string(std::cout);
            std::cout << std::endl;
        }
    }
}
// end::print-definitions

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 05_properties_and_quantities <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }
    auto windows = model.instances_by_type<Ifc4::IfcWindow>();
    if (windows.empty()) {
        std::cerr << "No IfcWindow instances found" << std::endl;
        return 1;
    }
    auto window = windows.front();
    std::cout << "Inspecting " << window.Name().value_or("<unnamed>") << std::endl;

    std::cout << "Element-level property sets:" << std::endl;
    // tag::element-level
    // A frequent point of confusion is that IsDefinedBy() does not return the
    // property set itself. It lists the relationships pointing at the element,
    // and the relationship still has to be unwrapped through
    // RelatingPropertyDefinition() to reach the actual definitions.
    for (auto& relationship : window.IsDefinedBy()) {
        auto definition = relationship.RelatingPropertyDefinition();
        // The definition is a select, because a relationship can also assign a
        // group of definitions at once.
        std::vector<Ifc4::IfcPropertySetDefinition> definitions;
        if (auto single = definition.as<Ifc4::IfcPropertySetDefinition>()) {
            definitions.push_back(single);
        } else if (auto group = definition.as<Ifc4::IfcPropertySetDefinitionSet>()) {
            definitions = static_cast<std::vector<Ifc4::IfcPropertySetDefinition>>(group);
        }
        print_definitions(definitions);
    }
    // end::element-level

    std::cout << "Type-level property sets:" << std::endl;
    // tag::type-level
    // There is a second, easily missed source of properties: the element's
    // type. Properties assigned to, for example, a shared IfcWindowType apply to
    // every element of that type. They are reached in a completely different
    // way, through IsTypedBy() and then straight to HasPropertySets(), with no
    // relationship in between to unwrap.
    auto typed_by = window.IsTypedBy();
    if (!typed_by.empty()) {
        // Unlike IsDefinedBy(), an element is defined by at most one type.
        auto type = typed_by.front().RelatingType();
        if (auto property_sets = type.HasPropertySets()) {
            print_definitions(*property_sets);
        }
    }
    // end::type-level

    // tag::value-visitor-use
    // The value of the first property of the first property set, read as the
    // type the file stores it in, without knowing which of the IFC value types
    // is involved. Note that the property sets above were printed by casting to
    // the schema types instead, this is the alternative to that.
    for (auto& relationship : window.IsDefinedBy()) {
        auto property_set = relationship.RelatingPropertyDefinition().as<Ifc4::IfcPropertySet>();
        if (!property_set || property_set.HasProperties().empty()) {
            continue;
        }
        auto property = property_set.HasProperties().front().as<Ifc4::IfcPropertySingleValue>();
        if (property) {
            std::cout << property.Name() << " = ";
            print_stored_value(property);
            std::cout << std::endl;
        }
        break;
    }
    // end::value-visitor-use

    return 0;
}
