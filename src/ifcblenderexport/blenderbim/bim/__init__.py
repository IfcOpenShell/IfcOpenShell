# Check if we are running in Blender before loading, to allow for multiprocessing
import sys
import os
bpy = sys.modules.get('bpy')

if bpy is not None:
    import bpy
    from . import ui, prop, operator

    classes = (
        operator.AssignClass,
        operator.SelectClass,
        operator.SelectType,
        operator.SelectBcfFile,
        operator.GetBcfTopics,
        operator.ViewBcfTopic,
        operator.ActivateBcfViewpoint,
        operator.OpenBcfFileReference,
        operator.OpenBcfReferenceLink,
        operator.OpenBcfBimSnippetSchema,
        operator.OpenBcfBimSnippetReference,
        operator.OpenBcfDocumentReference,
        operator.SelectFeaturesDir,
        operator.SelectDiffJsonFile,
        operator.SelectDiffNewFile,
        operator.SelectDiffOldFile,
        operator.SelectDataDir,
        operator.SelectSchemaDir,
        operator.SelectIfcFile,
        operator.ValidateIfcFile,
        operator.ExportIFC,
        operator.ImportIFC,
        operator.ColourByClass,
        operator.ColourByAttribute,
        operator.ColourByPset,
        operator.ResetObjectColours,
        operator.ApproveClass,
        operator.RejectClass,
        operator.SelectAudited,
        operator.RejectElement,
        operator.SelectExternalMaterialDir,
        operator.AddSweptSolid,
        operator.RemoveSweptSolid,
        operator.AssignSweptSolidOuterCurve,
        operator.SelectSweptSolidOuterCurve,
        operator.AddSweptSolidInnerCurve,
        operator.SelectSweptSolidInnerCurves,
        operator.AssignSweptSolidExtrusion,
        operator.SelectSweptSolidExtrusion,
        operator.AddPset,
        operator.RemovePset,
        operator.AddQto,
        operator.RemoveQto,
        operator.AddMaterialPset,
        operator.RemoveMaterialPset,
        operator.AddDocumentInformation,
        operator.RemoveDocumentInformation,
        operator.AssignDocumentInformation,
        operator.AddDocumentReference,
        operator.RemoveDocumentReference,
        operator.AssignDocumentReference,
        operator.UnassignDocumentReference,
        operator.RemoveObjectDocumentReference,
        operator.GenerateGlobalId,
        operator.AddAttribute,
        operator.RemoveAttribute,
        operator.AddMaterialAttribute,
        operator.RemoveMaterialAttribute,
        operator.QuickProjectSetup,
        operator.SelectGlobalId,
        operator.SelectAttribute,
        operator.SelectPset,
        operator.CreateAggregate,
        operator.EditAggregate,
        operator.SaveAggregate,
        operator.ExplodeAggregate,
        operator.LoadClassification,
        operator.AddClassification,
        operator.RemoveClassification,
        operator.AssignClassification,
        operator.UnassignClassification,
        operator.RemoveClassificationReference,
        operator.FetchLibraryInformation,
        operator.FetchExternalMaterial,
        operator.FetchObjectPassport,
        operator.AddSubcontext,
        operator.RemoveSubcontext,
        operator.CutSection,
        operator.CreateSheet,
        operator.OpenSheet,
        operator.OpenCompiledSheet,
        operator.AddViewToSheet,
        operator.CreateSheets,
        operator.GenerateDigitalTwin,
        operator.CreateView,
        operator.OpenView,
        operator.ActivateView,
        operator.ExecuteIfcDiff,
        operator.AssignContext,
        operator.SetViewPreset1,
        operator.OpenUpstream,
        operator.BIM_OT_CopyAttributesToSelection,
        operator.BIM_OT_ChangeClassificationLevel,
        operator.AddPropertySetTemplate,
        operator.RemovePropertySetTemplate,
        operator.EditPropertySetTemplate,
        operator.SavePropertySetTemplate,
        operator.AddPropertyTemplate,
        operator.RemovePropertyTemplate,
        operator.AddSectionPlane,
        operator.RemoveSectionPlane,
        operator.AddCsvAttribute,
        operator.RemoveCsvAttribute,
        operator.ExportIfcCsv,
        operator.ImportIfcCsv,
        operator.EyedropIfcCsv,
        operator.ReloadIfcFile,
        operator.SelectSimilarType,
        prop.StrProperty,
        prop.Classification,
        prop.ClassificationReference,
        prop.ClassificationView,
        prop.PropertySetTemplate,
        prop.PropertyTemplate,
        prop.DocumentInformation,
        prop.DocumentReference,
        prop.BcfTopic,
        prop.BcfTopicLabel,
        prop.BcfTopicFile,
        prop.BcfTopicLink,
        prop.BcfTopicDocumentReference,
        prop.BcfTopicRelatedTopic,
        prop.Subcontext,
        prop.BIMProperties,
        prop.BCFProperties,
        prop.DocProperties,
        prop.BIMLibrary,
        prop.MapConversion,
        prop.TargetCRS,
        prop.Attribute,
        prop.BoundaryCondition,
        prop.PsetQto,
        prop.GlobalId,
        prop.BIMObjectProperties,
        prop.BIMMaterialProperties,
        prop.SweptSolid,
        prop.BIMMeshProperties,
        prop.BIMCameraProperties,
        ui.BIM_PT_section_plane,
        ui.BIM_PT_documentation,
        ui.BIM_PT_bim,
        ui.BIM_PT_psets,
        ui.BIM_PT_classifications,
        ui.BIM_PT_document_information,
        ui.BIM_PT_search,
        ui.BIM_PT_ifccsv,
        ui.BIM_PT_bcf,
        ui.BIM_PT_owner,
        ui.BIM_PT_context,
        ui.BIM_PT_qa,
        ui.BIM_PT_library,
        ui.BIM_PT_gis,
        ui.BIM_PT_diff,
        ui.BIM_PT_mvd,
        ui.BIM_PT_material,
        ui.BIM_PT_mesh,
        ui.BIM_PT_object,
        ui.BIM_PT_classification_references,
        ui.BIM_PT_documents,
        ui.BIM_PT_camera,
        ui.BIM_UL_document_information,
        ui.BIM_UL_document_references,
        ui.BIM_UL_topics,
        ui.BIM_UL_classifications,
        ui.BIM_ADDON_preferences,
        )

    def menu_func_export(self, context):
        self.layout.operator(operator.ExportIFC.bl_idname,
             text="Industry Foundation Classes (.ifc/.ifczip)")

    def menu_func_import(self, context):
        self.layout.operator(operator.ImportIFC.bl_idname,
             text="Industry Foundation Classes (.ifc/.ifczip)")

    def on_register(scene):
        prop.setDefaultProperties(scene)
        bpy.app.handlers.scene_update_post.remove(on_register)

    def register():
        for cls in classes:
            bpy.utils.register_class(cls)
        bpy.app.handlers.depsgraph_update_post.append(on_register)
        bpy.app.handlers.load_post.append(prop.setDefaultProperties)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        bpy.types.Scene.BIMProperties = bpy.props.PointerProperty(type=prop.BIMProperties)
        bpy.types.Scene.BCFProperties = bpy.props.PointerProperty(type=prop.BCFProperties)
        bpy.types.Scene.DocProperties = bpy.props.PointerProperty(type=prop.DocProperties)
        bpy.types.Scene.BIMLibrary = bpy.props.PointerProperty(type=prop.BIMLibrary)
        bpy.types.Scene.MapConversion = bpy.props.PointerProperty(type=prop.MapConversion)
        bpy.types.Scene.TargetCRS = bpy.props.PointerProperty(type=prop.TargetCRS)
        bpy.types.Object.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
        bpy.types.Collection.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
        bpy.types.Material.BIMMaterialProperties = bpy.props.PointerProperty(type=prop.BIMMaterialProperties)
        bpy.types.Mesh.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
        bpy.types.Camera.BIMCameraProperties = bpy.props.PointerProperty(type=prop.BIMCameraProperties)

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        bpy.app.handlers.load_post.remove(prop.setDefaultProperties)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        del(bpy.types.Scene.BIMProperties)
        del(bpy.types.Scene.BCFProperties)
        del(bpy.types.Scene.DocProperties)
        del(bpy.types.Scene.MapConversion)
        del(bpy.types.Scene.TargetCRS)
        del(bpy.types.Object.BIMObjectProperties)
        del(bpy.types.Collection.BIMObjectProperties)
        del(bpy.types.Material.BIMMaterialProperties)
        del(bpy.types.Mesh.BIMMeshProperties)
        del(bpy.types.Camera.BIMCameraProperties)
