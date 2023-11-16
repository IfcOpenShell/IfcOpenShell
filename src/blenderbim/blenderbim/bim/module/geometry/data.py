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
import blenderbim.tool as tool
import ifcopenshell.util.placement
from mathutils import Vector


def refresh():
    PlacementData.is_loaded = False
    DerivedCoordinatesData.is_loaded = False
    RepresentationsData.is_loaded = False
    RepresentationItemsData.is_loaded = False
    ConnectionsData.is_loaded = False


class RepresentationsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"representations": cls.representations()}
        cls.data["contexts"] = cls.contexts()
        cls.is_loaded = True

    @classmethod
    def representations(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)

        active_representation_id = None
        if bpy.context.active_object.data and hasattr(bpy.context.active_object.data, "BIMMeshProperties"):
            active_representation_id = bpy.context.active_object.data.BIMMeshProperties.ifc_definition_id

        representations = []
        if element.is_a("IfcProduct") and element.Representation:
            representations = element.Representation.Representations
        elif element.is_a("IfcTypeProduct"):
            representations = [rm.MappedRepresentation for rm in element.RepresentationMaps or []]
        for representation in representations:
            representation_type = representation.RepresentationType
            if representation_type == "MappedRepresentation":
                representation_type = representation.Items[0].MappingSource.MappedRepresentation.RepresentationType
                representation_type += "*"
            data = {
                "id": representation.id(),
                "ContextType": representation.ContextOfItems.ContextType or "",
                "ContextIdentifier": "",
                "TargetView": "",
                "RepresentationType": representation_type or "",
                "is_active": representation.id() == active_representation_id,
            }
            if representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext"):
                data["ContextIdentifier"] = representation.ContextOfItems.ContextIdentifier or ""
                data["TargetView"] = representation.ContextOfItems.TargetView or ""
            results.append(data)
        return results

    @classmethod
    def contexts(cls):
        results = []
        for element in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            results.append((str(element.id()), element.ContextType or "Unnamed", ""))
        for element in tool.Ifc.get().by_type("IfcGeometricRepresentationSubContext", include_subtypes=False):
            results.append(
                (
                    str(element.id()),
                    "{}/{}/{}".format(
                        element.ContextType or "Unnamed",
                        element.ContextIdentifier or "Unnamed",
                        element.TargetView or "Unnamed",
                    ),
                    "",
                )
            )
        return results


class RepresentationItemsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_items": cls.total_items(),
            "active_surface_style": cls.active_surface_style(),
            "active_layer": cls.active_layer(),
        }
        cls.is_loaded = True

    @classmethod
    def total_items(cls):
        active_representation_id = None
        result = 0
        if bpy.context.active_object.data and hasattr(bpy.context.active_object.data, "BIMMeshProperties"):
            active_representation_id = bpy.context.active_object.data.BIMMeshProperties.ifc_definition_id
            element = tool.Ifc.get().by_id(active_representation_id)
            if not element.is_a("IfcShapeRepresentation"):
                return 0
            queue = list(element.Items)
            while queue:
                item = queue.pop()
                if item.is_a("IfcMappedItem"):
                    queue.extend(item.MappingSource.MappedRepresentation.Items)
                else:
                    result += 1
        return result

    @classmethod
    def active_surface_style(cls):
        props = bpy.context.active_object.BIMGeometryProperties
        if props.active_item_index < len(props.items):
            return props.items[props.active_item_index].surface_style

    @classmethod
    def active_layer(cls):
        props = bpy.context.active_object.BIMGeometryProperties
        if props.active_item_index < len(props.items):
            return props.items[props.active_item_index].layer


class ConnectionsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"connections": cls.connections(), "is_connection_realization": cls.is_connection_realization()}
        cls.is_loaded = True

    @classmethod
    def connections(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)

        connected_to = getattr(element, "ConnectedTo", [])
        connected_from = getattr(element, "ConnectedFrom", [])

        for rel in connected_to:
            if element.is_a("IfcDistributionPort"):
                related_element = rel.RelatedPort
            else:
                related_element = rel.RelatedElement

            realizing_elements = []
            realizing_elements_connection_type = ""
            if rel.is_a("IfcRelConnectsWithRealizingElements"):
                realizing_elements.extend(rel.RealizingElements)
                realizing_elements_connection_type = rel.ConnectionType

            if rel.is_a("IfcRelConnectsPathElements"):
                related_element_connection_type = rel.RelatedConnectionType
            else:
                related_element_connection_type = ""

            results.append(
                {
                    "id": rel.id(),
                    "is_relating": True,
                    "Name": related_element.Name or "Unnamed",
                    "ConnectionType": related_element_connection_type,
                    "realizing_elements": realizing_elements,
                    "realizing_elements_connection_type": realizing_elements_connection_type,
                }
            )

        for rel in connected_from:
            if element.is_a("IfcDistributionPort"):
                relating_element = rel.RelatingPort
            else:
                relating_element = rel.RelatingElement

            realizing_elements = []
            realizing_elements_connection_type = ""
            if rel.is_a("IfcRelConnectsWithRealizingElements"):
                realizing_elements.extend(rel.RealizingElements)
                realizing_elements_connection_type = rel.ConnectionType

            if rel.is_a("IfcRelConnectsPathElements"):
                relating_element_connection_type = rel.RelatingConnectionType
            else:
                relating_element_connection_type = ""

            results.append(
                {
                    "id": rel.id(),
                    "is_relating": False,
                    "Name": relating_element.Name or "Unnamed",
                    "ConnectionType": relating_element_connection_type,
                    "realizing_elements": realizing_elements,
                    "realizing_elements_connection_type": realizing_elements_connection_type,
                }
            )

        return results

    @classmethod
    def is_connection_realization(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        connections = element.IsConnectionRealization
        if not connections:
            return

        results = []
        for rel in connections:
            data = {
                "realizing_elements_connection_type": rel.ConnectionType,
                "connected_from": rel.RelatingElement,
                "connected_to": rel.RelatedElement,
            }
            results.append(data)
        return results


class DerivedCoordinatesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.load_z_values()
        cls.load_collection()
        cls.data = {
            "is_storey": cls.is_storey(),
            "storey_height": cls.storey_height(),
            "min_global_z": cls.min_global_z(),
            "max_global_z": cls.max_global_z(),
            "has_collection": cls.has_collection(),
            "min_decomposed_z": cls.min_decomposed_z(),
            "max_decomposed_z": cls.max_decomposed_z(),
        }
        cls.is_loaded = True

    @classmethod
    def load_z_values(cls):
        cls.z_values = [
            (bpy.context.active_object.matrix_world @ Vector(co))[2] for co in bpy.context.active_object.bound_box
        ]

    @classmethod
    def load_collection(cls):
        cls.collection = None
        cls.collection_z = 0
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return
        parent = ifcopenshell.util.element.get_aggregate(element)
        if not parent:
            parent = ifcopenshell.util.element.get_container(element)
        if parent:
            cls.collection = tool.Ifc.get_object(parent)
            if cls.collection:
                cls.collection_z = cls.collection.matrix_world.translation.z

    @classmethod
    def has_collection(cls):
        return bool(cls.collection)

    @classmethod
    def min_global_z(cls):
        return "{0:.3f}".format(round(min(cls.z_values), 3))

    @classmethod
    def max_global_z(cls):
        return "{0:.3f}".format(round(max(cls.z_values), 3))

    @classmethod
    def min_decomposed_z(cls):
        return "{0:.3f}".format(round(min(cls.z_values) - cls.collection_z, 3))

    @classmethod
    def max_decomposed_z(cls):
        return "{0:.3f}".format(round(max(cls.z_values) - cls.collection_z, 3))

    @classmethod
    def is_storey(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            return element.is_a("IfcBuildingStorey")

    @classmethod
    def storey_height(cls):
        if not cls.is_storey():
            return
        element = tool.Ifc.get_entity(bpy.context.active_object)
        storeys = [
            (s, ifcopenshell.util.placement.get_local_placement(s.ObjectPlacement)[2][3])
            for s in tool.Ifc.get().by_type("IfcBuildingStorey")
        ]
        storeys = sorted(storeys, key=lambda s: s[1])
        for i, storey in enumerate(storeys):
            if storey[0] != element:
                continue
            if i >= len(storeys) - 1:
                return "N/A"
            return "{0:.3f}".format(round(storeys[i + 1][1] - storey[1], 3))


class PlacementData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_placement": cls.has_placement(),
        }
        cls.is_loaded = True

    @classmethod
    def has_placement(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element and hasattr(element, "ObjectPlacement"):
            return True
        return False
