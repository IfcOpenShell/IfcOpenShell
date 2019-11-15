import bpy
import json
import os
import csv
from pathlib import Path
from bpy.types import PropertyGroup, Panel
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    CollectionProperty
)


cwd = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class IfcSchema():
    def __init__(self):
        with open('{}schema{}ifc_elements_IFC4.json'.format(cwd, os.path.sep)) as f:
            self.elements = json.load(f)

ifc_schema = IfcSchema()

# hold reference to dynamic enum
classes_enum = []
types_enum = []
psetnames_enum = []
psetfiles_enum = []
classification_enum = []
attributes_enum = []
documents_enum = []

# Note: unless we need dynamic behaviour
# enums should be cached especially when file io is involved
# we may clear on need to regen

def getIfcPredefinedTypes(self):
    global types_enum
    types_enum.clear()
    for name, data in ifc_schema.elements.items():
        if name != bpy.context.scene.BIMProperties.ifc_class:
            continue
        for attribute in data['attributes']:
            if attribute['name'] != 'PredefinedType':
                continue
            types_enum.extend([(e, e, '') for e in attribute['enum_values']])
    return types_enum

def getIfcClasses(self):
    global classes_enum
    classes_enum.clear()
    classes_enum.extend([(e, e, '') for e in ifc_schema.elements])
    return classes_enum

def getPsetNames(self):
    global psetnames_enum
    psetnames_enum.clear()
    files = os.listdir(bpy.context.scene.BIMProperties.data_dir + 'pset' + os.path.sep)
    psetnames_enum.extend([(f, f, '') for f in files])
    return psetnames_enum

def getPsetFiles(self):
    global psetfiles_enum
    psetfiles_enum.clear()
    if not bpy.context.scene.BIMProperties.pset_name:
        return psetfiles_enum
    files = os.listdir(
        bpy.context.scene.BIMProperties.data_dir + 'pset{}{}{}'.format(
            os.path.sep,
            bpy.context.scene.BIMProperties.pset_name,
            os.path.sep))
    psetfiles_enum.extend([(f.replace('.csv', ''), f.replace('.csv', ''), '') for f in files])
    return psetfiles_enum

def getClassifications(self):
    global classification_enum
    classification_enum.clear()
    with open(bpy.context.scene.BIMProperties.data_dir + 'class/classifications.csv', 'r') as f:
        data = list(csv.reader(f))
        keys = data.pop(0)
        index = keys.index('Name')
        classification_enum.extend([(str(i), d[index], '') for i, d in enumerate(data)])
    return classification_enum

def getReferences(self):
    global reference_enum
    reference_enum.clear()
    if not bpy.context.scene.BIMProperties.classification:
        return reference_enum
    with open(bpy.context.scene.BIMProperties.data_dir + 'class' + os.path.sep + 'references.csv', 'r') as f:
        data = list(csv.reader(f))
        keys = data.pop(0)
        reference_enum.extend([(d[0], '{} - {}'.format(d[0], d[1]), '') for d in data if
                d[2] == bpy.context.scene.BIMProperties.classification])
    return reference_enum

def getApplicableAttributes(self):
    global attributes_enum
    attributes_enum.clear()
    if '/' in bpy.context.active_object.name \
        and bpy.context.active_object.name.split('/')[0] in ifc_schema.elements:
        attributes_enum.extend([(a['name'], a['name'], '') for a in
            ifc_schema.elements[bpy.context.active_object.name.split('/')[0]]['attributes']
            if bpy.context.active_object.BIMObjectProperties.attributes.find(a['name']) == -1])
    return attributes_enum

def getApplicableDocuments(self):
    global documents_enum
    documents_enum.clear()
    doc_path = bpy.context.scene.BIMProperties.data_dir + 'doc' + os.path.sep
    for filename in Path(doc_path).glob('**/*'):
        uri = str(filename.relative_to(doc_path).as_posix())
        documents_enum.append((uri, uri, ''))
    return documents_enum


class BIMProperties(PropertyGroup):

    schema_dir: StringProperty(default=cwd + 'schema' + os.path.sep, name="Schema Directory")
    data_dir: StringProperty(default=cwd + 'data'  + os.path.sep, name="Data Directory")
    ifc_class: EnumProperty(items = getIfcClasses, name="Class")
    ifc_predefined_type: EnumProperty(
        items = getIfcPredefinedTypes,
        name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
    export_has_representations: BoolProperty(name="Export Representations", default=True)
    export_should_export_all_materials_as_styled_items: BoolProperty(name="Export All Materials as Styled Items", default=False)
    export_should_use_presentation_style_assignment: BoolProperty(name="Export with Presentation Style Assignment", default=False)
    import_should_ignore_site_coordinates: BoolProperty(name="Import Ignoring Site Coordinates", default=False)
    import_should_import_curves: BoolProperty(name="Import Curves", default=False)
    qa_reject_element_reason: StringProperty(name="Element Rejection Reason")
    pset_name: EnumProperty(items=getPsetNames, name="Pset Name")
    pset_file: EnumProperty(items=getPsetFiles, name="Pset File")
    has_georeferencing: BoolProperty(name="Has Georeferencing", default=False)
    global_id: StringProperty(name="GlobalId")
    features_dir: StringProperty(default='', name="Features Directory")
    diff_json_file: StringProperty(default='', name="Diff JSON File")
    aggregate_class: EnumProperty(items = getIfcClasses, name="Aggregate Class")
    aggregate_name: StringProperty(name="Aggregate Name")
    classification: EnumProperty(items = getClassifications, name="Classification")
    reference: EnumProperty(items = getReferences, name="Reference")

class MapConversion(PropertyGroup):
    eastings: StringProperty(name="Eastings")
    northings: StringProperty(name="Northings")
    orthogonal_height: StringProperty(name="Orthogonal Height")
    x_axis_abscissa: StringProperty(name="X Axis Abscissa")
    x_axis_ordinate: StringProperty(name="X Axis Ordinate")
    scale: StringProperty(name="Scale")

class TargetCRS(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    geodetic_datum: StringProperty(name="Geodetic Datum")
    vertical_datum: StringProperty(name="Vertical Datum")
    map_projection: StringProperty(name="Map Projection")
    map_zone: StringProperty(name="Map Zone")
    map_unit: StringProperty(name="Map Unit")

class Attribute(PropertyGroup):
    name: StringProperty(name="Name")
    data_type: StringProperty(name="Data Type")
    string_value: StringProperty(name="Value")
    bool_value: BoolProperty(name="Value")
    int_value: IntProperty(name="Value")
    float_value: FloatProperty(name="Value")

class Pset(PropertyGroup):
    name: StringProperty(name="Name")
    file: StringProperty(name="File")

class Document(PropertyGroup):
    file: StringProperty(name="File")

class Classification(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")


class GlobalId(PropertyGroup):
    name: StringProperty(name="Name")


class BIMObjectProperties(PropertyGroup):


    global_ids: CollectionProperty(name="GlobalIds", type=GlobalId)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    psets: CollectionProperty(name="Psets", type=Pset)
    applicable_attributes: EnumProperty(items=getApplicableAttributes, name="Attribute Names")
    documents: CollectionProperty(name="Documents", type=Document)
    applicable_documents: EnumProperty(items=getApplicableDocuments, name="Available Documents")
    classifications: CollectionProperty(name="Classifications", type=Classification)


class BIMMaterialProperties(PropertyGroup):
    is_external: BoolProperty(name="Has External Definition")
    location: StringProperty(name="Location")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")


class SweptSolid(PropertyGroup):
    name: StringProperty(name="Name")
    outer_curve: StringProperty(name="Outer Curve")
    inner_curves: StringProperty(name="Inner Curves")
    extrusion: StringProperty(name="Extrusion")


class BIMMeshProperties(PropertyGroup):
    is_wireframe: BoolProperty(name="Is Wireframe")
    is_swept_solid: BoolProperty(name="Is Swept Solid")
    swept_solids: CollectionProperty(name="Swept Solids", type=SweptSolid)


class BIM_PT_object(Panel):
    bl_label = 'IFC Object'
    bl_idname = 'BIM_PT_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and hasattr(context.active_object, "BIMObjectProperties")
    
    def draw(self, context):
        
        if context.active_object is None:
            return
        layout = self.layout
        props = context.active_object.BIMObjectProperties

        layout.label(text="Software Identity:")
        row = layout.row()
        row.operator('bim.generate_global_id')

        layout.label(text="Attributes:")
        row = layout.row(align=True)
        row.prop(props, 'applicable_attributes', text='')
        row.operator('bim.add_attribute')

        for index, attribute in enumerate(props.attributes):
            row = layout.row(align=True)
            row.prop(attribute, 'name', text='')
            row.prop(attribute, 'string_value', text='')
            row.operator('bim.remove_attribute', icon='X', text='').attribute_index = index

        row = layout.row()
        row.prop(props, 'attributes')

        layout.label(text="Property Sets:")
        row = layout.row()
        row.operator('bim.add_pset')

        for index, pset in enumerate(props.psets):
            row = layout.row(align=True)
            row.prop(pset, 'name', text='')
            row.prop(pset, 'file', text='')
            row.operator('bim.remove_pset', icon='X', text='').pset_index = index

        row = layout.row()
        row.prop(props, 'psets')

        layout.label(text="Documents:")
        row = layout.row(align=True)
        row.prop(props, 'applicable_documents', text='')
        row.operator('bim.add_document')

        for index, document in enumerate(props.documents):
            row = layout.row(align=True)
            row.prop(document, 'file', text='')
            row.operator('bim.remove_document', icon='X', text='').document_index = index

        row = layout.row()
        row.prop(props, 'documents')

        layout.label(text="Classification:")

        for index, classification in enumerate(props.classifications):
            row = layout.row(align=True)
            row.prop(classification, 'identification', text='')
            row.prop(classification, 'name', text='')
            row.operator('bim.remove_classification', icon='X', text='').classification_index = index

        row = layout.row()
        row.prop(props, 'classifications')


class BIM_PT_mesh(Panel):
    bl_label = 'IFC Representations'
    bl_idname = 'BIM_PT_mesh'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH" and \
               hasattr(context.active_object.data, "BIMMeshProperties")
    
    def draw(self, context):
        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties
        row = layout.row()
        row.prop(props, 'is_wireframe')
        row = layout.row()
        row.prop(props, 'is_swept_solid')

        row = layout.row()
        row.operator('bim.add_swept_solid')
        for index, swept_solid in enumerate(props.swept_solids):
            row = layout.row(align=True)
            row.prop(swept_solid, 'name', text='')
            row.operator('bim.remove_swept_solid', icon='X', text='').index = index
            row = layout.row()
            sub = row.row(align=True)
            sub.operator('bim.assign_swept_solid_outer_curve').index = index
            sub.operator('bim.select_swept_solid_outer_curve', icon='RESTRICT_SELECT_OFF', text='').index = index
            sub = row.row(align=True)
            sub.operator('bim.add_swept_solid_inner_curve').index = index
            sub.operator('bim.select_swept_solid_inner_curves', icon='RESTRICT_SELECT_OFF', text='').index = index
            row = layout.row(align=True)
            row.operator('bim.assign_swept_solid_extrusion').index = index
            row.operator('bim.select_swept_solid_extrusion', icon='RESTRICT_SELECT_OFF', text='').index = index
        row = layout.row()
        row.prop(props, 'swept_solids')


class BIM_PT_material(Panel):
    bl_label = 'IFC Materials'
    bl_idname = 'BIM_PT_material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.active_material is not None
    
    def draw(self, context):
        if not bpy.context.active_object.active_material:
            return
        props = context.active_object.active_material.BIMMaterialProperties
        layout = self.layout
        row = layout.row()
        row.prop(props, 'is_external')
        row = layout.row(align=True)
        row.prop(props, 'location')
        row.operator('bim.select_external_material_dir', icon="FILE_FOLDER", text="")
        row = layout.row()
        row.prop(props, 'identification')
        row = layout.row()
        row.prop(props, 'name')


class BIM_PT_gis(Panel):
    bl_label = 'IFC Georeferencing'
    bl_idname = "BIM_PT_gis"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        layout.row().prop(scene.BIMProperties, 'has_georeferencing')

        layout.label(text="Map Conversion:")
        layout.row().prop(scene.MapConversion, 'eastings')
        layout.row().prop(scene.MapConversion, 'northings')
        layout.row().prop(scene.MapConversion, 'orthogonal_height')
        layout.row().prop(scene.MapConversion, 'x_axis_abscissa')
        layout.row().prop(scene.MapConversion, 'x_axis_ordinate')
        layout.row().prop(scene.MapConversion, 'scale')

        layout.label(text="Target CRS:")
        layout.row().prop(scene.TargetCRS, 'name')
        layout.row().prop(scene.TargetCRS, 'description')
        layout.row().prop(scene.TargetCRS, 'geodetic_datum')
        layout.row().prop(scene.TargetCRS, 'vertical_datum')
        layout.row().prop(scene.TargetCRS, 'map_projection')
        layout.row().prop(scene.TargetCRS, 'map_zone')
        layout.row().prop(scene.TargetCRS, 'map_unit')


class BIM_PT_bim(Panel):
    bl_label = "Building Information Modeling"
    bl_idname = "BIM_PT_bim"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.BIMProperties

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

        layout.label(text="Aggregates:")
        row = layout.row()
        row.prop(bim_properties, "aggregate_class")
        row = layout.row()
        row.prop(bim_properties, "aggregate_name")
        row = layout.row()
        row.operator("bim.create_aggregate")

        row = layout.row(align=True)
        row.operator("bim.edit_aggregate")
        row.operator("bim.save_aggregate")

        layout.label(text="Classifications:")
        row = layout.row()
        row.prop(bim_properties, "classification")
        row = layout.row()
        row.prop(bim_properties, "reference")

        row = layout.row(align=True)
        row.operator("bim.assign_classification")
        row.operator("bim.unassign_classification")


class BIM_PT_qa(Panel):
    bl_label = "BIMTester Quality Auditing"
    bl_idname = "BIM_PT_qa"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = bpy.context.scene.BIMProperties

        layout.label(text="Gherkin Setup:")

        row = layout.row(align=True)
        row.prop(bim_properties, "features_dir")
        row.operator("bim.select_features_dir", icon="FILE_FOLDER", text="")

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


class BIM_PT_diff(Panel):
    bl_label = "IFC Diff"
    bl_idname = "BIM_PT_diff"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.label(text="IFC Diff Setup:")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_json_file")
        row.operator("bim.select_diff_json_file", icon="FILE_FOLDER", text="")


class BIM_PT_mvd(Panel):
    bl_label = "Model View Definitions"
    bl_idname = "BIM_PT_mvd"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        bim_properties = scene.BIMProperties

        layout.label(text="Custom MVD:")

        row = layout.row()
        row.prop(bim_properties, "export_has_representations")
        row = layout.row()
        row.prop(bim_properties, "export_should_export_all_materials_as_styled_items")
        row = layout.row()
        row.prop(bim_properties, "export_should_use_presentation_style_assignment")

        row = layout.row()
        row.prop(bim_properties, "import_should_ignore_site_coordinates")
        row = layout.row()
        row.prop(bim_properties, "import_should_import_curves")
