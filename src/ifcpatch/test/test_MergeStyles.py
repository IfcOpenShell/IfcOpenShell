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

import ifcopenshell.api.style

import ifcpatch
import test.bootstrap


class TestMergeStyles(test.bootstrap.IFC4):
    def _add_shading_style(self):
        style = ifcopenshell.api.style.add_style(self.file)
        ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleShading",
            attributes={"SurfaceColour": {"Name": None, "Red": 1.0, "Green": 0.0, "Blue": 0.0}},
        )
        return style

    def test_merges_identical_styles(self):
        self._add_shading_style()
        self._add_shading_style()
        assert len(self.file.by_type("IfcPresentationStyle")) == 2

        ifcpatch.execute({"file": self.file, "recipe": "MergeStyles", "arguments": []})

        assert len(self.file.by_type("IfcPresentationStyle")) == 1

    def test_summary_reports_the_requested_class_not_the_last_elements_subtype(self, capsys):
        # Regression test: the loop rebound the outer "ifc_class" loop
        # variable to each element's concrete subtype (e.g. IfcSurfaceStyle
        # for an IfcPresentationStyle element), so the final summary line
        # reported that subtype instead of the class that was actually
        # requested.
        self._add_shading_style()
        self._add_shading_style()

        ifcpatch.execute({"file": self.file, "recipe": "MergeStyles", "arguments": []})

        lines = capsys.readouterr().out.strip().splitlines()
        assert lines[-1] == "Replaced 1 IfcPresentationStyle"


class TestMergeStylesIFC2X3(test.bootstrap.IFC2X3, TestMergeStyles):
    pass
