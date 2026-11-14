# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

import csv
import json

import bpy
import ifcopenshell
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


@pytest.fixture
def ifc_file():
    previous = IfcStore.file
    IfcStore.file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(IfcStore.file, ifc_class="IfcProject", name="Project")
    yield IfcStore.file
    IfcStore.file = previous


def write_template(path, query, header):
    attribute = {"name": "Name", "header": header, "sort": "NONE", "group": "NONE", "summary": "NONE"}
    attribute["formatting"] = "{{value}}"
    settings = {
        "include_global_id": False,
        "null_value": "-",
        "empty_value": "-",
        "true_value": "YES",
        "false_value": "NO",
        "concat_value": ", ",
    }
    path.write_text(json.dumps({"query": query, "attributes": [attribute], "settings": settings}))
    return str(path)


def test_export_stacked_ifccsv_appends_each_template_as_its_own_block(ifc_file, tmp_path):
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall", name="Wall A")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSlab", name="Slab A")
    props = tool.Blender.get_csv_props()
    props.should_load_from_memory = True
    props.csv_delimiter = ","
    props.stacked_templates.clear()
    props.stacked_templates.add().name = write_template(tmp_path / "walls.json", "IfcWall", "Wall")
    props.stacked_templates.add().name = write_template(tmp_path / "slabs.json", "IfcSlab", "Slab")
    output = tmp_path / "stacked.csv"

    assert bpy.ops.bim.export_stacked_ifccsv(filepath=str(output)) == {"FINISHED"}

    with open(output, newline="") as f:
        rows = list(csv.reader(f))
    assert rows == [["Wall"], ["Wall A"], [], ["Slab"], ["Slab A"]]
