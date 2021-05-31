import bpy
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.module.model import product, wall, slab
from blenderbim.bim.ifc import IfcStore
from bpy.app.handlers import persistent


@persistent
def load_post(*args):
    ifcopenshell.api.add_post_listener("geometry.add_representation", None, product.generate_box)

    ifcopenshell.api.add_post_listener("geometry.add_representation", None, wall.generate_axis)
    ifcopenshell.api.add_post_listener("geometry.add_representation", None, wall.calculate_quantities)
    ifcopenshell.api.add_pre_listener("material.edit_layer", None, wall.DumbWallPlaner().regenerate_from_layer)
    ifcopenshell.api.add_pre_listener("type.assign_type", None, wall.DumbWallPlaner().regenerate_from_type)

    IfcStore.add_element_listener(slab.element_listener)
    ifcopenshell.api.add_pre_listener("material.edit_layer", None, slab.DumbSlabPlaner().regenerate_from_layer)
    ifcopenshell.api.add_pre_listener("type.assign_type", None, slab.DumbSlabPlaner().regenerate_from_type)
