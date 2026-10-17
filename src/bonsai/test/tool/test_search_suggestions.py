# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.search.operator import FilterValueSuggestions
from test.bim.bootstrap import NewFile


class TestGetPropertyValues(NewFile):
    def test_booleans_are_suggested_as_query_keywords(self):
        tool.Ifc.set(ifc := ifcopenshell.file(schema="IFC4"))
        wall = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        tool.Ifc.link(wall, bpy.data.objects.new("Wall", None))
        pset = ifcopenshell.api.pset.add_pset(ifc, product=wall, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"IsExternal": True, "LoadBearing": False})
        suggestions = FilterValueSuggestions.get_property_values
        assert suggestions(FilterValueSuggestions, ifc, "Pset_WallCommon", "IsExternal") == {"TRUE"}
        assert suggestions(FilterValueSuggestions, ifc, "Pset_WallCommon", "LoadBearing") == {"FALSE"}
