import bpy
import bmesh
import math
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import ifcopenshell.util.element
import mathutils.geometry
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
from math import pi, degrees, inf
from mathutils import Vector, Matrix
from ifcopenshell.api.pset.data import Data as PsetData
from ifcopenshell.api.material.data import Data as MaterialData
from blenderbim.bim.module.geometry.helper import Helper


def element_listener(element, obj):
    blenderbim.bim.handler.subscribe_to(obj, "mode", mode_callback)


def mode_callback(obj, data):
    for obj in set(bpy.context.selected_objects + [bpy.context.active_object]):
        if (
            not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbProfile":
            return
        if obj.mode == "EDIT":
            IfcStore.edited_objs.add(obj)
            bm = bmesh.from_edit_mesh(obj.data)
            bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
            bmesh.update_edit_mesh(obj.data)
            bm.free()
        else:
            material_usage = ifcopenshell.util.element.get_material(product)
            x, y = obj.dimensions[0:2]
            if not material_usage.CardinalPoint:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((x, y, 0)) / 2))
            elif material_usage.CardinalPoint == 1:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[4])
            elif material_usage.CardinalPoint == 2:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((x, 0, 0)) / 2))
            elif material_usage.CardinalPoint == 3:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[0])
            elif material_usage.CardinalPoint == 4:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[4]) + (Vector((0, y, 0)) / 2))
            elif material_usage.CardinalPoint == 5:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((x, y, 0)) / 2))
            elif material_usage.CardinalPoint == 6:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[0]) + (Vector((0, y, 0)) / 2))
            elif material_usage.CardinalPoint == 7:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[7])
            elif material_usage.CardinalPoint == 8:
                new_origin = obj.matrix_world @ (Vector(obj.bound_box[3]) + (Vector((x, 0, 0)) / 2))
            elif material_usage.CardinalPoint == 9:
                new_origin = obj.matrix_world @ Vector(obj.bound_box[3])
            if (obj.matrix_world.translation - new_origin).length < 0.001:
                return
            obj.data.transform(
                Matrix.Translation(
                    (obj.matrix_world.inverted().to_quaternion() @ (obj.matrix_world.translation - new_origin))
                )
            )
            obj.matrix_world.translation = new_origin


def ensure_solid(usecase_path, ifc_file, settings):
    product = ifc_file.by_id(settings["blender_object"].BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbProfile":
        return
    material = ifcopenshell.util.element.get_material(product)
    if material and material.is_a("IfcMaterialProfileSetUsage"):
        settings["profile_set_usage"] = material
    else:
        return
    settings["ifc_representation_class"] = "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage"


class DumbProfileGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type

    def generate(self):
        self.file = IfcStore.get_file()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        material = ifcopenshell.util.element.get_material(self.relating_type)
        if material and material.is_a("IfcMaterialProfileSet"):
            self.profile_set = material
        else:
            return

        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.length = 3
        self.rotation = 0
        self.location = Vector((0, 0, 0))
        return self.derive_from_cursor()

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        return self.create_profile()

    def create_profile(self):
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

        mesh = bpy.data.meshes.new(name="Dumb Profile")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Profile", mesh)
        obj.location = self.location
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2]
        self.collection.objects.link(obj)

        ifc_classes = ifcopenshell.util.type.get_applicable_entities(self.relating_type.is_a(), self.file.schema)
        # Standard cases are deprecated, so let's cull them
        ifc_class = [c for c in ifc_classes if "StandardCase" not in c][0]
        obj.name = ifc_class[3:]
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=ifc_class, should_add_representation=False)

        if self.relating_type.is_a() in ["IfcBeamType", "IfcMemberType"]:
            obj.rotation_euler[0] = math.pi / 2
            obj.rotation_euler[2] = math.pi / 2

        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        bpy.ops.bim.assign_type(relating_type=self.relating_type.id(), related_object=obj.name)
        profile_set_usage = ifcopenshell.util.element.get_material(element)
        bpy.ops.bim.add_representation(
            obj=obj.name,
            context_id=ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW").id(),
            ifc_representation_class="IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage",
            profile_set_usage=profile_set_usage.id(),
        )
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        bpy.ops.bim.switch_representation(
            obj=obj.name, ifc_definition_id=representation.id(), should_reload=True, should_switch_all_meshes=True
        )
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbProfile"})
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj


class DumbProfileRegenerator:
    def regenerate_from_profile(self, usecase_path, ifc_file, settings):
        self.file = ifc_file
        profile = settings["profile"].Profile
        if not profile:
            return
        for element in self.get_elements_using_profile(profile):
            self.change_profile(element)

    def sync_object_from_profile(self, usecase_path, ifc_file, settings):
        self.file = ifc_file
        profile = settings["profile"].Profile
        if not profile:
            return
        for element in self.get_elements_using_profile(profile):
            self.sync_object(element)

    def get_elements_using_profile(self, profile):
        results = []
        for profile_set in [
            mp.ToMaterialProfileSet[0] for mp in self.file.get_inverse(profile) if mp.is_a("IfcMaterialProfile")
        ]:
            for inverse in self.file.get_inverse(profile_set):
                if not inverse.is_a("IfcMaterialProfileSetUsage"):
                    continue
                if self.file.schema == "IFC2X3":
                    for rel in self.file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        results.extend(rel.RelatedObjects)
                else:
                    for rel in inverse.AssociatedTo:
                        results.extend(rel.RelatedObjects)
        return results

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material or not new_material.is_a("IfcMaterialProfileSet"):
            return
        self.change_profile(settings["related_object"])

    def change_profile(self, element):
        obj = IfcStore.get_element(element.id())
        if not obj:
            return
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if representation:
            bpy.ops.bim.switch_representation(
                obj=obj.name, ifc_definition_id=representation.id(), should_reload=True, should_switch_all_meshes=True
            )

    def sync_object(self, element):
        obj = IfcStore.get_element(element.id())
        if not obj or obj not in IfcStore.edited_objs:
            return
        bpy.ops.bim.update_representation(obj=obj.name)


class ExtendProfile(bpy.types.Operator):
    bl_idname = "bim.extend_profile"
    bl_label = "Extend Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected_objs = context.selected_objects
        for obj in selected_objs:
            bpy.ops.bim.dynamically_void_product(obj=obj.name)
        if len(selected_objs) == 0:
            return {"FINISHED"}
        if not context.active_object:
            return {"FINISHED"}
        if len(selected_objs) == 1:
            DumbProfileExtender(context.active_object, target_coordinate=context.scene.cursor.location).extend()
            IfcStore.edited_objs.add(context.active_object)
            return {"FINISHED"}
        if len(selected_objs) < 2:
            return {"FINISHED"}
        for obj in selected_objs:
            if obj == context.active_object:
                continue
            DumbProfileExtender(obj, context.active_object).extend()
            IfcStore.edited_objs.add(obj)
        return {"FINISHED"}


class DumbProfileExtender:
    # A profile is a prismatic extrusion along its local Z axis.
    def __init__(self, profile, target=None, target_coordinate=None):
        self.profile = profile
        self.target = target
        self.target_coordinate = target_coordinate

    # An extension of a profile is determined by casting a ray from the cardinal
    # point of either extreme along the profiles local Z axis to a target
    # object. The nearest result from this raycast will be the target extension
    # point.
    def extend(self):
        extension_data = self.get_closest_extension_point()
        if not extension_data:
            return
        if extension_data["end"] == "bottom":
            self.profile.matrix_world.translation = extension_data["contact"]
            if extension_data["direction"] == "up":
                self.shift_top_faces(-extension_data["distance"])
            elif extension_data["direction"] == "down":
                self.shift_top_faces(extension_data["distance"])
        if extension_data["end"] == "top":
            if extension_data["direction"] == "up":
                self.shift_top_faces(extension_data["distance"])
            elif extension_data["direction"] == "down":
                self.shift_top_faces(-extension_data["distance"])

    def shift_top_faces(self, z):
        vertices = []
        for f in self.get_profile_top_faces():
            vertices.extend(f.vertices)
        for v in set(vertices):
            self.profile.data.vertices[v].co.z += z

    # An top face is defined as having at least one vertex on the max
    # Z-axis, and a non-insignificant Z component of its face normal
    def get_profile_top_faces(self):
        faces = []
        max_z = max([v[2] for v in self.profile.bound_box])
        for f in self.profile.data.polygons:
            if abs(f.normal.z) < 0.1:
                continue
            for v in f.vertices:
                if self.profile.data.vertices[v].co.z == max_z:
                    faces.append(f)
                    break
        return faces

    def get_closest_extension_point(self):
        top = self.profile.matrix_world @ Vector((0, 0, self.profile.dimensions[2]))
        bottom = self.profile.matrix_world.translation
        up = self.profile.matrix_world.to_quaternion() @ Vector((0, 0, 1))
        down = self.profile.matrix_world.to_quaternion() @ Vector((0, 0, -1))

        if self.target:
            return self.get_closest_extension_point_from_target_obj(top, bottom, up, down)
        elif self.target_coordinate:
            return self.get_closest_extension_point_from_target_coordinate(top, bottom, up, down)

    def get_closest_extension_point_from_target_coordinate(self, top, bottom, up, down):
        point = mathutils.geometry.intersect_line_plane(
            bottom, top, self.target_coordinate, self.profile.matrix_world.to_quaternion() @ Vector((0, 0, 1))
        )
        if not point:
            return
        top_distance = (point - top).length
        bottom_distance = (point - bottom).length
        if top_distance < bottom_distance:
            intersection_point, signed_distance = mathutils.geometry.intersect_point_line(point, top, bottom)
            if signed_distance > 0:
                return {"contact": point, "distance": top_distance, "end": "top", "direction": "down"}
            else:
                return {"contact": point, "distance": top_distance, "end": "top", "direction": "up"}
        else:
            intersection_point, signed_distance = mathutils.geometry.intersect_point_line(point, bottom, top)
            if signed_distance > 0:
                return {"contact": point, "distance": bottom_distance, "end": "bottom", "direction": "up"}
            else:
                return {"contact": point, "distance": bottom_distance, "end": "bottom", "direction": "down"}

    def get_closest_extension_point_from_target_obj(self, top, bottom, up, down):
        t_top = self.target.matrix_world.inverted() @ top
        t_bottom = self.target.matrix_world.inverted() @ bottom
        t_up = self.target.matrix_world.inverted().to_quaternion() @ up
        t_down = self.target.matrix_world.inverted().to_quaternion() @ down

        results = []
        results.append((self.target.ray_cast(t_top, t_up, distance=50), top, "top", "up"))
        results.append((self.target.ray_cast(t_top, t_down, distance=50), top, "top", "down"))
        results.append((self.target.ray_cast(t_bottom, t_up, distance=50), bottom, "bottom", "up"))
        results.append((self.target.ray_cast(t_bottom, t_down, distance=50), bottom, "bottom", "down"))

        min_distance = float(inf)
        final = None

        for result in results:
            if result[0][0]:
                contact = self.target.matrix_world @ result[0][1]
                distance = (contact - result[1]).length
                if distance < min_distance:
                    min_distance = distance
                    final = {"contact": contact, "distance": distance, "end": result[2], "direction": result[3]}

        return final
