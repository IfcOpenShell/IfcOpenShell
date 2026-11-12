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

"""
Requires pytest installed under blender.

Usage:
    blender -b -P runpytest.py -- ARGS

Alternative (when the calling shell strips or reorders the ``--`` separator
before it reaches Blender — observed with some PowerShell / wrapper-script
invocations on Windows): pass the same pytest args via the
``BONSAI_TEST_ARGS`` environment variable as a single shell-quoted string
and invoke without ``--``::

    $env:BONSAI_TEST_ARGS = "test/bim/ -x -q"
    blender -b -P runpytest.py
"""

import os
import shlex
import sys

import pytest

argv = [__file__]

env_args = os.environ.get("BONSAI_TEST_ARGS", "")
if env_args:
    # POSIX-style quoting works on all three OSes — env var values are
    # literal strings (no shell evaluation when Python reads them), and
    # POSIX quoting (``'foo "bar baz" qux'`` → three tokens, quotes stripped)
    # matches what most docs and examples use.
    argv += shlex.split(env_args)
    # On the env-var path the args never appear in Blender's argv at all,
    # so any pytest plugin that reads ``sys.argv`` directly (instead of
    # going through pytest's API) would otherwise see only Blender's own
    # ``-b -P runpytest.py`` and miss the test args entirely. Shadow argv
    # so those plugins see the pytest-shaped view they expect.
    sys.argv = list(argv)
elif "--" in sys.argv:
    # The traditional path: Blender forwards everything after ``--`` to the
    # script via ``sys.argv``. ``sys.argv`` is deliberately left as Blender
    # set it — pre-existing behavior, preserved.
    i = sys.argv.index("--")
    argv += sys.argv[i + 1 :]

pytest.main(argv)
