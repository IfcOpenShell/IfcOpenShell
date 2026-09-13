# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Michael Yoder <myoder@desertspringscivil.com>
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

import pytest

import bonsai.core.alignment as subject
from test.core.bootstrap import alignment, ifc


# ---------------------------------------------------------------------------
# import_alignment_csv
# ---------------------------------------------------------------------------


class TestImportAlignmentCsv:
    def test_raises_when_no_ifc_file_loaded(self, ifc, alignment):
        ifc.get().should_be_called().will_return(None)
        with pytest.raises(ValueError, match="No IFC file loaded"):
            subject.import_alignment_csv(ifc, alignment, filepath="pis.csv")

    def test_imports_and_builds_hierarchy_for_parent_only(self, ifc, alignment):
        ifc.get().should_be_called().will_return("ifc_file")
        alignment.create_alignment_from_csv("pis.csv").should_be_called().will_return("parent")
        alignment.create_hierarchy_for_alignment("parent").should_be_called()
        alignment.get_child_alignments("parent").should_be_called().will_return([])
        alignment.create_objects_for_referents("parent").should_be_called()
        result = subject.import_alignment_csv(ifc, alignment, filepath="pis.csv")
        assert result == "parent"

    def test_builds_hierarchy_for_each_aggregated_child(self, ifc, alignment):
        ifc.get().should_be_called().will_return("ifc_file")
        alignment.create_alignment_from_csv("pis.csv").should_be_called().will_return("parent")
        alignment.create_hierarchy_for_alignment("parent").should_be_called()
        alignment.get_child_alignments("parent").should_be_called().will_return(["child_a", "child_b"])
        alignment.create_hierarchy_for_alignment("child_a").should_be_called()
        alignment.create_hierarchy_for_alignment("child_b").should_be_called()
        alignment.create_objects_for_referents("parent").should_be_called()
        result = subject.import_alignment_csv(ifc, alignment, filepath="pis.csv")
        assert result == "parent"
