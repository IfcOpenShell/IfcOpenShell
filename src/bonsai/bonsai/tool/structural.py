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
import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.util.representation
import json
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from typing import Union, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.structural.prop import BIMStructuralProperties, BIMObjectStructuralProperties


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
                new.enum_items = json.dumps(attribute.type_of_attribute().declared_type().enumeration_items())
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
