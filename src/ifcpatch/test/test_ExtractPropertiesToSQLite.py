# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import sqlite3

import ifcopenshell.api.material
import ifcopenshell.api.root

import ifcpatch
import test.bootstrap


class ExtractPropertiesToSQLiteMixin:
    def test_run(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall", name="Wall")
        db_path = ifcpatch.execute({"file": self.file, "recipe": "ExtractPropertiesToSQLite", "arguments": []})
        db = sqlite3.connect(db_path)
        rows = db.execute("SELECT global_id, ifc_class FROM elements WHERE ifc_class = 'IfcWall'").fetchall()
        assert rows == [(wall.GlobalId, "IfcWall")]

    def test_material_layer_without_material_does_not_crash(self):
        # Regression test: IfcMaterialLayer.Material is OPTIONAL. A layer set
        # containing a layer with no Material assigned used to raise
        # AttributeError: 'NoneType' object has no attribute 'Name', aborting
        # the whole extraction.
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        layer_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        layer = self.file.create_entity("IfcMaterialLayer", Material=None, LayerThickness=0.1)
        layer_set.MaterialLayers = [layer]
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialLayerSet", material=layer_set
        )

        db_path = ifcpatch.execute({"file": self.file, "recipe": "ExtractPropertiesToSQLite", "arguments": []})

        db = sqlite3.connect(db_path)
        names = {row[0] for row in db.execute("SELECT name FROM properties WHERE set_name = 'IFC Material'")}
        assert "Layer 1 Material" not in names


class TestExtractPropertiesToSQLite(test.bootstrap.IFC4, ExtractPropertiesToSQLiteMixin):
    def test_material_profile_without_material_does_not_crash(self):
        # Same optional-attribute defect as above, for IfcMaterialProfile.Material.
        # IfcMaterialProfileSet is IFC4+, so this is not run against IFC2X3.
        beam = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBeam")
        profile_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialProfileSet")
        profile_def = self.file.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=0.1, YDim=0.2)
        profile = self.file.create_entity("IfcMaterialProfile", Material=None, Profile=profile_def)
        profile_set.MaterialProfiles = [profile]
        ifcopenshell.api.material.assign_material(
            self.file, products=[beam], type="IfcMaterialProfileSet", material=profile_set
        )

        db_path = ifcpatch.execute({"file": self.file, "recipe": "ExtractPropertiesToSQLite", "arguments": []})

        db = sqlite3.connect(db_path)
        names = {row[0] for row in db.execute("SELECT name FROM properties WHERE set_name = 'IFC Material'")}
        assert "Profile 1 Material" not in names


class TestExtractPropertiesToSQLiteIFC2X3(test.bootstrap.IFC2X3, ExtractPropertiesToSQLiteMixin):
    pass
