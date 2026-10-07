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

import importlib
import pkgutil
import tempfile
import tomllib
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.root

import ifcpatch
import ifcpatch.recipes


class Test:
    def test_parsing_docs(self):
        for module_info in pkgutil.iter_modules(ifcpatch.recipes.__path__):
            docs = ifcpatch.extract_docs(module_info.name, "Patcher", "__init__", ("src", "file", "logger", "args"))
            assert docs is not None
            expected_keys = ("class_", "description", "output", "inputs")
            for key in expected_keys:
                assert key in docs

    def test_console_script_entry_point_patches_a_file(self, monkeypatch, tmp_path):
        pyproject = tomllib.loads((Path(ifcpatch.__file__).parent.parent / "pyproject.toml").read_text())
        module_name, function_name = pyproject["project"]["scripts"]["ifcpatch"].split(":")
        main = getattr(importlib.import_module(module_name), function_name)

        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSlab")
        input_path = tmp_path / "input.ifc"
        output_path = tmp_path / "output.ifc"
        ifc_file.write(str(input_path))
        monkeypatch.setattr(
            "sys.argv",
            ["ifcpatch", "-i", str(input_path), "-o", str(output_path), "-r", "ExtractElements", "-a", "IfcWall"],
        )

        main()

        output = ifcopenshell.open(str(output_path))
        assert len(output.by_type("IfcWall")) == 1
        assert not output.by_type("IfcSlab")

    def test_static_ifcpatch_execution(self):
        from ifcpatch.recipes import ExtractElements

        ifc_file = ifcopenshell.file()
        project = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")

        patcher = ExtractElements.Patcher(ifc_file, query="IfcWall")
        patcher.patch()

        output = patcher.get_output()
        assert isinstance(output, ifcopenshell.file)
        assert output.by_type("IfcProject")[0].GlobalId == project.GlobalId
        assert output.by_type("IfcWall")[0].GlobalId == wall.GlobalId

        output_path = Path(tempfile.mkstemp()[1])
        try:
            assert output_path.stat().st_size == 0
            ifcpatch.write(patcher.get_output(), output_path)
            assert output_path.stat().st_size != 0
        finally:
            output_path.unlink()
