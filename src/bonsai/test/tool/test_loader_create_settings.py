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

from types import SimpleNamespace
from unittest.mock import Mock, patch

from bonsai.tool.loader import Loader as subject


def test_create_settings_keeps_the_original_face_edges():
    context = Mock()
    context.id.return_value = 1
    import_settings = SimpleNamespace(contexts=[context], deflection_tolerance=0.001, angular_tolerance=0.5)

    with patch.object(subject, "settings", import_settings):
        (settings,) = subject.create_settings()

    assert settings.get("cgal-original-edges") is True
