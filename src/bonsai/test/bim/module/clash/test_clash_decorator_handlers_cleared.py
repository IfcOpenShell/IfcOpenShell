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

"""Runtime regression: viewport-decorator install / uninstall keeps the
``handlers`` list empty across repeated cycles.

ClashDecorator is the representative subclass — its lifecycle is now
inherited from ``tool.Blender.ViewportDecorator``. The contract pinned
here is the canonical one for every subclass: after each ``uninstall``,
``cls.handlers`` must be empty and ``cls.is_installed`` must be False."""

import bpy
import pytest

from bonsai.bim.module.clash.decorator import ClashDecorator

pytestmark = pytest.mark.clash


@pytest.fixture(autouse=True)
def _reset_decorator_state():
    ClashDecorator.uninstall()
    yield
    ClashDecorator.uninstall()


def test_clash_decorator_handlers_cleared_across_install_cycles():
    ctx = bpy.context
    for _ in range(3):
        ClashDecorator.install(ctx)
        assert ClashDecorator.is_installed is True
        assert len(ClashDecorator.handlers) > 0
        ClashDecorator.uninstall()
        assert ClashDecorator.is_installed is False
        assert ClashDecorator.handlers == []
