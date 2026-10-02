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
import stat
from pathlib import Path
from unittest import mock

import pytest

import bonsai.bim.module.light as light

pytestmark = pytest.mark.misc


@pytest.fixture
def pyradiance_install(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    binary = bin_dir / "rtrace"
    binary.write_text("binary")
    binary.chmod(0o644)
    with (
        mock.patch.object(light, "pyradiance", True),
        mock.patch.object(light, "get_pyradiance_path", return_value=str(tmp_path)),
    ):
        yield binary


class TestRegisterPyradianceBinaries:
    def test_registration_survives_a_read_only_install(self, pyradiance_install):
        with mock.patch.object(Path, "chmod", side_effect=PermissionError("read-only file system")):
            light.register()

    def test_binaries_without_the_exec_bit_are_made_executable(self, pyradiance_install):
        light.register()

        assert pyradiance_install.stat().st_mode & stat.S_IXUSR
        assert os.access(pyradiance_install, os.X_OK)
