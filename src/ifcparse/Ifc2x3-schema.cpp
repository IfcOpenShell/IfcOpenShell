/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

/********************************************************************************
 *                                                                              *
 * This file has been generated from IFC2X3_TC1.exp. Do not make modifications  *
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#ifndef USE_IFC4

#include "../ifcparse/IfcSchema.h"

void populate() {
    declaration* IfcAbsorbedDoseMeasure_type = new type_declaration("IfcAbsorbedDoseMeasure", new simple_type(simple_type::real_type));
    declaration* IfcAccelerationMeasure_type = new type_declaration("IfcAccelerationMeasure", new simple_type(simple_type::real_type));
    declaration* IfcAmountOfSubstanceMeasure_type = new type_declaration("IfcAmountOfSubstanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcAngularVelocityMeasure_type = new type_declaration("IfcAngularVelocityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcAreaMeasure_type = new type_declaration("IfcAreaMeasure", new simple_type(simple_type::real_type));
    declaration* IfcBoolean_type = new type_declaration("IfcBoolean", new simple_type(simple_type::boolean_type));
    declaration* IfcComplexNumber_type = new type_declaration("IfcComplexNumber", new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    declaration* IfcCompoundPlaneAngleMeasure_type = new type_declaration("IfcCompoundPlaneAngleMeasure", new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    declaration* IfcContextDependentMeasure_type = new type_declaration("IfcContextDependentMeasure", new simple_type(simple_type::real_type));
    declaration* IfcCountMeasure_type = new type_declaration("IfcCountMeasure", new simple_type(simple_type::number_type));
    declaration* IfcCurvatureMeasure_type = new type_declaration("IfcCurvatureMeasure", new simple_type(simple_type::real_type));
    declaration* IfcDayInMonthNumber_type = new type_declaration("IfcDayInMonthNumber", new simple_type(simple_type::integer_type));
    declaration* IfcDaylightSavingHour_type = new type_declaration("IfcDaylightSavingHour", new simple_type(simple_type::integer_type));
    declaration* IfcDescriptiveMeasure_type = new type_declaration("IfcDescriptiveMeasure", new simple_type(simple_type::string_type));
    declaration* IfcDimensionCount_type = new type_declaration("IfcDimensionCount", new simple_type(simple_type::integer_type));
    declaration* IfcDoseEquivalentMeasure_type = new type_declaration("IfcDoseEquivalentMeasure", new simple_type(simple_type::real_type));
    declaration* IfcDynamicViscosityMeasure_type = new type_declaration("IfcDynamicViscosityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcElectricCapacitanceMeasure_type = new type_declaration("IfcElectricCapacitanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcElectricChargeMeasure_type = new type_declaration("IfcElectricChargeMeasure", new simple_type(simple_type::real_type));
    declaration* IfcElectricConductanceMeasure_type = new type_declaration("IfcElectricConductanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcElectricCurrentMeasure_type = new type_declaration("IfcElectricCurrentMeasure", new simple_type(simple_type::real_type));
    declaration* IfcElectricResistanceMeasure_type = new type_declaration("IfcElectricResistanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcElectricVoltageMeasure_type = new type_declaration("IfcElectricVoltageMeasure", new simple_type(simple_type::real_type));
    declaration* IfcEnergyMeasure_type = new type_declaration("IfcEnergyMeasure", new simple_type(simple_type::real_type));
    declaration* IfcFontStyle_type = new type_declaration("IfcFontStyle", new simple_type(simple_type::string_type));
    declaration* IfcFontVariant_type = new type_declaration("IfcFontVariant", new simple_type(simple_type::string_type));
    declaration* IfcFontWeight_type = new type_declaration("IfcFontWeight", new simple_type(simple_type::string_type));
    declaration* IfcForceMeasure_type = new type_declaration("IfcForceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcFrequencyMeasure_type = new type_declaration("IfcFrequencyMeasure", new simple_type(simple_type::real_type));
    declaration* IfcGloballyUniqueId_type = new type_declaration("IfcGloballyUniqueId", new simple_type(simple_type::string_type));
    declaration* IfcHeatFluxDensityMeasure_type = new type_declaration("IfcHeatFluxDensityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcHeatingValueMeasure_type = new type_declaration("IfcHeatingValueMeasure", new simple_type(simple_type::real_type));
    declaration* IfcHourInDay_type = new type_declaration("IfcHourInDay", new simple_type(simple_type::integer_type));
    declaration* IfcIdentifier_type = new type_declaration("IfcIdentifier", new simple_type(simple_type::string_type));
    declaration* IfcIlluminanceMeasure_type = new type_declaration("IfcIlluminanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcInductanceMeasure_type = new type_declaration("IfcInductanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcInteger_type = new type_declaration("IfcInteger", new simple_type(simple_type::integer_type));
    declaration* IfcIntegerCountRateMeasure_type = new type_declaration("IfcIntegerCountRateMeasure", new simple_type(simple_type::integer_type));
    declaration* IfcIonConcentrationMeasure_type = new type_declaration("IfcIonConcentrationMeasure", new simple_type(simple_type::real_type));
    declaration* IfcIsothermalMoistureCapacityMeasure_type = new type_declaration("IfcIsothermalMoistureCapacityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcKinematicViscosityMeasure_type = new type_declaration("IfcKinematicViscosityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLabel_type = new type_declaration("IfcLabel", new simple_type(simple_type::string_type));
    declaration* IfcLengthMeasure_type = new type_declaration("IfcLengthMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLinearForceMeasure_type = new type_declaration("IfcLinearForceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLinearMomentMeasure_type = new type_declaration("IfcLinearMomentMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLinearStiffnessMeasure_type = new type_declaration("IfcLinearStiffnessMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLinearVelocityMeasure_type = new type_declaration("IfcLinearVelocityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLogical_type = new type_declaration("IfcLogical", new simple_type(simple_type::logical_type));
    declaration* IfcLuminousFluxMeasure_type = new type_declaration("IfcLuminousFluxMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLuminousIntensityDistributionMeasure_type = new type_declaration("IfcLuminousIntensityDistributionMeasure", new simple_type(simple_type::real_type));
    declaration* IfcLuminousIntensityMeasure_type = new type_declaration("IfcLuminousIntensityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMagneticFluxDensityMeasure_type = new type_declaration("IfcMagneticFluxDensityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMagneticFluxMeasure_type = new type_declaration("IfcMagneticFluxMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMassDensityMeasure_type = new type_declaration("IfcMassDensityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMassFlowRateMeasure_type = new type_declaration("IfcMassFlowRateMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMassMeasure_type = new type_declaration("IfcMassMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMassPerLengthMeasure_type = new type_declaration("IfcMassPerLengthMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMinuteInHour_type = new type_declaration("IfcMinuteInHour", new simple_type(simple_type::integer_type));
    declaration* IfcModulusOfElasticityMeasure_type = new type_declaration("IfcModulusOfElasticityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", new simple_type(simple_type::real_type));
    declaration* IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", new simple_type(simple_type::real_type));
    declaration* IfcModulusOfSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfSubgradeReactionMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMoistureDiffusivityMeasure_type = new type_declaration("IfcMoistureDiffusivityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMolecularWeightMeasure_type = new type_declaration("IfcMolecularWeightMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMomentOfInertiaMeasure_type = new type_declaration("IfcMomentOfInertiaMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMonetaryMeasure_type = new type_declaration("IfcMonetaryMeasure", new simple_type(simple_type::real_type));
    declaration* IfcMonthInYearNumber_type = new type_declaration("IfcMonthInYearNumber", new simple_type(simple_type::integer_type));
    declaration* IfcNumericMeasure_type = new type_declaration("IfcNumericMeasure", new simple_type(simple_type::number_type));
    declaration* IfcPHMeasure_type = new type_declaration("IfcPHMeasure", new simple_type(simple_type::real_type));
    declaration* IfcParameterValue_type = new type_declaration("IfcParameterValue", new simple_type(simple_type::real_type));
    declaration* IfcPlanarForceMeasure_type = new type_declaration("IfcPlanarForceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcPlaneAngleMeasure_type = new type_declaration("IfcPlaneAngleMeasure", new simple_type(simple_type::real_type));
    declaration* IfcPositiveLengthMeasure_type = new type_declaration("IfcPositiveLengthMeasure", new named_type(IfcLengthMeasure_type));
    declaration* IfcPositivePlaneAngleMeasure_type = new type_declaration("IfcPositivePlaneAngleMeasure", new named_type(IfcPlaneAngleMeasure_type));
    declaration* IfcPowerMeasure_type = new type_declaration("IfcPowerMeasure", new simple_type(simple_type::real_type));
    declaration* IfcPresentableText_type = new type_declaration("IfcPresentableText", new simple_type(simple_type::string_type));
    declaration* IfcPressureMeasure_type = new type_declaration("IfcPressureMeasure", new simple_type(simple_type::real_type));
    declaration* IfcRadioActivityMeasure_type = new type_declaration("IfcRadioActivityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcRatioMeasure_type = new type_declaration("IfcRatioMeasure", new simple_type(simple_type::real_type));
    declaration* IfcReal_type = new type_declaration("IfcReal", new simple_type(simple_type::real_type));
    declaration* IfcRotationalFrequencyMeasure_type = new type_declaration("IfcRotationalFrequencyMeasure", new simple_type(simple_type::real_type));
    declaration* IfcRotationalMassMeasure_type = new type_declaration("IfcRotationalMassMeasure", new simple_type(simple_type::real_type));
    declaration* IfcRotationalStiffnessMeasure_type = new type_declaration("IfcRotationalStiffnessMeasure", new simple_type(simple_type::real_type));
    declaration* IfcSecondInMinute_type = new type_declaration("IfcSecondInMinute", new simple_type(simple_type::real_type));
    declaration* IfcSectionModulusMeasure_type = new type_declaration("IfcSectionModulusMeasure", new simple_type(simple_type::real_type));
    declaration* IfcSectionalAreaIntegralMeasure_type = new type_declaration("IfcSectionalAreaIntegralMeasure", new simple_type(simple_type::real_type));
    declaration* IfcShearModulusMeasure_type = new type_declaration("IfcShearModulusMeasure", new simple_type(simple_type::real_type));
    declaration* IfcSolidAngleMeasure_type = new type_declaration("IfcSolidAngleMeasure", new simple_type(simple_type::real_type));
    declaration* IfcSoundPowerMeasure_type = new type_declaration("IfcSoundPowerMeasure", new simple_type(simple_type::real_type));
    declaration* IfcSoundPressureMeasure_type = new type_declaration("IfcSoundPressureMeasure", new simple_type(simple_type::real_type));
    declaration* IfcSpecificHeatCapacityMeasure_type = new type_declaration("IfcSpecificHeatCapacityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcSpecularExponent_type = new type_declaration("IfcSpecularExponent", new simple_type(simple_type::real_type));
    declaration* IfcSpecularRoughness_type = new type_declaration("IfcSpecularRoughness", new simple_type(simple_type::real_type));
    declaration* IfcTemperatureGradientMeasure_type = new type_declaration("IfcTemperatureGradientMeasure", new simple_type(simple_type::real_type));
    declaration* IfcText_type = new type_declaration("IfcText", new simple_type(simple_type::string_type));
    declaration* IfcTextAlignment_type = new type_declaration("IfcTextAlignment", new simple_type(simple_type::string_type));
    declaration* IfcTextDecoration_type = new type_declaration("IfcTextDecoration", new simple_type(simple_type::string_type));
    declaration* IfcTextFontName_type = new type_declaration("IfcTextFontName", new simple_type(simple_type::string_type));
    declaration* IfcTextTransformation_type = new type_declaration("IfcTextTransformation", new simple_type(simple_type::string_type));
    declaration* IfcThermalAdmittanceMeasure_type = new type_declaration("IfcThermalAdmittanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcThermalConductivityMeasure_type = new type_declaration("IfcThermalConductivityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcThermalExpansionCoefficientMeasure_type = new type_declaration("IfcThermalExpansionCoefficientMeasure", new simple_type(simple_type::real_type));
    declaration* IfcThermalResistanceMeasure_type = new type_declaration("IfcThermalResistanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcThermalTransmittanceMeasure_type = new type_declaration("IfcThermalTransmittanceMeasure", new simple_type(simple_type::real_type));
    declaration* IfcThermodynamicTemperatureMeasure_type = new type_declaration("IfcThermodynamicTemperatureMeasure", new simple_type(simple_type::real_type));
    declaration* IfcTimeMeasure_type = new type_declaration("IfcTimeMeasure", new simple_type(simple_type::real_type));
    declaration* IfcTimeStamp_type = new type_declaration("IfcTimeStamp", new simple_type(simple_type::integer_type));
    declaration* IfcTorqueMeasure_type = new type_declaration("IfcTorqueMeasure", new simple_type(simple_type::real_type));
    declaration* IfcVaporPermeabilityMeasure_type = new type_declaration("IfcVaporPermeabilityMeasure", new simple_type(simple_type::real_type));
    declaration* IfcVolumeMeasure_type = new type_declaration("IfcVolumeMeasure", new simple_type(simple_type::real_type));
    declaration* IfcVolumetricFlowRateMeasure_type = new type_declaration("IfcVolumetricFlowRateMeasure", new simple_type(simple_type::real_type));
    declaration* IfcWarpingConstantMeasure_type = new type_declaration("IfcWarpingConstantMeasure", new simple_type(simple_type::real_type));
    declaration* IfcWarpingMomentMeasure_type = new type_declaration("IfcWarpingMomentMeasure", new simple_type(simple_type::real_type));
    declaration* IfcYearNumber_type = new type_declaration("IfcYearNumber", new simple_type(simple_type::integer_type));
    declaration* IfcBoxAlignment_type = new type_declaration("IfcBoxAlignment", new named_type(IfcLabel_type));
    declaration* IfcNormalisedRatioMeasure_type = new type_declaration("IfcNormalisedRatioMeasure", new named_type(IfcRatioMeasure_type));
    declaration* IfcPositiveRatioMeasure_type = new type_declaration("IfcPositiveRatioMeasure", new named_type(IfcRatioMeasure_type));
    declaration* IfcActionSourceTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(27);
        items.push_back("BRAKES");
        items.push_back("BUOYANCY");
        items.push_back("COMPLETION_G1");
        items.push_back("CREEP");
        items.push_back("CURRENT");
        items.push_back("DEAD_LOAD_G");
        items.push_back("EARTHQUAKE_E");
        items.push_back("ERECTION");
        items.push_back("FIRE");
        items.push_back("ICE");
        items.push_back("IMPACT");
        items.push_back("IMPULSE");
        items.push_back("LACK_OF_FIT");
        items.push_back("LIVE_LOAD_Q");
        items.push_back("NOTDEFINED");
        items.push_back("PRESTRESSING_P");
        items.push_back("PROPPING");
        items.push_back("RAIN");
        items.push_back("SETTLEMENT_U");
        items.push_back("SHRINKAGE");
        items.push_back("SNOW_S");
        items.push_back("SYSTEM_IMPERFECTION");
        items.push_back("TEMPERATURE_T");
        items.push_back("TRANSPORT");
        items.push_back("USERDEFINED");
        items.push_back("WAVE");
        items.push_back("WIND_W");
        IfcActionSourceTypeEnum_type = new enumeration_type("IfcActionSourceTypeEnum", items);
    }
    declaration* IfcActionTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IfcActionTypeEnum_type = new enumeration_type("IfcActionTypeEnum", items);
    }
    declaration* IfcActuatorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("ELECTRICACTUATOR");
        items.push_back("HANDOPERATEDACTUATOR");
        items.push_back("HYDRAULICACTUATOR");
        items.push_back("NOTDEFINED");
        items.push_back("PNEUMATICACTUATOR");
        items.push_back("THERMOSTATICACTUATOR");
        items.push_back("USERDEFINED");
        IfcActuatorTypeEnum_type = new enumeration_type("IfcActuatorTypeEnum", items);
    }
    declaration* IfcAddressTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IfcAddressTypeEnum_type = new enumeration_type("IfcAddressTypeEnum", items);
    }
    declaration* IfcAheadOrBehind_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AHEAD");
        items.push_back("BEHIND");
        IfcAheadOrBehind_type = new enumeration_type("IfcAheadOrBehind", items);
    }
    declaration* IfcAirTerminalBoxTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IfcAirTerminalBoxTypeEnum_type = new enumeration_type("IfcAirTerminalBoxTypeEnum", items);
    }
    declaration* IfcAirTerminalTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("DIFFUSER");
        items.push_back("EYEBALL");
        items.push_back("GRILLE");
        items.push_back("IRIS");
        items.push_back("LINEARDIFFUSER");
        items.push_back("LINEARGRILLE");
        items.push_back("NOTDEFINED");
        items.push_back("REGISTER");
        items.push_back("USERDEFINED");
        IfcAirTerminalTypeEnum_type = new enumeration_type("IfcAirTerminalTypeEnum", items);
    }
    declaration* IfcAirToAirHeatRecoveryTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("FIXEDPLATECOUNTERFLOWEXCHANGER");
        items.push_back("FIXEDPLATECROSSFLOWEXCHANGER");
        items.push_back("FIXEDPLATEPARALLELFLOWEXCHANGER");
        items.push_back("HEATPIPE");
        items.push_back("NOTDEFINED");
        items.push_back("ROTARYWHEEL");
        items.push_back("RUNAROUNDCOILLOOP");
        items.push_back("THERMOSIPHONCOILTYPEHEATEXCHANGERS");
        items.push_back("THERMOSIPHONSEALEDTUBEHEATEXCHANGERS");
        items.push_back("TWINTOWERENTHALPYRECOVERYLOOPS");
        items.push_back("USERDEFINED");
        IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", items);
    }
    declaration* IfcAlarmTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("BELL");
        items.push_back("BREAKGLASSBUTTON");
        items.push_back("LIGHT");
        items.push_back("MANUALPULLBOX");
        items.push_back("NOTDEFINED");
        items.push_back("SIREN");
        items.push_back("USERDEFINED");
        items.push_back("WHISTLE");
        IfcAlarmTypeEnum_type = new enumeration_type("IfcAlarmTypeEnum", items);
    }
    declaration* IfcAnalysisModelTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IfcAnalysisModelTypeEnum_type = new enumeration_type("IfcAnalysisModelTypeEnum", items);
    }
    declaration* IfcAnalysisTheoryTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IfcAnalysisTheoryTypeEnum_type = new enumeration_type("IfcAnalysisTheoryTypeEnum", items);
    }
    declaration* IfcArithmeticOperatorEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IfcArithmeticOperatorEnum_type = new enumeration_type("IfcArithmeticOperatorEnum", items);
    }
    declaration* IfcAssemblyPlaceEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IfcAssemblyPlaceEnum_type = new enumeration_type("IfcAssemblyPlaceEnum", items);
    }
    declaration* IfcBSplineCurveForm_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IfcBSplineCurveForm_type = new enumeration_type("IfcBSplineCurveForm", items);
    }
    declaration* IfcBeamTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEAM");
        items.push_back("JOIST");
        items.push_back("LINTEL");
        items.push_back("NOTDEFINED");
        items.push_back("T_BEAM");
        items.push_back("USERDEFINED");
        IfcBeamTypeEnum_type = new enumeration_type("IfcBeamTypeEnum", items);
    }
    declaration* IfcBenchmarkEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EQUALTO");
        items.push_back("GREATERTHAN");
        items.push_back("GREATERTHANOREQUALTO");
        items.push_back("LESSTHAN");
        items.push_back("LESSTHANOREQUALTO");
        items.push_back("NOTEQUALTO");
        IfcBenchmarkEnum_type = new enumeration_type("IfcBenchmarkEnum", items);
    }
    declaration* IfcBoilerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IfcBoilerTypeEnum_type = new enumeration_type("IfcBoilerTypeEnum", items);
    }
    declaration* IfcBooleanOperator_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IfcBooleanOperator_type = new enumeration_type("IfcBooleanOperator", items);
    }
    declaration* IfcBuildingElementProxyTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcBuildingElementProxyTypeEnum_type = new enumeration_type("IfcBuildingElementProxyTypeEnum", items);
    }
    declaration* IfcCableCarrierFittingTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IfcCableCarrierFittingTypeEnum_type = new enumeration_type("IfcCableCarrierFittingTypeEnum", items);
    }
    declaration* IfcCableCarrierSegmentTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCableCarrierSegmentTypeEnum_type = new enumeration_type("IfcCableCarrierSegmentTypeEnum", items);
    }
    declaration* IfcCableSegmentTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCableSegmentTypeEnum_type = new enumeration_type("IfcCableSegmentTypeEnum", items);
    }
    declaration* IfcChangeActionEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("MODIFIEDADDED");
        items.push_back("MODIFIEDDELETED");
        items.push_back("NOCHANGE");
        IfcChangeActionEnum_type = new enumeration_type("IfcChangeActionEnum", items);
    }
    declaration* IfcChillerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IfcChillerTypeEnum_type = new enumeration_type("IfcChillerTypeEnum", items);
    }
    declaration* IfcCoilTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("DXCOOLINGCOIL");
        items.push_back("ELECTRICHEATINGCOIL");
        items.push_back("GASHEATINGCOIL");
        items.push_back("NOTDEFINED");
        items.push_back("STEAMHEATINGCOIL");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLINGCOIL");
        items.push_back("WATERHEATINGCOIL");
        IfcCoilTypeEnum_type = new enumeration_type("IfcCoilTypeEnum", items);
    }
    declaration* IfcColumnTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcColumnTypeEnum_type = new enumeration_type("IfcColumnTypeEnum", items);
    }
    declaration* IfcCompressorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(17);
        items.push_back("BOOSTER");
        items.push_back("DYNAMIC");
        items.push_back("HERMETIC");
        items.push_back("NOTDEFINED");
        items.push_back("OPENTYPE");
        items.push_back("RECIPROCATING");
        items.push_back("ROLLINGPISTON");
        items.push_back("ROTARY");
        items.push_back("ROTARYVANE");
        items.push_back("SCROLL");
        items.push_back("SEMIHERMETIC");
        items.push_back("SINGLESCREW");
        items.push_back("SINGLESTAGE");
        items.push_back("TROCHOIDAL");
        items.push_back("TWINSCREW");
        items.push_back("USERDEFINED");
        items.push_back("WELDEDSHELLHERMETIC");
        IfcCompressorTypeEnum_type = new enumeration_type("IfcCompressorTypeEnum", items);
    }
    declaration* IfcCondenserTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("AIRCOOLED");
        items.push_back("EVAPORATIVECOOLED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLEDBRAZEDPLATE");
        items.push_back("WATERCOOLEDSHELLCOIL");
        items.push_back("WATERCOOLEDSHELLTUBE");
        items.push_back("WATERCOOLEDTUBEINTUBE");
        IfcCondenserTypeEnum_type = new enumeration_type("IfcCondenserTypeEnum", items);
    }
    declaration* IfcConnectionTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IfcConnectionTypeEnum_type = new enumeration_type("IfcConnectionTypeEnum", items);
    }
    declaration* IfcConstraintEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IfcConstraintEnum_type = new enumeration_type("IfcConstraintEnum", items);
    }
    declaration* IfcControllerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("FLOATING");
        items.push_back("NOTDEFINED");
        items.push_back("PROPORTIONAL");
        items.push_back("PROPORTIONALINTEGRAL");
        items.push_back("PROPORTIONALINTEGRALDERIVATIVE");
        items.push_back("TIMEDTWOPOSITION");
        items.push_back("TWOPOSITION");
        items.push_back("USERDEFINED");
        IfcControllerTypeEnum_type = new enumeration_type("IfcControllerTypeEnum", items);
    }
    declaration* IfcCooledBeamTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IfcCooledBeamTypeEnum_type = new enumeration_type("IfcCooledBeamTypeEnum", items);
    }
    declaration* IfcCoolingTowerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCoolingTowerTypeEnum_type = new enumeration_type("IfcCoolingTowerTypeEnum", items);
    }
    declaration* IfcCostScheduleTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("BUDGET");
        items.push_back("COSTPLAN");
        items.push_back("ESTIMATE");
        items.push_back("NOTDEFINED");
        items.push_back("PRICEDBILLOFQUANTITIES");
        items.push_back("SCHEDULEOFRATES");
        items.push_back("TENDER");
        items.push_back("UNPRICEDBILLOFQUANTITIES");
        items.push_back("USERDEFINED");
        IfcCostScheduleTypeEnum_type = new enumeration_type("IfcCostScheduleTypeEnum", items);
    }
    declaration* IfcCoveringTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("CEILING");
        items.push_back("CLADDING");
        items.push_back("FLOORING");
        items.push_back("INSULATION");
        items.push_back("MEMBRANE");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFING");
        items.push_back("SLEEVING");
        items.push_back("USERDEFINED");
        items.push_back("WRAPPING");
        IfcCoveringTypeEnum_type = new enumeration_type("IfcCoveringTypeEnum", items);
    }
    declaration* IfcCurrencyEnum_type;
    {
        std::vector<std::string> items; items.reserve(83);
        items.push_back("AED");
        items.push_back("AES");
        items.push_back("ATS");
        items.push_back("AUD");
        items.push_back("BBD");
        items.push_back("BEG");
        items.push_back("BGL");
        items.push_back("BHD");
        items.push_back("BMD");
        items.push_back("BND");
        items.push_back("BRL");
        items.push_back("BSD");
        items.push_back("BWP");
        items.push_back("BZD");
        items.push_back("CAD");
        items.push_back("CBD");
        items.push_back("CHF");
        items.push_back("CLP");
        items.push_back("CNY");
        items.push_back("CYS");
        items.push_back("CZK");
        items.push_back("DDP");
        items.push_back("DEM");
        items.push_back("DKK");
        items.push_back("EGL");
        items.push_back("EST");
        items.push_back("EUR");
        items.push_back("FAK");
        items.push_back("FIM");
        items.push_back("FJD");
        items.push_back("FKP");
        items.push_back("FRF");
        items.push_back("GBP");
        items.push_back("GIP");
        items.push_back("GMD");
        items.push_back("GRX");
        items.push_back("HKD");
        items.push_back("HUF");
        items.push_back("ICK");
        items.push_back("IDR");
        items.push_back("ILS");
        items.push_back("INR");
        items.push_back("IRP");
        items.push_back("ITL");
        items.push_back("JMD");
        items.push_back("JOD");
        items.push_back("JPY");
        items.push_back("KES");
        items.push_back("KRW");
        items.push_back("KWD");
        items.push_back("KYD");
        items.push_back("LKR");
        items.push_back("LUF");
        items.push_back("MTL");
        items.push_back("MUR");
        items.push_back("MXN");
        items.push_back("MYR");
        items.push_back("NLG");
        items.push_back("NOK");
        items.push_back("NZD");
        items.push_back("OMR");
        items.push_back("PGK");
        items.push_back("PHP");
        items.push_back("PKR");
        items.push_back("PLN");
        items.push_back("PTN");
        items.push_back("QAR");
        items.push_back("RUR");
        items.push_back("SAR");
        items.push_back("SCR");
        items.push_back("SEK");
        items.push_back("SGD");
        items.push_back("SKP");
        items.push_back("THB");
        items.push_back("TRL");
        items.push_back("TTD");
        items.push_back("TWD");
        items.push_back("USD");
        items.push_back("VEB");
        items.push_back("VND");
        items.push_back("XEU");
        items.push_back("ZAR");
        items.push_back("ZWD");
        IfcCurrencyEnum_type = new enumeration_type("IfcCurrencyEnum", items);
    }
    declaration* IfcCurtainWallTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCurtainWallTypeEnum_type = new enumeration_type("IfcCurtainWallTypeEnum", items);
    }
    declaration* IfcDamperTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(13);
        items.push_back("BACKDRAFTDAMPER");
        items.push_back("BALANCINGDAMPER");
        items.push_back("BLASTDAMPER");
        items.push_back("CONTROLDAMPER");
        items.push_back("FIREDAMPER");
        items.push_back("FIRESMOKEDAMPER");
        items.push_back("FUMEHOODEXHAUST");
        items.push_back("GRAVITYDAMPER");
        items.push_back("GRAVITYRELIEFDAMPER");
        items.push_back("NOTDEFINED");
        items.push_back("RELIEFDAMPER");
        items.push_back("SMOKEDAMPER");
        items.push_back("USERDEFINED");
        IfcDamperTypeEnum_type = new enumeration_type("IfcDamperTypeEnum", items);
    }
    declaration* IfcDataOriginEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IfcDataOriginEnum_type = new enumeration_type("IfcDataOriginEnum", items);
    }
    declaration* IfcDerivedUnitEnum_type;
    {
        std::vector<std::string> items; items.reserve(49);
        items.push_back("ACCELERATIONUNIT");
        items.push_back("ANGULARVELOCITYUNIT");
        items.push_back("COMPOUNDPLANEANGLEUNIT");
        items.push_back("CURVATUREUNIT");
        items.push_back("DYNAMICVISCOSITYUNIT");
        items.push_back("HEATFLUXDENSITYUNIT");
        items.push_back("HEATINGVALUEUNIT");
        items.push_back("INTEGERCOUNTRATEUNIT");
        items.push_back("IONCONCENTRATIONUNIT");
        items.push_back("ISOTHERMALMOISTURECAPACITYUNIT");
        items.push_back("KINEMATICVISCOSITYUNIT");
        items.push_back("LINEARFORCEUNIT");
        items.push_back("LINEARMOMENTUNIT");
        items.push_back("LINEARSTIFFNESSUNIT");
        items.push_back("LINEARVELOCITYUNIT");
        items.push_back("LUMINOUSINTENSITYDISTRIBUTIONUNIT");
        items.push_back("MASSDENSITYUNIT");
        items.push_back("MASSFLOWRATEUNIT");
        items.push_back("MASSPERLENGTHUNIT");
        items.push_back("MODULUSOFELASTICITYUNIT");
        items.push_back("MODULUSOFLINEARSUBGRADEREACTIONUNIT");
        items.push_back("MODULUSOFROTATIONALSUBGRADEREACTIONUNIT");
        items.push_back("MODULUSOFSUBGRADEREACTIONUNIT");
        items.push_back("MOISTUREDIFFUSIVITYUNIT");
        items.push_back("MOLECULARWEIGHTUNIT");
        items.push_back("MOMENTOFINERTIAUNIT");
        items.push_back("PHUNIT");
        items.push_back("PLANARFORCEUNIT");
        items.push_back("ROTATIONALFREQUENCYUNIT");
        items.push_back("ROTATIONALMASSUNIT");
        items.push_back("ROTATIONALSTIFFNESSUNIT");
        items.push_back("SECTIONAREAINTEGRALUNIT");
        items.push_back("SECTIONMODULUSUNIT");
        items.push_back("SHEARMODULUSUNIT");
        items.push_back("SOUNDPOWERUNIT");
        items.push_back("SOUNDPRESSUREUNIT");
        items.push_back("SPECIFICHEATCAPACITYUNIT");
        items.push_back("TEMPERATUREGRADIENTUNIT");
        items.push_back("THERMALADMITTANCEUNIT");
        items.push_back("THERMALCONDUCTANCEUNIT");
        items.push_back("THERMALEXPANSIONCOEFFICIENTUNIT");
        items.push_back("THERMALRESISTANCEUNIT");
        items.push_back("THERMALTRANSMITTANCEUNIT");
        items.push_back("TORQUEUNIT");
        items.push_back("USERDEFINED");
        items.push_back("VAPORPERMEABILITYUNIT");
        items.push_back("VOLUMETRICFLOWRATEUNIT");
        items.push_back("WARPINGCONSTANTUNIT");
        items.push_back("WARPINGMOMENTUNIT");
        IfcDerivedUnitEnum_type = new enumeration_type("IfcDerivedUnitEnum", items);
    }
    declaration* IfcDimensionExtentUsage_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("ORIGIN");
        items.push_back("TARGET");
        IfcDimensionExtentUsage_type = new enumeration_type("IfcDimensionExtentUsage", items);
    }
    declaration* IfcDirectionSenseEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IfcDirectionSenseEnum_type = new enumeration_type("IfcDirectionSenseEnum", items);
    }
    declaration* IfcDistributionChamberElementTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("FORMEDDUCT");
        items.push_back("INSPECTIONCHAMBER");
        items.push_back("INSPECTIONPIT");
        items.push_back("MANHOLE");
        items.push_back("METERCHAMBER");
        items.push_back("NOTDEFINED");
        items.push_back("SUMP");
        items.push_back("TRENCH");
        items.push_back("USERDEFINED");
        items.push_back("VALVECHAMBER");
        IfcDistributionChamberElementTypeEnum_type = new enumeration_type("IfcDistributionChamberElementTypeEnum", items);
    }
    declaration* IfcDocumentConfidentialityEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IfcDocumentConfidentialityEnum_type = new enumeration_type("IfcDocumentConfidentialityEnum", items);
    }
    declaration* IfcDocumentStatusEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IfcDocumentStatusEnum_type = new enumeration_type("IfcDocumentStatusEnum", items);
    }
    declaration* IfcDoorPanelOperationEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("DOUBLE_ACTING");
        items.push_back("FOLDING");
        items.push_back("NOTDEFINED");
        items.push_back("REVOLVING");
        items.push_back("ROLLINGUP");
        items.push_back("SLIDING");
        items.push_back("SWINGING");
        items.push_back("USERDEFINED");
        IfcDoorPanelOperationEnum_type = new enumeration_type("IfcDoorPanelOperationEnum", items);
    }
    declaration* IfcDoorPanelPositionEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IfcDoorPanelPositionEnum_type = new enumeration_type("IfcDoorPanelPositionEnum", items);
    }
    declaration* IfcDoorStyleConstructionEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("ALUMINIUM");
        items.push_back("ALUMINIUM_PLASTIC");
        items.push_back("ALUMINIUM_WOOD");
        items.push_back("HIGH_GRADE_STEEL");
        items.push_back("NOTDEFINED");
        items.push_back("PLASTIC");
        items.push_back("STEEL");
        items.push_back("USERDEFINED");
        items.push_back("WOOD");
        IfcDoorStyleConstructionEnum_type = new enumeration_type("IfcDoorStyleConstructionEnum", items);
    }
    declaration* IfcDoorStyleOperationEnum_type;
    {
        std::vector<std::string> items; items.reserve(18);
        items.push_back("DOUBLE_DOOR_DOUBLE_SWING");
        items.push_back("DOUBLE_DOOR_FOLDING");
        items.push_back("DOUBLE_DOOR_SINGLE_SWING");
        items.push_back("DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT");
        items.push_back("DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT");
        items.push_back("DOUBLE_DOOR_SLIDING");
        items.push_back("DOUBLE_SWING_LEFT");
        items.push_back("DOUBLE_SWING_RIGHT");
        items.push_back("FOLDING_TO_LEFT");
        items.push_back("FOLDING_TO_RIGHT");
        items.push_back("NOTDEFINED");
        items.push_back("REVOLVING");
        items.push_back("ROLLINGUP");
        items.push_back("SINGLE_SWING_LEFT");
        items.push_back("SINGLE_SWING_RIGHT");
        items.push_back("SLIDING_TO_LEFT");
        items.push_back("SLIDING_TO_RIGHT");
        items.push_back("USERDEFINED");
        IfcDoorStyleOperationEnum_type = new enumeration_type("IfcDoorStyleOperationEnum", items);
    }
    declaration* IfcDuctFittingTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("BEND");
        items.push_back("CONNECTOR");
        items.push_back("ENTRY");
        items.push_back("EXIT");
        items.push_back("JUNCTION");
        items.push_back("NOTDEFINED");
        items.push_back("OBSTRUCTION");
        items.push_back("TRANSITION");
        items.push_back("USERDEFINED");
        IfcDuctFittingTypeEnum_type = new enumeration_type("IfcDuctFittingTypeEnum", items);
    }
    declaration* IfcDuctSegmentTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IfcDuctSegmentTypeEnum_type = new enumeration_type("IfcDuctSegmentTypeEnum", items);
    }
    declaration* IfcDuctSilencerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IfcDuctSilencerTypeEnum_type = new enumeration_type("IfcDuctSilencerTypeEnum", items);
    }
    declaration* IfcElectricApplianceTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(26);
        items.push_back("COMPUTER");
        items.push_back("DIRECTWATERHEATER");
        items.push_back("DISHWASHER");
        items.push_back("ELECTRICCOOKER");
        items.push_back("ELECTRICHEATER");
        items.push_back("FACSIMILE");
        items.push_back("FREESTANDINGFAN");
        items.push_back("FREEZER");
        items.push_back("FRIDGE_FREEZER");
        items.push_back("HANDDRYER");
        items.push_back("INDIRECTWATERHEATER");
        items.push_back("MICROWAVE");
        items.push_back("NOTDEFINED");
        items.push_back("PHOTOCOPIER");
        items.push_back("PRINTER");
        items.push_back("RADIANTHEATER");
        items.push_back("REFRIGERATOR");
        items.push_back("SCANNER");
        items.push_back("TELEPHONE");
        items.push_back("TUMBLEDRYER");
        items.push_back("TV");
        items.push_back("USERDEFINED");
        items.push_back("VENDINGMACHINE");
        items.push_back("WASHINGMACHINE");
        items.push_back("WATERCOOLER");
        items.push_back("WATERHEATER");
        IfcElectricApplianceTypeEnum_type = new enumeration_type("IfcElectricApplianceTypeEnum", items);
    }
    declaration* IfcElectricCurrentEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ALTERNATING");
        items.push_back("DIRECT");
        items.push_back("NOTDEFINED");
        IfcElectricCurrentEnum_type = new enumeration_type("IfcElectricCurrentEnum", items);
    }
    declaration* IfcElectricDistributionPointFunctionEnum_type;
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("ALARMPANEL");
        items.push_back("CONSUMERUNIT");
        items.push_back("CONTROLPANEL");
        items.push_back("DISTRIBUTIONBOARD");
        items.push_back("GASDETECTORPANEL");
        items.push_back("INDICATORPANEL");
        items.push_back("MIMICPANEL");
        items.push_back("MOTORCONTROLCENTRE");
        items.push_back("NOTDEFINED");
        items.push_back("SWITCHBOARD");
        items.push_back("USERDEFINED");
        IfcElectricDistributionPointFunctionEnum_type = new enumeration_type("IfcElectricDistributionPointFunctionEnum", items);
    }
    declaration* IfcElectricFlowStorageDeviceTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("BATTERY");
        items.push_back("CAPACITORBANK");
        items.push_back("HARMONICFILTER");
        items.push_back("INDUCTORBANK");
        items.push_back("NOTDEFINED");
        items.push_back("UPS");
        items.push_back("USERDEFINED");
        IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", items);
    }
    declaration* IfcElectricGeneratorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcElectricGeneratorTypeEnum_type = new enumeration_type("IfcElectricGeneratorTypeEnum", items);
    }
    declaration* IfcElectricHeaterTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELECTRICCABLEHEATER");
        items.push_back("ELECTRICMATHEATER");
        items.push_back("ELECTRICPOINTHEATER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcElectricHeaterTypeEnum_type = new enumeration_type("IfcElectricHeaterTypeEnum", items);
    }
    declaration* IfcElectricMotorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DC");
        items.push_back("INDUCTION");
        items.push_back("NOTDEFINED");
        items.push_back("POLYPHASE");
        items.push_back("RELUCTANCESYNCHRONOUS");
        items.push_back("SYNCHRONOUS");
        items.push_back("USERDEFINED");
        IfcElectricMotorTypeEnum_type = new enumeration_type("IfcElectricMotorTypeEnum", items);
    }
    declaration* IfcElectricTimeControlTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IfcElectricTimeControlTypeEnum_type = new enumeration_type("IfcElectricTimeControlTypeEnum", items);
    }
    declaration* IfcElementAssemblyTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("ACCESSORY_ASSEMBLY");
        items.push_back("ARCH");
        items.push_back("BEAM_GRID");
        items.push_back("BRACED_FRAME");
        items.push_back("GIRDER");
        items.push_back("NOTDEFINED");
        items.push_back("REINFORCEMENT_UNIT");
        items.push_back("RIGID_FRAME");
        items.push_back("SLAB_FIELD");
        items.push_back("TRUSS");
        items.push_back("USERDEFINED");
        IfcElementAssemblyTypeEnum_type = new enumeration_type("IfcElementAssemblyTypeEnum", items);
    }
    declaration* IfcElementCompositionEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IfcElementCompositionEnum_type = new enumeration_type("IfcElementCompositionEnum", items);
    }
    declaration* IfcEnergySequenceEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AUXILIARY");
        items.push_back("NOTDEFINED");
        items.push_back("PRIMARY");
        items.push_back("SECONDARY");
        items.push_back("TERTIARY");
        items.push_back("USERDEFINED");
        IfcEnergySequenceEnum_type = new enumeration_type("IfcEnergySequenceEnum", items);
    }
    declaration* IfcEnvironmentalImpactCategoryEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("COMBINEDVALUE");
        items.push_back("DISPOSAL");
        items.push_back("EXTRACTION");
        items.push_back("INSTALLATION");
        items.push_back("MANUFACTURE");
        items.push_back("NOTDEFINED");
        items.push_back("TRANSPORTATION");
        items.push_back("USERDEFINED");
        IfcEnvironmentalImpactCategoryEnum_type = new enumeration_type("IfcEnvironmentalImpactCategoryEnum", items);
    }
    declaration* IfcEvaporativeCoolerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("DIRECTEVAPORATIVEAIRWASHER");
        items.push_back("DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER");
        items.push_back("DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER");
        items.push_back("DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER");
        items.push_back("DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER");
        items.push_back("INDIRECTDIRECTCOMBINATION");
        items.push_back("INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER");
        items.push_back("INDIRECTEVAPORATIVEPACKAGEAIRCOOLER");
        items.push_back("INDIRECTEVAPORATIVEWETCOIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcEvaporativeCoolerTypeEnum_type = new enumeration_type("IfcEvaporativeCoolerTypeEnum", items);
    }
    declaration* IfcEvaporatorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DIRECTEXPANSIONBRAZEDPLATE");
        items.push_back("DIRECTEXPANSIONSHELLANDTUBE");
        items.push_back("DIRECTEXPANSIONTUBEINTUBE");
        items.push_back("FLOODEDSHELLANDTUBE");
        items.push_back("NOTDEFINED");
        items.push_back("SHELLANDCOIL");
        items.push_back("USERDEFINED");
        IfcEvaporatorTypeEnum_type = new enumeration_type("IfcEvaporatorTypeEnum", items);
    }
    declaration* IfcFanTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("CENTRIFUGALAIRFOIL");
        items.push_back("CENTRIFUGALBACKWARDINCLINEDCURVED");
        items.push_back("CENTRIFUGALFORWARDCURVED");
        items.push_back("CENTRIFUGALRADIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PROPELLORAXIAL");
        items.push_back("TUBEAXIAL");
        items.push_back("USERDEFINED");
        items.push_back("VANEAXIAL");
        IfcFanTypeEnum_type = new enumeration_type("IfcFanTypeEnum", items);
    }
    declaration* IfcFilterTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("AIRPARTICLEFILTER");
        items.push_back("NOTDEFINED");
        items.push_back("ODORFILTER");
        items.push_back("OILFILTER");
        items.push_back("STRAINER");
        items.push_back("USERDEFINED");
        items.push_back("WATERFILTER");
        IfcFilterTypeEnum_type = new enumeration_type("IfcFilterTypeEnum", items);
    }
    declaration* IfcFireSuppressionTerminalTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("BREECHINGINLET");
        items.push_back("FIREHYDRANT");
        items.push_back("HOSEREEL");
        items.push_back("NOTDEFINED");
        items.push_back("SPRINKLER");
        items.push_back("SPRINKLERDEFLECTOR");
        items.push_back("USERDEFINED");
        IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", items);
    }
    declaration* IfcFlowDirectionEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IfcFlowDirectionEnum_type = new enumeration_type("IfcFlowDirectionEnum", items);
    }
    declaration* IfcFlowInstrumentTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("AMMETER");
        items.push_back("FREQUENCYMETER");
        items.push_back("NOTDEFINED");
        items.push_back("PHASEANGLEMETER");
        items.push_back("POWERFACTORMETER");
        items.push_back("PRESSUREGAUGE");
        items.push_back("THERMOMETER");
        items.push_back("USERDEFINED");
        items.push_back("VOLTMETER_PEAK");
        items.push_back("VOLTMETER_RMS");
        IfcFlowInstrumentTypeEnum_type = new enumeration_type("IfcFlowInstrumentTypeEnum", items);
    }
    declaration* IfcFlowMeterTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("ELECTRICMETER");
        items.push_back("ENERGYMETER");
        items.push_back("FLOWMETER");
        items.push_back("GASMETER");
        items.push_back("NOTDEFINED");
        items.push_back("OILMETER");
        items.push_back("USERDEFINED");
        items.push_back("WATERMETER");
        IfcFlowMeterTypeEnum_type = new enumeration_type("IfcFlowMeterTypeEnum", items);
    }
    declaration* IfcFootingTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IfcFootingTypeEnum_type = new enumeration_type("IfcFootingTypeEnum", items);
    }
    declaration* IfcGasTerminalTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GASAPPLIANCE");
        items.push_back("GASBOOSTER");
        items.push_back("GASBURNER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcGasTerminalTypeEnum_type = new enumeration_type("IfcGasTerminalTypeEnum", items);
    }
    declaration* IfcGeometricProjectionEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("ELEVATION_VIEW");
        items.push_back("GRAPH_VIEW");
        items.push_back("MODEL_VIEW");
        items.push_back("NOTDEFINED");
        items.push_back("PLAN_VIEW");
        items.push_back("REFLECTED_PLAN_VIEW");
        items.push_back("SECTION_VIEW");
        items.push_back("SKETCH_VIEW");
        items.push_back("USERDEFINED");
        IfcGeometricProjectionEnum_type = new enumeration_type("IfcGeometricProjectionEnum", items);
    }
    declaration* IfcGlobalOrLocalEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IfcGlobalOrLocalEnum_type = new enumeration_type("IfcGlobalOrLocalEnum", items);
    }
    declaration* IfcHeatExchangerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IfcHeatExchangerTypeEnum_type = new enumeration_type("IfcHeatExchangerTypeEnum", items);
    }
    declaration* IfcHumidifierTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(15);
        items.push_back("ADIABATICAIRWASHER");
        items.push_back("ADIABATICATOMIZING");
        items.push_back("ADIABATICCOMPRESSEDAIRNOZZLE");
        items.push_back("ADIABATICPAN");
        items.push_back("ADIABATICRIGIDMEDIA");
        items.push_back("ADIABATICULTRASONIC");
        items.push_back("ADIABATICWETTEDELEMENT");
        items.push_back("ASSISTEDBUTANE");
        items.push_back("ASSISTEDELECTRIC");
        items.push_back("ASSISTEDNATURALGAS");
        items.push_back("ASSISTEDPROPANE");
        items.push_back("ASSISTEDSTEAM");
        items.push_back("NOTDEFINED");
        items.push_back("STEAMINJECTION");
        items.push_back("USERDEFINED");
        IfcHumidifierTypeEnum_type = new enumeration_type("IfcHumidifierTypeEnum", items);
    }
    declaration* IfcInternalOrExternalEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("EXTERNAL");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IfcInternalOrExternalEnum_type = new enumeration_type("IfcInternalOrExternalEnum", items);
    }
    declaration* IfcInventoryTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IfcInventoryTypeEnum_type = new enumeration_type("IfcInventoryTypeEnum", items);
    }
    declaration* IfcJunctionBoxTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcJunctionBoxTypeEnum_type = new enumeration_type("IfcJunctionBoxTypeEnum", items);
    }
    declaration* IfcLampTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("COMPACTFLUORESCENT");
        items.push_back("FLUORESCENT");
        items.push_back("HIGHPRESSUREMERCURY");
        items.push_back("HIGHPRESSURESODIUM");
        items.push_back("METALHALIDE");
        items.push_back("NOTDEFINED");
        items.push_back("TUNGSTENFILAMENT");
        items.push_back("USERDEFINED");
        IfcLampTypeEnum_type = new enumeration_type("IfcLampTypeEnum", items);
    }
    declaration* IfcLayerSetDirectionEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IfcLayerSetDirectionEnum_type = new enumeration_type("IfcLayerSetDirectionEnum", items);
    }
    declaration* IfcLightDistributionCurveEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IfcLightDistributionCurveEnum_type = new enumeration_type("IfcLightDistributionCurveEnum", items);
    }
    declaration* IfcLightEmissionSourceEnum_type;
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("COMPACTFLUORESCENT");
        items.push_back("FLUORESCENT");
        items.push_back("HIGHPRESSUREMERCURY");
        items.push_back("HIGHPRESSURESODIUM");
        items.push_back("LIGHTEMITTINGDIODE");
        items.push_back("LOWPRESSURESODIUM");
        items.push_back("LOWVOLTAGEHALOGEN");
        items.push_back("MAINVOLTAGEHALOGEN");
        items.push_back("METALHALIDE");
        items.push_back("NOTDEFINED");
        items.push_back("TUNGSTENFILAMENT");
        IfcLightEmissionSourceEnum_type = new enumeration_type("IfcLightEmissionSourceEnum", items);
    }
    declaration* IfcLightFixtureTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("USERDEFINED");
        IfcLightFixtureTypeEnum_type = new enumeration_type("IfcLightFixtureTypeEnum", items);
    }
    declaration* IfcLoadGroupTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_COMBINATION_GROUP");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcLoadGroupTypeEnum_type = new enumeration_type("IfcLoadGroupTypeEnum", items);
    }
    declaration* IfcLogicalOperatorEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALOR");
        IfcLogicalOperatorEnum_type = new enumeration_type("IfcLogicalOperatorEnum", items);
    }
    declaration* IfcMemberTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(14);
        items.push_back("BRACE");
        items.push_back("CHORD");
        items.push_back("COLLAR");
        items.push_back("MEMBER");
        items.push_back("MULLION");
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("POST");
        items.push_back("PURLIN");
        items.push_back("RAFTER");
        items.push_back("STRINGER");
        items.push_back("STRUT");
        items.push_back("STUD");
        items.push_back("USERDEFINED");
        IfcMemberTypeEnum_type = new enumeration_type("IfcMemberTypeEnum", items);
    }
    declaration* IfcMotorConnectionTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcMotorConnectionTypeEnum_type = new enumeration_type("IfcMotorConnectionTypeEnum", items);
    }
    declaration* IfcNullStyle_type;
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IfcNullStyle_type = new enumeration_type("IfcNullStyle", items);
    }
    declaration* IfcObjectTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("ACTOR");
        items.push_back("CONTROL");
        items.push_back("GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("PROCESS");
        items.push_back("PRODUCT");
        items.push_back("PROJECT");
        items.push_back("RESOURCE");
        IfcObjectTypeEnum_type = new enumeration_type("IfcObjectTypeEnum", items);
    }
    declaration* IfcObjectiveEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("CODECOMPLIANCE");
        items.push_back("DESIGNINTENT");
        items.push_back("HEALTHANDSAFETY");
        items.push_back("NOTDEFINED");
        items.push_back("REQUIREMENT");
        items.push_back("SPECIFICATION");
        items.push_back("TRIGGERCONDITION");
        items.push_back("USERDEFINED");
        IfcObjectiveEnum_type = new enumeration_type("IfcObjectiveEnum", items);
    }
    declaration* IfcOccupantTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("ASSIGNEE");
        items.push_back("ASSIGNOR");
        items.push_back("LESSEE");
        items.push_back("LESSOR");
        items.push_back("LETTINGAGENT");
        items.push_back("NOTDEFINED");
        items.push_back("OWNER");
        items.push_back("TENANT");
        items.push_back("USERDEFINED");
        IfcOccupantTypeEnum_type = new enumeration_type("IfcOccupantTypeEnum", items);
    }
    declaration* IfcOutletTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AUDIOVISUALOUTLET");
        items.push_back("COMMUNICATIONSOUTLET");
        items.push_back("NOTDEFINED");
        items.push_back("POWEROUTLET");
        items.push_back("USERDEFINED");
        IfcOutletTypeEnum_type = new enumeration_type("IfcOutletTypeEnum", items);
    }
    declaration* IfcPermeableCoveringOperationEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IfcPermeableCoveringOperationEnum_type = new enumeration_type("IfcPermeableCoveringOperationEnum", items);
    }
    declaration* IfcPhysicalOrVirtualEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IfcPhysicalOrVirtualEnum_type = new enumeration_type("IfcPhysicalOrVirtualEnum", items);
    }
    declaration* IfcPileConstructionEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IfcPileConstructionEnum_type = new enumeration_type("IfcPileConstructionEnum", items);
    }
    declaration* IfcPileTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COHESION");
        items.push_back("FRICTION");
        items.push_back("NOTDEFINED");
        items.push_back("SUPPORT");
        items.push_back("USERDEFINED");
        IfcPileTypeEnum_type = new enumeration_type("IfcPileTypeEnum", items);
    }
    declaration* IfcPipeFittingTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("BEND");
        items.push_back("CONNECTOR");
        items.push_back("ENTRY");
        items.push_back("EXIT");
        items.push_back("JUNCTION");
        items.push_back("NOTDEFINED");
        items.push_back("OBSTRUCTION");
        items.push_back("TRANSITION");
        items.push_back("USERDEFINED");
        IfcPipeFittingTypeEnum_type = new enumeration_type("IfcPipeFittingTypeEnum", items);
    }
    declaration* IfcPipeSegmentTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("GUTTER");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("SPOOL");
        items.push_back("USERDEFINED");
        IfcPipeSegmentTypeEnum_type = new enumeration_type("IfcPipeSegmentTypeEnum", items);
    }
    declaration* IfcPlateTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IfcPlateTypeEnum_type = new enumeration_type("IfcPlateTypeEnum", items);
    }
    declaration* IfcProcedureTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("ADVICE_CAUTION");
        items.push_back("ADVICE_NOTE");
        items.push_back("ADVICE_WARNING");
        items.push_back("CALIBRATION");
        items.push_back("DIAGNOSTIC");
        items.push_back("NOTDEFINED");
        items.push_back("SHUTDOWN");
        items.push_back("STARTUP");
        items.push_back("USERDEFINED");
        IfcProcedureTypeEnum_type = new enumeration_type("IfcProcedureTypeEnum", items);
    }
    declaration* IfcProfileTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IfcProfileTypeEnum_type = new enumeration_type("IfcProfileTypeEnum", items);
    }
    declaration* IfcProjectOrderRecordTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CHANGE");
        items.push_back("MAINTENANCE");
        items.push_back("MOVE");
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASE");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IfcProjectOrderRecordTypeEnum_type = new enumeration_type("IfcProjectOrderRecordTypeEnum", items);
    }
    declaration* IfcProjectOrderTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CHANGEORDER");
        items.push_back("MAINTENANCEWORKORDER");
        items.push_back("MOVEORDER");
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASEORDER");
        items.push_back("USERDEFINED");
        items.push_back("WORKORDER");
        IfcProjectOrderTypeEnum_type = new enumeration_type("IfcProjectOrderTypeEnum", items);
    }
    declaration* IfcProjectedOrTrueLengthEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IfcProjectedOrTrueLengthEnum_type = new enumeration_type("IfcProjectedOrTrueLengthEnum", items);
    }
    declaration* IfcPropertySourceEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("ASBUILT");
        items.push_back("COMMISSIONING");
        items.push_back("DESIGN");
        items.push_back("DESIGNMAXIMUM");
        items.push_back("DESIGNMINIMUM");
        items.push_back("MEASURED");
        items.push_back("NOTKNOWN");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IfcPropertySourceEnum_type = new enumeration_type("IfcPropertySourceEnum", items);
    }
    declaration* IfcProtectiveDeviceTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("CIRCUITBREAKER");
        items.push_back("EARTHFAILUREDEVICE");
        items.push_back("FUSEDISCONNECTOR");
        items.push_back("NOTDEFINED");
        items.push_back("RESIDUALCURRENTCIRCUITBREAKER");
        items.push_back("RESIDUALCURRENTSWITCH");
        items.push_back("USERDEFINED");
        items.push_back("VARISTOR");
        IfcProtectiveDeviceTypeEnum_type = new enumeration_type("IfcProtectiveDeviceTypeEnum", items);
    }
    declaration* IfcPumpTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CIRCULATOR");
        items.push_back("ENDSUCTION");
        items.push_back("NOTDEFINED");
        items.push_back("SPLITCASE");
        items.push_back("USERDEFINED");
        items.push_back("VERTICALINLINE");
        items.push_back("VERTICALTURBINE");
        IfcPumpTypeEnum_type = new enumeration_type("IfcPumpTypeEnum", items);
    }
    declaration* IfcRailingTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcRailingTypeEnum_type = new enumeration_type("IfcRailingTypeEnum", items);
    }
    declaration* IfcRampFlightTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IfcRampFlightTypeEnum_type = new enumeration_type("IfcRampFlightTypeEnum", items);
    }
    declaration* IfcRampTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("HALF_TURN_RAMP");
        items.push_back("NOTDEFINED");
        items.push_back("QUARTER_TURN_RAMP");
        items.push_back("SPIRAL_RAMP");
        items.push_back("STRAIGHT_RUN_RAMP");
        items.push_back("TWO_QUARTER_TURN_RAMP");
        items.push_back("TWO_STRAIGHT_RUN_RAMP");
        items.push_back("USERDEFINED");
        IfcRampTypeEnum_type = new enumeration_type("IfcRampTypeEnum", items);
    }
    declaration* IfcReflectanceMethodEnum_type;
    {
        std::vector<std::string> items; items.reserve(10);
        items.push_back("BLINN");
        items.push_back("FLAT");
        items.push_back("GLASS");
        items.push_back("MATT");
        items.push_back("METAL");
        items.push_back("MIRROR");
        items.push_back("NOTDEFINED");
        items.push_back("PHONG");
        items.push_back("PLASTIC");
        items.push_back("STRAUSS");
        IfcReflectanceMethodEnum_type = new enumeration_type("IfcReflectanceMethodEnum", items);
    }
    declaration* IfcReinforcingBarRoleEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("EDGE");
        items.push_back("LIGATURE");
        items.push_back("MAIN");
        items.push_back("NOTDEFINED");
        items.push_back("PUNCHING");
        items.push_back("RING");
        items.push_back("SHEAR");
        items.push_back("STUD");
        items.push_back("USERDEFINED");
        IfcReinforcingBarRoleEnum_type = new enumeration_type("IfcReinforcingBarRoleEnum", items);
    }
    declaration* IfcReinforcingBarSurfaceEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IfcReinforcingBarSurfaceEnum_type = new enumeration_type("IfcReinforcingBarSurfaceEnum", items);
    }
    declaration* IfcResourceConsumptionEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("CONSUMED");
        items.push_back("NOTCONSUMED");
        items.push_back("NOTDEFINED");
        items.push_back("NOTOCCUPIED");
        items.push_back("OCCUPIED");
        items.push_back("PARTIALLYCONSUMED");
        items.push_back("PARTIALLYOCCUPIED");
        items.push_back("USERDEFINED");
        IfcResourceConsumptionEnum_type = new enumeration_type("IfcResourceConsumptionEnum", items);
    }
    declaration* IfcRibPlateDirectionEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("DIRECTION_X");
        items.push_back("DIRECTION_Y");
        IfcRibPlateDirectionEnum_type = new enumeration_type("IfcRibPlateDirectionEnum", items);
    }
    declaration* IfcRoleEnum_type;
    {
        std::vector<std::string> items; items.reserve(23);
        items.push_back("ARCHITECT");
        items.push_back("BUILDINGOPERATOR");
        items.push_back("BUILDINGOWNER");
        items.push_back("CIVILENGINEER");
        items.push_back("CLIENT");
        items.push_back("COMISSIONINGENGINEER");
        items.push_back("CONSTRUCTIONMANAGER");
        items.push_back("CONSULTANT");
        items.push_back("CONTRACTOR");
        items.push_back("COSTENGINEER");
        items.push_back("ELECTRICALENGINEER");
        items.push_back("ENGINEER");
        items.push_back("FACILITIESMANAGER");
        items.push_back("FIELDCONSTRUCTIONMANAGER");
        items.push_back("MANUFACTURER");
        items.push_back("MECHANICALENGINEER");
        items.push_back("OWNER");
        items.push_back("PROJECTMANAGER");
        items.push_back("RESELLER");
        items.push_back("STRUCTURALENGINEER");
        items.push_back("SUBCONTRACTOR");
        items.push_back("SUPPLIER");
        items.push_back("USERDEFINED");
        IfcRoleEnum_type = new enumeration_type("IfcRoleEnum", items);
    }
    declaration* IfcRoofTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(14);
        items.push_back("BARREL_ROOF");
        items.push_back("BUTTERFLY_ROOF");
        items.push_back("DOME_ROOF");
        items.push_back("FLAT_ROOF");
        items.push_back("FREEFORM");
        items.push_back("GABLE_ROOF");
        items.push_back("GAMBREL_ROOF");
        items.push_back("HIPPED_GABLE_ROOF");
        items.push_back("HIP_ROOF");
        items.push_back("MANSARD_ROOF");
        items.push_back("NOTDEFINED");
        items.push_back("PAVILION_ROOF");
        items.push_back("RAINBOW_ROOF");
        items.push_back("SHED_ROOF");
        IfcRoofTypeEnum_type = new enumeration_type("IfcRoofTypeEnum", items);
    }
    declaration* IfcSIPrefix_type;
    {
        std::vector<std::string> items; items.reserve(16);
        items.push_back("ATTO");
        items.push_back("CENTI");
        items.push_back("DECA");
        items.push_back("DECI");
        items.push_back("EXA");
        items.push_back("FEMTO");
        items.push_back("GIGA");
        items.push_back("HECTO");
        items.push_back("KILO");
        items.push_back("MEGA");
        items.push_back("MICRO");
        items.push_back("MILLI");
        items.push_back("NANO");
        items.push_back("PETA");
        items.push_back("PICO");
        items.push_back("TERA");
        IfcSIPrefix_type = new enumeration_type("IfcSIPrefix", items);
    }
    declaration* IfcSIUnitName_type;
    {
        std::vector<std::string> items; items.reserve(30);
        items.push_back("AMPERE");
        items.push_back("BECQUEREL");
        items.push_back("CANDELA");
        items.push_back("COULOMB");
        items.push_back("CUBIC_METRE");
        items.push_back("DEGREE_CELSIUS");
        items.push_back("FARAD");
        items.push_back("GRAM");
        items.push_back("GRAY");
        items.push_back("HENRY");
        items.push_back("HERTZ");
        items.push_back("JOULE");
        items.push_back("KELVIN");
        items.push_back("LUMEN");
        items.push_back("LUX");
        items.push_back("METRE");
        items.push_back("MOLE");
        items.push_back("NEWTON");
        items.push_back("OHM");
        items.push_back("PASCAL");
        items.push_back("RADIAN");
        items.push_back("SECOND");
        items.push_back("SIEMENS");
        items.push_back("SIEVERT");
        items.push_back("SQUARE_METRE");
        items.push_back("STERADIAN");
        items.push_back("TESLA");
        items.push_back("VOLT");
        items.push_back("WATT");
        items.push_back("WEBER");
        IfcSIUnitName_type = new enumeration_type("IfcSIUnitName", items);
    }
    declaration* IfcSanitaryTerminalTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(12);
        items.push_back("BATH");
        items.push_back("BIDET");
        items.push_back("CISTERN");
        items.push_back("NOTDEFINED");
        items.push_back("SANITARYFOUNTAIN");
        items.push_back("SHOWER");
        items.push_back("SINK");
        items.push_back("TOILETPAN");
        items.push_back("URINAL");
        items.push_back("USERDEFINED");
        items.push_back("WASHHANDBASIN");
        items.push_back("WCSEAT");
        IfcSanitaryTerminalTypeEnum_type = new enumeration_type("IfcSanitaryTerminalTypeEnum", items);
    }
    declaration* IfcSectionTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IfcSectionTypeEnum_type = new enumeration_type("IfcSectionTypeEnum", items);
    }
    declaration* IfcSensorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(15);
        items.push_back("CO2SENSOR");
        items.push_back("FIRESENSOR");
        items.push_back("FLOWSENSOR");
        items.push_back("GASSENSOR");
        items.push_back("HEATSENSOR");
        items.push_back("HUMIDITYSENSOR");
        items.push_back("LIGHTSENSOR");
        items.push_back("MOISTURESENSOR");
        items.push_back("MOVEMENTSENSOR");
        items.push_back("NOTDEFINED");
        items.push_back("PRESSURESENSOR");
        items.push_back("SMOKESENSOR");
        items.push_back("SOUNDSENSOR");
        items.push_back("TEMPERATURESENSOR");
        items.push_back("USERDEFINED");
        IfcSensorTypeEnum_type = new enumeration_type("IfcSensorTypeEnum", items);
    }
    declaration* IfcSequenceEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        IfcSequenceEnum_type = new enumeration_type("IfcSequenceEnum", items);
    }
    declaration* IfcServiceLifeFactorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("A_QUALITYOFCOMPONENTS");
        items.push_back("B_DESIGNLEVEL");
        items.push_back("C_WORKEXECUTIONLEVEL");
        items.push_back("D_INDOORENVIRONMENT");
        items.push_back("E_OUTDOORENVIRONMENT");
        items.push_back("F_INUSECONDITIONS");
        items.push_back("G_MAINTENANCELEVEL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcServiceLifeFactorTypeEnum_type = new enumeration_type("IfcServiceLifeFactorTypeEnum", items);
    }
    declaration* IfcServiceLifeTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUALSERVICELIFE");
        items.push_back("EXPECTEDSERVICELIFE");
        items.push_back("OPTIMISTICREFERENCESERVICELIFE");
        items.push_back("PESSIMISTICREFERENCESERVICELIFE");
        items.push_back("REFERENCESERVICELIFE");
        IfcServiceLifeTypeEnum_type = new enumeration_type("IfcServiceLifeTypeEnum", items);
    }
    declaration* IfcSlabTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IfcSlabTypeEnum_type = new enumeration_type("IfcSlabTypeEnum", items);
    }
    declaration* IfcSoundScaleEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DBA");
        items.push_back("DBB");
        items.push_back("DBC");
        items.push_back("NC");
        items.push_back("NOTDEFINED");
        items.push_back("NR");
        items.push_back("USERDEFINED");
        IfcSoundScaleEnum_type = new enumeration_type("IfcSoundScaleEnum", items);
    }
    declaration* IfcSpaceHeaterTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("BASEBOARDHEATER");
        items.push_back("CONVECTOR");
        items.push_back("FINNEDTUBEUNIT");
        items.push_back("NOTDEFINED");
        items.push_back("PANELRADIATOR");
        items.push_back("SECTIONALRADIATOR");
        items.push_back("TUBULARRADIATOR");
        items.push_back("UNITHEATER");
        items.push_back("USERDEFINED");
        IfcSpaceHeaterTypeEnum_type = new enumeration_type("IfcSpaceHeaterTypeEnum", items);
    }
    declaration* IfcSpaceTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcSpaceTypeEnum_type = new enumeration_type("IfcSpaceTypeEnum", items);
    }
    declaration* IfcStackTerminalTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IfcStackTerminalTypeEnum_type = new enumeration_type("IfcStackTerminalTypeEnum", items);
    }
    declaration* IfcStairFlightTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CURVED");
        items.push_back("FREEFORM");
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        items.push_back("WINDER");
        IfcStairFlightTypeEnum_type = new enumeration_type("IfcStairFlightTypeEnum", items);
    }
    declaration* IfcStairTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(16);
        items.push_back("CURVED_RUN_STAIR");
        items.push_back("DOUBLE_RETURN_STAIR");
        items.push_back("HALF_TURN_STAIR");
        items.push_back("HALF_WINDING_STAIR");
        items.push_back("NOTDEFINED");
        items.push_back("QUARTER_TURN_STAIR");
        items.push_back("QUARTER_WINDING_STAIR");
        items.push_back("SPIRAL_STAIR");
        items.push_back("STRAIGHT_RUN_STAIR");
        items.push_back("THREE_QUARTER_TURN_STAIR");
        items.push_back("THREE_QUARTER_WINDING_STAIR");
        items.push_back("TWO_CURVED_RUN_STAIR");
        items.push_back("TWO_QUARTER_TURN_STAIR");
        items.push_back("TWO_QUARTER_WINDING_STAIR");
        items.push_back("TWO_STRAIGHT_RUN_STAIR");
        items.push_back("USERDEFINED");
        IfcStairTypeEnum_type = new enumeration_type("IfcStairTypeEnum", items);
    }
    declaration* IfcStateEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IfcStateEnum_type = new enumeration_type("IfcStateEnum", items);
    }
    declaration* IfcStructuralCurveTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CABLE");
        items.push_back("COMPRESSION_MEMBER");
        items.push_back("NOTDEFINED");
        items.push_back("PIN_JOINED_MEMBER");
        items.push_back("RIGID_JOINED_MEMBER");
        items.push_back("TENSION_MEMBER");
        items.push_back("USERDEFINED");
        IfcStructuralCurveTypeEnum_type = new enumeration_type("IfcStructuralCurveTypeEnum", items);
    }
    declaration* IfcStructuralSurfaceTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IfcStructuralSurfaceTypeEnum_type = new enumeration_type("IfcStructuralSurfaceTypeEnum", items);
    }
    declaration* IfcSurfaceSide_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IfcSurfaceSide_type = new enumeration_type("IfcSurfaceSide", items);
    }
    declaration* IfcSurfaceTextureEnum_type;
    {
        std::vector<std::string> items; items.reserve(9);
        items.push_back("BUMP");
        items.push_back("NOTDEFINED");
        items.push_back("OPACITY");
        items.push_back("REFLECTION");
        items.push_back("SELFILLUMINATION");
        items.push_back("SHININESS");
        items.push_back("SPECULAR");
        items.push_back("TEXTURE");
        items.push_back("TRANSPARENCYMAP");
        IfcSurfaceTextureEnum_type = new enumeration_type("IfcSurfaceTextureEnum", items);
    }
    declaration* IfcSwitchingDeviceTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CONTACTOR");
        items.push_back("EMERGENCYSTOP");
        items.push_back("NOTDEFINED");
        items.push_back("STARTER");
        items.push_back("SWITCHDISCONNECTOR");
        items.push_back("TOGGLESWITCH");
        items.push_back("USERDEFINED");
        IfcSwitchingDeviceTypeEnum_type = new enumeration_type("IfcSwitchingDeviceTypeEnum", items);
    }
    declaration* IfcTankTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXPANSION");
        items.push_back("NOTDEFINED");
        items.push_back("PREFORMED");
        items.push_back("PRESSUREVESSEL");
        items.push_back("SECTIONAL");
        items.push_back("USERDEFINED");
        IfcTankTypeEnum_type = new enumeration_type("IfcTankTypeEnum", items);
    }
    declaration* IfcTendonTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IfcTendonTypeEnum_type = new enumeration_type("IfcTendonTypeEnum", items);
    }
    declaration* IfcTextPath_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IfcTextPath_type = new enumeration_type("IfcTextPath", items);
    }
    declaration* IfcThermalLoadSourceEnum_type;
    {
        std::vector<std::string> items; items.reserve(13);
        items.push_back("AIREXCHANGERATE");
        items.push_back("DRYBULBTEMPERATURE");
        items.push_back("EQUIPMENT");
        items.push_back("EXHAUSTAIR");
        items.push_back("INFILTRATION");
        items.push_back("LIGHTING");
        items.push_back("NOTDEFINED");
        items.push_back("PEOPLE");
        items.push_back("RECIRCULATEDAIR");
        items.push_back("RELATIVEHUMIDITY");
        items.push_back("USERDEFINED");
        items.push_back("VENTILATIONINDOORAIR");
        items.push_back("VENTILATIONOUTSIDEAIR");
        IfcThermalLoadSourceEnum_type = new enumeration_type("IfcThermalLoadSourceEnum", items);
    }
    declaration* IfcThermalLoadTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LATENT");
        items.push_back("NOTDEFINED");
        items.push_back("RADIANT");
        items.push_back("SENSIBLE");
        IfcThermalLoadTypeEnum_type = new enumeration_type("IfcThermalLoadTypeEnum", items);
    }
    declaration* IfcTimeSeriesDataTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CONTINUOUS");
        items.push_back("DISCRETE");
        items.push_back("DISCRETEBINARY");
        items.push_back("NOTDEFINED");
        items.push_back("PIECEWISEBINARY");
        items.push_back("PIECEWISECONSTANT");
        items.push_back("PIECEWISECONTINUOUS");
        IfcTimeSeriesDataTypeEnum_type = new enumeration_type("IfcTimeSeriesDataTypeEnum", items);
    }
    declaration* IfcTimeSeriesScheduleTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ANNUAL");
        items.push_back("DAILY");
        items.push_back("MONTHLY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WEEKLY");
        IfcTimeSeriesScheduleTypeEnum_type = new enumeration_type("IfcTimeSeriesScheduleTypeEnum", items);
    }
    declaration* IfcTransformerTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IfcTransformerTypeEnum_type = new enumeration_type("IfcTransformerTypeEnum", items);
    }
    declaration* IfcTransitionCode_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IfcTransitionCode_type = new enumeration_type("IfcTransitionCode", items);
    }
    declaration* IfcTransportElementTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELEVATOR");
        items.push_back("ESCALATOR");
        items.push_back("MOVINGWALKWAY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcTransportElementTypeEnum_type = new enumeration_type("IfcTransportElementTypeEnum", items);
    }
    declaration* IfcTrimmingPreference_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IfcTrimmingPreference_type = new enumeration_type("IfcTrimmingPreference", items);
    }
    declaration* IfcTubeBundleTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcTubeBundleTypeEnum_type = new enumeration_type("IfcTubeBundleTypeEnum", items);
    }
    declaration* IfcUnitEnum_type;
    {
        std::vector<std::string> items; items.reserve(30);
        items.push_back("ABSORBEDDOSEUNIT");
        items.push_back("AMOUNTOFSUBSTANCEUNIT");
        items.push_back("AREAUNIT");
        items.push_back("DOSEEQUIVALENTUNIT");
        items.push_back("ELECTRICCAPACITANCEUNIT");
        items.push_back("ELECTRICCHARGEUNIT");
        items.push_back("ELECTRICCONDUCTANCEUNIT");
        items.push_back("ELECTRICCURRENTUNIT");
        items.push_back("ELECTRICRESISTANCEUNIT");
        items.push_back("ELECTRICVOLTAGEUNIT");
        items.push_back("ENERGYUNIT");
        items.push_back("FORCEUNIT");
        items.push_back("FREQUENCYUNIT");
        items.push_back("ILLUMINANCEUNIT");
        items.push_back("INDUCTANCEUNIT");
        items.push_back("LENGTHUNIT");
        items.push_back("LUMINOUSFLUXUNIT");
        items.push_back("LUMINOUSINTENSITYUNIT");
        items.push_back("MAGNETICFLUXDENSITYUNIT");
        items.push_back("MAGNETICFLUXUNIT");
        items.push_back("MASSUNIT");
        items.push_back("PLANEANGLEUNIT");
        items.push_back("POWERUNIT");
        items.push_back("PRESSUREUNIT");
        items.push_back("RADIOACTIVITYUNIT");
        items.push_back("SOLIDANGLEUNIT");
        items.push_back("THERMODYNAMICTEMPERATUREUNIT");
        items.push_back("TIMEUNIT");
        items.push_back("USERDEFINED");
        items.push_back("VOLUMEUNIT");
        IfcUnitEnum_type = new enumeration_type("IfcUnitEnum", items);
    }
    declaration* IfcUnitaryEquipmentTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AIRCONDITIONINGUNIT");
        items.push_back("AIRHANDLER");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFTOPUNIT");
        items.push_back("SPLITSYSTEM");
        items.push_back("USERDEFINED");
        IfcUnitaryEquipmentTypeEnum_type = new enumeration_type("IfcUnitaryEquipmentTypeEnum", items);
    }
    declaration* IfcValveTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(23);
        items.push_back("AIRRELEASE");
        items.push_back("ANTIVACUUM");
        items.push_back("CHANGEOVER");
        items.push_back("CHECK");
        items.push_back("COMMISSIONING");
        items.push_back("DIVERTING");
        items.push_back("DOUBLECHECK");
        items.push_back("DOUBLEREGULATING");
        items.push_back("DRAWOFFCOCK");
        items.push_back("FAUCET");
        items.push_back("FLUSHING");
        items.push_back("GASCOCK");
        items.push_back("GASTAP");
        items.push_back("ISOLATING");
        items.push_back("MIXING");
        items.push_back("NOTDEFINED");
        items.push_back("PRESSUREREDUCING");
        items.push_back("PRESSURERELIEF");
        items.push_back("REGULATING");
        items.push_back("SAFETYCUTOFF");
        items.push_back("STEAMTRAP");
        items.push_back("STOPCOCK");
        items.push_back("USERDEFINED");
        IfcValveTypeEnum_type = new enumeration_type("IfcValveTypeEnum", items);
    }
    declaration* IfcVibrationIsolatorTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IfcVibrationIsolatorTypeEnum_type = new enumeration_type("IfcVibrationIsolatorTypeEnum", items);
    }
    declaration* IfcWallTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("ELEMENTEDWALL");
        items.push_back("NOTDEFINED");
        items.push_back("PLUMBINGWALL");
        items.push_back("POLYGONAL");
        items.push_back("SHEAR");
        items.push_back("STANDARD");
        items.push_back("USERDEFINED");
        IfcWallTypeEnum_type = new enumeration_type("IfcWallTypeEnum", items);
    }
    declaration* IfcWasteTerminalTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(12);
        items.push_back("FLOORTRAP");
        items.push_back("FLOORWASTE");
        items.push_back("GREASEINTERCEPTOR");
        items.push_back("GULLYSUMP");
        items.push_back("GULLYTRAP");
        items.push_back("NOTDEFINED");
        items.push_back("OILINTERCEPTOR");
        items.push_back("PETROLINTERCEPTOR");
        items.push_back("ROOFDRAIN");
        items.push_back("USERDEFINED");
        items.push_back("WASTEDISPOSALUNIT");
        items.push_back("WASTETRAP");
        IfcWasteTerminalTypeEnum_type = new enumeration_type("IfcWasteTerminalTypeEnum", items);
    }
    declaration* IfcWindowPanelOperationEnum_type;
    {
        std::vector<std::string> items; items.reserve(14);
        items.push_back("BOTTOMHUNG");
        items.push_back("FIXEDCASEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("OTHEROPERATION");
        items.push_back("PIVOTHORIZONTAL");
        items.push_back("PIVOTVERTICAL");
        items.push_back("REMOVABLECASEMENT");
        items.push_back("SIDEHUNGLEFTHAND");
        items.push_back("SIDEHUNGRIGHTHAND");
        items.push_back("SLIDINGHORIZONTAL");
        items.push_back("SLIDINGVERTICAL");
        items.push_back("TILTANDTURNLEFTHAND");
        items.push_back("TILTANDTURNRIGHTHAND");
        items.push_back("TOPHUNG");
        IfcWindowPanelOperationEnum_type = new enumeration_type("IfcWindowPanelOperationEnum", items);
    }
    declaration* IfcWindowPanelPositionEnum_type;
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IfcWindowPanelPositionEnum_type = new enumeration_type("IfcWindowPanelPositionEnum", items);
    }
    declaration* IfcWindowStyleConstructionEnum_type;
    {
        std::vector<std::string> items; items.reserve(8);
        items.push_back("ALUMINIUM");
        items.push_back("ALUMINIUM_WOOD");
        items.push_back("HIGH_GRADE_STEEL");
        items.push_back("NOTDEFINED");
        items.push_back("OTHER_CONSTRUCTION");
        items.push_back("PLASTIC");
        items.push_back("STEEL");
        items.push_back("WOOD");
        IfcWindowStyleConstructionEnum_type = new enumeration_type("IfcWindowStyleConstructionEnum", items);
    }
    declaration* IfcWindowStyleOperationEnum_type;
    {
        std::vector<std::string> items; items.reserve(11);
        items.push_back("DOUBLE_PANEL_HORIZONTAL");
        items.push_back("DOUBLE_PANEL_VERTICAL");
        items.push_back("NOTDEFINED");
        items.push_back("SINGLE_PANEL");
        items.push_back("TRIPLE_PANEL_BOTTOM");
        items.push_back("TRIPLE_PANEL_HORIZONTAL");
        items.push_back("TRIPLE_PANEL_LEFT");
        items.push_back("TRIPLE_PANEL_RIGHT");
        items.push_back("TRIPLE_PANEL_TOP");
        items.push_back("TRIPLE_PANEL_VERTICAL");
        items.push_back("USERDEFINED");
        IfcWindowStyleOperationEnum_type = new enumeration_type("IfcWindowStyleOperationEnum", items);
    }
    declaration* IfcWorkControlTypeEnum_type;
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IfcWorkControlTypeEnum_type = new enumeration_type("IfcWorkControlTypeEnum", items);
    }
    entity* IfcActorRole_type = new entity("IfcActorRole", 0);
    entity* IfcAddress_type = new entity("IfcAddress", 0);
    entity* IfcApplication_type = new entity("IfcApplication", 0);
    entity* IfcAppliedValue_type = new entity("IfcAppliedValue", 0);
    entity* IfcAppliedValueRelationship_type = new entity("IfcAppliedValueRelationship", 0);
    entity* IfcApproval_type = new entity("IfcApproval", 0);
    entity* IfcApprovalActorRelationship_type = new entity("IfcApprovalActorRelationship", 0);
    entity* IfcApprovalPropertyRelationship_type = new entity("IfcApprovalPropertyRelationship", 0);
    entity* IfcApprovalRelationship_type = new entity("IfcApprovalRelationship", 0);
    entity* IfcBoundaryCondition_type = new entity("IfcBoundaryCondition", 0);
    entity* IfcBoundaryEdgeCondition_type = new entity("IfcBoundaryEdgeCondition", IfcBoundaryCondition_type);
    entity* IfcBoundaryFaceCondition_type = new entity("IfcBoundaryFaceCondition", IfcBoundaryCondition_type);
    entity* IfcBoundaryNodeCondition_type = new entity("IfcBoundaryNodeCondition", IfcBoundaryCondition_type);
    entity* IfcBoundaryNodeConditionWarping_type = new entity("IfcBoundaryNodeConditionWarping", IfcBoundaryNodeCondition_type);
    entity* IfcCalendarDate_type = new entity("IfcCalendarDate", 0);
    entity* IfcClassification_type = new entity("IfcClassification", 0);
    entity* IfcClassificationItem_type = new entity("IfcClassificationItem", 0);
    entity* IfcClassificationItemRelationship_type = new entity("IfcClassificationItemRelationship", 0);
    entity* IfcClassificationNotation_type = new entity("IfcClassificationNotation", 0);
    entity* IfcClassificationNotationFacet_type = new entity("IfcClassificationNotationFacet", 0);
    entity* IfcColourSpecification_type = new entity("IfcColourSpecification", 0);
    entity* IfcConnectionGeometry_type = new entity("IfcConnectionGeometry", 0);
    entity* IfcConnectionPointGeometry_type = new entity("IfcConnectionPointGeometry", IfcConnectionGeometry_type);
    entity* IfcConnectionPortGeometry_type = new entity("IfcConnectionPortGeometry", IfcConnectionGeometry_type);
    entity* IfcConnectionSurfaceGeometry_type = new entity("IfcConnectionSurfaceGeometry", IfcConnectionGeometry_type);
    entity* IfcConstraint_type = new entity("IfcConstraint", 0);
    entity* IfcConstraintAggregationRelationship_type = new entity("IfcConstraintAggregationRelationship", 0);
    entity* IfcConstraintClassificationRelationship_type = new entity("IfcConstraintClassificationRelationship", 0);
    entity* IfcConstraintRelationship_type = new entity("IfcConstraintRelationship", 0);
    entity* IfcCoordinatedUniversalTimeOffset_type = new entity("IfcCoordinatedUniversalTimeOffset", 0);
    entity* IfcCostValue_type = new entity("IfcCostValue", IfcAppliedValue_type);
    entity* IfcCurrencyRelationship_type = new entity("IfcCurrencyRelationship", 0);
    entity* IfcCurveStyleFont_type = new entity("IfcCurveStyleFont", 0);
    entity* IfcCurveStyleFontAndScaling_type = new entity("IfcCurveStyleFontAndScaling", 0);
    entity* IfcCurveStyleFontPattern_type = new entity("IfcCurveStyleFontPattern", 0);
    entity* IfcDateAndTime_type = new entity("IfcDateAndTime", 0);
    entity* IfcDerivedUnit_type = new entity("IfcDerivedUnit", 0);
    entity* IfcDerivedUnitElement_type = new entity("IfcDerivedUnitElement", 0);
    entity* IfcDimensionalExponents_type = new entity("IfcDimensionalExponents", 0);
    entity* IfcDocumentElectronicFormat_type = new entity("IfcDocumentElectronicFormat", 0);
    entity* IfcDocumentInformation_type = new entity("IfcDocumentInformation", 0);
    entity* IfcDocumentInformationRelationship_type = new entity("IfcDocumentInformationRelationship", 0);
    entity* IfcDraughtingCalloutRelationship_type = new entity("IfcDraughtingCalloutRelationship", 0);
    entity* IfcEnvironmentalImpactValue_type = new entity("IfcEnvironmentalImpactValue", IfcAppliedValue_type);
    entity* IfcExternalReference_type = new entity("IfcExternalReference", 0);
    entity* IfcExternallyDefinedHatchStyle_type = new entity("IfcExternallyDefinedHatchStyle", IfcExternalReference_type);
    entity* IfcExternallyDefinedSurfaceStyle_type = new entity("IfcExternallyDefinedSurfaceStyle", IfcExternalReference_type);
    entity* IfcExternallyDefinedSymbol_type = new entity("IfcExternallyDefinedSymbol", IfcExternalReference_type);
    entity* IfcExternallyDefinedTextFont_type = new entity("IfcExternallyDefinedTextFont", IfcExternalReference_type);
    entity* IfcGridAxis_type = new entity("IfcGridAxis", 0);
    entity* IfcIrregularTimeSeriesValue_type = new entity("IfcIrregularTimeSeriesValue", 0);
    entity* IfcLibraryInformation_type = new entity("IfcLibraryInformation", 0);
    entity* IfcLibraryReference_type = new entity("IfcLibraryReference", IfcExternalReference_type);
    entity* IfcLightDistributionData_type = new entity("IfcLightDistributionData", 0);
    entity* IfcLightIntensityDistribution_type = new entity("IfcLightIntensityDistribution", 0);
    entity* IfcLocalTime_type = new entity("IfcLocalTime", 0);
    entity* IfcMaterial_type = new entity("IfcMaterial", 0);
    entity* IfcMaterialClassificationRelationship_type = new entity("IfcMaterialClassificationRelationship", 0);
    entity* IfcMaterialLayer_type = new entity("IfcMaterialLayer", 0);
    entity* IfcMaterialLayerSet_type = new entity("IfcMaterialLayerSet", 0);
    entity* IfcMaterialLayerSetUsage_type = new entity("IfcMaterialLayerSetUsage", 0);
    entity* IfcMaterialList_type = new entity("IfcMaterialList", 0);
    entity* IfcMaterialProperties_type = new entity("IfcMaterialProperties", 0);
    entity* IfcMeasureWithUnit_type = new entity("IfcMeasureWithUnit", 0);
    entity* IfcMechanicalMaterialProperties_type = new entity("IfcMechanicalMaterialProperties", IfcMaterialProperties_type);
    entity* IfcMechanicalSteelMaterialProperties_type = new entity("IfcMechanicalSteelMaterialProperties", IfcMechanicalMaterialProperties_type);
    entity* IfcMetric_type = new entity("IfcMetric", IfcConstraint_type);
    entity* IfcMonetaryUnit_type = new entity("IfcMonetaryUnit", 0);
    entity* IfcNamedUnit_type = new entity("IfcNamedUnit", 0);
    entity* IfcObjectPlacement_type = new entity("IfcObjectPlacement", 0);
    entity* IfcObjective_type = new entity("IfcObjective", IfcConstraint_type);
    entity* IfcOpticalMaterialProperties_type = new entity("IfcOpticalMaterialProperties", IfcMaterialProperties_type);
    entity* IfcOrganization_type = new entity("IfcOrganization", 0);
    entity* IfcOrganizationRelationship_type = new entity("IfcOrganizationRelationship", 0);
    entity* IfcOwnerHistory_type = new entity("IfcOwnerHistory", 0);
    entity* IfcPerson_type = new entity("IfcPerson", 0);
    entity* IfcPersonAndOrganization_type = new entity("IfcPersonAndOrganization", 0);
    entity* IfcPhysicalQuantity_type = new entity("IfcPhysicalQuantity", 0);
    entity* IfcPhysicalSimpleQuantity_type = new entity("IfcPhysicalSimpleQuantity", IfcPhysicalQuantity_type);
    entity* IfcPostalAddress_type = new entity("IfcPostalAddress", IfcAddress_type);
    entity* IfcPreDefinedItem_type = new entity("IfcPreDefinedItem", 0);
    entity* IfcPreDefinedSymbol_type = new entity("IfcPreDefinedSymbol", IfcPreDefinedItem_type);
    entity* IfcPreDefinedTerminatorSymbol_type = new entity("IfcPreDefinedTerminatorSymbol", IfcPreDefinedSymbol_type);
    entity* IfcPreDefinedTextFont_type = new entity("IfcPreDefinedTextFont", IfcPreDefinedItem_type);
    entity* IfcPresentationLayerAssignment_type = new entity("IfcPresentationLayerAssignment", 0);
    entity* IfcPresentationLayerWithStyle_type = new entity("IfcPresentationLayerWithStyle", IfcPresentationLayerAssignment_type);
    entity* IfcPresentationStyle_type = new entity("IfcPresentationStyle", 0);
    entity* IfcPresentationStyleAssignment_type = new entity("IfcPresentationStyleAssignment", 0);
    entity* IfcProductRepresentation_type = new entity("IfcProductRepresentation", 0);
    entity* IfcProductsOfCombustionProperties_type = new entity("IfcProductsOfCombustionProperties", IfcMaterialProperties_type);
    entity* IfcProfileDef_type = new entity("IfcProfileDef", 0);
    entity* IfcProfileProperties_type = new entity("IfcProfileProperties", 0);
    entity* IfcProperty_type = new entity("IfcProperty", 0);
    entity* IfcPropertyConstraintRelationship_type = new entity("IfcPropertyConstraintRelationship", 0);
    entity* IfcPropertyDependencyRelationship_type = new entity("IfcPropertyDependencyRelationship", 0);
    entity* IfcPropertyEnumeration_type = new entity("IfcPropertyEnumeration", 0);
    entity* IfcQuantityArea_type = new entity("IfcQuantityArea", IfcPhysicalSimpleQuantity_type);
    entity* IfcQuantityCount_type = new entity("IfcQuantityCount", IfcPhysicalSimpleQuantity_type);
    entity* IfcQuantityLength_type = new entity("IfcQuantityLength", IfcPhysicalSimpleQuantity_type);
    entity* IfcQuantityTime_type = new entity("IfcQuantityTime", IfcPhysicalSimpleQuantity_type);
    entity* IfcQuantityVolume_type = new entity("IfcQuantityVolume", IfcPhysicalSimpleQuantity_type);
    entity* IfcQuantityWeight_type = new entity("IfcQuantityWeight", IfcPhysicalSimpleQuantity_type);
    entity* IfcReferencesValueDocument_type = new entity("IfcReferencesValueDocument", 0);
    entity* IfcReinforcementBarProperties_type = new entity("IfcReinforcementBarProperties", 0);
    entity* IfcRelaxation_type = new entity("IfcRelaxation", 0);
    entity* IfcRepresentation_type = new entity("IfcRepresentation", 0);
    entity* IfcRepresentationContext_type = new entity("IfcRepresentationContext", 0);
    entity* IfcRepresentationItem_type = new entity("IfcRepresentationItem", 0);
    entity* IfcRepresentationMap_type = new entity("IfcRepresentationMap", 0);
    entity* IfcRibPlateProfileProperties_type = new entity("IfcRibPlateProfileProperties", IfcProfileProperties_type);
    entity* IfcRoot_type = new entity("IfcRoot", 0);
    entity* IfcSIUnit_type = new entity("IfcSIUnit", IfcNamedUnit_type);
    entity* IfcSectionProperties_type = new entity("IfcSectionProperties", 0);
    entity* IfcSectionReinforcementProperties_type = new entity("IfcSectionReinforcementProperties", 0);
    entity* IfcShapeAspect_type = new entity("IfcShapeAspect", 0);
    entity* IfcShapeModel_type = new entity("IfcShapeModel", IfcRepresentation_type);
    entity* IfcShapeRepresentation_type = new entity("IfcShapeRepresentation", IfcShapeModel_type);
    entity* IfcSimpleProperty_type = new entity("IfcSimpleProperty", IfcProperty_type);
    entity* IfcStructuralConnectionCondition_type = new entity("IfcStructuralConnectionCondition", 0);
    entity* IfcStructuralLoad_type = new entity("IfcStructuralLoad", 0);
    entity* IfcStructuralLoadStatic_type = new entity("IfcStructuralLoadStatic", IfcStructuralLoad_type);
    entity* IfcStructuralLoadTemperature_type = new entity("IfcStructuralLoadTemperature", IfcStructuralLoadStatic_type);
    entity* IfcStyleModel_type = new entity("IfcStyleModel", IfcRepresentation_type);
    entity* IfcStyledItem_type = new entity("IfcStyledItem", IfcRepresentationItem_type);
    entity* IfcStyledRepresentation_type = new entity("IfcStyledRepresentation", IfcStyleModel_type);
    entity* IfcSurfaceStyle_type = new entity("IfcSurfaceStyle", IfcPresentationStyle_type);
    entity* IfcSurfaceStyleLighting_type = new entity("IfcSurfaceStyleLighting", 0);
    entity* IfcSurfaceStyleRefraction_type = new entity("IfcSurfaceStyleRefraction", 0);
    entity* IfcSurfaceStyleShading_type = new entity("IfcSurfaceStyleShading", 0);
    entity* IfcSurfaceStyleWithTextures_type = new entity("IfcSurfaceStyleWithTextures", 0);
    entity* IfcSurfaceTexture_type = new entity("IfcSurfaceTexture", 0);
    entity* IfcSymbolStyle_type = new entity("IfcSymbolStyle", IfcPresentationStyle_type);
    entity* IfcTable_type = new entity("IfcTable", 0);
    entity* IfcTableRow_type = new entity("IfcTableRow", 0);
    entity* IfcTelecomAddress_type = new entity("IfcTelecomAddress", IfcAddress_type);
    entity* IfcTextStyle_type = new entity("IfcTextStyle", IfcPresentationStyle_type);
    entity* IfcTextStyleFontModel_type = new entity("IfcTextStyleFontModel", IfcPreDefinedTextFont_type);
    entity* IfcTextStyleForDefinedFont_type = new entity("IfcTextStyleForDefinedFont", 0);
    entity* IfcTextStyleTextModel_type = new entity("IfcTextStyleTextModel", 0);
    entity* IfcTextStyleWithBoxCharacteristics_type = new entity("IfcTextStyleWithBoxCharacteristics", 0);
    entity* IfcTextureCoordinate_type = new entity("IfcTextureCoordinate", 0);
    entity* IfcTextureCoordinateGenerator_type = new entity("IfcTextureCoordinateGenerator", IfcTextureCoordinate_type);
    entity* IfcTextureMap_type = new entity("IfcTextureMap", IfcTextureCoordinate_type);
    entity* IfcTextureVertex_type = new entity("IfcTextureVertex", 0);
    entity* IfcThermalMaterialProperties_type = new entity("IfcThermalMaterialProperties", IfcMaterialProperties_type);
    entity* IfcTimeSeries_type = new entity("IfcTimeSeries", 0);
    entity* IfcTimeSeriesReferenceRelationship_type = new entity("IfcTimeSeriesReferenceRelationship", 0);
    entity* IfcTimeSeriesValue_type = new entity("IfcTimeSeriesValue", 0);
    entity* IfcTopologicalRepresentationItem_type = new entity("IfcTopologicalRepresentationItem", IfcRepresentationItem_type);
    entity* IfcTopologyRepresentation_type = new entity("IfcTopologyRepresentation", IfcShapeModel_type);
    entity* IfcUnitAssignment_type = new entity("IfcUnitAssignment", 0);
    entity* IfcVertex_type = new entity("IfcVertex", IfcTopologicalRepresentationItem_type);
    entity* IfcVertexBasedTextureMap_type = new entity("IfcVertexBasedTextureMap", 0);
    entity* IfcVertexPoint_type = new entity("IfcVertexPoint", IfcVertex_type);
    entity* IfcVirtualGridIntersection_type = new entity("IfcVirtualGridIntersection", 0);
    entity* IfcWaterProperties_type = new entity("IfcWaterProperties", IfcMaterialProperties_type);
    entity* IfcAnnotationOccurrence_type = new entity("IfcAnnotationOccurrence", IfcStyledItem_type);
    entity* IfcAnnotationSurfaceOccurrence_type = new entity("IfcAnnotationSurfaceOccurrence", IfcAnnotationOccurrence_type);
    entity* IfcAnnotationSymbolOccurrence_type = new entity("IfcAnnotationSymbolOccurrence", IfcAnnotationOccurrence_type);
    entity* IfcAnnotationTextOccurrence_type = new entity("IfcAnnotationTextOccurrence", IfcAnnotationOccurrence_type);
    entity* IfcArbitraryClosedProfileDef_type = new entity("IfcArbitraryClosedProfileDef", IfcProfileDef_type);
    entity* IfcArbitraryOpenProfileDef_type = new entity("IfcArbitraryOpenProfileDef", IfcProfileDef_type);
    entity* IfcArbitraryProfileDefWithVoids_type = new entity("IfcArbitraryProfileDefWithVoids", IfcArbitraryClosedProfileDef_type);
    entity* IfcBlobTexture_type = new entity("IfcBlobTexture", IfcSurfaceTexture_type);
    entity* IfcCenterLineProfileDef_type = new entity("IfcCenterLineProfileDef", IfcArbitraryOpenProfileDef_type);
    entity* IfcClassificationReference_type = new entity("IfcClassificationReference", IfcExternalReference_type);
    entity* IfcColourRgb_type = new entity("IfcColourRgb", IfcColourSpecification_type);
    entity* IfcComplexProperty_type = new entity("IfcComplexProperty", IfcProperty_type);
    entity* IfcCompositeProfileDef_type = new entity("IfcCompositeProfileDef", IfcProfileDef_type);
    entity* IfcConnectedFaceSet_type = new entity("IfcConnectedFaceSet", IfcTopologicalRepresentationItem_type);
    entity* IfcConnectionCurveGeometry_type = new entity("IfcConnectionCurveGeometry", IfcConnectionGeometry_type);
    entity* IfcConnectionPointEccentricity_type = new entity("IfcConnectionPointEccentricity", IfcConnectionPointGeometry_type);
    entity* IfcContextDependentUnit_type = new entity("IfcContextDependentUnit", IfcNamedUnit_type);
    entity* IfcConversionBasedUnit_type = new entity("IfcConversionBasedUnit", IfcNamedUnit_type);
    entity* IfcCurveStyle_type = new entity("IfcCurveStyle", IfcPresentationStyle_type);
    entity* IfcDerivedProfileDef_type = new entity("IfcDerivedProfileDef", IfcProfileDef_type);
    entity* IfcDimensionCalloutRelationship_type = new entity("IfcDimensionCalloutRelationship", IfcDraughtingCalloutRelationship_type);
    entity* IfcDimensionPair_type = new entity("IfcDimensionPair", IfcDraughtingCalloutRelationship_type);
    entity* IfcDocumentReference_type = new entity("IfcDocumentReference", IfcExternalReference_type);
    entity* IfcDraughtingPreDefinedTextFont_type = new entity("IfcDraughtingPreDefinedTextFont", IfcPreDefinedTextFont_type);
    entity* IfcEdge_type = new entity("IfcEdge", IfcTopologicalRepresentationItem_type);
    entity* IfcEdgeCurve_type = new entity("IfcEdgeCurve", IfcEdge_type);
    entity* IfcExtendedMaterialProperties_type = new entity("IfcExtendedMaterialProperties", IfcMaterialProperties_type);
    entity* IfcFace_type = new entity("IfcFace", IfcTopologicalRepresentationItem_type);
    entity* IfcFaceBound_type = new entity("IfcFaceBound", IfcTopologicalRepresentationItem_type);
    entity* IfcFaceOuterBound_type = new entity("IfcFaceOuterBound", IfcFaceBound_type);
    entity* IfcFaceSurface_type = new entity("IfcFaceSurface", IfcFace_type);
    entity* IfcFailureConnectionCondition_type = new entity("IfcFailureConnectionCondition", IfcStructuralConnectionCondition_type);
    entity* IfcFillAreaStyle_type = new entity("IfcFillAreaStyle", IfcPresentationStyle_type);
    entity* IfcFuelProperties_type = new entity("IfcFuelProperties", IfcMaterialProperties_type);
    entity* IfcGeneralMaterialProperties_type = new entity("IfcGeneralMaterialProperties", IfcMaterialProperties_type);
    entity* IfcGeneralProfileProperties_type = new entity("IfcGeneralProfileProperties", IfcProfileProperties_type);
    entity* IfcGeometricRepresentationContext_type = new entity("IfcGeometricRepresentationContext", IfcRepresentationContext_type);
    entity* IfcGeometricRepresentationItem_type = new entity("IfcGeometricRepresentationItem", IfcRepresentationItem_type);
    entity* IfcGeometricRepresentationSubContext_type = new entity("IfcGeometricRepresentationSubContext", IfcGeometricRepresentationContext_type);
    entity* IfcGeometricSet_type = new entity("IfcGeometricSet", IfcGeometricRepresentationItem_type);
    entity* IfcGridPlacement_type = new entity("IfcGridPlacement", IfcObjectPlacement_type);
    entity* IfcHalfSpaceSolid_type = new entity("IfcHalfSpaceSolid", IfcGeometricRepresentationItem_type);
    entity* IfcHygroscopicMaterialProperties_type = new entity("IfcHygroscopicMaterialProperties", IfcMaterialProperties_type);
    entity* IfcImageTexture_type = new entity("IfcImageTexture", IfcSurfaceTexture_type);
    entity* IfcIrregularTimeSeries_type = new entity("IfcIrregularTimeSeries", IfcTimeSeries_type);
    entity* IfcLightSource_type = new entity("IfcLightSource", IfcGeometricRepresentationItem_type);
    entity* IfcLightSourceAmbient_type = new entity("IfcLightSourceAmbient", IfcLightSource_type);
    entity* IfcLightSourceDirectional_type = new entity("IfcLightSourceDirectional", IfcLightSource_type);
    entity* IfcLightSourceGoniometric_type = new entity("IfcLightSourceGoniometric", IfcLightSource_type);
    entity* IfcLightSourcePositional_type = new entity("IfcLightSourcePositional", IfcLightSource_type);
    entity* IfcLightSourceSpot_type = new entity("IfcLightSourceSpot", IfcLightSourcePositional_type);
    entity* IfcLocalPlacement_type = new entity("IfcLocalPlacement", IfcObjectPlacement_type);
    entity* IfcLoop_type = new entity("IfcLoop", IfcTopologicalRepresentationItem_type);
    entity* IfcMappedItem_type = new entity("IfcMappedItem", IfcRepresentationItem_type);
    entity* IfcMaterialDefinitionRepresentation_type = new entity("IfcMaterialDefinitionRepresentation", IfcProductRepresentation_type);
    entity* IfcMechanicalConcreteMaterialProperties_type = new entity("IfcMechanicalConcreteMaterialProperties", IfcMechanicalMaterialProperties_type);
    entity* IfcObjectDefinition_type = new entity("IfcObjectDefinition", IfcRoot_type);
    entity* IfcOneDirectionRepeatFactor_type = new entity("IfcOneDirectionRepeatFactor", IfcGeometricRepresentationItem_type);
    entity* IfcOpenShell_type = new entity("IfcOpenShell", IfcConnectedFaceSet_type);
    entity* IfcOrientedEdge_type = new entity("IfcOrientedEdge", IfcEdge_type);
    entity* IfcParameterizedProfileDef_type = new entity("IfcParameterizedProfileDef", IfcProfileDef_type);
    entity* IfcPath_type = new entity("IfcPath", IfcTopologicalRepresentationItem_type);
    entity* IfcPhysicalComplexQuantity_type = new entity("IfcPhysicalComplexQuantity", IfcPhysicalQuantity_type);
    entity* IfcPixelTexture_type = new entity("IfcPixelTexture", IfcSurfaceTexture_type);
    entity* IfcPlacement_type = new entity("IfcPlacement", IfcGeometricRepresentationItem_type);
    entity* IfcPlanarExtent_type = new entity("IfcPlanarExtent", IfcGeometricRepresentationItem_type);
    entity* IfcPoint_type = new entity("IfcPoint", IfcGeometricRepresentationItem_type);
    entity* IfcPointOnCurve_type = new entity("IfcPointOnCurve", IfcPoint_type);
    entity* IfcPointOnSurface_type = new entity("IfcPointOnSurface", IfcPoint_type);
    entity* IfcPolyLoop_type = new entity("IfcPolyLoop", IfcLoop_type);
    entity* IfcPolygonalBoundedHalfSpace_type = new entity("IfcPolygonalBoundedHalfSpace", IfcHalfSpaceSolid_type);
    entity* IfcPreDefinedColour_type = new entity("IfcPreDefinedColour", IfcPreDefinedItem_type);
    entity* IfcPreDefinedCurveFont_type = new entity("IfcPreDefinedCurveFont", IfcPreDefinedItem_type);
    entity* IfcPreDefinedDimensionSymbol_type = new entity("IfcPreDefinedDimensionSymbol", IfcPreDefinedSymbol_type);
    entity* IfcPreDefinedPointMarkerSymbol_type = new entity("IfcPreDefinedPointMarkerSymbol", IfcPreDefinedSymbol_type);
    entity* IfcProductDefinitionShape_type = new entity("IfcProductDefinitionShape", IfcProductRepresentation_type);
    entity* IfcPropertyBoundedValue_type = new entity("IfcPropertyBoundedValue", IfcSimpleProperty_type);
    entity* IfcPropertyDefinition_type = new entity("IfcPropertyDefinition", IfcRoot_type);
    entity* IfcPropertyEnumeratedValue_type = new entity("IfcPropertyEnumeratedValue", IfcSimpleProperty_type);
    entity* IfcPropertyListValue_type = new entity("IfcPropertyListValue", IfcSimpleProperty_type);
    entity* IfcPropertyReferenceValue_type = new entity("IfcPropertyReferenceValue", IfcSimpleProperty_type);
    entity* IfcPropertySetDefinition_type = new entity("IfcPropertySetDefinition", IfcPropertyDefinition_type);
    entity* IfcPropertySingleValue_type = new entity("IfcPropertySingleValue", IfcSimpleProperty_type);
    entity* IfcPropertyTableValue_type = new entity("IfcPropertyTableValue", IfcSimpleProperty_type);
    entity* IfcRectangleProfileDef_type = new entity("IfcRectangleProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcRegularTimeSeries_type = new entity("IfcRegularTimeSeries", IfcTimeSeries_type);
    entity* IfcReinforcementDefinitionProperties_type = new entity("IfcReinforcementDefinitionProperties", IfcPropertySetDefinition_type);
    entity* IfcRelationship_type = new entity("IfcRelationship", IfcRoot_type);
    entity* IfcRoundedRectangleProfileDef_type = new entity("IfcRoundedRectangleProfileDef", IfcRectangleProfileDef_type);
    entity* IfcSectionedSpine_type = new entity("IfcSectionedSpine", IfcGeometricRepresentationItem_type);
    entity* IfcServiceLifeFactor_type = new entity("IfcServiceLifeFactor", IfcPropertySetDefinition_type);
    entity* IfcShellBasedSurfaceModel_type = new entity("IfcShellBasedSurfaceModel", IfcGeometricRepresentationItem_type);
    entity* IfcSlippageConnectionCondition_type = new entity("IfcSlippageConnectionCondition", IfcStructuralConnectionCondition_type);
    entity* IfcSolidModel_type = new entity("IfcSolidModel", IfcGeometricRepresentationItem_type);
    entity* IfcSoundProperties_type = new entity("IfcSoundProperties", IfcPropertySetDefinition_type);
    entity* IfcSoundValue_type = new entity("IfcSoundValue", IfcPropertySetDefinition_type);
    entity* IfcSpaceThermalLoadProperties_type = new entity("IfcSpaceThermalLoadProperties", IfcPropertySetDefinition_type);
    entity* IfcStructuralLoadLinearForce_type = new entity("IfcStructuralLoadLinearForce", IfcStructuralLoadStatic_type);
    entity* IfcStructuralLoadPlanarForce_type = new entity("IfcStructuralLoadPlanarForce", IfcStructuralLoadStatic_type);
    entity* IfcStructuralLoadSingleDisplacement_type = new entity("IfcStructuralLoadSingleDisplacement", IfcStructuralLoadStatic_type);
    entity* IfcStructuralLoadSingleDisplacementDistortion_type = new entity("IfcStructuralLoadSingleDisplacementDistortion", IfcStructuralLoadSingleDisplacement_type);
    entity* IfcStructuralLoadSingleForce_type = new entity("IfcStructuralLoadSingleForce", IfcStructuralLoadStatic_type);
    entity* IfcStructuralLoadSingleForceWarping_type = new entity("IfcStructuralLoadSingleForceWarping", IfcStructuralLoadSingleForce_type);
    entity* IfcStructuralProfileProperties_type = new entity("IfcStructuralProfileProperties", IfcGeneralProfileProperties_type);
    entity* IfcStructuralSteelProfileProperties_type = new entity("IfcStructuralSteelProfileProperties", IfcStructuralProfileProperties_type);
    entity* IfcSubedge_type = new entity("IfcSubedge", IfcEdge_type);
    entity* IfcSurface_type = new entity("IfcSurface", IfcGeometricRepresentationItem_type);
    entity* IfcSurfaceStyleRendering_type = new entity("IfcSurfaceStyleRendering", IfcSurfaceStyleShading_type);
    entity* IfcSweptAreaSolid_type = new entity("IfcSweptAreaSolid", IfcSolidModel_type);
    entity* IfcSweptDiskSolid_type = new entity("IfcSweptDiskSolid", IfcSolidModel_type);
    entity* IfcSweptSurface_type = new entity("IfcSweptSurface", IfcSurface_type);
    entity* IfcTShapeProfileDef_type = new entity("IfcTShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcTerminatorSymbol_type = new entity("IfcTerminatorSymbol", IfcAnnotationSymbolOccurrence_type);
    entity* IfcTextLiteral_type = new entity("IfcTextLiteral", IfcGeometricRepresentationItem_type);
    entity* IfcTextLiteralWithExtent_type = new entity("IfcTextLiteralWithExtent", IfcTextLiteral_type);
    entity* IfcTrapeziumProfileDef_type = new entity("IfcTrapeziumProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcTwoDirectionRepeatFactor_type = new entity("IfcTwoDirectionRepeatFactor", IfcOneDirectionRepeatFactor_type);
    entity* IfcTypeObject_type = new entity("IfcTypeObject", IfcObjectDefinition_type);
    entity* IfcTypeProduct_type = new entity("IfcTypeProduct", IfcTypeObject_type);
    entity* IfcUShapeProfileDef_type = new entity("IfcUShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcVector_type = new entity("IfcVector", IfcGeometricRepresentationItem_type);
    entity* IfcVertexLoop_type = new entity("IfcVertexLoop", IfcLoop_type);
    entity* IfcWindowLiningProperties_type = new entity("IfcWindowLiningProperties", IfcPropertySetDefinition_type);
    entity* IfcWindowPanelProperties_type = new entity("IfcWindowPanelProperties", IfcPropertySetDefinition_type);
    entity* IfcWindowStyle_type = new entity("IfcWindowStyle", IfcTypeProduct_type);
    entity* IfcZShapeProfileDef_type = new entity("IfcZShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcAnnotationCurveOccurrence_type = new entity("IfcAnnotationCurveOccurrence", IfcAnnotationOccurrence_type);
    entity* IfcAnnotationFillArea_type = new entity("IfcAnnotationFillArea", IfcGeometricRepresentationItem_type);
    entity* IfcAnnotationFillAreaOccurrence_type = new entity("IfcAnnotationFillAreaOccurrence", IfcAnnotationOccurrence_type);
    entity* IfcAnnotationSurface_type = new entity("IfcAnnotationSurface", IfcGeometricRepresentationItem_type);
    entity* IfcAxis1Placement_type = new entity("IfcAxis1Placement", IfcPlacement_type);
    entity* IfcAxis2Placement2D_type = new entity("IfcAxis2Placement2D", IfcPlacement_type);
    entity* IfcAxis2Placement3D_type = new entity("IfcAxis2Placement3D", IfcPlacement_type);
    entity* IfcBooleanResult_type = new entity("IfcBooleanResult", IfcGeometricRepresentationItem_type);
    entity* IfcBoundedSurface_type = new entity("IfcBoundedSurface", IfcSurface_type);
    entity* IfcBoundingBox_type = new entity("IfcBoundingBox", IfcGeometricRepresentationItem_type);
    entity* IfcBoxedHalfSpace_type = new entity("IfcBoxedHalfSpace", IfcHalfSpaceSolid_type);
    entity* IfcCShapeProfileDef_type = new entity("IfcCShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcCartesianPoint_type = new entity("IfcCartesianPoint", IfcPoint_type);
    entity* IfcCartesianTransformationOperator_type = new entity("IfcCartesianTransformationOperator", IfcGeometricRepresentationItem_type);
    entity* IfcCartesianTransformationOperator2D_type = new entity("IfcCartesianTransformationOperator2D", IfcCartesianTransformationOperator_type);
    entity* IfcCartesianTransformationOperator2DnonUniform_type = new entity("IfcCartesianTransformationOperator2DnonUniform", IfcCartesianTransformationOperator2D_type);
    entity* IfcCartesianTransformationOperator3D_type = new entity("IfcCartesianTransformationOperator3D", IfcCartesianTransformationOperator_type);
    entity* IfcCartesianTransformationOperator3DnonUniform_type = new entity("IfcCartesianTransformationOperator3DnonUniform", IfcCartesianTransformationOperator3D_type);
    entity* IfcCircleProfileDef_type = new entity("IfcCircleProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcClosedShell_type = new entity("IfcClosedShell", IfcConnectedFaceSet_type);
    entity* IfcCompositeCurveSegment_type = new entity("IfcCompositeCurveSegment", IfcGeometricRepresentationItem_type);
    entity* IfcCraneRailAShapeProfileDef_type = new entity("IfcCraneRailAShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcCraneRailFShapeProfileDef_type = new entity("IfcCraneRailFShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcCsgPrimitive3D_type = new entity("IfcCsgPrimitive3D", IfcGeometricRepresentationItem_type);
    entity* IfcCsgSolid_type = new entity("IfcCsgSolid", IfcSolidModel_type);
    entity* IfcCurve_type = new entity("IfcCurve", IfcGeometricRepresentationItem_type);
    entity* IfcCurveBoundedPlane_type = new entity("IfcCurveBoundedPlane", IfcBoundedSurface_type);
    entity* IfcDefinedSymbol_type = new entity("IfcDefinedSymbol", IfcGeometricRepresentationItem_type);
    entity* IfcDimensionCurve_type = new entity("IfcDimensionCurve", IfcAnnotationCurveOccurrence_type);
    entity* IfcDimensionCurveTerminator_type = new entity("IfcDimensionCurveTerminator", IfcTerminatorSymbol_type);
    entity* IfcDirection_type = new entity("IfcDirection", IfcGeometricRepresentationItem_type);
    entity* IfcDoorLiningProperties_type = new entity("IfcDoorLiningProperties", IfcPropertySetDefinition_type);
    entity* IfcDoorPanelProperties_type = new entity("IfcDoorPanelProperties", IfcPropertySetDefinition_type);
    entity* IfcDoorStyle_type = new entity("IfcDoorStyle", IfcTypeProduct_type);
    entity* IfcDraughtingCallout_type = new entity("IfcDraughtingCallout", IfcGeometricRepresentationItem_type);
    entity* IfcDraughtingPreDefinedColour_type = new entity("IfcDraughtingPreDefinedColour", IfcPreDefinedColour_type);
    entity* IfcDraughtingPreDefinedCurveFont_type = new entity("IfcDraughtingPreDefinedCurveFont", IfcPreDefinedCurveFont_type);
    entity* IfcEdgeLoop_type = new entity("IfcEdgeLoop", IfcLoop_type);
    entity* IfcElementQuantity_type = new entity("IfcElementQuantity", IfcPropertySetDefinition_type);
    entity* IfcElementType_type = new entity("IfcElementType", IfcTypeProduct_type);
    entity* IfcElementarySurface_type = new entity("IfcElementarySurface", IfcSurface_type);
    entity* IfcEllipseProfileDef_type = new entity("IfcEllipseProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcEnergyProperties_type = new entity("IfcEnergyProperties", IfcPropertySetDefinition_type);
    entity* IfcExtrudedAreaSolid_type = new entity("IfcExtrudedAreaSolid", IfcSweptAreaSolid_type);
    entity* IfcFaceBasedSurfaceModel_type = new entity("IfcFaceBasedSurfaceModel", IfcGeometricRepresentationItem_type);
    entity* IfcFillAreaStyleHatching_type = new entity("IfcFillAreaStyleHatching", IfcGeometricRepresentationItem_type);
    entity* IfcFillAreaStyleTileSymbolWithStyle_type = new entity("IfcFillAreaStyleTileSymbolWithStyle", IfcGeometricRepresentationItem_type);
    entity* IfcFillAreaStyleTiles_type = new entity("IfcFillAreaStyleTiles", IfcGeometricRepresentationItem_type);
    entity* IfcFluidFlowProperties_type = new entity("IfcFluidFlowProperties", IfcPropertySetDefinition_type);
    entity* IfcFurnishingElementType_type = new entity("IfcFurnishingElementType", IfcElementType_type);
    entity* IfcFurnitureType_type = new entity("IfcFurnitureType", IfcFurnishingElementType_type);
    entity* IfcGeometricCurveSet_type = new entity("IfcGeometricCurveSet", IfcGeometricSet_type);
    entity* IfcIShapeProfileDef_type = new entity("IfcIShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcLShapeProfileDef_type = new entity("IfcLShapeProfileDef", IfcParameterizedProfileDef_type);
    entity* IfcLine_type = new entity("IfcLine", IfcCurve_type);
    entity* IfcManifoldSolidBrep_type = new entity("IfcManifoldSolidBrep", IfcSolidModel_type);
    entity* IfcObject_type = new entity("IfcObject", IfcObjectDefinition_type);
    entity* IfcOffsetCurve2D_type = new entity("IfcOffsetCurve2D", IfcCurve_type);
    entity* IfcOffsetCurve3D_type = new entity("IfcOffsetCurve3D", IfcCurve_type);
    entity* IfcPermeableCoveringProperties_type = new entity("IfcPermeableCoveringProperties", IfcPropertySetDefinition_type);
    entity* IfcPlanarBox_type = new entity("IfcPlanarBox", IfcPlanarExtent_type);
    entity* IfcPlane_type = new entity("IfcPlane", IfcElementarySurface_type);
    entity* IfcProcess_type = new entity("IfcProcess", IfcObject_type);
    entity* IfcProduct_type = new entity("IfcProduct", IfcObject_type);
    entity* IfcProject_type = new entity("IfcProject", IfcObject_type);
    entity* IfcProjectionCurve_type = new entity("IfcProjectionCurve", IfcAnnotationCurveOccurrence_type);
    entity* IfcPropertySet_type = new entity("IfcPropertySet", IfcPropertySetDefinition_type);
    entity* IfcProxy_type = new entity("IfcProxy", IfcProduct_type);
    entity* IfcRectangleHollowProfileDef_type = new entity("IfcRectangleHollowProfileDef", IfcRectangleProfileDef_type);
    entity* IfcRectangularPyramid_type = new entity("IfcRectangularPyramid", IfcCsgPrimitive3D_type);
    entity* IfcRectangularTrimmedSurface_type = new entity("IfcRectangularTrimmedSurface", IfcBoundedSurface_type);
    entity* IfcRelAssigns_type = new entity("IfcRelAssigns", IfcRelationship_type);
    entity* IfcRelAssignsToActor_type = new entity("IfcRelAssignsToActor", IfcRelAssigns_type);
    entity* IfcRelAssignsToControl_type = new entity("IfcRelAssignsToControl", IfcRelAssigns_type);
    entity* IfcRelAssignsToGroup_type = new entity("IfcRelAssignsToGroup", IfcRelAssigns_type);
    entity* IfcRelAssignsToProcess_type = new entity("IfcRelAssignsToProcess", IfcRelAssigns_type);
    entity* IfcRelAssignsToProduct_type = new entity("IfcRelAssignsToProduct", IfcRelAssigns_type);
    entity* IfcRelAssignsToProjectOrder_type = new entity("IfcRelAssignsToProjectOrder", IfcRelAssignsToControl_type);
    entity* IfcRelAssignsToResource_type = new entity("IfcRelAssignsToResource", IfcRelAssigns_type);
    entity* IfcRelAssociates_type = new entity("IfcRelAssociates", IfcRelationship_type);
    entity* IfcRelAssociatesAppliedValue_type = new entity("IfcRelAssociatesAppliedValue", IfcRelAssociates_type);
    entity* IfcRelAssociatesApproval_type = new entity("IfcRelAssociatesApproval", IfcRelAssociates_type);
    entity* IfcRelAssociatesClassification_type = new entity("IfcRelAssociatesClassification", IfcRelAssociates_type);
    entity* IfcRelAssociatesConstraint_type = new entity("IfcRelAssociatesConstraint", IfcRelAssociates_type);
    entity* IfcRelAssociatesDocument_type = new entity("IfcRelAssociatesDocument", IfcRelAssociates_type);
    entity* IfcRelAssociatesLibrary_type = new entity("IfcRelAssociatesLibrary", IfcRelAssociates_type);
    entity* IfcRelAssociatesMaterial_type = new entity("IfcRelAssociatesMaterial", IfcRelAssociates_type);
    entity* IfcRelAssociatesProfileProperties_type = new entity("IfcRelAssociatesProfileProperties", IfcRelAssociates_type);
    entity* IfcRelConnects_type = new entity("IfcRelConnects", IfcRelationship_type);
    entity* IfcRelConnectsElements_type = new entity("IfcRelConnectsElements", IfcRelConnects_type);
    entity* IfcRelConnectsPathElements_type = new entity("IfcRelConnectsPathElements", IfcRelConnectsElements_type);
    entity* IfcRelConnectsPortToElement_type = new entity("IfcRelConnectsPortToElement", IfcRelConnects_type);
    entity* IfcRelConnectsPorts_type = new entity("IfcRelConnectsPorts", IfcRelConnects_type);
    entity* IfcRelConnectsStructuralActivity_type = new entity("IfcRelConnectsStructuralActivity", IfcRelConnects_type);
    entity* IfcRelConnectsStructuralElement_type = new entity("IfcRelConnectsStructuralElement", IfcRelConnects_type);
    entity* IfcRelConnectsStructuralMember_type = new entity("IfcRelConnectsStructuralMember", IfcRelConnects_type);
    entity* IfcRelConnectsWithEccentricity_type = new entity("IfcRelConnectsWithEccentricity", IfcRelConnectsStructuralMember_type);
    entity* IfcRelConnectsWithRealizingElements_type = new entity("IfcRelConnectsWithRealizingElements", IfcRelConnectsElements_type);
    entity* IfcRelContainedInSpatialStructure_type = new entity("IfcRelContainedInSpatialStructure", IfcRelConnects_type);
    entity* IfcRelCoversBldgElements_type = new entity("IfcRelCoversBldgElements", IfcRelConnects_type);
    entity* IfcRelCoversSpaces_type = new entity("IfcRelCoversSpaces", IfcRelConnects_type);
    entity* IfcRelDecomposes_type = new entity("IfcRelDecomposes", IfcRelationship_type);
    entity* IfcRelDefines_type = new entity("IfcRelDefines", IfcRelationship_type);
    entity* IfcRelDefinesByProperties_type = new entity("IfcRelDefinesByProperties", IfcRelDefines_type);
    entity* IfcRelDefinesByType_type = new entity("IfcRelDefinesByType", IfcRelDefines_type);
    entity* IfcRelFillsElement_type = new entity("IfcRelFillsElement", IfcRelConnects_type);
    entity* IfcRelFlowControlElements_type = new entity("IfcRelFlowControlElements", IfcRelConnects_type);
    entity* IfcRelInteractionRequirements_type = new entity("IfcRelInteractionRequirements", IfcRelConnects_type);
    entity* IfcRelNests_type = new entity("IfcRelNests", IfcRelDecomposes_type);
    entity* IfcRelOccupiesSpaces_type = new entity("IfcRelOccupiesSpaces", IfcRelAssignsToActor_type);
    entity* IfcRelOverridesProperties_type = new entity("IfcRelOverridesProperties", IfcRelDefinesByProperties_type);
    entity* IfcRelProjectsElement_type = new entity("IfcRelProjectsElement", IfcRelConnects_type);
    entity* IfcRelReferencedInSpatialStructure_type = new entity("IfcRelReferencedInSpatialStructure", IfcRelConnects_type);
    entity* IfcRelSchedulesCostItems_type = new entity("IfcRelSchedulesCostItems", IfcRelAssignsToControl_type);
    entity* IfcRelSequence_type = new entity("IfcRelSequence", IfcRelConnects_type);
    entity* IfcRelServicesBuildings_type = new entity("IfcRelServicesBuildings", IfcRelConnects_type);
    entity* IfcRelSpaceBoundary_type = new entity("IfcRelSpaceBoundary", IfcRelConnects_type);
    entity* IfcRelVoidsElement_type = new entity("IfcRelVoidsElement", IfcRelConnects_type);
    entity* IfcResource_type = new entity("IfcResource", IfcObject_type);
    entity* IfcRevolvedAreaSolid_type = new entity("IfcRevolvedAreaSolid", IfcSweptAreaSolid_type);
    entity* IfcRightCircularCone_type = new entity("IfcRightCircularCone", IfcCsgPrimitive3D_type);
    entity* IfcRightCircularCylinder_type = new entity("IfcRightCircularCylinder", IfcCsgPrimitive3D_type);
    entity* IfcSpatialStructureElement_type = new entity("IfcSpatialStructureElement", IfcProduct_type);
    entity* IfcSpatialStructureElementType_type = new entity("IfcSpatialStructureElementType", IfcElementType_type);
    entity* IfcSphere_type = new entity("IfcSphere", IfcCsgPrimitive3D_type);
    entity* IfcStructuralActivity_type = new entity("IfcStructuralActivity", IfcProduct_type);
    entity* IfcStructuralItem_type = new entity("IfcStructuralItem", IfcProduct_type);
    entity* IfcStructuralMember_type = new entity("IfcStructuralMember", IfcStructuralItem_type);
    entity* IfcStructuralReaction_type = new entity("IfcStructuralReaction", IfcStructuralActivity_type);
    entity* IfcStructuralSurfaceMember_type = new entity("IfcStructuralSurfaceMember", IfcStructuralMember_type);
    entity* IfcStructuralSurfaceMemberVarying_type = new entity("IfcStructuralSurfaceMemberVarying", IfcStructuralSurfaceMember_type);
    entity* IfcStructuredDimensionCallout_type = new entity("IfcStructuredDimensionCallout", IfcDraughtingCallout_type);
    entity* IfcSurfaceCurveSweptAreaSolid_type = new entity("IfcSurfaceCurveSweptAreaSolid", IfcSweptAreaSolid_type);
    entity* IfcSurfaceOfLinearExtrusion_type = new entity("IfcSurfaceOfLinearExtrusion", IfcSweptSurface_type);
    entity* IfcSurfaceOfRevolution_type = new entity("IfcSurfaceOfRevolution", IfcSweptSurface_type);
    entity* IfcSystemFurnitureElementType_type = new entity("IfcSystemFurnitureElementType", IfcFurnishingElementType_type);
    entity* IfcTask_type = new entity("IfcTask", IfcProcess_type);
    entity* IfcTransportElementType_type = new entity("IfcTransportElementType", IfcElementType_type);
    entity* IfcActor_type = new entity("IfcActor", IfcObject_type);
    entity* IfcAnnotation_type = new entity("IfcAnnotation", IfcProduct_type);
    entity* IfcAsymmetricIShapeProfileDef_type = new entity("IfcAsymmetricIShapeProfileDef", IfcIShapeProfileDef_type);
    entity* IfcBlock_type = new entity("IfcBlock", IfcCsgPrimitive3D_type);
    entity* IfcBooleanClippingResult_type = new entity("IfcBooleanClippingResult", IfcBooleanResult_type);
    entity* IfcBoundedCurve_type = new entity("IfcBoundedCurve", IfcCurve_type);
    entity* IfcBuilding_type = new entity("IfcBuilding", IfcSpatialStructureElement_type);
    entity* IfcBuildingElementType_type = new entity("IfcBuildingElementType", IfcElementType_type);
    entity* IfcBuildingStorey_type = new entity("IfcBuildingStorey", IfcSpatialStructureElement_type);
    entity* IfcCircleHollowProfileDef_type = new entity("IfcCircleHollowProfileDef", IfcCircleProfileDef_type);
    entity* IfcColumnType_type = new entity("IfcColumnType", IfcBuildingElementType_type);
    entity* IfcCompositeCurve_type = new entity("IfcCompositeCurve", IfcBoundedCurve_type);
    entity* IfcConic_type = new entity("IfcConic", IfcCurve_type);
    entity* IfcConstructionResource_type = new entity("IfcConstructionResource", IfcResource_type);
    entity* IfcControl_type = new entity("IfcControl", IfcObject_type);
    entity* IfcCostItem_type = new entity("IfcCostItem", IfcControl_type);
    entity* IfcCostSchedule_type = new entity("IfcCostSchedule", IfcControl_type);
    entity* IfcCoveringType_type = new entity("IfcCoveringType", IfcBuildingElementType_type);
    entity* IfcCrewResource_type = new entity("IfcCrewResource", IfcConstructionResource_type);
    entity* IfcCurtainWallType_type = new entity("IfcCurtainWallType", IfcBuildingElementType_type);
    entity* IfcDimensionCurveDirectedCallout_type = new entity("IfcDimensionCurveDirectedCallout", IfcDraughtingCallout_type);
    entity* IfcDistributionElementType_type = new entity("IfcDistributionElementType", IfcElementType_type);
    entity* IfcDistributionFlowElementType_type = new entity("IfcDistributionFlowElementType", IfcDistributionElementType_type);
    entity* IfcElectricalBaseProperties_type = new entity("IfcElectricalBaseProperties", IfcEnergyProperties_type);
    entity* IfcElement_type = new entity("IfcElement", IfcProduct_type);
    entity* IfcElementAssembly_type = new entity("IfcElementAssembly", IfcElement_type);
    entity* IfcElementComponent_type = new entity("IfcElementComponent", IfcElement_type);
    entity* IfcElementComponentType_type = new entity("IfcElementComponentType", IfcElementType_type);
    entity* IfcEllipse_type = new entity("IfcEllipse", IfcConic_type);
    entity* IfcEnergyConversionDeviceType_type = new entity("IfcEnergyConversionDeviceType", IfcDistributionFlowElementType_type);
    entity* IfcEquipmentElement_type = new entity("IfcEquipmentElement", IfcElement_type);
    entity* IfcEquipmentStandard_type = new entity("IfcEquipmentStandard", IfcControl_type);
    entity* IfcEvaporativeCoolerType_type = new entity("IfcEvaporativeCoolerType", IfcEnergyConversionDeviceType_type);
    entity* IfcEvaporatorType_type = new entity("IfcEvaporatorType", IfcEnergyConversionDeviceType_type);
    entity* IfcFacetedBrep_type = new entity("IfcFacetedBrep", IfcManifoldSolidBrep_type);
    entity* IfcFacetedBrepWithVoids_type = new entity("IfcFacetedBrepWithVoids", IfcManifoldSolidBrep_type);
    entity* IfcFastener_type = new entity("IfcFastener", IfcElementComponent_type);
    entity* IfcFastenerType_type = new entity("IfcFastenerType", IfcElementComponentType_type);
    entity* IfcFeatureElement_type = new entity("IfcFeatureElement", IfcElement_type);
    entity* IfcFeatureElementAddition_type = new entity("IfcFeatureElementAddition", IfcFeatureElement_type);
    entity* IfcFeatureElementSubtraction_type = new entity("IfcFeatureElementSubtraction", IfcFeatureElement_type);
    entity* IfcFlowControllerType_type = new entity("IfcFlowControllerType", IfcDistributionFlowElementType_type);
    entity* IfcFlowFittingType_type = new entity("IfcFlowFittingType", IfcDistributionFlowElementType_type);
    entity* IfcFlowMeterType_type = new entity("IfcFlowMeterType", IfcFlowControllerType_type);
    entity* IfcFlowMovingDeviceType_type = new entity("IfcFlowMovingDeviceType", IfcDistributionFlowElementType_type);
    entity* IfcFlowSegmentType_type = new entity("IfcFlowSegmentType", IfcDistributionFlowElementType_type);
    entity* IfcFlowStorageDeviceType_type = new entity("IfcFlowStorageDeviceType", IfcDistributionFlowElementType_type);
    entity* IfcFlowTerminalType_type = new entity("IfcFlowTerminalType", IfcDistributionFlowElementType_type);
    entity* IfcFlowTreatmentDeviceType_type = new entity("IfcFlowTreatmentDeviceType", IfcDistributionFlowElementType_type);
    entity* IfcFurnishingElement_type = new entity("IfcFurnishingElement", IfcElement_type);
    entity* IfcFurnitureStandard_type = new entity("IfcFurnitureStandard", IfcControl_type);
    entity* IfcGasTerminalType_type = new entity("IfcGasTerminalType", IfcFlowTerminalType_type);
    entity* IfcGrid_type = new entity("IfcGrid", IfcProduct_type);
    entity* IfcGroup_type = new entity("IfcGroup", IfcObject_type);
    entity* IfcHeatExchangerType_type = new entity("IfcHeatExchangerType", IfcEnergyConversionDeviceType_type);
    entity* IfcHumidifierType_type = new entity("IfcHumidifierType", IfcEnergyConversionDeviceType_type);
    entity* IfcInventory_type = new entity("IfcInventory", IfcGroup_type);
    entity* IfcJunctionBoxType_type = new entity("IfcJunctionBoxType", IfcFlowFittingType_type);
    entity* IfcLaborResource_type = new entity("IfcLaborResource", IfcConstructionResource_type);
    entity* IfcLampType_type = new entity("IfcLampType", IfcFlowTerminalType_type);
    entity* IfcLightFixtureType_type = new entity("IfcLightFixtureType", IfcFlowTerminalType_type);
    entity* IfcLinearDimension_type = new entity("IfcLinearDimension", IfcDimensionCurveDirectedCallout_type);
    entity* IfcMechanicalFastener_type = new entity("IfcMechanicalFastener", IfcFastener_type);
    entity* IfcMechanicalFastenerType_type = new entity("IfcMechanicalFastenerType", IfcFastenerType_type);
    entity* IfcMemberType_type = new entity("IfcMemberType", IfcBuildingElementType_type);
    entity* IfcMotorConnectionType_type = new entity("IfcMotorConnectionType", IfcEnergyConversionDeviceType_type);
    entity* IfcMove_type = new entity("IfcMove", IfcTask_type);
    entity* IfcOccupant_type = new entity("IfcOccupant", IfcActor_type);
    entity* IfcOpeningElement_type = new entity("IfcOpeningElement", IfcFeatureElementSubtraction_type);
    entity* IfcOrderAction_type = new entity("IfcOrderAction", IfcTask_type);
    entity* IfcOutletType_type = new entity("IfcOutletType", IfcFlowTerminalType_type);
    entity* IfcPerformanceHistory_type = new entity("IfcPerformanceHistory", IfcControl_type);
    entity* IfcPermit_type = new entity("IfcPermit", IfcControl_type);
    entity* IfcPipeFittingType_type = new entity("IfcPipeFittingType", IfcFlowFittingType_type);
    entity* IfcPipeSegmentType_type = new entity("IfcPipeSegmentType", IfcFlowSegmentType_type);
    entity* IfcPlateType_type = new entity("IfcPlateType", IfcBuildingElementType_type);
    entity* IfcPolyline_type = new entity("IfcPolyline", IfcBoundedCurve_type);
    entity* IfcPort_type = new entity("IfcPort", IfcProduct_type);
    entity* IfcProcedure_type = new entity("IfcProcedure", IfcProcess_type);
    entity* IfcProjectOrder_type = new entity("IfcProjectOrder", IfcControl_type);
    entity* IfcProjectOrderRecord_type = new entity("IfcProjectOrderRecord", IfcControl_type);
    entity* IfcProjectionElement_type = new entity("IfcProjectionElement", IfcFeatureElementAddition_type);
    entity* IfcProtectiveDeviceType_type = new entity("IfcProtectiveDeviceType", IfcFlowControllerType_type);
    entity* IfcPumpType_type = new entity("IfcPumpType", IfcFlowMovingDeviceType_type);
    entity* IfcRadiusDimension_type = new entity("IfcRadiusDimension", IfcDimensionCurveDirectedCallout_type);
    entity* IfcRailingType_type = new entity("IfcRailingType", IfcBuildingElementType_type);
    entity* IfcRampFlightType_type = new entity("IfcRampFlightType", IfcBuildingElementType_type);
    entity* IfcRelAggregates_type = new entity("IfcRelAggregates", IfcRelDecomposes_type);
    entity* IfcRelAssignsTasks_type = new entity("IfcRelAssignsTasks", IfcRelAssignsToControl_type);
    entity* IfcSanitaryTerminalType_type = new entity("IfcSanitaryTerminalType", IfcFlowTerminalType_type);
    entity* IfcScheduleTimeControl_type = new entity("IfcScheduleTimeControl", IfcControl_type);
    entity* IfcServiceLife_type = new entity("IfcServiceLife", IfcControl_type);
    entity* IfcSite_type = new entity("IfcSite", IfcSpatialStructureElement_type);
    entity* IfcSlabType_type = new entity("IfcSlabType", IfcBuildingElementType_type);
    entity* IfcSpace_type = new entity("IfcSpace", IfcSpatialStructureElement_type);
    entity* IfcSpaceHeaterType_type = new entity("IfcSpaceHeaterType", IfcEnergyConversionDeviceType_type);
    entity* IfcSpaceProgram_type = new entity("IfcSpaceProgram", IfcControl_type);
    entity* IfcSpaceType_type = new entity("IfcSpaceType", IfcSpatialStructureElementType_type);
    entity* IfcStackTerminalType_type = new entity("IfcStackTerminalType", IfcFlowTerminalType_type);
    entity* IfcStairFlightType_type = new entity("IfcStairFlightType", IfcBuildingElementType_type);
    entity* IfcStructuralAction_type = new entity("IfcStructuralAction", IfcStructuralActivity_type);
    entity* IfcStructuralConnection_type = new entity("IfcStructuralConnection", IfcStructuralItem_type);
    entity* IfcStructuralCurveConnection_type = new entity("IfcStructuralCurveConnection", IfcStructuralConnection_type);
    entity* IfcStructuralCurveMember_type = new entity("IfcStructuralCurveMember", IfcStructuralMember_type);
    entity* IfcStructuralCurveMemberVarying_type = new entity("IfcStructuralCurveMemberVarying", IfcStructuralCurveMember_type);
    entity* IfcStructuralLinearAction_type = new entity("IfcStructuralLinearAction", IfcStructuralAction_type);
    entity* IfcStructuralLinearActionVarying_type = new entity("IfcStructuralLinearActionVarying", IfcStructuralLinearAction_type);
    entity* IfcStructuralLoadGroup_type = new entity("IfcStructuralLoadGroup", IfcGroup_type);
    entity* IfcStructuralPlanarAction_type = new entity("IfcStructuralPlanarAction", IfcStructuralAction_type);
    entity* IfcStructuralPlanarActionVarying_type = new entity("IfcStructuralPlanarActionVarying", IfcStructuralPlanarAction_type);
    entity* IfcStructuralPointAction_type = new entity("IfcStructuralPointAction", IfcStructuralAction_type);
    entity* IfcStructuralPointConnection_type = new entity("IfcStructuralPointConnection", IfcStructuralConnection_type);
    entity* IfcStructuralPointReaction_type = new entity("IfcStructuralPointReaction", IfcStructuralReaction_type);
    entity* IfcStructuralResultGroup_type = new entity("IfcStructuralResultGroup", IfcGroup_type);
    entity* IfcStructuralSurfaceConnection_type = new entity("IfcStructuralSurfaceConnection", IfcStructuralConnection_type);
    entity* IfcSubContractResource_type = new entity("IfcSubContractResource", IfcConstructionResource_type);
    entity* IfcSwitchingDeviceType_type = new entity("IfcSwitchingDeviceType", IfcFlowControllerType_type);
    entity* IfcSystem_type = new entity("IfcSystem", IfcGroup_type);
    entity* IfcTankType_type = new entity("IfcTankType", IfcFlowStorageDeviceType_type);
    entity* IfcTimeSeriesSchedule_type = new entity("IfcTimeSeriesSchedule", IfcControl_type);
    entity* IfcTransformerType_type = new entity("IfcTransformerType", IfcEnergyConversionDeviceType_type);
    entity* IfcTransportElement_type = new entity("IfcTransportElement", IfcElement_type);
    entity* IfcTrimmedCurve_type = new entity("IfcTrimmedCurve", IfcBoundedCurve_type);
    entity* IfcTubeBundleType_type = new entity("IfcTubeBundleType", IfcEnergyConversionDeviceType_type);
    entity* IfcUnitaryEquipmentType_type = new entity("IfcUnitaryEquipmentType", IfcEnergyConversionDeviceType_type);
    entity* IfcValveType_type = new entity("IfcValveType", IfcFlowControllerType_type);
    entity* IfcVirtualElement_type = new entity("IfcVirtualElement", IfcElement_type);
    entity* IfcWallType_type = new entity("IfcWallType", IfcBuildingElementType_type);
    entity* IfcWasteTerminalType_type = new entity("IfcWasteTerminalType", IfcFlowTerminalType_type);
    entity* IfcWorkControl_type = new entity("IfcWorkControl", IfcControl_type);
    entity* IfcWorkPlan_type = new entity("IfcWorkPlan", IfcWorkControl_type);
    entity* IfcWorkSchedule_type = new entity("IfcWorkSchedule", IfcWorkControl_type);
    entity* IfcZone_type = new entity("IfcZone", IfcGroup_type);
    entity* Ifc2DCompositeCurve_type = new entity("Ifc2DCompositeCurve", IfcCompositeCurve_type);
    entity* IfcActionRequest_type = new entity("IfcActionRequest", IfcControl_type);
    entity* IfcAirTerminalBoxType_type = new entity("IfcAirTerminalBoxType", IfcFlowControllerType_type);
    entity* IfcAirTerminalType_type = new entity("IfcAirTerminalType", IfcFlowTerminalType_type);
    entity* IfcAirToAirHeatRecoveryType_type = new entity("IfcAirToAirHeatRecoveryType", IfcEnergyConversionDeviceType_type);
    entity* IfcAngularDimension_type = new entity("IfcAngularDimension", IfcDimensionCurveDirectedCallout_type);
    entity* IfcAsset_type = new entity("IfcAsset", IfcGroup_type);
    entity* IfcBSplineCurve_type = new entity("IfcBSplineCurve", IfcBoundedCurve_type);
    entity* IfcBeamType_type = new entity("IfcBeamType", IfcBuildingElementType_type);
    entity* IfcBezierCurve_type = new entity("IfcBezierCurve", IfcBSplineCurve_type);
    entity* IfcBoilerType_type = new entity("IfcBoilerType", IfcEnergyConversionDeviceType_type);
    entity* IfcBuildingElement_type = new entity("IfcBuildingElement", IfcElement_type);
    entity* IfcBuildingElementComponent_type = new entity("IfcBuildingElementComponent", IfcBuildingElement_type);
    entity* IfcBuildingElementPart_type = new entity("IfcBuildingElementPart", IfcBuildingElementComponent_type);
    entity* IfcBuildingElementProxy_type = new entity("IfcBuildingElementProxy", IfcBuildingElement_type);
    entity* IfcBuildingElementProxyType_type = new entity("IfcBuildingElementProxyType", IfcBuildingElementType_type);
    entity* IfcCableCarrierFittingType_type = new entity("IfcCableCarrierFittingType", IfcFlowFittingType_type);
    entity* IfcCableCarrierSegmentType_type = new entity("IfcCableCarrierSegmentType", IfcFlowSegmentType_type);
    entity* IfcCableSegmentType_type = new entity("IfcCableSegmentType", IfcFlowSegmentType_type);
    entity* IfcChillerType_type = new entity("IfcChillerType", IfcEnergyConversionDeviceType_type);
    entity* IfcCircle_type = new entity("IfcCircle", IfcConic_type);
    entity* IfcCoilType_type = new entity("IfcCoilType", IfcEnergyConversionDeviceType_type);
    entity* IfcColumn_type = new entity("IfcColumn", IfcBuildingElement_type);
    entity* IfcCompressorType_type = new entity("IfcCompressorType", IfcFlowMovingDeviceType_type);
    entity* IfcCondenserType_type = new entity("IfcCondenserType", IfcEnergyConversionDeviceType_type);
    entity* IfcCondition_type = new entity("IfcCondition", IfcGroup_type);
    entity* IfcConditionCriterion_type = new entity("IfcConditionCriterion", IfcControl_type);
    entity* IfcConstructionEquipmentResource_type = new entity("IfcConstructionEquipmentResource", IfcConstructionResource_type);
    entity* IfcConstructionMaterialResource_type = new entity("IfcConstructionMaterialResource", IfcConstructionResource_type);
    entity* IfcConstructionProductResource_type = new entity("IfcConstructionProductResource", IfcConstructionResource_type);
    entity* IfcCooledBeamType_type = new entity("IfcCooledBeamType", IfcEnergyConversionDeviceType_type);
    entity* IfcCoolingTowerType_type = new entity("IfcCoolingTowerType", IfcEnergyConversionDeviceType_type);
    entity* IfcCovering_type = new entity("IfcCovering", IfcBuildingElement_type);
    entity* IfcCurtainWall_type = new entity("IfcCurtainWall", IfcBuildingElement_type);
    entity* IfcDamperType_type = new entity("IfcDamperType", IfcFlowControllerType_type);
    entity* IfcDiameterDimension_type = new entity("IfcDiameterDimension", IfcDimensionCurveDirectedCallout_type);
    entity* IfcDiscreteAccessory_type = new entity("IfcDiscreteAccessory", IfcElementComponent_type);
    entity* IfcDiscreteAccessoryType_type = new entity("IfcDiscreteAccessoryType", IfcElementComponentType_type);
    entity* IfcDistributionChamberElementType_type = new entity("IfcDistributionChamberElementType", IfcDistributionFlowElementType_type);
    entity* IfcDistributionControlElementType_type = new entity("IfcDistributionControlElementType", IfcDistributionElementType_type);
    entity* IfcDistributionElement_type = new entity("IfcDistributionElement", IfcElement_type);
    entity* IfcDistributionFlowElement_type = new entity("IfcDistributionFlowElement", IfcDistributionElement_type);
    entity* IfcDistributionPort_type = new entity("IfcDistributionPort", IfcPort_type);
    entity* IfcDoor_type = new entity("IfcDoor", IfcBuildingElement_type);
    entity* IfcDuctFittingType_type = new entity("IfcDuctFittingType", IfcFlowFittingType_type);
    entity* IfcDuctSegmentType_type = new entity("IfcDuctSegmentType", IfcFlowSegmentType_type);
    entity* IfcDuctSilencerType_type = new entity("IfcDuctSilencerType", IfcFlowTreatmentDeviceType_type);
    entity* IfcEdgeFeature_type = new entity("IfcEdgeFeature", IfcFeatureElementSubtraction_type);
    entity* IfcElectricApplianceType_type = new entity("IfcElectricApplianceType", IfcFlowTerminalType_type);
    entity* IfcElectricFlowStorageDeviceType_type = new entity("IfcElectricFlowStorageDeviceType", IfcFlowStorageDeviceType_type);
    entity* IfcElectricGeneratorType_type = new entity("IfcElectricGeneratorType", IfcEnergyConversionDeviceType_type);
    entity* IfcElectricHeaterType_type = new entity("IfcElectricHeaterType", IfcFlowTerminalType_type);
    entity* IfcElectricMotorType_type = new entity("IfcElectricMotorType", IfcEnergyConversionDeviceType_type);
    entity* IfcElectricTimeControlType_type = new entity("IfcElectricTimeControlType", IfcFlowControllerType_type);
    entity* IfcElectricalCircuit_type = new entity("IfcElectricalCircuit", IfcSystem_type);
    entity* IfcElectricalElement_type = new entity("IfcElectricalElement", IfcElement_type);
    entity* IfcEnergyConversionDevice_type = new entity("IfcEnergyConversionDevice", IfcDistributionFlowElement_type);
    entity* IfcFanType_type = new entity("IfcFanType", IfcFlowMovingDeviceType_type);
    entity* IfcFilterType_type = new entity("IfcFilterType", IfcFlowTreatmentDeviceType_type);
    entity* IfcFireSuppressionTerminalType_type = new entity("IfcFireSuppressionTerminalType", IfcFlowTerminalType_type);
    entity* IfcFlowController_type = new entity("IfcFlowController", IfcDistributionFlowElement_type);
    entity* IfcFlowFitting_type = new entity("IfcFlowFitting", IfcDistributionFlowElement_type);
    entity* IfcFlowInstrumentType_type = new entity("IfcFlowInstrumentType", IfcDistributionControlElementType_type);
    entity* IfcFlowMovingDevice_type = new entity("IfcFlowMovingDevice", IfcDistributionFlowElement_type);
    entity* IfcFlowSegment_type = new entity("IfcFlowSegment", IfcDistributionFlowElement_type);
    entity* IfcFlowStorageDevice_type = new entity("IfcFlowStorageDevice", IfcDistributionFlowElement_type);
    entity* IfcFlowTerminal_type = new entity("IfcFlowTerminal", IfcDistributionFlowElement_type);
    entity* IfcFlowTreatmentDevice_type = new entity("IfcFlowTreatmentDevice", IfcDistributionFlowElement_type);
    entity* IfcFooting_type = new entity("IfcFooting", IfcBuildingElement_type);
    entity* IfcMember_type = new entity("IfcMember", IfcBuildingElement_type);
    entity* IfcPile_type = new entity("IfcPile", IfcBuildingElement_type);
    entity* IfcPlate_type = new entity("IfcPlate", IfcBuildingElement_type);
    entity* IfcRailing_type = new entity("IfcRailing", IfcBuildingElement_type);
    entity* IfcRamp_type = new entity("IfcRamp", IfcBuildingElement_type);
    entity* IfcRampFlight_type = new entity("IfcRampFlight", IfcBuildingElement_type);
    entity* IfcRationalBezierCurve_type = new entity("IfcRationalBezierCurve", IfcBezierCurve_type);
    entity* IfcReinforcingElement_type = new entity("IfcReinforcingElement", IfcBuildingElementComponent_type);
    entity* IfcReinforcingMesh_type = new entity("IfcReinforcingMesh", IfcReinforcingElement_type);
    entity* IfcRoof_type = new entity("IfcRoof", IfcBuildingElement_type);
    entity* IfcRoundedEdgeFeature_type = new entity("IfcRoundedEdgeFeature", IfcEdgeFeature_type);
    entity* IfcSensorType_type = new entity("IfcSensorType", IfcDistributionControlElementType_type);
    entity* IfcSlab_type = new entity("IfcSlab", IfcBuildingElement_type);
    entity* IfcStair_type = new entity("IfcStair", IfcBuildingElement_type);
    entity* IfcStairFlight_type = new entity("IfcStairFlight", IfcBuildingElement_type);
    entity* IfcStructuralAnalysisModel_type = new entity("IfcStructuralAnalysisModel", IfcSystem_type);
    entity* IfcTendon_type = new entity("IfcTendon", IfcReinforcingElement_type);
    entity* IfcTendonAnchor_type = new entity("IfcTendonAnchor", IfcReinforcingElement_type);
    entity* IfcVibrationIsolatorType_type = new entity("IfcVibrationIsolatorType", IfcDiscreteAccessoryType_type);
    entity* IfcWall_type = new entity("IfcWall", IfcBuildingElement_type);
    entity* IfcWallStandardCase_type = new entity("IfcWallStandardCase", IfcWall_type);
    entity* IfcWindow_type = new entity("IfcWindow", IfcBuildingElement_type);
    entity* IfcActuatorType_type = new entity("IfcActuatorType", IfcDistributionControlElementType_type);
    entity* IfcAlarmType_type = new entity("IfcAlarmType", IfcDistributionControlElementType_type);
    entity* IfcBeam_type = new entity("IfcBeam", IfcBuildingElement_type);
    entity* IfcChamferEdgeFeature_type = new entity("IfcChamferEdgeFeature", IfcEdgeFeature_type);
    entity* IfcControllerType_type = new entity("IfcControllerType", IfcDistributionControlElementType_type);
    entity* IfcDistributionChamberElement_type = new entity("IfcDistributionChamberElement", IfcDistributionFlowElement_type);
    entity* IfcDistributionControlElement_type = new entity("IfcDistributionControlElement", IfcDistributionElement_type);
    entity* IfcElectricDistributionPoint_type = new entity("IfcElectricDistributionPoint", IfcFlowController_type);
    entity* IfcReinforcingBar_type = new entity("IfcReinforcingBar", IfcReinforcingElement_type);
    declaration* IfcActorSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcOrganization_type);
        items.push_back(IfcPerson_type);
        items.push_back(IfcPersonAndOrganization_type);
        IfcActorSelect_type = new select_type("IfcActorSelect", items);
    }
    declaration* IfcAppliedValueSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcMeasureWithUnit_type);
        items.push_back(IfcMonetaryMeasure_type);
        items.push_back(IfcRatioMeasure_type);
        IfcAppliedValueSelect_type = new select_type("IfcAppliedValueSelect", items);
    }
    declaration* IfcAxis2Placement_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcAxis2Placement2D_type);
        items.push_back(IfcAxis2Placement3D_type);
        IfcAxis2Placement_type = new select_type("IfcAxis2Placement", items);
    }
    declaration* IfcBooleanOperand_type;
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IfcBooleanResult_type);
        items.push_back(IfcCsgPrimitive3D_type);
        items.push_back(IfcHalfSpaceSolid_type);
        items.push_back(IfcSolidModel_type);
        IfcBooleanOperand_type = new select_type("IfcBooleanOperand", items);
    }
    declaration* IfcCharacterStyleSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IfcTextStyleForDefinedFont_type);
        IfcCharacterStyleSelect_type = new select_type("IfcCharacterStyleSelect", items);
    }
    declaration* IfcClassificationNotationSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClassificationNotation_type);
        items.push_back(IfcClassificationReference_type);
        IfcClassificationNotationSelect_type = new select_type("IfcClassificationNotationSelect", items);
    }
    declaration* IfcColour_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcColourSpecification_type);
        items.push_back(IfcPreDefinedColour_type);
        IfcColour_type = new select_type("IfcColour", items);
    }
    declaration* IfcColourOrFactor_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcColourRgb_type);
        items.push_back(IfcNormalisedRatioMeasure_type);
        IfcColourOrFactor_type = new select_type("IfcColourOrFactor", items);
    }
    declaration* IfcConditionCriterionSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcLabel_type);
        items.push_back(IfcMeasureWithUnit_type);
        IfcConditionCriterionSelect_type = new select_type("IfcConditionCriterionSelect", items);
    }
    declaration* IfcCsgSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBooleanResult_type);
        items.push_back(IfcCsgPrimitive3D_type);
        IfcCsgSelect_type = new select_type("IfcCsgSelect", items);
    }
    declaration* IfcCurveOrEdgeCurve_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoundedCurve_type);
        items.push_back(IfcEdgeCurve_type);
        IfcCurveOrEdgeCurve_type = new select_type("IfcCurveOrEdgeCurve", items);
    }
    declaration* IfcCurveStyleFontSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCurveStyleFont_type);
        items.push_back(IfcPreDefinedCurveFont_type);
        IfcCurveStyleFontSelect_type = new select_type("IfcCurveStyleFontSelect", items);
    }
    declaration* IfcDateTimeSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcCalendarDate_type);
        items.push_back(IfcDateAndTime_type);
        items.push_back(IfcLocalTime_type);
        IfcDateTimeSelect_type = new select_type("IfcDateTimeSelect", items);
    }
    declaration* IfcDefinedSymbolSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternallyDefinedSymbol_type);
        items.push_back(IfcPreDefinedSymbol_type);
        IfcDefinedSymbolSelect_type = new select_type("IfcDefinedSymbolSelect", items);
    }
    declaration* IfcDerivedMeasureValue_type;
    {
        std::vector<const declaration*> items; items.reserve(68);
        items.push_back(IfcAbsorbedDoseMeasure_type);
        items.push_back(IfcAccelerationMeasure_type);
        items.push_back(IfcAngularVelocityMeasure_type);
        items.push_back(IfcCompoundPlaneAngleMeasure_type);
        items.push_back(IfcCurvatureMeasure_type);
        items.push_back(IfcDoseEquivalentMeasure_type);
        items.push_back(IfcDynamicViscosityMeasure_type);
        items.push_back(IfcElectricCapacitanceMeasure_type);
        items.push_back(IfcElectricChargeMeasure_type);
        items.push_back(IfcElectricConductanceMeasure_type);
        items.push_back(IfcElectricResistanceMeasure_type);
        items.push_back(IfcElectricVoltageMeasure_type);
        items.push_back(IfcEnergyMeasure_type);
        items.push_back(IfcForceMeasure_type);
        items.push_back(IfcFrequencyMeasure_type);
        items.push_back(IfcHeatFluxDensityMeasure_type);
        items.push_back(IfcHeatingValueMeasure_type);
        items.push_back(IfcIlluminanceMeasure_type);
        items.push_back(IfcInductanceMeasure_type);
        items.push_back(IfcIntegerCountRateMeasure_type);
        items.push_back(IfcIonConcentrationMeasure_type);
        items.push_back(IfcIsothermalMoistureCapacityMeasure_type);
        items.push_back(IfcKinematicViscosityMeasure_type);
        items.push_back(IfcLinearForceMeasure_type);
        items.push_back(IfcLinearMomentMeasure_type);
        items.push_back(IfcLinearStiffnessMeasure_type);
        items.push_back(IfcLinearVelocityMeasure_type);
        items.push_back(IfcLuminousFluxMeasure_type);
        items.push_back(IfcLuminousIntensityDistributionMeasure_type);
        items.push_back(IfcMagneticFluxDensityMeasure_type);
        items.push_back(IfcMagneticFluxMeasure_type);
        items.push_back(IfcMassDensityMeasure_type);
        items.push_back(IfcMassFlowRateMeasure_type);
        items.push_back(IfcMassPerLengthMeasure_type);
        items.push_back(IfcModulusOfElasticityMeasure_type);
        items.push_back(IfcModulusOfLinearSubgradeReactionMeasure_type);
        items.push_back(IfcModulusOfRotationalSubgradeReactionMeasure_type);
        items.push_back(IfcModulusOfSubgradeReactionMeasure_type);
        items.push_back(IfcMoistureDiffusivityMeasure_type);
        items.push_back(IfcMolecularWeightMeasure_type);
        items.push_back(IfcMomentOfInertiaMeasure_type);
        items.push_back(IfcMonetaryMeasure_type);
        items.push_back(IfcPHMeasure_type);
        items.push_back(IfcPlanarForceMeasure_type);
        items.push_back(IfcPowerMeasure_type);
        items.push_back(IfcPressureMeasure_type);
        items.push_back(IfcRadioActivityMeasure_type);
        items.push_back(IfcRotationalFrequencyMeasure_type);
        items.push_back(IfcRotationalMassMeasure_type);
        items.push_back(IfcRotationalStiffnessMeasure_type);
        items.push_back(IfcSectionModulusMeasure_type);
        items.push_back(IfcSectionalAreaIntegralMeasure_type);
        items.push_back(IfcShearModulusMeasure_type);
        items.push_back(IfcSoundPowerMeasure_type);
        items.push_back(IfcSoundPressureMeasure_type);
        items.push_back(IfcSpecificHeatCapacityMeasure_type);
        items.push_back(IfcTemperatureGradientMeasure_type);
        items.push_back(IfcThermalAdmittanceMeasure_type);
        items.push_back(IfcThermalConductivityMeasure_type);
        items.push_back(IfcThermalExpansionCoefficientMeasure_type);
        items.push_back(IfcThermalResistanceMeasure_type);
        items.push_back(IfcThermalTransmittanceMeasure_type);
        items.push_back(IfcTimeStamp_type);
        items.push_back(IfcTorqueMeasure_type);
        items.push_back(IfcVaporPermeabilityMeasure_type);
        items.push_back(IfcVolumetricFlowRateMeasure_type);
        items.push_back(IfcWarpingConstantMeasure_type);
        items.push_back(IfcWarpingMomentMeasure_type);
        IfcDerivedMeasureValue_type = new select_type("IfcDerivedMeasureValue", items);
    }
    declaration* IfcDocumentSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDocumentInformation_type);
        items.push_back(IfcDocumentReference_type);
        IfcDocumentSelect_type = new select_type("IfcDocumentSelect", items);
    }
    declaration* IfcDraughtingCalloutElement_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcAnnotationCurveOccurrence_type);
        items.push_back(IfcAnnotationSymbolOccurrence_type);
        items.push_back(IfcAnnotationTextOccurrence_type);
        IfcDraughtingCalloutElement_type = new select_type("IfcDraughtingCalloutElement", items);
    }
    declaration* IfcFillAreaStyleTileShapeSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IfcFillAreaStyleTileSymbolWithStyle_type);
        IfcFillAreaStyleTileShapeSelect_type = new select_type("IfcFillAreaStyleTileShapeSelect", items);
    }
    declaration* IfcFillStyleSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IfcColour_type);
        items.push_back(IfcExternallyDefinedHatchStyle_type);
        items.push_back(IfcFillAreaStyleHatching_type);
        items.push_back(IfcFillAreaStyleTiles_type);
        IfcFillStyleSelect_type = new select_type("IfcFillStyleSelect", items);
    }
    declaration* IfcGeometricSetSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcCurve_type);
        items.push_back(IfcPoint_type);
        items.push_back(IfcSurface_type);
        IfcGeometricSetSelect_type = new select_type("IfcGeometricSetSelect", items);
    }
    declaration* IfcHatchLineDistanceSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcOneDirectionRepeatFactor_type);
        items.push_back(IfcPositiveLengthMeasure_type);
        IfcHatchLineDistanceSelect_type = new select_type("IfcHatchLineDistanceSelect", items);
    }
    declaration* IfcLayeredItem_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcRepresentation_type);
        items.push_back(IfcRepresentationItem_type);
        IfcLayeredItem_type = new select_type("IfcLayeredItem", items);
    }
    declaration* IfcLibrarySelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcLibraryInformation_type);
        items.push_back(IfcLibraryReference_type);
        IfcLibrarySelect_type = new select_type("IfcLibrarySelect", items);
    }
    declaration* IfcLightDistributionDataSourceSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternalReference_type);
        items.push_back(IfcLightIntensityDistribution_type);
        IfcLightDistributionDataSourceSelect_type = new select_type("IfcLightDistributionDataSourceSelect", items);
    }
    declaration* IfcMaterialSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IfcMaterial_type);
        items.push_back(IfcMaterialLayer_type);
        items.push_back(IfcMaterialLayerSet_type);
        items.push_back(IfcMaterialLayerSetUsage_type);
        items.push_back(IfcMaterialList_type);
        IfcMaterialSelect_type = new select_type("IfcMaterialSelect", items);
    }
    declaration* IfcMeasureValue_type;
    {
        std::vector<const declaration*> items; items.reserve(22);
        items.push_back(IfcAmountOfSubstanceMeasure_type);
        items.push_back(IfcAreaMeasure_type);
        items.push_back(IfcComplexNumber_type);
        items.push_back(IfcContextDependentMeasure_type);
        items.push_back(IfcCountMeasure_type);
        items.push_back(IfcDescriptiveMeasure_type);
        items.push_back(IfcElectricCurrentMeasure_type);
        items.push_back(IfcLengthMeasure_type);
        items.push_back(IfcLuminousIntensityMeasure_type);
        items.push_back(IfcMassMeasure_type);
        items.push_back(IfcNormalisedRatioMeasure_type);
        items.push_back(IfcNumericMeasure_type);
        items.push_back(IfcParameterValue_type);
        items.push_back(IfcPlaneAngleMeasure_type);
        items.push_back(IfcPositiveLengthMeasure_type);
        items.push_back(IfcPositivePlaneAngleMeasure_type);
        items.push_back(IfcPositiveRatioMeasure_type);
        items.push_back(IfcRatioMeasure_type);
        items.push_back(IfcSolidAngleMeasure_type);
        items.push_back(IfcThermodynamicTemperatureMeasure_type);
        items.push_back(IfcTimeMeasure_type);
        items.push_back(IfcVolumeMeasure_type);
        IfcMeasureValue_type = new select_type("IfcMeasureValue", items);
    }
    declaration* IfcMetricValueSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcCostValue_type);
        items.push_back(IfcDateTimeSelect_type);
        items.push_back(IfcMeasureWithUnit_type);
        items.push_back(IfcTable_type);
        items.push_back(IfcText_type);
        items.push_back(IfcTimeSeries_type);
        IfcMetricValueSelect_type = new select_type("IfcMetricValueSelect", items);
    }
    declaration* IfcObjectReferenceSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(13);
        items.push_back(IfcAddress_type);
        items.push_back(IfcAppliedValue_type);
        items.push_back(IfcCalendarDate_type);
        items.push_back(IfcDateAndTime_type);
        items.push_back(IfcExternalReference_type);
        items.push_back(IfcLocalTime_type);
        items.push_back(IfcMaterial_type);
        items.push_back(IfcMaterialLayer_type);
        items.push_back(IfcMaterialList_type);
        items.push_back(IfcOrganization_type);
        items.push_back(IfcPerson_type);
        items.push_back(IfcPersonAndOrganization_type);
        items.push_back(IfcTimeSeries_type);
        IfcObjectReferenceSelect_type = new select_type("IfcObjectReferenceSelect", items);
    }
    declaration* IfcOrientationSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDirection_type);
        items.push_back(IfcPlaneAngleMeasure_type);
        IfcOrientationSelect_type = new select_type("IfcOrientationSelect", items);
    }
    declaration* IfcPointOrVertexPoint_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcPoint_type);
        items.push_back(IfcVertexPoint_type);
        IfcPointOrVertexPoint_type = new select_type("IfcPointOrVertexPoint", items);
    }
    declaration* IfcPresentationStyleSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcCurveStyle_type);
        items.push_back(IfcFillAreaStyle_type);
        items.push_back(IfcNullStyle_type);
        items.push_back(IfcSurfaceStyle_type);
        items.push_back(IfcSymbolStyle_type);
        items.push_back(IfcTextStyle_type);
        IfcPresentationStyleSelect_type = new select_type("IfcPresentationStyleSelect", items);
    }
    declaration* IfcShell_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClosedShell_type);
        items.push_back(IfcOpenShell_type);
        IfcShell_type = new select_type("IfcShell", items);
    }
    declaration* IfcSimpleValue_type;
    {
        std::vector<const declaration*> items; items.reserve(7);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcIdentifier_type);
        items.push_back(IfcInteger_type);
        items.push_back(IfcLabel_type);
        items.push_back(IfcLogical_type);
        items.push_back(IfcReal_type);
        items.push_back(IfcText_type);
        IfcSimpleValue_type = new select_type("IfcSimpleValue", items);
    }
    declaration* IfcSizeSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcDescriptiveMeasure_type);
        items.push_back(IfcLengthMeasure_type);
        items.push_back(IfcNormalisedRatioMeasure_type);
        items.push_back(IfcPositiveLengthMeasure_type);
        items.push_back(IfcPositiveRatioMeasure_type);
        items.push_back(IfcRatioMeasure_type);
        IfcSizeSelect_type = new select_type("IfcSizeSelect", items);
    }
    declaration* IfcSpecularHighlightSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcSpecularExponent_type);
        items.push_back(IfcSpecularRoughness_type);
        IfcSpecularHighlightSelect_type = new select_type("IfcSpecularHighlightSelect", items);
    }
    declaration* IfcStructuralActivityAssignmentSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcElement_type);
        items.push_back(IfcStructuralItem_type);
        IfcStructuralActivityAssignmentSelect_type = new select_type("IfcStructuralActivityAssignmentSelect", items);
    }
    declaration* IfcSurfaceOrFaceSurface_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcFaceBasedSurfaceModel_type);
        items.push_back(IfcFaceSurface_type);
        items.push_back(IfcSurface_type);
        IfcSurfaceOrFaceSurface_type = new select_type("IfcSurfaceOrFaceSurface", items);
    }
    declaration* IfcSurfaceStyleElementSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IfcExternallyDefinedSurfaceStyle_type);
        items.push_back(IfcSurfaceStyleLighting_type);
        items.push_back(IfcSurfaceStyleRefraction_type);
        items.push_back(IfcSurfaceStyleShading_type);
        items.push_back(IfcSurfaceStyleWithTextures_type);
        IfcSurfaceStyleElementSelect_type = new select_type("IfcSurfaceStyleElementSelect", items);
    }
    declaration* IfcSymbolStyleSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IfcColour_type);
        IfcSymbolStyleSelect_type = new select_type("IfcSymbolStyleSelect", items);
    }
    declaration* IfcTextFontSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternallyDefinedTextFont_type);
        items.push_back(IfcPreDefinedTextFont_type);
        IfcTextFontSelect_type = new select_type("IfcTextFontSelect", items);
    }
    declaration* IfcTextStyleSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcTextStyleTextModel_type);
        items.push_back(IfcTextStyleWithBoxCharacteristics_type);
        IfcTextStyleSelect_type = new select_type("IfcTextStyleSelect", items);
    }
    declaration* IfcTrimmingSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCartesianPoint_type);
        items.push_back(IfcParameterValue_type);
        IfcTrimmingSelect_type = new select_type("IfcTrimmingSelect", items);
    }
    declaration* IfcUnit_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcDerivedUnit_type);
        items.push_back(IfcMonetaryUnit_type);
        items.push_back(IfcNamedUnit_type);
        IfcUnit_type = new select_type("IfcUnit", items);
    }
    declaration* IfcValue_type;
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcDerivedMeasureValue_type);
        items.push_back(IfcMeasureValue_type);
        items.push_back(IfcSimpleValue_type);
        IfcValue_type = new select_type("IfcValue", items);
    }
    declaration* IfcVectorOrDirection_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDirection_type);
        items.push_back(IfcVector_type);
        IfcVectorOrDirection_type = new select_type("IfcVectorOrDirection", items);
    }
    declaration* IfcCurveFontOrScaledCurveFontSelect_type;
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCurveStyleFontAndScaling_type);
        items.push_back(IfcCurveStyleFontSelect_type);
        IfcCurveFontOrScaledCurveFontSelect_type = new select_type("IfcCurveFontOrScaledCurveFontSelect", items);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        Ifc2DCompositeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RequestID", new named_type(IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcActionRequest_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TheActor", new named_type(IfcActorSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcActor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Role", new named_type(IfcRoleEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedRole", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcActorRole_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcActuatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcActuatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Purpose", new named_type(IfcAddressTypeEnum_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPurpose", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAirTerminalBoxTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAirTerminalBoxType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAirTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAirTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAirToAirHeatRecoveryTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAirToAirHeatRecoveryType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAlarmTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAlarmType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcAngularDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotationCurveOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OuterBoundary", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcCurve_type)), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcAnnotationFillArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("FillStyleTarget", new named_type(IfcPoint_type), true));
        attributes.push_back(new entity::attribute("GlobalOrLocal", new named_type(IfcGlobalOrLocalEnum_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotationFillAreaOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotationOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Item", new named_type(IfcGeometricRepresentationItem_type), false));
        attributes.push_back(new entity::attribute("TextureCoordinates", new named_type(IfcTextureCoordinate_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcAnnotationSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotationSurfaceOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotationSymbolOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAnnotationTextOccurrence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ApplicationDeveloper", new named_type(IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("Version", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ApplicationFullName", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ApplicationIdentifier", new named_type(IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcApplication_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("AppliedValue", new named_type(IfcAppliedValueSelect_type), true));
        attributes.push_back(new entity::attribute("UnitBasis", new named_type(IfcMeasureWithUnit_type), true));
        attributes.push_back(new entity::attribute("ApplicableDate", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("FixedUntilDate", new named_type(IfcDateTimeSelect_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAppliedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ComponentOfTotal", new named_type(IfcAppliedValue_type), false));
        attributes.push_back(new entity::attribute("Components", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcAppliedValue_type)), false));
        attributes.push_back(new entity::attribute("ArithmeticOperator", new named_type(IfcArithmeticOperatorEnum_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAppliedValueRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ApprovalDateTime", new named_type(IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("ApprovalStatus", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ApprovalLevel", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ApprovalQualifier", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Identifier", new named_type(IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcApproval_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Actor", new named_type(IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("Approval", new named_type(IfcApproval_type), false));
        attributes.push_back(new entity::attribute("Role", new named_type(IfcActorRole_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcApprovalActorRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ApprovedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProperty_type)), false));
        attributes.push_back(new entity::attribute("Approval", new named_type(IfcApproval_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcApprovalPropertyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatedApproval", new named_type(IfcApproval_type), false));
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IfcApproval_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcApprovalRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("OuterCurve", new named_type(IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcArbitraryClosedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Curve", new named_type(IfcBoundedCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcArbitraryOpenProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("InnerCurves", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcCurve_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcArbitraryProfileDefWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("AssetID", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("OriginalValue", new named_type(IfcCostValue_type), false));
        attributes.push_back(new entity::attribute("CurrentValue", new named_type(IfcCostValue_type), false));
        attributes.push_back(new entity::attribute("TotalReplacementCost", new named_type(IfcCostValue_type), false));
        attributes.push_back(new entity::attribute("Owner", new named_type(IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("User", new named_type(IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("ResponsiblePerson", new named_type(IfcPerson_type), false));
        attributes.push_back(new entity::attribute("IncorporationDate", new named_type(IfcCalendarDate_type), false));
        attributes.push_back(new entity::attribute("DepreciatedValue", new named_type(IfcCostValue_type), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAsset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("TopFlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopFlangeThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TopFlangeFilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAsymmetricIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis", new named_type(IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcAxis1Placement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcAxis2Placement2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Axis", new named_type(IfcDirection_type), true));
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcAxis2Placement3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Degree", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("ControlPointsList", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcCartesianPoint_type)), false));
        attributes.push_back(new entity::attribute("CurveForm", new named_type(IfcBSplineCurveForm_type), false));
        attributes.push_back(new entity::attribute("ClosedCurve", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBSplineCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBeam_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBeamTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBeamType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBezierCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RasterFormat", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("RasterCode", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBlobTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("XLength", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YLength", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ZLength", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBlock_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBoilerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoilerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBooleanClippingResult_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Operator", new named_type(IfcBooleanOperator_type), false));
        attributes.push_back(new entity::attribute("FirstOperand", new named_type(IfcBooleanOperand_type), false));
        attributes.push_back(new entity::attribute("SecondOperand", new named_type(IfcBooleanOperand_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBooleanResult_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcBoundaryCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LinearStiffnessByLengthX", new named_type(IfcModulusOfLinearSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByLengthY", new named_type(IfcModulusOfLinearSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByLengthZ", new named_type(IfcModulusOfLinearSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthX", new named_type(IfcModulusOfRotationalSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthY", new named_type(IfcModulusOfRotationalSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessByLengthZ", new named_type(IfcModulusOfRotationalSubgradeReactionMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundaryEdgeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("LinearStiffnessByAreaX", new named_type(IfcModulusOfSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByAreaY", new named_type(IfcModulusOfSubgradeReactionMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessByAreaZ", new named_type(IfcModulusOfSubgradeReactionMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundaryFaceCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LinearStiffnessX", new named_type(IfcLinearStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessY", new named_type(IfcLinearStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearStiffnessZ", new named_type(IfcLinearStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessX", new named_type(IfcRotationalStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessY", new named_type(IfcRotationalStiffnessMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalStiffnessZ", new named_type(IfcRotationalStiffnessMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundaryNodeCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WarpingStiffness", new named_type(IfcWarpingMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundaryNodeConditionWarping_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcBoundedCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcBoundedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Corner", new named_type(IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("XDim", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ZDim", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoundingBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Enclosure", new named_type(IfcBoundingBox_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBoxedHalfSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ElevationOfRefHeight", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ElevationOfTerrain", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BuildingAddress", new named_type(IfcPostalAddress_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuilding_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElementComponent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElementPart_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CompositionType", new named_type(IfcElementCompositionEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElementProxy_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcBuildingElementProxyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElementProxyType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Elevation", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcBuildingStorey_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Girth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InternalFilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableCarrierFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableCarrierFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableCarrierSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableCarrierSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCableSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCableSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("DayComponent", new named_type(IfcDayInMonthNumber_type), false));
        attributes.push_back(new entity::attribute("MonthComponent", new named_type(IfcMonthInYearNumber_type), false));
        attributes.push_back(new entity::attribute("YearComponent", new named_type(IfcYearNumber_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCalendarDate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 1, 3, new named_type(IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcCartesianPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Axis1", new named_type(IfcDirection_type), true));
        attributes.push_back(new entity::attribute("Axis2", new named_type(IfcDirection_type), true));
        attributes.push_back(new entity::attribute("LocalOrigin", new named_type(IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Scale", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCartesianTransformationOperator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCartesianTransformationOperator2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Scale2", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCartesianTransformationOperator2DnonUniform_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Axis3", new named_type(IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCartesianTransformationOperator3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Scale2", new simple_type(simple_type::real_type), true));
        attributes.push_back(new entity::attribute("Scale3", new simple_type(simple_type::real_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCartesianTransformationOperator3DnonUniform_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Thickness", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCenterLineProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Width", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Height", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcChamferEdgeFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcChillerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcChillerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCircle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCircleHollowProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCircleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Source", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Edition", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("EditionDate", new named_type(IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Notation", new named_type(IfcClassificationNotationFacet_type), false));
        attributes.push_back(new entity::attribute("ItemOf", new named_type(IfcClassification_type), true));
        attributes.push_back(new entity::attribute("Title", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcClassificationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingItem", new named_type(IfcClassificationItem_type), false));
        attributes.push_back(new entity::attribute("RelatedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcClassificationItem_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcClassificationItemRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("NotationFacets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcClassificationNotationFacet_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcClassificationNotation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("NotationValue", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcClassificationNotationFacet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ReferencedSource", new named_type(IfcClassification_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcClassificationReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcClosedShell_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCoilTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoilType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Red", new named_type(IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("Green", new named_type(IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("Blue", new named_type(IfcNormalisedRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcColourRgb_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcColourSpecification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcColumn_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcColumnTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcColumnType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcComplexProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Segments", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcCompositeCurveSegment_type)), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCompositeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Transition", new named_type(IfcTransitionCode_type), false));
        attributes.push_back(new entity::attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("ParentCurve", new named_type(IfcCurve_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCompositeCurveSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Profiles", new aggregation_type(aggregation_type::set_type, 2, -1, new named_type(IfcProfileDef_type)), false));
        attributes.push_back(new entity::attribute("Label", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCompositeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCompressorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCompressorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCondenserTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCondenserType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Criterion", new named_type(IfcConditionCriterionSelect_type), false));
        attributes.push_back(new entity::attribute("CriterionDateTime", new named_type(IfcDateTimeSelect_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConditionCriterion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcConic_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CfsFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcFace_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcConnectedFaceSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CurveOnRelatingElement", new named_type(IfcCurveOrEdgeCurve_type), false));
        attributes.push_back(new entity::attribute("CurveOnRelatedElement", new named_type(IfcCurveOrEdgeCurve_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcConnectionCurveGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcConnectionGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("EccentricityInX", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EccentricityInY", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EccentricityInZ", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConnectionPointEccentricity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PointOnRelatingElement", new named_type(IfcPointOrVertexPoint_type), false));
        attributes.push_back(new entity::attribute("PointOnRelatedElement", new named_type(IfcPointOrVertexPoint_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcConnectionPointGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("LocationAtRelatingElement", new named_type(IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("LocationAtRelatedElement", new named_type(IfcAxis2Placement_type), true));
        attributes.push_back(new entity::attribute("ProfileOfPort", new named_type(IfcProfileDef_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConnectionPortGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SurfaceOnRelatingElement", new named_type(IfcSurfaceOrFaceSurface_type), false));
        attributes.push_back(new entity::attribute("SurfaceOnRelatedElement", new named_type(IfcSurfaceOrFaceSurface_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcConnectionSurfaceGeometry_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ConstraintGrade", new named_type(IfcConstraintEnum_type), false));
        attributes.push_back(new entity::attribute("ConstraintSource", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CreatingActor", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("UserDefinedGrade", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstraint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedConstraints", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcConstraint_type)), false));
        attributes.push_back(new entity::attribute("LogicalAggregator", new named_type(IfcLogicalOperatorEnum_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstraintAggregationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ClassifiedConstraint", new named_type(IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcClassificationNotationSelect_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcConstraintClassificationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedConstraints", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcConstraint_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstraintRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionEquipmentResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Suppliers", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("UsageRatio", new named_type(IfcRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionMaterialResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionProductResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ResourceIdentifier", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("ResourceGroup", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ResourceConsumption", new named_type(IfcResourceConsumptionEnum_type), true));
        attributes.push_back(new entity::attribute("BaseQuantity", new named_type(IfcMeasureWithUnit_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConstructionResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcContextDependentUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcControllerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcControllerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("ConversionFactor", new named_type(IfcMeasureWithUnit_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcConversionBasedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCooledBeamTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCooledBeamType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCoolingTowerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoolingTowerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("HourOffset", new named_type(IfcHourInDay_type), false));
        attributes.push_back(new entity::attribute("MinuteOffset", new named_type(IfcMinuteInHour_type), true));
        attributes.push_back(new entity::attribute("Sense", new named_type(IfcAheadOrBehind_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoordinatedUniversalTimeOffset_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCostItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("SubmittedBy", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("PreparedBy", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("SubmittedOn", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("TargetUsers", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("UpdateDate", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ID", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCostScheduleTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCostSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("CostType", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Condition", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCostValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCoveringTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCovering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCoveringTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCoveringType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseWidth2", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("HeadWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadDepth2", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadDepth3", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseWidth4", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth1", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth2", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth3", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCraneRailAShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("HeadDepth2", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("HeadDepth3", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth1", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BaseDepth2", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCraneRailFShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCrewResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcCsgPrimitive3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TreeRootExpression", new named_type(IfcCsgSelect_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcCsgSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingMonetaryUnit", new named_type(IfcMonetaryUnit_type), false));
        attributes.push_back(new entity::attribute("RelatedMonetaryUnit", new named_type(IfcMonetaryUnit_type), false));
        attributes.push_back(new entity::attribute("ExchangeRate", new named_type(IfcPositiveRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("RateDateTime", new named_type(IfcDateAndTime_type), false));
        attributes.push_back(new entity::attribute("RateSource", new named_type(IfcLibraryInformation_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurrencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurtainWall_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcCurtainWallTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurtainWallType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IfcPlane_type), false));
        attributes.push_back(new entity::attribute("OuterBoundary", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("InnerBoundaries", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IfcCurve_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurveBoundedPlane_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("CurveFont", new named_type(IfcCurveFontOrScaledCurveFontSelect_type), true));
        attributes.push_back(new entity::attribute("CurveWidth", new named_type(IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("CurveColour", new named_type(IfcColour_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurveStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PatternList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcCurveStyleFontPattern_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCurveStyleFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CurveFont", new named_type(IfcCurveStyleFontSelect_type), false));
        attributes.push_back(new entity::attribute("CurveFontScaling", new named_type(IfcPositiveRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcCurveStyleFontAndScaling_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VisibleSegmentLength", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InvisibleSegmentLength", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcCurveStyleFontPattern_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDamperTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDamperType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DateComponent", new named_type(IfcCalendarDate_type), false));
        attributes.push_back(new entity::attribute("TimeComponent", new named_type(IfcLocalTime_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcDateAndTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Definition", new named_type(IfcDefinedSymbolSelect_type), false));
        attributes.push_back(new entity::attribute("Target", new named_type(IfcCartesianTransformationOperator2D_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcDefinedSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ParentProfile", new named_type(IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Operator", new named_type(IfcCartesianTransformationOperator2D_type), false));
        attributes.push_back(new entity::attribute("Label", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDerivedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDerivedUnitElement_type)), false));
        attributes.push_back(new entity::attribute("UnitType", new named_type(IfcDerivedUnitEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDerivedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcNamedUnit_type), false));
        attributes.push_back(new entity::attribute("Exponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcDerivedUnitElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDiameterDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDimensionCalloutRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDimensionCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDimensionCurveDirectedCallout_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Role", new named_type(IfcDimensionExtentUsage_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDimensionCurveTerminator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDimensionPair_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("LengthExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("MassExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("TimeExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("ElectricCurrentExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("ThermodynamicTemperatureExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("AmountOfSubstanceExponent", new simple_type(simple_type::integer_type), false));
        attributes.push_back(new entity::attribute("LuminousIntensityExponent", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDimensionalExponents_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("DirectionRatios", new aggregation_type(aggregation_type::list_type, 2, 3, new simple_type(simple_type::real_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDirection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDiscreteAccessory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDiscreteAccessoryType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionChamberElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDistributionChamberElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionChamberElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ControlElementId", new named_type(IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionControlElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionControlElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionFlowElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionFlowElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FlowDirection", new named_type(IfcFlowDirectionEnum_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDistributionPort_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("FileExtension", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("MimeContentType", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("MimeSubtype", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDocumentElectronicFormat_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(17);
        attributes.push_back(new entity::attribute("DocumentId", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("DocumentReferences", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDocumentReference_type)), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("IntendedUse", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Scope", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Revision", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DocumentOwner", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("Editors", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcActorSelect_type)), true));
        attributes.push_back(new entity::attribute("CreationTime", new named_type(IfcDateAndTime_type), true));
        attributes.push_back(new entity::attribute("LastRevisionTime", new named_type(IfcDateAndTime_type), true));
        attributes.push_back(new entity::attribute("ElectronicFormat", new named_type(IfcDocumentElectronicFormat_type), true));
        attributes.push_back(new entity::attribute("ValidFrom", new named_type(IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("ValidUntil", new named_type(IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("Confidentiality", new named_type(IfcDocumentConfidentialityEnum_type), true));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcDocumentStatusEnum_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDocumentInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingDocument", new named_type(IfcDocumentInformation_type), false));
        attributes.push_back(new entity::attribute("RelatedDocuments", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDocumentInformation_type)), false));
        attributes.push_back(new entity::attribute("RelationshipType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDocumentInformationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDocumentReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(11);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomOffset", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningOffset", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ThresholdOffset", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CasingDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoorLiningProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PanelDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("PanelOperation", new named_type(IfcDoorPanelOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelWidth", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IfcDoorPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoorPanelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcDoorStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IfcDoorStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDoorStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Contents", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDraughtingCalloutElement_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDraughtingCallout_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingDraughtingCallout", new named_type(IfcDraughtingCallout_type), false));
        attributes.push_back(new entity::attribute("RelatedDraughtingCallout", new named_type(IfcDraughtingCallout_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDraughtingCalloutRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDraughtingPreDefinedColour_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDraughtingPreDefinedCurveFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcDraughtingPreDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDuctFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDuctFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDuctSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDuctSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcDuctSilencerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcDuctSilencerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeStart", new named_type(IfcVertex_type), false));
        attributes.push_back(new entity::attribute("EdgeEnd", new named_type(IfcVertex_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcEdge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeGeometry", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEdgeCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FeatureLength", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEdgeFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcOrientedEdge_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcEdgeLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricApplianceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricApplianceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DistributionPointFunction", new named_type(IfcElectricDistributionPointFunctionEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedFunction", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricDistributionPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricFlowStorageDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricFlowStorageDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricGeneratorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricGeneratorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricHeaterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricHeaterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricMotorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricMotorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElectricTimeControlTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricTimeControlType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("ElectricCurrentType", new named_type(IfcElectricCurrentEnum_type), true));
        attributes.push_back(new entity::attribute("InputVoltage", new named_type(IfcElectricVoltageMeasure_type), false));
        attributes.push_back(new entity::attribute("InputFrequency", new named_type(IfcFrequencyMeasure_type), false));
        attributes.push_back(new entity::attribute("FullLoadCurrent", new named_type(IfcElectricCurrentMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumCircuitCurrent", new named_type(IfcElectricCurrentMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumPowerInput", new named_type(IfcPowerMeasure_type), true));
        attributes.push_back(new entity::attribute("RatedPowerInput", new named_type(IfcPowerMeasure_type), true));
        attributes.push_back(new entity::attribute("InputPhase", new simple_type(simple_type::integer_type), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricalBaseProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricalCircuit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElectricalElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Tag", new named_type(IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AssemblyPlace", new named_type(IfcAssemblyPlaceEnum_type), true));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcElementAssemblyTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElementAssembly_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElementComponent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElementComponentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MethodOfMeasurement", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Quantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPhysicalQuantity_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElementQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ElementType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcElementarySurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SemiAxis1", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SemiAxis2", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEllipse_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SemiAxis1", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SemiAxis2", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEllipseProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEnergyConversionDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEnergyConversionDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EnergySequence", new named_type(IfcEnergySequenceEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedEnergySequence", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEnergyProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ImpactType", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Category", new named_type(IfcEnvironmentalImpactCategoryEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedCategory", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEnvironmentalImpactValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEquipmentElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEquipmentStandard_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEvaporativeCoolerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEvaporativeCoolerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcEvaporatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcEvaporatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ExtendedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProperty_type)), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExtendedMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Location", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ItemReference", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternalReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternallyDefinedHatchStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternallyDefinedSurfaceStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternallyDefinedSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExternallyDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ExtrudedDirection", new named_type(IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcExtrudedAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Bounds", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcFaceBound_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcFace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FbsmFaces", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcConnectedFaceSet_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcFaceBasedSurfaceModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Bound", new named_type(IfcLoop_type), false));
        attributes.push_back(new entity::attribute("Orientation", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcFaceBound_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcFaceOuterBound_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("FaceSurface", new named_type(IfcSurface_type), false));
        attributes.push_back(new entity::attribute("SameSense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFaceSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcFacetedBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Voids", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcClosedShell_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcFacetedBrepWithVoids_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TensionFailureX", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("TensionFailureY", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("TensionFailureZ", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureX", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureY", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("CompressionFailureZ", new named_type(IfcForceMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFailureConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFanTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFanType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFastenerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFeatureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFeatureElementAddition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFeatureElementSubtraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("FillStyles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcFillStyleSelect_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcFillAreaStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("HatchLineAppearance", new named_type(IfcCurveStyle_type), false));
        attributes.push_back(new entity::attribute("StartOfNextHatchLine", new named_type(IfcHatchLineDistanceSelect_type), false));
        attributes.push_back(new entity::attribute("PointOfReferenceHatchLine", new named_type(IfcCartesianPoint_type), true));
        attributes.push_back(new entity::attribute("PatternStart", new named_type(IfcCartesianPoint_type), true));
        attributes.push_back(new entity::attribute("HatchLineAngle", new named_type(IfcPlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFillAreaStyleHatching_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Symbol", new named_type(IfcAnnotationSymbolOccurrence_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcFillAreaStyleTileSymbolWithStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TilingPattern", new named_type(IfcOneDirectionRepeatFactor_type), false));
        attributes.push_back(new entity::attribute("Tiles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcFillAreaStyleTileShapeSelect_type)), false));
        attributes.push_back(new entity::attribute("TilingScale", new named_type(IfcPositiveRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFillAreaStyleTiles_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFilterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFilterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFireSuppressionTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFireSuppressionTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowController_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowControllerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowFitting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFlowInstrumentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowInstrumentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFlowMeterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowMeterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowMovingDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowMovingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowSegment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowStorageDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowStorageDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowTerminal_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowTreatmentDevice_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFlowTreatmentDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(15);
        attributes.push_back(new entity::attribute("PropertySource", new named_type(IfcPropertySourceEnum_type), false));
        attributes.push_back(new entity::attribute("FlowConditionTimeSeries", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("VelocityTimeSeries", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("FlowrateTimeSeries", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("Fluid", new named_type(IfcMaterial_type), false));
        attributes.push_back(new entity::attribute("PressureTimeSeries", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPropertySource", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("TemperatureSingleValue", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("WetBulbTemperatureSingleValue", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("WetBulbTemperatureTimeSeries", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("TemperatureTimeSeries", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("FlowrateSingleValue", new named_type(IfcDerivedMeasureValue_type), true));
        attributes.push_back(new entity::attribute("FlowConditionSingleValue", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("VelocitySingleValue", new named_type(IfcLinearVelocityMeasure_type), true));
        attributes.push_back(new entity::attribute("PressureSingleValue", new named_type(IfcPressureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(19);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFluidFlowProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcFootingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFooting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("CombustionTemperature", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("CarbonContent", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("LowerHeatingValue", new named_type(IfcHeatingValueMeasure_type), true));
        attributes.push_back(new entity::attribute("HigherHeatingValue", new named_type(IfcHeatingValueMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFuelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFurnishingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFurnishingElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFurnitureStandard_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AssemblyPlace", new named_type(IfcAssemblyPlaceEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcFurnitureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcGasTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGasTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MolecularWeight", new named_type(IfcMolecularWeightMeasure_type), true));
        attributes.push_back(new entity::attribute("Porosity", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("MassDensity", new named_type(IfcMassDensityMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGeneralMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PhysicalWeight", new named_type(IfcMassPerLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Perimeter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumPlateThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumPlateThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IfcAreaMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGeneralProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcGeometricCurveSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("CoordinateSpaceDimension", new named_type(IfcDimensionCount_type), false));
        attributes.push_back(new entity::attribute("Precision", new simple_type(simple_type::real_type), true));
        attributes.push_back(new entity::attribute("WorldCoordinateSystem", new named_type(IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("TrueNorth", new named_type(IfcDirection_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGeometricRepresentationContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcGeometricRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ParentContext", new named_type(IfcGeometricRepresentationContext_type), false));
        attributes.push_back(new entity::attribute("TargetScale", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("TargetView", new named_type(IfcGeometricProjectionEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedTargetView", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGeometricRepresentationSubContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Elements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcGeometricSetSelect_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcGeometricSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("UAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("VAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("WAxes", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcGridAxis_type)), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGrid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("AxisTag", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AxisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("SameSense", new named_type(IfcBoolean_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGridAxis_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PlacementLocation", new named_type(IfcVirtualGridIntersection_type), false));
        attributes.push_back(new entity::attribute("PlacementRefDirection", new named_type(IfcVirtualGridIntersection_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcGridPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BaseSurface", new named_type(IfcSurface_type), false));
        attributes.push_back(new entity::attribute("AgreementFlag", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcHalfSpaceSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcHeatExchangerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcHeatExchangerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcHumidifierTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcHumidifierType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("UpperVaporResistanceFactor", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("LowerVaporResistanceFactor", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("IsothermalMoistureCapacity", new named_type(IfcIsothermalMoistureCapacityMeasure_type), true));
        attributes.push_back(new entity::attribute("VaporPermeability", new named_type(IfcVaporPermeabilityMeasure_type), true));
        attributes.push_back(new entity::attribute("MoistureDiffusivity", new named_type(IfcMoistureDiffusivityMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcHygroscopicMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("OverallDepth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcIShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("UrlReference", new named_type(IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcImageTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("InventoryType", new named_type(IfcInventoryTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Jurisdiction", new named_type(IfcActorSelect_type), false));
        attributes.push_back(new entity::attribute("ResponsiblePersons", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPerson_type)), false));
        attributes.push_back(new entity::attribute("LastUpdateDate", new named_type(IfcCalendarDate_type), false));
        attributes.push_back(new entity::attribute("CurrentValue", new named_type(IfcCostValue_type), true));
        attributes.push_back(new entity::attribute("OriginalValue", new named_type(IfcCostValue_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcInventory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcIrregularTimeSeriesValue_type)), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcIrregularTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeStamp", new named_type(IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcIrregularTimeSeriesValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcJunctionBoxTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcJunctionBoxType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Width", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LegSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SkillSet", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLaborResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLampType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Version", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Publisher", new named_type(IfcOrganization_type), true));
        attributes.push_back(new entity::attribute("VersionDate", new named_type(IfcCalendarDate_type), true));
        attributes.push_back(new entity::attribute("LibraryReference", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcLibraryReference_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLibraryInformation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLibraryReference_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MainPlaneAngle", new named_type(IfcPlaneAngleMeasure_type), false));
        attributes.push_back(new entity::attribute("SecondaryPlaneAngle", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcPlaneAngleMeasure_type)), false));
        attributes.push_back(new entity::attribute("LuminousIntensity", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLuminousIntensityDistributionMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightDistributionData_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLightFixtureTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightFixtureType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LightDistributionCurve", new named_type(IfcLightDistributionCurveEnum_type), false));
        attributes.push_back(new entity::attribute("DistributionData", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLightDistributionData_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcLightIntensityDistribution_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("LightColour", new named_type(IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("AmbientIntensity", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Intensity", new named_type(IfcNormalisedRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightSource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightSourceAmbient_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightSourceDirectional_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), false));
        attributes.push_back(new entity::attribute("ColourAppearance", new named_type(IfcColourRgb_type), true));
        attributes.push_back(new entity::attribute("ColourTemperature", new named_type(IfcThermodynamicTemperatureMeasure_type), false));
        attributes.push_back(new entity::attribute("LuminousFlux", new named_type(IfcLuminousFluxMeasure_type), false));
        attributes.push_back(new entity::attribute("LightEmissionSource", new named_type(IfcLightEmissionSourceEnum_type), false));
        attributes.push_back(new entity::attribute("LightDistributionDataSource", new named_type(IfcLightDistributionDataSourceSelect_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightSourceGoniometric_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Position", new named_type(IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("ConstantAttenuation", new named_type(IfcReal_type), false));
        attributes.push_back(new entity::attribute("DistanceAttenuation", new named_type(IfcReal_type), false));
        attributes.push_back(new entity::attribute("QuadricAttenuation", new named_type(IfcReal_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightSourcePositional_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IfcDirection_type), false));
        attributes.push_back(new entity::attribute("ConcentrationExponent", new named_type(IfcReal_type), true));
        attributes.push_back(new entity::attribute("SpreadAngle", new named_type(IfcPositivePlaneAngleMeasure_type), false));
        attributes.push_back(new entity::attribute("BeamWidthAngle", new named_type(IfcPositivePlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLightSourceSpot_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Pnt", new named_type(IfcCartesianPoint_type), false));
        attributes.push_back(new entity::attribute("Dir", new named_type(IfcVector_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcLine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcLinearDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PlacementRelTo", new named_type(IfcObjectPlacement_type), true));
        attributes.push_back(new entity::attribute("RelativePlacement", new named_type(IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcLocalPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("HourComponent", new named_type(IfcHourInDay_type), false));
        attributes.push_back(new entity::attribute("MinuteComponent", new named_type(IfcMinuteInHour_type), true));
        attributes.push_back(new entity::attribute("SecondComponent", new named_type(IfcSecondInMinute_type), true));
        attributes.push_back(new entity::attribute("Zone", new named_type(IfcCoordinatedUniversalTimeOffset_type), true));
        attributes.push_back(new entity::attribute("DaylightSavingOffset", new named_type(IfcDaylightSavingHour_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcLocalTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Outer", new named_type(IfcClosedShell_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcManifoldSolidBrep_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappingSource", new named_type(IfcRepresentationMap_type), false));
        attributes.push_back(new entity::attribute("MappingTarget", new named_type(IfcCartesianTransformationOperator_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcMappedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcMaterial_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MaterialClassifications", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcClassificationNotationSelect_type)), false));
        attributes.push_back(new entity::attribute("ClassifiedMaterial", new named_type(IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcMaterialClassificationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RepresentedMaterial", new named_type(IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialDefinitionRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Material", new named_type(IfcMaterial_type), true));
        attributes.push_back(new entity::attribute("LayerThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("IsVentilated", new named_type(IfcLogical_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialLayer_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MaterialLayers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcMaterialLayer_type)), false));
        attributes.push_back(new entity::attribute("LayerSetName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcMaterialLayerSet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ForLayerSet", new named_type(IfcMaterialLayerSet_type), false));
        attributes.push_back(new entity::attribute("LayerSetDirection", new named_type(IfcLayerSetDirectionEnum_type), false));
        attributes.push_back(new entity::attribute("DirectionSense", new named_type(IfcDirectionSenseEnum_type), false));
        attributes.push_back(new entity::attribute("OffsetFromReferenceLine", new named_type(IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMaterialLayerSetUsage_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Materials", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcMaterial_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcMaterialList_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Material", new named_type(IfcMaterial_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ValueComponent", new named_type(IfcValue_type), false));
        attributes.push_back(new entity::attribute("UnitComponent", new named_type(IfcUnit_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcMeasureWithUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("CompressiveStrength", new named_type(IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("MaxAggregateSize", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("AdmixturesDescription", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Workability", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ProtectivePoreRatio", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("WaterImpermeability", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMechanicalConcreteMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalLength", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMechanicalFastener_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMechanicalFastenerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DynamicViscosity", new named_type(IfcDynamicViscosityMeasure_type), true));
        attributes.push_back(new entity::attribute("YoungModulus", new named_type(IfcModulusOfElasticityMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearModulus", new named_type(IfcModulusOfElasticityMeasure_type), true));
        attributes.push_back(new entity::attribute("PoissonRatio", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalExpansionCoefficient", new named_type(IfcThermalExpansionCoefficientMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMechanicalMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("YieldStress", new named_type(IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("UltimateStress", new named_type(IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("UltimateStrain", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("HardeningModule", new named_type(IfcModulusOfElasticityMeasure_type), true));
        attributes.push_back(new entity::attribute("ProportionalStress", new named_type(IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("PlasticStrain", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Relaxations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcRelaxation_type)), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMechanicalSteelMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMemberTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMemberType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Benchmark", new named_type(IfcBenchmarkEnum_type), false));
        attributes.push_back(new entity::attribute("ValueSource", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("DataValue", new named_type(IfcMetricValueSelect_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMetric_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Currency", new named_type(IfcCurrencyEnum_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcMonetaryUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcMotorConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMotorConnectionType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("MoveFrom", new named_type(IfcSpatialStructureElement_type), false));
        attributes.push_back(new entity::attribute("MoveTo", new named_type(IfcSpatialStructureElement_type), false));
        attributes.push_back(new entity::attribute("PunchList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcText_type)), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcMove_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Dimensions", new named_type(IfcDimensionalExponents_type), false));
        attributes.push_back(new entity::attribute("UnitType", new named_type(IfcUnitEnum_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcNamedUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ObjectType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcObjectDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcObjectPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BenchmarkValues", new named_type(IfcMetric_type), true));
        attributes.push_back(new entity::attribute("ResultValues", new named_type(IfcMetric_type), true));
        attributes.push_back(new entity::attribute("ObjectiveQualifier", new named_type(IfcObjectiveEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedQualifier", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcObjective_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcOccupantTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOccupant_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOffsetCurve2D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Distance", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SelfIntersect", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("RefDirection", new named_type(IfcDirection_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOffsetCurve3D_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RepeatFactor", new named_type(IfcVector_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcOneDirectionRepeatFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcOpenShell_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOpeningElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("VisibleTransmittance", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SolarTransmittance", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalIrTransmittance", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalIrEmissivityBack", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalIrEmissivityFront", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("VisibleReflectanceBack", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("VisibleReflectanceFront", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SolarReflectanceFront", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SolarReflectanceBack", new named_type(IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOpticalMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ActionID", new named_type(IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOrderAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Id", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcActorRole_type)), true));
        attributes.push_back(new entity::attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcAddress_type)), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOrganization_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("RelatingOrganization", new named_type(IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("RelatedOrganizations", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcOrganization_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOrganizationRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EdgeElement", new named_type(IfcEdge_type), false));
        attributes.push_back(new entity::attribute("Orientation", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(true); derived.push_back(false); derived.push_back(false);
        IfcOrientedEdge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcOutletTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOutletType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("OwningUser", new named_type(IfcPersonAndOrganization_type), false));
        attributes.push_back(new entity::attribute("OwningApplication", new named_type(IfcApplication_type), false));
        attributes.push_back(new entity::attribute("State", new named_type(IfcStateEnum_type), true));
        attributes.push_back(new entity::attribute("ChangeAction", new named_type(IfcChangeActionEnum_type), false));
        attributes.push_back(new entity::attribute("LastModifiedDate", new named_type(IfcTimeStamp_type), true));
        attributes.push_back(new entity::attribute("LastModifyingUser", new named_type(IfcPersonAndOrganization_type), true));
        attributes.push_back(new entity::attribute("LastModifyingApplication", new named_type(IfcApplication_type), true));
        attributes.push_back(new entity::attribute("CreationDate", new named_type(IfcTimeStamp_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcOwnerHistory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement2D_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcParameterizedProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("EdgeList", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcOrientedEdge_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPath_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LifeCyclePhase", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPerformanceHistory_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcPermeableCoveringOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IfcWindowPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("FrameDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FrameThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPermeableCoveringProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PermitID", new named_type(IfcIdentifier_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPermit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Id", new named_type(IfcIdentifier_type), true));
        attributes.push_back(new entity::attribute("FamilyName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("GivenName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("MiddleNames", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PrefixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("SuffixTitles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcActorRole_type)), true));
        attributes.push_back(new entity::attribute("Addresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcAddress_type)), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPerson_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ThePerson", new named_type(IfcPerson_type), false));
        attributes.push_back(new entity::attribute("TheOrganization", new named_type(IfcOrganization_type), false));
        attributes.push_back(new entity::attribute("Roles", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcActorRole_type)), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPersonAndOrganization_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("HasQuantities", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPhysicalQuantity_type)), false));
        attributes.push_back(new entity::attribute("Discrimination", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Quality", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Usage", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPhysicalComplexQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcPhysicalQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcNamedUnit_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPhysicalSimpleQuantity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPileTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IfcPileConstructionEnum_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPile_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPipeFittingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPipeFittingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPipeSegmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPipeSegmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Width", new named_type(IfcInteger_type), false));
        attributes.push_back(new entity::attribute("Height", new named_type(IfcInteger_type), false));
        attributes.push_back(new entity::attribute("ColourComponents", new named_type(IfcInteger_type), false));
        attributes.push_back(new entity::attribute("Pixel", new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::binary_type)), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPixelTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Location", new named_type(IfcCartesianPoint_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPlacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Placement", new named_type(IfcAxis2Placement_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPlanarBox_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SizeInX", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("SizeInY", new named_type(IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcPlanarExtent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPlane_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPlate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPlateTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPlateType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("PointParameter", new named_type(IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcPointOnCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IfcSurface_type), false));
        attributes.push_back(new entity::attribute("PointParameterU", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("PointParameterV", new named_type(IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPointOnSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Polygon", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPolyLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), false));
        attributes.push_back(new entity::attribute("PolygonalBoundary", new named_type(IfcBoundedCurve_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPolygonalBoundedHalfSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Points", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPolyline_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPort_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("InternalLocation", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("AddressLines", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PostalBox", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Town", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Region", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PostalCode", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Country", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPostalAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedColour_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedCurveFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedDimensionSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedPointMarkerSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedTerminatorSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPreDefinedTextFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("AssignedItems", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcLayeredItem_type)), false));
        attributes.push_back(new entity::attribute("Identifier", new named_type(IfcIdentifier_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPresentationLayerAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("LayerOn", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("LayerFrozen", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("LayerBlocked", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("LayerStyles", new aggregation_type(aggregation_type::set_type, 0, -1, new named_type(IfcPresentationStyleSelect_type)), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPresentationLayerWithStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPresentationStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPresentationStyleSelect_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcPresentationStyleAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ProcedureID", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("ProcedureType", new named_type(IfcProcedureTypeEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedProcedureType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProcedure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ObjectPlacement", new named_type(IfcObjectPlacement_type), true));
        attributes.push_back(new entity::attribute("Representation", new named_type(IfcProductRepresentation_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProductDefinitionShape_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Representations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcRepresentation_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProductRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("SpecificHeatCapacity", new named_type(IfcSpecificHeatCapacityMeasure_type), true));
        attributes.push_back(new entity::attribute("N20Content", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("COContent", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("CO2Content", new named_type(IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProductsOfCombustionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProfileType", new named_type(IfcProfileTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ProfileName", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProfileName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ProfileDefinition", new named_type(IfcProfileDef_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Phase", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RepresentationContexts", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcRepresentationContext_type)), false));
        attributes.push_back(new entity::attribute("UnitsInContext", new named_type(IfcUnitAssignment_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ID", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProjectOrderTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProjectOrder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Records", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcRelAssignsToProjectOrder_type)), false));
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProjectOrderRecordTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProjectOrderRecord_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProjectionCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProjectionElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("UpperBoundValue", new named_type(IfcValue_type), true));
        attributes.push_back(new entity::attribute("LowerBoundValue", new named_type(IfcValue_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyBoundedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IfcConstraint_type), false));
        attributes.push_back(new entity::attribute("RelatedProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProperty_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyConstraintRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DependingProperty", new named_type(IfcProperty_type), false));
        attributes.push_back(new entity::attribute("DependantProperty", new named_type(IfcProperty_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("Expression", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyDependencyRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        attributes.push_back(new entity::attribute("EnumerationReference", new named_type(IfcPropertyEnumeration_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyEnumeratedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("EnumerationValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyEnumeration_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyListValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("UsageName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("PropertyReference", new named_type(IfcObjectReferenceSelect_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyReferenceValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("HasProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertySet_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertySetDefinition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("NominalValue", new named_type(IfcValue_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertySingleValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DefiningValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        attributes.push_back(new entity::attribute("DefinedValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        attributes.push_back(new entity::attribute("Expression", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("DefiningUnit", new named_type(IfcUnit_type), true));
        attributes.push_back(new entity::attribute("DefinedUnit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPropertyTableValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcProtectiveDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProtectiveDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ProxyType", new named_type(IfcObjectTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Tag", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcProxy_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcPumpTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcPumpType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AreaValue", new named_type(IfcAreaMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityArea_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("CountValue", new named_type(IfcCountMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityCount_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LengthValue", new named_type(IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityLength_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TimeValue", new named_type(IfcTimeMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityTime_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("VolumeValue", new named_type(IfcVolumeMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityVolume_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightValue", new named_type(IfcMassMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcQuantityWeight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcRadiusDimension_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRailingTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRailing_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRailingTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRailingType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ShapeType", new named_type(IfcRampTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRamp_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRampFlight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcRampFlightTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRampFlightType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WeightsData", new aggregation_type(aggregation_type::list_type, 2, -1, new simple_type(simple_type::real_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRationalBezierCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("WallThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerFilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OuterFilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRectangleHollowProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("XDim", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRectangleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("XLength", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YLength", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Height", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRectangularPyramid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("BasisSurface", new named_type(IfcSurface_type), false));
        attributes.push_back(new entity::attribute("U1", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("V1", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("U2", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("V2", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("Usense", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Vsense", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRectangularTrimmedSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ReferencedDocument", new named_type(IfcDocumentSelect_type), false));
        attributes.push_back(new entity::attribute("ReferencingValues", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcAppliedValue_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReferencesValueDocument_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TimeStep", new named_type(IfcTimeMeasure_type), false));
        attributes.push_back(new entity::attribute("Values", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcTimeSeriesValue_type)), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRegularTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("TotalCrossSectionArea", new named_type(IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("SteelGrade", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IfcReinforcingBarSurfaceEnum_type), true));
        attributes.push_back(new entity::attribute("EffectiveDepth", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("NominalBarDiameter", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BarCount", new named_type(IfcCountMeasure_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcementBarProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DefinitionType", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ReinforcementSectionDefinitions", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcSectionReinforcementProperties_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcementDefinitionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("BarLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BarRole", new named_type(IfcReinforcingBarRoleEnum_type), false));
        attributes.push_back(new entity::attribute("BarSurface", new named_type(IfcReinforcingBarSurfaceEnum_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingBar_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SteelGrade", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("MeshLength", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MeshWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LongitudinalBarNominalDiameter", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TransverseBarNominalDiameter", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("LongitudinalBarCrossSectionArea", new named_type(IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("TransverseBarCrossSectionArea", new named_type(IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("LongitudinalBarSpacing", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TransverseBarSpacing", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcReinforcingMesh_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAggregates_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcObjectDefinition_type)), false));
        attributes.push_back(new entity::attribute("RelatedObjectsType", new named_type(IfcObjectTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssigns_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TimeForTask", new named_type(IfcScheduleTimeControl_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsTasks_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingActor", new named_type(IfcActor_type), false));
        attributes.push_back(new entity::attribute("ActingRole", new named_type(IfcActorRole_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToActor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingControl", new named_type(IfcControl_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingGroup", new named_type(IfcGroup_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IfcProcess_type), false));
        attributes.push_back(new entity::attribute("QuantityInProcess", new named_type(IfcMeasureWithUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToProcess_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingProduct", new named_type(IfcProduct_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToProjectOrder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingResource", new named_type(IfcResource_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssignsToResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcRoot_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociates_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingAppliedValue", new named_type(IfcAppliedValue_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesAppliedValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingApproval", new named_type(IfcApproval_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesApproval_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingClassification", new named_type(IfcClassificationNotationSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesClassification_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Intent", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("RelatingConstraint", new named_type(IfcConstraint_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesConstraint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingDocument", new named_type(IfcDocumentSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesDocument_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingLibrary", new named_type(IfcLibrarySelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesLibrary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingMaterial", new named_type(IfcMaterialSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesMaterial_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingProfileProperties", new named_type(IfcProfileProperties_type), false));
        attributes.push_back(new entity::attribute("ProfileSectionLocation", new named_type(IfcShapeAspect_type), true));
        attributes.push_back(new entity::attribute("ProfileOrientation", new named_type(IfcOrientationSelect_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelAssociatesProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnects_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ConnectionGeometry", new named_type(IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatingPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new simple_type(simple_type::integer_type)), false));
        attributes.push_back(new entity::attribute("RelatedPriorities", new aggregation_type(aggregation_type::list_type, 0, -1, new simple_type(simple_type::integer_type)), false));
        attributes.push_back(new entity::attribute("RelatedConnectionType", new named_type(IfcConnectionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("RelatingConnectionType", new named_type(IfcConnectionTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsPathElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingPort", new named_type(IfcPort_type), false));
        attributes.push_back(new entity::attribute("RelatedElement", new named_type(IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsPortToElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("RelatingPort", new named_type(IfcPort_type), false));
        attributes.push_back(new entity::attribute("RelatedPort", new named_type(IfcPort_type), false));
        attributes.push_back(new entity::attribute("RealizingElement", new named_type(IfcElement_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsPorts_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IfcStructuralActivityAssignmentSelect_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralActivity", new named_type(IfcStructuralActivity_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsStructuralActivity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralMember", new named_type(IfcStructuralMember_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsStructuralElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("RelatingStructuralMember", new named_type(IfcStructuralMember_type), false));
        attributes.push_back(new entity::attribute("RelatedStructuralConnection", new named_type(IfcStructuralConnection_type), false));
        attributes.push_back(new entity::attribute("AppliedCondition", new named_type(IfcBoundaryCondition_type), true));
        attributes.push_back(new entity::attribute("AdditionalConditions", new named_type(IfcStructuralConnectionCondition_type), true));
        attributes.push_back(new entity::attribute("SupportedLength", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ConditionCoordinateSystem", new named_type(IfcAxis2Placement3D_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsStructuralMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ConnectionConstraint", new named_type(IfcConnectionGeometry_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsWithEccentricity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RealizingElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcElement_type)), false));
        attributes.push_back(new entity::attribute("ConnectionType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelConnectsWithRealizingElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProduct_type)), false));
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IfcSpatialStructureElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelContainedInSpatialStructure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingBuildingElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcCovering_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelCoversBldgElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedSpace", new named_type(IfcSpace_type), false));
        attributes.push_back(new entity::attribute("RelatedCoverings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcCovering_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelCoversSpaces_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingObject", new named_type(IfcObjectDefinition_type), false));
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcObjectDefinition_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDecomposes_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatedObjects", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcObject_type)), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDefines_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingPropertyDefinition", new named_type(IfcPropertySetDefinition_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDefinesByProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RelatingType", new named_type(IfcTypeObject_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelDefinesByType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingOpeningElement", new named_type(IfcOpeningElement_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildingElement", new named_type(IfcElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelFillsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedControlElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDistributionControlElement_type)), false));
        attributes.push_back(new entity::attribute("RelatingFlowElement", new named_type(IfcDistributionFlowElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelFlowControlElements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("DailyInteraction", new named_type(IfcCountMeasure_type), true));
        attributes.push_back(new entity::attribute("ImportanceRating", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("LocationOfInteraction", new named_type(IfcSpatialStructureElement_type), true));
        attributes.push_back(new entity::attribute("RelatedSpaceProgram", new named_type(IfcSpaceProgram_type), false));
        attributes.push_back(new entity::attribute("RelatingSpaceProgram", new named_type(IfcSpaceProgram_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelInteractionRequirements_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelNests_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelOccupiesSpaces_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("OverridingProperties", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProperty_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelOverridesProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedFeatureElement", new named_type(IfcFeatureElementAddition_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelProjectsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatedElements", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcProduct_type)), false));
        attributes.push_back(new entity::attribute("RelatingStructure", new named_type(IfcSpatialStructureElement_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelReferencedInSpatialStructure_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelSchedulesCostItems_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RelatingProcess", new named_type(IfcProcess_type), false));
        attributes.push_back(new entity::attribute("RelatedProcess", new named_type(IfcProcess_type), false));
        attributes.push_back(new entity::attribute("TimeLag", new named_type(IfcTimeMeasure_type), false));
        attributes.push_back(new entity::attribute("SequenceType", new named_type(IfcSequenceEnum_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelSequence_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingSystem", new named_type(IfcSystem_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildings", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcSpatialStructureElement_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelServicesBuildings_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RelatingSpace", new named_type(IfcSpace_type), false));
        attributes.push_back(new entity::attribute("RelatedBuildingElement", new named_type(IfcElement_type), true));
        attributes.push_back(new entity::attribute("ConnectionGeometry", new named_type(IfcConnectionGeometry_type), true));
        attributes.push_back(new entity::attribute("PhysicalOrVirtualBoundary", new named_type(IfcPhysicalOrVirtualEnum_type), false));
        attributes.push_back(new entity::attribute("InternalOrExternalBoundary", new named_type(IfcInternalOrExternalEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelSpaceBoundary_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelatingBuildingElement", new named_type(IfcElement_type), false));
        attributes.push_back(new entity::attribute("RelatedOpeningElement", new named_type(IfcFeatureElementSubtraction_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelVoidsElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RelaxationValue", new named_type(IfcNormalisedRatioMeasure_type), false));
        attributes.push_back(new entity::attribute("InitialStress", new named_type(IfcNormalisedRatioMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcRelaxation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ContextOfItems", new named_type(IfcRepresentationContext_type), false));
        attributes.push_back(new entity::attribute("RepresentationIdentifier", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("RepresentationType", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Items", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcRepresentationItem_type)), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ContextIdentifier", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ContextType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcRepresentationContext_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("MappingOrigin", new named_type(IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("MappedRepresentation", new named_type(IfcRepresentation_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcRepresentationMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Axis", new named_type(IfcAxis1Placement_type), false));
        attributes.push_back(new entity::attribute("Angle", new named_type(IfcPlaneAngleMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRevolvedAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Thickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RibHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RibWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RibSpacing", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("Direction", new named_type(IfcRibPlateDirectionEnum_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRibPlateProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Height", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("BottomRadius", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRightCircularCone_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Height", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRightCircularCylinder_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ShapeType", new named_type(IfcRoofTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRoof_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("GlobalId", new named_type(IfcGloballyUniqueId_type), false));
        attributes.push_back(new entity::attribute("OwnerHistory", new named_type(IfcOwnerHistory_type), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRoot_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRoundedEdgeFeature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("RoundingRadius", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcRoundedRectangleProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Prefix", new named_type(IfcSIPrefix_type), true));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcSIUnitName_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(true); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSIUnit_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSanitaryTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSanitaryTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(18);
        attributes.push_back(new entity::attribute("ActualStart", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("EarlyStart", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("LateStart", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ScheduleStart", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ActualFinish", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("EarlyFinish", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("LateFinish", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ScheduleFinish", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("ScheduleDuration", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("ActualDuration", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("RemainingTime", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("FreeFloat", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("IsCritical", new simple_type(simple_type::boolean_type), true));
        attributes.push_back(new entity::attribute("StatusTime", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("StartFloat", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("FinishFloat", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("Completion", new named_type(IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(23);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcScheduleTimeControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SectionType", new named_type(IfcSectionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("StartProfile", new named_type(IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("EndProfile", new named_type(IfcProfileDef_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSectionProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LongitudinalStartPosition", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("LongitudinalEndPosition", new named_type(IfcLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TransversePosition", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ReinforcementRole", new named_type(IfcReinforcingBarRoleEnum_type), false));
        attributes.push_back(new entity::attribute("SectionDefinition", new named_type(IfcSectionProperties_type), false));
        attributes.push_back(new entity::attribute("CrossSectionReinforcementDefinitions", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcReinforcementBarProperties_type)), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSectionReinforcementProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SpineCurve", new named_type(IfcCompositeCurve_type), false));
        attributes.push_back(new entity::attribute("CrossSections", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcProfileDef_type)), false));
        attributes.push_back(new entity::attribute("CrossSectionPositions", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcAxis2Placement3D_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSectionedSpine_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSensorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSensorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ServiceLifeType", new named_type(IfcServiceLifeTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ServiceLifeDuration", new named_type(IfcTimeMeasure_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcServiceLife_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcServiceLifeFactorTypeEnum_type), false));
        attributes.push_back(new entity::attribute("UpperValue", new named_type(IfcMeasureValue_type), true));
        attributes.push_back(new entity::attribute("MostUsedValue", new named_type(IfcMeasureValue_type), false));
        attributes.push_back(new entity::attribute("LowerValue", new named_type(IfcMeasureValue_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcServiceLifeFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("ShapeRepresentations", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcShapeModel_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("ProductDefinitional", new simple_type(simple_type::logical_type), false));
        attributes.push_back(new entity::attribute("PartOfProductDefinitionShape", new named_type(IfcProductDefinitionShape_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcShapeAspect_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcShapeModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcShapeRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SbsmBoundary", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcShell_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcShellBasedSurfaceModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSimpleProperty_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("RefLatitude", new named_type(IfcCompoundPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RefLongitude", new named_type(IfcCompoundPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RefElevation", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LandTitleNumber", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("SiteAddress", new named_type(IfcPostalAddress_type), true));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSite_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSlabTypeEnum_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSlab_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSlabTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSlabType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SlippageX", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("SlippageY", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("SlippageZ", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSlippageConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcSolidModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("IsAttenuating", new named_type(IfcBoolean_type), false));
        attributes.push_back(new entity::attribute("SoundScale", new named_type(IfcSoundScaleEnum_type), true));
        attributes.push_back(new entity::attribute("SoundValues", new aggregation_type(aggregation_type::list_type, 1, 8, new named_type(IfcSoundValue_type)), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSoundProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("SoundLevelTimeSeries", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("Frequency", new named_type(IfcFrequencyMeasure_type), false));
        attributes.push_back(new entity::attribute("SoundLevelSingleValue", new named_type(IfcDerivedMeasureValue_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSoundValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("InteriorOrExteriorSpace", new named_type(IfcInternalOrExternalEnum_type), false));
        attributes.push_back(new entity::attribute("ElevationWithFlooring", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpace_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpaceHeaterTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpaceHeaterType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("SpaceProgramIdentifier", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("MaxRequiredArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("MinRequiredArea", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("RequestedLocation", new named_type(IfcSpatialStructureElement_type), true));
        attributes.push_back(new entity::attribute("StandardRequiredArea", new named_type(IfcAreaMeasure_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpaceProgram_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("ApplicableValueRatio", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalLoadSource", new named_type(IfcThermalLoadSourceEnum_type), false));
        attributes.push_back(new entity::attribute("PropertySource", new named_type(IfcPropertySourceEnum_type), false));
        attributes.push_back(new entity::attribute("SourceDescription", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("MaximumValue", new named_type(IfcPowerMeasure_type), false));
        attributes.push_back(new entity::attribute("MinimumValue", new named_type(IfcPowerMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalLoadTimeSeriesValues", new named_type(IfcTimeSeries_type), true));
        attributes.push_back(new entity::attribute("UserDefinedThermalLoadSource", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("UserDefinedPropertySource", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ThermalLoadType", new named_type(IfcThermalLoadTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpaceThermalLoadProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSpaceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpaceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("LongName", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("CompositionType", new named_type(IfcElementCompositionEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpatialStructureElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSpatialStructureElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSphere_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStackTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStackTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ShapeType", new named_type(IfcStairTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStair_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("NumberOfRiser", new simple_type(simple_type::integer_type), true));
        attributes.push_back(new entity::attribute("NumberOfTreads", new simple_type(simple_type::integer_type), true));
        attributes.push_back(new entity::attribute("RiserHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TreadLength", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStairFlight_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStairFlightTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStairFlightType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("DestabilizingLoad", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("CausedBy", new named_type(IfcStructuralReaction_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("AppliedLoad", new named_type(IfcStructuralLoad_type), false));
        attributes.push_back(new entity::attribute("GlobalOrLocal", new named_type(IfcGlobalOrLocalEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralActivity_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcAnalysisModelTypeEnum_type), false));
        attributes.push_back(new entity::attribute("OrientationOf2DPlane", new named_type(IfcAxis2Placement3D_type), true));
        attributes.push_back(new entity::attribute("LoadedBy", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcStructuralLoadGroup_type)), true));
        attributes.push_back(new entity::attribute("HasResults", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcStructuralResultGroup_type)), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralAnalysisModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AppliedCondition", new named_type(IfcBoundaryCondition_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcStructuralConnectionCondition_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralCurveTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralCurveMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IfcProjectedOrTrueLengthEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLinearAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VaryingAppliedLoadLocation", new named_type(IfcShapeAspect_type), false));
        attributes.push_back(new entity::attribute("SubsequentAppliedLoads", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcStructuralLoad_type)), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLinearActionVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcStructuralLoad_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcLoadGroupTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ActionType", new named_type(IfcActionTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ActionSource", new named_type(IfcActionSourceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Coefficient", new named_type(IfcRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("LinearForceX", new named_type(IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearForceY", new named_type(IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearForceZ", new named_type(IfcLinearForceMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentX", new named_type(IfcLinearMomentMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentY", new named_type(IfcLinearMomentMeasure_type), true));
        attributes.push_back(new entity::attribute("LinearMomentZ", new named_type(IfcLinearMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadLinearForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("PlanarForceX", new named_type(IfcPlanarForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PlanarForceY", new named_type(IfcPlanarForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PlanarForceZ", new named_type(IfcPlanarForceMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadPlanarForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("DisplacementX", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("DisplacementY", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("DisplacementZ", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRX", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRY", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("RotationalDisplacementRZ", new named_type(IfcPlaneAngleMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadSingleDisplacement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Distortion", new named_type(IfcCurvatureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadSingleDisplacementDistortion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("ForceX", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("ForceY", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("ForceZ", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentX", new named_type(IfcTorqueMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentY", new named_type(IfcTorqueMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentZ", new named_type(IfcTorqueMeasure_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadSingleForce_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("WarpingMoment", new named_type(IfcWarpingMomentMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadSingleForceWarping_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcStructuralLoadStatic_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("DeltaT_Constant", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaT_Y", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("DeltaT_Z", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralLoadTemperature_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ProjectedOrTrue", new named_type(IfcProjectedOrTrueLengthEnum_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPlanarAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("VaryingAppliedLoadLocation", new named_type(IfcShapeAspect_type), false));
        attributes.push_back(new entity::attribute("SubsequentAppliedLoads", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcStructuralLoad_type)), false));
        std::vector<bool> derived; derived.reserve(14);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPlanarActionVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPointAction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPointConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralPointReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(16);
        attributes.push_back(new entity::attribute("TorsionalConstantX", new named_type(IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentOfInertiaYZ", new named_type(IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentOfInertiaY", new named_type(IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("MomentOfInertiaZ", new named_type(IfcMomentOfInertiaMeasure_type), true));
        attributes.push_back(new entity::attribute("WarpingConstant", new named_type(IfcWarpingConstantMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearCentreZ", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearCentreY", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearDeformationAreaZ", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearDeformationAreaY", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumSectionModulusY", new named_type(IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumSectionModulusY", new named_type(IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("MaximumSectionModulusZ", new named_type(IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("MinimumSectionModulusZ", new named_type(IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("TorsionalSectionModulus", new named_type(IfcSectionModulusMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IfcLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IfcLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(23);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralReaction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TheoryType", new named_type(IfcAnalysisTheoryTypeEnum_type), false));
        attributes.push_back(new entity::attribute("ResultForLoadGroup", new named_type(IfcStructuralLoadGroup_type), true));
        attributes.push_back(new entity::attribute("IsLinear", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralResultGroup_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ShearAreaZ", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("ShearAreaY", new named_type(IfcAreaMeasure_type), true));
        attributes.push_back(new entity::attribute("PlasticShapeFactorY", new named_type(IfcPositiveRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("PlasticShapeFactorZ", new named_type(IfcPositiveRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(27);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSteelProfileProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceConnection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcStructuralSurfaceTypeEnum_type), false));
        attributes.push_back(new entity::attribute("Thickness", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceMember_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SubsequentThickness", new aggregation_type(aggregation_type::list_type, 2, -1, new named_type(IfcPositiveLengthMeasure_type)), false));
        attributes.push_back(new entity::attribute("VaryingThicknessLocation", new named_type(IfcShapeAspect_type), false));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStructuralSurfaceMemberVarying_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcStructuredDimensionCallout_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStyleModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Item", new named_type(IfcRepresentationItem_type), true));
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPresentationStyleAssignment_type)), false));
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStyledItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcStyledRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SubContractor", new named_type(IfcActorSelect_type), true));
        attributes.push_back(new entity::attribute("JobDescription", new named_type(IfcText_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSubContractResource_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ParentEdge", new named_type(IfcEdge_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSubedge_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("ReferenceSurface", new named_type(IfcSurface_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceCurveSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ExtrudedDirection", new named_type(IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceOfLinearExtrusion_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AxisPosition", new named_type(IfcAxis1Placement_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceOfRevolution_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Side", new named_type(IfcSurfaceSide_type), false));
        attributes.push_back(new entity::attribute("Styles", new aggregation_type(aggregation_type::set_type, 1, 5, new named_type(IfcSurfaceStyleElementSelect_type)), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("DiffuseTransmissionColour", new named_type(IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("DiffuseReflectionColour", new named_type(IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("TransmissionColour", new named_type(IfcColourRgb_type), false));
        attributes.push_back(new entity::attribute("ReflectanceColour", new named_type(IfcColourRgb_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceStyleLighting_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RefractionIndex", new named_type(IfcReal_type), true));
        attributes.push_back(new entity::attribute("DispersionFactor", new named_type(IfcReal_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSurfaceStyleRefraction_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Transparency", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("DiffuseColour", new named_type(IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("TransmissionColour", new named_type(IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("DiffuseTransmissionColour", new named_type(IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("ReflectionColour", new named_type(IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("SpecularColour", new named_type(IfcColourOrFactor_type), true));
        attributes.push_back(new entity::attribute("SpecularHighlight", new named_type(IfcSpecularHighlightSelect_type), true));
        attributes.push_back(new entity::attribute("ReflectanceMethod", new named_type(IfcReflectanceMethodEnum_type), false));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceStyleRendering_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SurfaceColour", new named_type(IfcColourRgb_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcSurfaceStyleShading_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Textures", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcSurfaceTexture_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcSurfaceStyleWithTextures_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("RepeatS", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("RepeatT", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("TextureType", new named_type(IfcSurfaceTextureEnum_type), false));
        attributes.push_back(new entity::attribute("TextureTransform", new named_type(IfcCartesianTransformationOperator2D_type), true));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSurfaceTexture_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptArea", new named_type(IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSweptAreaSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("Directrix", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Radius", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("InnerRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("StartParam", new named_type(IfcParameterValue_type), false));
        attributes.push_back(new entity::attribute("EndParam", new named_type(IfcParameterValue_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSweptDiskSolid_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("SweptCurve", new named_type(IfcProfileDef_type), false));
        attributes.push_back(new entity::attribute("Position", new named_type(IfcAxis2Placement3D_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSweptSurface_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcSwitchingDeviceTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSwitchingDeviceType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("StyleOfSymbol", new named_type(IfcSymbolStyleSelect_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcSymbolStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSystem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcSystemFurnitureElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeEdgeRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebEdgeRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("WebSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInY", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Name", new simple_type(simple_type::string_type), false));
        attributes.push_back(new entity::attribute("Rows", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcTableRow_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTable_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RowCells", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        attributes.push_back(new entity::attribute("IsHeading", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTableRow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTankTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTankType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("TaskId", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("Status", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("WorkMethod", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("IsMilestone", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Priority", new simple_type(simple_type::integer_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTask_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("TelephoneNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("FacsimileNumbers", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("PagerNumber", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("ElectronicMailAddresses", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcLabel_type)), true));
        attributes.push_back(new entity::attribute("WWWHomePageURL", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTelecomAddress_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTendonTypeEnum_type), false));
        attributes.push_back(new entity::attribute("NominalDiameter", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("CrossSectionArea", new named_type(IfcAreaMeasure_type), false));
        attributes.push_back(new entity::attribute("TensionForce", new named_type(IfcForceMeasure_type), true));
        attributes.push_back(new entity::attribute("PreStress", new named_type(IfcPressureMeasure_type), true));
        attributes.push_back(new entity::attribute("FrictionCoefficient", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("AnchorageSlip", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MinCurvatureRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(17);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTendon_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTendonAnchor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("AnnotatedCurve", new named_type(IfcAnnotationCurveOccurrence_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTerminatorSymbol_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("Literal", new named_type(IfcPresentableText_type), false));
        attributes.push_back(new entity::attribute("Placement", new named_type(IfcAxis2Placement_type), false));
        attributes.push_back(new entity::attribute("Path", new named_type(IfcTextPath_type), false));
        std::vector<bool> derived; derived.reserve(3);
        derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextLiteral_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Extent", new named_type(IfcPlanarExtent_type), false));
        attributes.push_back(new entity::attribute("BoxAlignment", new named_type(IfcBoxAlignment_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextLiteralWithExtent_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("TextCharacterAppearance", new named_type(IfcCharacterStyleSelect_type), true));
        attributes.push_back(new entity::attribute("TextStyle", new named_type(IfcTextStyleSelect_type), true));
        attributes.push_back(new entity::attribute("TextFontStyle", new named_type(IfcTextFontSelect_type), false));
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("FontFamily", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcTextFontName_type)), true));
        attributes.push_back(new entity::attribute("FontStyle", new named_type(IfcFontStyle_type), true));
        attributes.push_back(new entity::attribute("FontVariant", new named_type(IfcFontVariant_type), true));
        attributes.push_back(new entity::attribute("FontWeight", new named_type(IfcFontWeight_type), true));
        attributes.push_back(new entity::attribute("FontSize", new named_type(IfcSizeSelect_type), false));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextStyleFontModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Colour", new named_type(IfcColour_type), false));
        attributes.push_back(new entity::attribute("BackgroundColour", new named_type(IfcColour_type), true));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTextStyleForDefinedFont_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("TextIndent", new named_type(IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("TextAlign", new named_type(IfcTextAlignment_type), true));
        attributes.push_back(new entity::attribute("TextDecoration", new named_type(IfcTextDecoration_type), true));
        attributes.push_back(new entity::attribute("LetterSpacing", new named_type(IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("WordSpacing", new named_type(IfcSizeSelect_type), true));
        attributes.push_back(new entity::attribute("TextTransform", new named_type(IfcTextTransformation_type), true));
        attributes.push_back(new entity::attribute("LineHeight", new named_type(IfcSizeSelect_type), true));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextStyleTextModel_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("BoxHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BoxWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("BoxSlantAngle", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("BoxRotateAngle", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CharacterSpacing", new named_type(IfcSizeSelect_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTextStyleWithBoxCharacteristics_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcTextureCoordinate_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Mode", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Parameter", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcSimpleValue_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTextureCoordinateGenerator_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("TextureMaps", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcVertexBasedTextureMap_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Coordinates", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IfcParameterValue_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcTextureVertex_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("SpecificHeatCapacity", new named_type(IfcSpecificHeatCapacityMeasure_type), true));
        attributes.push_back(new entity::attribute("BoilingPoint", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("FreezingPoint", new named_type(IfcThermodynamicTemperatureMeasure_type), true));
        attributes.push_back(new entity::attribute("ThermalConductivity", new named_type(IfcThermalConductivityMeasure_type), true));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcThermalMaterialProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Name", new named_type(IfcLabel_type), false));
        attributes.push_back(new entity::attribute("Description", new named_type(IfcText_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("EndTime", new named_type(IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("TimeSeriesDataType", new named_type(IfcTimeSeriesDataTypeEnum_type), false));
        attributes.push_back(new entity::attribute("DataOrigin", new named_type(IfcDataOriginEnum_type), false));
        attributes.push_back(new entity::attribute("UserDefinedDataOrigin", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Unit", new named_type(IfcUnit_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTimeSeries_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ReferencedTimeSeries", new named_type(IfcTimeSeries_type), false));
        attributes.push_back(new entity::attribute("TimeSeriesReferences", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcDocumentSelect_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTimeSeriesReferenceRelationship_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("ApplicableDates", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcDateTimeSelect_type)), true));
        attributes.push_back(new entity::attribute("TimeSeriesScheduleType", new named_type(IfcTimeSeriesScheduleTypeEnum_type), false));
        attributes.push_back(new entity::attribute("TimeSeries", new named_type(IfcTimeSeries_type), false));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTimeSeriesSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("ListValues", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcValue_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcTimeSeriesValue_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcTopologicalRepresentationItem_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(4);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTopologyRepresentation_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTransformerTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTransformerType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcTransportElementTypeEnum_type), true));
        attributes.push_back(new entity::attribute("CapacityByWeight", new named_type(IfcMassMeasure_type), true));
        attributes.push_back(new entity::attribute("CapacityByNumber", new named_type(IfcCountMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTransportElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTransportElementTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTransportElementType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("BottomXDim", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopXDim", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("YDim", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("TopXOffset", new named_type(IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(7);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTrapeziumProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("BasisCurve", new named_type(IfcCurve_type), false));
        attributes.push_back(new entity::attribute("Trim1", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("Trim2", new aggregation_type(aggregation_type::set_type, 1, 2, new named_type(IfcTrimmingSelect_type)), false));
        attributes.push_back(new entity::attribute("SenseAgreement", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("MasterRepresentation", new named_type(IfcTrimmingPreference_type), false));
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTrimmedCurve_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcTubeBundleTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTubeBundleType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("SecondRepeatFactor", new named_type(IfcVector_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcTwoDirectionRepeatFactor_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("ApplicableOccurrence", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("HasPropertySets", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPropertySetDefinition_type)), true));
        std::vector<bool> derived; derived.reserve(6);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTypeObject_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("RepresentationMaps", new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(IfcRepresentationMap_type)), true));
        attributes.push_back(new entity::attribute("Tag", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcTypeProduct_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(8);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FlangeSlope", new named_type(IfcPlaneAngleMeasure_type), true));
        attributes.push_back(new entity::attribute("CentreOfGravityInX", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(11);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcUShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("Units", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcUnit_type)), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcUnitAssignment_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcUnitaryEquipmentTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcUnitaryEquipmentType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcValveTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcValveType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("Orientation", new named_type(IfcDirection_type), false));
        attributes.push_back(new entity::attribute("Magnitude", new named_type(IfcLengthMeasure_type), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcVector_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(0);
        
        IfcVertex_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("TextureVertices", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IfcTextureVertex_type)), false));
        attributes.push_back(new entity::attribute("TexturePoints", new aggregation_type(aggregation_type::list_type, 3, -1, new named_type(IfcCartesianPoint_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcVertexBasedTextureMap_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("LoopVertex", new named_type(IfcVertex_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcVertexLoop_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("VertexGeometry", new named_type(IfcPoint_type), false));
        std::vector<bool> derived; derived.reserve(1);
        derived.push_back(false);
        IfcVertexPoint_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcVibrationIsolatorTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcVibrationIsolatorType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcVirtualElement_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("IntersectingAxes", new aggregation_type(aggregation_type::list_type, 2, 2, new named_type(IfcGridAxis_type)), false));
        attributes.push_back(new entity::attribute("OffsetDistances", new aggregation_type(aggregation_type::list_type, 2, 3, new named_type(IfcLengthMeasure_type)), false));
        std::vector<bool> derived; derived.reserve(2);
        derived.push_back(false); derived.push_back(false);
        IfcVirtualGridIntersection_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWall_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWallStandardCase_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWallTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWallType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::attribute("PredefinedType", new named_type(IfcWasteTerminalTypeEnum_type), false));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWasteTerminalType_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(7);
        attributes.push_back(new entity::attribute("IsPotable", new simple_type(simple_type::boolean_type), true));
        attributes.push_back(new entity::attribute("Hardness", new named_type(IfcIonConcentrationMeasure_type), true));
        attributes.push_back(new entity::attribute("AlkalinityConcentration", new named_type(IfcIonConcentrationMeasure_type), true));
        attributes.push_back(new entity::attribute("AcidityConcentration", new named_type(IfcIonConcentrationMeasure_type), true));
        attributes.push_back(new entity::attribute("ImpuritiesContent", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("PHLevel", new named_type(IfcPHMeasure_type), true));
        attributes.push_back(new entity::attribute("DissolvedSolidsContent", new named_type(IfcNormalisedRatioMeasure_type), true));
        std::vector<bool> derived; derived.reserve(8);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWaterProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::attribute("OverallHeight", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("OverallWidth", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(10);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindow_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(9);
        attributes.push_back(new entity::attribute("LiningDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("LiningThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("TransomThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("MullionThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstTransomOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondTransomOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("FirstMullionOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("SecondMullionOffset", new named_type(IfcNormalisedRatioMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(13);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindowLiningProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(5);
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcWindowPanelOperationEnum_type), false));
        attributes.push_back(new entity::attribute("PanelPosition", new named_type(IfcWindowPanelPositionEnum_type), false));
        attributes.push_back(new entity::attribute("FrameDepth", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("FrameThickness", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("ShapeAspectStyle", new named_type(IfcShapeAspect_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindowPanelProperties_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::attribute("ConstructionType", new named_type(IfcWindowStyleConstructionEnum_type), false));
        attributes.push_back(new entity::attribute("OperationType", new named_type(IfcWindowStyleOperationEnum_type), false));
        attributes.push_back(new entity::attribute("ParameterTakesPrecedence", new simple_type(simple_type::boolean_type), false));
        attributes.push_back(new entity::attribute("Sizeable", new simple_type(simple_type::boolean_type), false));
        std::vector<bool> derived; derived.reserve(12);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWindowStyle_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(10);
        attributes.push_back(new entity::attribute("Identifier", new named_type(IfcIdentifier_type), false));
        attributes.push_back(new entity::attribute("CreationDate", new named_type(IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("Creators", new aggregation_type(aggregation_type::set_type, 1, -1, new named_type(IfcPerson_type)), true));
        attributes.push_back(new entity::attribute("Purpose", new named_type(IfcLabel_type), true));
        attributes.push_back(new entity::attribute("Duration", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("TotalFloat", new named_type(IfcTimeMeasure_type), true));
        attributes.push_back(new entity::attribute("StartTime", new named_type(IfcDateTimeSelect_type), false));
        attributes.push_back(new entity::attribute("FinishTime", new named_type(IfcDateTimeSelect_type), true));
        attributes.push_back(new entity::attribute("WorkControlType", new named_type(IfcWorkControlTypeEnum_type), true));
        attributes.push_back(new entity::attribute("UserDefinedControlType", new named_type(IfcLabel_type), true));
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkControl_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkPlan_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(15);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcWorkSchedule_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::attribute("Depth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeWidth", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("WebThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FlangeThickness", new named_type(IfcPositiveLengthMeasure_type), false));
        attributes.push_back(new entity::attribute("FilletRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        attributes.push_back(new entity::attribute("EdgeRadius", new named_type(IfcPositiveLengthMeasure_type), true));
        std::vector<bool> derived; derived.reserve(9);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcZShapeProfileDef_type->set_attributes(attributes, derived);
    }
    {
        std::vector<const entity::attribute*> attributes; attributes.reserve(0);
        std::vector<bool> derived; derived.reserve(5);
        derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false); derived.push_back(false);
        IfcZone_type->set_attributes(attributes, derived);
    }
}

#endif
