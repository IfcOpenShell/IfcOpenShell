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

import math
from collections.abc import Iterable
from typing import Union

import blf
import bpy
import gpu
import numpy as np
from bpy.types import SpaceView3D
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo, box_crosses_segments, get_plain_symbol


def update_loads_after_moves(scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph) -> None:
    """Redraw the shown loads when a structural item moves, so that they follow it"""
    if not tool.Ifc.get():
        return
    for update in depsgraph.updates:
        if update.is_updated_transform and isinstance(update.id, bpy.types.Object):
            element = tool.Ifc.get_entity(update.id.original)
            if element and element.is_a("IfcStructuralItem"):
                LoadsDecorator.update()
                tool.Blender.update_all_viewports()
                return


def show_loads(shown: bool) -> None:
    """Show or hide the structural loads overlay, and pick loads to edit while they are shown"""
    if shown and tool.Ifc.get():
        LoadsDecorator.install(bpy.context)
        if not bpy.app.timers.is_registered(start_load_picking):
            bpy.app.timers.register(start_load_picking)
    elif LoadsDecorator.is_installed:
        LoadsDecorator.uninstall()
    tool.Blender.update_all_viewports()


def show_loads_after_load() -> None:
    """Restore the loads overlay once a file and its IFC have loaded"""
    show_loads(tool.Structural.get_structural_props().show_loads)


def start_load_picking() -> None:
    """Start picking shown loads to edit, which needs a window to run an operator in"""
    if (
        LoadsDecorator.is_installed
        and not LoadsDecorator.is_picking
        and (windows := bpy.context.window_manager.windows)
    ):
        with bpy.context.temp_override(window=windows[0]):
            bpy.ops.bim.pick_structural_loads("INVOKE_DEFAULT")


class LoadsDecorator(tool.Blender.ViewportDecorator):
    """Decorator to show structural loads in 3D"""

    # draw_methods exists to satisfy ViewportDecorator.__init_subclass__'s
    # method-existence check; the override install below is what actually
    # registers handlers (the POST_VIEW binding passes no context arg, which
    # the base's generic install cannot express).
    draw_methods = (
        ("draw_load_values", "POST_PIXEL"),
        ("__call__", "POST_VIEW"),
    )
    decoration_data = None
    text_info = []
    shader_info = []
    depth_array = None
    pickables = []
    # Where clickable values were last drawn, as boxes with the pickable each stands for, by viewport region.
    label_boxes: dict[int, list[tuple[float, float, float, float, int, str, str]]] = {}
    hovered: Union[dict, None] = None
    hovered_focus = ""  # The value the label hovered stands for, to start editing it, or "" for an arrow.
    # The part of what is hovered, highlighted on its own: its arrow, or its magnitude, angle, slope or axes.
    hovered_part = "arrow"
    picked_part = "arrow"  # As pick last found, before it is taken as hovered.
    is_picking = False  # Whether bim.pick_structural_loads is running.

    @classmethod
    def install(cls, context: bpy.types.Context) -> None:
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_load_values, ((context,)), "WINDOW", "POST_PIXEL")
        )
        cls.handlers.append(SpaceView3D.draw_handler_add(handler, (), "WINDOW", "POST_VIEW"))
        cls.decoration_data = ShaderInfo()
        cls.update()
        cls.is_installed = True
        if update_loads_after_moves not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(update_loads_after_moves)
        cls.redraw_properties()

    @classmethod
    def uninstall(cls) -> None:
        if update_loads_after_moves in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(update_loads_after_moves)
        super().uninstall()
        cls.pickables = []
        cls.label_boxes = {}
        cls.hovered = None
        cls.redraw_properties()

    @classmethod
    def redraw_properties(cls) -> None:
        """Redraw property editors, whose load case eyes show whether loads are shown"""
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "PROPERTIES":
                    area.tag_redraw()

    @classmethod
    def update(cls) -> None:
        cls.decoration_data.update()
        cls.text_info = cls.decoration_data.text_info
        cls.shader_info = cls.decoration_data.info
        cls.pickables = cls.decoration_data.pickables
        cls.label_boxes = {}  # Until the labels are drawn again.
        cls.hovered = None

    @classmethod
    def is_visible(cls, info: dict) -> bool:
        """Whether drawing data is shown: loads hide with their structural item, in the viewport being drawn, and
        what belongs to several items, as a moment to its point and its centre, with any of them"""
        space = bpy.context.space_data
        for name in info.get("visible_with") or [info.get("object")]:
            if name and (obj := bpy.data.objects.get(name)):
                if not (obj.visible_get(viewport=space) if space and space.type == "VIEW_3D" else obj.visible_get()):
                    return False
        return True

    @classmethod
    def pick(cls, region: bpy.types.Region, rv3d: bpy.types.RegionView3D, x: float, y: float) -> Union[dict, None]:
        """Get the pickable arrow nearest the region coordinates x and y, if one is within a few pixels, or the one
        whose value is under them, which comes first"""
        cls.hovered_focus, cls.picked_part = "", "arrow"
        for left, low, width, height, index, focus, part in cls.label_boxes.get(region.as_pointer(), []):
            if left - 3 <= x <= left + width + 3 and low - 3 <= y <= low + height + 3 and index < len(cls.pickables):
                cls.hovered_focus, cls.picked_part = focus, part
                return cls.pickables[index]
        mouse = Vector((x, y))
        best, best_distance = None, 10.0
        for pickable in cls.pickables:
            if pickable.get("label_only") or not cls.is_visible(cls.shader_info[pickable["info"]]):
                continue
            # An arrow is one segment; a drawing of several lines, as a moment's, is picked along any of them.
            for start, end in pickable.get("segments") or [(pickable["tail"], pickable["tip"])]:
                tail = location_3d_to_region_2d(region, rv3d, Vector(start))
                tip = location_3d_to_region_2d(region, rv3d, Vector(end))
                if tail is None or tip is None or not (tip - tail).length:
                    continue
                along = max(0.0, min(1.0, (mouse - tail).dot(tip - tail) / (tip - tail).length_squared))
                if along * (tip - tail).length < 15 and not pickable.get("anywhere"):
                    continue  # Leave the tail, where the loaded point is, free for selecting it.
                distance = (tail + (tip - tail) * along - mouse).length
                if distance < best_distance:
                    best, best_distance = pickable, distance
        # An arrow standing for one value, as a component, opens its dialog with that value ready to type.
        cls.hovered_focus = best.get("focus", "") if best else ""
        return best

    def __call__(self) -> None:
        """set gpu configurations to draw 3D representations"""
        if not self.shader_info:
            return  # No loads, as in most models, which show loads by default.
        # set open gl configurations
        original_blend = gpu.state.blend_get()
        original_depth_test = gpu.state.depth_test_get()
        original_depth_mask = gpu.state.depth_mask_get()
        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("LESS_EQUAL")
        # Load glyphs stay behind the model but don't write depth, so they neither hide each other (later ones,
        # such as resultants, draw on top) nor hide the load values, whose visibility is tested against depth.
        gpu.state.depth_mask_set(False)

        self.draw_batch()

        # restore opengl configurations
        gpu.state.blend_set(original_blend)
        gpu.state.depth_test_set(original_depth_test)
        gpu.state.depth_mask_set(original_depth_mask)

    def draw_batch(self) -> None:
        """draw the 3D representation of loads"""
        if not self.decoration_data.is_empty:
            # What is hovered: a force's arrow, with its angle's arc and slope triangle if drawn.
            hovered = set()
            if self.hovered and self.hovered_part == "arrow":
                # A drawing of several lines, as a moment's, highlights whole.
                hovered = set(self.hovered.get("whole") or [self.hovered["info"]])
            elif self.hovered:
                hovered = set(self.hovered.get("parts", {}).get(self.hovered_part, []))
            for i, info in enumerate(self.shader_info):
                if not self.is_visible(info):
                    continue
                shader = info["shader"]
                args = info["args"]
                indices = info["indices"]
                if not tool.Blender.validate_shader_batch_data(args["coord"], indices):
                    continue
                batch = batch_for_shader(shader, "TRIS", args, indices=indices)
                matrix = bpy.context.region_data.perspective_matrix
                shader.bind()
                shader.uniform_float("viewProjectionMatrix", matrix)

                for key, value in info["uniforms"]:
                    if key == "color" and i in hovered:
                        rgb = [min(c, 1.0) for c in value[:3]]
                        # Highlight by contrast: light arrows, such as white resultants, darken; others brighten.
                        if 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2] > 0.85:
                            value = tuple(c * 0.5 for c in rgb) + (2,)
                        else:
                            value = tuple(c + (1 - c) * 0.6 for c in rgb) + (2,)
                    shader.uniform_float(key, value)

                batch.draw(shader)

    def draw_load_values(self, context: bpy.types.Context) -> None:
        """draw text representing the load values"""
        if not self.text_info:
            return  # Nothing to draw, so spare reading the depth buffer.
        # getting depth buffer info, code adapted from:
        # https://blender.stackexchange.com/questions/177185/is-there-a-way-to-render-depth-buffer-into-a-texture-with-gpu-bgl-python-modules
        framebuffer = gpu.state.active_framebuffer_get()
        width = context.region.width
        height = context.region.height
        depth_buffer = framebuffer.read_depth(0, 0, width, height)
        depth_array = np.array(depth_buffer.to_list())

        f = context.area.spaces.active.clip_end
        n = context.area.spaces.active.clip_start

        self.depth_array = n / (f - (f - n) * depth_array) * (f - n)

        placed: list[tuple[float, float, float, float]] = []
        segments = self.get_screen_segments(context)
        boxes = self.label_boxes[context.region.as_pointer()] = []
        # Each item's diagram size, its longest arrow, so that labels keep to it as in a report's diagram.
        sizes: dict[str, float] = {}
        for entry in self.shader_info:
            if (primitive := entry.get("primitive")) and (name := entry.get("object")):
                sizes[name] = max(sizes.get(name, 0.0), primitive["size"])
        for info in self.text_info:
            if not self.is_visible(info):
                continue
            text_position = self.location_3d_to_region_2d(info["position"], context)
            if text_position is not None:
                font_id = 0
                index = info.get("pickable")
                # The labels of what is hovered, its arrow or themselves, are highlighted with it, by colour alone.
                hovered = (
                    index is not None
                    and index < len(self.pickables)
                    and self.pickables[index] is self.hovered
                    and info.get("part") == self.hovered_part
                )
                blf.size(font_id, self.get_label_size(info, sizes.get(info.get("object", "")), context))
                # Named by its symbol, as in calculations and reports.
                text = (
                    f"{get_plain_symbol(symbol)} = {info['text']}" if (symbol := info.get("symbol")) else info["text"]
                )
                x, y = text_position[0], text_position[1]
                if (away := info.get("away")) is not None:
                    x, y = self.place_beside(info["position"], away, x, y, text, context, placed, segments)
                blf.position(font_id, x, y, text_position[2])
                if index is not None:
                    boxes.append(
                        (x, y, *blf.dimensions(font_id, text), index, info.get("focus", ""), info.get("part", ""))
                    )
                # Labels take the colour of what they describe, lightened to stay legible on a dark viewport.
                rgb = [min(c, 1.0) for c in info.get("color", (0.85, 0.85, 0.85))[:3]]
                r, g, b = (c + (1 - c) * 0.35 for c in rgb)
                if hovered:
                    # As arrows are highlighted: light ones, as the resultant's, darken; others brighten.
                    if 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2] > 0.85:
                        r, g, b = (c * 0.6 for c in rgb)
                    else:
                        r, g, b = (c + (1 - c) * 0.75 for c in rgb)
                blf.color(font_id, r, g, b, 1.0)
                blf.draw(font_id, text)
                if hovered and info.get("part") == "add":
                    # A note for what clicking it does, as +X and +Z add a load at their point.
                    blf.position(font_id, x + blf.dimensions(font_id, text)[0] + 8, y, text_position[2])
                    blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
                    blf.draw(font_id, "Add Load")

    def get_label_size(self, info: dict, size: Union[float, None], context: bpy.types.Context) -> float:
        """A label's font size: a share of its diagram's longest arrow on screen, as a report's diagram has, so
        that zooming scales labels with the arrows, kept within sizes that read"""
        if not size:
            return 20.0
        region, rv3d = context.region, context.region_data
        right = rv3d.view_rotation @ Vector((1, 0, 0))
        start = location_3d_to_region_2d(region, rv3d, Vector(info["position"]))
        end = location_3d_to_region_2d(region, rv3d, Vector(info["position"]) + right * size)
        if start is None or end is None:
            return 20.0
        # Some labels read a little larger than their diagram's share, as moments' do; all as the user sizes them.
        chosen = tool.Structural.get_structural_props().label_size
        return min(max((end - start).length * 0.032 * info.get("label_scale", 1.0), 8.0), 24.0) * chosen

    def place_beside(
        self,
        position: Iterable,
        away: Iterable,
        x: float,
        y: float,
        text: str,
        context: bpy.types.Context,
        placed: Union[list[tuple[float, float, float, float]], None] = None,
        segments: Iterable[tuple[Iterable, Iterable]] = (),
    ) -> tuple[float, float]:
        """Offset a label from its anchor towards away, so that it sits beside its line rather than on it.

        :param placed: The boxes of labels already drawn. The label moves further away until it clears them,
            and its box is added.
        :param segments: Arrows and lines on screen it keeps off too, or, if it cannot within reach, the
            nearest place clear of the other labels.
        """
        start = location_3d_to_region_2d(context.region, context.region_data, Vector(position))
        end = location_3d_to_region_2d(context.region, context.region_data, Vector(position) + Vector(away))
        if start is None or end is None or not (end - start).length:
            return x, y
        direction = (end - start).normalized()
        width, height = blf.dimensions(0, text)

        def get_box(towards: Vector, gap: float) -> tuple[float, float]:
            """The text box on the towards side of the anchor, centred across directions near perpendicular to it"""
            return (
                x + gap * towards.x + (0 if towards.x > 0.3 else -width if towards.x < -0.3 else -width / 2),
                y + gap * towards.y + (0 if towards.y > 0.3 else -height if towards.y < -0.3 else -height / 2),
            )

        if placed is None:
            return get_box(direction, 12)
        margin = 3
        # The nearest place clear of other labels and of lines, trying its own direction first at each distance,
        # then turning further from it, so that it moves round an arrow beside it rather than across it.
        turns = [math.radians(t) for t in (0, 30, -30, 60, -60, 90, -90, 135, -135, 180)]
        candidates = [
            Vector(
                (
                    direction.x * math.cos(t) - direction.y * math.sin(t),
                    direction.x * math.sin(t) + direction.y * math.cos(t),
                )
            )
            for t in turns
        ]
        # This runs on every redraw, so only lines within reach are tested, and a label that finds no clear place
        # within a number of tries keeps the nearest one clear of the other labels.
        steps, tries = 60, 60
        reach = 12 + 4 * steps + width + height
        nearby = [
            s
            for s in segments
            if max(s[0][0], s[1][0]) > x - reach
            and min(s[0][0], s[1][0]) < x + reach
            and max(s[0][1], s[1][1]) > y - reach
            and min(s[0][1], s[1][1]) < y + reach
        ]
        chosen = fallback = None  # Clear of all; clear of the labels only, if lines cannot be cleared too.
        for step in range(steps):
            for towards in candidates:
                bx, by = get_box(towards, 12 + 4 * step)
                if any(
                    bx < px + pw + margin
                    and px < bx + width + margin
                    and by < py + ph + margin
                    and py < by + height + margin
                    for px, py, pw, ph in placed
                ):
                    continue
                fallback = fallback or (bx, by)
                tries -= 1
                if tries < 0 or not box_crosses_segments(
                    bx - margin, by - margin, width + 2 * margin, height + 2 * margin, nearby
                ):
                    chosen = (bx, by) if tries >= 0 else fallback
                    break
            if chosen:
                break
        x, y = chosen or fallback or get_box(direction, 12)
        placed.append((x, y, width, height))
        return x, y

    def get_screen_segments(self, context: bpy.types.Context) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        """The visible arrows and solid lines, as arcs and slope triangles, on screen, for labels to keep off.
        Dashed guides, as parallelogram sides and reference axes, may be crossed."""
        segments = []
        for info in self.shader_info:
            if not (primitive := info.get("primitive")) or not self.is_visible(info):
                continue
            if primitive["type"] == "ARROW":
                ends = (primitive["tail"], primitive["tip"])
            elif not primitive["dashed"]:
                ends = (primitive["start"], primitive["end"])
            else:
                continue
            points = [location_3d_to_region_2d(context.region, context.region_data, Vector(p)) for p in ends]
            if None not in points:
                segments.append(tuple((p.x, p.y) for p in points))
        return segments

    def location_3d_to_region_2d(self, coord: Iterable, context: bpy.types.Context) -> Union[Vector, None]:
        """Convert from 3D space to 2D screen space.
        Filter out the text supposed to be hidden by 3D elements, using the depth array.
        It also hides text that are distant from the camera view to avoid clutter"""

        coord = Vector(coord)
        rv3d = context.region_data
        assert rv3d and context.region
        perspective = rv3d.view_perspective
        view_matrix = rv3d.view_matrix
        point_view_space = view_matrix @ coord

        if perspective == "ORTHO" or -10 < point_view_space.z < 0:
            prj = rv3d.perspective_matrix @ Vector((coord[0], coord[1], coord[2], 1.0))
            width_half = context.region.width / 2.0
            height_half = context.region.height / 2.0
            coord_2d = Vector(
                (
                    width_half + width_half * (prj.x / prj.w),
                    height_half + height_half * (prj.y / prj.w),
                    point_view_space.z,
                )
            )
            if (
                coord_2d[0] < 0
                or coord_2d[0] > context.region.width
                or coord_2d[1] > context.region.height
                or coord_2d[1] < 0
            ):
                return None
            depth = self.depth_array[int(coord_2d[1])][int(coord_2d[0])]
            if -0.98 * point_view_space.z > depth:
                return None
            return coord_2d
        return None
