import json
import os
import csv
from pathlib import Path
from . import export_ifc
from . import schema
import bpy
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    CollectionProperty
)

cwd = os.path.dirname(os.path.realpath(__file__))

diagram_scales_enum = []
products_enum = []
profiledef_enum = []
classes_enum = []
types_enum = []
availablematerialpsets_enum = []
featuresfiles_enum = []
scenarios_enum = []
psetnames_enum = []
psetfiles_enum = []
classification_enum = []
reference_enum = []
attributes_enum = []
materialattributes_enum = []
documents_enum = []
materialtypes_enum = []
contexts_enum = []
subcontexts_enum = []
target_views_enum = []
persons_enum = []
organisations_enum = []
views_enum = []

@persistent
def setDefaultProperties(scene):
    if bpy.context.scene.BIMProperties.has_model_context \
            and len(bpy.context.scene.BIMProperties.model_subcontexts) == 0:
        subcontext = bpy.context.scene.BIMProperties.model_subcontexts.add()
        subcontext.name = 'Body'
        subcontext.target_view = 'MODEL_VIEW'


def getIfcPredefinedTypes(self, context):
    global types_enum
    if len(types_enum) < 1:
        for name, data in schema.ifc.elements.items():
            if name != self.ifc_class.strip():
                continue
            for attribute in data['attributes']:
                if attribute['name'] != 'PredefinedType':
                    continue
                types_enum.extend([(e, e, '') for e in attribute['enum_values']])
    return types_enum


def refreshClasses(self, context):
    global classes_enum
    classes_enum.clear()
    enum = getIfcClasses(self, context)
    context.scene.BIMProperties.ifc_class = enum[0][0]


def refreshPredefinedTypes(self, context):
    global types_enum
    types_enum.clear()
    enum = getIfcPredefinedTypes(self, context)
    context.scene.BIMProperties.ifc_predefined_type = enum[0][0]


def getDiagramScales(self, context):
    global diagram_scales_enum
    if len(diagram_scales_enum) < 1:
        diagram_scales_enum.extend([
            ('1:5000', '1:5000', ''),
            ('1:2000', '1:2000', ''),
            ('1:1000', '1:1000', ''),
            ('1:500', '1:500', ''),
            ('1:200', '1:200', ''),
            ('1:100', '1:100', ''),
            ('1:50', '1:50', ''),
            ('1:20', '1:20', ''),
            ('1:10', '1:10', ''),
            ('1:5', '1:5', ''),
            ('1:2', '1:2', ''),
            ('1:1', '1:1', '')
        ])
    return diagram_scales_enum


def getBoundaryConditionClasses(self, context):
    return [(c, c, '') for c in
        ['IfcBoundaryEdgeCondition', 'IfcBoundaryFaceCondition',
            'IfcBoundaryNodeCondition', 'IfcBoundaryNodeConditionWarping']]


def refreshBoundaryConditionAttributes(self, context):
    while len(context.active_object.BIMObjectProperties.boundary_condition.attributes) > 0:
        context.active_object.BIMObjectProperties.boundary_condition.attributes.remove(0)
    for attribute in schema.ifc.elements[context.active_object.BIMObjectProperties.boundary_condition.name]['complex_attributes']:
        new_attribute = context.active_object.BIMObjectProperties.boundary_condition.attributes.add()
        new_attribute.name = attribute['name']


def getIfcProducts(self, context):
    global products_enum
    if len(products_enum) < 1:
        products_enum.extend([(e, e, '') for e in
            ['IfcElement', 'IfcElementType', 'IfcSpatialStructureElement', 'IfcStructural']])
    return products_enum


def getIfcClasses(self, context):
    global classes_enum
    if len(classes_enum) < 1:
        classes_enum.extend([(e, e, '') for e in getattr(schema.ifc, self.ifc_product)])
    return classes_enum


def getProfileDef(self, context):
    global profiledef_enum
    if len(profiledef_enum) < 1:
        profiledef_enum.extend([(e, e, '') for e in getattr(schema.ifc, 'IfcParameterizedProfileDef')])
    return profiledef_enum


def getPersons(self, context):
    global persons_enum
    if len(persons_enum) < 1:
        persons_enum.clear()
        with open(os.path.join(self.data_dir, 'owner', 'person.json'), 'r') as f:
            persons = json.load(f)
        persons_enum.extend([(p['Identification'], p['Identification'], '') for p in persons])
    return persons_enum


def getOrganisations(self, context):
    global organisations_enum
    if len(organisations_enum) < 1:
        organisations_enum.clear()
        with open(os.path.join(self.data_dir, 'owner', 'organisation.json'), 'r') as f:
            organisations = json.load(f)
        organisations_enum.extend([(o['Name'], o['Name'], '') for o in organisations])
    return organisations_enum


def getAvailableMaterialPsets(self, context):
    global availablematerialpsets_enum
    if len(availablematerialpsets_enum) < 1:
        availablematerialpsets_enum.clear()
        files = os.listdir(os.path.join(context.scene.BIMProperties.data_dir, 'material'))
        availablematerialpsets_enum.extend([(f, f, '') for f in files])
    return availablematerialpsets_enum


def getFeaturesFiles(self, context):
    global featuresfiles_enum
    if len(featuresfiles_enum) < 1:
        featuresfiles_enum.clear()
        for filename in Path(context.scene.BIMProperties.features_dir).glob('*.feature'):
            f = str(filename.stem)
            featuresfiles_enum.append((f, f, ''))
    return featuresfiles_enum


def refreshFeaturesFiles(self, context):
    global featuresfiles_enum
    featuresfiles_enum.clear()
    getFeaturesFiles(self, context)


def getScenarios(self, context):
    global scenarios_enum
    if len(scenarios_enum) < 1:
        scenarios_enum.clear()
        filename = os.path.join(
            context.scene.BIMProperties.features_dir,
            context.scene.BIMProperties.features_file + '.feature')
        with open(filename, 'r') as feature_file:
            lines = feature_file.readlines()
            for line in lines:
                if 'Scenario:' in line:
                    s = line.strip()[len('Scenario: '):]
                    scenarios_enum.append((s, s, ''))
    return scenarios_enum


def refreshScenarios(self, context):
    global scenarios_enum
    scenarios_enum.clear()
    getScenarios(self, context)


def getPsetNames(self, context):
    global psetnames_enum
    if len(psetnames_enum) < 1:
        psetnames_enum.clear()
        files = os.listdir(os.path.join(self.data_dir, 'pset'))
        psetnames_enum.extend([(f, f, '') for f in files])
    return psetnames_enum


def refreshPsetFiles(self, context):
    global psetfiles_enum
    psetfiles_enum.clear()
    getPsetFiles(self, context)


def getPsetFiles(self, context):
    global psetfiles_enum
    if len(psetfiles_enum) < 1:
        if not self.pset_name.strip():
            return psetfiles_enum
        files = os.listdir(os.path.join(self.data_dir, 'pset', self.pset_name.strip()))
        psetfiles_enum.extend([(f.replace('.csv', ''), f.replace('.csv', ''), '') for f in files])
    return psetfiles_enum


def getClassifications(self, context):
    global classification_enum
    if len(classification_enum) < 1:
        classification_enum.clear()
        with open(os.path.join(self.data_dir, 'class', 'classifications.csv'), 'r') as f:
            data = list(csv.reader(f))
            keys = data.pop(0)
            index = keys.index('Name')
            classification_enum.extend([(str(i), d[index], '') for i, d in enumerate(data)])
    return classification_enum


def refreshReferences(self, context):
    global reference_enum
    reference_enum.clear()
    getReferences(self, context)


def getReferences(self, context):
    global reference_enum
    if len(reference_enum) < 1:
        if not self.classification.strip():
            return reference_enum
        with open(os.path.join(self.data_dir, 'class', 'references.csv'), 'r') as f:
            data = list(csv.reader(f))
            keys = data.pop(0)
            reference_enum.extend([(d[0], '{} - {}'.format(d[0], d[1]), '') for d in data if
                    d[2] == self.classification.strip()])
    return reference_enum


def getApplicableAttributes(self, context):
    global attributes_enum
    attributes_enum.clear()
    if '/' in context.active_object.name \
            and context.active_object.name.split('/')[0] in schema.ifc.elements:
        attributes_enum.extend([(a['name'], a['name'], '') for a in
            schema.ifc.elements[context.active_object.name.split('/')[0]]['attributes']
            if self.attributes.find(a['name']) == -1])
    return attributes_enum


def getApplicableMaterialAttributes(self, context):
    global materialattributes_enum
    materialattributes_enum.clear()
    if '/' in context.active_object.name \
            and context.active_object.name.split('/')[0] in schema.ifc.elements:
        material_type = context.active_object.BIMObjectProperties.material_type
        if material_type[-3:] == 'Set':
            material_type = material_type[0:-3]
        materialattributes_enum.extend([(a['name'], a['name'], '') for a in
            schema.ifc.IfcMaterialDefinition[material_type]['attributes']
            if self.attributes.find(a['name']) == -1])
    return materialattributes_enum


def refreshProfileAttributes(self, context):
    while len(context.active_object.active_material.BIMMaterialProperties.profile_attributes) > 0:
        context.active_object.active_material.BIMMaterialProperties.profile_attributes.remove(0)
    for attribute in schema.ifc.IfcParameterizedProfileDef[self.profile_def]['attributes']:
        profile_attribute = context.active_object.active_material.BIMMaterialProperties.profile_attributes.add()
        profile_attribute.name = attribute['name']


def getApplicableDocuments(self, context):
    global documents_enum
    documents_enum.clear()
    doc_path = os.path.join(context.scene.BIMProperties.data_dir, 'doc')
    for filename in Path(doc_path).glob('**/*'):
        uri = str(filename.relative_to(doc_path).as_posix())
        documents_enum.append((uri, uri, ''))
    return documents_enum


def getMaterialTypes(self, context):
    global materialtypes_enum
    materialtypes_enum.clear()
    materialtypes_enum = [(m, m, '') for m in [
        'IfcMaterial',
        'IfcMaterialConstituentSet',
        'IfcMaterialLayerSet',
        'IfcMaterialProfileSet']]
    return materialtypes_enum


def getSubcontexts(self, context):
    global subcontexts_enum
    subcontexts_enum.clear()
    # TODO: allow override of generated subcontexts?
    subcontexts = export_ifc.IfcExportSettings().subcontexts
    for subcontext in subcontexts:
        subcontexts_enum.append((subcontext, subcontext, ''))
    return subcontexts_enum


def getTargetViews(self, context):
    global target_views_enum
    target_views_enum.clear()
    for target_view in export_ifc.IfcExportSettings().target_views:
        target_views_enum.append((target_view, target_view, ''))
    return target_views_enum


def getViews(self, context):
    global views_enum
    views_enum.clear()
    views_collection = bpy.data.collections.get('Views')
    if not views_collection:
        return views_enum
    for collection in views_collection.children:
        for obj in collection.objects:
            if obj.type == 'CAMERA':
                views_enum.append((obj.name, obj.name, ''))
    return views_enum


class Subcontext(PropertyGroup):
    name: StringProperty(name='Name')
    target_view: StringProperty(name='Target View')


class DocProperties(PropertyGroup):
    should_recut: BoolProperty(name="Should Recut", default=True)
    view_name: StringProperty(name="View Name")
    available_views: EnumProperty(items=getViews, name="Available Views")


class BIMCameraProperties(PropertyGroup):
    view_name: StringProperty(name="View Name")
    diagram_scale: EnumProperty(items=getDiagramScales, name='Diagram Scale')


class BIMProperties(PropertyGroup):
    schema_dir: StringProperty(default=os.path.join(cwd ,'schema') + os.path.sep, name="Schema Directory")
    data_dir: StringProperty(default=os.path.join(cwd, 'data') + os.path.sep, name="Data Directory")
    ifc_file: StringProperty(name="IFC File")
    audit_ifc_class: EnumProperty(items=getIfcClasses, name="Audit Class")
    ifc_product: EnumProperty(items=getIfcProducts, name="Products", update=refreshClasses)
    ifc_class: EnumProperty(items=getIfcClasses, name="Class", update=refreshPredefinedTypes)
    ifc_predefined_type: EnumProperty(
        items = getIfcPredefinedTypes,
        name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
    export_has_representations: BoolProperty(name="Export Representations", default=True)
    export_should_export_all_materials_as_styled_items: BoolProperty(name="Export All Materials as Styled Items", default=False)
    export_should_use_presentation_style_assignment: BoolProperty(name="Export with Presentation Style Assignment", default=False)
    import_should_ignore_site_coordinates: BoolProperty(name="Import Ignoring Site Coordinates", default=False)
    import_should_ignore_building_coordinates: BoolProperty(name="Import Ignoring Building Coordinates", default=False)
    import_should_reset_absolute_coordinates: BoolProperty(name="Import Resetting Absolute Coordinates", default=False)
    import_should_import_curves: BoolProperty(name="Import Curves", default=False)
    import_should_import_opening_elements: BoolProperty(name="Import Opening Elements", default=False)
    import_should_import_spaces: BoolProperty(name="Import Spaces", default=False)
    import_should_auto_set_workarounds: BoolProperty(name="Automatically Set Vendor Workarounds", default=True)
    import_should_treat_styled_item_as_material: BoolProperty(name="Import Treating Styled Item as Material", default=False)
    import_should_use_legacy: BoolProperty(name="Import with Legacy Importer", default=False)
    import_should_use_cpu_multiprocessing: BoolProperty(name="Import with CPU Multiprocessing", default=False)
    import_should_merge_by_class: BoolProperty(name="Import and Merge by Class", default=False)
    import_should_merge_by_material: BoolProperty(name="Import and Merge by Material", default=False)
    qa_reject_element_reason: StringProperty(name="Element Rejection Reason")
    person: EnumProperty(items=getPersons, name="Person")
    organisation: EnumProperty(items=getOrganisations, name="Organisation")
    pset_name: EnumProperty(items=getPsetNames, name="Pset Name", update=refreshPsetFiles)
    pset_file: EnumProperty(items=getPsetFiles, name="Pset File")
    has_georeferencing: BoolProperty(name="Has Georeferencing", default=False)
    has_library: BoolProperty(name="Has Project Library", default=False)
    search_regex: BoolProperty(name="Search With Regex", default=False)
    search_ignorecase: BoolProperty(name="Search Ignoring Case", default=True)
    global_id: StringProperty(name="GlobalId")
    search_attribute_name: StringProperty(name="Search Attribute Name")
    search_attribute_value: StringProperty(name="Search Attribute Value")
    search_pset_name: StringProperty(name="Search Pset Name")
    search_prop_name: StringProperty(name="Search Prop Name")
    search_pset_value: StringProperty(name="Search Pset Value")
    features_dir: StringProperty(default='', name="Features Directory", update=refreshFeaturesFiles)
    features_file: EnumProperty(items=getFeaturesFiles, name="Features File", update=refreshScenarios)
    scenario: EnumProperty(items=getScenarios, name="Scenario")
    diff_json_file: StringProperty(default='', name="Diff JSON File")
    diff_old_file: StringProperty(default='', name="Diff Old IFC File")
    diff_new_file: StringProperty(default='', name="Diff New IFC File")
    aggregate_class: EnumProperty(items=getIfcClasses, name="Aggregate Class")
    aggregate_name: StringProperty(name="Aggregate Name")
    classification: EnumProperty(items=getClassifications, name="Classification", update=refreshReferences)
    reference: EnumProperty(items=getReferences, name="Reference")
    has_model_context: BoolProperty(name="Has Model Context", default=True)
    has_plan_context: BoolProperty(name="Has Plan Context", default=False)
    model_subcontexts: CollectionProperty(name='Model Subcontexts', type=Subcontext)
    plan_subcontexts: CollectionProperty(name='Plan Subcontexts', type=Subcontext)
    available_contexts: EnumProperty(items=[('Model', 'Model', ''), ('Plan', 'Plan', '')], name="Available Contexts")
    available_subcontexts: EnumProperty(items=getSubcontexts, name="Available Subcontexts")
    available_target_views: EnumProperty(items=getTargetViews, name="Available Target Views")


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

class BIMLibrary(PropertyGroup):
    name: StringProperty(name="Name")
    version: StringProperty(name="Version")
    publisher: StringProperty(name="Publisher")
    version_date: StringProperty(name="Version Date")
    location: StringProperty(name="Location")
    description: StringProperty(name="Description")


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
    properties: CollectionProperty(name="Properties", type=Attribute)

class Document(PropertyGroup):
    file: StringProperty(name="File")

class Classification(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")


class GlobalId(PropertyGroup):
    name: StringProperty(name="Name")


class BoundaryCondition(PropertyGroup):
    name: EnumProperty(items=getBoundaryConditionClasses, name='Boundary Type', update=refreshBoundaryConditionAttributes)
    attributes: CollectionProperty(name="Attributes", type=Attribute)


class BIMObjectProperties(PropertyGroup):
    global_ids: CollectionProperty(name="GlobalIds", type=GlobalId)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    type_product: PointerProperty(name='Type Product', type=bpy.types.Object)
    psets: CollectionProperty(name="Psets", type=Pset)
    applicable_attributes: EnumProperty(items=getApplicableAttributes, name="Attribute Names")
    documents: CollectionProperty(name="Documents", type=Document)
    applicable_documents: EnumProperty(items=getApplicableDocuments, name="Available Documents")
    classifications: CollectionProperty(name="Classifications", type=Classification)
    material_type: EnumProperty(items=getMaterialTypes, name="Material Type")
    override_psets: CollectionProperty(name="Override Psets", type=Pset)
    override_pset_name: StringProperty(name="Override Pset Name")
    has_boundary_condition: BoolProperty(name='Has Boundary Condition')
    boundary_condition: PointerProperty(name='Boundary Condition', type=BoundaryCondition)
    structural_member_connection: PointerProperty(name='Structural Member Connection', type=bpy.types.Object)


class BIMMaterialProperties(PropertyGroup):
    is_external: BoolProperty(name="Has External Definition")
    location: StringProperty(name="Location")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    available_material_psets: EnumProperty(items=getAvailableMaterialPsets, name="Material Pset")
    psets: CollectionProperty(name="Psets", type=Pset)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    applicable_attributes: EnumProperty(items=getApplicableMaterialAttributes, name="Attribute Names")
    profile_def: EnumProperty(items=getProfileDef, name='Parameterized Profile Def', update=refreshProfileAttributes)
    profile_attributes: CollectionProperty(name='Profile Attributes', type=Attribute)


class SweptSolid(PropertyGroup):
    name: StringProperty(name="Name")
    outer_curve: StringProperty(name="Outer Curve")
    inner_curves: StringProperty(name="Inner Curves")
    extrusion: StringProperty(name="Extrusion")


class BIMMeshProperties(PropertyGroup):
    is_wireframe: BoolProperty(name="Is Wireframe")
    is_swept_solid: BoolProperty(name="Is Swept Solid")
    swept_solids: CollectionProperty(name="Swept Solids", type=SweptSolid)
    is_parametric: BoolProperty(name='Is Parametric', default=False)
