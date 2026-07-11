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
#
# This file was modified with the assistance of an AI coding tool.

import json
from typing import ClassVar

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.unit
from mathutils import Matrix, Vector

import bonsai.bim.module.drawing.gizmos as gizmo
import bonsai.tool as tool
from bonsai.bim.decorator_cache import TokenCache
from bonsai.bim.module.drawing.gizmos import (
    COLOR_GREEN,
    COLOR_RED,
    DimensionGizmoConfig,
    IconSlot,
)
from bonsai.bim.module.model.decorator import (
    _BBOX_EDGES,
    _BBOX_HIGHLIGHT_LINE_ALPHA,
    _BBOX_HIGHLIGHT_LINE_WIDTH,
    bbox_world_edges,
    draw_polyline_segments,
)
from bonsai.bim.parametric_lifecycle import (
    IntegerInputDialogMixin,
    ParametricEditMixinBase,
)


def _wipe_array_children(layers: list) -> None:
    """Delete every existing array child and clear ``children`` GUID lists.

    Rebuilding mints fresh GlobalIds, so external references (BCF, IDS, etc.)
    to the old GUIDs go stale. The bbox heuristic skips the wipe when the
    parent's geometry is unchanged."""
    for layer in layers:
        for child_guid in layer.get("children", []):
            try:
                child_element = tool.Ifc.get().by_guid(child_guid)
            except RuntimeError:
                continue
            child_obj = tool.Ifc.get_object(child_element)
            if child_obj is not None:
                tool.Geometry.delete_ifc_object(child_obj)
        layer["children"] = []


_BBOX_EQUALITY_EPS = 1e-5


def _resolve_array_edit_props(context: bpy.types.Context):
    """Resolve the active object's array props during an active edit
    lifecycle. Returns ``None`` when there's no active object or the user
    isn't mid-edit. Used as the execute / poll prologue for operators
    bound to the array edit gizmos so they no-op cleanly outside the
    edit lifecycle without bypassing the commit lifecycle."""
    obj = context.active_object
    if obj is None:
        return None
    props = tool.Model.get_array_props(obj)
    if not props.is_editing:
        return None
    return props


def _array_children_need_rebuild(parent_obj, layers: list) -> bool:
    """Cheap drift detector: True when the parent's local bbox dimensions
    differ from the first resolvable child's, indicating a parent geometry
    edit since the last array regen. Misses edits that preserve bbox
    dimensions (e.g. shape changes within the same envelope); those need
    a manual "Regenerate Array" via the UI button.

    Runs at array-edit finish as a safety net: when True, callers wipe and
    rebuild children so the array picks up the drift; when False, in-place
    transform updates suffice."""
    if not parent_obj.bound_box:
        return True
    parent_dims = tool.Blender.get_object_bounding_box(parent_obj)["dimensions"]
    for layer in layers:
        for child_guid in layer.get("children", []):
            try:
                child_element = tool.Ifc.get().by_guid(child_guid)
            except RuntimeError:
                continue
            child_obj = tool.Ifc.get_object(child_element)
            if child_obj is None or not child_obj.bound_box:
                continue
            child_dims = tool.Blender.get_object_bounding_box(child_obj)["dimensions"]
            return any(abs(a - b) > _BBOX_EQUALITY_EPS for a, b in zip(parent_dims, child_dims))
    return False


class AddArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_array"
    bl_label = "Add Array"
    bl_description = "Add an array of the active object"
    bl_options = {"REGISTER", "UNDO"}

    # Optional parameters — defaults preserve the existing UX (count=1, no offset)
    # for the panel + script callers. The gizmo-driven path (see
    # ``AddArrayFromFeatureEdit``) passes bbox-derived values so the new array
    # has a visible second instance and interactable offset gizmos out of the box.
    count: bpy.props.IntProperty(name="Count", default=1, min=1)
    x: bpy.props.FloatProperty(name="X Offset", default=0.0)
    y: bpy.props.FloatProperty(name="Y Offset", default=0.0)
    z: bpy.props.FloatProperty(name="Z Offset", default=0.0)

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
            "count": self.count,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "use_local_space": True,
            "method": "OFFSET",
            "per_child_opening": True,
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

        # Always regenerate so callers passing count >= 2 see the second+ instance
        # appear immediately. No-op for count=1 layers.
        tool.Model.regenerate_array(obj, data)
        tool.Array.constrain_children_to_parent(element)


class _ArrayEditMixin(ParametricEditMixinBase):
    """Array edit lifecycle scoped to one layer at a time.

    ``is_editing`` is paired with ``editing_item_index`` so Finish/Cancel
    know which layer to commit/discard. Gizmo drag mutates props in place;
    IFC writes happen only at Finish."""

    pset_name = "BBIM_Array"

    @classmethod
    def _is_element_type(cls, element):
        return tool.Parametric.is_array(element)

    @classmethod
    def _get_props(cls, obj: bpy.types.Object):
        return tool.Model.get_array_props(obj)

    @classmethod
    def _iter_targets(cls, context: bpy.types.Context) -> list[bpy.types.Object]:
        obj = context.active_object
        return [obj] if obj else []

    @classmethod
    def _resolve(cls, obj: bpy.types.Object):
        element = tool.Ifc.get_entity(obj)
        if not element or not cls._is_element_type(element):
            return None
        return element, cls._get_props(obj)

    @classmethod
    def _read_layers(cls, element) -> list:
        return json.loads(ifcopenshell.util.element.get_pset(element, cls.pset_name, "Data") or "[]")

    @classmethod
    def _hydrate_props_from_layer(cls, props, layer: dict, si_conversion: float) -> None:
        props.count = layer["count"]
        props.x = layer["x"] * si_conversion
        props.y = layer["y"] * si_conversion
        props.z = layer["z"] * si_conversion
        props.use_local_space = layer.get("use_local_space", True)
        props.method = layer.get("method", "OFFSET")
        props.per_child_opening = layer.get("per_child_opening", layer.get("mirror_to_host", True))

    @classmethod
    def _set_children_visibility(cls, element, hidden: bool) -> None:
        """Hide array children during edit so only the preview ghosts show.
        Auto-commit unhides on save; load-time heal clears stale flags."""
        layers = cls._read_layers(element)
        for layer in layers:
            for child_guid in layer.get("children", []):
                try:
                    child_element = tool.Ifc.get().by_guid(child_guid)
                except RuntimeError:
                    continue
                child_obj = tool.Ifc.get_object(child_element)
                if child_obj is not None:
                    child_obj.hide_set(hidden)

    @classmethod
    def _enable_one(cls, obj: bpy.types.Object, item: int = 0) -> None:
        """Enter array editing for layer ``item``; no-op for out-of-range index.

        If ``props.relating_array_object`` points at another array parent,
        seed the draft props from that object's matching layer."""
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        cls._handle_drift_on_enable(obj)
        source_layers = cls._layers_from_relating(props) or cls._read_layers(element)
        if item < 0 or item >= len(source_layers):
            return
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        cls._hydrate_props_from_layer(props, source_layers[item], si_conversion)
        props.is_editing = True
        props.editing_item_index = item
        cls._set_children_visibility(element, hidden=True)

    @classmethod
    def _layers_from_relating(cls, props) -> list | None:
        """If ``props.relating_array_object`` is set and resolves to another
        array parent, return its layers; else ``None``."""
        relating = getattr(props, "relating_array_object", None)
        if relating is None:
            return None
        element = tool.Ifc.get_entity(relating)
        if element is None:
            return None
        parent_guid = ifcopenshell.util.element.get_pset(element, "BBIM_Array", "Parent")
        if not parent_guid:
            return None
        try:
            parent_element = tool.Ifc.get().by_guid(parent_guid)
        except RuntimeError:
            return None
        data_text = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array", "Data")
        if not data_text:
            return None
        try:
            return json.loads(data_text)
        except (ValueError, TypeError):
            return None

    @classmethod
    def _finish_one(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Commit the in-progress edit to ``editing_item_index``'s layer.
        Drift (layer removed mid-edit) clears the flag and aborts."""
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        layers = cls._read_layers(element)
        item = props.editing_item_index
        if item < 0 or item >= len(layers):
            props.is_editing = False
            props.editing_item_index = -1
            return
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        layers[item]["count"] = props.count
        layers[item]["x"] = props.x / si_conversion
        layers[item]["y"] = props.y / si_conversion
        layers[item]["z"] = props.z / si_conversion
        layers[item]["use_local_space"] = props.use_local_space
        layers[item]["method"] = props.method
        layers[item]["per_child_opening"] = props.per_child_opening
        # Note: ``tool.Model.regenerate_array`` below removes and re-adds the
        # BBIM_Array pset with the in-memory ``layers`` data ([tool/model.py:
        # 1163-1167](src/bonsai/bonsai/tool/model.py#L1163-L1167)), so an
        # explicit ``edit_pset`` call here would just be overwritten — and
        # each redundant call adds an entry to the IFC owner-history audit
        # trail. Rely on the regenerator's pset write instead.
        tool.Array.remove_constraints(element)
        # Wipe-and-rebuild only when the parent's bbox dims differ from the
        # children's. For pure count / offset edits the children are already
        # valid and ``regenerate_array``'s in-place transform updates are
        # enough — saves the delete + re-duplicate cost per instance on
        # large arrays.
        if _array_children_need_rebuild(obj, layers):
            _wipe_array_children(layers)
        tool.Model.regenerate_array(obj, layers)
        tool.Array.set_children_lock_state(element, item, True)
        tool.Array.constrain_children_to_parent(element)
        # Set only on success: if any IFC op above raised, the draft survives for retry.
        props.is_editing = False
        props.editing_item_index = -1
        props.relating_array_object = None
        # Unhide the (possibly newly-regenerated) children so the user sees
        # the committed result. Mirrors the hide in ``_enable_one``.
        cls._set_children_visibility(element, hidden=False)
        tool.Array.select_only_parent(obj, context)

    @classmethod
    def _cancel_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        layers = cls._read_layers(element)
        item = props.editing_item_index
        if 0 <= item < len(layers):
            si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            cls._hydrate_props_from_layer(props, layers[item], si_conversion)
        props.is_editing = False
        props.editing_item_index = -1
        # Restore visibility — the pset is unchanged from when we hid them, so
        # the children's committed positions are still where they were before.
        cls._set_children_visibility(element, hidden=False)

    def _enable_targets(self, context: bpy.types.Context, item: int = 0) -> set[str]:
        for obj in self._iter_targets(context):
            self._enable_one(obj, item=item)
        return {"FINISHED"}

    def _finish_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._finish_one(obj, context)
        return {"FINISHED"}

    def _cancel_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._cancel_one(obj)
        return {"FINISHED"}


EnableEditingArray, FinishEditingArray, CancelEditingArray = tool.Parametric.build_edit_lifecycle(
    "array",
    _ArrayEditMixin,
    labels=(
        (
            "Enable Editing Array",
            "Edit this array — drag the offset arrows, adjust the count, switch the spacing method",
        ),
        ("Finish Editing Array", "Save the array changes and rebuild the copies"),
        ("Cancel Editing Array", "Discard the array changes and leave the existing copies as they were"),
    ),
    enable_extra_props={"item": bpy.props.IntProperty(name="Layer Index", default=0, min=0)},
    enable_extra_kwargs=lambda self: {"item": self.item},
    module_name=__name__,
)


class ApplyArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.apply_array"
    bl_label = "Apply Array"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Convert the array's copies into independent objects (last layer only)"

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
    bl_description = "Rebuild the array's copies from the original (works on parent or any copy)"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not pset or "Parent" not in pset:
            self.report({"ERROR"}, "Active object is not part of a Bonsai parametric array.")
            return {"CANCELLED"}
        try:
            parent_element = tool.Ifc.get().by_guid(pset["Parent"])
        except RuntimeError:
            self.report(
                {"ERROR"},
                f"Array parent GlobalId {pset['Parent']!r} not found — the array's parent "
                "element was deleted externally. Reseat the array by re-creating it.",
            )
            return {"CANCELLED"}
        parent = tool.Ifc.get_object(parent_element)
        pset = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array")
        arrays = json.loads(pset["Data"])
        pset = tool.Ifc.get().by_id(pset["id"])
        # Coalesce host recuts across the child-delete loop, the regenerate,
        # and the per-child opening mirror: each fans out its own host body
        # recut without the batch wrapper.
        with tool.Geometry.batch_host_recut():
            for array in arrays:
                for child in set(array["children"]):
                    try:
                        child_element = tool.Ifc.get().by_guid(child)
                    except RuntimeError:
                        continue
                    if child_obj := tool.Ifc.get_object(child_element):
                        tool.Geometry.delete_ifc_object(child_obj)
                array["children"].clear()
            # Always operate on the parent — this operator can be invoked with
            # either the parent OR any array child as active_object (the per-child
            # gizmo group fires it from a child selection). Using ``obj`` /
            # ``element`` directly would feed a child to ``regenerate_array`` and
            # constrain children against a sibling, silently corrupting the array.
            tool.Model.regenerate_array(parent, arrays)
            tool.Array.constrain_children_to_parent(parent_element)

        tool.Array.select_only_parent(parent, context)


class RemoveArray(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_array"
    bl_label = "Remove Array"
    bl_description = (
        "Remove this array layer (enable 'Keep Objects' to keep its copies as independent objects — last layer only)"
    )
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

        props.editing_item_index = -1

        try:
            parent_element = tool.Ifc.get().by_guid(pset["Parent"])
            parent = tool.Ifc.get_object(parent_element)
        except:
            return {"FINISHED"}

        with tool.Geometry.batch_host_recut():
            if self.keep_objs:
                tool.Array.bake_children_transform(element, self.item)
                tool.Array.set_children_lock_state(element, self.item, False)

            if not self.keep_objs:
                data[self.item]["count"] = 1
            tool.Array.remove_constraints(parent_element)
            tool.Model.regenerate_array(parent, data, array_layers_to_apply=[self.item] if self.keep_objs else [])

            pset = tool.Pset.get_element_pset(element, "BBIM_Array")
            if len(data) == 1:
                ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)
            else:
                del data[self.item]
                data = tool.Ifc.get().createIfcText(json.dumps(data))
                ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data})
                tool.Array.constrain_children_to_parent(element)


class SelectArrayParent(bpy.types.Operator):
    bl_idname = "bim.select_array_parent"
    bl_label = "Select Array Parent"
    bl_description = "Select the original object that this array copy belongs to"
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
    bl_description = "Select the original object and all of its array copies"
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

                    array_objects = tool.Array.get_all_objects(parent_element)
                    tool.Blender.set_objects_selection(
                        context,
                        active_object=array_objects[0],
                        selected_objects=array_objects,
                        clear_previous_selection=False,
                    )
        return {"FINISHED"}


class ArrayParentGizmoClick(bpy.types.Operator):
    """Dispatcher for the parent-tree gizmo on array children.

    - Click: select the array's parent.
    - Shift+Click: select parent + all children.
    - Ctrl+Click: select all children, excluding the parent."""

    bl_idname = "bim.array_parent_gizmo_click"
    bl_label = "Select Array Parent / Family"
    bl_description = (
        "Click: select the original object.\n"
        "Shift+Click: select the original object and all of its copies.\n"
        "Ctrl+Click: select only the copies"
    )
    bl_options = {"REGISTER", "UNDO"}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("PARENT", "Parent", "Select the array parent only"),
            ("ALL", "All", "Select parent + every child"),
            ("CHILDREN", "Children", "Select every child, excluding the parent"),
        ],
        default="PARENT",
    )

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            cls.poll_message_set("No active object selected")
            return False
        return True

    def invoke(self, context, event):
        if event.shift:
            self.mode = "ALL"
        elif event.ctrl:
            self.mode = "CHILDREN"
        else:
            self.mode = "PARENT"
        return self.execute(context)

    def execute(self, context):
        if self.mode == "PARENT":
            return bpy.ops.bim.select_array_parent("EXEC_DEFAULT")
        if self.mode == "ALL":
            return bpy.ops.bim.select_all_array_objects("EXEC_DEFAULT")
        # CHILDREN: resolve the parent of the active child, then select every
        # child of that parent's array without the parent itself.
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        if element is None:
            self.report({"ERROR"}, "Active object is not IFC-linked.")
            return {"CANCELLED"}
        array_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not array_pset:
            self.report({"ERROR"}, "Object is not part of an array.")
            return {"CANCELLED"}
        try:
            parent_element = tool.Ifc.get().by_guid(array_pset["Parent"])
        except RuntimeError:
            self.report({"ERROR"}, f"Couldn't find array parent by guid '{array_pset['Parent']}'")
            return {"CANCELLED"}
        all_objects = tool.Array.get_all_objects(parent_element)
        parent_obj = tool.Ifc.get_object(parent_element)
        children = [o for o in all_objects if o is not parent_obj]
        if not children:
            self.report({"INFO"}, "Array has no children to select.")
            return {"FINISHED"}
        tool.Blender.set_objects_selection(
            context,
            active_object=children[0],
            selected_objects=children,
            clear_previous_selection=True,
        )
        return {"FINISHED"}


class EditArrayFromChild(bpy.types.Operator):
    bl_idname = "bim.edit_array_from_child"
    bl_label = "Edit Array From Child"
    bl_description = "Edit the array this copy belongs to"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            cls.poll_message_set("No active object selected")
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        if element is None:
            self.report({"ERROR"}, "Active object is not IFC-linked.")
            return {"CANCELLED"}
        array_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not array_pset:
            self.report({"ERROR"}, "Object is not part of an array.")
            return {"CANCELLED"}
        try:
            parent_element = tool.Ifc.get().by_guid(array_pset["Parent"])
        except RuntimeError:
            self.report({"ERROR"}, f"Couldn't find array parent by guid '{array_pset['Parent']}'")
            return {"CANCELLED"}
        parent_obj = tool.Ifc.get_object(parent_element)
        if not parent_obj:
            self.report({"ERROR"}, "Array parent has no Blender object.")
            return {"CANCELLED"}
        layer_index = tool.Array.get_child_layer_index(element)
        if layer_index is None:
            layer_index = 0
        tool.Blender.select_and_activate_single_object(context, active_object=parent_obj)
        return bpy.ops.bim.enable_editing_array("INVOKE_DEFAULT", item=layer_index)


class Input3DCursorXArray(bpy.types.Operator):
    bl_idname = "bim.input_cursor_x_array"
    bl_label = "Get 3d Cursor X Input for Array"
    bl_description = "Set the X offset from the 3D cursor position"
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
    bl_description = "Set the Y offset from the 3D cursor position"
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
    bl_description = "Set the Z offset from the 3D cursor position"
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


class ArrayGizmoClick(bpy.types.Operator):
    """Per-layer ARRAY gizmo dispatcher: click enters edit for that layer,
    Shift+click adds a new layer with bbox-derived defaults.

    Wired to each layer icon in ``GizmoArrayEdition``'s row-of-arrays. The
    ``item`` property identifies which layer the user clicked, so the same
    operator class is reused across all surfaced layer gizmos."""

    bl_idname = "bim.array_gizmo_click"
    bl_label = "Array Layer"
    bl_description = "Click: edit this array layer.\n" "Shift+Click: add another array layer"
    bl_options = {"REGISTER", "UNDO"}

    item: bpy.props.IntProperty(name="Layer Index", default=0, min=0)

    def invoke(self, context, event):
        if event.shift:
            # Pass ``axis="X"`` via EXEC_DEFAULT to bypass
            # ``AddArrayFromFeatureEdit.invoke``'s modifier read — Shift on
            # the layer-indicator gizmo already means "add new layer", so
            # we shouldn't reinterpret it as "axis = Y" downstream.
            return bpy.ops.bim.add_array_from_feature_edit("EXEC_DEFAULT", axis="X")
        return bpy.ops.bim.enable_editing_array("INVOKE_DEFAULT", item=self.item)

    def execute(self, context):
        # No event in scripting / keymap exec contexts — plain enter-edit fallback.
        return bpy.ops.bim.enable_editing_array("EXEC_DEFAULT", item=self.item)


class EnableEditingParametric(bpy.types.Operator):
    """Pen-icon dispatcher: fires the gizmo group's per-feature edit operator.

    Bound to every parametric gizmo group's pen icon. The gizmo group's own
    ``enable_editing_operator`` (``bim.enable_editing_door``, ``…_wall``, …)
    is passed as ``feature_enable_op`` at setup time and invoked here. The
    indirection lets one gizmo class serve all features without per-feature
    subclasses.

    Array editing has its own dedicated entry points (the per-layer ARRAY
    gizmo icons and the panel's pen button) — this dispatcher does not
    branch into array edit anymore."""

    bl_idname = "bim.enable_editing_parametric"
    bl_label = "Enable Editing"
    bl_description = "Edit this object's parameters"
    bl_options = {"REGISTER", "UNDO"}

    feature_enable_op: bpy.props.StringProperty(
        default="",
        description="Operator bl_idname to invoke (e.g., 'bim.enable_editing_door').",
    )
    sibling_count: bpy.props.IntProperty(default=0, options={"HIDDEN"})

    @staticmethod
    def should_show_shared_rep_dialog(*, suppress: bool, has_entity: bool, sibling_count: int) -> bool:
        """Pure decision for the pre-edit warning. Returns ``True`` only when the
        edit will silently mutate other elements' geometry AND the user has not
        opted out of the warning for this session."""
        if suppress or not has_entity:
            return False
        return sibling_count > 0

    def invoke(self, context, event):
        prefs = getattr(context.window_manager, "BIMParametricEditDialogPrefs", None)
        suppress = bool(prefs and prefs.suppress_shared_rep_warning)
        obj = context.active_object
        element = tool.Ifc.get_entity(obj) if obj else None
        self.sibling_count = tool.Model.get_sibling_occurrence_count(element) if element is not None else 0
        if self.should_show_shared_rep_dialog(
            suppress=suppress, has_entity=element is not None, sibling_count=self.sibling_count
        ):
            return context.window_manager.invoke_props_dialog(self, width=400)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Shared geometry", icon="ERROR")
        layout.label(text=f"Geometry is shared with {self.sibling_count} other element(s).")
        layout.label(text="Edits will affect them too.")
        prefs = context.window_manager.BIMParametricEditDialogPrefs
        layout.prop(prefs, "suppress_shared_rep_warning", text="Don't show this again for this session")

    def execute(self, context):
        # Malformed ``feature_enable_op`` (missing dot) would otherwise crash
        # the unpack with ValueError; treat the same as the empty-string case.
        parts = self.feature_enable_op.split(".", 1)
        if len(parts) != 2:
            return {"CANCELLED"}
        domain, opname = parts
        return getattr(getattr(bpy.ops, domain), opname)("INVOKE_DEFAULT")


class ToggleArrayMethod(bpy.types.Operator):
    """Cycle the array layer's ``method`` between OFFSET and DISTRIBUTE.

    OFFSET: each instance is placed at ``i * (x, y, z)`` from the parent —
    spacing is fixed, total span scales with count.

    DISTRIBUTE: instances are spread evenly between the parent and the offset
    endpoint — total span is fixed at ``(x, y, z)``, spacing scales with count.

    No-op outside an active edit lifecycle so the operator can't bypass the Finish
    commit lifecycle by quietly flipping the method during a non-editing state."""

    bl_idname = "bim.toggle_array_method"
    bl_label = "Toggle Array Method"
    bl_description = "Switch between fixed spacing between copies and fixed total span"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = _resolve_array_edit_props(context)
        if props is None:
            return {"CANCELLED"}
        props.method = "DISTRIBUTE" if props.method == "OFFSET" else "OFFSET"
        return {"FINISHED"}


class RemoveArrayLayerFromEdit(bpy.types.Operator, tool.Ifc.Operator):
    """Discard the in-progress edit and delete the array layer being edited.

    Bound to the trash gizmo at the far right of the edit row. Reads the
    currently-edited layer from ``props.editing_item_index``, cancels the
    edit lifecycle (unhides children, clears editing flags), then routes through
    ``bim.remove_array`` to delete the layer from the BBIM_Array pset.
    Existing children of that layer are deleted as part of remove_array.

    Inherits ``tool.Ifc.Operator`` so the two chained sub-operators
    (``bim.cancel_editing_array`` + ``bim.remove_array``) run inside one
    transaction — one undo step instead of two, and an atomic rollback if
    the second op fails (no torn state where the draft is gone but the
    layer remains). The nested ``tool.Ifc.Operator`` calls detect the
    existing top-level transaction (via ``IfcStore.current_transaction``
    in [bim/ifc.py:486](src/bonsai/bonsai/bim/ifc.py#L486)) and join it
    rather than opening their own."""

    bl_idname = "bim.remove_array_layer_from_edit"
    bl_label = "Remove Array Layer"
    bl_description = "Discard the in-progress edit and delete this array layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = _resolve_array_edit_props(context)
        if props is None:
            cls.poll_message_set("No active object or not editing an array")
            return False
        # Mirror ``_execute``'s precondition so the gizmo correctly
        # disables on stale states (is_editing flag set but the index
        # was cleared by drift, undo, or external mutation).
        return props.editing_item_index >= 0

    def _execute(self, context):
        props = _resolve_array_edit_props(context)
        if props is None:
            return {"CANCELLED"}
        item = props.editing_item_index
        if item < 0:
            return {"CANCELLED"}
        # Cancel the in-progress edit first — this unhides children and
        # clears is_editing / editing_item_index. Then remove the layer
        # (which deletes its children and the layer's BBIM_Array entry).
        # Both calls join this operator's transaction (see class docstring).
        bpy.ops.bim.cancel_editing_array("EXEC_DEFAULT")
        bpy.ops.bim.remove_array("EXEC_DEFAULT", item=item)
        return {"FINISHED"}


class InputArrayCount(IntegerInputDialogMixin, bpy.types.Operator):
    """Popup-dialog entry point for typing a new draft ``count`` during an
    active array edit lifecycle. Bound to the world-space count gizmo in
    the edit row."""

    bl_idname = "bim.input_array_count"
    bl_label = "Set Array Count"
    bl_description = "Type the number of copies for this array"
    bl_options = {"REGISTER", "UNDO"}

    count: bpy.props.IntProperty(name="Count", default=1, min=1)
    attr_name = "count"
    props_getter = staticmethod(tool.Model.get_array_props)
    requires_editing = True


class AdjustArrayCount(bpy.types.Operator):
    """Bump props.count by ``increment`` during an active element-wide edit lifecycle.

    Bound to the +/- icon gizmos flanking the count drag handle. No-ops outside
    an edit lifecycle so accidentally invoking it doesn't bypass the commit lifecycle —
    Finish writes IFC; this operator only touches the draft props."""

    bl_idname = "bim.adjust_array_count"
    bl_label = "Adjust Array Count"
    bl_description = "Add or remove a copy from the array"
    bl_options = {"REGISTER", "UNDO"}
    increment: bpy.props.IntProperty()

    def execute(self, context):
        props = _resolve_array_edit_props(context)
        if props is None:
            return {"CANCELLED"}
        props.count = max(1, props.count + self.increment)
        return {"FINISHED"}


class GizmoArrayEdition(bpy.types.GizmoGroup, gizmo.BaseParametricGizmoGroup):
    """Viewport gizmos for the array edit lifecycle (single-layer arrays only).
    Drag/+/- mutate draft props in place; commit happens at Finish."""

    bl_idname = "OBJECT_GGT_bim_array_edition"
    bl_label = "Array Editing Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    enable_editing_operator = "bim.enable_editing_array"
    finish_editing_operator = "bim.finish_editing_array"
    cancel_editing_operator = "bim.cancel_editing_array"
    cycle_type_operator = ""
    # Array is not itself arrayable from the gizmo entry — adding an array
    # layer to an existing array is the panel's "+" button job. Hides the
    # base-class ARRAY icon for this gizmo group only.
    hide_array_button = True
    # The clickable ``xN`` count label (``GizmoArrayCount``) is already the
    # entry point for array edit mode from the idle state — see this class's
    # docstring. The default pen icon emitted by ``BaseParametricGizmoGroup``
    # is redundant with it, and on a feature object that's ALSO array-parent
    # (e.g. an arrayed duct segment) the user sees two pen icons: one for the
    # feature edit, one next to the array count. Hiding this group's pen
    # collapses to a single per-feature pen.
    hide_pen_button = True

    # Editing row layout: validate | cancel | xN | - | + | method | trash.
    # The ``count_label`` placeholder reserves the position for the
    # dynamically-built ``xN`` gizmo; the +/-/method/trash icons live in
    # ``feature_slots`` below and the base class assigns X positions from
    # tuple order. The trash carries ``extra_gap_before`` to visually
    # separate the destructive action from the routine controls.

    # Render scale for the +/- and method-toggle icons — ~70% of the standard
    # 0.5 used for validate/cancel. Makes the helpers look secondary.
    ICON_HELPER_SCALE = 0.35

    feature_slots: ClassVar[tuple[IconSlot, ...]] = (
        IconSlot(name="count_label", placeholder=True),
        IconSlot(
            name="count_minus",
            gizmo_idname="VIEW3D_GT_minus",
            operator="bim.adjust_array_count",
            scale=ICON_HELPER_SCALE,
            color=COLOR_RED,
            operator_props=(("increment", -1),),
        ),
        IconSlot(
            name="count_plus",
            gizmo_idname="VIEW3D_GT_plus",
            operator="bim.adjust_array_count",
            scale=ICON_HELPER_SCALE,
            color=COLOR_GREEN,
            operator_props=(("increment", 1),),
        ),
        IconSlot(
            name="method",
            gizmo_idname="VIEW3D_GT_cycle",
            operator="bim.toggle_array_method",
            scale=ICON_HELPER_SCALE,
        ),
        IconSlot(
            name="delete",
            gizmo_idname="VIEW3D_GT_trash",
            operator="bim.remove_array_layer_from_edit",
            scale=ICON_HELPER_SCALE,
            color=COLOR_RED,
            # Extra gap so the destructive action stays visually separated
            # from the routine edit controls — matches the prior 0.57 gap.
            extra_gap_before=0.20,
        ),
    )

    # Per-layer ARRAY icons — one shown in idle state per existing array
    # layer, surfaced to the right of the pen. Pre-allocated at setup time
    # (Blender's gizmo API doesn't support creating gizmos on demand at draw
    # time); the cap keeps the GPU resource footprint bounded. Multi-layer
    # arrays with more than ``MAX_LAYER_GIZMOS`` layers fall back to the
    # per-item panel UX for the overflow layers.
    MAX_LAYER_GIZMOS = 8
    # Local-X spacing between successive layer icons. The start position
    # is computed per-frame from peer parametric gizmo groups' idle rows
    # (see ``_resolve_feature_idle_max_x``) so layer icons clear any
    # feature-specific idle slots (e.g. wall's toggle-openings).
    LAYER_GIZMO_SPACING = 0.4

    dimension_gizmo_props = [
        # matrix_position must be provided even at the origin: without it, the
        # base class falls back to ``Matrix.Identity(4)`` for ``base_matrix``,
        # which means ``matrix_basis.col[0]`` (what GizmoDimension.draw reads
        # for the line direction) becomes the object's local X — every offset
        # gizmo would then render along X regardless of ``config.axis``.
        # ``compose_gizmo_matrix(position, axis)`` rotates so col[0] aligns with
        # the requested axis. The non-zero offsets along the OTHER two axes
        # shift each gizmo's origin off the object centre so they don't pile
        # up at (0,0,0).
        # Each offset gizmo starts at the centre of the bounding-box face
        # perpendicular to its axis (e.g. X-offset anchors at the +X face
        # centre). This pulls the three arrows apart visually and makes the
        # arrow tip land exactly where the next instance would appear — a
        # natural read of "drag this face out by N metres to space siblings".
        DimensionGizmoConfig(
            attr_name="x",
            axis=(1, 0, 0),
            prop_name="X Offset",
            min_value=-1e6,
            matrix_position=lambda p: GizmoArrayEdition._axis_start(0),
        ),
        DimensionGizmoConfig(
            attr_name="y",
            axis=(0, 1, 0),
            prop_name="Y Offset",
            min_value=-1e6,
            matrix_position=lambda p: GizmoArrayEdition._axis_start(1),
        ),
        DimensionGizmoConfig(
            attr_name="z",
            axis=(0, 0, 1),
            prop_name="Z Offset",
            min_value=-1e6,
            matrix_position=lambda p: GizmoArrayEdition._axis_start(2),
        ),
    ]

    props_getter = tool.Model.get_array_props
    gizmo_pref_name = "array"

    @staticmethod
    def _axis_start(axis_index: int) -> Vector:
        """Local-space anchor for the offset gizmo on the given axis: the
        centre of the bounding-box face perpendicular to that axis on its
        positive side.

        Axis 0 (X) → centre of the +X face;
        Axis 1 (Y) → centre of the +Y face;
        Axis 2 (Z) → centre of the +Z face.

        Returns ``Vector((0, 0, 0))`` when ``bpy.context.active_object`` is
        unset or has no ``bound_box`` attribute. For 0-extent objects (Empties,
        point annotations) the bbox is 8 zero-corners and the math yields the
        origin naturally — same result, different path."""
        obj = bpy.context.active_object
        if obj is None or not obj.bound_box:
            return Vector((0.0, 0.0, 0.0))
        bbox = tool.Blender.get_object_bounding_box(obj)
        center = bbox["center"]
        if axis_index == 0:
            return Vector((bbox["max_x"], center.y, center.z))
        if axis_index == 1:
            return Vector((center.x, bbox["max_y"], center.z))
        return Vector((center.x, center.y, bbox["max_z"]))

    @classmethod
    def is_element_type(cls, element: "ifcopenshell.entity_instance") -> bool:
        """Poll for any array parent — multi-layer is fully supported now via
        the per-layer ARRAY icons. The edit lifecycle reads ``editing_item_index`` to
        pick the target layer."""
        return tool.Parametric.is_array(element)

    def setup_element_specific_gizmos(self, context: bpy.types.Context) -> None:
        """Create the world-space count label and per-layer ARRAY entry icons.
        The +/- count adjusters, method toggle, and delete button live in
        ``feature_slots`` and are auto-created by the base class."""
        default_color, highlight_color = self.get_decoration_colors()
        # World-space count display for the edit row. Click opens a numeric
        # input dialog so the user can type a value directly instead of
        # clicking +/- repeatedly. Renders the same ``xN`` glyph as the
        # idle-state per-layer icons for visual consistency. Position is
        # reserved by the ``count_label`` placeholder slot in
        # ``feature_slots``; the matrix is set per-frame below.
        self.count_label_gizmo = self.gizmos.new("BIM_GT_array_layer_indicator")
        self.count_label_gizmo.use_draw_scale = False
        self.count_label_gizmo.color = default_color
        self.count_label_gizmo.color_highlight = highlight_color
        self.count_label_gizmo.alpha = 0.8
        self.count_label_gizmo.target_set_operator("bim.input_array_count")

        # Per-layer ARRAY icons — pre-allocated up to ``MAX_LAYER_GIZMOS`` and
        # shown/hidden in ``_refresh_element_specific`` based on the actual
        # layer count. ``BIM_GT_array_layer_indicator`` renders the 2×2-grid
        # glyph PLUS an ``xN`` count label above it (one custom gizmo per
        # layer keeps the label co-located with the icon at all zoom levels).
        # Each binds to ``bim.array_gizmo_click(item=i)``; the dispatcher
        # routes plain clicks to ``enable_editing_array(item=i)`` and
        # Shift+click to ``add_array_from_feature_edit`` (new layer).
        self.layer_gizmos = []
        for i in range(self.MAX_LAYER_GIZMOS):
            gz = self.gizmos.new("BIM_GT_array_layer_indicator")
            gz.use_draw_scale = False
            gz.color = default_color
            gz.color_highlight = highlight_color
            gz.alpha = 0.8
            op = gz.target_set_operator("bim.array_gizmo_click")
            op.item = i
            # Bind layer index for the hover-publisher inside the gizmo's own
            # draw method (see ``GizmoArrayLayerIndicator._publish_hover``).
            gz.set_layer_index(i)
            self.layer_gizmos.append(gz)

    def get_icon_y_extent(self, props) -> tuple[float, float]:
        """Return the active object's bounding-box Y extents (positive,
        negative absolute distances from origin) plus the standard 2× icon
        clearance — same pattern feature gizmo groups use for their pen-icon
        Y position. Without this, the array layer icons sit at the object
        centerline while the feature pen sits at the camera-facing edge, and
        the two rows end up on different local Y planes."""
        obj = bpy.context.active_object
        if obj is None or not obj.bound_box:
            return (0.0, 0.0)
        ys = [c[1] for c in obj.bound_box]
        pad = 2 * self.GIZMO_OFFSET
        return (max(0.0, max(ys)) + pad, max(0.0, -min(ys)) + pad)

    def get_element_height(self, props) -> float:
        """Return the visual top of the active object (bounding-box Z max) so the
        array validate/cancel icons sit at the same world position as the
        feature gizmo group's pen icon would on the same element.

        Why not the base behaviour: the base reads ``props.overall_height`` /
        ``props.height``, but ``BIMArrayProperties`` has neither — the array layer
        list doesn't know how tall the underlying door / wall / … actually is.
        Using the bounding-box top is a generic proxy that works for every
        arrayable IFC type, parametric or otherwise."""
        obj = bpy.context.active_object
        if obj and obj.bound_box:
            return tool.Blender.get_object_bounding_box(obj)["max_z"]
        return 1.0

    def _refresh_element_specific(self, context: bpy.types.Context, mw: Matrix, props) -> None:
        """Position the count label and per-layer ARRAY icons.

        Idle (``not props.is_editing``): show one ARRAY icon per existing
        array layer to the right of the pen. The +/-, method, and delete
        slot icons stay hidden (handled by the base).

        Active edit: show the count label; hide the per-layer icons. The
        +/-, method, and delete icons are positioned by the base class
        via the slot layout — no manual positioning needed here."""
        icon_z = self.get_element_height(props) + self.ICON_Z_OFFSET
        icon_y = self.get_icon_y_offset(context, mw)
        billboard_rot = self._frame_billboard_rot

        if not props.is_editing:
            self.count_label_gizmo.hide = True
            layers = self._read_array_layers(context)
            layer_count = min(len(layers), self.MAX_LAYER_GIZMOS)
            # Feature-aware start X — pushes the layer icons past any
            # feature-specific idle gizmos (e.g. wall's toggle-openings +
            # offset-baseline) so they don't stack on top.
            start_x = self.ICON_VALIDATE_X + self._resolve_feature_idle_max_x(context) + self.ICON_ARRAY_GAP
            for i, gz in enumerate(self.layer_gizmos):
                if i >= layer_count:
                    gz.hide = True
                    continue
                if self.is_gizmo_hidden_by_modal(gz):
                    gz.hide = True
                    continue
                gz.hide = False
                # Per-layer count rendered as ``xN`` above the gizmo glyph.
                gz.set_count(int(layers[i].get("count", 0)))
                world_pos = mw @ Vector(
                    (
                        start_x + i * self.LAYER_GIZMO_SPACING,
                        icon_y,
                        icon_z,
                    )
                )
                gz.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot, scale=0.5)
            return

        # Active edit: hide the layer icons, show the count label. The
        # +/-, method, and delete slot icons are positioned by the base.
        for gz in self.layer_gizmos:
            gz.hide = True
        # Clickable world-space ``xN`` between cancel and minus. Mirrors the
        # draft ``props.count`` so the displayed value tracks +/- drags live.
        if self.is_gizmo_hidden_by_modal(self.count_label_gizmo):
            self.count_label_gizmo.hide = True
        else:
            self.count_label_gizmo.hide = False
            self.count_label_gizmo.set_count(int(props.count))
            world_pos = mw @ Vector(
                (
                    self.ICON_VALIDATE_X + self._slot_x_positions()["count_label"],
                    icon_y,
                    icon_z,
                )
            )
            self.count_label_gizmo.matrix_basis = gizmo.billboarded_at(
                world_pos, billboard_rot, scale=self.ICON_HELPER_SCALE
            )

    @staticmethod
    def _read_array_layers(context: bpy.types.Context) -> list:
        """Return the active object's BBIM_Array layer list (one dict per
        layer), or an empty list if not resolvable. Used to decide how many
        per-layer ARRAY icons to surface AND to read each layer's ``count``
        for the ``xN`` label rendered by ``GizmoArrayLayerIndicator``."""
        obj = context.active_object
        if obj is None:
            return []
        element = tool.Ifc.get_entity(obj)
        if element is None:
            return []
        data_text = ifcopenshell.util.element.get_pset(element, "BBIM_Array", "Data")
        if not data_text:
            return []
        try:
            return json.loads(data_text)
        except (ValueError, TypeError):
            return []

    @classmethod
    def _resolve_feature_idle_max_x(cls, context: bpy.types.Context) -> float:
        """Rightmost local-X reserved by any peer ``BaseParametricGizmoGroup``
        whose ``poll`` passes on the active element. Per-layer ARRAY icons
        start one ``ICON_ARRAY_GAP`` past this so they don't stack on top of
        feature-specific idle slots (e.g. wall's toggle_openings).

        Walks ``BaseParametricGizmoGroup.REGISTRY`` rather than indexing a
        hardcoded per-feature table: each peer's ``_idle_row_right_edge()``
        derives from its declared ``idle_slots`` tuple, so adding an idle
        icon to any feature is a one-line ``IconSlot`` append with no
        coordination needed here. Defaults to 0.0 when no active object or
        no peer polls visible."""
        obj = context.active_object
        if obj is None:
            return 0.0
        max_x = 0.0
        for peer_cls in gizmo.BaseParametricGizmoGroup.REGISTRY:
            if peer_cls is cls:
                continue
            try:
                if not peer_cls.poll(context):
                    continue
            except Exception:
                continue
            edge = peer_cls._idle_row_right_edge()
            if edge > max_x:
                max_x = edge
        return max_x


class GizmoArrayChild(bpy.types.GizmoGroup, gizmo.BillboardingGizmoGroupMixin):
    """Two navigation icons on each array child:

    - ``VIEW3D_GT_array_parent`` (hierarchy tree) → modifier-aware select via
      ``bim.array_parent_gizmo_click``: click selects the parent, Shift+click
      selects the whole family, Ctrl+click selects only the children.
    - ``VIEW3D_GT_array_all`` (2×2 grid) → jump to the parent and enter
      array edit.

    Standalone gizmo group (not a ``BaseParametricGizmoGroup`` subclass)
    because the base's ``poll`` early-returns on array children — there's
    nothing to edit on a managed replica. Regenerate isn't surfaced as a
    child gizmo; the panel still exposes it."""

    bl_idname = "OBJECT_GGT_bim_array_child"
    bl_label = "Array Child Helpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    # Local-X positions for the two icons above the child's bounding-box top.
    # 0.5 spacing keeps the hit regions clear at standard view distances.
    ICON_PARENT_X = 0.0
    ICON_ALL_X = 0.5
    ICON_Z_OFFSET = 0.5
    ICON_SCALE = 0.5

    @classmethod
    def poll(cls, context):
        obj = tool.Blender.get_active_object(is_selected=True)
        if obj is None:
            return False
        if not tool.Blender.are_viewport_gizmos_enabled():
            return False
        if len(tool.Blender.get_selected_objects()) != 1:
            return False
        element = tool.Ifc.get_entity(obj)
        if not element:
            return False
        return tool.Blender.Modifier.is_array_child(element)

    def setup(self, context: bpy.types.Context) -> None:
        default_color, highlight_color = self.get_unselected_decoration_colors()
        self.parent_gizmo = self.setup_icon_gizmo(
            "VIEW3D_GT_array_parent", default_color, highlight_color, "bim.array_parent_gizmo_click"
        )
        self.all_gizmo = self.setup_icon_gizmo(
            "VIEW3D_GT_array_all", default_color, highlight_color, "bim.edit_array_from_child"
        )

    def position_gizmos(self, context: bpy.types.Context) -> None:
        obj = context.active_object
        if obj is None or not obj.bound_box:
            return
        bbox_top = max(corner[2] for corner in obj.bound_box)
        billboard_rot = gizmo.get_billboard_rotation(context)
        mw = obj.matrix_world
        for name, x in (
            ("parent_gizmo", self.ICON_PARENT_X),
            ("all_gizmo", self.ICON_ALL_X),
        ):
            gz = getattr(self, name)
            world_pos = mw @ Vector((x, 0, bbox_top + self.ICON_Z_OFFSET))
            gz.matrix_basis = gizmo.billboarded_at(world_pos, billboard_rot, self.ICON_SCALE)


_ARRAY_LAYER_BBOX_MAX_CHILDREN = 200


def draw_array_layer_children_bbox(
    context: bpy.types.Context,
    parent_element: ifcopenshell.entity_instance,
    layer_index: int,
    max_children: int = _ARRAY_LAYER_BBOX_MAX_CHILDREN,
) -> None:
    """Paint a wireframe bbox around every child of one array layer in the
    same 3D pass. Called inline from gizmo ``draw()`` methods so the highlight
    tracks the hover cursor one-for-one — no POST_VIEW handler, no timing lag.

    Total: silently no-ops on missing pset, unparseable JSON, out-of-range
    layer index, unresolvable child GUIDs, or empty child geometry."""
    if layer_index < 0:
        return
    data_text = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array", "Data")
    if not data_text:
        return
    try:
        layers = json.loads(data_text)
    except (ValueError, TypeError):
        return
    if layer_index >= len(layers):
        return
    child_guids = layers[layer_index].get("children", [])
    if not child_guids:
        return
    ifc_file = tool.Ifc.get()
    segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
    for guid in child_guids[:max_children]:
        try:
            child_element = ifc_file.by_guid(guid)
        except RuntimeError:
            continue
        child_obj = tool.Ifc.get_object(child_element)
        if child_obj is None:
            continue
        segments.extend(bbox_world_edges(child_obj))
    if not segments:
        return
    prefs = tool.Blender.get_addon_preferences()
    color = prefs.decorator_color_special[:3]
    draw_polyline_segments(
        context,
        segments,
        color,
        _BBOX_HIGHLIGHT_LINE_ALPHA,
        _BBOX_HIGHLIGHT_LINE_WIDTH,
    )


class ArrayPreviewDecorator(tool.Blender.ViewportDecorator):
    """Faint bbox wireframe at each future array instance during the edit lifecycle.
    Pure GPU preview gated on the array's draft props — no IFC mutation."""

    LINE_WIDTH = 1.2
    LINE_ALPHA = 0.45
    MAX_PREVIEW_INSTANCES = 200

    def draw(self, context: bpy.types.Context) -> None:
        if not tool.Blender.are_viewport_gizmos_enabled():
            return
        prefs = tool.Blender.get_addon_preferences()
        obj = context.active_object
        if obj is None or not obj.bound_box:
            return
        element = tool.Ifc.get_entity(obj)
        if not element or not tool.Parametric.is_array(element):
            return
        props = tool.Model.get_array_props(obj)
        if not props.is_editing:
            return
        count = int(props.count)
        if count <= 1 or count > self.MAX_PREVIEW_INSTANCES:
            return

        segments = self._compute_segments(obj, props, count)
        if not segments:
            return

        color = prefs.decorator_color_selected[:3]
        draw_polyline_segments(context, segments, color, self.LINE_ALPHA, self.LINE_WIDTH)

    def _compute_segments(
        self,
        parent_obj: bpy.types.Object,
        props,
        count: int,
    ) -> list[tuple[tuple[float, float, float], tuple[float, float, float]]]:
        """World-space (start, end) line segments for the bbox edges of
        every future instance (i = 1 … count-1; i = 0 is the parent itself).
        props.x/y/z are SI — the edit-lifecycle Enable hydrates them via
        si_conversion, so no unit_scale multiplier here."""
        offset = Vector((props.x, props.y, props.z))
        if props.method == "DISTRIBUTE":
            divider = (count - 1) if count > 1 else 1
            offset = offset / divider

        parent_mw = parent_obj.matrix_world
        parent_corners = [Vector(c) for c in parent_obj.bound_box]
        segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
        for i in range(1, count):
            delta = offset * i
            child_mw = parent_mw.copy()
            if props.use_local_space:
                child_mw.translation = parent_mw @ delta
            else:
                child_mw.translation = parent_mw.translation + delta
            world_corners = [child_mw @ corner for corner in parent_corners]
            for a, b in _BBOX_EDGES:
                segments.append((tuple(world_corners[a]), tuple(world_corners[b])))
        return segments


class ArraySelectionHighlightDecorator(tool.Blender.ViewportDecorator):
    """Bounding-box overlay surfacing the array family of the selected object.

    Two activation modes:

    - **Child selected** — parent drawn in the addon's *special*
      decorator color (bright accent); other siblings in the *unselected*
      color at lower alpha so the parent stands out. The selected child
      itself keeps Blender's standard selection outline.
    - **Parent selected** (idle, not editing) — every existing child drawn
      in the *unselected* color at lower alpha. The parent is already
      visually flagged by Blender's selection outline. Suppressed during
      an active array edit lifecycle so the live preview wireframes don't
      double-draw with the existing-children overlay."""

    LINE_WIDTH = 1.5
    PARENT_ALPHA = 0.7
    SIBLING_ALPHA = 0.35
    MAX_SIBLINGS = 200

    def __init__(self) -> None:
        self._family_cache: TokenCache = TokenCache()

    def draw(self, context: bpy.types.Context) -> None:
        if not tool.Blender.are_viewport_gizmos_enabled():
            return
        prefs = tool.Blender.get_addon_preferences()
        obj = context.active_object
        if obj is None:
            return
        if not obj.select_get():
            return
        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        if tool.Blender.Modifier.is_array_child(element):
            self._draw_for_child(context, prefs, element, obj)
        elif tool.Parametric.is_array(element):
            props = tool.Model.get_array_props(obj)
            if not props.is_editing:
                self._draw_for_parent(context, prefs, element, obj)

    def _draw_for_child(self, context, prefs, element, obj):
        family = self._resolve_family_for_child(obj, element)
        if family is None:
            return
        parent_obj, sibling_objs = family

        parent_segments = bbox_world_edges(parent_obj)
        if parent_segments:
            draw_polyline_segments(
                context,
                parent_segments,
                prefs.decorator_color_special[:3],
                self.PARENT_ALPHA,
                self.LINE_WIDTH,
            )
        self._draw_siblings(context, prefs, sibling_objs)

    def _draw_for_parent(self, context, prefs, element, obj):
        child_objs = self._resolve_children_for_parent(obj, element)
        self._draw_siblings(context, prefs, child_objs)

    def _resolve_family_for_child(self, obj, element):
        return self._family_cache.get_or_compute(
            ("child", obj.session_uid, element.id()),
            lambda: self._collect_family_from_child(element, obj),
        )

    def _resolve_children_for_parent(self, obj, element):
        return (
            self._family_cache.get_or_compute(
                ("parent", obj.session_uid, element.id()),
                lambda: self._collect_children(element, exclude=obj),
            )
            or []
        )

    def _draw_siblings(self, context, prefs, sibling_objs):
        if not sibling_objs:
            return
        if len(sibling_objs) > self.MAX_SIBLINGS:
            sibling_objs = sibling_objs[: self.MAX_SIBLINGS]
        segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
        for sib_obj in sibling_objs:
            segments.extend(bbox_world_edges(sib_obj))
        draw_polyline_segments(
            context,
            segments,
            prefs.decorator_color_unselected[:3],
            self.SIBLING_ALPHA,
            self.LINE_WIDTH,
        )

    def _collect_family_from_child(self, element, obj):
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not pset:
            return None
        parent_guid = pset.get("Parent")
        if not parent_guid:
            return None
        try:
            parent_element = tool.Ifc.get().by_guid(parent_guid)
        except RuntimeError:
            return None
        parent_obj = tool.Ifc.get_object(parent_element)
        if not parent_obj:
            return None
        siblings = self._collect_children(parent_element, exclude=obj, also_exclude=parent_obj)
        return parent_obj, siblings

    def _collect_children(self, parent_element, exclude=None, also_exclude=None):
        parent_data_text = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array", "Data")
        if not parent_data_text:
            return []
        try:
            layers = json.loads(parent_data_text)
        except (ValueError, TypeError):
            return []
        children: list[bpy.types.Object] = []
        seen_ids: set[int] = set()
        if exclude is not None:
            seen_ids.add(id(exclude))
        if also_exclude is not None:
            seen_ids.add(id(also_exclude))
        for layer in layers:
            for child_guid in layer.get("children", []):
                try:
                    child_element = tool.Ifc.get().by_guid(child_guid)
                except RuntimeError:
                    continue
                child_obj = tool.Ifc.get_object(child_element)
                if child_obj is None or id(child_obj) in seen_ids:
                    continue
                seen_ids.add(id(child_obj))
                children.append(child_obj)
        return children
