import bpy
import math
import ifcopenshell
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_object(self, context):
    guid = ifcopenshell.guid.new()
    leaf_width = self.overall_width - 0.045 - 0.045
    verts = [
        # Left lining
        Vector((0, 0, 0)),
        Vector((0, self.depth, 0)),
        Vector((0.04, self.depth, 0)),
        Vector((0.04, 0, 0)),
        # Right lining
        Vector((self.overall_width, 0, 0)),
        Vector((self.overall_width, self.depth, 0)),
        Vector((self.overall_width - 0.04, self.depth, 0)),
        Vector((self.overall_width - 0.04, 0, 0)),
        # Bottom lining
        Vector((0, 0, 0)),
        Vector((self.overall_width, 0, 0)),
        Vector((0, self.depth, 0)),
        Vector((self.overall_width, self.depth, 0)),
        # Window panel
        Vector((0.04, (self.depth / 2) + 0.005, 0)),
        Vector((0.04, (self.depth / 2) - 0.005, 0)),
        Vector((self.overall_width - 0.04, (self.depth / 2) - 0.005, 0)),
        Vector((self.overall_width - 0.04, (self.depth / 2) + 0.005, 0)),
    ]
    edges = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],  # Left lining
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],  # Right lining
        [8, 9],
        [10, 11],  # Bottom lining
        [12, 13],
        [13, 14],
        [14, 15],
        [15, 12],  # Window panel
    ]
    faces = []
    mesh = bpy.data.meshes.new(name="Plan/Annotation/PLAN_VIEW/" + guid)
    mesh.use_fake_user = True
    mesh.from_pydata(verts, edges, faces)

    # Window lining profile
    verts = [
        Vector((0, 0, 0)),
        Vector((0, -self.depth, 0)),
        Vector((0.04, -self.depth, 0)),
        Vector((0.04, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Window Profile")
    mesh.from_pydata(verts, edges, faces)
    obj = object_data_add(context, mesh, operator=self)
    bpy.ops.object.convert(target="CURVE")

    # Window lining sweep
    verts = [
        Vector((0, 0, 0)),
        Vector((0, self.overall_height, 0)),
        Vector((self.overall_width, self.overall_height, 0)),
        Vector((self.overall_width, 0, 0)),
    ]
    edges = [[0, 1], [1, 2], [2, 3]]
    faces = []
    mesh = bpy.data.meshes.new(name="Dumb Window")
    mesh.from_pydata(verts, edges, faces)
    obj2 = object_data_add(context, mesh, operator=self)
    bpy.ops.object.convert(target="CURVE")
    obj2.data.splines[0].use_cyclic_u = True

    obj2.data.dimensions = "2D"
    obj2.data.bevel_object = obj

    obj2.rotation_euler[0] = math.pi / 2
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.transform_apply(location=False)
    bpy.data.objects.remove(obj, do_unlink=True)

    # Window panel
    verts = [
        Vector((0.04, (self.depth / 2) + 0.005, 0.04)),
        Vector((0.04, (self.depth / 2) - 0.005, 0.04)),
        Vector((self.overall_width - 0.04, (self.depth / 2) - 0.005, 0.04)),
        Vector((self.overall_width - 0.04, (self.depth / 2) + 0.005, 0.04)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Window Panel")
    mesh.from_pydata(verts, edges, faces)
    obj3 = object_data_add(context, mesh, operator=self)
    modifier = obj3.modifiers.new("Panel Height", "SOLIDIFY")
    modifier.offset = 1
    modifier.thickness = self.overall_height - 0.08
    bpy.ops.object.convert(target="MESH")

    ctx = bpy.context.copy()
    ctx["active_object"] = obj2
    ctx["selected_editable_objects"] = [obj2, obj3]
    bpy.ops.object.join(ctx)

    # Window Opening
    verts = [
        Vector((0, -0.1, 0)),
        Vector((0, self.depth + 0.1, 0)),
        Vector((self.overall_width, self.depth + 0.1, 0)),
        Vector((self.overall_width, -0.1, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Window Opening")
    mesh.from_pydata(verts, edges, faces)
    obj4 = object_data_add(context, mesh, operator=self)
    modifier = obj4.modifiers.new("Panel Height", "SOLIDIFY")
    modifier.offset = -1
    modifier.thickness = self.overall_height
    bpy.ops.object.convert(target="MESH")
    obj4.display_type = "WIRE"
    obj4.parent = obj2
    obj4.matrix_parent_inverse = obj2.matrix_world.inverted()
    obj4.hide_render = True
    obj4.name = "IfcOpeningElement/Dumb Window Opening"
    attribute = obj4.BIMObjectProperties.attributes.add()
    attribute.name = "PredefinedType"
    attribute.string_value = "OPENING"

    obj2.name = "IfcWindow/Dumb Window"
    attribute = obj2.BIMObjectProperties.attributes.add()
    attribute.name = "PredefinedType"
    attribute.string_value = "WINDOW"
    obj2.data.name = "Model/Body/MODEL_VIEW/" + guid
    obj2.data.use_fake_user = True

    rep = obj2.BIMObjectProperties.representation_contexts.add()
    rep.context = "Model"
    rep.name = "Body"
    rep.target_view = "MODEL_VIEW"

    rep = obj2.BIMObjectProperties.representation_contexts.add()
    rep.context = "Plan"
    rep.name = "Annotation"
    rep.target_view = "PLAN_VIEW"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_window"
    bl_label = "Dumb Window"
    bl_options = {"REGISTER", "UNDO"}

    overall_width: FloatProperty(name="Overall Width", default=0.7)
    overall_height: FloatProperty(name="Overall Height", default=1)
    depth: FloatProperty(name="Depth", default=0.1)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
