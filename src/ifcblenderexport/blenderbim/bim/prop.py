import json
import os
import ifcopenshell
from pathlib import Path
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
products_enum = []
profiledef_enum = []
classes_enum = []
types_enum = []
availablematerialpsets_enum = []
ifcpatchrecipes_enum = []
featuresfiles_enum = []
titleblocks_enum = []
scenarios_enum = []
materialpsetnames_enum = []
psetfiles_enum = []
psettemplatefiles_enum = []
propertysettemplates_enum = []
classification_enum = []
attributes_enum = []
psetnames = {}
qtonames_enum = []
materialattributes_enum = []
materialtypes_enum = []
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


def getIfcPredefinedTypes(self, context):
    global types_enum
    file = IfcStore.get_file()
    if len(types_enum) < 1 and file:
        declaration = IfcStore.get_schema().declaration_by_name(self.ifc_class)
        for attribute in declaration.attributes():
            if attribute.name() == "PredefinedType":
                types_enum.extend([(e, e, "") for e in attribute.type_of_attribute().declared_type().enumeration_items()])
                break
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


def getIfcProducts(self, context):
    global products_enum
    file = IfcStore.get_file()
    if len(products_enum) < 1:
        products_enum.extend(
            [
                (e, e, "")
                for e in [
                    "IfcElement",
                    "IfcElementType",
                    "IfcSpatialElement",
                    "IfcGroup",
                    "IfcStructuralItem",
                    "IfcContext",
                    "IfcAnnotation",
                ]
            ]
        )
        if file.schema == "IFC2X3":
            products_enum[2] = ("IfcSpatialStructureElement", "IfcSpatialStructureElement", "")
    return products_enum


def getIfcClasses(self, context):
    global classes_enum
    file = IfcStore.get_file()
    if len(classes_enum) < 1 and file:
        declaration = IfcStore.get_schema().declaration_by_name(self.ifc_product)
        def get_classes(declaration):
            results = []
            if not declaration.is_abstract():
                results.append(declaration.name())
            for subtype in declaration.subtypes():
                results.extend(get_classes(subtype))
            return results
        classes = get_classes(declaration)
        classes_enum.extend([(c, c, "") for c in sorted(classes)])
    return classes_enum


def getAttributeEnumValues(self, context):
    return [(e, e, "") for e in json.loads(self.enum_items)]


def getProfileDef(self, context):
    global profiledef_enum
    if len(profiledef_enum) < 1:
        profiledef_enum.extend([(e, e, "") for e in getattr(schema.ifc, "IfcParameterizedProfileDef")])
    return profiledef_enum


def getPersons(self, context):
    from blenderbim.bim.module.owner.data import Data
    if not Data.is_loaded:
        Data.load()
    results = []
    for ifc_id, person in Data.people.items():
        if "Id" in person:
            identifier = person["Id"] or ""
        else:
            identifier = person["Identifier"] or ""
        results.append((str(ifc_id), identifier, ""))
    return results


def getOrganisations(self, context):
    from blenderbim.bim.module.owner.data import Data
    if not Data.is_loaded:
        Data.load()
    results = []
    for ifc_id, organisation in Data.organisations.items():
        results.append((str(ifc_id), organisation["Name"], ""))
    return results


def getIfcPatchRecipes(self, context):
    global ifcpatchrecipes_enum
    if len(ifcpatchrecipes_enum) < 1:
        ifcpatchrecipes_enum.clear()
        for filename in Path(os.path.join(cwd, "..", "libs", "site", "packages", "recipes")).glob("*.py"):
            f = str(filename.stem)
            if f == "__init__":
                continue
            ifcpatchrecipes_enum.append((f, f, ""))
    return ifcpatchrecipes_enum


def getFeaturesFiles(self, context):
    global featuresfiles_enum
    if len(featuresfiles_enum) < 1:
        featuresfiles_enum.clear()
        for filename in Path(context.scene.BIMProperties.features_dir).glob("*.feature"):
            f = str(filename.stem)
            featuresfiles_enum.append((f, f, ""))
    return featuresfiles_enum


def refreshFeaturesFiles(self, context):
    global featuresfiles_enum
    featuresfiles_enum.clear()
    getFeaturesFiles(self, context)


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


def getScenarios(self, context):
    global scenarios_enum
    if len(scenarios_enum) < 1:
        scenarios_enum.clear()
        filename = os.path.join(
            context.scene.BIMProperties.features_dir, context.scene.BIMProperties.features_file + ".feature"
        )
        with open(filename, "r") as feature_file:
            lines = feature_file.readlines()
            for line in lines:
                if "Scenario:" in line:
                    s = line.strip()[len("Scenario: ") :]
                    scenarios_enum.append((s, s, ""))
    return scenarios_enum


def refreshScenarios(self, context):
    global scenarios_enum
    scenarios_enum.clear()
    getScenarios(self, context)


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


def getClassifications(self, context):
    global classification_enum
    if len(classification_enum) < 1:
        classification_enum.clear()
        files = os.listdir(os.path.join(self.schema_dir, "classifications"))
        classification_enum.extend([(f.replace(".ifc", ""), f.replace(".ifc", ""), "") for f in files])
    return classification_enum


def refreshReferences(self, context):
    context.scene.BIMProperties.classification_references.root = None
    ClassificationView.raw_data = schema.ifc.load_classification(context.scene.BIMProperties.classification)
    context.scene.BIMProperties.classification_references.root = ""


def getPsetNames(self, context):
    global psetnames
    if "/" in context.active_object.name:
        ifc_class = context.active_object.name.split("/")[0]
        if ifc_class not in psetnames:
            psets = schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
            psetnames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
        return psetnames[ifc_class]
    return []


def getMaterialPsetNames(self, context):
    global materialpsetnames_enum
    materialpsetnames_enum.clear()
    pset_names = schema.ifc.psetqto.get_applicable_names("IfcMaterial", pset_only=True)
    materialpsetnames_enum.extend([(p, p, "") for p in pset_names])
    return materialpsetnames_enum


def getQtoNames(self, context):
    global qtonames_enum
    qtonames_enum.clear()
    if "/" in context.active_object.name and context.active_object.name.split("/")[0] in schema.ifc.elements:
        qto_names = schema.ifc.psetqto.get_applicable_names(context.active_object.name.split("/")[0], qto_only=True)
        qtonames_enum.extend([(q, q, "") for q in qto_names])
    return qtonames_enum


def getApplicableMaterialAttributes(self, context):
    global materialattributes_enum
    materialattributes_enum.clear()
    if "/" in context.active_object.name:
        ifc_schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(bpy.context.scene.BIMProperties.export_schema)
        entity = ifc_schema.declaration_by_name("IfcMaterial")
        materialattributes_enum.extend(
            [(a.name(), a.name(), "") for a in entity.all_attributes() if self.attributes.find(a.name()) == -1]
        )
    return materialattributes_enum


def refreshProfileAttributes(self, context):
    if not context.active_object:
        return
    props = context.active_object.BIMObjectProperties
    profile = props.material_set.material_profiles[props.material_set.active_material_profile_index]
    while len(profile.profile_attributes) > 0:
        profile.profile_attributes.remove(0)
    for attribute in schema.ifc.IfcParameterizedProfileDef[profile.profile]["attributes"]:
        profile_attribute = profile.profile_attributes.add()
        profile_attribute.name = attribute["name"]


def getMaterialTypes(self, context):
    global materialtypes_enum
    materialtypes_enum.clear()
    materialtypes_enum = [
        (m, m, "") for m in ["None", "IfcMaterial", "IfcMaterialConstituentSet", "IfcMaterialLayerSet", "IfcMaterialProfileSet"]
    ]
    return materialtypes_enum


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
    enum_items: StringProperty(name="Value")
    enum_value: EnumProperty(items=getAttributeEnumValues, name="Value")


class MaterialLayer(PropertyGroup):
    name: StringProperty(name="Name")
    material: PointerProperty(name="Material", type=bpy.types.Material)
    layer_thickness: FloatProperty(name="Layer Thickness")
    is_ventilated: EnumProperty(
        items=[
            ("TRUE", "True", "Is an air gap and provides air exchange from the layer to outside air"),
            ("FALSE", "False", "Is a solid material layer"),
            ("UNKNOWN", "Unknown", "Is an air gap but does not provide air exchange or not known"),
        ],
        name="Is Ventilated",
        default="FALSE",
    )
    description: StringProperty(name="Description")
    category: EnumProperty(
        items=[
            ("None", "None", ""),
            ("LoadBearing", "Load Bearing", ""),
            ("Insulation", "Insulation", ""),
            ("Finish", "Finish", ""),
            ("Custom", "Custom", ""),
        ],
        name="Category",
        default="None",
    )
    custom_category: StringProperty(name="Custom Category")
    priority: IntProperty(name="Priority")


class MaterialConstituent(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    material: PointerProperty(name="Material", type=bpy.types.Material)
    fraction: FloatProperty(name="Fraction")
    category: StringProperty(name="Category")


class MaterialProfile(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    material: PointerProperty(name="Material", type=bpy.types.Material)
    profile: EnumProperty(items=getProfileDef, name="Parameterized Profile Def", update=refreshProfileAttributes)
    profile_attributes: CollectionProperty(name="Profile Attributes", type=Attribute)
    priority: IntProperty(name="Priority")
    category: StringProperty(name="Category")


class MaterialSet(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    active_material_layer_index: IntProperty(name="Active Material Layer Index")
    material_layers: CollectionProperty(name="Material Layers", type=MaterialLayer)
    active_material_constituent_index: IntProperty(name="Active Material Constituent Index")
    material_constituents: CollectionProperty(name="Material Constituents", type=MaterialConstituent)
    active_material_profile_index: IntProperty(name="Active Material Profile Index")
    material_profiles: CollectionProperty(name="Material Profiles", type=MaterialProfile)


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


class DocumentInformation(PropertyGroup):
    name: StringProperty(name="Identification")
    human_name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    location: StringProperty(name="Location")
    purpose: StringProperty(name="Purpose")
    intended_use: StringProperty(name="Intended Use")
    scope: StringProperty(name="Scope")
    revision: StringProperty(name="Revision")
    document_owner: StringProperty(name="Owner")
    editors: StringProperty(name="Editors")
    creation_time: StringProperty(name="Created On")
    last_revision_time: StringProperty(name="Last Revised")
    electronic_format: StringProperty(name="Format")
    valid_from: StringProperty(name="Valid From")
    valid_until: StringProperty(name="Valid Until")
    confidentiality: EnumProperty(
        items=[
            ("NOTDEFINED", "NOTDEFINED", "Not defined."),
            ("PUBLIC", "PUBLIC", "Document is publicly available."),
            ("RESTRICTED", "RESTRICTED", "Document availability is restricted."),
            (
                "CONFIDENTIAL",
                "CONFIDENTIAL",
                "Document is confidential and its contents should not be revealed without permission.",
            ),
            ("PERSONAL", "PERSONAL", "Document is personal to the author."),
            ("USERDEFINED", "USERDEFINED", "Describe confidentiality elsewhere."),
        ],
        name="Confidentiality",
    )
    status: EnumProperty(
        items=[
            ("NOTDEFINED", "NOTDEFINED", "Not defined"),
            ("DRAFT", "DRAFT", "Document is a draft."),
            ("FINALDRAFT", "FINALDRAFT", "Document is a final draft."),
            ("FINAL", "FINAL", "Document is final."),
            ("REVISION", "REVISION", "Document has undergone revision."),
        ],
        name="Status",
    )


class DocumentReference(PropertyGroup):
    location: StringProperty(name="Location")
    name: StringProperty(name="Identification")
    human_name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    referenced_document: StringProperty(name="Referenced Document")


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


class Constraint(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    constraint_grade: EnumProperty(
        items=[
            (
                "HARD",
                "HARD",
                "Qualifies a constraint such that it must be followed rigidly within or at the values set.",
            ),
            ("SOFT", "SOFT", "Qualifies a constraint such that it should be followed within or at the values set."),
            (
                "ADVISORY",
                "ADVISORY",
                "Qualifies a constraint such that it is advised that it is followed within or at the values set.",
            ),
            (
                "USERDEFINED",
                "USERDEFINED",
                "A user-defined grade indicated by a separate attribute at the referencing entity.",
            ),
            ("NOTDEFINED", "NOTDEFINED", "Grade has not been specified."),
        ],
        name="Grade",
    )
    constraint_source: StringProperty(name="Source")
    user_defined_grade: StringProperty(name="Custom Grade")
    objective_qualifier: EnumProperty(
        items=[
            (
                "CODECOMPLIANCE",
                "CODECOMPLIANCE",
                "A constraint whose objective is to ensure satisfaction of a code compliance provision.",
            ),
            (
                "CODEWAIVER",
                "CODEWAIVER",
                "A constraint whose objective is to identify an agreement that code compliance requirements (the waiver) will not be enforced.",
            ),
            (
                "DESIGNINTENT",
                "DESIGNINTENT",
                "A constraint whose objective is to ensure satisfaction of a design intent provision.",
            ),
            (
                "EXTERNAL",
                "EXTERNAL",
                "A constraint whose objective is to synchronize data with an external source such as a file",
            ),
            (
                "HEALTHANDSAFETY",
                "HEALTHANDSAFETY",
                "A constraint whose objective is to ensure satisfaction of a health and safety provision.",
            ),
            (
                "MERGECONFLICT",
                "MERGECONFLICT",
                "A constraint whose objective is to resolve a conflict such as merging data from multiple sources.",
            ),
            (
                "MODELVIEW",
                "MODELVIEW",
                "A constraint whose objective is to ensure data conforms to a model view definition.",
            ),
            (
                "PARAMETER",
                "PARAMETER",
                "A constraint whose objective is to calculate a value based on other referenced values.",
            ),
            (
                "REQUIREMENT",
                "REQUIREMENT",
                "A constraint whose objective is to ensure satisfaction of a project requirement provision.",
            ),
            (
                "SPECIFICATION",
                "SPECIFICATION",
                "A constraint whose objective is to ensure satisfaction of a specification provision.",
            ),
            (
                "TRIGGERCONDITION",
                "TRIGGERCONDITION",
                "A constraint whose objective is to indicate a limiting value beyond which the condition of an object requires a particular form of attention.",
            ),
            ("USERDEFINED", "USERDEFINED", ""),
            ("NOTDEFINED", "NOTDEFINED", ""),
        ],
        name="Qualifier",
    )
    user_defined_qualifier: StringProperty(name="Custom Qualifier")


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


class Address(PropertyGroup):
    name: StringProperty(name="Name", default="IfcPostalAddress")  # Stores IfcPostalAddress or IfcTelecomAddress
    purpose: EnumProperty(
        items=[
            ("None", "None", ""),
            ("OFFICE", "OFFICE", "An office address."),
            ("SITE", "SITE", "A site address."),
            ("HOME", "HOME", "A home address."),
            ("DISTRIBUTIONPOINT", "DISTRIBUTIONPOINT", "A postal distribution point address."),
            ("USERDEFINED", "USERDEFINED", "A user defined address type to be provided."),
        ],
        name="Purpose",
    )
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
    facsimile_numbers: StringProperty(name="Facsimile Numbers")
    pager_number: StringProperty(name="Pager Number")
    electronic_mail_addresses: StringProperty(name="Emails")
    www_home_page_url: StringProperty(name="Websites")
    messaging_ids: StringProperty(name="IMs")


class Role(PropertyGroup):
    name: EnumProperty(
        items=[
            ("SUPPLIER", "SUPPLIER", ""),
            ("MANUFACTURER", "MANUFACTURER", ""),
            ("CONTRACTOR", "CONTRACTOR", ""),
            ("SUBCONTRACTOR", "SUBCONTRACTOR", ""),
            ("ARCHITECT", "ARCHITECT", ""),
            ("STRUCTURALENGINEER", "STRUCTURALENGINEER", ""),
            ("COSTENGINEER", "COSTENGINEER", ""),
            ("CLIENT", "CLIENT", ""),
            ("BUILDINGOWNER", "BUILDINGOWNER", ""),
            ("BUILDINGOPERATOR", "BUILDINGOPERATOR", ""),
            ("MECHANICALENGINEER", "MECHANICALENGINEER", ""),
            ("ELECTRICALENGINEER", "ELECTRICALENGINEER", ""),
            ("PROJECTMANAGER", "PROJECTMANAGER", ""),
            ("FACILITIESMANAGER", "FACILITIESMANAGER", ""),
            ("CIVILENGINEER", "CIVILENGINEER", ""),
            ("COMMISSIONINGENGINEER", "COMMISSIONINGENGINEER", ""),
            ("ENGINEER", "ENGINEER", ""),
            ("OWNER", "OWNER", ""),
            ("CONSULTANT", "CONSULTANT", ""),
            ("CONSTRUCTIONMANAGER", "CONSTRUCTIONMANAGER", ""),
            ("FIELDCONSTRUCTIONMANAGER", "FIELDCONSTRUCTIONMANAGER", ""),
            ("RESELLER", "RESELLER", ""),
            ("USERDEFINED", "USERDEFINED", ""),
        ],
        name="Name",
    )
    user_defined_role: StringProperty(name="Custom Role")
    description: StringProperty(name="Description")


class Organisation(PropertyGroup):
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")


class Person(PropertyGroup):
    name: StringProperty(name="Identification")
    family_name: StringProperty(name="Family Name")
    given_name: StringProperty(name="Given Name")
    middle_names: StringProperty(name="Middle Names")
    prefix_titles: StringProperty(name="Prefixes")
    suffix_titles: StringProperty(name="Suffixes")


class Classification(PropertyGroup):
    name: StringProperty(name="Name")
    source: StringProperty(name="Source")
    edition: StringProperty(name="Edition")
    edition_date: StringProperty(name="Edition Date")
    description: StringProperty(name="Description")
    location: StringProperty(name="Location")
    reference_tokens: StringProperty(name="Reference Tokens")
    data: StringProperty(name="Data")


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
            data = data["children"].get(crumb.name)
            if not data:
                raise TypeError("Cannot resolve crumb path")
        return data

    @root.setter
    def root(self, rt):
        if rt == None:
            self.crumbs.clear()
            self.children.clear()
        elif rt == "":
            if self.crumbs:
                self.crumbs.remove(len(self.crumbs) - 1)
            self.children.clear()
            for child in self.root["children"].keys():
                self.children.add().name = child
        else:
            data = self.root
            if rt in data["children"].keys():
                self.crumbs.add().name = rt
                self.children.clear()
                for child in data["children"][rt]["children"].keys():
                    self.children.add().name = child

    def draw_stub(self, context, layout):
        if not self.children:
            op = layout.operator("bim.change_classification_level", text="@Toplevel")
        else:
            op = layout.operator("bim.change_classification_level", text=self.root["name"])
        op.path_sid = "%r" % self.id_data
        op.path_lst = self.path_from_id()
        op.path_itm = ""
        layout.template_list("BIM_UL_classifications", self.path_from_id(), self, "children", self, "active_index")


# Monkey-patched, just to keep registration in one block
ClassificationView.__annotations__["crumbs"] = bpy.props.CollectionProperty(type=StrProperty)
ClassificationView.__annotations__["children"] = bpy.props.CollectionProperty(type=StrProperty)


class BIMProperties(PropertyGroup):
    schema_dir: StringProperty(default=os.path.join(cwd, "schema") + os.path.sep, name="Schema Directory")
    data_dir: StringProperty(default=os.path.join(cwd, "data") + os.path.sep, name="Data Directory")
    ifc_file: StringProperty(name="IFC File")
    ifc_cache: StringProperty(name="IFC Cache")
    audit_ifc_class: EnumProperty(items=getIfcClasses, name="Audit Class")
    ifc_product: EnumProperty(items=getIfcProducts, name="Products", update=refreshClasses)
    ifc_class: EnumProperty(items=getIfcClasses, name="Class", update=refreshPredefinedTypes)
    ifc_predefined_type: EnumProperty(items=getIfcPredefinedTypes, name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
    export_schema: EnumProperty(items=[("IFC4", "IFC4", ""), ("IFC2X3", "IFC2X3", "")], name="IFC Schema")
    export_json_version: EnumProperty(items=[("4", "4", ""), ("5a", "5a", "")], name="IFC JSON Version")
    export_json_compact: BoolProperty(name="Export Compact IFCJSON", default=False)
    export_has_representations: BoolProperty(name="Export Representations", default=True)
    export_should_guess_quantities: BoolProperty(name="Export with Guessed Quantities", default=False)
    export_should_use_presentation_style_assignment: BoolProperty(
        name="Export with Presentation Style Assignment", default=False
    )
    export_should_force_faceted_brep: BoolProperty(name="Export with Faceted Breps", default=False)
    export_should_force_triangulation: BoolProperty(name="Export with Triangulation", default=False)
    export_should_export_from_memory: BoolProperty(name="Export from Memory", default=True)
    import_should_ignore_site_coordinates: BoolProperty(name="Import Ignoring Site Coordinates", default=False)
    import_should_ignore_building_coordinates: BoolProperty(name="Import Ignoring Building Coordinates", default=False)
    import_should_reset_absolute_coordinates: BoolProperty(name="Import Resetting Absolute Coordinates", default=False)
    import_should_guess_georeferencing: BoolProperty(name="Import Guessing Georeferencing", default=False)
    import_should_import_type_representations: BoolProperty(name="Import Type Representations", default=False)
    import_should_import_curves: BoolProperty(name="Import Curves", default=False)
    import_should_import_opening_elements: BoolProperty(name="Import Opening Elements", default=False)
    import_should_import_spaces: BoolProperty(name="Import Spaces", default=False)
    import_should_auto_set_workarounds: BoolProperty(name="Automatically Set Vendor Workarounds", default=True)
    import_should_use_legacy: BoolProperty(name="Import with Legacy Importer", default=False)
    import_should_import_native: BoolProperty(name="Import Native Representations", default=False)
    import_export_should_roundtrip_native: BoolProperty(name="Roundtrip Native Representations", default=True)
    import_should_use_cpu_multiprocessing: BoolProperty(name="Import with CPU Multiprocessing", default=True)
    import_should_import_with_profiling: BoolProperty(name="Import with Profiling", default=True)
    import_should_import_aggregates: BoolProperty(name="Import Aggregates", default=True)
    import_should_merge_aggregates: BoolProperty(name="Import and Merge Aggregates", default=False)
    import_should_merge_by_class: BoolProperty(name="Import and Merge by Class", default=False)
    import_should_merge_by_material: BoolProperty(name="Import and Merge by Material", default=False)
    import_should_merge_materials_by_colour: BoolProperty(name="Import and Merge Materials by Colour", default=False)
    import_should_clean_mesh: BoolProperty(name="Import and Clean Mesh", default=True)
    import_deflection_tolerance: FloatProperty(name="Import Deflection Tolerance", default=0.001)
    import_angular_tolerance: FloatProperty(name="Import Angular Tolerance", default=0.5)
    import_should_allow_non_element_aggregates: BoolProperty(name="Import Non-Element Aggregates", default=False)
    import_should_offset_model: BoolProperty(name="Import and Offset Model", default=False)
    import_model_offset_coordinates: StringProperty(name="Model Offset Coordinates", default="0,0,0")
    qa_reject_element_reason: StringProperty(name="Element Rejection Reason")

    person: PointerProperty(type=Person)
    active_person_id: IntProperty(name="Active Person Id")
    organisation: PointerProperty(type=Organisation)
    active_organisation_id: IntProperty(name="Active Organisation Id")
    role: PointerProperty(type=Role)
    active_role_id: IntProperty(name="Active Role Id")
    address: PointerProperty(type=Address)
    active_address_id: IntProperty(name="Active Address Id")
    user_person: EnumProperty(items=getPersons, name="Person")
    user_organisation: EnumProperty(items=getOrganisations, name="Organisation")

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
    features_dir: StringProperty(default="", name="Features Directory", update=refreshFeaturesFiles)
    features_file: EnumProperty(items=getFeaturesFiles, name="Features File", update=refreshScenarios)
    scenario: EnumProperty(items=getScenarios, name="Scenario")
    diff_json_file: StringProperty(default="", name="Diff JSON File")
    diff_old_file: StringProperty(default="", name="Diff Old IFC File")
    diff_new_file: StringProperty(default="", name="Diff New IFC File")
    diff_relationships: StringProperty(default="", name="Diff Relationships")
    aggregate_class: EnumProperty(items=getIfcClasses, name="Aggregate Class")
    aggregate_name: StringProperty(name="Aggregate Name")
    classification: EnumProperty(items=getClassifications, name="Classification", update=refreshReferences)
    active_classification_name: StringProperty(name="Active Classification Name")
    classifications: CollectionProperty(name="Classifications", type=Classification)
    contexts: EnumProperty(items=getContexts, name="Contexts")
    available_contexts: EnumProperty(items=[("Model", "Model", ""), ("Plan", "Plan", "")], name="Available Contexts")
    available_subcontexts: EnumProperty(items=getSubcontexts, name="Available Subcontexts")
    available_target_views: EnumProperty(items=getTargetViews, name="Available Target Views")
    classification_references: PointerProperty(type=ClassificationView)
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
    ifc_import_filter: EnumProperty(
        items=[("NONE", "None", ""), ("WHITELIST", "Whitelist", ""), ("BLACKLIST", "Blacklist", ""),],
        name="Import Filter",
    )
    ifc_selector: StringProperty(default="", name="IFC Selector")
    csv_attributes: CollectionProperty(name="CSV Attributes", type=StrProperty)
    csv_delimiter: EnumProperty(
        items=[(";", ";", ""), (",", ",", ""), (".", ".", ""), ("CUSTOM", "Custom", ""),],
        name="IFC CSV Delimiter",
        default=";",
    )
    csv_custom_delimiter: StringProperty(default="", name="Custom Delimiter")
    document_information: CollectionProperty(name="Document Information", type=DocumentInformation)
    active_document_information_index: IntProperty(name="Active Document Information Index")
    document_references: CollectionProperty(name="Document References", type=DocumentReference)
    active_document_reference_index: IntProperty(name="Active Document Reference Index")
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
    constraints: CollectionProperty(name="Constraints", type=Constraint)
    active_constraint_index: IntProperty(name="Active Constraint Index")
    eastings: StringProperty(name="Eastings")
    northings: StringProperty(name="Northings")
    orthogonal_height: StringProperty(name="Orthogonal Height")
    ifc_patch_recipes: EnumProperty(items=getIfcPatchRecipes, name="Recipes")
    ifc_patch_input: StringProperty(default="", name="IFC Patch Input IFC")
    ifc_patch_output: StringProperty(default="", name="IFC Patch Output IFC")
    ifc_patch_args: StringProperty(default="", name="Arguments")
    qto_result: StringProperty(default="", name="Qto Result")
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
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    is_editing_attributes: BoolProperty(name="Is Editing Attributes")
    relating_object: PointerProperty(name="Aggregate", type=bpy.types.Object)
    is_editing_aggregate: BoolProperty(name="Is Editing Aggregate")
    is_editing_container: BoolProperty(name="Is Editing Container")
    relating_type: PointerProperty(name="Type", type=bpy.types.Object)
    is_editing_type: BoolProperty(name="Is Editing Type")
    relating_type: PointerProperty(name="Type Product", type=bpy.types.Object)
    relating_structure: PointerProperty(name="Spatial Container", type=bpy.types.Object)
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    psets: CollectionProperty(name="Psets", type=PsetQto)
    qtos: CollectionProperty(name="Qtos", type=PsetQto)
    document_references: CollectionProperty(name="Document References", type=DocumentReference)
    active_document_reference_index: IntProperty(name="Active Document Reference Index")
    constraints: CollectionProperty(name="Constraints", type=Constraint)
    active_constraint_index: IntProperty(name="Active Constraint Index")
    classifications: CollectionProperty(name="Classifications", type=ClassificationReference)
    material_type: EnumProperty(items=getMaterialTypes, name="Material Type")
    material: PointerProperty(name="Material", type=bpy.types.Material)
    material_set: PointerProperty(name="Material Set", type=MaterialSet)
    pset_name: EnumProperty(items=getPsetNames, name="Pset Name")
    qto_name: EnumProperty(items=getQtoNames, name="Qto Name")
    has_boundary_condition: BoolProperty(name="Has Boundary Condition")
    boundary_condition: PointerProperty(name="Boundary Condition", type=BoundaryCondition)
    structural_member_connection: PointerProperty(name="Structural Member Connection", type=bpy.types.Object)
    # Address applies to IfcSite's SiteAddress and IfcBuilding's BuildingAddress
    address: PointerProperty(name="Address", type=Address)


class BIMMaterialProperties(PropertyGroup):
    is_external: BoolProperty(name="Has External Definition")
    location: StringProperty(name="Location")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    pset_name: EnumProperty(items=getMaterialPsetNames, name="Pset Name")
    psets: CollectionProperty(name="Psets", type=PsetQto)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    applicable_attributes: EnumProperty(items=getApplicableMaterialAttributes, name="Attribute Names")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
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
