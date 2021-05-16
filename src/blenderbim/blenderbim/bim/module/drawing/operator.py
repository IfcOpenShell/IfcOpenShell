import os
import bpy
import json
import subprocess
import webbrowser
import ifcopenshell.util.representation
import blenderbim.bim.module.drawing.svgwriter as svgwriter
import blenderbim.bim.module.drawing.annotation as annotation
from mathutils import Vector, Matrix, Euler, geometry
from blenderbim.bim.operator import open_with_user_command
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.group.data import Data as GroupData
from ifcopenshell.api.pset.data import Data as PsetData

cwd = os.path.dirname(os.path.realpath(__file__))


class AddDrawing(bpy.types.Operator):
    bl_idname = "bim.add_drawing"
    bl_label = "Add Drawing"

    def execute(self, context):
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
        bpy.ops.bim.assign_group(product=camera.name, group=sorted(GroupData.groups.keys())[-1])
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
        base_svg = self.ifc_to_svg(context)
        annotation_svg = self.annotation_to_svg(context)
        svg_path = self.combine_svgs(context, base_svg, annotation_svg)
        open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.svg_command, svg_path)
        return {"FINISHED"}

    def combine_svgs(self, context, base, annotation):
        # Hacky :)
        svg_path = context.scene.BIMProperties.ifc_file[0:-4] + ".svg"
        with open(svg_path, "w") as outfile:
            with open(base) as infile:
                for line in infile:
                    if "</svg>" in line:
                        continue
                    outfile.write(line)
            with open(annotation) as infile:
                for i, line in enumerate(infile):
                    if i == 0 or i == 1:
                        continue
                    outfile.write(line)
        return svg_path

    def ifc_to_svg(self, context):
        svg_path = context.scene.BIMProperties.ifc_file[0:-4] + "-base.svg"
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
            ]
        )
        return svg_path

    def annotation_to_svg(self, context):
        camera = context.scene.camera

        if not (camera.type == "CAMERA" and camera.data.type == "ORTHO"):
            return

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
        svg_writer.output = context.scene.BIMProperties.ifc_file[0:-4] + "-annotation.svg"
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

        svg_writer.write()
        return svg_writer.output

    def is_landscape(self):
        return bpy.context.scene.render.resolution_x > bpy.context.scene.render.resolution_y


class AddAnnotation(bpy.types.Operator):
    bl_idname = "bim.add_annotation"
    bl_label = "Add Annotation"
    obj_name: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    def execute(self, context):
        if not bpy.context.scene.camera:
            return {"FINISHED"}
        subcontext = ifcopenshell.util.representation.get_context(
            IfcStore.get_file(), "Plan", "Annotation", context.scene.camera.data.BIMCameraProperties.target_view
        )
        if not subcontext:
            return {"FINISHED"}
        if self.data_type == "text":
            if bpy.context.selected_objects:
                for selected_object in bpy.context.selected_objects:
                    obj = annotation.Annotator.add_text(related_element=selected_object)
            else:
                obj = annotation.Annotator.add_text()
        else:
            obj = annotation.Annotator.get_annotation_obj(self.obj_name, self.data_type)
            if self.obj_name == "Break":
                obj = annotation.Annotator.add_plane_to_annotation(obj)
            else:
                obj = annotation.Annotator.add_line_to_annotation(obj)

        if not obj.BIMObjectProperties.ifc_definition_id:
            bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcAnnotation", context_id=subcontext.id())
        else:
            bpy.ops.bim.update_mesh_representation(obj=obj.name)

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}
