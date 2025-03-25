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
