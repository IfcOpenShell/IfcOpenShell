# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult, Yassine Oualid <dion@thinkmoult.com>
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

# ############################################################################ #

import bpy
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper
import blenderbim.bim.module.sequence.helper as helper
import json
import time
import isodate
from datetime import datetime
from dateutil import parser
import ifcopenshell.util.date as ifcdateutils
import ifcopenshell.util.cost
from ifcopenshell.api.unit.data import Data as UnitData


class Resource(blenderbim.core.tool.Resource):
    @classmethod
    def load_resources(cls):
        def create_new_resource_li(resource, level_index):
            new = bpy.context.scene.BIMResourceTreeProperties.resources.add()
            new.ifc_definition_id = resource.id()
            new.is_expanded = resource.id() not in contracted_resources
            new.level_index = level_index
            if resource.IsNestedBy:
                new.has_children = True
                if new.is_expanded:
                    for rel in resource.IsNestedBy:
                        [
                            create_new_resource_li(nested_resource, level_index + 1)
                            for nested_resource in rel.RelatedObjects
                        ]

        props = bpy.context.scene.BIMResourceProperties
        tprops = bpy.context.scene.BIMResourceTreeProperties
        tprops.resources.clear()
        contracted_resources = json.loads(props.contracted_resources)

        for resource in tool.Ifc.get().by_type("IfcResource"):
            if not resource.HasContext:
                continue
            create_new_resource_li(resource, 0)
        props.is_editing = True

    @classmethod
    def load_resource_properties(cls):
        props = bpy.context.scene.BIMResourceProperties
        tprops = bpy.context.scene.BIMResourceTreeProperties
        props.is_resource_update_enabled = False
        for item in tprops.resources:
            resource = tool.Ifc.get().by_id(item.ifc_definition_id)
            item.name = resource.Name if resource else "Unnamed"
        props.is_resource_update_enabled = True

    @classmethod
    def disable_editing_resource(cls):
        bpy.context.scene.BIMResourceProperties.active_resource_id = 0
        bpy.context.scene.BIMResourceProperties.active_resource_time_id = 0

    @classmethod
    def disable_resource_editing_ui(cls):
        bpy.context.scene.BIMResourceProperties.is_editing = False

    @classmethod
    def load_resource_attributes(cls, resource):
        blenderbim.bim.helper.import_attributes2(resource, bpy.context.scene.BIMResourceProperties.resource_attributes)

    @classmethod
    def enable_editing_resource(cls, resource):
        props = bpy.context.scene.BIMResourceProperties
        props.active_resource_id = resource.id()
        props.resource_attributes.clear()
        props.editing_resource_type = "ATTRIBUTES"

    @classmethod
    def get_resource_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMResourceProperties.resource_attributes)

    @classmethod
    def enable_editing_resource_time(cls, resource):
        props = bpy.context.scene.BIMResourceProperties
        props.resource_time_attributes.clear()
        props.active_resource_time_id = resource.Usage.id()
        props.active_resource_id = resource.id()
        props.editing_resource_type = "USAGE"

    @classmethod
    def get_resource_time(cls, resource):
        return resource.Usage if resource.Usage else None

    @classmethod
    def load_resource_time_attributes(cls, resource_time):
        def callback(name, prop, data):
            if prop.data_type == "string":
                if isinstance(data[name], datetime):
                    prop.string_value = "" if prop.is_null else data[name].isoformat()
                    return True
                elif isinstance(data[name], isodate.Duration):
                    prop.string_value = "" if prop.is_null else ifcdateutils.datetime2ifc(data[name], "IfcDuration")
                    return True

        blenderbim.bim.helper.import_attributes2(
            resource_time, bpy.context.scene.BIMResourceProperties.resource_time_attributes, callback
        )

    @classmethod
    def get_resource_time_attributes(cls):
        def callback(attributes, prop):
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

        props = bpy.context.scene.BIMResourceProperties
        return blenderbim.bim.helper.export_attributes(props.resource_time_attributes, callback)

    @classmethod
    def enable_editing_resource_costs(cls, resource):
        props = bpy.context.scene.BIMResourceProperties
        props.active_resource_id = resource.id()
        props.editing_resource_type = "COSTS"
        resource

    @classmethod
    def disable_editing_resource_cost_value(cls):
        props = bpy.context.scene.BIMResourceProperties
        props.active_cost_value_id = 0
        props.cost_value_editing_type = ""

    @classmethod
    def enable_editing_resource_cost_value_formula(cls, cost_value):
        props = bpy.context.scene.BIMResourceProperties
        props.cost_value_attributes.clear()
        props.active_cost_value_id = cost_value.id()
        props.cost_value_editing_type = "FORMULA"
        props.cost_value_formula = ifcopenshell.util.cost.serialise_cost_value(cost_value) if cost_value else ""

    @classmethod
    def load_cost_value_attributes(cls, cost_value):
        def callback(name, prop, data):
            if name == "AppliedValue":
                # TODO: for now, only support simple IfcValues (which are effectively IfcMonetaryMeasure)
                prop = props.cost_value_attributes.add()
                prop.data_type = "float"
                prop.name = "AppliedValue"
                prop.is_optional = True
                prop.float_value = 0.0 if prop.is_null or not data[name] else data[name][0]
                return True
            elif name == "UnitBasis":
                prop = props.cost_value_attributes.add()
                prop.name = "UnitBasisValue"
                prop.data_type = "float"
                prop.is_null = data["UnitBasis"] is None
                prop.is_optional = True
                if data["UnitBasis"]:
                    prop.float_value = data["UnitBasis"].ValueComponent[0] or 0
                else:
                    prop.float_value = 0

                prop = props.cost_value_attributes.add()
                prop.name = "UnitBasisUnit"
                prop.data_type = "enum"
                prop.is_null = prop.is_optional = False
                units = {}
                if not UnitData.is_loaded:
                    UnitData.load(tool.Ifc.get())
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
                if data["UnitBasis"] and data["UnitBasis"].UnitComponent:
                    name = data["UnitBasis"].UnitComponent.Name
                    unit_type = data["UnitBasis"].UnitComponent.UnitType
                    prop.enum_value = str(data["UnitBasis"].UnitComponent.id())
                return True

        props = bpy.context.scene.BIMResourceProperties
        blenderbim.bim.helper.import_attributes2(cost_value, props.cost_value_attributes, callback)

    @classmethod
    def enable_editing_cost_value_attributes(cls, cost_value):
        props = bpy.context.scene.BIMResourceProperties
        props.cost_value_attributes.clear()
        props.active_cost_value_id = cost_value.id()
        props.cost_value_editing_type = "ATTRIBUTES"

    @classmethod
    def get_resource_cost_value_formula(cls):
        return bpy.context.scene.BIMResourceProperties.cost_value_formula

    @classmethod
    def get_resource_cost_value_attributes(cls):
        def callback(attributes, prop):
            if prop.name == "UnitBasisValue":
                if prop.is_null:
                    attributes["UnitBasis"] = None
                    return True
                attributes["UnitBasis"] = {
                    "ValueComponent": prop.float_value or 1,
                    "UnitComponent": tool.Ifc.get().by_id(
                        int(
                            bpy.context.scene.BIMResourceProperties.cost_value_attributes.get(
                                "UnitBasisUnit"
                            ).enum_value
                        )
                    ),
                }
                return True
            if prop.name == "UnitBasisUnit":
                return True

        return blenderbim.bim.helper.export_attributes(
            bpy.context.scene.BIMResourceProperties.cost_value_attributes, callback
        )

    @classmethod
    def enable_editing_resource_base_quantity(cls, resource):
        props = bpy.context.scene.BIMResourceProperties
        props.active_resource_id = resource.id()
        props.editing_resource_type = "QUANTITY"

    @classmethod
    def enable_editing_resource_quantity(cls, resource_quantity):
        props = bpy.context.scene.BIMResourceProperties
        props.quantity_attributes.clear()
        props.is_editing_quantity = True
        blenderbim.bim.helper.import_attributes2(resource_quantity, props.quantity_attributes)

    @classmethod
    def disable_editing_resource_quantity(cls):
        bpy.context.scene.BIMResourceProperties.is_editing_quantity = False

    @classmethod
    def get_resource_quantity_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMResourceProperties.quantity_attributes)

    @classmethod
    def expand_resource(cls, resource):
        props = bpy.context.scene.BIMResourceProperties
        contracted_resources = json.loads(props.contracted_resources)
        contracted_resources.remove(resource.id())
        props.contracted_resources = json.dumps(contracted_resources)

    @classmethod
    def contract_resource(cls, resource):
        props = bpy.context.scene.BIMResourceProperties
        contracted_resources = json.loads(props.contracted_resources)
        contracted_resources.append(resource.id())
        props.contracted_resources = json.dumps(contracted_resources)

    @classmethod
    def get_selected_products(cls):
        return [
            tool.Ifc.get_entity(obj)
            for obj in bpy.context.selected_objects
            if obj.BIMObjectProperties.ifc_definition_id
        ] or []

    @classmethod
    def import_resources(cls, file_path):
        from ifc4d.csv2ifc import Csv2Ifc

        start = time.time()
        p62ifc = Csv2Ifc()
        p62ifc.csv = file_path
        p62ifc.file = tool.Ifc.get()
        p62ifc.execute()
        print("Importing Resources CSV finished in {:.2f} seconds".format(time.time() - start))
