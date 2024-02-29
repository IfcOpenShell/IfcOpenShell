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
    operator.AppendEntireLibrary,
    operator.AppendLibraryElement,
    operator.AppendLibraryElementByQuery,
    operator.AssignLibraryDeclaration,
    operator.ChangeLibraryElement,
    operator.CreateProject,
    operator.DisableCulling,
    operator.DisableEditingHeader,
    operator.EditHeader,
    operator.EnableCulling,
    operator.EnableEditingHeader,
    operator.ExportIFC,
    operator.ImportIFC,
    operator.LinkIfc,
    operator.LoadLink,
    operator.LoadLinkedProject,
    operator.LoadProject,
    operator.LoadProjectElements,
    operator.NewProject,
    operator.QueryLinkedElement,
    operator.RefreshLibrary,
    operator.ReloadLink,
    operator.RevertProject,
    operator.RewindLibrary,
    operator.SaveLibraryFile,
    operator.SelectLibraryFile,
    operator.ToggleFilterCategories,
    operator.ToggleLinkSelectability,
    operator.ToggleLinkVisibility,
    operator.UnassignLibraryDeclaration,
    operator.UnlinkIfc,
    operator.UnloadLink,
    operator.UnloadProject,
    prop.LibraryElement,
    prop.FilterCategory,
    prop.Link,
    prop.BIMProjectProperties,
    ui.BIM_MT_new_project,
    ui.BIM_MT_project,
    ui.BIM_PT_project,
    ui.BIM_PT_project_library,
    ui.BIM_PT_links,
    ui.BIM_PT_purge,
    ui.BIM_UL_library,
    ui.BIM_UL_filter_categories,
    ui.BIM_UL_links,
)


addon_keymaps = []


def register():
    bpy.types.Scene.BIMProjectProperties = bpy.props.PointerProperty(type=prop.BIMProjectProperties)
    bpy.types.TOPBAR_MT_file.prepend(ui.file_menu)
    bpy.types.TOPBAR_MT_file_context_menu.prepend(ui.file_menu)
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.get("Window")
        if not km:
            km = wm.keyconfigs.addon.keymaps.new("Window")
        kmi = km.keymap_items.new("wm.call_menu", "N", "PRESS", ctrl=True)
        kmi.properties.name = "BIM_MT_new_project"
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Window", space_type="EMPTY")
        kmi = km.keymap_items.new("export_ifc.bim", "S", "PRESS", ctrl=True)
        kmi.properties.should_save_as = False
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.types.TOPBAR_MT_file.remove(ui.file_menu)
    bpy.types.TOPBAR_MT_file_context_menu.remove(ui.file_menu)
    del bpy.types.Scene.BIMProjectProperties

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
