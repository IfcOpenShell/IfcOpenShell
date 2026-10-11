# This file was generated with the assistance of an AI coding tool.

from types import SimpleNamespace
from unittest.mock import patch

import bpy

import bonsai.bim.module.bcf.bcfstore as bcfstore
import bonsai.tool as tool
from test.bim.bootstrap import NewFile


def write_snapshot(write_still=True):
    with open(bpy.context.scene.render.filepath, "wb") as f:
        f.write(b"png")


class TestAddBcfViewpoint(NewFile):
    def test_camera_is_stored_in_global_coordinates_on_a_georeferenced_model(self):
        bpy.ops.bim.create_project()
        geo_props = tool.Georeference.get_georeference_props()
        geo_props.has_blender_offset = True
        geo_props.blender_offset_x = "1000"
        geo_props.blender_offset_y = "2000"
        geo_props.blender_offset_z = "3000"
        geo_props.blender_x_axis_abscissa = "1"
        geo_props.blender_x_axis_ordinate = "0"
        bpy.ops.bim.new_bcf_project()
        tool.Bcf.get_bcf_props().author = "test@example.org"
        bpy.ops.bim.add_bcf_topic()
        bpy.ops.object.camera_add(location=(1, 2, 3))
        bpy.context.scene.camera = bpy.context.active_object
        with patch.object(bpy.ops, "render", SimpleNamespace(opengl=write_snapshot), create=True):
            bpy.ops.bim.add_bcf_viewpoint()
        topic = next(iter(bcfstore.BcfStore.get_bcfxml().topics.values()))
        camera = next(iter(topic.viewpoints.values())).visualization_info.perspective_camera
        point = camera.camera_view_point
        assert (point.x, point.y, point.z) == (1001, 2002, 3003)
