# Check if we are running in Blender before loading, to allow for multiprocessing
import sys

bpy = sys.modules.get("bpy")

if bpy is not None:
    import bpy
    import importlib
    from . import ui, prop, operator

    modules = {
        "root": None,
        "aggregate": None,
        "attribute": None,
        "bcf": None,
        "classification": None,
        "cobie": None,
        "context": None,
        "constraint": None,
        "covetool": None,
        "csv": None,
        "diff": None,
        "bimtester": None,
        "debug": None,
        "document": None,
        "geometry": None,
        "georeference": None,
        "material": None,
        "model": None,
        "owner": None,
        "project": None,
        "pset": None,
        "qto": None,
        "search": None,
        "spatial": None,
        "style": None,
        "type": None,
        "unit": None,
        "void": None,
    }

    for name in modules.keys():
        modules[name] = importlib.import_module(f"blenderbim.bim.module.{name}")

    classes = [
        operator.OpenUri,
        operator.SelectDataDir,
        operator.SelectSchemaDir,
        operator.SelectIfcFile,
        operator.ExportIFC,
        operator.ImportIFC,
        operator.SelectExternalMaterialDir,
        operator.AddSweptSolid,
        operator.RemoveSweptSolid,
        operator.AssignSweptSolidOuterCurve,
        operator.SelectSweptSolidOuterCurve,
        operator.AddSweptSolidInnerCurve,
        operator.SelectSweptSolidInnerCurves,
        operator.AssignSweptSolidExtrusion,
        operator.SelectSweptSolidExtrusion,
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
        operator.AddMaterialAttribute,
        operator.RemoveMaterialAttribute,
        operator.FetchLibraryInformation,
        operator.FetchExternalMaterial,
        operator.FetchObjectPassport,
        operator.CutSection,
        operator.AddSheet,
        operator.OpenSheet,
        operator.AddDrawingToSheet,
        operator.CreateSheets,
        operator.OpenView,
        operator.OpenViewCamera,
        operator.ActivateView,
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
        operator.OpenUpstream,
        operator.AddPropertySetTemplate,
        operator.RemovePropertySetTemplate,
        operator.EditPropertySetTemplate,
        operator.SavePropertySetTemplate,
        operator.AddPropertyTemplate,
        operator.RemovePropertyTemplate,
        operator.AddSectionPlane,
        operator.RemoveSectionPlane,
        operator.ReloadIfcFile,
        operator.AddIfcFile,
        operator.RemoveIfcFile,
        operator.SelectDocIfcFile,
        operator.AddAnnotation,
        operator.GenerateReferences,
        operator.ResizeText,
        operator.AddVariable,
        operator.RemoveVariable,
        operator.PropagateTextData,
        operator.SelectIfcPatchInput,
        operator.SelectIfcPatchOutput,
        operator.ExecuteIfcPatch,
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
        operator.AddPresentationLayer,
        operator.AssignPresentationLayer,
        operator.UnassignPresentationLayer,
        operator.RemovePresentationLayer,
        operator.UpdatePresentationLayer,
        operator.AddDrawingStyleAttribute,
        operator.RemoveDrawingStyleAttribute,
        operator.CopyPropertyToSelection,
        operator.CopyAttributeToSelection,
        operator.RefreshDrawingList,
        operator.SetBlenderClashSetA,
        operator.SetBlenderClashSetB,
        operator.ExecuteBlenderClash,
        operator.CleanWireframes,
        operator.LinkIfc,
        operator.SnapSpacesTogether,
        operator.CopyGrid,
        operator.AddSectionsAnnotations,
        prop.StrProperty,
        prop.Attribute,
        prop.Variable,
        prop.PropertySetTemplate,
        prop.PropertyTemplate,
        prop.ClashSource,
        prop.ClashSet,
        prop.SmartClashGroup,
        prop.Drawing,
        prop.Schedule,
        prop.DrawingStyle,
        prop.Sheet,
        prop.PresentationLayer,
        prop.BIMProperties,
        prop.DocProperties,
        prop.BIMLibrary,
        prop.IfcParameter,
        prop.BoundaryCondition,
        prop.PsetQto,
        prop.GlobalId,
        prop.RepresentationItem,
        prop.BIMObjectProperties,
        prop.BIMMaterialProperties,
        prop.SweptSolid,
        prop.ItemSlotMap,
        prop.BIMMeshProperties,
        prop.BIMCameraProperties,
        prop.BIMTextProperties,
        ui.BIM_PT_section_plane,
        ui.BIM_PT_drawings,
        ui.BIM_PT_schedules,
        ui.BIM_PT_sheets,
        ui.BIM_PT_psets,
        ui.BIM_PT_ifcclash,
        ui.BIM_PT_library,
        ui.BIM_PT_presentation_layers,
        ui.BIM_PT_patch,
        ui.BIM_PT_mvd,
        ui.BIM_PT_presentation_layer_data,
        ui.BIM_PT_object_structural,
        ui.BIM_PT_camera,
        ui.BIM_PT_text,
        ui.BIM_PT_modeling_utilities,
        ui.BIM_PT_annotation_utilities,
        ui.BIM_PT_clash_manager,
        ui.BIM_PT_misc_utilities,
        ui.BIM_UL_generic,
        ui.BIM_UL_drawinglist,
        ui.BIM_UL_clash_sets,
        ui.BIM_UL_smart_groups,
        ui.BIM_UL_topics,
        ui.BIM_ADDON_preferences,
    ]

    for module in modules.values():
        classes.extend(module.classes)

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
        bpy.types.Scene.DocProperties = bpy.props.PointerProperty(type=prop.DocProperties)
        bpy.types.Scene.BIMLibrary = bpy.props.PointerProperty(type=prop.BIMLibrary)
        bpy.types.Object.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
        bpy.types.Material.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties)
        bpy.types.Collection.BIMObjectProperties = bpy.props.PointerProperty(type=prop.BIMObjectProperties) # Check if we need this
        bpy.types.Material.BIMMaterialProperties = bpy.props.PointerProperty(type=prop.BIMMaterialProperties)
        bpy.types.Mesh.BIMMeshProperties = bpy.props.PointerProperty(type=prop.BIMMeshProperties)
        bpy.types.Camera.BIMCameraProperties = bpy.props.PointerProperty(type=prop.BIMCameraProperties)
        bpy.types.TextCurve.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
        bpy.types.SCENE_PT_unit.append(ui.ifc_units)

        for module in modules.values():
            module.register()

        bpy.app.handlers.depsgraph_update_pre.append(operator.depsgraph_update_pre_handler)
        bpy.app.handlers.load_post.append(prop.toggleDecorationsOnLoad)

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        bpy.app.handlers.load_post.remove(prop.setDefaultProperties)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        del bpy.types.Scene.BIMProperties
        del bpy.types.Scene.DocProperties
        del bpy.types.Object.BIMObjectProperties
        del bpy.types.Material.BIMObjectProperties
        del bpy.types.Collection.BIMObjectProperties # Check if we need this
        del bpy.types.Material.BIMMaterialProperties
        del bpy.types.Mesh.BIMMeshProperties
        del bpy.types.Camera.BIMCameraProperties
        del bpy.types.TextCurve.BIMTextProperties
        bpy.types.SCENE_PT_unit.remove(ui.ifc_units)

        for module in reversed(list(modules.values())):
            module.unregister()

        bpy.app.handlers.depsgraph_update_pre.remove(operator.depsgraph_update_pre_handler)
