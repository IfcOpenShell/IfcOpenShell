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


def update_mode(self, context):
    if self.is_changing_mode:
        return
    if self.mode == "OBJECT":
        bpy.ops.bim.override_mode_set_object("INVOKE_DEFAULT")
    elif self.mode == "EDIT":
        bpy.ops.bim.override_mode_set_edit("INVOKE_DEFAULT")


def get_styles(self, context):
    # postponed import to avoid circular import
    from blenderbim.bim.module.material.data import MaterialsData

    if not MaterialsData.is_loaded:
        MaterialsData.load()
    return MaterialsData.data["styles"]


class RepresentationItem(PropertyGroup):
    name: StringProperty(name="Name")
    surface_style: StringProperty(name="Surface Style")
    layer: StringProperty(name="Layer")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    shape_aspect: StringProperty(name="Shape Aspect")


class BIMObjectGeometryProperties(PropertyGroup):
    contexts: EnumProperty(items=get_contexts, name="Contexts")
    is_editing: BoolProperty(name="Is Editing", default=False)
    items: CollectionProperty(name="Representation Items", type=RepresentationItem)
    active_item_index: IntProperty(name="Active Representation Item Index")
    is_editing_item_style: BoolProperty(name="Is Editing Item's Style", default=False)
    representation_item_style: EnumProperty(items=get_styles, name="Representation Item Style")


class BIMGeometryProperties(PropertyGroup):
    # Revit workaround
    should_use_presentation_style_assignment: BoolProperty(name="Force Presentation Style Assignment", default=False)
    # RIB iTwo, DESITE BIM workaround
    should_force_faceted_brep: BoolProperty(name="Force Faceted Breps", default=False)
    # Navisworks workaround
    should_force_triangulation: BoolProperty(name="Force Triangulation", default=False)
    is_changing_mode: BoolProperty(name="Is Changing Mode", default=False)
    mode: EnumProperty(
        default="OBJECT",
        items=[
            ("OBJECT", "IFC Object Mode", "", "OBJECT_DATAMODE", 0),
            ("EDIT", "IFC Edit Mode", "", "EDITMODE_HLT", 1),
        ],
        name="IFC Interaction Mode",
        update=update_mode,
    )
