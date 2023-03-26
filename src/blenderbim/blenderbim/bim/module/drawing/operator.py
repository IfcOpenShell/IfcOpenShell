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
from blenderbim.bim.module.drawing.data import DecoratorData
import blenderbim.bim.export_ifc
from lxml import etree
from mathutils import Vector
from timeit import default_timer as timer
from blenderbim.bim.module.drawing.prop import RasterStyleProperty, Literal
from blenderbim.bim.ifc import IfcStore

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
        + "SHIFT+CLICK to print all annotations"
    )
    print_all: bpy.props.BoolProperty(name="Print all", default=False)

    @classmethod
    def poll(cls, context):
        return bool(tool.Ifc.get() and tool.Drawing.is_camera_orthographic() and tool.Drawing.is_drawing_active())

    def invoke(self, context, event):
        # printing all annotations on shift+click
        if event.type == "LEFTMOUSE" and event.shift:
            self.print_all = True
        else:
            # can't rely on default value since `self.print_all = True`
            # will set the value to `True` for all future calls
            self.print_all = False
        return self.execute(context)

    def execute(self, context):
        self.props = context.scene.DocProperties

        if self.print_all:
            original_drawing_id = self.props.active_drawing_id
            drawings_to_print = [drawing.ifc_definition_id for drawing in self.props.drawings]
        else:
            drawings_to_print = [self.props.active_drawing_id]

        for drawing_id in drawings_to_print:
            if self.print_all:
                bpy.ops.bim.activate_view(drawing=drawing_id)

            self.camera = context.scene.camera
            self.camera_element = tool.Ifc.get_entity(self.camera)
            self.file = IfcStore.get_file()

            with profile("Drawing generation process"):
                with profile("Initialize drawing generation process"):
                    self.cprops = self.camera.data.BIMCameraProperties
                    self.drawing_name = self.file.by_id(drawing_id).Name
                    self.get_scale()
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
                    pset = ifcopenshell.util.element.get_psets(self.camera_element)["EPset_Drawing"]
                    related_paths = {
                        "Stylesheet": pset.get("Stylesheet"),
                        "Markers": pset.get("Markers"),
                        "Symbols": pset.get("Symbols"),
                        "Patterns": pset.get("Patterns"),
                    }
                    self.svg_writer.define_related_paths(**related_paths)

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
            bpy.ops.bim.activate_view(drawing=original_drawing_id)
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
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "diagrams", self.drawing_name + ".svg")
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
                shutil.copyfile(underlay[0:-4] + ".png", svg_path[0:-4] + "-underlay.png")
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
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-underlay.svg")
        context.scene.render.filepath = svg_path[0:-4] + ".png"
        drawing_style = context.scene.DocProperties.drawing_styles[self.cprops.active_drawing_style_index]

        if drawing_style.render_type == "DEFAULT":
            bpy.ops.render.render(write_still=True)
        else:
            previous_visibility = {}
            for obj in self.camera.users_collection[0].objects:
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
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-linework.svg")
        if os.path.isfile(svg_path) and self.props.should_use_linework_cache:
            return svg_path

        with profile("sync"):
            # All very hackish whilst prototyping
            exporter = blenderbim.bim.export_ifc.IfcExporter(None)
            exporter.file = tool.Ifc.get()
            invalidated_guids = exporter.sync_deletions()
            invalidated_elements = exporter.sync_all_objects()
            invalidated_elements += exporter.sync_edited_objects()
            [invalidated_guids.append(e.GlobalId) for e in invalidated_elements if hasattr(e, "GlobalId")]

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
                        elements -= processed

            with profile("Camera element"):
                # @todo tfk: is this needed?
                # If the camera isn't serialised, then nothing gets serialised. Odd behaviour.
                geom_settings = ifcopenshell.geom.settings(DISABLE_TRIANGULATION=True, STRICT_TOLERANCE=True)
                it = ifcopenshell.geom.iterator(geom_settings, ifc, include=[self.camera_element])
                for elem in self.yield_from_iterator(it):
                    self.serialiser.write(elem)

        with profile("Finalizing"):
            self.serialiser.finalize()
        results = self.svg_buffer.get_value()

        with profile("Post processing"):
            root = etree.fromstring(results)
            self.move_projection_to_bottom(root)
            self.merge_linework_and_add_metadata(root)
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

    def merge_linework_and_add_metadata(self, root):
        joined_paths = {}

        ifc = tool.Ifc.get()
        for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]"):
            classes = ["cut"]
            element = ifc.by_guid(el.get("{http://www.ifcopenshell.org/ns}guid"))
            material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
            material_name = ""
            if material:
                if material.is_a("IfcMaterialLayerSet"):
                    material_name = material.LayerSetName or "null"
                else:
                    material_name = getattr(material, "Name", "null") or "null"
                material_name = self.canonicalise_class_name(material_name)
                classes.append(f"material-{material_name}")
            el.set("class", (el.get("class", "") + " " + " ".join(classes)).strip())

            # Drawing convention states that objects with the same material are merged when cut.
            if material_name != "null" and el.findall("{http://www.w3.org/2000/svg}path"):
                joined_paths.setdefault(material_name, []).append(el)

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

            merged_polygons = shapely.ops.unary_union(polygons)

            if type(merged_polygons) == shapely.MultiPolygon:
                merged_polygons = merged_polygons.geoms
            elif type(merged_polygons) == shapely.Polygon:
                merged_polygons = [merged_polygons]

            root_g = root.findall(".//{http://www.w3.org/2000/svg}g")[0]
            for polygon in merged_polygons:
                g = etree.SubElement(root, "g")
                path = etree.SubElement(g, "path")
                d = "M" + " L".join([",".join([str(o) for o in co]) for co in polygon.exterior.coords[0:-1]]) + " Z"
                for interior in polygon.interiors:
                    d += " M" + " L".join([",".join([str(o) for o in co]) for co in interior.coords[0:-1]]) + " Z"
                path.attrib["d"] = d
                g.set("class", " ".join(list(classes)))
                root_g.append(g)

    def move_projection_to_bottom(self, root):
        # https://stackoverflow.com/questions/36018627/sorting-child-elements-with-lxml-based-on-attribute-value
        group = root.find("{http://www.w3.org/2000/svg}g")
        # group[:] = sorted(group, key=lambda e : "projection" in e.get("class"))
        if group is not None:
            group[:] = reversed(group)

    def canonicalise_class_name(self, name):
        return re.sub("[^0-9a-zA-Z]+", "", name)

    def generate_annotation(self, context):
        if not self.cprops.has_annotation:
            return
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-annotation.svg")
        if os.path.isfile(svg_path) and self.props.should_use_annotation_cache:
            return svg_path

        elements = tool.Drawing.get_group_elements(tool.Drawing.get_drawing_group(self.camera_element))
        annotations = sorted(elements, key=lambda a: tool.Drawing.get_annotation_z_index(a))

        self.svg_writer.metadata = tool.Drawing.get_drawing_metadata(self.camera_element)
        self.svg_writer.create_blank_svg(svg_path).draw_annotations(annotations).save()

        return svg_path

    def get_scale(self):
        if self.camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
            self.human_scale, fraction = self.camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
        else:
            self.human_scale, fraction = self.camera.data.BIMCameraProperties.diagram_scale.split("|")

        if self.camera.data.BIMCameraProperties.is_nts:
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

    def get_classes(self, element, position, svg_writer):
        classes = [position, element.is_a()]
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if material:
            classes.append("material-{}".format(re.sub("[^0-9a-zA-Z]+", "", self.get_material_name(material))))
        classes.append("globalid-{}".format(element.GlobalId))
        for attribute in svg_writer.annotations["attributes"]:
            result = ifcopenshell.util.selector.get_element_value(element, attribute)
            if result:
                classes.append(
                    "{}-{}".format(re.sub("[^0-9a-zA-Z]+", "", attribute), re.sub("[^0-9a-zA-Z]+", "", result))
                )
        return classes

    def get_material_name(self, element):
        if hasattr(element, "Name") and element.Name:
            return element.Name
        elif hasattr(element, "LayerSetName") and element.LayerSetName:
            return element.LayerSetName
        return "mat-" + str(element.id())


class AddAnnotation(bpy.types.Operator, Operator):
    bl_idname = "bim.add_annotation"
    bl_label = "Add Annotation"
    bl_options = {"REGISTER", "UNDO"}
    object_type: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file() and context.scene.camera

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


class AddDrawingToSheet(bpy.types.Operator):
    bl_idname = "bim.add_drawing_to_sheet"
    bl_label = "Add Drawing To Sheet"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.DocProperties
        return props.drawings and props.sheets and context.scene.BIMProperties.data_dir

    def execute(self, context):
        props = context.scene.DocProperties
        active_drawing = props.drawings[props.active_drawing_index]
        active_sheet = props.sheets[props.active_sheet_index]
        drawing = tool.Ifc.get().by_id(active_drawing.ifc_definition_id)
        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)
        if not sheet.is_a("IfcDocumentInformation"):
            return {"FINISHED"}

        if tool.Ifc.get_schema() == "IFC2X3":
            references = sheet.DocumentReferences or []
        else:
            references = sheet.HasDocumentReferences or []

        has_drawing = False
        for reference in references:
            if tool.Ifc.get_schema() == "IFC2X3":
                element = [r for r in tool.Ifc.by_type("IfcRelAssociatesDocument") if r.RelatingDocument == reference][
                    0
                ].RelatedObjects[0]
            else:
                element = reference.DocumentRefForObjects[0].RelatedObjects[0]
            if element == drawing:
                has_drawing = True
                break

        if has_drawing:
            return {"FINISHED"}

        reference = tool.Ifc.run("document.add_reference", information=sheet)
        if tool.Ifc.get_schema() == "IFC2X3":
            attributes = {"ItemReference": str(len(sheet.DocumentReferences or []))}
        else:
            attributes = {"Identification": str(len(sheet.HasDocumentReferences or []))}
        tool.Ifc.run("document.edit_reference", reference=reference, attributes=attributes)
        tool.Ifc.run("document.assign_document", product=drawing, document=reference)
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.add_drawing(reference, drawing, sheet)

        tool.Drawing.import_sheets()
        return {"FINISHED"}


class RemoveDrawingFromSheet(bpy.types.Operator):
    bl_idname = "bim.remove_drawing_from_sheet"
    bl_label = "Remove Drawing From Sheet"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()

    def execute(self, context):
        reference = tool.Ifc.get().by_id(self.reference)
        sheet = tool.Drawing.get_reference_document(reference)

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.remove_drawing(reference, sheet)

        drawing = tool.Drawing.get_reference_element(reference)
        if drawing:
            tool.Ifc.run("document.unassign_document", product=drawing, document=reference)

        tool.Ifc.run("document.remove_reference", reference=reference)

        tool.Drawing.import_sheets()
        return {"FINISHED"}


class CreateSheets(bpy.types.Operator):
    bl_idname = "bim.create_sheets"
    bl_label = "Create Sheets"
    # TODO: check undo redo

    @classmethod
    def poll(cls, context):
        return context.scene.DocProperties.sheets and context.scene.BIMProperties.data_dir

    def execute(self, context):
        scene = context.scene
        props = scene.DocProperties
        active_sheet = props.sheets[props.active_sheet_index]
        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)

        if not sheet.is_a("IfcDocumentInformation"):
            return {"FINISHED"}

        name = os.path.splitext(os.path.basename(tool.Drawing.get_document_uri(sheet)))[0]
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = scene.BIMProperties.data_dir
        sheet_builder.build(sheet)

        svg2pdf_command = context.preferences.addons["blenderbim"].preferences.svg2pdf_command
        svg2dxf_command = context.preferences.addons["blenderbim"].preferences.svg2dxf_command

        if svg2pdf_command:
            path = os.path.join(scene.BIMProperties.data_dir, "build", name)
            svg = os.path.join(path, name + ".svg")
            pdf = os.path.join(path, name + ".pdf")
            # With great power comes great responsibility. Example:
            # [['inkscape', svg, '-o', pdf]]
            commands = eval(svg2pdf_command)
            for command in commands:
                subprocess.run(command)

        if svg2dxf_command:
            path = os.path.join(scene.BIMProperties.data_dir, "build", name)
            svg = os.path.join(path, name + ".svg")
            eps = os.path.join(path, name + ".eps")
            dxf = os.path.join(path, name + ".dxf")
            base = os.path.join(path, name)
            # With great power comes great responsibility. Example:
            # [['inkscape', svg, '-o', eps], ['pstoedit', '-dt', '-f', 'dxf:-polyaslines -mm', eps, dxf, '-psarg', '-dNOSAFER']]
            commands = eval(svg2dxf_command)
            for command in commands:
                subprocess.run(command)

        if svg2pdf_command:
            open_with_user_command(context.preferences.addons["blenderbim"].preferences.pdf_command, pdf)
        else:
            open_with_user_command(
                context.preferences.addons["blenderbim"].preferences.svg_command,
                os.path.join(scene.BIMProperties.data_dir, "build", name, name + ".svg"),
            )
        return {"FINISHED"}


class OpenView(bpy.types.Operator):
    bl_idname = "bim.open_view"
    bl_label = "Open View"
    view: bpy.props.StringProperty()

    def execute(self, context):
        open_with_user_command(
            context.preferences.addons["blenderbim"].preferences.svg_command,
            os.path.join(context.scene.BIMProperties.data_dir, "diagrams", self.view + ".svg"),
        )
        return {"FINISHED"}


class ActivateView(bpy.types.Operator):
    """
    Activates the selected drawing view
    """

    bl_idname = "bim.activate_view"
    bl_label = "Activate View"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Activates the selected drawing view"
    drawing: bpy.props.IntProperty()

    def execute(self, context):
        core.activate_drawing_view(tool.Ifc, tool.Drawing, drawing=tool.Ifc.get().by_id(self.drawing))
        bpy.context.scene.DocProperties.active_drawing_id = self.drawing
        bpy.ops.bim.activate_drawing_style()
        core.sync_references(tool.Ifc, tool.Collector, tool.Drawing, drawing=tool.Ifc.get().by_id(self.drawing))
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
    drawing: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_drawing(tool.Ifc, tool.Drawing, drawing=tool.Ifc.get().by_id(self.drawing))


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


class EditVectorStyle(bpy.types.Operator):
    bl_idname = "bim.edit_vector_style"
    bl_label = "Edit Vector Style"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        camera = context.scene.camera
        vector_style = context.scene.DocProperties.drawing_styles[
            camera.data.BIMCameraProperties.active_drawing_style_index
        ].vector_style
        bpy.data.texts.load(os.path.join(context.scene.BIMProperties.data_dir, "styles", vector_style + ".css"))
        return {"FINISHED"}


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
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)

    def _execute(self, context):
        filepath = self.filepath
        if self.use_relative_path:
            filepath = os.path.relpath(filepath, bpy.path.abspath("//"))
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


class AddScheduleToSheet(bpy.types.Operator):
    bl_idname = "bim.add_schedule_to_sheet"
    bl_label = "Add Schedule To Sheet"
    bl_options = {"REGISTER", "UNDO"}
    # TODO: check undo redo

    @classmethod
    def poll(cls, context):
        props = context.scene.DocProperties
        return props.schedules and props.sheets and context.scene.BIMProperties.data_dir

    def execute(self, context):
        props = context.scene.DocProperties
        active_schedule = props.schedules[props.active_schedule_index]
        active_sheet = props.sheets[props.active_sheet_index]
        schedule = tool.Ifc.get().by_id(active_schedule.ifc_definition_id)
        sheet = tool.Ifc.get().by_id(active_sheet.ifc_definition_id)
        if not sheet.is_a("IfcDocumentInformation"):
            return {"FINISHED"}

        if tool.Ifc.get_schema() == "IFC2X3":
            references = sheet.DocumentReferences or []
        else:
            references = sheet.HasDocumentReferences or []

        has_schedule = False
        for reference in references:
            if reference.Location == tool.Drawing.get_schedule_location(schedule):
                has_schedule = True
                break

        if has_schedule:
            return {"FINISHED"}

        reference = tool.Ifc.run("document.add_reference", information=sheet)
        if tool.Ifc.get_schema() == "IFC2X3":
            attributes = {"ItemReference": str(len(sheet.DocumentReferences or []))}
        else:
            attributes = {"Identification": str(len(sheet.HasDocumentReferences or []))}
        attributes["Location"] = tool.Drawing.get_schedule_location(schedule)
        tool.Ifc.run("document.edit_reference", reference=reference, attributes=attributes)

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.add_schedule(reference, schedule, sheet)

        tool.Drawing.import_sheets()
        return {"FINISHED"}


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

        props = context.active_object.BIMTextProperties

        row = self.layout.row(align=True)
        row.operator("bim.add_text_literal", icon="ADD", text="Add literal")

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
            blenderbim.bim.helper.draw_attributes(attributes, box)

            # a bit hacky way to align box alignment widget
            rows = [box.row(align=True) for i in range(3)]
            for i in range(9):
                if i % 3 == 0:
                    split = rows[i // 3].split(factor=0.1, align=True)
                    split.column()
                split.prop(literal_props, "box_alignment", text="", index=i)

            text_lines = ["Text box alignment:", literal_props.attributes["BoxAlignment"].string_value, ""]
            for i in range(3):
                split = rows[i].split(factor=0.1, align=False)
                split.column()
                split.label(text=text_lines[i])

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
        core.disable_editing_text(tool.Drawing, obj=context.active_object)

        # force update this object's font size for viewport display
        DecoratorData.data.pop(context.object.name, None)
        tool.Blender.update_viewport()


class AddTextLiteral(bpy.types.Operator):
    bl_idname = "bim.add_text_literal"
    bl_label = "Add text literal"
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
    bl_label = "Remove text literal"
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
    bl_label = "Enable Editing Text Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_assigned_product(tool.Drawing, obj=context.active_object)


class DisableEditingAssignedProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_assigned_product"
    bl_label = "Disable Editing Text Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_assigned_product(tool.Drawing, obj=context.active_object)


class LoadSheets(bpy.types.Operator, Operator):
    bl_idname = "bim.load_sheets"
    bl_label = "Load Sheets"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_sheets(tool.Drawing)


class DisableEditingSheets(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_sheets"
    bl_label = "Disable Editing Text Product"
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
    bl_label = "Disable Editing Text Product"
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
    bl_label = "Disable Editing Text Product"
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
        core.select_assigned_product(tool.Drawing)
