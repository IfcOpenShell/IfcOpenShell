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

import bonsai.core.unit as subject
from test.core.bootstrap import ifc, unit


class TestAssignSceneUnits:
    def test_creating_and_assigning_metric_units(self, ifc, unit):
        unit.get_scene_unit_name("LENGTHUNIT").should_be_called().will_return("length_name")
        unit.get_scene_unit_name("AREAUNIT").should_be_called().will_return("area_name")
        unit.get_scene_unit_name("VOLUMEUNIT").should_be_called().will_return("volume_name")
        unit.get_scene_unit_name("MASSUNIT").should_be_called().will_return("mass_name")
        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return("time_name")
        unit.is_si_unit("length_name").should_be_called().will_return(True)
        unit.is_si_unit("area_name").should_be_called().will_return(True)
        unit.is_si_unit("volume_name").should_be_called().will_return(True)
        unit.is_si_unit("mass_name").should_be_called().will_return(True)
        unit.is_si_unit("time_name").should_be_called().will_return(True)
        unit.get_scene_unit_si_prefix("length_name").should_be_called().will_return("length_prefix")
        unit.get_scene_unit_si_prefix("area_name").should_be_called().will_return("area_prefix")
        unit.get_scene_unit_si_prefix("volume_name").should_be_called().will_return("volume_prefix")
        unit.get_scene_unit_si_prefix("mass_name").should_be_called().will_return("mass_prefix")
        unit.get_scene_unit_si_prefix("time_name").should_be_called().will_return("time_prefix")
        ifc.run("unit.add_si_unit", unit_type="LENGTHUNIT", prefix="length_prefix").should_be_called().will_return(
            "lengthunit"
        )
        ifc.run("unit.add_si_unit", unit_type="AREAUNIT", prefix="area_prefix").should_be_called().will_return(
            "areaunit"
        )
        ifc.run("unit.add_si_unit", unit_type="VOLUMEUNIT", prefix="volume_prefix").should_be_called().will_return(
            "volumeunit"
        )
        ifc.run("unit.add_si_unit", unit_type="MASSUNIT", prefix="mass_prefix").should_be_called().will_return(
            "massunit"
        )
        ifc.run("unit.add_si_unit", unit_type="TIMEUNIT", prefix="time_prefix").should_be_called().will_return(
            "timeunit"
        )
        ifc.run(
            "unit.assign_unit", units=["lengthunit", "areaunit", "volumeunit", "massunit", "timeunit"]
        ).should_be_called()
        subject.assign_scene_units(ifc, unit)

    def test_creating_and_assigning_only_specified_units(self, ifc, unit):
        unit.get_scene_unit_name("LENGTHUNIT").should_be_called().will_return("length_name")
        unit.get_scene_unit_name("AREAUNIT").should_be_called().will_return(None)
        unit.get_scene_unit_name("VOLUMEUNIT").should_be_called().will_return(None)
        unit.get_scene_unit_name("MASSUNIT").should_be_called().will_return(None)
        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return(None)
        unit.is_si_unit("length_name").should_be_called().will_return(True)
        unit.get_scene_unit_si_prefix("length_name").should_be_called().will_return("length_prefix")
        ifc.run("unit.add_si_unit", unit_type="LENGTHUNIT", prefix="length_prefix").should_be_called().will_return(
            "lengthunit"
        )
        ifc.run("unit.assign_unit", units=["lengthunit"]).should_be_called()
        subject.assign_scene_units(ifc, unit)

    def test_creating_and_assigning_imperial_units(self, ifc, unit):
        unit.get_scene_unit_name("LENGTHUNIT").should_be_called().will_return("length_name")
        unit.get_scene_unit_name("AREAUNIT").should_be_called().will_return("area_name")
        unit.get_scene_unit_name("VOLUMEUNIT").should_be_called().will_return("volume_name")
        unit.get_scene_unit_name("MASSUNIT").should_be_called().will_return("mass_name")
        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return("time_name")
        unit.is_si_unit("length_name").should_be_called().will_return(False)
        unit.is_si_unit("area_name").should_be_called().will_return(False)
        unit.is_si_unit("volume_name").should_be_called().will_return(False)
        unit.is_si_unit("mass_name").should_be_called().will_return(False)
        unit.is_si_unit("time_name").should_be_called().will_return(False)
        ifc.run("unit.add_conversion_based_unit", name="length_name").should_be_called().will_return("lengthunit")
        ifc.run("unit.add_conversion_based_unit", name="area_name").should_be_called().will_return("areaunit")
        ifc.run("unit.add_conversion_based_unit", name="volume_name").should_be_called().will_return("volumeunit")
        ifc.run("unit.add_conversion_based_unit", name="mass_name").should_be_called().will_return("massunit")
        ifc.run("unit.add_conversion_based_unit", name="time_name").should_be_called().will_return("timeunit")
        ifc.run(
            "unit.assign_unit", units=["lengthunit", "areaunit", "volumeunit", "massunit", "timeunit"]
        ).should_be_called()
        subject.assign_scene_units(ifc, unit)

    def test_creating_both_metric_and_imperial_units(self, ifc, unit):
        # I know British doctors measure with stones so...
        unit.get_scene_unit_name("LENGTHUNIT").should_be_called().will_return("length_name")
        unit.get_scene_unit_name("AREAUNIT").should_be_called().will_return("area_name")
        unit.get_scene_unit_name("VOLUMEUNIT").should_be_called().will_return(None)
        unit.get_scene_unit_name("MASSUNIT").should_be_called().will_return(None)
        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return(None)
        unit.is_si_unit("length_name").should_be_called().will_return(True)
        unit.is_si_unit("area_name").should_be_called().will_return(False)
        unit.get_scene_unit_si_prefix("length_name").should_be_called().will_return("length_prefix")
        ifc.run("unit.add_si_unit", unit_type="LENGTHUNIT", prefix="length_prefix").should_be_called().will_return(
            "lengthunit"
        )
        ifc.run("unit.add_conversion_based_unit", name="area_name").should_be_called().will_return("areaunit")
        ifc.run("unit.assign_unit", units=["lengthunit", "areaunit"]).should_be_called()
        subject.assign_scene_units(ifc, unit)


class TestAssignUnit:
    def test_run(self, ifc, unit):
        ifc.run("unit.assign_unit", units=["unit"]).should_be_called()
        unit.import_units().should_be_called()
        subject.assign_unit(ifc, unit, unit="unit")


class TestUnassignUnit:
    def test_run(self, ifc, unit):
        ifc.run("unit.unassign_unit", units=["unit"]).should_be_called()
        unit.import_units().should_be_called()
        subject.unassign_unit(ifc, unit, unit="unit")


class TestLoadUnits:
    def test_run(self, unit):
        unit.import_units().should_be_called()
        unit.enable_editing_units().should_be_called()
        subject.load_units(unit)


class TestDisableUnitEditingUI:
    def test_run(self, unit):
        unit.disable_editing_units().should_be_called()
        subject.disable_unit_editing_ui(unit)


class TestRemoveUnit:
    def test_run(self, ifc, unit):
        ifc.run("unit.remove_unit", unit="unit").should_be_called()
        unit.import_units().should_be_called()
        subject.remove_unit(ifc, unit, unit="unit")


class TestAddMonetaryUnit:
    def test_run(self, ifc, unit):
        ifc.run("unit.add_monetary_unit").should_be_called().will_return("unit")
        unit.import_units().should_be_called()
        assert subject.add_monetary_unit(ifc, unit) == "unit"


class TestAddSIUnit:
    def test_run(self, ifc, unit):
        ifc.run("unit.add_si_unit", unit_type="unit_type").should_be_called().will_return("unit")
        unit.import_units().should_be_called()
        assert subject.add_si_unit(ifc, unit, unit_type="unit_type") == "unit"


class TestAddContextDependentUnit:
    def test_run(self, ifc, unit):
        ifc.run("unit.add_context_dependent_unit", unit_type="unit_type", name="name").should_be_called().will_return(
            "unit"
        )
        unit.import_units().should_be_called()
        assert subject.add_context_dependent_unit(ifc, unit, unit_type="unit_type", name="name") == "unit"


class TestAddConversionBasedUnit:
    def test_run(self, ifc, unit):
        ifc.run("unit.add_conversion_based_unit", name="name").should_be_called().will_return("unit")
        unit.import_units().should_be_called()
        assert subject.add_conversion_based_unit(ifc, unit, name="name") == "unit"


class TestEnableEditingUnit:
    def test_run(self, unit):
        unit.set_active_unit("unit").should_be_called()
        unit.import_unit_attributes("unit").should_be_called()
        subject.enable_editing_unit(unit, unit="unit")


class TestDisableEditingUnit:
    def test_run(self, unit):
        unit.clear_active_unit().should_be_called()
        subject.disable_editing_unit(unit)


class TestEditUnit:
    def test_editing_monetary_units(self, ifc, unit):
        unit.export_unit_attributes().should_be_called().will_return("attributes")
        unit.is_unit_class("unit", "IfcMonetaryUnit").should_be_called().will_return(True)
        ifc.run("unit.edit_monetary_unit", unit="unit", attributes="attributes").should_be_called()
        unit.import_units().should_be_called()
        unit.clear_active_unit().should_be_called()
        subject.edit_unit(ifc, unit, unit="unit")

    def test_editing_derived_units(self, ifc, unit):
        unit.export_unit_attributes().should_be_called().will_return("attributes")
        unit.is_unit_class("unit", "IfcMonetaryUnit").should_be_called().will_return(False)
        unit.is_unit_class("unit", "IfcDerivedUnit").should_be_called().will_return(True)
        ifc.run("unit.edit_derived_unit", unit="unit", attributes="attributes").should_be_called()
        unit.import_units().should_be_called()
        unit.clear_active_unit().should_be_called()
        subject.edit_unit(ifc, unit, unit="unit")

    def test_editing_named_units(self, ifc, unit):
        unit.export_unit_attributes().should_be_called().will_return("attributes")
        unit.is_unit_class("unit", "IfcMonetaryUnit").should_be_called().will_return(False)
        unit.is_unit_class("unit", "IfcDerivedUnit").should_be_called().will_return(False)
        unit.is_unit_class("unit", "IfcNamedUnit").should_be_called().will_return(True)
        ifc.run("unit.edit_named_unit", unit="unit", attributes="attributes").should_be_called()
        unit.import_units().should_be_called()
        unit.clear_active_unit().should_be_called()
        subject.edit_unit(ifc, unit, unit="unit")
