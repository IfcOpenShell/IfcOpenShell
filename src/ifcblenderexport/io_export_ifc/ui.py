import bpy
import json
import os

cwd = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

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
