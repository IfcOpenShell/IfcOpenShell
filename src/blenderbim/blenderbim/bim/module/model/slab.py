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
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbSlab":
            return
        IfcStore.edited_objs.add(obj)
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


def ensure_solid(usecase_path, ifc_file, settings):
    product = ifc_file.by_id(settings["blender_object"].BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbSlab":
        return
    settings["ifc_representation_class"] = "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"


def generate_footprint(usecase_path, ifc_file, settings):
    footprint_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "FootPrint", "SKETCH_VIEW")
    if not footprint_context:
        return
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbSlab":
        return
    old_footprint = ifcopenshell.util.representation.get_representation(product, "Plan", "FootPrint", "SKETCH_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_footprint:
            bpy.ops.bim.remove_representation(representation_id=old_footprint.id(), obj=obj.name)

        helper = Helper(ifc_file)
        indices = helper.auto_detect_arbitrary_profile_with_voids_extruded_area_solid(settings["geometry"])

        bm = bmesh.new()
        bm.from_mesh(settings["geometry"])
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        profile_edges = []

        def append_profile_edges(profile_edges, indices):
            indices.append(indices[0]) # Close the loop
            edge_vert_pairs = list(zip(indices, indices[1:]))
            for p in edge_vert_pairs:
                profile_edges.append(
                    [e for e in bm.verts[p[0]].link_edges if e.other_vert(bm.verts[p[0]]).index == p[1]][0]
                )

        append_profile_edges(profile_edges, indices["profile"])
        for inner_indices in indices["inner_curves"]:
            append_profile_edges(profile_edges, inner_indices)

        irrelevant_edges = [e for e in bm.edges if e not in profile_edges]
        bmesh.ops.delete(bm, geom=irrelevant_edges, context="EDGES")
        mesh = bpy.data.meshes.new("Temporary Footprint")
        bm.to_mesh(mesh)
        bm.free()

        new_settings = settings.copy()
        new_settings["context"] = footprint_context
        new_settings["geometry"] = mesh
        new_footprint = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )

        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_footprint}
        )
        bpy.data.meshes.remove(mesh)


def calculate_quantities(usecase_path, ifc_file, settings):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbSlab":
        return
    qto = ifcopenshell.api.run(
        "pset.add_qto", ifc_file, should_run_listeners=False, product=product, name="Qto_SlabBaseQuantities"
    )
    length = obj.dimensions[0] / unit_scale
    width = obj.dimensions[1] / unit_scale
    depth = obj.dimensions[2] / unit_scale

    perimeter = 0
    helper = Helper(ifc_file)
    indices = helper.auto_detect_arbitrary_profile_with_voids_extruded_area_solid(settings["geometry"])

    bm = bmesh.new()
    bm.from_mesh(settings["geometry"])
    bm.verts.ensure_lookup_table()

    def calculate_profile_length(indices):
        indices.append(indices[0]) # Close the loop
        edge_vert_pairs = list(zip(indices, indices[1:]))
        return sum([(bm.verts[p[1]].co - bm.verts[p[0]].co).length for p in edge_vert_pairs])

    perimeter += calculate_profile_length(indices["profile"])
    for inner_indices in indices["inner_curves"]:
        perimeter += calculate_profile_length(inner_indices)

    bm.free()

    if product.HasOpenings:
        # TODO: calculate gross / net
        gross_area = 0
        net_area = 0
        gross_volume = 0
        net_volume = 0
    else:
        bm = bmesh.new()
        bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
        bm.faces.ensure_lookup_table()
        gross_area = sum([f.calc_area() for f in bm.faces if f.normal.z > 0.9])
        net_area = gross_area
        gross_volume = bm.calc_volume()
        net_volume = gross_volume
        bm.free()

    properties={
        "Depth": round(depth, 2),
        "Perimeter": round(perimeter, 2),
        "GrossArea": round(gross_area, 2),
        "NetArea": round(net_area, 2),
        "GrossVolume": round(gross_volume, 2),
        "NetVolume": round(net_volume, 2),
    }

    if round(obj.dimensions[0] * obj.dimensions[1] * obj.dimensions[2], 2) == round(gross_volume, 2):
        properties.update({
            "Length": round(length, 2),
            "Width": round(width, 2),
        })
    else:
        properties.update({
            "Length": None,
            "Width": None,
        })

    ifcopenshell.api.run( "pset.edit_qto", ifc_file, should_run_listeners=False, qto=qto, properties=properties)
    PsetData.load(ifc_file, obj.BIMObjectProperties.ifc_definition_id)


class AddSlabOpening(bpy.types.Operator):
    bl_idname = "bim.add_slab_opening"
    bl_label = "Add Slab Opening"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) == 0 or not context.active_object:
            return {"FINISHED"}
        slab_obj = context.active_object
        if not slab_obj.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        slab = IfcStore.get_file().by_id(slab_obj.BIMObjectProperties.ifc_definition_id)
        if not slab.is_a("IfcSlab"):
            return {"FINISHED"}
        local_location = slab_obj.matrix_world.inverted() @ context.scene.cursor.location
        raycast = slab_obj.closest_point_on_mesh(local_location, distance=0.01)
        if not raycast[0]:
            return {"FINISHED"}
        bpy.ops.mesh.primitive_cube_add(size=slab_obj.dimensions[2] * 2)
        opening = context.selected_objects[0]

        # Place the opening in the middle of the slab
        global_location = slab_obj.matrix_world @ raycast[1]
        normal = raycast[2]
        normal.negate()
        global_normal = slab_obj.matrix_world.to_quaternion() @ normal
        opening.location = global_location + (global_normal * (slab_obj.dimensions[2] / 2))

        opening.rotation_euler = slab_obj.rotation_euler
        opening.name = "Opening"
        bpy.ops.bim.add_opening(opening=opening.name, obj=slab_obj.name)
        return {"FINISHED"}


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
        bpy.ops.bim.assign_class(
            obj=obj.name,
            ifc_class="IfcSlab",
            predefined_type="FLOOR",
            ifc_representation_class="IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids",
        )
        bpy.ops.bim.assign_type(relating_type=self.relating_type.id(), related_object=obj.name)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbSlab"})
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj


class DumbSlabPlaner:
    def regenerate_from_layer(self, usecase_path, ifc_file, settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        layer = settings["layer"]
        thickness = settings["attributes"].get("LayerThickness")
        if thickness is None:
            return
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
                            self.change_thickness(element, thickness)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, thickness)

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material or not new_material.is_a("IfcMaterialLayerSet"):
            return
        new_thickness = sum([l.LayerThickness for l in new_material.MaterialLayers])
        self.change_thickness(settings["related_object"], new_thickness)

    def change_thickness(self, element, thickness):
        parametric = ifcopenshell.util.element.get_psets(element).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbSlab":
            return

        obj = IfcStore.get_element(element.id())
        if not obj:
            return

        delta_thickness = (thickness * self.unit_scale) - obj.dimensions.z
        if round(delta_thickness, 2) == 0:
            return

        modifier = [m for m in obj.modifiers if m.type == "SOLIDIFY"]
        if modifier:
            modifier = modifier[0]
        else:
            pass
        modifier.thickness += delta_thickness
        obj.location[2] -= delta_thickness
