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
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.bim.helper
from bonsai.bim.module.search.data import SearchData


def get_applied_drawing_style(camera):
    """The shading style currently applied to the drawing (EPset_Drawing.CurrentShadingStyle),
    which is what actually drives the render type -- not whichever style is selected in the list."""
    drawing = tool.Ifc.get_entity(camera)
    if not drawing:
        return None
    name = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", "CurrentShadingStyle")
    if not name:
        return None
    dprops = tool.Drawing.get_document_props()
    return next((style for style in dprops.drawing_styles if style.name == name), None)


class BIM_UL_render_override_rules(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon="SHADERFX")


class BIM_PT_status_render(bpy.types.Panel):
    bl_label = "Render Overrides"
    bl_idname = "BIM_PT_status_render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_camera"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # Same as the sibling drawing panels: only for an active IFC drawing camera.
        return bool((camera := context.scene.camera) and tool.Ifc.get_entity(camera))

    def draw(self, context):
        layout = self.layout
        camera = context.scene.camera
        props = camera.data.BIMRenderOverrideProperties

        # The override needs the compositor, which only runs for Default-render drawings
        # (and F12). Gate on the *applied* shading style (CurrentShadingStyle), since that
        # is what drives the render -- not whichever style is highlighted in the list.
        applied_style = get_applied_drawing_style(camera)
        blocked = applied_style is not None and applied_style.render_type != "DEFAULT"

        if blocked:
            col = layout.column(align=True)
            col.label(text="Current Shading Style is not 'Default'", icon="ERROR")
            col.label(text="render type, so the compositor is bypassed.")
            col.label(text="Apply a Default-render shading style.")

        header = layout.column()
        header.enabled = not blocked
        header.prop(props, "enabled", toggle=True, icon="RENDER_RESULT")

        # When the compositor is bypassed, the rules can't do anything -- hide them so
        # only the greyed toggle and the explanation remain.
        if blocked:
            return

        row = layout.row()
        row.template_list(
            "BIM_UL_render_override_rules", "", props, "rules", props, "active_rule_index", rows=3
        )
        col = row.column(align=True)
        col.operator("bim.add_render_override_rule", icon="ADD", text="")
        col.operator("bim.remove_render_override_rule", icon="REMOVE", text="")

        if 0 <= props.active_rule_index < len(props.rules):
            rule = props.rules[props.active_rule_index]
            box = layout.box()
            box.active = props.enabled
            box.prop(rule, "name")

            # Per-rule filter (same UI as bim.search), keyed to this rule's index.
            bonsai.bim.helper.draw_filter(
                box, rule.filter_groups, SearchData, f"status_render_{props.active_rule_index}"
            )

            col = box.column(align=True)
            col.label(text="Effects:")
            col.prop(rule, "exposure")
            col.prop(rule, "gamma")
            col.prop(rule, "transparency")

        if not blocked:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Applied automatically during F12 and", icon="INFO")
            col.label(text="Default-render drawing underlays, then")
            col.label(text="removed. The drawing needs an underlay.")
