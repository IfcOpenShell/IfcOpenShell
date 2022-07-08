# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import math
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from mathutils import Vector
from test.bim.bootstrap import NewFile
from blenderbim.tool.georeference import Georeference as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Georeference)


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
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT", name="METRE")
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


class TestImportMapConversion(NewFile):
    def test_importing_nothing_with_no_georeferencing(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        subject.import_map_conversion()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert len(props.map_conversion) == 0

    def test_importing_map_conversion(self):
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
        subject.import_map_conversion()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert props.map_conversion.get("Eastings").string_value == "1.0"
        assert props.map_conversion.get("Northings").string_value == "2.0"
        assert props.map_conversion.get("OrthogonalHeight").string_value == "3.0"
        assert props.map_conversion.get("XAxisAbscissa").string_value == "4.0"
        assert props.map_conversion.get("XAxisOrdinate").string_value == "5.0"
        assert props.map_conversion.get("Scale").string_value == "6.0"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        subject.import_map_conversion()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert len(props.map_conversion) == 0


class TestImportTrueNorth(NewFile):
    def test_detecting_no_true_north(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        context = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        subject.import_true_north()
        props = bpy.context.scene.BIMGeoreferenceProperties
        assert props.has_true_north is False

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
        assert props.has_true_north is True


class TestGetProjectedCRSAttributes(NewFile):
    def test_run(self):
        TestImportProjectedCRS().test_importing_projected_crs()
        assert subject.get_projected_crs_attributes() == {
            "Name": "Name",
            "Description": "Description",
            "GeodeticDatum": "GeodeticDatum",
            "VerticalDatum": "VerticalDatum",
            "MapProjection": "MapProjection",
            "MapZone": "MapZone",
            "MapUnit": tool.Ifc.get().by_type("IfcNamedUnit")[0],
        }


class TestGetMapConversionAttributes(NewFile):
    def test_run(self):
        TestImportMapConversion().test_importing_map_conversion()
        assert subject.get_map_conversion_attributes() == {
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
        subject.set_coordinates("input", [1.0, 2.0, 3.0])
        assert bpy.context.scene.BIMGeoreferenceProperties.coordinate_input == "1.0,2.0,3.0"
        subject.set_coordinates("output", [4.0, 5.0, 6.0])
        assert bpy.context.scene.BIMGeoreferenceProperties.coordinate_output == "4.0,5.0,6.0"


class TestGetCoordinates(NewFile):
    def test_run(self):
        bpy.context.scene.BIMGeoreferenceProperties.coordinate_input = "1.0,2.0,3.0"
        assert subject.get_coordinates("input") == [1.0, 2.0, 3.0]
        bpy.context.scene.BIMGeoreferenceProperties.coordinate_output = "4.0,5.0,6.0"
        assert subject.get_coordinates("output") == [4.0, 5.0, 6.0]


class TestGetCursorLocation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT", prefix="MILLI", name="METRE")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[unit])
        bpy.context.scene.cursor.location = (1.0, 2.0, 3.0)
        assert subject.get_cursor_location() == [1000.0, 2000.0, 3000.0]


class TestSetCursorLocation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT", prefix="MILLI", name="METRE")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[unit])
        subject.set_cursor_location([1000.0, 2000.0, 3000.0])
        assert list(bpy.context.scene.cursor.location) == [1.0, 2.0, 3.0]


class TestSetIfcTrueNorth(NewFile):
    def test_run(self):
        subject.set_ifc_true_north()
        assert round(float(bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa), 3) == 0.0
        assert round(float(bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate), 3) == 1.0
        bpy.context.scene.sun_pos_properties.north_offset = math.radians(45)
        subject.set_ifc_true_north()
        assert round(float(bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa), 3) == 0.707
        assert round(float(bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate), 3) == 0.707


class TestSetBlenderTrueNorth(NewFile):
    def test_run(self):
        bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa = "0.0"
        bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate = "1.0"
        subject.set_blender_true_north()
        assert bpy.context.scene.sun_pos_properties.north_offset == 0
        bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa = "0.707"
        bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate = "0.707"
        subject.set_blender_true_north()
        assert round(math.degrees(bpy.context.scene.sun_pos_properties.north_offset)) == 45


class TestGetMapConversion(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        assert subject.get_map_conversion().is_a("IfcMapConversion")


class TestXyz2Enh(NewFile):
    def test_run(self):
        assert subject.xyz2enh([0.0, 0.0, 0.0], None) == [0.0, 0.0, 0.0]

    def test_using_the_blender_offset(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_eastings = "1.0"
        assert subject.xyz2enh([0.0, 0.0, 0.0], None) == (1.0, 0.0, 0.0)

    def test_using_the_map_conversion(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Eastings = 1.0
        assert subject.xyz2enh([0.0, 0.0, 0.0], map_conversion) == (1.0, 0.0, 0.0)

    def test_applying_both_blender_offset_and_map_conversion(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_eastings = "1.0"
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Northings = 1.0
        assert subject.xyz2enh([0.0, 0.0, 0.0], map_conversion) == (1.0, 1.0, 0.0)


class TestEnh2Xyz(NewFile):
    def test_run(self):
        assert subject.enh2xyz([0.0, 0.0, 0.0], None) == [0.0, 0.0, 0.0]

    def test_using_the_blender_offset(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_eastings = "1.0"
        assert subject.enh2xyz([0.0, 0.0, 0.0], None) == (-1.0, 0.0, 0.0)

    def test_using_the_map_conversion(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Eastings = 1.0
        assert subject.enh2xyz([0.0, 0.0, 0.0], map_conversion) == (-1.0, 0.0, 0.0)

    def test_applying_both_blender_offset_and_map_conversion(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.has_blender_offset = True
        props.blender_eastings = "1.0"
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        ifcopenshell.api.run("georeference.add_georeferencing", ifc)
        map_conversion = ifc.by_type("IfcMapConversion")[0]
        map_conversion.Northings = 1.0
        assert subject.enh2xyz([0.0, 0.0, 0.0], map_conversion) == (-1.0, -1.0, 0.0)


class TestSetIfcGridNorth(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        new = props.map_conversion.add()
        new.name = "XAxisAbscissa"
        new = props.map_conversion.add()
        new.name = "XAxisOrdinate"
        subject.set_ifc_grid_north()
        assert round(float(props.map_conversion.get("XAxisAbscissa").string_value), 3) == 1.0
        assert round(float(props.map_conversion.get("XAxisOrdinate").string_value), 3) == 0.0
        bpy.context.scene.sun_pos_properties.north_offset = math.radians(-45)
        subject.set_ifc_grid_north()
        assert round(float(props.map_conversion.get("XAxisAbscissa").string_value), 3) == 0.707
        assert round(float(props.map_conversion.get("XAxisOrdinate").string_value), 3) == -0.707
        bpy.context.scene.sun_pos_properties.north_offset = math.radians(45)
        subject.set_ifc_grid_north()
        assert round(float(props.map_conversion.get("XAxisAbscissa").string_value), 3) == 0.707
        assert round(float(props.map_conversion.get("XAxisOrdinate").string_value), 3) == 0.707
        bpy.context.scene.sun_pos_properties.north_offset = math.radians(135)
        subject.set_ifc_grid_north()
        assert round(float(props.map_conversion.get("XAxisAbscissa").string_value), 3) == -0.707
        assert round(float(props.map_conversion.get("XAxisOrdinate").string_value), 3) == 0.707
        bpy.context.scene.sun_pos_properties.north_offset = math.radians(-135)
        subject.set_ifc_grid_north()
        assert round(float(props.map_conversion.get("XAxisAbscissa").string_value), 3) == -0.707
        assert round(float(props.map_conversion.get("XAxisOrdinate").string_value), 3) == -0.707


class TestSetBlenderGridNorth(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        new = props.map_conversion.add()
        new.name = "XAxisAbscissa"
        new = props.map_conversion.add()
        new.name = "XAxisOrdinate"
        props.map_conversion.get("XAxisAbscissa").string_value = "1.0"
        props.map_conversion.get("XAxisOrdinate").string_value = "0.0"
        subject.set_blender_grid_north()
        assert bpy.context.scene.sun_pos_properties.north_offset == 0
        props.map_conversion.get("XAxisAbscissa").string_value = "0.707"
        props.map_conversion.get("XAxisOrdinate").string_value = "-0.707"
        subject.set_blender_grid_north()
        assert round(math.degrees(bpy.context.scene.sun_pos_properties.north_offset)) == -45
        props.map_conversion.get("XAxisAbscissa").string_value = "0.707"
        props.map_conversion.get("XAxisOrdinate").string_value = "0.707"
        subject.set_blender_grid_north()
        assert round(math.degrees(bpy.context.scene.sun_pos_properties.north_offset)) == 45
        props.map_conversion.get("XAxisAbscissa").string_value = "-0.707"
        props.map_conversion.get("XAxisOrdinate").string_value = "0.707"
        subject.set_blender_grid_north()
        assert round(math.degrees(bpy.context.scene.sun_pos_properties.north_offset)) == 135
        props.map_conversion.get("XAxisAbscissa").string_value = "-0.707"
        props.map_conversion.get("XAxisOrdinate").string_value = "-0.707"
        subject.set_blender_grid_north()
        assert round(math.degrees(bpy.context.scene.sun_pos_properties.north_offset)) == -135
