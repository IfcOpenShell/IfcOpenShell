# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import bpy.utils
import bpy.utils.previews
import ifcopenshell.util.doc
import bonsai.tool as tool


def refresh():
    ProfileData.is_loaded = False


class ProfileData:
    data = {}
    failed_previews: set[int] = set()
    preview_collection = bpy.utils.previews.new()
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_profiles": cls.total_profiles(),
            "active_profile_users": cls.active_profile_users(),
            "profile_classes": cls.profile_classes(),
            "is_arbitrary_profile": cls.is_arbitrary_profile(),
            "is_editing_arbitrary_profile": cls.is_editing_arbitrary_profile(),
            "profile_def_classes_enum": cls.profile_def_classes_enum(),
        }
        cls.is_loaded = True

    @classmethod
    def total_profiles(cls):
        return len([p for p in tool.Ifc.get().by_type("IfcProfileDef") if p.ProfileName])

    @classmethod
    def active_profile_users(cls):
        profiles_props = bpy.context.scene.BIMProfileProperties
        if profiles_props.active_profile_index >= len(profiles_props.profiles):
            return 0
        profile_prop = profiles_props.profiles[profiles_props.active_profile_index]
        profile_ifc = tool.Ifc.get().by_id(profile_prop.ifc_definition_id)
        return tool.Ifc.get().get_total_inverses(profile_ifc)

    @classmethod
    def profile_classes(cls):
        classes = ["IfcArbitraryClosedProfileDef"]
        queue = ["IfcParameterizedProfileDef"]
        while queue:
            item = queue.pop()
            subtypes = [s.name() for s in tool.Ifc.schema().declaration_by_name(item).subtypes()]
            classes.extend(subtypes)
            queue.extend(subtypes)
        schema_identifier = tool.Ifc.get_schema()
        return [
            (c, c, ifcopenshell.util.doc.get_entity_doc(schema_identifier, c)["description"] or "")
            for c in sorted(classes)
        ]

    @classmethod
    def profile_def_classes_enum(cls) -> list[tuple[str, str, str]]:
        version = tool.Ifc.get_schema()
        return [
            (t.name(), t.name(), ifcopenshell.util.doc.get_entity_doc(version, t.name()).get("description", ""))
            for t in tool.Ifc.schema().declaration_by_name("IfcProfileDef").subtypes()
        ]

    @classmethod
    def is_arbitrary_profile(cls):
        props = bpy.context.scene.BIMProfileProperties
        if props.active_profile_id:
            profile = tool.Ifc.get().by_id(props.active_profile_id)
            if profile.is_a("IfcArbitraryClosedProfileDef"):
                return True

    @classmethod
    def is_editing_arbitrary_profile(cls):
        obj = bpy.context.active_object
        return (
            obj
            and obj.data
            and hasattr(obj.data, "BIMMeshProperties")
            and obj.data.BIMMeshProperties.subshape_type == "PROFILE"
        )
