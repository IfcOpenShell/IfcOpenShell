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
import ifcopenshell.api.document
import ifcopenshell.guid
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


class TestSheetSpatial:
    """{{Site...}} and {{Building...}} fields: the site and building a sheet is about."""

    def _guid(self):
        return ifcopenshell.guid.new()

    def _project(self, sheet_model):
        projects = sheet_model.ifc.by_type("IfcProject")
        return projects[0] if projects else sheet_model.ifc.createIfcProject(GlobalId=self._guid(), Name="P")

    def _aggregate(self, sheet_model, parent, *parts):
        sheet_model.ifc.createIfcRelAggregates(GlobalId=self._guid(), RelatingObject=parent, RelatedObjects=parts)

    def _site(self, sheet_model, name=None, parent=None, **address):
        site = sheet_model.ifc.createIfcSite(GlobalId=self._guid(), Name=name)
        if address:
            site.SiteAddress = sheet_model.ifc.createIfcPostalAddress(**address)
        self._aggregate(sheet_model, parent or self._project(sheet_model), site)
        return site

    def _building(self, sheet_model, site, name=None, **address):
        building = sheet_model.ifc.createIfcBuilding(GlobalId=self._guid(), Name=name)
        if address:
            building.BuildingAddress = sheet_model.ifc.createIfcPostalAddress(**address)
        self._aggregate(sheet_model, site, building)
        return building

    def _link(self, sheet_model, *elements):
        ifcopenshell.api.document.assign_document(sheet_model.ifc, products=list(elements), document=sheet_model.sheet)

    def _data(self, sheet_model):
        return sheet_model.builder.get_spatial_data(sheet_model.sheet)

    def _set(self, sheet_model, values):
        return sheet_model.builder.set_template_values(sheet_model.layout, {"kind": "sheet"}, values)

    def _fields(self, sheet_model, names):
        return sheet_model.builder.get_editable_fields(sheet_model.layout, {"kind": "sheet"}, names)["fields"]

    # --- reading ---------------------------------------------------------

    def test_a_single_site_and_building_need_no_link(self, sheet_model):
        site = self._site(
            sheet_model, "Lot 7", AddressLines=["123 Main St", "Suite 4"], Town="Madison", Region="WI", PostalCode="53703"
        )
        self._building(sheet_model, site, "Library", Town="Madison")
        data = self._data(sheet_model)
        assert data["SiteName"] == "Lot 7"
        assert data["SiteAddressLines"] == "123 Main St, Suite 4"
        assert data["SiteAddress"] == "123 Main St, Suite 4, Madison, WI 53703"
        assert data["BuildingName"] == "Library"
        assert data["BuildingTown"] == "Madison"

    def test_a_building_and_its_site_each_show_their_own_address(self, sheet_model):
        # A Revit export's address is on the building; it is not shown as the site's.
        site = self._site(sheet_model, "Lot 7")
        self._building(sheet_model, site, "Library", Town="Chicago")
        data = self._data(sheet_model)
        assert data["SiteTown"] == ""
        assert data["BuildingTown"] == "Chicago"

    def test_several_buildings_and_no_link_leave_the_building_blank(self, sheet_model):
        # Guessing would put one building's address on another's sheet.
        site = self._site(sheet_model, "Campus")
        self._building(sheet_model, site, "North Hall", Town="Madison")
        self._building(sheet_model, site, "South Hall", Town="Verona")
        data = self._data(sheet_model)
        assert data["SiteName"] == "Campus"
        assert data["BuildingName"] == ""
        assert data["BuildingTown"] == ""

    def test_a_linked_building_is_shown_with_the_site_it_is_on(self, sheet_model):
        north = self._site(sheet_model, "North Lot")
        south = self._site(sheet_model, "South Lot")
        self._building(sheet_model, north, "North Hall")
        hall = self._building(sheet_model, south, "South Hall", Town="Verona")
        self._link(sheet_model, hall)
        data = self._data(sheet_model)
        assert data["BuildingName"] == "South Hall"
        assert data["BuildingTown"] == "Verona"
        assert data["SiteName"] == "South Lot"

    def test_a_linked_site_narrows_the_buildings_to_its_own(self, sheet_model):
        north = self._site(sheet_model, "North Lot")
        south = self._site(sheet_model, "South Lot")
        self._building(sheet_model, north, "North Hall")
        self._building(sheet_model, south, "South Hall")
        self._link(sheet_model, south)
        assert self._data(sheet_model)["BuildingName"] == "South Hall"

    def test_the_lots_of_a_site_complex_do_not_make_it_ambiguous(self, sheet_model):
        campus = self._site(sheet_model, "Campus")
        self._site(sheet_model, "Lot A", parent=campus)
        self._site(sheet_model, "Lot B", parent=campus)
        assert self._data(sheet_model)["SiteName"] == "Campus"

    def test_no_site_or_building_is_blank_not_the_word_None(self, sheet_model):
        data = self._data(sheet_model)
        assert data["SiteAddress"] == ""
        assert data["BuildingName"] == ""

    # --- the link, as a field ------------------------------------------------

    def test_the_link_is_a_choice_labelled_with_what_automatic_gives(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        self._building(sheet_model, site, "South Hall")
        north = self._building(sheet_model, site, "North Hall")
        building, = self._fields(sheet_model, ["Building"])
        assert building["value"] == ""
        assert building["editable"] is True
        assert building["options"][0] == {"value": "", "label": "Automatic (none - more than one to choose from)"}
        # Sorted by name, which is what a person reading the list can see.
        assert [o["label"] for o in building["options"][1:]] == ["North Hall", "South Hall"]

        self._link(sheet_model, north)
        site_field, building = self._fields(sheet_model, ["Site", "Building"])
        assert building["value"] == north.GlobalId
        assert site_field["options"][0]["label"] == "Automatic (Campus)"

    def test_two_with_the_same_name_are_told_apart(self, sheet_model):
        a = self._site(sheet_model, "Lot")
        self._site(sheet_model, "Lot")
        site, = self._fields(sheet_model, ["Site"])
        assert f"Lot ({a.GlobalId})" in [o["label"] for o in site["options"]]

    # --- editing -------------------------------------------------------------

    def test_linking_a_building_replaces_the_last_link(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        north = self._building(sheet_model, site, "North Hall")
        south = self._building(sheet_model, site, "South Hall")
        self._set(sheet_model, {"Building": north.GlobalId})
        self._set(sheet_model, {"Building": south.GlobalId})
        assert sheet_model.builder.get_sheet_links(sheet_model.sheet)["Building"] == south
        assert self._data(sheet_model)["BuildingName"] == "South Hall"
        # The old link is gone, not merely outranked.
        assert [e for r in sheet_model.sheet.DocumentInfoForObjects for e in r.RelatedObjects] == [south]

    def test_an_empty_link_unlinks(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        north = self._building(sheet_model, site, "North Hall")
        self._building(sheet_model, site, "South Hall")
        self._link(sheet_model, north)
        self._set(sheet_model, {"Building": ""})
        assert sheet_model.builder.get_sheet_links(sheet_model.sheet)["Building"] is None

    def test_a_link_to_something_gone_is_refused(self, sheet_model):
        self._site(sheet_model, "Campus")
        with pytest.raises(ValueError, match="no longer in the model"):
            self._set(sheet_model, {"Site": "0000000000000000000000"})

    def test_a_link_to_the_wrong_kind_of_thing_is_refused(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        with pytest.raises(ValueError, match="building is no longer"):
            self._set(sheet_model, {"Building": site.GlobalId})

    def test_an_edit_goes_to_the_linked_building(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        north = self._building(sheet_model, site, "North Hall", Town="Madison")
        south = self._building(sheet_model, site, "South Hall", Town="Verona")
        self._link(sheet_model, south)
        self._set(sheet_model, {"BuildingTown": "Fitchburg", "BuildingAddressLines": "1 Elm St, Unit 2"})
        assert south.BuildingAddress.Town == "Fitchburg"
        # One typed line stays one line; commas in it are not line breaks.
        assert south.BuildingAddress.AddressLines == ("1 Elm St, Unit 2",)
        assert north.BuildingAddress.Town == "Madison"

    def test_linking_and_editing_at_once_edits_the_new_link(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        self._building(sheet_model, site, "North Hall")
        south = self._building(sheet_model, site, "South Hall")
        self._set(sheet_model, {"Building": south.GlobalId, "BuildingDescription": "Classrooms"})
        assert south.Description == "Classrooms"

    def test_an_edit_with_no_building_to_go_to_says_to_pick_one(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        self._building(sheet_model, site, "North Hall")
        self._building(sheet_model, site, "South Hall")
        with pytest.raises(ValueError, match="pick one in its Building list"):
            self._set(sheet_model, {"BuildingTown": "Madison", "Revision": "C"})
        # All or nothing: the sheet's own field was not written either.
        assert sheet_model.sheet.Revision is None

    def test_an_edit_in_a_model_without_a_site_says_so(self, sheet_model):
        with pytest.raises(ValueError, match="no site"):
            self._set(sheet_model, {"SiteName": "Lot 7"})

    def test_an_element_without_an_address_gets_one(self, sheet_model):
        site = self._site(sheet_model, "Lot 7")
        building = self._building(sheet_model, site, "Library")
        self._set(sheet_model, {"SiteTown": "Madison", "BuildingTown": "Madison"})
        assert site.SiteAddress.Purpose == "SITE"
        assert building.BuildingAddress.Town == "Madison"

    def test_clearing_every_part_removes_the_address(self, sheet_model):
        # An IfcPostalAddress with nothing in it breaks WR1.
        site = self._site(sheet_model, "Lot 7", Town="Madison")
        self._set(sheet_model, {"SiteTown": ""})
        assert site.SiteAddress is None
        assert not sheet_model.ifc.by_type("IfcPostalAddress")

    def test_renaming_renames_the_object_and_the_spatial_tree(self, sheet_model, monkeypatch):
        import bonsai.core.spatial
        import bonsai.tool as tool

        site = self._site(sheet_model, "Lot 7")
        obj = object()
        renamed, refreshed = [], []
        monkeypatch.setattr(tool.Ifc, "get_object", classmethod(lambda cls, element: obj))
        monkeypatch.setattr(tool.Root, "set_object_name", classmethod(lambda cls, o, e: renamed.append((o, e))))
        monkeypatch.setattr(bonsai.core.spatial, "import_spatial_decomposition", lambda spatial: refreshed.append(1))

        self._set(sheet_model, {"SiteName": "Lot 8", "SiteDescription": "South parcel"})
        assert (site.Name, site.Description) == ("Lot 8", "South parcel")
        assert renamed == [(obj, site)]
        assert refreshed == [1]

    def test_a_description_alone_leaves_the_object_name_alone(self, sheet_model, monkeypatch):
        import bonsai.tool as tool

        site = self._site(sheet_model, "Lot 7")
        site.Description = "North parcel"
        monkeypatch.setattr(tool.Ifc, "get_object", classmethod(lambda cls, element: pytest.fail("renamed")))
        self._set(sheet_model, {"SiteDescription": ""})
        assert site.Description is None

    def test_the_whole_address_is_read_only_without_a_reason(self, sheet_model):
        # It sits beside its editable parts; saying why would only be noise.
        whole, = self._fields(sheet_model, ["BuildingAddress"])
        assert whole["editable"] is False
        assert "reason" not in whole

    def test_two_linked_buildings_count_as_none(self, sheet_model):
        # IFC keeps the links as a set; taking "the first" would be a guess.
        site = self._site(sheet_model, "Campus")
        north = self._building(sheet_model, site, "North Hall")
        south = self._building(sheet_model, site, "South Hall")
        self._link(sheet_model, north, south)
        assert sheet_model.builder.get_sheet_links(sheet_model.sheet)["Building"] is None
        assert self._data(sheet_model)["BuildingName"] == ""

    def test_a_conflict_shows_as_the_current_value(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        self._link(
            sheet_model,
            self._building(sheet_model, site, "North Hall"),
            self._building(sheet_model, site, "South Hall"),
        )
        building, = self._fields(sheet_model, ["Building"])
        assert building["value"] == "*"
        assert building["options"][0] == {"value": "*", "label": "2 buildings linked - pick one"}

    def test_picking_one_resolves_a_conflict(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        north = self._building(sheet_model, site, "North Hall")
        south = self._building(sheet_model, site, "South Hall")
        self._link(sheet_model, north, south)
        self._set(sheet_model, {"Building": south.GlobalId})
        assert sheet_model.builder.get_all_sheet_links(sheet_model.sheet)["Building"] == [south]

    def test_automatic_resolves_a_conflict_by_unlinking_both(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        self._link(
            sheet_model,
            self._building(sheet_model, site, "North Hall"),
            self._building(sheet_model, site, "South Hall"),
        )
        self._set(sheet_model, {"Building": ""})
        assert sheet_model.builder.get_all_sheet_links(sheet_model.sheet)["Building"] == []

    def test_saving_the_conflict_value_back_changes_nothing(self, sheet_model):
        site = self._site(sheet_model, "Campus")
        north = self._building(sheet_model, site, "North Hall")
        south = self._building(sheet_model, site, "South Hall")
        self._link(sheet_model, north, south)
        self._set(sheet_model, {"Building": "*"})
        assert len(sheet_model.builder.get_all_sheet_links(sheet_model.sheet)["Building"]) == 2

    def test_checking_refuses_without_writing(self, sheet_model):
        # The web handler checks before starting an undoable operator.
        site = self._site(sheet_model, "Campus")
        self._building(sheet_model, site, "North Hall")
        self._building(sheet_model, site, "South Hall")
        with pytest.raises(ValueError, match="pick one in its Building list"):
            sheet_model.builder.check_template_values(
                sheet_model.layout, {"kind": "sheet"}, {"Revision": "C", "BuildingTown": "Madison"}
            )
        assert sheet_model.sheet.Revision is None

    def test_checking_accepts_and_returns_text(self, sheet_model):
        self._site(sheet_model, "Campus")
        values = sheet_model.builder.check_template_values(sheet_model.layout, {"kind": "sheet"}, {"SiteName": None})
        assert values == {"SiteName": ""}

    def test_removing_the_sheet_removes_its_links(self, sheet_model):
        site = self._site(sheet_model, "Lot 7")
        self._link(sheet_model, site)
        ifcopenshell.api.document.remove_information(sheet_model.ifc, information=sheet_model.sheet)
        assert not sheet_model.ifc.by_type("IfcRelAssociatesDocument")
        assert site.HasAssociations == ()
