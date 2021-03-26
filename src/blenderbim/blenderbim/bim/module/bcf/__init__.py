import bpy
from . import ui, prop, operator

classes = (
    operator.NewBcfProject,
    operator.LoadBcfProject,
    operator.LoadBcfTopics,
    operator.LoadBcfTopic,
    operator.LoadBcfComments,
    operator.EditBcfProjectName,
    operator.EditBcfAuthor,
    operator.EditBcfTopicName,
    operator.EditBcfTopic,
    operator.SaveBcfProject,
    operator.AddBcfTopic,
    operator.AddBcfHeaderFile,
    operator.AddBcfBimSnippet,
    operator.AddBcfReferenceLink,
    operator.AddBcfDocumentReference,
    operator.AddBcfLabel,
    operator.AddBcfRelatedTopic,
    operator.ViewBcfTopic,
    operator.RemoveBcfComment,
    operator.RemoveBcfBimSnippet,
    operator.RemoveBcfReferenceLink,
    operator.RemoveBcfDocumentReference,
    operator.RemoveBcfRelatedTopic,
    operator.EditBcfReferenceLinks,
    operator.EditBcfLabels,
    operator.RemoveBcfLabel,
    operator.EditBcfComment,
    operator.AddBcfComment,
    operator.ActivateBcfViewpoint,
    operator.AddBcfViewpoint,
    operator.RemoveBcfViewpoint,
    operator.RemoveBcfFile,
    operator.OpenBcfReferenceLink,
    operator.SelectBcfHeaderFile,
    operator.SelectBcfBimSnippetReference,
    operator.SelectBcfDocumentReference,
    prop.BcfReferenceLink,
    prop.BcfLabel,
    prop.BcfBimSnippet,
    prop.BcfDocumentReference,
    prop.BcfComment,
    prop.BcfTopic,
    prop.BCFProperties,
    ui.BIM_PT_bcf,
    ui.BIM_PT_bcf_metadata,
    ui.BIM_PT_bcf_comments,
)


def register():
    bpy.types.Scene.BCFProperties = bpy.props.PointerProperty(type=prop.BCFProperties)


def unregister():
    del bpy.types.Scene.BCFProperties
