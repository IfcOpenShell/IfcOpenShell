import bpy
from blenderbim.bim.prop import StrProperty, Attribute
from ifcopenshell.api.classification.data import Data
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)

classification_enum = []


def purge():
    global classification_enum
    classification_enum = []


def getClassifications(self, context):
    global classification_enum
    if len(classification_enum) < 1:
        classification_enum.clear()
        classification_enum.extend([(str(i), n, "") for i, n in Data.library_classifications.items()])
        if classification_enum:
            getReferences(self, context, parent_id=int(classification_enum[0][0]))
    return classification_enum


def updateClassification(self, context):
    getReferences(self, context, parent_id=int(self.available_classifications))


def getReferences(self, context, parent_id=None):
    props = context.scene.BIMClassificationProperties
    while len(props.available_library_references) > 0:
        props.available_library_references.remove(0)
    for reference in Data.library_file.by_id(parent_id).HasReferences:
        new = props.available_library_references.add()
        new.identification = reference.Identification or ""
        new.name = reference.Name or ""
        new.ifc_definition_id = reference.id()
        new.has_references = bool(reference.HasReferences)
        new.referenced_source
    if reference.ReferencedSource.is_a("IfcClassificationReference"):
        props.active_library_referenced_source = reference.ReferencedSource.ReferencedSource.id()
    else:
        props.active_library_referenced_source = 0


class ClassificationReference(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_references: BoolProperty(name="Has References")
    referenced_source: IntProperty(name="IFC Definition ID")


class BIMClassificationProperties(PropertyGroup):
    available_classifications: EnumProperty(
        items=getClassifications, name="Available Classifications", update=updateClassification
    )
    classification_attributes: CollectionProperty(name="Classification Attributes", type=Attribute)
    active_classification_id: IntProperty(name="Active Classification Id")
    available_library_references: CollectionProperty(name="Available Library References", type=ClassificationReference)
    active_library_referenced_source: IntProperty(name="Active Library Referenced Source")
    active_library_reference_index: IntProperty(name="Active Library Reference Index")


class BIMClassificationReferenceProperties(PropertyGroup):
    reference_attributes: CollectionProperty(name="Reference Attributes", type=Attribute)
    active_reference_id: IntProperty(name="Active Reference Id")
