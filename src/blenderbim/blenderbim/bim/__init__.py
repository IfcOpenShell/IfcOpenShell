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

import os
from pathlib import Path
import bpy
import bpy.utils.previews
import blenderbim
import importlib
from . import handler, ui, prop, operator, helper

cwd = os.path.dirname(os.path.realpath(__file__))

modules = {
    "project": None,
    "search": None,
    "bcf": None,
    "root": None,
    "unit": None,
    "model": None,
    "cad": None,
    "georeference": None,
    "context": None,
    "drawing": None,
    "misc": None,
    "attribute": None,
    "type": None,
    "spatial": None,
    "void": None,
    "aggregate": None,
    "geometry": None,
    "cobie": None,
    "resource": None,
    "cost": None,
    "sequence": None,
    "group": None,
    "system": None,
    "brick": None,
    "structural": None,
    "boundary": None,
    "profile": None,
    "material": None,
    "style": None,
    "layer": None,
    "owner": None,
    "pset": None,
    "qto": None,
    "classification": None,
    "library": None,
    "constraint": None,
    "document": None,
    "pset_template": None,
    "clash": None,
    "lca": None,
    "csv": None,
    "tester": None,
    "bimtester": None,
    "diff": None,
    "patch": None,
    "gis": None,
    "covetool": None,
    "augin": None,
    "debug": None,
    "ifcgit": None,
    # Uncomment this line to enable loading of the demo module. Happy hacking!
    # The name "demo" must correlate to a folder name in `bim/module/`.
    # "demo": None,
}


for name in modules.keys():
    modules[name] = importlib.import_module(f"blenderbim.bim.module.{name}")


classes = [
    operator.AddIfcFile,
    operator.BIM_OT_add_section_plane,
    operator.BIM_OT_remove_section_plane,
    operator.ConfigureVisibility,
    operator.OpenUpstream,
    operator.OpenUri,
    operator.SwitchTab,
    operator.SetTab,
    operator.ReloadIfcFile,
    operator.RemoveIfcFile,
    operator.SelectDataDir,
    operator.SelectIfcFile,
    operator.ReloadSelectedIfcFile,
    operator.SelectSchemaDir,
    operator.FileAssociate,
    operator.FileUnassociate,
    operator.SelectURIAttribute,
    operator.EditBlenderCollection,
    operator.BIM_OT_open_webbrowser,
    operator.BIM_OT_show_description,
    prop.StrProperty,
    operator.BIM_OT_enum_property_search,  # /!\ Register AFTER prop.StrProperty
    prop.ObjProperty,
    prop.Attribute,
    prop.ModuleVisibility,
    prop.BIMAreaProperties,
    prop.BIMProperties,
    prop.IfcParameter,
    prop.PsetQto,
    prop.GlobalId,
    prop.BIMObjectProperties,
    prop.BIMCollectionProperties,
    prop.BIMMaterialProperties,
    prop.BIMMeshProperties,
    ui.BIM_UL_generic,
    ui.BIM_UL_topics,
    ui.BIM_ADDON_preferences,
    # Project overview
    ui.BIM_PT_project_info,
    ui.BIM_PT_project_setup,
    ui.BIM_PT_geometry,
    ui.BIM_PT_tab_grouping_and_filtering,
    # Tabs panel
    ui.BIM_PT_tabs,
    # Object information
    ui.BIM_PT_tab_object_metadata,
    ui.BIM_PT_tab_misc,
    # Geometry and materials
    ui.BIM_PT_tab_representations,
    ui.BIM_PT_tab_geometric_relationships,
    ui.BIM_PT_tab_parametric_geometry,
    ui.BIM_PT_tab_materials,
    ui.BIM_PT_tab_styles,
    # Drawings and documents
    # Services and systems
    ui.BIM_PT_tab_services,
    ui.BIM_PT_tab_services_object,
    # Structural analysis
    ui.BIM_PT_tab_structural,
    # Construction scheduling
    ui.BIM_PT_tab_4D5D,
    # Facility management
    ui.BIM_PT_tab_handover,
    ui.BIM_PT_tab_operations,
    # Quality and coordination
    ui.BIM_PT_tab_quality_control,
    ui.BIM_PT_tab_collaboration,
    ui.BIM_PT_tab_sandbox,
    # TODO: move this somewhere else and clean it up
    ui.BIM_PT_section_plane,
]

for mod in modules.values():
    classes.extend(mod.classes)

addon_keymaps = []
icons = None
is_registering = False
last_commit_hash = "8888888"


def on_register(scene):
    global is_registering

    if is_registering:
        return
    is_registering = True
    handler.load_post(scene)
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.remove(on_register)
    is_registering = False


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(on_register)
    bpy.app.handlers.undo_post.append(handler.undo_post)
    bpy.app.handlers.redo_post.append(handler.redo_post)
    bpy.app.handlers.load_post.append(handler.load_post)
    bpy.app.handlers.load_post.append(handler.loadIfcStore)
    bpy.types.Scene.BIMProperties = bpy.props.PointerProperty(type=prop.BIMProperties)
    bpy.types.Screen.BIMAreaProperties = bpy.props.CollectionProperty(type=prop.BIMAreaProperties)
    bpy.types.Collection.BIMCollectionProperties = bpy.props.PointerProperty(type=prop.BIMCollectionProperties)
    bpy.types.Object.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
    bpy.types.Material.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
    bpy.types.Material.BIMMaterialProperties = bpy.props.PointerProperty(type=prop.BIMMaterialProperties)
    bpy.types.Mesh.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
    bpy.types.Curve.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
    bpy.types.Camera.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
    bpy.types.PointLight.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
    if hasattr(bpy.types, "UI_MT_button_context_menu"):
        bpy.types.UI_MT_button_context_menu.append(ui.draw_custom_context_menu)
    bpy.types.STATUSBAR_HT_header.append(ui.draw_statusbar)

    for mod in modules.values():
        mod.register()

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new('bim.switch_tab', 'TAB', 'PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

    global icons

    icons_dir = os.path.join(cwd, "data", "icons")
    icon_preview = bpy.utils.previews.new()
    for filename in os.listdir(icons_dir):
        if filename.endswith(".png"):
            icon_name = os.path.splitext(filename)[0]
            icon_path = os.path.join(icons_dir, filename)
            icon_preview.load(icon_name, icon_path, "IMAGE")

    icons = icon_preview

    global last_commit_hash
    try:
        import git
        path = Path(__file__).resolve().parent
        repo = git.Repo(str(path), search_parent_directories=True)
        last_commit_hash = repo.head.object.hexsha
    except:
        pass

def unregister():
    global icons

    bpy.utils.previews.remove(icons)

    for cls in reversed(classes):
        # GizmoGroup, Gizmo and Macro doesn't have cls.is_registered attribute
        if set((bpy.types.GizmoGroup, bpy.types.Gizmo)) & set(cls.__bases__):
            if bpy.data.scenes["Scene"].BIMProperties.module_visibility["drawing"].is_visible:
                bpy.utils.unregister_class(cls)
            continue

        if bpy.types.Macro in cls.__bases__:
            bpy.utils.unregister_class(cls)
            continue

        if getattr(cls, "is_registered", None) is None:
            bpy.utils.unregister_class(cls)
        else:
            if cls.is_registered is not False:
                bpy.utils.unregister_class(cls)

    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.app.handlers.load_post.remove(handler.loadIfcStore)
    del bpy.types.Scene.BIMProperties
    del bpy.types.Collection.BIMCollectionProperties
    del bpy.types.Object.BIMObjectProperties
    del bpy.types.Material.BIMObjectProperties
    del bpy.types.Material.BIMMaterialProperties
    del bpy.types.Mesh.BIMMeshProperties
    del bpy.types.Curve.BIMMeshProperties
    del bpy.types.Camera.BIMMeshProperties
    del bpy.types.PointLight.BIMMeshProperties
    if hasattr(bpy.types, "UI_MT_button_context_menu"):
        bpy.types.UI_MT_button_context_menu.remove(ui.draw_custom_context_menu)
    bpy.types.STATUSBAR_HT_header.remove(ui.draw_statusbar)

    for mod in reversed(list(modules.values())):
        mod.unregister()

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for panel in [
        "SCENE_PT_scene",
        "SCENE_PT_unit",
        "SCENE_PT_physics",
        "SCENE_PT_rigid_body_world",
        "SCENE_PT_audio",
        "SCENE_PT_keying_sets",
        "SCENE_PT_custom_props",
    ]:
        try:
            bpy.utils.unregister_class(getattr(handler, f"Override_{panel}"))
        except:
            pass
