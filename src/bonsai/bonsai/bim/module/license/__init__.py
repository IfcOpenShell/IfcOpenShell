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

import bpy

from . import operator, prop, ui

classes = (
    operator.DisableEditingObjectLicense,
    operator.DisableEditingProjectLicense,
    operator.EditObjectLicense,
    operator.EditProjectLicense,
    operator.EnableEditingObjectLicense,
    operator.EnableEditingProjectLicense,
    operator.RemoveObjectLicense,
    operator.RemoveProjectLicense,
    prop.BIMLicenseProperties,
    ui.BIM_PT_object_license,
    ui.BIM_PT_project_license,
)


def register():
    bpy.types.Scene.BIMLicenseProperties = bpy.props.PointerProperty(type=prop.BIMLicenseProperties)


def unregister():
    del bpy.types.Scene.BIMLicenseProperties
