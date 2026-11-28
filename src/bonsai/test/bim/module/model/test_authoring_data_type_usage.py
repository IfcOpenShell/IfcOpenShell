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

"""Regression test for #6967 ("Generate walls from slab perimeter
button/icon/feature missing").

``EditObjectUI.draw_operations`` in ``bim/module/model/workspace.py`` draws
the "Add From Perimeter" button (slab selected, a LAYER2 wall type picked)
and the "Add From Closed Loop" button (walls selected, a LAYER3 slab type
picked) by reading ``AuthoringData.data["relating_type_data"].get("usage")``.

Commit b49cc6c5e9 ("AuthoringData.data['relating_type_data']") collapsed
several separate ``AuthoringData`` fields -- including
``relating_type_material_usage`` -- into that one dict, built by
``get_type_data()``, but never carried the usage value across. The two
``.get("usage")`` reads in workspace.py were left unchanged, so they always
read ``None`` and both buttons silently disappeared, even though the
underlying operators (``bim.draw_walls_from_slab`` / ``bim.draw_slab_from_wall``)
still work fine via the Shift+A hotkey. The feature was never removed, only
its icon."""

import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.root
import pytest

pytestmark = pytest.mark.model


def _make_layered_type(f: ifcopenshell.file, ifc_class: str, name: str) -> ifcopenshell.entity_instance:
    element_type = ifcopenshell.api.root.create_entity(f, ifc_class=ifc_class, name=name)
    material = ifcopenshell.api.material.add_material(f, name="Concrete")
    material_set = ifcopenshell.api.material.add_material_set(f, set_type="IfcMaterialLayerSet")
    ifcopenshell.api.material.add_layer(f, layer_set=material_set, material=material)
    ifcopenshell.api.material.assign_material(
        f, products=[element_type], type="IfcMaterialLayerSet", material=material_set
    )
    return element_type


def test_get_type_data_reports_usage_for_wall_type():
    from bonsai.bim.module.model.data import AuthoringData

    f = ifcopenshell.file(schema="IFC4")
    wall_type = _make_layered_type(f, "IfcWallType", "TestWallType")

    data = AuthoringData.get_type_data(wall_type)

    assert data.get("usage") == "LAYER2", (
        "relating_type_data must carry 'usage', or the Add From Perimeter "
        "button in workspace.py's LAYER3 branch never draws"
    )


def test_get_type_data_reports_usage_for_slab_type():
    from bonsai.bim.module.model.data import AuthoringData

    f = ifcopenshell.file(schema="IFC4")
    slab_type = _make_layered_type(f, "IfcSlabType", "TestSlabType")

    data = AuthoringData.get_type_data(slab_type)

    assert data.get("usage") == "LAYER3", (
        "relating_type_data must carry 'usage', or the Add From Closed Loop "
        "button in workspace.py's LAYER2 branch never draws"
    )
