# This file was generated with the assistance of an AI coding tool.

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

import shutil
import subprocess
from pathlib import Path

import pytest

import ifcopenshell
import ifcopenshell.guid

WALL_NAME = "Test Wall"


def write_model(path: Path, schema: str, relation: str) -> None:
    f = ifcopenshell.file(schema=schema)
    units = f.createIfcUnitAssignment([f.createIfcSIUnit(UnitType="LENGTHUNIT", Name="METRE")])
    project = f.createIfcProject(ifcopenshell.guid.new(), Name="Project", UnitsInContext=units)
    wall = f.createIfcWall(ifcopenshell.guid.new(), Name=WALL_NAME)
    f.createIfcRelAggregates(ifcopenshell.guid.new(), RelatingObject=project, RelatedObjects=[wall])
    if relation == "type":
        wall_type = f.createIfcWallType(ifcopenshell.guid.new(), Name="Wall Type", PredefinedType="STANDARD")
        f.createIfcRelDefinesByType(ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingType=wall_type)
    elif relation == "properties":
        value = f.createIfcPropertySingleValue(Name="Prop", NominalValue=f.createIfcLabel("Value"))
        pset = f.createIfcPropertySet(ifcopenshell.guid.new(), Name="Pset_Test", HasProperties=[value])
        f.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(), RelatedObjects=[wall], RelatingPropertyDefinition=pset
        )
    f.write(str(path))


@pytest.mark.skipif(shutil.which("IfcConvert") is None, reason="Requires IfcConvert in path")
class TestDocumentSerializers:
    @pytest.mark.parametrize("extension", ["json", "xml"])
    @pytest.mark.parametrize("schema", ["IFC2X3", "IFC4"])
    @pytest.mark.parametrize("relation", ["type", "properties", "none"])
    def test_model_converts_with_its_wall(self, tmp_path, schema, relation, extension):
        source = tmp_path / "model.ifc"
        target = tmp_path / f"model.{extension}"
        write_model(source, schema, relation)
        result = subprocess.run([shutil.which("IfcConvert"), "-qy", str(source), str(target)], capture_output=True)
        assert result.returncode == 0, result.stderr.decode(errors="replace")
        assert WALL_NAME in target.read_text(encoding="utf-8")
