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


import codegen
import templates

from schema import OrderedCaseInsensitiveDict


class Implementation(codegen.Base):
    def __init__(self, mapping):
        enumeration_functions = []
        entity_implementations = []
        schema_entity_statements = []

        schema_name = mapping.schema.name.capitalize()
        schema_name_upper = mapping.schema.name.upper()

        stringify = lambda s: '"%s"' % s
        cat = lambda vs: "".join(vs)
        catc = lambda vs: ", ".join(vs)
        catnl = lambda vs: "\n".join(vs)
        cator = lambda vs: " || ".join(vs)
        nl = lambda s: "%s\n" % s if len(s) else s

        write = lambda str, **kwargs: enumeration_functions.append(str % kwargs)

        collections_by_type = (
            ("entity", mapping.schema.entities),
            ("type_declaration", mapping.schema.simpletypes),
            ("select_type", mapping.schema.selects),
            ("enumeration_type", mapping.schema.enumerations),
        )
        self.names = []
        for _, collection in collections_by_type:
            self.names.extend(collection.keys())
        self.names.sort(key=str.lower)

        for name, enum in mapping.schema.enumerations.items():
            short_name = name[:-4] if name.endswith("Enum") else name
            context = locals()
            write(
                templates.enumeration_function,
                max_id=len(enum.values),
                name=name,
                schema_name=schema_name,
                schema_name_upper=schema_name_upper,
                index_in_schema=self.names.index(str(name)),
                values=catc(map(stringify, enum.values)),
                from_string_statements=catnl(
                    templates.enum_from_string_stmt % dict(context, **locals()) for value in enum.values
                ),
            )
            
        for name, enum in mapping.schema.selects.items():
            write(
                templates.select_function,
                name=name,
                schema_name=schema_name,
                schema_name_upper=schema_name_upper,
                index_in_schema=self.names.index(str(name)),
            )

        write = lambda str, **kwargs: entity_implementations.append(str % kwargs)

        for name, type in mapping.schema.entities.items():
            parent_type_test = (
                ""
                if not type.supertypes or len(type.supertypes) != 1
                else templates.parent_type_test % (type.supertypes[0])
            )

            constructor_arguments = mapping.get_assignable_arguments(type, include_derived=True)
            constructor_arguments_str = catc(
                "%(full_type)s v%(index)d_%(name)s" % a for a in constructor_arguments if not a["is_derived"]
            )
            attributes = []
            constructor_implementations = []
            write_attr = lambda str, **kwargs: attributes.append(str % kwargs)
            for arg in constructor_arguments:
                if not arg["is_inherited"] and not arg["is_derived"]:

                    def find_template(arg):
                        simple = mapping.schema.is_simpletype(arg["list_instance_type"])
                        express = (
                            mapping.flatten_type_string(arg["list_instance_type"]) in mapping.express_to_cpp_typemapping
                        )
                        if arg["is_enum"]:
                            return templates.get_attr_stmt_enum
                        elif arg["is_nested"] and arg["is_templated_list"]:
                            return templates.get_attr_stmt_nested_array
                        elif arg["is_templated_list"] and not (simple or express):
                            return templates.get_attr_stmt_array
                        elif arg["non_optional_type"].endswith("*"):
                            return templates.get_attr_stmt_entity
                        else:
                            return templates.get_attr_stmt

                    null_check = ""
                    if arg["is_optional"]:
                        attr_check = (
                            "if(data_.get_attribute_value(%d).isNull()) { return %%s; }"
                            % (arg["index"] - 1,)
                        )
                        if "boost::optional" in arg["full_type"]:
                            null_check = attr_check % "boost::none"
                        else:
                            null_check = attr_check % "nullptr"

                    tmpl = find_template(arg)
                    write_attr(
                        templates.const_function,
                        class_name=name,
                        name=arg["name"],
                        arguments="",
                        schema_name=schema_name,
                        schema_name_upper=schema_name_upper,
                        return_type=arg["full_type"],
                        body=tmpl
                        % {
                            "index": arg["index"] - 1,
                            "type": arg["full_type"].replace("::Value", ""),
                            "non_optional_type": arg["non_optional_type"].replace("::Value", ""),
                            "non_optional_type_no_pointer": arg["non_optional_type"]
                            .replace("::Value", "")
                            .replace("*", ""),
                            "list_instance_type": arg["list_instance_type"],
                            "null_check": null_check,
                        },
                    )

                    def find_template(arg):
                        simple = mapping.schema.is_simpletype(arg["list_instance_type"])
                        select = arg["list_instance_type"] == "IfcUtil::IfcBaseClass"
                        express = arg["list_instance_type"] in mapping.express_to_cpp_typemapping
                        if arg["is_enum"]:
                            return templates.set_attr_stmt_enum
                        elif arg["is_templated_list"] and not (select or simple or express):
                            return templates.set_attr_stmt_array
                        elif arg["full_type"].endswith('*'):
                            return templates.set_attr_instance
                        else:
                            return templates.set_attr_stmt

                    tmpl = find_template(arg)
                    write_attr(
                        templates.function,
                        class_name=name,
                        name="set%s" % arg["name"],
                        arguments="%s v" % arg["full_type"],
                        return_type="void",
                        schema_name=schema_name,
                        schema_name_upper=schema_name_upper,
                        body=tmpl
                        % {
                            "index": arg["index"] - 1,
                            "type": arg["full_type"].replace("::Value", ""),
                            "non_optional_type": arg["non_optional_type"].replace("::Value", ""),
                            "star_if_optional": "*" if "boost::optional" in arg["full_type"] else "",
                            "check_optional_set_begin": "if (v) {" if "boost::optional" in arg["full_type"] else "",
                            "check_optional_set_else": "} else {" if "boost::optional" in arg["full_type"] else "if constexpr (false)",
                            "check_optional_set_end": "}" if "boost::optional" in arg["full_type"] else "",
                        },
                    )

                if arg["is_derived"]:
                    constructor_implementations.append(templates.constructor_stmt_derived % {"index": arg["index"] - 1})
                else:
                    is_optional_non_naked_ptr = arg["is_optional"] and not arg["non_optional_type"].endswith("*")
                    arg_name = "v%(index)d_%(name)s" % arg
                    deref_name = ("*%s" % arg_name) if is_optional_non_naked_ptr else arg_name

                    tmpl = (
                        templates.constructor_stmt_array
                        if arg["is_templated_list"]
                        else templates.constructor_stmt_enum
                        if arg["is_enum"]
                        else templates.constructor_stmt_instance
                        if arg["full_type"].endswith('*')
                        else templates.constructor_stmt
                    )
                    impl = tmpl % {
                        "name": deref_name,
                        "index": arg["index"] - 1,
                        "type": arg["non_optional_type"].replace("::Value", ""),
                    }
                    if is_optional_non_naked_ptr:
                        impl = templates.constructor_stmt_optional % {
                            "name": arg_name,
                            "index": arg["index"] - 1,
                            "stmt": impl,
                        }
                    constructor_implementations.append(impl)

            def get_attribute_index(entity, attr_name):
                related_entity = mapping.schema.entities[entity]
                return [
                    a["name"].lower() for a in mapping.get_assignable_arguments(related_entity, include_derived=True)
                ].index(attr_name.lower())

            inverse = [
                templates.const_function
                % {
                    "class_name": name,
                    "schema_name": schema_name,
                    "schema_name_upper": schema_name_upper,
                    "name": i.name,
                    "arguments": "",
                    "return_type": "::%s::%s::list::ptr" % (schema_name, i.entity),
                    "body": templates.get_inverse
                    % {
                        "type": i.entity,
                        "type_index": self.names.index(i.entity),
                        "index": get_attribute_index(i.entity, i.attribute),
                        "schema_name": schema_name,
                        "schema_name_upper": schema_name_upper,
                    },
                }
                for i in type.inverse
            ]

            superclass = (
                "%s(std::move(e))" % type.supertypes[0]
                if len(type.supertypes) == 1
                else "IfcUtil::IfcBaseEntity(std::move(e))"
            )

            superclass_num_attrs = (
                "%s(IfcEntityInstanceData(storage_t(%%d)))" % type.supertypes[0]
                if len(type.supertypes) == 1
                else "IfcUtil::IfcBaseEntity(IfcEntityInstanceData(storage_t(%d)))"
            ) % len(constructor_arguments)

            write(
                templates.entity_implementation,
                name=name,
                parent_type_test=parent_type_test,
                constructor_arguments=constructor_arguments_str,
                constructor_implementation=cat(constructor_implementations),
                attributes=nl(catnl(attributes)),
                inverse=nl(catnl(inverse)),
                superclass=superclass,
                superclass_num_attrs=superclass_num_attrs,
                schema_name=schema_name,
                schema_name_upper=schema_name_upper,
                index_in_schema=self.names.index(str(name)),
            )

        selectable_simple_types = sorted(
            set(sum([b.values for a, b in mapping.schema.selects.items()], []))
            & set(map(str, mapping.schema.types.keys()))
        )
        schema_entity_statements += [
            templates.schema_entity_stmt % locals() for name, type in mapping.schema.simpletypes.items()
        ]
        schema_entity_statements += [
            templates.schema_entity_stmt % locals() for name, type in mapping.schema.enumerations.items()
        ]
        schema_entity_statements += [
            templates.schema_entity_stmt % locals() for name, type in mapping.schema.entities.items()
        ]

        enumerable_types = sorted(
            set(
                [name for name, type in mapping.schema.types.items()]
                + [name for name, type in mapping.schema.entities.items()]
            )
        )
        max_len = max(map(len, enumerable_types))
        type_name_strings = catc(map(stringify, enumerable_types))
        string_map_statements = [
            templates.string_map_statement
            % {"uppercase_name": name.upper(), "name": name, "padding": " " * (max_len - len(name))}
            for name in enumerable_types
        ]

        enumeration_index_by_str = OrderedCaseInsensitiveDict((j, i) for i, j in enumerate(enumerable_types))

        def get_parent_id(s):
            e = mapping.schema.entities.get(s)
            if e and e.supertypes:
                return enumeration_index_by_str[e.supertypes[0]]
            else:
                return -1

        parent_type_statements = ",".join(map(str, map(get_parent_id, enumerable_types)))

        max_id = len(enumerable_types)

        simple_type_statements = cator("v == Type::%s" % name for name in selectable_simple_types)

        simple_type_impl = []
        for class_name, type in mapping.schema.simpletypes.items():
            type_str = mapping.make_type_string(mapping.flatten_type_string(type))
            attr_type = mapping.make_argument_type(type)
            superclass = mapping.simple_type_parent(class_name) or "IfcUtil::IfcBaseType"

            simpletype_impl_is = (
                templates.simpletype_impl_is_with_supertype
                if superclass
                else templates.simpletype_impl_is_without_supertype
            )

            constructor = templates.constructor_single_initlist#  if superclass else templates.constructor

            simpletype_impl_cast = (
                templates.simpletype_impl_cast_templated
                if mapping.is_templated_list(type)
                else templates.simpletype_impl_cast
            )

            simpletype_impl_constructor = (
                templates.simpletype_impl_constructor_templated
                if mapping.is_templated_list(type)
                else templates.simpletype_impl_constructor
            )

            def compose(params, schema_name=schema_name, schema_name_upper=schema_name_upper):
                class_name, attr_type, superclass, superclass_init, name, tmpl, return_type, args, body = params
                index_in_schema = self.names.index(str(class_name))
                underlying_type = mapping.list_instance_type(type)
                arguments = ",".join(args)
                body = body % locals()
                return tmpl % locals()

            simple_type_impl.append(templates.simpletype_impl_comment % {"name": class_name})
            simple_type_impl.extend(
                map(
                    compose,
                    map(
                        lambda x: (class_name, attr_type, superclass) + x,
                        (
                            (
                                "",
                                "Class",
                                templates.function,
                                "const IfcParse::type_declaration&",
                                (),
                                templates.simpletype_impl_class,
                            ),
                            (
                                "",
                                "declaration",
                                templates.const_function,
                                "const IfcParse::type_declaration&",
                                (),
                                templates.simpletype_impl_declaration,
                            ),
                            (
                                "std::move(e)",
                                "",
                                constructor,
                                "",
                                ("IfcEntityInstanceData&& e",),
                                "",
                            ),
                            ("", "", constructor, "", ("%s v" % type_str,), ("set_attribute_value(0, v%s);" % ("->generalize()" if mapping.is_templated_list(type) else ""))) if mapping.simple_type_parent(class_name) is None else \
                            ("v", "", constructor, "", ("%s v" % type_str,), ""),
                            ("", "", templates.cast_function, type_str, (), simpletype_impl_cast),
                        ),
                    ),
                )
            )
            simple_type_impl.append("")

        """
        external_definitions = (
            [("extern entity* %s_%%s_type;" % schema_name_upper) % n for n in mapping.schema.entities.keys()]
            + [
                ("extern type_declaration* %s_%%s_type;" % schema_name_upper) % n
                for n in mapping.schema.simpletypes.keys()
            ]
            + [
                ("extern enumeration_type* %s_%%s_type;" % schema_name_upper) % n
                for n in mapping.schema.enumerations.keys()
            ]
            + [
                ("extern select_type* %s_%%s_type;" % schema_name_upper) % n
                for n in mapping.schema.selects.keys()
            ]
        )
        """
        external_definitions = ["extern declaration* %s_types[%d];" % (schema_name_upper, len(self.names))]

        self.str = templates.implementation % {
            "schema_name_upper": schema_name_upper,
            "schema_name": schema_name,
            "max_id": max_id,
            "enumeration_functions": cat(enumeration_functions),
            "schema_entity_statements": catnl(schema_entity_statements),
            "type_name_strings": type_name_strings,
            "string_map_statements": catnl(string_map_statements),
            "simple_type_statement": simple_type_statements,
            "parent_type_statements": parent_type_statements,
            "entity_implementations": catnl(entity_implementations),
            "simple_type_impl": catnl(simple_type_impl),
            "external_definitions": catnl(external_definitions),
        }

        self.schema_name = mapping.schema.name.capitalize()

        self.file_name = "%s.cpp" % self.schema_name

    def __repr__(self):
        return self.str


Generator = Implementation
