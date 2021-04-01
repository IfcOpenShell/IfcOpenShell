import bpy
from . import ui, prop, operator

classes = (
    operator.ExportClashSets,
    operator.ImportClashSets,
    operator.AddClashSet,
    operator.RemoveClashSet,
    operator.AddClashSource,
    operator.RemoveClashSource,
    operator.SelectClashSource,
    operator.ExecuteIfcClash,
    operator.SelectIfcClashResults,
    operator.SelectClashResults,
    operator.SelectSmartGroupedClashesPath,
    operator.SmartClashGroup,
    operator.SelectSmartGroup,
    operator.LoadSmartGroupsForActiveClashSet,
    operator.SetBlenderClashSetA,
    operator.SetBlenderClashSetB,
    operator.ExecuteBlenderClash,
    prop.ClashSource,
    prop.ClashSet,
    prop.SmartClashGroup,
    prop.BIMClashProperties,
    ui.BIM_PT_ifcclash,
    ui.BIM_PT_clash_manager,
    ui.BIM_UL_clash_sets,
    ui.BIM_UL_smart_groups,
)


def register():
    bpy.types.Scene.BIMClashProperties = bpy.props.PointerProperty(type=prop.BIMClashProperties)


def unregister():
    del bpy.types.Scene.BIMClashProperties
