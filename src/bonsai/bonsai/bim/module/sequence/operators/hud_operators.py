# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Federico Eraso <feraso@svisuals.net
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

# Description: Operators for managing the 2D/3D Head-Up Display (HUD), including text, legends, and GPU overlays.

import bpy
import bonsai.tool as tool
from .. import hud as hud_overlay

# ============================================================================
# 3D TEXT HUD OPERATORS
# ============================================================================

class ArrangeScheduleTexts(bpy.types.Operator):
    bl_idname = "bim.arrange_schedule_texts"
    bl_label = "Auto-Arrange Schedule Texts"
    bl_description = "Arranges the 3D schedule texts to a predefined layout"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        parent_empty = bpy.data.objects.get("Schedule_Display_Parent")
        if parent_empty:
            parent_empty.location = (0, 0, 0)
            parent_empty.rotation_euler = (0, 0, 0)
            parent_empty.scale = (1, 1, 1)

        collection = bpy.data.collections.get("Schedule_Display_Texts")
        if not collection:
            self.report({'WARNING'}, "No schedule texts found")
            return {'CANCELLED'}

        text_states = {
            "Schedule_Name": {"pos": (-3.1, 13.3, 0), "size": 1.0, "color": (1, 1, 1, 1)},
            "Schedule_Date": {"pos": (0, 12, 0), "size": 1.2, "color": (1, 1, 1, 1)},
            "Schedule_Week": {"pos": (0, 10.8, 0), "size": 1.0, "color": (1, 1, 1, 1)},
            "Schedule_Day_Counter": {"pos": (-0.34, 9.75, 0), "size": 0.8, "color": (1.0, 1.0, 1.0, 1.0)},
            "Schedule_Progress": {"pos": (0.37, 8.8, 0), "size": 1.0, "color": (1.0, 1.0, 1.0, 1.0)},
        }

        for name, state in text_states.items():
            text_obj = collection.objects.get(name)
            if not text_obj:
                continue

            if hasattr(text_obj.data, 'align_y'):
                text_obj.data.align_y = 'BOTTOM_BASELINE'
            if hasattr(text_obj.data, 'align_x'):
                text_obj.data.align_x = 'CENTER'
            
            corrected_pos = (state["pos"][0], state["pos"][1], 0.0)
            text_obj.location = corrected_pos
            
            if hasattr(text_obj.data, 'size'):
                text_obj.data.size = state["size"]
            
            if hasattr(text_obj.data, 'offset_x'):
                text_obj.data.offset_x = 0.0
            if hasattr(text_obj.data, 'offset_y'):
                text_obj.data.offset_y = 0.0

            if state["color"]:
                if not text_obj.data.materials:
                    mat = bpy.data.materials.new(name=f"{name}_Material")
                    text_obj.data.materials.append(mat)
                    mat.use_nodes = True
                else:
                    mat = text_obj.data.materials[0]

                if mat.use_nodes and mat.node_tree:
                    bsdf = mat.node_tree.nodes.get("Principled BSDF")
                    if not bsdf:
                        bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
                        output_node = mat.node_tree.nodes.get('Material Output')
                        if output_node:
                            mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
                    if bsdf:
                        bsdf.inputs['Base Color'].default_value = state["color"]

        self._ensure_all_texts_proper_alignment(collection)
        self.report({'INFO'}, "Texts arranged to default layout with proper Z=0 alignment")
        return {'FINISHED'}
    
    def _ensure_all_texts_proper_alignment(self, collection):
        for obj in collection.objects:
            if obj.type == 'FONT':
                if hasattr(obj.data, 'align_x'):
                    obj.data.align_x = 'CENTER'
                if hasattr(obj.data, 'align_y'):
                    obj.data.align_y = 'BOTTOM_BASELINE'
                if hasattr(obj.data, 'offset_x'):
                    obj.data.offset_x = 0.0
                if hasattr(obj.data, 'offset_y'):
                    obj.data.offset_y = 0.0
                current_loc = obj.location
                if abs(current_loc.z) > 0.001:
                    obj.location = (current_loc.x, current_loc.y, 0.0)


class Fix3DTextAlignment(bpy.types.Operator):
    bl_idname = "bim.fix_3d_text_alignment"
    bl_label = "Fix 3D Text Alignment"
    bl_description = "Ensures all 3D texts are vertically and horizontally aligned with Z=0 height"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        fixed_count = 0
        for obj in bpy.data.objects:
            if obj.type == 'FONT':
                fixed_count += 1
                if hasattr(obj.data, 'align_x'):
                    obj.data.align_x = 'CENTER'
                if hasattr(obj.data, 'align_y'):
                    obj.data.align_y = 'BOTTOM_BASELINE'
                if hasattr(obj.data, 'offset_x'):
                    obj.data.offset_x = 0.0
                if hasattr(obj.data, 'offset_y'):
                    obj.data.offset_y = 0.0
                current_location = obj.location
                obj.location = (current_location.x, current_location.y, 0.0)
                obj.update_tag()
        
        parent_empty = bpy.data.objects.get("Schedule_Display_Parent")
        if parent_empty:
            parent_empty.location = (0, 0, 0)
            parent_empty.rotation_euler = (0, 0, 0)
            parent_empty.scale = (1, 1, 1)
        
        if context.view_layer:
            context.view_layer.update()
        
        self.report({'INFO'}, f"Fixed alignment for {fixed_count} 3D text objects with Z=0 height")
        return {'FINISHED'}


# ==============================
# 3D TEXT HUD 
# ==============================

class SetupTextHUD(bpy.types.Operator):
    bl_idname = "bim.setup_text_hud"
    bl_label = "Setup Text HUD"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        try:
            active_camera = context.scene.camera
            if not active_camera:
                self.report({'ERROR'}, "No active camera found")
                return {'CANCELLED'}

            collection = bpy.data.collections.get("Schedule_Display_Texts")
            if not collection:
                self.report({'WARNING'}, "No schedule texts found")
                return {'CANCELLED'}

            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit

            text_objects = self._get_ordered_text_objects(collection)

            for i, text_obj in enumerate(text_objects):
                if text_obj:
                    self._setup_text_as_hud(text_obj, active_camera, i, camera_props)

            self.report({'INFO'}, f"HUD configured for {len([t for t in text_objects if t])} text objects")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to setup HUD: {e}")
            return {'CANCELLED'}

    def _get_ordered_text_objects(self, collection):
        order = ["Schedule_Date", "Schedule_Week", "Schedule_Day_Counter", "Schedule_Progress"]
        return [collection.objects.get(name) for name in order]

    def _setup_text_as_hud(self, text_obj, camera, index, camera_props):
        for c in list(text_obj.constraints):
            if "HUD" in c.name:
                text_obj.constraints.remove(c)

        child_constraint = text_obj.constraints.new(type='CHILD_OF')
        child_constraint.name = "HUD_Follow_Camera"
        child_constraint.target = camera

        for axis in ('x', 'y', 'z'):
            setattr(child_constraint, f'use_location_{axis}', True)
            setattr(child_constraint, f'use_rotation_{axis}', False)
            setattr(child_constraint, f'use_scale_{axis}', False)

        try:
            child_constraint.inverse_matrix = camera.matrix_world.inverted()
        except Exception:
            pass

        local_position = self._calculate_hud_position(camera, index, camera_props)
        text_obj.location = local_position

        self._update_text_scale(text_obj, camera, camera_props)

        text_obj["is_hud_element"] = True
        text_obj["hud_index"] = int(index)

    def _get_aspect_ratio(self, scene):
        try:
            r = scene.render
            w = float(getattr(r, "resolution_x", 1920)) * float(getattr(r, "pixel_aspect_x", 1.0))
            h = float(getattr(r, "resolution_y", 1080)) * float(getattr(r, "pixel_aspect_y", 1.0))
            if h == 0: return 1.0
            return max(0.0001, w / h)
        except Exception:
            return 1.0

    def _calculate_hud_position(self, camera, index, camera_props):
        import mathutils
        scene = bpy.context.scene
        cam_data = camera.data
        aspect = self._get_aspect_ratio(scene)
        distance_plane = -10.0

        if cam_data.type == 'PERSP':
            sensor_width = float(getattr(cam_data, "sensor_width", 36.0))
            focal_length = float(getattr(cam_data, "lens", 50.0))
            view_width_at_dist = (sensor_width / max(0.001, focal_length)) * abs(distance_plane)
            view_height_at_dist = view_width_at_dist / (aspect if aspect else 1.0)
        else:
            view_height_at_dist = float(getattr(cam_data, "ortho_scale", 10.0))
            view_width_at_dist = view_height_at_dist * (aspect if aspect else 1.0)

        margin_h = view_width_at_dist * float(getattr(camera_props, "hud_margin_horizontal", 0.05))
        margin_v = view_height_at_dist * float(getattr(camera_props, "hud_margin_vertical", 0.05))
        spacing  = view_height_at_dist * float(getattr(camera_props, "hud_text_spacing", 0.08))
        pos = str(getattr(camera_props, "hud_position", "TOP_LEFT"))

        if pos == 'TOP_LEFT':
            base_x = -view_width_at_dist / 2.0 + margin_h
            base_y =  view_height_at_dist / 2.0 - margin_v
        elif pos == 'TOP_RIGHT':
            base_x =  view_width_at_dist / 2.0 - margin_h
            base_y =  view_height_at_dist / 2.0 - margin_v
        elif pos == 'BOTTOM_LEFT':
            base_x = -view_width_at_dist / 2.0 + margin_h
            base_y = -view_height_at_dist / 2.0 + margin_v
        else:
            base_x =  view_width_at_dist / 2.0 - margin_h
            base_y = -view_height_at_dist / 2.0 + margin_v

        pos_y = base_y - (int(index) * spacing) if pos.startswith('TOP') else base_y + (int(index) * spacing)
        return mathutils.Vector((base_x, pos_y, distance_plane))

    def _update_text_scale(self, text_obj, camera, camera_props):
        try:
            base_scale = 0.5 * float(getattr(camera_props, "hud_scale_factor", 1.0))
        except Exception:
            base_scale = 0.5
        text_obj.scale = (base_scale, base_scale, base_scale)


class ClearTextHUD(bpy.types.Operator):
    bl_idname = "bim.clear_text_hud"
    bl_label = "Clear Text HUD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            collection = bpy.data.collections.get("Schedule_Display_Texts")
            if not collection: return {'FINISHED'}
            cleared_count = 0
            for text_obj in list(collection.objects):
                if text_obj.get("is_hud_element", False):
                    for constraint in list(text_obj.constraints):
                        if "HUD" in getattr(constraint, "name", ""):
                            try:
                                text_obj.constraints.remove(constraint)
                            except Exception: pass
                    try:
                        if "is_hud_element" in text_obj: del text_obj["is_hud_element"]
                        if "hud_index" in text_obj: del text_obj["hud_index"]
                    except Exception: pass
                    cleared_count += 1
            self.report({'INFO'}, f"HUD cleared from {cleared_count} text objects")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear HUD: {e}")
            return {'CANCELLED'}


class UpdateTextHUDPositions(bpy.types.Operator):
    bl_idname = "bim.update_text_hud_positions"
    bl_label = "Update HUD Positions"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            active_camera = context.scene.camera
            if not active_camera: return {'CANCELLED'}
            collection = bpy.data.collections.get("Schedule_Display_Texts")
            if not collection: return {'CANCELLED'}
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            setup_operator = SetupTextHUD()
            for text_obj in list(collection.objects):
                if text_obj.get("is_hud_element", False):
                    index = int(text_obj.get("hud_index", 0))
                    local_position = setup_operator._calculate_hud_position(active_camera, index, camera_props)
                    try:
                        text_obj.location = local_position
                    except Exception:
                        text_obj.location = (float(local_position.x), float(local_position.y), float(local_position.z))
            return {'FINISHED'}
        except Exception as e:
            print(f"Error updating HUD positions: {e}")
            return {'CANCELLED'}


class UpdateTextHUDScale(bpy.types.Operator):
    bl_idname = "bim.update_text_hud_scale"
    bl_label = "Update HUD Scale"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            active_camera = context.scene.camera
            if not active_camera: return {'CANCELLED'}
            collection = bpy.data.collections.get("Schedule_Display_Texts")
            if not collection: return {'CANCELLED'}
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            setup_operator = SetupTextHUD()
            for text_obj in list(collection.objects):
                if text_obj.get("is_hud_element", False):
                    setup_operator._update_text_scale(text_obj, active_camera, camera_props)
            return {'FINISHED'}
        except Exception as e:
            print(f"Error updating HUD scale: {e}")
            return {'CANCELLED'}


class ToggleTextHUD(bpy.types.Operator):
    bl_idname = "bim.toggle_text_hud"
    bl_label = "Toggle Text HUD"
    bl_description = "Enable/disable text HUD attachment to active camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            camera_props.enable_text_hud = not bool(camera_props.enable_text_hud)
            if camera_props.enable_text_hud:
                bpy.ops.bim.setup_text_hud()
                self.report({'INFO'}, "Text HUD enabled")
            else:
                bpy.ops.bim.clear_text_hud()
                self.report({'INFO'}, "Text HUD disabled")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to toggle HUD: {e}")
            return {'CANCELLED'}

# ==============================
# 3D LEGEND HUD OPERATORS
# ==============================

class Setup3DLegendHUD(bpy.types.Operator):
    bl_idname = "bim.setup_3d_legend_hud"
    bl_label = "Setup 3D Legend HUD"
    bl_description = "Create 3D Legend HUD with current active ColorTypes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            bpy.ops.bim.clear_3d_legend_hud()
            active_camera = context.scene.camera
            if not active_camera:
                self.report({'ERROR'}, "No active camera found")
                return {'CANCELLED'}
            legend_data = self._get_active_colortype_data()
            if not legend_data:
                self.report({'WARNING'}, "No active ColorTypes found")
                return {'CANCELLED'}
            self._create_3d_legend_hud(active_camera, legend_data)
            self.report({'INFO'}, f"3D Legend HUD created with {len(legend_data)} ColorTypes")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to setup 3D Legend HUD: {e}")
            return {'CANCELLED'}
    
    def _get_active_colortype_data(self):
        try:

            # Check if we're in snapshot mode
            is_snapshot = bpy.context.scene.get("is_snapshot_mode", False)

            # Check HUD overlay availability
            has_schedule_hud = hasattr(hud_overlay, 'schedule_hud') and hud_overlay.schedule_hud

            if has_schedule_hud:
                hud_instance = hud_overlay.schedule_hud
            else:
                hud_instance = hud_overlay.ScheduleHUD()

            legend_data = hud_instance.get_active_colortype_legend_data(include_hidden=False)

            for i, item in enumerate(legend_data[:3]):  # Show first 3 items
                pass  # Process legend items (removed debug code)

            return legend_data
        except Exception as e:
            print(f"[ERROR] Exception in _get_active_colortype_data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_synchronized_settings(self, camera_props):
        base_3d_scale = 0.015
        legend_scale = getattr(camera_props, 'legend_hud_scale', 1.0)
        spacing_scale = base_3d_scale * legend_scale
        settings = {
            'hud_distance': getattr(camera_props, 'legend_3d_hud_distance', 2.2),
            'hud_pos_x': getattr(camera_props, 'legend_3d_hud_pos_x', -3.6),
            'hud_pos_y': getattr(camera_props, 'legend_3d_hud_pos_y', 1.4),
            'hud_scale': legend_scale,
            'panel_width': getattr(camera_props, 'legend_3d_panel_width', 2.2),
            'panel_radius': getattr(camera_props, 'legend_hud_border_radius', 5.0) * spacing_scale,
            'panel_alpha': getattr(camera_props, 'legend_hud_background_color', (0.05, 0.05, 0.05, 0.85))[3],
            'panel_color': getattr(camera_props, 'legend_hud_background_color', (0.05, 0.05, 0.05, 1.0)),
            'font_size_title': getattr(camera_props, 'legend_hud_title_font_size', 16.0) * base_3d_scale * legend_scale,
            'font_size_item': 14.0 * base_3d_scale * legend_scale,
            'padding_x': getattr(camera_props, 'legend_hud_padding_horizontal', 12.0) * spacing_scale,
            'padding_top': getattr(camera_props, 'legend_hud_padding_vertical', 8.0) * spacing_scale,
            'padding_bottom': getattr(camera_props, 'legend_hud_padding_vertical', 8.0) * spacing_scale,
            'row_height': getattr(camera_props, 'legend_hud_item_spacing', 8.0) * spacing_scale * 2.0,
            'dot_diameter': getattr(camera_props, 'legend_hud_color_indicator_size', 12.0) * spacing_scale,
            'dot_text_gap': getattr(camera_props, 'legend_hud_item_spacing', 8.0) * spacing_scale * 1.2,
            'title_text': getattr(camera_props, 'legend_hud_title_text', 'Legend'),
            'show_title': getattr(camera_props, 'legend_hud_show_title', True),
            'title_color': getattr(camera_props, 'legend_hud_title_color', (1.0, 1.0, 1.0, 1.0)),
            'text_color': getattr(camera_props, 'legend_hud_text_color', (1.0, 1.0, 1.0, 1.0)),
            'text_shadow_enabled': getattr(camera_props, 'legend_hud_text_shadow_enabled', True),
            'text_shadow_color': getattr(camera_props, 'legend_hud_text_shadow_color', (0.0, 0.0, 0.0, 0.8)),
            'text_shadow_offset_x': getattr(camera_props, 'legend_hud_text_shadow_offset_x', 1.0) * spacing_scale,
            'text_shadow_offset_y': getattr(camera_props, 'legend_hud_text_shadow_offset_y', -1.0) * spacing_scale,
            'show_start_column': getattr(camera_props, 'legend_hud_show_start_column', False),
            'show_active_column': getattr(camera_props, 'legend_hud_show_active_column', True),
            'show_end_column': getattr(camera_props, 'legend_hud_show_end_column', False),
            'show_start_title': getattr(camera_props, 'legend_hud_show_start_title', False),
            'show_active_title': getattr(camera_props, 'legend_hud_show_active_title', False),
            'show_end_title': getattr(camera_props, 'legend_hud_show_end_title', False),
            'column_spacing': getattr(camera_props, 'legend_hud_column_spacing', 16.0) * spacing_scale,
            'auto_scale': getattr(camera_props, 'legend_hud_auto_scale', True),
            'max_width': getattr(camera_props, 'legend_hud_max_width', 0.3),
            'orientation': getattr(camera_props, 'legend_hud_orientation', 'VERTICAL'),
        }
        return settings
    
    def _create_3d_legend_hud(self, camera, legend_data):
        """
        RESTORED from v117_P: Full 3D Legend HUD creation with panels and color dots
        """
        try:
            self._create_3d_legend_hud_full(camera, legend_data)
        except Exception as e:
            print(f"[ERROR] Full 3D Legend creation failed: {e}")
            # Fallback: create safe version
            self._create_3d_legend_hud_safe(camera, legend_data)

    def _create_3d_legend_hud_safe(self, camera, legend_data):
        """
        CRASH-SAFE implementation: Creates only simple Empty objects to avoid mesh creation crashes.
        This provides a basic 3D legend placeholder without complex geometry.
        """
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit

        # Create basic collection for 3D legend
        collection_name = "Schedule_Display_3D_Legend"
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)

        # Clear any existing legend objects to avoid duplicates
        for obj in list(collection.objects):
            if obj.get("is_3d_legend_hud", False):
                bpy.data.objects.remove(obj, do_unlink=True)

        # Control visibility based on checkbox
        should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)
        collection.hide_viewport = should_hide
        collection.hide_render = should_hide

        # Create simple parent empty (SAFE - no mesh creation)
        parent_name = "HUD_3D_Legend_Parent"
        parent_empty = bpy.data.objects.get(parent_name)
        if not parent_empty:
            parent_empty = bpy.data.objects.new(parent_name, None)
            collection.objects.link(parent_empty)
            parent_empty.empty_display_type = 'PLAIN_AXES'
            parent_empty.empty_display_size = 0.5
            parent_empty["is_3d_legend_hud"] = True

        # Position the legend near the camera
        if camera:
            parent_empty.location = (camera.location.x + 2, camera.location.y + 2, camera.location.z)
        else:
            parent_empty.location = (2, 2, 0)

        # Create text objects for each legend item (SAFER approach)
        for i, item_data in enumerate(legend_data):
            item_name = item_data.get('name', 'Unknown')

            # Create text object for the legend item name
            text_obj_name = f"Legend_Text_{i:02d}_{item_name}"
            text_obj = self._create_text_object(
                text_obj_name,
                item_name,
                0.3,  # size
                (1, 1, 1, 1),  # white color
                1.0,  # strength
                collection
            )

            if text_obj:
                text_obj.parent = parent_empty
                text_obj.location = (0, -i * 0.5, 0)  # Stack vertically with more spacing
                text_obj["is_3d_legend_hud"] = True
                text_obj["legend_item_data"] = str(item_data)

            # Create simple colored empty as color indicator
            color_indicator_name = f"Legend_Color_{i:02d}_{item_name}"
            color_empty = bpy.data.objects.new(color_indicator_name, None)
            collection.objects.link(color_empty)
            color_empty.parent = parent_empty
            color_empty.location = (-1.0, -i * 0.5, 0)  # To the left of text
            color_empty.empty_display_type = 'SPHERE'
            color_empty.empty_display_size = 0.1
            color_empty["is_3d_legend_hud"] = True

            # Set color if available
            if 'active_color' in item_data and hasattr(color_empty, 'color'):
                active_color = item_data['active_color']
                color_empty.color = (*active_color[:3], 1.0) if len(active_color) >= 3 else (1, 1, 1, 1)

        print(f"   Visibility: {'Hidden' if should_hide else 'Visible'}")

    def _create_minimal_3d_placeholder(self):
        """
        Ultra-minimal fallback: Creates just one empty object as placeholder.
        """
        try:
            collection_name = "Schedule_Display_3D_Legend"
            collection = bpy.data.collections.get(collection_name)
            if not collection:
                collection = bpy.data.collections.new(collection_name)
                bpy.context.scene.collection.children.link(collection)

            placeholder_name = "HUD_3D_Legend_Placeholder"
            if not bpy.data.objects.get(placeholder_name):
                placeholder = bpy.data.objects.new(placeholder_name, None)
                collection.objects.link(placeholder)
                placeholder.empty_display_type = 'CUBE'
                placeholder.empty_display_size = 1.0
                placeholder["is_3d_legend_hud"] = True
                placeholder.location = (0, 0, 0)
        except Exception as e:
            print(f"[ERROR] Even minimal placeholder failed: {e}")

    def _create_3d_legend_hud_full(self, camera, legend_data):
        """
        EXACT COPY from v117_P working version
        """
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        settings = self._get_synchronized_settings(camera_props)
        collection_name = "Schedule_Display_3D_Legend"
        collection = bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
        if collection.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(collection)
        should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)
        collection.hide_viewport = should_hide
        collection.hide_render = should_hide

        # Use Schedule_Display_Parent as root - TODO goes there
        parent_name = "Schedule_Display_Parent"
        parent_empty = bpy.data.objects.get(parent_name)
        if not parent_empty:
            parent_empty = bpy.data.objects.new(parent_name, None)
            bpy.context.scene.collection.objects.link(parent_empty)
            parent_empty.empty_display_type = 'PLAIN_AXES'
            parent_empty.empty_display_size = 2

        # The 3D Legend HUD is created INSIDE Schedule_Display_Parent
        root = parent_empty
        total_rows = len(legend_data)
        title_height = settings['font_size_title'] + 0.12 if settings['show_title'] else 0
        column_titles_height = settings['row_height'] * 0.8 if (settings['show_start_title'] or settings['show_active_title'] or settings['show_end_title']) else 0
        panel_height = settings['padding_top'] + title_height + column_titles_height + total_rows * settings['row_height'] + settings['padding_bottom']
        max_text_length = max((len(item.get('name', '')) for item in legend_data), default=0)
        text_width = max_text_length * settings['font_size_item'] * 0.6
        visible_columns = sum([settings['show_start_column'], settings['show_active_column'], settings['show_end_column']])
        dots_width = settings['dot_diameter'] * visible_columns + settings['column_spacing'] * (visible_columns - 1) if visible_columns > 0 else 0
        content_width = dots_width + settings['dot_text_gap'] + text_width
        panel_width = max((settings['padding_x'] * 2) + content_width, 1.2)
        if settings['auto_scale'] and panel_width > (settings['max_width'] * 10):
            panel_width = settings['max_width'] * 10
        panel = self._create_rounded_panel("HUD_3D_Legend_Panel", panel_width, panel_height, settings['panel_radius'], settings['panel_alpha'], settings['panel_color'], collection)
        if not panel: return
        panel.parent = root
        panel.location = (settings['hud_pos_x'], settings['hud_pos_y'], 0.0)
        panel.scale = (settings['hud_scale'], settings['hud_scale'], settings['hud_scale'])
        panel["is_3d_legend_hud"] = True
        top_y = panel_height * 0.5 - settings['padding_top'] - settings['font_size_title'] * 0.5 if settings['show_title'] else panel_height * 0.5 - settings['padding_top']
        if settings['show_title']:
            title = self._create_text_object("HUD_3D_Legend_Title", settings['title_text'], settings['font_size_title'], settings['title_color'], 5.0, collection)
            title.location = (panel.location.x + (-panel_width * 0.5 + settings['padding_x']) * panel.scale.x, panel.location.y + top_y * panel.scale.y, panel.location.z + 0.0014)
            title.parent = root
        start_y = top_y - (title_height if settings['show_title'] else 0)
        x_dot = -panel_width * 0.5 + settings['padding_x'] + settings['dot_diameter'] * 0.5
        x_text_base = x_dot + settings['dot_diameter'] * 0.5 + settings['dot_text_gap']
        for i, item_data in enumerate(legend_data):
            y = start_y - i * settings['row_height']
            current_dot_x = x_dot
            dot_count = 0
            if settings['show_start_column'] and 'start_color' in item_data:
                dot = self._create_color_dot(f"{root.name}_Dot_Start_{i:02d}", settings['dot_diameter'], item_data['start_color'], collection)
                dot.location = (panel.location.x + current_dot_x * panel.scale.x, panel.location.y + y * panel.scale.y, panel.location.z + 0.001)
                dot.parent = root
                current_dot_x += settings['dot_diameter'] + settings['column_spacing']
                dot_count += 1
            if settings['show_active_column'] and 'active_color' in item_data:
                dot = self._create_color_dot(f"{root.name}_Dot_Active_{i:02d}", settings['dot_diameter'], item_data['active_color'], collection)
                dot.location = (panel.location.x + current_dot_x * panel.scale.x, panel.location.y + y * panel.scale.y, panel.location.z + 0.001)
                dot.parent = root
                current_dot_x += settings['dot_diameter'] + settings['column_spacing']
                dot_count += 1
            if settings['show_end_column'] and 'end_color' in item_data:
                dot = self._create_color_dot(f"{root.name}_Dot_End_{i:02d}", settings['dot_diameter'], item_data['end_color'], collection)
                dot.location = (panel.location.x + current_dot_x * panel.scale.x, panel.location.y + y * panel.scale.y, panel.location.z + 0.001)
                dot.parent = root
            text_x_offset = x_text_base + (current_dot_x - x_dot if dot_count > 0 else 0)
            text = self._create_text_object(f"{root.name}_Text_{i:02d}", item_data.get('name', ''), settings['font_size_item'], settings['text_color'], 5.0, collection)
            text.location = (panel.location.x + text_x_offset * panel.scale.x, panel.location.y + y * panel.scale.y, panel.location.z + 0.0012)
            text.parent = root
        for obj in collection.objects:
            obj["is_3d_legend_hud"] = True

    def _create_rounded_panel(self, name, width, height, radius, alpha, color, collection):
        """
        RESTORED from v117_P working version
        """
        import bmesh
        bm = bmesh.new()
        max_radius = min(width, height) * 0.4
        actual_radius = min(radius, max_radius)
        if actual_radius > 0.005:
            bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=1.0)
            bmesh.ops.scale(bm, vec=(width, height, 1.0), verts=bm.verts)
            try:
                bmesh.ops.inset_individual(bm, faces=bm.faces[:], thickness=actual_radius * 0.5, depth=0.0, use_boundary=True)
            except Exception: pass
        else:
            bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
            bmesh.ops.scale(bm, vec=(width, height, 1.0), verts=bm.verts)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        try:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
        except Exception: pass
        mat = self._create_emission_material(f"{name}_Mat", color, 1.2, alpha)
        obj.data.materials.append(mat)
        return obj

    def _create_rounded_panel_DISABLED(self, name, width, height, radius, alpha, color, collection):
        import bmesh
        bm = bmesh.new()
        max_radius = min(width, height) * 0.4
        actual_radius = min(radius, max_radius)
        if actual_radius > 0.005:
            bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=1.0)
            bmesh.ops.scale(bm, vec=(width, height, 1.0), verts=bm.verts)
            try:
                bmesh.ops.inset_individual(bm, faces=bm.faces[:], thickness=actual_radius * 0.5, depth=0.0, use_boundary=True)
            except Exception: pass
        else:
            bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
            bmesh.ops.scale(bm, vec=(width, height, 1.0), verts=bm.verts)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        try:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
        except Exception: pass
        mat = self._create_emission_material(f"{name}_Mat", color, 1.2, alpha)
        obj.data.materials.append(mat)
        return obj

    def _create_color_dot(self, name, diameter, color, collection):
        """
        RESTORED from v117_P working version
        """
        bpy.ops.mesh.primitive_circle_add(vertices=24, radius=diameter * 0.5, fill_type='NGON')
        obj = bpy.context.active_object
        obj.name = name
        if obj.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(obj)
        if obj.name not in collection.objects:
            collection.objects.link(obj)
        mat = self._create_emission_material(f"{name}_Mat", color, 6.0, 1.0)
        obj.data.materials.append(mat)
        return obj

    def _create_color_dot_DISABLED(self, name, diameter, color, collection):
        bpy.ops.mesh.primitive_circle_add(vertices=24, radius=diameter * 0.5, fill_type='NGON')
        obj = bpy.context.active_object
        obj.name = name
        if obj.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(obj)
        if obj.name not in collection.objects:
            collection.objects.link(obj)
        mat = self._create_emission_material(f"{name}_Mat", color, 6.0, 1.0)
        obj.data.materials.append(mat)
        return obj

    def _create_text_object(self, name, text, size, color, strength, collection):
        """
        RESTORED from v117_P working version
        """
        curve = bpy.data.curves.new(name, 'FONT')
        curve.body = text
        curve.size = size
        curve.align_x = 'LEFT'
        curve.align_y = 'CENTER'
        obj = bpy.data.objects.new(name, curve)
        collection.objects.link(obj)
        mat = self._create_emission_material(f"{name}_Mat", color, strength, 1.0)
        obj.data.materials.append(mat)
        return obj

    def _create_text_object_DISABLED(self, name, text, size, color, strength, collection):
        curve = bpy.data.curves.new(name, 'FONT')
        curve.body = text
        curve.size = size
        curve.align_x = 'LEFT'
        curve.align_y = 'CENTER'
        obj = bpy.data.objects.new(name, curve)
        collection.objects.link(obj)
        mat = self._create_emission_material(f"{name}_Mat", color, strength, 1.0)
        obj.data.materials.append(mat)
        return obj

    def _create_emission_material(self, name, color, strength, alpha):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for node in nodes: nodes.remove(node)
        output = nodes.new("ShaderNodeOutputMaterial")
        if alpha >= 0.999:
            emission = nodes.new("ShaderNodeEmission")
            emission.inputs["Color"].default_value = (color[0], color[1], color[2], 1.0)
            emission.inputs["Strength"].default_value = strength
            links.new(emission.outputs["Emission"], output.inputs["Surface"])
            mat.blend_method = 'OPAQUE'
        else:
            transparent = nodes.new("ShaderNodeBsdfTransparent")
            emission = nodes.new("ShaderNodeEmission")
            emission.inputs["Color"].default_value = (color[0], color[1], color[2], 1.0)
            emission.inputs["Strength"].default_value = strength
            mix = nodes.new("ShaderNodeMixShader")
            value = nodes.new("ShaderNodeValue")
            value.outputs[0].default_value = alpha
            links.new(transparent.outputs["BSDF"], mix.inputs[1])
            links.new(emission.outputs["Emission"], mix.inputs[2])
            links.new(value.outputs[0], mix.inputs[0])
            links.new(mix.outputs["Shader"], output.inputs["Surface"])
            mat.blend_method = 'BLEND'
            try: mat.shadow_method = 'NONE'
            except: pass
        return mat

class Clear3DLegendHUD(bpy.types.Operator):
    bl_idname = "bim.clear_3d_legend_hud"
    bl_label = "Clear 3D Legend HUD"
    bl_description = "Remove all 3D Legend HUD objects and materials"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            cleared_objects = 0
            for obj in list(bpy.data.objects):
                if obj.get("is_3d_legend_hud", False):
                    bpy.data.objects.remove(obj, do_unlink=True)
                    cleared_objects += 1
            for mat in list(bpy.data.materials):
                if mat.name.startswith("HUD_3D_Legend"):
                    bpy.data.materials.remove(mat, do_unlink=True)
            collection_name = "Schedule_Display_3D_Legend"
            if collection_name in bpy.data.collections and not bpy.data.collections[collection_name].objects:
                bpy.data.collections.remove(bpy.data.collections[collection_name])
            self.report({'INFO'}, f"Cleared {cleared_objects} objects")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear 3D Legend HUD: {e}")
            return {'CANCELLED'}

class Update3DLegendHUD(bpy.types.Operator):
    bl_idname = "bim.update_3d_legend_hud"
    bl_label = "Update 3D Legend HUD"
    bl_description = "Refresh 3D Legend HUD with current active ColorTypes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            if any(obj.get("is_3d_legend_hud", False) for obj in bpy.data.objects):
                bpy.ops.bim.clear_3d_legend_hud()
                bpy.ops.bim.setup_3d_legend_hud()
                self.report({'INFO'}, "3D Legend HUD updated")
                return {'FINISHED'}
            else:
                self.report({'INFO'}, "No 3D Legend HUD found to update.")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to update 3D Legend HUD: {e}")
            return {'CANCELLED'}

class Toggle3DLegendHUD(bpy.types.Operator):
    bl_idname = "bim.toggle_3d_legend_hud"
    bl_label = "Toggle 3D Legend HUD"
    bl_description = "Toggle 3D Legend HUD visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            enable_3d_legend = not getattr(camera_props, 'enable_3d_legend_hud', False)
            camera_props.enable_3d_legend_hud = enable_3d_legend
            if enable_3d_legend:
                bpy.ops.bim.setup_3d_legend_hud()
                self.report({'INFO'}, "3D Legend HUD enabled")
            else:
                bpy.ops.bim.clear_3d_legend_hud()
                self.report({'INFO'}, "3D Legend HUD disabled")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to toggle 3D Legend HUD: {e}")
            return {'CANCELLED'}

# ==============================
# GPU OVERLAY HUD OPERATORS
# ==============================

class EnableScheduleHUD(bpy.types.Operator):
    bl_idname = "bim.enable_schedule_hud"
    bl_label = "Enable Schedule HUD"
    bl_description = "Enable GPU-based HUD overlay for schedule information"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            if not camera_props.enable_text_hud:
                camera_props.enable_text_hud = True
            from .. import hud
            if not hud_overlay.is_hud_enabled():
                hud_overlay.register_hud_handler()
            hud_overlay.refresh_hud()
            self.report({'INFO'}, "Schedule HUD enabled")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to enable HUD: {e}")
            return {'CANCELLED'}

class DisableScheduleHUD(bpy.types.Operator):
    bl_idname = "bim.disable_schedule_hud"
    bl_label = "Disable Schedule HUD"
    bl_description = "Disable GPU-based HUD overlay"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            if camera_props.enable_text_hud:
                camera_props.enable_text_hud = False
            from .. import hud
            hud_overlay.unregister_hud_handler()
            for area in context.screen.areas:
                if getattr(area, "type", None) == 'VIEW_3D':
                    area.tag_redraw()
            self.report({'INFO'}, "Schedule HUD disabled")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to disable HUD: {e}")
            return {'CANCELLED'}

class ToggleScheduleHUD(bpy.types.Operator):
    bl_idname = "bim.toggle_schedule_hud"
    bl_label = "Toggle Schedule HUD"
    bl_description = "Toggle GPU-based HUD overlay on/off"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            from .. import hud
            if hud_overlay.is_hud_enabled():
                bpy.ops.bim.disable_schedule_hud()
            else:
                bpy.ops.bim.enable_schedule_hud()
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to toggle HUD: {e}")
            return {'CANCELLED'}

class RefreshScheduleHUD(bpy.types.Operator):
    bl_idname = "bim.refresh_schedule_hud"
    bl_label = "Refresh HUD"
    bl_description = "Refresh HUD display and settings with forced redraw"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            from .. import hud
            hud_overlay.ensure_hud_handlers()
            hud_overlay.refresh_hud()
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
            return {'FINISHED'}
        except Exception as e:
            return {'CANCELLED'}

class LegendHudcolortypeScrollUp(bpy.types.Operator):
    bl_idname = "bim.legend_hud_colortype_scroll_up"
    bl_label = "Scroll Up"
    bl_description = "Scroll up in the legend HUD colortype list"
    bl_options = {"REGISTER"}

    def execute(self, context):
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        current_offset = getattr(camera_props, 'legend_hud_colortype_scroll_offset', 0)
        new_offset = max(0, current_offset - 1)
        if new_offset != current_offset:
            camera_props.legend_hud_colortype_scroll_offset = new_offset
        return {'FINISHED'}

class LegendHudcolortypeScrollDown(bpy.types.Operator):
    bl_idname = "bim.legend_hud_colortype_scroll_down"
    bl_label = "Scroll Down"
    bl_description = "Scroll down in the legend HUD colortype list"
    bl_options = {"REGISTER"}

    def execute(self, context):
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        current_offset = getattr(camera_props, 'legend_hud_colortype_scroll_offset', 0)
        from .. import hud
        if hasattr(hud_overlay, 'schedule_hud') and hud_overlay.schedule_hud:
            all_colortype_data = hud_overlay.schedule_hud.get_active_colortype_legend_data(include_hidden=True)
            total_colortypes = len(all_colortype_data) if all_colortype_data else 0
            max_offset = max(0, total_colortypes - 5)
            if current_offset < max_offset:
                camera_props.legend_hud_colortype_scroll_offset = current_offset + 1
        return {'FINISHED'}


class LegendHudTogglecolortypeVisibility(bpy.types.Operator):
    bl_idname = "bim.legend_hud_toggle_colortype_visibility"
    bl_label = "Toggle colortype HUD Visibility"
    bl_description = "Toggle whether colortype appears in viewport HUD legend"
    bl_options = {"REGISTER"}
    
    colortype_name: bpy.props.StringProperty(name="colortype Name")

    def execute(self, context):
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        hidden_colortypes = getattr(camera_props, 'legend_hud_visible_colortypes', '')
        hidden_list = [p.strip() for p in hidden_colortypes.split(',') if p.strip()] if hidden_colortypes.strip() else []
        if self.colortype_name in hidden_list:
            hidden_list.remove(self.colortype_name)
        else:
            hidden_list.append(self.colortype_name)
        camera_props.legend_hud_visible_colortypes = ', '.join(hidden_list)
        return {'FINISHED'}

    # ==============================
    # WORKING 3D LEGEND HUD METHODS 
    # ==============================

    def _create_rounded_panel_working(self, name, width, height, radius, alpha, color, collection):
        """WORKING VERSION from v117_P"""
        import bmesh
        bm = bmesh.new()
        max_radius = min(width, height) * 0.4
        actual_radius = min(radius, max_radius)
        if actual_radius > 0.005:
            bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=1.0)
            bmesh.ops.scale(bm, vec=(width, height, 1.0), verts=bm.verts)
            try:
                bmesh.ops.inset_individual(bm, faces=bm.faces[:], thickness=actual_radius * 0.5, depth=0.0, use_boundary=True)
            except Exception: pass
        else:
            bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
            bmesh.ops.scale(bm, vec=(width, height, 1.0), verts=bm.verts)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        try:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
        except Exception: pass
        mat = self._create_emission_material(f"{name}_Mat", color, 1.2, alpha)
        obj.data.materials.append(mat)
        return obj

    def _create_color_dot_working(self, name, diameter, color, collection):
        """WORKING VERSION from v117_P"""
        bpy.ops.mesh.primitive_circle_add(vertices=24, radius=diameter * 0.5, fill_type='NGON')
        obj = bpy.context.active_object
        obj.name = name
        if obj.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(obj)
        if obj.name not in collection.objects:
            collection.objects.link(obj)
        mat = self._create_emission_material(f"{name}_Mat", color, 6.0, 1.0)
        obj.data.materials.append(mat)
        return obj

    def _create_text_object_working(self, name, text, size, color, strength, collection):
        """WORKING VERSION from v117_P"""
        curve = bpy.data.curves.new(name, 'FONT')
        curve.body = text
        curve.size = size
        curve.align_x = 'LEFT'
        curve.align_y = 'CENTER'
        obj = bpy.data.objects.new(name, curve)
        collection.objects.link(obj)
        mat = self._create_emission_material(f"{name}_Mat", color, strength, 1.0)
        obj.data.materials.append(mat)
        return obj
