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

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.schema


class Pset(blenderbim.core.tool.Pset):
    @classmethod
    def get_element_pset(cls, element, pset_name):
        pset = ifcopenshell.util.element.get_pset(element, pset_name)
        if pset:
            return tool.Ifc.get().by_id(pset["id"])

    @classmethod
    def get_pset_props(cls, obj, obj_type):
        if obj_type == "Object":
            return bpy.data.objects.get(obj).PsetProperties
        elif obj_type == "Material":
            return bpy.data.materials.get(obj).PsetProperties
        elif obj_type == "MaterialSet":
            return bpy.data.objects.get(obj).MaterialSetPsetProperties
        elif obj_type == "MaterialSetItem":
            return bpy.data.objects.get(obj).MaterialSetItemPsetProperties
        elif obj_type == "Task":
            return bpy.context.scene.TaskPsetProperties
        elif obj_type == "Resource":
            return bpy.context.scene.ResourcePsetProperties
        elif obj_type == "Profile":
            return bpy.context.scene.ProfilePsetProperties
        elif obj_type == "WorkSchedule":
            return bpy.context.scene.WorkSchedulePsetProperties

    @classmethod
    def get_pset_name(cls, obj, obj_type):
        pset = cls.get_pset_props(obj, obj_type)
        return pset.pset_name

    @classmethod
    def is_pset_applicable(cls, element, pset_name):
        return bool(pset_name in blenderbim.bim.schema.ifc.psetqto.get_applicable_names(element.is_a(), pset_only=True))

    @classmethod
    def is_pset_empty(cls, pset):
        pset_dict = ifcopenshell.util.element.get_property_definition(pset)
        del pset_dict["id"]
        for value in pset_dict.values():
            if value is not None:
                return False
        return True
