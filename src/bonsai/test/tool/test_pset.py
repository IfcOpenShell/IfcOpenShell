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
import ifcopenshell.api
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.pset import Pset as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Pset)


class TestGetElementPset(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo")
        assert subject.get_element_pset(element, "Foo") == pset


class TestIsPsetEmpty(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo")
        assert subject.is_pset_empty(pset) is True
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        assert subject.is_pset_empty(pset) is False
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": None})
        assert subject.is_pset_empty(pset) is True


class TestEditingAnOverriddenUnitPropertyRoundTrips(NewFile):
    def test_run(self):
        # Project default is mm, but this property is authored directly in m.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Test")
        prop = ifc.createIfcPropertySingleValue(
            Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2.5), Unit=length_m
        )
        pset.HasProperties = [prop]

        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        blender_props = obj.PsetProperties
        subject.import_pset_from_existing(pset, blender_props, None)

        metadata = blender_props.properties["Foo"].metadata
        assert metadata.unit_symbol == "m"
        assert metadata.float_value == 2.5  # raw stored value, not rescaled to the project's mm

        # Simulate a user edit in the property editor.
        metadata.float_value = 3.5

        # Simulate what EditPset.execute() does: collect the raw value straight
        # off the metadata and write it back, with no rescaling step.
        properties = {"Foo": metadata.get_value()}
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties=properties)

        assert prop.NominalValue.wrappedValue == 3.5  # not rescaled to 3500mm
        assert prop.Unit == length_m  # override preserved


class TestImportingATemplatedQuantityRespectsItsOwnUnitOverride(NewFile):
    def test_run(self):
        # Regression test: import_pset_from_template's Q_ branch used to
        # unconditionally re-template existing quantities, which shadowed
        # their own Unit override with the project default -- edit mode
        # showed "m" while the read-only panel correctly showed "mm".
        # Project default is m, but this quantity is authored directly in mm.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_m])
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")

        element = ifc.createIfcBeam()
        qto = ifcopenshell.api.pset.add_qto(ifc, product=element, name="Qto_Test")
        quantity = ifc.createIfcQuantityLength(Name="Foo", Unit=length_mm, LengthValue=2500.0)
        qto.Quantities = [quantity]

        pset_template = ifc.createIfcPropertySetTemplate(
            Name="Qto_Test",
            TemplateType="PSET_TYPEDRIVENOVERRIDE",
            ApplicableEntity="IfcBeam",
            HasPropertyTemplates=[ifc.createIfcSimplePropertyTemplate(Name="Foo", TemplateType="Q_LENGTH")],
        )

        obj = bpy.data.objects.new("Beam", None)
        tool.Ifc.link(element, obj)
        blender_props = obj.PsetProperties
        # Mirrors core/pset.py's enable_pset_editing: template pass, then existing-data pass.
        subject.import_pset_from_template(pset_template, qto, blender_props)
        subject.import_pset_from_existing(qto, blender_props, pset_template)

        assert len(blender_props.properties) == 1  # not duplicated by the template pass
        metadata = blender_props.properties["Foo"].metadata
        assert metadata.unit_symbol == "mm"  # the quantity's own override, not the project default "m"
        assert metadata.float_value == 2500.0  # raw stored value, not rescaled
