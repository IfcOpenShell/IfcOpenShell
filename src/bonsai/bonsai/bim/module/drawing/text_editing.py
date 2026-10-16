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

"""Typing text annotations directly in the viewport, see #6427.

Everything here is plain Python so it can be tested without Blender: the caret based
edit buffer, the mapping from key presses to edits, and the helpers that keep line
breaks, tabs and indentation intact when a literal is printed.
"""

import re
from typing import Literal, Optional

TAB_SIZE = 4
NBSP = "\u00a0"
CARET = "|"

KeyResult = Literal["CONTINUE", "CONFIRM", "CANCEL", "PASS_THROUGH"]

# Events that keep navigating the viewport while a literal is being typed.
PASS_THROUGH_EVENTS = {
    "MIDDLEMOUSE",
    "WHEELUPMOUSE",
    "WHEELDOWNMOUSE",
    "WHEELINMOUSE",
    "WHEELOUTMOUSE",
    "MOUSEMOVE",
    "INBETWEEN_MOUSEMOVE",
    "TRACKPADPAN",
    "TRACKPADZOOM",
    "MOUSEROTATE",
    "MOUSESMARTZOOM",
    "TIMER",
    "TIMER_REPORT",
    "WINDOW_DEACTIVATE",
}


def split_text_lines(text: str) -> list[str]:
    """Split a literal into printed lines.

    Both real line breaks and the older ``\\n`` escape sequence start a new line.
    """
    return text.replace("\\n", "\n").split("\n")


def expand_tabs(line: str) -> str:
    return line.expandtabs(TAB_SIZE)


def split_indent(line: str) -> tuple[int, str]:
    """Return the indentation width of a printed line and the rest of it.

    Tabs are expanded and trailing spaces dropped. Runs of spaces inside the rest
    become non-breaking spaces, as SVG would otherwise collapse them into one.
    """
    line = expand_tabs(line).rstrip(" ")
    body = line.lstrip(" ")
    return len(line) - len(body), re.sub(r" {2,}", lambda m: NBSP * len(m.group()), body)


def preserve_whitespace(line: str) -> str:
    """Keep the tabs, indentation and repeated spaces of a line when it is printed to SVG."""
    indent, body = split_indent(line)
    return NBSP * indent + body


# Block level markdown that would otherwise eat the characters a user typed at the start
# of a line: headings, quotes, numbered lists, horizontal rules and code fences.
BLOCK_MARKDOWN = re.compile(r"^(#{1,6}(?=\s|$)|>|\d{1,9}(?=[.)](?:\s|$))|(?:[-*_]\s*){3,}$|`{3,}|~{3,})")


def escape_block_markdown(line: str) -> str:
    """Keep a line as written, only bullet points and inline formatting are interpreted."""
    match = BLOCK_MARKDOWN.match(line)
    if not match:
        return line
    if match.group(0)[0].isdigit():
        number = match.group(0)
        return number + "\\" + line[len(number) :]
    return "\\" + line


class TextEditBuffer:
    """A literal being typed, with a caret given as an index into the text."""

    def __init__(self, text: str = "", caret: Optional[int] = None):
        self.text = text
        self.caret = len(text) if caret is None else max(0, min(caret, len(text)))

    def get_row_column(self) -> tuple[int, int]:
        before = self.text[: self.caret]
        row = before.count("\n")
        return row, len(before) - (before.rfind("\n") + 1)

    def get_line_start(self, position: Optional[int] = None) -> int:
        position = self.caret if position is None else position
        return self.text.rfind("\n", 0, position) + 1

    def get_line_end(self, position: Optional[int] = None) -> int:
        position = self.caret if position is None else position
        end = self.text.find("\n", position)
        return len(self.text) if end == -1 else end

    def insert(self, value: str) -> None:
        value = value.replace("\r\n", "\n").replace("\r", "\n")
        self.text = self.text[: self.caret] + value + self.text[self.caret :]
        self.caret += len(value)

    def backspace(self, word: bool = False) -> None:
        start = self.find_word_start() if word else max(0, self.caret - 1)
        self.text = self.text[:start] + self.text[self.caret :]
        self.caret = start

    def delete(self, word: bool = False) -> None:
        end = self.find_word_end() if word else min(len(self.text), self.caret + 1)
        self.text = self.text[: self.caret] + self.text[end:]

    def move_left(self, word: bool = False) -> None:
        self.caret = self.find_word_start() if word else max(0, self.caret - 1)

    def move_right(self, word: bool = False) -> None:
        self.caret = self.find_word_end() if word else min(len(self.text), self.caret + 1)

    def move_home(self, document: bool = False) -> None:
        self.caret = 0 if document else self.get_line_start()

    def move_end(self, document: bool = False) -> None:
        self.caret = len(self.text) if document else self.get_line_end()

    def move_up(self) -> None:
        line_start = self.get_line_start()
        if line_start == 0:
            self.caret = 0
            return
        column = self.caret - line_start
        previous_start = self.get_line_start(line_start - 1)
        self.caret = min(previous_start + column, line_start - 1)

    def move_down(self) -> None:
        line_end = self.get_line_end()
        if line_end == len(self.text):
            self.caret = line_end
            return
        column = self.caret - self.get_line_start()
        next_start = line_end + 1
        self.caret = min(next_start + column, self.get_line_end(next_start))

    def find_word_start(self) -> int:
        i = self.caret
        while i > 0 and self.text[i - 1].isspace():
            i -= 1
        while i > 0 and not self.text[i - 1].isspace():
            i -= 1
        return i

    def find_word_end(self) -> int:
        i = self.caret
        while i < len(self.text) and self.text[i].isspace():
            i += 1
        while i < len(self.text) and not self.text[i].isspace():
            i += 1
        return i

    def toggle_bold(self) -> None:
        self.toggle_emphasis(2)

    def toggle_italic(self) -> None:
        self.toggle_emphasis(1)

    def toggle_emphasis(self, weight: int) -> None:
        """Toggle markdown bold (weight 2) or italic (weight 1) on the word at the caret.

        Without a word at the caret, an empty pair of markers is inserted to type into.
        """
        if not (word := self.find_emphasis_word()):
            markers = "*" * weight
            self.insert(markers + markers)
            self.caret -= weight
            return
        start, end = word
        before = len(self.text[:start]) - len(self.text[:start].rstrip("*"))
        after = len(self.text[end:]) - len(self.text[end:].lstrip("*"))
        current = min(before, after, 3)
        # Bold uses two asterisks, italic one and both together three.
        has_weight = current in ((2, 3) if weight == 2 else (1, 3))
        new = current - weight if has_weight else current + weight
        markers = "*" * new
        self.text = self.text[: start - current] + markers + self.text[start:end] + markers + self.text[end + current :]
        self.caret = start - current + len(markers) + (end - start) + len(markers)

    def find_emphasis_word(self) -> Optional[tuple[int, int]]:
        def is_word_character(character: str) -> bool:
            return not character.isspace() and character != "*"

        text = self.text
        i = self.caret
        while i > 0 and text[i - 1] == "*":
            i -= 1
        if i > 0 and is_word_character(text[i - 1]):
            end = i
            start = end
            while start > 0 and is_word_character(text[start - 1]):
                start -= 1
            while end < len(text) and is_word_character(text[end]):
                end += 1
            return start, end
        j = self.caret
        while j < len(text) and text[j] == "*":
            j += 1
        if j < len(text) and is_word_character(text[j]):
            start = end = j
            while end < len(text) and is_word_character(text[end]):
                end += 1
            return start, end
        return None

    def get_text_with_caret(self) -> str:
        return self.text[: self.caret] + CARET + self.text[self.caret :]


def handle_key(
    buffer: TextEditBuffer,
    key: str,
    unicode: str = "",
    ctrl: bool = False,
    alt: bool = False,
    clipboard: str = "",
) -> KeyResult:
    """Apply one key press to the buffer and say whether typing goes on."""
    if key in PASS_THROUGH_EVENTS or key.startswith("NDOF_"):
        return "PASS_THROUGH"
    if key in {"ESC", "RIGHTMOUSE"}:
        return "CANCEL"
    if key == "LEFTMOUSE":
        return "CONFIRM"
    if key in {"RET", "NUMPAD_ENTER"}:
        if ctrl:
            return "CONFIRM"
        buffer.insert("\n")
    elif key == "TAB":
        buffer.insert("\t")
    elif key == "BACK_SPACE":
        buffer.backspace(word=ctrl)
    elif key == "DEL":
        buffer.delete(word=ctrl)
    elif key == "LEFT_ARROW":
        buffer.move_left(word=ctrl)
    elif key == "RIGHT_ARROW":
        buffer.move_right(word=ctrl)
    elif key == "UP_ARROW":
        buffer.move_up()
    elif key == "DOWN_ARROW":
        buffer.move_down()
    elif key == "HOME":
        buffer.move_home(document=ctrl)
    elif key == "END":
        buffer.move_end(document=ctrl)
    elif ctrl and not alt and key == "B":
        buffer.toggle_bold()
    elif ctrl and not alt and key == "I":
        buffer.toggle_italic()
    elif ctrl and not alt and key == "V":
        buffer.insert(clipboard)
    elif unicode and unicode.isprintable() and (alt or not ctrl):
        # AltGr is reported as Ctrl+Alt and types characters such as @ on many layouts.
        buffer.insert(unicode)
    return "CONTINUE"


class ViewportTextEdit:
    """The literal currently being typed in the viewport, so the decorator can draw a caret."""

    obj_name: Optional[str] = None
    literal_index: int = 0
    buffer: Optional[TextEditBuffer] = None

    @classmethod
    def start(cls, obj_name: str, literal_index: int, buffer: TextEditBuffer) -> None:
        cls.obj_name = obj_name
        cls.literal_index = literal_index
        cls.buffer = buffer

    @classmethod
    def stop(cls) -> None:
        cls.obj_name = None
        cls.literal_index = 0
        cls.buffer = None

    @classmethod
    def is_active(cls) -> bool:
        return cls.buffer is not None

    @classmethod
    def get_displayed_text(cls, obj_name: str, literal_index: int, text: str) -> str:
        """Return the literal text to draw, with a caret if it is the one being typed."""
        if cls.buffer is None or cls.obj_name != obj_name or cls.literal_index != literal_index:
            return text
        if cls.buffer.text != text:
            return text
        return cls.buffer.get_text_with_caret()
