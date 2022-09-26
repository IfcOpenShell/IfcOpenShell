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
from bpy_extras.io_utils import ImportHelper
import blenderbim.core.resource as core
import blenderbim.tool as tool


class LoadResources(bpy.types.Operator):
    bl_idname = "bim.load_resources"
    bl_label = "Load Resources"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_resources(tool.Resource)
        return {"FINISHED"}


class LoadResourceProperties(bpy.types.Operator):
    bl_idname = "bim.load_resource_properties"
    bl_label = "Load Resource Properties"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.load_resource_properties(
            tool.Resource, resource=tool.Ifc.get().by_id(self.resource) if self.resource else None
        )
        return {"FINISHED"}


class AddResource(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_resource"
    bl_label = "Add resource"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    parent_resource: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_resource(
            tool.Ifc,
            tool.Resource,
            ifc_class=self.ifc_class,
            parent_resource=tool.Ifc.get().by_id(self.parent_resource) if self.parent_resource else None,
        )


class EnableEditingResource(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource"
    bl_label = "Enable Editing Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_resource(tool.Resource, resource=tool.Ifc.get().by_id(self.resource))
        return {"FINISHED"}


class DisableEditingResource(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource"
    bl_label = "Disable Editing Resources"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_resource(tool.Resource)
        return {"FINISHED"}


class DisableResourceEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_resource_editing_ui"
    bl_label = "Disable Resources Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_resource_editing_ui(tool.Resource)
        return {"FINISHED"}


class EditResource(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_resource"
    bl_label = "Edit Resource"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_resource(
            tool.Ifc,
            tool.Resource,
            resource=tool.Ifc.get().by_id(context.scene.BIMResourceProperties.active_resource_id),
        )


class RemoveResource(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_resource"
    bl_label = "Remove Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_resource(tool.Ifc, tool.Resource, resource=tool.Ifc.get().by_id(self.resource))


class ExpandResource(bpy.types.Operator):
    bl_idname = "bim.expand_resource"
    bl_label = "Expand Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.expand_resource(tool.Resource, resource=tool.Ifc.get().by_id(self.resource))
        return {"FINISHED"}


class ContractResource(bpy.types.Operator):
    bl_idname = "bim.contract_resource"
    bl_label = "Contract Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.contract_resource(tool.Resource, resource=tool.Ifc.get().by_id(self.resource))
        return {"FINISHED"}


class AssignResource(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_resource"
    bl_label = "Assign Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def _execute(self, context):
        core.assign_resource(tool.Ifc, tool.Resource, resource=tool.Ifc.get().by_id(self.resource))


class UnassignResource(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_resource"
    bl_label = "Unassign Resource"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def _execute(self, context):
        core.unassign_resource(tool.Ifc, tool.Resource, resource=tool.Ifc.get().by_id(self.resource))


class EnableEditingResourceTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_resource_time"
    bl_label = "Enable Editing Resource Usage"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_resource_time(tool.Ifc, tool.Resource, resource=tool.Ifc.get().by_id(self.resource))


class DisableEditingResourceTime(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource_time"
    bl_label = "Disable Editing Resource Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_resource_time(tool.Resource)
        return {"FINISHED"}


class EditResourceTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_resource_time"
    bl_label = "Edit Resource Usage"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_resource_time(
            tool.Ifc,
            tool.Resource,
            resource_time=tool.Ifc.get().by_id(context.scene.BIMResourceProperties.active_resource_time_id),
        )


class CalculateResourceWork(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_resource_work"
    bl_label = "Calculate Resource Work"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def _execute(self, context):
        core.calculate_resource_work(tool.Ifc, tool.Resource, resource=tool.Ifc.get().by_id(self.resource))


class EnableEditingResourceCosts(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_costs"
    bl_label = "Enable Editing Resource Costs"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_resource_costs(tool.Resource, resource=tool.Ifc.get().by_id(self.resource))
        return {"FINISHED"}


class DisableEditingResourceCostValue(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource_cost_value"
    bl_label = "Disable Editing Resource Cost Value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_resource_cost_value(tool.Resource)
        return {"FINISHED"}


class EnableEditingResourceCostValueFormula(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_cost_value_formula"
    bl_label = "Enable Editing Resource Cost Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_resource_cost_value_formula(tool.Resource, cost_value=tool.Ifc.get().by_id(self.cost_value))
        return {"FINISHED"}


class EnableEditingResourceCostValue(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_cost_value"
    bl_label = "Enable Editing Resource Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_resource_cost_value(tool.Resource, cost_value=tool.Ifc.get().by_id(self.cost_value))
        return {"FINISHED"}


class EditResourceCostValueFormula(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_resource_cost_value_formula"
    bl_label = "Edit Resource Cost Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_resource_cost_value_formula(tool.Ifc, tool.Resource, cost_value=tool.Ifc.get().by_id(self.cost_value))


class EditResourceCostValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_resource_cost_value"
    bl_label = "Edit Resource Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_resource_cost_value(tool.Ifc, tool.Resource, cost_value=tool.Ifc.get().by_id(self.cost_value))


class EnableEditingResourceBaseQuantity(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_base_quantity"
    bl_label = "Enable Editing Resource Quantity"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_resource_base_quantity(tool.Resource, resource=tool.Ifc.get().by_id(self.resource))
        return {"FINISHED"}


class AddResourceQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_resource_quantity"
    bl_label = "Add Resource Quantity"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_resource_quantity(tool.Ifc, ifc_class=self.ifc_class, resource=tool.Ifc.get().by_id(self.resource))


class RemoveResourceQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_resource_quantity"
    bl_label = "Remove Resource Quantity"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_resource_quantity(tool.Ifc, resource=tool.Ifc.get().by_id(self.resource))


class EnableEditingResourceQuantity(bpy.types.Operator):
    bl_idname = "bim.enable_editing_resource_quantity"
    bl_label = "Enable Editing Resource Quantity"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_resource_quantity(
            tool.Resource, resource_quantity=tool.Ifc.get().by_id(self.resource).BaseQuantity
        )
        return {"FINISHED"}


class DisableEditingResourceQuantity(bpy.types.Operator):
    bl_idname = "bim.disable_editing_resource_quantity"
    bl_label = "Disable Editing Resource Quantity"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_resource_quantity(tool.Resource)
        return {"FINISHED"}


class EditResourceQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_resource_quantity"
    bl_label = "Edit Resource Quantity"
    bl_options = {"REGISTER", "UNDO"}
    physical_quantity: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_resource_quantity(
            tool.Resource, tool.Ifc, physical_quantity=tool.Ifc.get().by_id(self.physical_quantity)
        )


class ImportResources(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "import_resources.bim"
    bl_label = "Import P6"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        return ifc_file is not None

    def _execute(self, context):
        core.import_resources(tool.Resource, file_path=self.filepath)
