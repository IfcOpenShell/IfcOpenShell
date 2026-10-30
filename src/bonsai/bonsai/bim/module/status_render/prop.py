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

import bpy
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import PropertyGroup
from bonsai.bim.module.search.prop import BIMFilterGroup
from typing import TYPE_CHECKING


def update_live_preview(self, context):
    """Re-sync the live (viewport) material preview when the toggle or a live effect changes."""
    # Lazy import avoids any import-order coupling with the operator module.
    from bonsai.bim.module.status_render import operator

    if context.scene:
        operator.sync_live_effects(context.scene)


class BIMRenderOverrideRule(PropertyGroup):
    """One selection (filter) plus the render effects applied to it."""

    name: StringProperty(name="Name", default="Rule")
    # Each rule has its own filter, resolved by tool.Search.get_filter_groups(f"status_render_{i}").
    filter_groups: CollectionProperty(type=BIMFilterGroup, name="Filter Groups")
    exposure: FloatProperty(
        name="Exposure",
        description="Extra exposure stops applied to matching elements, on top of the scene's "
        "colour management. 0 = no change",
        default=0.0,
        soft_min=-10.0,
        soft_max=10.0,
    )
    gamma: FloatProperty(
        name="Gamma",
        description="Extra gamma applied to matching elements. 1 = no change",
        default=1.0,
        min=0.001,
        soft_max=5.0,
    )
    transparency: FloatProperty(
        name="Transparency",
        description="Render the matching elements with transparent materials so the geometry "
        "behind them shows through. Shown live in the Rendered viewport while enabled. "
        "0 = opaque, 1 = fully transparent",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        update=update_live_preview,
    )

    if TYPE_CHECKING:
        name: str
        filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]
        exposure: float
        gamma: float
        transparency: float


class BIMRenderOverrideProperties(PropertyGroup):
    """Per-drawing render overrides. Stored on the camera datablock so each drawing
    carries its own rules (registered as ``Camera.BIMRenderOverrideProperties``)."""

    enabled: BoolProperty(
        name="Enable Render Overrides",
        description="While enabled, transparency is shown live in the Rendered viewport, and all "
        "overrides are applied to renders that run the compositor (F12 and Default-render drawing "
        "underlays). Exposure/gamma are render-only (the viewport compositor can't mask them)",
        default=False,
        update=update_live_preview,
    )
    rules: CollectionProperty(type=BIMRenderOverrideRule, name="Rules")
    active_rule_index: IntProperty(name="Active Rule")

    if TYPE_CHECKING:
        enabled: bool
        rules: bpy.types.bpy_prop_collection_idprop[BIMRenderOverrideRule]
        active_rule_index: int
