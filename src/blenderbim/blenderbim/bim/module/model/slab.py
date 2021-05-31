import bpy
import bmesh
import math
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import mathutils.geometry
from blenderbim.bim.ifc import IfcStore
from math import pi, degrees
from mathutils import Vector, Matrix
from ifcopenshell.api.material.data import Data as MaterialData


class DumbSlabGenerator:
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
        self.depth = sum(thicknesses) * unit_scale
        self.width = 3
        self.length = 3
        self.rotation = 0
        self.location = Vector((0, 0, 0))
        return self.derive_from_cursor()

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        return self.create_slab()

    def create_slab(self):
        verts = [
            Vector((0, 0, 0)),
            Vector((0, self.width, 0)),
            Vector((self.length, self.width, 0)),
            Vector((self.length, 0, 0)),
        ]
        edges = []
        faces = [[0, 3, 2, 1]]

        mesh = bpy.data.meshes.new(name="Dumb Slab")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Slab", mesh)
        modifier = obj.modifiers.new("Slab Depth", "SOLIDIFY")
        modifier.use_even_offset = True
        modifier.offset = 1
        modifier.thickness = self.depth
        obj.name = "Slab"
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2] - self.depth
        else:
            obj.location[2] -= self.depth
        self.collection.objects.link(obj)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcSlab", predefined_type="FLOOR")
        bpy.ops.bim.assign_type(relating_type=self.relating_type.id(), related_object=obj.name)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbSlab"})
        ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSetUsage")
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj
