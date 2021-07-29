import bpy
import ifcopenshell.util.attribute
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.system.data import Data


class LoadSystems(bpy.types.Operator):
    bl_idname = "bim.load_systems"
    bl_label = "Load Systems"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMSystemProperties
        while len(props.systems) > 0:
            props.systems.remove(0)
        for ifc_definition_id, system in Data.systems.items():
            new = props.systems.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = system["Name"]
        props.is_editing = True
        bpy.ops.bim.disable_editing_system()
        return {"FINISHED"}


class DisableSystemEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_system_editing_ui"
    bl_label = "Disable System Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMSystemProperties.is_editing = False
        return {"FINISHED"}


class AddSystem(bpy.types.Operator):
    bl_idname = "bim.add_system"
    bl_label = "Add System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("system.add_system", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_systems()
        bpy.ops.bim.enable_editing_system(system=result.id())
        return {"FINISHED"}


class EditSystem(bpy.types.Operator):
    bl_idname = "bim.edit_system"
    bl_label = "Edit System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMSystemProperties
        attributes = {}
        for attribute in props.system_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "system.edit_system", self.file, **{"system": self.file.by_id(props.active_system_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_systems()
        return {"FINISHED"}


class RemoveSystem(bpy.types.Operator):
    bl_idname = "bim.remove_system"
    bl_label = "Remove System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMSystemProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("system.remove_system", self.file, **{"system": self.file.by_id(self.system)})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_systems()
        return {"FINISHED"}


class EnableEditingSystem(bpy.types.Operator):
    bl_idname = "bim.enable_editing_system"
    bl_label = "Enable Editing System"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMSystemProperties
        while len(props.system_attributes) > 0:
            props.system_attributes.remove(0)

        data = Data.systems[self.system]

        for attribute in IfcStore.get_schema().declaration_by_name("IfcSystem").all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.system_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.string_value = "" if new.is_null else data[attribute.name()]
        props.active_system_id = self.system
        return {"FINISHED"}


class DisableEditingSystem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_system"
    bl_label = "Disable Editing System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMSystemProperties.active_system_id = 0
        return {"FINISHED"}


class AssignSystem(bpy.types.Operator):
    bl_idname = "bim.assign_system"
    bl_label = "Assign System"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    system: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        product = bpy.data.objects.get(self.product) if self.product else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "system.assign_system",
            self.file,
            **{
                "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                "system": self.file.by_id(self.system),
            }
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class UnassignSystem(bpy.types.Operator):
    bl_idname = "bim.unassign_system"
    bl_label = "Unassign System"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    system: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        product = bpy.data.objects.get(self.product) if self.product else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "system.unassign_system",
            self.file,
            **{
                "product": self.file.by_id(product.BIMObjectProperties.ifc_definition_id),
                "system": self.file.by_id(self.system),
            }
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class SelectSystemProducts(bpy.types.Operator):
    bl_idname = "bim.select_system_products"
    bl_label = "Select System Products"
    bl_options = {"REGISTER", "UNDO"}
    system: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        for obj in context.visible_objects:
            obj.select_set(False)
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            product_systems = Data.products.get(obj.BIMObjectProperties.ifc_definition_id, [])
            if self.system in product_systems:
                obj.select_set(True)
        return {"FINISHED"}
