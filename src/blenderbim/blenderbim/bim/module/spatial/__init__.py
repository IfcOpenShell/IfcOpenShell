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
    operator.AssignContainer,
    operator.ChangeSpatialLevel,
    operator.CopyToContainer,
    operator.DereferenceStructure,
    operator.DisableEditingContainer,
    operator.EnableEditingContainer,
    operator.ReferenceStructure,
    operator.RemoveContainer,
    operator.SelectContainer,
    operator.SelectSimilarContainer,
    prop.SpatialElement,
    prop.BIMSpatialProperties,
    prop.BIMObjectSpatialProperties,
    ui.BIM_PT_spatial,
    ui.BIM_UL_containers,
)


def register():
    bpy.types.Scene.BIMSpatialProperties = bpy.props.PointerProperty(type=prop.BIMSpatialProperties)
    bpy.types.Object.BIMObjectSpatialProperties = bpy.props.PointerProperty(type=prop.BIMObjectSpatialProperties)


def unregister():
    del bpy.types.Scene.BIMSpatialProperties
    del bpy.types.Object.BIMObjectSpatialProperties
