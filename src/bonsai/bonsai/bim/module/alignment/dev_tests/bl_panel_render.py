# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool


class Rec:
    """Records what a panel's draw() puts on screen: labels, operators, props."""

    def __init__(self, out, depth=0):
        self.out, self.depth = out, depth

    def _child(self, *a, **k):
        return Rec(self.out, self.depth + 1)

    row = column = box = split = column_flow = grid_flow = _child

    def label(self, text="", icon="NONE", **k):
        self.out.append("  " * self.depth + f"label: {text}")

    def operator(self, idname, text=None, **k):
        self.out.append("  " * self.depth + f"op: {idname} {text!r}")
        return type("OpProps", (), {"__setattr__": lambda s, n, v: None})()

    def prop(self, data, name, text=None, **k):
        self.out.append("  " * self.depth + f"prop: {name}")

    def template_list(self, *a, **k):
        self.out.append("  " * self.depth + f"list: {a[0]}")

    def separator(self, *a, **k):
        pass

    def __setattr__(self, name, value):
        if name in ("out", "depth"):
            object.__setattr__(self, name, value)


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    bpy.ops.align.add_alignment(alignment_name="Survey", definition="POLYLINE", define_stationing=True, start_station="0")
    a = next(x for x in tool.Ifc.get().by_type("IfcAlignment") if x.Name == "Survey")
    tool.Alignment.set_polyline_points(a, [(0.0, 0.0, 5.0), (100.0, 0.0, 5.0), (100.0, 50.0, 15.0)], 3)
    obj = tool.Ifc.get_object(a)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    from bonsai.bim.module.alignment import ui as ui_mod

    def render(panel_cls, title):
        out = []
        panel = type("P", (), {"layout": Rec(out)})()
        for name in ("_draw_polyline", "_draw_horizontal", "_draw_vertical", "_draw_cant", "_segments", "_draw_segment_editor"):
            if hasattr(panel_cls, name):
                setattr(type(panel), name, getattr(panel_cls, name))
        panel_cls.draw(panel, bpy.context)
        print(f"==== {title}")
        print(chr(10).join(out))

    render(ui_mod.ALIGN_PT_alignment_segments, "segments: 3D polyline, listed")
    bpy.ops.align.load_polyline_table()
    render(ui_mod.ALIGN_PT_alignment_segments, "segments: 3D polyline, editing")
    render(ui_mod.ALIGN_PT_alignment_authoring, "authoring: while editing")
    bpy.ops.align.finish_polyline_table()
    b = tool.Alignment.create_bare_alignment("Plan", define_stationing=False)
    tool.Alignment.set_polyline_points(b, [(0.0, 0.0), (30.0, 40.0)], 2)
    o2 = tool.Ifc.get_object(b)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    o2.select_set(True)
    bpy.context.view_layer.objects.active = o2
    out = []
    ui_mod.ALIGN_PT_alignment_segments._draw_polyline(None, Rec(out), bpy.context.scene.CivilAlignmentProperties, b)
    print("==== segments: 2D polyline section")
    print(chr(10).join(out))
    for panel_cls in ():
        out = []
        panel = type("P", (), {"layout": Rec(out)})()
        for name in ("_draw_polyline", "_draw_horizontal", "_draw_vertical", "_draw_cant", "_segments", "_draw_segment_editor"):
            if hasattr(panel_cls, name):
                setattr(type(panel), name, getattr(panel_cls, name))
        try:
            panel_cls.draw(panel, bpy.context)
        except Exception:
            traceback.print_exc()
        print(f"==== {panel_cls.__name__}")
        print("\n".join(out))
    print("RENDER_DONE")
except Exception:
    traceback.print_exc()
sys.stdout.flush()
