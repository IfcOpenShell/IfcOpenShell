import bpy
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset.data import Data as PsetData
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
        start = (Vector(obj.bound_box[3]) + Vector(obj.bound_box[0])) / 2
        end = (Vector(obj.bound_box[7]) + Vector(obj.bound_box[4])) / 2
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
        "pset.add_qto", ifc_file, should_run_listeners=False, product=product, Name="Qto_WallBaseQuantities"
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

    ifcopenshell.api.run("pset.edit_qto", ifc_file, should_run_listeners=False, qto=qto, Properties={
        "Length": round(length, 2),
        "Width": round(width, 2),
        "Height": round(height, 2),
        "GrossVolume": round(gross_volume, 2),
        "NetVolume": round(net_volume, 2)
    })
    PsetData.load(ifc_file, obj.BIMObjectProperties.ifc_definition_id)


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
        return {"FINISHED"}
