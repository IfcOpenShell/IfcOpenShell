def get_psets(element):
    psets = {}
    try:
        if element.is_a('IfcTypeObject'):
            if element.HasPropertySets:
                for definition in element.HasPropertySets:
                    psets[definition.Name] = get_properties(definition)
        else:
            for relationship in element.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByProperties'):
                    definition = relationship.RelatingPropertyDefinition
                    psets[definition.Name] = get_properties(definition)
    except Exception as e:
        import traceback
        print('failed to load properties: {}'.format(e))
        traceback.print_exc()
    return psets

def get_properties(definition):
    if definition is not None:
        props = {}
        if definition.is_a('IfcElementQuantity'):
            for q in definition.Quantities:
                if q.is_a('IfcPhysicalSimpleQuantity'):
                    props[q.Name] = q[3]
        elif definition.is_a('IfcPropertySet'):
            for prop in definition.HasProperties:
                if prop.is_a('IfcPropertySingleValue'):
                    props[prop.Name] = prop.NominalValue
        else:
            # Entity introduced in IFC4
            # definition.is_a('IfcPreDefinedPropertySet'):
            for prop in range(4, len(definition)):
                props[definition.attribute_name(prop)] = definition[prop]
        return props
