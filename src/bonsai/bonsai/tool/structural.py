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
import ifcopenshell
import json
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from pprint import pprint


class Structural(bonsai.core.tool.Structural):
    @classmethod
    def disable_editing_structural_analysis_model(cls):
        bpy.context.scene.BIMStructuralProperties.active_structural_analysis_model_id = 0

    @classmethod
    def disable_structural_analysis_model_editing_ui(cls):
        bpy.context.scene.BIMStructuralProperties.is_editing = False

    @classmethod
    def enable_editing_structural_analysis_model(cls, model):
        if model:
            bpy.context.scene.BIMStructuralProperties.active_structural_analysis_model_id = model

    @classmethod
    def enable_structural_analysis_model_editing_ui(cls):
        bpy.context.scene.BIMStructuralProperties.is_editing = True

    @classmethod
    def enabled_structural_analysis_model_editing_ui(cls):
        return bpy.context.scene.BIMStructuralProperties.is_editing

    @classmethod
    def ensure_representation_contexts(cls):
        model = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model")
        if not model:
            model = tool.Ifc.run(
                "context.add_context",
                context_type="Model",
                context_identifier="",
                target_view="",
                parent=0,
            )
        graph = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Reference", "GRAPH_VIEW")
        if not graph:
            model = tool.Ifc.run(
                "context.add_context",
                context_type="Model",
                context_identifier="Reference",
                target_view="GRAPH_VIEW",
                parent=model,
            )

    @classmethod
    def get_active_structural_analysis_model(cls):
        props = bpy.context.scene.BIMStructuralProperties
        model = tool.Ifc.get().by_id(props.active_structural_analysis_model_id)
        return model

    @classmethod
    def get_ifc_structural_analysis_model_attributes(cls, model):
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
    def get_ifc_structural_analysis_models(cls):
        models = {}
        for model in tool.Ifc.get().by_type("IfcStructuralAnalysisModel"):
            models[model.id()] = {"Name": model.Name}
        return models

    @classmethod
    def get_product_or_active_object(cls, product):
        product = bpy.data.objects.get(product) if product else bpy.context.active_object
        try:
            if product.BIMObjectProperties.ifc_definition_id:
                return product
            else:
                return None
        except:
            return None

    @classmethod
    def get_structural_analysis_model_attributes(cls):
        props = bpy.context.scene.BIMStructuralProperties
        attributes = bonsai.bim.helper.export_attributes(props.structural_analysis_model_attributes)
        return attributes

    @classmethod
    def load_structural_analysis_model_attributes(cls, data):
        props = bpy.context.scene.BIMStructuralProperties
        props.structural_analysis_model_attributes.clear()
        for attribute in IfcStore.get_schema().declaration_by_name("IfcStructuralAnalysisModel").all_attributes():
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
    def load_structural_analysis_models(cls):
        models = tool.Structural.get_ifc_structural_analysis_models()
        props = bpy.context.scene.BIMStructuralProperties
        props.structural_analysis_models.clear()
        for ifc_definition_id, model in models.items():
            new = props.structural_analysis_models.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = model["Name"] or "Unnamed"
