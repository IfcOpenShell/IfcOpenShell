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
from typing import TYPE_CHECKING, Optional, Union, Any

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def copy_property_to_selection(
    ifc: tool.Ifc,
    pset: tool.Pset,
    obj: bpy.types.Object,
    pset_name: str,
    prop_name: str,
    prop_value: Any,
    is_pset: bool = True,
) -> None:
    element = ifc.get_entity(obj)
    if not element:
        return
    ifc_pset = pset.get_element_pset(element, pset_name)
    if not ifc_pset:
        ifc_pset = ifc.run("pset.add_pset" if is_pset else "pset.add_qto", product=element, name=pset_name)
    if is_pset:
        ifc.run("pset.edit_pset", pset=ifc_pset, properties={prop_name: prop_value})
    else:
        ifc.run("pset.edit_qto", qto=ifc_pset, properties={prop_name: prop_value})


def add_pset(
    ifc: tool.Ifc, pset: tool.Pset, blender: tool.Blender, obj_name: str, obj_type: tool.Ifc.OBJECT_TYPE
) -> None:
    pset_name = pset.get_pset_name(obj_name, obj_type, pset_type="PSET")
    if obj_type == "Object":
        elements = [ifc.get_entity(obj) for obj in blender.get_selected_objects()]
    else:
        elements = [ifc.get().by_id(blender.get_obj_ifc_definition_id(obj_name, obj_type))]
    for element in elements:
        if not element:
            continue
        if pset_name and not pset.is_pset_applicable(element, pset_name):
            continue
        pset.enable_pset_editing(pset_id=0, pset_name=pset_name, pset_type="PSET", obj=obj_name, obj_type=obj_type)


def enable_pset_editing(
    pset_tool: tool.Pset,
    pset: Union[ifcopenshell.entity_instance, None],
    pset_name: str,
    pset_type: tool.Pset.PSET_TYPE,
    obj_name: str,
    obj_type: tool.Ifc.OBJECT_TYPE,
) -> None:
    props = pset_tool.get_pset_props(obj_name, obj_type)
    pset_tool.clear_blender_pset_properties(props)

    pset_template = pset_tool.get_pset_template(pset_name)

    if pset_template:
        pset_tool.import_pset_from_template(pset_template, pset, props)
        has_template = True
    else:
        has_template = False

    if pset:
        pset_tool.import_pset_from_existing(pset, props)
        pset_tool.set_active_pset(props, pset, has_template)
    else:
        pset_tool.enable_proposed_pset(props, pset_name, pset_type, has_template)


def add_proposed_prop(
    pset: tool.Pset, obj_name: str, obj_type: tool.Ifc.OBJECT_TYPE, name: str, value: Any
) -> Union[None, str]:
    props = pset.get_pset_props(obj_name, obj_type)
    res = pset.add_proposed_property(name, pset.cast_string_to_primitive(value), props)
    pset.reset_proposed_property_fields(props)
    return res


def unshare_pset(
    ifc: tool.Ifc, pset_tool: tool.Pset, obj_type: tool.Ifc.OBJECT_TYPE, obj_name: str, pset_id: int
) -> None:
    elements: list[ifcopenshell.entity_instance]
    pset = ifc.get_entity_by_id(pset_id)
    assert pset
    elements = pset_tool.get_selected_pset_elements(obj_name, obj_type, pset)
    ifc.run("pset.unshare_pset", products=elements, pset=pset)
