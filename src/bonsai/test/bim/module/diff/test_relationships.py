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

The fix keeps the user's selection as-is (ExecuteIfcDiff never mutates
``diff_relationships``, since Blender forbids ID writes from ``draw()``) and
instead reports, via ``get_skipped_default_relationships``, which of the
library's own default relationships are NOT being compared, so "0 changed"
can no longer be mistaken for "0 checked".

``bonsai.bim.module.diff.relationships`` is deliberately bpy-free, and this
test file loads it directly by path (bypassing the bonsai package's
``__init__`` chain, which imports bpy) so the fix can be verified without a
running Blender instance."""

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


class TestGetSkippedDefaultRelationships:
    """Unit tests for the pure function ExecuteIfcDiff uses to decide
    whether to warn the user. Fails with ImportError/AttributeError before
    the fix, since neither the module nor the function existed."""

    def test_empty_selection_skips_nothing(self):
        # An empty list makes ifcdiff.IfcDiff apply its own default
        # (attributes + geometry), so nothing is silently skipped.
        get_skipped = _load_bonsai_diff_relationships_module().get_skipped_default_relationships
        assert get_skipped([]) == []

    def test_unrelated_relationship_skips_both_defaults(self):
        get_skipped = _load_bonsai_diff_relationships_module().get_skipped_default_relationships
        assert set(get_skipped(["property"])) == {"attributes", "geometry"}

    def test_selecting_both_defaults_skips_nothing(self):
        get_skipped = _load_bonsai_diff_relationships_module().get_skipped_default_relationships
        assert get_skipped(["property", "attributes", "geometry"]) == []

    def test_selecting_one_default_skips_the_other(self):
        get_skipped = _load_bonsai_diff_relationships_module().get_skipped_default_relationships
        assert get_skipped(["property", "attributes"]) == ["geometry"]


class TestDiffPanelDefaultRelationships:
    def test_selected_relationship_alone_misses_attribute_changes(self):
        # Documents *why* the warning matters: exactly what ExecuteIfcDiff
        # sends to ifcdiff.IfcDiff when a user selects only "property" (its
        # own selection, unmodified) misses a real attribute change.
        relationships_module = _load_bonsai_diff_relationships_module()
        assert relationships_module.get_skipped_default_relationships(["property"]) == [
            "attributes",
            "geometry",
        ]

        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        wall.PredefinedType = "SOLIDWALL"

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        wall_new.PredefinedType = "NOTDEFINED"
        pset = ifcopenshell.api.pset.add_pset(new_file, product=wall_new, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(new_file, pset=pset, properties={"FireRating": "2HR"})

        diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["property"])
        diff.diff()
        changes = diff.change_register.get(wall.GlobalId, {})
        assert changes.get("properties_changed")
        assert "attributes_changed" not in changes  # the cleared PredefinedType is missed

        # Following the warning and adding "attributes"/"geometry" catches it.
        fixed_relationships = [*relationships_module.DEFAULT_RELATIONSHIPS, "property"]
        assert relationships_module.get_skipped_default_relationships(fixed_relationships) == []
        fixed_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=fixed_relationships, is_shallow=False)
        fixed_diff.diff()
        fixed_changes = fixed_diff.change_register.get(wall.GlobalId, {})
        assert fixed_changes.get("attributes_changed") is True
        assert fixed_changes.get("properties_changed")
