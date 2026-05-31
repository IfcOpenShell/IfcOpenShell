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

"""Side-effect-free slab helpers — IFC reads for LAYER3 extrusions.

Exposes ``read_geometry``: a single live read of the parametric attributes
(extrusion depth and slope) that drive icon placement and dimension display
on a LAYER3 slab. Lives in ``tool/`` so bim-layer callers can stay
declarative — they get a dict, not an IFC walk."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import ifcopenshell.util.unit

import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    import bpy


class SlabGeometry(TypedDict):
    depth: float
    x_angle: float


class Slab(bonsai.core.tool.Slab):
    @classmethod
    def read_geometry(cls, obj: bpy.types.Object) -> SlabGeometry | None:
        """Live-read slab parametric geometry as a dict, or ``None`` if the
        object is not a LAYER3 extruded slab.

        Returned keys (all SI units): ``depth`` (extrusion thickness along the
        slab's local Z), ``x_angle`` (slope in radians; zero for level slabs).

        The slope is encoded in ``obj.matrix_world`` as a post-rotation, so
        callers projecting world points into slab-local space via
        ``mw.inverted()`` will see a level frame whose Z runs along the slab
        thickness — ``x_angle`` is reported for callers that need the slope
        as a scalar but is already applied by the placement."""
        element = tool.Ifc.get_entity(obj)
        if not element or not tool.Blender.Modifier.is_slab(element):
            return None
        representation = tool.Geometry.get_body_representation(element)
        if not representation:
            return None
        extrusion = tool.Model.get_extrusion(representation)
        if not extrusion:
            return None
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        x_angle = tool.Model.get_existing_x_angle(extrusion)
        return {
            "depth": extrusion.Depth * unit_scale,
            "x_angle": x_angle,
        }
