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

    def getPsetNames(self, context):
        files = os.listdir(bpy.context.scene.BIMProperties.data_dir + 'pset/')
        return [(f, f, '') for f in files]

    def getPsetFiles(self, context):
        if not bpy.context.scene.BIMProperties.pset_name:
            return []
        files = os.listdir(bpy.context.scene.BIMProperties.data_dir + 'pset/{}/'.format(bpy.context.scene.BIMProperties.pset_name))
        return [(f.replace('.csv', ''), f.replace('.csv', ''), '') for f in files]

    schema_dir: bpy.props.StringProperty(default=cwd + 'schema/', name="Schema Directory")
    data_dir: bpy.props.StringProperty(default=cwd + 'data/', name="Data Directory")
    ifc_class: bpy.props.EnumProperty(items = getIfcClasses, name="Class")
    ifc_predefined_type: bpy.props.EnumProperty(
        items = getIfcPredefinedTypes,
        name="Predefined Type", default=None)
    ifc_userdefined_type: bpy.props.StringProperty(name="Userdefined Type")
    export_has_representations: bpy.props.BoolProperty(name="Export Representations", default=True)
    qa_reject_element_reason: bpy.props.StringProperty(name="Element Rejection Reason")
    pset_name: bpy.props.EnumProperty(items=getPsetNames, name="Pset Name")
    pset_file: bpy.props.EnumProperty(items=getPsetFiles, name="Pset File")
    has_georeferencing: bpy.props.BoolProperty(name="Has Georeferencing", default=False)
    global_id: bpy.props.StringProperty(name="GlobalId")

class MapConversion(bpy.types.PropertyGroup):
    eastings: bpy.props.StringProperty(name="Eastings")
    northings: bpy.props.StringProperty(name="Northings")
    orthogonal_height: bpy.props.StringProperty(name="Orthogonal Height")
    x_axis_abscissa: bpy.props.StringProperty(name="X Axis Abscissa")
    x_axis_ordinate: bpy.props.StringProperty(name="X Axis Ordinate")
    scale: bpy.props.StringProperty(name="Scale")

class TargetCRS(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    description: bpy.props.StringProperty(name="Description")
    geodetic_datum: bpy.props.StringProperty(name="Geodetic Datum")
    vertical_datum: bpy.props.StringProperty(name="Vertical Datum")
    map_projection: bpy.props.StringProperty(name="Map Projection")
    map_zone: bpy.props.StringProperty(name="Map Zone")
    map_unit: bpy.props.StringProperty(name="Map Unit")

class Attribute(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    data_type: bpy.props.StringProperty(name="Data Type")
    string_value: bpy.props.StringProperty(name="Value")
    bool_value: bpy.props.BoolProperty(name="Value")
    int_value: bpy.props.IntProperty(name="Value")
    float_value: bpy.props.FloatProperty(name="Value")

class Pset(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    file: bpy.props.StringProperty(name="File")

class BIMObjectProperties(bpy.types.PropertyGroup):
    def getApplicableAttributes(self, context):
        if '/' in bpy.context.active_object.name \
            and bpy.context.active_object.name.split('/')[0] in ifc_schema.elements:
            return [(a['name'], a['name'], '') for a in
                ifc_schema.elements[bpy.context.active_object.name.split('/')[0]]['attributes']
                if bpy.context.active_object.BIMObjectProperties.attributes.find(a['name']) == -1]
        return []

    attributes: bpy.props.CollectionProperty(name="Attributes", type=Attribute)
    psets: bpy.props.CollectionProperty(name="Psets", type=Pset)
    applicable_attributes: bpy.props.EnumProperty(items=getApplicableAttributes, name="Attribute Names")

class BIMMaterialProperties(bpy.types.PropertyGroup):
    is_external: bpy.props.BoolProperty(name="Has External Definition")
    location: bpy.props.StringProperty(name="Location")
    identification: bpy.props.StringProperty(name="Identification")
    name: bpy.props.StringProperty(name="Name")

class BIMMeshProperties(bpy.types.PropertyGroup):
    is_wireframe: bpy.props.BoolProperty(name="Is Wireframe")
    is_swept_solid: bpy.props.BoolProperty(name="Is Swept Solid")

class ObjectPanel(bpy.types.Panel):
    bl_label = 'IFC Object'
    bl_idname = 'BIM_PT_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        if not bpy.context.active_object:
            return
        layout = self.layout
        layout.label(text="Software Identity:")
        row = layout.row()
        row.operator('bim.generate_global_id')

        layout.label(text="Attributes:")
        row = layout.row(align=True)
        row.prop(bpy.context.active_object.BIMObjectProperties, 'applicable_attributes', text='')
        row.operator('bim.add_attribute')

        for index, attribute in enumerate(bpy.context.active_object.BIMObjectProperties.attributes):
            row = layout.row(align=True)
            row.prop(attribute, 'name', text='')
            row.prop(attribute, 'string_value', text='')
            row.operator('bim.remove_attribute', icon='CANCEL', text='').attribute_index = index

        row = layout.row()
        row.prop(bpy.context.active_object.BIMObjectProperties, 'attributes')

        layout.label(text="Property Sets:")
        row = layout.row()
        row.operator('bim.add_pset')

        for index, pset in enumerate(bpy.context.active_object.BIMObjectProperties.psets):
            row = layout.row(align=True)
            row.prop(pset, 'name', text='')
            row.prop(pset, 'file', text='')
            row.operator('bim.remove_pset', icon='CANCEL', text='').pset_index = index

        row = layout.row()
        row.prop(bpy.context.active_object.BIMObjectProperties, 'psets')

class MeshPanel(bpy.types.Panel):
    bl_label = 'IFC Representations'
    bl_idname = 'BIM_PT_mesh'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    def draw(self, context):
        if not bpy.context.active_object.data:
            return
        layout = self.layout
        row = layout.row()
        row.prop(bpy.context.active_object.data.BIMMeshProperties, 'is_wireframe')
        row = layout.row()
        row.prop(bpy.context.active_object.data.BIMMeshProperties, 'is_swept_solid')
        row = layout.row(align=True)
        row.operator('bim.assign_swept_solid_profile')
        row.operator('bim.assign_swept_solid_extrusion')

class MaterialPanel(bpy.types.Panel):
    bl_label = 'IFC Materials'
    bl_idname = 'BIM_PT_material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        if not bpy.context.active_object.active_material:
            return
        layout = self.layout
        row = layout.row()
        row.prop(bpy.context.active_object.active_material.BIMMaterialProperties, 'is_external')
        row = layout.row(align=True)
        row.prop(bpy.context.active_object.active_material.BIMMaterialProperties, 'location')
        row.operator('bim.select_external_material_dir', icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(bpy.context.active_object.active_material.BIMMaterialProperties, 'identification')
        row = layout.row()
        row.prop(bpy.context.active_object.active_material.BIMMaterialProperties, 'name')

class GISPanel(bpy.types.Panel):
    bl_label = 'IFC Georeferencing'
    bl_idname = "BIM_PT_gis"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.row().prop(bpy.context.scene.BIMProperties, 'has_georeferencing')

        layout.label(text="Map Conversion:")
        layout.row().prop(bpy.context.scene.MapConversion, 'eastings')
        layout.row().prop(bpy.context.scene.MapConversion, 'northings')
        layout.row().prop(bpy.context.scene.MapConversion, 'orthogonal_height')
        layout.row().prop(bpy.context.scene.MapConversion, 'x_axis_abscissa')
        layout.row().prop(bpy.context.scene.MapConversion, 'x_axis_ordinate')
        layout.row().prop(bpy.context.scene.MapConversion, 'scale')

        layout.label(text="Target CRS:")
        layout.row().prop(bpy.context.scene.TargetCRS, 'name')
        layout.row().prop(bpy.context.scene.TargetCRS, 'description')
        layout.row().prop(bpy.context.scene.TargetCRS, 'geodetic_datum')
        layout.row().prop(bpy.context.scene.TargetCRS, 'vertical_datum')
        layout.row().prop(bpy.context.scene.TargetCRS, 'map_projection')
        layout.row().prop(bpy.context.scene.TargetCRS, 'map_zone')
        layout.row().prop(bpy.context.scene.TargetCRS, 'map_unit')

class BIMPanel(bpy.types.Panel):
    bl_label = "Building Information Modeling"
    bl_idname = "BIM_PT_bim"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = bpy.context.scene.BIMProperties

        layout.label(text="System Setup:")

        row = layout.row()
        row.operator('bim.quick_project_setup')

        col = layout.column()
        row = col.row(align=True)
        row.prop(bim_properties, "schema_dir")
        row.operator("bim.select_schema_dir", icon="FILE_FOLDER", text="")

        col = layout.column()
        row = col.row(align=True)
        row.prop(bim_properties, "data_dir")
        row.operator("bim.select_data_dir", icon="FILE_FOLDER", text="")

        layout.label(text="Software Identity:")

        row = layout.row()
        row.prop(bim_properties, 'global_id')
        row = layout.row()
        row.operator('bim.select_global_id')

        layout.label(text="IFC Categorisation:")

        row = layout.row()
        row.prop(bim_properties, "ifc_class")
        row = layout.row()
        row.prop(bim_properties, "ifc_predefined_type")
        row = layout.row()
        row.prop(bim_properties, "ifc_userdefined_type")
        row = layout.row()
        row.operator("bim.assign_class")

        row = layout.row(align=True)
        row.operator("bim.select_class")
        row.operator("bim.select_type")

        layout.label(text="Property Sets:")
        row = layout.row()
        row.prop(bim_properties, "pset_name")
        row = layout.row()
        row.prop(bim_properties, "pset_file")

        row = layout.row(align=True)
        row.operator("bim.assign_pset")
        row.operator("bim.unassign_pset")

        layout.label(text="Quality Auditing:")

        row = layout.row()
        row.prop(bim_properties, "qa_reject_element_reason")
        row = layout.row()
        row.operator("bim.reject_element")

        row = layout.row(align=True)
        row.operator("bim.colour_by_class")
        row.operator("bim.reset_object_colours")

        row = layout.row(align=True)
        row.operator("bim.approve_class")
        row.operator("bim.reject_class")

        row = layout.row()
        row.operator("bim.select_audited")

class MVDPanel(bpy.types.Panel):
    bl_label = "Model View Definitions"
    bl_idname = "BIM_PT_mvd"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        bim_properties = bpy.context.scene.BIMProperties

        layout.label(text="Custom MVD:")

        row = layout.row()
        row.prop(bim_properties, "export_has_representations")
