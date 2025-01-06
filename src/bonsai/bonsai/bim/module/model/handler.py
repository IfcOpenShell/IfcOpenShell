# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api
from bonsai.bim.module.model import root, product, wall, slab, profile, opening, task
from bonsai.bim.ifc import IfcStore
from bpy.app.handlers import persistent


@persistent
def load_post(*args):
    ifcopenshell.api.add_pre_listener("style.edit_presentation_style", "Bonsai.Root.SyncStyleName", root.sync_name)

    ifcopenshell.api.add_post_listener(
        "geometry.add_representation", "Bonsai.Product.GenerateBox", product.generate_box
    )

    ifcopenshell.api.add_post_listener(
        "sequence.edit_task_time", "Bonsai.Task.CalculateQuantities", task.calculate_quantities
    )

    ifcopenshell.api.add_post_listener(
        "material.edit_profile_usage",
        "Bonsai.Product.RegenerateProfileUsage",
        product.regenerate_profile_usage,
    )

    ifcopenshell.api.add_post_listener(
        "material.edit_layer", "Bonsai.DumbWall.RegenerateFromLayer", wall.DumbWallPlaner().regenerate_from_layer
    )
    ifcopenshell.api.add_post_listener(
        "type.assign_type", "Bonsai.DumbWall.RegenerateFromType", wall.DumbWallPlaner().regenerate_from_type
    )

    ifcopenshell.api.add_post_listener(
        "material.edit_layer", "Bonsai.DumbSlab.RegenerateFromLayer", slab.DumbSlabPlaner().regenerate_from_layer
    )
    ifcopenshell.api.add_post_listener(
        "type.assign_type", "Bonsai.DumbSlab.RegenerateFromType", slab.DumbSlabPlaner().regenerate_from_type
    )

    ifcopenshell.api.add_post_listener(
        "material.edit_profile",
        "Bonsai.DumbProfile.RegenerateFromProfile",
        profile.DumbProfileRegenerator().regenerate_from_profile,
    )
    ifcopenshell.api.add_post_listener(
        "type.assign_type",
        "Bonsai.DumbProfile.RegenerateFromType",
        profile.DumbProfileRegenerator().regenerate_from_type,
    )

    ifcopenshell.api.add_post_listener(
        "type.assign_type",
        "Bonsai.Opening.RegenerateFromType",
        opening.FilledOpeningGenerator().regenerate_from_type,
    )
