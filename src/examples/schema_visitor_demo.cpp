// This file was generated with the assistance of an AI coding tool.

// Prototype / demonstration for IfcOpenShell/IfcOpenShell#1333
// ("Template programming for schema independent code").
//
// Unlike the other examples in this directory, this file is NOT compiled
// once per schema via the `-DIfcSchema=IfcNNN` build-system trick (see
// ../ifcgeom/mapping/CMakeLists.txt for that pattern). It is compiled ONCE
// and, in that single binary, can open an .ifc file of *any* schema and
// dispatch generically to the right per-schema C++ type at runtime - which
// is what the issue actually asked for.
//
// See schema_visitor.h for the generic apply_visitor() implementation and
// commentary on why it works, and the PR/commit message on branch
// concept-1333-schema-visitor for the write-up of what already existed in
// the codebase versus what is new here.

#include "../ifcparse/IfcFile.h"
#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/Ifc4.h"
#include "../ifcparse/Ifc4x3_add2.h"
#include "schema_visitor.h"

#include <iostream>
#include <string>
#include <type_traits>

// One line, written once, reusable for apply_visitor<..., IfcSpace_selector>
// with any schema list - this is the piece the original issue reporter said
// they had not found a way to make generic across entity classes.
IFC_SCHEMA_CLASS(IfcSpace);

using AllSchemas = schema_visitor::schema_list<Ifc2x3, Ifc4, Ifc4x3_add2>;

namespace {

// A single call site, compiled exactly once, used below for files of any of
// the three schemas in AllSchemas. No per-schema branching is visible here.
void print_space(IfcUtil::IfcBaseClass* inst) {
    bool matched = schema_visitor::apply_visitor<AllSchemas, IfcSpace_selector>(inst, [](auto* space) {
        // `space` is Ifc2x3::IfcSpace*, Ifc4::IfcSpace* or
        // Ifc4x3_add2::IfcSpace*, depending on which schema this file
        // turned out to be. GlobalId()/Name() have an identical signature
        // on IfcRoot in every schema, so this generic lambda body is
        // literally shared, unmodified, across all three schemas.
        std::cout << "  " << space->GlobalId() << ": "
                  << (space->Name() ? *space->Name() : std::string("<no name>")) << "\n";

        // Divergence *does* exist below IfcRoot, and no amount of generic
        // programming makes that go away: IFC2X3's IfcSpace has a required
        // InteriorOrExteriorSpace enum attribute that IFC4 replaced with an
        // optional PredefinedType. Those are genuinely different members on
        // genuinely different, unrelated C++ types. `if constexpr`, keyed
        // on the now-concrete type, is the honest way to keep this in one
        // generic lambda body instead of one bespoke dispatch chain per
        // attribute:
        using T = std::remove_pointer_t<decltype(space)>;
        if constexpr (std::is_same_v<T, Ifc2x3::IfcSpace>) {
            std::cout << "    (2X3-only attribute) InteriorOrExteriorSpace\n";
        } else {
            std::cout << "    (IFC4+ attribute) PredefinedType is "
                      << (space->PredefinedType() ? "set" : "not set") << "\n";
        }
    });

    if (!matched) {
        std::cout << "  (not an IfcSpace in any schema tried)\n";
    }
}

void run(const std::string& path) {
    std::cout << "Opening " << path << "\n";
    IfcParse::IfcFile file(path);
    if (!file.good()) {
        std::cerr << "  failed to parse " << path << "\n";
        return;
    }
    std::cout << "  schema: " << file.schema()->name() << "\n";

    // Runtime, string-keyed lookup - this part of IfcOpenShell already knows
    // how to fetch "all instances of a class" without the caller knowing
    // the schema at compile time. What it does *not* give you is a
    // strongly-typed pointer to operate on; that's what apply_visitor adds.
    auto spaces = file.instances_by_type("IfcSpace");
    if (spaces) {
        for (auto it = spaces->begin(); it != spaces->end(); ++it) {
            print_space(*it);
        }
    }
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " <file.ifc> [<file2.ifc> ...]\n";
        return 1;
    }
    for (int i = 1; i < argc; ++i) {
        run(argv[i]);
    }
    return 0;
}
