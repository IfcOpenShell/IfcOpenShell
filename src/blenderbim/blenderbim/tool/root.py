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
from blenderbim.bim.module.model.opening import FilledOpeningGenerator


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
        def exclude_callback(attribute):
            return attribute.is_a("IfcProfileDef") and attribute.ProfileName

        if dest.is_a("IfcProduct"):
            if not source.Representation:
                return
            dest.Representation = ifcopenshell.util.element.copy_deep(
                tool.Ifc.get(),
                source.Representation,
                exclude=["IfcGeometricRepresentationContext"],
                exclude_callback=exclude_callback,
            )
        elif dest.is_a("IfcTypeProduct"):
            if not source.RepresentationMaps:
                return
            dest.RepresentationMaps = [
                ifcopenshell.util.element.copy_deep(
                    tool.Ifc.get(), m, exclude=["IfcGeometricRepresentationContext"], exclude_callback=exclude_callback
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
    def get_connection_relationships(cls, objs):
        relationships = {}
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if hasattr(element, "ConnectedTo") and element.ConnectedTo:
                paths = [connection for connection in element.ConnectedTo if connection.is_a("IfcRelConnectsPathElements")]
                for path in paths:
                    relationships[element] = {"type": "path",
                         "related_connection_type": path.RelatedConnectionType,
                         "related_element": path.RelatedElement,
                         "related_priorities": path.RelatedPriorities,
                         "relating_connection_type": path.RelatingConnectionType,
                         "relating_element": path.RelatingElement,
                         "relating_priorities": path.RelatingPriorities,
                    }
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
        if element.is_a("IfcTypeProduct"):
            if element.RepresentationMaps:
                return element.RepresentationMaps[0].MappedRepresentation
        elif element.is_a("IfcProduct"):
            if element.Representation:
                return element.Representation.Representations[0]

    @classmethod
    def get_representation_context(cls, representation):
        return representation.ContextOfItems

    @classmethod
    def is_element_a(cls, element, ifc_class):
        return element.is_a(ifc_class)

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
                    element = new_element
                    filling = new_subelement
                    voided_obj = tool.Ifc.get_object(new_element)
                    filling_obj = tool.Ifc.get_object(new_subelement)

                    existing_opening_occurrence = subelement.FillsVoids[0].RelatingOpeningElement
                    opening = ifcopenshell.api.run(
                        "root.copy_class", tool.Ifc.get(), product=existing_opening_occurrence
                    )
                    ifcopenshell.api.run(
                        "geometry.edit_object_placement",
                        tool.Ifc.get(),
                        product=opening,
                        matrix=ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement),
                        is_si=False,
                    )

                    representation = ifcopenshell.util.representation.get_representation(
                        existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
                    )
                    representation = ifcopenshell.util.representation.resolve_representation(representation)
                    mapped_representation = ifcopenshell.api.run(
                        "geometry.map_representation", tool.Ifc.get(), representation=representation
                    )
                    ifcopenshell.api.run(
                        "geometry.assign_representation",
                        tool.Ifc.get(),
                        product=opening,
                        representation=mapped_representation,
                    )
                    ifcopenshell.api.run("void.add_opening", tool.Ifc.get(), opening=opening, element=element)
                    ifcopenshell.api.run("void.add_filling", tool.Ifc.get(), opening=opening, element=filling)

                    voided_objs = [voided_obj]
                    # Openings affect all subelements of an aggregate
                    for subelement in ifcopenshell.util.element.get_decomposition(element):
                        subobj = tool.Ifc.get_object(subelement)
                        if subobj:
                            voided_objs.append(subobj)

                    for voided_obj in voided_objs:
                        if voided_obj.data:
                            representation = tool.Ifc.get().by_id(voided_obj.data.BIMMeshProperties.ifc_definition_id)
                            blenderbim.core.geometry.switch_representation(
                                tool.Ifc,
                                tool.Geometry,
                                obj=voided_obj,
                                representation=representation,
                                should_reload=True,
                                is_global=True,
                                should_sync_changes_first=False,
                            )

    @classmethod
    def recreate_connections(cls, relationship, old_to_new):
        for element, data in relationship.items():
            try:
                new_relating_element = old_to_new.get(data["relating_element"])[0]
                new_related_element = old_to_new.get(data["related_element"])[0]
            except:
                continue
            ifcopenshell.api.run(
                "geometry.connect_path",
                tool.Ifc.get(),
                relating_element=new_relating_element,
                related_element=new_related_element,
                relating_connection=data["relating_connection_type"],
                related_connection=data["related_connection_type"],
            )

    
    @classmethod
    def recreate_aggregate(cls, old_to_new):
        for old, new in old_to_new.items():
            old_aggregate = ifcopenshell.util.element.get_aggregate(old)
            if old_aggregate:
                try:
                    new_aggregate = old_to_new[old_aggregate]
                except:
                    blenderbim.core.aggregate.unassign_object(
                                                tool.Ifc,
                                                tool.Aggregate,
                                                tool.Collector,
                                                relating_obj=tool.Ifc.get_object(old_aggregate),
                                                related_obj=tool.Ifc.get_object(new[0]),
                                            )
                    continue
                
                blenderbim.core.aggregate.assign_object(
                                            tool.Ifc,
                                            tool.Aggregate,
                                            tool.Collector,
                                            relating_obj=tool.Ifc.get_object(new_aggregate[0]),
                                            related_obj=tool.Ifc.get_object(new[0]),
                                        )
                
                # Make sure that the array children also get reassigned to the correct aggregate
                pset = ifcopenshell.util.element.get_pset(new[0], "BBIM_Array")
                if pset:
                    array_children = tool.Blender.Modifier.Array.get_all_children_objects(new[0])
                    for obj in array_children:
                        blenderbim.core.aggregate.assign_object(
                                                    tool.Ifc,
                                                    tool.Aggregate,
                                                    tool.Collector,
                                                    relating_obj=tool.Ifc.get_object(new_aggregate[0]),
                                                    related_obj=tool.Ifc.get_object(tool.Ifc.get_entity(obj)),
                                                )
    

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
    def set_object_name(cls, obj, element):
        # This disables the Blender name event handler
        obj.BIMObjectProperties.is_renaming = True
        name = getattr(element, "Name", getattr(element, "AxisTag", None))
        obj.name = "{}/{}".format(element.is_a(), name or "Unnamed")
        obj.BIMObjectProperties.is_renaming = False

    @classmethod
    def unlink_object(cls, obj):
        tool.Ifc.unlink(obj=obj)
        if hasattr(obj.data, "BIMMeshProperties"):
            obj.data.BIMMeshProperties.ifc_definition_id = 0
        for material_slot in obj.material_slots:
            if material_slot.material:
                blenderbim.core.style.unlink_style(tool.Ifc, tool.Style, obj=material_slot.material)
                blenderbim.core.material.unlink_material(tool.Ifc, obj=material_slot.material)
        if "Ifc" in obj.name and "/" in obj.name:
            obj.name = obj.name.split("/", 1)[1]
