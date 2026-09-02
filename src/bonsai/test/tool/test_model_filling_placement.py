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

"""Where a door or window lands when it is dropped into an imported wall.

``get_wall_axis`` reads the wall run off ``bound_box`` min_x/max_x, so every
caller that positions a filling from it assumes the wall's placement X is the
wall reference line. Only an IfcMaterialLayerSetUsage makes that true. Across
a corpus of real models, hosts carrying a plain IfcMaterial, an
IfcMaterialConstituentSet or a bare IfcMaterialLayerSet produced doors rotated
by exactly the angle between the placement X and the wall run: 89.11, 84.74,
43.87, 21.44, 14.32 degrees. ``has_layer2_reference_line`` is the gate that
sends those hosts down the geometry-derived path instead."""

import ifcopenshell
import pytest

pytestmark = pytest.mark.model


def _wall_with_material(schema, material_builder):
    ifc = ifcopenshell.file(schema=schema)
    wall = ifc.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new())
    material = material_builder(ifc)
    if material is not None:
        ifc.create_entity(
            "IfcRelAssociatesMaterial",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[wall],
            RelatingMaterial=material,
        )
    return ifc, wall


def _layer_set(ifc, thickness):
    material = ifc.create_entity("IfcMaterial", Name="Concrete")
    layer = ifc.create_entity("IfcMaterialLayer", Material=material, LayerThickness=thickness)
    return ifc.create_entity("IfcMaterialLayerSet", MaterialLayers=[layer], LayerSetName="Wall")


def test_layer_set_usage_keeps_the_reference_line_path():
    from bonsai import tool

    def build(ifc):
        return ifc.create_entity(
            "IfcMaterialLayerSetUsage",
            ForLayerSet=_layer_set(ifc, 0.2),
            LayerSetDirection="AXIS2",
            DirectionSense="POSITIVE",
            OffsetFromReferenceLine=0.0,
        )

    _ifc, wall = _wall_with_material("IFC4", build)
    assert tool.Model.has_layer2_reference_line(wall) is True


def test_plain_material_has_no_reference_line():
    from bonsai import tool

    _ifc, wall = _wall_with_material("IFC4", lambda ifc: ifc.create_entity("IfcMaterial", Name="Concrete"))
    assert tool.Model.has_layer2_reference_line(wall) is False


def test_layer_set_without_usage_has_no_reference_line():
    from bonsai import tool

    _ifc, wall = _wall_with_material("IFC4", lambda ifc: _layer_set(ifc, 0.2))
    assert tool.Model.has_layer2_reference_line(wall) is False


def test_no_material_has_no_reference_line():
    from bonsai import tool

    _ifc, wall = _wall_with_material("IFC4", lambda ifc: None)
    assert tool.Model.has_layer2_reference_line(wall) is False


def test_axis3_usage_is_not_a_wall_reference_line():
    from bonsai import tool

    def build(ifc):
        return ifc.create_entity(
            "IfcMaterialLayerSetUsage",
            ForLayerSet=_layer_set(ifc, 0.2),
            LayerSetDirection="AXIS3",
            DirectionSense="POSITIVE",
            OffsetFromReferenceLine=0.0,
        )

    _ifc, wall = _wall_with_material("IFC4", build)
    assert tool.Model.has_layer2_reference_line(wall) is False


def test_zero_thickness_layer_set_has_no_usable_reference_line():
    from bonsai import tool

    def build(ifc):
        return ifc.create_entity(
            "IfcMaterialLayerSetUsage",
            ForLayerSet=_layer_set(ifc, 0.0),
            LayerSetDirection="AXIS2",
            DirectionSense="POSITIVE",
            OffsetFromReferenceLine=0.0,
        )

    _ifc, wall = _wall_with_material("IFC4", build)
    assert tool.Model.has_layer2_reference_line(wall) is False


def test_filling_rotation_puts_local_y_into_the_wall_and_z_up():
    from mathutils import Vector

    from bonsai import tool

    inward = Vector((0.0, 1.0, 0.0))
    matrix = tool.Model.get_filling_rotation(inward)
    assert (matrix.to_3x3() @ Vector((0.0, 1.0, 0.0)) - inward).length < 1e-6
    assert (matrix.to_3x3() @ Vector((0.0, 0.0, 1.0)) - Vector((0.0, 0.0, 1.0))).length < 1e-6
    assert matrix.to_3x3().determinant() == pytest.approx(1.0)


def test_filling_rotation_follows_a_skewed_wall_face():
    import math

    from mathutils import Vector

    from bonsai import tool

    inward = Vector((math.cos(math.radians(37.0)), math.sin(math.radians(37.0)), 0.0))
    matrix = tool.Model.get_filling_rotation(inward)
    local_x = matrix.to_3x3() @ Vector((1.0, 0.0, 0.0))
    assert abs(local_x.dot(inward)) < 1e-6
    assert abs(local_x.z) < 1e-6
