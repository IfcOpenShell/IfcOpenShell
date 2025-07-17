# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult, Yassine Oualid <dion@thinkmoult.com>
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

# ############################################################################ #

from __future__ import annotations
import bpy
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.bim.helper
import json
import time
import isodate
from datetime import datetime
import ifcopenshell.api.pset
import ifcopenshell.api.resource
import ifcopenshell.util.date as ifcdateutils
import ifcopenshell.util.cost
import ifcopenshell.util.resource
import ifcopenshell.util.constraint
from typing import Any, Union, TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from bonsai.bim.prop import Attribute
    from bonsai.bim.module.resource.prop import BIMResourceProperties, BIMResourceProductivity


class Resource(bonsai.core.tool.Resource):
    @classmethod
    def get_resource_props(cls) -> BIMResourceProperties:
        """
        BIMResourceTreeProperties can be accessed using `.tree`.
        BIMResourceProductivity - using `.productivity`.
        """
        return bpy.context.scene.BIMResourceProperties

    @classmethod
    def load_resources(cls) -> None:
        props = cls.get_resource_props()
        tprops = props.tree

        def create_new_resource_li(resource: ifcopenshell.entity_instance, level_index: int) -> None:
            new = tprops.resources.add()
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

        tprops.resources.clear()
        contracted_resources = json.loads(props.contracted_resources)
        props.is_resource_update_enabled = False
        for resource in tool.Ifc.get().by_type("IfcResource"):
            if not resource.HasContext:
                continue
            create_new_resource_li(resource, 0)
        cls.load_productivity_data()
        cls.load_resource_properties()
        props.is_resource_update_enabled = True
        props.is_editing = True

    @classmethod
    def load_resource_properties(cls) -> None:
        props = cls.get_resource_props()
        tprops = props.tree
        props.is_resource_update_enabled = False
        for item in tprops.resources:
            resource = tool.Ifc.get().by_id(item.ifc_definition_id)
            item.name = resource.Name if resource.Name else "Unnamed"
            item.schedule_usage = (
                resource.Usage.ScheduleUsage if (resource.Usage and resource.Usage.ScheduleUsage) else 0
            )
        props.is_resource_update_enabled = True

    @classmethod
    def disable_editing_resource(cls) -> None:
        props = cls.get_resource_props()
        props.property_unset("active_resource_id")
        props.property_unset("active_resource_time_id")

    @classmethod
    def disable_resource_editing_ui(cls) -> None:
        props = cls.get_resource_props()
        props.property_unset("is_editing")

    @classmethod
    def load_resource_attributes(cls, resource: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        bonsai.bim.helper.import_attributes(resource, props.resource_attributes)

    @classmethod
    def enable_editing_resource(cls, resource: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        props.active_resource_id = resource.id()
        props.resource_attributes.clear()
        props.editing_resource_type = "ATTRIBUTES"
        cls.update_cost_values_ui_data()

    @classmethod
    def get_resource_attributes(cls) -> dict[str, Any]:
        props = cls.get_resource_props()
        return bonsai.bim.helper.export_attributes(props.resource_attributes)

    @classmethod
    def enable_editing_resource_time(cls, resource: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        props.resource_time_attributes.clear()
        props.active_resource_time_id = resource.Usage.id()
        props.active_resource_id = resource.id()
        props.editing_resource_type = "USAGE"
        cls.update_cost_values_ui_data()

    @classmethod
    def get_resource_time(cls, resource: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return resource.Usage or None

    @classmethod
    def load_resource_time_attributes(cls, resource_time: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()

        def callback(name: str, prop: Union[Attribute, None], data: dict[str, Any]) -> None | Literal[True]:
            if prop and prop.data_type == "string":
                if isinstance(data[name], datetime):
                    prop.string_value = "" if prop.is_null else data[name].isoformat()
                    return True
                elif isinstance(data[name], isodate.Duration):
                    prop.string_value = "" if prop.is_null else ifcdateutils.datetime2ifc(data[name], "IfcDuration")
                    return True

        bonsai.bim.helper.import_attributes(resource_time, props.resource_time_attributes, callback)

    @classmethod
    def get_resource_time_attributes(cls) -> dict[str, Any]:
        import bonsai.bim.module.sequence.helper as helper

        def callback(attributes: dict[str, Any], prop: Attribute) -> bool:
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
            return False

        props = cls.get_resource_props()
        return bonsai.bim.helper.export_attributes(props.resource_time_attributes, callback)

    @classmethod
    def enable_editing_resource_costs(cls, resource: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        props.active_resource_id = resource.id()
        props.editing_resource_type = "COSTS"
        cls.update_cost_values_ui_data()

    @classmethod
    def disable_editing_resource_cost_value(cls) -> None:
        props = cls.get_resource_props()
        props.active_cost_value_id = 0
        props.cost_value_editing_type = ""

    @classmethod
    def enable_editing_resource_cost_value_formula(cls, cost_value: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        props.cost_value_attributes.clear()
        props.active_cost_value_id = cost_value.id()
        props.cost_value_editing_type = "FORMULA"
        props.cost_value_formula = ifcopenshell.util.cost.serialise_cost_value(cost_value) if cost_value else ""

    @classmethod
    def load_cost_value_attributes(cls, cost_value: ifcopenshell.entity_instance):
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
                for unit in tool.Ifc.get().by_type("IfcNamedUnit"):
                    if getattr(unit, "UnitType", None) in [
                        "AREAUNIT",
                        "LENGTHUNIT",
                        "TIMEUNIT",
                        "VOLUMEUNIT",
                        "MASSUNIT",
                        "USERDEFINED",
                    ]:
                        if unit.is_a("IfcContextDependentUnit"):
                            units[unit.id()] = f"{unit.is_a()} / {unit.Name}"
                        else:
                            name = unit.Name
                            if getattr(unit, "Prefix", None):
                                name = f"(unit.Prefix) {name}"
                            units[unit.id()] = f"{unit.UnitType} / {name}"
                prop.enum_items = json.dumps(units)
                if data["UnitBasis"] and data["UnitBasis"].UnitComponent:
                    name = data["UnitBasis"].UnitComponent.Name
                    unit_type = data["UnitBasis"].UnitComponent.UnitType
                    prop.enum_value = str(data["UnitBasis"].UnitComponent.id())
                return True

        props = cls.get_resource_props()
        bonsai.bim.helper.import_attributes(cost_value, props.cost_value_attributes, callback)

    @classmethod
    def enable_editing_cost_value_attributes(cls, cost_value: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        props.cost_value_attributes.clear()
        props.active_cost_value_id = cost_value.id()
        props.cost_value_editing_type = "ATTRIBUTES"

    @classmethod
    def get_resource_cost_value_formula(cls):
        props = cls.get_resource_props()
        return props.cost_value_formula

    @classmethod
    def get_resource_cost_value_attributes(cls) -> dict[str, Any]:
        props = cls.get_resource_props()

        def callback(data: dict[str, Any], prop: Attribute) -> bool:
            if prop.name == "UnitBasisValue":
                if prop.is_null:
                    data["UnitBasis"] = None
                    return True
                data["UnitBasis"] = {
                    "ValueComponent": prop.float_value or 1,
                    "UnitComponent": tool.Ifc.get().by_id(int(props.cost_value_attributes["UnitBasisUnit"].enum_value)),
                }
                return True
            if prop.name == "UnitBasisUnit":
                return True
            return False

        return bonsai.bim.helper.export_attributes(props.cost_value_attributes, callback)

    @classmethod
    def enable_editing_resource_base_quantity(cls, resource: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        props.active_resource_id = resource.id()
        props.editing_resource_type = "QUANTITY"
        props.active_resource_class = resource.is_a()
        cls.update_cost_values_ui_data()

    @classmethod
    def enable_editing_resource_quantity(cls, resource_quantity: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        props.quantity_attributes.clear()
        props.is_editing_quantity = True
        bonsai.bim.helper.import_attributes(resource_quantity, props.quantity_attributes)

    @classmethod
    def disable_editing_resource_quantity(cls) -> None:
        props = cls.get_resource_props()
        props.property_unset("is_editing_quantity")

    @classmethod
    def get_resource_quantity_attributes(cls) -> dict[str, Any]:
        props = cls.get_resource_props()
        return bonsai.bim.helper.export_attributes(props.quantity_attributes)

    @classmethod
    def expand_resource(cls, resource: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        contracted_resources = json.loads(props.contracted_resources)
        if not resource.id() in contracted_resources:
            return
        contracted_resources.remove(resource.id())
        props.contracted_resources = json.dumps(contracted_resources)

    @classmethod
    def contract_resource(cls, resource: ifcopenshell.entity_instance) -> None:
        props = cls.get_resource_props()
        contracted_resources = json.loads(props.contracted_resources)
        contracted_resources.append(resource.id())
        props.contracted_resources = json.dumps(contracted_resources)

    @classmethod
    def import_resources(cls, file_path: str) -> None:
        from ifc4d.csv2ifc import Csv2Ifc

        start = time.time()
        csv2ifc = Csv2Ifc(file_path, tool.Ifc.get())
        csv2ifc.execute()
        print("Importing Resources CSV finished in {:.2f} seconds".format(time.time() - start))

    @classmethod
    def export_resources(cls, file_path: str) -> None:
        from ifc4d.csv2ifc import Ifc2Csv

        start = time.time()
        csv2ifc = Ifc2Csv(file_path, tool.Ifc.get())
        csv2ifc.execute()
        print("Importing Resources CSV finished in {:.2f} seconds".format(time.time() - start))

    @classmethod
    def get_highlighted_resource(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = cls.get_resource_props()
        active_resource = props.active_resource
        if active_resource:
            return tool.Ifc.get().by_id(active_resource.ifc_definition_id)

    @classmethod
    def clear_productivity_data(cls, props: BIMResourceProductivity) -> None:
        for duration_prop in props.quantity_consumed or []:
            if duration_prop.name == "BaseQuantityConsumed":
                duration_prop.years = 0
                duration_prop.months = 0
                duration_prop.days = 0
                duration_prop.hours = 0
                duration_prop.minutes = 0
                duration_prop.seconds = 0
        props.quantity_produced = 0
        props.quantity_produced_name = ""

    @classmethod
    def load_productivity_data(cls) -> None:
        duration_props = None
        productivity_props = tool.Resource.get_resource_props().productivity
        for collection_prop in productivity_props.quantity_consumed:
            duration_props = collection_prop if collection_prop.name == "BaseQuantityConsumed" else None
            break
        if not duration_props:
            duration_props = productivity_props.quantity_consumed.add()
            duration_props.name = "BaseQuantityConsumed"
        cls.clear_productivity_data(productivity_props)
        current_resource = tool.Resource.get_highlighted_resource()
        if current_resource:
            productivity = cls.get_productivity(current_resource)
            if productivity:
                productivity_props.quantity_produced = ifcopenshell.util.resource.get_quantity_produced(productivity)
                productivity_props.quantity_produced_name = ifcopenshell.util.resource.get_quantity_produced_name(
                    productivity
                )
                time_consumed = ifcopenshell.util.resource.get_unit_consumed(productivity)
                if time_consumed:
                    import bonsai.bim.module.sequence.helper as helper

                    durations_attributes = helper.parse_duration_as_blender_props(time_consumed)
                    duration_props.years = durations_attributes["years"]
                    duration_props.months = durations_attributes["months"]
                    duration_props.days = durations_attributes["days"]
                    duration_props.hours = durations_attributes["hours"]
                    duration_props.minutes = durations_attributes["minutes"]
                    duration_props.seconds = durations_attributes["seconds"]

    @classmethod
    def get_productivity_attributes(cls) -> dict[str, Any]:
        props = tool.Resource.get_resource_props().productivity
        productivity = {}
        if props.quantity_consumed:
            import bonsai.bim.module.sequence.helper as helper

            productivity["BaseQuantityConsumed"] = helper.blender_props_to_iso_duration(
                props.quantity_consumed, "ELAPSEDTIME", "BaseQuantityConsumed"
            )
        productivity["BaseQuantityProducedValue"] = props.quantity_produced
        productivity["BaseQuantityProducedName"] = props.quantity_produced_name
        return productivity

    @classmethod
    def get_productivity(
        cls, resource: ifcopenshell.entity_instance, should_inherit: bool = False
    ) -> ifcopenshell.util.resource.PRODUCTIVITY_PSET_DATA:
        return ifcopenshell.util.resource.get_productivity(resource, should_inherit=should_inherit)

    @classmethod
    def edit_productivity_pset(cls, resource, attributes):
        productivity = cls.get_productivity(resource)
        if not productivity:
            return
        ifc_file = tool.Ifc.get()
        return ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=ifc_file.by_id(productivity["id"]),
            properties=attributes,
        )

    @classmethod
    def get_constraints(cls, resource: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.constraint.get_constraints(product=resource)

    @classmethod
    def get_metrics(cls, constraint: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.constraint.get_metrics(constraint)

    @classmethod
    def get_metric_reference(cls, metric: ifcopenshell.entity_instance, is_deep: bool = True):
        return ifcopenshell.util.constraint.get_metric_reference(metric, is_deep=is_deep)

    @classmethod
    def has_metric_constraint(cls, resource: ifcopenshell.entity_instance, attribute):
        metrics = ifcopenshell.util.constraint.get_metric_constraints(resource, attribute)
        return True if metrics else False

    @classmethod
    def run_edit_resource_time(cls, resource: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
        ifc_file = tool.Ifc.get()
        if not resource.Usage:
            ifcopenshell.api.resource.add_resource_time(
                ifc_file,
                resource=resource,
            )
        ifcopenshell.api.resource.edit_resource_time(ifc_file, resource_time=resource.Usage, attributes=attributes)

    @classmethod
    def go_to_resource(cls, resource: ifcopenshell.entity_instance) -> None:
        def get_ancestors_ids(resource: ifcopenshell.entity_instance) -> list[int]:
            ids: list[int] = []
            for rel in resource.Nests or []:
                ids.append(rel.RelatingObject.id())
                ids.extend(get_ancestors_ids(rel.RelatingObject))
            return ids

        props = cls.get_resource_props()
        ancestors = get_ancestors_ids(resource)
        contracted_resources = json.loads(props.contracted_resources)
        for ancestor in ancestors:
            if ancestor in contracted_resources:
                contracted_resources.remove(ancestor)
        props.contracted_resources = json.dumps(contracted_resources)
        cls.load_resources()

        expanded_resources = [item.ifc_definition_id for item in props.tree.resources]
        props.active_resource_index = expanded_resources.index(resource.id())

    @classmethod
    def run_calculate_resource_usage(cls, resource: ifcopenshell.entity_instance) -> None:
        ifcopenshell.api.resource.calculate_resource_usage(tool.Ifc.get(), resource=resource)

    @classmethod
    def calculate_resource_quantity(cls, resource: ifcopenshell.entity_instance) -> None:
        quantity: ifcopenshell.entity_instance = resource.BaseQuantity
        quantity_from_products = ifcopenshell.util.resource.get_total_quantity_produced(resource, quantity.Name)
        quantity[3] = quantity_from_products

    @classmethod
    def get_task_assignments(cls, resource: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.resource.get_task_assignments(resource)

    @classmethod
    def get_nested_resources(cls, resource: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.resource.get_nested_resources(resource)

    @classmethod
    def is_attribute_locked(cls, resource: ifcopenshell.entity_instance, attribute) -> bool:
        return ifcopenshell.util.constraint.is_attribute_locked(resource, attribute)

    @classmethod
    def update_cost_values_ui_data(cls) -> None:
        from bonsai.bim.module.resource.data import ResourceData

        if not ResourceData.is_loaded:
            return
        ResourceData.data["cost_values"] = ResourceData.cost_values()
