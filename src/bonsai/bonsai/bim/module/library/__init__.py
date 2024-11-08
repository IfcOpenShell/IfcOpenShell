# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
from . import ui, prop, operator

classes = (
    operator.AddLibrary,
    operator.AddLibraryReference,
    operator.AssignLibraryReference,
    operator.DisableEditingLibrary,
    operator.DisableEditingLibraryReference,
    operator.DisableEditingLibraryReferences,
    operator.EditLibrary,
    operator.EditLibraryReference,
    operator.EnableEditingLibrary,
    operator.EnableEditingLibraryReference,
    operator.EnableEditingLibraryReferences,
    operator.RemoveLibrary,
    operator.RemoveLibraryReference,
    operator.UnassignLibraryReference,
    prop.LibraryReference,
    prop.BIMLibraryProperties,
    ui.BIM_PT_libraries,
    ui.BIM_PT_library_references,
    ui.BIM_UL_library_references,
    ui.BIM_UL_object_library_references,
)


def register():
    bpy.types.Scene.BIMLibraryProperties = bpy.props.PointerProperty(type=prop.BIMLibraryProperties)


def unregister():
    del bpy.types.Scene.BIMLibraryProperties
