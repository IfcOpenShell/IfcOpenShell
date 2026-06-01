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

import json

import bpy
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.unit
from mathutils import Matrix

import bonsai.tool as tool


class AddArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_array"
    bl_label = "Add Array"
    bl_description = "Add Bonsai parametric array to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        assert (obj := context.active_object)
        assert (element := tool.Ifc.get_entity(obj))
        ifc_file = tool.Ifc.get()

        allowed_types = (
            "IfcElement",
            "IfcAnnotation",
            "IfcOpeningElement",
            "IfcSpatialElement",
        )

        if not any(element.is_a(c) for c in allowed_types):
            self.report(
                {"ERROR"},
                f"Adding array to element of type '{element.is_a()}' is not supported. Supported types: {','.join(allowed_types)}.",
            )
            return {"CANCELLED"}

        array = {
            "children": [],
            "count": 1,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "use_local_space": True,
            "method": "OFFSET",
        }

        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")

        if pset:
            data = json.loads(pset["Data"])
            data.append(array)
            pset = tool.Ifc.get().by_id(pset["id"])
        else:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="BBIM_Array")
            data = [array]

        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=pset,
            properties={"Parent": element.GlobalId, "Data": ifc_file.create_entity("IfcText", json.dumps(data))},
        )


class DisableEditingArray(bpy.types.Operator):
    bl_idname = "bim.disable_editing_array"
    bl_label = "Disable Editing Array"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        assert obj
        tool.Model.get_array_props(obj).is_editing = -1
        return {"FINISHED"}


class EnableEditingArray(bpy.types.Operator):
    bl_idname = "bim.enable_editing_array"
    bl_label = "Enable Editing Array"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_array_props(obj)

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
        props = tool.Model.get_array_props(obj)
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
            "method": props.method,
        }

        props.is_editing = -1

        try:
            parent_element = tool.Ifc.get().by_guid(pset["Parent"])
            parent = tool.Ifc.get_object(parent_element)
        except:
            return {"FINISHED"}

        tool.Blender.Modifier.Array.remove_constraints(parent_element)
        tool.Model.regenerate_array(parent, data)
        tool.Blender.Modifier.Array.set_children_lock_state(element, self.item, True)
        tool.Blender.Modifier.Array.constrain_children_to_parent(element)

        # clears the relating_array_object so it doesn't show again next time
        props.relating_array_object = None


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


class RegenerateArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.regenerate_array"
    bl_label = "Regenerate Array"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        try:
            parent_element = tool.Ifc.get().by_guid(pset["Parent"])
            parent = tool.Ifc.get_object(parent_element)
        except:
            return {"FINISHED"}
        pset = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array")
        arrays = json.loads(pset["Data"])
        pset = tool.Ifc.get().by_id(pset["id"])
        for array in arrays:
            for child in set(array["children"]):
                if child_obj := tool.Ifc.get_object(tool.Ifc.get().by_guid(child)):
                    tool.Geometry.delete_ifc_object(child_obj)
            array["children"].clear()
        print("cleared array", arrays)
        tool.Model.regenerate_array(obj, arrays)
        tool.Blender.Modifier.Array.constrain_children_to_parent(element)


class RemoveArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_array"
    bl_label = "Remove Array"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.IntProperty()
    keep_objs: bpy.props.BoolProperty(name="Keep Objects", default=False)

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_array_props(obj)

        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        data = json.loads(pset["Data"])

        if (self.keep_objs) & (self.item < (len(data) - 1)):
            self.report(
                {"INFO"}, "Keeping the objects is only allowed when you are removing the last Array of the object"
            )
            return {"FINISHED"}

        props.is_editing = -1

        try:
            parent_element = tool.Ifc.get().by_guid(pset["Parent"])
            parent = tool.Ifc.get_object(parent_element)
        except:
            return {"FINISHED"}

        if self.keep_objs:
            tool.Blender.Modifier.Array.bake_children_transform(element, self.item)
            tool.Blender.Modifier.Array.set_children_lock_state(element, self.item, False)

        if not self.keep_objs:
            data[self.item]["count"] = 1
        tool.Blender.Modifier.Array.remove_constraints(parent_element)
        tool.Model.regenerate_array(parent, data, array_layers_to_apply=[self.item] if self.keep_objs else [])

        pset = tool.Pset.get_element_pset(element, "BBIM_Array")
        if len(data) == 1:
            ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)
        else:
            del data[self.item]
            data = tool.Ifc.get().createIfcText(json.dumps(data))
            ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data})
            tool.Blender.Modifier.Array.constrain_children_to_parent(element)


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
        assert obj
        props = tool.Model.get_array_props(obj)
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
        assert obj
        props = tool.Model.get_array_props(obj)
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
        assert obj
        props = tool.Model.get_array_props(obj)
        cursor = context.scene.cursor
        if props.use_local_space:
            props.z = (Matrix.inverted(obj.matrix_world) @ cursor.matrix.translation).z
        else:
            props.z = cursor.location.z - obj.location.z
        return {"FINISHED"}


class EnableEditingParametric(bpy.types.Operator):
    """Pen-icon dispatcher: fires the gizmo group's per-feature edit operator.

    Bound to every parametric gizmo group's pen icon. The gizmo group's own
    ``enable_editing_operator`` (``bim.enable_editing_door``, ``…_wall``, …)
    is passed as ``feature_enable_op`` at setup time and invoked here. The
    indirection lets one gizmo class serve all features without per-feature
    subclasses."""

    bl_idname = "bim.enable_editing_parametric"
    bl_label = "Enable Editing"
    bl_description = "Edit this object's parameters"
    bl_options = {"REGISTER", "UNDO"}

    feature_enable_op: bpy.props.StringProperty(
        default="",
        description="Operator bl_idname to invoke (e.g., 'bim.enable_editing_door').",
    )

    def execute(self, context):
        # Malformed ``feature_enable_op`` (missing dot) would otherwise crash
        # the unpack with ValueError; treat the same as the empty-string case.
        parts = self.feature_enable_op.split(".", 1)
        if len(parts) != 2:
            return {"CANCELLED"}
        domain, opname = parts
        return getattr(getattr(bpy.ops, domain), opname)("INVOKE_DEFAULT")


class AddArrayFromFeatureEdit(bpy.types.Operator, tool.Ifc.Operator):
    """Commit any in-progress feature edit and add an array with
    gizmo-friendly defaults (count=2, offset = bbox extent along the axis).

    Modifier-aware: plain click → X, Shift → Y, Ctrl → Z. Callers can pass
    ``axis="X"`` via EXEC_DEFAULT to bypass the modifier read.

    All three chained operators (feature finish + add_array + enable_editing)
    run inside one transaction for a single undo step."""

    bl_idname = "bim.add_array_from_feature_edit"
    bl_label = "Add Array"
    bl_description = (
        "Click: add an array along X.\n" "Shift+Click: add an array along Y.\n" "Ctrl+Click: add an array along Z"
    )
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.EnumProperty(
        name="Offset Axis",
        items=[
            ("X", "X", "Offset along the object's X axis (bbox X extent)"),
            ("Y", "Y", "Offset along the object's Y axis (bbox Y extent)"),
            ("Z", "Z", "Offset along the object's Z axis (bbox Z extent)"),
        ],
        default="X",
    )

    # Minimum offset to use when the object's bbox extent is tiny — prevents
    # the second instance from visually overlapping the parent on small
    # annotations / openings (0.3m ≈ a clearly-separated next-instance distance).
    MIN_DEFAULT_OFFSET = 0.3

    def invoke(self, context, event):
        # Modifier-aware axis pick: X by default, Shift → Y, Ctrl → Z.
        if event.shift:
            self.axis = "Y"
        elif event.ctrl:
            self.axis = "Z"
        else:
            self.axis = "X"
        return self.execute(context)

    def _execute(self, context):
        obj = context.active_object
        if obj is None:
            return {"CANCELLED"}
        # Commit any in-progress parametric edit lifecycle on this object first — the
        # user expects "Add Array" to also finalise whatever they were editing
        # so they don't lose their draft changes.
        editing = tool.Parametric.is_object_editing(obj, skip_name="array")
        if editing is not None:
            finish_op_name = editing.finish_op.removeprefix("bim.")
            getattr(bpy.ops.bim, finish_op_name)("INVOKE_DEFAULT")
        # Bounding-box derived offset along the chosen axis, converted from
        # Blender SI (meters) to IFC project units (which is what
        # ``BBIM_Array.Data`` stores; the regenerator multiplies by
        # unit_scale on the way out).
        axis_idx = "XYZ".index(self.axis)
        if obj.bound_box:
            bbox_extent_si = max(c[axis_idx] for c in obj.bound_box) - min(c[axis_idx] for c in obj.bound_box)
        else:
            bbox_extent_si = 1.0
        bbox_extent_si = max(bbox_extent_si, self.MIN_DEFAULT_OFFSET)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        offset_project = bbox_extent_si / si_conversion if si_conversion else bbox_extent_si
        add_kwargs = {"count": 2, "x": 0.0, "y": 0.0, "z": 0.0}
        add_kwargs[self.axis.lower()] = offset_project
        result = bpy.ops.bim.add_array(**add_kwargs)
        if result != {"FINISHED"}:
            return result
        # Restore selection to just the parent. ``regenerate_array`` calls
        # ``tool.Geometry.duplicate_ifc_objects`` which leaves the newly-created
        # child selected alongside the parent. The edit-lifecycle gizmos poll on a
        # single-selected parent, so with both selected the gizmos wouldn't
        # surface and "ARRAY → enter edit" would feel broken.
        tool.Blender.select_and_activate_single_object(context, active_object=obj)
        # Chain straight into array edit for the newly-added layer (always the
        # last entry in the pset's Data list, by AddArray's append semantics).
        # The user's expectation after clicking ARRAY is "I want to tweak this
        # array now" — entering edit mode immediately collapses the 2-click
        # discover-then-edit flow into one.
        element = tool.Ifc.get_entity(obj)
        if element is None:
            return {"FINISHED"}
        data_text = ifcopenshell.util.element.get_pset(element, "BBIM_Array", "Data")
        if not data_text:
            return {"FINISHED"}
        try:
            layers = json.loads(data_text)
        except (ValueError, TypeError):
            return {"FINISHED"}
        if not layers:
            return {"FINISHED"}
        bpy.ops.bim.enable_editing_array("INVOKE_DEFAULT", item=len(layers) - 1)
        return {"FINISHED"}
