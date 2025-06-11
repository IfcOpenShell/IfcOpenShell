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

from __future__ import annotations
import sys
import numpy as np
import dataclasses
import ifcopenshell.api.geometry
import ifcopenshell.util.unit
from itertools import chain
from ifcopenshell.util.shape_builder import ShapeBuilder, V
from typing import Any, Optional, Literal, Union, overload

DATACLASS_SLOTS = {} if sys.version_info < (3, 10) else {"slots": True}
ZIP_STRICT = {} if sys.version_info < (3, 10) else {"strict": True}

# SCHEMAS describe panels setup
# where:
# - schema rows represent window X axis
# - schema columns represent window Y axis
# - order of rows is from top of the window to bottom

WINDOW_TYPE = Literal[
    "SINGLE_PANEL",
    "DOUBLE_PANEL_HORIZONTAL",
    "DOUBLE_PANEL_VERTICAL",
    "TRIPLE_PANEL_BOTTOM",
    "TRIPLE_PANEL_HORIZONTAL",
    "TRIPLE_PANEL_LEFT",
    "TRIPLE_PANEL_RIGHT",
    "TRIPLE_PANEL_TOP",
    "TRIPLE_PANEL_VERTICAL",
]

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


def mm(x: float) -> float:
    """mm to meters shortcut for readability"""
    return x / 1000


def create_ifc_window_frame_simple(
    builder: ShapeBuilder, size: np.ndarray, thickness: Union[list[float], float], position: Optional[np.ndarray] = None
) -> list[ifcopenshell.entity_instance]:
    """`thickness` of the profile is defined as list in the following order:
    `(LEFT, TOP, RIGHT, BOTTOM)`

    `thickness` can be also defined just as 1 float value.
    """

    if not isinstance(thickness, list):
        thickness = [thickness] * 4
    if position is None:
        position = np.zeros(3)
    np_X, np_Y, np_Z = 0, 1, 2
    np_XZ = [0, 2]
    th_left, th_up, th_right, th_bottom = thickness

    def get_extruded_profile(profile: ifcopenshell.entity_instance):
        return builder.extrude(profile, size[np_Y], position=position, **builder.extrude_kwargs("Y"))

    # if all lining sides are present then we can just use two rectangles
    # as inner and outer curves of the profile
    if thickness.count(0) == 0:
        panel_rect = builder.rectangle(size=size[np_XZ])

        inner_rect_size = size - (th_left + th_right, 0, th_bottom + th_up)
        inner_rect = builder.rectangle(size=inner_rect_size[np_XZ], position=(th_left, th_bottom))

        panel_profile = builder.profile(panel_rect, inner_curves=inner_rect)
        return [get_extruded_profile(panel_profile)]

    # if some side has zero thickness it means we cannot use inner curves
    # and need to generate L/U shape or just separate rectangles
    else:

        def get_segments_from_thickness() -> list[tuple[float, ...]]:
            nonlocal thickness
            segments = []
            cur_segment = []
            for i, thickness_ in enumerate(thickness):
                if thickness_ == 0:
                    if cur_segment:
                        segments.append(tuple(cur_segment))
                    cur_segment = []
                else:
                    cur_segment.append(i)

            if cur_segment:
                if len(segments) > 0 and segments[0][0] == 0:
                    segments[0] = tuple(cur_segment) + segments[0]
                else:
                    segments.append(tuple(cur_segment))
            return segments

        # prepare coords to build a lining
        # fmt: off
        outer_coords = [
            ((0, 0),                   (0, size[np_Z])),
            ((0, size[np_Z]),          (size[np_X], size[np_Z])),
            ((size[np_X], size[np_Z]), (size[np_X], 0)),
            ((size[np_X], 0),          (0, 0)),
        ]
        inner_coords = [
            ((th_left, th_bottom),                        (th_left, size[np_Z] - th_up)),
            ((th_left, size[np_Z] - th_up),               (size[np_X] - th_right, size[np_Z] - th_up)),
            ((size[np_X] - th_right, size[np_Z] - th_up), (size[np_X] - th_right, th_bottom)),
            ((size[np_X] - th_right, th_bottom),          (th_left, th_bottom)),
        ]
        # fmt: on

        def get_points(segment: tuple[float, ...]) -> list[tuple[float, float]]:
            points = []
            for side in segment:
                outer = outer_coords[side]
                if side == segment[0]:  # first segment
                    points.append(outer[0])
                points.append(outer[1])

            for side in reversed(segment):
                inner = inner_coords[side]
                if side == segment[-1]:  # last non zero segment
                    points.append(inner[1])
                points.append(inner[0])
            return points

        segments = get_segments_from_thickness()
        segments_items: list[ifcopenshell.entity_instance] = []
        for seg in segments:
            polyline = builder.polyline(points=get_points(seg), closed=True)
            panel_profile = builder.profile(polyline)
            segments_items.append(get_extruded_profile(panel_profile))

        return segments_items


def window_l_shape_check(
    lining_to_panel_offset_y_full: float,
    lining_depth: float,
    lining_to_panel_offset_x: list[float],
    lining_thickness: list[float],
) -> bool:
    """`lining_thickness` and `lining_to_panel_offset_x` expected to be defined as a list,
    similarly to `create_ifc_window_frame_simple` `thickness` argument"""
    l_shape_check = lining_to_panel_offset_y_full < lining_depth and any(
        x_offset < th for th, x_offset in zip(lining_thickness, lining_to_panel_offset_x, **ZIP_STRICT)
    )
    return l_shape_check


def create_ifc_window(
    builder: ShapeBuilder,
    lining_size: np.ndarray,
    lining_thickness: list[float],
    lining_to_panel_offset_x: float,
    lining_to_panel_offset_y_full: float,
    frame_size: np.ndarray,
    frame_thickness: float,
    glass_thickness: float,
    position: np.ndarray,
    x_offsets: Optional[list[float]] = None,
) -> dict[str, list[ifcopenshell.entity_instance]]:
    """`lining_thickness` and `x_offsets` are expected to be defined as a list,
    similarly to `create_ifc_window_frame_simple` `thickness` argument"""
    lining_items: list[ifcopenshell.entity_instance] = []
    main_lining_size = lining_size

    np_Y = 1

    if x_offsets is None:
        x_offsets = [lining_to_panel_offset_x] * 4
    # need to check offsets to decide whether lining should be rectangle
    # or L shaped
    l_shape_check = window_l_shape_check(
        lining_to_panel_offset_y_full,
        lining_size[np_Y],
        x_offsets,
        lining_thickness,
    )

    if l_shape_check:
        main_lining_size = lining_size.copy()
        main_lining_size[np_Y] = lining_to_panel_offset_y_full

        second_lining_size = lining_size.copy()
        second_lining_size[np_Y] = lining_size[np_Y] - lining_to_panel_offset_y_full
        second_lining_position = V(0, lining_to_panel_offset_y_full, 0)
        second_lining_thickness = [min(th, x_offset) for th, x_offset in zip(lining_thickness, x_offsets, **ZIP_STRICT)]

        second_lining_items = create_ifc_window_frame_simple(
            builder, second_lining_size, second_lining_thickness, second_lining_position
        )
        lining_items.extend(second_lining_items)

    main_lining_items = create_ifc_window_frame_simple(builder, main_lining_size, lining_thickness)
    lining_items.extend(main_lining_items)

    frame_position = V(
        x_offsets[0],
        lining_to_panel_offset_y_full,
        x_offsets[3],
    )

    frame_extruded_items = create_ifc_window_frame_simple(builder, frame_size, frame_thickness, frame_position)

    glass_position = frame_position + V(0, frame_size[np_Y] / 2 - glass_thickness / 2, 0)
    glass_rect = builder.deep_copy(frame_extruded_items[0].SweptArea.InnerCurves[0])
    glass = builder.extrude(glass_rect, glass_thickness, position=glass_position, **builder.extrude_kwargs("Y"))

    output_items = (lining_items, frame_extruded_items, [glass])
    builder.translate(chain(*output_items), position)

    return {"Lining": lining_items, "Framing": frame_extruded_items, "Glazing": [glass]}


# we use dataclass as we need default values for arguments
# it's okay to use slots since we don't need dynamic attributes
@dataclasses.dataclass(**DATACLASS_SLOTS)
class WindowLiningProperties:
    LiningDepth: Optional[float] = None
    """Optional, defaults to 50mm."""

    LiningThickness: Optional[float] = None
    """Optional, defaults to 50mm."""

    LiningOffset: Optional[float] = None
    """Offset to the wall. Optional, defaults to 50mm."""

    LiningToPanelOffsetX: Optional[float] = None
    """Offset from the wall. Optional, defaults to 25mm."""

    # that way it allows you to define overall_depth constant between all panels
    # and still have panels with different size:
    # overall_depth = lining_depth + offset_y
    # full offset from X axis = overall_depth - frame_depth.
    LiningToPanelOffsetY: Optional[float] = None
    """Offset from the lining. Optional, defaults to 25mm."""

    MullionThickness: Optional[float] = None
    """Mullion thickness (horizontal distance between panels).

    Applies to windows of types: DoublePanelVertical, TriplePanelBottom, TriplePanelTop,
    TriplePanelLeft, TriplePanelRight.

    Optional, defaults to 50mm."""

    FirstMullionOffset: Optional[float] = None
    """Distance from the first lining to the mullion center. Optional, defaults to 300mm."""

    SecondMullionOffset: Optional[float] = None
    """Distance from the first lining to the second mullion center. 

    Applies to windows of type: TriplePanelVertical.

    Optional, defaults to 450mm."""

    TransomThickness: Optional[float] = None
    """Transom thickness (vertical distance between panels), works similar way to mullions.

    Applies to windows of types:DoublePanelHorizontal, TriplePanelBottom, TriplePanelTop,
    TriplePanelLeft, TriplePanelRight.

    Optional, defaults to 50mm."""

    FirstTransomOffset: Optional[float] = None
    """Optional, defaults to 300mm."""

    SecondTransomOffset: Optional[float] = None
    """
    Applies to windows of type: TriplePanelHorizontal.
    Optional, defaults to 600mm."""

    ShapeAspectStyle: None = None
    """Optional. Deprecated argument."""

    def initialize_properties(self, unit_scale: float) -> None:
        # in meters
        # fmt: off
        default_values: dict[str, float] = dict(
            LiningDepth          = mm(50),
            LiningThickness      = mm(50),
            LiningOffset         = mm(50),
            LiningToPanelOffsetX = mm(25),
            LiningToPanelOffsetY = mm(25),
            MullionThickness     = mm(50),
            FirstMullionOffset   = mm(300),
            SecondMullionOffset  = mm(450),
            TransomThickness     = mm(50),
            FirstTransomOffset   = mm(300),
            SecondTransomOffset  = mm(600),
        )
        # fmt: on

        si_conversion = 1 / unit_scale
        for attr, default_value in default_values.items():
            if getattr(self, attr) is not None:
                continue
            setattr(self, attr, default_value * si_conversion)


@dataclasses.dataclass(**DATACLASS_SLOTS)
class WindowPanelProperties:
    FrameDepth: Optional[float] = None
    """Frame thickness by Y axis. Optional, defaults to 35 mm."""

    FrameThickness: Optional[float] = None
    """Frame thickness by X axis. Optional, defaults to 35 mm."""

    PanelPosition: None = None
    """Optional, value is never used"""

    PanelOperation: None = None
    """Optional, value is never used.
    Defines the basic ways to describe how window panels operate."""

    ShapeAspectStyle: None = None
    """Optional. Deprecated argument."""

    def initialize_properties(self, unit_scale: float) -> None:
        # in meters
        # fmt: off
        default_values: dict[str, float] = dict(
            FrameDepth     = mm(35),
            FrameThickness = mm(35),
        )
        # fmt: on

        si_conversion = 1 / unit_scale
        for attr, default_value in default_values.items():
            if getattr(self, attr) is not None:
                continue
            setattr(self, attr, default_value * si_conversion)


def add_window_representation(
    file: ifcopenshell.file,
    *,  # keywords only as this API implementation is probably not final
    context: ifcopenshell.entity_instance,
    overall_height: Optional[float] = None,
    overall_width: Optional[float] = None,
    partition_type: WINDOW_TYPE = "SINGLE_PANEL",
    lining_properties: Optional[Union[WindowLiningProperties, dict[str, Any]]] = None,
    panel_properties: Optional[list[Union[WindowPanelProperties, dict[str, Any]]]] = None,
    part_of_product: Optional[ifcopenshell.entity_instance] = None,
    unit_scale: Optional[float] = None,
) -> ifcopenshell.entity_instance:
    """units in usecase_settings expected to be in ifc project units

    :param context: IfcGeometricRepresentationContext for the representation.
    :param overall_height: Overall window height. Defaults to 0.9m.
    :param overall_width: Overall window width. Defaults to 0.6m.
    :param partition_type: Type of the window. Defaults to SINGLE_PANEL.
    :param lining_properties: WindowLiningProperties or a dictionary to create one.
        See WindowLiningProperties description for details.
    :param panel_properties: A list of WindowPanelProperties or dictionaries to create one.
        See WindowPanelProperties description for details.
    :param unit_scale: The unit scale as calculated by
        ifcopenshell.util.unit.calculate_unit_scale. If not provided, it
        will be automatically calculated for you.
    :return: IfcShapeRepresentation for a window.
    """
    usecase = Usecase()
    usecase.file = file
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindow.htm
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowTypePartitioningEnum.htm
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowLiningProperties.htm
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcWindowPanelProperties.htm
    # define unit_scale first as it's going to be used setting default arguments
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file) if unit_scale is None else unit_scale
    settings: dict[str, Any] = {"unit_scale": unit_scale}

    if lining_properties is None:
        lining_properties = WindowLiningProperties()
    elif not isinstance(lining_properties, WindowLiningProperties):
        lining_properties = WindowLiningProperties(**lining_properties)
    lining_properties.initialize_properties(unit_scale)
    lining_properties = dataclasses.asdict(lining_properties)

    if panel_properties is None:
        panel_properties = [WindowPanelProperties()]

    for i in range(len(panel_properties)):
        properties = panel_properties[i]
        if not isinstance(properties, WindowPanelProperties):
            properties = WindowPanelProperties(**properties)
        properties.initialize_properties(unit_scale)
        panel_properties[i] = dataclasses.asdict(properties)

    settings.update(
        {
            "context": context,
            "overall_height": overall_height if overall_height is not None else usecase.convert_si_to_unit(0.9),
            "overall_width": overall_width if overall_width is not None else usecase.convert_si_to_unit(0.6),
            "partition_type": partition_type,
            "lining_properties": lining_properties,
            "panel_properties": panel_properties,
            "part_of_product": part_of_product,
        }
    )

    usecase.settings = settings
    usecase.settings["panel_schema"] = DEFAULT_PANEL_SCHEMAS[usecase.settings["partition_type"]]
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        builder = ShapeBuilder(self.file)
        np_X, np_Y, np_Z = 0, 1, 2
        overall_height: float = self.settings["overall_height"]
        overall_width: float = self.settings["overall_width"]

        if self.settings["context"].TargetView == "ELEVATION_VIEW":
            rect = builder.rectangle(V(overall_width, 0, overall_height))
            representation_evelevation = builder.get_representation(self.settings["context"], rect)
            return representation_evelevation

        panel_schema: list[list[int]] = self.settings["panel_schema"]
        panels: list[dict[str, Any]] = self.settings["panel_properties"]
        accumulated_height: list[float] = [0] * len(panel_schema[0])
        built_panels: list[int] = []
        window_items: list[ifcopenshell.entity_instance] = []
        lining_items: list[ifcopenshell.entity_instance] = []
        framing_items: list[ifcopenshell.entity_instance] = []
        glazing_items: list[ifcopenshell.entity_instance] = []

        lining_props: dict[str, Any] = self.settings["lining_properties"]
        lining_thickness: float = lining_props["LiningThickness"]
        lining_depth: float = lining_props["LiningDepth"]
        lining_offset: float = lining_props["LiningOffset"]
        lining_to_panel_offset_x: float = lining_props["LiningToPanelOffsetX"]
        lining_to_panel_offset_y: float = lining_props["LiningToPanelOffsetY"]
        overall_depth: float = lining_depth + lining_to_panel_offset_y

        mullion_thickness: float = lining_props["MullionThickness"] / 2
        first_mullion_offset: float = lining_props["FirstMullionOffset"]
        second_mullion_offset: float = lining_props["SecondMullionOffset"]
        transom_thickness: float = lining_props["TransomThickness"] / 2
        first_transom_offset: float = lining_props["FirstTransomOffset"]
        second_transom_offset: float = lining_props["SecondTransomOffset"]
        glass_thickness: float = self.convert_si_to_unit(0.01)

        panel_schema = list(reversed(panel_schema))

        # create 2d representation
        def create_ifc_window_2d_representation() -> ifcopenshell.entity_instance:
            items_2d: list[ifcopenshell.entity_instance] = []

            top_row = panel_schema[-1]
            unique_cols = len(set(top_row))
            built_panels: list[int] = []
            accumulated_width: float = 0

            for column_i, panel_i in enumerate(top_row):
                cur_panel_items: list[ifcopenshell.entity_instance] = []

                # lists represent left and right linings
                window_lining_thickness = [lining_thickness] * 2
                closed_lining = [True] * 2

                if panel_i in built_panels:
                    continue

                # detect mullion
                has_mullion = unique_cols > 1
                first_column = column_i == 0
                last_column = column_i == unique_cols - 1
                left_to_mullion = has_mullion and not last_column
                right_to_mullion = has_mullion and not first_column

                if has_mullion:
                    if first_column:
                        panel_width = first_mullion_offset
                    elif last_column:
                        panel_width = overall_width - accumulated_width
                    else:
                        panel_width = second_mullion_offset - accumulated_width

                    # mullion thickness
                    if not first_column:
                        window_lining_thickness[0] = mullion_thickness  # left column
                        closed_lining[0] = False
                    if not last_column:
                        window_lining_thickness[1] = mullion_thickness  # right column
                        closed_lining[1] = False
                else:
                    panel_width = overall_width

                frame_depth: float = panels[panel_i]["FrameDepth"]
                frame_thickness: float = panels[panel_i]["FrameThickness"]
                lining_to_panel_offset_y_full = (lining_depth - frame_depth) + lining_to_panel_offset_y
                base_frame_clear = lining_to_panel_offset_x + frame_thickness - lining_thickness
                current_offset_x = base_frame_clear - frame_thickness + mullion_thickness

                # add lining
                cur_panel_items.append(
                    builder.polyline(
                        [
                            (window_lining_thickness[0], 0),
                            (panel_width - window_lining_thickness[1], 0),
                        ]
                    )
                )

                def get_lining_shape(
                    lining_thickness: float, closed: bool = True, mirror: bool = False, x_offset: Optional[float] = None
                ) -> ifcopenshell.entity_instance:
                    if x_offset is None:
                        x_offset = lining_to_panel_offset_x
                    l_shape_check = window_l_shape_check(
                        lining_to_panel_offset_y_full,
                        lining_depth,
                        [x_offset],
                        [lining_thickness],
                    )
                    if l_shape_check:
                        lining_shape = builder.polyline(
                            [
                                (0, lining_depth),
                                (x_offset, lining_depth),
                                (x_offset, lining_to_panel_offset_y_full),
                                (lining_thickness, lining_to_panel_offset_y_full),
                                (lining_thickness, 0),
                                (0, 0),
                            ],
                            closed=closed,
                        )
                    else:
                        lining_shape = builder.polyline(
                            [
                                (0, lining_depth),
                                (lining_thickness, lining_depth),
                                (lining_thickness, 0),
                                (0, 0),
                            ],
                            closed=closed,
                        )

                    if mirror:
                        builder.mirror(
                            lining_shape,
                            mirror_axes=(1, 0),
                            mirror_point=(panel_width / 2, 0),
                        )

                    return lining_shape

                cur_panel_items.extend(
                    [
                        get_lining_shape(
                            window_lining_thickness[0],
                            closed=closed_lining[0],
                            x_offset=current_offset_x if right_to_mullion else None,
                        ),
                        get_lining_shape(
                            window_lining_thickness[1],
                            closed=closed_lining[1],
                            x_offset=current_offset_x if left_to_mullion else None,
                            mirror=True,
                        ),
                    ]
                )

                # add frame
                frame_items: list[ifcopenshell.entity_instance] = []

                frame_position = (
                    current_offset_x if right_to_mullion else lining_to_panel_offset_x,
                    lining_to_panel_offset_y_full,
                )

                frame_width = panel_width
                frame_width -= current_offset_x if left_to_mullion else lining_to_panel_offset_x
                frame_width -= current_offset_x if right_to_mullion else lining_to_panel_offset_x

                frame_vertical = builder.rectangle(size=(frame_thickness, frame_depth))
                frame_items.extend(
                    [
                        frame_vertical,
                        builder.mirror(
                            frame_vertical,
                            mirror_axes=(1, 0),
                            mirror_point=(frame_width / 2, 0),
                            create_copy=True,
                        ),
                    ]
                )

                frame_horizontal = builder.polyline([(frame_thickness, 0), (frame_width - frame_thickness, 0)])
                frame_items.extend(
                    [
                        frame_horizontal,
                        builder.translate(frame_horizontal, (0, frame_depth), create_copy=True),
                    ]
                )
                # glass
                frame_items.append(builder.translate(frame_horizontal, (0, frame_depth / 2), create_copy=True))

                builder.translate(frame_items, frame_position)
                cur_panel_items.extend(frame_items)

                builder.translate(cur_panel_items, (accumulated_width, 0))

                accumulated_width += panel_width
                built_panels.append(panel_i)
                items_2d.extend(cur_panel_items)

            builder.translate(items_2d, (0, lining_offset))
            representation_2d = builder.get_representation(self.settings["context"], items_2d)
            return representation_2d

        if self.settings["context"].TargetView == "PLAN_VIEW":
            return create_ifc_window_2d_representation()

        # TODO: need more readable way to define panel width and height
        unique_rows_in_col = [
            len(set(row[column_i] for row in panel_schema)) for column_i in range(len(panel_schema[0]))
        ]

        for row_i, panel_row in enumerate(panel_schema):
            accumulated_width = 0
            unique_cols = len(set(panel_row))

            for column_i, panel_i in enumerate(panel_row):
                # detect mullion
                has_mullion = unique_cols > 1
                first_column = column_i == 0
                last_column = column_i == unique_cols - 1
                left_to_mullion = has_mullion and not last_column
                right_to_mullion = has_mullion and not first_column

                # detect transom
                has_transom = unique_rows_in_col[column_i] > 1
                first_row = row_i == 0
                last_row = row_i == unique_rows_in_col[column_i] - 1
                top_to_transom = has_transom and not first_row
                bottom_to_transom = has_transom and not last_row

                # calculate current panel dimensions
                if has_mullion:
                    # panel_width
                    if first_column:
                        panel_width = first_mullion_offset
                    elif last_column:
                        panel_width = overall_width - accumulated_width
                    else:
                        panel_width = second_mullion_offset - accumulated_width
                else:
                    panel_width = overall_width

                if has_transom:
                    if first_row:
                        panel_height = first_transom_offset
                    elif last_row:
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
                frame_depth = cur_panel["FrameDepth"]
                frame_thickness = cur_panel["FrameThickness"]
                lining_to_panel_offset_y_full = (lining_depth - frame_depth) + lining_to_panel_offset_y

                # fmt: off
                # calculate lining thickness and frame size / offset
                # taking into account mullions and transoms
                window_lining_thickness = [
                    mullion_thickness if right_to_mullion  else lining_thickness,
                    transom_thickness if bottom_to_transom else lining_thickness,
                    mullion_thickness if left_to_mullion   else lining_thickness,
                    transom_thickness if top_to_transom    else lining_thickness,
                ]

                # x offsets can differ if there are mullions or transoms because we're trying to maintain symmetry
                base_frame_clear = lining_to_panel_offset_x + frame_thickness - lining_thickness
                current_offset_x = base_frame_clear - frame_thickness + mullion_thickness
                current_offset_z = base_frame_clear - frame_thickness + transom_thickness
                x_offsets = [
                    current_offset_x if right_to_mullion  else lining_to_panel_offset_x,  # LEFT
                    current_offset_z if bottom_to_transom else lining_to_panel_offset_x,  # TOP
                    current_offset_x if left_to_mullion   else lining_to_panel_offset_x,  # RIGHT
                    current_offset_z if top_to_transom    else lining_to_panel_offset_x,  # BOTTOM
                ]
                # fmt: on

                window_lining_size = V(panel_width, lining_depth, panel_height)
                frame_size = window_lining_size.copy()
                frame_size[np_Y] = frame_depth
                frame_size[np_X] -= x_offsets[0] + x_offsets[2]
                frame_size[np_Z] -= x_offsets[1] + x_offsets[3]

                window_panel_position = V(accumulated_width, 0, accumulated_height[column_i])
                # create window panel
                current_window_items = create_ifc_window(
                    builder,
                    window_lining_size,
                    window_lining_thickness,
                    lining_to_panel_offset_x,
                    lining_to_panel_offset_y_full,
                    frame_size,
                    frame_thickness,
                    glass_thickness,
                    window_panel_position,
                    x_offsets,
                )
                built_panels.append(panel_i)
                window_items.extend(chain(*current_window_items.values()))
                lining_items.extend(current_window_items["Lining"])
                framing_items.extend(current_window_items["Framing"])
                glazing_items.extend(current_window_items["Glazing"])

                accumulated_height[column_i] += panel_height
                accumulated_width += panel_width

        builder.translate(window_items, (0, lining_offset, 0))  # wall offset
        representation = builder.get_representation(self.settings["context"], window_items)
        if self.settings["part_of_product"]:
            ifcopenshell.api.geometry.add_shape_aspect(
                self.file,
                "Lining",
                items=lining_items,
                representation=representation,
                part_of_product=self.settings["part_of_product"],
            )
            ifcopenshell.api.geometry.add_shape_aspect(
                self.file,
                "Framing",
                items=framing_items,
                representation=representation,
                part_of_product=self.settings["part_of_product"],
            )
            ifcopenshell.api.geometry.add_shape_aspect(
                self.file,
                "Glazing",
                items=glazing_items,
                representation=representation,
                part_of_product=self.settings["part_of_product"],
            )

        return representation

    @overload
    def convert_si_to_unit(self, value: float) -> float: ...
    @overload
    def convert_si_to_unit(self, value: np.ndarray) -> np.ndarray: ...
    def convert_si_to_unit(self, value: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        si_conversion = 1 / self.settings["unit_scale"]
        return value * si_conversion
