# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.guid

import bonsai.tool as tool
from bonsai.bim.module.boundary.data import SpaceBoundariesData
from test.bim.bootstrap import NewFile


class TestBoundaries(NewFile):
    def add_space(self, ifc):
        space = ifc.createIfcSpace()
        obj = bpy.data.objects.new("Space", None)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        tool.Ifc.link(space, obj)
        return space

    def test_a_virtual_boundary_without_a_related_element(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        space = self.add_space(ifc)
        boundary = ifc.createIfcRelSpaceBoundary(
            ifcopenshell.guid.new(), RelatingSpace=space, PhysicalOrVirtualBoundary="VIRTUAL"
        )
        assert SpaceBoundariesData.boundaries() == [{"id": boundary.id(), "description": f"{boundary.id()} > Virtual"}]

    def test_a_physical_boundary_with_a_related_element(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        space = self.add_space(ifc)
        wall = ifc.createIfcWall(ifcopenshell.guid.new(), Name="Wall")
        boundary = ifc.createIfcRelSpaceBoundary(
            ifcopenshell.guid.new(),
            RelatingSpace=space,
            RelatedBuildingElement=wall,
            PhysicalOrVirtualBoundary="PHYSICAL",
        )
        assert SpaceBoundariesData.boundaries() == [
            {"id": boundary.id(), "description": f"{boundary.id()} > IfcWall/Wall"}
        ]
