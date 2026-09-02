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

import pytest

import ifcopenshell


def fail_lookup(*args, **kwargs):
    raise RuntimeError("No schema named IFC4")


class TestSchemaByName:
    def test_schema_by_name(self):
        assert ifcopenshell.schema_by_name("IFC4").name() == "IFC4"

    def test_unknown_schema_keeps_the_original_error(self):
        with pytest.raises(RuntimeError) as excinfo:
            ifcopenshell.schema_by_name("IFC9")
        assert not isinstance(excinfo.value, ifcopenshell.SchemaError)

    def test_missing_schema_plugins_are_explained(self, monkeypatch):
        monkeypatch.setattr(ifcopenshell.ifcopenshell_wrapper, "schema_by_name", fail_lookup)
        monkeypatch.setattr(ifcopenshell.ifcopenshell_wrapper, "schema_names", lambda: ("HEADER_SECTION_SCHEMA",))
        with pytest.raises(ifcopenshell.SchemaError) as excinfo:
            ifcopenshell.schema_by_name("IFC4")
        message = str(excinfo.value)
        assert "No schema named IFC4" in message
        assert "incomplete or half updated" in message
        assert "ifcopenshell_parse_schema_ifc4" in message

    def test_a_registered_schema_is_not_reported_as_a_broken_install(self, monkeypatch):
        monkeypatch.setattr(ifcopenshell.ifcopenshell_wrapper, "schema_by_name", fail_lookup)
        with pytest.raises(RuntimeError) as excinfo:
            ifcopenshell.schema_by_name("IFC4")
        assert not isinstance(excinfo.value, ifcopenshell.SchemaError)
