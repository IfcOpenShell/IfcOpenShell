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
import re
import struct
import tempfile

import pytest

import ifcopenshell
import ifcopenshell.guid

try:
    import psutil
except ImportError:
    psutil = None

fn = os.path.join(os.path.dirname(__file__), "fixtures/ColumnPSetsOfSets.ifc")

needs_rocksdb = pytest.mark.skipif(
    not hasattr(ifcopenshell.ifcopenshell_wrapper, "RocksDBPrefixIterator"),
    reason="IfcOpenShell was built without RocksDB support",
)
SCHEMAS = ["IFC2X3", "IFC4", "IFC4X3"]
STORAGES = [
    "memory",
    pytest.param("rocksdb_readonly", marks=needs_rocksdb),
    pytest.param("rocksdb", marks=needs_rocksdb),
]
WRITABLE_STORAGES = ["memory", pytest.param("rocksdb", marks=needs_rocksdb)]


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


def test_opening_unicode():
    import ifcopenshell.template

    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, "ხყჯ𐰢ᨕதకᎣᚱᾗ.ifc")
        f = ifcopenshell.template.create()
        f.write(fn)
        g = ifcopenshell.open(fn)
        assert g.by_type("ifcproject")


@pytest.mark.skipif(psutil is None, reason="psutil not installed")
def test_memusage_partial_open():
    # Run in a subprocess to ensure the file is not already in the process page
    # cache from earlier tests, which would make both RSS deltas read as zero.
    import subprocess
    import sys

    script = f"""
import sys; sys.path.remove('')
import psutil
import ifcopenshell

fn = {repr(fn)}
m0 = psutil.Process().memory_info().rss
f = ifcopenshell.open(fn)
m1 = psutil.Process().memory_info().rss
g = ifcopenshell.open(fn, bypass_types=("IfcRepresentationItem",))
m2 = psutil.Process().memory_info().rss
expected_ratio = 0.75
assert (m2 - m1) < (m1 - m0) * expected_ratio, (
    f"bypass_types did not reduce memory: normal open added {{m1 - m0}} bytes, "
    f"bypass open added {{m2 - m1}} bytes (expected < {{(m1 - m0) * expected_ratio:.0f}})"
)
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout


def test_rocks():
    with tempfile.TemporaryDirectory() as d:
        rfn = os.path.join(d, os.path.basename(fn))
        ifcopenshell.convert_path_to_rocksdb(fn, rfn)

        assert os.path.exists(rfn)

        f = ifcopenshell.open(rfn)
        assert f[139].RelatingPropertyDefinition.is_a("IfcPropertySetDefinitionSet")
        assert {x.id() for x in f[139].RelatingPropertyDefinition[0]} == {136, 138}

        # Numeric key segments are fixed-width hex: i|<id>|<attribute>,
        # t|<identity>|<attribute>. See rocksdb_map_adapter.h.
        b = f.key_value_store_query(f"i|{139:016x}|{5:016x}")[2:]
        iden = struct.unpack("Q", b)[0]
        b = f.key_value_store_query(f"t|{iden:016x}|{0:016x}")[1:]
        assert set(struct.unpack("Q", b[i : i + 8])[0] for i in range(1, len(b), 9)) == {136, 138}

        g = ifcopenshell.open(fn)
        for inst in g.by_type("IfcRoot"):
            assert f.by_guid(inst.GlobalId).id() == inst.id()

        del g
        del f
        gc.collect()


def create_guid_model(directory, schema):
    f = ifcopenshell.file(schema=schema)
    f.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="Project")
    for i in range(5):
        f.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name=f"Wall {i}")
    for i in range(200):
        f.create_entity("IfcCartesianPoint", Coordinates=(float(i), 0.0, 0.0))
    spf_path = os.path.join(directory, "model.ifc")
    f.write(spf_path)
    return spf_path, {inst.GlobalId: inst.id() for inst in f.by_type("IfcRoot")}


def open_guid_model(directory, schema, storage):
    spf_path, roots = create_guid_model(directory, schema)
    if storage == "memory":
        return ifcopenshell.open(spf_path), roots
    rocks_path = os.path.join(directory, "model.rdb")
    ifcopenshell.convert_path_to_rocksdb(spf_path, rocks_path)
    return ifcopenshell.open(rocks_path, readonly=storage == "rocksdb_readonly"), roots


@pytest.mark.parametrize("schema", SCHEMAS)
@pytest.mark.parametrize("storage", STORAGES)
def test_by_guid_resolves_every_converted_global_id(tmp_path, schema, storage):
    g, roots = open_guid_model(str(tmp_path), schema, storage)
    assert len(roots) == 6
    for guid, instance_id in roots.items():
        found = g.by_guid(guid)
        assert found.id() == instance_id
        assert found.GlobalId == guid
    del g
    gc.collect()


@pytest.mark.parametrize("schema", SCHEMAS)
@pytest.mark.parametrize("storage", STORAGES)
def test_by_guid_unknown_global_id_raises(tmp_path, schema, storage):
    g, roots = open_guid_model(str(tmp_path), schema, storage)
    unknown = ifcopenshell.guid.new()
    with pytest.raises(RuntimeError, match=re.escape(f"GlobalId '{unknown}' not found")):
        g.by_guid(unknown)
    del g
    gc.collect()


@pytest.mark.parametrize("schema", SCHEMAS)
@pytest.mark.parametrize("storage", WRITABLE_STORAGES)
def test_by_guid_resolves_added_entity(tmp_path, schema, storage):
    g, roots = open_guid_model(str(tmp_path), schema, storage)
    guid = ifcopenshell.guid.new()
    added = g.create_entity("IfcBuildingElementProxy", GlobalId=guid, Name="Added")
    assert added.id() not in roots.values()
    found = g.by_guid(guid)
    assert found.id() == added.id()
    assert found.is_a("IfcBuildingElementProxy")
    assert found.GlobalId == guid
    for existing_guid, instance_id in roots.items():
        assert g.by_guid(existing_guid).id() == instance_id
    del g
    gc.collect()


@pytest.mark.parametrize("schema", SCHEMAS)
@pytest.mark.parametrize("storage", WRITABLE_STORAGES)
def test_by_guid_follows_changed_global_id(tmp_path, schema, storage):
    g, roots = open_guid_model(str(tmp_path), schema, storage)
    wall = g.by_type("IfcWall")[0]
    old_guid = wall.GlobalId
    new_guid = ifcopenshell.guid.new()
    wall.GlobalId = new_guid
    found = g.by_guid(new_guid)
    assert found.id() == wall.id()
    assert found.is_a("IfcWall")
    with pytest.raises(RuntimeError, match=re.escape(f"GlobalId '{old_guid}' not found")):
        g.by_guid(old_guid)
    for existing_guid, instance_id in roots.items():
        if existing_guid != old_guid:
            assert g.by_guid(existing_guid).id() == instance_id
    del g
    gc.collect()


@pytest.mark.parametrize("schema", SCHEMAS)
@pytest.mark.parametrize("storage", WRITABLE_STORAGES)
def test_by_guid_removed_entity_raises(tmp_path, schema, storage):
    g, roots = open_guid_model(str(tmp_path), schema, storage)
    added_guid = ifcopenshell.guid.new()
    added = g.create_entity("IfcBuildingElementProxy", GlobalId=added_guid, Name="Added")
    assert g.by_guid(added_guid).id() == added.id()
    g.remove(added)
    with pytest.raises(RuntimeError, match=re.escape(f"GlobalId '{added_guid}' not found")):
        g.by_guid(added_guid)
    wall = g.by_type("IfcWall")[0]
    wall_guid = wall.GlobalId
    g.remove(wall)
    with pytest.raises(RuntimeError, match=re.escape(f"GlobalId '{wall_guid}' not found")):
        g.by_guid(wall_guid)
    for existing_guid, instance_id in roots.items():
        if existing_guid != wall_guid:
            assert g.by_guid(existing_guid).id() == instance_id
    del g
    gc.collect()


@needs_rocksdb
@pytest.mark.parametrize("schema", SCHEMAS)
def test_rocks_by_guid_added_entity_does_not_resolve_to_another_entity(tmp_path, schema):
    import subprocess
    import sys

    spf_path, roots = create_guid_model(str(tmp_path), schema)
    rocks_path = str(tmp_path / "model.rdb")
    ifcopenshell.convert_path_to_rocksdb(spf_path, rocks_path)
    script = """
import sys
import ifcopenshell
import ifcopenshell.guid

g = ifcopenshell.open(sys.argv[1], readonly=False)
guid = ifcopenshell.guid.new()
added = g.create_entity("IfcBuildingElementProxy", GlobalId=guid, Name="Added")
found = g.by_guid(guid)
assert found.id() == added.id(), f"{guid} resolved to #{found.id()} {found.is_a()}, expected #{added.id()}"
"""
    result = subprocess.run([sys.executable, "-c", script, rocks_path], capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stderr or result.stdout


def test_rocks_storage_getattr_invalid_attribute():
    with tempfile.TemporaryDirectory() as d:
        rfn = os.path.join(d, os.path.basename(fn))
        ifcopenshell.convert_path_to_rocksdb(fn, rfn)

        f = ifcopenshell.open(rfn)
        inst = f.storage.by_id(139)
        with pytest.raises(AttributeError):
            inst.NotARealAttribute

        del f
        gc.collect()


def test_rocks_storage_ids_and_type_lookups():
    with tempfile.TemporaryDirectory() as d:
        rfn = os.path.join(d, os.path.basename(fn))
        ifcopenshell.convert_path_to_rocksdb(fn, rfn)

        f = ifcopenshell.open(rfn)
        m = ifcopenshell.open(fn)
        assert sorted(i.id() for i in f.storage) == sorted(i.id() for i in m)
        inst = f.storage.by_id(139)
        assert inst.id() == 139
        assert len(inst) == 6
        assert repr(inst).startswith("#139=IfcRelDefinesByProperties(")
        assert [i.id() for i in f.storage.by_type("IfcColumn")] == [93]
        assert [i.id() for i in f.storage.by_id(93).IsDefinedBy] == [101, 102, 103, 139]

        del f
        gc.collect()


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
