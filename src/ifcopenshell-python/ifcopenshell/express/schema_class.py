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
import operator
import re

import nodes
import codegen
import templates
import mapping

from collections import defaultdict

try:
    import ifcopenshell.ifcopenshell_wrapper as w
except:
    pass


class LateBoundSchemaInstantiator:
    def __init__(self, schema_name):
        self.schema_name = schema_name
        self.schema_name_title = schema_name.capitalize()
        self.declarations = {}
        self.names = []
        # We need to make sure anonymous types are not gc'ed.
        self.cache = []

    def aggregation_type(self, aggr_type, bound1, bound2, decl_type):
        self.cache.append(
            w.aggregation_type(getattr(w.aggregation_type, aggr_type + "_type"), bound1, bound2, decl_type)
        )
        return self.cache[-1]

    def simple_type(self, type):
        self.cache.append(w.simple_type(getattr(w.simple_type, type + "_type")))
        return self.cache[-1]

    def named_type(self, type):
        self.cache.append(w.named_type(self.declarations[str(type)]))
        return self.cache[-1]

    def declare(self, definition_type, name):
        self.names.append(str(name))

    def begin_schema(self):
        self.names.sort(key=str.lower)

    def typedef(self, name, declared_type):
        index_in_schema = self.names.index(str(name))
        self.declarations[str(name)] = w.type_declaration(name, index_in_schema, declared_type)

    def enumeration(self, name, enum):
        schema_name = self.schema_name
        index_in_schema = self.names.index(str(name))
        self.declarations[str(name)] = w.enumeration_type(name, index_in_schema, enum.values)

    def entity(self, name, type):
        index_in_schema = self.names.index(str(name))
        supertype = None if len(type.supertypes) == 0 else self.declarations[str(type.supertypes[0])]
        self.declarations[str(name)] = w.entity(name, type.abstract, index_in_schema, supertype)

    def select(self, name, type):
        index_in_schema = self.names.index(str(name))
        children = [self.declarations[str(v)] for v in type.values]
        self.declarations[str(name)] = w.select_type(name, index_in_schema, children)

    def entity_attributes(self, name, attribute_definitions, is_derived):
        attributes = []
        for attr_name, decl_type, optional in attribute_definitions:
            attributes.append(w.attribute(attr_name, decl_type, optional))
        self.declarations[str(name)].set_attributes(attributes, is_derived)
        self.cache.extend(attributes)

    def inverse_attributes(self, name, inv_attrs):
        attributes = []
        for attr_name, aggr_type, bound1, bound2, entity_ref, attribute_entity, attribute_entity_index in inv_attrs:
            en = self.declarations[str(entity_ref)]
            attributes.append(
                w.inverse_attribute(
                    attr_name,
                    getattr(w.inverse_attribute, aggr_type + "_type"),
                    bound1,
                    bound2,
                    en,
                    en.attributes()[attribute_entity_index],
                )
            )
        self.cache.extend(attributes)
        self.declarations[str(name)].set_inverse_attributes(attributes)

    def entity_subtypes(self, name, tys):
        self.declarations[str(name)].set_subtypes([self.declarations[str(v)] for v in tys])

    def finalize(self, can_be_instantiated_set, override_schema_name=None):
        self.schema = w.schema_definition(
            override_schema_name or self.schema_name, list(self.declarations.values()), None
        )

    def disown(self):
        for elem in self.cache + list(self.declarations.values()):
            elem.this.disown()


class string_pool:
    def __init__(self, fn):
        self.di = {}
        self.fn = fn
    def append(self, v):
        def _():
            if i := self.di.get(v):
                return i
            else:
                i = len(self.di)
                self.di[v] = i
                return i
        return self.fn(_())
    def __iter__(self):
        return iter(self.di.keys())


class EarlyBoundCodeWriter:
    def __init__(self, schema_name):
        self.strings = string_pool(lambda i: "strings[%d]" % i)
        self.schema_name = schema_name
        self.schema_name_title = schema_name.capitalize()

        self.statements = [
            "",
            '#include "../ifcparse/IfcSchema.h"',
            '#include "../ifcparse/%(schema_name_title)s.h"' % self.__dict__,
            '#include <string>',
            "",
            'using namespace std::string_literals;',
            "using namespace IfcParse;",
            "",
        ]

        self.names = []

    def aggregation_type(self, aggr_type, bound1, bound2, decl_type):
        return (
            "new aggregation_type(aggregation_type::%(aggr_type)s_type, %(bound1)d, %(bound2)d, %(decl_type)s)"
            % locals()
        )

    def simple_type(self, type):
        return "new simple_type(simple_type::%s_type)" % type

    def named_type(self, type):
        return "new named_type(%s_%s_type)" % (self.schema_name, type)

    def declare(self, definition_type, name):
        schema_name = self.schema_name
        # self.statements.append("%(definition_type)s* %(schema_name)s_%(name)s_type = 0;" % locals())
        self.names.append(name)

    def begin_schema(self):
        self.names.sort(key=str.lower)
        schema_name = self.schema_name
        num_names = len(self.names)
        self.statements.append("declaration* %(schema_name)s_types[%(num_names)d] = {nullptr};" % locals())

        self.statements.append("{string_pool_placeholder}")

        self.statements.append("{factory_placeholder}")

#         self.statements.append(
#             """
# #if defined(__clang__)
# __attribute__((optnone))
# #elif defined(__GNUC__) || defined(__GNUG__)
# #pragma GCC push_options
# #pragma GCC optimize ("O0")
# #elif defined(_MSC_VER)
# #pragma optimize("", off)
# #endif
#         """
#         )
        self.statements.append("IfcParse::schema_definition* %s_populate_schema() {" % self.schema_name)

    def typedef(self, name, declared_type):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        ref = self.strings.append(name)
        self.statements.append(
            '    %(schema_name)s_types[%(index_in_schema)d] = new type_declaration(%(ref)s, %(index_in_schema)d, %(declared_type)s);'
            % locals()
        )

    def enumeration(self, name, enum):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        ref = self.strings.append(name)
        items = ",".join(self.strings.append(v) for v in enum.values)
        self.statements.append(
            '    %(schema_name)s_types[%(index_in_schema)d] = new enumeration_type(%(ref)s, %(index_in_schema)d, {%(items)s});'
            % locals()
        )

    def entity(self, name, type):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        ref = self.strings.append(name)
        supertype = "0" if len(type.supertypes) == 0 else "%s_types[%d]" % (self.schema_name, self.names.index(type.supertypes[0]))
        is_abstract = "true" if type.abstract else "false"
        self.statements.append(
            '    %(schema_name)s_types[%(index_in_schema)d] = new entity(%(ref)s, %(is_abstract)s, %(index_in_schema)d, (entity*) %(supertype)s);'
            % locals()
        )

    def select(self, name, type):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        ref = self.strings.append(name)
        items = ",".join(
            map(lambda v: "%s_types[%d]" % (self.schema_name, self.names.index(v)), sorted(map(str, type.values)))
        )
        self.statements.append(
            '    %(schema_name)s_types[%(index_in_schema)d] = new select_type(%(ref)s, %(index_in_schema)d, {%(items)s});'
            % locals()
        )

    def entity_attributes(self, name, attribute_definitions, is_derived):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        def _():
            index_in_schema = self.names.index(name)
            schema_name = self.schema_name
            for attr_name, decl_type, optional in attribute_definitions:
                attr_name_ref = self.strings.append(attr_name)
                optional_cpp = str(optional).lower()
                yield 'new attribute(%(attr_name_ref)s, %(decl_type)s, %(optional_cpp)s)' % locals()
        attributes = ",".join(_())
        derived = ",".join(map(lambda b: str(b).lower(), is_derived))
        self.statements.append("    ((entity*)%(schema_name)s_types[%(index_in_schema)d])->set_attributes({%(attributes)s}, {%(derived)s});" % locals())

    def inverse_attributes(self, name, inv_attrs):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        def _():
            schema_name = self.schema_name
            index_in_schema = self.names.index(name)
            for attr_name, aggr_type, bound1, bound2, entity_ref, attribute_entity, attribute_entity_index in inv_attrs:
                attr_name_ref = self.strings.append(attr_name)
                opposite_index_in_schema = self.names.index(entity_ref)
                opposite1 = '%(schema_name)s_types[%(opposite_index_in_schema)d]' % locals()
                opposite_index_in_schema = self.names.index(attribute_entity)
                opposite2 = '%(schema_name)s_types[%(opposite_index_in_schema)d]' % locals()
                yield 'new inverse_attribute(%(attr_name_ref)s, inverse_attribute::%(aggr_type)s_type, %(bound1)d, %(bound2)d, ((entity*) %(opposite1)s), ((entity*) %(opposite2)s)->attributes()[%(attribute_entity_index)d])' % locals()
        attributes = ",".join(_())
        self.statements.append("    ((entity*) %(schema_name)s_types[%(index_in_schema)d])->set_inverse_attributes({%(attributes)s});" % locals())

    def entity_subtypes(self, name, tys):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        subtypes = ",".join(map(lambda t: ("((entity*) %%(schema_name)s_types[%d])" % self.names.index(t)), tys)) % locals()
        self.statements.append("    ((entity*) %(schema_name)s_types[%(index_in_schema)d])->set_subtypes({%(subtypes)s});" % locals())

    def finalize(self, can_be_instantiated_set):
        schema_name = self.schema_name
        schema_name_title = self.schema_name.capitalize()
        def _():
            schema_name = self.schema_name
            schema_name_title = self.schema_name.capitalize()
            for type_name in self.names:
                index_in_schema = self.names.index(type_name)
                yield "%(schema_name)s_types[%(index_in_schema)d]" % locals()
        declarations = ",".join(_())
        schema_name_ref = self.strings.append(schema_name)
        self.statements.append(
            '    return new schema_definition(%(schema_name_ref)s, {%(declarations)s}, new %(schema_name)s_instance_factory());'
            % locals()
        )
        self.statements.append("}");

#         self.statements.append(
#             """
# #if defined(__clang__)
# #elif defined(__GNUC__) || defined(__GNUG__)
# #pragma GCC pop_options
# #elif defined(_MSC_VER)
# #pragma optimize("", on)
# #endif
#         """
#         )

        self.statements.extend(
            (
                "static std::unique_ptr<schema_definition> schema;",
                "",
                "void %s::clear_schema() {" % schema_name_title,
                "    schema.reset();",
                "}",
                "",
            )
        )

        self.statements.extend(
            (
                "const schema_definition& %s::get_schema() {" % schema_name_title,
                "    if (!schema) {",
                "        schema.reset(%(schema_name)s_populate_schema());" % locals(),
                "    }",
                "    return *schema;",
                "}",
                "",
                "",
            )
        )

        def can_be_instantiated(idx_name):
            name = idx_name[1]
            return name in can_be_instantiated_set

        instance_mapping = """switch(decl->index_in_schema()) {
            %s
            default: throw IfcParse::IfcException(decl->name() + " cannot be instantiated");
        }
""" % "\n            ".join(
            map(
                lambda tup: ("case %%d: return new ::%s::%%s(std::move(data));" % schema_name_title) % tup,
                filter(can_be_instantiated, enumerate(self.names)),
            )
        )

        self.statements[self.statements.index("{factory_placeholder}")] = (
            """
class %(schema_name)s_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(const IfcParse::declaration* decl, IfcEntityInstanceData&& data) const {
        %(instance_mapping)s
    }
};
"""
            % locals()
        )

        ""
        self.statements[self.statements.index("{string_pool_placeholder}")] = (
            """
const std::string strings[] = {%s};
"""
            % ",".join(map(lambda s: '"%s"s' % s, self.strings))
        )

    def __str__(self):
        return "\n".join(self.statements)


class SchemaClass(codegen.Base):
    def __init__(self, mapping: mapping.Mapping, code=EarlyBoundCodeWriter):
        class UnmetDependenciesException(Exception):
            pass

        schema_name = mapping.schema.name
        self.schema_name = schema_name_title = schema_name.capitalize()

        declared_types = []

        x = code(schema_name)

        def transform_to_indexed(fn):
            def wrapper(*args, **kwargs):
                declared_type = fn(*args, **kwargs)
                if 'simple_type' in declared_type:
                    pass
                else:
                    match = re.search(r'\((\w+?_[\w+]+?_\w+?)\)', declared_type)
                    if match:
                        old_decl = match.group(1)
                        tn = old_decl.rsplit('_', 2)[1]
                        idx = x.names.index(tn)
                        snu = schema_name.upper()
                        declared_type = declared_type.replace(old_decl, '%(snu)s_types[%(idx)d]' % locals())
                return declared_type
            return wrapper if code == EarlyBoundCodeWriter else fn

        @transform_to_indexed
        def get_declared_type(type, emitted_names=None):
            if isinstance(type, nodes.SimpleType):
                type = type.type
            if isinstance(type, nodes.NamedType):
                type = str(type)

            if isinstance(type, nodes.AggregationType):
                aggr_type = type.aggregate_type
                make_bound = lambda b: -1 if b == "?" else int(b)
                bound1, bound2 = map(make_bound, (type.bounds.lower, type.bounds.upper))
                decl_type = get_declared_type(type.type, emitted_names)
                return x.aggregation_type(aggr_type, bound1, bound2, decl_type)
            elif isinstance(type, nodes.BinaryType):
                return x.simple_type("binary")
            elif isinstance(type, nodes.StringType):
                return x.simple_type("string")
            elif isinstance(type, str):
                if mapping.schema.is_type(type) or mapping.schema.is_entity(type):
                    if emitted_names is None or type.lower() in emitted_names:
                        return x.named_type(type)
                    else:
                        raise UnmetDependenciesException(type)
                else:
                    return x.simple_type(type)
            else:
                raise ValueError("No declared type for <%r>" % type)

        def find_inverse_name_and_index(entity_name, attribute_name):
            entity_name_orig = entity_name
            attributes_per_subtype = []
            while True:
                entity = mapping.schema.entities[entity_name]
                attr_names = list(map(operator.attrgetter("name"), entity.attributes))
                if len(attr_names):
                    attributes_per_subtype.append((entity_name, attr_names))
                if len(entity.supertypes) != 1:
                    break
                entity_name = entity.supertypes[0]
            index = 0
            for et, attrs in attributes_per_subtype[::-1]:
                try:
                    return et, attrs.index(attribute_name)
                except:
                    pass

            else:
                raise Exception("No attribute named %s.%s" % (entity_name_orig, attribute_name))

        collections_by_type = (
            ("entity", mapping.schema.entities),
            ("type_declaration", mapping.schema.simpletypes),
            ("select_type", mapping.schema.selects),
            ("enumeration_type", mapping.schema.enumerations),
        )

        for definition_type, collection in collections_by_type:
            for name in collection.keys():
                x.declare(definition_type, name)

        declarations_by_index = []

        x.begin_schema()

        emitted = set()
        len_to_emit = len(mapping.schema) - len(mapping.schema.rules) - len(mapping.schema.functions)

        def write_simpletype(schema_name, name, type):
            try:
                declared_type = get_declared_type(type, emitted)
            except UnmetDependenciesException:
                # @todo?
                # print("Unmet", repr(name))
                return False

            x.typedef(name, declared_type)

        def write_enumeration(schema_name, name, enum):
            x.enumeration(name, enum)

        def write_entity(schema_name, name, type):
            if len(type.supertypes) == 0 or set(map(lambda s: s.lower(), type.supertypes)) < emitted:
                x.entity(name, type)
            else:
                return False

        def write_select(schema_name, name, type):
            if set(map(lambda s: str(s).lower(), type.values)) < emitted:
                x.select(name, type)
            else:
                return False

        def write(name):
            if mapping.schema.is_simpletype(name):
                fn = write_simpletype
            elif mapping.schema.is_enumeration(name):
                fn = write_enumeration
            elif mapping.schema.is_entity(name):
                fn = write_entity
            elif mapping.schema.is_select(name):
                fn = write_select
            elif name in mapping.schema.rules:
                return
            elif name in mapping.schema.functions:
                return

            decl = mapping.schema[name]
            if isinstance(decl, nodes.TypeDeclaration):
                decl = decl.type
            return fn(schema_name, name, decl) is not False

        while len(emitted) < len_to_emit:
            for name in mapping.schema:
                if name.lower() in emitted:
                    continue
                if write(name):
                    emitted.add(name.lower())
                    declarations_by_index.append(name)

        num_declarations = len(emitted)

        for name, type in mapping.schema.entities.items():
            derived = set(mapping.derived_in_supertype(type))
            attribute_names = list(map(operator.attrgetter("name"), mapping.arguments(type)))
            is_derived = [b in derived for b in attribute_names]
            attribute_definitions = []
            for attr in type.attributes:
                decl_type = get_declared_type(attr.type)
                attribute_definitions.append((attr.name, decl_type, attr.optional))
            x.entity_attributes(name, attribute_definitions, is_derived)

        for name, type in mapping.schema.entities.items():
            if type.inverse:
                inv_attrs = []
                for attr in type.inverse:
                    if attr.bounds:
                        make_bound = lambda b: -1 if b == "?" else int(b)
                        bound1, bound2 = map(make_bound, (attr.bounds.lower, attr.bounds.upper))
                    else:
                        bound1, bound2 = -1, -1
                    attr_name, aggr_type, entity_ref = attr.name, attr.type, attr.entity
                    if aggr_type is None:
                        aggr_type = "unspecified"
                    attribute_entity, attribute_entity_index = find_inverse_name_and_index(entity_ref, attr.attribute)
                    inv_attrs.append(
                        (attr_name, aggr_type, bound1, bound2, entity_ref, attribute_entity, attribute_entity_index)
                    )
                x.inverse_attributes(name, inv_attrs)

        subtypes = defaultdict(list)

        for name, type in mapping.schema.entities.items():
            for ty in type.supertypes:
                subtypes[ty].append(name)

        for name, tys in subtypes.items():
            x.entity_subtypes(name, tys)

        can_be_instantiated_set = set(
            list(mapping.schema.entities.keys())
            + list(mapping.schema.simpletypes.keys())
            + list(mapping.schema.enumerations.keys())
        )

        x.finalize(can_be_instantiated_set)

        self.str = str(x)
        self.file_name = "%s-schema.cpp" % self.schema_name
        self.code = x

    def __repr__(self):
        return self.str


Generator = SchemaClass
