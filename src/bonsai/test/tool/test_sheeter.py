# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Bruno Postle <bruno@postle.net>
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

import os
import re
import time
import xml.etree.ElementTree as ET

import ifcopenshell
import pytest

try:
    import git
    import git.exc

    HAS_GIT = True
except ImportError:
    HAS_GIT = False

requires_git = pytest.mark.skipif(not HAS_GIT, reason="GitPython not available")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_repo(tmpdir: str) -> "git.Repo":
    repo = git.Repo.init(tmpdir)
    with repo.config_writer() as cfg:
        cfg.set_value("user", "name", "Test User")
        cfg.set_value("user", "email", "test@example.com")
    return repo


def _commit(repo: "git.Repo", tmpdir: str, content: str = "data") -> "git.Commit":
    path = os.path.join(tmpdir, "model.ifc")
    with open(path, "w") as f:
        f.write(content)
    repo.index.add([os.path.normpath(path)])
    return repo.index.commit(content)


@pytest.fixture
def builder():
    """Return a SheetBuilder with bonsai.bim loaded lazily."""
    from bonsai.bim.module.drawing import sheeter

    return sheeter.SheetBuilder()


@pytest.fixture
def builder_at(monkeypatch):
    """Factory: builder_at(ifc_path) patches tool.Ifc.get_path and returns a SheetBuilder."""
    import bonsai.tool as tool
    from bonsai.bim.module.drawing import sheeter

    def factory(ifc_path):
        monkeypatch.setattr(tool.Ifc, "get_path", classmethod(lambda cls: ifc_path))
        return sheeter.SheetBuilder()

    return factory


# ---------------------------------------------------------------------------
# Unit conversions (pure, no add-on registration required)
# ---------------------------------------------------------------------------


class TestConvertToMm:
    def test_mm(self, builder):
        assert builder.convert_to_mm("297mm") == pytest.approx(297.0)

    def test_cm(self, builder):
        assert builder.convert_to_mm("29.7cm") == pytest.approx(297.0)

    def test_in(self, builder):
        assert builder.convert_to_mm("1in") == pytest.approx(25.4)

    def test_px(self, builder):
        # 96 dpi: 96 px = 25.4 mm
        assert builder.convert_to_mm("96px") == pytest.approx(25.4, rel=1e-3)

    def test_pt(self, builder):
        # 72 pt = 25.4 mm
        assert builder.convert_to_mm("72pt") == pytest.approx(25.4, rel=1e-3)


class TestMmToPx:
    def test_round_trip(self, builder):
        assert builder.mm_to_px(builder.convert_to_mm("96px")) == pytest.approx(96.0, rel=1e-3)

    def test_zero(self, builder):
        assert builder.mm_to_px(0.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# parse_embedded_svg — Pystache template rendering
# ---------------------------------------------------------------------------


class TestParseEmbeddedSvg:
    def _image_element(self, filename="titleblock.svg"):
        image = ET.Element("image")
        image.attrib["x"] = "0mm"
        image.attrib["y"] = "0mm"
        image.attrib["width"] = "420mm"
        image.attrib["height"] = "297mm"
        image.attrib["{http://www.w3.org/1999/xlink}href"] = filename
        return image

    def _make_builder(self, tmp_path):
        from bonsai.bim.module.drawing import sheeter

        b = sheeter.SheetBuilder()
        b.layout_dir = str(tmp_path)
        b.sheets_dir = str(tmp_path)
        b.defs = ET.Element("defs")
        return b

    def test_variable_substitution(self, tmp_path):
        svg = '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><text>{{Name}}</text></svg>'
        (tmp_path / "titleblock.svg").write_text(svg)

        group = self._make_builder(tmp_path).parse_embedded_svg(self._image_element(), {"Name": "My Sheet"})
        texts = group.findall(".//{http://www.w3.org/2000/svg}text")
        assert any(t.text == "My Sheet" for t in texts)

    def test_revision_rows_rendered(self, tmp_path):
        svg = (
            '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><g>'
            '{{#revisions}}<text x="11" y="{{y}}">{{rev}}</text>{{/revisions}}'
            "</g></svg>"
        )
        (tmp_path / "titleblock.svg").write_text(svg)

        revisions = [
            {"rev": "v1.0", "date": "2024-01-01", "description": "First", "author": "TU", "issued": "", "y": 0},
            {"rev": "v2.0", "date": "2025-01-01", "description": "Second", "author": "TU", "issued": "", "y": -5},
        ]
        group = self._make_builder(tmp_path).parse_embedded_svg(self._image_element(), {"revisions": revisions})
        labels = [t.text for t in group.findall(".//{http://www.w3.org/2000/svg}text")]
        assert "v1.0" in labels
        assert "v2.0" in labels

    def test_has_revisions_section_hidden_when_false(self, tmp_path):
        svg = (
            '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg">'
            "{{#has_revisions}}<text>HEADERS</text>{{/has_revisions}}"
            "</svg>"
        )
        (tmp_path / "titleblock.svg").write_text(svg)

        group = self._make_builder(tmp_path).parse_embedded_svg(
            self._image_element(), {"has_revisions": False, "revisions": []}
        )
        texts = group.findall(".//{http://www.w3.org/2000/svg}text")
        assert not any(t.text == "HEADERS" for t in texts)

    def test_has_revisions_section_shown_when_true(self, tmp_path):
        svg = (
            '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg">'
            "{{#has_revisions}}<text>HEADERS</text>{{/has_revisions}}"
            "</svg>"
        )
        (tmp_path / "titleblock.svg").write_text(svg)

        group = self._make_builder(tmp_path).parse_embedded_svg(
            self._image_element(), {"has_revisions": True, "revisions": []}
        )
        texts = group.findall(".//{http://www.w3.org/2000/svg}text")
        assert any(t.text == "HEADERS" for t in texts)


# ---------------------------------------------------------------------------
# _get_git_revisions
# ---------------------------------------------------------------------------


class TestGetGitRevisions:
    def test_no_ifc_path_returns_empty(self, builder_at):
        assert builder_at(None)._get_git_revisions() == []

    @requires_git
    def test_not_a_git_repo_returns_empty(self, builder_at, tmp_path):
        assert builder_at(str(tmp_path / "model.ifc"))._get_git_revisions() == []

    @requires_git
    def test_no_tags_returns_empty(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))
        assert builder_at(str(tmp_path / "model.ifc"))._get_git_revisions() == []

    @requires_git
    def test_lightweight_tag_fields(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))
        repo.create_tag("v1.0")

        rows = builder_at(str(tmp_path / "model.ifc"))._get_git_revisions()

        assert len(rows) == 1
        assert rows[0]["rev"] == "v1.0"
        assert rows[0]["description"] == ""
        assert rows[0]["author"] == "TU"  # initials of "Test User"
        assert rows[0]["issued"] == ""
        assert rows[0]["y"] == 0

    @requires_git
    def test_annotated_tag_uses_message_first_line(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))
        repo.create_tag("v1.0", message="First release\nExtra detail ignored")

        rows = builder_at(str(tmp_path / "model.ifc"))._get_git_revisions()

        assert rows[0]["description"] == "First release"

    @requires_git
    def test_annotated_tag_author_is_tagger_initials(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))
        repo.create_tag("v1.0", message="Release")

        rows = builder_at(str(tmp_path / "model.ifc"))._get_git_revisions()

        assert rows[0]["author"] == "TU"

    @requires_git
    def test_date_is_iso_format(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))
        repo.create_tag("v1.0", message="Release")

        rows = builder_at(str(tmp_path / "model.ifc"))._get_git_revisions()

        assert re.match(r"\d{4}-\d{2}-\d{2}$", rows[0]["date"])

    @requires_git
    def test_multiple_tags_sorted_oldest_first(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path), "first")
        repo.create_tag("v1.0", message="First")
        time.sleep(1.1)  # ensure distinct second-level timestamps
        _commit(repo, str(tmp_path), "second")
        repo.create_tag("v2.0", message="Second")

        rows = builder_at(str(tmp_path / "model.ifc"))._get_git_revisions()

        assert len(rows) == 2
        assert rows[0]["rev"] == "v1.0"  # oldest at index 0 (bottom of table)
        assert rows[1]["rev"] == "v2.0"  # newest at index 1 (stacks upward)

    @requires_git
    def test_y_offsets_are_negative_multiples_of_5(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        for i in range(3):
            _commit(repo, str(tmp_path), f"rev{i}")
            repo.create_tag(f"v{i}.0", message=f"Release {i}")
            time.sleep(1.1)

        rows = builder_at(str(tmp_path / "model.ifc"))._get_git_revisions()

        assert rows[0]["y"] == 0
        assert rows[1]["y"] == -5
        assert rows[2]["y"] == -10


# ---------------------------------------------------------------------------
# get_titleblock_data
# ---------------------------------------------------------------------------


class TestGetTitleblockData:
    @requires_git
    def test_has_revisions_false_when_no_tags(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))

        ifc = ifcopenshell.file()
        sheet = ifc.createIfcDocumentInformation(Identification="DR-01", Name="Site Plan")
        data = builder_at(str(tmp_path / "model.ifc")).get_titleblock_data(sheet)

        assert data["has_revisions"] is False
        assert data["revisions"] == []

    @requires_git
    def test_has_revisions_true_when_tags_present(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))
        repo.create_tag("v1.0", message="Issued for review")

        ifc = ifcopenshell.file()
        sheet = ifc.createIfcDocumentInformation(Identification="DR-01", Name="Site Plan")
        data = builder_at(str(tmp_path / "model.ifc")).get_titleblock_data(sheet)

        assert data["has_revisions"] is True
        assert len(data["revisions"]) == 1

    @requires_git
    def test_sheet_ifc_attributes_are_included(self, builder_at, tmp_path):
        repo = _make_repo(str(tmp_path))
        _commit(repo, str(tmp_path))

        ifc = ifcopenshell.file()
        sheet = ifc.createIfcDocumentInformation(Identification="DR-01", Name="Site Plan")
        data = builder_at(str(tmp_path / "model.ifc")).get_titleblock_data(sheet)

        assert data["Identification"] == "DR-01"
        assert data["Name"] == "Site Plan"
