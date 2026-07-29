# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

"""Regression test for the Covering Tool's "Load Thumbnails" button never
being replaced by the actual thumbnail once it loads.

``CoveringToolUI.draw_basic_bim_tool_interface`` in
``bim/module/covering/workspace.py`` used to gate the thumbnail preview on
``AuthoringData.data["relating_type_data"].get("thumbnail")``. But
``AuthoringData.get_type_data()`` (which builds ``relating_type_data``) never
sets a ``"thumbnail"`` key -- it sets ``"icon_id"`` instead, computed once at
``AuthoringData.load()`` time. So the ``.get("thumbnail")`` read was always
``None`` and the box permanently showed the "Load Thumbnails" operator
button, even after clicking it: ``bim.load_type_thumbnails`` updates
``AuthoringData.type_thumbnails`` directly without forcing a full
``AuthoringData.load()``, so the cached ``relating_type_data`` dict (and its
now-fixed ``"icon_id"`` entry) stays stale across the redraw that follows.

This was introduced by commit b49cc6c5e9 ("AuthoringData.data
['relating_type_data']"), which collapsed the old, always-fresh
``AuthoringData.data["type_thumbnail"]`` field into ``relating_type_data``
but updated the covering workspace consumer to read the wrong key.

The fix reads ``AuthoringData.type_thumbnails`` directly (keyed by the
relating type's id), the same live-lookup pattern already used by
``bim/module/model/workspace.py`` and ``bim/module/model/ui.py`` for the
identical purpose."""

import ifcopenshell
import ifcopenshell.api.root
import pytest

pytestmark = pytest.mark.covering


def test_get_type_data_never_sets_a_thumbnail_key():
    from bonsai.bim.module.model.data import AuthoringData

    f = ifcopenshell.file(schema="IFC4")
    covering_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcCoveringType", name="TestCoveringType")
    AuthoringData.type_thumbnails = {covering_type.id(): 99}

    relating_type_data = AuthoringData.get_type_data(covering_type)

    assert relating_type_data.get("thumbnail") is None, (
        "get_type_data() must never populate a 'thumbnail' key; a consumer reading "
        "relating_type_data.get('thumbnail') always gets None, even once a thumbnail "
        "has been loaded"
    )
    assert relating_type_data["id"] == covering_type.id()


def test_type_thumbnails_lookup_by_relating_type_id_reflects_loaded_thumbnail():
    from bonsai.bim.module.model.data import AuthoringData

    f = ifcopenshell.file(schema="IFC4")
    covering_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcCoveringType", name="TestCoveringType")

    # Before "Load Thumbnails" is clicked, nothing is registered yet.
    AuthoringData.type_thumbnails = {}
    relating_type_data = AuthoringData.get_type_data(covering_type)
    thumbnail = AuthoringData.type_thumbnails.get(relating_type_data["id"], 0)
    assert thumbnail == 0, "no thumbnail loaded yet, the Load Thumbnails button must stay visible"

    # bim.load_type_thumbnails populates AuthoringData.type_thumbnails directly,
    # without forcing a full AuthoringData.load() / relating_type_data rebuild.
    AuthoringData.type_thumbnails[covering_type.id()] = 42

    # covering/workspace.py must look the icon up live via type_thumbnails
    # (keyed by relating_type_data["id"]) so the preview appears on the very
    # next redraw, matching bim/module/model/workspace.py's draw_thumbnail().
    thumbnail = AuthoringData.type_thumbnails.get(relating_type_data["id"], 0)
    assert thumbnail == 42, (
        "once bim.load_type_thumbnails runs, covering/workspace.py's lookup via "
        "AuthoringData.type_thumbnails must reflect the loaded icon immediately, "
        "without requiring AuthoringData to be fully reloaded"
    )
