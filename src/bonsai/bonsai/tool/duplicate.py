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

# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import bpy
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation

import bonsai.core.geometry
import bonsai.core.tool
import bonsai.tool as tool


@dataclass
class DecompositionRecord:
    type: Literal["fill"]
    element: ifcopenshell.entity_instance


@dataclass
class ConnectionRecord:
    type: Literal["path"]
    relating_element: ifcopenshell.entity_instance
    related_element: ifcopenshell.entity_instance
    relating_connection_type: str
    related_connection_type: str
    relating_priorities: list[int]
    related_priorities: list[int]


@dataclass
class PortConnectionRecord:
    relating_port_index: int
    related_element: ifcopenshell.entity_instance
    related_port_index: int
    direction: str


@dataclass
class PortConnectionSnapshot:
    """Port-to-port connections and per-element port counts captured before duplication."""

    by_element: dict[ifcopenshell.entity_instance, list[PortConnectionRecord]] = field(default_factory=dict)
    port_counts: dict[ifcopenshell.entity_instance, int] = field(default_factory=dict)


class Duplicate(bonsai.core.tool.Duplicate):

    _pending_warnings: list[str] = []

    @classmethod
    def _emit_warning(cls, message: str) -> None:
        """Buffer a warning for later retrieval by an operator. Falling through
        to a print keeps the message in the Blender console for the headless /
        no-operator code path."""
        cls._pending_warnings.append(message)
        print(f"Bonsai: WARNING — {message}")

    @classmethod
    def consume_warnings(cls) -> list[str]:
        """Return and clear the buffered warnings — operators call this after
        ``tool.Geometry.duplicate_ifc_objects`` to forward each to ``self.report``."""
        warnings = cls._pending_warnings
        cls._pending_warnings = []
        return warnings

    @classmethod
    def get_decomposition_relationships(
        cls, objs: list[bpy.types.Object]
    ) -> dict[ifcopenshell.entity_instance, DecompositionRecord]:
        relationships: dict[ifcopenshell.entity_instance, DecompositionRecord] = {}
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if building := tool.Spatial.get_host_element(element):
                relationships[element] = DecompositionRecord(type="fill", element=building)
        return relationships

    @classmethod
    def get_connection_relationships(
        cls, objs: list[bpy.types.Object]
    ) -> dict[ifcopenshell.entity_instance, ConnectionRecord]:
        relationships: dict[ifcopenshell.entity_instance, ConnectionRecord] = {}
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if hasattr(element, "ConnectedTo") and element.ConnectedTo:
                paths = [
                    connection for connection in element.ConnectedTo if connection.is_a("IfcRelConnectsPathElements")
                ]
                for path in paths:
                    relationships[element] = ConnectionRecord(
                        type="path",
                        relating_element=path.RelatingElement,
                        related_element=path.RelatedElement,
                        relating_connection_type=path.RelatingConnectionType,
                        related_connection_type=path.RelatedConnectionType,
                        relating_priorities=list(path.RelatingPriorities or []),
                        related_priorities=list(path.RelatedPriorities or []),
                    )
        return relationships

    @classmethod
    def get_port_connection_relationships(cls, objs: list[bpy.types.Object]) -> PortConnectionSnapshot:
        """Snapshot ``IfcRelConnectsPorts`` among MEP elements in ``objs``, indexed for positional-port replay onto duplicates."""
        # Function-local: top-level import would trigger a partial-init cycle.
        from bonsai.tool.system import direction_from_port_pair

        snapshot = PortConnectionSnapshot()
        elements_in_set: set[ifcopenshell.entity_instance] = set()
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if element is not None and tool.System.is_mep_element(element):
                elements_in_set.add(element)
        if not elements_in_set:
            return snapshot

        ordered_elements = sorted(elements_in_set, key=lambda e: e.id())
        for element in ordered_elements:
            snapshot.port_counts[element] = len(tool.System.get_ports(element))

        seen: set[tuple[tuple[int, int], tuple[int, int]]] = set()
        for element in ordered_elements:
            ports = tool.System.get_ports(element)
            for port_index, port in enumerate(ports):
                connected_port = tool.System.get_connected_port(port)
                if connected_port is None:
                    continue
                other_element = tool.System.get_port_relating_element(connected_port)
                if other_element is None or other_element not in elements_in_set:
                    continue
                other_ports = tool.System.get_ports(other_element)
                try:
                    other_port_index = other_ports.index(connected_port)
                except ValueError:
                    continue
                pair_key = tuple(
                    sorted(
                        [
                            (element.id(), port_index),
                            (other_element.id(), other_port_index),
                        ]
                    )
                )
                if pair_key in seen:
                    continue
                seen.add(pair_key)

                snapshot.by_element.setdefault(element, []).append(
                    PortConnectionRecord(
                        relating_port_index=port_index,
                        related_element=other_element,
                        related_port_index=other_port_index,
                        direction=direction_from_port_pair(port, connected_port),
                    )
                )
        return snapshot

    @classmethod
    def recreate_decompositions(
        cls,
        relationships: dict[ifcopenshell.entity_instance, DecompositionRecord],
        old_to_new: dict[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]],
    ) -> None:
        for subelement, data in relationships.items():
            new_subelements = old_to_new.get(subelement)
            new_elements = old_to_new.get(data.element)
            if not new_subelements or not new_elements:
                continue
            for i, new_subelement in enumerate(new_subelements):
                new_element = new_elements[i]
                if data.type == "fill":
                    element = new_element
                    filling = new_subelement
                    voided_obj = tool.Ifc.get_object(new_element)
                    filling_obj = tool.Ifc.get_object(new_subelement)

                    existing_opening_occurrence = subelement.FillsVoids[0].RelatingOpeningElement
                    opening = tool.Ifc.run("root.copy_class", product=existing_opening_occurrence)
                    tool.Ifc.run(
                        "geometry.edit_object_placement",
                        product=opening,
                        matrix=ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement),
                        is_si=False,
                    )

                    representation = ifcopenshell.util.representation.get_representation(
                        existing_opening_occurrence, "Model", "Body", "MODEL_VIEW"
                    )
                    representation = ifcopenshell.util.representation.resolve_representation(representation)
                    mapped_representation = tool.Ifc.run("geometry.map_representation", representation=representation)
                    tool.Ifc.run(
                        "geometry.assign_representation",
                        product=opening,
                        representation=mapped_representation,
                    )
                    tool.Ifc.run("feature.add_feature", feature=opening, element=element)
                    tool.Ifc.run("feature.add_filling", opening=opening, element=filling)

                    voided_objs = [voided_obj]
                    # Openings affect all subelements of an aggregate
                    for child_subelement in ifcopenshell.util.element.get_decomposition(element):
                        subobj = tool.Ifc.get_object(child_subelement)
                        if subobj:
                            voided_objs.append(subobj)

                    for voided_obj in voided_objs:
                        if mesh_data := voided_obj.data:
                            representation = tool.Ifc.get().by_id(
                                tool.Geometry.get_mesh_props(mesh_data).ifc_definition_id
                            )
                            bonsai.core.geometry.switch_representation(
                                tool.Ifc,
                                tool.Geometry,
                                obj=voided_obj,
                                representation=representation,
                            )

    @classmethod
    def recreate_connections(
        cls,
        relationship: dict[ifcopenshell.entity_instance, ConnectionRecord],
        old_to_new: dict[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]],
    ) -> None:
        for element, data in relationship.items():
            new_relating_elements = old_to_new.get(data.relating_element) or []
            new_related_elements = old_to_new.get(data.related_element) or []
            # connect_path hardcodes priorities to []; restore them post-hoc.
            priority_attrs: dict[str, Any] = {}
            if data.relating_priorities:
                priority_attrs["RelatingPriorities"] = data.relating_priorities
            if data.related_priorities:
                priority_attrs["RelatedPriorities"] = data.related_priorities
            for new_relating_element, new_related_element in zip(new_relating_elements, new_related_elements):
                new_rel = tool.Ifc.run(
                    "geometry.connect_path",
                    relating_element=new_relating_element,
                    related_element=new_related_element,
                    relating_connection=data.relating_connection_type,
                    related_connection=data.related_connection_type,
                )
                if new_rel is not None and priority_attrs:
                    try:
                        tool.Ifc.run("attribute.edit_attributes", product=new_rel, attributes=priority_attrs)
                    except (RuntimeError, ifcopenshell.Error) as e:
                        cls._emit_warning(
                            f"connection priority restore failed for {new_rel}; "
                            f"duplicate has empty RelatingPriorities/RelatedPriorities: {e}"
                        )

    @classmethod
    def recreate_port_connections(
        cls,
        snapshot: PortConnectionSnapshot,
        old_to_new: dict[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]],
    ) -> None:
        """Recreate ``IfcRelConnectsPorts`` between duplicates; skip records whose duplicate's port count diverges from the snapshot."""
        for relating_element, records in snapshot.by_element.items():
            new_relatings = old_to_new.get(relating_element) or []
            expected_relating = snapshot.port_counts.get(relating_element)
            for record in records:
                related_element = record.related_element
                new_relateds = old_to_new.get(related_element) or []
                expected_related = snapshot.port_counts.get(related_element)
                for new_relating, new_related in zip(new_relatings, new_relateds):
                    new_relating_ports = tool.System.get_ports(new_relating)
                    new_related_ports = tool.System.get_ports(new_related)

                    if expected_relating is not None and len(new_relating_ports) != expected_relating:
                        cls._emit_warning(
                            f"port reconnect skipped — duplicate has {len(new_relating_ports)} ports, "
                            f"snapshot had {expected_relating}"
                        )
                        continue
                    if expected_related is not None and len(new_related_ports) != expected_related:
                        cls._emit_warning(
                            f"port reconnect skipped — duplicate has {len(new_related_ports)} ports, "
                            f"snapshot had {expected_related}"
                        )
                        continue

                    try:
                        new_port_a = new_relating_ports[record.relating_port_index]
                        new_port_b = new_related_ports[record.related_port_index]
                    except IndexError:
                        cls._emit_warning(
                            f"port reconnect skipped — record references port index past the duplicate's port list"
                        )
                        continue
                    try:
                        tool.Ifc.run(
                            "system.connect_port",
                            port1=new_port_a,
                            port2=new_port_b,
                            direction=record.direction or "NOTDEFINED",
                        )
                    except (RuntimeError, ifcopenshell.Error) as e:
                        cls._emit_warning(f"port reconnect failed between duplicates: {e}")
