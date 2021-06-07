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
        parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbColumn":
            return
        IfcStore.edited_objs.add(obj)
        bm = bmesh.from_edit_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.update_edit_mesh(obj.data)
        bm.free()


def ensure_solid(usecase_path, ifc_file, settings):
    product = ifc_file.by_id(settings["blender_object"].BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbColumn":
        return
    material = ifcopenshell.util.element.get_material(product)
    if material and material.is_a("IfcMaterialProfileSet"):
        settings["profile_set"] = material
    else:
        return
    settings["ifc_representation_class"] = "IfcExtrudedAreaSolid/IfcMaterialProfileSet"


class DumbColumnGenerator:
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
        return self.create_column()

    def create_column(self):
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

        mesh = bpy.data.meshes.new(name="Dumb Column")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Column", mesh)
        obj.name = "Column"
        obj.location = self.location
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2]
        self.collection.objects.link(obj)
        bpy.ops.bim.assign_class(
            obj=obj.name, ifc_class="IfcColumn", predefined_type="COLUMN", should_add_representation=False
        )
        bpy.ops.bim.assign_type(relating_type=self.relating_type.id(), related_object=obj.name)
        bpy.ops.bim.add_representation(
            obj=obj.name,
            context_id=ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW").id(),
            ifc_representation_class="IfcExtrudedAreaSolid/IfcMaterialProfileSet",
            profile_set=self.profile_set.id(),
        )
        representation = ifcopenshell.util.representation.get_representation(
            self.file.by_id(obj.BIMObjectProperties.ifc_definition_id), "Model", "Body", "MODEL_VIEW"
        )
        bpy.ops.bim.switch_representation(obj=obj.name, ifc_definition_id=representation.id(), should_reload=True)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbColumn"})
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj
