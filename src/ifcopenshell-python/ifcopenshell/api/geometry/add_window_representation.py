# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 @Andrej730
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
from math import sin, cos
from ifcopenshell.util.shape_builder import ShapeBuilder, V
from mathutils import Vector


# SCHEMAS describe panels setup
# where:
# - schema rows represent window X axis
# - schema columns represent window Y axis
# - order of rows is from top of the window to bottom

DEFAULT_PANEL_SCHEMAS = {
    "SINGLE_PANEL": [[0]],
    "DOUBLE_PANEL_HORIZONTAL": [[0], [1]],
    "DOUBLE_PANEL_VERTICAL": [[0, 1]],
    "TRIPLE_PANEL_BOTTOM": [[0, 1], [2, 2]],
    "TRIPLE_PANEL_TOP": [[0, 0], [1, 2]],
    "TRIPLE_PANEL_LEFT": [[0, 1], [0, 2]],
    "TRIPLE_PANEL_RIGHT": [[0, 1], [2, 1]],
    "TRIPLE_PANEL_HORIZONTAL": [[0], [1], [2]],
    "TRIPLE_PANEL_VERTICAL": [[0, 1, 2]],
}


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindow.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowTypePartitioningEnum.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowLiningProperties.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowPanelProperties.htm
        self.settings = {
            "context": None,  # IfcGeometricRepresentationContext
            # SINGLE_PANEL, DOUBLE_PANEL_HORIZONTAL, DOUBLE_PANEL_VERTICAL,
            # TRIPLE_PANEL_BOTTOM, TRIPLE_PANEL_HORIZONTAL, TRIPLE_PANEL_LEFT, TRIPLE_PANEL_RIGHT, TRIPLE_PANEL_TOP, TRIPLE_PANEL_VERTICAL
            "partition_type": "SINGLE_PANEL",
            "overall_height": 900,
            "overall_width": 600,
            "lining_properties": {
                "LiningDepth": 50,
                "LiningThickness": 50,
                "LiningOffset": 50,  # offset to the wall
                "LiningToPanelOffsetX": 25,
                "LiningToPanelOffsetY": 25,
                # applies to DoublePanelVertical, TriplePanelBottom, TriplePanelTop, TriplePanelLeft, TriplePanelRight
                # mullion - horizontal distance between panels
                "MullionThickness": 50,
                "FirstMullionOffset": 300,  # distance from the first lining to the mullion center
                # applies to TriplePanelVertical
                "SecondMullionOffset": 450,  # distance from the first lining to the second mullion
                # applies to DoublePanelHorizontal, TriplePanelBottom, TriplePanelTop, TriplePanelLeft, TriplePanelRight
                # works similar way to mullion
                "TransomThickness": 50,
                "FirstTransomOffset": 300,
                # applies to TriplePanelHorizontal
                "SecondTransomOffset": 600,
                "ShapeAspectStyle": None,  # DEPRECATED
            },
            "panel_properties": [
                {
                    "FrameDepth": 35,  # by Y
                    "FrameThickness": 35,  # by X
                    # BOTTOM, LEFT, MIDDLE, RIGHT, TOP
                    "PanelPosition": ...,
                    # defines the basic ways to describe how window panels operate
                    # how it's hanged, how it opens
                    "OperationType": None,
                    "ShapeAspectStyle": None,  # DEPRECATED
                },
            ],
        }

        for key, value in settings.items():
            self.settings[key] = value
        self.settings["panel_schema"] = DEFAULT_PANEL_SCHEMAS[self.settings["partition_type"]]

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        builder = ShapeBuilder(self.file)
        overall_height = self.convert_si_to_unit(self.settings["overall_height"])
        overall_width = self.convert_si_to_unit(self.settings["overall_width"])

        if self.settings["context"].TargetView == "ELEVATION_VIEW":
            rect = builder.rectangle(V(overall_width, 0, overall_height))
            representation_evelevation = builder.get_representation(self.settings["context"], rect)
            return representation_evelevation

        panel_schema = self.settings["panel_schema"]
        panels = self.settings["panel_properties"]
        accumulated_height = [0] * len(panel_schema[0])
        built_panels = []
        window_items = []

        lining_thickness = self.convert_si_to_unit(self.settings["lining_properties"]["LiningThickness"])
        lining_depth = self.convert_si_to_unit(self.settings["lining_properties"]["LiningDepth"])
        lining_offset = self.convert_si_to_unit(self.settings["lining_properties"]["LiningOffset"])
        lining_panel_offset_x = self.convert_si_to_unit(self.settings["lining_properties"]["LiningToPanelOffsetX"])
        lining_panel_offset_y = self.convert_si_to_unit(self.settings["lining_properties"]["LiningToPanelOffsetY"])
        glass_thickness = self.convert_si_to_unit(10)

        mullion_thickness = self.convert_si_to_unit(self.settings["lining_properties"]["MullionThickness"]) / 2
        first_mullion_offset = self.convert_si_to_unit(self.settings["lining_properties"]["FirstMullionOffset"])
        second_mullion_offset = self.convert_si_to_unit(self.settings["lining_properties"]["SecondMullionOffset"])
        transom_thickness = self.convert_si_to_unit(self.settings["lining_properties"]["TransomThickness"]) / 2
        first_transom_offset = self.convert_si_to_unit(self.settings["lining_properties"]["FirstTransomOffset"])
        second_transom_offset = self.convert_si_to_unit(self.settings["lining_properties"]["SecondTransomOffset"])

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
                        panel_width = first_mullion_offset
                    elif column_i == unique_cols - 1:
                        panel_width = overall_width - accumulated_width
                    else:
                        panel_width = second_mullion_offset - accumulated_width
                else:
                    panel_width = overall_width

                if unique_rows_in_col[column_i] > 1:
                    if row_i == 0:
                        panel_height = first_transom_offset
                    elif row_i == unique_rows_in_col[column_i] - 1:
                        panel_height = overall_height - accumulated_height[column_i]
                    else:
                        panel_height = second_transom_offset - accumulated_height[column_i]
                else:
                    panel_height = overall_height

                if panel_i in built_panels:
                    accumulated_height[column_i] += panel_height
                    accumulated_width += panel_width
                    continue

                cur_panel = panels[panel_i]
                current_items = []
                panel_depth = self.convert_si_to_unit(cur_panel["FrameDepth"])
                panel_thickness = self.convert_si_to_unit(cur_panel["FrameThickness"])

                panel_actual_width = panel_width - lining_panel_offset_x * 2
                panel_actual_height = panel_height - lining_panel_offset_x * 2

                glass_width = panel_actual_width - panel_thickness * 2
                glass_height = panel_actual_height - panel_thickness * 2

                # build lining
                # lining is calculated on panel level because
                # panel depth is used
                lining_items_vertical_left = []
                lining_items = []

                # calculate lining thickness
                # taking into account mullions and transoms
                thickness = [lining_thickness] * 4
                # mullion thickness
                if unique_cols > 1:
                    if column_i != 0:
                        thickness[0] = mullion_thickness  # left column
                    if column_i != unique_cols - 1:
                        thickness[2] = mullion_thickness  # right column
                # transom thickness
                if unique_rows_in_col[column_i] > 1:
                    if row_i != 0:
                        thickness[3] = transom_thickness  # bottom row
                    if row_i != unique_rows_in_col[column_i] - 1:
                        thickness[1] = transom_thickness  # top row

                def get_lining_rectangle(current_lining_thickness):
                    lining_rectangle = builder.rectangle(size=V(current_lining_thickness, lining_depth))
                    return lining_rectangle

                def get_lining_polyline(current_lining_thickness):
                    # need to check offsets to decide whether lining should be rectangle
                    # or L shaped
                    if lining_panel_offset_x >= current_lining_thickness or lining_panel_offset_y >= lining_depth:
                        lining_polyline = get_lining_rectangle(current_lining_thickness)
                    else:
                        lining_points = [
                            V(0, 0),
                            V(0, lining_depth),
                            V(lining_panel_offset_x, lining_depth),
                            V(lining_panel_offset_x, lining_depth - (panel_depth - lining_panel_offset_y)),
                            V(current_lining_thickness, lining_depth - (panel_depth - lining_panel_offset_y)),
                            V(current_lining_thickness, 0),
                        ]
                        lining_polyline = builder.polyline(lining_points, closed=True)
                    return lining_polyline

                def create_lining_vertical(current_lining_thickness):
                    current_vertical_lining_items = []
                    lining_vertical_polyline = get_lining_polyline(current_lining_thickness)
                    lining_vertical_height = panel_height - lining_panel_offset_x * 2
                    extrusion_position = V(0, 0, lining_panel_offset_x)
                    lining_vertical_extruded = builder.extrude(
                        lining_vertical_polyline, lining_vertical_height, position=extrusion_position
                    )
                    current_vertical_lining_items.append(lining_vertical_extruded)

                    # if lining panel X offset is present
                    # then we also need to add two more box shapes
                    # to finish the lining after the panel ends
                    if lining_panel_offset_x > 0:
                        lining_vertical_addition = builder.extrude(
                            get_lining_rectangle(current_lining_thickness), lining_panel_offset_x
                        )

                        current_vertical_lining_items.append(lining_vertical_addition)
                        current_vertical_lining_items.append(
                            builder.translate(
                                lining_vertical_addition,
                                V(0, 0, panel_height - lining_panel_offset_x),
                                create_copy=True,
                            )
                        )

                    return current_vertical_lining_items

                # vertical lining
                lining_items_vertical_left = create_lining_vertical(thickness[0])
                lining_items_vertical_right = create_lining_vertical(thickness[2])
                lining_items_vertical_right = builder.mirror(
                    lining_items_vertical_right, mirror_point=V(panel_width / 2, 0), mirror_axes=V(1, 0)
                )
                lining_items.extend(lining_items_vertical_left)
                lining_items.extend(lining_items_vertical_right)

                # horizontal lining
                def create_horizontal_lining(current_lining_thickness, mirror_point=None):
                    lining_horizontal_polyline = get_lining_polyline(current_lining_thickness)
                    if mirror_point:
                        lining_horizontal_polyline = builder.mirror(
                            lining_horizontal_polyline,
                            mirror_axes=V(1, 0),
                            mirror_point=mirror_point
                        )
                        builder.translate(lining_horizontal_polyline, -mirror_point)
                    lining_horizontal_extruded = builder.extrude(
                        lining_horizontal_polyline,
                        magnitude=panel_width - (thickness[0] + thickness[2]),
                        extrusion_vector=V(0, 0, -1),
                        position_z_axis=V(-1, 0, 0),
                        position_x_axis=V(0, 0, 1),
                    )
                    return lining_horizontal_extruded

                lining_horizontal_bottom = create_horizontal_lining(thickness[3])
                builder.translate(lining_horizontal_bottom, V(thickness[0], 0, 0))

                lining_horizontal_top = create_horizontal_lining(thickness[1], mirror_point=V(thickness[1], 0))
                builder.translate(lining_horizontal_top, V(thickness[0], 0, panel_height - thickness[1]))

                # TODO: should implement mirror by Z for more readability
                # TODO: investigate meaning of mirror axes in case of custom x/y/z space
                # lining_horizontal_mirrored = builder.mirror(
                #     lining_horizontal_extruded,
                #     mirror_point=V(0, panel_height/2),
                #     mirror_axes=V(0,1),
                #     create_copy=True
                # )

                lining_items.extend([lining_horizontal_bottom, lining_horizontal_top])
                current_items.extend(lining_items)

                # PANEL
                panel_items = []

                panel_position = V(
                    lining_panel_offset_x, (lining_depth - panel_depth) + lining_panel_offset_y, lining_panel_offset_x
                )
                panel_rect = builder.rectangle(size=V(panel_actual_width, 0, panel_actual_height))
                glass_rect = builder.rectangle(
                    size=V(glass_width, 0, glass_height), position=V(panel_thickness, 0, panel_thickness)
                )
                panel_profile = builder.profile(panel_rect, inner_curves=glass_rect)
                panel_extruded = builder.extrude(
                    panel_profile, panel_depth, extrusion_vector=V(0, 1, 0), position=panel_position
                )
                panel_items.append(panel_extruded)

                current_items.extend(panel_items)

                # add glass
                glass_position = panel_position + V(0, panel_depth / 2 - glass_thickness / 2, 0)
                glass_rect = builder.deep_copy(glass_rect)
                glass = builder.extrude(
                    glass_rect, glass_thickness, extrusion_vector=V(0, 1, 0), position=glass_position
                )
                current_items.append(glass)

                # translate panel
                accumulated_offset = V(accumulated_width, 0, accumulated_height[column_i])
                builder.translate(current_items, accumulated_offset)

                built_panels.append(panel_i)
                window_items.extend(current_items)

                accumulated_height[column_i] += panel_height
                accumulated_width += panel_width

        builder.translate(window_items, V(0, lining_offset, 0))  # wall offset
        representation = builder.get_representation(self.settings["context"], window_items)
        return representation

    def convert_si_to_unit(self, value):
        return value * 0.001 / self.settings["unit_scale"]
