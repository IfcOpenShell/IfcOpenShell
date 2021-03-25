###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

header = """
#ifndef %(schema_name_upper)s_H
#define %(schema_name_upper)s_H

#include <string>
#include <vector>

#include <boost/optional.hpp>

#include "../ifcparse/ifc_parse_api.h"

#include "../ifcparse/IfcEntityList.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/Argument.h"

struct %(schema_name)s {

static const IfcParse::schema_definition& get_schema();

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
#include "../ifcparse/IfcWrite.h"

#include <map>

const char* const %(schema_name)s::Identifier = "%(schema_name_upper)s";

using namespace IfcParse;
using namespace IfcWrite;

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
class IFC_PARSE_API %(name)s : public %(superclass)s {
public:
    virtual const IfcParse::type_declaration& declaration() const;
    static const IfcParse::type_declaration& Class();
    explicit %(name)s (IfcEntityInstanceData* e);
    %(name)s (%(type)s v);
    operator %(type)s() const;
};
"""

simpletype_impl_comment = "// Function implementations for %(name)s"
simpletype_impl_argument_type = 'if (i == 0) { return %(attr_type)s; } else { throw IfcParse::IfcAttributeOutOfRangeException("Argument index out of range"); }'
simpletype_impl_argument = "return data_->getArgument(i);"
simpletype_impl_is_with_supertype = "return v == %(class_name)s_type || %(superclass)s::is(v);"
simpletype_impl_is_without_supertype = "return v == %(class_name)s_type;"
simpletype_impl_type = "return *%(schema_name_upper)s_%(class_name)s_type;"
simpletype_impl_class = "return *%(schema_name_upper)s_%(class_name)s_type;"
simpletype_impl_explicit_constructor = "data_ = e;"
simpletype_impl_constructor = (
    "data_ = new IfcEntityInstanceData(%(schema_name_upper)s_%(class_name)s_type); {IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(v"
    + "); data_->setArgument(0, attr);}"
)
simpletype_impl_constructor_templated = "data_ = new IfcEntityInstanceData(%(schema_name_upper)s_%(class_name)s_type); {IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(v->generalize()); data_->setArgument(0, attr);}"
simpletype_impl_cast = "return *data_->getArgument(0);"
simpletype_impl_cast_templated = (
    "IfcEntityList::ptr es = *data_->getArgument(0); return es->as< %(underlying_type)s >();"
)
simpletype_impl_declaration = "return *%(schema_name_upper)s_%(class_name)s_type;"

select = """%(documentation)s
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
    %(name)s (IfcEntityInstanceData* e);
    %(name)s (Value v);
    %(name)s (const std::string& v);
    operator Value() const;
};
"""

entity = """%(documentation)s
class IFC_PARSE_API %(name)s %(superclass)s{
public:
%(attributes)s    %(inverse)s    virtual const IfcParse::entity& declaration() const;
    static const IfcParse::entity& Class();
    %(name)s (IfcEntityInstanceData* e);
    %(name)s (%(constructor_arguments)s);
    typedef IfcTemplatedEntityList< %(name)s > list;
};
"""

enumeration_function = """
const IfcParse::enumeration_type& %(schema_name)s::%(name)s::declaration() const { return *%(schema_name_upper)s_%(name)s_type; }
const IfcParse::enumeration_type& %(schema_name)s::%(name)s::Class() { return *%(schema_name_upper)s_%(name)s_type; }

%(schema_name)s::%(name)s::%(name)s(IfcEntityInstanceData* e) {
    data_ = e;
}

%(schema_name)s::%(name)s::%(name)s(Value v) {
    IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();
    attr->set(IfcWrite::IfcWriteArgument::EnumerationReference(v,ToString(v)));
    data_->setArgument(0,attr);
}

%(schema_name)s::%(name)s::%(name)s(const std::string& v) {
    IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();
    attr->set(IfcWrite::IfcWriteArgument::EnumerationReference(FromString(v),ToString(FromString(v))));
    data_->setArgument(0,attr);
}

const char* %(schema_name)s::%(name)s::ToString(Value v) {
    if ( v < 0 || v >= %(max_id)d ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { %(values)s };
    return names[v];
}

%(schema_name)s::%(name)s::Value %(schema_name)s::%(name)s::FromString(const std::string& s) {
%(from_string_statements)s
    throw IfcException("Unable to find find keyword in schema");
}
"""

entity_implementation = """// Function implementations for %(name)s
%(attributes)s
%(inverse)s
const IfcParse::entity& %(schema_name)s::%(name)s::declaration() const { return *%(schema_name_upper)s_%(name)s_type; }
const IfcParse::entity& %(schema_name)s::%(name)s::Class() { return *%(schema_name_upper)s_%(name)s_type; }
%(schema_name)s::%(name)s::%(name)s(IfcEntityInstanceData* e) : %(superclass)s { if (!e) return; if (e->type() != %(schema_name_upper)s_%(name)s_type) throw IfcException("Unable to find find keyword in schema"); data_ = e; }
%(schema_name)s::%(name)s::%(name)s(%(constructor_arguments)s) : %(superclass)s {data_ = new IfcEntityInstanceData(%(schema_name_upper)s_%(name)s_type); %(constructor_implementation)s }
"""

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
list_type = "IfcTemplatedEntityList< %(instance_type)s >::ptr"
list_list_type = "IfcTemplatedEntityListList< %(instance_type)s >::ptr"
untyped_list = "IfcEntityList::ptr"
inverse_attr = "IfcTemplatedEntityList< %(entity)s >::ptr %(name)s() const; // INVERSE %(entity)s::%(attribute)s"

enum_from_string_stmt = '    if (s == "%(value)s") return ::%(schema_name)s::%(name)s::%(short_name)s_%(value)s;'

schema_entity_stmt = "        case Type::%(name)s: return new %(name)s(e); break;"
string_map_statement = '    string_map["%(uppercase_name)s"%(padding)s] = Type::%(name)s;'
parent_type_stmt = "    if(v==%(name)s%(padding)s) { return %(parent)s; }"

parent_type_test = " || %s::is(v)"

optional_attr_stmt = "return !data_->getArgument(%(index)d)->isNull();"

get_attr_stmt = "return *data_->getArgument(%(index)d);"
get_attr_stmt_enum = "return %(type)s::FromString(*data_->getArgument(%(index)d));"
get_attr_stmt_entity = "return (%(type)s)((IfcUtil::IfcBaseClass*)(*data_->getArgument(%(index)d)));"
get_attr_stmt_array = (
    "IfcEntityList::ptr es = *data_->getArgument(%(index)d); return es->as< %(list_instance_type)s >();"
)
get_attr_stmt_nested_array = (
    "IfcEntityListList::ptr es = *data_->getArgument(%(index)d); return es->as< %(list_instance_type)s >();"
)

get_inverse = "return data_->getInverse(%(schema_name_upper)s_%(type)s_type, %(index)d)->as<%(type)s>();"

set_attr_stmt = (
    "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(v"
    + ");data_->setArgument(%(index)d,attr);}"
)
set_attr_stmt_enum = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(IfcWrite::IfcWriteArgument::EnumerationReference(v,%(type)s::ToString(v)));data_->setArgument(%(index)d,attr);}"
set_attr_stmt_array = (
    "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(v->generalize()"
    + ");data_->setArgument(%(index)d,attr);}"
)

constructor_stmt = (
    "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set((%(name)s)"
    + ");data_->setArgument(%(index)d,attr);}"
)
constructor_stmt_enum = (
    "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set((IfcWrite::IfcWriteArgument::EnumerationReference(%(name)s,%(type)s::ToString(%(name)s)))"
    + ");data_->setArgument(%(index)d,attr);}"
)
constructor_stmt_array = (
    "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set((%(name)s)->generalize()"
    + ");data_->setArgument(%(index)d,attr);}"
)
constructor_stmt_derived = (
    "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(IfcWrite::IfcWriteArgument::Derived()"
    + ");data_->setArgument(%(index)d,attr);}"
)

constructor_stmt_optional = " if (%(name)s) {%(stmt)s } else { IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(boost::blank()); data_->setArgument(%(index)d, attr); }"

inverse_implementation = '    inverse_map[Type::%(type)s].insert(std::make_pair("%(name)s", std::make_pair(Type::%(related_type)s, %(index)d)));'


def multi_line_comment(li):
    return ("/// %s" % ("\n/// ".join(li))) if len(li) else ""
