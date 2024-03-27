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

from __future__ import annotations
import ifcopenshell
import ifcopenshell.util.element
from typing import List, Any, Callable, Optional, Union


def get_pset(
    element: ifcopenshell.entity_instance,
    name: str,
    prop: Optional[str] = None,
    psets_only=False,
    qtos_only=False,
    should_inherit=True,
    verbose=False,
) -> Union[Any, dict[str, Any]]:
    """Retrieve a single property set or single property

    This is more efficient than ifcopenshell.util.element.get_psets if you know
    exactly which property set and property you are after.

    If should_inherit is true, the pset "id" only refers to the ID of the
    occurrence, not the type's pset.

    :param element: The IFC Element entity
    :type element: ifcopenshell.entity_instance.entity_instance
    :param name: The name of the pset
    :type name: str
    :param prop: The name of the property
    :type prop: str,optional
    :param psets_only: Default as False. Set to true if only property sets are needed.
    :type psets_only: bool,optional
    :param qtos_only: Default as False. Set to true if only quantities are needed.
    :type qtos_only: bool,optional
    :param should_inherit: Default as True. Set to false if you don't want to inherit property sets from the Type.
    :type should_inherit: bool,optional
    :return: A dictionary of property names and values, or a single value if a
        property is specified.
    :rtype: dict[str, Any]

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        psets_and_qtos = ifcopenshell.util.element.get_pset(element, "Pset_WallCommon")
    """
    pset = None
    type_pset = None

    if element.is_a("IfcTypeObject"):
        for definition in element.HasPropertySets or []:
            if definition.Name == name:
                pset = definition
                break
    elif element.is_a("IfcMaterialDefinition") or element.is_a("IfcProfileDef"):
        for definition in element.HasProperties or []:
            if definition.Name == name:
                pset = definition
                break
    elif hasattr(element, "IsDefinedBy"):
        if should_inherit:
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                type_pset = get_pset(element_type, name, prop, should_inherit=False, verbose=verbose)
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByProperties"):
                definition = relationship.RelatingPropertyDefinition
                if definition.Name == name:
                    pset = definition
                    break

    if pset:
        if psets_only and not pset.is_a("IfcPropertySet"):
            pset = None
        elif qtos_only and not pset.is_a("IfcElementQuantity"):
            pset = None

    if type_pset:
        if psets_only and not type_pset.is_a("IfcPropertySet"):
            type_pset = None
        elif qtos_only and not type_pset.is_a("IfcElementQuantity"):
            type_pset = None

    if not pset and not type_pset:
        return

    if not prop:
        if type_pset:
            occurrence_pset = get_property_definition(pset, verbose=verbose)
            if occurrence_pset:
                type_pset.update(occurrence_pset)
            return type_pset
        return get_property_definition(pset, verbose=verbose)

    value = get_property_definition(pset, prop=prop, verbose=verbose)
    if value is None and type_pset is not None:
        return type_pset
    return value


def get_psets(
    element: ifcopenshell.entity_instance, psets_only=False, qtos_only=False, should_inherit=True, verbose=False
) -> dict[str, dict[str, Any]]:
    """Retrieve property sets, their related properties' names & values and ids.

    If should_inherit is true, the pset "id" only refers to the ID of the
    occurrence, not the type's pset.

    :param element: The IFC Element entity
    :type element: ifcopenshell.entity_instance.entity_instance
    :param psets_only: Default as False. Set to true if only property sets are needed.
    :type psets_only: bool,optional
    :param qtos_only: Default as False. Set to true if only quantities are needed.
    :type qtos_only: bool,optional
    :param should_inherit: Default as True. Set to false if you don't want to inherit property sets from the Type.
    :type should_inherit: bool,optional
    :return: Key, value pair of psets' names and their properties' names & values
    :rtype: dict[str, dict[str, Any]]

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        psets = ifcopenshell.util.element.get_psets(element, psets_only=True)
        qsets = ifcopenshell.util.element.get_psets(element, qtos_only=True)
        psets_and_qtos = ifcopenshell.util.element.get_psets(element)
    """
    psets = {}
    if element.is_a("IfcTypeObject"):
        for definition in element.HasPropertySets or []:
            if psets_only and not definition.is_a("IfcPropertySet"):
                continue
            if qtos_only and not definition.is_a("IfcElementQuantity"):
                continue
            psets[definition.Name] = get_property_definition(definition, verbose=verbose)
    elif element.is_a("IfcMaterialDefinition") or element.is_a("IfcProfileDef"):
        for definition in getattr(element, "HasProperties", None) or []:
            if qtos_only:
                continue
            psets[definition.Name] = get_property_definition(definition, verbose=verbose)
    elif hasattr(element, "IsDefinedBy"):
        if should_inherit:
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                psets = get_psets(element_type, psets_only=psets_only, qtos_only=qtos_only, should_inherit=False)
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByProperties"):
                definition = relationship.RelatingPropertyDefinition
                if psets_only and not definition.is_a("IfcPropertySet"):
                    continue
                if qtos_only and not definition.is_a("IfcElementQuantity"):
                    continue
                psets.setdefault(definition.Name, {}).update(get_property_definition(definition, verbose=verbose))
    return psets


def get_property_definition(
    definition: ifcopenshell.entity_instance, prop: Optional[str] = None, verbose=False
) -> Union[Any, dict[str, Any]]:
    if not definition:
        return

    ifc_class = definition.is_a()

    if prop:
        if ifc_class == "IfcElementQuantity":
            return get_quantity(definition.Quantities, prop, verbose=verbose)
        elif ifc_class == "IfcPropertySet":
            return get_property(definition.HasProperties, prop, verbose=verbose)
        elif ifc_class == "IfcMaterialProperties" or ifc_class == "IfcProfileProperties":
            return get_property(definition.Properties, prop, verbose=verbose)
        else:
            # Entity introduced in IFC4
            # definition.is_a('IfcPreDefinedPropertySet'):
            for i in range(4, len(definition)):
                if definition[i] is not None:
                    if definition.attribute_name(i) == prop:
                        return definition[i]
        return

    props = {}
    if ifc_class == "IfcElementQuantity":
        props.update(get_quantities(definition[5], verbose=verbose))
    elif ifc_class == "IfcPropertySet":
        props.update(get_properties(definition[4], verbose=verbose))
    elif ifc_class == "IfcMaterialProperties" or ifc_class == "IfcProfileProperties":
        props.update(get_properties(definition[2], verbose=verbose))
    else:
        # Entity introduced in IFC4
        # definition.is_a('IfcPreDefinedPropertySet'):
        for prop_i in range(4, len(definition)):
            if definition[prop_i] is not None:
                props[definition.attribute_name(prop_i)] = definition[prop_i]
    props["id"] = definition.id()
    return props


def get_quantity(
    quantities: list[ifcopenshell.entity_instance], name: str, verbose=False
) -> Union[Any, dict[str, Any]]:
    for quantity in quantities or []:
        if quantity[0] != name:
            continue
        if quantity.is_a("IfcPhysicalSimpleQuantity"):
            result = quantity[3]
        elif quantity.is_a("IfcPhysicalComplexQuantity"):
            data = {k: v for k, v in quantity.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_quantities(quantity.HasQuantities)
            del data["HasQuantities"]
            result = data
        if verbose:
            result = {"id": quantity.id(), "class": quantity.is_a(), "value": result}
        return result


def get_quantities(quantities: list[ifcopenshell.entity_instance], verbose=False) -> dict[str, dict[str, Any]]:
    results = {}
    for quantity in quantities or []:
        if quantity.is_a("IfcPhysicalSimpleQuantity"):
            results[quantity[0]] = quantity[3]
            if verbose:
                results[quantity[0]] = {
                    "id": quantity.id(),
                    "class": quantity.is_a(),
                    "value": results[quantity[0]],
                }
        elif quantity.is_a("IfcPhysicalComplexQuantity"):
            data = {k: v for k, v in quantity.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_quantities(quantity.HasQuantities)
            del data["HasQuantities"]
            results[quantity[0]] = data
            if verbose:
                results[quantity[0]] = {
                    "id": quantity.id(),
                    "class": quantity.is_a(),
                    "value": results[quantity[0]],
                }
    return results


def get_property(
    properties: list[ifcopenshell.entity_instance], name: str, verbose=False
) -> Union[Any, dict[str, Any]]:
    for prop in properties or []:
        if prop.Name != name:
            continue
        if prop.is_a("IfcPropertySingleValue"):
            result = prop[2].wrappedValue if prop[2] else None
        elif prop.is_a("IfcPropertyEnumeratedValue"):
            result = [v.wrappedValue for v in prop.EnumerationValues] if prop.EnumerationValues else None
        elif prop.is_a("IfcPropertyListValue"):
            result = [v.wrappedValue for v in prop.ListValues] or None
        elif prop.is_a("IfcPropertyBoundedValue"):
            data = prop.get_info()
            del data["Unit"]
            result = data
        elif prop.is_a("IfcPropertyTableValue"):
            result = prop.get_info()
        elif prop.is_a("IfcComplexProperty"):
            data = {k: v for k, v in prop.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_properties(prop.HasProperties)
            del data["HasProperties"]
            result = data
        if verbose:
            result = {"id": prop.id(), "class": prop.is_a(), "value": result}
        return result


def get_properties(properties: list[ifcopenshell.entity_instance], verbose=False) -> dict[str, dict[str, Any]]:
    results = {}
    for prop in properties or []:
        ifc_class = prop.is_a()
        if ifc_class == "IfcPropertySingleValue":
            results[prop[0]] = prop[2].wrappedValue if prop[2] else None
            if verbose:
                results[prop[0]] = {"id": prop.id(), "class": prop.is_a(), "value": results[prop[0]]}
        elif ifc_class == "IfcPropertyEnumeratedValue":
            results[prop[0]] = [v.wrappedValue for v in prop.EnumerationValues] if prop.EnumerationValues else None
            if verbose:
                results[prop[0]] = {"id": prop.id(), "class": prop.is_a(), "value": results[prop[0]]}
        elif ifc_class == "IfcPropertyListValue":
            results[prop[0]] = [v.wrappedValue for v in prop.ListValues] or None
            if verbose:
                results[prop[0]] = {"id": prop.id(), "class": prop.is_a(), "value": results[prop[0]]}
        elif ifc_class == "IfcPropertyBoundedValue":
            data = prop.get_info()
            del data["Unit"]
            results[prop[0]] = data
            if verbose:
                results[prop[0]] = {"id": prop.id(), "class": prop.is_a(), "value": results[prop[0]]}
        elif ifc_class == "IfcPropertyTableValue":
            results[prop[0]] = prop.get_info()
            if verbose:
                results[prop[0]] = {"id": prop.id(), "class": prop.is_a(), "value": results[prop[0]]}
        elif ifc_class == "IfcComplexProperty":
            data = {k: v for k, v in prop.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_properties(prop.HasProperties)
            del data["HasProperties"]
            results[prop[0]] = data
            if verbose:
                results[prop[0]] = {"id": prop.id(), "class": prop.is_a(), "value": results[prop[0]]}
    return results


def get_predefined_type(element: ifcopenshell.entity_instance) -> str:
    """Retrieves the PrefefinedType attribute of an element.

    If the predefined type is user defined, the custom type (such as object
    type, element type, or process type depending on the class) is returned
    instead.  Predefined types from the associated type element are also
    considered first.

    :param element: The IFC Element entity
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: The predefined type of the element
    :rtype: str

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
    """
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


def get_type(element: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Retrieves the construction type element of an element occurrence

    :param element: The element occurrence
    :type: ifcopenshell.entity_instance.entity_instance
    :return: The related type element
    :rtype: ifcopenshell.entity_instance.entity_instance

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        element_type = ifcopenshell.util.element.get_type(element)
    """
    if element.is_a("IfcTypeObject"):
        return element
    elif hasattr(element, "IsTypedBy") and element.IsTypedBy:
        return element.IsTypedBy[0].RelatingType
    elif hasattr(element, "IsDefinedBy") and element.IsDefinedBy:  # IFC2X3
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByType"):
                return relationship.RelatingType


def get_types(type: ifcopenshell.entity_instance) -> List[ifcopenshell.entity_instance]:
    """Get all the occurrences of a type element

    :param type: The type element
    :type type: ifcopenshell.entity_instance.entity_instance
    :return: A list of occurrences of that type
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element_type = ifcopenshell.by_type("IfcWallType")[0]
        walls = ifcopenshell.util.element.get_types(element_type)
    """
    for rel in getattr(type, "Types", []):
        return rel.RelatedObjects
    for rel in getattr(type, "ObjectTypeOf", []):
        return rel.RelatedObjects
    return []


def get_shape_aspects(element: ifcopenshell.entity_instance) -> List[ifcopenshell.entity_instance]:
    """Gets element shape aspects

    :param element: The element to get the shape aspects of.
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: The associated shape aspects of the element.
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        shape_aspect = ifcopenshell.util.element.get_shape_aspects(element)
    """

    # IfcProduct
    if hasattr(element, "Representation"):
        return element.Representation.HasShapeAspects

    # IfcTypeProduct
    shape_aspects = []
    for repersentation_map in element.RepresentationMaps:
        shape_aspects += repersentation_map.HasShapeAspects
    return shape_aspects


def get_material(
    element: ifcopenshell.entity_instance, should_skip_usage=False, should_inherit=True
) -> ifcopenshell.entity_instance:
    """Gets the material of the element

    The material may be a single material, material set (layered, profiled, or
    constituent), or a material set usage.

    :param element: The element to get the material of.
    :type element: ifcopenshell.entity_instance.entity_instance
    :param should_skip_usage: If set to True, if the material is a material set
        usage, the material set itself will be returned. Useful if you don't
        care about occurrence usage parameters. If False, the usage will be
        returned.
    :type should_skip_usage: bool
    :param should_inherit: If True, any inherited materials from associated
        types will be considered.
    :type should_inherit: bool
    :return: The associated material of the element.
    :rtype: ifcopenshell.entity_instance.entity_instance

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        material = ifcopenshell.util.element.get_material(element)
    """
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


def get_materials(element: ifcopenshell.entity_instance, should_inherit=True) -> List[ifcopenshell.entity_instance]:
    """Gets individual materials of an element

    If the element has a material set, the individual materials of that set are
    returned as a list.

    :param element: The element to get the materials of.
    :type element: ifcopenshell.entity_instance.entity_instance
    :param should_inherit: If True, any inherited materials from associated
        types will be considered.
    :return: The associated materials of the element.
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        materials = ifcopenshell.util.element.get_materials(element)
    """
    material = get_material(element, should_skip_usage=True, should_inherit=should_inherit)
    if not material:
        return []
    elif material.is_a("IfcMaterial"):
        return [material]
    elif material.is_a("IfcMaterialLayerSet"):
        return [l.Material for l in material.MaterialLayers]
    elif material.is_a("IfcMaterialProfileSet"):
        return [p.Material for p in material.MaterialProfiles]
    elif material.is_a("IfcMaterialConstituentSet"):
        return [c.Material for c in material.MaterialConstituents]
    elif material.is_a("IfcMaterialList"):
        return list(material.Materials)


def get_styles(element: ifcopenshell.entity_instance) -> List[ifcopenshell.entity_instance]:
    """Retrieves the styles used in an element's representation.

    Styles may be retreived from the material or the body representation.

    :param element: The element to get the styles of.
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: A list of surface styles
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        wall = file.by_type("IfcWall")[0]
        styles = ifcopenshell.util.element.get_styles(wall)
    """
    styles = []

    materials = ifcopenshell.util.element.get_materials(element)
    for material in materials:
        for material_definition_representation in material.HasRepresentation or []:
            for representation in material_definition_representation.Representations:
                for item in representation.Items:
                    styles.extend([s for s in item.Styles if s.is_a("IfcSurfaceStyle")])

    body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    if not body:
        return styles

    for representation in [body]:
        queue = list(representation.Items)
        while queue:
            item = queue.pop()
            if item.is_a("IfcMappedItem"):
                queue.extend(item.MappingSource.MappedRepresentation.Items)
            if item.is_a("IfcBooleanResult"):
                queue.append(item.FirstOperand)
                queue.append(item.SecondOperand)
            if item.StyledByItem:
                styles.extend([s for s in item.StyledByItem[0].Styles if s.is_a("IfcSurfaceStyle")])
    return styles


def get_elements_by_material(
    ifc_file: ifcopenshell.file, material: ifcopenshell.entity_instance
) -> List[ifcopenshell.entity_instance]:
    """Retrieves the elements related to a material.

    This includes elements using the material as part of a material set or set
    usage.

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param material: The IFC Material entity
    :type material: ifcopenshell.entity_instance.entity_instance
    :return: A list of elements using the to the material
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        material = file.by_type("IfcMaterial")[0]
        elements = ifcopenshell.util.element.get_elements_by_material(file, material)
    """
    results = set()
    for inverse in ifc_file.get_inverse(material):
        if inverse.is_a("IfcRelAssociatesMaterial"):
            results.update(inverse.RelatedObjects or [])  # See Revit bug #675
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


def get_elements_by_style(
    ifc_file: ifcopenshell.file, style: ifcopenshell.entity_instance
) -> List[ifcopenshell.entity_instance]:
    """Retrieves the elements whose geometric representation uses a style

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param style: The IfcPresentationStyle entity
    :type style: ifcopenshell.entity_instance.entity_instance
    :return: The elements related to the style
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        style = file.by_type("IfcSurfaceStyle")[0]
        elements = ifcopenshell.util.element.get_elements_by_style(file, style)
    """
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


def get_elements_by_representation(
    ifc_file: ifcopenshell.file, representation: ifcopenshell.entity_instance
) -> List[ifcopenshell.entity_instance]:
    """Gets all elements using a geometric representation

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param representation: The IfcShapeRepresentation representation
    :type representation: ifcopenshell.entity_instance.entity_instance
    :return: The elements using the geometric representation
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        representation = file.by_type("IfcShapeRepresentation")[0]
        elements = ifcopenshell.util.element.get_elements_by_representation(file, representation)
    """
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


def get_elements_by_layer(
    ifc_file: ifcopenshell.file, layer: ifcopenshell.entity_instance
) -> List[ifcopenshell.entity_instance]:
    """Get all the elements that are used by a presentation layer

    :param ifc_file: The IFC file
    :type ifc_file: ifcopenshell.file.file
    :param layer: The IfcPresentationLayerAssignment layer
    :type layer: ifcopenshell.entity_instance.entity_instance
    :return: The elements using the geometric representation
    :rtype: list[ifcopenshell.entity_instance.entity_instance]
    """
    results = set()
    for item in layer.AssignedItems or []:
        if item.is_a("IfcShapeRepresentation"):
            results.update(get_elements_by_representation(ifc_file, item))
        elif item.is_a("IfcRepresentationItem"):
            for inverse in ifc_file.get_inverse(item):
                if inverse.is_a("IfcShapeRepresentation"):
                    results.update(get_elements_by_representation(ifc_file, inverse))
    return results


def get_layers(
    ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance
) -> List[ifcopenshell.entity_instance]:
    """Get the CAD layers that an element is part of

    An element may have portions or all of its geometry assigned to a
    traditional CAD presentation layer.

    :param ifc_file: The IFC file object
    :type ifc_file: ifcopenshell.file.file
    :param element: The IFC element to interrogate
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: A list of IfcPresentationLayerAssignment
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        layers = ifcopenshell.util.element.get_layers(element)
    """
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


def get_container(
    element: ifcopenshell.entity_instance, should_get_direct=False, ifc_class: Optional[str] = None
) -> ifcopenshell.entity_instance:
    """
    Retrieves the spatial structure container of an element.

    :param element: The IFC element
    :type element: ifcopenshell.entity_instance.entity_instance
    :param should_get_direct: If True, a result is only returned if the element
        is directly contained in a spatial structure element. If False, an
        indirect spatial container may be returned, such as if an element is a
        part of an aggregate, and then if that aggregate is contained in a
        spatial structure element.
    :type should_get_direct: bool
    :param ifc_class: Optionally filter the type of container you're after. For
        example, you may be after the storey, not a space.
    :type ifc_class: str, optional
    :return: The direct or indirect container of the element or None.
    :rtype: ifcopenshell.entity_instance.entity_instance

    Example:

    .. code:: python

        element = file.by_type("IfcWall")[0]
        container = ifcopenshell.util.element.get_container(element)
    """
    if should_get_direct:
        if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
            container = element.ContainedInStructure[0].RelatingStructure
            if not ifc_class:
                return container
            if container.is_a(ifc_class):
                return container
    else:
        aggregate = get_aggregate(element)
        if aggregate:
            return get_container(aggregate, should_get_direct)
        nest = get_nest(element)
        if nest:
            return get_container(nest, should_get_direct)
        if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
            container = element.ContainedInStructure[0].RelatingStructure
            if not ifc_class:
                return container
            while container:
                if container.is_a(ifc_class):
                    return container
                container = get_aggregate(container)


def get_referenced_structures(element: ifcopenshell.entity_instance) -> List[ifcopenshell.entity_instance]:
    """Retreives a list of referenced spatial elements

    Typically useful for multistorey elements, such as columns or facade
    elements, or elements that span multiple spaces or in-between spaces, such
    as stairs, doors, etc.

    :param element: The IFC element
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: A list of IfcSpatialElement
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = file.by_type("IfcWall")[0]
        print(ifcopenshell.util.element.get_referenced_structures(element))
    """
    if hasattr(element, "ReferencedInStructures"):
        return [r.RelatingStructure for r in element.ReferencedInStructures]
    return []


def get_decomposition(element: ifcopenshell.entity_instance, is_recursive=True) -> List[ifcopenshell.entity_instance]:
    """
    Retrieves all subelements of an element based on the spatial decomposition
    hierarchy. This includes all subspaces and elements contained in subspaces,
    parts of an aggreate, all openings, and all fills of any openings.

    :param element: The IFC element
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: The decomposition of the element
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = file.by_type("IfcProject")[0]
        decomposition = ifcopenshell.util.element.get_decomposition(element)
    """
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
        for rel in getattr(element, "HasOpenings", []):
            queue.append(rel.RelatedOpeningElement)
            results.append(rel.RelatedOpeningElement)
        for rel in getattr(element, "HasFillings", []):
            queue.append(rel.RelatedBuildingElement)
            results.append(rel.RelatedBuildingElement)
        for rel in getattr(element, "IsNestedBy", []):
            queue.extend(rel.RelatedObjects)
            results.extend(rel.RelatedObjects)
        if not is_recursive:
            break
    return results


def get_grouped_by(element: ifcopenshell.entity_instance) -> List[ifcopenshell.entity_instance]:
    """Retrieves all subelements of an element based on the group.

    :param element: The IFC element
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: All subelements of the group
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = file.by_type("IfcGroup")[0]
        subelements = ifcopenshell.util.element.get_grouped_by(element)
    """
    queue = [element]
    results = []
    while queue:
        element = queue.pop()
        for rel in getattr(element, "IsGroupedBy", []):
            queue.extend(rel.RelatedObjects)
            results.extend(rel.RelatedObjects)
    return results


def get_aggregate(element: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """
    Retrieves the aggregate parent of an element.

    :param element: The IFC element
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: The aggregate of the element
    :rtype: ifcopenshell.entity_instance.entity_instance

    Example:

    .. code:: python

        element = file.by_type("IfcBeam")[0]
        aggregate = ifcopenshell.util.element.get_aggregate(element)
    """
    if hasattr(element, "Decomposes") and element.Decomposes:
        if element.Decomposes[0].is_a("IfcRelAggregates"):  # IFC2X3
            return element.Decomposes[0].RelatingObject


def get_nest(element: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """
    Retrieves the nest parent of an element.

    :param element: The IFC element
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: The nested whole of the element
    :rtype: ifcopenshell.entity_instance.entity_instance

    Example:

    .. code:: python

        element = file.by_type("IfcBeam")[0]
        aggregate = ifcopenshell.util.element.get_nest(element)
    """
    if hasattr(element, "Nests"):
        if element.Nests:
            return element.Nests[0].RelatingObject
    elif hasattr(element, "Decomposes") and element.Decomposes:  # IFC2X3
        if element.Decomposes[0].is_a("IfcRelNests"):
            return element.Decomposes[0].RelatingObject


def get_parts(element: ifcopenshell.entity_instance) -> List[ifcopenshell.entity_instance]:
    """
    Retrieves the parts of an element that have an aggregation relationship.

    :param element: The IFC element
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: The parts of the element
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = file.by_type("IfcElementAssembly")[0]
        parts = ifcopenshell.util.element.get_parts(element)
    """
    if hasattr(element, "IsDecomposedBy") and element.IsDecomposedBy:
        if element.IsDecomposedBy[0].is_a("IfcRelAggregates"):
            return element.IsDecomposedBy[0].RelatedObjects


def get_components(element: ifcopenshell.entity_instance, include_ports=False) -> List[ifcopenshell.entity_instance]:
    """
    Retrieves the components of an element that have an nest relationship.

    For nested ports, see ifcopenshell.util.system.

    :param element: The IFC element
    :param include_ports: Default as False. Set to true if you also want to get ports.
    :type include_ports: bool,optional
    :return: The components of the element
    :rtype: list[ifcopenshell.entity_instance.entity_instance]

    Example:

    .. code:: python

        element = file.by_type("IfcElementAssembly")[0]
        components = ifcopenshell.util.element.get_components(element)
    """
    if hasattr(element, "IsNestedBy"):
        if element.IsNestedBy:
            if include_ports:
                return element.IsNestedBy[0].RelatedObjects
            return [e for e in element.IsNestedBy[0].RelatedObjects if not e.is_a("IfcPort")]
    elif hasattr(element, "IsDecomposedBy") and element.IsDecomposedBy:
        if element.IsDecomposedBy[0].is_a("IfcRelNests"):
            return element.IsDecomposedBy[0].RelatedObjects


def replace_attribute(element: ifcopenshell.entity_instance, old: Any, new: Any) -> None:
    for i, attribute_value in enumerate(element):
        if has_element_reference(attribute_value, old):
            element[i] = element.walk(lambda v: v == old, lambda v: new, attribute_value)


def has_element_reference(value: Any, element: ifcopenshell.entity_instance) -> bool:
    if isinstance(value, (tuple, list)):
        for v in value:
            if has_element_reference(v, element):
                return True
        return False
    return value == element


def remove_deep(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> None:
    """Recursively purges a subgraph safely.

    Do not use, use remove_deep2() instead.
    """
    # @todo maybe some sort of try-finally mechanism.
    ifc_file.batch()
    subgraph = list(ifc_file.traverse(element, breadth_first=True))
    subgraph_set = set(subgraph)
    for ref in subgraph[::-1]:
        if ref.id() and len(set(ifc_file.get_inverse(ref)) - subgraph_set) == 0:
            ifc_file.remove(ref)
    ifc_file.unbatch()


def batch_remove_deep2(ifc_file: ifcopenshell.file) -> None:
    """Enable batch removal after running remove_deep2 using serialisation

    See #944 and #3226. Removing elements in an IFC graph is slow as a lot of
    mappings need to be edited. In larger models (>100MB) and when removing
    many elements (>10000), it is faster to serialise the IFC, remove elements
    using string replacement, and then reload the modified serialised IFC.

    The trade-off is that extra memory will be used, and string replacement
    only works with remove_deep2 where the removed elements have no inverses.
    In addition, transaction history will be lost, and any scripts using this
    method will have to refetch elements from the reloaded IFC and cannot rely
    on existing variables in memory.

    :param ifc_file: The IFC file object
    :type ifc_file: ifcopenshell.file.file
    :rtype: None

    Example:

    .. code:: python

        element1 = model.by_id(123)
        element2 = model.by_id(456)

        ifcopenshell.util.element.batch_remove_deep2(model)
        ifcopenshell.util.element.remove_deep2(model, element2)

        # Notice how we reload the model.
        model = ifcopenshell.util.element.unbatch_remove_deep2(model)

        print(element1) # Don't call element1!
    """
    ifc_file.to_delete = set()


def unbatch_remove_deep2(ifc_file: ifcopenshell.file) -> ifcopenshell.file:
    """Finish removing elements batched from remove_deep2 using string replacement

    See documentation for batch_remove_deep2.

    :param ifc_file: The IFC file object
    :type ifc_file: ifcopenshell.file.file
    :return: A newly loaded file with the elements removed.
    :rtype: ifcopenshell.file.file
    """
    ifc_string = ifc_file.to_string()
    lines = iter(ifc_string.split("\n"))
    ids_to_delete = iter(sorted([e.id() for e in ifc_file.to_delete]))
    id_to_delete = next(ids_to_delete, None)
    result = []

    for line in lines:
        if id_to_delete is None:
            result.append(line)
            continue

        if line.startswith(f"#{id_to_delete}="):
            id_to_delete = next(ids_to_delete, None)
        else:
            result.append(line)

    ifc_file.to_delete = None
    return ifcopenshell.file.from_string("\n".join(result))


def remove_deep2(
    ifc_file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    also_consider: List[ifcopenshell.entity_instance] = [],
    do_not_delete: List[ifcopenshell.entity_instance] = [],
) -> None:
    """Recursively purges a subgraph safely, starting at an element

    This should always be used instead of remove_deep. See #1812. The start
    element must have no inverses. The subgraph to be purged is calculated using
    all forward relationships determined by the traverse() function.

    The deletion process starts at element and traverses forward through the
    subgraph. Each subelement is checked for any inverses outside the subgraph.
    If there are no inverses outside, it may be safely purged. If there are
    inverses that aren't part of this subgraph, that subelement, and all of its
    subelements (i.e. that entire branch of subelements) will not be deleted as
    it is used elsewhere.

    For simple subgraphs, traverse() is sufficient to fully represent all
    related subelements. When it isn't, the ``also_consider`` argument may be
    used. These are typically inverses futher down the subelement chain.

    Note that remove_deep2 will _not_ remove elements in also_consider. Instead,
    it is only used as a consideration for whether or not an element has all
    inverses fully contained in the subgraph.

    The do_not_delete argument contains all elements that may be part of the
    subgraph but are protected from deletion.

    :param ifc_file: The IFC file object
    :type ifc_file: ifcopenshell.file.file
    :param also_consider: elements to also consider as a part of a subgraph
    :type also_consider: list[ifcopenshell.entity_instance.entity_instance], optional
    :param do_not_delete: elements to protect from deletion
    :type do_not_delete: list[ifcopenshell.entity_instance.entity_instance], optional
    :param element: The starting element that defines the subgraph
    :type element: ifcopenshell.entity_instance.entity_instance
    """
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
            and subelement not in do_not_delete
            and len(set(ifc_file.get_inverse(subelement)) - subgraph_set) == 0
        ):
            to_delete.add(subelement)
            subelement_queue.extend(ifc_file.traverse(subelement, max_levels=1)[1:])
            # See #3052. IfcOpenShell is extremely slow in removing elements if
            # the element has an inverse, and that inverse references that
            # element in a big list. The most common example is an
            # IfcPolygonalFaceSet with a Faces attribute of tens of thousands
            # of IfcIndexedPolygonalFace. In this situation, removing a
            # IfcIndexedPolygonalFace will take very, very long. If we are
            # going to delete an element (i.e. added to the to_delete set), we
            # clear any large lists (10 is an arbitrary threshold) to prevent
            # this issue.
            for i, attribute in enumerate(subelement):
                if isinstance(attribute, tuple) and len(attribute) > 10:
                    subelement[i] = []

    if getattr(ifc_file, "to_delete", None) is not None:
        ifc_file.to_delete.update(to_delete)
        return

    # We delete elements from subgraph in reverse order to allow batching to work
    for subelement in filter(lambda e: e in to_delete, subgraph[::-1]):
        ifc_file.remove(subelement)
    # ifc_file.unbatch()


def copy(ifc_file: ifcopenshell.file, element: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """
    Copy a single element. Any referenced elements are not copied.

    GlobalIds are regenerated.

    :param ifc_file: The IFC file object
    :type ifc_file: ifcopenshell.file.file
    :param element: The IFC element to copy
    :type element: ifcopenshell.entity_instance.entity_instance
    :return: The newly copied element
    :rtype: ifcopenshell.entity_instance.entity_instance
    """
    new = ifc_file.create_entity(element.is_a())
    for i, attribute in enumerate(element):
        if attribute is None:
            continue
        if new.attribute_name(i) == "GlobalId":
            new[i] = ifcopenshell.guid.new()
        else:
            new[i] = attribute
    return new


def copy_deep(
    ifc_file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    exclude: Optional[List[str]] = None,
    exclude_callback: Optional[Callable[[ifcopenshell.entity_instance], bool]] = None,
    copied_entities: Optional[dict[int, ifcopenshell.entity_instance]] = None,
) -> ifcopenshell.entity_instance:
    """
    Recursively copy an element and all of its directly related subelements.

    GlobalIds are regenerated.

    :param ifc_file: The IFC file object
    :type ifc_file: ifcopenshell.file.file
    :param element: The IFC element to copy
    :type element: ifcopenshell.entity_instance.entity_instance
    :param exclude: An optional list of strings of IFC class names to not copy.
        If any of the subelement is this class, it will not be copied and the
        original instance will be referenced.
    :type exclude: list[str],optional
    :param exclude_callback: A callback to determine whether or not to exclude
        an entity or not. Returns True to exclude and False to exclude.
    :type exclude_callback: function,optional
    :param copied_entities: A dictionary of IDs as keys and entities as values
        to reuse when coming across the same entity twice. This can typically
        be left as None.
    :type copied_entities: dict[int:ifcopenshell.entity_instance.entity_instance], optional
    :return: The newly copied element
    :rtype: ifcopenshell.entity_instance.entity_instance
    """
    if copied_entities is None:
        copied_entities = {}
    else:
        copied_entity = copied_entities.get(element.id(), None)
        if copied_entity:
            return copied_entity
    new = ifc_file.create_entity(element.is_a())
    if element.id():
        copied_entities[element.id()] = new
    for i, attribute in enumerate(element):
        if attribute is None:
            continue
        if isinstance(attribute, ifcopenshell.entity_instance):
            if exclude and any([attribute.is_a(e) for e in exclude]):
                pass
            elif exclude_callback and exclude_callback(attribute):
                pass
            else:
                attribute = copy_deep(
                    ifc_file,
                    attribute,
                    exclude=exclude,
                    copied_entities=copied_entities,
                    exclude_callback=exclude_callback,
                )
        elif isinstance(attribute, tuple) and attribute and isinstance(attribute[0], ifcopenshell.entity_instance):
            if exclude and any([attribute[0].is_a(e) for e in exclude]):
                pass
            elif exclude_callback and exclude_callback(attribute[0]):
                pass
            else:
                attribute = list(attribute)
                for j, item in enumerate(attribute):
                    attribute[j] = copy_deep(
                        ifc_file,
                        item,
                        exclude=exclude,
                        exclude_callback=exclude_callback,
                        copied_entities=copied_entities,
                    )
        if new.attribute_name(i) == "GlobalId":
            new[i] = ifcopenshell.guid.new()
        else:
            new[i] = attribute
    return new
