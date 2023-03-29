# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import test.bim.bootstrap
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.qto import Qto as subject
from blenderbim.bim.module.pset.qto_calculator import QtoCalculator


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Qto)

class TestGetRadiusOfSelectedVertices(test.bim.bootstrap.NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_circle_add()
        assert round(subject.get_radius_of_selected_vertices(bpy.data.objects.get("Circle")), 3) == 1

class TestSetQtoResult(test.bim.bootstrap.NewFile):
    def test_run(self):
        subject.set_qto_result(123.4567)
        assert bpy.context.scene.BIMQtoProperties.qto_result == "123.457"

class TestGetApplicableQuantityNames(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        schema = ifc.schema
        properties_templates = ifcopenshell.util.pset.PsetQto(schema).get_by_name('Qto_WallBaseQuantities').get_info()['HasPropertyTemplates']
        applicable_quantity_names = [a.Name for a in properties_templates]
        assert subject.get_applicable_quantity_names('Qto_WallBaseQuantities') == applicable_quantity_names

class TestGetApplicableBaseQuantityName(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        assert subject.get_applicable_base_quantity_name(wall) == "Qto_WallBaseQuantities"

    def test_no_base_quantity(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class = "IfcProject")
        product = ifc.by_type('IfcProject')[0]
        assert subject.get_applicable_base_quantity_name(product) == None

class TestGetRoundedValue(test.bim.bootstrap.NewFile):
    def test_run(self):
        quantity = 1.2345
        assert subject.get_rounded_value(quantity) == 1.234

class TestGetCalculatedObjectQuantities(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject", name="My Project")
        ifcopenshell.api.run("unit.assign_unit", ifc)
        context = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        bpy.ops.mesh.primitive_cube_add(location=(0.0,0.0,0.0), size = 2)
        obj = bpy.context.active_object
        element = blenderbim.core.root.assign_class(tool.Ifc,
                                                    tool.Collector,
                                                    tool.Root,
                                                    obj=obj,
                                                    ifc_class="IfcWall",
                                                    predefined_type = "ELEMENTEDWALL",
                                                    context = context)
        calculator = QtoCalculator()
        base_qto = ifcopenshell.api.run("pset.add_qto", ifc, product=element, name="Qto_WallBaseQuantities")
        quantities = subject.get_calculated_object_quantities(calculator = calculator, qto_name = "Qto_WallBaseQuantities", obj = obj)
        assert quantities["Length"] == 2
        assert quantities["Width"] == 2
        assert quantities["Height"] == 2
        assert quantities["GrossFootprintArea"] == 4
        assert quantities["NetFootprintArea"] == 4
        assert quantities["GrossSideArea"] == 4
        assert quantities["NetSideArea"] == 4
        assert quantities["GrossVolume"] == 8
        assert quantities["NetVolume"] == 8

class TestAddObjectBaseQto(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject", name="My Project")
        context = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        bpy.ops.mesh.primitive_cube_add(location=(0.0,0.0,0.0), size = 2)
        obj = bpy.context.active_object
        element = blenderbim.core.root.assign_class(tool.Ifc,
                                                    tool.Collector,
                                                    tool.Root,
                                                    obj=obj,
                                                    ifc_class="IfcWall",
                                                    predefined_type = "ELEMENTEDWALL",
                                                    context = context)
        assert subject.add_object_base_qto(obj).Name == "Qto_WallBaseQuantities"

class TestAddProductBaseQto(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        base_qto = subject.add_product_base_qto(wall)
        assert base_qto.Name == "Qto_WallBaseQuantities"

class TestGetBaseQto(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        wall_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        tool.Ifc.link(wall, wall_obj)
        product = tool.Ifc.get_entity(wall_obj)
        pset_qto = ifcopenshell.api.run("pset.add_qto", ifc, product=wall, name="Qto_Basefoo")
        assert subject.get_base_qto(product).id() == pset_qto.get_info()['id']
        assert subject.get_base_qto(product).Name == pset_qto.Name

    def test_isempty(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        wall_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        tool.Ifc.link(wall, wall_obj)
        product = tool.Ifc.get_entity(wall_obj)
        assert not subject.get_base_qto(product) == True

class TestGetRelatedCostItemQuantities(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        product = tool.Ifc.get_entity(wall)
        schedule = ifcopenshell.api.run("cost.add_cost_schedule", ifc)
        item = ifcopenshell.api.run("cost.add_cost_item", ifc, cost_schedule=schedule)
        ifcopenshell.api.run("cost.edit_cost_item", ifc, cost_item=item, attributes={"Name": "Foo"})
        qto = ifcopenshell.api.run("pset.add_qto", ifc, product=wall, name="Qto_WallBaseQuantities")
        ifcopenshell.api.run("pset.edit_qto", ifc, qto=qto, properties={"NetVolume": 42.0})
        ifcopenshell.api.run("cost.assign_cost_item_quantity", ifc, cost_item=item, products=[wall], prop_name="NetVolume")
        assert subject.get_related_cost_item_quantities(wall)[0]['cost_item_name'] == "Foo"
        assert subject.get_related_cost_item_quantities(wall)[0]['quantity_name'] == "NetVolume"
        assert subject.get_related_cost_item_quantities(wall)[0]['quantity_value'] == 42
        assert subject.get_related_cost_item_quantities(wall)[0]['quantity_type'] == "IfcQuantityVolume"
