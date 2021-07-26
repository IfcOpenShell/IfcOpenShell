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
from math import pi, degrees
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
        if self.relating_type.is_a("IfcColumnType"):
            obj.name = "Column"
            bpy.ops.bim.assign_class(
                obj=obj.name, ifc_class="IfcColumn", predefined_type="COLUMN", should_add_representation=False
            )
        elif self.relating_type.is_a("IfcBeamType"):
            obj.name = "Beam"
            obj.rotation_euler[0] = math.pi / 2
            obj.rotation_euler[2] = math.pi / 2
            bpy.ops.bim.assign_class(
                obj=obj.name, ifc_class="IfcBeam", predefined_type="BEAM", should_add_representation=False
            )
        elif self.relating_type.is_a("IfcMemberType"):
            obj.name = "Member"
            obj.rotation_euler[0] = math.pi / 2
            obj.rotation_euler[2] = math.pi / 2
            bpy.ops.bim.assign_class(
                obj=obj.name, ifc_class="IfcMember", predefined_type="MEMBER", should_add_representation=False
            )
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
