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
import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.attribute
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.profile.data import ProfileData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def get_profile_classes(self, context):
    if not ProfileData.is_loaded:
        ProfileData.load()
    return ProfileData.data["profile_classes"]


def update_profile_name(self: "Profile", context: bpy.types.Context) -> None:
    profile = tool.Ifc.get().by_id(self.ifc_definition_id)
    profile.ProfileName = self.name


class Profile(PropertyGroup):
    name: StringProperty(name="Name", update=update_profile_name)
    ifc_class: StringProperty(name="IFC Class")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


def update_active_profile_index(self, context):
    ProfileData.data["active_profile_users"] = ProfileData.active_profile_users()


class BIMProfileProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    profiles: CollectionProperty(name="Profiles", type=Profile)
    active_profile_index: IntProperty(name="Active Profile Index", update=update_active_profile_index)
    active_profile_id: IntProperty(name="Active Profile Id")
    active_arbitrary_profile_id: IntProperty(name="Active Arbitrary Profile Id")
    profile_attributes: CollectionProperty(name="Profile Attributes", type=Attribute)
    profile_classes: EnumProperty(items=get_profile_classes, name="Profile Classes")
    is_filtering_material_profiles: bpy.props.BoolProperty(
        name="Filter Material Profiles",
        default=False,
        description="Check to only show IfcProfileDefs attached to IfcMaterialProfiles",
        update=lambda self, context: bpy.ops.bim.load_profiles(),
    )
    object_to_profile: PointerProperty(name="Object to profile", type=bpy.types.Object, description="Object to copy the mesh to a profile")


def generate_thumbnail_for_active_profile():
    from PIL import Image, ImageDraw

    if bpy.app.background:
        return

    props = bpy.context.scene.BIMProfileProperties
    ifc_file = tool.Ifc.get()
    preview_collection = ProfileData.preview_collection

    if not props.profiles:
        bpy.ops.bim.load_profiles()

    active_profile = tool.Profile.get_active_profile_ui()
    assert active_profile
    profile_id = active_profile.ifc_definition_id
    profile = ifc_file.by_id(profile_id)

    # generate image
    size = 128
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)

    try:
        tool.Profile.draw_image_for_ifc_profile(draw, profile, size)
    except RuntimeError as e:
        print(f"Failed to generate preview image for profile '{profile}': '{e}'.")
        ProfileData.failed_previews.add(profile_id)
        return

    ProfileData.failed_previews.discard(profile_id)
    pixels = [item for sublist in img.getdata() for item in sublist]

    # save generated image to preview collection
    profile_id_str = str(profile_id)
    if profile_id_str in preview_collection:
        preview_image = preview_collection[profile_id_str]
    else:
        preview_image = preview_collection.new(profile_id_str)
    preview_image.image_size = size, size
    preview_image.image_pixels_float = pixels
