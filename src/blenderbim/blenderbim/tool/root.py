# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.core.tool
import blenderbim.core.geometry
import blenderbim.tool as tool
from mathutils import Vector


class Root(blenderbim.core.tool.Root):
    @classmethod
    def add_tracked_opening(cls, obj):
        new = bpy.context.scene.BIMModelProperties.openings.add()
        new.obj = obj

    @classmethod
    def does_type_have_representations(cls, element):
        return bool(element.RepresentationMaps)

    @classmethod
    def get_element_type(cls, element):
        return ifcopenshell.util.element.get_type(element)

    @classmethod
    def get_object_name(cls, obj):
        if "." in obj.name and obj.name.split(".")[-1].isnumeric():
            return ".".join(obj.name.split(".")[:-1])
        return obj.name

    @classmethod
    def get_object_representation(cls, obj):
        if obj.data and obj.data.BIMMeshProperties.ifc_definition_id:
            return tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        element = tool.Ifc.get_entity(obj)
        if not obj.data and getattr(element, "ObjectType", None) == "TEXT":
            return element.Representation.Representations[0]

    @classmethod
    def get_representation_context(cls, representation):
        return representation.ContextOfItems

    @classmethod
    def is_opening_element(cls, element):
        return element.is_a("IfcOpeningElement")

    @classmethod
    def link_object_data(cls, source_obj, destination_obj):
        destination_obj.data = source_obj.data

    @classmethod
    def run_geometry_add_representation(
        cls, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None
    ):
        return blenderbim.core.geometry.add_representation(
            tool.Ifc,
            tool.Geometry,
            tool.Style,
            tool.Surveyor,
            obj=obj,
            context=context,
            ifc_representation_class=ifc_representation_class,
            profile_set_usage=profile_set_usage,
        )

    @classmethod
    def set_element_specific_display_settings(cls, obj, element):
        if element.is_a("IfcOpeningElement"):
            obj.display_type = "WIRE"

    @classmethod
    def set_object_name(cls, obj, element):
        name = obj.name
        if "/" in name and name.split("/")[0][0:3] == "Ifc":
            name = "/".join(name.split("/")[1:])
        obj.name = "{}/{}".format(element.is_a(), name)
