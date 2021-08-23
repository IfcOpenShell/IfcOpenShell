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
import olca
import ifcopenshell


class CalculateLCA(bpy.types.Operator):
    bl_idname = "bim.calculate_lca"
    bl_label = "Calculate LCA"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.xlsx", options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.BIMLCAProperties
        client = olca.Client(context.preferences.addons["blenderbim"].preferences.openlca_port)
        setup = olca.CalculationSetup()
        setup.calculation_type = olca.CalculationType.SIMPLE_CALCULATION
        setup.impact_method = client.find(olca.ImpactMethod, "CML-IA baseline")
        setup.product_system = client.find(olca.ProductSystem, props.product_systems)
        setup.amount = props.amount
        result = client.calculate(setup)
        client.excel_export(result, self.filepath)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
