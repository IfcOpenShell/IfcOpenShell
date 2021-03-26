import bpy
import ifcopenshell.api.style.add_style as add_style
import ifcopenshell.api.style.edit_style as edit_style
from blenderbim.bim.ifc import IfcStore


def get_colour_settings(material):
    transparency = material.diffuse_color[3]
    diffuse_colour = material.diffuse_color
    if material.use_nodes and hasattr(material.node_tree, "nodes") and "Principled BSDF" in material.node_tree.nodes:
        bsdf = material.node_tree.nodes["Principled BSDF"]
        transparency = bsdf.inputs["Alpha"].default_value
        diffuse_colour = bsdf.inputs["Base Color"].default_value
    return {
        "SurfaceColour": material.diffuse_color,
        "Transparency": transparency,
        "DiffuseColour": diffuse_colour,
    }


class EditStyle(bpy.types.Operator):
    bl_idname = "bim.edit_style"
    bl_label = "Edit Style"
    material: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        material = bpy.data.objects.get(self.material) if self.material else bpy.context.active_object.active_material
        settings = get_colour_settings(material)
        settings["style"] = self.file.by_id(material.BIMMaterialProperties.ifc_style_id)
        edit_style.Usecase(self.file, settings).execute()
        return {"FINISHED"}


class AddStyle(bpy.types.Operator):
    bl_idname = "bim.add_style"
    bl_label = "Add Style"
    material: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        material = bpy.data.materials.get(self.material) if self.material else bpy.context.active_object.active_material
        settings = get_colour_settings(material)
        settings["Name"] = material.name
        settings["external_definition"] = None # TODO: Implement. See #1222
        style = add_style.Usecase(self.file, settings).execute()
        material.BIMMaterialProperties.ifc_style_id = int(style.id())
        return {"FINISHED"}


class UnlinkStyle(bpy.types.Operator):
    bl_idname = "bim.unlink_style"
    bl_label = "Unlink Style"
    material: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        material = bpy.data.materials.get(self.material)
        material.BIMMaterialProperties.ifc_style_id = 0
        if "Ifc" in material.name and "/" in material.name:
            material.name = "/".join(material.name.split("/")[1:])
        return {"FINISHED"}
