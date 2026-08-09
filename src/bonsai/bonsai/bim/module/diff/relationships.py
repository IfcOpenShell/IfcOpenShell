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

"""Relationship-set constants for the Diff panel. Deliberately bpy-free so
the default relationship set can be unit tested without Blender."""

# ifcdiff.IfcDiff defaults to checking these two relationships when no
# relationships are given at all (see ifcdiff.py's IfcDiff.__init__). The
# Diff panel pre-populates its relationship list with the same two, so that
# adding another relationship (eg. "property") in the UI is additive, not a
# replacement that silently stops attribute and geometry changes (eg. a
# cleared PredefinedType or a changed mesh) from being reported.
DEFAULT_RELATIONSHIPS = ("attributes", "geometry")
