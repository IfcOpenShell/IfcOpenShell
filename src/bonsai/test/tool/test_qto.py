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

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.context
import ifcopenshell.api.cost
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.pset

import bonsai.bim.import_ifc as import_ifc
import bonsai.bim.module.qto.calculator as calculator
import bonsai.core.root
import bonsai.core.tool
import bonsai.tool as tool
import test.bim.bootstrap
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
        props = tool.Qto.get_qto_props()
        assert props.qto_result == "123.457"


class TestGetRoundedValue(test.bim.bootstrap.NewFile):
    def test_run(self):
        quantity = 1.2345
        assert subject.get_rounded_value(quantity) == 1.234


class TestGetCalculatedObjectQuantities(test.bim.bootstrap.NewFile):
    def setup_file(self):
        import logging

        self.ifc = ifcopenshell.file()
        tool.Ifc.set(self.ifc)
        ifcopenshell.api.root.create_entity(self.ifc, ifc_class="IfcProject", name="My Project")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(
            bpy.context, tool.Ifc.get_path(), logging.getLogger("ImportIFC")
        )
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.ifc
        ifc_importer.create_project()

    def setup_units(self, units):
        ifcopenshell.api.unit.assign_unit(self.ifc, **units)

    def calculate_quantities(self, obj):
        import ifc5d.qto

        context = ifcopenshell.api.context.add_context(self.ifc, context_type="Model")
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


class TestGetGrossSideAreaWithoutOpeningRelationship(test.bim.bootstrap.NewFile):
    """Regression tests for #9235.

    An opening can be baked directly into the body tessellation (e.g. an
    IfcIndexedPolygonalFaceWithVoids) instead of being modelled as an
    IfcOpeningElement related via IfcRelVoidsElement. has_openings() only
    sees the relationship, so it is blind to this case.
    """

    def setup_file(self):
        import logging

        self.ifc = ifcopenshell.file()
        tool.Ifc.set(self.ifc)
        ifcopenshell.api.root.create_entity(self.ifc, ifc_class="IfcProject", name="My Project")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(
            bpy.context, tool.Ifc.get_path(), logging.getLogger("ImportIFC")
        )
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.ifc
        ifc_importer.create_project()
        ifcopenshell.api.unit.assign_unit(
            self.ifc,
            length={"is_metric": True, "raw": "METERS"},
            area={"is_metric": True, "raw": "SQUARE_METERS"},
            volume={"is_metric": True, "raw": "CUBIC_METERS"},
        )

    def make_wall(self, mesh: bpy.types.Mesh) -> bpy.types.Object:
        context = ifcopenshell.api.context.add_context(self.ifc, context_type="Model")
        obj = bpy.data.objects.new("Wall", mesh)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcWall",
            predefined_type="NOTDEFINED",
            context=context,
        )
        return obj

    def build_wall_with_baked_hole(
        self,
        length: float,
        height: float,
        thickness: float,
        hole_size: float,
        main_axis: str = "x",
    ) -> bpy.types.Mesh:
        """A rectangular wall with a square hole cut straight into the mesh.

        No IfcOpeningElement is involved: the hole is a topological gap in
        the body geometry itself, like an opening baked into an
        IfcIndexedPolygonalFaceWithVoids.

        :param main_axis: which local axis the wall runs along ("x" or "y").
            The thickness always runs along the other horizontal axis, and
            height is always along Z. #9237 was Bonsai only handling "x".
        """
        cx, cz = length / 2, height / 2
        outer = [(0, 0), (length, 0), (length, height), (0, height)]
        h = hole_size / 2
        inner = [(cx - h, cz - h), (cx + h, cz - h), (cx + h, cz + h), (cx - h, cz + h)]

        def point(along_main: float, along_thickness: float, z: float) -> tuple[float, float, float]:
            return (along_main, along_thickness, z) if main_axis == "x" else (along_thickness, along_main, z)

        mesh = bpy.data.meshes.new("WallWithBakedHole")
        bm = bmesh.new()

        def make_ring(thickness_pos: float):
            outer_v = [bm.verts.new(point(x, thickness_pos, z)) for x, z in outer]
            inner_v = [bm.verts.new(point(x, thickness_pos, z)) for x, z in inner]
            return outer_v, inner_v

        outer_front, inner_front = make_ring(0.0)
        outer_back, inner_back = make_ring(thickness)
        bm.verts.ensure_lookup_table()

        n = 4
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([outer_front[i], outer_front[j], inner_front[j], inner_front[i]])
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([outer_back[j], outer_back[i], inner_back[i], inner_back[j]])
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([outer_front[i], outer_front[j], outer_back[j], outer_back[i]])
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([inner_front[j], inner_front[i], inner_back[i], inner_back[j]])

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        bm.free()
        return mesh

    def build_gable_wall(
        self, length: float, eave_height: float, ridge_height: float, thickness: float
    ) -> bpy.types.Mesh:
        """A gable-shaped wall (pentagon profile), no openings at all.

        Its bounding box is taller than the wall itself, so a fallback that
        substitutes the bounding box for GrossSideArea would overstate it.
        """
        profile = [
            (0.0, 0.0),
            (length, 0.0),
            (length, eave_height),
            (length / 2, ridge_height),
            (0.0, eave_height),
        ]

        mesh = bpy.data.meshes.new("GableWall")
        bm = bmesh.new()
        verts_front = [bm.verts.new((x, 0.0, z)) for x, z in profile]
        verts_back = [bm.verts.new((x, thickness, z)) for x, z in profile]
        bm.verts.ensure_lookup_table()

        bm.faces.new(verts_front[::-1])
        bm.faces.new(verts_back)
        n = len(profile)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([verts_front[i], verts_front[j], verts_back[j], verts_back[i]])

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        bm.free()
        return mesh

    def test_baked_opening_is_recovered(self):
        self.setup_file()
        length, height, thickness, hole = 4.0, 3.0, 0.2, 1.0
        obj = self.make_wall(self.build_wall_with_baked_hole(length, height, thickness, hole))

        assert calculator.has_openings(obj) == []
        assert round(calculator.get_net_side_area(obj), 3) == round(length * height - hole * hole, 3)
        assert round(calculator.get_gross_side_area(obj), 3) == round(length * height, 3)

    def test_y_oriented_wall_baked_opening_is_recovered(self):
        """Regression test for #9237.

        A wall whose length runs along local Y (thickness along X) used to
        report its end face instead of its elevation face, because
        get_net_side_area/get_gross_side_area hardcoded main_axis="x".
        """
        self.setup_file()
        length, height, thickness, hole = 4.0, 3.0, 0.2, 1.0
        obj = self.make_wall(self.build_wall_with_baked_hole(length, height, thickness, hole, main_axis="y"))

        assert calculator.get_x(obj) < calculator.get_y(obj)
        assert calculator.has_openings(obj) == []
        assert round(calculator.get_net_side_area(obj), 3) == round(length * height - hole * hole, 3)
        assert round(calculator.get_gross_side_area(obj), 3) == round(length * height, 3)

    def test_x_and_y_oriented_walls_agree(self):
        """The same wall, modelled with its length along local X or local Y,
        must report the same NetSideArea and GrossSideArea (#9237)."""
        self.setup_file()
        length, height, thickness, hole = 4.0, 3.0, 0.2, 1.0
        obj_x = self.make_wall(self.build_wall_with_baked_hole(length, height, thickness, hole, main_axis="x"))
        obj_y = self.make_wall(self.build_wall_with_baked_hole(length, height, thickness, hole, main_axis="y"))

        assert round(calculator.get_net_side_area(obj_x), 3) == round(calculator.get_net_side_area(obj_y), 3)
        assert round(calculator.get_gross_side_area(obj_x), 3) == round(calculator.get_gross_side_area(obj_y), 3)

    def test_non_rectangular_wall_without_openings_is_not_overstated(self):
        self.setup_file()
        length, eave_height, ridge_height, thickness = 6.0, 2.0, 4.0, 0.3
        obj = self.make_wall(self.build_gable_wall(length, eave_height, ridge_height, thickness))

        true_area = length * eave_height + 0.5 * length * (ridge_height - eave_height)
        bbox_area = calculator.get_side_area(obj)  # what a bounding-box fallback would return

        assert calculator.has_openings(obj) == []
        assert round(calculator.get_net_side_area(obj), 3) == round(true_area, 3)
        assert round(calculator.get_gross_side_area(obj), 3) == round(true_area, 3)
        assert bbox_area > true_area + 1  # the bounding box would have overstated this wall


class TestGetBaseQto(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall()
        wall_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        tool.Ifc.link(wall, wall_obj)
        product = tool.Ifc.get_entity(wall_obj)
        pset_qto = ifcopenshell.api.pset.add_qto(ifc, product=wall, name="Qto_Basefoo")
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
        schedule = ifcopenshell.api.cost.add_cost_schedule(ifc)
        item = ifcopenshell.api.cost.add_cost_item(ifc, cost_schedule=schedule)
        ifcopenshell.api.cost.edit_cost_item(ifc, cost_item=item, attributes={"Name": "Foo"})
        qto = ifcopenshell.api.pset.add_qto(ifc, product=wall, name="Qto_WallBaseQuantities")
        ifcopenshell.api.pset.edit_qto(ifc, qto=qto, properties={"NetVolume": 42.0})
        ifcopenshell.api.cost.assign_cost_item_quantity(ifc, cost_item=item, products=[wall], prop_name="NetVolume")
        assert subject.get_related_cost_item_quantities(wall)[0]["cost_item_name"] == "Foo"
        assert subject.get_related_cost_item_quantities(wall)[0]["quantity_name"] == "NetVolume"
        assert subject.get_related_cost_item_quantities(wall)[0]["quantity_value"] == 42
        assert subject.get_related_cost_item_quantities(wall)[0]["quantity_type"] == "IfcQuantityVolume"
