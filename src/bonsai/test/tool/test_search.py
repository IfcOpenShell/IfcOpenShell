# This file was generated with the assistance of an AI coding tool.

import bpy

import bonsai.bim.module.search.data
import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestSaveAndLoadCsvSearch(NewFile):
    def test_csv_attributes_round_trip(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_filter(index=0, type="entity", module="csv")
        tool.Search.get_filter_groups("csv")[0].filters[0].value = "IfcWall"
        csv_props = tool.Blender.get_csv_props()
        csv_props.csv_attributes.clear()
        attribute = csv_props.csv_attributes.add()
        attribute.name = "Name"
        attribute.header = "Wall Name"
        attribute.sort = "ASC"

        bpy.ops.bim.save_search(name="Walls", module="csv")
        csv_props.csv_attributes.clear()
        bonsai.bim.module.search.data.refresh()
        group = tool.Ifc.get().by_type("IfcGroup")[0]
        tool.Search.get_search_props().saved_searches = str(group.id())
        bpy.ops.bim.load_search(module="csv")

        assert [(a.name, a.header, a.sort) for a in csv_props.csv_attributes] == [("Name", "Wall Name", "ASC")]
