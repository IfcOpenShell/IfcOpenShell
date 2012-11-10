header = """
/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/
 """.strip()

###############################################################################
#                                                                             #
# This file can be used to generate C++ code from Express schema files. The   #
# generated code works alongside the IfcOpenShell IfcParse library. This      #
# script has only been tested on IFC2X3_TC1.exp and will most probably not    #
# work on any other schemas.                                                  #
#                                                                             #
# Note this script uses funcparserlib, which is available at:                 #
# http://code.google.com/p/funcparserlib/                                     #
# The script only works with revision 30f7ee896bc9 because it uses the some() #
# parser and is incompatible with other changes as well.                      #
#                                                                             #
###############################################################################

import os, sys
import IfcDocumentation

filename = sys.argv[1]

#
# A class to split the Express schema files into seperate tokens
#
class Tokenizer(object):
    comment = ['(*','*)']
    termchars = ',;()=[]:'
    def __init__(self, fn):
        if hasattr(fn,'read'): object.__setattr__(self,'f',fn)
        else: object.__setattr__(self,'f',open(fn,'rb'))
    def __getattr__(self, name):
        return getattr(self.f, name)
    def __setattr__(self, name, value):
        setattr(self.f, name, value)
    def __iter__(self): return self
    def next(self):
        def get():
            buffer = ''
            in_comment = False
            in_string = False
            offset = self.tell()
            while True:
                c = self.read(2)
                if len(c) < 2: raise StopIteration
                if c in Tokenizer.comment:
                    in_comment = c == Tokenizer.comment[0]
                    continue
                if in_string and c == "''":
                    buffer += "'"
                    continue
                self.seek(-1,1)
                if not in_string and c[0].isspace():
                    if ( len(buffer) ): return buffer
                    else:
                        offset = self.tell()
                        continue
                if not in_comment:
                    if len(buffer) and (c[0] in Tokenizer.termchars or buffer[-1] in Tokenizer.termchars):
                        self.seek(-1,1)
                        return buffer
                    buffer += c[0]
        return get()

#
# Some global variables to keep track of variable names
#
express_to_cpp = {
    'BOOLEAN':'bool',
    'LOGICAL':'bool',
    'INTEGER':'int',
    'REAL':'double',
    'NUMBER':'double',
    'STRING':'std::string'
}
schema_version = ''
enumerations = set()
selections = set()
entity_names = set()
simple_types = {}
selectable_simple_types = set()
argument_count = {}
parent_relations = {}
argument_names_and_types = {}
entity_map = {}

#
# Since inherited arguments of Express entities are placed in sequence before the 
# non-inherited ones, we need to keep track of how many inherited arguments exist
#
def argument_start(c):
    if c not in parent_relations: return 0
    i = 0
    while True:
        c = parent_relations[c]
        i += argument_count[c] if c in argument_count else 0
        if not (c in parent_relations): break
    return i
    
def parent_arguments(c):
    if c not in parent_relations: return []
    l = []
    while True:
        c = parent_relations[c]
        i += argument_count[c] if c in argument_count else 0
        if not (c in parent_relations): break
    return []

#
# Every constructor also initializes their parent class members, hence they
# need be stored as well.
#    
def parent_arguments(c):
    if c not in parent_relations: return []
    l = []
    while True:
        c = parent_relations[c]
        i += argument_count[c] if c in argument_count else 0
        if not (c in parent_relations): break
    return []

#
# Several classes to generate code from Express types and entities
#
class ArrayType:
    def __init__(self,l): 
        self.type = express_to_cpp.get(l[3],l[3])
        self.upper = l[2]
        self.lower = l[1]
    def is_select_list(self): return self.type in selections
    def __str__(self):
        if self.type in entity_names:
            return "SHARED_PTR< IfcTemplatedEntityList< %s > >"%self.type
        elif self.type in selections:
            return "SHARED_PTR< IfcTemplatedEntityList< IfcAbstractSelect > >"
        else:
            return "std::vector< %(type)s > /*[%(lower)s:%(upper)s]*/"%self.__dict__
    def is_shared_ptr(self): return self.type in entity_names or self.type in selections
    def type_enum(self):
        if self.type in simple_types:
            t = simple_types[self.type].type_enum()
        else:
            t = self.type
        if t in entity_names or t == "Argument_ENTITY":
            return "Argument_ENTITY_LIST"
        elif t in selections:
            return "Argument_ENTITY_LIST"
        elif t == "int":
            return "Argument_VECTOR_INT"
        elif t == "double" or t == "Argument_DOUBLE":
            return "Argument_VECTOR_DOUBLE"
        elif t == "std::string" or t == "Argument_STRING":
            return "Argument_VECTOR_STRING"
        elif isinstance(t, BinaryType):
            return "Argument_UNKNOWN"
        else:
            assert False, t
        
class ScalarType:
    def __init__(self,l): self.type = express_to_cpp.get(l,l)
    def __str__(self): return self.type
    def is_select_list(self): return False
    def type_enum(self):
        if self.type in simple_types:
            return simple_types[self.type].type_enum()
        elif self.type in entity_names:
            return "Argument_ENTITY"
        else:
            return { "bool":"Argument_BOOL","int":"Argument_INT","double":"Argument_DOUBLE","std::string":"Argument_STRING"}[self.type]
class EnumType:
    def __init__(self,l):
        self.v = [(x,'%s_%s'%('%(fancy_name)s',x)) for x in l]
        self.maxlen = max([len(v) for v in self.v])
    def __str__(self): 
        if generator_mode == 'HEADER':
            return "enum {%s}"%", ".join([v2 for v1,v2 in self.v])
        elif generator_mode == 'SOURCE_TO':
            return '{ "%s" }'%'","'.join([v1 for v1,v2 in self.v])
        elif generator_mode == 'SOURCE_FROM':
            return "".join(['    if(s=="%s"%s) return ::%s::%s::%s;\n'%(v1.upper()," "*(self.maxlen-len(v1)),schema_version,"%(name)s",v2) for v1,v2 in self.v])
    def is_select_list(self): return False
    def __len__(self): return len(self.v)
    def type_enum(self):
        return "Argument_ENUMERATION"
class SelectType:
    def __init__(self,l): 
        for x in l: 
            if x in simple_types: selectable_simple_types.add(x)
    def __str__(self): return "IfcSchemaEntity"
    def is_select_list(self): return False
    def type_enum(self): return "Argument_ENTITY"
class BinaryType:
    def __init__(self,l): self.l = int(l)
    def __str__(self): return "char[%s]"%self.l
    def is_select_list(self): return False
    def type_enum(self): raise NotImplementedError()
class InverseType:
    def __init__(self,l):
        self.name, self.type, self.reference = l
    def type_enum(self): return "Argument_ENTITY"
    def is_select_list(self): return False
class Typedef:
    def __init__(self,l):
        self.name,self.type=l[1:3]
        self.fancy_name = self.name[:-4] if self.name.endswith("Enum") else self.name
        if isinstance(self.type,EnumType): 
            enumerations.add(self.name)
            self.len = len(self.type)
        elif isinstance(self.type,SelectType): selections.add(self.name)
        simple_types[self.name] = self
        comment = IfcDocumentation.description(self.name)
        self.comment = comment+"\n" if comment else ''
    def __str__(self):
        global generator_mode
        if generator_mode == 'HEADER' and isinstance(self.type,EnumType):
            return ("namespace %(name)s {\n%(comment)stypedef %(type)s %(name)s;\nconst char* ToString(%(name)s v);\n%(name)s FromString(const std::string& s);\n}"%self.__dict__)%self.__dict__
        elif generator_mode == 'HEADER':
            return "%stypedef %s %s;"%(self.comment,self.type,self.name)
        elif generator_mode == 'SOURCE' and isinstance(self.type,EnumType):
            generator_mode = 'SOURCE_TO'
            s =  "const char* %(name)s::ToString(%(name)s v) {\n    if ( v < 0 || v >= %(len)d ) throw IfcException(\"Unable to find find keyword in schema\");\n    const char* names[] = %(type)s;\n    return names[v];\n}\n"%self.__dict__
            generator_mode = 'SOURCE_FROM'
            s += ("%(name)s::%(name)s %(name)s::FromString(const std::string& s) {\n%(type)s    throw IfcException(\"Unable to find find keyword in schema\");\n}"%self.__dict__)%self.__dict__
            generator_mode = 'SOURCE'
            return s
    def type_enum(self):
        return self.type.type_enum()
class Argument(object):
    def __init__(self,l):
        self.name, self.optional, self.type = l
    def is_enum(self): return str(self.type) in enumerations
    def type_str(self):
        if self.type.is_select_list():
            # This is extremely hackish indeed
            return "optional< IfcEntities >" if self.optional else "IfcEntities"
        elif str(self.type) in entity_names:
            return "%(type)s*"%self.__dict__
        else:
            t = "%(type)s::%(type)s"%self.__dict__ if self.is_enum() else self.type
            return "optional< %s >"%t if self.optional else t
class ArgumentList:
    def __init__(self,l):
        self.l = [Argument(a) for a in l]
        self.argstart = 0
    def __len__(self): return len(self.l)
    def __str__(self):
        s = ""
        argv = self.argstart
        for a in self.l:
            class_name = indent = comment = optional_comment = ""
            is_array = isinstance(a.type,ArrayType) and a.type.is_shared_ptr()
            return_type = str(a.type)
            if generator_mode == 'SOURCE':
                class_name = "%(class_name)s::"
                if isinstance(a.type,BinaryType) or (isinstance(a.type,ArrayType) and isinstance(a.type.type,BinaryType)):
                    function_body = " { throw; /* Not implemented argument*/ }"
                elif isinstance(a.type,ArrayType) and str(a.type.type) in entity_names:
                    function_body = " { RETURN_AS_LIST(%s,%d) }"%(a.type.type,argv)
                elif isinstance(a.type,ArrayType) and str(a.type.type) in selections:
                    function_body = " { RETURN_AS_LIST(IfcAbstractSelect,%d) }"%(argv)
                elif return_type in entity_names:
                    function_body = " { return reinterpret_pointer_cast<IfcBaseClass,%s>(*entity->getArgument(%d)); }"%(return_type,argv)
                elif return_type in enumerations:
                    function_body = " { return %s::FromString(*entity->getArgument(%d)); }"%(return_type,argv)
                else:
                    function_body = " { return *entity->getArgument(%d); }"%argv
                function_body2 = " { return !entity->getArgument(%d)->isNull(); }"%argv
                if isinstance(a.type,BinaryType) or (isinstance(a.type,ArrayType) and isinstance(a.type.type,BinaryType)):
                    function_body3 = " { if ( ! entity->isWritable() ) { throw; } }"
                elif return_type in enumerations:
                    function_body3 = " { if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%d,v%s,%s::ToString(v)); }"%(argv,"->generalize()" if is_array else "",return_type)
                else:
                    function_body3 = " { if ( ! entity->isWritable() ) { entity = new IfcWritableEntity(entity); } ((IfcWritableEntity*)entity)->setArgument(%d,v%s); }"%(argv,"->generalize()" if is_array else "")
            else:
                indent = "    "
                function_body = function_body2 = function_body3 = ";"
                comment = IfcDocumentation.description((self.class_name,a.name))
                comment = comment+"\n" if comment else ''
                comment = comment.replace("///","%s///"%indent)
                optional_comment = "%s/// Whether the optional attribute %s is defined for this %s\n"%(indent,a.name,self.class_name)
            if a.optional: s += "\n%s%sbool %shas%s()%s"%(optional_comment,indent,class_name,a.name,function_body2)
            if ( str(a.type) in enumerations ):
                return_type = "%(type)s::%(type)s"%a.__dict__
            elif ( str(a.type) in entity_names ):
                return_type = "%(type)s*"%a.__dict__
            s += "\n%s%s%s %s%s()%s"%(comment,indent,return_type,class_name,a.name,function_body)
            s += "\n%svoid %sset%s(%s v)%s"%(indent,class_name,a.name,return_type,function_body3)
            argv += 1

        if generator_mode == 'HEADER':
            s += "\n virtual unsigned int getArgumentCount() const { return %(n_arguments)d; }" % dict(class_name=self.class_name, n_arguments=len(self.l) + argument_start(self.class_name))

            s += "\n virtual ArgumentType getArgumentType(unsigned int i) const {"
            if len(self.l):
                s += " switch (i) {"
                for i, a in enumerate(self.l):
                    s += "case %d: " % (i + argument_start(self.class_name))
                    s += "return %s; " % a.type.type_enum()
                s += "}"
            if self.parent_class is not None:
                s += " return %s::getArgumentType(i); }" % self.parent_class
            else:
                s += " throw IfcException(\"argument out of range\"); }"

            s += "\n virtual const char* getArgumentName(unsigned int i) const {"
            if len(self.l):
                s += " switch (i) {"
                for i, a in enumerate(self.l):
                    s += "case %d: " % (i + argument_start(self.class_name))
                    s += "return \"%s\"; " % a.name
                s += "}"
            if self.parent_class is not None:
                s += " return %s::getArgumentName(i); }" % self.parent_class
            else:
                s += " throw IfcException(\"argument out of range\"); }"

            s += "\n virtual ArgumentPtr getArgument(unsigned int i) const { return entity->getArgument(i); }"
        return s
class InverseList:
    def __init__(self,l):
        self.l = l
    def __str__(self):
        if self.l is None: return ""
        s = ""
        for i in self.l:
            if generator_mode == 'HEADER':
                s += "\n    SHARED_PTR< IfcTemplatedEntityList< %s > > %s(); // INVERSE %s::%s"%(i.type.type,i.name,i.type.type,i.reference)
            elif generator_mode == 'SOURCE':
                s += "\n%s::list %s::%s() { RETURN_INVERSE(%s) }"%(i.type.type,"%(class_name)s",i.name,i.type.type)
        return s
class Classdef:
    def __init__(self,l):
        self.class_name, self.parent_class, self.arguments, derive, self.inverse = l
        self.arguments.class_name = self.class_name
        self.arguments.parent_class = self.parent_class
        entity_names.add(self.class_name)
        parent_relations[self.class_name] = self.parent_class
        argument_count[self.class_name] = len(self.arguments)
        entity_map[self.class_name] = self
        # For derived attributes only a reference is kepts to overridden attributes in parent classes
        self.derive = [x[0].split('.')[-1] for x in derive[1] if x[0].startswith("SELF\\")] if derive else []
    def list_constructor_args(self):
        s = entity_map[self.parent_class].list_constructor_args() if self.parent_class else []
        i = len(s) + 1
        s += [(a.type_str(),b+i,a.name) for a,b in zip(self.arguments.l,range(len(self.arguments)))]
        return s
    def get_constructor_args(self):
        return ["%s v%d_%s"%x for x in self.list_constructor_args() if x[2] not in self.get_derived()]        
    def get_constructor_implementation(self):
        s = entity_map[self.parent_class].get_constructor_implementation() if self.parent_class else []
        i = len(s) + 1
        b = 0
        for a in self.arguments.l:
            is_enumeration = str(a.type) in enumerations
            # boost::optional is not used for pointer types, because they are set to NULL using 0
            use_boost_optional = a.optional and str(a.type) not in entity_names
            # boost::optional types need to be dereferenced before passing to the writable entity
            dereference = "*" if use_boost_optional else ""
            generalize = "->generalize()" if (isinstance(a.type,ArrayType) and a.type.is_shared_ptr() and not a.type.is_select_list()) else ""
            if isinstance(a.type,BinaryType) or (isinstance(a.type,ArrayType) and isinstance(a.type.type,BinaryType)):
                continue
            if is_enumeration:
                impl = "e->setArgument(%d,%sv%d_%s,%s::ToString(%sv%d_%s))"%(b+i-1,dereference,b+i,a.name,str(a.type),dereference,b+i,a.name)
            else:
                impl = "e->setArgument(%d,(%sv%d_%s)%s)"%(b+i-1,dereference,b+i,a.name,generalize)            
            if use_boost_optional:
                s.append(["if (v%d_%s) { %s; } else { e->setArgument(%d); } "%(b+i,a.name,impl,b+i-1),a.name,i-1])
            else: s.append([impl,a.name,i-1])
            b += 1
        return s
    def get_derived(self):
        s = entity_map[self.parent_class].get_derived() if self.parent_class else []
        return s + self.derive
    def __str__(self):
        self.constructor_args_list = self.get_constructor_args()
        self.constructor_args = ", ".join(self.constructor_args_list)
        if generator_mode == 'HEADER':            
            comment = IfcDocumentation.description(self.class_name)
            comment = comment+"\n" if comment else ''
            return "%sclass %s : public %s {\npublic:%s%s%s\n};" % (comment,self.class_name,
                "IfcBaseEntity" if self.parent_class is None else self.parent_class,
                self.arguments,
                self.inverse,
                ("\n    bool is(Type::Enum v) const;"+
                "\n    Type::Enum type() const;"+
                "\n    static Type::Enum Class();"+
                "\n    %(class_name)s (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());"+
               ("\n    %(class_name)s (%(constructor_args)s);" if len(self.constructor_args_list) else "")+
                "\n    typedef %(class_name)s* ptr;"+
                "\n    typedef SHARED_PTR< IfcTemplatedEntityList< %(class_name)s > > list;"+
                "\n    typedef IfcTemplatedEntityList< %(class_name)s >::it it;")%self.__dict__
            )
        elif generator_mode == 'SOURCE':
            self.arguments.argstart = argument_start(self.class_name)
            self.constructor_implementation = "; ".join([x[0] if x[1] not in self.get_derived() else "e->setArgumentDerived(%d)"%x[2] for x in self.get_constructor_implementation()])
            return (("\n// Function implementations for %(class_name)s"+str(self.arguments)+str(self.inverse)+
            ("\nbool %(class_name)s::is(Type::Enum v) const { return v == Type::%(class_name)s; }" if self.parent_class is None else
            "\nbool %(class_name)s::is(Type::Enum v) const { return v == Type::%(class_name)s || %(parent_class)s::is(v); }")+
            "\nType::Enum %(class_name)s::type() const { return Type::%(class_name)s; }"+
            "\nType::Enum %(class_name)s::Class() { return Type::%(class_name)s; }"+
            "\n%(class_name)s::%(class_name)s(IfcAbstractEntityPtr e) { if (!is(Type::%(class_name)s)) throw IfcException(\"Unable to find find keyword in schema\"); entity = e; }"+
            ("\n%(class_name)s::%(class_name)s(%(constructor_args)s) { IfcWritableEntity* e = new IfcWritableEntity(Class()); %(constructor_implementation)s; entity = e; EntityBuffer::Add(this); }"  if len(self.constructor_args_list) else "")
            )%self.__dict__)%self.__dict__


from funcparserlib.parser import a, skip, many, maybe, some

#
# Lambda functions to map combinator output to classes
# 
array_type = lambda t: ArrayType(t)
scalar_type = lambda t: ScalarType(t)
enum_type = lambda t: EnumType(t)
select_type = lambda t: SelectType(t)
binary_type = lambda t: BinaryType(t)
inverse_type = lambda t: InverseType(t)
format_type = lambda t: Typedef(t)
argument_list = lambda t: ArgumentList(t)
inverse_list = lambda t: InverseList(t)
format_options = lambda t: [t[0]]+t[1]

#
# The actual grammar definition
#
s = some(lambda t: not t in ['UNIQUE','WHERE','END_ENTITY','END_TYPE','INVERSE','DERIVE'])
x = lambda s:skip(a(s))
list_or_array = a('ARRAY') | a('LIST') | a('SET')
binary = x('BINARY')+x('(') + s + x(')') >> binary_type
array = list_or_array + x('[') + s + x(':') + s + x(']') + x('OF') + skip(maybe(a('UNIQUE'))) + (binary|s) >> array_type
options = x('(') + s + many(x(',')+s) + x(')') >> format_options
enum = x('ENUMERATION') + x('OF') + options >> enum_type
select = x('SELECT') + options >> select_type
single = s + skip(maybe(x('(')+s+x(')')) + maybe(a('FIXED'))) >> scalar_type
type_type = array | enum | select | single
type_start = a('TYPE') + s + x('=') + type_type + x(';')
type_end = a('END_TYPE') + x(';')

to_end = many(some(lambda t: t != ';'))
clause = s + x(':') + to_end + x(';')
where = a('WHERE') + many(clause)

type = type_start + maybe(where) + type_end >> format_type

subtype = x('SUBTYPE') + x('OF') + x('(') + s + x(')')
supertype = maybe(x('ABSTRACT')) + x('SUPERTYPE') + x('OF') + x('(') + x('ONEOF') + options + x(')')
entity_start = x('ENTITY') + s + skip(maybe(supertype)) + maybe(subtype) + x(';')
entity_end = x('END_ENTITY') + x(';')
key_value = s + x(':') + maybe(a('OPTIONAL')) + (array|binary|single) + x(';')
arguments = many(key_value) >> argument_list
unique_value = s + x(':') + s + many(a(',')+s) + a(';')
unique = skip(a('UNIQUE') + many(unique_value))
inverse_def = s + x(':') + (array|single) + x('FOR') + s + x(';') >> inverse_type
inverse = maybe(x('INVERSE') + many( inverse_def )) >> inverse_list
derive = a('DERIVE') + many(clause)

entity = entity_start + arguments + skip(maybe(unique)) + maybe(derive) + inverse + skip(maybe(where)) + entity_end >> Classdef

schema = skip(a('SCHEMA')) + s + x(';')

express = schema + many(type) + many(entity)
schema_version,types,entities = express.parse(list(Tokenizer(filename)))
schema_version = schema_version.capitalize()

#
# Writing of the three generated files starts here
#
h_file = open("%s.h"%schema_version,'w')
enumh_file = open("%senum.h"%schema_version,'w')
cpp_file = open("%s.cpp"%schema_version,'w')

header += """

/********************************************************************************
 *                                                                              *
 * This file has been generated from %s. Do not make modifications  *
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/
 """%filename

generator_mode = 'HEADER'
 
print >>h_file, header
print >>enumh_file, header
print >>cpp_file, header
print >>h_file, """#ifndef %(schema_upper)s_H
#define %(schema_upper)s_H

#include <string>
#include <vector>
#include <map>

#include <boost/optional.hpp>

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/%(schema)senum.h"

using namespace IfcUtil;
using IfcParse::IfcException;
using boost::optional;

#define RETURN_INVERSE(T) \\
    IfcEntities e = entity->getInverse(T::Class()); \\
    SHARED_PTR< IfcTemplatedEntityList<T> > l ( new IfcTemplatedEntityList<T>() ); \\
    for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) { \\
        l->push(reinterpret_pointer_cast<IfcBaseClass,T>(*it)); \\
    } \\
    return l;

#define RETURN_AS_SINGLE(T,a) \\
    return reinterpret_pointer_cast<IfcBaseClass,T>(*entity->getArgument(a));

#define RETURN_AS_LIST(T,a)  \\
    IfcEntities e = *entity->getArgument(a);  \\
    SHARED_PTR< IfcTemplatedEntityList<T> > l ( new IfcTemplatedEntityList<T>() );  \\
    for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) {  \\
        l->push(reinterpret_pointer_cast<IfcBaseClass,T>(*it)); \\
    }  \\
    return l;

namespace %(schema)s {
"""%{'schema_upper':schema_version.upper(),'schema':schema_version}

simple_enumerations = sorted(selectable_simple_types)
entity_enumerations = sorted(entity_names)
all_enumerations = simple_enumerations + entity_enumerations

print >>enumh_file, """#ifndef IFC2X3ENUM_H
#define IFC2X3ENUM_H

namespace Ifc2x3 {

namespace Type {
    typedef enum {
        %(enum)s
    } Enum;
    Enum Parent(Enum v);
    Enum FromString(const std::string& s);
    std::string ToString(Enum v);
    bool IsSimple(Enum v);
}

}

#endif
"""%{'schema_upper':schema_version.upper(),'schema':schema_version,'enum':", ".join(all_enumerations + ["ALL"])}

defined_types = set(express_to_cpp.values())
deferred_types = []

for t in [T for T in types if not (isinstance(T.type,EnumType) or isinstance(T.type,SelectType))]:
    if isinstance(t.type,ScalarType) and str(t.type) not in defined_types:
        deferred_types.append(t)
    else:
        print >>h_file, t
for t in [T for T in types if isinstance(T.type,SelectType)]:
    print >>h_file, t
for t in deferred_types:
    print >>h_file, t
for t in [T for T in types if isinstance(T.type,EnumType)]:
    print >>h_file, t
    
print >>h_file, "// Forward definitions"
print >>h_file, "class %s;\n"%"; class ".join([e.class_name for e in entities])

defined_classes = set()
while True:
    classes = [c for c in entities if c.class_name not in defined_classes]
    if not len(classes): break
    for c in classes:
        if c.parent_class is None or c.parent_class in defined_classes:
            defined_classes.add(c.class_name)
            print >>h_file, c

print >>h_file, "void InitStringMap();"
print >>h_file, "IfcSchemaEntity SchemaEntity(IfcAbstractEntityPtr e = 0);"

print >>h_file, "}\n\n#endif"

generator_mode = 'SOURCE'

print >>cpp_file, """#include "%(schema)s.h"
#include "IfcException.h"
#include "IfcWrite.h"
#include "IfcWritableEntity.h"

using namespace %(schema)s;
using namespace IfcParse;
using namespace IfcWrite;

IfcSchemaEntity %(schema)s::SchemaEntity(IfcAbstractEntityPtr e) {
    switch(e->type()){"""%{'schema':schema_version}

for e in simple_enumerations:
    print >>cpp_file, "        case Type::%s: return new IfcEntitySelect(e); break;"%e
for e in entity_enumerations:
    print >>cpp_file, "        case Type::%s: return new %s(e); break;"%(e,e)
print >>cpp_file, "        default: throw IfcException(\"Unable to find find keyword in schema\"); break; "
print >>cpp_file, "    }\n}"
print >>cpp_file
print >>cpp_file, "std::string Type::ToString(Enum v) {"
print >>cpp_file, "    if (v < 0 || v >= %d) throw IfcException(\"Unable to find find keyword in schema\");"%len(all_enumerations)
print >>cpp_file, '    const char* names[] = { "%s" };'%'","'.join(all_enumerations)
print >>cpp_file, '    return names[v];'
print >>cpp_file, "}"
print >>cpp_file
#print >>cpp_file, "Type::Enum Type::FromStringOld(const std::string& s){"
#elseif = "if"
#maxlen = max([len(e) for e in all_enumerations])
#for e in all_enumerations:
#    print >>cpp_file, '    %s(s=="%s"%s) { return %s; }'%(elseif,e.upper()," "*(maxlen-len(e)),e)
#print >>cpp_file, "    throw;"
#print >>cpp_file, "}"
print >>cpp_file, "std::map<std::string,Type::Enum> string_map;"
print >>cpp_file, "void Ifc2x3::InitStringMap() {"
maxlen = max([len(e) for e in all_enumerations])
for e in all_enumerations:
    print >>cpp_file, '    string_map["%s"%s] = Type::%s;'%(e.upper()," "*(maxlen-len(e)),e)
print >>cpp_file, """}
Type::Enum Type::FromString(const std::string& s) {
    std::map<std::string,Type::Enum>::const_iterator it = string_map.find(s);
    if ( it == string_map.end() ) throw IfcException("Unable to find find keyword in schema");
    else return it->second;
}"""

print >>cpp_file, "Type::Enum Type::Parent(Enum v){"
print >>cpp_file, "    if (v < 0 || v >= %d) return (Enum)-1;"%len(all_enumerations)
for e in entity_enumerations:
    if e not in parent_relations or parent_relations[e] is None: continue
    print >>cpp_file, '    if(v==%s%s) { return %s; }'%(e," "*(maxlen-len(e)),parent_relations[e])
print >>cpp_file, "    return (Enum)-1;"
print >>cpp_file, "}"

print >>cpp_file, "bool Type::IsSimple(Enum v){"
print >>cpp_file, "    return v == Type::%s;"%" || v == Type::".join(simple_enumerations)
print >>cpp_file, "}"

for t in [T for T in types if isinstance(T.type,EnumType)]:
    print >>cpp_file, t
for e in entities: print >>cpp_file, e,
