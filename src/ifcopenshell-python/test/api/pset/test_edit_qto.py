# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.pset
import ifcopenshell.api.root
import test.bootstrap


class TestEditQto(test.bootstrap.IFC4):
    def test_editing_a_blank_buildingsmart_templated_qto(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Qto_WallBaseQuantities")
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={"Length": 1, "NetSideArea": 2, "NetVolume": 3},
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert pset.Quantities[0].Name == "Length"
        assert pset.Quantities[0].LengthValue == 1

        assert pset.Quantities[1].Name == "NetSideArea"
        assert pset.Quantities[1].AreaValue == 2

        assert pset.Quantities[2].Name == "NetVolume"
        assert pset.Quantities[2].VolumeValue == 3

    def test_editing_an_existing_buildingsmart_templated_pset(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Qto_WallBaseQuantities")
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={"Length": 1, "NetSideArea": 2, "NetVolume": 3},
        )
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"Length": 42, "NetSideArea": None})
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert qto.Quantities[0].Name == "Length"
        assert qto.Quantities[0].LengthValue == 42

        assert qto.Quantities[1].Name == "NetVolume"
        assert qto.Quantities[1].VolumeValue == 3

        assert len(qto.Quantities) == 2

    def test_not_adding_a_property_if_it_is_none(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Qto_WallBaseQuantities")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"Length": None})
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(qto.Quantities) == 0

    def test_editing_a_qto_name(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="foo")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, name="bar")
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert qto.Name == "bar"

    def test_adding_quantities_without_a_template_with_autodetected_and_manual_data_types(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={
                "MyArea": self.file.createIfcAreaMeasure(1),
                "MyCount": self.file.createIfcCountMeasure(2),
                "MyLength": self.file.createIfcLengthMeasure(3),
                "MyTime": self.file.createIfcTimeMeasure(5),
                "MyVolume": self.file.createIfcVolumeMeasure(6),
                "MyWeight": self.file.createIfcMassMeasure(7),
            },
        )
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert qto.Quantities[0].Name == "MyArea"
        assert qto.Quantities[0].AreaValue == 1

        assert qto.Quantities[1].Name == "MyCount"
        assert qto.Quantities[1].CountValue == 2

        assert qto.Quantities[2].Name == "MyLength"
        assert qto.Quantities[2].LengthValue == 3

        assert qto.Quantities[3].Name == "MyTime"
        assert qto.Quantities[3].TimeValue == 5

        assert qto.Quantities[4].Name == "MyVolume"
        assert qto.Quantities[4].VolumeValue == 6

        assert qto.Quantities[5].Name == "MyWeight"
        assert qto.Quantities[5].WeightValue == 7

    def test_editing_quantities_with_autodetected_existing_types(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={
                "MyLength": self.file.createIfcLengthMeasure(12),
            },
        )
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={
                "MyLength": 34,
            },
        )
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert qto.Quantities[0].Name == "MyLength"
        assert qto.Quantities[0].LengthValue == 34

    def test_editing_properties_with_an_explicit_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={
                "MyLength": self.file.createIfcLengthMeasure(12),
            },
        )
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={
                "MyLength": self.file.createIfcAreaMeasure(34),
            },
        )
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert qto.Quantities[0].Name == "MyLength"
        assert qto.Quantities[0].LengthValue == 34

    def test_adding_a_new_quantity_with_a_custom_unit(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        custom_unit = self.file.createIfcSIUnit(UnitType="LENGTHUNIT", Prefix="MILLI", Name="METRE")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(
            self.file, qto=qto, properties={"MyLength": {"NominalValue": 30.0, "Unit": custom_unit}}
        )
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert qto.Quantities[0].Name == "MyLength"
        assert qto.Quantities[0].LengthValue == 30.0
        assert qto.Quantities[0].Unit == custom_unit

    def test_editing_an_existing_quantitys_unit(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        custom_unit = self.file.createIfcSIUnit(UnitType="LENGTHUNIT", Prefix="MILLI", Name="METRE")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"MyLength": 12.0})
        quantity = qto.Quantities[0]
        assert quantity.Unit is None

        ifcopenshell.api.pset.edit_qto(
            self.file, qto=qto, properties={"MyLength": {"NominalValue": 30.0, "Unit": custom_unit}}
        )
        assert quantity.Unit == custom_unit
        assert quantity.LengthValue == 30.0

    def test_explicitly_clearing_a_quantitys_unit_override(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        custom_unit = self.file.createIfcSIUnit(UnitType="LENGTHUNIT", Prefix="MILLI", Name="METRE")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(
            self.file, qto=qto, properties={"MyLength": {"NominalValue": 30.0, "Unit": custom_unit}}
        )
        quantity = qto.Quantities[0]
        assert quantity.Unit == custom_unit

        ifcopenshell.api.pset.edit_qto(
            self.file, qto=qto, properties={"MyLength": {"NominalValue": 40.0, "Unit": None}}
        )
        assert quantity.Unit is None
        assert quantity.LengthValue == 40.0

    def test_a_bare_value_does_not_disturb_an_existing_units_override(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        custom_unit = self.file.createIfcSIUnit(UnitType="LENGTHUNIT", Prefix="MILLI", Name="METRE")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(
            self.file, qto=qto, properties={"MyLength": {"NominalValue": 30.0, "Unit": custom_unit}}
        )
        quantity = qto.Quantities[0]
        assert quantity.Unit == custom_unit

        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"MyLength": 42.0})
        assert quantity.Unit == custom_unit
        assert quantity.LengthValue == 42.0

    def test_complex_quantity_editing_is_unaffected_by_the_unit_wrapper_convention(self):
        # Regression guard: dict values are already overloaded to mean "this is an
        # IfcPhysicalComplexQuantity spec" ({"Discrimination": ..., "HasQuantities": ...}).
        # The new {"Unit": ..., "NominalValue": ...} convention must not be confused with it.
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={"Layers": {"Discrimination": "layer", "HasQuantities": {"Width": 5.0}}},
        )
        qto = element.IsDefinedBy[0].RelatingPropertyDefinition
        complex_qty = qto.Quantities[0]
        assert complex_qty.is_a("IfcPhysicalComplexQuantity")
        assert complex_qty.Name == "Layers"
        assert complex_qty.Discrimination == "layer"
        assert complex_qty.HasQuantities[0].Name == "Width"
        assert complex_qty.HasQuantities[0].LengthValue == 5.0

        # Editing it again (update_existing_property's complex-quantity branch) still works too.
        ifcopenshell.api.pset.edit_qto(
            self.file,
            qto=qto,
            properties={"Layers": {"Discrimination": "layer2", "HasQuantities": {"Width": 6.0}}},
        )
        assert complex_qty.Discrimination == "layer2"
        assert complex_qty.HasQuantities[0].LengthValue == 6.0
