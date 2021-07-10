import bpy
import ifcopenshell.api
import ifcopenshell.util.representation
import blenderbim.bim.helper
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.style.data import Data


def get_colour_settings(material):
    transparency = material.diffuse_color[3]
    diffuse_colour = material.diffuse_color
    if material.use_nodes and hasattr(material.node_tree, "nodes") and "Principled BSDF" in material.node_tree.nodes:
        bsdf = material.node_tree.nodes["Principled BSDF"]
        transparency = bsdf.inputs["Alpha"].default_value
        diffuse_colour = bsdf.inputs["Base Color"].default_value
    transparency = 1 - transparency
    return {
        "surface_colour": tuple(material.diffuse_color),
        "transparency": transparency,
        "diffuse_colour": tuple(diffuse_colour),
    }


class UpdateStyleColours(bpy.types.Operator):
    bl_idname = "bim.update_style_colours"
    bl_label = "Update Style Colours"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        material = bpy.data.materials.get(self.material) if self.material else bpy.context.active_object.active_material
        settings = get_colour_settings(material)
        settings["style"] = self.file.by_id(material.BIMMaterialProperties.ifc_style_id)
        ifcopenshell.api.run("style.edit_style_colours", self.file, **settings)
        return {"FINISHED"}


class RemoveStyle(bpy.types.Operator):
    bl_idname = "bim.remove_style"
    bl_label = "Remove Style"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        material = bpy.data.materials.get(self.material) if self.material else bpy.context.active_object.active_material
        ifcopenshell.api.run(
            "style.remove_style", self.file, style=self.file.by_id(material.BIMMaterialProperties.ifc_style_id)
        )
        material.BIMMaterialProperties.ifc_style_id = 0
        return {"FINISHED"}


class AddStyle(bpy.types.Operator):
    bl_idname = "bim.add_style"
    bl_label = "Add Style"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        material = bpy.data.materials.get(self.material) if self.material else bpy.context.active_object.active_material
        settings = get_colour_settings(material)
        settings["name"] = material.name
        settings["external_definition"] = None  # TODO: Implement. See #1222
        style = ifcopenshell.api.run("style.add_style", self.file, **settings)
        material.BIMMaterialProperties.ifc_style_id = style.id()
        if material.BIMObjectProperties.ifc_definition_id:
            context = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
            if context:
                ifcopenshell.api.run("style.assign_material_style", self.file, **{
                    "material": self.file.by_id(material.BIMObjectProperties.ifc_definition_id),
                    "style": style,
                    "context": context,
                })
        return {"FINISHED"}


class UnlinkStyle(bpy.types.Operator):
    bl_idname = "bim.unlink_style"
    bl_label = "Unlink Style"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        material = bpy.data.materials.get(self.material)
        material.BIMMaterialProperties.ifc_style_id = 0
        if "Ifc" in material.name and "/" in material.name:
            material.name = "/".join(material.name.split("/")[1:])
        return {"FINISHED"}


class EnableEditingStyle(bpy.types.Operator):
    bl_idname = "bim.enable_editing_style"
    bl_label = "Enable Editing Style"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.StringProperty()

    def execute(self, context):
        material = bpy.data.materials.get(self.material) if self.material else bpy.context.active_object.active_material
        props = material.BIMStyleProperties
        while len(props.attributes) > 0:
            props.attributes.remove(0)

        data = Data.styles[material.BIMMaterialProperties.ifc_style_id]
        blenderbim.bim.helper.import_attributes("IfcSurfaceStyle", props.attributes, data)
        props.is_editing_attributes = True
        return {"FINISHED"}


class DisableEditingStyle(bpy.types.Operator):
    bl_idname = "bim.disable_editing_style"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Style"
    material: bpy.props.StringProperty()

    def execute(self, context):
        material = bpy.data.materials.get(self.material) if self.material else bpy.context.active_object.active_material
        props = material.BIMStyleProperties
        props.is_editing_attributes = False
        return {"FINISHED"}


class EditStyle(bpy.types.Operator):
    bl_idname = "bim.edit_style"
    bl_label = "Edit Style"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        material = bpy.context.active_object.active_material
        props = material.BIMStyleProperties
        attributes = blenderbim.bim.helper.export_attributes(props.attributes)
        self.file = IfcStore.get_file()
        style = self.file.by_id(material.BIMMaterialProperties.ifc_style_id)
        ifcopenshell.api.run("style.edit_style", self.file, **{"style": style, "attributes": attributes})
        Data.load(IfcStore.get_file(), material.BIMMaterialProperties.ifc_style_id)
        bpy.ops.bim.disable_editing_style()
        return {"FINISHED"}
