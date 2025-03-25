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
import ifcopenshell.util.unit
import ifcopenshell.api.geometry
import dataclasses
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder, V
from ifcopenshell.api.geometry.add_window_representation import create_ifc_window
from math import cos, radians
from typing import Any, Optional, Literal, Union, get_args, overload


DOOR_TYPE = Literal[
    "SINGLE_SWING_LEFT",
    "SINGLE_SWING_RIGHT",
    "DOUBLE_SWING_RIGHT",
    "DOUBLE_SWING_LEFT",
    "DOUBLE_DOOR_SINGLE_SWING",
    "DOUBLE_DOOR_DOUBLE_SWING",
    "SLIDING_TO_LEFT",
    "SLIDING_TO_RIGHT",
    "DOUBLE_DOOR_SLIDING",
]
SUPPORTED_DOOR_TYPES = get_args(DOOR_TYPE)


def mm(x: float) -> float:
    """mm to meters shortcut for readability"""
    return x / 1000


def create_ifc_door_lining(
    builder: ShapeBuilder, size: np.ndarray, thickness: Union[list[float], float], position: Optional[np.ndarray] = None
) -> ifcopenshell.entity_instance:
    """`thickness` of the profile is defined as list in the following order: `(SIDE, TOP)`

    `thickness` can be also defined just as 1 float value.
    """
    np_X, np_Y, np_Z = 0, 1, 2
    np_XZ = [0, 2]
    if not isinstance(thickness, list):
        thickness = [thickness, thickness]

    th_side, th_up = thickness

    points = V(
        [
            (0.0, 0.0, 0.0),
            (0.0, 0.0, size[np_Z]),
            (size[np_X], 0.0, size[np_Z]),
            (size[np_X], 0.0, 0.0),
            (size[np_X] - th_side, 0.0, 0.0),
            (size[np_X] - th_side, 0.0, size[np_Z] - th_up),
            (th_side, 0.0, size[np_Z] - th_up),
            (th_side, 0.0, 0.0),
        ]
    )

    points = points[:, np_XZ]
    door_lining = builder.polyline(points, closed=True)
    door_lining = builder.extrude(door_lining, size[np_Y], **builder.extrude_kwargs("Y"))
    if position is None:
        position = np.zeros(3)
    builder.translate(door_lining, position)

    return door_lining


def create_ifc_box(
    builder: ShapeBuilder, size: np.ndarray, position: Optional[np.ndarray] = None
) -> ifcopenshell.entity_instance:
    np_Z, np_XY = 2, slice(2)
    rect = builder.rectangle(size[np_XY])
    if position is None:
        position = np.zeros(3)
    box = builder.extrude(rect, size[np_Z], position=position, extrusion_vector=(0, 0, 1))
    return box


# we use dataclass as we need default values for arguments
# it's okay to use slots since we don't need dynamic attributes
@dataclasses.dataclass(slots=True)
class DoorLiningProperties:
    LiningDepth: Optional[float] = None
    """Optional, defaults to 50mm."""

    LiningThickness: Optional[float] = None
    """Optional, defaults to 50mm."""

    LiningOffset: Optional[float] = None
    """Offset from the outer side of the wall (by Y-axis). Optional, defaults to 0.0."""

    LiningToPanelOffsetX: Optional[float] = None
    """Offset from the wall. Optional, defaults to 25mm."""

    LiningToPanelOffsetY: Optional[float] = None
    """Offset from the X-axis (unlike windows). Optional, defaults to 25mm."""

    TransomThickness: Optional[float] = None
    """Vertical distance between door and window panels. Optional, defaults to 0.0."""

    TransomOffset: Optional[float] = None
    """Distance from the bottom door opening
    to the beginning of the transom
    unlike windows TransomOffset which goes to the center of the transom.
    Optional, defaults 1.525m."""

    ShapeAspectStyle: None = None
    """Optional. Deprecated argument."""

    CasingDepth: Optional[float] = None
    """Casing cover wall faces around the opening
    on the left, right and upper sides
    Casing should be either on both sides of the wall or no casing
    If `LiningOffset` is present then therefore casing is not possible on outer wall
    therefore there will be no casing on inner wall either. Optional, defaults to 5mm."""

    CasingThickness: Optional[float] = None
    """Casing thickness by Z-axis. Optional, defaults to 75mm."""

    ThresholdDepth: Optional[float] = None
    """Threshold covers the bottom side of the opening. Optional, defaults to 100mm."""

    ThresholdThickness: Optional[float] = None
    """Theshold thickness by Z-axis. Optional, defaults to 25mm."""

    ThresholdOffset: Optional[float] = None
    """Threshold offset by Y-axis. Optional, defaults to 0.0."""

    def initialize_properties(self, unit_scale: float) -> None:
        # in meters
        # fmt: off
        default_values: dict[str, float] = dict(
            LiningDepth          = mm(50),
            LiningThickness      = mm(50),
            LiningOffset         = 0.0,
            LiningToPanelOffsetX = mm(25),
            LiningToPanelOffsetY = mm(25),
            TransomThickness     = 0.0,
            TransomOffset        = mm(1525),
            CasingDepth          = mm(5),
            CasingThickness      = mm(75),
            ThresholdDepth       = mm(100),
            ThresholdThickness   = mm(25),
            ThresholdOffset      = 0.0,
        )
        # fmt: on

        si_conversion = 1 / unit_scale
        for attr, default_value in default_values.items():
            if getattr(self, attr) is not None:
                continue
            setattr(self, attr, default_value * si_conversion)


@dataclasses.dataclass(slots=True)
class DoorPanelProperties:
    PanelDepth: Optional[float] = None
    """Frame thickness by Y axis. Optional, defaults to 35 mm."""

    PanelWidth: float = 1.0
    """Ratio to the clear door opening. Optional, defaults to 1.0."""

    FrameDepth: Optional[float] = None
    """Frame thickness by Y axis. Optional, defaults to 35 mm."""

    FrameThickness: Optional[float] = None
    """Frame thickness by X axis. Optional, defaults to 35 mm."""

    PanelPosition: None = None
    """Optional, value is never used"""

    PanelOperation: None = None
    """Optional, value is never used.
    Defines the basic ways to describe how door panels operate."""

    ShapeAspectStyle: None = None
    """Optional. Deprecated argument."""

    def initialize_properties(self, unit_scale: float) -> None:
        # in meters
        # fmt: off
        default_values: dict[str, float] = dict(
            PanelDepth     = mm(35),
            FrameDepth     = mm(35),
            FrameThickness = mm(35),
        )
        # fmt: on

        si_conversion = 1 / unit_scale
        for attr, default_value in default_values.items():
            if getattr(self, attr) is not None:
                continue
            setattr(self, attr, default_value * si_conversion)


def add_door_representation(
    file: ifcopenshell.file,
    *,  # keywords only as this API implementation is probably not final
    context: ifcopenshell.entity_instance,
    overall_height: Optional[float] = None,
    overall_width: Optional[float] = None,
    # door type
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoorTypeOperationEnum.htm
    operation_type: DOOR_TYPE = "SINGLE_SWING_LEFT",
    lining_properties: Optional[Union[DoorLiningProperties, dict[str, Any]]] = None,
    panel_properties: Optional[Union[DoorPanelProperties, dict[str, Any]]] = None,
    part_of_product: Optional[ifcopenshell.entity_instance] = None,
    unit_scale: Optional[float] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    """Add a geometric representation for a door.

    units in usecase_settings expected to be in ifc project units

    :param context: IfcGeometricRepresentationContext for the representation.
    :param overall_height: Overall door height. Defaults to 2m.
    :param overall_width: Overall door width. Defaults to 0.9m.
    :param operation_type: Type of the door. Defaults to SINGLE_SWING_LEFT.
    :param lining_properties: DoorLiningProperties or a dictionary to create one.
        See DoorLiningProperties description for details.
    :param panel_properties: DoorPanelProperties or a dictionary to create one.
        See DoorPanelProperties description for details.
    :param unit_scale: The unit scale as calculated by
        ifcopenshell.util.unit.calculate_unit_scale. If not provided, it
        will be automatically calculated for you.
    :return: IfcShapeRepresentation for a door.
    """
    usecase = Usecase()
    usecase.file = file
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoor.htm
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoorLiningProperties.htm
    # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoorPanelProperties.htm
    # define unit_scale first as it's going to be used setting default arguments
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file) if unit_scale is None else unit_scale
    settings: dict[str, Any] = {"unit_scale": unit_scale}

    if lining_properties is None:
        lining_properties = DoorLiningProperties()
    elif not isinstance(lining_properties, DoorLiningProperties):
        lining_properties = DoorLiningProperties(**lining_properties)
    lining_properties.initialize_properties(unit_scale)
    lining_properties = dataclasses.asdict(lining_properties)

    if panel_properties is None:
        panel_properties = DoorPanelProperties()
    elif not isinstance(panel_properties, DoorPanelProperties):
        panel_properties = DoorPanelProperties(**panel_properties)
    panel_properties.initialize_properties(unit_scale)
    panel_properties = dataclasses.asdict(panel_properties)

    settings.update(
        {
            "context": context,
            "overall_height": overall_height if overall_height is not None else usecase.convert_si_to_unit(2.0),
            "overall_width": overall_width if overall_width is not None else usecase.convert_si_to_unit(0.9),
            "operation_type": operation_type,
            "lining_properties": lining_properties,
            "panel_properties": panel_properties,
            "part_of_product": part_of_product,
        }
    )
    usecase.settings = settings
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self) -> Union[ifcopenshell.entity_instance, None]:
        builder = ShapeBuilder(self.file)

        np_X, np_Y, np_Z = 0, 1, 2
        np_XY = slice(2)
        np_YX = [1, 0]

        overall_height: float = self.settings["overall_height"]
        overall_width: float = self.settings["overall_width"]
        door_type: DOOR_TYPE = self.settings["operation_type"]
        double_swing_door = "DOUBLE_SWING" in door_type
        double_door = "DOUBLE_DOOR" in door_type
        sliding_door = "SLIDING" in door_type

        if self.settings["context"].TargetView == "ELEVATION_VIEW":
            rect = builder.rectangle((overall_width, 0, overall_height))
            representation_evelevation = builder.get_representation(self.settings["context"], rect)
            return representation_evelevation

        panel_props = self.settings["panel_properties"]
        lining_props = self.settings["lining_properties"]

        # lining params
        lining_depth: float = lining_props["LiningDepth"]
        lining_thickness_default: float = lining_props["LiningThickness"]
        lining_offset: float = lining_props["LiningOffset"]
        lining_to_panel_offset_x: float = (
            lining_props["LiningToPanelOffsetX"] if not sliding_door else lining_thickness_default
        )
        panel_depth: float = panel_props["PanelDepth"]
        lining_to_panel_offset_y_full: float = (
            lining_props["LiningToPanelOffsetY"] if not sliding_door else -panel_depth
        )

        transom_thickness: float = lining_props["TransomThickness"] / 2
        transfom_offset: float = lining_props["TransomOffset"]
        if transom_thickness == 0:
            transfom_offset = 0
        window_lining_height = overall_height - transfom_offset - transom_thickness

        side_lining_thickness = lining_thickness_default
        panel_lining_overlap_x = max(lining_thickness_default - lining_to_panel_offset_x, 0) if not sliding_door else 0

        top_lining_thickness = transom_thickness or lining_thickness_default
        panel_top_lining_overlap_x = max(top_lining_thickness - lining_to_panel_offset_x, 0) if not sliding_door else 0
        door_opening_width = overall_width - lining_to_panel_offset_x * 2
        if double_swing_door:
            side_lining_thickness = side_lining_thickness - panel_lining_overlap_x
            top_lining_thickness = top_lining_thickness - panel_top_lining_overlap_x

        threshold_thickness: float = lining_props["ThresholdThickness"]
        threshold_depth: float = lining_props["ThresholdDepth"]
        threshold_offset: float = lining_props["ThresholdOffset"]
        threshold_width = overall_width - side_lining_thickness * 2

        casing_thickness: float = lining_props["CasingThickness"]
        casing_depth: float = lining_props["CasingDepth"]

        # panel params
        panel_width: float = door_opening_width * panel_props["PanelWidth"]
        frame_depth: float = panel_props["FrameDepth"]
        frame_thickness: float = panel_props["FrameThickness"]
        frame_height = window_lining_height - lining_to_panel_offset_x * 2
        glass_thickness = self.convert_si_to_unit(0.01)

        # handle dimensions (hardcoded)
        handle_size = self.convert_si_to_unit(V(120, 40, 20) * 0.001)
        handle_offset = self.convert_si_to_unit(V(60, 0, 1000) * 0.001)  # to the handle center
        handle_center_offset = V(handle_size[np_Y] / 2, 0, handle_size[np_Z]) / 2
        slider_arrow_symbol_size = self.convert_si_to_unit(30 * 0.001)

        if transfom_offset:
            panel_height = transfom_offset + transom_thickness - lining_to_panel_offset_x - threshold_thickness
            lining_height = transfom_offset + transom_thickness
        else:
            panel_height = overall_height - lining_to_panel_offset_x - threshold_thickness
            lining_height = overall_height

        # add lining
        lining_size = V(overall_width, lining_depth, lining_height)
        lining_thickness = [side_lining_thickness, top_lining_thickness]

        def l_shape_check(lining_thickness: list[float]) -> bool:
            return lining_to_panel_offset_y_full < lining_depth and any(
                lining_to_panel_offset_x < th for th in lining_thickness
            )

        # create 2d representation
        if self.settings["context"].TargetView == "PLAN_VIEW":
            items_2d: list[ifcopenshell.entity_instance] = []
            panel_size = V(panel_width, panel_depth)
            if not sliding_door:
                panel_position = V(lining_to_panel_offset_x, lining_depth)
            else:
                panel_position = V(lining_to_panel_offset_x, -panel_size[np_Y])

            if self.settings["context"].ContextIdentifier == "Annotation":
                # only sliding door has annotation representation
                if not sliding_door:
                    return None

                # arrow symbol
                arrow_symbol: list[ifcopenshell.entity_instance] = []
                arrow_offset = slider_arrow_symbol_size / cos(radians(15))
                arrow_symbol.append(
                    builder.polyline(
                        points=((0.35 * panel_size[np_X], 0), (0.65 * panel_size[np_X], 0)),
                    )
                )
                arrow_symbol.append(
                    builder.polyline(
                        points=(
                            (slider_arrow_symbol_size, arrow_offset),
                            (0, 0),
                            (slider_arrow_symbol_size, -arrow_offset),
                        ),
                        position_offset=(0.35 * panel_size[np_X], 0),
                    )
                )

                builder.translate(arrow_symbol, panel_position + (0, -arrow_offset * 1.5))

                items_2d.extend(arrow_symbol)

                representation_2d = builder.get_representation(self.settings["context"], items_2d, "Curve2D")
                return representation_2d

            door_items: list[ifcopenshell.entity_instance] = []
            # create lining
            if l_shape_check([side_lining_thickness]):
                lining_points = [
                    (0, 0),
                    (0, lining_depth),
                    (lining_to_panel_offset_x, lining_depth),
                    (lining_to_panel_offset_x, lining_to_panel_offset_y_full),
                    (lining_thickness_default, lining_to_panel_offset_y_full),
                    (lining_thickness_default, 0),
                ]
                lining = builder.polyline(lining_points, closed=True)
            else:
                lining = builder.rectangle((side_lining_thickness, lining_depth))

            items_2d.append(lining)
            items_2d.append(
                builder.mirror(lining, mirror_axes=V(1, 0), mirror_point=V(overall_width / 2, 0), create_copy=True)
            )

            # TODO: make second swing lines dashed
            def create_ifc_door_panel_2d(
                panel_size: np.ndarray,
                panel_position: np.ndarray,
                door_swing_type: Literal["LEFT", "RIGHT"],
                sliding: bool = False,
            ) -> list[ifcopenshell.entity_instance]:
                if sliding:
                    return create_ifc_door_sliding_panel_2d(panel_size, panel_position, door_swing_type)

                door_items: list[ifcopenshell.entity_instance] = []
                panel_size = panel_size[np_YX]
                # create semi-semi-circle
                if double_swing_door:
                    trim_points_mask = (3, 1)
                    second_swing_line = builder.polyline(
                        points=(
                            (0, 0),
                            (0, -panel_size[np_Y]),
                            (panel_size[np_X], -panel_size[np_Y]),
                        )
                    )
                    door_items.append(second_swing_line)
                else:
                    trim_points_mask = (0, 1)
                semicircle = builder.create_ellipse_curve(
                    panel_size[np_Y] - panel_size[np_X],
                    panel_size[np_Y],
                    trim_points_mask=trim_points_mask,
                    position=(panel_size[np_X], 0),
                )
                door_items.append(semicircle)

                # create door
                door = builder.rectangle(panel_size)
                door_items.append(door)

                builder.translate(door_items, panel_position)

                if door_swing_type == "RIGHT":
                    mirror_point = panel_position + (panel_size[np_Y] / 2, 0)
                    builder.mirror(door_items, mirror_axes=(1, 0), mirror_point=mirror_point)
                return door_items

            def create_ifc_door_sliding_panel_2d(
                panel_size: np.ndarray, panel_position: np.ndarray, door_swing_type: Literal["LEFT", "RIGHT"]
            ) -> list[ifcopenshell.entity_instance]:
                door = builder.rectangle(panel_size, position=panel_position - (panel_size[np_X] * 0.5, 0))

                if door_swing_type == "RIGHT":
                    mirror_point = panel_position + (panel_size[np_X] / 2, 0)
                    builder.mirror(door, mirror_axes=(1, 0), mirror_point=mirror_point)
                return [door]

            door_items: list[ifcopenshell.entity_instance] = []
            if double_door:
                panel_size[np_X] = panel_size[np_X] / 2
                door_items.extend(create_ifc_door_panel_2d(panel_size, panel_position, "LEFT", sliding_door))

                mirror_point = panel_position + V(door_opening_width / 2, 0)
                door_items.extend(
                    builder.mirror(door_items, mirror_axes=(1, 0), mirror_point=mirror_point, create_copy=True)
                )
            else:
                door_swing_type = "LEFT" if door_type.endswith("LEFT") else "RIGHT"
                door_items.extend(create_ifc_door_panel_2d(panel_size, panel_position, door_swing_type, sliding_door))
            items_2d.extend(door_items)

            builder.translate(items_2d, (0, lining_offset))
            representation_2d = builder.get_representation(self.settings["context"], items_2d)
            return representation_2d

        lining_items: list[ifcopenshell.entity_instance] = []
        main_lining_size = lining_size

        # need to check offsets to decide whether lining should be rectangle
        # or L shaped
        if l_shape_check(lining_thickness):
            main_lining_size = lining_size.copy()
            main_lining_size[np_Y] = lining_to_panel_offset_y_full

            second_lining_size = lining_size.copy()
            second_lining_size[np_Y] = lining_size[np_Y] - lining_to_panel_offset_y_full
            second_lining_position = V(0, lining_to_panel_offset_y_full, 0)
            second_lining_thickness = [min(th, lining_to_panel_offset_x) for th in lining_thickness]

            second_lining = create_ifc_door_lining(
                builder, second_lining_size, second_lining_thickness, second_lining_position
            )
            lining_items.append(second_lining)

        main_lining = create_ifc_door_lining(builder, main_lining_size, lining_thickness)
        lining_items.append(main_lining)

        # add threshold
        threshold_items: list[ifcopenshell.entity_instance]
        if not threshold_thickness:
            threshold_items = []
        else:
            threshold_size = V(threshold_width, threshold_depth, threshold_thickness)
            threshold_position = V(side_lining_thickness, threshold_offset, 0)
            threshold_items = [create_ifc_box(builder, threshold_size, threshold_position)]

        # add casings
        casing_items: list[ifcopenshell.entity_instance] = []
        if not lining_offset and casing_thickness:
            casing_wall_overlap = max(casing_thickness - lining_thickness_default, 0)
            inner_casing_thickness = [
                casing_thickness - panel_lining_overlap_x,
                casing_thickness - panel_top_lining_overlap_x,
            ]
            outer_casing_thickness = inner_casing_thickness.copy() if double_swing_door else casing_thickness

            casing_size = V(overall_width + casing_wall_overlap * 2, casing_depth, overall_height + casing_wall_overlap)
            casing_position = V(-casing_wall_overlap, -casing_depth, 0)
            outer_casing = create_ifc_door_lining(builder, casing_size, outer_casing_thickness, casing_position)
            casing_items.append(outer_casing)

            inner_casing_position = V(-casing_wall_overlap, lining_depth, 0)
            inner_casing = create_ifc_door_lining(builder, casing_size, inner_casing_thickness, inner_casing_position)
            casing_items.append(inner_casing)

        def create_ifc_door_panel(
            panel_size: np.ndarray, panel_position: np.ndarray, door_swing_type: Literal["LEFT", "RIGHT"]
        ) -> list[ifcopenshell.entity_instance]:
            door_items: list[ifcopenshell.entity_instance] = []
            # add door panel
            door_items.append(create_ifc_box(builder, panel_size, panel_position))
            # add door handle
            handle_points = [
                (0, 0),
                (0, -handle_size[np_Y]),
                (handle_size[np_X], -handle_size[np_Y]),
                (handle_size[np_X], -handle_size[np_Y] / 2),
                (handle_size[np_Y] / 2, -handle_size[np_Y] / 2),
                (handle_size[np_Y] / 2, 0),
            ]
            handle_polyline = builder.polyline(handle_points, closed=True)

            handle_position = panel_position + handle_offset - handle_center_offset

            door_handle = builder.extrude(handle_polyline, handle_size[np_Z], position=handle_position)
            door_items.append(door_handle)

            if door_swing_type == "LEFT":
                builder.mirror(
                    door_handle, mirror_axes=(1, 0), mirror_point=panel_position[np_XY] + (panel_size[np_X] / 2, 0)
                )

            door_handle_mirrored = builder.mirror(
                door_handle,
                mirror_axes=(0, 1),
                mirror_point=handle_position[np_XY] + (0, panel_size[np_Y] / 2),
                create_copy=True,
            )
            door_items.append(door_handle_mirrored)
            return door_items

        door_items: list[ifcopenshell.entity_instance] = []
        panel_size = V(panel_width, panel_depth, panel_height)
        panel_position = V(lining_to_panel_offset_x, lining_to_panel_offset_y_full, threshold_thickness)

        if double_door:
            # keeping a little space between doors for readibility
            double_door_offset = self.convert_si_to_unit(0.001)
            panel_size[np_X] = panel_size[np_X] / 2 - double_door_offset
            door_items.extend(create_ifc_door_panel(panel_size, panel_position, "LEFT"))

            mirror_point = panel_position + V(door_opening_width / 2, 0, 0)
            door_items.extend(
                builder.mirror(door_items, mirror_axes=(1, 0), mirror_point=mirror_point[np_XY], create_copy=True)
            )
        else:
            door_swing_type = "LEFT" if door_type.endswith("LEFT") else "RIGHT"
            door_items.extend(create_ifc_door_panel(panel_size, panel_position, door_swing_type))

        # add on top window
        if not transom_thickness:
            window_lining_items = []
            frame_items = []
            glass_items = []
        else:
            window_lining_thickness = [
                side_lining_thickness,
                lining_thickness_default,
                side_lining_thickness,
                transom_thickness,
            ]
            window_lining_size = V(overall_width, lining_depth, window_lining_height)
            window_position = V(0, 0, overall_height - window_lining_height)
            frame_size = V(door_opening_width, frame_depth, frame_height)
            current_window_items = create_ifc_window(
                builder,
                window_lining_size,
                window_lining_thickness,
                lining_to_panel_offset_x,
                lining_to_panel_offset_y_full,
                frame_size,
                frame_thickness,
                glass_thickness,
                window_position,
            )
            window_lining_items = current_window_items["Lining"]
            frame_items = current_window_items["Framing"]
            glass_items = current_window_items["Glazing"]

        lining_offset_items = lining_items + door_items + window_lining_items + frame_items + glass_items
        builder.translate(lining_offset_items, (0, lining_offset, 0))

        output_items = lining_offset_items + threshold_items + casing_items

        representation = builder.get_representation(self.settings["context"], output_items)
        if self.settings["part_of_product"]:
            ifcopenshell.api.geometry.add_shape_aspect(
                self.file,
                "Lining",
                items=lining_items + window_lining_items + threshold_items + casing_items,
                representation=representation,
                part_of_product=self.settings["part_of_product"],
            )
            ifcopenshell.api.geometry.add_shape_aspect(
                self.file,
                "Framing",
                items=door_items + frame_items,
                representation=representation,
                part_of_product=self.settings["part_of_product"],
            )
            if glass_items:
                ifcopenshell.api.geometry.add_shape_aspect(
                    self.file,
                    "Glazing",
                    items=glass_items,
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
