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

import nodes
import templates

class Mapping:

    express_to_cpp_typemapping = {
        'boolean' : 'bool',
        'logical' : 'bool',
        'integer' : 'int',
        'real'    : 'double',
        'number'  : 'double',
        'string'  : 'std::string'
    }

    def __init__(self, schema):
        self.schema = schema

    def make_type_string(self, type):
        if isinstance(type, str):
            return self.express_to_cpp_typemapping.get(type, type)
        else:
            is_list = self.schema.is_entity(type.type)
            is_nested_list = isinstance(type.type, nodes.AggregationType)
            tmpl = templates.list_list_type if is_nested_list else templates.list_type if is_list else templates.array_type
            return tmpl % {
                'instance_type' : self.make_type_string(type.type),
                'lower'         : type.bounds.lower,
                'upper'         : type.bounds.upper,
            }

    def is_array(self, type):
        if isinstance(type, nodes.AggregationType):
            return True
        elif isinstance(type, str) and self.schema.is_type(type):
            return self.is_array(self.schema.types[type].type.type)
        else:
            return False

    def make_argument_type(self, attr):
        def _make_argument_type(type):
            if type in self.express_to_cpp_typemapping:
                return self.express_to_cpp_typemapping.get(type, type).split('::')[-1].upper()
            elif self.schema.is_entity(type):
                return "ENTITY"
            elif self.schema.is_type(type):
                return _make_argument_type(self.schema.types[type].type.type)
            elif isinstance(type, nodes.BinaryType):
                return "UNKNOWN"
            elif isinstance(type, nodes.EnumerationType):
                return "ENUMERATION"
            elif isinstance(type, nodes.SelectType):
                return "ENTITY"
            elif isinstance(type, nodes.AggregationType):
                ty = _make_argument_type(type.type)
                if ty == "UNKNOWN": return "UNKNOWN"
                return "%s_LIST"%ty if ty.startswith("ENTITY") else ("VECTOR_%s"%ty)
            else: raise ValueError
        supported = {'INT', 'BOOL', 'DOUBLE', 'STRING', 'VECTOR_INT', 'VECTOR_DOUBLE', 'VECTOR_STRING', 'ENTITY', 'ENTITY_LIST', 'ENTITY_LIST_LIST', 'ENUMERATION'}
        ty = _make_argument_type(attr.type)
        if ty not in supported: ty = 'UNKNOWN'
        return "IfcUtil::Argument_%s" % ty

    def get_type_dep(self, type):
        if isinstance(type, str):
            return self.express_to_cpp_typemapping.get(type, type)
        else:
            return self.get_type_dep(type.type)

    def get_parameter_type(self, attr, allow_optional, allow_entities, allow_pointer = True):
        type_str = self.express_to_cpp_typemapping.get(str(attr.type), attr.type)
        is_ptr = False
        if self.schema.is_enumeration(attr.type):
            type_str = '%s::%s'%(attr.type, attr.type)
        elif isinstance(type_str, nodes.AggregationType):
            is_nested_list = isinstance(attr.type.type, nodes.AggregationType)
            ty = self.get_parameter_type(attr.type.type if is_nested_list else attr.type, False, allow_entities, allow_pointer=False)
            if allow_entities and self.schema.is_select(attr.type.type):
                type_str = templates.untyped_list
            elif self.schema.is_simpletype(ty) or ty in self.express_to_cpp_typemapping.values():
                type_str = templates.array_type % {
                    'instance_type' : ty,
                    'lower'         : attr.type.bounds.lower,
                    'upper'         : attr.type.bounds.upper
                }
            else:
                tmpl = templates.list_list_type if is_nested_list else templates.list_type
                type_str = tmpl % {
                    'instance_type': ty
                }
        elif allow_pointer and self.schema.is_entity(type_str):
            type_str += '*'
            is_ptr = True
        elif not allow_pointer and self.schema.is_select(type_str):
            type_str = "IfcUtil::IfcAbstractSelect"
            is_ptr = True
        if allow_optional and attr.optional and not is_ptr:
            type_str = "boost::optional< %s >"%type_str
        return type_str

    def argument_count(self, t):
        c = sum([self.argument_count(self.schema.entities[s]) for s in t.supertypes])
        return c + len(t.attributes)

    def arguments(self, t):
        c = sum([self.arguments(self.schema.entities[s]) for s in t.supertypes], [])
        return c + t.attributes

    def derived_in_supertype(self, t):
        c = sum([self.derived_in_supertype(self.schema.entities[s]) for s in t.supertypes], [])
        return c + ([str(s) for s in t.derive.elements] if t.derive else [])

    def list_instance_type(self, attr):
        f = lambda v : 'IfcUtil::IfcAbstractSelect' if self.schema.is_select(v) else v
        if self.is_array(attr.type):
            if not isinstance(attr.type, str) and self.is_array(attr.type.type):
                if isinstance(attr.type.type, str):
                    return f(attr.type.type)
                else: return f(attr.type.type.type)
            else:
                if isinstance(attr.type, str):
                    return f(attr.type)
                else: return f(attr.type.type)
        return None

    def is_templated_list(self, attr):
        ty = self.list_instance_type(attr)
        arr = self.is_array(attr.type)
        simple = self.schema.is_simpletype(ty)
        express = ty in self.express_to_cpp_typemapping
        select = ty == 'IfcUtil::IfcAbstractSelect'
        return arr and not simple and not express and not select

    def get_assignable_arguments(self, t, include_derived = False):
        count = self.argument_count(t)
        num_inherited = count - len(t.attributes)
        derived = set(self.derived_in_supertype(t))
        attrs = enumerate(self.arguments(t))

        def include(attr):
            not_derived = include_derived or (attr.name not in derived)
            supported = self.make_argument_type(attr) != "IfcUtil::Argument_UNKNOWN"
            return not_derived and supported

        return [{
            'index'              : i+1,
            'name'               : attr.name,
            'full_type'          : self.get_parameter_type(attr, allow_optional=True, allow_entities=True),
            'specialized_type'   : self.get_parameter_type(attr, allow_optional=True, allow_entities=False),
            'non_optional_type'  : self.get_parameter_type(attr, allow_optional=False, allow_entities=False),
            'list_instance_type' : self.list_instance_type(attr),
            'is_optional'        : attr.optional,
            'is_inherited'       : i < num_inherited,
            'is_enum'            : attr.type in self.schema.enumerations,
            'is_array'           : self.is_array(attr.type),
            'is_nested'          : self.is_array(attr.type) and not isinstance(attr.type, str) and self.is_array(attr.type.type),
            'is_derived'         : attr.name in derived,
            'is_templated_list'  : self.is_templated_list(attr)
        } for i, attr in attrs if include(attr)]

