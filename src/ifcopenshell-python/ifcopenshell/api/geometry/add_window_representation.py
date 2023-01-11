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
    'SINGLE_PANEL': [[0]],
    'DOUBLE_PANEL_HORIZONTAL': [[0],[1]],
    'DOUBLE_PANEL_VERTICAL': [[0,1]],
    'TRIPLE_PANEL_BOTTOM': [[0,1],[2,2]],
    'TRIPLE_PANEL_TOP': [[0,0], [1,2]],
    'TRIPLE_PANEL_LEFT': [[0,1],[0,2]],
    'TRIPLE_PANEL_RIGHT': [[0,1],[2,1]],
    'TRIPLE_PANEL_HORIZONTAL': [[0],[1],[2]],
    'TRIPLE_PANEL_VERTICAL': [[0,1,2]],
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
            "partition_type": 'SINGLE_PANEL',
            "overall_height": 900,
            "overall_width": 600, 
            "lining_properties": {
                'LiningDepth': 50,
                'LiningThickness': 50,
                'LiningOffset': 50, # offset to the wall
                'LiningToPanelOffsetX': 25,
                'LiningToPanelOffsetY': 25,
                # applies to DoublePanelVertical, TriplePanelBottom, TriplePanelTop, TriplePanelLeft, TriplePanelRight
                # mullion - distance between panels
                'FirstMullionOffset': ..., # distance from the first lining to the mullion
                # TODO: take mullion thickness into account
                'MullionThickness': ...,
                # applies to DoublePanelHorizontal, TriplePanelBottom, TriplePanelTop, TriplePanelLeft, TriplePanelRight
                # works similar way to mullion
                'FirstTransomOffset': ..., 
                'TransomThickness': ...,
                # applies to TriplePanelVertical
                'SecondMullionOffset': ..., # distance from the first lining to the second mullion
                # applies to TriplePanelHorizontal
                'SecondTransomOffset': ...,
                'ShapeAspectStyle': None, # DEPRECATED
            }, 
            "panel_properties": [
                {
                    'FrameDepth': 35, # by Y
                    'FrameThickness': 35, # by X
                    # BOTTOM, LEFT, MIDDLE, RIGHT, TOP
                    'PanelPosition': ...,
                    # defines the basic ways to describe how window panels operate
                    # how it's hanged, how it opens
                    'OperationType': None, 
                    'ShapeAspectStyle': None, # DEPRECATED

                    # Custom Parameter not available in IFC
                    # dimensions of the panel relative to overall window dimensions
                    'RelativeWidth': 1.0,
                    'RelativeHeight': 1.0,
                },
            ]
        }

        for key, value in settings.items():
            self.settings[key] = value
        self.settings["panel_schema"] = DEFAULT_PANEL_SCHEMAS[self.settings['partition_type']]

        # recalculate relative width and height to avoid errors
        # TODO: rework or remove
        # panels_data = self.settings['panel_properties']
        # current_height = sum(p['RelativeHeight'] for p in panels_data)
        # current_width = sum(p['RelativeWidth'] for p in panels_data)
        
        # for p in panels_data:
        #     if current_height != 1.0:
        #         p['RelativeHeight'] = p['RelativeHeight'] / current_height

        #     if current_width != 1.0:
        #         p['RelativeWidth'] = p['RelativeWidth'] / current_width

        

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        builder = ShapeBuilder(self.file)
        overall_height = self.convert_si_to_unit(self.settings['overall_height'])
        overall_width = self.convert_si_to_unit(self.settings['overall_width'])

        if self.settings['context'].TargetView == 'ELEVATION_VIEW':
            rect = builder.rectangle(V(overall_width, 0, overall_height))
            representation_evelevation = builder.get_representation(self.settings['context'], rect)
            return representation_evelevation


        panel_schema = self.settings['panel_schema']
        panels = self.settings['panel_properties']
        accumulated_height = [0] * len(panel_schema[0])
        built_panels = []
        window_items = []

        lining_thickness = self.convert_si_to_unit(self.settings['lining_properties']['LiningThickness'])
        lining_depth = self.convert_si_to_unit(self.settings['lining_properties']['LiningDepth'])
        lining_offset = self.convert_si_to_unit(self.settings['lining_properties']['LiningOffset'])
        lining_panel_offset_x = self.convert_si_to_unit(self.settings['lining_properties']['LiningToPanelOffsetX'])
        lining_panel_offset_y = self.convert_si_to_unit(self.settings['lining_properties']['LiningToPanelOffsetY'])
        glass_thickness = self.convert_si_to_unit(10)

        for row_i, panel_row in enumerate(reversed(panel_schema)):
            accumulated_width = 0
            for column_i, panel_i in enumerate(panel_row):
                if panel_i in built_panels:
                    accumulated_height[column_i] += cur_panel['RelativeHeight']
                    accumulated_width += cur_panel['RelativeWidth']
                    continue
                cur_panel = panels[panel_i]
                current_items = []
                panel_depth = self.convert_si_to_unit(cur_panel['FrameDepth'])
                panel_thickness = self.convert_si_to_unit(cur_panel['FrameThickness'])
                panel_height = cur_panel['RelativeHeight'] * overall_height
                panel_width = cur_panel['RelativeWidth'] * overall_width

                panel_actual_width = panel_width-lining_panel_offset_x*2
                panel_actual_height = panel_height-lining_panel_offset_x*2

                glass_width = panel_actual_width - panel_thickness*2
                glass_height = panel_actual_height - panel_thickness*2

                # build lining
                lining_items_vertical = []
                lining_items = []
                # lining is calculated on panel level because
                # panel depth is used
                lining_rectangle = builder.rectangle( size=V(lining_thickness, lining_depth) )

                # need to check offsets to decide whether lining should be rectangle
                # or L shaped
                if lining_panel_offset_x >= lining_thickness \
                    or lining_panel_offset_y >= lining_depth:
                    lining_vertical_polyline = ifcopenshell.util.element.copy_deep(self.file, lining_rectangle)
                    lining_vertical_height = panel_height

                else:
                    lining_points = [
                        V(0, 0), 
                        V(0, lining_depth),
                        V(lining_panel_offset_x, lining_depth),
                        V(lining_panel_offset_x, lining_depth-(panel_depth-lining_panel_offset_y)),
                        V(lining_thickness, lining_depth-(panel_depth-lining_panel_offset_y)),
                        V(lining_thickness, 0),
                    ]

                    # lining vertical
                    lining_vertical_polyline = builder.polyline(lining_points, closed=True)
                    lining_vertical_height = panel_height - lining_panel_offset_x * 2

                    # if lining panel X offset is present 
                    # then we also need to add two more box shapes
                    # to finish the lining after the panel ends 
                    if lining_panel_offset_x > 0:
                        lining_vertical_addition =  builder.extrude(builder.deep_copy(lining_rectangle), lining_panel_offset_x)

                        lining_items_vertical.extend([
                            lining_vertical_addition,
                            builder.translate(lining_vertical_addition, V(0,0,panel_height - lining_panel_offset_x), create_copy=True)
                        ])

                    # horizontal lining
                    lining_horizontal_polyline = builder.deep_copy(lining_vertical_polyline)
                    lining_horizontal_extruded = builder.extrude(
                        lining_horizontal_polyline,
                        magnitude=panel_width-2*lining_thickness,
                        extrusion_vector=V(0,0,-1),
                        position_z_axis=V(-1,0,0),
                        position_x_axis=V(0,0,1),
                        position=V(lining_thickness, 0, 0)
                    )

                    # TODO: should implement mirror by Z for more readability
                    # TODO: investigate meaning of mirror axes in case of custom x/y/z space
                    # lining_horizontal_mirrored = builder.mirror(
                    #     lining_horizontal_extruded, 
                    #     mirror_point=V(0, panel_height/2),
                    #     mirror_axes=V(0,1),
                    #     create_copy=True
                    # )
                    
                    lining_horizontal_polyline_mirrored = builder.mirror(
                        lining_horizontal_polyline,
                        mirror_axes=V(1,0),
                        mirror_point=V(lining_thickness,0),
                        create_copy=True
                    )
                    lining_horizontal_mirrored = builder.extrude(
                        lining_horizontal_polyline_mirrored,
                        magnitude=panel_width-2*lining_thickness,
                        extrusion_vector=V(0,0,-1),
                        position_z_axis=V(-1,0,0),
                        position_x_axis=V(0,0,1),
                        position=V(lining_thickness, 0, panel_height - lining_thickness*2)
                    )
                    lining_items.extend([lining_horizontal_extruded, lining_horizontal_mirrored])

                extrusion_position = V(0,0,lining_panel_offset_x)
                lining_vertical_extruded = builder.extrude(lining_vertical_polyline, lining_vertical_height, position=extrusion_position)
                lining_items_vertical.append(lining_vertical_extruded)

                lining_items_vertical_mirrored = builder.mirror(
                    lining_items_vertical, mirror_point=V(panel_width/2, 0), 
                    mirror_axes=V(1,0),
                    create_copy=True)

                lining_items.extend(lining_items_vertical)
                lining_items.extend(lining_items_vertical_mirrored)
                current_items.extend(lining_items)

                # PANEL
                panel_items = []

                panel_position = V(
                    lining_panel_offset_x,
                    (lining_depth-panel_depth) + lining_panel_offset_y,
                    lining_panel_offset_x)
                panel_rect = builder.rectangle(size=V(panel_actual_width, 0, panel_actual_height))
                glass_rect = builder.rectangle(
                    size=V(glass_width, 0, glass_height), 
                    position=V(panel_thickness, 0, panel_thickness))
                panel_profile = builder.profile(panel_rect, inner_curves=glass_rect)
                panel_extruded = builder.extrude(
                    panel_profile, 
                    panel_depth, 
                    extrusion_vector=V(0,1,0),
                    position=panel_position)
                panel_items.append(panel_extruded)

                current_items.extend(panel_items)

                # add glass
                glass_position = panel_position + V(0, panel_depth/2-glass_thickness/2, 0)
                glass_rect = builder.deep_copy(glass_rect)
                glass = builder.extrude(
                    glass_rect, 
                    glass_thickness,
                    extrusion_vector=V(0,1,0),
                    position=glass_position
                )
                current_items.append(glass)

                # translate panel
                accumulated_offset = V(accumulated_width, 0, accumulated_height[column_i]) * V(overall_width, 0, overall_height)
                builder.translate(current_items, accumulated_offset)

                built_panels.append(panel_i)
                window_items.extend(current_items)
            
                accumulated_height[column_i] += cur_panel['RelativeHeight']
                accumulated_width += cur_panel['RelativeWidth']

        builder.translate(window_items, V(0, lining_offset, 0)) # wall offset
        representation = builder.get_representation(self.settings['context'], window_items)
        return representation

    def convert_si_to_unit(self, value):
        return value * 0.001 / self.settings["unit_scale"]

# TODO: remove test at the end
if __name__ == "__main__":
    ifc_file = ifcopenshell.file()
    project = ifcopenshell.api.run(
        "root.create_entity", ifc_file, ifc_class="IfcProject", name=f"Non-structural assets library"
    )
    library = ifcopenshell.api.run(
        "root.create_entity", ifc_file, ifc_class="IfcProjectLibrary", name=f"Non-structural assets library"
    )
    ifcopenshell.api.run("project.assign_declaration", ifc_file, definition=library, relating_context=project)
    unit = ifcopenshell.api.run("unit.add_si_unit", ifc_file, unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
    ifcopenshell.api.run("unit.assign_unit", ifc_file, units=[unit])
    model = ifcopenshell.api.run("context.add_context", ifc_file, context_type="Model")
    plan = ifcopenshell.api.run("context.add_context", ifc_file, context_type="Plan")

    representations = {
        "body": ifcopenshell.api.run(
            "context.add_context",
            ifc_file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        ),
        "elevation": ifcopenshell.api.run(
            "context.add_context",
            ifc_file,
            context_type="Model",
            context_identifier="Profile",
            target_view="ELEVATION_VIEW",
            parent=model,
        ),
        "annotation": ifcopenshell.api.run(
            "context.add_context",
            ifc_file,
            context_type="Plan",
            context_identifier="Annotation",
            target_view="PLAN_VIEW",
            parent=plan,
        ),
    }


    settings = {
        'context': representations['body'],
        # SINGLE_PANEL, DOUBLE_PANEL_HORIZONTAL, DOUBLE_PANEL_VERTICAL, 
        # TRIPLE_PANEL_BOTTOM, TRIPLE_PANEL_HORIZONTAL, TRIPLE_PANEL_LEFT, TRIPLE_PANEL_RIGHT, TRIPLE_PANEL_TOP, TRIPLE_PANEL_VERTICAL
        "partition_type": 'TRIPLE_PANEL_RIGHT',
        "overall_height": 900,
        "overall_width": 600*3, 
        # "lining_properties": {
        #     'LiningDepth': 50,
        #     'LiningThickness': 50,
        #     'LiningOffset': 50, # offset to the wall
        #     'LiningToPanelOffsetX': 25,
        #     'LiningToPanelOffsetY': 25,
        #     # applies to DoublePanelVertical, TriplePanelBottom, TriplePanelTop, TriplePanelLeft, TriplePanelRight
        #     # mullion - distance between panels
        #     'FirstMullionOffset': ..., # distance from the first lining to the mullion
        #     # TODO: take mullion thickness into account
        #     'MullionThickness': ...,
        #     # applies to DoublePanelHorizontal, TriplePanelBottom, TriplePanelTop, TriplePanelLeft, TriplePanelRight
        #     # works similar way to mullion
        #     'FirstTransomOffset': ..., 
        #     'TransomThickness': ...,
        #     # applies to TriplePanelVertical
        #     'SecondMullionOffset': ..., # distance from the first lining to the second mullion
        #     # applies to TriplePanelHorizontal
        #     'SecondTransomOffset': ...,
        #     'ShapeAspectStyle': None, # DEPRECATED
        # }, 
        "panel_properties": [
            {
                'FrameDepth': 35, # by Y
                'FrameThickness': 35, # by X
                'RelativeWidth': 1.0/2,
                'RelativeHeight': 1.0/2,
            },
            {
                'FrameDepth': 35, # by Y
                'FrameThickness': 35, # by X
                'RelativeWidth': 1.0/2,
                'RelativeHeight': 1.0,
            },
            {
                'FrameDepth': 35, # by Y
                'FrameThickness': 35, # by X
                'RelativeWidth': 1.0/2,
                'RelativeHeight': 1.0/2,
            },
        ]
    }
    # builder = ShapeBuilder(ifc_file)
    # points = [V(0,0), V(5,1)]
    # print(points)
    # base_point = V(2,2)
    # points = [p + base_point for p in points]
    # points = [builder.mirror_2d_point(p, mirror_axes=V(0,1), mirror_point=V(3,3)) for p in points]
    # print('mirrored')
    # print(points)
    # print('mirrored base point')
    # base_point = builder.mirror_2d_point(base_point, mirror_axes=V(0,1), mirror_point=V(3,3))
    # print(base_point)
    # print('base line')
    # print([p - base_point for p in points])

    use_case = Usecase(ifc_file, **settings)
    representation = use_case.execute()
    print(representation)

    settings['context'] = representations['elevation']
    use_case = Usecase(ifc_file, **settings)
    representation_2d = use_case.execute()
    print(representation_2d)

    ifc_file.write("tmp.ifc")