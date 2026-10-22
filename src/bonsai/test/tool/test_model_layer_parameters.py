# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.type

import bonsai.tool as tool
from bonsai.tool.model import Model as subject
from test.bim.bootstrap import NewFile


class TestGetMaterialLayerParameters(NewFile):
    """https://github.com/IfcOpenShell/IfcOpenShell/issues/5611 : a host with
    no material (eg. a parametric IfcRoof, which never gets an
    IfcMaterialLayerSetUsage) used to silently default to AXIS2, the
    wall convention, so windows/skylights added to it never rotated or cut
    an opening. The default should follow the host's class instead, the
    same way ``get_usage_type`` already infers AXIS3 vs AXIS2."""

    def test_roof_with_no_material_defaults_to_axis3(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        roof = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcRoof")
        assert subject.get_material_layer_parameters(roof)["layer_set_direction"] == "AXIS3"

    def test_slab_with_no_material_defaults_to_axis3(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        slab = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        assert subject.get_material_layer_parameters(slab)["layer_set_direction"] == "AXIS3"

    def test_wall_with_no_material_defaults_to_axis2(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        assert subject.get_material_layer_parameters(wall)["layer_set_direction"] == "AXIS2"

    def test_unrelated_class_with_no_material_defaults_to_axis2(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        proxy = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuildingElementProxy")
        assert subject.get_material_layer_parameters(proxy)["layer_set_direction"] == "AXIS2"

    def test_explicit_layer_set_usage_still_wins_over_class_default(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType", name="WAL01")
        material_set = ifcopenshell.api.material.add_material_set(ifc, set_type="IfcMaterialLayerSet")
        material = ifcopenshell.api.material.add_material(ifc, name="PB01", category="gypsum")
        layer = ifcopenshell.api.material.add_layer(ifc, layer_set=material_set, material=material)
        ifcopenshell.api.material.edit_layer(ifc, layer=layer, attributes={"LayerThickness": 100})
        ifcopenshell.api.material.assign_material(ifc, products=[wall_type], material=material_set)

        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
        rel = ifcopenshell.api.material.assign_material(ifc, products=[wall], type="IfcMaterialLayerSetUsage")
        rel.RelatingMaterial.LayerSetDirection = "AXIS3"
        assert subject.get_material_layer_parameters(wall)["layer_set_direction"] == "AXIS3"
