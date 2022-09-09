# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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
import blenderbim.tool as tool
from ifcopenshell.api.cost.data import CostValueTrait
import ifcopenshell


def refresh():
    ResourceData.is_loaded = False


class ResourceData(CostValueTrait):
    data = {}
    is_loaded = False
    cost_values = {}

    @classmethod
    def load(cls):
        cls.data = {
            "has_resources": cls.has_resources(),
        }
        cls.load_resources()
        cls.is_loaded = True

    @classmethod
    def has_resources(cls):
        return bool(tool.Ifc.get().by_type("IfcResource"))

    @classmethod
    def number_of_resources_loaded(cls):
        return len(tool.Ifc.get().by_type("IfcResource"))

    @classmethod
    def load_resources(cls):
        cls.data["resources"] = {}
        for resource in tool.Ifc.get().by_type("IfcResource"):
            data = resource.get_info()
            del data["OwnerHistory"]
            data["IsNestedBy"] = []
            for rel in resource.IsNestedBy:
                [data["IsNestedBy"].append(o.id()) for o in rel.RelatedObjects]
            data["Nests"] = []
            for rel in resource.Nests:
                [data["Nests"].append(rel.RelatingObject.id())]
            data["ResourceOf"] = []
            for rel in resource.ResourceOf:
                [data["ResourceOf"].append(o.id()) for o in rel.RelatedObjects]
            data["HasContext"] = resource.HasContext[0].RelatingContext.id() if resource.HasContext else None
            if resource.Usage:
                data["Usage"] = data["Usage"].id()
            data["TotalCostQuantity"] = cls.get_total_quantity(resource)
            if resource.BaseQuantity:
                data["BaseQuantity"] = resource.BaseQuantity.get_info()
                del data["BaseQuantity"]["Unit"]
            if resource.BaseCosts:
                data["BaseCosts"] = [e.id() for e in resource.BaseCosts]
                cls.load_cost_values(resource, data)
            cls.data["resources"][resource.id()] = data
        cls.data["number_of_resources_loaded"] = cls.number_of_resources_loaded()

    def load_resource_times(cls):
        cls.data["resource_times"] = {}
        for resource_time in tool.Ifc.get().by_type("IfcResourceTime"):
            data = resource_time.get_info()
            for key, value in data.items():
                if not value:
                    continue
                if "Start" in key or "Finish" in key or key == "StatusTime":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
                elif "Work" in key or key == "LevelingDelay":
                    data[key] = ifcopenshell.util.date.ifc2datetime(value)
            cls.data["resource_times"][resource_time.id()] = data
