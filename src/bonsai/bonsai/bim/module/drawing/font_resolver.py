# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bonsai contributors
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
# This file was written with the assistance of an AI coding tool.

"""Cross-platform lookup for a drawing font that is not bundled with Bonsai.

Bonsai ships a single default annotation font (OpenGost Type B TT), which does
not cover every Latin-script glyph (for example Scandinavian letters such as
AE/OE/AA, umlauts, etc). Users who need those glyphs can point the "Drawing
Font" preference at any TrueType/OpenType font already installed on their
system. This module contains the OS-aware search logic in isolation from bpy
so it can be unit tested without a running Blender instance.
"""

from __future__ import annotations

import os
import platform
from collections.abc import Iterable
from pathlib import Path
from typing import Optional


def system_font_directories(system: Optional[str] = None) -> list[Path]:
    """Return the conventional font install directories for an OS.

    `system` defaults to the live `platform.system()` value ("Windows",
    "Darwin", "Linux", ...) and is otherwise accepted as a parameter purely
    so this can be unit tested for every OS from any host.
    """
    system = system if system is not None else platform.system()
    if system == "Windows":
        return [Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"]
    if system == "Darwin":
        return [
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path.home() / "Library" / "Fonts",
        ]
    # Linux and other unix-likes.
    return [
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".fonts",
        Path.home() / ".local" / "share" / "fonts",
    ]


def find_font_in_directories(font_name: str, search_dirs: Iterable[Path]) -> Optional[Path]:
    """Search `search_dirs` (including subfolders) for a file named `font_name`."""
    if not font_name:
        return None
    for font_dir in search_dirs:
        if not font_dir.is_dir():
            continue
        candidate = font_dir / font_name
        if candidate.is_file():
            return candidate
        for match in font_dir.rglob(font_name):
            if match.is_file():
                return match
    return None


def find_system_font(font_name: str, system: Optional[str] = None) -> Optional[Path]:
    """Search this OS's conventional font directories for `font_name`."""
    return find_font_in_directories(font_name, system_font_directories(system))
