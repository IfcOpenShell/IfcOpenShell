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

import fractions
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
    def get_in_plane_components(
        cls,
        mode: str,
        magnitude: float = 0.0,
        angle: float = 0.0,
        rise: float = 0.0,
        run: float = 0.0,
        direction: str = "UP_RIGHT",
    ) -> tuple[float, float]:
        """Get the horizontal and vertical components of a force in a vertical plane.

        :param mode: ANGLE for an angle in degrees above the horizontal, or SLOPE
            for a rise over a run. Negative angles, rises or runs give downward
            or leftward components.
        :param direction: UP_RIGHT, UP_LEFT, DOWN_LEFT or DOWN_RIGHT. The angle or
            slope is measured from the horizontal towards this quadrant, so that
            40 degrees UP_LEFT points 140 degrees from +X.
        :return: The horizontal (X) and vertical (Z) components.
        """
        if mode == "ANGLE":
            x, z = magnitude * math.cos(math.radians(angle)), magnitude * math.sin(math.radians(angle))
        elif length := math.hypot(rise, run):
            x, z = magnitude * run / length, magnitude * rise / length
        else:
            return 0.0, 0.0
        sign_x, sign_z = {"UP_RIGHT": (1, 1), "UP_LEFT": (-1, 1), "DOWN_LEFT": (-1, -1), "DOWN_RIGHT": (1, -1)}[
            direction
        ]
        return sign_x * x, sign_z * z

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
        are the load cases that no model lists and whose loads are all on items of this model and of no other.
        A case that could belong to more than one model is left out rather than guessed."""
        ifc_file = tool.Ifc.get()
        cases = [g for g in ifc_file.by_type("IfcStructuralLoadGroup") if cls.is_load_case(g)]
        if model is None:
            return cases
        if model.LoadedBy:
            return list(model.LoadedBy)
        models = {m: cls.get_model_items(m) for m in ifc_file.by_type("IfcStructuralAnalysisModel")}
        inferred = []
        for case in cases:
            if case.LoadGroupFor or not (loaded := cls.get_loaded_items(case)):
                continue
            if [m for m, items in models.items() if loaded <= items] == [model]:
                inferred.append(case)
        return inferred

    @classmethod
    def get_model_items(cls, model: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        """The structural items grouped into an analysis model"""
        return {obj for rel in model.IsGroupedBy or [] for obj in rel.RelatedObjects}

    @classmethod
    def get_loaded_items(cls, group: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        """The structural items with loads in a load group, directly or in the groups within it"""
        items, groups, seen = set(), [group], set()
        while groups:
            group = groups.pop()
            if group.id() in seen:
                continue
            seen.add(group.id())
            for rel in group.IsGroupedBy or []:
                for obj in rel.RelatedObjects:
                    if obj.is_a("IfcStructuralLoadGroup"):
                        groups.append(obj)
                    elif obj.is_a("IfcStructuralActivity") and (connects := obj.AssignedToStructuralItem):
                        items.add(connects[0].RelatingElement)
        return items

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
        for prefix in ("Force", "Moment"):
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

    @classmethod
    def get_simple_slope(cls, x: float, z: float, max_denominator: int = 24) -> tuple[float, float]:
        """Get a rise and run along the in-plane components x and z, as small whole numbers if they make one.

        For example, components of -160 and -120 give a rise of -3 and a run of -4.
        No force gives a rise and run of 1 and 1.
        """
        if not x and not z:
            return 1.0, 1.0
        if not x or not z:
            return (math.copysign(1.0, z) if z else 0.0), (math.copysign(1.0, x) if x else 0.0)
        exact = abs(z) / abs(x)
        ratio = fractions.Fraction(exact).limit_denominator(max_denominator)
        if ratio and math.isclose(float(ratio), exact, rel_tol=1e-6):
            return math.copysign(ratio.numerator, z), math.copysign(ratio.denominator, x)
        length = math.hypot(x, z)
        return z / length, x / length

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
                else:
                    print(value)
                    new.float_value = 0 if new.is_null else value
                    new.data_type = "float"
                    new.enum_value = next(i for i in enum_items if i != "IfcBoolean")

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
