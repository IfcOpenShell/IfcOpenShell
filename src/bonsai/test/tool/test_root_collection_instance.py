# This file was generated with the assistance of an AI coding tool.

import bpy

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAssignClass(NewFile):
    def test_a_collection_instance_warns_that_it_has_no_representation(self, capfd):
        bpy.ops.bim.create_project()
        collection = bpy.data.collections.new("CubeAsset")
        bpy.ops.object.collection_instance_add(collection=collection.name)
        props = tool.Root.get_root_props()
        props.ifc_product = "IfcElement"
        props.ifc_class = "IfcFurniture"
        bpy.ops.bim.assign_class()
        assert "is a collection instance" in capfd.readouterr().out
