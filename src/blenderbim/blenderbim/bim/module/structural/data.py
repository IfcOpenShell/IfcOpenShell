# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool


def refresh():
    StructuralData.is_loaded = False


class StructuralData:
    products = {}
    number_of_structural_analysis_models = 0
    is_loaded = False

    @classmethod
    def load(cls):
        cls.load_structural_analysis_models()
        cls.is_loaded = True

    @classmethod
    def load_structural_analysis_models(cls):
        cls.products = {}
        cls.number_of_structural_analysis_models = len(tool.Ifc.get().by_type("IfcStructuralAnalysisModel"))

        for model in tool.Ifc.get().by_type("IfcStructuralAnalysisModel"):
            if model.IsGroupedBy:
                for rel in model.IsGroupedBy:
                    for product in rel.RelatedObjects:
                        cls.products.setdefault(product.id(), []).append(model.id())
