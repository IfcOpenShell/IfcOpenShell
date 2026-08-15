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

import json
import os
import tempfile

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.representation

import ifcdiff


def setup_project() -> ifcopenshell.file:
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
    ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])
    model = ifcopenshell.api.context.add_context(ifc_file, "Model")
    ifcopenshell.api.context.add_context(ifc_file, "Model", "Body", "MODEL_VIEW", parent=model)
    return ifc_file


def setup_spatial_tree(ifc_file: ifcopenshell.file) -> tuple[ifcopenshell.entity_instance, ...]:
    """Aggregate a Project > Site > Building > (Level 1, Level 2) tree."""
    project = ifc_file.by_type("IfcProject")[0]
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding", name="Building")
    level_1 = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Level 1")
    level_2 = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Level 2")
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[level_1, level_2], relating_object=building)
    return site, building, level_1, level_2


class TestIfcDiff:
    def test_add_element(self):
        ifc_file = setup_project()

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall = ifcopenshell.api.root.create_entity(new_file, ifc_class="IfcWall")

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file)
        ifc_diff.diff()
        assert ifc_diff.added_elements == {wall.GlobalId}
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {}

    def test_remove_element(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        ifcopenshell.api.root.remove_product(new_file, wall_new)

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file)
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == {wall.GlobalId}
        assert ifc_diff.change_register == {}

    def test_changed_attribute(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        wall_new.Name = "Bar"

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["attributes"])
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {wall.GlobalId: {"attributes_changed": True}}

    def test_changed_predefined_type_is_caught_by_default(self):
        # Regression test for #8214: a plain diff (no relationships specified)
        # must report a modified or removed PredefinedType. Previously the
        # default only compared geometry, so attribute-only edits were missed.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        wall.PredefinedType = "SOLIDWALL"

        new_file = ifc_file.from_string(ifc_file.to_string())
        new_file.by_id(wall.id()).PredefinedType = "NOTDEFINED"

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file)
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {wall.GlobalId: {"attributes_changed": True}}

    def test_property_diff_exports_to_json(self):
        # Regression test for #8905: comparing "property" relationships makes
        # DeepDiff report a dictionary_item_added as a SetOrdered, which
        # json.dump couldn't serialise, crashing export() with no results.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        pset = ifcopenshell.api.pset.add_pset(new_file, product=wall_new, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(new_file, pset=pset, properties={"FireRating": "2HR"})

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["property"])
        ifc_diff.diff()
        assert ifc_diff.change_register[wall.GlobalId]["properties_changed"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            output = os.path.join(tmp_dir, "diff.json")
            ifc_diff.export(output)
            with open(output) as f:
                results = json.load(f)
            assert "Pset_WallCommon" in str(results["changed"][wall.GlobalId]["properties_changed"])

    def test_unchanged_container_is_not_a_change(self):
        # Regression test for #4110: the container check compared the entity
        # instances returned by get_container. They belong to two different
        # ifcopenshell.file objects and so never compare equal, meaning every
        # contained element was reported as changed even when it had not moved.
        ifc_file = setup_project()
        _, _, level_1, _ = setup_spatial_tree(ifc_file)
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        ifcopenshell.api.spatial.assign_container(ifc_file, products=[wall], relating_structure=level_1)

        new_file = ifc_file.from_string(ifc_file.to_string())

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["container"])
        ifc_diff.diff()
        assert ifc_diff.change_register == {}

    def test_unchanged_aggregate_is_not_a_change(self):
        # Regression test for #4110, the same defect on the aggregate check.
        ifc_file = setup_project()
        setup_spatial_tree(ifc_file)

        new_file = ifc_file.from_string(ifc_file.to_string())

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["aggregate"])
        ifc_diff.diff()
        assert ifc_diff.change_register == {}

    def test_changed_container(self):
        ifc_file = setup_project()
        _, _, level_1, level_2 = setup_spatial_tree(ifc_file)
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        ifcopenshell.api.spatial.assign_container(ifc_file, products=[wall], relating_structure=level_1)

        new_file = ifc_file.from_string(ifc_file.to_string())
        ifcopenshell.api.spatial.assign_container(
            new_file, products=[new_file.by_id(wall.id())], relating_structure=new_file.by_id(level_2.id())
        )

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["container"])
        ifc_diff.diff()
        assert ifc_diff.change_register == {wall.GlobalId: {"container_changed": True}}

    def test_changed_geometry(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        assert context
        representation = ifcopenshell.api.geometry.add_slab_representation(ifc_file, context, depth=0.2)
        ifcopenshell.api.geometry.assign_representation(ifc_file, wall, representation)

        new_file = ifc_file.from_string(ifc_file.to_string())
        extrusion = new_file.by_type("IfcExtrudedAreaSolid")[0]
        extrusion.Depth = 500.0

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["geometry"])
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {wall.GlobalId: {"geometry_changed": True}}
