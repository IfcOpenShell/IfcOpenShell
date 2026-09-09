// This file was generated with the assistance of an AI coding tool.

#include <catch2/catch_test_macros.hpp>
#include <ifcparse/file.h>
#include <ifcparse/parse.h>
#include <string>
#include <vector>

TEST_CASE("SPF strings can be encoded and decoded", "[ifcparse]") {
    const std::string decoded = "Caf\xC3\xA9" "'s \\";
    const std::string encoded = R"('Caf\X2\00E9\X0\''s \\')";

    CHECK(ifcopenshell::encode_spf_string(decoded) == encoded);
    CHECK(ifcopenshell::decode_spf_string(encoded) == decoded);
    CHECK(ifcopenshell::decode_spf_string(encoded.substr(1, encoded.size() - 2)) == decoded);
}

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

TEST_CASE("Aggregate inverse updates preserve reference multiplicity", "[ifcparse]") {
    ifcopenshell::file file(ifcopenshell::schema_by_name("IFC4"));
    const auto* segment_declaration = file.schema()->declaration_by_name("IfcCompositeCurveSegment");
    auto curve = file.create(file.schema()->declaration_by_name("IfcCompositeCurve"));
    auto segment_a = file.create(segment_declaration);
    auto segment_b = file.create(segment_declaration);
    auto segment_c = file.create(segment_declaration);
    auto segment_d = file.create(segment_declaration);
    const auto inverse_count = [&file](const express::base& instance) {
        return file.instances_by_reference(instance.id()).size();
    };

    curve.set_attribute_value(0, std::vector<express::base>{segment_a, segment_a, segment_b, segment_c});
    CHECK(inverse_count(segment_a) == 2);
    CHECK(inverse_count(segment_b) == 1);
    CHECK(inverse_count(segment_c) == 1);
    CHECK(inverse_count(segment_d) == 0);

    curve.set_attribute_value(0, std::vector<express::base>{segment_a, segment_a, segment_b, segment_c, segment_d});
    CHECK(inverse_count(segment_a) == 2);
    CHECK(inverse_count(segment_b) == 1);
    CHECK(inverse_count(segment_c) == 1);
    CHECK(inverse_count(segment_d) == 1);

    curve.set_attribute_value(0, std::vector<express::base>{segment_a, segment_a, segment_b, segment_c});
    CHECK(inverse_count(segment_a) == 2);
    CHECK(inverse_count(segment_b) == 1);
    CHECK(inverse_count(segment_c) == 1);
    CHECK(inverse_count(segment_d) == 0);

    const std::vector<express::base> reordered{segment_c, segment_a, segment_b, segment_a};
    curve.set_attribute_value(0, reordered);
    CHECK((std::vector<express::base>)curve.get_attribute_value(0) == reordered);
    CHECK(inverse_count(segment_a) == 2);
    CHECK(inverse_count(segment_b) == 1);
    CHECK(inverse_count(segment_c) == 1);
    CHECK(inverse_count(segment_d) == 0);

    curve.set_attribute_value(0, std::vector<express::base>{segment_a, segment_b, segment_b, segment_d});
    CHECK(inverse_count(segment_a) == 1);
    CHECK(inverse_count(segment_b) == 2);
    CHECK(inverse_count(segment_c) == 0);
    CHECK(inverse_count(segment_d) == 1);

    curve.set_attribute_value(0, std::vector<express::base>{segment_c, segment_c, segment_d});
    CHECK(inverse_count(segment_a) == 0);
    CHECK(inverse_count(segment_b) == 0);
    CHECK(inverse_count(segment_c) == 2);
    CHECK(inverse_count(segment_d) == 1);
}

TEST_CASE("Inverse lookups stay consistent across interleaved adds, removals and reads", "[ifcparse]") {
    ifcopenshell::file file(ifcopenshell::schema_by_name("IFC4"));
    const auto* point_declaration = file.schema()->declaration_by_name("IfcCartesianPoint");
    const auto* polyline_declaration = file.schema()->declaration_by_name("IfcPolyline");
    auto target = file.create(point_declaration);
    auto other = file.create(point_declaration);

    const auto referencing_ids = [&file](const express::base& instance) {
        std::vector<int> ids;
        for (const auto& referencing : file.instances_by_reference(instance.id())) {
            ids.push_back(referencing.id());
        }
        std::sort(ids.begin(), ids.end());
        return ids;
    };

    // Reading an inverse after every write is the pattern that used to
    // re-sort the whole index per iteration. Enough iterations to fold the
    // delta into the base several times over.
    std::vector<express::base> polylines;
    std::vector<int> expected;
    for (int i = 0; i < 600; ++i) {
        auto polyline = file.create(polyline_declaration);
        polyline.set_attribute_value(0, std::vector<express::base>{target});
        polylines.push_back(polyline);
        expected.push_back(polyline.id());
        REQUIRE(file.instances_by_reference(target.id()).size() == (size_t)i + 1);
    }
    CHECK(referencing_ids(target) == expected);
    CHECK(file.get_inverse_indices_by_id(target.id()) == std::vector<int>(600, 0));
    CHECK(file.get_total_inverses(target.id()) == 600);

    // Repointing an attribute removes the old record and adds a new one,
    // whether the record lives in the base or in the delta.
    for (int i = 0; i < 600; i += 7) {
        polylines[i].set_attribute_value(0, std::vector<express::base>{other});
        expected.erase(std::find(expected.begin(), expected.end(), polylines[i].id()));
    }
    CHECK(referencing_ids(target) == expected);
    CHECK(file.instances_by_reference(other.id()).size() == 86);

    // The same source referencing the target through two attributes yields two records.
    const auto* trimmed_curve_declaration = file.schema()->declaration_by_name("IfcTrimmedCurve");
    auto trimmed = file.create(trimmed_curve_declaration);
    trimmed.set_attribute_value(1, std::vector<express::base>{target});
    trimmed.set_attribute_value(2, std::vector<express::base>{target});
    CHECK(file.instances_by_reference(target.id()).size() == expected.size() + 2);
    CHECK(file.get_total_inverses(target.id()) == expected.size() + 1);
    trimmed.set_attribute_value(2, std::vector<express::base>{other});
    expected.push_back((int)trimmed.id());
    CHECK(referencing_ids(target) == expected);

    // Deleting a referencing instance drops its records; deleting the
    // target drops the records into it.
    file.remove_entity(polylines[1]);
    expected.erase(std::find(expected.begin(), expected.end(), polylines[1].id()));
    CHECK(referencing_ids(target) == expected);
    file.remove_entity(other);
    CHECK(file.instances_by_reference(other.id()).empty());

    // Removing most of the base tombstones it past the compaction threshold.
    for (int i = 2; i < 600; ++i) {
        if (i % 7 != 0) {
            file.remove_entity(polylines[i]);
        }
    }
    CHECK(referencing_ids(target) == std::vector<int>{(int)trimmed.id()});
}
