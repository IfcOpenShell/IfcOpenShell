# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import math
import ifcopenshell
import ifcopenshell.api
import bonsai.core.tool
import bonsai.tool as tool
from mathutils import Vector
from test.bim.bootstrap import NewFile
from bonsai.tool.georeference import Georeference as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Georeference)


class TestImportProjectedCRS(NewFile):
    def test_importing_nothing_with_no_georeferencing(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        subject.import_projected_crs()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert len(props.projected_crs) == 0

    def test_importing_projected_crs(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        projected_crs = ifc.by_type("IfcProjectedCRS")[0]
        projected_crs.Name = "Name"
        projected_crs.Description = "Description"
        projected_crs.GeodeticDatum = "GeodeticDatum"
        projected_crs.VerticalDatum = "VerticalDatum"
        projected_crs.MapProjection = "MapProjection"
        projected_crs.MapZone = "MapZone"
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT")
        projected_crs.MapUnit = unit
        subject.import_projected_crs()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert props.projected_crs.get("Name").string_value == "Name"
        assert props.projected_crs.get("Description").string_value == "Description"
        assert props.projected_crs.get("GeodeticDatum").string_value == "GeodeticDatum"
        assert props.projected_crs.get("VerticalDatum").string_value == "VerticalDatum"
        assert props.projected_crs.get("MapProjection").string_value == "MapProjection"
        assert props.projected_crs.get("MapZone").string_value == "MapZone"
        assert props.projected_crs.get("MapUnit").enum_value == str(unit.id())

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        subject.import_projected_crs()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert len(props.projected_crs) == 0


class TestImportCoordinateOperation(NewFile):
    def test_importing_nothing_with_no_georeferencing(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        subject.import_coordinate_operation()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert len(props.coordinate_operation) == 0

    def test_importing_coordinate_operation(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Eastings = 1
        map_conversion.Northings = 2
        map_conversion.OrthogonalHeight = 3
        map_conversion.XAxisAbscissa = 4
        map_conversion.XAxisOrdinate = 5
        map_conversion.Scale = 6
        subject.import_coordinate_operation()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert props.coordinate_operation.get("Eastings").string_value == "1.0"
        assert props.coordinate_operation.get("Northings").string_value == "2.0"
        assert props.coordinate_operation.get("OrthogonalHeight").string_value == "3.0"
        assert props.x_axis_abscissa == "4.0"
        assert props.x_axis_ordinate == "5.0"
        assert props.grid_north_angle == "-51.3401917"
        assert props.coordinate_operation.get("Scale").string_value == "6.0"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        subject.import_coordinate_operation()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert len(props.coordinate_operation) == 0


class TestImportTrueNorth(NewFile):
    def test_detecting_no_true_north(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        subject.import_true_north()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert props.true_north_abscissa == "0"
        assert props.true_north_ordinate == "1"
        assert props.true_north_angle == "0"

    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        context = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        context.TrueNorth = ifc.createIfcDirection((1.0, 2.0, 0.0))
        subject.import_true_north()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert props.true_north_abscissa == "1.0"
        assert props.true_north_ordinate == "2.0"
        assert props.true_north_angle == "-26.5650512"


class TestExportProjectedCRS(NewFile):
    def test_run(self):
        TestImportProjectedCRS().test_importing_projected_crs()
        assert subject.export_projected_crs() == {
            "Name": "Name",
            "Description": "Description",
            "GeodeticDatum": "GeodeticDatum",
            "VerticalDatum": "VerticalDatum",
            "MapProjection": "MapProjection",
            "MapZone": "MapZone",
            "MapUnit": tool.Ifc.get().by_type("IfcNamedUnit")[0],
        }


class TestExportCoordinateOperation(NewFile):
    def test_run(self):
        TestImportCoordinateOperation().test_importing_coordinate_operation()
        assert subject.export_coordinate_operation() == {
            "Eastings": 1.0,
            "Northings": 2.0,
            "OrthogonalHeight": 3.0,
            "XAxisAbscissa": 4.0,
            "XAxisOrdinate": 5.0,
            "Scale": 6.0,
        }


class TestGetTrueNorthAttributes(NewFile):
    def test_run(self):
        TestImportTrueNorth().test_run()
        assert subject.get_true_north_attributes() == [1.0, 2.0]


class TestEnableEditing(NewFile):
    def test_run(self):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = False
        subject.enable_editing()
        assert bpy.context.scene.BIMGeoreferenceProperties.is_editing is True


class TestDisableEditing(NewFile):
    def test_run(self):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = True
        subject.disable_editing()
        assert bpy.context.scene.BIMGeoreferenceProperties.is_editing is False


class TestSetCoordinates(NewFile):
    def test_run(self):
        subject.set_coordinates("local", [1.0, 2.0, 3.0])
        assert bpy.context.scene.BIMGeoreferenceProperties.local_coordinates == "1.0,2.0,3.0"
        subject.set_coordinates("blender", [4.0, 5.0, 6.0])
        assert bpy.context.scene.BIMGeoreferenceProperties.blender_coordinates == "4.0,5.0,6.0"
        subject.set_coordinates("map", [7.0, 8.0, 9.0])
        assert bpy.context.scene.BIMGeoreferenceProperties.map_coordinates == "7.0,8.0,9.0"


class TestGetCoordinates(NewFile):
    def test_run(self):
        bpy.context.scene.BIMGeoreferenceProperties.local_coordinates = "1.0,2.0,3.0"
        assert subject.get_coordinates("local") == [1.0, 2.0, 3.0]
        bpy.context.scene.BIMGeoreferenceProperties.blender_coordinates = "4.0,5.0,6.0"
        assert subject.get_coordinates("blender") == [4.0, 5.0, 6.0]
        bpy.context.scene.BIMGeoreferenceProperties.map_coordinates = "7.0,8.0,9.0"
        assert subject.get_coordinates("map") == [7.0, 8.0, 9.0]


class TestGetCursorLocation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[unit])
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.get_cursor_location() == [1000.0, 2000.0, 3000.0]


class TestXyz2Enh(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        tool.Ifc.set(ifc)
        assert subject.xyz2enh([0.0, 0.0, 0.0]) == (0.0, 0.0, 0.0)

    def test_using_the_blender_offset(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        tool.Ifc.set(ifc)
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_offset_x = "1.0"
        assert subject.xyz2enh([0.0, 0.0, 0.0]) == (1.0, 0.0, 0.0)

    def test_using_the_map_conversion(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Eastings = 1.0
        assert subject.xyz2enh([0.0, 0.0, 0.0]) == (1.0, 0.0, 0.0)

    def test_applying_both_blender_offset_and_map_conversion(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_offset_x = "1.0"
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Northings = 1.0
        assert subject.xyz2enh([0.0, 0.0, 0.0]) == (1.0, 1.0, 0.0)


class TestEnh2Xyz(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        tool.Ifc.set(ifc)
        assert subject.enh2xyz([0.0, 0.0, 0.0]) == (0.0, 0.0, 0.0)

    def test_using_the_blender_offset(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        tool.Ifc.set(ifc)
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_offset_x = "1.0"
        assert subject.enh2xyz([0.0, 0.0, 0.0]) == (-1.0, 0.0, 0.0)

    def test_using_the_map_conversion(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Eastings = 1.0
        assert subject.enh2xyz([0.0, 0.0, 0.0]) == (-1.0, 0.0, 0.0)

    def test_applying_both_blender_offset_and_map_conversion(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_offset_x = "1.0"
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Northings = 1.0
        assert subject.enh2xyz([0.0, 0.0, 0.0]) == (-1.0, -1.0, 0.0)
