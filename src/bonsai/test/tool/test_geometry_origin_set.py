# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.root
from ifcopenshell.util.shape_builder import ShapeBuilder, V

import bonsai.tool as tool
from bonsai.bim.module.geometry.operator import OverrideOriginSet
from test.bim.bootstrap import NewFile


class TestCanRegenerateSweptSolid(NewFile):
    def create_element_with_extrusion(self):
        tool.Ifc.set(ifc := ifcopenshell.file(schema="IFC4"))
        element = ifcopenshell.api.root.create_entity(ifc, "IfcBuildingElementProxy")
        builder = ShapeBuilder(ifc)
        context = ifc.createIfcGeometricRepresentationContext(None, "Model")
        extrusion = builder.extrude(builder.rectangle(size=V(1, 1)), 1.0)
        return ifc, element, builder.get_representation(context, [extrusion])

    def test_a_single_simple_extrusion_can_be_regenerated(self):
        _, element, representation = self.create_element_with_extrusion()
        assert OverrideOriginSet.can_regenerate_swept_solid(element, representation)

    def test_a_parametric_material_profile_set_cannot_be_regenerated(self):
        ifc, element, representation = self.create_element_with_extrusion()
        profile_set = ifcopenshell.api.material.add_material_set(ifc, name="Profiles", set_type="IfcMaterialProfileSet")
        ifcopenshell.api.material.assign_material(ifc, products=[element], material=profile_set)
        assert not OverrideOriginSet.can_regenerate_swept_solid(element, representation)
