import bpy
from . import ui, prop, operator

classes = (
    operator.AddMaterial,
    operator.RemoveMaterial,
    operator.AssignMaterial,
    operator.UnassignMaterial,
    operator.AddConstituent,
    operator.RemoveConstituent,
    operator.AddProfile,
    operator.RemoveProfile,
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
