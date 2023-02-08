import os
import bpy
import blenderbim.tool as tool
import ifcopenshell.util.date
import blenderbim.bim.helper
import json


class Cost(blenderbim.core.tool.Cost):
    @classmethod
    def get_cost_schedule_attributes(cls):
        props = bpy.context.scene.BIMCostProperties
        return blenderbim.bim.helper.export_attributes(props.cost_schedule_attributes)

    @classmethod
    def disable_editing_cost_schedule(cls):
        bpy.context.scene.BIMCostProperties.active_cost_schedule_id = 0
    
    @classmethod
    def enable_editing_cost_schedule_attributes(cls, cost_schedule):
        def special_import(name, prop, data):
            if name in ["SubmittedOn", "UpdateDate"]:
                prop.string_value = "" if prop.is_null else ifcopenshell.util.date.ifc2datetime(data[name]).isoformat()
                return True
        
        bpy.context.scene.BIMCostProperties.active_cost_schedule_id = cost_schedule.id()
        bpy.context.scene.BIMCostProperties.is_editing = "COST_SCHEDULE_ATTRIBUTES"
    
    @classmethod
    def load_cost_schedule_attributes(cls, cost_schedule):
        props = bpy.context.scene.BIMCostProperties
        props.cost_schedule_attributes.clear()
        blenderbim.bim.helper.import_attributes(cost_schedule, props.cost_schedule_attributes)

    @classmethod
    def play_chaching_sound(cls):
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
    def enable_editing_cost_items(cls, cost_schedule):
        props = bpy.context.scene.BIMCostProperties
        props.is_cost_update_enabled = False
        props.active_cost_schedule_id = cost_schedule.id()
        props.is_editing = "COST_ITEMS"
        props.is_cost_update_enabled = True

    @classmethod
    def play_chaching_sound(cls):
        if bpy.context.preferences.addons["blenderbim"].preferences.should_play_chaching_sound:
            cls.play_chaching_sound()  # lol

    @classmethod
    def load_cost_items(cls):
        props = bpy.context.scene.BIMCostProperties
        cost_schedule = tool.Ifc.get().by_id(props.active_cost_schedule_id)
        props.cost_items.clear()
        if not hasattr(cls, "contracted_cost_items"):
            cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        for rel in cost_schedule.Controls or []:
            for cost_item in rel.RelatedObjects:
                cls.create_new_cost_item_li(props, cost_item, 0)

    @classmethod
    def create_new_cost_item_li(cls, props, cost_item, level_index):
        new = props.cost_items.add()
        new.ifc_definition_id = cost_item.id()
        new.name = cost_item.Name or "Unnamed"
        new.identification = cost_item.Identification or "XXX"
        new.is_expanded = cost_item.id() not in cls.contracted_cost_items
        new.level_index = level_index
        if cost_item.IsNestedBy:
            new.has_children = True
            if new.is_expanded:
                for rel in cost_item.IsNestedBy:
                    for sub_cost_item in rel.RelatedObjects:
                        cls.create_new_cost_item_li(props, sub_cost_item, level_index + 1)

    @classmethod
    def expand_cost_item(cls, cost_item):
        props = bpy.context.scene.BIMCostProperties
        cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        cls.contracted_cost_items.remove(cost_item.id())
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)

    @classmethod
    def expand_cost_items(cls):
        props = bpy.context.scene.BIMCostProperties
        cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        for cost_item in props.cost_items:
            if cost_item.ifc_definition_id in cls.contracted_cost_items:
                cls.contracted_cost_items.remove(cost_item.ifc_definition_id)
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)

    @classmethod
    def contract_cost_item(cls, cost_item):
        props = bpy.context.scene.BIMCostProperties
        cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        cls.contracted_cost_items.append(cost_item.id())
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)

    @classmethod
    def contract_cost_items(cls):
        props = bpy.context.scene.BIMCostProperties
        cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        for cost_item in props.cost_items:
            if cost_item.ifc_definition_id not in cls.contracted_cost_items:
                cls.contracted_cost_items.append(cost_item.ifc_definition_id)
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)
    
    @classmethod
    def clean_up_cost_item_tree(cls, cost_item):
        props = bpy.context.scene.BIMCostProperties
        cls.contracted_cost_items = json.loads(props.contracted_cost_items)
        if props.active_cost_item_index in cls.contracted_cost_items:
            cls.contracted_cost_items.remove(props.active_cost_item_index)
        props.contracted_cost_items = json.dumps(cls.contracted_cost_items)
        bpy.ops.bim.enable_editing_cost_items(cost_schedule=props.active_cost_schedule_id)
        if props.active_cost_item_id == cost_item.id():
            props.active_cost_item_id = 0            

    @classmethod
    def enable_editing_cost_item_attributes(cls, cost_item):
        bpy.context.scene.BIMCostProperties.active_cost_item_id = cost_item.id()
        bpy.context.scene.BIMCostProperties.cost_item_editing_type = "ATTRIBUTES"
    
    @classmethod
    def load_cost_item_attributes(cls, cost_item):
        props = bpy.context.scene.BIMCostProperties
        props.cost_item_attributes.clear()
        blenderbim.bim.helper.import_attributes2(cost_item, props.cost_item_attributes)
    
    @classmethod
    def disable_editing_cost_item(cls):
        bpy.context.scene.BIMCostProperties.active_cost_item_id = 0
    
    @classmethod
    def get_cost_item_attributes(cls):
        props = bpy.context.scene.BIMCostProperties
        return blenderbim.bim.helper.export_attributes(props.cost_item_attributes)

    @classmethod
    def get_active_cost_item(cls):
        if bpy.context.scene.BIMCostProperties.active_cost_item_id == 0:
            return None
        return tool.Ifc.get().by_id(bpy.context.scene.BIMCostProperties.active_cost_item_id)