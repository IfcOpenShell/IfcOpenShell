// This file was generated with the assistance of an AI coding tool.

#include <catch2/catch_test_macros.hpp>
#include <ifcparse/exception.h>
#include <ifcparse/file.h>
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

TEST_CASE("Only a 22-character GlobalId is indexed", "[ifcparse]") {
    const std::string data =
        "ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION((''),'2;1');\nFILE_NAME('','',(''),(''),'','','');\nFILE_SCHEMA(('IFC4'));\nENDSEC;\nDATA;\n"
        "#1=IFCWALL('0YvctVUKr0kugbFTf53O9L',$,$,$,$,$,$,$,$);\n"
        "#2=IFCWALL('id',$,$,$,$,$,$,$,$);\n"
        "ENDSEC;\nEND-ISO-10303-21;\n";
    std::string copy(data);
    ifcopenshell::file file(copy.data(), (int)copy.size());
    REQUIRE(file.good());
    CHECK(file.instance_by_guid("0YvctVUKr0kugbFTf53O9L").id() == 1);
    CHECK_THROWS(file.instance_by_guid("id"));
    CHECK_THROWS(file.instance_by_guid("0YvctVUKr0kugbFTf53O9M"));
    // A wall created after the open follows the same rule.
    express::base wall = file.instance_by_id(2);
    wall.set_attribute_value(0, std::string("1F$7lN9$r5MOA_lpAoNM52"));
    CHECK(file.instance_by_guid("1F$7lN9$r5MOA_lpAoNM52").id() == 2);
}
namespace {
struct recording_consumer {
    static constexpr bool decode_strings = false;
    static constexpr bool decode_values = false;
    static constexpr bool keep_keywords = false;
    std::vector<std::pair<size_t, char>> seen;
    std::vector<uint32_t> identifiers;
    bool operator_(size_t pos, char c) {
        seen.push_back({pos, c});
        return true;
    }
    bool identifier(size_t pos, uint32_t value) {
        seen.push_back({pos, '#'});
        identifiers.push_back(value);
        return true;
    }
    bool string(size_t pos, size_t) {
        seen.push_back({pos, '\''});
        return true;
    }
    bool literal(size_t pos) {
        seen.push_back({pos, 'L'});
        return true;
    }
};
} // namespace

TEST_CASE("The index token policy ends every token where the full policy does, without decoding", "[ifcparse]") {
    // Doubled quotes, a \S\' escape (an apostrophe as the page character,
    // which a byte scan would take for the end of the string), a \X2\
    // escape, a comment, binaries, enumerations, numbers and names.
    const std::string data =
        "#1=IFCWALL('it''s','a\\S\\'b','\\X2\\00E9\\X0\\c',/* #9 */ #2, \"0A\", .T., -1.5E-3, 42, $, *, (IFCLABEL('x'), #3));\n";
    ifcopenshell::file_reader<ifcopenshell::full_buffer_impl> full_reader(data, ifcopenshell::caller_fed_tag{});
    ifcopenshell::file_reader<ifcopenshell::full_buffer_impl> index_reader(data, ifcopenshell::caller_fed_tag{});
    ifcopenshell::spf_lexer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>> full(&full_reader), index(&index_reader);
    size_t count = 0;
    std::vector<unsigned> names;
    while (true) {
        ifcopenshell::token a = full.next(), b = index.next<ifcopenshell::index_tokens>();
        REQUIRE((bool)a == (bool)b);
        if (!a) {
            break;
        }
        ++count;
        CHECK(a.start_pos == b.start_pos);
        CHECK(full_reader.tell() == index_reader.tell());
        if (a.is_identifier()) {
            REQUIRE(b.is_identifier());
            CHECK(a.as_identifier() == b.as_identifier());
            names.push_back(b.as_identifier());
        } else if (a.is_keyword()) {
            REQUIRE(b.is_keyword());
            CHECK(a.as_string() == b.as_string());
        } else if (a.is_operator()) {
            REQUIRE(b.is_operator());
            CHECK(a.value_char == b.value_char);
        } else if (a.is_string()) {
            CHECK(b.type == ifcopenshell::token::Token_STRING);
        } else {
            CHECK(b.type == ifcopenshell::token::Token_LITERAL);
        }
        full.reset_pool();
        index.reset_pool();
    }
    CHECK(count == 34);
    CHECK(names == std::vector<unsigned>{1, 2, 3});
    // A scan() consumer that decodes nothing sees the same tokens at the same
    // positions as next() under the index policy, in one pass.
    ifcopenshell::file_reader<ifcopenshell::full_buffer_impl> scan_reader(data, ifcopenshell::caller_fed_tag{});
    ifcopenshell::spf_lexer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>> scanner(&scan_reader);
    recording_consumer recorded;
    scanner.scan(recorded);
    ifcopenshell::file_reader<ifcopenshell::full_buffer_impl> index_again(data, ifcopenshell::caller_fed_tag{});
    ifcopenshell::spf_lexer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>> index2(&index_again);
    std::vector<std::pair<size_t, char>> expected;
    while (true) {
        ifcopenshell::token tk = index2.next<ifcopenshell::index_tokens>();
        if (!tk) {
            break;
        }
        expected.push_back({tk.start_pos, tk.is_operator() ? tk.value_char : tk.is_identifier() ? '#' : tk.is_string() ? '\'' : (tk.is_keyword() ? 'K' : 'L')});
        index2.reset_pool();
    }
    // Keywords inside the attribute list are literals to a consumer that keeps no keyword text.
    for (auto& e : expected) {
        if (e.second == 'K') {
            e.second = 'L';
        }
    }
    CHECK(recorded.seen == expected);
    // And the full policy decoded the escapes.
    ifcopenshell::file_reader<ifcopenshell::full_buffer_impl> again(data, ifcopenshell::caller_fed_tag{});
    ifcopenshell::spf_lexer<ifcopenshell::file_reader<ifcopenshell::full_buffer_impl>> lexer(&again);
    lexer.next(); lexer.next(); lexer.next(); lexer.next();
    CHECK(lexer.next().as_string() == "it's");
    lexer.next();
    CHECK(lexer.next().as_string() == "a\xc2\xa7" "b");
}

TEST_CASE("Scanning preserves identifiers and token boundaries across reader pages", "[ifcparse][scan]") {
    const std::string data =
        "#1=IFCEXAMPLE(#0,#+12,#-1,#2147483647,#+-2,#1 2,#000003,"
        "'it''s','a\\S\\'b','\\X2\\00E9\\X0\\c',/* #999 */ .T.,\"0A\",-1.5E-3,$,*,(IFCLABEL(''),#42));#9";
    ifcopenshell::file_reader<ifcopenshell::full_buffer_impl> reference(data, ifcopenshell::caller_fed_tag{});
    ifcopenshell::spf_lexer<decltype(reference)> lexer(&reference);
    recording_consumer expected;
    while (auto tk = lexer.next()) {
        expected.seen.push_back({tk.start_pos, tk.is_operator() ? tk.value_char : tk.is_identifier() ? '#' : tk.is_string() ? '\'' : 'L'});
        if (tk.is_identifier()) {
            expected.identifiers.push_back(tk.as_identifier());
        }
        lexer.reset_pool();
    }
    CHECK(expected.identifiers == std::vector<uint32_t>{1, 0, 12, UINT32_MAX, INT32_MAX, UINT32_MAX - 1, 12, 3, 42, 9});
    const auto check = [&](auto& source) {
        ifcopenshell::spf_lexer<std::decay_t<decltype(source)>> scanner(&source);
        recording_consumer actual;
        scanner.scan(actual);
        CHECK(actual.seen == expected.seen);
        CHECK(actual.identifiers == expected.identifiers);
        CHECK(source.tell() == data.size());
    };
    reference.seek(0);
    check(reference);
    ifcopenshell::file_reader<ifcopenshell::pushed_sequential_impl> pushed(ifcopenshell::caller_fed_tag{});
    for (char c : data) {
        pushed.push_next_page(std::string(1, c));
    }
    check(pushed);
    const auto path = std::filesystem::temp_directory_path() / "ifcopenshell_scan_pages_test.ifc";
    {
        std::ofstream out(path, std::ios::binary);
        out << data;
    }
    for (size_t page_size : {1, 2, 3, 7, 8, 9, 16, 64}) {
        CAPTURE(page_size);
        ifcopenshell::file_reader<ifcopenshell::paged_file_impl> paged(path.string(), page_size, 1);
        check(paged);
    }
    std::filesystem::remove(path);
}

TEST_CASE("Identifier shortcuts retain invalid-token errors", "[ifcparse][scan]") {
    for (const std::string data : {"#;", "#+;", "#2147483648;", "#-2147483649;", "#12a;", "#1.0;", "##2;"}) {
        CAPTURE(data);
        ifcopenshell::file_reader<ifcopenshell::full_buffer_impl> reader(data, ifcopenshell::caller_fed_tag{});
        ifcopenshell::spf_lexer<decltype(reader)> lexer(&reader);
        CHECK_THROWS_AS(lexer.next(), ifcopenshell::invalid_token_exception);
        reader.seek(0);
        lexer.reset_pool();
        recording_consumer consumer;
        CHECK_THROWS_AS(lexer.scan(consumer), ifcopenshell::invalid_token_exception);
    }
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

TEST_CASE("Lazy loading passes over a stray keyword like the full parser and falls back on what the index pass rejects", "[ifcparse]") {
    const auto path = std::filesystem::temp_directory_path() / "ifcopenshell_lazy_fallback_test.ifc";
    {
        std::ofstream out(path);
        // A stray keyword between instances: the shared header loop slides past it.
        std::string spf(reference_resolution_spf);
        spf.replace(spf.find("#8=IFCWALL"), 0, "STRAY;\n");
        out << spf;
    }
    check_lazy_matches_strict(path.string());
    {
        std::ofstream out(path);
        // A semicolon inside an attribute list is not something the index pass tracks; the full parser takes over.
        std::string spf(reference_resolution_spf);
        spf.replace(spf.find("(#1,#2,#3)"), 10, "(#1;#2,#3)");
        out << spf;
    }
    ifcopenshell::file lazy(ifcopenshell::uninitialized_tag{});
    lazy.lazy_loading(true);
    lazy.initialize(path.string());
    std::filesystem::remove(path);
    CHECK_FALSE(lazy.lazy_loading());
    CHECK(lazy.instance_by_id(8));
}

TEST_CASE("Parallel and paged parsing yield the same instances, attributes, inverses and GlobalIds as serial in-memory parsing, comments in DATA included", "[ifcparse]") {
    // The fixture is small, so the threshold would keep it serial; write a
    // file big enough to be chunked by repeating its DATA section under new
    // names, with a comment and a string holding '/*' between the copies.
    const std::string fixture = std::string(IFCOPENSHELL_TEST_FIXTURES) + "/ColumnPSetsOfSets.ifc";
    std::string source;
    {
        std::ifstream in(fixture, std::ios::binary);
        source.assign(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
    }
    const size_t data_begin = source.find("\nDATA;") + 6;
    const size_t data_end = source.find("\nENDSEC", data_begin);
    const std::string data = source.substr(data_begin, data_end - data_begin);
    // Renumber "#N" to "#N+offset" per copy; every name and reference is offset consistently.
    const auto renumber = [](const std::string& block, uint32_t offset) {
        std::string out;
        out.reserve(block.size() + block.size() / 4);
        for (size_t i = 0; i < block.size(); ++i) {
            if (block[i] == '#' && i + 1 < block.size() && isdigit((unsigned char)block[i + 1])) {
                size_t j = i + 1;
                uint32_t name = 0;
                while (j < block.size() && isdigit((unsigned char)block[j])) {
                    name = name * 10 + (uint32_t)(block[j++] - '0');
                }
                out += "#" + std::to_string(name + offset);
                i = j - 1;
            } else {
                out += block[i];
            }
        }
        return out;
    };
    std::string big = source.substr(0, data_begin);
    uint32_t offset = 0;
    while (big.size() < (12u << 20)) {
        big += renumber(data, offset);
        big += "\n/* a comment between instances\n#1=NOT AN INSTANCE\n*/\n#" + std::to_string(offset + 999999) + "=IFCLABEL('/* not a comment');\n";
        offset += 1000000;
    }
    big += source.substr(data_end);
    const auto path = std::filesystem::temp_directory_path() / "ifcopenshell_parallel_parse_test.ifc";
    {
        std::ofstream out(path, std::ios::binary);
        out << big;
    }

    ifcopenshell::file serial(ifcopenshell::uninitialized_tag{});
    serial.parse_threads(1);
    REQUIRE(serial.initialize(path.string()));
    ifcopenshell::file parallel(ifcopenshell::uninitialized_tag{});
    parallel.parse_threads(5);
    REQUIRE(parallel.initialize(path.string()));
    // The same file through the paged reader, serially and with 5 workers,
    // each with its own page cache.
    ifcopenshell::file paged(ifcopenshell::uninitialized_tag{});
    paged.paged_reading(true);
    paged.parse_threads(1);
    REQUIRE(paged.initialize(path.string()));
    ifcopenshell::file paged_parallel(ifcopenshell::uninitialized_tag{});
    paged_parallel.paged_reading(true);
    paged_parallel.parse_threads(5);
    REQUIRE(paged_parallel.initialize(path.string()));
    // And the lazy index built by 5 workers.
    ifcopenshell::file lazy_parallel(ifcopenshell::uninitialized_tag{});
    lazy_parallel.lazy_loading(true);
    lazy_parallel.parse_threads(5);
    REQUIRE(lazy_parallel.initialize(path.string()));
    REQUIRE(lazy_parallel.lazy_loading());
    std::filesystem::remove(path);

    size_t count = 0;
    for (auto it = serial.begin(); it != serial.end(); ++it) {
        const express::base a = it->second;
        const express::base b = parallel.instance_by_id((int)a.id());
        REQUIRE(b);
        REQUIRE(&b.declaration() == &a.declaration());
        REQUIRE(parallel.instances_by_reference((int)a.id()).size() == serial.instances_by_reference((int)a.id()).size());
        std::ostringstream sa, sb;
        a.to_string(sa);
        b.to_string(sb);
        REQUIRE(sb.str() == sa.str());
        for (ifcopenshell::file* other : {&paged, &paged_parallel, &lazy_parallel}) {
            const express::base c = other->instance_by_id((int)a.id());
            REQUIRE(c);
            std::ostringstream sc;
            c.to_string(sc);
            REQUIRE(sc.str() == sa.str());
            REQUIRE(other->instances_by_reference((int)a.id()).size() == serial.instances_by_reference((int)a.id()).size());
        }
        ++count;
    }
    size_t parallel_count = 0;
    for (auto it = parallel.begin(); it != parallel.end(); ++it) {
        ++parallel_count;
    }
    CHECK(parallel_count == count);
    CHECK(count > 5000);
    CHECK(parallel.get_max_id() == serial.get_max_id());
    for (const auto& rooted : serial.instances_by_type("IfcRoot")) {
        const std::string guid = rooted.get_attribute_value(0);
        REQUIRE(parallel.instance_by_guid(guid).id() == serial.instance_by_guid(guid).id());
        REQUIRE(lazy_parallel.instance_by_guid(guid).id() == serial.instance_by_guid(guid).id());
    }
}
