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
import bonsai.tool as tool
import ifcopenshell.util.element


def refresh():
    SpatialData.is_loaded = False
    SpatialDecompositionData.is_loaded = False


class SpatialData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["poll"] = cls.poll()
        if cls.data["poll"]:
            cls.data.update(
                {
                    "default_container": cls.default_container(),
                    "selected_containers": cls.selected_containers(),
                    "is_directly_contained": cls.is_directly_contained(),
                    "label": cls.label(),
                    "references": cls.references(),
                }
            )

    @classmethod
    def poll(cls):
        if not bpy.context.active_object:
            return False
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return False
        if element.is_a("IfcElement") or element.is_a("IfcAnnotation") or element.is_a("IfcGrid"):
            return True
        return False

    @classmethod
    def default_container(cls) -> str | None:
        props = bpy.context.scene.BIMSpatialDecompositionProperties
        if props.default_container:
            try:
                return tool.Ifc.get().by_id(props.default_container).Name
            except:
                pass

    @classmethod
    def selected_containers(cls):
        return sorted([e.Name or "Unnamed" for e in tool.Spatial.get_selected_containers()])

    @classmethod
    def label(cls):
        container = ifcopenshell.util.element.get_container(tool.Ifc.get_entity(bpy.context.active_object))
        if container:
            label = f"{container.is_a()}/{container.Name or ''}"
            if not cls.is_directly_contained():
                label += "*"
            return label

    @classmethod
    def references(cls):
        results = ifcopenshell.util.element.get_referenced_structures(tool.Ifc.get_entity(bpy.context.active_object))
        return sorted([f"{r.is_a()}/{r.Name or ''}" for r in results])

    @classmethod
    def is_directly_contained(cls):
        return bool(getattr(tool.Ifc.get_entity(bpy.context.active_object), "ContainedInStructure", False))


class SpatialDecompositionData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {
            "default_container": cls.default_container(),
            "subelement_class": cls.subelement_class(),
        }

    @classmethod
    def default_container(cls) -> str | None:
        props = bpy.context.scene.BIMSpatialDecompositionProperties
        if props.default_container:
            try:
                return tool.Ifc.get().by_id(props.default_container).Name
            except:
                pass

    @classmethod
    def subelement_class(cls):
        results = []
        props = bpy.context.scene.BIMSpatialDecompositionProperties
        if not (container := props.active_container):
            return results
        container_class = tool.Ifc.get().by_id(container.ifc_definition_id).is_a()
        if tool.Ifc.get_schema() == "IFC2X3":
            results = {
                "IfcBuilding": ["IfcBuilding", "IfcBuildingStorey", "IfcSpace"],
                "IfcBuildingStorey": ["IfcBuildingStorey", "IfcSpace"],
                "IfcProject": ["IfcBuilding", "IfcSite", "IfcSpace"],
                "IfcSite": ["IfcBuilding", "IfcSite", "IfcSpace"],
                "IfcSpace": ["IfcSpace"],
            }[container_class]
        elif tool.Ifc.get_schema() == "IFC4":
            results = {
                "IfcBuilding": ["IfcBuilding", "IfcBuildingStorey", "IfcSpace"],
                "IfcBuildingStorey": ["IfcBuildingStorey", "IfcSpace"],
                "IfcExternalSpatialElement": ["IfcExternalSpatialElement"],
                "IfcProject": ["IfcBuilding", "IfcExternalSpatialElement", "IfcSite", "IfcSpace"],
                "IfcSite": ["IfcBuilding", "IfcExternalSpatialElement", "IfcSite", "IfcSpace"],
                "IfcSpace": ["IfcSpace"],
            }[container_class]
        elif tool.Ifc.get_schema() == "IFC4X3":
            results = {
                "IfcBridge": ["IfcBridge", "IfcBridgePart", "IfcSpace"],
                "IfcBridgePart": ["IfcSpace"],
                "IfcBuilding": ["IfcBuilding", "IfcBuildingStorey", "IfcSpace"],
                "IfcBuildingStorey": ["IfcBuildingStorey", "IfcSpace"],
                "IfcExternalSpatialElement": ["IfcExternalSpatialElement"],
                "IfcFacility": ["IfcFacility", "IfcFacilityPartCommon", "IfcSpace"],
                "IfcFacilityPartCommon": ["IfcSpace"],
                "IfcMarineFacility": ["IfcMarineFacility", "IfcMarinePart", "IfcSpace"],
                "IfcMarinePart": ["IfcSpace"],
                "IfcProject": [
                    "IfcBridge",
                    "IfcBuilding",
                    "IfcExternalSpatialElement",
                    "IfcFacility",
                    "IfcMarineFacility",
                    "IfcRailway",
                    "IfcRoad",
                    "IfcSite",
                    "IfcSpace",
                ],
                "IfcRailway": ["IfcRailway", "IfcRailwayPart", "IfcSpace"],
                "IfcRailwayPart": ["IfcSpace"],
                "IfcRoad": ["IfcRoad", "IfcRoadPart", "IfcSpace"],
                "IfcRoadPart": ["IfcSpace"],
                "IfcSite": [
                    "IfcBridge",
                    "IfcBuilding",
                    "IfcExternalSpatialElement",
                    "IfcFacility",
                    "IfcMarineFacility",
                    "IfcRailway",
                    "IfcRoad",
                    "IfcSite",
                    "IfcSpace",
                ],
                "IfcSpace": ["IfcSpace"],
            }[container_class]

        return [(r, r, "") for r in results]
