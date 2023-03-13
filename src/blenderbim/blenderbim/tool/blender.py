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
import ifcopenshell.api
import blenderbim.tool as tool


class Blender:
    @classmethod
    def set_active_object(cls, obj):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    @classmethod
    def get_name(cls, ifc_class, name):
        if not bpy.data.objects.get(f"{ifc_class}/{name}"):
            return name
        i = 2
        while bpy.data.objects.get(f"{ifc_class}/{name} {i}"):
            i += 1
        return f"{name} {i}"

    @classmethod
    def get_selected_objects(cls):
        if bpy.context.selected_objects:
            return set(bpy.context.selected_objects + [bpy.context.active_object])
        return set([bpy.context.active_object])

    @classmethod
    def create_ifc_object(cls, ifc_class: str, name: str = None, data=None) -> bpy.types.Object:
        name = name or "My " + ifc_class
        name = cls.get_name(ifc_class, name)
        obj = bpy.data.objects.new(name, data)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=ifc_class)
        return obj

    @classmethod
    def get_obj_ifc_definition_id(cls, obj=None, obj_type=None):
        if obj_type == "Object":
            return bpy.data.objects.get(obj).BIMObjectProperties.ifc_definition_id
        elif obj_type == "Material":
            return bpy.data.materials.get(obj).BIMObjectProperties.ifc_definition_id
        elif obj_type == "MaterialSet":
            return ifcopenshell.util.element.get_material(
                tool.Ifc.get_entity(bpy.data.objects.get(obj)), should_skip_usage=True
            ).id()
        elif obj_type == "MaterialSetItem":
            return bpy.data.objects.get(obj).BIMObjectMaterialProperties.active_material_set_item_id
        elif obj_type == "Task":
            return bpy.context.scene.BIMTaskTreeProperties.tasks[
                bpy.context.scene.BIMWorkScheduleProperties.active_task_index
            ].ifc_definition_id
        elif obj_type == "Cost":
            return bpy.context.scene.BIMCostProperties.cost_items[
                bpy.context.scene.BIMCostProperties.active_cost_item_index
            ].ifc_definition_id
        elif obj_type == "Resource":
            return bpy.context.scene.BIMResourceTreeProperties.resources[
                bpy.context.scene.BIMResourceProperties.active_resource_index
            ].ifc_definition_id
        elif obj_type == "Profile":
            return bpy.context.scene.BIMProfileProperties.profiles[
                bpy.context.scene.BIMProfileProperties.active_profile_index
            ].ifc_definition_id
        elif obj_type == "WorkSchedule":
            return bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id

    @classmethod
    def is_ifc_object(cls, obj):
        return bool(obj.BIMObjectProperties.ifc_definition_id)

    @classmethod
    def is_ifc_class_active(cls, ifc_class):
        if bpy.context.active_object:
            if cls.is_ifc_object(bpy.context.active_object):
                return tool.Ifc.get_entity(bpy.context.active_object).is_a(ifc_class)
            return False
        return False

    @classmethod
    def apply_bmesh(cls, mesh, bm):
        import bmesh

        if bpy.context.object and bpy.context.object.mode == "EDIT":
            # better to be safe because otherwise mesh won't be updated
            # and you won't get any errors
            if not bm.is_wrapped or hash(bmesh.from_edit_mesh(mesh)) != hash(bm):
                raise Exception(
                    f"{bm} is not edit mesh for {mesh}. "
                    "For applying bmesh in edit mode bmesh should be acquired with `bmesh.from_edit_mesh(me)`."
                )
            bmesh.update_edit_mesh(mesh)
            bpy.context.object.update_from_editmode()
        else:
            bm.to_mesh(mesh)
            # only freeing bmesh if object is in OBJECT mode
            # because if it's in EDIT mode
            # freeing mesh will result in dead bmeshes from `bmesh.from_edit_mesh(mesh)`
            # until you restart EDIT mode
            # which may result in errors when some other scripts will try to get bmesh
            bm.free()
        
        mesh.update()

    @classmethod
    def get_bmesh_for_mesh(cls, mesh, clean=False):
        import bmesh

        if bpy.context.object.mode == "EDIT":
            bm = bmesh.from_edit_mesh(mesh)
            if clean:
                bm.clear()
        else:
            bm = bmesh.new()
            if not clean:
                bm.from_mesh(mesh)
        return bm
    
    @classmethod
    def get_viewport_context(cls):
        """Get viewport area context for context overriding.

        Useful for calling operators outside viewport context.

        It's a bit naive since it's just taking the first available `VIEW_3D` area
        when in real life you can have a couple of those but should work for the most cases.
        """
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        context_override = {"area": area}
        return context_override