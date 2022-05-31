# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell


def get_psets(element, psets_only=False, qtos_only=False, should_inherit=True):
    psets = {}
    if element.is_a("IfcTypeObject"):
        for definition in element.HasPropertySets or []:
            if psets_only and not definition.is_a("IfcPropertySet"):
                continue
            if qtos_only and not definition.is_a("IfcElementQuantity"):
                continue
            psets[definition.Name] = get_property_definition(definition)
    elif element.is_a("IfcMaterialDefinition") or element.is_a("IfcProfileDef"):
        for definition in element.HasProperties or []:
            if qtos_only:
                continue
            psets[definition.Name] = get_property_definition(definition)
    elif hasattr(element, "IsDefinedBy"):
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type and should_inherit:
            psets = get_psets(element_type)
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByProperties"):
                definition = relationship.RelatingPropertyDefinition
                if psets_only and not definition.is_a("IfcPropertySet"):
                    continue
                if qtos_only and not definition.is_a("IfcElementQuantity"):
                    continue
                psets.setdefault(definition.Name, {}).update(get_property_definition(definition))
    return psets


def get_property_definition(definition):
    if definition is not None:
        props = {}
        if definition.is_a("IfcElementQuantity"):
            props.update(get_quantities(definition.Quantities))
        elif definition.is_a("IfcPropertySet"):
            props.update(get_properties(definition.HasProperties))
        elif definition.is_a("IfcMaterialProperties") or definition.is_a("IfcProfileProperties"):
            props.update(get_properties(definition.Properties))
        else:
            # Entity introduced in IFC4
            # definition.is_a('IfcPreDefinedPropertySet'):
            for prop in range(4, len(definition)):
                if definition[prop] is not None:
                    props[definition.attribute_name(prop)] = definition[prop]
        props["id"] = definition.id()
        return props


def get_quantities(quantities):
    results = {}
    for quantity in quantities or []:
        if quantity.is_a("IfcPhysicalSimpleQuantity"):
            results[quantity.Name] = quantity[3]
    return results


def get_properties(properties):
    results = {}
    for prop in properties or []:
        if prop.is_a("IfcPropertySingleValue"):
            results[prop.Name] = prop.NominalValue.wrappedValue if prop.NominalValue else None
        elif prop.is_a("IfcComplexProperty"):
            data = {k: v for k, v in prop.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_properties(prop.HasProperties)
            del data["HasProperties"]
            results[prop.Name] = data
    return results


def get_predefined_type(element):
    element_type = get_type(element)
    if element_type:
        predefined_type = getattr(element_type, "PredefinedType", None)
        if predefined_type == "USERDEFINED" or not predefined_type:
            predefined_type = getattr(element_type, "ElementType", getattr(element_type, "ProcessType", None))
        if predefined_type and predefined_type != "NOTDEFINED":
            return predefined_type
    predefined_type = getattr(element, "PredefinedType", None)
    if predefined_type == "USERDEFINED" or not predefined_type:
        predefined_type = getattr(element, "ObjectType", None)
    return predefined_type


def get_type(element):
    if element.is_a("IfcTypeObject"):
        return element
    elif hasattr(element, "IsTypedBy") and element.IsTypedBy:
        return element.IsTypedBy[0].RelatingType
    elif hasattr(element, "IsDefinedBy") and element.IsDefinedBy:  # IFC2X3
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByType"):
                return relationship.RelatingType


def get_types(type):
    for rel in getattr(type, "Types", []):
        return rel.RelatedObjects
    for rel in getattr(type, "ObjectTypeOf", []):
        return rel.RelatedObjects
    return []


def get_material(element, should_skip_usage=False, should_inherit=True):
    if hasattr(element, "HasAssociations") and element.HasAssociations:
        for relationship in element.HasAssociations:
            if relationship.is_a("IfcRelAssociatesMaterial"):
                if should_skip_usage:
                    if relationship.RelatingMaterial.is_a("IfcMaterialLayerSetUsage"):
                        return relationship.RelatingMaterial.ForLayerSet
                    elif relationship.RelatingMaterial.is_a("IfcMaterialProfileSetUsage"):
                        return relationship.RelatingMaterial.ForProfileSet
                return relationship.RelatingMaterial
    if should_inherit:
        relating_type = get_type(element)
        if relating_type != element and hasattr(relating_type, "HasAssociations") and relating_type.HasAssociations:
            return get_material(relating_type, should_skip_usage)


def get_elements_by_material(ifc_file, material):
    results = set()
    for inverse in ifc_file.get_inverse(material):
        if inverse.is_a("IfcRelAssociatesMaterial"):
            results.update(inverse.RelatedObjects)
        elif inverse.is_a("IfcMaterialLayer"):
            for material_set in inverse.ToMaterialLayerSet:
                results.update(get_elements_by_material(ifc_file, material_set))
        elif inverse.is_a("IfcMaterialProfile"):
            for material_set in inverse.ToMaterialProfileSet:
                results.update(get_elements_by_material(ifc_file, material_set))
        elif inverse.is_a("IfcMaterialConstituent"):
            for material_set in inverse.ToMaterialConstituentSet:
                results.update(get_elements_by_material(ifc_file, material_set))
        elif inverse.is_a("IfcMaterialLayerSetUsage"):
            results.update(get_elements_by_material(ifc_file, inverse))
        elif inverse.is_a("IfcMaterialProfileSetUsage"):
            results.update(get_elements_by_material(ifc_file, inverse))
        elif inverse.is_a("IfcMaterialList"):
            results.update(get_elements_by_material(ifc_file, inverse))
    return results


def get_elements_by_style(ifc_file, style):
    results = set()
    inverses = list(ifc_file.get_inverse(style))
    while inverses:
        inverse = inverses.pop()
        if inverse.is_a("IfcPresentationStyleAssignment"):
            inverses.extend(ifc_file.get_inverse(inverse))
            continue
        if not inverse.is_a("IfcStyledItem"):
            continue
        if inverse.Item:
            [
                results.update(get_elements_by_representation(ifc_file, i))
                for i in ifc_file.get_inverse(inverse.Item)
                if i.is_a("IfcShapeRepresentation")
            ]
        else:
            styled_reps = [i for i in ifc_file.get_inverse(inverse) if i.is_a("IfcStyledRepresentation")]
            for styled_rep in styled_reps:
                for material_def_rep in styled_rep.OfProductRepresentation:
                    results.update(get_elements_by_material(ifc_file, material_def_rep.RepresentedMaterial))
    return results


def get_elements_by_representation(ifc_file, representation):
    results = set()
    [results.update(pr.ShapeOfProduct) for pr in representation.OfProductRepresentation]
    for rep_map in representation.RepresentationMap:
        for inverse in ifc_file.get_inverse(rep_map):
            if inverse.is_a("IfcTypeProduct"):
                results.add(inverse)
            elif inverse.is_a("IfcMappedItem"):
                [
                    results.update(get_elements_by_representation(ifc_file, rep))
                    for rep in ifc_file.get_inverse(inverse)
                    if rep.is_a("IfcShapeRepresentation")
                ]
    return results


def get_layers(ifc_file, element):
    layers = []
    representations = []
    if getattr(element, "Representation", None):
        representations = [element.Representation]
    elif getattr(element, "RepresentationMaps", None):
        representations = element.RepresentationMaps
    for representation in representations:
        for subelement in ifc_file.traverse(representation):
            if subelement.is_a("IfcShapeRepresentation"):
                layers.extend(subelement.LayerAssignments or [])
            elif subelement.is_a("IfcGeometricRepresentationItem"):
                if ifc_file.schema == "IFC2X3":
                    layers.extend(subelement.LayerAssignments or [])
                else:
                    layers.extend(subelement.LayerAssignment or [])
    return layers


def get_container(element, should_get_direct=False):
    if should_get_direct:
        if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
            return element.ContainedInStructure[0].RelatingStructure
    else:
        aggregate = get_aggregate(element)
        if aggregate:
            return get_container(aggregate, should_get_direct)
        if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
            return element.ContainedInStructure[0].RelatingStructure


def get_decomposition(element):
    queue = [element]
    results = []
    while queue:
        element = queue.pop()
        for rel in getattr(element, "ContainsElements", []):
            queue.extend(rel.RelatedElements)
            results.extend(rel.RelatedElements)
        for rel in getattr(element, "IsDecomposedBy", []):
            queue.extend(rel.RelatedObjects)
            results.extend(rel.RelatedObjects)
    return results


def get_aggregate(element):
    if hasattr(element, "Decomposes") and element.Decomposes:
        return element.Decomposes[0].RelatingObject


def get_parts(element):
    if hasattr(element, "IsDecomposedBy") and element.IsDecomposedBy:
        return element.IsDecomposedBy[0].RelatedObjects


def replace_attribute(element, old, new):
    for i, attribute in enumerate(element):
        if has_element_reference(attribute, old):
            new_attribute = element.walk(lambda v: v == old, lambda v: new, attribute)
            element[i] = new_attribute


def has_element_reference(value, element):
    if isinstance(value, (tuple, list)):
        for v in value:
            if has_element_reference(v, element):
                return True
        return False
    return value == element


def remove_deep(ifc_file, element):
    # @todo maybe some sort of try-finally mechanism.
    ifc_file.batch()
    subgraph = list(ifc_file.traverse(element, breadth_first=True))
    subgraph_set = set(subgraph)
    for ref in subgraph[::-1]:
        if ref.id() and len(set(ifc_file.get_inverse(ref)) - subgraph_set) == 0:
            ifc_file.remove(ref)
    ifc_file.unbatch()


def remove_deep2(ifc_file, element, also_consider=[], do_not_delete=[]):
    # Experimental remove deep proposal. No batch for now until this is more certain. See #1812.
    # ifc_file.batch()
    to_delete = set()
    subgraph = list(ifc_file.traverse(element, breadth_first=True))
    subgraph.extend(also_consider)
    subgraph_set = set(subgraph)
    subelement_queue = ifc_file.traverse(element, max_levels=1)
    while subelement_queue:
        subelement = subelement_queue.pop(0)
        if (
            subelement.id()
            and len(set(ifc_file.get_inverse(subelement)) - subgraph_set) == 0
            and subelement not in do_not_delete
        ):
            to_delete.add(subelement)
            subelement_queue.extend(ifc_file.traverse(subelement, max_levels=1)[1:])
    for subelement in to_delete:
        ifc_file.remove(subelement)
    # ifc_file.unbatch()


def copy(ifc_file, element):
    new = ifc_file.create_entity(element.is_a())
    for i, attribute in enumerate(element):
        if attribute is None:
            continue
        if new.attribute_name(i) == "GlobalId":
            new[i] = ifcopenshell.guid.new()
        else:
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
