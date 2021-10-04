import bpy
import ifcopenshell
import ifcopenshell.api
import blenderbim.tool as tool
import test.bim.bootstrap
import blenderbim.core.tool.surveyor
import numpy as np
from blenderbim.tool import Surveyor as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.surveyor.Surveyor)


class TestGetGlobalMatrix(test.bim.bootstrap.NewFile):
    def test_getting_an_absolute_matrix_if_no_blender_offset(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = False
        obj = bpy.data.objects.new("Object", None)
        assert (subject.get_absolute_matrix(obj) == np.array(obj.matrix_world)).all()

    def test_applying_an_object_placement_blender_offset(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[unit])
        tool.Ifc.set(ifc)
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_eastings = "1000"
        props.blender_northings = "2000"
        props.blender_orthogonal_height = "3000"
        props.blender_x_axis_abscissa = "0"
        props.blender_x_axis_ordinate = "1"
        obj = bpy.data.objects.new("Object", None)
        obj.BIMObjectProperties.blender_offset_type = "OBJECT_PLACEMENT"
        matrix = ifcopenshell.util.geolocation.local2global(np.array(obj.matrix_world), 1.0, 2.0, 3.0, 0.0, 1.0)
        assert (subject.get_absolute_matrix(obj) == matrix).all()
