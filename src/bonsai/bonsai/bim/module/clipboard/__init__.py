# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
from . import operator, prop, ui
from bpy.app.handlers import persistent
import os
import bonsai.tool as tool

classes = (
    operator.CopyToClipboard,
    operator.PasteFromClipboard,
    prop.ClipboardSection,
    prop.BIMClipboardProperties,
    ui.BIM_PT_tab_clipboard,
)

addon_keymaps = []


@persistent
def load_post_handler(dummy):
    clipboard_json = tool.Blender.get_data_dir_path("bonsai_clipboard.json").__str__()
    clipboard_ifc = tool.Blender.get_data_dir_path("bonsai_clipboard.ifc").__str__()
    
    if os.path.exists(clipboard_json) and os.path.exists(clipboard_ifc):
        bpy.context.scene.BIMClipboardProperties.ensure_sections()


def register():
    bpy.types.Scene.BIMClipboardProperties = bpy.props.PointerProperty(type=prop.BIMClipboardProperties)
    bpy.app.handlers.load_post.append(load_post_handler)
    
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.copy_to_clipboard", "C", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.paste_from_clipboard", "V", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    del bpy.types.Scene.BIMClipboardProperties
    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)

