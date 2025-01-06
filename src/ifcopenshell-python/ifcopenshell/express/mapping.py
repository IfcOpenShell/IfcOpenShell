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


from __future__ import annotations
import sys
import nodes
import templates
import schema


class Mapping:

    express_to_cpp_typemapping = {
        "boolean": "bool",
        "logical": "boost::logic::tribool",
        "integer": "int",
        "real": "double",
        "number": "double",
        "string": "std::string",
        "binary": "boost::dynamic_bitset<>",
    }

    supported_argument_types = set(
        [
            "INT",
            "BOOL",
            "LOGICAL",
            "DOUBLE",
            "STRING",
            "BINARY",
            "ENUMERATION",
            "ENTITY_INSTANCE",
            "AGGREGATE_OF_INT",
            "AGGREGATE_OF_DOUBLE",
            "AGGREGATE_OF_STRING",
            "AGGREGATE_OF_BINARY",
            "AGGREGATE_OF_ENTITY_INSTANCE",
            "AGGREGATE_OF_AGGREGATE_OF_INT",
            "AGGREGATE_OF_AGGREGATE_OF_DOUBLE",
            "AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE",
        ]
    )

    def __init__(self, schema: schema.Schema):
        self.schema = schema

    def flatten_type_string(self, type):
        return self.flatten_type_string(self.schema.types[type].type) if self.schema.is_simpletype(type) else type

    def flatten_type(self, type):
        res = self.flatten_type(self.schema.types[type].type) if self.schema.is_simpletype(type) else type
        return res

    def simple_type_parent(self, type):
        parent = self.schema.types[type].type
        if isinstance(parent, (nodes.AggregationType, nodes.StringType)) or (
            isinstance(parent, nodes.SimpleType) and isinstance(parent.type, nodes.StringType)
        ):
            return None
        if str(parent) in self.express_to_cpp_typemapping:
            return None
        return str(parent)

    def make_type_string(self, type):
        if isinstance(type, nodes.StringType) or (
            isinstance(type, nodes.SimpleType) and isinstance(type.type, nodes.StringType)
        ):
            type = "string"
        if isinstance(type, (str, nodes.BinaryType, nodes.SimpleType, nodes.NamedType)):
            return self.express_to_cpp_typemapping.get(str(type), "::%s::%s" % (self.schema.name.capitalize(), type))
        else:
            if type.bounds is None:
                import pdb

                pdb.set_trace()
            is_list = self.schema.is_entity(type.type)
            is_nested_list = isinstance(type.type, nodes.AggregationType)
            tmpl = (
                templates.list_list_type if is_nested_list else templates.list_type if is_list else templates.array_type
            )
            return tmpl % {
                "instance_type": self.make_type_string(self.flatten_type_string(type.type)),
                "lower": type.bounds.lower,
                "upper": type.bounds.upper,
            }

    def is_array(self, type):
        if isinstance(type, nodes.AggregationType):
            return True
        elif isinstance(type, str) and self.schema.is_type(type):
            return self.is_array(self.schema.types[type].type)
        else:
            return False

    def make_argument_entity(self, attr):
        type = attr.type if hasattr(attr, "type") else attr
        while isinstance(type, nodes.AggregationType):
            type = type.type
        if str(type) in self.express_to_cpp_typemapping:
            return "Type::UNDEFINED"
        else:
            return "Type::%s" % type

    def make_argument_type(self, attr):
        def _make_argument_type(type):
            if isinstance(type, nodes.SimpleType):
                type = type.type
            if self.schema.is_entity(type) or isinstance(type, nodes.SelectType):
                return "ENTITY_INSTANCE"
            elif isinstance(type, nodes.BinaryType):
                return "BINARY"
            elif isinstance(type, nodes.StringType):
                return "STRING"
            elif isinstance(type, nodes.EnumerationType):
                return "ENUMERATION"
            elif isinstance(type, nodes.AggregationType):
                ty = _make_argument_type(type.type)
                if ty == "UNKNOWN":
                    return "UNKNOWN"
                return "AGGREGATE_OF_" + ty
            elif str(type) in self.express_to_cpp_typemapping:
                return self.express_to_cpp_typemapping.get(str(type), type).split("::")[-1].upper()
            elif self.schema.is_type(type):
                return _make_argument_type(self.schema.types[type].type)
            else:
                raise ValueError("Unable to map type %r for attribute %r" % (type, attr))

        ty = _make_argument_type(attr.type if hasattr(attr, "type") else attr)
        if ty == "TRIBOOL":
            ty = "LOGICAL"

        if ty not in self.supported_argument_types:
            import pdb

            pdb.set_trace()
            print("Attribute %r mapped as 'unknown'" % (attr), file=sys.stderr)
            ty = "UNKNOWN"
        return "IfcUtil::Argument_%s" % ty

    def get_type_dep(self, type):
        if isinstance(type, str):
            return self.express_to_cpp_typemapping.get(str(type), type)
        else:
            return self.get_type_dep(type.type)

    def get_parameter_type(self, attr, allow_optional=True):
        attr_type = self.flatten_type(attr.type)

        if (isinstance(attr_type, nodes.SimpleType) and isinstance(attr_type.type, nodes.StringType)) or isinstance(
            attr_type, nodes.StringType
        ):
            type_str = self.express_to_cpp_typemapping["string"]
        else:
            type_str = self.express_to_cpp_typemapping.get(str(attr_type), attr_type)

        is_ptr = False

        if self.schema.is_enumeration(attr_type):
            type_str = "::%s::%s::Value" % (self.schema.name.capitalize(), attr_type)
        elif isinstance(type_str, nodes.AggregationType):
            is_nested_list = isinstance(attr_type.type, nodes.AggregationType)
            ty = self.get_parameter_type(attr_type.type if is_nested_list else attr_type)
            # We do not use pointers in aggregate_of<T>. aggregate_of has member vector<T*>
            ty = ty.replace("*", "")

            # https://github.com/IfcOpenShell/IfcOpenShell/issues/2805
            # This is no longer applicable, we do support statically typed select types as aggregates
            #
            # if self.schema.is_select(attr_type.type):
            #     type_str = templates.untyped_list

            if self.schema.is_simpletype(ty) or str(ty) in self.express_to_cpp_typemapping.values():
                tmpl = templates.nested_array_type if is_nested_list else templates.array_type
                bounds = (attr_type.bounds.lower, attr_type.bounds.upper) if attr_type.bounds else (-1, -1)
                type_str = tmpl % {"instance_type": ty, "lower": bounds[0], "upper": bounds[1]}
            else:
                tmpl = templates.list_list_type if is_nested_list else templates.list_type
                type_str = tmpl % {"instance_type": ty}
        elif self.schema.is_entity(type_str) or self.schema.is_select(type_str):
            type_str = "::%s::%s*" % (self.schema.name.capitalize(), attr_type)
            is_ptr = True
        if allow_optional and attr.optional and not is_ptr:
            # pointers are still handled with nullptr for the time being
            type_str = "boost::optional< %s >" % type_str
        return type_str

    def argument_count(self, t):
        c = sum([self.argument_count(self.schema.entities[s]) for s in t.supertypes])
        return c + len(t.attributes)

    def arguments(self, t):
        c = sum([self.arguments(self.schema.entities[s]) for s in t.supertypes], [])
        return c + t.attributes

    def derived_in_supertype(self, t):
        c = sum([self.derived_in_supertype(self.schema.entities[s]) for s in t.supertypes], [])
        derived = c + t.derive
        return [d[0][1] for d in derived if isinstance(d[0], tuple)]

    def list_instance_type(self, attr):
        attr_type = attr.type if isinstance(attr, nodes.ExplicitAttribute) else attr
        if isinstance(attr_type, str):
            return None

        def f(v):
            v = self.flatten_type(v)
            if isinstance(v, (nodes.AggregationType, nodes.StringType)) or (
                isinstance(v, nodes.SimpleType) and isinstance(v.type, nodes.StringType)
            ):
                return "string"
            # if self.schema.is_select(v):
            #     return "IfcUtil::IfcBaseClass"
            if str(v) in self.schema.types or str(v) in self.schema.entities:
                return "::%s::%s" % (self.schema.name.capitalize(), v)
            else:
                return str(v)

        if self.is_array(attr_type):
            if not isinstance(attr_type, str) and self.is_array(attr_type.type):
                if isinstance(attr_type.type, str):
                    return f(attr_type.type)
                else:
                    return f(attr_type.type.type)
            else:
                if isinstance(attr_type, str):
                    return f(attr_type)
                else:
                    return f(attr_type.type)
        return None

    def is_templated_list(self, attr):
        attr_type = attr.type if isinstance(attr, nodes.ExplicitAttribute) else attr
        if isinstance(attr, str):
            return False
        ty = self.list_instance_type(attr)
        if ty is None:
            return False
        arr = self.is_array(attr_type)
        simple = self.schema.is_simpletype(ty)
        express = self.flatten_type_string(ty) in self.express_to_cpp_typemapping
        select = ty == "IfcUtil::IfcBaseClass"
        return arr and not simple and not express and not select

    def get_assignable_arguments(self, t, include_derived=False):
        count = self.argument_count(t)
        num_inherited = count - len(t.attributes)
        derived = set(self.derived_in_supertype(t))
        attrs = enumerate(self.arguments(t))

        def include(attr):
            not_derived = include_derived or (attr.name not in derived)
            supported = self.make_argument_type(attr) != "IfcUtil::Argument_UNKNOWN"
            return not_derived and supported

        return [
            {
                "index": i + 1,
                "name": attr.name,
                "full_type": self.get_parameter_type(attr),
                "specialized_type": self.get_parameter_type(attr),
                "non_optional_type": self.get_parameter_type(attr, allow_optional=False),
                "list_instance_type": self.list_instance_type(attr),
                "is_optional": attr.optional,
                "is_inherited": i < num_inherited,
                "is_enum": attr.type in self.schema.enumerations,
                "is_array": self.is_array(attr.type),
                "is_nested": self.is_array(attr.type)
                and not isinstance(attr.type, str)
                and self.is_array(attr.type.type),
                "is_derived": attr.name in derived,
                "is_templated_list": self.is_templated_list(attr),
                "argument_type_enum": self.make_argument_type(attr),
                "argument_entity": self.make_argument_entity(attr),
                "argument_type": attr.type,
            }
            for i, attr in attrs
            if include(attr)
        ]
