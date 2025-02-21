# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


header = """
#ifndef %(schema_name_upper)s_H
#define %(schema_name_upper)s_H

#include <string>
#include <vector>

#include <boost/optional.hpp>

#include "../ifcparse/ifc_parse_api.h"

#include "../ifcparse/aggregate_of_instance.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/Argument.h"

struct %(schema_name)s {

IFC_PARSE_API static const IfcParse::schema_definition& get_schema();

IFC_PARSE_API static void clear_schema();

static const char* const Identifier;

// Forward definitions
%(forward_definitions)s

%(declarations)s

%(class_definitions)s
};

#endif
"""

enum_header = """
#ifndef %(schema_name_upper)sENUM_H
#define %(schema_name_upper)sENUM_H

#include "../ifcparse/ifc_parse_api.h"

#include <string>
#include <boost/optional.hpp>

#endif
"""

lb_header = """"""

implementation = """
#include "../ifcparse/%(schema_name)s.h"
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcFile.h"

#include <map>

const char* const %(schema_name)s::Identifier = "%(schema_name_upper)s";

using namespace IfcParse;

// External definitions
%(external_definitions)s

%(enumeration_functions)s

%(simple_type_impl)s

%(entity_implementations)s
"""

lb_implementation = """"""

entity_descriptor = """    current = entity_descriptor_map[Type::%(type)s] = new IfcEntityDescriptor(Type::%(type)s,%(parent_statement)s);
%(entity_descriptor_attributes)s"""

entity_descriptor_parent = "entity_descriptor_map.find(Type::%(type)s)->second"
entity_descriptor_attribute_without_entity = '    current->add("%(name)s",%(optional)s,%(type)s);'
entity_descriptor_attribute_with_entity = '    current->add("%(name)s",%(optional)s,%(type)s,Type::%(entity_name)s);'

enumeration_descriptor = """    values.clear(); values.reserve(128);
%(enumeration_descriptor_values)s
    enumeration_descriptor_map[Type::%(type)s] = new IfcEnumerationDescriptor(Type::%(type)s, values);"""

enumeration_descriptor_value = '    values.push_back("%(name)s");'

derived_field_statement = "    {std::set<int> idxs; %(statements)sderived_map[Type::%(type)s] = idxs;}"
derived_field_statement_attrs = "idxs.insert(%d); "

simpletype = """%(documentation)s
class IFC_PARSE_API %(name)s : %(superclass)s {
public:
    virtual const IfcParse::type_declaration& declaration() const;
    static const IfcParse::type_declaration& Class();
    explicit %(name)s (IfcEntityInstanceData&& e);
    %(name)s (%(type)s v);
    operator %(type)s() const;
};
"""

simpletype_impl_comment = "// Function implementations for %(name)s"
simpletype_impl_argument_type = 'if (i == 0) { return %(attr_type)s; } else { throw IfcParse::IfcAttributeOutOfRangeException("Argument index out of range"); }'
simpletype_impl_argument = "return get_attribute_value(i);"
simpletype_impl_is_with_supertype = "return v == %(class_name)s_type || %(superclass)s::is(v);"
simpletype_impl_is_without_supertype = "return v == %(class_name)s_type;"
simpletype_impl_type = "return *((IfcParse::type_declaration*)%(schema_name_upper)s_types[%(index_in_schema)d]);"
simpletype_impl_class = "return *((IfcParse::type_declaration*)%(schema_name_upper)s_types[%(index_in_schema)d]);"
simpletype_impl_explicit_constructor = "data_ = e;"
simpletype_impl_constructor = (
    "data_ = new IfcEntityInstanceData(%(schema_name_upper)s_types[%(index_in_schema)d]); set_attribute_value(0, v);"
)
simpletype_impl_constructor_templated = "data_ = new IfcEntityInstanceData(%(schema_name_upper)s_types[%(index_in_schema)d]); set_attribute_value(0, v->generalize());"
simpletype_impl_cast = "return get_attribute_value(0);"
simpletype_impl_cast_templated = (
    "aggregate_of_instance::ptr es = get_attribute_value(0); return es->as< %(underlying_type)s >();"
)
simpletype_impl_declaration = "return *((IfcParse::type_declaration*)%(schema_name_upper)s_types[%(index_in_schema)d]);"

select_virtual = """%(documentation)s
class IFC_PARSE_API %(name)s : public virtual IfcUtil::IfcBaseInterface {
public:
    static const IfcParse::select_type& Class();
    typedef aggregate_of< %(name)s > list;
};
"""

select_plain = """%(documentation)s
typedef IfcUtil::IfcBaseClass %(name)s;
"""

enumeration = """class IFC_PARSE_API %(name)s : public IfcUtil::IfcBaseType {
%(documentation)s
public:
    typedef enum {%(values)s} Value;
    static const char* ToString(Value v);
    static Value FromString(const std::string& s);

    virtual const IfcParse::enumeration_type& declaration() const;
    static const IfcParse::enumeration_type& Class();
    %(name)s (IfcEntityInstanceData&& e);
    %(name)s (Value v);
    %(name)s (const std::string& v);
    operator Value() const;
};
"""

entity = """%(documentation)s
class IFC_PARSE_API %(name)s : %(superclass)s {
public:
%(attributes)s    %(inverse)s    virtual const IfcParse::entity& declaration() const;
    static const IfcParse::entity& Class();
    %(name)s (IfcEntityInstanceData&& e);
    %(name)s (%(constructor_arguments)s);
    typedef aggregate_of< %(name)s > list;
};
"""

select_function = """
const IfcParse::select_type& %(schema_name)s::%(name)s::Class() { return *((IfcParse::select_type*)%(schema_name_upper)s_types[%(index_in_schema)d]); }
"""

enumeration_function = """
const IfcParse::enumeration_type& %(schema_name)s::%(name)s::declaration() const { return *((IfcParse::enumeration_type*)%(schema_name_upper)s_types[%(index_in_schema)d]); }
const IfcParse::enumeration_type& %(schema_name)s::%(name)s::Class() { return *((IfcParse::enumeration_type*)%(schema_name_upper)s_types[%(index_in_schema)d]); }

%(schema_name)s::%(name)s::%(name)s(IfcEntityInstanceData&& e)
    : IfcBaseType(std::move(e))
{}

%(schema_name)s::%(name)s::%(name)s(Value v) {
    set_attribute_value(0, EnumerationReference(&declaration(), static_cast<size_t>(v)));
}

%(schema_name)s::%(name)s::%(name)s(const std::string& v) {
    set_attribute_value(0, EnumerationReference(&declaration(), declaration().lookup_enum_offset(v)));
}

const char* %(schema_name)s::%(name)s::ToString(Value v) {
    return %(schema_name)s::%(name)s::%(name)s::Class().lookup_enum_value((size_t)v);
}

%(schema_name)s::%(name)s::Value %(schema_name)s::%(name)s::FromString(const std::string& s) {
    return (%(schema_name)s::%(name)s::Value) %(schema_name)s::%(name)s::%(name)s::Class().lookup_enum_offset(s);
}

%(schema_name)s::%(name)s::operator %(schema_name)s::%(name)s::Value() const {
    return (%(schema_name)s::%(name)s::Value) ((EnumerationReference) get_attribute_value(0)).index();
}
"""

entity_implementation = """// Function implementations for %(name)s
%(attributes)s
%(inverse)s
const IfcParse::entity& %(schema_name)s::%(name)s::declaration() const { return *((IfcParse::entity*)%(schema_name_upper)s_types[%(index_in_schema)d]); }
const IfcParse::entity& %(schema_name)s::%(name)s::Class() { return *((IfcParse::entity*)%(schema_name_upper)s_types[%(index_in_schema)d]); }
%(schema_name)s::%(name)s::%(name)s(IfcEntityInstanceData&& e) : %(superclass)s { }
%(schema_name)s::%(name)s::%(name)s(%(constructor_arguments)s) : %(superclass_num_attrs)s { %(constructor_implementation)s; populate_derived(); }
"""

# data_ = e; 
# data_ = new IfcEntityInstanceData(%(schema_name_upper)s_types[%(index_in_schema)d]);

optional_attribute_description = "/// Whether the optional attribute %s is defined for this %s"

function = "%(return_type)s %(schema_name)s::%(class_name)s::%(name)s(%(arguments)s) { %(body)s }"
const_function = "%(return_type)s %(schema_name)s::%(class_name)s::%(name)s(%(arguments)s) const { %(body)s }"
constructor = "%(schema_name)s::%(class_name)s::%(class_name)s(%(arguments)s) { %(body)s }"
constructor_single_initlist = (
    "%(schema_name)s::%(class_name)s::%(class_name)s(%(arguments)s) : %(superclass)s(%(superclass_init)s) { %(body)s }"
)
cast_function = "%(schema_name)s::%(class_name)s::operator %(return_type)s() const { %(body)s }"

array_type = "std::vector< %(instance_type)s > /*[%(lower)s:%(upper)s]*/"
nested_array_type = "std::vector< std::vector< %(instance_type)s > >"
list_type = "aggregate_of< %(instance_type)s >::ptr"
list_list_type = "aggregate_of_aggregate_of< %(instance_type)s >::ptr"
untyped_list = "aggregate_of_instance::ptr"
inverse_attr = "aggregate_of< %(entity)s >::ptr %(name)s() const; // INVERSE %(entity)s::%(attribute)s"

enum_from_string_stmt = '    if (s == "%(value)s") return ::%(schema_name)s::%(name)s::%(short_name)s_%(value)s;'

schema_entity_stmt = "        case Type::%(name)s: return new %(name)s(e); break;"
string_map_statement = '    string_map["%(uppercase_name)s"%(padding)s] = Type::%(name)s;'
parent_type_stmt = "    if(v==%(name)s%(padding)s) { return %(parent)s; }"

parent_type_test = " || %s::is(v)"

optional_attr_stmt = "return !get_attribute_value(%(index)d).isNull();"

get_attr_stmt = "%(null_check)s %(non_optional_type)s v = get_attribute_value(%(index)d); return v;"
get_attr_stmt_enum = "%(null_check)s return %(non_optional_type)s::FromString(get_attribute_value(%(index)d));"
get_attr_stmt_entity = "%(null_check)s return ((IfcUtil::IfcBaseClass*)(get_attribute_value(%(index)d)))->as<%(non_optional_type_no_pointer)s>(true);"
get_attr_stmt_array = "%(null_check)s aggregate_of_instance::ptr es = get_attribute_value(%(index)d); return es->as< %(list_instance_type)s >();"
get_attr_stmt_nested_array = "%(null_check)s aggregate_of_aggregate_of_instance::ptr es = get_attribute_value(%(index)d); return es->as< %(list_instance_type)s >();"

get_inverse = "if (!file_) { return nullptr; } return file_->getInverse(id_, %(schema_name_upper)s_types[%(type_index)d], %(index)d)->as<%(type)s>();"

set_attr_stmt = (
    "%(check_optional_set_begin)sset_attribute_value(%(index)d, %(star_if_optional)sv);%(check_optional_set_else)sunset_attribute_value(%(index)d);%(check_optional_set_end)s"
)
set_attr_instance = (
    "%(check_optional_set_begin)sset_attribute_value(%(index)d, v->as<IfcUtil::IfcBaseClass>());%(check_optional_set_else)sunset_attribute_value(%(index)d);%(check_optional_set_end)s"
)
set_attr_stmt_enum =  "%(check_optional_set_begin)sset_attribute_value(%(index)d, EnumerationReference(&%(non_optional_type)s::Class(), (size_t) %(star_if_optional)sv));%(check_optional_set_else)sunset_attribute_value(%(index)d);%(check_optional_set_end)s"
set_attr_stmt_array = (
    "%(check_optional_set_begin)sset_attribute_value(%(index)d, (%(star_if_optional)sv)->generalize());%(check_optional_set_else)sunset_attribute_value(%(index)d);%(check_optional_set_end)s"
)

constructor_stmt = (
    "set_attribute_value(%(index)d, (%(name)s));"
)
constructor_stmt_enum = (
    "set_attribute_value(%(index)d, (EnumerationReference(&%(type)s::Class(),(size_t)%(name)s)));"
)
constructor_stmt_array = (
    "set_attribute_value(%(index)d, (%(name)s)->generalize());"
)
constructor_stmt_derived = (
    ""
)
constructor_stmt_instance = (
    "set_attribute_value(%(index)d, %(name)s ? %(name)s->as<IfcUtil::IfcBaseClass>() : (IfcUtil::IfcBaseClass*) nullptr);"
)

constructor_stmt_optional = " if (%(name)s) {%(stmt)s }"

inverse_implementation = '    inverse_map[Type::%(type)s].insert(std::make_pair("%(name)s", std::make_pair(Type::%(related_type)s, %(index)d)));'


def multi_line_comment(li):
    return ("/// %s" % ("\n/// ".join(li))) if len(li) else ""
