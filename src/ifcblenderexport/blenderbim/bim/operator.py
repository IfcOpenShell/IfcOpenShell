import os
import bpy
import time
import json
import logging
import webbrowser
import ifcopenshell
import tempfile
from . import export_ifc
from . import import_ifc
from . import cut_ifc
from . import svgwriter
from . import sheeter
from . import schema
from . import bcf
from . import ifc
from . import annotation
from bpy_extras.io_utils import ImportHelper
from itertools import cycle
from mathutils import Vector, Matrix, Euler
from math import radians, atan, tan, cos, sin, atan2
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
    bl_idname = "bim.export_ifc"
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
        elif extension == 'ifcjson':
            output_file = bpy.path.ensure_ext(self.filepath, '.ifcjson')
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
    bl_idname = "bim.import_ifc"
    bl_label = "Import IFC"
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={'HIDDEN'})

    def execute(self, context):
        start = time.time()
        logger = logging.getLogger('ImportIFC')
        logging.basicConfig(
            filename=bpy.context.scene.BIMProperties.data_dir + 'process.log',
            filemode='a', level=logging.DEBUG)
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, self.filepath, logger)
        ifc_import_settings.logger.info('Starting import')
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
            pset_index = object.BIMObjectProperties.psets.find(search_pset_name)
            if pset_index == -1:
                continue
            prop_index = object.BIMObjectProperties.psets[pset_index].properties.find(search_prop_name)
            if prop_index == -1:
                continue
            value = object.BIMObjectProperties.psets[pset_index].properties[prop_index].string_value
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
            pset_index = obj.BIMObjectProperties.psets.find(search_pset_name)
            if pset_index == -1:
                continue
            prop_index = obj.BIMObjectProperties.psets[pset_index].properties.find(search_prop_name)
            if prop_index == -1:
                continue
            value = obj.BIMObjectProperties.psets[pset_index].properties[prop_index].string_value
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

        gp = bpy.data.grease_pencils.get('BCF')
        if gp:
            bpy.data.grease_pencils.remove(gp)
        if viewpoint.lines:
            self.draw_lines(viewpoint)

        self.delete_clipping_planes()
        if viewpoint.clippingPlanes:
            self.create_clipping_planes(viewpoint)

        self.delete_bitmaps()
        if viewpoint.bitmaps:
            self.create_bitmaps(viewpoint)

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

    def draw_lines(self, viewpoint):
        gp = bpy.data.grease_pencils.new('BCF')
        scene = bpy.context.scene
        scene.grease_pencil = gp
        scene.frame_set(1)
        layer = gp.layers.new('BCF Annotation', set_active=True)
        layer.thickness = 3
        layer.color = (1, 0, 0)
        frame = layer.frames.new(1)
        stroke = frame.strokes.new()
        stroke.display_mode = '3DSPACE'
        stroke.points.add(len(viewpoint.lines)*2)
        coords = []
        for l in viewpoint.lines:
            coords.extend([l.start.x, l.start.y, l.start.z, l.end.x, l.end.y, l.end.z])
        stroke.points.foreach_set('co', coords)

    def create_clipping_planes(self, viewpoint):
        n = 0
        for plane in viewpoint.clippingPlanes:
            bpy.ops.bim.add_section_plane()
            if n == 0:
                obj = bpy.data.objects['Section']
            else:
                obj = bpy.data.objects['Section.{:03d}'.format(n)]
            obj.location = (plane.location.x, plane.location.y, plane.location.z)
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = Vector(
                    (plane.direction.x, plane.direction.y, plane.direction.z)
                ).to_track_quat('Z', 'Y')
            n += 1

    def delete_clipping_planes(self):
        collection = bpy.data.collections.get('Sections')
        if not collection:
            return
        for section in collection.objects:
            bpy.context.view_layer.objects.active = section
            bpy.ops.bim.remove_section_plane()

    def delete_bitmaps(self):
        collection = bpy.data.collections.get('Bitmaps')
        if not collection:
            collection = bpy.data.collections.new('Bitmaps')
            bpy.context.scene.collection.children.link(collection)
        for bitmap in collection.objects:
            bpy.data.objects.remove(bitmap)

    def create_bitmaps(self, viewpoint):
        import bcfplugin
        topics = bcf.BcfStore.topics
        topic = topics[bpy.context.scene.BCFProperties.active_topic_index][1]
        collection = bpy.data.collections.get('Bitmaps')
        if not collection:
            collection = bpy.data.collections.new('Bitmaps')
        for bitmap in viewpoint.bitmaps:
            obj = bpy.data.objects.new('Bitmap', None)
            obj.empty_display_type = 'IMAGE'
            image = bpy.data.images.load(os.path.join(
                bcfplugin.util.getBcfDir(),
                str(topic.xmlId),
                bitmap.reference
            ))
            src_width = image.size[0]
            src_height = image.size[1]
            if src_height > src_width:
                obj.empty_display_size = bitmap.height
            else:
                obj.empty_display_size = bitmap.height * (src_width / src_height)
            obj.data = image
            y = Vector((bitmap.upVector.x, bitmap.upVector.y, bitmap.upVector.z))
            z = Vector((bitmap.normal.x, bitmap.normal.y, bitmap.normal.z))
            x = y.cross(z)
            obj.matrix_world = Matrix([
                [x[0], y[0], z[0], 0],
                [x[1], y[1], z[1], 0],
                [x[2], y[2], z[2], 0],
                [0, 0, 0, 1]
            ])
            obj.location = (bitmap.location.x, bitmap.location.y, bitmap.location.z)
            collection.objects.link(obj)

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


class AddPset(bpy.types.Operator):
    bl_idname = 'bim.add_pset'
    bl_label = 'Add Pset'

    def execute(self, context):
        pset_name = bpy.context.active_object.BIMObjectProperties.pset_name
        if pset_name not in schema.ifc.psets:
            return {'FINISHED'}
        pset = bpy.context.active_object.BIMObjectProperties.psets.add()
        pset.name = pset_name
        for prop_name in schema.ifc.psets[pset_name]['HasPropertyTemplates'].keys():
            prop = pset.properties.add()
            prop.name = prop_name
        return {'FINISHED'}


class RemovePset(bpy.types.Operator):
    bl_idname = 'bim.remove_pset'
    bl_label = 'Remove Pset'
    pset_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.psets.remove(self.pset_index)
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


class AddDocumentInformation(bpy.types.Operator):
    bl_idname = 'bim.add_document_information'
    bl_label = 'Add Document Information'

    def execute(self, context):
        info = bpy.context.scene.BIMProperties.document_information.add()
        info.name = 'New Document ID'
        return {'FINISHED'}


class RemoveDocumentInformation(bpy.types.Operator):
    bl_idname = 'bim.remove_document_information'
    bl_label = 'Remove Document Information'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.document_information.remove(self.index)
        return {'FINISHED'}


class AssignDocumentInformation(bpy.types.Operator):
    bl_idname = 'bim.assign_document_information'
    bl_label = 'Assign Document Information'
    index: bpy.props.IntProperty()

    def execute(self, context):
        reference = bpy.context.scene.BIMProperties.document_references[self.index]
        index = bpy.context.scene.BIMProperties.active_document_information_index
        info = bpy.context.scene.BIMProperties.document_information
        if index < len(info):
            reference.referenced_document = info[index].name
        return {'FINISHED'}


class AddDocumentReference(bpy.types.Operator):
    bl_idname = 'bim.add_document_reference'
    bl_label = 'Add Document Reference'

    def execute(self, context):
        document = bpy.context.scene.BIMProperties.document_references.add()
        document.name = 'New Document Reference ID'
        return {'FINISHED'}


class RemoveDocumentReference(bpy.types.Operator):
    bl_idname = 'bim.remove_document_reference'
    bl_label = 'Remove Document Reference'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.document_references.remove(self.index)
        return {'FINISHED'}


class RemoveObjectDocumentReference(bpy.types.Operator):
    bl_idname = 'bim.remove_object_document_reference'
    bl_label = 'Remove Object Document Reference'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.document_references.remove(self.index)
        return {'FINISHED'}


class AssignDocumentReference(bpy.types.Operator):
    bl_idname = 'bim.assign_document_reference'
    bl_label = 'Assign Document Reference'

    def execute(self, context):
        identification = bpy.context.scene.BIMProperties.document_references[bpy.context.scene.BIMProperties.active_document_reference_index].name
        for obj in bpy.context.selected_objects:
            if obj.BIMObjectProperties.document_references.get(identification):
                continue
            reference = obj.BIMObjectProperties.document_references.add()
            reference.name = identification
        return {'FINISHED'}


class UnassignDocumentReference(bpy.types.Operator):
    bl_idname = 'bim.unassign_document_reference'
    bl_label = 'Unassign Document Reference'

    def execute(self, context):
        identification = bpy.context.scene.BIMProperties.document_references[bpy.context.scene.BIMProperties.active_document_reference_index].name
        for obj in bpy.context.selected_objects:
            index = obj.BIMObjectProperties.document_references.find(identification)
            if index >= 0:
                obj.BIMObjectProperties.document_references.remove(index)
        return {'FINISHED'}


class RemoveObjectDocumentReference(bpy.types.Operator):
    bl_idname = 'bim.remove_object_document_reference'
    bl_label = 'Remove Object Document Reference'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.document_references.remove(self.index)
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
    filename_ext = '.json'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.json')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import ifcdiff
        ifc_diff = ifcdiff.IfcDiff(
            bpy.context.scene.BIMProperties.diff_old_file,
            bpy.context.scene.BIMProperties.diff_new_file,
            self.filepath,
            bpy.context.scene.BIMProperties.diff_relationships.split()
        )
        ifc_diff.diff()
        ifc_diff.export()
        bpy.context.scene.BIMProperties.diff_json_file = self.filepath
        return {'FINISHED'}


class ExportClashSets(bpy.types.Operator):
    bl_idname = 'bim.export_clash_sets'
    bl_label = 'Export Clash Sets'
    filename_ext = '.json'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.json')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.filepath = bpy.path.ensure_ext(self.filepath, '.json')
        clash_sets = []
        for clash_set in bpy.context.scene.BIMProperties.clash_sets:
            self.a = []
            self.b = []
            for ab in ['a', 'b']:
                for data in getattr(clash_set, ab):
                    clash_source = { 'file': data.name }
                    if data.selector:
                        clash_source['selector'] = data.selector
                        clash_source['mode'] = data.mode
                    getattr(self, ab).append(clash_source)
            clash_sets.append({
                'name': clash_set.name,
                'tolerance': clash_set.tolerance,
                'a': self.a,
                'b': self.b
                })
        with open(self.filepath, 'w') as destination:
            destination.write(json.dumps(clash_sets, indent=4))
        return {'FINISHED'}


class ImportClashSets(bpy.types.Operator):
    bl_idname = 'bim.import_clash_sets'
    bl_label = 'Import Clash Sets'
    filename_ext = '.json'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.json')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        with open(self.filepath) as f:
            clash_sets = json.load(f)
        for clash_set in clash_sets:
            new = bpy.context.scene.BIMProperties.clash_sets.add()
            new.name = clash_set['name']
            new.tolerance = clash_set['tolerance']
            for clash_source in clash_set['a']:
                new_source = new.a.add()
                new_source.name = clash_source['file']
                if 'selector' in clash_source:
                    new_source.selector = clash_source['selector']
                    new_source.mode = clash_source['mode']
            if clash_set['b']:
                for clash_source in clash_set['b']:
                    new_source = new.b.add()
                    new_source.name = clash_source['file']
                    if 'selector' in clash_source:
                        new_source.selector = clash_source['selector']
                        new_source.mode = clash_source['mode']
        return {'FINISHED'}


class AddClashSet(bpy.types.Operator):
    bl_idname = 'bim.add_clash_set'
    bl_label = 'Add Clash Set'

    def execute(self, context):
        new = bpy.context.scene.BIMProperties.clash_sets.add()
        new.name = 'New Clash Set'
        new.tolerance = 0.01
        return {'FINISHED'}


class RemoveClashSet(bpy.types.Operator):
    bl_idname = 'bim.remove_clash_set'
    bl_label = 'Remove Clash Set'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.clash_sets.remove(self.index)
        return {'FINISHED'}


class AddClashSource(bpy.types.Operator):
    bl_idname = 'bim.add_clash_source'
    bl_label = 'Add Clash Source'
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = bpy.context.scene.BIMProperties.clash_sets[bpy.context.scene.BIMProperties.active_clash_set_index]
        source = getattr(clash_set, self.group).add()
        return {'FINISHED'}


class RemoveClashSource(bpy.types.Operator):
    bl_idname = 'bim.remove_clash_source'
    bl_label = 'Remove Clash Source'
    index: bpy.props.IntProperty()
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = bpy.context.scene.BIMProperties.clash_sets[bpy.context.scene.BIMProperties.active_clash_set_index]
        getattr(clash_set, self.group).remove(self.index)
        return {'FINISHED'}


class SelectClashSource(bpy.types.Operator):
    bl_idname = "bim.select_clash_source"
    bl_label = "Select Clash Source"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    index: bpy.props.IntProperty()
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = bpy.context.scene.BIMProperties.clash_sets[bpy.context.scene.BIMProperties.active_clash_set_index]
        getattr(clash_set, self.group)[self.index].name = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ExecuteIfcClash(bpy.types.Operator):
    bl_idname = 'bim.execute_ifc_clash'
    bl_label = 'Execute IFC Clash'
    filename_ext = '.json'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.json')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import ifcclash
        settings = ifcclash.IfcClashSettings()
        self.filepath = bpy.path.ensure_ext(self.filepath, '.json')
        settings.output = self.filepath
        settings.logger = logging.getLogger('Clash')
        settings.logger.setLevel(logging.DEBUG)
        ifc_clasher = ifcclash.IfcClasher(settings)
        ifc_clasher.clash_sets = []
        for clash_set in bpy.context.scene.BIMProperties.clash_sets:
            self.a = []
            self.b = []
            for ab in ['a', 'b']:
                for data in getattr(clash_set, ab):
                    clash_source = { 'file': data.name }
                    if data.selector:
                        clash_source['selector'] = data.selector
                        clash_source['mode'] = data.mode
                    getattr(self, ab).append(clash_source)
            ifc_clasher.clash_sets.append({
                'name': clash_set.name,
                'tolerance': clash_set.tolerance,
                'a': self.a,
                'b': self.b
                })
        ifc_clasher.clash()
        ifc_clasher.export()
        return {'FINISHED'}


class SelectIfcClashResults(bpy.types.Operator):
    bl_idname = 'bim.select_ifc_clash_results'
    bl_label = 'Select IFC Clash Results'
    filename_ext = '.json'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.json')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.filepath = bpy.path.ensure_ext(self.filepath, '.json')
        with open(self.filepath) as f:
            clash_sets = json.load(f)
        clash_set_name = bpy.context.scene.BIMProperties.clash_sets[
            bpy.context.scene.BIMProperties.active_clash_set_index].name
        global_ids = []
        for clash_set in clash_sets:
            if clash_set['name'] != clash_set_name:
                continue
            for clash in clash_set['clashes'].values():
                global_ids.extend([clash['a_global_id'], clash['b_global_id']])
        for obj in bpy.context.visible_objects:
            global_id = obj.BIMObjectProperties.attributes.get('GlobalId')
            if global_id and global_id.string_value in global_ids:
                obj.select_set(True)
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
        ifcopenshell.validate.validate(ifc.IfcStore.get_file(), logger)
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


class LoadClassification(bpy.types.Operator):
    bl_idname = 'bim.load_classification'
    bl_label = 'Load Classification'

    def execute(self, context):
        from . import prop
        prop.ClassificationView.raw_data = schema.ifc.load_classification(
            context.scene.BIMProperties.classification)
        context.scene.BIMProperties.classification_references.root = ''
        return {'FINISHED'}


class AddClassification(bpy.types.Operator):
    bl_idname = 'bim.add_classification'
    bl_label = 'Add Classification'

    def execute(self, context):
        if context.scene.BIMProperties.classification not in schema.ifc.classifications:
            return {'FINISHED'}
        data = schema.ifc.classifications[context.scene.BIMProperties.classification]
        classification = context.scene.BIMProperties.classifications.add()
        data_map = {
            'name': 'Name', 'source': 'Source',
            'edition': 'Edition', 'edition_date': 'EditionDate',
            'description': 'Description', 'location': 'Location',
            'reference_tokens': 'ReferenceTokens'
        }
        for key, value in data_map.items():
            if getattr(data, value):
                setattr(classification, key, str(getattr(data, value)))
        classification.filename = context.scene.BIMProperties.classification
        return {'FINISHED'}


class RemoveClassification(bpy.types.Operator):
    bl_idname = 'bim.remove_classification'
    bl_label = 'Remove Classification'
    classification_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.classifications.remove(self.classification_index)
        return {'FINISHED'}


class AssignClassification(bpy.types.Operator):
    bl_idname = 'bim.assign_classification'
    bl_label = 'Assign Classification'

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            classification = obj.BIMObjectProperties.classifications.add()
            refs = bpy.context.scene.BIMProperties.classification_references
            data = refs.root['children'][refs.children[refs.active_index].name]
            if data['identification']:
                classification.name = data['identification']
            if data['name']:
                classification.human_name = data['name']
            for key in ['location', 'description']:
                if data[key]:
                    setattr(classification, key, data[key])
            classification.referenced_source = bpy.context.scene.BIMProperties.classification
        return {'FINISHED'}


class UnassignClassification(bpy.types.Operator):
    bl_idname = 'bim.unassign_classification'
    bl_label = 'Unassign Classification'

    def execute(self, context):
        refs = bpy.context.scene.BIMProperties.classification_references
        key = refs.children[refs.active_index].name
        for obj in bpy.context.selected_objects:
            index = obj.BIMObjectProperties.classifications.find(key)
            if index != -1:
                obj.BIMObjectProperties.classifications.remove(index)

            obj.BIMObjectProperties.classification = ''
        return {'FINISHED'}


class RemoveClassificationReference(bpy.types.Operator):
    bl_idname = 'bim.remove_classification_reference'
    bl_label = 'Remove Classification Reference'
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
        view_collection = bpy.data.collections.new('IfcGroup/' + bpy.context.scene.DocProperties.view_name)
        views_collection.children.link(view_collection)
        camera = bpy.data.objects.new('IfcGroup/' + bpy.context.scene.DocProperties.view_name,
                bpy.data.cameras.new(bpy.context.scene.DocProperties.view_name))
        camera.data.type = 'ORTHO'
        camera.data.BIMCameraProperties.diagram_scale = '1:100'
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
        self.diagram_name = camera.name.split('/')[1]
        bpy.context.scene.render.filepath = os.path.join(
            bpy.context.scene.BIMProperties.data_dir,
            'diagrams',
            '{}.png'.format(self.diagram_name)
        )
        if bpy.context.scene.DocProperties.should_render:
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
        import ifccsv
        ifc_cutter.ifc_attribute_extractor = ifccsv.IfcAttributeExtractor
        ifc_cutter.ifc_filenames = [i.name for i in bpy.context.scene.DocProperties.ifc_files]
        ifc_cutter.data_dir = bpy.context.scene.BIMProperties.data_dir
        ifc_cutter.diagram_name = self.diagram_name
        ifc_cutter.background_image = bpy.context.scene.render.filepath
        ifc_cutter.leader_obj = None
        ifc_cutter.stair_obj = None
        ifc_cutter.dimension_obj = None
        ifc_cutter.break_obj = None
        ifc_cutter.equal_obj = None
        ifc_cutter.hidden_objs = []
        ifc_cutter.solid_objs = []
        ifc_cutter.plan_level_obj = None
        ifc_cutter.section_level_obj = None
        ifc_cutter.grid_objs = []
        ifc_cutter.text_objs = []
        for obj in camera.users_collection[0].objects:
            if 'Leader' in obj.name:
                ifc_cutter.leader_obj = (obj, obj.data)
            elif 'Stair' in obj.name:
                ifc_cutter.stair_obj = obj
            elif 'Equal' in obj.name:
                ifc_cutter.equal_obj = obj
            elif 'Dimension' in obj.name:
                ifc_cutter.dimension_obj = obj
            elif 'Break' in obj.name:
                ifc_cutter.break_obj = obj
            elif 'Hidden' in obj.name:
                ifc_cutter.hidden_objs.append((obj, obj.data))
            elif 'Solid' in obj.name:
                ifc_cutter.solid_objs.append((obj, obj.data))
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

        for obj in bpy.context.visible_objects:
            for subcontext in  obj.BIMObjectProperties.representation_contexts:
                if subcontext.context == 'Plan' \
                        and subcontext.name == 'Annotation' \
                        and subcontext.target_view == 'PLAN_VIEW' \
                        and '/' in obj.data.name:
                    data = bpy.data.meshes.get('Plan/Annotation/PLAN_VIEW/{}'.format(obj.data.name.split('/')[-1]))
                    if data:
                        ifc_cutter.solid_objs.append((obj, data))

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
        ifc_cutter.cut_pickle_file = os.path.join(ifc_cutter.data_dir, '{}-cut.pickle'.format(self.diagram_name))
        ifc_cutter.text_pickle_file = os.path.join(ifc_cutter.data_dir, '{}-text.pickle'.format(self.diagram_name))
        ifc_cutter.metadata_pickle_file = os.path.join(ifc_cutter.data_dir, '{}-metadata.pickle'.format(self.diagram_name))
        ifc_cutter.should_recut = bpy.context.scene.DocProperties.should_recut
        ifc_cutter.should_extract = bpy.context.scene.DocProperties.should_extract
        svg_writer = svgwriter.SvgWriter(ifc_cutter)
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
        camera = bpy.data.objects.get('IfcGroup/' + bpy.context.scene.DocProperties.available_views)
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


class SwitchContext(bpy.types.Operator):
    bl_idname = 'bim.switch_context'
    bl_label = 'Switch Context'
    has_target_context: bpy.props.BoolProperty()
    context_name: bpy.props.StringProperty()
    subcontext_name: bpy.props.StringProperty()
    target_view_name: bpy.props.StringProperty()

    # Warning: This is an incredibly experimental operator. It effectively does
    # a mini-import. A better approach will make this obsolete in the future.
    def execute(self, context):
        self.obj = bpy.context.active_object

        if '/' not in self.obj.data.name:
            self.obj.data.name = 'Model/Body/MODEL_VIEW/' + self.obj.data.name

        self.context = bpy.context.scene.BIMProperties.available_contexts
        self.subcontext = bpy.context.scene.BIMProperties.available_subcontexts
        self.target_view = bpy.context.scene.BIMProperties.available_target_views

        if self.has_target_context:
            self.context = self.context_name
            self.subcontext = self.subcontext_name
            self.target_view = self.target_view_name

        mesh = bpy.data.meshes.get('{}/{}/{}/{}'.format(
            self.context, self.subcontext, self.target_view, self.obj.data.name.split('/')[3]))
        if not mesh:
            try:
                global_id = self.obj.BIMObjectProperties.attributes.get('GlobalId').string_value
                mesh = self.pull_mesh_from_ifc(global_id)
            except:
                mesh = bpy.data.meshes.new('{}/{}/{}/{}'.format(
                    self.context, self.subcontext, self.target_view, self.obj.data.name.split('/')[3]))
                representation_context = self.obj.BIMObjectProperties.representation_contexts.add()
                representation_context.context = self.context
                representation_context.name = self.subcontext
                representation_context.target_view = self.target_view

        self.obj.data = mesh
        return {'FINISHED'}

    def pull_mesh_from_ifc(self, global_id):
        self.file = ifc.IfcStore.get_file()
        logger = logging.getLogger('ImportIFC')
        ifc_import_settings = import_ifc.IfcImportSettings.factory(bpy.context, ifc.IfcStore.path, logger)
        element = self.file.by_id(global_id)
        settings = ifcopenshell.geom.settings()
        settings.set(settings.INCLUDE_CURVES, True)
        if element.is_a('IfcProduct'):
            representations = element.Representation.Representations
        else:
            representations = element.RepresentationMaps

        for rep in element.Representation.Representations:
            if rep.ContextOfItems.is_a('IfcGeometricRepresentationSubContext') \
                    and rep.ContextOfItems.ContextType == self.context \
                    and rep.ContextOfItems.ContextIdentifier == self.subcontext \
                    and rep.ContextOfItems.TargetView == self.target_view:
                break
            elif rep.ContextOfItems.is_a('IfcGeometricRepresentationContext') \
                    and rep.ContextOfItems.ContextType == self.context \
                    and rep.ContextOfItems.ContextIdentifier == self.subcontext:
                break

        if not element.is_a('IfcProduct'):
            rep = rep.MappedRepresentation

        shape = ifcopenshell.geom.create_shape(settings, rep)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        mesh = ifc_importer.create_mesh(element, shape)
        mesh.name = '{}/{}/{}/{}'.format(
            self.context, self.subcontext, self.target_view, self.obj.data.name.split('/')[3])
        self.obj.data = mesh
        material_creator = import_ifc.MaterialCreator(ifc_import_settings)
        material_creator.create(element, self.obj, mesh)
        return mesh


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


class SetViewPreset2(bpy.types.Operator):
    bl_idname = 'bim.set_view_preset_2'
    bl_label = 'Set View Preset 2'

    def execute(self, context):
        bpy.data.worlds[0].color = (1, 1, 1)
        bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
        bpy.context.scene.display.shading.show_object_outline = True
        bpy.context.scene.display.shading.show_cavity = True
        bpy.context.scene.display.shading.cavity_type = 'BOTH'
        bpy.context.scene.display.shading.curvature_ridge_factor = 1
        bpy.context.scene.display.shading.curvature_valley_factor = 1
        bpy.context.scene.view_settings.view_transform = 'Standard'

        bpy.context.scene.display.shading.light = 'FLAT'
        bpy.context.scene.display.shading.color_type = 'SINGLE'
        bpy.context.scene.display.shading.single_color = (1, 1, 1)
        bpy.context.scene.view_settings.use_curve_mapping = True
        bpy.context.scene.view_settings.curve_mapping.curves[3].points.new(.4, 0) # Increase black contrast
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


class BIM_OT_ChangeClassificationLevel(bpy.types.Operator):
    bl_idname = "bim.change_classification_level"
    bl_label = "Change Classification Level"

    # string representing the id-data (e.g. the scene).
    path_sid: bpy.props.StringProperty()
    # path from the id-data to the classification view object
    path_lst: bpy.props.StringProperty()
    # name of child entity to enter (empty = go up one level)
    path_itm: bpy.props.StringProperty()

    def invoke(self, context, event):
        id_data = eval(self.path_sid)
        lst = id_data.path_resolve(self.path_lst)
        if self.path_itm:
            lst.root = self.path_itm
        else:
            lst.root = ''
        return {'FINISHED'}


class AddPropertySetTemplate(bpy.types.Operator):
    bl_idname = 'bim.add_property_set_template'
    bl_label = 'Add Property Set Template'

    def execute(self, context):
        context.scene.BIMProperties.active_property_set_template.global_id = ''
        context.scene.BIMProperties.active_property_set_template.name = 'New_Pset'
        context.scene.BIMProperties.active_property_set_template.description = ''
        context.scene.BIMProperties.active_property_set_template.template_type = 'PSET_TYPEDRIVENONLY'
        context.scene.BIMProperties.active_property_set_template.applicable_entity = 'IfcTypeObject'
        while len(bpy.context.scene.BIMProperties.property_templates) > 0:
            bpy.context.scene.BIMProperties.property_templates.remove(0)
        return {'FINISHED'}


class RemovePropertySetTemplate(bpy.types.Operator):
    bl_idname = 'bim.remove_property_set_template'
    bl_label = 'Remove Property Set Template'

    def execute(self, context):
        template = ifc.IfcStore.pset_template_file.by_guid(context.scene.BIMProperties.property_set_templates)
        ifc.IfcStore.pset_template_file.remove(template)
        ifc.IfcStore.pset_template_file.write(ifc.IfcStore.pset_template_path)
        from . import prop
        prop.refreshPropertySetTemplates(self, context)
        return {'FINISHED'}

class EditPropertySetTemplate(bpy.types.Operator):
    bl_idname = 'bim.edit_property_set_template'
    bl_label = 'Edit Property Set Template'

    def execute(self, context):
        template = ifc.IfcStore.pset_template_file.by_guid(context.scene.BIMProperties.property_set_templates)
        context.scene.BIMProperties.active_property_set_template.global_id = template.GlobalId
        context.scene.BIMProperties.active_property_set_template.name = template.Name
        context.scene.BIMProperties.active_property_set_template.description = template.Description
        context.scene.BIMProperties.active_property_set_template.template_type = template.TemplateType
        context.scene.BIMProperties.active_property_set_template.applicable_entity = template.ApplicableEntity

        while len(bpy.context.scene.BIMProperties.property_templates) > 0:
            bpy.context.scene.BIMProperties.property_templates.remove(0)

        if template.HasPropertyTemplates:
            for property_template in template.HasPropertyTemplates:
                if not property_template.is_a('IfcSimplePropertyTemplate'):
                    continue
                new = context.scene.BIMProperties.property_templates.add()
                new.global_id = property_template.GlobalId
                new.name = property_template.Name
                new.description = property_template.Description
                new.primary_measure_type = property_template.PrimaryMeasureType
        return {'FINISHED'}

class SavePropertySetTemplate(bpy.types.Operator):
    bl_idname = 'bim.save_property_set_template'
    bl_label = 'Save Property Set Template'

    def execute(self, context):
        blender_property_set_template = context.scene.BIMProperties.active_property_set_template
        if blender_property_set_template.global_id:
            template = ifc.IfcStore.pset_template_file.by_guid(blender_property_set_template.global_id)
        else:
            template = ifc.IfcStore.pset_template_file.createIfcPropertySetTemplate()
            template.GlobalId = ifcopenshell.guid.new()
        template.Name = blender_property_set_template.name
        template.Description = blender_property_set_template.description
        template.TemplateType = blender_property_set_template.template_type
        template.ApplicableEntity = blender_property_set_template.applicable_entity

        saved_global_ids = []

        for blender_property_template in context.scene.BIMProperties.property_templates:
            if blender_property_template.global_id:
                property_template = ifc.IfcStore.pset_template_file.by_guid(blender_property_template.global_id)
            else:
                property_template = ifc.IfcStore.pset_template_file.createIfcSimplePropertyTemplate()
                property_template.GlobalId = ifcopenshell.guid.new()
                if template.HasPropertyTemplates:
                    has_property_templates = list(template.HasPropertyTemplates)
                else:
                    has_property_templates = []
                has_property_templates.append(property_template)
                template.HasPropertyTemplates = has_property_templates
            property_template.Name = blender_property_template.name
            property_template.Description = blender_property_template.description
            property_template.PrimaryMeasureType = blender_property_template.primary_measure_type
            property_template.TemplateType = 'P_SINGLEVALUE'
            property_template.AccessState = 'READWRITE'
            saved_global_ids.append(property_template.GlobalId)

        for element in template.HasPropertyTemplates:
            if element.GlobalId not in saved_global_ids:
                ifc.IfcStore.pset_template_file.remove(element)

        ifc.IfcStore.pset_template_file.write(ifc.IfcStore.pset_template_path)
        from . import prop
        prop.refreshPropertySetTemplates(self, context)
        return {'FINISHED'}


class AddPropertyTemplate(bpy.types.Operator):
    bl_idname = 'bim.add_property_template'
    bl_label = 'Add Property Template'

    def execute(self, context):
        context.scene.BIMProperties.property_templates.add()
        return {'FINISHED'}


class RemovePropertyTemplate(bpy.types.Operator):
    bl_idname = 'bim.remove_property_template'
    bl_label = 'Remove Property Template'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.property_templates.remove(self.index)
        return {'FINISHED'}


class AddSectionPlane(bpy.types.Operator):
    bl_idname = 'bim.add_section_plane'
    bl_label = 'Add Section Plane'

    def execute(self, context):
        obj = self.create_section_obj()
        if not self.has_section_override_node():
            self.create_section_compare_node()
            self.create_section_override_node(obj)
        else:
            self.append_obj_to_section_override_node(obj)
        self.add_default_material_if_none_exists()
        self.override_materials()
        return {'FINISHED'}

    def create_section_obj(self):
        section = bpy.data.objects.new('Section', None)
        section.empty_display_type = 'SINGLE_ARROW'
        section.empty_display_size = 5
        section.rotation_euler = Euler((radians(180.0), 0.0, 0.0), 'XYZ')
        section.location = bpy.context.scene.cursor.location
        section.show_in_front = True
        collection = bpy.data.collections.get('Sections')
        if not collection:
            collection = bpy.data.collections.new('Sections')
            bpy.context.scene.collection.children.link(collection)
        collection.objects.link(section)
        return section

    def has_section_override_node(self):
        return bpy.data.node_groups.get('Section Override')

    def create_section_compare_node(self):
        group = bpy.data.node_groups.new('Section Compare', type='ShaderNodeTree')
        group_input = group.nodes.new(type='NodeGroupInput')
        group_output = group.nodes.new(type='NodeGroupOutput')
        separate_xyz_a = group.nodes.new(type='ShaderNodeSeparateXYZ')
        separate_xyz_b = group.nodes.new(type='ShaderNodeSeparateXYZ')
        gt_a = group.nodes.new(type='ShaderNodeMath')
        gt_a.operation = 'GREATER_THAN'
        gt_a.inputs[1].default_value = 0
        gt_b = group.nodes.new(type='ShaderNodeMath')
        gt_b.operation = 'GREATER_THAN'
        gt_b.inputs[1].default_value = 0
        add = group.nodes.new(type='ShaderNodeMath')
        compare = group.nodes.new(type='ShaderNodeMath')
        compare.operation = 'COMPARE'
        compare.inputs[1].default_value = 2
        group.links.new(group_input.outputs[''], separate_xyz_a.inputs['Vector'])
        group.links.new(group_input.outputs[''], separate_xyz_b.inputs['Vector'])
        group.links.new(separate_xyz_a.outputs['Z'], gt_a.inputs[0])
        group.links.new(separate_xyz_b.outputs['Z'], gt_b.inputs[0])
        group.links.new(gt_a.outputs['Value'], add.inputs[0])
        group.links.new(gt_b.outputs['Value'], add.inputs[1])
        group.links.new(add.outputs['Value'], compare.inputs[0])
        group.links.new(compare.outputs['Value'], group_output.inputs[''])

    def create_section_override_node(self, obj):
        group = bpy.data.node_groups.new('Section Override', type='ShaderNodeTree')

        group_input = group.nodes.new(type='NodeGroupInput')
        group_output = group.nodes.new(type='NodeGroupOutput')

        backfacing = group.nodes.new(type='ShaderNodeNewGeometry')
        backfacing_mix = group.nodes.new(type='ShaderNodeMixShader')
        emission = group.nodes.new(type='ShaderNodeEmission')
        emission.inputs['Color'].default_value = list(bpy.context.scene.BIMProperties.section_plane_colour) + [1]

        group.links.new(backfacing.outputs['Backfacing'], backfacing_mix.inputs['Fac'])
        group.links.new(group_input.outputs[''], backfacing_mix.inputs[1])
        group.links.new(emission.outputs['Emission'], backfacing_mix.inputs[2])

        transparent = group.nodes.new(type='ShaderNodeBsdfTransparent')
        section_mix = group.nodes.new(type='ShaderNodeMixShader')
        section_mix.name = 'Section Mix'

        group.links.new(transparent.outputs['BSDF'], section_mix.inputs[1])
        group.links.new(backfacing_mix.outputs['Shader'], section_mix.inputs[2])

        group.links.new(section_mix.outputs['Shader'], group_output.inputs[''])

        cut_obj = group.nodes.new(type='ShaderNodeTexCoord')
        cut_obj.object = obj
        section_compare = group.nodes.new(type='ShaderNodeGroup')
        section_compare.node_tree = bpy.data.node_groups.get('Section Compare')
        section_compare.name = 'Last Section Compare'
        value = group.nodes.new(type='ShaderNodeValue')
        value.name = 'Mock Section'
        group.links.new(cut_obj.outputs['Object'], section_compare.inputs[0])
        group.links.new(value.outputs['Value'], section_compare.inputs[1])
        group.links.new(section_compare.outputs['Value'], section_mix.inputs['Fac'])

    def append_obj_to_section_override_node(self, obj):
        group = bpy.data.node_groups.get('Section Override')
        cut_obj = group.nodes.new(type='ShaderNodeTexCoord')
        cut_obj.object = obj
        section_compare = group.nodes.new(type='ShaderNodeGroup')
        section_compare.node_tree = bpy.data.node_groups.get('Section Compare')

        last_compare = group.nodes.get('Last Section Compare')
        last_compare.name = 'Section Compare'
        mock_section = group.nodes.get('Mock Section')
        section_mix = group.nodes.get('Section Mix')

        group.links.new(last_compare.outputs['Value'], section_compare.inputs[0])
        group.links.new(mock_section.outputs['Value'], section_compare.inputs[1])
        group.links.new(cut_obj.outputs['Object'], last_compare.inputs[1])
        group.links.new(section_compare.outputs['Value'], section_mix.inputs['Fac'])

        section_compare.name = 'Last Section Compare'

    def add_default_material_if_none_exists(self):
        material = bpy.data.materials.get('Section Override')
        if not material:
            material = bpy.data.materials.new('Section Override')
            material.use_nodes = True

        if bpy.context.scene.BIMProperties.should_section_selected_objects:
            objects = list(bpy.context.selected_objects)
        else:
            objects = list(bpy.context.visible_objects)

        for obj in objects:
            aggregate = obj.instance_collection
            if aggregate and 'IfcRelAggregates/' in aggregate.name:
                for part in aggregate.objects:
                    objects.append(part)
            if not (obj.data \
                    and hasattr(obj.data, 'materials') \
                    and obj.data.materials \
                    and obj.data.materials[0]):
                if obj.data and hasattr(obj.data, 'materials'):
                    if len(obj.material_slots):
                        obj.material_slots[0].material = material
                    else:
                        obj.data.materials.append(material)

    def override_materials(self):
        override = bpy.data.node_groups.get('Section Override')
        for material in bpy.data.materials:
            material.use_nodes = True
            if material.node_tree.nodes.get('Section Override'):
                continue
            material.blend_method = 'HASHED'
            material.shadow_method = 'HASHED'
            material_output = material.node_tree.nodes['Material Output']
            from_socket = material_output.inputs['Surface'].links[0].from_socket
            section_override = material.node_tree.nodes.new(type='ShaderNodeGroup')
            section_override.name = 'Section Override'
            section_override.node_tree = override
            material.node_tree.links.new(from_socket, section_override.inputs[0])
            material.node_tree.links.new(section_override.outputs[0], material_output.inputs['Surface'])


class RemoveSectionPlane(bpy.types.Operator):
    bl_idname = 'bim.remove_section_plane'
    bl_label = 'Remove Section Plane'

    def execute(self, context):
        name = bpy.context.active_object.name
        section_override = bpy.data.node_groups.get('Section Override')
        if not section_override:
            return {'FINISHED'}
        for node in section_override.nodes:
            if node.type != 'TEX_COORD' or node.object.name != name:
                continue
            section_compare = node.outputs['Object'].links[0].to_node
            # If the tex coord links to section_compare.inputs[1], it is called 'Input_3'
            if node.outputs['Object'].links[0].to_socket.identifier == 'Input_3':
                section_override.links.new(
                    section_compare.inputs[0].links[0].from_socket,
                    section_compare.outputs[0].links[0].to_socket)
            else: # If it links to section_compare.inputs[0]
                if section_compare.inputs[1].links[0].from_node.name == 'Mock Section':
                    # Then it is the very last section. Purge everything.
                    self.purge_all_section_data()
                    return {'FINISHED'}
                section_override.links.new(
                    section_compare.inputs[1].links[0].from_socket,
                    section_compare.outputs[0].links[0].to_socket)
            section_override.nodes.remove(section_compare)
            section_override.nodes.remove(node)

            old_last_compare = section_override.nodes.get('Last Section Compare')
            old_last_compare.name = 'Section Compare'
            section_mix = section_override.nodes.get('Section Mix')
            new_last_compare = section_mix.inputs['Fac'].links[0].from_node
            new_last_compare.name = 'Last Section Compare'
        bpy.ops.object.delete({"selected_objects": [bpy.context.active_object]})
        return {'FINISHED'}

    def purge_all_section_data(self):
        bpy.data.materials.remove(bpy.data.materials.get('Section Override'))
        for material in bpy.data.materials:
            if not material.node_tree:
                continue
            override = material.node_tree.nodes.get('Section Override')
            material.node_tree.links.new(
                override.inputs[0].links[0].from_socket,
                override.outputs[0].links[0].to_socket)
            material.node_tree.nodes.remove(override)
        bpy.data.node_groups.remove(bpy.data.node_groups.get('Section Override'))
        bpy.data.node_groups.remove(bpy.data.node_groups.get('Section Compare'))
        bpy.ops.object.delete({"selected_objects": [bpy.context.active_object]})


class AddCsvAttribute(bpy.types.Operator):
    bl_idname = 'bim.add_csv_attribute'
    bl_label = 'Add CSV Attribute'

    def execute(self, context):
        attribute = bpy.context.scene.BIMProperties.csv_attributes.add()
        return {'FINISHED'}


class RemoveCsvAttribute(bpy.types.Operator):
    bl_idname = 'bim.remove_csv_attribute'
    bl_label = 'Remove CSV Attribute'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.csv_attributes.remove(self.index)
        return {'FINISHED'}


class ExportIfcCsv(bpy.types.Operator):
    bl_idname = 'bim.export_ifccsv'
    bl_label = 'Export IFC to CSV'
    filename_ext = '.csv'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.csv')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import ifccsv
        self.filepath = bpy.path.ensure_ext(self.filepath, '.csv')
        ifc_selector_parser = ifccsv.IfcSelectorParser()
        ifc_selector_parser.ifc = bpy.context.scene.BIMProperties.ifc_file
        ifc_selector_parser.query = bpy.context.scene.BIMProperties.ifc_selector
        ifc_selector_parser.parse()
        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.output = self.filepath
        ifc_csv.attributes = [a.name for a in bpy.context.scene.BIMProperties.csv_attributes]
        ifc_csv.export(ifc_selector_parser.results)
        return {'FINISHED'}


class ImportIfcCsv(bpy.types.Operator):
    bl_idname = 'bim.import_ifccsv'
    bl_label = 'Import CSV to IFC'
    filename_ext = '.csv'
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, '.csv')
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        import ifccsv
        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.output = self.filepath
        ifc_csv.Import(bpy.context.scene.BIMProperties.ifc_file)
        return {'FINISHED'}


class EyedropIfcCsv(bpy.types.Operator):
    bl_idname = 'bim.eyedrop_ifccsv'
    bl_label = 'Query Selected Items'

    def execute(self, context):
        global_ids = []
        for obj in bpy.context.selected_objects:
            if hasattr(obj, 'BIMObjectProperties') \
                    and obj.BIMObjectProperties.attributes.get('GlobalId'):
                global_ids.append('#' + obj.BIMObjectProperties.attributes.get('GlobalId').string_value)
        bpy.context.scene.BIMProperties.ifc_selector = '|'.join(global_ids)
        return {'FINISHED'}


class ReloadIfcFile(bpy.types.Operator):
    bl_idname = 'bim.reload_ifc_file'
    bl_label = 'Reload IFC File'

    def execute(self, context):
        self.diff_ifc()
        self.reimport_ifc(context)
        return {'FINISHED'}

    def diff_ifc(self):
        import ifcdiff
        temp_file = tempfile.NamedTemporaryFile(delete = False)
        temp_file.close()
        ifc_diff = ifcdiff.IfcDiff(
            bpy.context.scene.BIMProperties.ifc_cache,
            bpy.context.scene.BIMProperties.ifc_file,
            temp_file.name
        )
        ifc_diff.diff()
        ifc_diff.export()
        bpy.context.scene.BIMProperties.diff_json_file = temp_file.name

    def reimport_ifc(self, context):
        logger = logging.getLogger('ImportIFC')
        logging.basicConfig(
            filename=bpy.context.scene.BIMProperties.data_dir + 'process.log',
            filemode='a', level=logging.DEBUG)
        ifc_import_settings = import_ifc.IfcImportSettings.factory(
            context, bpy.context.scene.BIMProperties.ifc_file, logger)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.execute()


class SelectSimilarType(bpy.types.Operator):
    bl_idname = 'bim.select_similar_type'
    bl_label = 'Select Similar Type'

    def execute(self, context):
        if context.active_object.BIMObjectProperties.relating_type:
            relating_type = context.active_object.BIMObjectProperties.relating_type
        elif 'Type/' in context.active_object.name:
            relating_type = context.active_object
        else:
            return {'FINISHED'}
        for obj in bpy.context.visible_objects:
            if obj.BIMObjectProperties.relating_type == relating_type:
                obj.select_set(True)
        return {'FINISHED'}


class AddIfcFile(bpy.types.Operator):
    bl_idname = 'bim.add_ifc_file'
    bl_label = 'Add IFC File'

    def execute(self, context):
        pset = bpy.context.scene.DocProperties.ifc_files.add()
        return {'FINISHED'}


class RemoveIfcFile(bpy.types.Operator):
    bl_idname = 'bim.remove_ifc_file'
    bl_label = 'Remove IFC File'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.DocProperties.ifc_files.remove(self.index)
        return {'FINISHED'}


class SelectDocIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_doc_ifc_file"
    bl_label = "Select Documentation IFC File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.DocProperties.ifc_files[self.index].name = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class AddAnnotation(bpy.types.Operator):
    bl_idname = 'bim.add_annotation'
    bl_label = 'Add Annotation'
    obj_name = bpy.props.StringProperty()
    data_type = bpy.props.StringProperty()

    def execute(self, context):
        if not bpy.context.scene.camera:
            return {'FINISHED'}
        if self.data_type == 'text':
            if bpy.context.selected_objects:
                for selected_object in bpy.context.selected_objects:
                    obj = annotation.Annotator.add_text(related_element=selected_object)
            else:
                obj = annotation.Annotator.add_text()
        else:
            obj = annotation.Annotator.get_annotation_obj(self.obj_name, self.data_type)
            obj = annotation.Annotator.add_line_to_annotation(obj)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


class ResizeText(bpy.types.Operator):
    bl_idname = 'bim.resize_text'
    bl_label = 'Resize Text'

    def execute(self, context):
        for obj in bpy.context.scene.camera.users_collection[0].objects:
            if isinstance(obj.data, bpy.types.TextCurve):
                annotation.Annotator.resize_text(obj)
        return {'FINISHED'}


class AddVariable(bpy.types.Operator):
    bl_idname = 'bim.add_variable'
    bl_label = 'Add Variable'

    def execute(self, context):
        bpy.context.active_object.data.BIMTextProperties.variables.add()
        return {'FINISHED'}


class RemoveVariable(bpy.types.Operator):
    bl_idname = 'bim.remove_variable'
    bl_label = 'Remove Variable'
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.data.BIMTextProperties.variables.remove(self.index)
        return {'FINISHED'}


class PropagateTextData(bpy.types.Operator):
    bl_idname = 'bim.propagate_text_data'
    bl_label = 'Propagate Text Data'

    def execute(self, context):
        source = bpy.context.active_object
        for obj in bpy.context.selected_objects:
            if obj == source:
                continue
            obj.data.body = source.data.body
            obj.data.align_x = source.data.align_x
            obj.data.align_y = source.data.align_y
            obj.data.BIMTextProperties.font_size = source.data.BIMTextProperties.font_size
            obj.data.BIMTextProperties.symbol = source.data.BIMTextProperties.symbol
            while len(obj.data.BIMTextProperties.variables) > 0:
                obj.data.BIMTextProperties.variables.remove(0)
            for variable in source.data.BIMTextProperties.variables:
                new_variable = obj.data.BIMTextProperties.variables.add()
                new_variable.name = variable.name
                new_variable.prop_key = variable.prop_key
        return {'FINISHED'}


class PushRepresentation(bpy.types.Operator):
    bl_idname = 'bim.push_representation'
    bl_label = 'Push Representation'

    # Warning: This is an incredibly experimental operator.
    def execute(self, context):
        self.file = ifc.IfcStore.get_file()

        logger = logging.getLogger('ExportIFC')
        output_file = 'tmp.ifc'
        ifc_export_settings = export_ifc.IfcExportSettings.factory(context, output_file, logger)
        ifc_parser = export_ifc.IfcParser(ifc_export_settings)
        ifc_parser.parse([bpy.context.active_object])
        qto_calculator = export_ifc.QtoCalculator()
        self.ifc_exporter = export_ifc.IfcExporter(ifc_export_settings, ifc_parser, qto_calculator)
        self.ifc_exporter.file = ifcopenshell.file(schema=self.file.schema)
        self.ifc_exporter.create_origin()
        self.ifc_exporter.create_rep_context()
        self.ifc_exporter.create_representations()

        self.context, self.subcontext, self.target_view, self.mesh_name = bpy.context.active_object.data.name.split('/')
        rep_context = self.get_geometric_representation_context()

        for key, rep in self.ifc_exporter.ifc_parser.representations.items():
            if key != bpy.context.active_object.data.name:
                continue
            if rep_context:
                self.ifc_exporter.file.add(rep_context)
                rep['ifc'].MappedRepresentation.ContextOfItems = rep_context
            self.push_representation(rep['ifc'])
            break
        self.file.write(bpy.context.scene.BIMProperties.ifc_file[0:-4] + '-patch.ifc')
        return {'FINISHED'}

    def get_geometric_representation_context(self):
        for element in self.file.by_type('IfcGeometricRepresentationSubContext'):
            if self.is_current_context(element):
                return element

    def push_representation(self, new_representation):
        element = self.file.by_guid(bpy.context.active_object.BIMObjectProperties.attributes.get('GlobalId').string_value)
        old_shape = None
        new_shape = self.file.add(new_representation.MappedRepresentation)
        if element.is_a('IfcProduct'):
            representations = element.Representation.Representations
        else:
            representations = [rm.MappedRepresentation for rm in element.RepresentationMaps]
        for representation in representations:
            if self.is_current_context(representation.ContextOfItems):
                old_shape = self.resolve_mapped_representation(representation)
                break
        if old_shape:
            self.swap_old_representation(old_shape, new_shape)
        else:
            self.add_new_representation(element, new_shape)

    def resolve_mapped_representation(self, representation):
        if representation.RepresentationType == 'MappedRepresentation':
            if representation.Items:
                return representation.Items[0].MappingSource.MappedRepresentation
        return representation

    def swap_old_representation(self, old, new):
        inverse_elements = self.file.get_inverse(old)
        for element in inverse_elements:
            for i, attribute in enumerate(element):
                if (isinstance(attribute, list) or isinstance(attribute, tuple)) \
                        and old in attribute:
                    items = list(attribute)
                    for j, item in enumerate(items):
                        if item == old:
                            del items[j]
                    items.append(new)
                    element[i] = items
                elif attribute == old:
                    element[i] = new

    def add_new_representation(self, element, new):
        if element.is_a('IfcProduct'):
            self.add_new_representation_to_product(element, new)
            return

        if element.RepresentationMaps:
            representation_maps = list(element.RepresentationMaps)
            representation_maps.append(self.file.createIfcRepresentationMap(self.ifc_exporter.origin, new))
            element.RepresentationMaps = representation_maps
        else:
            element.RepresentationMaps = (self.file.createIfcRepresentationMap(self.ifc_exporter.origin, new))

        if hasattr(element, 'Types'):
            related_objects = element.Types[0].RelatedObjects
        elif hasattr(element, 'ObjectTypeOf'): # IFC2X3
            related_objects = element.ObjectTypeOf[0].RelatedObjects

        for related_object in related_objects:
            self.add_new_representation_to_product(related_object, new)

    def add_new_representation_to_product(self, element, new):
        representations = list(element.Representation.Representations)
        representations.append(new)
        element.Representation.Representations = representations

    def is_current_context(self, element):
        return element.ContextType == self.context \
            and element.ContextIdentifier == self.subcontext \
            and element.TargetView == self.target_view


class ConvertLocalToGlobal(bpy.types.Operator):
    bl_idname = 'bim.convert_local_to_global'
    bl_label = 'Convert Local To Global'

    def execute(self, context):
        x, y, z = bpy.context.scene.cursor.location

        if bpy.context.scene.MapConversion.scale:
            scale = float(bpy.context.scene.MapConversion.scale)
        else:
            scale = 1.

        rotation = atan2(
            float(bpy.context.scene.MapConversion.x_axis_ordinate),
            float(bpy.context.scene.MapConversion.x_axis_abscissa))
        a = scale * cos(rotation)
        b = scale * sin(rotation)

        eastings = (a * x) - (b * y) + float(bpy.context.scene.MapConversion.eastings)
        northings = (b * x) + (a * y) + float(bpy.context.scene.MapConversion.northings)
        height = z + float(bpy.context.scene.MapConversion.orthogonal_height)

        bpy.context.scene.cursor.location = (eastings, northings, height)
        return {'FINISHED'}
