import bpy
import time
import logging
from . import export

class ExportIFC(bpy.types.Operator):
    bl_idname = "export.ifc"
    bl_label = "Export .ifc file"
    filename_ext = ".ifc"
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".ifc")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        start = time.time()
        ifc_export_settings = export.IfcExportSettings()
        logging.basicConfig(
            filename=bpy.context.scene.BIMProperties.data_dir + 'export.log',
            filemode='a', level=logging.DEBUG)
        ifc_export_settings.logger = logging.getLogger('ExportIFC')
        ifc_export_settings.logger.info('Starting export')
        ifc_export_settings.data_dir = bpy.context.scene.BIMProperties.data_dir
        ifc_export_settings.schema_dir = bpy.context.scene.BIMProperties.schema_dir
        ifc_export_settings.output_file = bpy.path.ensure_ext(self.filepath, '.ifc')
        ifc_parser = export.IfcParser(ifc_export_settings)
        ifc_schema = export.IfcSchema(ifc_export_settings)
        qto_calculator = export.QtoCalculator()
        ifc_exporter = export.IfcExporter(ifc_export_settings, ifc_schema, ifc_parser, qto_calculator)
        ifc_exporter.export()
        ifc_export_settings.logger.info('Export finished in {:.2f} seconds'.format(time.time() - start))
        return {'FINISHED'}

class AssignClass(bpy.types.Operator):
    bl_idname = 'bim.assign_class'
    bl_label = 'Assign IFC Class'

    def execute(self, context):
        for object in bpy.context.selected_objects:
            existing_class = None
            if '/' in object.name \
                and object.name[0:3] == 'Ifc':
                existing_class = object.name.split('/')[0]
            if existing_class:
                object.name = '{}/{}'.format(
                    bpy.context.scene.BIMProperties.ifc_class,
                    object.name.split('/')[1])
            else:
                object.name = '{}/{}'.format(
                    bpy.context.scene.BIMProperties.ifc_class,
                    object.name)
            if existing_class != bpy.context.scene.BIMProperties.ifc_class \
                and 'IfcPredefinedType' in object.keys():
                del(object['IfcPredefinedType'])
            object['IfcPredefinedType'] = bpy.context.scene.BIMProperties.ifc_predefined_type
            if bpy.context.scene.BIMProperties.ifc_predefined_type == 'USERDEFINED':
                object['IfcObjectType'] = bpy.context.scene.BIMProperties.ifc_userdefined_type
            elif 'IfcObjectType' in object.keys():
                del(object['IfcObjectType'])
        return {'FINISHED'}

class SelectDataDir(bpy.types.Operator):
    bl_idname = "bim.select_data_dir"
    bl_label = "Select Data Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.data_dir = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SelectSchemaDir(bpy.types.Operator):
    bl_idname = "bim.select_schema_dir"
    bl_label = "Select Schema Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.schema_dir = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
