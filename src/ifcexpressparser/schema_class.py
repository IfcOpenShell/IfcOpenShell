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
        self.schema_name = schema_name_title = schema_name.capitalize()

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
                        return "new named_type(%s_%s_type)" % (schema_name, type)
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
                    
        statements = ['',
                      '#include "../ifcparse/IfcSchema.h"',
                      '#include "../ifcparse/%(schema_name_title)s.h"' % locals(),
                      '',
                      'using namespace IfcParse;',
                      '']

        collections_by_type = (('entity',           mapping.schema.entities    ),
                               ('type_declaration', mapping.schema.simpletypes ),
                               ('select_type',      mapping.schema.selects     ),
                               ('enumeration_type', mapping.schema.enumerations))

        for cpp_type, collection in collections_by_type:
            for name in collection.keys():
                statements.append('%(cpp_type)s* %(schema_name)s_%(name)s_type = 0;' % locals())
                
        declarations_by_index = []
        
        statements.append("{factory_placeholder}")
                      
        statements.append("""
#ifdef _MSC_VER
#pragma optimize("", off)
#endif
        """)
        statements.append('IfcParse::schema_definition* %(schema_name)s_populate_schema() {' % locals())
        
        emitted_types = set()
        while len(emitted_types) < len(mapping.schema.simpletypes):
            for name, type in mapping.schema.simpletypes.items():
                if name.lower() in emitted_types: continue
                
                try:
                    declared_type = get_declared_type(type, emitted_types)
                except UnmetDependenciesException:
                    # print("Unmet", repr(name))
                    continue

                statements.append('    %(schema_name)s_%(name)s_type = new type_declaration("%(name)s", %%(index_in_schema_%(name)s)d, %(declared_type)s);' % locals())
                emitted_types.add(name.lower())
                
                declared_types.append('%(schema_name)s_%(name)s_type' % locals())
                declarations_by_index.append(name)
                
        for name, enum in mapping.schema.enumerations.items():
            statements.append('    {')
            statements.append('        std::vector<std::string> items; items.reserve(%d);' % len(enum.values))
            statements.extend(map(lambda v: '        items.push_back("%s");' % v, sorted(enum.values)))
            statements.append('        %(schema_name)s_%(name)s_type = new enumeration_type("%(name)s", %%(index_in_schema_%(name)s)d, items);' % locals())
            statements.append('    }')
            
            declared_types.append('%(schema_name)s_%(name)s_type' % locals())
            declarations_by_index.append(name)
        
        emitted_entities = set()
        while len(emitted_entities) < len(mapping.schema.entities):
            for name, type in mapping.schema.entities.items():
                if name.lower() in emitted_entities: continue
                if len(type.supertypes) == 0 or set(map(lambda s: s.lower(), type.supertypes)) < emitted_entities:
                    supertype = '0' if len(type.supertypes) == 0 else '%s_%s_type' % (schema_name, type.supertypes[0])
                    statements.append('    %(schema_name)s_%(name)s_type = new entity("%(name)s", %%(index_in_schema_%(name)s)d, %(supertype)s);' % locals())
                    emitted_entities.add(name.lower())
                    
                    declared_types.append('%(schema_name)s_%(name)s_type' % locals())
                    declarations_by_index.append(name)
        
        emmited = emitted_types | emitted_entities | set(mapping.schema.enumerations.keys())
        
        emitted_selects = set()
        while len(emitted_selects) < len(mapping.schema.selects):
            for name, type in mapping.schema.selects.items():
                if name.lower() in emitted_selects: continue
                if set(map(lambda s: s.lower(),type.values)) < emmited:
                    statements.append('    {')
                    statements.append('        std::vector<const declaration*> items; items.reserve(%d);' % len(type.values))
                    statements.extend(map(lambda v: '        items.push_back(%s_%s_type);' % (schema_name, v), sorted(type.values)))
                    statements.append('        %(schema_name)s_%(name)s_type = new select_type("%(name)s", %%(index_in_schema_%(name)s)d, items);' % locals())
                    statements.append('    }')
                    emitted_selects.add(name.lower())
                    emmited.add(name)
                    
                    declared_types.append('%(schema_name)s_%(name)s_type' % locals())
                    declarations_by_index.append(name)
                    
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
            statements.append('        %(schema_name)s_%(name)s_type->set_attributes(attributes, derived);' % locals())
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
                    statements.append('        attributes.push_back(new entity::inverse_attribute("%(attr_name)s", entity::inverse_attribute::%(aggr_type)s_type, %(bound1)d, %(bound2)d, %(schema_name)s_%(entity_ref)s_type, %(schema_name)s_%(attribute_entity)s_type->attributes()[%(attribute_entity_index)d]));' % locals())
                statements.append('        %(schema_name)s_%(name)s_type->set_inverse_attributes(attributes);' % locals())
                statements.append('    }')
            
        statements.append('')
        statements.append('    std::vector<const declaration*> declarations; declarations.reserve(%(num_declarations)d);' % locals())
        for type_name in declared_types:
            statements.append('    declarations.push_back(%(type_name)s);' % locals())
            
        statements.append('    return new schema_definition("%(schema_name)s", declarations, new %(schema_name)s_instance_factory());' % locals())
        
        statements.extend(('}',''))
        
        statements.append("""
#ifdef _MSC_VER
#pragma optimize("", on)
#endif
        """)
        
        statements.extend(('const schema_definition& %s::get_schema() {' % schema_name_title,
                           '',
                           '    static const schema_definition* s = %(schema_name)s_populate_schema();' % locals(),
                           '    return *s;',
                           '}','',''))
                           
        declarations_by_index.sort(key=str.lower)
        declarations_by_index_map = dict(("index_in_schema_%s" % j,i) for i,j in enumerate(declarations_by_index))
        
        def bind(s):
            if "%" in s: return s % declarations_by_index_map
            else: return s
            
        can_be_instantiated_set = set(list(mapping.schema.entities.keys()) + list(mapping.schema.simpletypes.keys()))
        def can_be_instantiated(idx_name):
            name = idx_name[1]
            return name in can_be_instantiated_set
                           
        instance_mapping = """switch(data->type()->index_in_schema()) {
            %s
            default: throw IfcParse::IfcException(data->type()->name() + " cannot be instantiated");
        }
""" % "\n            ".join(map(lambda tup: ("case %%d: return new ::%s::%%s(data);" % schema_name_title) % tup, filter(can_be_instantiated, enumerate(declarations_by_index))))

        statements[statements.index("{factory_placeholder}")] = """
class %(schema_name)s_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        %(instance_mapping)s
    }
};
""" % locals()
                           
        self.str = "\n".join(map(bind, statements))
        
        self.file_name = '%s-schema.cpp'%self.schema_name

    def __repr__(self):
        return self.str
