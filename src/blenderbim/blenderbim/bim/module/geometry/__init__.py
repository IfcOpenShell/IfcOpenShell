# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from . import ui, prop, operator

classes = (
    operator.AddRepresentation,
    operator.CopyRepresentation,
    operator.EditObjectPlacement,
    operator.GetRepresentationIfcParameters,
    operator.RemoveRepresentation,
    operator.SwitchRepresentation,
    operator.UpdateParametricRepresentation,
    operator.UpdateRepresentation,
    prop.BIMGeometryProperties,
    ui.BIM_PT_derived_placements,
    ui.BIM_PT_representations,
    ui.BIM_PT_mesh,
    ui.BIM_PT_workarounds,
)


def register():
    bpy.types.Scene.BIMGeometryProperties = bpy.props.PointerProperty(type=prop.BIMGeometryProperties)
    bpy.types.OBJECT_PT_transform.append(ui.BIM_PT_transform)


def unregister():
    bpy.types.OBJECT_PT_transform.remove(ui.BIM_PT_transform)
    del bpy.types.Scene.BIMGeometryProperties
