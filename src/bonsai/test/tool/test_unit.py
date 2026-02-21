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
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.unit import Unit as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Unit)


class TestParseDistanceString(NewFile):
    def test_run(self):
        assert subject.parse_distance_string("5m") == (True, 5.0)
        assert subject.parse_distance_string("30cm") == (True, 0.3)
        assert subject.parse_distance_string("10ft") == (True, 3.048)
        assert subject.parse_distance_string("12in") == (True, 0.3048)
        assert subject.parse_distance_string("5'6\"") == (True, 1.6764)
        assert subject.parse_distance_string("-5'6\"") == (True, -1.6764)
        assert subject.parse_distance_string("invalid") == (False, 0.0)


class TestClearActiveUnit(NewFile):
    def test_run(self):
        props = tool.Unit.get_unit_props()
        props.active_unit_id = 1
        subject.clear_active_unit()
        assert props.active_unit_id == 0


class TestDisableEditingUnits(NewFile):
    def test_run(self):
        props = tool.Unit.get_unit_props()
        props.is_editing = True
        subject.disable_editing_units()
        assert props.is_editing == False


class TestEnableEditingUnits(NewFile):
    def test_run(self):
        props = tool.Unit.get_unit_props()
        props.is_editing = False
        subject.enable_editing_units()
        assert props.is_editing == True


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
        assert bpy.context.scene
        props = tool.Blender.get_bim_props()
        bpy.context.scene.unit_settings.system = "IMPERIAL"
        bpy.context.scene.unit_settings.length_unit = "MILES"
        props.area_unit = "square foot"
        props.volume_unit = "cubic inch"
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

    def test_getting_an_si_name(self):
        props = tool.Blender.get_bim_props()
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.length_unit = "METERS"
        props.area_unit = "SQUARE_METRE"
        props.volume_unit = "CUBIC_METRE"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "METRE"
        assert subject.get_scene_unit_name("AREAUNIT") == "SQUARE_METRE"
        assert subject.get_scene_unit_name("VOLUMEUNIT") == "CUBIC_METRE"
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "MILLI/METRE"
        bpy.context.scene.unit_settings.length_unit = "ADAPTIVE"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "METRE"

    def test_getting_a_name_with_no_unit_system(self):
        assert bpy.context.scene
        bpy.context.scene.unit_settings.system = "NONE"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "METRE"
        bpy.context.scene.unit_settings.length_unit = "ADAPTIVE"
        assert subject.get_scene_unit_name("LENGTHUNIT") == "METRE"
        assert subject.get_scene_unit_name("AREAUNIT") == "SQUARE_METRE"
        assert subject.get_scene_unit_name("VOLUMEUNIT") == "CUBIC_METRE"

    def test_getting_mass_unit_names(self):
        """Test getting mass unit names for different systems"""
        assert bpy.context.scene
        props = tool.Blender.get_bim_props()
        props.mass_unit = "GRAM"
        assert subject.get_scene_unit_name("MASSUNIT") == "GRAM"
        props.mass_unit = "KILO/GRAM"
        assert subject.get_scene_unit_name("MASSUNIT") == "KILO/GRAM"
        props.mass_unit = "MEGA/GRAM"
        assert subject.get_scene_unit_name("MASSUNIT") == "MEGA/GRAM"
        props.mass_unit = "pound"
        assert subject.get_scene_unit_name("MASSUNIT") == "pound"
        props.mass_unit = "ounce"
        assert subject.get_scene_unit_name("MASSUNIT") == "ounce"

    def test_getting_time_unit_names(self):
        """Test getting time unit names for different systems"""
        assert bpy.context.scene
        props = tool.Blender.get_bim_props()

        props.time_unit = "SECOND"
        assert subject.get_scene_unit_name("TIMEUNIT") == "SECOND"
        props.time_unit = "minute"
        assert subject.get_scene_unit_name("TIMEUNIT") == "minute"
        props.time_unit = "NONE"
        assert not subject.get_scene_unit_name("TIMEUNIT")


class TestGetSceneUnitSIPrefix:
    def test_run(self):
        assert bpy.context.scene
        assert subject.get_scene_unit_si_prefix("METRE") is None
        assert subject.get_scene_unit_si_prefix("MICRO/METRE") == "MICRO"
        assert subject.get_scene_unit_si_prefix("SQUARE_METRE") is None
        assert subject.get_scene_unit_si_prefix("MILLI/SQUARE_METRE") == "MILLI"
        assert subject.get_scene_unit_si_prefix("foot") is None

    def test_mass_and_time_unit_prefixes(self):
        assert subject.get_scene_unit_si_prefix("KILO/GRAM") == "KILO"
        assert subject.get_scene_unit_si_prefix("MEGA/GRAM") == "MEGA"
        assert subject.get_scene_unit_si_prefix("GRAM") is None


class TestImportUnitAttributes(NewFile):
    def test_importing_derived_units(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        unit = ifc.createIfcDerivedUnit()
        unit.UnitType = "ANGULARVELOCITYUNIT"
        unit.UserDefinedType = "UserDefinedType"
        subject.import_unit_attributes(unit)
        props = tool.Unit.get_unit_props()
        assert props.unit_attributes["UnitType"].enum_value == "ANGULARVELOCITYUNIT"
        assert props.unit_attributes["UserDefinedType"].string_value == "UserDefinedType"

    def test_importing_monetary_units(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        unit = ifc.createIfcMonetaryUnit()
        unit.Currency = "Currency"
        subject.import_unit_attributes(unit)
        props = tool.Unit.get_unit_props()
        assert props.unit_attributes["Currency"].string_value == "Currency"

    def test_importing_monetary_units_ifc2x3(self):
        tool.Ifc.set(ifc := ifcopenshell.file(schema="IFC2X3"))
        unit = ifc.createIfcMonetaryUnit()
        unit.Currency = "USD"
        subject.import_unit_attributes(unit)
        props = tool.Unit.get_unit_props()
        assert props.unit_attributes["Currency"].enum_value == "USD"

    def test_importing_context_dependent_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcContextDependentUnit()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Name = "Name"
        unit.Dimensions = ifc.createIfcDimensionalExponents(1, 2, 3, 4, 5, 6, 7)
        subject.import_unit_attributes(unit)
        props = tool.Unit.get_unit_props()
        assert props.unit_attributes["UnitType"].enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes["Name"].string_value == "Name"
        assert props.unit_attributes["Dimensions"].string_value == "[1, 2, 3, 4, 5, 6, 7]"

    def test_importing_conversion_based_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcConversionBasedUnit()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Name = "Name"
        unit.Dimensions = ifc.createIfcDimensionalExponents(1, 2, 3, 4, 5, 6, 7)
        subject.import_unit_attributes(unit)
        props = tool.Unit.get_unit_props()
        assert props.unit_attributes["UnitType"].enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes["Name"].string_value == "Name"
        assert props.unit_attributes["Dimensions"].string_value == "[1, 2, 3, 4, 5, 6, 7]"

    def test_importing_conversion_based_with_offset_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcConversionBasedUnitWithOffset()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Name = "Name"
        unit.Dimensions = ifc.createIfcDimensionalExponents(1, 2, 3, 4, 5, 6, 7)
        unit.ConversionOffset = 1
        subject.import_unit_attributes(unit)
        props = tool.Unit.get_unit_props()
        assert props.unit_attributes["UnitType"].enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes["Name"].string_value == "Name"
        assert props.unit_attributes["Dimensions"].string_value == "[1, 2, 3, 4, 5, 6, 7]"
        assert props.unit_attributes["ConversionOffset"].float_value == 1

    def test_importing_si_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        unit = ifc.createIfcSIUnit()
        unit.UnitType = "ABSORBEDDOSEUNIT"
        unit.Prefix = "EXA"
        unit.Name = "AMPERE"
        subject.import_unit_attributes(unit)
        props = tool.Unit.get_unit_props()
        assert props.unit_attributes["UnitType"].enum_value == "ABSORBEDDOSEUNIT"
        assert props.unit_attributes["Prefix"].enum_value == "EXA"
        assert props.unit_attributes["Name"].enum_value == "AMPERE"
        assert "Dimensions" not in props.unit_attributes


class TestImportUnits(NewFile):
    def test_importing_multiple_units(self):
        ifc = ifcopenshell.api.project.create_file()
        tool.Ifc.set(ifc)
        unit1 = ifc.createIfcDerivedUnit(UnitType="ANGULARVELOCITYUNIT")
        unit2 = ifc.createIfcMonetaryUnit(Currency="Currency")
        unit3 = ifc.createIfcContextDependentUnit(Name="Name", UnitType="ABSORBEDDOSEUNIT")
        unit4 = ifc.createIfcConversionBasedUnit(Name="Name", UnitType="ABSORBEDDOSEUNIT")
        unit5 = ifc.createIfcSIUnit(Name="AMPERE", Prefix="MILLI", UnitType="ABSORBEDDOSEUNIT")
        unit6 = ifc.createIfcSIUnit(Name="CUBIC_METRE", Prefix="CENTI", UnitType="ABSORBEDDOSEUNIT")
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc, units=[unit2])
        subject.import_units()
        props = tool.Unit.get_unit_props()
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

    def test_importing_mass_and_time_units(self):
        """Test importing mass and time conversion based units"""
        ifc = ifcopenshell.api.project.create_file()
        tool.Ifc.set(ifc)

        tonne_unit = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="tonne")
        pound_unit = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="pound")
        ounce_unit = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="ounce")

        minute_unit = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="minute")
        hour_unit = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="hour")
        day_unit = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="day")

        kg_unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="MASSUNIT", prefix="KILO")
        gram_unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="MASSUNIT")
        second_unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="TIMEUNIT")

        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc, units=[tonne_unit, minute_unit, kg_unit])

        subject.import_units()
        props = tool.Unit.get_unit_props()

        assert len(props.units) == 15

        unit_ids = [u.ifc_definition_id for u in props.units]
        assert tonne_unit.id() in unit_ids
        assert pound_unit.id() in unit_ids
        assert ounce_unit.id() in unit_ids
        assert minute_unit.id() in unit_ids
        assert hour_unit.id() in unit_ids
        assert day_unit.id() in unit_ids
        assert kg_unit.id() in unit_ids
        assert gram_unit.id() in unit_ids
        assert second_unit.id() in unit_ids

        tonne_prop = next(u for u in props.units if u.ifc_definition_id == tonne_unit.id())
        assert tonne_prop.name == "tonne"
        assert tonne_prop.unit_type == "MASSUNIT"
        assert tonne_prop.is_assigned is True
        assert tonne_prop.ifc_class == "IfcConversionBasedUnit"

        pound_prop = next(u for u in props.units if u.ifc_definition_id == pound_unit.id())
        assert pound_prop.name == "pound"
        assert pound_prop.unit_type == "MASSUNIT"
        assert pound_prop.is_assigned is False
        assert pound_prop.ifc_class == "IfcConversionBasedUnit"

        ounce_prop = next(u for u in props.units if u.ifc_definition_id == ounce_unit.id())
        assert ounce_prop.name == "ounce"
        assert ounce_prop.unit_type == "MASSUNIT"
        assert ounce_prop.is_assigned is False
        assert ounce_prop.ifc_class == "IfcConversionBasedUnit"

        kg_prop = next(u for u in props.units if u.ifc_definition_id == kg_unit.id())
        assert kg_prop.name == "KILOGRAM"
        assert kg_prop.unit_type == "MASSUNIT"
        assert kg_prop.is_assigned is True
        assert kg_prop.ifc_class == "IfcSIUnit"

        gram_prop = next(u for u in props.units if u.ifc_definition_id == gram_unit.id())
        assert gram_prop.name == "GRAM"
        assert gram_prop.unit_type == "MASSUNIT"
        assert gram_prop.is_assigned is False
        assert gram_prop.ifc_class == "IfcSIUnit"

        minute_prop = next(u for u in props.units if u.ifc_definition_id == minute_unit.id())
        assert minute_prop.name == "minute"
        assert minute_prop.unit_type == "TIMEUNIT"
        assert minute_prop.is_assigned is True
        assert minute_prop.ifc_class == "IfcConversionBasedUnit"

        hour_prop = next(u for u in props.units if u.ifc_definition_id == hour_unit.id())
        assert hour_prop.name == "hour"
        assert hour_prop.unit_type == "TIMEUNIT"
        assert hour_prop.is_assigned is False
        assert hour_prop.ifc_class == "IfcConversionBasedUnit"

        day_prop = next(u for u in props.units if u.ifc_definition_id == day_unit.id())
        assert day_prop.name == "day"
        assert day_prop.unit_type == "TIMEUNIT"
        assert day_prop.is_assigned is False
        assert day_prop.ifc_class == "IfcConversionBasedUnit"

        second_prop = next(u for u in props.units if u.ifc_definition_id == second_unit.id())
        assert second_prop.name == "SECOND"
        assert second_prop.unit_type == "TIMEUNIT"
        assert second_prop.is_assigned is False
        assert second_prop.ifc_class == "IfcSIUnit"


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
        props = tool.Unit.get_unit_props()
        assert props.active_unit_id == unit.id()
