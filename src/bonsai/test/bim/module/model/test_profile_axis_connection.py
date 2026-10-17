# This file was generated with the assistance of an AI coding tool.

import bpy

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


def select_only(*objs):
    for obj in bpy.data.objects:
        obj.select_set(False)
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[-1]


class TestEditExtrusionAxis(NewFile):
    def test_moving_the_start_drops_the_start_connection(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.select_library_file(filepath="./bonsai/bim/data/libraries/IFC4 Demo Library.ifc", append_all=True)
        ifc = tool.Ifc.get()
        props = tool.Model.get_model_props()
        props.ifc_class = "IfcBeamType"
        props.relating_type_id = str(next(e for e in ifc.by_type("IfcBeamType") if e.Name == "B1").id())
        bpy.ops.bim.add_occurrence()
        bpy.context.scene.cursor.location = (1, 1, 0)
        bpy.ops.bim.add_occurrence()
        beam = bpy.data.objects["IfcBeam/Beam"]
        other = bpy.data.objects["IfcBeam/Beam.001"]
        select_only(other)
        bpy.ops.bim.hotkey(hotkey="S_R")
        select_only(other, beam)
        bpy.ops.bim.hotkey(hotkey="S_T")
        element = tool.Ifc.get_entity(beam)
        assert element.ConnectedTo or element.ConnectedFrom

        select_only(beam)
        bpy.ops.bim.enable_editing_extrusion_axis()
        bpy.ops.object.mode_set(mode="OBJECT")
        length = (beam.data.vertices[1].co - beam.data.vertices[0].co).length
        beam.data.vertices[0].co.z += 0.5
        bpy.ops.bim.edit_extrusion_axis()

        assert not element.ConnectedTo and not element.ConnectedFrom
        assert abs(beam.dimensions.z - (length - 0.5)) < 1e-4
