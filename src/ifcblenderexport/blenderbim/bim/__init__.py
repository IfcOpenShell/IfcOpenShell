# Check if we are running in Blender before loading, to allow for multiprocessing
import sys

bpy = sys.modules.get("bpy")

if bpy is not None:
    import bpy
    import importlib
    from . import handler, ui, prop, operator

    modules = {
        "project": None,
        "search": None,
        "bcf": None,
        "root": None,
        "unit": None,
        "georeference": None,
        "context": None,
        "attribute": None,
        "type": None,
        "spatial": None,
        "void": None,
        "aggregate": None,
        "geometry": None,
        "cobie": None,
        "sequence": None,
        "material": None,
        "style": None,
        "layer": None,
        "model": None,
        "owner": None,
        "pset": None,
        "qto": None,
        "classification": None,
        "constraint": None,
        "document": None,
        "pset_template": None,
        "clash": None,
        "csv": None,
        "bimtester": None,
        "diff": None,
        "patch": None,
        "covetool": None,
        "debug": None,
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
        operator.OpenUpstream,
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
        operator.AddDrawingStyleAttribute,
        operator.RemoveDrawingStyleAttribute,
        operator.CopyPropertyToSelection,
        operator.CopyAttributeToSelection,
        operator.RefreshDrawingList,
        operator.CleanWireframes,
        operator.LinkIfc,
        operator.SnapSpacesTogether,
        operator.CopyGrid,
        operator.AddSectionsAnnotations,
        prop.StrProperty,
        prop.Attribute,
        prop.Variable,
        prop.Drawing,
        prop.Schedule,
        prop.DrawingStyle,
        prop.Sheet,
        prop.BIMProperties,
        prop.DocProperties,
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
        ui.BIM_PT_camera,
        ui.BIM_PT_text,
        ui.BIM_PT_annotation_utilities,
        ui.BIM_PT_misc_utilities,
        ui.BIM_UL_generic,
        ui.BIM_UL_drawinglist,
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
        handler.setDefaultProperties(scene)
        bpy.app.handlers.depsgraph_update_post.remove(on_register)

    def register():
        for cls in classes:
            bpy.utils.register_class(cls)
        bpy.app.handlers.depsgraph_update_post.append(on_register)
        bpy.app.handlers.load_post.append(handler.setDefaultProperties)
        bpy.app.handlers.load_post.append(handler.loadIfcStore)
        bpy.app.handlers.save_pre.append(handler.ensureIfcExported)
        bpy.app.handlers.save_pre.append(handler.storeIdMap)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        bpy.types.Scene.BIMProperties = bpy.props.PointerProperty(type=prop.BIMProperties)
        bpy.types.Scene.DocProperties = bpy.props.PointerProperty(type=prop.DocProperties)
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
        bpy.app.handlers.load_post.append(handler.toggleDecorationsOnLoad)

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        bpy.app.handlers.load_post.remove(handler.setDefaultProperties)
        bpy.app.handlers.load_post.remove(handler.loadIfcStore)
        bpy.app.handlers.save_pre.remove(handler.storeIdMap)
        bpy.app.handlers.save_pre.remove(handler.ensureIfcExported)
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
        bpy.app.handlers.load_post.remove(handler.toggleDecorationsOnLoad)
