# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz <ryan@openingdesign.com>
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

import xml.etree.ElementTree as ET


class _FakeReference:
    def __init__(self, step_id: int):
        self._id = step_id

    def id(self) -> int:
        return self._id


class TestFindDrawingGroup:
    LAYOUT = (
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
        '  <g data-type="drawing" data-id="{first}" data-drawing="0aaa">'
        '    <image data-type="foreground"'
        '           xlink:href="..%5Cdrawings%5CPLAN%20-%20LEVEL%201.svg" />'
        "  </g>"
        '  <g data-type="drawing" data-id="{second}" data-drawing="0bbb">'
        '    <image data-type="foreground"'
        '           xlink:href="..%5Cdrawings%5CSECTION%20A.svg" />'
        "  </g>"
        "</svg>"
    )

    def _setup(self, tmp_path, monkeypatch, first="101", second="102", drawing="PLAN - LEVEL 1.svg"):
        import bonsai.tool as tool
        from bonsai.bim.module.drawing import sheeter

        layouts = tmp_path / "layouts"
        layouts.mkdir()
        layout_path = layouts / "A101 - PLANS.svg"
        layout_path.write_text(self.LAYOUT.format(first=first, second=second))

        drawing_path = str(tmp_path / "drawings" / drawing)
        monkeypatch.setattr(tool.Drawing, "get_document_uri", lambda *a, **k: drawing_path)

        root = ET.parse(str(layout_path)).getroot()
        return sheeter.SheetBuilder(), root, str(layout_path)

    def test_matches_on_data_id_when_ids_are_current(self, tmp_path, monkeypatch):
        builder, root, layout_path = self._setup(tmp_path, monkeypatch)
        group = builder.find_drawing_group(root, layout_path, _FakeReference(102))
        assert group is not None
        assert group.attrib["data-drawing"] == "0bbb"

    def test_falls_back_to_the_drawing_path_when_data_id_is_stale(self, tmp_path, monkeypatch):
        """STEP ids do not survive a re-serialisation of the IFC.

        Merging a project renumbers entities, so every data-id in every layout
        points at nothing. Matching on it alone found no group, and the drawing
        was left on the sheet while leaving the model - silently.
        """
        builder, root, layout_path = self._setup(tmp_path, monkeypatch, first="3729889", second="3729890")
        group = builder.find_drawing_group(root, layout_path, _FakeReference(101))
        assert group is not None
        assert group.attrib["data-drawing"] == "0aaa"

    def test_returns_none_when_the_drawing_is_not_on_the_sheet(self, tmp_path, monkeypatch):
        builder, root, layout_path = self._setup(
            tmp_path, monkeypatch, first="3729889", second="3729890", drawing="ELEVATION - NORTH.svg"
        )
        assert builder.find_drawing_group(root, layout_path, _FakeReference(101)) is None
