# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys, traceback, bpy
import bonsai.bim.handler, bonsai.tool as tool, ifcopenshell.api.alignment

def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    from bonsai.bim.module.alignment.prop import _alignment_enum_items
    props = bpy.context.scene.CivilAlignmentProperties
    made = []
    for name in ("A", "B"):
        a = ifcopenshell.api.alignment.create_by_pi_method(ifc, name, [(0.0, 0.0), (100.0, 0.0)], [], [], [])
        tool.Alignment.create_object_for_alignment(a)
        tool.Alignment.refresh_alignment_representation_object(a)
        made.append(a)
    # select B through the dropdown's own index convention (what the handlers do)
    items = _alignment_enum_items(props, bpy.context)
    idx = [i for i, it in enumerate(items) if it[0] == str(made[1].id())][0]
    props["active_alignment_id_str"] = idx
    print("before delete:", props.active_alignment_id_str, "index", props.get("active_alignment_id_str"))
    select(tool.Ifc.get_object(made[1]))
    print("remove:", bpy.ops.align.remove_alignment())
    print("stored index after delete:", props.get("active_alignment_id_str"), "items now:", len(_alignment_enum_items(props, bpy.context)))
    print("value after delete:", repr(props.active_alignment_id_str))
    from bonsai.bim.module.alignment.prop import _clamp_alignment_enum
    props["active_alignment_id_str"] = 7  # stale, e.g. after an undo removed alignments
    _clamp_alignment_enum(props, bpy.context)
    print("stale index clamped to:", props.get("active_alignment_id_str"), repr(props.active_alignment_id_str))
    assert props.get("active_alignment_id_str") == 0
    props["active_alignment_id_str"] = 1  # a valid one is left alone
    _clamp_alignment_enum(props, bpy.context)
    assert props.get("active_alignment_id_str") == 1
    print("ENUM_REPRO_DONE")
except Exception:
    traceback.print_exc()
sys.stdout.flush()
