# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy_extras.io_utils import ImportHelper
from bonsai.bim.module.resource.ui import draw_productivity_ui
import bonsai.core.resource as core
import bonsai.tool as tool


class LoadResources(bpy.types.Operator):
    bl_idname = "bim.load_resources"
    bl_label = "Load Resources"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_resources(tool.Resource)
        return {"FINISHED"}


class AddResource(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_resource"
    bl_label = "Add Resource"
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
    bl_label = "Disable Editing Resource"
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
    bl_description = "Assign resource to the selected objects"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_resource(tool.Ifc, tool.Spatial, resource=tool.Ifc.get().by_id(self.resource))


class UnassignResource(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_resource"
    bl_label = "Unassign Resource"
    bl_description = "Unassign resource from the selected objects"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_resource(tool.Ifc, tool.Spatial, resource=tool.Ifc.get().by_id(self.resource))


class EnableEditingResourceTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_resource_time"
    bl_label = "Enable Editing Resource Time"
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

    @classmethod
    def poll(cls, context):
        active_resource = tool.Resource.get_highlighted_resource()
        if not active_resource:
            cls.poll_message_set("No resource is active.")
            return False
        if not tool.Resource.get_productivity(active_resource, should_inherit=True):
            cls.poll_message_set("No productivity data for active resource.")
            return False
        return True

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
    bl_label = "Enable Editing Resource Base Quantity"
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
    bl_idname = "bim.import_resources"
    bl_label = "Import Resources"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        return ifc_file is not None

    def _execute(self, context):
        core.import_resources(tool.Resource, file_path=self.filepath)


class AddProductivityData(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_productivity_data"
    bl_label = "Add Productivity"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        tool.Ifc.run("pset.add_pset", product=tool.Resource.get_highlighted_resource(), name="EPset_Productivity")


class EditProductivityData(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_productivity_data"
    bl_label = "Edit Productivity"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_productivity_pset(tool.Ifc, tool.Resource)

    def draw(self, context):
        draw_productivity_ui(self, context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)


class ConstrainResourceWork(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_usage_constraint"
    bl_label = "Constrain Resource Work"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()
    attribute: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_usage_constraint(
            tool.Ifc, tool.Resource, resource=tool.Ifc.get().by_id(self.resource), reference_path=self.attribute
        )


class RemoveUsageConstraint(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_usage_constraint"
    bl_label = "Remove Usage Constraint"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()
    attribute: bpy.props.StringProperty()

    def _execute(self, context):
        core.remove_usage_constraint(
            tool.Ifc, tool.Resource, resource=tool.Ifc.get().by_id(self.resource), reference_path=self.attribute
        )


class GoToResource(bpy.types.Operator):
    bl_idname = "bim.go_to_resource"
    bl_label = "Go To Resource"
    bl_description = "Selects the resource in the Resource Panel"
    bl_options = {"REGISTER", "UNDO"}
    resource: bpy.props.IntProperty()

    def execute(self, context):
        core.go_to_resource(tool.Resource, resource=tool.Ifc.get().by_id(self.resource))
        return {"FINISHED"}


class CalculateResourceUsage(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_resource_usage"
    bl_label = "Calculate Resource Usage"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        active_resource = tool.Resource.get_highlighted_resource()
        if not active_resource:
            cls.poll_message_set("No resource is active.")
            return False
        if active_resource.Usage and active_resource.Usage.ScheduleWork:
            task = tool.Resource.get_task_assignments(active_resource)
            if task and tool.Sequence.has_duration(task):
                return True
        cls.poll_message_set("No usage data for active resource.")
        return False

    def _execute(self, context):
        core.calculate_resource_usage(tool.Ifc, tool.Resource, resource=tool.Resource.get_highlighted_resource())
