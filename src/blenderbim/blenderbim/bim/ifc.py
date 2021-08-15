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
    undo_redo_stack_objects = set()
    current_transaction = ""
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
            obj.name  # In case the object has been deleted, this triggers an exception
        except:
            return
        return obj

    @staticmethod
    def add_element_listener(callback):
        IfcStore.element_listeners.add(callback)

    @staticmethod
    def update_undo_redo_stack_objects():
        """Keeps track of selected object names, typically during undo and redo

        When any Blender object is stored outside a Blender PointerProperty, such as
        in a regular Python list, there is the likely probability that the object
        will be invalidated when undo or redo occurs. Object invalidation seems to
        only occur for selected objects either pre/post undo/redo event, including
        selected objects for consecutive undo/redos, and all children.

        So if I first select o1, then o2, then o3, then press undo, o3 will be
        invalidated. If instead I press undo twice, o3 and o2 will be invalidated.
        """
        if bpy.context.active_object:
            objects = set([o.name for o in bpy.context.selected_objects + [bpy.context.active_object]])
            objects.update([o.name for o in bpy.context.active_object.children])
        else:
            objects = set([o.name for o in bpy.context.selected_objects])
        for obj in bpy.context.selected_objects:
            objects.update([o.name for o in obj.children])
        IfcStore.undo_redo_stack_objects |= objects

    @staticmethod
    def reload_linked_elements(objects=None):
        file = IfcStore.get_file()
        if not file:
            return
        if objects is None:
            objects = bpy.data.objects

        for obj in objects:
            if not obj:
                continue
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            data = {"id": element.id(), "obj": obj.name}
            if hasattr(element, "GlobalId"):
                data["guid"] = element.GlobalId
            IfcStore.commit_link_element(data)

    @staticmethod
    def link_element(element, obj):
        IfcStore.id_map[element.id()] = obj
        if hasattr(element, "GlobalId"):
            IfcStore.guid_map[element.GlobalId] = obj

        if element.is_a("IfcSurfaceStyle"):
            obj.BIMMaterialProperties.ifc_style_id = element.id()
        else:
            obj.BIMObjectProperties.ifc_definition_id = element.id()

        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)

        if isinstance(obj, bpy.types.Material):
            blenderbim.bim.handler.subscribe_to(obj, "diffuse_color", blenderbim.bim.handler.color_callback)
        elif isinstance(obj, bpy.types.Object):
            blenderbim.bim.handler.subscribe_to(obj, "mode", blenderbim.bim.handler.mode_callback)

        for listener in IfcStore.element_listeners:
            listener(element, obj)

        if IfcStore.history:
            data = {"id": element.id(), "guid": getattr(element, "GlobalId", None), "obj": obj.name}
            IfcStore.history[-1]["operations"].append(
                {"rollback": IfcStore.rollback_link_element, "commit": IfcStore.commit_link_element, "data": data}
            )

    @staticmethod
    def rollback_link_element(data):
        del IfcStore.id_map[data["id"]]
        if data["guid"]:
            del IfcStore.guid_map[data["guid"]]

    @staticmethod
    def commit_link_element(data):
        obj = bpy.data.objects.get(data["obj"])
        IfcStore.id_map[data["id"]] = obj
        if data["guid"]:
            IfcStore.guid_map[data["guid"]] = obj
        blenderbim.bim.handler.subscribe_to(obj, "mode", blenderbim.bim.handler.mode_callback)
        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)
        if isinstance(obj, bpy.types.Material):
            blenderbim.bim.handler.subscribe_to(obj, "diffuse_color", blenderbim.bim.handler.color_callback)
        # TODO Listeners are not re-registered. Does this cause nasty problems to debug later on?
        # TODO We're handling id_map and guid_map, but what about edited_objs? This might cause big problems.

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
        is_top_level_operator = not bool(IfcStore.current_transaction)

        if is_top_level_operator:
            IfcStore.begin_transaction(operator)
            IfcStore.get_file().begin_transaction()
            # This empty transaction ensures that each operator has at least one transaction
            IfcStore.add_transaction_operation(operator, rollback=lambda data: True, commit=lambda data: True)
        else:
            operator.transaction_key = IfcStore.current_transaction

        result = getattr(operator, "_execute")(context)

        if is_top_level_operator:
            IfcStore.get_file().end_transaction()
            IfcStore.add_transaction_operation(
                operator, rollback=lambda d: IfcStore.get_file().undo(), commit=lambda d: IfcStore.get_file().redo()
            )
            IfcStore.end_transaction(operator)

        return result

    @staticmethod
    def begin_transaction(operator):
        IfcStore.undo_redo_stack_objects = set()
        IfcStore.current_transaction = str(uuid.uuid4())
        operator.transaction_key = IfcStore.current_transaction

    @staticmethod
    def end_transaction(operator):
        IfcStore.current_transaction = ""
        operator.transaction_key = ""

    @staticmethod
    def add_transaction_operation(operator, rollback=None, commit=None):
        key = getattr(operator, "transaction_key", None)
        data = getattr(operator, "transaction_data", None)
        bpy.context.scene.BIMProperties.last_transaction = key
        IfcStore.last_transaction = key
        rollback = rollback or getattr(operator, "rollback", lambda data: True)
        commit = commit or getattr(operator, "commit", lambda data: True)
        if IfcStore.history and IfcStore.history[-1]["key"] == key:
            IfcStore.history[-1]["operations"].append({"rollback": rollback, "commit": commit, "data": data})
        else:
            IfcStore.history.append(
                {"key": key, "operations": [{"rollback": rollback, "commit": commit, "data": data}]}
            )
        IfcStore.future = []

    @staticmethod
    def undo():
        if not IfcStore.history:
            return
        event = IfcStore.history.pop()
        for transaction in event["operations"][::-1]:
            transaction["rollback"](transaction["data"])
        IfcStore.future.append(event)

    @staticmethod
    def redo():
        if not IfcStore.future:
            return
        event = IfcStore.future.pop()
        for transaction in event["operations"]:
            transaction["commit"](transaction["data"])
        IfcStore.history.append(event)
