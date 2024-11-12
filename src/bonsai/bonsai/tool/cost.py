import os
import bpy
import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.date
import ifcopenshell.util.cost
import ifcopenshell.util.unit
import bonsai.bim.helper
import json
from typing import Optional, Any, Generator, Union, Literal


class Cost(bonsai.core.tool.Cost):

    RELATED_OBJECT_TYPE = Literal["PRODUCT", "PROCESS", "RESOURCE"]

    @classmethod
    def get_cost_schedule_attributes(cls) -> dict[str, Any]:
        props = bpy.context.scene.BIMCostProperties
        return bonsai.bim.helper.export_attributes(props.cost_schedule_attributes)

    @classmethod
    def disable_editing_cost_schedule(cls) -> None:
        cls.store_active_schedule_columns()
        bpy.context.scene.BIMCostProperties.active_cost_schedule_id = 0
        cls.disable_editing_cost_item()

    @classmethod
    def load_active_schedule_columns(cls) -> None:
        props = bpy.context.scene.BIMCostProperties
        active_columns = props.columns
        storage = props.columns_storage
        active_cost_schedule_id = cls.get_active_cost_schedule().id()

        # store column names to keep the original order
        cols_to_add = []

        # collection property only support removal by index
        for storage_col_i, storage_col in reversed(list(enumerate(storage[:]))):
            if storage_col.schedule_id != active_cost_schedule_id:
                continue
            cols_to_add.insert(0, storage_col.name)
            # We don't store active schedule columns in storage
            # so it will be easy to edit them.
            storage.remove(storage_col_i)

        for col_name in cols_to_add:
            col = active_columns.add()
            col.name = col_name

    @classmethod
    def store_active_schedule_columns(cls) -> None:
        props = bpy.context.scene.BIMCostProperties
        active_columns = props.columns
        storage = props.columns_storage
        active_cost_schedule_id = cls.get_active_cost_schedule().id()

        for col in active_columns:
            storage_col = storage.add()
            storage_col.name = col.name
            storage_col.schedule_id = active_cost_schedule_id

        props.columns.clear()

    @classmethod
    def remove_stored_schedule_columns(cls, cost_schedule: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        storage = props.columns_storage
        active_cost_schedule_id = cost_schedule.id()

        # collection property only support removal by index
        for storage_col_i, storage_col in reversed(list(enumerate(storage[:]))):
            if storage_col.schedule_id != active_cost_schedule_id:
                continue
            storage.remove(storage_col_i)

    @classmethod
    def enable_editing_cost_schedule_attributes(cls, cost_schedule: ifcopenshell.entity_instance) -> None:
        bpy.context.scene.BIMCostProperties.active_cost_schedule_id = cost_schedule.id()
        bpy.context.scene.BIMCostProperties.is_editing = "COST_SCHEDULE_ATTRIBUTES"

    @classmethod
    def load_cost_schedule_attributes(cls, cost_schedule: ifcopenshell.entity_instance) -> None:
        def special_import(name, prop, data):
            if name in ["SubmittedOn", "UpdateDate"]:
                prop.string_value = "" if prop.is_null else ifcopenshell.util.date.ifc2datetime(data[name]).isoformat()
                return True

        props = bpy.context.scene.BIMCostProperties
        props.cost_schedule_attributes.clear()
        bonsai.bim.helper.import_attributes2(cost_schedule, props.cost_schedule_attributes, callback=special_import)

    @classmethod
    def enable_editing_cost_items(cls, cost_schedule: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.active_cost_schedule_id = cost_schedule.id()
        props.is_editing = "COST_ITEMS"

    @classmethod
    def play_sound(cls) -> None:
        if tool.Blender.get_addon_preferences().should_play_chaching_sound:
            cls.play_chaching_sound()  # lol

    @classmethod
    def play_chaching_sound(cls) -> None:
        # TODO: make pitch higher as costs rise
        try:
            import aud

            device = aud.Device()
            # chaching.mp3 is by Lucish_ CC-BY-3.0 https://freesound.org/people/Lucish_/sounds/554841/
            sound = aud.Sound(os.path.join(bpy.context.scene.BIMProperties.data_dir, "chaching.mp3"))
            handle = device.play(sound)
            sound_buffered = aud.Sound.buffer(sound)
            handle_buffered = device.play(sound_buffered)
            handle.stop()
            handle_buffered.stop()
        except:
            pass  # ah well

    @classmethod
    def load_cost_schedule_tree(cls) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.is_cost_update_enabled = False
        cost_schedule = tool.Ifc.get().by_id(props.active_cost_schedule_id)
        props.cost_items.clear()
        cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        [
            cls.create_new_cost_item_li(props.cost_items, cost_item, 0, type="cost")
            for rel in cost_schedule.Controls or []
            for cost_item in rel.RelatedObjects or []
        ]
        props.is_cost_update_enabled = True

    @classmethod
    def expand_cost_item(cls, cost_item: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        if not hasattr(cls, "contracted_cost_items"):
            cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        if cost_item.id() in cls.contracted_cost_items:
            cls.contracted_cost_items.remove(cost_item.id())
            props.contracted_cost_items = json.dumps(cls.contracted_cost_items)

    @classmethod
    def expand_cost_items(cls) -> None:
        props = bpy.context.scene.BIMCostProperties
        cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        for cost_item in props.cost_items:
            if cost_item.ifc_definition_id in cls.contracted_cost_items:
                cls.contracted_cost_items.remove(cost_item.ifc_definition_id)
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)

    @classmethod
    def contract_cost_item(cls, cost_item: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        if not hasattr(cls, "contracted_cost_items"):
            cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        cls.contracted_cost_items.append(cost_item.id())
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)

    @classmethod
    def contract_cost_items(cls) -> None:
        props = bpy.context.scene.BIMCostProperties
        if not hasattr(cls, "contracted_cost_items"):
            cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        for cost_item in props.cost_items:
            if cost_item.ifc_definition_id not in cls.contracted_cost_items:
                cls.contracted_cost_items.append(cost_item.ifc_definition_id)
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)

    @classmethod
    def clean_up_cost_item_tree(cls, cost_item_id: int) -> None:
        props = bpy.context.scene.BIMCostProperties
        if not hasattr(cls, "contracted_cost_items"):
            cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        if props.active_cost_item_id == cost_item_id:
            props.active_cost_item_id = 0
        if props.active_cost_item_index in cls.contracted_cost_items:
            cls.contracted_cost_items.remove(props.active_cost_item_index)
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)
        cls.enable_editing_cost_items(cost_schedule=tool.Ifc.get().by_id(props.active_cost_schedule_id))

    @classmethod
    def enable_editing_cost_item_attributes(cls, cost_item: ifcopenshell.entity_instance):
        bpy.context.scene.BIMCostProperties.active_cost_item_id = cost_item.id()
        bpy.context.scene.BIMCostProperties.cost_item_editing_type = "ATTRIBUTES"

    @classmethod
    def load_cost_item_attributes(cls, cost_item: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.cost_item_attributes.clear()
        bonsai.bim.helper.import_attributes2(cost_item, props.cost_item_attributes)

    @classmethod
    def disable_editing_cost_item(cls) -> None:
        bpy.context.scene.BIMCostProperties.active_cost_item_id = 0
        bpy.context.scene.BIMCostProperties.change_cost_item_parent = False

    @classmethod
    def get_cost_item_attributes(cls) -> dict[str, Any]:
        props = bpy.context.scene.BIMCostProperties
        return bonsai.bim.helper.export_attributes(props.cost_item_attributes)

    @classmethod
    def get_active_cost_item(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = bpy.context.scene.BIMCostProperties
        if not props.active_cost_item_id:
            return None
        return tool.Ifc.get().by_id(bpy.context.scene.BIMCostProperties.active_cost_item_id)

    @classmethod
    def get_highlighted_cost_item(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = bpy.context.scene.BIMCostProperties
        if not props.active_cost_schedule_id:
            return
        if props.active_cost_item_index < len(props.cost_items):
            return tool.Ifc.get().by_id(props.cost_items[props.active_cost_item_index].ifc_definition_id)
        return

    @classmethod
    def load_cost_item_types(cls, cost_item: Optional[ifcopenshell.entity_instance] = None) -> None:
        if not cost_item:
            cost_item = cls.get_highlighted_cost_item()
            if not cost_item:
                return
        props = bpy.context.scene.BIMCostProperties
        props.cost_item_type_products.clear()
        # TODO implement process and resource types
        # props.cost_item_processes.clear()
        # props.cost_item_resources.clear()
        for rel in cost_item.Controls or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcTypeProduct"):
                    new = props.cost_item_type_products.add()
                # TODO implement process and resource types
                # elif related_object.is_a("IfcProcess"):
                #    new = props.cost_item_processes.add()
                # elif related_object.is_a("IfcResource"):
                #    new = props.cost_item_resources.add()
                new.ifc_definition_id = related_object.id()
                new.name = related_object.Name or "Unnamed"

    @classmethod
    def load_cost_item_quantity_assignments(
        cls, cost_item: ifcopenshell.entity_instance, related_object_type: RELATED_OBJECT_TYPE
    ) -> None:
        def create_list_items(
            collection: bpy.types.bpy_prop_collection, cost_item: ifcopenshell.entity_instance, is_deep: bool
        ) -> None:
            products = cls.get_cost_item_assignments(cost_item, filter_by_type=related_object_type, is_deep=False)
            for product in products:
                new = collection.add()
                new.ifc_definition_id = product.id()
                new.name = product.Name or "Unnamed"
                total_quantity, unit = cls.calculate_parametric_quantity(cost_item, product)
                new.total_quantity = total_quantity or 0
                new.unit_symbol = unit or ""
            if is_deep:
                for cost_item in ifcopenshell.util.cost.get_nested_cost_items(cost_item, is_deep):
                    create_list_items(collection, cost_item, is_deep=False)

        props = bpy.context.scene.BIMCostProperties
        if related_object_type == "PRODUCT":
            props.cost_item_products.clear()
            is_deep = bpy.context.scene.BIMCostProperties.show_nested_elements
            create_list_items(props.cost_item_products, cost_item, is_deep)
        elif related_object_type == "PROCESS":
            props.cost_item_processes.clear()
            is_deep = bpy.context.scene.BIMCostProperties.show_nested_tasks
            create_list_items(props.cost_item_processes, cost_item, is_deep)
        elif related_object_type == "RESOURCE":
            props.cost_item_resources.clear()
            is_deep = bpy.context.scene.BIMCostProperties.show_nested_resources
            create_list_items(props.cost_item_resources, cost_item, is_deep)

    @classmethod
    def calculate_parametric_quantity(
        cls, cost_item: ifcopenshell.entity_instance, product: ifcopenshell.entity_instance
    ) -> tuple[float, Union[str, None]]:
        quantities, unit = cls.get_assigned_quantities(cost_item, product)
        return sum(quantity[3] for quantity in quantities), unit

    @classmethod
    def get_assigned_quantities(
        cls, cost_item: ifcopenshell.entity_instance, product: ifcopenshell.entity_instance
    ) -> tuple[list[ifcopenshell.entity_instance], Union[str, None]]:
        selected_quantitites = []
        unit = None
        cost_quantities = cost_item.CostQuantities
        if not cost_quantities:
            return selected_quantitites, unit

        cost_quantities = set(cost_quantities)
        for quantities in ifcopenshell.util.element.get_psets(product, qtos_only=True).values():
            for qto in tool.Ifc.get().by_id(quantities["id"]).Quantities or []:
                if qto in cost_quantities:
                    selected_quantitites.append(qto)
        unit = next((symbol for q in cost_quantities if (symbol := cls.get_quantity_unit_symbol(q))), None)
        return selected_quantitites, unit

    @classmethod
    def get_assigned_product(cls, cost_item, quantity):
        assigned_products = cls.get_cost_item_assignments(cost_item, filter_by_type="PRODUCT", is_deep=False)
        for product in assigned_products:
            assigned_quantities, _ = cls.get_assigned_quantities(cost_item, product)
            if quantity in assigned_quantities:
                return product

    @classmethod
    def get_products(cls, related_object_type: RELATED_OBJECT_TYPE) -> list[ifcopenshell.entity_instance]:
        if related_object_type == "PRODUCT":
            products = list(tool.Spatial.get_selected_products())
        elif related_object_type == "PROCESS":
            products = [tool.Sequence.get_highlighted_task()]
        elif related_object_type == "RESOURCE":
            products = [tool.Resource.get_highlighted_resource()]
        return products or []

    @classmethod
    def enable_editing_cost_item_quantities(cls, cost_item: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.active_cost_item_id = cost_item.id()
        props.cost_item_editing_type = "QUANTITIES"

    @classmethod
    def enable_editing_cost_item_quantity(cls, physical_quantity: ifcopenshell.entity_instance) -> None:
        bpy.context.scene.BIMCostProperties.active_cost_item_quantity_id = physical_quantity.id()

    @classmethod
    def load_cost_item_quantity_attributes(cls, physical_quantity: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.quantity_attributes.clear()
        bonsai.bim.helper.import_attributes2(physical_quantity, props.quantity_attributes)

    @classmethod
    def enable_editing_cost_item_values(cls, cost_item: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.active_cost_item_id = cost_item.id()
        props.cost_item_editing_type = "VALUES"

    @classmethod
    def disable_editing_cost_item_quantity(cls) -> None:
        bpy.context.scene.BIMCostProperties.active_cost_item_quantity_id = 0

    @classmethod
    def get_cost_item_quantity_attributes(cls) -> dict[str, Any]:
        props = bpy.context.scene.BIMCostProperties
        return bonsai.bim.helper.export_attributes(props.quantity_attributes)

    @classmethod
    def get_attributes_for_cost_value(
        cls, cost_type: Literal["FIXED", "SUM", "CATEGORY"], cost_category: Optional[str] = None
    ) -> dict[str, Any]:
        if cost_type == "FIXED":
            category = None
            attributes = {"AppliedValue": bpy.context.scene.BIMCostProperties.fixed_cost_value}
        elif cost_type == "SUM":
            category = "*"
            attributes = {"Category": category}
        elif cost_type == "CATEGORY":
            category = cost_category
            attributes = {"Category": category}
        return attributes

    @classmethod
    def load_cost_item_value_attributes(cls, cost_value: ifcopenshell.entity_instance) -> None:
        def import_attributes(name, prop, data, cost_value, is_rates, props_collection):
            if name == "AppliedValue":
                # TODO: for now, only support simple IfcValues (which are effectively IfcMonetaryMeasure)
                prop = props_collection.add()
                prop.data_type = "float"
                prop.name = "AppliedValue"
                prop.is_optional = True
                prop.float_value = (
                    0.0
                    if prop.is_null
                    else cls.calculate_applied_value(tool.Ifc.get().by_id(props.active_cost_item_id), cost_value)
                )
                return True
            if name == "UnitBasis" and is_rates:
                prop = props_collection.add()
                prop.name = "UnitBasisValue"
                prop.data_type = "float"
                prop.is_null = data["UnitBasis"] is None
                prop.is_optional = True
                if data["UnitBasis"] and data["UnitBasis"].ValueComponent:
                    prop.float_value = data["UnitBasis"].ValueComponent.wrappedValue or 0
                else:
                    prop.float_value = 0

                prop = props_collection.add()
                prop.name = "UnitBasisUnit"
                prop.data_type = "enum"
                prop.is_null = prop.is_optional = False
                units = cls.get_units()
                prop.enum_items = json.dumps(units)
                if data["UnitBasis"] and data["UnitBasis"].UnitComponent:
                    for key, value in json.loads(prop.enum_items).items():
                        if value == cls.format_unit(data["UnitBasis"].UnitComponent):
                            prop.enum_value = key
                            break
                return True

        props = bpy.context.scene.BIMCostProperties
        props.cost_value_attributes.clear()
        is_rates = cls.is_active_schedule_of_rates()
        callback = lambda name, prop, data: import_attributes(
            name, prop, data, cost_value, is_rates, props.cost_value_attributes
        )
        bonsai.bim.helper.import_attributes2(cost_value, props.cost_value_attributes, callback=callback)

    @classmethod
    def calculate_applied_value(
        cls, cost_item: ifcopenshell.entity_instance, cost_value: ifcopenshell.entity_instance
    ) -> float:
        return ifcopenshell.util.cost.calculate_applied_value(cost_item, cost_value)

    @classmethod
    def is_active_schedule_of_rates(cls) -> bool:
        return (
            tool.Ifc.get().by_id(bpy.context.scene.BIMCostProperties.active_cost_schedule_id).PredefinedType
            == "SCHEDULEOFRATES"
        )

    @classmethod
    def enable_editing_cost_item_value(cls, cost_value: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.active_cost_value_id = cost_value.id()
        props.cost_value_editing_type = "ATTRIBUTES"

    @classmethod
    def disable_editing_cost_item_value(cls) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.active_cost_value_id = 0
        props.cost_value_editing_type = ""

    @classmethod
    def load_cost_item_value_formula_attributes(cls, cost_value: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.cost_value_attributes.clear()
        bpy.context.scene.BIMCostProperties.cost_value_formula = ifcopenshell.util.cost.serialise_cost_value(cost_value)

    @classmethod
    def enable_editing_cost_item_value_formula(cls, cost_value: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.active_cost_value_id = cost_value.id()
        props.cost_value_editing_type = "FORMULA"

    @classmethod
    def get_cost_item_value_formula(cls) -> str:
        return bpy.context.scene.BIMCostProperties.cost_value_formula

    @classmethod
    def get_cost_value_attributes(cls) -> dict[str, Any]:
        def export_attributes(attributes, prop):
            if prop.name == "UnitBasisValue":
                if prop.is_null:
                    attributes["UnitBasis"] = None
                    return True
                attributes["UnitBasis"] = {
                    "ValueComponent": prop.float_value or 1,
                    "UnitComponent": cls.get_cost_value_unit_component(),
                }
                return True
            if prop.name == "UnitBasisUnit":
                return True

        props = bpy.context.scene.BIMCostProperties
        callback = lambda attributes, prop: export_attributes(attributes, prop)
        return bonsai.bim.helper.export_attributes(props.cost_value_attributes, callback)

    @classmethod
    def get_cost_value_unit_component(cls) -> ifcopenshell.entity_instance:
        return tool.Ifc.get().by_id(
            int(bpy.context.scene.BIMCostProperties.cost_value_attributes.get("UnitBasisUnit").enum_value)
        )

    @classmethod
    def get_cost_item_assignments(
        cls,
        cost_item: ifcopenshell.entity_instance,
        filter_by_type: Optional[ifcopenshell.util.cost.FILTER_BY_TYPE] = None,
        is_deep: bool = False,
    ) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.cost.get_cost_item_assignments(
            cost_item, filter_by_type=filter_by_type, is_deep=is_deep
        )

    @classmethod
    def show_nested_cost_item_elements(cls) -> bool:
        return bpy.context.scene.BIMCostProperties.show_nested_elements

    @classmethod
    def get_cost_item_products(
        cls, cost_item: ifcopenshell.entity_instance, is_deep: bool = False
    ) -> list[ifcopenshell.entity_instance]:
        return cls.get_cost_item_assignments(cost_item, filter_by_type="PRODUCT", is_deep=is_deep)

    @classmethod
    def get_cost_item_resources(
        cls, cost_item: ifcopenshell.entity_instance, is_deep: bool = False
    ) -> list[ifcopenshell.entity_instance]:
        return cls.get_cost_item_assignments(cost_item, filter_by_type="RESOURCE", is_deep=is_deep)

    @classmethod
    def get_cost_item_processes(
        cls, cost_item: ifcopenshell.entity_instance, is_deep: bool = False
    ) -> list[ifcopenshell.entity_instance]:
        return cls.get_cost_item_assignments(cost_item, filter_by_type="PROCESS", is_deep=is_deep)

    @classmethod
    def get_schedule_cost_items(
        cls, cost_schedule: ifcopenshell.entity_instance
    ) -> Generator[ifcopenshell.entity_instance, None, None]:
        return ifcopenshell.util.cost.get_schedule_cost_items(cost_schedule)

    @classmethod
    def get_cost_schedule_products(
        cls, cost_schedule: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        products = []
        for cost_item in ifcopenshell.util.cost.get_schedule_cost_items(cost_schedule):
            products.extend(cls.get_cost_item_products(cost_item))
        return products

    @classmethod
    def import_cost_schedule_csv(cls, file_path: Optional[str] = None, is_schedule_of_rates: bool = False) -> None:
        if not file_path:
            return
        from ifc5d.csv2ifc import Csv2Ifc
        import time

        start = time.time()
        csv2ifc = Csv2Ifc()
        csv2ifc.csv = file_path
        csv2ifc.file = tool.Ifc.get()
        csv2ifc.is_schedule_of_rates = is_schedule_of_rates
        csv2ifc.execute()
        print("Import finished in {:.2f} seconds".format(time.time() - start))

    @classmethod
    def add_cost_column(cls, name: str) -> None:
        props = bpy.context.scene.BIMCostProperties
        new = props.columns.add()
        new.name = name

    @classmethod
    def remove_cost_column(cls, name: str) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.columns.remove(props.columns.find(name))

    @classmethod
    def expand_cost_item_rate(cls, cost_item: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        contracted_cost_item_rates = json.loads(props.contracted_cost_item_rates)
        contracted_cost_item_rates.remove(cost_item)
        props.contracted_cost_item_rates = json.dumps(contracted_cost_item_rates)
        cls.load_schedule_of_rates_tree(schedule_of_rates=tool.Ifc.get().by_id(int(props.schedule_of_rates)))

    @classmethod
    def contract_cost_item_rate(cls, cost_item: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        contracted_cost_item_rates = json.loads(props.contracted_cost_item_rates)
        contracted_cost_item_rates.append(cost_item)
        props.contracted_cost_item_rates = json.dumps(contracted_cost_item_rates)
        cls.load_schedule_of_rates_tree(schedule_of_rates=tool.Ifc.get().by_id(int(props.schedule_of_rates)))

    @classmethod
    def create_new_cost_item_li(
        cls, props_collection, cost_item: ifcopenshell.entity_instance, level_index: int, type: str = "cost_rate"
    ) -> None:
        new = props_collection.add()
        new.ifc_definition_id = cost_item.id()
        new.name = cost_item.Name or "Unnamed"
        new.identification = cost_item.Identification or "XXX"
        new.is_expanded = (
            cost_item.id() not in cls.contracted_cost_item_rates
            if type == "cost_rate"
            else cost_item.id() not in cls.contracted_cost_items
        )
        new.level_index = level_index
        if cost_item.IsNestedBy:
            new.has_children = True
            if new.is_expanded:
                [
                    cls.create_new_cost_item_li(props_collection, sub_cost_item, level_index + 1, type)
                    for rel in cost_item.IsNestedBy
                    for sub_cost_item in rel.RelatedObjects
                ]

    @classmethod
    def load_schedule_of_rates_tree(cls, schedule_of_rates: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.is_cost_update_enabled = False
        props.cost_item_rates.clear()
        props.columns.clear()
        cls.contracted_cost_item_rates = json.loads(props.contracted_cost_item_rates)
        for rel in schedule_of_rates.Controls or []:
            [
                cls.create_new_cost_item_li(props.cost_item_rates, cost_item, 0, type="cost_rate")
                for cost_item in rel.RelatedObjects
            ]
        props.is_cost_update_enabled = True

    @classmethod
    def export_cost_schedules(
        cls, filepath: str, format: str, cost_schedule: Optional[ifcopenshell.entity_instance] = None
    ) -> Union[str, None]:
        import subprocess
        import os
        import sys

        if filepath:
            path = filepath
        else:
            path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "build", "cost_schedules")

        if not os.path.exists(path):
            os.makedirs(path)
        if format == "CSV":
            from ifc5d.ifc5Dspreadsheet import Ifc5DCsvWriter

            writer = Ifc5DCsvWriter(file=tool.Ifc.get(), output=path, cost_schedule=cost_schedule)
            writer.write()
        elif format == "ODS":
            from ifc5d.ifc5Dspreadsheet import Ifc5DOdsWriter

            writer = Ifc5DOdsWriter(file=tool.Ifc.get(), output=path, cost_schedule=cost_schedule)
            writer.write()
        elif format == "XLSX":
            from ifc5d.ifc5Dspreadsheet import Ifc5DXlsxWriter

            writer = Ifc5DXlsxWriter(file=tool.Ifc.get(), output=path, cost_schedule=cost_schedule)
            writer.write()
        try:
            if path:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.call(["open", path])
                elif sys.platform == "linux":
                    subprocess.call(["xdg-open", path])
        except:
            return "Could not open file location"

    @classmethod
    def get_units(cls) -> dict[int, str]:
        units = {}
        for unit in tool.Ifc.get().by_type("IfcNamedUnit"):
            if unit.get_info().get("UnitType", None) in [
                "AREAUNIT",
                "LENGTHUNIT",
                "TIMEUNIT",
                "VOLUMEUNIT",
                "MASSUNIT",
                "USERDEFINED",
            ]:
                units[unit.id()] = cls.format_unit(unit)
        return units

    @staticmethod
    def format_unit(unit: ifcopenshell.entity_instance) -> str:
        if unit.is_a("IfcContextDependentUnit"):
            return f"{unit.UnitType} / {unit.Name}"
        else:
            name = unit.Name
            if unit.get_info().get("Prefix", None):
                name = f"{unit.Prefix} {name}"
            return f"{unit.UnitType} / {name}"

    @classmethod
    def get_cost_schedule(cls, cost_item: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        return ifcopenshell.util.cost.get_cost_schedule(cost_item)

    @classmethod
    def is_cost_schedule_active(cls, cost_schedule: ifcopenshell.entity_instance) -> bool:
        return True if cost_schedule.id() == bpy.context.scene.BIMCostProperties.active_cost_schedule_id else False

    @classmethod
    def get_active_cost_schedule(cls) -> Union[ifcopenshell.entity_instance, None]:
        if not bpy.context.scene.BIMCostProperties.active_cost_schedule_id:
            return None
        return tool.Ifc.get().by_id(bpy.context.scene.BIMCostProperties.active_cost_schedule_id)

    @classmethod
    def highlight_cost_item(cls, cost_item: ifcopenshell.entity_instance) -> None:
        def expand_ancestors(cost_item):
            cls.expand_cost_item(cost_item)
            for rel in cost_item.Nests or []:
                parent_cost = rel.RelatingObject if rel.RelatingObject.is_a("IfcCostItem") else None
                if parent_cost:
                    expand_ancestors(parent_cost)
            cls.load_cost_schedule_tree()

        cost_props = bpy.context.scene.BIMCostProperties
        if not cost_item.id() in [item.ifc_definition_id for item in cost_props.cost_items]:
            expand_ancestors(cost_item)
        cost_item_index = [item.ifc_definition_id for item in bpy.context.scene.BIMCostProperties.cost_items].index(
            cost_item.id()
        ) or 0
        bpy.context.scene.BIMCostProperties.active_cost_item_index = cost_item_index

    @classmethod
    def get_cost_items_for_product(cls, product: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.cost.get_cost_items_for_product(product)

    @classmethod
    def has_cost_assignments(
        cls, product: ifcopenshell.entity_instance, cost_schedule: Optional[ifcopenshell.entity_instance] = None
    ) -> bool:
        cost_items = ifcopenshell.util.cost.get_cost_items_for_product(product)
        if cost_schedule:
            cost_items = [
                cost_item for cost_item in cost_items or [] if cls.get_cost_schedule(cost_item) == cost_schedule
            ]
        return bool(cost_items)

    @classmethod
    def load_product_cost_items(cls, product: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMCostProperties
        props.is_cost_update_enabled = False
        props.product_cost_items.clear()
        cost_items = ifcopenshell.util.cost.get_cost_items_for_product(product)
        if cost_items:
            for cost_item in cost_items:
                new = props.product_cost_items.add()
                new.name = cost_item.Name or "Unnamed"
                new.ifc_definition_id = cost_item.id()
                quantity, unit = cls.calculate_parametric_quantity(cost_item, product)
                new.total_quantity = quantity or 1
                new.unit_symbol = unit or ""
                new.total_cost_quantity = ifcopenshell.util.cost.get_total_quantity(cost_item)

    @classmethod
    def get_quantity_unit_symbol(cls, quantity: ifcopenshell.entity_instance) -> Union[str, None]:
        unit = ifcopenshell.util.unit.get_property_unit(quantity, tool.Ifc.get())
        if unit:
            return ifcopenshell.util.unit.get_unit_symbol(unit)
        else:
            return None

    @classmethod
    def is_root_cost_item(cls, cost_item: ifcopenshell.entity_instance) -> bool:
        if cost_item.HasAssignments:
            for rel in cost_item.HasAssignments:
                if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcCostSchedule"):
                    return True
        return False

    @classmethod
    def toggle_cost_item_parent_change(cls, cost_item: Optional[ifcopenshell.entity_instance] = None) -> None:
        if not cost_item:
            return
        props = bpy.context.scene.BIMCostProperties
        if props.change_cost_item_parent:
            props.active_cost_item_id = cost_item.id()
            props.cost_item_editing_type = "PARENT"
        else:
            cls.disable_editing_cost_item_parent()

    @classmethod
    def change_parent_cost_item(
        cls, cost_item: ifcopenshell.entity_instance, new_parent: ifcopenshell.entity_instance
    ) -> None:
        ifcopenshell.api.run("nest.change_nest", tool.Ifc.get(), item=cost_item, new_parent=new_parent)

    @classmethod
    def disable_editing_cost_item_parent(cls) -> None:
        bpy.context.scene.BIMCostProperties.active_cost_item_id = 0
        bpy.context.scene.BIMCostProperties.change_cost_item_parent = False

    @classmethod
    def load_cost_item_quantities(cls, cost_item: Optional[ifcopenshell.entity_instance] = None) -> None:
        if not cost_item:
            cost_item = cls.get_highlighted_cost_item()
        if not cost_item:
            return
        cls.load_cost_item_quantity_assignments(cost_item, related_object_type="PRODUCT")
        cls.load_cost_item_quantity_assignments(cost_item, related_object_type="PROCESS")
        cls.load_cost_item_quantity_assignments(cost_item, related_object_type="RESOURCE")

    @classmethod
    def update_cost_items(
        cls, product: Optional[ifcopenshell.entity_instance] = None, pset: Optional[ifcopenshell.entity_instance] = None
    ) -> None:
        cost_items = []
        if product:
            cost_items = ifcopenshell.util.cost.get_cost_items_for_product(product)
        if pset:

            def get_products_from_pset(pset):
                products = []
                for rel in pset.DefinesOccurrence or []:
                    if rel.is_a("IfcRelDefinesByProperties"):
                        products.extend(rel.RelatedObjects)
                return products

            products = get_products_from_pset(pset)
            for product in products or []:
                cost_items.extend(ifcopenshell.util.cost.get_cost_items_for_product(product))
        for cost_item in cost_items:
            cls.load_cost_item_quantity_assignments(cost_item, related_object_type="PRODUCT")

    @classmethod
    def has_schedules(cls) -> bool:
        return bool(tool.Ifc.get().by_type("IfcCostSchedule"))

    @classmethod
    def get_currency_attributes(cls) -> dict[str, str]:
        props = bpy.context.scene.BIMCostProperties
        currency = props.currency
        if currency == "CUSTOM":
            currency = props.custom_currency
        return {
            "Currency": currency,
        }

    @classmethod
    def create_cost_schedule_json(cls, cost_schedule: ifcopenshell.entity_instance) -> dict:
        from bonsai.bim.module.cost.data import CostSchedulesData

        CostSchedulesData.load()
        cost_items = CostSchedulesData.data["cost_items"]
        data = []
        for rel in cost_schedule.Controls or []:
            for cost_item in rel.RelatedObjects or []:
                cls.create_cost_item_json(cost_item, cost_items, data)
        return data

    @classmethod
    def create_cost_item_json(cls, cost_item: ifcopenshell.entity_instance, cost_items: dict, data: list):
        if cost_item.id() in cost_items.keys():
            cost_item_data = cost_items[cost_item.id()]
            cost_item_data["id"] = cost_item.id()
            cost_item_data["name"] = cost_item.Name
            cost_item_data["is_nested_by"] = []
            cost_item_data["is_sum"] = cls.is_cost_item_sum(cost_item)
            data.append(cost_item_data)
        else:
            return None
        for rel in cost_item.IsNestedBy or []:
            for sub_cost_item in rel.RelatedObjects or []:
                cls.create_cost_item_json(sub_cost_item, cost_items, cost_item_data["is_nested_by"])

    @classmethod
    def is_cost_item_sum(cls, cost_item: ifcopenshell.entity_instance) -> bool:
        cost_values = []
        if cost_item.is_a("IfcCostItem"):
            cost_values = cost_item.CostValues
        elif cost_item.is_a("IfcCostValue"):
            cost_values = cost_item.Components
        for cost_value in cost_values or []:
            if cost_value.Category == "*":
                return True
        return False

    @classmethod
    def currency(cls):
        unit = tool.Unit.get_project_currency_unit()
        if unit:
            return {"id": unit.id(), "name": unit.Currency}

    @classmethod
    def generate_cost_schedule_browser(cls, cost_chedule) -> None:
        if not bpy.context.scene.WebProperties.is_connected:
            bpy.ops.bim.connect_websocket_server(page="costing")
        tool.Web.load_cost_schedule_web_ui(cost_chedule)

    @classmethod
    def get_cost_quantities(cls, cost_item: ifcopenshell.entity_instance) -> dict:
        results = {
            "quantities": [],
            "unit_symbol": None,
        }
        if not cost_item:
            return results
        results["quantity_type"] = cost_item.CostQuantities[0].is_a() if cost_item.CostQuantities else None
        unit = (
            ifcopenshell.util.unit.get_property_unit(cost_item.CostQuantities[0], tool.Ifc.get())
            if cost_item.CostQuantities
            else None
        )
        if unit:
            results["unit_symbol"] = ifcopenshell.util.unit.get_unit_symbol(unit)
        for quantity in cost_item.CostQuantities or []:
            assigned_product = cls.get_assigned_product(cost_item, quantity)
            info = quantity.get_info()
            info["fromProduct"] = assigned_product.get_info(recursive=True) if assigned_product else None
            results["quantities"].append(info)
        if results["quantity_type"] == "IfcQuantityCount":
            results["unit_symbol"] = "U"
        return results
