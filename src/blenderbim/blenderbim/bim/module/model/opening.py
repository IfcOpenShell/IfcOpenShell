import bpy
import bmesh
import blenderbim.bim.handler
import ifcopenshell
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore
from math import pi
from bpy.types import Operator
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add


def element_listener(element, obj):
    blenderbim.bim.handler.subscribe_to(obj, "mode", mode_callback)


def mode_callback(obj, data):
    for obj in set(bpy.context.selected_objects + [bpy.context.active_object]):
        if (
            obj.mode != "EDIT"
            or not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        if not product.is_a("IfcOpeningElement"):
            return
        for rel in product.VoidsElements:
            building_element_obj = IfcStore.get_element(rel.RelatingBuildingElement.id())
            if not building_element_obj:
                continue
            if [m for m in building_element_obj.modifiers if m.type == "BOOLEAN"]:
                continue
            representation = ifcopenshell.util.representation.get_representation(
                rel.RelatingBuildingElement, "Model", "Body", "MODEL_VIEW"
            )
            if not representation:
                continue
            bpy.ops.bim.switch_representation(
                obj=building_element_obj.name,
                should_switch_all_meshes=True,
                should_reload=True,
                ifc_definition_id=representation.id(),
                disable_opening_subtractions=True,
            )
        IfcStore.edited_objs.add(obj)
        bm = bmesh.from_edit_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.update_edit_mesh(obj.data)
        bm.free()


class AddElementOpening(bpy.types.Operator):
    bl_idname = "bim.add_element_opening"
    bl_label = "Add Element Opening"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) == 0 or not context.active_object:
            return {"FINISHED"}
        obj = context.active_object
        if not obj.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        local_location = obj.matrix_world.inverted() @ context.scene.cursor.location
        raycast = obj.closest_point_on_mesh(local_location, distance=0.01)
        if not raycast[0]:
            return {"FINISHED"}

        # The opening shall be based on the smallest bounding dimension of the element
        dimension = min(obj.dimensions)
        bpy.ops.mesh.primitive_cube_add(size=dimension * 2)
        opening = context.selected_objects[0]

        # Place the opening in the middle of the element
        global_location = obj.matrix_world @ raycast[1]
        normal = raycast[2]
        normal.negate()
        global_normal = obj.matrix_world.to_quaternion() @ normal
        opening.location = global_location + (global_normal * (dimension / 2))

        opening.rotation_euler = obj.rotation_euler
        opening.name = "Opening"
        bpy.ops.bim.add_opening(opening=opening.name, obj=obj.name)
        return {"FINISHED"}



def add_object(self, context):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=self.size)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    mesh = bpy.data.meshes.new(name="Dumb Opening")
    bm.to_mesh(mesh)
    bm.free()
    obj = object_data_add(context, mesh, operator=self)
    obj.name = "Opening"
    obj.display_type = "WIRE"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_opening"
    bl_label = "Dumb Opening"
    bl_options = {"REGISTER", "UNDO"}

    size: FloatProperty(name="Size", default=2)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
