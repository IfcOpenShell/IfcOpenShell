import json
import os
import csv
import ifcopenshell
from pathlib import Path
from . import export_ifc
from . import schema
from . import bcf
from . import ifc
from . import annotation
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
    FloatVectorProperty,
    CollectionProperty
)

cwd = os.path.dirname(os.path.realpath(__file__))

diagram_scales_enum = []
products_enum = []
profiledef_enum = []
classes_enum = []
types_enum = []
availablematerialpsets_enum = []
ifcpatchrecipes_enum = []
featuresfiles_enum = []
scenarios_enum = []
psetnames_enum = []
psetfiles_enum = []
psettemplatefiles_enum = []
propertysettemplates_enum = []
classification_enum = []
attributes_enum = []
psetnames_enum = []
qtonames_enum = []
materialattributes_enum = []
materialtypes_enum = []
contexts_enum = []
subcontexts_enum = []
target_views_enum = []
persons_enum = []
organisations_enum = []
views_enum = []
sheets_enum = []
bcfviewpoints_enum = []

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
        products_enum.extend([(e, e, '') for e in [
            'IfcElement',
            'IfcElementType',
            'IfcSpatialElement',
            'IfcGroup',
            'IfcStructural',
            'IfcPositioningElement',
            'IfcContext',
            'IfcAnnotation']])
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
    persons_enum.clear()
    persons_enum.extend([(p.name, p.name, '') for p in bpy.context.scene.BIMProperties.people])
    return persons_enum


def getOrganisations(self, context):
    global organisations_enum
    organisations_enum.clear()
    organisations_enum.extend([(o.name, o.name, '') for o in bpy.context.scene.BIMProperties.organisations])
    return organisations_enum


def getAvailableMaterialPsets(self, context):
    global availablematerialpsets_enum
    if len(availablematerialpsets_enum) < 1:
        availablematerialpsets_enum.clear()
        files = os.listdir(os.path.join(context.scene.BIMProperties.data_dir, 'material'))
        availablematerialpsets_enum.extend([(f, f, '') for f in files])
    return availablematerialpsets_enum


def getIfcPatchRecipes(self, context):
    global ifcpatchrecipes_enum
    if len(ifcpatchrecipes_enum) < 1:
        ifcpatchrecipes_enum.clear()
        for filename in Path(os.path.join(cwd, '..', 'libs', 'site', 'packages', 'recipes')).glob('*.py'):
            f = str(filename.stem)
            if f == '__init__':
                continue
            ifcpatchrecipes_enum.append((f, f, ''))
    return ifcpatchrecipes_enum


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


def getPsetTemplateFiles(self, context):
    global psettemplatefiles_enum
    if len(psettemplatefiles_enum) < 1:
        files = os.listdir(os.path.join(self.data_dir, 'pset'))
        psettemplatefiles_enum.extend([(f.replace('.ifc', ''), f.replace('.ifc', ''), '') for f in files])
    return psettemplatefiles_enum


def refreshPropertySetTemplates(self, context):
    global propertysettemplates_enum
    propertysettemplates_enum.clear()
    getPropertySetTemplates(self, context)


def getPropertySetTemplates(self, context):
    global propertysettemplates_enum
    if len(propertysettemplates_enum) < 1:
        ifc.IfcStore.pset_template_path = os.path.join(
            context.scene.BIMProperties.data_dir, 'pset', context.scene.BIMProperties.pset_template_files + '.ifc')
        ifc.IfcStore.pset_template_file = ifcopenshell.open(ifc.IfcStore.pset_template_path)
        templates = ifc.IfcStore.pset_template_file.by_type('IfcPropertySetTemplate')
        propertysettemplates_enum.extend([(t.GlobalId, t.Name, '') for t in templates])
    return propertysettemplates_enum


def getClassifications(self, context):
    global classification_enum
    if len(classification_enum) < 1:
        classification_enum.clear()
        files = os.listdir(os.path.join(self.schema_dir, 'classifications'))
        classification_enum.extend([(f.replace('.ifc', ''), f.replace('.ifc', ''), '') for f in files])
    return classification_enum


def refreshReferences(self, context):
    context.scene.BIMProperties.classification_references.root = None
    ClassificationView.raw_data = schema.ifc.load_classification(context.scene.BIMProperties.classification)
    context.scene.BIMProperties.classification_references.root = ''


def getPsetNames(self, context):
    global psetnames_enum
    psetnames_enum.clear()
    if '/' in context.active_object.name \
            and context.active_object.name.split('/')[0] in schema.ifc.elements:
        empty = ifcopenshell.file()
        element = empty.create_entity(context.active_object.name.split('/')[0])
        for ifc_class, pset_names in schema.ifc.applicable_psets.items():
            if element.is_a(ifc_class):
                psetnames_enum.extend([(p, p, '') for p in pset_names])
    return psetnames_enum


def getQtoNames(self, context):
    global qtonames_enum
    qtonames_enum.clear()
    if '/' in context.active_object.name \
            and context.active_object.name.split('/')[0] in schema.ifc.elements:
        empty = ifcopenshell.file()
        element = empty.create_entity(context.active_object.name.split('/')[0])
        for ifc_class, qto_names in schema.ifc.applicable_qtos.items():
            if element.is_a(ifc_class):
                qtonames_enum.extend([(q, q, '') for q in qto_names])
    return qtonames_enum


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
                views_enum.append((obj.name.split('/')[1], obj.name.split('/')[1], ''))
    return views_enum


def refreshSheets(self, context):
    global sheets_enum
    sheets_enum.clear()
    getSheets(self, context)


def getSheets(self, context):
    global sheets_enum
    if len(sheets_enum) < 1:
        sheets_enum.clear()
        for filename in Path(os.path.join(context.scene.BIMProperties.data_dir, 'sheets')).glob('*.svg'):
            f = str(filename.stem)
            sheets_enum.append((f, f, ''))
    return sheets_enum


def refreshFontSize(self, context):
    annotation.Annotator.resize_text(context.active_object)


class StrProperty(PropertyGroup):
    pass


class Variable(PropertyGroup):
    name: StringProperty(name="Name")
    prop_key: StringProperty(name="Property Key")


class Subcontext(PropertyGroup):
    name: StringProperty(name='Name')
    context: StringProperty(name='Context')
    target_view: StringProperty(name='Target View')


class DocProperties(PropertyGroup):
    should_recut: BoolProperty(name="Should Recut", default=True)
    should_recut_selected: BoolProperty(name="Should Recut Selected Only", default=False)
    should_render: BoolProperty(name="Should Render", default=True)
    should_extract: BoolProperty(name="Should Extract", default=True)
    view_name: StringProperty(name="View Name")
    available_views: EnumProperty(items=getViews, name="Available Views")
    sheet_name: StringProperty(name="Sheet Name", update=refreshSheets)
    available_sheets: EnumProperty(items=getSheets, name="Available Sheets")
    ifc_files: CollectionProperty(name='IFCs', type=StrProperty)


class BIMCameraProperties(PropertyGroup):
    view_name: StringProperty(name="View Name")
    diagram_scale: EnumProperty(items=getDiagramScales, name='Diagram Scale')
    is_nts: BoolProperty(name='Is NTS')
    cut_objects: EnumProperty(items=[
        ('.IfcWall|.IfcSlab|.IfcCurtainWall|.IfcStair|.IfcStairFlight|.IfcColumn|.IfcBeam|.IfcMember|.IfcCovering',
            'Overall Plan / Section', ''),
        ('.IfcElement', 'Detail Drawing', ''),
        ('CUSTOM', 'Custom', '')
        ], name='Cut Objects')
    cut_objects_custom: StringProperty(name='Custom Cut')


class BIMTextProperties(PropertyGroup):
    font_size: EnumProperty(items=[
        ('1.8', '1.8 - Small', ''),
        ('2.5', '2.5 - Regular', ''),
        ('3.5', '3.5 - Large', ''),
        ('5.0', '5.0 - Header', ''),
        ('7.0', '7.0 - Title', ''),
        ], update=refreshFontSize, name='Font Size')
    symbol: EnumProperty(items=[
        ('None', 'None', ''),
        ('rectangle-tag', 'Rectangle Tag', ''),
        ('door-tag', 'Door Tag', ''),
        ], update=refreshFontSize, name='Symbol')
    related_element: PointerProperty(name='Related Element', type=bpy.types.Object)
    variables: CollectionProperty(name='Variables', type=Variable)


class DocumentInformation(PropertyGroup):
    name: StringProperty(name='Identification')
    human_name: StringProperty(name='Name')
    description: StringProperty(name='Description')
    location: StringProperty(name='Location')
    purpose: StringProperty(name='Purpose')
    intended_use: StringProperty(name='Intended Use')
    scope: StringProperty(name='Scope')
    revision: StringProperty(name='Revision')
    document_owner: StringProperty(name='Owner')
    editors: StringProperty(name='Editors')
    creation_time: StringProperty(name='Created On')
    last_revision_time: StringProperty(name='Last Revised')
    electronic_format: StringProperty(name='Format')
    valid_from: StringProperty(name='Valid From')
    valid_until: StringProperty(name='Valid Until')
    confidentiality: EnumProperty(items=[
        ('NOTDEFINED', 'NOTDEFINED', 'Not defined.'),
        ('PUBLIC', 'PUBLIC', 'Document is publicly available.'),
        ('RESTRICTED', 'RESTRICTED', 'Document availability is restricted.'),
        ('CONFIDENTIAL', 'CONFIDENTIAL', 'Document is confidential and its contents should not be revealed without permission.'),
        ('PERSONAL', 'PERSONAL', 'Document is personal to the author.'),
        ('USERDEFINED', 'USERDEFINED', 'Describe confidentiality elsewhere.')
        ], name='Confidentiality')
    status: EnumProperty(items=[
        ('NOTDEFINED', 'NOTDEFINED', 'Not defined'),
        ('DRAFT', 'DRAFT', 'Document is a draft.'),
        ('FINALDRAFT', 'FINALDRAFT', 'Document is a final draft.'),
        ('FINAL', 'FINAL', 'Document is final.'),
        ('REVISION', 'REVISION', 'Document has undergone revision.'),
        ], name='Status')


class DocumentReference(PropertyGroup):
    location: StringProperty(name="Location")
    name: StringProperty(name="Identification")
    human_name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    referenced_document: StringProperty(name="Referenced Document")


class ClashSource(PropertyGroup):
    name: StringProperty(name='File')
    selector: StringProperty(name='Selector')
    mode: EnumProperty(items=[
        ('i', 'Include', 'Only the selected objects are included for clashing'),
        ('e', 'Exclude', 'All objects except the selected objects are included for clashing')
        ], name='Mode')


class ClashSet(PropertyGroup):
    name: StringProperty(name='Name')
    tolerance: FloatProperty(name='Tolerance')
    a: CollectionProperty(name='Group A', type=ClashSource)
    b: CollectionProperty(name='Group B', type=ClashSource)


class Constraint(PropertyGroup):
    name: StringProperty(name='Name')
    description: StringProperty(name='Description')
    constraint_grade: EnumProperty(items=[
        ('HARD', 'HARD', 'Qualifies a constraint such that it must be followed rigidly within or at the values set.'),
        ('SOFT', 'SOFT', 'Qualifies a constraint such that it should be followed within or at the values set.'),
        ('ADVISORY', 'ADVISORY', 'Qualifies a constraint such that it is advised that it is followed within or at the values set.'),
        ('USERDEFINED', 'USERDEFINED', 'A user-defined grade indicated by a separate attribute at the referencing entity.'),
        ('NOTDEFINED', 'NOTDEFINED', 'Grade has not been specified.'),
        ], name='Grade')
    constraint_source: StringProperty(name='Source')
    user_defined_grade: StringProperty(name='Custom Grade')
    objective_qualifier: EnumProperty(items=[
        ('CODECOMPLIANCE', 'CODECOMPLIANCE', 'A constraint whose objective is to ensure satisfaction of a code compliance provision.'),
        ('CODEWAIVER', 'CODEWAIVER', 'A constraint whose objective is to identify an agreement that code compliance requirements (the waiver) will not be enforced.'),
        ('DESIGNINTENT', 'DESIGNINTENT', 'A constraint whose objective is to ensure satisfaction of a design intent provision.'),
        ('EXTERNAL', 'EXTERNAL', 'A constraint whose objective is to synchronize data with an external source such as a file'),
        ('HEALTHANDSAFETY', 'HEALTHANDSAFETY', 'A constraint whose objective is to ensure satisfaction of a health and safety provision.'),
        ('MERGECONFLICT', 'MERGECONFLICT', 'A constraint whose objective is to resolve a conflict such as merging data from multiple sources.'),
        ('MODELVIEW', 'MODELVIEW', 'A constraint whose objective is to ensure data conforms to a model view definition.'),
        ('PARAMETER', 'PARAMETER', 'A constraint whose objective is to calculate a value based on other referenced values.'),
        ('REQUIREMENT', 'REQUIREMENT', 'A constraint whose objective is to ensure satisfaction of a project requirement provision.'),
        ('SPECIFICATION', 'SPECIFICATION', 'A constraint whose objective is to ensure satisfaction of a specification provision.'),
        ('TRIGGERCONDITION', 'TRIGGERCONDITION', 'A constraint whose objective is to indicate a limiting value beyond which the condition of an object requires a particular form of attention.'),
        ('USERDEFINED', 'USERDEFINED', ''),
        ('NOTDEFINED', 'NOTDEFINED', '')
        ], name='Qualifier')
    user_defined_qualifier: StringProperty(name='Custom Qualifier')


class BcfTopic(PropertyGroup):
    name: StringProperty(name='Name')


class BcfTopicLabel(PropertyGroup):
    name: StringProperty(name='Name')


class BcfTopicLink(PropertyGroup):
    name: StringProperty(name='Name')


class BcfTopicFile(PropertyGroup):
    name: StringProperty(name='Name')
    reference: StringProperty(name='Reference')
    date: StringProperty(name='Date')
    is_external: BoolProperty(name='Is External')
    ifc_project: StringProperty(name='IFC Project')
    ifc_spatial: StringProperty(name='IFC Spatial')


class BcfTopicDocumentReference(PropertyGroup):
    name: StringProperty(name='Reference')
    description: StringProperty(name='Description')
    guid: StringProperty(name='GUID')
    is_external: BoolProperty(name='Is External')


class BcfTopicRelatedTopic(PropertyGroup):
    name: StringProperty(name='Name')
    guid: StringProperty(name='GUID')


def refreshBcfTopic(self, context):
    RefreshBcfTopic.refresh(context)

class RefreshBcfTopic():
    props: None
    topic: None

    @classmethod
    def refresh(cls, context):
        import bcfplugin
        global bcfviewpoints_enum

        cls.props = bpy.context.scene.BCFProperties
        cls.topic = bcf.BcfStore.topics[cls.props.active_topic_index][1]

        cls.load_topic_metadata()
        cls.load_topic_labels()
        cls.load_topic_files()
        cls.load_topic_links()
        cls.load_snippet()
        cls.load_document_references()
        cls.load_related_topics()
        cls.load_viewpoints()
        cls.load_comments()

    @classmethod
    def load_topic_metadata(cls):
        cls.props.topic_guid = str(cls.topic.xmlId)
        cls.props.topic_type = cls.topic.type
        cls.props.topic_status = cls.topic.status
        cls.props.topic_priority = cls.topic.priority
        cls.props.topic_stage = cls.topic.stage
        if cls.topic.date:
            cls.props.topic_creation_date = cls.topic.date.strftime('%a %Y-%m-%d %H:%S')
        else:
            cls.props.topic_creation_date = ''
        cls.props.topic_creation_author = cls.topic.author
        if cls.topic.modDate:
            cls.props.topic_modified_date = cls.topic.modDate.strftime('%a %Y-%m-%d %H:%S')
        else:
            cls.props.topic_modified_date = ''
        cls.props.topic_modified_author = cls.topic.modAuthor
        cls.props.topic_assigned_to = cls.topic.assignee
        if cls.topic.dueDate:
            cls.props.topic_due_date = cls.topic.dueDate.strftime('%a %Y-%m-%d %H:%S')
        else:
            cls.props.topic_due_date = ''
        cls.props.topic_description = cls.topic.description

    @classmethod
    def load_topic_labels(cls):
        while len(cls.props.topic_labels) > 0:
            cls.props.topic_labels.remove(0)
        for label in cls.topic.labels:
            new = cls.props.topic_labels.add()
            new.name = label.value

    @classmethod
    def load_topic_files(cls):
        import bcfplugin
        while len(cls.props.topic_files) > 0:
            cls.props.topic_files.remove(0)
        files = bcfplugin.getRelevantIfcFiles(cls.topic)
        for f in files:
            new = cls.props.topic_files.add()
            new.name = f.filename
            new.date = f.time.strftime('%a %Y-%m-%d %H:%S')
            new.reference = f.reference.uri
            new.ifc_project = f.ifcProjectId
            new.ifc_spatial = f.ifcSpatialStructureElement
            new.is_external = f.external

    @classmethod
    def load_topic_links(cls):
        while len(cls.props.topic_links) > 0:
            cls.props.topic_links.remove(0)
        for link in cls.topic.referenceLinks:
            new = cls.props.topic_links.add()
            new.name = link.value

    @classmethod
    def load_snippet(cls):
        cls.props.topic_has_snippet = bool(cls.topic.bimSnippet)
        if cls.topic.bimSnippet:
            cls.props.topic_snippet_reference = cls.topic.bimSnippet.reference.uri
            if cls.topic.bimSnippet.schema.uri:
                cls.props.topic_snippet_schema = cls.topic.bimSnippet.schema.uri
            cls.props.topic_snippet_type = cls.topic.bimSnippet.type
            if cls.topic.bimSnippet.external:
                cls.props.topic_snippet_is_external = cls.topic.bimSnippet.external
            else:
                cls.props.topic_snippet_is_external = False

    @classmethod
    def load_document_references(cls):
        while len(cls.props.topic_document_references) > 0:
            cls.props.topic_document_references.remove(0)
        for doc in cls.topic.docRefs:
            new = cls.props.topic_document_references.add()
            new.name = doc.reference.uri
            new.description = doc.description
            new.guid = str(doc.guid)
            new.is_external = doc.external

    @classmethod
    def load_related_topics(cls):
        import bcfplugin
        while len(cls.props.topic_related_topics) > 0:
            cls.props.topic_related_topics.remove(0)
        for t in cls.topic.relatedTopics:
            new = cls.props.topic_related_topics.add()
            new.name = bcfplugin.getTopicFromUUID(t.value).title
            new.guid = str(t.value)

    @classmethod
    def load_viewpoints(cls):
        import bcfplugin
        bcfviewpoints_enum.clear()
        bcf.BcfStore.viewpoints = bcfplugin.getViewpoints(cls.topic, realViewpoint=False)
        for i, viewpoint in enumerate(bcf.BcfStore.viewpoints):
            bcfviewpoints_enum.append((str(i), 'View {}'.format(i+1), ''))

    @classmethod
    def load_comments(cls):
        import bcfplugin
        bcf.BcfStore.comments = bcfplugin.getComments(cls.topic)
        comments = bpy.data.texts.get('BCF Comments')
        if comments:
            comments.clear()
        else:
            comments = bpy.data.texts.new('BCF Comments')
        for i, comment in enumerate(bcf.BcfStore.comments):
            comments.write('# Comment {} - {}\n'.format(i + 1, comment[1].xmlId))
            comments.write('# From: {} on {}\n'.format(comment[1].author, comment[1].date))
            if comment[1].modDate:
                comments.write('# Modified by {} on {}\n'.format(comment[1].modAuthor, comment[1].modDate))
            comments.write(comment[1].comment)
            comments.write('\n\n-----\n\n')


def getBcfViewpoints(self, context):
    global bcfviewpoints_enum
    return bcfviewpoints_enum


class PropertySetTemplate(PropertyGroup):
    global_id: StringProperty(name="Global ID")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    template_type: EnumProperty(items=[
        ('PSET_TYPEDRIVENONLY', 'Pset - IfcTypeObject', 'The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.'),
        ('PSET_TYPEDRIVENOVERRIDE', 'Pset - IfcTypeObject - Override', 'The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.'),
        ('PSET_OCCURRENCEDRIVEN', 'Pset - IfcObject', 'The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcObject.'),
        ('PSET_PERFORMANCEDRIVEN', 'Pset - IfcPerformanceHistory', 'The property sets defined by this IfcPropertySetTemplate can only be assigned to IfcPerformanceHistory.'),
        ('QTO_TYPEDRIVENONLY', 'Qto - IfcTypeObject', 'The element quantity defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.'),
        ('QTO_TYPEDRIVENOVERRIDE', 'Qto - IfcTypeObject - Override', 'The element quantity defined by this IfcPropertySetTemplate can be assigned to subtypes of IfcTypeObject and can be overridden by an element quantity with same name at subtypes of IfcObject.'),
        ('QTO_OCCURRENCEDRIVEN', 'Qto - IfcObject', 'The element quantity defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcObject.'),
        ('NOTDEFINED', 'Not defined', 'No restriction provided, the property sets defined by this IfcPropertySetTemplate can be assigned to any entity, if not otherwise restricted by the ApplicableEntity attribute.')
        ], name="Template Type")
    applicable_entity: StringProperty(name="Applicable Entity")


class PropertyTemplate(PropertyGroup):
    global_id: StringProperty(name='Global ID')
    name: StringProperty(name='Name')
    description: StringProperty(name='Description')
    primary_measure_type: EnumProperty(items=[
        (x, x, '') for x in [
            'IfcInteger',
            'IfcReal',
            'IfcBoolean',
            'IfcIdentifier',
            'IfcText',
            'IfcLabel',
            'IfcLogical',
            'IfcDateTime',
            'IfcDate',
            'IfcTime',
            'IfcDuration',
            'IfcTimeStamp',

            'IfcPositiveInteger',
            'IfcBinary',
            'IfcVolumeMeasure',
            'IfcTimeMeasure',
            'IfcThermodynamicTemperatureMeasure',
            'IfcSolidAngleMeasure',
            'IfcPositiveRatioMeasure',
            'IfcRatioMeasure',
            'IfcPositivePlaneAngleMeasure',
            'IfcPlaneAngleMeasure',
            'IfcParameterValue',
            'IfcNumericMeasure',
            'IfcMassMeasure',
            'IfcPositiveLengthMeasure',
            'IfcLengthMeasure',
            'IfcElectricCurrentMeasure',
            'IfcDescriptiveMeasure',
            'IfcCountMeasure',
            'IfcContextDependentMeasure',
            'IfcAreaMeasure',
            'IfcAmountOfSubstanceMeasure',
            'IfcLuminousIntensityMeasure',
            'IfcNormalisedRatioMeasure',
            'IfcComplexNumber',
            'IfcNonNegativeLengthMeasure',

            'IfcAbsorbedDoseMeasure',
            'IfcAccelerationMeasure',
            'IfcAngularVelocityMeasure',
            'IfcAreaDensityMeasure',
            'IfcCompoundPlaneAngleMeasure',
            'IfcCurvatureMeasure',
            'IfcDoseEquivalentMeasure',
            'IfcDynamicViscosityMeasure',
            'IfcElectricCapacitanceMeasure',
            'IfcElectricChargeMeasure',
            'IfcElectricConductanceMeasure',
            'IfcElectricResistanceMeasure',
            'IfcElectricVoltageMeasure',
            'IfcEnergyMeasure',
            'IfcForceMeasure',
            'IfcFrequencyMeasure',
            'IfcHeatFluxDensityMeasure',
            'IfcHeatingValueMeasure',
            'IfcIlluminanceMeasure',
            'IfcInductanceMeasure',
            'IfcIntegerCountRateMeasure',
            'IfcIonConcentrationMeasure',
            'IfcIsothermalMoistureCapacityMeasure',
            'IfcKinematicViscosityMeasure',
            'IfcLinearForceMeasure',
            'IfcLinearMomentMeasure',
            'IfcLinearStiffnessMeasure',
            'IfcLinearVelocityMeasure',
            'IfcLuminousFluxMeasure',
            'IfcLuminousIntensityDistributionMeasure',
            'IfcMagneticFluxDensityMeasure',
            'IfcMagneticFluxMeasure',
            'IfcMassDensityMeasure',
            'IfcMassFlowRateMeasure',
            'IfcMassPerLengthMeasure',
            'IfcModulusOfElasticityMeasure',
            'IfcModulusOfLinearSubgradeReactionMeasure',
            'IfcModulusOfRotationalSubgradeReactionMeasure',
            'IfcModulusOfSubgradeReactionMeasure',
            'IfcMoistureDiffusivityMeasure',
            'IfcMolecularWeightMeasure',
            'IfcMomentOfInertiaMeasure',
            'IfcMonetaryMeasure',
            'IfcPHMeasure',
            'IfcPlanarForceMeasure',
            'IfcPowerMeasure',
            'IfcPressureMeasure',
            'IfcRadioActivityMeasure',
            'IfcRotationalFrequencyMeasure',
            'IfcRotationalMassMeasure',
            'IfcRotationalStiffnessMeasure',
            'IfcSectionModulusMeasure',
            'IfcSectionalAreaIntegralMeasure',
            'IfcShearModulusMeasure',
            'IfcSoundPowerLevelMeasure',
            'IfcSoundPowerMeasure',
            'IfcSoundPressureLevelMeasure',
            'IfcSoundPressureMeasure',
            'IfcSpecificHeatCapacityMeasure',
            'IfcTemperatureGradientMeasure',
            'IfcTemperatureRateOfChangeMeasure',
            'IfcThermalAdmittanceMeasure',
            'IfcThermalConductivityMeasure',
            'IfcThermalExpansionCoefficientMeasure',
            'IfcThermalResistanceMeasure',
            'IfcThermalTransmittanceMeasure',
            'IfcTorqueMeasure',
            'IfcVaporPermeabilityMeasure',
            'IfcVolumetricFlowRateMeasure',
            'IfcWarpingConstantMeasure',
            'IfcWarpingMomentMeasure',
            ]
        ], name='Primary Measure Type')


class Address(PropertyGroup):
    name: StringProperty(name="Name") # Stores IfcPostalAddress or IfcTelecomAddress
    purpose: EnumProperty(items=[
        ('OFFICE', 'OFFICE', 'An office address.'),
        ('SITE', 'SITE', 'A site address.'),
        ('HOME', 'HOME', 'A home address.'),
        ('DISTRIBUTIONPOINT', 'DISTRIBUTIONPOINT', 'A postal distribution point address.'),
        ('USERDEFINED', 'USERDEFINED', 'A user defined address type to be provided.'),
    ], name='Purpose')
    description: StringProperty(name="Description")
    user_defined_purpose: StringProperty(name="Custom Purpose")

    internal_location: StringProperty(name="Internal Location")
    address_lines: StringProperty(name="Address")
    postal_box: StringProperty(name="Postal Box")
    town: StringProperty(name="Town")
    region: StringProperty(name="Region")
    postal_code: StringProperty(name="Postal Code")
    country: StringProperty(name="Country")

    telephone_numbers: StringProperty(name="Telephone Numbers")
    fascimile_numbers: StringProperty(name="Fascimile Numbers")
    pager_number: StringProperty(name="Pager Number")
    electronic_mail_addresses: StringProperty(name="Emails")
    www_home_page_url: StringProperty(name="Websites")
    messaging_ids: StringProperty(name="IMs")


class Role(PropertyGroup):
    name: EnumProperty(items=[
        ('SUPPLIER', 'SUPPLIER', ''),
        ('MANUFACTURER', 'MANUFACTURER', ''),
        ('CONTRACTOR', 'CONTRACTOR', ''),
        ('SUBCONTRACTOR', 'SUBCONTRACTOR', ''),
        ('ARCHITECT', 'ARCHITECT', ''),
        ('STRUCTURALENGINEER', 'STRUCTURALENGINEER', ''),
        ('COSTENGINEER', 'COSTENGINEER', ''),
        ('CLIENT', 'CLIENT', ''),
        ('BUILDINGOWNER', 'BUILDINGOWNER', ''),
        ('BUILDINGOPERATOR', 'BUILDINGOPERATOR', ''),
        ('MECHANICALENGINEER', 'MECHANICALENGINEER', ''),
        ('ELECTRICALENGINEER', 'ELECTRICALENGINEER', ''),
        ('PROJECTMANAGER', 'PROJECTMANAGER', ''),
        ('FACILITIESMANAGER', 'FACILITIESMANAGER', ''),
        ('CIVILENGINEER', 'CIVILENGINEER', ''),
        ('COMMISSIONINGENGINEER', 'COMMISSIONINGENGINEER', ''),
        ('ENGINEER', 'ENGINEER', ''),
        ('OWNER', 'OWNER', ''),
        ('CONSULTANT', 'CONSULTANT', ''),
        ('CONSTRUCTIONMANAGER', 'CONSTRUCTIONMANAGER', ''),
        ('FIELDCONSTRUCTIONMANAGER', 'FIELDCONSTRUCTIONMANAGER', ''),
        ('RESELLER', 'RESELLER', ''),
        ('USERDEFINED', 'USERDEFINED', ''),
    ], name='Name')
    user_defined_role: StringProperty(name="Custom Role")
    description: StringProperty(name="Description")


class Organisation(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    roles: CollectionProperty(name="Roles", type=Role)
    active_role_index: bpy.props.IntProperty()
    addresses: CollectionProperty(name="Addresses", type=Address)
    active_address_index: bpy.props.IntProperty()


class Person(PropertyGroup):
    name: StringProperty(name="Identification")
    family_name: StringProperty(name="Family Name")
    given_name: StringProperty(name="Given Name")
    middle_names: StringProperty(name="Middle Names")
    prefix_titles: StringProperty(name="Prefixes")
    suffix_titles: StringProperty(name="Suffixes")
    roles: CollectionProperty(name="Roles", type=Role)
    active_role_index: bpy.props.IntProperty()
    addresses: CollectionProperty(name="Addresses", type=Address)
    active_address_index: bpy.props.IntProperty()


class Classification(PropertyGroup):
    name: StringProperty(name="Name")
    source: StringProperty(name="Source")
    edition: StringProperty(name="Edition")
    edition_date: StringProperty(name="Edition Date")
    description: StringProperty(name="Description")
    location: StringProperty(name="Location")
    reference_tokens: StringProperty(name="Reference Tokens")
    filename: StringProperty(name="Filename")


class ClassificationReference(PropertyGroup):
    name: StringProperty(name="Identification")
    location: StringProperty(name="Location")
    human_name: StringProperty(name="Name")
    referenced_source: StringProperty(name="Source")
    description: StringProperty(name="Description")
    sort: StringProperty(name="Sort")


class ClassificationView(PropertyGroup):
    crumbs: None
    children: None
    active_index: bpy.props.IntProperty()
    raw_data = {}

    @property
    def root(self):
        data = self.raw_data
        for crumb in self.crumbs:
            data = data['children'].get(crumb.name)
            if not data:
                raise TypeError('Cannot resolve crumb path')
        return data

    @root.setter
    def root(self, rt):
        if rt == None:
            self.crumbs.clear()
            self.children.clear()
        elif rt == '':
            if self.crumbs:
                self.crumbs.remove(len(self.crumbs)-1)
            self.children.clear()
            for child in self.root['children'].keys():
                self.children.add().name = child
        else:
            data = self.root
            if rt in data['children'].keys():
                self.crumbs.add().name = rt
                self.children.clear()
                for child in data['children'][rt]['children'].keys():
                    self.children.add().name = child

    def draw_stub(self, context, layout):
        if not self.children:
            op = layout.operator('bim.change_classification_level', text="@Toplevel")
        else:
            op = layout.operator('bim.change_classification_level', text=self.root['name'])
        op.path_sid = "%r"%self.id_data
        op.path_lst = self.path_from_id()
        op.path_itm = ''
        layout.template_list('BIM_UL_classifications',
            self.path_from_id(), self, 'children', self, 'active_index')


# Monkey-patched, just to keep registration in one block
ClassificationView.__annotations__['crumbs'] = \
    bpy.props.CollectionProperty(type=StrProperty)
ClassificationView.__annotations__['children'] = \
    bpy.props.CollectionProperty(type=StrProperty)


class BIMProperties(PropertyGroup):
    schema_dir: StringProperty(default=os.path.join(cwd ,'schema') + os.path.sep, name="Schema Directory")
    data_dir: StringProperty(default=os.path.join(cwd, 'data') + os.path.sep, name="Data Directory")
    ifc_file: StringProperty(name="IFC File")
    ifc_cache: StringProperty(name="IFC Cache")
    audit_ifc_class: EnumProperty(items=getIfcClasses, name="Audit Class")
    ifc_product: EnumProperty(items=getIfcProducts, name="Products", update=refreshClasses)
    ifc_class: EnumProperty(items=getIfcClasses, name="Class", update=refreshPredefinedTypes)
    ifc_predefined_type: EnumProperty(
        items = getIfcPredefinedTypes,
        name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
    export_schema: EnumProperty(items=[('IFC4', 'IFC4', ''), ('IFC2X3', 'IFC2X3', '')], name='IFC Schema')
    export_json_version: EnumProperty(items=[('4', '4', ''), ('5a', '5a', '')], name='IFC JSON Version')
    export_json_compact: BoolProperty(name="Export Compact IFCJSON", default=False)
    export_has_representations: BoolProperty(name="Export Representations", default=True)
    export_should_guess_quantities: BoolProperty(name="Export with Guessed Quantities", default=False)
    export_should_use_presentation_style_assignment: BoolProperty(name="Export with Presentation Style Assignment", default=False)
    import_should_ignore_site_coordinates: BoolProperty(name="Import Ignoring Site Coordinates", default=False)
    import_should_ignore_building_coordinates: BoolProperty(name="Import Ignoring Building Coordinates", default=False)
    import_should_reset_absolute_coordinates: BoolProperty(name="Import Resetting Absolute Coordinates", default=False)
    import_should_import_type_representations: BoolProperty(name="Import Type Representations", default=False)
    import_should_import_curves: BoolProperty(name="Import Curves", default=False)
    import_should_import_opening_elements: BoolProperty(name="Import Opening Elements", default=False)
    import_should_import_spaces: BoolProperty(name="Import Spaces", default=False)
    import_should_auto_set_workarounds: BoolProperty(name="Automatically Set Vendor Workarounds", default=True)
    import_should_treat_styled_item_as_material: BoolProperty(name="Import Treating Styled Item as Material", default=False)
    import_should_use_legacy: BoolProperty(name="Import with Legacy Importer", default=False)
    import_should_import_native: BoolProperty(name="Import Native Representations", default=False)
    import_should_use_cpu_multiprocessing: BoolProperty(name="Import with CPU Multiprocessing", default=False)
    import_should_import_with_profiling: BoolProperty(name="Import with Profiling", default=True)
    import_should_import_aggregates: BoolProperty(name="Import Aggregates", default=True)
    import_should_merge_aggregates: BoolProperty(name="Import and Merge Aggregates", default=False)
    import_should_merge_by_class: BoolProperty(name="Import and Merge by Class", default=False)
    import_should_merge_by_material: BoolProperty(name="Import and Merge by Material", default=False)
    import_should_merge_materials_by_colour: BoolProperty(name="Import and Merge Materials by Colour", default=False)
    import_should_clean_mesh: BoolProperty(name="Import and Clean Mesh", default=True)
    qa_reject_element_reason: StringProperty(name="Element Rejection Reason")
    person: EnumProperty(items=getPersons, name="Person")
    organisation: EnumProperty(items=getOrganisations, name="Organisation")
    people: CollectionProperty(name="People", type=Person)
    organisations: CollectionProperty(name="Organisations", type=Organisation)
    active_person_index: IntProperty(name='Active Person Index')
    active_organisation_index: IntProperty(name='Active Organisation Index')
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
    cobie_ifc_file: StringProperty(default='', name="COBie IFC File")
    diff_json_file: StringProperty(default='', name="Diff JSON File")
    diff_old_file: StringProperty(default='', name="Diff Old IFC File")
    diff_new_file: StringProperty(default='', name="Diff New IFC File")
    diff_relationships: StringProperty(default='', name="Diff Relationships")
    aggregate_class: EnumProperty(items=getIfcClasses, name="Aggregate Class")
    aggregate_name: StringProperty(name="Aggregate Name")
    classification: EnumProperty(items=getClassifications, name="Classification", update=refreshReferences)
    classifications: CollectionProperty(name="Classifications", type=Classification)
    has_model_context: BoolProperty(name="Has Model Context", default=True)
    has_plan_context: BoolProperty(name="Has Plan Context", default=False)
    model_subcontexts: CollectionProperty(name='Model Subcontexts', type=Subcontext)
    plan_subcontexts: CollectionProperty(name='Plan Subcontexts', type=Subcontext)
    available_contexts: EnumProperty(items=[('Model', 'Model', ''), ('Plan', 'Plan', '')], name="Available Contexts")
    available_subcontexts: EnumProperty(items=getSubcontexts, name="Available Subcontexts")
    available_target_views: EnumProperty(items=getTargetViews, name="Available Target Views")
    classification_references: PointerProperty(type=ClassificationView)
    pset_template_files: EnumProperty(items=getPsetTemplateFiles, name="Pset Template Files", update=refreshPropertySetTemplates)
    property_set_templates: EnumProperty(items=getPropertySetTemplates, name="Pset Template Files")
    active_property_set_template: PointerProperty(type=PropertySetTemplate)
    property_templates: CollectionProperty(name='Property Templates', type=PropertyTemplate)
    should_section_selected_objects: BoolProperty(name="Section Selected Objects", default=False)
    section_plane_colour: FloatVectorProperty(name='Temporary Section Cutaway Colour', subtype='COLOR', default=(1, 0, 0), min=0.0, max=1.0)
    ifc_import_filter: EnumProperty(items=[
        ('NONE', 'None', ''),
        ('WHITELIST', 'Whitelist', ''),
        ('BLACKLIST', 'Blacklist', ''),
        ], name='Import Filter')
    ifc_selector: StringProperty(default='', name='IFC Selector')
    csv_attributes: CollectionProperty(name='CSV Attributes', type=StrProperty)
    document_information: CollectionProperty(name='Document Information', type=DocumentInformation)
    active_document_information_index: IntProperty(name='Active Document Information Index')
    document_references: CollectionProperty(name='Document References', type=DocumentReference)
    active_document_reference_index: IntProperty(name='Active Document Reference Index')
    clash_sets: CollectionProperty(name='Clash Sets', type=ClashSet)
    active_clash_set_index: IntProperty(name='Active Clash Set Index')
    constraints: CollectionProperty(name='Constraints', type=Constraint)
    active_constraint_index: IntProperty(name='Active Constraint Index')
    ifc_patch_recipes: EnumProperty(items=getIfcPatchRecipes, name="Recipes")
    ifc_patch_input: StringProperty(default='', name='IFC Patch Input IFC')
    ifc_patch_output: StringProperty(default='', name='IFC Patch Output IFC')
    ifc_patch_args: StringProperty(default='', name='Arguments')
    qto_result: StringProperty(default='', name='Qto Result')
    area_unit: StringProperty(default='', name='IFC Area Unit')
    volume_unit: StringProperty(default='', name='IFC Volume Unit')
    override_colour: FloatVectorProperty(name='Override Colour', subtype='COLOR', default=(1, 0, 0, 1), min=0.0, max=1.0, size=4)


class BCFProperties(PropertyGroup):
    bcf_file: StringProperty(default='', name='BCF File')
    topics: CollectionProperty(name='BCF Topics', type=BcfTopic)
    active_topic_index: IntProperty(name='Active BCF Topic Index', update=refreshBcfTopic)
    viewpoints: EnumProperty(items=getBcfViewpoints, name='BCF Viewpoints')
    topic_guid: StringProperty(default='', name='Topic GUID')
    topic_type: StringProperty(default='', name='Topic Type')
    topic_status: StringProperty(default='', name='Topic Status')
    topic_priority: StringProperty(default='', name='Topic Priority')
    topic_stage: StringProperty(default='', name='Topic Stage')
    topic_creation_date: StringProperty(default='', name='Topic Date')
    topic_creation_author: StringProperty(default='', name='Topic Author')
    topic_modified_date: StringProperty(default='', name='Topic Modified Date')
    topic_modified_author: StringProperty(default='', name='Topic Modified By')
    topic_assigned_to: StringProperty(default='', name='Topic Assigned To')
    topic_due_date: StringProperty(default='', name='Topic Due Date')
    topic_description: StringProperty(default='', name='Topic Description')
    topic_labels: CollectionProperty(name='BCF Topic Labels', type=BcfTopicLabel)
    topic_files: CollectionProperty(name='BCF Topic Files', type=BcfTopicFile)
    topic_links: CollectionProperty(name='BCF Topic Links', type=BcfTopicLink)
    topic_has_snippet: BoolProperty(name='BCF Topic Has Snippet', default=False)
    topic_snippet_reference: StringProperty(name='BIM Snippet Reference')
    topic_snippet_schema: StringProperty(name='BIM Snippet Schema')
    topic_snippet_type: StringProperty(name='BIM Snippet Type')
    topic_snippet_is_external: BoolProperty(name='Is BIM Snippet External')
    topic_document_references: CollectionProperty(name='BCF Topic Document References', type=BcfTopicDocumentReference)
    topic_related_topics: CollectionProperty(name='BCF Topic Related Topics', type=BcfTopicRelatedTopic)


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

class PsetQto(PropertyGroup):
    name: StringProperty(name="Name")
    properties: CollectionProperty(name="Properties", type=Attribute)


class GlobalId(PropertyGroup):
    name: StringProperty(name="Name")


class BoundaryCondition(PropertyGroup):
    name: EnumProperty(items=getBoundaryConditionClasses, name='Boundary Type', update=refreshBoundaryConditionAttributes)
    attributes: CollectionProperty(name="Attributes", type=Attribute)


class BIMObjectProperties(PropertyGroup):
    global_ids: CollectionProperty(name="GlobalIds", type=GlobalId)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    relating_type: PointerProperty(name='Type Product', type=bpy.types.Object)
    relating_structure: PointerProperty(name='Spatial Container', type=bpy.types.Object)
    psets: CollectionProperty(name="Psets", type=PsetQto)
    qtos: CollectionProperty(name="Qtos", type=PsetQto)
    applicable_attributes: EnumProperty(items=getApplicableAttributes, name="Attribute Names")
    document_references: CollectionProperty(name="Document References", type=DocumentReference)
    active_document_reference_index: IntProperty(name='Active Document Reference Index')
    constraints: CollectionProperty(name='Constraints', type=Constraint)
    active_constraint_index: IntProperty(name='Active Constraint Index')
    classifications: CollectionProperty(name="Classifications", type=ClassificationReference)
    material_type: EnumProperty(items=getMaterialTypes, name="Material Type")
    pset_name: EnumProperty(items=getPsetNames, name='Pset Name')
    qto_name: EnumProperty(items=getQtoNames, name='Qto Name')
    has_boundary_condition: BoolProperty(name='Has Boundary Condition')
    boundary_condition: PointerProperty(name='Boundary Condition', type=BoundaryCondition)
    structural_member_connection: PointerProperty(name='Structural Member Connection', type=bpy.types.Object)
    representation_contexts: CollectionProperty(name="Representation Contexts", type=Subcontext)


class BIMMaterialProperties(PropertyGroup):
    is_external: BoolProperty(name="Has External Definition")
    location: StringProperty(name="Location")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    available_material_psets: EnumProperty(items=getAvailableMaterialPsets, name="Material Pset")
    psets: CollectionProperty(name="Psets", type=PsetQto)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    applicable_attributes: EnumProperty(items=getApplicableMaterialAttributes, name="Attribute Names")
    profile_def: EnumProperty(items=getProfileDef, name='Parameterized Profile Def', update=refreshProfileAttributes)
    profile_attributes: CollectionProperty(name='Profile Attributes', type=Attribute)


class SweptSolid(PropertyGroup):
    name: StringProperty(name="Name")
    outer_curve: StringProperty(name="Outer Curve")
    inner_curves: StringProperty(name="Inner Curves")
    extrusion: StringProperty(name="Extrusion")


class RepresentationItem(PropertyGroup):
    name: StringProperty(name="Name")
    vgroup: StringProperty(name="Vertex Group")


class BIMMeshProperties(PropertyGroup):
    is_wireframe: BoolProperty(name="Is Wireframe")
    is_native: BoolProperty(name="Is Native", default=False)
    is_swept_solid: BoolProperty(name="Is Swept Solid")
    swept_solids: CollectionProperty(name="Swept Solids", type=SweptSolid)
    is_parametric: BoolProperty(name='Is Parametric', default=False)
    presentation_layer: StringProperty(name="Presentation Layer")
    geometry_type: StringProperty(name="Geometry Type")
    representation_items: CollectionProperty(name="Representation Items", type=RepresentationItem)
    active_representation_item_index: IntProperty(name='Active Representation Item Index')
