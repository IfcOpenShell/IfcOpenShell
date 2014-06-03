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
IfcUtil::IfcSchemaEntity SchemaEntity(IfcAbstractEntityPtr e = 0);
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

rt_header = """
#ifndef %(schema_name_upper)sRT_H
#define %(schema_name_upper)sRT_H

#define IfcSchema %(schema_name)s

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcEntityDescriptor.h"
#include "../ifcparse/IfcWritableEntity.h"

namespace %(schema_name)s {
namespace Type {
    int GetAttributeCount(Enum t);
    int GetAttributeIndex(Enum t, const std::string& a);
    IfcUtil::ArgumentType GetAttributeType(Enum t, unsigned char a);
    const std::string& GetAttributeName(Enum t, unsigned char a);
    bool GetAttributeOptional(Enum t, unsigned char a);
    std::pair<const char*, int> GetEnumerationIndex(Enum t, const std::string& a);
    std::pair<Enum, unsigned> GetInverseAttribute(Enum t, const std::string& a);
    Enum GetAttributeEnumerationClass(Enum t, unsigned char a);
    void PopulateDerivedFields(IfcWrite::IfcWritableEntity* e);
}}

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

IfcUtil::IfcSchemaEntity %(schema_name)s::SchemaEntity(IfcAbstractEntityPtr e) {
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
    if (string_map.empty()) InitStringMap();
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

#define RETURN_INVERSE(T) \
    IfcEntities e = entity->getInverse(T::Class()); \
    SHARED_PTR< IfcTemplatedEntityList<T> > l ( new IfcTemplatedEntityList<T>() ); \
    for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) { \
        l->push(reinterpret_pointer_cast<IfcBaseClass,T>(*it)); \
    } \
    return l;

#define RETURN_AS_SINGLE(T,a) \
    return reinterpret_pointer_cast<IfcBaseClass,T>(*entity->getArgument(a));

#define RETURN_AS_LIST(T,a)  \
    IfcEntities e = *entity->getArgument(a);  \
    SHARED_PTR< IfcTemplatedEntityList<T> > l ( new IfcTemplatedEntityList<T>() );  \
    for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) {  \
        l->push(reinterpret_pointer_cast<IfcBaseClass,T>(*it)); \
    }  \
    return l;

%(entity_implementations)s
"""

rt_implementation = """
#include "../ifcparse/%(schema_name)s.h"
#include "../ifcparse/%(schema_name)s-rt.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcWritableEntity.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcEntityDescriptor.h"

using namespace %(schema_name)s;
using namespace IfcParse;
using namespace IfcWrite;
using namespace IfcUtil;

std::map<Type::Enum,IfcEntityDescriptor*> entity_descriptor_map;
std::map<Type::Enum,IfcEnumerationDescriptor*> enumeration_descriptor_map;
std::map<std::pair<Type::Enum, std::string>, std::pair<Type::Enum, int> > inverse_map;
void InitDescriptorMap() {
    IfcEntityDescriptor* current;
%(entity_descriptors)s
    // Enumerations
    IfcEnumerationDescriptor* current_enum;
    std::vector<std::string> values;
%(enumeration_descriptors)s
}

void InitInverseMap() {
%(inverse_implementations)s
}

int Type::GetAttributeIndex(Enum t, const std::string& a) {
    if (entity_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEntityDescriptor*>::const_iterator i = entity_descriptor_map.find(t);
    if ( i == entity_descriptor_map.end() ) throw IfcException("Type not found");
    else return i->second->getArgumentIndex(a);
}

int Type::GetAttributeCount(Enum t) {
    if (entity_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEntityDescriptor*>::const_iterator i = entity_descriptor_map.find(t);
    if ( i == entity_descriptor_map.end() ) throw IfcException("Type not found");
    else return i->second->getArgumentCount();
}

ArgumentType Type::GetAttributeType(Enum t, unsigned char a) {
    if (entity_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEntityDescriptor*>::const_iterator i = entity_descriptor_map.find(t);
    if ( i == entity_descriptor_map.end() ) throw IfcException("Type not found");
    else return i->second->getArgumentType(a);
}

const std::string& Type::GetAttributeName(Enum t, unsigned char a) {
    if (entity_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEntityDescriptor*>::const_iterator i = entity_descriptor_map.find(t);
    if ( i == entity_descriptor_map.end() ) throw IfcException("Type not found");
    else return i->second->getArgumentName(a);
}

bool Type::GetAttributeOptional(Enum t, unsigned char a) {
    if (entity_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEntityDescriptor*>::const_iterator i = entity_descriptor_map.find(t);
    if ( i == entity_descriptor_map.end() ) throw IfcException("Type not found");
    else return i->second->getArgumentOptional(a);
}

std::pair<const char*, int> Type::GetEnumerationIndex(Enum t, const std::string& a) {
    if (enumeration_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEnumerationDescriptor*>::const_iterator i = enumeration_descriptor_map.find(t);
    if ( i == enumeration_descriptor_map.end() ) throw IfcException("Value not found");
    else return i->second->getIndex(a);
}

std::pair<Type::Enum, unsigned> Type::GetInverseAttribute(Enum t, const std::string& a) {
	if (inverse_map.empty()) ::InitInverseMap();
	std::map<std::pair<Type::Enum, std::string>, std::pair<Type::Enum, int> >::const_iterator it;
    std::pair<Type::Enum, std::string> key = std::make_pair(t, a);
    while (true) {
        it = inverse_map.find(key);
        if (it != inverse_map.end()) return it->second;
        if ((key.first = Parent(key.first)) == -1) break;
    }
    throw IfcException("Attribute not found");
}

Type::Enum Type::GetAttributeEnumerationClass(Enum t, unsigned char a) {
    if (entity_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEntityDescriptor*>::const_iterator i = entity_descriptor_map.find(t);
    if ( i == entity_descriptor_map.end() ) throw IfcException("Type not found");
    else {
        Type::Enum t = i->second->getArgumentEnumerationClass(a);
        if ( t == Type::ALL ) throw IfcException("Not an enumeration");
        else return t;
    }
}

void Type::PopulateDerivedFields(IfcWrite::IfcWritableEntity* e) {
    Type::Enum type = e->type();
%(derived_field_statements)s
}
"""

entity_descriptor = """    current = entity_descriptor_map[Type::%(type)s] = new IfcEntityDescriptor(Type::%(type)s,%(parent_statement)s);
%(entity_descriptor_attributes)s"""

entity_descriptor_parent = "entity_descriptor_map.find(Type::%(type)s)->second"
entity_descriptor_attribute = '    current->add("%(name)s",%(optional)s,%(type)s);'
entity_descriptor_attribute_enum = '    current->add("%(name)s",%(optional)s,%(type)s,Type::%(enum_type)s);'

enumeration_descriptor = """    values.clear(); values.reserve(128);
%(enumeration_descriptor_values)s
    current_enum = enumeration_descriptor_map[Type::%(type)s] = new IfcEnumerationDescriptor(Type::%(type)s, values);"""

enumeration_descriptor_value = '    values.push_back("%(name)s");'

derived_field_statement = '    if (type == Type::%(type)s) { %(statements)s}';
derived_field_statement_attrs = 'e->setArgumentDerived(%d); '

simpletype = """%(documentation)s
typedef %(type)s %(name)s;
"""

select = """%(documentation)s
typedef IfcUtil::IfcSchemaEntity %(name)s;
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
    virtual ArgumentPtr getArgument(unsigned int i) const { return entity->getArgument(i); }
%(inverse)s    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    %(name)s (IfcAbstractEntityPtr e);
    %(name)s (%(constructor_arguments)s);
    typedef %(name)s* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList< %(name)s > > list;
    typedef IfcTemplatedEntityList< %(name)s >::it it;
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
%(name)s::%(name)s(IfcAbstractEntityPtr e) : %(superclass)s { if (!e) return; if (!e->is(Type::%(name)s)) throw IfcException("Unable to find find keyword in schema"); entity = e; }
%(name)s::%(name)s(%(constructor_arguments)s) : %(superclass)s { IfcWritableEntity* e = new IfcWritableEntity(Class());%(constructor_implementation)s entity = e; EntityBuffer::Add(this); }
"""

optional_attribute_description = "/// Whether the optional attribute %s is defined for this %s"

function = "%(return_type)s %(class_name)s::%(name)s(%(arguments)s) { %(body)s }"

array_type = "std::vector< %(instance_type)s > /*[%(lower)s:%(upper)s]*/"
list_type = "SHARED_PTR< IfcTemplatedEntityList< %(instance_type)s > >"
untyped_list = "IfcEntities"
inverse_attr = "SHARED_PTR< IfcTemplatedEntityList< %(entity)s > > %(name)s(); // INVERSE %(entity)s::%(attribute)s"

enum_from_string_stmt = '    if (s == "%(value)s") return ::%(schema_name)s::%(name)s::%(short_name)s_%(value)s;'

schema_entity_stmt = '        case Type::%(name)s: return new %(name)s(e); break;'
schema_simple_stmt = '        case Type::%(name)s: return new IfcUtil::IfcEntitySelect(e); break;'
string_map_statement = '    string_map["%(uppercase_name)s"%(padding)s] = Type::%(name)s;'
parent_type_stmt = '    if(v==%(name)s%(padding)s) { return %(parent)s; }'

parent_type_test = " || %s::is(v)"

optional_attr_stmt = "return !entity->getArgument(%(index)d)->isNull();"

get_attr_stmt = "return *entity->getArgument(%(index)d);"
get_attr_stmt_enum = "return %(type)s::FromString(*entity->getArgument(%(index)d));"
get_attr_stmt_entity = "return (%(type)s)((IfcUtil::IfcSchemaEntity)(*entity->getArgument(%(index)d)));"
get_attr_stmt_array = "RETURN_AS_LIST(%(list_instance_type)s,%(index)d)"

get_inverse = "RETURN_INVERSE(%(type)s)"

set_attr_stmt = "if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%(index)d,v);"
set_attr_stmt_enum = "if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%(index)d,v,%(type)s::ToString(v));"
set_attr_stmt_array = "if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%(index)d,v->generalize());"

constructor_stmt = " e->setArgument(%(index)d,(%(name)s));"
constructor_stmt_enum = " e->setArgument(%(index)d,%(name)s,%(type)s::ToString(%(name)s));"
constructor_stmt_array = " e->setArgument(%(index)d,(%(name)s)->generalize());"
constructor_stmt_optional = " if (%(name)s) {%(stmt)s } else { e->setArgument(%(index)d); }"
constructor_stmt_derived = " e->setArgumentDerived(%(index)d);"

inverse_implementation = "    inverse_map.insert(std::make_pair(std::make_pair(Type::%(type)s, \"%(name)s\"), std::make_pair(Type::%(related_type)s, %(index)d)));"

def multi_line_comment(li):
    return ("/// %s"%("\n/// ".join(li))) if len(li) else ""

