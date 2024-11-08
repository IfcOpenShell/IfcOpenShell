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
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.unit import Unit as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Unit)


class TestClearActiveUnit(NewFile):
    def test_run(self):
        bpy.context.scene.BIMUnitProperties.active_unit_id = 1
        subject.clear_active_unit()
        assert bpy.context.scene.BIMUnitProperties.active_unit_id == 0


class TestDisableEditingUnits(NewFile):
    def test_run(self):
        bpy.context.scene.BIMUnitProperties.is_editing = True
        subject.disable_editing_units()
        assert bpy.context.scene.BIMUnitProperties.is_editing == False


class TestEnableEditingUnits(NewFile):
    def test_run(self):
        bpy.context.scene.BIMUnitProperties.is_editing = False
        subject.enable_editing_units()
        assert bpy.context.scene.BIMUnitProperties.is_editing == True


class TestExportUnitAttributes(NewFile):
    def test_exporting_derived_units(self):
        TestImportUnitAttributes().test_importing_derived_units()
        assert subject.export_unit_attributes() == {
            "UnitType": "ANGULARVELOCITYUNIT",
            "UserDefinedType": "UserDefinedType",
        }

    def test_exporting_monetary_units(self):
        TestImportUnitAttributes().test_importing_monetary_units()
        assert subject.export_unit_attributes() == {"Currency": "Currency"}

    def test_exporting_monetary_units_ifc2x3(self):
        TestImportUnitAttributes().test_importing_monetary_units_ifc2x3()
        assert subject.export_unit_attributes() == {"Currency": "USD"}

    def test_exporting_context_dependent_units(self):
        TestImportUnitAttributes().test_importing_context_dependent_units()
        assert subject.export_unit_attributes() == {
            "UnitType": "ABSORBEDDOSEUNIT",
            "Name": "Name",
            "Dimensions": [1, 2, 3, 4, 5, 6, 7],
        }

    def test_exporting_conversion_based_units(self):
        TestImportUnitAttributes().test_importing_conversion_based_units()
        assert subject.export_unit_attributes() == {
            "UnitType": "ABSORBEDDOSEUNIT",
            "Name": "Name",
            "Dimensions": [1, 2, 3, 4, 5, 6, 7],
        }

    def test_exporting_conversion_based_with_offset_units(self):
        TestImportUnitAttributes().test_importing_conversion_based_with_offset_units()
        assert subject.export_unit_attributes() == {
            "UnitType": "ABSORBEDDOSEUNIT",
            "Name": "Name",
            "Dimensions": [1, 2, 3, 4, 5, 6, 7],
            "ConversionOffset": 1,
        }

    def test_exporting_si_units(self):
        TestImportUnitAttributes().test_importing_si_units()
        assert subject.export_unit_attributes() == {"UnitType": "ABSORBEDDOSEUNIT", "Prefix": "EXA", "Name": "AMPERE"}


class TestGetSceneUnitName(NewFile):
    def test_getting_an_imperial_name(self):
        bpy.context.scene.unit_settings.system = "IMPERIAL"
        bpy.context.scene.unit_settings.length_unit = "MILES"
        bpy.context.scene.BIMProperties.area_unit = "square foot"
        bpy.context.scene.BIMProperties.volume_unit = "cubic inch"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "mile"
        assert subject.get_scene_unit_name("AREAUNIT") == "square foot"
        assert subject.get_scene_unit_name("VOLUMEUNIT") == "cubic inch"
        bpy.context.scene.unit_settings.length_unit = "FEET"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "foot"
        assert subject.get_scene_unit_name("AREAUNIT") == "square foot"
        assert subject.get_scene_unit_name("VOLUMEUNIT") == "cubic inch"
        bpy.context.scene.unit_settings.length_unit = "INCHES"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "inch"
        assert subject.get_scene_unit_name("AREAUNIT") == "square foot"
        assert subject.get_scene_unit_name("VOLUMEUNIT") == "cubic inch"
        bpy.context.scene.unit_settings.length_unit = "THOU"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "thou"
        assert subject.get_scene_unit_name("AREAUNIT") == "square foot"
        assert subject.get_scene_unit_name("VOLUMEUNIT") == "cubic inch"
        bpy.context.scene.unit_settings.length_unit = "ADAPTIVE"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "foot"
        assert subject.get_scene_unit_name("AREAUNIT") == "square foot"
        assert subject.get_scene_unit_name("VOLUMEUNIT") == "cubic inch"

    def test_getting_a_name_with_no_unit_system(self):
        bpy.context.scene.unit_settings.system = "NONE"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "foot"


class TestGetSceneUnitSIPrefix:
    def test_run(self):
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.length_unit = "METERS"
        assert subject.get_scene_unit_si_prefix("LENGTHUNIT") is None
        bpy.context.scene.unit_settings.length_unit = "MICROMETERS"
        assert subject.get_scene_unit_si_prefix("LENGTHUNIT") == "MICRO"
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        assert subject.get_scene_unit_si_prefix("LENGTHUNIT") == "MILLI"
        bpy.context.scene.unit_settings.length_unit = "CENTIMETERS"
        assert subject.get_scene_unit_si_prefix("LENGTHUNIT") == "CENTI"
        bpy.context.scene.unit_settings.length_unit = "KILOMETERS"
        assert subject.get_scene_unit_si_prefix("LENGTHUNIT") == "KILO"
        bpy.context.scene.unit_settings.length_unit = "ADAPTIVE"
        assert subject.get_scene_unit_si_prefix("LENGTHUNIT") is None
        bpy.context.scene.BIMProperties.area_unit = "SQUARE_METRE"
        assert subject.get_scene_unit_si_prefix("AREAUNIT") is None
        bpy.context.scene.BIMProperties.area_unit = "MILLI/SQUARE_METRE"
        assert subject.get_scene_unit_si_prefix("AREAUNIT") == "MILLI"
        bpy.context.scene.BIMProperties.volume_unit = "CUBIC_METRE"
        assert subject.get_scene_unit_si_prefix("VOLUMEUNIT") is None
        bpy.context.scene.BIMProperties.volume_unit = "MILLI/CUBIC_METRE"
        assert subject.get_scene_unit_si_prefix("VOLUMEUNIT") == "MILLI"


class TestImportUnitAttributes(NewFile):
    def test_importing_derived_units(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        unit = ifc.createIfcDerivedUnit()
        unit.UnitType = "ANGULARVELOCITYUNIT"
        unit.UserDefinedType = "UserDefinedType"
        subject.import_unit_attributes(unit)
        props = bpy.context.scene.BIMUnitProperties
        assert props.unit_attributes.get("UnitType").enum_value == "ANGULARVELOCITYUNIT"
        assert props.unit_attributes.get("UserDefinedType").string_value == "UserDefinedType"

    def test_importing_monetary_units(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        unit = ifc.createIfcMonetaryUnit()
        unit.Currency = "Currency"
        subject.import_unit_attributes(unit)
        props = bpy.context.scene.BIMUnitProperties
        assert props.unit_attributes.get("Currency").string_value == "Currency"

    def test_importing_monetary_units_ifc2x3(self):
        tool.Ifc.set(ifc := ifcopenshell.file(schema="IFC2X3"))
        unit = ifc.createIfcMonetaryUnit()
        unit.Currency = "USD"
        subject.import_unit_attributes(unit)
        props = bpy.context.scene.BIMUnitProperties
        assert props.unit_attributes.get("Currency").enum_value == "USD"

    def test_importing_context_dependent_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcContextDependentUnit()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Name = "Name"
        unit.Dimensions = ifc.createIfcDimensionalExponents(1, 2, 3, 4, 5, 6, 7)
        subject.import_unit_attributes(unit)
        props = bpy.context.scene.BIMUnitProperties
        assert props.unit_attributes.get("UnitType").enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes.get("Name").string_value == "Name"
        assert props.unit_attributes.get("Dimensions").string_value == "[1, 2, 3, 4, 5, 6, 7]"

    def test_importing_conversion_based_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcConversionBasedUnit()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Name = "Name"
        unit.Dimensions = ifc.createIfcDimensionalExponents(1, 2, 3, 4, 5, 6, 7)
        subject.import_unit_attributes(unit)
        props = bpy.context.scene.BIMUnitProperties
        assert props.unit_attributes.get("UnitType").enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes.get("Name").string_value == "Name"
        assert props.unit_attributes.get("Dimensions").string_value == "[1, 2, 3, 4, 5, 6, 7]"

    def test_importing_conversion_based_with_offset_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcConversionBasedUnitWithOffset()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Name = "Name"
        unit.Dimensions = ifc.createIfcDimensionalExponents(1, 2, 3, 4, 5, 6, 7)
        unit.ConversionOffset = 1
        subject.import_unit_attributes(unit)
        props = bpy.context.scene.BIMUnitProperties
        assert props.unit_attributes.get("UnitType").enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes.get("Name").string_value == "Name"
        assert props.unit_attributes.get("Dimensions").string_value == "[1, 2, 3, 4, 5, 6, 7]"
        assert props.unit_attributes.get("ConversionOffset").float_value == 1

    def test_importing_si_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcSIUnit()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Prefix = "EXA"
        unit.Name = "AMPERE"
        subject.import_unit_attributes(unit)
        props = bpy.context.scene.BIMUnitProperties
        assert props.unit_attributes.get("UnitType").enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes.get("Prefix").enum_value == "EXA"
        assert props.unit_attributes.get("Name").enum_value == "AMPERE"
        assert props.unit_attributes.get("Dimensions") is None


class TestImportUnits(NewFile):
    def test_importing_multiple_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit1 = ifc.createIfcDerivedUnit(UnitType="ANGULARVELOCITYUNIT")
        unit2 = ifc.createIfcMonetaryUnit(Currency="Currency")
        unit3 = ifc.createIfcContextDependentUnit(Name="Name", UnitType="ABSORBEDDOSEUNIT")
        unit4 = ifc.createIfcConversionBasedUnit(Name="Name", UnitType="ABSORBEDDOSEUNIT")
        unit5 = ifc.createIfcSIUnit(Name="AMPERE", Prefix="MILLI", UnitType="ABSORBEDDOSEUNIT")
        unit6 = ifc.createIfcSIUnit(Name="CUBIC_METRE", Prefix="CENTI", UnitType="ABSORBEDDOSEUNIT")
        ifc.createIfcUnitAssignment(Units=[unit2])
        subject.import_units()
        props = bpy.context.scene.BIMUnitProperties
        assert len(props.units) == 6

        assert props.units[0].ifc_definition_id == unit1.id()
        assert props.units[0].name == ""
        assert props.units[0].is_assigned is False
        assert props.units[0].unit_type == unit1.UnitType
        assert props.units[0].ifc_class == unit1.is_a()

        assert props.units[1].ifc_definition_id == unit2.id()
        assert props.units[1].name == "Currency"
        assert props.units[1].is_assigned is True
        assert props.units[1].unit_type == "CURRENCY"
        assert props.units[1].ifc_class == unit2.is_a()

        assert props.units[2].ifc_definition_id == unit3.id()
        assert props.units[2].name == "Name"
        assert props.units[2].is_assigned is False
        assert props.units[2].unit_type == unit3.UnitType
        assert props.units[2].ifc_class == unit3.is_a()

        assert props.units[3].ifc_definition_id == unit4.id()
        assert props.units[3].name == "Name"
        assert props.units[3].is_assigned is False
        assert props.units[3].unit_type == unit4.UnitType
        assert props.units[3].ifc_class == unit4.is_a()

        assert props.units[4].ifc_definition_id == unit5.id()
        assert props.units[4].name == "MILLIAMPERE"
        assert props.units[4].is_assigned is False
        assert props.units[4].unit_type == unit5.UnitType
        assert props.units[4].ifc_class == unit5.is_a()

        assert props.units[5].ifc_definition_id == unit6.id()
        assert props.units[5].name == "CUBIC CENTIMETRE"
        assert props.units[5].is_assigned is False
        assert props.units[5].unit_type == unit6.UnitType
        assert props.units[5].ifc_class == unit6.is_a()


class TestIsSceneUnitMetric(NewFile):
    def test_run(self):
        props = bpy.context.scene.unit_settings
        props.system = "METRIC"
        assert subject.is_scene_unit_metric() is True
        props.system = "IMPERIAL"
        assert subject.is_scene_unit_metric() is False
        props.system = "NONE"
        assert subject.is_scene_unit_metric() is True


class TestIsUnitClass:
    def test_run(self):
        ifc = ifcopenshell.file()
        assert subject.is_unit_class(ifc.createIfcSIUnit(), "IfcNamedUnit") is True
        assert subject.is_unit_class(ifc.createIfcSIUnit(), "IfcMonetaryUnit") is False


class TestSetActiveUnit(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        unit = ifc.createIfcSIUnit()
        subject.set_active_unit(unit)
        assert bpy.context.scene.BIMUnitProperties.active_unit_id == unit.id()
