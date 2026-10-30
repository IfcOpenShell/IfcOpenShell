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


def refresh():
    """Called by bonsai.bim.handler.refresh_ui_data() after IFC operations, including
    project load (which fires too late for the blend load_post handler). Pulls each
    freshly-imported drawing camera's rules out of its IFC pset. Guarded so it never
    overwrites rules being edited in-session.
    """
    from bonsai.bim.module.status_render import operator

    for camera in operator.drawing_cameras():
        operator.ensure_rules_loaded(camera)
