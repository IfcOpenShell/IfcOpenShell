import bpy
import bmesh
import math
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import mathutils.geometry
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
from math import pi, degrees
from mathutils import Vector, Matrix
from ifcopenshell.api.material.data import Data as MaterialData


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
        if parametric and parametric["Engine"] != "BlenderBIM.DumbSlab":
            return
        modifier = [m for m in obj.modifiers if m.type == "SOLIDIFY"]
        if modifier:
            return
        depth = obj.dimensions.z
        bm = bmesh.from_edit_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bm.faces.ensure_lookup_table()
        non_bottom_faces = []
        for face in bm.faces:
            if face.normal.z > -0.9:
                non_bottom_faces.append(face)
            else:
                face.normal_flip()
        bmesh.ops.delete(bm, geom=non_bottom_faces, context="FACES")
        bmesh.update_edit_mesh(obj.data)
        bm.free()
        modifier = obj.modifiers.new("Slab Depth", "SOLIDIFY")
        modifier.use_even_offset = True
        modifier.offset = 1
        modifier.thickness = depth


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
        obj.location = self.location
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
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj


class DumbSlabPlaner:
    def regenerate_from_layer(self, usecase_path, ifc_file, **settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        layer = settings["layer"]
        thickness = settings["attributes"].get("LayerThickness")
        if thickness is None or layer.LayerThickness == thickness:
            return
        delta_thickness = thickness - layer.LayerThickness
        for layer_set in layer.ToMaterialLayerSet:
            total_thickness = sum([l.LayerThickness for l in layer_set.MaterialLayers])
            if not total_thickness:
                continue
            for inverse in ifc_file.get_inverse(layer_set):
                if not inverse.is_a("IfcMaterialLayerSetUsage"):
                    continue
                if ifc_file.schema == "IFC2X3":
                    for rel in ifc_file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, delta_thickness)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, delta_thickness)

    def regenerate_from_type(self, usecase_path, ifc_file, **settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material.is_a("IfcMaterialLayerSet"):
            return
        obj = IfcStore.get_element(settings["related_object"].id())
        if not obj:
            return
        current_thickness = obj.dimensions.z / self.unit_scale
        new_thickness = sum([l.LayerThickness for l in new_material.MaterialLayers])
        if current_thickness == new_thickness:
            return
        self.change_thickness(settings["related_object"], new_thickness - current_thickness)

    def change_thickness(self, element, delta_thickness):
        parametric = ifcopenshell.util.element.get_psets(element).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbSlab":
            return

        obj = IfcStore.get_element(element.id())
        if not obj:
            return

        modifier = [m for m in obj.modifiers if m.type == "SOLIDIFY"]
        if modifier:
            modifier = modifier[0]
        else:
            pass
        modifier.thickness += delta_thickness * self.unit_scale
        obj.location[2] -= delta_thickness * self.unit_scale
