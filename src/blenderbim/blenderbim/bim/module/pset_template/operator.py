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

import bpy
import ifcopenshell
import ifcopenshell.api
import blenderbim.bim.schema
import blenderbim.bim.handler
from blenderbim.bim.module.pset_template.prop import updatePsetTemplateFiles, updatePsetTemplates, getPsetTemplates
from ifcopenshell.api.pset_template.data import Data
from blenderbim.bim.ifc import IfcStore


class AddPsetTemplate(bpy.types.Operator):
    bl_idname = "bim.add_pset_template"
    bl_label = "Add Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.pset_template_file.begin_transaction()
        result = self._execute(context)
        IfcStore.pset_template_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        ifcopenshell.api.run("pset_template.add_pset_template", IfcStore.pset_template_file)
        Data.load(IfcStore.pset_template_file)
        updatePsetTemplates(self, context)
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.pset_template_file.undo()

    def commit(self, data):
        IfcStore.pset_template_file.redo()


class RemovePsetTemplate(bpy.types.Operator):
    bl_idname = "bim.remove_pset_template"
    bl_label = "Remove Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMPsetTemplateProperties
        return bool(getPsetTemplates(props, context))

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.pset_template_file.begin_transaction()
        result = self._execute(context)
        IfcStore.pset_template_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        if props.active_pset_template_id == int(props.pset_templates):
            bpy.ops.bim.disable_editing_pset_template()
        ifcopenshell.api.run(
            "pset_template.remove_pset_template",
            IfcStore.pset_template_file,
            **{"pset_template": IfcStore.pset_template_file.by_id(int(props.pset_templates))}
        )
        Data.load(IfcStore.pset_template_file)
        updatePsetTemplates(self, context)
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.pset_template_file.undo()

    def commit(self, data):
        IfcStore.pset_template_file.redo()


class EnableEditingPsetTemplate(bpy.types.Operator):
    bl_idname = "bim.enable_editing_pset_template"
    bl_label = "Enable Editing Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMPsetTemplateProperties
        return bool(getPsetTemplates(props, context))

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        props.active_pset_template_id = int(props.pset_templates)
        template = Data.pset_templates[props.active_pset_template_id]
        props.active_pset_template.global_id = template["GlobalId"]
        props.active_pset_template.name = template["Name"] or ""
        props.active_pset_template.description = template["Description"] or ""
        props.active_pset_template.template_type = template["TemplateType"]
        props.active_pset_template.applicable_entity = template["ApplicableEntity"] or ""
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
        template = Data.prop_templates[props.active_prop_template_id]
        props.active_prop_template.name = template["Name"] or ""
        props.active_prop_template.description = template["Description"] or ""
        props.active_prop_template.primary_measure_type = template["PrimaryMeasureType"]
        return {"FINISHED"}


class DisableEditingPropTemplate(bpy.types.Operator):
    bl_idname = "bim.disable_editing_prop_template"
    bl_label = "Disable Editing Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        props.active_prop_template_id = 0
        return {"FINISHED"}


class EditPsetTemplate(bpy.types.Operator):
    bl_idname = "bim.edit_pset_template"
    bl_label = "Edit Pset Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.pset_template_file.begin_transaction()
        result = self._execute(context)
        IfcStore.pset_template_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

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
        Data.load(IfcStore.pset_template_file)
        updatePsetTemplates(self, context)
        bpy.ops.bim.disable_editing_pset_template()
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.pset_template_file.undo()

    def commit(self, data):
        IfcStore.pset_template_file.redo()


class SavePsetTemplateFile(bpy.types.Operator):
    bl_idname = "bim.save_pset_template_file"
    bl_label = "Save Pset Template File"

    def execute(self, context):
        IfcStore.pset_template_file.write(IfcStore.pset_template_path)
        blenderbim.bim.handler.purge_module_data()
        blenderbim.bim.schema.reload()
        return {"FINISHED"}


class AddPropTemplate(bpy.types.Operator):
    bl_idname = "bim.add_prop_template"
    bl_label = "Add Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.pset_template_file.begin_transaction()
        result = self._execute(context)
        IfcStore.pset_template_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        pset_template_id = props.active_pset_template_id or int(props.pset_templates)
        ifcopenshell.api.run(
            "pset_template.add_prop_template",
            IfcStore.pset_template_file,
            **{"pset_template": IfcStore.pset_template_file.by_id(pset_template_id)}
        )
        Data.load(IfcStore.pset_template_file)
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.pset_template_file.undo()

    def commit(self, data):
        IfcStore.pset_template_file.redo()


class RemovePropTemplate(bpy.types.Operator):
    bl_idname = "bim.remove_prop_template"
    bl_label = "Remove Prop Template"
    bl_options = {"REGISTER", "UNDO"}
    prop_template: bpy.props.IntProperty()

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.pset_template_file.begin_transaction()
        result = self._execute(context)
        IfcStore.pset_template_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        ifcopenshell.api.run(
            "pset_template.remove_prop_template",
            IfcStore.pset_template_file,
            **{"prop_template": IfcStore.pset_template_file.by_id(self.prop_template)}
        )
        Data.load(IfcStore.pset_template_file)
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.pset_template_file.undo()

    def commit(self, data):
        IfcStore.pset_template_file.redo()


class EditPropTemplate(bpy.types.Operator):
    bl_idname = "bim.edit_prop_template"
    bl_label = "Edit Prop Template"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.pset_template_file.begin_transaction()
        result = self._execute(context)
        IfcStore.pset_template_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = context.scene.BIMPsetTemplateProperties
        ifcopenshell.api.run(
            "pset_template.edit_prop_template",
            IfcStore.pset_template_file,
            **{
                "prop_template": IfcStore.pset_template_file.by_id(props.active_prop_template_id),
                "attributes": {
                    "Name": props.active_prop_template.name,
                    "Description": props.active_prop_template.description,
                    "PrimaryMeasureType": props.active_prop_template.primary_measure_type,
                },
            }
        )
        Data.load(IfcStore.pset_template_file)
        bpy.ops.bim.disable_editing_prop_template()
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.pset_template_file.undo()

    def commit(self, data):
        IfcStore.pset_template_file.redo()
