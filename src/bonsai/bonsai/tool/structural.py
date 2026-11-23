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

import json
import math
from typing import TYPE_CHECKING, Any, Union

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.structural
import ifcopenshell.util.attribute
import ifcopenshell.util.representation
import ifcopenshell.util.structural
import numpy as np
from mathutils import Matrix, Vector

import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from ifcopenshell.api.structural.edit_structural_boundary_condition import (
        AttributeDict,
    )

    from bonsai.bim.module.structural.prop import (
        BIMObjectStructuralProperties,
        BIMStructuralProperties,
    )


class Structural(bonsai.core.tool.Structural):
    @classmethod
    def get_structural_props(cls) -> BIMStructuralProperties:
        return bpy.context.scene.BIMStructuralProperties

    @classmethod
    def get_object_structural_props(cls, obj: bpy.types.Object) -> BIMObjectStructuralProperties:
        return obj.BIMStructuralProperties

    @classmethod
    def get_default_item_axes(cls, edge: Vector) -> Matrix:
        """A curve item's local axes before any roll, as columns: x along its edge, z as near up as is square to it.

        :param edge: The edge's direction, in the item's own coordinates.
        """
        return edge.normalized().to_track_quat("X", "Z").to_matrix()

    @classmethod
    def get_item_axis_roll(cls, edge: Vector, axis: Vector) -> Union[float, None]:
        """The angle in degrees a curve item's local axes are rolled about its edge from their default, for its z
        axis to be its Axis, or None if its Axis gives no z axis, being along the edge.

        As IFC defines a curve item's local axes, z is Axis less its component along the edge, so an Axis a little
        off square is projected rather than refused. Both are in the item's own coordinates.
        """
        x = edge.normalized()
        z = axis.normalized()
        z = z - z.dot(x) * x
        if z.length < 1e-6:
            return None
        default = cls.get_default_item_axes(edge)
        # Rolled by a about x, z becomes cos(a) z0 - sin(a) y0.
        return math.degrees(math.atan2(-z.dot(default.col[1]), z.dot(default.col[2])))

    @classmethod
    def get_item_axes(cls, obj: bpy.types.Object, roll: float) -> Matrix:
        """The world matrix of a curve item's local axes at its edge's start, rolled about the edge by degrees"""
        start, end = obj.data.vertices[0].co, obj.data.vertices[1].co
        axes = cls.get_default_item_axes(end - start) @ Matrix.Rotation(math.radians(roll), 3, "X")
        return obj.matrix_world @ Matrix.Translation(start) @ axes.to_4x4()

    @classmethod
    def turn_axis_off_edge(
        cls, item: ifcopenshell.entity_instance, start: tuple[float, ...], end: tuple[float, ...]
    ) -> None:
        """Give a curve item its default Axis when its edge has come to lie along its Axis.

        An Axis along the edge gives no local z, as when the end of a new, horizontal edge is moved straight up to
        make a column. It is then replaced by the default local z, as Edit Axis shows it at 0 degrees. An Axis that
        gives a local z is kept, as is everything in IFC2X3, which has no Axis.

        :param item: An IfcStructuralCurveMember or IfcStructuralCurveConnection; other items are left alone.
        :param start: The edge's start, in the item's own coordinates.
        :param end: The edge's end, in the item's own coordinates.
        """
        if not (item.is_a("IfcStructuralCurveMember") or item.is_a("IfcStructuralCurveConnection")):
            return
        if tool.Ifc.get_schema() == "IFC2X3":
            return
        edge = Vector(end) - Vector(start)
        if edge.length < 1e-9:
            return
        if item.Axis and cls.get_item_axis_roll(edge, Vector(item.Axis.DirectionRatios)) is not None:
            return
        axis = cls.get_default_item_axes(edge).col[2]
        ifcopenshell.api.structural.edit_structural_item_axis(tool.Ifc.get(), structural_item=item, axis=tuple(axis))

    @classmethod
    def disable_editing_structural_analysis_model(cls) -> None:
        props = cls.get_structural_props()
        props.active_structural_analysis_model_id = 0

    @classmethod
    def disable_structural_analysis_model_editing_ui(cls) -> None:
        props = cls.get_structural_props()
        props.is_editing = False

    @classmethod
    def enable_editing_structural_analysis_model(cls, model: Union[int, None]) -> None:
        if model:
            props = cls.get_structural_props()
            props.active_structural_analysis_model_id = model

    @classmethod
    def enable_structural_analysis_model_editing_ui(cls) -> None:
        props = cls.get_structural_props()
        props.is_editing = True

    @classmethod
    def enabled_structural_analysis_model_editing_ui(cls) -> bool:
        props = cls.get_structural_props()
        return props.is_editing

    @classmethod
    def ensure_representation_contexts(cls) -> None:
        ifc_file = tool.Ifc.get()
        model = ifcopenshell.util.representation.get_context(ifc_file, "Model")
        if not model:
            model = ifcopenshell.api.context.add_context(
                ifc_file,
                context_type="Model",
                context_identifier="",
                target_view="",
                parent=0,
            )
        graph = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Reference", "GRAPH_VIEW")
        if not graph:
            model = ifcopenshell.api.context.add_context(
                ifc_file,
                context_type="Model",
                context_identifier="Reference",
                target_view="GRAPH_VIEW",
                parent=model,
            )

    @classmethod
    def get_active_structural_analysis_model(cls) -> ifcopenshell.entity_instance:
        props = cls.get_structural_props()
        model = tool.Ifc.get().by_id(props.active_structural_analysis_model_id)
        return model

    @classmethod
    def is_load_case(cls, group: ifcopenshell.entity_instance) -> bool:
        """Whether a load group is a load case: an IfcStructuralLoadCase, or a load group typed LOAD_CASE, as
        some programs, such as RFEM, write them"""
        return group.is_a("IfcStructuralLoadCase") or (
            group.is_a("IfcStructuralLoadGroup") and group.PredefinedType == "LOAD_CASE"
        )

    @classmethod
    def get_load_cases(
        cls, model: Union[ifcopenshell.entity_instance, None] = None
    ) -> list[ifcopenshell.entity_instance]:
        """The load groups loading an analysis model. Without a model, every load case.

        These are the groups the model is loaded by. Some programs, such as RFEM, leave LoadedBy empty: then they
        are the load cases that no model lists and whose loads are all on items of this model and of no other,
        and the load combinations that no model lists and whose load cases are all among them. A case that could
        belong to more than one model is left out rather than guessed."""
        ifc_file = tool.Ifc.get()
        cases = [g for g in ifc_file.by_type("IfcStructuralLoadGroup") if cls.is_load_case(g)]
        if model is None:
            return cases
        if loaded_by := ifcopenshell.util.structural.get_model_load_groups(model):
            return loaded_by
        models = {
            m: set(ifcopenshell.util.structural.get_model_items(m))
            for m in ifc_file.by_type("IfcStructuralAnalysisModel")
        }
        inferred = []
        for case in cases:
            if case.LoadGroupFor:
                continue
            activities = ifcopenshell.util.structural.get_group_activities(case)
            loaded = {ifcopenshell.util.structural.get_activity_item(a) for a in activities} - {None}
            if loaded and [m for m, items in models.items() if loaded <= items] == [model]:
                inferred.append(case)
        for combination in ifc_file.by_type("IfcStructuralLoadGroup"):
            if combination.PredefinedType != "LOAD_COMBINATION" or combination.LoadGroupFor:
                continue
            combined = ifcopenshell.util.structural.get_combination_factors(combination)
            if combined and all(c in inferred for c in combined):
                inferred.append(combination)
        return inferred

    @classmethod
    def get_model_rotation(cls, load: ifcopenshell.entity_instance) -> Union[np.ndarray, None]:
        """The rotation from the axes of the analysis model a load acts in to Blender's, where they differ. IFC gives
        global load components in the model's axes, set by its SharedPlacement; RFEM, for one, points Z down."""
        for activity in tool.Ifc.get().get_inverse(load):
            if not activity.is_a("IfcStructuralActivity") or activity.GlobalOrLocal == "LOCAL_COORDS":
                continue
            rotation = ifcopenshell.util.structural.get_global_axes(activity)
            return None if np.allclose(rotation, np.eye(3)) else rotation
        return None

    @classmethod
    def to_blender_axes(cls, load: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> dict[str, Any]:
        """Load attributes with their X, Y and Z components turned from the axes of the load's model to Blender's"""
        return cls.turn_load_attributes(load, attributes, to_model=False)

    @classmethod
    def to_model_axes(cls, load: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> dict[str, Any]:
        """Load attributes with their X, Y and Z components turned from Blender's axes to those of the load's model"""
        return cls.turn_load_attributes(load, attributes, to_model=True)

    @classmethod
    def turn_load_attributes(
        cls, load: ifcopenshell.entity_instance, attributes: dict[str, Any], to_model: bool
    ) -> dict[str, Any]:
        attributes = dict(attributes)
        if (rotation := cls.get_model_rotation(load)) is None:
            return attributes
        for prefix in ("Force", "Moment", "LinearForce", "LinearMoment", "PlanarForce"):
            keys = [f"{prefix}{axis}" for axis in "XYZ"]
            if any(k in attributes for k in keys):
                vector = np.array([attributes.get(k) or 0.0 for k in keys])
                vector = (rotation.T if to_model else rotation) @ vector
                # A zero the file gave stays one; one it left unset stays unset.
                given = [attributes.get(k) is not None for k in keys]
                attributes.update({k: float(v) if (v or g) else None for k, v, g in zip(keys, vector, given)})
        return attributes

    @classmethod
    def get_force(cls, load: ifcopenshell.entity_instance) -> tuple[float, float, float]:
        """A single force load's force, in Blender's axes"""
        attributes = cls.to_blender_axes(load, {a: getattr(load, a) for a in ("ForceX", "ForceY", "ForceZ")})
        return tuple(attributes[a] or 0.0 for a in ("ForceX", "ForceY", "ForceZ"))

    # The applied load each kind of structural item takes, and the loads it can take.
    APPLIED_LOADS = {
        "IfcStructuralPointConnection": (
            "IfcStructuralPointAction",
            ("IfcStructuralLoadTemperature", "IfcStructuralLoadSingleForce", "IfcStructuralLoadSingleDisplacement"),
        ),
        "IfcStructuralCurveMember": (
            "IfcStructuralLinearAction",
            ("IfcStructuralLoadTemperature", "IfcStructuralLoadLinearForce"),
        ),
        "IfcStructuralSurfaceMember": (
            "IfcStructuralPlanarAction",
            ("IfcStructuralLoadTemperature", "IfcStructuralLoadPlanarForce"),
        ),
    }

    @classmethod
    def get_load_targets(
        cls,
        objects: list[bpy.types.Object],
        load: Union[ifcopenshell.entity_instance, None],
        group: Union[ifcopenshell.entity_instance, None],
    ) -> list[ifcopenshell.entity_instance]:
        """The structural items of these objects a load would be applied to in a load group: those that can take it
        and don't already have it there"""
        if not load or not group:
            return []
        targets = []
        for obj in objects:
            if not (element := tool.Ifc.get_entity(obj)) or element.is_a() not in cls.APPLIED_LOADS:
                continue
            if not any(load.is_a(c) for c in cls.APPLIED_LOADS[element.is_a()][1]):
                continue
            if any(a.AppliedLoad == load for a in cls.get_group_activities(element, group)):
                continue
            targets.append(element)
        return targets

    @classmethod
    def follow_active_item_load(cls) -> None:
        """While a load group's applied loads are being edited, set its load picker to the first load the active
        structural item has there, so the picker shows the load at the item selected. Only Blender properties change.
        """
        props = cls.get_structural_props()
        if props.load_group_editing_type == "ACTIVITY" and props.active_load_group_id:
            group_id = props.active_load_group_id
        else:
            group_id = props.active_load_case_id
        obj = bpy.context.active_object
        if not group_id or not obj or not (element := tool.Ifc.get_entity(obj)):
            return
        if element.is_a() not in cls.APPLIED_LOADS:
            return
        try:
            group = tool.Ifc.get().by_id(group_id)
        except RuntimeError:
            return
        load = next((a.AppliedLoad for a in cls.get_group_activities(element, group) if a.AppliedLoad), None)
        if not load or not load.Name:
            return  # The picker lists named loads only.
        try:
            if props.applicable_structural_load_types != load.is_a():
                props.applicable_structural_load_types = load.is_a()
            props.applicable_structural_loads = str(load.id())
        except TypeError:
            pass  # Not offered for the current selection.

    @classmethod
    def get_group_activities(
        cls, item: ifcopenshell.entity_instance, group: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        """The applied loads on a structural item in a load case or load group, directly or through a load group
        within it"""

        def is_in_group(activity: ifcopenshell.entity_instance) -> bool:
            for rel in activity.HasAssignments:
                if not rel.is_a("IfcRelAssignsToGroup") or not (assigned := rel.RelatingGroup):
                    continue
                if assigned == group or any(
                    r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup == group for r in assigned.HasAssignments
                ):
                    return True
            return False

        activities = [r.RelatedStructuralActivity for r in item.AssignedStructuralActivity]
        return [a for a in activities if a and is_in_group(a)]

    @classmethod
    def get_structural_item_predefined_types(cls, ifc_class: str) -> list[str]:
        """The predefined types an item of this class can be added with, USERDEFINED left out."""
        declaration = tool.Ifc.schema().declaration_by_name(ifc_class).as_entity()
        assert declaration
        for attribute in declaration.all_attributes():
            if attribute.name() == "PredefinedType":
                return [t for t in ifcopenshell.util.attribute.get_enum_items(attribute) if t != "USERDEFINED"]
        return []

    @classmethod
    def get_structural_item_representation_template(cls, ifc_class: str) -> str:
        """The Add Element representation template for the topology of a structural item."""
        if ifc_class.startswith("IfcStructuralPoint"):
            return "VERTEX"
        elif ifc_class.startswith("IfcStructuralCurve"):
            return "EDGE"
        elif ifc_class.startswith("IfcStructuralSurface"):
            return "FACE"
        raise ValueError(f"{ifc_class} is not a point, curve or surface structural item")

    @classmethod
    def get_member_connections_to_add(
        cls, elements: list[ifcopenshell.entity_instance]
    ) -> list[tuple[ifcopenshell.entity_instance, ifcopenshell.entity_instance]]:
        """The (member, connection) pairs to connect among the elements, leaving out those already connected.

        Either one member is connected to every connection, or one connection to every member: with
        several of both it cannot be told which member meets which connection.

        :raises ValueError: if the elements are not members and connections, one of them alone.
        """
        members = [e for e in elements if e.is_a("IfcStructuralMember")]
        connections = [e for e in elements if e.is_a("IfcStructuralConnection")]
        if not members or not connections:
            raise ValueError("Select structural members and the connection that joins them.")
        if len(members) > 1 and len(connections) > 1:
            raise ValueError("Select one connection with its members, or one member with its connections.")
        pairs = []
        for member in members:
            connected = ifcopenshell.util.structural.get_member_connections(member)
            pairs.extend((member, c) for c in connections if c not in connected)
        return pairs

    @classmethod
    def get_structural_items(cls, elements: list[ifcopenshell.entity_instance]) -> list[ifcopenshell.entity_instance]:
        """The structural items among the elements."""
        return [e for e in elements if e.is_a("IfcStructuralItem")]

    @classmethod
    def is_in_structural_analysis_model(
        cls, element: ifcopenshell.entity_instance, model: ifcopenshell.entity_instance
    ) -> bool:
        """Whether the element is assigned to the structural analysis model."""
        return model in ifcopenshell.util.structural.get_analysis_models(element)

    @classmethod
    def get_current_structural_analysis_model(cls) -> Union[ifcopenshell.entity_instance, None]:
        """Get the model that new structural items and load cases are assigned to.

        Falls back to the only model in the project when none has been chosen.
        """
        ifc_file = tool.Ifc.get()
        if model_id := cls.get_structural_props().current_structural_analysis_model_id:
            try:
                model = ifc_file.by_id(model_id)
                if model.is_a("IfcStructuralAnalysisModel"):
                    return model
            except RuntimeError:
                pass
        models = ifc_file.by_type("IfcStructuralAnalysisModel")
        return models[0] if len(models) == 1 else None

    @classmethod
    def set_current_structural_analysis_model(cls, model: ifcopenshell.entity_instance) -> None:
        cls.get_structural_props().current_structural_analysis_model_id = model.id()

    @classmethod
    def assign_to_current_structural_analysis_model(cls, element: ifcopenshell.entity_instance) -> None:
        if not (model := cls.get_current_structural_analysis_model()):
            return
        if element.is_a("IfcStructuralLoadGroup"):
            ifcopenshell.api.structural.assign_structural_load_group(
                tool.Ifc.get(), load_groups=[element], structural_analysis_model=model
            )
        elif element.is_a("IfcStructuralItem"):
            ifcopenshell.api.structural.assign_structural_analysis_model(
                tool.Ifc.get(), products=[element], structural_analysis_model=model
            )

    @classmethod
    def get_ifc_structural_analysis_model_attributes(cls, model: Union[int, None]) -> Union[dict[str, Any], None]:
        if model:
            ifc_model = tool.Ifc.get().by_id(model)
            data = ifc_model.get_info()

            del data["OwnerHistory"]

            loaded_by = []
            for load_group in ifc_model.LoadedBy or []:
                loaded_by.append(load_group.id())
            data["LoadedBy"] = loaded_by

            has_results = []
            for result_group in ifc_model.HasResults or []:
                has_results.append(result_group.id())
            data["HasResults"] = has_results

            data["OrientationOf2DPlane"] = (
                ifc_model.OrientationOf2DPlane.id() if ifc_model.OrientationOf2DPlane else None
            )
            data["SharedPlacement"] = ifc_model.SharedPlacement.id() if ifc_model.SharedPlacement else None
            return data

    @classmethod
    def get_ifc_structural_analysis_models(cls) -> dict[int, dict[str, Union[str, None]]]:
        models = {}
        for model in tool.Ifc.get().by_type("IfcStructuralAnalysisModel"):
            models[model.id()] = {"Name": model.Name}
        return models

    @classmethod
    def get_product_or_active_object(cls, product: str) -> Union[bpy.types.Object, None]:
        product = bpy.data.objects.get(product) if product else bpy.context.active_object
        try:
            props = tool.Blender.get_object_bim_props(product)
            if props.ifc_definition_id:
                return product
            else:
                return None
        except:
            return None

    @classmethod
    def get_structural_analysis_model_attributes(cls) -> dict[str, Any]:
        props = cls.get_structural_props()
        attributes = bonsai.bim.helper.export_attributes(props.structural_analysis_model_attributes)
        return attributes

    @classmethod
    def load_structural_analysis_model_attributes(cls, data: dict[str, Any]) -> None:
        props = cls.get_structural_props()
        props.structural_analysis_model_attributes.clear()
        schema = tool.Ifc.schema()
        assert (entity := schema.declaration_by_name("IfcStructuralAnalysisModel").as_entity())
        for attribute in entity.all_attributes():
            data_type = str(attribute.type_of_attribute)
            if "<entity" in data_type:
                continue
            new = props.structural_analysis_model_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            if attribute.name() == "PredefinedType":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                new.data_type = "enum"
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
            else:
                new.string_value = "" if new.is_null else data[attribute.name()]
                new.data_type = "string"

    @classmethod
    def load_structural_analysis_models(cls) -> None:
        models = tool.Structural.get_ifc_structural_analysis_models()
        props = cls.get_structural_props()
        props.structural_analysis_models.clear()
        for ifc_definition_id, model in models.items():
            new = props.structural_analysis_models.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = model["Name"] or "Unnamed"

    @classmethod
    def get_vertex_representation(
        cls, product: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        """
        :param product: IfcStructuralPointConnection
        :return: IfcTopologyRepresentation if it's valid.
        """
        vertex_representation, undefined_representation = None, None
        # At least 1 representation is mandatory in IFC for IfcStructuralPointConnection.
        for rep in product.Representation.Representations:
            rep: ifcopenshell.entity_instance
            rep_type: str = rep.RepresentationType
            if rep_type == "Vertex":
                vertex_representation = rep
                break
            # It's possible to have 'Undefined' or some other non-predefined type.
            elif rep_type not in ("Edge", "Path", "Face", "Shell"):
                undefined_representation = rep

        if not vertex_representation and not undefined_representation:
            return

        # All other checks in this case are covered by IFC validation.
        if vertex_representation:
            items = vertex_representation.Items
            if len(items) != 1:
                return None
            return vertex_representation

        if undefined_representation is None:
            return

        items = undefined_representation.Items
        if len(items) != 1 or not all(item.is_a("IfcVertex") for item in items):
            return None

        return undefined_representation

    @classmethod
    def import_boundary_condition_attributes(
        cls,
        boundary_condition: ifcopenshell.entity_instance,
        props: Union[BIMStructuralProperties, BIMObjectStructuralProperties],
    ) -> None:
        props_attrs = props.boundary_condition_attributes
        props_attrs.clear()
        schema = tool.Ifc.schema()
        # Don't use `import_attributes`,
        # because we need to support 2 types of values for the same props.
        ifc_class = boundary_condition.is_a()
        entity = schema.declaration_by_name(ifc_class).as_entity()
        assert entity
        for attribute in entity.all_attributes():
            attribute_name = attribute.name()
            value = getattr(boundary_condition, attribute_name)
            new = props_attrs.add()
            new.name = attribute_name
            new.ifc_class = ifc_class
            new.is_null = value is None
            new.is_optional = attribute.optional()

            # Select attribute values are typically wrapped.
            if isinstance(value, ifcopenshell.entity_instance):
                value = value.wrappedValue

            if attribute_name == "Name":
                new.string_value = "" if new.is_null else value
                new.data_type = "string"
            else:
                enum_items = [s.name() for s in ifcopenshell.util.attribute.get_select_items(attribute)]
                new.enum_items = json.dumps(enum_items)
                if isinstance(value, bool):
                    new.bool_value = False if new.is_null else value
                    new.data_type = "boolean"
                    new.enum_value = "IfcBoolean"
                elif value is None and "IfcBoolean" in enum_items:
                    new.bool_value = False
                    new.data_type = "boolean"
                    new.enum_value = "IfcBoolean"
                else:
                    new.float_value = 0 if new.is_null else value
                    new.data_type = "float"
                    new.enum_value = next((i for i in enum_items if i != "IfcBoolean"), enum_items[0])

    @classmethod
    def export_and_apply_boundary_condition_attributes(
        cls,
        boundary_condition: ifcopenshell.entity_instance,
        props: Union[BIMStructuralProperties, BIMObjectStructuralProperties],
    ) -> None:
        attributes: dict[str, AttributeDict] = {}
        for attribute in props.boundary_condition_attributes:
            if attribute.is_null:
                attributes[attribute.name] = {"value": None, "type": "null"}
            elif attribute.data_type == "string":
                attributes[attribute.name] = {"value": attribute.string_value, "type": "string"}
            elif attribute.enum_value == "IfcBoolean":
                attributes[attribute.name] = {"value": attribute.bool_value, "type": attribute.enum_value}
            else:
                attributes[attribute.name] = {"value": attribute.float_value, "type": attribute.enum_value}

        ifc_file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_boundary_condition(
            ifc_file, condition=boundary_condition, attributes=attributes
        )
