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

from pathlib import Path

import ifcopenshell

TEST_FILE = Path(__file__).parent / "files" / "basic.ifc"


def build_ifc_with_many_points(num_points: int = 600) -> tuple[bytes, int, tuple[float, float, float]]:
    """Return LF-terminated IFC bytes with extra IfcCartesianPoints appended near the end.

    Also returns the step id and expected coordinates of the last appended point, which
    is used to detect any accumulated per-line byte offset drift.
    """
    lines = TEST_FILE.read_text().split("\n")
    endsec_index = lines.index("ENDSEC;")
    next_id = 1000
    last_id = None
    last_coords = None
    extra_lines = []
    for i in range(num_points):
        step_id = next_id + i
        coords = (float(i), float(i) * 2, float(i) * 3)
        extra_lines.append(f"#{step_id}=IFCCARTESIANPOINT(({coords[0]},{coords[1]},{coords[2]}));")
        last_id = step_id
        last_coords = coords
    lines[endsec_index:endsec_index] = extra_lines
    return "\n".join(lines).encode("ascii"), last_id, last_coords


class TestStreamLineEndings:
    def test_stream_handles_lf_and_crlf_line_endings(self, tmp_path: Path) -> None:
        lf_content, late_id, expected_coords = build_ifc_with_many_points()
        crlf_content = lf_content.replace(b"\n", b"\r\n")

        lf_path = tmp_path / "many_points_lf.ifc"
        crlf_path = tmp_path / "many_points_crlf.ifc"
        lf_path.write_bytes(lf_content)
        crlf_path.write_bytes(crlf_content)

        for path in (lf_path, crlf_path):
            stream_file: ifcopenshell.stream
            stream_file = ifcopenshell.open(path, should_stream=True)
            assert (element := stream_file.by_id(late_id))
            assert element.Coordinates == expected_coords

    def test_stream_handles_crlf_on_original_test_file(self, tmp_path: Path) -> None:
        crlf_content = TEST_FILE.read_bytes().replace(b"\n", b"\r\n")
        crlf_path = tmp_path / "basic_crlf.ifc"
        crlf_path.write_bytes(crlf_content)

        stream_file: ifcopenshell.stream
        stream_file = ifcopenshell.open(crlf_path, should_stream=True)
        assert (element := stream_file.by_id(1))
        assert element.Name == "My Project"


class TestFile:
    def test_run(self):
        stream_file: ifcopenshell.stream
        stream_file = ifcopenshell.open(TEST_FILE, should_stream=True)
        assert stream_file.schema == "IFC4"

    def test_by_id(self):
        stream_file: ifcopenshell.stream
        stream_file = ifcopenshell.open(TEST_FILE, should_stream=True)
        assert (element := stream_file.by_id(1))
        assert str(element) == "#1=IFCPROJECT('3kv235yMjDO9tHiTzD8QuS',$,'My Project',$,$,$,$,(#14,#26),#9);"

    def test_by_type(self):
        stream_file: ifcopenshell.stream
        stream_file = ifcopenshell.open(TEST_FILE, should_stream=True)
        assert (elements := stream_file.by_type("IfcProject"))
        assert str(elements[0]) == "#1=IFCPROJECT('3kv235yMjDO9tHiTzD8QuS',$,'My Project',$,$,$,$,(#14,#26),#9);"


class TestEntity:
    def test_getattr(self):
        stream_file: ifcopenshell.stream
        stream_file = ifcopenshell.open(TEST_FILE, should_stream=True)
        assert (element := stream_file.by_id(1))
        assert element.Name == "My Project"
