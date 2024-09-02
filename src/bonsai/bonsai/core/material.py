# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_material(
    ifc: tool.Ifc,
    material: tool.Material,
    name: str,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    ifc_material = ifc.run("material.add_material", name=name, category=category, description=description)
    if material.is_editing_materials():
        material.import_material_definitions(material.get_active_material_type())
    return ifc_material


def add_material_set(ifc: tool.Ifc, material: tool.Material, set_type: str) -> ifcopenshell.entity_instance:
    ifc_material = ifc.run("material.add_material_set", name="Unnamed", set_type=set_type)
    material.ensure_new_material_set_is_valid(ifc_material)
    if material.is_editing_materials():
        material.import_material_definitions(material.get_active_material_type())
    return ifc_material


def remove_material(ifc: tool.Ifc, material_tool: tool.Material, material: ifcopenshell.entity_instance) -> bool:
    """Remove an IFC material.

    Return True if deletion succeeded,\n
    return False if material is used in material sets and cannot be removed.
    """
    if material_tool.is_material_used_in_sets(material):
        return False
    ifc.run("material.remove_material", material=material)
    if material_tool.is_editing_materials():
        material_tool.import_material_definitions(material_tool.get_active_material_type())
    return True


def remove_material_set(ifc: tool.Ifc, material_tool: tool.Material, material: ifcopenshell.entity_instance) -> None:
    ifc.run("material.remove_material_set", material=material)
    if material_tool.is_editing_materials():
        material_tool.import_material_definitions(material_tool.get_active_material_type())


def load_materials(material: tool.Material, material_type: str) -> None:
    material.import_material_definitions(material_type)
    material.enable_editing_materials()


def disable_editing_materials(material: tool.Material) -> None:
    material.disable_editing_materials()


def select_by_material(
    material_tool: tool.Material, spatial: tool.Spatial, material: ifcopenshell.entity_instance
) -> None:
    spatial.select_products(material_tool.get_elements_by_material(material))


def enable_editing_material(material_tool: tool.Material, material: ifcopenshell.entity_instance) -> None:
    material_tool.load_material_attributes(material)
    material_tool.enable_editing_material(material)


def edit_material(ifc: tool.Ifc, material_tool: tool.Material, material: ifcopenshell.entity_instance) -> None:
    attributes = material_tool.get_material_attributes()
    ifc.run("material.edit_material", material=material, attributes=attributes)
    material_tool.disable_editing_material()
    material_type = material_tool.get_active_material_type()
    material_tool.import_material_definitions(material_type)
    material_tool.enable_editing_materials()


def disable_editing_material(material_tool: tool.Material) -> None:
    material_tool.disable_editing_material()


def assign_material(
    ifc: tool.Ifc,
    material_tool: tool.Material,
    material_type: Union[str, None],
    objects: list[bpy.types.Object],
    material: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    """Assign material to the provided objects.

    If `material_type` or `material` are not provided, the active ones from
        Object Materials UI is used.
    """
    material_type = material_type or material_tool.get_object_ui_material_type()
    material = material or material_tool.get_object_ui_active_material()
    for obj in objects:
        element = ifc.get_entity(obj)
        if not element:
            continue

        ifc.run("material.assign_material", products=[element], type=material_type, material=material)
        assigned_material = material_tool.get_material(element)
        assert assigned_material  # Type checker.

        if material_tool.is_a_material_set(material):
            # Ensure set is a valid IFC.
            default_material = material_tool.get_default_material()
            material_tool.add_material_to_set(material_set=material, material=default_material)
        elif material_tool.is_a_material_set(assigned_material):
            material_tool.add_material_to_set(material_set=assigned_material, material=material)
        material_tool.ensure_material_assigned(elements=[element], material_type=material_type, material=material)


def unassign_material(ifc: tool.Ifc, material_tool: tool.Material, objects: list[bpy.types.Object]) -> None:
    for obj in objects:
        element = ifc.get_entity(obj)
        if not element:
            continue
        material = material_tool.get_material(element, should_inherit=False)
        inherited_material = material_tool.get_material(element, should_inherit=True)
        if material:
            if "Usage" in material.is_a():
                element_type = material_tool.get_type(element)
                assert element_type  # Type checker.
                ifc.run("material.unassign_material", products=[element_type])
                material_tool.ensure_material_unassigned(elements=[element_type])
            else:
                ifc.run("material.unassign_material", products=[element])
                material_tool.ensure_material_unassigned(elements=[element])
        elif inherited_material:
            element_type = material_tool.get_type(element)
            assert element_type  # Type checker.
            ifc.run("material.unassign_material", products=[element_type])
            material_tool.ensure_material_unassigned(elements=[element_type])
        else:
            # Has no material and has no inherited material, nothing to unassign.
            pass


def patch_non_parametric_mep_segment(
    ifc: tool.Ifc, material_tool: tool.Material, profile_tool: tool.Profile, obj: bpy.types.Object
) -> None:
    element = ifc.get_entity(obj)
    if not element:
        return
    if not material_tool.is_a_flow_segment(element):
        return
    has_material_profile = material_tool.has_material_profile(element)
    if has_material_profile:
        return
    representation_profile = profile_tool.get_profile(element)
    if not representation_profile:
        return
    material_profile = material_tool.replace_material_with_material_profile(element=element)
    ifc.run("material.assign_profile", material_profile=material_profile, profile=representation_profile)
