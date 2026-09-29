#ifndef SCHEMA_VISITOR_H
#define SCHEMA_VISITOR_H

// This file was generated with the assistance of an AI coding tool.

// Prototype for IfcOpenShell/IfcOpenShell#1333 ("Template programming for
// schema independent code"). See schema_visitor_demo.cpp for a runnable
// example against real IFC2X3 / IFC4 / IFC4X3_ADD2 files.
//
// The issue's stuck point was item (3) in the report: a hand-written
// apply_visitor() that dynamic_casts across schemas works for one entity
// class (IfcSpace), but the reporter could not find a way to reuse it
// generically for other classes without rewriting the whole if/else chain.
//
// The key fact that makes this solvable with plain C++17 (no boost::mpl)
// is that the generated per-schema "namespaces" (Ifc2x3, Ifc4, ...) are
// not namespaces at all: they are ordinary structs, and IfcSpace etc. are
// ordinary nested classes of those structs. Ordinary struct types can be
// template arguments, so a schema can be a template parameter like any
// other type.

#include "../ifcparse/IfcBaseClass.h"

#include <utility>

namespace schema_visitor {

// Compile-time list of schema "tag" types, e.g. schema_list<Ifc2x3, Ifc4>.
template <typename... Schemas>
struct schema_list {};

namespace detail {

    template <template <typename> class Selector, typename Fn>
    inline bool apply_visitor_impl(schema_list<>, IfcUtil::IfcBaseClass*, Fn&&) {
        return false;
    }

    template <template <typename> class Selector, typename Schema, typename... Rest, typename Fn>
    inline bool apply_visitor_impl(schema_list<Schema, Rest...>, IfcUtil::IfcBaseClass* inst, Fn&& fn) {
        if (auto* p = inst->as<typename Selector<Schema>::type>()) {
            std::forward<Fn>(fn)(p);
            return true;
        }
        return apply_visitor_impl<Selector>(schema_list<Rest...>{}, inst, std::forward<Fn>(fn));
    }

} // namespace detail

// Generic runtime dispatch across an arbitrary compile-time list of schemas.
//
// - SchemaList: e.g. schema_list<Ifc2x3, Ifc4, Ifc4x3_add2>
// - Selector:   a class template with a nested `::type`, naming the
//               concrete per-schema class for one entity class. Written
//               ONCE per entity class name (see IFC_SCHEMA_CLASS below),
//               then reusable for any class and any schema list - this is
//               precisely the piece the issue was missing.
// - fn:         a generic callable, invoked with the entity cast to its
//               real, schema-specific pointer type as soon as a schema
//               match is found.
//
// Returns false if `inst` does not match any schema's variant of the
// requested class (e.g. it is some unrelated entity type).
template <typename SchemaList, template <typename> class Selector, typename Fn>
inline bool apply_visitor(IfcUtil::IfcBaseClass* inst, Fn&& fn) {
    return detail::apply_visitor_impl<Selector>(SchemaList{}, inst, std::forward<Fn>(fn));
}

} // namespace schema_visitor

// Declares a reusable class selector for entity class `Name`. One line,
// independent of how many schemas exist or which ones a given call site
// wants to dispatch over.
#define IFC_SCHEMA_CLASS(Name)               \
    template <typename Schema>               \
    struct Name##_selector {                 \
        using type = typename Schema::Name;  \
    }

#endif
