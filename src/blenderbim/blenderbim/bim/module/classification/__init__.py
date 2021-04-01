import bpy
from . import ui, prop, operator

classes = (
    operator.LoadClassificationLibrary,
    operator.AddClassification,
    operator.RemoveClassification,
    operator.EnableEditingClassification,
    operator.DisableEditingClassification,
    operator.EditClassification,
    operator.RemoveClassificationReference,
    operator.EnableEditingClassificationReference,
    operator.DisableEditingClassificationReference,
    operator.EditClassificationReference,
    operator.AddClassificationReference,
    operator.ChangeClassificationLevel,
    prop.ClassificationReference,
    prop.BIMClassificationProperties,
    prop.BIMClassificationReferenceProperties,
    ui.BIM_PT_classifications,
    ui.BIM_PT_classification_references,
    ui.BIM_UL_classifications,
)


def register():
    bpy.types.Scene.BIMClassificationProperties = bpy.props.PointerProperty(type=prop.BIMClassificationProperties)
    bpy.types.Object.BIMClassificationReferenceProperties = bpy.props.PointerProperty(
        type=prop.BIMClassificationReferenceProperties
    )


def unregister():
    del bpy.types.Scene.BIMClassificationProperties
    del bpy.types.Object.BIMClassificationReferenceProperties
