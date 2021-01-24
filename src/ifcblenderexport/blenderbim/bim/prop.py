import json
import os
from pathlib import Path
import importlib
import ifcopenshell
from . import export_ifc
from . import schema
from . import ifc
from . import annotation
from . import decoration
import bpy
from blenderbim.bim.ifc import IfcStore
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
    CollectionProperty,
)

cwd = os.path.dirname(os.path.realpath(__file__))

diagram_scales_enum = []
profiledef_enum = []
availablematerialpsets_enum = []
ifcpatchrecipes_enum = []
titleblocks_enum = []
materialpsetnames_enum = []
psetfiles_enum = []
psettemplatefiles_enum = []
propertysettemplates_enum = []
attributes_enum = []
materialattributes_enum = []
contexts_enum = []
subcontexts_enum = []
target_views_enum = []
sheets_enum = []
vector_styles_enum = []


@persistent
def setDefaultProperties(scene):
    if len(bpy.context.scene.DocProperties.drawing_styles) == 0:
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Technical"
        drawing_style.render_type = "VIEWPORT"
        drawing_style.raster_style = json.dumps(
            {
                "bpy.data.worlds[0].color": (1, 1, 1),
                "bpy.context.scene.render.engine": "BLENDER_WORKBENCH",
                "bpy.context.scene.render.film_transparent": False,
                "bpy.context.scene.display.shading.show_object_outline": True,
                "bpy.context.scene.display.shading.show_cavity": False,
                "bpy.context.scene.display.shading.cavity_type": "BOTH",
                "bpy.context.scene.display.shading.curvature_ridge_factor": 1,
                "bpy.context.scene.display.shading.curvature_valley_factor": 1,
                "bpy.context.scene.view_settings.view_transform": "Standard",
                "bpy.context.scene.display.shading.light": "FLAT",
                "bpy.context.scene.display.shading.color_type": "SINGLE",
                "bpy.context.scene.display.shading.single_color": (1, 1, 1),
                "bpy.context.scene.display.shading.show_shadows": False,
                "bpy.context.scene.display.shading.shadow_intensity": 0.5,
                "bpy.context.scene.display.light_direction": (0.5, 0.5, 0.5),
                "bpy.context.scene.view_settings.use_curve_mapping": False,
                "space.overlay.show_wireframes": True,
                "space.overlay.wireframe_threshold": 0,
                "space.overlay.show_floor": False,
                "space.overlay.show_axis_x": False,
                "space.overlay.show_axis_y": False,
                "space.overlay.show_axis_z": False,
                "space.overlay.show_object_origins": False,
                "space.overlay.show_relationship_lines": False,
            }
        )
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Shaded"
        drawing_style.render_type = "VIEWPORT"
        drawing_style.raster_style = json.dumps(
            {
                "bpy.data.worlds[0].color": (1, 1, 1),
                "bpy.context.scene.render.engine": "BLENDER_WORKBENCH",
                "bpy.context.scene.render.film_transparent": False,
                "bpy.context.scene.display.shading.show_object_outline": True,
                "bpy.context.scene.display.shading.show_cavity": True,
                "bpy.context.scene.display.shading.cavity_type": "BOTH",
                "bpy.context.scene.display.shading.curvature_ridge_factor": 1,
                "bpy.context.scene.display.shading.curvature_valley_factor": 1,
                "bpy.context.scene.view_settings.view_transform": "Standard",
                "bpy.context.scene.display.shading.light": "STUDIO",
                "bpy.context.scene.display.shading.color_type": "MATERIAL",
                "bpy.context.scene.display.shading.single_color": (1, 1, 1),
                "bpy.context.scene.display.shading.show_shadows": True,
                "bpy.context.scene.display.shading.shadow_intensity": 0.5,
                "bpy.context.scene.display.light_direction": (0.5, 0.5, 0.5),
                "bpy.context.scene.view_settings.use_curve_mapping": False,
                "space.overlay.show_wireframes": True,
                "space.overlay.wireframe_threshold": 0,
                "space.overlay.show_floor": False,
                "space.overlay.show_axis_x": False,
                "space.overlay.show_axis_y": False,
                "space.overlay.show_axis_z": False,
                "space.overlay.show_object_origins": False,
                "space.overlay.show_relationship_lines": False,
            }
        )
        drawing_style = bpy.context.scene.DocProperties.drawing_styles.add()
        drawing_style.name = "Blender Default"
        drawing_style.render_type = "DEFAULT"
        bpy.ops.bim.save_drawing_style(index="2")


def getDiagramScales(self, context):
    global diagram_scales_enum
    if (
        len(diagram_scales_enum) < 1
        or (bpy.context.scene.unit_settings.system == "IMPERIAL" and len(diagram_scales_enum) == 13)
        or (bpy.context.scene.unit_settings.system == "METRIC" and len(diagram_scales_enum) == 31)
    ):
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            diagram_scales_enum = [
                ("CUSTOM", "Custom", ""),
                ("1'=1'-0\"|1/1", "1'=1'-0\"", ""),
                ('6"=1\'-0"|1/6', '6"=1\'-0"', ""),
                ('1-1/2"=1\'-0"|1/8', '1-1/2"=1\'-0"', ""),
                ('1"=1\'-0"|1/12', '1"=1\'-0"', ""),
                ('3/4"=1\'-0"|1/16', '3/4"=1\'-0"', ""),
                ('1/2"=1\'-0"|1/24', '1/2"=1\'-0"', ""),
                ('3/8"=1\'-0"|1/32', '3/8"=1\'-0"', ""),
                ('1/4"=1\'-0"|1/48', '1/4"=1\'-0"', ""),
                ('3/16"=1\'-0"|1/64', '3/16"=1\'-0"', ""),
                ('1/8"=1\'-0"|1/96', '1/8"=1\'-0"', ""),
                ('3/32"=1\'-0"|1/128', '3/32"=1\'-0"', ""),
                ('1/16"=1\'-0"|1/192', '1/16"=1\'-0"', ""),
                ('1/32"=1\'-0"|1/384', '1/32"=1\'-0"', ""),
                ('1/64"=1\'-0"|1/768', '1/64"=1\'-0"', ""),
                ('1/128"=1\'-0"|1/1536', '1/128"=1\'-0"', ""),
                ("1\"=10'|1/120", "1\"=10'", ""),
                ("1\"=20'|1/240", "1\"=20'", ""),
                ("1\"=30'|1/360", "1\"=30'", ""),
                ("1\"=40'|1/480", "1\"=40'", ""),
                ("1\"=50'|1/600", "1\"=50'", ""),
                ("1\"=60'|1/720", "1\"=60'", ""),
                ("1\"=70'|1/840", "1\"=70'", ""),
                ("1\"=80'|1/960", "1\"=80'", ""),
                ("1\"=90'|1/1080", "1\"=90'", ""),
                ("1\"=100'|1/1200", "1\"=100'", ""),
                ("1\"=150'|1/1800", "1\"=150'", ""),
                ("1\"=200'|1/2400", "1\"=200'", ""),
                ("1\"=300'|1/3600", "1\"=300'", ""),
                ("1\"=400'|1/4800", "1\"=400'", ""),
                ("1\"=500'|1/6000", "1\"=500'", ""),
            ]
        else:
            diagram_scales_enum = [
                ("CUSTOM", "Custom", ""),
                ("1:5000|1/5000", "1:5000", ""),
                ("1:2000|1/2000", "1:2000", ""),
                ("1:1000|1/1000", "1:1000", ""),
                ("1:500|1/500", "1:500", ""),
                ("1:200|1/200", "1:200", ""),
                ("1:100|1/100", "1:100", ""),
                ("1:50|1/50", "1:50", ""),
                ("1:20|1/20", "1:20", ""),
                ("1:10|1/10", "1:10", ""),
                ("1:5|1/5", "1:5", ""),
                ("1:2|1/2", "1:2", ""),
                ("1:1|1/1", "1:1", ""),
            ]
    return diagram_scales_enum


def updateDrawingName(self, context):
    if not self.camera:
        return
    if self.camera.name == self.name:
        return
    self.camera.name = "IfcGroup/{}".format(self.name)
    self.camera.users_collection[0].name = self.camera.name
    self.name = self.camera.name.split("/")[1]


def getBoundaryConditionClasses(self, context):
    return [
        (c, c, "")
        for c in [
            "IfcBoundaryEdgeCondition",
            "IfcBoundaryFaceCondition",
            "IfcBoundaryNodeCondition",
            "IfcBoundaryNodeConditionWarping",
        ]
    ]


def refreshBoundaryConditionAttributes(self, context):
    while len(context.active_object.BIMObjectProperties.boundary_condition.attributes) > 0:
        context.active_object.BIMObjectProperties.boundary_condition.attributes.remove(0)
    for attribute in schema.ifc.elements[context.active_object.BIMObjectProperties.boundary_condition.name][
        "complex_attributes"
    ]:
        new_attribute = context.active_object.BIMObjectProperties.boundary_condition.attributes.add()
        new_attribute.name = attribute["name"]


def refreshActiveDrawingIndex(self, context):
    bpy.ops.bim.activate_view(drawing_index=context.scene.DocProperties.active_drawing_index)


def getAttributeEnumValues(self, context):
    return [(e, e, "") for e in json.loads(self.enum_items)]


def getIfcPatchRecipes(self, context):
    global ifcpatchrecipes_enum
    if len(ifcpatchrecipes_enum) < 1:
        ifcpatchrecipes_enum.clear()
        ifcpatch_path = Path(importlib.util.find_spec("ifcpatch").submodule_search_locations[0])
        for filename in ifcpatch_path.joinpath("recipes").glob("*.py"):
            f = str(filename.stem)
            if f == "__init__":
                continue
            ifcpatchrecipes_enum.append((f, f, ""))
    return ifcpatchrecipes_enum

def getTitleblocks(self, context):
    global titleblocks_enum
    if len(titleblocks_enum) < 1:
        titleblocks_enum.clear()
        for filename in Path(os.path.join(context.scene.BIMProperties.data_dir, "templates", "titleblocks")).glob(
            "*.svg"
        ):
            f = str(filename.stem)
            titleblocks_enum.append((f, f, ""))
    return titleblocks_enum


def refreshTitleblocks(self, context):
    global titleblocks_enum
    titleblocks_enum.clear()
    getTitleblocks(self, context)


def toggleDecorations(self, context):
    toggle = self.should_draw_decorations
    if toggle:
        decoration.DecorationsHandler.install(context)
    else:
        decoration.DecorationsHandler.uninstall()


@persistent
def toggleDecorationsOnLoad(*args):
    toggle = bpy.context.scene.DocProperties.should_draw_decorations
    if toggle:
        decoration.DecorationsHandler.install(bpy.context)
    else:
        decoration.DecorationsHandler.uninstall()


def getPsetTemplateFiles(self, context):
    global psettemplatefiles_enum
    if len(psettemplatefiles_enum) < 1:
        files = os.listdir(os.path.join(self.data_dir, "pset"))
        psettemplatefiles_enum.extend([(f.replace(".ifc", ""), f.replace(".ifc", ""), "") for f in files])
    return psettemplatefiles_enum


def refreshPropertySetTemplates(self, context):
    global propertysettemplates_enum
    propertysettemplates_enum.clear()
    getPropertySetTemplates(self, context)


def getPropertySetTemplates(self, context):
    global propertysettemplates_enum
    if len(propertysettemplates_enum) < 1:
        ifc.IfcStore.pset_template_path = os.path.join(
            context.scene.BIMProperties.data_dir, "pset", context.scene.BIMProperties.pset_template_files + ".ifc"
        )
        ifc.IfcStore.pset_template_file = ifcopenshell.open(ifc.IfcStore.pset_template_path)
        templates = ifc.IfcStore.pset_template_file.by_type("IfcPropertySetTemplate")
        propertysettemplates_enum.extend([(t.GlobalId, t.Name, "") for t in templates])
    return propertysettemplates_enum


def getMaterialPsetNames(self, context):
    global materialpsetnames_enum
    materialpsetnames_enum.clear()
    pset_names = schema.ifc.psetqto.get_applicable_names("IfcMaterial", pset_only=True)
    materialpsetnames_enum.extend([(p, p, "") for p in pset_names])
    return materialpsetnames_enum


def getContexts(self, context):
    from blenderbim.bim.module.context.data import Data
    if not Data.is_loaded:
        Data.load()
    results = []
    for ifc_id, context in Data.contexts.items():
        results.append((str(ifc_id), context["ContextType"], ""))
        for ifc_id2, subcontext in context["HasSubContexts"].items():
            results.append((str(ifc_id2), "{}/{}/{}".format(
                subcontext["ContextType"], subcontext["ContextIdentifier"], subcontext["TargetView"]), ""))
    return results


def getSubcontexts(self, context):
    global subcontexts_enum
    subcontexts_enum.clear()
    # TODO: allow override of generated subcontexts?
    subcontexts = export_ifc.IfcExportSettings().subcontexts
    for subcontext in subcontexts:
        subcontexts_enum.append((subcontext, subcontext, ""))
    return subcontexts_enum


def getTargetViews(self, context):
    global target_views_enum
    target_views_enum.clear()
    for target_view in export_ifc.IfcExportSettings().target_views:
        target_views_enum.append((target_view, target_view, ""))
    return target_views_enum


def getVectorStyles(self, context):
    global vector_styles_enum
    if len(vector_styles_enum) < 1:
        sheets_enum.clear()
        for filename in Path(os.path.join(context.scene.BIMProperties.data_dir, "styles")).glob("*.css"):
            f = str(filename.stem)
            vector_styles_enum.append((f, f, ""))
    return vector_styles_enum


def refreshFontSize(self, context):
    annotation.Annotator.resize_text(context.active_object)


class StrProperty(PropertyGroup):
    pass


class Variable(PropertyGroup):
    name: StringProperty(name="Name")
    prop_key: StringProperty(name="Property Key")


class Attribute(PropertyGroup):
    name: StringProperty(name="Name")
    data_type: StringProperty(name="Data Type")
    string_value: StringProperty(name="Value")
    bool_value: BoolProperty(name="Value")
    int_value: IntProperty(name="Value")
    float_value: FloatProperty(name="Value")
    is_null: BoolProperty(name="Is Null")
    is_optional: BoolProperty(name="Is Optional")
    enum_items: StringProperty(name="Value")
    enum_value: EnumProperty(items=getAttributeEnumValues, name="Value")


class Drawing(PropertyGroup):
    name: StringProperty(name="Name", update=updateDrawingName)
    camera: PointerProperty(name="Camera", type=bpy.types.Object)


class Schedule(PropertyGroup):
    name: StringProperty(name="Name")
    file: StringProperty(name="File")


class Sheet(PropertyGroup):
    def set_name(self, new):
        old = self.get("name")
        path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "sheets")
        if old and os.path.isfile(os.path.join(path, old + ".svg")):
            os.rename(os.path.join(path, old + ".svg"), os.path.join(path, new + ".svg"))
        self["name"] = new

    def get_name(self):
        return self.get("name")

    name: StringProperty(name="Name", get=get_name, set=set_name)
    drawings: CollectionProperty(name="Drawings", type=Drawing)
    active_drawing_index: IntProperty(name="Active Drawing Index")


class DrawingStyle(PropertyGroup):
    name: StringProperty(name="Name")
    raster_style: StringProperty(name="Raster Style")
    render_type: EnumProperty(
        items=[("NONE", "None", ""), ("DEFAULT", "Default", ""), ("VIEWPORT", "Viewport", ""),],
        name="Render Type",
        default="VIEWPORT",
    )
    vector_style: EnumProperty(items=getVectorStyles, name="Vector Style")
    include_query: StringProperty(name="Include Query")
    exclude_query: StringProperty(name="Exclude Query")
    attributes: CollectionProperty(name="Attributes", type=StrProperty)


class DocProperties(PropertyGroup):
    should_recut: BoolProperty(name="Should Recut", default=True)
    should_recut_selected: BoolProperty(name="Should Recut Selected Only", default=False)
    should_extract: BoolProperty(name="Should Extract", default=True)
    drawings: CollectionProperty(name="Drawings", type=Drawing)
    active_drawing_index: IntProperty(name="Active Drawing Index", update=refreshActiveDrawingIndex)
    current_drawing_index: IntProperty(name="Current Drawing Index")
    schedules: CollectionProperty(name="Schedules", type=Schedule)
    active_schedule_index: IntProperty(name="Active Schedule Index")
    titleblock: EnumProperty(items=getTitleblocks, name="Titleblock", update=refreshTitleblocks)
    sheets: CollectionProperty(name="Sheets", type=Sheet)
    active_sheet_index: IntProperty(name="Active Sheet Index")
    ifc_files: CollectionProperty(name="IFCs", type=StrProperty)
    drawing_styles: CollectionProperty(name="Drawing Styles", type=DrawingStyle)
    should_draw_decorations: BoolProperty(name="Should Draw Decorations", update=toggleDecorations)
    decorations_colour: FloatVectorProperty(name="Decorations Colour", subtype="COLOR", default=(1, 0, 0, 1),
                                            min=0.0, max=1.0, size=4)


class BIMCameraProperties(PropertyGroup):
    view_name: StringProperty(name="View Name")
    target_view: EnumProperty(
        items=[
            ("PLAN_VIEW", "PLAN_VIEW", ""),
            ("ELEVATION_VIEW", "ELEVATION_VIEW", ""),
            ("SECTION_VIEW", "SECTION_VIEW", ""),
            ("REFLECTED_PLAN_VIEW", "REFLECTED_PLAN_VIEW", ""),
            ("MODEL_VIEW", "MODEL_VIEW", ""),
        ],
        name="Target View",
        default="PLAN_VIEW",
    )
    diagram_scale: EnumProperty(items=getDiagramScales, name="Drawing Scale")
    custom_diagram_scale: StringProperty(name="Custom Scale")
    raster_x: IntProperty(name="Raster X", default=1000)
    raster_y: IntProperty(name="Raster Y", default=1000)
    is_nts: BoolProperty(name="Is NTS")
    cut_objects: EnumProperty(
        items=[
            (
                ".IfcWall|.IfcSlab|.IfcCurtainWall|.IfcStair|.IfcStairFlight|.IfcColumn|.IfcBeam|.IfcMember|.IfcCovering|.IfcSpace",
                "Overall Plan / Section",
                "",
            ),
            (".IfcElement", "Detail Drawing", ""),
            ("CUSTOM", "Custom", ""),
        ],
        name="Cut Objects",
    )
    cut_objects_custom: StringProperty(name="Custom Cut")
    active_drawing_style_index: IntProperty(name="Active Drawing Style Index")


class BIMTextProperties(PropertyGroup):
    font_size: EnumProperty(
        items=[
            ("1.8", "1.8 - Small", ""),
            ("2.5", "2.5 - Regular", ""),
            ("3.5", "3.5 - Large", ""),
            ("5.0", "5.0 - Header", ""),
            ("7.0", "7.0 - Title", ""),
        ],
        update=refreshFontSize,
        name="Font Size",
    )
    symbol: EnumProperty(
        items=[("None", "None", ""), ("rectangle-tag", "Rectangle Tag", ""), ("door-tag", "Door Tag", ""),],
        update=refreshFontSize,
        name="Symbol",
    )
    related_element: PointerProperty(name="Related Element", type=bpy.types.Object)
    variables: CollectionProperty(name="Variables", type=Variable)


class ClashSource(PropertyGroup):
    name: StringProperty(name="File")
    selector: StringProperty(name="Selector")
    mode: EnumProperty(
        items=[
            ("i", "Include", "Only the selected objects are included for clashing"),
            ("e", "Exclude", "All objects except the selected objects are included for clashing"),
        ],
        name="Mode",
    )


class ClashSet(PropertyGroup):
    name: StringProperty(name="Name")
    tolerance: FloatProperty(name="Tolerance")
    a: CollectionProperty(name="Group A", type=ClashSource)
    b: CollectionProperty(name="Group B", type=ClashSource)


class PresentationLayer(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    identifier: StringProperty(name="Identifier")
    layer_on: BoolProperty(name="LayerOn", default=True)
    layer_frozen: BoolProperty(name="LayerFrozen", default=False)
    layer_blocked: BoolProperty(name="LayerBlocked", default=False)

class SmartClashGroup(PropertyGroup):
    number: StringProperty(name="Number")
    global_ids: CollectionProperty(name="GlobalIDs", type=StrProperty)


class PropertySetTemplate(PropertyGroup):
    global_id: StringProperty(name="Global ID")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    template_type: EnumProperty(
        items=[
            (
                "PSET_TYPEDRIVENONLY",
                "Pset - IfcTypeObject",
                "The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.",
            ),
            (
                "PSET_TYPEDRIVENOVERRIDE",
                "Pset - IfcTypeObject - Override",
                "The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.",
            ),
            (
                "PSET_OCCURRENCEDRIVEN",
                "Pset - IfcObject",
                "The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcObject.",
            ),
            (
                "PSET_PERFORMANCEDRIVEN",
                "Pset - IfcPerformanceHistory",
                "The property sets defined by this IfcPropertySetTemplate can only be assigned to IfcPerformanceHistory.",
            ),
            (
                "QTO_TYPEDRIVENONLY",
                "Qto - IfcTypeObject",
                "The element quantity defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.",
            ),
            (
                "QTO_TYPEDRIVENOVERRIDE",
                "Qto - IfcTypeObject - Override",
                "The element quantity defined by this IfcPropertySetTemplate can be assigned to subtypes of IfcTypeObject and can be overridden by an element quantity with same name at subtypes of IfcObject.",
            ),
            (
                "QTO_OCCURRENCEDRIVEN",
                "Qto - IfcObject",
                "The element quantity defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcObject.",
            ),
            (
                "NOTDEFINED",
                "Not defined",
                "No restriction provided, the property sets defined by this IfcPropertySetTemplate can be assigned to any entity, if not otherwise restricted by the ApplicableEntity attribute.",
            ),
        ],
        name="Template Type",
    )
    applicable_entity: StringProperty(name="Applicable Entity")


class PropertyTemplate(PropertyGroup):
    global_id: StringProperty(name="Global ID")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    primary_measure_type: EnumProperty(
        items=[
            (x, x, "")
            for x in [
                "IfcInteger",
                "IfcReal",
                "IfcBoolean",
                "IfcIdentifier",
                "IfcText",
                "IfcLabel",
                "IfcLogical",
                "IfcDateTime",
                "IfcDate",
                "IfcTime",
                "IfcDuration",
                "IfcTimeStamp",
                "IfcPositiveInteger",
                "IfcBinary",
                "IfcVolumeMeasure",
                "IfcTimeMeasure",
                "IfcThermodynamicTemperatureMeasure",
                "IfcSolidAngleMeasure",
                "IfcPositiveRatioMeasure",
                "IfcRatioMeasure",
                "IfcPositivePlaneAngleMeasure",
                "IfcPlaneAngleMeasure",
                "IfcParameterValue",
                "IfcNumericMeasure",
                "IfcMassMeasure",
                "IfcPositiveLengthMeasure",
                "IfcLengthMeasure",
                "IfcElectricCurrentMeasure",
                "IfcDescriptiveMeasure",
                "IfcCountMeasure",
                "IfcContextDependentMeasure",
                "IfcAreaMeasure",
                "IfcAmountOfSubstanceMeasure",
                "IfcLuminousIntensityMeasure",
                "IfcNormalisedRatioMeasure",
                "IfcComplexNumber",
                "IfcNonNegativeLengthMeasure",
                "IfcAbsorbedDoseMeasure",
                "IfcAccelerationMeasure",
                "IfcAngularVelocityMeasure",
                "IfcAreaDensityMeasure",
                "IfcCompoundPlaneAngleMeasure",
                "IfcCurvatureMeasure",
                "IfcDoseEquivalentMeasure",
                "IfcDynamicViscosityMeasure",
                "IfcElectricCapacitanceMeasure",
                "IfcElectricChargeMeasure",
                "IfcElectricConductanceMeasure",
                "IfcElectricResistanceMeasure",
                "IfcElectricVoltageMeasure",
                "IfcEnergyMeasure",
                "IfcForceMeasure",
                "IfcFrequencyMeasure",
                "IfcHeatFluxDensityMeasure",
                "IfcHeatingValueMeasure",
                "IfcIlluminanceMeasure",
                "IfcInductanceMeasure",
                "IfcIntegerCountRateMeasure",
                "IfcIonConcentrationMeasure",
                "IfcIsothermalMoistureCapacityMeasure",
                "IfcKinematicViscosityMeasure",
                "IfcLinearForceMeasure",
                "IfcLinearMomentMeasure",
                "IfcLinearStiffnessMeasure",
                "IfcLinearVelocityMeasure",
                "IfcLuminousFluxMeasure",
                "IfcLuminousIntensityDistributionMeasure",
                "IfcMagneticFluxDensityMeasure",
                "IfcMagneticFluxMeasure",
                "IfcMassDensityMeasure",
                "IfcMassFlowRateMeasure",
                "IfcMassPerLengthMeasure",
                "IfcModulusOfElasticityMeasure",
                "IfcModulusOfLinearSubgradeReactionMeasure",
                "IfcModulusOfRotationalSubgradeReactionMeasure",
                "IfcModulusOfSubgradeReactionMeasure",
                "IfcMoistureDiffusivityMeasure",
                "IfcMolecularWeightMeasure",
                "IfcMomentOfInertiaMeasure",
                "IfcMonetaryMeasure",
                "IfcPHMeasure",
                "IfcPlanarForceMeasure",
                "IfcPowerMeasure",
                "IfcPressureMeasure",
                "IfcRadioActivityMeasure",
                "IfcRotationalFrequencyMeasure",
                "IfcRotationalMassMeasure",
                "IfcRotationalStiffnessMeasure",
                "IfcSectionModulusMeasure",
                "IfcSectionalAreaIntegralMeasure",
                "IfcShearModulusMeasure",
                "IfcSoundPowerLevelMeasure",
                "IfcSoundPowerMeasure",
                "IfcSoundPressureLevelMeasure",
                "IfcSoundPressureMeasure",
                "IfcSpecificHeatCapacityMeasure",
                "IfcTemperatureGradientMeasure",
                "IfcTemperatureRateOfChangeMeasure",
                "IfcThermalAdmittanceMeasure",
                "IfcThermalConductivityMeasure",
                "IfcThermalExpansionCoefficientMeasure",
                "IfcThermalResistanceMeasure",
                "IfcThermalTransmittanceMeasure",
                "IfcTorqueMeasure",
                "IfcVaporPermeabilityMeasure",
                "IfcVolumetricFlowRateMeasure",
                "IfcWarpingConstantMeasure",
                "IfcWarpingMomentMeasure",
            ]
        ],
        name="Primary Measure Type",
    )


class BIMProperties(PropertyGroup):
    schema_dir: StringProperty(default=os.path.join(cwd, "schema") + os.path.sep, name="Schema Directory")
    data_dir: StringProperty(default=os.path.join(cwd, "data") + os.path.sep, name="Data Directory")
    ifc_file: StringProperty(name="IFC File")
    export_schema: EnumProperty(items=[("IFC4", "IFC4", ""), ("IFC2X3", "IFC2X3", "")], name="IFC Schema")
    has_library: BoolProperty(name="Has Project Library", default=False)
    contexts: EnumProperty(items=getContexts, name="Contexts")
    available_contexts: EnumProperty(items=[("Model", "Model", ""), ("Plan", "Plan", "")], name="Available Contexts")
    available_subcontexts: EnumProperty(items=getSubcontexts, name="Available Subcontexts")
    available_target_views: EnumProperty(items=getTargetViews, name="Available Target Views")
    pset_template_files: EnumProperty(
        items=getPsetTemplateFiles, name="Pset Template Files", update=refreshPropertySetTemplates
    )
    property_set_templates: EnumProperty(items=getPropertySetTemplates, name="Pset Template Files")
    active_property_set_template: PointerProperty(type=PropertySetTemplate)
    property_templates: CollectionProperty(name="Property Templates", type=PropertyTemplate)
    should_section_selected_objects: BoolProperty(name="Section Selected Objects", default=False)
    section_plane_colour: FloatVectorProperty(
        name="Temporary Section Cutaway Colour", subtype="COLOR", default=(1, 0, 0), min=0.0, max=1.0
    )
    blender_clash_set_a: CollectionProperty(name="Blender Clash Set A", type=StrProperty)
    blender_clash_set_b: CollectionProperty(name="Blender Clash Set B", type=StrProperty)
    clash_sets: CollectionProperty(name="Clash Sets", type=ClashSet)
    should_create_clash_snapshots: BoolProperty(name="Create Snapshots", default=True)
    clash_results_path: StringProperty(name="Clash Results Path")
    smart_grouped_clashes_path: StringProperty(name="Smart Grouped Clashes Path")
    active_clash_set_index: IntProperty(name="Active Clash Set Index")
    smart_clash_groups: CollectionProperty(name="Smart Clash Groups", type=SmartClashGroup)
    active_smart_group_index: IntProperty(name="Active Smart Group Index")
    smart_clash_grouping_max_distance: IntProperty(name="Smart Clash Grouping Max Distance", default=3, soft_min=1, soft_max=10)
    ifc_patch_recipes: EnumProperty(items=getIfcPatchRecipes, name="Recipes")
    ifc_patch_input: StringProperty(default="", name="IFC Patch Input IFC")
    ifc_patch_output: StringProperty(default="", name="IFC Patch Output IFC")
    ifc_patch_args: StringProperty(default="", name="Arguments")
    area_unit: EnumProperty(
        default="SQUARE_METRE",
        items=[
            ("MILLI/SQUARE_METRE", "Square Millimetre", ""),
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
            ("MILLI/CUBIC_METRE", "Cubic Millimetre", ""),
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
    active_presentation_layer_index: IntProperty(name="Active Presentation Layer Index")
    presentation_layers: CollectionProperty(name="Presentation Layers", type=PresentationLayer)


class BIMLibrary(PropertyGroup):
    name: StringProperty(name="Name")
    version: StringProperty(name="Version")
    publisher: StringProperty(name="Publisher")
    version_date: StringProperty(name="Version Date")
    location: StringProperty(name="Location")
    description: StringProperty(name="Description")


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


class BoundaryCondition(PropertyGroup):
    name: EnumProperty(
        items=getBoundaryConditionClasses, name="Boundary Type", update=refreshBoundaryConditionAttributes
    )
    attributes: CollectionProperty(name="Attributes", type=Attribute)


class BIMObjectProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_reassigning_class: BoolProperty(name="Is Reassigning Class")
    global_ids: CollectionProperty(name="GlobalIds", type=GlobalId)
    relating_object: PointerProperty(name="Aggregate", type=bpy.types.Object)
    is_editing_aggregate: BoolProperty(name="Is Editing Aggregate")
    is_editing_container: BoolProperty(name="Is Editing Container")
    relating_type: PointerProperty(name="Type", type=bpy.types.Object)
    is_editing_type: BoolProperty(name="Is Editing Type")
    relating_type: PointerProperty(name="Type Product", type=bpy.types.Object)
    relating_structure: PointerProperty(name="Spatial Container", type=bpy.types.Object)
    psets: CollectionProperty(name="Psets", type=PsetQto)
    qtos: CollectionProperty(name="Qtos", type=PsetQto)
    has_boundary_condition: BoolProperty(name="Has Boundary Condition")
    boundary_condition: PointerProperty(name="Boundary Condition", type=BoundaryCondition)
    structural_member_connection: PointerProperty(name="Structural Member Connection", type=bpy.types.Object)


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


class SweptSolid(PropertyGroup):
    name: StringProperty(name="Name")
    outer_curve: StringProperty(name="Outer Curve")
    inner_curves: StringProperty(name="Inner Curves")
    extrusion: StringProperty(name="Extrusion")


class RepresentationItem(PropertyGroup):
    name: StringProperty(name="Name")
    vgroup: StringProperty(name="Vertex Group")


class ItemSlotMap(PropertyGroup):
    name: StringProperty(name="Item Element ID")
    slot_index: IntProperty(name="Material Slot Index")


class BIMMeshProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_native: BoolProperty(name="Is Native", default=False)
    is_swept_solid: BoolProperty(name="Is Swept Solid")
    swept_solids: CollectionProperty(name="Swept Solids", type=SweptSolid)
    is_parametric: BoolProperty(name="Is Parametric", default=False)
    ifc_definition: StringProperty(name="IFC Definition")
    ifc_parameters: CollectionProperty(name="IFC Parameters", type=IfcParameter)
    active_representation_item_index: IntProperty(name="Active Representation Item Index")
    presentation_layer_index: IntProperty(name="Presentation Layer Index", default=-1)
    ifc_item_ids: CollectionProperty(name="IFC Item IDs", type=ItemSlotMap)
