# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.util.placement

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAssignClass(NewFile):
    def test_a_plain_empty_keeps_its_placement(self):
        bpy.ops.bim.create_project()
        empty = bpy.data.objects.new("Marker", None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = (3.0, 4.0, 5.0)
        bpy.context.view_layer.objects.active = empty
        props = tool.Root.get_root_props()
        props.ifc_product = "IfcElement"
        props.ifc_class = "IfcBuildingElementProxy"
        bpy.ops.bim.assign_class()
        element = tool.Ifc.get_entity(empty)
        assert element.ObjectPlacement is not None
        assert tuple(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)[:3, 3]) == (3.0, 4.0, 5.0)

    def test_a_collection_instance_warns_that_it_has_no_representation(self, capfd):
        bpy.ops.bim.create_project()
        collection = bpy.data.collections.new("CubeAsset")
        bpy.ops.object.collection_instance_add(collection=collection.name)
        props = tool.Root.get_root_props()
        props.ifc_product = "IfcElement"
        props.ifc_class = "IfcFurniture"
        bpy.ops.bim.assign_class()
        assert "is a collection instance" in capfd.readouterr().out
