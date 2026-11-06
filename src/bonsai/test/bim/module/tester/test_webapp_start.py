# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import subprocess
import sys
import time

import bpy
import pytest

import bonsai.bim.module.tester.operator as operator
import bonsai.tool as tool
from test.bim.bootstrap import NewFile

DIES_ON_STARTUP = "import sys; print('boom'); sys.exit(3)"

LISTENS_THEN_FLOODS_STDOUT = (
    "import socket, sys, pathlib, time\n"
    "s = socket.socket(); s.bind(('127.0.0.1', int(sys.argv[1]))); s.listen(1)\n"
    "sys.stdout.write('x' * 1000 * 1000); sys.stdout.flush()\n"
    "pathlib.Path(sys.argv[2]).write_text('done')\n"
    "time.sleep(60)\n"
)


def replace_webapp_process(monkeypatch, script, *extra_args):
    real_popen = subprocess.Popen

    def fake_popen(args, **kwargs):
        return real_popen([sys.executable, "-c", script, args[-1], *extra_args], **kwargs)

    monkeypatch.setattr(operator.subprocess, "Popen", fake_popen)


class TestStartIfcTesterWebapp(NewFile):
    @pytest.fixture(autouse=True)
    def _record_browser(self, monkeypatch):
        self.opened = []
        monkeypatch.setattr(operator.webbrowser, "open", self.opened.append)
        self.monkeypatch = monkeypatch

    def test_a_webapp_that_dies_on_startup_does_not_open_the_browser_and_can_be_restarted(self):
        replace_webapp_process(self.monkeypatch, DIES_ON_STARTUP)
        props = tool.Tester.get_tester_props()
        assert bpy.ops.bim.start_ifc_tester_webapp() == {"FINISHED"}
        time.sleep(4)
        assert self.opened == []
        assert not props.webapp_is_running
        assert bpy.ops.bim.start_ifc_tester_webapp() == {"FINISHED"}
        time.sleep(4)
        assert not props.webapp_is_running

    def test_a_running_webapp_is_not_blocked_by_its_own_output(self, tmp_path):
        marker = tmp_path / "marker"
        replace_webapp_process(self.monkeypatch, LISTENS_THEN_FLOODS_STDOUT, str(marker))
        assert bpy.ops.bim.start_ifc_tester_webapp() == {"FINISHED"}
        deadline = time.monotonic() + 15
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.25)
        bpy.ops.bim.stop_ifc_tester_webapp()
        assert marker.exists()
        assert len(self.opened) == 1
