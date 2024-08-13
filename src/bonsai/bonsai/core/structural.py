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


def add_structural_analysis_model(ifc, structural):
    result = ifc.run("structural.add_structural_analysis_model")
    structural.load_structural_analysis_models()
    structural.ensure_representation_contexts()
    return result


def assign_structural_analysis_model(ifc, structural, product=None, structural_analysis_model=None):
    product = structural.get_product_or_active_object(product)
    if structural_analysis_model and product:
        ifc.run(
            "structural.assign_structural_analysis_model",
            **{
                "product": ifc.get().by_id(product.BIMObjectProperties.ifc_definition_id),
                "structural_analysis_model": ifc.get().by_id(structural_analysis_model),
            },
        )


def disable_editing_structural_analysis_model(structural):
    structural.disable_editing_structural_analysis_model()


def disable_structural_analysis_model_editing_ui(structural):
    structural.disable_structural_analysis_model_editing_ui()


def edit_structural_analysis_model(ifc, structural):
    attributes = structural.get_structural_analysis_model_attributes()
    ifc.run(
        "structural.edit_structural_analysis_model",
        **{
            "structural_analysis_model": structural.get_active_structural_analysis_model(),
            "attributes": attributes,
        },
    )
    structural.load_structural_analysis_models()
    structural.disable_editing_structural_analysis_model()


def enable_editing_structural_analysis_model(structural, model=None):
    structural.enable_editing_structural_analysis_model(model)


def enable_structural_analysis_model_editing_ui(structural):
    structural.enable_structural_analysis_model_editing_ui()


def load_structural_analysis_model_attributes(structural, model=None):
    data = structural.get_ifc_structural_analysis_model_attributes(model)
    structural.load_structural_analysis_model_attributes(data)


def load_structural_analysis_models(structural):
    structural.load_structural_analysis_models()
    structural.enable_structural_analysis_model_editing_ui()
    # structural.disable_editing_structural_analysis_model()


def remove_structural_analysis_model(ifc, structural, model=None):
    ifc.run(
        "structural.remove_structural_analysis_model",
        **{"structural_analysis_model": ifc.get().by_id(model)},
    )
    structural.load_structural_analysis_models()


def unassign_structural_analysis_model(ifc, structural, product=None, structural_analysis_model=None):
    product = structural.get_product_or_active_object(product)
    if structural_analysis_model and product:
        ifc.run(
            "structural.unassign_structural_analysis_model",
            **{
                "product": ifc.get().by_id(product.BIMObjectProperties.ifc_definition_id),
                "structural_analysis_model": ifc.get().by_id(structural_analysis_model),
            },
        )
