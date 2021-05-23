import bpy
import math
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import mathutils.geometry
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add Type Instance"

    def execute(self, context):
        tprops = context.scene.BIMTypeProperties
        if not tprops.ifc_class or not tprops.relating_type:
            return {"FINISHED"}
        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(tprops.ifc_class, self.file.schema)[0]
        if instance_class in ["IfcWall", "IfcWallStandardCase"]:
            obj = DumbWallGenerator(self.file.by_id(int(tprops.relating_type))).generate()
            if obj:
                return {"FINISHED"}
        # A cube
        verts = [
            Vector((-1, -1, -1)),
            Vector((-1, -1, 1)),
            Vector((-1, 1, -1)),
            Vector((-1, 1, 1)),
            Vector((1, -1, -1)),
            Vector((1, -1, 1)),
            Vector((1, 1, -1)),
            Vector((1, 1, 1)),
        ]
        edges = []
        faces = [
            [0, 2, 3, 1],
            [2, 3, 7, 6],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 3, 7, 5],
            [0, 2, 6, 4],
        ]
        mesh = bpy.data.meshes.new(name="Instance")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Instance", mesh)
        obj.location = context.scene.cursor.location
        collection = bpy.context.view_layer.active_layer_collection.collection
        collection.objects.link(obj)
        collection_obj = bpy.data.objects.get(collection.name)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        bpy.ops.bim.assign_type(relating_type=int(tprops.relating_type), related_object=obj.name)
        if collection_obj and collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = collection_obj.location[2] - min([v[2] for v in obj.bound_box])
        return {"FINISHED"}


class JoinWall(bpy.types.Operator):
    bl_idname = "bim.join_wall"
    bl_label = "Join Wall"
    join_type: bpy.props.StringProperty()

    def execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) == 0:
            return {"FINISHED"}
        if not self.join_type:
            for obj in selected_objs:
                DumbWallJoiner(obj, obj).unjoin()
            return {"FINISHED"}
        if len(selected_objs) < 2:
            return {"FINISHED"}
        for obj in selected_objs:
            if obj == context.active_object:
                continue
            joiner = DumbWallJoiner(obj, context.active_object)
            if self.join_type == "T":
                joiner.join_T()
            elif self.join_type == "L":
                joiner.join_L()
            elif self.join_type == "V":
                joiner.join_V()
        return {"FINISHED"}


class DumbWallJoiner:
    # A dumb wall is a prismatic wall along its local X axis.
    # Given two dumb walls, there are three types of wall joints.
    #  1. T-junction joints
    #  2. L-junction "butt" joints
    #  3. V-junction "mitre" joints
    # The algorithms that handle all joints rely on three fundamental functions.
    #  1. Identify faces at either end of the wall, called "end faces".
    #  2. Given an "end face", identify a side "target face" of the other wall
    #     to project towards.
    #  3. Project the vertices of an "end face" to the "target face".
    def __init__(self, wall1, wall2):
        self.wall1 = wall1
        self.wall2 = wall2
        self.should_project_to_frontface = True
        self.should_attempt_v_junction_projection = False
        self.initialise_convenience_variables()

    def initialise_convenience_variables(self):
        self.wall1_matrix = self.wall1.matrix_world
        self.wall2_matrix = self.wall2.matrix_world
        self.pos_x = self.wall1_matrix.to_quaternion() @ Vector((1, 0, 0))
        self.neg_x = self.wall1_matrix.to_quaternion() @ Vector((-1, 0, 0))

    # Unjoining a wall geometrically means to flatten the ends of the wall to
    # remove any mitred angle from it.
    def unjoin(self):
        wall1_min_faces, wall1_max_faces = self.get_wall_end_faces(self.wall1)
        min_x = min([v[0] for v in self.wall1.bound_box])
        max_x = max([v[0] for v in self.wall1.bound_box])
        for face in wall1_min_faces:
            for v in face.vertices:
                self.wall1.data.vertices[v].co[0] = min_x
        for face in wall1_max_faces:
            for v in face.vertices:
                self.wall1.data.vertices[v].co[0] = max_x

    # A T-junction is an ordered operation where a single end of wall1 is joined
    # to wall2 if possible (i.e. walls aren't parallel). Wall2 is not modified.
    # First, wall1 end faces are identified. We attempt to project an end face
    # at both ends to a front face of wall2. We then choose the end face that
    # has the shortest projection distance, and project it.
    def join_T(self):
        wall1_min_faces, wall1_max_faces = self.get_wall_end_faces(self.wall1)
        wall2_end_faces1, wall2_end_faces2 = self.get_wall_end_faces(self.wall2)
        self.wall2_end_faces = wall2_end_faces1 + wall2_end_faces2
        ef1_distance, ef1_target_frontface, ef1_target_backface = self.get_projection_target(wall1_min_faces, 1)
        ef2_distance, ef2_target_frontface, ef2_target_backface = self.get_projection_target(wall1_max_faces, 2)

        # Large distances probably means rounding issues which lead to very long projections
        if ef1_distance and ef1_distance > 50:
            ef1_distance = None
        if ef2_distance and ef2_distance > 50:
            ef2_distance = None

        # Project only the end faces that are closer to their target
        if ef1_distance and ef2_distance is None:
            self.project_end_faces(wall1_min_faces, ef1_target_frontface, ef1_target_backface)
            return (wall1_min_faces, ef1_target_frontface, ef1_target_backface)
        elif ef2_distance and ef1_distance is None:
            self.project_end_faces(wall1_max_faces, ef2_target_frontface, ef2_target_backface)
            return (wall1_max_faces, ef2_target_frontface, ef2_target_backface)
        elif ef1_distance is None and ef2_distance is None:
            return  # Life is short. BIM is hard.
        elif ef1_distance < ef2_distance:
            self.project_end_faces(wall1_min_faces, ef1_target_frontface, ef1_target_backface)
            return (wall1_min_faces, ef1_target_frontface, ef1_target_backface)
        else:
            self.project_end_faces(wall1_max_faces, ef2_target_frontface, ef2_target_backface)
            return (wall1_max_faces, ef2_target_frontface, ef2_target_backface)

    # An L-junction is ordered operation where a single end of wall1 is joined
    # to the backface of a side of wall2, and then a single end of wall2 is
    # joined back to wall1 as a regular T-junction.
    def join_L(self):
        self.should_project_to_frontface = False
        self.join_T()
        self.swap_walls()
        self.should_project_to_frontface = True
        self.join_T()

    # A V-junction is an unordered operation where wall1 is joined to wall2,
    # then vice versa. First, we do a T-junction from wall1 to wall2, then vice
    # versa. This creates a junction where the inner vertices of the mitre joint
    # touches, but the outer vertices do not. So, we just loop through the end
    # point vertices of each wall, find outer vertices (i.e. vertices that don't
    # touch the other wall), then continue projecting those to the back face of
    # the other wall.
    def join_V(self):
        wall2_end_faces, wall2_target_frontface, wall2_target_backface = self.join_T()
        self.swap_walls()
        wall1_end_faces, wall1_target_frontface, wall1_target_backface = self.join_T()

        for face in wall1_end_faces:
            for v in face.vertices:
                global_co = self.wall1_matrix @ self.wall1.data.vertices[v].co
                if self.wall2.closest_point_on_mesh(self.wall2_matrix.inverted() @ global_co, distance=0.001)[0]:
                    continue  # Vertex is already coincident with other wall, do not mitre
                target_face_center = self.wall2_matrix @ wall1_target_backface.center
                target_face_normal = (self.wall2_matrix.to_quaternion() @ wall1_target_backface.normal).normalized()
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)

        self.swap_walls()

        for face in wall2_end_faces:
            for v in face.vertices:
                global_co = self.wall1_matrix @ self.wall1.data.vertices[v].co
                if self.wall2.closest_point_on_mesh(self.wall2_matrix.inverted() @ global_co, distance=0.001)[0]:
                    continue  # Vertex is already coincident with other wall, do not mitre
                target_face_center = self.wall2_matrix @ wall2_target_backface.center
                target_face_normal = (self.wall2_matrix.to_quaternion() @ wall2_target_backface.normal).normalized()
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)

    def swap_walls(self):
        self.wall1, self.wall2 = self.wall2, self.wall1
        self.initialise_convenience_variables()

    def project_end_faces(self, end_faces, target_frontface, target_backface):
        target_face = target_frontface if self.should_project_to_frontface else target_backface
        target_face_center = self.wall2_matrix @ target_face.center
        target_face_normal = (self.wall2_matrix.to_quaternion() @ target_face.normal).normalized()

        for end_face in end_faces:
            for v in end_face.vertices:
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)

    def project_vertex(self, v, target_face_center, target_face_normal, wall, wall_matrix):
        point = mathutils.geometry.intersect_line_plane(
            wall_matrix @ wall.data.vertices[v].co,
            (wall_matrix @ wall.data.vertices[v].co) + self.pos_x,
            target_face_center,
            target_face_normal,
        )
        if not point:
            return  # Not sure when this would trigger
        local_point = wall_matrix.inverted() @ point
        wall.data.vertices[v].co = local_point

    # A projection target face is a side face on the target wall that has a
    # significant local Y component to its normal (i.e. is not pointing up or
    # down or something). In addition, its plane must intersect with the
    # projection vector of an end face. Finally, the projection vector and the
    # normal of the target face must not be acute.
    def get_projection_target(self, end_faces, which_end):
        if not end_faces:
            return (None, None, None)

        # Get a single end face as a sample.
        f1 = end_faces[0]
        f1_center = self.wall1_matrix @ f1.center

        if which_end == 1:
            outwards = self.neg_x
            inwards = self.pos_x
        elif which_end == 2:
            outwards = self.pos_x
            inwards = self.neg_x

        distance = None
        target_frontface = None
        target_backface = None

        for f2 in self.wall2.data.polygons:
            if abs(f2.normal.y) < 0.75:
                continue  # Probably not a side wall
            if f2 in self.wall2_end_faces:
                continue
            # Can we project the end face to the target face?
            f2_center = self.wall2_matrix @ f2.center
            f1_center_offset_x = f1_center + outwards
            f2_normal = (self.wall2_matrix.to_quaternion() @ f2.normal).normalized()
            point = mathutils.geometry.intersect_line_plane(
                f1_center,
                f1_center_offset_x,
                f2_center,
                f2_normal,
            )
            if not point:
                continue  # We can't project to the face at all
            intersection_point, signed_distance = mathutils.geometry.intersect_point_line(
                point, f1_center, f1_center_offset_x
            )
            raycast_direction = outwards if signed_distance > 0 else inwards

            if raycast_direction == outwards and f2_normal.angle(raycast_direction) < math.pi / 2:
                target_backface = f2  # f2 is on the wrong side of the wall
            elif raycast_direction == inwards and f2_normal.angle(raycast_direction) > math.pi / 2:
                target_backface = f2  # f2 is on the wrong side of the wall
            else:
                target_frontface = f2

            distance = (point - f1_center).length

            if distance is not None and target_frontface is not None and target_backface is not None:
                return (distance, target_frontface, target_backface)
        return (None, None, None)

    # An end face is a set of faces that represents either one end of the wall or
    # the other. There is typically only 1 quad or 2 tris for each end.
    # An end face is defined as having at least one vertex on either extreme
    # X-axis, and a non-insignificant X component of its face normal
    def get_wall_end_faces(self, wall):
        min_faces = []
        max_faces = []
        min_x = min([v[0] for v in wall.bound_box])
        max_x = max([v[0] for v in wall.bound_box])
        for f in wall.data.polygons:
            end_face_index = self.get_wall_face_end(wall, f, min_x, max_x)
            if end_face_index == 1:
                min_faces.append(f)
            elif end_face_index == 2:
                max_faces.append(f)
        return (min_faces, max_faces)

    # 1 is the leftmost (minimum local X axis) end, and 2 is the rightmost end
    def get_wall_face_end(self, wall, face, min_x, max_x):
        for v in face.vertices:
            if wall.data.vertices[v].co.x == min_x and abs(face.normal.x) > 0.1:
                return 1
            if wall.data.vertices[v].co.x == max_x and abs(face.normal.x) > 0.1:
                return 2


class DumbWallGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type

    def generate(self):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        thicknesses = []
        for rel in self.relating_type.HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                material = rel.RelatingMaterial
                if material.is_a("IfcMaterialLayerSet"):
                    thicknesses = [l.LayerThickness for l in material.MaterialLayers]
                    break
        if not thicknesses:
            return

        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.width = sum(thicknesses) * unit_scale
        self.height = 3
        self.length = 1
        self.rotation = 0
        self.location = Vector((0, 0, 0))

        if self.has_sketch():
            return self.derive_from_sketch()
        return self.derive_from_cursor()

    def has_sketch(self):
        return (
            len(bpy.context.scene.grease_pencil.layers) == 1
            and bpy.context.scene.grease_pencil.layers[0].active_frame.strokes
        )

    def derive_from_sketch(self):
        objs = []
        layer = bpy.context.scene.grease_pencil.layers[0]
        for stroke in layer.active_frame.strokes:
            if len(stroke.points) == 1:
                continue
            direction = stroke.points[-1].co - stroke.points[0].co
            self.length = direction.length
            if self.length < 0.1:
                continue
            # Round to nearest 50mm (yes, metric for now)
            self.length = 0.05 * round(self.length / 0.05)
            # self.length = round(self.length, 2)
            self.rotation = math.atan2(direction[1], direction[0])
            # Round to nearest 15 degrees
            nearest_degree = (math.pi / 4) / 3
            self.rotation = nearest_degree * round(self.rotation / nearest_degree)
            self.location = stroke.points[0].co
            obj = self.create_wall()
            objs.append(obj)
            if len(objs) > 1:
                DumbWallJoiner(obj, objs[-2]).join_T()
        bpy.context.scene.grease_pencil.layers.remove(layer)
        return objs

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        if self.collection:
            for sibling_obj in self.collection.objects:
                if not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                if "IfcWall" not in sibling_obj.name:
                    continue
                raycast = sibling_obj.closest_point_on_mesh(bpy.context.scene.cursor.location, distance=0.05)
                if raycast[0]:
                    # Rotate the wall in the direction of the face normal
                    self.rotation = math.atan2(raycast[2][1], raycast[2][0])
                    break
        return self.create_wall()

    def create_wall(self):
        verts = [
            Vector((0, self.width / 2, 0)),
            Vector((0, -self.width / 2, 0)),
            Vector((0, self.width / 2, self.height)),
            Vector((0, -self.width / 2, self.height)),
            Vector((self.length, self.width / 2, 0)),
            Vector((self.length, -self.width / 2, 0)),
            Vector((self.length, self.width / 2, self.height)),
            Vector((self.length, -self.width / 2, self.height)),
        ]
        faces = [
            [1, 3, 2, 0],
            [4, 6, 7, 5],
            [1, 0, 4, 5],
            [3, 7, 6, 2],
            [0, 2, 6, 4],
            [1, 5, 7, 3],
        ]
        mesh = bpy.data.meshes.new(name="Wall")
        mesh.from_pydata(verts, [], faces)
        obj = bpy.data.objects.new("Wall", mesh)
        obj.location = self.location
        obj.rotation_euler[2] = self.rotation
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2]
        self.collection.objects.link(obj)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcWall")
        bpy.ops.bim.assign_type(relating_type=self.relating_type.id(), related_object=obj.name)
        return obj
