import bpy
import ifcopenshell
from blenderbim.bim.module.pset_template.prop import refreshPropertySetTemplates
from blenderbim.bim.ifc import IfcStore


class AddPropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.add_property_set_template"
    bl_label = "Add Property Set Template"

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        props.active_property_set_template.global_id = ""
        props.active_property_set_template.name = "New_Pset"
        props.active_property_set_template.description = ""
        props.active_property_set_template.template_type = "PSET_TYPEDRIVENONLY"
        props.active_property_set_template.applicable_entity = "IfcTypeObject"
        while len(props.property_templates) > 0:
            props.property_templates.remove(0)
        return {"FINISHED"}


class RemovePropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.remove_property_set_template"
    bl_label = "Remove Property Set Template"

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        template = IfcStore.pset_template_file.by_guid(props.property_set_templates)
        IfcStore.pset_template_file.remove(template)
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        refreshPropertySetTemplates(self, context)
        return {"FINISHED"}


class EditPropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.edit_property_set_template"
    bl_label = "Edit Property Set Template"

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        template = IfcStore.pset_template_file.by_guid(props.property_set_templates)
        props.active_property_set_template.global_id = template.GlobalId
        props.active_property_set_template.name = template.Name
        props.active_property_set_template.description = template.Description
        props.active_property_set_template.template_type = template.TemplateType
        props.active_property_set_template.applicable_entity = template.ApplicableEntity

        while len(props.property_templates) > 0:
            props.property_templates.remove(0)

        if template.HasPropertyTemplates:
            for property_template in template.HasPropertyTemplates:
                if not property_template.is_a("IfcSimplePropertyTemplate"):
                    continue
                new = props.property_templates.add()
                new.global_id = property_template.GlobalId
                new.name = property_template.Name
                new.description = property_template.Description
                new.primary_measure_type = property_template.PrimaryMeasureType
        return {"FINISHED"}


class SavePropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.save_property_set_template"
    bl_label = "Save Property Set Template"

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        blender_property_set_template = props.active_property_set_template
        if blender_property_set_template.global_id:
            template = IfcStore.pset_template_file.by_guid(blender_property_set_template.global_id)
        else:
            template = IfcStore.pset_template_file.createIfcPropertySetTemplate()
            template.GlobalId = ifcopenshell.guid.new()
        template.Name = blender_property_set_template.name
        template.Description = blender_property_set_template.description
        template.TemplateType = blender_property_set_template.template_type
        template.ApplicableEntity = blender_property_set_template.applicable_entity

        saved_global_ids = []

        for blender_property_template in props.property_templates:
            if blender_property_template.global_id:
                property_template = IfcStore.pset_template_file.by_guid(blender_property_template.global_id)
            else:
                property_template = IfcStore.pset_template_file.createIfcSimplePropertyTemplate()
                property_template.GlobalId = ifcopenshell.guid.new()
                if template.HasPropertyTemplates:
                    has_property_templates = list(template.HasPropertyTemplates)
                else:
                    has_property_templates = []
                has_property_templates.append(property_template)
                template.HasPropertyTemplates = has_property_templates
            property_template.Name = blender_property_template.name
            property_template.Description = blender_property_template.description
            property_template.PrimaryMeasureType = blender_property_template.primary_measure_type
            property_template.TemplateType = "P_SINGLEVALUE"
            property_template.AccessState = "READWRITE"
            saved_global_ids.append(property_template.GlobalId)

        for element in template.HasPropertyTemplates:
            if element.GlobalId not in saved_global_ids:
                IfcStore.pset_template_file.remove(element)

        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        refreshPropertySetTemplates(self, context)
        return {"FINISHED"}


class AddPropertyTemplate(bpy.types.Operator):
    bl_idname = "bim.add_property_template"
    bl_label = "Add Property Template"

    def execute(self, context):
        context.scene.BIMPsetTemplateProperties.property_templates.add()
        return {"FINISHED"}


class RemovePropertyTemplate(bpy.types.Operator):
    bl_idname = "bim.remove_property_template"
    bl_label = "Remove Property Template"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMPsetTemplateProperties.property_templates.remove(self.index)
        return {"FINISHED"}
