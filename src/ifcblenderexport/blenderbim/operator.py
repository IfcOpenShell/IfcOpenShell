import os
import bpy
import time
import json
import logging
from . import ifcopenshell
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
        ifc_export_settings.should_export_all_materials_as_styled_items = bpy.context.scene.BIMProperties.export_should_export_all_materials_as_styled_items
        ifc_export_settings.should_use_presentation_style_assignment = bpy.context.scene.BIMProperties.export_should_use_presentation_style_assignment
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
        ifc_import_settings.diff_file = bpy.context.scene.BIMProperties.diff_json_file
        ifc_import_settings.should_ignore_site_coordinates = bpy.context.scene.BIMProperties.import_should_ignore_site_coordinates
        ifc_import_settings.should_import_curves = bpy.context.scene.BIMProperties.import_should_import_curves
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.execute()
        ifc_import_settings.logger.info('Import finished in {:.2f} seconds'.format(time.time() - start))
        return {'FINISHED'}

class SelectGlobalId(bpy.types.Operator):
    bl_idname = 'bim.select_global_id'
    bl_label = 'Select GlobalId'

    def execute(self, context):
        for object in bpy.context.visible_objects:
            index = object.BIMObjectProperties.attributes.find('GlobalId')
            if index != -1 \
                and object.BIMObjectProperties.attributes[index].string_value == bpy.context.scene.BIMProperties.global_id:
                object.select_set(True)
                break
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
            predefined_type_index = object.BIMObjectProperties.attributes.find('PredefinedType')
            if predefined_type_index >= 0:
                object.BIMObjectProperties.attributes.remove(predefined_type_index)
            object_type_index = object.BIMObjectProperties.attributes.find('ObjectType')
            if object_type_index >= 0:
                object.BIMObjectProperties.attributes.remove(object_type_index)
            if bpy.context.scene.BIMProperties.ifc_predefined_type:
                predefined_type = object.BIMObjectProperties.attributes.add()
                predefined_type.name = 'PredefinedType'
                predefined_type.string_value = bpy.context.scene.BIMProperties.ifc_predefined_type # TODO: make it an enum
            if bpy.context.scene.BIMProperties.ifc_predefined_type == 'USERDEFINED':
                object_type = object.BIMObjectProperties.attributes.add()
                object_type.name = 'ObjectType'
                object_type.string_value = bpy.context.scene.BIMProperties.ifc_userdefined_type
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
                    and 'PredefinedType' in object.BIMObjectProperties.attributes \
                    and object.BIMObjectProperties.attributes['PredefinedType'].string_value == bpy.context.scene.BIMProperties.ifc_predefined_type:
                if bpy.context.scene.BIMProperties.ifc_predefined_type != 'USERDEFINED':
                    object.select_set(True)
                elif 'ObjectType' in object.BIMObjectProperties.attributes \
                        and object.BIMObjectProperties.attributes['ObjectType'].string_value == bpy.context.scene.BIMProperties.ifc_userdefined_type:
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
                index = object.BIMObjectProperties.attributes.find('GlobalId')
                if index == -1:
                    continue
                file.write('Then the element {} is an {}\n'.format(
                    object.BIMObjectProperties.attributes[index].string_value,
                    object.name.split('/')[0]))
        return {'FINISHED'}

class RejectClass(bpy.types.Operator):
    bl_idname = 'bim.reject_class'
    bl_label = 'Reject Class'

    def execute(self, context):
        with open(bpy.context.scene.BIMProperties.data_dir + 'audit.txt', 'a') as file:
            for object in bpy.context.selected_objects:
                file.write('Then the element {} is an {}\n'.format(
                    object.BIMObjectProperties.attributes[
                        object.BIMObjectProperties.attributes.find('GlobalId')].string_value,
                    bpy.context.scene.BIMProperties.audit_ifc_class))
        return {'FINISHED'}

class RejectElement(bpy.types.Operator):
    bl_idname = 'bim.reject_element'
    bl_label = 'Reject Element'

    def execute(self, context):
        with open(bpy.context.scene.BIMProperties.data_dir + 'audit.txt', 'a') as file:
            for object in bpy.context.selected_objects:
                file.write('Then the element {} should not exist because {}\n'.format(
                    object.BIMObjectProperties.attributes[
                        object.BIMObjectProperties.attributes.find('GlobalId')].string_value,
                    bpy.context.scene.BIMProperties.qa_reject_element_reason))
        return {'FINISHED'}

class SelectAudited(bpy.types.Operator):
    bl_idname = 'bim.select_audited'
    bl_label = 'Select Audited'

    def execute(self, context):
        audited_global_ids = []
        with open(bpy.context.scene.BIMProperties.data_dir + 'audit.txt') as file:
            for line in file:
                audited_global_ids.append(line.split(' ')[3])
        for object in bpy.context.visible_objects:
            index = object.BIMObjectProperties.attributes.find('GlobalId')
            if index != -1 \
                and object.BIMObjectProperties.attributes[index].string_value in audited_global_ids:
                object.select_set(True)
        return {'FINISHED'}

class QuickProjectSetup(bpy.types.Operator):
    bl_idname = 'bim.quick_project_setup'
    bl_label = 'Quick Project Setup'

    def execute(self, context):
        project = bpy.data.collections.new('IfcProject/My Project')
        bpy.context.scene.collection.children.link(project)
        site = bpy.data.collections.new('IfcSite/My Site')
        project.children.link(site)
        building = bpy.data.collections.new('IfcBuilding/My Building')
        site.children.link(building)
        building_storey = bpy.data.collections.new('IfcBuildingStorey/Ground Floor')
        building.children.link(building_storey)
        return {'FINISHED'}

class AssignPset(bpy.types.Operator):
    bl_idname = 'bim.assign_pset'
    bl_label = 'Assign Pset'

    def execute(self, context):
        for object in bpy.context.selected_objects:
            index = object.BIMObjectProperties.psets.find(bpy.context.scene.BIMProperties.pset_name)
            if index >= 0:
                global_id = object.BIMObjectProperties.psets[index]
            else:
                global_id = object.BIMObjectProperties.psets.add()
            global_id.name = bpy.context.scene.BIMProperties.pset_name
            global_id.file = bpy.context.scene.BIMProperties.pset_file
        return {'FINISHED'}

class UnassignPset(bpy.types.Operator):
    bl_idname = 'bim.unassign_pset'
    bl_label = 'Unassign Pset'

    def execute(self, context):
        for object in bpy.context.selected_objects:
            index = object.BIMObjectProperties.psets.find(bpy.context.scene.BIMProperties.pset_name)
            if index != -1:
                object.BIMObjectProperties.psets.remove(index)
        return {'FINISHED'}

class AddPset(bpy.types.Operator):
    bl_idname = 'bim.add_pset'
    bl_label = 'Add Pset'

    # This is a temporary measure until we get a better UI
    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.psets.add()
        return {'FINISHED'}

class RemovePset(bpy.types.Operator):
    bl_idname = 'bim.remove_pset'
    bl_label = 'Remove Pset'
    pset_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.psets.remove(self.pset_index)
        return {'FINISHED'}

class AddDocument(bpy.types.Operator):
    bl_idname = 'bim.add_document'
    bl_label = 'Add Document'

    def execute(self, context):
        document = bpy.context.active_object.BIMObjectProperties.documents.add()
        document.file = bpy.context.active_object.BIMObjectProperties.applicable_documents
        return {'FINISHED'}

class RemoveDocument(bpy.types.Operator):
    bl_idname = 'bim.remove_document'
    bl_label = 'Remove Document'
    document_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.documents.remove(self.document_index)
        return {'FINISHED'}

class GenerateGlobalId(bpy.types.Operator):
    bl_idname = 'bim.generate_global_id'
    bl_label = 'Generate GlobalId'

    def execute(self, context):
        index = bpy.context.active_object.BIMObjectProperties.attributes.find('GlobalId')
        if index >= 0:
            global_id = bpy.context.active_object.BIMObjectProperties.attributes[index]
        else:
            global_id = bpy.context.active_object.BIMObjectProperties.attributes.add()
        global_id.name = 'GlobalId'
        global_id.data_type = 'string'
        global_id.string_value = ifcopenshell.guid.new()
        return {'FINISHED'}

class AddAttribute(bpy.types.Operator):
    bl_idname = 'bim.add_attribute'
    bl_label = 'Add Attribute'

    def execute(self, context):
        if bpy.context.active_object.BIMObjectProperties.applicable_attributes:
            attribute = bpy.context.active_object.BIMObjectProperties.attributes.add()
            attribute.name = bpy.context.active_object.BIMObjectProperties.applicable_attributes
        return {'FINISHED'}

class RemoveAttribute(bpy.types.Operator):
    bl_idname = 'bim.remove_attribute'
    bl_label = 'Remove Attribute'
    attribute_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.attributes.remove(self.attribute_index)
        return {'FINISHED'}

class AddSweptSolid(bpy.types.Operator):
    bl_idname = 'bim.add_swept_solid'
    bl_label = 'Add Swept Solid'

    def execute(self, context):
        swept_solids = bpy.context.active_object.data.BIMMeshProperties.swept_solids
        swept_solid = swept_solids.add()
        swept_solid.name = 'Swept Solid {}'.format(len(swept_solids))
        return {'FINISHED'}

class RemoveSweptSolid(bpy.types.Operator):
    bl_idname = 'bim.remove_swept_solid'
    bl_label = 'Remove Swept Solid'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.data.BIMMeshProperties.swept_solids.remove(self.index)
        return {'FINISHED'}

class AssignSweptSolidOuterCurve(bpy.types.Operator):
    bl_idname = 'bim.assign_swept_solid_outer_curve'
    bl_label = 'Assign Outer Curve'
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != 'EDIT_MESH':
            return {'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        vertices = [v.index for v in bpy.context.active_object.data.vertices if v.select == True]
        print(vertices)
        bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].outer_curve = json.dumps(vertices)
        return {'FINISHED'}

class SelectSweptSolidOuterCurve(bpy.types.Operator):
    bl_idname = 'bim.select_swept_solid_outer_curve'
    bl_label = 'Select Outer Curve'
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != 'EDIT_MESH':
            return {'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        outer_curve = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].outer_curve
        if not outer_curve:
            return {'FINISHED'}
        indices = json.loads(outer_curve)
        for index in indices:
            bpy.context.active_object.data.vertices[index].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class AddSweptSolidInnerCurve(bpy.types.Operator):
    bl_idname = 'bim.add_swept_solid_inner_curve'
    bl_label = 'Add Inner Curve'
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != 'EDIT_MESH':
            return {'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        vertices = [v.index for v in bpy.context.active_object.data.vertices if v.select == True]
        swept_solid = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index]
        if swept_solid.inner_curves:
            curves = json.loads(swept_solid.inner_curves)
        else:
            curves = []
        curves.append(vertices)
        swept_solid.inner_curves = json.dumps(curves)
        return {'FINISHED'}

class SelectSweptSolidInnerCurves(bpy.types.Operator):
    bl_idname = 'bim.select_swept_solid_inner_curves'
    bl_label = 'Select Inner Curves'
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != 'EDIT_MESH':
            return {'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        inner_curves = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].inner_curves
        if not inner_curves:
            return {'FINISHED'}
        curves = json.loads(inner_curves)
        for curve in curves:
            for index in curve:
                bpy.context.active_object.data.vertices[index].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class AssignSweptSolidExtrusion(bpy.types.Operator):
    bl_idname = 'bim.assign_swept_solid_extrusion'
    bl_label = 'Assign Extrusion'
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != 'EDIT_MESH':
            return {'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        vertices = [v.index for v in bpy.context.active_object.data.vertices if v.select == True]
        bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].extrusion = json.dumps(vertices)
        return {'FINISHED'}

class SelectSweptSolidExtrusion(bpy.types.Operator):
    bl_idname = 'bim.select_swept_solid_extrusion'
    bl_label = 'Select Extrusion'
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != 'EDIT_MESH':
            return {'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        extrusion = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].extrusion
        if not extrusion:
            return {'FINISHED'}
        indices = json.loads(extrusion)
        for index in indices:
            bpy.context.active_object.data.vertices[index].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class SelectExternalMaterialDir(bpy.types.Operator):
    bl_idname = "bim.select_external_material_dir"
    bl_label = "Select Material File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.active_object.active_material.BIMMaterialProperties.location = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SelectDiffJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_json_file"
    bl_label = "Select Diff JSON File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.diff_json_file = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SelectFeaturesDir(bpy.types.Operator):
    bl_idname = "bim.select_features_dir"
    bl_label = "Select Features Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.features_dir = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

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

class CreateAggregate(bpy.types.Operator):
    bl_idname = 'bim.create_aggregate'
    bl_label = 'Create Aggregate'

    def execute(self, context):
        spatial_container = None
        for obj in bpy.context.selected_objects:
            if obj.instance_collection:
                return {'FINISHED'}
            for collection in obj.users_collection:
                if 'IfcRelAggregates' in collection.name:
                    return {'FINISHED'}
                elif collection.name[0:3] == 'Ifc':
                    spatial_container = collection
        if not spatial_container:
            return {'FINISHED'}

        aggregate = bpy.data.collections.new('IfcRelAggregates/{}'.format(
            bpy.context.scene.BIMProperties.aggregate_class))
        bpy.context.scene.collection.children.link(aggregate)
        for obj in bpy.context.selected_objects:
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            aggregate.objects.link(obj)

        instance = bpy.data.objects.new('{}/{}'.format(
            bpy.context.scene.BIMProperties.aggregate_class,
            bpy.context.scene.BIMProperties.aggregate_name),
            None)
        instance.instance_type = 'COLLECTION'
        instance.instance_collection = aggregate
        spatial_container.objects.link(instance)

        bpy.context.view_layer.layer_collection.children[aggregate.name].hide_viewport = True
        return {'FINISHED'}

class EditAggregate(bpy.types.Operator):
    bl_idname = 'bim.edit_aggregate'
    bl_label = 'Edit Aggregate'

    def execute(self, context):
        obj = bpy.context.active_object
        if obj.instance_type != 'COLLECTION' \
            or 'IfcRelAggregates' not in obj.instance_collection.name:
            return {'FINISHED'}
        bpy.context.view_layer.objects[obj.name].hide_viewport = True
        bpy.context.view_layer.layer_collection.children[obj.instance_collection.name].hide_viewport = False
        return {'FINISHED'}

class SaveAggregate(bpy.types.Operator):
    bl_idname = 'bim.save_aggregate'
    bl_label = 'Save Aggregate'

    def execute(self, context):
        obj = bpy.context.active_object
        aggregate = None
        for collection in obj.users_collection:
            if 'IfcRelAggregates' in collection.name:
                bpy.context.view_layer.layer_collection.children[collection.name].hide_viewport = True
                aggregate = collection
                break
        if not aggregate:
            return {'FINISHED'}
        for obj in bpy.context.view_layer.objects:
            if obj.instance_collection == aggregate:
                obj.hide_viewport = False
        return {'FINISHED'}

class AssignClassification(bpy.types.Operator):
    bl_idname = 'bim.assign_classification'
    bl_label = 'Assign Classification'

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            classification = obj.BIMObjectProperties.classifications.add()
            classification.identification = bpy.context.scene.BIMProperties.reference
        return {'FINISHED'}


class UnassignClassification(bpy.types.Operator):
    bl_idname = 'bim.unassign_classification'
    bl_label = 'Unassign Classification'

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            index = object.BIMObjectProperties.classifications.find(bpy.context.scene.BIMProperties.classification)
            if index != -1:
                object.BIMObjectProperties.classifications.remove(index)

            obj.BIMObjectProperties.classification = ''
        return {'FINISHED'}


class RemoveClassification(bpy.types.Operator):
    bl_idname = 'bim.remove_classification'
    bl_label = 'Remove Classification'
    classification_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.classifications.remove(self.classification_index)
        return {'FINISHED'}


class FetchExternalMaterial(bpy.types.Operator):
    bl_idname = 'bim.fetch_external_material'
    bl_label = 'Fetch External Material'

    def execute(self, context):
        location = bpy.context.active_object.active_material.BIMMaterialProperties.location
        if location[-6:] != '.mpass':
            return {'FINISHED'}
        with open(location) as f:
            self.material_pass = json.load(f)
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE' \
                and 'eevee' in self.material_pass:
            self.fetch_eevee_or_cycles('eevee')
        elif bpy.context.scene.render.engine == 'CYCLES' \
                and 'cycles' in self.material_pass:
            self.fetch_eevee_or_cycles('cycles')
        return {'FINISHED'}

    def fetch_eevee_or_cycles(self, name):
        identification = bpy.context.active_object.active_material.BIMMaterialProperties.identification
        bpy.ops.wm.link(
            filename=identification,
            directory=os.path.join(self.material_pass[name]['uri'], 'Material')
        )
        for material in bpy.data.materials:
            if material.name == identification \
                    and material.library:
                bpy.context.active_object.material_slots[0].material = material
                return


class FetchLibraryInformation(bpy.types.Operator):
    bl_idname = 'bim.fetch_library_information'
    bl_label = 'Fetch Library Information'

    def execute(self, context):
        # TODO
        return {'FINISHED'}


class FetchObjectPassport(bpy.types.Operator):
    bl_idname = 'bim.fetch_object_passport'
    bl_label = 'Fetch Object Passport'

    def execute(self, context):
        for document in bpy.context.active_object.BIMObjectProperties.documents:
            if not document.file[-6:] == '.opass':
                continue
            with open(os.path.join(bpy.context.scene.BIMProperties.data_dir, 'doc', document.file)) as f:
                self.object_pass = json.load(f)
            if 'blender' in self.object_pass:
                self.fetch_blender()
        return {'FINISHED'}

    def fetch_blender(self):
        identification = self.object_pass['blender']['identification']
        uri = os.path.join(bpy.context.scene.BIMProperties.data_dir,
                           'doc',
                           self.object_pass['blender']['uri'])
        bpy.ops.wm.link(
            filename=identification,
            directory=os.path.join(uri, 'Mesh')
        )
        bpy.context.active_object.data = bpy.data.meshes[identification]


class AddContext(bpy.types.Operator):
    bl_idname = 'bim.add_context'
    bl_label = 'Add Context'

    def execute(self, context):
        context = bpy.context.scene.BIMProperties.contexts.add()
        context.name = bpy.context.scene.BIMProperties.available_contexts
        return {'FINISHED'}


class RemoveContext(bpy.types.Operator):
    bl_idname = 'bim.remove_context'
    bl_label = 'Remove Context'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.contexts.remove(self.index)
        return {'FINISHED'}


class AddSubcontext(bpy.types.Operator):
    bl_idname = 'bim.add_subcontext'
    bl_label = 'Add Subcontext'
    context_index: bpy.props.IntProperty()

    def execute(self, context):
        subcontext = bpy.context.scene.BIMProperties.contexts[self.context_index].subcontexts.add()
        subcontext.name = bpy.context.scene.BIMProperties.available_subcontexts
        subcontext.target_view = bpy.context.scene.BIMProperties.available_target_views
        return {'FINISHED'}


class RemoveSubcontext(bpy.types.Operator):
    bl_idname = 'bim.remove_subcontext'
    bl_label = 'Remove Context'
    indexes: bpy.props.StringProperty()

    def execute(self, context):
        context_index, subcontext_index = self.indexes.split('-')
        context_index = int(context_index)
        subcontext_index = int(subcontext_index)
        bpy.context.scene.BIMProperties.contexts[context_index].subcontexts.remove(subcontext_index)
        return {'FINISHED'}
