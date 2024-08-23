# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.context.data import ContextData
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


class BIMContextProperties(PropertyGroup):
    contexts: EnumProperty(items=[("Model", "Model", ""), ("Plan", "Plan", "")], name="Contexts")
    subcontexts: EnumProperty(
        items=[
            ("Annotation", "Annotation", ""),
            ("Axis", "Axis", ""),
            ("Box", "Box", ""),
            ("FootPrint", "FootPrint", ""),
            ("Reference", "Reference", ""),
            ("Body", "Body", ""),
            ("Clearance", "Clearance", ""),
            ("CoG", "CoG", ""),
            ("Profile", "Profile", ""),
            ("SurveyPoints", "SurveyPoints", ""),
            ("Lighting", "Lighting", ""),
        ],
        name="Subcontexts",
    )
    target_views: EnumProperty(
        items=[
            ("GRAPH_VIEW", "GRAPH_VIEW", ""),
            ("SKETCH_VIEW", "SKETCH_VIEW", ""),
            ("MODEL_VIEW", "MODEL_VIEW", ""),
            ("PLAN_VIEW", "PLAN_VIEW", ""),
            ("REFLECTED_PLAN_VIEW", "REFLECTED_PLAN_VIEW", ""),
            ("SECTION_VIEW", "SECTION_VIEW", ""),
            ("ELEVATION_VIEW", "ELEVATION_VIEW", ""),
            ("USERDEFINED", "USERDEFINED", ""),
            ("NOTDEFINED", "NOTDEFINED", ""),
        ],
        name="Target Views",
    )
    active_context_id: IntProperty(name="Active Context Id")
    context_attributes: CollectionProperty(name="Context Attributes", type=Attribute)
