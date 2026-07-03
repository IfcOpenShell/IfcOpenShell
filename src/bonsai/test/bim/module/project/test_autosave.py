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
#
# This file was generated with the assistance of an AI coding tool.

import os
import time
from pathlib import Path

import pytest

from bonsai.tool.autosave import AUTOSAVED_SUFFIX, AUTOSAVING_SUFFIX, Autosave

pytestmark = pytest.mark.project


class TestAutosavePaths:
    def test_get_paths_for_ifc_file(self):
        main_path, autosaving_path, autosaved_path = Autosave.get_paths("/tmp/myfile.ifc")
        assert main_path == Path("/tmp/myfile.ifc")
        assert autosaving_path == Path(f"/tmp/myfile{AUTOSAVING_SUFFIX}")
        assert autosaved_path == Path(f"/tmp/myfile{AUTOSAVED_SUFFIX}")

    def test_get_newer_autosaved_path_when_missing(self, tmp_path):
        ifc_path = tmp_path / "myfile.ifc"
        ifc_path.write_text("ifc")
        assert Autosave.get_newer_autosaved_path(ifc_path) is None

    def test_get_newer_autosaved_path_when_older(self, tmp_path):
        ifc_path = tmp_path / "myfile.ifc"
        autosaved_path = tmp_path / f"myfile{AUTOSAVED_SUFFIX}"
        ifc_path.write_text("ifc")
        autosaved_path.write_text("autosaved")
        past = time.time() - 10
        os.utime(ifc_path, (past, past))
        os.utime(autosaved_path, (time.time(), time.time()))
        assert Autosave.get_newer_autosaved_path(ifc_path) == autosaved_path.as_posix()

    def test_get_newer_autosaved_path_when_not_newer(self, tmp_path):
        ifc_path = tmp_path / "myfile.ifc"
        autosaved_path = tmp_path / f"myfile{AUTOSAVED_SUFFIX}"
        ifc_path.write_text("ifc")
        autosaved_path.write_text("autosaved")
        now = time.time()
        os.utime(ifc_path, (now, now))
        past = now - 10
        os.utime(autosaved_path, (past, past))
        assert Autosave.get_newer_autosaved_path(ifc_path) is None

    def test_get_newer_autosaved_path_ignores_non_ifc(self, tmp_path):
        path = tmp_path / "myfile.ifczip"
        path.write_text("zip")
        assert Autosave.get_newer_autosaved_path(path) is None
