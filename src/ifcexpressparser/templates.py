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
#include "../ifcparse/IfcException.h"
#include "../ifcparse/Argument.h"

#include "../ifcparse/%(schema_name)senum.h"

#define IfcSchema %(schema_name)s

namespace %(schema_name)s {

const char* const Identifier = "%(schema_name_upper)s";

// Forward definitions
%(forward_definitions)s

%(declarations)s

%(class_definitions)s
IFC_PARSE_API void InitStringMap();
IFC_PARSE_API IfcUtil::IfcBaseClass* SchemaEntity(IfcEntityInstanceData* e = 0);
}

#endif
"""

enum_header = """
#ifndef %(schema_name_upper)sENUM_H
#define %(schema_name_upper)sENUM_H

#include "../ifcparse/ifc_parse_api.h"

#include <string>
#include <boost/optional.hpp>

#define IfcSchema %(schema_name)s

namespace %(schema_name)s {

namespace Type {
    typedef enum {
        %(types)s, UNDEFINED
    } Enum;
    IFC_PARSE_API boost::optional<Enum> Parent(Enum v);
    IFC_PARSE_API Enum FromString(const std::string& s);
    IFC_PARSE_API const std::string& ToString(Enum v);
    IFC_PARSE_API bool IsSimple(Enum v);
}

}

#endif
"""

lb_header = """
#ifndef %(schema_name_upper)sRT_H
#define %(schema_name_upper)sRT_H

#define IfcSchema %(schema_name)s

#include "../ifcparse/ifc_parse_api.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcEntityDescriptor.h"

namespace %(schema_name)s {
namespace Type {
    IFC_PARSE_API int GetAttributeCount(Enum t);
    IFC_PARSE_API int GetAttributeIndex(Enum t, const std::string& a);
    IFC_PARSE_API IfcUtil::ArgumentType GetAttributeType(Enum t, unsigned char a);
    IFC_PARSE_API Enum GetAttributeEntity(Enum t, unsigned char a);
    IFC_PARSE_API const std::string& GetAttributeName(Enum t, unsigned char a);
    IFC_PARSE_API bool GetAttributeOptional(Enum t, unsigned char a);
    IFC_PARSE_API bool GetAttributeDerived(Enum t, unsigned char a);
    IFC_PARSE_API std::pair<const char*, int> GetEnumerationIndex(Enum t, const std::string& a);
    IFC_PARSE_API std::pair<Enum, unsigned> GetInverseAttribute(Enum t, const std::string& a);
    IFC_PARSE_API std::set<std::string> GetInverseAttributeNames(Enum t);
    IFC_PARSE_API void PopulateDerivedFields(IfcEntityInstanceData* e);
}}

#endif
"""

implementation= """
#include "../ifcparse/%(schema_name)s.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcWrite.h"

#include <map>

using namespace %(schema_name)s;
using namespace IfcParse;
using namespace IfcWrite;

IfcUtil::IfcBaseClass* %(schema_name)s::SchemaEntity(IfcEntityInstanceData* e) {
    switch(e->type()) {
%(schema_entity_statements)s
        default: throw IfcException("Unable to find find keyword in schema"); break;
    }
}

const std::string& Type::ToString(Enum v) {
    if (v < 0 || v >= %(max_id)d) throw IfcException("Unable to find find keyword in schema");
    static std::string names[] = { %(type_name_strings)s };
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

static int parent_map[] = {%(parent_type_statements)s};
boost::optional<Type::Enum> Type::Parent(Enum v){
    const int p = parent_map[static_cast<int>(v)];
    if (p >= 0) {
        return static_cast<Type::Enum>(p);
    } else {
        return boost::none;
    }
}

bool Type::IsSimple(Enum v) {
    return %(simple_type_statement)s;
}

%(enumeration_functions)s

%(simple_type_impl)s

%(entity_implementations)s
"""

lb_implementation = """
#include <set>

#include "../ifcparse/%(schema_name)s.h"
#include "../ifcparse/%(schema_name)s-latebound.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcEntityDescriptor.h"

using namespace %(schema_name)s;
using namespace IfcParse;
using namespace IfcWrite;
using namespace IfcUtil;

typedef std::map<Type::Enum,IfcEntityDescriptor*> entity_descriptor_map_t;
typedef std::map<Type::Enum,IfcEnumerationDescriptor*> enumeration_descriptor_map_t;
typedef std::map<Type::Enum, std::map<std::string, std::pair<Type::Enum, int> > > inverse_map_t;
typedef std::map<Type::Enum,std::set<int> > derived_map_t;

entity_descriptor_map_t entity_descriptor_map;
enumeration_descriptor_map_t enumeration_descriptor_map;
inverse_map_t inverse_map;
derived_map_t derived_map;


#ifdef _MSC_VER
#  pragma optimize( "", off )
#endif

void InitDescriptorMap() {
    IfcEntityDescriptor* current;
%(entity_descriptors)s
    // Enumerations
    std::vector<std::string> values;
%(enumeration_descriptors)s
}

#ifdef _MSC_VER
#  pragma optimize( "", on )
#endif

void InitInverseMap() {
%(inverse_implementations)s
}

void InitDerivedMap() {
%(derived_field_statements)s
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

Type::Enum Type::GetAttributeEntity(Enum t, unsigned char a) {
    if (entity_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEntityDescriptor*>::const_iterator i = entity_descriptor_map.find(t);
    if ( i == entity_descriptor_map.end() ) throw IfcException("Type not found");
    else return i->second->getArgumentEntity(a);
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

bool Type::GetAttributeDerived(Enum t, unsigned char a) {
    if (derived_map.empty()) ::InitDerivedMap();
    std::map<Type::Enum,std::set<int> >::const_iterator i = derived_map.find(t);
    return i != derived_map.end() && i->second.find(a) != i->second.end();
}

std::pair<const char*, int> Type::GetEnumerationIndex(Enum t, const std::string& a) {
    if (enumeration_descriptor_map.empty()) ::InitDescriptorMap();
    std::map<Type::Enum,IfcEnumerationDescriptor*>::const_iterator i = enumeration_descriptor_map.find(t);
    if ( i == enumeration_descriptor_map.end() ) throw IfcException("Value not found");
    else return i->second->getIndex(a);
}

std::pair<Type::Enum, unsigned> Type::GetInverseAttribute(Enum t, const std::string& a) {
    if (inverse_map.empty()) ::InitInverseMap();
    inverse_map_t::const_iterator it;
    inverse_map_t::mapped_type::const_iterator jt;
    for(;;) {
        it = inverse_map.find(t);
        if (it != inverse_map.end()) {
            jt = it->second.find(a);
            if (jt != it->second.end()) {
                return jt->second;
            }
        }
        boost::optional<Enum> pt = Parent(t);
        if (pt) {
            t = *pt;
        }
        else {
            break;
        }
    }
    throw IfcException("Attribute not found");
}

std::set<std::string> Type::GetInverseAttributeNames(Enum t) {
    if (inverse_map.empty()) ::InitInverseMap();
    inverse_map_t::const_iterator it;
    inverse_map_t::mapped_type::const_iterator jt;

    std::set<std::string> return_value;

    for (;;) {
        it = inverse_map.find(t);
        if (it != inverse_map.end()) {
            for (jt = it->second.begin(); jt != it->second.end(); ++jt) {
                return_value.insert(jt->first);
            }
        }
        boost::optional<Enum> pt = Parent(t);
        if (pt) {
            t = *pt;
        }
        else {
            break;
        }
    }

    return return_value;
}

void Type::PopulateDerivedFields(IfcEntityInstanceData* e) {
    if (derived_map.empty()) ::InitDerivedMap();
    std::map<Type::Enum, std::set<int> >::const_iterator i = derived_map.find(e->type());
    if (i != derived_map.end()) {
        for (std::set<int>::const_iterator it = i->second.begin(); it != i->second.end(); ++it) {
            IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();
            attr->set(IfcWrite::IfcWriteArgument::Derived());
            e->setArgument(*it, attr);
        }
    }
}
"""

entity_descriptor = """    current = entity_descriptor_map[Type::%(type)s] = new IfcEntityDescriptor(Type::%(type)s,%(parent_statement)s);
%(entity_descriptor_attributes)s"""

entity_descriptor_parent = "entity_descriptor_map.find(Type::%(type)s)->second"
entity_descriptor_attribute_without_entity = '    current->add("%(name)s",%(optional)s,%(type)s);'
entity_descriptor_attribute_with_entity = '    current->add("%(name)s",%(optional)s,%(type)s,Type::%(entity_name)s);'

enumeration_descriptor = """    values.clear(); values.reserve(128);
%(enumeration_descriptor_values)s
    enumeration_descriptor_map[Type::%(type)s] = new IfcEnumerationDescriptor(Type::%(type)s, values);"""

enumeration_descriptor_value = '    values.push_back("%(name)s");'

derived_field_statement = '    {std::set<int> idxs; %(statements)sderived_map[Type::%(type)s] = idxs;}';
derived_field_statement_attrs = 'idxs.insert(%d); '

simpletype = """%(documentation)s
class IFC_PARSE_API %(name)s : public %(superclass)s {
public:
    virtual IfcUtil::ArgumentType getArgumentType(unsigned int i) const;
    virtual Argument* getArgument(unsigned int i) const;
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    explicit %(name)s (IfcEntityInstanceData* e);
    %(name)s (%(type)s v);
    operator %(type)s() const;
};
"""

simpletype_impl_comment = "// Function implementations for %(name)s"
simpletype_impl_argument_type = "if (i == 0) { return %(attr_type)s; } else { throw IfcParse::IfcAttributeOutOfRangeException(\"Argument index out of range\"); }"
simpletype_impl_argument = "return entity->getArgument(i);"
simpletype_impl_is_with_supertype = "return v == Type::%(class_name)s || %(superclass)s::is(v);"
simpletype_impl_is_without_supertype = "return v == %(class_name)s::Class();"
simpletype_impl_type = "return Type::%(class_name)s;"
simpletype_impl_class = "return Type::%(class_name)s;"
simpletype_impl_explicit_constructor = "entity = e;"
simpletype_impl_constructor           = "entity = new IfcEntityInstanceData(Class()); {IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(v"           +"); entity->setArgument(0, attr);}"
simpletype_impl_constructor_templated = "entity = new IfcEntityInstanceData(Class()); {IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(v->generalize()); entity->setArgument(0, attr);}"
simpletype_impl_cast = "return *entity->getArgument(0);"
simpletype_impl_cast_templated = "IfcEntityList::ptr es = *entity->getArgument(0); return es->as<%(underlying_type)s>();"
    
select = """%(documentation)s
typedef IfcUtil::IfcBaseClass %(name)s;
"""

enumeration = """namespace %(name)s {
%(documentation)s
typedef enum {%(values)s} %(name)s;
IFC_PARSE_API const char* ToString(%(name)s v);
IFC_PARSE_API %(name)s FromString(const std::string& s);
}
"""

entity = """%(documentation)s
class IFC_PARSE_API %(name)s %(superclass)s{
public:
%(attributes)s    virtual unsigned int getArgumentCount() const { return %(argument_count)d; }
    virtual IfcUtil::ArgumentType getArgumentType(unsigned int i) const {%(argument_type_function_body)s}
    virtual Type::Enum getArgumentEntity(unsigned int i) const {%(argument_entity_function_body)s}
    virtual const char* getArgumentName(unsigned int i) const {%(argument_name_function_body)s}
    virtual Argument* getArgument(unsigned int i) const { return entity->getArgument(i); }
%(inverse)s    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    %(name)s (IfcEntityInstanceData* e);
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
%(name)s::%(name)s(IfcEntityInstanceData* e) : %(superclass)s { if (!e) return; if (e->type() != Type::%(name)s) throw IfcException("Unable to find find keyword in schema"); entity = e; }
%(name)s::%(name)s(%(constructor_arguments)s) : %(superclass)s {entity = new IfcEntityInstanceData(Class()); %(constructor_implementation)s }
"""

optional_attribute_description = "/// Whether the optional attribute %s is defined for this %s"

function = "%(return_type)s %(class_name)s::%(name)s(%(arguments)s) { %(body)s }"
const_function = "%(return_type)s %(class_name)s::%(name)s(%(arguments)s) const { %(body)s }"
constructor = "%(class_name)s::%(class_name)s(%(arguments)s) { %(body)s }"
constructor_single_initlist = "%(class_name)s::%(class_name)s(%(arguments)s) : %(superclass)s(%(superclass_init)s) { %(body)s }"
cast_function = "%(class_name)s::operator %(return_type)s() const { %(body)s }"

array_type = "std::vector< %(instance_type)s > /*[%(lower)s:%(upper)s]*/"
nested_array_type = "std::vector< std::vector< %(instance_type)s > >"
list_type = "IfcTemplatedEntityList< %(instance_type)s >::ptr"
list_list_type = "IfcTemplatedEntityListList< %(instance_type)s >::ptr"
untyped_list = "IfcEntityList::ptr"
inverse_attr = "IfcTemplatedEntityList< %(entity)s >::ptr %(name)s() const; // INVERSE %(entity)s::%(attribute)s"

enum_from_string_stmt = '    if (s == "%(value)s") return ::%(schema_name)s::%(name)s::%(short_name)s_%(value)s;'

schema_entity_stmt = '        case Type::%(name)s: return new %(name)s(e); break;'
string_map_statement = '    string_map["%(uppercase_name)s"%(padding)s] = Type::%(name)s;'
parent_type_stmt = '    if(v==%(name)s%(padding)s) { return %(parent)s; }'

parent_type_test = " || %s::is(v)"

optional_attr_stmt = "return !entity->getArgument(%(index)d)->isNull();"

get_attr_stmt = "return *entity->getArgument(%(index)d);"
get_attr_stmt_enum = "return %(type)s::FromString(*entity->getArgument(%(index)d));"
get_attr_stmt_entity = "return (%(type)s)((IfcUtil::IfcBaseClass*)(*entity->getArgument(%(index)d)));"
get_attr_stmt_array = "IfcEntityList::ptr es = *entity->getArgument(%(index)d); return es->as<%(list_instance_type)s>();"
get_attr_stmt_nested_array = "IfcEntityListList::ptr es = *entity->getArgument(%(index)d); return es->as<%(list_instance_type)s>();"

get_inverse = "return entity->getInverse(Type::%(type)s, %(index)d)->as<%(type)s>();"

set_attr_stmt       = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(v"                                                                     +");entity->setArgument(%(index)d,attr);}"
set_attr_stmt_enum  = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(IfcWrite::IfcWriteArgument::EnumerationReference(v,%(type)s::ToString(v)));entity->setArgument(%(index)d,attr);}"
set_attr_stmt_array = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(v->generalize()"                                                       +");entity->setArgument(%(index)d,attr);}"

constructor_stmt          = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set((%(name)s)"                                                                                +");entity->setArgument(%(index)d,attr);}"
constructor_stmt_enum     = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set((IfcWrite::IfcWriteArgument::EnumerationReference(%(name)s,%(type)s::ToString(%(name)s)))" +");entity->setArgument(%(index)d,attr);}"
constructor_stmt_array    = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set((%(name)s)->generalize()"                                                                  +");entity->setArgument(%(index)d,attr);}"
constructor_stmt_derived  = "{IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument();attr->set(IfcWrite::IfcWriteArgument::Derived()"                                                     +");entity->setArgument(%(index)d,attr);}"

constructor_stmt_optional = " if (%(name)s) {%(stmt)s } else { IfcWrite::IfcWriteArgument* attr = new IfcWrite::IfcWriteArgument(); attr->set(boost::blank()); entity->setArgument(%(index)d, attr); }"

inverse_implementation = "    inverse_map[Type::%(type)s].insert(std::make_pair(\"%(name)s\", std::make_pair(Type::%(related_type)s, %(index)d)));"

def multi_line_comment(li):
    return ("/// %s"%("\n/// ".join(li))) if len(li) else ""

