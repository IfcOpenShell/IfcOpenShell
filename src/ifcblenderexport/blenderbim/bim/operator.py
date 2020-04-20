import os
import bpy
import time
import json
import logging
import webbrowser
import ifcopenshell
from . import export_ifc
from . import import_ifc
from . import cut_ifc
from . import sheeter
from . import schema
from . import bcf
from . import ifc
from bpy_extras.io_utils import ImportHelper
from itertools import cycle
from mathutils import Vector, Matrix
from math import radians, atan, tan
from pathlib import Path

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

class ExportIFC(bpy.types.Operator):
    bl_idname = "export.ifc"
    bl_label = "Export IFC"
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
        logger = logging.getLogger('ExportIFC')
        logging.basicConfig(
                filename=context.scene.BIMProperties.data_dir + 'process.log',
                filemode='a', level=logging.DEBUG)
        extension = self.filepath.split('.')[-1]
        if extension == 'ifczip':
            output_file = bpy.path.ensure_ext(self.filepath, '.ifczip')
        else:
            output_file = bpy.path.ensure_ext(self.filepath, '.ifc')
        ifc_export_settings = export_ifc.IfcExportSettings.factory(context, output_file, logger)
        ifc_parser = export_ifc.IfcParser(ifc_export_settings)
        qto_calculator = export_ifc.QtoCalculator()
        ifc_exporter = export_ifc.IfcExporter(ifc_export_settings, ifc_parser, qto_calculator)
        ifc_export_settings.logger.info('Starting export')
        ifc_exporter.export(context.selected_objects)
        ifc_export_settings.logger.info('Export finished in {:.2f} seconds'.format(time.time() - start))
        return {'FINISHED'}

class ImportIFC(bpy.types.Operator, ImportHelper):
    bl_idname = "import.ifc"
    bl_label = "Import IFC"
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip", options={'HIDDEN'})

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
        ifc_import_settings.should_ignore_building_coordinates = bpy.context.scene.BIMProperties.import_should_ignore_building_coordinates
        ifc_import_settings.should_import_curves = bpy.context.scene.BIMProperties.import_should_import_curves
        ifc_import_settings.should_import_opening_elements = bpy.context.scene.BIMProperties.import_should_import_opening_elements
        ifc_import_settings.should_import_spaces = bpy.context.scene.BIMProperties.import_should_import_spaces
        ifc_import_settings.should_auto_set_workarounds = bpy.context.scene.BIMProperties.import_should_auto_set_workarounds
        ifc_import_settings.should_treat_styled_item_as_material = bpy.context.scene.BIMProperties.import_should_treat_styled_item_as_material
        ifc_import_settings.should_use_cpu_multiprocessing = bpy.context.scene.BIMProperties.import_should_use_cpu_multiprocessing
        ifc_import_settings.should_use_legacy = bpy.context.scene.BIMProperties.import_should_use_legacy
        ifc_import_settings.should_import_aggregates = bpy.context.scene.BIMProperties.import_should_import_aggregates
        ifc_import_settings.should_merge_by_class = bpy.context.scene.BIMProperties.import_should_merge_by_class
        ifc_import_settings.should_merge_by_material = bpy.context.scene.BIMProperties.import_should_merge_by_material
        ifc_import_settings.should_clean_mesh = bpy.context.scene.BIMProperties.import_should_clean_mesh
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.execute()
        ifc_import_settings.logger.info('Import finished in {:.2f} seconds'.format(time.time() - start))
        return {'FINISHED'}

class SelectGlobalId(bpy.types.Operator):
    bl_idname = 'bim.select_global_id'
    bl_label = 'Select GlobalId'

    def execute(self, context):
        for obj in bpy.context.visible_objects:
            index = obj.BIMObjectProperties.attributes.find('GlobalId')
            if index != -1 \
                    and obj.BIMObjectProperties.attributes[index].string_value == bpy.context.scene.BIMProperties.global_id:
                obj.select_set(True)
                break
        return {'FINISHED'}

class SelectAttribute(bpy.types.Operator):
    bl_idname = 'bim.select_attribute'
    bl_label = 'Select Attribute'

    def execute(self, context):
        import re
        search_value = bpy.context.scene.BIMProperties.search_attribute_value
        for object in bpy.context.visible_objects:
            index = object.BIMObjectProperties.attributes.find(bpy.context.scene.BIMProperties.search_attribute_name)
            if index == -1:
                continue
            value = object.BIMObjectProperties.attributes[index].string_value
            if bpy.context.scene.BIMProperties.search_regex \
                    and bpy.context.scene.BIMProperties.search_ignorecase \
                    and re.search(search_value, value, flags=re.IGNORECASE):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_regex \
                    and re.search(search_value, value):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_ignorecase \
                    and value.lower() == search_value.lower():
                object.select_set(True)
            elif value == search_value:
                object.select_set(True)
        return {'FINISHED'}


class SelectPset(bpy.types.Operator):
    bl_idname = 'bim.select_pset'
    bl_label = 'Select Pset'

    def execute(self, context):
        import re
        search_pset_name = bpy.context.scene.BIMProperties.search_pset_name
        search_prop_name = bpy.context.scene.BIMProperties.search_prop_name
        search_value = bpy.context.scene.BIMProperties.search_pset_value
        for object in bpy.context.visible_objects:
            pset_index = object.BIMObjectProperties.override_psets.find(search_pset_name)
            if pset_index == -1:
                continue
            prop_index = object.BIMObjectProperties.override_psets[pset_index].properties.find(search_prop_name)
            if prop_index == -1:
                continue
            value = object.BIMObjectProperties.override_psets[pset_index].properties[prop_index].string_value
            if bpy.context.scene.BIMProperties.search_regex \
                    and bpy.context.scene.BIMProperties.search_ignorecase \
                    and re.search(search_value, value, flags=re.IGNORECASE):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_regex \
                    and re.search(search_value, value):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_ignorecase \
                    and value.lower() == search_value.lower():
                object.select_set(True)
            elif value == search_value:
                object.select_set(True)
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
        colours = cycle(colour_list)
        ifc_classes = {}
        for obj in bpy.context.visible_objects:
            if '/' not in obj.name:
                continue
            ifc_class = obj.name.split('/')[0]
            if ifc_class not in ifc_classes:
                ifc_classes[ifc_class] = next(colours)
            obj.color = ifc_classes[ifc_class]
        return {'FINISHED'}


class ColourByAttribute(bpy.types.Operator):
    bl_idname = 'bim.colour_by_attribute'
    bl_label = 'Colour by Attribute'

    def execute(self, context):
        colours = cycle(colour_list)
        values = {}
        attribute_name = bpy.context.scene.BIMProperties.search_attribute_name
        for obj in bpy.context.visible_objects:
            index = obj.BIMObjectProperties.attributes.find(attribute_name)
            if index == -1:
                continue
            value = obj.BIMObjectProperties.attributes[index].string_value
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        return {'FINISHED'}


class ColourByPset(bpy.types.Operator):
    bl_idname = 'bim.colour_by_pset'
    bl_label = 'Colour by Pset'

    def execute(self, context):
        colours = cycle(colour_list)
        values = {}
        search_pset_name = bpy.context.scene.BIMProperties.search_pset_name
        search_prop_name = bpy.context.scene.BIMProperties.search_prop_name
        for obj in bpy.context.visible_objects:
            pset_index = obj.BIMObjectProperties.override_psets.find(search_pset_name)
            if pset_index == -1:
                continue
            prop_index = obj.BIMObjectProperties.override_psets[pset_index].properties.find(search_prop_name)
            if prop_index == -1:
                continue
            value = obj.BIMObjectProperties.override_psets[pset_index].properties[prop_index].string_value
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        return {'FINISHED'}


class ResetObjectColours(bpy.types.Operator):
    bl_idname = 'bim.reset_object_colours'
    bl_label = 'Reset Colours'

    def execute(self, context):
        for object in bpy.context.selected_objects:
            object.color = (1, 1, 1, 1)
        return {'FINISHED'}


class QAHelper():
    @classmethod
    def append_to_scenario(cls, lines):
        filename = os.path.join(
            bpy.context.scene.BIMProperties.features_dir,
            bpy.context.scene.BIMProperties.features_file + '.feature')
        if os.path.exists(filename+'~'):
            os.remove(filename+'~')
        os.rename(filename, filename+'~')
        with open(filename, 'w') as destination:
            with open(filename+'~', 'r') as source:
                is_in_scenario = False
                for source_line in source:
                    if 'Scenario: 'in source_line \
                            and bpy.context.scene.BIMProperties.scenario == source_line.strip()[len('Scenario: '):]:
                        is_in_scenario = True
                    if is_in_scenario and source_line.strip()[0:4] == 'Then':
                        for line in lines:
                            destination.write((' '*8) + line + '\n')
                        is_in_scenario = False
                    destination.write(source_line)
        os.remove(filename+'~')


class ApproveClass(bpy.types.Operator):
    bl_idname = 'bim.approve_class'
    bl_label = 'Approve Class'

    def execute(self, context):
        lines = []
        for object in bpy.context.selected_objects:
            index = object.BIMObjectProperties.attributes.find('GlobalId')
            if index != -1:
                lines.append('Then the element {} is an {}'.format(
                    object.BIMObjectProperties.attributes[index].string_value,
                    object.name.split('/')[0]))
        QAHelper.append_to_scenario(lines)
        return {'FINISHED'}


class RejectClass(bpy.types.Operator):
    bl_idname = 'bim.reject_class'
    bl_label = 'Reject Class'

    def execute(self, context):
        lines = []
        for object in bpy.context.selected_objects:
            lines.append('Then the element {} is an {}'.format(
                object.BIMObjectProperties.attributes[
                    object.BIMObjectProperties.attributes.find('GlobalId')].string_value,
                bpy.context.scene.BIMProperties.audit_ifc_class))
        QAHelper.append_to_scenario(lines)
        return {'FINISHED'}


class RejectElement(bpy.types.Operator):
    bl_idname = 'bim.reject_element'
    bl_label = 'Reject Element'

    def execute(self, context):
        lines = []
        for object in bpy.context.selected_objects:
            lines.append('Then the element {} should not exist because {}'.format(
                object.BIMObjectProperties.attributes[
                    object.BIMObjectProperties.attributes.find('GlobalId')].string_value,
                bpy.context.scene.BIMProperties.qa_reject_element_reason))
        QAHelper.append_to_scenario(lines)
        return {'FINISHED'}


class GetBcfTopics(bpy.types.Operator):
    bl_idname = 'bim.get_bcf_topics'
    bl_label = 'Get BCF Topics'

    def execute(self, context):
        import bcfplugin
        bcfplugin.openProject(bpy.context.scene.BCFProperties.bcf_file)
        bcf.BcfStore.topics = bcfplugin.getTopics()
        while len(bpy.context.scene.BCFProperties.topics) > 0:
            bpy.context.scene.BCFProperties.topics.remove(0)
        for topic in bcf.BcfStore.topics:
            new = bpy.context.scene.BCFProperties.topics.add()
            new.name = topic[0]
        return {'FINISHED'}


class ViewBcfTopic(bpy.types.Operator):
    bl_idname = 'bim.view_bcf_topic'
    bl_label = 'Get BCF Topic'
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        for index, topic in enumerate(bcf.BcfStore.topics):
            if str(topic[1].xmlId) == self.topic_guid:
                bpy.context.scene.BCFProperties.active_topic_index = index
        return {'FINISHED'}


class ActivateBcfViewpoint(bpy.types.Operator):
    bl_idname = 'bim.activate_bcf_viewpoint'
    bl_label = 'Activate BCF Viewpoint'

    def execute(self, context):
        import bcfplugin

        topics = bcf.BcfStore.topics
        if not topics:
            return {'FINISHED'}
        topic = topics[bpy.context.scene.BCFProperties.active_topic_index][1]
        viewpoints = bcf.BcfStore.viewpoints
        if not viewpoints:
            return {'FINISHED'}
        viewpoint_reference = viewpoints[int(bpy.context.scene.BCFProperties.viewpoints)][1]
        viewpoint = viewpoint_reference.viewpoint

        obj = bpy.data.objects.get('Viewpoint')
        if not obj:
            obj = bpy.data.objects.new('Viewpoint', bpy.data.cameras.new('Viewpoint'))
            bpy.context.scene.collection.objects.link(obj)
            bpy.context.scene.camera = obj

        cam_width = bpy.context.scene.render.resolution_x
        cam_height = bpy.context.scene.render.resolution_y
        cam_aspect = cam_width / cam_height

        if viewpoint_reference.snapshot:
            obj.data.show_background_images = True
            while len(obj.data.background_images) > 0:
                obj.data.background_images.remove(obj.data.background_images[0])
            background = obj.data.background_images.new()
            background.image = bpy.data.images.load(os.path.join(
                bcfplugin.util.getBcfDir(),
                str(topic.xmlId),
                viewpoint_reference.snapshot.uri
            ))
            src_width = background.image.size[0]
            src_height = background.image.size[1]
            src_aspect = src_width / src_height

            if src_aspect > cam_aspect:
                background.frame_method = 'FIT'
            else:
                background.frame_method = 'CROP'
            background.display_depth = 'FRONT'
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_perspective = 'CAMERA'

        if viewpoint.oCamera:
            camera = viewpoint.oCamera
            obj.data.type = 'ORTHO'
            obj.data.ortho_scale = viewpoint.oCamera.viewWorldScale
        elif viewpoint.pCamera:
            camera = viewpoint.pCamera
            obj.data.type = 'PERSP'
            if cam_aspect >= 1:
                obj.data.angle = radians(camera.fieldOfView)
            else:
                # https://blender.stackexchange.com/questions/23431/how-to-set-camera-horizontal-and-vertical-fov
                obj.data.angle = 2 * atan((0.5 * cam_height) / (0.5 * cam_width / tan(radians(camera.fieldOfView)/2)))

        self.set_viewpoint_components(viewpoint)

        z_axis = Vector((-camera.direction.x, -camera.direction.y, -camera.direction.z)).normalized()
        y_axis = Vector((camera.upVector.x, camera.upVector.y, camera.upVector.z)).normalized()
        x_axis = y_axis.cross(z_axis).normalized()
        rotation = Matrix((x_axis, y_axis, z_axis))
        rotation.invert()
        location = Vector((camera.viewPoint.x, camera.viewPoint.y, camera.viewPoint.z))
        obj.matrix_world = rotation.to_4x4()
        obj.location = location
        return {'FINISHED'}

    def set_viewpoint_components(self, viewpoint):
        selected_global_ids = [s.ifcId for s in viewpoint.components.selection]
        exception_global_ids = [v.ifcId for v in viewpoint.components.visibilityExceptions]
        global_id_colours = {}
        for colouring in viewpoint.components.colouring:
            for component in colouring.components:
                global_id_colours.setdefault(component.ifcId, colouring.colour)

        for obj in bpy.data.objects:
            global_id = obj.BIMObjectProperties.attributes.get('GlobalId')
            if not global_id:
                continue
            global_id = global_id.string_value
            is_visible = viewpoint.components.visibilityDefault
            if global_id in exception_global_ids:
                is_visible = not is_visible
            if not is_visible:
                obj.hide_set(True)
                continue
            if 'IfcSpace' in obj.name:
                is_visible = viewpoint.components.viewSetuphints.spacesVisible
            elif 'IfcOpeningElement' in obj.name:
                is_visible = viewpoint.components.viewSetuphints.openingsVisible
            obj.hide_set(not is_visible)
            if not is_visible:
                continue
            obj.select_set(global_id in selected_global_ids)
            if global_id in global_id_colours:
                obj.color = self.hex_to_rgb(global_id_colours[global_id])

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        t = tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))
        return [t[0]/255., t[1]/255., t[2]/255., 1]

class OpenBcfFileReference(bpy.types.Operator):
    bl_idname = 'bim.open_bcf_file_reference'
    bl_label = 'Open BCF File Reference'
    data: bpy.props.StringProperty()

    def execute(self, context):
        if '/' not in self.data:
            webbrowser.open(bpy.context.scene.BCFProperties.topic_files[int(self.data)].reference)
            return {'FINISHED'}
        import bcfplugin
        topic_guid, index = self.data.split('/')
        path = os.path.join(
            bcfplugin.util.getBcfDir(), topic_guid)
        #   bpy.context.scene.BCFProperties.topic_files[int(index)].reference)
        # TODO - maybe allow immediate importing?
        webbrowser.open(path)
        return {'FINISHED'}


class OpenBcfReferenceLink(bpy.types.Operator):
    bl_idname = 'bim.open_bcf_reference_link'
    bl_label = 'Open BCF Reference Link'
    index: bpy.props.IntProperty()

    def execute(self, context):
        webbrowser.open(bpy.context.scene.BCFProperties.topic_links[self.index].name)
        return {'FINISHED'}


class OpenBcfBimSnippetSchema(bpy.types.Operator):
    bl_idname = 'bim.open_bcf_bim_snippet_schema'
    bl_label = 'Open BCF BIM Snippet Schema'

    def execute(self, context):
        webbrowser.open(bpy.context.scene.BCFProperties.topic_snippet_schema)
        return {'FINISHED'}


class OpenBcfBimSnippetReference(bpy.types.Operator):
    bl_idname = 'bim.open_bcf_bim_snippet_reference'
    bl_label = 'Open BCF BIM Snippet Reference'
    topic_guid: bpy.props.StringProperty()

    def execute(self, context):
        import bcfplugin
        if bpy.context.scene.BCFProperties.topic_snippet_is_external:
            webbrowser.open(bpy.context.scene.BCFProperties.topic_snippet_reference)
            return {'FINISHED'}
        webbrowser.open('file:///' + os.path.join(
            bcfplugin.util.getBcfDir(),
            self.topic_guid,
            bpy.context.scene.BCFProperties.topic_snippet_reference
            ))
        return {'FINISHED'}


class OpenBcfDocumentReference(bpy.types.Operator):
    bl_idname = 'bim.open_bcf_document_reference'
    bl_label = 'Open BCF Document Reference'
    data: bpy.props.StringProperty()

    def execute(self, context):
        import bcfplugin
        topic_guid, index = self.data.split('/')
        doc = bpy.context.scene.BCFProperties.topic_document_references[int(index)]
        uri = doc.name
        if doc.is_external:
            webbrowser.open(uri)
            return {'FINISHED'}
        webbrowser.open('file:///' + os.path.join(
            bcfplugin.util.getBcfDir(),
            topic_guid, uri))
        return {'FINISHED'}


class SelectAudited(bpy.types.Operator):
    bl_idname = 'bim.select_audited'
    bl_label = 'Select Audited'

    def execute(self, context):
        audited_global_ids = []
        for filename in Path(bpy.context.scene.BIMProperties.features_dir).glob('*.feature'):
            with open(filename, 'r') as feature_file:
                lines = feature_file.readlines()
                for line in lines:
                    words = line.strip().split()
                    for word in words:
                        if self.is_a_global_id(word):
                            audited_global_ids.append(word)
        for object in bpy.context.visible_objects:
            index = object.BIMObjectProperties.attributes.find('GlobalId')
            if index != -1 \
                and object.BIMObjectProperties.attributes[index].string_value in audited_global_ids:
                object.select_set(True)
        return {'FINISHED'}

    def is_a_global_id(self, word):
        return word[0] in ['0', '1', '2', '3'] and len(word) == 22

class QuickProjectSetup(bpy.types.Operator):
    bl_idname = 'bim.quick_project_setup'
    bl_label = 'Quick Project Setup'

    def execute(self, context):
        project = bpy.data.collections.new('IfcProject/My Project')
        site = bpy.data.collections.new('IfcSite/My Site')
        building = bpy.data.collections.new('IfcBuilding/My Building')
        building_storey = bpy.data.collections.new('IfcBuildingStorey/Ground Floor')

        project_obj = bpy.data.objects.new('IfcProject/My Project', None)
        site_obj = bpy.data.objects.new('IfcSite/My Site', None)
        building_obj = bpy.data.objects.new('IfcBuilding/My Building', None)
        building_storey_obj = bpy.data.objects.new('IfcBuildingStorey/Ground Floor', None)

        bpy.context.scene.collection.children.link(project)
        project.children.link(site)
        site.children.link(building)
        building.children.link(building_storey)

        project.objects.link(project_obj)
        site.objects.link(site_obj)
        building.objects.link(building_obj)
        building_storey.objects.link(building_storey_obj)
        return {'FINISHED'}

class AssignPset(bpy.types.Operator):
    bl_idname = 'bim.assign_pset'
    bl_label = 'Assign Pset'

    def execute(self, context):
        for object in bpy.context.selected_objects:
            index = object.BIMObjectProperties.psets.find(bpy.context.scene.BIMProperties.pset_name)
            if index >= 0:
                pset = object.BIMObjectProperties.psets[index]
            else:
                pset = object.BIMObjectProperties.psets.add()
            pset.name = bpy.context.scene.BIMProperties.pset_name
            pset.file = bpy.context.scene.BIMProperties.pset_file
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

    def execute(self, context):
        pset = bpy.context.active_object.BIMObjectProperties.psets.add()
        pset.name = bpy.context.scene.BIMProperties.pset_name
        pset.file = bpy.context.scene.BIMProperties.pset_file
        return {'FINISHED'}


class RemovePset(bpy.types.Operator):
    bl_idname = 'bim.remove_pset'
    bl_label = 'Remove Pset'
    pset_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.psets.remove(self.pset_index)
        return {'FINISHED'}


class AddQto(bpy.types.Operator):
    bl_idname = 'bim.add_qto'
    bl_label = 'Add Qto'

    def execute(self, context):
        name = bpy.context.active_object.BIMObjectProperties.qto_name
        if name not in schema.ifc.qtos:
            return {'FINISHED'}
        qto = bpy.context.active_object.BIMObjectProperties.qtos.add()
        qto.name = name
        for prop_name in schema.ifc.qtos[name]['HasPropertyTemplates'].keys():
            prop = qto.properties.add()
            prop.name = prop_name
        return {'FINISHED'}


class AddOverridePset(bpy.types.Operator):
    bl_idname = 'bim.add_override_pset'
    bl_label = 'Add Override Pset'

    def execute(self, context):
        pset_name = bpy.context.active_object.BIMObjectProperties.override_pset_name
        if pset_name not in schema.ifc.psets:
            return {'FINISHED'}
        pset = bpy.context.active_object.BIMObjectProperties.override_psets.add()
        pset.name = pset_name
        for prop_name in schema.ifc.psets[pset_name]['HasPropertyTemplates'].keys():
            prop = pset.properties.add()
            prop.name = prop_name
        return {'FINISHED'}


class RemoveOverridePset(bpy.types.Operator):
    bl_idname = 'bim.remove_override_pset'
    bl_label = 'Remove Override Pset'
    pset_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.override_psets.remove(self.pset_index)
        return {'FINISHED'}


class RemoveQto(bpy.types.Operator):
    bl_idname = 'bim.remove_qto'
    bl_label = 'Remove Qto'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.qtos.remove(self.index)
        return {'FINISHED'}


class AddMaterialPset(bpy.types.Operator):
    bl_idname = 'bim.add_material_pset'
    bl_label = 'Add Material Pset'

    def execute(self, context):
        pset = bpy.context.active_object.active_material.BIMMaterialProperties.psets.add()
        pset.name = bpy.context.active_object.active_material.BIMMaterialProperties.available_material_psets
        return {'FINISHED'}


class RemoveMaterialPset(bpy.types.Operator):
    bl_idname = 'bim.remove_material_pset'
    bl_label = 'Remove Pset'
    pset_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.active_material.BIMMaterialProperties.psets.remove(self.pset_index)
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


class AddMaterialAttribute(bpy.types.Operator):
    bl_idname = 'bim.add_material_attribute'
    bl_label = 'Add Material Attribute'

    def execute(self, context):
        if bpy.context.active_object.active_material.BIMMaterialProperties.applicable_attributes:
            attribute = bpy.context.active_object.active_material.BIMMaterialProperties.attributes.add()
            attribute.name = bpy.context.active_object.active_material.BIMMaterialProperties.applicable_attributes
        return {'FINISHED'}


class RemoveAttribute(bpy.types.Operator):
    bl_idname = 'bim.remove_attribute'
    bl_label = 'Remove Attribute'
    attribute_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.attributes.remove(self.attribute_index)
        return {'FINISHED'}


class RemoveMaterialAttribute(bpy.types.Operator):
    bl_idname = 'bim.remove_material_attribute'
    bl_label = 'Remove Material Attribute'
    attribute_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.active_material.BIMMaterialProperties.attributes.remove(self.attribute_index)
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


class SelectDiffOldFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_old_file"
    bl_label = "Select Diff Old File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.diff_old_file = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SelectDiffNewFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_new_file"
    bl_label = "Select Diff New File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.diff_new_file = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ExecuteIfcDiff(bpy.types.Operator):
    bl_idname = 'bim.execute_ifc_diff'
    bl_label = 'Execute IFC Diff'

    def execute(self, context):
        import ifcdiff
        ifc_diff = ifcdiff.IfcDiff(
            bpy.context.scene.BIMProperties.diff_old_file,
            bpy.context.scene.BIMProperties.diff_new_file,
            bpy.context.scene.BIMProperties.diff_json_file
        )
        ifc_diff.diff()
        ifc_diff.export()
        return {'FINISHED'}


class SelectBcfFile(bpy.types.Operator):
    bl_idname = "bim.select_bcf_file"
    bl_label = "Select BCF File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BCFProperties.bcf_file = self.filepath
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


class SelectIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_ifc_file"
    bl_label = "Select IFC File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.ifc_file = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ValidateIfcFile(bpy.types.Operator):
    bl_idname = 'bim.validate_ifc_file'
    bl_label = 'Validate IFC File'

    def execute(self, context):
        import ifcopenshell.validate
        logger = logging.getLogger('validate')
        logger.setLevel(logging.DEBUG)
        if bpy.context.scene.BIMProperties.ifc_file \
                and bpy.context.scene.BIMProperties.ifc_file != ifc.IfcStore.path:
            ifc.IfcStore.file = ifcopenshell.open(bpy.context.scene.BIMProperties.ifc_file)
            ifc.IfcStore.path = bpy.context.scene.BIMProperties.ifc_file
        ifcopenshell.validate.validate(ifc.IfcStore.file, logger)
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


class ExplodeAggregate(bpy.types.Operator):
    bl_idname = 'bim.explode_aggregate'
    bl_label = 'Explode Aggregate'

    def execute(self, context):
        obj = bpy.context.active_object
        if obj.instance_type != 'COLLECTION' \
            or 'IfcRelAggregates' not in obj.instance_collection.name:
            return {'FINISHED'}
        aggregate_collection = bpy.data.collections.get(obj.instance_collection.name)
        spatial_collection = obj.users_collection[0]
        for part in aggregate_collection.objects:
            spatial_collection.objects.link(part)
            aggregate_collection.objects.unlink(part)
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(aggregate_collection, do_unlink=True)
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
        if not os.path.isabs(location):
            location = os.path.join(os.path.join(
                bpy.context.scene.BIMProperties.data_dir, location))
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
        uri = self.material_pass[name]['uri']
        if not os.path.isabs(uri):
            uri = os.path.join(os.path.join(
                bpy.context.scene.BIMProperties.data_dir, uri))
        bpy.ops.wm.link(
            filename=identification,
            directory=os.path.join(uri, 'Material')
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


class AddSubcontext(bpy.types.Operator):
    bl_idname = 'bim.add_subcontext'
    bl_label = 'Add Subcontext'
    context: bpy.props.StringProperty()

    def execute(self, context):
        props = bpy.context.scene.BIMProperties
        subcontext = getattr(bpy.context.scene.BIMProperties, '{}_subcontexts'.format(self.context)).add()
        subcontext.name = bpy.context.scene.BIMProperties.available_subcontexts
        subcontext.target_view = bpy.context.scene.BIMProperties.available_target_views
        return {'FINISHED'}


class RemoveSubcontext(bpy.types.Operator):
    bl_idname = 'bim.remove_subcontext'
    bl_label = 'Remove Context'
    indexes: bpy.props.StringProperty()

    def execute(self, context):
        context, subcontext_index = self.indexes.split('-')
        subcontext_index = int(subcontext_index)
        getattr(bpy.context.scene.BIMProperties, '{}_subcontexts'.format(context)).remove(subcontext_index)
        return {'FINISHED'}


class CreateView(bpy.types.Operator):
    bl_idname = 'bim.create_view'
    bl_label = 'Create View'

    def execute(self, context):
        if not bpy.data.collections.get('Views'):
            bpy.context.scene.collection.children.link(bpy.data.collections.new('Views'))
        views_collection = bpy.data.collections.get('Views')
        view_collection = bpy.data.collections.new(bpy.context.scene.DocProperties.view_name)
        views_collection.children.link(view_collection)
        camera = bpy.data.objects.new(bpy.context.scene.DocProperties.view_name, bpy.data.cameras.new(bpy.context.scene.DocProperties.view_name))
        camera.data.type = 'ORTHO'
        bpy.context.scene.camera = camera
        view_collection.objects.link(camera)
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
        return {'FINISHED'}


class OpenView(bpy.types.Operator):
    bl_idname = 'bim.open_view'
    bl_label = 'Open View'

    def execute(self, context):
        webbrowser.open('file:///' + os.path.join(
            bpy.context.scene.BIMProperties.data_dir, 'diagrams',
            bpy.context.scene.DocProperties.available_views + '.svg'))
        return {'FINISHED'}


class CutSection(bpy.types.Operator):
    bl_idname = 'bim.cut_section'
    bl_label = 'Cut Section'

    def execute(self, context):
        camera = bpy.context.scene.camera
        if not (camera.type == 'CAMERA' and camera.data.type == 'ORTHO'):
            return {'FINISHED'}
        self.diagram_name = camera.name
        bpy.context.scene.render.filepath = os.path.join(
            bpy.context.scene.BIMProperties.data_dir,
            'diagrams',
            '{}.png'.format(self.diagram_name)
        )
        bpy.ops.render.render(write_still=True)
        location = camera.location
        render = bpy.context.scene.render
        if self.is_landscape():
            width = camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x
        depth = camera.data.clip_end
        projection = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        x_axis = camera.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        y_axis = camera.matrix_world.to_quaternion() @ Vector((0, -1, 0))
        top_left_corner = location - (width / 2 * x_axis) - (height / 2 * y_axis)
        ifc_cutter = cut_ifc.IfcCutter()
        ifc_cutter.data_dir = bpy.context.scene.BIMProperties.data_dir
        ifc_cutter.diagram_name = self.diagram_name
        ifc_cutter.background_image = bpy.context.scene.render.filepath
        ifc_cutter.leader_obj = None
        ifc_cutter.stair_obj = None
        ifc_cutter.dimension_obj = None
        ifc_cutter.equal_obj = None
        ifc_cutter.hidden_obj = None
        ifc_cutter.plan_level_obj = None
        ifc_cutter.section_level_obj = None
        ifc_cutter.grid_objs = []
        ifc_cutter.text_objs = []
        for obj in camera.users_collection[0].objects:
            if 'Leader' in obj.name:
                ifc_cutter.leader_obj = obj
            elif 'Stair' in obj.name:
                ifc_cutter.stair_obj = obj
            elif 'Equal' in obj.name:
                ifc_cutter.equal_obj = obj
            elif 'Dimension' in obj.name:
                ifc_cutter.dimension_obj = obj
            elif 'Hidden' in obj.name:
                ifc_cutter.hidden_obj = obj
            elif 'IfcGrid' in obj.name:
                ifc_cutter.grid_objs.append(obj)
            elif 'Plan Level' in obj.name:
                ifc_cutter.plan_level_obj = obj
            elif 'Section Level' in obj.name:
                ifc_cutter.section_level_obj = obj
            elif obj.type == 'CAMERA':
                ifc_cutter.camera_obj = obj
            elif obj.type == 'FONT':
                ifc_cutter.text_objs.append(obj)
        ifc_cutter.section_box = {
            'projection': tuple(projection),
            'x_axis': tuple(x_axis),
            'y_axis': tuple(y_axis),
            'top_left_corner': tuple(top_left_corner),
            'x': width,
            'y': height,
            'z': depth,
            'shape': None,
            'face': None
        }
        ifc_cutter.shapes_pickle_file = os.path.join(ifc_cutter.data_dir, 'shapes.pickle')
        ifc_cutter.cut_pickle_file = os.path.join(ifc_cutter.data_dir, '{}-cut.pickle'.format(self.diagram_name))
        ifc_cutter.should_recut = bpy.context.scene.DocProperties.should_recut
        svg_writer = cut_ifc.SvgWriter(ifc_cutter)
        numerator, denominator = camera.data.BIMCameraProperties.diagram_scale.split(':')
        if camera.data.BIMCameraProperties.is_nts:
            svg_writer.human_scale = 'NTS'
        else:
            svg_writer.human_scale = camera.data.BIMCameraProperties.diagram_scale
        svg_writer.scale = float(numerator) / float(denominator)
        ifc_cutter.cut()
        svg_writer.write()
        return {'FINISHED'}

    def is_landscape(self):
        return bpy.context.scene.render.resolution_x > bpy.context.scene.render.resolution_y


class CreateSheet(bpy.types.Operator):
    bl_idname = 'bim.create_sheet'
    bl_label = 'Create Sheet'

    def execute(self, context):
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.create(bpy.context.scene.DocProperties.sheet_name)
        bpy.context.scene.DocProperties.sheet_name = ''
        return {'FINISHED'}


class OpenSheet(bpy.types.Operator):
    bl_idname = 'bim.open_sheet'
    bl_label = 'Open Sheet'

    def execute(self, context):
        webbrowser.open('file:///' + os.path.join(
            bpy.context.scene.BIMProperties.data_dir, 'sheets',
            bpy.context.scene.DocProperties.available_sheets + '.svg'))
        return {'FINISHED'}


class OpenCompiledSheet(bpy.types.Operator):
    bl_idname = 'bim.open_compiled_sheet'
    bl_label = 'Open Compiled Sheet'

    def execute(self, context):
        webbrowser.open('file:///' + os.path.join(
            bpy.context.scene.BIMProperties.data_dir, 'build',
            bpy.context.scene.DocProperties.available_sheets,
            bpy.context.scene.DocProperties.available_sheets + '.svg'))
        return {'FINISHED'}


class AddViewToSheet(bpy.types.Operator):
    bl_idname = 'bim.add_view_to_sheet'
    bl_label = 'Add View To Sheet'

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.add_view(props.available_views, props.available_sheets)
        return {'FINISHED'}


class CreateSheets(bpy.types.Operator):
    bl_idname = 'bim.create_sheets'
    bl_label = 'Create Sheets'

    def execute(self, context):
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.build(bpy.context.scene.DocProperties.available_sheets)
        return {'FINISHED'}


class GenerateDigitalTwin(bpy.types.Operator):
    bl_idname = 'bim.generate_digital_twin'
    bl_label = 'Generate Digital Twin'

    def execute(self, context):
        # Does absolutely nothing at all :D
        return {'FINISHED'}


class ActivateView(bpy.types.Operator):
    bl_idname = 'bim.activate_view'
    bl_label = 'Activate View'

    def execute(self, context):
        camera = bpy.data.objects.get(bpy.context.scene.DocProperties.available_views)
        if not camera:
            return {'FINISHED'}
        bpy.context.scene.camera = camera
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        area.spaces[0].region_3d.view_perspective = 'CAMERA'
        views_collection = bpy.data.collections.get('Views')
        for collection in views_collection.children:
            bpy.context.view_layer.layer_collection.children['Views'].children[collection.name].hide_viewport = True
            bpy.data.collections.get(collection.name).hide_render = True
        bpy.context.view_layer.layer_collection.children['Views'].children[camera.users_collection[0].name].hide_viewport = False
        bpy.data.collections.get(camera.users_collection[0].name).hide_render = False
        return {'FINISHED'}


class AssignContext(bpy.types.Operator):
    bl_idname = 'bim.assign_context'
    bl_label = 'Assign Context'

    def execute(self, context):
        if not self.is_mesh_context_sensitive(bpy.context.active_object.data.name):
            bpy.context.active_object.data.name = '{}/{}/{}/{}'.format(
                bpy.context.scene.BIMProperties.available_contexts,
                bpy.context.scene.BIMProperties.available_subcontexts,
                bpy.context.scene.BIMProperties.available_target_views,
                bpy.context.active_object.data.name
            )
        else:
            bpy.context.active_object.data.name = '{}/{}/{}/{}'.format(
                bpy.context.scene.BIMProperties.available_contexts,
                bpy.context.scene.BIMProperties.available_subcontexts,
                bpy.context.scene.BIMProperties.available_target_views,
                bpy.context.active_object.data.name.split('/')[3]
            )
        return {'FINISHED'}

    def is_mesh_context_sensitive(self, name):
        return '/' in name \
            and ( \
                name[0:6] == 'Model/' \
                or name[0:5] == 'Plan/' \
            )


class SetViewPreset1(bpy.types.Operator):
    bl_idname = 'bim.set_view_preset_1'
    bl_label = 'Set View Preset 1'

    def execute(self, context):
        bpy.data.worlds[0].color = (1, 1, 1)
        bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
        bpy.context.scene.display.shading.show_object_outline = True
        bpy.context.scene.display.shading.show_cavity = True
        bpy.context.scene.display.shading.cavity_type = 'BOTH'
        bpy.context.scene.display.shading.curvature_ridge_factor = 1
        bpy.context.scene.display.shading.curvature_valley_factor = 1
        bpy.context.scene.view_settings.view_transform = 'Standard'
        return {'FINISHED'}


class OpenUpstream(bpy.types.Operator):
    bl_idname = 'bim.open_upstream'
    bl_label = 'Open Upstream Reference'
    page: bpy.props.StringProperty()

    def execute(self, context):
        if self.page == 'home':
            webbrowser.open('https://blenderbim.org/')
        elif self.page == 'docs':
            webbrowser.open('https://blenderbim.org/docs/')
        elif self.page == 'wiki':
            webbrowser.open('https://wiki.osarch.org/')
        elif self.page == 'community':
            webbrowser.open('https://community.osarch.org/')
        return {'FINISHED'}


class BIM_OT_CopyAttributesToSelection(bpy.types.Operator):
    """Copies attributes from the active object towards selected objects"""
    bl_idname = "bim.copy_attributes_to_selection"
    bl_label = "Copy Attributes To Selection"

    prop_base = bpy.props.StringProperty() # data for properties to assign to
    prop_name = bpy.props.StringProperty(description="Property name which to change")
    sub_props = bpy.props.StringProperty() # properties which to copy (commasep). (empty = all)
    collection_element = bpy.props.BoolProperty(
        description="If this is a collection element, copy the complete thing")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        active_object = bpy.context.active_object
        selected_objects = [obj for obj in bpy.context.visible_objects
            if obj.type == active_object.type and obj in bpy.context.selected_objects and obj!=active_object]
        if self.prop_base:
            prop_base = eval('active_object.'+ self.prop_base)
        else:
            prop_base = active_object
        if not self.collection_element:
            self.copy_simple(prop_base, selected_objects)
            return {'FINISHED'}
        self.copy_collection(prop_base, selected_objects)
        return {'FINISHED'}

    def copy_simple(self, prop_base, selected_objects):
        prop = getattr(prop_base, self.prop_name)
        for obj in selected_objects:
            if self.prop_base:
                new_prop_base = eval('obj.' + self.prop_base)
            else:
                new_prop_base = obj
            setattr(new_prop_base, self.prop_name, prop)

    def copy_collection(self, prop_base, selected_objects):
        prop = prop_base[self.prop_name]
        for obj in selected_objects:
            if self.prop_base:
                new_prop_base = eval('obj.' + self.prop_base)
            else:
                new_prop_base = obj

            if self.prop_name in new_prop_base:
                new_prop_base = new_prop_base[self.prop_name]
            else:
                new_prop_base = new_prop_base.add()

            if self.sub_props:
                for p in self.sub_props.replace(' ','').split(','):
                    try:
                        setattr(new_prop_base, p, getattr(prop, p))
                    except: pass
            else:
                for p in dir(prop):
                    try:
                        setattr(new_prop_base, p, getattr(prop, p))
                    except: pass
