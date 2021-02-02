import os
from pathlib import Path
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty
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

scenarios_enum = []
featuresfiles_enum = []
classes_enum = []


def getIfcClasses(self, context): # This is a copy of the one in bim.prop (as it is used in other modules, can be refactored later)
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


def getFeaturesFiles(self, context):
        global featuresfiles_enum
        if len(featuresfiles_enum) < 1:
            featuresfiles_enum.clear()
            for filename in Path(context.scene.BimTesterProperties.features_dir).glob("*.feature"):
                f = str(filename.stem)
                featuresfiles_enum.append((f, f, ""))
        return featuresfiles_enum


def refreshFeaturesFiles(self, context):
    global featuresfiles_enum
    featuresfiles_enum.clear()
    getFeaturesFiles(self, context)


def getScenarios(self, context):
    global scenarios_enum
    if len(scenarios_enum) < 1:
        scenarios_enum.clear()

        if context.scene.BimTesterProperties.features_file != '': # To handle the error when no .feature file exists in the folder
            filename = os.path.join(
                context.scene.BimTesterProperties.features_dir, context.scene.BimTesterProperties.features_file + ".feature"
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


class BimTesterProperties(PropertyGroup):
    features_dir: StringProperty(default="", name="Features Directory", update=refreshFeaturesFiles)
    features_file: EnumProperty(items=getFeaturesFiles, name="Features File", update=refreshScenarios)
    audit_ifc_class: EnumProperty(items=getIfcClasses, name="Audit Class")
    qa_reject_element_reason: StringProperty(name="Element Rejection Reason")
    scenario: EnumProperty(items=getScenarios, name="Scenario")
    # should_load_from_memory: BoolProperty(default=False, name="Load from Memory") # can be added later to mimic the functionality in the CSV Module

    
    
    
