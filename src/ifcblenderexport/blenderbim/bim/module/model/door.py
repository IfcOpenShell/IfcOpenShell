import bpy
import math
import ifcopenshell
from bpy.types import Operator
from bpy.props import FloatProperty
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore


def add_object(self, context):
    guid = ifcopenshell.guid.new()
    leaf_width = self.overall_width - 0.045 - 0.045
    # TODO reimplement 2D. See #1222.
    #verts = [
    #    # Left lining
    #    Vector((0, 0, 0)),
    #    Vector((0, self.depth, 0)),
    #    Vector((0.04, self.depth, 0)),
    #    Vector((0.04, self.depth - 0.04, 0)),
    #    Vector((0.065, self.depth - 0.04, 0)),
    #    Vector((0.065, 0, 0)),
    #    # Right lining
    #    Vector((self.overall_width, 0, 0)),
    #    Vector((self.overall_width, self.depth, 0)),
    #    Vector((self.overall_width - 0.04, self.depth, 0)),
    #    Vector((self.overall_width - 0.04, self.depth - 0.04, 0)),
    #    Vector((self.overall_width - 0.065, self.depth - 0.04, 0)),
    #    Vector((self.overall_width - 0.065, 0, 0)),
    #    # Door panel
    #    Vector((0.045, self.depth, 0)),
    #    Vector((0.045, self.depth + leaf_width, 0)),
    #    Vector((0.080, self.depth + leaf_width, 0)),
    #    Vector((0.080, self.depth, 0)),
    #]
    #edges = [
    #    [0, 1],
    #    [1, 2],
    #    [2, 3],
    #    [3, 4],
    #    [4, 5],  # Left lining
    #    [6, 7],
    #    [7, 8],
    #    [8, 9],
    #    [9, 10],
    #    [10, 11],  # Right lining
    #    [12, 13],
    #    [13, 14],
    #    [14, 15],
    #    [15, 12],  # Door panel
    #]
    ## Door swing
    #for i in range(0, 9):
    #    verts.append(
    #        Vector(
    #            (
    #                0.045 + (leaf_width * math.cos((math.pi / 2) / 8 * i)),
    #                self.depth + (leaf_width * math.sin((math.pi / 2) / 8 * i)),
    #                0,
    #            )
    #        )
    #    )
    #    edges.append([16 + i, 17 + i])
    #edges.pop()
    #faces = []
    #mesh = bpy.data.meshes.new(name="Plan/Annotation/PLAN_VIEW/" + guid)
    #mesh.use_fake_user = True
    #mesh.from_pydata(verts, edges, faces)

    # Door lining profile
    verts = [
        Vector((0, 0, 0)),
        Vector((0, -self.depth, 0)),
        Vector((0.04, -self.depth, 0)),
        Vector((0.04, -self.depth + 0.04, 0)),
        Vector((0.065, -self.depth + 0.04, 0)),
        Vector((0.065, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3, 4, 5]]
    mesh = bpy.data.meshes.new(name="Dumb Door Profile")
    mesh.from_pydata(verts, edges, faces)
    obj = bpy.data.objects.new("Door Profile", mesh)

    context.view_layer.active_layer_collection.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="CURVE")

    # Door lining sweep
    verts = [
        Vector((0, 0, 0)),
        Vector((0, self.overall_height, 0)),
        Vector((self.overall_width, self.overall_height, 0)),
        Vector((self.overall_width, 0, 0)),
    ]
    edges = [[0, 1], [1, 2], [2, 3]]
    faces = []
    mesh = bpy.data.meshes.new(name="Dumb Door")
    mesh.from_pydata(verts, edges, faces)
    obj2 = bpy.data.objects.new("Door", mesh)

    context.view_layer.active_layer_collection.collection.objects.link(obj2)
    bpy.context.view_layer.objects.active = obj2
    obj2.select_set(True)
    bpy.ops.object.convert(target="CURVE")

    obj2.data.dimensions = "2D"
    obj2.data.bevel_mode = "OBJECT"
    obj2.data.bevel_object = obj

    obj2.rotation_euler[0] = math.pi / 2
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.transform_apply(location=False)
    bpy.data.objects.remove(obj, do_unlink=True)

    # Door panel
    verts = [
        Vector((0.045, self.depth, 0)),
        Vector((0.045, self.depth - 0.035, 0)),
        Vector((self.overall_width - 0.045, self.depth - 0.035, 0)),
        Vector((self.overall_width - 0.045, self.depth, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Door Panel")
    mesh.from_pydata(verts, edges, faces)
    obj3 = bpy.data.objects.new("Door Panel", mesh)
    modifier = obj3.modifiers.new("Panel Height", "SOLIDIFY")
    modifier.offset = 1
    modifier.thickness = self.overall_height - 0.045

    context.view_layer.active_layer_collection.collection.objects.link(obj3)
    bpy.context.view_layer.objects.active = obj3
    obj3.select_set(True)
    bpy.ops.object.convert(target="MESH")

    ctx = bpy.context.copy()
    ctx["active_object"] = obj2
    ctx["selected_editable_objects"] = [obj2, obj3]
    bpy.ops.object.join(ctx)

    # Door Opening
    verts = [
        Vector((0, -0.1, -0.1)),
        Vector((0, self.depth + 0.1, -0.1)),
        Vector((self.overall_width, self.depth + 0.1, -0.1)),
        Vector((self.overall_width, -0.1, -0.1)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Door Opening")
    mesh.from_pydata(verts, edges, faces)
    obj4 = bpy.data.objects.new("Door Opening", mesh)
    modifier = obj4.modifiers.new("Panel Height", "SOLIDIFY")
    modifier.offset = -1
    modifier.thickness = self.overall_height + 0.1

    context.view_layer.active_layer_collection.collection.objects.link(obj4)
    bpy.context.view_layer.objects.active = obj4
    obj4.select_set(True)
    bpy.ops.object.convert(target="MESH")

    obj4.display_type = "WIRE"
    obj4.parent = obj2
    obj4.matrix_parent_inverse = obj2.matrix_world.inverted()
    obj4.hide_render = True
    obj4.name = "Door Opening"

    obj2.name = "Door"

    if IfcStore.get_file():
        bpy.ops.bim.assign_class(obj=obj2.name, ifc_class="IfcDoor")
    #obj2.data.name = "Model/Body/MODEL_VIEW/" + guid
    #obj2.data.use_fake_user = True

    # TODO: reimplement. See #1222.
    #rep = obj2.BIMObjectProperties.representation_contexts.add()
    #rep.context = "Model"
    #rep.name = "Body"
    #rep.target_view = "MODEL_VIEW"

    #rep = obj2.BIMObjectProperties.representation_contexts.add()
    #rep.context = "Plan"
    #rep.name = "Annotation"
    #rep.target_view = "PLAN_VIEW"


class BIM_OT_add_object(Operator):
    bl_idname = "mesh.add_door"
    bl_label = "Dumb Door"

    overall_width: FloatProperty(name="Overall Width", default=0.85)
    overall_height: FloatProperty(name="Overall Height", default=2.1)
    depth: FloatProperty(name="Depth", default=0.2)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
