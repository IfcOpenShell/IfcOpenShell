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
import bpy
import ifcopenshell
import ifcopenshell.api
import blenderbim.bim.schema
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore


class Operator:
    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.pset_template_file.begin_transaction()
        result = self._execute(context)
        IfcStore.pset_template_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.pset_template_file.undo()

    def commit(self, data):
        IfcStore.pset_template_file.redo()


class AddPsetFile(bpy.types.Operator):
    bl_idname = "bim.add_pset_file"
    bl_label = "Add Pset File"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=250)

    def draw(self, context):
        self.props = context.scene.BIMPsetTemplateProperties
        self.layout.prop(self.props, "new_template_filename", text="Filename:")

    def execute(self, context):
        template = ifcopenshell.file()
        filepath = os.path.join(
            context.scene.BIMProperties.data_dir,
            "pset",
            self.props.new_template_filename + ".ifc",
        )

        template.create_entity(
            "IFCPROPERTYSETTEMPLATE",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "Name": "Name",
                "Description": "Description",
                "TemplateType": "PSET_TYPEDRIVENONLY",
                "ApplicableEntity": "IfcTypeObject",
            }
        )
        template.write(filepath)
        self.props.new_template_filename = ""
        return {"FINISHED"}


class AddPsetTemplate(bpy.types.Operator, Operator):
    bl_idname = "bim.add_pset_template"
    bl_label = "Add Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        template = ifcopenshell.api.run("pset_template.add_pset_template", IfcStore.pset_template_file)
        blenderbim.bim.handler.refresh_ui_data()
        context.scene.BIMPsetTemplateProperties.pset_templates = str(template.id())


class RemovePsetTemplate(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_pset_template"
    bl_label = "Remove Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        if props.active_pset_template_id == int(props.pset_templates):
            bpy.ops.bim.disable_editing_pset_template()
        ifcopenshell.api.run(
            "pset_template.remove_pset_template",
            IfcStore.pset_template_file,
            **{"pset_template": IfcStore.pset_template_file.by_id(int(props.pset_templates))}
        )


class EnableEditingPsetTemplate(bpy.types.Operator):
    bl_idname = "bim.enable_editing_pset_template"
    bl_label = "Enable Editing Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        props.active_pset_template_id = int(props.pset_templates)
        template = IfcStore.pset_template_file.by_id(props.active_pset_template_id)
        props.active_pset_template.global_id = template.GlobalId
        props.active_pset_template.name = template.Name or ""
        props.active_pset_template.description = template.Description or ""
        props.active_pset_template.template_type = template.TemplateType
        props.active_pset_template.applicable_entity = template.ApplicableEntity or ""
        return {"FINISHED"}


class DisableEditingPsetTemplate(bpy.types.Operator):
    bl_idname = "bim.disable_editing_pset_template"
    bl_label = "Disable Editing Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        props.active_pset_template_id = 0
        return {"FINISHED"}


class EnableEditingPropTemplate(bpy.types.Operator):
    bl_idname = "bim.enable_editing_prop_template"
    bl_label = "Enable Editing Prop Template"
    bl_options = {"REGISTER", "UNDO"}
    prop_template: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        props.active_prop_template_id = self.prop_template
        template = IfcStore.pset_template_file.by_id(props.active_prop_template_id)
        props.active_prop_template.name = template.Name or ""
        props.active_prop_template.description = template.Description or ""
        props.active_prop_template.primary_measure_type = template.PrimaryMeasureType
        props.active_prop_template.template_type = template.TemplateType
        props.active_prop_template.enum_values.clear()

        if template.Enumerators:
            props.active_prop_template.enum_values.clear()
            data_type = props.active_prop_template.get_value_name()
            for e in template.Enumerators.EnumerationValues:
                new = props.active_prop_template.enum_values.add()
                setattr(new, data_type, e.wrappedValue)
        return {"FINISHED"}


class DeletePropEnum(bpy.types.Operator):
    bl_idname = "bim.delete_prop_enum"
    bl_label = "delete property enumeration"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        active_prop = context.scene.BIMPsetTemplateProperties.active_prop_template
        active_prop.enum_values.remove(self.index)
        return {"FINISHED"}


class AddPropEnum(bpy.types.Operator):
    bl_idname = "bim.add_prop_enum"
    bl_label = "add property enumeration"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        active_prop = context.scene.BIMPsetTemplateProperties.active_prop_template
        active_prop.enum_values.add()
        return {"FINISHED"}


class DisableEditingPropTemplate(bpy.types.Operator):
    bl_idname = "bim.disable_editing_prop_template"
    bl_label = "Disable Editing Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        props.active_prop_template_id = 0
        return {"FINISHED"}


class EditPsetTemplate(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_pset_template"
    bl_label = "Edit Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        ifcopenshell.api.run(
            "pset_template.edit_pset_template",
            IfcStore.pset_template_file,
            **{
                "pset_template": IfcStore.pset_template_file.by_id(props.active_pset_template_id),
                "attributes": {
                    "Name": props.active_pset_template.name,
                    "Description": props.active_pset_template.description,
                    "TemplateType": props.active_pset_template.template_type,
                    "ApplicableEntity": props.active_pset_template.applicable_entity,
                },
            }
        )
        bpy.ops.bim.disable_editing_pset_template()


class SavePsetTemplateFile(bpy.types.Operator):
    bl_idname = "bim.save_pset_template_file"
    bl_label = "Save Pset Template File"

    def execute(self, context):
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        blenderbim.bim.handler.purge_module_data()
        blenderbim.bim.schema.reload()
        return {"FINISHED"}


class AddPropTemplate(bpy.types.Operator, Operator):
    bl_idname = "bim.add_prop_template"
    bl_label = "Add Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        pset_template_id = props.active_pset_template_id or int(props.pset_templates)
        ifcopenshell.api.run(
            "pset_template.add_prop_template",
            IfcStore.pset_template_file,
            **{"pset_template": IfcStore.pset_template_file.by_id(pset_template_id)}
        )
        bpy.ops.bim.disable_editing_prop_template()


class RemovePropTemplate(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_prop_template"
    bl_label = "Remove Prop Template"
    bl_options = {"REGISTER", "UNDO"}
    prop_template: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        ifcopenshell.api.run(
            "pset_template.remove_prop_template",
            IfcStore.pset_template_file,
            **{"prop_template": IfcStore.pset_template_file.by_id(self.prop_template)}
        )


class EditPropTemplate(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_prop_template"
    bl_label = "Edit Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        if props.active_prop_template.template_type == "P_ENUMERATEDVALUE":
            enumerator = self.generate_prop_enum(props)
        else:
            enumerator = None
        ifcopenshell.api.run(
            "pset_template.edit_prop_template",
            IfcStore.pset_template_file,
            **{
                "prop_template": IfcStore.pset_template_file.by_id(props.active_prop_template_id),
                "attributes": {
                    "Name": props.active_prop_template.name,
                    "Description": props.active_prop_template.description,
                    "PrimaryMeasureType": props.active_prop_template.primary_measure_type,
                    "TemplateType": props.active_prop_template.template_type,
                    "Enumerators": enumerator,
                },
            }
        )
        bpy.ops.bim.disable_editing_prop_template()

    # TODO -This will need to go into the
    # api code at some point - vulevukusej
    def generate_prop_enum(self, props):
        self.file = IfcStore.pset_template_file
        data_type = props.active_prop_template.get_value_name()
        prop = props.active_prop_template
        prop_enum = self.file.create_entity(
            "IFCPROPERTYENUMERATION",
            Name=prop.name,
            EnumerationValues=tuple(
                self.file.create_entity(prop.primary_measure_type, getattr(ev, data_type)) for ev in prop.enum_values
            ),
        )
        return prop_enum
