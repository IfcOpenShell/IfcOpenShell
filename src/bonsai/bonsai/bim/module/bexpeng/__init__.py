# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bonsai contributors
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

import json
import re

import bpy

import bonsai.tool as tool
from . import operator, prop

classes = (
    prop.BIMBexpengProperties,
    operator.BIM_OT_bexpeng_attach_param,
    operator.BIM_OT_bexpeng_detach_param,
    operator.BIM_OT_bexpeng_bulk_apply_param,
)

_observers: dict[str, tuple[str, object]] = {}


def is_integration_active() -> bool:
    """Return True when the user preference toggle is on and bexpeng is loaded."""
    import bonsai.tool as tool

    prefs = tool.Blender.get_addon_preferences()
    return prefs.use_bexpeng_integration and "bexpeng" in bpy.context.preferences.addons


def get_binding(binding_key: str) -> str:
    """Return the current BExpEng parameter name bound to *binding_key*, or ``""``."""
    try:
        props = bpy.context.scene.BIMBexpengProperties
        bindings = json.loads(props.bindings_json or "{}")
        entry = bindings.get(binding_key, "")
        if not isinstance(entry, dict):
            return ""
        param_id = entry.get("param_id", "")
        if not param_id:
            return ""
        from bexpeng.engine import ParametricEngine

        return ParametricEngine.get_instance().get_name(param_id) or ""
    except Exception:
        return ""


def set_binding(
    binding_key: str,
    param_id: str,
    data_type: str,
    commit: dict | None = None,
    objects: list[str] | None = None,
) -> None:
    """Persist a binding entry in the scene's bindings_json property."""
    try:
        props = bpy.context.scene.BIMBexpengProperties
        bindings = json.loads(props.bindings_json or "{}")
    except (json.JSONDecodeError, AttributeError):
        bindings = {}
    entry: dict = {"param_id": param_id, "type": data_type}
    if commit:
        entry["commit"] = commit
    if objects:
        entry["objects"] = objects
    bindings[binding_key] = entry
    bpy.context.scene.BIMBexpengProperties.bindings_json = json.dumps(bindings)


def _detect_commit(binding_key: str, context) -> dict | None:
    """Return the Bonsai commit operator dict for binding_key, or None."""
    m = re.search(
        r"bpy\.data\.objects\['([^']+)'\]\.BIMObjectMaterialProperties\.material_set_item_attributes",
        binding_key,
    )
    if m:
        obj_name = m.group(1)
        obj = bpy.data.objects.get(obj_name)
        if obj:
            item_id = obj.BIMObjectMaterialProperties.active_material_set_item_id
            if item_id:
                return {"op": "bim.edit_material_set_item", "kwargs": {"obj": obj_name, "material_set_item": item_id}}

    m = re.search(
        r"bpy\.data\.objects\['([^']+)'\]\.BIMObjectMaterialProperties\.material_set_item_profile_attributes",
        binding_key,
    )
    if m:
        obj_name = m.group(1)
        obj = bpy.data.objects.get(obj_name)
        if obj:
            item_id = obj.BIMObjectMaterialProperties.active_material_set_item_id
            if item_id:
                return {
                    "op": "bim.edit_material_set_item_profile",
                    "kwargs": {"obj": obj_name, "material_set_item": item_id},
                }

    m = re.search(
        r"bpy\.data\.objects\['([^']+)'\]\.BIMAttributeProperties\.attributes",
        binding_key,
    )
    if m:
        obj_name = m.group(1)
        return {"op": "bim.edit_attributes", "kwargs": {"_obj": obj_name}}

    m = re.search(r"bpy\.data\.objects\['([^']+)'\]\.location\[(\d+)\]", binding_key)
    if m:
        obj_name = m.group(1)
        return {"op": "bim.edit_object_placement", "kwargs": {"obj": obj_name}}

    if re.search(r"BIMModelProperties\.extrusion_depth(?:::|$)", binding_key):
        return {"op": "bim.change_extrusion_depth", "kwargs": {"depth": "_value"}}

    if re.search(r"BIMModelProperties\.length(?:::|$)", binding_key):
        return {"op": "bim.change_layer_length", "kwargs": {"length": "_value"}}

    m = re.search(r"bpy\.data\.objects\['([^']+)'\]\.BIMWindowProperties\.", binding_key)
    if m:
        obj_name = m.group(1)
        return {"op": "bim.apply_window_bexpeng", "kwargs": {"_obj": obj_name}}

    m = re.search(r"bpy\.data\.objects\['([^']+)'\]\.BIMDoorProperties\.", binding_key)
    if m:
        obj_name = m.group(1)
        return {"op": "bim.apply_door_bexpeng", "kwargs": {"_obj": obj_name}}

    return None


def _run_commit(commit: dict, value: object = None, objects: list[str] | None = None) -> None:
    """Execute the Bonsai commit operator, temporarily restoring bind-time selection if needed."""
    op_idname = commit.get("op", "")
    if not op_idname:
        return
    kwargs = dict(commit.get("kwargs", {}))
    if value is not None:
        kwargs = {k: (value if v == "_value" else v) for k, v in kwargs.items()}
    obj_override = kwargs.pop("_obj", None)
    module, _, func = op_idname.partition(".")
    op_func = getattr(getattr(bpy.ops, module), func)

    prev_selected = None
    prev_active = None

    if objects:
        prev_selected = [o for o in bpy.context.view_layer.objects if o.select_get()]
        prev_active = bpy.context.view_layer.objects.active
        for o in prev_selected:
            o.select_set(False)
        for name in objects:
            o = bpy.data.objects.get(name)
            if o:
                o.select_set(True)
        first = next((bpy.data.objects.get(n) for n in objects if bpy.data.objects.get(n)), None)
        if first:
            bpy.context.view_layer.objects.active = first

    try:
        poll_result = op_func.poll()
        if not poll_result:
            return
        if obj_override:
            save_active = bpy.context.view_layer.objects.active
            o = bpy.data.objects.get(obj_override)
            if o:
                bpy.context.view_layer.objects.active = o
            op_func(**kwargs)
            bpy.context.view_layer.objects.active = save_active
        else:
            op_func(**kwargs)

        # After moving a fill element (window/door), recalculate the opening hole.
        fill_target = obj_override or (kwargs.get("obj") if op_idname == "bim.edit_object_placement" else None)
        if op_idname == "bim.edit_object_placement" and fill_target:
            try:
                fill_obj = bpy.data.objects.get(fill_target)
                if fill_obj:
                    element = tool.Ifc.get_entity(fill_obj)
                    fills_voids = getattr(element, "FillsVoids", None)
                    if element and fills_voids:
                        with bpy.context.temp_override(selected_objects=[fill_obj]):
                            bpy.ops.bim.recalculate_fill()
            except Exception:
                pass
    finally:
        if prev_selected is not None:
            for o in bpy.context.view_layer.objects:
                o.select_set(False)
            for o in prev_selected:
                o.select_set(True)
            bpy.context.view_layer.objects.active = prev_active


def clear_binding(binding_key: str) -> None:
    """Remove the binding for *binding_key* and detach from the engine."""
    _detach(binding_key)
    try:
        props = bpy.context.scene.BIMBexpengProperties
        bindings: dict[str, str] = json.loads(props.bindings_json or "{}")
    except (json.JSONDecodeError, AttributeError):
        bindings = {}
    bindings.pop(binding_key, None)
    bpy.context.scene.BIMBexpengProperties.bindings_json = json.dumps(bindings)


def _write_engine_value(
    binding_key: str,
    data_type: str,
    param_id: str,
    commit: dict | None = None,
    objects: list[str] | None = None,
) -> None:
    """Write the current engine value for param_id to the Blender property at binding_key."""
    from bexpeng.engine import ParametricEngine

    engine = ParametricEngine.get_instance()
    value = engine.get_value_by_id(param_id)
    if value is None:
        return
    prop_path = binding_key.split("::")[0]
    props_path, _, prop_name = prop_path.rpartition(".")
    if not props_path:
        return
    if data_type == "integer":
        coerced: object = int(round(float(value)))
    elif data_type == "float":
        coerced = float(value)
    elif data_type == "boolean":
        coerced = bool(value)
    else:
        coerced = str(value)
    try:
        owner = eval(props_path)  # nosec
    except (KeyError, IndexError):
        return
    _idx_match = re.match(r"^(\w+)\[(\d+)\]$", prop_name)
    if _idx_match:
        getattr(owner, _idx_match.group(1))[int(_idx_match.group(2))] = coerced
    else:
        setattr(owner, prop_name, coerced)
    if commit:
        _run_commit(commit, value=coerced, objects=objects)


def _attach(
    binding_key: str,
    data_type: str,
    param_id: str,
    commit: dict | None = None,
    objects: list[str] | None = None,
) -> None:
    """Attach a callback to the engine for param_id, wiring value changes to binding_key."""
    _detach(binding_key)
    if not param_id:
        return
    try:
        from bexpeng.engine import ParametricEngine

        engine = ParametricEngine.get_instance()

        def _callback(_name: str) -> None:
            try:
                _write_engine_value(binding_key, data_type, param_id, commit, objects)
            except Exception:
                import traceback

                traceback.print_exc()

        _observers[binding_key] = (param_id, _callback)
        engine.attach(param_id, _callback)
    except (ImportError, AttributeError):
        pass


def _attach_and_apply(
    binding_key: str,
    data_type: str,
    param_id: str,
    commit: dict | None = None,
    apply_commit: bool = True,
    objects: list[str] | None = None,
) -> None:
    """Attach to the engine for param_id and immediately write the current value to binding_key."""
    _attach(binding_key, data_type, param_id, commit, objects)
    _write_engine_value(binding_key, data_type, param_id, commit if apply_commit else None, objects)


def _write_window_bindings(obj: "bpy.types.Object") -> None:
    """Write current engine values for all bindings targeting obj.BIMWindowProperties."""
    _write_prop_bindings(obj, "BIMWindowProperties")


def _write_door_bindings(obj: "bpy.types.Object") -> None:
    """Write current engine values for all bindings targeting obj.BIMDoorProperties."""
    _write_prop_bindings(obj, "BIMDoorProperties")


def _write_prop_bindings(obj: "bpy.types.Object", prop_group_name: str) -> None:
    """Write current engine values for all bindings targeting obj.<prop_group_name>.*, without commit."""
    try:
        props = bpy.context.scene.BIMBexpengProperties
        bindings = json.loads(props.bindings_json or "{}")
    except (json.JSONDecodeError, AttributeError):
        return
    prefix = f"bpy.data.objects['{obj.name}'].{prop_group_name}."
    for binding_key, entry in bindings.items():
        base_key = binding_key.split("::")[0]
        if not base_key.startswith(prefix):
            continue
        if not isinstance(entry, dict):
            continue
        param_id = entry.get("param_id", "")
        data_type = entry.get("type", "float")
        if param_id:
            _write_engine_value(binding_key, data_type, param_id)


def _detach(binding_key: str) -> None:
    entry = _observers.pop(binding_key, None)
    if entry is None:
        return
    try:
        from bexpeng.engine import ParametricEngine

        engine = ParametricEngine.get_instance()
        engine.detach(entry[0], entry[1])
    except (ImportError, AttributeError):
        pass


def draw_bexpeng_buttons(
    layout: bpy.types.UILayout,
    binding_key: str,
    data_type: str,
    param_name: str,
    show_bulk: bool = True,
) -> None:
    """Draw bind/detach buttons for binding_key on layout."""
    if param_name:
        alert = layout.row(align=True)
        alert.alert = True
        op = alert.operator("bim.bexpeng_attach_param", text="", icon="CON_TRANSFORM_CACHE")
        op.binding_key = binding_key
        op.data_type = data_type
        op.show_bulk = show_bulk
    else:
        op = layout.operator("bim.bexpeng_attach_param", text="", icon="CON_TRANSFORM_CACHE")
        op.binding_key = binding_key
        op.data_type = data_type
        op.show_bulk = show_bulk


def _attach_all() -> None:
    """Attach all saved bindings to the engine (called after engine load, which wipes per-parameter callbacks)."""
    _observers.clear()
    for scene in bpy.data.scenes:
        try:
            props = scene.BIMBexpengProperties
            bindings = json.loads(props.bindings_json or "{}")
        except (json.JSONDecodeError, AttributeError):
            continue
        for binding_key, entry in bindings.items():
            if not isinstance(entry, dict):
                continue
            param_id = entry.get("param_id", "")
            if not param_id:
                continue
            data_type = entry.get("type", "float")
            commit = entry.get("commit") or None
            objects = entry.get("objects") or None
            _attach_and_apply(binding_key, data_type, param_id, commit, apply_commit=False, objects=objects)


def register() -> None:
    bpy.types.Scene.BIMBexpengProperties = bpy.props.PointerProperty(type=prop.BIMBexpengProperties)
    try:
        from bexpeng.engine import ParametricEngine

        ParametricEngine.get_instance().attach_post_load(_attach_all)
    except Exception:
        pass


def unregister() -> None:
    try:
        from bexpeng.engine import ParametricEngine

        ParametricEngine.get_instance().detach_post_load(_attach_all)
    except Exception:
        pass
    del bpy.types.Scene.BIMBexpengProperties
