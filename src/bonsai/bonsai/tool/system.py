# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import bpy
import ifcopenshell.util.element
import ifcopenshell.util.system
import bonsai.bim.helper
import bonsai.core.geometry
import bonsai.core.root
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim import import_ifc
import re
from math import pi, cos, sin
from mathutils import Matrix, Vector
from bonsai.bim.module.system.data import ObjectSystemData, SystemDecorationData
from enum import Enum
from typing import TYPE_CHECKING, Optional, Any, Union

if TYPE_CHECKING:
    from bonsai.bim.module.system.prop import BIMSystemProperties, BIMZoneProperties, BIMZoneProperties


class System(bonsai.core.tool.System):
    @classmethod
    def get_system_props(cls) -> BIMSystemProperties:
        return bpy.context.scene.BIMSystemProperties

    @classmethod
    def get_zone_props(cls) -> BIMZoneProperties:
        return bpy.context.scene.BIMZoneProperties

    @classmethod
    def add_ports(
        cls,
        obj: bpy.types.Object,
        add_start_port: bool = True,
        add_end_port: bool = True,
        end_port_pos: Optional[Vector] = None,
        offset_end_port: Optional[Vector] = None,
    ) -> list[ifcopenshell.entity_instance]:
        def add_port(mep_element, matrix):
            port = tool.Ifc.run("system.add_port", element=mep_element)
            port.FlowDirection = "NOTDEFINED"
            port.PredefinedType = tool.System.get_port_predefined_type(mep_element)
            tool.Ifc.run("geometry.edit_object_placement", product=port, matrix=matrix, is_si=True)
            return port

        # make sure obj.dimensions and .matrix_world has valid data
        bpy.context.view_layer.update()
        # need to make sure .ObjectPlacement is also updated when we're going to add ports
        tool.Model.sync_object_ifc_position(obj)

        mep_element = tool.Ifc.get_entity(obj)
        bbox = tool.Blender.get_object_bounding_box(obj)
        length = bbox["min_z"] if tool.Cad.is_x(bbox["max_z"], 0) else bbox["max_z"]
        ports = []
        if add_start_port:
            ports.append(add_port(mep_element, obj.matrix_world))
        if add_end_port:
            m = obj.matrix_world.copy()
            if end_port_pos:
                m.translation = end_port_pos
            else:
                m = m @ Matrix.Translation((0, 0, length))
                if offset_end_port:
                    m.translation += offset_end_port
            ports.append(add_port(mep_element, m))
        return ports

    @classmethod
    def create_empty_at_cursor_with_element_orientation(cls, element: ifcopenshell.entity_instance) -> bpy.types.Object:
        element_obj = tool.Ifc.get_object(element)
        obj = bpy.data.objects.new("Port", None)
        obj.matrix_world = element_obj.matrix_world
        obj.matrix_world.translation = bpy.context.scene.cursor.matrix.translation
        bpy.context.scene.collection.objects.link(obj)
        return obj

    @classmethod
    def delete_element_objects(cls, elements: list[ifcopenshell.entity_instance]) -> None:
        for element in elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                bpy.data.objects.remove(obj)

    @classmethod
    def disable_editing_system(cls) -> None:
        cls.get_system_props().edited_system_id = 0

    @classmethod
    def disable_system_editing_ui(cls) -> None:
        cls.get_system_props().is_editing = False

    @classmethod
    def enable_system_editing_ui(cls) -> None:
        cls.get_system_props().is_editing = True

    @classmethod
    def export_system_attributes(cls) -> dict[str, Any]:
        return bonsai.bim.helper.export_attributes(cls.get_system_props().system_attributes)

    @classmethod
    def get_connected_port(cls, port: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.system.get_connected_port(port)

    @classmethod
    def get_ports(cls, element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.system.get_ports(element)

    @classmethod
    def get_port_relating_element(cls, port: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        if tool.Ifc.get_schema() == "IFC2X3":
            element = port.ContainedIn[0].RelatedElement
        else:
            element = port.Nests[0].RelatingObject
        return element

    @classmethod
    def get_port_predefined_type(cls, mep_element: ifcopenshell.entity_instance) -> str:
        split_camel_case = lambda x: re.findall("[A-Z][^A-Z]*", x)
        mep_class = mep_element.is_a()
        if mep_class.endswith("Type"):
            mep_class = mep_class[:-4]
        class_name = "".join(split_camel_case(mep_class)[1:-1]).upper()
        if class_name == "CONVEYOR":
            return "NOTDEFINED"
        return class_name

    @classmethod
    def import_system_attributes(cls, system: ifcopenshell.entity_instance) -> None:
        props = cls.get_system_props()
        props.system_attributes.clear()
        bonsai.bim.helper.import_attributes2(system, props.system_attributes)

    @classmethod
    def get_systems(cls) -> list[ifcopenshell.entity_instance]:
        if tool.Ifc.get_schema() == "IFC2X3":
            return tool.Ifc.get().by_type("IfcSystem") + tool.Ifc.get().by_type("IfcZone")
        return tool.Ifc.get().by_type("IfcSystem")

    @classmethod
    def import_systems(cls) -> None:
        props = cls.get_system_props()
        props.systems.clear()
        for system in cls.get_systems():
            if system.is_a() in ["IfcStructuralAnalysisModel"]:
                continue
            new = props.systems.add()
            new.ifc_definition_id = system.id()
            new["name"] = system.Name or "Unnamed"
            new.ifc_class = system.is_a()

    @classmethod
    def load_ports(cls, element: ifcopenshell.entity_instance, ports: list[ifcopenshell.entity_instance]) -> None:
        if not ports:
            return

        ports_to_create = ports.copy()
        for port in ports:
            if tool.Ifc.get_object(port):
                ports_to_create.remove(port)

        obj = tool.Ifc.get_object(element)
        assert isinstance(obj, bpy.types.Object)
        ifc_import_settings = import_ifc.IfcImportSettings.factory()
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ifc_importer.create_generic_elements(set(ports_to_create))

        container = ifcopenshell.util.element.get_container(element)
        if container:
            collection = tool.Blender.get_object_bim_props(tool.Ifc.get_object(container)).collection
            ifc_importer.collections[container.GlobalId] = collection
        ifc_importer.place_objects_in_collections()

        for port_obj in ifc_importer.added_data.values():
            assert isinstance(port_obj, bpy.types.Object)
            port_obj.parent = obj
            port_obj.matrix_parent_inverse = obj.matrix_world.inverted()

    @classmethod
    def run_geometry_edit_object_placement(cls, obj: bpy.types.Object) -> None:
        return bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

    @classmethod
    def run_root_assign_class(
        cls,
        obj=None,
        ifc_class=None,
        predefined_type=None,
        should_add_representation=True,
        context=None,
        ifc_representation_class=None,
    ):
        return bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            should_add_representation=should_add_representation,
            context=context,
            ifc_representation_class=ifc_representation_class,
        )

    @classmethod
    def select_system_products(cls, system: ifcopenshell.entity_instance) -> None:
        tool.Spatial.select_products(ifcopenshell.util.system.get_system_elements(system))

    @classmethod
    def set_active_edited_system(cls, system: ifcopenshell.entity_instance) -> None:
        cls.get_system_props().edited_system_id = system.id()

    @classmethod
    def set_active_system(cls, system: ifcopenshell.entity_instance) -> None:
        cls.get_system_props().active_system_id = system.id()

    @classmethod
    def get_active_system(cls) -> Union[ifcopenshell.entity_instance, None]:
        system_props = cls.get_system_props()
        return tool.Ifc.get_entity_by_id(system_props.active_system_id)

    @classmethod
    def get_decoration_data(cls) -> dict[str, Any]:
        all_vertices = []
        preview_edges = []
        special_vertices = []
        selected_edges = []
        selected_vertices = []

        view3d_space = tool.Blender.get_viewport_context()["space_data"].region_3d
        viewport_matrix = view3d_space.view_matrix.inverted()
        viewport_y_axis = viewport_matrix.col[1].to_3d().normalized()
        camera_pos = viewport_matrix.translation
        dir_to_camera = lambda x: (camera_pos - x).normalized()

        def most_aligned_vector(a, vectors):
            return max(vectors, key=lambda v: abs(a.dot(v)))

        start_vert_i = 0

        if not ObjectSystemData.is_loaded:
            ObjectSystemData.load()

        if not SystemDecorationData.is_loaded:
            SystemDecorationData.load()

        class FlowDirection(Enum):
            BACKWARD = -1
            FORWARD = 1
            BOTH = 2
            AMBIGUOUS = 0

        connected_elements = ObjectSystemData.data["connected_elements"]

        for element in SystemDecorationData.data["decorated_elements"]:
            start_vert_i = len(all_vertices)
            obj = tool.Ifc.get_object(element)

            # skip stuff without objects, like distribution ports
            if not obj:
                continue

            if obj.hide_get():
                continue

            if not cls.is_mep_element(element):
                continue

            selected_element = element in connected_elements
            verts_pos = []

            port_data = SystemDecorationData.get_element_ports_data(element)
            verts_pos.extend([obj.matrix_world @ data["position"] for data in port_data])

            verts = range(start_vert_i, start_vert_i + len(port_data))
            edges = [(i, i + 1) for i in range(start_vert_i, start_vert_i + len(port_data) - 1)]

            def get_flow_direction(port_data):
                # diagram - https://i.imgur.com/ioYL7bZ.png
                flow_dirs = [p["flow_direction"] for p in port_data]
                unique = set(flow_dirs)
                if len(unique) == 1:
                    if unique == {"SOURCEANDSINK"}:
                        return FlowDirection.BOTH
                    return FlowDirection.AMBIGUOUS
                elif flow_dirs[0] == "SOURCE":
                    return FlowDirection.BACKWARD
                elif flow_dirs[0] == "SINK":
                    return FlowDirection.FORWARD
                elif flow_dirs[1] == "SOURCE":
                    return FlowDirection.FORWARD
                elif flow_dirs[1] == "SINK":
                    return FlowDirection.BACKWARD
                return FlowDirection.AMBIGUOUS

            if (
                len(port_data) == 2
                and selected_element
                and (flow_direction := get_flow_direction(port_data)) != FlowDirection.AMBIGUOUS
            ):
                edge_verts = verts_pos.copy()

                both_directions = flow_direction == FlowDirection.BOTH
                if not both_directions:
                    edge_verts = edge_verts[:: flow_direction.value]

                # create direction lines
                direction_lines_offset = 0.4
                direction_lines_width = 0.05
                base_vert = edge_verts[0]
                edge = edge_verts[1] - edge_verts[0]
                edge_length = edge.length
                edge_dir = edge.normalized()
                # edge_ortho = most_aligned_vector(
                #     viewport_y_axis, (
                #         obj.matrix_world.col[0].to_3d().normalized(),
                #         obj.matrix_world.col[1].to_3d().normalized(),
                # ))

                # for now it's hardcoded to local Y axis to avoid using viewport data
                # for performance reasons
                for j in range(2):
                    edge_ortho = obj.matrix_world.col[j].to_3d().normalized()
                    second_ortho = edge_dir.cross(edge_ortho)
                    edge_ortho = second_ortho.cross(edge_dir)
    
                    # direction lines should be around the edge center
                    n_direction_lines, start_offset = divmod(edge_length, direction_lines_offset)
                    n_direction_lines = int(n_direction_lines) + 1
                    start_offset /= 2
                    start_offset = edge_dir * start_offset + base_vert
                    
                    if both_directions:
                        cur_vert_index = start_vert_i + len(port_data) + j * 2 * n_direction_lines
                    else:
                        cur_vert_index = start_vert_i + len(port_data) + j * 3 * n_direction_lines

                    for i in range(n_direction_lines):
                        cur_offset = start_offset + edge_dir * i * direction_lines_offset
                        if both_directions:
                            verts_pos.append(cur_offset + edge_ortho * direction_lines_width)
                            verts_pos.append(cur_offset - edge_ortho * direction_lines_width)
                            edges.append((cur_vert_index, cur_vert_index + 1))
                            cur_vert_index += 2
                        else:
                            arrow_base = cur_offset - edge_dir * direction_lines_width
                            verts_pos.append(arrow_base + edge_ortho * direction_lines_width)
                            verts_pos.append(cur_offset)
                            verts_pos.append(arrow_base - edge_ortho * direction_lines_width)
                            edges.append((cur_vert_index, cur_vert_index + 1))
                            edges.append((cur_vert_index + 1, cur_vert_index + 2))
                            cur_vert_index += 3

            all_vertices.extend(verts_pos)

            if selected_element:
                selected_vertices.extend(verts)
                selected_edges.extend(edges)
            else:
                special_vertices.extend(verts)
                preview_edges.extend(edges)

        decoration_data = {
            "all_vertices": all_vertices,
            "preview_edges": preview_edges,
            "special_vertices": [all_vertices[i] for i in special_vertices],
            "selected_edges": selected_edges,
            "selected_vertices": [all_vertices[i] for i in selected_vertices],
        }
        return decoration_data

    @classmethod
    def get_connected_elements(
        cls,
        element: ifcopenshell.entity_instance,
        traversed_elements: Optional[set[ifcopenshell.entity_instance]] = None,
    ) -> set[ifcopenshell.entity_instance]:
        """Recursively retrieves all connected elements to the given `element`.

        `traversed_elements` is a set to store connected elements fetched recursively,
        should be `None`"""
        if traversed_elements is None:
            traversed_elements = set((element,))

        connected_elements = ifcopenshell.util.system.get_connected_from(element)
        connected_elements += ifcopenshell.util.system.get_connected_to(element)

        for element in connected_elements:
            if element in traversed_elements:
                continue
            traversed_elements.add(element)
            cls.get_connected_elements(element, traversed_elements)

        return traversed_elements

    @classmethod
    def is_mep_element(cls, element: ifcopenshell.entity_instance) -> bool:
        return element.is_a("IfcFlowSegment") or element.is_a("IfcFlowFitting")

    @classmethod
    def get_flow_element_controls(cls, element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        if not element.HasControlElements:
            return []
        return [control for control in element.HasControlElements[0].RelatedControlElements]

    @classmethod
    def get_flow_control_flow_element(
        cls, element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        if not element.AssignedToFlowElement:
            return
        return element.AssignedToFlowElement[0].RelatingFlowElement

    @classmethod
    def draw_system_ui(cls, layout: bpy.types.UILayout, system_id: int, system_name: str, system_class: str) -> None:
        from bonsai.bim.module.system.ui import SYSTEM_ICONS

        row = layout.row(align=True)
        row.label(text=system_name, icon=SYSTEM_ICONS[system_class])
        op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
        op.system = system_id
        op = row.operator("bim.unassign_system", text="", icon="X")
        op.system = system_id
