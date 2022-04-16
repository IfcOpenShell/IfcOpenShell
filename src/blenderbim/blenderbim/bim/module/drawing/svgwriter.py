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
import pystache
import xml.etree.ElementTree as ET
import svgwrite
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.bim.module.drawing.helper as helper
import blenderbim.bim.module.drawing.annotation as annotation
from mathutils import Vector
from mathutils import geometry
from blenderbim.bim.ifc import IfcStore


def load_occ():
    # Don't import until we really need to, as a temporary step before we can purge OCC
    try:
        from OCC.Core import BRep, BRepTools, TopExp, TopAbs
    except ImportError:
        from OCC import BRep, BRepTools, TopExp, TopAbs


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
        self.output = "out.svg"
        self.data_dir = None
        self.vector_style = None
        self.human_scale = "NTS"
        self.annotations = {}
        self.background_image = None
        self.scale = 1 / 100  # 1:100

    def write(self, layer):
        self.calculate_scale()
        self.svg = svgwrite.Drawing(
            self.output,
            debug=False,
            size=("{}mm".format(self.width), "{}mm".format(self.height)),
            viewBox=("0 0 {} {}".format(self.width, self.height)),
            id="root",
            data_scale=self.human_scale,
        )

        if layer == "underlay":
            self.draw_background_image()
        elif layer == "annotation":
            self.add_stylesheet()
            self.add_markers()
            self.add_symbols()
            self.add_patterns()
            # self.draw_background_elements()
            # self.draw_cut_polygons()
            self.draw_annotations()
        self.svg.save(pretty=True)

    def calculate_scale(self):
        self.scale *= 1000  # IFC is in meters, SVG is in mm
        self.raw_width = self.camera_width
        self.raw_height = self.camera_height
        self.width = self.raw_width * self.scale
        self.height = self.raw_height * self.scale

    def add_stylesheet(self):
        with open(os.path.join(self.data_dir, "styles", f"{self.vector_style}.css"), "r") as stylesheet:
            self.svg.defs.add(self.svg.style(stylesheet.read()))

    def add_markers(self):
        tree = ET.parse(os.path.join(self.data_dir, "templates", "markers.svg"))
        root = tree.getroot()
        for child in root:
            self.svg.defs.add(External(child))

    def add_symbols(self):
        tree = ET.parse(os.path.join(self.data_dir, "templates", "symbols.svg"))
        root = tree.getroot()
        for child in root:
            self.svg.defs.add(External(child))

    def add_patterns(self):
        tree = ET.parse(os.path.join(self.data_dir, "templates", "patterns.svg"))
        root = tree.getroot()
        for child in root:
            self.svg.defs.add(External(child))

    def draw_background_image(self):
        self.svg.add(
            self.svg.image(
                os.path.join("..", "diagrams", os.path.basename(self.background_image)),
                **{"width": self.width, "height": self.height},
            )
        )

    def draw_background_elements(self):
        return  # TODO purge?
        for element in self.ifc_cutter.background_elements:
            if element["type"] == "polygon":
                self.draw_polygon(element, "background")
            elif element["type"] == "polyline":
                self.draw_polyline(element, "background")
            elif element["type"] == "line":
                self.draw_line(element, "background")

    def draw_annotations(self):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        for obj in self.annotations.get("equal_objs", []):
            self.draw_dimension_annotations(obj, text_override="EQ")
        for obj in self.annotations.get("dimension_objs", []):
            self.draw_dimension_annotations(obj)
        self.draw_measureit_arch_dimension_annotations()

        if self.annotations.get("break_obj"):
            self.draw_break_annotations(self.annotations["break_obj"])

        for grid_obj in self.annotations.get("grid_objs", []):
            matrix_world = grid_obj.matrix_world
            classes = self.get_attribute_classes(grid_obj)
            for edge in grid_obj.data.edges:
                v0_global = matrix_world @ grid_obj.data.vertices[edge.vertices[0]].co.xyz
                v1_global = matrix_world @ grid_obj.data.vertices[edge.vertices[1]].co.xyz
                v0 = self.project_point_onto_camera(v0_global)
                v1 = self.project_point_onto_camera(v1_global)
                start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
                end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
                vector = end - start
                line = self.svg.add(
                    self.svg.line(
                        start=tuple(start * self.scale), end=tuple(end * self.scale), class_=" ".join(classes)
                    )
                )
                line["stroke-dasharray"] = "12.5, 3, 3, 3"
                axis_tag = tool.Ifc.get_entity(grid_obj).Name
                self.svg.add(
                    self.svg.text(
                        axis_tag,
                        insert=tuple(start * self.scale),
                        **{
                            "font-size": annotation.Annotator.get_svg_text_size(5.0),
                            "font-family": "OpenGost Type B TT",
                            "text-anchor": "middle",
                            "alignment-baseline": "middle",
                            "dominant-baseline": "middle",
                        },
                    )
                )
                self.svg.add(
                    self.svg.text(
                        axis_tag,
                        insert=tuple(end * self.scale),
                        **{
                            "font-size": annotation.Annotator.get_svg_text_size(5.0),
                            "font-family": "OpenGost Type B TT",
                            "text-anchor": "middle",
                            "alignment-baseline": "middle",
                            "dominant-baseline": "middle",
                        },
                    )
                )

        self.draw_ifc_annotation()

        for obj in self.annotations.get("misc_objs", []):
            self.draw_misc_annotation(obj)

        for obj_data in self.annotations.get("hidden_objs", []):
            self.draw_line_annotation(obj_data)

        for obj_data in self.annotations.get("solid_objs", []):
            self.draw_line_annotation(obj_data)

        self.draw_leader_annotations()

        for obj in self.annotations.get("plan_level_objs", []):
            self.draw_plan_level_annotation(obj)

        if self.annotations.get("section_level_obj"):
            matrix_world = self.annotations["section_level_obj"].matrix_world
            classes = self.get_attribute_classes(self.annotations["section_level_obj"])
            for spline in self.annotations["section_level_obj"].data.splines:
                points = self.get_spline_points(spline)
                projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
                d = " ".join(
                    [
                        "L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                        for p in projected_points
                    ]
                )
                d = "M{}".format(d[1:])
                path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
                text_position = Vector(
                    (
                        (x_offset + projected_points[0].x) * self.scale,
                        ((y_offset - projected_points[0].y) * self.scale) - 3.5,
                    )
                )
                # TODO: allow metric to be configurable
                rl = (matrix_world @ points[0].co.xyz).z
                if bpy.context.scene.unit_settings.system == "IMPERIAL":
                    rl = helper.format_distance(rl)
                else:
                    rl = "{:.3f}m".format(rl)
                self.svg.add(
                    self.svg.text(
                        "RL +{}".format(rl),
                        insert=tuple(text_position),
                        **{
                            "font-size": annotation.Annotator.get_svg_text_size(2.5),
                            "font-family": "OpenGost Type B TT",
                            "text-anchor": "start",
                            "alignment-baseline": "baseline",
                            "dominant-baseline": "baseline",
                        },
                    )
                )

        if self.annotations.get("stair_obj"):
            matrix_world = self.annotations["stair_obj"].matrix_world
            classes = self.get_attribute_classes(self.annotations["stair_obj"])
            for spline in self.annotations["stair_obj"].data.splines:
                points = self.get_spline_points(spline)
                projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
                d = " ".join(
                    [
                        "L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                        for p in projected_points
                    ]
                )
                d = "M{}".format(d[1:])
                start = Vector(((x_offset + projected_points[0].x), (y_offset - projected_points[0].y)))
                next_point = Vector(((x_offset + projected_points[1].x), (y_offset - projected_points[1].y)))
                text_position = (start * self.scale) - ((next_point - start).normalized() * 5)
                path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
                self.svg.add(
                    self.svg.text(
                        "UP",
                        insert=tuple(text_position),
                        **{
                            "font-size": annotation.Annotator.get_svg_text_size(2.5),
                            "font-family": "OpenGost Type B TT",
                            "text-anchor": "middle",
                            "alignment-baseline": "middle",
                            "dominant-baseline": "middle",
                        },
                    )
                )

        for obj in self.annotations.get("elevation_objs", []):
            self.draw_elevation_annotation(obj)

        for obj in self.annotations.get("section_objs", []):
            self.draw_section_annotation(obj)

        for text_obj in self.annotations.get("text_objs", []):
            self.draw_text_annotation(text_obj, text_obj.location)

    def draw_ifc_annotation(self):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        for annotation in self.annotations.get("annotation_objs", []):
            for edge in annotation["edges"]:
                v0_global = annotation["vertices"][edge[0]]
                v1_global = annotation["vertices"][edge[1]]
                v0 = self.project_point_onto_camera(v0_global)
                v1 = self.project_point_onto_camera(v1_global)
                start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
                end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
                vector = end - start
                line = self.svg.add(
                    self.svg.line(
                        start=tuple(start * self.scale),
                        end=tuple(end * self.scale),
                        class_=" ".join(annotation["classes"]),
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
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        for polygon in obj.data.polygons:
            points = [obj.data.vertices[v] for v in polygon.vertices]
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            projected_points.append(projected_points[0])
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
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
        for attribute in self.annotations.get("attributes", []):
            result = self.get_obj_value(obj, attribute)
            if result:
                classes.append(
                    "{}-{}".format(re.sub("[^0-9a-zA-Z]+", "", attribute), re.sub("[^0-9a-zA-Z]+", "", result))
                )
        return classes

    def canonicalise_class_name(self, name):
        return re.sub("[^0-9a-zA-Z]+", "", name)

    def get_obj_value(self, obj, key):
        # This is a duplicate implementation of the IFC selector key in Blender
        # In the future if all this becomes purely IFC based this can be deleted
        if "." in key and key.split(".")[0] == "type":
            try:
                obj = obj.BIMObjectProperties.relating_type
            except:
                return
            key = ".".join(key.split(".")[1:])
        result = obj.BIMObjectProperties.attributes.get(key)
        if result:
            return result.string_value
        elif key == "Name":
            return obj.name.split("/")[1]
        elif "." in key:
            pset_name, prop = key.split(".")
            pset = obj.BIMObjectProperties.psets.get(pset_name)
            if not pset:
                pset = obj.BIMObjectProperties.qtos.get(pset_name)
            if not pset:
                return
            result = pset.properties.get(prop)
            if result:
                return result.string_value

    def draw_line_annotation(self, obj_data):
        # TODO: properly scope these offsets
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        obj, data = obj_data

        classes = self.get_attribute_classes(obj)
        matrix_world = obj.matrix_world

        if isinstance(data, bpy.types.Curve):
            for spline in data.splines:
                points = self.get_spline_points(spline)
                projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
                d = " ".join(
                    [
                        "L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                        for p in projected_points
                    ]
                )
                d = "M{}".format(d[1:])
                path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
        elif isinstance(data, bpy.types.Mesh):
            self.draw_edge_annotation(obj, classes)

    def draw_edge_annotation(self, obj, classes):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        for edge in obj.data.edges:
            v0_global = matrix_world @ obj.data.vertices[edge.vertices[0]].co.xyz
            v1_global = matrix_world @ obj.data.vertices[edge.vertices[1]].co.xyz
            v0 = self.project_point_onto_camera(v0_global)
            v1 = self.project_point_onto_camera(v1_global)
            start = Vector(((x_offset + v0.x), (y_offset - v0.y)))
            end = Vector(((x_offset + v1.x), (y_offset - v1.y)))
            vector = end - start
            line = self.svg.add(
                self.svg.line(start=tuple(start * self.scale), end=tuple(end * self.scale), class_=" ".join(classes))
            )

    def draw_leader_annotations(self):
        for obj in self.annotations.get("leader_objs", []):
            self.draw_line_annotation((obj, obj.data))
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

        self.draw_line_annotation((obj, obj.data))

        v1 = self.project_point_onto_camera(obj.matrix_world @ Vector((0, 0, 0)))
        v2 = self.project_point_onto_camera(obj.matrix_world @ Vector((0, 0, -1)))
        angle = -math.degrees((v2 - v1).xy.angle_signed(Vector((0, 1))))

        for vert in obj.data.vertices:
            point = obj.matrix_world @ vert.co
            symbol_position = self.project_point_onto_camera(point)
            symbol_position = Vector(((x_offset + symbol_position.x), (y_offset - symbol_position.y)))
            transform = "rotate({}, {}, {})".format(
                angle,
                (symbol_position * self.scale)[0],
                (symbol_position * self.scale)[1],
            )

            self.svg.add(
                self.svg.use("#section-arrow", insert=tuple(symbol_position * self.scale), transform=transform)
            )
            self.svg.add(self.svg.use("#section-tag", insert=tuple(symbol_position * self.scale)))

            reference_id, sheet_id = self.get_reference_and_sheet_id_from_annotation(tool.Ifc.get_entity(obj))
            text_position = list(symbol_position * self.scale)
            text_style = {
                "font-size": annotation.Annotator.get_svg_text_size(2.5),
                "font-family": "OpenGost Type B TT",
                "text-anchor": "middle",
                "alignment-baseline": "middle",
                "dominant-baseline": "middle",
            }
            self.svg.add(self.svg.text(reference_id, insert=(text_position[0], text_position[1] - 2.5), **text_style))
            self.svg.add(self.svg.text(sheet_id, insert=(text_position[0], text_position[1] + 2.5), **text_style))

    def draw_elevation_annotation(self, obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        symbol_position = self.project_point_onto_camera(obj.location)
        symbol_position = Vector(((x_offset + symbol_position.x), (y_offset - symbol_position.y)))

        v1 = self.project_point_onto_camera(obj.matrix_world @ Vector((0, 0, 0)))
        v2 = self.project_point_onto_camera(obj.matrix_world @ Vector((0, 0, -1)))
        angle = -math.degrees((v2 - v1).xy.angle_signed(Vector((0, 1))))

        transform = "rotate({}, {}, {})".format(
            angle,
            (symbol_position * self.scale)[0],
            (symbol_position * self.scale)[1],
        )

        self.svg.add(self.svg.use("#elevation-arrow", insert=tuple(symbol_position * self.scale), transform=transform))
        self.svg.add(self.svg.use("#elevation-tag", insert=tuple(symbol_position * self.scale)))

        reference_id, sheet_id = self.get_reference_and_sheet_id_from_annotation(tool.Ifc.get_entity(obj))
        text_position = list(symbol_position * self.scale)
        text_style = {
            "font-size": annotation.Annotator.get_svg_text_size(2.5),
            "font-family": "OpenGost Type B TT",
            "text-anchor": "middle",
            "alignment-baseline": "middle",
            "dominant-baseline": "middle",
        }
        self.svg.add(self.svg.text(reference_id, insert=(text_position[0], text_position[1] - 2.5), **text_style))
        self.svg.add(self.svg.text(sheet_id, insert=(text_position[0], text_position[1] + 2.5), **text_style))

    def get_reference_and_sheet_id_from_annotation(self, element):
        reference_id = "-"
        sheet_id = "-"
        drawing = tool.Drawing.get_annotation_element(element)
        reference = tool.Drawing.get_drawing_reference(drawing)
        if reference:
            sheet = tool.Drawing.get_reference_sheet(reference)
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
        rep = ifcopenshell.util.representation.get_representation(element, "Plan", "Annotation")
        text_literal = [i for i in rep.Items if i.is_a("IfcTextLiteral")][0]

        text_position = self.project_point_onto_camera(position)
        text_position = Vector(((x_offset + text_position.x), (y_offset - text_position.y)))

        local_x_axis = text_obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        projected_x_axis = self.project_point_onto_camera(position + local_x_axis)
        angle = math.degrees(
            (Vector((x_offset + projected_x_axis.x, y_offset - projected_x_axis.y)) - text_position).angle_signed(
                Vector((1, 0))
            )
        )

        transform = "rotate({}, {}, {})".format(
            angle,
            (text_position * self.scale)[0],
            (text_position * self.scale)[1],
        )

        if text_obj.BIMTextProperties.symbol != "None":
            self.svg.add(
                self.svg.use(f"#{text_obj.BIMTextProperties.symbol}", insert=tuple(text_position * self.scale))
            )

        if text_literal.BoxAlignment == "top-left":
            alignment_baseline = "hanging"
            text_anchor = "start"
        elif text_literal.BoxAlignment == "top-middle":
            alignment_baseline = "hanging"
            text_anchor = "middle"
        elif text_literal.BoxAlignment == "top-right":
            alignment_baseline = "hanging"
            text_anchor = "end"
        elif text_literal.BoxAlignment == "middle-left":
            alignment_baseline = "middle"
            text_anchor = "start"
        elif text_literal.BoxAlignment == "center":
            alignment_baseline = "middle"
            text_anchor = "middle"
        elif text_literal.BoxAlignment == "middle-right":
            alignment_baseline = "middle"
            text_anchor = "end"
        elif text_literal.BoxAlignment == "bottom-left":
            alignment_baseline = "baseline"
            text_anchor = "start"
        elif text_literal.BoxAlignment == "bottom-middle":
            alignment_baseline = "baseline"
            text_anchor = "middle"
        elif text_literal.BoxAlignment == "bottom-right":
            alignment_baseline = "baseline"
            text_anchor = "end"

        literal = text_literal.Literal

        product = tool.Drawing.get_text_product(element)
        selector = ifcopenshell.util.selector.Selector
        variables = {}
        for variable in re.findall("{{.*?}}", literal):
            literal = literal.replace(variable, selector.get_element_value(product, variable[2:-2]) or "")

        for line_number, text_line in enumerate(literal.replace("\\n", "\n").split("\n")):
            self.svg.add(
                self.svg.text(
                    text_line,
                    insert=tuple((text_position * self.scale) + Vector((0, 3.5 * line_number))),
                    class_=" ".join(self.get_attribute_classes(text_obj)),
                    **{
                        "font-size": annotation.Annotator.get_svg_text_size(text_obj.BIMTextProperties.font_size),
                        "font-family": "OpenGost Type B TT",
                        "text-anchor": text_anchor,
                        "alignment-baseline": alignment_baseline,
                        "dominant-baseline": alignment_baseline,
                        "transform": transform,
                    },
                )
            )

    def draw_break_annotations(self, break_obj):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        matrix_world = break_obj.matrix_world
        for polygon in break_obj.data.polygons:
            points = [break_obj.data.vertices[v] for v in polygon.vertices]
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(["break"])))

            break_points = [
                projected_points[0],
                ((projected_points[1] - projected_points[0]) / 2) + projected_points[0],
                projected_points[1],
            ]
            d = " ".join(
                ["L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale) for p in break_points]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(["breakline"])))

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
                    "L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))
            text_position = Vector(
                (
                    (x_offset + projected_points[0].x) * self.scale,
                    ((y_offset - projected_points[0].y) * self.scale) - 2.5,
                )
            )
            # TODO: allow metric to be configurable
            rl = ((matrix_world @ points[0].co).xyz + obj.location).z
            if bpy.context.scene.unit_settings.system == "IMPERIAL":
                rl = helper.format_distance(rl)
            else:
                rl = "{:.3f}m".format(rl)
            if projected_points[0].x > projected_points[-1].x:
                text_anchor = "end"
            else:
                text_anchor = "start"
            self.svg.add(
                self.svg.text(
                    "RL +{}".format(rl),
                    insert=tuple(text_position),
                    **{
                        "font-size": annotation.Annotator.get_svg_text_size(2.5),
                        "font-family": "OpenGost Type B TT",
                        "text-anchor": text_anchor,
                        "alignment-baseline": "baseline",
                        "dominant-baseline": "baseline",
                    },
                )
            )

    def draw_dimension_annotations(self, dimension_obj, text_override=None):
        classes = self.get_attribute_classes(dimension_obj)
        matrix_world = dimension_obj.matrix_world
        for spline in dimension_obj.data.splines:
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

    def draw_dimension_annotation(self, v0_global, v1_global, classes, text_override=None):
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
        sheet_dimension = ((end * self.scale) - (start * self.scale)).length
        if sheet_dimension < 5:  # annotation can't fit
            # offset text to right of marker
            text_position = (end * self.scale) + perpendicular + (3 * vector.normalized())
        else:
            text_position = (mid * self.scale) + perpendicular
        rotation = math.degrees(vector.angle_signed(Vector((1, 0))))
        line = self.svg.add(
            self.svg.line(start=tuple(start * self.scale), end=tuple(end * self.scale), class_=" ".join(classes))
        )
        if text_override is not None:
            text = text_override
        else:
            text = str(dimension)
        self.svg.add(
            self.svg.text(
                text,
                insert=tuple(text_position),
                **{
                    "transform": "rotate({} {} {})".format(rotation, text_position.x, text_position.y),
                    "font-size": annotation.Annotator.get_svg_text_size(2.5),
                    "font-family": "OpenGost Type B TT",
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

    def draw_cut_polygons(self):
        return  # deprecate?
        for polygon in self.ifc_cutter.cut_polygons:
            self.draw_polygon(polygon, "cut")

    def draw_polyline(self, element, position):
        load_occ()
        classes = self.get_classes(element["raw"], position)
        exp = BRepTools.BRepTools_WireExplorer(element["geometry"])
        points = []
        while exp.More():
            point = BRep.BRep_Tool.Pnt(exp.CurrentVertex())
            points.append((point.X() * self.scale, -point.Y() * self.scale))
            exp.Next()
        self.svg.add(self.svg.polyline(points=points, class_=" ".join(classes)))

    def draw_line(self, element, position):
        load_occ()
        classes = self.get_classes(element["raw"], position)
        exp = TopExp.TopExp_Explorer(element["geometry"], TopAbs.TopAbs_VERTEX)
        points = []
        while exp.More():
            point = BRep.BRep_Tool.Pnt(topods.Vertex(exp.Current()))
            points.append((point.X() * self.scale, -point.Y() * self.scale))
            exp.Next()
        self.svg.add(self.svg.line(start=points[0], end=points[1], class_=" ".join(classes)))

    def draw_polygon(self, polygon, position):
        points = [(p[0] * self.scale, p[1] * self.scale) for p in polygon["points"]]
        if "classes" in polygon["metadata"]:
            classes = " ".join(polygon["metadata"]["classes"])
        else:
            classes = ""
        self.svg.add(self.svg.polygon(points=points, class_=classes))
