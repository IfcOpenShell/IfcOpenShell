# This file was generated with the assistance of an AI coding tool.
import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.drawing.ui import BIM_UL_drawinglist, BIM_UL_sheets
from test.bim.bootstrap import NewFile

BIT = 1 << 30


class FakeList:
    filter_name = ""
    bitflag_filter_item = BIT
    use_filter_sort_reverse = False


def visible(flags, collection):
    return [item.name for item, flag in zip(collection, flags) if flag & BIT]


def make_drawing(ifc, name, target_view):
    drawing = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcAnnotation", name=name)
    drawing.ObjectType = "DRAWING"
    pset = ifcopenshell.api.pset.add_pset(ifc, product=drawing, name="EPset_Drawing")
    ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"TargetView": target_view})
    return drawing


class TestDrawingListSelectedOnly(NewFile):
    def load(self, views):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        for name, view in views:
            make_drawing(ifc, name, view)
        tool.Drawing.import_drawings()
        props = tool.Drawing.get_document_props()
        for item in props.drawings:
            if not item.is_drawing:
                item.is_expanded = True
        tool.Drawing.import_drawings()
        return props

    def test_only_checked_drawings_and_their_headers_are_shown(self):
        props = self.load([("A", "PLAN_VIEW"), ("B", "PLAN_VIEW"), ("C", "SECTION_VIEW")])
        for item in props.drawings:
            if item.name in ("B", "C"):
                item.is_selected = False
        props.show_selected_drawings_only = True
        flags, _ = BIM_UL_drawinglist.filter_items(FakeList(), bpy.context, props, "drawings")
        assert visible(flags, props.drawings) == ["Plan View (2)", "A"]

    def test_all_items_are_shown_when_the_toggle_is_off(self):
        props = self.load([("A", "PLAN_VIEW"), ("B", "PLAN_VIEW")])
        props.drawings[1].is_selected = False
        flags, _ = BIM_UL_drawinglist.filter_items(FakeList(), bpy.context, props, "drawings")
        assert len(visible(flags, props.drawings)) == len(props.drawings)


class TestSheetListSelectedOnly(NewFile):
    def test_only_checked_sheets_are_shown(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        for identification in ("A1", "A2"):
            ifc.createIfcDocumentInformation(Identification=identification, Name="Sheet", Scope="SHEET")
        tool.Drawing.import_sheets()
        props = tool.Drawing.get_document_props()
        props.sheets[1].is_selected = False
        props.show_selected_sheets_only = True
        flags, _ = BIM_UL_sheets.filter_items(FakeList(), bpy.context, props, "sheets")
        assert [props.sheets[i].identification for i, f in enumerate(flags) if f & BIT] == ["A1"]
