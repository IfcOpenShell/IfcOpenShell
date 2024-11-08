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

import bpy
from . import ui, prop, operator, workspace, gizmo, decorator

classes = (
    operator.AppendEntireLibrary,
    operator.AppendInspectedLinkedElement,
    operator.AppendLibraryElement,
    operator.AppendLibraryElementByQuery,
    operator.AssignLibraryDeclaration,
    operator.BIM_OT_load_clipping_planes,
    operator.BIM_OT_save_clipping_planes,
    operator.ChangeLibraryElement,
    operator.ClearRecentIFCProjects,
    operator.CreateClippingPlane,
    operator.CreateProject,
    operator.DisableCulling,
    operator.DisableEditingHeader,
    operator.EditHeader,
    operator.EnableCulling,
    operator.EnableEditingHeader,
    operator.ExportIFC,
    operator.FlipClippingPlane,
    operator.LinkIfc,
    operator.LoadLink,
    operator.LoadLinkedProject,
    operator.LoadProject,
    operator.LoadProjectElements,
    operator.MeasureTool,
    operator.NewProject,
    operator.QueryLinkedElement,
    operator.RefreshClippingPlanes,
    operator.RefreshLibrary,
    operator.ReloadLink,
    operator.RevertProject,
    operator.RewindLibrary,
    operator.SaveLibraryFile,
    operator.SelectLibraryFile,
    operator.SelectLinkHandle,
    operator.ToggleFilterCategories,
    operator.ToggleLinkSelectability,
    operator.ToggleLinkVisibility,
    operator.UnassignLibraryDeclaration,
    operator.UnlinkIfc,
    operator.UnloadLink,
    workspace.ExploreHotkey,
    prop.LibraryElement,
    prop.FilterCategory,
    prop.Link,
    prop.EditedObj,
    prop.BIMProjectProperties,
    prop.MeasureToolSettings,
    ui.BIM_MT_new_project,
    ui.BIM_MT_project,
    ui.BIM_PT_new_project_wizard,
    ui.BIM_MT_recent_projects,
    ui.BIM_PT_project,
    ui.BIM_PT_project_library,
    ui.BIM_PT_links,
    ui.BIM_PT_purge,
    ui.BIM_UL_library,
    ui.BIM_UL_filter_categories,
    ui.BIM_UL_links,
    gizmo.ClippingPlane,
)

if bpy.app.version >= (4, 1, 0):
    classes += (
        operator.IFCFileHandlerOperator,
        operator.BIM_FH_import_ifc,
    )

addon_keymaps = []


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.ExploreTool, after={"builtin.transform"}, separator=True, group=False)
    bpy.types.Scene.BIMProjectProperties = bpy.props.PointerProperty(type=prop.BIMProjectProperties)
    bpy.types.Scene.MeasureToolSettings = bpy.props.PointerProperty(type=prop.MeasureToolSettings)
    bpy.app.handlers.load_post.append(decorator.toggle_decorations_on_load)
    bpy.types.TOPBAR_MT_file_import.append(ui.file_import_menu)
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
        kmi = km.keymap_items.new("bim.save_project", "S", "PRESS", ctrl=True)
        kmi.properties.should_save_as = False
        addon_keymaps.append((km, kmi))


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.ExploreTool)
    del bpy.types.Scene.BIMProjectProperties
    del bpy.types.Scene.MeasureToolSettings
    bpy.app.handlers.load_post.remove(decorator.toggle_decorations_on_load)
    bpy.types.TOPBAR_MT_file.remove(ui.file_menu)
    bpy.types.TOPBAR_MT_file_context_menu.remove(ui.file_menu)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
