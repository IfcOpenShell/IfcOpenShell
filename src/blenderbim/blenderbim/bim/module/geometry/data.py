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
    DerivedPlacementsData.is_loaded = False
    RepresentationsData.is_loaded = False
    ConnectionsData.is_loaded = False


class RepresentationsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"representations": cls.representations()}
        cls.is_loaded = True

    @classmethod
    def representations(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
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
            }
            if representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext"):
                data["ContextIdentifier"] = representation.ContextOfItems.ContextIdentifier or ""
                data["TargetView"] = representation.ContextOfItems.TargetView or ""
            results.append(data)
        return results


class ConnectionsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"connections": cls.connections()}
        cls.is_loaded = True

    @classmethod
    def connections(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        for rel in getattr(element, "ConnectedTo", []):
            results.append(
                {
                    "id": rel.id(),
                    "is_relating": True,
                    "Name": rel.RelatedElement.Name or "Unnamed",
                    "ConnectionType": rel.RelatingConnectionType,
                }
            )
        for rel in getattr(element, "ConnectedFrom", []):
            results.append(
                {
                    "id": rel.id(),
                    "is_relating": False,
                    "Name": rel.RelatingElement.Name or "Unnamed",
                    "ConnectionType": rel.RelatedConnectionType,
                }
            )
        return results


class DerivedPlacementsData:
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
        cls.collection = bpy.data.objects.get(bpy.context.active_object.users_collection[0].name)
        cls.collection_z = 0
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
            if i >= len(storeys):
                return "N/A"
            return "{0:.3f}".format(round(storeys[i + 1][1] - storey[1], 3))
