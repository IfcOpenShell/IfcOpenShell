# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.root
from ifcopenshell.util.shape_builder import ShapeBuilder

import bonsai.tool as tool
from bonsai.tool.model import Model as subject
from test.bim.bootstrap import NewFile


class TestRemapManualBooleans(NewFile):
    def test_a_copied_element_tracks_its_own_manual_booleans(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        element = ifc.createIfcWall()
        items = [ifc.createIfcExtrudedAreaSolid()]
        representation = ifc.createIfcShapeRepresentation(Items=items, ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)
        builder = ShapeBuilder(ifc)
        cut = builder.half_space_solid(builder.plane())
        bools = ifcopenshell.api.geometry.add_boolean(ifc, first_item=items[0], second_items=[cut])
        subject.mark_manual_booleans(element, bools)

        copy = ifcopenshell.api.root.copy_class(ifc, product=element)
        tool.Root.copy_representation(element, copy)

        copied = subject.get_manual_booleans(copy, copy.Representation.Representations[0])
        assert len(copied) == 1
        assert copied[0] not in bools
