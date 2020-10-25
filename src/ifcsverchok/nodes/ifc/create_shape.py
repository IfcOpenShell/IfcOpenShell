import bpy
import logging
import ifcopenshell
import ifcsverchok.helper
import blenderbim.bim.import_ifc
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcCreateShapeRefresh(bpy.types.Operator):
    bl_idname = "node.sv_ifc_create_shape_refresh"
    bl_label = "IFC Create Shape Refresh"
    bl_options = {'UNDO'}

    idtree: StringProperty(default='')
    idname: StringProperty(default='')

    def execute(self, context):
        node = bpy.data.node_groups[self.idtree].nodes[self.idname]
        node.process()
        return {'FINISHED'}


class SvIfcCreateShape(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = 'SvIfcCreateShape'
    bl_label = 'IFC Create Shape'
    file: StringProperty(name='file', update=updateNode)
    entity: StringProperty(name='entity', update=updateNode)

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'file').prop_name = 'file'
        self.inputs.new('SvStringsSocket', 'entity').prop_name = 'entity'

    def draw_buttons(self, context, layout):
        self.wrapper_tracked_ui_draw_op(layout, 'node.sv_ifc_create_shape_refresh', icon='FILE_REFRESH', text='Refresh')

    def process(self):
        self.sv_input_names = ['file', 'entity']
        super().process()

    def process_ifc(self, file, entity):
        try:
            if not entity.is_a('IfcProduct'):
                return
            logger = logging.getLogger('ImportIFC')
            self.ifc_import_settings = blenderbim.bim.import_ifc.IfcImportSettings.factory(bpy.context, '', logger)
            settings = ifcopenshell.geom.settings()
            shape = ifcopenshell.geom.create_shape(settings, entity)
            ifc_importer = blenderbim.bim.import_ifc.IfcImporter(self.ifc_import_settings)
            ifc_importer.file = file
            mesh = ifc_importer.create_mesh(entity, shape)
            obj = bpy.data.objects.new('IFC Element', mesh)
            bpy.context.scene.collection.objects.link(obj)
        except:
            print('Entity could not be converted into a shape', entity)


def register():
    bpy.utils.register_class(SvIfcCreateShapeRefresh)
    bpy.utils.register_class(SvIfcCreateShape)

def unregister():
    bpy.utils.unregister_class(SvIfcCreateShape)
    bpy.utils.unregister_class(SvIfcCreateShapeRefresh)
