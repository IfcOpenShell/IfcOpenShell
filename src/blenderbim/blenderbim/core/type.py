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

import blenderbim.core.geometry


def assign_type(ifc, type_tool, element=None, type=None):
    ifc.run("type.assign_type", related_object=element, relating_type=type)
    obj = ifc.get_object(element)
    if type_tool.has_material_usage(element):
        representation = type_tool.get_body_representation(element)
        if representation:
            body_context = type_tool.get_representation_context(representation)
            ifc.run("geometry.unassign_representation", product=element, representation=representation)
            ifc.run("geometry.remove_representation", representation=representation)
        else:
            body_context = type_tool.get_body_context()
        representation = type_tool.run_geometry_add_representation(
            obj=obj,
            context=body_context,
            ifc_representation_class=type_tool.get_ifc_representation_class(element),
            profile_set_usage=type_tool.get_profile_set_usage(element),
        )
        should_reload = True
    else:
        representation = type_tool.get_body_representation(element)
        if not representation:
            representation = type_tool.get_any_representation(element)
        should_reload = False
    if representation:
        type_tool.run_geometry_switch_representation(
            obj=obj,
            representation=representation,
            should_reload=should_reload,
            enable_dynamic_voids=type_tool.has_dynamic_voids(obj),
            is_global=False,
        )
    type_tool.disable_editing(obj)
