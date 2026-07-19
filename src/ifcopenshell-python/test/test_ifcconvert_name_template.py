# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

"""IfcConvert --name-template: a generic printf/find-style template to derive
per-entity identifiers/names upon serialization (see issue #413)."""

import shutil
import subprocess
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "files" / "name_template_fixture.ifc"

# The fixture contains a single IfcWall with a known GlobalId, Name and Tag,
# used below to assert on the exact naming output of each placeholder.
WALL_NAME = "Test Wall"
WALL_GUID_COMPRESSED = "27uW0y7Gr72R8yo2C4vBlV"
WALL_GUID_UNCOMPRESSED = "87e2003c-1d0d-4709-b23c-c82304e4bbdf"
WALL_STEP_ID = "40"
WALL_TAG = "TAG-001"


@pytest.mark.skipif(shutil.which("IfcConvert") is None, reason="Requires IfcConvert in path")
class TestNameTemplate:
    def convert(self, tmp_path: Path, *extra_args: str) -> str:
        out = tmp_path / "output.obj"
        subprocess.check_call([shutil.which("IfcConvert"), str(FIXTURE), str(out), *extra_args])
        return out.read_text()

    def test_combines_multiple_placeholders(self, tmp_path):
        contents = self.convert(tmp_path, "--name-template", "%T-%N (%G) tag=%t")
        assert f"g IfcWall-{WALL_NAME} ({WALL_GUID_COMPRESSED}) tag={WALL_TAG}" in contents

    def test_uncompressed_globalid_placeholder(self, tmp_path):
        contents = self.convert(tmp_path, "--name-template", "%g")
        assert f"g {WALL_GUID_UNCOMPRESSED}" in contents

    def test_step_id_placeholder(self, tmp_path):
        contents = self.convert(tmp_path, "--name-template", "%i")
        assert f"g {WALL_STEP_ID}" in contents

    def test_literal_percent_sign(self, tmp_path):
        contents = self.convert(tmp_path, "--name-template", "100%%")
        assert "g 100%" in contents

    def test_unknown_placeholder_is_kept_verbatim(self, tmp_path):
        contents = self.convert(tmp_path, "--name-template", "%Z-%N")
        assert f"g %Z-{WALL_NAME}" in contents

    def test_takes_priority_over_legacy_naming_flags(self, tmp_path):
        contents = self.convert(tmp_path, "--name-template", "%N", "--use-element-guids")
        assert f"g {WALL_NAME}" in contents

    def test_legacy_use_element_guids_unaffected_when_not_given(self, tmp_path):
        contents = self.convert(tmp_path, "--use-element-guids")
        assert f"g {WALL_GUID_COMPRESSED}" in contents

    def test_legacy_use_element_names_unaffected_when_not_given(self, tmp_path):
        contents = self.convert(tmp_path, "--use-element-names")
        assert f"g {WALL_NAME}" in contents

    def test_legacy_use_element_step_ids_unaffected_when_not_given(self, tmp_path):
        contents = self.convert(tmp_path, "--use-element-step-ids")
        assert f"g id-{WALL_STEP_ID}" in contents
