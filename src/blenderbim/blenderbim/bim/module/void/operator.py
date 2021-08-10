import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.void.data import Data
from ifcopenshell.api.context.data import Data as ContextData


class AddOpening(bpy.types.Operator):
    bl_idname = "bim.add_opening"
    bl_label = "Add Opening"
    bl_options = {"REGISTER", "UNDO"}
    opening: bpy.props.StringProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
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
    bl_options = {"REGISTER", "UNDO"}
    opening_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        for modifier in obj.modifiers:
            if modifier.type != "BOOLEAN":
                continue
            if modifier.object and modifier.object.BIMObjectProperties.ifc_definition_id == self.opening_id:
                IfcStore.unlink_element(obj=modifier.object)
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
    bl_options = {"REGISTER", "UNDO"}
    opening: bpy.props.StringProperty()
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
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
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "void.remove_filling", self.file, **{"element": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)}
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class ToggleOpeningVisibility(bpy.types.Operator):
    bl_idname = "bim.toggle_opening_visibility"
    bl_label = "Toggle Opening Visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for project in [c for c in context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            for collection in [c for c in project.children if "IfcOpeningElements" in c.name]:
                collection.hide_viewport = not collection.hide_viewport
        return {"FINISHED"}


class ToggleDecompositionParenting(bpy.types.Operator):
    bl_idname = "bim.toggle_decomposition_parenting"
    bl_label = "Toggle Decomposition Parenting"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        is_parenting = None

        self.decompositions = {}
        self.load_decompositions(obj)

        for parent, children in self.decompositions.items():
            bpy.ops.bim.dynamically_void_product(obj=parent.name)
            for child in children:
                bpy.ops.bim.dynamically_void_product(obj=child.name)
                if is_parenting is None:
                    is_parenting = not bool(child.parent)

                if is_parenting:
                    child.parent = parent
                    child.matrix_parent_inverse = parent.matrix_world.inverted()
                else:
                    parent_matrix_world = child.matrix_world.copy()
                    child.parent = None
                    child.matrix_world = parent_matrix_world

        return {"FINISHED"}

    def load_decompositions(self, parent_obj):
        element = self.file.by_id(parent_obj.BIMObjectProperties.ifc_definition_id)
        for rel in self.file.get_inverse(element):
            if not (rel.is_a("IfcRelDecomposes") or rel.is_a("IfcRelFillsElement")):
                continue
            if rel[4] != element:
                continue
            if isinstance(rel[5], tuple):
                for related_object in rel[5]:
                    self.add_decomposition(parent_obj, related_object)
            else:
                self.add_decomposition(parent_obj, rel[5])

    def add_decomposition(self, parent_obj, child_element):
        child_obj = IfcStore.get_element(child_element.id())
        if child_obj:
            self.decompositions.setdefault(parent_obj, []).append(child_obj)
            self.load_decompositions(child_obj)
