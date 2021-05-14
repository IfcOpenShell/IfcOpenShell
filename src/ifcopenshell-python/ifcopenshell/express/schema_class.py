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

import operator

import nodes
import codegen
import templates

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
        self.declarations[str(name)] = w.enumeration_type(name, index_in_schema, sorted(enum.values))

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
        self.cache.append(attributes)

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
        self.declarations[str(name)].set_inverse_attributes(attributes)

    def entity_subtypes(self, name, tys):
        self.declarations[str(name)].set_subtypes([self.declarations[str(v)] for v in tys])

    def finalize(self, can_be_instantiated_set, override_schema_name=None):
        self.schema = w.schema_definition(
            override_schema_name or self.schema_name, list(self.declarations.values()), None
        )


class EarlyBoundCodeWriter:
    def __init__(self, schema_name):
        self.schema_name = schema_name
        self.schema_name_title = schema_name.capitalize()

        self.statements = [
            "",
            '#include "../ifcparse/IfcSchema.h"',
            '#include "../ifcparse/%(schema_name_title)s.h"' % self.__dict__,
            "",
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
        self.statements.append("%(definition_type)s* %(schema_name)s_%(name)s_type = 0;" % locals())
        self.names.append(name)

    def begin_schema(self):
        self.names.sort(key=str.lower)

        self.statements.append("{factory_placeholder}")

        self.statements.append(
            """
#if defined(__clang__)
__attribute__((optnone))
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC push_options
#pragma GCC optimize ("O0")
#elif defined(_MSC_VER)
#pragma optimize("", off)
#endif
        """
        )
        self.statements.append("IfcParse::schema_definition* %s_populate_schema() {" % self.schema_name)

    def typedef(self, name, declared_type):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        self.statements.append(
            '    %(schema_name)s_%(name)s_type = new type_declaration("%(name)s", %(index_in_schema)d, %(declared_type)s);'
            % locals()
        )

    def enumeration(self, name, enum):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        self.statements.append("    {")
        self.statements.append("        std::vector<std::string> items; items.reserve(%d);" % len(enum.values))
        self.statements.extend(map(lambda v: '        items.push_back("%s");' % v, sorted(enum.values)))
        self.statements.append(
            '        %(schema_name)s_%(name)s_type = new enumeration_type("%(name)s", %(index_in_schema)d, items);'
            % locals()
        )
        self.statements.append("    }")

    def entity(self, name, type):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        supertype = "0" if len(type.supertypes) == 0 else "%s_%s_type" % (self.schema_name, type.supertypes[0])
        is_abstract = "true" if type.abstract else "false"
        self.statements.append(
            '    %(schema_name)s_%(name)s_type = new entity("%(name)s", %(is_abstract)s, %(index_in_schema)d, %(supertype)s);'
            % locals()
        )

    def select(self, name, type):
        schema_name = self.schema_name
        index_in_schema = self.names.index(name)
        self.statements.append("    {")
        self.statements.append("        std::vector<const declaration*> items; items.reserve(%d);" % len(type.values))
        self.statements.extend(
            map(lambda v: "        items.push_back(%s_%s_type);" % (self.schema_name, v), sorted(map(str, type.values)))
        )
        self.statements.append(
            '        %(schema_name)s_%(name)s_type = new select_type("%(name)s", %(index_in_schema)d, items);'
            % locals()
        )
        self.statements.append("    }")

    def entity_attributes(self, name, attribute_definitions, is_derived):
        schema_name = self.schema_name
        self.statements.append("    {")
        self.statements.append(
            "        std::vector<const attribute*> attributes; attributes.reserve(%d);" % len(attribute_definitions)
        )
        for attr_name, decl_type, optional in attribute_definitions:
            optional_cpp = str(optional).lower()
            self.statements.append(
                '        attributes.push_back(new attribute("%(attr_name)s", %(decl_type)s, %(optional_cpp)s));'
                % locals()
            )
        self.statements.append("        std::vector<bool> derived; derived.reserve(%d);" % len(is_derived))
        self.statements.append(
            "        " + " ".join(map(lambda b: "derived.push_back(%s);" % str(b).lower(), is_derived))
        )
        self.statements.append("        %(schema_name)s_%(name)s_type->set_attributes(attributes, derived);" % locals())
        self.statements.append("    }")

    def inverse_attributes(self, name, inv_attrs):
        schema_name = self.schema_name
        self.statements.append("    {")
        self.statements.append(
            "        std::vector<const inverse_attribute*> attributes; attributes.reserve(%d);" % len(inv_attrs)
        )
        for attr_name, aggr_type, bound1, bound2, entity_ref, attribute_entity, attribute_entity_index in inv_attrs:
            self.statements.append(
                '        attributes.push_back(new inverse_attribute("%(attr_name)s", inverse_attribute::%(aggr_type)s_type, %(bound1)d, %(bound2)d, %(schema_name)s_%(entity_ref)s_type, %(schema_name)s_%(attribute_entity)s_type->attributes()[%(attribute_entity_index)d]));'
                % locals()
            )
        self.statements.append("        %(schema_name)s_%(name)s_type->set_inverse_attributes(attributes);" % locals())
        self.statements.append("    }")

    def entity_subtypes(self, name, tys):
        schema_name = self.schema_name
        self.statements.append("    {")
        self.statements.append("        std::vector<const entity*> defs; defs.reserve(%d);" % len(tys))
        self.statements.append(
            ("        " + "".join(map(lambda t: ("defs.push_back(%%(schema_name)s_%s_type);" % t), tys))) % locals()
        )
        self.statements.append("        %(schema_name)s_%(name)s_type->set_subtypes(defs);" % locals())
        self.statements.append("    }")

    def finalize(self, can_be_instantiated_set):
        schema_name = self.schema_name
        schema_name_title = self.schema_name.capitalize()

        num_declarations = len(self.names)

        self.statements.append("")
        self.statements.append(
            "    std::vector<const declaration*> declarations; declarations.reserve(%(num_declarations)d);" % locals()
        )
        for type_name in self.names:
            self.statements.append("    declarations.push_back(%(schema_name)s_%(type_name)s_type);" % locals())

        self.statements.append(
            '    return new schema_definition("%(schema_name)s", declarations, new %(schema_name)s_instance_factory());'
            % locals()
        )

        self.statements.extend(("}", ""))

        self.statements.append(
            """
#if defined(__clang__)
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC pop_options
#elif defined(_MSC_VER)
#pragma optimize("", on)
#endif
        """
        )

        self.statements.extend(
            (
                "const schema_definition& %s::get_schema() {" % schema_name_title,
                "",
                "    static const schema_definition* s = %(schema_name)s_populate_schema();" % locals(),
                "    return *s;",
                "}",
                "",
                "",
            )
        )

        def can_be_instantiated(idx_name):
            name = idx_name[1]
            return name in can_be_instantiated_set

        instance_mapping = """switch(data->type()->index_in_schema()) {
            %s
            default: throw IfcParse::IfcException(data->type()->name() + " cannot be instantiated");
        }
""" % "\n            ".join(
            map(
                lambda tup: ("case %%d: return new ::%s::%%s(data);" % schema_name_title) % tup,
                filter(can_be_instantiated, enumerate(self.names)),
            )
        )

        self.statements[self.statements.index("{factory_placeholder}")] = (
            """
class %(schema_name)s_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        %(instance_mapping)s
    }
};
"""
            % locals()
        )

    def __str__(self):
        return "\n".join(self.statements)


class SchemaClass(codegen.Base):
    def __init__(self, mapping, code=EarlyBoundCodeWriter):
        class UnmetDependenciesException(Exception):
            pass

        schema_name = mapping.schema.name
        self.schema_name = schema_name_title = schema_name.capitalize()

        declared_types = []

        x = code(schema_name)

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
                raise ValueError("No mapping for '%s'" % type)

        def find_inverse_name_and_index(entity_name, attribute_name):
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
                raise Exception("No declared type for <%r>" % type)

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
        len_to_emit = len(mapping.schema)

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
                    declared_types.append("%(schema_name)s_%(name)s_type" % locals())

        num_declarations = len(declared_types)

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

        can_be_instantiated_set = set(list(mapping.schema.entities.keys()) + \
            list(mapping.schema.simpletypes.keys()) + \
            list(mapping.schema.enumerations.keys()))
            
        x.finalize(can_be_instantiated_set)

        self.str = str(x)
        self.file_name = "%s-schema.cpp" % self.schema_name
        self.code = x

    def __repr__(self):
        return self.str


Generator = SchemaClass
