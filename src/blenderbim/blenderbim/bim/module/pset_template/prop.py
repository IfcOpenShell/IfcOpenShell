import os
import bpy
import ifcopenshell
from blenderbim.bim.prop import StrProperty, Attribute
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
from ifcopenshell.api.pset_template.data import Data


psettemplatefiles_enum = []
psettemplates_enum = []


def purge():
    global psettemplatefiles_enum
    global psettemplates_enum
    psettemplatefiles_enum = []
    psettemplates_enum = []


def updatePsetTemplateFiles(self, context):
    global psettemplates_enum
    IfcStore.pset_template_path = os.path.join(
        context.scene.BIMProperties.data_dir,
        "pset",
        context.scene.BIMPsetTemplateProperties.pset_template_files + ".ifc",
    )
    IfcStore.pset_template_file = ifcopenshell.open(IfcStore.pset_template_path)
    updatePsetTemplates(self, context)


def getPsetTemplateFiles(self, context):
    global psettemplatefiles_enum
    if len(psettemplatefiles_enum) < 1:
        files = os.listdir(os.path.join(context.scene.BIMProperties.data_dir, "pset"))
        psettemplatefiles_enum.extend([(f.replace(".ifc", ""), f.replace(".ifc", ""), "") for f in files])
    return psettemplatefiles_enum


def updatePsetTemplates(self, context):
    global psettemplates_enum
    psettemplates_enum.clear()
    getPsetTemplates(self, context)


def getPsetTemplates(self, context):
    global psettemplates_enum
    if len(psettemplates_enum) < 1:
        if not IfcStore.pset_template_file:
            IfcStore.pset_template_path = os.path.join(
                context.scene.BIMProperties.data_dir,
                "pset",
                context.scene.BIMPsetTemplateProperties.pset_template_files + ".ifc",
            )
            IfcStore.pset_template_file = ifcopenshell.open(IfcStore.pset_template_path)
        templates = IfcStore.pset_template_file.by_type("IfcPropertySetTemplate")
        psettemplates_enum.extend([(str(t.id()), t.Name, "") for t in templates])
        Data.load(IfcStore.pset_template_file)
    return psettemplates_enum


class PsetTemplate(PropertyGroup):
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


class PropTemplate(PropertyGroup):
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


class BIMPsetTemplateProperties(PropertyGroup):
    pset_template_files: EnumProperty(
        items=getPsetTemplateFiles, name="Pset Template Files", update=updatePsetTemplateFiles
    )
    pset_templates: EnumProperty(items=getPsetTemplates, name="Pset Template Files")
    active_pset_template_id: IntProperty(name="Active Pset Template Id")
    active_prop_template_id: IntProperty(name="Active Prop Template Id")
    active_pset_template: PointerProperty(type=PsetTemplate)
    active_prop_template: PointerProperty(type=PropTemplate)
