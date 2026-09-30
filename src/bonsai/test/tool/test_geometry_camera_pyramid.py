# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAddCameraRepresentation(NewFile):
    @pytest.mark.parametrize("depth", [3.0, 1.5])
    def test_perspective_pyramid_base_ignores_depth(self, depth):
        ifc = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        context = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        camera = bpy.data.cameras.new("Camera")
        camera.type = "PERSP"
        camera.clip_end = depth
        props = tool.Drawing.get_camera_props(camera)
        props["width"] = 4.0
        props["height"] = 2.0
        obj = bpy.data.objects.new("Camera", camera)
        bpy.context.scene.collection.objects.link(obj)
        representation = ifcopenshell.api.geometry.add_representation(
            ifc, context=context, blender_object=obj, geometry=camera
        )
        pyramid = next(e for e in ifc.traverse(representation) if e.is_a("IfcRectangularPyramid"))
        assert pyramid.XLength == pytest.approx(4.0)
        assert pyramid.YLength == pytest.approx(2.0)
        assert pyramid.Height == pytest.approx(depth)
