import bpy
import uuid
import ifcopenshell
import blenderbim.bim.handler


class IfcStore:
    path = ""
    file = None
    schema = None
    edited_objs = set()
    pset_template_path = ""
    pset_template_file = None
    library_path = ""
    library_file = None
    element_listeners = set()
    last_transaction = ""
    history = []
    future = []

    @staticmethod
    def purge():
        IfcStore.path = ""
        IfcStore.file = None
        IfcStore.schema = None
        IfcStore.edited_objs = set()
        IfcStore.pset_template_path = ""
        IfcStore.pset_template_file = None
        IfcStore.library_path = ""
        IfcStore.library_file = None
        bpy.context.scene.BIMIdMap.id_map.clear()
        bpy.context.scene.BIMGuidMap.guid_map.clear()

    @staticmethod
    def get_file():
        if IfcStore.file is None:
            IfcStore.path = bpy.context.scene.BIMProperties.ifc_file
            if IfcStore.path:
                try:
                    IfcStore.file = ifcopenshell.open(IfcStore.path)
                except:
                    IfcStore.file
        return IfcStore.file

    @staticmethod
    def get_schema():
        if IfcStore.file is None:
            return
        elif IfcStore.schema is None:
            IfcStore.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(IfcStore.file.schema)
        return IfcStore.schema

    @staticmethod
    def get_element(id_or_guid):
        if isinstance(id_or_guid, int):
            map_object = bpy.context.scene.BIMIdMap.id_map
            id_or_guid = str(id_or_guid)
        else:
            map_object = bpy.context.scene.BIMGuidMap.guid_map
        try:
            obj = map_object.get(id_or_guid).obj
            obj.type  # In case the object has been deleted, this triggers an exception
        except:
            return
        return obj

    @staticmethod
    def add_element_listener(callback):
        IfcStore.element_listeners.add(callback)

    @staticmethod
    def link_element(element, obj):
        element_link = bpy.context.scene.BIMIdMap.id_map.get(str(element.id()))
        if not element_link:
            new = bpy.context.scene.BIMIdMap.id_map.add()
            new.name = str(element.id())
            new.obj = obj
        if hasattr(element, "GlobalId"):
            element_link = bpy.context.scene.BIMGuidMap.guid_map.get(element.GlobalId)
            if not element_link:
                new = bpy.context.scene.BIMGuidMap.guid_map.add()
                new.name = element.GlobalId
                new.obj = obj
        obj.BIMObjectProperties.ifc_definition_id = element.id()
        blenderbim.bim.handler.subscribe_to(obj, "mode", blenderbim.bim.handler.mode_callback)
        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)
        for listener in IfcStore.element_listeners:
            listener(element, obj)

    @staticmethod
    def unlink_element(element=None, obj=None):
        if element is None:
            try:
                element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
            except:
                pass

        try:
            if element:
                bpy.context.scene.BIMIdMap.id_map.remove(bpy.context.scene.BIMIdMap.id_map.find(str(element.id())))
            else:
                bpy.context.scene.BIMIdMap.id_map.remove(
                    bpy.context.scene.BIMIdMap.id_map.find(str(obj.BIMObjectProperties.ifc_definition_id))
                )
        except:
            pass

        try:
            if element and hasattr(element, "GlobalId"):
                bpy.context.scene.BIMGuidMap.guid_map.remove(
                    bpy.context.scene.BIMGuidMap.guid_map.find(element.GlobalId)
                )
        except:
            pass

        if obj:
            obj.BIMObjectProperties.ifc_definition_id = 0

    @staticmethod
    def generate_transaction_key(operator):
        if not getattr(operator, "transaction_key", None):
            setattr(operator, "transaction_key", str(uuid.uuid4()))

    @staticmethod
    def add_transaction(operator, rollback=None, commit=None):
        IfcStore.generate_transaction_key(operator)
        key = getattr(operator, "transaction_key", None)
        data = getattr(operator, "transaction_data", None)
        bpy.context.scene.BIMProperties.last_transaction = key
        IfcStore.last_transaction = key
        rollback = rollback or getattr(operator, "rollback", lambda: True)
        commit = commit or getattr(operator, "commit", lambda: True)
        if IfcStore.history and IfcStore.history[-1]["key"] == key:
            IfcStore.history[-1]["transactions"].append({"rollback": rollback, "commit": commit, "data": data})
        else:
            IfcStore.history.append(
                {"key": key, "transactions": [{"rollback": rollback, "commit": commit, "data": data}]}
            )
        IfcStore.future = []

    @staticmethod
    def undo():
        if not IfcStore.history:
            return
        event = IfcStore.history.pop()
        for transaction in event["transactions"][::-1]:
            transaction["rollback"](transaction["data"])
        IfcStore.future.append(event)

    @staticmethod
    def redo():
        if not IfcStore.future:
            return
        event = IfcStore.future.pop()
        for transaction in event["transactions"]:
            transaction["commit"](transaction["data"])
        IfcStore.history.append(event)
