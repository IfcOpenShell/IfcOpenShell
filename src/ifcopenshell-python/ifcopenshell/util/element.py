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
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.representation
from typing import Any, Callable, Optional, Union, Literal, overload, Sequence, Generator
from collections import namedtuple


MATERIAL_TYPE = Literal[
    "IfcMaterial",
    "IfcMaterialConstituentSet",
    "IfcMaterialLayerSet",
    "IfcMaterialLayerSetUsage",
    "IfcMaterialProfileSet",
    "IfcMaterialProfileSetUsage",
    "IfcMaterialList",
]


def get_pset(
    element: ifcopenshell.entity_instance,
    name: str,
    prop: Optional[str] = None,
    psets_only: bool = False,
    qtos_only: bool = False,
    should_inherit: bool = True,
    verbose: bool = False,
) -> Union[Any, dict[str, Any]]:
    """Retrieve a single property set or single property

    This is more efficient than ifcopenshell.util.element.get_psets if you know
    exactly which property set and property you are after.

    If should_inherit is true, the pset "id" only refers to the ID of the
    occurrence, not the type's pset.

    :param element: The IFC Element entity
    :param name: The name of the pset
    :param prop: The name of the property
    :param psets_only: Default as False. Set to true if only property sets are needed.
    :param qtos_only: Default as False. Set to true if only quantities are needed.
    :param should_inherit: Default as True. Set to false if you don't want to inherit property sets from the Type.
    :return: A dictionary of property names and values, or a single value if a
        property is specified.

    Example:

    .. code:: python

        element = ifc_file.by_type("IfcWall")[0]
        psets_and_qtos = ifcopenshell.util.element.get_pset(element, "Pset_WallCommon")
    """
    pset = None
    type_pset = None
    ifc_file = element.file
    is_ifc2x3 = ifc_file.schema == "IFC2X3"
    is_profile = False

    if element.is_a("IfcTypeObject"):
        for definition in element.HasPropertySets or []:
            if definition.Name == name:
                pset = definition
                break
    elif (
        (is_ifc2x3_material := (is_ifc2x3 and element.is_a("IfcMaterial")))
        or element.is_a("IfcMaterialDefinition")
        or (is_profile := element.is_a("IfcProfileDef"))
    ):
        if is_ifc2x3_material:
            # Support extended props as they do have a name.
            for definition in ifc_file.by_type("IfcExtendedMaterialProperties"):
                if definition.Material == element and definition.Name == name:
                    pset = definition
                    break
        elif is_ifc2x3 and is_profile:
            # Don't support them as they don't have a name.
            pass
        else:
            # IfcProfileDef or IfcMaterialDefinition, IFC4+.
            for definition in element.HasProperties or []:
                if definition.Name == name:
                    pset = definition
                    break
    elif (is_defined_by := getattr(element, "IsDefinedBy", None)) is not None:
        # other IfcObjectDefinition
        if should_inherit:
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                type_pset = get_pset(element_type, name, prop, should_inherit=False, verbose=verbose)
        for relationship in is_defined_by:
            if relationship.is_a("IfcRelDefinesByProperties"):
                definition = relationship.RelatingPropertyDefinition
                if definition.Name == name:
                    pset = definition
                    break

    if pset:
        if (
            psets_only
            and not pset.is_a("IfcPropertySet")
            and not (is_ifc2x3 and pset.is_a("IfcExtendedMaterialProperties"))
        ):
            pset = None
        elif qtos_only and not pset.is_a("IfcElementQuantity"):
            pset = None

    if type_pset is not None and not prop:
        if psets_only or qtos_only:
            type_pset_element = element.file.by_id(type_pset["id"])
            if psets_only and not type_pset_element.is_a("IfcPropertySet"):
                type_pset = None
            elif qtos_only and not type_pset_element.is_a("IfcElementQuantity"):
                type_pset = None

    if pset is None and type_pset is None:
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
    :param psets_only: Default as False. Set to true if only property sets are needed.
    :param qtos_only: Default as False. Set to true if only quantities are needed.
    :param should_inherit: Default as True. Set to false if you don't want to inherit property sets from the Type.
    :param verbose: More detailed prop values, defaults to False.
    :return: Key, value pair of psets' names and their properties' names & values

    Example:

    .. code:: python

        element = ifc_file.by_type("IfcWall")[0]
        psets = ifcopenshell.util.element.get_psets(element, psets_only=True)
        qsets = ifcopenshell.util.element.get_psets(element, qtos_only=True)
        psets_and_qtos = ifcopenshell.util.element.get_psets(element)
    """
    ifc_file = element.file
    is_ifc2x3 = ifc_file.schema == "IFC2X3"
    psets = {}
    if element.is_a("IfcTypeObject"):
        for definition in element.HasPropertySets or []:
            if psets_only and not definition.is_a("IfcPropertySet"):
                continue
            if qtos_only and not definition.is_a("IfcElementQuantity"):
                continue
            psets.setdefault(definition.Name, {}).update(get_property_definition(definition, verbose=verbose))
    # NOTE: doesn't account for IFC2X3 missing HasProperties
    elif (
        (is_ifc2x3_material := (is_ifc2x3 and element.is_a("IfcMaterial")))
        or element.is_a("IfcMaterialDefinition")
        or element.is_a("IfcProfileDef")
    ):
        definitions: list[ifcopenshell.entity_instance]
        if is_ifc2x3:
            if is_ifc2x3_material:
                # Only extended props have a name.
                definitions = [d for d in ifc_file.by_type("IfcExtendedMaterialProperties") if d.Material == element]
            else:
                # Ignoring profiles as they don't have names.
                definitions = []
        else:
            definitions = getattr(element, "HasProperties", None) or []
        for definition in definitions:
            if qtos_only:
                continue
            psets.setdefault(definition.Name, {}).update(get_property_definition(definition, verbose=verbose))
    elif (is_defined_by := getattr(element, "IsDefinedBy", None)) is not None:
        # other IfcObjectDefinition
        if should_inherit:
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                psets = get_psets(
                    element_type, psets_only=psets_only, qtos_only=qtos_only, should_inherit=False, verbose=verbose
                )
        for relationship in is_defined_by:
            if relationship.is_a("IfcRelDefinesByProperties"):
                definition = relationship.RelatingPropertyDefinition
                if psets_only and not definition.is_a("IfcPropertySet"):
                    continue
                if qtos_only and not definition.is_a("IfcElementQuantity"):
                    continue
                psets.setdefault(definition.Name, {}).update(get_property_definition(definition, verbose=verbose))
    return psets


@overload
def get_property_definition(
    definition: Optional[ifcopenshell.entity_instance], prop: None = None, verbose=False
) -> dict[str, Any]: ...
@overload
def get_property_definition(definition: Optional[ifcopenshell.entity_instance], prop: str, verbose=False) -> Any: ...
@overload
def get_property_definition(definition: None, prop: None = None, verbose: bool = False) -> None: ...
def get_property_definition(
    definition: Optional[ifcopenshell.entity_instance], prop: Optional[str] = None, verbose=False
) -> Union[Any, dict[str, Any]]:
    """if prop name is not provided in `prop`, will return dict of all available properties
    otherwise will return the value of the specified `prop`.
    """
    if not definition:
        return

    ifc_class = definition.is_a()

    if prop:
        if ifc_class == "IfcElementQuantity":
            return get_quantity(definition.Quantities, prop, verbose=verbose)
        elif ifc_class == "IfcPropertySet":
            return get_property(definition.HasProperties, prop, verbose=verbose)
        elif ifc_class == "IfcMaterialProperties" or ifc_class == "IfcProfileProperties":
            # IfcExtendedProperties
            return get_property(definition.Properties, prop, verbose=verbose)
        elif ifc_class == "IfcExtendedMaterialProperties":
            # IFC2X3.
            return get_property(definition.ExtendedProperties, prop, verbose=verbose)
        else:
            # Entity introduced in IFC4
            # definition.is_a('IfcPreDefinedPropertySet'):
            for i in range(4, len(definition)):
                if definition.attribute_name(i) == prop:
                    if (v := definition[i]) is not None:
                        return v
        return

    props = {}
    if ifc_class == "IfcElementQuantity":
        # 5 IfcElementQuantity.Quantities
        props.update(get_quantities(definition[5], verbose=verbose))
    elif ifc_class == "IfcPropertySet":
        # 5 IfcPropertySet.HasProperties
        props.update(get_properties(definition[4], verbose=verbose))
    elif ifc_class == "IfcMaterialProperties" or ifc_class == "IfcProfileProperties":
        # 2 IfcExtendedProperties.Properties
        props.update(get_properties(definition[2], verbose=verbose))
    elif ifc_class == "IfcExtendedMaterialProperties":
        # 1 IfcExtendedMaterialProperties.ExtendedProperties
        props.update(get_properties(definition[1], verbose=verbose))
    else:
        # Entity introduced in IFC4
        # definition.is_a('IfcPreDefinedPropertySet'):
        for prop_i in range(4, len(definition)):
            if (v := definition[prop_i]) is not None:
                props[definition.attribute_name(prop_i)] = v
    props["id"] = definition.id()
    return props


@overload
def get_quantity(quantities: list[ifcopenshell.entity_instance], name: str, verbose: Literal[False] = False) -> Any: ...
@overload
def get_quantity(
    quantities: list[ifcopenshell.entity_instance], name: str, verbose: Literal[True]
) -> dict[str, Any]: ...
def get_quantity(
    quantities: list[ifcopenshell.entity_instance], name: str, verbose=False
) -> Union[Any, dict[str, Any]]:
    for quantity in quantities or []:
        # 0 IfcPhysicalQuantity.Name
        if quantity[0] != name:
            continue
        if quantity.is_a("IfcPhysicalSimpleQuantity"):
            # 3 IfcPhysicalSimpleQuantity.XXXValue
            result = quantity[3]
        elif quantity.is_a("IfcPhysicalComplexQuantity"):
            data = {k: v for k, v in quantity.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_quantities(quantity.HasQuantities, verbose=verbose)
            del data["HasQuantities"]
            result = data
        if verbose:
            result = {"id": quantity.id(), "class": quantity.is_a(), "value": result}
        return result


@overload
def get_quantities(
    quantities: list[ifcopenshell.entity_instance], verbose: Literal[False] = False
) -> dict[str, Any]: ...
@overload
def get_quantities(
    quantities: list[ifcopenshell.entity_instance], verbose: Literal[True]
) -> dict[str, dict[str, Any]]: ...
def get_quantities(
    quantities: list[ifcopenshell.entity_instance], verbose=False
) -> dict[str, Union[Any, dict[str, Any]]]:
    results = {}
    for quantity in quantities or []:
        # 0 IfcPhysicalQuantity.Name
        quantity_name = quantity[0]
        if quantity.is_a("IfcPhysicalSimpleQuantity"):
            # 3 IfcPhysicalSimpleQuantity.XXXValue
            results[quantity_name] = quantity[3]
            if verbose:
                results[quantity_name] = {
                    "id": quantity.id(),
                    "class": quantity.is_a(),
                    "value": results[quantity_name],
                }
        elif quantity.is_a("IfcPhysicalComplexQuantity"):
            data = {k: v for k, v in quantity.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_quantities(quantity.HasQuantities, verbose=verbose)
            del data["HasQuantities"]
            results[quantity_name] = data
            if verbose:
                results[quantity_name] = {
                    "id": data["id"],
                    "class": data["class"],
                    "value": results[quantity_name],
                }
    return results


@overload
def get_property(properties: list[ifcopenshell.entity_instance], name: str, verbose: Literal[False] = False) -> Any: ...
@overload
def get_property(
    properties: list[ifcopenshell.entity_instance], name: str, verbose: Literal[True]
) -> dict[str, Any]: ...
def get_property(
    properties: list[ifcopenshell.entity_instance], name: str, verbose=False
) -> Union[Any, dict[str, Any]]:
    for prop in properties or []:
        if prop.Name != name:
            continue
        is_single_value = False  # For now we pass value type only for single values.
        if prop.is_a("IfcPropertySingleValue"):
            # 2 IfcPropertySingleValue.NominalValue
            result = v.wrappedValue if (v := prop[2]) else None
            result_type = v.is_a() if v else None
            is_single_value = True
        elif prop.is_a("IfcPropertyEnumeratedValue"):
            # 2 IfcPropertyEnumeratedValue.EnumerationValues
            result = [v.wrappedValue for v in values] if (values := prop[2]) else None
        elif prop.is_a("IfcPropertyListValue"):
            # 2 IfcPropertyListValue.ListValues
            result = [v.wrappedValue for v in values] if (values := prop[2]) else None
        elif prop.is_a("IfcPropertyBoundedValue"):
            data = prop.get_info()
            del data["Unit"]
            result = data
        elif prop.is_a("IfcPropertyTableValue"):
            result = prop.get_info()
        elif prop.is_a("IfcComplexProperty"):
            data = {k: v for k, v in prop.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_properties(prop.HasProperties, verbose=verbose)
            del data["HasProperties"]
            result = data
        if verbose:
            result = {"id": prop.id(), "class": prop.is_a(), "value": result}
            if is_single_value:
                result["value_type"] = result_type
        return result


@overload
def get_properties(
    properties: list[ifcopenshell.entity_instance], verbose: Literal[False] = False
) -> dict[str, Any]: ...
@overload
def get_properties(
    properties: list[ifcopenshell.entity_instance], verbose: Literal[True]
) -> dict[str, dict[str, Any]]: ...
def get_properties(
    properties: list[ifcopenshell.entity_instance], verbose=False
) -> dict[str, Union[Any, dict[str, Any]]]:
    results = {}
    for prop in properties or []:
        ifc_class = prop.is_a()
        prop_name = prop[0]  # 0 IfcProperty.Name
        if ifc_class == "IfcPropertySingleValue":
            # 2 IfcPropertySingleValue.NominalValue
            results[prop_name] = v.wrappedValue if (v := prop[2]) else None
            if verbose:
                results[prop_name] = {
                    "id": prop.id(),
                    "class": prop.is_a(),
                    "value": results[prop_name],
                    "value_type": v.is_a() if v else None,
                }
        elif ifc_class == "IfcPropertyEnumeratedValue":
            # 2 IfcPropertyEnumeratedValue.EnumerationValues
            results[prop_name] = [v.wrappedValue for v in values] if (values := prop[2]) else None
            if verbose:
                results[prop_name] = {
                    "id": prop.id(),
                    "class": prop.is_a(),
                    "value": results[prop_name],
                }
        elif ifc_class == "IfcPropertyListValue":
            # 2 IfcPropertyListValue.ListValues
            results[prop_name] = [v.wrappedValue for v in values] if (values := prop[2]) else None
            if verbose:
                results[prop_name] = {
                    "id": prop.id(),
                    "class": prop.is_a(),
                    "value": results[prop_name],
                }
        elif ifc_class == "IfcPropertyBoundedValue":
            data = prop.get_info()
            del data["Unit"]
            results[prop_name] = data
            if verbose:
                results[prop_name] = {
                    "id": data["id"],
                    "class": data["type"],
                    "value": results[prop_name],
                }
        elif ifc_class == "IfcPropertyTableValue":
            data = prop.get_info()
            results[prop_name] = data
            if verbose:
                results[prop_name] = {
                    "id": data["id"],
                    "class": data["type"],
                    "value": results[prop_name],
                }
        elif ifc_class == "IfcComplexProperty":
            data = {k: v for k, v in prop.get_info().items() if v is not None and k != "Name"}
            data["properties"] = get_properties(prop.HasProperties, verbose=verbose)
            del data["HasProperties"]
            results[prop_name] = data
            if verbose:
                results[prop_name] = {"id": data["id"], "class": data["class"], "value": results[prop_name]}
    return results


def get_elements_by_pset(pset: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
    """Retrieve the elements (or element types) that are using the provided property set."""
    is_ifc2x3 = pset.file.schema == "IFC2X3"
    elements = set()
    if pset.is_a("IfcPropertySet") or pset.is_a("IfcElementQuantity"):
        rels = pset.PropertyDefinitionOf if is_ifc2x3 else pset.DefinesOccurrence
        for rel in rels:
            elements.update(rel.RelatedObjects)
        for element_type in pset.DefinesType:
            elements.add(element_type)
    elif pset.is_a("IfcProfileProperties"):
        elements.add(pset.ProfileDefinition)
    elif pset.is_a("IfcMaterialProperties"):
        elements.add(pset.Material)
    else:
        raise Exception(f"Unexpected pset type: '{pset.is_a()}' ({pset}).")
    return elements


def get_element_mass_density(element: ifcopenshell.entity_instance) -> Union[float, None]:
    """Calculate object mass density based on material's Pset_MaterialCommon.MassDensity.

    :param element: IFC element entity.
    :return: ``float`` mass density in project units if calculation was successful, ``None`` if element either
        doesn't have a material or this type of material is not supported.
    """
    material = ifcopenshell.util.element.get_material(element)
    if material is None:
        return

    if (
        material.is_a("IfcMaterialLayerSet")
        or material.is_a("IfcMaterialProfileSet")
        or material.is_a("IfcMaterialConstituentSet")
    ):
        return

    if material.is_a("IfcMaterial"):
        material_mass_density = ifcopenshell.util.element.get_pset(material, "Pset_MaterialCommon", "MassDensity")
        return material_mass_density

    if material.is_a("IfcMaterialLayerSetUsage"):
        material_layers = material.ForLayerSet.MaterialLayers
        densities = []
        thicknesses = []
        obj_mass_density = 0
        for material_layer in material_layers:
            material_mass_density = ifcopenshell.util.element.get_pset(
                material_layer.Material, "Pset_MaterialCommon", "MassDensity"
            )
            if material_mass_density is None:
                return
            densities.append(material_mass_density)
            thickness = material_layer.LayerThickness
            thicknesses.append(thickness)
            obj_mass_density = obj_mass_density + (material_mass_density * thickness)
        total_thickness = sum(thicknesses)
        obj_mass_density = obj_mass_density / total_thickness
        return obj_mass_density

    if material.is_a("IfcMaterialProfileSetUsage"):
        material_profiles = material.ForProfileSet.MaterialProfiles
        if len(material_profiles) == 1:
            material_mass_density = ifcopenshell.util.element.get_pset(
                material_profiles[0].Material, "Pset_MaterialCommon", "MassDensity"
            )
            return material_mass_density
        else:
            return


def get_predefined_type(element: ifcopenshell.entity_instance) -> Union[str, None]:
    """Retrieves the PrefefinedType attribute of an element.

    If the predefined type is user defined, the custom type (such as object
    type, element type, or process type depending on the class) is returned
    instead.  Predefined types from the associated type element are also
    considered first.

    :param element: The IFC Element entity
    :return: The predefined type of the element

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
    """
    if element_type := get_type(element):
        predefined_type = getattr(element_type, "PredefinedType", None)
        if predefined_type == "USERDEFINED" or not predefined_type:
            predefined_type = getattr(element_type, "ElementType", ...)
            if predefined_type == ...:
                predefined_type = getattr(element_type, "ProcessType", None)
        if predefined_type and predefined_type != "NOTDEFINED":
            return predefined_type

    predefined_type = getattr(element, "PredefinedType", None)
    if predefined_type == "USERDEFINED" or not predefined_type:
        predefined_type = getattr(element, "ObjectType", None)
    return predefined_type


def get_type(element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    """Retrieves the construction type element of an element occurrence.

    Note: `get_type(type_element) == type_element`.

    :param element: The element occurrence (IfcObject)
    :return: The related type element

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        element_type = ifcopenshell.util.element.get_type(element)
    """
    if element.is_a("IfcTypeObject"):
        return element

    schema = element.file.schema
    if schema != "IFC2X3":
        if is_typed_by := getattr(element, "IsTypedBy", ()):
            return is_typed_by[0].RelatingType
        return

    if is_defined_by := getattr(element, "IsDefinedBy", ()):  # IFC2X3
        for relationship in is_defined_by:
            if relationship.is_a("IfcRelDefinesByType"):
                return relationship.RelatingType


def get_types(type: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """Get all the occurrences of a type element

    :param type: The type element
    :return: A list of occurrences of that type

    Example:

    .. code:: python

        element_type = ifcopenshell.by_type("IfcWallType")[0]
        walls = ifcopenshell.util.element.get_types(element_type)
    """
    if type.file.schema == "IFC2X3":
        if object_type_of := getattr(type, "ObjectTypeOf", ()):
            return object_type_of[0].RelatedObjects
    else:
        if types := getattr(type, "Types", ()):
            return types[0].RelatedObjects
    return []


def get_shape_aspects(
    element: ifcopenshell.entity_instance,
    should_inherit: bool = True,
) -> list[ifcopenshell.entity_instance]:
    """Get element's shape aspects.

    :param element: IfcProduct or IfcTypeProduct.
    :param should_inherit: If True, the shape aspects of the element's type will be considered.
        Useful in cases when IfcShapeAspects are assigned to the type's IfcRepresentationMap
        instead of the element's IfcProductDefinitionShape.
    :return: The associated shape aspects of the element.

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        shape_aspect = ifcopenshell.util.element.get_shape_aspects(element)
    """

    # IfcProduct
    if (representation := getattr(element, "Representation", ...)) != ...:
        shape_aspects: list[ifcopenshell.entity_instance] = []
        if should_inherit and (element_type := get_type(element)):
            shape_aspects.extend(get_shape_aspects(element_type))
        shape_aspects.extend(representation.HasShapeAspects)
        return shape_aspects

    if element.file.schema == "IFC2X3":
        return []

    # IfcTypeProduct
    shape_aspects = []
    for representation_map in element.RepresentationMaps or []:
        shape_aspects += representation_map.HasShapeAspects
    return shape_aspects


def get_material(
    element: ifcopenshell.entity_instance, should_skip_usage=False, should_inherit=True
) -> Union[ifcopenshell.entity_instance, None]:
    """Gets the material of the element

    The material may be a single material, material set (layered, profiled, or
    constituent), or a material set usage.

    :param element: The element to get the material of.
    :param should_skip_usage: If set to True, if the material is a material set
        usage, the material set itself will be returned. Useful if you don't
        care about occurrence usage parameters. If False, the usage will be
        returned.
    :param should_inherit: If True, any inherited materials from associated
        types will be considered.
    :return: The associated material of the element or `None`.

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        material = ifcopenshell.util.element.get_material(element)
    """
    if (has_associations := getattr(element, "HasAssociations", None)) is not None and has_associations:
        for relationship in has_associations:
            if relationship.is_a("IfcRelAssociatesMaterial"):
                if should_skip_usage:
                    relating_material = relationship.RelatingMaterial
                    if relating_material.is_a("IfcMaterialLayerSetUsage"):
                        return relating_material.ForLayerSet
                    elif relating_material.is_a("IfcMaterialProfileSetUsage"):
                        return relating_material.ForProfileSet
                return relationship.RelatingMaterial
    if should_inherit:
        relating_type = get_type(element)
        if relating_type != element and (has_associations := getattr(relating_type, "HasAssociations", None)):
            return get_material(relating_type, should_skip_usage)


def get_materials(
    element: ifcopenshell.entity_instance, should_inherit: bool = True
) -> list[ifcopenshell.entity_instance]:
    """Gets individual materials of an element

    If the element has a material set, the individual materials of that set are
    returned as a list.

    :param element: The element to get the materials of.
    :param should_inherit: If True, any inherited materials from associated
        types will be considered.
    :return: The associated materials of the element.

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
    else:
        assert False, f"Unexpected material type: {material.is_a()}"


def get_styles(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """Retrieves the styles used in an element's representation.

    Styles may be retreived from the material or the body representation.

    :param element: The element to get the styles of.
    :return: A list of surface styles

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


# TODO: ifc_file argument is unnecessary for some methods now
# since we have entity_instance.file, so we can deprecate it.
def get_elements_by_material(
    ifc_file: Union[ifcopenshell.file, None], material: ifcopenshell.entity_instance
) -> set[ifcopenshell.entity_instance]:
    """Retrieves the elements related to a material.

    This includes elements using the material as part of a material set or set
    usage.

    :param ifc_file: The IFC file
    :param material: The IFC Material entity
    :return: A set of elements using the to the material

    Example:

    .. code:: python

        material = file.by_type("IfcMaterial")[0]
        elements = ifcopenshell.util.element.get_elements_by_material(file, material)
    """
    if not ifc_file:
        ifc_file = material.file
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
    ifc_file: Union[ifcopenshell.file, None], style: ifcopenshell.entity_instance
) -> set[ifcopenshell.entity_instance]:
    """Retrieves the elements whose geometric representation uses a style

    :param ifc_file: The IFC file
    :param style: The IfcPresentationStyle entity
    :return: The elements related to the style

    Example:

    .. code:: python

        style = file.by_type("IfcSurfaceStyle")[0]
        elements = ifcopenshell.util.element.get_elements_by_style(file, style)
    """
    if not ifc_file:
        ifc_file = style.file
    results = set()
    inverses = list(ifc_file.get_inverse(style))
    while inverses:
        inverse = inverses.pop()
        inverse_class = inverse.is_a()
        # IfcPresentationStyleAssignment for < IFC4X3.
        # IfcFillAreaStyleHatching->IfcFillAreaStyle only for IfcCurveStyle.
        # IfcFillAreaStyleTiles->IfcFillAreaStyle is not restricted to IfcCurveStyle.
        if inverse_class in (
            "IfcPresentationStyleAssignment",
            "IfcFillAreaStyleHatching",
            "IfcFillAreaStyle",
            "IfcFillAreaStyleTiles",
        ):
            inverses.extend(ifc_file.get_inverse(inverse))
            continue
        if not inverse.is_a("IfcStyledItem"):
            continue
        if geometry_item := inverse.Item:
            for inverse_ in ifc_file.get_inverse(geometry_item):
                if inverse_.is_a("IfcShapeRepresentation"):
                    results.update(get_elements_by_representation(ifc_file, inverse_))
            # IfcFillAreaStyleTiles requires .Item to be set.
            inverses.extend(ifc_file.get_inverse(inverse))
        else:
            styled_reps = [i for i in ifc_file.get_inverse(inverse) if i.is_a("IfcStyledRepresentation")]
            for styled_rep in styled_reps:
                for material_def_rep in styled_rep.OfProductRepresentation:
                    results.update(get_elements_by_material(ifc_file, material_def_rep.RepresentedMaterial))
    return results


def get_elements_by_representation(
    ifc_file: Union[ifcopenshell.file, None], representation: ifcopenshell.entity_instance
) -> set[ifcopenshell.entity_instance]:
    """Gets all elements using a geometric representation

    :param ifc_file: The IFC file
    :param representation: The IfcShapeRepresentation representation
    :return: The elements using the geometric representation

    Example:

    .. code:: python

        representation = file.by_type("IfcShapeRepresentation")[0]
        elements = ifcopenshell.util.element.get_elements_by_representation(file, representation)
    """
    if not ifc_file:
        ifc_file = representation.file
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


def get_elements_by_profile(profile: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
    """Get all elements using provided IfcProfileDef.

    Skip elements that have the profile in IfcMaterialProfileSet
    but not actually use it in their representations.

    :param profile: IfcProfileDef:
    :return: The elements using the profile.
    """
    ifc_file = profile.file
    queue = ifc_file.get_inverse(profile)
    processed: set[ifcopenshell.entity_instance] = set()
    representations: set[ifcopenshell.entity_instance] = set()
    while queue:
        item = queue.pop()
        if item.is_a("IfcRepresentationItem"):
            queue.update(i for i in ifc_file.get_inverse(item) if i not in processed)
        elif item.is_a("IfcShapeRepresentation"):
            representations.add(item)
        else:
            pass
        processed.add(item)

    elements = set()
    for representation in representations:
        elements.update(get_elements_by_representation(ifc_file, representation))
    return elements


def get_elements_by_layer(
    ifc_file: Union[ifcopenshell.file, None], layer: ifcopenshell.entity_instance
) -> set[ifcopenshell.entity_instance]:
    """Get all the elements that are used by a presentation layer

    :param ifc_file: The IFC file
    :param layer: The IfcPresentationLayerAssignment layer
    :return: The elements using the geometric representation
    """
    if not ifc_file:
        ifc_file = layer.file
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
    ifc_file: Union[ifcopenshell.file, None], element: ifcopenshell.entity_instance
) -> list[ifcopenshell.entity_instance]:
    """Get the CAD layers that an element is part of

    An element may have portions or all of its geometry assigned to a
    traditional CAD presentation layer.

    :param ifc_file: The IFC file object
    :param element: The IFC element to interrogate
    :return: A list of IfcPresentationLayerAssignment

    Example:

    .. code:: python

        element = ifcopenshell.by_type("IfcWall")[0]
        layers = ifcopenshell.util.element.get_layers(element)
    """
    if not ifc_file:
        ifc_file = element.file
    layers = []
    representations = []
    if representation := getattr(element, "Representation", None):
        representations = [representation]
    elif representation_maps := getattr(element, "RepresentationMaps", None):
        representations = representation_maps
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
    element: ifcopenshell.entity_instance, should_get_direct: bool = False, ifc_class: Optional[str] = None
) -> Union[ifcopenshell.entity_instance, None]:
    """
    Retrieves the spatial structure container of an element.

    :param element: The IFC element
    :param should_get_direct: If True, a result is only returned if the element
        is directly contained in a spatial structure element. If False, an
        indirect spatial container may be returned, such as if an element is a
        part of an aggregate, and then if that aggregate is contained in a
        spatial structure element.
    :param ifc_class: Optionally filter the type of container you're after. For
        example, you may be after the storey, not a space.
    :return: The direct or indirect container of the element or None.

    Example:

    .. code:: python

        element = file.by_type("IfcWall")[0]
        container = ifcopenshell.util.element.get_container(element)
    """
    if should_get_direct:
        if (
            contained_in_structure := getattr(element, "ContainedInStructure", None)
        ) is not None and contained_in_structure:
            container = contained_in_structure[0].RelatingStructure
            if not ifc_class:
                return container
            if container.is_a(ifc_class):
                return container
    elif contained_in_structure := getattr(element, "ContainedInStructure", None):
        container = contained_in_structure[0].RelatingStructure
        if not ifc_class:
            return container
        while container:
            if container.is_a(ifc_class):
                return container
            container = get_aggregate(container)
    elif parent := get_parent(element):
        return get_container(parent, should_get_direct, ifc_class)


def get_referenced_structures(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """Retreives a list of referenced spatial elements

    Typically useful for multistorey elements, such as columns or facade
    elements, or elements that span multiple spaces or in-between spaces, such
    as stairs, doors, etc.

    :param element: The IFC element
    :return: A list of IfcSpatialElement

    Example:

    .. code:: python

        element = file.by_type("IfcWall")[0]
        print(ifcopenshell.util.element.get_referenced_structures(element))
    """
    return [r.RelatingStructure for r in getattr(element, "ReferencedInStructures", [])]


def get_structure_referenced_elements(structure: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
    """Retreives a set of elements referenced by a structure

    :param structure: IfcSpatialElement
    :return: A set of referenced elements, IfcSpatialReferenceSelect

    Example:

    .. code:: python

        element = file.by_type("IfcBuildingStorey")[0]
        print(ifcopenshell.util.element.get_structure_referenced_elements(element))
    """
    referenced = set()
    for rel in structure.ReferencesElements:
        referenced.update(rel.RelatedElements)
    return referenced


def get_decomposition(element: ifcopenshell.entity_instance, is_recursive=True) -> set[ifcopenshell.entity_instance]:
    """
    Retrieves all subelements of an element based on the spatial decomposition
    hierarchy. This includes all subspaces and elements contained in subspaces,
    parts of an aggregate, all openings, and all fills of any openings.

    :param element: The IFC element
    :return: The decomposition of the element

    Example:

    .. code:: python

        element = file.by_type("IfcProject")[0]
        decomposition = ifcopenshell.util.element.get_decomposition(element)
    """
    queue = [element]
    results = set()
    while queue:
        element = queue.pop()
        for rel in getattr(element, "ContainsElements", []):
            related = rel.RelatedElements
            queue.extend(related)
            results.update(related)
        for rel in getattr(element, "IsDecomposedBy", []):
            related = rel.RelatedObjects
            queue.extend(related)
            results.update(related)
        for rel in getattr(element, "HasOpenings", []):
            related = rel.RelatedOpeningElement
            queue.append(related)
            results.add(related)
        for rel in getattr(element, "HasFillings", []):
            related = rel.RelatedBuildingElement
            queue.append(related)
            results.add(related)
        for rel in getattr(element, "IsNestedBy", []):
            related = rel.RelatedObjects
            queue.extend(related)
            results.update(related)
        if not is_recursive:
            break
    return results


def get_grouped_by(
    element: ifcopenshell.entity_instance, is_recursive: bool = True
) -> list[ifcopenshell.entity_instance]:
    """Retrieves all subelements of an element based on the group.

    :param element: IfcGroup entity
    :return: All subelements of the group

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
            related_objects = rel.RelatedObjects
            queue.extend(related_objects)
            results.extend(related_objects)
        if not is_recursive:
            break
    return results


def get_groups(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """
    Retrieves the groups of an element.

    :param element: The IFC element
    :return: List of IfcGroups element is assigned to.

    Example:

    .. code:: python

        wall = file.by_type("IfcWall")[0]
        group = ifcopenshell.util.element.get_groups(element)[0]
    """
    groups = []
    for rel in element.HasAssignments:
        if rel.is_a("IfcRelAssignsToGroup"):
            groups.append(rel.RelatingGroup)
    return groups


def get_parent(element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    """Get the parent in the spatial heirarchy

    IFC features a spatial hierarchy tree of all objects. Each spatial element
    or physical element must be located inside this hierarchy exactly once.

    The top level parent of this tree is the IfcProject, which has no parent.

    All children may have parent-child relationships of one of the following types:

    - Spatial containment: a physical object is located in a space
    - Aggregation: a physical object is broken up into parts, or a spatial location is split into sub locations
    - Nesting: components are attached to a host parent
    - Filling: the physical element fills an opening, such as a window filling a hole
    - Voiding: the opening voids another physical element, such as a hole in a wall

    :param element: Any physical or spatial element in the tree
    :return: Its parent. This must exist for any valid file, or None if we've reached the IfcProject.

    Example:

    .. code:: python

        element = file.by_type("IfcWall")[0]
        parent = ifcopenshell.util.element.get_parent(element)
    """
    return (
        get_container(element, should_get_direct=True)
        or get_aggregate(element)
        or get_nest(element)
        or get_filled_void(element)
        or get_voided_element(element)
    )


def get_filled_void(element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    """If the element is filling a void, get the void

    Examples include windows and doors which fill a opening inside a wall.

    :param element: The building element, typically a window or door
    :return: The IfcOpeningElement that it is filling

    Example:

    .. code:: python

        window = file.by_type("IfcWindow")[0]
        opening = ifcopenshell.util.element.get_filled_void(window)
    """
    if rel := getattr(element, "FillsVoids", None):
        return rel[0].RelatingOpeningElement


def get_voided_element(element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    """For an opening, get the building element that the opening is voiding

    For all valid models, this should never return None.

    :param element: The IfcOpeningElement
    :return: The building element, such as a wall or slab

    Example:

    .. code:: python

        opening = file.by_type("IfcOpeningElement")[0]
        element = ifcopenshell.util.element.get_voided_element(opening)
    """
    if rel := getattr(element, "VoidsElements", None):
        return rel[0].RelatingBuildingElement


def get_aggregate(element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    """
    Retrieves the aggregate parent of an element.

    :param element: The IFC element
    :return: The aggregate of the element

    Example:

    .. code:: python

        element = file.by_type("IfcBeam")[0]
        aggregate = ifcopenshell.util.element.get_aggregate(element)
    """
    if decomposes := getattr(element, "Decomposes", None):
        is_not_ifc2x3 = element.file.schema != "IFC2X3"
        if is_not_ifc2x3 or decomposes[0].is_a("IfcRelAggregates"):
            return decomposes[0].RelatingObject


def get_nest(element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    """
    Retrieves the nest parent of an element.

    :param element: The IFC element
    :return: The nested whole of the element

    Example:

    .. code:: python

        element = file.by_type("IfcBeam")[0]
        aggregate = ifcopenshell.util.element.get_nest(element)
    """
    is_ifc2x3 = element.file.schema == "IFC2X3"
    if is_ifc2x3:
        if not (decomposes := getattr(element, "Decomposes", None)):
            return
        if decomposes[0].is_a("IfcRelNests"):
            return decomposes[0].RelatingObject
    else:
        if nests := getattr(element, "Nests", None):
            return nests[0].RelatingObject


def get_parts(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """
    Retrieves the parts of an element that have an aggregation relationship.

    :param element: The IFC element
    :return: The parts of the element

    Example:

    .. code:: python

        element = file.by_type("IfcElementAssembly")[0]
        parts = ifcopenshell.util.element.get_parts(element)
    """
    objects: list[ifcopenshell.entity_instance] = []
    is_not_ifc2x3 = element.file.schema != "IFC2X3"
    if is_decomposed_by := getattr(element, "IsDecomposedBy", ()):
        for rel in is_decomposed_by:
            if is_not_ifc2x3 or rel.is_a("IfcRelAggregates"):
                objects.extend(rel.RelatedObjects)
    return objects


def get_contained(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """
    Retrieves the contained elements of spatial element.

    :param element: The IFC element
    :return: The parts of the element

    Example:

    .. code:: python

        element = file.by_type("IfcBuildingStorey")[0]
        elements = ifcopenshell.util.element.get_contained(element)
    """
    objects: list[ifcopenshell.entity_instance] = []
    if contains_elements := getattr(element, "ContainsElements", ()):
        for rel in contains_elements:
            objects.extend(rel.RelatedElements)
    return objects


def get_components(
    element: ifcopenshell.entity_instance, include_ports: bool = False
) -> list[ifcopenshell.entity_instance]:
    """
    Retrieves the components of an element that have an nest relationship.

    For nested ports, see ifcopenshell.util.system.

    :param element: The IFC element
    :param include_ports: Default as False. Set to true if you also want to get ports.
    :return: The components of the element

    Example:

    .. code:: python

        element = file.by_type("IfcElementAssembly")[0]
        components = ifcopenshell.util.element.get_components(element)
    """
    objects: list[ifcopenshell.entity_instance] = []
    is_ifc2x3 = element.file.schema == "IFC2X3"
    if is_ifc2x3:
        if is_decomposed_by := getattr(element, "IsDecomposedBy", ()):
            for rel in is_decomposed_by:
                if rel.is_a("IfcRelNests"):
                    objects.extend(rel.RelatedObjects)
    else:
        if is_nested_by := getattr(element, "IsNestedBy", None):
            for rel in is_nested_by:
                objects.extend(rel.RelatedObjects)
    if include_ports:
        return objects
    return [e for e in objects if not e.is_a("IfcPort")]


ReferenceData = namedtuple("ReferenceData", "inverse_attribute, rel_class, relating_element_attribute")

# References below are omitted because they do not introduce
# any additional referenced objects besides the objects
# from their supertype IfcExternalReference
# - IfcExternallyDefinedHatchStyle
# - IfcExternallyDefinedSurfaceStyle
# - IfcExternallyDefinedTextFont

REFERENCE_TYPES: dict[str, ReferenceData] = {
    "IfcClassificationReference": ReferenceData(
        "ClassificationRefForObjects",
        "IfcRelAssociatesClassification",
        "RelatingClassification",
    ),
    "IfcDocumentReference": ReferenceData("DocumentRefForObjects", "IfcRelAssociatesDocument", "RelatingDocument"),
    "IfcLibraryReference": ReferenceData("LibraryRefForObjects", "IfcRelAssociatesLibrary", "RelatingLibrary"),
    "IfcClassification": ReferenceData(
        "ClassificationForObjects", "IfcRelAssociatesClassification", "RelatingClassification"
    ),
    "IfcDocumentInformation": ReferenceData("DocumentInfoForObjects", "IfcRelAssociatesDocument", "RelatingDocument"),
    "IfcLibraryInformation": ReferenceData("LibraryInfoForObjects", "IfcRelAssociatesLibrary", "RelatingLibrary"),
}


def get_referenced_elements(reference: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
    """Get all elements with assigned `reference`

    :param reference: IfcExternalReference/IfcExternalInformation subtype reference
    :return: The elements with assigned `reference`

    Example:

    .. code:: python

        reference = file.by_type("IfcClassificationReference")[0]
        elements = ifcopenshell.util.element.get_referenced_elements(reference)
    """

    related_objects: set[ifcopenshell.entity_instance] = set()
    ifc_file = reference.file
    ifc_class = reference.is_a()

    if ifc_file.schema == "IFC2X3":
        reference_data = REFERENCE_TYPES.get(ifc_class)
        if reference_data:
            for rel in ifc_file.by_type(reference_data.rel_class):
                if getattr(rel, reference_data.relating_element_attribute) == reference:
                    related_objects.update(rel.RelatedObjects)

    else:
        if reference.is_a("IfcExternalReference"):
            # IfcExternalReference
            for external_rel in reference.ExternalReferenceForResources:
                related_objects.update(external_rel.RelatedResourceObjects)

        reference_data = REFERENCE_TYPES.get(ifc_class)
        if reference_data:
            for rel in getattr(reference, reference_data.inverse_attribute):
                related_objects.update(rel.RelatedObjects)

    return related_objects


def replace_element(element: ifcopenshell.entity_instance, replacement: ifcopenshell.entity_instance) -> None:
    for inverse in element.file.get_inverse(element):
        replace_attribute(inverse, element, replacement)


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


def remove_deep(ifc_file: Union[ifcopenshell.file, None], element: ifcopenshell.entity_instance) -> None:
    """Recursively purges a subgraph safely.

    Do not use, use remove_deep2() instead.
    """
    # @todo maybe some sort of try-finally mechanism.
    if not ifc_file:
        ifc_file = element.file
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
    :return: A newly loaded file with the elements removed.
    """
    assert ifc_file.to_delete is not None
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
    ifc_file: Union[ifcopenshell.file, None],
    element: ifcopenshell.entity_instance,
    also_consider: list[ifcopenshell.entity_instance] = [],
    do_not_delete: set[ifcopenshell.entity_instance] = set(),
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
    :param also_consider: elements to also consider as a part of a subgraph
        Order could matter for perfomance - elements that reference `element`
        directly should go first for the better performance.
    :param do_not_delete: elements to protect from deletion
    :param element: The starting element that defines the subgraph
    """
    # ifc_file.batch()
    if not ifc_file:
        ifc_file = element.file
    total_inverses = ifc_file.get_total_inverses(element)
    if total_inverses > 0:

        def are_inverses_contained() -> bool:
            also_considered_inverses = 0

            for considered_element in also_consider:
                traverse = ifc_file.traverse(considered_element, max_levels=1)
                if element in traverse:
                    also_considered_inverses += 1
                    if total_inverses == also_considered_inverses:
                        return True
            return False

        if not are_inverses_contained():
            return

    to_delete = set()
    subgraph = list(ifc_file.traverse(element, breadth_first=True))
    subgraph.extend(also_consider)
    subgraph_set = set(subgraph)
    subelement_queue = [element]
    while subelement_queue:
        subelement = subelement_queue.pop(0)
        if (
            subelement.id()
            and subelement not in do_not_delete
            and (
                # 0 or 1 inverses guarantees that the subelement only exists in this subgraph
                ifc_file.get_total_inverses(subelement) < 2
                # Alternatively, let's ensure all inverses are within the subgrpah
                or len(set(ifc_file.get_inverse(subelement)) - subgraph_set) == 0
            )
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

    if ifc_file.to_delete is not None:
        ifc_file.to_delete.update(to_delete)
        return

    # We delete elements from subgraph in reverse order to allow batching to work
    for subelement in filter(lambda e: e in to_delete, subgraph[::-1]):
        ifc_file.remove(subelement)
    # ifc_file.unbatch()


def copy(
    ifc_file: Union[ifcopenshell.file, None], element: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    """
    Copy a single element. Any referenced elements are not copied.

    GlobalIds are regenerated.

    :param ifc_file: The IFC file object
    :param element: The IFC element to copy
    :return: The newly copied element
    """
    if not ifc_file:
        ifc_file = element.file
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
    ifc_file: Union[ifcopenshell.file, None],
    element: ifcopenshell.entity_instance,
    exclude: Optional[Sequence[str]] = None,
    exclude_callback: Optional[Callable[[ifcopenshell.entity_instance], bool]] = None,
    copied_entities: Optional[dict[int, ifcopenshell.entity_instance]] = None,
) -> ifcopenshell.entity_instance:
    """
    Recursively copy an element and all of its directly related subelements.

    GlobalIds are regenerated.

    :param ifc_file: The IFC file object
    :param element: The IFC element to copy
    :param exclude: An optional list of strings of IFC class names to not copy.
        If any of the subelement is this class, it will not be copied and the
        original instance will be referenced.
    :param exclude_callback: A callback to determine whether or not to exclude
        an entity or not. Returns True to exclude and False to exclude.
    :param copied_entities: A dictionary of IDs as keys and entities as values
        to reuse when coming across the same entity twice. This can typically
        be left as None.
    :return: The newly copied element
    """
    if not ifc_file:
        ifc_file = element.file
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


def has_property(product: ifcopenshell.entity_instance, property_name: str) -> bool:
    """
    Check if a product has a property with a given name.

    :param product: The IFC product
    :param property_name: The property name
    :return: True if the product has the property, False otherwise

    Example:

    .. code:: python

        product = file.by_type("IfcWall")[0]
        has_property = ifcopenshell.util.element.has_property(product, "NetArea")
    """
    if not property_name:
        return True
    qtos = get_psets(product, qtos_only=True)
    return any(property_name in quantities.keys() for quantities in qtos.values())


def get_openings(element: ifcopenshell.entity_instance) -> Generator[ifcopenshell.entity_instance, None, None]:
    """Get element openings as IfcRelVoidsElements.

    Use `.RelatedOpeningElement` to get the opening element.

    :param element: IfcElement.
    :return: Generator of IfcRelVoidsElements.
    """
    for element_rel in getattr(element, "HasOpenings", ()):
        yield element_rel

    if aggregate := get_aggregate(element):
        yield from get_openings(aggregate)


def has_openings(element: ifcopenshell.entity_instance) -> bool:
    """Check if the element has openings.

    :param element: IfcElement.
    :return: True if element has openings.
    """
    return bool(next(get_openings(element), False))
