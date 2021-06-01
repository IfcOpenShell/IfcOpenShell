import os
import re
import bpy
import math
import pystache
import xml.etree.ElementTree as ET
import svgwrite
import ifcopenshell
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
        ns = u"{http://www.w3.org/2000/svg}"
        nsl = len(ns)
        for elem in self.xml.getiterator():
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
        for child in root.getchildren():
            self.svg.defs.add(External(child))

    def add_symbols(self):
        tree = ET.parse(os.path.join(self.data_dir, "templates", "symbols.svg"))
        root = tree.getroot()
        for child in root.getchildren():
            self.svg.defs.add(External(child))

    def add_patterns(self):
        tree = ET.parse(os.path.join(self.data_dir, "templates", "patterns.svg"))
        root = tree.getroot()
        for child in root.getchildren():
            self.svg.defs.add(External(child))

    def draw_background_image(self):
        self.svg.add(
            self.svg.image(
                os.path.join("..", "diagrams", os.path.basename(self.background_image)),
                **{"width": self.width, "height": self.height}
            )
        )

    def draw_background_elements(self):
        return # TODO purge?
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
            for edge in grid_obj.data.edges:
                classes = ["annotation", "grid"]
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
                line["marker-start"] = "url(#grid-marker)"
                line["marker-end"] = "url(#grid-marker)"
                line["stroke-dasharray"] = "12.5, 3, 3, 3"
                axis_tag = IfcStore.get_file().by_id(grid_obj.BIMObjectProperties.ifc_definition_id).AxisTag
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
                        }
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
                        }
                    )
                )

        self.draw_ifc_annotation()

        for obj in self.annotations.get("misc_objs", []):
            self.draw_misc_annotation(obj, ["IfcAnnotation"])

        for obj_data in self.annotations.get("hidden_objs", []):
            self.draw_line_annotation(obj_data, ["hidden"])

        for obj_data in self.annotations.get("solid_objs", []):
            self.draw_line_annotation(obj_data, ["solid"])

        if self.annotations.get("leader_obj"):
            self.draw_line_annotation(self.annotations["leader_obj"], ["leader"])

        if self.annotations.get("plan_level_obj"):
            matrix_world = self.annotations["plan_level_obj"].matrix_world
            for spline in self.annotations["plan_level_obj"].data.splines:
                classes = ["annotation", "plan-level"]
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
                path["marker-end"] = "url(#plan-level-marker)"
                text_position = Vector(
                    (
                        (x_offset + projected_points[0].x) * self.scale,
                        ((y_offset - projected_points[0].y) * self.scale) - 2.5,
                    )
                )
                # TODO: allow metric to be configurable
                rl = ((matrix_world @ points[0].co).xyz + self.annotations["plan_level_obj"].location).z
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
                        }
                    )
                )

        if self.annotations.get("section_level_obj"):
            matrix_world = self.annotations["section_level_obj"].matrix_world
            for spline in self.annotations["section_level_obj"].data.splines:
                classes = ["annotation", "section-level"]
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
                path["marker-start"] = "url(#section-level-marker)"
                path["stroke-dasharray"] = "12.5, 3, 3, 3"
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
                        }
                    )
                )

        if self.annotations.get("stair_obj"):
            matrix_world = self.annotations["stair_obj"].matrix_world
            for spline in self.annotations["stair_obj"].data.splines:
                classes = ["annotation", "stair"]
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
                        }
                    )
                )
        self.draw_text_annotations()

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

    def draw_misc_annotation(self, obj, classes):
        # We have to decide whether this should come from Blender or from IFC.
        # For the moment, for convenience of experimenting with ideas, it comes
        # from Blender. In the future, it should probably come from IFC.
        if not isinstance(obj.data, bpy.types.Mesh):
            return
        classes.extend(self.get_attribute_classes(obj))
        if len(obj.data.polygons) == 0:
            self.draw_edge_annotation(obj, classes)
            return
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2
        matrix_world = obj.matrix_world
        for polygon in obj.data.polygons:
            points = [obj.data.vertices[v] for v in polygon.vertices]
            projected_points = [self.project_point_onto_camera(matrix_world @ p.co.xyz) for p in points]
            d = " ".join(
                [
                    "L {} {}".format((x_offset + p.x) * self.scale, (y_offset - p.y) * self.scale)
                    for p in projected_points
                ]
            )
            d = "M{}".format(d[1:])
            path = self.svg.add(self.svg.path(d=d, class_=" ".join(classes)))

    def get_attribute_classes(self, obj):
        classes = [obj.name.split("/")[0]]
        for slot in obj.material_slots:
            if slot.material:
                classes.append("material-{}".format(re.sub("[^0-9a-zA-Z]+", "", slot.material.name)))
        global_id = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId
        classes.append("globalid-{}".format(global_id))
        for attribute in self.annotations.get("attributes", []):
            result = self.get_obj_value(obj, attribute)
            if result:
                classes.append(
                    "{}-{}".format(re.sub("[^0-9a-zA-Z]+", "", attribute), re.sub("[^0-9a-zA-Z]+", "", result))
                )
        return classes

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

    def draw_line_annotation(self, obj_data, classes):
        # TODO: properly scope these offsets
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        obj, data = obj_data

        classes.extend(["annotation"])
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

    def draw_text_annotations(self):
        x_offset = self.raw_width / 2
        y_offset = self.raw_height / 2

        for text_obj in self.annotations.get("text_objs", []):
            text_position = self.project_point_onto_camera(text_obj.location)
            text_position = Vector(((x_offset + text_position.x), (y_offset - text_position.y)))

            local_x_axis = text_obj.matrix_world.to_quaternion() @ Vector((1, 0, 0))
            projected_x_axis = self.project_point_onto_camera(text_obj.location + local_x_axis)
            angle = math.degrees(
                (Vector((x_offset + projected_x_axis.x, y_offset - projected_x_axis.y)) - text_position).angle_signed(
                    Vector((1, 0))
                )
            )

            transform = "rotate({}, {}, {})".format(
                angle, (text_position * self.scale)[0], (text_position * self.scale)[1],
            )

            if text_obj.data.BIMTextProperties.symbol != "None":
                self.svg.add(
                    self.svg.use(
                        "#{}".format(text_obj.data.BIMTextProperties.symbol), insert=tuple(text_position * self.scale)
                    )
                )

            if text_obj.data.align_x == "CENTER":
                text_anchor = "middle"
            elif text_obj.data.align_x == "RIGHT":
                text_anchor = "end"
            else:
                text_anchor = "start"

            if text_obj.data.align_y == "CENTER":
                alignment_baseline = "middle"
            elif text_obj.data.align_y == "TOP":
                alignment_baseline = "hanging"
            else:
                alignment_baseline = "baseline"

            text_body = text_obj.data.body
            if text_obj.name in self.annotations.get("template_variables", {}):
                text_body = pystache.render(text_body, self.annotations["template_variables"][text_obj.name])

            for line_number, text_line in enumerate(text_body.split("\n")):
                self.svg.add(
                    self.svg.text(
                        text_line,
                        insert=tuple((text_position * self.scale) + Vector((0, 3.5 * line_number))),
                        class_=" ".join(self.get_attribute_classes(text_obj)),
                        **{
                            "font-size": annotation.Annotator.get_svg_text_size(
                                text_obj.data.BIMTextProperties.font_size
                            ),
                            "font-family": "OpenGost Type B TT",
                            "text-anchor": text_anchor,
                            "alignment-baseline": alignment_baseline,
                            "dominant-baseline": alignment_baseline,
                            "transform": transform,
                        }
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

    def draw_dimension_annotations(self, dimension_obj, text_override=None):
        matrix_world = dimension_obj.matrix_world
        for spline in dimension_obj.data.splines:
            points = self.get_spline_points(spline)
            for i, p in enumerate(points):
                if i + 1 >= len(points):
                    continue
                v0_global = matrix_world @ points[i].co.xyz
                v1_global = matrix_world @ points[i + 1].co.xyz
                self.draw_dimension_annotation(v0_global, v1_global, text_override)

    def draw_measureit_arch_dimension_annotations(self):
        try:
            import MeasureIt_ARCH.measureit_arch_external_utils

            coords = MeasureIt_ARCH.measureit_arch_external_utils.blenderBIM_get_coords(bpy.context)
        except:
            return
        for coord in coords:
            self.draw_dimension_annotation(Vector(coord[0]), Vector(coord[1]))

    def draw_dimension_annotation(self, v0_global, v1_global, text_override=None):
        classes = ["annotation", "dimension"]
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
        line["marker-start"] = "url(#dimension-marker-start)"
        line["marker-end"] = "url(#dimension-marker-end)"
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
                }
            )
        )

    def project_point_onto_camera(self, point):
        return self.camera.matrix_world.inverted() @ geometry.intersect_line_plane(
            point.xyz,
            point.xyz - Vector(self.camera_projection),
            self.camera.location,
            Vector(self.camera_projection),
        )

    def get_spline_points(self, spline):
        return spline.bezier_points if spline.bezier_points else spline.points

    def draw_cut_polygons(self):
        return # deprecate?
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
