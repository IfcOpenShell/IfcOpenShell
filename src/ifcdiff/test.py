# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcdiff
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.util.representation


def setup_project() -> ifcopenshell.file:
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")
    unit = ifcopenshell.api.run("unit.add_si_unit", ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
    ifcopenshell.api.run("unit.assign_unit", ifc_file, units=[unit])
    model = ifcopenshell.api.context.add_context(ifc_file, "Model")
    ifcopenshell.api.context.add_context(ifc_file, "Model", "Body", "MODEL_VIEW", parent=model)
    return ifc_file


class TestIfcDiff:
    def test_add_element(self):
        ifc_file = setup_project()

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall = ifcopenshell.api.root.create_entity(new_file, ifc_class="IfcWall")

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file)
        ifc_diff.diff()
        assert ifc_diff.added_elements == {wall.GlobalId}
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {}

    def test_remove_element(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        ifcopenshell.api.root.remove_product(new_file, wall_new)

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file)
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == {wall.GlobalId}
        assert ifc_diff.change_register == {}

    def test_changed_attribute(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")

        new_file = ifc_file.from_string(ifc_file.to_string())
        wall_new = new_file.by_id(wall.id())
        wall_new.Name = "Bar"

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["attributes"])
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {wall.GlobalId: {"attributes_changed": True}}

    def test_changed_geometry(self):
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Foo")
        context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        assert context
        representation = ifcopenshell.api.geometry.add_slab_representation(ifc_file, context, depth=0.2)
        ifcopenshell.api.geometry.assign_representation(ifc_file, wall, representation)

        new_file = ifc_file.from_string(ifc_file.to_string())
        extrusion = new_file.by_type("IfcExtrudedAreaSolid")[0]
        extrusion.Depth = 500.0

        ifc_diff = ifcdiff.IfcDiff(ifc_file, new_file, relationships=["geometry"])
        ifc_diff.diff()
        assert ifc_diff.added_elements == set()
        assert ifc_diff.deleted_elements == set()
        assert ifc_diff.change_register == {wall.GlobalId: {"geometry_changed": True}}
