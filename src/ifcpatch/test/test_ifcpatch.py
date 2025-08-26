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

import tempfile
import ifcopenshell.api.root
import ifcpatch
from pathlib import Path


class Test:
    def test_parsing_docs(self):
        recipes = Path(ifcpatch.__file__).parent / "recipes"

        for f in recipes.glob("*.py"):
            if f.stem in "__init__":
                continue
            docs = ifcpatch.extract_docs(f.stem, "Patcher", "__init__", ("src", "file", "logger", "args"))
            assert docs is not None
            expected_keys = ("class_", "description", "output", "inputs")
            for key in expected_keys:
                assert key in docs

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

        output_path = Path(tempfile.mktemp())
        try:
            assert not output_path.exists()
            ifcpatch.write(patcher.get_output(), output_path)
            assert output_path.exists()
        finally:
            output_path.unlink()
