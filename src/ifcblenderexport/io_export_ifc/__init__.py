bl_info = {
    "name": "IfcBlenderExport",
    "description": "Export files in the "
        "Industry Foundation Classes (.ifc) file format",
    "author": "Dion Moult, IfcOpenShell",
    "blender": (2, 80, 0),
    "location": "File > Export",
    "tracker_url": "https://sourceforge.net/p/ifcopenshell/"
        "_list/tickets?source=navbar",
    "category": "Import-Export"}

if "bpy" in locals():
    from importlib import reload
    reload(export)
    del reload

import bpy
import time
from . import export
import os
from bpy.props import (StringProperty,)

cwd = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class ExportIFC(bpy.types.Operator):
    bl_idname = "export.ifc"
    bl_label = "Export .ifc file"
    filename_ext = ".ifc"
    filepath: StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".ifc")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        print('# Starting export')
        start = time.time()
        ifc_export_settings = export.IfcExportSettings()
        ifc_export_settings.bim_path = cwd
        ifc_export_settings.output_file = bpy.path.ensure_ext(self.filepath, '.ifc')
        ifc_parser = export.IfcParser(ifc_export_settings)
        ifc_schema = export.IfcSchema(ifc_export_settings)
        qto_calculator = export.QtoCalculator()
        ifc_exporter = export.IfcExporter(ifc_export_settings, ifc_schema, ifc_parser, qto_calculator)
        ifc_exporter.export()
        print('# Export finished in {:.2f} seconds'.format(time.time() - start))
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ExportIFC.bl_idname,
         text="Industry Foundation Classes (.ifc)")

classes = (ExportIFC,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
