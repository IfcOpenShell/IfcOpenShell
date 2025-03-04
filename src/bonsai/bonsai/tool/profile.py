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

from __future__ import annotations
import bpy
import ifcopenshell
import ifcopenshell.api.profile
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.unit
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import numpy as np
import bonsai.core.tool
import bonsai.tool as tool
import PIL.ImageDraw
from bonsai.bim.module.model.decorator import ProfileDecorator
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    import bonsai.bim.module.profile.prop
    from bonsai.bim.module.profile.prop import BIMProfileProperties


class Profile(bonsai.core.tool.Profile):
    @classmethod
    def get_profile_props(cls) -> BIMProfileProperties:
        return bpy.context.scene.BIMProfileProperties

    @classmethod
    def draw_image_for_ifc_profile(
        cls, draw: PIL.ImageDraw.ImageDraw, profile: ifcopenshell.entity_instance, size: float
    ) -> None:
        """generates image based on `profile` using `PIL.ImageDraw`"""
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, profile)

        verts = ifcopenshell.util.shape.get_vertices(shape)
        if verts.size == 0:
            raise RuntimeError(f"Profile shape has no vertices, it probably is invalid: '{profile}'.")

        edges = ifcopenshell.util.shape.get_edges(shape)
        verts_flat = verts.ravel()
        max_x = np.max(verts_flat[0::3]).item()
        min_x = np.min(verts_flat[0::3]).item()
        max_y = np.max(verts_flat[1::3]).item()
        min_y = np.min(verts_flat[1::3]).item()

        dim_x = max_x - min_x
        dim_y = max_y - min_y
        max_dim = max([dim_x, dim_y])
        scale = 100 / max_dim
        dim = np.array([dim_x, dim_y])

        verts = verts[:, :2]
        verts = np.round(scale * (verts - [min_x, min_y]) + (size / 2) - scale * dim / 2)
        for verts_ in verts[edges]:
            # draw.line seem to support only tuple of tuples.
            verts_tuple: tuple[tuple[float, ...], ...]
            verts_tuple = tuple(tuple(i) for i in verts_)
            draw.line(verts_tuple, fill="white", width=2)

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
        new_profile = ifcopenshell.api.profile.copy_profile(tool.Ifc.get(), profile)
        # In UI unnamed profiles are not available, so we don't handle them.
        new_profile.ProfileName = profile.ProfileName + "_copy"
        return new_profile

    @classmethod
    def get_active_profile_ui(cls) -> Union[bonsai.bim.module.profile.prop.Profile, None]:
        props = cls.get_profile_props()
        index = props.active_profile_index
        if len(props.profiles) > index >= 0:
            return props.profiles[index]

    # Lengths are in meters.
    DEFAULT_PROFILE_ATTRS = {
        "IfcCircleProfileDef": {
            "Radius": 0.05,
        },
        # TODO: test after debug
        "IfcAsymmetricIShapeProfileDef": {
            "BottomFlangeWidth": 0.1,
            "BottomFlangeThickness": 0.01,
            "BottomFlangeFilletRadius": 0.01,
            "OverallDepth": 0.1,
            "WebThickness": 0.005,
            "TopFlangeWidth": 0.075,
            "TopFlangeThickness": 0.01,
            "TopFlangeFilletRadius": 0.01,
        },
        "IfcCShapeProfileDef": {
            "Depth": 0.1,
            "Width": 0.05,
            "WallThickness": 0.01,
            "Girth": 0.01,
        },
        # 101.6-10.0
        "IfcCircleHollowProfileDef": {
            "WallThickness": 0.01,
        },
        "IfcEllipseProfileDef": {
            "SemiAxis1": 0.15,
            "SemiAxis2": 0.1,
        },
        # HEA100
        "IfcIShapeProfileDef": {
            "OverallWidth": 0.1,
            "OverallDepth": 0.1,
            "WebThickness": 0.005,
            "FlangeThickness": 0.01,
            "FilletRadius": 0.01,
        },
        # LNP100x10
        "IfcLShapeProfileDef": {
            "Depth": 0.1,
            "Thickness": 0.01,
            "FilletRadius": 0.012,
            "EdgeRadius": 0.01,
        },
        "IfcRectangleProfileDef": {
            "XDim": 0.1,
            "YDim": 0.1,
        },
        "IfcRoundedRectangleProfileDef": {
            "RoundingRadius": 0.01,
        },
        # 100-10.0
        "IfcRectangleHollowProfileDef": {
            "WallThickness": 0.01,
            "InnerFilletRadius": 0.01,
            "OuterFilletRadius": 0.01,
        },
        "IfcTShapeProfileDef": {
            "Depth": 0.1,
            "FlangeWidth": 0.05,
            "WebThickness": 0.005,
            "FlangeThickness": 0.009,
        },
        "IfcTrapeziumProfileDef": {
            "BottomXDim": 0.1,
            "TopXDim": 0.08,
            "YDim": 0.05,
            "TopXOffset": 0.01,
        },
        # UAP100
        "IfcUShapeProfileDef": {
            "Depth": 0.1,
            "FlangeWidth": 0.05,
            "WebThickness": 0.005,
            "FlangeThickness": 0.009,
        },
        # ZNP100
        "IfcZShapeProfileDef": {
            "Depth": 0.1,
            "FlangeWidth": 0.05,
            "WebThickness": 0.007,
            "FlangeThickness": 0.01,
        },
    }

    @classmethod
    def set_default_profile_attrs(cls, profile: ifcopenshell.entity_instance) -> None:
        """Set default profile attributes to keep profile valid."""
        class_match = False
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for ifc_class, params in cls.DEFAULT_PROFILE_ATTRS.items():
            if profile.is_a(ifc_class):
                class_match = True
                for key, value in params.items():
                    setattr(profile, key, value / si_conversion)

        if not class_match:
            raise ValueError(f"Unable to set default profile parameters for {profile.is_a()}.")
