// This file was generated with the assistance of an AI coding tool.

#include <catch2/catch_test_macros.hpp>
#include <ifcparse/exception.h>
#include <ifcparse/file.h>
#include <ifcparse/dense_id_map.h>
#include <ifcparse/guid_map.h>
#include <ifcparse/parse.h>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <sstream>
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

TEST_CASE("Tokens without a string representation do not recurse in to_string()", "[ifcparse]") {
    // to_string() used to delegate to as_string() for every token type it did
    // not handle explicitly, while as_string() builds its exception message
    // with to_string(). An EOF marker or an instance name therefore recursed
    // between the two until the stack was exhausted.
    ifcopenshell::token eof;
    REQUIRE(eof.type == ifcopenshell::token::Token_NONE);
    CHECK_THROWS_AS(eof.to_string(), ifcopenshell::invalid_token_exception);
    CHECK_THROWS_AS(eof.as_string(), ifcopenshell::invalid_token_exception);

    ifcopenshell::token identifier(0, ifcopenshell::token::Token_IDENTIFIER, (int64_t)123);
    CHECK(identifier.to_string() == "#123");
    CHECK_THROWS_AS(identifier.as_string(), ifcopenshell::invalid_token_exception);
}

TEST_CASE("Files that contain no tokens are rejected rather than crashing", "[ifcparse]") {
    // The header parser asks the lexer for a keyword before checking for EOF,
    // so input that lexes to zero tokens reaches token::as_string() on the EOF
    // marker. Parsing must fail cleanly instead of overflowing the stack.
    const std::vector<std::string> inputs{" ", "\r\n\t  ", "/* only a comment */"};

    for (const auto& contents : inputs) {
        INFO("input: " << contents);
        ifcopenshell::logger log;
        std::istringstream input(contents);
        ifcopenshell::file file(input, (int)contents.size(), log);

        CHECK(file.good().value() != ifcopenshell::file_open_status::SUCCESS);
    }
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

TEST_CASE("Deleting an instance unregisters the records its own attributes contributed", "[ifcparse]") {
    ifcopenshell::file file(ifcopenshell::schema_by_name("IFC4"));
    const auto* point_declaration = file.schema()->declaration_by_name("IfcCartesianPoint");
    const auto* polyline_declaration = file.schema()->declaration_by_name("IfcPolyline");
    const auto* trimmed_curve_declaration = file.schema()->declaration_by_name("IfcTrimmedCurve");

    auto target = file.create(point_declaration);
    auto second = file.create(point_declaration);

    // A reference registered before the first lookup lands in the base tier,
    // one registered after it in the delta.
    auto base_referencer = file.create(polyline_declaration);
    base_referencer.set_attribute_value(0, std::vector<express::base>{target, target});
    REQUIRE(file.instances_by_reference(target.id()).size() == 2);
    auto delta_referencer = file.create(polyline_declaration);
    delta_referencer.set_attribute_value(0, std::vector<express::base>{target, second});
    REQUIRE(file.instances_by_reference(target.id()).size() == 3);

    // Duplicate references in one aggregate contribute two records; deleting
    // the source must drop both.
    file.remove_entity(base_referencer);
    CHECK(file.instances_by_reference(target.id()).size() == 1);

    // Referencing the same instance through two attributes contributes a
    // record per attribute; deleting the source must drop them all.
    auto trimmed = file.create(trimmed_curve_declaration);
    trimmed.set_attribute_value(1, std::vector<express::base>{second});
    trimmed.set_attribute_value(2, std::vector<express::base>{second});
    CHECK(file.instances_by_reference(second.id()).size() == 3);
    file.remove_entity(trimmed);
    CHECK(file.instances_by_reference(second.id()).size() == 1);

    // Deleting the target first prunes it out of the source's attribute, so
    // deleting the source afterwards finds nothing left to unregister.
    file.remove_entity(target);
    file.remove_entity(delta_referencer);
    CHECK(file.instances_by_reference(second.id()).empty());
    CHECK(file.get_total_inverses(second.id()) == 0);
}

TEST_CASE("Batch deletion prunes surviving referencers and leaves no stale records", "[ifcparse]") {
    ifcopenshell::file file(ifcopenshell::schema_by_name("IFC4"));
    const auto* point_declaration = file.schema()->declaration_by_name("IfcCartesianPoint");
    const auto* polyline_declaration = file.schema()->declaration_by_name("IfcPolyline");

    auto kept_point = file.create(point_declaration);
    std::vector<express::base> doomed_points;
    for (int i = 0; i < 50; ++i) {
        doomed_points.push_back(file.create(point_declaration));
    }

    // The survivor references every doomed point plus the kept one; a doomed
    // referencer references the kept point.
    auto survivor = file.create(polyline_declaration);
    auto survivor_points = doomed_points;
    survivor_points.push_back(kept_point);
    survivor.set_attribute_value(0, survivor_points);
    auto doomed_referencer = file.create(polyline_declaration);
    doomed_referencer.set_attribute_value(0, std::vector<express::base>{kept_point});
    REQUIRE(file.instances_by_reference(kept_point.id()).size() == 2);

    file.batch();
    for (auto& point : doomed_points) {
        file.remove_entity(point);
    }
    file.remove_entity(doomed_referencer);
    file.unbatch();

    CHECK((std::vector<express::base>)survivor.get_attribute_value(0) == std::vector<express::base>{kept_point});
    CHECK(file.instances_by_reference(kept_point.id()).size() == 1);
    CHECK(file.get_total_inverses(kept_point.id()) == 1);
    for (auto& point : doomed_points) {
        CHECK(file.instances_by_reference(point.id()).empty());
    }
    CHECK(file.instances_by_reference(doomed_referencer.id()).empty());
}

TEST_CASE("dense_id_map keeps dense names in a vector and sparse names in the overflow", "[ifcparse]") {
    int a = 0, b = 0, c = 0, d = 0;
    ifcopenshell::dense_id_map<int*> map;
    CHECK(map.insert({1, &a}).second);
    CHECK(map.insert({3, &b}).second);
    CHECK_FALSE(map.insert({3, &c}).second);
    // Far beyond the populated range: must not grow the vector to a billion slots.
    CHECK(map.insert({1u << 30, &c}).second);
    CHECK(map.insert({2, &d}).second);
    CHECK(map.size() == 4);
    CHECK(map.find(3)->second == &b);
    CHECK(map.find(1u << 30)->second == &c);
    CHECK(map.find(4) == map.end());
    CHECK(map.find(5000) == map.end());

    std::vector<uint32_t> visited;
    for (auto it = map.begin(); it != map.end(); ++it) {
        visited.push_back(it->first);
    }
    CHECK(visited == std::vector<uint32_t>{1, 2, 3, 1u << 30});

    CHECK(map.erase(3) == 1);
    CHECK(map.erase(3) == 0);
    CHECK(map.erase(1u << 30) == 1);
    CHECK(map.size() == 2);
    CHECK(map.find(3) == map.end());
    visited.clear();
    for (const auto& entry : map) {
        visited.push_back(entry.first);
    }
    CHECK(visited == std::vector<uint32_t>{1, 2});
    CHECK(map.insert({3, &b}).second);
    CHECK(map.find(3)->second == &b);
}

TEST_CASE("guid_map keeps GlobalIds inline and still accepts overlong keys", "[ifcparse]") {
    int a = 0, b = 0, c = 0;
    ifcopenshell::guid_map<int*> map;
    const std::string g1 = "0YvctVUKr0kugbFTf53O9L", g2 = "1F$7lN9$r5MOA_lpAoNM52", overlong = "this-key-is-far-longer-than-a-guid";
    CHECK(map.insert({g1, &a}).second);
    CHECK_FALSE(map.insert({g1, &b}).second);
    map[g2] = &b;
    map[overlong] = &c;
    CHECK(map.size() == 3);
    CHECK(map.find(g1)->second == &a);
    CHECK(map.find(g2)->second == &b);
    CHECK(map.find(overlong)->second == &c);
    CHECK(map.find("0YvctVUKr0kugbFTf53O9M") == map.end());
    CHECK(map.find("") == map.end());
    size_t visited = 0;
    for (auto it = map.begin(); it != map.end(); ++it) {
        CHECK(map.find(it->first)->second == it->second);
        ++visited;
    }
    CHECK(visited == 3);
    CHECK(map.erase(g1) == 1);
    CHECK(map.erase(g1) == 0);
    CHECK(map.erase(overlong) == 1);
    CHECK(map.size() == 1);
    CHECK(map.find(g1) == map.end());
}

namespace {
const char* const reference_resolution_spf =
    "ISO-10303-21;\n"
    "HEADER;\n"
    "FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');\n"
    "FILE_NAME('','',(''),(''),'','','');\n"
    "FILE_SCHEMA(('IFC4'));\n"
    "ENDSEC;\n"
    "DATA;\n"
    "#1=IFCCARTESIANPOINT((0.,0.,0.));\n"
    "#2=IFCCARTESIANPOINT((1.,0.,0.));\n"
    "#3=IFCCARTESIANPOINT((0.,1.,0.));\n"
    "#4=IFCPOLYLINE((#1,#2,#3));\n"
    "#5=IFCTRIMMEDCURVE(#4,(IFCPARAMETERVALUE(0.),#1),(IFCPARAMETERVALUE(1.)),.T.,.PARAMETER.);\n"
    "#6=IFCPROPERTYSINGLEVALUE('A',$,IFCLABEL('x'),$);\n"
    "#7=IFCPROPERTYSET('0YvctVUKr0kugbFTf53O9L',$,'Pset',$,(#6,#999));\n"
    "#8=IFCWALL('1F$7lN9$r5MOA_lpAoNM52',$,$,$,$,$,$,$,$);\n"
    "#9=IFCRELDEFINESBYPROPERTIES('2F$7lN9$r5MOA_lpAoNM53',$,$,$,(#8),#7);\n"
    "#10=IFCBSPLINESURFACEWITHKNOTS(1,1,((#1,#2),(#3,#999)),.UNSPECIFIED.,.F.,.F.,.U.,(2,2),(2,2),(0.,1.),(0.,1.),.UNSPECIFIED.);\n"
    "#11=IFCRELAGGREGATES('3F$7lN9$r5MOA_lpAoNM54',$,$,$,#999,(#8));\n"
    "ENDSEC;\n"
    "END-ISO-10303-21;\n";
}

TEST_CASE("References are resolved in place: scalars, lists, nested lists, mixed selects and missing names", "[ifcparse]") {
    std::string data(reference_resolution_spf);
    ifcopenshell::file file(data.data(), (int)data.size());
    REQUIRE(file.good());

    const std::vector<express::base> points = file.instance_by_id(4).get_attribute_value(0);
    REQUIRE(points.size() == 3);
    CHECK(points[0].id() == 1);
    CHECK(points[2].id() == 3);

    // A select-typed list mixing an inline typed value with a reference.
    const std::vector<express::base> trim1 = file.instance_by_id(5).get_attribute_value(1);
    REQUIRE(trim1.size() == 2);
    CHECK(trim1[0].declaration().name() == "IfcParameterValue");
    CHECK(trim1[1].id() == 1);
    const std::vector<express::base> trim2 = file.instance_by_id(5).get_attribute_value(2);
    REQUIRE(trim2.size() == 1);
    CHECK(trim2[0].declaration().name() == "IfcParameterValue");

    // A missing name is dropped from a list and nulls a scalar.
    const std::vector<express::base> properties = file.instance_by_id(7).get_attribute_value(4);
    REQUIRE(properties.size() == 1);
    CHECK(properties[0].id() == 6);
    CHECK(file.instance_by_id(11).get_attribute_value(4).isNull());
    const std::vector<express::base> related = file.instance_by_id(11).get_attribute_value(5);
    REQUIRE(related.size() == 1);
    CHECK(related[0].id() == 8);

    const express::base definition = file.instance_by_id(9).get_attribute_value(5);
    REQUIRE(definition);
    CHECK(definition.id() == 7);

    const std::vector<std::vector<express::base>> control_points = file.instance_by_id(10).get_attribute_value(2);
    REQUIRE(control_points.size() == 2);
    REQUIRE(control_points[0].size() == 2);
    CHECK(control_points[0][1].id() == 2);
    REQUIRE(control_points[1].size() == 1);
    CHECK(control_points[1][0].id() == 3);

    // Inverses were registered for every reference, resolved or not.
    CHECK(file.instances_by_reference(1).size() == 3);
    CHECK(file.instances_by_reference(8).size() == 2);
}

TEST_CASE("References to bypassed instances are dropped from slots and from mixed lists", "[ifcparse]") {
    const auto path = std::filesystem::temp_directory_path() / "ifcopenshell_reference_resolution_test.ifc";
    {
        std::ofstream out(path);
        out << reference_resolution_spf;
    }
    ifcopenshell::file file(ifcopenshell::uninitialized_tag{});
    file.bypass_type("IfcCartesianPoint");
    REQUIRE(file.initialize(path.string()));
    std::filesystem::remove(path);

    const std::vector<express::base> points = file.instance_by_id(4).get_attribute_value(0);
    CHECK(points.empty());
    const std::vector<express::base> trim1 = file.instance_by_id(5).get_attribute_value(1);
    REQUIRE(trim1.size() == 1);
    CHECK(trim1[0].declaration().name() == "IfcParameterValue");
    const std::vector<std::vector<express::base>> control_points = file.instance_by_id(10).get_attribute_value(2);
    REQUIRE(control_points.size() == 2);
    CHECK(control_points[0].empty());
    CHECK(control_points[1].empty());
}

TEST_CASE("dense_id_map finds names inserted before the vector grew past them", "[ifcparse]") {
    // A Bimserver-style file: names start high and arrive in no particular
    // order, so the first ones land in the overflow while the vector is small.
    ifcopenshell::dense_id_map<int*> map;
    std::vector<int> values(200000);
    const uint32_t base = 3000000;
    for (uint32_t i = 0; i < 200000; ++i) {
        const uint32_t name = base + ((i * 7919u) % 200000u);
        REQUIRE(map.insert({name, &values[i]}).second);
    }
    CHECK(map.size() == 200000);
    for (uint32_t i = 0; i < 200000; ++i) {
        const uint32_t name = base + ((i * 7919u) % 200000u);
        REQUIRE(map.find(name) != map.end());
        REQUIRE(map.find(name)->second == &values[i]);
    }
    size_t visited = 0;
    for (const auto& entry : map) {
        CHECK(entry.first >= base);
        ++visited;
    }
    CHECK(visited == 200000);
    CHECK(map.erase(base + 5) == 1);
    CHECK(map.find(base + 5) == map.end());
    CHECK(map.size() == 199999);
}

namespace {
void check_lazy_matches_strict(const std::string& path) {
    ifcopenshell::file strict(path);
    REQUIRE(strict.good());
    ifcopenshell::file lazy(ifcopenshell::uninitialized_tag{});
    lazy.lazy_loading(true);
    REQUIRE(lazy.initialize(path));
    REQUIRE(lazy.lazy_loading());
    REQUIRE(lazy.schema() == strict.schema());

    size_t strict_count = 0;
    for (auto it = strict.begin(); it != strict.end(); ++it) {
        const express::base a = it->second;
        const express::base b = lazy.instance_by_id((int)a.id());
        REQUIRE(b);
        REQUIRE(&b.declaration() == &a.declaration());
        REQUIRE(lazy.instances_by_reference((int)a.id()).size() == strict.instances_by_reference((int)a.id()).size());
        std::ostringstream sa, sb;
        a.to_string(sa);
        b.to_string(sb);
        REQUIRE(sb.str() == sa.str());
        ++strict_count;
    }
    size_t lazy_count = 0;
    for (auto it = lazy.begin(); it != lazy.end(); ++it) {
        ++lazy_count;
    }
    CHECK(lazy_count == strict_count);

    for (const auto& rooted : strict.instances_by_type("IfcRoot")) {
        const std::string guid = rooted.get_attribute_value(0);
        REQUIRE(lazy.instance_by_guid(guid).id() == rooted.id());
    }
}
}

TEST_CASE("Lazy loading yields the same instances, attributes, inverses and GlobalIds as a full parse", "[ifcparse]") {
    check_lazy_matches_strict(std::string(IFCOPENSHELL_TEST_FIXTURES) + "/ColumnPSetsOfSets.ifc");

    const auto path = std::filesystem::temp_directory_path() / "ifcopenshell_lazy_loading_test.ifc";
    {
        std::ofstream out(path);
        out << reference_resolution_spf;
    }
    check_lazy_matches_strict(path.string());
    std::filesystem::remove(path);
}

TEST_CASE("Lazy loading falls back to the full parser on syntax the scanner does not handle", "[ifcparse]") {
    const auto path = std::filesystem::temp_directory_path() / "ifcopenshell_lazy_fallback_test.ifc";
    {
        std::ofstream out(path);
        // A stray token between instances is legal for the full parser to complain about and skip, but the scanner gives up.
        std::string spf(reference_resolution_spf);
        spf.replace(spf.find("#8=IFCWALL"), 0, "STRAY;\n");
        out << spf;
    }
    ifcopenshell::file lazy(ifcopenshell::uninitialized_tag{});
    lazy.lazy_loading(true);
    lazy.initialize(path.string());
    std::filesystem::remove(path);
    CHECK_FALSE(lazy.lazy_loading());
    CHECK(lazy.instance_by_id(4));
}
