# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 @Andrej730
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import blenderbim.core.tool


class Profile(blenderbim.core.tool.Profile):
    @classmethod
    def draw_image_for_ifc_profile(cls, draw, profile, size):
        """generates image based on `profile` using `PIL.ImageDraw`"""
        settings = ifcopenshell.geom.settings()
        settings.set(settings.INCLUDE_CURVES, True)
        shape = ifcopenshell.geom.create_shape(settings, profile)
        verts = shape.verts
        edges = shape.edges

        grouped_verts = [[verts[i], verts[i + 1]] for i in range(0, len(verts), 3)]
        grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

        max_x = max([v[0] for v in grouped_verts])
        min_x = min([v[0] for v in grouped_verts])
        max_y = max([v[1] for v in grouped_verts])
        min_y = min([v[1] for v in grouped_verts])

        dim_x = max_x - min_x
        dim_y = max_y - min_y
        max_dim = max([dim_x, dim_y])
        scale = 100 / max_dim

        for vert in grouped_verts:
            vert[0] = round(scale * (vert[0] - min_x)) + ((size / 2) - scale * (dim_x / 2))
            vert[1] = round(scale * (vert[1] - min_y)) + ((size / 2) - scale * (dim_y / 2))

        for e in grouped_edges:
            draw.line((tuple(grouped_verts[e[0]]), tuple(grouped_verts[e[1]])), fill="white", width=2)
