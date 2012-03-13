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
 
#ifndef IFC2X3_H
#define IFC2X3_H

#include <string>
#include <vector>
#include <map>

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/Ifc2x3enum.h"

using namespace IfcUtil;

#define RETURN_INVERSE(T) \
    IfcEntities e = entity->getInverse(T::Class()); \
    SHARED_PTR< IfcTemplatedEntityList<T> > l ( new IfcTemplatedEntityList<T>() ); \
    for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) { \
        l->push(reinterpret_pointer_cast<IfcBaseClass,T>(*it)); \
    } \
    return l;

#define RETURN_AS_SINGLE(T,a) \
    return reinterpret_pointer_cast<IfcBaseClass,T>(*entity->getArgument(a));

#define RETURN_AS_LIST(T,a)  \
    IfcEntities e = *entity->getArgument(a);  \
    SHARED_PTR< IfcTemplatedEntityList<T> > l ( new IfcTemplatedEntityList<T>() );  \
    for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) {  \
        l->push(reinterpret_pointer_cast<IfcBaseClass,T>(*it)); \
    }  \
    return l;

namespace Ifc2x3 {

typedef double IfcAbsorbedDoseMeasure;
typedef double IfcAccelerationMeasure;
typedef double IfcAmountOfSubstanceMeasure;
typedef double IfcAngularVelocityMeasure;
typedef double IfcAreaMeasure;
typedef bool IfcBoolean;
typedef std::vector<double> /*[1:2]*/ IfcComplexNumber;
typedef std::vector<int> /*[3:4]*/ IfcCompoundPlaneAngleMeasure;
typedef double IfcContextDependentMeasure;
typedef double IfcCountMeasure;
typedef double IfcCurvatureMeasure;
typedef int IfcDayInMonthNumber;
typedef int IfcDaylightSavingHour;
typedef std::string IfcDescriptiveMeasure;
typedef int IfcDimensionCount;
typedef double IfcDoseEquivalentMeasure;
typedef double IfcDynamicViscosityMeasure;
typedef double IfcElectricCapacitanceMeasure;
typedef double IfcElectricChargeMeasure;
typedef double IfcElectricConductanceMeasure;
typedef double IfcElectricCurrentMeasure;
typedef double IfcElectricResistanceMeasure;
typedef double IfcElectricVoltageMeasure;
typedef double IfcEnergyMeasure;
typedef std::string IfcFontStyle;
typedef std::string IfcFontVariant;
typedef std::string IfcFontWeight;
typedef double IfcForceMeasure;
typedef double IfcFrequencyMeasure;
typedef std::string IfcGloballyUniqueId;
typedef double IfcHeatFluxDensityMeasure;
typedef double IfcHeatingValueMeasure;
typedef int IfcHourInDay;
typedef std::string IfcIdentifier;
typedef double IfcIlluminanceMeasure;
typedef double IfcInductanceMeasure;
typedef int IfcInteger;
typedef int IfcIntegerCountRateMeasure;
typedef double IfcIonConcentrationMeasure;
typedef double IfcIsothermalMoistureCapacityMeasure;
typedef double IfcKinematicViscosityMeasure;
typedef std::string IfcLabel;
typedef double IfcLengthMeasure;
typedef double IfcLinearForceMeasure;
typedef double IfcLinearMomentMeasure;
typedef double IfcLinearStiffnessMeasure;
typedef double IfcLinearVelocityMeasure;
typedef bool IfcLogical;
typedef double IfcLuminousFluxMeasure;
typedef double IfcLuminousIntensityDistributionMeasure;
typedef double IfcLuminousIntensityMeasure;
typedef double IfcMagneticFluxDensityMeasure;
typedef double IfcMagneticFluxMeasure;
typedef double IfcMassDensityMeasure;
typedef double IfcMassFlowRateMeasure;
typedef double IfcMassMeasure;
typedef double IfcMassPerLengthMeasure;
typedef int IfcMinuteInHour;
typedef double IfcModulusOfElasticityMeasure;
typedef double IfcModulusOfLinearSubgradeReactionMeasure;
typedef double IfcModulusOfRotationalSubgradeReactionMeasure;
typedef double IfcModulusOfSubgradeReactionMeasure;
typedef double IfcMoistureDiffusivityMeasure;
typedef double IfcMolecularWeightMeasure;
typedef double IfcMomentOfInertiaMeasure;
typedef double IfcMonetaryMeasure;
typedef int IfcMonthInYearNumber;
typedef double IfcNumericMeasure;
typedef double IfcPHMeasure;
typedef double IfcParameterValue;
typedef double IfcPlanarForceMeasure;
typedef double IfcPlaneAngleMeasure;
typedef double IfcPowerMeasure;
typedef std::string IfcPresentableText;
typedef double IfcPressureMeasure;
typedef double IfcRadioActivityMeasure;
typedef double IfcRatioMeasure;
typedef double IfcReal;
typedef double IfcRotationalFrequencyMeasure;
typedef double IfcRotationalMassMeasure;
typedef double IfcRotationalStiffnessMeasure;
typedef double IfcSecondInMinute;
typedef double IfcSectionModulusMeasure;
typedef double IfcSectionalAreaIntegralMeasure;
typedef double IfcShearModulusMeasure;
typedef double IfcSolidAngleMeasure;
typedef double IfcSoundPowerMeasure;
typedef double IfcSoundPressureMeasure;
typedef double IfcSpecificHeatCapacityMeasure;
typedef double IfcSpecularExponent;
typedef double IfcSpecularRoughness;
typedef double IfcTemperatureGradientMeasure;
typedef std::string IfcText;
typedef std::string IfcTextAlignment;
typedef std::string IfcTextDecoration;
typedef std::string IfcTextFontName;
typedef std::string IfcTextTransformation;
typedef double IfcThermalAdmittanceMeasure;
typedef double IfcThermalConductivityMeasure;
typedef double IfcThermalExpansionCoefficientMeasure;
typedef double IfcThermalResistanceMeasure;
typedef double IfcThermalTransmittanceMeasure;
typedef double IfcThermodynamicTemperatureMeasure;
typedef double IfcTimeMeasure;
typedef int IfcTimeStamp;
typedef double IfcTorqueMeasure;
typedef double IfcVaporPermeabilityMeasure;
typedef double IfcVolumeMeasure;
typedef double IfcVolumetricFlowRateMeasure;
typedef double IfcWarpingConstantMeasure;
typedef double IfcWarpingMomentMeasure;
typedef int IfcYearNumber;
typedef IfcSchemaEntity IfcActorSelect;
typedef IfcSchemaEntity IfcAppliedValueSelect;
typedef IfcSchemaEntity IfcAxis2Placement;
typedef IfcSchemaEntity IfcBooleanOperand;
typedef IfcSchemaEntity IfcCharacterStyleSelect;
typedef IfcSchemaEntity IfcClassificationNotationSelect;
typedef IfcSchemaEntity IfcColour;
typedef IfcSchemaEntity IfcColourOrFactor;
typedef IfcSchemaEntity IfcConditionCriterionSelect;
typedef IfcSchemaEntity IfcCsgSelect;
typedef IfcSchemaEntity IfcCurveFontOrScaledCurveFontSelect;
typedef IfcSchemaEntity IfcCurveOrEdgeCurve;
typedef IfcSchemaEntity IfcCurveStyleFontSelect;
typedef IfcSchemaEntity IfcDateTimeSelect;
typedef IfcSchemaEntity IfcDefinedSymbolSelect;
typedef IfcSchemaEntity IfcDerivedMeasureValue;
typedef IfcSchemaEntity IfcDocumentSelect;
typedef IfcSchemaEntity IfcDraughtingCalloutElement;
typedef IfcSchemaEntity IfcFillAreaStyleTileShapeSelect;
typedef IfcSchemaEntity IfcFillStyleSelect;
typedef IfcSchemaEntity IfcGeometricSetSelect;
typedef IfcSchemaEntity IfcHatchLineDistanceSelect;
typedef IfcSchemaEntity IfcLayeredItem;
typedef IfcSchemaEntity IfcLibrarySelect;
typedef IfcSchemaEntity IfcLightDistributionDataSourceSelect;
typedef IfcSchemaEntity IfcMaterialSelect;
typedef IfcSchemaEntity IfcMeasureValue;
typedef IfcSchemaEntity IfcMetricValueSelect;
typedef IfcSchemaEntity IfcObjectReferenceSelect;
typedef IfcSchemaEntity IfcOrientationSelect;
typedef IfcSchemaEntity IfcPointOrVertexPoint;
typedef IfcSchemaEntity IfcPresentationStyleSelect;
typedef IfcSchemaEntity IfcShell;
typedef IfcSchemaEntity IfcSimpleValue;
typedef IfcSchemaEntity IfcSizeSelect;
typedef IfcSchemaEntity IfcSpecularHighlightSelect;
typedef IfcSchemaEntity IfcStructuralActivityAssignmentSelect;
typedef IfcSchemaEntity IfcSurfaceOrFaceSurface;
typedef IfcSchemaEntity IfcSurfaceStyleElementSelect;
typedef IfcSchemaEntity IfcSymbolStyleSelect;
typedef IfcSchemaEntity IfcTextFontSelect;
typedef IfcSchemaEntity IfcTextStyleSelect;
typedef IfcSchemaEntity IfcTrimmingSelect;
typedef IfcSchemaEntity IfcUnit;
typedef IfcSchemaEntity IfcValue;
typedef IfcSchemaEntity IfcVectorOrDirection;
typedef IfcLabel IfcBoxAlignment;
typedef IfcRatioMeasure IfcNormalisedRatioMeasure;
typedef IfcLengthMeasure IfcPositiveLengthMeasure;
typedef IfcPlaneAngleMeasure IfcPositivePlaneAngleMeasure;
typedef IfcRatioMeasure IfcPositiveRatioMeasure;
namespace IfcActionSourceTypeEnum {typedef enum {IfcActionSourceType_DEAD_LOAD_G, IfcActionSourceType_COMPLETION_G1, IfcActionSourceType_LIVE_LOAD_Q, IfcActionSourceType_SNOW_S, IfcActionSourceType_WIND_W, IfcActionSourceType_PRESTRESSING_P, IfcActionSourceType_SETTLEMENT_U, IfcActionSourceType_TEMPERATURE_T, IfcActionSourceType_EARTHQUAKE_E, IfcActionSourceType_FIRE, IfcActionSourceType_IMPULSE, IfcActionSourceType_IMPACT, IfcActionSourceType_TRANSPORT, IfcActionSourceType_ERECTION, IfcActionSourceType_PROPPING, IfcActionSourceType_SYSTEM_IMPERFECTION, IfcActionSourceType_SHRINKAGE, IfcActionSourceType_CREEP, IfcActionSourceType_LACK_OF_FIT, IfcActionSourceType_BUOYANCY, IfcActionSourceType_ICE, IfcActionSourceType_CURRENT, IfcActionSourceType_WAVE, IfcActionSourceType_RAIN, IfcActionSourceType_BRAKES, IfcActionSourceType_USERDEFINED, IfcActionSourceType_NOTDEFINED} IfcActionSourceTypeEnum;
std::string ToString(IfcActionSourceTypeEnum v);
IfcActionSourceTypeEnum FromString(const std::string& s);}
namespace IfcActionTypeEnum {typedef enum {IfcActionType_PERMANENT_G, IfcActionType_VARIABLE_Q, IfcActionType_EXTRAORDINARY_A, IfcActionType_USERDEFINED, IfcActionType_NOTDEFINED} IfcActionTypeEnum;
std::string ToString(IfcActionTypeEnum v);
IfcActionTypeEnum FromString(const std::string& s);}
namespace IfcActuatorTypeEnum {typedef enum {IfcActuatorType_ELECTRICACTUATOR, IfcActuatorType_HANDOPERATEDACTUATOR, IfcActuatorType_HYDRAULICACTUATOR, IfcActuatorType_PNEUMATICACTUATOR, IfcActuatorType_THERMOSTATICACTUATOR, IfcActuatorType_USERDEFINED, IfcActuatorType_NOTDEFINED} IfcActuatorTypeEnum;
std::string ToString(IfcActuatorTypeEnum v);
IfcActuatorTypeEnum FromString(const std::string& s);}
namespace IfcAddressTypeEnum {typedef enum {IfcAddressType_OFFICE, IfcAddressType_SITE, IfcAddressType_HOME, IfcAddressType_DISTRIBUTIONPOINT, IfcAddressType_USERDEFINED} IfcAddressTypeEnum;
std::string ToString(IfcAddressTypeEnum v);
IfcAddressTypeEnum FromString(const std::string& s);}
namespace IfcAheadOrBehind {typedef enum {IfcAheadOrBehind_AHEAD, IfcAheadOrBehind_BEHIND} IfcAheadOrBehind;
std::string ToString(IfcAheadOrBehind v);
IfcAheadOrBehind FromString(const std::string& s);}
namespace IfcAirTerminalBoxTypeEnum {typedef enum {IfcAirTerminalBoxType_CONSTANTFLOW, IfcAirTerminalBoxType_VARIABLEFLOWPRESSUREDEPENDANT, IfcAirTerminalBoxType_VARIABLEFLOWPRESSUREINDEPENDANT, IfcAirTerminalBoxType_USERDEFINED, IfcAirTerminalBoxType_NOTDEFINED} IfcAirTerminalBoxTypeEnum;
std::string ToString(IfcAirTerminalBoxTypeEnum v);
IfcAirTerminalBoxTypeEnum FromString(const std::string& s);}
namespace IfcAirTerminalTypeEnum {typedef enum {IfcAirTerminalType_GRILLE, IfcAirTerminalType_REGISTER, IfcAirTerminalType_DIFFUSER, IfcAirTerminalType_EYEBALL, IfcAirTerminalType_IRIS, IfcAirTerminalType_LINEARGRILLE, IfcAirTerminalType_LINEARDIFFUSER, IfcAirTerminalType_USERDEFINED, IfcAirTerminalType_NOTDEFINED} IfcAirTerminalTypeEnum;
std::string ToString(IfcAirTerminalTypeEnum v);
IfcAirTerminalTypeEnum FromString(const std::string& s);}
namespace IfcAirToAirHeatRecoveryTypeEnum {typedef enum {IfcAirToAirHeatRecoveryType_FIXEDPLATECOUNTERFLOWEXCHANGER, IfcAirToAirHeatRecoveryType_FIXEDPLATECROSSFLOWEXCHANGER, IfcAirToAirHeatRecoveryType_FIXEDPLATEPARALLELFLOWEXCHANGER, IfcAirToAirHeatRecoveryType_ROTARYWHEEL, IfcAirToAirHeatRecoveryType_RUNAROUNDCOILLOOP, IfcAirToAirHeatRecoveryType_HEATPIPE, IfcAirToAirHeatRecoveryType_TWINTOWERENTHALPYRECOVERYLOOPS, IfcAirToAirHeatRecoveryType_THERMOSIPHONSEALEDTUBEHEATEXCHANGERS, IfcAirToAirHeatRecoveryType_THERMOSIPHONCOILTYPEHEATEXCHANGERS, IfcAirToAirHeatRecoveryType_USERDEFINED, IfcAirToAirHeatRecoveryType_NOTDEFINED} IfcAirToAirHeatRecoveryTypeEnum;
std::string ToString(IfcAirToAirHeatRecoveryTypeEnum v);
IfcAirToAirHeatRecoveryTypeEnum FromString(const std::string& s);}
namespace IfcAlarmTypeEnum {typedef enum {IfcAlarmType_BELL, IfcAlarmType_BREAKGLASSBUTTON, IfcAlarmType_LIGHT, IfcAlarmType_MANUALPULLBOX, IfcAlarmType_SIREN, IfcAlarmType_WHISTLE, IfcAlarmType_USERDEFINED, IfcAlarmType_NOTDEFINED} IfcAlarmTypeEnum;
std::string ToString(IfcAlarmTypeEnum v);
IfcAlarmTypeEnum FromString(const std::string& s);}
namespace IfcAnalysisModelTypeEnum {typedef enum {IfcAnalysisModelType_IN_PLANE_LOADING_2D, IfcAnalysisModelType_OUT_PLANE_LOADING_2D, IfcAnalysisModelType_LOADING_3D, IfcAnalysisModelType_USERDEFINED, IfcAnalysisModelType_NOTDEFINED} IfcAnalysisModelTypeEnum;
std::string ToString(IfcAnalysisModelTypeEnum v);
IfcAnalysisModelTypeEnum FromString(const std::string& s);}
namespace IfcAnalysisTheoryTypeEnum {typedef enum {IfcAnalysisTheoryType_FIRST_ORDER_THEORY, IfcAnalysisTheoryType_SECOND_ORDER_THEORY, IfcAnalysisTheoryType_THIRD_ORDER_THEORY, IfcAnalysisTheoryType_FULL_NONLINEAR_THEORY, IfcAnalysisTheoryType_USERDEFINED, IfcAnalysisTheoryType_NOTDEFINED} IfcAnalysisTheoryTypeEnum;
std::string ToString(IfcAnalysisTheoryTypeEnum v);
IfcAnalysisTheoryTypeEnum FromString(const std::string& s);}
namespace IfcArithmeticOperatorEnum {typedef enum {IfcArithmeticOperator_ADD, IfcArithmeticOperator_DIVIDE, IfcArithmeticOperator_MULTIPLY, IfcArithmeticOperator_SUBTRACT} IfcArithmeticOperatorEnum;
std::string ToString(IfcArithmeticOperatorEnum v);
IfcArithmeticOperatorEnum FromString(const std::string& s);}
namespace IfcAssemblyPlaceEnum {typedef enum {IfcAssemblyPlace_SITE, IfcAssemblyPlace_FACTORY, IfcAssemblyPlace_NOTDEFINED} IfcAssemblyPlaceEnum;
std::string ToString(IfcAssemblyPlaceEnum v);
IfcAssemblyPlaceEnum FromString(const std::string& s);}
namespace IfcBSplineCurveForm {typedef enum {IfcBSplineCurveForm_POLYLINE_FORM, IfcBSplineCurveForm_CIRCULAR_ARC, IfcBSplineCurveForm_ELLIPTIC_ARC, IfcBSplineCurveForm_PARABOLIC_ARC, IfcBSplineCurveForm_HYPERBOLIC_ARC, IfcBSplineCurveForm_UNSPECIFIED} IfcBSplineCurveForm;
std::string ToString(IfcBSplineCurveForm v);
IfcBSplineCurveForm FromString(const std::string& s);}
namespace IfcBeamTypeEnum {typedef enum {IfcBeamType_BEAM, IfcBeamType_JOIST, IfcBeamType_LINTEL, IfcBeamType_T_BEAM, IfcBeamType_USERDEFINED, IfcBeamType_NOTDEFINED} IfcBeamTypeEnum;
std::string ToString(IfcBeamTypeEnum v);
IfcBeamTypeEnum FromString(const std::string& s);}
namespace IfcBenchmarkEnum {typedef enum {IfcBenchmark_GREATERTHAN, IfcBenchmark_GREATERTHANOREQUALTO, IfcBenchmark_LESSTHAN, IfcBenchmark_LESSTHANOREQUALTO, IfcBenchmark_EQUALTO, IfcBenchmark_NOTEQUALTO} IfcBenchmarkEnum;
std::string ToString(IfcBenchmarkEnum v);
IfcBenchmarkEnum FromString(const std::string& s);}
namespace IfcBoilerTypeEnum {typedef enum {IfcBoilerType_WATER, IfcBoilerType_STEAM, IfcBoilerType_USERDEFINED, IfcBoilerType_NOTDEFINED} IfcBoilerTypeEnum;
std::string ToString(IfcBoilerTypeEnum v);
IfcBoilerTypeEnum FromString(const std::string& s);}
namespace IfcBooleanOperator {typedef enum {IfcBooleanOperator_UNION, IfcBooleanOperator_INTERSECTION, IfcBooleanOperator_DIFFERENCE} IfcBooleanOperator;
std::string ToString(IfcBooleanOperator v);
IfcBooleanOperator FromString(const std::string& s);}
namespace IfcBuildingElementProxyTypeEnum {typedef enum {IfcBuildingElementProxyType_USERDEFINED, IfcBuildingElementProxyType_NOTDEFINED} IfcBuildingElementProxyTypeEnum;
std::string ToString(IfcBuildingElementProxyTypeEnum v);
IfcBuildingElementProxyTypeEnum FromString(const std::string& s);}
namespace IfcCableCarrierFittingTypeEnum {typedef enum {IfcCableCarrierFittingType_BEND, IfcCableCarrierFittingType_CROSS, IfcCableCarrierFittingType_REDUCER, IfcCableCarrierFittingType_TEE, IfcCableCarrierFittingType_USERDEFINED, IfcCableCarrierFittingType_NOTDEFINED} IfcCableCarrierFittingTypeEnum;
std::string ToString(IfcCableCarrierFittingTypeEnum v);
IfcCableCarrierFittingTypeEnum FromString(const std::string& s);}
namespace IfcCableCarrierSegmentTypeEnum {typedef enum {IfcCableCarrierSegmentType_CABLELADDERSEGMENT, IfcCableCarrierSegmentType_CABLETRAYSEGMENT, IfcCableCarrierSegmentType_CABLETRUNKINGSEGMENT, IfcCableCarrierSegmentType_CONDUITSEGMENT, IfcCableCarrierSegmentType_USERDEFINED, IfcCableCarrierSegmentType_NOTDEFINED} IfcCableCarrierSegmentTypeEnum;
std::string ToString(IfcCableCarrierSegmentTypeEnum v);
IfcCableCarrierSegmentTypeEnum FromString(const std::string& s);}
namespace IfcCableSegmentTypeEnum {typedef enum {IfcCableSegmentType_CABLESEGMENT, IfcCableSegmentType_CONDUCTORSEGMENT, IfcCableSegmentType_USERDEFINED, IfcCableSegmentType_NOTDEFINED} IfcCableSegmentTypeEnum;
std::string ToString(IfcCableSegmentTypeEnum v);
IfcCableSegmentTypeEnum FromString(const std::string& s);}
namespace IfcChangeActionEnum {typedef enum {IfcChangeAction_NOCHANGE, IfcChangeAction_MODIFIED, IfcChangeAction_ADDED, IfcChangeAction_DELETED, IfcChangeAction_MODIFIEDADDED, IfcChangeAction_MODIFIEDDELETED} IfcChangeActionEnum;
std::string ToString(IfcChangeActionEnum v);
IfcChangeActionEnum FromString(const std::string& s);}
namespace IfcChillerTypeEnum {typedef enum {IfcChillerType_AIRCOOLED, IfcChillerType_WATERCOOLED, IfcChillerType_HEATRECOVERY, IfcChillerType_USERDEFINED, IfcChillerType_NOTDEFINED} IfcChillerTypeEnum;
std::string ToString(IfcChillerTypeEnum v);
IfcChillerTypeEnum FromString(const std::string& s);}
namespace IfcCoilTypeEnum {typedef enum {IfcCoilType_DXCOOLINGCOIL, IfcCoilType_WATERCOOLINGCOIL, IfcCoilType_STEAMHEATINGCOIL, IfcCoilType_WATERHEATINGCOIL, IfcCoilType_ELECTRICHEATINGCOIL, IfcCoilType_GASHEATINGCOIL, IfcCoilType_USERDEFINED, IfcCoilType_NOTDEFINED} IfcCoilTypeEnum;
std::string ToString(IfcCoilTypeEnum v);
IfcCoilTypeEnum FromString(const std::string& s);}
namespace IfcColumnTypeEnum {typedef enum {IfcColumnType_COLUMN, IfcColumnType_USERDEFINED, IfcColumnType_NOTDEFINED} IfcColumnTypeEnum;
std::string ToString(IfcColumnTypeEnum v);
IfcColumnTypeEnum FromString(const std::string& s);}
namespace IfcCompressorTypeEnum {typedef enum {IfcCompressorType_DYNAMIC, IfcCompressorType_RECIPROCATING, IfcCompressorType_ROTARY, IfcCompressorType_SCROLL, IfcCompressorType_TROCHOIDAL, IfcCompressorType_SINGLESTAGE, IfcCompressorType_BOOSTER, IfcCompressorType_OPENTYPE, IfcCompressorType_HERMETIC, IfcCompressorType_SEMIHERMETIC, IfcCompressorType_WELDEDSHELLHERMETIC, IfcCompressorType_ROLLINGPISTON, IfcCompressorType_ROTARYVANE, IfcCompressorType_SINGLESCREW, IfcCompressorType_TWINSCREW, IfcCompressorType_USERDEFINED, IfcCompressorType_NOTDEFINED} IfcCompressorTypeEnum;
std::string ToString(IfcCompressorTypeEnum v);
IfcCompressorTypeEnum FromString(const std::string& s);}
namespace IfcCondenserTypeEnum {typedef enum {IfcCondenserType_WATERCOOLEDSHELLTUBE, IfcCondenserType_WATERCOOLEDSHELLCOIL, IfcCondenserType_WATERCOOLEDTUBEINTUBE, IfcCondenserType_WATERCOOLEDBRAZEDPLATE, IfcCondenserType_AIRCOOLED, IfcCondenserType_EVAPORATIVECOOLED, IfcCondenserType_USERDEFINED, IfcCondenserType_NOTDEFINED} IfcCondenserTypeEnum;
std::string ToString(IfcCondenserTypeEnum v);
IfcCondenserTypeEnum FromString(const std::string& s);}
namespace IfcConnectionTypeEnum {typedef enum {IfcConnectionType_ATPATH, IfcConnectionType_ATSTART, IfcConnectionType_ATEND, IfcConnectionType_NOTDEFINED} IfcConnectionTypeEnum;
std::string ToString(IfcConnectionTypeEnum v);
IfcConnectionTypeEnum FromString(const std::string& s);}
namespace IfcConstraintEnum {typedef enum {IfcConstraint_HARD, IfcConstraint_SOFT, IfcConstraint_ADVISORY, IfcConstraint_USERDEFINED, IfcConstraint_NOTDEFINED} IfcConstraintEnum;
std::string ToString(IfcConstraintEnum v);
IfcConstraintEnum FromString(const std::string& s);}
namespace IfcControllerTypeEnum {typedef enum {IfcControllerType_FLOATING, IfcControllerType_PROPORTIONAL, IfcControllerType_PROPORTIONALINTEGRAL, IfcControllerType_PROPORTIONALINTEGRALDERIVATIVE, IfcControllerType_TIMEDTWOPOSITION, IfcControllerType_TWOPOSITION, IfcControllerType_USERDEFINED, IfcControllerType_NOTDEFINED} IfcControllerTypeEnum;
std::string ToString(IfcControllerTypeEnum v);
IfcControllerTypeEnum FromString(const std::string& s);}
namespace IfcCooledBeamTypeEnum {typedef enum {IfcCooledBeamType_ACTIVE, IfcCooledBeamType_PASSIVE, IfcCooledBeamType_USERDEFINED, IfcCooledBeamType_NOTDEFINED} IfcCooledBeamTypeEnum;
std::string ToString(IfcCooledBeamTypeEnum v);
IfcCooledBeamTypeEnum FromString(const std::string& s);}
namespace IfcCoolingTowerTypeEnum {typedef enum {IfcCoolingTowerType_NATURALDRAFT, IfcCoolingTowerType_MECHANICALINDUCEDDRAFT, IfcCoolingTowerType_MECHANICALFORCEDDRAFT, IfcCoolingTowerType_USERDEFINED, IfcCoolingTowerType_NOTDEFINED} IfcCoolingTowerTypeEnum;
std::string ToString(IfcCoolingTowerTypeEnum v);
IfcCoolingTowerTypeEnum FromString(const std::string& s);}
namespace IfcCostScheduleTypeEnum {typedef enum {IfcCostScheduleType_BUDGET, IfcCostScheduleType_COSTPLAN, IfcCostScheduleType_ESTIMATE, IfcCostScheduleType_TENDER, IfcCostScheduleType_PRICEDBILLOFQUANTITIES, IfcCostScheduleType_UNPRICEDBILLOFQUANTITIES, IfcCostScheduleType_SCHEDULEOFRATES, IfcCostScheduleType_USERDEFINED, IfcCostScheduleType_NOTDEFINED} IfcCostScheduleTypeEnum;
std::string ToString(IfcCostScheduleTypeEnum v);
IfcCostScheduleTypeEnum FromString(const std::string& s);}
namespace IfcCoveringTypeEnum {typedef enum {IfcCoveringType_CEILING, IfcCoveringType_FLOORING, IfcCoveringType_CLADDING, IfcCoveringType_ROOFING, IfcCoveringType_INSULATION, IfcCoveringType_MEMBRANE, IfcCoveringType_SLEEVING, IfcCoveringType_WRAPPING, IfcCoveringType_USERDEFINED, IfcCoveringType_NOTDEFINED} IfcCoveringTypeEnum;
std::string ToString(IfcCoveringTypeEnum v);
IfcCoveringTypeEnum FromString(const std::string& s);}
namespace IfcCurrencyEnum {typedef enum {IfcCurrency_AED, IfcCurrency_AES, IfcCurrency_ATS, IfcCurrency_AUD, IfcCurrency_BBD, IfcCurrency_BEG, IfcCurrency_BGL, IfcCurrency_BHD, IfcCurrency_BMD, IfcCurrency_BND, IfcCurrency_BRL, IfcCurrency_BSD, IfcCurrency_BWP, IfcCurrency_BZD, IfcCurrency_CAD, IfcCurrency_CBD, IfcCurrency_CHF, IfcCurrency_CLP, IfcCurrency_CNY, IfcCurrency_CYS, IfcCurrency_CZK, IfcCurrency_DDP, IfcCurrency_DEM, IfcCurrency_DKK, IfcCurrency_EGL, IfcCurrency_EST, IfcCurrency_EUR, IfcCurrency_FAK, IfcCurrency_FIM, IfcCurrency_FJD, IfcCurrency_FKP, IfcCurrency_FRF, IfcCurrency_GBP, IfcCurrency_GIP, IfcCurrency_GMD, IfcCurrency_GRX, IfcCurrency_HKD, IfcCurrency_HUF, IfcCurrency_ICK, IfcCurrency_IDR, IfcCurrency_ILS, IfcCurrency_INR, IfcCurrency_IRP, IfcCurrency_ITL, IfcCurrency_JMD, IfcCurrency_JOD, IfcCurrency_JPY, IfcCurrency_KES, IfcCurrency_KRW, IfcCurrency_KWD, IfcCurrency_KYD, IfcCurrency_LKR, IfcCurrency_LUF, IfcCurrency_MTL, IfcCurrency_MUR, IfcCurrency_MXN, IfcCurrency_MYR, IfcCurrency_NLG, IfcCurrency_NZD, IfcCurrency_OMR, IfcCurrency_PGK, IfcCurrency_PHP, IfcCurrency_PKR, IfcCurrency_PLN, IfcCurrency_PTN, IfcCurrency_QAR, IfcCurrency_RUR, IfcCurrency_SAR, IfcCurrency_SCR, IfcCurrency_SEK, IfcCurrency_SGD, IfcCurrency_SKP, IfcCurrency_THB, IfcCurrency_TRL, IfcCurrency_TTD, IfcCurrency_TWD, IfcCurrency_USD, IfcCurrency_VEB, IfcCurrency_VND, IfcCurrency_XEU, IfcCurrency_ZAR, IfcCurrency_ZWD, IfcCurrency_NOK} IfcCurrencyEnum;
std::string ToString(IfcCurrencyEnum v);
IfcCurrencyEnum FromString(const std::string& s);}
namespace IfcCurtainWallTypeEnum {typedef enum {IfcCurtainWallType_USERDEFINED, IfcCurtainWallType_NOTDEFINED} IfcCurtainWallTypeEnum;
std::string ToString(IfcCurtainWallTypeEnum v);
IfcCurtainWallTypeEnum FromString(const std::string& s);}
namespace IfcDamperTypeEnum {typedef enum {IfcDamperType_CONTROLDAMPER, IfcDamperType_FIREDAMPER, IfcDamperType_SMOKEDAMPER, IfcDamperType_FIRESMOKEDAMPER, IfcDamperType_BACKDRAFTDAMPER, IfcDamperType_RELIEFDAMPER, IfcDamperType_BLASTDAMPER, IfcDamperType_GRAVITYDAMPER, IfcDamperType_GRAVITYRELIEFDAMPER, IfcDamperType_BALANCINGDAMPER, IfcDamperType_FUMEHOODEXHAUST, IfcDamperType_USERDEFINED, IfcDamperType_NOTDEFINED} IfcDamperTypeEnum;
std::string ToString(IfcDamperTypeEnum v);
IfcDamperTypeEnum FromString(const std::string& s);}
namespace IfcDataOriginEnum {typedef enum {IfcDataOrigin_MEASURED, IfcDataOrigin_PREDICTED, IfcDataOrigin_SIMULATED, IfcDataOrigin_USERDEFINED, IfcDataOrigin_NOTDEFINED} IfcDataOriginEnum;
std::string ToString(IfcDataOriginEnum v);
IfcDataOriginEnum FromString(const std::string& s);}
namespace IfcDerivedUnitEnum {typedef enum {IfcDerivedUnit_ANGULARVELOCITYUNIT, IfcDerivedUnit_COMPOUNDPLANEANGLEUNIT, IfcDerivedUnit_DYNAMICVISCOSITYUNIT, IfcDerivedUnit_HEATFLUXDENSITYUNIT, IfcDerivedUnit_INTEGERCOUNTRATEUNIT, IfcDerivedUnit_ISOTHERMALMOISTURECAPACITYUNIT, IfcDerivedUnit_KINEMATICVISCOSITYUNIT, IfcDerivedUnit_LINEARVELOCITYUNIT, IfcDerivedUnit_MASSDENSITYUNIT, IfcDerivedUnit_MASSFLOWRATEUNIT, IfcDerivedUnit_MOISTUREDIFFUSIVITYUNIT, IfcDerivedUnit_MOLECULARWEIGHTUNIT, IfcDerivedUnit_SPECIFICHEATCAPACITYUNIT, IfcDerivedUnit_THERMALADMITTANCEUNIT, IfcDerivedUnit_THERMALCONDUCTANCEUNIT, IfcDerivedUnit_THERMALRESISTANCEUNIT, IfcDerivedUnit_THERMALTRANSMITTANCEUNIT, IfcDerivedUnit_VAPORPERMEABILITYUNIT, IfcDerivedUnit_VOLUMETRICFLOWRATEUNIT, IfcDerivedUnit_ROTATIONALFREQUENCYUNIT, IfcDerivedUnit_TORQUEUNIT, IfcDerivedUnit_MOMENTOFINERTIAUNIT, IfcDerivedUnit_LINEARMOMENTUNIT, IfcDerivedUnit_LINEARFORCEUNIT, IfcDerivedUnit_PLANARFORCEUNIT, IfcDerivedUnit_MODULUSOFELASTICITYUNIT, IfcDerivedUnit_SHEARMODULUSUNIT, IfcDerivedUnit_LINEARSTIFFNESSUNIT, IfcDerivedUnit_ROTATIONALSTIFFNESSUNIT, IfcDerivedUnit_MODULUSOFSUBGRADEREACTIONUNIT, IfcDerivedUnit_ACCELERATIONUNIT, IfcDerivedUnit_CURVATUREUNIT, IfcDerivedUnit_HEATINGVALUEUNIT, IfcDerivedUnit_IONCONCENTRATIONUNIT, IfcDerivedUnit_LUMINOUSINTENSITYDISTRIBUTIONUNIT, IfcDerivedUnit_MASSPERLENGTHUNIT, IfcDerivedUnit_MODULUSOFLINEARSUBGRADEREACTIONUNIT, IfcDerivedUnit_MODULUSOFROTATIONALSUBGRADEREACTIONUNIT, IfcDerivedUnit_PHUNIT, IfcDerivedUnit_ROTATIONALMASSUNIT, IfcDerivedUnit_SECTIONAREAINTEGRALUNIT, IfcDerivedUnit_SECTIONMODULUSUNIT, IfcDerivedUnit_SOUNDPOWERUNIT, IfcDerivedUnit_SOUNDPRESSUREUNIT, IfcDerivedUnit_TEMPERATUREGRADIENTUNIT, IfcDerivedUnit_THERMALEXPANSIONCOEFFICIENTUNIT, IfcDerivedUnit_WARPINGCONSTANTUNIT, IfcDerivedUnit_WARPINGMOMENTUNIT, IfcDerivedUnit_USERDEFINED} IfcDerivedUnitEnum;
std::string ToString(IfcDerivedUnitEnum v);
IfcDerivedUnitEnum FromString(const std::string& s);}
namespace IfcDimensionExtentUsage {typedef enum {IfcDimensionExtentUsage_ORIGIN, IfcDimensionExtentUsage_TARGET} IfcDimensionExtentUsage;
std::string ToString(IfcDimensionExtentUsage v);
IfcDimensionExtentUsage FromString(const std::string& s);}
namespace IfcDirectionSenseEnum {typedef enum {IfcDirectionSense_POSITIVE, IfcDirectionSense_NEGATIVE} IfcDirectionSenseEnum;
std::string ToString(IfcDirectionSenseEnum v);
IfcDirectionSenseEnum FromString(const std::string& s);}
namespace IfcDistributionChamberElementTypeEnum {typedef enum {IfcDistributionChamberElementType_FORMEDDUCT, IfcDistributionChamberElementType_INSPECTIONCHAMBER, IfcDistributionChamberElementType_INSPECTIONPIT, IfcDistributionChamberElementType_MANHOLE, IfcDistributionChamberElementType_METERCHAMBER, IfcDistributionChamberElementType_SUMP, IfcDistributionChamberElementType_TRENCH, IfcDistributionChamberElementType_VALVECHAMBER, IfcDistributionChamberElementType_USERDEFINED, IfcDistributionChamberElementType_NOTDEFINED} IfcDistributionChamberElementTypeEnum;
std::string ToString(IfcDistributionChamberElementTypeEnum v);
IfcDistributionChamberElementTypeEnum FromString(const std::string& s);}
namespace IfcDocumentConfidentialityEnum {typedef enum {IfcDocumentConfidentiality_PUBLIC, IfcDocumentConfidentiality_RESTRICTED, IfcDocumentConfidentiality_CONFIDENTIAL, IfcDocumentConfidentiality_PERSONAL, IfcDocumentConfidentiality_USERDEFINED, IfcDocumentConfidentiality_NOTDEFINED} IfcDocumentConfidentialityEnum;
std::string ToString(IfcDocumentConfidentialityEnum v);
IfcDocumentConfidentialityEnum FromString(const std::string& s);}
namespace IfcDocumentStatusEnum {typedef enum {IfcDocumentStatus_DRAFT, IfcDocumentStatus_FINALDRAFT, IfcDocumentStatus_FINAL, IfcDocumentStatus_REVISION, IfcDocumentStatus_NOTDEFINED} IfcDocumentStatusEnum;
std::string ToString(IfcDocumentStatusEnum v);
IfcDocumentStatusEnum FromString(const std::string& s);}
namespace IfcDoorPanelOperationEnum {typedef enum {IfcDoorPanelOperation_SWINGING, IfcDoorPanelOperation_DOUBLE_ACTING, IfcDoorPanelOperation_SLIDING, IfcDoorPanelOperation_FOLDING, IfcDoorPanelOperation_REVOLVING, IfcDoorPanelOperation_ROLLINGUP, IfcDoorPanelOperation_USERDEFINED, IfcDoorPanelOperation_NOTDEFINED} IfcDoorPanelOperationEnum;
std::string ToString(IfcDoorPanelOperationEnum v);
IfcDoorPanelOperationEnum FromString(const std::string& s);}
namespace IfcDoorPanelPositionEnum {typedef enum {IfcDoorPanelPosition_LEFT, IfcDoorPanelPosition_MIDDLE, IfcDoorPanelPosition_RIGHT, IfcDoorPanelPosition_NOTDEFINED} IfcDoorPanelPositionEnum;
std::string ToString(IfcDoorPanelPositionEnum v);
IfcDoorPanelPositionEnum FromString(const std::string& s);}
namespace IfcDoorStyleConstructionEnum {typedef enum {IfcDoorStyleConstruction_ALUMINIUM, IfcDoorStyleConstruction_HIGH_GRADE_STEEL, IfcDoorStyleConstruction_STEEL, IfcDoorStyleConstruction_WOOD, IfcDoorStyleConstruction_ALUMINIUM_WOOD, IfcDoorStyleConstruction_ALUMINIUM_PLASTIC, IfcDoorStyleConstruction_PLASTIC, IfcDoorStyleConstruction_USERDEFINED, IfcDoorStyleConstruction_NOTDEFINED} IfcDoorStyleConstructionEnum;
std::string ToString(IfcDoorStyleConstructionEnum v);
IfcDoorStyleConstructionEnum FromString(const std::string& s);}
namespace IfcDoorStyleOperationEnum {typedef enum {IfcDoorStyleOperation_SINGLE_SWING_LEFT, IfcDoorStyleOperation_SINGLE_SWING_RIGHT, IfcDoorStyleOperation_DOUBLE_DOOR_SINGLE_SWING, IfcDoorStyleOperation_DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT, IfcDoorStyleOperation_DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT, IfcDoorStyleOperation_DOUBLE_SWING_LEFT, IfcDoorStyleOperation_DOUBLE_SWING_RIGHT, IfcDoorStyleOperation_DOUBLE_DOOR_DOUBLE_SWING, IfcDoorStyleOperation_SLIDING_TO_LEFT, IfcDoorStyleOperation_SLIDING_TO_RIGHT, IfcDoorStyleOperation_DOUBLE_DOOR_SLIDING, IfcDoorStyleOperation_FOLDING_TO_LEFT, IfcDoorStyleOperation_FOLDING_TO_RIGHT, IfcDoorStyleOperation_DOUBLE_DOOR_FOLDING, IfcDoorStyleOperation_REVOLVING, IfcDoorStyleOperation_ROLLINGUP, IfcDoorStyleOperation_USERDEFINED, IfcDoorStyleOperation_NOTDEFINED} IfcDoorStyleOperationEnum;
std::string ToString(IfcDoorStyleOperationEnum v);
IfcDoorStyleOperationEnum FromString(const std::string& s);}
namespace IfcDuctFittingTypeEnum {typedef enum {IfcDuctFittingType_BEND, IfcDuctFittingType_CONNECTOR, IfcDuctFittingType_ENTRY, IfcDuctFittingType_EXIT, IfcDuctFittingType_JUNCTION, IfcDuctFittingType_OBSTRUCTION, IfcDuctFittingType_TRANSITION, IfcDuctFittingType_USERDEFINED, IfcDuctFittingType_NOTDEFINED} IfcDuctFittingTypeEnum;
std::string ToString(IfcDuctFittingTypeEnum v);
IfcDuctFittingTypeEnum FromString(const std::string& s);}
namespace IfcDuctSegmentTypeEnum {typedef enum {IfcDuctSegmentType_RIGIDSEGMENT, IfcDuctSegmentType_FLEXIBLESEGMENT, IfcDuctSegmentType_USERDEFINED, IfcDuctSegmentType_NOTDEFINED} IfcDuctSegmentTypeEnum;
std::string ToString(IfcDuctSegmentTypeEnum v);
IfcDuctSegmentTypeEnum FromString(const std::string& s);}
namespace IfcDuctSilencerTypeEnum {typedef enum {IfcDuctSilencerType_FLATOVAL, IfcDuctSilencerType_RECTANGULAR, IfcDuctSilencerType_ROUND, IfcDuctSilencerType_USERDEFINED, IfcDuctSilencerType_NOTDEFINED} IfcDuctSilencerTypeEnum;
std::string ToString(IfcDuctSilencerTypeEnum v);
IfcDuctSilencerTypeEnum FromString(const std::string& s);}
namespace IfcElectricApplianceTypeEnum {typedef enum {IfcElectricApplianceType_COMPUTER, IfcElectricApplianceType_DIRECTWATERHEATER, IfcElectricApplianceType_DISHWASHER, IfcElectricApplianceType_ELECTRICCOOKER, IfcElectricApplianceType_ELECTRICHEATER, IfcElectricApplianceType_FACSIMILE, IfcElectricApplianceType_FREESTANDINGFAN, IfcElectricApplianceType_FREEZER, IfcElectricApplianceType_FRIDGE_FREEZER, IfcElectricApplianceType_HANDDRYER, IfcElectricApplianceType_INDIRECTWATERHEATER, IfcElectricApplianceType_MICROWAVE, IfcElectricApplianceType_PHOTOCOPIER, IfcElectricApplianceType_PRINTER, IfcElectricApplianceType_REFRIGERATOR, IfcElectricApplianceType_RADIANTHEATER, IfcElectricApplianceType_SCANNER, IfcElectricApplianceType_TELEPHONE, IfcElectricApplianceType_TUMBLEDRYER, IfcElectricApplianceType_TV, IfcElectricApplianceType_VENDINGMACHINE, IfcElectricApplianceType_WASHINGMACHINE, IfcElectricApplianceType_WATERHEATER, IfcElectricApplianceType_WATERCOOLER, IfcElectricApplianceType_USERDEFINED, IfcElectricApplianceType_NOTDEFINED} IfcElectricApplianceTypeEnum;
std::string ToString(IfcElectricApplianceTypeEnum v);
IfcElectricApplianceTypeEnum FromString(const std::string& s);}
namespace IfcElectricCurrentEnum {typedef enum {IfcElectricCurrent_ALTERNATING, IfcElectricCurrent_DIRECT, IfcElectricCurrent_NOTDEFINED} IfcElectricCurrentEnum;
std::string ToString(IfcElectricCurrentEnum v);
IfcElectricCurrentEnum FromString(const std::string& s);}
namespace IfcElectricDistributionPointFunctionEnum {typedef enum {IfcElectricDistributionPointFunction_ALARMPANEL, IfcElectricDistributionPointFunction_CONSUMERUNIT, IfcElectricDistributionPointFunction_CONTROLPANEL, IfcElectricDistributionPointFunction_DISTRIBUTIONBOARD, IfcElectricDistributionPointFunction_GASDETECTORPANEL, IfcElectricDistributionPointFunction_INDICATORPANEL, IfcElectricDistributionPointFunction_MIMICPANEL, IfcElectricDistributionPointFunction_MOTORCONTROLCENTRE, IfcElectricDistributionPointFunction_SWITCHBOARD, IfcElectricDistributionPointFunction_USERDEFINED, IfcElectricDistributionPointFunction_NOTDEFINED} IfcElectricDistributionPointFunctionEnum;
std::string ToString(IfcElectricDistributionPointFunctionEnum v);
IfcElectricDistributionPointFunctionEnum FromString(const std::string& s);}
namespace IfcElectricFlowStorageDeviceTypeEnum {typedef enum {IfcElectricFlowStorageDeviceType_BATTERY, IfcElectricFlowStorageDeviceType_CAPACITORBANK, IfcElectricFlowStorageDeviceType_HARMONICFILTER, IfcElectricFlowStorageDeviceType_INDUCTORBANK, IfcElectricFlowStorageDeviceType_UPS, IfcElectricFlowStorageDeviceType_USERDEFINED, IfcElectricFlowStorageDeviceType_NOTDEFINED} IfcElectricFlowStorageDeviceTypeEnum;
std::string ToString(IfcElectricFlowStorageDeviceTypeEnum v);
IfcElectricFlowStorageDeviceTypeEnum FromString(const std::string& s);}
namespace IfcElectricGeneratorTypeEnum {typedef enum {IfcElectricGeneratorType_USERDEFINED, IfcElectricGeneratorType_NOTDEFINED} IfcElectricGeneratorTypeEnum;
std::string ToString(IfcElectricGeneratorTypeEnum v);
IfcElectricGeneratorTypeEnum FromString(const std::string& s);}
namespace IfcElectricHeaterTypeEnum {typedef enum {IfcElectricHeaterType_ELECTRICPOINTHEATER, IfcElectricHeaterType_ELECTRICCABLEHEATER, IfcElectricHeaterType_ELECTRICMATHEATER, IfcElectricHeaterType_USERDEFINED, IfcElectricHeaterType_NOTDEFINED} IfcElectricHeaterTypeEnum;
std::string ToString(IfcElectricHeaterTypeEnum v);
IfcElectricHeaterTypeEnum FromString(const std::string& s);}
namespace IfcElectricMotorTypeEnum {typedef enum {IfcElectricMotorType_DC, IfcElectricMotorType_INDUCTION, IfcElectricMotorType_POLYPHASE, IfcElectricMotorType_RELUCTANCESYNCHRONOUS, IfcElectricMotorType_SYNCHRONOUS, IfcElectricMotorType_USERDEFINED, IfcElectricMotorType_NOTDEFINED} IfcElectricMotorTypeEnum;
std::string ToString(IfcElectricMotorTypeEnum v);
IfcElectricMotorTypeEnum FromString(const std::string& s);}
namespace IfcElectricTimeControlTypeEnum {typedef enum {IfcElectricTimeControlType_TIMECLOCK, IfcElectricTimeControlType_TIMEDELAY, IfcElectricTimeControlType_RELAY, IfcElectricTimeControlType_USERDEFINED, IfcElectricTimeControlType_NOTDEFINED} IfcElectricTimeControlTypeEnum;
std::string ToString(IfcElectricTimeControlTypeEnum v);
IfcElectricTimeControlTypeEnum FromString(const std::string& s);}
namespace IfcElementAssemblyTypeEnum {typedef enum {IfcElementAssemblyType_ACCESSORY_ASSEMBLY, IfcElementAssemblyType_ARCH, IfcElementAssemblyType_BEAM_GRID, IfcElementAssemblyType_BRACED_FRAME, IfcElementAssemblyType_GIRDER, IfcElementAssemblyType_REINFORCEMENT_UNIT, IfcElementAssemblyType_RIGID_FRAME, IfcElementAssemblyType_SLAB_FIELD, IfcElementAssemblyType_TRUSS, IfcElementAssemblyType_USERDEFINED, IfcElementAssemblyType_NOTDEFINED} IfcElementAssemblyTypeEnum;
std::string ToString(IfcElementAssemblyTypeEnum v);
IfcElementAssemblyTypeEnum FromString(const std::string& s);}
namespace IfcElementCompositionEnum {typedef enum {IfcElementComposition_COMPLEX, IfcElementComposition_ELEMENT, IfcElementComposition_PARTIAL} IfcElementCompositionEnum;
std::string ToString(IfcElementCompositionEnum v);
IfcElementCompositionEnum FromString(const std::string& s);}
namespace IfcEnergySequenceEnum {typedef enum {IfcEnergySequence_PRIMARY, IfcEnergySequence_SECONDARY, IfcEnergySequence_TERTIARY, IfcEnergySequence_AUXILIARY, IfcEnergySequence_USERDEFINED, IfcEnergySequence_NOTDEFINED} IfcEnergySequenceEnum;
std::string ToString(IfcEnergySequenceEnum v);
IfcEnergySequenceEnum FromString(const std::string& s);}
namespace IfcEnvironmentalImpactCategoryEnum {typedef enum {IfcEnvironmentalImpactCategory_COMBINEDVALUE, IfcEnvironmentalImpactCategory_DISPOSAL, IfcEnvironmentalImpactCategory_EXTRACTION, IfcEnvironmentalImpactCategory_INSTALLATION, IfcEnvironmentalImpactCategory_MANUFACTURE, IfcEnvironmentalImpactCategory_TRANSPORTATION, IfcEnvironmentalImpactCategory_USERDEFINED, IfcEnvironmentalImpactCategory_NOTDEFINED} IfcEnvironmentalImpactCategoryEnum;
std::string ToString(IfcEnvironmentalImpactCategoryEnum v);
IfcEnvironmentalImpactCategoryEnum FromString(const std::string& s);}
namespace IfcEvaporativeCoolerTypeEnum {typedef enum {IfcEvaporativeCoolerType_DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER, IfcEvaporativeCoolerType_DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER, IfcEvaporativeCoolerType_DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER, IfcEvaporativeCoolerType_DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER, IfcEvaporativeCoolerType_DIRECTEVAPORATIVEAIRWASHER, IfcEvaporativeCoolerType_INDIRECTEVAPORATIVEPACKAGEAIRCOOLER, IfcEvaporativeCoolerType_INDIRECTEVAPORATIVEWETCOIL, IfcEvaporativeCoolerType_INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER, IfcEvaporativeCoolerType_INDIRECTDIRECTCOMBINATION, IfcEvaporativeCoolerType_USERDEFINED, IfcEvaporativeCoolerType_NOTDEFINED} IfcEvaporativeCoolerTypeEnum;
std::string ToString(IfcEvaporativeCoolerTypeEnum v);
IfcEvaporativeCoolerTypeEnum FromString(const std::string& s);}
namespace IfcEvaporatorTypeEnum {typedef enum {IfcEvaporatorType_DIRECTEXPANSIONSHELLANDTUBE, IfcEvaporatorType_DIRECTEXPANSIONTUBEINTUBE, IfcEvaporatorType_DIRECTEXPANSIONBRAZEDPLATE, IfcEvaporatorType_FLOODEDSHELLANDTUBE, IfcEvaporatorType_SHELLANDCOIL, IfcEvaporatorType_USERDEFINED, IfcEvaporatorType_NOTDEFINED} IfcEvaporatorTypeEnum;
std::string ToString(IfcEvaporatorTypeEnum v);
IfcEvaporatorTypeEnum FromString(const std::string& s);}
namespace IfcFanTypeEnum {typedef enum {IfcFanType_CENTRIFUGALFORWARDCURVED, IfcFanType_CENTRIFUGALRADIAL, IfcFanType_CENTRIFUGALBACKWARDINCLINEDCURVED, IfcFanType_CENTRIFUGALAIRFOIL, IfcFanType_TUBEAXIAL, IfcFanType_VANEAXIAL, IfcFanType_PROPELLORAXIAL, IfcFanType_USERDEFINED, IfcFanType_NOTDEFINED} IfcFanTypeEnum;
std::string ToString(IfcFanTypeEnum v);
IfcFanTypeEnum FromString(const std::string& s);}
namespace IfcFilterTypeEnum {typedef enum {IfcFilterType_AIRPARTICLEFILTER, IfcFilterType_ODORFILTER, IfcFilterType_OILFILTER, IfcFilterType_STRAINER, IfcFilterType_WATERFILTER, IfcFilterType_USERDEFINED, IfcFilterType_NOTDEFINED} IfcFilterTypeEnum;
std::string ToString(IfcFilterTypeEnum v);
IfcFilterTypeEnum FromString(const std::string& s);}
namespace IfcFireSuppressionTerminalTypeEnum {typedef enum {IfcFireSuppressionTerminalType_BREECHINGINLET, IfcFireSuppressionTerminalType_FIREHYDRANT, IfcFireSuppressionTerminalType_HOSEREEL, IfcFireSuppressionTerminalType_SPRINKLER, IfcFireSuppressionTerminalType_SPRINKLERDEFLECTOR, IfcFireSuppressionTerminalType_USERDEFINED, IfcFireSuppressionTerminalType_NOTDEFINED} IfcFireSuppressionTerminalTypeEnum;
std::string ToString(IfcFireSuppressionTerminalTypeEnum v);
IfcFireSuppressionTerminalTypeEnum FromString(const std::string& s);}
namespace IfcFlowDirectionEnum {typedef enum {IfcFlowDirection_SOURCE, IfcFlowDirection_SINK, IfcFlowDirection_SOURCEANDSINK, IfcFlowDirection_NOTDEFINED} IfcFlowDirectionEnum;
std::string ToString(IfcFlowDirectionEnum v);
IfcFlowDirectionEnum FromString(const std::string& s);}
namespace IfcFlowInstrumentTypeEnum {typedef enum {IfcFlowInstrumentType_PRESSUREGAUGE, IfcFlowInstrumentType_THERMOMETER, IfcFlowInstrumentType_AMMETER, IfcFlowInstrumentType_FREQUENCYMETER, IfcFlowInstrumentType_POWERFACTORMETER, IfcFlowInstrumentType_PHASEANGLEMETER, IfcFlowInstrumentType_VOLTMETER_PEAK, IfcFlowInstrumentType_VOLTMETER_RMS, IfcFlowInstrumentType_USERDEFINED, IfcFlowInstrumentType_NOTDEFINED} IfcFlowInstrumentTypeEnum;
std::string ToString(IfcFlowInstrumentTypeEnum v);
IfcFlowInstrumentTypeEnum FromString(const std::string& s);}
namespace IfcFlowMeterTypeEnum {typedef enum {IfcFlowMeterType_ELECTRICMETER, IfcFlowMeterType_ENERGYMETER, IfcFlowMeterType_FLOWMETER, IfcFlowMeterType_GASMETER, IfcFlowMeterType_OILMETER, IfcFlowMeterType_WATERMETER, IfcFlowMeterType_USERDEFINED, IfcFlowMeterType_NOTDEFINED} IfcFlowMeterTypeEnum;
std::string ToString(IfcFlowMeterTypeEnum v);
IfcFlowMeterTypeEnum FromString(const std::string& s);}
namespace IfcFootingTypeEnum {typedef enum {IfcFootingType_FOOTING_BEAM, IfcFootingType_PAD_FOOTING, IfcFootingType_PILE_CAP, IfcFootingType_STRIP_FOOTING, IfcFootingType_USERDEFINED, IfcFootingType_NOTDEFINED} IfcFootingTypeEnum;
std::string ToString(IfcFootingTypeEnum v);
IfcFootingTypeEnum FromString(const std::string& s);}
namespace IfcGasTerminalTypeEnum {typedef enum {IfcGasTerminalType_GASAPPLIANCE, IfcGasTerminalType_GASBOOSTER, IfcGasTerminalType_GASBURNER, IfcGasTerminalType_USERDEFINED, IfcGasTerminalType_NOTDEFINED} IfcGasTerminalTypeEnum;
std::string ToString(IfcGasTerminalTypeEnum v);
IfcGasTerminalTypeEnum FromString(const std::string& s);}
namespace IfcGeometricProjectionEnum {typedef enum {IfcGeometricProjection_GRAPH_VIEW, IfcGeometricProjection_SKETCH_VIEW, IfcGeometricProjection_MODEL_VIEW, IfcGeometricProjection_PLAN_VIEW, IfcGeometricProjection_REFLECTED_PLAN_VIEW, IfcGeometricProjection_SECTION_VIEW, IfcGeometricProjection_ELEVATION_VIEW, IfcGeometricProjection_USERDEFINED, IfcGeometricProjection_NOTDEFINED} IfcGeometricProjectionEnum;
std::string ToString(IfcGeometricProjectionEnum v);
IfcGeometricProjectionEnum FromString(const std::string& s);}
namespace IfcGlobalOrLocalEnum {typedef enum {IfcGlobalOrLocal_GLOBAL_COORDS, IfcGlobalOrLocal_LOCAL_COORDS} IfcGlobalOrLocalEnum;
std::string ToString(IfcGlobalOrLocalEnum v);
IfcGlobalOrLocalEnum FromString(const std::string& s);}
namespace IfcHeatExchangerTypeEnum {typedef enum {IfcHeatExchangerType_PLATE, IfcHeatExchangerType_SHELLANDTUBE, IfcHeatExchangerType_USERDEFINED, IfcHeatExchangerType_NOTDEFINED} IfcHeatExchangerTypeEnum;
std::string ToString(IfcHeatExchangerTypeEnum v);
IfcHeatExchangerTypeEnum FromString(const std::string& s);}
namespace IfcHumidifierTypeEnum {typedef enum {IfcHumidifierType_STEAMINJECTION, IfcHumidifierType_ADIABATICAIRWASHER, IfcHumidifierType_ADIABATICPAN, IfcHumidifierType_ADIABATICWETTEDELEMENT, IfcHumidifierType_ADIABATICATOMIZING, IfcHumidifierType_ADIABATICULTRASONIC, IfcHumidifierType_ADIABATICRIGIDMEDIA, IfcHumidifierType_ADIABATICCOMPRESSEDAIRNOZZLE, IfcHumidifierType_ASSISTEDELECTRIC, IfcHumidifierType_ASSISTEDNATURALGAS, IfcHumidifierType_ASSISTEDPROPANE, IfcHumidifierType_ASSISTEDBUTANE, IfcHumidifierType_ASSISTEDSTEAM, IfcHumidifierType_USERDEFINED, IfcHumidifierType_NOTDEFINED} IfcHumidifierTypeEnum;
std::string ToString(IfcHumidifierTypeEnum v);
IfcHumidifierTypeEnum FromString(const std::string& s);}
namespace IfcInternalOrExternalEnum {typedef enum {IfcInternalOrExternal_INTERNAL, IfcInternalOrExternal_EXTERNAL, IfcInternalOrExternal_NOTDEFINED} IfcInternalOrExternalEnum;
std::string ToString(IfcInternalOrExternalEnum v);
IfcInternalOrExternalEnum FromString(const std::string& s);}
namespace IfcInventoryTypeEnum {typedef enum {IfcInventoryType_ASSETINVENTORY, IfcInventoryType_SPACEINVENTORY, IfcInventoryType_FURNITUREINVENTORY, IfcInventoryType_USERDEFINED, IfcInventoryType_NOTDEFINED} IfcInventoryTypeEnum;
std::string ToString(IfcInventoryTypeEnum v);
IfcInventoryTypeEnum FromString(const std::string& s);}
namespace IfcJunctionBoxTypeEnum {typedef enum {IfcJunctionBoxType_USERDEFINED, IfcJunctionBoxType_NOTDEFINED} IfcJunctionBoxTypeEnum;
std::string ToString(IfcJunctionBoxTypeEnum v);
IfcJunctionBoxTypeEnum FromString(const std::string& s);}
namespace IfcLampTypeEnum {typedef enum {IfcLampType_COMPACTFLUORESCENT, IfcLampType_FLUORESCENT, IfcLampType_HIGHPRESSUREMERCURY, IfcLampType_HIGHPRESSURESODIUM, IfcLampType_METALHALIDE, IfcLampType_TUNGSTENFILAMENT, IfcLampType_USERDEFINED, IfcLampType_NOTDEFINED} IfcLampTypeEnum;
std::string ToString(IfcLampTypeEnum v);
IfcLampTypeEnum FromString(const std::string& s);}
namespace IfcLayerSetDirectionEnum {typedef enum {IfcLayerSetDirection_AXIS1, IfcLayerSetDirection_AXIS2, IfcLayerSetDirection_AXIS3} IfcLayerSetDirectionEnum;
std::string ToString(IfcLayerSetDirectionEnum v);
IfcLayerSetDirectionEnum FromString(const std::string& s);}
namespace IfcLightDistributionCurveEnum {typedef enum {IfcLightDistributionCurve_TYPE_A, IfcLightDistributionCurve_TYPE_B, IfcLightDistributionCurve_TYPE_C, IfcLightDistributionCurve_NOTDEFINED} IfcLightDistributionCurveEnum;
std::string ToString(IfcLightDistributionCurveEnum v);
IfcLightDistributionCurveEnum FromString(const std::string& s);}
namespace IfcLightEmissionSourceEnum {typedef enum {IfcLightEmissionSource_COMPACTFLUORESCENT, IfcLightEmissionSource_FLUORESCENT, IfcLightEmissionSource_HIGHPRESSUREMERCURY, IfcLightEmissionSource_HIGHPRESSURESODIUM, IfcLightEmissionSource_LIGHTEMITTINGDIODE, IfcLightEmissionSource_LOWPRESSURESODIUM, IfcLightEmissionSource_LOWVOLTAGEHALOGEN, IfcLightEmissionSource_MAINVOLTAGEHALOGEN, IfcLightEmissionSource_METALHALIDE, IfcLightEmissionSource_TUNGSTENFILAMENT, IfcLightEmissionSource_NOTDEFINED} IfcLightEmissionSourceEnum;
std::string ToString(IfcLightEmissionSourceEnum v);
IfcLightEmissionSourceEnum FromString(const std::string& s);}
namespace IfcLightFixtureTypeEnum {typedef enum {IfcLightFixtureType_POINTSOURCE, IfcLightFixtureType_DIRECTIONSOURCE, IfcLightFixtureType_USERDEFINED, IfcLightFixtureType_NOTDEFINED} IfcLightFixtureTypeEnum;
std::string ToString(IfcLightFixtureTypeEnum v);
IfcLightFixtureTypeEnum FromString(const std::string& s);}
namespace IfcLoadGroupTypeEnum {typedef enum {IfcLoadGroupType_LOAD_GROUP, IfcLoadGroupType_LOAD_CASE, IfcLoadGroupType_LOAD_COMBINATION_GROUP, IfcLoadGroupType_LOAD_COMBINATION, IfcLoadGroupType_USERDEFINED, IfcLoadGroupType_NOTDEFINED} IfcLoadGroupTypeEnum;
std::string ToString(IfcLoadGroupTypeEnum v);
IfcLoadGroupTypeEnum FromString(const std::string& s);}
namespace IfcLogicalOperatorEnum {typedef enum {IfcLogicalOperator_LOGICALAND, IfcLogicalOperator_LOGICALOR} IfcLogicalOperatorEnum;
std::string ToString(IfcLogicalOperatorEnum v);
IfcLogicalOperatorEnum FromString(const std::string& s);}
namespace IfcMemberTypeEnum {typedef enum {IfcMemberType_BRACE, IfcMemberType_CHORD, IfcMemberType_COLLAR, IfcMemberType_MEMBER, IfcMemberType_MULLION, IfcMemberType_PLATE, IfcMemberType_POST, IfcMemberType_PURLIN, IfcMemberType_RAFTER, IfcMemberType_STRINGER, IfcMemberType_STRUT, IfcMemberType_STUD, IfcMemberType_USERDEFINED, IfcMemberType_NOTDEFINED} IfcMemberTypeEnum;
std::string ToString(IfcMemberTypeEnum v);
IfcMemberTypeEnum FromString(const std::string& s);}
namespace IfcMotorConnectionTypeEnum {typedef enum {IfcMotorConnectionType_BELTDRIVE, IfcMotorConnectionType_COUPLING, IfcMotorConnectionType_DIRECTDRIVE, IfcMotorConnectionType_USERDEFINED, IfcMotorConnectionType_NOTDEFINED} IfcMotorConnectionTypeEnum;
std::string ToString(IfcMotorConnectionTypeEnum v);
IfcMotorConnectionTypeEnum FromString(const std::string& s);}
namespace IfcNullStyle {typedef enum {IfcNullStyle_NULL} IfcNullStyle;
std::string ToString(IfcNullStyle v);
IfcNullStyle FromString(const std::string& s);}
namespace IfcObjectTypeEnum {typedef enum {IfcObjectType_PRODUCT, IfcObjectType_PROCESS, IfcObjectType_CONTROL, IfcObjectType_RESOURCE, IfcObjectType_ACTOR, IfcObjectType_GROUP, IfcObjectType_PROJECT, IfcObjectType_NOTDEFINED} IfcObjectTypeEnum;
std::string ToString(IfcObjectTypeEnum v);
IfcObjectTypeEnum FromString(const std::string& s);}
namespace IfcObjectiveEnum {typedef enum {IfcObjective_CODECOMPLIANCE, IfcObjective_DESIGNINTENT, IfcObjective_HEALTHANDSAFETY, IfcObjective_REQUIREMENT, IfcObjective_SPECIFICATION, IfcObjective_TRIGGERCONDITION, IfcObjective_USERDEFINED, IfcObjective_NOTDEFINED} IfcObjectiveEnum;
std::string ToString(IfcObjectiveEnum v);
IfcObjectiveEnum FromString(const std::string& s);}
namespace IfcOccupantTypeEnum {typedef enum {IfcOccupantType_ASSIGNEE, IfcOccupantType_ASSIGNOR, IfcOccupantType_LESSEE, IfcOccupantType_LESSOR, IfcOccupantType_LETTINGAGENT, IfcOccupantType_OWNER, IfcOccupantType_TENANT, IfcOccupantType_USERDEFINED, IfcOccupantType_NOTDEFINED} IfcOccupantTypeEnum;
std::string ToString(IfcOccupantTypeEnum v);
IfcOccupantTypeEnum FromString(const std::string& s);}
namespace IfcOutletTypeEnum {typedef enum {IfcOutletType_AUDIOVISUALOUTLET, IfcOutletType_COMMUNICATIONSOUTLET, IfcOutletType_POWEROUTLET, IfcOutletType_USERDEFINED, IfcOutletType_NOTDEFINED} IfcOutletTypeEnum;
std::string ToString(IfcOutletTypeEnum v);
IfcOutletTypeEnum FromString(const std::string& s);}
namespace IfcPermeableCoveringOperationEnum {typedef enum {IfcPermeableCoveringOperation_GRILL, IfcPermeableCoveringOperation_LOUVER, IfcPermeableCoveringOperation_SCREEN, IfcPermeableCoveringOperation_USERDEFINED, IfcPermeableCoveringOperation_NOTDEFINED} IfcPermeableCoveringOperationEnum;
std::string ToString(IfcPermeableCoveringOperationEnum v);
IfcPermeableCoveringOperationEnum FromString(const std::string& s);}
namespace IfcPhysicalOrVirtualEnum {typedef enum {IfcPhysicalOrVirtual_PHYSICAL, IfcPhysicalOrVirtual_VIRTUAL, IfcPhysicalOrVirtual_NOTDEFINED} IfcPhysicalOrVirtualEnum;
std::string ToString(IfcPhysicalOrVirtualEnum v);
IfcPhysicalOrVirtualEnum FromString(const std::string& s);}
namespace IfcPileConstructionEnum {typedef enum {IfcPileConstruction_CAST_IN_PLACE, IfcPileConstruction_COMPOSITE, IfcPileConstruction_PRECAST_CONCRETE, IfcPileConstruction_PREFAB_STEEL, IfcPileConstruction_USERDEFINED, IfcPileConstruction_NOTDEFINED} IfcPileConstructionEnum;
std::string ToString(IfcPileConstructionEnum v);
IfcPileConstructionEnum FromString(const std::string& s);}
namespace IfcPileTypeEnum {typedef enum {IfcPileType_COHESION, IfcPileType_FRICTION, IfcPileType_SUPPORT, IfcPileType_USERDEFINED, IfcPileType_NOTDEFINED} IfcPileTypeEnum;
std::string ToString(IfcPileTypeEnum v);
IfcPileTypeEnum FromString(const std::string& s);}
namespace IfcPipeFittingTypeEnum {typedef enum {IfcPipeFittingType_BEND, IfcPipeFittingType_CONNECTOR, IfcPipeFittingType_ENTRY, IfcPipeFittingType_EXIT, IfcPipeFittingType_JUNCTION, IfcPipeFittingType_OBSTRUCTION, IfcPipeFittingType_TRANSITION, IfcPipeFittingType_USERDEFINED, IfcPipeFittingType_NOTDEFINED} IfcPipeFittingTypeEnum;
std::string ToString(IfcPipeFittingTypeEnum v);
IfcPipeFittingTypeEnum FromString(const std::string& s);}
namespace IfcPipeSegmentTypeEnum {typedef enum {IfcPipeSegmentType_FLEXIBLESEGMENT, IfcPipeSegmentType_RIGIDSEGMENT, IfcPipeSegmentType_GUTTER, IfcPipeSegmentType_SPOOL, IfcPipeSegmentType_USERDEFINED, IfcPipeSegmentType_NOTDEFINED} IfcPipeSegmentTypeEnum;
std::string ToString(IfcPipeSegmentTypeEnum v);
IfcPipeSegmentTypeEnum FromString(const std::string& s);}
namespace IfcPlateTypeEnum {typedef enum {IfcPlateType_CURTAIN_PANEL, IfcPlateType_SHEET, IfcPlateType_USERDEFINED, IfcPlateType_NOTDEFINED} IfcPlateTypeEnum;
std::string ToString(IfcPlateTypeEnum v);
IfcPlateTypeEnum FromString(const std::string& s);}
namespace IfcProcedureTypeEnum {typedef enum {IfcProcedureType_ADVICE_CAUTION, IfcProcedureType_ADVICE_NOTE, IfcProcedureType_ADVICE_WARNING, IfcProcedureType_CALIBRATION, IfcProcedureType_DIAGNOSTIC, IfcProcedureType_SHUTDOWN, IfcProcedureType_STARTUP, IfcProcedureType_USERDEFINED, IfcProcedureType_NOTDEFINED} IfcProcedureTypeEnum;
std::string ToString(IfcProcedureTypeEnum v);
IfcProcedureTypeEnum FromString(const std::string& s);}
namespace IfcProfileTypeEnum {typedef enum {IfcProfileType_CURVE, IfcProfileType_AREA} IfcProfileTypeEnum;
std::string ToString(IfcProfileTypeEnum v);
IfcProfileTypeEnum FromString(const std::string& s);}
namespace IfcProjectOrderRecordTypeEnum {typedef enum {IfcProjectOrderRecordType_CHANGE, IfcProjectOrderRecordType_MAINTENANCE, IfcProjectOrderRecordType_MOVE, IfcProjectOrderRecordType_PURCHASE, IfcProjectOrderRecordType_WORK, IfcProjectOrderRecordType_USERDEFINED, IfcProjectOrderRecordType_NOTDEFINED} IfcProjectOrderRecordTypeEnum;
std::string ToString(IfcProjectOrderRecordTypeEnum v);
IfcProjectOrderRecordTypeEnum FromString(const std::string& s);}
namespace IfcProjectOrderTypeEnum {typedef enum {IfcProjectOrderType_CHANGEORDER, IfcProjectOrderType_MAINTENANCEWORKORDER, IfcProjectOrderType_MOVEORDER, IfcProjectOrderType_PURCHASEORDER, IfcProjectOrderType_WORKORDER, IfcProjectOrderType_USERDEFINED, IfcProjectOrderType_NOTDEFINED} IfcProjectOrderTypeEnum;
std::string ToString(IfcProjectOrderTypeEnum v);
IfcProjectOrderTypeEnum FromString(const std::string& s);}
namespace IfcProjectedOrTrueLengthEnum {typedef enum {IfcProjectedOrTrueLength_PROJECTED_LENGTH, IfcProjectedOrTrueLength_TRUE_LENGTH} IfcProjectedOrTrueLengthEnum;
std::string ToString(IfcProjectedOrTrueLengthEnum v);
IfcProjectedOrTrueLengthEnum FromString(const std::string& s);}
namespace IfcPropertySourceEnum {typedef enum {IfcPropertySource_DESIGN, IfcPropertySource_DESIGNMAXIMUM, IfcPropertySource_DESIGNMINIMUM, IfcPropertySource_SIMULATED, IfcPropertySource_ASBUILT, IfcPropertySource_COMMISSIONING, IfcPropertySource_MEASURED, IfcPropertySource_USERDEFINED, IfcPropertySource_NOTKNOWN} IfcPropertySourceEnum;
std::string ToString(IfcPropertySourceEnum v);
IfcPropertySourceEnum FromString(const std::string& s);}
namespace IfcProtectiveDeviceTypeEnum {typedef enum {IfcProtectiveDeviceType_FUSEDISCONNECTOR, IfcProtectiveDeviceType_CIRCUITBREAKER, IfcProtectiveDeviceType_EARTHFAILUREDEVICE, IfcProtectiveDeviceType_RESIDUALCURRENTCIRCUITBREAKER, IfcProtectiveDeviceType_RESIDUALCURRENTSWITCH, IfcProtectiveDeviceType_VARISTOR, IfcProtectiveDeviceType_USERDEFINED, IfcProtectiveDeviceType_NOTDEFINED} IfcProtectiveDeviceTypeEnum;
std::string ToString(IfcProtectiveDeviceTypeEnum v);
IfcProtectiveDeviceTypeEnum FromString(const std::string& s);}
namespace IfcPumpTypeEnum {typedef enum {IfcPumpType_CIRCULATOR, IfcPumpType_ENDSUCTION, IfcPumpType_SPLITCASE, IfcPumpType_VERTICALINLINE, IfcPumpType_VERTICALTURBINE, IfcPumpType_USERDEFINED, IfcPumpType_NOTDEFINED} IfcPumpTypeEnum;
std::string ToString(IfcPumpTypeEnum v);
IfcPumpTypeEnum FromString(const std::string& s);}
namespace IfcRailingTypeEnum {typedef enum {IfcRailingType_HANDRAIL, IfcRailingType_GUARDRAIL, IfcRailingType_BALUSTRADE, IfcRailingType_USERDEFINED, IfcRailingType_NOTDEFINED} IfcRailingTypeEnum;
std::string ToString(IfcRailingTypeEnum v);
IfcRailingTypeEnum FromString(const std::string& s);}
namespace IfcRampFlightTypeEnum {typedef enum {IfcRampFlightType_STRAIGHT, IfcRampFlightType_SPIRAL, IfcRampFlightType_USERDEFINED, IfcRampFlightType_NOTDEFINED} IfcRampFlightTypeEnum;
std::string ToString(IfcRampFlightTypeEnum v);
IfcRampFlightTypeEnum FromString(const std::string& s);}
namespace IfcRampTypeEnum {typedef enum {IfcRampType_STRAIGHT_RUN_RAMP, IfcRampType_TWO_STRAIGHT_RUN_RAMP, IfcRampType_QUARTER_TURN_RAMP, IfcRampType_TWO_QUARTER_TURN_RAMP, IfcRampType_HALF_TURN_RAMP, IfcRampType_SPIRAL_RAMP, IfcRampType_USERDEFINED, IfcRampType_NOTDEFINED} IfcRampTypeEnum;
std::string ToString(IfcRampTypeEnum v);
IfcRampTypeEnum FromString(const std::string& s);}
namespace IfcReflectanceMethodEnum {typedef enum {IfcReflectanceMethod_BLINN, IfcReflectanceMethod_FLAT, IfcReflectanceMethod_GLASS, IfcReflectanceMethod_MATT, IfcReflectanceMethod_METAL, IfcReflectanceMethod_MIRROR, IfcReflectanceMethod_PHONG, IfcReflectanceMethod_PLASTIC, IfcReflectanceMethod_STRAUSS, IfcReflectanceMethod_NOTDEFINED} IfcReflectanceMethodEnum;
std::string ToString(IfcReflectanceMethodEnum v);
IfcReflectanceMethodEnum FromString(const std::string& s);}
namespace IfcReinforcingBarRoleEnum {typedef enum {IfcReinforcingBarRole_MAIN, IfcReinforcingBarRole_SHEAR, IfcReinforcingBarRole_LIGATURE, IfcReinforcingBarRole_STUD, IfcReinforcingBarRole_PUNCHING, IfcReinforcingBarRole_EDGE, IfcReinforcingBarRole_RING, IfcReinforcingBarRole_USERDEFINED, IfcReinforcingBarRole_NOTDEFINED} IfcReinforcingBarRoleEnum;
std::string ToString(IfcReinforcingBarRoleEnum v);
IfcReinforcingBarRoleEnum FromString(const std::string& s);}
namespace IfcReinforcingBarSurfaceEnum {typedef enum {IfcReinforcingBarSurface_PLAIN, IfcReinforcingBarSurface_TEXTURED} IfcReinforcingBarSurfaceEnum;
std::string ToString(IfcReinforcingBarSurfaceEnum v);
IfcReinforcingBarSurfaceEnum FromString(const std::string& s);}
namespace IfcResourceConsumptionEnum {typedef enum {IfcResourceConsumption_CONSUMED, IfcResourceConsumption_PARTIALLYCONSUMED, IfcResourceConsumption_NOTCONSUMED, IfcResourceConsumption_OCCUPIED, IfcResourceConsumption_PARTIALLYOCCUPIED, IfcResourceConsumption_NOTOCCUPIED, IfcResourceConsumption_USERDEFINED, IfcResourceConsumption_NOTDEFINED} IfcResourceConsumptionEnum;
std::string ToString(IfcResourceConsumptionEnum v);
IfcResourceConsumptionEnum FromString(const std::string& s);}
namespace IfcRibPlateDirectionEnum {typedef enum {IfcRibPlateDirection_DIRECTION_X, IfcRibPlateDirection_DIRECTION_Y} IfcRibPlateDirectionEnum;
std::string ToString(IfcRibPlateDirectionEnum v);
IfcRibPlateDirectionEnum FromString(const std::string& s);}
namespace IfcRoleEnum {typedef enum {IfcRole_SUPPLIER, IfcRole_MANUFACTURER, IfcRole_CONTRACTOR, IfcRole_SUBCONTRACTOR, IfcRole_ARCHITECT, IfcRole_STRUCTURALENGINEER, IfcRole_COSTENGINEER, IfcRole_CLIENT, IfcRole_BUILDINGOWNER, IfcRole_BUILDINGOPERATOR, IfcRole_MECHANICALENGINEER, IfcRole_ELECTRICALENGINEER, IfcRole_PROJECTMANAGER, IfcRole_FACILITIESMANAGER, IfcRole_CIVILENGINEER, IfcRole_COMISSIONINGENGINEER, IfcRole_ENGINEER, IfcRole_OWNER, IfcRole_CONSULTANT, IfcRole_CONSTRUCTIONMANAGER, IfcRole_FIELDCONSTRUCTIONMANAGER, IfcRole_RESELLER, IfcRole_USERDEFINED} IfcRoleEnum;
std::string ToString(IfcRoleEnum v);
IfcRoleEnum FromString(const std::string& s);}
namespace IfcRoofTypeEnum {typedef enum {IfcRoofType_FLAT_ROOF, IfcRoofType_SHED_ROOF, IfcRoofType_GABLE_ROOF, IfcRoofType_HIP_ROOF, IfcRoofType_HIPPED_GABLE_ROOF, IfcRoofType_GAMBREL_ROOF, IfcRoofType_MANSARD_ROOF, IfcRoofType_BARREL_ROOF, IfcRoofType_RAINBOW_ROOF, IfcRoofType_BUTTERFLY_ROOF, IfcRoofType_PAVILION_ROOF, IfcRoofType_DOME_ROOF, IfcRoofType_FREEFORM, IfcRoofType_NOTDEFINED} IfcRoofTypeEnum;
std::string ToString(IfcRoofTypeEnum v);
IfcRoofTypeEnum FromString(const std::string& s);}
namespace IfcSIPrefix {typedef enum {IfcSIPrefix_EXA, IfcSIPrefix_PETA, IfcSIPrefix_TERA, IfcSIPrefix_GIGA, IfcSIPrefix_MEGA, IfcSIPrefix_KILO, IfcSIPrefix_HECTO, IfcSIPrefix_DECA, IfcSIPrefix_DECI, IfcSIPrefix_CENTI, IfcSIPrefix_MILLI, IfcSIPrefix_MICRO, IfcSIPrefix_NANO, IfcSIPrefix_PICO, IfcSIPrefix_FEMTO, IfcSIPrefix_ATTO} IfcSIPrefix;
std::string ToString(IfcSIPrefix v);
IfcSIPrefix FromString(const std::string& s);}
namespace IfcSIUnitName {typedef enum {IfcSIUnitName_AMPERE, IfcSIUnitName_BECQUEREL, IfcSIUnitName_CANDELA, IfcSIUnitName_COULOMB, IfcSIUnitName_CUBIC_METRE, IfcSIUnitName_DEGREE_CELSIUS, IfcSIUnitName_FARAD, IfcSIUnitName_GRAM, IfcSIUnitName_GRAY, IfcSIUnitName_HENRY, IfcSIUnitName_HERTZ, IfcSIUnitName_JOULE, IfcSIUnitName_KELVIN, IfcSIUnitName_LUMEN, IfcSIUnitName_LUX, IfcSIUnitName_METRE, IfcSIUnitName_MOLE, IfcSIUnitName_NEWTON, IfcSIUnitName_OHM, IfcSIUnitName_PASCAL, IfcSIUnitName_RADIAN, IfcSIUnitName_SECOND, IfcSIUnitName_SIEMENS, IfcSIUnitName_SIEVERT, IfcSIUnitName_SQUARE_METRE, IfcSIUnitName_STERADIAN, IfcSIUnitName_TESLA, IfcSIUnitName_VOLT, IfcSIUnitName_WATT, IfcSIUnitName_WEBER} IfcSIUnitName;
std::string ToString(IfcSIUnitName v);
IfcSIUnitName FromString(const std::string& s);}
namespace IfcSanitaryTerminalTypeEnum {typedef enum {IfcSanitaryTerminalType_BATH, IfcSanitaryTerminalType_BIDET, IfcSanitaryTerminalType_CISTERN, IfcSanitaryTerminalType_SHOWER, IfcSanitaryTerminalType_SINK, IfcSanitaryTerminalType_SANITARYFOUNTAIN, IfcSanitaryTerminalType_TOILETPAN, IfcSanitaryTerminalType_URINAL, IfcSanitaryTerminalType_WASHHANDBASIN, IfcSanitaryTerminalType_WCSEAT, IfcSanitaryTerminalType_USERDEFINED, IfcSanitaryTerminalType_NOTDEFINED} IfcSanitaryTerminalTypeEnum;
std::string ToString(IfcSanitaryTerminalTypeEnum v);
IfcSanitaryTerminalTypeEnum FromString(const std::string& s);}
namespace IfcSectionTypeEnum {typedef enum {IfcSectionType_UNIFORM, IfcSectionType_TAPERED} IfcSectionTypeEnum;
std::string ToString(IfcSectionTypeEnum v);
IfcSectionTypeEnum FromString(const std::string& s);}
namespace IfcSensorTypeEnum {typedef enum {IfcSensorType_CO2SENSOR, IfcSensorType_FIRESENSOR, IfcSensorType_FLOWSENSOR, IfcSensorType_GASSENSOR, IfcSensorType_HEATSENSOR, IfcSensorType_HUMIDITYSENSOR, IfcSensorType_LIGHTSENSOR, IfcSensorType_MOISTURESENSOR, IfcSensorType_MOVEMENTSENSOR, IfcSensorType_PRESSURESENSOR, IfcSensorType_SMOKESENSOR, IfcSensorType_SOUNDSENSOR, IfcSensorType_TEMPERATURESENSOR, IfcSensorType_USERDEFINED, IfcSensorType_NOTDEFINED} IfcSensorTypeEnum;
std::string ToString(IfcSensorTypeEnum v);
IfcSensorTypeEnum FromString(const std::string& s);}
namespace IfcSequenceEnum {typedef enum {IfcSequence_START_START, IfcSequence_START_FINISH, IfcSequence_FINISH_START, IfcSequence_FINISH_FINISH, IfcSequence_NOTDEFINED} IfcSequenceEnum;
std::string ToString(IfcSequenceEnum v);
IfcSequenceEnum FromString(const std::string& s);}
namespace IfcServiceLifeFactorTypeEnum {typedef enum {IfcServiceLifeFactorType_A_QUALITYOFCOMPONENTS, IfcServiceLifeFactorType_B_DESIGNLEVEL, IfcServiceLifeFactorType_C_WORKEXECUTIONLEVEL, IfcServiceLifeFactorType_D_INDOORENVIRONMENT, IfcServiceLifeFactorType_E_OUTDOORENVIRONMENT, IfcServiceLifeFactorType_F_INUSECONDITIONS, IfcServiceLifeFactorType_G_MAINTENANCELEVEL, IfcServiceLifeFactorType_USERDEFINED, IfcServiceLifeFactorType_NOTDEFINED} IfcServiceLifeFactorTypeEnum;
std::string ToString(IfcServiceLifeFactorTypeEnum v);
IfcServiceLifeFactorTypeEnum FromString(const std::string& s);}
namespace IfcServiceLifeTypeEnum {typedef enum {IfcServiceLifeType_ACTUALSERVICELIFE, IfcServiceLifeType_EXPECTEDSERVICELIFE, IfcServiceLifeType_OPTIMISTICREFERENCESERVICELIFE, IfcServiceLifeType_PESSIMISTICREFERENCESERVICELIFE, IfcServiceLifeType_REFERENCESERVICELIFE} IfcServiceLifeTypeEnum;
std::string ToString(IfcServiceLifeTypeEnum v);
IfcServiceLifeTypeEnum FromString(const std::string& s);}
namespace IfcSlabTypeEnum {typedef enum {IfcSlabType_FLOOR, IfcSlabType_ROOF, IfcSlabType_LANDING, IfcSlabType_BASESLAB, IfcSlabType_USERDEFINED, IfcSlabType_NOTDEFINED} IfcSlabTypeEnum;
std::string ToString(IfcSlabTypeEnum v);
IfcSlabTypeEnum FromString(const std::string& s);}
namespace IfcSoundScaleEnum {typedef enum {IfcSoundScale_DBA, IfcSoundScale_DBB, IfcSoundScale_DBC, IfcSoundScale_NC, IfcSoundScale_NR, IfcSoundScale_USERDEFINED, IfcSoundScale_NOTDEFINED} IfcSoundScaleEnum;
std::string ToString(IfcSoundScaleEnum v);
IfcSoundScaleEnum FromString(const std::string& s);}
namespace IfcSpaceHeaterTypeEnum {typedef enum {IfcSpaceHeaterType_SECTIONALRADIATOR, IfcSpaceHeaterType_PANELRADIATOR, IfcSpaceHeaterType_TUBULARRADIATOR, IfcSpaceHeaterType_CONVECTOR, IfcSpaceHeaterType_BASEBOARDHEATER, IfcSpaceHeaterType_FINNEDTUBEUNIT, IfcSpaceHeaterType_UNITHEATER, IfcSpaceHeaterType_USERDEFINED, IfcSpaceHeaterType_NOTDEFINED} IfcSpaceHeaterTypeEnum;
std::string ToString(IfcSpaceHeaterTypeEnum v);
IfcSpaceHeaterTypeEnum FromString(const std::string& s);}
namespace IfcSpaceTypeEnum {typedef enum {IfcSpaceType_USERDEFINED, IfcSpaceType_NOTDEFINED} IfcSpaceTypeEnum;
std::string ToString(IfcSpaceTypeEnum v);
IfcSpaceTypeEnum FromString(const std::string& s);}
namespace IfcStackTerminalTypeEnum {typedef enum {IfcStackTerminalType_BIRDCAGE, IfcStackTerminalType_COWL, IfcStackTerminalType_RAINWATERHOPPER, IfcStackTerminalType_USERDEFINED, IfcStackTerminalType_NOTDEFINED} IfcStackTerminalTypeEnum;
std::string ToString(IfcStackTerminalTypeEnum v);
IfcStackTerminalTypeEnum FromString(const std::string& s);}
namespace IfcStairFlightTypeEnum {typedef enum {IfcStairFlightType_STRAIGHT, IfcStairFlightType_WINDER, IfcStairFlightType_SPIRAL, IfcStairFlightType_CURVED, IfcStairFlightType_FREEFORM, IfcStairFlightType_USERDEFINED, IfcStairFlightType_NOTDEFINED} IfcStairFlightTypeEnum;
std::string ToString(IfcStairFlightTypeEnum v);
IfcStairFlightTypeEnum FromString(const std::string& s);}
namespace IfcStairTypeEnum {typedef enum {IfcStairType_STRAIGHT_RUN_STAIR, IfcStairType_TWO_STRAIGHT_RUN_STAIR, IfcStairType_QUARTER_WINDING_STAIR, IfcStairType_QUARTER_TURN_STAIR, IfcStairType_HALF_WINDING_STAIR, IfcStairType_HALF_TURN_STAIR, IfcStairType_TWO_QUARTER_WINDING_STAIR, IfcStairType_TWO_QUARTER_TURN_STAIR, IfcStairType_THREE_QUARTER_WINDING_STAIR, IfcStairType_THREE_QUARTER_TURN_STAIR, IfcStairType_SPIRAL_STAIR, IfcStairType_DOUBLE_RETURN_STAIR, IfcStairType_CURVED_RUN_STAIR, IfcStairType_TWO_CURVED_RUN_STAIR, IfcStairType_USERDEFINED, IfcStairType_NOTDEFINED} IfcStairTypeEnum;
std::string ToString(IfcStairTypeEnum v);
IfcStairTypeEnum FromString(const std::string& s);}
namespace IfcStateEnum {typedef enum {IfcState_READWRITE, IfcState_READONLY, IfcState_LOCKED, IfcState_READWRITELOCKED, IfcState_READONLYLOCKED} IfcStateEnum;
std::string ToString(IfcStateEnum v);
IfcStateEnum FromString(const std::string& s);}
namespace IfcStructuralCurveTypeEnum {typedef enum {IfcStructuralCurveType_RIGID_JOINED_MEMBER, IfcStructuralCurveType_PIN_JOINED_MEMBER, IfcStructuralCurveType_CABLE, IfcStructuralCurveType_TENSION_MEMBER, IfcStructuralCurveType_COMPRESSION_MEMBER, IfcStructuralCurveType_USERDEFINED, IfcStructuralCurveType_NOTDEFINED} IfcStructuralCurveTypeEnum;
std::string ToString(IfcStructuralCurveTypeEnum v);
IfcStructuralCurveTypeEnum FromString(const std::string& s);}
namespace IfcStructuralSurfaceTypeEnum {typedef enum {IfcStructuralSurfaceType_BENDING_ELEMENT, IfcStructuralSurfaceType_MEMBRANE_ELEMENT, IfcStructuralSurfaceType_SHELL, IfcStructuralSurfaceType_USERDEFINED, IfcStructuralSurfaceType_NOTDEFINED} IfcStructuralSurfaceTypeEnum;
std::string ToString(IfcStructuralSurfaceTypeEnum v);
IfcStructuralSurfaceTypeEnum FromString(const std::string& s);}
namespace IfcSurfaceSide {typedef enum {IfcSurfaceSide_POSITIVE, IfcSurfaceSide_NEGATIVE, IfcSurfaceSide_BOTH} IfcSurfaceSide;
std::string ToString(IfcSurfaceSide v);
IfcSurfaceSide FromString(const std::string& s);}
namespace IfcSurfaceTextureEnum {typedef enum {IfcSurfaceTexture_BUMP, IfcSurfaceTexture_OPACITY, IfcSurfaceTexture_REFLECTION, IfcSurfaceTexture_SELFILLUMINATION, IfcSurfaceTexture_SHININESS, IfcSurfaceTexture_SPECULAR, IfcSurfaceTexture_TEXTURE, IfcSurfaceTexture_TRANSPARENCYMAP, IfcSurfaceTexture_NOTDEFINED} IfcSurfaceTextureEnum;
std::string ToString(IfcSurfaceTextureEnum v);
IfcSurfaceTextureEnum FromString(const std::string& s);}
namespace IfcSwitchingDeviceTypeEnum {typedef enum {IfcSwitchingDeviceType_CONTACTOR, IfcSwitchingDeviceType_EMERGENCYSTOP, IfcSwitchingDeviceType_STARTER, IfcSwitchingDeviceType_SWITCHDISCONNECTOR, IfcSwitchingDeviceType_TOGGLESWITCH, IfcSwitchingDeviceType_USERDEFINED, IfcSwitchingDeviceType_NOTDEFINED} IfcSwitchingDeviceTypeEnum;
std::string ToString(IfcSwitchingDeviceTypeEnum v);
IfcSwitchingDeviceTypeEnum FromString(const std::string& s);}
namespace IfcTankTypeEnum {typedef enum {IfcTankType_PREFORMED, IfcTankType_SECTIONAL, IfcTankType_EXPANSION, IfcTankType_PRESSUREVESSEL, IfcTankType_USERDEFINED, IfcTankType_NOTDEFINED} IfcTankTypeEnum;
std::string ToString(IfcTankTypeEnum v);
IfcTankTypeEnum FromString(const std::string& s);}
namespace IfcTendonTypeEnum {typedef enum {IfcTendonType_STRAND, IfcTendonType_WIRE, IfcTendonType_BAR, IfcTendonType_COATED, IfcTendonType_USERDEFINED, IfcTendonType_NOTDEFINED} IfcTendonTypeEnum;
std::string ToString(IfcTendonTypeEnum v);
IfcTendonTypeEnum FromString(const std::string& s);}
namespace IfcTextPath {typedef enum {IfcTextPath_LEFT, IfcTextPath_RIGHT, IfcTextPath_UP, IfcTextPath_DOWN} IfcTextPath;
std::string ToString(IfcTextPath v);
IfcTextPath FromString(const std::string& s);}
namespace IfcThermalLoadSourceEnum {typedef enum {IfcThermalLoadSource_PEOPLE, IfcThermalLoadSource_LIGHTING, IfcThermalLoadSource_EQUIPMENT, IfcThermalLoadSource_VENTILATIONINDOORAIR, IfcThermalLoadSource_VENTILATIONOUTSIDEAIR, IfcThermalLoadSource_RECIRCULATEDAIR, IfcThermalLoadSource_EXHAUSTAIR, IfcThermalLoadSource_AIREXCHANGERATE, IfcThermalLoadSource_DRYBULBTEMPERATURE, IfcThermalLoadSource_RELATIVEHUMIDITY, IfcThermalLoadSource_INFILTRATION, IfcThermalLoadSource_USERDEFINED, IfcThermalLoadSource_NOTDEFINED} IfcThermalLoadSourceEnum;
std::string ToString(IfcThermalLoadSourceEnum v);
IfcThermalLoadSourceEnum FromString(const std::string& s);}
namespace IfcThermalLoadTypeEnum {typedef enum {IfcThermalLoadType_SENSIBLE, IfcThermalLoadType_LATENT, IfcThermalLoadType_RADIANT, IfcThermalLoadType_NOTDEFINED} IfcThermalLoadTypeEnum;
std::string ToString(IfcThermalLoadTypeEnum v);
IfcThermalLoadTypeEnum FromString(const std::string& s);}
namespace IfcTimeSeriesDataTypeEnum {typedef enum {IfcTimeSeriesDataType_CONTINUOUS, IfcTimeSeriesDataType_DISCRETE, IfcTimeSeriesDataType_DISCRETEBINARY, IfcTimeSeriesDataType_PIECEWISEBINARY, IfcTimeSeriesDataType_PIECEWISECONSTANT, IfcTimeSeriesDataType_PIECEWISECONTINUOUS, IfcTimeSeriesDataType_NOTDEFINED} IfcTimeSeriesDataTypeEnum;
std::string ToString(IfcTimeSeriesDataTypeEnum v);
IfcTimeSeriesDataTypeEnum FromString(const std::string& s);}
namespace IfcTimeSeriesScheduleTypeEnum {typedef enum {IfcTimeSeriesScheduleType_ANNUAL, IfcTimeSeriesScheduleType_MONTHLY, IfcTimeSeriesScheduleType_WEEKLY, IfcTimeSeriesScheduleType_DAILY, IfcTimeSeriesScheduleType_USERDEFINED, IfcTimeSeriesScheduleType_NOTDEFINED} IfcTimeSeriesScheduleTypeEnum;
std::string ToString(IfcTimeSeriesScheduleTypeEnum v);
IfcTimeSeriesScheduleTypeEnum FromString(const std::string& s);}
namespace IfcTransformerTypeEnum {typedef enum {IfcTransformerType_CURRENT, IfcTransformerType_FREQUENCY, IfcTransformerType_VOLTAGE, IfcTransformerType_USERDEFINED, IfcTransformerType_NOTDEFINED} IfcTransformerTypeEnum;
std::string ToString(IfcTransformerTypeEnum v);
IfcTransformerTypeEnum FromString(const std::string& s);}
namespace IfcTransitionCode {typedef enum {IfcTransitionCode_DISCONTINUOUS, IfcTransitionCode_CONTINUOUS, IfcTransitionCode_CONTSAMEGRADIENT, IfcTransitionCode_CONTSAMEGRADIENTSAMECURVATURE} IfcTransitionCode;
std::string ToString(IfcTransitionCode v);
IfcTransitionCode FromString(const std::string& s);}
namespace IfcTransportElementTypeEnum {typedef enum {IfcTransportElementType_ELEVATOR, IfcTransportElementType_ESCALATOR, IfcTransportElementType_MOVINGWALKWAY, IfcTransportElementType_USERDEFINED, IfcTransportElementType_NOTDEFINED} IfcTransportElementTypeEnum;
std::string ToString(IfcTransportElementTypeEnum v);
IfcTransportElementTypeEnum FromString(const std::string& s);}
namespace IfcTrimmingPreference {typedef enum {IfcTrimmingPreference_CARTESIAN, IfcTrimmingPreference_PARAMETER, IfcTrimmingPreference_UNSPECIFIED} IfcTrimmingPreference;
std::string ToString(IfcTrimmingPreference v);
IfcTrimmingPreference FromString(const std::string& s);}
namespace IfcTubeBundleTypeEnum {typedef enum {IfcTubeBundleType_FINNED, IfcTubeBundleType_USERDEFINED, IfcTubeBundleType_NOTDEFINED} IfcTubeBundleTypeEnum;
std::string ToString(IfcTubeBundleTypeEnum v);
IfcTubeBundleTypeEnum FromString(const std::string& s);}
namespace IfcUnitEnum {typedef enum {IfcUnit_ABSORBEDDOSEUNIT, IfcUnit_AMOUNTOFSUBSTANCEUNIT, IfcUnit_AREAUNIT, IfcUnit_DOSEEQUIVALENTUNIT, IfcUnit_ELECTRICCAPACITANCEUNIT, IfcUnit_ELECTRICCHARGEUNIT, IfcUnit_ELECTRICCONDUCTANCEUNIT, IfcUnit_ELECTRICCURRENTUNIT, IfcUnit_ELECTRICRESISTANCEUNIT, IfcUnit_ELECTRICVOLTAGEUNIT, IfcUnit_ENERGYUNIT, IfcUnit_FORCEUNIT, IfcUnit_FREQUENCYUNIT, IfcUnit_ILLUMINANCEUNIT, IfcUnit_INDUCTANCEUNIT, IfcUnit_LENGTHUNIT, IfcUnit_LUMINOUSFLUXUNIT, IfcUnit_LUMINOUSINTENSITYUNIT, IfcUnit_MAGNETICFLUXDENSITYUNIT, IfcUnit_MAGNETICFLUXUNIT, IfcUnit_MASSUNIT, IfcUnit_PLANEANGLEUNIT, IfcUnit_POWERUNIT, IfcUnit_PRESSUREUNIT, IfcUnit_RADIOACTIVITYUNIT, IfcUnit_SOLIDANGLEUNIT, IfcUnit_THERMODYNAMICTEMPERATUREUNIT, IfcUnit_TIMEUNIT, IfcUnit_VOLUMEUNIT, IfcUnit_USERDEFINED} IfcUnitEnum;
std::string ToString(IfcUnitEnum v);
IfcUnitEnum FromString(const std::string& s);}
namespace IfcUnitaryEquipmentTypeEnum {typedef enum {IfcUnitaryEquipmentType_AIRHANDLER, IfcUnitaryEquipmentType_AIRCONDITIONINGUNIT, IfcUnitaryEquipmentType_SPLITSYSTEM, IfcUnitaryEquipmentType_ROOFTOPUNIT, IfcUnitaryEquipmentType_USERDEFINED, IfcUnitaryEquipmentType_NOTDEFINED} IfcUnitaryEquipmentTypeEnum;
std::string ToString(IfcUnitaryEquipmentTypeEnum v);
IfcUnitaryEquipmentTypeEnum FromString(const std::string& s);}
namespace IfcValveTypeEnum {typedef enum {IfcValveType_AIRRELEASE, IfcValveType_ANTIVACUUM, IfcValveType_CHANGEOVER, IfcValveType_CHECK, IfcValveType_COMMISSIONING, IfcValveType_DIVERTING, IfcValveType_DRAWOFFCOCK, IfcValveType_DOUBLECHECK, IfcValveType_DOUBLEREGULATING, IfcValveType_FAUCET, IfcValveType_FLUSHING, IfcValveType_GASCOCK, IfcValveType_GASTAP, IfcValveType_ISOLATING, IfcValveType_MIXING, IfcValveType_PRESSUREREDUCING, IfcValveType_PRESSURERELIEF, IfcValveType_REGULATING, IfcValveType_SAFETYCUTOFF, IfcValveType_STEAMTRAP, IfcValveType_STOPCOCK, IfcValveType_USERDEFINED, IfcValveType_NOTDEFINED} IfcValveTypeEnum;
std::string ToString(IfcValveTypeEnum v);
IfcValveTypeEnum FromString(const std::string& s);}
namespace IfcVibrationIsolatorTypeEnum {typedef enum {IfcVibrationIsolatorType_COMPRESSION, IfcVibrationIsolatorType_SPRING, IfcVibrationIsolatorType_USERDEFINED, IfcVibrationIsolatorType_NOTDEFINED} IfcVibrationIsolatorTypeEnum;
std::string ToString(IfcVibrationIsolatorTypeEnum v);
IfcVibrationIsolatorTypeEnum FromString(const std::string& s);}
namespace IfcWallTypeEnum {typedef enum {IfcWallType_STANDARD, IfcWallType_POLYGONAL, IfcWallType_SHEAR, IfcWallType_ELEMENTEDWALL, IfcWallType_PLUMBINGWALL, IfcWallType_USERDEFINED, IfcWallType_NOTDEFINED} IfcWallTypeEnum;
std::string ToString(IfcWallTypeEnum v);
IfcWallTypeEnum FromString(const std::string& s);}
namespace IfcWasteTerminalTypeEnum {typedef enum {IfcWasteTerminalType_FLOORTRAP, IfcWasteTerminalType_FLOORWASTE, IfcWasteTerminalType_GULLYSUMP, IfcWasteTerminalType_GULLYTRAP, IfcWasteTerminalType_GREASEINTERCEPTOR, IfcWasteTerminalType_OILINTERCEPTOR, IfcWasteTerminalType_PETROLINTERCEPTOR, IfcWasteTerminalType_ROOFDRAIN, IfcWasteTerminalType_WASTEDISPOSALUNIT, IfcWasteTerminalType_WASTETRAP, IfcWasteTerminalType_USERDEFINED, IfcWasteTerminalType_NOTDEFINED} IfcWasteTerminalTypeEnum;
std::string ToString(IfcWasteTerminalTypeEnum v);
IfcWasteTerminalTypeEnum FromString(const std::string& s);}
namespace IfcWindowPanelOperationEnum {typedef enum {IfcWindowPanelOperation_SIDEHUNGRIGHTHAND, IfcWindowPanelOperation_SIDEHUNGLEFTHAND, IfcWindowPanelOperation_TILTANDTURNRIGHTHAND, IfcWindowPanelOperation_TILTANDTURNLEFTHAND, IfcWindowPanelOperation_TOPHUNG, IfcWindowPanelOperation_BOTTOMHUNG, IfcWindowPanelOperation_PIVOTHORIZONTAL, IfcWindowPanelOperation_PIVOTVERTICAL, IfcWindowPanelOperation_SLIDINGHORIZONTAL, IfcWindowPanelOperation_SLIDINGVERTICAL, IfcWindowPanelOperation_REMOVABLECASEMENT, IfcWindowPanelOperation_FIXEDCASEMENT, IfcWindowPanelOperation_OTHEROPERATION, IfcWindowPanelOperation_NOTDEFINED} IfcWindowPanelOperationEnum;
std::string ToString(IfcWindowPanelOperationEnum v);
IfcWindowPanelOperationEnum FromString(const std::string& s);}
namespace IfcWindowPanelPositionEnum {typedef enum {IfcWindowPanelPosition_LEFT, IfcWindowPanelPosition_MIDDLE, IfcWindowPanelPosition_RIGHT, IfcWindowPanelPosition_BOTTOM, IfcWindowPanelPosition_TOP, IfcWindowPanelPosition_NOTDEFINED} IfcWindowPanelPositionEnum;
std::string ToString(IfcWindowPanelPositionEnum v);
IfcWindowPanelPositionEnum FromString(const std::string& s);}
namespace IfcWindowStyleConstructionEnum {typedef enum {IfcWindowStyleConstruction_ALUMINIUM, IfcWindowStyleConstruction_HIGH_GRADE_STEEL, IfcWindowStyleConstruction_STEEL, IfcWindowStyleConstruction_WOOD, IfcWindowStyleConstruction_ALUMINIUM_WOOD, IfcWindowStyleConstruction_PLASTIC, IfcWindowStyleConstruction_OTHER_CONSTRUCTION, IfcWindowStyleConstruction_NOTDEFINED} IfcWindowStyleConstructionEnum;
std::string ToString(IfcWindowStyleConstructionEnum v);
IfcWindowStyleConstructionEnum FromString(const std::string& s);}
namespace IfcWindowStyleOperationEnum {typedef enum {IfcWindowStyleOperation_SINGLE_PANEL, IfcWindowStyleOperation_DOUBLE_PANEL_VERTICAL, IfcWindowStyleOperation_DOUBLE_PANEL_HORIZONTAL, IfcWindowStyleOperation_TRIPLE_PANEL_VERTICAL, IfcWindowStyleOperation_TRIPLE_PANEL_BOTTOM, IfcWindowStyleOperation_TRIPLE_PANEL_TOP, IfcWindowStyleOperation_TRIPLE_PANEL_LEFT, IfcWindowStyleOperation_TRIPLE_PANEL_RIGHT, IfcWindowStyleOperation_TRIPLE_PANEL_HORIZONTAL, IfcWindowStyleOperation_USERDEFINED, IfcWindowStyleOperation_NOTDEFINED} IfcWindowStyleOperationEnum;
std::string ToString(IfcWindowStyleOperationEnum v);
IfcWindowStyleOperationEnum FromString(const std::string& s);}
namespace IfcWorkControlTypeEnum {typedef enum {IfcWorkControlType_ACTUAL, IfcWorkControlType_BASELINE, IfcWorkControlType_PLANNED, IfcWorkControlType_USERDEFINED, IfcWorkControlType_NOTDEFINED} IfcWorkControlTypeEnum;
std::string ToString(IfcWorkControlTypeEnum v);
IfcWorkControlTypeEnum FromString(const std::string& s);}
// Forward definitions
class Ifc2DCompositeCurve; class IfcActionRequest; class IfcActor; class IfcActorRole; class IfcActuatorType; class IfcAddress; class IfcAirTerminalBoxType; class IfcAirTerminalType; class IfcAirToAirHeatRecoveryType; class IfcAlarmType; class IfcAngularDimension; class IfcAnnotation; class IfcAnnotationCurveOccurrence; class IfcAnnotationFillArea; class IfcAnnotationFillAreaOccurrence; class IfcAnnotationOccurrence; class IfcAnnotationSurface; class IfcAnnotationSurfaceOccurrence; class IfcAnnotationSymbolOccurrence; class IfcAnnotationTextOccurrence; class IfcApplication; class IfcAppliedValue; class IfcAppliedValueRelationship; class IfcApproval; class IfcApprovalActorRelationship; class IfcApprovalPropertyRelationship; class IfcApprovalRelationship; class IfcArbitraryClosedProfileDef; class IfcArbitraryOpenProfileDef; class IfcArbitraryProfileDefWithVoids; class IfcAsset; class IfcAsymmetricIShapeProfileDef; class IfcAxis1Placement; class IfcAxis2Placement2D; class IfcAxis2Placement3D; class IfcBSplineCurve; class IfcBeam; class IfcBeamType; class IfcBezierCurve; class IfcBlobTexture; class IfcBlock; class IfcBoilerType; class IfcBooleanClippingResult; class IfcBooleanResult; class IfcBoundaryCondition; class IfcBoundaryEdgeCondition; class IfcBoundaryFaceCondition; class IfcBoundaryNodeCondition; class IfcBoundaryNodeConditionWarping; class IfcBoundedCurve; class IfcBoundedSurface; class IfcBoundingBox; class IfcBoxedHalfSpace; class IfcBuilding; class IfcBuildingElement; class IfcBuildingElementComponent; class IfcBuildingElementPart; class IfcBuildingElementProxy; class IfcBuildingElementProxyType; class IfcBuildingElementType; class IfcBuildingStorey; class IfcCShapeProfileDef; class IfcCableCarrierFittingType; class IfcCableCarrierSegmentType; class IfcCableSegmentType; class IfcCalendarDate; class IfcCartesianPoint; class IfcCartesianTransformationOperator; class IfcCartesianTransformationOperator2D; class IfcCartesianTransformationOperator2DnonUniform; class IfcCartesianTransformationOperator3D; class IfcCartesianTransformationOperator3DnonUniform; class IfcCenterLineProfileDef; class IfcChamferEdgeFeature; class IfcChillerType; class IfcCircle; class IfcCircleHollowProfileDef; class IfcCircleProfileDef; class IfcClassification; class IfcClassificationItem; class IfcClassificationItemRelationship; class IfcClassificationNotation; class IfcClassificationNotationFacet; class IfcClassificationReference; class IfcClosedShell; class IfcCoilType; class IfcColourRgb; class IfcColourSpecification; class IfcColumn; class IfcColumnType; class IfcComplexProperty; class IfcCompositeCurve; class IfcCompositeCurveSegment; class IfcCompositeProfileDef; class IfcCompressorType; class IfcCondenserType; class IfcCondition; class IfcConditionCriterion; class IfcConic; class IfcConnectedFaceSet; class IfcConnectionCurveGeometry; class IfcConnectionGeometry; class IfcConnectionPointEccentricity; class IfcConnectionPointGeometry; class IfcConnectionPortGeometry; class IfcConnectionSurfaceGeometry; class IfcConstraint; class IfcConstraintAggregationRelationship; class IfcConstraintClassificationRelationship; class IfcConstraintRelationship; class IfcConstructionEquipmentResource; class IfcConstructionMaterialResource; class IfcConstructionProductResource; class IfcConstructionResource; class IfcContextDependentUnit; class IfcControl; class IfcControllerType; class IfcConversionBasedUnit; class IfcCooledBeamType; class IfcCoolingTowerType; class IfcCoordinatedUniversalTimeOffset; class IfcCostItem; class IfcCostSchedule; class IfcCostValue; class IfcCovering; class IfcCoveringType; class IfcCraneRailAShapeProfileDef; class IfcCraneRailFShapeProfileDef; class IfcCrewResource; class IfcCsgPrimitive3D; class IfcCsgSolid; class IfcCurrencyRelationship; class IfcCurtainWall; class IfcCurtainWallType; class IfcCurve; class IfcCurveBoundedPlane; class IfcCurveStyle; class IfcCurveStyleFont; class IfcCurveStyleFontAndScaling; class IfcCurveStyleFontPattern; class IfcDamperType; class IfcDateAndTime; class IfcDefinedSymbol; class IfcDerivedProfileDef; class IfcDerivedUnit; class IfcDerivedUnitElement; class IfcDiameterDimension; class IfcDimensionCalloutRelationship; class IfcDimensionCurve; class IfcDimensionCurveDirectedCallout; class IfcDimensionCurveTerminator; class IfcDimensionPair; class IfcDimensionalExponents; class IfcDirection; class IfcDiscreteAccessory; class IfcDiscreteAccessoryType; class IfcDistributionChamberElement; class IfcDistributionChamberElementType; class IfcDistributionControlElement; class IfcDistributionControlElementType; class IfcDistributionElement; class IfcDistributionElementType; class IfcDistributionFlowElement; class IfcDistributionFlowElementType; class IfcDistributionPort; class IfcDocumentElectronicFormat; class IfcDocumentInformation; class IfcDocumentInformationRelationship; class IfcDocumentReference; class IfcDoor; class IfcDoorLiningProperties; class IfcDoorPanelProperties; class IfcDoorStyle; class IfcDraughtingCallout; class IfcDraughtingCalloutRelationship; class IfcDraughtingPreDefinedColour; class IfcDraughtingPreDefinedCurveFont; class IfcDraughtingPreDefinedTextFont; class IfcDuctFittingType; class IfcDuctSegmentType; class IfcDuctSilencerType; class IfcEdge; class IfcEdgeCurve; class IfcEdgeFeature; class IfcEdgeLoop; class IfcElectricApplianceType; class IfcElectricDistributionPoint; class IfcElectricFlowStorageDeviceType; class IfcElectricGeneratorType; class IfcElectricHeaterType; class IfcElectricMotorType; class IfcElectricTimeControlType; class IfcElectricalBaseProperties; class IfcElectricalCircuit; class IfcElectricalElement; class IfcElement; class IfcElementAssembly; class IfcElementComponent; class IfcElementComponentType; class IfcElementQuantity; class IfcElementType; class IfcElementarySurface; class IfcEllipse; class IfcEllipseProfileDef; class IfcEnergyConversionDevice; class IfcEnergyConversionDeviceType; class IfcEnergyProperties; class IfcEnvironmentalImpactValue; class IfcEquipmentElement; class IfcEquipmentStandard; class IfcEvaporativeCoolerType; class IfcEvaporatorType; class IfcExtendedMaterialProperties; class IfcExternalReference; class IfcExternallyDefinedHatchStyle; class IfcExternallyDefinedSurfaceStyle; class IfcExternallyDefinedSymbol; class IfcExternallyDefinedTextFont; class IfcExtrudedAreaSolid; class IfcFace; class IfcFaceBasedSurfaceModel; class IfcFaceBound; class IfcFaceOuterBound; class IfcFaceSurface; class IfcFacetedBrep; class IfcFacetedBrepWithVoids; class IfcFailureConnectionCondition; class IfcFanType; class IfcFastener; class IfcFastenerType; class IfcFeatureElement; class IfcFeatureElementAddition; class IfcFeatureElementSubtraction; class IfcFillAreaStyle; class IfcFillAreaStyleHatching; class IfcFillAreaStyleTileSymbolWithStyle; class IfcFillAreaStyleTiles; class IfcFilterType; class IfcFireSuppressionTerminalType; class IfcFlowController; class IfcFlowControllerType; class IfcFlowFitting; class IfcFlowFittingType; class IfcFlowInstrumentType; class IfcFlowMeterType; class IfcFlowMovingDevice; class IfcFlowMovingDeviceType; class IfcFlowSegment; class IfcFlowSegmentType; class IfcFlowStorageDevice; class IfcFlowStorageDeviceType; class IfcFlowTerminal; class IfcFlowTerminalType; class IfcFlowTreatmentDevice; class IfcFlowTreatmentDeviceType; class IfcFluidFlowProperties; class IfcFooting; class IfcFuelProperties; class IfcFurnishingElement; class IfcFurnishingElementType; class IfcFurnitureStandard; class IfcFurnitureType; class IfcGasTerminalType; class IfcGeneralMaterialProperties; class IfcGeneralProfileProperties; class IfcGeometricCurveSet; class IfcGeometricRepresentationContext; class IfcGeometricRepresentationItem; class IfcGeometricRepresentationSubContext; class IfcGeometricSet; class IfcGrid; class IfcGridAxis; class IfcGridPlacement; class IfcGroup; class IfcHalfSpaceSolid; class IfcHeatExchangerType; class IfcHumidifierType; class IfcHygroscopicMaterialProperties; class IfcIShapeProfileDef; class IfcImageTexture; class IfcInventory; class IfcIrregularTimeSeries; class IfcIrregularTimeSeriesValue; class IfcJunctionBoxType; class IfcLShapeProfileDef; class IfcLaborResource; class IfcLampType; class IfcLibraryInformation; class IfcLibraryReference; class IfcLightDistributionData; class IfcLightFixtureType; class IfcLightIntensityDistribution; class IfcLightSource; class IfcLightSourceAmbient; class IfcLightSourceDirectional; class IfcLightSourceGoniometric; class IfcLightSourcePositional; class IfcLightSourceSpot; class IfcLine; class IfcLinearDimension; class IfcLocalPlacement; class IfcLocalTime; class IfcLoop; class IfcManifoldSolidBrep; class IfcMappedItem; class IfcMaterial; class IfcMaterialClassificationRelationship; class IfcMaterialDefinitionRepresentation; class IfcMaterialLayer; class IfcMaterialLayerSet; class IfcMaterialLayerSetUsage; class IfcMaterialList; class IfcMaterialProperties; class IfcMeasureWithUnit; class IfcMechanicalConcreteMaterialProperties; class IfcMechanicalFastener; class IfcMechanicalFastenerType; class IfcMechanicalMaterialProperties; class IfcMechanicalSteelMaterialProperties; class IfcMember; class IfcMemberType; class IfcMetric; class IfcMonetaryUnit; class IfcMotorConnectionType; class IfcMove; class IfcNamedUnit; class IfcObject; class IfcObjectDefinition; class IfcObjectPlacement; class IfcObjective; class IfcOccupant; class IfcOffsetCurve2D; class IfcOffsetCurve3D; class IfcOneDirectionRepeatFactor; class IfcOpenShell; class IfcOpeningElement; class IfcOpticalMaterialProperties; class IfcOrderAction; class IfcOrganization; class IfcOrganizationRelationship; class IfcOrientedEdge; class IfcOutletType; class IfcOwnerHistory; class IfcParameterizedProfileDef; class IfcPath; class IfcPerformanceHistory; class IfcPermeableCoveringProperties; class IfcPermit; class IfcPerson; class IfcPersonAndOrganization; class IfcPhysicalComplexQuantity; class IfcPhysicalQuantity; class IfcPhysicalSimpleQuantity; class IfcPile; class IfcPipeFittingType; class IfcPipeSegmentType; class IfcPixelTexture; class IfcPlacement; class IfcPlanarBox; class IfcPlanarExtent; class IfcPlane; class IfcPlate; class IfcPlateType; class IfcPoint; class IfcPointOnCurve; class IfcPointOnSurface; class IfcPolyLoop; class IfcPolygonalBoundedHalfSpace; class IfcPolyline; class IfcPort; class IfcPostalAddress; class IfcPreDefinedColour; class IfcPreDefinedCurveFont; class IfcPreDefinedDimensionSymbol; class IfcPreDefinedItem; class IfcPreDefinedPointMarkerSymbol; class IfcPreDefinedSymbol; class IfcPreDefinedTerminatorSymbol; class IfcPreDefinedTextFont; class IfcPresentationLayerAssignment; class IfcPresentationLayerWithStyle; class IfcPresentationStyle; class IfcPresentationStyleAssignment; class IfcProcedure; class IfcProcess; class IfcProduct; class IfcProductDefinitionShape; class IfcProductRepresentation; class IfcProductsOfCombustionProperties; class IfcProfileDef; class IfcProfileProperties; class IfcProject; class IfcProjectOrder; class IfcProjectOrderRecord; class IfcProjectionCurve; class IfcProjectionElement; class IfcProperty; class IfcPropertyBoundedValue; class IfcPropertyConstraintRelationship; class IfcPropertyDefinition; class IfcPropertyDependencyRelationship; class IfcPropertyEnumeratedValue; class IfcPropertyEnumeration; class IfcPropertyListValue; class IfcPropertyReferenceValue; class IfcPropertySet; class IfcPropertySetDefinition; class IfcPropertySingleValue; class IfcPropertyTableValue; class IfcProtectiveDeviceType; class IfcProxy; class IfcPumpType; class IfcQuantityArea; class IfcQuantityCount; class IfcQuantityLength; class IfcQuantityTime; class IfcQuantityVolume; class IfcQuantityWeight; class IfcRadiusDimension; class IfcRailing; class IfcRailingType; class IfcRamp; class IfcRampFlight; class IfcRampFlightType; class IfcRationalBezierCurve; class IfcRectangleHollowProfileDef; class IfcRectangleProfileDef; class IfcRectangularPyramid; class IfcRectangularTrimmedSurface; class IfcReferencesValueDocument; class IfcRegularTimeSeries; class IfcReinforcementBarProperties; class IfcReinforcementDefinitionProperties; class IfcReinforcingBar; class IfcReinforcingElement; class IfcReinforcingMesh; class IfcRelAggregates; class IfcRelAssigns; class IfcRelAssignsTasks; class IfcRelAssignsToActor; class IfcRelAssignsToControl; class IfcRelAssignsToGroup; class IfcRelAssignsToProcess; class IfcRelAssignsToProduct; class IfcRelAssignsToProjectOrder; class IfcRelAssignsToResource; class IfcRelAssociates; class IfcRelAssociatesAppliedValue; class IfcRelAssociatesApproval; class IfcRelAssociatesClassification; class IfcRelAssociatesConstraint; class IfcRelAssociatesDocument; class IfcRelAssociatesLibrary; class IfcRelAssociatesMaterial; class IfcRelAssociatesProfileProperties; class IfcRelConnects; class IfcRelConnectsElements; class IfcRelConnectsPathElements; class IfcRelConnectsPortToElement; class IfcRelConnectsPorts; class IfcRelConnectsStructuralActivity; class IfcRelConnectsStructuralElement; class IfcRelConnectsStructuralMember; class IfcRelConnectsWithEccentricity; class IfcRelConnectsWithRealizingElements; class IfcRelContainedInSpatialStructure; class IfcRelCoversBldgElements; class IfcRelCoversSpaces; class IfcRelDecomposes; class IfcRelDefines; class IfcRelDefinesByProperties; class IfcRelDefinesByType; class IfcRelFillsElement; class IfcRelFlowControlElements; class IfcRelInteractionRequirements; class IfcRelNests; class IfcRelOccupiesSpaces; class IfcRelOverridesProperties; class IfcRelProjectsElement; class IfcRelReferencedInSpatialStructure; class IfcRelSchedulesCostItems; class IfcRelSequence; class IfcRelServicesBuildings; class IfcRelSpaceBoundary; class IfcRelVoidsElement; class IfcRelationship; class IfcRelaxation; class IfcRepresentation; class IfcRepresentationContext; class IfcRepresentationItem; class IfcRepresentationMap; class IfcResource; class IfcRevolvedAreaSolid; class IfcRibPlateProfileProperties; class IfcRightCircularCone; class IfcRightCircularCylinder; class IfcRoof; class IfcRoot; class IfcRoundedEdgeFeature; class IfcRoundedRectangleProfileDef; class IfcSIUnit; class IfcSanitaryTerminalType; class IfcScheduleTimeControl; class IfcSectionProperties; class IfcSectionReinforcementProperties; class IfcSectionedSpine; class IfcSensorType; class IfcServiceLife; class IfcServiceLifeFactor; class IfcShapeAspect; class IfcShapeModel; class IfcShapeRepresentation; class IfcShellBasedSurfaceModel; class IfcSimpleProperty; class IfcSite; class IfcSlab; class IfcSlabType; class IfcSlippageConnectionCondition; class IfcSolidModel; class IfcSoundProperties; class IfcSoundValue; class IfcSpace; class IfcSpaceHeaterType; class IfcSpaceProgram; class IfcSpaceThermalLoadProperties; class IfcSpaceType; class IfcSpatialStructureElement; class IfcSpatialStructureElementType; class IfcSphere; class IfcStackTerminalType; class IfcStair; class IfcStairFlight; class IfcStairFlightType; class IfcStructuralAction; class IfcStructuralActivity; class IfcStructuralAnalysisModel; class IfcStructuralConnection; class IfcStructuralConnectionCondition; class IfcStructuralCurveConnection; class IfcStructuralCurveMember; class IfcStructuralCurveMemberVarying; class IfcStructuralItem; class IfcStructuralLinearAction; class IfcStructuralLinearActionVarying; class IfcStructuralLoad; class IfcStructuralLoadGroup; class IfcStructuralLoadLinearForce; class IfcStructuralLoadPlanarForce; class IfcStructuralLoadSingleDisplacement; class IfcStructuralLoadSingleDisplacementDistortion; class IfcStructuralLoadSingleForce; class IfcStructuralLoadSingleForceWarping; class IfcStructuralLoadStatic; class IfcStructuralLoadTemperature; class IfcStructuralMember; class IfcStructuralPlanarAction; class IfcStructuralPlanarActionVarying; class IfcStructuralPointAction; class IfcStructuralPointConnection; class IfcStructuralPointReaction; class IfcStructuralProfileProperties; class IfcStructuralReaction; class IfcStructuralResultGroup; class IfcStructuralSteelProfileProperties; class IfcStructuralSurfaceConnection; class IfcStructuralSurfaceMember; class IfcStructuralSurfaceMemberVarying; class IfcStructuredDimensionCallout; class IfcStyleModel; class IfcStyledItem; class IfcStyledRepresentation; class IfcSubContractResource; class IfcSubedge; class IfcSurface; class IfcSurfaceCurveSweptAreaSolid; class IfcSurfaceOfLinearExtrusion; class IfcSurfaceOfRevolution; class IfcSurfaceStyle; class IfcSurfaceStyleLighting; class IfcSurfaceStyleRefraction; class IfcSurfaceStyleRendering; class IfcSurfaceStyleShading; class IfcSurfaceStyleWithTextures; class IfcSurfaceTexture; class IfcSweptAreaSolid; class IfcSweptDiskSolid; class IfcSweptSurface; class IfcSwitchingDeviceType; class IfcSymbolStyle; class IfcSystem; class IfcSystemFurnitureElementType; class IfcTShapeProfileDef; class IfcTable; class IfcTableRow; class IfcTankType; class IfcTask; class IfcTelecomAddress; class IfcTendon; class IfcTendonAnchor; class IfcTerminatorSymbol; class IfcTextLiteral; class IfcTextLiteralWithExtent; class IfcTextStyle; class IfcTextStyleFontModel; class IfcTextStyleForDefinedFont; class IfcTextStyleTextModel; class IfcTextStyleWithBoxCharacteristics; class IfcTextureCoordinate; class IfcTextureCoordinateGenerator; class IfcTextureMap; class IfcTextureVertex; class IfcThermalMaterialProperties; class IfcTimeSeries; class IfcTimeSeriesReferenceRelationship; class IfcTimeSeriesSchedule; class IfcTimeSeriesValue; class IfcTopologicalRepresentationItem; class IfcTopologyRepresentation; class IfcTransformerType; class IfcTransportElement; class IfcTransportElementType; class IfcTrapeziumProfileDef; class IfcTrimmedCurve; class IfcTubeBundleType; class IfcTwoDirectionRepeatFactor; class IfcTypeObject; class IfcTypeProduct; class IfcUShapeProfileDef; class IfcUnitAssignment; class IfcUnitaryEquipmentType; class IfcValveType; class IfcVector; class IfcVertex; class IfcVertexBasedTextureMap; class IfcVertexLoop; class IfcVertexPoint; class IfcVibrationIsolatorType; class IfcVirtualElement; class IfcVirtualGridIntersection; class IfcWall; class IfcWallStandardCase; class IfcWallType; class IfcWasteTerminalType; class IfcWaterProperties; class IfcWindow; class IfcWindowLiningProperties; class IfcWindowPanelProperties; class IfcWindowStyle; class IfcWorkControl; class IfcWorkPlan; class IfcWorkSchedule; class IfcZShapeProfileDef; class IfcZone;

class IfcActorRole : public IfcBaseClass {
public:
    IfcRoleEnum::IfcRoleEnum Role();
    bool hasUserDefinedRole();
    IfcLabel UserDefinedRole();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcActorRole (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcActorRole* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > list;
    typedef IfcTemplatedEntityList<IfcActorRole>::it it;
};
class IfcAddress : public IfcBaseClass {
public:
    bool hasPurpose();
    IfcAddressTypeEnum::IfcAddressTypeEnum Purpose();
    bool hasDescription();
    IfcText Description();
    bool hasUserDefinedPurpose();
    IfcLabel UserDefinedPurpose();
    SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > OfPerson(); // INVERSE IfcPerson::Addresses
    SHARED_PTR< IfcTemplatedEntityList<IfcOrganization> > OfOrganization(); // INVERSE IfcOrganization::Addresses
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAddress (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAddress* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAddress> > list;
    typedef IfcTemplatedEntityList<IfcAddress>::it it;
};
class IfcApplication : public IfcBaseClass {
public:
    IfcOrganization* ApplicationDeveloper();
    IfcLabel Version();
    IfcLabel ApplicationFullName();
    IfcIdentifier ApplicationIdentifier();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcApplication (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcApplication* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApplication> > list;
    typedef IfcTemplatedEntityList<IfcApplication>::it it;
};
class IfcAppliedValue : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool hasAppliedValue();
    IfcAppliedValueSelect AppliedValue();
    bool hasUnitBasis();
    IfcMeasureWithUnit* UnitBasis();
    bool hasApplicableDate();
    IfcDateTimeSelect ApplicableDate();
    bool hasFixedUntilDate();
    IfcDateTimeSelect FixedUntilDate();
    SHARED_PTR< IfcTemplatedEntityList<IfcReferencesValueDocument> > ValuesReferenced(); // INVERSE IfcReferencesValueDocument::ReferencingValues
    SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValueRelationship> > ValueOfComponents(); // INVERSE IfcAppliedValueRelationship::ComponentOfTotal
    SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValueRelationship> > IsComponentIn(); // INVERSE IfcAppliedValueRelationship::Components
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAppliedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAppliedValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > list;
    typedef IfcTemplatedEntityList<IfcAppliedValue>::it it;
};
class IfcAppliedValueRelationship : public IfcBaseClass {
public:
    IfcAppliedValue* ComponentOfTotal();
    SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > Components();
    IfcArithmeticOperatorEnum::IfcArithmeticOperatorEnum ArithmeticOperator();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAppliedValueRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAppliedValueRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValueRelationship> > list;
    typedef IfcTemplatedEntityList<IfcAppliedValueRelationship>::it it;
};
class IfcApproval : public IfcBaseClass {
public:
    bool hasDescription();
    IfcText Description();
    IfcDateTimeSelect ApprovalDateTime();
    bool hasApprovalStatus();
    IfcLabel ApprovalStatus();
    bool hasApprovalLevel();
    IfcLabel ApprovalLevel();
    bool hasApprovalQualifier();
    IfcText ApprovalQualifier();
    IfcLabel Name();
    IfcIdentifier Identifier();
    SHARED_PTR< IfcTemplatedEntityList<IfcApprovalActorRelationship> > Actors(); // INVERSE IfcApprovalActorRelationship::Approval
    SHARED_PTR< IfcTemplatedEntityList<IfcApprovalRelationship> > IsRelatedWith(); // INVERSE IfcApprovalRelationship::RelatedApproval
    SHARED_PTR< IfcTemplatedEntityList<IfcApprovalRelationship> > Relates(); // INVERSE IfcApprovalRelationship::RelatingApproval
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcApproval (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcApproval* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApproval> > list;
    typedef IfcTemplatedEntityList<IfcApproval>::it it;
};
class IfcApprovalActorRelationship : public IfcBaseClass {
public:
    IfcActorSelect Actor();
    IfcApproval* Approval();
    IfcActorRole* Role();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcApprovalActorRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcApprovalActorRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApprovalActorRelationship> > list;
    typedef IfcTemplatedEntityList<IfcApprovalActorRelationship>::it it;
};
class IfcApprovalPropertyRelationship : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > ApprovedProperties();
    IfcApproval* Approval();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcApprovalPropertyRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcApprovalPropertyRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApprovalPropertyRelationship> > list;
    typedef IfcTemplatedEntityList<IfcApprovalPropertyRelationship>::it it;
};
class IfcApprovalRelationship : public IfcBaseClass {
public:
    IfcApproval* RelatedApproval();
    IfcApproval* RelatingApproval();
    bool hasDescription();
    IfcText Description();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcApprovalRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcApprovalRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApprovalRelationship> > list;
    typedef IfcTemplatedEntityList<IfcApprovalRelationship>::it it;
};
class IfcBoundaryCondition : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundaryCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundaryCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundaryCondition> > list;
    typedef IfcTemplatedEntityList<IfcBoundaryCondition>::it it;
};
class IfcBoundaryEdgeCondition : public IfcBoundaryCondition {
public:
    bool hasLinearStiffnessByLengthX();
    IfcModulusOfLinearSubgradeReactionMeasure LinearStiffnessByLengthX();
    bool hasLinearStiffnessByLengthY();
    IfcModulusOfLinearSubgradeReactionMeasure LinearStiffnessByLengthY();
    bool hasLinearStiffnessByLengthZ();
    IfcModulusOfLinearSubgradeReactionMeasure LinearStiffnessByLengthZ();
    bool hasRotationalStiffnessByLengthX();
    IfcModulusOfRotationalSubgradeReactionMeasure RotationalStiffnessByLengthX();
    bool hasRotationalStiffnessByLengthY();
    IfcModulusOfRotationalSubgradeReactionMeasure RotationalStiffnessByLengthY();
    bool hasRotationalStiffnessByLengthZ();
    IfcModulusOfRotationalSubgradeReactionMeasure RotationalStiffnessByLengthZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundaryEdgeCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundaryEdgeCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundaryEdgeCondition> > list;
    typedef IfcTemplatedEntityList<IfcBoundaryEdgeCondition>::it it;
};
class IfcBoundaryFaceCondition : public IfcBoundaryCondition {
public:
    bool hasLinearStiffnessByAreaX();
    IfcModulusOfSubgradeReactionMeasure LinearStiffnessByAreaX();
    bool hasLinearStiffnessByAreaY();
    IfcModulusOfSubgradeReactionMeasure LinearStiffnessByAreaY();
    bool hasLinearStiffnessByAreaZ();
    IfcModulusOfSubgradeReactionMeasure LinearStiffnessByAreaZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundaryFaceCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundaryFaceCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundaryFaceCondition> > list;
    typedef IfcTemplatedEntityList<IfcBoundaryFaceCondition>::it it;
};
class IfcBoundaryNodeCondition : public IfcBoundaryCondition {
public:
    bool hasLinearStiffnessX();
    IfcLinearStiffnessMeasure LinearStiffnessX();
    bool hasLinearStiffnessY();
    IfcLinearStiffnessMeasure LinearStiffnessY();
    bool hasLinearStiffnessZ();
    IfcLinearStiffnessMeasure LinearStiffnessZ();
    bool hasRotationalStiffnessX();
    IfcRotationalStiffnessMeasure RotationalStiffnessX();
    bool hasRotationalStiffnessY();
    IfcRotationalStiffnessMeasure RotationalStiffnessY();
    bool hasRotationalStiffnessZ();
    IfcRotationalStiffnessMeasure RotationalStiffnessZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundaryNodeCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundaryNodeCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundaryNodeCondition> > list;
    typedef IfcTemplatedEntityList<IfcBoundaryNodeCondition>::it it;
};
class IfcBoundaryNodeConditionWarping : public IfcBoundaryNodeCondition {
public:
    bool hasWarpingStiffness();
    IfcWarpingMomentMeasure WarpingStiffness();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundaryNodeConditionWarping (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundaryNodeConditionWarping* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundaryNodeConditionWarping> > list;
    typedef IfcTemplatedEntityList<IfcBoundaryNodeConditionWarping>::it it;
};
class IfcCalendarDate : public IfcBaseClass {
public:
    IfcDayInMonthNumber DayComponent();
    IfcMonthInYearNumber MonthComponent();
    IfcYearNumber YearComponent();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCalendarDate (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCalendarDate* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCalendarDate> > list;
    typedef IfcTemplatedEntityList<IfcCalendarDate>::it it;
};
class IfcClassification : public IfcBaseClass {
public:
    IfcLabel Source();
    IfcLabel Edition();
    bool hasEditionDate();
    IfcCalendarDate* EditionDate();
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > Contains(); // INVERSE IfcClassificationItem::ItemOf
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcClassification (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcClassification* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassification> > list;
    typedef IfcTemplatedEntityList<IfcClassification>::it it;
};
class IfcClassificationItem : public IfcBaseClass {
public:
    IfcClassificationNotationFacet* Notation();
    bool hasItemOf();
    IfcClassification* ItemOf();
    IfcLabel Title();
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItemRelationship> > IsClassifiedItemIn(); // INVERSE IfcClassificationItemRelationship::RelatedItems
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItemRelationship> > IsClassifyingItemIn(); // INVERSE IfcClassificationItemRelationship::RelatingItem
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcClassificationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcClassificationItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > list;
    typedef IfcTemplatedEntityList<IfcClassificationItem>::it it;
};
class IfcClassificationItemRelationship : public IfcBaseClass {
public:
    IfcClassificationItem* RelatingItem();
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > RelatedItems();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcClassificationItemRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcClassificationItemRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItemRelationship> > list;
    typedef IfcTemplatedEntityList<IfcClassificationItemRelationship>::it it;
};
class IfcClassificationNotation : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotationFacet> > NotationFacets();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcClassificationNotation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcClassificationNotation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotation> > list;
    typedef IfcTemplatedEntityList<IfcClassificationNotation>::it it;
};
class IfcClassificationNotationFacet : public IfcBaseClass {
public:
    IfcLabel NotationValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcClassificationNotationFacet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcClassificationNotationFacet* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotationFacet> > list;
    typedef IfcTemplatedEntityList<IfcClassificationNotationFacet>::it it;
};
class IfcColourSpecification : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcColourSpecification (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcColourSpecification* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColourSpecification> > list;
    typedef IfcTemplatedEntityList<IfcColourSpecification>::it it;
};
class IfcConnectionGeometry : public IfcBaseClass {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConnectionGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConnectionGeometry* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionGeometry>::it it;
};
class IfcConnectionPointGeometry : public IfcConnectionGeometry {
public:
    IfcPointOrVertexPoint PointOnRelatingElement();
    bool hasPointOnRelatedElement();
    IfcPointOrVertexPoint PointOnRelatedElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConnectionPointGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConnectionPointGeometry* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionPointGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionPointGeometry>::it it;
};
class IfcConnectionPortGeometry : public IfcConnectionGeometry {
public:
    IfcAxis2Placement LocationAtRelatingElement();
    bool hasLocationAtRelatedElement();
    IfcAxis2Placement LocationAtRelatedElement();
    IfcProfileDef* ProfileOfPort();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConnectionPortGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConnectionPortGeometry* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionPortGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionPortGeometry>::it it;
};
class IfcConnectionSurfaceGeometry : public IfcConnectionGeometry {
public:
    IfcSurfaceOrFaceSurface SurfaceOnRelatingElement();
    bool hasSurfaceOnRelatedElement();
    IfcSurfaceOrFaceSurface SurfaceOnRelatedElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConnectionSurfaceGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConnectionSurfaceGeometry* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionSurfaceGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionSurfaceGeometry>::it it;
};
class IfcConstraint : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    IfcConstraintEnum::IfcConstraintEnum ConstraintGrade();
    bool hasConstraintSource();
    IfcLabel ConstraintSource();
    bool hasCreatingActor();
    IfcActorSelect CreatingActor();
    bool hasCreationTime();
    IfcDateTimeSelect CreationTime();
    bool hasUserDefinedGrade();
    IfcLabel UserDefinedGrade();
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraintClassificationRelationship> > ClassifiedAs(); // INVERSE IfcConstraintClassificationRelationship::ClassifiedConstraint
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraintRelationship> > RelatesConstraints(); // INVERSE IfcConstraintRelationship::RelatingConstraint
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraintRelationship> > IsRelatedWith(); // INVERSE IfcConstraintRelationship::RelatedConstraints
    SHARED_PTR< IfcTemplatedEntityList<IfcPropertyConstraintRelationship> > PropertiesForConstraint(); // INVERSE IfcPropertyConstraintRelationship::RelatingConstraint
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraintAggregationRelationship> > Aggregates(); // INVERSE IfcConstraintAggregationRelationship::RelatingConstraint
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraintAggregationRelationship> > IsAggregatedIn(); // INVERSE IfcConstraintAggregationRelationship::RelatedConstraints
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstraint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstraint* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > list;
    typedef IfcTemplatedEntityList<IfcConstraint>::it it;
};
class IfcConstraintAggregationRelationship : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    IfcConstraint* RelatingConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > RelatedConstraints();
    IfcLogicalOperatorEnum::IfcLogicalOperatorEnum LogicalAggregator();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstraintAggregationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstraintAggregationRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraintAggregationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcConstraintAggregationRelationship>::it it;
};
class IfcConstraintClassificationRelationship : public IfcBaseClass {
public:
    IfcConstraint* ClassifiedConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > RelatedClassifications();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstraintClassificationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstraintClassificationRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraintClassificationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcConstraintClassificationRelationship>::it it;
};
class IfcConstraintRelationship : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    IfcConstraint* RelatingConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > RelatedConstraints();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstraintRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstraintRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraintRelationship> > list;
    typedef IfcTemplatedEntityList<IfcConstraintRelationship>::it it;
};
class IfcCoordinatedUniversalTimeOffset : public IfcBaseClass {
public:
    IfcHourInDay HourOffset();
    bool hasMinuteOffset();
    IfcMinuteInHour MinuteOffset();
    IfcAheadOrBehind::IfcAheadOrBehind Sense();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCoordinatedUniversalTimeOffset (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCoordinatedUniversalTimeOffset* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoordinatedUniversalTimeOffset> > list;
    typedef IfcTemplatedEntityList<IfcCoordinatedUniversalTimeOffset>::it it;
};
class IfcCostValue : public IfcAppliedValue {
public:
    IfcLabel CostType();
    bool hasCondition();
    IfcText Condition();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCostValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCostValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCostValue> > list;
    typedef IfcTemplatedEntityList<IfcCostValue>::it it;
};
class IfcCurrencyRelationship : public IfcBaseClass {
public:
    IfcMonetaryUnit* RelatingMonetaryUnit();
    IfcMonetaryUnit* RelatedMonetaryUnit();
    IfcPositiveRatioMeasure ExchangeRate();
    IfcDateAndTime* RateDateTime();
    bool hasRateSource();
    IfcLibraryInformation* RateSource();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurrencyRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurrencyRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurrencyRelationship> > list;
    typedef IfcTemplatedEntityList<IfcCurrencyRelationship>::it it;
};
class IfcCurveStyleFont : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontPattern> > PatternList();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurveStyleFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurveStyleFont* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFont> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyleFont>::it it;
};
class IfcCurveStyleFontAndScaling : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    IfcCurveStyleFontSelect CurveFont();
    IfcPositiveRatioMeasure CurveFontScaling();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurveStyleFontAndScaling (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurveStyleFontAndScaling* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontAndScaling> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyleFontAndScaling>::it it;
};
class IfcCurveStyleFontPattern : public IfcBaseClass {
public:
    IfcLengthMeasure VisibleSegmentLength();
    IfcPositiveLengthMeasure InvisibleSegmentLength();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurveStyleFontPattern (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurveStyleFontPattern* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontPattern> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyleFontPattern>::it it;
};
class IfcDateAndTime : public IfcBaseClass {
public:
    IfcCalendarDate* DateComponent();
    IfcLocalTime* TimeComponent();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDateAndTime (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDateAndTime* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDateAndTime> > list;
    typedef IfcTemplatedEntityList<IfcDateAndTime>::it it;
};
class IfcDerivedUnit : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcDerivedUnitElement> > Elements();
    IfcDerivedUnitEnum::IfcDerivedUnitEnum UnitType();
    bool hasUserDefinedType();
    IfcLabel UserDefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDerivedUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDerivedUnit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDerivedUnit> > list;
    typedef IfcTemplatedEntityList<IfcDerivedUnit>::it it;
};
class IfcDerivedUnitElement : public IfcBaseClass {
public:
    IfcNamedUnit* Unit();
    int Exponent();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDerivedUnitElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDerivedUnitElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDerivedUnitElement> > list;
    typedef IfcTemplatedEntityList<IfcDerivedUnitElement>::it it;
};
class IfcDimensionalExponents : public IfcBaseClass {
public:
    int LengthExponent();
    int MassExponent();
    int TimeExponent();
    int ElectricCurrentExponent();
    int ThermodynamicTemperatureExponent();
    int AmountOfSubstanceExponent();
    int LuminousIntensityExponent();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDimensionalExponents (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDimensionalExponents* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionalExponents> > list;
    typedef IfcTemplatedEntityList<IfcDimensionalExponents>::it it;
};
class IfcDocumentElectronicFormat : public IfcBaseClass {
public:
    bool hasFileExtension();
    IfcLabel FileExtension();
    bool hasMimeContentType();
    IfcLabel MimeContentType();
    bool hasMimeSubtype();
    IfcLabel MimeSubtype();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDocumentElectronicFormat (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDocumentElectronicFormat* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDocumentElectronicFormat> > list;
    typedef IfcTemplatedEntityList<IfcDocumentElectronicFormat>::it it;
};
class IfcDocumentInformation : public IfcBaseClass {
public:
    IfcIdentifier DocumentId();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool hasDocumentReferences();
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentReference> > DocumentReferences();
    bool hasPurpose();
    IfcText Purpose();
    bool hasIntendedUse();
    IfcText IntendedUse();
    bool hasScope();
    IfcText Scope();
    bool hasRevision();
    IfcLabel Revision();
    bool hasDocumentOwner();
    IfcActorSelect DocumentOwner();
    bool hasEditors();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Editors();
    bool hasCreationTime();
    IfcDateAndTime* CreationTime();
    bool hasLastRevisionTime();
    IfcDateAndTime* LastRevisionTime();
    bool hasElectronicFormat();
    IfcDocumentElectronicFormat* ElectronicFormat();
    bool hasValidFrom();
    IfcCalendarDate* ValidFrom();
    bool hasValidUntil();
    IfcCalendarDate* ValidUntil();
    bool hasConfidentiality();
    IfcDocumentConfidentialityEnum::IfcDocumentConfidentialityEnum Confidentiality();
    bool hasStatus();
    IfcDocumentStatusEnum::IfcDocumentStatusEnum Status();
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformationRelationship> > IsPointedTo(); // INVERSE IfcDocumentInformationRelationship::RelatedDocuments
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformationRelationship> > IsPointer(); // INVERSE IfcDocumentInformationRelationship::RelatingDocument
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDocumentInformation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDocumentInformation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > list;
    typedef IfcTemplatedEntityList<IfcDocumentInformation>::it it;
};
class IfcDocumentInformationRelationship : public IfcBaseClass {
public:
    IfcDocumentInformation* RelatingDocument();
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > RelatedDocuments();
    bool hasRelationshipType();
    IfcLabel RelationshipType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDocumentInformationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDocumentInformationRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcDocumentInformationRelationship>::it it;
};
class IfcDraughtingCalloutRelationship : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    IfcDraughtingCallout* RelatingDraughtingCallout();
    IfcDraughtingCallout* RelatedDraughtingCallout();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDraughtingCalloutRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDraughtingCalloutRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCalloutRelationship> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingCalloutRelationship>::it it;
};
class IfcEnvironmentalImpactValue : public IfcAppliedValue {
public:
    IfcLabel ImpactType();
    IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategoryEnum Category();
    bool hasUserDefinedCategory();
    IfcLabel UserDefinedCategory();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEnvironmentalImpactValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEnvironmentalImpactValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEnvironmentalImpactValue> > list;
    typedef IfcTemplatedEntityList<IfcEnvironmentalImpactValue>::it it;
};
class IfcExternalReference : public IfcBaseClass {
public:
    bool hasLocation();
    IfcLabel Location();
    bool hasItemReference();
    IfcIdentifier ItemReference();
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcExternalReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcExternalReference* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternalReference> > list;
    typedef IfcTemplatedEntityList<IfcExternalReference>::it it;
};
class IfcExternallyDefinedHatchStyle : public IfcExternalReference {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcExternallyDefinedHatchStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcExternallyDefinedHatchStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedHatchStyle> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedHatchStyle>::it it;
};
class IfcExternallyDefinedSurfaceStyle : public IfcExternalReference {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcExternallyDefinedSurfaceStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcExternallyDefinedSurfaceStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedSurfaceStyle> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedSurfaceStyle>::it it;
};
class IfcExternallyDefinedSymbol : public IfcExternalReference {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcExternallyDefinedSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcExternallyDefinedSymbol* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedSymbol> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedSymbol>::it it;
};
class IfcExternallyDefinedTextFont : public IfcExternalReference {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcExternallyDefinedTextFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcExternallyDefinedTextFont* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedTextFont> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedTextFont>::it it;
};
class IfcGridAxis : public IfcBaseClass {
public:
    bool hasAxisTag();
    IfcLabel AxisTag();
    IfcCurve* AxisCurve();
    IfcBoolean SameSense();
    SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > PartOfW(); // INVERSE IfcGrid::WAxes
    SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > PartOfV(); // INVERSE IfcGrid::VAxes
    SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > PartOfU(); // INVERSE IfcGrid::UAxes
    SHARED_PTR< IfcTemplatedEntityList<IfcVirtualGridIntersection> > HasIntersections(); // INVERSE IfcVirtualGridIntersection::IntersectingAxes
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGridAxis (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGridAxis* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > list;
    typedef IfcTemplatedEntityList<IfcGridAxis>::it it;
};
class IfcIrregularTimeSeriesValue : public IfcBaseClass {
public:
    IfcDateTimeSelect TimeStamp();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ListValues();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcIrregularTimeSeriesValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcIrregularTimeSeriesValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeriesValue> > list;
    typedef IfcTemplatedEntityList<IfcIrregularTimeSeriesValue>::it it;
};
class IfcLibraryInformation : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasVersion();
    IfcLabel Version();
    bool hasPublisher();
    IfcOrganization* Publisher();
    bool hasVersionDate();
    IfcCalendarDate* VersionDate();
    bool hasLibraryReference();
    SHARED_PTR< IfcTemplatedEntityList<IfcLibraryReference> > LibraryReference();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLibraryInformation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLibraryInformation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLibraryInformation> > list;
    typedef IfcTemplatedEntityList<IfcLibraryInformation>::it it;
};
class IfcLibraryReference : public IfcExternalReference {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcLibraryInformation> > ReferenceIntoLibrary(); // INVERSE IfcLibraryInformation::LibraryReference
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLibraryReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLibraryReference* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLibraryReference> > list;
    typedef IfcTemplatedEntityList<IfcLibraryReference>::it it;
};
class IfcLightDistributionData : public IfcBaseClass {
public:
    IfcPlaneAngleMeasure MainPlaneAngle();
    std::vector<IfcPlaneAngleMeasure> /*[1:?]*/ SecondaryPlaneAngle();
    std::vector<IfcLuminousIntensityDistributionMeasure> /*[1:?]*/ LuminousIntensity();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightDistributionData (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightDistributionData* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightDistributionData> > list;
    typedef IfcTemplatedEntityList<IfcLightDistributionData>::it it;
};
class IfcLightIntensityDistribution : public IfcBaseClass {
public:
    IfcLightDistributionCurveEnum::IfcLightDistributionCurveEnum LightDistributionCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcLightDistributionData> > DistributionData();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightIntensityDistribution (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightIntensityDistribution* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightIntensityDistribution> > list;
    typedef IfcTemplatedEntityList<IfcLightIntensityDistribution>::it it;
};
class IfcLocalTime : public IfcBaseClass {
public:
    IfcHourInDay HourComponent();
    bool hasMinuteComponent();
    IfcMinuteInHour MinuteComponent();
    bool hasSecondComponent();
    IfcSecondInMinute SecondComponent();
    bool hasZone();
    IfcCoordinatedUniversalTimeOffset* Zone();
    bool hasDaylightSavingOffset();
    IfcDaylightSavingHour DaylightSavingOffset();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLocalTime (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLocalTime* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLocalTime> > list;
    typedef IfcTemplatedEntityList<IfcLocalTime>::it it;
};
class IfcMaterial : public IfcBaseClass {
public:
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialDefinitionRepresentation> > HasRepresentation(); // INVERSE IfcMaterialDefinitionRepresentation::RepresentedMaterial
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialClassificationRelationship> > ClassifiedAs(); // INVERSE IfcMaterialClassificationRelationship::ClassifiedMaterial
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterial (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterial* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterial> > list;
    typedef IfcTemplatedEntityList<IfcMaterial>::it it;
};
class IfcMaterialClassificationRelationship : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > MaterialClassifications();
    IfcMaterial* ClassifiedMaterial();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterialClassificationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterialClassificationRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialClassificationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcMaterialClassificationRelationship>::it it;
};
class IfcMaterialLayer : public IfcBaseClass {
public:
    bool hasMaterial();
    IfcMaterial* Material();
    IfcPositiveLengthMeasure LayerThickness();
    bool hasIsVentilated();
    IfcLogical IsVentilated();
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayerSet> > ToMaterialLayerSet(); // INVERSE IfcMaterialLayerSet::MaterialLayers
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterialLayer (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterialLayer* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayer> > list;
    typedef IfcTemplatedEntityList<IfcMaterialLayer>::it it;
};
class IfcMaterialLayerSet : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayer> > MaterialLayers();
    bool hasLayerSetName();
    IfcLabel LayerSetName();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterialLayerSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterialLayerSet* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayerSet> > list;
    typedef IfcTemplatedEntityList<IfcMaterialLayerSet>::it it;
};
class IfcMaterialLayerSetUsage : public IfcBaseClass {
public:
    IfcMaterialLayerSet* ForLayerSet();
    IfcLayerSetDirectionEnum::IfcLayerSetDirectionEnum LayerSetDirection();
    IfcDirectionSenseEnum::IfcDirectionSenseEnum DirectionSense();
    IfcLengthMeasure OffsetFromReferenceLine();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterialLayerSetUsage (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterialLayerSetUsage* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayerSetUsage> > list;
    typedef IfcTemplatedEntityList<IfcMaterialLayerSetUsage>::it it;
};
class IfcMaterialList : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterial> > Materials();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterialList (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterialList* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialList> > list;
    typedef IfcTemplatedEntityList<IfcMaterialList>::it it;
};
class IfcMaterialProperties : public IfcBaseClass {
public:
    IfcMaterial* Material();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcMaterialProperties>::it it;
};
class IfcMeasureWithUnit : public IfcBaseClass {
public:
    IfcValue ValueComponent();
    IfcUnit UnitComponent();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMeasureWithUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMeasureWithUnit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMeasureWithUnit> > list;
    typedef IfcTemplatedEntityList<IfcMeasureWithUnit>::it it;
};
class IfcMechanicalMaterialProperties : public IfcMaterialProperties {
public:
    bool hasDynamicViscosity();
    IfcDynamicViscosityMeasure DynamicViscosity();
    bool hasYoungModulus();
    IfcModulusOfElasticityMeasure YoungModulus();
    bool hasShearModulus();
    IfcModulusOfElasticityMeasure ShearModulus();
    bool hasPoissonRatio();
    IfcPositiveRatioMeasure PoissonRatio();
    bool hasThermalExpansionCoefficient();
    IfcThermalExpansionCoefficientMeasure ThermalExpansionCoefficient();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMechanicalMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMechanicalMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalMaterialProperties>::it it;
};
class IfcMechanicalSteelMaterialProperties : public IfcMechanicalMaterialProperties {
public:
    bool hasYieldStress();
    IfcPressureMeasure YieldStress();
    bool hasUltimateStress();
    IfcPressureMeasure UltimateStress();
    bool hasUltimateStrain();
    IfcPositiveRatioMeasure UltimateStrain();
    bool hasHardeningModule();
    IfcModulusOfElasticityMeasure HardeningModule();
    bool hasProportionalStress();
    IfcPressureMeasure ProportionalStress();
    bool hasPlasticStrain();
    IfcPositiveRatioMeasure PlasticStrain();
    bool hasRelaxations();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelaxation> > Relaxations();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMechanicalSteelMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMechanicalSteelMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalSteelMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalSteelMaterialProperties>::it it;
};
class IfcMetric : public IfcConstraint {
public:
    IfcBenchmarkEnum::IfcBenchmarkEnum Benchmark();
    bool hasValueSource();
    IfcLabel ValueSource();
    IfcMetricValueSelect DataValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMetric (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMetric* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMetric> > list;
    typedef IfcTemplatedEntityList<IfcMetric>::it it;
};
class IfcMonetaryUnit : public IfcBaseClass {
public:
    IfcCurrencyEnum::IfcCurrencyEnum Currency();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMonetaryUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMonetaryUnit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMonetaryUnit> > list;
    typedef IfcTemplatedEntityList<IfcMonetaryUnit>::it it;
};
class IfcNamedUnit : public IfcBaseClass {
public:
    IfcDimensionalExponents* Dimensions();
    IfcUnitEnum::IfcUnitEnum UnitType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcNamedUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcNamedUnit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcNamedUnit> > list;
    typedef IfcTemplatedEntityList<IfcNamedUnit>::it it;
};
class IfcObjectPlacement : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > PlacesObject(); // INVERSE IfcProduct::ObjectPlacement
    SHARED_PTR< IfcTemplatedEntityList<IfcLocalPlacement> > ReferencedByPlacements(); // INVERSE IfcLocalPlacement::PlacementRelTo
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcObjectPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcObjectPlacement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcObjectPlacement> > list;
    typedef IfcTemplatedEntityList<IfcObjectPlacement>::it it;
};
class IfcObjective : public IfcConstraint {
public:
    bool hasBenchmarkValues();
    IfcMetric* BenchmarkValues();
    bool hasResultValues();
    IfcMetric* ResultValues();
    IfcObjectiveEnum::IfcObjectiveEnum ObjectiveQualifier();
    bool hasUserDefinedQualifier();
    IfcLabel UserDefinedQualifier();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcObjective (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcObjective* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcObjective> > list;
    typedef IfcTemplatedEntityList<IfcObjective>::it it;
};
class IfcOpticalMaterialProperties : public IfcMaterialProperties {
public:
    bool hasVisibleTransmittance();
    IfcPositiveRatioMeasure VisibleTransmittance();
    bool hasSolarTransmittance();
    IfcPositiveRatioMeasure SolarTransmittance();
    bool hasThermalIrTransmittance();
    IfcPositiveRatioMeasure ThermalIrTransmittance();
    bool hasThermalIrEmissivityBack();
    IfcPositiveRatioMeasure ThermalIrEmissivityBack();
    bool hasThermalIrEmissivityFront();
    IfcPositiveRatioMeasure ThermalIrEmissivityFront();
    bool hasVisibleReflectanceBack();
    IfcPositiveRatioMeasure VisibleReflectanceBack();
    bool hasVisibleReflectanceFront();
    IfcPositiveRatioMeasure VisibleReflectanceFront();
    bool hasSolarReflectanceFront();
    IfcPositiveRatioMeasure SolarReflectanceFront();
    bool hasSolarReflectanceBack();
    IfcPositiveRatioMeasure SolarReflectanceBack();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOpticalMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOpticalMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOpticalMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcOpticalMaterialProperties>::it it;
};
class IfcOrganization : public IfcBaseClass {
public:
    bool hasId();
    IfcIdentifier Id();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool hasRoles();
    SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > Roles();
    bool hasAddresses();
    SHARED_PTR< IfcTemplatedEntityList<IfcAddress> > Addresses();
    SHARED_PTR< IfcTemplatedEntityList<IfcOrganizationRelationship> > IsRelatedBy(); // INVERSE IfcOrganizationRelationship::RelatedOrganizations
    SHARED_PTR< IfcTemplatedEntityList<IfcOrganizationRelationship> > Relates(); // INVERSE IfcOrganizationRelationship::RelatingOrganization
    SHARED_PTR< IfcTemplatedEntityList<IfcPersonAndOrganization> > Engages(); // INVERSE IfcPersonAndOrganization::TheOrganization
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOrganization (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOrganization* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrganization> > list;
    typedef IfcTemplatedEntityList<IfcOrganization>::it it;
};
class IfcOrganizationRelationship : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    IfcOrganization* RelatingOrganization();
    SHARED_PTR< IfcTemplatedEntityList<IfcOrganization> > RelatedOrganizations();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOrganizationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOrganizationRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrganizationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcOrganizationRelationship>::it it;
};
class IfcOwnerHistory : public IfcBaseClass {
public:
    IfcPersonAndOrganization* OwningUser();
    IfcApplication* OwningApplication();
    bool hasState();
    IfcStateEnum::IfcStateEnum State();
    IfcChangeActionEnum::IfcChangeActionEnum ChangeAction();
    bool hasLastModifiedDate();
    IfcTimeStamp LastModifiedDate();
    bool hasLastModifyingUser();
    IfcPersonAndOrganization* LastModifyingUser();
    bool hasLastModifyingApplication();
    IfcApplication* LastModifyingApplication();
    IfcTimeStamp CreationDate();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOwnerHistory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOwnerHistory* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOwnerHistory> > list;
    typedef IfcTemplatedEntityList<IfcOwnerHistory>::it it;
};
class IfcPerson : public IfcBaseClass {
public:
    bool hasId();
    IfcIdentifier Id();
    bool hasFamilyName();
    IfcLabel FamilyName();
    bool hasGivenName();
    IfcLabel GivenName();
    bool hasMiddleNames();
    std::vector<IfcLabel> /*[1:?]*/ MiddleNames();
    bool hasPrefixTitles();
    std::vector<IfcLabel> /*[1:?]*/ PrefixTitles();
    bool hasSuffixTitles();
    std::vector<IfcLabel> /*[1:?]*/ SuffixTitles();
    bool hasRoles();
    SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > Roles();
    bool hasAddresses();
    SHARED_PTR< IfcTemplatedEntityList<IfcAddress> > Addresses();
    SHARED_PTR< IfcTemplatedEntityList<IfcPersonAndOrganization> > EngagedIn(); // INVERSE IfcPersonAndOrganization::ThePerson
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPerson (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPerson* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > list;
    typedef IfcTemplatedEntityList<IfcPerson>::it it;
};
class IfcPersonAndOrganization : public IfcBaseClass {
public:
    IfcPerson* ThePerson();
    IfcOrganization* TheOrganization();
    bool hasRoles();
    SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > Roles();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPersonAndOrganization (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPersonAndOrganization* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPersonAndOrganization> > list;
    typedef IfcTemplatedEntityList<IfcPersonAndOrganization>::it it;
};
class IfcPhysicalQuantity : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalComplexQuantity> > PartOfComplex(); // INVERSE IfcPhysicalComplexQuantity::HasQuantities
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPhysicalQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPhysicalQuantity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > list;
    typedef IfcTemplatedEntityList<IfcPhysicalQuantity>::it it;
};
class IfcPhysicalSimpleQuantity : public IfcPhysicalQuantity {
public:
    bool hasUnit();
    IfcNamedUnit* Unit();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPhysicalSimpleQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPhysicalSimpleQuantity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalSimpleQuantity> > list;
    typedef IfcTemplatedEntityList<IfcPhysicalSimpleQuantity>::it it;
};
class IfcPostalAddress : public IfcAddress {
public:
    bool hasInternalLocation();
    IfcLabel InternalLocation();
    bool hasAddressLines();
    std::vector<IfcLabel> /*[1:?]*/ AddressLines();
    bool hasPostalBox();
    IfcLabel PostalBox();
    bool hasTown();
    IfcLabel Town();
    bool hasRegion();
    IfcLabel Region();
    bool hasPostalCode();
    IfcLabel PostalCode();
    bool hasCountry();
    IfcLabel Country();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPostalAddress (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPostalAddress* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPostalAddress> > list;
    typedef IfcTemplatedEntityList<IfcPostalAddress>::it it;
};
class IfcPreDefinedItem : public IfcBaseClass {
public:
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedItem> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedItem>::it it;
};
class IfcPreDefinedSymbol : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedSymbol* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedSymbol>::it it;
};
class IfcPreDefinedTerminatorSymbol : public IfcPreDefinedSymbol {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedTerminatorSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedTerminatorSymbol* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedTerminatorSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedTerminatorSymbol>::it it;
};
class IfcPreDefinedTextFont : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedTextFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedTextFont* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedTextFont> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedTextFont>::it it;
};
class IfcPresentationLayerAssignment : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > AssignedItems();
    bool hasIdentifier();
    IfcIdentifier Identifier();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPresentationLayerAssignment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPresentationLayerAssignment* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerAssignment> > list;
    typedef IfcTemplatedEntityList<IfcPresentationLayerAssignment>::it it;
};
class IfcPresentationLayerWithStyle : public IfcPresentationLayerAssignment {
public:
    bool LayerOn();
    bool LayerFrozen();
    bool LayerBlocked();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > LayerStyles();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPresentationLayerWithStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPresentationLayerWithStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerWithStyle> > list;
    typedef IfcTemplatedEntityList<IfcPresentationLayerWithStyle>::it it;
};
class IfcPresentationStyle : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPresentationStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPresentationStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPresentationStyle> > list;
    typedef IfcTemplatedEntityList<IfcPresentationStyle>::it it;
};
class IfcPresentationStyleAssignment : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Styles();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPresentationStyleAssignment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPresentationStyleAssignment* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPresentationStyleAssignment> > list;
    typedef IfcTemplatedEntityList<IfcPresentationStyleAssignment>::it it;
};
class IfcProductRepresentation : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentation> > Representations();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProductRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProductRepresentation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProductRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcProductRepresentation>::it it;
};
class IfcProductsOfCombustionProperties : public IfcMaterialProperties {
public:
    bool hasSpecificHeatCapacity();
    IfcSpecificHeatCapacityMeasure SpecificHeatCapacity();
    bool hasN20Content();
    IfcPositiveRatioMeasure N20Content();
    bool hasCOContent();
    IfcPositiveRatioMeasure COContent();
    bool hasCO2Content();
    IfcPositiveRatioMeasure CO2Content();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProductsOfCombustionProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProductsOfCombustionProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProductsOfCombustionProperties> > list;
    typedef IfcTemplatedEntityList<IfcProductsOfCombustionProperties>::it it;
};
class IfcProfileDef : public IfcBaseClass {
public:
    IfcProfileTypeEnum::IfcProfileTypeEnum ProfileType();
    bool hasProfileName();
    IfcLabel ProfileName();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcProfileDef>::it it;
};
class IfcProfileProperties : public IfcBaseClass {
public:
    bool hasProfileName();
    IfcLabel ProfileName();
    bool hasProfileDefinition();
    IfcProfileDef* ProfileDefinition();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProfileProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcProfileProperties>::it it;
};
class IfcProperty : public IfcBaseClass {
public:
    IfcIdentifier Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR< IfcTemplatedEntityList<IfcPropertyDependencyRelationship> > PropertyForDependance(); // INVERSE IfcPropertyDependencyRelationship::DependingProperty
    SHARED_PTR< IfcTemplatedEntityList<IfcPropertyDependencyRelationship> > PropertyDependsOn(); // INVERSE IfcPropertyDependencyRelationship::DependantProperty
    SHARED_PTR< IfcTemplatedEntityList<IfcComplexProperty> > PartOfComplex(); // INVERSE IfcComplexProperty::HasProperties
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProperty (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProperty* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > list;
    typedef IfcTemplatedEntityList<IfcProperty>::it it;
};
class IfcPropertyConstraintRelationship : public IfcBaseClass {
public:
    IfcConstraint* RelatingConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > RelatedProperties();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyConstraintRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyConstraintRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyConstraintRelationship> > list;
    typedef IfcTemplatedEntityList<IfcPropertyConstraintRelationship>::it it;
};
class IfcPropertyDependencyRelationship : public IfcBaseClass {
public:
    IfcProperty* DependingProperty();
    IfcProperty* DependantProperty();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool hasExpression();
    IfcText Expression();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyDependencyRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyDependencyRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyDependencyRelationship> > list;
    typedef IfcTemplatedEntityList<IfcPropertyDependencyRelationship>::it it;
};
class IfcPropertyEnumeration : public IfcBaseClass {
public:
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > EnumerationValues();
    bool hasUnit();
    IfcUnit Unit();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyEnumeration (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyEnumeration* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyEnumeration> > list;
    typedef IfcTemplatedEntityList<IfcPropertyEnumeration>::it it;
};
class IfcQuantityArea : public IfcPhysicalSimpleQuantity {
public:
    IfcAreaMeasure AreaValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcQuantityArea (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcQuantityArea* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityArea> > list;
    typedef IfcTemplatedEntityList<IfcQuantityArea>::it it;
};
class IfcQuantityCount : public IfcPhysicalSimpleQuantity {
public:
    IfcCountMeasure CountValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcQuantityCount (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcQuantityCount* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityCount> > list;
    typedef IfcTemplatedEntityList<IfcQuantityCount>::it it;
};
class IfcQuantityLength : public IfcPhysicalSimpleQuantity {
public:
    IfcLengthMeasure LengthValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcQuantityLength (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcQuantityLength* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityLength> > list;
    typedef IfcTemplatedEntityList<IfcQuantityLength>::it it;
};
class IfcQuantityTime : public IfcPhysicalSimpleQuantity {
public:
    IfcTimeMeasure TimeValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcQuantityTime (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcQuantityTime* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityTime> > list;
    typedef IfcTemplatedEntityList<IfcQuantityTime>::it it;
};
class IfcQuantityVolume : public IfcPhysicalSimpleQuantity {
public:
    IfcVolumeMeasure VolumeValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcQuantityVolume (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcQuantityVolume* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityVolume> > list;
    typedef IfcTemplatedEntityList<IfcQuantityVolume>::it it;
};
class IfcQuantityWeight : public IfcPhysicalSimpleQuantity {
public:
    IfcMassMeasure WeightValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcQuantityWeight (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcQuantityWeight* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityWeight> > list;
    typedef IfcTemplatedEntityList<IfcQuantityWeight>::it it;
};
class IfcReferencesValueDocument : public IfcBaseClass {
public:
    IfcDocumentSelect ReferencedDocument();
    SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > ReferencingValues();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcReferencesValueDocument (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcReferencesValueDocument* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReferencesValueDocument> > list;
    typedef IfcTemplatedEntityList<IfcReferencesValueDocument>::it it;
};
class IfcReinforcementBarProperties : public IfcBaseClass {
public:
    IfcAreaMeasure TotalCrossSectionArea();
    IfcLabel SteelGrade();
    bool hasBarSurface();
    IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum BarSurface();
    bool hasEffectiveDepth();
    IfcLengthMeasure EffectiveDepth();
    bool hasNominalBarDiameter();
    IfcPositiveLengthMeasure NominalBarDiameter();
    bool hasBarCount();
    IfcCountMeasure BarCount();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcReinforcementBarProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcReinforcementBarProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementBarProperties> > list;
    typedef IfcTemplatedEntityList<IfcReinforcementBarProperties>::it it;
};
class IfcRelaxation : public IfcBaseClass {
public:
    IfcNormalisedRatioMeasure RelaxationValue();
    IfcNormalisedRatioMeasure InitialStress();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelaxation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelaxation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelaxation> > list;
    typedef IfcTemplatedEntityList<IfcRelaxation>::it it;
};
class IfcRepresentation : public IfcBaseClass {
public:
    IfcRepresentationContext* ContextOfItems();
    bool hasRepresentationIdentifier();
    IfcLabel RepresentationIdentifier();
    bool hasRepresentationType();
    IfcLabel RepresentationType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationItem> > Items();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationMap> > RepresentationMap(); // INVERSE IfcRepresentationMap::MappedRepresentation
    SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerAssignment> > LayerAssignments(); // INVERSE IfcPresentationLayerAssignment::AssignedItems
    SHARED_PTR< IfcTemplatedEntityList<IfcProductRepresentation> > OfProductRepresentation(); // INVERSE IfcProductRepresentation::Representations
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRepresentation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcRepresentation>::it it;
};
class IfcRepresentationContext : public IfcBaseClass {
public:
    bool hasContextIdentifier();
    IfcLabel ContextIdentifier();
    bool hasContextType();
    IfcLabel ContextType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentation> > RepresentationsInContext(); // INVERSE IfcRepresentation::ContextOfItems
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRepresentationContext (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRepresentationContext* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationContext> > list;
    typedef IfcTemplatedEntityList<IfcRepresentationContext>::it it;
};
class IfcRepresentationItem : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerAssignment> > LayerAssignments(); // INVERSE IfcPresentationLayerAssignment::AssignedItems
    SHARED_PTR< IfcTemplatedEntityList<IfcStyledItem> > StyledByItem(); // INVERSE IfcStyledItem::Item
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRepresentationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRepresentationItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationItem> > list;
    typedef IfcTemplatedEntityList<IfcRepresentationItem>::it it;
};
class IfcRepresentationMap : public IfcBaseClass {
public:
    IfcAxis2Placement MappingOrigin();
    IfcRepresentation* MappedRepresentation();
    SHARED_PTR< IfcTemplatedEntityList<IfcMappedItem> > MapUsage(); // INVERSE IfcMappedItem::MappingSource
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRepresentationMap (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRepresentationMap* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationMap> > list;
    typedef IfcTemplatedEntityList<IfcRepresentationMap>::it it;
};
class IfcRibPlateProfileProperties : public IfcProfileProperties {
public:
    bool hasThickness();
    IfcPositiveLengthMeasure Thickness();
    bool hasRibHeight();
    IfcPositiveLengthMeasure RibHeight();
    bool hasRibWidth();
    IfcPositiveLengthMeasure RibWidth();
    bool hasRibSpacing();
    IfcPositiveLengthMeasure RibSpacing();
    IfcRibPlateDirectionEnum::IfcRibPlateDirectionEnum Direction();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRibPlateProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRibPlateProfileProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRibPlateProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcRibPlateProfileProperties>::it it;
};
class IfcRoot : public IfcBaseClass {
public:
    IfcGloballyUniqueId GlobalId();
    IfcOwnerHistory* OwnerHistory();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRoot (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRoot* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoot> > list;
    typedef IfcTemplatedEntityList<IfcRoot>::it it;
};
class IfcSIUnit : public IfcNamedUnit {
public:
    bool hasPrefix();
    IfcSIPrefix::IfcSIPrefix Prefix();
    IfcSIUnitName::IfcSIUnitName Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSIUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSIUnit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSIUnit> > list;
    typedef IfcTemplatedEntityList<IfcSIUnit>::it it;
};
class IfcSectionProperties : public IfcBaseClass {
public:
    IfcSectionTypeEnum::IfcSectionTypeEnum SectionType();
    IfcProfileDef* StartProfile();
    bool hasEndProfile();
    IfcProfileDef* EndProfile();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSectionProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSectionProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSectionProperties> > list;
    typedef IfcTemplatedEntityList<IfcSectionProperties>::it it;
};
class IfcSectionReinforcementProperties : public IfcBaseClass {
public:
    IfcLengthMeasure LongitudinalStartPosition();
    IfcLengthMeasure LongitudinalEndPosition();
    bool hasTransversePosition();
    IfcLengthMeasure TransversePosition();
    IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum ReinforcementRole();
    IfcSectionProperties* SectionDefinition();
    SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementBarProperties> > CrossSectionReinforcementDefinitions();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSectionReinforcementProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSectionReinforcementProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSectionReinforcementProperties> > list;
    typedef IfcTemplatedEntityList<IfcSectionReinforcementProperties>::it it;
};
class IfcShapeAspect : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcShapeModel> > ShapeRepresentations();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool ProductDefinitional();
    IfcProductDefinitionShape* PartOfProductDefinitionShape();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcShapeAspect (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcShapeAspect* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcShapeAspect> > list;
    typedef IfcTemplatedEntityList<IfcShapeAspect>::it it;
};
class IfcShapeModel : public IfcRepresentation {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcShapeAspect> > OfShapeAspect(); // INVERSE IfcShapeAspect::ShapeRepresentations
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcShapeModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcShapeModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcShapeModel> > list;
    typedef IfcTemplatedEntityList<IfcShapeModel>::it it;
};
class IfcShapeRepresentation : public IfcShapeModel {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcShapeRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcShapeRepresentation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcShapeRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcShapeRepresentation>::it it;
};
class IfcSimpleProperty : public IfcProperty {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSimpleProperty (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSimpleProperty* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSimpleProperty> > list;
    typedef IfcTemplatedEntityList<IfcSimpleProperty>::it it;
};
class IfcStructuralConnectionCondition : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralConnectionCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralConnectionCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralConnectionCondition> > list;
    typedef IfcTemplatedEntityList<IfcStructuralConnectionCondition>::it it;
};
class IfcStructuralLoad : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoad (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoad* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoad>::it it;
};
class IfcStructuralLoadStatic : public IfcStructuralLoad {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadStatic (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadStatic* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadStatic> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadStatic>::it it;
};
class IfcStructuralLoadTemperature : public IfcStructuralLoadStatic {
public:
    bool hasDeltaT_Constant();
    IfcThermodynamicTemperatureMeasure DeltaT_Constant();
    bool hasDeltaT_Y();
    IfcThermodynamicTemperatureMeasure DeltaT_Y();
    bool hasDeltaT_Z();
    IfcThermodynamicTemperatureMeasure DeltaT_Z();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadTemperature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadTemperature* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadTemperature> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadTemperature>::it it;
};
class IfcStyleModel : public IfcRepresentation {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStyleModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStyleModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStyleModel> > list;
    typedef IfcTemplatedEntityList<IfcStyleModel>::it it;
};
class IfcStyledItem : public IfcRepresentationItem {
public:
    bool hasItem();
    IfcRepresentationItem* Item();
    SHARED_PTR< IfcTemplatedEntityList<IfcPresentationStyleAssignment> > Styles();
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStyledItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStyledItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStyledItem> > list;
    typedef IfcTemplatedEntityList<IfcStyledItem>::it it;
};
class IfcStyledRepresentation : public IfcStyleModel {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStyledRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStyledRepresentation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStyledRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcStyledRepresentation>::it it;
};
class IfcSurfaceStyle : public IfcPresentationStyle {
public:
    IfcSurfaceSide::IfcSurfaceSide Side();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Styles();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyle> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyle>::it it;
};
class IfcSurfaceStyleLighting : public IfcBaseClass {
public:
    IfcColourRgb* DiffuseTransmissionColour();
    IfcColourRgb* DiffuseReflectionColour();
    IfcColourRgb* TransmissionColour();
    IfcColourRgb* ReflectanceColour();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceStyleLighting (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceStyleLighting* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleLighting> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleLighting>::it it;
};
class IfcSurfaceStyleRefraction : public IfcBaseClass {
public:
    bool hasRefractionIndex();
    IfcReal RefractionIndex();
    bool hasDispersionFactor();
    IfcReal DispersionFactor();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceStyleRefraction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceStyleRefraction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleRefraction> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleRefraction>::it it;
};
class IfcSurfaceStyleShading : public IfcBaseClass {
public:
    IfcColourRgb* SurfaceColour();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceStyleShading (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceStyleShading* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleShading> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleShading>::it it;
};
class IfcSurfaceStyleWithTextures : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceTexture> > Textures();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceStyleWithTextures (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceStyleWithTextures* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleWithTextures> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleWithTextures>::it it;
};
class IfcSurfaceTexture : public IfcBaseClass {
public:
    bool RepeatS();
    bool RepeatT();
    IfcSurfaceTextureEnum::IfcSurfaceTextureEnum TextureType();
    bool hasTextureTransform();
    IfcCartesianTransformationOperator2D* TextureTransform();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceTexture* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceTexture> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceTexture>::it it;
};
class IfcSymbolStyle : public IfcPresentationStyle {
public:
    IfcSymbolStyleSelect StyleOfSymbol();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSymbolStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSymbolStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSymbolStyle> > list;
    typedef IfcTemplatedEntityList<IfcSymbolStyle>::it it;
};
class IfcTable : public IfcBaseClass {
public:
    std::string Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcTableRow> > Rows();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTable (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTable* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTable> > list;
    typedef IfcTemplatedEntityList<IfcTable>::it it;
};
class IfcTableRow : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > RowCells();
    bool IsHeading();
    SHARED_PTR< IfcTemplatedEntityList<IfcTable> > OfTable(); // INVERSE IfcTable::Rows
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTableRow (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTableRow* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTableRow> > list;
    typedef IfcTemplatedEntityList<IfcTableRow>::it it;
};
class IfcTelecomAddress : public IfcAddress {
public:
    bool hasTelephoneNumbers();
    std::vector<IfcLabel> /*[1:?]*/ TelephoneNumbers();
    bool hasFacsimileNumbers();
    std::vector<IfcLabel> /*[1:?]*/ FacsimileNumbers();
    bool hasPagerNumber();
    IfcLabel PagerNumber();
    bool hasElectronicMailAddresses();
    std::vector<IfcLabel> /*[1:?]*/ ElectronicMailAddresses();
    bool hasWWWHomePageURL();
    IfcLabel WWWHomePageURL();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTelecomAddress (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTelecomAddress* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTelecomAddress> > list;
    typedef IfcTemplatedEntityList<IfcTelecomAddress>::it it;
};
class IfcTextStyle : public IfcPresentationStyle {
public:
    bool hasTextCharacterAppearance();
    IfcCharacterStyleSelect TextCharacterAppearance();
    bool hasTextStyle();
    IfcTextStyleSelect TextStyle();
    IfcTextFontSelect TextFontStyle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextStyle> > list;
    typedef IfcTemplatedEntityList<IfcTextStyle>::it it;
};
class IfcTextStyleFontModel : public IfcPreDefinedTextFont {
public:
    bool hasFontFamily();
    std::vector<IfcTextFontName> /*[1:?]*/ FontFamily();
    bool hasFontStyle();
    IfcFontStyle FontStyle();
    bool hasFontVariant();
    IfcFontVariant FontVariant();
    bool hasFontWeight();
    IfcFontWeight FontWeight();
    IfcSizeSelect FontSize();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextStyleFontModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextStyleFontModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextStyleFontModel> > list;
    typedef IfcTemplatedEntityList<IfcTextStyleFontModel>::it it;
};
class IfcTextStyleForDefinedFont : public IfcBaseClass {
public:
    IfcColour Colour();
    bool hasBackgroundColour();
    IfcColour BackgroundColour();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextStyleForDefinedFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextStyleForDefinedFont* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextStyleForDefinedFont> > list;
    typedef IfcTemplatedEntityList<IfcTextStyleForDefinedFont>::it it;
};
class IfcTextStyleTextModel : public IfcBaseClass {
public:
    bool hasTextIndent();
    IfcSizeSelect TextIndent();
    bool hasTextAlign();
    IfcTextAlignment TextAlign();
    bool hasTextDecoration();
    IfcTextDecoration TextDecoration();
    bool hasLetterSpacing();
    IfcSizeSelect LetterSpacing();
    bool hasWordSpacing();
    IfcSizeSelect WordSpacing();
    bool hasTextTransform();
    IfcTextTransformation TextTransform();
    bool hasLineHeight();
    IfcSizeSelect LineHeight();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextStyleTextModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextStyleTextModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextStyleTextModel> > list;
    typedef IfcTemplatedEntityList<IfcTextStyleTextModel>::it it;
};
class IfcTextStyleWithBoxCharacteristics : public IfcBaseClass {
public:
    bool hasBoxHeight();
    IfcPositiveLengthMeasure BoxHeight();
    bool hasBoxWidth();
    IfcPositiveLengthMeasure BoxWidth();
    bool hasBoxSlantAngle();
    IfcPlaneAngleMeasure BoxSlantAngle();
    bool hasBoxRotateAngle();
    IfcPlaneAngleMeasure BoxRotateAngle();
    bool hasCharacterSpacing();
    IfcSizeSelect CharacterSpacing();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextStyleWithBoxCharacteristics (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextStyleWithBoxCharacteristics* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextStyleWithBoxCharacteristics> > list;
    typedef IfcTemplatedEntityList<IfcTextStyleWithBoxCharacteristics>::it it;
};
class IfcTextureCoordinate : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSurface> > AnnotatedSurface(); // INVERSE IfcAnnotationSurface::TextureCoordinates
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextureCoordinate (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextureCoordinate* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextureCoordinate> > list;
    typedef IfcTemplatedEntityList<IfcTextureCoordinate>::it it;
};
class IfcTextureCoordinateGenerator : public IfcTextureCoordinate {
public:
    IfcLabel Mode();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Parameter();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextureCoordinateGenerator (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextureCoordinateGenerator* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextureCoordinateGenerator> > list;
    typedef IfcTemplatedEntityList<IfcTextureCoordinateGenerator>::it it;
};
class IfcTextureMap : public IfcTextureCoordinate {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcVertexBasedTextureMap> > TextureMaps();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextureMap (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextureMap* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextureMap> > list;
    typedef IfcTemplatedEntityList<IfcTextureMap>::it it;
};
class IfcTextureVertex : public IfcBaseClass {
public:
    std::vector<IfcParameterValue> /*[2:2]*/ Coordinates();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextureVertex (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextureVertex* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextureVertex> > list;
    typedef IfcTemplatedEntityList<IfcTextureVertex>::it it;
};
class IfcThermalMaterialProperties : public IfcMaterialProperties {
public:
    bool hasSpecificHeatCapacity();
    IfcSpecificHeatCapacityMeasure SpecificHeatCapacity();
    bool hasBoilingPoint();
    IfcThermodynamicTemperatureMeasure BoilingPoint();
    bool hasFreezingPoint();
    IfcThermodynamicTemperatureMeasure FreezingPoint();
    bool hasThermalConductivity();
    IfcThermalConductivityMeasure ThermalConductivity();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcThermalMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcThermalMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcThermalMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcThermalMaterialProperties>::it it;
};
class IfcTimeSeries : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    IfcDateTimeSelect StartTime();
    IfcDateTimeSelect EndTime();
    IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataTypeEnum TimeSeriesDataType();
    IfcDataOriginEnum::IfcDataOriginEnum DataOrigin();
    bool hasUserDefinedDataOrigin();
    IfcLabel UserDefinedDataOrigin();
    bool hasUnit();
    IfcUnit Unit();
    SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesReferenceRelationship> > DocumentedBy(); // INVERSE IfcTimeSeriesReferenceRelationship::ReferencedTimeSeries
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTimeSeries (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTimeSeries* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeries> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeries>::it it;
};
class IfcTimeSeriesReferenceRelationship : public IfcBaseClass {
public:
    IfcTimeSeries* ReferencedTimeSeries();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > TimeSeriesReferences();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTimeSeriesReferenceRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTimeSeriesReferenceRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesReferenceRelationship> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeriesReferenceRelationship>::it it;
};
class IfcTimeSeriesValue : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ListValues();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTimeSeriesValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTimeSeriesValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesValue> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeriesValue>::it it;
};
class IfcTopologicalRepresentationItem : public IfcRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTopologicalRepresentationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTopologicalRepresentationItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTopologicalRepresentationItem> > list;
    typedef IfcTemplatedEntityList<IfcTopologicalRepresentationItem>::it it;
};
class IfcTopologyRepresentation : public IfcShapeModel {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTopologyRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTopologyRepresentation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTopologyRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcTopologyRepresentation>::it it;
};
class IfcUnitAssignment : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Units();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcUnitAssignment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcUnitAssignment* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcUnitAssignment> > list;
    typedef IfcTemplatedEntityList<IfcUnitAssignment>::it it;
};
class IfcVertex : public IfcTopologicalRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVertex (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVertex* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVertex> > list;
    typedef IfcTemplatedEntityList<IfcVertex>::it it;
};
class IfcVertexBasedTextureMap : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcTextureVertex> > TextureVertices();
    SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > TexturePoints();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVertexBasedTextureMap (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVertexBasedTextureMap* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVertexBasedTextureMap> > list;
    typedef IfcTemplatedEntityList<IfcVertexBasedTextureMap>::it it;
};
class IfcVertexPoint : public IfcVertex {
public:
    IfcPoint* VertexGeometry();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVertexPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVertexPoint* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVertexPoint> > list;
    typedef IfcTemplatedEntityList<IfcVertexPoint>::it it;
};
class IfcVirtualGridIntersection : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IntersectingAxes();
    std::vector<IfcLengthMeasure> /*[2:3]*/ OffsetDistances();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVirtualGridIntersection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVirtualGridIntersection* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVirtualGridIntersection> > list;
    typedef IfcTemplatedEntityList<IfcVirtualGridIntersection>::it it;
};
class IfcWaterProperties : public IfcMaterialProperties {
public:
    bool hasIsPotable();
    bool IsPotable();
    bool hasHardness();
    IfcIonConcentrationMeasure Hardness();
    bool hasAlkalinityConcentration();
    IfcIonConcentrationMeasure AlkalinityConcentration();
    bool hasAcidityConcentration();
    IfcIonConcentrationMeasure AcidityConcentration();
    bool hasImpuritiesContent();
    IfcNormalisedRatioMeasure ImpuritiesContent();
    bool hasPHLevel();
    IfcPHMeasure PHLevel();
    bool hasDissolvedSolidsContent();
    IfcNormalisedRatioMeasure DissolvedSolidsContent();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWaterProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWaterProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWaterProperties> > list;
    typedef IfcTemplatedEntityList<IfcWaterProperties>::it it;
};
class IfcAnnotationOccurrence : public IfcStyledItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationOccurrence* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationOccurrence>::it it;
};
class IfcAnnotationSurfaceOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationSurfaceOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationSurfaceOccurrence* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSurfaceOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationSurfaceOccurrence>::it it;
};
class IfcAnnotationSymbolOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationSymbolOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationSymbolOccurrence* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSymbolOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationSymbolOccurrence>::it it;
};
class IfcAnnotationTextOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationTextOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationTextOccurrence* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationTextOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationTextOccurrence>::it it;
};
class IfcArbitraryClosedProfileDef : public IfcProfileDef {
public:
    IfcCurve* OuterCurve();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcArbitraryClosedProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcArbitraryClosedProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcArbitraryClosedProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcArbitraryClosedProfileDef>::it it;
};
class IfcArbitraryOpenProfileDef : public IfcProfileDef {
public:
    IfcBoundedCurve* Curve();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcArbitraryOpenProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcArbitraryOpenProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcArbitraryOpenProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcArbitraryOpenProfileDef>::it it;
};
class IfcArbitraryProfileDefWithVoids : public IfcArbitraryClosedProfileDef {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > InnerCurves();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcArbitraryProfileDefWithVoids (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcArbitraryProfileDefWithVoids* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcArbitraryProfileDefWithVoids> > list;
    typedef IfcTemplatedEntityList<IfcArbitraryProfileDefWithVoids>::it it;
};
class IfcBlobTexture : public IfcSurfaceTexture {
public:
    IfcIdentifier RasterFormat();
    bool RasterCode();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBlobTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBlobTexture* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBlobTexture> > list;
    typedef IfcTemplatedEntityList<IfcBlobTexture>::it it;
};
class IfcCenterLineProfileDef : public IfcArbitraryOpenProfileDef {
public:
    IfcPositiveLengthMeasure Thickness();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCenterLineProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCenterLineProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCenterLineProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCenterLineProfileDef>::it it;
};
class IfcClassificationReference : public IfcExternalReference {
public:
    bool hasReferencedSource();
    IfcClassification* ReferencedSource();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcClassificationReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcClassificationReference* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationReference> > list;
    typedef IfcTemplatedEntityList<IfcClassificationReference>::it it;
};
class IfcColourRgb : public IfcColourSpecification {
public:
    IfcNormalisedRatioMeasure Red();
    IfcNormalisedRatioMeasure Green();
    IfcNormalisedRatioMeasure Blue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcColourRgb (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcColourRgb* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColourRgb> > list;
    typedef IfcTemplatedEntityList<IfcColourRgb>::it it;
};
class IfcComplexProperty : public IfcProperty {
public:
    IfcIdentifier UsageName();
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > HasProperties();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcComplexProperty (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcComplexProperty* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcComplexProperty> > list;
    typedef IfcTemplatedEntityList<IfcComplexProperty>::it it;
};
class IfcCompositeProfileDef : public IfcProfileDef {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > Profiles();
    bool hasLabel();
    IfcLabel Label();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCompositeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCompositeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCompositeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCompositeProfileDef>::it it;
};
class IfcConnectedFaceSet : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcFace> > CfsFaces();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConnectedFaceSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConnectedFaceSet* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectedFaceSet> > list;
    typedef IfcTemplatedEntityList<IfcConnectedFaceSet>::it it;
};
class IfcConnectionCurveGeometry : public IfcConnectionGeometry {
public:
    IfcCurveOrEdgeCurve CurveOnRelatingElement();
    bool hasCurveOnRelatedElement();
    IfcCurveOrEdgeCurve CurveOnRelatedElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConnectionCurveGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConnectionCurveGeometry* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionCurveGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionCurveGeometry>::it it;
};
class IfcConnectionPointEccentricity : public IfcConnectionPointGeometry {
public:
    bool hasEccentricityInX();
    IfcLengthMeasure EccentricityInX();
    bool hasEccentricityInY();
    IfcLengthMeasure EccentricityInY();
    bool hasEccentricityInZ();
    IfcLengthMeasure EccentricityInZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConnectionPointEccentricity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConnectionPointEccentricity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionPointEccentricity> > list;
    typedef IfcTemplatedEntityList<IfcConnectionPointEccentricity>::it it;
};
class IfcContextDependentUnit : public IfcNamedUnit {
public:
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcContextDependentUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcContextDependentUnit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcContextDependentUnit> > list;
    typedef IfcTemplatedEntityList<IfcContextDependentUnit>::it it;
};
class IfcConversionBasedUnit : public IfcNamedUnit {
public:
    IfcLabel Name();
    IfcMeasureWithUnit* ConversionFactor();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConversionBasedUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConversionBasedUnit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConversionBasedUnit> > list;
    typedef IfcTemplatedEntityList<IfcConversionBasedUnit>::it it;
};
class IfcCurveStyle : public IfcPresentationStyle {
public:
    bool hasCurveFont();
    IfcCurveFontOrScaledCurveFontSelect CurveFont();
    bool hasCurveWidth();
    IfcSizeSelect CurveWidth();
    bool hasCurveColour();
    IfcColour CurveColour();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurveStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurveStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyle> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyle>::it it;
};
class IfcDerivedProfileDef : public IfcProfileDef {
public:
    IfcProfileDef* ParentProfile();
    IfcCartesianTransformationOperator2D* Operator();
    bool hasLabel();
    IfcLabel Label();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDerivedProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDerivedProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDerivedProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcDerivedProfileDef>::it it;
};
class IfcDimensionCalloutRelationship : public IfcDraughtingCalloutRelationship {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDimensionCalloutRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDimensionCalloutRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCalloutRelationship> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCalloutRelationship>::it it;
};
class IfcDimensionPair : public IfcDraughtingCalloutRelationship {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDimensionPair (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDimensionPair* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionPair> > list;
    typedef IfcTemplatedEntityList<IfcDimensionPair>::it it;
};
class IfcDocumentReference : public IfcExternalReference {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > ReferenceToDocument(); // INVERSE IfcDocumentInformation::DocumentReferences
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDocumentReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDocumentReference* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDocumentReference> > list;
    typedef IfcTemplatedEntityList<IfcDocumentReference>::it it;
};
class IfcDraughtingPreDefinedTextFont : public IfcPreDefinedTextFont {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDraughtingPreDefinedTextFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDraughtingPreDefinedTextFont* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingPreDefinedTextFont> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingPreDefinedTextFont>::it it;
};
class IfcEdge : public IfcTopologicalRepresentationItem {
public:
    IfcVertex* EdgeStart();
    IfcVertex* EdgeEnd();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEdge (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEdge* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdge> > list;
    typedef IfcTemplatedEntityList<IfcEdge>::it it;
};
class IfcEdgeCurve : public IfcEdge {
public:
    IfcCurve* EdgeGeometry();
    bool SameSense();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEdgeCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEdgeCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdgeCurve> > list;
    typedef IfcTemplatedEntityList<IfcEdgeCurve>::it it;
};
class IfcExtendedMaterialProperties : public IfcMaterialProperties {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > ExtendedProperties();
    bool hasDescription();
    IfcText Description();
    IfcLabel Name();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcExtendedMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcExtendedMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExtendedMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcExtendedMaterialProperties>::it it;
};
class IfcFace : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcFaceBound> > Bounds();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFace* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFace> > list;
    typedef IfcTemplatedEntityList<IfcFace>::it it;
};
class IfcFaceBound : public IfcTopologicalRepresentationItem {
public:
    IfcLoop* Bound();
    bool Orientation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFaceBound (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFaceBound* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFaceBound> > list;
    typedef IfcTemplatedEntityList<IfcFaceBound>::it it;
};
class IfcFaceOuterBound : public IfcFaceBound {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFaceOuterBound (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFaceOuterBound* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFaceOuterBound> > list;
    typedef IfcTemplatedEntityList<IfcFaceOuterBound>::it it;
};
class IfcFaceSurface : public IfcFace {
public:
    IfcSurface* FaceSurface();
    bool SameSense();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFaceSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFaceSurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFaceSurface> > list;
    typedef IfcTemplatedEntityList<IfcFaceSurface>::it it;
};
class IfcFailureConnectionCondition : public IfcStructuralConnectionCondition {
public:
    bool hasTensionFailureX();
    IfcForceMeasure TensionFailureX();
    bool hasTensionFailureY();
    IfcForceMeasure TensionFailureY();
    bool hasTensionFailureZ();
    IfcForceMeasure TensionFailureZ();
    bool hasCompressionFailureX();
    IfcForceMeasure CompressionFailureX();
    bool hasCompressionFailureY();
    IfcForceMeasure CompressionFailureY();
    bool hasCompressionFailureZ();
    IfcForceMeasure CompressionFailureZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFailureConnectionCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFailureConnectionCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFailureConnectionCondition> > list;
    typedef IfcTemplatedEntityList<IfcFailureConnectionCondition>::it it;
};
class IfcFillAreaStyle : public IfcPresentationStyle {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > FillStyles();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFillAreaStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFillAreaStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFillAreaStyle> > list;
    typedef IfcTemplatedEntityList<IfcFillAreaStyle>::it it;
};
class IfcFuelProperties : public IfcMaterialProperties {
public:
    bool hasCombustionTemperature();
    IfcThermodynamicTemperatureMeasure CombustionTemperature();
    bool hasCarbonContent();
    IfcPositiveRatioMeasure CarbonContent();
    bool hasLowerHeatingValue();
    IfcHeatingValueMeasure LowerHeatingValue();
    bool hasHigherHeatingValue();
    IfcHeatingValueMeasure HigherHeatingValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFuelProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFuelProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFuelProperties> > list;
    typedef IfcTemplatedEntityList<IfcFuelProperties>::it it;
};
class IfcGeneralMaterialProperties : public IfcMaterialProperties {
public:
    bool hasMolecularWeight();
    IfcMolecularWeightMeasure MolecularWeight();
    bool hasPorosity();
    IfcNormalisedRatioMeasure Porosity();
    bool hasMassDensity();
    IfcMassDensityMeasure MassDensity();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGeneralMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGeneralMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeneralMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcGeneralMaterialProperties>::it it;
};
class IfcGeneralProfileProperties : public IfcProfileProperties {
public:
    bool hasPhysicalWeight();
    IfcMassPerLengthMeasure PhysicalWeight();
    bool hasPerimeter();
    IfcPositiveLengthMeasure Perimeter();
    bool hasMinimumPlateThickness();
    IfcPositiveLengthMeasure MinimumPlateThickness();
    bool hasMaximumPlateThickness();
    IfcPositiveLengthMeasure MaximumPlateThickness();
    bool hasCrossSectionArea();
    IfcAreaMeasure CrossSectionArea();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGeneralProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGeneralProfileProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeneralProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcGeneralProfileProperties>::it it;
};
class IfcGeometricRepresentationContext : public IfcRepresentationContext {
public:
    IfcDimensionCount CoordinateSpaceDimension();
    bool hasPrecision();
    double Precision();
    IfcAxis2Placement WorldCoordinateSystem();
    bool hasTrueNorth();
    IfcDirection* TrueNorth();
    SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationSubContext> > HasSubContexts(); // INVERSE IfcGeometricRepresentationSubContext::ParentContext
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGeometricRepresentationContext (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGeometricRepresentationContext* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationContext> > list;
    typedef IfcTemplatedEntityList<IfcGeometricRepresentationContext>::it it;
};
class IfcGeometricRepresentationItem : public IfcRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGeometricRepresentationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGeometricRepresentationItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationItem> > list;
    typedef IfcTemplatedEntityList<IfcGeometricRepresentationItem>::it it;
};
class IfcGeometricRepresentationSubContext : public IfcGeometricRepresentationContext {
public:
    IfcGeometricRepresentationContext* ParentContext();
    bool hasTargetScale();
    IfcPositiveRatioMeasure TargetScale();
    IfcGeometricProjectionEnum::IfcGeometricProjectionEnum TargetView();
    bool hasUserDefinedTargetView();
    IfcLabel UserDefinedTargetView();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGeometricRepresentationSubContext (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGeometricRepresentationSubContext* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationSubContext> > list;
    typedef IfcTemplatedEntityList<IfcGeometricRepresentationSubContext>::it it;
};
class IfcGeometricSet : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Elements();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGeometricSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGeometricSet* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricSet> > list;
    typedef IfcTemplatedEntityList<IfcGeometricSet>::it it;
};
class IfcGridPlacement : public IfcObjectPlacement {
public:
    IfcVirtualGridIntersection* PlacementLocation();
    bool hasPlacementRefDirection();
    IfcVirtualGridIntersection* PlacementRefDirection();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGridPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGridPlacement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGridPlacement> > list;
    typedef IfcTemplatedEntityList<IfcGridPlacement>::it it;
};
class IfcHalfSpaceSolid : public IfcGeometricRepresentationItem {
public:
    IfcSurface* BaseSurface();
    bool AgreementFlag();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcHalfSpaceSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcHalfSpaceSolid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcHalfSpaceSolid> > list;
    typedef IfcTemplatedEntityList<IfcHalfSpaceSolid>::it it;
};
class IfcHygroscopicMaterialProperties : public IfcMaterialProperties {
public:
    bool hasUpperVaporResistanceFactor();
    IfcPositiveRatioMeasure UpperVaporResistanceFactor();
    bool hasLowerVaporResistanceFactor();
    IfcPositiveRatioMeasure LowerVaporResistanceFactor();
    bool hasIsothermalMoistureCapacity();
    IfcIsothermalMoistureCapacityMeasure IsothermalMoistureCapacity();
    bool hasVaporPermeability();
    IfcVaporPermeabilityMeasure VaporPermeability();
    bool hasMoistureDiffusivity();
    IfcMoistureDiffusivityMeasure MoistureDiffusivity();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcHygroscopicMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcHygroscopicMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcHygroscopicMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcHygroscopicMaterialProperties>::it it;
};
class IfcImageTexture : public IfcSurfaceTexture {
public:
    IfcIdentifier UrlReference();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcImageTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcImageTexture* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcImageTexture> > list;
    typedef IfcTemplatedEntityList<IfcImageTexture>::it it;
};
class IfcIrregularTimeSeries : public IfcTimeSeries {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeriesValue> > Values();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcIrregularTimeSeries (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcIrregularTimeSeries* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeries> > list;
    typedef IfcTemplatedEntityList<IfcIrregularTimeSeries>::it it;
};
class IfcLightSource : public IfcGeometricRepresentationItem {
public:
    bool hasName();
    IfcLabel Name();
    IfcColourRgb* LightColour();
    bool hasAmbientIntensity();
    IfcNormalisedRatioMeasure AmbientIntensity();
    bool hasIntensity();
    IfcNormalisedRatioMeasure Intensity();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightSource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightSource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSource> > list;
    typedef IfcTemplatedEntityList<IfcLightSource>::it it;
};
class IfcLightSourceAmbient : public IfcLightSource {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightSourceAmbient (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightSourceAmbient* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceAmbient> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceAmbient>::it it;
};
class IfcLightSourceDirectional : public IfcLightSource {
public:
    IfcDirection* Orientation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightSourceDirectional (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightSourceDirectional* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceDirectional> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceDirectional>::it it;
};
class IfcLightSourceGoniometric : public IfcLightSource {
public:
    IfcAxis2Placement3D* Position();
    bool hasColourAppearance();
    IfcColourRgb* ColourAppearance();
    IfcThermodynamicTemperatureMeasure ColourTemperature();
    IfcLuminousFluxMeasure LuminousFlux();
    IfcLightEmissionSourceEnum::IfcLightEmissionSourceEnum LightEmissionSource();
    IfcLightDistributionDataSourceSelect LightDistributionDataSource();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightSourceGoniometric (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightSourceGoniometric* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceGoniometric> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceGoniometric>::it it;
};
class IfcLightSourcePositional : public IfcLightSource {
public:
    IfcCartesianPoint* Position();
    IfcPositiveLengthMeasure Radius();
    IfcReal ConstantAttenuation();
    IfcReal DistanceAttenuation();
    IfcReal QuadricAttenuation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightSourcePositional (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightSourcePositional* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourcePositional> > list;
    typedef IfcTemplatedEntityList<IfcLightSourcePositional>::it it;
};
class IfcLightSourceSpot : public IfcLightSourcePositional {
public:
    IfcDirection* Orientation();
    bool hasConcentrationExponent();
    IfcReal ConcentrationExponent();
    IfcPositivePlaneAngleMeasure SpreadAngle();
    IfcPositivePlaneAngleMeasure BeamWidthAngle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightSourceSpot (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightSourceSpot* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceSpot> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceSpot>::it it;
};
class IfcLocalPlacement : public IfcObjectPlacement {
public:
    bool hasPlacementRelTo();
    IfcObjectPlacement* PlacementRelTo();
    IfcAxis2Placement RelativePlacement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLocalPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLocalPlacement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLocalPlacement> > list;
    typedef IfcTemplatedEntityList<IfcLocalPlacement>::it it;
};
class IfcLoop : public IfcTopologicalRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLoop* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLoop> > list;
    typedef IfcTemplatedEntityList<IfcLoop>::it it;
};
class IfcMappedItem : public IfcRepresentationItem {
public:
    IfcRepresentationMap* MappingSource();
    IfcCartesianTransformationOperator* MappingTarget();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMappedItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMappedItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMappedItem> > list;
    typedef IfcTemplatedEntityList<IfcMappedItem>::it it;
};
class IfcMaterialDefinitionRepresentation : public IfcProductRepresentation {
public:
    IfcMaterial* RepresentedMaterial();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMaterialDefinitionRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMaterialDefinitionRepresentation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialDefinitionRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcMaterialDefinitionRepresentation>::it it;
};
class IfcMechanicalConcreteMaterialProperties : public IfcMechanicalMaterialProperties {
public:
    bool hasCompressiveStrength();
    IfcPressureMeasure CompressiveStrength();
    bool hasMaxAggregateSize();
    IfcPositiveLengthMeasure MaxAggregateSize();
    bool hasAdmixturesDescription();
    IfcText AdmixturesDescription();
    bool hasWorkability();
    IfcText Workability();
    bool hasProtectivePoreRatio();
    IfcNormalisedRatioMeasure ProtectivePoreRatio();
    bool hasWaterImpermeability();
    IfcText WaterImpermeability();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMechanicalConcreteMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMechanicalConcreteMaterialProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalConcreteMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalConcreteMaterialProperties>::it it;
};
class IfcObjectDefinition : public IfcRoot {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssigns> > HasAssignments(); // INVERSE IfcRelAssigns::RelatedObjects
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDecomposes> > IsDecomposedBy(); // INVERSE IfcRelDecomposes::RelatingObject
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDecomposes> > Decomposes(); // INVERSE IfcRelDecomposes::RelatedObjects
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociates> > HasAssociations(); // INVERSE IfcRelAssociates::RelatedObjects
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcObjectDefinition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcObjectDefinition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > list;
    typedef IfcTemplatedEntityList<IfcObjectDefinition>::it it;
};
class IfcOneDirectionRepeatFactor : public IfcGeometricRepresentationItem {
public:
    IfcVector* RepeatFactor();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOneDirectionRepeatFactor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOneDirectionRepeatFactor* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOneDirectionRepeatFactor> > list;
    typedef IfcTemplatedEntityList<IfcOneDirectionRepeatFactor>::it it;
};
class IfcOpenShell : public IfcConnectedFaceSet {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOpenShell (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOpenShell* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOpenShell> > list;
    typedef IfcTemplatedEntityList<IfcOpenShell>::it it;
};
class IfcOrientedEdge : public IfcEdge {
public:
    IfcEdge* EdgeElement();
    bool Orientation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOrientedEdge (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOrientedEdge* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > list;
    typedef IfcTemplatedEntityList<IfcOrientedEdge>::it it;
};
class IfcParameterizedProfileDef : public IfcProfileDef {
public:
    IfcAxis2Placement2D* Position();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcParameterizedProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcParameterizedProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcParameterizedProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcParameterizedProfileDef>::it it;
};
class IfcPath : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > EdgeList();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPath (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPath* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPath> > list;
    typedef IfcTemplatedEntityList<IfcPath>::it it;
};
class IfcPhysicalComplexQuantity : public IfcPhysicalQuantity {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > HasQuantities();
    IfcLabel Discrimination();
    bool hasQuality();
    IfcLabel Quality();
    bool hasUsage();
    IfcLabel Usage();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPhysicalComplexQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPhysicalComplexQuantity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalComplexQuantity> > list;
    typedef IfcTemplatedEntityList<IfcPhysicalComplexQuantity>::it it;
};
class IfcPixelTexture : public IfcSurfaceTexture {
public:
    IfcInteger Width();
    IfcInteger Height();
    IfcInteger ColourComponents();
    std::vector<char[32]> /*[1:?]*/ Pixel();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPixelTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPixelTexture* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPixelTexture> > list;
    typedef IfcTemplatedEntityList<IfcPixelTexture>::it it;
};
class IfcPlacement : public IfcGeometricRepresentationItem {
public:
    IfcCartesianPoint* Location();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPlacement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlacement> > list;
    typedef IfcTemplatedEntityList<IfcPlacement>::it it;
};
class IfcPlanarExtent : public IfcGeometricRepresentationItem {
public:
    IfcLengthMeasure SizeInX();
    IfcLengthMeasure SizeInY();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPlanarExtent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPlanarExtent* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlanarExtent> > list;
    typedef IfcTemplatedEntityList<IfcPlanarExtent>::it it;
};
class IfcPoint : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPoint* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPoint> > list;
    typedef IfcTemplatedEntityList<IfcPoint>::it it;
};
class IfcPointOnCurve : public IfcPoint {
public:
    IfcCurve* BasisCurve();
    IfcParameterValue PointParameter();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPointOnCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPointOnCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPointOnCurve> > list;
    typedef IfcTemplatedEntityList<IfcPointOnCurve>::it it;
};
class IfcPointOnSurface : public IfcPoint {
public:
    IfcSurface* BasisSurface();
    IfcParameterValue PointParameterU();
    IfcParameterValue PointParameterV();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPointOnSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPointOnSurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPointOnSurface> > list;
    typedef IfcTemplatedEntityList<IfcPointOnSurface>::it it;
};
class IfcPolyLoop : public IfcLoop {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > Polygon();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPolyLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPolyLoop* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPolyLoop> > list;
    typedef IfcTemplatedEntityList<IfcPolyLoop>::it it;
};
class IfcPolygonalBoundedHalfSpace : public IfcHalfSpaceSolid {
public:
    IfcAxis2Placement3D* Position();
    IfcBoundedCurve* PolygonalBoundary();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPolygonalBoundedHalfSpace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPolygonalBoundedHalfSpace* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPolygonalBoundedHalfSpace> > list;
    typedef IfcTemplatedEntityList<IfcPolygonalBoundedHalfSpace>::it it;
};
class IfcPreDefinedColour : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedColour (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedColour* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedColour> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedColour>::it it;
};
class IfcPreDefinedCurveFont : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedCurveFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedCurveFont* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedCurveFont> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedCurveFont>::it it;
};
class IfcPreDefinedDimensionSymbol : public IfcPreDefinedSymbol {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedDimensionSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedDimensionSymbol* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedDimensionSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedDimensionSymbol>::it it;
};
class IfcPreDefinedPointMarkerSymbol : public IfcPreDefinedSymbol {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPreDefinedPointMarkerSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPreDefinedPointMarkerSymbol* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedPointMarkerSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedPointMarkerSymbol>::it it;
};
class IfcProductDefinitionShape : public IfcProductRepresentation {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > ShapeOfProduct(); // INVERSE IfcProduct::Representation
    SHARED_PTR< IfcTemplatedEntityList<IfcShapeAspect> > HasShapeAspects(); // INVERSE IfcShapeAspect::PartOfProductDefinitionShape
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProductDefinitionShape (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProductDefinitionShape* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProductDefinitionShape> > list;
    typedef IfcTemplatedEntityList<IfcProductDefinitionShape>::it it;
};
class IfcPropertyBoundedValue : public IfcSimpleProperty {
public:
    bool hasUpperBoundValue();
    IfcValue UpperBoundValue();
    bool hasLowerBoundValue();
    IfcValue LowerBoundValue();
    bool hasUnit();
    IfcUnit Unit();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyBoundedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyBoundedValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyBoundedValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyBoundedValue>::it it;
};
class IfcPropertyDefinition : public IfcRoot {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociates> > HasAssociations(); // INVERSE IfcRelAssociates::RelatedObjects
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyDefinition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyDefinition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyDefinition> > list;
    typedef IfcTemplatedEntityList<IfcPropertyDefinition>::it it;
};
class IfcPropertyEnumeratedValue : public IfcSimpleProperty {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > EnumerationValues();
    bool hasEnumerationReference();
    IfcPropertyEnumeration* EnumerationReference();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyEnumeratedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyEnumeratedValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyEnumeratedValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyEnumeratedValue>::it it;
};
class IfcPropertyListValue : public IfcSimpleProperty {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ListValues();
    bool hasUnit();
    IfcUnit Unit();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyListValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyListValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyListValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyListValue>::it it;
};
class IfcPropertyReferenceValue : public IfcSimpleProperty {
public:
    bool hasUsageName();
    IfcLabel UsageName();
    IfcObjectReferenceSelect PropertyReference();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyReferenceValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyReferenceValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyReferenceValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyReferenceValue>::it it;
};
class IfcPropertySetDefinition : public IfcPropertyDefinition {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDefinesByProperties> > PropertyDefinitionOf(); // INVERSE IfcRelDefinesByProperties::RelatingPropertyDefinition
    SHARED_PTR< IfcTemplatedEntityList<IfcTypeObject> > DefinesType(); // INVERSE IfcTypeObject::HasPropertySets
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertySetDefinition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertySetDefinition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertySetDefinition> > list;
    typedef IfcTemplatedEntityList<IfcPropertySetDefinition>::it it;
};
class IfcPropertySingleValue : public IfcSimpleProperty {
public:
    bool hasNominalValue();
    IfcValue NominalValue();
    bool hasUnit();
    IfcUnit Unit();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertySingleValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertySingleValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertySingleValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertySingleValue>::it it;
};
class IfcPropertyTableValue : public IfcSimpleProperty {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > DefiningValues();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > DefinedValues();
    bool hasExpression();
    IfcText Expression();
    bool hasDefiningUnit();
    IfcUnit DefiningUnit();
    bool hasDefinedUnit();
    IfcUnit DefinedUnit();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertyTableValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertyTableValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyTableValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyTableValue>::it it;
};
class IfcRectangleProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure XDim();
    IfcPositiveLengthMeasure YDim();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRectangleProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRectangleProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangleProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcRectangleProfileDef>::it it;
};
class IfcRegularTimeSeries : public IfcTimeSeries {
public:
    IfcTimeMeasure TimeStep();
    SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesValue> > Values();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRegularTimeSeries (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRegularTimeSeries* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRegularTimeSeries> > list;
    typedef IfcTemplatedEntityList<IfcRegularTimeSeries>::it it;
};
class IfcReinforcementDefinitionProperties : public IfcPropertySetDefinition {
public:
    bool hasDefinitionType();
    IfcLabel DefinitionType();
    SHARED_PTR< IfcTemplatedEntityList<IfcSectionReinforcementProperties> > ReinforcementSectionDefinitions();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcReinforcementDefinitionProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcReinforcementDefinitionProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementDefinitionProperties> > list;
    typedef IfcTemplatedEntityList<IfcReinforcementDefinitionProperties>::it it;
};
class IfcRelationship : public IfcRoot {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelationship* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelationship> > list;
    typedef IfcTemplatedEntityList<IfcRelationship>::it it;
};
class IfcRoundedRectangleProfileDef : public IfcRectangleProfileDef {
public:
    IfcPositiveLengthMeasure RoundingRadius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRoundedRectangleProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRoundedRectangleProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoundedRectangleProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcRoundedRectangleProfileDef>::it it;
};
class IfcSectionedSpine : public IfcGeometricRepresentationItem {
public:
    IfcCompositeCurve* SpineCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > CrossSections();
    SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement3D> > CrossSectionPositions();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSectionedSpine (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSectionedSpine* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSectionedSpine> > list;
    typedef IfcTemplatedEntityList<IfcSectionedSpine>::it it;
};
class IfcServiceLifeFactor : public IfcPropertySetDefinition {
public:
    IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorTypeEnum PredefinedType();
    bool hasUpperValue();
    IfcMeasureValue UpperValue();
    IfcMeasureValue MostUsedValue();
    bool hasLowerValue();
    IfcMeasureValue LowerValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcServiceLifeFactor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcServiceLifeFactor* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcServiceLifeFactor> > list;
    typedef IfcTemplatedEntityList<IfcServiceLifeFactor>::it it;
};
class IfcShellBasedSurfaceModel : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > SbsmBoundary();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcShellBasedSurfaceModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcShellBasedSurfaceModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcShellBasedSurfaceModel> > list;
    typedef IfcTemplatedEntityList<IfcShellBasedSurfaceModel>::it it;
};
class IfcSlippageConnectionCondition : public IfcStructuralConnectionCondition {
public:
    bool hasSlippageX();
    IfcLengthMeasure SlippageX();
    bool hasSlippageY();
    IfcLengthMeasure SlippageY();
    bool hasSlippageZ();
    IfcLengthMeasure SlippageZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSlippageConnectionCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSlippageConnectionCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSlippageConnectionCondition> > list;
    typedef IfcTemplatedEntityList<IfcSlippageConnectionCondition>::it it;
};
class IfcSolidModel : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSolidModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSolidModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSolidModel> > list;
    typedef IfcTemplatedEntityList<IfcSolidModel>::it it;
};
class IfcSoundProperties : public IfcPropertySetDefinition {
public:
    IfcBoolean IsAttenuating();
    bool hasSoundScale();
    IfcSoundScaleEnum::IfcSoundScaleEnum SoundScale();
    SHARED_PTR< IfcTemplatedEntityList<IfcSoundValue> > SoundValues();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSoundProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSoundProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSoundProperties> > list;
    typedef IfcTemplatedEntityList<IfcSoundProperties>::it it;
};
class IfcSoundValue : public IfcPropertySetDefinition {
public:
    bool hasSoundLevelTimeSeries();
    IfcTimeSeries* SoundLevelTimeSeries();
    IfcFrequencyMeasure Frequency();
    bool hasSoundLevelSingleValue();
    IfcDerivedMeasureValue SoundLevelSingleValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSoundValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSoundValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSoundValue> > list;
    typedef IfcTemplatedEntityList<IfcSoundValue>::it it;
};
class IfcSpaceThermalLoadProperties : public IfcPropertySetDefinition {
public:
    bool hasApplicableValueRatio();
    IfcPositiveRatioMeasure ApplicableValueRatio();
    IfcThermalLoadSourceEnum::IfcThermalLoadSourceEnum ThermalLoadSource();
    IfcPropertySourceEnum::IfcPropertySourceEnum PropertySource();
    bool hasSourceDescription();
    IfcText SourceDescription();
    IfcPowerMeasure MaximumValue();
    bool hasMinimumValue();
    IfcPowerMeasure MinimumValue();
    bool hasThermalLoadTimeSeriesValues();
    IfcTimeSeries* ThermalLoadTimeSeriesValues();
    bool hasUserDefinedThermalLoadSource();
    IfcLabel UserDefinedThermalLoadSource();
    bool hasUserDefinedPropertySource();
    IfcLabel UserDefinedPropertySource();
    IfcThermalLoadTypeEnum::IfcThermalLoadTypeEnum ThermalLoadType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSpaceThermalLoadProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSpaceThermalLoadProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpaceThermalLoadProperties> > list;
    typedef IfcTemplatedEntityList<IfcSpaceThermalLoadProperties>::it it;
};
class IfcStructuralLoadLinearForce : public IfcStructuralLoadStatic {
public:
    bool hasLinearForceX();
    IfcLinearForceMeasure LinearForceX();
    bool hasLinearForceY();
    IfcLinearForceMeasure LinearForceY();
    bool hasLinearForceZ();
    IfcLinearForceMeasure LinearForceZ();
    bool hasLinearMomentX();
    IfcLinearMomentMeasure LinearMomentX();
    bool hasLinearMomentY();
    IfcLinearMomentMeasure LinearMomentY();
    bool hasLinearMomentZ();
    IfcLinearMomentMeasure LinearMomentZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadLinearForce (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadLinearForce* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadLinearForce> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadLinearForce>::it it;
};
class IfcStructuralLoadPlanarForce : public IfcStructuralLoadStatic {
public:
    bool hasPlanarForceX();
    IfcPlanarForceMeasure PlanarForceX();
    bool hasPlanarForceY();
    IfcPlanarForceMeasure PlanarForceY();
    bool hasPlanarForceZ();
    IfcPlanarForceMeasure PlanarForceZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadPlanarForce (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadPlanarForce* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadPlanarForce> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadPlanarForce>::it it;
};
class IfcStructuralLoadSingleDisplacement : public IfcStructuralLoadStatic {
public:
    bool hasDisplacementX();
    IfcLengthMeasure DisplacementX();
    bool hasDisplacementY();
    IfcLengthMeasure DisplacementY();
    bool hasDisplacementZ();
    IfcLengthMeasure DisplacementZ();
    bool hasRotationalDisplacementRX();
    IfcPlaneAngleMeasure RotationalDisplacementRX();
    bool hasRotationalDisplacementRY();
    IfcPlaneAngleMeasure RotationalDisplacementRY();
    bool hasRotationalDisplacementRZ();
    IfcPlaneAngleMeasure RotationalDisplacementRZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadSingleDisplacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadSingleDisplacement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadSingleDisplacement> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadSingleDisplacement>::it it;
};
class IfcStructuralLoadSingleDisplacementDistortion : public IfcStructuralLoadSingleDisplacement {
public:
    bool hasDistortion();
    IfcCurvatureMeasure Distortion();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadSingleDisplacementDistortion (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadSingleDisplacementDistortion* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadSingleDisplacementDistortion> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadSingleDisplacementDistortion>::it it;
};
class IfcStructuralLoadSingleForce : public IfcStructuralLoadStatic {
public:
    bool hasForceX();
    IfcForceMeasure ForceX();
    bool hasForceY();
    IfcForceMeasure ForceY();
    bool hasForceZ();
    IfcForceMeasure ForceZ();
    bool hasMomentX();
    IfcTorqueMeasure MomentX();
    bool hasMomentY();
    IfcTorqueMeasure MomentY();
    bool hasMomentZ();
    IfcTorqueMeasure MomentZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadSingleForce (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadSingleForce* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadSingleForce> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadSingleForce>::it it;
};
class IfcStructuralLoadSingleForceWarping : public IfcStructuralLoadSingleForce {
public:
    bool hasWarpingMoment();
    IfcWarpingMomentMeasure WarpingMoment();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadSingleForceWarping (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadSingleForceWarping* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadSingleForceWarping> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadSingleForceWarping>::it it;
};
class IfcStructuralProfileProperties : public IfcGeneralProfileProperties {
public:
    bool hasTorsionalConstantX();
    IfcMomentOfInertiaMeasure TorsionalConstantX();
    bool hasMomentOfInertiaYZ();
    IfcMomentOfInertiaMeasure MomentOfInertiaYZ();
    bool hasMomentOfInertiaY();
    IfcMomentOfInertiaMeasure MomentOfInertiaY();
    bool hasMomentOfInertiaZ();
    IfcMomentOfInertiaMeasure MomentOfInertiaZ();
    bool hasWarpingConstant();
    IfcWarpingConstantMeasure WarpingConstant();
    bool hasShearCentreZ();
    IfcLengthMeasure ShearCentreZ();
    bool hasShearCentreY();
    IfcLengthMeasure ShearCentreY();
    bool hasShearDeformationAreaZ();
    IfcAreaMeasure ShearDeformationAreaZ();
    bool hasShearDeformationAreaY();
    IfcAreaMeasure ShearDeformationAreaY();
    bool hasMaximumSectionModulusY();
    IfcSectionModulusMeasure MaximumSectionModulusY();
    bool hasMinimumSectionModulusY();
    IfcSectionModulusMeasure MinimumSectionModulusY();
    bool hasMaximumSectionModulusZ();
    IfcSectionModulusMeasure MaximumSectionModulusZ();
    bool hasMinimumSectionModulusZ();
    IfcSectionModulusMeasure MinimumSectionModulusZ();
    bool hasTorsionalSectionModulus();
    IfcSectionModulusMeasure TorsionalSectionModulus();
    bool hasCentreOfGravityInX();
    IfcLengthMeasure CentreOfGravityInX();
    bool hasCentreOfGravityInY();
    IfcLengthMeasure CentreOfGravityInY();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralProfileProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcStructuralProfileProperties>::it it;
};
class IfcStructuralSteelProfileProperties : public IfcStructuralProfileProperties {
public:
    bool hasShearAreaZ();
    IfcAreaMeasure ShearAreaZ();
    bool hasShearAreaY();
    IfcAreaMeasure ShearAreaY();
    bool hasPlasticShapeFactorY();
    IfcPositiveRatioMeasure PlasticShapeFactorY();
    bool hasPlasticShapeFactorZ();
    IfcPositiveRatioMeasure PlasticShapeFactorZ();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralSteelProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralSteelProfileProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSteelProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSteelProfileProperties>::it it;
};
class IfcSubedge : public IfcEdge {
public:
    IfcEdge* ParentEdge();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSubedge (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSubedge* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSubedge> > list;
    typedef IfcTemplatedEntityList<IfcSubedge>::it it;
};
class IfcSurface : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurface> > list;
    typedef IfcTemplatedEntityList<IfcSurface>::it it;
};
class IfcSurfaceStyleRendering : public IfcSurfaceStyleShading {
public:
    bool hasTransparency();
    IfcNormalisedRatioMeasure Transparency();
    bool hasDiffuseColour();
    IfcColourOrFactor DiffuseColour();
    bool hasTransmissionColour();
    IfcColourOrFactor TransmissionColour();
    bool hasDiffuseTransmissionColour();
    IfcColourOrFactor DiffuseTransmissionColour();
    bool hasReflectionColour();
    IfcColourOrFactor ReflectionColour();
    bool hasSpecularColour();
    IfcColourOrFactor SpecularColour();
    bool hasSpecularHighlight();
    IfcSpecularHighlightSelect SpecularHighlight();
    IfcReflectanceMethodEnum::IfcReflectanceMethodEnum ReflectanceMethod();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceStyleRendering (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceStyleRendering* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleRendering> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleRendering>::it it;
};
class IfcSweptAreaSolid : public IfcSolidModel {
public:
    IfcProfileDef* SweptArea();
    IfcAxis2Placement3D* Position();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSweptAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSweptAreaSolid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSweptAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcSweptAreaSolid>::it it;
};
class IfcSweptDiskSolid : public IfcSolidModel {
public:
    IfcCurve* Directrix();
    IfcPositiveLengthMeasure Radius();
    bool hasInnerRadius();
    IfcPositiveLengthMeasure InnerRadius();
    IfcParameterValue StartParam();
    IfcParameterValue EndParam();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSweptDiskSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSweptDiskSolid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSweptDiskSolid> > list;
    typedef IfcTemplatedEntityList<IfcSweptDiskSolid>::it it;
};
class IfcSweptSurface : public IfcSurface {
public:
    IfcProfileDef* SweptCurve();
    IfcAxis2Placement3D* Position();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSweptSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSweptSurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSweptSurface> > list;
    typedef IfcTemplatedEntityList<IfcSweptSurface>::it it;
};
class IfcTShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure Depth();
    IfcPositiveLengthMeasure FlangeWidth();
    IfcPositiveLengthMeasure WebThickness();
    IfcPositiveLengthMeasure FlangeThickness();
    bool hasFilletRadius();
    IfcPositiveLengthMeasure FilletRadius();
    bool hasFlangeEdgeRadius();
    IfcPositiveLengthMeasure FlangeEdgeRadius();
    bool hasWebEdgeRadius();
    IfcPositiveLengthMeasure WebEdgeRadius();
    bool hasWebSlope();
    IfcPlaneAngleMeasure WebSlope();
    bool hasFlangeSlope();
    IfcPlaneAngleMeasure FlangeSlope();
    bool hasCentreOfGravityInY();
    IfcPositiveLengthMeasure CentreOfGravityInY();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcTShapeProfileDef>::it it;
};
class IfcTerminatorSymbol : public IfcAnnotationSymbolOccurrence {
public:
    IfcAnnotationCurveOccurrence* AnnotatedCurve();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTerminatorSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTerminatorSymbol* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTerminatorSymbol> > list;
    typedef IfcTemplatedEntityList<IfcTerminatorSymbol>::it it;
};
class IfcTextLiteral : public IfcGeometricRepresentationItem {
public:
    IfcPresentableText Literal();
    IfcAxis2Placement Placement();
    IfcTextPath::IfcTextPath Path();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextLiteral (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextLiteral* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextLiteral> > list;
    typedef IfcTemplatedEntityList<IfcTextLiteral>::it it;
};
class IfcTextLiteralWithExtent : public IfcTextLiteral {
public:
    IfcPlanarExtent* Extent();
    IfcBoxAlignment BoxAlignment();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTextLiteralWithExtent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTextLiteralWithExtent* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextLiteralWithExtent> > list;
    typedef IfcTemplatedEntityList<IfcTextLiteralWithExtent>::it it;
};
class IfcTrapeziumProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure BottomXDim();
    IfcPositiveLengthMeasure TopXDim();
    IfcPositiveLengthMeasure YDim();
    IfcLengthMeasure TopXOffset();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTrapeziumProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTrapeziumProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTrapeziumProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcTrapeziumProfileDef>::it it;
};
class IfcTwoDirectionRepeatFactor : public IfcOneDirectionRepeatFactor {
public:
    IfcVector* SecondRepeatFactor();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTwoDirectionRepeatFactor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTwoDirectionRepeatFactor* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTwoDirectionRepeatFactor> > list;
    typedef IfcTemplatedEntityList<IfcTwoDirectionRepeatFactor>::it it;
};
class IfcTypeObject : public IfcObjectDefinition {
public:
    bool hasApplicableOccurrence();
    IfcLabel ApplicableOccurrence();
    bool hasHasPropertySets();
    SHARED_PTR< IfcTemplatedEntityList<IfcPropertySetDefinition> > HasPropertySets();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDefinesByType> > ObjectTypeOf(); // INVERSE IfcRelDefinesByType::RelatingType
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTypeObject (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTypeObject* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTypeObject> > list;
    typedef IfcTemplatedEntityList<IfcTypeObject>::it it;
};
class IfcTypeProduct : public IfcTypeObject {
public:
    bool hasRepresentationMaps();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationMap> > RepresentationMaps();
    bool hasTag();
    IfcLabel Tag();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTypeProduct (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTypeProduct* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTypeProduct> > list;
    typedef IfcTemplatedEntityList<IfcTypeProduct>::it it;
};
class IfcUShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure Depth();
    IfcPositiveLengthMeasure FlangeWidth();
    IfcPositiveLengthMeasure WebThickness();
    IfcPositiveLengthMeasure FlangeThickness();
    bool hasFilletRadius();
    IfcPositiveLengthMeasure FilletRadius();
    bool hasEdgeRadius();
    IfcPositiveLengthMeasure EdgeRadius();
    bool hasFlangeSlope();
    IfcPlaneAngleMeasure FlangeSlope();
    bool hasCentreOfGravityInX();
    IfcPositiveLengthMeasure CentreOfGravityInX();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcUShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcUShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcUShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcUShapeProfileDef>::it it;
};
class IfcVector : public IfcGeometricRepresentationItem {
public:
    IfcDirection* Orientation();
    IfcLengthMeasure Magnitude();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVector (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVector* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVector> > list;
    typedef IfcTemplatedEntityList<IfcVector>::it it;
};
class IfcVertexLoop : public IfcLoop {
public:
    IfcVertex* LoopVertex();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVertexLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVertexLoop* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVertexLoop> > list;
    typedef IfcTemplatedEntityList<IfcVertexLoop>::it it;
};
class IfcWindowLiningProperties : public IfcPropertySetDefinition {
public:
    bool hasLiningDepth();
    IfcPositiveLengthMeasure LiningDepth();
    bool hasLiningThickness();
    IfcPositiveLengthMeasure LiningThickness();
    bool hasTransomThickness();
    IfcPositiveLengthMeasure TransomThickness();
    bool hasMullionThickness();
    IfcPositiveLengthMeasure MullionThickness();
    bool hasFirstTransomOffset();
    IfcNormalisedRatioMeasure FirstTransomOffset();
    bool hasSecondTransomOffset();
    IfcNormalisedRatioMeasure SecondTransomOffset();
    bool hasFirstMullionOffset();
    IfcNormalisedRatioMeasure FirstMullionOffset();
    bool hasSecondMullionOffset();
    IfcNormalisedRatioMeasure SecondMullionOffset();
    bool hasShapeAspectStyle();
    IfcShapeAspect* ShapeAspectStyle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWindowLiningProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWindowLiningProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWindowLiningProperties> > list;
    typedef IfcTemplatedEntityList<IfcWindowLiningProperties>::it it;
};
class IfcWindowPanelProperties : public IfcPropertySetDefinition {
public:
    IfcWindowPanelOperationEnum::IfcWindowPanelOperationEnum OperationType();
    IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum PanelPosition();
    bool hasFrameDepth();
    IfcPositiveLengthMeasure FrameDepth();
    bool hasFrameThickness();
    IfcPositiveLengthMeasure FrameThickness();
    bool hasShapeAspectStyle();
    IfcShapeAspect* ShapeAspectStyle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWindowPanelProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWindowPanelProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWindowPanelProperties> > list;
    typedef IfcTemplatedEntityList<IfcWindowPanelProperties>::it it;
};
class IfcWindowStyle : public IfcTypeProduct {
public:
    IfcWindowStyleConstructionEnum::IfcWindowStyleConstructionEnum ConstructionType();
    IfcWindowStyleOperationEnum::IfcWindowStyleOperationEnum OperationType();
    bool ParameterTakesPrecedence();
    bool Sizeable();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWindowStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWindowStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWindowStyle> > list;
    typedef IfcTemplatedEntityList<IfcWindowStyle>::it it;
};
class IfcZShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure Depth();
    IfcPositiveLengthMeasure FlangeWidth();
    IfcPositiveLengthMeasure WebThickness();
    IfcPositiveLengthMeasure FlangeThickness();
    bool hasFilletRadius();
    IfcPositiveLengthMeasure FilletRadius();
    bool hasEdgeRadius();
    IfcPositiveLengthMeasure EdgeRadius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcZShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcZShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcZShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcZShapeProfileDef>::it it;
};
class IfcAnnotationCurveOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationCurveOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationCurveOccurrence* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationCurveOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationCurveOccurrence>::it it;
};
class IfcAnnotationFillArea : public IfcGeometricRepresentationItem {
public:
    IfcCurve* OuterBoundary();
    bool hasInnerBoundaries();
    SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > InnerBoundaries();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationFillArea (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationFillArea* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationFillArea> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationFillArea>::it it;
};
class IfcAnnotationFillAreaOccurrence : public IfcAnnotationOccurrence {
public:
    bool hasFillStyleTarget();
    IfcPoint* FillStyleTarget();
    bool hasGlobalOrLocal();
    IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum GlobalOrLocal();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationFillAreaOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationFillAreaOccurrence* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationFillAreaOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationFillAreaOccurrence>::it it;
};
class IfcAnnotationSurface : public IfcGeometricRepresentationItem {
public:
    IfcGeometricRepresentationItem* Item();
    bool hasTextureCoordinates();
    IfcTextureCoordinate* TextureCoordinates();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotationSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotationSurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSurface> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationSurface>::it it;
};
class IfcAxis1Placement : public IfcPlacement {
public:
    bool hasAxis();
    IfcDirection* Axis();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAxis1Placement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAxis1Placement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAxis1Placement> > list;
    typedef IfcTemplatedEntityList<IfcAxis1Placement>::it it;
};
class IfcAxis2Placement2D : public IfcPlacement {
public:
    bool hasRefDirection();
    IfcDirection* RefDirection();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAxis2Placement2D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAxis2Placement2D* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement2D> > list;
    typedef IfcTemplatedEntityList<IfcAxis2Placement2D>::it it;
};
class IfcAxis2Placement3D : public IfcPlacement {
public:
    bool hasAxis();
    IfcDirection* Axis();
    bool hasRefDirection();
    IfcDirection* RefDirection();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAxis2Placement3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAxis2Placement3D* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement3D> > list;
    typedef IfcTemplatedEntityList<IfcAxis2Placement3D>::it it;
};
class IfcBooleanResult : public IfcGeometricRepresentationItem {
public:
    IfcBooleanOperator::IfcBooleanOperator Operator();
    IfcBooleanOperand FirstOperand();
    IfcBooleanOperand SecondOperand();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBooleanResult (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBooleanResult* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBooleanResult> > list;
    typedef IfcTemplatedEntityList<IfcBooleanResult>::it it;
};
class IfcBoundedSurface : public IfcSurface {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundedSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundedSurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundedSurface> > list;
    typedef IfcTemplatedEntityList<IfcBoundedSurface>::it it;
};
class IfcBoundingBox : public IfcGeometricRepresentationItem {
public:
    IfcCartesianPoint* Corner();
    IfcPositiveLengthMeasure XDim();
    IfcPositiveLengthMeasure YDim();
    IfcPositiveLengthMeasure ZDim();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundingBox (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundingBox* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundingBox> > list;
    typedef IfcTemplatedEntityList<IfcBoundingBox>::it it;
};
class IfcBoxedHalfSpace : public IfcHalfSpaceSolid {
public:
    IfcBoundingBox* Enclosure();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoxedHalfSpace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoxedHalfSpace* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoxedHalfSpace> > list;
    typedef IfcTemplatedEntityList<IfcBoxedHalfSpace>::it it;
};
class IfcCShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure Depth();
    IfcPositiveLengthMeasure Width();
    IfcPositiveLengthMeasure WallThickness();
    IfcPositiveLengthMeasure Girth();
    bool hasInternalFilletRadius();
    IfcPositiveLengthMeasure InternalFilletRadius();
    bool hasCentreOfGravityInX();
    IfcPositiveLengthMeasure CentreOfGravityInX();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCShapeProfileDef>::it it;
};
class IfcCartesianPoint : public IfcPoint {
public:
    std::vector<IfcLengthMeasure> /*[1:3]*/ Coordinates();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCartesianPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCartesianPoint* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > list;
    typedef IfcTemplatedEntityList<IfcCartesianPoint>::it it;
};
class IfcCartesianTransformationOperator : public IfcGeometricRepresentationItem {
public:
    bool hasAxis1();
    IfcDirection* Axis1();
    bool hasAxis2();
    IfcDirection* Axis2();
    IfcCartesianPoint* LocalOrigin();
    bool hasScale();
    double Scale();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCartesianTransformationOperator (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCartesianTransformationOperator* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator>::it it;
};
class IfcCartesianTransformationOperator2D : public IfcCartesianTransformationOperator {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCartesianTransformationOperator2D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCartesianTransformationOperator2D* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator2D> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator2D>::it it;
};
class IfcCartesianTransformationOperator2DnonUniform : public IfcCartesianTransformationOperator2D {
public:
    bool hasScale2();
    double Scale2();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCartesianTransformationOperator2DnonUniform (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCartesianTransformationOperator2DnonUniform* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator2DnonUniform> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator2DnonUniform>::it it;
};
class IfcCartesianTransformationOperator3D : public IfcCartesianTransformationOperator {
public:
    bool hasAxis3();
    IfcDirection* Axis3();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCartesianTransformationOperator3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCartesianTransformationOperator3D* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator3D> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator3D>::it it;
};
class IfcCartesianTransformationOperator3DnonUniform : public IfcCartesianTransformationOperator3D {
public:
    bool hasScale2();
    double Scale2();
    bool hasScale3();
    double Scale3();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCartesianTransformationOperator3DnonUniform (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCartesianTransformationOperator3DnonUniform* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator3DnonUniform> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator3DnonUniform>::it it;
};
class IfcCircleProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCircleProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCircleProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCircleProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCircleProfileDef>::it it;
};
class IfcClosedShell : public IfcConnectedFaceSet {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcClosedShell (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcClosedShell* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClosedShell> > list;
    typedef IfcTemplatedEntityList<IfcClosedShell>::it it;
};
class IfcCompositeCurveSegment : public IfcGeometricRepresentationItem {
public:
    IfcTransitionCode::IfcTransitionCode Transition();
    bool SameSense();
    IfcCurve* ParentCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurve> > UsingCurves(); // INVERSE IfcCompositeCurve::Segments
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCompositeCurveSegment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCompositeCurveSegment* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurveSegment> > list;
    typedef IfcTemplatedEntityList<IfcCompositeCurveSegment>::it it;
};
class IfcCraneRailAShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure OverallHeight();
    IfcPositiveLengthMeasure BaseWidth2();
    bool hasRadius();
    IfcPositiveLengthMeasure Radius();
    IfcPositiveLengthMeasure HeadWidth();
    IfcPositiveLengthMeasure HeadDepth2();
    IfcPositiveLengthMeasure HeadDepth3();
    IfcPositiveLengthMeasure WebThickness();
    IfcPositiveLengthMeasure BaseWidth4();
    IfcPositiveLengthMeasure BaseDepth1();
    IfcPositiveLengthMeasure BaseDepth2();
    IfcPositiveLengthMeasure BaseDepth3();
    bool hasCentreOfGravityInY();
    IfcPositiveLengthMeasure CentreOfGravityInY();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCraneRailAShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCraneRailAShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCraneRailAShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCraneRailAShapeProfileDef>::it it;
};
class IfcCraneRailFShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure OverallHeight();
    IfcPositiveLengthMeasure HeadWidth();
    bool hasRadius();
    IfcPositiveLengthMeasure Radius();
    IfcPositiveLengthMeasure HeadDepth2();
    IfcPositiveLengthMeasure HeadDepth3();
    IfcPositiveLengthMeasure WebThickness();
    IfcPositiveLengthMeasure BaseDepth1();
    IfcPositiveLengthMeasure BaseDepth2();
    bool hasCentreOfGravityInY();
    IfcPositiveLengthMeasure CentreOfGravityInY();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCraneRailFShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCraneRailFShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCraneRailFShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCraneRailFShapeProfileDef>::it it;
};
class IfcCsgPrimitive3D : public IfcGeometricRepresentationItem {
public:
    IfcAxis2Placement3D* Position();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCsgPrimitive3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCsgPrimitive3D* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCsgPrimitive3D> > list;
    typedef IfcTemplatedEntityList<IfcCsgPrimitive3D>::it it;
};
class IfcCsgSolid : public IfcSolidModel {
public:
    IfcCsgSelect TreeRootExpression();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCsgSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCsgSolid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCsgSolid> > list;
    typedef IfcTemplatedEntityList<IfcCsgSolid>::it it;
};
class IfcCurve : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > list;
    typedef IfcTemplatedEntityList<IfcCurve>::it it;
};
class IfcCurveBoundedPlane : public IfcBoundedSurface {
public:
    IfcPlane* BasisSurface();
    IfcCurve* OuterBoundary();
    SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > InnerBoundaries();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurveBoundedPlane (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurveBoundedPlane* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveBoundedPlane> > list;
    typedef IfcTemplatedEntityList<IfcCurveBoundedPlane>::it it;
};
class IfcDefinedSymbol : public IfcGeometricRepresentationItem {
public:
    IfcDefinedSymbolSelect Definition();
    IfcCartesianTransformationOperator2D* Target();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDefinedSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDefinedSymbol* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDefinedSymbol> > list;
    typedef IfcTemplatedEntityList<IfcDefinedSymbol>::it it;
};
class IfcDimensionCurve : public IfcAnnotationCurveOccurrence {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcTerminatorSymbol> > AnnotatedBySymbols(); // INVERSE IfcTerminatorSymbol::AnnotatedCurve
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDimensionCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDimensionCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCurve> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCurve>::it it;
};
class IfcDimensionCurveTerminator : public IfcTerminatorSymbol {
public:
    IfcDimensionExtentUsage::IfcDimensionExtentUsage Role();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDimensionCurveTerminator (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDimensionCurveTerminator* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCurveTerminator> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCurveTerminator>::it it;
};
class IfcDirection : public IfcGeometricRepresentationItem {
public:
    std::vector<double> /*[2:3]*/ DirectionRatios();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDirection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDirection* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDirection> > list;
    typedef IfcTemplatedEntityList<IfcDirection>::it it;
};
class IfcDoorLiningProperties : public IfcPropertySetDefinition {
public:
    bool hasLiningDepth();
    IfcPositiveLengthMeasure LiningDepth();
    bool hasLiningThickness();
    IfcPositiveLengthMeasure LiningThickness();
    bool hasThresholdDepth();
    IfcPositiveLengthMeasure ThresholdDepth();
    bool hasThresholdThickness();
    IfcPositiveLengthMeasure ThresholdThickness();
    bool hasTransomThickness();
    IfcPositiveLengthMeasure TransomThickness();
    bool hasTransomOffset();
    IfcLengthMeasure TransomOffset();
    bool hasLiningOffset();
    IfcLengthMeasure LiningOffset();
    bool hasThresholdOffset();
    IfcLengthMeasure ThresholdOffset();
    bool hasCasingThickness();
    IfcPositiveLengthMeasure CasingThickness();
    bool hasCasingDepth();
    IfcPositiveLengthMeasure CasingDepth();
    bool hasShapeAspectStyle();
    IfcShapeAspect* ShapeAspectStyle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDoorLiningProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDoorLiningProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDoorLiningProperties> > list;
    typedef IfcTemplatedEntityList<IfcDoorLiningProperties>::it it;
};
class IfcDoorPanelProperties : public IfcPropertySetDefinition {
public:
    bool hasPanelDepth();
    IfcPositiveLengthMeasure PanelDepth();
    IfcDoorPanelOperationEnum::IfcDoorPanelOperationEnum PanelOperation();
    bool hasPanelWidth();
    IfcNormalisedRatioMeasure PanelWidth();
    IfcDoorPanelPositionEnum::IfcDoorPanelPositionEnum PanelPosition();
    bool hasShapeAspectStyle();
    IfcShapeAspect* ShapeAspectStyle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDoorPanelProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDoorPanelProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDoorPanelProperties> > list;
    typedef IfcTemplatedEntityList<IfcDoorPanelProperties>::it it;
};
class IfcDoorStyle : public IfcTypeProduct {
public:
    IfcDoorStyleOperationEnum::IfcDoorStyleOperationEnum OperationType();
    IfcDoorStyleConstructionEnum::IfcDoorStyleConstructionEnum ConstructionType();
    bool ParameterTakesPrecedence();
    bool Sizeable();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDoorStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDoorStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDoorStyle> > list;
    typedef IfcTemplatedEntityList<IfcDoorStyle>::it it;
};
class IfcDraughtingCallout : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Contents();
    SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCalloutRelationship> > IsRelatedFromCallout(); // INVERSE IfcDraughtingCalloutRelationship::RelatedDraughtingCallout
    SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCalloutRelationship> > IsRelatedToCallout(); // INVERSE IfcDraughtingCalloutRelationship::RelatingDraughtingCallout
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDraughtingCallout (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDraughtingCallout* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCallout> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingCallout>::it it;
};
class IfcDraughtingPreDefinedColour : public IfcPreDefinedColour {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDraughtingPreDefinedColour (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDraughtingPreDefinedColour* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingPreDefinedColour> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingPreDefinedColour>::it it;
};
class IfcDraughtingPreDefinedCurveFont : public IfcPreDefinedCurveFont {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDraughtingPreDefinedCurveFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDraughtingPreDefinedCurveFont* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingPreDefinedCurveFont> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingPreDefinedCurveFont>::it it;
};
class IfcEdgeLoop : public IfcLoop {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > EdgeList();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEdgeLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEdgeLoop* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdgeLoop> > list;
    typedef IfcTemplatedEntityList<IfcEdgeLoop>::it it;
};
class IfcElementQuantity : public IfcPropertySetDefinition {
public:
    bool hasMethodOfMeasurement();
    IfcLabel MethodOfMeasurement();
    SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > Quantities();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElementQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElementQuantity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementQuantity> > list;
    typedef IfcTemplatedEntityList<IfcElementQuantity>::it it;
};
class IfcElementType : public IfcTypeProduct {
public:
    bool hasElementType();
    IfcLabel ElementType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementType> > list;
    typedef IfcTemplatedEntityList<IfcElementType>::it it;
};
class IfcElementarySurface : public IfcSurface {
public:
    IfcAxis2Placement3D* Position();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElementarySurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElementarySurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementarySurface> > list;
    typedef IfcTemplatedEntityList<IfcElementarySurface>::it it;
};
class IfcEllipseProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure SemiAxis1();
    IfcPositiveLengthMeasure SemiAxis2();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEllipseProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEllipseProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEllipseProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcEllipseProfileDef>::it it;
};
class IfcEnergyProperties : public IfcPropertySetDefinition {
public:
    bool hasEnergySequence();
    IfcEnergySequenceEnum::IfcEnergySequenceEnum EnergySequence();
    bool hasUserDefinedEnergySequence();
    IfcLabel UserDefinedEnergySequence();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEnergyProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEnergyProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEnergyProperties> > list;
    typedef IfcTemplatedEntityList<IfcEnergyProperties>::it it;
};
class IfcExtrudedAreaSolid : public IfcSweptAreaSolid {
public:
    IfcDirection* ExtrudedDirection();
    IfcPositiveLengthMeasure Depth();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcExtrudedAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcExtrudedAreaSolid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExtrudedAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcExtrudedAreaSolid>::it it;
};
class IfcFaceBasedSurfaceModel : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcConnectedFaceSet> > FbsmFaces();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFaceBasedSurfaceModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFaceBasedSurfaceModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFaceBasedSurfaceModel> > list;
    typedef IfcTemplatedEntityList<IfcFaceBasedSurfaceModel>::it it;
};
class IfcFillAreaStyleHatching : public IfcGeometricRepresentationItem {
public:
    IfcCurveStyle* HatchLineAppearance();
    IfcHatchLineDistanceSelect StartOfNextHatchLine();
    bool hasPointOfReferenceHatchLine();
    IfcCartesianPoint* PointOfReferenceHatchLine();
    bool hasPatternStart();
    IfcCartesianPoint* PatternStart();
    IfcPlaneAngleMeasure HatchLineAngle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFillAreaStyleHatching (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFillAreaStyleHatching* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFillAreaStyleHatching> > list;
    typedef IfcTemplatedEntityList<IfcFillAreaStyleHatching>::it it;
};
class IfcFillAreaStyleTileSymbolWithStyle : public IfcGeometricRepresentationItem {
public:
    IfcAnnotationSymbolOccurrence* Symbol();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFillAreaStyleTileSymbolWithStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFillAreaStyleTileSymbolWithStyle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFillAreaStyleTileSymbolWithStyle> > list;
    typedef IfcTemplatedEntityList<IfcFillAreaStyleTileSymbolWithStyle>::it it;
};
class IfcFillAreaStyleTiles : public IfcGeometricRepresentationItem {
public:
    IfcOneDirectionRepeatFactor* TilingPattern();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Tiles();
    IfcPositiveRatioMeasure TilingScale();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFillAreaStyleTiles (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFillAreaStyleTiles* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFillAreaStyleTiles> > list;
    typedef IfcTemplatedEntityList<IfcFillAreaStyleTiles>::it it;
};
class IfcFluidFlowProperties : public IfcPropertySetDefinition {
public:
    IfcPropertySourceEnum::IfcPropertySourceEnum PropertySource();
    bool hasFlowConditionTimeSeries();
    IfcTimeSeries* FlowConditionTimeSeries();
    bool hasVelocityTimeSeries();
    IfcTimeSeries* VelocityTimeSeries();
    bool hasFlowrateTimeSeries();
    IfcTimeSeries* FlowrateTimeSeries();
    IfcMaterial* Fluid();
    bool hasPressureTimeSeries();
    IfcTimeSeries* PressureTimeSeries();
    bool hasUserDefinedPropertySource();
    IfcLabel UserDefinedPropertySource();
    bool hasTemperatureSingleValue();
    IfcThermodynamicTemperatureMeasure TemperatureSingleValue();
    bool hasWetBulbTemperatureSingleValue();
    IfcThermodynamicTemperatureMeasure WetBulbTemperatureSingleValue();
    bool hasWetBulbTemperatureTimeSeries();
    IfcTimeSeries* WetBulbTemperatureTimeSeries();
    bool hasTemperatureTimeSeries();
    IfcTimeSeries* TemperatureTimeSeries();
    bool hasFlowrateSingleValue();
    IfcDerivedMeasureValue FlowrateSingleValue();
    bool hasFlowConditionSingleValue();
    IfcPositiveRatioMeasure FlowConditionSingleValue();
    bool hasVelocitySingleValue();
    IfcLinearVelocityMeasure VelocitySingleValue();
    bool hasPressureSingleValue();
    IfcPressureMeasure PressureSingleValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFluidFlowProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFluidFlowProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFluidFlowProperties> > list;
    typedef IfcTemplatedEntityList<IfcFluidFlowProperties>::it it;
};
class IfcFurnishingElementType : public IfcElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFurnishingElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFurnishingElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnishingElementType> > list;
    typedef IfcTemplatedEntityList<IfcFurnishingElementType>::it it;
};
class IfcFurnitureType : public IfcFurnishingElementType {
public:
    IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum AssemblyPlace();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFurnitureType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFurnitureType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnitureType> > list;
    typedef IfcTemplatedEntityList<IfcFurnitureType>::it it;
};
class IfcGeometricCurveSet : public IfcGeometricSet {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGeometricCurveSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGeometricCurveSet* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricCurveSet> > list;
    typedef IfcTemplatedEntityList<IfcGeometricCurveSet>::it it;
};
class IfcIShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure OverallWidth();
    IfcPositiveLengthMeasure OverallDepth();
    IfcPositiveLengthMeasure WebThickness();
    IfcPositiveLengthMeasure FlangeThickness();
    bool hasFilletRadius();
    IfcPositiveLengthMeasure FilletRadius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcIShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcIShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcIShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcIShapeProfileDef>::it it;
};
class IfcLShapeProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure Depth();
    bool hasWidth();
    IfcPositiveLengthMeasure Width();
    IfcPositiveLengthMeasure Thickness();
    bool hasFilletRadius();
    IfcPositiveLengthMeasure FilletRadius();
    bool hasEdgeRadius();
    IfcPositiveLengthMeasure EdgeRadius();
    bool hasLegSlope();
    IfcPlaneAngleMeasure LegSlope();
    bool hasCentreOfGravityInX();
    IfcPositiveLengthMeasure CentreOfGravityInX();
    bool hasCentreOfGravityInY();
    IfcPositiveLengthMeasure CentreOfGravityInY();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcLShapeProfileDef>::it it;
};
class IfcLine : public IfcCurve {
public:
    IfcCartesianPoint* Pnt();
    IfcVector* Dir();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLine (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLine* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLine> > list;
    typedef IfcTemplatedEntityList<IfcLine>::it it;
};
class IfcManifoldSolidBrep : public IfcSolidModel {
public:
    IfcClosedShell* Outer();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcManifoldSolidBrep (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcManifoldSolidBrep* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcManifoldSolidBrep> > list;
    typedef IfcTemplatedEntityList<IfcManifoldSolidBrep>::it it;
};
class IfcObject : public IfcObjectDefinition {
public:
    bool hasObjectType();
    IfcLabel ObjectType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDefines> > IsDefinedBy(); // INVERSE IfcRelDefines::RelatedObjects
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcObject (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcObject* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcObject> > list;
    typedef IfcTemplatedEntityList<IfcObject>::it it;
};
class IfcOffsetCurve2D : public IfcCurve {
public:
    IfcCurve* BasisCurve();
    IfcLengthMeasure Distance();
    bool SelfIntersect();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOffsetCurve2D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOffsetCurve2D* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOffsetCurve2D> > list;
    typedef IfcTemplatedEntityList<IfcOffsetCurve2D>::it it;
};
class IfcOffsetCurve3D : public IfcCurve {
public:
    IfcCurve* BasisCurve();
    IfcLengthMeasure Distance();
    bool SelfIntersect();
    IfcDirection* RefDirection();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOffsetCurve3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOffsetCurve3D* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOffsetCurve3D> > list;
    typedef IfcTemplatedEntityList<IfcOffsetCurve3D>::it it;
};
class IfcPermeableCoveringProperties : public IfcPropertySetDefinition {
public:
    IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperationEnum OperationType();
    IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum PanelPosition();
    bool hasFrameDepth();
    IfcPositiveLengthMeasure FrameDepth();
    bool hasFrameThickness();
    IfcPositiveLengthMeasure FrameThickness();
    bool hasShapeAspectStyle();
    IfcShapeAspect* ShapeAspectStyle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPermeableCoveringProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPermeableCoveringProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPermeableCoveringProperties> > list;
    typedef IfcTemplatedEntityList<IfcPermeableCoveringProperties>::it it;
};
class IfcPlanarBox : public IfcPlanarExtent {
public:
    IfcAxis2Placement Placement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPlanarBox (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPlanarBox* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlanarBox> > list;
    typedef IfcTemplatedEntityList<IfcPlanarBox>::it it;
};
class IfcPlane : public IfcElementarySurface {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPlane (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPlane* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlane> > list;
    typedef IfcTemplatedEntityList<IfcPlane>::it it;
};
class IfcProcess : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProcess> > OperatesOn(); // INVERSE IfcRelAssignsToProcess::RelatingProcess
    SHARED_PTR< IfcTemplatedEntityList<IfcRelSequence> > IsSuccessorFrom(); // INVERSE IfcRelSequence::RelatedProcess
    SHARED_PTR< IfcTemplatedEntityList<IfcRelSequence> > IsPredecessorTo(); // INVERSE IfcRelSequence::RelatingProcess
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProcess (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProcess* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProcess> > list;
    typedef IfcTemplatedEntityList<IfcProcess>::it it;
};
class IfcProduct : public IfcObject {
public:
    bool hasObjectPlacement();
    IfcObjectPlacement* ObjectPlacement();
    bool hasRepresentation();
    IfcProductRepresentation* Representation();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProduct> > ReferencedBy(); // INVERSE IfcRelAssignsToProduct::RelatingProduct
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProduct (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProduct* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > list;
    typedef IfcTemplatedEntityList<IfcProduct>::it it;
};
class IfcProject : public IfcObject {
public:
    bool hasLongName();
    IfcLabel LongName();
    bool hasPhase();
    IfcLabel Phase();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationContext> > RepresentationContexts();
    IfcUnitAssignment* UnitsInContext();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProject (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProject* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProject> > list;
    typedef IfcTemplatedEntityList<IfcProject>::it it;
};
class IfcProjectionCurve : public IfcAnnotationCurveOccurrence {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProjectionCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProjectionCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectionCurve> > list;
    typedef IfcTemplatedEntityList<IfcProjectionCurve>::it it;
};
class IfcPropertySet : public IfcPropertySetDefinition {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > HasProperties();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPropertySet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPropertySet* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertySet> > list;
    typedef IfcTemplatedEntityList<IfcPropertySet>::it it;
};
class IfcProxy : public IfcProduct {
public:
    IfcObjectTypeEnum::IfcObjectTypeEnum ProxyType();
    bool hasTag();
    IfcLabel Tag();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProxy (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProxy* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProxy> > list;
    typedef IfcTemplatedEntityList<IfcProxy>::it it;
};
class IfcRectangleHollowProfileDef : public IfcRectangleProfileDef {
public:
    IfcPositiveLengthMeasure WallThickness();
    bool hasInnerFilletRadius();
    IfcPositiveLengthMeasure InnerFilletRadius();
    bool hasOuterFilletRadius();
    IfcPositiveLengthMeasure OuterFilletRadius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRectangleHollowProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRectangleHollowProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangleHollowProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcRectangleHollowProfileDef>::it it;
};
class IfcRectangularPyramid : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure XLength();
    IfcPositiveLengthMeasure YLength();
    IfcPositiveLengthMeasure Height();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRectangularPyramid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRectangularPyramid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangularPyramid> > list;
    typedef IfcTemplatedEntityList<IfcRectangularPyramid>::it it;
};
class IfcRectangularTrimmedSurface : public IfcBoundedSurface {
public:
    IfcSurface* BasisSurface();
    IfcParameterValue U1();
    IfcParameterValue V1();
    IfcParameterValue U2();
    IfcParameterValue V2();
    bool Usense();
    bool Vsense();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRectangularTrimmedSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRectangularTrimmedSurface* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangularTrimmedSurface> > list;
    typedef IfcTemplatedEntityList<IfcRectangularTrimmedSurface>::it it;
};
class IfcRelAssigns : public IfcRelationship {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > RelatedObjects();
    bool hasRelatedObjectsType();
    IfcObjectTypeEnum::IfcObjectTypeEnum RelatedObjectsType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssigns (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssigns* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssigns> > list;
    typedef IfcTemplatedEntityList<IfcRelAssigns>::it it;
};
class IfcRelAssignsToActor : public IfcRelAssigns {
public:
    IfcActor* RelatingActor();
    bool hasActingRole();
    IfcActorRole* ActingRole();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsToActor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsToActor* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToActor> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToActor>::it it;
};
class IfcRelAssignsToControl : public IfcRelAssigns {
public:
    IfcControl* RelatingControl();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsToControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsToControl* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToControl> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToControl>::it it;
};
class IfcRelAssignsToGroup : public IfcRelAssigns {
public:
    IfcGroup* RelatingGroup();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsToGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsToGroup* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToGroup> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToGroup>::it it;
};
class IfcRelAssignsToProcess : public IfcRelAssigns {
public:
    IfcProcess* RelatingProcess();
    bool hasQuantityInProcess();
    IfcMeasureWithUnit* QuantityInProcess();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsToProcess (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsToProcess* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProcess> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToProcess>::it it;
};
class IfcRelAssignsToProduct : public IfcRelAssigns {
public:
    IfcProduct* RelatingProduct();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsToProduct (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsToProduct* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProduct> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToProduct>::it it;
};
class IfcRelAssignsToProjectOrder : public IfcRelAssignsToControl {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsToProjectOrder (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsToProjectOrder* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProjectOrder> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToProjectOrder>::it it;
};
class IfcRelAssignsToResource : public IfcRelAssigns {
public:
    IfcResource* RelatingResource();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsToResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsToResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToResource> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToResource>::it it;
};
class IfcRelAssociates : public IfcRelationship {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRoot> > RelatedObjects();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociates (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociates* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociates> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociates>::it it;
};
class IfcRelAssociatesAppliedValue : public IfcRelAssociates {
public:
    IfcAppliedValue* RelatingAppliedValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesAppliedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesAppliedValue* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesAppliedValue> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesAppliedValue>::it it;
};
class IfcRelAssociatesApproval : public IfcRelAssociates {
public:
    IfcApproval* RelatingApproval();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesApproval (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesApproval* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesApproval> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesApproval>::it it;
};
class IfcRelAssociatesClassification : public IfcRelAssociates {
public:
    IfcClassificationNotationSelect RelatingClassification();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesClassification (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesClassification* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesClassification> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesClassification>::it it;
};
class IfcRelAssociatesConstraint : public IfcRelAssociates {
public:
    IfcLabel Intent();
    IfcConstraint* RelatingConstraint();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesConstraint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesConstraint* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesConstraint> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesConstraint>::it it;
};
class IfcRelAssociatesDocument : public IfcRelAssociates {
public:
    IfcDocumentSelect RelatingDocument();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesDocument (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesDocument* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesDocument> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesDocument>::it it;
};
class IfcRelAssociatesLibrary : public IfcRelAssociates {
public:
    IfcLibrarySelect RelatingLibrary();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesLibrary (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesLibrary* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesLibrary> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesLibrary>::it it;
};
class IfcRelAssociatesMaterial : public IfcRelAssociates {
public:
    IfcMaterialSelect RelatingMaterial();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesMaterial (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesMaterial* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesMaterial> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesMaterial>::it it;
};
class IfcRelAssociatesProfileProperties : public IfcRelAssociates {
public:
    IfcProfileProperties* RelatingProfileProperties();
    bool hasProfileSectionLocation();
    IfcShapeAspect* ProfileSectionLocation();
    bool hasProfileOrientation();
    IfcOrientationSelect ProfileOrientation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssociatesProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssociatesProfileProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesProfileProperties>::it it;
};
class IfcRelConnects : public IfcRelationship {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnects (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnects* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnects> > list;
    typedef IfcTemplatedEntityList<IfcRelConnects>::it it;
};
class IfcRelConnectsElements : public IfcRelConnects {
public:
    bool hasConnectionGeometry();
    IfcConnectionGeometry* ConnectionGeometry();
    IfcElement* RelatingElement();
    IfcElement* RelatedElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsElements* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsElements> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsElements>::it it;
};
class IfcRelConnectsPathElements : public IfcRelConnectsElements {
public:
    std::vector<int> /*[0:?]*/ RelatingPriorities();
    std::vector<int> /*[0:?]*/ RelatedPriorities();
    IfcConnectionTypeEnum::IfcConnectionTypeEnum RelatedConnectionType();
    IfcConnectionTypeEnum::IfcConnectionTypeEnum RelatingConnectionType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsPathElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsPathElements* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPathElements> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsPathElements>::it it;
};
class IfcRelConnectsPortToElement : public IfcRelConnects {
public:
    IfcPort* RelatingPort();
    IfcElement* RelatedElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsPortToElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsPortToElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPortToElement> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsPortToElement>::it it;
};
class IfcRelConnectsPorts : public IfcRelConnects {
public:
    IfcPort* RelatingPort();
    IfcPort* RelatedPort();
    bool hasRealizingElement();
    IfcElement* RealizingElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsPorts (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsPorts* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPorts> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsPorts>::it it;
};
class IfcRelConnectsStructuralActivity : public IfcRelConnects {
public:
    IfcStructuralActivityAssignmentSelect RelatingElement();
    IfcStructuralActivity* RelatedStructuralActivity();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsStructuralActivity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsStructuralActivity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralActivity> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsStructuralActivity>::it it;
};
class IfcRelConnectsStructuralElement : public IfcRelConnects {
public:
    IfcElement* RelatingElement();
    IfcStructuralMember* RelatedStructuralMember();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsStructuralElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsStructuralElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralElement> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsStructuralElement>::it it;
};
class IfcRelConnectsStructuralMember : public IfcRelConnects {
public:
    IfcStructuralMember* RelatingStructuralMember();
    IfcStructuralConnection* RelatedStructuralConnection();
    bool hasAppliedCondition();
    IfcBoundaryCondition* AppliedCondition();
    bool hasAdditionalConditions();
    IfcStructuralConnectionCondition* AdditionalConditions();
    bool hasSupportedLength();
    IfcLengthMeasure SupportedLength();
    bool hasConditionCoordinateSystem();
    IfcAxis2Placement3D* ConditionCoordinateSystem();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsStructuralMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsStructuralMember* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralMember> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsStructuralMember>::it it;
};
class IfcRelConnectsWithEccentricity : public IfcRelConnectsStructuralMember {
public:
    IfcConnectionGeometry* ConnectionConstraint();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsWithEccentricity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsWithEccentricity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsWithEccentricity> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsWithEccentricity>::it it;
};
class IfcRelConnectsWithRealizingElements : public IfcRelConnectsElements {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcElement> > RealizingElements();
    bool hasConnectionType();
    IfcLabel ConnectionType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelConnectsWithRealizingElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelConnectsWithRealizingElements* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsWithRealizingElements> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsWithRealizingElements>::it it;
};
class IfcRelContainedInSpatialStructure : public IfcRelConnects {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > RelatedElements();
    IfcSpatialStructureElement* RelatingStructure();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelContainedInSpatialStructure (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelContainedInSpatialStructure* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelContainedInSpatialStructure> > list;
    typedef IfcTemplatedEntityList<IfcRelContainedInSpatialStructure>::it it;
};
class IfcRelCoversBldgElements : public IfcRelConnects {
public:
    IfcElement* RelatingBuildingElement();
    SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > RelatedCoverings();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelCoversBldgElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelCoversBldgElements* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversBldgElements> > list;
    typedef IfcTemplatedEntityList<IfcRelCoversBldgElements>::it it;
};
class IfcRelCoversSpaces : public IfcRelConnects {
public:
    IfcSpace* RelatedSpace();
    SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > RelatedCoverings();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelCoversSpaces (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelCoversSpaces* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversSpaces> > list;
    typedef IfcTemplatedEntityList<IfcRelCoversSpaces>::it it;
};
class IfcRelDecomposes : public IfcRelationship {
public:
    IfcObjectDefinition* RelatingObject();
    SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > RelatedObjects();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelDecomposes (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelDecomposes* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDecomposes> > list;
    typedef IfcTemplatedEntityList<IfcRelDecomposes>::it it;
};
class IfcRelDefines : public IfcRelationship {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcObject> > RelatedObjects();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelDefines (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelDefines* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDefines> > list;
    typedef IfcTemplatedEntityList<IfcRelDefines>::it it;
};
class IfcRelDefinesByProperties : public IfcRelDefines {
public:
    IfcPropertySetDefinition* RelatingPropertyDefinition();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelDefinesByProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelDefinesByProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDefinesByProperties> > list;
    typedef IfcTemplatedEntityList<IfcRelDefinesByProperties>::it it;
};
class IfcRelDefinesByType : public IfcRelDefines {
public:
    IfcTypeObject* RelatingType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelDefinesByType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelDefinesByType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDefinesByType> > list;
    typedef IfcTemplatedEntityList<IfcRelDefinesByType>::it it;
};
class IfcRelFillsElement : public IfcRelConnects {
public:
    IfcOpeningElement* RelatingOpeningElement();
    IfcElement* RelatedBuildingElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelFillsElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelFillsElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelFillsElement> > list;
    typedef IfcTemplatedEntityList<IfcRelFillsElement>::it it;
};
class IfcRelFlowControlElements : public IfcRelConnects {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElement> > RelatedControlElements();
    IfcDistributionFlowElement* RelatingFlowElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelFlowControlElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelFlowControlElements* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelFlowControlElements> > list;
    typedef IfcTemplatedEntityList<IfcRelFlowControlElements>::it it;
};
class IfcRelInteractionRequirements : public IfcRelConnects {
public:
    bool hasDailyInteraction();
    IfcCountMeasure DailyInteraction();
    bool hasImportanceRating();
    IfcNormalisedRatioMeasure ImportanceRating();
    bool hasLocationOfInteraction();
    IfcSpatialStructureElement* LocationOfInteraction();
    IfcSpaceProgram* RelatedSpaceProgram();
    IfcSpaceProgram* RelatingSpaceProgram();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelInteractionRequirements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelInteractionRequirements* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelInteractionRequirements> > list;
    typedef IfcTemplatedEntityList<IfcRelInteractionRequirements>::it it;
};
class IfcRelNests : public IfcRelDecomposes {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelNests (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelNests* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelNests> > list;
    typedef IfcTemplatedEntityList<IfcRelNests>::it it;
};
class IfcRelOccupiesSpaces : public IfcRelAssignsToActor {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelOccupiesSpaces (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelOccupiesSpaces* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelOccupiesSpaces> > list;
    typedef IfcTemplatedEntityList<IfcRelOccupiesSpaces>::it it;
};
class IfcRelOverridesProperties : public IfcRelDefinesByProperties {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > OverridingProperties();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelOverridesProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelOverridesProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelOverridesProperties> > list;
    typedef IfcTemplatedEntityList<IfcRelOverridesProperties>::it it;
};
class IfcRelProjectsElement : public IfcRelConnects {
public:
    IfcElement* RelatingElement();
    IfcFeatureElementAddition* RelatedFeatureElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelProjectsElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelProjectsElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelProjectsElement> > list;
    typedef IfcTemplatedEntityList<IfcRelProjectsElement>::it it;
};
class IfcRelReferencedInSpatialStructure : public IfcRelConnects {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > RelatedElements();
    IfcSpatialStructureElement* RelatingStructure();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelReferencedInSpatialStructure (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelReferencedInSpatialStructure* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelReferencedInSpatialStructure> > list;
    typedef IfcTemplatedEntityList<IfcRelReferencedInSpatialStructure>::it it;
};
class IfcRelSchedulesCostItems : public IfcRelAssignsToControl {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelSchedulesCostItems (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelSchedulesCostItems* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelSchedulesCostItems> > list;
    typedef IfcTemplatedEntityList<IfcRelSchedulesCostItems>::it it;
};
class IfcRelSequence : public IfcRelConnects {
public:
    IfcProcess* RelatingProcess();
    IfcProcess* RelatedProcess();
    IfcTimeMeasure TimeLag();
    IfcSequenceEnum::IfcSequenceEnum SequenceType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelSequence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelSequence* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelSequence> > list;
    typedef IfcTemplatedEntityList<IfcRelSequence>::it it;
};
class IfcRelServicesBuildings : public IfcRelConnects {
public:
    IfcSystem* RelatingSystem();
    SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElement> > RelatedBuildings();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelServicesBuildings (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelServicesBuildings* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelServicesBuildings> > list;
    typedef IfcTemplatedEntityList<IfcRelServicesBuildings>::it it;
};
class IfcRelSpaceBoundary : public IfcRelConnects {
public:
    IfcSpace* RelatingSpace();
    bool hasRelatedBuildingElement();
    IfcElement* RelatedBuildingElement();
    bool hasConnectionGeometry();
    IfcConnectionGeometry* ConnectionGeometry();
    IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtualEnum PhysicalOrVirtualBoundary();
    IfcInternalOrExternalEnum::IfcInternalOrExternalEnum InternalOrExternalBoundary();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelSpaceBoundary (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelSpaceBoundary* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelSpaceBoundary> > list;
    typedef IfcTemplatedEntityList<IfcRelSpaceBoundary>::it it;
};
class IfcRelVoidsElement : public IfcRelConnects {
public:
    IfcElement* RelatingBuildingElement();
    IfcFeatureElementSubtraction* RelatedOpeningElement();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelVoidsElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelVoidsElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelVoidsElement> > list;
    typedef IfcTemplatedEntityList<IfcRelVoidsElement>::it it;
};
class IfcResource : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToResource> > ResourceOf(); // INVERSE IfcRelAssignsToResource::RelatingResource
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcResource> > list;
    typedef IfcTemplatedEntityList<IfcResource>::it it;
};
class IfcRevolvedAreaSolid : public IfcSweptAreaSolid {
public:
    IfcAxis1Placement* Axis();
    IfcPlaneAngleMeasure Angle();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRevolvedAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRevolvedAreaSolid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRevolvedAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcRevolvedAreaSolid>::it it;
};
class IfcRightCircularCone : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure Height();
    IfcPositiveLengthMeasure BottomRadius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRightCircularCone (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRightCircularCone* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRightCircularCone> > list;
    typedef IfcTemplatedEntityList<IfcRightCircularCone>::it it;
};
class IfcRightCircularCylinder : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure Height();
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRightCircularCylinder (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRightCircularCylinder* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRightCircularCylinder> > list;
    typedef IfcTemplatedEntityList<IfcRightCircularCylinder>::it it;
};
class IfcSpatialStructureElement : public IfcProduct {
public:
    bool hasLongName();
    IfcLabel LongName();
    IfcElementCompositionEnum::IfcElementCompositionEnum CompositionType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelReferencedInSpatialStructure> > ReferencesElements(); // INVERSE IfcRelReferencedInSpatialStructure::RelatingStructure
    SHARED_PTR< IfcTemplatedEntityList<IfcRelServicesBuildings> > ServicedBySystems(); // INVERSE IfcRelServicesBuildings::RelatedBuildings
    SHARED_PTR< IfcTemplatedEntityList<IfcRelContainedInSpatialStructure> > ContainsElements(); // INVERSE IfcRelContainedInSpatialStructure::RelatingStructure
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSpatialStructureElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSpatialStructureElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElement> > list;
    typedef IfcTemplatedEntityList<IfcSpatialStructureElement>::it it;
};
class IfcSpatialStructureElementType : public IfcElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSpatialStructureElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSpatialStructureElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElementType> > list;
    typedef IfcTemplatedEntityList<IfcSpatialStructureElementType>::it it;
};
class IfcSphere : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSphere (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSphere* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSphere> > list;
    typedef IfcTemplatedEntityList<IfcSphere>::it it;
};
class IfcStructuralActivity : public IfcProduct {
public:
    IfcStructuralLoad* AppliedLoad();
    IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum GlobalOrLocal();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralActivity> > AssignedToStructuralItem(); // INVERSE IfcRelConnectsStructuralActivity::RelatedStructuralActivity
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralActivity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralActivity* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralActivity> > list;
    typedef IfcTemplatedEntityList<IfcStructuralActivity>::it it;
};
class IfcStructuralItem : public IfcProduct {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralActivity> > AssignedStructuralActivity(); // INVERSE IfcRelConnectsStructuralActivity::RelatingElement
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralItem> > list;
    typedef IfcTemplatedEntityList<IfcStructuralItem>::it it;
};
class IfcStructuralMember : public IfcStructuralItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralElement> > ReferencesElement(); // INVERSE IfcRelConnectsStructuralElement::RelatedStructuralMember
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralMember> > ConnectedBy(); // INVERSE IfcRelConnectsStructuralMember::RelatingStructuralMember
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralMember* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralMember> > list;
    typedef IfcTemplatedEntityList<IfcStructuralMember>::it it;
};
class IfcStructuralReaction : public IfcStructuralActivity {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAction> > Causes(); // INVERSE IfcStructuralAction::CausedBy
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralReaction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralReaction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralReaction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralReaction>::it it;
};
class IfcStructuralSurfaceMember : public IfcStructuralMember {
public:
    IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceTypeEnum PredefinedType();
    bool hasThickness();
    IfcPositiveLengthMeasure Thickness();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralSurfaceMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralSurfaceMember* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSurfaceMember> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSurfaceMember>::it it;
};
class IfcStructuralSurfaceMemberVarying : public IfcStructuralSurfaceMember {
public:
    std::vector<IfcPositiveLengthMeasure> /*[2:?]*/ SubsequentThickness();
    IfcShapeAspect* VaryingThicknessLocation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralSurfaceMemberVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralSurfaceMemberVarying* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSurfaceMemberVarying> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSurfaceMemberVarying>::it it;
};
class IfcStructuredDimensionCallout : public IfcDraughtingCallout {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuredDimensionCallout (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuredDimensionCallout* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuredDimensionCallout> > list;
    typedef IfcTemplatedEntityList<IfcStructuredDimensionCallout>::it it;
};
class IfcSurfaceCurveSweptAreaSolid : public IfcSweptAreaSolid {
public:
    IfcCurve* Directrix();
    IfcParameterValue StartParam();
    IfcParameterValue EndParam();
    IfcSurface* ReferenceSurface();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceCurveSweptAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceCurveSweptAreaSolid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceCurveSweptAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceCurveSweptAreaSolid>::it it;
};
class IfcSurfaceOfLinearExtrusion : public IfcSweptSurface {
public:
    IfcDirection* ExtrudedDirection();
    IfcLengthMeasure Depth();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceOfLinearExtrusion (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceOfLinearExtrusion* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceOfLinearExtrusion> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceOfLinearExtrusion>::it it;
};
class IfcSurfaceOfRevolution : public IfcSweptSurface {
public:
    IfcAxis1Placement* AxisPosition();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSurfaceOfRevolution (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSurfaceOfRevolution* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceOfRevolution> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceOfRevolution>::it it;
};
class IfcSystemFurnitureElementType : public IfcFurnishingElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSystemFurnitureElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSystemFurnitureElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSystemFurnitureElementType> > list;
    typedef IfcTemplatedEntityList<IfcSystemFurnitureElementType>::it it;
};
class IfcTask : public IfcProcess {
public:
    IfcIdentifier TaskId();
    bool hasStatus();
    IfcLabel Status();
    bool hasWorkMethod();
    IfcLabel WorkMethod();
    bool IsMilestone();
    bool hasPriority();
    int Priority();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTask (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTask* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTask> > list;
    typedef IfcTemplatedEntityList<IfcTask>::it it;
};
class IfcTransportElementType : public IfcElementType {
public:
    IfcTransportElementTypeEnum::IfcTransportElementTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTransportElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTransportElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTransportElementType> > list;
    typedef IfcTemplatedEntityList<IfcTransportElementType>::it it;
};
class IfcActor : public IfcObject {
public:
    IfcActorSelect TheActor();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToActor> > IsActingUpon(); // INVERSE IfcRelAssignsToActor::RelatingActor
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcActor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcActor* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcActor> > list;
    typedef IfcTemplatedEntityList<IfcActor>::it it;
};
class IfcAnnotation : public IfcProduct {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelContainedInSpatialStructure> > ContainedInStructure(); // INVERSE IfcRelContainedInSpatialStructure::RelatedElements
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAnnotation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAnnotation* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotation> > list;
    typedef IfcTemplatedEntityList<IfcAnnotation>::it it;
};
class IfcAsymmetricIShapeProfileDef : public IfcIShapeProfileDef {
public:
    IfcPositiveLengthMeasure TopFlangeWidth();
    bool hasTopFlangeThickness();
    IfcPositiveLengthMeasure TopFlangeThickness();
    bool hasTopFlangeFilletRadius();
    IfcPositiveLengthMeasure TopFlangeFilletRadius();
    bool hasCentreOfGravityInY();
    IfcPositiveLengthMeasure CentreOfGravityInY();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAsymmetricIShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAsymmetricIShapeProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAsymmetricIShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcAsymmetricIShapeProfileDef>::it it;
};
class IfcBlock : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure XLength();
    IfcPositiveLengthMeasure YLength();
    IfcPositiveLengthMeasure ZLength();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBlock (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBlock* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBlock> > list;
    typedef IfcTemplatedEntityList<IfcBlock>::it it;
};
class IfcBooleanClippingResult : public IfcBooleanResult {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBooleanClippingResult (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBooleanClippingResult* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBooleanClippingResult> > list;
    typedef IfcTemplatedEntityList<IfcBooleanClippingResult>::it it;
};
class IfcBoundedCurve : public IfcCurve {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoundedCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoundedCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundedCurve> > list;
    typedef IfcTemplatedEntityList<IfcBoundedCurve>::it it;
};
class IfcBuilding : public IfcSpatialStructureElement {
public:
    bool hasElevationOfRefHeight();
    IfcLengthMeasure ElevationOfRefHeight();
    bool hasElevationOfTerrain();
    IfcLengthMeasure ElevationOfTerrain();
    bool hasBuildingAddress();
    IfcPostalAddress* BuildingAddress();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuilding (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuilding* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuilding> > list;
    typedef IfcTemplatedEntityList<IfcBuilding>::it it;
};
class IfcBuildingElementType : public IfcElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuildingElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuildingElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementType> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementType>::it it;
};
class IfcBuildingStorey : public IfcSpatialStructureElement {
public:
    bool hasElevation();
    IfcLengthMeasure Elevation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuildingStorey (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuildingStorey* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingStorey> > list;
    typedef IfcTemplatedEntityList<IfcBuildingStorey>::it it;
};
class IfcCircleHollowProfileDef : public IfcCircleProfileDef {
public:
    IfcPositiveLengthMeasure WallThickness();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCircleHollowProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCircleHollowProfileDef* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCircleHollowProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCircleHollowProfileDef>::it it;
};
class IfcColumnType : public IfcBuildingElementType {
public:
    IfcColumnTypeEnum::IfcColumnTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcColumnType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcColumnType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColumnType> > list;
    typedef IfcTemplatedEntityList<IfcColumnType>::it it;
};
class IfcCompositeCurve : public IfcBoundedCurve {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurveSegment> > Segments();
    bool SelfIntersect();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCompositeCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCompositeCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurve> > list;
    typedef IfcTemplatedEntityList<IfcCompositeCurve>::it it;
};
class IfcConic : public IfcCurve {
public:
    IfcAxis2Placement Position();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConic (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConic* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConic> > list;
    typedef IfcTemplatedEntityList<IfcConic>::it it;
};
class IfcConstructionResource : public IfcResource {
public:
    bool hasResourceIdentifier();
    IfcIdentifier ResourceIdentifier();
    bool hasResourceGroup();
    IfcLabel ResourceGroup();
    bool hasResourceConsumption();
    IfcResourceConsumptionEnum::IfcResourceConsumptionEnum ResourceConsumption();
    bool hasBaseQuantity();
    IfcMeasureWithUnit* BaseQuantity();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstructionResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstructionResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionResource>::it it;
};
class IfcControl : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToControl> > Controls(); // INVERSE IfcRelAssignsToControl::RelatingControl
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcControl* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcControl> > list;
    typedef IfcTemplatedEntityList<IfcControl>::it it;
};
class IfcCostItem : public IfcControl {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCostItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCostItem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCostItem> > list;
    typedef IfcTemplatedEntityList<IfcCostItem>::it it;
};
class IfcCostSchedule : public IfcControl {
public:
    bool hasSubmittedBy();
    IfcActorSelect SubmittedBy();
    bool hasPreparedBy();
    IfcActorSelect PreparedBy();
    bool hasSubmittedOn();
    IfcDateTimeSelect SubmittedOn();
    bool hasStatus();
    IfcLabel Status();
    bool hasTargetUsers();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > TargetUsers();
    bool hasUpdateDate();
    IfcDateTimeSelect UpdateDate();
    IfcIdentifier ID();
    IfcCostScheduleTypeEnum::IfcCostScheduleTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCostSchedule (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCostSchedule* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCostSchedule> > list;
    typedef IfcTemplatedEntityList<IfcCostSchedule>::it it;
};
class IfcCoveringType : public IfcBuildingElementType {
public:
    IfcCoveringTypeEnum::IfcCoveringTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCoveringType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCoveringType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoveringType> > list;
    typedef IfcTemplatedEntityList<IfcCoveringType>::it it;
};
class IfcCrewResource : public IfcConstructionResource {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCrewResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCrewResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCrewResource> > list;
    typedef IfcTemplatedEntityList<IfcCrewResource>::it it;
};
class IfcCurtainWallType : public IfcBuildingElementType {
public:
    IfcCurtainWallTypeEnum::IfcCurtainWallTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurtainWallType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurtainWallType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurtainWallType> > list;
    typedef IfcTemplatedEntityList<IfcCurtainWallType>::it it;
};
class IfcDimensionCurveDirectedCallout : public IfcDraughtingCallout {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDimensionCurveDirectedCallout (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDimensionCurveDirectedCallout* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCurveDirectedCallout> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCurveDirectedCallout>::it it;
};
class IfcDistributionElementType : public IfcElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionElementType> > list;
    typedef IfcTemplatedEntityList<IfcDistributionElementType>::it it;
};
class IfcDistributionFlowElementType : public IfcDistributionElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionFlowElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionFlowElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionFlowElementType> > list;
    typedef IfcTemplatedEntityList<IfcDistributionFlowElementType>::it it;
};
class IfcElectricalBaseProperties : public IfcEnergyProperties {
public:
    bool hasElectricCurrentType();
    IfcElectricCurrentEnum::IfcElectricCurrentEnum ElectricCurrentType();
    IfcElectricVoltageMeasure InputVoltage();
    IfcFrequencyMeasure InputFrequency();
    bool hasFullLoadCurrent();
    IfcElectricCurrentMeasure FullLoadCurrent();
    bool hasMinimumCircuitCurrent();
    IfcElectricCurrentMeasure MinimumCircuitCurrent();
    bool hasMaximumPowerInput();
    IfcPowerMeasure MaximumPowerInput();
    bool hasRatedPowerInput();
    IfcPowerMeasure RatedPowerInput();
    int InputPhase();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricalBaseProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricalBaseProperties* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricalBaseProperties> > list;
    typedef IfcTemplatedEntityList<IfcElectricalBaseProperties>::it it;
};
class IfcElement : public IfcProduct {
public:
    bool hasTag();
    IfcIdentifier Tag();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralElement> > HasStructuralMember(); // INVERSE IfcRelConnectsStructuralElement::RelatingElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelFillsElement> > FillsVoids(); // INVERSE IfcRelFillsElement::RelatedBuildingElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsElements> > ConnectedTo(); // INVERSE IfcRelConnectsElements::RelatingElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversBldgElements> > HasCoverings(); // INVERSE IfcRelCoversBldgElements::RelatingBuildingElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelProjectsElement> > HasProjections(); // INVERSE IfcRelProjectsElement::RelatingElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelReferencedInSpatialStructure> > ReferencedInStructures(); // INVERSE IfcRelReferencedInSpatialStructure::RelatedElements
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPortToElement> > HasPorts(); // INVERSE IfcRelConnectsPortToElement::RelatedElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelVoidsElement> > HasOpenings(); // INVERSE IfcRelVoidsElement::RelatingBuildingElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsWithRealizingElements> > IsConnectionRealization(); // INVERSE IfcRelConnectsWithRealizingElements::RealizingElements
    SHARED_PTR< IfcTemplatedEntityList<IfcRelSpaceBoundary> > ProvidesBoundaries(); // INVERSE IfcRelSpaceBoundary::RelatedBuildingElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsElements> > ConnectedFrom(); // INVERSE IfcRelConnectsElements::RelatedElement
    SHARED_PTR< IfcTemplatedEntityList<IfcRelContainedInSpatialStructure> > ContainedInStructure(); // INVERSE IfcRelContainedInSpatialStructure::RelatedElements
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElement> > list;
    typedef IfcTemplatedEntityList<IfcElement>::it it;
};
class IfcElementAssembly : public IfcElement {
public:
    bool hasAssemblyPlace();
    IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum AssemblyPlace();
    IfcElementAssemblyTypeEnum::IfcElementAssemblyTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElementAssembly (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElementAssembly* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementAssembly> > list;
    typedef IfcTemplatedEntityList<IfcElementAssembly>::it it;
};
class IfcElementComponent : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElementComponent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElementComponent* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementComponent> > list;
    typedef IfcTemplatedEntityList<IfcElementComponent>::it it;
};
class IfcElementComponentType : public IfcElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElementComponentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElementComponentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementComponentType> > list;
    typedef IfcTemplatedEntityList<IfcElementComponentType>::it it;
};
class IfcEllipse : public IfcConic {
public:
    IfcPositiveLengthMeasure SemiAxis1();
    IfcPositiveLengthMeasure SemiAxis2();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEllipse (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEllipse* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEllipse> > list;
    typedef IfcTemplatedEntityList<IfcEllipse>::it it;
};
class IfcEnergyConversionDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEnergyConversionDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEnergyConversionDeviceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEnergyConversionDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcEnergyConversionDeviceType>::it it;
};
class IfcEquipmentElement : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEquipmentElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEquipmentElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEquipmentElement> > list;
    typedef IfcTemplatedEntityList<IfcEquipmentElement>::it it;
};
class IfcEquipmentStandard : public IfcControl {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEquipmentStandard (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEquipmentStandard* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEquipmentStandard> > list;
    typedef IfcTemplatedEntityList<IfcEquipmentStandard>::it it;
};
class IfcEvaporativeCoolerType : public IfcEnergyConversionDeviceType {
public:
    IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEvaporativeCoolerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEvaporativeCoolerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEvaporativeCoolerType> > list;
    typedef IfcTemplatedEntityList<IfcEvaporativeCoolerType>::it it;
};
class IfcEvaporatorType : public IfcEnergyConversionDeviceType {
public:
    IfcEvaporatorTypeEnum::IfcEvaporatorTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEvaporatorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEvaporatorType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEvaporatorType> > list;
    typedef IfcTemplatedEntityList<IfcEvaporatorType>::it it;
};
class IfcFacetedBrep : public IfcManifoldSolidBrep {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFacetedBrep (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFacetedBrep* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFacetedBrep> > list;
    typedef IfcTemplatedEntityList<IfcFacetedBrep>::it it;
};
class IfcFacetedBrepWithVoids : public IfcManifoldSolidBrep {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcClosedShell> > Voids();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFacetedBrepWithVoids (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFacetedBrepWithVoids* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFacetedBrepWithVoids> > list;
    typedef IfcTemplatedEntityList<IfcFacetedBrepWithVoids>::it it;
};
class IfcFastener : public IfcElementComponent {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFastener (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFastener* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFastener> > list;
    typedef IfcTemplatedEntityList<IfcFastener>::it it;
};
class IfcFastenerType : public IfcElementComponentType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFastenerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFastenerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFastenerType> > list;
    typedef IfcTemplatedEntityList<IfcFastenerType>::it it;
};
class IfcFeatureElement : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFeatureElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFeatureElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFeatureElement> > list;
    typedef IfcTemplatedEntityList<IfcFeatureElement>::it it;
};
class IfcFeatureElementAddition : public IfcFeatureElement {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelProjectsElement> > ProjectsElements(); // INVERSE IfcRelProjectsElement::RelatedFeatureElement
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFeatureElementAddition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFeatureElementAddition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFeatureElementAddition> > list;
    typedef IfcTemplatedEntityList<IfcFeatureElementAddition>::it it;
};
class IfcFeatureElementSubtraction : public IfcFeatureElement {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelVoidsElement> > VoidsElements(); // INVERSE IfcRelVoidsElement::RelatedOpeningElement
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFeatureElementSubtraction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFeatureElementSubtraction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFeatureElementSubtraction> > list;
    typedef IfcTemplatedEntityList<IfcFeatureElementSubtraction>::it it;
};
class IfcFlowControllerType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowControllerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowControllerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowControllerType> > list;
    typedef IfcTemplatedEntityList<IfcFlowControllerType>::it it;
};
class IfcFlowFittingType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowFittingType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowFittingType> > list;
    typedef IfcTemplatedEntityList<IfcFlowFittingType>::it it;
};
class IfcFlowMeterType : public IfcFlowControllerType {
public:
    IfcFlowMeterTypeEnum::IfcFlowMeterTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowMeterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowMeterType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowMeterType> > list;
    typedef IfcTemplatedEntityList<IfcFlowMeterType>::it it;
};
class IfcFlowMovingDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowMovingDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowMovingDeviceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowMovingDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcFlowMovingDeviceType>::it it;
};
class IfcFlowSegmentType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowSegmentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcFlowSegmentType>::it it;
};
class IfcFlowStorageDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowStorageDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowStorageDeviceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowStorageDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcFlowStorageDeviceType>::it it;
};
class IfcFlowTerminalType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowTerminalType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcFlowTerminalType>::it it;
};
class IfcFlowTreatmentDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowTreatmentDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowTreatmentDeviceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTreatmentDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcFlowTreatmentDeviceType>::it it;
};
class IfcFurnishingElement : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFurnishingElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFurnishingElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnishingElement> > list;
    typedef IfcTemplatedEntityList<IfcFurnishingElement>::it it;
};
class IfcFurnitureStandard : public IfcControl {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFurnitureStandard (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFurnitureStandard* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnitureStandard> > list;
    typedef IfcTemplatedEntityList<IfcFurnitureStandard>::it it;
};
class IfcGasTerminalType : public IfcFlowTerminalType {
public:
    IfcGasTerminalTypeEnum::IfcGasTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGasTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGasTerminalType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGasTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcGasTerminalType>::it it;
};
class IfcGrid : public IfcProduct {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > UAxes();
    SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > VAxes();
    bool hasWAxes();
    SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > WAxes();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelContainedInSpatialStructure> > ContainedInStructure(); // INVERSE IfcRelContainedInSpatialStructure::RelatedElements
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGrid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGrid* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > list;
    typedef IfcTemplatedEntityList<IfcGrid>::it it;
};
class IfcGroup : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToGroup> > IsGroupedBy(); // INVERSE IfcRelAssignsToGroup::RelatingGroup
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcGroup* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGroup> > list;
    typedef IfcTemplatedEntityList<IfcGroup>::it it;
};
class IfcHeatExchangerType : public IfcEnergyConversionDeviceType {
public:
    IfcHeatExchangerTypeEnum::IfcHeatExchangerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcHeatExchangerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcHeatExchangerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcHeatExchangerType> > list;
    typedef IfcTemplatedEntityList<IfcHeatExchangerType>::it it;
};
class IfcHumidifierType : public IfcEnergyConversionDeviceType {
public:
    IfcHumidifierTypeEnum::IfcHumidifierTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcHumidifierType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcHumidifierType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcHumidifierType> > list;
    typedef IfcTemplatedEntityList<IfcHumidifierType>::it it;
};
class IfcInventory : public IfcGroup {
public:
    IfcInventoryTypeEnum::IfcInventoryTypeEnum InventoryType();
    IfcActorSelect Jurisdiction();
    SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > ResponsiblePersons();
    IfcCalendarDate* LastUpdateDate();
    bool hasCurrentValue();
    IfcCostValue* CurrentValue();
    bool hasOriginalValue();
    IfcCostValue* OriginalValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcInventory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcInventory* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcInventory> > list;
    typedef IfcTemplatedEntityList<IfcInventory>::it it;
};
class IfcJunctionBoxType : public IfcFlowFittingType {
public:
    IfcJunctionBoxTypeEnum::IfcJunctionBoxTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcJunctionBoxType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcJunctionBoxType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcJunctionBoxType> > list;
    typedef IfcTemplatedEntityList<IfcJunctionBoxType>::it it;
};
class IfcLaborResource : public IfcConstructionResource {
public:
    bool hasSkillSet();
    IfcText SkillSet();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLaborResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLaborResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLaborResource> > list;
    typedef IfcTemplatedEntityList<IfcLaborResource>::it it;
};
class IfcLampType : public IfcFlowTerminalType {
public:
    IfcLampTypeEnum::IfcLampTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLampType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLampType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLampType> > list;
    typedef IfcTemplatedEntityList<IfcLampType>::it it;
};
class IfcLightFixtureType : public IfcFlowTerminalType {
public:
    IfcLightFixtureTypeEnum::IfcLightFixtureTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLightFixtureType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLightFixtureType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightFixtureType> > list;
    typedef IfcTemplatedEntityList<IfcLightFixtureType>::it it;
};
class IfcLinearDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcLinearDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcLinearDimension* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLinearDimension> > list;
    typedef IfcTemplatedEntityList<IfcLinearDimension>::it it;
};
class IfcMechanicalFastener : public IfcFastener {
public:
    bool hasNominalDiameter();
    IfcPositiveLengthMeasure NominalDiameter();
    bool hasNominalLength();
    IfcPositiveLengthMeasure NominalLength();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMechanicalFastener (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMechanicalFastener* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalFastener> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalFastener>::it it;
};
class IfcMechanicalFastenerType : public IfcFastenerType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMechanicalFastenerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMechanicalFastenerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalFastenerType> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalFastenerType>::it it;
};
class IfcMemberType : public IfcBuildingElementType {
public:
    IfcMemberTypeEnum::IfcMemberTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMemberType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMemberType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMemberType> > list;
    typedef IfcTemplatedEntityList<IfcMemberType>::it it;
};
class IfcMotorConnectionType : public IfcEnergyConversionDeviceType {
public:
    IfcMotorConnectionTypeEnum::IfcMotorConnectionTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMotorConnectionType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMotorConnectionType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMotorConnectionType> > list;
    typedef IfcTemplatedEntityList<IfcMotorConnectionType>::it it;
};
class IfcMove : public IfcTask {
public:
    IfcSpatialStructureElement* MoveFrom();
    IfcSpatialStructureElement* MoveTo();
    bool hasPunchList();
    std::vector<IfcText> /*[1:?]*/ PunchList();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMove (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMove* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMove> > list;
    typedef IfcTemplatedEntityList<IfcMove>::it it;
};
class IfcOccupant : public IfcActor {
public:
    IfcOccupantTypeEnum::IfcOccupantTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOccupant (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOccupant* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOccupant> > list;
    typedef IfcTemplatedEntityList<IfcOccupant>::it it;
};
class IfcOpeningElement : public IfcFeatureElementSubtraction {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelFillsElement> > HasFillings(); // INVERSE IfcRelFillsElement::RelatingOpeningElement
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOpeningElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOpeningElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOpeningElement> > list;
    typedef IfcTemplatedEntityList<IfcOpeningElement>::it it;
};
class IfcOrderAction : public IfcTask {
public:
    IfcIdentifier ActionID();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOrderAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOrderAction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrderAction> > list;
    typedef IfcTemplatedEntityList<IfcOrderAction>::it it;
};
class IfcOutletType : public IfcFlowTerminalType {
public:
    IfcOutletTypeEnum::IfcOutletTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcOutletType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcOutletType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOutletType> > list;
    typedef IfcTemplatedEntityList<IfcOutletType>::it it;
};
class IfcPerformanceHistory : public IfcControl {
public:
    IfcLabel LifeCyclePhase();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPerformanceHistory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPerformanceHistory* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPerformanceHistory> > list;
    typedef IfcTemplatedEntityList<IfcPerformanceHistory>::it it;
};
class IfcPermit : public IfcControl {
public:
    IfcIdentifier PermitID();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPermit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPermit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPermit> > list;
    typedef IfcTemplatedEntityList<IfcPermit>::it it;
};
class IfcPipeFittingType : public IfcFlowFittingType {
public:
    IfcPipeFittingTypeEnum::IfcPipeFittingTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPipeFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPipeFittingType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPipeFittingType> > list;
    typedef IfcTemplatedEntityList<IfcPipeFittingType>::it it;
};
class IfcPipeSegmentType : public IfcFlowSegmentType {
public:
    IfcPipeSegmentTypeEnum::IfcPipeSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPipeSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPipeSegmentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPipeSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcPipeSegmentType>::it it;
};
class IfcPlateType : public IfcBuildingElementType {
public:
    IfcPlateTypeEnum::IfcPlateTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPlateType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPlateType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlateType> > list;
    typedef IfcTemplatedEntityList<IfcPlateType>::it it;
};
class IfcPolyline : public IfcBoundedCurve {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > Points();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPolyline (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPolyline* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPolyline> > list;
    typedef IfcTemplatedEntityList<IfcPolyline>::it it;
};
class IfcPort : public IfcProduct {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPortToElement> > ContainedIn(); // INVERSE IfcRelConnectsPortToElement::RelatingPort
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPorts> > ConnectedFrom(); // INVERSE IfcRelConnectsPorts::RelatedPort
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPorts> > ConnectedTo(); // INVERSE IfcRelConnectsPorts::RelatingPort
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPort (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPort* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPort> > list;
    typedef IfcTemplatedEntityList<IfcPort>::it it;
};
class IfcProcedure : public IfcProcess {
public:
    IfcIdentifier ProcedureID();
    IfcProcedureTypeEnum::IfcProcedureTypeEnum ProcedureType();
    bool hasUserDefinedProcedureType();
    IfcLabel UserDefinedProcedureType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProcedure (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProcedure* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProcedure> > list;
    typedef IfcTemplatedEntityList<IfcProcedure>::it it;
};
class IfcProjectOrder : public IfcControl {
public:
    IfcIdentifier ID();
    IfcProjectOrderTypeEnum::IfcProjectOrderTypeEnum PredefinedType();
    bool hasStatus();
    IfcLabel Status();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProjectOrder (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProjectOrder* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectOrder> > list;
    typedef IfcTemplatedEntityList<IfcProjectOrder>::it it;
};
class IfcProjectOrderRecord : public IfcControl {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProjectOrder> > Records();
    IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProjectOrderRecord (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProjectOrderRecord* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectOrderRecord> > list;
    typedef IfcTemplatedEntityList<IfcProjectOrderRecord>::it it;
};
class IfcProjectionElement : public IfcFeatureElementAddition {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProjectionElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProjectionElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectionElement> > list;
    typedef IfcTemplatedEntityList<IfcProjectionElement>::it it;
};
class IfcProtectiveDeviceType : public IfcFlowControllerType {
public:
    IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcProtectiveDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcProtectiveDeviceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProtectiveDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcProtectiveDeviceType>::it it;
};
class IfcPumpType : public IfcFlowMovingDeviceType {
public:
    IfcPumpTypeEnum::IfcPumpTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPumpType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPumpType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPumpType> > list;
    typedef IfcTemplatedEntityList<IfcPumpType>::it it;
};
class IfcRadiusDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRadiusDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRadiusDimension* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRadiusDimension> > list;
    typedef IfcTemplatedEntityList<IfcRadiusDimension>::it it;
};
class IfcRailingType : public IfcBuildingElementType {
public:
    IfcRailingTypeEnum::IfcRailingTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRailingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRailingType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRailingType> > list;
    typedef IfcTemplatedEntityList<IfcRailingType>::it it;
};
class IfcRampFlightType : public IfcBuildingElementType {
public:
    IfcRampFlightTypeEnum::IfcRampFlightTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRampFlightType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRampFlightType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRampFlightType> > list;
    typedef IfcTemplatedEntityList<IfcRampFlightType>::it it;
};
class IfcRelAggregates : public IfcRelDecomposes {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAggregates (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAggregates* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAggregates> > list;
    typedef IfcTemplatedEntityList<IfcRelAggregates>::it it;
};
class IfcRelAssignsTasks : public IfcRelAssignsToControl {
public:
    bool hasTimeForTask();
    IfcScheduleTimeControl* TimeForTask();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRelAssignsTasks (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRelAssignsTasks* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsTasks> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsTasks>::it it;
};
class IfcSanitaryTerminalType : public IfcFlowTerminalType {
public:
    IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSanitaryTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSanitaryTerminalType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSanitaryTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcSanitaryTerminalType>::it it;
};
class IfcScheduleTimeControl : public IfcControl {
public:
    bool hasActualStart();
    IfcDateTimeSelect ActualStart();
    bool hasEarlyStart();
    IfcDateTimeSelect EarlyStart();
    bool hasLateStart();
    IfcDateTimeSelect LateStart();
    bool hasScheduleStart();
    IfcDateTimeSelect ScheduleStart();
    bool hasActualFinish();
    IfcDateTimeSelect ActualFinish();
    bool hasEarlyFinish();
    IfcDateTimeSelect EarlyFinish();
    bool hasLateFinish();
    IfcDateTimeSelect LateFinish();
    bool hasScheduleFinish();
    IfcDateTimeSelect ScheduleFinish();
    bool hasScheduleDuration();
    IfcTimeMeasure ScheduleDuration();
    bool hasActualDuration();
    IfcTimeMeasure ActualDuration();
    bool hasRemainingTime();
    IfcTimeMeasure RemainingTime();
    bool hasFreeFloat();
    IfcTimeMeasure FreeFloat();
    bool hasTotalFloat();
    IfcTimeMeasure TotalFloat();
    bool hasIsCritical();
    bool IsCritical();
    bool hasStatusTime();
    IfcDateTimeSelect StatusTime();
    bool hasStartFloat();
    IfcTimeMeasure StartFloat();
    bool hasFinishFloat();
    IfcTimeMeasure FinishFloat();
    bool hasCompletion();
    IfcPositiveRatioMeasure Completion();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsTasks> > ScheduleTimeControlAssigned(); // INVERSE IfcRelAssignsTasks::TimeForTask
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcScheduleTimeControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcScheduleTimeControl* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcScheduleTimeControl> > list;
    typedef IfcTemplatedEntityList<IfcScheduleTimeControl>::it it;
};
class IfcServiceLife : public IfcControl {
public:
    IfcServiceLifeTypeEnum::IfcServiceLifeTypeEnum ServiceLifeType();
    IfcTimeMeasure ServiceLifeDuration();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcServiceLife (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcServiceLife* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcServiceLife> > list;
    typedef IfcTemplatedEntityList<IfcServiceLife>::it it;
};
class IfcSite : public IfcSpatialStructureElement {
public:
    bool hasRefLatitude();
    IfcCompoundPlaneAngleMeasure RefLatitude();
    bool hasRefLongitude();
    IfcCompoundPlaneAngleMeasure RefLongitude();
    bool hasRefElevation();
    IfcLengthMeasure RefElevation();
    bool hasLandTitleNumber();
    IfcLabel LandTitleNumber();
    bool hasSiteAddress();
    IfcPostalAddress* SiteAddress();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSite (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSite* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSite> > list;
    typedef IfcTemplatedEntityList<IfcSite>::it it;
};
class IfcSlabType : public IfcBuildingElementType {
public:
    IfcSlabTypeEnum::IfcSlabTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSlabType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSlabType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSlabType> > list;
    typedef IfcTemplatedEntityList<IfcSlabType>::it it;
};
class IfcSpace : public IfcSpatialStructureElement {
public:
    IfcInternalOrExternalEnum::IfcInternalOrExternalEnum InteriorOrExteriorSpace();
    bool hasElevationWithFlooring();
    IfcLengthMeasure ElevationWithFlooring();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversSpaces> > HasCoverings(); // INVERSE IfcRelCoversSpaces::RelatedSpace
    SHARED_PTR< IfcTemplatedEntityList<IfcRelSpaceBoundary> > BoundedBy(); // INVERSE IfcRelSpaceBoundary::RelatingSpace
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSpace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSpace* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpace> > list;
    typedef IfcTemplatedEntityList<IfcSpace>::it it;
};
class IfcSpaceHeaterType : public IfcEnergyConversionDeviceType {
public:
    IfcSpaceHeaterTypeEnum::IfcSpaceHeaterTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSpaceHeaterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSpaceHeaterType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpaceHeaterType> > list;
    typedef IfcTemplatedEntityList<IfcSpaceHeaterType>::it it;
};
class IfcSpaceProgram : public IfcControl {
public:
    IfcIdentifier SpaceProgramIdentifier();
    bool hasMaxRequiredArea();
    IfcAreaMeasure MaxRequiredArea();
    bool hasMinRequiredArea();
    IfcAreaMeasure MinRequiredArea();
    bool hasRequestedLocation();
    IfcSpatialStructureElement* RequestedLocation();
    IfcAreaMeasure StandardRequiredArea();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelInteractionRequirements> > HasInteractionReqsFrom(); // INVERSE IfcRelInteractionRequirements::RelatedSpaceProgram
    SHARED_PTR< IfcTemplatedEntityList<IfcRelInteractionRequirements> > HasInteractionReqsTo(); // INVERSE IfcRelInteractionRequirements::RelatingSpaceProgram
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSpaceProgram (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSpaceProgram* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpaceProgram> > list;
    typedef IfcTemplatedEntityList<IfcSpaceProgram>::it it;
};
class IfcSpaceType : public IfcSpatialStructureElementType {
public:
    IfcSpaceTypeEnum::IfcSpaceTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSpaceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSpaceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpaceType> > list;
    typedef IfcTemplatedEntityList<IfcSpaceType>::it it;
};
class IfcStackTerminalType : public IfcFlowTerminalType {
public:
    IfcStackTerminalTypeEnum::IfcStackTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStackTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStackTerminalType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStackTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcStackTerminalType>::it it;
};
class IfcStairFlightType : public IfcBuildingElementType {
public:
    IfcStairFlightTypeEnum::IfcStairFlightTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStairFlightType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStairFlightType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStairFlightType> > list;
    typedef IfcTemplatedEntityList<IfcStairFlightType>::it it;
};
class IfcStructuralAction : public IfcStructuralActivity {
public:
    bool DestabilizingLoad();
    bool hasCausedBy();
    IfcStructuralReaction* CausedBy();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralAction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralAction>::it it;
};
class IfcStructuralConnection : public IfcStructuralItem {
public:
    bool hasAppliedCondition();
    IfcBoundaryCondition* AppliedCondition();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralMember> > ConnectsStructuralMembers(); // INVERSE IfcRelConnectsStructuralMember::RelatedStructuralConnection
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralConnection* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralConnection>::it it;
};
class IfcStructuralCurveConnection : public IfcStructuralConnection {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralCurveConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralCurveConnection* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralCurveConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralCurveConnection>::it it;
};
class IfcStructuralCurveMember : public IfcStructuralMember {
public:
    IfcStructuralCurveTypeEnum::IfcStructuralCurveTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralCurveMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralCurveMember* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralCurveMember> > list;
    typedef IfcTemplatedEntityList<IfcStructuralCurveMember>::it it;
};
class IfcStructuralCurveMemberVarying : public IfcStructuralCurveMember {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralCurveMemberVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralCurveMemberVarying* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralCurveMemberVarying> > list;
    typedef IfcTemplatedEntityList<IfcStructuralCurveMemberVarying>::it it;
};
class IfcStructuralLinearAction : public IfcStructuralAction {
public:
    IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum ProjectedOrTrue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLinearAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLinearAction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLinearAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLinearAction>::it it;
};
class IfcStructuralLinearActionVarying : public IfcStructuralLinearAction {
public:
    IfcShapeAspect* VaryingAppliedLoadLocation();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > SubsequentAppliedLoads();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLinearActionVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLinearActionVarying* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLinearActionVarying> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLinearActionVarying>::it it;
};
class IfcStructuralLoadGroup : public IfcGroup {
public:
    IfcLoadGroupTypeEnum::IfcLoadGroupTypeEnum PredefinedType();
    IfcActionTypeEnum::IfcActionTypeEnum ActionType();
    IfcActionSourceTypeEnum::IfcActionSourceTypeEnum ActionSource();
    bool hasCoefficient();
    IfcRatioMeasure Coefficient();
    bool hasPurpose();
    IfcLabel Purpose();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralResultGroup> > SourceOfResultGroup(); // INVERSE IfcStructuralResultGroup::ResultForLoadGroup
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAnalysisModel> > LoadGroupFor(); // INVERSE IfcStructuralAnalysisModel::LoadedBy
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralLoadGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralLoadGroup* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadGroup> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadGroup>::it it;
};
class IfcStructuralPlanarAction : public IfcStructuralAction {
public:
    IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum ProjectedOrTrue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralPlanarAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralPlanarAction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPlanarAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPlanarAction>::it it;
};
class IfcStructuralPlanarActionVarying : public IfcStructuralPlanarAction {
public:
    IfcShapeAspect* VaryingAppliedLoadLocation();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > SubsequentAppliedLoads();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralPlanarActionVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralPlanarActionVarying* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPlanarActionVarying> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPlanarActionVarying>::it it;
};
class IfcStructuralPointAction : public IfcStructuralAction {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralPointAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralPointAction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPointAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPointAction>::it it;
};
class IfcStructuralPointConnection : public IfcStructuralConnection {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralPointConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralPointConnection* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPointConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPointConnection>::it it;
};
class IfcStructuralPointReaction : public IfcStructuralReaction {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralPointReaction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralPointReaction* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPointReaction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPointReaction>::it it;
};
class IfcStructuralResultGroup : public IfcGroup {
public:
    IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryTypeEnum TheoryType();
    bool hasResultForLoadGroup();
    IfcStructuralLoadGroup* ResultForLoadGroup();
    bool IsLinear();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAnalysisModel> > ResultGroupFor(); // INVERSE IfcStructuralAnalysisModel::HasResults
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralResultGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralResultGroup* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralResultGroup> > list;
    typedef IfcTemplatedEntityList<IfcStructuralResultGroup>::it it;
};
class IfcStructuralSurfaceConnection : public IfcStructuralConnection {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralSurfaceConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralSurfaceConnection* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSurfaceConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSurfaceConnection>::it it;
};
class IfcSubContractResource : public IfcConstructionResource {
public:
    bool hasSubContractor();
    IfcActorSelect SubContractor();
    bool hasJobDescription();
    IfcText JobDescription();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSubContractResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSubContractResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSubContractResource> > list;
    typedef IfcTemplatedEntityList<IfcSubContractResource>::it it;
};
class IfcSwitchingDeviceType : public IfcFlowControllerType {
public:
    IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSwitchingDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSwitchingDeviceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSwitchingDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcSwitchingDeviceType>::it it;
};
class IfcSystem : public IfcGroup {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelServicesBuildings> > ServicesBuildings(); // INVERSE IfcRelServicesBuildings::RelatingSystem
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSystem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSystem* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSystem> > list;
    typedef IfcTemplatedEntityList<IfcSystem>::it it;
};
class IfcTankType : public IfcFlowStorageDeviceType {
public:
    IfcTankTypeEnum::IfcTankTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTankType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTankType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTankType> > list;
    typedef IfcTemplatedEntityList<IfcTankType>::it it;
};
class IfcTimeSeriesSchedule : public IfcControl {
public:
    bool hasApplicableDates();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ApplicableDates();
    IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleTypeEnum TimeSeriesScheduleType();
    IfcTimeSeries* TimeSeries();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTimeSeriesSchedule (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTimeSeriesSchedule* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesSchedule> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeriesSchedule>::it it;
};
class IfcTransformerType : public IfcEnergyConversionDeviceType {
public:
    IfcTransformerTypeEnum::IfcTransformerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTransformerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTransformerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTransformerType> > list;
    typedef IfcTemplatedEntityList<IfcTransformerType>::it it;
};
class IfcTransportElement : public IfcElement {
public:
    bool hasOperationType();
    IfcTransportElementTypeEnum::IfcTransportElementTypeEnum OperationType();
    bool hasCapacityByWeight();
    IfcMassMeasure CapacityByWeight();
    bool hasCapacityByNumber();
    IfcCountMeasure CapacityByNumber();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTransportElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTransportElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTransportElement> > list;
    typedef IfcTemplatedEntityList<IfcTransportElement>::it it;
};
class IfcTrimmedCurve : public IfcBoundedCurve {
public:
    IfcCurve* BasisCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Trim1();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Trim2();
    bool SenseAgreement();
    IfcTrimmingPreference::IfcTrimmingPreference MasterRepresentation();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTrimmedCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTrimmedCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTrimmedCurve> > list;
    typedef IfcTemplatedEntityList<IfcTrimmedCurve>::it it;
};
class IfcTubeBundleType : public IfcEnergyConversionDeviceType {
public:
    IfcTubeBundleTypeEnum::IfcTubeBundleTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTubeBundleType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTubeBundleType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTubeBundleType> > list;
    typedef IfcTemplatedEntityList<IfcTubeBundleType>::it it;
};
class IfcUnitaryEquipmentType : public IfcEnergyConversionDeviceType {
public:
    IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcUnitaryEquipmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcUnitaryEquipmentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcUnitaryEquipmentType> > list;
    typedef IfcTemplatedEntityList<IfcUnitaryEquipmentType>::it it;
};
class IfcValveType : public IfcFlowControllerType {
public:
    IfcValveTypeEnum::IfcValveTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcValveType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcValveType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcValveType> > list;
    typedef IfcTemplatedEntityList<IfcValveType>::it it;
};
class IfcVirtualElement : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVirtualElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVirtualElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVirtualElement> > list;
    typedef IfcTemplatedEntityList<IfcVirtualElement>::it it;
};
class IfcWallType : public IfcBuildingElementType {
public:
    IfcWallTypeEnum::IfcWallTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWallType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWallType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWallType> > list;
    typedef IfcTemplatedEntityList<IfcWallType>::it it;
};
class IfcWasteTerminalType : public IfcFlowTerminalType {
public:
    IfcWasteTerminalTypeEnum::IfcWasteTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWasteTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWasteTerminalType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWasteTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcWasteTerminalType>::it it;
};
class IfcWorkControl : public IfcControl {
public:
    IfcIdentifier Identifier();
    IfcDateTimeSelect CreationDate();
    bool hasCreators();
    SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > Creators();
    bool hasPurpose();
    IfcLabel Purpose();
    bool hasDuration();
    IfcTimeMeasure Duration();
    bool hasTotalFloat();
    IfcTimeMeasure TotalFloat();
    IfcDateTimeSelect StartTime();
    bool hasFinishTime();
    IfcDateTimeSelect FinishTime();
    bool hasWorkControlType();
    IfcWorkControlTypeEnum::IfcWorkControlTypeEnum WorkControlType();
    bool hasUserDefinedControlType();
    IfcLabel UserDefinedControlType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWorkControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWorkControl* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWorkControl> > list;
    typedef IfcTemplatedEntityList<IfcWorkControl>::it it;
};
class IfcWorkPlan : public IfcWorkControl {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWorkPlan (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWorkPlan* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWorkPlan> > list;
    typedef IfcTemplatedEntityList<IfcWorkPlan>::it it;
};
class IfcWorkSchedule : public IfcWorkControl {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWorkSchedule (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWorkSchedule* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWorkSchedule> > list;
    typedef IfcTemplatedEntityList<IfcWorkSchedule>::it it;
};
class IfcZone : public IfcGroup {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcZone (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcZone* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcZone> > list;
    typedef IfcTemplatedEntityList<IfcZone>::it it;
};
class Ifc2DCompositeCurve : public IfcCompositeCurve {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    Ifc2DCompositeCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef Ifc2DCompositeCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<Ifc2DCompositeCurve> > list;
    typedef IfcTemplatedEntityList<Ifc2DCompositeCurve>::it it;
};
class IfcActionRequest : public IfcControl {
public:
    IfcIdentifier RequestID();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcActionRequest (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcActionRequest* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcActionRequest> > list;
    typedef IfcTemplatedEntityList<IfcActionRequest>::it it;
};
class IfcAirTerminalBoxType : public IfcFlowControllerType {
public:
    IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAirTerminalBoxType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAirTerminalBoxType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAirTerminalBoxType> > list;
    typedef IfcTemplatedEntityList<IfcAirTerminalBoxType>::it it;
};
class IfcAirTerminalType : public IfcFlowTerminalType {
public:
    IfcAirTerminalTypeEnum::IfcAirTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAirTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAirTerminalType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAirTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcAirTerminalType>::it it;
};
class IfcAirToAirHeatRecoveryType : public IfcEnergyConversionDeviceType {
public:
    IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAirToAirHeatRecoveryType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAirToAirHeatRecoveryType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAirToAirHeatRecoveryType> > list;
    typedef IfcTemplatedEntityList<IfcAirToAirHeatRecoveryType>::it it;
};
class IfcAngularDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAngularDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAngularDimension* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAngularDimension> > list;
    typedef IfcTemplatedEntityList<IfcAngularDimension>::it it;
};
class IfcAsset : public IfcGroup {
public:
    IfcIdentifier AssetID();
    IfcCostValue* OriginalValue();
    IfcCostValue* CurrentValue();
    IfcCostValue* TotalReplacementCost();
    IfcActorSelect Owner();
    IfcActorSelect User();
    IfcPerson* ResponsiblePerson();
    IfcCalendarDate* IncorporationDate();
    IfcCostValue* DepreciatedValue();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAsset (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAsset* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAsset> > list;
    typedef IfcTemplatedEntityList<IfcAsset>::it it;
};
class IfcBSplineCurve : public IfcBoundedCurve {
public:
    int Degree();
    SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > ControlPointsList();
    IfcBSplineCurveForm::IfcBSplineCurveForm CurveForm();
    bool ClosedCurve();
    bool SelfIntersect();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBSplineCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBSplineCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBSplineCurve> > list;
    typedef IfcTemplatedEntityList<IfcBSplineCurve>::it it;
};
class IfcBeamType : public IfcBuildingElementType {
public:
    IfcBeamTypeEnum::IfcBeamTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBeamType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBeamType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBeamType> > list;
    typedef IfcTemplatedEntityList<IfcBeamType>::it it;
};
class IfcBezierCurve : public IfcBSplineCurve {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBezierCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBezierCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBezierCurve> > list;
    typedef IfcTemplatedEntityList<IfcBezierCurve>::it it;
};
class IfcBoilerType : public IfcEnergyConversionDeviceType {
public:
    IfcBoilerTypeEnum::IfcBoilerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBoilerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBoilerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoilerType> > list;
    typedef IfcTemplatedEntityList<IfcBoilerType>::it it;
};
class IfcBuildingElement : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuildingElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuildingElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElement> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElement>::it it;
};
class IfcBuildingElementComponent : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuildingElementComponent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuildingElementComponent* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementComponent> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementComponent>::it it;
};
class IfcBuildingElementPart : public IfcBuildingElementComponent {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuildingElementPart (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuildingElementPart* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementPart> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementPart>::it it;
};
class IfcBuildingElementProxy : public IfcBuildingElement {
public:
    bool hasCompositionType();
    IfcElementCompositionEnum::IfcElementCompositionEnum CompositionType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuildingElementProxy (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuildingElementProxy* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementProxy> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementProxy>::it it;
};
class IfcBuildingElementProxyType : public IfcBuildingElementType {
public:
    IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBuildingElementProxyType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBuildingElementProxyType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementProxyType> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementProxyType>::it it;
};
class IfcCableCarrierFittingType : public IfcFlowFittingType {
public:
    IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCableCarrierFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCableCarrierFittingType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCableCarrierFittingType> > list;
    typedef IfcTemplatedEntityList<IfcCableCarrierFittingType>::it it;
};
class IfcCableCarrierSegmentType : public IfcFlowSegmentType {
public:
    IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCableCarrierSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCableCarrierSegmentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCableCarrierSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcCableCarrierSegmentType>::it it;
};
class IfcCableSegmentType : public IfcFlowSegmentType {
public:
    IfcCableSegmentTypeEnum::IfcCableSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCableSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCableSegmentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCableSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcCableSegmentType>::it it;
};
class IfcChillerType : public IfcEnergyConversionDeviceType {
public:
    IfcChillerTypeEnum::IfcChillerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcChillerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcChillerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcChillerType> > list;
    typedef IfcTemplatedEntityList<IfcChillerType>::it it;
};
class IfcCircle : public IfcConic {
public:
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCircle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCircle* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCircle> > list;
    typedef IfcTemplatedEntityList<IfcCircle>::it it;
};
class IfcCoilType : public IfcEnergyConversionDeviceType {
public:
    IfcCoilTypeEnum::IfcCoilTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCoilType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCoilType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoilType> > list;
    typedef IfcTemplatedEntityList<IfcCoilType>::it it;
};
class IfcColumn : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcColumn (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcColumn* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColumn> > list;
    typedef IfcTemplatedEntityList<IfcColumn>::it it;
};
class IfcCompressorType : public IfcFlowMovingDeviceType {
public:
    IfcCompressorTypeEnum::IfcCompressorTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCompressorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCompressorType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCompressorType> > list;
    typedef IfcTemplatedEntityList<IfcCompressorType>::it it;
};
class IfcCondenserType : public IfcEnergyConversionDeviceType {
public:
    IfcCondenserTypeEnum::IfcCondenserTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCondenserType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCondenserType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCondenserType> > list;
    typedef IfcTemplatedEntityList<IfcCondenserType>::it it;
};
class IfcCondition : public IfcGroup {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCondition* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCondition> > list;
    typedef IfcTemplatedEntityList<IfcCondition>::it it;
};
class IfcConditionCriterion : public IfcControl {
public:
    IfcConditionCriterionSelect Criterion();
    IfcDateTimeSelect CriterionDateTime();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConditionCriterion (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConditionCriterion* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConditionCriterion> > list;
    typedef IfcTemplatedEntityList<IfcConditionCriterion>::it it;
};
class IfcConstructionEquipmentResource : public IfcConstructionResource {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstructionEquipmentResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstructionEquipmentResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionEquipmentResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionEquipmentResource>::it it;
};
class IfcConstructionMaterialResource : public IfcConstructionResource {
public:
    bool hasSuppliers();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Suppliers();
    bool hasUsageRatio();
    IfcRatioMeasure UsageRatio();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstructionMaterialResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstructionMaterialResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionMaterialResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionMaterialResource>::it it;
};
class IfcConstructionProductResource : public IfcConstructionResource {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcConstructionProductResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcConstructionProductResource* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionProductResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionProductResource>::it it;
};
class IfcCooledBeamType : public IfcEnergyConversionDeviceType {
public:
    IfcCooledBeamTypeEnum::IfcCooledBeamTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCooledBeamType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCooledBeamType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCooledBeamType> > list;
    typedef IfcTemplatedEntityList<IfcCooledBeamType>::it it;
};
class IfcCoolingTowerType : public IfcEnergyConversionDeviceType {
public:
    IfcCoolingTowerTypeEnum::IfcCoolingTowerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCoolingTowerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCoolingTowerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoolingTowerType> > list;
    typedef IfcTemplatedEntityList<IfcCoolingTowerType>::it it;
};
class IfcCovering : public IfcBuildingElement {
public:
    bool hasPredefinedType();
    IfcCoveringTypeEnum::IfcCoveringTypeEnum PredefinedType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversSpaces> > CoversSpaces(); // INVERSE IfcRelCoversSpaces::RelatedCoverings
    SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversBldgElements> > Covers(); // INVERSE IfcRelCoversBldgElements::RelatedCoverings
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCovering (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCovering* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > list;
    typedef IfcTemplatedEntityList<IfcCovering>::it it;
};
class IfcCurtainWall : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcCurtainWall (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcCurtainWall* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurtainWall> > list;
    typedef IfcTemplatedEntityList<IfcCurtainWall>::it it;
};
class IfcDamperType : public IfcFlowControllerType {
public:
    IfcDamperTypeEnum::IfcDamperTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDamperType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDamperType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDamperType> > list;
    typedef IfcTemplatedEntityList<IfcDamperType>::it it;
};
class IfcDiameterDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDiameterDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDiameterDimension* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDiameterDimension> > list;
    typedef IfcTemplatedEntityList<IfcDiameterDimension>::it it;
};
class IfcDiscreteAccessory : public IfcElementComponent {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDiscreteAccessory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDiscreteAccessory* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDiscreteAccessory> > list;
    typedef IfcTemplatedEntityList<IfcDiscreteAccessory>::it it;
};
class IfcDiscreteAccessoryType : public IfcElementComponentType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDiscreteAccessoryType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDiscreteAccessoryType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDiscreteAccessoryType> > list;
    typedef IfcTemplatedEntityList<IfcDiscreteAccessoryType>::it it;
};
class IfcDistributionChamberElementType : public IfcDistributionFlowElementType {
public:
    IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionChamberElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionChamberElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionChamberElementType> > list;
    typedef IfcTemplatedEntityList<IfcDistributionChamberElementType>::it it;
};
class IfcDistributionControlElementType : public IfcDistributionElementType {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionControlElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionControlElementType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElementType> > list;
    typedef IfcTemplatedEntityList<IfcDistributionControlElementType>::it it;
};
class IfcDistributionElement : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionElement>::it it;
};
class IfcDistributionFlowElement : public IfcDistributionElement {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelFlowControlElements> > HasControlElements(); // INVERSE IfcRelFlowControlElements::RelatingFlowElement
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionFlowElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionFlowElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionFlowElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionFlowElement>::it it;
};
class IfcDistributionPort : public IfcPort {
public:
    bool hasFlowDirection();
    IfcFlowDirectionEnum::IfcFlowDirectionEnum FlowDirection();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionPort (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionPort* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionPort> > list;
    typedef IfcTemplatedEntityList<IfcDistributionPort>::it it;
};
class IfcDoor : public IfcBuildingElement {
public:
    bool hasOverallHeight();
    IfcPositiveLengthMeasure OverallHeight();
    bool hasOverallWidth();
    IfcPositiveLengthMeasure OverallWidth();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDoor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDoor* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDoor> > list;
    typedef IfcTemplatedEntityList<IfcDoor>::it it;
};
class IfcDuctFittingType : public IfcFlowFittingType {
public:
    IfcDuctFittingTypeEnum::IfcDuctFittingTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDuctFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDuctFittingType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDuctFittingType> > list;
    typedef IfcTemplatedEntityList<IfcDuctFittingType>::it it;
};
class IfcDuctSegmentType : public IfcFlowSegmentType {
public:
    IfcDuctSegmentTypeEnum::IfcDuctSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDuctSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDuctSegmentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDuctSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcDuctSegmentType>::it it;
};
class IfcDuctSilencerType : public IfcFlowTreatmentDeviceType {
public:
    IfcDuctSilencerTypeEnum::IfcDuctSilencerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDuctSilencerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDuctSilencerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDuctSilencerType> > list;
    typedef IfcTemplatedEntityList<IfcDuctSilencerType>::it it;
};
class IfcEdgeFeature : public IfcFeatureElementSubtraction {
public:
    bool hasFeatureLength();
    IfcPositiveLengthMeasure FeatureLength();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEdgeFeature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEdgeFeature* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdgeFeature> > list;
    typedef IfcTemplatedEntityList<IfcEdgeFeature>::it it;
};
class IfcElectricApplianceType : public IfcFlowTerminalType {
public:
    IfcElectricApplianceTypeEnum::IfcElectricApplianceTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricApplianceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricApplianceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricApplianceType> > list;
    typedef IfcTemplatedEntityList<IfcElectricApplianceType>::it it;
};
class IfcElectricFlowStorageDeviceType : public IfcFlowStorageDeviceType {
public:
    IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricFlowStorageDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricFlowStorageDeviceType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricFlowStorageDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcElectricFlowStorageDeviceType>::it it;
};
class IfcElectricGeneratorType : public IfcEnergyConversionDeviceType {
public:
    IfcElectricGeneratorTypeEnum::IfcElectricGeneratorTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricGeneratorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricGeneratorType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricGeneratorType> > list;
    typedef IfcTemplatedEntityList<IfcElectricGeneratorType>::it it;
};
class IfcElectricHeaterType : public IfcFlowTerminalType {
public:
    IfcElectricHeaterTypeEnum::IfcElectricHeaterTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricHeaterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricHeaterType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricHeaterType> > list;
    typedef IfcTemplatedEntityList<IfcElectricHeaterType>::it it;
};
class IfcElectricMotorType : public IfcEnergyConversionDeviceType {
public:
    IfcElectricMotorTypeEnum::IfcElectricMotorTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricMotorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricMotorType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricMotorType> > list;
    typedef IfcTemplatedEntityList<IfcElectricMotorType>::it it;
};
class IfcElectricTimeControlType : public IfcFlowControllerType {
public:
    IfcElectricTimeControlTypeEnum::IfcElectricTimeControlTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricTimeControlType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricTimeControlType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricTimeControlType> > list;
    typedef IfcTemplatedEntityList<IfcElectricTimeControlType>::it it;
};
class IfcElectricalCircuit : public IfcSystem {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricalCircuit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricalCircuit* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricalCircuit> > list;
    typedef IfcTemplatedEntityList<IfcElectricalCircuit>::it it;
};
class IfcElectricalElement : public IfcElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricalElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricalElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricalElement> > list;
    typedef IfcTemplatedEntityList<IfcElectricalElement>::it it;
};
class IfcEnergyConversionDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcEnergyConversionDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcEnergyConversionDevice* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEnergyConversionDevice> > list;
    typedef IfcTemplatedEntityList<IfcEnergyConversionDevice>::it it;
};
class IfcFanType : public IfcFlowMovingDeviceType {
public:
    IfcFanTypeEnum::IfcFanTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFanType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFanType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFanType> > list;
    typedef IfcTemplatedEntityList<IfcFanType>::it it;
};
class IfcFilterType : public IfcFlowTreatmentDeviceType {
public:
    IfcFilterTypeEnum::IfcFilterTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFilterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFilterType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFilterType> > list;
    typedef IfcTemplatedEntityList<IfcFilterType>::it it;
};
class IfcFireSuppressionTerminalType : public IfcFlowTerminalType {
public:
    IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFireSuppressionTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFireSuppressionTerminalType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFireSuppressionTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcFireSuppressionTerminalType>::it it;
};
class IfcFlowController : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowController (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowController* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowController> > list;
    typedef IfcTemplatedEntityList<IfcFlowController>::it it;
};
class IfcFlowFitting : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowFitting (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowFitting* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowFitting> > list;
    typedef IfcTemplatedEntityList<IfcFlowFitting>::it it;
};
class IfcFlowInstrumentType : public IfcDistributionControlElementType {
public:
    IfcFlowInstrumentTypeEnum::IfcFlowInstrumentTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowInstrumentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowInstrumentType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowInstrumentType> > list;
    typedef IfcTemplatedEntityList<IfcFlowInstrumentType>::it it;
};
class IfcFlowMovingDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowMovingDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowMovingDevice* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowMovingDevice> > list;
    typedef IfcTemplatedEntityList<IfcFlowMovingDevice>::it it;
};
class IfcFlowSegment : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowSegment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowSegment* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowSegment> > list;
    typedef IfcTemplatedEntityList<IfcFlowSegment>::it it;
};
class IfcFlowStorageDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowStorageDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowStorageDevice* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowStorageDevice> > list;
    typedef IfcTemplatedEntityList<IfcFlowStorageDevice>::it it;
};
class IfcFlowTerminal : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowTerminal (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowTerminal* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTerminal> > list;
    typedef IfcTemplatedEntityList<IfcFlowTerminal>::it it;
};
class IfcFlowTreatmentDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFlowTreatmentDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFlowTreatmentDevice* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTreatmentDevice> > list;
    typedef IfcTemplatedEntityList<IfcFlowTreatmentDevice>::it it;
};
class IfcFooting : public IfcBuildingElement {
public:
    IfcFootingTypeEnum::IfcFootingTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcFooting (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcFooting* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFooting> > list;
    typedef IfcTemplatedEntityList<IfcFooting>::it it;
};
class IfcMember : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcMember* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMember> > list;
    typedef IfcTemplatedEntityList<IfcMember>::it it;
};
class IfcPile : public IfcBuildingElement {
public:
    IfcPileTypeEnum::IfcPileTypeEnum PredefinedType();
    bool hasConstructionType();
    IfcPileConstructionEnum::IfcPileConstructionEnum ConstructionType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPile (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPile* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPile> > list;
    typedef IfcTemplatedEntityList<IfcPile>::it it;
};
class IfcPlate : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcPlate (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcPlate* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlate> > list;
    typedef IfcTemplatedEntityList<IfcPlate>::it it;
};
class IfcRailing : public IfcBuildingElement {
public:
    bool hasPredefinedType();
    IfcRailingTypeEnum::IfcRailingTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRailing (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRailing* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRailing> > list;
    typedef IfcTemplatedEntityList<IfcRailing>::it it;
};
class IfcRamp : public IfcBuildingElement {
public:
    IfcRampTypeEnum::IfcRampTypeEnum ShapeType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRamp (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRamp* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRamp> > list;
    typedef IfcTemplatedEntityList<IfcRamp>::it it;
};
class IfcRampFlight : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRampFlight (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRampFlight* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRampFlight> > list;
    typedef IfcTemplatedEntityList<IfcRampFlight>::it it;
};
class IfcRationalBezierCurve : public IfcBezierCurve {
public:
    std::vector<double> /*[2:?]*/ WeightsData();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRationalBezierCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRationalBezierCurve* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRationalBezierCurve> > list;
    typedef IfcTemplatedEntityList<IfcRationalBezierCurve>::it it;
};
class IfcReinforcingElement : public IfcBuildingElementComponent {
public:
    bool hasSteelGrade();
    IfcLabel SteelGrade();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcReinforcingElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcReinforcingElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcingElement> > list;
    typedef IfcTemplatedEntityList<IfcReinforcingElement>::it it;
};
class IfcReinforcingMesh : public IfcReinforcingElement {
public:
    bool hasMeshLength();
    IfcPositiveLengthMeasure MeshLength();
    bool hasMeshWidth();
    IfcPositiveLengthMeasure MeshWidth();
    IfcPositiveLengthMeasure LongitudinalBarNominalDiameter();
    IfcPositiveLengthMeasure TransverseBarNominalDiameter();
    IfcAreaMeasure LongitudinalBarCrossSectionArea();
    IfcAreaMeasure TransverseBarCrossSectionArea();
    IfcPositiveLengthMeasure LongitudinalBarSpacing();
    IfcPositiveLengthMeasure TransverseBarSpacing();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcReinforcingMesh (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcReinforcingMesh* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcingMesh> > list;
    typedef IfcTemplatedEntityList<IfcReinforcingMesh>::it it;
};
class IfcRoof : public IfcBuildingElement {
public:
    IfcRoofTypeEnum::IfcRoofTypeEnum ShapeType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRoof (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRoof* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoof> > list;
    typedef IfcTemplatedEntityList<IfcRoof>::it it;
};
class IfcRoundedEdgeFeature : public IfcEdgeFeature {
public:
    bool hasRadius();
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcRoundedEdgeFeature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcRoundedEdgeFeature* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoundedEdgeFeature> > list;
    typedef IfcTemplatedEntityList<IfcRoundedEdgeFeature>::it it;
};
class IfcSensorType : public IfcDistributionControlElementType {
public:
    IfcSensorTypeEnum::IfcSensorTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSensorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSensorType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSensorType> > list;
    typedef IfcTemplatedEntityList<IfcSensorType>::it it;
};
class IfcSlab : public IfcBuildingElement {
public:
    bool hasPredefinedType();
    IfcSlabTypeEnum::IfcSlabTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcSlab (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcSlab* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSlab> > list;
    typedef IfcTemplatedEntityList<IfcSlab>::it it;
};
class IfcStair : public IfcBuildingElement {
public:
    IfcStairTypeEnum::IfcStairTypeEnum ShapeType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStair (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStair* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStair> > list;
    typedef IfcTemplatedEntityList<IfcStair>::it it;
};
class IfcStairFlight : public IfcBuildingElement {
public:
    bool hasNumberOfRiser();
    int NumberOfRiser();
    bool hasNumberOfTreads();
    int NumberOfTreads();
    bool hasRiserHeight();
    IfcPositiveLengthMeasure RiserHeight();
    bool hasTreadLength();
    IfcPositiveLengthMeasure TreadLength();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStairFlight (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStairFlight* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStairFlight> > list;
    typedef IfcTemplatedEntityList<IfcStairFlight>::it it;
};
class IfcStructuralAnalysisModel : public IfcSystem {
public:
    IfcAnalysisModelTypeEnum::IfcAnalysisModelTypeEnum PredefinedType();
    bool hasOrientationOf2DPlane();
    IfcAxis2Placement3D* OrientationOf2DPlane();
    bool hasLoadedBy();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadGroup> > LoadedBy();
    bool hasHasResults();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralResultGroup> > HasResults();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcStructuralAnalysisModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcStructuralAnalysisModel* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAnalysisModel> > list;
    typedef IfcTemplatedEntityList<IfcStructuralAnalysisModel>::it it;
};
class IfcTendon : public IfcReinforcingElement {
public:
    IfcTendonTypeEnum::IfcTendonTypeEnum PredefinedType();
    IfcPositiveLengthMeasure NominalDiameter();
    IfcAreaMeasure CrossSectionArea();
    bool hasTensionForce();
    IfcForceMeasure TensionForce();
    bool hasPreStress();
    IfcPressureMeasure PreStress();
    bool hasFrictionCoefficient();
    IfcNormalisedRatioMeasure FrictionCoefficient();
    bool hasAnchorageSlip();
    IfcPositiveLengthMeasure AnchorageSlip();
    bool hasMinCurvatureRadius();
    IfcPositiveLengthMeasure MinCurvatureRadius();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTendon (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTendon* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTendon> > list;
    typedef IfcTemplatedEntityList<IfcTendon>::it it;
};
class IfcTendonAnchor : public IfcReinforcingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcTendonAnchor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcTendonAnchor* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTendonAnchor> > list;
    typedef IfcTemplatedEntityList<IfcTendonAnchor>::it it;
};
class IfcVibrationIsolatorType : public IfcDiscreteAccessoryType {
public:
    IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcVibrationIsolatorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcVibrationIsolatorType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVibrationIsolatorType> > list;
    typedef IfcTemplatedEntityList<IfcVibrationIsolatorType>::it it;
};
class IfcWall : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWall (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWall* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWall> > list;
    typedef IfcTemplatedEntityList<IfcWall>::it it;
};
class IfcWallStandardCase : public IfcWall {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWallStandardCase (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWallStandardCase* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWallStandardCase> > list;
    typedef IfcTemplatedEntityList<IfcWallStandardCase>::it it;
};
class IfcWindow : public IfcBuildingElement {
public:
    bool hasOverallHeight();
    IfcPositiveLengthMeasure OverallHeight();
    bool hasOverallWidth();
    IfcPositiveLengthMeasure OverallWidth();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcWindow (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcWindow* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWindow> > list;
    typedef IfcTemplatedEntityList<IfcWindow>::it it;
};
class IfcActuatorType : public IfcDistributionControlElementType {
public:
    IfcActuatorTypeEnum::IfcActuatorTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcActuatorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcActuatorType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcActuatorType> > list;
    typedef IfcTemplatedEntityList<IfcActuatorType>::it it;
};
class IfcAlarmType : public IfcDistributionControlElementType {
public:
    IfcAlarmTypeEnum::IfcAlarmTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcAlarmType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcAlarmType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAlarmType> > list;
    typedef IfcTemplatedEntityList<IfcAlarmType>::it it;
};
class IfcBeam : public IfcBuildingElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcBeam (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcBeam* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBeam> > list;
    typedef IfcTemplatedEntityList<IfcBeam>::it it;
};
class IfcChamferEdgeFeature : public IfcEdgeFeature {
public:
    bool hasWidth();
    IfcPositiveLengthMeasure Width();
    bool hasHeight();
    IfcPositiveLengthMeasure Height();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcChamferEdgeFeature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcChamferEdgeFeature* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcChamferEdgeFeature> > list;
    typedef IfcTemplatedEntityList<IfcChamferEdgeFeature>::it it;
};
class IfcControllerType : public IfcDistributionControlElementType {
public:
    IfcControllerTypeEnum::IfcControllerTypeEnum PredefinedType();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcControllerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcControllerType* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcControllerType> > list;
    typedef IfcTemplatedEntityList<IfcControllerType>::it it;
};
class IfcDistributionChamberElement : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionChamberElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionChamberElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionChamberElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionChamberElement>::it it;
};
class IfcDistributionControlElement : public IfcDistributionElement {
public:
    bool hasControlElementId();
    IfcIdentifier ControlElementId();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelFlowControlElements> > AssignedToFlowElement(); // INVERSE IfcRelFlowControlElements::RelatedControlElements
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcDistributionControlElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcDistributionControlElement* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionControlElement>::it it;
};
class IfcElectricDistributionPoint : public IfcFlowController {
public:
    IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunctionEnum DistributionPointFunction();
    bool hasUserDefinedFunction();
    IfcLabel UserDefinedFunction();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcElectricDistributionPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcElectricDistributionPoint* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricDistributionPoint> > list;
    typedef IfcTemplatedEntityList<IfcElectricDistributionPoint>::it it;
};
class IfcReinforcingBar : public IfcReinforcingElement {
public:
    IfcPositiveLengthMeasure NominalDiameter();
    IfcAreaMeasure CrossSectionArea();
    bool hasBarLength();
    IfcPositiveLengthMeasure BarLength();
    IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum BarRole();
    bool hasBarSurface();
    IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum BarSurface();
    bool is(Type::Enum v) const;
    Type::Enum type() const;
    static Type::Enum Class();
    IfcReinforcingBar (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef IfcReinforcingBar* ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcingBar> > list;
    typedef IfcTemplatedEntityList<IfcReinforcingBar>::it it;
};
void InitStringMap();
IfcSchemaEntity SchemaEntity(IfcAbstractEntityPtr e = 0);
}

#endif
