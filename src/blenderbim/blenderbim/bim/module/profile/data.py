# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell.util.doc
import blenderbim.tool as tool


def refresh():
    ProfileData.is_loaded = False


class ProfileData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_profiles": cls.total_profiles(),
            "profile_classes": cls.profile_classes(),
            "is_arbitrary_profile": cls.is_arbitrary_profile(),
            "is_editing_arbitrary_profile": cls.is_editing_arbitrary_profile(),
        }
        cls.is_loaded = True

    @classmethod
    def total_profiles(cls):
        return len(tool.Ifc.get().by_type("IfcProfileDef"))

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
    def is_arbitrary_profile(cls):
        props = bpy.context.scene.BIMProfileProperties
        if props.active_profile_id:
            profile = tool.Ifc.get().by_id(props.active_profile_id)
            if profile.is_a("IfcArbitraryClosedProfileDef"):
                return True

    @classmethod
    def is_editing_arbitrary_profile(cls):
        obj = bpy.context.active_object
        return obj and obj.data and hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.is_profile
