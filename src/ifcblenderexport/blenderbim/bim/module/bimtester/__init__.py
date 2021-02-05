import bpy
from . import ui, prop, operator

classes = (
    operator.ExecuteBIMTester,
    operator.BIMTesterPurge,
    operator.SelectFeature,
    operator.SelectSteps,
    operator.SelectBIMTesterIfcFile,
    operator.RejectElement,
    operator.ApproveClass,
    operator.RejectClass,
    operator.SelectAudited,
    prop.BimTesterProperties,
    ui.BIM_PT_qa,
)


def register():
    bpy.types.Scene.BimTesterProperties = bpy.props.PointerProperty(type=prop.BimTesterProperties)


def unregister():
    del bpy.types.Scene.BimTesterProperties
