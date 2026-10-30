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


import ast

import ifcopenshell.util.scripts.validate_stub as subject


class TestValidateStub:
    def test_resolve_property_wrapping_an_underscore_prefixed_function(self):
        tree = ast.parse(
            "class Geom:\n"
            "    def _geometry_getter(self):\n"
            "        return 1\n"
            "    geometry = property(_geometry_getter)\n"
        )
        assert subject.get_names_tree(tree) == {"class Geom:": {("@property", "def geometry(self): ...")}}

    def test_resolve_staticmethod_wrapping_an_underscore_prefixed_function(self):
        tree = ast.parse("class Geom:\n    def _make(a, b):\n        return a\n    make = staticmethod(_make)\n")
        assert subject.get_names_tree(tree) == {"class Geom:": {("@staticmethod", "def make(a, b): ...")}}

    def test_resolve_property_getter_and_setter_with_underscore_prefix(self):
        tree = ast.parse(
            "class Geom:\n"
            "    def _get(self):\n"
            "        return 1\n"
            "    def _set(self, value):\n"
            "        pass\n"
            "    value = property(_get, _set)\n"
        )
        assert subject.get_names_tree(tree) == {"class Geom:": {"value"}}

    def test_run(self):
        subject.main()
