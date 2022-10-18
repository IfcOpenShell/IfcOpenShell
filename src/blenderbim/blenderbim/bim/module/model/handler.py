# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.module.model import root, product, wall, slab, profile, opening, task
from blenderbim.bim.ifc import IfcStore
from bpy.app.handlers import persistent


@persistent
def load_post(*args):
    ifcopenshell.api.add_pre_listener("attribute.edit_attributes", "BlenderBIM.Root.SyncName", root.sync_name)
    ifcopenshell.api.add_pre_listener("style.edit_presentation_style", "BlenderBIM.Root.SyncStyleName", root.sync_name)

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

    IfcStore.add_element_listener(wall.element_listener)
    IfcStore.add_element_listener(profile.element_listener)

    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.DumbWall.CalculateQuantities", wall.calculate_quantities
    )
    ifcopenshell.api.add_post_listener(
        "material.edit_layer", "BlenderBIM.DumbWall.RegenerateFromLayer", wall.DumbWallPlaner().regenerate_from_layer
    )
    ifcopenshell.api.add_post_listener(
        "type.assign_type", "BlenderBIM.DumbWall.RegenerateFromType", wall.DumbWallPlaner().regenerate_from_type
    )

    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "BlenderBIM.DumbSlab.CalculateQuantities", slab.calculate_quantities
    )
    ifcopenshell.api.add_post_listener(
        "material.edit_layer", "BlenderBIM.DumbSlab.RegenerateFromLayer", slab.DumbSlabPlaner().regenerate_from_layer
    )
    ifcopenshell.api.add_post_listener(
        "type.assign_type", "BlenderBIM.DumbSlab.RegenerateFromType", slab.DumbSlabPlaner().regenerate_from_type
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
