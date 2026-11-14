# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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

"""Bring Blender's objects up to date after an MCP edit changed the IFC model.

An edit made through ``ifcopenshell.api`` changes only the IFC model. The
operations recorded in the model's transaction say which entities were
created, edited or deleted; each is traced up its inverse references to the
products and types it belongs to. New ones get objects, removed ones lose
them, and the rest have their name, placement and collection refreshed, or
are imported again when their geometry changed.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import bpy
import ifcopenshell

import bonsai.tool as tool
from bonsai.bim import import_ifc
from bonsai.bim.ifc import IfcStore

# Passing through one of these on the way up to a product means its shape changed.
_SHAPE_CLASSES = ("IfcRepresentation", "IfcProductRepresentation", "IfcRepresentationMap")
_SHAPE_ATTRIBUTES = ("Representation", "RepresentationMaps")
# Relationships that decide where an object sits in Blender, or cut its geometry.
_SHOWN_RELATIONSHIPS = ("IfcRelContainedInSpatialStructure", "IfcRelAggregates", "IfcRelNests", "IfcRelVoidsElement")


@dataclass
class Changes:
    created: set[int] = field(default_factory=set)
    deleted: set[int] = field(default_factory=set)
    # Products and types that still exist, mapped to whether their shape changed.
    edited: dict[int, bool] = field(default_factory=dict)

    def edit(self, element: ifcopenshell.entity_instance, shape: bool) -> None:
        self.edited[element.id()] = self.edited.get(element.id(), False) or shape


def _is_product(element: ifcopenshell.entity_instance) -> bool:
    return element.is_a("IfcProduct") or element.is_a("IfcTypeProduct")


def _ids(value: Any) -> Iterator[int]:
    """Yield the step ids referenced in a value serialised by an ifcopenshell transaction."""
    if isinstance(value, dict):
        if value.get("id"):
            yield value["id"]
        else:
            for v in value.values():
                yield from _ids(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _ids(v)


def _by_id(model: ifcopenshell.file, step_id: int) -> ifcopenshell.entity_instance | None:
    try:
        return model.by_id(step_id)
    except RuntimeError:
        return None


def _shape_class(element: ifcopenshell.entity_instance) -> bool:
    return any(element.is_a(c) for c in _SHAPE_CLASSES)


def _trace(model: ifcopenshell.file, start: ifcopenshell.entity_instance, changes: Changes) -> None:
    """Find the products and types that ``start`` belongs to, without crossing relationships.

    Owner history is shared by everything, and changes nothing Blender shows.
    """
    if start.is_a("IfcRelationship"):
        return _trace_relationship(start, changes)
    if start.is_a("IfcOwnerHistory"):
        return
    queue = [(start, _shape_class(start))]
    seen = {start.id()}
    while queue:
        element, shape = queue.pop()
        if _is_product(element):
            changes.edit(element, shape)
            continue
        for inverse in model.get_inverse(element):
            if inverse.id() in seen or inverse.is_a("IfcRelationship"):
                continue
            seen.add(inverse.id())
            queue.append((inverse, shape or _shape_class(inverse)))


def _trace_relationship(rel: ifcopenshell.entity_instance, changes: Changes) -> None:
    """Refresh the products a relationship links, whose container or openings may have changed."""
    if not any(rel.is_a(c) for c in _SHOWN_RELATIONSHIPS):
        return
    for attribute in rel:
        for element in attribute if isinstance(attribute, tuple) else [attribute]:
            if isinstance(element, ifcopenshell.entity_instance) and _is_product(element):
                changes.edit(element, False)
    if rel.is_a("IfcRelVoidsElement"):
        changes.edit(rel.RelatingBuildingElement, True)


def find_changes(model: ifcopenshell.file, operations: list[dict[str, Any]]) -> Changes:
    """Work out which products and types an edit created, deleted or changed."""
    changes = Changes()
    traced: list[int] = []
    # Products that a changed relationship no longer refers to, so cannot be traced to.
    dropped: list[int] = []
    for operation in operations:
        action = operation["action"]
        if action == "create":
            changes.created.add(operation["value"]["id"])
            traced.append(operation["value"]["id"])
        elif action == "edit":
            traced.append(operation["id"])
            element = _by_id(model, operation["id"])
            if element is None:
                continue
            if _is_product(element):
                changes.edit(element, element.attribute_name(operation["index"]) in _SHAPE_ATTRIBUTES)
            elif any(element.is_a(c) for c in _SHOWN_RELATIONSHIPS):
                dropped.extend(_ids(operation["old"]))
        elif action == "delete":
            value = operation["value"]
            changes.deleted.add(value["id"])
            if value["type"] in _SHOWN_RELATIONSHIPS:
                dropped.extend(i for k, v in value.items() if k not in ("id", "type") for i in _ids(v))
            if value["type"] == "IfcRelVoidsElement" and (
                wall := _by_id(model, value["RelatingBuildingElement"]["id"])
            ):
                changes.edit(wall, True)
            # Those that referred to it lost the reference.
            traced.extend(operation.get("inverses") or {})
        elif action == "batch_delete":
            traced.extend(operation["inverses"])
    for step_id in traced:
        if (element := _by_id(model, step_id)) is not None:
            _trace(model, element, changes)
    for step_id in dropped:
        if (element := _by_id(model, step_id)) is not None and _is_product(element):
            changes.edit(element, False)
    for step_id in list(changes.edited):
        element = model.by_id(step_id)
        if element.is_a("IfcOpeningElement"):
            for rel in element.VoidsElements:
                changes.edit(rel.RelatingBuildingElement, True)
    # Only what exists now: an entity may be created and deleted by the same edit.
    changes.created = {
        i
        for i in changes.created
        if (e := _by_id(model, i)) is not None and _is_product(e) and not e.is_a("IfcFeatureElementSubtraction")
    }
    changes.deleted = {i for i in changes.deleted if _by_id(model, i) is None}
    # Bonsai loads no object for some products, such as openings: there is nothing to refresh.
    changes.edited = {
        i: shape for i, shape in changes.edited.items() if i not in changes.created and IfcStore.get_element(i)
    }
    return changes


def _remove_object(step_id: int, global_id: str | None = None) -> None:
    obj = IfcStore.get_element(step_id)
    IfcStore.id_map.pop(step_id, None)
    if global_id:
        IfcStore.guid_map.pop(global_id, None)
    if obj is None or not isinstance(obj, bpy.types.Object):
        return
    if collection := tool.Blender.get_object_bim_props(obj).collection:
        _remove_collection(collection)
    tool.Ifc.unlink(obj=obj)
    bpy.data.objects.remove(obj)


def _remove_collection(collection: bpy.types.Collection) -> None:
    """Remove a spatial element's collection, moving what it holds to its parents until they are refreshed."""
    scene_collection = bpy.context.scene.collection
    parents = [c for c in [scene_collection, *bpy.data.collections] if collection.name in c.children]
    for parent in parents:
        for child in collection.children:
            if child.name not in parent.children:
                parent.children.link(child)
        for obj in collection.objects:
            if obj.name not in parent.objects:
                parent.objects.link(obj)
    bpy.data.collections.remove(collection)


def _import(model: ifcopenshell.file, elements: set[ifcopenshell.entity_instance]) -> None:
    """Create objects for products and types, as appending them from a library does."""
    settings = import_ifc.IfcImportSettings.factory(bpy.context, tool.Ifc.get_path(), logging.getLogger("ImportIFC"))
    importer = import_ifc.IfcImporter(settings)
    importer.file = model
    importer.process_context_filter()
    importer.material_creator.load_existing_materials()
    for style in model.by_type("IfcSurfaceStyle"):
        if IfcStore.get_element(style.id()) is None:
            importer.create_style(style)
    types = {e for e in elements if e.is_a("IfcTypeProduct")}
    for element_type in types:
        importer.create_element_type(element_type)
    if products := elements - types:
        importer.create_generic_elements(products)
    importer.place_objects_in_collections()


def _refresh(element: ifcopenshell.entity_instance, obj: bpy.types.Object) -> None:
    tool.Root.set_object_name(obj, element)
    if element.is_a("IfcProduct") and element.ObjectPlacement:
        tool.Geometry.restore_placement_from_ifc(obj, element)
    tool.Collector.assign(obj)


def apply(model: ifcopenshell.file, changes: Changes) -> None:
    """Create, remove and refresh objects to match ``changes``."""
    for step_id in changes.deleted:
        _remove_object(step_id)
    reimport = set()
    for step_id, shape in changes.edited.items():
        element = model.by_id(step_id)
        obj = IfcStore.get_element(step_id)
        if not isinstance(obj, bpy.types.Object):
            continue
        # Spatial containers own collections: refresh them in place rather than import them again.
        if shape and (element.is_a("IfcSpace") or not element.is_a("IfcSpatialStructureElement")):
            _remove_object(step_id, getattr(element, "GlobalId", None))
            reimport.add(element)
        else:
            _refresh(element, obj)
    reimport |= {model.by_id(i) for i in changes.created}
    if reimport:
        _import(model, reimport)
