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

"""No bpy or mathutils dependency: this module is deliberately pure so it can
run under plain pytest, without a Blender instance."""

from pathlib import Path

from bonsai.bim.module.drawing.font_resolver import (
    find_font_in_directories,
    find_system_font,
    system_font_directories,
)


class TestSystemFontDirectories:
    def test_windows_only_checks_the_windows_fonts_folder(self):
        dirs = system_font_directories("Windows")
        assert dirs == [Path("C:\\Windows") / "Fonts"]

    def test_darwin_includes_user_and_system_font_folders(self):
        dirs = system_font_directories("Darwin")
        assert Path("/System/Library/Fonts") in dirs
        assert Path("/Library/Fonts") in dirs
        assert (Path.home() / "Library" / "Fonts") in dirs

    def test_linux_includes_user_and_system_font_folders(self):
        dirs = system_font_directories("Linux")
        assert Path("/usr/share/fonts") in dirs
        assert (Path.home() / ".fonts") in dirs


class TestFindFontInDirectories:
    def test_finds_a_font_directly_inside_a_search_dir(self, tmp_path):
        font_dir = tmp_path / "Fonts"
        font_dir.mkdir()
        font_file = font_dir / "MyScandinavianFont.ttf"
        font_file.write_bytes(b"fake-ttf-data")

        result = find_font_in_directories("MyScandinavianFont.ttf", [font_dir])

        assert result == font_file

    def test_finds_a_font_nested_in_a_subfolder(self, tmp_path):
        font_dir = tmp_path / "Fonts"
        nested = font_dir / "Collections" / "Vendor"
        nested.mkdir(parents=True)
        font_file = nested / "MyScandinavianFont.ttf"
        font_file.write_bytes(b"fake-ttf-data")

        result = find_font_in_directories("MyScandinavianFont.ttf", [font_dir])

        assert result == font_file

    def test_returns_none_when_not_found(self, tmp_path):
        font_dir = tmp_path / "Fonts"
        font_dir.mkdir()

        result = find_font_in_directories("Missing.ttf", [font_dir])

        assert result is None

    def test_skips_a_search_dir_that_does_not_exist(self, tmp_path):
        missing_dir = tmp_path / "does-not-exist"

        result = find_font_in_directories("Anything.ttf", [missing_dir])

        assert result is None

    def test_empty_font_name_returns_none(self, tmp_path):
        assert find_font_in_directories("", [tmp_path]) is None


class TestFindSystemFont:
    def test_reproduces_the_reported_bug_font_not_found_on_macos(self, monkeypatch, tmp_path):
        """This is the exact regression: before the fix, the fallback search only
        checked Windows font directories, so any Mac (or Linux) user whose
        chosen font was not in Bonsai's bundled fonts folder got no font at
        all, even though the font was sitting right there on their system."""
        mac_fonts_dir = tmp_path / "Library" / "Fonts"
        mac_fonts_dir.mkdir(parents=True)
        font_file = mac_fonts_dir / "OpenGOSTtypeA-Regular.ttf"
        font_file.write_bytes(b"fake-ttf-data")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        result = find_system_font("OpenGOSTtypeA-Regular.ttf", system="Darwin")

        assert result == font_file
