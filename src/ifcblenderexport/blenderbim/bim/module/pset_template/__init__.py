import bpy
from . import ui, prop, operator

classes = (
    operator.AddPropertySetTemplate,
    operator.RemovePropertySetTemplate,
    operator.EditPropertySetTemplate,
    operator.SavePropertySetTemplate,
    operator.AddPropertyTemplate,
    operator.RemovePropertyTemplate,
    prop.PropertySetTemplate,
    prop.PropertyTemplate,
    prop.BIMPsetTemplateProperties,
    ui.BIM_PT_pset_template,
)


def register():
    bpy.types.Scene.BIMPsetTemplateProperties = bpy.props.PointerProperty(type=prop.BIMPsetTemplateProperties)


def unregister():
    del bpy.types.Scene.BIMPsetTemplateProperties
