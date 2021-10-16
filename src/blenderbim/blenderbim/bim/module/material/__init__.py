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
    operator.AddConstituent,
    operator.AddLayer,
    operator.AddListItem,
    operator.AddMaterial,
    operator.AddProfile,
    operator.AssignMaterial,
    operator.AssignParameterizedProfile,
    operator.CopyMaterial,
    operator.DisableEditingAssignedMaterial,
    operator.DisableEditingMaterialSetItem,
    operator.EditAssignedMaterial,
    operator.EditMaterialSetItem,
    operator.EnableEditingAssignedMaterial,
    operator.EnableEditingMaterialSetItem,
    operator.RemoveConstituent,
    operator.RemoveLayer,
    operator.RemoveListItem,
    operator.RemoveMaterial,
    operator.RemoveProfile,
    operator.ReorderMaterialSetItem,
    operator.UnassignMaterial,
    operator.UnlinkMaterial,
    prop.BIMObjectMaterialProperties,
    ui.BIM_PT_material,
    ui.BIM_PT_object_material,
)


def register():
    bpy.types.Object.BIMObjectMaterialProperties = bpy.props.PointerProperty(type=prop.BIMObjectMaterialProperties)


def unregister():
    del bpy.types.Object.BIMObjectMaterialProperties
