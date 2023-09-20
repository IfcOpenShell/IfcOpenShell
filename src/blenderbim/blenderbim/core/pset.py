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


def copy_property_to_selection(ifc, pset, is_pset=True, obj=None, pset_name=None, prop_name=None, prop_value=None):
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

def add_pset(ifc, pset, blender, obj_name, obj_type):
    pset_name = pset.get_pset_name(obj_name, obj_type)
    if obj_type == "Object":
        elements = [ifc.get_entity(obj) for obj in blender.get_selected_objects()]
    else:
        elements = [ifc.get().by_id(blender.get_obj_ifc_definition_id(obj_name, obj_type))]
    for element in elements:
        if not element:
            continue
        if not pset.is_pset_applicable(element, pset_name):
            continue
        ifc_pset = pset.get_element_pset(element, pset_name)
        if not ifc_pset:
            ifc.run("pset.add_pset", product=element, name=pset_name)
    pset.enable_pset_editing(pset_id=0, pset_name=pset_name, pset_type="PSET",obj=obj_name, obj_type=obj_type)