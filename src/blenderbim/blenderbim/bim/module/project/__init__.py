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
    operator.AppendLibraryElement,
    operator.AssignLibraryDeclaration,
    operator.AppendEntireLibrary,
    operator.ChangeLibraryElement,
    operator.CreateProject,
    operator.DisableEditingHeader,
    operator.EditHeader,
    operator.EnableEditingHeader,
    operator.ExportIFC,
    operator.ImportIFC,
    operator.LinkIfc,
    operator.LoadLink,
    operator.LoadProject,
    operator.LoadProjectElements,
    operator.NewProject,
    operator.RefreshLibrary,
    operator.RewindLibrary,
    operator.SaveLibraryFile,
    operator.SelectLibraryFile,
    operator.ToggleFilterCategories,
    operator.ToggleLinkVisibility,
    operator.UnassignLibraryDeclaration,
    operator.UnlinkIfc,
    operator.UnloadLink,
    operator.UnloadProject,
    prop.LibraryElement,
    prop.FilterCategory,
    prop.Link,
    prop.BIMProjectProperties,
    ui.BIM_MT_project,
    ui.BIM_PT_project,
    ui.BIM_PT_project_library,
    ui.BIM_PT_links,
    ui.BIM_UL_library,
    ui.BIM_UL_filter_categories,
    ui.BIM_UL_links,
)


def register():
    bpy.types.Scene.BIMProjectProperties = bpy.props.PointerProperty(type=prop.BIMProjectProperties)
    bpy.types.TOPBAR_MT_file.prepend(ui.file_menu)


def unregister():
    bpy.types.TOPBAR_MT_file.remove(ui.file_menu)
    del bpy.types.Scene.BIMProjectProperties
