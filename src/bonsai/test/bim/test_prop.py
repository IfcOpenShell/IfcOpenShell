# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


def import_single_property(ifc, element, prop):
    """Import a single existing IfcProperty into a real, addon-registered
    PsetProperties collection, exactly as the property editor does, and
    return its `metadata` (an `Attribute`)."""
    pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Test")
    pset.HasProperties = [prop]
    obj = bpy.data.objects.new(prop.Name, None)
    tool.Ifc.link(element, obj)
    props = obj.PsetProperties
    tool.Pset.import_pset_from_existing(pset, props, None)
    return props.properties[prop.Name].metadata


class TestGetDisplayName(NewFile):
    def test_appends_the_resolved_unit_symbol(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        pressure = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PRESSUREUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[pressure])

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        assert metadata.display_name == "Foo, Pa"

    def test_falls_back_to_the_plain_name_when_no_unit_is_resolvable(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        # No units assigned to the project at all -- nothing to resolve.

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        assert metadata.unit_symbol == ""
        assert metadata.display_name == "Foo"

    def test_falls_back_to_the_plain_name_for_a_non_measure_property(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcText("Bar"))
        metadata = import_single_property(ifc, element, prop)

        assert metadata.unit_symbol == ""
        assert metadata.display_name == "Foo"
