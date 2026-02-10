# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>, @Andrej730
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

import bonsai.tool as tool


class ApplyExternalParametricGeometry(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.apply_external_parametric_geometry"
    bl_label = "Apply External Parametric Geometry"
    bl_description = "Apply external parametric geometry to the active object."
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        props = tool.Model.get_epg_props(obj)

        # TODO: consider nodes being empty.
        if props.geometry_source == "GEONODES":
            assert (active_representation := tool.Geometry.get_active_representation(obj))
            ifc_context = active_representation.ContextOfItems

            tool.Model.add_representation(obj, ifc_context)
        elif props.geometry_source == "IFCSVERCHOK":
            import ifcsverchok.helper as helper

            nodes = props.sverchok_nodes
            assert nodes is not None
            tool.Model.run_ifcsverchok_graph_on_bonsai_file(nodes)
            output_node = tool.Model.get_ifcsverchok_shape_output(nodes)
            representation = helper.get_socket_value(output_node.inputs, "Representation")
            tool.Model.replace_object_ifc_representation(representation.ContextOfItems, obj, representation)

        props.is_editing = False
        return {"FINISHED"}
