# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

"""Scope raw CSS text from an embedded drawing SVG to a per drawing prefix.

Deliberately dependency free (no bpy, no bonsai imports) so it stays unit
testable without Blender. Handles comments, quoted strings and at-rule
preludes correctly, unlike a plain character scan, so it does not need to
assume the CSS has no braces outside of rule blocks.
"""

import re

__all__ = ["replace_css_urls", "scope_css_rules"]


def replace_css_urls(text: str, prefix: str) -> str:
    """Rewrite `url(#marker)` references to `url(#prefix-marker)`.

    `url(#marker.prefix)` does not work, so the prefix is joined with a dash.
    """
    return re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}-\1)", text)


def _split_top_level(selector_list: str, separator: str) -> list[str]:
    """Split on `separator`, ignoring occurrences nested inside parentheses,
    brackets or quotes.

    Needed for selectors like `:is(.a, .b)` where the comma is part of the
    functional pseudo-class argument list, and for `[data-x='a,b']` where the
    comma is part of an attribute value, neither being a selector separator.
    """
    parts = []
    buffer = ""
    depth = 0
    quote = None
    for char in selector_list:
        if quote is not None:
            buffer += char
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
            buffer += char
            continue
        if char in "([":
            depth += 1
        elif char in ")]":
            depth = max(depth - 1, 0)
        if char == separator and depth == 0:
            parts.append(buffer)
            buffer = ""
        else:
            buffer += char
    parts.append(buffer)
    return parts


def scope_css_rules(style_data: str, prefix: str) -> str:
    """Append `.prefix` to every selector of every top level CSS rule.

    Comments and quoted strings are copied through untouched, so a brace
    inside `content: "{"` or inside `/* like this { */` no longer desyncs
    the brace counter and silently drops the scoping of the rules that
    follow. At-rule preludes (`@media (...)`, `@font-face`, ...) are left
    alone rather than being corrupted into `@media (...).prefix`, since they
    are not selectors. Nested rules inside an at-rule block (e.g. inside
    `@media`) are still not individually scoped, matching prior behaviour.
    """
    text = ""
    depth = 0
    i = 0
    n = len(style_data)

    while i < n:
        char = style_data[i]

        if style_data.startswith("/*", i):
            end = style_data.find("*/", i + 2)
            end = n if end == -1 else end + 2
            text += style_data[i:end]
            i = end
            continue

        if char in "\"'":
            quote = char
            j = i + 1
            while j < n:
                if style_data[j] == "\\":
                    j += 2
                    continue
                if style_data[j] == quote:
                    j += 1
                    break
                j += 1
            text += style_data[i:j]
            i = j
            continue

        if char == "{":
            if depth == 0:
                last_close = text.rfind("}")
                head = text[: last_close + 1] if last_close != -1 else ""
                prelude = text[last_close + 1 :] if last_close != -1 else text
                if prelude.strip().startswith("@"):
                    text = head + prelude
                else:
                    selectors = []
                    for selector in _split_top_level(prelude, ","):
                        selector = selector.strip()
                        if selector:
                            selectors.append(f"{selector}.{prefix}")
                    text = head + ", ".join(selectors) + " "
            depth += 1
            text += char
            i += 1
            continue

        if char == "}":
            depth = max(depth - 1, 0)
            text += char
            i += 1
            continue

        text += char
        i += 1

    return replace_css_urls(text, prefix)
