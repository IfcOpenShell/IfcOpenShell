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
import blenderbim.bim.module.drawing.svgwriter as svgwriter
import blenderbim.bim.module.drawing.annotation as annotation
import blenderbim.bim.module.drawing.sheeter as sheeter
import blenderbim.bim.module.drawing.scheduler as scheduler
import blenderbim.bim.module.drawing.helper as helper
from mathutils import Vector, Matrix, Euler, geometry
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


class AddDrawing(bpy.types.Operator):
    bl_idname = "bim.add_drawing"
    bl_label = "Add Drawing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        new = context.scene.DocProperties.drawings.add()
        new.name = "DRAWING {}".format(len(context.scene.DocProperties.drawings))
        if not bpy.data.collections.get("Views"):
            context.scene.collection.children.link(bpy.data.collections.new("Views"))
        views_collection = bpy.data.collections.get("Views")
        view_collection = bpy.data.collections.new("IfcGroup/" + new.name)
        views_collection.children.link(view_collection)
        camera = bpy.data.objects.new(new.name, bpy.data.cameras.new(new.name))
        camera.location = (0, 0, 1.7)  # The view shall be 1.7m above the origin
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = 50  # The default of 6m is too small
        camera.data.clip_end = 10  # A slightly more reasonable default
        if context.scene.unit_settings.system == "IMPERIAL":
            camera.data.BIMCameraProperties.diagram_scale = '1/8"=1\'-0"|1/96'
        else:
            camera.data.BIMCameraProperties.diagram_scale = "1:100|1/100"
        context.scene.camera = camera
        view_collection.objects.link(camera)
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].region_3d.view_perspective = "CAMERA"
        new.camera = camera
        bpy.ops.bim.assign_class(obj=camera.name, ifc_class="IfcAnnotation", predefined_type="DRAWING")
        bpy.ops.bim.activate_drawing_style()

        bpy.ops.bim.add_group()
        group = self.file.by_id(sorted(GroupData.groups.keys())[-1])
        ifcopenshell.api.run("group.edit_group", self.file, **{"group": group, "attributes": {"Name": new.name}})
        bpy.ops.bim.assign_group(product=camera.name, group=group.id())
        bpy.ops.bim.add_pset(obj=camera.name, obj_type="Object", pset_name="EPset_Drawing")
        pset_id = sorted(PsetData.products[camera.BIMObjectProperties.ifc_definition_id]["psets"])[-1]
        bpy.ops.bim.edit_pset(
            obj=camera.name,
            obj_type="Object",
            pset_id=pset_id,
            properties=json.dumps({"TargetView": "PLAN_VIEW", "Scale": "1/100"}),
        )
        return {"FINISHED"}


class CreateDrawing(bpy.types.Operator):
    bl_idname = "bim.create_drawing"
    bl_label = "Create Drawing"

    def execute(self, context):
        self.camera = context.scene.camera
        if (
            not (self.camera.type == "CAMERA" and self.camera.data.type == "ORTHO")
            or not self.camera.BIMObjectProperties.ifc_definition_id
        ):
            return
        self.file = IfcStore.get_file()
        self.time = None
        start = time.time()
        self.profile_code("Start drawing generation process")
        self.props = context.scene.DocProperties
        self.drawing_name = IfcStore.get_file().by_id(self.camera.BIMObjectProperties.ifc_definition_id).Name
        underlay_svg = self.generate_underlay(context)
        self.profile_code("Generate underlay")
        linework_svg = self.generate_linework(context)
        self.profile_code("Generate linework")
        annotation_svg = self.generate_annotation(context)
        self.profile_code("Generate annotation")
        svg_path = self.combine_svgs(context, underlay_svg, linework_svg, annotation_svg)
        self.profile_code("Combine SVG layers")
        open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.svg_command, svg_path)
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
                        elif "</style>" in line:
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
        bpy.context.scene.render.filepath = svg_path[0:-4] + ".png"
        drawing_style = bpy.context.scene.DocProperties.drawing_styles[
            self.camera.data.BIMCameraProperties.active_drawing_style_index
        ]

        if drawing_style.render_type == "DEFAULT":
            bpy.ops.render.render(write_still=True)
        else:
            previous_visibility = {}
            for obj in self.camera.users_collection[0].objects:
                previous_visibility[obj.name] = obj.hide_get()
                obj.hide_set(True)
            for obj in bpy.context.visible_objects:
                if (
                    (not obj.data and not obj.instance_collection)
                    or isinstance(obj.data, bpy.types.Camera)
                    or "IfcGrid/" in obj.name
                    or "IfcGridAxis/" in obj.name
                    or "IfcOpeningElement/" in obj.name
                ):
                    previous_visibility[obj.name] = obj.hide_get()
                    obj.hide_set(True)

            space = self.get_view_3d()
            previous_shading = space.shading.type
            previous_format = bpy.context.scene.render.image_settings.file_format
            space.shading.type = "RENDERED"
            bpy.context.scene.render.image_settings.file_format = "PNG"
            bpy.ops.render.opengl(write_still=True)
            space.shading.type = previous_shading
            bpy.context.scene.render.image_settings.file_format = previous_format

            for name, value in previous_visibility.items():
                bpy.data.objects[name].hide_set(value)

        svg_writer = svgwriter.SvgWriter()
        if self.camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
            human_scale, fraction = self.camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
        else:
            human_scale, fraction = self.camera.data.BIMCameraProperties.diagram_scale.split("|")
        if self.camera.data.BIMCameraProperties.is_nts:
            svg_writer.human_scale = "NTS"
        else:
            svg_writer.human_scale = human_scale
        render = bpy.context.scene.render
        if self.is_landscape():
            width = self.camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = self.camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x
        svg_writer.output = svg_path
        svg_writer.data_dir = bpy.context.scene.BIMProperties.data_dir
        svg_writer.vector_style = drawing_style.vector_style
        svg_writer.camera = self.camera
        svg_writer.camera_width = width
        svg_writer.camera_height = height
        svg_writer.camera_projection = tuple(self.camera.matrix_world.to_quaternion() @ Vector((0, 0, -1)))
        svg_writer.background_image = bpy.context.scene.render.filepath
        svg_writer.write("underlay")
        return svg_path

    def generate_linework(self, context):
        if not self.props.has_linework:
            return
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-linework.svg")
        if os.path.isfile(svg_path) and self.props.should_use_linework_cache:
            return svg_path
        # This is a work in progress. See #1153 and #1564.
        # Switch from old to new if you are testing v0.7.0
        self.generate_linework_old(context, svg_path)
        # self.generate_linework_new(svg_path)
        return svg_path

    def generate_linework_new(self, svg_path):
        settings = ifcopenshell.geom.settings(
            APPLY_DEFAULT_MATERIALS=True,
            DISABLE_TRIANGULATION=True,
            INCLUDE_CURVES=True,
            EXCLUDE_SOLIDS_AND_SURFACES=False,
        )
        buffer = ifcopenshell.geom.serializers.buffer()
        serialiser = ifcopenshell.geom.serializers.svg(buffer, settings)
        serialiser.setFile(self.file)
        serialiser.setElevationRef("DRAWING")
        serialiser.setUseNamespace(True)
        serialiser.setAlwaysProject(True)
        serialiser.setUseHlrPoly(True)
        serialiser.setWithoutStoreys(True)
        excluded_elements = []
        for ifc_class in ["IfcSpace", "IfcOpeningElement", "IfcDoor", "IfcWindow"]:
            excluded_elements += self.file.by_type(ifc_class)
        for element in ifcopenshell.geom.iterate(
            settings, self.file, multiprocessing.cpu_count(), exclude=excluded_elements
        ):
            serialiser.write(element)
        serialiser.finalize()
        with open(svg_path, "w") as svg:
            svg.write(buffer.get_value())

    def generate_linework_old(self, context, svg_path):
        ifcconvert_path = os.path.join(cwd, "..", "..", "..", "libs", "IfcConvert")
        subprocess.run(
            [
                ifcconvert_path,
                context.scene.BIMProperties.ifc_file,
                "-yv",
                svg_path,
                "--plan",
                "--model",
                "--elevation-ref=DRAWING",
                "--svg-xmlns",
                "--svg-project",
                "--svg-poly",
                "--svg-without-storeys",
                "--exclude",
                "entities",
                "IfcSpace",
                "IfcOpeningElement",
                "IfcDoor",
                "IfcWindow",
            ]
        )
        return svg_path

    def generate_annotation(self, context):
        if not self.props.has_annotation:
            return
        svg_path = os.path.join(context.scene.BIMProperties.data_dir, "cache", self.drawing_name + "-annotation.svg")
        if os.path.isfile(svg_path) and self.props.should_use_annotation_cache:
            return svg_path

        camera = self.camera
        svg_writer = svgwriter.SvgWriter()

        if camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
            human_scale, fraction = camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
        else:
            human_scale, fraction = camera.data.BIMCameraProperties.diagram_scale.split("|")

        numerator, denominator = fraction.split("/")

        if camera.data.BIMCameraProperties.is_nts:
            svg_writer.human_scale = "NTS"
        else:
            svg_writer.human_scale = human_scale

        drawing_style = bpy.context.scene.DocProperties.drawing_styles[
            camera.data.BIMCameraProperties.active_drawing_style_index
        ]

        render = bpy.context.scene.render
        if self.is_landscape():
            width = camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x

        svg_writer.scale = float(numerator) / float(denominator)
        svg_writer.output = svg_path
        svg_writer.data_dir = bpy.context.scene.BIMProperties.data_dir
        svg_writer.vector_style = drawing_style.vector_style
        svg_writer.camera = camera
        svg_writer.camera_width = width
        svg_writer.camera_height = height
        svg_writer.camera_projection = tuple(camera.matrix_world.to_quaternion() @ Vector((0, 0, -1)))

        for obj in camera.users_collection[0].objects:
            if "IfcGrid" in obj.name:
                svg_writer.annotations.setdefault("grid_objs", []).append(obj)
            elif obj.type == "CAMERA":
                continue

            if "IfcAnnotation/" not in obj.name:
                continue

            if "Leader" in obj.name:
                svg_writer.annotations["leader_obj"] = (obj, obj.data)
            elif "Stair" in obj.name:
                svg_writer.annotations["stair_obj"] = obj
            elif "Equal" in obj.name:
                svg_writer.annotations.setdefault("equal_objs", []).append(obj)
            elif "Dimension" in obj.name:
                svg_writer.annotations.setdefault("dimension_objs", []).append(obj)
            elif "Break" in obj.name:
                svg_writer.annotations["break_obj"] = obj
            elif "Hidden" in obj.name:
                svg_writer.annotations.setdefault("hidden_objs", []).append((obj, obj.data))
            elif "Solid" in obj.name:
                svg_writer.annotations.setdefault("solid_objs", []).append((obj, obj.data))
            elif "Plan Level" in obj.name:
                svg_writer.annotations["plan_level_obj"] = obj
            elif "Section Level" in obj.name:
                svg_writer.annotations["section_level_obj"] = obj
            elif obj.type == "FONT":
                svg_writer.annotations.setdefault("text_objs", []).append(obj)
            else:
                svg_writer.annotations.setdefault("misc_objs", []).append(obj)

        svg_writer.annotations["attributes"] = [a.name for a in drawing_style.attributes]
        svg_writer.annotations["annotation_objs"] = self.get_annotation(svg_writer)

        svg_writer.write("annotation")
        return svg_writer.output

    def is_landscape(self):
        return bpy.context.scene.render.resolution_x > bpy.context.scene.render.resolution_y

    def get_view_3d(self):
        for area in bpy.context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                return space

    def get_annotation(self, svg_writer):
        results = []
        x = svg_writer.camera_width / 2
        y = svg_writer.camera_height / 2
        z = 0.01
        camera_box = helper.BoundingBox(
            self.camera,
            [
                self.camera.matrix_world @ Vector((-x, -y, -z)),
                self.camera.matrix_world @ Vector((-x, -y, 0)),
                self.camera.matrix_world @ Vector((-x, y, 0)),
                self.camera.matrix_world @ Vector((-x, y, -z)),
                self.camera.matrix_world @ Vector((x, -y, -z)),
                self.camera.matrix_world @ Vector((x, -y, 0)),
                self.camera.matrix_world @ Vector((x, y, 0)),
                self.camera.matrix_world @ Vector((x, y, -z)),
            ],
        )
        # This should probably be also part of IfcConvert in the future, here is a Python prototype
        settings_2d = ifcopenshell.geom.settings()
        settings_2d.set(settings_2d.INCLUDE_CURVES, True)
        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            if obj == self.camera:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if element.is_a("IfcTypeProduct"):
                continue
            representation = ifcopenshell.util.representation.get_representation(
                element, "Plan", "Annotation", self.camera.data.BIMCameraProperties.target_view
            )
            if not representation:
                continue
            if not camera_box.intersect(helper.BoundingBox(obj)):
                continue
            shape = ifcopenshell.geom.create_shape(settings_2d, representation)
            geometry = shape
            e = geometry.edges
            v = geometry.verts
            results.append(
                {
                    "raw": element,
                    "classes": self.get_classes(element, "annotation", svg_writer),
                    "edges": [[e[i], e[i + 1]] for i in range(0, len(e), 2)],
                    "vertices": [obj.matrix_world @ Vector((v[i], v[i + 1], v[i + 2])) for i in range(0, len(v), 3)],
                }
            )
        return results

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


class AddAnnotation(bpy.types.Operator):
    bl_idname = "bim.add_annotation"
    bl_label = "Add Annotation"
    bl_options = {"REGISTER", "UNDO"}
    obj_name: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if not context.scene.camera:
            return {"FINISHED"}
        subcontext = ifcopenshell.util.representation.get_context(
            IfcStore.get_file(), "Plan", "Annotation", context.scene.camera.data.BIMCameraProperties.target_view
        )
        if not subcontext:
            return {"FINISHED"}
        if self.data_type == "text":
            if context.selected_objects:
                for selected_object in context.selected_objects:
                    obj = annotation.Annotator.add_text(context, related_element=selected_object)
            else:
                obj = annotation.Annotator.add_text(context)
        else:
            obj = annotation.Annotator.get_annotation_obj(self.obj_name, self.data_type, context)
            if self.obj_name == "Break":
                obj = annotation.Annotator.add_plane_to_annotation(obj, context)
            else:
                obj = annotation.Annotator.add_line_to_annotation(obj, context)

        if not obj.BIMObjectProperties.ifc_definition_id:
            bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcAnnotation", context_id=subcontext.id())
        else:
            bpy.ops.bim.update_representation(obj=obj.name)

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class AddSheet(bpy.types.Operator):
    bl_idname = "bim.add_sheet"
    bl_label = "Add Sheet"
    bl_options = {"REGISTER", "UNDO"}
    # TODO: check undo redo

    def execute(self, context):
        new = bpy.context.scene.DocProperties.sheets.add()
        new.name = "{} - SHEET".format(len(bpy.context.scene.DocProperties.sheets))
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.create(new.name, bpy.context.scene.DocProperties.titleblock)
        return {"FINISHED"}


class OpenSheet(bpy.types.Operator):
    bl_idname = "bim.open_sheet"
    bl_label = "Open Sheet"

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        open_with_user_command(
            bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
            os.path.join(
                bpy.context.scene.BIMProperties.data_dir, "sheets", props.sheets[props.active_sheet_index].name + ".svg"
            ),
        )
        return {"FINISHED"}


class AddDrawingToSheet(bpy.types.Operator):
    bl_idname = "bim.add_drawing_to_sheet"
    bl_label = "Add Drawing To Sheet"
    bl_options = {"REGISTER", "UNDO"}
    # TODO: check undo redo

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        try:
            sheet_builder.add_drawing(
                props.drawings[props.active_drawing_index].name, props.sheets[props.active_sheet_index].name
            )
        except:
            self.report({"ERROR"}, "Drawings need to be created before being added to a sheet")
        return {"FINISHED"}


class CreateSheets(bpy.types.Operator):
    bl_idname = "bim.create_sheets"
    bl_label = "Create Sheets"
    # TODO: check undo redo

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        name = props.sheets[props.active_sheet_index].name
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.build(name)

        svg2pdf_command = bpy.context.preferences.addons["blenderbim"].preferences.svg2pdf_command
        svg2dxf_command = bpy.context.preferences.addons["blenderbim"].preferences.svg2dxf_command

        if svg2pdf_command:
            path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "build", name)
            svg = os.path.join(path, name + ".svg")
            pdf = os.path.join(path, name + ".pdf")
            # With great power comes great responsibility. Example:
            # [['inkscape', svg, '-o', pdf]]
            commands = eval(svg2pdf_command)
            for command in commands:
                subprocess.run(command)

        if svg2dxf_command:
            path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "build", name)
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
            open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.pdf_command, pdf)
        else:
            open_with_user_command(
                bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
                os.path.join(bpy.context.scene.BIMProperties.data_dir, "build", name, name + ".svg"),
            )
        return {"FINISHED"}


class OpenView(bpy.types.Operator):
    bl_idname = "bim.open_view"
    bl_label = "Open View"
    view: bpy.props.StringProperty()

    def execute(self, context):
        open_with_user_command(
            bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
            os.path.join(bpy.context.scene.BIMProperties.data_dir, "diagrams", self.view + ".svg"),
        )
        return {"FINISHED"}


class OpenViewCamera(bpy.types.Operator):
    bl_idname = "bim.open_view_camera"
    bl_label = "Open View Camera"
    bl_options = {"REGISTER", "UNDO"}
    view_name: bpy.props.StringProperty()

    def execute(self, context):
        new_drawing_index = bpy.context.scene.DocProperties.drawings.find(self.view_name)
        bpy.context.scene.DocProperties.active_drawing_index = new_drawing_index
        drawing = bpy.context.scene.DocProperties.drawings[new_drawing_index]
        bpy.context.view_layer.objects.active = drawing.camera
        bpy.ops.object.select_all(action="DESELECT")
        drawing.camera.select_set(True)
        for area in bpy.context.screen.areas:
            if area.ui_type == "PROPERTIES":
                for space in area.spaces:
                    space.context = "DATA"
        return {"FINISHED"}


class ActivateView(bpy.types.Operator):
    bl_idname = "bim.activate_view"
    bl_label = "Activate View"
    bl_options = {"REGISTER", "UNDO"}
    drawing_index: bpy.props.IntProperty()

    def execute(self, context):
        camera = bpy.context.scene.DocProperties.drawings[self.drawing_index].camera
        if not camera:
            return {"FINISHED"}
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        is_local_view = area.spaces[0].local_view is not None
        if is_local_view:
            bpy.ops.view3d.localview()
            bpy.context.scene.camera = camera
            bpy.ops.view3d.localview()
        else:
            bpy.context.scene.camera = camera
        area.spaces[0].region_3d.view_perspective = "CAMERA"
        views_collection = bpy.data.collections.get("Views")
        for collection in views_collection.children:
            # We assume the project collection is at the top level
            for project_collection in bpy.context.view_layer.layer_collection.children:
                # We assume a convention that the 'Views' collection is directly
                # in the project collection
                if (
                    "Views" in project_collection.children
                    and collection.name in project_collection.children["Views"].children
                ):
                    project_collection.children["Views"].children[collection.name].hide_viewport = True
                    bpy.data.collections.get(collection.name).hide_render = True
        bpy.context.view_layer.layer_collection.children["Views"].children[
            camera.users_collection[0].name
        ].hide_viewport = False
        bpy.data.collections.get(camera.users_collection[0].name).hide_render = False
        bpy.ops.bim.activate_drawing_style()
        return {"FINISHED"}


class SelectDocIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_doc_ifc_file"
    bl_label = "Select Documentation IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.DocProperties.ifc_files[self.index].name = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class GenerateReferences(bpy.types.Operator):
    bl_idname = "bim.generate_references"
    bl_label = "Generate References"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.camera = bpy.context.scene.camera
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
        if self.camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
            human_scale, fraction = self.camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
        else:
            human_scale, fraction = self.camera.data.BIMCameraProperties.diagram_scale.split("|")
        numerator, denominator = fraction.split("/")
        scale = float(numerator) / float(denominator)
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
        for obj in bpy.context.scene.camera.users_collection[0].objects:
            if isinstance(obj.data, bpy.types.TextCurve):
                annotation.Annotator.resize_text(obj)
        return {"FINISHED"}


class AddVariable(bpy.types.Operator):
    bl_idname = "bim.add_variable"
    bl_label = "Add Variable"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.active_object.data.BIMTextProperties.variables.add()
        return {"FINISHED"}


class RemoveVariable(bpy.types.Operator):
    bl_idname = "bim.remove_variable"
    bl_label = "Remove Variable"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.data.BIMTextProperties.variables.remove(self.index)
        return {"FINISHED"}


class PropagateTextData(bpy.types.Operator):
    bl_idname = "bim.propagate_text_data"
    bl_label = "Propagate Text Data"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        source = bpy.context.active_object
        for obj in bpy.context.selected_objects:
            if obj == source:
                continue
            obj.data.body = source.data.body
            obj.data.align_x = source.data.align_x
            obj.data.align_y = source.data.align_y
            obj.data.BIMTextProperties.font_size = source.data.BIMTextProperties.font_size
            obj.data.BIMTextProperties.symbol = source.data.BIMTextProperties.symbol
            while len(obj.data.BIMTextProperties.variables) > 0:
                obj.data.BIMTextProperties.variables.remove(0)
            for variable in source.data.BIMTextProperties.variables:
                new_variable = obj.data.BIMTextProperties.variables.add()
                new_variable.name = variable.name
                new_variable.prop_key = variable.prop_key
        return {"FINISHED"}


class RemoveDrawing(bpy.types.Operator):
    bl_idname = "bim.remove_drawing"
    bl_label = "Remove Drawing"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        camera = props.drawings[self.index].camera
        collection = camera.users_collection[0]
        for obj in collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(collection, do_unlink=True)
        props.drawings.remove(self.index)
        return {"FINISHED"}


class AddDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.add_drawing_style"
    bl_label = "Add Drawing Style"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        new = bpy.context.scene.DocProperties.drawing_styles.add()
        new.name = "New Drawing Style"
        return {"FINISHED"}


class RemoveDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.remove_drawing_style"
    bl_label = "Remove Drawing Style"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.DocProperties.drawing_styles.remove(self.index)
        return {"FINISHED"}


class SaveDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.save_drawing_style"
    bl_label = "Save Drawing Style"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.StringProperty()
    # TODO: check undo redo

    def execute(self, context):
        space = self.get_view_3d()
        style = {
            "bpy.data.worlds[0].color": tuple(bpy.data.worlds[0].color),
            "bpy.context.scene.render.engine": bpy.context.scene.render.engine,
            "bpy.context.scene.render.film_transparent": bpy.context.scene.render.film_transparent,
            "bpy.context.scene.display.shading.show_object_outline": bpy.context.scene.display.shading.show_object_outline,
            "bpy.context.scene.display.shading.show_cavity": bpy.context.scene.display.shading.show_cavity,
            "bpy.context.scene.display.shading.cavity_type": bpy.context.scene.display.shading.cavity_type,
            "bpy.context.scene.display.shading.curvature_ridge_factor": bpy.context.scene.display.shading.curvature_ridge_factor,
            "bpy.context.scene.display.shading.curvature_valley_factor": bpy.context.scene.display.shading.curvature_valley_factor,
            "bpy.context.scene.view_settings.view_transform": bpy.context.scene.view_settings.view_transform,
            "bpy.context.scene.display.shading.light": bpy.context.scene.display.shading.light,
            "bpy.context.scene.display.shading.color_type": bpy.context.scene.display.shading.color_type,
            "bpy.context.scene.display.shading.single_color": tuple(bpy.context.scene.display.shading.single_color),
            "bpy.context.scene.display.shading.show_shadows": bpy.context.scene.display.shading.show_shadows,
            "bpy.context.scene.display.shading.shadow_intensity": bpy.context.scene.display.shading.shadow_intensity,
            "bpy.context.scene.display.light_direction": tuple(bpy.context.scene.display.light_direction),
            "bpy.context.scene.view_settings.use_curve_mapping": bpy.context.scene.view_settings.use_curve_mapping,
            "space.overlay.show_wireframes": space.overlay.show_wireframes,
            "space.overlay.wireframe_threshold": space.overlay.wireframe_threshold,
            "space.overlay.show_floor": space.overlay.show_floor,
            "space.overlay.show_axis_x": space.overlay.show_axis_x,
            "space.overlay.show_axis_y": space.overlay.show_axis_y,
            "space.overlay.show_axis_z": space.overlay.show_axis_z,
            "space.overlay.show_object_origins": space.overlay.show_object_origins,
            "space.overlay.show_relationship_lines": space.overlay.show_relationship_lines,
        }
        if self.index:
            index = int(self.index)
        else:
            index = bpy.context.active_object.data.BIMCameraProperties.active_drawing_style_index
        bpy.context.scene.DocProperties.drawing_styles[index].raster_style = json.dumps(style)
        return {"FINISHED"}

    def get_view_3d(self):
        for area in bpy.context.screen.areas:
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
        if context.scene.camera.data.BIMCameraProperties.active_drawing_style_index < len(
            bpy.context.scene.DocProperties.drawing_styles
        ):
            self.drawing_style = bpy.context.scene.DocProperties.drawing_styles[
                context.scene.camera.data.BIMCameraProperties.active_drawing_style_index
            ]
            self.set_raster_style()
            self.set_query()
        return {"FINISHED"}

    def set_raster_style(self):
        space = self.get_view_3d()
        style = json.loads(self.drawing_style.raster_style)
        bpy.data.worlds[0].color = style["bpy.data.worlds[0].color"]
        bpy.context.scene.render.engine = style["bpy.context.scene.render.engine"]
        bpy.context.scene.render.film_transparent = style["bpy.context.scene.render.film_transparent"]
        bpy.context.scene.display.shading.show_object_outline = style[
            "bpy.context.scene.display.shading.show_object_outline"
        ]
        bpy.context.scene.display.shading.show_cavity = style["bpy.context.scene.display.shading.show_cavity"]
        bpy.context.scene.display.shading.cavity_type = style["bpy.context.scene.display.shading.cavity_type"]
        bpy.context.scene.display.shading.curvature_ridge_factor = style[
            "bpy.context.scene.display.shading.curvature_ridge_factor"
        ]
        bpy.context.scene.display.shading.curvature_valley_factor = style[
            "bpy.context.scene.display.shading.curvature_valley_factor"
        ]
        bpy.context.scene.view_settings.view_transform = style["bpy.context.scene.view_settings.view_transform"]
        bpy.context.scene.display.shading.light = style["bpy.context.scene.display.shading.light"]
        bpy.context.scene.display.shading.color_type = style["bpy.context.scene.display.shading.color_type"]
        bpy.context.scene.display.shading.single_color = style["bpy.context.scene.display.shading.single_color"]
        bpy.context.scene.display.shading.show_shadows = style["bpy.context.scene.display.shading.show_shadows"]
        bpy.context.scene.display.shading.shadow_intensity = style["bpy.context.scene.display.shading.shadow_intensity"]
        bpy.context.scene.display.light_direction = style["bpy.context.scene.display.light_direction"]

        bpy.context.scene.view_settings.use_curve_mapping = style["bpy.context.scene.view_settings.use_curve_mapping"]
        space.overlay.show_wireframes = style["space.overlay.show_wireframes"]
        space.overlay.wireframe_threshold = style["space.overlay.wireframe_threshold"]
        space.overlay.show_floor = style["space.overlay.show_floor"]
        space.overlay.show_axis_x = style["space.overlay.show_axis_x"]
        space.overlay.show_axis_y = style["space.overlay.show_axis_y"]
        space.overlay.show_axis_z = style["space.overlay.show_axis_z"]
        space.overlay.show_object_origins = style["space.overlay.show_object_origins"]
        space.overlay.show_relationship_lines = style["space.overlay.show_relationship_lines"]

    def set_query(self):
        self.selector = ifcopenshell.util.selector.Selector()
        self.include_global_ids = []
        self.exclude_global_ids = []
        for ifc_file in bpy.context.scene.DocProperties.ifc_files:
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
            self.parse_filter_query("INCLUDE")
        if self.drawing_style.exclude_query:
            self.parse_filter_query("EXCLUDE")

    def parse_filter_query(self, mode):
        if mode == "INCLUDE":
            objects = bpy.context.scene.objects
        elif mode == "EXCLUDE":
            objects = bpy.context.visible_objects
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

    def get_view_3d(self):
        for area in bpy.context.screen.areas:
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


class RemoveSheet(bpy.types.Operator):
    bl_idname = "bim.remove_sheet"
    bl_label = "Remove Sheet"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        props.sheets.remove(self.index)
        return {"FINISHED"}


class AddSchedule(bpy.types.Operator):
    bl_idname = "bim.add_schedule"
    bl_label = "Add Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        new = bpy.context.scene.DocProperties.schedules.add()
        new.name = "SCHEDULE {}".format(len(bpy.context.scene.DocProperties.schedules))
        return {"FINISHED"}


class RemoveSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_schedule"
    bl_label = "Remove Schedule"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.DocProperties
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
        props = bpy.context.scene.DocProperties
        props.schedules[props.active_schedule_index].file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class BuildSchedule(bpy.types.Operator):
    bl_idname = "bim.build_schedule"
    bl_label = "Build Schedule"

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        schedule = props.schedules[props.active_schedule_index]
        schedule_creator = scheduler.Scheduler()
        outfile = os.path.join(bpy.context.scene.BIMProperties.data_dir, "schedules", schedule.name + ".svg")
        schedule_creator.schedule(schedule.file, outfile)
        open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.svg_command, outfile)
        return {"FINISHED"}


class AddScheduleToSheet(bpy.types.Operator):
    bl_idname = "bim.add_schedule_to_sheet"
    bl_label = "Add Schedule To Sheet"
    bl_options = {"REGISTER", "UNDO"}
    # TODO: check undo redo

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.add_schedule(
            props.schedules[props.active_schedule_index].name, props.sheets[props.active_sheet_index].name
        )
        return {"FINISHED"}


class AddDrawingStyleAttribute(bpy.types.Operator):
    bl_idname = "bim.add_drawing_style_attribute"
    bl_label = "Add Drawing Style Attribute"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = bpy.context.scene.camera.data.BIMCameraProperties
        context.scene.DocProperties.drawing_styles[props.active_drawing_style_index].attributes.add()
        return {"FINISHED"}


class RemoveDrawingStyleAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_drawing_style_attribute"
    bl_label = "Remove Drawing Style Attribute"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.camera.data.BIMCameraProperties
        context.scene.DocProperties.drawing_styles[props.active_drawing_style_index].attributes.remove(self.index)
        return {"FINISHED"}


class RefreshDrawingList(bpy.types.Operator):
    bl_idname = "bim.refresh_drawing_list"
    bl_label = "Refresh Drawing List"

    def execute(self, context):
        while len(bpy.context.scene.DocProperties.drawings) > 0:
            bpy.context.scene.DocProperties.drawings.remove(0)
        for obj in bpy.context.scene.objects:
            if not isinstance(obj.data, bpy.types.Camera):
                continue
            if "IfcAnnotation/" in obj.name:
                new = bpy.context.scene.DocProperties.drawings.add()
                new.name = "/".join(obj.name.split("/")[1:])
                new.camera = obj
        return {"FINISHED"}


class CleanWireframes(bpy.types.Operator):
    bl_idname = "bim.clean_wireframes"
    bl_label = "Clean Wireframes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        objects = bpy.data.objects
        if bpy.context.selected_objects:
            objects = bpy.context.selected_objects
        for obj in objects:
            if not isinstance(obj.data, bpy.types.Mesh):
                continue
            if "EDGE_SPLIT" not in [m.type for m in obj.modifiers]:
                obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
        return {"FINISHED"}


class CopyGrid(bpy.types.Operator):
    bl_idname = "bim.add_grid"
    bl_label = "Add Grid"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        proj_coll = helper.get_project_collection(context.scene)
        view_coll, camera = helper.get_active_drawing(context.scene)
        if view_coll is None:
            return {"CANCELLED"}
        is_ortho = camera.data.type == "ORTHO"
        bounds = helper.ortho_view_frame(camera.data) if is_ortho else None
        clipping = is_ortho and camera.data.BIMCameraProperties.target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW")
        elevating = is_ortho and camera.data.BIMCameraProperties.target_view in ("ELEVATION_VIEW", "SECTION_VIEW")

        def grep(coll):
            return [obj for obj in coll.all_objects if obj.name.startswith("IfcGridAxis")]

        def clone(src):
            dst = src.copy()
            dst.data = dst.data.copy()
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

        grid = [localize(*disassemble(clone(obj))) for obj in grep(proj_coll)]

        if clipping:
            grid = [(obj, clip(mesh)) for obj, mesh in grid]
        elif elevating:
            grid = [(obj, elev(mesh)) for obj, mesh in grid]

        for obj, mesh in grid:
            if mesh is not None:
                view_coll.objects.link(assemble(obj, mesh))

        return {"FINISHED"}


class AddSectionsAnnotations(bpy.types.Operator):
    bl_idname = "bim.add_sections_annotations"
    bl_label = "Add Sections"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        view_coll, camera = helper.get_active_drawing(scene)
        is_ortho = camera.data.type == "ORTHO"
        if not is_ortho:
            return {"CANCELLED"}
        bounds = helper.ortho_view_frame(camera.data) if is_ortho else None

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
