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
    prop.Document,
    prop.BIMDocumentProperties,
    ui.BIM_PT_documents,
    ui.BIM_UL_documents,
)


def register():
    bpy.types.Scene.BIMDocumentProperties = bpy.props.PointerProperty(type=prop.BIMDocumentProperties)


def unregister():
    del bpy.types.Scene.BIMDocumentProperties
