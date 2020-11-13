# Check if we are running in Blender before loading, to allow for multiprocessing
import sys

bpy = sys.modules.get("bpy")

if bpy is not None:
    import bpy
    from . import ui, prop, operator

    from .module.covetool import prop as covetool_prop
    from .module.covetool import ui as covetool_ui
    from .module.covetool import operator as covetool_operator

    from .module.model import grid as model_grid
    from .module.model import wall as model_wall
    from .module.model import stair as model_stair
    from .module.model import door as model_door
    from .module.model import window as model_window
    from .module.model import slab as model_slab
    from .module.model import opening as model_opening

    classes = (
        operator.ReassignClass,
        operator.AssignClass,
        operator.UnassignClass,
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
        operator.AddMaterialLayer,
        operator.RemoveMaterialLayer,
        operator.MoveMaterialLayer,
        operator.AddMaterialConstituent,
        operator.RemoveMaterialConstituent,
        operator.MoveMaterialConstituent,
        operator.AddMaterialProfile,
        operator.RemoveMaterialProfile,
        operator.MoveMaterialProfile,
        operator.AddConstraint,
        operator.RemoveConstraint,
        operator.AssignConstraint,
        operator.UnassignConstraint,
        operator.RemoveObjectConstraint,
        operator.AddPerson,
        operator.RemovePerson,
        operator.AddPersonRole,
        operator.RemovePersonRole,
        operator.AddPersonAddress,
        operator.RemovePersonAddress,
        operator.AddOrganisation,
        operator.RemoveOrganisation,
        operator.AddOrganisationRole,
        operator.RemoveOrganisationRole,
        operator.AddOrganisationAddress,
        operator.RemoveOrganisationAddress,
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
        operator.AddSheet,
        operator.OpenSheet,
        operator.AddDrawingToSheet,
        operator.CreateSheets,
        operator.OpenView,
        operator.ActivateView,
        operator.ExecuteIfcDiff,
        operator.VisualiseDiff,
        operator.ExportClashSets,
        operator.ImportClashSets,
        operator.AddClashSet,
        operator.RemoveClashSet,
        operator.AddClashSource,
        operator.RemoveClashSource,
        operator.SelectClashSource,
        operator.ExecuteIfcClash,
        operator.SelectIfcClashResults,
        operator.SwitchContext,
        operator.RemoveContext,
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
        operator.AddIfcFile,
        operator.RemoveIfcFile,
        operator.SelectDocIfcFile,
        operator.AddAnnotation,
        operator.GenerateReferences,
        operator.ResizeText,
        operator.AddVariable,
        operator.RemoveVariable,
        operator.PropagateTextData,
        operator.PushRepresentation,
        operator.ConvertLocalToGlobal,
        operator.ConvertGlobalToLocal,
        operator.GuessQuantity,
        operator.ExecuteBIMTester,
        operator.BIMTesterPurge,
        operator.SelectCobieIfcFile,
        operator.SelectCobieJsonFile,
        operator.ExecuteIfcCobie,
        operator.SelectIfcPatchInput,
        operator.SelectIfcPatchOutput,
        operator.ExecuteIfcPatch,
        operator.CalculateEdgeLengths,
        operator.CalculateFaceAreas,
        operator.CalculateObjectVolumes,
        operator.AddOpening,
        operator.SetOverrideColour,
        operator.AddDrawing,
        operator.RemoveDrawing,
        operator.AddDrawingStyle,
        operator.RemoveDrawingStyle,
        operator.SaveDrawingStyle,
        operator.ActivateDrawingStyle,
        operator.EditVectorStyle,
        operator.RemoveSheet,
        operator.AddSchedule,
        operator.RemoveSchedule,
        operator.SelectScheduleFile,
        operator.BuildSchedule,
        operator.AddScheduleToSheet,
        operator.SetViewportShadowFromSun,
        operator.SetNorthOffset,
        operator.GetNorthOffset,
        operator.AddDrawingStyleAttribute,
        operator.RemoveDrawingStyleAttribute,
        operator.CopyPropertyToSelection,
        operator.CreateShapeFromStepId,
        operator.SelectHighPolygonMeshes,
        operator.InspectFromStepId,
        operator.InspectFromObject,
        operator.RewindInspector,
        operator.RefreshDrawingList,
        operator.GetRepresentationIfcParameters,
        operator.UpdateIfcRepresentation,
        prop.StrProperty,
        prop.Attribute,
        prop.MaterialLayer,
        prop.MaterialConstituent,
        prop.MaterialProfile,
        prop.MaterialSet,
        prop.Variable,
        prop.Role,
        prop.Address,
        prop.Person,
        prop.Organisation,
        prop.Classification,
        prop.ClassificationReference,
        prop.ClassificationView,
        prop.PropertySetTemplate,
        prop.PropertyTemplate,
        prop.DocumentInformation,
        prop.DocumentReference,
        prop.ClashSource,
        prop.ClashSet,
        prop.Constraint,
        prop.Drawing,
        prop.Schedule,
        prop.DrawingStyle,
        prop.Sheet,
        prop.BcfTopic,
        prop.BcfTopicLabel,
        prop.BcfTopicFile,
        prop.BcfTopicLink,
        prop.BcfTopicDocumentReference,
        prop.BcfTopicRelatedTopic,
        prop.Subcontext,
        prop.BIMProperties,
        prop.BIMDebugProperties,
        prop.BCFProperties,
        prop.DocProperties,
        prop.BIMLibrary,
        prop.MapConversion,
        prop.TargetCRS,
        prop.IfcParameter,
        prop.BoundaryCondition,
        prop.PsetQto,
        prop.GlobalId,
        prop.RepresentationItem,
        prop.BIMObjectProperties,
        prop.BIMMaterialProperties,
        prop.SweptSolid,
        prop.BIMMeshProperties,
        prop.BIMCameraProperties,
        prop.BIMTextProperties,
        ui.BIM_PT_section_plane,
        ui.BIM_PT_drawings,
        ui.BIM_PT_schedules,
        ui.BIM_PT_sheets,
        ui.BIM_PT_bim,
        ui.BIM_PT_psets,
        ui.BIM_PT_classifications,
        ui.BIM_PT_document_information,
        ui.BIM_PT_constraints,
        ui.BIM_PT_search,
        ui.BIM_PT_ifccsv,
        ui.BIM_PT_ifcclash,
        ui.BIM_PT_bcf,
        ui.BIM_PT_owner,
        ui.BIM_PT_people,
        ui.BIM_PT_organisations,
        ui.BIM_PT_context,
        ui.BIM_PT_qa,
        ui.BIM_PT_library,
        ui.BIM_PT_gis,
        ui.BIM_PT_diff,
        ui.BIM_PT_cobie,
        ui.BIM_PT_patch,
        ui.BIM_PT_mvd,
        ui.BIM_PT_debug,
        ui.BIM_PT_material,
        ui.BIM_PT_mesh,
        ui.BIM_PT_object,
        ui.BIM_PT_object_material,
        ui.BIM_PT_object_psets,
        ui.BIM_PT_object_qto,
        ui.BIM_PT_representations,
        ui.BIM_PT_classification_references,
        ui.BIM_PT_documents,
        ui.BIM_PT_constraint_relations,
        ui.BIM_PT_object_structural,
        ui.BIM_PT_camera,
        ui.BIM_PT_text,
        ui.BIM_PT_modeling_utilities,
        ui.BIM_PT_annotation_utilities,
        ui.BIM_PT_qto_utilities,
        ui.BIM_PT_misc_utilities,
        ui.BIM_UL_generic,
        ui.BIM_UL_clash_sets,
        ui.BIM_UL_constraints,
        ui.BIM_UL_document_information,
        ui.BIM_UL_document_references,
        ui.BIM_UL_topics,
        ui.BIM_UL_classifications,
        ui.BIM_ADDON_preferences,
        covetool_prop.CoveToolProject,
        covetool_prop.CoveToolSimpleAnalysis,
        covetool_prop.CoveToolProperties,
        covetool_ui.BIM_UL_covetool_projects,
        covetool_ui.BIM_PT_covetool,
        covetool_operator.Login,
        covetool_operator.RunSimpleAnalysis,
        covetool_operator.RunAnalysis,
        model_grid.BIM_OT_add_object,
        model_wall.BIM_OT_add_object,
        model_stair.BIM_OT_add_object,
        model_door.BIM_OT_add_object,
        model_window.BIM_OT_add_object,
        model_slab.BIM_OT_add_object,
        model_opening.BIM_OT_add_object,
    )

    def menu_func_export(self, context):
        self.layout.operator(operator.ExportIFC.bl_idname, text="Industry Foundation Classes (.ifc/.ifczip/.ifcjson)")

    def menu_func_import(self, context):
        self.layout.operator(operator.ImportIFC.bl_idname, text="Industry Foundation Classes (.ifc/.ifczip/.ifcxml)")

    def on_register(scene):
        prop.setDefaultProperties(scene)
        bpy.app.handlers.depsgraph_update_post.remove(on_register)

    def register():
        for cls in classes:
            bpy.utils.register_class(cls)
        bpy.app.handlers.depsgraph_update_post.append(on_register)
        bpy.app.handlers.load_post.append(prop.setDefaultProperties)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        bpy.types.Scene.BIMProperties = bpy.props.PointerProperty(type=prop.BIMProperties)
        bpy.types.Scene.BIMDebugProperties = bpy.props.PointerProperty(type=prop.BIMDebugProperties)
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
        bpy.types.TextCurve.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
        bpy.types.Scene.CoveToolProperties = bpy.props.PointerProperty(type=covetool_prop.CoveToolProperties)
        bpy.types.SCENE_PT_unit.append(ui.ifc_units)
        bpy.types.VIEW3D_MT_mesh_add.append(model_grid.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.append(model_wall.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.append(model_stair.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.append(model_door.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.append(model_window.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.append(model_slab.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.append(model_opening.add_object_button)
        bpy.app.handlers.depsgraph_update_pre.append(operator.depsgraph_update_pre_handler)

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        bpy.app.handlers.load_post.remove(prop.setDefaultProperties)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        del bpy.types.Scene.BIMProperties
        del bpy.types.Scene.BIMDebugProperties
        del bpy.types.Scene.BCFProperties
        del bpy.types.Scene.DocProperties
        del bpy.types.Scene.MapConversion
        del bpy.types.Scene.TargetCRS
        del bpy.types.Object.BIMObjectProperties
        del bpy.types.Collection.BIMObjectProperties
        del bpy.types.Material.BIMMaterialProperties
        del bpy.types.Mesh.BIMMeshProperties
        del bpy.types.Camera.BIMCameraProperties
        del bpy.types.TextCurve.BIMTextProperties
        bpy.types.SCENE_PT_unit.remove(ui.ifc_units)
        bpy.types.VIEW3D_MT_mesh_add.remove(model_grid.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.remove(model_wall.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.remove(model_stair.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.remove(model_door.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.remove(model_window.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.remove(model_slab.add_object_button)
        bpy.types.VIEW3D_MT_mesh_add.remove(model_opening.add_object_button)
        bpy.app.handlers.depsgraph_update_pre.remove(operator.depsgraph_update_pre_handler)
