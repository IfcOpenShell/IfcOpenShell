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

import gc
import os
import struct
import pytest
import ifcopenshell
import tempfile

try:
    import psutil
except ImportError:
    psutil = None

fn = os.path.join(os.path.dirname(__file__), "fixtures/ColumnPSetsOfSets.ifc")


def test_stream():
    assert next(filter(lambda d: d.get("id") == 139, ifcopenshell.stream2(fn)))["RelatingPropertyDefinition"] == {
        "type": "IfcPropertySetDefinitionSet",
        "value": ({"ref": 136}, {"ref": 138}),
    }


def test_chunked_stream():
    assert list(ifcopenshell.stream2(fn)) == list(ifcopenshell.stream2(fn, page_size=1024))


def test_mmaped_stream():
    assert list(ifcopenshell.stream2(fn)) == list(ifcopenshell.stream2(fn, mmap=True))


def test_file():
    f = ifcopenshell.open(fn)
    assert f[139].RelatingPropertyDefinition.is_a("IfcPropertySetDefinitionSet")
    assert {x.id() for x in f[139].RelatingPropertyDefinition[0]} == {136, 138}


def test_partial_open():
    f = ifcopenshell.open(fn)
    assert len(f.by_type("ifccartesianpoint"))
    f = ifcopenshell.open(fn, bypass_types=("IfcRepresentationItem",))
    assert len(f.by_type("ifccartesianpoint")) == 0


@pytest.mark.skipif(psutil is None, reason="psutil not installed")
def test_memusage_partial_open():
    m0 = psutil.Process().memory_info().rss
    f = ifcopenshell.open(fn)
    m1 = psutil.Process().memory_info().rss
    g = ifcopenshell.open(fn, bypass_types=("IfcRepresentationItem",))
    m2 = psutil.Process().memory_info().rss
    # arbitrary...
    expected_ratio = 0.75
    assert (m2 - m1) < (m1 - m0) * expected_ratio


def test_rocks():
    with tempfile.TemporaryDirectory() as d:
        rfn = os.path.join(d, os.path.basename(fn))
        ifcopenshell.convert_path_to_rocksdb(fn, rfn)

        assert os.path.exists(rfn)

        f = ifcopenshell.open(rfn)
        assert f[139].RelatingPropertyDefinition.is_a("IfcPropertySetDefinitionSet")
        assert {x.id() for x in f[139].RelatingPropertyDefinition[0]} == {136, 138}

        b = f.wrapped_data.key_value_store_query("i|139|5")[2:]
        iden = struct.unpack("Q", b)[0]
        b = f.wrapped_data.key_value_store_query(f"t|{iden}|0")[1:]
        assert set(struct.unpack("Q", b[i : i + 8])[0] for i in range(1, len(b), 9)) == {136, 138}

        del f
        gc.collect()


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
