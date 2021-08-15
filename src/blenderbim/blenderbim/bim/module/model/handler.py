import bpy
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.module.model import root, product, wall, slab, profile, opening, task
from blenderbim.bim.ifc import IfcStore
from bpy.app.handlers import persistent


@persistent
def load_post(*args):
    ifcopenshell.api.add_pre_listener("attribute.edit_attributes", "BlenderBIM.Root.SyncName", root.sync_name)

    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.Product.GenerateBox", product.generate_box
    )

    ifcopenshell.api.add_post_listener(
        "sequence.edit_task_time", "BlenderBIM.Task.CalculateQuantities", task.calculate_quantities
    )

    for usecase in [
        "material.assign_material",
        "material.edit_constituent",
        "material.edit_layer",
        "material.edit_profile",
        "material.add_constituent",
        "material.add_layer",
        "material.add_profile",
    ]:
        ifcopenshell.api.add_post_listener(
            usecase, "BlenderBIM.Product.EnsureMaterialAssigned", product.ensure_material_assigned
        )

    ifcopenshell.api.add_post_listener(
        "material.edit_profile_usage",
        "BlenderBIM.Product.RegenerateProfileUsage",
        product.regenerate_profile_usage,
    )

    IfcStore.add_element_listener(opening.element_listener)
    IfcStore.add_element_listener(wall.element_listener)
    IfcStore.add_element_listener(slab.element_listener)
    IfcStore.add_element_listener(profile.element_listener)

    ifcopenshell.api.add_pre_listener(
        "geometry.add_representation", "BlenderBIM.DumbWall.EnsureSolid", wall.ensure_solid
    )
    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.DumbWall.GenerateAxis", wall.generate_axis
    )
    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.DumbWall.CalculateQuantities", wall.calculate_quantities
    )
    ifcopenshell.api.add_pre_listener(
        "material.edit_layer", "BlenderBIM.DumbWall.RegenerateFromLayer", wall.DumbWallPlaner().regenerate_from_layer
    )
    ifcopenshell.api.add_pre_listener(
        "type.assign_type", "BlenderBIM.DumbWall.RegenerateFromType", wall.DumbWallPlaner().regenerate_from_type
    )

    ifcopenshell.api.add_pre_listener(
        "geometry.add_representation", "BlenderBIM.DumbSlab.EnsureSolid", slab.ensure_solid
    )
    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.DumbSlab.GenerateFootprint", slab.generate_footprint
    )
    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.DumbSlab.CalculateQuantities", slab.calculate_quantities
    )
    ifcopenshell.api.add_pre_listener(
        "material.edit_layer", "BlenderBIM.DumbSlab.RegenerateFromLayer", slab.DumbSlabPlaner().regenerate_from_layer
    )
    ifcopenshell.api.add_pre_listener(
        "type.assign_type", "BlenderBIM.DumbSlab.RegenerateFromType", slab.DumbSlabPlaner().regenerate_from_type
    )

    ifcopenshell.api.add_pre_listener(
        "geometry.add_representation", "BlenderBIM.DumbProfile.EnsureSolid", profile.ensure_solid
    )
    ifcopenshell.api.add_pre_listener(
        "material.edit_profile",
        "BlenderBIM.DumbProfile.SyncObjectFromProfile",
        profile.DumbProfileRegenerator().sync_object_from_profile,
    )
    ifcopenshell.api.add_post_listener(
        "material.edit_profile",
        "BlenderBIM.DumbProfile.RegenerateFromProfile",
        profile.DumbProfileRegenerator().regenerate_from_profile,
    )
    ifcopenshell.api.add_post_listener(
        "type.assign_type",
        "BlenderBIM.DumbProfile.RegenerateFromType",
        profile.DumbProfileRegenerator().regenerate_from_type,
    )
