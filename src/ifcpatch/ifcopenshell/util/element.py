def get_psets(element):
    psets = {}
    try:
        if element.is_a('IfcTypeObject'):
            if element.HasPropertySets:
                for definition in element.HasPropertySets:
                    psets[definition.Name] = get_property_definition(definition)
        else:
            for relationship in element.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByProperties'):
                    definition = relationship.RelatingPropertyDefinition
                    psets[definition.Name] = get_property_definition(definition)
    except Exception as e:
        import traceback
        print('failed to load properties: {}'.format(e))
        traceback.print_exc()
    return psets


def get_property_definition(definition):
    if definition is not None:
        props = {}
        if definition.is_a('IfcElementQuantity'):
            props.update(get_quantities(definition.Quantities))
        elif definition.is_a('IfcPropertySet'):
            props.update(get_properties(definition.HasProperties))
        else:
            # Entity introduced in IFC4
            # definition.is_a('IfcPreDefinedPropertySet'):
            for prop in range(4, len(definition)):
                props[definition.attribute_name(prop)] = definition[prop]
        return props


def get_quantities(quantities):
    results = {}
    for quantity in quantities:
        if quantity.is_a('IfcPhysicalSimpleQuantity'):
            results[quantity.Name] = quantity[3]
    return results


def get_properties(properties):
    results = {}
    for prop in properties:
        if prop.is_a('IfcPropertySingleValue'):
            results[prop.Name] = prop.NominalValue.wrappedValue
        elif prop.is_a('IfcComplexProperty'):
            data = prop.get_info()
            data['properties'] = get_properties(prop.HasProperties)
            del(data['HasProperties'])
            results[prop.Name] = data
    return results


def get_type(element):
    if hasattr(element, 'IsTypedBy') and element.IsTypedBy:
        return element.IsTypedBy[0].RelatingType
    elif hasattr(element, 'IsDefinedBy') and element.IsDefinedBy: # IFC2X3
        for relationship in element.IsDefinedBy:
            if relationship.is_a('IfcRelDefinesByType'):
                return relationship.RelatingType


def replace_attribute(element, old, new):
    for i, attribute in enumerate(element):
        if attribute == old:
            element[i] = new
        elif isinstance(attribute, tuple):
            new_attribute = list(attribute)
            for j, item in enumerate(attribute):
                if item == old:
                    new_attribute[j] = new
                    element[i] = new_attribute
