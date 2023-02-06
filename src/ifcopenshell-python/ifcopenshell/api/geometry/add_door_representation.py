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
from ifcopenshell.api.geometry.add_window_representation import create_ifc_window
from mathutils import Vector

import collections


def create_ifc_door_lining_items(builder: ShapeBuilder, size: Vector, thickness: Vector, position:Vector=V(0,0,0).freeze()):
    """`thickness` of the profile is defined as list in the following order: `(SIDE, TOP)`

    `thickness` can be also defined just as 1 float value.
    """
    if not isinstance(thickness, collections.abc.Iterable):
        thickness = [thickness] * 2

    th_side, th_up = thickness

    left_lining = builder.rectangle(V(th_side, 0, size.z))
    right_lining = builder.translate(left_lining, V(size.x-th_side, 0, 0), create_copy=True)
    top_lining = builder.rectangle(V(size.x, 0, th_up), V(0, 0, size.z-th_up))
    items = [left_lining, right_lining, top_lining]

    items = [builder.extrude(l, size.y, extrusion_vector=V(0,1,0)) for l in items]
    builder.translate(items, position)

    return items

def create_ifc_box(builder: ShapeBuilder, size: Vector, position:Vector=V(0,0,0).freeze()):
    rect = builder.rectangle(size.xy)
    box = builder.extrude(rect, size.z, position=position, extrusion_vector=V(0,0,1))
    return box


class Usecase:
    def __init__(self, file, **settings):
        """units in settings expected to be in ifc project units"""
        self.file = file
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoor.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoorTypeOperationEnum.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoorLiningProperties.htm
        # http://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDoorPanelProperties.htm
        self.settings = {"unit_scale": ifcopenshell.util.unit.calculate_unit_scale(self.file)}
        # TODO: remove upper window from default props after tests
        # TODO: check default values with blender props
        self.settings.update(
            {
                "context": None,  # IfcGeometricRepresentationContext
                "overall_height": self.convert_si_to_unit(0.9),
                "overall_width": self.convert_si_to_unit(0.6),

                # DOUBLE_DOOR_DOUBLE_SWING, DOUBLE_DOOR_FOLDING, DOUBLE_DOOR_LIFTING_VERTICAL, 
                # DOUBLE_DOOR_SINGLE_SWING, DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT, 
                # DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT, DOUBLE_DOOR_SLIDING, 
                # DOUBLE_SWING_LEFT, DOUBLE_SWING_RIGHT, FOLDING_TO_LEFT, 
                # FOLDING_TO_RIGHT, LIFTING_HORIZONTAL, LIFTING_VERTICAL_LEFT, 
                # LIFTING_VERTICAL_RIGHT, REVOLVING, REVOLVING_VERTICAL, 
                # ROLLINGUP, SINGLE_SWING_LEFT, SINGLE_SWING_RIGHT, SLIDING_TO_LEFT, 
                # SLIDING_TO_RIGHT, SWING_FIXED_LEFT, SWING_FIXED_RIGHT
                # TODO: take into account door types
                "operation_type": "SINGLE_SWING_LEFT", # door type
                "lining_properties": {
                    "LiningDepth": self.convert_si_to_unit(0.050),
                    "LiningThickness": self.convert_si_to_unit(0.050),

                    # offset from the outer side of the wall (by Y-axis)
                    "LiningOffset": self.convert_si_to_unit(0.050),
                    # offset from the wall
                    "LiningToPanelOffsetX": self.convert_si_to_unit(0.025), 
                    # offset from the elevation view rectangle (unlike windows)
                    "LiningToPanelOffsetY": self.convert_si_to_unit(0.025),

                    # Casing cover wall faces around the opening
                    # on the left, right and upper sides
                    # Casing should be either on both sides of the wall or no casing
                    # If `LiningOffset` is present then therefore casing is not possible on outer wall
                    # therefore there will be no casing on inner wall either 
                    "CasingDepth": self.convert_si_to_unit(0.025), 
                    "CasingThickness": self.convert_si_to_unit(0.075), # by Z-axis

                    # TODO: link to wall thickness?
                    # Threshold covers the bottom side of the opening
                    "ThresholdDepth": self.convert_si_to_unit(0.025), 
                    "ThresholdThickness": self.convert_si_to_unit(0.025), # by Z-axis
                    # offset to X-axis
                    # TODO: offset goes by Z-axis?
                    "ThresholdOffset": self.convert_si_to_unit(0.025), 

                    # transom - vertical distance between door and window panels 
                    "TransomThickness": self.convert_si_to_unit(0.050),
                    # TransomOffset - distance from the bottom door opening
                    # to the beginning of the transom
                    # unlike windows TransomOffset which goes to the center of the transom
                    "TransomOffset": self.convert_si_to_unit(0.6),
                    "ShapeAspectStyle": None,  # DEPRECATED
                },
                "panel_properties": {
                    "PanelDepth": self.convert_si_to_unit(0.030),  # by Y
                    "PanelWidth": 1.0,  # as ratio to the clear door opening
                    "FrameDepth": self.convert_si_to_unit(0.035),  # by Y
                    "FrameThickness": self.convert_si_to_unit(0.035),  # by X
                    # LEFT, MIDDLE, RIGHT, NOTDEFINED
                    "PanelPosition": ...,  # NEVER USED
                    # defines the basic ways to describe how door panels operate
                    # basically how it opens
                    "PanelOperation": None,  # NEVER USED
                    "ShapeAspectStyle": None,  # DEPRECATED
                },
            }
        )
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):        
        builder = ShapeBuilder(self.file)
        overall_height = self.settings["overall_height"]
        overall_width = self.settings["overall_width"]
        door_type = self.settings["operation_type"]
        
        if door_type not in ('SINGLE_SWING_LEFT', 'SINGLE_SWING_RIGHT'):
            raise NotImplementedError(f'Door type "{door_type}" is not currently supported.')

        if self.settings["context"].TargetView == "ELEVATION_VIEW":
            rect = builder.rectangle(V(overall_width, 0, overall_height))
            representation_evelevation = builder.get_representation(self.settings["context"], rect)
            return representation_evelevation

        panel_props = self.settings["panel_properties"]
        lining_props = self.settings["lining_properties"]

        # lining params
        lining_depth = lining_props['LiningDepth']
        lining_thickness_default = lining_props['LiningThickness']
        lining_offset = lining_props['LiningOffset']
        lining_to_panel_offset_x = lining_props['LiningToPanelOffsetX']
        lining_to_panel_offset_y_full = lining_props['LiningToPanelOffsetY']

        transom_thickness = lining_props['TransomThickness'] / 2
        transfom_offset = lining_props['TransomOffset']
        if transom_thickness == 0:
            transfom_offset = 0

        window_lining_height = overall_height - transfom_offset - transom_thickness
        top_lining_thickness = transom_thickness or lining_thickness_default
        panel_lining_overlap_x = max(lining_thickness_default - lining_to_panel_offset_x, 0) 
        panel_top_lining_overlap_x = max(top_lining_thickness - lining_to_panel_offset_x, 0) 
        door_opening_width = (overall_width - lining_to_panel_offset_x * 2)

        threshold_thickness = lining_props['ThresholdThickness']
        threshold_depth = lining_props['ThresholdDepth']
        threshold_offset = lining_props['ThresholdOffset']
        threshold_width = overall_width - lining_thickness_default * 2

        casing_thickness = lining_props['CasingThickness']
        casing_depth = lining_props['CasingDepth']

        # panel params
        panel_depth = panel_props['PanelDepth']
        panel_width = door_opening_width * panel_props['PanelWidth']
        frame_depth = panel_props['FrameDepth']
        frame_thickness = panel_props['FrameThickness']
        frame_height = window_lining_height - lining_to_panel_offset_x * 2
        glass_thickness = self.convert_si_to_unit(0.01)

        if transfom_offset:
            panel_height = transfom_offset + transom_thickness - lining_to_panel_offset_x - threshold_thickness
            lining_height = transfom_offset + transom_thickness
        else:
            panel_height = overall_height - lining_to_panel_offset_x - threshold_thickness
            lining_height = overall_height
        
        # add lining
        lining_size = V(overall_width, lining_depth, lining_height)
        lining_thickness = [lining_thickness_default, top_lining_thickness]

        def l_shape_check(lining_thickness):
            return lining_to_panel_offset_y_full < lining_depth \
                and any(lining_to_panel_offset_x < th for th in lining_thickness)

        # create 2d representation
        if self.settings["context"].TargetView == "PLAN_VIEW":

            items_2d = []

            # create lining
            if l_shape_check([lining_thickness_default]):
                lining_points = [
                    V(0, 0),
                    V(0, lining_depth),
                    V(lining_to_panel_offset_x, lining_depth),
                    V(lining_to_panel_offset_x, lining_to_panel_offset_y_full),
                    V(lining_thickness_default, lining_to_panel_offset_y_full),
                    V(lining_thickness_default, 0),
                ]
                lining = builder.polyline(lining_points, closed=True)
            else:
                lining = builder.rectangle(V(lining_thickness_default, lining_depth))

            items_2d.append(lining)
            items_2d.append(builder.mirror(lining, mirror_axes=V(1,0), mirror_point=V(overall_width/2, 0), create_copy=True))

            # create semi-semi-circle
            semicircle = builder.create_ellipse_curve(panel_width-panel_depth, 
                                                      panel_width, 
                                                      trim_points_mask=(0,1), 
                                                      position=V(panel_depth, 0))
            items_2d.append(semicircle)

            # create door
            door = builder.rectangle(V(panel_depth, panel_width))
            items_2d.append(door)

            builder.translate([semicircle, door], V(lining_to_panel_offset_x, lining_depth))
            
            if door_type == 'SINGLE_SWING_RIGHT':
                builder.mirror([semicircle, door], mirror_axes=V(1,0), mirror_point=V(overall_width/2, 0))

            representation_2d = builder.get_representation(self.settings["context"], items_2d)
            return representation_2d

        lining_items = []
        main_lining_size = lining_size

        # need to check offsets to decide whether lining should be rectangle
        # or L shaped
        if l_shape_check(lining_thickness):
            main_lining_size = lining_size.copy()
            main_lining_size.y = lining_to_panel_offset_y_full

            second_lining_size = lining_size.copy()
            second_lining_size.y = lining_size.y - lining_to_panel_offset_y_full
            second_lining_position = V(0, lining_to_panel_offset_y_full, 0)
            second_lining_thickness = [min(th, lining_to_panel_offset_x) for th in lining_thickness]

            second_lining = create_ifc_door_lining_items(builder, 
                                                        second_lining_size, 
                                                        second_lining_thickness, 
                                                        second_lining_position)
            lining_items.extend(second_lining)

        main_lining = create_ifc_door_lining_items(builder, main_lining_size, lining_thickness)
        lining_items.extend(main_lining)

        # add threshold
        if not threshold_thickness:
            threshold_items = []
        else:
            threshold_size = V(threshold_width, threshold_depth, threshold_thickness)
            threshold_position = V(lining_thickness_default, threshold_offset, 0)
            threshold_items = [create_ifc_box(builder, threshold_size, threshold_position)]

        # add casings
        casing_items = []
        if not lining_offset and casing_thickness:
            casing_wall_overlap = max(casing_thickness - lining_thickness_default, 0)
            casing_size = V(overall_width + casing_wall_overlap*2, casing_depth, overall_height+casing_wall_overlap)
            casing_position = V(-casing_wall_overlap, -casing_depth, 0)
            outer_casing_items = create_ifc_door_lining_items(builder, casing_size, casing_thickness, casing_position)
            casing_items.extend(outer_casing_items)

            inner_casing_thickness = [
                casing_thickness-panel_lining_overlap_x, 
                casing_thickness-panel_top_lining_overlap_x
            ]
            inner_casing_position = V(-casing_wall_overlap, lining_depth, 0)
            inner_casing_items = create_ifc_door_lining_items(builder, casing_size, inner_casing_thickness, inner_casing_position)
            casing_items.extend(inner_casing_items)

        # add door panel
        panel_size = V(
            panel_width,
            panel_depth,
            panel_height
        )
        panel_position = V(
            lining_to_panel_offset_x,
            lining_to_panel_offset_y_full,
            threshold_thickness
        )
        panel_items = [create_ifc_box(builder, panel_size, panel_position)]

        # add on top window
        if not transom_thickness:
            window_lining_items = []
            frame_items = []
            glass_items = []
        else:
            window_lining_thickness = [lining_thickness_default] * 3        
            window_lining_thickness.append(transom_thickness)
            window_lining_size = V(
                overall_width, 
                lining_depth,
                window_lining_height
            )
            window_position = V(0, 0, overall_height-window_lining_height)
            frame_size = V(
                door_opening_width,
                frame_depth,
                frame_height
            )
            window_lining_items, frame_items, glass_items = create_ifc_window(
                builder, 
                window_lining_size,
                window_lining_thickness,
                lining_to_panel_offset_x,
                lining_to_panel_offset_y_full,
                frame_size,
                frame_thickness,
                glass_thickness,
                window_position
            )

        lining_offset_items = lining_items+panel_items+window_lining_items+frame_items+glass_items
        builder.translate(lining_offset_items, V(0, lining_offset, 0))

        ouput_items = lining_offset_items + threshold_items + casing_items
        representation = builder.get_representation(self.settings["context"], ouput_items)
        return representation

    def convert_si_to_unit(self, value):
        return value / self.settings["unit_scale"]
