import ifcopenshell


def get_psets(element):
    psets = {}
    if element.is_a("IfcTypeObject"):
        if element.HasPropertySets:
            for definition in element.HasPropertySets:
                psets[definition.Name] = get_property_definition(definition)
    elif hasattr(element, "IsDefinedBy"):
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByProperties"):
                definition = relationship.RelatingPropertyDefinition
                psets[definition.Name] = get_property_definition(definition)
    return psets


def get_property_definition(definition):
    if definition is not None:
        props = {}
        if definition.is_a("IfcElementQuantity"):
            props.update(get_quantities(definition.Quantities))
        elif definition.is_a("IfcPropertySet"):
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
        if quantity.is_a("IfcPhysicalSimpleQuantity"):
            results[quantity.Name] = quantity[3]
    return results


def get_properties(properties):
    results = {}
    for prop in properties:
        if prop.is_a("IfcPropertySingleValue"):
            results[prop.Name] = prop.NominalValue.wrappedValue if prop.NominalValue else None
        elif prop.is_a("IfcComplexProperty"):
            data = prop.get_info()
            data["properties"] = get_properties(prop.HasProperties)
            del data["HasProperties"]
            results[prop.Name] = data
    return results


def get_type(element):
    if element.is_a("IfcTypeObject"):
        return element
    elif hasattr(element, "IsTypedBy") and element.IsTypedBy:
        return element.IsTypedBy[0].RelatingType
    elif hasattr(element, "IsDefinedBy") and element.IsDefinedBy:  # IFC2X3
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByType"):
                return relationship.RelatingType


def get_material(element, should_skip_usage=False):
    if hasattr(element, "HasAssociations") and element.HasAssociations:
        for relationship in element.HasAssociations:
            if relationship.is_a("IfcRelAssociatesMaterial"):
                if should_skip_usage:
                    if relationship.RelatingMaterial.is_a("IfcMaterialLayerSetUsage"):
                        return relationship.RelatingMaterial.ForLayerSet
                    elif relationship.RelatingMaterial.is_a("IfcMaterialProfileSetUsage"):
                        return relationship.RelatingMaterial.ForProfileSet
                return relationship.RelatingMaterial
    relating_type = get_type(element)
    if hasattr(relating_type, "HasAssociations") and relating_type.HasAssociations:
        for relationship in relating_type.HasAssociations:
            if relationship.is_a("IfcRelAssociatesMaterial"):
                return relationship.RelatingMaterial


def get_container(element):
    if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
        return element.ContainedInStructure[0].RelatingStructure


def get_aggregate(element):
    if hasattr(element, "Decomposes") and element.Decomposes:
        return element.Decomposes[0].RelatingObject


def replace_attribute(element, old, new):
    for i, attribute in enumerate(element):
        if has_element_reference(attribute, old):
            new_attribute = element.walk(lambda v: v == old, lambda v: new, attribute)
            element[i] = new_attribute


def has_element_reference(value, element):
    if isinstance(value, (tuple, list)):
        for v in value:
            return has_element_reference(v, element)
    return value == element


def remove_deep(ifc_file, element):
    # @todo maybe some sort of try-finally mechanism.
    ifc_file.batch()
    subgraph = list(ifc_file.traverse(element))
    subgraph_set = set(subgraph)
    for ref in subgraph[::-1]:
        if ref.id() and len(set(ifc_file.get_inverse(ref)) - subgraph_set) == 0:
            ifc_file.remove(ref)
    ifc_file.unbatch()


def copy(ifc_file, element):
    new = ifc_file.create_entity(element.is_a())
    for i, attribute in enumerate(element):
        if attribute is None:
            continue
        new[i] = attribute
    return new


def copy_deep(ifc_file, element):
    new = ifc_file.create_entity(element.is_a())
    for i, attribute in enumerate(element):
        if attribute is None:
            continue
        if isinstance(attribute, ifcopenshell.entity_instance):
            attribute = copy_deep(ifc_file, attribute)
        elif isinstance(attribute, tuple) and attribute and isinstance(attribute[0], ifcopenshell.entity_instance):
            attribute = list(attribute)
            for j, item in enumerate(attribute):
                attribute[j] = copy_deep(ifc_file, item)
        new[i] = attribute
    return new
