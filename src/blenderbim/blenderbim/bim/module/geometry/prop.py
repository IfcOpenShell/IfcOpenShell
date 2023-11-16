# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.geometry.data import RepresentationsData
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


def get_contexts(self, context):
    if not RepresentationsData.is_loaded:
        RepresentationsData.load()
    return RepresentationsData.data["contexts"]


class RepresentationItem(PropertyGroup):
    name: StringProperty(name="Name")
    surface_style: StringProperty(name="Surface Style")
    layer: StringProperty(name="Layer")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMObjectGeometryProperties(PropertyGroup):
    contexts: EnumProperty(items=get_contexts, name="Contexts")
    is_editing: BoolProperty(name="Is Editing", default=False)
    items: CollectionProperty(name="Representation Items", type=RepresentationItem)
    active_item_index: IntProperty(name="Active Representation Item Index")


class BIMGeometryProperties(PropertyGroup):
    # Revit workaround
    should_use_presentation_style_assignment: BoolProperty(name="Force Presentation Style Assignment", default=False)
    # RIB iTwo, DESITE BIM workaround
    should_force_faceted_brep: BoolProperty(name="Force Faceted Breps", default=False)
    # Navisworks workaround
    should_force_triangulation: BoolProperty(name="Force Triangulation", default=False)
