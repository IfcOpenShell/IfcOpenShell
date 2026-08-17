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


def get_render_drawing_style(camera):
    """The drawing style the underlay render will actually use.

    ``CreateDrawing.generate_underlay`` branches on
    ``BIMCameraProperties.get_active_drawing_style()`` -- the row highlighted in the
    Drawing Styles list for this camera -- so that, and not the pset's
    ``CurrentShadingStyle``, decides whether the compositor runs.

    The two drift apart in practice: ``CurrentShadingStyle`` is only rewritten by
    ``bim.activate_drawing_style``, and ``bim.reload_drawing_styles`` leaves the index
    pointing at whatever it pointed at before (often index 0) when it can't find that
    style name in the drawing's shading_styles.json. Gating on the pset then reads
    "Blender Default" while the render is really using style 0.
    """
    return tool.Drawing.get_camera_props(camera).get_active_drawing_style()


def get_current_shading_style_name(camera):
    """EPset_Drawing.CurrentShadingStyle -- what the Drawing Styles panel displays."""
    drawing = tool.Ifc.get_entity(camera)
    if not drawing:
        return None
    return ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", "CurrentShadingStyle")


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
        # (and F12). Gate on exactly what the underlay render branches on -- the camera's
        # highlighted drawing style -- so the panel can never disagree with the render.
        render_style = get_render_drawing_style(camera)
        blocked = render_style is None or render_style.render_type != "DEFAULT"

        if blocked:
            col = layout.column(align=True)
            if render_style is None:
                col.label(text="No drawing style resolved for this camera,", icon="ERROR")
                col.label(text="so the underlay cannot render at all.")
                col.label(text="Press Reload Drawing Styles in Drawing Styles.")
            else:
                col.label(text=f"Style '{render_style.name}' has render type", icon="ERROR")
                col.label(text=f"'{render_style.render_type.title()}', so the compositor")
                col.label(text="is bypassed. Use a Default-render style.")
                # CurrentShadingStyle is what the Drawing Styles panel shows, and it goes
                # stale whenever reload can't find its name in shading_styles.json -- the
                # render keeps using the highlighted row. Call the mismatch out here,
                # otherwise the two panels appear to contradict each other.
                current = get_current_shading_style_name(camera)
                if current and current != render_style.name:
                    col.separator()
                    col.label(text=f"(EPset_Drawing says '{current}', but that", icon="INFO")
                    col.label(text="is not the style being rendered.)")

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
