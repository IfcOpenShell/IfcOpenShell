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
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import numpy as np
import pytest

import ifcdiff

SAMPLE_MODEL_DIR = "/Users/petruc/dev/sample models/012"
SAMPLE_MODEL_OLD = os.path.join(SAMPLE_MODEL_DIR, "PCERT_PRA-bSI-L-INFRA-3E-ARL_version1.ifc")
SAMPLE_MODEL_NEW = os.path.join(SAMPLE_MODEL_DIR, "PCERT_PRA-bSI-L-INFRA-3E-ARL_version2.ifc")


def setup_project() -> ifcopenshell.file:
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
    ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])
    model = ifcopenshell.api.context.add_context(ifc_file, "Model")
    ifcopenshell.api.context.add_context(ifc_file, "Model", "Body", "MODEL_VIEW", parent=model)
    return ifc_file


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
        changes = ifc_diff.change_register[wall.GlobalId]["attributes_changed"]
        assert changes["values_changed"]["root['Name']"]["old_value"] == "Foo"
        assert changes["values_changed"]["root['Name']"]["new_value"] == "Bar"

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
        changes = ifc_diff.change_register[wall.GlobalId]["attributes_changed"]
        assert changes["values_changed"]["root['PredefinedType']"]["old_value"] == "SOLIDWALL"
        assert changes["values_changed"]["root['PredefinedType']"]["new_value"] == "NOTDEFINED"

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
        assert ifc_diff.change_register[wall.GlobalId]["geometry_changed"]

    def test_class_change_is_detected(self):
        # Regression test: a reclassified element (same GlobalId, different
        # is_a()) with no other attribute differences was previously reported
        # as unchanged, since diff_element only compared attribute values.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        global_id = wall.GlobalId

        new_file = ifc_file.from_string(ifc_file.to_string())
        ifcopenshell.api.root.remove_product(new_file, new_file.by_id(wall.id()))
        slab = ifcopenshell.api.root.create_entity(new_file, ifc_class="IfcSlab", name="Foo")
        slab.GlobalId = global_id

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["attributes", "geometry", "property", "type"])
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {
            global_id: {"class_changed": {"old_class": "IfcWall", "new_class": "IfcSlab"}}
        }

    def test_property_diff_excludes_step_id_bookkeeping_key(self):
        # Regression test: the exclude_regex_paths pattern for the pset "id"
        # bookkeeping key was r".*id$", which never matches a DeepDiff path
        # like root['Pset_WallCommon']['id'] because the path ends with "]".
        # A pset re-saved with a different STEP entity number (but otherwise
        # identical properties) was falsely reported as changed.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=wall, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"FireRating": "2HR"})

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        for rel in list(wall_new.IsDefinedBy):
            pset_def = rel.RelatingPropertyDefinition
            if pset_def.Name == "Pset_WallCommon":
                ifcopenshell.api.pset.remove_pset(new_file, product=wall_new, pset=pset_def)
        # shift STEP numbering so the recreated pset gets a different "id"
        dummy = ifcopenshell.api.root.create_entity(new_file, ifc_class="IfcWall", name="Dummy")
        ifcopenshell.api.root.remove_product(new_file, dummy)
        new_pset = ifcopenshell.api.pset.add_pset(new_file, product=wall_new, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(new_file, pset=new_pset, properties={"FireRating": "2HR"})
        assert pset.id() != new_pset.id()

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["property"])
        ifc_diff.diff()
        assert ifc_diff.change_register == {}

    def test_property_diff_still_detects_real_change_despite_id_exclusion(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=wall, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"FireRating": "2HR"})

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        for rel in list(wall_new.IsDefinedBy):
            pset_def = rel.RelatingPropertyDefinition
            if pset_def.Name == "Pset_WallCommon":
                ifcopenshell.api.pset.remove_pset(new_file, product=wall_new, pset=pset_def)
        dummy = ifcopenshell.api.root.create_entity(new_file, ifc_class="IfcWall", name="Dummy")
        ifcopenshell.api.root.remove_product(new_file, dummy)
        new_pset = ifcopenshell.api.pset.add_pset(new_file, product=wall_new, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(new_file, pset=new_pset, properties={"FireRating": "1HR"})

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["property"])
        ifc_diff.diff()
        changed = ifc_diff.change_register[wall.GlobalId]["properties_changed"]
        assert changed["values_changed"]["root['Pset_WallCommon']['FireRating']"]["old_value"] == "2HR"
        assert changed["values_changed"]["root['Pset_WallCommon']['FireRating']"]["new_value"] == "1HR"
        assert "id" not in str(changed)

    def test_attributes_changed_includes_diff_detail(self):
        # Regression test: attributes_changed used to be a bare True even
        # though a full DeepDiff was computed and then discarded, and it
        # compared positional attribute lists, so paths were root[N] instead
        # of the attribute name.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        wall.PredefinedType = "SOLIDWALL"

        new_file = ifc_file.from_string(ifc_file.to_string())
        new_file.by_id(wall.id()).PredefinedType = None

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["attributes"])
        ifc_diff.diff()
        changed = ifc_diff.change_register[wall.GlobalId]["attributes_changed"]
        assert changed["type_changes"]["root['PredefinedType']"]["old_value"] == "SOLIDWALL"
        assert changed["type_changes"]["root['PredefinedType']"]["new_value"] is None

    def test_is_shallow_true_reports_only_first_relationship_change(self):
        # Documents the current default: is_shallow=True keeps the historical
        # "first difference only" behaviour for speed.
        ifc_file = setup_project()
        storey1 = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey")
        storey2 = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey")
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        ifcopenshell.api.spatial.assign_container(ifc_file, products=[wall], relating_structure=storey1)
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=wall, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"FireRating": "2HR"})

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        storey2_new = new_file.by_id(storey2.id())
        ifcopenshell.api.spatial.assign_container(new_file, products=[wall_new], relating_structure=storey2_new)
        new_pset = ifcopenshell.util.element.get_psets(wall_new)["Pset_WallCommon"]
        pset_new = new_file.by_id(new_pset["id"])
        ifcopenshell.api.pset.edit_pset(new_file, pset=pset_new, properties={"FireRating": "1HR"})

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["container", "property"], is_shallow=True)
        ifc_diff.diff()
        assert len(ifc_diff.change_register[wall.GlobalId]) == 1

    def test_is_shallow_false_accumulates_multiple_relationship_changes(self):
        # Regression test: diff_element_relationships returned as soon as any
        # one relationship in the loop differed, unconditionally, even when
        # is_shallow=False. So material+property changes on the same
        # element only ever reported the first relationship checked.
        # NOTE: "container" is deliberately not used here. The
        # container/aggregate GlobalId-comparison fix (and its is_shallow
        # accumulation behaviour) is left to PR #9312 to avoid duplicating
        # that fix; see the removed old_container/old_aggregate handling
        # below.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        material_a = ifcopenshell.api.material.add_material(ifc_file, name="Soil1")
        ifcopenshell.api.material.assign_material(ifc_file, products=[wall], material=material_a)
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=wall, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"FireRating": "2HR"})

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        material_b = ifcopenshell.api.material.add_material(new_file, name="topsoil")
        ifcopenshell.api.material.assign_material(new_file, products=[wall_new], material=material_b)
        new_pset = ifcopenshell.util.element.get_psets(wall_new)["Pset_WallCommon"]
        pset_new = new_file.by_id(new_pset["id"])
        ifcopenshell.api.pset.edit_pset(new_file, pset=pset_new, properties={"FireRating": "1HR"})

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["material", "property"], is_shallow=False)
        ifc_diff.diff()
        changes = ifc_diff.change_register[wall.GlobalId]
        assert "material_changed" in changes
        assert "properties_changed" in changes

    def test_material_change_is_detected(self):
        # Regression test: there was no "material" relationship at all, so a
        # material reassignment (e.g. Soil1 -> topsoil) was invisible.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        material_a = ifcopenshell.api.material.add_material(ifc_file, name="Soil1")
        ifcopenshell.api.material.assign_material(ifc_file, products=[wall], material=material_a)

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        material_b = ifcopenshell.api.material.add_material(new_file, name="topsoil")
        ifcopenshell.api.material.assign_material(new_file, products=[wall_new], material=material_b)

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["material"])
        ifc_diff.diff()
        assert ifc_diff.change_register == {
            wall.GlobalId: {"material_changed": {"old_materials": ["Soil1"], "new_materials": ["topsoil"]}}
        }

    def test_material_change_through_layer_set_is_detected(self):
        # get_materials() should resolve a layer set down to its individual
        # materials, not just compare the layer set entity itself.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        material_set = ifcopenshell.api.material.add_material_set(ifc_file, set_type="IfcMaterialLayerSet")
        material_a = ifcopenshell.api.material.add_material(ifc_file, name="Concrete")
        ifcopenshell.api.material.add_layer(ifc_file, layer_set=material_set, material=material_a)
        ifcopenshell.api.material.assign_material(
            ifc_file, products=[wall], type="IfcMaterialLayerSet", material=material_set
        )

        new_file = ifc_file.from_string(ifc_file.to_string())
        new_layer = new_file.by_type("IfcMaterialLayer")[0]
        material_b = ifcopenshell.api.material.add_material(new_file, name="Brick")
        new_layer.Material = material_b

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["material"])
        ifc_diff.diff()
        assert ifc_diff.change_register == {
            wall.GlobalId: {"material_changed": {"old_materials": ["Concrete"], "new_materials": ["Brick"]}}
        }

    def test_unmoved_placement_is_not_reported(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")

        new_file = ifc_file.from_string(ifc_file.to_string())

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["placement"])
        ifc_diff.diff()
        assert ifc_diff.change_register == {}

    def test_placement_change_is_detected(self):
        # Regression test: ifcdiff never compared object placement at all, so
        # a moved or rotated element whose attributes, properties, and mesh
        # were unchanged was reported as unchanged.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        matrix = np.eye(4)
        matrix[0, 3] = 1.0  # 1 metre, is_si=True converts to the project's mm units
        ifcopenshell.api.geometry.edit_object_placement(new_file, product=wall_new, matrix=matrix)

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["placement"])
        ifc_diff.diff()
        changed = ifc_diff.change_register[wall.GlobalId]["placement_changed"]
        assert changed["moved"] == pytest.approx(1000.0)
        assert changed["rotated"] is False


class TestIfcDiffRealSamplePair:
    @pytest.mark.skipif(
        not os.path.exists(SAMPLE_MODEL_OLD) or not os.path.exists(SAMPLE_MODEL_NEW),
        reason="Real sample IFC pair not available on this machine",
    )
    def test_real_sample_pair_ground_truth(self):
        # Regression test using a real revision pair that exercises class
        # change, attribute change, geometry change, material change, and
        # placement change together. Ground truth established independently
        # of ifcdiff: 1 added, 2 deleted, 26 modified.
        # "container" and "aggregate" are deliberately excluded: the
        # comparison here still compares get_container()/get_aggregate()
        # results by instance identity across two different
        # ifcopenshell.file objects, which are never equal, so every element
        # with a container/aggregate would be falsely flagged. That fix is
        # left to PR #9312 rather than duplicated here.
        old = ifcopenshell.open(SAMPLE_MODEL_OLD)
        new = ifcopenshell.open(SAMPLE_MODEL_NEW)

        ifc_diff = ifcdiff.IfcDiff(
            old,
            new,
            relationships=[
                "attributes",
                "geometry",
                "property",
                "type",
                "classification",
                "material",
                "placement",
            ],
            is_shallow=False,
        )
        ifc_diff.diff()

        assert len(ifc_diff.added_elements) == 1
        assert len(ifc_diff.deleted_elements) == 2
        assert len(ifc_diff.change_register) == 26

        reclassified = {
            "3pUQsWUqb8deDoLZ6CIIET",
            "0zGSqxrLf0ngxWk8EXkozt",
            "0yVWtUza9BkBPidcrOmhrJ",
            "3pzBWeief4XhSr5Lnykkbq",
        }
        for global_id in reclassified:
            assert ifc_diff.change_register[global_id]["class_changed"] == {
                "old_class": "IfcBuildingElementProxy",
                "new_class": "IfcGeographicElement",
            }

        # the one reclassified element that also has genuinely changed
        # geometry (316 to 200 vertices, i.e. 948 to 600 flat floats)
        geometry_change = ifc_diff.change_register["3pzBWeief4XhSr5Lnykkbq"]["geometry_changed"]
        assert geometry_change["values_changed"]["root['total_verts']"]["old_value"] == 948
        assert geometry_change["values_changed"]["root['total_verts']"]["new_value"] == 600

        for global_id in ("2eGMeS8JXEqPOIXktx3T6F", "3$Tc0Y2BH1KhfYOdLzGw$7"):
            material_change = ifc_diff.change_register[global_id]["material_changed"]
            assert material_change["old_materials"] == ["Soil1"]
            assert material_change["new_materials"] == ["topsoil"]

        placement_change = ifc_diff.change_register["23sFQGRy90RxVbRHD9iSE2"]["placement_changed"]
        assert placement_change["moved"] == pytest.approx(40000.0, abs=1.0)
        assert placement_change["rotated"] is True
