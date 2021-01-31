def get_psets(element):
    psets = {}
    try:
        if element.is_a("IfcTypeObject"):
            if element.HasPropertySets:
                for definition in element.HasPropertySets:
                    psets[definition.Name] = get_property_definition(definition)
        else:
            for relationship in element.IsDefinedBy:
                if relationship.is_a("IfcRelDefinesByProperties"):
                    definition = relationship.RelatingPropertyDefinition
                    psets[definition.Name] = get_property_definition(definition)
    except Exception as e:
        import traceback

        print("failed to load properties: {}".format(e))
        traceback.print_exc()
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
    if hasattr(element, "IsTypedBy") and element.IsTypedBy:
        return element.IsTypedBy[0].RelatingType
    elif hasattr(element, "IsDefinedBy") and element.IsDefinedBy:  # IFC2X3
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByType"):
                return relationship.RelatingType


def get_material(element):
    if hasattr(element, "HasAssociations") and element.HasAssociations:
        for relationship in element.HasAssociations:
            if relationship.is_a("IfcRelAssociatesMaterial"):
                if relationship.RelatingMaterial.is_a("IfcMaterialLayerSetUsage"):
                    return relationship.RelatingMaterial.ForLayerSet
                elif relationship.RelatingMaterial.is_a("IfcMaterialProfileSetUsage"):
                    return relationship.RelatingMaterial.ForProfileSet
                return relationship.RelatingMaterial
    relating_type = get_type(element)
    if hasattr(relating_type, "HasAssociations") and relating_type.HasAssociations:
        for relationship in relating_type.HasAssociations:
            if relationship.is_a("IfcRelAssociatesMaterial"):
                if relationship.RelatingMaterial.is_a("IfcMaterialLayerSetUsage"):
                    return relationship.RelatingMaterial.ForLayerSet
                elif relationship.RelatingMaterial.is_a("IfcMaterialProfileSetUsage"):
                    return relationship.RelatingMaterial.ForProfileSet
                return relationship.RelatingMaterial


def get_container(element):
    if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
        return element.ContainedInStructure[0].RelatingStructure


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


def is_representation_of_context(representation, context, subcontext=None, target_view=None):
    if target_view is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.TargetView == target_view
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )
    elif subcontext is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )
    elif representation.ContextOfItems.ContextType == context:
        return True


def remove_deep(ifc_file, element):
    subgraph = list(ifc_file.traverse(element))
    subgraph_set = set(subgraph)
    for ref in subgraph[::-1]:
        if ref.id() and len(set(ifc_file.get_inverse(ref)) - subgraph_set) == 0:
            ifc_file.remove(ref)


def get_representation(element, context, subcontext=None, target_view=None):
    if element.is_a("IfcProduct") and element.Representation:
        for r in element.Representation.Representations:
            if is_representation_of_context(r, context, subcontext, target_view):
                return r
    elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
        for r in element.RepresentationMaps:
            if is_representation_of_context(r.MappedRepresentation, context, subcontext, target_view):
                return r.MappedRepresentation
