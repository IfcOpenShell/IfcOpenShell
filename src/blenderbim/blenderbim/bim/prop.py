import os
import bpy
import json
import importlib
import ifcopenshell
import ifcopenshell.util.pset
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
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

cwd = os.path.dirname(os.path.realpath(__file__))

materialpsetnames_enum = []
contexts_enum = []
subcontexts_enum = []
target_views_enum = []


def getAttributeEnumValues(self, context):
    # Support weird buildingSMART dictionary mappings which behave like enums
    data = json.loads(self.enum_items)
    if isinstance(data, dict):
        return [(str(k), v, "") for k, v in data.items()]
    return [(e, e, "") for e in data]


def updateSchemaDir(self, context):
    import blenderbim.bim.schema

    blenderbim.bim.schema.ifc.schema_dir = context.scene.BIMProperties.schema_dir


def updateDataDir(self, context):
    import blenderbim.bim.schema

    blenderbim.bim.schema.ifc.data_dir = context.scene.BIMProperties.data_dir


def updateIfcFile(self, context):
    if context.scene.BIMProperties.ifc_file:
        blenderbim.bim.handler.loadIfcStore(context.scene)


def getMaterialPsetNames(self, context):
    global materialpsetnames_enum
    materialpsetnames_enum.clear()
    psetqto = ifcopenshell.util.pset.get_template("IFC4")
    pset_names = psetqto.get_applicable_names("IfcMaterial", pset_only=True)
    materialpsetnames_enum.extend([(p, p, "") for p in pset_names])
    return materialpsetnames_enum


def getContexts(self, context):
    from ifcopenshell.api.context.data import Data

    if not Data.is_loaded:
        Data.load(IfcStore.get_file())
    results = []
    for ifc_id, context in Data.contexts.items():
        results.append((str(ifc_id), context["ContextType"], ""))
        for ifc_id2, subcontext in context["HasSubContexts"].items():
            results.append(
                (
                    str(ifc_id2),
                    "{}/{}/{}".format(
                        subcontext["ContextType"], subcontext["ContextIdentifier"], subcontext["TargetView"]
                    ),
                    "",
                )
            )
    return results


def getSubcontexts(self, context):
    global subcontexts_enum
    subcontexts_enum.clear()
    # TODO: allow override of generated subcontexts?
    subcontexts = [
        "Annotation",
        "Axis",
        "Box",
        "FootPrint",
        "Reference",
        "Body",
        "Clearance",
        "CoG",
        "Profile",
        "SurveyPoints",
        "Lighting",
    ]
    for subcontext in subcontexts:
        subcontexts_enum.append((subcontext, subcontext, ""))
    return subcontexts_enum


def getTargetViews(self, context):
    global target_views_enum
    target_views_enum.clear()
    target_views = [
        "GRAPH_VIEW",
        "SKETCH_VIEW",
        "MODEL_VIEW",
        "PLAN_VIEW",
        "REFLECTED_PLAN_VIEW",
        "SECTION_VIEW",
        "ELEVATION_VIEW",
        "USERDEFINED",
        "NOTDEFINED",
    ]
    for target_view in target_views:
        target_views_enum.append((target_view, target_view, ""))
    return target_views_enum


class StrProperty(PropertyGroup):
    pass


def updateAttributeStringValue(self, context):
    updateAttributeValue(self, self.string_value)


def updateAttributeBoolValue(self, context):
    updateAttributeValue(self, self.bool_value)


def updateAttributeIntValue(self, context):
    updateAttributeValue(self, self.int_value)


def updateAttributeFloatValue(self, context):
    updateAttributeValue(self, self.float_value)


def updateAttributeEnumValue(self, context):
    updateAttributeValue(self, self.enum_value)


def updateAttributeValue(self, value):
    if value:
        self.is_null = False


class Attribute(PropertyGroup):
    name: StringProperty(name="Name")
    data_type: StringProperty(name="Data Type")
    string_value: StringProperty(name="Value", update=updateAttributeStringValue)
    bool_value: BoolProperty(name="Value", update=updateAttributeBoolValue)
    int_value: IntProperty(name="Value", update=updateAttributeIntValue)
    float_value: FloatProperty(name="Value", update=updateAttributeFloatValue)
    is_null: BoolProperty(name="Is Null")
    is_optional: BoolProperty(name="Is Optional")
    enum_items: StringProperty(name="Value")
    enum_value: EnumProperty(items=getAttributeEnumValues, name="Value", update=updateAttributeEnumValue)


class BIMProperties(PropertyGroup):
    schema_dir: StringProperty(
        default=os.path.join(cwd, "schema") + os.path.sep, name="Schema Directory", update=updateSchemaDir
    )
    data_dir: StringProperty(
        default=os.path.join(cwd, "data") + os.path.sep, name="Data Directory", update=updateDataDir
    )
    ifc_file: StringProperty(name="IFC File", update=updateIfcFile)
    export_schema: EnumProperty(items=[("IFC4", "IFC4", ""), ("IFC2X3", "IFC2X3", "")], name="IFC Schema")
    last_transaction: StringProperty(name="Last Transaction")
    contexts: EnumProperty(items=getContexts, name="Contexts")
    available_contexts: EnumProperty(items=[("Model", "Model", ""), ("Plan", "Plan", "")], name="Available Contexts")
    available_subcontexts: EnumProperty(items=getSubcontexts, name="Available Subcontexts")
    available_target_views: EnumProperty(items=getTargetViews, name="Available Target Views")
    should_section_selected_objects: BoolProperty(name="Section Selected Objects", default=False)
    section_plane_colour: FloatVectorProperty(
        name="Temporary Section Cutaway Colour", subtype="COLOR", default=(1, 0, 0), min=0.0, max=1.0
    )
    area_unit: EnumProperty(
        default="SQUARE_METRE",
        items=[
            ("NANO/SQUARE_METRE", "Square Nanometre", ""),
            ("MICRO/SQUARE_METRE", "Square Micrometre", ""),
            ("MILLI/SQUARE_METRE", "Square Millimetre", ""),
            ("DECI/SQUARE_METRE", "Square Decimetre", ""),
            ("CENTI/SQUARE_METRE", "Square Centimetre", ""),
            ("SQUARE_METRE", "Square Metre", ""),
            ("KILO/SQUARE_METRE", "Square Kilometre", ""),
            ("square inch", "Square Inch", ""),
            ("square foot", "Square Foot", ""),
            ("square yard", "Square Yard", ""),
            ("square mile", "Square Mile", ""),
        ],
        name="IFC Area Unit",
    )
    volume_unit: EnumProperty(
        default="CUBIC_METRE",
        items=[
            ("NANO/CUBIC_METRE", "Cubic Nanometre", ""),
            ("MICRO/CUBIC_METRE", "Cubic Micrometre", ""),
            ("MILLI/CUBIC_METRE", "Cubic Millimetre", ""),
            ("DECI/CUBIC_METRE", "Cubic Decimetre", ""),
            ("CENTI/CUBIC_METRE", "Cubic Centimetre", ""),
            ("CUBIC_METRE", "Cubic Metre", ""),
            ("KILO/CUBIC_METRE", "Cubic Kilometre", ""),
            ("cubic inch", "Cubic Inch", ""),
            ("cubic foot", "Cubic Foot", ""),
            ("cubic yard", "Cubic Yard", ""),
        ],
        name="IFC Volume Unit",
    )
    metric_precision: FloatProperty(default=0, name="Drawing Metric Precision")
    imperial_precision: EnumProperty(
        items=[
            ("NONE", "No rounding", ""),
            ("1", 'Nearest 1"', ""),
            ("1/2", 'Nearest 1/2"', ""),
            ("1/4", 'Nearest 1/4"', ""),
            ("1/8", 'Nearest 1/8"', ""),
            ("1/16", 'Nearest 1/16"', ""),
            ("1/32", 'Nearest 1/32"', ""),
            ("1/64", 'Nearest 1/64"', ""),
            ("1/128", 'Nearest 1/128"', ""),
            ("1/256", 'Nearest 1/256"', ""),
        ],
        name="Drawing Imperial Precision",
    )
    override_colour: FloatVectorProperty(
        name="Override Colour", subtype="COLOR", default=(1, 0, 0, 1), min=0.0, max=1.0, size=4
    )


class IfcParameter(PropertyGroup):
    name: StringProperty(name="Name")
    step_id: IntProperty(name="STEP ID")
    index: IntProperty(name="Index")
    value: FloatProperty(name="Value")  # For now, only floats
    type: StringProperty(name="Type")


class PsetQto(PropertyGroup):
    name: StringProperty(name="Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    is_expanded: BoolProperty(name="Is Expanded", default=True)
    is_editable: BoolProperty(name="Is Editable")


class GlobalId(PropertyGroup):
    name: StringProperty(name="Name")


class BIMObjectProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    blender_offset_type: EnumProperty(
        items=[(o, o, "") for o in ["NONE", "OBJECT_PLACEMENT", "CARTESIAN_POINT"]],
        name="Blender Offset",
        default="NONE",
    )
    is_reassigning_class: BoolProperty(name="Is Reassigning Class")
    global_ids: CollectionProperty(name="GlobalIds", type=GlobalId)
    relating_object: PointerProperty(name="Aggregate", type=bpy.types.Object)
    is_editing_aggregate: BoolProperty(name="Is Editing Aggregate")
    psets: CollectionProperty(name="Psets", type=PsetQto)
    qtos: CollectionProperty(name="Qtos", type=PsetQto)


class BIMMaterialProperties(PropertyGroup):
    is_external: BoolProperty(name="Has External Definition")
    location: StringProperty(name="Location")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    pset_name: EnumProperty(items=getMaterialPsetNames, name="Pset Name")
    psets: CollectionProperty(name="Psets", type=PsetQto)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    # In Blender, a material object can map to an IFC material, IFC surface style, or both
    ifc_style_id: IntProperty(name="IFC Style ID")


class BIMMeshProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_native: BoolProperty(name="Is Native", default=False)
    is_swept_solid: BoolProperty(name="Is Swept Solid")
    is_parametric: BoolProperty(name="Is Parametric", default=False)
    ifc_definition: StringProperty(name="IFC Definition")
    ifc_parameters: CollectionProperty(name="IFC Parameters", type=IfcParameter)
