import os
import bpy
import json
import subprocess
import webbrowser
from blenderbim.bim.operator import open_with_user_command
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.group.data import Data as GroupData
from blenderbim.bim.module.pset.data import Data as PsetData

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
        ifcconvert_path = os.path.join(cwd, "..", "..", "..", "libs", "IfcConvert")
        subprocess.run(
            [
                ifcconvert_path,
                context.scene.BIMProperties.ifc_file,
                "-yv",
                context.scene.BIMProperties.ifc_file[0:-4] + ".svg",
                "--plan",
                "--model",
                "--section-height-from-storeys",
                "--section-height=1.2",
                "--door-arcs",
                "--print-space-names",
                "--print-space-areas",
                "--bounds=1024x1024",
                "--elevation-ref=DRAWING",
                "--svg-xmlns",
                "--svg-project",
                "--svg-poly",
                "--exclude",
                "entities",
                "IfcSpace",
                "IfcOpeningElement",
            ]
        )
        open_with_user_command(
            bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
            context.scene.BIMProperties.ifc_file[0:-4] + ".svg",
        )
        return {"FINISHED"}
