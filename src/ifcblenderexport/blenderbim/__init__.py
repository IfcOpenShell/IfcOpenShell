bl_info = {
    "name": "BlenderBIM",
    "description": "Author, import, and export files in the "
        "Industry Foundation Classes (.ifc) file format",
    "author": "Dion Moult, IfcOpenShell",
    "blender": (2, 80, 0),
    "version": (0, 0, 999999),
    "location": "File > Export, File > Import, Scene / Object / Material / Mesh Properties",
    "tracker_url": "https://sourceforge.net/p/ifcopenshell/"
        "_list/tickets?source=navbar",
    "category": "Import-Export"
    }

# Check if we are running in Blender before loading, to allow for multiprocessing
import sys
import os
bpy = sys.modules.get('bpy')

if bpy is not None:
    cwd = os.path.dirname(os.path.realpath(__file__))
    # This workaround is for Mac and Linux Conda builds, which have an rpath set
    # to $ORIGIN/../../../
    lib_dir = os.path.join(cwd, '..', 'lib')
    if os.path.isdir(lib_dir):
        import shutil
        files = os.listdir(lib_dir)
        for f in files:
            shutil.move(os.path.join(lib_dir, f), os.path.join(lib_dir, '..', '..', '..'))

    import bpy
    from . import ui, prop, operator

    classes = (
        operator.AssignClass,
        operator.SelectClass,
        operator.SelectType,
        operator.SelectFeaturesDir,
        operator.SelectDiffJsonFile,
        operator.SelectDiffNewFile,
        operator.SelectDiffOldFile,
        operator.SelectDataDir,
        operator.SelectSchemaDir,
        operator.SelectIfcFile,
        operator.ExportIFC,
        operator.ImportIFC,
        operator.ColourByClass,
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
        operator.AssignPset,
        operator.UnassignPset,
        operator.AddPset,
        operator.RemovePset,
        operator.AddOverridePset,
        operator.RemoveOverridePset,
        operator.AddMaterialPset,
        operator.RemoveMaterialPset,
        operator.AddDocument,
        operator.RemoveDocument,
        operator.GenerateGlobalId,
        operator.AddAttribute,
        operator.RemoveAttribute,
        operator.AddMaterialAttribute,
        operator.RemoveMaterialAttribute,
        operator.QuickProjectSetup,
        operator.SelectGlobalId,
        operator.CreateAggregate,
        operator.EditAggregate,
        operator.SaveAggregate,
        operator.ExplodeAggregate,
        operator.AssignClassification,
        operator.UnassignClassification,
        operator.RemoveClassification,
        operator.FetchLibraryInformation,
        operator.FetchExternalMaterial,
        operator.FetchObjectPassport,
        operator.AddSubcontext,
        operator.RemoveSubcontext,
        operator.CutSection,
        operator.CreateSheets,
        operator.GenerateDigitalTwin,
        operator.CreateView,
        operator.ActivateView,
        operator.ExecuteIfcDiff,
        operator.AssignContext,
        prop.Subcontext,
        prop.BIMProperties,
        prop.DocProperties,
        prop.BIMLibrary,
        prop.MapConversion,
        prop.TargetCRS,
        prop.Attribute,
        prop.BoundaryCondition,
        prop.Pset,
        prop.Document,
        prop.Classification,
        prop.GlobalId,
        prop.BIMObjectProperties,
        prop.BIMMaterialProperties,
        prop.SweptSolid,
        prop.BIMMeshProperties,
        prop.BIMCameraProperties,
        ui.BIM_PT_documentation,
        ui.BIM_PT_bim,
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
        ui.BIM_PT_camera,
        )

    def menu_func_export(self, context):
        self.layout.operator(operator.ExportIFC.bl_idname,
             text="Industry Foundation Classes (.ifc)")

    def menu_func_import(self, context):
        self.layout.operator(operator.ImportIFC.bl_idname,
             text="Industry Foundation Classes (.ifc)")

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
        del(bpy.types.Scene.DocProperties)
        del(bpy.types.Scene.MapConversion)
        del(bpy.types.Scene.TargetCRS)
        del(bpy.types.Object.BIMObjectProperties)
        del(bpy.types.Collection.BIMObjectProperties)
        del(bpy.types.Material.BIMMaterialProperties)
        del(bpy.types.Mesh.BIMMeshProperties)
        del(bpy.types.Mesh.BIMCameraProperties)

    if __name__ == "__main__":
        register()
