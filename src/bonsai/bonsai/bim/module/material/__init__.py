# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from . import ui, prop, operator

classes = (
    operator.AddConstituent,
    operator.AddLayer,
    operator.AddListItem,
    operator.AddMaterial,
    operator.DuplicateMaterial,
    operator.AddMaterialSet,
    operator.AddProfile,
    operator.AssignMaterial,
    operator.AssignMaterialToSelected,
    operator.AssignParameterizedProfile,
    operator.ContractMaterialCategory,
    operator.DisableEditingAssignedMaterial,
    operator.DisableEditingMaterial,
    operator.DisableEditingMaterialSetItem,
    operator.DisableEditingMaterialSetItemProfile,
    operator.DisableEditingMaterials,
    operator.DuplicateLayer,
    operator.EditAssignedMaterial,
    operator.EditMaterial,
    operator.EditMaterialSetItem,
    operator.EditMaterialSetItemProfile,
    operator.EditMaterialStyle,
    operator.EnableEditingAssignedMaterial,
    operator.EnableEditingMaterial,
    operator.EnableEditingMaterialSetItem,
    operator.EnableEditingMaterialSetItemProfile,
    operator.EnableEditingMaterialStyle,
    operator.ExpandMaterialCategory,
    operator.LoadMaterials,
    operator.RemoveConstituent,
    operator.RemoveLayer,
    operator.RemoveListItem,
    operator.RemoveMaterial,
    operator.RemoveMaterialSet,
    operator.RemoveProfile,
    operator.ReorderMaterialSetItem,
    operator.SelectByMaterial,
    operator.SelectMaterialInMaterialsUI,
    operator.UnassignMaterial,
    operator.UnassignMaterialStyle,
    prop.Material,
    prop.BIMMaterialProperties,
    prop.BIMObjectMaterialProperties,
    ui.BIM_PT_materials,
    ui.BIM_PT_object_material,
    ui.BIM_UL_materials,
)


def register():
    bpy.types.Scene.BIMMaterialProperties = bpy.props.PointerProperty(type=prop.BIMMaterialProperties)
    bpy.types.Object.BIMObjectMaterialProperties = bpy.props.PointerProperty(type=prop.BIMObjectMaterialProperties)


def unregister():
    del bpy.types.Scene.BIMMaterialProperties
    del bpy.types.Object.BIMObjectMaterialProperties
