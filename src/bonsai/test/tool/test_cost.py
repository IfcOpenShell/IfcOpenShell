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


import bpy
import ifcopenshell
import ifcopenshell.api.cost
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit

import bonsai.core.tool
import bonsai.tool as tool
import test.bim.bootstrap
from bonsai.tool.cost import Cost as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Cost)


class TestDisableEditingCostItemParent(NewFile):
    def test_avoid_recursion_error(newfile, monkeypatch):
        class DummyProps:
            def __init__(self):
                self.change_cost_item_parent = None
                self.active_cost_item_id = 5

        props = DummyProps()
        monkeypatch.setattr("bonsai.tool.Cost.get_cost_props", lambda: props)
        subject.disable_editing_cost_item_parent()
        assert props.active_cost_item_id == 0
        assert props.change_cost_item_parent is not False


class TestLoadProductCostItems(NewFile):
    def test_a_legitimate_zero_quantity_is_not_shown_as_one(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name="My Project")
        ifcopenshell.api.unit.assign_unit(ifc)
        wall = ifc.createIfcWall()
        wall_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        tool.Ifc.link(wall, wall_obj)
        product = tool.Ifc.get_entity(wall_obj)

        schedule = ifcopenshell.api.cost.add_cost_schedule(ifc)
        item = ifcopenshell.api.cost.add_cost_item(ifc, cost_schedule=schedule)
        qto = ifcopenshell.api.pset.add_qto(ifc, product=wall, name="Qto_WallBaseQuantities")
        # A wall fully covered by openings can legitimately have a NetArea of 0.
        ifcopenshell.api.pset.edit_qto(ifc, qto=qto, properties={"NetArea": 0.0})
        ifcopenshell.api.cost.assign_cost_item_quantity(ifc, cost_item=item, products=[wall], prop_name="NetArea")

        subject.load_product_cost_items(product)
        assert tool.Cost.get_cost_props().product_cost_items[0].total_quantity == 0
