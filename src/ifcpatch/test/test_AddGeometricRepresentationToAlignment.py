# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import re

from ifcpatch.recipes.AddGeometricRepresentationToAlignment import Patcher


class TestAddGeometricRepresentationToAlignmentDocstring:
    """Regression test: the docstring's example was copy-pasteable as-is by
    users, and is shown as CLI/Bonsai UI help text, but it quoted a recipe
    name ("AddGeometricRepresentationAlignment") that does not match this
    module's actual name, so copying it verbatim raised
    ModuleNotFoundError."""

    def test_docstring_example_recipe_name_matches_the_module_name(self):
        doc = Patcher.__init__.__doc__
        assert doc is not None
        match = re.search(r'"recipe":\s*"([^"]+)"', doc)
        assert match is not None, "docstring example must quote a recipe name"
        assert match.group(1) == "AddGeometricRepresentationToAlignment"
