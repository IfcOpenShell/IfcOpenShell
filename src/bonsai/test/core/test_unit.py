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
        unit.is_scene_unit_metric().should_be_called().will_return(True)
        unit.get_scene_unit_si_prefix("LENGTHUNIT").should_be_called().will_return("prefix")
        unit.get_scene_unit_si_prefix("AREAUNIT").should_be_called().will_return("prefix")
        unit.get_scene_unit_si_prefix("VOLUMEUNIT").should_be_called().will_return("prefix")
        unit.get_scene_unit_si_prefix("MASSUNIT").should_be_called().will_return("KILO")
        unit.get_scene_unit_si_prefix("TIMEUNIT").should_be_called().will_return(None)

        ifc.run("unit.add_si_unit", unit_type="LENGTHUNIT", prefix="prefix").should_be_called().will_return(
            "lengthunit"
        )

        ifc.run("unit.add_si_unit", unit_type="AREAUNIT", prefix="prefix").should_be_called().will_return("areaunit")

        ifc.run("unit.add_si_unit", unit_type="VOLUMEUNIT", prefix="prefix").should_be_called().will_return(
            "volumeunit"
        )

        ifc.run("unit.add_conversion_based_unit", name="degree").should_be_called().will_return("planeangleunit")

        ifc.run("unit.add_si_unit", unit_type="MASSUNIT", prefix="KILO").should_be_called().will_return("massunit")

        ifc.run("unit.add_si_unit", unit_type="TIMEUNIT", prefix=None).should_be_called().will_return("timeunit")

        ifc.run(
            "unit.assign_unit", units=["lengthunit", "areaunit", "volumeunit", "planeangleunit", "massunit", "timeunit"]
        ).should_be_called()
        subject.assign_scene_units(ifc, unit)

    def test_creating_and_assigning_imperial_units(self, ifc, unit):
        unit.is_scene_unit_metric().should_be_called().will_return(False)
        unit.get_scene_unit_name("LENGTHUNIT").should_be_called().will_return("lengthname")
        ifc.run("unit.add_conversion_based_unit", name="lengthname").should_be_called().will_return("lengthunit")

        unit.get_scene_unit_name("AREAUNIT").should_be_called().will_return("areaname")
        ifc.run("unit.add_conversion_based_unit", name="areaname").should_be_called().will_return("areaunit")

        unit.get_scene_unit_name("VOLUMEUNIT").should_be_called().will_return("volumename")
        ifc.run("unit.add_conversion_based_unit", name="volumename").should_be_called().will_return("volumeunit")

        ifc.run("unit.add_conversion_based_unit", name="degree").should_be_called().will_return("planeangleunit")

        unit.get_scene_unit_name("MASSUNIT").should_be_called().will_return("massname")
        ifc.run("unit.add_conversion_based_unit", name="massname").should_be_called().will_return("massunit")

        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return("timename")
        ifc.run("unit.add_conversion_based_unit", name="timename").should_be_called().will_return("timeunit")

        ifc.run(
            "unit.assign_unit", units=["lengthunit", "areaunit", "volumeunit", "planeangleunit", "massunit", "timeunit"]
        ).should_be_called()
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


class TestAssignSceneUnitsWithMassAndTime:
    def test_creating_and_assigning_metric_units_with_mass_and_time(self, ifc, unit):
        unit.is_scene_unit_metric().should_be_called().will_return(True)
        unit.get_scene_unit_si_prefix("LENGTHUNIT").should_be_called().will_return("prefix")
        unit.get_scene_unit_si_prefix("AREAUNIT").should_be_called().will_return("prefix")
        unit.get_scene_unit_si_prefix("VOLUMEUNIT").should_be_called().will_return("prefix")
        unit.get_scene_unit_si_prefix("MASSUNIT").should_be_called().will_return("KILO")
        unit.get_scene_unit_si_prefix("TIMEUNIT").should_be_called().will_return("CONVERSION")
        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return("minute")

        ifc.run("unit.add_si_unit", unit_type="LENGTHUNIT", prefix="prefix").should_be_called().will_return(
            "lengthunit"
        )
        ifc.run("unit.add_si_unit", unit_type="AREAUNIT", prefix="prefix").should_be_called().will_return("areaunit")
        ifc.run("unit.add_si_unit", unit_type="VOLUMEUNIT", prefix="prefix").should_be_called().will_return(
            "volumeunit"
        )
        ifc.run("unit.add_si_unit", unit_type="MASSUNIT", prefix="KILO").should_be_called().will_return("massunit")
        ifc.run("unit.add_conversion_based_unit", name="minute").should_be_called().will_return("timeunit")
        ifc.run("unit.add_conversion_based_unit", name="degree").should_be_called().will_return("planeangleunit")

        ifc.run(
            "unit.assign_unit", units=["lengthunit", "areaunit", "volumeunit", "planeangleunit", "massunit", "timeunit"]
        ).should_be_called()
        subject.assign_scene_units(ifc, unit)

    def test_creating_and_assigning_imperial_units_with_mass_and_time(self, ifc, unit):
        unit.is_scene_unit_metric().should_be_called().will_return(False)
        unit.get_scene_unit_name("LENGTHUNIT").should_be_called().will_return("foot")
        unit.get_scene_unit_name("AREAUNIT").should_be_called().will_return("square foot")
        unit.get_scene_unit_name("VOLUMEUNIT").should_be_called().will_return("cubic foot")
        unit.get_scene_unit_name("MASSUNIT").should_be_called().will_return("pound")
        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return("SECOND")

        ifc.run("unit.add_conversion_based_unit", name="foot").should_be_called().will_return("lengthunit")
        ifc.run("unit.add_conversion_based_unit", name="square foot").should_be_called().will_return("areaunit")
        ifc.run("unit.add_conversion_based_unit", name="cubic foot").should_be_called().will_return("volumeunit")
        ifc.run("unit.add_conversion_based_unit", name="pound").should_be_called().will_return("massunit")
        ifc.run("unit.add_si_unit", unit_type="TIMEUNIT", prefix=None).should_be_called().will_return("timeunit")
        ifc.run("unit.add_conversion_based_unit", name="degree").should_be_called().will_return("planeangleunit")

        ifc.run(
            "unit.assign_unit", units=["lengthunit", "areaunit", "volumeunit", "planeangleunit", "massunit", "timeunit"]
        ).should_be_called()
        subject.assign_scene_units(ifc, unit)

    def test_creating_and_assigning_conversion_based_mass_units(self, ifc, unit):
        unit.is_scene_unit_metric().should_be_called().will_return(False)
        unit.get_scene_unit_name("LENGTHUNIT").should_be_called().will_return("foot")
        unit.get_scene_unit_name("AREAUNIT").should_be_called().will_return("square foot")
        unit.get_scene_unit_name("VOLUMEUNIT").should_be_called().will_return("cubic foot")
        unit.get_scene_unit_name("MASSUNIT").should_be_called().will_return("tonne")
        unit.get_scene_unit_name("TIMEUNIT").should_be_called().will_return("minute")

        ifc.run("unit.add_conversion_based_unit", name="foot").should_be_called().will_return("lengthunit")
        ifc.run("unit.add_conversion_based_unit", name="square foot").should_be_called().will_return("areaunit")
        ifc.run("unit.add_conversion_based_unit", name="cubic foot").should_be_called().will_return("volumeunit")
        ifc.run("unit.add_conversion_based_unit", name="tonne").should_be_called().will_return("massunit")
        ifc.run("unit.add_conversion_based_unit", name="minute").should_be_called().will_return("timeunit")
        ifc.run("unit.add_conversion_based_unit", name="degree").should_be_called().will_return("planeangleunit")

        ifc.run(
            "unit.assign_unit", units=["lengthunit", "areaunit", "volumeunit", "planeangleunit", "massunit", "timeunit"]
        ).should_be_called()
        subject.assign_scene_units(ifc, unit)


class TestAddTimeUnit:
    def test_adding_si_time_unit(self, ifc, unit):
        ifc.run("unit.add_si_unit", unit_type="TIMEUNIT").should_be_called().will_return("unit")
        unit.import_units().should_be_called()
        assert subject.add_si_unit(ifc, unit, unit_type="TIMEUNIT") == "unit"

    def test_adding_conversion_based_time_unit_minute(self, ifc, unit):
        ifc.run("unit.add_conversion_based_unit", name="minute").should_be_called().will_return("unit")
        unit.import_units().should_be_called()
        assert subject.add_conversion_based_unit(ifc, unit, name="minute") == "unit"

    def test_adding_conversion_based_time_unit_hour(self, ifc, unit):
        ifc.run("unit.add_conversion_based_unit", name="hour").should_be_called().will_return("unit")
        unit.import_units().should_be_called()
        assert subject.add_conversion_based_unit(ifc, unit, name="hour") == "unit"

    def test_adding_conversion_based_time_unit_day(self, ifc, unit):
        ifc.run("unit.add_conversion_based_unit", name="day").should_be_called().will_return("unit")
        unit.import_units().should_be_called()
        assert subject.add_conversion_based_unit(ifc, unit, name="day") == "unit"


class TestAssignMassAndTimeUnits:
    def test_assigning_mass_unit(self, ifc, unit):
        ifc.run("unit.assign_unit", units=["massunit"]).should_be_called()
        unit.import_units().should_be_called()
        subject.assign_unit(ifc, unit, unit="massunit")

    def test_assigning_time_unit(self, ifc, unit):
        ifc.run("unit.assign_unit", units=["timeunit"]).should_be_called()
        unit.import_units().should_be_called()
        subject.assign_unit(ifc, unit, unit="timeunit")

    def test_assigning_multiple_mass_and_time_units(self, ifc, unit):
        ifc.run("unit.assign_unit", units=["massunit"]).should_be_called()
        unit.import_units().should_be_called()
        ifc.run("unit.assign_unit", units=["timeunit"]).should_be_called()
        unit.import_units().should_be_called()

        subject.assign_unit(ifc, unit, unit="massunit")
        subject.assign_unit(ifc, unit, unit="timeunit")


class TestUnassignMassAndTimeUnits:
    def test_unassigning_mass_unit(self, ifc, unit):
        ifc.run("unit.unassign_unit", units=["massunit"]).should_be_called()
        unit.import_units().should_be_called()
        subject.unassign_unit(ifc, unit, unit="massunit")

    def test_unassigning_time_unit(self, ifc, unit):
        ifc.run("unit.unassign_unit", units=["timeunit"]).should_be_called()
        unit.import_units().should_be_called()
        subject.unassign_unit(ifc, unit, unit="timeunit")


class TestRemoveMassAndTimeUnits:
    def test_removing_mass_unit(self, ifc, unit):
        ifc.run("unit.remove_unit", unit="massunit").should_be_called()
        unit.import_units().should_be_called()
        subject.remove_unit(ifc, unit, unit="massunit")

    def test_removing_time_unit(self, ifc, unit):
        ifc.run("unit.remove_unit", unit="timeunit").should_be_called()
        unit.import_units().should_be_called()
        subject.remove_unit(ifc, unit, unit="timeunit")
