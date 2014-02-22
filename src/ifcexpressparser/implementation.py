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

import templates

class Implementation:
    def __init__(self, mapping):
        enumeration_functions = []
        entity_implementations = []
        schema_entity_statements = []

        schema_name = mapping.schema.name.capitalize()

        stringify = lambda s: '"%s"'%s
        cat = lambda vs: "".join(vs)
        catc = lambda vs: ", ".join(vs)
        catnl = lambda vs: "\n".join(vs)
        cator = lambda vs: " || ".join(vs)
        nl = lambda s: "%s\n"%s if len(s) else s

        write = lambda str, **kwargs: enumeration_functions.append(str%kwargs)

        for name, enum in mapping.schema.enumerations.items():
            short_name = name[:-4] if name.endswith("Enum") else name
            context = locals()
            write(
                templates.enumeration_function,
                max_id = len(enum.values),
                name = name,
                values = catc(map(stringify, enum.values)),
                from_string_statements = catnl(templates.enum_from_string_stmt%dict(context,**locals()) for value in enum.values)
            )

        write = lambda str, **kwargs: entity_implementations.append(str%kwargs)

        for name, type in mapping.schema.entities.items():
            parent_type_test = "" if not type.supertypes or len(type.supertypes) != 1 \
                else templates.parent_type_test%(type.supertypes[0])
            constructor_arguments = mapping.get_assignable_arguments(type, include_derived = True)
            constructor_arguments_str = catc("%(full_type)s v%(index)d_%(name)s"%a for a in constructor_arguments if not a['is_derived'])
            attributes = []
            constructor_implementations = []
            write_attr = lambda str, **kwargs: attributes.append(str%kwargs)
            for arg in constructor_arguments:
                if not arg['is_inherited'] and not arg['is_derived']:
                    if arg['is_optional']:
                        write_attr(
                            templates.function,
                            class_name  = name,
                            name        = 'has%s'%arg['name'],
                            arguments   = '',
                            return_type = 'bool',
                            body        = templates.optional_attr_stmt % {'index':arg['index']-1}
                        )

                    tmpl = templates.get_attr_stmt_enum if arg['is_enum'] else templates.get_attr_stmt_array if arg['is_array'] and not mapping.schema.is_simpletype(arg['list_instance_type']) and arg['list_instance_type'] not in mapping.express_to_cpp_typemapping else templates.get_attr_stmt_entity if arg['non_optional_type'].endswith('*') else templates.get_attr_stmt
                    write_attr(
                        templates.function,
                        class_name  = name,
                        name        = arg['name'],
                        arguments   = '',
                        return_type = arg['non_optional_type'],
                        body        = tmpl % {'index': arg['index']-1,
                                              'type' : arg['non_optional_type'].split('::')[0],
                                              'list_instance_type' : arg['list_instance_type']}
                    )

                    tmpl = templates.set_attr_stmt_enum if arg['is_enum'] else templates.set_attr_stmt_array if arg['is_array'] and not mapping.schema.is_simpletype(arg['list_instance_type']) and arg['list_instance_type'] not in mapping.express_to_cpp_typemapping else templates.set_attr_stmt
                    write_attr(
                        templates.function,
                        class_name  = name,
                        name        = 'set%s'%arg['name'],
                        arguments   = '%s v'%arg['non_optional_type'],
                        return_type = 'void',
                        body        = tmpl % {'index': arg['index']-1,
                                              'type' : arg['non_optional_type'].split('::')[0]}
                    )

                if arg['is_derived']:
                    constructor_implementations.append(templates.constructor_stmt_derived % {'index' : arg['index']-1})
                else:
                    is_optional_non_naked_ptr = arg['is_optional'] and not arg['non_optional_type'].endswith('*')
                    arg_name = "v%(index)d_%(name)s"%arg
                    deref_name = ("*%s"%arg_name) if is_optional_non_naked_ptr else arg_name

                    tmpl = templates.constructor_stmt_array if arg['is_templated_list'] \
                        else templates.constructor_stmt_enum if arg['is_enum'] \
                        else templates.constructor_stmt
                    impl = tmpl % {'name'  : deref_name,
                                   'index' : arg['index']-1,
                                   'type'  : arg['non_optional_type'].split('::')[0]}
                    if is_optional_non_naked_ptr:
                        impl = templates.constructor_stmt_optional%{'name'  : arg_name,
                                                            'index' : arg['index']-1,
                                                            'stmt'  : impl}
                    constructor_implementations.append(impl)

            inverse = [templates.function % {
                'class_name'  : name,
                'name'        : i.name,
                'arguments'   : '',
                'return_type' : '%s::list' % i.entity,
                'body'        : templates.get_inverse % {'type': i.entity}
            } for i in (type.inverse.elements if type.inverse else [])]

            superclass = "%s((IfcAbstractEntityPtr)0)" % type.supertypes[0] if len(type.supertypes) == 1 else 'IfcUtil::IfcBaseEntity()'

            write(
                templates.entity_implementation,
                name                       = name,
                parent_type_test           = parent_type_test,
                constructor_arguments      = constructor_arguments_str,
                constructor_implementation = cat(constructor_implementations),
                attributes                 = nl(catnl(attributes)),
                inverse                    = nl(catnl(inverse)),
                superclass                 = superclass
            )

        selectable_simple_types = sorted(set(sum([b.values for a,b in mapping.schema.selects.items()], [])) & set(mapping.schema.types.keys()))
        schema_entity_statements += [templates.schema_simple_stmt%locals() for name in selectable_simple_types]
        schema_entity_statements += [templates.schema_entity_stmt%locals() for name, type in mapping.schema.entities.items()]

        enumerable_types = sorted(set([name for name, type in mapping.schema.types.items()] + [name for name, type in mapping.schema.entities.items()]))
        max_len = max(map(len, enumerable_types))
        type_name_strings = catc(map(stringify, enumerable_types))
        string_map_statements = [templates.string_map_statement % {
            'uppercase_name' : name.upper(),
            'name'           : name,
            'padding'        : ' ' * (max_len - len(name))
        } for name in enumerable_types]

        parent_type_statements = [templates.parent_type_stmt % {
            'name'    : name,
            'parent'  : type.supertypes[0],
            'padding' : ' ' * (max_len - len(name))
        } for name, type in mapping.schema.entities.items() if type.supertypes and len(type.supertypes) == 1]

        max_id = len(enumerable_types)

        simple_type_statements = cator("v == Type::%s"%name for name in selectable_simple_types)

        self.str = templates.implementation % {
            'schema_name_upper'        : mapping.schema.name.upper(),
            'schema_name'              : mapping.schema.name.capitalize(),
            'max_id'                   : max_id,
            'enumeration_functions'    : cat(enumeration_functions),
            'schema_entity_statements' : catnl(schema_entity_statements),
            'type_name_strings'        : type_name_strings,
            'string_map_statements'    : catnl(string_map_statements),
            'simple_type_statement'    : simple_type_statements,
            'parent_type_statements'   : catnl(parent_type_statements),
            'entity_implementations'   : catnl(entity_implementations)
        }

        self.schema_name = mapping.schema.name.capitalize()
    def __repr__(self):
        return self.str
    def emit(self):
        f = open('%s.cpp'%self.schema_name, 'w', encoding='utf-8')
        f.write(str(self))
        f.close()

