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

import pytest

import bonsai.tool.web
from bonsai.tool.web import Web as subject
from test.bim.bootstrap import NewFile


class TestDisconnectWithoutAThread(NewFile):
    """Disconnecting when the connection has already gone.

    The websocket server outlives the Blender that started it, so a second
    Blender reuses it and inherits a connection that can disappear underneath it.
    What is left is a scene that says "connected" and no thread to disconnect.

    Both buttons in the Web UI panel are then dead: this one raised
    AttributeError, and Connect returns early because it reads the same flag. The
    panel could only be recovered from the Python console or by restarting
    Blender, which is not something to ask of someone whose server merely
    restarted.
    """

    def test_it_does_not_raise_when_the_thread_has_gone(self):
        bonsai.tool.web.ws_thread = None
        bonsai.tool.web.sio = None
        subject.set_is_connected(True)

        subject.disconnect_websocket_server()

        assert subject.get_web_props().is_connected is False

    def test_it_clears_the_client_as_well(self):
        # Left set, the next connect would build a second client beside it.
        bonsai.tool.web.ws_thread = None
        bonsai.tool.web.sio = object()
        subject.set_is_connected(True)

        subject.disconnect_websocket_server()

        assert bonsai.tool.web.sio is None
        assert bonsai.tool.web.ws_thread is None

    def test_a_live_thread_is_still_stopped(self):
        # The ordinary path has to keep working: a real connection is asked to
        # disconnect and its thread stopped, not just forgotten.
        calls = []

        class FakeThread:
            def run_coro(self, coro):
                calls.append("run_coro")
                coro.close()  # never awaited, and an unawaited coroutine warns

            def stop(self):
                calls.append("stop")

        bonsai.tool.web.ws_thread = FakeThread()
        bonsai.tool.web.sio = object()
        subject.set_is_connected(True)

        subject.disconnect_websocket_server()

        assert calls == ["run_coro", "stop"]
        assert bonsai.tool.web.ws_thread is None
        assert bonsai.tool.web.sio is None
        assert subject.get_web_props().is_connected is False

    @pytest.fixture(autouse=True)
    def _leave_the_module_as_it_was(self):
        # These are module globals, so a test that set them would otherwise leak
        # into whatever runs next in the same Blender.
        yield
        bonsai.tool.web.ws_thread = None
        bonsai.tool.web.sio = None
