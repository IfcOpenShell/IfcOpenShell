# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
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

# This file was generated with the assistance of an AI coding tool.

import os

import pytest

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.util.element

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
FILES = ["ColumnPSetsOfSets.ifc"]


@pytest.mark.parametrize("name", FILES)
def test_lazy_open_matches_full_parse(name):
    ifcopenshell.get_log()  # the log buffer is global: drop what earlier modules logged
    strict = ifcopenshell.open(os.path.join(FIXTURES, name))
    lazy = ifcopenshell.open(os.path.join(FIXTURES, name), lazy=True)
    assert lazy.schema == strict.schema
    strict_ids = sorted(e.id() for e in strict)
    assert sorted(e.id() for e in lazy) == strict_ids
    for e in strict:
        l = lazy.by_id(e.id())
        assert l.is_a() == e.is_a()
        assert str(l) == str(e)
        assert len(lazy.get_inverse(l)) == len(strict.get_inverse(e))
    for e in strict.by_type("IfcRoot"):
        assert lazy.by_guid(e.GlobalId).id() == e.id()
    assert len(lazy.by_type("IfcWall")) == len(strict.by_type("IfcWall"))
    assert ifcopenshell.get_log() == ""


def test_lazy_file_can_be_edited_and_written(tmp_path):
    lazy = ifcopenshell.open(os.path.join(FIXTURES, FILES[0]), lazy=True)
    existing = lazy.by_type("IfcProduct")[0]
    existing.Name = "Renamed"
    wall = ifcopenshell.api.root.create_entity(lazy, ifc_class="IfcWall")
    pset = ifcopenshell.api.pset.add_pset(lazy, product=wall, name="Pset_LazyTest")
    ifcopenshell.api.pset.edit_pset(lazy, pset=pset, properties={"Answer": 42})
    out = tmp_path / "lazy.ifc"
    lazy.write(str(out))
    reread = ifcopenshell.open(str(out))
    assert reread.by_id(existing.id()).Name == "Renamed"
    assert ifcopenshell.util.element.get_psets(reread.by_id(wall.id()))["Pset_LazyTest"]["Answer"] == 42
    assert len(list(reread)) == len(list(ifcopenshell.open(os.path.join(FIXTURES, FILES[0])))) + len(list(lazy)) - len(
        list(ifcopenshell.open(os.path.join(FIXTURES, FILES[0])))
    )


def test_lazy_open_falls_back_on_unsupported_syntax(tmp_path):
    src = open(os.path.join(FIXTURES, FILES[0]), "rb").read()
    data_at = src.index(b"DATA;")
    patched = src[: data_at + 5] + b"\nSTRAY;" + src[data_at + 5 :]
    path = tmp_path / "stray.ifc"
    path.write_bytes(patched)
    f = ifcopenshell.open(str(path), lazy=True)
    assert not f.lazy_loading()
    assert len(f.by_type("IfcRoot")) > 0
