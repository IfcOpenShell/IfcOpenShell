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
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.schema
import ifcopenshell.util.unit
import bonsai.tool as tool
from mathutils import Vector


def refresh():
    ViewportData.is_loaded = False
    PlacementData.is_loaded = False
    DerivedCoordinatesData.is_loaded = False
    RepresentationsData.is_loaded = False
    RepresentationItemsData.is_loaded = False
    ConnectionsData.is_loaded = False


class ViewportData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"mode": cls.mode()}

    @classmethod
    def mode(cls):
        obj_mode = ("OBJECT", "IFC Object Mode", "View and move the placements of objects", "OBJECT_DATAMODE", 0)
        item_mode = ("ITEM", "IFC Item Mode", "View individual representation items", "MESH_DATA", 1)
        edit_mode = ("EDIT", "IFC Edit Mode", "Edit representation items", "EDITMODE_HLT", 2)

        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)

        modes = [obj_mode]

        if bpy.context.scene.BIMGeometryProperties.representation_obj:
            modes.append(item_mode)

        if not obj:
            return modes

        if obj in bpy.context.scene.BIMProjectProperties.clipping_planes_objs:
            pass
        elif element:
            if (usage := tool.Model.get_usage_type(element)) and usage in ("LAYER1", "LAYER2"):
                pass
            elif tool.Geometry.is_locked(element):
                pass
            elif usage == "PROFILE":
                modes.append(edit_mode)
            elif usage == "LAYER3":
                modes.append(edit_mode)
            elif obj.data and tool.Geometry.is_profile_based(obj.data):
                modes.append(edit_mode)
            elif element.is_a("IfcRelSpaceBoundary"):
                modes.append(edit_mode)
            elif element.is_a("IfcGridAxis"):
                modes.append(edit_mode)
            elif tool.Blender.Modifier.is_editing_parameters(obj):
                # This should go BEFORE the modifiers
                pass
            elif tool.Blender.Modifier.is_roof(element):
                modes.append(edit_mode)
            elif tool.Blender.Modifier.is_railing(element):
                modes.append(edit_mode)
            elif item_mode not in modes:
                modes.append(item_mode)
        elif tool.Geometry.is_representation_item(obj):
            modes.append(edit_mode)
        else:  # A regular Blender object
            modes.append(edit_mode)

        return modes


class RepresentationsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"representations": cls.representations()}
        cls.data["contexts"] = cls.contexts()

        # Only after cls.representations().
        cls.data["shape_aspects"] = cls.shape_aspects()

        cls.is_loaded = True

    @classmethod
    def representations(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)

        active_representation_id = None
        if bpy.context.active_object.data and hasattr(bpy.context.active_object.data, "BIMMeshProperties"):
            active_representation_id = bpy.context.active_object.data.BIMMeshProperties.ifc_definition_id

        for representation in tool.Geometry.get_representations_iter(element):
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

    @classmethod
    def shape_aspects(cls) -> list[tuple[str, str, str]]:
        """Get list of current's representation shape aspects for prop's enum_items."""
        # Ignore objects without representations, e.g. IfcRelSpaceBoundary.
        if not cls.data["representations"]:
            return []
        obj = bpy.context.active_object
        if not obj.data:
            return []
        element = tool.Ifc.get_entity(obj)
        active_representation_id = obj.data.BIMMeshProperties.ifc_definition_id
        base_representation = tool.Ifc.get().by_id(active_representation_id)

        # shape aspects matching context of the active representation
        matching_shape_aspects = []
        for shape_aspect in ifcopenshell.util.element.get_shape_aspects(element):
            matching_representation = tool.Geometry.get_shape_aspect_representation(shape_aspect, base_representation)
            if matching_representation:
                matching_shape_aspects.append(shape_aspect)

        # blender enum items
        new_shape_aspect = [("NEW", "Create A New Shape Aspect", "")]
        return new_shape_aspect + [(str(s.id()), s.Name or "Unnamed", "") for s in matching_shape_aspects]


class RepresentationItemsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_items": cls.total_items(),
        }
        cls.is_loaded = True

    @classmethod
    def total_items(cls) -> int:
        result = 0
        obj = bpy.context.active_object
        assert obj
        element = tool.Geometry.get_active_representation(obj)
        if element:
            # IfcShapeRepresentation or IfcTopologyRepresentation.
            if not element.is_a("IfcShapeModel"):
                return 0
            queue = list(element.Items)
            while queue:
                item = queue.pop()
                if item.is_a("IfcMappedItem"):
                    queue.extend(item.MappingSource.MappedRepresentation.Items)
                else:
                    result += 1
        return result


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
        connections = getattr(element, "IsConnectionRealization", None)
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
        cls.data = {"has_placement": cls.has_placement()}

        props = bpy.context.scene.BIMGeoreferenceProperties
        obj = bpy.context.active_object
        if obj and props.has_blender_offset:
            xyz = cls.original_xyz(obj)
            cls.data.update(
                {
                    "original_x": str(xyz[0]),
                    "original_y": str(xyz[1]),
                    "original_z": str(xyz[2]),
                }
            )
        cls.is_loaded = True

    @classmethod
    def has_placement(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element and hasattr(element, "ObjectPlacement"):
            return True
        return False

    @classmethod
    def original_xyz(cls, obj):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        props = bpy.context.scene.BIMGeoreferenceProperties
        xyz = ifcopenshell.util.geolocation.xyz2enh(
            obj.matrix_world[0][3],
            obj.matrix_world[1][3],
            obj.matrix_world[2][3],
            float(props.blender_offset_x) * unit_scale,
            float(props.blender_offset_y) * unit_scale,
            float(props.blender_offset_z) * unit_scale,
            float(props.blender_x_axis_abscissa),
            float(props.blender_x_axis_ordinate),
            1.0,
        )
        return [round(o, 3) / unit_scale for o in xyz]  # To nearest mm of precision
