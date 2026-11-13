# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import ezdxf

from bonsai.tool.drawing import Drawing as subject
from test.bim.bootstrap import NewFile

SVG_HEADER = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:ifc="http://www.ifcopenshell.org/ns">'


def convert(tmp_path, groups):
    svg_path = tmp_path / "in.svg"
    dxf_path = tmp_path / "out.dxf"
    svg_path.write_text(SVG_HEADER + groups + "</svg>")
    subject.convert_svg_to_dxf(svg_path, dxf_path)
    return list(ezdxf.readfile(dxf_path).modelspace())


class TestConvertSvgToDxf(NewFile):
    def test_single_digit_integer_and_scientific_coordinates(self, tmp_path):
        groups = (
            '<g ifc:name="plan"><g><path d="M0,0 L5,0 L5,3 L0,3 Z"/><path d="M1.5e-13,0 L2,0 L2,1.5e-13 Z"/></g></g>'
        )
        entities = convert(tmp_path, groups)
        assert [e.dxftype() for e in entities] == ["LWPOLYLINE", "LWPOLYLINE"]
        assert [tuple(map(round, p)) for p in entities[0].get_points("xy")] == [(0, 0), (5, 0), (5, -3), (0, -3)]
        assert [tuple(map(round, p)) for p in entities[1].get_points("xy")] == [(0, 0), (2, 0), (2, 0)]

    def test_every_named_group_is_exported(self, tmp_path):
        groups = (
            '<g ifc:name="a"><g><path d="M0.5,0.5 L1.5,0.5"/></g></g>'
            '<g ifc:name="b"><g><path d="M2.5,0.5 L3.5,0.5"/></g></g>'
        )
        assert len(convert(tmp_path, groups)) == 2
