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

class SchemaClass(codegen.Base):
    def __init__(self, mapping):
        
        class UnmetDependenciesException(Exception): pass
        
        schema_name = mapping.schema.name
        declared_types = []
        
        def get_declared_type(type, emitted_names=None):
            if isinstance(type, nodes.AggregationType):
                aggr_type = type.aggregate_type
                make_bound = lambda b: -1 if b == '?' else int(b)
                bound1, bound2 = map(make_bound, (type.bounds.lower, type.bounds.upper))
                decl_type = get_declared_type(type.type)
                return "new aggregation_type(aggregation_type::%(aggr_type)s_type, %(bound1)d, %(bound2)d, %(decl_type)s)" % locals()
            elif isinstance(type, nodes.BinaryType):
                return "new simple_type(simple_type::binary_type)"
            elif isinstance(type, nodes.StringType):
                return "new simple_type(simple_type::string_type)"
            elif isinstance(type, str):
                if mapping.schema.is_type(type) or mapping.schema.is_entity(type):
                    if emitted_names is None or type.lower() in emitted_types:
                        return "new named_type(%s_type)" % type
                    else:
                        raise UnmetDependenciesException(type)
                else:
                    return "new simple_type(simple_type::%s_type)" % type

        def find_inverse_name_and_index(entity_name, attribute_name):
            attributes_per_subtype = []
            while True:
                entity = mapping.schema.entities[entity_name]
                attr_names = list(map(operator.attrgetter('name'), entity.attributes))
                if len(attr_names):
                    attributes_per_subtype.append((entity_name, attr_names))
                if len(entity.supertypes) != 1: break
                entity_name = entity.supertypes[0]
            index = 0
            for et, attrs in attributes_per_subtype[::-1]:
                try: return et, attrs.index(attribute_name)
                except: pass
    
            else:
                raise Exception("No declared type for <%r>" % type)
                    
        self.schema_name = mapping.schema.name.capitalize()
        
        statements = ['',
                      '#include "../ifcparse/IfcSchema.h"',
                      '',
                      'using namespace IfcParse;'
                      '']

        collections_by_type = (('entity',           mapping.schema.entities    ),
                               ('type_declaration', mapping.schema.simpletypes ),
                               ('select_type',      mapping.schema.selects     ),
                               ('enumeration_type', mapping.schema.enumerations))

        for cpp_type, collection in collections_by_type:
            for name in collection.keys():
                statements.append('%(cpp_type)s* %(name)s_type = 0;' % locals())
                      
        statements.append("""
#ifdef _MSC_VER
#pragma optimize("", off)
#endif
        """)
        statements.append('schema_definition* populate_schema() {')
        
        emitted_types = set()
        while len(emitted_types) < len(mapping.schema.simpletypes):
            for name, type in mapping.schema.simpletypes.items():
                if name.lower() in emitted_types: continue
                
                try:
                    declared_type = get_declared_type(type, emitted_types)
                except UnmetDependenciesException:
                    # print("Unmet", repr(name))
                    continue

                statements.append('    %(name)s_type = new type_declaration(IfcSchema::Type::%(name)s, %(declared_type)s);' % locals())
                emitted_types.add(name.lower())
                
                declared_types.append('%(name)s_type' % locals())
                
        for name, enum in mapping.schema.enumerations.items():
            statements.append('    {')
            statements.append('        std::vector<std::string> items; items.reserve(%d);' % len(enum.values))
            statements.extend(map(lambda v: '        items.push_back("%s");' % v, sorted(enum.values)))
            statements.append('        %(name)s_type = new enumeration_type(IfcSchema::Type::%(name)s, items);' % locals())
            statements.append('    }')
            
            declared_types.append('%(name)s_type' % locals())
        
        emitted_entities = set()
        while len(emitted_entities) < len(mapping.schema.entities):
            for name, type in mapping.schema.entities.items():
                if name.lower() in emitted_entities: continue
                if len(type.supertypes) == 0 or set(map(lambda s: s.lower(), type.supertypes)) < emitted_entities:
                    supertype = '0' if len(type.supertypes) == 0 else '%s_type' % type.supertypes[0]
                    statements.append('    %(name)s_type = new entity(IfcSchema::Type::%(name)s, %(supertype)s);' % locals())
                    emitted_entities.add(name.lower())
                    
                    declared_types.append('%(name)s_type' % locals())
        
        emmited = emitted_types | emitted_entities | set(mapping.schema.enumerations.keys())
        
        emitted_selects = set()
        while len(emitted_selects) < len(mapping.schema.selects):
            for name, type in mapping.schema.selects.items():
                if name.lower() in emitted_selects: continue
                if set(map(lambda s: s.lower(),type.values)) < emmited:
                    statements.append('    {')
                    statements.append('        std::vector<const declaration*> items; items.reserve(%d);' % len(type.values))
                    statements.extend(map(lambda v: '        items.push_back(%s_type);' % v, sorted(type.values)))
                    statements.append('        %(name)s_type = new select_type(IfcSchema::Type::%(name)s, items);' % locals())
                    statements.append('    }')
                    emitted_selects.add(name.lower())
                    emmited.add(name)
                    
                    declared_types.append('%(name)s_type' % locals())
                    
        num_declarations = len(declared_types)
                    
        for name, type in mapping.schema.entities.items():
            derived = set(mapping.derived_in_supertype(type))
            attribute_names = list(map(operator.attrgetter('name'), mapping.arguments(type)))
            
            statements.append('    {')
            statements.append('        std::vector<const entity::attribute*> attributes; attributes.reserve(%d);' % len(type.attributes))
            for attr in type.attributes:
                attr_name, optional = attr.name, str(attr.optional).lower()
                decl_type = get_declared_type(attr.type)
                statements.append('        attributes.push_back(new entity::attribute("%(attr_name)s", %(decl_type)s, %(optional)s));' % locals())
            statements.append('        std::vector<bool> derived; derived.reserve(%d);' % len(attribute_names))
            statements.append('        ' + " ".join(map(lambda b: 'derived.push_back(%s);' % str(b in derived).lower(), attribute_names)))
            statements.append('        %(name)s_type->set_attributes(attributes, derived);' % locals())
            statements.append('    }')
            
        for name, type in mapping.schema.entities.items():
            if type.inverse:
                statements.append('    {')
                statements.append('        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(%d);' % len(type.inverse.elements))
                for attr in type.inverse.elements:
                    if attr.bounds:
                        make_bound = lambda b: -1 if b == '?' else int(b)
                        bound1, bound2 = map(make_bound, (attr.bounds.lower, attr.bounds.upper))
                    else:
                        bound1, bound2 = -1, -1
                    attr_name, aggr_type, entity_ref = attr.name, attr.type, attr.entity
                    if aggr_type is None: aggr_type = 'unspecified'
                    attribute_entity, attribute_entity_index = find_inverse_name_and_index(entity_ref, attr.attribute)
                    statements.append('        attributes.push_back(new entity::inverse_attribute("%(attr_name)s", entity::inverse_attribute::%(aggr_type)s_type, %(bound1)d, %(bound2)d, %(entity_ref)s_type, %(attribute_entity)s_type->attributes()[%(attribute_entity_index)d]));' % locals())
                statements.append('        %(name)s_type->set_inverse_attributes(attributes);' % locals())
                statements.append('    }')
            
        statements.append('')
        statements.append('    std::vector<const declaration*> declarations; declarations.reserve(%(num_declarations)d);' % locals())
        for type_name in declared_types:
            statements.append('    declarations.push_back(%(type_name)s);' % locals())
            
        statements.append('    return new schema_definition("%(schema_name)s", declarations, true);' % locals())
        
        statements.extend(('}',''))
        
        statements.append("""
#ifdef _MSC_VER
#pragma optimize("", on)
#endif
        """)
        
        statements.append("namespace %s {" % mapping.schema.name)
        
        statements.extend(('const schema_definition& get_schema() {',
                           '',
                           '    static const schema_definition* s = populate_schema();',
                           '    return *s;',
                           '}','}','',''))
                           
        self.str = "\n".join(statements)
        
        self.file_name = '%s-schema.cpp'%self.schema_name

    def __repr__(self):
        return self.str
