# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import bpy
import json
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.unit
import bonsai.tool as tool
from mathutils import Vector, Matrix


class AddArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_array"
    bl_label = "Add Array"
    bl_description = "Add Bonsai parametric array to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)

        array = {
            "children": [],
            "count": 1,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "use_local_space": True,
            "sync_children": False,
            "method": "OFFSET",
        }

        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")

        if pset:
            data = json.loads(pset["Data"])
            data.append(array)
            pset = tool.Ifc.get().by_id(pset["id"])
        else:
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Array")
            data = [array]

        ifcopenshell.api.run(
            "pset.edit_pset",
            tool.Ifc.get(),
            pset=pset,
            properties={"Parent": element.GlobalId, "Data": tool.Ifc.get().createIfcText(json.dumps(data))},
        )
        return {"FINISHED"}


class DisableEditingArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_array"
    bl_label = "Disable Editing Array"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        context.active_object.BIMArrayProperties.is_editing = -1
        return {"FINISHED"}


class EnableEditingArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_array"
    bl_label = "Enable Editing Array"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.IntProperty()

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMArrayProperties

        relating_obj = props.relating_array_object

        if relating_obj:
            element = tool.Ifc.get_entity(relating_obj)
            parent_globalid = ifcopenshell.util.element.get_pset(element, "BBIM_Array", "Parent")
            parent_element = tool.Ifc.get().by_guid(parent_globalid)
            data = json.loads(ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array", "Data"))[self.item]
        else:
            data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Array", "Data"))[self.item]
        props.count = data["count"]
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        props.x = data["x"] * si_conversion
        props.y = data["y"] * si_conversion
        props.z = data["z"] * si_conversion
        props.use_local_space = data.get("use_local_space", False)
        props.sync_children = data.get("sync_children", False)
        props.method = data.get("method", "OFFSET")

        props.is_editing = self.item

        return {"FINISHED"}


class EditArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_array"
    bl_label = "Edit Array"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.IntProperty()

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMArrayProperties
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        data = json.loads(pset["Data"])
        data[self.item] = {
            "children": data[self.item]["children"],
            "count": props.count,
            "x": props.x / si_conversion,
            "y": props.y / si_conversion,
            "z": props.z / si_conversion,
            "use_local_space": props.use_local_space,
            "sync_children": props.sync_children,
            "method": props.method,
        }

        props.is_editing = -1

        try:
            parent = tool.Ifc.get_object(tool.Ifc.get().by_guid(pset["Parent"]))
        except:
            return {"FINISHED"}

        tool.Model.regenerate_array(parent, data)

        pset = tool.Ifc.get().by_id(pset["id"])
        data = tool.Ifc.get().createIfcText(json.dumps(data))
        ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": data})

        tool.Blender.Modifier.Array.set_children_lock_state(element, self.item, True)
        tool.Blender.Modifier.Array.constrain_children_to_parent(element)

        # clears the relating_array_object so it doesn't show again next time
        props.relating_array_object = None

        return {"FINISHED"}


class ApplyArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.apply_array"
    bl_label = "Apply Array"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Apply the array and keep children as separate entities. Only available for the last array"

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        data = json.loads(pset["Data"])
        bpy.ops.bim.remove_array(item=len(data) - 1, keep_objs=True)
        return {"FINISHED"}


class RemoveArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_array"
    bl_label = "Remove Array"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.IntProperty()
    keep_objs: bpy.props.BoolProperty(name="Keep Objects", default=False)

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMArrayProperties

        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        data = json.loads(pset["Data"])

        if (self.keep_objs) & (self.item < (len(data) - 1)):
            self.report(
                {"INFO"}, "Keeping the objects is only allowed when you are removing the last Array of the object"
            )
            return {"FINISHED"}

        props.is_editing = -1

        try:
            parent = tool.Ifc.get_object(tool.Ifc.get().by_guid(pset["Parent"]))
        except:
            return {"FINISHED"}

        if self.keep_objs:
            tool.Blender.Modifier.Array.bake_children_transform(element, self.item)
            tool.Blender.Modifier.Array.set_children_lock_state(element, self.item, False)

        if not self.keep_objs:
            data[self.item]["count"] = 1
        tool.Model.regenerate_array(parent, data, array_layers_to_apply=[self.item] if self.keep_objs else [])

        pset = tool.Ifc.get().by_id(pset["id"])
        if len(data) == 1:
            ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)
        else:
            del data[self.item]
            data = tool.Ifc.get().createIfcText(json.dumps(data))
            ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": data})
            tool.Blender.Modifier.Array.constrain_children_to_parent(element)

        return {"FINISHED"}


class SelectArrayParent(bpy.types.Operator):
    bl_idname = "bim.select_array_parent"
    bl_label = "Select Array Parent"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            cls.poll_message_set("No active object selected")
            return False
        return True

    def execute(self, context):
        object = context.active_object
        element = tool.Ifc.get_entity(object)
        array_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not array_pset:
            self.report({"ERROR"}, f"Object is not part of an array.")
            return {"CANCELLED"}

        try:
            parent_element = tool.Ifc.get().by_guid(array_pset["Parent"])
        except:
            self.report({"ERROR"}, f"Couldn't find array parent by guid '{array_pset['Parent']}'")
            return {"CANCELLED"}

        obj = tool.Ifc.get_object(parent_element)
        if obj:
            tool.Blender.select_and_activate_single_object(context, active_object=obj)
        return {"FINISHED"}


class SelectAllArrayObjects(bpy.types.Operator):
    bl_idname = "bim.select_all_array_objects"
    bl_label = "Select All Array Objects"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            cls.poll_message_set("No active object selected")
            return False
        return True

    def execute(self, context):
        objects = context.selected_objects
        for object in objects:
            element = tool.Ifc.get_entity(object)
            if not element:
                self.report({"ERROR"}, f"Non IFC objects, were deselected.")
                object.select_set(False)

            if element:
                array_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
                if not array_pset:
                    self.report({"ERROR"}, f"Objects not part of an array, were deselected.")
                    object.select_set(False)

                if array_pset:
                    try:
                        parent_element = tool.Ifc.get().by_guid(array_pset["Parent"])
                    except RuntimeError:
                        self.report({"ERROR"}, f"Objects that don't have an array parent, were deselected.")
                        object.select_set(False)

                    array_objects = tool.Blender.Modifier.Array.get_all_objects(parent_element)
                    tool.Blender.set_objects_selection(
                        context,
                        active_object=array_objects[0],
                        selected_objects=array_objects,
                        clear_previous_selection=False,
                    )
        return {"FINISHED"}


class Input3DCursorXArray(bpy.types.Operator):
    bl_idname = "bim.input_cursor_x_array"
    bl_label = "Get 3d Cursor X Input for Array"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMArrayProperties
        cursor = context.scene.cursor
        if props.use_local_space:
            props.x = (Matrix.inverted(obj.matrix_world) @ cursor.matrix.translation).x
        else:
            props.x = cursor.location.x - obj.location.x
        return {"FINISHED"}


class Input3DCursorYArray(bpy.types.Operator):
    bl_idname = "bim.input_cursor_y_array"
    bl_label = "Get 3d Cursor Y Input for Array"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMArrayProperties
        cursor = context.scene.cursor
        if props.use_local_space:
            props.y = (Matrix.inverted(obj.matrix_world) @ cursor.matrix.translation).y
        else:
            props.y = cursor.location.y - obj.location.y
        return {"FINISHED"}


class Input3DCursorZArray(bpy.types.Operator):
    bl_idname = "bim.input_cursor_z_array"
    bl_label = "Get 3d Cursor Z Input for Array"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        props = obj.BIMArrayProperties
        cursor = context.scene.cursor
        if props.use_local_space:
            props.z = (Matrix.inverted(obj.matrix_world) @ cursor.matrix.translation).z
        else:
            props.z = cursor.location.z - obj.location.z
        return {"FINISHED"}
