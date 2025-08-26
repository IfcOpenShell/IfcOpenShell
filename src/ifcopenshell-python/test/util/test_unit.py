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
import numpy as np
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.api.root
import ifcopenshell.api.georeference
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit as subject
from ifcopenshell.util.shape_builder import ShapeBuilder
from math import pi


class TestCacheUnits(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        assert self.file.units == {}
        subject.cache_units(self.file)
        assert self.file.units == {"LENGTHUNIT": length, "AREAUNIT": area}


class TestClearUnitCache(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        subject.cache_units(self.file)
        subject.clear_unit_cache(self.file)
        assert self.file.units == {}


class TestGetProjectUnit(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        assert subject.get_project_unit(self.file, "LENGTHUNIT") == length
        assert subject.get_project_unit(self.file, "AREAUNIT") == area

    def test_using_a_cache(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        assert self.file.units == {}
        assert subject.get_project_unit(self.file, "LENGTHUNIT", use_cache=True) == length
        assert self.file.units == {"LENGTHUNIT": length, "AREAUNIT": area}
        ifcopenshell.api.unit.assign_unit(self.file, units=[length2])
        assert subject.get_project_unit(self.file, "LENGTHUNIT", use_cache=True) == length
        subject.clear_unit_cache(self.file)
        assert subject.get_project_unit(self.file, "LENGTHUNIT", use_cache=True) == length2
        assert self.file.units == {"LENGTHUNIT": length2, "AREAUNIT": area}


class TestGetPropertyUnit(test.bootstrap.IFC4):
    def test_no_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        prop = self.file.createIfcQuantityLength(Name="Foo", LengthValue=42.0)
        assert subject.get_property_unit(prop, self.file) is None

    def test_simple_quantity(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcQuantityLength(Name="Foo", LengthValue=42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2

    def test_single_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertySingleValue(Name="Foo", NominalValue=self.file.createIfcLengthMeasure(42.0))
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2

    def test_enumerated_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertyEnumeratedValue(
            Name="Foo", EnumerationValues=[self.file.createIfcLengthMeasure(42.0)]
        )
        assert subject.get_property_unit(prop, self.file) == length
        prop.EnumerationValues = []
        prop.EnumerationReference = self.file.createIfcPropertyEnumeration(
            "Foo", [self.file.createIfcAreaMeasure(42.0)]
        )
        assert subject.get_property_unit(prop, self.file) == area
        prop.EnumerationReference = self.file.createIfcPropertyEnumeration(
            "Foo", [self.file.createIfcAreaMeasure(42.0)], Unit=length2
        )
        assert subject.get_property_unit(prop, self.file) == length2
        prop.EnumerationValues = [self.file.createIfcAreaMeasure(42.0)]
        assert subject.get_property_unit(prop, self.file) == length2
        prop.EnumerationReference.Unit = None
        assert subject.get_property_unit(prop, self.file) == area

    def test_list_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertyListValue(Name="Foo", ListValues=[self.file.createIfcLengthMeasure(42.0)])
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2
        prop.Unit = None
        prop.ListValues = []
        assert subject.get_property_unit(prop, self.file) is None

    def test_bounded_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertyBoundedValue(Name="Foo")
        assert subject.get_property_unit(prop, self.file) is None
        prop.UpperBoundValue = self.file.createIfcLengthMeasure(42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.UpperBoundValue = None
        prop.LowerBoundValue = self.file.createIfcLengthMeasure(42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.LowerBoundValue = None
        prop.SetPointValue = self.file.createIfcLengthMeasure(42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2


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
        declaration = schema.declaration_by_name("IfcPropertySingleValue").as_entity()
        assert declaration
        nominal_value = declaration.attribute_by_index(2).type_of_attribute()
        assert subject.is_attr_type(nominal_value, "IfcValue")
        assert subject.is_attr_type(nominal_value, "IfcLengthMeasure")
        assert not subject.is_attr_type(nominal_value, "IfcLengthMeasure", include_select_types=False)


class TestConvertFileLengthUnits(test.bootstrap.IFC2X3):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"

    def test_attribute_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")

        builder = ShapeBuilder(self.file)
        rectangle = builder.rectangle((100, 100))
        extrusion = builder.extrude(rectangle, 1000)

        # IfcLengthMeasure entities.
        product = ifcopenshell.api.root.create_entity(self.file, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product, "TestPset")
        # Consider weird case when same entity is reused.
        length_measure = self.file.create_entity("IfcLengthMeasure", 50.0)
        enum_property = self.file.create_entity(
            "IfcPropertyEnumeratedValue",
            Name="Enum",
            # Not entirely sure if there are real life cases when mixed typed entities used in the list
            # but just to be safe.
            EnumerationValues=[
                length_measure,
                self.file.create_entity("IfcLabel", "TEXT"),
                self.file.create_entity("IfcLengthMeasure", 250.0),
                length_measure,
            ],
        )
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset,
            properties={
                "Length": self.file.create_entity("IfcLengthMeasure", 25.0),
                "Enum": enum_property,
            },
        )

        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        extrusion = output.by_type("IfcExtrudedAreaSolid")[0]

        # Simple float attribute.
        assert extrusion.Depth == 1

        # List of floats in IFC2X3 and list of lists of floats in IFC4+.
        rectangle = extrusion.SweptArea.OuterCurve
        expected_points = [(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1)]
        if self.file.schema == "IFC2X3":
            # IfcPolyline.
            points = [p.Coordinates for p in rectangle.Points]
            expected_points += expected_points[:1]
        else:
            # IfcIndexedPolyCurve.
            points = rectangle.Points.CoordList
        assert np.allclose(points, expected_points)

        # IfcLengthMeasure entities.
        product = output.by_type("IfcWall")[0]
        pset_data = ifcopenshell.util.element.get_pset(product, "TestPset")
        assert pset_data["Length"] == 0.025
        assert pset_data["Enum"] == [0.05, "TEXT", 0.25, 0.05]

    def test_converting_map_conversion_if_there_is_no_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Eastings": 10000})
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        if self.file.schema == "IFC2X3":
            parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
            assert parameters
            assert parameters.e == 10
        else:
            assert output.by_type("IfcMapConversion")[0].Eastings == 10

    def test_preserving_enh_if_there_is_a_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        meter = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        map_unit = subject.get_full_unit_name(meter) if self.file.schema == "IFC2X3" else meter
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"MapUnit": map_unit},
            coordinate_operation={"Eastings": 10, "Scale": 0.001},
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        if self.file.schema == "IFC2X3":
            parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
            assert parameters
            assert parameters.e == 10
            assert parameters.n == 0
            assert parameters.scale == 1
            crs = ifcopenshell.util.element.get_pset(output.by_type("IfcProject")[0], name="ePSet_ProjectedCRS")
            assert crs["MapUnit"] == "METRE"
        else:
            map_conversion = output.by_type("IfcMapConversion")[0]
            assert map_conversion.Eastings == 10
            assert map_conversion.Northings == 0
            assert map_conversion.Scale == 1
            assert subject.get_full_unit_name(output.by_type("IfcProjectedCRS")[0].MapUnit) == "METRE"

    def test_preserving_enh_if_there_is_a_map_unit_which_is_also_the_project_default(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        meter = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        map_unit = subject.get_full_unit_name(meter) if self.file.schema == "IFC2X3" else meter
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"MapUnit": map_unit},
            coordinate_operation={"Eastings": 10, "Scale": 1},
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[meter])
        output = subject.convert_file_length_units(self.file, target_units="MILLIMETER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "MILLIMETRE"
        if self.file.schema == "IFC2X3":
            parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
            assert parameters
            assert parameters.e == 10
            assert parameters.n == 0
            assert parameters.scale == 1
            crs = ifcopenshell.util.element.get_pset(output.by_type("IfcProject")[0], name="ePSet_ProjectedCRS")
            assert crs["MapUnit"] == "METRE"
        else:
            map_conversion = output.by_type("IfcMapConversion")[0]
            assert map_conversion.Eastings == 10
            assert map_conversion.Northings == 0
            assert map_conversion.Scale == 0.001
            assert subject.get_full_unit_name(output.by_type("IfcProjectedCRS")[0].MapUnit) == "METRE"

        unit_assignment = subject.get_unit_assignment(output)
        assert unit_assignment
        assert len(unit_assignment.Units) == 1


class TestConvertFileLengthUnitsIFC4(test.bootstrap.IFC4, TestConvertFileLengthUnits):
    pass


class TestConvertFileLengthUnitsIFC4X3(test.bootstrap.IFC4X3, TestConvertFileLengthUnits):
    pass
