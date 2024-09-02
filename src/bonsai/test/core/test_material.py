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

import bonsai.core.material as subject
from test.core.bootstrap import ifc, material, style, spatial


class TestAddMaterial:
    def test_add_a_material(self, ifc, material):
        ifc.run(
            "material.add_material", name="name", category="category", description="description"
        ).should_be_called().will_return("material")
        material.is_editing_materials().should_be_called().will_return(False)
        assert (
            subject.add_material(ifc, material, name="name", category="category", description="description")
            == "material"
        )

    def test_reloading_imported_materials_if_you_are_editing_scene_materials(self, ifc, material):
        ifc.run(
            "material.add_material", name="name", category="category", description="description"
        ).should_be_called().will_return("material")
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        assert (
            subject.add_material(ifc, material, name="name", category="category", description="description")
            == "material"
        )


class TestAddMaterialSet:
    def test_adding_a_material_set(self, ifc, material):
        ifc.run("material.add_material_set", name="Unnamed", set_type="set_type").should_be_called().will_return(
            "material"
        )
        material.ensure_new_material_set_is_valid("material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(False)
        assert subject.add_material_set(ifc, material, set_type="set_type") == "material"

    def test_adding_a_material_set_and_reloading_imported_materials(self, ifc, material):
        ifc.run("material.add_material_set", name="Unnamed", set_type="set_type").should_be_called().will_return(
            "material"
        )
        material.ensure_new_material_set_is_valid("material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        assert subject.add_material_set(ifc, material, set_type="set_type") == "material"


class TestRemoveMaterial:
    def test_removing_a_material(self, ifc, material):
        material.is_material_used_in_sets("material").should_be_called().will_return(False)
        ifc.run("material.remove_material", material="material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(False)
        subject.remove_material(ifc, material, material="material")

    def test_removing_a_material_and_reloading_imported_materials(self, ifc, material):
        material.is_material_used_in_sets("material").should_be_called().will_return(False)
        ifc.run("material.remove_material", material="material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        subject.remove_material(ifc, material, material="material")

    def test_not_removing_a_material_if_it_is_used_in_a_material_set(self, ifc, material):
        material.is_material_used_in_sets("material").should_be_called().will_return(True)
        subject.remove_material(ifc, material, material="material")


class TestRemoveMaterialSet:
    def test_run(self, ifc, material):
        ifc.run("material.remove_material_set", material="material").should_be_called()
        material.is_editing_materials().should_be_called().will_return(True)
        material.get_active_material_type().should_be_called().will_return("material_type")
        material.import_material_definitions("material_type").should_be_called()
        subject.remove_material_set(ifc, material, material="material")


class TestLoadMaterials:
    def test_run(self, material):
        material.import_material_definitions("material_type").should_be_called()
        material.enable_editing_materials().should_be_called()
        subject.load_materials(material, "material_type")


class TestDisableEditingMaterials:
    def test_run(self, material):
        material.disable_editing_materials().should_be_called()
        subject.disable_editing_materials(material)


class TestSelectByMaterial:
    def test_run(self, material, spatial):
        material.get_elements_by_material("material").should_be_called().will_return("elements")
        spatial.select_products("elements").should_be_called()
        subject.select_by_material(material, spatial, material="material")
