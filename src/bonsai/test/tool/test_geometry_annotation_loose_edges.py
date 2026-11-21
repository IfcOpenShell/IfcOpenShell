# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import pytest

from test.bim.bootstrap import NewFile


class TestAddAnnotationRepresentation(NewFile):
    @pytest.mark.parametrize("schema", ["IFC4", "IFC2X3"])
    def test_loose_edges_are_kept_next_to_faces(self, schema):
        ifc = ifcopenshell.file(schema=schema)
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        plan = ifcopenshell.api.context.add_context(ifc, context_type="Plan")
        context = ifcopenshell.api.context.add_context(
            ifc, context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan
        )
        mesh = bpy.data.meshes.new("Mesh")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (2, 0, 0), (3, 0, 0)], [(4, 5)], [(0, 1, 2, 3)])
        obj = bpy.data.objects.new("Mesh", mesh)
        bpy.context.scene.collection.objects.link(obj)
        representation = ifcopenshell.api.geometry.add_representation(
            ifc, context=context, blender_object=obj, geometry=mesh
        )
        assert sorted(i.is_a() for i in representation.Items) == ["IfcAnnotationFillArea", "IfcGeometricCurveSet"]
        curve_set = next(i for i in representation.Items if i.is_a("IfcGeometricCurveSet"))
        assert len(curve_set.Elements) == 1
