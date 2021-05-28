import bpy
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset.data import Data as PsetData
from math import pi
from mathutils import Vector


def generate_box(usecase_path, ifc_file, **settings):
    box_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Box", "MODEL_VIEW")
    if not box_context:
        return
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    old_box = ifcopenshell.util.representation.get_representation(product, "Model", "Box", "MODEL_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_box:
            bpy.ops.bim.remove_representation(representation_id=old_box.id(), obj=obj.name)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box}
        )


def generate_dumb_wall_axis(usecase_path, ifc_file, **settings):
    axis_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Axis", "GRAPH_VIEW")
    if not axis_context:
        return
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbWall":
        return
    old_axis = ifcopenshell.util.representation.get_representation(product, "Model", "Axis", "GRAPH_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_axis:
            bpy.ops.bim.remove_representation(representation_id=old_axis.id(), obj=obj.name)

        new_settings = settings.copy()
        new_settings["context"] = axis_context

        mesh = bpy.data.meshes.new("Temporary Axis")
        start = Vector(obj.bound_box[0])
        end = Vector(obj.bound_box[4])
        mesh.from_pydata([start, end], [(0, 1)], [])

        new_settings["geometry"] = mesh
        new_axis = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_axis}
        )
        bpy.data.meshes.remove(mesh)


def calculate_dumb_quantities(usecase_path, ifc_file, **settings):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or parametric["Engine"] != "BlenderBIM.DumbWall":
        return
    qto = ifcopenshell.api.run(
        "pset.add_qto", ifc_file, should_run_listeners=False, product=product, name="Qto_WallBaseQuantities"
    )
    length = obj.dimensions[0] / unit_scale
    width = obj.dimensions[1] / unit_scale
    height = obj.dimensions[2] / unit_scale

    if product.HasOpenings:
        # TODO: calculate gross / net
        gross_volume = 0
        net_volume = 0
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        gross_volume = bm.calc_volume()
        net_volume = gross_volume
        bm.free()

    ifcopenshell.api.run("pset.edit_qto", ifc_file, should_run_listeners=False, qto=qto, properties={
        "Length": round(length, 2),
        "Width": round(width, 2),
        "Height": round(height, 2),
        "GrossVolume": round(gross_volume, 2),
        "NetVolume": round(net_volume, 2)
    })
    PsetData.load(ifc_file, obj.BIMObjectProperties.ifc_definition_id)


class DumbWallPlaner:
    def regenerate_dumb_wall_thicknesses(self, usecase_path, ifc_file, **settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        layer = settings["layer"]
        thickness = settings["attributes"].get("LayerThickness")
        if thickness is None or layer.LayerThickness == thickness:
            return
        delta_thickness = thickness - layer.LayerThickness
        for layer_set in layer.ToMaterialLayerSet:
            total_thickness = sum([l.LayerThickness for l in layer_set.MaterialLayers]) * self.unit_scale
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
                            self.regenerate_wall_thickness(element, delta_thickness)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.regenerate_wall_thickness(element, delta_thickness)

    def regenerate_wall_thickness(self, element, delta_thickness):
        parametric = ifcopenshell.util.element.get_psets(element).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbWall":
            return
        try:
            obj = IfcStore.id_map[element.id()]
            obj.name # In case the object has been deleted
        except:
            return

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)

        min_face, max_face = self.get_wall_end_faces(obj, bm)

        self.thicken_face(min_face, delta_thickness)
        self.thicken_face(max_face, delta_thickness)

        bm.to_mesh(obj.data)
        obj.data.update()
        bm.free()

    def thicken_face(self, face, delta_thickness):
        slide_magnitude = abs(delta_thickness) / 2 * self.unit_scale
        for vert in face.verts:
            slide_vector = None
            for edge in vert.link_edges:
                other_vert = edge.verts[1] if edge.verts[0] == vert else edge.verts[0]
                if delta_thickness > 0:
                    potential_slide_vector = vert.co - other_vert.co
                else:
                    potential_slide_vector = other_vert.co - vert.co
                if abs(potential_slide_vector.x) > 0.9 or abs(potential_slide_vector.z) > 0.9:
                    continue
                slide_vector = potential_slide_vector
                break
            if not slide_vector:
                continue
            slide_vector *= (slide_magnitude / abs(slide_vector.y))
            vert.co += slide_vector

    # An end face is a quad that is on one end of the wall or the other. It must
    # have at least one vertex on either extreme X-axis, and a non-insignificant
    # X component of its face normal
    def get_wall_end_faces(self, wall, bm):
        min_face = None
        max_face = None
        min_x = min([v[0] for v in wall.bound_box])
        max_x = max([v[0] for v in wall.bound_box])
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            for v in f.verts:
                if v.co.x == min_x and abs(f.normal.x) > 0.1:
                    min_face = f
                elif v.co.x == max_x and abs(f.normal.x) > 0.1:
                    max_face = f
            if min_face and max_face:
                break
        return min_face, max_face


class ActivateParametricEngine(bpy.types.Operator):
    bl_idname = "bim.activate_parametric_engine"
    bl_label = "Activate Parametric Engine"

    def execute(self, context):
        ifcopenshell.api.add_post_listener("geometry.add_representation", IfcStore.get_file(), generate_box)
        ifcopenshell.api.add_post_listener(
            "geometry.add_representation", IfcStore.get_file(), generate_dumb_wall_axis
        )
        ifcopenshell.api.add_post_listener(
            "geometry.add_representation", IfcStore.get_file(), calculate_dumb_quantities
        )
        ifcopenshell.api.add_pre_listener(
            "material.edit_layer", IfcStore.get_file(), DumbWallPlaner().regenerate_dumb_wall_thicknesses
        )
        return {"FINISHED"}
