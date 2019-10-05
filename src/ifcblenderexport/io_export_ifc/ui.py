import bpy
import json
import os

cwd = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class BIMOpAssignClass(bpy.types.Operator):
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

class BIMOpSelectDataDir(bpy.types.Operator):
    bl_idname = "bim.select_data_dir"
    bl_label = "Select Data Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.data_dir = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BIMOpSelectSchemaDir(bpy.types.Operator):
    bl_idname = "bim.select_schema_dir"
    bl_label = "Select Schema Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.schema_dir = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class IfcSchema():
    def __init__(self):
        with open('{}ifc_elements_IFC4.json'.format(cwd + 'schema/')) as f:
            self.elements = json.load(f)

ifc_schema = IfcSchema()

class BIMProperties(bpy.types.PropertyGroup):
    def getIfcClasses(self, context):
        return [(e, e, '') for e in ifc_schema.elements]

    def getIfcPredefinedTypes(self, context):
        results = []
        for name, data in ifc_schema.elements.items():
            if name != bpy.context.scene.BIMProperties.ifc_class:
                continue
            for attribute in data['attributes']:
                if attribute['name'] != 'PredefinedType':
                    continue
                return [(e, e, '') for e in attribute['enum_values']]

    schema_dir: bpy.props.StringProperty(default=cwd + 'schema/', name="Schema Directory")
    data_dir: bpy.props.StringProperty(default=cwd + 'data/', name="Data Directory")
    ifc_class: bpy.props.EnumProperty(items = getIfcClasses, name="Class")
    ifc_predefined_type: bpy.props.EnumProperty(
        items = getIfcPredefinedTypes,
        name="Predefined Type", default=None)
    ifc_userdefined_type: bpy.props.StringProperty(name="Userdefined Type")

class BIMPanel(bpy.types.Panel):
    bl_label = "Building Information Modeling"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        bim_properties = bpy.context.scene.BIMProperties

        layout.label(text="System Setup:")

        col = layout.column()
        row = col.row(align=True)
        row.prop(bim_properties, "schema_dir")
        row.operator("bim.select_schema_dir", icon="FILE_FOLDER", text="")

        col = layout.column()
        row = col.row(align=True)
        row.prop(bim_properties, "data_dir")
        row.operator("bim.select_data_dir", icon="FILE_FOLDER", text="")

        layout.label(text="IFC Categorisation:")

        row = layout.row()
        row.prop(bim_properties, "ifc_class")
        row = layout.row()
        row.prop(bim_properties, "ifc_predefined_type")
        row = layout.row()
        row.prop(bim_properties, "ifc_userdefined_type")
        row = layout.row()
        row.operator("bim.assign_class")
