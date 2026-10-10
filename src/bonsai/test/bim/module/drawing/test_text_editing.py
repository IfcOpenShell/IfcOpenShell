# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 woahwhattheheck <293286387+woahwhattheheck@users.noreply.github.com>
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
#
# This file was generated with the assistance of an AI coding tool.

import glob
import re

import bpy
import ifcopenshell
import pytest
import svgwrite
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing import text_editing
from bonsai.bim.module.drawing.svgwriter import SvgWriter, is_plain_text, parse_markdown_lines
from bonsai.bim.module.drawing.text_editing import NBSP, TextEditBuffer, ViewportTextEdit, handle_key
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.drawing


def type_keys(buffer: TextEditBuffer, *keys: str) -> None:
    for key in keys:
        if len(key) == 1:
            handle_key(buffer, key.upper(), key)
        else:
            handle_key(buffer, key)


class TestTextEditBuffer:
    def test_typing_enter_and_tab(self):
        buffer = TextEditBuffer("")
        type_keys(buffer, "a", "RET", "TAB", "b")
        assert buffer.text == "a\n\tb"
        assert buffer.get_row_column() == (1, 2)

    def test_ctrl_enter_confirms_without_a_new_line(self):
        buffer = TextEditBuffer("a")
        assert handle_key(buffer, "RET", ctrl=True) == "CONFIRM"
        assert handle_key(buffer, "NUMPAD_ENTER", ctrl=True) == "CONFIRM"
        assert handle_key(buffer, "LEFTMOUSE") == "CONFIRM"
        assert buffer.text == "a"

    def test_escape_cancels(self):
        assert handle_key(TextEditBuffer("a"), "ESC") == "CANCEL"
        assert handle_key(TextEditBuffer("a"), "RIGHTMOUSE") == "CANCEL"

    def test_viewport_navigation_passes_through(self):
        buffer = TextEditBuffer("a")
        for key in ("MIDDLEMOUSE", "WHEELUPMOUSE", "MOUSEMOVE", "TRACKPADPAN", "NDOF_MOTION"):
            assert handle_key(buffer, key) == "PASS_THROUGH"
        assert buffer.text == "a"

    def test_ctrl_shortcuts_do_not_type(self):
        buffer = TextEditBuffer("a")
        assert handle_key(buffer, "S", "s", ctrl=True) == "CONTINUE"
        assert buffer.text == "a"

    def test_altgr_characters_are_typed(self):
        buffer = TextEditBuffer("a")
        handle_key(buffer, "Q", "@", ctrl=True, alt=True)
        assert buffer.text == "a@"

    def test_backspace_and_delete(self):
        buffer = TextEditBuffer("ab\ncd", caret=3)
        handle_key(buffer, "BACK_SPACE")
        assert (buffer.text, buffer.caret) == ("abcd", 2)
        handle_key(buffer, "DEL")
        assert (buffer.text, buffer.caret) == ("abd", 2)
        buffer = TextEditBuffer("one two  ")
        handle_key(buffer, "BACK_SPACE", ctrl=True)
        assert buffer.text == "one "
        buffer = TextEditBuffer("one two", caret=0)
        handle_key(buffer, "DEL", ctrl=True)
        assert buffer.text == " two"

    def test_caret_movement(self):
        buffer = TextEditBuffer("first\nab\nthird", caret=4)
        handle_key(buffer, "DOWN_ARROW")
        assert buffer.get_row_column() == (1, 2)
        handle_key(buffer, "DOWN_ARROW")
        assert buffer.get_row_column() == (2, 2)
        handle_key(buffer, "UP_ARROW")
        handle_key(buffer, "UP_ARROW")
        assert buffer.get_row_column() == (0, 2)
        handle_key(buffer, "UP_ARROW")
        assert buffer.caret == 0
        handle_key(buffer, "END")
        assert buffer.caret == 5
        handle_key(buffer, "END", ctrl=True)
        assert buffer.caret == len(buffer.text)
        handle_key(buffer, "HOME")
        assert buffer.get_row_column() == (2, 0)
        handle_key(buffer, "HOME", ctrl=True)
        assert buffer.caret == 0
        handle_key(buffer, "RIGHT_ARROW", ctrl=True)
        assert buffer.caret == 5
        handle_key(buffer, "LEFT_ARROW")
        assert buffer.caret == 4
        handle_key(buffer, "LEFT_ARROW", ctrl=True)
        assert buffer.caret == 0

    def test_paste_normalises_line_breaks(self):
        buffer = TextEditBuffer("")
        handle_key(buffer, "V", ctrl=True, clipboard="a\r\nb\rc")
        assert buffer.text == "a\nb\nc"

    @pytest.mark.parametrize(
        "text, caret, key, expected",
        (
            ("make it bold", 7, "B", "make **it** bold"),
            ("make it bold", 5, "B", "make **it** bold"),
            ("make **it** bold", 11, "B", "make it bold"),
            ("make **it** bold", 7, "I", "make ***it*** bold"),
            ("make ***it*** bold", 8, "B", "make *it* bold"),
            ("make *it* bold", 6, "I", "make it bold"),
            ("", 0, "B", "****"),
            ("a ", 2, "I", "a **"),
        ),
    )
    def test_toggle_emphasis(self, text, caret, key, expected):
        buffer = TextEditBuffer(text, caret=caret)
        handle_key(buffer, key, ctrl=True)
        assert buffer.text == expected

    def test_emphasis_on_empty_place_puts_caret_between_markers(self):
        buffer = TextEditBuffer("a ")
        handle_key(buffer, "B", ctrl=True)
        type_keys(buffer, "x")
        assert buffer.text == "a **x**"

    def test_caret_moves_after_emphasised_word(self):
        buffer = TextEditBuffer("word", caret=2)
        handle_key(buffer, "B", ctrl=True)
        type_keys(buffer, "!")
        assert buffer.text == "**word**!"


class TestWhitespace:
    def test_split_text_lines_accepts_escaped_and_real_line_breaks(self):
        assert text_editing.split_text_lines("a\\nb\nc") == ["a", "b", "c"]

    def test_split_indent(self):
        assert text_editing.split_indent("\tx  y   ") == (4, f"x{NBSP * 2}y")
        assert text_editing.split_indent("ab\tc") == (0, "ab  c".replace("  ", NBSP * 2))

    def test_preserve_whitespace(self):
        assert text_editing.preserve_whitespace("  a b") == f"{NBSP * 2}a b"
        assert text_editing.preserve_whitespace("plain text") == "plain text"


class TestParseMarkdownLines:
    def get_lines(self, text: str) -> list[str]:
        lines = [""]
        for segment in parse_markdown_lines(text_editing.split_text_lines(text)):
            if segment["break"]:
                lines.append("")
            else:
                lines[-1] += segment["text"]
        return lines

    def test_blank_lines_are_kept(self):
        assert self.get_lines("A\n\nB") == ["A", "", "B"]

    def test_indented_lines_are_kept(self):
        assert self.get_lines("A\n\tB\n    C") == ["A", f"{NBSP * 4}B", f"{NBSP * 4}C"]

    def test_lines_are_printed_as_typed(self):
        text = "# 1\n1. First\n2) Second\n> quoted\n---\n```"
        assert self.get_lines(text) == ["# 1", "1. First", "2) Second", "> quoted", "---", "```"]

    def test_bullet_points(self):
        assert self.get_lines("Notes:\n- a\n  - b") == ["Notes:", "\u2022 a", f"{NBSP * 2}\u2022 b"]

    def test_inline_formatting_and_escaped_line_breaks(self):
        segments = parse_markdown_lines(text_editing.split_text_lines("**bold**\\nnext"))
        bold = [s["text"] for s in segments if s["bold"]]
        assert bold == ["bold"]
        assert self.get_lines("**bold**\\nnext") == ["bold", "next"]

    def test_is_plain_text(self):
        def is_plain(text):
            lines = text_editing.split_text_lines(text)
            return is_plain_text(parse_markdown_lines(lines), lines)

        assert is_plain("plain")
        assert is_plain("two\\nlines")
        assert is_plain("tab\tand  spaces")
        assert is_plain("# not a heading")
        assert not is_plain("**bold**")
        assert not is_plain("- bullet")
        assert not is_plain("[link](https://ifcopenshell.org)")


class TestSvgText:
    @pytest.fixture
    def writer(self) -> SvgWriter:
        writer = SvgWriter.__new__(SvgWriter)
        writer.svg = svgwrite.Drawing(debug=False)
        return writer

    def test_plain_text_keeps_tabs_and_indentation(self, writer):
        (text_tag,) = writer.create_text_tag("a\tb\n  c", Vector((0, 0)), text_format=text_editing.preserve_whitespace)
        assert [t.text for t in text_tag.elements] == [f"a{NBSP * 3}b", f"{NBSP * 2}c"]

    def test_markdown_text_continues_after_previous_literal_lines(self, writer):
        lines = text_editing.split_text_lines("**A**\n\nB")
        text_tag, line_count = writer.create_markdown_text_tag(
            parse_markdown_lines(lines), Vector((0, 0)), 0, "bottom-left", "", line_number_start=2
        )
        assert line_count == 3
        tspans = [t for t in text_tag.elements if t.text]
        assert [(t.text, t.attribs.get("dy"), t.attribs.get("font-weight")) for t in tspans] == [
            ("A", "2em", "bold"),
            ("B", "4em", None),
        ]


class TestViewportTextEdit:
    def teardown_method(self):
        ViewportTextEdit.stop()

    def test_caret_is_drawn_only_on_the_edited_literal(self):
        buffer = TextEditBuffer("ab", caret=1)
        ViewportTextEdit.start("Text", 1, buffer)
        assert ViewportTextEdit.is_active()
        assert ViewportTextEdit.get_displayed_text("Text", 1, "ab") == "a|b"
        assert ViewportTextEdit.get_displayed_text("Text", 0, "ab") == "ab"
        assert ViewportTextEdit.get_displayed_text("Other", 1, "ab") == "ab"
        ViewportTextEdit.stop()
        assert not ViewportTextEdit.is_active()
        assert ViewportTextEdit.get_displayed_text("Text", 1, "ab") == "ab"


class TestPrintMultilineText(NewIfc):
    def test_run(self):
        literal = "First line\n\tIndented\n\n**Bold** end\n1. kept"
        tool.Project.save_test_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        ifc_file = tool.Ifc.get()
        drawing = next(a for a in ifc_file.by_type("IfcAnnotation") if a.ObjectType == "DRAWING")
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        bpy.ops.bim.add_annotation()
        obj = bpy.data.objects["IfcAnnotation/TEXT"]
        bpy.context.view_layer.objects.active = obj
        assert bpy.ops.bim.edit_text_in_viewport.poll()

        bpy.ops.bim.enable_editing_text()
        props = tool.Drawing.get_text_props(obj)
        props.literals[0].attributes["Literal"].string_value = literal
        bpy.ops.bim.add_text_literal()
        props.literals[1].attributes["Literal"].string_value = "Second literal"
        bpy.ops.bim.edit_text()

        path = tool.Project.TEMP_PROJECT_PATH.parent / "multiline_text.ifc"
        ifc_file.write(str(path))
        assert literal in [l.Literal for l in ifcopenshell.open(str(path)).by_type("IfcTextLiteral")]

        bpy.ops.bim.create_drawing()
        (svg_path,) = glob.glob(str(tool.Project.TEMP_PROJECT_PATH.parent / "drawings" / "*.svg"))
        with open(svg_path, encoding="utf-8") as f:
            svg = f.read()
        tspans = re.findall(r'<tspan[^>]*?dy="(\d+)em"[^>]*>(.*?)</tspan>', svg)
        assert tspans == [
            ("0", "First line"),
            ("1", NBSP * 4),
            ("3", "Bold"),
            ("4", "1. kept"),
            ("5", "Second literal"),
        ]
        assert "Indented</tspan>" in svg
