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
import ifcopenshell.api
import ifcopenshell.util.pset
import test.bim.bootstrap
import bonsai.core.tool
import bonsai.core.root
import bonsai.tool as tool
import bonsai.bim.import_ifc as import_ifc
from bonsai.tool.qto import Qto as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Qto)


class TestGetRadiusOfSelectedVertices(test.bim.bootstrap.NewFile):
    def test_run(self):
        bpy.ops.mesh.primitive_circle_add()
        assert round(subject.get_radius_of_selected_vertices(bpy.data.objects.get("Circle")), 3) == 1


class TestSetQtoResult(test.bim.bootstrap.NewFile):
    def test_run(self):
        subject.set_qto_result(123.4567)
        assert bpy.context.scene.BIMQtoProperties.qto_result == "123.457"


class TestGetRoundedValue(test.bim.bootstrap.NewFile):
    def test_run(self):
        quantity = 1.2345
        assert subject.get_rounded_value(quantity) == 1.234


class TestGetCalculatedObjectQuantities(test.bim.bootstrap.NewFile):
    def setup_file(self):
        import logging

        self.ifc = ifcopenshell.file()
        tool.Ifc.set(self.ifc)
        ifcopenshell.api.run("root.create_entity", self.ifc, ifc_class="IfcProject", name="My Project")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(
            bpy.context, tool.Ifc.get_path(), logging.getLogger("ImportIFC")
        )
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.ifc
        ifc_importer.create_project()

    def setup_units(self, units):
        ifcopenshell.api.run("unit.assign_unit", self.ifc, **units)

    def calculate_quantities(self, obj):
        import ifc5d.qto

        context = ifcopenshell.api.run("context.add_context", self.ifc, context_type="Model")
        bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0), size=2)
        obj = bpy.context.active_object
        element = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcWall",
            predefined_type="ELEMENTEDWALL",
            context=context,
        )

        rules = {
            "calculators": {
                "Blender": {
                    "IfcWall": {
                        "Qto_WallBaseQuantities": {
                            "GrossFootprintArea": "get_gross_footprint_area",
                            "GrossSideArea": "get_gross_side_area",
                            "GrossVolume": "get_gross_volume",
                            "GrossWeight": "get_gross_weight",
                            "Height": "get_height",
                            "Length": "get_length",
                            "NetFootprintArea": "get_net_footprint_area",
                            "NetSideArea": "get_net_side_area",
                            "NetVolume": "get_net_volume",
                            "NetWeight": "get_net_weight",
                            "Width": "get_width",
                        }
                    },
                }
            }
        }

        ifc_file = tool.Ifc.get()
        results = ifc5d.qto.quantify(ifc_file, {element}, rules)
        return {k: round(v, 3) for k, v in results[element]["Qto_WallBaseQuantities"].items() if v is not None}

    def test_meters_project_unit(self):
        self.setup_file()
        self.setup_units(
            {
                "length": {"is_metric": True, "raw": "METERS"},
                "area": {"is_metric": True, "raw": "SQUARE_METERS"},
                "volume": {"is_metric": True, "raw": "CUBIC_METERS"},
            }
        )
        quantities = self.calculate_quantities(bpy.context.active_object)

        assert quantities["Length"] == 2
        assert quantities["Width"] == 2
        assert quantities["Height"] == 2
        assert quantities["GrossFootprintArea"] == 4
        assert quantities["NetFootprintArea"] == 4
        assert quantities["GrossSideArea"] == 4
        assert quantities["NetSideArea"] == 4
        assert quantities["GrossVolume"] == 8
        assert quantities["NetVolume"] == 8

    def test_prefix_project_unit(self):
        self.setup_file()
        self.setup_units(
            {
                "length": {"is_metric": True, "raw": "MILLIMETERS"},
                "area": {"is_metric": True, "raw": "SQUARE_MILLIMETERS"},
                "volume": {"is_metric": True, "raw": "CUBIC_MILLIMETERS"},
            }
        )
        quantities = self.calculate_quantities(bpy.context.active_object)

        assert quantities["Length"] == 2e3
        assert quantities["Width"] == 2e3
        assert quantities["Height"] == 2e3
        assert quantities["GrossFootprintArea"] == 4e6
        assert quantities["NetFootprintArea"] == 4e6
        assert quantities["GrossSideArea"] == 4e6
        assert quantities["NetSideArea"] == 4e6
        assert quantities["GrossVolume"] == 8e9
        assert quantities["NetVolume"] == 8e9

    def test_imperial_project_unit(self):
        self.setup_file()
        self.setup_units(
            {
                "length": {"is_metric": False, "raw": "FEET"},
                "area": {"is_metric": False, "raw": "FEET"},
                "volume": {"is_metric": False, "raw": "FEET"},
            }
        )
        quantities = self.calculate_quantities(bpy.context.active_object)

        assert quantities["Length"] == 6.562
        assert quantities["Width"] == 6.562
        assert quantities["Height"] == 6.562
        assert quantities["GrossFootprintArea"] == 43.056
        assert quantities["NetFootprintArea"] == 43.056
        assert quantities["GrossSideArea"] == 43.056
        assert quantities["NetSideArea"] == 43.056
        assert quantities["GrossVolume"] == 282.517
        assert quantities["NetVolume"] == 282.517


class TestGetBaseQto(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        wall_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        tool.Ifc.link(wall, wall_obj)
        product = tool.Ifc.get_entity(wall_obj)
        pset_qto = ifcopenshell.api.run("pset.add_qto", ifc, product=wall, name="Qto_Basefoo")
        assert subject.get_base_qto(product).id() == pset_qto.get_info()["id"]
        assert subject.get_base_qto(product).Name == pset_qto.Name

    def test_no_quantities(self):
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
        ifcopenshell.api.run(
            "cost.assign_cost_item_quantity", ifc, cost_item=item, products=[wall], prop_name="NetVolume"
        )
        assert subject.get_related_cost_item_quantities(wall)[0]["cost_item_name"] == "Foo"
        assert subject.get_related_cost_item_quantities(wall)[0]["quantity_name"] == "NetVolume"
        assert subject.get_related_cost_item_quantities(wall)[0]["quantity_value"] == 42
        assert subject.get_related_cost_item_quantities(wall)[0]["quantity_type"] == "IfcQuantityVolume"
