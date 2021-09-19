# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import ui, prop, operator

classes = (
    operator.CreateProject,
    operator.LoadProject,
    operator.UnloadProject,
    operator.LoadProjectElements,
    operator.LinkIfc,
    operator.UnlinkIfc,
    operator.UnloadLink,
    operator.LoadLink,
    operator.SelectLibraryFile,
    operator.ChangeLibraryElement,
    operator.RefreshLibrary,
    operator.RewindLibrary,
    operator.AssignLibraryDeclaration,
    operator.UnassignLibraryDeclaration,
    operator.SaveLibraryFile,
    operator.AppendLibraryElement,
    operator.EnableEditingHeader,
    operator.DisableEditingHeader,
    operator.EditHeader,
    prop.LibraryElement,
    prop.FilterCategory,
    prop.Link,
    prop.BIMProjectProperties,
    ui.BIM_PT_project,
    ui.BIM_PT_project_library,
    ui.BIM_PT_links,
    ui.BIM_UL_library,
    ui.BIM_UL_filter_categories,
    ui.BIM_UL_links,
)


def register():
    bpy.types.Scene.BIMProjectProperties = bpy.props.PointerProperty(type=prop.BIMProjectProperties)


def unregister():
    del bpy.types.Scene.BIMProjectProperties
