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

import ifcopenshell
import pytest


# ---------------------------------------------------------------------------
# as_template_data - values for tools that render sheet templates themselves
# ---------------------------------------------------------------------------


class TestAsTemplateData:
    """Values must render as pystache would render them, and survive JSON."""

    def _convert(self, value):
        from bonsai.bim.module.drawing import sheeter

        return sheeter.as_template_data(value)

    def test_scalars_become_text_as_pystache_prints_them(self):
        assert self._convert({"Name": None, "Scale": 1.0, "id": 5}) == {"Name": "None", "Scale": "1.0", "id": "5"}

    def test_booleans_stay_booleans_for_sections(self):
        assert self._convert({"has_revisions": False}) == {"has_revisions": False}

    def test_rows_stay_a_list_even_when_empty(self):
        # An empty list turned into the text "[]" would be truthy, and a
        # {{#revisions}} section would render once for nothing.
        assert self._convert({"revisions": []}) == {"revisions": []}
        assert self._convert({"revisions": [{"rev": "v1", "y": 0}]}) == {"revisions": [{"rev": "v1", "y": "0"}]}

    def test_other_sequences_are_text(self):
        assert self._convert({"Editors": ()}) == {"Editors": "()"}


# ---------------------------------------------------------------------------
# Editing template values - the write half, for tools that show sheets
# ---------------------------------------------------------------------------


@pytest.fixture
def sheet_model(tmp_path, monkeypatch):
    """A model with one sheet, one drawing placed on it, and tool.Drawing stubbed.

    The methods stubbed are the ones that reach into Blender or resolve URIs
    against the project; everything the code under test decides - which sheet a
    layout belongs to, which view a request names, what may be written - is real.
    """
    import ifcopenshell.api

    import bonsai.tool as tool
    from bonsai.bim.module.drawing import sheeter

    layout_path = str(tmp_path / "layouts" / "A01 - PLANS.svg")
    drawing_path = str(tmp_path / "drawings" / "MY STOREY PLAN.svg")

    ifc = ifcopenshell.file()
    sheet = ifc.createIfcDocumentInformation(Identification="A01", Name="PLANS", Scope="SHEET")
    layout_ref = ifc.createIfcDocumentReference(Location=layout_path, Description="LAYOUT")
    drawing_ref = ifc.createIfcDocumentReference(Location=drawing_path, Description="DRAWING", Identification="1")
    annotation = ifc.createIfcAnnotation(GlobalId="0abcdefghijklmnopqrstu", ObjectType="DRAWING", Name="MY STOREY PLAN")

    references = {sheet.id(): [layout_ref, drawing_ref]}
    uris = {layout_ref.id(): layout_path, drawing_ref.id(): drawing_path}

    def get_document_uri(document, description=None):
        if document.is_a("IfcDocumentInformation"):
            for reference in references.get(document.id(), []):
                if reference.Description == description:
                    return uris[reference.id()]
            return None
        return uris.get(document.id())

    monkeypatch.setattr(tool.Ifc, "get", classmethod(lambda cls: ifc))
    monkeypatch.setattr(tool.Ifc, "get_path", classmethod(lambda cls: str(tmp_path / "model.ifc")))
    # tool.Ifc.run reaches for the file Blender has open, not the one patched in.
    monkeypatch.setattr(
        tool.Ifc, "run", classmethod(lambda cls, command, **kwargs: ifcopenshell.api.run(command, ifc, **kwargs))
    )
    monkeypatch.setattr(tool.Drawing, "get_document_uri", staticmethod(get_document_uri))
    monkeypatch.setattr(
        tool.Drawing, "get_document_references", staticmethod(lambda info: references.get(info.id(), []))
    )
    monkeypatch.setattr(tool.Drawing, "get_reference_description", staticmethod(lambda ref: ref.Description))
    monkeypatch.setattr(tool.Drawing, "get_drawing_document", staticmethod(lambda drawing: drawing_ref))
    monkeypatch.setattr(tool.Drawing, "get_sheet_identification", staticmethod(lambda s: s.Identification))
    monkeypatch.setattr(tool.Drawing, "get_drawing_human_scale", staticmethod(lambda drawing: '1/4"=1\'-0"'))
    monkeypatch.setattr(tool.Drawing, "import_sheets", staticmethod(lambda: None))
    monkeypatch.setattr(tool.Drawing, "import_drawings", staticmethod(lambda: None))

    class Model:
        pass

    model = Model()
    model.builder = sheeter.SheetBuilder()
    model.ifc = ifc
    model.sheet = sheet
    model.drawing = annotation
    model.reference = drawing_ref
    model.layout = layout_path
    model.drawing_path = drawing_path
    # So a test can move the layout the way rename_sheet would.
    model.uris = uris
    model.layout_ref = layout_ref
    return model


@pytest.fixture
def calls(monkeypatch):
    """Record what would be asked of bonsai.core.drawing, without doing it."""
    import bonsai.core.drawing as core

    recorded = []
    for name in ("rename_sheet", "rename_reference", "update_drawing_name"):
        monkeypatch.setattr(
            core,
            name,
            lambda *a, _name=name, **kw: recorded.append((_name, kw)),
        )
    return recorded


class TestFindSheet:
    def test_matches_a_layout_by_path(self, sheet_model):
        assert sheet_model.builder.find_sheet(sheet_model.layout) == sheet_model.sheet

    def test_matches_however_the_path_is_spelled(self, sheet_model, tmp_path):
        # The caller is another tool: it may have the path from a layout link,
        # with a different case or a relative step in it.
        spelled = os.path.join(str(tmp_path), "layouts", "..", "layouts", "A01 - PLANS.svg").upper()
        assert sheet_model.builder.find_sheet(spelled) == sheet_model.sheet

    def test_none_when_no_sheet_uses_it(self, sheet_model, tmp_path):
        assert sheet_model.builder.find_sheet(str(tmp_path / "layouts" / "A99.svg")) is None


class TestGetEditableFields:
    def test_a_titleblock_field_reports_its_value(self, sheet_model):
        fields = sheet_model.builder.get_editable_fields(sheet_model.layout, {"kind": "sheet"}, ["Name"])["fields"]
        assert fields == [{"name": "Name", "value": "PLANS", "editable": True}]

    def test_an_unset_field_is_empty_not_the_word_None(self, sheet_model):
        # A build prints "None" for an unset attribute, but this value goes into
        # a box someone types in - and saving it back would set that word.
        fields = sheet_model.builder.get_editable_fields(sheet_model.layout, {"kind": "sheet"}, ["Revision"])["fields"]
        assert fields[0]["value"] == ""

    def test_scale_is_read_only_with_a_reason(self, sheet_model):
        fields = sheet_model.builder.get_editable_fields(
            sheet_model.layout, {"kind": "drawing", "globalId": "0abcdefghijklmnopqrstu"}, ["Scale"]
        )["fields"]
        assert fields[0]["editable"] is False
        assert "camera" in fields[0]["reason"]

    def test_a_sheet_field_on_a_view_title_says_where_to_edit_it(self, sheet_model):
        fields = sheet_model.builder.get_editable_fields(
            sheet_model.layout, {"kind": "drawing", "globalId": "0abcdefghijklmnopqrstu"}, ["SheetName"]
        )["fields"]
        assert fields[0]["editable"] is False
        assert "titleblock" in fields[0]["reason"]

    def test_a_drawing_is_found_by_the_file_it_places(self, sheet_model):
        answer = sheet_model.builder.get_editable_fields(
            sheet_model.layout, {"kind": "placement", "path": sheet_model.drawing_path}, ["Name"]
        )
        assert answer["kind"] == "drawing"
        # The reference has no name of its own, so the title shows the drawing's.
        assert answer["fields"][0]["value"] == "MY STOREY PLAN"

    def test_an_unknown_view_is_refused_by_name(self, sheet_model, tmp_path):
        with pytest.raises(ValueError, match="no such view"):
            sheet_model.builder.get_editable_fields(
                sheet_model.layout, {"kind": "placement", "path": str(tmp_path / "drawings" / "GONE.svg")}, ["Name"]
            )

    def test_an_unknown_layout_is_refused_by_name(self, sheet_model, tmp_path):
        with pytest.raises(ValueError, match="A99"):
            sheet_model.builder.get_editable_fields(str(tmp_path / "layouts" / "A99.svg"), {"kind": "sheet"}, ["Name"])


class TestSetTemplateValues:
    def test_renaming_a_sheet_keeps_the_field_not_being_set(self, sheet_model, calls):
        # Identification and Name together name the layout and sheet files, so
        # Bonsai renames on both at once - setting one must not blank the other.
        sheet_model.builder.set_template_values(sheet_model.layout, {"kind": "sheet"}, {"Name": "PLANS AND SECTIONS"})
        assert calls == [("rename_sheet", {"sheet": sheet_model.sheet, "identification": "A01", "name": "PLANS AND SECTIONS"})]

    def test_renaming_a_sheet_sets_both_when_both_are_given(self, sheet_model, calls):
        sheet_model.builder.set_template_values(
            sheet_model.layout, {"kind": "sheet"}, {"Identification": "A02", "Name": "SECTIONS"}
        )
        assert calls[0][1]["identification"] == "A02"
        assert calls[0][1]["name"] == "SECTIONS"

    def test_a_plain_titleblock_field_is_written_as_an_attribute(self, sheet_model, calls):
        sheet_model.builder.set_template_values(sheet_model.layout, {"kind": "sheet"}, {"Revision": "C"})
        assert calls == []
        assert sheet_model.sheet.Revision == "C"

    def test_renaming_a_drawing_goes_through_bonsai(self, sheet_model, calls):
        # Renaming a drawing moves its SVG and relinks every layout placing it,
        # which is the whole reason an edit comes here rather than to the file.
        sheet_model.builder.set_template_values(
            sheet_model.layout, {"kind": "drawing", "globalId": "0abcdefghijklmnopqrstu"}, {"Name": "LEVEL 1 PLAN"}
        )
        assert calls == [("update_drawing_name", {"drawing": sheet_model.drawing, "name": "LEVEL 1 PLAN"})]

    def test_a_named_reference_is_renamed_in_place(self, sheet_model, calls):
        # A view-title shows the reference's own name when it has one, so that
        # is where the edit goes - the drawing keeps its name and its file.
        sheet_model.reference.Name = "PLAN AS PLACED"
        sheet_model.builder.set_template_values(
            sheet_model.layout, {"kind": "drawing", "globalId": "0abcdefghijklmnopqrstu"}, {"Name": "PLAN, AS PLACED"}
        )
        assert calls == []
        assert sheet_model.reference.Name == "PLAN, AS PLACED"

    def test_a_view_number_goes_through_bonsai(self, sheet_model, calls):
        sheet_model.builder.set_template_values(
            sheet_model.layout, {"kind": "drawing", "globalId": "0abcdefghijklmnopqrstu"}, {"Identification": "3"}
        )
        assert calls == [("rename_reference", {"reference": sheet_model.reference, "identification": "3"})]

    def test_a_read_only_field_is_refused_with_its_reason(self, sheet_model, calls):
        with pytest.raises(ValueError, match="camera"):
            sheet_model.builder.set_template_values(
                sheet_model.layout, {"kind": "drawing", "globalId": "0abcdefghijklmnopqrstu"}, {"Scale": "1:50"}
            )
        assert calls == []

    def test_nothing_is_written_when_one_field_is_refused(self, sheet_model, calls):
        # All or nothing: a half-applied edit would leave the sheet showing a
        # mixture of what was asked for and what was there.
        with pytest.raises(ValueError):
            sheet_model.builder.set_template_values(
                sheet_model.layout, {"kind": "sheet"}, {"Name": "SECTIONS", "Scope": "DRAWING"}
            )
        assert calls == []
        assert sheet_model.sheet.Name == "PLANS"

    def test_it_answers_with_where_the_layout_is_now(self, sheet_model, monkeypatch, tmp_path):
        # Renaming a sheet moves its layout, so the path the caller asked about
        # is gone by the time it is answered. Without being told the new one it
        # would have to wait to notice the file move before it could ask again.
        import bonsai.core.drawing as core

        moved = str(tmp_path / "layouts" / "A02 - PLANS.svg")
        monkeypatch.setattr(
            core,
            "rename_sheet",
            lambda *a, **kw: sheet_model.uris.update({sheet_model.layout_ref.id(): moved}),
        )
        answer = sheet_model.builder.set_template_values(
            sheet_model.layout, {"kind": "sheet"}, {"Identification": "A02"}
        )
        assert answer["layout"] == os.path.abspath(moved)
        assert answer["changed"] == ["Identification"]

    def test_an_empty_edit_changes_nothing(self, sheet_model, calls):
        assert sheet_model.builder.set_template_values(sheet_model.layout, {"kind": "sheet"}, {}) == {"changed": []}
        assert calls == []
