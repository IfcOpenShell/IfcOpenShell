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
import ifcopenshell.util.representation
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
    def assign_body_styles(cls, element, obj):
        # Should this even be here? Should it be in the geometry tool?
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if body:
            [
                tool.Geometry.run_style_add_style(obj=mat)
                for mat in tool.Geometry.get_object_materials_without_styles(obj)
            ]
            ifcopenshell.api.run(
                "style.assign_representation_styles",
                tool.Ifc.get(),
                shape_representation=body,
                styles=tool.Geometry.get_styles(obj),
                should_use_presentation_style_assignment=bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment,
            )

    @classmethod
    def copy_representation(cls, source, dest):
        if dest.is_a("IfcProduct"):
            if not source.Representation:
                return
            dest.Representation = ifcopenshell.util.element.copy_deep(
                tool.Ifc.get(), source.Representation, exclude=["IfcGeometricRepresentationContext", "IfcProfileDef"]
            )
        elif dest.is_a("IfcTypeProduct"):
            if not source.RepresentationMaps:
                return
            dest.RepresentationMaps = [
                ifcopenshell.util.element.copy_deep(
                    tool.Ifc.get(), m, exclude=["IfcGeometricRepresentationContext", "IfcProfileDef"]
                )
                for m in source.RepresentationMaps
            ]

    @classmethod
    def does_type_have_representations(cls, element):
        return bool(element.RepresentationMaps)

    @classmethod
    def get_decomposition_relationships(cls, objs):
        relationships = {}
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if hasattr(element, "FillsVoids") and element.FillsVoids:
                building = element.FillsVoids[0].RelatingOpeningElement.VoidsElements[0].RelatingBuildingElement
                relationships[element] = {"type": "fill", "element": building}
        return relationships

    @classmethod
    def get_element_representation(cls, element, context):
        if context.is_a("IfcGeometricRepresentationSubContext"):
            return ifcopenshell.util.representation.get_representation(
                element,
                context=context.ContextType,
                subcontext=context.ContextIdentifier,
                target_view=context.TargetView,
            )
        return ifcopenshell.util.representation.get_representation(element, context=context.ContextType)

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
    def recreate_decompositions(cls, relationships, old_to_new):
        for subelement, data in relationships.items():
            new_subelements = old_to_new.get(subelement)
            new_elements = old_to_new.get(data["element"])
            if not new_subelements or not new_elements:
                continue
            for i, new_subelement in enumerate(new_subelements):
                new_element = new_elements[i]
                if data["type"] == "fill":
                    obj1 = tool.Ifc.get_object(new_element)
                    obj2 = tool.Ifc.get_object(new_subelement)
                    bpy.ops.bim.add_filled_opening(voided_obj=obj1.name, filling_obj=obj2.name)

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
