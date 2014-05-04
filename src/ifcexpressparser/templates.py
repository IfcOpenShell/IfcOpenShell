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
#include <map>

#include <boost/optional.hpp>

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/%(schema_name)senum.h"

#define IfcSchema %(schema_name)s

namespace %(schema_name)s {

// Forward definitions
%(forward_definitions)s

%(declarations)s

%(class_definitions)s
void InitStringMap();
IfcUtil::IfcBaseClass* SchemaEntity(IfcAbstractEntity* e = 0);
}

#endif
"""

enum_header = """
#ifndef %(schema_name_upper)sENUM_H
#define %(schema_name_upper)sENUM_H

#define IfcSchema %(schema_name)s

namespace %(schema_name)s {

namespace Type {
    typedef enum {
        %(types)s, ALL
    } Enum;
    Enum Parent(Enum v);
    Enum FromString(const std::string& s);
    std::string ToString(Enum v);
    bool IsSimple(Enum v);
}

}

#endif
"""

implementation= """
#include "../ifcparse/%(schema_name)s.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcWritableEntity.h"

using namespace %(schema_name)s;
using namespace IfcParse;
using namespace IfcWrite;

IfcUtil::IfcBaseClass* %(schema_name)s::SchemaEntity(IfcAbstractEntity* e) {
    switch(e->type()) {
%(schema_entity_statements)s
        default: throw IfcException("Unable to find find keyword in schema"); break;
    }
}

std::string Type::ToString(Enum v) {
    if (v < 0 || v >= %(max_id)d) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { %(type_name_strings)s };
    return names[v];
}

static std::map<std::string,Type::Enum> string_map;
void %(schema_name)s::InitStringMap() {
%(string_map_statements)s
}

Type::Enum Type::FromString(const std::string& s) {
    std::map<std::string,Type::Enum>::const_iterator it = string_map.find(s);
    if ( it == string_map.end() ) throw IfcException("Unable to find find keyword in schema");
    else return it->second;
}

Type::Enum Type::Parent(Enum v){
    if (v < 0 || v >= %(max_id)d) return (Enum)-1;
%(parent_type_statements)s
    return (Enum)-1;
}

bool Type::IsSimple(Enum v) {
    return %(simple_type_statement)s;
}

%(enumeration_functions)s

%(entity_implementations)s
"""

simpletype = """%(documentation)s
typedef %(type)s %(name)s;
"""

select = """%(documentation)s
typedef IfcUtil::IfcBaseClass* %(name)s;
"""

enumeration = """namespace %(name)s {
%(documentation)s
typedef enum {%(values)s} %(name)s;
const char* ToString(%(name)s v);
%(name)s FromString(const std::string& s);
}
"""

entity = """%(documentation)s
class %(name)s %(superclass)s{
public:
%(attributes)s    virtual unsigned int getArgumentCount() const { return %(argument_count)d; }
    virtual IfcUtil::ArgumentType getArgumentType(unsigned int i) const {%(argument_type_function_body)s}
    virtual const char* getArgumentName(unsigned int i) const {%(argument_name_function_body)s}
    virtual Argument* getArgument(unsigned int i) const { return entity->getArgument(i); }
%(inverse)s    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    %(name)s (IfcAbstractEntity* e);
    %(name)s (%(constructor_arguments)s);
    typedef IfcTemplatedEntityList< %(name)s > list;
};
"""

enumeration_function="""
const char* %(name)s::ToString(%(name)s v) {
    if ( v < 0 || v >= %(max_id)d ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { %(values)s };
    return names[v];
}

%(name)s::%(name)s %(name)s::FromString(const std::string& s) {
%(from_string_statements)s
    throw IfcException("Unable to find find keyword in schema");
}
"""

entity_implementation = """// Function implementations for %(name)s
%(attributes)s%(inverse)sbool %(name)s::is(Type::Enum v) const { return v == Type::%(name)s%(parent_type_test)s; }
Type::Enum %(name)s::type() const { return Type::%(name)s; }
Type::Enum %(name)s::Class() { return Type::%(name)s; }
%(name)s::%(name)s(IfcAbstractEntity* e) : %(superclass)s { if (!e) return; if (!e->is(Type::%(name)s)) throw IfcException("Unable to find find keyword in schema"); entity = e; }
%(name)s::%(name)s(%(constructor_arguments)s) : %(superclass)s { IfcWritableEntity* e = new IfcWritableEntity(Class());%(constructor_implementation)s entity = e; EntityBuffer::Add(this); }
"""

optional_attribute_description = "/// Whether the optional attribute %s is defined for this %s"

function = "%(return_type)s %(class_name)s::%(name)s(%(arguments)s) { %(body)s }"
const_function = "%(return_type)s %(class_name)s::%(name)s(%(arguments)s) const { %(body)s }"

array_type = "std::vector< %(instance_type)s > /*[%(lower)s:%(upper)s]*/"
list_type = "IfcTemplatedEntityList< %(instance_type)s >::ptr"
list_list_type = "IfcTemplatedEntityListList< %(instance_type)s >::ptr"
untyped_list = "IfcEntityList::ptr"
inverse_attr = "IfcTemplatedEntityList< %(entity)s >::ptr %(name)s() const; // INVERSE %(entity)s::%(attribute)s"

enum_from_string_stmt = '    if (s == "%(value)s") return ::%(schema_name)s::%(name)s::%(short_name)s_%(value)s;'

schema_entity_stmt = '        case Type::%(name)s: return new %(name)s(e); break;'
schema_simple_stmt = '        case Type::%(name)s: return new IfcUtil::IfcEntitySelect(e); break;'
string_map_statement = '    string_map["%(uppercase_name)s"%(padding)s] = Type::%(name)s;'
parent_type_stmt = '    if(v==%(name)s%(padding)s) { return %(parent)s; }'

parent_type_test = " || %s::is(v)"

optional_attr_stmt = "return !entity->getArgument(%(index)d)->isNull();"

get_attr_stmt = "return *entity->getArgument(%(index)d);"
get_attr_stmt_enum = "return %(type)s::FromString(*entity->getArgument(%(index)d));"
get_attr_stmt_entity = "return (%(type)s)((IfcUtil::IfcBaseClass*)(*entity->getArgument(%(index)d)));"
get_attr_stmt_array = "IfcEntityList::ptr es = *entity->getArgument(%(index)d); return es->as<%(list_instance_type)s>();"
get_attr_stmt_nested_array = "IfcEntityListList::ptr es = *entity->getArgument(%(index)d); return es->as<%(list_instance_type)s>();"

get_inverse = "return entity->getInverse(Type::%(type)s)->as<%(type)s>();"

set_attr_stmt = "if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%(index)d,v);"
set_attr_stmt_enum = "if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%(index)d,v,%(type)s::ToString(v));"
set_attr_stmt_array = "if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%(index)d,v->generalize());"

constructor_stmt = " e->setArgument(%(index)d,(%(name)s));"
constructor_stmt_enum = " e->setArgument(%(index)d,%(name)s,%(type)s::ToString(%(name)s));"
constructor_stmt_array = " e->setArgument(%(index)d,(%(name)s)->generalize());"
constructor_stmt_optional = " if (%(name)s) {%(stmt)s } else { e->setArgument(%(index)d); }"
constructor_stmt_derived = " e->setArgumentDerived(%(index)d);"

def multi_line_comment(li):
    return ("/// %s"%("\n/// ".join(li))) if len(li) else ""

