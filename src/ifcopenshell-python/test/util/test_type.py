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

import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.type as subject


class TestGetApplicableTypes(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.get_applicable_types("IfcWall") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcWallStandardCase") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcFlowSegment") == ["IfcDistributionElementType"]
        assert subject.get_applicable_types("IfcDuctSegment") == ["IfcDuctSegmentType"]
        assert subject.get_applicable_types("IfcTask") == []


class TestGetApplicableTypesIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        assert subject.get_applicable_types("IfcWall", schema="IFC2X3") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcWallStandardCase", schema="IFC2X3") == ["IfcWallType"]
        assert subject.get_applicable_types("IfcBuildingElementProxy", schema="IFC2X3") == [
            "IfcBuildingElementProxyType"
        ]


class TestGetApplicableEntities(test.bootstrap.IFC4):
    def test_run(self):
        assert set(subject.get_applicable_entities("IfcWallType")) == {
            "IfcWall",
            "IfcWallElementedCase",
            "IfcWallStandardCase",
        }


class TestGetApplicableEntitiesIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        assert set(subject.get_applicable_entities("IfcWallType", schema="IFC2X3")) == {
            "IfcWall",
            "IfcWallStandardCase",
        }
        assert subject.get_applicable_entities("IfcBuildingElementProxyType", schema="IFC2X3") == [
            "IfcBuildingElementProxy"
        ]
