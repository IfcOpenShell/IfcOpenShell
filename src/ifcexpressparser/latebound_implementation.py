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

import codegen
import templates

class LateBoundImplementation(codegen.Base):
    def __init__(self, mapping):
        schema_name = mapping.schema.name.capitalize()
        
        entity_descriptors = []
        enumeration_descriptors = []
        derived_field_statements = []
        inverse_implementations = []
        
        for name, type in mapping.schema.simpletypes.items():
            entity_descriptors.append(templates.entity_descriptor % {
                'type'                         : name,
                'parent_statement'             : '0',
                'entity_descriptor_attributes' : templates.entity_descriptor_attribute_without_entity % {
                    'name'     : 'wrappedValue',
                    'optional' : 'false',
                    'type'     : mapping.make_argument_type(mapping.schema.types[name].type)
                }
            })
            
        emitted_entities = set()
        while len(emitted_entities) < len(mapping.schema.entities):
            for name, type in mapping.schema.entities.items():
                if name.lower() in emitted_entities: continue
                if len(type.supertypes) == 0 or set(map(str.lower, type.supertypes)) <= emitted_entities:
                    constructor_arguments = mapping.get_assignable_arguments(type, include_derived = True)
                    entity_descriptor_attributes = []
                    for arg in constructor_arguments:
                        if not arg['is_inherited']:
                            is_enumeration = arg['argument_type_enum'] == 'IfcUtil::Argument_ENUMERATION'
                            tmpl = templates.entity_descriptor_attribute_with_entity
                            entity_name = arg['argument_type'] if is_enumeration else arg['argument_entity'].split('::')[1]
                            entity_descriptor_attributes.append(tmpl % {
                                'name'       : arg['name'],
                                'optional'   : 'true' if arg['is_optional'] else 'false',
                                'type'       : arg['argument_type_enum'],
                                'entity_name': entity_name
                            })
                        
                    emitted_entities.add(name)
                    
                    parent_statement = '0' if len(type.supertypes) != 1 else templates.entity_descriptor_parent % {
                        'type' : [k for k in mapping.schema.entities.keys() if k.lower() == type.supertypes[0].lower()][0]
                    }
                    entity_descriptors.append(templates.entity_descriptor % {
                        'type'                         : name,
                        'parent_statement'             : parent_statement,
                        'entity_descriptor_attributes' : '\n'.join(entity_descriptor_attributes)
                    })
                    
        for name, enum in mapping.schema.enumerations.items():
            enumeration_descriptor_values = '\n'.join([templates.enumeration_descriptor_value % {
                'name' : v
            } for v in enum.values])
            enumeration_descriptors.append(templates.enumeration_descriptor % {
                'type'                          : name,
                'enumeration_descriptor_values' : enumeration_descriptor_values
            })
            
        for name, type in mapping.schema.entities.items():
            constructor_arguments = mapping.get_assignable_arguments(type, include_derived = True)
            statements = ''.join(templates.derived_field_statement_attrs % (a['index']-1) for a in constructor_arguments if a['is_derived'])
            if len(statements):
                derived_field_statements.append(templates.derived_field_statement % {
                    'type'       : name,
                    'statements' : statements
                })
                
        for name, type in mapping.schema.entities.items():
            if type.inverse:
                for attr in type.inverse.elements:
                    related_entity = mapping.schema.entities[attr.entity]
                    related_attrs = [a['name'].lower() for a in mapping.get_assignable_arguments(related_entity, include_derived=True)]

                    inverse_implementations.append(templates.inverse_implementation % {
                        'type'         : name,
                        'name'         : attr.name,
                        'related_type' : attr.entity,
                        'index'        : related_attrs.index(attr.attribute.lower())
                    })

        self.str = templates.lb_implementation % {
            'schema_name_upper'        : mapping.schema.name.upper(),
            'schema_name'              : mapping.schema.name.capitalize(),
            'entity_descriptors'       : '\n'.join(entity_descriptors),
            'enumeration_descriptors'  : '\n'.join(enumeration_descriptors),
            'derived_field_statements' : '\n'.join(derived_field_statements),
            'inverse_implementations'  : '\n'.join(inverse_implementations)
        }

        self.schema_name = mapping.schema.name.capitalize()
        
        self.file_name = '%s-latebound.cpp'%self.schema_name
        
        
    def __repr__(self):
        return self.str
