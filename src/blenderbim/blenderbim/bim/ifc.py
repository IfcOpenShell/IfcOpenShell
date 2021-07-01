import bpy
import uuid
import ifcopenshell
import blenderbim.bim.handler


class IfcStore:
    path = ""
    file = None
    schema = None
    id_map = {}
    guid_map = {}
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
        IfcStore.id_map = {}
        IfcStore.guid_map = {}
        IfcStore.edited_objs = set()
        IfcStore.pset_template_path = ""
        IfcStore.pset_template_file = None
        IfcStore.library_path = ""
        IfcStore.library_file = None

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
            map_object = IfcStore.id_map
        else:
            map_object = IfcStore.guid_map
        try:
            obj = map_object[id_or_guid]
            obj.type  # In case the object has been deleted, this triggers an exception
        except:
            return
        return obj

    @staticmethod
    def add_element_listener(callback):
        IfcStore.element_listeners.add(callback)

    @staticmethod
    def reload_linked_elements(should_reload_selected=False):
        file = IfcStore.get_file()
        if not file:
            return
        if should_reload_selected:
            objects = bpy.context.selected_objects
            if bpy.context.active_object:
                objects += [bpy.context.active_object]
        else:
            objects = bpy.data.objects
        [
            IfcStore.link_element(file.by_id(obj.BIMObjectProperties.ifc_definition_id), obj)
            for obj in objects
            if obj.BIMObjectProperties.ifc_definition_id
        ]

    @staticmethod
    def link_element(element, obj):
        IfcStore.id_map[element.id()] = obj
        if hasattr(element, "GlobalId"):
            IfcStore.guid_map[element.GlobalId] = obj
        obj.BIMObjectProperties.ifc_definition_id = element.id()
        blenderbim.bim.handler.subscribe_to(obj, "mode", blenderbim.bim.handler.mode_callback)
        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)
        for listener in IfcStore.element_listeners:
            listener(element, obj)

        if IfcStore.history:
            data = {"id": element.id(), "guid": getattr(element, "GlobalId", None), "obj": obj.name}
            IfcStore.history[-1]["transactions"].append(
                {"rollback": IfcStore.rollback_link_element, "commit": IfcStore.commit_link_element, "data": data}
            )

    @staticmethod
    def rollback_link_element(data):
        del IfcStore.id_map[data["id"]]
        if data["guid"]:
            del IfcStore.guid_map[data["guid"]]

    @staticmethod
    def commit_link_element(data):
        IfcStore.id_map[data["id"]] = bpy.data.objects.get(data["obj"])
        if data["guid"]:
            IfcStore.guid_map[data["guid"]] = bpy.data.objects.get(data["obj"])

    @staticmethod
    def unlink_element(element=None, obj=None):
        if element is None:
            try:
                element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
            except:
                pass

        try:
            if element:
                del IfcStore.id_map[element.id()]
            else:
                del IfcStore.id_map[obj.BIMObjectProperties.ifc_definition_id]
        except:
            pass

        try:
            if element and hasattr(element, "GlobalId"):
                del IfcStore.guid_map[element.GlobalId]
        except:
            pass

        if obj:
            obj.BIMObjectProperties.ifc_definition_id = 0

    @staticmethod
    def execute_ifc_operator(operator, context):
        is_top_level_operator = not bool(operator.transaction_key)

        if is_top_level_operator:
            IfcStore.get_file().begin_transaction()
            # This empty transaction ensures that each operator has at least one transaction
            IfcStore.add_transaction(operator, rollback=lambda data: True, commit=lambda data: True)

        result = getattr(operator, "_execute")(context)

        if is_top_level_operator:
            IfcStore.get_file().end_transaction()
            IfcStore.add_transaction(
                operator, rollback=IfcStore.rollback_ifc_operator, commit=IfcStore.commit_ifc_operator
            )

        return result

    @staticmethod
    def rollback_ifc_operator(data):
        IfcStore.get_file().undo()
        blenderbim.bim.handler.purge_module_data()

    @staticmethod
    def commit_ifc_operator(data):
        IfcStore.get_file().redo()
        blenderbim.bim.handler.purge_module_data()

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
        rollback = rollback or getattr(operator, "rollback", lambda data: True)
        commit = commit or getattr(operator, "commit", lambda data: True)
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
