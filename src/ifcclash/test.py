# IfcClash - IFC-based clash detection.
# Copyright (C) 2020-2024 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcClash.
#
# IfcClash is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcClash is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcClash.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import tempfile

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.guid
import numpy as np

from ifcclash.ifcclash import Clasher, ClashSettings

# Two walls, 5m x 3m x 0.2m thick, arranged perpendicular so they genuinely cross.
# This layout is deliberately the same as ifcquery's clash test fixture: it is a
# known-good recipe for producing a real, detectable collision.
CROSSING_MATRIX = np.array(
    [
        [0.0, -1.0, 0.0, 2.5],
        [1.0, 0.0, 0.0, -2.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
)


def far_matrix() -> np.ndarray:
    """A placement far enough away that it cannot overlap anything else in these tests."""
    matrix = np.eye(4)
    matrix[0, 3] = 1000.0
    matrix[1, 3] = 1000.0
    return matrix


def build_project() -> tuple[ifcopenshell.file, ifcopenshell.entity_instance, ifcopenshell.entity_instance]:
    """Create a minimal IFC4 project with a Model/Body context and a single storey."""
    ifc_file = ifcopenshell.api.project.create_file()
    # Owner history needs a person/application to resolve against; stub them out like ifcquery's tests do.
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(ifc_file)

    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding")
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey")
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(ifc_file, products=[storey], relating_object=building)

    model = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc_file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    return ifc_file, storey, body


def add_wall(
    ifc_file: ifcopenshell.file,
    storey: ifcopenshell.entity_instance,
    body: ifcopenshell.entity_instance,
    matrix: "np.ndarray | None" = None,
    global_id: "str | None" = None,
) -> ifcopenshell.entity_instance:
    """Add a 5m x 3m x 0.2m wall, optionally moved by ``matrix`` and forced to ``global_id``."""
    wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")
    representation = ifcopenshell.api.geometry.add_wall_representation(
        ifc_file, context=body, length=5, height=3, thickness=0.2
    )
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=wall, representation=representation)
    ifcopenshell.api.spatial.assign_container(ifc_file, products=[wall], relating_structure=storey)
    if matrix is not None:
        ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=wall, matrix=matrix)
    if global_id is not None:
        wall.GlobalId = global_id
    return wall


def run_collision_clash(source_paths: list[str]) -> dict:
    """Run a single self-collision clash set over the given source files and return its clashes."""
    settings = ClashSettings()
    settings.logger = logging.getLogger("ifcclash.test")
    settings.logger.addHandler(logging.NullHandler())
    settings.output = os.path.join(tempfile.mkdtemp(), "clashes.json")

    clasher = Clasher(settings)
    clash_set = {
        "name": "Test",
        "a": [{"file": path} for path in source_paths],
        "mode": "collision",
        "allow_touching": False,
    }
    clasher.clash_sets = [clash_set]
    clasher.clash()
    return clash_set["clashes"]


class TestDuplicateGlobalIdAcrossSources:
    """Regression test for the fix in d1173a12b1.

    ``add_collision_objects`` used to key each clash group's elements by
    ``GlobalId``. GlobalIds are only unique within a single file, so when a
    clash set federated two sources that happened to reuse a GlobalId (e.g.
    the same file referenced twice, or a federated dataset split by
    discipline that preserved GlobalIds), the later source silently
    overwrote the earlier element in the group used for testing. The
    overwritten element's geometry was still added to the tree, but it was
    never compared against anything, so a real clash could be missed with
    no error or warning.
    """

    def test_missed_clash_is_found_when_a_duplicate_global_id_is_introduced(self, tmp_path):
        # Source A: two walls that genuinely overlap (perpendicular, crossing).
        file_a, storey_a, body_a = build_project()
        shared_guid = ifcopenshell.guid.new()
        wall_1 = add_wall(file_a, storey_a, body_a, global_id=shared_guid)
        wall_2 = add_wall(file_a, storey_a, body_a, matrix=CROSSING_MATRIX)
        path_a = str(tmp_path / "a.ifc")
        file_a.write(path_a)

        # Source B: an unrelated wall, far away, that happens to reuse wall_1's GlobalId.
        file_b, storey_b, body_b = build_project()
        add_wall(file_b, storey_b, body_b, matrix=far_matrix(), global_id=shared_guid)
        path_b = str(tmp_path / "b.ifc")
        file_b.write(path_b)

        clashes = run_collision_clash([path_a, path_b])

        assert len(clashes) == 1, "the genuine overlap between wall_1 and wall_2 in source A must be found"
        guids = {c["a_global_id"] for c in clashes.values()} | {c["b_global_id"] for c in clashes.values()}
        assert wall_1.GlobalId in guids
        assert wall_2.GlobalId in guids

    def test_control_unique_global_ids_across_sources_still_clash(self, tmp_path):
        """Same layout as above, but no source reuses a GlobalId. Must still find the clash.

        This proves the fix (keying groups by element identity instead of GlobalId)
        did not change correct behaviour for the common case of no duplicate GlobalIds.
        """
        file_a, storey_a, body_a = build_project()
        wall_1 = add_wall(file_a, storey_a, body_a)
        wall_2 = add_wall(file_a, storey_a, body_a, matrix=CROSSING_MATRIX)
        path_a = str(tmp_path / "a.ifc")
        file_a.write(path_a)

        file_b, storey_b, body_b = build_project()
        add_wall(file_b, storey_b, body_b, matrix=far_matrix())  # unique GlobalId, unrelated to A
        path_b = str(tmp_path / "b.ifc")
        file_b.write(path_b)

        clashes = run_collision_clash([path_a, path_b])

        assert len(clashes) == 1
        guids = {c["a_global_id"] for c in clashes.values()} | {c["b_global_id"] for c in clashes.values()}
        assert {wall_1.GlobalId, wall_2.GlobalId} == guids

    def test_no_clash_when_sources_do_not_overlap(self, tmp_path):
        """Sanity check: two far-apart sources, even with a duplicate GlobalId, must not clash."""
        file_a, storey_a, body_a = build_project()
        shared_guid = ifcopenshell.guid.new()
        add_wall(file_a, storey_a, body_a, global_id=shared_guid)
        path_a = str(tmp_path / "a.ifc")
        file_a.write(path_a)

        file_b, storey_b, body_b = build_project()
        add_wall(file_b, storey_b, body_b, matrix=far_matrix(), global_id=shared_guid)
        path_b = str(tmp_path / "b.ifc")
        file_b.write(path_b)

        clashes = run_collision_clash([path_a, path_b])

        assert len(clashes) == 0
