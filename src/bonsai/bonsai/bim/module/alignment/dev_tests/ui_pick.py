# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""UI mode with --enable-event-simulate: click a few pixels off a PI marker; it should become active.
A click far from any marker must fall through to Blender's own select (deselects)."""

import os
import traceback

import bpy

RESULT = os.path.join(os.environ.get("TEMP", "."), "align_ui_pick_result.txt")
open(RESULT, "w").close()


def log(msg):
    with open(RESULT, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


state = {"step": 0}


def area_region():
    window = bpy.context.window_manager.windows[0]
    area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    return window, area, region


def setup():
    if os.environ.get("PICK_CONTROL"):
        for km in bpy.context.window_manager.keyconfigs.addon.keymaps:
            for kmi in km.keymap_items:
                if kmi.idname == "align.pick_pi_marker":
                    kmi.active = False
    import bonsai.tool as tool
    import ifcopenshell.api.alignment

    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    a = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "Main", [(0.0, 0.0), (400.0, 0.0), (800.0, 300.0)], [100.0],
        [(0.0, 10.0), (300.0, 12.0), (800.0, 10.0)], [0.0],
    )
    tool.Alignment.create_object_for_alignment(a)
    tool.Alignment.refresh_alignment_representation_object(a)
    bpy.ops.mesh.primitive_plane_add(size=600.0, location=(400.0, 150.0, -1.0))
    obj = tool.Ifc.get_object(a)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.align.edit_horizontal_pis()
    window, area, region = area_region()
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.view3d.view_axis(type="TOP")
        bpy.ops.view3d.view_all()
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = None


def click(window, region, x, y):
    gx, gy = region.x + int(x), region.y + int(y)
    window.event_simulate(type="MOUSEMOVE", value="NOTHING", x=gx, y=gy)
    window.event_simulate(type="LEFTMOUSE", value="PRESS", x=gx, y=gy)
    window.event_simulate(type="LEFTMOUSE", value="RELEASE", x=gx, y=gy)


def run():
    try:
        from bpy_extras.view3d_utils import location_3d_to_region_2d

        step = state["step"]
        state["step"] += 1
        window, area, region = area_region()
        rv3d = area.spaces.active.region_3d
        markers = [o for o in bpy.data.objects if o.bonsai_pi_curve_marker.is_pi_marker]
        if step == 0:
            setup()
            return 1.0
        if step == 1:
            log(f"markers: {[m.name for m in markers]}; tool={bpy.context.workspace.tools.from_space_view3d_mode('OBJECT').idname}")
            pi = next(m for m in markers if m.name.startswith("PI"))
            px = location_3d_to_region_2d(region, rv3d, pi.matrix_world.translation)
            log(f"target {pi.name} at {tuple(px)}")
            click(window, region, px[0] + 8, px[1] - 6)
            return 1.0
        if step == 2:
            active = bpy.context.view_layer.objects.active
            log(f"after near click: active={active.name if active else None}")
            click(window, region, region.width * 0.5, region.height * 0.08)
            return 1.0
        if step == 3:
            active = bpy.context.view_layer.objects.active
            log(f"after far click: selected={[o.name for o in bpy.context.selected_objects]}")
            bpy.ops.wm.quit_blender()
            return None
    except Exception:
        log("EXCEPTION\n" + traceback.format_exc())
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(run, first_interval=2.0)
