# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
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
import json
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper
import blenderbim.bim.module.sequence.helper as helper


class Sequence(blenderbim.core.tool.Sequence):
    @classmethod
    def get_work_plans(cls):
        work_plans = {}
        for work_plan in tool.Ifc.get().by_type("IfcWorkPlan"):
            work_plans[work_plan.id()] = {"Name": work_plan.Name}
        return work_plans

    @classmethod
    def load_work_plans(cls):
        work_plans = tool.Sequence.get_work_plans()
        props = bpy.context.scene.BIMWorkPlanProperties
        props.work_plans.clear()
        for ifc_definition_id, work_plan in work_plans.items():
            new = props.work_plans.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = work_plan["Name"] or "Unnamed"

    @classmethod
    def enable_editing_work_plan(cls, work_plan):
        if work_plan:
            bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = work_plan
            bpy.context.scene.BIMWorkPlanProperties.editing_type = "ATTRIBUTES"

    @classmethod
    def disable_editing_work_plan(cls):
        bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = 0

    @classmethod
    def get_current_ifc_work_plan(cls):
        active_work_plan = bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id
        ifc_work_plan = tool.Ifc.get().by_id(active_work_plan)
        return ifc_work_plan

    @classmethod
    def get_ifc_work_plan_attributes(cls, work_plan):
        if work_plan:
            ifc_work_plan = tool.Ifc.get().by_id(work_plan)
            data = ifc_work_plan.get_info()
            del data["OwnerHistory"]
            if data["Creators"]:
                data["Creators"] = [p.id() for p in data["Creators"]]
            data["CreationDate"] = ifcopenshell.util.date.ifc2datetime(data["CreationDate"])
            data["StartTime"] = ifcopenshell.util.date.ifc2datetime(data["StartTime"])
            if data["FinishTime"]:
                data["FinishTime"] = ifcopenshell.util.date.ifc2datetime(data["FinishTime"])
            data["IsDecomposedBy"] = []
            for rel in ifc_work_plan.IsDecomposedBy:
                data["IsDecomposedBy"].extend([o.id() for o in rel.RelatedObjects])
            return data

    @classmethod
    def load_work_plan_attributes(cls, data):
        props = bpy.context.scene.BIMWorkPlanProperties
        props.work_plan_attributes.clear()
        blenderbim.bim.helper.import_attributes(
            "IfcWorkPlan", props.work_plan_attributes, data, tool.Sequence.import_attributes
        )

    @classmethod
    def import_attributes(name, prop, data):
        if name in ["CreationDate", "StartTime", "FinishTime"]:
            prop.string_value = "" if prop.is_null else data[name].isoformat()
            return True

    @classmethod
    def get_work_plan_attributes(cls):
        props = bpy.context.scene.BIMWorkPlanProperties
        attributes = blenderbim.bim.helper.export_attributes(
            props.work_plan_attributes, tool.Sequence.export_attributes
        )
        return attributes

    @classmethod
    def export_attributes(attributes, prop):
        if "Date" in prop.name or "Time" in prop.name:
            if prop.is_null:
                attributes[prop.name] = None
                return True
            attributes[prop.name] = helper.parse_datetime(prop.string_value)
            return True
        elif prop.name == "Duration" or prop.name == "TotalFloat":
            if prop.is_null:
                attributes[prop.name] = None
                return True
            attributes[prop.name] = helper.parse_duration(prop.string_value)
            return True
