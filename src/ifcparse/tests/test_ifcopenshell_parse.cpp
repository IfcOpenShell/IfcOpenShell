// This file was generated with the assistance of an AI coding tool.

#include <catch2/catch_test_macros.hpp>
#include <ifcparse/file.h>
#include <string>
#include <vector>

TEST_CASE("IfcPropertySetDefinitionSet references are resolved without replacing their owner", "[ifcparse]") {
    const std::string fixture = std::string(IFCOPENSHELL_TEST_FIXTURES) + "/ColumnPSetsOfSets.ifc";
    ifcopenshell::file file(fixture);

    REQUIRE(file.good());

    const auto relationship = file.instance_by_id(139);
    REQUIRE(relationship);
    CHECK(relationship.id() == 139);
    CHECK(relationship.declaration().name() == "IfcRelDefinesByProperties");

    const express::base definition_set = relationship.get_attribute_value(5);
    REQUIRE(definition_set);
    CHECK(definition_set.declaration().name() == "IfcPropertySetDefinitionSet");

    const std::vector<express::base> definitions = definition_set.get_attribute_value(0);
    REQUIRE(definitions.size() == 2);
    CHECK(definitions[0].id() == 136);
    CHECK(definitions[1].id() == 138);
}

TEST_CASE("Bypassed entity types include their subtypes", "[ifcparse]") {
    const std::string fixture = std::string(IFCOPENSHELL_TEST_FIXTURES) + "/ColumnPSetsOfSets.ifc";
    ifcopenshell::file file(ifcopenshell::uninitialized_tag{});
    file.bypass_type("IfcRepresentationItem");

    REQUIRE(file.initialize(fixture));
    CHECK(file.instances_by_type("IfcRepresentationItem").empty());
    CHECK(file.instances_by_type("IfcCartesianPoint").empty());
}
