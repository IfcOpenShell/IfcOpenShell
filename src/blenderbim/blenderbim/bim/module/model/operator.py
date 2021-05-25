import bpy
import math
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import mathutils.geometry
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector, Matrix
from ifcopenshell.api.material.data import Data as MaterialData


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add Type Instance"
    bl_options = {"REGISTER", "UNDO"}

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
    bl_options = {"REGISTER", "UNDO"}
    join_type: bpy.props.StringProperty()

    def execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) == 0:
            return {"FINISHED"}
        if not self.join_type:
            for obj in selected_objs:
                DumbWallJoiner(obj, obj).unjoin()
            return {"FINISHED"}
        if len(selected_objs) < 2 or not context.active_object:
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
            IfcStore.edited_objs.add(obj)
        if self.join_type != "T":
            IfcStore.edited_objs.add(context.active_object)
        return {"FINISHED"}


class AlignWall(bpy.types.Operator):
    bl_idname = "bim.align_wall"
    bl_label = "Align Wall"
    bl_options = {"REGISTER", "UNDO"}
    align_type: bpy.props.StringProperty()

    def execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) < 2 or not context.active_object:
            return {"FINISHED"}
        for obj in selected_objs:
            if obj == context.active_object:
                continue
            aligner = DumbWallAligner(obj, context.active_object)
            if self.align_type == "CENTERLINE":
                aligner.align_centerline()
            elif self.align_type == "EXTERIOR":
                aligner.align_exterior()
            elif self.align_type == "INTERIOR":
                aligner.align_interior()
        return {"FINISHED"}


def recalculate_dumb_wall_origin(wall):
    new_origin = wall.matrix_world @ Vector(wall.bound_box[0])
    if (wall.matrix_world.translation - new_origin).length > 0.001:
        wall.data.transform(
            Matrix.Translation(
                (wall.matrix_world.inverted().to_quaternion() @ (wall.matrix_world.translation - new_origin))
            )
        )
        wall.matrix_world.translation = new_origin


class DumbWallAligner:
    # An alignment shifts the origin of all walls to the closest point on the
    # local X axis of the reference wall. In addition, the Z rotation is copied.
    # Z translations are ignored for alignment.
    def __init__(self, wall, reference_wall):
        self.wall = wall
        self.reference_wall = reference_wall

    def align_centerline(self):
        self.align(self.reference_wall.matrix_world.translation, self.reference_wall.matrix_world @ Vector((1, 0, 0)))

    def align_exterior(self):
        width = (Vector(self.wall.bound_box[3]) - Vector(self.wall.bound_box[0])).y
        offset = self.wall.matrix_world.to_quaternion() @ Vector((0, -width / 2, 0))
        self.align(
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[3]),
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[7]),
            offset,
        )

    def align_interior(self):
        width = (Vector(self.wall.bound_box[3]) - Vector(self.wall.bound_box[0])).y
        offset = self.wall.matrix_world.to_quaternion() @ Vector((0, width / 2, 0))
        self.align(
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[0]),
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[4]),
            offset,
        )

    def align(self, start, end, offset=None):
        if offset is None:
            offset = Vector()
        recalculate_dumb_wall_origin(self.wall)
        recalculate_dumb_wall_origin(self.reference_wall)
        point, distance = mathutils.geometry.intersect_point_line(self.wall.matrix_world.translation, start, end)
        new_origin = point + offset
        self.wall.matrix_world.translation[0] = new_origin[0]
        self.wall.matrix_world.translation[1] = new_origin[1]
        self.wall.rotation_euler[2] = self.reference_wall.rotation_euler[2]


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
        self.recalculate_origins()

    # A T-junction is an ordered operation where a single end of wall1 is joined
    # to wall2 if possible (i.e. walls aren't parallel). Wall2 is not modified.
    # First, wall1 end faces are identified. We attempt to project an end face
    # at both ends to a front face of wall2. We then choose the end face that
    # has the shortest projection distance, and project it.
    def join_T(self):
        self._join_T()
        self.recalculate_origins()

    def _join_T(self):
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
            return (None, None, None)  # Life is short. BIM is hard.
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
        self._join_T()
        self.swap_walls()
        self.should_project_to_frontface = True
        self._join_T()
        self.recalculate_origins()

    # A V-junction is an unordered operation where wall1 is joined to wall2,
    # then vice versa. First, we do a T-junction from wall1 to wall2, then vice
    # versa. This creates a junction where the inner vertices of the mitre joint
    # touches, but the outer vertices do not. So, we just loop through the end
    # point vertices of each wall, find outer vertices (i.e. vertices that don't
    # touch the other wall), then continue projecting those to the back face of
    # the other wall.
    def join_V(self):
        wall2_end_faces, wall2_target_frontface, wall2_target_backface = self._join_T()
        self.swap_walls()
        wall1_end_faces, wall1_target_frontface, wall1_target_backface = self._join_T()

        for face in wall1_end_faces or []:
            for v in face.vertices:
                global_co = self.wall1_matrix @ self.wall1.data.vertices[v].co
                if self.wall2.closest_point_on_mesh(self.wall2_matrix.inverted() @ global_co, distance=0.001)[0]:
                    continue  # Vertex is already coincident with other wall, do not mitre
                target_face_center = self.wall2_matrix @ wall1_target_backface.center
                target_face_normal = (self.wall2_matrix.to_quaternion() @ wall1_target_backface.normal).normalized()
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)

        self.swap_walls()

        for face in wall2_end_faces or []:
            for v in face.vertices:
                global_co = self.wall1_matrix @ self.wall1.data.vertices[v].co
                if self.wall2.closest_point_on_mesh(self.wall2_matrix.inverted() @ global_co, distance=0.001)[0]:
                    continue  # Vertex is already coincident with other wall, do not mitre
                target_face_center = self.wall2_matrix @ wall2_target_backface.center
                target_face_normal = (self.wall2_matrix.to_quaternion() @ wall2_target_backface.normal).normalized()
                self.project_vertex(v, target_face_center, target_face_normal, self.wall1, self.wall1_matrix)
        self.recalculate_origins()

    def recalculate_origins(self):
        bpy.context.view_layer.update()
        recalculate_dumb_wall_origin(self.wall1)
        recalculate_dumb_wall_origin(self.wall2)

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
        original_point = wall_matrix @ wall.data.vertices[v].co
        point = mathutils.geometry.intersect_line_plane(
            original_point,
            (original_point) + self.pos_x,
            target_face_center,
            target_face_normal,
        )
        if not point or (point - original_point).length > 50:
            return
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
        self.file = IfcStore.get_file()
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
            bpy.context.scene.grease_pencil
            and len(bpy.context.scene.grease_pencil.layers) == 1
            and bpy.context.scene.grease_pencil.layers[0].active_frame.strokes
        )

    def derive_from_sketch(self):
        objs = []
        strokes = []
        layer = bpy.context.scene.grease_pencil.layers[0]

        for stroke in layer.active_frame.strokes:
            if len(stroke.points) == 1:
                continue
            coords = (stroke.points[0].co, stroke.points[-1].co)
            direction = coords[1] - coords[0]
            length = direction.length
            if length < 0.1:
                continue
            data = {"coords": coords}

            # Round to nearest 50mm (yes, metric for now)
            self.length = 0.05 * round(length / 0.05)
            self.rotation = math.atan2(direction[1], direction[0])
            # Round to nearest 5 degrees
            nearest_degree = (math.pi / 180) * 5
            self.rotation = nearest_degree * round(self.rotation / nearest_degree)
            self.location = coords[0]
            data["obj"] = self.create_wall()
            strokes.append(data)
            objs.append(data["obj"])

        if len(objs) < 2:
            return objs

        l_joins = set()
        for stroke in strokes:
            if not stroke["obj"]:
                continue
            for stroke2 in strokes:
                if stroke2 == stroke or not stroke2["obj"]:
                    continue
                if self.has_nearby_ends(stroke, stroke2):
                    wall_join = "-JOIN-".join(sorted([stroke["obj"].name, stroke2["obj"].name]))
                    if wall_join not in l_joins:
                        l_joins.add(wall_join)
                        DumbWallJoiner(stroke["obj"], stroke2["obj"]).join_L()
                elif self.has_end_near_stroke(stroke, stroke2):
                    DumbWallJoiner(stroke["obj"], stroke2["obj"]).join_T()
        bpy.context.scene.grease_pencil.layers.remove(layer)
        return objs

    def has_end_near_stroke(self, stroke, stroke2):
        point, distance = mathutils.geometry.intersect_point_line(stroke["coords"][0], *stroke2["coords"])
        if distance > 0 and distance < 1 and self.is_near(point, stroke["coords"][0]):
            return True
        point, distance = mathutils.geometry.intersect_point_line(stroke["coords"][1], *stroke2["coords"])
        if distance > 0 and distance < 1 and self.is_near(point, stroke["coords"][1]):
            return True

    def has_nearby_ends(self, stroke, stroke2):
        return (
            self.is_near(stroke["coords"][0], stroke2["coords"][0])
            or self.is_near(stroke["coords"][0], stroke2["coords"][1])
            or self.is_near(stroke["coords"][1], stroke2["coords"][0])
            or self.is_near(stroke["coords"][1], stroke2["coords"][1])
        )

    def is_near(self, point1, point2):
        return (point1 - point2).length < 0.1

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        if self.collection:
            for sibling_obj in self.collection.objects:
                if not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                if "IfcWall" not in sibling_obj.name:
                    continue
                local_location = sibling_obj.matrix_world.inverted() @ self.location
                raycast = sibling_obj.closest_point_on_mesh(local_location, distance=0.01)
                if not raycast[0]:
                    continue
                for face in sibling_obj.data.polygons:
                    if (
                        abs(face.normal.y) >= 0.75
                        and abs(mathutils.geometry.distance_point_to_plane(local_location, face.center, face.normal))
                        < 0.01
                    ):
                        # Rotate the wall in the direction of the face normal
                        normal = (sibling_obj.matrix_world.to_quaternion() @ face.normal).normalized()
                        self.rotation = math.atan2(normal[1], normal[0])
                        break
        return self.create_wall()

    def create_wall(self):
        verts = [
            Vector((0, self.width, 0)),
            Vector((0, 0, 0)),
            Vector((0, self.width, self.height)),
            Vector((0, 0, self.height)),
            Vector((self.length, self.width, 0)),
            Vector((self.length, 0, 0)),
            Vector((self.length, self.width, self.height)),
            Vector((self.length, 0, self.height)),
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
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, Name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, Properties={"Engine": "BlenderBIM.DumbWall"})
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSetUsage")
        MaterialData.load(self.file)
        return obj
