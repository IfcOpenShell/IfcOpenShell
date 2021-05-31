import bpy
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.module.model import product, wall, slab
from blenderbim.bim.ifc import IfcStore
from bpy.app.handlers import persistent

@persistent
def load_post(*args):
    ifcopenshell.api.add_post_listener("geometry.add_representation", IfcStore.get_file(), product.generate_box)
    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", IfcStore.get_file(), wall.generate_dumb_wall_axis
    )
    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", IfcStore.get_file(), wall.calculate_dumb_quantities
    )
    ifcopenshell.api.add_pre_listener(
        "material.edit_layer", IfcStore.get_file(), wall.DumbWallPlaner().regenerate_wall_thicknesses_from_layer
    )
    ifcopenshell.api.add_pre_listener(
        "type.assign_type", IfcStore.get_file(), wall.DumbWallPlaner().regenerate_wall_thicknesses_from_type
    )
