bl_info = {
    "name": "IfcBlenderExport",
    "description": "Export files in the "
        "Industry Foundation Classes (.ifc) file format",
    "author": "Dion Moult, IfcOpenShell",
    "blender": (2, 80, 0),
    "location": "File > Export",
    "tracker_url": "https://sourceforge.net/p/ifcopenshell/"
        "_list/tickets?source=navbar",
    "category": "Import-Export"
    }

import bpy
from . import ui
from . import operator

classes = (
    operator.AssignClass,
    operator.SelectClass,
    operator.SelectType,
    operator.SelectFeaturesDir,
    operator.SelectDiffJsonFile,
    operator.SelectDataDir,
    operator.SelectSchemaDir,
    operator.ExportIFC,
    operator.ImportIFC,
    operator.ColourByClass,
    operator.ResetObjectColours,
    operator.ApproveClass,
    operator.RejectClass,
    operator.SelectAudited,
    operator.RejectElement,
    operator.SelectExternalMaterialDir,
    operator.AssignSweptSolidProfile,
    operator.AssignSweptSolidExtrusion,
    operator.AssignPset,
    operator.UnassignPset,
    operator.AddPset,
    operator.RemovePset,
    operator.AddDocument,
    operator.RemoveDocument,
    operator.GenerateGlobalId,
    operator.AddAttribute,
    operator.RemoveAttribute,
    operator.QuickProjectSetup,
    operator.SelectGlobalId,
    operator.CreateAggregate,
    operator.EditAggregate,
    operator.SaveAggregate,
    operator.AssignClassification,
    operator.UnassignClassification,
    operator.RemoveClassification,
    ui.BIMProperties,
    ui.MapConversion,
    ui.TargetCRS,
    ui.Attribute,
    ui.Pset,
    ui.Document,
    ui.Classification,
    ui.BIMObjectProperties,
    ui.BIMMaterialProperties,
    ui.BIMMeshProperties,
    ui.GISPanel,
    ui.BIMPanel,
    ui.QAPanel,
    ui.DiffPanel,
    ui.MVDPanel,
    ui.MaterialPanel,
    ui.MeshPanel,
    ui.ObjectPanel,
    )

def menu_func_export(self, context):
    self.layout.operator(operator.ExportIFC.bl_idname,
         text="Industry Foundation Classes (.ifc)")

def menu_func_import(self, context):
    self.layout.operator(operator.ImportIFC.bl_idname,
         text="Industry Foundation Classes (.ifc)")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.Scene.BIMProperties = bpy.props.PointerProperty(type=ui.BIMProperties)
    bpy.types.Scene.MapConversion = bpy.props.PointerProperty(type=ui.MapConversion)
    bpy.types.Scene.TargetCRS = bpy.props.PointerProperty(type=ui.TargetCRS)
    bpy.types.Object.BIMObjectProperties = bpy.props.PointerProperty(type=ui.BIMObjectProperties)
    bpy.types.Collection.BIMObjectProperties = bpy.props.PointerProperty(type=ui.BIMObjectProperties)
    bpy.types.Material.BIMMaterialProperties = bpy.props.PointerProperty(type=ui.BIMMaterialProperties)
    bpy.types.Mesh.BIMMeshProperties = bpy.props.PointerProperty(type=ui.BIMMeshProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    del(bpy.types.Scene.BIMProperties)
    del(bpy.types.Scene.MapConversion)
    del(bpy.types.Scene.TargetCRS)
    del(bpy.types.Object.BIMObjectProperties)
    del(bpy.types.Collection.BIMObjectProperties)
    del(bpy.types.Material.BIMMaterialProperties)
    del(bpy.types.Mesh.BIMMeshProperties)

if __name__ == "__main__":
    register()
