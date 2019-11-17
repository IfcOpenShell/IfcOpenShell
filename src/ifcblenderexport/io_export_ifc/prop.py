import json
import os
import csv
from pathlib import Path
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    CollectionProperty
)

cwd = os.path.dirname(os.path.realpath(__file__))

class IfcSchema():
    def __init__(self):
        with open(os.path.join(cwd, 'schema', 'ifc_elements_IFC4.json')) as f:
            self.elements = json.load(f)

ifc_schema = IfcSchema()

classes_enum = []
types_enum = []
psetnames_enum = []
psetfiles_enum = []
classification_enum = []
reference_enum = []
attributes_enum = []
documents_enum = []

def getIfcPredefinedTypes(self, context):
    global types_enum
    if len(types_enum) < 1:
        types_enum.append((' ', 'None',''))
        for name, data in ifc_schema.elements.items():
            if name != self.ifc_class.strip():
                continue
            for attribute in data['attributes']:
                if attribute['name'] != 'PredefinedType':
                    continue
                types_enum.extend([(e, e, '') for e in attribute['enum_values']])
    return types_enum


def refreshPredefinedTypes(self, context):
    global types_enum
    types_enum.clear()
    getIfcPredefinedTypes(self, context)
    # set to None
    self.ifc_predefined_type = " "


def getIfcClasses(self, context):
    global classes_enum
    if len(classes_enum) < 1:
        classes_enum.append((' ', 'None', ''))
        classes_enum.extend([(e, e, '') for e in ifc_schema.elements])
    return classes_enum


def getPsetNames(self, context):
    global psetnames_enum
    if len(psetnames_enum) < 1:
        psetnames_enum.clear()
        psetnames_enum.append((' ', 'None', ''))
        files = os.listdir(os.path.join(self.data_dir, 'pset'))
        psetnames_enum.extend([(f, f, '') for f in files])
    return psetnames_enum

def refreshPsetFiles(self, context):
    global psetfiles_enum
    psetfiles_enum.clear()
    getPsetFiles(self, context)
    # set to None
    self.pset_file = " "

def getPsetFiles(self, context):
    global psetfiles_enum
    if len(psetfiles_enum) < 1:
        psetfiles_enum.append((' ', 'None', ''))
        if not self.pset_name.strip():
            return psetfiles_enum
        files = os.listdir(os.path.join(self.data_dir, 'pset', self.pset_name.strip()))
        psetfiles_enum.extend([(f.replace('.csv', ''), f.replace('.csv', ''), '') for f in files])
    return psetfiles_enum

def getClassifications(self, context):
    global classification_enum
    if len(classification_enum) < 1:
        classification_enum.clear()
        classification_enum.append((' ', 'None', ''))
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
    # set to None
    self.reference = " "

def getReferences(self, context):
    global reference_enum
    if len(reference_enum) < 1:
        reference_enum.append((' ', 'None', ''))
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
    attributes_enum.append((' ', 'None', ''))
    if '/' in context.active_object.name \
        and context.active_object.name.split('/')[0] in ifc_schema.elements:
        attributes_enum.extend([(a['name'], a['name'], '') for a in
            ifc_schema.elements[context.active_object.name.split('/')[0]]['attributes']
            if self.attributes.find(a['name']) == -1])
    return attributes_enum

def getApplicableDocuments(self, context):
    global documents_enum
    documents_enum.clear()
    documents_enum.append((' ', 'None', ''))
    doc_path = os.path.join(context.scene.BIMProperties.data_dir, 'doc')
    for filename in Path(doc_path).glob('**/*'):
        uri = str(filename.relative_to(doc_path).as_posix())
        documents_enum.append((uri, uri, ''))
    return documents_enum


class BIMProperties(PropertyGroup):

    schema_dir: StringProperty(default=os.path.join(cwd ,'schema') + os.path.sep, name="Schema Directory")
    data_dir: StringProperty(default=os.path.join(cwd, 'data') + os.path.sep, name="Data Directory")
    ifc_class: EnumProperty(items=getIfcClasses, name="Class", update=refreshPredefinedTypes)
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
    pset_name: EnumProperty(items=getPsetNames, name="Pset Name", update=refreshPsetFiles)
    pset_file: EnumProperty(items=getPsetFiles, name="Pset File")
    has_georeferencing: BoolProperty(name="Has Georeferencing", default=False)
    global_id: StringProperty(name="GlobalId")
    features_dir: StringProperty(default='', name="Features Directory")
    diff_json_file: StringProperty(default='', name="Diff JSON File")
    aggregate_class: EnumProperty(items=getIfcClasses, name="Aggregate Class")
    aggregate_name: StringProperty(name="Aggregate Name")
    classification: EnumProperty(items=getClassifications, name="Classification", update=refreshReferences)
    reference: EnumProperty(items=getReferences, name="Reference")

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
