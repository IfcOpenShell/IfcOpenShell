import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.void.data import Data
from ifcopenshell.api.context.data import Data as ContextData


class AddOpening(bpy.types.Operator):
    bl_idname = "bim.add_opening"
    bl_label = "Add Opening"
    opening: bpy.props.StringProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        opening = bpy.data.objects.get(self.opening)
        opening.display_type = "WIRE"
        if not opening.BIMObjectProperties.ifc_definition_id:
            body_context_id = None
            if not ContextData.is_loaded:
                ContextData.load(IfcStore.get_file())
            for context in ContextData.contexts.values():
                for subcontext_id, subcontext in context["HasSubContexts"].items():
                    if subcontext["ContextType"] == "Model" and subcontext["ContextIdentifier"] == "Body":
                        body_context_id = subcontext_id
                        break
            if not body_context_id:
                return {"FINISHED"}
            bpy.ops.bim.assign_class(obj=opening.name, ifc_class="IfcOpeningElement", context_id=body_context_id)

        self.file = IfcStore.get_file()
        element_id = obj.BIMObjectProperties.ifc_definition_id
        ifcopenshell.api.run(
            "void.add_opening",
            self.file,
            **{
                "opening": self.file.by_id(opening.BIMObjectProperties.ifc_definition_id),
                "element": self.file.by_id(element_id),
            },
        )
        Data.load(IfcStore.get_file(), element_id)

        has_modifier = False

        for modifier in obj.modifiers:
            if modifier.type == "BOOLEAN" and modifier.object and modifier.object == opening:
                has_modifier = True
                break

        if not has_modifier:
            modifier = obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
            modifier.operation = "DIFFERENCE"
            modifier.object = opening
        return {"FINISHED"}


class RemoveOpening(bpy.types.Operator):
    bl_idname = "bim.remove_opening"
    bl_label = "Remove Opening"
    opening_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        for modifier in obj.modifiers:
            if modifier.type != "BOOLEAN":
                continue
            if modifier.object and modifier.object.BIMObjectProperties.ifc_definition_id == self.opening_id:
                modifier.object.BIMObjectProperties.ifc_definition_id = 0
                if "/" in modifier.object.name and modifier.object.name[0:3] == "Ifc":
                    modifier.object.name = "/".join(modifier.object.name.split("/")[1:])
                obj.modifiers.remove(modifier)
                break

        ifcopenshell.api.run("void.remove_opening", self.file, **{"opening": self.file.by_id(self.opening_id)})
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class AddFilling(bpy.types.Operator):
    bl_idname = "bim.add_filling"
    bl_label = "Add Filling"
    opening: bpy.props.StringProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        opening = bpy.data.objects.get(self.opening) if self.opening else context.scene.VoidProperties.desired_opening
        self.file = IfcStore.get_file()
        element_id = obj.BIMObjectProperties.ifc_definition_id
        ifcopenshell.api.run(
            "void.add_filling",
            self.file,
            **{
                "opening": self.file.by_id(opening.BIMObjectProperties.ifc_definition_id),
                "element": self.file.by_id(element_id),
            },
        )
        Data.load(IfcStore.get_file(), element_id)
        return {"FINISHED"}


class RemoveFilling(bpy.types.Operator):
    bl_idname = "bim.remove_filling"
    bl_label = "Remove Filling"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "void.remove_filling", self.file, **{"element": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)}
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}
