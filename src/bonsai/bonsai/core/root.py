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

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell

    import bonsai.tool as tool


def copy_class(
    ifc: type[tool.Ifc],
    collector: type[tool.Collector],
    geometry: type[tool.Geometry],
    root: type[tool.Root],
    obj: bpy.types.Object,
) -> ifcopenshell.entity_instance | None:
    element = ifc.get_entity(obj)
    if not element:
        return
    if root.is_element_a(element, "IfcRelSpaceBoundary"):
        new = ifc.run("boundary.copy_boundary", boundary=element)
        ifc.link(new, obj)
        return new
    representation = root.get_object_representation(obj)

    def _ctx_str(rep):
        c = rep.ContextOfItems
        return f"{c.ContextType}/{c.ContextIdentifier}/{getattr(c, 'TargetView', None)}"

    _src_reps = element.Representation.Representations if element.Representation else []
    print(f"[copy_class] source {element.is_a()} #{element.id()} reps: {[_ctx_str(r) for r in _src_reps]}")

    new = ifc.run("root.copy_class", product=element)
    ifc.link(new, obj)
    relating_type = root.get_element_type(new)
    if relating_type and root.does_type_have_representations(relating_type):
        _type_ctxs = [_ctx_str(rm.MappedRepresentation) for rm in (relating_type.RepresentationMaps or [])]
        print(f"[copy_class] TYPE branch: type #{relating_type.id()} RepresentationMaps ctxs: {_type_ctxs}")
        _dropped = [_ctx_str(r) for r in _src_reps if _ctx_str(r) not in _type_ctxs]
        print(f"[copy_class] TYPE branch: occurrence-only reps that will be DROPPED: {_dropped}")
        ifc.run("type.map_type_representations", related_object=new, relating_type=relating_type)
        # map_type_representations wipes the occurrence's own representations and
        # only re-maps the type's, so occurrence-specific representations (e.g. a
        # per-occurrence Model/Body/PLAN_VIEW) would be lost. Re-add them.
        root.copy_occurrence_only_representations(element, new, relating_type)
        _new_reps = new.Representation.Representations if new.Representation else []
        print(f"[copy_class] TYPE branch: new #{new.id()} reps after mapping+merge: {[_ctx_str(r) for r in _new_reps]}")
        root.link_object_data(ifc.get_object(relating_type), obj)
    elif representation:
        copied_entities = root.copy_representation(element, new)
        data = geometry.duplicate_object_data(obj)
        if data:
            geometry.copy_data_links(data, copied_entities)
            geometry.change_object_data(obj, data, is_global=True)
            geometry.rename_object(data, geometry.get_representation_name(ifc.get_entity(data)))
        # Only assign styles if element doesn't get them from material
        if not root.has_material_styles(new):
            root.assign_body_styles(new, obj)
    collector.assign(obj)
    return new


def assign_class(
    ifc: type[tool.Ifc],
    collector: type[tool.Collector],
    root: type[tool.Root],
    obj: bpy.types.Object,
    ifc_class: str,
    context: Optional[ifcopenshell.entity_instance] = None,
    predefined_type: Optional[str] = None,
    should_add_representation: bool = True,
    ifc_representation_class: Optional[str] = None,
) -> Optional[ifcopenshell.entity_instance]:
    """
    :param context: is not optional if ``should_add_representation`` is True

    TODO: Do NOT use should_add_representation. Because it internally calls
    geometry.add_representation which is 1,000 lines of Blender -> IFC magic.
    Instead, explicitly create a representation using tool.Geometry.
    """
    if ifc.get_entity(obj):
        return

    name = root.get_object_name(obj)
    element = ifc.run("root.create_entity", ifc_class=ifc_class, predefined_type=predefined_type, name=name)
    root.set_object_name(obj, element)
    ifc.link(element, obj)

    if should_add_representation:
        assert context, "Context is required for adding a representation"
        root.run_geometry_add_representation(
            obj=obj, context=context, ifc_representation_class=ifc_representation_class, profile_set_usage=None
        )

    if not root.is_drawing_annotation(element) and (default_container := root.get_default_container()):
        if root.is_spatial_element(element):
            ifc.run("aggregate.assign_object", products=[element], relating_object=default_container)
        elif root.is_containable(element):
            ifc.run("spatial.assign_container", products=[element], relating_structure=default_container)
            if relating_obj := root.is_in_aggregate_mode(element):
                ifc.run("aggregate.assign_object", products=[element], relating_object=relating_obj)
            if relating_obj := root.is_in_nest_mode(element):
                ifc.run("nest.assign_object", related_objects=[element], relating_object=relating_obj)
    collector.assign(obj)
    return element
