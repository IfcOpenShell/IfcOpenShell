# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

# AI-assisted development tool was used in writing this file.

from __future__ import annotations

from typing import Any, Optional

import bpy

import bonsai.tool as tool


def refresh():
    ProjectLicenseData.is_loaded = False
    ObjectLicenseData.is_loaded = False


class ProjectLicenseData:
    data: dict[str, Any] = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["license"] = cls.license()

    @classmethod
    def license(cls) -> Optional[dict]:
        ifc = tool.Ifc.get()
        if not ifc:
            return None
        projects = ifc.by_type("IfcProject")
        if not projects:
            return None
        return tool.License.get_pset(projects[0])


class ObjectLicenseData:
    data: dict[str, Any] = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["license"] = None
        cls.data["inherited_from"] = None
        cls.data["inherited_from_type"] = None

        obj = bpy.context.active_object
        if not obj:
            return
        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        pset, source = tool.License.get_effective_pset(element)
        cls.data["license"] = pset
        if source is not None and source.id() != element.id():
            cls.data["inherited_from"] = getattr(source, "Name", None) or source.is_a()
            cls.data["inherited_from_type"] = source.is_a()
