# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


def unlink_material(ifc, obj=None):
    ifc.unlink(obj=obj)


def add_material(ifc, material, style, obj=None, name=None):
    if not obj:
        obj = material.add_default_material_object(name)
    ifc_material = ifc.run("material.add_material", name=material.get_name(obj))
    ifc.link(ifc_material, obj)
    ifc_style = style.get_style(obj)
    if ifc_style:
        context = style.get_context(obj)
        if context:
            ifc.run("style.assign_material_style", material=ifc_material, style=ifc_style, context=context)
    if material.is_editing_materials():
        material.import_material_definitions(material.get_active_material_type())
    return ifc_material


def add_material_set(ifc, material, set_type=None):
    ifc_material = ifc.run("material.add_material_set", name="Unnamed", set_type=set_type)
    if material.is_editing_materials():
        material.import_material_definitions(material.get_active_material_type())
    return ifc_material


def remove_material(ifc, material_tool, style, material=None) -> bool:
    """returns True after deleting False,\n
    returns False if material used in material sets and cannot be removed"""
    if material_tool.is_material_used_in_sets(material):
        return False
    obj = ifc.get_object(material)
    ifc.unlink(element=material)
    ifc.run("material.remove_material", material=material)
    if obj and not style.get_style(obj):
        material_tool.delete_object(obj)
    if material_tool.is_editing_materials():
        material_tool.import_material_definitions(material_tool.get_active_material_type())
    return True


def remove_material_set(ifc, material_tool, material=None):
    ifc.run("material.remove_material_set", material=material)
    if material_tool.is_editing_materials():
        material_tool.import_material_definitions(material_tool.get_active_material_type())


def load_materials(material, material_type=None):
    material.import_material_definitions(material_type)
    material.enable_editing_materials()


def disable_editing_materials(material):
    material.disable_editing_materials()


def select_by_material(material_tool, spatial, material=None):
    spatial.select_products(material_tool.get_elements_by_material(material))


def enable_editing_material(material_tool, material):
    material_tool.load_material_attributes(material)
    material_tool.enable_editing_material(material)


def edit_material(ifc, material_tool, material):
    attributes = material_tool.get_material_attributes()
    ifc.run("material.edit_material", material=material, attributes=attributes)
    material_tool.disable_editing_material()
    material_type = material_tool.get_active_material_type()
    material_tool.import_material_definitions(material_type)
    material_tool.enable_editing_materials()


def disable_editing_material(material_tool):
    material_tool.disable_editing_material()


def assign_material(ifc, material_tool, material_type, objects):
    material_type = material_type or material_tool.get_active_object_material()
    material = material_tool.get_active_material()
    for obj in objects:
        element = ifc.get_entity(obj)
        if not element:
            continue
        ifc.run("material.assign_material", products=[element], type=material_type, material=material)
        assigned_material = material_tool.get_material(element)
        if material_tool.is_a_material_set(assigned_material):
            material_tool.add_material_to_set(material_set=assigned_material, material=material)


def unassign_material(ifc, material_tool, objects):
    for obj in objects:
        element = ifc.get_entity(obj)
        if element:
            material = material_tool.get_material(element, should_inherit=False)
            inherited_material = material_tool.get_material(element, should_inherit=True)
            if material and "Usage" in material.is_a():
                element_type = material_tool.get_type(element)
                ifc.run("material.unassign_material", product=element_type)
            elif not material and inherited_material:
                element_type = material_tool.get_type(element)
                ifc.run("material.unassign_material", product=element_type)
            elif material:
                ifc.run("material.unassign_material", product=element)


def patch_non_parametric_mep_segment(ifc, material_tool, profile_tool, obj):
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
