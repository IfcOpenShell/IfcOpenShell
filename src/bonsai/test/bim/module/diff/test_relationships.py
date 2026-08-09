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

"""Regression test for the Diff panel silently reporting zero changes.

ifcdiff.IfcDiff only compares attributes and geometry when the caller's
``relationships`` list is empty (its own default). Bonsai's Diff panel used
to build that list straight from its ``RelationshipType`` enum, which did
not include "attributes" or "geometry" at all: the moment a user added any
other relationship (eg. "property"), the list became non-empty without
attributes/geometry in it, and ifcdiff's own default never kicked in. This
silently hid changes such as a cleared PredefinedType or a changed mesh.

This module ``bonsai.bim.module.diff.relationships`` is deliberately
bpy-free, and this test file loads it directly by path (bypassing the
bonsai package's ``__init__`` chain, which imports bpy) so the fix can be
verified without a running Blender instance."""

import importlib.util
import sys
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit

BONSAI_ADDON_DIR = Path(__file__).resolve().parents[4] / "bonsai"
IFCDIFF_DIR = Path(__file__).resolve().parents[5] / "ifcdiff"

if str(IFCDIFF_DIR) not in sys.path:
    sys.path.insert(0, str(IFCDIFF_DIR))

import ifcdiff  # noqa: E402


def _load_bonsai_diff_relationships_module():
    module_path = BONSAI_ADDON_DIR / "bim" / "module" / "diff" / "relationships.py"
    spec = importlib.util.spec_from_file_location("bonsai_diff_relationships", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def setup_project() -> ifcopenshell.file:
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
    ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])
    model = ifcopenshell.api.context.add_context(ifc_file, "Model")
    ifcopenshell.api.context.add_context(ifc_file, "Model", "Body", "MODEL_VIEW", parent=model)
    return ifc_file


class TestDiffPanelDefaultRelationships:
    def test_selected_relationship_still_detects_attribute_changes(self):
        default_relationships = _load_bonsai_diff_relationships_module().DEFAULT_RELATIONSHIPS
        assert set(default_relationships) == {"attributes", "geometry"}

        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        wall.PredefinedType = "SOLIDWALL"

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        wall_new.PredefinedType = "NOTDEFINED"
        pset = ifcopenshell.api.pset.add_pset(new_file, product=wall_new, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(new_file, pset=pset, properties={"FireRating": "2HR"})

        # The old, buggy Bonsai operator: "attributes"/"geometry" were not in
        # RelationshipType, so a user adding a "property" check could only
        # ever send ["property"] to IfcDiff.
        old_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["property"])
        old_diff.diff()
        old_changes = old_diff.change_register.get(wall.GlobalId, {})
        assert old_changes.get("properties_changed")
        assert "attributes_changed" not in old_changes  # the cleared PredefinedType is missed

        # The fixed Bonsai operator: the Diff panel pre-populates
        # diff_relationships with DEFAULT_RELATIONSHIPS, so adding "property"
        # results in ["attributes", "geometry", "property"].
        new_diff = ifcdiff.IfcDiff(
            ifc_file, new_file, relationships=[*default_relationships, "property"], is_shallow=False
        )
        new_diff.diff()
        new_changes = new_diff.change_register.get(wall.GlobalId, {})
        assert new_changes.get("attributes_changed") is True
        assert new_changes.get("properties_changed")
