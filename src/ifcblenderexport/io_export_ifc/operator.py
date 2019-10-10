import bpy
import time
import logging
from . import export_ifc
from . import import_ifc
from bpy_extras.io_utils import ImportHelper
from itertools import cycle

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
        ifc_export_settings = export_ifc.IfcExportSettings()
        logging.basicConfig(
            filename=bpy.context.scene.BIMProperties.data_dir + 'process.log',
            filemode='a', level=logging.DEBUG)
        ifc_export_settings.logger = logging.getLogger('ExportIFC')
        ifc_export_settings.logger.info('Starting export')
        ifc_export_settings.data_dir = bpy.context.scene.BIMProperties.data_dir
        ifc_export_settings.schema_dir = bpy.context.scene.BIMProperties.schema_dir
        ifc_export_settings.output_file = bpy.path.ensure_ext(self.filepath, '.ifc')
        ifc_export_settings.has_representations = bpy.context.scene.BIMProperties.export_has_representations
        ifc_parser = export_ifc.IfcParser(ifc_export_settings)
        ifc_schema = export_ifc.IfcSchema(ifc_export_settings)
        qto_calculator = export_ifc.QtoCalculator()
        ifc_exporter = export_ifc.IfcExporter(ifc_export_settings, ifc_schema, ifc_parser, qto_calculator)
        ifc_exporter.export()
        ifc_export_settings.logger.info('Export finished in {:.2f} seconds'.format(time.time() - start))
        return {'FINISHED'}

class ImportIFC(bpy.types.Operator, ImportHelper):
    bl_idname = "import.ifc"
    bl_label = "Import .ifc file"

    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={'HIDDEN'})

    def execute(self, context):
        start = time.time()
        ifc_import_settings = import_ifc.IfcImportSettings()
        logging.basicConfig(
            filename=bpy.context.scene.BIMProperties.data_dir + 'process.log',
            filemode='a', level=logging.DEBUG)
        ifc_import_settings.logger = logging.getLogger('ImportIFC')
        ifc_import_settings.logger.info('Starting import')
        ifc_import_settings.input_file = self.filepath
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.execute()
        ifc_import_settings.logger.info('Import finished in {:.2f} seconds'.format(time.time() - start))
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

class SelectClass(bpy.types.Operator):
    bl_idname = 'bim.select_class'
    bl_label = 'Select IFC Class'

    def execute(self, context):
        for object in bpy.context.visible_objects:
            if '/' in object.name \
                and object.name[0:3] == 'Ifc' \
                and object.name.split('/')[0] == bpy.context.scene.BIMProperties.ifc_class:
                object.select_set(True)
        return {'FINISHED'}

class SelectType(bpy.types.Operator):
    bl_idname = 'bim.select_type'
    bl_label = 'Select IFC Type'

    def execute(self, context):
        for object in bpy.context.visible_objects:
            if '/' in object.name \
                and object.name[0:3] == 'Ifc' \
                and object.name.split('/')[0] == bpy.context.scene.BIMProperties.ifc_class \
                and 'IfcPredefinedType' in object.keys() \
                and object['IfcPredefinedType'] == bpy.context.scene.BIMProperties.ifc_predefined_type:
                if bpy.context.scene.BIMProperties.ifc_predefined_type != 'USERDEFINED':
                    object.select_set(True)
                elif object['IfcObjectType'] == bpy.context.scene.BIMProperties.ifc_userdefined_type:
                    object.select_set(True)
        return {'FINISHED'}

class ColourByClass(bpy.types.Operator):
    bl_idname = 'bim.colour_by_class'
    bl_label = 'Colour by Class'

    def execute(self, context):
        colour_list = [
            (.651, .81, .892, 1),
            (.121, .471, .706, 1),
            (.699, .876, .54, 1),
            (.199, .629, .174, 1),
            (.983, .605, .602, 1),
            (.89, .101, .112, 1),
            (.989, .751, .427, 1),
            (.986, .497, .1, 1),
            (.792, .699, .839, 1),
            (.414, .239, .603, 1),
            (.993, .999, .6, 1),
            (.693, .349, .157, 1)]
        colours = cycle(colour_list)
        ifc_classes = {}
        for object in bpy.context.selected_objects:
            if '/' not in object.name:
                continue
            ifc_class = object.name.split('/')[0]
            if ifc_class not in ifc_classes:
                ifc_classes[ifc_class] = next(colours)
            object.color = ifc_classes[ifc_class]
        return {'FINISHED'}

class ResetObjectColours(bpy.types.Operator):
    bl_idname = 'bim.reset_object_colours'
    bl_label = 'Reset Colours'

    def execute(self, context):
        for object in bpy.context.selected_objects:
            object.color = (1, 1, 1, 1)
        return {'FINISHED'}

class ApproveClass(bpy.types.Operator):
    bl_idname = 'bim.approve_class'
    bl_label = 'Approve Class'

    def execute(self, context):
        with open(bpy.context.scene.BIMProperties.data_dir + 'audit.txt', 'a') as file:
            for object in bpy.context.selected_objects:
                file.write('Then the element {} is an {}\n'.format(
                    object['IfcGlobalId'], object.name.split('/')[0]))
        return {'FINISHED'}

class RejectClass(bpy.types.Operator):
    bl_idname = 'bim.reject_class'
    bl_label = 'Reject Class'

    def execute(self, context):
        with open(bpy.context.scene.BIMProperties.data_dir + 'audit.txt', 'a') as file:
            for object in bpy.context.selected_objects:
                file.write('Then the element {} is an {}\n'.format(
                    object['IfcGlobalId'], bpy.context.scene.BIMProperties.ifc_class))
        return {'FINISHED'}

class RejectElement(bpy.types.Operator):
    bl_idname = 'bim.reject_element'
    bl_label = 'Reject Element'

    def execute(self, context):
        with open(bpy.context.scene.BIMProperties.data_dir + 'audit.txt', 'a') as file:
            for object in bpy.context.selected_objects:
                file.write('Then the element {} should not exist because {}\n'.format(
                    object['IfcGlobalId'], bpy.context.scene.BIMProperties.qa_reject_element_reason))
        return {'FINISHED'}

class SelectAudited(bpy.types.Operator):
    bl_idname = 'bim.select_audited'
    bl_label = 'Select Audited'

    def execute(self, context):
        with open(bpy.context.scene.BIMProperties.data_dir + 'audit.txt') as file:
            for line in file:
                for object in bpy.context.visible_objects:
                    if 'IfcGlobalId' in object.keys() \
                        and object['IfcGlobalId'] == line.split(' ')[3]:
                        object.select_set(True)
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
