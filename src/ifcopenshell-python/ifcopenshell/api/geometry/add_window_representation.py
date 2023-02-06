# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 @Andrej730
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.util.unit
from ifcopenshell.util.shape_builder import ShapeBuilder, V
from itertools import chain
from mathutils import Vector
import collections


# SCHEMAS describe panels setup
# where:
# - schema rows represent window X axis
# - schema columns represent window Y axis
# - order of rows is from top of the window to bottom

DEFAULT_PANEL_SCHEMAS = {
    "SINGLE_PANEL":            [[0]],
    "DOUBLE_PANEL_HORIZONTAL": [[0],    [1]],
    "DOUBLE_PANEL_VERTICAL":   [[0, 1]],
    "TRIPLE_PANEL_BOTTOM":     [[0, 1], [2, 2]],
    "TRIPLE_PANEL_TOP":        [[0, 0], [1, 2]],
    "TRIPLE_PANEL_LEFT":       [[0, 1], [0, 2]],
    "TRIPLE_PANEL_RIGHT":      [[0, 1], [2, 1]],
    "TRIPLE_PANEL_HORIZONTAL": [[0],    [1],   [2]],
    "TRIPLE_PANEL_VERTICAL":   [[0, 1, 2]],
}


def create_ifc_window_frame_simple(builder, size: Vector, thickness: Vector, position: Vector = V(0,0,0).freeze()):
    """`thickness` of the profile is defined as list in the following order:
    `(LEFT, TOP, RIGHT, BOTTOM)`

    `thickness` can be also defined just as 1 float value.
    """

    if not isinstance(thickness, collections.abc.Iterable):
        thickness = [thickness] * 4

    th_left, th_up, th_right, th_bottom = thickness

    panel_rect = builder.rectangle(size=size*V(1,0,1))

    inner_rect_size = size - V(th_left + th_right, 0, th_bottom + th_up)
    inner_rect = builder.rectangle(size=inner_rect_size * V(1, 0, 1), position=V(th_left, 0, th_bottom))

    panel_profile = builder.profile(panel_rect, inner_curves=inner_rect)
    panel_extruded = builder.extrude(panel_profile, size.y, extrusion_vector=V(0, 1, 0), position=position)
    return panel_extruded


def create_ifc_window(
    builder,
    lining_size: Vector,
    lining_thickness,
    lining_to_panel_offset_x,
    lining_to_panel_offset_y_full,
    frame_size,
    frame_thickness,
    glass_thickness,
    position: Vector,
):
    lining_items = []
    main_lining_size = lining_size

    # need to check offsets to decide whether lining should be rectangle
    # or L shaped
    l_shape_check = lining_to_panel_offset_y_full < lining_size.y \
                        and any(lining_to_panel_offset_x < th for th in lining_thickness)

    if l_shape_check:
        main_lining_size = lining_size.copy()
        main_lining_size.y = lining_to_panel_offset_y_full

        second_lining_size = lining_size.copy()
        second_lining_size.y = lining_size.y - lining_to_panel_offset_y_full
        second_lining_position = V(0, lining_to_panel_offset_y_full, 0)
        second_lining_thickness = [min(th, lining_to_panel_offset_x) for th in lining_thickness]

        second_lining = create_ifc_window_frame_simple(
            builder, second_lining_size, second_lining_thickness, second_lining_position
        )
        lining_items.append(second_lining)

    main_lining = create_ifc_window_frame_simple(builder, main_lining_size, lining_thickness)
    lining_items.append(main_lining)

    frame_position = V(lining_to_panel_offset_x, lining_to_panel_offset_y_full, lining_to_panel_offset_x)

    frame_extruded = create_ifc_window_frame_simple(builder, frame_size, frame_thickness, frame_position)

    glass_position = frame_position + V(0, frame_size.y / 2 - glass_thickness / 2, 0)
    glass_rect = builder.deep_copy(frame_extruded.SweptArea.InnerCurves[0])
    glass = builder.extrude(glass_rect, glass_thickness, extrusion_vector=V(0, 1, 0), position=glass_position)

    output_items = [lining_items, [frame_extruded], [glass]]
    builder.translate(chain(*output_items), position)

    return output_items


class Usecase:
    def __init__(self, file, **settings):
        """units in settings expected to be in ifc project units"""
        self.file = file
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindow.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowTypePartitioningEnum.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowLiningProperties.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowPanelProperties.htm
        self.settings = {"unit_scale": ifcopenshell.util.unit.calculate_unit_scale(self.file)}
        self.settings.update(
            {
                "context": None,  # IfcGeometricRepresentationContext
                # SINGLE_PANEL, DOUBLE_PANEL_HORIZONTAL, DOUBLE_PANEL_VERTICAL,
                # TRIPLE_PANEL_BOTTOM, TRIPLE_PANEL_HORIZONTAL, TRIPLE_PANEL_LEFT,
                # TRIPLE_PANEL_RIGHT, TRIPLE_PANEL_TOP, TRIPLE_PANEL_VERTICAL
                "partition_type": "SINGLE_PANEL",
                "overall_height": self.convert_si_to_unit(0.9),
                "overall_width": self.convert_si_to_unit(0.6),
                "lining_properties": {
                    "LiningDepth": self.convert_si_to_unit(0.050),
                    "LiningThickness": self.convert_si_to_unit(0.050),
                    "LiningOffset": self.convert_si_to_unit(0.050),  # offset to the wall
                    # offset from the wall
                    "LiningToPanelOffsetX": self.convert_si_to_unit(0.025),
                    # offset from the lining
                    # full offset from Y axis = (lining_depth - frame_depth) + lining_to_panel_offset_y
                    "LiningToPanelOffsetY": self.convert_si_to_unit(0.025),
                    # applies to DoublePanelVertical, TriplePanelBottom, TriplePanelTop,
                    # TriplePanelLeft, TriplePanelRight
                    # mullion - horizontal distance between panels
                    "MullionThickness": self.convert_si_to_unit(0.050),
                    # distance from the first lining to the mullion center
                    "FirstMullionOffset": self.convert_si_to_unit(0.3),
                    # applies to TriplePanelVertical
                    # distance from the first lining to the second mullion center
                    "SecondMullionOffset": self.convert_si_to_unit(0.45),
                    # applies to DoublePanelHorizontal, TriplePanelBottom, TriplePanelTop,
                    # TriplePanelLeft, TriplePanelRight
                    # works similar way to mullion
                    "TransomThickness": self.convert_si_to_unit(0.050),
                    "FirstTransomOffset": self.convert_si_to_unit(0.3),
                    # applies to TriplePanelHorizontal
                    "SecondTransomOffset": self.convert_si_to_unit(0.6),
                    "ShapeAspectStyle": None,  # DEPRECATED
                },
                "panel_properties": [
                    {
                        "FrameDepth": self.convert_si_to_unit(0.035),  # by Y
                        "FrameThickness": self.convert_si_to_unit(0.035),  # by X
                        # BOTTOM, LEFT, MIDDLE, RIGHT, TOP
                        "PanelPosition": ...,  # NEVER USED
                        # defines the basic ways to describe how window panels operate
                        # how it's hanged, how it opens
                        "OperationType": None,  # NEVER USED
                        "ShapeAspectStyle": None,  # DEPRECATED
                    },
                ],
            }
        )

        for key, value in settings.items():
            self.settings[key] = value
        self.settings["panel_schema"] = DEFAULT_PANEL_SCHEMAS[self.settings["partition_type"]]

    def execute(self):
        builder = ShapeBuilder(self.file)
        overall_height = self.settings["overall_height"]
        overall_width = self.settings["overall_width"]

        if self.settings["context"].TargetView == "ELEVATION_VIEW":
            rect = builder.rectangle(V(overall_width, 0, overall_height))
            representation_evelevation = builder.get_representation(self.settings["context"], rect)
            return representation_evelevation

        panel_schema = self.settings["panel_schema"]
        panels = self.settings["panel_properties"]
        accumulated_height = [0] * len(panel_schema[0])
        built_panels = []
        window_items = []

        lining_props = self.settings["lining_properties"]
        lining_thickness = lining_props["LiningThickness"]
        lining_depth = lining_props["LiningDepth"]
        lining_offset = lining_props["LiningOffset"]
        lining_to_panel_offset_x = lining_props["LiningToPanelOffsetX"]
        lining_to_panel_offset_y = lining_props["LiningToPanelOffsetY"]

        mullion_thickness = lining_props["MullionThickness"] / 2
        first_mullion_offset = lining_props["FirstMullionOffset"]
        second_mullion_offset = lining_props["SecondMullionOffset"]
        transom_thickness = lining_props["TransomThickness"] / 2
        first_transom_offset = lining_props["FirstTransomOffset"]
        second_transom_offset = lining_props["SecondTransomOffset"]
        glass_thickness = self.convert_si_to_unit(0.01)

        panel_schema = list(reversed(panel_schema))

        # TODO: need more readable way to define panel width and height
        unique_rows_in_col = [
            len(set(row[column_i] for row in panel_schema)) for column_i in range(len(panel_schema[0]))
        ]
        for row_i, panel_row in enumerate(panel_schema):
            accumulated_width = 0
            unique_cols = len(set(panel_row))

            for column_i, panel_i in enumerate(panel_row):
                # calculate current panel dimensions
                if unique_cols > 1:
                    if column_i == 0:
                        lining_width = first_mullion_offset
                    elif column_i == unique_cols - 1:
                        lining_width = overall_width - accumulated_width
                    else:
                        lining_width = second_mullion_offset - accumulated_width
                else:
                    lining_width = overall_width

                if unique_rows_in_col[column_i] > 1:
                    if row_i == 0:
                        lining_height = first_transom_offset
                    elif row_i == unique_rows_in_col[column_i] - 1:
                        lining_height = overall_height - accumulated_height[column_i]
                    else:
                        lining_height = second_transom_offset - accumulated_height[column_i]
                else:
                    lining_height = overall_height

                if panel_i in built_panels:
                    accumulated_height[column_i] += lining_height
                    accumulated_width += lining_width
                    continue

                cur_panel = panels[panel_i]
                frame_depth = cur_panel["FrameDepth"]
                frame_thickness = cur_panel["FrameThickness"]
                current_items = []

                frame_width = lining_width - lining_to_panel_offset_x * 2
                frame_height = lining_height - lining_to_panel_offset_x * 2

                # calculate lining thickness
                # lining is calculated on panel level because
                # panel depth is used
                # also taking into account mullions and transoms
                window_lining_thickness = [lining_thickness] * 4
                # mullion thickness
                if unique_cols > 1:
                    if column_i != 0:
                        window_lining_thickness[0] = mullion_thickness  # left column
                    if column_i != unique_cols - 1:
                        window_lining_thickness[2] = mullion_thickness  # right column
                # transom thickness
                if unique_rows_in_col[column_i] > 1:
                    if row_i != 0:
                        window_lining_thickness[3] = transom_thickness  # bottom row
                    if row_i != unique_rows_in_col[column_i] - 1:
                        window_lining_thickness[1] = transom_thickness  # top row
                window_lining_size = V(lining_width, lining_depth, lining_height)
                frame_size = V(frame_width, frame_depth, frame_height)
                window_panel_position = V(accumulated_width, 0, accumulated_height[column_i])

                # create window panel
                current_window_items = create_ifc_window(
                    builder,
                    window_lining_size,
                    window_lining_thickness,
                    lining_to_panel_offset_x,
                    (lining_depth - frame_depth) + lining_to_panel_offset_y,
                    frame_size,
                    frame_thickness,
                    glass_thickness,
                    window_panel_position,
                )
                built_panels.append(panel_i)
                window_items.extend(chain(*current_window_items))

                accumulated_height[column_i] += lining_height
                accumulated_width += lining_width

        builder.translate(window_items, V(0, lining_offset, 0))  # wall offset
        representation = builder.get_representation(self.settings["context"], window_items)
        return representation

    def convert_si_to_unit(self, value):
        return value / self.settings["unit_scale"]
