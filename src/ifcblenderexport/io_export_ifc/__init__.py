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
    ui.BIMProperties,
    ui.MaterialProperties,
    ui.BIMPanel,
    ui.MVDPanel,
    ui.MaterialPanel,
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
    bpy.types.Material.MaterialProperties = bpy.props.PointerProperty(type=ui.MaterialProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    del(bpy.types.Scene.BIMProperties)
    del(bpy.types.Scene.MaterialProperties)

if __name__ == "__main__":
    register()
