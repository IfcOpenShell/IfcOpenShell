import bpy
from . import ui, prop, operator

classes = (
    operator.LoadInformation,
    operator.LoadDocumentReferences,
    operator.DisableDocumentEditingUI,
    operator.EnableEditingDocument,
    operator.DisableEditingDocument,
    operator.AddInformation,
    operator.AddDocumentReference,
    operator.EditInformation,
    operator.EditDocumentReference,
    operator.RemoveDocument,
    operator.EnableAssigningDocument,
    operator.DisableAssigningDocument,
    operator.AssignDocument,
    operator.UnassignDocument,
    prop.Document,
    prop.BIMDocumentProperties,
    prop.BIMObjectDocumentProperties,
    ui.BIM_PT_documents,
    ui.BIM_PT_object_documents,
    ui.BIM_UL_documents,
    ui.BIM_UL_object_documents,
)


def register():
    bpy.types.Scene.BIMDocumentProperties = bpy.props.PointerProperty(type=prop.BIMDocumentProperties)
    bpy.types.Object.BIMObjectDocumentProperties = bpy.props.PointerProperty(type=prop.BIMObjectDocumentProperties)


def unregister():
    del bpy.types.Scene.BIMDocumentProperties
    del bpy.types.Scene.BIMObjectDocumentProperties
