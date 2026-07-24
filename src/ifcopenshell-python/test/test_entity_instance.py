# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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


import test.bootstrap


class TestGetInfo2(test.bootstrap.IFC4):
    def test_instance_attribute(self):
        brep = self.file.create_entity("IfcFacetedBrep")
        shell = self.file.create_entity("IfcClosedShell")
        brep.Outer = shell
        assert brep.get_info_2(recursive=True) == {
            "Outer": {"CfsFaces": None, "id": 2, "type": "IfcClosedShell"},
            "id": 1,
            "type": "IfcFacetedBrep",
        }

    def test_aggregate_of_instance_attribute(self):
        shell = self.file.create_entity("IfcClosedShell")
        faces = [self.file.create_entity("IfcFace") for i in range(3)]
        shell.CfsFaces = faces
        assert shell.get_info_2(recursive=True)["CfsFaces"] == (
            {"Bounds": None, "id": 2, "type": "IfcFace"},
            {"Bounds": None, "id": 3, "type": "IfcFace"},
            {"Bounds": None, "id": 4, "type": "IfcFace"},
        )

    def test_aggregate_of_aggregate_of_instance_attribute(self):
        surface = self.file.create_entity("IfcBSplineSurfaceWithKnots")
        pp = [self.file.create_entity("IfcCartesianPoint", [float(i)]) for i in range(4)]
        surface.ControlPointsList = [pp[:2], pp[2:]]
        assert surface.get_info_2(recursive=True)["ControlPointsList"] == (
            (
                {"Coordinates": (0.0,), "id": 2, "type": "IfcCartesianPoint"},
                {"Coordinates": (1.0,), "id": 3, "type": "IfcCartesianPoint"},
            ),
            (
                {"Coordinates": (2.0,), "id": 4, "type": "IfcCartesianPoint"},
                {"Coordinates": (3.0,), "id": 5, "type": "IfcCartesianPoint"},
            ),
        )

    def test_exclude_identifier(self):
        brep = self.file.create_entity("IfcFacetedBrep")
        shell = self.file.create_entity("IfcClosedShell")
        brep.Outer = shell
        assert brep.get_info_2(recursive=True, include_identifier=False) == {
            "Outer": {"CfsFaces": None, "type": "IfcClosedShell"},
            "type": "IfcFacetedBrep",
        }

    def test_unsupported_arguments_fall_back_to_get_info(self):
        # Regression test for #4270: get_info_2 raised a bare AssertionError
        # when called with its own default arguments (recursive=False) or any
        # other combination the C++ fast path does not implement. It must
        # delegate to get_info instead of crashing.
        brep = self.file.create_entity("IfcFacetedBrep")
        shell = self.file.create_entity("IfcClosedShell")
        brep.Outer = shell
        assert brep.get_info_2() == brep.get_info()
        assert brep.get_info_2(recursive=True, ignore=("Outer",)) == brep.get_info(recursive=True, ignore=("Outer",))


class TestIsA(test.bootstrap.IFC4):
    def test_regular_entity_names_are_unaffected(self):
        wall = self.file.create_entity("IfcWall")
        assert wall.is_a("IfcWall")
        assert wall.is_a("ifcwall")
        assert wall.is_a("IfcElement")
        assert not wall.is_a("IfcSlab")
        assert wall.is_a() == "IfcWall"
        assert wall.is_a(True) == "IFC4.IfcWall"

    def test_unknown_class_name_returns_false(self):
        wall = self.file.create_entity("IfcWall")
        assert wall.is_a("NotARealClass") is False

    def test_select_type(self):
        # IfcDefinitionSelect = IfcObjectDefinition | IfcPropertyDefinition (#6063).
        window_type = self.file.create_entity("IfcWindowType")
        assert window_type.is_a("IfcObjectDefinition")
        assert window_type.is_a("IfcDefinitionSelect")
        assert window_type.is_a("ifcdefinitionselect")

        person = self.file.create_entity("IfcPerson")
        assert not person.is_a("IfcDefinitionSelect")

    def test_nested_select_type(self):
        # IfcFillStyleSelect = IfcColour | ... and IfcColour = IfcColourSpecification | IfcPreDefinedColour,
        # so resolving IfcFillStyleSelect must recurse through the nested IfcColour select.
        colour = self.file.create_entity("IfcColourRgb", Red=0.1, Green=0.2, Blue=0.3)
        assert colour.is_a("IfcColour")
        assert colour.is_a("IfcFillStyleSelect")

        wall = self.file.create_entity("IfcWall")
        assert not wall.is_a("IfcFillStyleSelect")

    def test_select_type_with_defined_type_members(self):
        # IfcValue is a SELECT composed entirely of defined/enumeration types (no
        # ENTITY members), reachable by recursing through IfcMeasureValue,
        # IfcSimpleValue, and IfcDerivedMeasureValue. Unlike by_type(), is_a() can
        # test such non-entity instances directly, since it only needs to inspect
        # the instance's own declared type rather than retrieve it from an index.
        length = self.file.createIfcLengthMeasure(3.0)
        assert length.is_a("IfcLengthMeasure")
        assert length.is_a("IfcMeasureValue")
        assert length.is_a("IfcValue")

        wall = self.file.create_entity("IfcWall")
        assert not wall.is_a("IfcValue")

    def test_mixed_select_type(self):
        # IfcTrimmingSelect = IfcCartesianPoint (entity) | IfcParameterValue (defined type).
        # is_a() resolves both kinds of member consistently.
        point = self.file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0))
        param = self.file.createIfcParameterValue(0.5)
        assert point.is_a("IfcTrimmingSelect")
        assert param.is_a("IfcTrimmingSelect")

        wall = self.file.create_entity("IfcWall")
        assert not wall.is_a("IfcTrimmingSelect")
