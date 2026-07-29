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

import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.util.element
import test.bootstrap


class TestEditGeoreferencing(test.bootstrap.IFC4):
    def test_editing_georeferencing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 123.45, "Northings": 234.56},
        )
        crs = self.file.by_type("IfcProjectedCRS")[0]
        assert crs.Name == "EPSG:7856"
        conversion = self.file.by_type("IfcMapConversion")[0]
        assert conversion.Eastings == 123.45
        assert conversion.Northings == 234.56

        ifcopenshell.api.georeference.edit_georeferencing(self.file, projected_crs={"Name": "EPSG:1234"})
        assert crs.Name == "EPSG:1234"
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Eastings": 42})
        assert conversion.Eastings == 42


class TestEditGeoreferencingIFC2X3(test.bootstrap.IFC2X3):
    def test_editing_georeferencing(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"Name": "EPSG:7856"},
            coordinate_operation={"Eastings": 123.45, "Northings": 234.56},
        )
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion", verbose=True)
        crs = ifcopenshell.util.element.get_pset(project, "ePSet_ProjectedCRS", verbose=True)
        assert crs["Name"]["value"] == "EPSG:7856"
        assert self.file.by_id(crs["Name"]["id"]).NominalValue.is_a("IfcLabel")
        assert conversion["Eastings"]["value"] == 123.45
        assert self.file.by_id(conversion["Eastings"]["id"]).NominalValue.is_a("IfcLengthMeasure")
        assert conversion["Northings"]["value"] == 234.56
        assert conversion["OrthogonalHeight"]["value"] == 0

    def test_editing_georeferencing_properties_not_seeded_by_add_georeferencing(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={
                "Description": "Amersfoort / RD New",
                "GeodeticDatum": "Amersfoort",
                "VerticalDatum": "NAP",
                "MapProjection": "RD",
                "MapZone": "1",
            },
            coordinate_operation={"XAxisAbscissa": 0.866, "Scale": 0.99956},
        )
        crs = ifcopenshell.util.element.get_pset(project, "ePSet_ProjectedCRS", verbose=True)
        assert self.file.by_id(crs["Description"]["id"]).NominalValue.is_a("IfcText")
        for name in ("GeodeticDatum", "VerticalDatum", "MapProjection", "MapZone"):
            assert self.file.by_id(crs[name]["id"]).NominalValue.is_a("IfcIdentifier")
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion", verbose=True)
        for name in ("XAxisAbscissa", "Scale"):
            assert self.file.by_id(conversion[name]["id"]).NominalValue.is_a("IfcReal")

    def test_editing_a_map_conversion_property_never_seeded_by_add_georeferencing(self):
        # XAxisAbscissa and Scale above are not seeded by add_georeferencing
        # either, but that assertion alone cannot prove the loop wraps values
        # correctly: a raw, unwrapped Python float also falls back to
        # IfcReal in edit_pset's own type inference, so it passes whether or
        # not edit_georeferencing wraps the value at all.
        #
        # Eastings takes the IfcLengthMeasure branch instead, so an unwrapped
        # float would fall back to IfcReal, not IfcLengthMeasure, and this
        # assertion actually distinguishes the two. This simulates an
        # IFC2X3 file authored by another tool: the ePSet_MapConversion
        # pset exists (so edit_georeferencing's own lookup succeeds) but
        # Eastings itself was never seeded by add_georeferencing, so
        # edit_pset must add it as a brand new property instead of
        # inheriting the type of an existing one.
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.pset.add_pset(self.file, project, "ePSet_MapConversion")
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Eastings": 100.0})
        conversion = ifcopenshell.util.element.get_pset(project, "ePSet_MapConversion", verbose=True)
        assert self.file.by_id(conversion["Eastings"]["id"]).NominalValue.is_a("IfcLengthMeasure")
