# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

from test.bim.bootstrap import NewIfc


class TestGetConnectedSystemElements(NewIfc):
    def test_reporting_an_error_when_the_active_object_is_not_an_ifc_element(self):
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        with pytest.raises(RuntimeError, match="Active object is not an IFC element"):
            bpy.ops.bim.get_connected_system_elements()
