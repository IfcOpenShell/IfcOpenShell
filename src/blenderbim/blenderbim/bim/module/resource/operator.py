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
import json
import time
import isodate
import ifcopenshell.api
import blenderbim.bim.helper
import blenderbim.bim.module.sequence.helper as helper
from datetime import datetime
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data
from ifcopenshell.api.unit.data import Data as UnitData


class LoadResources(bpy.types.Operator):
    bl_idname = "bim.load_resources"
    bl_label = "Load Resources"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        self.tprops.resources.clear()

        self.contracted_resources = json.loads(self.props.contracted_resources)
        for resource_id, data in Data.resources.items():
            if not data["HasContext"]:
                continue
            self.create_new_resource_li(resource_id, 0)
        bpy.ops.bim.load_resource_properties()
        self.props.is_editing = True
        return {"FINISHED"}

    def create_new_resource_li(self, related_object_id, level_index):
        resource = Data.resources[related_object_id]
        new = self.tprops.resources.add()
        new.ifc_definition_id = related_object_id
        new.is_expanded = related_object_id not in self.contracted_resources
        new.level_index = level_index
        if resource["IsNestedBy"]:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in resource["IsNestedBy"]:
                    self.create_new_resource_li(related_object_id, level_index + 1)
        return {"FINISHED"}


class EnableEditingResource(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource"
    bl_label = "Enable Editing Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.props.active_resource_id = self.resource
        self.props.resource_attributes.clear()
        self.props.editing_resource_type = "ATTRIBUTES"
        self.enable_editing_resource()
        return {"FINISHED"}

    def enable_editing_resource(self):
        data = Data.resources[self.resource]
        for attribute in IfcStore.get_schema().declaration_by_name(data["type"]).all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity" or isinstance(data_type, tuple):
                continue
            new = self.props.resource_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]


class LoadResourceProperties(bpy.types.Operator):
    bl_idname = "bim.load_resource_properties"
    bl_label = "Load Resource Properties"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        self.props.is_resource_update_enabled = False
        for item in self.tprops.resources:
            if self.resource and item.ifc_definition_id != self.resource:
                continue
            resource = Data.resources[item.ifc_definition_id]
            item.name = resource["Name"] or "Unnamed"
        self.props.is_resource_update_enabled = True
        return {"FINISHED"}


class DisableEditingResource(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource"
    bl_label = "Disable Editing Workplan"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMResourceProperties.active_resource_id = 0
        context.scene.BIMResourceProperties.active_task_time_id = 0
        return {"FINISHED"}


class DisableResourceEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_resource_editing_ui"
    bl_label = "Disable Resources Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMResourceProperties.is_editing = False
        return {"FINISHED"}


class AddResource(bpy.types.Operator):
    bl_idname = "bim.add_resource"
    bl_label = "Add resource"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    resource: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run(
            "resource.add_resource",
            IfcStore.get_file(),
            parent_resource=IfcStore.get_file().by_id(self.resource) if self.resource else None,
            ifc_class=self.ifc_class,
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class EditResource(bpy.types.Operator):
    bl_idname = "bim.edit_resource"
    bl_label = "Edit Resource"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMResourceProperties
        attributes = blenderbim.bim.helper.export_attributes(props.resource_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "resource.edit_resource",
            self.file,
            **{"resource": self.file.by_id(props.active_resource_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_resource_properties(resource=props.active_resource_id)
        bpy.ops.bim.disable_editing_resource()
        return {"FINISHED"}


class RemoveResource(bpy.types.Operator):
    bl_idname = "bim.remove_resource"
    bl_label = "Remove Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run(
            "resource.remove_resource",
            IfcStore.get_file(),
            resource=IfcStore.get_file().by_id(self.resource),
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class ExpandResource(bpy.types.Operator):
    bl_idname = "bim.expand_resource"
    bl_label = "Expand Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        self.file = IfcStore.get_file()
        contracted_resources = json.loads(props.contracted_resources)
        contracted_resources.remove(self.resource)
        props.contracted_resources = json.dumps(contracted_resources)
        Data.load(self.file)
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class ContractResource(bpy.types.Operator):
    bl_idname = "bim.contract_resource"
    bl_label = "Contract Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        self.file = IfcStore.get_file()
        contracted_resources = json.loads(props.contracted_resources)
        contracted_resources.append(self.resource)
        props.contracted_resources = json.dumps(contracted_resources)
        Data.load(self.file)
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class AssignResource(bpy.types.Operator):
    bl_idname = "bim.assign_resource"
    bl_label = "Assign Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        )
        for related_object in related_objects:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "resource.assign_resource",
                self.file,
                relating_resource=self.file.by_id(self.resource),
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
            )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignResource(bpy.types.Operator):
    bl_idname = "bim.unassign_resource"
    bl_label = "Unassign Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        )
        for related_object in related_objects:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "resource.unassign_resource",
                self.file,
                relating_resource=self.file.by_id(self.resource),
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
            )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingResourceTime(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_time"
    bl_label = "Enable Editing Resource Usage"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMResourceProperties
        self.file = IfcStore.get_file()
        resource_time_id = Data.resources[self.resource]["Usage"] or self.add_resource_time().id()
        props.resource_time_attributes.clear()

        data = Data.resource_times[resource_time_id]

        blenderbim.bim.helper.import_attributes(
            "IfcResourceTime", props.resource_time_attributes, data, self.import_attributes
        )
        props.active_resource_time_id = resource_time_id
        props.active_resource_id = self.resource
        props.editing_resource_type = "USAGE"
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if prop.data_type == "string":
            if isinstance(data[name], datetime):
                prop.string_value = "" if prop.is_null else data[name].isoformat()
                return True
            elif isinstance(data[name], isodate.Duration):
                prop.string_value = (
                    "" if prop.is_null else ifcopenshell.util.date.datetime2ifc(data[name], "IfcDuration")
                )
                return True

    def add_resource_time(self):
        resource_time = ifcopenshell.api.run(
            "resource.add_resource_time", self.file, resource=self.file.by_id(self.resource)
        )
        Data.load(self.file)
        return resource_time


class DisableEditingResourceTime(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource_time"
    bl_label = "Disable Editing Resource Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMResourceProperties.active_resource_time_id = 0
        bpy.ops.bim.disable_editing_resource()
        return {"FINISHED"}


class EditResourceTime(bpy.types.Operator):
    bl_idname = "bim.edit_resource_time"
    bl_label = "Edit Resource Usage"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.props = context.scene.BIMResourceProperties
        attributes = blenderbim.bim.helper.export_attributes(
            self.props.resource_time_attributes, self.export_attributes
        )

        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "resource.edit_resource_time",
            self.file,
            **{"resource_time": self.file.by_id(self.props.active_resource_time_id), "attributes": attributes},
        )
        Data.load(self.file)
        bpy.ops.bim.disable_editing_resource_time()
        bpy.ops.bim.load_resource_properties(resource=self.props.active_resource_id)
        return {"FINISHED"}

    def export_attributes(self, attributes, prop):
        if "Start" in prop.name or "Finish" in prop.name or prop.name == "StatusTime":
            if prop.is_null:
                attributes[prop.name] = None
                return True
            attributes[prop.name] = helper.parse_datetime(prop.string_value)
            return True
        elif prop.name == "LevelingDelay" or "Work" in prop.name:
            if prop.is_null:
                attributes[prop.name] = None
                return True
            attributes[prop.name] = helper.parse_duration(prop.string_value)
            return True


class CalculateResourceWork(bpy.types.Operator):
    bl_idname = "bim.calculate_resource_work"
    bl_label = "Calculate Resource Work"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("resource.calculate_resource_work", self.file, resource=self.file.by_id(self.resource))
        Data.load(self.file)
        bpy.ops.bim.load_resources()
        return {"FINISHED"}


class EnableEditingResourceCosts(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_costs"
    bl_label = "Enable Editing Resource Costs"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        props.active_resource_id = self.resource
        props.editing_resource_type = "COSTS"
        bpy.ops.bim.disable_editing_resource_cost_value()
        return {"FINISHED"}


class DisableEditingResourceCostValue(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource_cost_value"
    bl_label = "Disable Editing Resource Cost Value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        props.active_cost_value_id = 0
        props.cost_value_editing_type = ""
        return {"FINISHED"}


class DisableEditingResourceCostValue(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource_cost_value"
    bl_label = "Disable Editing Resource Cost Value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMResourceProperties
        props.active_cost_value_id = 0
        props.cost_value_editing_type = ""
        return {"FINISHED"}


class EnableEditingResourceCostValueFormula(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_cost_value_formula"
    bl_label = "Enable Editing Resource Cost Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.props.cost_value_attributes.clear()
        self.props.active_cost_value_id = self.cost_value
        self.props.cost_value_editing_type = "FORMULA"
        self.props.cost_value_formula = Data.cost_values[self.cost_value]["Formula"]
        return {"FINISHED"}


class EnableEditingResourceCostValue(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_cost_value"
    bl_label = "Enable Editing Resource Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMResourceProperties
        self.props.cost_value_attributes.clear()
        self.props.active_cost_value_id = self.cost_value
        self.props.cost_value_editing_type = "ATTRIBUTES"
        data = Data.cost_values[self.cost_value]

        blenderbim.bim.helper.import_attributes(
            data["type"],
            self.props.cost_value_attributes,
            data,
            lambda name, prop, data: self.import_attributes(name, prop, data, context),
        )
        return {"FINISHED"}

    def import_attributes(self, name, prop, data, context):
        if name == "AppliedValue":
            # TODO: for now, only support simple IfcValues (which are effectively IfcMonetaryMeasure)
            prop = self.props.cost_value_attributes.add()
            prop.data_type = "float"
            prop.name = "AppliedValue"
            prop.is_optional = True
            prop.float_value = 0.0 if prop.is_null else data[name]
            return True
        elif name == "UnitBasis":
            prop = self.props.cost_value_attributes.add()
            prop.name = "UnitBasisValue"
            prop.data_type = "float"
            prop.is_null = data["UnitBasis"] is None
            prop.is_optional = True
            if data["UnitBasis"]:
                prop.float_value = data["UnitBasis"]["ValueComponent"] or 0
            else:
                prop.float_value = 0

            prop = self.props.cost_value_attributes.add()
            prop.name = "UnitBasisUnit"
            prop.data_type = "enum"
            prop.is_null = prop.is_optional = False
            units = {}
            for unit_id, unit in UnitData.units.items():
                if unit.get("UnitType", None) in [
                    "AREAUNIT",
                    "LENGTHUNIT",
                    "TIMEUNIT",
                    "VOLUMEUNIT",
                    "MASSUNIT",
                    "USERDEFINED",
                ]:
                    if unit["type"] == "IfcContextDependentUnit":
                        units[unit_id] = f"{unit['UnitType']} / {unit['Name']}"
                    else:
                        name = unit["Name"]
                        if unit.get("Prefix", None):
                            name = f"(unit['Prefix']) {name}"
                        units[unit_id] = f"{unit['UnitType']} / {name}"
            prop.enum_items = json.dumps(units)
            if data["UnitBasis"] and data["UnitBasis"]["UnitComponent"]:
                prop.enum_value = str(data["UnitBasis"]["UnitComponent"])
            return True


class EditResourceCostValueFormula(bpy.types.Operator):
    bl_idname = "bim.edit_resource_cost_value_formula"
    bl_label = "Edit Resource Cost Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMResourceProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_value_formula",
            self.file,
            **{"cost_value": self.file.by_id(self.cost_value), "formula": props.cost_value_formula},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_resource_cost_value()
        return {"FINISHED"}


class EditResourceCostValue(bpy.types.Operator):
    bl_idname = "bim.edit_resource_cost_value"
    bl_label = "Edit Resource Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMResourceProperties
        attributes = blenderbim.bim.helper.export_attributes(
            props.cost_value_attributes, lambda attributes, prop: self.export_attributes(attributes, prop, context)
        )
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "cost.edit_cost_value",
            self.file,
            **{"cost_value": self.file.by_id(self.cost_value), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_resource_cost_value()
        return {"FINISHED"}

    def export_attributes(self, attributes, prop, context):
        if prop.name == "UnitBasisValue":
            if prop.is_null:
                attributes["UnitBasis"] = None
                return True
            attributes["UnitBasis"] = {
                "ValueComponent": prop.float_value or 1,
                "UnitComponent": IfcStore.get_file().by_id(
                    int(context.scene.BIMResourceProperties.cost_value_attributes.get("UnitBasisUnit").enum_value)
                ),
            }
            return True
        if prop.name == "UnitBasisUnit":
            return True
