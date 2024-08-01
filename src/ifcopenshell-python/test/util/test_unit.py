# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import test.bootstrap
import ifcopenshell.api.unit
import ifcopenshell.api.root
import ifcopenshell.api.georeference
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit as subject
from math import pi


class TestConvert(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.convert(1, None, "METRE", None, "METRE") == 1
        assert subject.convert(1, None, "METRE", "MILLI", "METRE") == 1000
        assert subject.convert(1000, "MILLI", "METRE", None, "METRE") == 1
        assert subject.convert(1, None, "SQUARE_METRE", None, "SQUARE_METRE") == 1
        assert subject.convert(1, None, "SQUARE_METRE", "MILLI", "SQUARE_METRE") == 1000000
        assert subject.convert(1, None, "CUBIC_METRE", "MILLI", "CUBIC_METRE") == 1000000000


class TestCalculateUnitScale(test.bootstrap.IFC4):
    def test_prefix_and_conversion_based_units_are_considered(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="foot")
        length.ConversionFactor.UnitComponent.Prefix = "MILLI"
        ifcopenshell.api.unit.assign_unit(self.file, units=[length])
        assert subject.calculate_unit_scale(self.file) == 0.3048 * 0.001

        angle = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="degree")
        angle.ConversionFactor.UnitComponent.Prefix = "MILLI"
        ifcopenshell.api.unit.assign_unit(self.file, units=[angle])
        assert subject.calculate_unit_scale(self.file, "PLANEANGLEUNIT") == pi / 180 * 0.001


class TestFormatLength(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.format_length(1, 1, decimal_places=0, unit_system="metric") == "1"
        assert subject.format_length(1, 1, decimal_places=2, unit_system="metric") == "1.00"
        assert subject.format_length(3, 5, decimal_places=2, unit_system="metric") == "5.00"
        assert subject.format_length(3.123, 0.01, decimal_places=2, unit_system="metric") == "3.12"

        assert subject.format_length(3, 1, unit_system="imperial", input_unit="foot") == "3'"
        assert subject.format_length(3.5, 1, unit_system="imperial", input_unit="foot") == "3' - 6\""
        assert subject.format_length(3.123, 1, unit_system="imperial", input_unit="foot") == "3' - 1\""
        assert subject.format_length(3.123, 2, unit_system="imperial", input_unit="foot") == "3' - 1 1/2\""
        assert subject.format_length(3.123, 4, unit_system="imperial", input_unit="foot") == "3' - 1 1/2\""
        assert subject.format_length(3.123, 32, unit_system="imperial", input_unit="foot") == "3' - 1 15/32\""
        assert subject.format_length(24, 1, unit_system="imperial", input_unit="inch") == "2'"
        assert subject.format_length(25.23, 1, unit_system="imperial", input_unit="inch") == "2' - 1\""
        assert subject.format_length(25.23, 4, unit_system="imperial", input_unit="inch") == "2' - 1 1/4\""

        assert subject.format_length(3, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '36"'
        assert subject.format_length(3.5, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '42"'
        assert subject.format_length(3.123, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '37"'
        assert (
            subject.format_length(3.123, 2, unit_system="imperial", input_unit="foot", output_unit="inch") == '37 1/2"'
        )
        assert (
            subject.format_length(3.123, 4, unit_system="imperial", input_unit="foot", output_unit="inch") == '37 1/2"'
        )
        assert (
            subject.format_length(3.123, 32, unit_system="imperial", input_unit="foot", output_unit="inch")
            == '37 15/32"'
        )
        assert subject.format_length(24, 1, unit_system="imperial", input_unit="inch", output_unit="inch") == '24"'
        assert subject.format_length(25.23, 1, unit_system="imperial", input_unit="inch", output_unit="inch") == '25"'
        assert (
            subject.format_length(25.23, 4, unit_system="imperial", input_unit="inch", output_unit="inch") == '25 1/4"'
        )


class TestIsAttrType(test.bootstrap.IFC4):
    def test_run(self):
        schema = ifcopenshell.schema_by_name("IFC4")
        declaration = schema.declaration_by_name("IfcPropertySingleValue")
        nominal_value = declaration.attribute_by_index(2).type_of_attribute()
        assert subject.is_attr_type(nominal_value, "IfcValue")
        assert subject.is_attr_type(nominal_value, "IfcLengthMeasure")
        assert not subject.is_attr_type(nominal_value, "IfcLengthMeasure", include_select_types=False)


class TestConvertFileLengthUnits(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"

    def test_converting_map_conversion_if_there_is_no_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Eastings": 10000})
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        assert output.by_type("IfcMapConversion")[0].Eastings == 10

    def test_preserving_enh_if_there_is_a_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        meter = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, projected_crs={"MapUnit": meter}, coordinate_operation={"Eastings": 10, "Scale": 0.001}
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        assert output.by_type("IfcMapConversion")[0].Eastings == 10
        assert output.by_type("IfcMapConversion")[0].Northings == 0
        assert output.by_type("IfcMapConversion")[0].Scale == 1
        assert subject.get_full_unit_name(output.by_type("IfcProjectedCRS")[0].MapUnit) == "METRE"

    def test_preserving_enh_if_there_is_a_map_unit_which_is_also_the_project_default(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        meter = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, projected_crs={"MapUnit": meter}, coordinate_operation={"Eastings": 10, "Scale": 1}
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[meter])
        output = subject.convert_file_length_units(self.file, target_units="MILLIMETER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "MILLIMETRE"
        assert output.by_type("IfcMapConversion")[0].Eastings == 10
        assert output.by_type("IfcMapConversion")[0].Northings == 0
        assert output.by_type("IfcMapConversion")[0].Scale == 0.001
        assert subject.get_full_unit_name(output.by_type("IfcProjectedCRS")[0].MapUnit) == "METRE"

        unit_assignment = subject.get_unit_assignment(output)
        assert len(unit_assignment.Units) == 1


class TestConvertFileLengthUnitsIFC2X3(test.bootstrap.IFC2X3):
    def test_converting_map_conversion_if_there_is_no_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Eastings": 10000})
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
        assert parameters.e == 10

    def test_preserving_enh_if_there_is_a_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        meter = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"MapUnit": subject.get_full_unit_name(meter)},
            coordinate_operation={"Eastings": 10, "Scale": 0.001},
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
        assert parameters.e == 10
        assert parameters.n == 0
        assert parameters.scale == 1
        crs = ifcopenshell.util.element.get_pset(output.by_type("IfcProject")[0], name="ePSet_ProjectedCRS")
        assert crs["MapUnit"] == "METRE"
