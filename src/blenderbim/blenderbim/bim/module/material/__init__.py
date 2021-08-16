
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
    operator.CopyMaterial,
    operator.AddMaterial,
    operator.RemoveMaterial,
    operator.AssignMaterial,
    operator.UnassignMaterial,
    operator.AddConstituent,
    operator.RemoveConstituent,
    operator.AddProfile,
    operator.RemoveProfile,
    operator.AssignParameterizedProfile,
    operator.AddLayer,
    operator.RemoveLayer,
    operator.ReorderMaterialSetItem,
    operator.AddListItem,
    operator.RemoveListItem,
    operator.EnableEditingAssignedMaterial,
    operator.DisableEditingAssignedMaterial,
    operator.EditAssignedMaterial,
    operator.EnableEditingMaterialSetItem,
    operator.DisableEditingMaterialSetItem,
    operator.EditMaterialSetItem,
    prop.BIMObjectMaterialProperties,
    ui.BIM_PT_material,
    ui.BIM_PT_object_material,
)


def register():
    bpy.types.Object.BIMObjectMaterialProperties = bpy.props.PointerProperty(type=prop.BIMObjectMaterialProperties)


def unregister():
    del bpy.types.Object.BIMObjectMaterialProperties
