import bpy
from . import ui, prop, operator

classes = (
    operator.SavePsetTemplateFile,
    operator.AddPsetTemplate,
    operator.EditPsetTemplate,
    operator.RemovePsetTemplate,
    operator.AddPropTemplate,
    operator.EditPropTemplate,
    operator.RemovePropTemplate,
    operator.EnableEditingPsetTemplate,
    operator.DisableEditingPsetTemplate,
    operator.EnableEditingPropTemplate,
    operator.DisableEditingPropTemplate,
    prop.PsetTemplate,
    prop.PropTemplate,
    prop.BIMPsetTemplateProperties,
    ui.BIM_PT_pset_template,
)


def register():
    bpy.types.Scene.BIMPsetTemplateProperties = bpy.props.PointerProperty(type=prop.BIMPsetTemplateProperties)


def unregister():
    del bpy.types.Scene.BIMPsetTemplateProperties
