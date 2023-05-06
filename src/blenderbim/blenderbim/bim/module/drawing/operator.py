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
import json
import time
import bmesh
import shutil
import shapely
import subprocess
import webbrowser
import numpy as np
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector
import ifcopenshell.util.representation
import blenderbim.bim.schema
import blenderbim.tool as tool
import blenderbim.core.drawing as core
import blenderbim.bim.module.drawing.svgwriter as svgwriter
import blenderbim.bim.module.drawing.annotation as annotation
import blenderbim.bim.module.drawing.sheeter as sheeter
import blenderbim.bim.module.drawing.scheduler as scheduler
import blenderbim.bim.module.drawing.helper as helper
from blenderbim.bim.module.drawing.decoration import CutDecorator
from blenderbim.bim.module.drawing.data import DecoratorData
import blenderbim.bim.export_ifc
from lxml import etree
from mathutils import Vector
from timeit import default_timer as timer
from blenderbim.bim.module.drawing.prop import RasterStyleProperty, Literal
from blenderbim.bim.ifc import IfcStore
from pathlib import Path

cwd = os.path.dirname(os.path.realpath(__file__))


class profile:
    """
    A python context manager timing utility
    """

    def __init__(self, task):
        self.task = task

    def __enter__(self):
        self.start = timer()

    def __exit__(self, *args):
        print(self.task, timer() - self.start)


def open_with_user_command(user_command, path):
    if user_command:
        commands = eval(user_command)
        for command in commands:
            subprocess.Popen(command)
    else:
        webbrowser.open("file://" + path)


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class AddDrawing(bpy.types.Operator, Operator):
    bl_idname = "bim.add_drawing"
    bl_label = "Add Drawing"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = context.scene.DocProperties
        hint = self.props.location_hint
        if self.props.target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]:
            hint = int(hint)
        core.add_drawing(
            tool.Ifc,
            tool.Collector,
            tool.Drawing,
            target_view=self.props.target_view,
            location_hint=hint,
        )
        try:
            drawing = tool.Ifc.get().by_id(self.props.active_drawing_id)
            core.sync_references(tool.Ifc, tool.Collector, tool.Drawing, drawing=drawing)
        except:
            pass


class DuplicateDrawing(bpy.types.Operator, Operator):
    bl_idname = "bim.duplicate_drawing"
    bl_label = "Duplicate Drawing"
    bl_options = {"REGISTER", "UNDO"}
    drawing: bpy.props.IntProperty()
    should_duplicate_annotations: bpy.props.BoolProperty(name="Should Duplicate Annotations", default=False)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout
        row.prop(self, "should_duplicate_annotations")

    def _execute(self, context):
        self.props = context.scene.DocProperties
        core.duplicate_drawing(
            tool.Ifc,
            tool.Drawing,
            drawing=tool.Ifc.get().by_id(self.drawing),
            should_duplicate_annotations=self.should_duplicate_annotations,
        )
        try:
            drawing = tool.Ifc.get().by_id(self.props.active_drawing_id)
            core.sync_references(tool.Ifc, tool.Collector, tool.Drawing, drawing=drawing)
        except:
            pass


class CreateDrawing(bpy.types.Operator):
    """Creates/refreshes a .svg drawing

    Only available if :
    - IFC file is created
    - Camera is in Orthographic mode"""

    bl_idname = "bim.create_drawing"
    bl_label = "Create Drawing"
    bl_description = (
        "Creates/refreshes a .svg drawing based on currently active camera.\n\n"
        + "SHIFT+CLICK to print all selected drawings"
    )
    print_all: bpy.props.BoolProperty(name="Print All", default=False)

    @classmethod
    def poll(cls, context):
        return bool(tool.Ifc.get() and tool.Drawing.is_camera_orthographic() and tool.Drawing.is_drawing_active())

    def invoke(self, context, event):
        # printing all drawings on shift+click
        if event.type == "LEFTMOUSE" and event.shift:
            self.print_all = True
        else:
            # can't rely on default value since the line above
            # will set the value to `True` for all future operator calls
            self.print_all = False
        return self.execute(context)

    def execute(self, context):
        self.props = context.scene.DocProperties

        if self.print_all:
            original_drawing_id = self.props.active_drawing_id
            drawings_to_print = [d.ifc_definition_id for d in self.props.drawings if d.is_selected]
        else:
            drawings_to_print = [self.props.active_drawing_id]

        for drawing_id in drawings_to_print:
            if self.print_all:
                bpy.ops.bim.activate_drawing(drawing=drawing_id)

            self.camera = context.scene.camera
            self.camera_element = tool.Ifc.get_entity(self.camera)
            self.camera_document = tool.Drawing.get_drawing_document(self.camera_element)
            self.file = IfcStore.get_file()

            with profile("Drawing generation process"):
                with profile("Initialize drawing generation process"):
                    self.cprops = self.camera.data.BIMCameraProperties
                    self.drawing_name = self.file.by_id(drawing_id).Name
                    self.metadata = tool.Drawing.get_drawing_metadata(self.camera_element)
                    self.get_scale(context)
                    if self.cprops.update_representation(self.camera):
                        bpy.ops.bim.update_representation(obj=self.camera.name, ifc_representation_class="")

                    self.svg_writer = svgwriter.SvgWriter()
                    self.svg_writer.human_scale = self.human_scale
                    self.svg_writer.scale = self.scale
                    self.svg_writer.data_dir = context.scene.BIMProperties.data_dir
                    self.svg_writer.camera = self.camera
                    self.svg_writer.camera_width, self.svg_writer.camera_height = self.get_camera_dimensions()
                    self.svg_writer.camera_projection = tuple(
                        self.camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
                    )

                    self.svg_writer.setup_drawing_resource_paths(self.camera_element)

                with profile("Generate underlay"):
                    underlay_svg = self.generate_underlay(context)

                with profile("Generate linework"):
                    linework_svg = self.generate_linework(context)

                with profile("Generate annotation"):
                    annotation_svg = self.generate_annotation(context)

                with profile("Combine SVG layers"):
                    svg_path = self.combine_svgs(context, underlay_svg, linework_svg, annotation_svg)

            open_with_user_command(context.preferences.addons["blenderbim"].preferences.svg_command, svg_path)

        if self.print_all:
            bpy.ops.bim.activate_drawing(drawing=original_drawing_id)
        return {"FINISHED"}

    def get_camera_dimensions(self):
        render = bpy.context.scene.render
        if self.is_landscape(render):
            width = self.camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = self.camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x
        return width, height

    def combine_svgs(self, context, underlay, linework, annotation):
        # Hacky :)
        svg_path = self.get_svg_path()
        with open(svg_path, "w") as outfile:
            self.svg_writer.create_blank_svg(svg_path).define_boilerplate()
            boilerplate = self.svg_writer.svg.tostring()
            outfile.write(boilerplate.replace("</svg>", ""))
            if underlay:
                with open(underlay) as infile:
                    for i, line in enumerate(infile):
                        if i < 2:
                            continue
                        elif "</svg>" in line:
                            continue
                        outfile.write(line)
                shutil.copyfile(os.path.splitext(underlay)[0] + ".png", os.path.splitext(svg_path)[0] + "-underlay.png")
            if linework:
                with open(linework) as infile:
                    should_skip = False
                    for i, line in enumerate(infile):
                        if i == 0:
                            continue
                        if "</svg>" in line:
                            continue
                        elif "<defs>" in line:
                            should_skip = True
                            continue
                        elif "</defs>" in line:
                            should_skip = False
                            continue
                        elif should_skip:
                            continue
                        outfile.write(line)
            if annotation:
                with open(annotation) as infile:
                    for i, line in enumerate(infile):
                        if i < 2:
                            continue
                        if "</svg>" in line:
                            continue
                        outfile.write(line)
            outfile.write("</svg>")
        return svg_path

    def generate_underlay(self, context):
        if not self.cprops.has_underlay:
            return
        svg_path = self.get_svg_path(cache_type="underlay")
        context.scene.render.filepath = svg_path[0:-4] + ".png"
        drawing_style = context.scene.DocProperties.drawing_styles[self.cprops.active_drawing_style_index]

        if drawing_style.render_type == "DEFAULT":
            bpy.ops.render.render(write_still=True)
        else:
            previous_visibility = {}
            for obj in self.camera.users_collection[0].objects:
                if bpy.context.view_layer.objects.get(obj.name):
                    previous_visibility[obj.name] = obj.hide_get()
                    obj.hide_set(True)
            for obj in context.visible_objects:
                if (
                    (not obj.data and not obj.instance_collection)
                    or isinstance(obj.data, bpy.types.Camera)
                    or "IfcGrid/" in obj.name
                    or "IfcGridAxis/" in obj.name
                    or "IfcOpeningElement/" in obj.name
                ):
                    if bpy.context.view_layer.objects.get(obj.name):
                        previous_visibility[obj.name] = obj.hide_get()
                        obj.hide_set(True)

            space = self.get_view_3d(context.screen.areas)
            previous_shading = space.shading.type
            previous_format = context.scene.render.image_settings.file_format
            space.shading.type = "RENDERED"
            context.scene.render.image_settings.file_format = "PNG"
            bpy.ops.render.opengl(write_still=True)
            space.shading.type = previous_shading
            context.scene.render.image_settings.file_format = previous_format

            for name, value in previous_visibility.items():
                bpy.data.objects[name].hide_set(value)

        self.svg_writer.create_blank_svg(svg_path).draw_underlay(context.scene.render.filepath).save()
        return svg_path

    def generate_linework(self, context):
        if not self.cprops.has_linework:
            return
        svg_path = self.get_svg_path(cache_type="linework")
        if os.path.isfile(svg_path) and self.props.should_use_linework_cache:
            return svg_path

        with profile("sync"):
            # All very hackish whilst prototyping
            exporter = blenderbim.bim.export_ifc.IfcExporter(None)
            exporter.file = tool.Ifc.get()
            invalidated_elements = exporter.sync_all_objects()
            invalidated_elements += exporter.sync_edited_objects()
            invalidated_guids = [e.GlobalId for e in invalidated_elements if hasattr(e, "GlobalId")]

        # If we have already calculated it in the SVG in the past, don't recalculate
        edited_guids = set()
        for obj in IfcStore.edited_objs:
            element = tool.Ifc.get_entity(obj)
            edited_guids.add(element.GlobalId) if hasattr(element, "GlobalId") else None
        cached_linework = set()
        if os.path.isfile(svg_path):
            tree = etree.parse(svg_path)
            root = tree.getroot()
            cached_linework = {
                el.get("{http://www.ifcopenshell.org/ns}guid")
                for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]")
            }
        cached_linework -= edited_guids

        # This is a work in progress. See #1153 and #1564.
        import hashlib
        import ifcopenshell.draw

        files = {context.scene.BIMProperties.ifc_file: tool.Ifc.get()}

        for ifc_path, ifc in files.items():
            # Don't use draw.main() just whilst we're prototyping and experimenting
            ifc_hash = hashlib.md5(ifc_path.encode("utf-8")).hexdigest()
            ifc_cache_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", f"{ifc_hash}.h5")

            # Get all representation contexts to see what we're dealing with.
            # Drawings only draw bodies and annotations (and facetation, due to a Revit bug).
            # A drawing prioritises a target view context first, followed by a model view context as a fallback.
            # Specifically for PLAN_VIEW and REFLECTED_PLAN_VIEW, any Plan context is also prioritised.

            plan_body_target_contexts = []
            plan_body_model_contexts = []
            model_body_target_contexts = []
            model_body_model_contexts = []

            plan_annotation_target_contexts = []
            plan_annotation_model_contexts = []
            model_annotation_target_contexts = []
            model_annotation_model_contexts = []

            target_view = ifcopenshell.util.element.get_psets(self.camera_element)["EPset_Drawing"]["TargetView"]

            for rep_context in ifc.by_type("IfcGeometricRepresentationContext"):
                if rep_context.is_a("IfcGeometricRepresentationSubContext"):
                    if rep_context.ContextType == "Plan":
                        if rep_context.ContextIdentifier in ["Body", "Facetation"]:
                            if rep_context.TargetView == target_view:
                                plan_body_target_contexts.append(rep_context.id())
                            elif rep_context.TargetView == "MODEL_VIEW":
                                plan_body_model_contexts.append(rep_context.id())
                        elif rep_context.ContextIdentifier == "Annotation":
                            if rep_context.TargetView == target_view:
                                plan_annotation_target_contexts.append(rep_context.id())
                            elif rep_context.TargetView == "MODEL_VIEW":
                                plan_annotation_model_contexts.append(rep_context.id())
                    elif rep_context.ContextType == "Model":
                        if rep_context.ContextIdentifier in ["Body", "Facetation"]:
                            if rep_context.TargetView == target_view:
                                model_body_target_contexts.append(rep_context.id())
                            elif rep_context.TargetView == "MODEL_VIEW":
                                model_body_model_contexts.append(rep_context.id())
                        elif rep_context.ContextIdentifier == "Annotation":
                            if rep_context.TargetView == target_view:
                                model_annotation_target_contexts.append(rep_context.id())
                            elif rep_context.TargetView == "MODEL_VIEW":
                                model_annotation_model_contexts.append(rep_context.id())
                elif rep_context.ContextType == "Model":
                    # You should never purely assign to a "Model" context, but
                    # if you do, this is what we assume your intention is.
                    model_body_model_contexts.append(rep_context.id())
                    continue

            body_contexts = (
                [
                    plan_body_target_contexts,
                    plan_body_model_contexts,
                    model_body_target_contexts,
                    model_body_model_contexts,
                ]
                if target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]
                else [
                    model_body_target_contexts,
                    model_body_model_contexts,
                ]
            )

            annotation_contexts = (
                [
                    plan_annotation_target_contexts,
                    plan_annotation_model_contexts,
                    model_annotation_target_contexts,
                    model_annotation_model_contexts,
                ]
                if target_view in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]
                else [
                    model_annotation_target_contexts,
                    model_annotation_model_contexts,
                ]
            )

            drawing_elements = tool.Drawing.get_drawing_elements(self.camera_element)

            self.setup_serialiser(ifc)
            cache = IfcStore.get_cache()
            [cache.remove(guid) for guid in invalidated_guids]
            tree = ifcopenshell.geom.tree()
            tree.enable_face_styles(True)

            elements = drawing_elements.copy()
            for body_context in body_contexts:
                with profile("Processing body context"):
                    if body_context and elements:
                        geom_settings = ifcopenshell.geom.settings(
                            DISABLE_TRIANGULATION=True, STRICT_TOLERANCE=True, INCLUDE_CURVES=True
                        )
                        geom_settings.set_context_ids(body_context)
                        it = ifcopenshell.geom.iterator(
                            geom_settings, ifc, multiprocessing.cpu_count(), include=elements
                        )
                        it.set_cache(cache)
                        processed = set()
                        for elem in self.yield_from_iterator(it):
                            processed.add(ifc.by_id(elem.id))
                            self.serialiser.write(elem)
                            tree.add_element(elem)
                        elements -= processed

            elements = drawing_elements.copy()
            for annotation_context in annotation_contexts:
                with profile("Processing annotation context"):
                    if annotation_context and elements:
                        geom_settings = ifcopenshell.geom.settings(
                            DISABLE_TRIANGULATION=True, STRICT_TOLERANCE=True, INCLUDE_CURVES=True
                        )
                        geom_settings.set_context_ids(annotation_context)
                        it = ifcopenshell.geom.iterator(
                            geom_settings, ifc, multiprocessing.cpu_count(), include=elements
                        )
                        it.set_cache(cache)
                        processed = set()
                        for elem in self.yield_from_iterator(it):
                            processed.add(ifc.by_id(elem.id))
                            self.serialiser.write(elem)
                            tree.add_element(elem)
                        elements -= processed

        with profile("Finalizing"):
            self.serialiser.finalize()
        results = self.svg_buffer.get_value()

        root = etree.fromstring(results)
        self.move_projection_to_bottom(root)
        self.merge_linework_and_add_metadata(root)

        if self.camera.data.BIMCameraProperties.calculate_shapely_surfaces:
            # shapely variant
            group = root.findall(".//{http://www.w3.org/2000/svg}g")[0]
            nm = group.attrib["{http://www.ifcopenshell.org/ns}name"]
            m4 = np.array(json.loads(group.attrib["{http://www.ifcopenshell.org/ns}plane"]))
            m3 = np.array(json.loads(group.attrib["{http://www.ifcopenshell.org/ns}matrix3"]))
            m44 = np.eye(4)
            m44[0][0:2] = m3[0][0:2]
            m44[1][0:2] = m3[1][0:2]
            m44[0][3] = m3[0][2]
            m44[1][3] = m3[1][2]
            m44 = np.linalg.inv(m44)

            projections = group.findall('.//{http://www.w3.org/2000/svg}g[@class="projection"]') or []

            for projection in projections:
                boundary_lines = []
                for path in projection.findall("./{http://www.w3.org/2000/svg}path"):
                    start, end = [co[1:].split(",") for co in path.attrib["d"].split()]
                    boundary_lines.append(shapely.LineString([start, end]))
                unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
                closed_polygons = shapely.polygonize(unioned_boundaries.geoms)

                for polygon in closed_polygons.geoms:
                    # Less than 1mm2 is not worth styling on sheet
                    if polygon.area < 1:
                        continue
                    centroid = polygon.centroid
                    internal_point = centroid if polygon.contains(centroid) else polygon.representative_point()
                    if internal_point:
                        internal_point = [internal_point.x, internal_point.y]
                        a, b = self.drawing_to_model_co(m44, m4, internal_point, 0.0), self.drawing_to_model_co(
                            m44, m4, internal_point, -100.0
                        )
                        inside_elements = [e for e in tree.select(self.pythonize(a)) if not e.is_a("IfcAnnotation")]
                        if not inside_elements:
                            elements = [
                                e
                                for e in tree.select_ray(self.pythonize(a), self.pythonize(b - a))
                                if not e.instance.is_a("IfcAnnotation")
                            ]
                            if elements:
                                path = etree.Element("path")
                                d = (
                                    "M"
                                    + " L".join(
                                        [",".join([str(o) for o in co]) for co in polygon.exterior.coords[0:-1]]
                                    )
                                    + " Z"
                                )
                                for interior in polygon.interiors:
                                    d += (
                                        " M"
                                        + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]])
                                        + " Z"
                                    )
                                path.attrib["d"] = d
                                classes = self.get_svg_classes(ifc.by_id(elements[0].instance.id()))
                                classes.append("surface")
                                path.set("class", " ".join(list(classes)))
                                group.insert(0, path)

        if self.camera.data.BIMCameraProperties.calculate_svgfill_surfaces:
            results = etree.tostring(root).decode("utf8")
            svg_data_1 = results
            from xml.dom.minidom import parseString

            def yield_groups(n):
                if n.nodeType == n.ELEMENT_NODE and n.tagName == "g":
                    yield n
                for c in n.childNodes:
                    yield from yield_groups(c)

            dom1 = parseString(svg_data_1)
            svg1 = dom1.childNodes[0]
            groups1 = [g for g in yield_groups(svg1) if g.getAttribute("class") == "projection"]

            ls_groups = ifcopenshell.ifcopenshell_wrapper.svg_to_line_segments(results, "projection")

            for i, (ls, g1) in enumerate(zip(ls_groups, groups1)):
                projection, g1 = g1, g1.parentNode

                svgfill_context = ifcopenshell.ifcopenshell_wrapper.context(
                    ifcopenshell.ifcopenshell_wrapper.EXACT_CONSTRUCTIONS, 1.0e-3
                )

                # EXACT_CONSTRUCTIONS is significantly faster than FILTERED_CARTESIAN_QUOTIENT
                # remove duplicates (without tolerance)
                ls = [l for l in map(tuple, set(map(frozenset, ls))) if len(l) == 2 and l[0] != l[1]]
                svgfill_context.add(ls)

                num_passes = 0

                for iteration in range(num_passes + 1):
                    # initialize empty group, note that in the current approach only one
                    # group is stored
                    ps = ifcopenshell.ifcopenshell_wrapper.svg_groups_of_polygons()
                    if iteration != 0 or svgfill_context.build():
                        svgfill_context.write(ps)

                    if iteration != num_passes:
                        pairs = svgfill_context.get_face_pairs()
                        semantics = [None] * (max(pairs) + 1)

                    # Reserialize cells into an SVG string
                    svg_data_2 = ifcopenshell.ifcopenshell_wrapper.polygons_to_svg(ps, True)

                    # We parse both SVG files to create on document with the combination of sections from
                    # the output directly from the serializer and the cells found from the hidden line
                    # rendering
                    dom2 = parseString(svg_data_2)
                    svg2 = dom2.childNodes[0]
                    # file 2 only has the groups we are interested in.
                    # in fact in the approach, it's only a single group

                    g2 = list(yield_groups(svg2))[0]

                    # These are attributes on the original group that we can use to reconstruct
                    # a 4x4 matrix of the projection used in the SVG generation process
                    nm = g1.getAttribute("ifc:name")
                    m4 = np.array(json.loads(g1.getAttribute("ifc:plane")))
                    m3 = np.array(json.loads(g1.getAttribute("ifc:matrix3")))
                    m44 = np.eye(4)
                    m44[0][0:2] = m3[0][0:2]
                    m44[1][0:2] = m3[1][0:2]
                    m44[0][3] = m3[0][2]
                    m44[1][3] = m3[1][2]
                    m44 = np.linalg.inv(m44)

                    # Loop over the cell paths
                    for pi, p in enumerate(g2.getElementsByTagName("path")):

                        d = p.getAttribute("d")
                        coords = [co[1:].split(",") for co in d.split() if co[1:]]
                        polygon = shapely.Polygon(coords)
                        # 1mm2 polygons aren't worth styling in paperspace. Raycasting is expensive!
                        if polygon.area < 1:
                            continue
                        # point inside is an attribute that comes from line_segments_to_polygons() polygons_to_svg?
                        # it is an arbitrary point guaranteed to be inside the polygon and outside
                        # of any potential inner bounds. We can use this to construct a ray to find
                        # the face of the IFC element that the cell belongs to.
                        assert p.hasAttribute("ifc:pointInside")

                        xy = list(map(float, p.getAttribute("ifc:pointInside").split(",")))

                        a, b = self.drawing_to_model_co(m44, m4, xy, 0.0), self.drawing_to_model_co(m44, m4, xy, -100.0)

                        inside_elements = [e for e in tree.select(self.pythonize(a)) if not e.is_a("IfcAnnotation")]
                        if inside_elements:
                            elements = None
                            if iteration != num_passes:
                                semantics[pi] = (inside_elements[0], -1)
                        else:
                            elements = [
                                e
                                for e in tree.select_ray(self.pythonize(a), self.pythonize(b - a))
                                if not e.instance.is_a("IfcAnnotation")
                            ]

                        if elements:
                            classes = self.get_svg_classes(ifc.by_id(elements[0].instance.id()))
                            classes.append("projection")

                            if iteration != num_passes:
                                semantics[pi] = elements[0]
                        else:
                            classes = ["projection"]

                        p.setAttribute("style", "")
                        p.setAttribute("class", " ".join(classes))

                    if iteration != num_passes:
                        to_remove = []

                        for he_idx in range(0, len(pairs), 2):
                            # @todo instead of ray_distance, better do (x.point - y.point).dot(x.normal)
                            # to see if they're coplanar, because ray-distance will be different in case
                            # of element surfaces non-orthogonal to the view direction

                            def format(x):
                                if x is None:
                                    return None
                                elif isinstance(x, tuple):
                                    # found to be inside element using tree.select() no face or style info
                                    return x
                                else:
                                    return (x.instance.is_a(), x.ray_distance, tuple(x.position))

                            pp = pairs[he_idx : he_idx + 2]
                            if pp == (-1, -1):
                                continue
                            data = list(map(format, map(semantics.__getitem__, pp)))
                            if None not in data and data[0][0] == data[1][0] and abs(data[0][1] - data[1][1]) < 1.0e-5:
                                to_remove.append(he_idx // 2)
                                # Print edge index and semantic data
                                # print(he_idx // 2, *data)

                        svgfill_context.merge(to_remove)

                # Swap the XML nodes from the files
                # Remove the original hidden line node we still have in the serializer output
                g1.removeChild(projection)
                g2.setAttribute("class", "projection")
                # Find the children of the projection node parent
                children = [x for x in g1.childNodes if x.nodeType == x.ELEMENT_NODE]
                if children:
                    # Insert the new semantically enriched cell-based projection node
                    # *before* the node with sections from the serializer. SVG derives
                    # draw order from node order in the DOM so sections are draw over
                    # the projections.
                    g1.insertBefore(g2, children[0])
                else:
                    # This generally shouldn't happen
                    g1.appendChild(g2)

            results = dom1.toxml()
            results = results.encode("ascii", "xmlcharrefreplace")
            root = etree.fromstring(results)

        # Spaces are handled as a special case, since they are often overlayed
        # in addition to elements. For example, a space should not obscure
        # other elements in projection. Spaces should also not override cut
        # elements but instead be drawn in addition to cut elements.
        spaces = tool.Drawing.get_drawing_spaces(self.camera_element)

        group = root.findall(".//{http://www.w3.org/2000/svg}g")[0]

        self.svg_writer.calculate_scale()
        x_offset = self.svg_writer.raw_width / 2
        y_offset = self.svg_writer.raw_height / 2

        for space in spaces:
            obj = tool.Ifc.get_object(space)
            if not obj or not tool.Drawing.is_intersecting_camera(obj, self.camera):
                continue
            verts, edges = tool.Drawing.bisect_mesh(obj, self.camera)
            verts = [self.svg_writer.project_point_onto_camera(Vector(v)) for v in verts]
            line_strings = [
                shapely.LineString(
                    [
                        (
                            (x_offset + verts[e[0]][0]) * self.svg_writer.svg_scale,
                            (y_offset - verts[e[0]][1]) * self.svg_writer.svg_scale,
                        ),
                        (
                            (x_offset + verts[e[1]][0]) * self.svg_writer.svg_scale,
                            (y_offset - verts[e[1]][1]) * self.svg_writer.svg_scale,
                        ),
                    ]
                )
                for e in edges
            ]
            closed_polygons = shapely.polygonize(line_strings)
            for polygon in closed_polygons.geoms:
                classes = self.get_svg_classes(space)
                path = etree.Element("path")
                d = "M" + " L".join([",".join([str(o) for o in co]) for co in polygon.exterior.coords[0:-1]]) + " Z"
                for interior in polygon.interiors:
                    d += " M" + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]]) + " Z"
                path.attrib["d"] = d
                path.set("class", " ".join(list(classes)))
                group.append(path)

        with open(svg_path, "wb") as svg:
            svg.write(etree.tostring(root))

        return svg_path

    def setup_serialiser(self, ifc):
        self.svg_settings = ifcopenshell.geom.settings(
            DISABLE_TRIANGULATION=True, STRICT_TOLERANCE=True, INCLUDE_CURVES=True
        )
        self.svg_buffer = ifcopenshell.geom.serializers.buffer()
        self.serialiser = ifcopenshell.geom.serializers.svg(self.svg_buffer, self.svg_settings)
        self.serialiser.setFile(ifc)
        self.serialiser.setWithoutStoreys(True)
        self.serialiser.setPolygonal(True)
        self.serialiser.setUseHlrPoly(True)
        # Objects with more than these edges are rendered as wireframe instead of HLR for optimisation
        self.serialiser.setProfileThreshold(1000)
        self.serialiser.setUseNamespace(True)
        self.serialiser.setAlwaysProject(True)
        self.serialiser.setAutoElevation(False)
        self.serialiser.setAutoSection(False)
        self.serialiser.setPrintSpaceNames(False)
        self.serialiser.setPrintSpaceAreas(False)
        self.serialiser.setDrawDoorArcs(False)
        self.serialiser.setNoCSS(True)
        self.serialiser.setElevationRefGuid(self.camera_element.GlobalId)
        self.serialiser.setScale(self.scale)
        self.serialiser.setSubtractionSettings(ifcopenshell.ifcopenshell_wrapper.ALWAYS)
        # tree = ifcopenshell.geom.tree()
        # This instructs the tree to explode BReps into faces and return
        # the style of the face when running tree.select_ray()
        # tree.enable_face_styles(True)

    def yield_from_iterator(self, it):
        if it.initialize():
            while True:
                yield it.get()
                if not it.next():
                    break

    def get_svg_classes(self, element):
        classes = [element.is_a()]
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        material_name = ""
        if material:
            if material.is_a("IfcMaterialLayerSet"):
                material_name = material.LayerSetName or "null"
            else:
                material_name = getattr(material, "Name", "null") or "null"
            material_name = tool.Drawing.canonicalise_class_name(material_name)
            classes.append(f"material-{material_name}")
        else:
            classes.append(f"material-null")

        for key in self.metadata:
            value = ifcopenshell.util.selector.get_element_value(element, key)
            if value:
                classes.append(
                    tool.Drawing.canonicalise_class_name(key) + "-" + tool.Drawing.canonicalise_class_name(str(value))
                )
        return classes

    def merge_linework_and_add_metadata(self, root):
        join_criteria = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "JoinCriteria")
        if join_criteria:
            join_criteria = join_criteria.split(",")
        else:
            # Drawing convention states that same objects classes with the same material are merged when cut.
            join_criteria = ["class", "material.Name", 'r"Pset.*Common"."Status"']

        group = root.findall(".//{http://www.w3.org/2000/svg}g")[0]
        joined_paths = {}

        ifc = tool.Ifc.get()
        for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]"):
            element = ifc.by_guid(el.get("{http://www.ifcopenshell.org/ns}guid"))
            # Architectural convention only merges these objects. E.g. pipe segments and fittings shouldn't merge.
            if not element.is_a("IfcWall") and not element.is_a("IfcSlab"):
                continue

            classes = self.get_svg_classes(element)
            classes.append("cut")

            el.set("class", " ".join(classes))

            keys = []
            for query in join_criteria:
                key = ifcopenshell.util.selector.get_element_value(element, query)
                if isinstance(key, (list, tuple)):
                    keys.extend(key)
                else:
                    keys.append(key)

            hash_keys = hash(tuple(keys))

            if el.findall("{http://www.w3.org/2000/svg}path"):
                joined_paths.setdefault(hash_keys, []).append(el)

        for key, els in joined_paths.items():
            polygons = []
            classes = set()

            for el in els:
                classes.update(el.attrib["class"].split())
                classes.add(el.attrib["{http://www.ifcopenshell.org/ns}guid"])
                is_closed_polygon = False
                for path in el.findall("{http://www.w3.org/2000/svg}path"):
                    for subpath in path.attrib["d"].split("M")[1:]:
                        subpath = "M" + subpath.strip()
                        coords = [[round(float(o), 1) for o in co[1:].split(",")] for co in subpath.split()]
                        if len(coords) > 2 and coords[0] == coords[-1]:
                            is_closed_polygon = True
                            polygons.append(shapely.Polygon(coords))
                if is_closed_polygon:
                    el.getparent().remove(el)

            try:
                merged_polygons = shapely.ops.unary_union(polygons)
            except:
                print("Warning. Portions of the merge failed. Please report a bug!", polygons)
                merged_polygons = polygons

            if type(merged_polygons) == shapely.MultiPolygon:
                merged_polygons = merged_polygons.geoms
            elif type(merged_polygons) == shapely.Polygon:
                merged_polygons = [merged_polygons]
            else:
                merged_polygons = []

            for polygon in merged_polygons:
                g = etree.Element("g")
                path = etree.SubElement(g, "path")
                d = "M" + " L".join([",".join([str(o) for o in co]) for co in polygon.exterior.coords[0:-1]]) + " Z"
                for interior in polygon.interiors:
                    d += " M" + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]]) + " Z"
                path.attrib["d"] = d
                g.set("class", " ".join(list(classes)))
                group.append(g)

    def drawing_to_model_co(self, m44, m4, xy, z=0.0):
        xyzw = m44 @ np.array(xy + [z, 1.0])
        xyzw[1] *= -1.0
        return (m4 @ xyzw)[0:3]

    def pythonize(self, arr):
        return tuple(map(float, arr))

    def move_projection_to_bottom(self, root):
        # IfcConvert puts the projection afterwards which is not correct since
        # projection should be drawn underneath the cut.
        group = root.find("{http://www.w3.org/2000/svg}g")
        projection = group.find("{http://www.w3.org/2000/svg}g[@class='projection']")
        projection.getparent().remove(projection)
        group.insert(0, projection)

    def generate_annotation(self, context):
        if not self.cprops.has_annotation:
            return
        svg_path = self.get_svg_path(cache_type="annotation")
        if os.path.isfile(svg_path) and self.props.should_use_annotation_cache:
            return svg_path

        elements = tool.Drawing.get_group_elements(tool.Drawing.get_drawing_group(self.camera_element))
        filtered_drawing_elements = tool.Drawing.get_drawing_elements(self.camera_element)
        elements = [e for e in elements if e in filtered_drawing_elements]

        annotations = sorted(elements, key=lambda a: tool.Drawing.get_annotation_z_index(a))

        precision = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "MetricPrecision")
        if not precision:
            precision = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "ImperialPrecision")

        decimal_places = ifcopenshell.util.element.get_pset(self.camera_element, "EPset_Drawing", "DecimalPlaces")
        self.svg_writer.metadata = self.metadata
        self.svg_writer.create_blank_svg(svg_path).draw_annotations(annotations, precision, decimal_places).save()

        return svg_path

    def get_scale(self, context):
        camera_props = self.camera.data.BIMCameraProperties
        if camera_props.diagram_scale == "CUSTOM":
            if context.scene.unit_settings.system == "IMPERIAL":
                if camera_props.custom_diagram_scale_input1[-1] == "'" or camera_props.custom_diagram_scale_input1[-1] == "\"":
                    camera_props.custom_diagram_scale_input1 = camera_props.custom_diagram_scale_input1[:-1]
                if camera_props.custom_diagram_scale_input2[-1] == "'":
                    camera_props.custom_diagram_scale_input2 = camera_props.custom_diagram_scale_input2[:-1]
                if camera_props.custom_diagram_scale_input2[1:] == "'-0\"" or camera_props.custom_diagram_scale_input2[1:] == "' 0\"":
                    camera_props.custom_diagram_scale_input2 = camera_props.custom_diagram_scale_input2[0]
                if "/" in camera_props.custom_diagram_scale_input1:
                    if " " in camera_props.custom_diagram_scale_input1:
                        n1, n2 = camera_props.custom_diagram_scale_input1.split(" ")
                        n2_1, n2_2 = n2.split("/")
                        numerator = int(n1) + (int(n2_1) / int(n2_2))
                    elif "-" in camera_props.custom_diagram_scale_input1:
                        n1, n2 = camera_props.custom_diagram_scale_input1.split("-")
                        n2_1, n2_2 = n2.split("/")
                        numerator = int(n1) + (int(n2_1) / int(n2_2))
                    else:
                        n1, n2 = camera_props.custom_diagram_scale_input1.split("/")
                        numerator = int(n1) / int(n2)
                else:
                    numerator = 1
                denominator = (int(camera_props.custom_diagram_scale_input2) / numerator) * 12
                scale = "1" + "/" + str(denominator)
                human_scale = camera_props.custom_diagram_scale_input1 + "=" + camera_props.custom_diagram_scale_input2
            else:
                scale = camera_props.custom_diagram_scale_input1 + "/" + camera_props.custom_diagram_scale_input2
                human_scale = camera_props.custom_diagram_scale_input1 + ":" + camera_props.custom_diagram_scale_input2

            camera_props.custom_diagram_scale = human_scale + "|" + scale
            self.human_scale, fraction = camera_props.custom_diagram_scale.split("|")
        else:
            self.human_scale, fraction = camera_props.diagram_scale.split("|")

        if camera_props.is_nts:
            self.human_scale = "NTS"

        numerator, denominator = fraction.split("/")
        self.scale = float(numerator) / float(denominator)

    def is_landscape(self, render):
        return render.resolution_x > render.resolution_y

    def get_view_3d(self, areas):
        for area in areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                return space

    def get_material_name(self, element):
        if hasattr(element, "Name") and element.Name:
            return element.Name
        elif hasattr(element, "LayerSetName") and element.LayerSetName:
            return element.LayerSetName
        return "mat-" + str(element.id())

    def get_svg_path(self, cache_type=None):
        drawing_path = tool.Drawing.get_document_uri(self.camera_document)
        drawings_dir = os.path.dirname(drawing_path)

        if cache_type:
            drawings_dir = os.path.join(drawings_dir, "cache")
            os.makedirs(drawings_dir, exist_ok=True)
            return os.path.join(drawings_dir, f"{self.drawing_name}-{cache_type}.svg")
        os.makedirs(drawings_dir, exist_ok=True)
        return drawing_path


class AddAnnotation(bpy.types.Operator, Operator):
    bl_idname = "bim.add_annotation"
    bl_label = "Add Annotation"
    bl_options = {"REGISTER", "UNDO"}
    object_type: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file() and context.scene.camera

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def _execute(self, context):
        drawing = tool.Ifc.get_entity(context.scene.camera)
        if not drawing:
            self.report({"WARNING"}, "Not a BIM camera")
            return

        r = core.add_annotation(tool.Ifc, tool.Collector, tool.Drawing, drawing=drawing, object_type=self.object_type)
        if isinstance(r, str):
            self.report({"WARNING"}, r)


class AddSheet(bpy.types.Operator, Operator):
    bl_idname = "bim.add_sheet"
    bl_label = "Add Sheet"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_sheet(tool.Ifc, tool.Drawing, titleblock=context.scene.DocProperties.titleblock)


class OpenSheet(bpy.types.Operator, Operator):
    bl_idname = "bim.open_sheet"
    bl_label = "Open Sheet"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = context.scene.DocProperties
        sheet = tool.Ifc.get().by_id(self.props.sheets[self.props.active_sheet_index].ifc_definition_id)
        core.open_sheet(tool.Drawing, sheet=sheet)


class AddDrawingToSheet(bpy.types.Operator, Operator):
    bl_idname = "bim.add_drawing_to_sheet"
    bl_label = "Add Drawing To Sheet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.DocProperties
        return props.drawings and props.sheets and context.scene.BIMProperties.data_dir

    def _execute(self, context):
        props = context.scene.DocProperties
        active_drawing = props.drawings[props.active_drawing_index]
        active_sheet = tool.Drawing.get_active_sheet(context)
        drawing = tool.Ifc.get().by_id(active_drawing.ifc_definition_id)
        drawing_reference = tool.Drawing.get_drawing_document(drawing)

        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)
        if not sheet.is_a("IfcDocumentInformation"):
            return

        references = tool.Drawing.get_document_references(sheet)

        has_drawing = False
        for reference in references:
            if reference.Location == drawing_reference.Location:
                has_drawing = True
                break
        if has_drawing:
            return

        if not tool.Drawing.does_file_exist(tool.Drawing.get_document_uri(drawing_reference)):
            self.report({"ERROR"}, "The drawing must be generated before adding to a sheet.")
            return

        reference = tool.Ifc.run("document.add_reference", information=sheet)
        id_attr = "ItemReference" if tool.Ifc.get_schema() == "IFC2X3" else "Identification"
        attributes = {
            id_attr: str(len([r for r in references if r.Description in ("DRAWING", "SCHEDULE")]) + 1),
            "Location": drawing_reference.Location,
            "Description": "DRAWING",
        }
        tool.Ifc.run("document.edit_reference", reference=reference, attributes=attributes)
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.add_drawing(reference, drawing, sheet)

        tool.Drawing.import_sheets()


class RemoveDrawingFromSheet(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_drawing_from_sheet"
    bl_label = "Remove Drawing From Sheet"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()

    def _execute(self, context):
        reference = tool.Ifc.get().by_id(self.reference)
        sheet = tool.Drawing.get_reference_document(reference)

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.remove_drawing(reference, sheet)

        tool.Ifc.run("document.remove_reference", reference=reference)

        tool.Drawing.import_sheets()


class CreateSheets(bpy.types.Operator, Operator):
    bl_idname = "bim.create_sheets"
    bl_label = "Create Sheets"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.DocProperties.sheets and context.scene.BIMProperties.data_dir

    def _execute(self, context):
        scene = context.scene
        props = scene.DocProperties
        active_sheet = props.sheets[props.active_sheet_index]
        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)

        if not sheet.is_a("IfcDocumentInformation"):
            return

        name = os.path.splitext(os.path.basename(tool.Drawing.get_document_uri(sheet)))[0]
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = scene.BIMProperties.data_dir

        references = sheet_builder.build(sheet)
        raster_references = [tool.Ifc.get_relative_uri(r) for r in references["RASTER"]]

        # These variables will be made available to the evaluated commands
        svg = references["SHEET"]
        basename = os.path.basename(svg)
        path = os.path.dirname(svg)
        pdf = os.path.splitext(svg)[0] + ".pdf"
        eps = os.path.splitext(svg)[0] + ".eps"
        dxf = os.path.splitext(svg)[0] + ".dxf"

        has_sheet_reference = False
        for reference in tool.Drawing.get_document_references(sheet):
            if reference.Description == "SHEET":
                has_sheet_reference = True
            elif reference.Description == "RASTER":
                if reference.Location in raster_references:
                    del raster_references[reference.Location]
                else:
                    tool.Ifc.run("document.remove_reference", reference=reference)

        if not has_sheet_reference:
            reference = tool.Ifc.run("document.add_reference", information=sheet)
            tool.Ifc.run(
                "document.edit_reference",
                reference=reference,
                attributes={"Location": tool.Ifc.get_relative_uri(svg), "Description": "SHEET"},
            )

        for raster_reference in raster_references:
            reference = tool.Ifc.run("document.add_reference", information=sheet)
            tool.Ifc.run(
                "document.edit_reference",
                reference=reference,
                attributes={"Location": tool.Ifc.get_relative_uri(raster_reference), "Description": "RASTER"},
            )

        svg2pdf_command = context.preferences.addons["blenderbim"].preferences.svg2pdf_command
        svg2dxf_command = context.preferences.addons["blenderbim"].preferences.svg2dxf_command

        if svg2pdf_command:
            # With great power comes great responsibility. Example:
            # [['inkscape', svg, '-o', pdf]]
            commands = eval(svg2pdf_command)
            for command in commands:
                subprocess.run(command)

        if svg2dxf_command:
            # With great power comes great responsibility. Example:
            # [['inkscape', svg, '-o', eps], ['pstoedit', '-dt', '-f', 'dxf:-polyaslines -mm', eps, dxf, '-psarg', '-dNOSAFER']]
            commands = eval(svg2dxf_command)
            for command in commands:
                subprocess.run(command)

        if svg2pdf_command:
            open_with_user_command(context.preferences.addons["blenderbim"].preferences.pdf_command, pdf)
        else:
            open_with_user_command(context.preferences.addons["blenderbim"].preferences.svg_command, svg)


class SelectAllDrawings(bpy.types.Operator):
    bl_idname = "bim.select_all_drawings"
    bl_label = "Select All Drawings"
    view: bpy.props.StringProperty()
    bl_description = "Select all drawings in the drawing list.\n\n" + "SHIFT+CLICK to deselect all drawings"
    select_all: bpy.props.BoolProperty(name="Open All", default=False)

    def invoke(self, context, event):
        # deselect all drawings on shift+click
        if event.type == "LEFTMOUSE" and event.shift:
            self.select_all = False
        else:
            # can't rely on default value since the line above
            # will set the value to `True` for all future operator calls
            self.select_all = True
        return self.execute(context)

    def execute(self, context):
        for drawing in context.scene.DocProperties.drawings:
            if drawing.is_selected != self.select_all:
                drawing.is_selected = self.select_all
        return {"FINISHED"}


class OpenDrawing(bpy.types.Operator):
    bl_idname = "bim.open_drawing"
    bl_label = "Open Drawing"
    view: bpy.props.StringProperty()
    bl_description = (
        "Opens a .svg drawing based on currently active camera with default system viewer\n"
        + 'or using "svg_command" from the BlenderBIM preferences (if provided).\n\n'
        + "SHIFT+CLICK to open all selected drawings"
    )
    open_all: bpy.props.BoolProperty(name="Open All", default=False)

    def invoke(self, context, event):
        # opening all drawings on shift+click
        if event.type == "LEFTMOUSE" and event.shift:
            self.open_all = True
        else:
            # can't rely on default value since the line above
            # will set the value to `True` for all future operator calls
            self.open_all = False
        return self.execute(context)

    def execute(self, context):
        if self.open_all:
            drawings = [
                tool.Ifc.get().by_id(d.ifc_definition_id) for d in context.scene.DocProperties.drawings if d.is_selected
            ]
        else:
            drawings = [tool.Ifc.get().by_id(context.scene.DocProperties.drawings.get(self.view).ifc_definition_id)]

        drawing_uris = []
        drawings_not_found = []

        for drawing in drawings:
            drawing_uri = tool.Drawing.get_document_uri(tool.Drawing.get_drawing_document(drawing))
            drawing_uris.append(drawing_uri)
            if not os.path.exists(drawing_uri):
                drawings_not_found.append(drawing.Name)

        if drawings_not_found:
            msg = "Some drawings .svg files were not found, need to print them first: \n{}.".format(
                "\n".join(drawings_not_found)
            )
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        for drawing_uri in drawing_uris:
            open_with_user_command(context.preferences.addons["blenderbim"].preferences.svg_command, drawing_uri)
        return {"FINISHED"}


class ActivateModel(bpy.types.Operator):
    bl_idname = "bim.activate_model"
    bl_label = "Activate Model"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Activates the model view"

    def execute(self, context):
        CutDecorator.uninstall()

        bpy.ops.object.hide_view_clear()

        subcontext = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            model = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if model:
                current_representation = tool.Geometry.get_active_representation(obj)
                if current_representation != model:
                    blenderbim.core.geometry.switch_representation(
                        tool.Ifc,
                        tool.Geometry,
                        obj=obj,
                        representation=model,
                        should_reload=False,
                        is_global=True,
                        should_sync_changes_first=True,
                    )
        tool.Blender.update_viewport()
        return {"FINISHED"}


class ActivateDrawing(bpy.types.Operator):
    """
    Activates the selected drawing view
    """

    bl_idname = "bim.activate_drawing"
    bl_label = "Activate Drawing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Activates the selected drawing view"
    drawing: bpy.props.IntProperty()

    def execute(self, context):
        drawing = tool.Ifc.get().by_id(self.drawing)
        core.activate_drawing_view(tool.Ifc, tool.Drawing, drawing=drawing)
        bpy.context.scene.DocProperties.active_drawing_id = self.drawing
        if ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", "HasUnderlay"):
            bpy.ops.bim.activate_drawing_style()
        core.sync_references(tool.Ifc, tool.Collector, tool.Drawing, drawing=tool.Ifc.get().by_id(self.drawing))
        CutDecorator.install(context)
        return {"FINISHED"}


class SelectDocIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_doc_ifc_file"
    bl_label = "Select Documentation IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.DocProperties.ifc_files[self.index].name = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ResizeText(bpy.types.Operator):
    bl_idname = "bim.resize_text"
    bl_label = "Resize Text"
    bl_options = {"REGISTER", "UNDO"}
    # TODO: check undo redo

    def execute(self, context):
        for obj in context.scene.camera.users_collection[0].objects:
            if isinstance(obj.data, bpy.types.TextCurve):
                annotation.Annotator.resize_text(obj)
        return {"FINISHED"}


class RemoveDrawing(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_drawing"
    bl_label = "Remove Drawing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove currently selected drawing.\n\n" + "SHIFT+CLICK to remove all selected drawings"

    drawing: bpy.props.IntProperty()
    remove_all: bpy.props.BoolProperty(name="Remove All", default=False)

    def invoke(self, context, event):
        # removing all selected drawings on shift+click
        if event.type == "LEFTMOUSE" and event.shift:
            self.remove_all = True
        else:
            # can't rely on default value since the line above
            # will set the value to `True` for all future operator calls
            self.remove_all = False
        return self.execute(context)

    def _execute(self, context):
        if self.remove_all:
            drawings = [
                tool.Ifc.get().by_id(d.ifc_definition_id) for d in context.scene.DocProperties.drawings if d.is_selected
            ]
        else:
            drawings = [tool.Ifc.get().by_id(self.drawing)]

        print("Removing drawings: {}".format([d for d in drawings]))

        for drawing in drawings:
            core.remove_drawing(tool.Ifc, tool.Drawing, drawing=drawing)


class AddDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.add_drawing_style"
    bl_label = "Add Drawing Style"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        new = context.scene.DocProperties.drawing_styles.add()
        new.name = "New Drawing Style"
        return {"FINISHED"}


class RemoveDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.remove_drawing_style"
    bl_label = "Remove Drawing Style"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.DocProperties.drawing_styles.remove(self.index)
        return {"FINISHED"}


class SaveDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.save_drawing_style"
    bl_label = "Save Drawing Style"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.StringProperty()
    # TODO: check undo redo

    def execute(self, context):
        space = self.get_view_3d(context)  # Do not remove. It is used later in eval
        scene = context.scene
        style = {}
        for prop in RasterStyleProperty:
            value = eval(prop.value)
            if not isinstance(value, str):
                try:
                    value = tuple(value)
                except TypeError:
                    pass
            style[prop.value] = value
        if self.index:
            index = int(self.index)
        else:
            index = context.active_object.data.BIMCameraProperties.active_drawing_style_index
        scene.DocProperties.drawing_styles[index].raster_style = json.dumps(style)
        return {"FINISHED"}

    def get_view_3d(self, context):
        for area in context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                return space


class ActivateDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.activate_drawing_style"
    bl_label = "Activate Drawing Style"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        if scene.camera.data.BIMCameraProperties.active_drawing_style_index < len(scene.DocProperties.drawing_styles):
            self.drawing_style = scene.DocProperties.drawing_styles[
                scene.camera.data.BIMCameraProperties.active_drawing_style_index
            ]
            self.set_raster_style(context)
            self.set_query(context)
        return {"FINISHED"}

    def set_raster_style(self, context):
        scene = context.scene  # Do not remove. It is used in exec later
        space = self.get_view_3d(context)  # Do not remove. It is used in exec later
        style = json.loads(self.drawing_style.raster_style)
        for path, value in style.items():
            if isinstance(value, str):
                exec(f"{path} = '{value}'")
            else:
                exec(f"{path} = {value}")

    def set_query(self, context):
        self.include_global_ids = []
        self.exclude_global_ids = []
        for ifc_file in context.scene.DocProperties.ifc_files:
            try:
                ifc = ifcopenshell.open(ifc_file.name)
            except:
                continue
            if self.drawing_style.include_query:
                results = ifcopenshell.util.selector.Selector.parse(ifc, self.drawing_style.include_query)
                self.include_global_ids.extend([e.GlobalId for e in results])
            if self.drawing_style.exclude_query:
                results = ifcopenshell.util.selector.Selector.parse(ifc, self.drawing_style.exclude_query)
                self.exclude_global_ids.extend([e.GlobalId for e in results])
        if self.drawing_style.include_query:
            self.parse_filter_query("INCLUDE", context)
        if self.drawing_style.exclude_query:
            self.parse_filter_query("EXCLUDE", context)

    def parse_filter_query(self, mode, context):
        if mode == "INCLUDE":
            objects = context.scene.objects
        elif mode == "EXCLUDE":
            objects = context.visible_objects
        for obj in objects:
            if mode == "INCLUDE":
                obj.hide_viewport = False  # Note: this breaks alt-H
            global_id = obj.BIMObjectProperties.attributes.get("GlobalId")
            if not global_id:
                continue
            global_id = global_id.string_value
            if mode == "INCLUDE":
                if global_id not in self.include_global_ids:
                    obj.hide_viewport = True  # Note: this breaks alt-H
            elif mode == "EXCLUDE":
                if global_id in self.exclude_global_ids:
                    obj.hide_viewport = True  # Note: this breaks alt-H

    def get_view_3d(self, context):
        for area in context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                return space


class RemoveSheet(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_sheet"
    bl_label = "Remove Sheet"
    bl_options = {"REGISTER", "UNDO"}
    sheet: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_sheet(tool.Ifc, tool.Drawing, sheet=tool.Ifc.get().by_id(self.sheet))


class AddSchedule(bpy.types.Operator, Operator):
    bl_idname = "bim.add_schedule"
    bl_label = "Add Schedule"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ods;*.xls;*.xlsx", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=True)

    def _execute(self, context):
        filepath = self.filepath
        if self.use_relative_path:
            ifc_path = tool.Ifc.get_path()
            if os.path.isfile(ifc_path):
                ifc_path = os.path.dirname(ifc_path)
            filepath = os.path.relpath(filepath, ifc_path)
        core.add_schedule(
            tool.Ifc,
            tool.Drawing,
            uri=filepath,
        )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class RemoveSchedule(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_schedule"
    bl_label = "Remove Schedule"
    bl_options = {"REGISTER", "UNDO"}
    schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_schedule(tool.Ifc, tool.Drawing, schedule=tool.Ifc.get().by_id(self.schedule))


class OpenSchedule(bpy.types.Operator, Operator):
    bl_idname = "bim.open_schedule"
    bl_label = "Open Schedule"
    bl_options = {"REGISTER", "UNDO"}
    schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.open_schedule(tool.Drawing, schedule=tool.Ifc.get().by_id(self.schedule))


class BuildSchedule(bpy.types.Operator, Operator):
    bl_idname = "bim.build_schedule"
    bl_label = "Build Schedule"
    schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.build_schedule(tool.Drawing, schedule=tool.Ifc.get().by_id(self.schedule))


class AddScheduleToSheet(bpy.types.Operator, Operator):
    bl_idname = "bim.add_schedule_to_sheet"
    bl_label = "Add Schedule To Sheet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.DocProperties
        return props.schedules and props.sheets and context.scene.BIMProperties.data_dir

    def _execute(self, context):
        props = context.scene.DocProperties
        active_schedule = props.schedules[props.active_schedule_index]
        active_sheet = tool.Drawing.get_active_sheet(context)
        schedule = tool.Ifc.get().by_id(active_schedule.ifc_definition_id)
        if tool.Ifc.get_schema() == "IFC2X3":
            schedule_location = tool.Drawing.get_path_with_ext(schedule.DocumentReferences[0].Location, "svg")
        else:
            schedule_location = tool.Drawing.get_path_with_ext(schedule.HasDocumentReferences[0].Location, "svg")

        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)
        if not sheet.is_a("IfcDocumentInformation"):
            return

        references = tool.Drawing.get_document_references(sheet)

        has_schedule = False
        for reference in references:
            if reference.Location == schedule_location:
                has_schedule = True
                break
        if has_schedule:
            return

        if not tool.Drawing.does_file_exist(tool.Ifc.resolve_uri(schedule_location)):
            self.report({"ERROR"}, "The schedule must be generated before adding to a sheet.")
            return

        reference = tool.Ifc.run("document.add_reference", information=sheet)
        id_attr = "ItemReference" if tool.Ifc.get_schema() == "IFC2X3" else "Identification"
        attributes = {
            id_attr: str(len([r for r in references if r.Description in ("DRAWING", "SCHEDULE")]) + 1),
            "Location": schedule_location,
            "Description": "SCHEDULE",
        }
        tool.Ifc.run("document.edit_reference", reference=reference, attributes=attributes)

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.add_schedule(reference, schedule, sheet)

        tool.Drawing.import_sheets()


class AddDrawingStyleAttribute(bpy.types.Operator):
    bl_idname = "bim.add_drawing_style_attribute"
    bl_label = "Add Drawing Style Attribute"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.camera.data.BIMCameraProperties
        context.scene.DocProperties.drawing_styles[props.active_drawing_style_index].attributes.add()
        return {"FINISHED"}


class RemoveDrawingStyleAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_drawing_style_attribute"
    bl_label = "Remove Drawing Style Attribute"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.camera.data.BIMCameraProperties
        context.scene.DocProperties.drawing_styles[props.active_drawing_style_index].attributes.remove(self.index)
        return {"FINISHED"}


class CleanWireframes(bpy.types.Operator):
    bl_idname = "bim.clean_wireframes"
    bl_label = "Clean Wireframes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.selected_objects:
            objects = context.selected_objects
        else:
            objects = context.scene.objects
        for obj in (o for o in objects if o.type == "MESH"):
            if "EDGE_SPLIT" not in (m.type for m in obj.modifiers):
                obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
        return {"FINISHED"}


class EditTextPopup(bpy.types.Operator):
    bl_idname = "bim.edit_text_popup"
    bl_label = "Edit Text"
    first_run: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        # shares most of the code with BIM_PT_text.draw()
        # need to keep them in sync or move to some common function
        # NOTE: that `popup_active_attribute` is used here when it's not used in `BIM_PT_text.draw()`

        props = context.active_object.BIMTextProperties

        row = self.layout.row(align=True)
        row.operator("bim.add_text_literal", icon="ADD", text="Add Literal")

        row = self.layout.row(align=True)
        row.prop(props, "font_size")

        for i, literal_props in enumerate(props.literals):
            box = self.layout.box()
            row = self.layout.row(align=True)

            row = box.row(align=True)
            row.label(text=f"Literal[{i}]:")
            row.operator("bim.remove_text_literal", icon="X", text="").literal_prop_id = i

            # skip BoxAlignment since we're going to format it ourselves
            attributes = [a for a in literal_props.attributes if a.name != "BoxAlignment"]
            blenderbim.bim.helper.draw_attributes(attributes, box, popup_active_attribute=attributes[0])

            row = box.row(align=True)
            cols = [row.column(align=True) for i in range(3)]
            for i in range(9):
                cols[i % 3].prop(
                    literal_props,
                    "box_alignment",
                    text="",
                    index=i,
                    icon="RADIOBUT_ON" if literal_props.box_alignment[i] else "RADIOBUT_OFF",
                )

            col = row.column(align=True)
            col.label(text="    Text box alignment:")
            col.label(text=f'    {literal_props.attributes["BoxAlignment"].string_value}')

    def cancel(self, context):
        # disable editing when dialog is closed
        bpy.ops.bim.disable_editing_text()

    def execute(self, context):
        # can't use invoke() because this operator
        # will be run indirectly by hotkey
        # so we use execute() and track whether it's the first run of the operator
        if self.first_run:
            bpy.ops.bim.enable_editing_text()
            self.first_run = False
            return context.window_manager.invoke_props_dialog(self)
        else:
            bpy.ops.bim.edit_text()
            return {"FINISHED"}


class EditText(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_text"
    bl_label = "Edit Text"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_text(tool.Drawing, obj=context.active_object)
        tool.Blender.update_viewport()


class EnableEditingText(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_text"
    bl_label = "Enable Editing Text"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_text(tool.Drawing, obj=context.active_object)


class DisableEditingText(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_text"
    bl_label = "Disable Editing Text"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        core.disable_editing_text(tool.Drawing, obj=obj)

        # force update this object's font size for viewport display
        DecoratorData.data.pop(obj.name, None)
        tool.Drawing.update_text_value(obj)
        tool.Blender.update_viewport()


class AddTextLiteral(bpy.types.Operator):
    bl_idname = "bim.add_text_literal"
    bl_label = "Add Text Literal"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object

        # similar to `tool.Drawing.import_text_attributes`
        literal_props = obj.BIMTextProperties.literals.add()
        literal_attributes = literal_props.attributes
        literal_attr_values = {
            "Literal": "Literal",
            "Path": "RIGHT",
            "BoxAlignment": "bottom_left",
        }
        # emulates `blenderbim.bim.helper.import_attributes2(ifc_literal, literal_props.attributes)`
        for attr_name in literal_attr_values:
            attr = literal_attributes.add()
            attr.name = attr_name
            if attr_name == "Path":
                attr.data_type = "enum"
                attr.enum_items = '["DOWN", "LEFT", "RIGHT", "UP"]'
                attr.enum_value = literal_attr_values[attr_name]

            else:
                attr.data_type = "string"
                attr.string_value = literal_attr_values[attr_name]

        box_alignment_mask = [False] * 9
        box_alignment_mask[6] = True  # bottom_left box_alignment
        literal_props.box_alignment = box_alignment_mask
        return {"FINISHED"}


class RemoveTextLiteral(bpy.types.Operator):
    bl_idname = "bim.remove_text_literal"
    bl_label = "Remove Text Literal"
    bl_options = {"REGISTER", "UNDO"}

    literal_prop_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.active_object
        obj.BIMTextProperties.literals.remove(self.literal_prop_id)
        return {"FINISHED"}


class EditAssignedProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_assigned_product"
    bl_label = "Edit Text Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        product = None
        if context.active_object.BIMAssignedProductProperties.relating_product:
            product = tool.Ifc.get_entity(context.active_object.BIMAssignedProductProperties.relating_product)
        core.edit_assigned_product(tool.Ifc, tool.Drawing, obj=context.active_object, product=product)
        tool.Blender.update_viewport()


class EnableEditingAssignedProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_assigned_product"
    bl_label = "Enable Editing Assigned Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_assigned_product(tool.Drawing, obj=context.active_object)


class DisableEditingAssignedProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_assigned_product"
    bl_label = "Disable Editing Assigned Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_assigned_product(tool.Drawing, obj=context.active_object)


class LoadSheets(bpy.types.Operator, Operator):
    bl_idname = "bim.load_sheets"
    bl_label = "Load Sheets"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_sheets(tool.Drawing)

        props = context.scene.DocProperties
        sheets_not_found = []
        for sheet_prop in props.sheets:
            if not sheet_prop.is_sheet:
                continue

            sheet = tool.Ifc.get().by_id(sheet_prop.ifc_definition_id)
            document_uri = tool.Drawing.get_document_uri(sheet)

            filepath = Path(document_uri)
            if not filepath.is_file():
                sheet_name = f"{sheet_prop.identification} - {sheet_prop.name}"
                sheets_not_found.append(f'"{sheet_name}" - {document_uri}')

        if sheets_not_found:
            self.report({"ERROR"}, "Some sheets svg files are missing:\n" + "\n".join(sheets_not_found))


class EditSheet(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_sheet"
    bl_label = "Edit Sheet"
    bl_options = {"REGISTER", "UNDO"}
    identification: bpy.props.StringProperty()
    name: bpy.props.StringProperty()

    def invoke(self, context, event):
        self.props = context.scene.DocProperties
        sheet = tool.Ifc.get().by_id(self.props.sheets[self.props.active_sheet_index].ifc_definition_id)
        if sheet.is_a("IfcDocumentInformation"):
            self.document_type = "SHEET"
            self.name = sheet.Name
            self.identification = sheet.Identification
        elif sheet.is_a("IfcDocumentReference") and sheet.Description == "TITLEBLOCK":
            self.document_type = "TITLEBLOCK"
        else:
            self.document_type = "EMBEDDED"
            self.identification = sheet.Identification
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        if self.document_type == "SHEET":
            row = self.layout.row()
            row.prop(self, "identification", text="Identification")
            row = self.layout.row()
            row.prop(self, "name", text="Name")
        elif self.document_type == "TITLEBLOCK":
            row = self.layout.row()
            row.prop(context.scene.DocProperties, "titleblock", text="Titleblock")
        elif self.document_type == "EMBEDDED":
            row = self.layout.row()
            row.prop(self, "identification", text="Identification")

    def _execute(self, context):
        self.props = context.scene.DocProperties
        sheet = tool.Ifc.get().by_id(self.props.sheets[self.props.active_sheet_index].ifc_definition_id)
        if self.document_type == "SHEET":
            core.rename_sheet(tool.Ifc, tool.Drawing, sheet=sheet, identification=self.identification, name=self.name)
        elif self.document_type == "EMBEDDED":
            core.rename_reference(tool.Ifc, reference=sheet, identification=self.identification)
        elif self.document_type == "TITLEBLOCK":
            titleblock = self.props.titleblock
            reference = sheet
            sheet = tool.Drawing.get_reference_document(reference)
            tool.Ifc.run(
                "document.edit_reference",
                reference=reference,
                attributes={"Location": tool.Drawing.get_default_titleblock_path(titleblock)},
            )
            sheet_builder = sheeter.SheetBuilder()
            sheet_builder.data_dir = context.scene.BIMProperties.data_dir
            sheet_builder.change_titleblock(sheet, titleblock)
        tool.Drawing.import_sheets()


class DisableEditingSheets(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_sheets"
    bl_label = "Disable Editing Sheets"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_sheets(tool.Drawing)


class LoadSchedules(bpy.types.Operator, Operator):
    bl_idname = "bim.load_schedules"
    bl_label = "Load Schedules"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_schedules(tool.Drawing)


class DisableEditingSchedules(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_schedules"
    bl_label = "Disable Editing Schedules"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_schedules(tool.Drawing)


class LoadDrawings(bpy.types.Operator, Operator):
    bl_idname = "bim.load_drawings"
    bl_label = "Load Drawings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_drawings(tool.Drawing)


class DisableEditingDrawings(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_drawings"
    bl_label = "Disable Editing Drawings"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_drawings(tool.Drawing)


class ExpandSheet(bpy.types.Operator):
    bl_idname = "bim.expand_sheet"
    bl_label = "Expand Sheet"
    bl_options = {"REGISTER", "UNDO"}
    sheet: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.DocProperties
        for sheet in [s for s in props.sheets if s.ifc_definition_id == self.sheet]:
            sheet.is_expanded = True
        core.load_sheets(tool.Drawing)
        return {"FINISHED"}


class ContractSheet(bpy.types.Operator):
    bl_idname = "bim.contract_sheet"
    bl_label = "Contract Sheet"
    bl_options = {"REGISTER", "UNDO"}
    sheet: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.DocProperties
        for sheet in [s for s in props.sheets if s.ifc_definition_id == self.sheet]:
            sheet.is_expanded = False
        core.load_sheets(tool.Drawing)
        return {"FINISHED"}


class SelectAssignedProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.select_assigned_product"
    bl_label = "Select Assigned Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.select_assigned_product(tool.Drawing, context)
