# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 @Andrej730
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

import ifcopenshell
import ifcopenshell.api.profile
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.unit
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import bonsai.core.tool
import bonsai.tool as tool
import PIL.ImageDraw
from bonsai.bim.module.model.decorator import ProfileDecorator
from typing import Union


class Profile(bonsai.core.tool.Profile):
    @classmethod
    def draw_image_for_ifc_profile(
        cls, draw: PIL.ImageDraw.ImageDraw, profile: ifcopenshell.entity_instance, size: float
    ) -> None:
        """generates image based on `profile` using `PIL.ImageDraw`"""
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
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

    @classmethod
    def is_editing_profile(cls) -> bool:
        return bool(ProfileDecorator.installed)

    @classmethod
    def get_profile(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        representations = element.Representation
        for representation in representations.Representations:
            if not representation.is_a("IfcShapeRepresentation"):
                continue
            for representation_item in representation.Items:
                if representation_item.is_a("IfcExtrudedAreaSolid"):
                    profile = representation_item.SweptArea
                    if profile:
                        return profile
        return None

    @classmethod
    def get_default_profile(cls) -> ifcopenshell.entity_instance:
        """Return first found IfcProfileDef in IFC file or create a new default profile."""
        ifc_file = tool.Ifc.get()
        profile = next(iter(ifc_file.by_type("IfcProfileDef")), None)
        if profile:
            return profile
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc_file, ifc_class="IfcRectangleProfileDef")
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        profile.ProfileType = "AREA"
        profile.ProfileName = "Default Profile"
        profile.XDim = 0.1 / si_conversion
        profile.YDim = 0.1 / si_conversion
        return profile

    @classmethod
    def get_model_profiles(cls) -> list[ifcopenshell.entity_instance]:
        return tool.Ifc.get().by_type("IfcProfileDef")

    @classmethod
    def duplicate_profile(cls, profile: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        new_profile = ifcopenshell.util.element.copy_deep(tool.Ifc.get(), profile)
        # In UI unnamed profiles are not available, so we don't handle them.
        new_profile.ProfileName = profile.ProfileName + "_copy"
        return new_profile
