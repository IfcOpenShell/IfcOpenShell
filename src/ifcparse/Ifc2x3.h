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

typedef float IfcAbsorbedDoseMeasure;
typedef float IfcAccelerationMeasure;
typedef float IfcAmountOfSubstanceMeasure;
typedef float IfcAngularVelocityMeasure;
typedef float IfcAreaMeasure;
typedef bool IfcBoolean;
typedef std::vector<float> /*[1:2]*/ IfcComplexNumber;
typedef std::vector<int> /*[3:4]*/ IfcCompoundPlaneAngleMeasure;
typedef float IfcContextDependentMeasure;
typedef float IfcCountMeasure;
typedef float IfcCurvatureMeasure;
typedef int IfcDayInMonthNumber;
typedef int IfcDaylightSavingHour;
typedef std::string IfcDescriptiveMeasure;
typedef int IfcDimensionCount;
typedef float IfcDoseEquivalentMeasure;
typedef float IfcDynamicViscosityMeasure;
typedef float IfcElectricCapacitanceMeasure;
typedef float IfcElectricChargeMeasure;
typedef float IfcElectricConductanceMeasure;
typedef float IfcElectricCurrentMeasure;
typedef float IfcElectricResistanceMeasure;
typedef float IfcElectricVoltageMeasure;
typedef float IfcEnergyMeasure;
typedef std::string IfcFontStyle;
typedef std::string IfcFontVariant;
typedef std::string IfcFontWeight;
typedef float IfcForceMeasure;
typedef float IfcFrequencyMeasure;
typedef std::string IfcGloballyUniqueId;
typedef float IfcHeatFluxDensityMeasure;
typedef float IfcHeatingValueMeasure;
typedef int IfcHourInDay;
typedef std::string IfcIdentifier;
typedef float IfcIlluminanceMeasure;
typedef float IfcInductanceMeasure;
typedef int IfcInteger;
typedef int IfcIntegerCountRateMeasure;
typedef float IfcIonConcentrationMeasure;
typedef float IfcIsothermalMoistureCapacityMeasure;
typedef float IfcKinematicViscosityMeasure;
typedef std::string IfcLabel;
typedef float IfcLengthMeasure;
typedef float IfcLinearForceMeasure;
typedef float IfcLinearMomentMeasure;
typedef float IfcLinearStiffnessMeasure;
typedef float IfcLinearVelocityMeasure;
typedef bool IfcLogical;
typedef float IfcLuminousFluxMeasure;
typedef float IfcLuminousIntensityDistributionMeasure;
typedef float IfcLuminousIntensityMeasure;
typedef float IfcMagneticFluxDensityMeasure;
typedef float IfcMagneticFluxMeasure;
typedef float IfcMassDensityMeasure;
typedef float IfcMassFlowRateMeasure;
typedef float IfcMassMeasure;
typedef float IfcMassPerLengthMeasure;
typedef int IfcMinuteInHour;
typedef float IfcModulusOfElasticityMeasure;
typedef float IfcModulusOfLinearSubgradeReactionMeasure;
typedef float IfcModulusOfRotationalSubgradeReactionMeasure;
typedef float IfcModulusOfSubgradeReactionMeasure;
typedef float IfcMoistureDiffusivityMeasure;
typedef float IfcMolecularWeightMeasure;
typedef float IfcMomentOfInertiaMeasure;
typedef float IfcMonetaryMeasure;
typedef int IfcMonthInYearNumber;
typedef float IfcNumericMeasure;
typedef float IfcPHMeasure;
typedef float IfcParameterValue;
typedef float IfcPlanarForceMeasure;
typedef float IfcPlaneAngleMeasure;
typedef float IfcPowerMeasure;
typedef std::string IfcPresentableText;
typedef float IfcPressureMeasure;
typedef float IfcRadioActivityMeasure;
typedef float IfcRatioMeasure;
typedef float IfcReal;
typedef float IfcRotationalFrequencyMeasure;
typedef float IfcRotationalMassMeasure;
typedef float IfcRotationalStiffnessMeasure;
typedef float IfcSecondInMinute;
typedef float IfcSectionModulusMeasure;
typedef float IfcSectionalAreaIntegralMeasure;
typedef float IfcShearModulusMeasure;
typedef float IfcSolidAngleMeasure;
typedef float IfcSoundPowerMeasure;
typedef float IfcSoundPressureMeasure;
typedef float IfcSpecificHeatCapacityMeasure;
typedef float IfcSpecularExponent;
typedef float IfcSpecularRoughness;
typedef float IfcTemperatureGradientMeasure;
typedef std::string IfcText;
typedef std::string IfcTextAlignment;
typedef std::string IfcTextDecoration;
typedef std::string IfcTextFontName;
typedef std::string IfcTextTransformation;
typedef float IfcThermalAdmittanceMeasure;
typedef float IfcThermalConductivityMeasure;
typedef float IfcThermalExpansionCoefficientMeasure;
typedef float IfcThermalResistanceMeasure;
typedef float IfcThermalTransmittanceMeasure;
typedef float IfcThermodynamicTemperatureMeasure;
typedef float IfcTimeMeasure;
typedef int IfcTimeStamp;
typedef float IfcTorqueMeasure;
typedef float IfcVaporPermeabilityMeasure;
typedef float IfcVolumeMeasure;
typedef float IfcVolumetricFlowRateMeasure;
typedef float IfcWarpingConstantMeasure;
typedef float IfcWarpingMomentMeasure;
typedef int IfcYearNumber;
typedef SHARED_PTR<IfcAbstractSelect> IfcActorSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcAppliedValueSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcAxis2Placement;
typedef SHARED_PTR<IfcAbstractSelect> IfcBooleanOperand;
typedef SHARED_PTR<IfcAbstractSelect> IfcCharacterStyleSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcClassificationNotationSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcColour;
typedef SHARED_PTR<IfcAbstractSelect> IfcColourOrFactor;
typedef SHARED_PTR<IfcAbstractSelect> IfcConditionCriterionSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcCsgSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcCurveFontOrScaledCurveFontSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcCurveOrEdgeCurve;
typedef SHARED_PTR<IfcAbstractSelect> IfcCurveStyleFontSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcDateTimeSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcDefinedSymbolSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcDerivedMeasureValue;
typedef SHARED_PTR<IfcAbstractSelect> IfcDocumentSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcDraughtingCalloutElement;
typedef SHARED_PTR<IfcAbstractSelect> IfcFillAreaStyleTileShapeSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcFillStyleSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcGeometricSetSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcHatchLineDistanceSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcLayeredItem;
typedef SHARED_PTR<IfcAbstractSelect> IfcLibrarySelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcLightDistributionDataSourceSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcMaterialSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcMeasureValue;
typedef SHARED_PTR<IfcAbstractSelect> IfcMetricValueSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcObjectReferenceSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcOrientationSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcPointOrVertexPoint;
typedef SHARED_PTR<IfcAbstractSelect> IfcPresentationStyleSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcShell;
typedef SHARED_PTR<IfcAbstractSelect> IfcSimpleValue;
typedef SHARED_PTR<IfcAbstractSelect> IfcSizeSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcSpecularHighlightSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcStructuralActivityAssignmentSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcSurfaceOrFaceSurface;
typedef SHARED_PTR<IfcAbstractSelect> IfcSurfaceStyleElementSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcSymbolStyleSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcTextFontSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcTextStyleSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcTrimmingSelect;
typedef SHARED_PTR<IfcAbstractSelect> IfcUnit;
typedef SHARED_PTR<IfcAbstractSelect> IfcValue;
typedef SHARED_PTR<IfcAbstractSelect> IfcVectorOrDirection;
typedef IfcLabel IfcBoxAlignment;
typedef IfcRatioMeasure IfcNormalisedRatioMeasure;
typedef IfcLengthMeasure IfcPositiveLengthMeasure;
typedef IfcPlaneAngleMeasure IfcPositivePlaneAngleMeasure;
typedef IfcRatioMeasure IfcPositiveRatioMeasure;
namespace IfcActionSourceTypeEnum {typedef enum {DEAD_LOAD_G, COMPLETION_G1, LIVE_LOAD_Q, SNOW_S, WIND_W, PRESTRESSING_P, SETTLEMENT_U, TEMPERATURE_T, EARTHQUAKE_E, FIRE, IMPULSE, IMPACT, TRANSPORT, ERECTION, PROPPING, SYSTEM_IMPERFECTION, SHRINKAGE, CREEP, LACK_OF_FIT, BUOYANCY, ICE, CURRENT, WAVE, RAIN, BRAKES, USERDEFINED, NOTDEFINED} IfcActionSourceTypeEnum;
std::string ToString(IfcActionSourceTypeEnum v);
IfcActionSourceTypeEnum FromString(const std::string& s);}
namespace IfcActionTypeEnum {typedef enum {PERMANENT_G, VARIABLE_Q, EXTRAORDINARY_A, USERDEFINED, NOTDEFINED} IfcActionTypeEnum;
std::string ToString(IfcActionTypeEnum v);
IfcActionTypeEnum FromString(const std::string& s);}
namespace IfcActuatorTypeEnum {typedef enum {ELECTRICACTUATOR, HANDOPERATEDACTUATOR, HYDRAULICACTUATOR, PNEUMATICACTUATOR, THERMOSTATICACTUATOR, USERDEFINED, NOTDEFINED} IfcActuatorTypeEnum;
std::string ToString(IfcActuatorTypeEnum v);
IfcActuatorTypeEnum FromString(const std::string& s);}
namespace IfcAddressTypeEnum {typedef enum {OFFICE, SITE, HOME, DISTRIBUTIONPOINT, USERDEFINED} IfcAddressTypeEnum;
std::string ToString(IfcAddressTypeEnum v);
IfcAddressTypeEnum FromString(const std::string& s);}
namespace IfcAheadOrBehind {typedef enum {AHEAD, BEHIND} IfcAheadOrBehind;
std::string ToString(IfcAheadOrBehind v);
IfcAheadOrBehind FromString(const std::string& s);}
namespace IfcAirTerminalBoxTypeEnum {typedef enum {CONSTANTFLOW, VARIABLEFLOWPRESSUREDEPENDANT, VARIABLEFLOWPRESSUREINDEPENDANT, USERDEFINED, NOTDEFINED} IfcAirTerminalBoxTypeEnum;
std::string ToString(IfcAirTerminalBoxTypeEnum v);
IfcAirTerminalBoxTypeEnum FromString(const std::string& s);}
namespace IfcAirTerminalTypeEnum {typedef enum {GRILLE, REGISTER, DIFFUSER, EYEBALL, IRIS, LINEARGRILLE, LINEARDIFFUSER, USERDEFINED, NOTDEFINED} IfcAirTerminalTypeEnum;
std::string ToString(IfcAirTerminalTypeEnum v);
IfcAirTerminalTypeEnum FromString(const std::string& s);}
namespace IfcAirToAirHeatRecoveryTypeEnum {typedef enum {FIXEDPLATECOUNTERFLOWEXCHANGER, FIXEDPLATECROSSFLOWEXCHANGER, FIXEDPLATEPARALLELFLOWEXCHANGER, ROTARYWHEEL, RUNAROUNDCOILLOOP, HEATPIPE, TWINTOWERENTHALPYRECOVERYLOOPS, THERMOSIPHONSEALEDTUBEHEATEXCHANGERS, THERMOSIPHONCOILTYPEHEATEXCHANGERS, USERDEFINED, NOTDEFINED} IfcAirToAirHeatRecoveryTypeEnum;
std::string ToString(IfcAirToAirHeatRecoveryTypeEnum v);
IfcAirToAirHeatRecoveryTypeEnum FromString(const std::string& s);}
namespace IfcAlarmTypeEnum {typedef enum {BELL, BREAKGLASSBUTTON, LIGHT, MANUALPULLBOX, SIREN, WHISTLE, USERDEFINED, NOTDEFINED} IfcAlarmTypeEnum;
std::string ToString(IfcAlarmTypeEnum v);
IfcAlarmTypeEnum FromString(const std::string& s);}
namespace IfcAnalysisModelTypeEnum {typedef enum {IN_PLANE_LOADING_2D, OUT_PLANE_LOADING_2D, LOADING_3D, USERDEFINED, NOTDEFINED} IfcAnalysisModelTypeEnum;
std::string ToString(IfcAnalysisModelTypeEnum v);
IfcAnalysisModelTypeEnum FromString(const std::string& s);}
namespace IfcAnalysisTheoryTypeEnum {typedef enum {FIRST_ORDER_THEORY, SECOND_ORDER_THEORY, THIRD_ORDER_THEORY, FULL_NONLINEAR_THEORY, USERDEFINED, NOTDEFINED} IfcAnalysisTheoryTypeEnum;
std::string ToString(IfcAnalysisTheoryTypeEnum v);
IfcAnalysisTheoryTypeEnum FromString(const std::string& s);}
namespace IfcArithmeticOperatorEnum {typedef enum {ADD, DIVIDE, MULTIPLY, SUBTRACT} IfcArithmeticOperatorEnum;
std::string ToString(IfcArithmeticOperatorEnum v);
IfcArithmeticOperatorEnum FromString(const std::string& s);}
namespace IfcAssemblyPlaceEnum {typedef enum {SITE, FACTORY, NOTDEFINED} IfcAssemblyPlaceEnum;
std::string ToString(IfcAssemblyPlaceEnum v);
IfcAssemblyPlaceEnum FromString(const std::string& s);}
namespace IfcBSplineCurveForm {typedef enum {POLYLINE_FORM, CIRCULAR_ARC, ELLIPTIC_ARC, PARABOLIC_ARC, HYPERBOLIC_ARC, UNSPECIFIED} IfcBSplineCurveForm;
std::string ToString(IfcBSplineCurveForm v);
IfcBSplineCurveForm FromString(const std::string& s);}
namespace IfcBeamTypeEnum {typedef enum {BEAM, JOIST, LINTEL, T_BEAM, USERDEFINED, NOTDEFINED} IfcBeamTypeEnum;
std::string ToString(IfcBeamTypeEnum v);
IfcBeamTypeEnum FromString(const std::string& s);}
namespace IfcBenchmarkEnum {typedef enum {GREATERTHAN, GREATERTHANOREQUALTO, LESSTHAN, LESSTHANOREQUALTO, EQUALTO, NOTEQUALTO} IfcBenchmarkEnum;
std::string ToString(IfcBenchmarkEnum v);
IfcBenchmarkEnum FromString(const std::string& s);}
namespace IfcBoilerTypeEnum {typedef enum {WATER, STEAM, USERDEFINED, NOTDEFINED} IfcBoilerTypeEnum;
std::string ToString(IfcBoilerTypeEnum v);
IfcBoilerTypeEnum FromString(const std::string& s);}
namespace IfcBooleanOperator {typedef enum {UNION, INTERSECTION, DIFFERENCE} IfcBooleanOperator;
std::string ToString(IfcBooleanOperator v);
IfcBooleanOperator FromString(const std::string& s);}
namespace IfcBuildingElementProxyTypeEnum {typedef enum {USERDEFINED, NOTDEFINED} IfcBuildingElementProxyTypeEnum;
std::string ToString(IfcBuildingElementProxyTypeEnum v);
IfcBuildingElementProxyTypeEnum FromString(const std::string& s);}
namespace IfcCableCarrierFittingTypeEnum {typedef enum {BEND, CROSS, REDUCER, TEE, USERDEFINED, NOTDEFINED} IfcCableCarrierFittingTypeEnum;
std::string ToString(IfcCableCarrierFittingTypeEnum v);
IfcCableCarrierFittingTypeEnum FromString(const std::string& s);}
namespace IfcCableCarrierSegmentTypeEnum {typedef enum {CABLELADDERSEGMENT, CABLETRAYSEGMENT, CABLETRUNKINGSEGMENT, CONDUITSEGMENT, USERDEFINED, NOTDEFINED} IfcCableCarrierSegmentTypeEnum;
std::string ToString(IfcCableCarrierSegmentTypeEnum v);
IfcCableCarrierSegmentTypeEnum FromString(const std::string& s);}
namespace IfcCableSegmentTypeEnum {typedef enum {CABLESEGMENT, CONDUCTORSEGMENT, USERDEFINED, NOTDEFINED} IfcCableSegmentTypeEnum;
std::string ToString(IfcCableSegmentTypeEnum v);
IfcCableSegmentTypeEnum FromString(const std::string& s);}
namespace IfcChangeActionEnum {typedef enum {NOCHANGE, MODIFIED, ADDED, DELETED, MODIFIEDADDED, MODIFIEDDELETED} IfcChangeActionEnum;
std::string ToString(IfcChangeActionEnum v);
IfcChangeActionEnum FromString(const std::string& s);}
namespace IfcChillerTypeEnum {typedef enum {AIRCOOLED, WATERCOOLED, HEATRECOVERY, USERDEFINED, NOTDEFINED} IfcChillerTypeEnum;
std::string ToString(IfcChillerTypeEnum v);
IfcChillerTypeEnum FromString(const std::string& s);}
namespace IfcCoilTypeEnum {typedef enum {DXCOOLINGCOIL, WATERCOOLINGCOIL, STEAMHEATINGCOIL, WATERHEATINGCOIL, ELECTRICHEATINGCOIL, GASHEATINGCOIL, USERDEFINED, NOTDEFINED} IfcCoilTypeEnum;
std::string ToString(IfcCoilTypeEnum v);
IfcCoilTypeEnum FromString(const std::string& s);}
namespace IfcColumnTypeEnum {typedef enum {COLUMN, USERDEFINED, NOTDEFINED} IfcColumnTypeEnum;
std::string ToString(IfcColumnTypeEnum v);
IfcColumnTypeEnum FromString(const std::string& s);}
namespace IfcCompressorTypeEnum {typedef enum {DYNAMIC, RECIPROCATING, ROTARY, SCROLL, TROCHOIDAL, SINGLESTAGE, BOOSTER, OPENTYPE, HERMETIC, SEMIHERMETIC, WELDEDSHELLHERMETIC, ROLLINGPISTON, ROTARYVANE, SINGLESCREW, TWINSCREW, USERDEFINED, NOTDEFINED} IfcCompressorTypeEnum;
std::string ToString(IfcCompressorTypeEnum v);
IfcCompressorTypeEnum FromString(const std::string& s);}
namespace IfcCondenserTypeEnum {typedef enum {WATERCOOLEDSHELLTUBE, WATERCOOLEDSHELLCOIL, WATERCOOLEDTUBEINTUBE, WATERCOOLEDBRAZEDPLATE, AIRCOOLED, EVAPORATIVECOOLED, USERDEFINED, NOTDEFINED} IfcCondenserTypeEnum;
std::string ToString(IfcCondenserTypeEnum v);
IfcCondenserTypeEnum FromString(const std::string& s);}
namespace IfcConnectionTypeEnum {typedef enum {ATPATH, ATSTART, ATEND, NOTDEFINED} IfcConnectionTypeEnum;
std::string ToString(IfcConnectionTypeEnum v);
IfcConnectionTypeEnum FromString(const std::string& s);}
namespace IfcConstraintEnum {typedef enum {HARD, SOFT, ADVISORY, USERDEFINED, NOTDEFINED} IfcConstraintEnum;
std::string ToString(IfcConstraintEnum v);
IfcConstraintEnum FromString(const std::string& s);}
namespace IfcControllerTypeEnum {typedef enum {FLOATING, PROPORTIONAL, PROPORTIONALINTEGRAL, PROPORTIONALINTEGRALDERIVATIVE, TIMEDTWOPOSITION, TWOPOSITION, USERDEFINED, NOTDEFINED} IfcControllerTypeEnum;
std::string ToString(IfcControllerTypeEnum v);
IfcControllerTypeEnum FromString(const std::string& s);}
namespace IfcCooledBeamTypeEnum {typedef enum {ACTIVE, PASSIVE, USERDEFINED, NOTDEFINED} IfcCooledBeamTypeEnum;
std::string ToString(IfcCooledBeamTypeEnum v);
IfcCooledBeamTypeEnum FromString(const std::string& s);}
namespace IfcCoolingTowerTypeEnum {typedef enum {NATURALDRAFT, MECHANICALINDUCEDDRAFT, MECHANICALFORCEDDRAFT, USERDEFINED, NOTDEFINED} IfcCoolingTowerTypeEnum;
std::string ToString(IfcCoolingTowerTypeEnum v);
IfcCoolingTowerTypeEnum FromString(const std::string& s);}
namespace IfcCostScheduleTypeEnum {typedef enum {BUDGET, COSTPLAN, ESTIMATE, TENDER, PRICEDBILLOFQUANTITIES, UNPRICEDBILLOFQUANTITIES, SCHEDULEOFRATES, USERDEFINED, NOTDEFINED} IfcCostScheduleTypeEnum;
std::string ToString(IfcCostScheduleTypeEnum v);
IfcCostScheduleTypeEnum FromString(const std::string& s);}
namespace IfcCoveringTypeEnum {typedef enum {CEILING, FLOORING, CLADDING, ROOFING, INSULATION, MEMBRANE, SLEEVING, WRAPPING, USERDEFINED, NOTDEFINED} IfcCoveringTypeEnum;
std::string ToString(IfcCoveringTypeEnum v);
IfcCoveringTypeEnum FromString(const std::string& s);}
namespace IfcCurrencyEnum {typedef enum {AED, AES, ATS, AUD, BBD, BEG, BGL, BHD, BMD, BND, BRL, BSD, BWP, BZD, CAD, CBD, CHF, CLP, CNY, CYS, CZK, DDP, DEM, DKK, EGL, EST, EUR, FAK, FIM, FJD, FKP, FRF, GBP, GIP, GMD, GRX, HKD, HUF, ICK, IDR, ILS, INR, IRP, ITL, JMD, JOD, JPY, KES, KRW, KWD, KYD, LKR, LUF, MTL, MUR, MXN, MYR, NLG, NZD, OMR, PGK, PHP, PKR, PLN, PTN, QAR, RUR, SAR, SCR, SEK, SGD, SKP, THB, TRL, TTD, TWD, USD, VEB, VND, XEU, ZAR, ZWD, NOK} IfcCurrencyEnum;
std::string ToString(IfcCurrencyEnum v);
IfcCurrencyEnum FromString(const std::string& s);}
namespace IfcCurtainWallTypeEnum {typedef enum {USERDEFINED, NOTDEFINED} IfcCurtainWallTypeEnum;
std::string ToString(IfcCurtainWallTypeEnum v);
IfcCurtainWallTypeEnum FromString(const std::string& s);}
namespace IfcDamperTypeEnum {typedef enum {CONTROLDAMPER, FIREDAMPER, SMOKEDAMPER, FIRESMOKEDAMPER, BACKDRAFTDAMPER, RELIEFDAMPER, BLASTDAMPER, GRAVITYDAMPER, GRAVITYRELIEFDAMPER, BALANCINGDAMPER, FUMEHOODEXHAUST, USERDEFINED, NOTDEFINED} IfcDamperTypeEnum;
std::string ToString(IfcDamperTypeEnum v);
IfcDamperTypeEnum FromString(const std::string& s);}
namespace IfcDataOriginEnum {typedef enum {MEASURED, PREDICTED, SIMULATED, USERDEFINED, NOTDEFINED} IfcDataOriginEnum;
std::string ToString(IfcDataOriginEnum v);
IfcDataOriginEnum FromString(const std::string& s);}
namespace IfcDerivedUnitEnum {typedef enum {ANGULARVELOCITYUNIT, COMPOUNDPLANEANGLEUNIT, DYNAMICVISCOSITYUNIT, HEATFLUXDENSITYUNIT, INTEGERCOUNTRATEUNIT, ISOTHERMALMOISTURECAPACITYUNIT, KINEMATICVISCOSITYUNIT, LINEARVELOCITYUNIT, MASSDENSITYUNIT, MASSFLOWRATEUNIT, MOISTUREDIFFUSIVITYUNIT, MOLECULARWEIGHTUNIT, SPECIFICHEATCAPACITYUNIT, THERMALADMITTANCEUNIT, THERMALCONDUCTANCEUNIT, THERMALRESISTANCEUNIT, THERMALTRANSMITTANCEUNIT, VAPORPERMEABILITYUNIT, VOLUMETRICFLOWRATEUNIT, ROTATIONALFREQUENCYUNIT, TORQUEUNIT, MOMENTOFINERTIAUNIT, LINEARMOMENTUNIT, LINEARFORCEUNIT, PLANARFORCEUNIT, MODULUSOFELASTICITYUNIT, SHEARMODULUSUNIT, LINEARSTIFFNESSUNIT, ROTATIONALSTIFFNESSUNIT, MODULUSOFSUBGRADEREACTIONUNIT, ACCELERATIONUNIT, CURVATUREUNIT, HEATINGVALUEUNIT, IONCONCENTRATIONUNIT, LUMINOUSINTENSITYDISTRIBUTIONUNIT, MASSPERLENGTHUNIT, MODULUSOFLINEARSUBGRADEREACTIONUNIT, MODULUSOFROTATIONALSUBGRADEREACTIONUNIT, PHUNIT, ROTATIONALMASSUNIT, SECTIONAREAINTEGRALUNIT, SECTIONMODULUSUNIT, SOUNDPOWERUNIT, SOUNDPRESSUREUNIT, TEMPERATUREGRADIENTUNIT, THERMALEXPANSIONCOEFFICIENTUNIT, WARPINGCONSTANTUNIT, WARPINGMOMENTUNIT, USERDEFINED} IfcDerivedUnitEnum;
std::string ToString(IfcDerivedUnitEnum v);
IfcDerivedUnitEnum FromString(const std::string& s);}
namespace IfcDimensionExtentUsage {typedef enum {ORIGIN, TARGET} IfcDimensionExtentUsage;
std::string ToString(IfcDimensionExtentUsage v);
IfcDimensionExtentUsage FromString(const std::string& s);}
namespace IfcDirectionSenseEnum {typedef enum {POSITIVE, NEGATIVE} IfcDirectionSenseEnum;
std::string ToString(IfcDirectionSenseEnum v);
IfcDirectionSenseEnum FromString(const std::string& s);}
namespace IfcDistributionChamberElementTypeEnum {typedef enum {FORMEDDUCT, INSPECTIONCHAMBER, INSPECTIONPIT, MANHOLE, METERCHAMBER, SUMP, TRENCH, VALVECHAMBER, USERDEFINED, NOTDEFINED} IfcDistributionChamberElementTypeEnum;
std::string ToString(IfcDistributionChamberElementTypeEnum v);
IfcDistributionChamberElementTypeEnum FromString(const std::string& s);}
namespace IfcDocumentConfidentialityEnum {typedef enum {PUBLIC, RESTRICTED, CONFIDENTIAL, PERSONAL, USERDEFINED, NOTDEFINED} IfcDocumentConfidentialityEnum;
std::string ToString(IfcDocumentConfidentialityEnum v);
IfcDocumentConfidentialityEnum FromString(const std::string& s);}
namespace IfcDocumentStatusEnum {typedef enum {DRAFT, FINALDRAFT, FINAL, REVISION, NOTDEFINED} IfcDocumentStatusEnum;
std::string ToString(IfcDocumentStatusEnum v);
IfcDocumentStatusEnum FromString(const std::string& s);}
namespace IfcDoorPanelOperationEnum {typedef enum {SWINGING, DOUBLE_ACTING, SLIDING, FOLDING, REVOLVING, ROLLINGUP, USERDEFINED, NOTDEFINED} IfcDoorPanelOperationEnum;
std::string ToString(IfcDoorPanelOperationEnum v);
IfcDoorPanelOperationEnum FromString(const std::string& s);}
namespace IfcDoorPanelPositionEnum {typedef enum {LEFT, MIDDLE, RIGHT, NOTDEFINED} IfcDoorPanelPositionEnum;
std::string ToString(IfcDoorPanelPositionEnum v);
IfcDoorPanelPositionEnum FromString(const std::string& s);}
namespace IfcDoorStyleConstructionEnum {typedef enum {ALUMINIUM, HIGH_GRADE_STEEL, STEEL, WOOD, ALUMINIUM_WOOD, ALUMINIUM_PLASTIC, PLASTIC, USERDEFINED, NOTDEFINED} IfcDoorStyleConstructionEnum;
std::string ToString(IfcDoorStyleConstructionEnum v);
IfcDoorStyleConstructionEnum FromString(const std::string& s);}
namespace IfcDoorStyleOperationEnum {typedef enum {SINGLE_SWING_LEFT, SINGLE_SWING_RIGHT, DOUBLE_DOOR_SINGLE_SWING, DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT, DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT, DOUBLE_SWING_LEFT, DOUBLE_SWING_RIGHT, DOUBLE_DOOR_DOUBLE_SWING, SLIDING_TO_LEFT, SLIDING_TO_RIGHT, DOUBLE_DOOR_SLIDING, FOLDING_TO_LEFT, FOLDING_TO_RIGHT, DOUBLE_DOOR_FOLDING, REVOLVING, ROLLINGUP, USERDEFINED, NOTDEFINED} IfcDoorStyleOperationEnum;
std::string ToString(IfcDoorStyleOperationEnum v);
IfcDoorStyleOperationEnum FromString(const std::string& s);}
namespace IfcDuctFittingTypeEnum {typedef enum {BEND, CONNECTOR, ENTRY, EXIT, JUNCTION, OBSTRUCTION, TRANSITION, USERDEFINED, NOTDEFINED} IfcDuctFittingTypeEnum;
std::string ToString(IfcDuctFittingTypeEnum v);
IfcDuctFittingTypeEnum FromString(const std::string& s);}
namespace IfcDuctSegmentTypeEnum {typedef enum {RIGIDSEGMENT, FLEXIBLESEGMENT, USERDEFINED, NOTDEFINED} IfcDuctSegmentTypeEnum;
std::string ToString(IfcDuctSegmentTypeEnum v);
IfcDuctSegmentTypeEnum FromString(const std::string& s);}
namespace IfcDuctSilencerTypeEnum {typedef enum {FLATOVAL, RECTANGULAR, ROUND, USERDEFINED, NOTDEFINED} IfcDuctSilencerTypeEnum;
std::string ToString(IfcDuctSilencerTypeEnum v);
IfcDuctSilencerTypeEnum FromString(const std::string& s);}
namespace IfcElectricApplianceTypeEnum {typedef enum {COMPUTER, DIRECTWATERHEATER, DISHWASHER, ELECTRICCOOKER, ELECTRICHEATER, FACSIMILE, FREESTANDINGFAN, FREEZER, FRIDGE_FREEZER, HANDDRYER, INDIRECTWATERHEATER, MICROWAVE, PHOTOCOPIER, PRINTER, REFRIGERATOR, RADIANTHEATER, SCANNER, TELEPHONE, TUMBLEDRYER, TV, VENDINGMACHINE, WASHINGMACHINE, WATERHEATER, WATERCOOLER, USERDEFINED, NOTDEFINED} IfcElectricApplianceTypeEnum;
std::string ToString(IfcElectricApplianceTypeEnum v);
IfcElectricApplianceTypeEnum FromString(const std::string& s);}
namespace IfcElectricCurrentEnum {typedef enum {ALTERNATING, DIRECT, NOTDEFINED} IfcElectricCurrentEnum;
std::string ToString(IfcElectricCurrentEnum v);
IfcElectricCurrentEnum FromString(const std::string& s);}
namespace IfcElectricDistributionPointFunctionEnum {typedef enum {ALARMPANEL, CONSUMERUNIT, CONTROLPANEL, DISTRIBUTIONBOARD, GASDETECTORPANEL, INDICATORPANEL, MIMICPANEL, MOTORCONTROLCENTRE, SWITCHBOARD, USERDEFINED, NOTDEFINED} IfcElectricDistributionPointFunctionEnum;
std::string ToString(IfcElectricDistributionPointFunctionEnum v);
IfcElectricDistributionPointFunctionEnum FromString(const std::string& s);}
namespace IfcElectricFlowStorageDeviceTypeEnum {typedef enum {BATTERY, CAPACITORBANK, HARMONICFILTER, INDUCTORBANK, UPS, USERDEFINED, NOTDEFINED} IfcElectricFlowStorageDeviceTypeEnum;
std::string ToString(IfcElectricFlowStorageDeviceTypeEnum v);
IfcElectricFlowStorageDeviceTypeEnum FromString(const std::string& s);}
namespace IfcElectricGeneratorTypeEnum {typedef enum {USERDEFINED, NOTDEFINED} IfcElectricGeneratorTypeEnum;
std::string ToString(IfcElectricGeneratorTypeEnum v);
IfcElectricGeneratorTypeEnum FromString(const std::string& s);}
namespace IfcElectricHeaterTypeEnum {typedef enum {ELECTRICPOINTHEATER, ELECTRICCABLEHEATER, ELECTRICMATHEATER, USERDEFINED, NOTDEFINED} IfcElectricHeaterTypeEnum;
std::string ToString(IfcElectricHeaterTypeEnum v);
IfcElectricHeaterTypeEnum FromString(const std::string& s);}
namespace IfcElectricMotorTypeEnum {typedef enum {DC, INDUCTION, POLYPHASE, RELUCTANCESYNCHRONOUS, SYNCHRONOUS, USERDEFINED, NOTDEFINED} IfcElectricMotorTypeEnum;
std::string ToString(IfcElectricMotorTypeEnum v);
IfcElectricMotorTypeEnum FromString(const std::string& s);}
namespace IfcElectricTimeControlTypeEnum {typedef enum {TIMECLOCK, TIMEDELAY, RELAY, USERDEFINED, NOTDEFINED} IfcElectricTimeControlTypeEnum;
std::string ToString(IfcElectricTimeControlTypeEnum v);
IfcElectricTimeControlTypeEnum FromString(const std::string& s);}
namespace IfcElementAssemblyTypeEnum {typedef enum {ACCESSORY_ASSEMBLY, ARCH, BEAM_GRID, BRACED_FRAME, GIRDER, REINFORCEMENT_UNIT, RIGID_FRAME, SLAB_FIELD, TRUSS, USERDEFINED, NOTDEFINED} IfcElementAssemblyTypeEnum;
std::string ToString(IfcElementAssemblyTypeEnum v);
IfcElementAssemblyTypeEnum FromString(const std::string& s);}
namespace IfcElementCompositionEnum {typedef enum {COMPLEX, ELEMENT, PARTIAL} IfcElementCompositionEnum;
std::string ToString(IfcElementCompositionEnum v);
IfcElementCompositionEnum FromString(const std::string& s);}
namespace IfcEnergySequenceEnum {typedef enum {PRIMARY, SECONDARY, TERTIARY, AUXILIARY, USERDEFINED, NOTDEFINED} IfcEnergySequenceEnum;
std::string ToString(IfcEnergySequenceEnum v);
IfcEnergySequenceEnum FromString(const std::string& s);}
namespace IfcEnvironmentalImpactCategoryEnum {typedef enum {COMBINEDVALUE, DISPOSAL, EXTRACTION, INSTALLATION, MANUFACTURE, TRANSPORTATION, USERDEFINED, NOTDEFINED} IfcEnvironmentalImpactCategoryEnum;
std::string ToString(IfcEnvironmentalImpactCategoryEnum v);
IfcEnvironmentalImpactCategoryEnum FromString(const std::string& s);}
namespace IfcEvaporativeCoolerTypeEnum {typedef enum {DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER, DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER, DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER, DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER, DIRECTEVAPORATIVEAIRWASHER, INDIRECTEVAPORATIVEPACKAGEAIRCOOLER, INDIRECTEVAPORATIVEWETCOIL, INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER, INDIRECTDIRECTCOMBINATION, USERDEFINED, NOTDEFINED} IfcEvaporativeCoolerTypeEnum;
std::string ToString(IfcEvaporativeCoolerTypeEnum v);
IfcEvaporativeCoolerTypeEnum FromString(const std::string& s);}
namespace IfcEvaporatorTypeEnum {typedef enum {DIRECTEXPANSIONSHELLANDTUBE, DIRECTEXPANSIONTUBEINTUBE, DIRECTEXPANSIONBRAZEDPLATE, FLOODEDSHELLANDTUBE, SHELLANDCOIL, USERDEFINED, NOTDEFINED} IfcEvaporatorTypeEnum;
std::string ToString(IfcEvaporatorTypeEnum v);
IfcEvaporatorTypeEnum FromString(const std::string& s);}
namespace IfcFanTypeEnum {typedef enum {CENTRIFUGALFORWARDCURVED, CENTRIFUGALRADIAL, CENTRIFUGALBACKWARDINCLINEDCURVED, CENTRIFUGALAIRFOIL, TUBEAXIAL, VANEAXIAL, PROPELLORAXIAL, USERDEFINED, NOTDEFINED} IfcFanTypeEnum;
std::string ToString(IfcFanTypeEnum v);
IfcFanTypeEnum FromString(const std::string& s);}
namespace IfcFilterTypeEnum {typedef enum {AIRPARTICLEFILTER, ODORFILTER, OILFILTER, STRAINER, WATERFILTER, USERDEFINED, NOTDEFINED} IfcFilterTypeEnum;
std::string ToString(IfcFilterTypeEnum v);
IfcFilterTypeEnum FromString(const std::string& s);}
namespace IfcFireSuppressionTerminalTypeEnum {typedef enum {BREECHINGINLET, FIREHYDRANT, HOSEREEL, SPRINKLER, SPRINKLERDEFLECTOR, USERDEFINED, NOTDEFINED} IfcFireSuppressionTerminalTypeEnum;
std::string ToString(IfcFireSuppressionTerminalTypeEnum v);
IfcFireSuppressionTerminalTypeEnum FromString(const std::string& s);}
namespace IfcFlowDirectionEnum {typedef enum {SOURCE, SINK, SOURCEANDSINK, NOTDEFINED} IfcFlowDirectionEnum;
std::string ToString(IfcFlowDirectionEnum v);
IfcFlowDirectionEnum FromString(const std::string& s);}
namespace IfcFlowInstrumentTypeEnum {typedef enum {PRESSUREGAUGE, THERMOMETER, AMMETER, FREQUENCYMETER, POWERFACTORMETER, PHASEANGLEMETER, VOLTMETER_PEAK, VOLTMETER_RMS, USERDEFINED, NOTDEFINED} IfcFlowInstrumentTypeEnum;
std::string ToString(IfcFlowInstrumentTypeEnum v);
IfcFlowInstrumentTypeEnum FromString(const std::string& s);}
namespace IfcFlowMeterTypeEnum {typedef enum {ELECTRICMETER, ENERGYMETER, FLOWMETER, GASMETER, OILMETER, WATERMETER, USERDEFINED, NOTDEFINED} IfcFlowMeterTypeEnum;
std::string ToString(IfcFlowMeterTypeEnum v);
IfcFlowMeterTypeEnum FromString(const std::string& s);}
namespace IfcFootingTypeEnum {typedef enum {FOOTING_BEAM, PAD_FOOTING, PILE_CAP, STRIP_FOOTING, USERDEFINED, NOTDEFINED} IfcFootingTypeEnum;
std::string ToString(IfcFootingTypeEnum v);
IfcFootingTypeEnum FromString(const std::string& s);}
namespace IfcGasTerminalTypeEnum {typedef enum {GASAPPLIANCE, GASBOOSTER, GASBURNER, USERDEFINED, NOTDEFINED} IfcGasTerminalTypeEnum;
std::string ToString(IfcGasTerminalTypeEnum v);
IfcGasTerminalTypeEnum FromString(const std::string& s);}
namespace IfcGeometricProjectionEnum {typedef enum {GRAPH_VIEW, SKETCH_VIEW, MODEL_VIEW, PLAN_VIEW, REFLECTED_PLAN_VIEW, SECTION_VIEW, ELEVATION_VIEW, USERDEFINED, NOTDEFINED} IfcGeometricProjectionEnum;
std::string ToString(IfcGeometricProjectionEnum v);
IfcGeometricProjectionEnum FromString(const std::string& s);}
namespace IfcGlobalOrLocalEnum {typedef enum {GLOBAL_COORDS, LOCAL_COORDS} IfcGlobalOrLocalEnum;
std::string ToString(IfcGlobalOrLocalEnum v);
IfcGlobalOrLocalEnum FromString(const std::string& s);}
namespace IfcHeatExchangerTypeEnum {typedef enum {PLATE, SHELLANDTUBE, USERDEFINED, NOTDEFINED} IfcHeatExchangerTypeEnum;
std::string ToString(IfcHeatExchangerTypeEnum v);
IfcHeatExchangerTypeEnum FromString(const std::string& s);}
namespace IfcHumidifierTypeEnum {typedef enum {STEAMINJECTION, ADIABATICAIRWASHER, ADIABATICPAN, ADIABATICWETTEDELEMENT, ADIABATICATOMIZING, ADIABATICULTRASONIC, ADIABATICRIGIDMEDIA, ADIABATICCOMPRESSEDAIRNOZZLE, ASSISTEDELECTRIC, ASSISTEDNATURALGAS, ASSISTEDPROPANE, ASSISTEDBUTANE, ASSISTEDSTEAM, USERDEFINED, NOTDEFINED} IfcHumidifierTypeEnum;
std::string ToString(IfcHumidifierTypeEnum v);
IfcHumidifierTypeEnum FromString(const std::string& s);}
namespace IfcInternalOrExternalEnum {typedef enum {INTERNAL, EXTERNAL, NOTDEFINED} IfcInternalOrExternalEnum;
std::string ToString(IfcInternalOrExternalEnum v);
IfcInternalOrExternalEnum FromString(const std::string& s);}
namespace IfcInventoryTypeEnum {typedef enum {ASSETINVENTORY, SPACEINVENTORY, FURNITUREINVENTORY, USERDEFINED, NOTDEFINED} IfcInventoryTypeEnum;
std::string ToString(IfcInventoryTypeEnum v);
IfcInventoryTypeEnum FromString(const std::string& s);}
namespace IfcJunctionBoxTypeEnum {typedef enum {USERDEFINED, NOTDEFINED} IfcJunctionBoxTypeEnum;
std::string ToString(IfcJunctionBoxTypeEnum v);
IfcJunctionBoxTypeEnum FromString(const std::string& s);}
namespace IfcLampTypeEnum {typedef enum {COMPACTFLUORESCENT, FLUORESCENT, HIGHPRESSUREMERCURY, HIGHPRESSURESODIUM, METALHALIDE, TUNGSTENFILAMENT, USERDEFINED, NOTDEFINED} IfcLampTypeEnum;
std::string ToString(IfcLampTypeEnum v);
IfcLampTypeEnum FromString(const std::string& s);}
namespace IfcLayerSetDirectionEnum {typedef enum {AXIS1, AXIS2, AXIS3} IfcLayerSetDirectionEnum;
std::string ToString(IfcLayerSetDirectionEnum v);
IfcLayerSetDirectionEnum FromString(const std::string& s);}
namespace IfcLightDistributionCurveEnum {typedef enum {TYPE_A, TYPE_B, TYPE_C, NOTDEFINED} IfcLightDistributionCurveEnum;
std::string ToString(IfcLightDistributionCurveEnum v);
IfcLightDistributionCurveEnum FromString(const std::string& s);}
namespace IfcLightEmissionSourceEnum {typedef enum {COMPACTFLUORESCENT, FLUORESCENT, HIGHPRESSUREMERCURY, HIGHPRESSURESODIUM, LIGHTEMITTINGDIODE, LOWPRESSURESODIUM, LOWVOLTAGEHALOGEN, MAINVOLTAGEHALOGEN, METALHALIDE, TUNGSTENFILAMENT, NOTDEFINED} IfcLightEmissionSourceEnum;
std::string ToString(IfcLightEmissionSourceEnum v);
IfcLightEmissionSourceEnum FromString(const std::string& s);}
namespace IfcLightFixtureTypeEnum {typedef enum {POINTSOURCE, DIRECTIONSOURCE, USERDEFINED, NOTDEFINED} IfcLightFixtureTypeEnum;
std::string ToString(IfcLightFixtureTypeEnum v);
IfcLightFixtureTypeEnum FromString(const std::string& s);}
namespace IfcLoadGroupTypeEnum {typedef enum {LOAD_GROUP, LOAD_CASE, LOAD_COMBINATION_GROUP, LOAD_COMBINATION, USERDEFINED, NOTDEFINED} IfcLoadGroupTypeEnum;
std::string ToString(IfcLoadGroupTypeEnum v);
IfcLoadGroupTypeEnum FromString(const std::string& s);}
namespace IfcLogicalOperatorEnum {typedef enum {LOGICALAND, LOGICALOR} IfcLogicalOperatorEnum;
std::string ToString(IfcLogicalOperatorEnum v);
IfcLogicalOperatorEnum FromString(const std::string& s);}
namespace IfcMemberTypeEnum {typedef enum {BRACE, CHORD, COLLAR, MEMBER, MULLION, PLATE, POST, PURLIN, RAFTER, STRINGER, STRUT, STUD, USERDEFINED, NOTDEFINED} IfcMemberTypeEnum;
std::string ToString(IfcMemberTypeEnum v);
IfcMemberTypeEnum FromString(const std::string& s);}
namespace IfcMotorConnectionTypeEnum {typedef enum {BELTDRIVE, COUPLING, DIRECTDRIVE, USERDEFINED, NOTDEFINED} IfcMotorConnectionTypeEnum;
std::string ToString(IfcMotorConnectionTypeEnum v);
IfcMotorConnectionTypeEnum FromString(const std::string& s);}
namespace IfcNullStyle {typedef enum {IFC_NULL} IfcNullStyle;
std::string ToString(IfcNullStyle v);
IfcNullStyle FromString(const std::string& s);}
namespace IfcObjectTypeEnum {typedef enum {PRODUCT, PROCESS, CONTROL, RESOURCE, ACTOR, GROUP, PROJECT, NOTDEFINED} IfcObjectTypeEnum;
std::string ToString(IfcObjectTypeEnum v);
IfcObjectTypeEnum FromString(const std::string& s);}
namespace IfcObjectiveEnum {typedef enum {CODECOMPLIANCE, DESIGNINTENT, HEALTHANDSAFETY, REQUIREMENT, SPECIFICATION, TRIGGERCONDITION, USERDEFINED, NOTDEFINED} IfcObjectiveEnum;
std::string ToString(IfcObjectiveEnum v);
IfcObjectiveEnum FromString(const std::string& s);}
namespace IfcOccupantTypeEnum {typedef enum {ASSIGNEE, ASSIGNOR, LESSEE, LESSOR, LETTINGAGENT, OWNER, TENANT, USERDEFINED, NOTDEFINED} IfcOccupantTypeEnum;
std::string ToString(IfcOccupantTypeEnum v);
IfcOccupantTypeEnum FromString(const std::string& s);}
namespace IfcOutletTypeEnum {typedef enum {AUDIOVISUALOUTLET, COMMUNICATIONSOUTLET, POWEROUTLET, USERDEFINED, NOTDEFINED} IfcOutletTypeEnum;
std::string ToString(IfcOutletTypeEnum v);
IfcOutletTypeEnum FromString(const std::string& s);}
namespace IfcPermeableCoveringOperationEnum {typedef enum {GRILL, LOUVER, SCREEN, USERDEFINED, NOTDEFINED} IfcPermeableCoveringOperationEnum;
std::string ToString(IfcPermeableCoveringOperationEnum v);
IfcPermeableCoveringOperationEnum FromString(const std::string& s);}
namespace IfcPhysicalOrVirtualEnum {typedef enum {PHYSICAL, VIRTUAL, NOTDEFINED} IfcPhysicalOrVirtualEnum;
std::string ToString(IfcPhysicalOrVirtualEnum v);
IfcPhysicalOrVirtualEnum FromString(const std::string& s);}
namespace IfcPileConstructionEnum {typedef enum {CAST_IN_PLACE, COMPOSITE, PRECAST_CONCRETE, PREFAB_STEEL, USERDEFINED, NOTDEFINED} IfcPileConstructionEnum;
std::string ToString(IfcPileConstructionEnum v);
IfcPileConstructionEnum FromString(const std::string& s);}
namespace IfcPileTypeEnum {typedef enum {COHESION, FRICTION, SUPPORT, USERDEFINED, NOTDEFINED} IfcPileTypeEnum;
std::string ToString(IfcPileTypeEnum v);
IfcPileTypeEnum FromString(const std::string& s);}
namespace IfcPipeFittingTypeEnum {typedef enum {BEND, CONNECTOR, ENTRY, EXIT, JUNCTION, OBSTRUCTION, TRANSITION, USERDEFINED, NOTDEFINED} IfcPipeFittingTypeEnum;
std::string ToString(IfcPipeFittingTypeEnum v);
IfcPipeFittingTypeEnum FromString(const std::string& s);}
namespace IfcPipeSegmentTypeEnum {typedef enum {FLEXIBLESEGMENT, RIGIDSEGMENT, GUTTER, SPOOL, USERDEFINED, NOTDEFINED} IfcPipeSegmentTypeEnum;
std::string ToString(IfcPipeSegmentTypeEnum v);
IfcPipeSegmentTypeEnum FromString(const std::string& s);}
namespace IfcPlateTypeEnum {typedef enum {CURTAIN_PANEL, SHEET, USERDEFINED, NOTDEFINED} IfcPlateTypeEnum;
std::string ToString(IfcPlateTypeEnum v);
IfcPlateTypeEnum FromString(const std::string& s);}
namespace IfcProcedureTypeEnum {typedef enum {ADVICE_CAUTION, ADVICE_NOTE, ADVICE_WARNING, CALIBRATION, DIAGNOSTIC, SHUTDOWN, STARTUP, USERDEFINED, NOTDEFINED} IfcProcedureTypeEnum;
std::string ToString(IfcProcedureTypeEnum v);
IfcProcedureTypeEnum FromString(const std::string& s);}
namespace IfcProfileTypeEnum {typedef enum {CURVE, AREA} IfcProfileTypeEnum;
std::string ToString(IfcProfileTypeEnum v);
IfcProfileTypeEnum FromString(const std::string& s);}
namespace IfcProjectOrderRecordTypeEnum {typedef enum {CHANGE, MAINTENANCE, MOVE, PURCHASE, WORK, USERDEFINED, NOTDEFINED} IfcProjectOrderRecordTypeEnum;
std::string ToString(IfcProjectOrderRecordTypeEnum v);
IfcProjectOrderRecordTypeEnum FromString(const std::string& s);}
namespace IfcProjectOrderTypeEnum {typedef enum {CHANGEORDER, MAINTENANCEWORKORDER, MOVEORDER, PURCHASEORDER, WORKORDER, USERDEFINED, NOTDEFINED} IfcProjectOrderTypeEnum;
std::string ToString(IfcProjectOrderTypeEnum v);
IfcProjectOrderTypeEnum FromString(const std::string& s);}
namespace IfcProjectedOrTrueLengthEnum {typedef enum {PROJECTED_LENGTH, TRUE_LENGTH} IfcProjectedOrTrueLengthEnum;
std::string ToString(IfcProjectedOrTrueLengthEnum v);
IfcProjectedOrTrueLengthEnum FromString(const std::string& s);}
namespace IfcPropertySourceEnum {typedef enum {DESIGN, DESIGNMAXIMUM, DESIGNMINIMUM, SIMULATED, ASBUILT, COMMISSIONING, MEASURED, USERDEFINED, NOTKNOWN} IfcPropertySourceEnum;
std::string ToString(IfcPropertySourceEnum v);
IfcPropertySourceEnum FromString(const std::string& s);}
namespace IfcProtectiveDeviceTypeEnum {typedef enum {FUSEDISCONNECTOR, CIRCUITBREAKER, EARTHFAILUREDEVICE, RESIDUALCURRENTCIRCUITBREAKER, RESIDUALCURRENTSWITCH, VARISTOR, USERDEFINED, NOTDEFINED} IfcProtectiveDeviceTypeEnum;
std::string ToString(IfcProtectiveDeviceTypeEnum v);
IfcProtectiveDeviceTypeEnum FromString(const std::string& s);}
namespace IfcPumpTypeEnum {typedef enum {CIRCULATOR, ENDSUCTION, SPLITCASE, VERTICALINLINE, VERTICALTURBINE, USERDEFINED, NOTDEFINED} IfcPumpTypeEnum;
std::string ToString(IfcPumpTypeEnum v);
IfcPumpTypeEnum FromString(const std::string& s);}
namespace IfcRailingTypeEnum {typedef enum {HANDRAIL, GUARDRAIL, BALUSTRADE, USERDEFINED, NOTDEFINED} IfcRailingTypeEnum;
std::string ToString(IfcRailingTypeEnum v);
IfcRailingTypeEnum FromString(const std::string& s);}
namespace IfcRampFlightTypeEnum {typedef enum {STRAIGHT, SPIRAL, USERDEFINED, NOTDEFINED} IfcRampFlightTypeEnum;
std::string ToString(IfcRampFlightTypeEnum v);
IfcRampFlightTypeEnum FromString(const std::string& s);}
namespace IfcRampTypeEnum {typedef enum {STRAIGHT_RUN_RAMP, TWO_STRAIGHT_RUN_RAMP, QUARTER_TURN_RAMP, TWO_QUARTER_TURN_RAMP, HALF_TURN_RAMP, SPIRAL_RAMP, USERDEFINED, NOTDEFINED} IfcRampTypeEnum;
std::string ToString(IfcRampTypeEnum v);
IfcRampTypeEnum FromString(const std::string& s);}
namespace IfcReflectanceMethodEnum {typedef enum {BLINN, FLAT, GLASS, MATT, METAL, MIRROR, PHONG, PLASTIC, STRAUSS, NOTDEFINED} IfcReflectanceMethodEnum;
std::string ToString(IfcReflectanceMethodEnum v);
IfcReflectanceMethodEnum FromString(const std::string& s);}
namespace IfcReinforcingBarRoleEnum {typedef enum {MAIN, SHEAR, LIGATURE, STUD, PUNCHING, EDGE, RING, USERDEFINED, NOTDEFINED} IfcReinforcingBarRoleEnum;
std::string ToString(IfcReinforcingBarRoleEnum v);
IfcReinforcingBarRoleEnum FromString(const std::string& s);}
namespace IfcReinforcingBarSurfaceEnum {typedef enum {PLAIN, TEXTURED} IfcReinforcingBarSurfaceEnum;
std::string ToString(IfcReinforcingBarSurfaceEnum v);
IfcReinforcingBarSurfaceEnum FromString(const std::string& s);}
namespace IfcResourceConsumptionEnum {typedef enum {CONSUMED, PARTIALLYCONSUMED, NOTCONSUMED, OCCUPIED, PARTIALLYOCCUPIED, NOTOCCUPIED, USERDEFINED, NOTDEFINED} IfcResourceConsumptionEnum;
std::string ToString(IfcResourceConsumptionEnum v);
IfcResourceConsumptionEnum FromString(const std::string& s);}
namespace IfcRibPlateDirectionEnum {typedef enum {DIRECTION_X, DIRECTION_Y} IfcRibPlateDirectionEnum;
std::string ToString(IfcRibPlateDirectionEnum v);
IfcRibPlateDirectionEnum FromString(const std::string& s);}
namespace IfcRoleEnum {typedef enum {SUPPLIER, MANUFACTURER, CONTRACTOR, SUBCONTRACTOR, ARCHITECT, STRUCTURALENGINEER, COSTENGINEER, CLIENT, BUILDINGOWNER, BUILDINGOPERATOR, MECHANICALENGINEER, ELECTRICALENGINEER, PROJECTMANAGER, FACILITIESMANAGER, CIVILENGINEER, COMISSIONINGENGINEER, ENGINEER, OWNER, CONSULTANT, CONSTRUCTIONMANAGER, FIELDCONSTRUCTIONMANAGER, RESELLER, USERDEFINED} IfcRoleEnum;
std::string ToString(IfcRoleEnum v);
IfcRoleEnum FromString(const std::string& s);}
namespace IfcRoofTypeEnum {typedef enum {FLAT_ROOF, SHED_ROOF, GABLE_ROOF, HIP_ROOF, HIPPED_GABLE_ROOF, GAMBREL_ROOF, MANSARD_ROOF, BARREL_ROOF, RAINBOW_ROOF, BUTTERFLY_ROOF, PAVILION_ROOF, DOME_ROOF, FREEFORM, NOTDEFINED} IfcRoofTypeEnum;
std::string ToString(IfcRoofTypeEnum v);
IfcRoofTypeEnum FromString(const std::string& s);}
namespace IfcSIPrefix {typedef enum {EXA, PETA, TERA, GIGA, MEGA, KILO, HECTO, DECA, DECI, CENTI, MILLI, MICRO, NANO, PICO, FEMTO, ATTO} IfcSIPrefix;
std::string ToString(IfcSIPrefix v);
IfcSIPrefix FromString(const std::string& s);}
namespace IfcSIUnitName {typedef enum {AMPERE, BECQUEREL, CANDELA, COULOMB, CUBIC_METRE, DEGREE_CELSIUS, FARAD, GRAM, GRAY, HENRY, HERTZ, JOULE, KELVIN, LUMEN, LUX, METRE, MOLE, NEWTON, OHM, PASCAL, RADIAN, SECOND, SIEMENS, SIEVERT, SQUARE_METRE, STERADIAN, TESLA, VOLT, WATT, WEBER} IfcSIUnitName;
std::string ToString(IfcSIUnitName v);
IfcSIUnitName FromString(const std::string& s);}
namespace IfcSanitaryTerminalTypeEnum {typedef enum {BATH, BIDET, CISTERN, SHOWER, SINK, SANITARYFOUNTAIN, TOILETPAN, URINAL, WASHHANDBASIN, WCSEAT, USERDEFINED, NOTDEFINED} IfcSanitaryTerminalTypeEnum;
std::string ToString(IfcSanitaryTerminalTypeEnum v);
IfcSanitaryTerminalTypeEnum FromString(const std::string& s);}
namespace IfcSectionTypeEnum {typedef enum {UNIFORM, TAPERED} IfcSectionTypeEnum;
std::string ToString(IfcSectionTypeEnum v);
IfcSectionTypeEnum FromString(const std::string& s);}
namespace IfcSensorTypeEnum {typedef enum {CO2SENSOR, FIRESENSOR, FLOWSENSOR, GASSENSOR, HEATSENSOR, HUMIDITYSENSOR, LIGHTSENSOR, MOISTURESENSOR, MOVEMENTSENSOR, PRESSURESENSOR, SMOKESENSOR, SOUNDSENSOR, TEMPERATURESENSOR, USERDEFINED, NOTDEFINED} IfcSensorTypeEnum;
std::string ToString(IfcSensorTypeEnum v);
IfcSensorTypeEnum FromString(const std::string& s);}
namespace IfcSequenceEnum {typedef enum {START_START, START_FINISH, FINISH_START, FINISH_FINISH, NOTDEFINED} IfcSequenceEnum;
std::string ToString(IfcSequenceEnum v);
IfcSequenceEnum FromString(const std::string& s);}
namespace IfcServiceLifeFactorTypeEnum {typedef enum {A_QUALITYOFCOMPONENTS, B_DESIGNLEVEL, C_WORKEXECUTIONLEVEL, D_INDOORENVIRONMENT, E_OUTDOORENVIRONMENT, F_INUSECONDITIONS, G_MAINTENANCELEVEL, USERDEFINED, NOTDEFINED} IfcServiceLifeFactorTypeEnum;
std::string ToString(IfcServiceLifeFactorTypeEnum v);
IfcServiceLifeFactorTypeEnum FromString(const std::string& s);}
namespace IfcServiceLifeTypeEnum {typedef enum {ACTUALSERVICELIFE, EXPECTEDSERVICELIFE, OPTIMISTICREFERENCESERVICELIFE, PESSIMISTICREFERENCESERVICELIFE, REFERENCESERVICELIFE} IfcServiceLifeTypeEnum;
std::string ToString(IfcServiceLifeTypeEnum v);
IfcServiceLifeTypeEnum FromString(const std::string& s);}
namespace IfcSlabTypeEnum {typedef enum {FLOOR, ROOF, LANDING, BASESLAB, USERDEFINED, NOTDEFINED} IfcSlabTypeEnum;
std::string ToString(IfcSlabTypeEnum v);
IfcSlabTypeEnum FromString(const std::string& s);}
namespace IfcSoundScaleEnum {typedef enum {DBA, DBB, DBC, NC, NR, USERDEFINED, NOTDEFINED} IfcSoundScaleEnum;
std::string ToString(IfcSoundScaleEnum v);
IfcSoundScaleEnum FromString(const std::string& s);}
namespace IfcSpaceHeaterTypeEnum {typedef enum {SECTIONALRADIATOR, PANELRADIATOR, TUBULARRADIATOR, CONVECTOR, BASEBOARDHEATER, FINNEDTUBEUNIT, UNITHEATER, USERDEFINED, NOTDEFINED} IfcSpaceHeaterTypeEnum;
std::string ToString(IfcSpaceHeaterTypeEnum v);
IfcSpaceHeaterTypeEnum FromString(const std::string& s);}
namespace IfcSpaceTypeEnum {typedef enum {USERDEFINED, NOTDEFINED} IfcSpaceTypeEnum;
std::string ToString(IfcSpaceTypeEnum v);
IfcSpaceTypeEnum FromString(const std::string& s);}
namespace IfcStackTerminalTypeEnum {typedef enum {BIRDCAGE, COWL, RAINWATERHOPPER, USERDEFINED, NOTDEFINED} IfcStackTerminalTypeEnum;
std::string ToString(IfcStackTerminalTypeEnum v);
IfcStackTerminalTypeEnum FromString(const std::string& s);}
namespace IfcStairFlightTypeEnum {typedef enum {STRAIGHT, WINDER, SPIRAL, CURVED, FREEFORM, USERDEFINED, NOTDEFINED} IfcStairFlightTypeEnum;
std::string ToString(IfcStairFlightTypeEnum v);
IfcStairFlightTypeEnum FromString(const std::string& s);}
namespace IfcStairTypeEnum {typedef enum {STRAIGHT_RUN_STAIR, TWO_STRAIGHT_RUN_STAIR, QUARTER_WINDING_STAIR, QUARTER_TURN_STAIR, HALF_WINDING_STAIR, HALF_TURN_STAIR, TWO_QUARTER_WINDING_STAIR, TWO_QUARTER_TURN_STAIR, THREE_QUARTER_WINDING_STAIR, THREE_QUARTER_TURN_STAIR, SPIRAL_STAIR, DOUBLE_RETURN_STAIR, CURVED_RUN_STAIR, TWO_CURVED_RUN_STAIR, USERDEFINED, NOTDEFINED} IfcStairTypeEnum;
std::string ToString(IfcStairTypeEnum v);
IfcStairTypeEnum FromString(const std::string& s);}
namespace IfcStateEnum {typedef enum {READWRITE, READONLY, LOCKED, READWRITELOCKED, READONLYLOCKED} IfcStateEnum;
std::string ToString(IfcStateEnum v);
IfcStateEnum FromString(const std::string& s);}
namespace IfcStructuralCurveTypeEnum {typedef enum {RIGID_JOINED_MEMBER, PIN_JOINED_MEMBER, CABLE, TENSION_MEMBER, COMPRESSION_MEMBER, USERDEFINED, NOTDEFINED} IfcStructuralCurveTypeEnum;
std::string ToString(IfcStructuralCurveTypeEnum v);
IfcStructuralCurveTypeEnum FromString(const std::string& s);}
namespace IfcStructuralSurfaceTypeEnum {typedef enum {BENDING_ELEMENT, MEMBRANE_ELEMENT, SHELL, USERDEFINED, NOTDEFINED} IfcStructuralSurfaceTypeEnum;
std::string ToString(IfcStructuralSurfaceTypeEnum v);
IfcStructuralSurfaceTypeEnum FromString(const std::string& s);}
namespace IfcSurfaceSide {typedef enum {POSITIVE, NEGATIVE, BOTH} IfcSurfaceSide;
std::string ToString(IfcSurfaceSide v);
IfcSurfaceSide FromString(const std::string& s);}
namespace IfcSurfaceTextureEnum {typedef enum {BUMP, OPACITY, REFLECTION, SELFILLUMINATION, SHININESS, SPECULAR, TEXTURE, TRANSPARENCYMAP, NOTDEFINED} IfcSurfaceTextureEnum;
std::string ToString(IfcSurfaceTextureEnum v);
IfcSurfaceTextureEnum FromString(const std::string& s);}
namespace IfcSwitchingDeviceTypeEnum {typedef enum {CONTACTOR, EMERGENCYSTOP, STARTER, SWITCHDISCONNECTOR, TOGGLESWITCH, USERDEFINED, NOTDEFINED} IfcSwitchingDeviceTypeEnum;
std::string ToString(IfcSwitchingDeviceTypeEnum v);
IfcSwitchingDeviceTypeEnum FromString(const std::string& s);}
namespace IfcTankTypeEnum {typedef enum {PREFORMED, SECTIONAL, EXPANSION, PRESSUREVESSEL, USERDEFINED, NOTDEFINED} IfcTankTypeEnum;
std::string ToString(IfcTankTypeEnum v);
IfcTankTypeEnum FromString(const std::string& s);}
namespace IfcTendonTypeEnum {typedef enum {STRAND, WIRE, BAR, COATED, USERDEFINED, NOTDEFINED} IfcTendonTypeEnum;
std::string ToString(IfcTendonTypeEnum v);
IfcTendonTypeEnum FromString(const std::string& s);}
namespace IfcTextPath {typedef enum {LEFT, RIGHT, UP, DOWN} IfcTextPath;
std::string ToString(IfcTextPath v);
IfcTextPath FromString(const std::string& s);}
namespace IfcThermalLoadSourceEnum {typedef enum {PEOPLE, LIGHTING, EQUIPMENT, VENTILATIONINDOORAIR, VENTILATIONOUTSIDEAIR, RECIRCULATEDAIR, EXHAUSTAIR, AIREXCHANGERATE, DRYBULBTEMPERATURE, RELATIVEHUMIDITY, INFILTRATION, USERDEFINED, NOTDEFINED} IfcThermalLoadSourceEnum;
std::string ToString(IfcThermalLoadSourceEnum v);
IfcThermalLoadSourceEnum FromString(const std::string& s);}
namespace IfcThermalLoadTypeEnum {typedef enum {SENSIBLE, LATENT, RADIANT, NOTDEFINED} IfcThermalLoadTypeEnum;
std::string ToString(IfcThermalLoadTypeEnum v);
IfcThermalLoadTypeEnum FromString(const std::string& s);}
namespace IfcTimeSeriesDataTypeEnum {typedef enum {CONTINUOUS, DISCRETE, DISCRETEBINARY, PIECEWISEBINARY, PIECEWISECONSTANT, PIECEWISECONTINUOUS, NOTDEFINED} IfcTimeSeriesDataTypeEnum;
std::string ToString(IfcTimeSeriesDataTypeEnum v);
IfcTimeSeriesDataTypeEnum FromString(const std::string& s);}
namespace IfcTimeSeriesScheduleTypeEnum {typedef enum {ANNUAL, MONTHLY, WEEKLY, DAILY, USERDEFINED, NOTDEFINED} IfcTimeSeriesScheduleTypeEnum;
std::string ToString(IfcTimeSeriesScheduleTypeEnum v);
IfcTimeSeriesScheduleTypeEnum FromString(const std::string& s);}
namespace IfcTransformerTypeEnum {typedef enum {CURRENT, FREQUENCY, VOLTAGE, USERDEFINED, NOTDEFINED} IfcTransformerTypeEnum;
std::string ToString(IfcTransformerTypeEnum v);
IfcTransformerTypeEnum FromString(const std::string& s);}
namespace IfcTransitionCode {typedef enum {DISCONTINUOUS, CONTINUOUS, CONTSAMEGRADIENT, CONTSAMEGRADIENTSAMECURVATURE} IfcTransitionCode;
std::string ToString(IfcTransitionCode v);
IfcTransitionCode FromString(const std::string& s);}
namespace IfcTransportElementTypeEnum {typedef enum {ELEVATOR, ESCALATOR, MOVINGWALKWAY, USERDEFINED, NOTDEFINED} IfcTransportElementTypeEnum;
std::string ToString(IfcTransportElementTypeEnum v);
IfcTransportElementTypeEnum FromString(const std::string& s);}
namespace IfcTrimmingPreference {typedef enum {CARTESIAN, PARAMETER, UNSPECIFIED} IfcTrimmingPreference;
std::string ToString(IfcTrimmingPreference v);
IfcTrimmingPreference FromString(const std::string& s);}
namespace IfcTubeBundleTypeEnum {typedef enum {FINNED, USERDEFINED, NOTDEFINED} IfcTubeBundleTypeEnum;
std::string ToString(IfcTubeBundleTypeEnum v);
IfcTubeBundleTypeEnum FromString(const std::string& s);}
namespace IfcUnitEnum {typedef enum {ABSORBEDDOSEUNIT, AMOUNTOFSUBSTANCEUNIT, AREAUNIT, DOSEEQUIVALENTUNIT, ELECTRICCAPACITANCEUNIT, ELECTRICCHARGEUNIT, ELECTRICCONDUCTANCEUNIT, ELECTRICCURRENTUNIT, ELECTRICRESISTANCEUNIT, ELECTRICVOLTAGEUNIT, ENERGYUNIT, FORCEUNIT, FREQUENCYUNIT, ILLUMINANCEUNIT, INDUCTANCEUNIT, LENGTHUNIT, LUMINOUSFLUXUNIT, LUMINOUSINTENSITYUNIT, MAGNETICFLUXDENSITYUNIT, MAGNETICFLUXUNIT, MASSUNIT, PLANEANGLEUNIT, POWERUNIT, PRESSUREUNIT, RADIOACTIVITYUNIT, SOLIDANGLEUNIT, THERMODYNAMICTEMPERATUREUNIT, TIMEUNIT, VOLUMEUNIT, USERDEFINED} IfcUnitEnum;
std::string ToString(IfcUnitEnum v);
IfcUnitEnum FromString(const std::string& s);}
namespace IfcUnitaryEquipmentTypeEnum {typedef enum {AIRHANDLER, AIRCONDITIONINGUNIT, SPLITSYSTEM, ROOFTOPUNIT, USERDEFINED, NOTDEFINED} IfcUnitaryEquipmentTypeEnum;
std::string ToString(IfcUnitaryEquipmentTypeEnum v);
IfcUnitaryEquipmentTypeEnum FromString(const std::string& s);}
namespace IfcValveTypeEnum {typedef enum {AIRRELEASE, ANTIVACUUM, CHANGEOVER, CHECK, COMMISSIONING, DIVERTING, DRAWOFFCOCK, DOUBLECHECK, DOUBLEREGULATING, FAUCET, FLUSHING, GASCOCK, GASTAP, ISOLATING, MIXING, PRESSUREREDUCING, PRESSURERELIEF, REGULATING, SAFETYCUTOFF, STEAMTRAP, STOPCOCK, USERDEFINED, NOTDEFINED} IfcValveTypeEnum;
std::string ToString(IfcValveTypeEnum v);
IfcValveTypeEnum FromString(const std::string& s);}
namespace IfcVibrationIsolatorTypeEnum {typedef enum {COMPRESSION, SPRING, USERDEFINED, NOTDEFINED} IfcVibrationIsolatorTypeEnum;
std::string ToString(IfcVibrationIsolatorTypeEnum v);
IfcVibrationIsolatorTypeEnum FromString(const std::string& s);}
namespace IfcWallTypeEnum {typedef enum {STANDARD, POLYGONAL, SHEAR, ELEMENTEDWALL, PLUMBINGWALL, USERDEFINED, NOTDEFINED} IfcWallTypeEnum;
std::string ToString(IfcWallTypeEnum v);
IfcWallTypeEnum FromString(const std::string& s);}
namespace IfcWasteTerminalTypeEnum {typedef enum {FLOORTRAP, FLOORWASTE, GULLYSUMP, GULLYTRAP, GREASEINTERCEPTOR, OILINTERCEPTOR, PETROLINTERCEPTOR, ROOFDRAIN, WASTEDISPOSALUNIT, WASTETRAP, USERDEFINED, NOTDEFINED} IfcWasteTerminalTypeEnum;
std::string ToString(IfcWasteTerminalTypeEnum v);
IfcWasteTerminalTypeEnum FromString(const std::string& s);}
namespace IfcWindowPanelOperationEnum {typedef enum {SIDEHUNGRIGHTHAND, SIDEHUNGLEFTHAND, TILTANDTURNRIGHTHAND, TILTANDTURNLEFTHAND, TOPHUNG, BOTTOMHUNG, PIVOTHORIZONTAL, PIVOTVERTICAL, SLIDINGHORIZONTAL, SLIDINGVERTICAL, REMOVABLECASEMENT, FIXEDCASEMENT, OTHEROPERATION, NOTDEFINED} IfcWindowPanelOperationEnum;
std::string ToString(IfcWindowPanelOperationEnum v);
IfcWindowPanelOperationEnum FromString(const std::string& s);}
namespace IfcWindowPanelPositionEnum {typedef enum {LEFT, MIDDLE, RIGHT, BOTTOM, TOP, NOTDEFINED} IfcWindowPanelPositionEnum;
std::string ToString(IfcWindowPanelPositionEnum v);
IfcWindowPanelPositionEnum FromString(const std::string& s);}
namespace IfcWindowStyleConstructionEnum {typedef enum {ALUMINIUM, HIGH_GRADE_STEEL, STEEL, WOOD, ALUMINIUM_WOOD, PLASTIC, OTHER_CONSTRUCTION, NOTDEFINED} IfcWindowStyleConstructionEnum;
std::string ToString(IfcWindowStyleConstructionEnum v);
IfcWindowStyleConstructionEnum FromString(const std::string& s);}
namespace IfcWindowStyleOperationEnum {typedef enum {SINGLE_PANEL, DOUBLE_PANEL_VERTICAL, DOUBLE_PANEL_HORIZONTAL, TRIPLE_PANEL_VERTICAL, TRIPLE_PANEL_BOTTOM, TRIPLE_PANEL_TOP, TRIPLE_PANEL_LEFT, TRIPLE_PANEL_RIGHT, TRIPLE_PANEL_HORIZONTAL, USERDEFINED, NOTDEFINED} IfcWindowStyleOperationEnum;
std::string ToString(IfcWindowStyleOperationEnum v);
IfcWindowStyleOperationEnum FromString(const std::string& s);}
namespace IfcWorkControlTypeEnum {typedef enum {ACTUAL, BASELINE, PLANNED, USERDEFINED, NOTDEFINED} IfcWorkControlTypeEnum;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcActorRole (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcActorRole> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAddress (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAddress> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAddress> > list;
    typedef IfcTemplatedEntityList<IfcAddress>::it it;
};
class IfcApplication : public IfcBaseClass {
public:
    SHARED_PTR<IfcOrganization> ApplicationDeveloper();
    IfcLabel Version();
    IfcLabel ApplicationFullName();
    IfcIdentifier ApplicationIdentifier();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcApplication (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcApplication> ptr;
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
    SHARED_PTR<IfcMeasureWithUnit> UnitBasis();
    bool hasApplicableDate();
    IfcDateTimeSelect ApplicableDate();
    bool hasFixedUntilDate();
    IfcDateTimeSelect FixedUntilDate();
    SHARED_PTR< IfcTemplatedEntityList<IfcReferencesValueDocument> > ValuesReferenced(); // INVERSE IfcReferencesValueDocument::ReferencingValues
    SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValueRelationship> > ValueOfComponents(); // INVERSE IfcAppliedValueRelationship::ComponentOfTotal
    SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValueRelationship> > IsComponentIn(); // INVERSE IfcAppliedValueRelationship::Components
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAppliedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAppliedValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > list;
    typedef IfcTemplatedEntityList<IfcAppliedValue>::it it;
};
class IfcAppliedValueRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcAppliedValue> ComponentOfTotal();
    SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > Components();
    IfcArithmeticOperatorEnum::IfcArithmeticOperatorEnum ArithmeticOperator();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAppliedValueRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAppliedValueRelationship> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcApproval (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcApproval> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApproval> > list;
    typedef IfcTemplatedEntityList<IfcApproval>::it it;
};
class IfcApprovalActorRelationship : public IfcBaseClass {
public:
    IfcActorSelect Actor();
    SHARED_PTR<IfcApproval> Approval();
    SHARED_PTR<IfcActorRole> Role();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcApprovalActorRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcApprovalActorRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApprovalActorRelationship> > list;
    typedef IfcTemplatedEntityList<IfcApprovalActorRelationship>::it it;
};
class IfcApprovalPropertyRelationship : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > ApprovedProperties();
    SHARED_PTR<IfcApproval> Approval();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcApprovalPropertyRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcApprovalPropertyRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApprovalPropertyRelationship> > list;
    typedef IfcTemplatedEntityList<IfcApprovalPropertyRelationship>::it it;
};
class IfcApprovalRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcApproval> RelatedApproval();
    SHARED_PTR<IfcApproval> RelatingApproval();
    bool hasDescription();
    IfcText Description();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcApprovalRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcApprovalRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcApprovalRelationship> > list;
    typedef IfcTemplatedEntityList<IfcApprovalRelationship>::it it;
};
class IfcBoundaryCondition : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundaryCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundaryCondition> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundaryEdgeCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundaryEdgeCondition> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundaryFaceCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundaryFaceCondition> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundaryNodeCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundaryNodeCondition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundaryNodeCondition> > list;
    typedef IfcTemplatedEntityList<IfcBoundaryNodeCondition>::it it;
};
class IfcBoundaryNodeConditionWarping : public IfcBoundaryNodeCondition {
public:
    bool hasWarpingStiffness();
    IfcWarpingMomentMeasure WarpingStiffness();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundaryNodeConditionWarping (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundaryNodeConditionWarping> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundaryNodeConditionWarping> > list;
    typedef IfcTemplatedEntityList<IfcBoundaryNodeConditionWarping>::it it;
};
class IfcCalendarDate : public IfcBaseClass {
public:
    IfcDayInMonthNumber DayComponent();
    IfcMonthInYearNumber MonthComponent();
    IfcYearNumber YearComponent();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCalendarDate (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCalendarDate> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCalendarDate> > list;
    typedef IfcTemplatedEntityList<IfcCalendarDate>::it it;
};
class IfcClassification : public IfcBaseClass {
public:
    IfcLabel Source();
    IfcLabel Edition();
    bool hasEditionDate();
    SHARED_PTR<IfcCalendarDate> EditionDate();
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > Contains(); // INVERSE IfcClassificationItem::ItemOf
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcClassification (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcClassification> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassification> > list;
    typedef IfcTemplatedEntityList<IfcClassification>::it it;
};
class IfcClassificationItem : public IfcBaseClass {
public:
    SHARED_PTR<IfcClassificationNotationFacet> Notation();
    bool hasItemOf();
    SHARED_PTR<IfcClassification> ItemOf();
    IfcLabel Title();
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItemRelationship> > IsClassifiedItemIn(); // INVERSE IfcClassificationItemRelationship::RelatedItems
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItemRelationship> > IsClassifyingItemIn(); // INVERSE IfcClassificationItemRelationship::RelatingItem
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcClassificationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcClassificationItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > list;
    typedef IfcTemplatedEntityList<IfcClassificationItem>::it it;
};
class IfcClassificationItemRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcClassificationItem> RelatingItem();
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > RelatedItems();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcClassificationItemRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcClassificationItemRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItemRelationship> > list;
    typedef IfcTemplatedEntityList<IfcClassificationItemRelationship>::it it;
};
class IfcClassificationNotation : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotationFacet> > NotationFacets();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcClassificationNotation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcClassificationNotation> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotation> > list;
    typedef IfcTemplatedEntityList<IfcClassificationNotation>::it it;
};
class IfcClassificationNotationFacet : public IfcBaseClass {
public:
    IfcLabel NotationValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcClassificationNotationFacet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcClassificationNotationFacet> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotationFacet> > list;
    typedef IfcTemplatedEntityList<IfcClassificationNotationFacet>::it it;
};
class IfcColourSpecification : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcColourSpecification (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcColourSpecification> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColourSpecification> > list;
    typedef IfcTemplatedEntityList<IfcColourSpecification>::it it;
};
class IfcConnectionGeometry : public IfcBaseClass {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConnectionGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConnectionGeometry> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionGeometry>::it it;
};
class IfcConnectionPointGeometry : public IfcConnectionGeometry {
public:
    IfcPointOrVertexPoint PointOnRelatingElement();
    bool hasPointOnRelatedElement();
    IfcPointOrVertexPoint PointOnRelatedElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConnectionPointGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConnectionPointGeometry> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionPointGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionPointGeometry>::it it;
};
class IfcConnectionPortGeometry : public IfcConnectionGeometry {
public:
    IfcAxis2Placement LocationAtRelatingElement();
    bool hasLocationAtRelatedElement();
    IfcAxis2Placement LocationAtRelatedElement();
    SHARED_PTR<IfcProfileDef> ProfileOfPort();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConnectionPortGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConnectionPortGeometry> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionPortGeometry> > list;
    typedef IfcTemplatedEntityList<IfcConnectionPortGeometry>::it it;
};
class IfcConnectionSurfaceGeometry : public IfcConnectionGeometry {
public:
    IfcSurfaceOrFaceSurface SurfaceOnRelatingElement();
    bool hasSurfaceOnRelatedElement();
    IfcSurfaceOrFaceSurface SurfaceOnRelatedElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConnectionSurfaceGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConnectionSurfaceGeometry> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstraint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstraint> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > list;
    typedef IfcTemplatedEntityList<IfcConstraint>::it it;
};
class IfcConstraintAggregationRelationship : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR<IfcConstraint> RelatingConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > RelatedConstraints();
    IfcLogicalOperatorEnum::IfcLogicalOperatorEnum LogicalAggregator();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstraintAggregationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstraintAggregationRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraintAggregationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcConstraintAggregationRelationship>::it it;
};
class IfcConstraintClassificationRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcConstraint> ClassifiedConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > RelatedClassifications();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstraintClassificationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstraintClassificationRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraintClassificationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcConstraintClassificationRelationship>::it it;
};
class IfcConstraintRelationship : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR<IfcConstraint> RelatingConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > RelatedConstraints();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstraintRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstraintRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstraintRelationship> > list;
    typedef IfcTemplatedEntityList<IfcConstraintRelationship>::it it;
};
class IfcCoordinatedUniversalTimeOffset : public IfcBaseClass {
public:
    IfcHourInDay HourOffset();
    bool hasMinuteOffset();
    IfcMinuteInHour MinuteOffset();
    IfcAheadOrBehind::IfcAheadOrBehind Sense();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCoordinatedUniversalTimeOffset (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCoordinatedUniversalTimeOffset> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoordinatedUniversalTimeOffset> > list;
    typedef IfcTemplatedEntityList<IfcCoordinatedUniversalTimeOffset>::it it;
};
class IfcCostValue : public IfcAppliedValue {
public:
    IfcLabel CostType();
    bool hasCondition();
    IfcText Condition();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCostValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCostValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCostValue> > list;
    typedef IfcTemplatedEntityList<IfcCostValue>::it it;
};
class IfcCurrencyRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcMonetaryUnit> RelatingMonetaryUnit();
    SHARED_PTR<IfcMonetaryUnit> RelatedMonetaryUnit();
    IfcPositiveRatioMeasure ExchangeRate();
    SHARED_PTR<IfcDateAndTime> RateDateTime();
    bool hasRateSource();
    SHARED_PTR<IfcLibraryInformation> RateSource();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurrencyRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurrencyRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurrencyRelationship> > list;
    typedef IfcTemplatedEntityList<IfcCurrencyRelationship>::it it;
};
class IfcCurveStyleFont : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontPattern> > PatternList();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurveStyleFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurveStyleFont> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFont> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyleFont>::it it;
};
class IfcCurveStyleFontAndScaling : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    IfcCurveStyleFontSelect CurveFont();
    IfcPositiveRatioMeasure CurveFontScaling();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurveStyleFontAndScaling (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurveStyleFontAndScaling> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontAndScaling> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyleFontAndScaling>::it it;
};
class IfcCurveStyleFontPattern : public IfcBaseClass {
public:
    IfcLengthMeasure VisibleSegmentLength();
    IfcPositiveLengthMeasure InvisibleSegmentLength();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurveStyleFontPattern (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurveStyleFontPattern> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontPattern> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyleFontPattern>::it it;
};
class IfcDateAndTime : public IfcBaseClass {
public:
    SHARED_PTR<IfcCalendarDate> DateComponent();
    SHARED_PTR<IfcLocalTime> TimeComponent();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDateAndTime (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDateAndTime> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDateAndTime> > list;
    typedef IfcTemplatedEntityList<IfcDateAndTime>::it it;
};
class IfcDerivedUnit : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcDerivedUnitElement> > Elements();
    IfcDerivedUnitEnum::IfcDerivedUnitEnum UnitType();
    bool hasUserDefinedType();
    IfcLabel UserDefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDerivedUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDerivedUnit> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDerivedUnit> > list;
    typedef IfcTemplatedEntityList<IfcDerivedUnit>::it it;
};
class IfcDerivedUnitElement : public IfcBaseClass {
public:
    SHARED_PTR<IfcNamedUnit> Unit();
    int Exponent();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDerivedUnitElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDerivedUnitElement> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDimensionalExponents (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDimensionalExponents> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDocumentElectronicFormat (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDocumentElectronicFormat> ptr;
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
    SHARED_PTR<IfcDateAndTime> CreationTime();
    bool hasLastRevisionTime();
    SHARED_PTR<IfcDateAndTime> LastRevisionTime();
    bool hasElectronicFormat();
    SHARED_PTR<IfcDocumentElectronicFormat> ElectronicFormat();
    bool hasValidFrom();
    SHARED_PTR<IfcCalendarDate> ValidFrom();
    bool hasValidUntil();
    SHARED_PTR<IfcCalendarDate> ValidUntil();
    bool hasConfidentiality();
    IfcDocumentConfidentialityEnum::IfcDocumentConfidentialityEnum Confidentiality();
    bool hasStatus();
    IfcDocumentStatusEnum::IfcDocumentStatusEnum Status();
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformationRelationship> > IsPointedTo(); // INVERSE IfcDocumentInformationRelationship::RelatedDocuments
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformationRelationship> > IsPointer(); // INVERSE IfcDocumentInformationRelationship::RelatingDocument
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDocumentInformation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDocumentInformation> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > list;
    typedef IfcTemplatedEntityList<IfcDocumentInformation>::it it;
};
class IfcDocumentInformationRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcDocumentInformation> RelatingDocument();
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > RelatedDocuments();
    bool hasRelationshipType();
    IfcLabel RelationshipType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDocumentInformationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDocumentInformationRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcDocumentInformationRelationship>::it it;
};
class IfcDraughtingCalloutRelationship : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR<IfcDraughtingCallout> RelatingDraughtingCallout();
    SHARED_PTR<IfcDraughtingCallout> RelatedDraughtingCallout();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDraughtingCalloutRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDraughtingCalloutRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCalloutRelationship> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingCalloutRelationship>::it it;
};
class IfcEnvironmentalImpactValue : public IfcAppliedValue {
public:
    IfcLabel ImpactType();
    IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategoryEnum Category();
    bool hasUserDefinedCategory();
    IfcLabel UserDefinedCategory();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEnvironmentalImpactValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEnvironmentalImpactValue> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcExternalReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcExternalReference> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternalReference> > list;
    typedef IfcTemplatedEntityList<IfcExternalReference>::it it;
};
class IfcExternallyDefinedHatchStyle : public IfcExternalReference {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcExternallyDefinedHatchStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcExternallyDefinedHatchStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedHatchStyle> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedHatchStyle>::it it;
};
class IfcExternallyDefinedSurfaceStyle : public IfcExternalReference {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcExternallyDefinedSurfaceStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcExternallyDefinedSurfaceStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedSurfaceStyle> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedSurfaceStyle>::it it;
};
class IfcExternallyDefinedSymbol : public IfcExternalReference {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcExternallyDefinedSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcExternallyDefinedSymbol> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedSymbol> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedSymbol>::it it;
};
class IfcExternallyDefinedTextFont : public IfcExternalReference {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcExternallyDefinedTextFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcExternallyDefinedTextFont> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExternallyDefinedTextFont> > list;
    typedef IfcTemplatedEntityList<IfcExternallyDefinedTextFont>::it it;
};
class IfcGridAxis : public IfcBaseClass {
public:
    bool hasAxisTag();
    IfcLabel AxisTag();
    SHARED_PTR<IfcCurve> AxisCurve();
    IfcBoolean SameSense();
    SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > PartOfW(); // INVERSE IfcGrid::WAxes
    SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > PartOfV(); // INVERSE IfcGrid::VAxes
    SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > PartOfU(); // INVERSE IfcGrid::UAxes
    SHARED_PTR< IfcTemplatedEntityList<IfcVirtualGridIntersection> > HasIntersections(); // INVERSE IfcVirtualGridIntersection::IntersectingAxes
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGridAxis (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGridAxis> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > list;
    typedef IfcTemplatedEntityList<IfcGridAxis>::it it;
};
class IfcIrregularTimeSeriesValue : public IfcBaseClass {
public:
    IfcDateTimeSelect TimeStamp();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ListValues();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcIrregularTimeSeriesValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcIrregularTimeSeriesValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeriesValue> > list;
    typedef IfcTemplatedEntityList<IfcIrregularTimeSeriesValue>::it it;
};
class IfcLibraryInformation : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasVersion();
    IfcLabel Version();
    bool hasPublisher();
    SHARED_PTR<IfcOrganization> Publisher();
    bool hasVersionDate();
    SHARED_PTR<IfcCalendarDate> VersionDate();
    bool hasLibraryReference();
    SHARED_PTR< IfcTemplatedEntityList<IfcLibraryReference> > LibraryReference();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLibraryInformation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLibraryInformation> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLibraryInformation> > list;
    typedef IfcTemplatedEntityList<IfcLibraryInformation>::it it;
};
class IfcLibraryReference : public IfcExternalReference {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcLibraryInformation> > ReferenceIntoLibrary(); // INVERSE IfcLibraryInformation::LibraryReference
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLibraryReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLibraryReference> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLibraryReference> > list;
    typedef IfcTemplatedEntityList<IfcLibraryReference>::it it;
};
class IfcLightDistributionData : public IfcBaseClass {
public:
    IfcPlaneAngleMeasure MainPlaneAngle();
    std::vector<IfcPlaneAngleMeasure> /*[1:?]*/ SecondaryPlaneAngle();
    std::vector<IfcLuminousIntensityDistributionMeasure> /*[1:?]*/ LuminousIntensity();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightDistributionData (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightDistributionData> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightDistributionData> > list;
    typedef IfcTemplatedEntityList<IfcLightDistributionData>::it it;
};
class IfcLightIntensityDistribution : public IfcBaseClass {
public:
    IfcLightDistributionCurveEnum::IfcLightDistributionCurveEnum LightDistributionCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcLightDistributionData> > DistributionData();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightIntensityDistribution (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightIntensityDistribution> ptr;
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
    SHARED_PTR<IfcCoordinatedUniversalTimeOffset> Zone();
    bool hasDaylightSavingOffset();
    IfcDaylightSavingHour DaylightSavingOffset();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLocalTime (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLocalTime> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLocalTime> > list;
    typedef IfcTemplatedEntityList<IfcLocalTime>::it it;
};
class IfcMaterial : public IfcBaseClass {
public:
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialDefinitionRepresentation> > HasRepresentation(); // INVERSE IfcMaterialDefinitionRepresentation::RepresentedMaterial
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialClassificationRelationship> > ClassifiedAs(); // INVERSE IfcMaterialClassificationRelationship::ClassifiedMaterial
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterial (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterial> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterial> > list;
    typedef IfcTemplatedEntityList<IfcMaterial>::it it;
};
class IfcMaterialClassificationRelationship : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > MaterialClassifications();
    SHARED_PTR<IfcMaterial> ClassifiedMaterial();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterialClassificationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterialClassificationRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialClassificationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcMaterialClassificationRelationship>::it it;
};
class IfcMaterialLayer : public IfcBaseClass {
public:
    bool hasMaterial();
    SHARED_PTR<IfcMaterial> Material();
    IfcPositiveLengthMeasure LayerThickness();
    bool hasIsVentilated();
    IfcLogical IsVentilated();
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayerSet> > ToMaterialLayerSet(); // INVERSE IfcMaterialLayerSet::MaterialLayers
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterialLayer (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterialLayer> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayer> > list;
    typedef IfcTemplatedEntityList<IfcMaterialLayer>::it it;
};
class IfcMaterialLayerSet : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayer> > MaterialLayers();
    bool hasLayerSetName();
    IfcLabel LayerSetName();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterialLayerSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterialLayerSet> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayerSet> > list;
    typedef IfcTemplatedEntityList<IfcMaterialLayerSet>::it it;
};
class IfcMaterialLayerSetUsage : public IfcBaseClass {
public:
    SHARED_PTR<IfcMaterialLayerSet> ForLayerSet();
    IfcLayerSetDirectionEnum::IfcLayerSetDirectionEnum LayerSetDirection();
    IfcDirectionSenseEnum::IfcDirectionSenseEnum DirectionSense();
    IfcLengthMeasure OffsetFromReferenceLine();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterialLayerSetUsage (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterialLayerSetUsage> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayerSetUsage> > list;
    typedef IfcTemplatedEntityList<IfcMaterialLayerSetUsage>::it it;
};
class IfcMaterialList : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcMaterial> > Materials();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterialList (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterialList> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialList> > list;
    typedef IfcTemplatedEntityList<IfcMaterialList>::it it;
};
class IfcMaterialProperties : public IfcBaseClass {
public:
    SHARED_PTR<IfcMaterial> Material();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterialProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcMaterialProperties>::it it;
};
class IfcMeasureWithUnit : public IfcBaseClass {
public:
    IfcValue ValueComponent();
    IfcUnit UnitComponent();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMeasureWithUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMeasureWithUnit> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMechanicalMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMechanicalMaterialProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMechanicalSteelMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMechanicalSteelMaterialProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalSteelMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalSteelMaterialProperties>::it it;
};
class IfcMetric : public IfcConstraint {
public:
    IfcBenchmarkEnum::IfcBenchmarkEnum Benchmark();
    bool hasValueSource();
    IfcLabel ValueSource();
    IfcMetricValueSelect DataValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMetric (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMetric> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMetric> > list;
    typedef IfcTemplatedEntityList<IfcMetric>::it it;
};
class IfcMonetaryUnit : public IfcBaseClass {
public:
    IfcCurrencyEnum::IfcCurrencyEnum Currency();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMonetaryUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMonetaryUnit> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMonetaryUnit> > list;
    typedef IfcTemplatedEntityList<IfcMonetaryUnit>::it it;
};
class IfcNamedUnit : public IfcBaseClass {
public:
    SHARED_PTR<IfcDimensionalExponents> Dimensions();
    IfcUnitEnum::IfcUnitEnum UnitType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcNamedUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcNamedUnit> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcNamedUnit> > list;
    typedef IfcTemplatedEntityList<IfcNamedUnit>::it it;
};
class IfcObjectPlacement : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > PlacesObject(); // INVERSE IfcProduct::ObjectPlacement
    SHARED_PTR< IfcTemplatedEntityList<IfcLocalPlacement> > ReferencedByPlacements(); // INVERSE IfcLocalPlacement::PlacementRelTo
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcObjectPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcObjectPlacement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcObjectPlacement> > list;
    typedef IfcTemplatedEntityList<IfcObjectPlacement>::it it;
};
class IfcObjective : public IfcConstraint {
public:
    bool hasBenchmarkValues();
    SHARED_PTR<IfcMetric> BenchmarkValues();
    bool hasResultValues();
    SHARED_PTR<IfcMetric> ResultValues();
    IfcObjectiveEnum::IfcObjectiveEnum ObjectiveQualifier();
    bool hasUserDefinedQualifier();
    IfcLabel UserDefinedQualifier();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcObjective (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcObjective> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOpticalMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOpticalMaterialProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOrganization (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOrganization> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrganization> > list;
    typedef IfcTemplatedEntityList<IfcOrganization>::it it;
};
class IfcOrganizationRelationship : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR<IfcOrganization> RelatingOrganization();
    SHARED_PTR< IfcTemplatedEntityList<IfcOrganization> > RelatedOrganizations();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOrganizationRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOrganizationRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrganizationRelationship> > list;
    typedef IfcTemplatedEntityList<IfcOrganizationRelationship>::it it;
};
class IfcOwnerHistory : public IfcBaseClass {
public:
    SHARED_PTR<IfcPersonAndOrganization> OwningUser();
    SHARED_PTR<IfcApplication> OwningApplication();
    bool hasState();
    IfcStateEnum::IfcStateEnum State();
    IfcChangeActionEnum::IfcChangeActionEnum ChangeAction();
    bool hasLastModifiedDate();
    IfcTimeStamp LastModifiedDate();
    bool hasLastModifyingUser();
    SHARED_PTR<IfcPersonAndOrganization> LastModifyingUser();
    bool hasLastModifyingApplication();
    SHARED_PTR<IfcApplication> LastModifyingApplication();
    IfcTimeStamp CreationDate();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOwnerHistory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOwnerHistory> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPerson (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPerson> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > list;
    typedef IfcTemplatedEntityList<IfcPerson>::it it;
};
class IfcPersonAndOrganization : public IfcBaseClass {
public:
    SHARED_PTR<IfcPerson> ThePerson();
    SHARED_PTR<IfcOrganization> TheOrganization();
    bool hasRoles();
    SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > Roles();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPersonAndOrganization (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPersonAndOrganization> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPersonAndOrganization> > list;
    typedef IfcTemplatedEntityList<IfcPersonAndOrganization>::it it;
};
class IfcPhysicalQuantity : public IfcBaseClass {
public:
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalComplexQuantity> > PartOfComplex(); // INVERSE IfcPhysicalComplexQuantity::HasQuantities
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPhysicalQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPhysicalQuantity> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > list;
    typedef IfcTemplatedEntityList<IfcPhysicalQuantity>::it it;
};
class IfcPhysicalSimpleQuantity : public IfcPhysicalQuantity {
public:
    bool hasUnit();
    SHARED_PTR<IfcNamedUnit> Unit();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPhysicalSimpleQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPhysicalSimpleQuantity> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPostalAddress (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPostalAddress> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPostalAddress> > list;
    typedef IfcTemplatedEntityList<IfcPostalAddress>::it it;
};
class IfcPreDefinedItem : public IfcBaseClass {
public:
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedItem> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedItem>::it it;
};
class IfcPreDefinedSymbol : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedSymbol> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedSymbol>::it it;
};
class IfcPreDefinedTerminatorSymbol : public IfcPreDefinedSymbol {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedTerminatorSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedTerminatorSymbol> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedTerminatorSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedTerminatorSymbol>::it it;
};
class IfcPreDefinedTextFont : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedTextFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedTextFont> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPresentationLayerAssignment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPresentationLayerAssignment> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerAssignment> > list;
    typedef IfcTemplatedEntityList<IfcPresentationLayerAssignment>::it it;
};
class IfcPresentationLayerWithStyle : public IfcPresentationLayerAssignment {
public:
    bool LayerOn();
    bool LayerFrozen();
    bool LayerBlocked();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > LayerStyles();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPresentationLayerWithStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPresentationLayerWithStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerWithStyle> > list;
    typedef IfcTemplatedEntityList<IfcPresentationLayerWithStyle>::it it;
};
class IfcPresentationStyle : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPresentationStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPresentationStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPresentationStyle> > list;
    typedef IfcTemplatedEntityList<IfcPresentationStyle>::it it;
};
class IfcPresentationStyleAssignment : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Styles();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPresentationStyleAssignment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPresentationStyleAssignment> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProductRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProductRepresentation> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProductsOfCombustionProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProductsOfCombustionProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProductsOfCombustionProperties> > list;
    typedef IfcTemplatedEntityList<IfcProductsOfCombustionProperties>::it it;
};
class IfcProfileDef : public IfcBaseClass {
public:
    IfcProfileTypeEnum::IfcProfileTypeEnum ProfileType();
    bool hasProfileName();
    IfcLabel ProfileName();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcProfileDef>::it it;
};
class IfcProfileProperties : public IfcBaseClass {
public:
    bool hasProfileName();
    IfcLabel ProfileName();
    bool hasProfileDefinition();
    SHARED_PTR<IfcProfileDef> ProfileDefinition();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProfileProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProperty (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProperty> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > list;
    typedef IfcTemplatedEntityList<IfcProperty>::it it;
};
class IfcPropertyConstraintRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcConstraint> RelatingConstraint();
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > RelatedProperties();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyConstraintRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyConstraintRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyConstraintRelationship> > list;
    typedef IfcTemplatedEntityList<IfcPropertyConstraintRelationship>::it it;
};
class IfcPropertyDependencyRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcProperty> DependingProperty();
    SHARED_PTR<IfcProperty> DependantProperty();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool hasExpression();
    IfcText Expression();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyDependencyRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyDependencyRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyDependencyRelationship> > list;
    typedef IfcTemplatedEntityList<IfcPropertyDependencyRelationship>::it it;
};
class IfcPropertyEnumeration : public IfcBaseClass {
public:
    IfcLabel Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > EnumerationValues();
    bool hasUnit();
    IfcUnit Unit();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyEnumeration (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyEnumeration> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyEnumeration> > list;
    typedef IfcTemplatedEntityList<IfcPropertyEnumeration>::it it;
};
class IfcQuantityArea : public IfcPhysicalSimpleQuantity {
public:
    IfcAreaMeasure AreaValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcQuantityArea (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcQuantityArea> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityArea> > list;
    typedef IfcTemplatedEntityList<IfcQuantityArea>::it it;
};
class IfcQuantityCount : public IfcPhysicalSimpleQuantity {
public:
    IfcCountMeasure CountValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcQuantityCount (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcQuantityCount> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityCount> > list;
    typedef IfcTemplatedEntityList<IfcQuantityCount>::it it;
};
class IfcQuantityLength : public IfcPhysicalSimpleQuantity {
public:
    IfcLengthMeasure LengthValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcQuantityLength (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcQuantityLength> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityLength> > list;
    typedef IfcTemplatedEntityList<IfcQuantityLength>::it it;
};
class IfcQuantityTime : public IfcPhysicalSimpleQuantity {
public:
    IfcTimeMeasure TimeValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcQuantityTime (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcQuantityTime> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityTime> > list;
    typedef IfcTemplatedEntityList<IfcQuantityTime>::it it;
};
class IfcQuantityVolume : public IfcPhysicalSimpleQuantity {
public:
    IfcVolumeMeasure VolumeValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcQuantityVolume (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcQuantityVolume> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcQuantityVolume> > list;
    typedef IfcTemplatedEntityList<IfcQuantityVolume>::it it;
};
class IfcQuantityWeight : public IfcPhysicalSimpleQuantity {
public:
    IfcMassMeasure WeightValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcQuantityWeight (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcQuantityWeight> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcReferencesValueDocument (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcReferencesValueDocument> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcReinforcementBarProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcReinforcementBarProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementBarProperties> > list;
    typedef IfcTemplatedEntityList<IfcReinforcementBarProperties>::it it;
};
class IfcRelaxation : public IfcBaseClass {
public:
    IfcNormalisedRatioMeasure RelaxationValue();
    IfcNormalisedRatioMeasure InitialStress();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelaxation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelaxation> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelaxation> > list;
    typedef IfcTemplatedEntityList<IfcRelaxation>::it it;
};
class IfcRepresentation : public IfcBaseClass {
public:
    SHARED_PTR<IfcRepresentationContext> ContextOfItems();
    bool hasRepresentationIdentifier();
    IfcLabel RepresentationIdentifier();
    bool hasRepresentationType();
    IfcLabel RepresentationType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationItem> > Items();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationMap> > RepresentationMap(); // INVERSE IfcRepresentationMap::MappedRepresentation
    SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerAssignment> > LayerAssignments(); // INVERSE IfcPresentationLayerAssignment::AssignedItems
    SHARED_PTR< IfcTemplatedEntityList<IfcProductRepresentation> > OfProductRepresentation(); // INVERSE IfcProductRepresentation::Representations
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRepresentation> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRepresentationContext (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRepresentationContext> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationContext> > list;
    typedef IfcTemplatedEntityList<IfcRepresentationContext>::it it;
};
class IfcRepresentationItem : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcPresentationLayerAssignment> > LayerAssignments(); // INVERSE IfcPresentationLayerAssignment::AssignedItems
    SHARED_PTR< IfcTemplatedEntityList<IfcStyledItem> > StyledByItem(); // INVERSE IfcStyledItem::Item
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRepresentationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRepresentationItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationItem> > list;
    typedef IfcTemplatedEntityList<IfcRepresentationItem>::it it;
};
class IfcRepresentationMap : public IfcBaseClass {
public:
    IfcAxis2Placement MappingOrigin();
    SHARED_PTR<IfcRepresentation> MappedRepresentation();
    SHARED_PTR< IfcTemplatedEntityList<IfcMappedItem> > MapUsage(); // INVERSE IfcMappedItem::MappingSource
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRepresentationMap (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRepresentationMap> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRibPlateProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRibPlateProfileProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRibPlateProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcRibPlateProfileProperties>::it it;
};
class IfcRoot : public IfcBaseClass {
public:
    IfcGloballyUniqueId GlobalId();
    SHARED_PTR<IfcOwnerHistory> OwnerHistory();
    bool hasName();
    IfcLabel Name();
    bool hasDescription();
    IfcText Description();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRoot (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRoot> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoot> > list;
    typedef IfcTemplatedEntityList<IfcRoot>::it it;
};
class IfcSIUnit : public IfcNamedUnit {
public:
    bool hasPrefix();
    IfcSIPrefix::IfcSIPrefix Prefix();
    IfcSIUnitName::IfcSIUnitName Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSIUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSIUnit> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSIUnit> > list;
    typedef IfcTemplatedEntityList<IfcSIUnit>::it it;
};
class IfcSectionProperties : public IfcBaseClass {
public:
    IfcSectionTypeEnum::IfcSectionTypeEnum SectionType();
    SHARED_PTR<IfcProfileDef> StartProfile();
    bool hasEndProfile();
    SHARED_PTR<IfcProfileDef> EndProfile();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSectionProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSectionProperties> ptr;
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
    SHARED_PTR<IfcSectionProperties> SectionDefinition();
    SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementBarProperties> > CrossSectionReinforcementDefinitions();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSectionReinforcementProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSectionReinforcementProperties> ptr;
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
    SHARED_PTR<IfcProductDefinitionShape> PartOfProductDefinitionShape();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcShapeAspect (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcShapeAspect> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcShapeAspect> > list;
    typedef IfcTemplatedEntityList<IfcShapeAspect>::it it;
};
class IfcShapeModel : public IfcRepresentation {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcShapeAspect> > OfShapeAspect(); // INVERSE IfcShapeAspect::ShapeRepresentations
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcShapeModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcShapeModel> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcShapeModel> > list;
    typedef IfcTemplatedEntityList<IfcShapeModel>::it it;
};
class IfcShapeRepresentation : public IfcShapeModel {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcShapeRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcShapeRepresentation> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcShapeRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcShapeRepresentation>::it it;
};
class IfcSimpleProperty : public IfcProperty {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSimpleProperty (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSimpleProperty> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSimpleProperty> > list;
    typedef IfcTemplatedEntityList<IfcSimpleProperty>::it it;
};
class IfcStructuralConnectionCondition : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralConnectionCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralConnectionCondition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralConnectionCondition> > list;
    typedef IfcTemplatedEntityList<IfcStructuralConnectionCondition>::it it;
};
class IfcStructuralLoad : public IfcBaseClass {
public:
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoad (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoad> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoad>::it it;
};
class IfcStructuralLoadStatic : public IfcStructuralLoad {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadStatic (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadStatic> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadTemperature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadTemperature> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadTemperature> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadTemperature>::it it;
};
class IfcStyleModel : public IfcRepresentation {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStyleModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStyleModel> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStyleModel> > list;
    typedef IfcTemplatedEntityList<IfcStyleModel>::it it;
};
class IfcStyledItem : public IfcRepresentationItem {
public:
    bool hasItem();
    SHARED_PTR<IfcRepresentationItem> Item();
    SHARED_PTR< IfcTemplatedEntityList<IfcPresentationStyleAssignment> > Styles();
    bool hasName();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStyledItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStyledItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStyledItem> > list;
    typedef IfcTemplatedEntityList<IfcStyledItem>::it it;
};
class IfcStyledRepresentation : public IfcStyleModel {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStyledRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStyledRepresentation> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStyledRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcStyledRepresentation>::it it;
};
class IfcSurfaceStyle : public IfcPresentationStyle {
public:
    IfcSurfaceSide::IfcSurfaceSide Side();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Styles();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyle> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyle>::it it;
};
class IfcSurfaceStyleLighting : public IfcBaseClass {
public:
    SHARED_PTR<IfcColourRgb> DiffuseTransmissionColour();
    SHARED_PTR<IfcColourRgb> DiffuseReflectionColour();
    SHARED_PTR<IfcColourRgb> TransmissionColour();
    SHARED_PTR<IfcColourRgb> ReflectanceColour();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceStyleLighting (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceStyleLighting> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleLighting> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleLighting>::it it;
};
class IfcSurfaceStyleRefraction : public IfcBaseClass {
public:
    bool hasRefractionIndex();
    IfcReal RefractionIndex();
    bool hasDispersionFactor();
    IfcReal DispersionFactor();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceStyleRefraction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceStyleRefraction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleRefraction> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleRefraction>::it it;
};
class IfcSurfaceStyleShading : public IfcBaseClass {
public:
    SHARED_PTR<IfcColourRgb> SurfaceColour();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceStyleShading (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceStyleShading> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleShading> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleShading>::it it;
};
class IfcSurfaceStyleWithTextures : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceTexture> > Textures();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceStyleWithTextures (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceStyleWithTextures> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleWithTextures> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleWithTextures>::it it;
};
class IfcSurfaceTexture : public IfcBaseClass {
public:
    bool RepeatS();
    bool RepeatT();
    IfcSurfaceTextureEnum::IfcSurfaceTextureEnum TextureType();
    bool hasTextureTransform();
    SHARED_PTR<IfcCartesianTransformationOperator2D> TextureTransform();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceTexture> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceTexture> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceTexture>::it it;
};
class IfcSymbolStyle : public IfcPresentationStyle {
public:
    IfcSymbolStyleSelect StyleOfSymbol();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSymbolStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSymbolStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSymbolStyle> > list;
    typedef IfcTemplatedEntityList<IfcSymbolStyle>::it it;
};
class IfcTable : public IfcBaseClass {
public:
    std::string Name();
    SHARED_PTR< IfcTemplatedEntityList<IfcTableRow> > Rows();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTable (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTable> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTable> > list;
    typedef IfcTemplatedEntityList<IfcTable>::it it;
};
class IfcTableRow : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > RowCells();
    bool IsHeading();
    SHARED_PTR< IfcTemplatedEntityList<IfcTable> > OfTable(); // INVERSE IfcTable::Rows
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTableRow (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTableRow> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTelecomAddress (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTelecomAddress> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextStyle> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextStyleFontModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextStyleFontModel> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextStyleFontModel> > list;
    typedef IfcTemplatedEntityList<IfcTextStyleFontModel>::it it;
};
class IfcTextStyleForDefinedFont : public IfcBaseClass {
public:
    IfcColour Colour();
    bool hasBackgroundColour();
    IfcColour BackgroundColour();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextStyleForDefinedFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextStyleForDefinedFont> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextStyleTextModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextStyleTextModel> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextStyleWithBoxCharacteristics (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextStyleWithBoxCharacteristics> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextStyleWithBoxCharacteristics> > list;
    typedef IfcTemplatedEntityList<IfcTextStyleWithBoxCharacteristics>::it it;
};
class IfcTextureCoordinate : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSurface> > AnnotatedSurface(); // INVERSE IfcAnnotationSurface::TextureCoordinates
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextureCoordinate (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextureCoordinate> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextureCoordinate> > list;
    typedef IfcTemplatedEntityList<IfcTextureCoordinate>::it it;
};
class IfcTextureCoordinateGenerator : public IfcTextureCoordinate {
public:
    IfcLabel Mode();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Parameter();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextureCoordinateGenerator (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextureCoordinateGenerator> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextureCoordinateGenerator> > list;
    typedef IfcTemplatedEntityList<IfcTextureCoordinateGenerator>::it it;
};
class IfcTextureMap : public IfcTextureCoordinate {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcVertexBasedTextureMap> > TextureMaps();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextureMap (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextureMap> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextureMap> > list;
    typedef IfcTemplatedEntityList<IfcTextureMap>::it it;
};
class IfcTextureVertex : public IfcBaseClass {
public:
    std::vector<IfcParameterValue> /*[2:2]*/ Coordinates();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextureVertex (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextureVertex> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcThermalMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcThermalMaterialProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTimeSeries (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTimeSeries> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeries> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeries>::it it;
};
class IfcTimeSeriesReferenceRelationship : public IfcBaseClass {
public:
    SHARED_PTR<IfcTimeSeries> ReferencedTimeSeries();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > TimeSeriesReferences();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTimeSeriesReferenceRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTimeSeriesReferenceRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesReferenceRelationship> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeriesReferenceRelationship>::it it;
};
class IfcTimeSeriesValue : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ListValues();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTimeSeriesValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTimeSeriesValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesValue> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeriesValue>::it it;
};
class IfcTopologicalRepresentationItem : public IfcRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTopologicalRepresentationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTopologicalRepresentationItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTopologicalRepresentationItem> > list;
    typedef IfcTemplatedEntityList<IfcTopologicalRepresentationItem>::it it;
};
class IfcTopologyRepresentation : public IfcShapeModel {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTopologyRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTopologyRepresentation> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTopologyRepresentation> > list;
    typedef IfcTemplatedEntityList<IfcTopologyRepresentation>::it it;
};
class IfcUnitAssignment : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Units();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcUnitAssignment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcUnitAssignment> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcUnitAssignment> > list;
    typedef IfcTemplatedEntityList<IfcUnitAssignment>::it it;
};
class IfcVertex : public IfcTopologicalRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVertex (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVertex> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVertex> > list;
    typedef IfcTemplatedEntityList<IfcVertex>::it it;
};
class IfcVertexBasedTextureMap : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcTextureVertex> > TextureVertices();
    SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > TexturePoints();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVertexBasedTextureMap (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVertexBasedTextureMap> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVertexBasedTextureMap> > list;
    typedef IfcTemplatedEntityList<IfcVertexBasedTextureMap>::it it;
};
class IfcVertexPoint : public IfcVertex {
public:
    SHARED_PTR<IfcPoint> VertexGeometry();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVertexPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVertexPoint> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVertexPoint> > list;
    typedef IfcTemplatedEntityList<IfcVertexPoint>::it it;
};
class IfcVirtualGridIntersection : public IfcBaseClass {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IntersectingAxes();
    std::vector<IfcLengthMeasure> /*[2:3]*/ OffsetDistances();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVirtualGridIntersection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVirtualGridIntersection> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWaterProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWaterProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWaterProperties> > list;
    typedef IfcTemplatedEntityList<IfcWaterProperties>::it it;
};
class IfcAnnotationOccurrence : public IfcStyledItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationOccurrence> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationOccurrence>::it it;
};
class IfcAnnotationSurfaceOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationSurfaceOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationSurfaceOccurrence> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSurfaceOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationSurfaceOccurrence>::it it;
};
class IfcAnnotationSymbolOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationSymbolOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationSymbolOccurrence> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSymbolOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationSymbolOccurrence>::it it;
};
class IfcAnnotationTextOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationTextOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationTextOccurrence> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationTextOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationTextOccurrence>::it it;
};
class IfcArbitraryClosedProfileDef : public IfcProfileDef {
public:
    SHARED_PTR<IfcCurve> OuterCurve();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcArbitraryClosedProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcArbitraryClosedProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcArbitraryClosedProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcArbitraryClosedProfileDef>::it it;
};
class IfcArbitraryOpenProfileDef : public IfcProfileDef {
public:
    SHARED_PTR<IfcBoundedCurve> Curve();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcArbitraryOpenProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcArbitraryOpenProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcArbitraryOpenProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcArbitraryOpenProfileDef>::it it;
};
class IfcArbitraryProfileDefWithVoids : public IfcArbitraryClosedProfileDef {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > InnerCurves();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcArbitraryProfileDefWithVoids (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcArbitraryProfileDefWithVoids> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcArbitraryProfileDefWithVoids> > list;
    typedef IfcTemplatedEntityList<IfcArbitraryProfileDefWithVoids>::it it;
};
class IfcBlobTexture : public IfcSurfaceTexture {
public:
    IfcIdentifier RasterFormat();
    bool RasterCode();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBlobTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBlobTexture> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBlobTexture> > list;
    typedef IfcTemplatedEntityList<IfcBlobTexture>::it it;
};
class IfcCenterLineProfileDef : public IfcArbitraryOpenProfileDef {
public:
    IfcPositiveLengthMeasure Thickness();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCenterLineProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCenterLineProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCenterLineProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCenterLineProfileDef>::it it;
};
class IfcClassificationReference : public IfcExternalReference {
public:
    bool hasReferencedSource();
    SHARED_PTR<IfcClassification> ReferencedSource();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcClassificationReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcClassificationReference> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClassificationReference> > list;
    typedef IfcTemplatedEntityList<IfcClassificationReference>::it it;
};
class IfcColourRgb : public IfcColourSpecification {
public:
    IfcNormalisedRatioMeasure Red();
    IfcNormalisedRatioMeasure Green();
    IfcNormalisedRatioMeasure Blue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcColourRgb (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcColourRgb> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColourRgb> > list;
    typedef IfcTemplatedEntityList<IfcColourRgb>::it it;
};
class IfcComplexProperty : public IfcProperty {
public:
    IfcIdentifier UsageName();
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > HasProperties();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcComplexProperty (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcComplexProperty> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcComplexProperty> > list;
    typedef IfcTemplatedEntityList<IfcComplexProperty>::it it;
};
class IfcCompositeProfileDef : public IfcProfileDef {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > Profiles();
    bool hasLabel();
    IfcLabel Label();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCompositeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCompositeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCompositeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCompositeProfileDef>::it it;
};
class IfcConnectedFaceSet : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcFace> > CfsFaces();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConnectedFaceSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConnectedFaceSet> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectedFaceSet> > list;
    typedef IfcTemplatedEntityList<IfcConnectedFaceSet>::it it;
};
class IfcConnectionCurveGeometry : public IfcConnectionGeometry {
public:
    IfcCurveOrEdgeCurve CurveOnRelatingElement();
    bool hasCurveOnRelatedElement();
    IfcCurveOrEdgeCurve CurveOnRelatedElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConnectionCurveGeometry (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConnectionCurveGeometry> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConnectionPointEccentricity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConnectionPointEccentricity> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConnectionPointEccentricity> > list;
    typedef IfcTemplatedEntityList<IfcConnectionPointEccentricity>::it it;
};
class IfcContextDependentUnit : public IfcNamedUnit {
public:
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcContextDependentUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcContextDependentUnit> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcContextDependentUnit> > list;
    typedef IfcTemplatedEntityList<IfcContextDependentUnit>::it it;
};
class IfcConversionBasedUnit : public IfcNamedUnit {
public:
    IfcLabel Name();
    SHARED_PTR<IfcMeasureWithUnit> ConversionFactor();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConversionBasedUnit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConversionBasedUnit> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurveStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurveStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyle> > list;
    typedef IfcTemplatedEntityList<IfcCurveStyle>::it it;
};
class IfcDerivedProfileDef : public IfcProfileDef {
public:
    SHARED_PTR<IfcProfileDef> ParentProfile();
    SHARED_PTR<IfcCartesianTransformationOperator2D> Operator();
    bool hasLabel();
    IfcLabel Label();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDerivedProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDerivedProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDerivedProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcDerivedProfileDef>::it it;
};
class IfcDimensionCalloutRelationship : public IfcDraughtingCalloutRelationship {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDimensionCalloutRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDimensionCalloutRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCalloutRelationship> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCalloutRelationship>::it it;
};
class IfcDimensionPair : public IfcDraughtingCalloutRelationship {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDimensionPair (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDimensionPair> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionPair> > list;
    typedef IfcTemplatedEntityList<IfcDimensionPair>::it it;
};
class IfcDocumentReference : public IfcExternalReference {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > ReferenceToDocument(); // INVERSE IfcDocumentInformation::DocumentReferences
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDocumentReference (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDocumentReference> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDocumentReference> > list;
    typedef IfcTemplatedEntityList<IfcDocumentReference>::it it;
};
class IfcDraughtingPreDefinedTextFont : public IfcPreDefinedTextFont {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDraughtingPreDefinedTextFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDraughtingPreDefinedTextFont> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingPreDefinedTextFont> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingPreDefinedTextFont>::it it;
};
class IfcEdge : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR<IfcVertex> EdgeStart();
    SHARED_PTR<IfcVertex> EdgeEnd();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEdge (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEdge> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdge> > list;
    typedef IfcTemplatedEntityList<IfcEdge>::it it;
};
class IfcEdgeCurve : public IfcEdge {
public:
    SHARED_PTR<IfcCurve> EdgeGeometry();
    bool SameSense();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEdgeCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEdgeCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdgeCurve> > list;
    typedef IfcTemplatedEntityList<IfcEdgeCurve>::it it;
};
class IfcExtendedMaterialProperties : public IfcMaterialProperties {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > ExtendedProperties();
    bool hasDescription();
    IfcText Description();
    IfcLabel Name();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcExtendedMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcExtendedMaterialProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExtendedMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcExtendedMaterialProperties>::it it;
};
class IfcFace : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcFaceBound> > Bounds();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFace> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFace> > list;
    typedef IfcTemplatedEntityList<IfcFace>::it it;
};
class IfcFaceBound : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR<IfcLoop> Bound();
    bool Orientation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFaceBound (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFaceBound> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFaceBound> > list;
    typedef IfcTemplatedEntityList<IfcFaceBound>::it it;
};
class IfcFaceOuterBound : public IfcFaceBound {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFaceOuterBound (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFaceOuterBound> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFaceOuterBound> > list;
    typedef IfcTemplatedEntityList<IfcFaceOuterBound>::it it;
};
class IfcFaceSurface : public IfcFace {
public:
    SHARED_PTR<IfcSurface> FaceSurface();
    bool SameSense();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFaceSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFaceSurface> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFailureConnectionCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFailureConnectionCondition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFailureConnectionCondition> > list;
    typedef IfcTemplatedEntityList<IfcFailureConnectionCondition>::it it;
};
class IfcFillAreaStyle : public IfcPresentationStyle {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > FillStyles();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFillAreaStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFillAreaStyle> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFuelProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFuelProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGeneralMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGeneralMaterialProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGeneralProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGeneralProfileProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeneralProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcGeneralProfileProperties>::it it;
};
class IfcGeometricRepresentationContext : public IfcRepresentationContext {
public:
    IfcDimensionCount CoordinateSpaceDimension();
    bool hasPrecision();
    float Precision();
    IfcAxis2Placement WorldCoordinateSystem();
    bool hasTrueNorth();
    SHARED_PTR<IfcDirection> TrueNorth();
    SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationSubContext> > HasSubContexts(); // INVERSE IfcGeometricRepresentationSubContext::ParentContext
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGeometricRepresentationContext (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGeometricRepresentationContext> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationContext> > list;
    typedef IfcTemplatedEntityList<IfcGeometricRepresentationContext>::it it;
};
class IfcGeometricRepresentationItem : public IfcRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGeometricRepresentationItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGeometricRepresentationItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationItem> > list;
    typedef IfcTemplatedEntityList<IfcGeometricRepresentationItem>::it it;
};
class IfcGeometricRepresentationSubContext : public IfcGeometricRepresentationContext {
public:
    SHARED_PTR<IfcGeometricRepresentationContext> ParentContext();
    bool hasTargetScale();
    IfcPositiveRatioMeasure TargetScale();
    IfcGeometricProjectionEnum::IfcGeometricProjectionEnum TargetView();
    bool hasUserDefinedTargetView();
    IfcLabel UserDefinedTargetView();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGeometricRepresentationSubContext (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGeometricRepresentationSubContext> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricRepresentationSubContext> > list;
    typedef IfcTemplatedEntityList<IfcGeometricRepresentationSubContext>::it it;
};
class IfcGeometricSet : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Elements();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGeometricSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGeometricSet> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGeometricSet> > list;
    typedef IfcTemplatedEntityList<IfcGeometricSet>::it it;
};
class IfcGridPlacement : public IfcObjectPlacement {
public:
    SHARED_PTR<IfcVirtualGridIntersection> PlacementLocation();
    bool hasPlacementRefDirection();
    SHARED_PTR<IfcVirtualGridIntersection> PlacementRefDirection();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGridPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGridPlacement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGridPlacement> > list;
    typedef IfcTemplatedEntityList<IfcGridPlacement>::it it;
};
class IfcHalfSpaceSolid : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcSurface> BaseSurface();
    bool AgreementFlag();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcHalfSpaceSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcHalfSpaceSolid> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcHygroscopicMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcHygroscopicMaterialProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcHygroscopicMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcHygroscopicMaterialProperties>::it it;
};
class IfcImageTexture : public IfcSurfaceTexture {
public:
    IfcIdentifier UrlReference();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcImageTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcImageTexture> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcImageTexture> > list;
    typedef IfcTemplatedEntityList<IfcImageTexture>::it it;
};
class IfcIrregularTimeSeries : public IfcTimeSeries {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeriesValue> > Values();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcIrregularTimeSeries (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcIrregularTimeSeries> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeries> > list;
    typedef IfcTemplatedEntityList<IfcIrregularTimeSeries>::it it;
};
class IfcLightSource : public IfcGeometricRepresentationItem {
public:
    bool hasName();
    IfcLabel Name();
    SHARED_PTR<IfcColourRgb> LightColour();
    bool hasAmbientIntensity();
    IfcNormalisedRatioMeasure AmbientIntensity();
    bool hasIntensity();
    IfcNormalisedRatioMeasure Intensity();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightSource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightSource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSource> > list;
    typedef IfcTemplatedEntityList<IfcLightSource>::it it;
};
class IfcLightSourceAmbient : public IfcLightSource {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightSourceAmbient (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightSourceAmbient> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceAmbient> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceAmbient>::it it;
};
class IfcLightSourceDirectional : public IfcLightSource {
public:
    SHARED_PTR<IfcDirection> Orientation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightSourceDirectional (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightSourceDirectional> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceDirectional> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceDirectional>::it it;
};
class IfcLightSourceGoniometric : public IfcLightSource {
public:
    SHARED_PTR<IfcAxis2Placement3D> Position();
    bool hasColourAppearance();
    SHARED_PTR<IfcColourRgb> ColourAppearance();
    IfcThermodynamicTemperatureMeasure ColourTemperature();
    IfcLuminousFluxMeasure LuminousFlux();
    IfcLightEmissionSourceEnum::IfcLightEmissionSourceEnum LightEmissionSource();
    IfcLightDistributionDataSourceSelect LightDistributionDataSource();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightSourceGoniometric (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightSourceGoniometric> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceGoniometric> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceGoniometric>::it it;
};
class IfcLightSourcePositional : public IfcLightSource {
public:
    SHARED_PTR<IfcCartesianPoint> Position();
    IfcPositiveLengthMeasure Radius();
    IfcReal ConstantAttenuation();
    IfcReal DistanceAttenuation();
    IfcReal QuadricAttenuation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightSourcePositional (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightSourcePositional> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourcePositional> > list;
    typedef IfcTemplatedEntityList<IfcLightSourcePositional>::it it;
};
class IfcLightSourceSpot : public IfcLightSourcePositional {
public:
    SHARED_PTR<IfcDirection> Orientation();
    bool hasConcentrationExponent();
    IfcReal ConcentrationExponent();
    IfcPositivePlaneAngleMeasure SpreadAngle();
    IfcPositivePlaneAngleMeasure BeamWidthAngle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightSourceSpot (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightSourceSpot> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightSourceSpot> > list;
    typedef IfcTemplatedEntityList<IfcLightSourceSpot>::it it;
};
class IfcLocalPlacement : public IfcObjectPlacement {
public:
    bool hasPlacementRelTo();
    SHARED_PTR<IfcObjectPlacement> PlacementRelTo();
    IfcAxis2Placement RelativePlacement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLocalPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLocalPlacement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLocalPlacement> > list;
    typedef IfcTemplatedEntityList<IfcLocalPlacement>::it it;
};
class IfcLoop : public IfcTopologicalRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLoop> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLoop> > list;
    typedef IfcTemplatedEntityList<IfcLoop>::it it;
};
class IfcMappedItem : public IfcRepresentationItem {
public:
    SHARED_PTR<IfcRepresentationMap> MappingSource();
    SHARED_PTR<IfcCartesianTransformationOperator> MappingTarget();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMappedItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMappedItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMappedItem> > list;
    typedef IfcTemplatedEntityList<IfcMappedItem>::it it;
};
class IfcMaterialDefinitionRepresentation : public IfcProductRepresentation {
public:
    SHARED_PTR<IfcMaterial> RepresentedMaterial();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMaterialDefinitionRepresentation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMaterialDefinitionRepresentation> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMechanicalConcreteMaterialProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMechanicalConcreteMaterialProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalConcreteMaterialProperties> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalConcreteMaterialProperties>::it it;
};
class IfcObjectDefinition : public IfcRoot {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssigns> > HasAssignments(); // INVERSE IfcRelAssigns::RelatedObjects
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDecomposes> > IsDecomposedBy(); // INVERSE IfcRelDecomposes::RelatingObject
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDecomposes> > Decomposes(); // INVERSE IfcRelDecomposes::RelatedObjects
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociates> > HasAssociations(); // INVERSE IfcRelAssociates::RelatedObjects
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcObjectDefinition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcObjectDefinition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > list;
    typedef IfcTemplatedEntityList<IfcObjectDefinition>::it it;
};
class IfcOneDirectionRepeatFactor : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcVector> RepeatFactor();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOneDirectionRepeatFactor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOneDirectionRepeatFactor> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOneDirectionRepeatFactor> > list;
    typedef IfcTemplatedEntityList<IfcOneDirectionRepeatFactor>::it it;
};
class IfcOpenShell : public IfcConnectedFaceSet {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOpenShell (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOpenShell> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOpenShell> > list;
    typedef IfcTemplatedEntityList<IfcOpenShell>::it it;
};
class IfcOrientedEdge : public IfcEdge {
public:
    SHARED_PTR<IfcEdge> EdgeElement();
    bool Orientation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOrientedEdge (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOrientedEdge> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > list;
    typedef IfcTemplatedEntityList<IfcOrientedEdge>::it it;
};
class IfcParameterizedProfileDef : public IfcProfileDef {
public:
    SHARED_PTR<IfcAxis2Placement2D> Position();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcParameterizedProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcParameterizedProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcParameterizedProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcParameterizedProfileDef>::it it;
};
class IfcPath : public IfcTopologicalRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > EdgeList();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPath (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPath> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPhysicalComplexQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPhysicalComplexQuantity> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalComplexQuantity> > list;
    typedef IfcTemplatedEntityList<IfcPhysicalComplexQuantity>::it it;
};
class IfcPixelTexture : public IfcSurfaceTexture {
public:
    IfcInteger Width();
    IfcInteger Height();
    IfcInteger ColourComponents();
    std::vector<char[32]> /*[1:?]*/ Pixel();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPixelTexture (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPixelTexture> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPixelTexture> > list;
    typedef IfcTemplatedEntityList<IfcPixelTexture>::it it;
};
class IfcPlacement : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcCartesianPoint> Location();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPlacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPlacement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlacement> > list;
    typedef IfcTemplatedEntityList<IfcPlacement>::it it;
};
class IfcPlanarExtent : public IfcGeometricRepresentationItem {
public:
    IfcLengthMeasure SizeInX();
    IfcLengthMeasure SizeInY();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPlanarExtent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPlanarExtent> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlanarExtent> > list;
    typedef IfcTemplatedEntityList<IfcPlanarExtent>::it it;
};
class IfcPoint : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPoint> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPoint> > list;
    typedef IfcTemplatedEntityList<IfcPoint>::it it;
};
class IfcPointOnCurve : public IfcPoint {
public:
    SHARED_PTR<IfcCurve> BasisCurve();
    IfcParameterValue PointParameter();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPointOnCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPointOnCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPointOnCurve> > list;
    typedef IfcTemplatedEntityList<IfcPointOnCurve>::it it;
};
class IfcPointOnSurface : public IfcPoint {
public:
    SHARED_PTR<IfcSurface> BasisSurface();
    IfcParameterValue PointParameterU();
    IfcParameterValue PointParameterV();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPointOnSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPointOnSurface> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPointOnSurface> > list;
    typedef IfcTemplatedEntityList<IfcPointOnSurface>::it it;
};
class IfcPolyLoop : public IfcLoop {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > Polygon();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPolyLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPolyLoop> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPolyLoop> > list;
    typedef IfcTemplatedEntityList<IfcPolyLoop>::it it;
};
class IfcPolygonalBoundedHalfSpace : public IfcHalfSpaceSolid {
public:
    SHARED_PTR<IfcAxis2Placement3D> Position();
    SHARED_PTR<IfcBoundedCurve> PolygonalBoundary();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPolygonalBoundedHalfSpace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPolygonalBoundedHalfSpace> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPolygonalBoundedHalfSpace> > list;
    typedef IfcTemplatedEntityList<IfcPolygonalBoundedHalfSpace>::it it;
};
class IfcPreDefinedColour : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedColour (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedColour> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedColour> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedColour>::it it;
};
class IfcPreDefinedCurveFont : public IfcPreDefinedItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedCurveFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedCurveFont> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedCurveFont> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedCurveFont>::it it;
};
class IfcPreDefinedDimensionSymbol : public IfcPreDefinedSymbol {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedDimensionSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedDimensionSymbol> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedDimensionSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedDimensionSymbol>::it it;
};
class IfcPreDefinedPointMarkerSymbol : public IfcPreDefinedSymbol {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPreDefinedPointMarkerSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPreDefinedPointMarkerSymbol> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPreDefinedPointMarkerSymbol> > list;
    typedef IfcTemplatedEntityList<IfcPreDefinedPointMarkerSymbol>::it it;
};
class IfcProductDefinitionShape : public IfcProductRepresentation {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > ShapeOfProduct(); // INVERSE IfcProduct::Representation
    SHARED_PTR< IfcTemplatedEntityList<IfcShapeAspect> > HasShapeAspects(); // INVERSE IfcShapeAspect::PartOfProductDefinitionShape
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProductDefinitionShape (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProductDefinitionShape> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyBoundedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyBoundedValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyBoundedValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyBoundedValue>::it it;
};
class IfcPropertyDefinition : public IfcRoot {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociates> > HasAssociations(); // INVERSE IfcRelAssociates::RelatedObjects
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyDefinition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyDefinition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyDefinition> > list;
    typedef IfcTemplatedEntityList<IfcPropertyDefinition>::it it;
};
class IfcPropertyEnumeratedValue : public IfcSimpleProperty {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > EnumerationValues();
    bool hasEnumerationReference();
    SHARED_PTR<IfcPropertyEnumeration> EnumerationReference();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyEnumeratedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyEnumeratedValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyEnumeratedValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyEnumeratedValue>::it it;
};
class IfcPropertyListValue : public IfcSimpleProperty {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ListValues();
    bool hasUnit();
    IfcUnit Unit();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyListValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyListValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyListValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyListValue>::it it;
};
class IfcPropertyReferenceValue : public IfcSimpleProperty {
public:
    bool hasUsageName();
    IfcLabel UsageName();
    IfcObjectReferenceSelect PropertyReference();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyReferenceValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyReferenceValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyReferenceValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyReferenceValue>::it it;
};
class IfcPropertySetDefinition : public IfcPropertyDefinition {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDefinesByProperties> > PropertyDefinitionOf(); // INVERSE IfcRelDefinesByProperties::RelatingPropertyDefinition
    SHARED_PTR< IfcTemplatedEntityList<IfcTypeObject> > DefinesType(); // INVERSE IfcTypeObject::HasPropertySets
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertySetDefinition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertySetDefinition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertySetDefinition> > list;
    typedef IfcTemplatedEntityList<IfcPropertySetDefinition>::it it;
};
class IfcPropertySingleValue : public IfcSimpleProperty {
public:
    bool hasNominalValue();
    IfcValue NominalValue();
    bool hasUnit();
    IfcUnit Unit();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertySingleValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertySingleValue> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertyTableValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertyTableValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertyTableValue> > list;
    typedef IfcTemplatedEntityList<IfcPropertyTableValue>::it it;
};
class IfcRectangleProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure XDim();
    IfcPositiveLengthMeasure YDim();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRectangleProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRectangleProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangleProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcRectangleProfileDef>::it it;
};
class IfcRegularTimeSeries : public IfcTimeSeries {
public:
    IfcTimeMeasure TimeStep();
    SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesValue> > Values();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRegularTimeSeries (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRegularTimeSeries> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRegularTimeSeries> > list;
    typedef IfcTemplatedEntityList<IfcRegularTimeSeries>::it it;
};
class IfcReinforcementDefinitionProperties : public IfcPropertySetDefinition {
public:
    bool hasDefinitionType();
    IfcLabel DefinitionType();
    SHARED_PTR< IfcTemplatedEntityList<IfcSectionReinforcementProperties> > ReinforcementSectionDefinitions();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcReinforcementDefinitionProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcReinforcementDefinitionProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementDefinitionProperties> > list;
    typedef IfcTemplatedEntityList<IfcReinforcementDefinitionProperties>::it it;
};
class IfcRelationship : public IfcRoot {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelationship (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelationship> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelationship> > list;
    typedef IfcTemplatedEntityList<IfcRelationship>::it it;
};
class IfcRoundedRectangleProfileDef : public IfcRectangleProfileDef {
public:
    IfcPositiveLengthMeasure RoundingRadius();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRoundedRectangleProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRoundedRectangleProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoundedRectangleProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcRoundedRectangleProfileDef>::it it;
};
class IfcSectionedSpine : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcCompositeCurve> SpineCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > CrossSections();
    SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement3D> > CrossSectionPositions();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSectionedSpine (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSectionedSpine> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcServiceLifeFactor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcServiceLifeFactor> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcServiceLifeFactor> > list;
    typedef IfcTemplatedEntityList<IfcServiceLifeFactor>::it it;
};
class IfcShellBasedSurfaceModel : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > SbsmBoundary();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcShellBasedSurfaceModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcShellBasedSurfaceModel> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSlippageConnectionCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSlippageConnectionCondition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSlippageConnectionCondition> > list;
    typedef IfcTemplatedEntityList<IfcSlippageConnectionCondition>::it it;
};
class IfcSolidModel : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSolidModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSolidModel> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSolidModel> > list;
    typedef IfcTemplatedEntityList<IfcSolidModel>::it it;
};
class IfcSoundProperties : public IfcPropertySetDefinition {
public:
    IfcBoolean IsAttenuating();
    bool hasSoundScale();
    IfcSoundScaleEnum::IfcSoundScaleEnum SoundScale();
    SHARED_PTR< IfcTemplatedEntityList<IfcSoundValue> > SoundValues();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSoundProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSoundProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSoundProperties> > list;
    typedef IfcTemplatedEntityList<IfcSoundProperties>::it it;
};
class IfcSoundValue : public IfcPropertySetDefinition {
public:
    bool hasSoundLevelTimeSeries();
    SHARED_PTR<IfcTimeSeries> SoundLevelTimeSeries();
    IfcFrequencyMeasure Frequency();
    bool hasSoundLevelSingleValue();
    IfcDerivedMeasureValue SoundLevelSingleValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSoundValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSoundValue> ptr;
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
    SHARED_PTR<IfcTimeSeries> ThermalLoadTimeSeriesValues();
    bool hasUserDefinedThermalLoadSource();
    IfcLabel UserDefinedThermalLoadSource();
    bool hasUserDefinedPropertySource();
    IfcLabel UserDefinedPropertySource();
    IfcThermalLoadTypeEnum::IfcThermalLoadTypeEnum ThermalLoadType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSpaceThermalLoadProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSpaceThermalLoadProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadLinearForce (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadLinearForce> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadPlanarForce (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadPlanarForce> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadSingleDisplacement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadSingleDisplacement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadSingleDisplacement> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadSingleDisplacement>::it it;
};
class IfcStructuralLoadSingleDisplacementDistortion : public IfcStructuralLoadSingleDisplacement {
public:
    bool hasDistortion();
    IfcCurvatureMeasure Distortion();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadSingleDisplacementDistortion (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadSingleDisplacementDistortion> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadSingleForce (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadSingleForce> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadSingleForce> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadSingleForce>::it it;
};
class IfcStructuralLoadSingleForceWarping : public IfcStructuralLoadSingleForce {
public:
    bool hasWarpingMoment();
    IfcWarpingMomentMeasure WarpingMoment();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadSingleForceWarping (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadSingleForceWarping> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralProfileProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralSteelProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralSteelProfileProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSteelProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSteelProfileProperties>::it it;
};
class IfcSubedge : public IfcEdge {
public:
    SHARED_PTR<IfcEdge> ParentEdge();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSubedge (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSubedge> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSubedge> > list;
    typedef IfcTemplatedEntityList<IfcSubedge>::it it;
};
class IfcSurface : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurface> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceStyleRendering (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceStyleRendering> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceStyleRendering> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceStyleRendering>::it it;
};
class IfcSweptAreaSolid : public IfcSolidModel {
public:
    SHARED_PTR<IfcProfileDef> SweptArea();
    SHARED_PTR<IfcAxis2Placement3D> Position();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSweptAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSweptAreaSolid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSweptAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcSweptAreaSolid>::it it;
};
class IfcSweptDiskSolid : public IfcSolidModel {
public:
    SHARED_PTR<IfcCurve> Directrix();
    IfcPositiveLengthMeasure Radius();
    bool hasInnerRadius();
    IfcPositiveLengthMeasure InnerRadius();
    IfcParameterValue StartParam();
    IfcParameterValue EndParam();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSweptDiskSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSweptDiskSolid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSweptDiskSolid> > list;
    typedef IfcTemplatedEntityList<IfcSweptDiskSolid>::it it;
};
class IfcSweptSurface : public IfcSurface {
public:
    SHARED_PTR<IfcProfileDef> SweptCurve();
    SHARED_PTR<IfcAxis2Placement3D> Position();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSweptSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSweptSurface> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTShapeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcTShapeProfileDef>::it it;
};
class IfcTerminatorSymbol : public IfcAnnotationSymbolOccurrence {
public:
    SHARED_PTR<IfcAnnotationCurveOccurrence> AnnotatedCurve();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTerminatorSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTerminatorSymbol> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTerminatorSymbol> > list;
    typedef IfcTemplatedEntityList<IfcTerminatorSymbol>::it it;
};
class IfcTextLiteral : public IfcGeometricRepresentationItem {
public:
    IfcPresentableText Literal();
    IfcAxis2Placement Placement();
    IfcTextPath::IfcTextPath Path();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextLiteral (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextLiteral> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextLiteral> > list;
    typedef IfcTemplatedEntityList<IfcTextLiteral>::it it;
};
class IfcTextLiteralWithExtent : public IfcTextLiteral {
public:
    SHARED_PTR<IfcPlanarExtent> Extent();
    IfcBoxAlignment BoxAlignment();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTextLiteralWithExtent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTextLiteralWithExtent> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTextLiteralWithExtent> > list;
    typedef IfcTemplatedEntityList<IfcTextLiteralWithExtent>::it it;
};
class IfcTrapeziumProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure BottomXDim();
    IfcPositiveLengthMeasure TopXDim();
    IfcPositiveLengthMeasure YDim();
    IfcLengthMeasure TopXOffset();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTrapeziumProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTrapeziumProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTrapeziumProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcTrapeziumProfileDef>::it it;
};
class IfcTwoDirectionRepeatFactor : public IfcOneDirectionRepeatFactor {
public:
    SHARED_PTR<IfcVector> SecondRepeatFactor();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTwoDirectionRepeatFactor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTwoDirectionRepeatFactor> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTypeObject (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTypeObject> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTypeObject> > list;
    typedef IfcTemplatedEntityList<IfcTypeObject>::it it;
};
class IfcTypeProduct : public IfcTypeObject {
public:
    bool hasRepresentationMaps();
    SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationMap> > RepresentationMaps();
    bool hasTag();
    IfcLabel Tag();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTypeProduct (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTypeProduct> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcUShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcUShapeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcUShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcUShapeProfileDef>::it it;
};
class IfcVector : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcDirection> Orientation();
    IfcLengthMeasure Magnitude();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVector (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVector> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVector> > list;
    typedef IfcTemplatedEntityList<IfcVector>::it it;
};
class IfcVertexLoop : public IfcLoop {
public:
    SHARED_PTR<IfcVertex> LoopVertex();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVertexLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVertexLoop> ptr;
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
    SHARED_PTR<IfcShapeAspect> ShapeAspectStyle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWindowLiningProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWindowLiningProperties> ptr;
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
    SHARED_PTR<IfcShapeAspect> ShapeAspectStyle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWindowPanelProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWindowPanelProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWindowPanelProperties> > list;
    typedef IfcTemplatedEntityList<IfcWindowPanelProperties>::it it;
};
class IfcWindowStyle : public IfcTypeProduct {
public:
    IfcWindowStyleConstructionEnum::IfcWindowStyleConstructionEnum ConstructionType();
    IfcWindowStyleOperationEnum::IfcWindowStyleOperationEnum OperationType();
    bool ParameterTakesPrecedence();
    bool Sizeable();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWindowStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWindowStyle> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcZShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcZShapeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcZShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcZShapeProfileDef>::it it;
};
class IfcAnnotationCurveOccurrence : public IfcAnnotationOccurrence {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationCurveOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationCurveOccurrence> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationCurveOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationCurveOccurrence>::it it;
};
class IfcAnnotationFillArea : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcCurve> OuterBoundary();
    bool hasInnerBoundaries();
    SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > InnerBoundaries();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationFillArea (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationFillArea> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationFillArea> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationFillArea>::it it;
};
class IfcAnnotationFillAreaOccurrence : public IfcAnnotationOccurrence {
public:
    bool hasFillStyleTarget();
    SHARED_PTR<IfcPoint> FillStyleTarget();
    bool hasGlobalOrLocal();
    IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum GlobalOrLocal();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationFillAreaOccurrence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationFillAreaOccurrence> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationFillAreaOccurrence> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationFillAreaOccurrence>::it it;
};
class IfcAnnotationSurface : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcGeometricRepresentationItem> Item();
    bool hasTextureCoordinates();
    SHARED_PTR<IfcTextureCoordinate> TextureCoordinates();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotationSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotationSurface> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAnnotationSurface> > list;
    typedef IfcTemplatedEntityList<IfcAnnotationSurface>::it it;
};
class IfcAxis1Placement : public IfcPlacement {
public:
    bool hasAxis();
    SHARED_PTR<IfcDirection> Axis();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAxis1Placement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAxis1Placement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAxis1Placement> > list;
    typedef IfcTemplatedEntityList<IfcAxis1Placement>::it it;
};
class IfcAxis2Placement2D : public IfcPlacement {
public:
    bool hasRefDirection();
    SHARED_PTR<IfcDirection> RefDirection();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAxis2Placement2D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAxis2Placement2D> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement2D> > list;
    typedef IfcTemplatedEntityList<IfcAxis2Placement2D>::it it;
};
class IfcAxis2Placement3D : public IfcPlacement {
public:
    bool hasAxis();
    SHARED_PTR<IfcDirection> Axis();
    bool hasRefDirection();
    SHARED_PTR<IfcDirection> RefDirection();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAxis2Placement3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAxis2Placement3D> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement3D> > list;
    typedef IfcTemplatedEntityList<IfcAxis2Placement3D>::it it;
};
class IfcBooleanResult : public IfcGeometricRepresentationItem {
public:
    IfcBooleanOperator::IfcBooleanOperator Operator();
    IfcBooleanOperand FirstOperand();
    IfcBooleanOperand SecondOperand();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBooleanResult (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBooleanResult> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBooleanResult> > list;
    typedef IfcTemplatedEntityList<IfcBooleanResult>::it it;
};
class IfcBoundedSurface : public IfcSurface {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundedSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundedSurface> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundedSurface> > list;
    typedef IfcTemplatedEntityList<IfcBoundedSurface>::it it;
};
class IfcBoundingBox : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcCartesianPoint> Corner();
    IfcPositiveLengthMeasure XDim();
    IfcPositiveLengthMeasure YDim();
    IfcPositiveLengthMeasure ZDim();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundingBox (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundingBox> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoundingBox> > list;
    typedef IfcTemplatedEntityList<IfcBoundingBox>::it it;
};
class IfcBoxedHalfSpace : public IfcHalfSpaceSolid {
public:
    SHARED_PTR<IfcBoundingBox> Enclosure();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoxedHalfSpace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoxedHalfSpace> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCShapeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCShapeProfileDef>::it it;
};
class IfcCartesianPoint : public IfcPoint {
public:
    std::vector<IfcLengthMeasure> /*[1:3]*/ Coordinates();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCartesianPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCartesianPoint> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > list;
    typedef IfcTemplatedEntityList<IfcCartesianPoint>::it it;
};
class IfcCartesianTransformationOperator : public IfcGeometricRepresentationItem {
public:
    bool hasAxis1();
    SHARED_PTR<IfcDirection> Axis1();
    bool hasAxis2();
    SHARED_PTR<IfcDirection> Axis2();
    SHARED_PTR<IfcCartesianPoint> LocalOrigin();
    bool hasScale();
    float Scale();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCartesianTransformationOperator (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCartesianTransformationOperator> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator>::it it;
};
class IfcCartesianTransformationOperator2D : public IfcCartesianTransformationOperator {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCartesianTransformationOperator2D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCartesianTransformationOperator2D> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator2D> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator2D>::it it;
};
class IfcCartesianTransformationOperator2DnonUniform : public IfcCartesianTransformationOperator2D {
public:
    bool hasScale2();
    float Scale2();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCartesianTransformationOperator2DnonUniform (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCartesianTransformationOperator2DnonUniform> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator2DnonUniform> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator2DnonUniform>::it it;
};
class IfcCartesianTransformationOperator3D : public IfcCartesianTransformationOperator {
public:
    bool hasAxis3();
    SHARED_PTR<IfcDirection> Axis3();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCartesianTransformationOperator3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCartesianTransformationOperator3D> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator3D> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator3D>::it it;
};
class IfcCartesianTransformationOperator3DnonUniform : public IfcCartesianTransformationOperator3D {
public:
    bool hasScale2();
    float Scale2();
    bool hasScale3();
    float Scale3();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCartesianTransformationOperator3DnonUniform (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCartesianTransformationOperator3DnonUniform> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCartesianTransformationOperator3DnonUniform> > list;
    typedef IfcTemplatedEntityList<IfcCartesianTransformationOperator3DnonUniform>::it it;
};
class IfcCircleProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCircleProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCircleProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCircleProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCircleProfileDef>::it it;
};
class IfcClosedShell : public IfcConnectedFaceSet {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcClosedShell (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcClosedShell> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcClosedShell> > list;
    typedef IfcTemplatedEntityList<IfcClosedShell>::it it;
};
class IfcCompositeCurveSegment : public IfcGeometricRepresentationItem {
public:
    IfcTransitionCode::IfcTransitionCode Transition();
    bool SameSense();
    SHARED_PTR<IfcCurve> ParentCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurve> > UsingCurves(); // INVERSE IfcCompositeCurve::Segments
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCompositeCurveSegment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCompositeCurveSegment> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCraneRailAShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCraneRailAShapeProfileDef> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCraneRailFShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCraneRailFShapeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCraneRailFShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCraneRailFShapeProfileDef>::it it;
};
class IfcCsgPrimitive3D : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcAxis2Placement3D> Position();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCsgPrimitive3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCsgPrimitive3D> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCsgPrimitive3D> > list;
    typedef IfcTemplatedEntityList<IfcCsgPrimitive3D>::it it;
};
class IfcCsgSolid : public IfcSolidModel {
public:
    IfcCsgSelect TreeRootExpression();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCsgSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCsgSolid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCsgSolid> > list;
    typedef IfcTemplatedEntityList<IfcCsgSolid>::it it;
};
class IfcCurve : public IfcGeometricRepresentationItem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > list;
    typedef IfcTemplatedEntityList<IfcCurve>::it it;
};
class IfcCurveBoundedPlane : public IfcBoundedSurface {
public:
    SHARED_PTR<IfcPlane> BasisSurface();
    SHARED_PTR<IfcCurve> OuterBoundary();
    SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > InnerBoundaries();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurveBoundedPlane (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurveBoundedPlane> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurveBoundedPlane> > list;
    typedef IfcTemplatedEntityList<IfcCurveBoundedPlane>::it it;
};
class IfcDefinedSymbol : public IfcGeometricRepresentationItem {
public:
    IfcDefinedSymbolSelect Definition();
    SHARED_PTR<IfcCartesianTransformationOperator2D> Target();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDefinedSymbol (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDefinedSymbol> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDefinedSymbol> > list;
    typedef IfcTemplatedEntityList<IfcDefinedSymbol>::it it;
};
class IfcDimensionCurve : public IfcAnnotationCurveOccurrence {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcTerminatorSymbol> > AnnotatedBySymbols(); // INVERSE IfcTerminatorSymbol::AnnotatedCurve
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDimensionCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDimensionCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCurve> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCurve>::it it;
};
class IfcDimensionCurveTerminator : public IfcTerminatorSymbol {
public:
    IfcDimensionExtentUsage::IfcDimensionExtentUsage Role();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDimensionCurveTerminator (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDimensionCurveTerminator> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCurveTerminator> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCurveTerminator>::it it;
};
class IfcDirection : public IfcGeometricRepresentationItem {
public:
    std::vector<float> /*[2:3]*/ DirectionRatios();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDirection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDirection> ptr;
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
    SHARED_PTR<IfcShapeAspect> ShapeAspectStyle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDoorLiningProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDoorLiningProperties> ptr;
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
    SHARED_PTR<IfcShapeAspect> ShapeAspectStyle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDoorPanelProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDoorPanelProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDoorPanelProperties> > list;
    typedef IfcTemplatedEntityList<IfcDoorPanelProperties>::it it;
};
class IfcDoorStyle : public IfcTypeProduct {
public:
    IfcDoorStyleOperationEnum::IfcDoorStyleOperationEnum OperationType();
    IfcDoorStyleConstructionEnum::IfcDoorStyleConstructionEnum ConstructionType();
    bool ParameterTakesPrecedence();
    bool Sizeable();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDoorStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDoorStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDoorStyle> > list;
    typedef IfcTemplatedEntityList<IfcDoorStyle>::it it;
};
class IfcDraughtingCallout : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Contents();
    SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCalloutRelationship> > IsRelatedFromCallout(); // INVERSE IfcDraughtingCalloutRelationship::RelatedDraughtingCallout
    SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCalloutRelationship> > IsRelatedToCallout(); // INVERSE IfcDraughtingCalloutRelationship::RelatingDraughtingCallout
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDraughtingCallout (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDraughtingCallout> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingCallout> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingCallout>::it it;
};
class IfcDraughtingPreDefinedColour : public IfcPreDefinedColour {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDraughtingPreDefinedColour (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDraughtingPreDefinedColour> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingPreDefinedColour> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingPreDefinedColour>::it it;
};
class IfcDraughtingPreDefinedCurveFont : public IfcPreDefinedCurveFont {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDraughtingPreDefinedCurveFont (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDraughtingPreDefinedCurveFont> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDraughtingPreDefinedCurveFont> > list;
    typedef IfcTemplatedEntityList<IfcDraughtingPreDefinedCurveFont>::it it;
};
class IfcEdgeLoop : public IfcLoop {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > EdgeList();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEdgeLoop (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEdgeLoop> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdgeLoop> > list;
    typedef IfcTemplatedEntityList<IfcEdgeLoop>::it it;
};
class IfcElementQuantity : public IfcPropertySetDefinition {
public:
    bool hasMethodOfMeasurement();
    IfcLabel MethodOfMeasurement();
    SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > Quantities();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElementQuantity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElementQuantity> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementQuantity> > list;
    typedef IfcTemplatedEntityList<IfcElementQuantity>::it it;
};
class IfcElementType : public IfcTypeProduct {
public:
    bool hasElementType();
    IfcLabel ElementType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementType> > list;
    typedef IfcTemplatedEntityList<IfcElementType>::it it;
};
class IfcElementarySurface : public IfcSurface {
public:
    SHARED_PTR<IfcAxis2Placement3D> Position();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElementarySurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElementarySurface> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementarySurface> > list;
    typedef IfcTemplatedEntityList<IfcElementarySurface>::it it;
};
class IfcEllipseProfileDef : public IfcParameterizedProfileDef {
public:
    IfcPositiveLengthMeasure SemiAxis1();
    IfcPositiveLengthMeasure SemiAxis2();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEllipseProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEllipseProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEllipseProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcEllipseProfileDef>::it it;
};
class IfcEnergyProperties : public IfcPropertySetDefinition {
public:
    bool hasEnergySequence();
    IfcEnergySequenceEnum::IfcEnergySequenceEnum EnergySequence();
    bool hasUserDefinedEnergySequence();
    IfcLabel UserDefinedEnergySequence();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEnergyProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEnergyProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEnergyProperties> > list;
    typedef IfcTemplatedEntityList<IfcEnergyProperties>::it it;
};
class IfcExtrudedAreaSolid : public IfcSweptAreaSolid {
public:
    SHARED_PTR<IfcDirection> ExtrudedDirection();
    IfcPositiveLengthMeasure Depth();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcExtrudedAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcExtrudedAreaSolid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcExtrudedAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcExtrudedAreaSolid>::it it;
};
class IfcFaceBasedSurfaceModel : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcConnectedFaceSet> > FbsmFaces();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFaceBasedSurfaceModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFaceBasedSurfaceModel> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFaceBasedSurfaceModel> > list;
    typedef IfcTemplatedEntityList<IfcFaceBasedSurfaceModel>::it it;
};
class IfcFillAreaStyleHatching : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcCurveStyle> HatchLineAppearance();
    IfcHatchLineDistanceSelect StartOfNextHatchLine();
    bool hasPointOfReferenceHatchLine();
    SHARED_PTR<IfcCartesianPoint> PointOfReferenceHatchLine();
    bool hasPatternStart();
    SHARED_PTR<IfcCartesianPoint> PatternStart();
    IfcPlaneAngleMeasure HatchLineAngle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFillAreaStyleHatching (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFillAreaStyleHatching> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFillAreaStyleHatching> > list;
    typedef IfcTemplatedEntityList<IfcFillAreaStyleHatching>::it it;
};
class IfcFillAreaStyleTileSymbolWithStyle : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcAnnotationSymbolOccurrence> Symbol();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFillAreaStyleTileSymbolWithStyle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFillAreaStyleTileSymbolWithStyle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFillAreaStyleTileSymbolWithStyle> > list;
    typedef IfcTemplatedEntityList<IfcFillAreaStyleTileSymbolWithStyle>::it it;
};
class IfcFillAreaStyleTiles : public IfcGeometricRepresentationItem {
public:
    SHARED_PTR<IfcOneDirectionRepeatFactor> TilingPattern();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Tiles();
    IfcPositiveRatioMeasure TilingScale();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFillAreaStyleTiles (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFillAreaStyleTiles> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFillAreaStyleTiles> > list;
    typedef IfcTemplatedEntityList<IfcFillAreaStyleTiles>::it it;
};
class IfcFluidFlowProperties : public IfcPropertySetDefinition {
public:
    IfcPropertySourceEnum::IfcPropertySourceEnum PropertySource();
    bool hasFlowConditionTimeSeries();
    SHARED_PTR<IfcTimeSeries> FlowConditionTimeSeries();
    bool hasVelocityTimeSeries();
    SHARED_PTR<IfcTimeSeries> VelocityTimeSeries();
    bool hasFlowrateTimeSeries();
    SHARED_PTR<IfcTimeSeries> FlowrateTimeSeries();
    SHARED_PTR<IfcMaterial> Fluid();
    bool hasPressureTimeSeries();
    SHARED_PTR<IfcTimeSeries> PressureTimeSeries();
    bool hasUserDefinedPropertySource();
    IfcLabel UserDefinedPropertySource();
    bool hasTemperatureSingleValue();
    IfcThermodynamicTemperatureMeasure TemperatureSingleValue();
    bool hasWetBulbTemperatureSingleValue();
    IfcThermodynamicTemperatureMeasure WetBulbTemperatureSingleValue();
    bool hasWetBulbTemperatureTimeSeries();
    SHARED_PTR<IfcTimeSeries> WetBulbTemperatureTimeSeries();
    bool hasTemperatureTimeSeries();
    SHARED_PTR<IfcTimeSeries> TemperatureTimeSeries();
    bool hasFlowrateSingleValue();
    IfcDerivedMeasureValue FlowrateSingleValue();
    bool hasFlowConditionSingleValue();
    IfcPositiveRatioMeasure FlowConditionSingleValue();
    bool hasVelocitySingleValue();
    IfcLinearVelocityMeasure VelocitySingleValue();
    bool hasPressureSingleValue();
    IfcPressureMeasure PressureSingleValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFluidFlowProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFluidFlowProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFluidFlowProperties> > list;
    typedef IfcTemplatedEntityList<IfcFluidFlowProperties>::it it;
};
class IfcFurnishingElementType : public IfcElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFurnishingElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFurnishingElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnishingElementType> > list;
    typedef IfcTemplatedEntityList<IfcFurnishingElementType>::it it;
};
class IfcFurnitureType : public IfcFurnishingElementType {
public:
    IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum AssemblyPlace();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFurnitureType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFurnitureType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnitureType> > list;
    typedef IfcTemplatedEntityList<IfcFurnitureType>::it it;
};
class IfcGeometricCurveSet : public IfcGeometricSet {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGeometricCurveSet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGeometricCurveSet> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcIShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcIShapeProfileDef> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLShapeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcLShapeProfileDef>::it it;
};
class IfcLine : public IfcCurve {
public:
    SHARED_PTR<IfcCartesianPoint> Pnt();
    SHARED_PTR<IfcVector> Dir();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLine (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLine> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLine> > list;
    typedef IfcTemplatedEntityList<IfcLine>::it it;
};
class IfcManifoldSolidBrep : public IfcSolidModel {
public:
    SHARED_PTR<IfcClosedShell> Outer();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcManifoldSolidBrep (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcManifoldSolidBrep> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcManifoldSolidBrep> > list;
    typedef IfcTemplatedEntityList<IfcManifoldSolidBrep>::it it;
};
class IfcObject : public IfcObjectDefinition {
public:
    bool hasObjectType();
    IfcLabel ObjectType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelDefines> > IsDefinedBy(); // INVERSE IfcRelDefines::RelatedObjects
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcObject (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcObject> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcObject> > list;
    typedef IfcTemplatedEntityList<IfcObject>::it it;
};
class IfcOffsetCurve2D : public IfcCurve {
public:
    SHARED_PTR<IfcCurve> BasisCurve();
    IfcLengthMeasure Distance();
    bool SelfIntersect();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOffsetCurve2D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOffsetCurve2D> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOffsetCurve2D> > list;
    typedef IfcTemplatedEntityList<IfcOffsetCurve2D>::it it;
};
class IfcOffsetCurve3D : public IfcCurve {
public:
    SHARED_PTR<IfcCurve> BasisCurve();
    IfcLengthMeasure Distance();
    bool SelfIntersect();
    SHARED_PTR<IfcDirection> RefDirection();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOffsetCurve3D (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOffsetCurve3D> ptr;
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
    SHARED_PTR<IfcShapeAspect> ShapeAspectStyle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPermeableCoveringProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPermeableCoveringProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPermeableCoveringProperties> > list;
    typedef IfcTemplatedEntityList<IfcPermeableCoveringProperties>::it it;
};
class IfcPlanarBox : public IfcPlanarExtent {
public:
    IfcAxis2Placement Placement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPlanarBox (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPlanarBox> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlanarBox> > list;
    typedef IfcTemplatedEntityList<IfcPlanarBox>::it it;
};
class IfcPlane : public IfcElementarySurface {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPlane (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPlane> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlane> > list;
    typedef IfcTemplatedEntityList<IfcPlane>::it it;
};
class IfcProcess : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProcess> > OperatesOn(); // INVERSE IfcRelAssignsToProcess::RelatingProcess
    SHARED_PTR< IfcTemplatedEntityList<IfcRelSequence> > IsSuccessorFrom(); // INVERSE IfcRelSequence::RelatedProcess
    SHARED_PTR< IfcTemplatedEntityList<IfcRelSequence> > IsPredecessorTo(); // INVERSE IfcRelSequence::RelatingProcess
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProcess (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProcess> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProcess> > list;
    typedef IfcTemplatedEntityList<IfcProcess>::it it;
};
class IfcProduct : public IfcObject {
public:
    bool hasObjectPlacement();
    SHARED_PTR<IfcObjectPlacement> ObjectPlacement();
    bool hasRepresentation();
    SHARED_PTR<IfcProductRepresentation> Representation();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProduct> > ReferencedBy(); // INVERSE IfcRelAssignsToProduct::RelatingProduct
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProduct (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProduct> ptr;
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
    SHARED_PTR<IfcUnitAssignment> UnitsInContext();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProject (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProject> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProject> > list;
    typedef IfcTemplatedEntityList<IfcProject>::it it;
};
class IfcProjectionCurve : public IfcAnnotationCurveOccurrence {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProjectionCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProjectionCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectionCurve> > list;
    typedef IfcTemplatedEntityList<IfcProjectionCurve>::it it;
};
class IfcPropertySet : public IfcPropertySetDefinition {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > HasProperties();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPropertySet (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPropertySet> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPropertySet> > list;
    typedef IfcTemplatedEntityList<IfcPropertySet>::it it;
};
class IfcProxy : public IfcProduct {
public:
    IfcObjectTypeEnum::IfcObjectTypeEnum ProxyType();
    bool hasTag();
    IfcLabel Tag();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProxy (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProxy> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRectangleHollowProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRectangleHollowProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangleHollowProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcRectangleHollowProfileDef>::it it;
};
class IfcRectangularPyramid : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure XLength();
    IfcPositiveLengthMeasure YLength();
    IfcPositiveLengthMeasure Height();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRectangularPyramid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRectangularPyramid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangularPyramid> > list;
    typedef IfcTemplatedEntityList<IfcRectangularPyramid>::it it;
};
class IfcRectangularTrimmedSurface : public IfcBoundedSurface {
public:
    SHARED_PTR<IfcSurface> BasisSurface();
    IfcParameterValue U1();
    IfcParameterValue V1();
    IfcParameterValue U2();
    IfcParameterValue V2();
    bool Usense();
    bool Vsense();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRectangularTrimmedSurface (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRectangularTrimmedSurface> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRectangularTrimmedSurface> > list;
    typedef IfcTemplatedEntityList<IfcRectangularTrimmedSurface>::it it;
};
class IfcRelAssigns : public IfcRelationship {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > RelatedObjects();
    bool hasRelatedObjectsType();
    IfcObjectTypeEnum::IfcObjectTypeEnum RelatedObjectsType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssigns (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssigns> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssigns> > list;
    typedef IfcTemplatedEntityList<IfcRelAssigns>::it it;
};
class IfcRelAssignsToActor : public IfcRelAssigns {
public:
    SHARED_PTR<IfcActor> RelatingActor();
    bool hasActingRole();
    SHARED_PTR<IfcActorRole> ActingRole();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsToActor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsToActor> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToActor> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToActor>::it it;
};
class IfcRelAssignsToControl : public IfcRelAssigns {
public:
    SHARED_PTR<IfcControl> RelatingControl();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsToControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsToControl> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToControl> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToControl>::it it;
};
class IfcRelAssignsToGroup : public IfcRelAssigns {
public:
    SHARED_PTR<IfcGroup> RelatingGroup();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsToGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsToGroup> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToGroup> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToGroup>::it it;
};
class IfcRelAssignsToProcess : public IfcRelAssigns {
public:
    SHARED_PTR<IfcProcess> RelatingProcess();
    bool hasQuantityInProcess();
    SHARED_PTR<IfcMeasureWithUnit> QuantityInProcess();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsToProcess (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsToProcess> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProcess> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToProcess>::it it;
};
class IfcRelAssignsToProduct : public IfcRelAssigns {
public:
    SHARED_PTR<IfcProduct> RelatingProduct();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsToProduct (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsToProduct> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProduct> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToProduct>::it it;
};
class IfcRelAssignsToProjectOrder : public IfcRelAssignsToControl {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsToProjectOrder (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsToProjectOrder> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProjectOrder> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToProjectOrder>::it it;
};
class IfcRelAssignsToResource : public IfcRelAssigns {
public:
    SHARED_PTR<IfcResource> RelatingResource();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsToResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsToResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToResource> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsToResource>::it it;
};
class IfcRelAssociates : public IfcRelationship {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRoot> > RelatedObjects();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociates (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociates> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociates> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociates>::it it;
};
class IfcRelAssociatesAppliedValue : public IfcRelAssociates {
public:
    SHARED_PTR<IfcAppliedValue> RelatingAppliedValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesAppliedValue (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesAppliedValue> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesAppliedValue> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesAppliedValue>::it it;
};
class IfcRelAssociatesApproval : public IfcRelAssociates {
public:
    SHARED_PTR<IfcApproval> RelatingApproval();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesApproval (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesApproval> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesApproval> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesApproval>::it it;
};
class IfcRelAssociatesClassification : public IfcRelAssociates {
public:
    IfcClassificationNotationSelect RelatingClassification();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesClassification (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesClassification> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesClassification> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesClassification>::it it;
};
class IfcRelAssociatesConstraint : public IfcRelAssociates {
public:
    IfcLabel Intent();
    SHARED_PTR<IfcConstraint> RelatingConstraint();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesConstraint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesConstraint> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesConstraint> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesConstraint>::it it;
};
class IfcRelAssociatesDocument : public IfcRelAssociates {
public:
    IfcDocumentSelect RelatingDocument();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesDocument (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesDocument> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesDocument> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesDocument>::it it;
};
class IfcRelAssociatesLibrary : public IfcRelAssociates {
public:
    IfcLibrarySelect RelatingLibrary();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesLibrary (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesLibrary> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesLibrary> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesLibrary>::it it;
};
class IfcRelAssociatesMaterial : public IfcRelAssociates {
public:
    IfcMaterialSelect RelatingMaterial();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesMaterial (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesMaterial> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesMaterial> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesMaterial>::it it;
};
class IfcRelAssociatesProfileProperties : public IfcRelAssociates {
public:
    SHARED_PTR<IfcProfileProperties> RelatingProfileProperties();
    bool hasProfileSectionLocation();
    SHARED_PTR<IfcShapeAspect> ProfileSectionLocation();
    bool hasProfileOrientation();
    IfcOrientationSelect ProfileOrientation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssociatesProfileProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssociatesProfileProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssociatesProfileProperties> > list;
    typedef IfcTemplatedEntityList<IfcRelAssociatesProfileProperties>::it it;
};
class IfcRelConnects : public IfcRelationship {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnects (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnects> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnects> > list;
    typedef IfcTemplatedEntityList<IfcRelConnects>::it it;
};
class IfcRelConnectsElements : public IfcRelConnects {
public:
    bool hasConnectionGeometry();
    SHARED_PTR<IfcConnectionGeometry> ConnectionGeometry();
    SHARED_PTR<IfcElement> RelatingElement();
    SHARED_PTR<IfcElement> RelatedElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsElements> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsElements> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsElements>::it it;
};
class IfcRelConnectsPathElements : public IfcRelConnectsElements {
public:
    std::vector<int> /*[0:?]*/ RelatingPriorities();
    std::vector<int> /*[0:?]*/ RelatedPriorities();
    IfcConnectionTypeEnum::IfcConnectionTypeEnum RelatedConnectionType();
    IfcConnectionTypeEnum::IfcConnectionTypeEnum RelatingConnectionType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsPathElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsPathElements> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPathElements> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsPathElements>::it it;
};
class IfcRelConnectsPortToElement : public IfcRelConnects {
public:
    SHARED_PTR<IfcPort> RelatingPort();
    SHARED_PTR<IfcElement> RelatedElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsPortToElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsPortToElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPortToElement> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsPortToElement>::it it;
};
class IfcRelConnectsPorts : public IfcRelConnects {
public:
    SHARED_PTR<IfcPort> RelatingPort();
    SHARED_PTR<IfcPort> RelatedPort();
    bool hasRealizingElement();
    SHARED_PTR<IfcElement> RealizingElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsPorts (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsPorts> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPorts> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsPorts>::it it;
};
class IfcRelConnectsStructuralActivity : public IfcRelConnects {
public:
    IfcStructuralActivityAssignmentSelect RelatingElement();
    SHARED_PTR<IfcStructuralActivity> RelatedStructuralActivity();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsStructuralActivity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsStructuralActivity> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralActivity> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsStructuralActivity>::it it;
};
class IfcRelConnectsStructuralElement : public IfcRelConnects {
public:
    SHARED_PTR<IfcElement> RelatingElement();
    SHARED_PTR<IfcStructuralMember> RelatedStructuralMember();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsStructuralElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsStructuralElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralElement> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsStructuralElement>::it it;
};
class IfcRelConnectsStructuralMember : public IfcRelConnects {
public:
    SHARED_PTR<IfcStructuralMember> RelatingStructuralMember();
    SHARED_PTR<IfcStructuralConnection> RelatedStructuralConnection();
    bool hasAppliedCondition();
    SHARED_PTR<IfcBoundaryCondition> AppliedCondition();
    bool hasAdditionalConditions();
    SHARED_PTR<IfcStructuralConnectionCondition> AdditionalConditions();
    bool hasSupportedLength();
    IfcLengthMeasure SupportedLength();
    bool hasConditionCoordinateSystem();
    SHARED_PTR<IfcAxis2Placement3D> ConditionCoordinateSystem();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsStructuralMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsStructuralMember> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralMember> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsStructuralMember>::it it;
};
class IfcRelConnectsWithEccentricity : public IfcRelConnectsStructuralMember {
public:
    SHARED_PTR<IfcConnectionGeometry> ConnectionConstraint();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsWithEccentricity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsWithEccentricity> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsWithEccentricity> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsWithEccentricity>::it it;
};
class IfcRelConnectsWithRealizingElements : public IfcRelConnectsElements {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcElement> > RealizingElements();
    bool hasConnectionType();
    IfcLabel ConnectionType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelConnectsWithRealizingElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelConnectsWithRealizingElements> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsWithRealizingElements> > list;
    typedef IfcTemplatedEntityList<IfcRelConnectsWithRealizingElements>::it it;
};
class IfcRelContainedInSpatialStructure : public IfcRelConnects {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > RelatedElements();
    SHARED_PTR<IfcSpatialStructureElement> RelatingStructure();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelContainedInSpatialStructure (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelContainedInSpatialStructure> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelContainedInSpatialStructure> > list;
    typedef IfcTemplatedEntityList<IfcRelContainedInSpatialStructure>::it it;
};
class IfcRelCoversBldgElements : public IfcRelConnects {
public:
    SHARED_PTR<IfcElement> RelatingBuildingElement();
    SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > RelatedCoverings();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelCoversBldgElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelCoversBldgElements> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversBldgElements> > list;
    typedef IfcTemplatedEntityList<IfcRelCoversBldgElements>::it it;
};
class IfcRelCoversSpaces : public IfcRelConnects {
public:
    SHARED_PTR<IfcSpace> RelatedSpace();
    SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > RelatedCoverings();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelCoversSpaces (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelCoversSpaces> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversSpaces> > list;
    typedef IfcTemplatedEntityList<IfcRelCoversSpaces>::it it;
};
class IfcRelDecomposes : public IfcRelationship {
public:
    SHARED_PTR<IfcObjectDefinition> RelatingObject();
    SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > RelatedObjects();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelDecomposes (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelDecomposes> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDecomposes> > list;
    typedef IfcTemplatedEntityList<IfcRelDecomposes>::it it;
};
class IfcRelDefines : public IfcRelationship {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcObject> > RelatedObjects();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelDefines (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelDefines> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDefines> > list;
    typedef IfcTemplatedEntityList<IfcRelDefines>::it it;
};
class IfcRelDefinesByProperties : public IfcRelDefines {
public:
    SHARED_PTR<IfcPropertySetDefinition> RelatingPropertyDefinition();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelDefinesByProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelDefinesByProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDefinesByProperties> > list;
    typedef IfcTemplatedEntityList<IfcRelDefinesByProperties>::it it;
};
class IfcRelDefinesByType : public IfcRelDefines {
public:
    SHARED_PTR<IfcTypeObject> RelatingType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelDefinesByType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelDefinesByType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelDefinesByType> > list;
    typedef IfcTemplatedEntityList<IfcRelDefinesByType>::it it;
};
class IfcRelFillsElement : public IfcRelConnects {
public:
    SHARED_PTR<IfcOpeningElement> RelatingOpeningElement();
    SHARED_PTR<IfcElement> RelatedBuildingElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelFillsElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelFillsElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelFillsElement> > list;
    typedef IfcTemplatedEntityList<IfcRelFillsElement>::it it;
};
class IfcRelFlowControlElements : public IfcRelConnects {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElement> > RelatedControlElements();
    SHARED_PTR<IfcDistributionFlowElement> RelatingFlowElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelFlowControlElements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelFlowControlElements> ptr;
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
    SHARED_PTR<IfcSpatialStructureElement> LocationOfInteraction();
    SHARED_PTR<IfcSpaceProgram> RelatedSpaceProgram();
    SHARED_PTR<IfcSpaceProgram> RelatingSpaceProgram();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelInteractionRequirements (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelInteractionRequirements> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelInteractionRequirements> > list;
    typedef IfcTemplatedEntityList<IfcRelInteractionRequirements>::it it;
};
class IfcRelNests : public IfcRelDecomposes {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelNests (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelNests> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelNests> > list;
    typedef IfcTemplatedEntityList<IfcRelNests>::it it;
};
class IfcRelOccupiesSpaces : public IfcRelAssignsToActor {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelOccupiesSpaces (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelOccupiesSpaces> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelOccupiesSpaces> > list;
    typedef IfcTemplatedEntityList<IfcRelOccupiesSpaces>::it it;
};
class IfcRelOverridesProperties : public IfcRelDefinesByProperties {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > OverridingProperties();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelOverridesProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelOverridesProperties> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelOverridesProperties> > list;
    typedef IfcTemplatedEntityList<IfcRelOverridesProperties>::it it;
};
class IfcRelProjectsElement : public IfcRelConnects {
public:
    SHARED_PTR<IfcElement> RelatingElement();
    SHARED_PTR<IfcFeatureElementAddition> RelatedFeatureElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelProjectsElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelProjectsElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelProjectsElement> > list;
    typedef IfcTemplatedEntityList<IfcRelProjectsElement>::it it;
};
class IfcRelReferencedInSpatialStructure : public IfcRelConnects {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > RelatedElements();
    SHARED_PTR<IfcSpatialStructureElement> RelatingStructure();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelReferencedInSpatialStructure (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelReferencedInSpatialStructure> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelReferencedInSpatialStructure> > list;
    typedef IfcTemplatedEntityList<IfcRelReferencedInSpatialStructure>::it it;
};
class IfcRelSchedulesCostItems : public IfcRelAssignsToControl {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelSchedulesCostItems (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelSchedulesCostItems> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelSchedulesCostItems> > list;
    typedef IfcTemplatedEntityList<IfcRelSchedulesCostItems>::it it;
};
class IfcRelSequence : public IfcRelConnects {
public:
    SHARED_PTR<IfcProcess> RelatingProcess();
    SHARED_PTR<IfcProcess> RelatedProcess();
    IfcTimeMeasure TimeLag();
    IfcSequenceEnum::IfcSequenceEnum SequenceType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelSequence (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelSequence> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelSequence> > list;
    typedef IfcTemplatedEntityList<IfcRelSequence>::it it;
};
class IfcRelServicesBuildings : public IfcRelConnects {
public:
    SHARED_PTR<IfcSystem> RelatingSystem();
    SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElement> > RelatedBuildings();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelServicesBuildings (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelServicesBuildings> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelServicesBuildings> > list;
    typedef IfcTemplatedEntityList<IfcRelServicesBuildings>::it it;
};
class IfcRelSpaceBoundary : public IfcRelConnects {
public:
    SHARED_PTR<IfcSpace> RelatingSpace();
    bool hasRelatedBuildingElement();
    SHARED_PTR<IfcElement> RelatedBuildingElement();
    bool hasConnectionGeometry();
    SHARED_PTR<IfcConnectionGeometry> ConnectionGeometry();
    IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtualEnum PhysicalOrVirtualBoundary();
    IfcInternalOrExternalEnum::IfcInternalOrExternalEnum InternalOrExternalBoundary();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelSpaceBoundary (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelSpaceBoundary> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelSpaceBoundary> > list;
    typedef IfcTemplatedEntityList<IfcRelSpaceBoundary>::it it;
};
class IfcRelVoidsElement : public IfcRelConnects {
public:
    SHARED_PTR<IfcElement> RelatingBuildingElement();
    SHARED_PTR<IfcFeatureElementSubtraction> RelatedOpeningElement();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelVoidsElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelVoidsElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelVoidsElement> > list;
    typedef IfcTemplatedEntityList<IfcRelVoidsElement>::it it;
};
class IfcResource : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToResource> > ResourceOf(); // INVERSE IfcRelAssignsToResource::RelatingResource
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcResource> > list;
    typedef IfcTemplatedEntityList<IfcResource>::it it;
};
class IfcRevolvedAreaSolid : public IfcSweptAreaSolid {
public:
    SHARED_PTR<IfcAxis1Placement> Axis();
    IfcPlaneAngleMeasure Angle();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRevolvedAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRevolvedAreaSolid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRevolvedAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcRevolvedAreaSolid>::it it;
};
class IfcRightCircularCone : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure Height();
    IfcPositiveLengthMeasure BottomRadius();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRightCircularCone (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRightCircularCone> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRightCircularCone> > list;
    typedef IfcTemplatedEntityList<IfcRightCircularCone>::it it;
};
class IfcRightCircularCylinder : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure Height();
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRightCircularCylinder (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRightCircularCylinder> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSpatialStructureElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSpatialStructureElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElement> > list;
    typedef IfcTemplatedEntityList<IfcSpatialStructureElement>::it it;
};
class IfcSpatialStructureElementType : public IfcElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSpatialStructureElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSpatialStructureElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElementType> > list;
    typedef IfcTemplatedEntityList<IfcSpatialStructureElementType>::it it;
};
class IfcSphere : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSphere (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSphere> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSphere> > list;
    typedef IfcTemplatedEntityList<IfcSphere>::it it;
};
class IfcStructuralActivity : public IfcProduct {
public:
    SHARED_PTR<IfcStructuralLoad> AppliedLoad();
    IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum GlobalOrLocal();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralActivity> > AssignedToStructuralItem(); // INVERSE IfcRelConnectsStructuralActivity::RelatedStructuralActivity
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralActivity (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralActivity> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralActivity> > list;
    typedef IfcTemplatedEntityList<IfcStructuralActivity>::it it;
};
class IfcStructuralItem : public IfcProduct {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralActivity> > AssignedStructuralActivity(); // INVERSE IfcRelConnectsStructuralActivity::RelatingElement
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralItem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralItem> > list;
    typedef IfcTemplatedEntityList<IfcStructuralItem>::it it;
};
class IfcStructuralMember : public IfcStructuralItem {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralElement> > ReferencesElement(); // INVERSE IfcRelConnectsStructuralElement::RelatedStructuralMember
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralMember> > ConnectedBy(); // INVERSE IfcRelConnectsStructuralMember::RelatingStructuralMember
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralMember> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralMember> > list;
    typedef IfcTemplatedEntityList<IfcStructuralMember>::it it;
};
class IfcStructuralReaction : public IfcStructuralActivity {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAction> > Causes(); // INVERSE IfcStructuralAction::CausedBy
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralReaction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralReaction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralReaction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralReaction>::it it;
};
class IfcStructuralSurfaceMember : public IfcStructuralMember {
public:
    IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceTypeEnum PredefinedType();
    bool hasThickness();
    IfcPositiveLengthMeasure Thickness();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralSurfaceMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralSurfaceMember> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSurfaceMember> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSurfaceMember>::it it;
};
class IfcStructuralSurfaceMemberVarying : public IfcStructuralSurfaceMember {
public:
    std::vector<IfcPositiveLengthMeasure> /*[2:?]*/ SubsequentThickness();
    SHARED_PTR<IfcShapeAspect> VaryingThicknessLocation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralSurfaceMemberVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralSurfaceMemberVarying> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSurfaceMemberVarying> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSurfaceMemberVarying>::it it;
};
class IfcStructuredDimensionCallout : public IfcDraughtingCallout {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuredDimensionCallout (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuredDimensionCallout> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuredDimensionCallout> > list;
    typedef IfcTemplatedEntityList<IfcStructuredDimensionCallout>::it it;
};
class IfcSurfaceCurveSweptAreaSolid : public IfcSweptAreaSolid {
public:
    SHARED_PTR<IfcCurve> Directrix();
    IfcParameterValue StartParam();
    IfcParameterValue EndParam();
    SHARED_PTR<IfcSurface> ReferenceSurface();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceCurveSweptAreaSolid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceCurveSweptAreaSolid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceCurveSweptAreaSolid> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceCurveSweptAreaSolid>::it it;
};
class IfcSurfaceOfLinearExtrusion : public IfcSweptSurface {
public:
    SHARED_PTR<IfcDirection> ExtrudedDirection();
    IfcLengthMeasure Depth();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceOfLinearExtrusion (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceOfLinearExtrusion> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceOfLinearExtrusion> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceOfLinearExtrusion>::it it;
};
class IfcSurfaceOfRevolution : public IfcSweptSurface {
public:
    SHARED_PTR<IfcAxis1Placement> AxisPosition();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSurfaceOfRevolution (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSurfaceOfRevolution> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceOfRevolution> > list;
    typedef IfcTemplatedEntityList<IfcSurfaceOfRevolution>::it it;
};
class IfcSystemFurnitureElementType : public IfcFurnishingElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSystemFurnitureElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSystemFurnitureElementType> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTask (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTask> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTask> > list;
    typedef IfcTemplatedEntityList<IfcTask>::it it;
};
class IfcTransportElementType : public IfcElementType {
public:
    IfcTransportElementTypeEnum::IfcTransportElementTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTransportElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTransportElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTransportElementType> > list;
    typedef IfcTemplatedEntityList<IfcTransportElementType>::it it;
};
class IfcActor : public IfcObject {
public:
    IfcActorSelect TheActor();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToActor> > IsActingUpon(); // INVERSE IfcRelAssignsToActor::RelatingActor
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcActor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcActor> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcActor> > list;
    typedef IfcTemplatedEntityList<IfcActor>::it it;
};
class IfcAnnotation : public IfcProduct {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelContainedInSpatialStructure> > ContainedInStructure(); // INVERSE IfcRelContainedInSpatialStructure::RelatedElements
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAnnotation (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAnnotation> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAsymmetricIShapeProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAsymmetricIShapeProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAsymmetricIShapeProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcAsymmetricIShapeProfileDef>::it it;
};
class IfcBlock : public IfcCsgPrimitive3D {
public:
    IfcPositiveLengthMeasure XLength();
    IfcPositiveLengthMeasure YLength();
    IfcPositiveLengthMeasure ZLength();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBlock (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBlock> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBlock> > list;
    typedef IfcTemplatedEntityList<IfcBlock>::it it;
};
class IfcBooleanClippingResult : public IfcBooleanResult {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBooleanClippingResult (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBooleanClippingResult> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBooleanClippingResult> > list;
    typedef IfcTemplatedEntityList<IfcBooleanClippingResult>::it it;
};
class IfcBoundedCurve : public IfcCurve {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoundedCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoundedCurve> ptr;
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
    SHARED_PTR<IfcPostalAddress> BuildingAddress();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuilding (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuilding> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuilding> > list;
    typedef IfcTemplatedEntityList<IfcBuilding>::it it;
};
class IfcBuildingElementType : public IfcElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuildingElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuildingElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementType> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementType>::it it;
};
class IfcBuildingStorey : public IfcSpatialStructureElement {
public:
    bool hasElevation();
    IfcLengthMeasure Elevation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuildingStorey (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuildingStorey> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingStorey> > list;
    typedef IfcTemplatedEntityList<IfcBuildingStorey>::it it;
};
class IfcCircleHollowProfileDef : public IfcCircleProfileDef {
public:
    IfcPositiveLengthMeasure WallThickness();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCircleHollowProfileDef (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCircleHollowProfileDef> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCircleHollowProfileDef> > list;
    typedef IfcTemplatedEntityList<IfcCircleHollowProfileDef>::it it;
};
class IfcColumnType : public IfcBuildingElementType {
public:
    IfcColumnTypeEnum::IfcColumnTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcColumnType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcColumnType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColumnType> > list;
    typedef IfcTemplatedEntityList<IfcColumnType>::it it;
};
class IfcCompositeCurve : public IfcBoundedCurve {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurveSegment> > Segments();
    bool SelfIntersect();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCompositeCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCompositeCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurve> > list;
    typedef IfcTemplatedEntityList<IfcCompositeCurve>::it it;
};
class IfcConic : public IfcCurve {
public:
    IfcAxis2Placement Position();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConic (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConic> ptr;
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
    SHARED_PTR<IfcMeasureWithUnit> BaseQuantity();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstructionResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstructionResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionResource>::it it;
};
class IfcControl : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToControl> > Controls(); // INVERSE IfcRelAssignsToControl::RelatingControl
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcControl> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcControl> > list;
    typedef IfcTemplatedEntityList<IfcControl>::it it;
};
class IfcCostItem : public IfcControl {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCostItem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCostItem> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCostSchedule (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCostSchedule> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCostSchedule> > list;
    typedef IfcTemplatedEntityList<IfcCostSchedule>::it it;
};
class IfcCoveringType : public IfcBuildingElementType {
public:
    IfcCoveringTypeEnum::IfcCoveringTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCoveringType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCoveringType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoveringType> > list;
    typedef IfcTemplatedEntityList<IfcCoveringType>::it it;
};
class IfcCrewResource : public IfcConstructionResource {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCrewResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCrewResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCrewResource> > list;
    typedef IfcTemplatedEntityList<IfcCrewResource>::it it;
};
class IfcCurtainWallType : public IfcBuildingElementType {
public:
    IfcCurtainWallTypeEnum::IfcCurtainWallTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurtainWallType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurtainWallType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurtainWallType> > list;
    typedef IfcTemplatedEntityList<IfcCurtainWallType>::it it;
};
class IfcDimensionCurveDirectedCallout : public IfcDraughtingCallout {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDimensionCurveDirectedCallout (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDimensionCurveDirectedCallout> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDimensionCurveDirectedCallout> > list;
    typedef IfcTemplatedEntityList<IfcDimensionCurveDirectedCallout>::it it;
};
class IfcDistributionElementType : public IfcElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionElementType> > list;
    typedef IfcTemplatedEntityList<IfcDistributionElementType>::it it;
};
class IfcDistributionFlowElementType : public IfcDistributionElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionFlowElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionFlowElementType> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricalBaseProperties (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricalBaseProperties> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElement> > list;
    typedef IfcTemplatedEntityList<IfcElement>::it it;
};
class IfcElementAssembly : public IfcElement {
public:
    bool hasAssemblyPlace();
    IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum AssemblyPlace();
    IfcElementAssemblyTypeEnum::IfcElementAssemblyTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElementAssembly (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElementAssembly> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementAssembly> > list;
    typedef IfcTemplatedEntityList<IfcElementAssembly>::it it;
};
class IfcElementComponent : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElementComponent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElementComponent> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementComponent> > list;
    typedef IfcTemplatedEntityList<IfcElementComponent>::it it;
};
class IfcElementComponentType : public IfcElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElementComponentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElementComponentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElementComponentType> > list;
    typedef IfcTemplatedEntityList<IfcElementComponentType>::it it;
};
class IfcEllipse : public IfcConic {
public:
    IfcPositiveLengthMeasure SemiAxis1();
    IfcPositiveLengthMeasure SemiAxis2();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEllipse (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEllipse> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEllipse> > list;
    typedef IfcTemplatedEntityList<IfcEllipse>::it it;
};
class IfcEnergyConversionDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEnergyConversionDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEnergyConversionDeviceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEnergyConversionDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcEnergyConversionDeviceType>::it it;
};
class IfcEquipmentElement : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEquipmentElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEquipmentElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEquipmentElement> > list;
    typedef IfcTemplatedEntityList<IfcEquipmentElement>::it it;
};
class IfcEquipmentStandard : public IfcControl {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEquipmentStandard (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEquipmentStandard> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEquipmentStandard> > list;
    typedef IfcTemplatedEntityList<IfcEquipmentStandard>::it it;
};
class IfcEvaporativeCoolerType : public IfcEnergyConversionDeviceType {
public:
    IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEvaporativeCoolerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEvaporativeCoolerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEvaporativeCoolerType> > list;
    typedef IfcTemplatedEntityList<IfcEvaporativeCoolerType>::it it;
};
class IfcEvaporatorType : public IfcEnergyConversionDeviceType {
public:
    IfcEvaporatorTypeEnum::IfcEvaporatorTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEvaporatorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEvaporatorType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEvaporatorType> > list;
    typedef IfcTemplatedEntityList<IfcEvaporatorType>::it it;
};
class IfcFacetedBrep : public IfcManifoldSolidBrep {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFacetedBrep (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFacetedBrep> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFacetedBrep> > list;
    typedef IfcTemplatedEntityList<IfcFacetedBrep>::it it;
};
class IfcFacetedBrepWithVoids : public IfcManifoldSolidBrep {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcClosedShell> > Voids();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFacetedBrepWithVoids (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFacetedBrepWithVoids> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFacetedBrepWithVoids> > list;
    typedef IfcTemplatedEntityList<IfcFacetedBrepWithVoids>::it it;
};
class IfcFastener : public IfcElementComponent {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFastener (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFastener> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFastener> > list;
    typedef IfcTemplatedEntityList<IfcFastener>::it it;
};
class IfcFastenerType : public IfcElementComponentType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFastenerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFastenerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFastenerType> > list;
    typedef IfcTemplatedEntityList<IfcFastenerType>::it it;
};
class IfcFeatureElement : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFeatureElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFeatureElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFeatureElement> > list;
    typedef IfcTemplatedEntityList<IfcFeatureElement>::it it;
};
class IfcFeatureElementAddition : public IfcFeatureElement {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelProjectsElement> > ProjectsElements(); // INVERSE IfcRelProjectsElement::RelatedFeatureElement
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFeatureElementAddition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFeatureElementAddition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFeatureElementAddition> > list;
    typedef IfcTemplatedEntityList<IfcFeatureElementAddition>::it it;
};
class IfcFeatureElementSubtraction : public IfcFeatureElement {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelVoidsElement> > VoidsElements(); // INVERSE IfcRelVoidsElement::RelatedOpeningElement
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFeatureElementSubtraction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFeatureElementSubtraction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFeatureElementSubtraction> > list;
    typedef IfcTemplatedEntityList<IfcFeatureElementSubtraction>::it it;
};
class IfcFlowControllerType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowControllerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowControllerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowControllerType> > list;
    typedef IfcTemplatedEntityList<IfcFlowControllerType>::it it;
};
class IfcFlowFittingType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowFittingType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowFittingType> > list;
    typedef IfcTemplatedEntityList<IfcFlowFittingType>::it it;
};
class IfcFlowMeterType : public IfcFlowControllerType {
public:
    IfcFlowMeterTypeEnum::IfcFlowMeterTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowMeterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowMeterType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowMeterType> > list;
    typedef IfcTemplatedEntityList<IfcFlowMeterType>::it it;
};
class IfcFlowMovingDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowMovingDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowMovingDeviceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowMovingDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcFlowMovingDeviceType>::it it;
};
class IfcFlowSegmentType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowSegmentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcFlowSegmentType>::it it;
};
class IfcFlowStorageDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowStorageDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowStorageDeviceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowStorageDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcFlowStorageDeviceType>::it it;
};
class IfcFlowTerminalType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowTerminalType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcFlowTerminalType>::it it;
};
class IfcFlowTreatmentDeviceType : public IfcDistributionFlowElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowTreatmentDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowTreatmentDeviceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTreatmentDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcFlowTreatmentDeviceType>::it it;
};
class IfcFurnishingElement : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFurnishingElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFurnishingElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnishingElement> > list;
    typedef IfcTemplatedEntityList<IfcFurnishingElement>::it it;
};
class IfcFurnitureStandard : public IfcControl {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFurnitureStandard (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFurnitureStandard> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFurnitureStandard> > list;
    typedef IfcTemplatedEntityList<IfcFurnitureStandard>::it it;
};
class IfcGasTerminalType : public IfcFlowTerminalType {
public:
    IfcGasTerminalTypeEnum::IfcGasTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGasTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGasTerminalType> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGrid (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGrid> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGrid> > list;
    typedef IfcTemplatedEntityList<IfcGrid>::it it;
};
class IfcGroup : public IfcObject {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToGroup> > IsGroupedBy(); // INVERSE IfcRelAssignsToGroup::RelatingGroup
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcGroup> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcGroup> > list;
    typedef IfcTemplatedEntityList<IfcGroup>::it it;
};
class IfcHeatExchangerType : public IfcEnergyConversionDeviceType {
public:
    IfcHeatExchangerTypeEnum::IfcHeatExchangerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcHeatExchangerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcHeatExchangerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcHeatExchangerType> > list;
    typedef IfcTemplatedEntityList<IfcHeatExchangerType>::it it;
};
class IfcHumidifierType : public IfcEnergyConversionDeviceType {
public:
    IfcHumidifierTypeEnum::IfcHumidifierTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcHumidifierType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcHumidifierType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcHumidifierType> > list;
    typedef IfcTemplatedEntityList<IfcHumidifierType>::it it;
};
class IfcInventory : public IfcGroup {
public:
    IfcInventoryTypeEnum::IfcInventoryTypeEnum InventoryType();
    IfcActorSelect Jurisdiction();
    SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > ResponsiblePersons();
    SHARED_PTR<IfcCalendarDate> LastUpdateDate();
    bool hasCurrentValue();
    SHARED_PTR<IfcCostValue> CurrentValue();
    bool hasOriginalValue();
    SHARED_PTR<IfcCostValue> OriginalValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcInventory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcInventory> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcInventory> > list;
    typedef IfcTemplatedEntityList<IfcInventory>::it it;
};
class IfcJunctionBoxType : public IfcFlowFittingType {
public:
    IfcJunctionBoxTypeEnum::IfcJunctionBoxTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcJunctionBoxType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcJunctionBoxType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcJunctionBoxType> > list;
    typedef IfcTemplatedEntityList<IfcJunctionBoxType>::it it;
};
class IfcLaborResource : public IfcConstructionResource {
public:
    bool hasSkillSet();
    IfcText SkillSet();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLaborResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLaborResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLaborResource> > list;
    typedef IfcTemplatedEntityList<IfcLaborResource>::it it;
};
class IfcLampType : public IfcFlowTerminalType {
public:
    IfcLampTypeEnum::IfcLampTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLampType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLampType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLampType> > list;
    typedef IfcTemplatedEntityList<IfcLampType>::it it;
};
class IfcLightFixtureType : public IfcFlowTerminalType {
public:
    IfcLightFixtureTypeEnum::IfcLightFixtureTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLightFixtureType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLightFixtureType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLightFixtureType> > list;
    typedef IfcTemplatedEntityList<IfcLightFixtureType>::it it;
};
class IfcLinearDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcLinearDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcLinearDimension> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcLinearDimension> > list;
    typedef IfcTemplatedEntityList<IfcLinearDimension>::it it;
};
class IfcMechanicalFastener : public IfcFastener {
public:
    bool hasNominalDiameter();
    IfcPositiveLengthMeasure NominalDiameter();
    bool hasNominalLength();
    IfcPositiveLengthMeasure NominalLength();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMechanicalFastener (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMechanicalFastener> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalFastener> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalFastener>::it it;
};
class IfcMechanicalFastenerType : public IfcFastenerType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMechanicalFastenerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMechanicalFastenerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMechanicalFastenerType> > list;
    typedef IfcTemplatedEntityList<IfcMechanicalFastenerType>::it it;
};
class IfcMemberType : public IfcBuildingElementType {
public:
    IfcMemberTypeEnum::IfcMemberTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMemberType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMemberType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMemberType> > list;
    typedef IfcTemplatedEntityList<IfcMemberType>::it it;
};
class IfcMotorConnectionType : public IfcEnergyConversionDeviceType {
public:
    IfcMotorConnectionTypeEnum::IfcMotorConnectionTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMotorConnectionType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMotorConnectionType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMotorConnectionType> > list;
    typedef IfcTemplatedEntityList<IfcMotorConnectionType>::it it;
};
class IfcMove : public IfcTask {
public:
    SHARED_PTR<IfcSpatialStructureElement> MoveFrom();
    SHARED_PTR<IfcSpatialStructureElement> MoveTo();
    bool hasPunchList();
    std::vector<IfcText> /*[1:?]*/ PunchList();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMove (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMove> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMove> > list;
    typedef IfcTemplatedEntityList<IfcMove>::it it;
};
class IfcOccupant : public IfcActor {
public:
    IfcOccupantTypeEnum::IfcOccupantTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOccupant (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOccupant> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOccupant> > list;
    typedef IfcTemplatedEntityList<IfcOccupant>::it it;
};
class IfcOpeningElement : public IfcFeatureElementSubtraction {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelFillsElement> > HasFillings(); // INVERSE IfcRelFillsElement::RelatingOpeningElement
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOpeningElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOpeningElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOpeningElement> > list;
    typedef IfcTemplatedEntityList<IfcOpeningElement>::it it;
};
class IfcOrderAction : public IfcTask {
public:
    IfcIdentifier ActionID();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOrderAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOrderAction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOrderAction> > list;
    typedef IfcTemplatedEntityList<IfcOrderAction>::it it;
};
class IfcOutletType : public IfcFlowTerminalType {
public:
    IfcOutletTypeEnum::IfcOutletTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcOutletType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcOutletType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcOutletType> > list;
    typedef IfcTemplatedEntityList<IfcOutletType>::it it;
};
class IfcPerformanceHistory : public IfcControl {
public:
    IfcLabel LifeCyclePhase();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPerformanceHistory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPerformanceHistory> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPerformanceHistory> > list;
    typedef IfcTemplatedEntityList<IfcPerformanceHistory>::it it;
};
class IfcPermit : public IfcControl {
public:
    IfcIdentifier PermitID();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPermit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPermit> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPermit> > list;
    typedef IfcTemplatedEntityList<IfcPermit>::it it;
};
class IfcPipeFittingType : public IfcFlowFittingType {
public:
    IfcPipeFittingTypeEnum::IfcPipeFittingTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPipeFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPipeFittingType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPipeFittingType> > list;
    typedef IfcTemplatedEntityList<IfcPipeFittingType>::it it;
};
class IfcPipeSegmentType : public IfcFlowSegmentType {
public:
    IfcPipeSegmentTypeEnum::IfcPipeSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPipeSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPipeSegmentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPipeSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcPipeSegmentType>::it it;
};
class IfcPlateType : public IfcBuildingElementType {
public:
    IfcPlateTypeEnum::IfcPlateTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPlateType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPlateType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlateType> > list;
    typedef IfcTemplatedEntityList<IfcPlateType>::it it;
};
class IfcPolyline : public IfcBoundedCurve {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > Points();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPolyline (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPolyline> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPolyline> > list;
    typedef IfcTemplatedEntityList<IfcPolyline>::it it;
};
class IfcPort : public IfcProduct {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPortToElement> > ContainedIn(); // INVERSE IfcRelConnectsPortToElement::RelatingPort
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPorts> > ConnectedFrom(); // INVERSE IfcRelConnectsPorts::RelatedPort
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsPorts> > ConnectedTo(); // INVERSE IfcRelConnectsPorts::RelatingPort
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPort (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPort> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPort> > list;
    typedef IfcTemplatedEntityList<IfcPort>::it it;
};
class IfcProcedure : public IfcProcess {
public:
    IfcIdentifier ProcedureID();
    IfcProcedureTypeEnum::IfcProcedureTypeEnum ProcedureType();
    bool hasUserDefinedProcedureType();
    IfcLabel UserDefinedProcedureType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProcedure (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProcedure> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProcedure> > list;
    typedef IfcTemplatedEntityList<IfcProcedure>::it it;
};
class IfcProjectOrder : public IfcControl {
public:
    IfcIdentifier ID();
    IfcProjectOrderTypeEnum::IfcProjectOrderTypeEnum PredefinedType();
    bool hasStatus();
    IfcLabel Status();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProjectOrder (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProjectOrder> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectOrder> > list;
    typedef IfcTemplatedEntityList<IfcProjectOrder>::it it;
};
class IfcProjectOrderRecord : public IfcControl {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProjectOrder> > Records();
    IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProjectOrderRecord (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProjectOrderRecord> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectOrderRecord> > list;
    typedef IfcTemplatedEntityList<IfcProjectOrderRecord>::it it;
};
class IfcProjectionElement : public IfcFeatureElementAddition {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProjectionElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProjectionElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProjectionElement> > list;
    typedef IfcTemplatedEntityList<IfcProjectionElement>::it it;
};
class IfcProtectiveDeviceType : public IfcFlowControllerType {
public:
    IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcProtectiveDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcProtectiveDeviceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcProtectiveDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcProtectiveDeviceType>::it it;
};
class IfcPumpType : public IfcFlowMovingDeviceType {
public:
    IfcPumpTypeEnum::IfcPumpTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPumpType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPumpType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPumpType> > list;
    typedef IfcTemplatedEntityList<IfcPumpType>::it it;
};
class IfcRadiusDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRadiusDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRadiusDimension> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRadiusDimension> > list;
    typedef IfcTemplatedEntityList<IfcRadiusDimension>::it it;
};
class IfcRailingType : public IfcBuildingElementType {
public:
    IfcRailingTypeEnum::IfcRailingTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRailingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRailingType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRailingType> > list;
    typedef IfcTemplatedEntityList<IfcRailingType>::it it;
};
class IfcRampFlightType : public IfcBuildingElementType {
public:
    IfcRampFlightTypeEnum::IfcRampFlightTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRampFlightType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRampFlightType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRampFlightType> > list;
    typedef IfcTemplatedEntityList<IfcRampFlightType>::it it;
};
class IfcRelAggregates : public IfcRelDecomposes {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAggregates (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAggregates> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAggregates> > list;
    typedef IfcTemplatedEntityList<IfcRelAggregates>::it it;
};
class IfcRelAssignsTasks : public IfcRelAssignsToControl {
public:
    bool hasTimeForTask();
    SHARED_PTR<IfcScheduleTimeControl> TimeForTask();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRelAssignsTasks (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRelAssignsTasks> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsTasks> > list;
    typedef IfcTemplatedEntityList<IfcRelAssignsTasks>::it it;
};
class IfcSanitaryTerminalType : public IfcFlowTerminalType {
public:
    IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSanitaryTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSanitaryTerminalType> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcScheduleTimeControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcScheduleTimeControl> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcScheduleTimeControl> > list;
    typedef IfcTemplatedEntityList<IfcScheduleTimeControl>::it it;
};
class IfcServiceLife : public IfcControl {
public:
    IfcServiceLifeTypeEnum::IfcServiceLifeTypeEnum ServiceLifeType();
    IfcTimeMeasure ServiceLifeDuration();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcServiceLife (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcServiceLife> ptr;
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
    SHARED_PTR<IfcPostalAddress> SiteAddress();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSite (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSite> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSite> > list;
    typedef IfcTemplatedEntityList<IfcSite>::it it;
};
class IfcSlabType : public IfcBuildingElementType {
public:
    IfcSlabTypeEnum::IfcSlabTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSlabType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSlabType> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSpace (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSpace> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpace> > list;
    typedef IfcTemplatedEntityList<IfcSpace>::it it;
};
class IfcSpaceHeaterType : public IfcEnergyConversionDeviceType {
public:
    IfcSpaceHeaterTypeEnum::IfcSpaceHeaterTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSpaceHeaterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSpaceHeaterType> ptr;
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
    SHARED_PTR<IfcSpatialStructureElement> RequestedLocation();
    IfcAreaMeasure StandardRequiredArea();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelInteractionRequirements> > HasInteractionReqsFrom(); // INVERSE IfcRelInteractionRequirements::RelatedSpaceProgram
    SHARED_PTR< IfcTemplatedEntityList<IfcRelInteractionRequirements> > HasInteractionReqsTo(); // INVERSE IfcRelInteractionRequirements::RelatingSpaceProgram
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSpaceProgram (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSpaceProgram> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpaceProgram> > list;
    typedef IfcTemplatedEntityList<IfcSpaceProgram>::it it;
};
class IfcSpaceType : public IfcSpatialStructureElementType {
public:
    IfcSpaceTypeEnum::IfcSpaceTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSpaceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSpaceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSpaceType> > list;
    typedef IfcTemplatedEntityList<IfcSpaceType>::it it;
};
class IfcStackTerminalType : public IfcFlowTerminalType {
public:
    IfcStackTerminalTypeEnum::IfcStackTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStackTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStackTerminalType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStackTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcStackTerminalType>::it it;
};
class IfcStairFlightType : public IfcBuildingElementType {
public:
    IfcStairFlightTypeEnum::IfcStairFlightTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStairFlightType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStairFlightType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStairFlightType> > list;
    typedef IfcTemplatedEntityList<IfcStairFlightType>::it it;
};
class IfcStructuralAction : public IfcStructuralActivity {
public:
    bool DestabilizingLoad();
    bool hasCausedBy();
    SHARED_PTR<IfcStructuralReaction> CausedBy();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralAction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralAction>::it it;
};
class IfcStructuralConnection : public IfcStructuralItem {
public:
    bool hasAppliedCondition();
    SHARED_PTR<IfcBoundaryCondition> AppliedCondition();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelConnectsStructuralMember> > ConnectsStructuralMembers(); // INVERSE IfcRelConnectsStructuralMember::RelatedStructuralConnection
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralConnection> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralConnection>::it it;
};
class IfcStructuralCurveConnection : public IfcStructuralConnection {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralCurveConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralCurveConnection> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralCurveConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralCurveConnection>::it it;
};
class IfcStructuralCurveMember : public IfcStructuralMember {
public:
    IfcStructuralCurveTypeEnum::IfcStructuralCurveTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralCurveMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralCurveMember> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralCurveMember> > list;
    typedef IfcTemplatedEntityList<IfcStructuralCurveMember>::it it;
};
class IfcStructuralCurveMemberVarying : public IfcStructuralCurveMember {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralCurveMemberVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralCurveMemberVarying> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralCurveMemberVarying> > list;
    typedef IfcTemplatedEntityList<IfcStructuralCurveMemberVarying>::it it;
};
class IfcStructuralLinearAction : public IfcStructuralAction {
public:
    IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum ProjectedOrTrue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLinearAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLinearAction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLinearAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLinearAction>::it it;
};
class IfcStructuralLinearActionVarying : public IfcStructuralLinearAction {
public:
    SHARED_PTR<IfcShapeAspect> VaryingAppliedLoadLocation();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > SubsequentAppliedLoads();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLinearActionVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLinearActionVarying> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralLoadGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralLoadGroup> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadGroup> > list;
    typedef IfcTemplatedEntityList<IfcStructuralLoadGroup>::it it;
};
class IfcStructuralPlanarAction : public IfcStructuralAction {
public:
    IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum ProjectedOrTrue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralPlanarAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralPlanarAction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPlanarAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPlanarAction>::it it;
};
class IfcStructuralPlanarActionVarying : public IfcStructuralPlanarAction {
public:
    SHARED_PTR<IfcShapeAspect> VaryingAppliedLoadLocation();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > SubsequentAppliedLoads();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralPlanarActionVarying (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralPlanarActionVarying> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPlanarActionVarying> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPlanarActionVarying>::it it;
};
class IfcStructuralPointAction : public IfcStructuralAction {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralPointAction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralPointAction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPointAction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPointAction>::it it;
};
class IfcStructuralPointConnection : public IfcStructuralConnection {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralPointConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralPointConnection> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPointConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPointConnection>::it it;
};
class IfcStructuralPointReaction : public IfcStructuralReaction {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralPointReaction (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralPointReaction> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralPointReaction> > list;
    typedef IfcTemplatedEntityList<IfcStructuralPointReaction>::it it;
};
class IfcStructuralResultGroup : public IfcGroup {
public:
    IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryTypeEnum TheoryType();
    bool hasResultForLoadGroup();
    SHARED_PTR<IfcStructuralLoadGroup> ResultForLoadGroup();
    bool IsLinear();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralAnalysisModel> > ResultGroupFor(); // INVERSE IfcStructuralAnalysisModel::HasResults
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralResultGroup (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralResultGroup> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralResultGroup> > list;
    typedef IfcTemplatedEntityList<IfcStructuralResultGroup>::it it;
};
class IfcStructuralSurfaceConnection : public IfcStructuralConnection {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralSurfaceConnection (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralSurfaceConnection> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStructuralSurfaceConnection> > list;
    typedef IfcTemplatedEntityList<IfcStructuralSurfaceConnection>::it it;
};
class IfcSubContractResource : public IfcConstructionResource {
public:
    bool hasSubContractor();
    IfcActorSelect SubContractor();
    bool hasJobDescription();
    IfcText JobDescription();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSubContractResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSubContractResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSubContractResource> > list;
    typedef IfcTemplatedEntityList<IfcSubContractResource>::it it;
};
class IfcSwitchingDeviceType : public IfcFlowControllerType {
public:
    IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSwitchingDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSwitchingDeviceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSwitchingDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcSwitchingDeviceType>::it it;
};
class IfcSystem : public IfcGroup {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelServicesBuildings> > ServicesBuildings(); // INVERSE IfcRelServicesBuildings::RelatingSystem
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSystem (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSystem> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSystem> > list;
    typedef IfcTemplatedEntityList<IfcSystem>::it it;
};
class IfcTankType : public IfcFlowStorageDeviceType {
public:
    IfcTankTypeEnum::IfcTankTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTankType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTankType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTankType> > list;
    typedef IfcTemplatedEntityList<IfcTankType>::it it;
};
class IfcTimeSeriesSchedule : public IfcControl {
public:
    bool hasApplicableDates();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > ApplicableDates();
    IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleTypeEnum TimeSeriesScheduleType();
    SHARED_PTR<IfcTimeSeries> TimeSeries();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTimeSeriesSchedule (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTimeSeriesSchedule> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesSchedule> > list;
    typedef IfcTemplatedEntityList<IfcTimeSeriesSchedule>::it it;
};
class IfcTransformerType : public IfcEnergyConversionDeviceType {
public:
    IfcTransformerTypeEnum::IfcTransformerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTransformerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTransformerType> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTransportElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTransportElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTransportElement> > list;
    typedef IfcTemplatedEntityList<IfcTransportElement>::it it;
};
class IfcTrimmedCurve : public IfcBoundedCurve {
public:
    SHARED_PTR<IfcCurve> BasisCurve();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Trim1();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Trim2();
    bool SenseAgreement();
    IfcTrimmingPreference::IfcTrimmingPreference MasterRepresentation();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTrimmedCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTrimmedCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTrimmedCurve> > list;
    typedef IfcTemplatedEntityList<IfcTrimmedCurve>::it it;
};
class IfcTubeBundleType : public IfcEnergyConversionDeviceType {
public:
    IfcTubeBundleTypeEnum::IfcTubeBundleTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTubeBundleType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTubeBundleType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTubeBundleType> > list;
    typedef IfcTemplatedEntityList<IfcTubeBundleType>::it it;
};
class IfcUnitaryEquipmentType : public IfcEnergyConversionDeviceType {
public:
    IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcUnitaryEquipmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcUnitaryEquipmentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcUnitaryEquipmentType> > list;
    typedef IfcTemplatedEntityList<IfcUnitaryEquipmentType>::it it;
};
class IfcValveType : public IfcFlowControllerType {
public:
    IfcValveTypeEnum::IfcValveTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcValveType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcValveType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcValveType> > list;
    typedef IfcTemplatedEntityList<IfcValveType>::it it;
};
class IfcVirtualElement : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVirtualElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVirtualElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVirtualElement> > list;
    typedef IfcTemplatedEntityList<IfcVirtualElement>::it it;
};
class IfcWallType : public IfcBuildingElementType {
public:
    IfcWallTypeEnum::IfcWallTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWallType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWallType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWallType> > list;
    typedef IfcTemplatedEntityList<IfcWallType>::it it;
};
class IfcWasteTerminalType : public IfcFlowTerminalType {
public:
    IfcWasteTerminalTypeEnum::IfcWasteTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWasteTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWasteTerminalType> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWorkControl (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWorkControl> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWorkControl> > list;
    typedef IfcTemplatedEntityList<IfcWorkControl>::it it;
};
class IfcWorkPlan : public IfcWorkControl {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWorkPlan (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWorkPlan> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWorkPlan> > list;
    typedef IfcTemplatedEntityList<IfcWorkPlan>::it it;
};
class IfcWorkSchedule : public IfcWorkControl {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWorkSchedule (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWorkSchedule> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWorkSchedule> > list;
    typedef IfcTemplatedEntityList<IfcWorkSchedule>::it it;
};
class IfcZone : public IfcGroup {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcZone (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcZone> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcZone> > list;
    typedef IfcTemplatedEntityList<IfcZone>::it it;
};
class Ifc2DCompositeCurve : public IfcCompositeCurve {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    Ifc2DCompositeCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<Ifc2DCompositeCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<Ifc2DCompositeCurve> > list;
    typedef IfcTemplatedEntityList<Ifc2DCompositeCurve>::it it;
};
class IfcActionRequest : public IfcControl {
public:
    IfcIdentifier RequestID();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcActionRequest (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcActionRequest> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcActionRequest> > list;
    typedef IfcTemplatedEntityList<IfcActionRequest>::it it;
};
class IfcAirTerminalBoxType : public IfcFlowControllerType {
public:
    IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAirTerminalBoxType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAirTerminalBoxType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAirTerminalBoxType> > list;
    typedef IfcTemplatedEntityList<IfcAirTerminalBoxType>::it it;
};
class IfcAirTerminalType : public IfcFlowTerminalType {
public:
    IfcAirTerminalTypeEnum::IfcAirTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAirTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAirTerminalType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAirTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcAirTerminalType>::it it;
};
class IfcAirToAirHeatRecoveryType : public IfcEnergyConversionDeviceType {
public:
    IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAirToAirHeatRecoveryType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAirToAirHeatRecoveryType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAirToAirHeatRecoveryType> > list;
    typedef IfcTemplatedEntityList<IfcAirToAirHeatRecoveryType>::it it;
};
class IfcAngularDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAngularDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAngularDimension> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAngularDimension> > list;
    typedef IfcTemplatedEntityList<IfcAngularDimension>::it it;
};
class IfcAsset : public IfcGroup {
public:
    IfcIdentifier AssetID();
    SHARED_PTR<IfcCostValue> OriginalValue();
    SHARED_PTR<IfcCostValue> CurrentValue();
    SHARED_PTR<IfcCostValue> TotalReplacementCost();
    IfcActorSelect Owner();
    IfcActorSelect User();
    SHARED_PTR<IfcPerson> ResponsiblePerson();
    SHARED_PTR<IfcCalendarDate> IncorporationDate();
    SHARED_PTR<IfcCostValue> DepreciatedValue();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAsset (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAsset> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBSplineCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBSplineCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBSplineCurve> > list;
    typedef IfcTemplatedEntityList<IfcBSplineCurve>::it it;
};
class IfcBeamType : public IfcBuildingElementType {
public:
    IfcBeamTypeEnum::IfcBeamTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBeamType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBeamType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBeamType> > list;
    typedef IfcTemplatedEntityList<IfcBeamType>::it it;
};
class IfcBezierCurve : public IfcBSplineCurve {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBezierCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBezierCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBezierCurve> > list;
    typedef IfcTemplatedEntityList<IfcBezierCurve>::it it;
};
class IfcBoilerType : public IfcEnergyConversionDeviceType {
public:
    IfcBoilerTypeEnum::IfcBoilerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBoilerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBoilerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBoilerType> > list;
    typedef IfcTemplatedEntityList<IfcBoilerType>::it it;
};
class IfcBuildingElement : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuildingElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuildingElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElement> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElement>::it it;
};
class IfcBuildingElementComponent : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuildingElementComponent (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuildingElementComponent> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementComponent> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementComponent>::it it;
};
class IfcBuildingElementPart : public IfcBuildingElementComponent {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuildingElementPart (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuildingElementPart> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementPart> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementPart>::it it;
};
class IfcBuildingElementProxy : public IfcBuildingElement {
public:
    bool hasCompositionType();
    IfcElementCompositionEnum::IfcElementCompositionEnum CompositionType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuildingElementProxy (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuildingElementProxy> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementProxy> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementProxy>::it it;
};
class IfcBuildingElementProxyType : public IfcBuildingElementType {
public:
    IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBuildingElementProxyType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBuildingElementProxyType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBuildingElementProxyType> > list;
    typedef IfcTemplatedEntityList<IfcBuildingElementProxyType>::it it;
};
class IfcCableCarrierFittingType : public IfcFlowFittingType {
public:
    IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCableCarrierFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCableCarrierFittingType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCableCarrierFittingType> > list;
    typedef IfcTemplatedEntityList<IfcCableCarrierFittingType>::it it;
};
class IfcCableCarrierSegmentType : public IfcFlowSegmentType {
public:
    IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCableCarrierSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCableCarrierSegmentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCableCarrierSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcCableCarrierSegmentType>::it it;
};
class IfcCableSegmentType : public IfcFlowSegmentType {
public:
    IfcCableSegmentTypeEnum::IfcCableSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCableSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCableSegmentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCableSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcCableSegmentType>::it it;
};
class IfcChillerType : public IfcEnergyConversionDeviceType {
public:
    IfcChillerTypeEnum::IfcChillerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcChillerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcChillerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcChillerType> > list;
    typedef IfcTemplatedEntityList<IfcChillerType>::it it;
};
class IfcCircle : public IfcConic {
public:
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCircle (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCircle> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCircle> > list;
    typedef IfcTemplatedEntityList<IfcCircle>::it it;
};
class IfcCoilType : public IfcEnergyConversionDeviceType {
public:
    IfcCoilTypeEnum::IfcCoilTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCoilType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCoilType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoilType> > list;
    typedef IfcTemplatedEntityList<IfcCoilType>::it it;
};
class IfcColumn : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcColumn (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcColumn> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcColumn> > list;
    typedef IfcTemplatedEntityList<IfcColumn>::it it;
};
class IfcCompressorType : public IfcFlowMovingDeviceType {
public:
    IfcCompressorTypeEnum::IfcCompressorTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCompressorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCompressorType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCompressorType> > list;
    typedef IfcTemplatedEntityList<IfcCompressorType>::it it;
};
class IfcCondenserType : public IfcEnergyConversionDeviceType {
public:
    IfcCondenserTypeEnum::IfcCondenserTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCondenserType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCondenserType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCondenserType> > list;
    typedef IfcTemplatedEntityList<IfcCondenserType>::it it;
};
class IfcCondition : public IfcGroup {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCondition (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCondition> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCondition> > list;
    typedef IfcTemplatedEntityList<IfcCondition>::it it;
};
class IfcConditionCriterion : public IfcControl {
public:
    IfcConditionCriterionSelect Criterion();
    IfcDateTimeSelect CriterionDateTime();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConditionCriterion (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConditionCriterion> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConditionCriterion> > list;
    typedef IfcTemplatedEntityList<IfcConditionCriterion>::it it;
};
class IfcConstructionEquipmentResource : public IfcConstructionResource {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstructionEquipmentResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstructionEquipmentResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionEquipmentResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionEquipmentResource>::it it;
};
class IfcConstructionMaterialResource : public IfcConstructionResource {
public:
    bool hasSuppliers();
    SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > Suppliers();
    bool hasUsageRatio();
    IfcRatioMeasure UsageRatio();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstructionMaterialResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstructionMaterialResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionMaterialResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionMaterialResource>::it it;
};
class IfcConstructionProductResource : public IfcConstructionResource {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcConstructionProductResource (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcConstructionProductResource> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcConstructionProductResource> > list;
    typedef IfcTemplatedEntityList<IfcConstructionProductResource>::it it;
};
class IfcCooledBeamType : public IfcEnergyConversionDeviceType {
public:
    IfcCooledBeamTypeEnum::IfcCooledBeamTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCooledBeamType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCooledBeamType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCooledBeamType> > list;
    typedef IfcTemplatedEntityList<IfcCooledBeamType>::it it;
};
class IfcCoolingTowerType : public IfcEnergyConversionDeviceType {
public:
    IfcCoolingTowerTypeEnum::IfcCoolingTowerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCoolingTowerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCoolingTowerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCoolingTowerType> > list;
    typedef IfcTemplatedEntityList<IfcCoolingTowerType>::it it;
};
class IfcCovering : public IfcBuildingElement {
public:
    bool hasPredefinedType();
    IfcCoveringTypeEnum::IfcCoveringTypeEnum PredefinedType();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversSpaces> > CoversSpaces(); // INVERSE IfcRelCoversSpaces::RelatedCoverings
    SHARED_PTR< IfcTemplatedEntityList<IfcRelCoversBldgElements> > Covers(); // INVERSE IfcRelCoversBldgElements::RelatedCoverings
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCovering (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCovering> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > list;
    typedef IfcTemplatedEntityList<IfcCovering>::it it;
};
class IfcCurtainWall : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcCurtainWall (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcCurtainWall> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcCurtainWall> > list;
    typedef IfcTemplatedEntityList<IfcCurtainWall>::it it;
};
class IfcDamperType : public IfcFlowControllerType {
public:
    IfcDamperTypeEnum::IfcDamperTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDamperType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDamperType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDamperType> > list;
    typedef IfcTemplatedEntityList<IfcDamperType>::it it;
};
class IfcDiameterDimension : public IfcDimensionCurveDirectedCallout {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDiameterDimension (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDiameterDimension> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDiameterDimension> > list;
    typedef IfcTemplatedEntityList<IfcDiameterDimension>::it it;
};
class IfcDiscreteAccessory : public IfcElementComponent {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDiscreteAccessory (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDiscreteAccessory> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDiscreteAccessory> > list;
    typedef IfcTemplatedEntityList<IfcDiscreteAccessory>::it it;
};
class IfcDiscreteAccessoryType : public IfcElementComponentType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDiscreteAccessoryType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDiscreteAccessoryType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDiscreteAccessoryType> > list;
    typedef IfcTemplatedEntityList<IfcDiscreteAccessoryType>::it it;
};
class IfcDistributionChamberElementType : public IfcDistributionFlowElementType {
public:
    IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionChamberElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionChamberElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionChamberElementType> > list;
    typedef IfcTemplatedEntityList<IfcDistributionChamberElementType>::it it;
};
class IfcDistributionControlElementType : public IfcDistributionElementType {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionControlElementType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionControlElementType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElementType> > list;
    typedef IfcTemplatedEntityList<IfcDistributionControlElementType>::it it;
};
class IfcDistributionElement : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionElement>::it it;
};
class IfcDistributionFlowElement : public IfcDistributionElement {
public:
    SHARED_PTR< IfcTemplatedEntityList<IfcRelFlowControlElements> > HasControlElements(); // INVERSE IfcRelFlowControlElements::RelatingFlowElement
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionFlowElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionFlowElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionFlowElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionFlowElement>::it it;
};
class IfcDistributionPort : public IfcPort {
public:
    bool hasFlowDirection();
    IfcFlowDirectionEnum::IfcFlowDirectionEnum FlowDirection();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionPort (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionPort> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionPort> > list;
    typedef IfcTemplatedEntityList<IfcDistributionPort>::it it;
};
class IfcDoor : public IfcBuildingElement {
public:
    bool hasOverallHeight();
    IfcPositiveLengthMeasure OverallHeight();
    bool hasOverallWidth();
    IfcPositiveLengthMeasure OverallWidth();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDoor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDoor> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDoor> > list;
    typedef IfcTemplatedEntityList<IfcDoor>::it it;
};
class IfcDuctFittingType : public IfcFlowFittingType {
public:
    IfcDuctFittingTypeEnum::IfcDuctFittingTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDuctFittingType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDuctFittingType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDuctFittingType> > list;
    typedef IfcTemplatedEntityList<IfcDuctFittingType>::it it;
};
class IfcDuctSegmentType : public IfcFlowSegmentType {
public:
    IfcDuctSegmentTypeEnum::IfcDuctSegmentTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDuctSegmentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDuctSegmentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDuctSegmentType> > list;
    typedef IfcTemplatedEntityList<IfcDuctSegmentType>::it it;
};
class IfcDuctSilencerType : public IfcFlowTreatmentDeviceType {
public:
    IfcDuctSilencerTypeEnum::IfcDuctSilencerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDuctSilencerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDuctSilencerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDuctSilencerType> > list;
    typedef IfcTemplatedEntityList<IfcDuctSilencerType>::it it;
};
class IfcEdgeFeature : public IfcFeatureElementSubtraction {
public:
    bool hasFeatureLength();
    IfcPositiveLengthMeasure FeatureLength();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEdgeFeature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEdgeFeature> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEdgeFeature> > list;
    typedef IfcTemplatedEntityList<IfcEdgeFeature>::it it;
};
class IfcElectricApplianceType : public IfcFlowTerminalType {
public:
    IfcElectricApplianceTypeEnum::IfcElectricApplianceTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricApplianceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricApplianceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricApplianceType> > list;
    typedef IfcTemplatedEntityList<IfcElectricApplianceType>::it it;
};
class IfcElectricFlowStorageDeviceType : public IfcFlowStorageDeviceType {
public:
    IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricFlowStorageDeviceType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricFlowStorageDeviceType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricFlowStorageDeviceType> > list;
    typedef IfcTemplatedEntityList<IfcElectricFlowStorageDeviceType>::it it;
};
class IfcElectricGeneratorType : public IfcEnergyConversionDeviceType {
public:
    IfcElectricGeneratorTypeEnum::IfcElectricGeneratorTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricGeneratorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricGeneratorType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricGeneratorType> > list;
    typedef IfcTemplatedEntityList<IfcElectricGeneratorType>::it it;
};
class IfcElectricHeaterType : public IfcFlowTerminalType {
public:
    IfcElectricHeaterTypeEnum::IfcElectricHeaterTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricHeaterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricHeaterType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricHeaterType> > list;
    typedef IfcTemplatedEntityList<IfcElectricHeaterType>::it it;
};
class IfcElectricMotorType : public IfcEnergyConversionDeviceType {
public:
    IfcElectricMotorTypeEnum::IfcElectricMotorTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricMotorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricMotorType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricMotorType> > list;
    typedef IfcTemplatedEntityList<IfcElectricMotorType>::it it;
};
class IfcElectricTimeControlType : public IfcFlowControllerType {
public:
    IfcElectricTimeControlTypeEnum::IfcElectricTimeControlTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricTimeControlType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricTimeControlType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricTimeControlType> > list;
    typedef IfcTemplatedEntityList<IfcElectricTimeControlType>::it it;
};
class IfcElectricalCircuit : public IfcSystem {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricalCircuit (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricalCircuit> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricalCircuit> > list;
    typedef IfcTemplatedEntityList<IfcElectricalCircuit>::it it;
};
class IfcElectricalElement : public IfcElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricalElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricalElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcElectricalElement> > list;
    typedef IfcTemplatedEntityList<IfcElectricalElement>::it it;
};
class IfcEnergyConversionDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcEnergyConversionDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcEnergyConversionDevice> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcEnergyConversionDevice> > list;
    typedef IfcTemplatedEntityList<IfcEnergyConversionDevice>::it it;
};
class IfcFanType : public IfcFlowMovingDeviceType {
public:
    IfcFanTypeEnum::IfcFanTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFanType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFanType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFanType> > list;
    typedef IfcTemplatedEntityList<IfcFanType>::it it;
};
class IfcFilterType : public IfcFlowTreatmentDeviceType {
public:
    IfcFilterTypeEnum::IfcFilterTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFilterType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFilterType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFilterType> > list;
    typedef IfcTemplatedEntityList<IfcFilterType>::it it;
};
class IfcFireSuppressionTerminalType : public IfcFlowTerminalType {
public:
    IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFireSuppressionTerminalType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFireSuppressionTerminalType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFireSuppressionTerminalType> > list;
    typedef IfcTemplatedEntityList<IfcFireSuppressionTerminalType>::it it;
};
class IfcFlowController : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowController (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowController> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowController> > list;
    typedef IfcTemplatedEntityList<IfcFlowController>::it it;
};
class IfcFlowFitting : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowFitting (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowFitting> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowFitting> > list;
    typedef IfcTemplatedEntityList<IfcFlowFitting>::it it;
};
class IfcFlowInstrumentType : public IfcDistributionControlElementType {
public:
    IfcFlowInstrumentTypeEnum::IfcFlowInstrumentTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowInstrumentType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowInstrumentType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowInstrumentType> > list;
    typedef IfcTemplatedEntityList<IfcFlowInstrumentType>::it it;
};
class IfcFlowMovingDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowMovingDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowMovingDevice> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowMovingDevice> > list;
    typedef IfcTemplatedEntityList<IfcFlowMovingDevice>::it it;
};
class IfcFlowSegment : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowSegment (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowSegment> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowSegment> > list;
    typedef IfcTemplatedEntityList<IfcFlowSegment>::it it;
};
class IfcFlowStorageDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowStorageDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowStorageDevice> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowStorageDevice> > list;
    typedef IfcTemplatedEntityList<IfcFlowStorageDevice>::it it;
};
class IfcFlowTerminal : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowTerminal (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowTerminal> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTerminal> > list;
    typedef IfcTemplatedEntityList<IfcFlowTerminal>::it it;
};
class IfcFlowTreatmentDevice : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFlowTreatmentDevice (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFlowTreatmentDevice> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFlowTreatmentDevice> > list;
    typedef IfcTemplatedEntityList<IfcFlowTreatmentDevice>::it it;
};
class IfcFooting : public IfcBuildingElement {
public:
    IfcFootingTypeEnum::IfcFootingTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcFooting (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcFooting> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcFooting> > list;
    typedef IfcTemplatedEntityList<IfcFooting>::it it;
};
class IfcMember : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcMember (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcMember> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcMember> > list;
    typedef IfcTemplatedEntityList<IfcMember>::it it;
};
class IfcPile : public IfcBuildingElement {
public:
    IfcPileTypeEnum::IfcPileTypeEnum PredefinedType();
    bool hasConstructionType();
    IfcPileConstructionEnum::IfcPileConstructionEnum ConstructionType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPile (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPile> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPile> > list;
    typedef IfcTemplatedEntityList<IfcPile>::it it;
};
class IfcPlate : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcPlate (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcPlate> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcPlate> > list;
    typedef IfcTemplatedEntityList<IfcPlate>::it it;
};
class IfcRailing : public IfcBuildingElement {
public:
    bool hasPredefinedType();
    IfcRailingTypeEnum::IfcRailingTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRailing (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRailing> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRailing> > list;
    typedef IfcTemplatedEntityList<IfcRailing>::it it;
};
class IfcRamp : public IfcBuildingElement {
public:
    IfcRampTypeEnum::IfcRampTypeEnum ShapeType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRamp (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRamp> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRamp> > list;
    typedef IfcTemplatedEntityList<IfcRamp>::it it;
};
class IfcRampFlight : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRampFlight (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRampFlight> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRampFlight> > list;
    typedef IfcTemplatedEntityList<IfcRampFlight>::it it;
};
class IfcRationalBezierCurve : public IfcBezierCurve {
public:
    std::vector<float> /*[2:?]*/ WeightsData();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRationalBezierCurve (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRationalBezierCurve> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRationalBezierCurve> > list;
    typedef IfcTemplatedEntityList<IfcRationalBezierCurve>::it it;
};
class IfcReinforcingElement : public IfcBuildingElementComponent {
public:
    bool hasSteelGrade();
    IfcLabel SteelGrade();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcReinforcingElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcReinforcingElement> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcReinforcingMesh (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcReinforcingMesh> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcingMesh> > list;
    typedef IfcTemplatedEntityList<IfcReinforcingMesh>::it it;
};
class IfcRoof : public IfcBuildingElement {
public:
    IfcRoofTypeEnum::IfcRoofTypeEnum ShapeType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRoof (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRoof> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoof> > list;
    typedef IfcTemplatedEntityList<IfcRoof>::it it;
};
class IfcRoundedEdgeFeature : public IfcEdgeFeature {
public:
    bool hasRadius();
    IfcPositiveLengthMeasure Radius();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcRoundedEdgeFeature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcRoundedEdgeFeature> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcRoundedEdgeFeature> > list;
    typedef IfcTemplatedEntityList<IfcRoundedEdgeFeature>::it it;
};
class IfcSensorType : public IfcDistributionControlElementType {
public:
    IfcSensorTypeEnum::IfcSensorTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSensorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSensorType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSensorType> > list;
    typedef IfcTemplatedEntityList<IfcSensorType>::it it;
};
class IfcSlab : public IfcBuildingElement {
public:
    bool hasPredefinedType();
    IfcSlabTypeEnum::IfcSlabTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcSlab (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcSlab> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcSlab> > list;
    typedef IfcTemplatedEntityList<IfcSlab>::it it;
};
class IfcStair : public IfcBuildingElement {
public:
    IfcStairTypeEnum::IfcStairTypeEnum ShapeType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStair (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStair> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStairFlight (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStairFlight> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcStairFlight> > list;
    typedef IfcTemplatedEntityList<IfcStairFlight>::it it;
};
class IfcStructuralAnalysisModel : public IfcSystem {
public:
    IfcAnalysisModelTypeEnum::IfcAnalysisModelTypeEnum PredefinedType();
    bool hasOrientationOf2DPlane();
    SHARED_PTR<IfcAxis2Placement3D> OrientationOf2DPlane();
    bool hasLoadedBy();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadGroup> > LoadedBy();
    bool hasHasResults();
    SHARED_PTR< IfcTemplatedEntityList<IfcStructuralResultGroup> > HasResults();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcStructuralAnalysisModel (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcStructuralAnalysisModel> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTendon (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTendon> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTendon> > list;
    typedef IfcTemplatedEntityList<IfcTendon>::it it;
};
class IfcTendonAnchor : public IfcReinforcingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcTendonAnchor (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcTendonAnchor> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcTendonAnchor> > list;
    typedef IfcTemplatedEntityList<IfcTendonAnchor>::it it;
};
class IfcVibrationIsolatorType : public IfcDiscreteAccessoryType {
public:
    IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcVibrationIsolatorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcVibrationIsolatorType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcVibrationIsolatorType> > list;
    typedef IfcTemplatedEntityList<IfcVibrationIsolatorType>::it it;
};
class IfcWall : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWall (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWall> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWall> > list;
    typedef IfcTemplatedEntityList<IfcWall>::it it;
};
class IfcWallStandardCase : public IfcWall {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWallStandardCase (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWallStandardCase> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWallStandardCase> > list;
    typedef IfcTemplatedEntityList<IfcWallStandardCase>::it it;
};
class IfcWindow : public IfcBuildingElement {
public:
    bool hasOverallHeight();
    IfcPositiveLengthMeasure OverallHeight();
    bool hasOverallWidth();
    IfcPositiveLengthMeasure OverallWidth();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcWindow (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcWindow> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcWindow> > list;
    typedef IfcTemplatedEntityList<IfcWindow>::it it;
};
class IfcActuatorType : public IfcDistributionControlElementType {
public:
    IfcActuatorTypeEnum::IfcActuatorTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcActuatorType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcActuatorType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcActuatorType> > list;
    typedef IfcTemplatedEntityList<IfcActuatorType>::it it;
};
class IfcAlarmType : public IfcDistributionControlElementType {
public:
    IfcAlarmTypeEnum::IfcAlarmTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcAlarmType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcAlarmType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcAlarmType> > list;
    typedef IfcTemplatedEntityList<IfcAlarmType>::it it;
};
class IfcBeam : public IfcBuildingElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcBeam (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcBeam> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcBeam> > list;
    typedef IfcTemplatedEntityList<IfcBeam>::it it;
};
class IfcChamferEdgeFeature : public IfcEdgeFeature {
public:
    bool hasWidth();
    IfcPositiveLengthMeasure Width();
    bool hasHeight();
    IfcPositiveLengthMeasure Height();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcChamferEdgeFeature (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcChamferEdgeFeature> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcChamferEdgeFeature> > list;
    typedef IfcTemplatedEntityList<IfcChamferEdgeFeature>::it it;
};
class IfcControllerType : public IfcDistributionControlElementType {
public:
    IfcControllerTypeEnum::IfcControllerTypeEnum PredefinedType();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcControllerType (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcControllerType> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcControllerType> > list;
    typedef IfcTemplatedEntityList<IfcControllerType>::it it;
};
class IfcDistributionChamberElement : public IfcDistributionFlowElement {
public:
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionChamberElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionChamberElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionChamberElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionChamberElement>::it it;
};
class IfcDistributionControlElement : public IfcDistributionElement {
public:
    bool hasControlElementId();
    IfcIdentifier ControlElementId();
    SHARED_PTR< IfcTemplatedEntityList<IfcRelFlowControlElements> > AssignedToFlowElement(); // INVERSE IfcRelFlowControlElements::RelatedControlElements
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcDistributionControlElement (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcDistributionControlElement> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElement> > list;
    typedef IfcTemplatedEntityList<IfcDistributionControlElement>::it it;
};
class IfcElectricDistributionPoint : public IfcFlowController {
public:
    IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunctionEnum DistributionPointFunction();
    bool hasUserDefinedFunction();
    IfcLabel UserDefinedFunction();
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcElectricDistributionPoint (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcElectricDistributionPoint> ptr;
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
    bool is(Type::Enum v);
    Type::Enum type();
    static Type::Enum Class();
    IfcReinforcingBar (IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
    typedef SHARED_PTR<IfcReinforcingBar> ptr;
    typedef SHARED_PTR< IfcTemplatedEntityList<IfcReinforcingBar> > list;
    typedef IfcTemplatedEntityList<IfcReinforcingBar>::it it;
};
IfcSchemaEntity SchemaEntity(IfcAbstractEntityPtr e = IfcAbstractEntityPtr());
}

#endif
