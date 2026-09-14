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

"""Relationship-set helpers for the Diff panel. Deliberately bpy-free so this
logic can be unit tested without Blender."""

from collections.abc import Sequence

# ifcdiff.IfcDiff defaults to checking these two relationships when no
# relationships are given at all (see ifcdiff.py's IfcDiff.__init__).
DEFAULT_RELATIONSHIPS = ("attributes", "geometry")


def get_skipped_default_relationships(selected: Sequence[str]) -> list[str]:
    """Which of DEFAULT_RELATIONSHIPS are silently NOT compared given the
    user's ``selected`` relationships.

    An empty ``selected`` list makes ifcdiff.IfcDiff apply its own default
    (attributes and geometry), so nothing is skipped. A non-empty list is
    used by ifcdiff exactly as given: if the user picked other relationships
    (eg. "property") without also picking "attributes"/"geometry", those two
    are silently skipped. This is the trap fixed here: callers should report
    the result of this function to the user instead of guessing what they
    meant."""
    if not selected:
        return []
    return [r for r in DEFAULT_RELATIONSHIPS if r not in selected]
