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

import ifcpatch
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.util.element
import test.bootstrap


class TestConvertPropertiesToQuantities(test.bootstrap.IFC4):
    def test_run(self):
        TEST_DATA = {
            "IFC2X3": ("IfcWall", "Qto_WallBaseQuantities", "Area", "NetSideArea"),
            "IFC4": ("IfcWall", "Qto_WallBaseQuantities", "Area", "NetSideArea"),
            "IFC4X3": ("IfcRail", "Qto_RailBaseQuantities", "RailLength", "Length"),
        }

        ifc_class, qto_name, source_quantity_name, destination_quantity_name = TEST_DATA[self.file.schema]

        element = ifcopenshell.api.root.create_entity(self.file, ifc_class=ifc_class)
        pset_name = "Foo_Bar"
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foo_Bar")
        pset_data = {source_quantity_name: 25.0}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=pset_data)

        output = ifcpatch.execute(
            {
                "file": self.file,
                "recipe": "ConvertPropertiesToQuantities",
                "arguments": [source_quantity_name, destination_quantity_name],
            }
        )
        assert isinstance(output, ifcopenshell.file)

        new_element = output.by_type(ifc_class)[0]
        psets = ifcopenshell.util.element.get_psets(new_element, psets_only=True)
        del psets[pset_name]["id"]
        assert psets == {"Foo_Bar": pset_data}

        qtos = ifcopenshell.util.element.get_psets(new_element, qtos_only=True)
        del qtos[qto_name]["id"]
        assert qtos == {qto_name: {destination_quantity_name: 25}}


class TestConvertPropertiesToQuantitiesIFC2X3(test.bootstrap.IFC2X3, TestConvertPropertiesToQuantities):
    pass


class TestConvertPropertiesToQuantitiesIFC4X3(test.bootstrap.IFC4X3, TestConvertPropertiesToQuantities):
    pass
