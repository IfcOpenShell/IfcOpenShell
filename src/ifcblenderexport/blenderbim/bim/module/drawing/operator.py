import bpy
from blenderbim.bim.ifc import IfcStore


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
        bpy.ops.bim.assign_class(obj=camera.name, ifc_class="IfcAnnotation")
        bpy.ops.bim.activate_drawing_style()
        return {"FINISHED"}
