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

import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.util.element


class TestAddGeoreferencing(test.bootstrap.IFC4):
    def test_adding_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        assert len(self.file.by_type("IfcMapConversion")) == 1
        assert len(self.file.by_type("IfcProjectedCRS")) == 1
        assert (conversion := self.file.by_type("IfcMapConversion")[0])
        assert (crs := self.file.by_type("IfcProjectedCRS")[0])
        assert conversion.Eastings == conversion.Northings == conversion.OrthogonalHeight == 0
        assert crs.Name == "EPSG:3857"

    def test_not_doing_anything_if_no_model_context(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.context.add_context(self.file, "Plan")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        assert len(self.file.by_type("IfcMapConversion")) == 0
        assert len(self.file.by_type("IfcProjectedCRS")) == 0

    def test_not_adding_georeferencing_twice(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        assert len(self.file.by_type("IfcMapConversion")) == 1
        assert len(self.file.by_type("IfcProjectedCRS")) == 1


class TestAddGeoreferencingIFC2X3(test.bootstrap.IFC2X3):
    def test_adding_georeferencing(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion", verbose=True)
        crs = ifcopenshell.util.element.get_pset(project, "ePSet_ProjectedCRS", verbose=True)
        assert len(self.file.by_type("IfcPropertySet")) == 2
        assert conversion
        assert crs
        assert crs["Name"]["value"] == "EPSG:3857"
        assert self.file.by_id(crs["Name"]["id"]).NominalValue.is_a("IfcLabel")
        assert conversion["Eastings"]["value"] == 0
        assert self.file.by_id(conversion["Eastings"]["id"]).NominalValue.is_a("IfcLengthMeasure")
        assert conversion["Northings"]["value"] == 0
        assert conversion["OrthogonalHeight"]["value"] == 0
