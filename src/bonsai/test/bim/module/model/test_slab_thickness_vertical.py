# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from unittest.mock import Mock, patch

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.model.slab import DumbSlabPlaner


def test_change_thickness_leaves_a_vertical_slab_extrusion_alone():
    ifc = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
    model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    slab = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
    layer_set = ifcopenshell.api.material.add_material_set(ifc, name="Slab", set_type="IfcMaterialLayerSet")
    layer = ifcopenshell.api.material.add_layer(ifc, layer_set=layer_set, material=ifc.createIfcMaterial("Concrete"))
    layer.LayerThickness = 0.2
    ifcopenshell.api.material.assign_material(ifc, products=[slab], material=layer_set, type="IfcMaterialLayerSetUsage")
    representation = ifcopenshell.api.geometry.add_slab_representation(ifc, context=body, depth=0.2)
    ifcopenshell.api.geometry.assign_representation(ifc, product=slab, representation=representation)
    extrusion = representation.Items[0]
    extrusion.ExtrudedDirection.DirectionRatios = (0.0, 1.0, 0.0)

    with (
        patch.object(tool.Ifc, "get", return_value=ifc),
        patch.object(tool.Ifc, "get_object", return_value=Mock()),
        patch.object(tool.Model, "get_material_layer_custom_offset", return_value=None),
        patch("bonsai.bim.module.model.slab.bonsai.core.geometry.switch_representation"),
    ):
        DumbSlabPlaner().change_thickness(slab, 0.4)

    assert extrusion.Depth == 0.2
