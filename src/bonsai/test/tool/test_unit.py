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
import ifcopenshell.util.attribute
import ifcopenshell.util.unit
import pytest

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


class TestAddDerivedUnit(NewFile):
    def setup_project(self, *units):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        if units:
            ifcopenshell.api.unit.assign_unit(ifc, units=[u(ifc) for u in units])
        return ifc

    def test_composes_from_the_project_length_unit(self):
        ifc = self.setup_project(lambda f: ifcopenshell.api.unit.add_si_unit(f, "LENGTHUNIT", prefix="MILLI"))
        unit = subject.add_derived_unit("MOMENTOFINERTIAUNIT")
        assert unit.is_a("IfcDerivedUnit")
        assert unit.UnitType == "MOMENTOFINERTIAUNIT"
        assert ifcopenshell.util.unit.get_unit_symbol(unit) == "mm4"
        assert ifcopenshell.util.unit.get_unit_scale(unit) == pytest.approx(1e-12)
        # Reuses the project's own millimetre rather than creating another.
        assert len(ifc.by_type("IfcSIUnit")) == 1

    def test_composes_from_several_project_units(self):
        self.setup_project(
            lambda f: ifcopenshell.api.unit.add_si_unit(f, "LENGTHUNIT"),
            lambda f: ifcopenshell.api.unit.add_si_unit(f, "FORCEUNIT", prefix="KILO"),
        )
        unit = subject.add_derived_unit("LINEARFORCEUNIT")
        assert ifcopenshell.util.unit.get_unit_symbol(unit) == "kN/m"
        assert ifcopenshell.util.unit.get_unit_scale(unit) == pytest.approx(1e3)

    def test_falls_back_to_unassigned_si_units_for_missing_components(self):
        ifc = self.setup_project(lambda f: ifcopenshell.api.unit.add_si_unit(f, "LENGTHUNIT"))
        unit = subject.add_derived_unit("MASSPERLENGTHUNIT")
        assert ifcopenshell.util.unit.get_unit_symbol(unit) == "kg/m"
        # The fallback kilogram isn't assigned: that would silently change the project's units.
        assert ifcopenshell.util.unit.get_project_unit(ifc, "MASSUNIT") is None

    def test_inch_section_properties_in_a_foot_project(self):
        ifc = self.setup_project(lambda f: ifcopenshell.api.unit.add_conversion_based_unit(f, name="foot"))
        inch = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="inch")
        unit = subject.add_derived_unit("MOMENTOFINERTIAUNIT", {"LENGTHUNIT": inch})
        assert ifcopenshell.util.unit.get_unit_symbol(unit) == "in4"
        assert ifcopenshell.util.unit.get_unit_scale(unit) == pytest.approx(0.0254**4)
        assert (
            ifcopenshell.util.unit.get_unit_symbol(ifcopenshell.util.unit.get_project_unit(ifc, "LENGTHUNIT")) == "ft"
        )

    def test_chosen_length_unit_only_replaces_length_components(self):
        self.setup_project(
            lambda f: ifcopenshell.api.unit.add_conversion_based_unit(f, name="foot"),
            lambda f: ifcopenshell.api.unit.add_conversion_based_unit(f, name="kip"),
        )
        inch = ifcopenshell.api.unit.add_conversion_based_unit(tool.Ifc.get(), name="inch")
        unit = subject.add_derived_unit("MODULUSOFELASTICITYUNIT", {"LENGTHUNIT": inch})
        assert ifcopenshell.util.unit.get_unit_symbol(unit) == "kip/in2"

    def test_get_derived_unit_component_types(self):
        assert subject.get_derived_unit_component_types("MOMENTOFINERTIAUNIT") == ["LENGTHUNIT"]
        # LINEARMOMENTUNIT repeats length (kN.m/m) but needs only one length picker.
        assert subject.get_derived_unit_component_types("LINEARMOMENTUNIT") == ["FORCEUNIT", "LENGTHUNIT"]

    def test_every_composition_satisfies_ifc_derived_unit_wr1(self):
        # IfcDerivedUnit WR1: more than one element, or a single element whose exponent isn't 1.
        for unit_type, composition in subject.DERIVED_UNIT_COMPOSITIONS.items():
            assert len(composition) > 1 or composition[0][1] != 1, unit_type

    def test_every_offered_type_builds_a_valid_unit(self):
        import ifcopenshell.validate

        ifc = self.setup_project()
        for unit_type in subject.get_derived_unit_types():
            subject.add_derived_unit(unit_type)
        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(ifc, logger, express_rules=True)
        assert [s for s in logger.statements if "IfcDerivedUnit" in str(s)] == []

    def test_a_repeated_component_type_reuses_one_unit(self):
        ifc = self.setup_project()
        unit = subject.add_derived_unit("LINEARMOMENTUNIT")
        assert [e.Exponent for e in unit.Elements] == [1, 1, -1]
        assert unit.Elements[1].Unit == unit.Elements[2].Unit
        assert len(ifc.by_type("IfcSIUnit")) == 2  # one newton, one metre

    def test_every_composition_is_a_real_derived_unit_type(self):
        all_values = set()
        for schema in ("IFC2X3", "IFC4", "IFC4X3"):
            entity = ifcopenshell.schema_by_name(schema).declaration_by_name("IfcDerivedUnit").as_entity()
            all_values |= set(ifcopenshell.util.attribute.get_enum_items(entity.attribute_by_index(1)))
        assert set(subject.DERIVED_UNIT_COMPOSITIONS) <= all_values

    def test_every_offered_type_can_be_built(self):
        ifc = self.setup_project()
        unit_types = subject.get_derived_unit_types()
        assert "MOMENTOFINERTIAUNIT" in unit_types
        assert "USERDEFINED" not in unit_types
        for unit_type in unit_types:
            unit = subject.add_derived_unit(unit_type)
            assert unit.UnitType == unit_type
            assert ifcopenshell.util.unit.get_unit_symbol(unit)

    def test_only_offers_types_in_the_current_schema(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        # AREADENSITYUNIT was introduced in IFC4.
        assert "AREADENSITYUNIT" not in subject.get_derived_unit_types()
        assert "MOMENTOFINERTIAUNIT" in subject.get_derived_unit_types()


class TestComponentUnitChoices(NewFile):
    def setup_pa_foot_project(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        foot = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="foot")
        pascal = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PRESSUREUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[foot, pascal])
        return ifc

    def labels(self, unit_type):
        return [label for _, label, _ in subject.get_component_unit_choices(unit_type)]

    def test_default_then_existing_then_new_units(self):
        self.setup_pa_foot_project()
        labels = self.labels("LENGTHUNIT")
        assert labels[0] == "Default (ft)"
        assert labels[1] == "foot (ft)"
        assert "+ inch (in)" in labels
        assert "+ MILLIMETRE (mm)" in labels
        assert "+ foot (ft)" not in labels  # already in the file

    def test_pressure_offers_the_imperial_catalog(self):
        self.setup_pa_foot_project()
        labels = self.labels("PRESSUREUNIT")
        assert labels[0] == "Default (Pa)"
        for expected in ("+ psi (psi)", "+ ksi (ksi)", "+ psf (psf)", "+ ksf (ksf)", "+ KILOPASCAL (kPa)"):
            assert expected in labels
        assert "+ PASCAL (Pa)" not in labels  # already in the file

    def test_a_type_without_a_project_unit_defaults_to_si(self):
        self.setup_pa_foot_project()
        assert self.labels("FORCEUNIT")[0] == "SI (N)"
        assert self.labels("MASSUNIT")[0] == "SI (kg)"

    def test_offset_units_are_not_offered(self):
        self.setup_pa_foot_project()
        assert not any("fahrenheit" in label for label in self.labels("THERMODYNAMICTEMPERATUREUNIT"))

    def test_resolving_choices(self):
        ifc = self.setup_pa_foot_project()
        foot = ifcopenshell.util.unit.get_project_unit(ifc, "LENGTHUNIT")
        assert subject.resolve_unit_choice("LENGTHUNIT", "0") is None
        assert subject.resolve_unit_choice("LENGTHUNIT", str(foot.id())) == foot
        kip = subject.resolve_unit_choice("FORCEUNIT", "+CONV:kip")
        assert kip.is_a("IfcConversionBasedUnit") and kip.Name == "kip"
        kpa = subject.resolve_unit_choice("PRESSUREUNIT", "+SI:KILO")
        assert kpa.is_a("IfcSIUnit") and kpa.Prefix == "KILO"
        assert subject.resolve_unit_choice("LENGTHUNIT", "+SI:").Prefix is None

    def test_ksi_modulus_of_elasticity_in_a_foot_project(self):
        ifc = self.setup_pa_foot_project()
        components = {
            "FORCEUNIT": subject.resolve_unit_choice("FORCEUNIT", "+CONV:kip"),
            "LENGTHUNIT": subject.resolve_unit_choice("LENGTHUNIT", "+CONV:inch"),
        }
        unit = subject.add_derived_unit("MODULUSOFELASTICITYUNIT", components)
        assert ifcopenshell.util.unit.get_unit_symbol(unit) == "kip/in2"
        assert ifcopenshell.util.unit.get_unit_scale(unit) == pytest.approx(6894757.2932)  # = 1 ksi
        assert (
            ifcopenshell.util.unit.get_unit_symbol(ifcopenshell.util.unit.get_project_unit(ifc, "LENGTHUNIT")) == "ft"
        )


class TestAddStructuralUnits(NewFile):
    def get_units(self, system: str) -> dict[str, tuple[str, float]]:
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        bpy.context.scene.unit_settings.system = system
        units = subject.add_structural_units()
        return {
            u.UnitType: (ifcopenshell.util.unit.get_unit_symbol(u), ifcopenshell.util.unit.get_unit_scale(u))
            for u in units
        }

    def test_metric(self):
        units = self.get_units("METRIC")
        assert units["FORCEUNIT"] == ("kN", 1e3)
        assert units["TORQUEUNIT"] == ("kN.m", 1e3)
        assert units["LINEARFORCEUNIT"] == ("kN/m", 1e3)
        assert units["LINEARMOMENTUNIT"] == ("kN.m/m", 1e3)
        assert units["PLANARFORCEUNIT"] == ("kN/m2", 1e3)
        assert units["LINEARSTIFFNESSUNIT"] == ("kN/m", 1e3)
        assert units["ROTATIONALSTIFFNESSUNIT"] == ("kN.m/rad", 1e3)
        assert units["MODULUSOFLINEARSUBGRADEREACTIONUNIT"] == ("kN/m2", 1e3)
        assert units["MODULUSOFROTATIONALSUBGRADEREACTIONUNIT"] == ("kN.m/m.rad", 1e3)
        assert units["MODULUSOFSUBGRADEREACTIONUNIT"] == ("kN/m3", 1e3)
        assert units["MODULUSOFELASTICITYUNIT"] == ("N/mm2", pytest.approx(1e6))
        assert units["SHEARMODULUSUNIT"] == ("N/mm2", pytest.approx(1e6))
        assert units["MASSDENSITYUNIT"][0] == "kg/m3"  # get_unit_scale counts mass in grams
        assert len(units) == 13

    def test_imperial(self):
        kip, foot, inch = 4448.2216153, 0.3048, 0.0254
        units = self.get_units("IMPERIAL")
        assert units["FORCEUNIT"] == ("kip", pytest.approx(kip))
        assert units["TORQUEUNIT"] == ("kip.ft", pytest.approx(kip * foot))
        assert units["LINEARFORCEUNIT"] == ("kip/ft", pytest.approx(kip / foot))
        assert units["PLANARFORCEUNIT"] == ("lbf/ft2", pytest.approx(4.4482216153 / foot**2))
        assert units["LINEARSTIFFNESSUNIT"] == ("kip/in", pytest.approx(kip / inch))
        assert units["ROTATIONALSTIFFNESSUNIT"] == ("kip.ft/rad", pytest.approx(kip * foot))
        assert units["MODULUSOFELASTICITYUNIT"] == ("kip/in2", pytest.approx(kip / inch**2))
        assert units["MASSDENSITYUNIT"][0] == "lb/ft3"
        assert len(units) == 13

    def test_assigning_them_replaces_none_of_the_scene_units(self):
        ifc = ifcopenshell.api.project.create_file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)
        bpy.context.scene.unit_settings.system = "METRIC"
        ifcopenshell.api.unit.assign_unit(ifc, units=subject.add_structural_units())
        assert ifcopenshell.util.unit.get_project_unit(ifc, "LENGTHUNIT").Prefix == "MILLI"
        assert ifcopenshell.util.unit.get_project_unit(ifc, "PLANEANGLEUNIT") is None


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
    def test_derived_units_are_named_by_their_symbol(self):
        ifc = ifcopenshell.api.project.create_file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(ifc, "LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.add_derived_unit(ifc, "MOMENTOFINERTIAUNIT", None, {length: 4})
        subject.import_units()
        props = tool.Unit.get_unit_props()
        assert [u.name for u in props.units if u.ifc_class == "IfcDerivedUnit"] == ["mm4"]

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


class TestGetUnitSiScale(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        assert subject.get_unit_si_scale(ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")) == 1
        mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        assert subject.get_unit_si_scale(mm) == 0.001
        foot = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="foot")
        assert round(subject.get_unit_si_scale(foot), 4) == 0.3048
        thing = ifcopenshell.api.unit.add_context_dependent_unit(ifc, name="THINGS", unit_type="LENGTHUNIT")
        assert subject.get_unit_si_scale(thing) is None


class TestGetProjectRescaleFactor(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[unit])
        assert subject.get_project_rescale_factor(0.001) is None
        ifc.createIfcShapeRepresentation()
        assert subject.get_project_rescale_factor(0.001) == 0.001
        assert subject.get_project_rescale_factor(1.0) is None
        assert subject.get_project_rescale_factor(None) is None


class TestIsProjectUnit(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        assert subject.is_project_unit(m) is False
        ifcopenshell.api.unit.assign_unit(ifc, units=[m])
        assert subject.is_project_unit(m) is True
        assert subject.is_project_unit(mm) is False


class TestGetAssignUnitRescaleFactor(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[m])
        ifc.createIfcShapeRepresentation()
        assert subject.get_assign_unit_rescale_factor(mm) == 0.001
        assert subject.get_assign_unit_rescale_factor(m) is None
        assert subject.get_assign_unit_rescale_factor(area) is None


class TestGetEditUnitRescaleFactor(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[m])
        ifc.createIfcShapeRepresentation()
        subject.import_unit_attributes(m)
        assert subject.get_edit_unit_rescale_factor(m) is None
        props = tool.Unit.get_unit_props()
        prefix = props.unit_attributes["Prefix"]
        prefix.is_null = False
        prefix.enum_value = "MILLI"
        assert subject.get_edit_unit_rescale_factor(m) == 0.001
        assert subject.get_edit_unit_rescale_factor(mm) is None


class TestGetSceneUnitsRescaleFactor(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[m])
        ifc.createIfcShapeRepresentation()
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
        assert subject.get_scene_units_rescale_factor() == 0.001
        bpy.context.scene.unit_settings.length_unit = "METERS"
        assert subject.get_scene_units_rescale_factor() is None
