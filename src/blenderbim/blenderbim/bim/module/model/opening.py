import bpy
import bmesh
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
from math import pi
from bpy.types import Operator
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add


def element_listener(element, obj):
    blenderbim.bim.handler.subscribe_to(obj, "mode", mode_callback)


def mode_callback(obj, data):
    for obj in bpy.context.selected_objects + [bpy.context.active_object]:
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
        IfcStore.edited_objs.add(obj)
        bm = bmesh.from_edit_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.update_edit_mesh(obj.data)
        bm.free()


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
