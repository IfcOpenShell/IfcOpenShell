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
import blenderbim.bim.export_ifc
from lxml import etree
from mathutils import Vector, Matrix, Euler, geometry
from blenderbim.bim.module.drawing.prop import RasterStyleProperty
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.group.data import Data as GroupData
from ifcopenshell.api.pset.data import Data as PsetData

cwd = os.path.dirname(os.path.realpath(__file__))


def open_with_user_command(user_command, path):
    if user_command:
        commands = eval(user_command)
        for command in commands:
            subprocess.run(command)
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


class CreateDrawing(bpy.types.Operator):
    """Creates a svg drawing

    Only available if :
    - IFC file is created
    - Camera is in Orthographic mode
    """

    bl_idname = "bim.create_drawing"
    bl_label = "Create Drawing"

    @classmethod
    def poll(cls, context):
        camera = context.scene.camera
        return (
            IfcStore.get_file()
            and camera
            and camera.type == "CAMERA"
            and camera.data.type == "ORTHO"
            and camera.BIMObjectProperties.ifc_definition_id
        )

    def execute(self, context):
        self.camera = context.scene.camera
        self.camera_element = tool.Ifc.get_entity(self.camera)
        self.file = IfcStore.get_file()
        self.time = None
        start = time.time()
        self.profile_code("Start drawing generation process")
        self.props = context.scene.DocProperties
        self.drawing_name = self.file.by_id(self.camera.BIMObjectProperties.ifc_definition_id).Name
        self.get_scale()
        if self.camera.data.BIMCameraProperties.update_representation(self.camera):
            bpy.ops.bim.update_representation(obj=self.camera.name, ifc_representation_class="")
        underlay_svg = self.generate_underlay(context)
        self.profile_code("Generate underlay")
        linework_svg = self.generate_linework(context)
        self.profile_code("Generate linework")
        annotation_svg = self.generate_annotation(context)
        self.profile_code("Generate annotation")
        svg_path = self.combine_svgs(context, underlay_svg, linework_svg, annotation_svg)
        self.profile_code("Combine SVG layers")
        open_with_user_command(context.preferences.addons["blenderbim"].preferences.svg_command, svg_path)
        print("Total Time: {:.2f}".format(time.time() - start))
        return {"FINISHED"}

    def profile_code(self, message):
        if not self.time:
            self.time = time.time()
        print("{} :: {:.2f}".format(message, time.time() - self.time))
        self.time = time.time()

    def combine_svgs(self, context, underlay, linework, annotation):
        # Hacky :)
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "diagrams", self.drawing_name + ".svg")
        with open(svg_path, "w") as outfile:
            has_boilerplate = False
            if underlay:
                with open(underlay) as infile:
                    for line in infile:
                        if "<svg " in line:
                            line = line.replace('">', '" xmlns:ifc="http://www.ifcopenshell.org/ns">')
                        if "</svg>" in line:
                            continue
                        outfile.write(line)
                shutil.copyfile(underlay[0:-4] + ".png", svg_path[0:-4] + "-underlay.png")
                has_boilerplate = True
            if linework:
                with open(linework) as infile:
                    should_skip = False
                    for i, line in enumerate(infile):
                        if has_boilerplate and i == 0:
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
                has_boilerplate = True
            if annotation:
                with open(annotation) as infile:
                    for i, line in enumerate(infile):
                        if has_boilerplate and i in [0, 1]:
                            continue
                        if "</svg>" in line:
                            continue
                        outfile.write(line)
            outfile.write("</svg>")
        return svg_path

    def generate_underlay(self, context):
        if not self.props.has_underlay:
            return
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-underlay.svg")
        context.scene.render.filepath = svg_path[0:-4] + ".png"
        drawing_style = context.scene.DocProperties.drawing_styles[
            self.camera.data.BIMCameraProperties.active_drawing_style_index
        ]

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

        svg_writer = svgwriter.SvgWriter()
        render = context.scene.render
        if self.is_landscape(render):
            width = self.camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = self.camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x
        svg_writer.human_scale = self.human_scale
        svg_writer.scale = self.scale
        svg_writer.output = svg_path
        svg_writer.data_dir = context.scene.BIMProperties.data_dir
        svg_writer.vector_style = drawing_style.vector_style
        svg_writer.camera = self.camera
        svg_writer.camera_width = width
        svg_writer.camera_height = height
        svg_writer.camera_projection = tuple(self.camera.matrix_world.to_quaternion() @ Vector((0, 0, -1)))
        svg_writer.background_image = context.scene.render.filepath
        svg_writer.write("underlay")
        return svg_path

    def generate_linework(self, context):
        if not self.props.has_linework:
            return
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-linework.svg")
        if os.path.isfile(svg_path) and self.props.should_use_linework_cache:
            return svg_path

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

            # Get all representation contexts to see what we're dealing with
            # A drawing prioritises a target view context first, followed by a body context as a fallback
            body_contexts = []
            target_view_contexts = []
            target_view = ifcopenshell.util.element.get_psets(self.camera_element)["EPset_Drawing"]["TargetView"]
            for rep_context in ifc.by_type("IfcGeometricRepresentationContext"):
                if rep_context.is_a("IfcGeometricRepresentationSubContext"):
                    if rep_context.TargetView == target_view:
                        target_view_contexts.append(rep_context.id())
                        continue
                if rep_context.ContextIdentifier in ["Body", "Facetation"]:
                    body_contexts.append(rep_context.id())
                    continue
                if rep_context.is_a() == "IfcGeometricRepresentationContext" and rep_context.ContextType == "Model":
                    body_contexts.append(rep_context.id())
                    continue

            elements = set(ifc.by_type("IfcElement")) - set(ifc.by_type("IfcOpeningElement"))

            self.setup_serialiser(ifc)
            cache_settings = ifcopenshell.geom.settings(DISABLE_TRIANGULATION=True)
            cache = IfcStore.get_cache()
            [cache.remove(guid) for guid in invalidated_guids]

            if target_view_contexts and elements:
                geom_settings = ifcopenshell.geom.settings(DISABLE_TRIANGULATION=True, INCLUDE_CURVES=True)
                geom_settings.set_context_ids(target_view_contexts)
                it = ifcopenshell.geom.iterator(geom_settings, ifc, multiprocessing.cpu_count(), include=elements)
                it.set_cache(cache)
                processed = set()
                for elem in self.yield_from_iterator(it):
                    processed.add(ifc.by_id(elem.id))
                    self.serialiser.write(elem)
                elements -= processed

            if body_contexts and elements:
                geom_settings = ifcopenshell.geom.settings(
                    DISABLE_TRIANGULATION=True,
                )
                geom_settings.set_context_ids(body_contexts)
                it = ifcopenshell.geom.iterator(geom_settings, ifc, multiprocessing.cpu_count(), include=elements)
                it.set_cache(cache)
                for elem in self.yield_from_iterator(it):
                    self.serialiser.write(elem)

            geom_settings = ifcopenshell.geom.settings(
                DISABLE_TRIANGULATION=True,
            )
            it = ifcopenshell.geom.iterator(geom_settings, ifc, include=[self.camera_element])
            for elem in self.yield_from_iterator(it):
                self.serialiser.write(elem)

        self.serialiser.finalize()
        results = self.svg_buffer.get_value()

        root = etree.fromstring(results)
        self.enrich_linework_with_metadata(root)
        self.move_projection_to_bottom(root)
        with open(svg_path, "wb") as svg:
            svg.write(etree.tostring(root))

        return svg_path

    def setup_serialiser(self, ifc):
        self.svg_settings = ifcopenshell.geom.settings(DISABLE_TRIANGULATION=True, INCLUDE_CURVES=True)
        self.svg_buffer = ifcopenshell.geom.serializers.buffer()
        self.serialiser = ifcopenshell.geom.serializers.svg(self.svg_buffer, self.svg_settings)
        self.serialiser.setFile(ifc)
        self.serialiser.setWithoutStoreys(True)
        self.serialiser.setPolygonal(True)
        self.serialiser.setUseHlrPoly(True)
        self.serialiser.setProfileThreshold(64)
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

    def enrich_linework_with_metadata(self, root):
        ifc = tool.Ifc.get()
        for el in root.findall(".//{http://www.w3.org/2000/svg}g[@{http://www.ifcopenshell.org/ns}guid]"):
            classes = ["cut"]
            try:
                element = ifc.by_guid(el.get("{http://www.ifcopenshell.org/ns}guid"))
            except:
                # See #1861 - freshly created guids cannot be extracted unfortunately
                continue
            material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
            if material:
                if material.is_a("IfcMaterialLayerSet"):
                    name = material.LayerSetName or "null"
                else:
                    name = getattr(material, "Name", "null") or "null"
                name = self.canonicalise_class_name(name)
                classes.append(f"material-{name}")
            el.set("class", (el.get("class", "") + " " + " ".join(classes)).strip())

    def move_projection_to_bottom(self, root):
        # https://stackoverflow.com/questions/36018627/sorting-child-elements-with-lxml-based-on-attribute-value
        group = root.find("{http://www.w3.org/2000/svg}g")
        # group[:] = sorted(group, key=lambda e : "projection" in e.get("class"))
        if group:
            group[:] = reversed(group)

    def canonicalise_class_name(self, name):
        return re.sub("[^0-9a-zA-Z]+", "", name)

    def generate_annotation(self, context):
        if not self.props.has_annotation:
            return
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-annotation.svg")
        if os.path.isfile(svg_path) and self.props.should_use_annotation_cache:
            return svg_path

        camera = self.camera
        svg_writer = svgwriter.SvgWriter()

        drawing_style = context.scene.DocProperties.drawing_styles[
            camera.data.BIMCameraProperties.active_drawing_style_index
        ]

        render = context.scene.render
        if self.is_landscape(render):
            width = camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x

        svg_writer.human_scale = self.human_scale
        svg_writer.scale = self.scale
        svg_writer.output = svg_path
        svg_writer.data_dir = context.scene.BIMProperties.data_dir
        svg_writer.vector_style = drawing_style.vector_style
        svg_writer.camera = camera
        svg_writer.camera_width = width
        svg_writer.camera_height = height
        svg_writer.camera_projection = tuple(camera.matrix_world.to_quaternion() @ Vector((0, 0, -1)))

        for obj in camera.users_collection[0].objects:
            if "IfcAnnotation/" not in obj.name:
                continue
            element = tool.Ifc.get_entity(obj)
            if element.ObjectType == "GRID":
                svg_writer.annotations.setdefault("grid_objs", []).append(obj)
            elif obj.type == "CAMERA":
                continue
            elif element.ObjectType == "TEXT_LEADER":
                svg_writer.annotations.setdefault("leader_objs", []).append(obj)
            elif element.ObjectType == "STAIR_ARROW":
                svg_writer.annotations["stair_obj"] = obj
            elif element.ObjectType == "EQUAL_DIMENSION":
                svg_writer.annotations.setdefault("equal_objs", []).append(obj)
            elif element.ObjectType == "DIMENSION":
                svg_writer.annotations.setdefault("dimension_objs", []).append(obj)
            elif element.ObjectType == "BREAKLINE":
                svg_writer.annotations["break_obj"] = obj
            elif element.ObjectType == "HIDDEN_LINE":
                svg_writer.annotations.setdefault("hidden_objs", []).append((obj, obj.data))
            elif element.ObjectType == "SOLID_LINE":
                svg_writer.annotations.setdefault("solid_objs", []).append((obj, obj.data))
            elif element.ObjectType == "PLAN_LEVEL":
                svg_writer.annotations.setdefault("plan_level_objs", []).append(obj)
            elif element.ObjectType == "SECTION_LEVEL":
                svg_writer.annotations["section_level_obj"] = obj
            elif element.ObjectType == "TEXT":
                svg_writer.annotations.setdefault("text_objs", []).append(obj)
            elif element.ObjectType == "MISC":
                svg_writer.annotations.setdefault("misc_objs", []).append(obj)

        svg_writer.annotations["attributes"] = [a.name for a in drawing_style.attributes]
        # TODO: This was the old 2D annotation box checking system, prepare to deprecate
        svg_writer.annotations["annotation_objs"] = []

        svg_writer.write("annotation")
        return svg_writer.output

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
            result = self.selector.get_element_value(element, attribute)
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
            return
        core.add_annotation(tool.Ifc, tool.Collector, tool.Drawing, drawing=drawing, object_type=self.object_type)


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
    # TODO: check undo redo

    @classmethod
    def poll(cls, context):
        props = context.scene.DocProperties
        return props.drawings and props.sheets and context.scene.BIMProperties.data_dir

    def execute(self, context):
        props = context.scene.DocProperties
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.add_drawing(props.active_drawing.name, props.active_sheet.name)
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
        name = props.active_sheet.name
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = scene.BIMProperties.data_dir
        sheet_builder.build(name)

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
    bl_idname = "bim.activate_view"
    bl_label = "Activate View"
    bl_options = {"REGISTER", "UNDO"}
    drawing: bpy.props.IntProperty()

    def execute(self, context):
        camera = tool.Ifc.get_object(tool.Ifc.get().by_id(self.drawing))
        if not camera:
            return {"FINISHED"}
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        is_local_view = area.spaces[0].local_view is not None
        if is_local_view:
            bpy.ops.view3d.localview()
            context.scene.camera = camera
            bpy.ops.view3d.localview()
        else:
            context.scene.camera = camera
        area.spaces[0].region_3d.view_perspective = "CAMERA"
        views_collection = bpy.data.collections.get("Views")
        for collection in views_collection.children:
            # We assume the project collection is at the top level
            for project_collection in context.view_layer.layer_collection.children:
                # We assume a convention that the 'Views' collection is directly
                # in the project collection
                if (
                    "Views" in project_collection.children
                    and collection.name in project_collection.children["Views"].children
                ):
                    project_collection.children["Views"].children[collection.name].hide_viewport = True
                    bpy.data.collections.get(collection.name).hide_render = True

                    project_collection.children["Views"].children[camera.users_collection[0].name].hide_viewport = False
        bpy.data.collections.get(camera.users_collection[0].name).hide_render = False
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


class GenerateReferences(bpy.types.Operator):
    bl_idname = "bim.generate_references"
    bl_label = "Generate References"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.camera = context.scene.camera
        self.filter_potential_references()
        if self.camera.data.BIMCameraProperties.target_view == "PLAN_VIEW":
            self.generate_grids()
        if self.camera.data.BIMCameraProperties.target_view == "ELEVATION_VIEW":
            self.generate_grids()
            self.generate_levels(context)
        if self.camera.data.BIMCameraProperties.target_view == "SECTION_VIEW":
            self.generate_grids()
            self.generate_levels(context)
        return {"FINISHED"}

    def filter_potential_references(self):
        for name in ["grids", "levels"]:
            setattr(self, name, [])
        for obj in bpy.data.objects:
            if "IfcGridAxis/" in obj.name:
                self.grids.append(obj)
            if "IfcBuildingStorey/" in obj.name:
                self.levels.append(obj)

    def generate_grids(self):
        # TODO
        pass

    def generate_levels(self, context):
        if self.camera.data.BIMCameraProperties.raster_x > self.camera.data.BIMCameraProperties.raster_y:
            width = self.camera.data.ortho_scale
            height = (
                width / self.camera.data.BIMCameraProperties.raster_x * self.camera.data.BIMCameraProperties.raster_y
            )
        else:
            height = self.camera.data.ortho_scale
            width = (
                height / self.camera.data.BIMCameraProperties.raster_y * self.camera.data.BIMCameraProperties.raster_x
            )
        level_obj = annotation.Annotator.get_annotation_obj("Section Level", "curve", context)

        width_in_mm = width * 1000
        real_world_width_in_mm = width_in_mm * scale
        offset_in_mm = 20
        offset_percentage = offset_in_mm / real_world_width_in_mm

        for obj in self.levels:
            projection = self.project_point_onto_camera(obj.location)
            co1 = self.camera.matrix_world @ Vector((width / 2 - (offset_percentage * width), projection[1], -1))
            co2 = self.camera.matrix_world @ Vector((-(width / 2), projection[1], -1))
            annotation.Annotator.add_line_to_annotation(level_obj, context, co1, co2)

    def project_point_onto_camera(self, point):
        projection = self.camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        return self.camera.matrix_world.inverted() @ geometry.intersect_line_plane(
            point.xyz, point.xyz - projection, self.camera.location, projection
        )


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
    index: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.DocProperties
        drawing = tool.Ifc.get().by_id(props.drawings[self.index].ifc_definition_id)
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
        self.selector = ifcopenshell.util.selector.Selector()
        self.include_global_ids = []
        self.exclude_global_ids = []
        for ifc_file in context.scene.DocProperties.ifc_files:
            try:
                ifc = ifcopenshell.open(ifc_file.name)
            except:
                continue
            if self.drawing_style.include_query:
                results = self.selector.parse(ifc, self.drawing_style.include_query)
                self.include_global_ids.extend([e.GlobalId for e in results])
            if self.drawing_style.exclude_query:
                results = self.selector.parse(ifc, self.drawing_style.exclude_query)
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
    index: bpy.props.IntProperty()

    def _execute(self, context):
        self.props = context.scene.DocProperties
        sheet = tool.Ifc.get().by_id(self.props.sheets[self.props.active_sheet_index].ifc_definition_id)
        core.remove_sheet(tool.Ifc, tool.Drawing, sheet=sheet)


class AddSchedule(bpy.types.Operator):
    bl_idname = "bim.add_schedule"
    bl_label = "Add Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        new = context.scene.DocProperties.schedules.add()
        new.name = "SCHEDULE {}".format(len(context.scene.DocProperties.schedules))
        return {"FINISHED"}


class RemoveSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_schedule"
    bl_label = "Remove Schedule"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.DocProperties
        props.schedules.remove(self.index)
        return {"FINISHED"}


class SelectScheduleFile(bpy.types.Operator):
    bl_idname = "bim.select_schedule_file"
    bl_label = "Select Documentation IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ods", options={"HIDDEN"})
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.DocProperties
        props.active_schedule.file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class BuildSchedule(bpy.types.Operator):
    bl_idname = "bim.build_schedule"
    bl_label = "Build Schedule"

    @classmethod
    def poll(cls, context):
        return context.scene.DocProperties.active_schedule.file

    def execute(self, context):
        props = context.scene.DocProperties
        schedule = props.active_schedule
        schedule_creator = scheduler.Scheduler()
        outfile = os.path.join(context.scene.BIMProperties.data_dir, "schedules", schedule.name + ".svg")
        schedule_creator.schedule(schedule.file, outfile)
        open_with_user_command(context.preferences.addons["blenderbim"].preferences.svg_command, outfile)
        return {"FINISHED"}


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
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = context.scene.BIMProperties.data_dir
        sheet_builder.add_schedule(props.active_schedule.name, props.active_sheet.name)
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


class CopyGrid(bpy.types.Operator):
    bl_idname = "bim.add_grid"
    bl_label = "Add Grid"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return helper.get_active_drawing(context.scene)[0] is not None

    def execute(self, context):
        drawing = tool.Ifc.get_entity(context.scene.camera)
        target_view = tool.Drawing.get_drawing_target_view(drawing)
        subcontext = ifcopenshell.util.representation.get_context(
            IfcStore.get_file(), "Plan", "Annotation", target_view
        )
        if not subcontext:
            return {"FINISHED"}

        proj_coll = helper.get_project_collection(context.scene)
        view_coll, camera = helper.get_active_drawing(context.scene)
        is_ortho = camera.data.type == "ORTHO"
        bounds = helper.ortho_view_frame(camera.data) if is_ortho else None
        clipping = is_ortho and target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW")
        elevating = is_ortho and target_view in ("ELEVATION_VIEW", "SECTION_VIEW")

        def grep(coll):
            results = []
            for obj in coll.all_objects:
                element = tool.Ifc.get_entity(obj)
                if element and element.is_a("IfcAnnotation") and element.ObjectType == "GRID":
                    results.append(obj)
            return results

        def clone(src):
            dst = src.copy()
            dst.data = dst.data.copy()
            dst.name = dst.name.replace("IfcGridAxis/", "")
            dst.BIMObjectProperties.ifc_definition_id = 0
            dst.data.BIMMeshProperties.ifc_definition_id = 0
            return dst

        def disassemble(obj):
            mesh = bmesh.new()
            mesh.verts.ensure_lookup_table()
            mesh.from_mesh(obj.data)
            return obj, mesh

        def assemble(obj, mesh):
            mesh.to_mesh(obj.data)
            return obj

        def localize(obj, mesh):
            # convert to camera coords
            mesh.transform(camera.matrix_world.inverted() @ obj.matrix_world)
            obj.matrix_world = camera.matrix_world
            return obj, mesh

        def clip(mesh):
            # clip segment against camera view bounds
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        def elev(mesh):
            # put camera-perpendicular segments vertically
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.elevate_segment(bounds, points)
            if points is None:
                return None
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        for obj in grep(view_coll):
            view_coll.objects.unlink(obj)

        grids = []
        for element in tool.Ifc.get().by_type("IfcGridAxis"):
            obj = tool.Ifc.get_object(element)
            if not obj:
                continue
            grids.append((*localize(*disassemble(clone(obj))), element))

        if clipping:
            grids = [(obj, clip(mesh), element) for obj, mesh, element in grids]
        elif elevating:
            grids = [(obj, elev(mesh), element) for obj, mesh, element in grids]

        for obj, mesh, element in grids:
            if mesh is not None:
                view_coll.objects.link(assemble(obj, mesh))
                bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcAnnotation", context_id=subcontext.id())
                annotation = tool.Ifc.get_entity(obj)
                annotation.Name = element.AxisTag
                annotation.ObjectType = "GRID"
        return {"FINISHED"}


class AddSectionsAnnotations(bpy.types.Operator):
    bl_idname = "bim.add_sections_annotations"
    bl_label = "Add Sections"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        camera = helper.get_active_drawing(context.scene)[1]
        return camera and camera.data.type == "ORTHO"

    def execute(self, context):
        scene = context.scene
        view_coll, camera = helper.get_active_drawing(scene)
        bounds = helper.ortho_view_frame(camera.data)

        drawings = [
            d
            for d in scene.DocProperties.drawings
            if (
                d.camera is not camera
                and d.camera.data.type == "ORTHO"
                and d.camera.data.BIMCameraProperties.target_view == "SECTION_VIEW"
            )
        ]

        def sideview(cam):
            # leftmost and righmost points of camera view area, local coords
            xmin, xmax, _, _, _, _ = helper.ortho_view_frame(cam.data, margin=0)
            proj = camera.matrix_world.inverted() @ cam.matrix_world
            p_l = proj @ Vector((xmin, 0, 0))
            p_r = proj @ Vector((xmax, 0, 0))
            return helper.clip_segment(bounds, (p_l, p_r))

        def annotation(drawing, points):
            # object with path geometry
            name = drawing.name
            curve = bpy.data.curves.new(f"Section/{name}", "CURVE")
            spline = curve.splines.new("POLY")  # has 1 initial point
            spline.points.add(1)
            p1, p2 = points
            z = bounds[4] - 1e-5  # zmin
            spline.points[0].co = (p1.x, p1.y, z, 1)
            spline.points[1].co = (p2.x, p2.y, z, 1)
            obj = bpy.data.objects.new(f"IfcAnnotation/Section/{name}", curve)
            obj.matrix_world = camera.matrix_world
            return obj

        for d in drawings:
            points = sideview(d.camera)
            if points is None:
                continue
            obj = annotation(d, points)
            view_coll.objects.link(obj)

        return {"FINISHED"}


class EditText(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_text"
    bl_label = "Edit Text"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_text(tool.Ifc, tool.Drawing, obj=context.active_object)


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


class EditTextProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_text_product"
    bl_label = "Edit Text Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        product = None
        if context.active_object.BIMTextProperties.relating_product:
            product = tool.Ifc.get_entity(context.active_object.BIMTextProperties.relating_product)
        core.edit_text_product(tool.Ifc, tool.Drawing, obj=context.active_object, product=product)


class EnableEditingTextProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_text_product"
    bl_label = "Enable Editing Text Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_text_product(tool.Drawing, obj=context.active_object)


class DisableEditingTextProduct(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_text_product"
    bl_label = "Disable Editing Text Product"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_text_product(tool.Drawing, obj=context.active_object)


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
