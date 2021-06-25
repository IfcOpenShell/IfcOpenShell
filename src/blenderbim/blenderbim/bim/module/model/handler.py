import bpy
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.module.model import product, wall, slab, column
from blenderbim.bim.ifc import IfcStore
from bpy.app.handlers import persistent


@persistent
def load_post(*args):
    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.Product.GenerateBox", product.generate_box
    )
    ifcopenshell.api.add_post_listener(
        "material.edit_profile_usage",
        "BlenderBIM.Product.RegenerateProfileUsage",
        product.regenerate_profile_usage,
    )

    IfcStore.add_element_listener(wall.element_listener)
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

    IfcStore.add_element_listener(slab.element_listener)
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

    IfcStore.add_element_listener(column.element_listener)
    ifcopenshell.api.add_pre_listener(
        "geometry.add_representation", "BlenderBIM.DumbColumn.EnsureSolid", column.ensure_solid
    )
    ifcopenshell.api.add_post_listener(
        "material.edit_profile",
        "BlenderBIM.DumbColumn.RegenerateFromProfile",
        column.DumbColumnRegenerator().regenerate_from_profile,
    )
    ifcopenshell.api.add_post_listener(
        "type.assign_type",
        "BlenderBIM.DumbColumn.RegenerateFromType",
        column.DumbColumnRegenerator().regenerate_from_type,
    )
