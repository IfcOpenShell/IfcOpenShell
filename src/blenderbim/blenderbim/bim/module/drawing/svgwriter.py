# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import bpy
import math
import bmesh
import pystache
import mathutils
import xml.etree.ElementTree as ET
import svgwrite
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.bim.module.drawing.helper as helper
import blenderbim.bim.module.drawing.annotation as annotation

from blenderbim.bim.module.drawing.data import DecoratorData
from blenderbim.bim.ifc import IfcStore

from math import pi, ceil, atan, degrees
from mathutils import geometry, Vector
from bpy_extras import view3d_utils


class External(svgwrite.container.Group):
    def __init__(self, xml, **extra):
        self.xml = xml

        # Remove namespace
        ns = "{http://www.w3.org/2000/svg}"
        nsl = len(ns)
        for elem in self.xml.iter():
            if elem.tag.startswith(ns):
                elem.tag = elem.tag[nsl:]

        super(External, self).__init__(**extra)

    def get_xml(self):
        return self.xml


class SvgWriter:
    def __init__(self):
        self.data_dir = None
        self.human_scale = "NTS"
        self.metadata = []
        self.scale = 1 / 100  # 1:100
        self.camera_width = None
        self.camera_height = None
        self.related_paths = None

    def create_blank_svg(self, output_path):
        self.define_related_paths() # making sure all paths are defined
        self.calculate_scale()
        self.svg = svgwrite.Drawing(
            output_path,
            size=("{}mm".format(self.width), "{}mm".format(self.height)),
            viewBox=("0 0 {} {}".format(self.width, self.height)),
            id="root",
            data_scale=self.human_scale,
            debug=False,  # Disable validation so that we can insert the IFC namespace
        )
        self.svg.attribs["xmlns:ifc"] = "http://www.ifcopenshell.org/ns"
        return self

    def save(self):
        self.svg.save(pretty=True)

    def draw_underlay(self, image):
        self.svg.add(
            self.svg.image(
                os.path.join("..", "diagrams", os.path.basename(image)),
                width=self.width,
                height=self.height,
            )
        )
        return self

    def define_related_paths(self, **related_paths):
        if not self.related_paths:
            self.related_paths = {}

        if not related_paths:
            related_paths = {
                "Stylesheet": os.path.join(self.data_dir, "styles", f"default.css"),
                "Markers": os.path.join(self.data_dir, "templates", "markers.svg"),
                "Symbols": os.path.join(self.data_dir, "templates", "symbols.svg"),
                "Patterns": os.path.join(self.data_dir, "templates", "patterns.svg"),
            }
            for path_name in list(related_paths.keys()):
                if path_name in self.related_paths:
                    del related_paths[path_name]

        for path_name in related_paths:
            uri = related_paths[path_name]
            custom_path = tool.Ifc.resolve_uri(uri)
            if custom_path:
                self.related_paths[path_name] = custom_path

    def define_boilerplate(self):
        self.add_stylesheet()
        self.add_markers()
        self.add_symbols()
        self.add_patterns()
        return self

    def calculate_scale(self):
        # svg_scale is for conversion from m to paper units
        # paper units = mm x drawing scale
        self.svg_scale = self.scale * 1000  # IFC is in meters, SVG is in mm
        self.raw_width = self.camera_width
        self.raw_height = self.camera_height
        self.width = self.raw_width * self.svg_scale
        self.height = self.raw_height * self.svg_scale

    def add_stylesheet(self):
        with open(self.related_paths["Stylesheet"], "r") as stylesheet:
            self.svg.defs.add(self.svg.style(stylesheet.read()))

    def add_markers(self):
        tree = ET.parse(self.related_paths["Markers"])
        root = tree.getroot()
        for child in root:
            self.svg.defs.add(External(child))

    def add_symbols(self):
        tree = ET.parse(self.related_paths["Symbols"])
        root = tree.getroot()
        for child in root:
            self.svg.defs.add(External(child))

    def find_xml_symbol_by_id(self, id):
        tree = ET.parse(self.related_paths["Symbols"])
        xml_symbol = tree.find(f'.//*[@id="{id}"]')
        return External(xml_symbol) if xml_symbol else None

    def add_patterns(self):
        tree = ET.parse(self.related_paths["Patterns"])
        root = tree.getroot()
        for child in root:
            self.svg.defs.add(External(child))

    def draw_annotations(self, annotations):
        for element in annotations:
            obj = tool.Ifc.get_object(element)
            if not obj or element.ObjectType == "DRAWING":
                continue
            elif element.ObjectType == "GRID":
                self.draw_grid_annotation(obj)
            elif element.ObjectType == "TEXT_LEADER":
                self.draw_leader_annotation(obj)
            elif element.ObjectType == "STAIR_ARROW":
                self.draw_stair_annotation(obj)
            elif element.ObjectType == "DIMENSION":
                self.draw_dimension_annotations(obj)
            elif element.ObjectType == "ANGLE":
                self.draw_angle_annotations(obj)
            elif element.ObjectType == "RADIUS":
                self.draw_radius_annotations(obj)
            elif element.ObjectType == "DIAMETER":
                self.draw_diameter_annotations(obj)
            elif element.ObjectType == "ELEVATION":
                self.draw_elevation_annotation(obj)
            elif element.ObjectType == "SECTION":
                self.draw_section_annotation(obj)
            elif element.ObjectType == "BREAKLINE":
                self.draw_break_annotations(obj)
            elif element.ObjectType == "HIDDEN_LINE":
                self.draw_line_annotation(obj)
            elif element.ObjectType == "PLAN_LEVEL":
                self.draw_plan_level_annotation(obj)
            elif element.ObjectType == "SECTION_LEVEL":
                self.draw_section_level_annotation(obj)
            elif element.ObjectType == "TEXT":
                self.draw_text_annotation(obj, obj.location)
            elif element.ObjectType in ("FALL", "SLOPE_ANGLE", "SLOPE_FRACTION", "SLOPE_PERCENT"):
                self.draw_fall_annotations(obj)
            else:
                self.draw_misc_annotation(obj)

        # Experimental integration with the MeasureIt-ARCH Add-on
        self.draw_measureit_arch_dimension_annotations()
        return self

    def draw_section_level_annotation(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        classes = self.get_attribute_classes(obj)
        element = tool.Ifc.get_entity(obj)
        storey = tool.Drawing.get_annotation_element(element)
        tag = storey.Name if storey else element.Description
        for spline in obj.data.splines:
            points = self.get_spline_points(spline)
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
            text_position = Vector(
                (
                    (x_offset + projected_points[0].x) * self.svg_scale,
                    ((y_offset - projected_points[0].y) * self.svg_scale) - 3.5,
                )
            )
            # TODO: allow metric to be configurable
            rl = (matrix_world @ points[0].co.xyz).z
            if bpy.context.scene.unit_settings.system == "IMPERIAL":
                rl = helper.format_distance(rl)
            else:
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                rl /= unit_scale
                rl = ifcopenshell.util.geolocation.auto_z2e(tool.Ifc.get(), rl)
                rl *= unit_scale
                rl = "{:.3f}m".format(rl)
            text_style = {
                "text-anchor": "start",
                "alignment-baseline": "baseline",
                "dominant-baseline": "baseline",
            }
            self.svg.add(self.svg.text(f"RL +{rl}", insert=tuple(text_position), class_="SECTIONLEVEL", **text_style))
            if tag:
                self.svg.add(self.svg.text(tag, insert=(text_position[0], text_position[1] - 5), **text_style))

    def draw_stair_annotation(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        classes = self.get_attribute_classes(obj)
        for spline in obj.data.splines:
            points = self.get_spline_points(spline)
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            start = Vector(((x_offset + projected_points[0].x), (y_offset - projected_points[0].y)))
            next_point = Vector(((x_offset + projected_points[1].x), (y_offset - projected_points[1].y)))
            text_position = (start * self.svg_scale) - ((next_point - start).normalized() * 5)
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
            self.svg.add(
                self.svg.text(
                    "UP",
                    insert=tuple(text_position),
                    class_="STAIR",
                    **{
                        "text-anchor": "middle",
                        "alignment-baseline": "middle",
                        "dominant-baseline": "middle",
                    },
                )
            )

    def draw_grid_annotation(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        classes = self.get_attribute_classes(obj)
        for edge in obj.data.edges:
            v0_global = matrix_world @ obj.data.vertices[edge.vertices[0]].co.xyz
            v1_global = matrix_world @ obj.data.vertices[edge.vertices[1]].co.xyz
            v0 = self.project_point_onto_camera(v0_global)
            v1 = self.project_point_onto_camera(v1_global)
            start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
            end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
            vector = end - start
            line = self.svg.add(
                self.svg.line(
                    start=tuple(start * self.svg_scale), end=tuple(end * self.svg_scale), class_=" ".join(classes)
                )
            )
            line["stroke-dasharray"] = "12.5, 3, 3, 3"
            axis_tag = tool.Ifc.get_entity(obj).Name
            self.svg.add(
                self.svg.text(
                    axis_tag,
                    insert=tuple(start * self.svg_scale),
                    class_="GRID",
                    **{
                        "text-anchor": "middle",
                        "alignment-baseline": "middle",
                        "dominant-baseline": "middle",
                    },
                )
            )
            self.svg.add(
                self.svg.text(
                    axis_tag,
                    insert=tuple(end * self.svg_scale),
                    class_="GRID",
                    **{
                        "text-anchor": "middle",
                        "alignment-baseline": "middle",
                        "dominant-baseline": "middle",
                    },
                )
            )

    def draw_misc_annotation(self, obj):
        # We have to decide whether this should come from Blender or from IFC.
        # For the moment, for convenience of experimenting with ideas, it comes
        # from Blender. In the future, it should probably come from IFC.
        if not isinstance(obj.data, bpy.types.Mesh):
            return

        classes = self.get_attribute_classes(obj)
        if len(obj.data.polygons) == 0:
            self.draw_edge_annotation(obj, classes)
            return

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bm.faces.ensure_lookup_table()

        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        for face in bm.faces:
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in face.verts]
            projected_points.append(projected_points[0])
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))

    def get_attribute_classes(self, obj):
        element = tool.Ifc.get_entity(obj)
        global_id = "GlobalId-{}".format(element.GlobalId)
        predefined_type = "PredefinedType-" + self.canonicalise_class_name(
            str(ifcopenshell.util.element.get_predefined_type(element))
        )
        classes = [global_id, element.is_a(), predefined_type]
        custom_classes = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes")
        if custom_classes:
            classes.extend(custom_classes.split())
        for key in self.metadata:
            value = ifcopenshell.util.selector.get_element_value(element, key)
            if value:
                classes.append(self.canonicalise_class_name(key) + "-" + self.canonicalise_class_name(str(value)))
        return classes

    def canonicalise_class_name(self, name):
        return re.sub("[^0-9a-zA-Z]+", "", name)

    def draw_line_annotation(self, obj):
        # TODO: properly scope these offsets
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        classes = self.get_attribute_classes(obj)
        matrix_world = obj.matrix_world

        if isinstance(obj.data, bpy.types.Curve):
            for spline in obj.data.splines:
                points = self.get_spline_points(spline)
                projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
                d = " ".join(
                    [
                        "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                        for p in projected_points
                    ]
                )
                d = "M{}".format(d[1:])
                path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
        elif isinstance(obj.data, bpy.types.Mesh):
            self.draw_edge_annotation(obj, classes)

    def draw_edge_annotation(self, obj, classes):
        predefined_type = classes[2].split("-", 1)[1]

        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world

        def draw_simple_edge_annotation(v0, v1):
            v0_global = matrix_world @ obj.data.vertices[v0].co.xyz
            v1_global = matrix_world @ obj.data.vertices[v1].co.xyz
            v0 = self.project_point_onto_camera(v0_global)
            v1 = self.project_point_onto_camera(v1_global)
            start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
            end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
            line = self.svg.add(
                self.svg.line(start=start * self.svg_scale, end=end * self.svg_scale, class_=" ".join(classes))
            )

        # BATTING ANNOTATIONS
        if predefined_type == "BATTING":
            v0_global = matrix_world @ obj.data.vertices[0].co.xyz
            v1_global = matrix_world @ obj.data.vertices[1].co.xyz
            v0 = self.project_point_onto_camera(v0_global)
            v1 = self.project_point_onto_camera(v1_global)
            start_svg = Vector(((x_offset + v0.x), (y_offset - v0.y))) * self.svg_scale
            end_svg = Vector(((x_offset + v1.x), (y_offset - v1.y))) * self.svg_scale

            element = tool.Ifc.get_entity(obj)
            pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_Batting") or {}

            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            # default thickness set to 15 mm in paper space to keep the insulation visible
            thickness = pset_data["Thickness"] * unit_scale * self.svg_scale if "Thickness" in pset_data else 15.0
            reverse_x = pset_data.get("Reverse pattern direction", False)

            if reverse_x:
                start_svg, end_svg = end_svg, start_svg

            pattern_dir = (end_svg - start_svg).normalized()
            pattern_length = (end_svg - start_svg).length
            segment_width = thickness / 2.5

            segments = ceil(pattern_length / segment_width)
            end_marker_width = pattern_length - segment_width * (segments - 1)

            points = [start_svg + pattern_dir * segment_width * i for i in range(segments)]
            marker_id = f"batting-{element.GlobalId}"
            marker_end_id = f"batting-end-{element.GlobalId}"
            path_data = f"""M 0 {0.2*thickness}
                A {0.5*segment_width} {0.2*thickness} 0 0 1 {segment_width} {0.2*thickness}
                L {0.5*segment_width} {0.8*thickness}
                M 0 {0.2*thickness}
                L {0.5*segment_width} {0.8*thickness}
                A {0.5*segment_width} {0.2*thickness} 0 0 0 {segment_width} {1.0*thickness}
                M {0.5*segment_width} {0.8*thickness}
                A {0.5*segment_width} {0.2*thickness} 0 0 1 0 {1.0*thickness}
                """
            path_data = " ".join(path_data.split())

            svg_path = self.svg.path(style="fill: none; stroke:black; stroke-width:0.18", d=path_data)
            if reverse_x:
                svg_path.update({"transform": f"scale(-1,-1) translate(-{segment_width}, -{thickness})"})

            marker = self.svg.marker(
                markerUnits="userSpaceOnUse",
                insert=(0, thickness / 2),
                size=(segment_width, thickness),
                orient="auto",
                id=marker_id,
            )
            marker.add(svg_path)
            self.svg.add(marker)

            # separate marker for the end of the pattern to truncate it more gracefully
            marker_end = marker.copy()
            marker_end.update({"markerWidth": end_marker_width, "id": marker_end_id})
            self.svg.add(marker_end)

            polyline_style = (
                f"marker-start: url(#{marker_id}); "
                f"marker-mid: url(#{marker_id}); stroke: none; "
                f"marker-end: url(#{marker_end_id}); stroke: none; "
            )
            self.svg.add(self.svg.polyline(points=points, class_=" ".join(classes), style=polyline_style))

        elif predefined_type == "SECTION":
            display_data = DecoratorData.get_section_markers_display_data(obj)
            connect_markers = display_data["connect_markers"]

            if connect_markers:
                for edge in obj.data.edges:
                    draw_simple_edge_annotation(*edge.vertices[:])
            else:
                for edge in obj.data.edges:
                    v0_marker_position = "start" if edge.vertices[0] == 0 else "end"
                    v1_marker_position = "start" if edge.vertices[1] == 0 else "end"

                    v0_global = matrix_world @ obj.data.vertices[edge.vertices[0]].co.xyz
                    v1_global = matrix_world @ obj.data.vertices[edge.vertices[1]].co.xyz
                    v0 = self.project_point_onto_camera(v0_global)
                    v1 = self.project_point_onto_camera(v1_global)
                    start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
                    end = Vector(((x_offset + v1.x), (y_offset - v1.y)))

                    edge_dir = (end - start).normalized()
                    circle_radius = 5
                    segment_size = circle_radius * 3

                    if display_data[v0_marker_position]["add_symbol"]:
                        self.svg.add(
                            self.svg.line(
                                start=start * self.svg_scale,
                                end=start * self.svg_scale + edge_dir * segment_size,
                                class_=" ".join(classes),
                            )
                        )

                    if display_data[v1_marker_position]["add_symbol"]:
                        self.svg.add(
                            self.svg.line(
                                start=end * self.svg_scale,
                                end=end * self.svg_scale - edge_dir * segment_size,
                                class_=" ".join(classes),
                            )
                        )

        else:
            for edge in obj.data.edges:
                draw_simple_edge_annotation(*edge.vertices[:])

    def draw_leader_annotation(self, obj):
        self.draw_line_annotation(obj)
        spline = obj.data.splines[0]
        spline_points = spline.bezier_points if spline.bezier_points else spline.points
        if spline_points:
            position = obj.matrix_world @ spline_points[0].co.xyz
        else:
            position = Vector((0, 0, 0))
        self.draw_text_annotation(obj, position)

    def draw_section_annotation(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        self.draw_line_annotation(obj)

        display_data = DecoratorData.get_section_markers_display_data(obj)

        for edge in obj.data.edges:
            edge_verts = [obj.data.vertices[v_i] for v_i in edge.vertices]

            # convert edge vertiices coordinates to svg space
            # to calculate the edge angle and for later use
            edge_verts_svg = []
            for vert in edge_verts:
                point = obj.matrix_world @ vert.co
                symbol_position = self.project_point_onto_camera(point)
                symbol_position = Vector(((x_offset + symbol_position.x), (y_offset - symbol_position.y)))
                symbol_position_svg = symbol_position * self.svg_scale
                edge_verts_svg.append(symbol_position_svg)

            edge_dir = (edge_verts_svg[1] - edge_verts_svg[0]).normalized()
            angle = degrees(edge_dir.xy.angle_signed(Vector([1, 0])))

            for v_i, symbol_position_svg in zip(edge.vertices, edge_verts_svg):
                current_marker_position = "start" if v_i == 0 else "end"

                # marker arrow symbol
                if display_data[current_marker_position]["add_symbol"]:
                    transform = "rotate({}, {}, {})".format(angle, *symbol_position_svg.xy)
                    symbol_id = display_data[current_marker_position]["symbol"]
                    self.svg.add(self.svg.use(f"#{symbol_id}", insert=symbol_position_svg, transform=transform))

                # marker circle and it's text
                if display_data[current_marker_position]["add_circle"]:
                    self.svg.add(self.svg.use("#section-tag", insert=symbol_position_svg))

                    reference_id, sheet_id = self.get_reference_and_sheet_id_from_annotation(tool.Ifc.get_entity(obj))
                    text_position = symbol_position_svg
                    text_style = {
                        "text-anchor": "middle",
                        "alignment-baseline": "middle",
                        "dominant-baseline": "middle",
                    }
                    self.svg.add(
                        self.svg.text(
                            reference_id,
                            insert=(text_position[0], text_position[1] - 2.5),
                            class_="SECTION",
                            **text_style,
                        )
                    )
                    self.svg.add(
                        self.svg.text(
                            sheet_id, insert=(text_position[0], text_position[1] + 2.5), class_="SECTION", **text_style
                        )
                    )

    def draw_elevation_annotation(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        symbol_position = self.project_point_onto_camera(obj.location)
        symbol_position = Vector(((x_offset + symbol_position.x), (y_offset - symbol_position.y)))
        symbol_position_svg = symbol_position * self.svg_scale

        v1 = self.project_point_onto_camera(obj.matrix_world @ Vector((0, 0, 0)))
        v2 = self.project_point_onto_camera(obj.matrix_world @ Vector((0, 0, -1)))
        angle = -math.degrees((v2 - v1).xy.angle_signed(Vector((0, 1))))

        transform = "rotate({}, {}, {})".format(angle, *symbol_position_svg.xy)

        self.svg.add(self.svg.use("#elevation-arrow", insert=symbol_position_svg, transform=transform))
        self.svg.add(self.svg.use("#elevation-tag", insert=symbol_position_svg))

        reference_id, sheet_id = self.get_reference_and_sheet_id_from_annotation(tool.Ifc.get_entity(obj))
        text_position = symbol_position_svg
        text_style = {
            "text-anchor": "middle",
            "alignment-baseline": "middle",
            "dominant-baseline": "middle",
        }
        self.svg.add(
            self.svg.text(
                reference_id, insert=(text_position[0], text_position[1] - 2.5), class_="ELEVATION", **text_style
            )
        )
        self.svg.add(
            self.svg.text(sheet_id, insert=(text_position[0], text_position[1] + 2.5), class_="ELEVATION", **text_style)
        )

    def get_reference_and_sheet_id_from_annotation(self, element):
        reference_id = "-"
        sheet_id = "-"
        drawing = tool.Drawing.get_annotation_element(element)
        reference = tool.Drawing.get_drawing_reference(drawing)
        if reference:
            sheet = tool.Drawing.get_reference_document(reference)
            if sheet:
                if tool.Ifc.get_schema() == "IFC2X3":
                    reference_id = reference.ItemReference or "-"
                    sheet_id = sheet.DocumentId or "-"
                else:
                    reference_id = reference.Identification or "-"
                    sheet_id = sheet.Identification or "-"
                return (reference_id, sheet_id)
        return ("-", "-")

    def draw_text_annotation(self, text_obj, position):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        element = tool.Ifc.get_entity(text_obj)
        text_literals = tool.Drawing.get_text_literal(text_obj, return_list=True)
        product = tool.Drawing.get_assigned_product(element)

        text_position = self.project_point_onto_camera(position)
        text_position = Vector(((x_offset + text_position.x), (y_offset - text_position.y)))
        text_position_svg = text_position * self.svg_scale

        local_x_axis = text_obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        projected_x_axis = self.project_point_onto_camera(position + local_x_axis)
        angle = math.degrees(
            (Vector((x_offset + projected_x_axis.x, y_offset - projected_x_axis.y)) - text_position).angle_signed(
                Vector((1, 0))
            )
        )

        transform = "rotate({}, {}, {})".format(angle, *text_position_svg)
        classes_str = " ".join(self.get_attribute_classes(text_obj))

        symbol = tool.Drawing.get_annotation_symbol(element)
        template_text_fields = []
        if symbol:
            symbol_svg = self.find_xml_symbol_by_id(symbol)
            if symbol_svg:
                symbol_xml = symbol_svg.get_xml()
                template_text_fields = symbol_xml.findall('.//text[@data-type="text-template"]')
                # if there is a symbol with template text fields
                # then we just populate it's fields with the data from text literals
                if template_text_fields:
                    symbol_xml.attrib["transform"] = f"translate({', '.join(map(str, text_position_svg))})"
                    symbol_xml.attrib.pop("id")
                    # note: zip makes sure that we iterate over the shortest list
                    for field, text_literal in zip(template_text_fields, text_literals):
                        field.text = tool.Drawing.replace_text_literal_variables(text_literal.Literal, product)
                        field.attrib["class"] = classes_str
                    self.svg.add(symbol_svg)
                    return None

            if not symbol_svg or not template_text_fields:
                self.svg.add(self.svg.use(f"#{symbol}", insert=text_position_svg))

        def get_box_alignment_parameters(box_alignment):
            # reference for alignment values:
            # https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/text-anchor
            # https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/alignment-baseline
            vertical_alignment = {
                "top": "hanging",
                "bottom": "baseline",
                "center": "middle",
                "middle": "middle",
            }
            alignment_baseline = vertical_alignment[
                next(align for align in vertical_alignment if align in box_alignment)
            ]
            horizontal_alignment = {
                "left": "start",
                "right": "end",
                "center": "middle",
                "middle": "middle",
            }
            text_anchor = horizontal_alignment[next(align for align in horizontal_alignment if align in box_alignment)]

            # using dominant-baseline because we plan to use <tspan> subtags
            # otherwise alignment-baseline would be sufficient
            return {
                "dominant-baseline": alignment_baseline,
                "text-anchor": text_anchor,
            }

        for text_literal in text_literals:
            # after pretty indentation some redundant spaces can occur in svg tags
            # this is why we apply "font-size: 0;" to the text tag to remove those spaces
            # and add clases to the tspan tags
            # ref: https://github.com/IfcOpenShell/IfcOpenShell/issues/2833#issuecomment-1471584960

            text = tool.Drawing.replace_text_literal_variables(text_literal.Literal, product)
            text_tag = self.svg.text(
                "",
                **{
                    "transform": transform,
                    "style": "font-size: 0;",
                },
                **get_box_alignment_parameters(text_literal.BoxAlignment),
            )
            self.svg.add(text_tag)

            for line_number, text_line in enumerate(text.replace("\\n", "\n").split("\n")):
                # position has to be inserted at tspan to avoid x offset between tspans
                t_span = self.svg.tspan(text_line, class_=classes_str, insert=text_position_svg)
                # doing it here and not in tspan constructor because constructor adds unnecessary spaces
                t_span.update({"dy": f"{line_number}em"})
                text_tag.add(t_span)

    def draw_break_annotations(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        classes = self.get_attribute_classes(obj)
        matrix_world = obj.matrix_world
        for edge in obj.data.edges:
            points = [obj.data.vertices[v] for v in edge.vertices]
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            projected_points = [
                projected_points[0],
                (projected_points[0] + projected_points[1]) / 2,
                projected_points[1],
            ]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))

    def draw_plan_level_annotation(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        classes = self.get_attribute_classes(obj)
        for spline in obj.data.splines:
            points = self.get_spline_points(spline)
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
            text_position = Vector(
                (
                    (x_offset + projected_points[0].x) * self.svg_scale,
                    ((y_offset - projected_points[0].y) * self.svg_scale) - 2.5,
                )
            )
            # TODO: allow metric to be configurable
            rl = ((matrix_world @ points[0].co).xyz + obj.location).z
            if bpy.context.scene.unit_settings.system == "IMPERIAL":
                rl = helper.format_distance(rl)
            else:
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                rl /= unit_scale
                rl = ifcopenshell.util.geolocation.auto_z2e(tool.Ifc.get(), rl)
                rl *= unit_scale
                rl = "{:.3f}m".format(rl)
            if projected_points[0].x > projected_points[-1].x:
                text_anchor = "end"
            else:
                text_anchor = "start"
            self.svg.add(
                self.svg.text(
                    "RL +{}".format(rl),
                    insert=tuple(text_position),
                    class_="PLANLEVEL",
                    **{
                        "text-anchor": text_anchor,
                        "alignment-baseline": "baseline",
                        "dominant-baseline": "baseline",
                    },
                )
            )

    def draw_angle_annotations(self, obj):
        points = obj.data.splines[0].points
        region = bpy.context.region
        region_3d = bpy.context.area.spaces.active.region_3d
        points_chunked = [points[i : i + 3] for i in range(len(points) - 2)]

        for points_chunk in points_chunked:
            points_2d = [view3d_utils.location_3d_to_region_2d(region, region_3d, p.co.xyz) for p in points_chunk]

            edge0 = points_2d[0] - points_2d[1]
            edge1 = points_2d[2] - points_2d[1]
            angle_radius = min(edge0.length, edge1.length)
            dir0 = edge0.normalized()
            dir1 = edge1.normalized()
            dir2 = ((dir0 + dir1) / 2).normalized()

            # calculate p3 which is the center of the arc
            # to use draw_svg_3point_arc()
            p3 = points_2d[1] + dir2 * angle_radius

            # make all edges the same radius
            p0 = points_2d[1] + dir0 * angle_radius
            p2 = points_2d[1] + dir1 * angle_radius
            points_chunk = [view3d_utils.region_2d_to_origin_3d(region, region_3d, p) for p in [p0, p3, p2]]
            # points = [p.co.xyz for p in bpy.context.object.data.splines[0].points[:3]]

            bm = bmesh.new()
            bm.verts.index_update()
            bm.edges.index_update()
            new_verts = [bm.verts.new(p) for p in points_chunk]
            new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in ((0, 1), (1, 2))]
            self.draw_svg_3point_arc(obj, bm)

    def draw_svg_3point_arc(self, obj, bm):
        # This implementation uses an SVG arc, which means that it can only draw
        # arcs that are orthogonal to the view (e.g. not arcs in 3D).
        # Gosh this is bad code :(

        points = [v.co for v in bm.verts][:3]
        center = tool.Cad.get_center_of_arc(points, obj)
        classes = self.get_attribute_classes(obj)
        matrix_world = obj.matrix_world
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        bm.verts.ensure_lookup_table()
        arc_end_verts = [v for v in bm.verts if len(v.link_edges) == 1]
        arc_end_pts = [matrix_world @ v.co for v in arc_end_verts]

        # Probably need this when rewriting to use an SVG polyline instead of an arc
        # arc_path = [arc_end_verts[0]]
        # while True:
        #    last_point = arc_end_verts[0]
        #    found_another_point = False
        #    for edge in last_point.link_edges:
        #        v = edge.other_vert(last_point)
        #        if v not in arc_path:
        #            found_another_point = True
        #            arc_path.append(v)
        #    if not found_another_point:
        #        break

        distance_between_end_verts = (arc_end_verts[0].co - arc_end_verts[1].co).length
        arc_mid_vert = arc_end_verts[0].link_edges[0].other_vert(arc_end_verts[0])
        is_reflex = 0 if (arc_mid_vert.co - arc_end_verts[1].co).length < distance_between_end_verts else 1

        bm.free()

        # Calculate the angle
        # This is the true normal in 3D, whereas the camera projection we use is the drawing direction.
        # This assumes (because we use SVG arcs) that the radius is always orthogonal to our view.
        # When rewriting to use polylines, we should use this normal instead.
        # normal = mathutils.geometry.normal([arc_end_pts[0], arc_end_pts[1], center])
        normal = Vector(self.camera_projection)
        dir1 = (arc_end_pts[0] - center).normalized()
        dir2 = (arc_end_pts[1] - center).normalized()

        # Let's get the matrix that represents the coordinate system of the arc.
        # This matrix allows us to get 2D vectors for calculating the signed arc angle.
        z = normal
        x = (arc_end_pts[0] - center).normalized()
        y = z.cross(x)
        arc_matrix = mathutils.Matrix([x, y, z]).transposed().to_4x4()

        dir1 = ((arc_matrix.inverted() @ arc_end_pts[0]) - (arc_matrix.inverted() @ center)).normalized()
        dir2 = ((arc_matrix.inverted() @ arc_end_pts[1]) - (arc_matrix.inverted() @ center)).normalized()
        angle = -dir1.xy.angle_signed(dir2.xy)

        # if is_reflex:
        #    angle = angle % (math.pi * 2)

        # Center of gravity of all vertices, used to help position the text
        cog = Vector((0, 0, 0))
        for point in points:
            cog += point
        cog = matrix_world @ (cog / len(points))

        radius = ((matrix_world @ points[0]) - center).length

        arc_midpoint = center + ((cog - center).normalized() * radius)

        text_position = self.project_point_onto_camera(arc_midpoint)
        text_position = Vector(
            ((x_offset + text_position.x) * self.svg_scale, (y_offset - text_position.y) * self.svg_scale)
        )

        center_projected = self.project_point_onto_camera(center)
        center_position = Vector(
            ((x_offset + center_projected.x) * self.svg_scale, (y_offset - center_projected.y) * self.svg_scale)
        )
        text_offset = (text_position - center_position).xy.normalized() * 5
        text_position += text_offset

        text_style = {
            "text-anchor": "middle",
            "alignment-baseline": "middle",
            "dominant-baseline": "middle",
        }

        angle_text = abs(round(math.degrees(angle), 3))
        if is_reflex:
            angle_text = 360 - angle_text
        self.svg.add(self.svg.text(f"{angle_text}deg", insert=tuple(text_position), class_="ANGLE", **text_style))

        # Draw SVG arc, see for details: http://xahlee.info/js/svg_circle_arc.html
        arc_proj_end_pts = [self.project_point_onto_camera(v) for v in arc_end_pts]
        p1 = Vector(
            ((x_offset + arc_proj_end_pts[0].x) * self.svg_scale, (y_offset - arc_proj_end_pts[0].y) * self.svg_scale)
        )
        p2 = Vector(
            ((x_offset + arc_proj_end_pts[1].x) * self.svg_scale, (y_offset - arc_proj_end_pts[1].y) * self.svg_scale)
        )
        r = radius * self.svg_scale
        # reflex = 1 if angle > math.pi else 0
        reflex = is_reflex
        if reflex:
            sense = 0 if angle > 0 else 1
        else:
            sense = 1 if angle > 0 else 0
        d = f"M {p1.x} {p1.y} A {r} {r} 0 {reflex} {sense} {p2.x} {p2.y}"
        path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))

    def draw_radius_annotations(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        classes = self.get_attribute_classes(obj)
        element = tool.Ifc.get_entity(obj)
        matrix_world = obj.matrix_world
        for spline in obj.data.splines:
            points = self.get_spline_points(spline)
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))

            p0 = Vector(
                (
                    (x_offset + projected_points[0].x) * self.svg_scale,
                    (y_offset - projected_points[0].y) * self.svg_scale,
                )
            )
            p1 = Vector(
                (
                    (x_offset + projected_points[1].x) * self.svg_scale,
                    (y_offset - projected_points[1].y) * self.svg_scale,
                )
            )
            text_offset = (p0 - p1).xy.normalized() * 5
            text_position = projected_points[0]
            text_position = Vector(
                ((x_offset + text_position.x) * self.svg_scale, (y_offset - text_position.y) * self.svg_scale)
            )
            text_position += text_offset

            text_style = {
                "text-anchor": "middle",
                "alignment-baseline": "middle",
                "dominant-baseline": "middle",
            }

            radius = (points[-1].co - points[-2].co).length
            radius = helper.format_distance(radius)
            tag = element.Description or f"R{radius}"

            self.svg.add(self.svg.text(tag, insert=tuple(text_position), class_="RADIUS", **text_style))

    def draw_fall_annotations(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        classes = self.get_attribute_classes(obj)
        element = tool.Ifc.get_entity(obj)
        matrix_world = obj.matrix_world
        for spline in obj.data.splines:
            points = self.get_spline_points(spline)
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.svg_scale, (y_offset - p.y) * self.svg_scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))

            p0 = Vector(
                (
                    (x_offset + projected_points[0].x) * self.svg_scale,
                    (y_offset - projected_points[0].y) * self.svg_scale,
                )
            )
            p1 = Vector(
                (
                    (x_offset + projected_points[1].x) * self.svg_scale,
                    (y_offset - projected_points[1].y) * self.svg_scale,
                )
            )

            # generate label text
            # same function as in decoration.py
            def get_label_text():
                B, A = [v.co.xyz for v in points[:2]]
                rise = abs(A.z - B.z)
                O = A.copy()
                O.z = B.z
                run = (B - O).length
                if run != 0:
                    angle_tg = rise / run
                    angle = round(degrees(atan(angle_tg)))
                else:
                    angle = 90

                # ues SLOPE_ANGLE as default
                if element.ObjectType in ("FALL", "SLOPE_ANGLE"):
                    return f"{angle}°"
                elif element.ObjectType == "SLOPE_FRACTION":
                    if angle == 90:
                        return "-"
                    return f"{helper.format_distance(rise)} / {helper.format_distance(run)}"
                elif element.ObjectType == "SLOPE_PERCENT":
                    if angle == 90:
                        return "-"
                    return f"{round(angle_tg * 100)} %"

            tag = element.Description or get_label_text()

            text_offset = (p0 - p1).xy.normalized() * len(tag)
            text_position = projected_points[0]
            text_position = Vector(
                ((x_offset + text_position.x) * self.svg_scale, (y_offset - text_position.y) * self.svg_scale)
            )
            text_position += text_offset

            text_style = {
                "text-anchor": "middle",
                "alignment-baseline": "middle",
                "dominant-baseline": "middle",
            }

            self.svg.add(self.svg.text(tag, insert=tuple(text_position), class_="RADIUS", **text_style))

    def draw_diameter_annotations(self, obj):
        classes = self.get_attribute_classes(obj)
        matrix_world = obj.matrix_world
        element = tool.Ifc.get_entity(obj)
        text_override = element.Description
        for spline in obj.data.splines:
            points = self.get_spline_points(spline)
            for i, p in enumerate(points):
                if i + 1 >= len(points):
                    continue
                v0_global = matrix_world @ points[i].co.xyz
                v1_global = matrix_world @ points[i + 1].co.xyz
                self.draw_dimension_annotation(
                    v0_global, v1_global, classes, text_override, text_format=lambda x: "D" + x
                )

    def draw_dimension_annotations(self, obj):
        classes = self.get_attribute_classes(obj)
        matrix_world = obj.matrix_world
        element = tool.Ifc.get_entity(obj)
        text_override = element.Description
        for spline in obj.data.splines:
            points = self.get_spline_points(spline)
            for i, p in enumerate(points):
                if i + 1 >= len(points):
                    continue
                v0_global = matrix_world @ points[i].co.xyz
                v1_global = matrix_world @ points[i + 1].co.xyz
                self.draw_dimension_annotation(v0_global, v1_global, classes, text_override)

    def draw_measureit_arch_dimension_annotations(self):
        try:
            import MeasureIt_ARCH.measureit_arch_external_utils

            coords = MeasureIt_ARCH.measureit_arch_external_utils.blenderBIM_get_coords(bpy.context)
        except:
            return
        for coord in coords:
            self.draw_dimension_annotation(
                Vector(coord[0]), Vector(coord[1]), ["IfcAnnotation", "PredefinedType-DIMENSION"]
            )

    def draw_dimension_annotation(self, v0_global, v1_global, classes, text_override=None, text_format=lambda x: x):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        v0 = self.project_point_onto_camera(v0_global)
        v1 = self.project_point_onto_camera(v1_global)
        start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
        end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
        mid = ((end - start) / 2) + start
        vector = end - start
        perpendicular = Vector((vector.y, -vector.x)).normalized()
        dimension = (v1_global - v0_global).length
        dimension = helper.format_distance(dimension)
        sheet_dimension = ((end * self.svg_scale) - (start * self.svg_scale)).length
        if sheet_dimension < 5:  # annotation can't fit
            # offset text to right of marker
            text_position = (end * self.svg_scale) + perpendicular + (3 * vector.normalized())
        else:
            text_position = (mid * self.svg_scale) + perpendicular
        rotation = math.degrees(vector.angle_signed(Vector((1, 0))))
        line = self.svg.add(
            self.svg.line(
                start=tuple(start * self.svg_scale), end=tuple(end * self.svg_scale), class_=" ".join(classes)
            )
        )
        if text_override is not None:
            text = text_override
        else:
            text = str(dimension)
        text = text_format(text)
        self.svg.add(
            self.svg.text(
                text,
                insert=tuple(text_position),
                class_="DIMENSION",
                **{
                    "transform": "rotate({} {} {})".format(rotation, text_position.x, text_position.y),
                    "text-anchor": "middle",
                },
            )
        )

    def project_point_onto_camera(self, point):
        # TODO is this needlessly complex?
        return self.camera.matrix_world.inverted() @ geometry.intersect_line_plane(
            point.xyz,
            point.xyz - Vector(self.camera_projection),
            self.camera.location,
            Vector(self.camera_projection),
        )

    def get_spline_points(self, spline):
        return spline.bezier_points if spline.bezier_points else spline.points

    def draw_polygon(self, polygon, position):
        points = [(p[0] * self.svg_scale, p[1] * self.svg_scale) for p in polygon["points"]]
        if "classes" in polygon["metadata"]:
            classes = " ".join(polygon["metadata"]["classes"])
        else:
            classes = ""
        self.svg.add(self.svg.polygon(points=points, class_=classes))
