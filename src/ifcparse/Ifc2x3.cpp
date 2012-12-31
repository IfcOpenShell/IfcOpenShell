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
 
#include "Ifc2x3.h"
#include "IfcException.h"

using namespace Ifc2x3;
using namespace IfcParse;

IfcSchemaEntity Ifc2x3::SchemaEntity(IfcAbstractEntityPtr e) {
    switch(e->type()){
        case Type::IfcAbsorbedDoseMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcAccelerationMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcAmountOfSubstanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcAngularVelocityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcAreaMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcBoolean: return new IfcEntitySelect(e); break;
        case Type::IfcColour: return new IfcEntitySelect(e); break;
        case Type::IfcComplexNumber: return new IfcEntitySelect(e); break;
        case Type::IfcCompoundPlaneAngleMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcContextDependentMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcCountMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcCurvatureMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcDateTimeSelect: return new IfcEntitySelect(e); break;
        case Type::IfcDerivedMeasureValue: return new IfcEntitySelect(e); break;
        case Type::IfcDescriptiveMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcDoseEquivalentMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcDynamicViscosityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcElectricCapacitanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcElectricChargeMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcElectricConductanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcElectricCurrentMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcElectricResistanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcElectricVoltageMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcEnergyMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcForceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcFrequencyMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcHeatFluxDensityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcHeatingValueMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcIdentifier: return new IfcEntitySelect(e); break;
        case Type::IfcIlluminanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcInductanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcInteger: return new IfcEntitySelect(e); break;
        case Type::IfcIntegerCountRateMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcIonConcentrationMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcIsothermalMoistureCapacityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcKinematicViscosityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLabel: return new IfcEntitySelect(e); break;
        case Type::IfcLengthMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLinearForceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLinearMomentMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLinearStiffnessMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLinearVelocityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLogical: return new IfcEntitySelect(e); break;
        case Type::IfcLuminousFluxMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLuminousIntensityDistributionMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcLuminousIntensityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMagneticFluxDensityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMagneticFluxMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMassDensityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMassFlowRateMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMassMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMassPerLengthMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMeasureValue: return new IfcEntitySelect(e); break;
        case Type::IfcModulusOfElasticityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcModulusOfLinearSubgradeReactionMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcModulusOfRotationalSubgradeReactionMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcModulusOfSubgradeReactionMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMoistureDiffusivityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMolecularWeightMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMomentOfInertiaMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcMonetaryMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcNormalisedRatioMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcNullStyle: return new IfcEntitySelect(e); break;
        case Type::IfcNumericMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcPHMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcParameterValue: return new IfcEntitySelect(e); break;
        case Type::IfcPlanarForceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcPlaneAngleMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcPositiveLengthMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcPositivePlaneAngleMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcPositiveRatioMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcPowerMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcPressureMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcRadioActivityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcRatioMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcReal: return new IfcEntitySelect(e); break;
        case Type::IfcRotationalFrequencyMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcRotationalMassMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcRotationalStiffnessMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcSectionModulusMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcSectionalAreaIntegralMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcShearModulusMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcSimpleValue: return new IfcEntitySelect(e); break;
        case Type::IfcSolidAngleMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcSoundPowerMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcSoundPressureMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcSpecificHeatCapacityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcSpecularExponent: return new IfcEntitySelect(e); break;
        case Type::IfcSpecularRoughness: return new IfcEntitySelect(e); break;
        case Type::IfcTemperatureGradientMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcText: return new IfcEntitySelect(e); break;
        case Type::IfcThermalAdmittanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcThermalConductivityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcThermalExpansionCoefficientMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcThermalResistanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcThermalTransmittanceMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcThermodynamicTemperatureMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcTimeMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcTimeStamp: return new IfcEntitySelect(e); break;
        case Type::IfcTorqueMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcVaporPermeabilityMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcVolumeMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcVolumetricFlowRateMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcWarpingConstantMeasure: return new IfcEntitySelect(e); break;
        case Type::IfcWarpingMomentMeasure: return new IfcEntitySelect(e); break;
        case Type::Ifc2DCompositeCurve: return new Ifc2DCompositeCurve(e); break;
        case Type::IfcActionRequest: return new IfcActionRequest(e); break;
        case Type::IfcActor: return new IfcActor(e); break;
        case Type::IfcActorRole: return new IfcActorRole(e); break;
        case Type::IfcActuatorType: return new IfcActuatorType(e); break;
        case Type::IfcAddress: return new IfcAddress(e); break;
        case Type::IfcAirTerminalBoxType: return new IfcAirTerminalBoxType(e); break;
        case Type::IfcAirTerminalType: return new IfcAirTerminalType(e); break;
        case Type::IfcAirToAirHeatRecoveryType: return new IfcAirToAirHeatRecoveryType(e); break;
        case Type::IfcAlarmType: return new IfcAlarmType(e); break;
        case Type::IfcAngularDimension: return new IfcAngularDimension(e); break;
        case Type::IfcAnnotation: return new IfcAnnotation(e); break;
        case Type::IfcAnnotationCurveOccurrence: return new IfcAnnotationCurveOccurrence(e); break;
        case Type::IfcAnnotationFillArea: return new IfcAnnotationFillArea(e); break;
        case Type::IfcAnnotationFillAreaOccurrence: return new IfcAnnotationFillAreaOccurrence(e); break;
        case Type::IfcAnnotationOccurrence: return new IfcAnnotationOccurrence(e); break;
        case Type::IfcAnnotationSurface: return new IfcAnnotationSurface(e); break;
        case Type::IfcAnnotationSurfaceOccurrence: return new IfcAnnotationSurfaceOccurrence(e); break;
        case Type::IfcAnnotationSymbolOccurrence: return new IfcAnnotationSymbolOccurrence(e); break;
        case Type::IfcAnnotationTextOccurrence: return new IfcAnnotationTextOccurrence(e); break;
        case Type::IfcApplication: return new IfcApplication(e); break;
        case Type::IfcAppliedValue: return new IfcAppliedValue(e); break;
        case Type::IfcAppliedValueRelationship: return new IfcAppliedValueRelationship(e); break;
        case Type::IfcApproval: return new IfcApproval(e); break;
        case Type::IfcApprovalActorRelationship: return new IfcApprovalActorRelationship(e); break;
        case Type::IfcApprovalPropertyRelationship: return new IfcApprovalPropertyRelationship(e); break;
        case Type::IfcApprovalRelationship: return new IfcApprovalRelationship(e); break;
        case Type::IfcArbitraryClosedProfileDef: return new IfcArbitraryClosedProfileDef(e); break;
        case Type::IfcArbitraryOpenProfileDef: return new IfcArbitraryOpenProfileDef(e); break;
        case Type::IfcArbitraryProfileDefWithVoids: return new IfcArbitraryProfileDefWithVoids(e); break;
        case Type::IfcAsset: return new IfcAsset(e); break;
        case Type::IfcAsymmetricIShapeProfileDef: return new IfcAsymmetricIShapeProfileDef(e); break;
        case Type::IfcAxis1Placement: return new IfcAxis1Placement(e); break;
        case Type::IfcAxis2Placement2D: return new IfcAxis2Placement2D(e); break;
        case Type::IfcAxis2Placement3D: return new IfcAxis2Placement3D(e); break;
        case Type::IfcBSplineCurve: return new IfcBSplineCurve(e); break;
        case Type::IfcBeam: return new IfcBeam(e); break;
        case Type::IfcBeamType: return new IfcBeamType(e); break;
        case Type::IfcBezierCurve: return new IfcBezierCurve(e); break;
        case Type::IfcBlobTexture: return new IfcBlobTexture(e); break;
        case Type::IfcBlock: return new IfcBlock(e); break;
        case Type::IfcBoilerType: return new IfcBoilerType(e); break;
        case Type::IfcBooleanClippingResult: return new IfcBooleanClippingResult(e); break;
        case Type::IfcBooleanResult: return new IfcBooleanResult(e); break;
        case Type::IfcBoundaryCondition: return new IfcBoundaryCondition(e); break;
        case Type::IfcBoundaryEdgeCondition: return new IfcBoundaryEdgeCondition(e); break;
        case Type::IfcBoundaryFaceCondition: return new IfcBoundaryFaceCondition(e); break;
        case Type::IfcBoundaryNodeCondition: return new IfcBoundaryNodeCondition(e); break;
        case Type::IfcBoundaryNodeConditionWarping: return new IfcBoundaryNodeConditionWarping(e); break;
        case Type::IfcBoundedCurve: return new IfcBoundedCurve(e); break;
        case Type::IfcBoundedSurface: return new IfcBoundedSurface(e); break;
        case Type::IfcBoundingBox: return new IfcBoundingBox(e); break;
        case Type::IfcBoxedHalfSpace: return new IfcBoxedHalfSpace(e); break;
        case Type::IfcBuilding: return new IfcBuilding(e); break;
        case Type::IfcBuildingElement: return new IfcBuildingElement(e); break;
        case Type::IfcBuildingElementComponent: return new IfcBuildingElementComponent(e); break;
        case Type::IfcBuildingElementPart: return new IfcBuildingElementPart(e); break;
        case Type::IfcBuildingElementProxy: return new IfcBuildingElementProxy(e); break;
        case Type::IfcBuildingElementProxyType: return new IfcBuildingElementProxyType(e); break;
        case Type::IfcBuildingElementType: return new IfcBuildingElementType(e); break;
        case Type::IfcBuildingStorey: return new IfcBuildingStorey(e); break;
        case Type::IfcCShapeProfileDef: return new IfcCShapeProfileDef(e); break;
        case Type::IfcCableCarrierFittingType: return new IfcCableCarrierFittingType(e); break;
        case Type::IfcCableCarrierSegmentType: return new IfcCableCarrierSegmentType(e); break;
        case Type::IfcCableSegmentType: return new IfcCableSegmentType(e); break;
        case Type::IfcCalendarDate: return new IfcCalendarDate(e); break;
        case Type::IfcCartesianPoint: return new IfcCartesianPoint(e); break;
        case Type::IfcCartesianTransformationOperator: return new IfcCartesianTransformationOperator(e); break;
        case Type::IfcCartesianTransformationOperator2D: return new IfcCartesianTransformationOperator2D(e); break;
        case Type::IfcCartesianTransformationOperator2DnonUniform: return new IfcCartesianTransformationOperator2DnonUniform(e); break;
        case Type::IfcCartesianTransformationOperator3D: return new IfcCartesianTransformationOperator3D(e); break;
        case Type::IfcCartesianTransformationOperator3DnonUniform: return new IfcCartesianTransformationOperator3DnonUniform(e); break;
        case Type::IfcCenterLineProfileDef: return new IfcCenterLineProfileDef(e); break;
        case Type::IfcChamferEdgeFeature: return new IfcChamferEdgeFeature(e); break;
        case Type::IfcChillerType: return new IfcChillerType(e); break;
        case Type::IfcCircle: return new IfcCircle(e); break;
        case Type::IfcCircleHollowProfileDef: return new IfcCircleHollowProfileDef(e); break;
        case Type::IfcCircleProfileDef: return new IfcCircleProfileDef(e); break;
        case Type::IfcClassification: return new IfcClassification(e); break;
        case Type::IfcClassificationItem: return new IfcClassificationItem(e); break;
        case Type::IfcClassificationItemRelationship: return new IfcClassificationItemRelationship(e); break;
        case Type::IfcClassificationNotation: return new IfcClassificationNotation(e); break;
        case Type::IfcClassificationNotationFacet: return new IfcClassificationNotationFacet(e); break;
        case Type::IfcClassificationReference: return new IfcClassificationReference(e); break;
        case Type::IfcClosedShell: return new IfcClosedShell(e); break;
        case Type::IfcCoilType: return new IfcCoilType(e); break;
        case Type::IfcColourRgb: return new IfcColourRgb(e); break;
        case Type::IfcColourSpecification: return new IfcColourSpecification(e); break;
        case Type::IfcColumn: return new IfcColumn(e); break;
        case Type::IfcColumnType: return new IfcColumnType(e); break;
        case Type::IfcComplexProperty: return new IfcComplexProperty(e); break;
        case Type::IfcCompositeCurve: return new IfcCompositeCurve(e); break;
        case Type::IfcCompositeCurveSegment: return new IfcCompositeCurveSegment(e); break;
        case Type::IfcCompositeProfileDef: return new IfcCompositeProfileDef(e); break;
        case Type::IfcCompressorType: return new IfcCompressorType(e); break;
        case Type::IfcCondenserType: return new IfcCondenserType(e); break;
        case Type::IfcCondition: return new IfcCondition(e); break;
        case Type::IfcConditionCriterion: return new IfcConditionCriterion(e); break;
        case Type::IfcConic: return new IfcConic(e); break;
        case Type::IfcConnectedFaceSet: return new IfcConnectedFaceSet(e); break;
        case Type::IfcConnectionCurveGeometry: return new IfcConnectionCurveGeometry(e); break;
        case Type::IfcConnectionGeometry: return new IfcConnectionGeometry(e); break;
        case Type::IfcConnectionPointEccentricity: return new IfcConnectionPointEccentricity(e); break;
        case Type::IfcConnectionPointGeometry: return new IfcConnectionPointGeometry(e); break;
        case Type::IfcConnectionPortGeometry: return new IfcConnectionPortGeometry(e); break;
        case Type::IfcConnectionSurfaceGeometry: return new IfcConnectionSurfaceGeometry(e); break;
        case Type::IfcConstraint: return new IfcConstraint(e); break;
        case Type::IfcConstraintAggregationRelationship: return new IfcConstraintAggregationRelationship(e); break;
        case Type::IfcConstraintClassificationRelationship: return new IfcConstraintClassificationRelationship(e); break;
        case Type::IfcConstraintRelationship: return new IfcConstraintRelationship(e); break;
        case Type::IfcConstructionEquipmentResource: return new IfcConstructionEquipmentResource(e); break;
        case Type::IfcConstructionMaterialResource: return new IfcConstructionMaterialResource(e); break;
        case Type::IfcConstructionProductResource: return new IfcConstructionProductResource(e); break;
        case Type::IfcConstructionResource: return new IfcConstructionResource(e); break;
        case Type::IfcContextDependentUnit: return new IfcContextDependentUnit(e); break;
        case Type::IfcControl: return new IfcControl(e); break;
        case Type::IfcControllerType: return new IfcControllerType(e); break;
        case Type::IfcConversionBasedUnit: return new IfcConversionBasedUnit(e); break;
        case Type::IfcCooledBeamType: return new IfcCooledBeamType(e); break;
        case Type::IfcCoolingTowerType: return new IfcCoolingTowerType(e); break;
        case Type::IfcCoordinatedUniversalTimeOffset: return new IfcCoordinatedUniversalTimeOffset(e); break;
        case Type::IfcCostItem: return new IfcCostItem(e); break;
        case Type::IfcCostSchedule: return new IfcCostSchedule(e); break;
        case Type::IfcCostValue: return new IfcCostValue(e); break;
        case Type::IfcCovering: return new IfcCovering(e); break;
        case Type::IfcCoveringType: return new IfcCoveringType(e); break;
        case Type::IfcCraneRailAShapeProfileDef: return new IfcCraneRailAShapeProfileDef(e); break;
        case Type::IfcCraneRailFShapeProfileDef: return new IfcCraneRailFShapeProfileDef(e); break;
        case Type::IfcCrewResource: return new IfcCrewResource(e); break;
        case Type::IfcCsgPrimitive3D: return new IfcCsgPrimitive3D(e); break;
        case Type::IfcCsgSolid: return new IfcCsgSolid(e); break;
        case Type::IfcCurrencyRelationship: return new IfcCurrencyRelationship(e); break;
        case Type::IfcCurtainWall: return new IfcCurtainWall(e); break;
        case Type::IfcCurtainWallType: return new IfcCurtainWallType(e); break;
        case Type::IfcCurve: return new IfcCurve(e); break;
        case Type::IfcCurveBoundedPlane: return new IfcCurveBoundedPlane(e); break;
        case Type::IfcCurveStyle: return new IfcCurveStyle(e); break;
        case Type::IfcCurveStyleFont: return new IfcCurveStyleFont(e); break;
        case Type::IfcCurveStyleFontAndScaling: return new IfcCurveStyleFontAndScaling(e); break;
        case Type::IfcCurveStyleFontPattern: return new IfcCurveStyleFontPattern(e); break;
        case Type::IfcDamperType: return new IfcDamperType(e); break;
        case Type::IfcDateAndTime: return new IfcDateAndTime(e); break;
        case Type::IfcDefinedSymbol: return new IfcDefinedSymbol(e); break;
        case Type::IfcDerivedProfileDef: return new IfcDerivedProfileDef(e); break;
        case Type::IfcDerivedUnit: return new IfcDerivedUnit(e); break;
        case Type::IfcDerivedUnitElement: return new IfcDerivedUnitElement(e); break;
        case Type::IfcDiameterDimension: return new IfcDiameterDimension(e); break;
        case Type::IfcDimensionCalloutRelationship: return new IfcDimensionCalloutRelationship(e); break;
        case Type::IfcDimensionCurve: return new IfcDimensionCurve(e); break;
        case Type::IfcDimensionCurveDirectedCallout: return new IfcDimensionCurveDirectedCallout(e); break;
        case Type::IfcDimensionCurveTerminator: return new IfcDimensionCurveTerminator(e); break;
        case Type::IfcDimensionPair: return new IfcDimensionPair(e); break;
        case Type::IfcDimensionalExponents: return new IfcDimensionalExponents(e); break;
        case Type::IfcDirection: return new IfcDirection(e); break;
        case Type::IfcDiscreteAccessory: return new IfcDiscreteAccessory(e); break;
        case Type::IfcDiscreteAccessoryType: return new IfcDiscreteAccessoryType(e); break;
        case Type::IfcDistributionChamberElement: return new IfcDistributionChamberElement(e); break;
        case Type::IfcDistributionChamberElementType: return new IfcDistributionChamberElementType(e); break;
        case Type::IfcDistributionControlElement: return new IfcDistributionControlElement(e); break;
        case Type::IfcDistributionControlElementType: return new IfcDistributionControlElementType(e); break;
        case Type::IfcDistributionElement: return new IfcDistributionElement(e); break;
        case Type::IfcDistributionElementType: return new IfcDistributionElementType(e); break;
        case Type::IfcDistributionFlowElement: return new IfcDistributionFlowElement(e); break;
        case Type::IfcDistributionFlowElementType: return new IfcDistributionFlowElementType(e); break;
        case Type::IfcDistributionPort: return new IfcDistributionPort(e); break;
        case Type::IfcDocumentElectronicFormat: return new IfcDocumentElectronicFormat(e); break;
        case Type::IfcDocumentInformation: return new IfcDocumentInformation(e); break;
        case Type::IfcDocumentInformationRelationship: return new IfcDocumentInformationRelationship(e); break;
        case Type::IfcDocumentReference: return new IfcDocumentReference(e); break;
        case Type::IfcDoor: return new IfcDoor(e); break;
        case Type::IfcDoorLiningProperties: return new IfcDoorLiningProperties(e); break;
        case Type::IfcDoorPanelProperties: return new IfcDoorPanelProperties(e); break;
        case Type::IfcDoorStyle: return new IfcDoorStyle(e); break;
        case Type::IfcDraughtingCallout: return new IfcDraughtingCallout(e); break;
        case Type::IfcDraughtingCalloutRelationship: return new IfcDraughtingCalloutRelationship(e); break;
        case Type::IfcDraughtingPreDefinedColour: return new IfcDraughtingPreDefinedColour(e); break;
        case Type::IfcDraughtingPreDefinedCurveFont: return new IfcDraughtingPreDefinedCurveFont(e); break;
        case Type::IfcDraughtingPreDefinedTextFont: return new IfcDraughtingPreDefinedTextFont(e); break;
        case Type::IfcDuctFittingType: return new IfcDuctFittingType(e); break;
        case Type::IfcDuctSegmentType: return new IfcDuctSegmentType(e); break;
        case Type::IfcDuctSilencerType: return new IfcDuctSilencerType(e); break;
        case Type::IfcEdge: return new IfcEdge(e); break;
        case Type::IfcEdgeCurve: return new IfcEdgeCurve(e); break;
        case Type::IfcEdgeFeature: return new IfcEdgeFeature(e); break;
        case Type::IfcEdgeLoop: return new IfcEdgeLoop(e); break;
        case Type::IfcElectricApplianceType: return new IfcElectricApplianceType(e); break;
        case Type::IfcElectricDistributionPoint: return new IfcElectricDistributionPoint(e); break;
        case Type::IfcElectricFlowStorageDeviceType: return new IfcElectricFlowStorageDeviceType(e); break;
        case Type::IfcElectricGeneratorType: return new IfcElectricGeneratorType(e); break;
        case Type::IfcElectricHeaterType: return new IfcElectricHeaterType(e); break;
        case Type::IfcElectricMotorType: return new IfcElectricMotorType(e); break;
        case Type::IfcElectricTimeControlType: return new IfcElectricTimeControlType(e); break;
        case Type::IfcElectricalBaseProperties: return new IfcElectricalBaseProperties(e); break;
        case Type::IfcElectricalCircuit: return new IfcElectricalCircuit(e); break;
        case Type::IfcElectricalElement: return new IfcElectricalElement(e); break;
        case Type::IfcElement: return new IfcElement(e); break;
        case Type::IfcElementAssembly: return new IfcElementAssembly(e); break;
        case Type::IfcElementComponent: return new IfcElementComponent(e); break;
        case Type::IfcElementComponentType: return new IfcElementComponentType(e); break;
        case Type::IfcElementQuantity: return new IfcElementQuantity(e); break;
        case Type::IfcElementType: return new IfcElementType(e); break;
        case Type::IfcElementarySurface: return new IfcElementarySurface(e); break;
        case Type::IfcEllipse: return new IfcEllipse(e); break;
        case Type::IfcEllipseProfileDef: return new IfcEllipseProfileDef(e); break;
        case Type::IfcEnergyConversionDevice: return new IfcEnergyConversionDevice(e); break;
        case Type::IfcEnergyConversionDeviceType: return new IfcEnergyConversionDeviceType(e); break;
        case Type::IfcEnergyProperties: return new IfcEnergyProperties(e); break;
        case Type::IfcEnvironmentalImpactValue: return new IfcEnvironmentalImpactValue(e); break;
        case Type::IfcEquipmentElement: return new IfcEquipmentElement(e); break;
        case Type::IfcEquipmentStandard: return new IfcEquipmentStandard(e); break;
        case Type::IfcEvaporativeCoolerType: return new IfcEvaporativeCoolerType(e); break;
        case Type::IfcEvaporatorType: return new IfcEvaporatorType(e); break;
        case Type::IfcExtendedMaterialProperties: return new IfcExtendedMaterialProperties(e); break;
        case Type::IfcExternalReference: return new IfcExternalReference(e); break;
        case Type::IfcExternallyDefinedHatchStyle: return new IfcExternallyDefinedHatchStyle(e); break;
        case Type::IfcExternallyDefinedSurfaceStyle: return new IfcExternallyDefinedSurfaceStyle(e); break;
        case Type::IfcExternallyDefinedSymbol: return new IfcExternallyDefinedSymbol(e); break;
        case Type::IfcExternallyDefinedTextFont: return new IfcExternallyDefinedTextFont(e); break;
        case Type::IfcExtrudedAreaSolid: return new IfcExtrudedAreaSolid(e); break;
        case Type::IfcFace: return new IfcFace(e); break;
        case Type::IfcFaceBasedSurfaceModel: return new IfcFaceBasedSurfaceModel(e); break;
        case Type::IfcFaceBound: return new IfcFaceBound(e); break;
        case Type::IfcFaceOuterBound: return new IfcFaceOuterBound(e); break;
        case Type::IfcFaceSurface: return new IfcFaceSurface(e); break;
        case Type::IfcFacetedBrep: return new IfcFacetedBrep(e); break;
        case Type::IfcFacetedBrepWithVoids: return new IfcFacetedBrepWithVoids(e); break;
        case Type::IfcFailureConnectionCondition: return new IfcFailureConnectionCondition(e); break;
        case Type::IfcFanType: return new IfcFanType(e); break;
        case Type::IfcFastener: return new IfcFastener(e); break;
        case Type::IfcFastenerType: return new IfcFastenerType(e); break;
        case Type::IfcFeatureElement: return new IfcFeatureElement(e); break;
        case Type::IfcFeatureElementAddition: return new IfcFeatureElementAddition(e); break;
        case Type::IfcFeatureElementSubtraction: return new IfcFeatureElementSubtraction(e); break;
        case Type::IfcFillAreaStyle: return new IfcFillAreaStyle(e); break;
        case Type::IfcFillAreaStyleHatching: return new IfcFillAreaStyleHatching(e); break;
        case Type::IfcFillAreaStyleTileSymbolWithStyle: return new IfcFillAreaStyleTileSymbolWithStyle(e); break;
        case Type::IfcFillAreaStyleTiles: return new IfcFillAreaStyleTiles(e); break;
        case Type::IfcFilterType: return new IfcFilterType(e); break;
        case Type::IfcFireSuppressionTerminalType: return new IfcFireSuppressionTerminalType(e); break;
        case Type::IfcFlowController: return new IfcFlowController(e); break;
        case Type::IfcFlowControllerType: return new IfcFlowControllerType(e); break;
        case Type::IfcFlowFitting: return new IfcFlowFitting(e); break;
        case Type::IfcFlowFittingType: return new IfcFlowFittingType(e); break;
        case Type::IfcFlowInstrumentType: return new IfcFlowInstrumentType(e); break;
        case Type::IfcFlowMeterType: return new IfcFlowMeterType(e); break;
        case Type::IfcFlowMovingDevice: return new IfcFlowMovingDevice(e); break;
        case Type::IfcFlowMovingDeviceType: return new IfcFlowMovingDeviceType(e); break;
        case Type::IfcFlowSegment: return new IfcFlowSegment(e); break;
        case Type::IfcFlowSegmentType: return new IfcFlowSegmentType(e); break;
        case Type::IfcFlowStorageDevice: return new IfcFlowStorageDevice(e); break;
        case Type::IfcFlowStorageDeviceType: return new IfcFlowStorageDeviceType(e); break;
        case Type::IfcFlowTerminal: return new IfcFlowTerminal(e); break;
        case Type::IfcFlowTerminalType: return new IfcFlowTerminalType(e); break;
        case Type::IfcFlowTreatmentDevice: return new IfcFlowTreatmentDevice(e); break;
        case Type::IfcFlowTreatmentDeviceType: return new IfcFlowTreatmentDeviceType(e); break;
        case Type::IfcFluidFlowProperties: return new IfcFluidFlowProperties(e); break;
        case Type::IfcFooting: return new IfcFooting(e); break;
        case Type::IfcFuelProperties: return new IfcFuelProperties(e); break;
        case Type::IfcFurnishingElement: return new IfcFurnishingElement(e); break;
        case Type::IfcFurnishingElementType: return new IfcFurnishingElementType(e); break;
        case Type::IfcFurnitureStandard: return new IfcFurnitureStandard(e); break;
        case Type::IfcFurnitureType: return new IfcFurnitureType(e); break;
        case Type::IfcGasTerminalType: return new IfcGasTerminalType(e); break;
        case Type::IfcGeneralMaterialProperties: return new IfcGeneralMaterialProperties(e); break;
        case Type::IfcGeneralProfileProperties: return new IfcGeneralProfileProperties(e); break;
        case Type::IfcGeometricCurveSet: return new IfcGeometricCurveSet(e); break;
        case Type::IfcGeometricRepresentationContext: return new IfcGeometricRepresentationContext(e); break;
        case Type::IfcGeometricRepresentationItem: return new IfcGeometricRepresentationItem(e); break;
        case Type::IfcGeometricRepresentationSubContext: return new IfcGeometricRepresentationSubContext(e); break;
        case Type::IfcGeometricSet: return new IfcGeometricSet(e); break;
        case Type::IfcGrid: return new IfcGrid(e); break;
        case Type::IfcGridAxis: return new IfcGridAxis(e); break;
        case Type::IfcGridPlacement: return new IfcGridPlacement(e); break;
        case Type::IfcGroup: return new IfcGroup(e); break;
        case Type::IfcHalfSpaceSolid: return new IfcHalfSpaceSolid(e); break;
        case Type::IfcHeatExchangerType: return new IfcHeatExchangerType(e); break;
        case Type::IfcHumidifierType: return new IfcHumidifierType(e); break;
        case Type::IfcHygroscopicMaterialProperties: return new IfcHygroscopicMaterialProperties(e); break;
        case Type::IfcIShapeProfileDef: return new IfcIShapeProfileDef(e); break;
        case Type::IfcImageTexture: return new IfcImageTexture(e); break;
        case Type::IfcInventory: return new IfcInventory(e); break;
        case Type::IfcIrregularTimeSeries: return new IfcIrregularTimeSeries(e); break;
        case Type::IfcIrregularTimeSeriesValue: return new IfcIrregularTimeSeriesValue(e); break;
        case Type::IfcJunctionBoxType: return new IfcJunctionBoxType(e); break;
        case Type::IfcLShapeProfileDef: return new IfcLShapeProfileDef(e); break;
        case Type::IfcLaborResource: return new IfcLaborResource(e); break;
        case Type::IfcLampType: return new IfcLampType(e); break;
        case Type::IfcLibraryInformation: return new IfcLibraryInformation(e); break;
        case Type::IfcLibraryReference: return new IfcLibraryReference(e); break;
        case Type::IfcLightDistributionData: return new IfcLightDistributionData(e); break;
        case Type::IfcLightFixtureType: return new IfcLightFixtureType(e); break;
        case Type::IfcLightIntensityDistribution: return new IfcLightIntensityDistribution(e); break;
        case Type::IfcLightSource: return new IfcLightSource(e); break;
        case Type::IfcLightSourceAmbient: return new IfcLightSourceAmbient(e); break;
        case Type::IfcLightSourceDirectional: return new IfcLightSourceDirectional(e); break;
        case Type::IfcLightSourceGoniometric: return new IfcLightSourceGoniometric(e); break;
        case Type::IfcLightSourcePositional: return new IfcLightSourcePositional(e); break;
        case Type::IfcLightSourceSpot: return new IfcLightSourceSpot(e); break;
        case Type::IfcLine: return new IfcLine(e); break;
        case Type::IfcLinearDimension: return new IfcLinearDimension(e); break;
        case Type::IfcLocalPlacement: return new IfcLocalPlacement(e); break;
        case Type::IfcLocalTime: return new IfcLocalTime(e); break;
        case Type::IfcLoop: return new IfcLoop(e); break;
        case Type::IfcManifoldSolidBrep: return new IfcManifoldSolidBrep(e); break;
        case Type::IfcMappedItem: return new IfcMappedItem(e); break;
        case Type::IfcMaterial: return new IfcMaterial(e); break;
        case Type::IfcMaterialClassificationRelationship: return new IfcMaterialClassificationRelationship(e); break;
        case Type::IfcMaterialDefinitionRepresentation: return new IfcMaterialDefinitionRepresentation(e); break;
        case Type::IfcMaterialLayer: return new IfcMaterialLayer(e); break;
        case Type::IfcMaterialLayerSet: return new IfcMaterialLayerSet(e); break;
        case Type::IfcMaterialLayerSetUsage: return new IfcMaterialLayerSetUsage(e); break;
        case Type::IfcMaterialList: return new IfcMaterialList(e); break;
        case Type::IfcMaterialProperties: return new IfcMaterialProperties(e); break;
        case Type::IfcMeasureWithUnit: return new IfcMeasureWithUnit(e); break;
        case Type::IfcMechanicalConcreteMaterialProperties: return new IfcMechanicalConcreteMaterialProperties(e); break;
        case Type::IfcMechanicalFastener: return new IfcMechanicalFastener(e); break;
        case Type::IfcMechanicalFastenerType: return new IfcMechanicalFastenerType(e); break;
        case Type::IfcMechanicalMaterialProperties: return new IfcMechanicalMaterialProperties(e); break;
        case Type::IfcMechanicalSteelMaterialProperties: return new IfcMechanicalSteelMaterialProperties(e); break;
        case Type::IfcMember: return new IfcMember(e); break;
        case Type::IfcMemberType: return new IfcMemberType(e); break;
        case Type::IfcMetric: return new IfcMetric(e); break;
        case Type::IfcMonetaryUnit: return new IfcMonetaryUnit(e); break;
        case Type::IfcMotorConnectionType: return new IfcMotorConnectionType(e); break;
        case Type::IfcMove: return new IfcMove(e); break;
        case Type::IfcNamedUnit: return new IfcNamedUnit(e); break;
        case Type::IfcObject: return new IfcObject(e); break;
        case Type::IfcObjectDefinition: return new IfcObjectDefinition(e); break;
        case Type::IfcObjectPlacement: return new IfcObjectPlacement(e); break;
        case Type::IfcObjective: return new IfcObjective(e); break;
        case Type::IfcOccupant: return new IfcOccupant(e); break;
        case Type::IfcOffsetCurve2D: return new IfcOffsetCurve2D(e); break;
        case Type::IfcOffsetCurve3D: return new IfcOffsetCurve3D(e); break;
        case Type::IfcOneDirectionRepeatFactor: return new IfcOneDirectionRepeatFactor(e); break;
        case Type::IfcOpenShell: return new IfcOpenShell(e); break;
        case Type::IfcOpeningElement: return new IfcOpeningElement(e); break;
        case Type::IfcOpticalMaterialProperties: return new IfcOpticalMaterialProperties(e); break;
        case Type::IfcOrderAction: return new IfcOrderAction(e); break;
        case Type::IfcOrganization: return new IfcOrganization(e); break;
        case Type::IfcOrganizationRelationship: return new IfcOrganizationRelationship(e); break;
        case Type::IfcOrientedEdge: return new IfcOrientedEdge(e); break;
        case Type::IfcOutletType: return new IfcOutletType(e); break;
        case Type::IfcOwnerHistory: return new IfcOwnerHistory(e); break;
        case Type::IfcParameterizedProfileDef: return new IfcParameterizedProfileDef(e); break;
        case Type::IfcPath: return new IfcPath(e); break;
        case Type::IfcPerformanceHistory: return new IfcPerformanceHistory(e); break;
        case Type::IfcPermeableCoveringProperties: return new IfcPermeableCoveringProperties(e); break;
        case Type::IfcPermit: return new IfcPermit(e); break;
        case Type::IfcPerson: return new IfcPerson(e); break;
        case Type::IfcPersonAndOrganization: return new IfcPersonAndOrganization(e); break;
        case Type::IfcPhysicalComplexQuantity: return new IfcPhysicalComplexQuantity(e); break;
        case Type::IfcPhysicalQuantity: return new IfcPhysicalQuantity(e); break;
        case Type::IfcPhysicalSimpleQuantity: return new IfcPhysicalSimpleQuantity(e); break;
        case Type::IfcPile: return new IfcPile(e); break;
        case Type::IfcPipeFittingType: return new IfcPipeFittingType(e); break;
        case Type::IfcPipeSegmentType: return new IfcPipeSegmentType(e); break;
        case Type::IfcPixelTexture: return new IfcPixelTexture(e); break;
        case Type::IfcPlacement: return new IfcPlacement(e); break;
        case Type::IfcPlanarBox: return new IfcPlanarBox(e); break;
        case Type::IfcPlanarExtent: return new IfcPlanarExtent(e); break;
        case Type::IfcPlane: return new IfcPlane(e); break;
        case Type::IfcPlate: return new IfcPlate(e); break;
        case Type::IfcPlateType: return new IfcPlateType(e); break;
        case Type::IfcPoint: return new IfcPoint(e); break;
        case Type::IfcPointOnCurve: return new IfcPointOnCurve(e); break;
        case Type::IfcPointOnSurface: return new IfcPointOnSurface(e); break;
        case Type::IfcPolyLoop: return new IfcPolyLoop(e); break;
        case Type::IfcPolygonalBoundedHalfSpace: return new IfcPolygonalBoundedHalfSpace(e); break;
        case Type::IfcPolyline: return new IfcPolyline(e); break;
        case Type::IfcPort: return new IfcPort(e); break;
        case Type::IfcPostalAddress: return new IfcPostalAddress(e); break;
        case Type::IfcPreDefinedColour: return new IfcPreDefinedColour(e); break;
        case Type::IfcPreDefinedCurveFont: return new IfcPreDefinedCurveFont(e); break;
        case Type::IfcPreDefinedDimensionSymbol: return new IfcPreDefinedDimensionSymbol(e); break;
        case Type::IfcPreDefinedItem: return new IfcPreDefinedItem(e); break;
        case Type::IfcPreDefinedPointMarkerSymbol: return new IfcPreDefinedPointMarkerSymbol(e); break;
        case Type::IfcPreDefinedSymbol: return new IfcPreDefinedSymbol(e); break;
        case Type::IfcPreDefinedTerminatorSymbol: return new IfcPreDefinedTerminatorSymbol(e); break;
        case Type::IfcPreDefinedTextFont: return new IfcPreDefinedTextFont(e); break;
        case Type::IfcPresentationLayerAssignment: return new IfcPresentationLayerAssignment(e); break;
        case Type::IfcPresentationLayerWithStyle: return new IfcPresentationLayerWithStyle(e); break;
        case Type::IfcPresentationStyle: return new IfcPresentationStyle(e); break;
        case Type::IfcPresentationStyleAssignment: return new IfcPresentationStyleAssignment(e); break;
        case Type::IfcProcedure: return new IfcProcedure(e); break;
        case Type::IfcProcess: return new IfcProcess(e); break;
        case Type::IfcProduct: return new IfcProduct(e); break;
        case Type::IfcProductDefinitionShape: return new IfcProductDefinitionShape(e); break;
        case Type::IfcProductRepresentation: return new IfcProductRepresentation(e); break;
        case Type::IfcProductsOfCombustionProperties: return new IfcProductsOfCombustionProperties(e); break;
        case Type::IfcProfileDef: return new IfcProfileDef(e); break;
        case Type::IfcProfileProperties: return new IfcProfileProperties(e); break;
        case Type::IfcProject: return new IfcProject(e); break;
        case Type::IfcProjectOrder: return new IfcProjectOrder(e); break;
        case Type::IfcProjectOrderRecord: return new IfcProjectOrderRecord(e); break;
        case Type::IfcProjectionCurve: return new IfcProjectionCurve(e); break;
        case Type::IfcProjectionElement: return new IfcProjectionElement(e); break;
        case Type::IfcProperty: return new IfcProperty(e); break;
        case Type::IfcPropertyBoundedValue: return new IfcPropertyBoundedValue(e); break;
        case Type::IfcPropertyConstraintRelationship: return new IfcPropertyConstraintRelationship(e); break;
        case Type::IfcPropertyDefinition: return new IfcPropertyDefinition(e); break;
        case Type::IfcPropertyDependencyRelationship: return new IfcPropertyDependencyRelationship(e); break;
        case Type::IfcPropertyEnumeratedValue: return new IfcPropertyEnumeratedValue(e); break;
        case Type::IfcPropertyEnumeration: return new IfcPropertyEnumeration(e); break;
        case Type::IfcPropertyListValue: return new IfcPropertyListValue(e); break;
        case Type::IfcPropertyReferenceValue: return new IfcPropertyReferenceValue(e); break;
        case Type::IfcPropertySet: return new IfcPropertySet(e); break;
        case Type::IfcPropertySetDefinition: return new IfcPropertySetDefinition(e); break;
        case Type::IfcPropertySingleValue: return new IfcPropertySingleValue(e); break;
        case Type::IfcPropertyTableValue: return new IfcPropertyTableValue(e); break;
        case Type::IfcProtectiveDeviceType: return new IfcProtectiveDeviceType(e); break;
        case Type::IfcProxy: return new IfcProxy(e); break;
        case Type::IfcPumpType: return new IfcPumpType(e); break;
        case Type::IfcQuantityArea: return new IfcQuantityArea(e); break;
        case Type::IfcQuantityCount: return new IfcQuantityCount(e); break;
        case Type::IfcQuantityLength: return new IfcQuantityLength(e); break;
        case Type::IfcQuantityTime: return new IfcQuantityTime(e); break;
        case Type::IfcQuantityVolume: return new IfcQuantityVolume(e); break;
        case Type::IfcQuantityWeight: return new IfcQuantityWeight(e); break;
        case Type::IfcRadiusDimension: return new IfcRadiusDimension(e); break;
        case Type::IfcRailing: return new IfcRailing(e); break;
        case Type::IfcRailingType: return new IfcRailingType(e); break;
        case Type::IfcRamp: return new IfcRamp(e); break;
        case Type::IfcRampFlight: return new IfcRampFlight(e); break;
        case Type::IfcRampFlightType: return new IfcRampFlightType(e); break;
        case Type::IfcRationalBezierCurve: return new IfcRationalBezierCurve(e); break;
        case Type::IfcRectangleHollowProfileDef: return new IfcRectangleHollowProfileDef(e); break;
        case Type::IfcRectangleProfileDef: return new IfcRectangleProfileDef(e); break;
        case Type::IfcRectangularPyramid: return new IfcRectangularPyramid(e); break;
        case Type::IfcRectangularTrimmedSurface: return new IfcRectangularTrimmedSurface(e); break;
        case Type::IfcReferencesValueDocument: return new IfcReferencesValueDocument(e); break;
        case Type::IfcRegularTimeSeries: return new IfcRegularTimeSeries(e); break;
        case Type::IfcReinforcementBarProperties: return new IfcReinforcementBarProperties(e); break;
        case Type::IfcReinforcementDefinitionProperties: return new IfcReinforcementDefinitionProperties(e); break;
        case Type::IfcReinforcingBar: return new IfcReinforcingBar(e); break;
        case Type::IfcReinforcingElement: return new IfcReinforcingElement(e); break;
        case Type::IfcReinforcingMesh: return new IfcReinforcingMesh(e); break;
        case Type::IfcRelAggregates: return new IfcRelAggregates(e); break;
        case Type::IfcRelAssigns: return new IfcRelAssigns(e); break;
        case Type::IfcRelAssignsTasks: return new IfcRelAssignsTasks(e); break;
        case Type::IfcRelAssignsToActor: return new IfcRelAssignsToActor(e); break;
        case Type::IfcRelAssignsToControl: return new IfcRelAssignsToControl(e); break;
        case Type::IfcRelAssignsToGroup: return new IfcRelAssignsToGroup(e); break;
        case Type::IfcRelAssignsToProcess: return new IfcRelAssignsToProcess(e); break;
        case Type::IfcRelAssignsToProduct: return new IfcRelAssignsToProduct(e); break;
        case Type::IfcRelAssignsToProjectOrder: return new IfcRelAssignsToProjectOrder(e); break;
        case Type::IfcRelAssignsToResource: return new IfcRelAssignsToResource(e); break;
        case Type::IfcRelAssociates: return new IfcRelAssociates(e); break;
        case Type::IfcRelAssociatesAppliedValue: return new IfcRelAssociatesAppliedValue(e); break;
        case Type::IfcRelAssociatesApproval: return new IfcRelAssociatesApproval(e); break;
        case Type::IfcRelAssociatesClassification: return new IfcRelAssociatesClassification(e); break;
        case Type::IfcRelAssociatesConstraint: return new IfcRelAssociatesConstraint(e); break;
        case Type::IfcRelAssociatesDocument: return new IfcRelAssociatesDocument(e); break;
        case Type::IfcRelAssociatesLibrary: return new IfcRelAssociatesLibrary(e); break;
        case Type::IfcRelAssociatesMaterial: return new IfcRelAssociatesMaterial(e); break;
        case Type::IfcRelAssociatesProfileProperties: return new IfcRelAssociatesProfileProperties(e); break;
        case Type::IfcRelConnects: return new IfcRelConnects(e); break;
        case Type::IfcRelConnectsElements: return new IfcRelConnectsElements(e); break;
        case Type::IfcRelConnectsPathElements: return new IfcRelConnectsPathElements(e); break;
        case Type::IfcRelConnectsPortToElement: return new IfcRelConnectsPortToElement(e); break;
        case Type::IfcRelConnectsPorts: return new IfcRelConnectsPorts(e); break;
        case Type::IfcRelConnectsStructuralActivity: return new IfcRelConnectsStructuralActivity(e); break;
        case Type::IfcRelConnectsStructuralElement: return new IfcRelConnectsStructuralElement(e); break;
        case Type::IfcRelConnectsStructuralMember: return new IfcRelConnectsStructuralMember(e); break;
        case Type::IfcRelConnectsWithEccentricity: return new IfcRelConnectsWithEccentricity(e); break;
        case Type::IfcRelConnectsWithRealizingElements: return new IfcRelConnectsWithRealizingElements(e); break;
        case Type::IfcRelContainedInSpatialStructure: return new IfcRelContainedInSpatialStructure(e); break;
        case Type::IfcRelCoversBldgElements: return new IfcRelCoversBldgElements(e); break;
        case Type::IfcRelCoversSpaces: return new IfcRelCoversSpaces(e); break;
        case Type::IfcRelDecomposes: return new IfcRelDecomposes(e); break;
        case Type::IfcRelDefines: return new IfcRelDefines(e); break;
        case Type::IfcRelDefinesByProperties: return new IfcRelDefinesByProperties(e); break;
        case Type::IfcRelDefinesByType: return new IfcRelDefinesByType(e); break;
        case Type::IfcRelFillsElement: return new IfcRelFillsElement(e); break;
        case Type::IfcRelFlowControlElements: return new IfcRelFlowControlElements(e); break;
        case Type::IfcRelInteractionRequirements: return new IfcRelInteractionRequirements(e); break;
        case Type::IfcRelNests: return new IfcRelNests(e); break;
        case Type::IfcRelOccupiesSpaces: return new IfcRelOccupiesSpaces(e); break;
        case Type::IfcRelOverridesProperties: return new IfcRelOverridesProperties(e); break;
        case Type::IfcRelProjectsElement: return new IfcRelProjectsElement(e); break;
        case Type::IfcRelReferencedInSpatialStructure: return new IfcRelReferencedInSpatialStructure(e); break;
        case Type::IfcRelSchedulesCostItems: return new IfcRelSchedulesCostItems(e); break;
        case Type::IfcRelSequence: return new IfcRelSequence(e); break;
        case Type::IfcRelServicesBuildings: return new IfcRelServicesBuildings(e); break;
        case Type::IfcRelSpaceBoundary: return new IfcRelSpaceBoundary(e); break;
        case Type::IfcRelVoidsElement: return new IfcRelVoidsElement(e); break;
        case Type::IfcRelationship: return new IfcRelationship(e); break;
        case Type::IfcRelaxation: return new IfcRelaxation(e); break;
        case Type::IfcRepresentation: return new IfcRepresentation(e); break;
        case Type::IfcRepresentationContext: return new IfcRepresentationContext(e); break;
        case Type::IfcRepresentationItem: return new IfcRepresentationItem(e); break;
        case Type::IfcRepresentationMap: return new IfcRepresentationMap(e); break;
        case Type::IfcResource: return new IfcResource(e); break;
        case Type::IfcRevolvedAreaSolid: return new IfcRevolvedAreaSolid(e); break;
        case Type::IfcRibPlateProfileProperties: return new IfcRibPlateProfileProperties(e); break;
        case Type::IfcRightCircularCone: return new IfcRightCircularCone(e); break;
        case Type::IfcRightCircularCylinder: return new IfcRightCircularCylinder(e); break;
        case Type::IfcRoof: return new IfcRoof(e); break;
        case Type::IfcRoot: return new IfcRoot(e); break;
        case Type::IfcRoundedEdgeFeature: return new IfcRoundedEdgeFeature(e); break;
        case Type::IfcRoundedRectangleProfileDef: return new IfcRoundedRectangleProfileDef(e); break;
        case Type::IfcSIUnit: return new IfcSIUnit(e); break;
        case Type::IfcSanitaryTerminalType: return new IfcSanitaryTerminalType(e); break;
        case Type::IfcScheduleTimeControl: return new IfcScheduleTimeControl(e); break;
        case Type::IfcSectionProperties: return new IfcSectionProperties(e); break;
        case Type::IfcSectionReinforcementProperties: return new IfcSectionReinforcementProperties(e); break;
        case Type::IfcSectionedSpine: return new IfcSectionedSpine(e); break;
        case Type::IfcSensorType: return new IfcSensorType(e); break;
        case Type::IfcServiceLife: return new IfcServiceLife(e); break;
        case Type::IfcServiceLifeFactor: return new IfcServiceLifeFactor(e); break;
        case Type::IfcShapeAspect: return new IfcShapeAspect(e); break;
        case Type::IfcShapeModel: return new IfcShapeModel(e); break;
        case Type::IfcShapeRepresentation: return new IfcShapeRepresentation(e); break;
        case Type::IfcShellBasedSurfaceModel: return new IfcShellBasedSurfaceModel(e); break;
        case Type::IfcSimpleProperty: return new IfcSimpleProperty(e); break;
        case Type::IfcSite: return new IfcSite(e); break;
        case Type::IfcSlab: return new IfcSlab(e); break;
        case Type::IfcSlabType: return new IfcSlabType(e); break;
        case Type::IfcSlippageConnectionCondition: return new IfcSlippageConnectionCondition(e); break;
        case Type::IfcSolidModel: return new IfcSolidModel(e); break;
        case Type::IfcSoundProperties: return new IfcSoundProperties(e); break;
        case Type::IfcSoundValue: return new IfcSoundValue(e); break;
        case Type::IfcSpace: return new IfcSpace(e); break;
        case Type::IfcSpaceHeaterType: return new IfcSpaceHeaterType(e); break;
        case Type::IfcSpaceProgram: return new IfcSpaceProgram(e); break;
        case Type::IfcSpaceThermalLoadProperties: return new IfcSpaceThermalLoadProperties(e); break;
        case Type::IfcSpaceType: return new IfcSpaceType(e); break;
        case Type::IfcSpatialStructureElement: return new IfcSpatialStructureElement(e); break;
        case Type::IfcSpatialStructureElementType: return new IfcSpatialStructureElementType(e); break;
        case Type::IfcSphere: return new IfcSphere(e); break;
        case Type::IfcStackTerminalType: return new IfcStackTerminalType(e); break;
        case Type::IfcStair: return new IfcStair(e); break;
        case Type::IfcStairFlight: return new IfcStairFlight(e); break;
        case Type::IfcStairFlightType: return new IfcStairFlightType(e); break;
        case Type::IfcStructuralAction: return new IfcStructuralAction(e); break;
        case Type::IfcStructuralActivity: return new IfcStructuralActivity(e); break;
        case Type::IfcStructuralAnalysisModel: return new IfcStructuralAnalysisModel(e); break;
        case Type::IfcStructuralConnection: return new IfcStructuralConnection(e); break;
        case Type::IfcStructuralConnectionCondition: return new IfcStructuralConnectionCondition(e); break;
        case Type::IfcStructuralCurveConnection: return new IfcStructuralCurveConnection(e); break;
        case Type::IfcStructuralCurveMember: return new IfcStructuralCurveMember(e); break;
        case Type::IfcStructuralCurveMemberVarying: return new IfcStructuralCurveMemberVarying(e); break;
        case Type::IfcStructuralItem: return new IfcStructuralItem(e); break;
        case Type::IfcStructuralLinearAction: return new IfcStructuralLinearAction(e); break;
        case Type::IfcStructuralLinearActionVarying: return new IfcStructuralLinearActionVarying(e); break;
        case Type::IfcStructuralLoad: return new IfcStructuralLoad(e); break;
        case Type::IfcStructuralLoadGroup: return new IfcStructuralLoadGroup(e); break;
        case Type::IfcStructuralLoadLinearForce: return new IfcStructuralLoadLinearForce(e); break;
        case Type::IfcStructuralLoadPlanarForce: return new IfcStructuralLoadPlanarForce(e); break;
        case Type::IfcStructuralLoadSingleDisplacement: return new IfcStructuralLoadSingleDisplacement(e); break;
        case Type::IfcStructuralLoadSingleDisplacementDistortion: return new IfcStructuralLoadSingleDisplacementDistortion(e); break;
        case Type::IfcStructuralLoadSingleForce: return new IfcStructuralLoadSingleForce(e); break;
        case Type::IfcStructuralLoadSingleForceWarping: return new IfcStructuralLoadSingleForceWarping(e); break;
        case Type::IfcStructuralLoadStatic: return new IfcStructuralLoadStatic(e); break;
        case Type::IfcStructuralLoadTemperature: return new IfcStructuralLoadTemperature(e); break;
        case Type::IfcStructuralMember: return new IfcStructuralMember(e); break;
        case Type::IfcStructuralPlanarAction: return new IfcStructuralPlanarAction(e); break;
        case Type::IfcStructuralPlanarActionVarying: return new IfcStructuralPlanarActionVarying(e); break;
        case Type::IfcStructuralPointAction: return new IfcStructuralPointAction(e); break;
        case Type::IfcStructuralPointConnection: return new IfcStructuralPointConnection(e); break;
        case Type::IfcStructuralPointReaction: return new IfcStructuralPointReaction(e); break;
        case Type::IfcStructuralProfileProperties: return new IfcStructuralProfileProperties(e); break;
        case Type::IfcStructuralReaction: return new IfcStructuralReaction(e); break;
        case Type::IfcStructuralResultGroup: return new IfcStructuralResultGroup(e); break;
        case Type::IfcStructuralSteelProfileProperties: return new IfcStructuralSteelProfileProperties(e); break;
        case Type::IfcStructuralSurfaceConnection: return new IfcStructuralSurfaceConnection(e); break;
        case Type::IfcStructuralSurfaceMember: return new IfcStructuralSurfaceMember(e); break;
        case Type::IfcStructuralSurfaceMemberVarying: return new IfcStructuralSurfaceMemberVarying(e); break;
        case Type::IfcStructuredDimensionCallout: return new IfcStructuredDimensionCallout(e); break;
        case Type::IfcStyleModel: return new IfcStyleModel(e); break;
        case Type::IfcStyledItem: return new IfcStyledItem(e); break;
        case Type::IfcStyledRepresentation: return new IfcStyledRepresentation(e); break;
        case Type::IfcSubContractResource: return new IfcSubContractResource(e); break;
        case Type::IfcSubedge: return new IfcSubedge(e); break;
        case Type::IfcSurface: return new IfcSurface(e); break;
        case Type::IfcSurfaceCurveSweptAreaSolid: return new IfcSurfaceCurveSweptAreaSolid(e); break;
        case Type::IfcSurfaceOfLinearExtrusion: return new IfcSurfaceOfLinearExtrusion(e); break;
        case Type::IfcSurfaceOfRevolution: return new IfcSurfaceOfRevolution(e); break;
        case Type::IfcSurfaceStyle: return new IfcSurfaceStyle(e); break;
        case Type::IfcSurfaceStyleLighting: return new IfcSurfaceStyleLighting(e); break;
        case Type::IfcSurfaceStyleRefraction: return new IfcSurfaceStyleRefraction(e); break;
        case Type::IfcSurfaceStyleRendering: return new IfcSurfaceStyleRendering(e); break;
        case Type::IfcSurfaceStyleShading: return new IfcSurfaceStyleShading(e); break;
        case Type::IfcSurfaceStyleWithTextures: return new IfcSurfaceStyleWithTextures(e); break;
        case Type::IfcSurfaceTexture: return new IfcSurfaceTexture(e); break;
        case Type::IfcSweptAreaSolid: return new IfcSweptAreaSolid(e); break;
        case Type::IfcSweptDiskSolid: return new IfcSweptDiskSolid(e); break;
        case Type::IfcSweptSurface: return new IfcSweptSurface(e); break;
        case Type::IfcSwitchingDeviceType: return new IfcSwitchingDeviceType(e); break;
        case Type::IfcSymbolStyle: return new IfcSymbolStyle(e); break;
        case Type::IfcSystem: return new IfcSystem(e); break;
        case Type::IfcSystemFurnitureElementType: return new IfcSystemFurnitureElementType(e); break;
        case Type::IfcTShapeProfileDef: return new IfcTShapeProfileDef(e); break;
        case Type::IfcTable: return new IfcTable(e); break;
        case Type::IfcTableRow: return new IfcTableRow(e); break;
        case Type::IfcTankType: return new IfcTankType(e); break;
        case Type::IfcTask: return new IfcTask(e); break;
        case Type::IfcTelecomAddress: return new IfcTelecomAddress(e); break;
        case Type::IfcTendon: return new IfcTendon(e); break;
        case Type::IfcTendonAnchor: return new IfcTendonAnchor(e); break;
        case Type::IfcTerminatorSymbol: return new IfcTerminatorSymbol(e); break;
        case Type::IfcTextLiteral: return new IfcTextLiteral(e); break;
        case Type::IfcTextLiteralWithExtent: return new IfcTextLiteralWithExtent(e); break;
        case Type::IfcTextStyle: return new IfcTextStyle(e); break;
        case Type::IfcTextStyleFontModel: return new IfcTextStyleFontModel(e); break;
        case Type::IfcTextStyleForDefinedFont: return new IfcTextStyleForDefinedFont(e); break;
        case Type::IfcTextStyleTextModel: return new IfcTextStyleTextModel(e); break;
        case Type::IfcTextStyleWithBoxCharacteristics: return new IfcTextStyleWithBoxCharacteristics(e); break;
        case Type::IfcTextureCoordinate: return new IfcTextureCoordinate(e); break;
        case Type::IfcTextureCoordinateGenerator: return new IfcTextureCoordinateGenerator(e); break;
        case Type::IfcTextureMap: return new IfcTextureMap(e); break;
        case Type::IfcTextureVertex: return new IfcTextureVertex(e); break;
        case Type::IfcThermalMaterialProperties: return new IfcThermalMaterialProperties(e); break;
        case Type::IfcTimeSeries: return new IfcTimeSeries(e); break;
        case Type::IfcTimeSeriesReferenceRelationship: return new IfcTimeSeriesReferenceRelationship(e); break;
        case Type::IfcTimeSeriesSchedule: return new IfcTimeSeriesSchedule(e); break;
        case Type::IfcTimeSeriesValue: return new IfcTimeSeriesValue(e); break;
        case Type::IfcTopologicalRepresentationItem: return new IfcTopologicalRepresentationItem(e); break;
        case Type::IfcTopologyRepresentation: return new IfcTopologyRepresentation(e); break;
        case Type::IfcTransformerType: return new IfcTransformerType(e); break;
        case Type::IfcTransportElement: return new IfcTransportElement(e); break;
        case Type::IfcTransportElementType: return new IfcTransportElementType(e); break;
        case Type::IfcTrapeziumProfileDef: return new IfcTrapeziumProfileDef(e); break;
        case Type::IfcTrimmedCurve: return new IfcTrimmedCurve(e); break;
        case Type::IfcTubeBundleType: return new IfcTubeBundleType(e); break;
        case Type::IfcTwoDirectionRepeatFactor: return new IfcTwoDirectionRepeatFactor(e); break;
        case Type::IfcTypeObject: return new IfcTypeObject(e); break;
        case Type::IfcTypeProduct: return new IfcTypeProduct(e); break;
        case Type::IfcUShapeProfileDef: return new IfcUShapeProfileDef(e); break;
        case Type::IfcUnitAssignment: return new IfcUnitAssignment(e); break;
        case Type::IfcUnitaryEquipmentType: return new IfcUnitaryEquipmentType(e); break;
        case Type::IfcValveType: return new IfcValveType(e); break;
        case Type::IfcVector: return new IfcVector(e); break;
        case Type::IfcVertex: return new IfcVertex(e); break;
        case Type::IfcVertexBasedTextureMap: return new IfcVertexBasedTextureMap(e); break;
        case Type::IfcVertexLoop: return new IfcVertexLoop(e); break;
        case Type::IfcVertexPoint: return new IfcVertexPoint(e); break;
        case Type::IfcVibrationIsolatorType: return new IfcVibrationIsolatorType(e); break;
        case Type::IfcVirtualElement: return new IfcVirtualElement(e); break;
        case Type::IfcVirtualGridIntersection: return new IfcVirtualGridIntersection(e); break;
        case Type::IfcWall: return new IfcWall(e); break;
        case Type::IfcWallStandardCase: return new IfcWallStandardCase(e); break;
        case Type::IfcWallType: return new IfcWallType(e); break;
        case Type::IfcWasteTerminalType: return new IfcWasteTerminalType(e); break;
        case Type::IfcWaterProperties: return new IfcWaterProperties(e); break;
        case Type::IfcWindow: return new IfcWindow(e); break;
        case Type::IfcWindowLiningProperties: return new IfcWindowLiningProperties(e); break;
        case Type::IfcWindowPanelProperties: return new IfcWindowPanelProperties(e); break;
        case Type::IfcWindowStyle: return new IfcWindowStyle(e); break;
        case Type::IfcWorkControl: return new IfcWorkControl(e); break;
        case Type::IfcWorkPlan: return new IfcWorkPlan(e); break;
        case Type::IfcWorkSchedule: return new IfcWorkSchedule(e); break;
        case Type::IfcZShapeProfileDef: return new IfcZShapeProfileDef(e); break;
        case Type::IfcZone: return new IfcZone(e); break;
        default: throw IfcException("Unable to find find keyword in schema"); break; 
    }
}

std::string Type::ToString(Enum v) {
    if (v < 0 || v >= 758) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "IfcAbsorbedDoseMeasure","IfcAccelerationMeasure","IfcAmountOfSubstanceMeasure","IfcAngularVelocityMeasure","IfcAreaMeasure","IfcBoolean","IfcColour","IfcComplexNumber","IfcCompoundPlaneAngleMeasure","IfcContextDependentMeasure","IfcCountMeasure","IfcCurvatureMeasure","IfcDateTimeSelect","IfcDerivedMeasureValue","IfcDescriptiveMeasure","IfcDoseEquivalentMeasure","IfcDynamicViscosityMeasure","IfcElectricCapacitanceMeasure","IfcElectricChargeMeasure","IfcElectricConductanceMeasure","IfcElectricCurrentMeasure","IfcElectricResistanceMeasure","IfcElectricVoltageMeasure","IfcEnergyMeasure","IfcForceMeasure","IfcFrequencyMeasure","IfcHeatFluxDensityMeasure","IfcHeatingValueMeasure","IfcIdentifier","IfcIlluminanceMeasure","IfcInductanceMeasure","IfcInteger","IfcIntegerCountRateMeasure","IfcIonConcentrationMeasure","IfcIsothermalMoistureCapacityMeasure","IfcKinematicViscosityMeasure","IfcLabel","IfcLengthMeasure","IfcLinearForceMeasure","IfcLinearMomentMeasure","IfcLinearStiffnessMeasure","IfcLinearVelocityMeasure","IfcLogical","IfcLuminousFluxMeasure","IfcLuminousIntensityDistributionMeasure","IfcLuminousIntensityMeasure","IfcMagneticFluxDensityMeasure","IfcMagneticFluxMeasure","IfcMassDensityMeasure","IfcMassFlowRateMeasure","IfcMassMeasure","IfcMassPerLengthMeasure","IfcMeasureValue","IfcModulusOfElasticityMeasure","IfcModulusOfLinearSubgradeReactionMeasure","IfcModulusOfRotationalSubgradeReactionMeasure","IfcModulusOfSubgradeReactionMeasure","IfcMoistureDiffusivityMeasure","IfcMolecularWeightMeasure","IfcMomentOfInertiaMeasure","IfcMonetaryMeasure","IfcNormalisedRatioMeasure","IfcNullStyle","IfcNumericMeasure","IfcPHMeasure","IfcParameterValue","IfcPlanarForceMeasure","IfcPlaneAngleMeasure","IfcPositiveLengthMeasure","IfcPositivePlaneAngleMeasure","IfcPositiveRatioMeasure","IfcPowerMeasure","IfcPressureMeasure","IfcRadioActivityMeasure","IfcRatioMeasure","IfcReal","IfcRotationalFrequencyMeasure","IfcRotationalMassMeasure","IfcRotationalStiffnessMeasure","IfcSectionModulusMeasure","IfcSectionalAreaIntegralMeasure","IfcShearModulusMeasure","IfcSimpleValue","IfcSolidAngleMeasure","IfcSoundPowerMeasure","IfcSoundPressureMeasure","IfcSpecificHeatCapacityMeasure","IfcSpecularExponent","IfcSpecularRoughness","IfcTemperatureGradientMeasure","IfcText","IfcThermalAdmittanceMeasure","IfcThermalConductivityMeasure","IfcThermalExpansionCoefficientMeasure","IfcThermalResistanceMeasure","IfcThermalTransmittanceMeasure","IfcThermodynamicTemperatureMeasure","IfcTimeMeasure","IfcTimeStamp","IfcTorqueMeasure","IfcVaporPermeabilityMeasure","IfcVolumeMeasure","IfcVolumetricFlowRateMeasure","IfcWarpingConstantMeasure","IfcWarpingMomentMeasure","Ifc2DCompositeCurve","IfcActionRequest","IfcActor","IfcActorRole","IfcActuatorType","IfcAddress","IfcAirTerminalBoxType","IfcAirTerminalType","IfcAirToAirHeatRecoveryType","IfcAlarmType","IfcAngularDimension","IfcAnnotation","IfcAnnotationCurveOccurrence","IfcAnnotationFillArea","IfcAnnotationFillAreaOccurrence","IfcAnnotationOccurrence","IfcAnnotationSurface","IfcAnnotationSurfaceOccurrence","IfcAnnotationSymbolOccurrence","IfcAnnotationTextOccurrence","IfcApplication","IfcAppliedValue","IfcAppliedValueRelationship","IfcApproval","IfcApprovalActorRelationship","IfcApprovalPropertyRelationship","IfcApprovalRelationship","IfcArbitraryClosedProfileDef","IfcArbitraryOpenProfileDef","IfcArbitraryProfileDefWithVoids","IfcAsset","IfcAsymmetricIShapeProfileDef","IfcAxis1Placement","IfcAxis2Placement2D","IfcAxis2Placement3D","IfcBSplineCurve","IfcBeam","IfcBeamType","IfcBezierCurve","IfcBlobTexture","IfcBlock","IfcBoilerType","IfcBooleanClippingResult","IfcBooleanResult","IfcBoundaryCondition","IfcBoundaryEdgeCondition","IfcBoundaryFaceCondition","IfcBoundaryNodeCondition","IfcBoundaryNodeConditionWarping","IfcBoundedCurve","IfcBoundedSurface","IfcBoundingBox","IfcBoxedHalfSpace","IfcBuilding","IfcBuildingElement","IfcBuildingElementComponent","IfcBuildingElementPart","IfcBuildingElementProxy","IfcBuildingElementProxyType","IfcBuildingElementType","IfcBuildingStorey","IfcCShapeProfileDef","IfcCableCarrierFittingType","IfcCableCarrierSegmentType","IfcCableSegmentType","IfcCalendarDate","IfcCartesianPoint","IfcCartesianTransformationOperator","IfcCartesianTransformationOperator2D","IfcCartesianTransformationOperator2DnonUniform","IfcCartesianTransformationOperator3D","IfcCartesianTransformationOperator3DnonUniform","IfcCenterLineProfileDef","IfcChamferEdgeFeature","IfcChillerType","IfcCircle","IfcCircleHollowProfileDef","IfcCircleProfileDef","IfcClassification","IfcClassificationItem","IfcClassificationItemRelationship","IfcClassificationNotation","IfcClassificationNotationFacet","IfcClassificationReference","IfcClosedShell","IfcCoilType","IfcColourRgb","IfcColourSpecification","IfcColumn","IfcColumnType","IfcComplexProperty","IfcCompositeCurve","IfcCompositeCurveSegment","IfcCompositeProfileDef","IfcCompressorType","IfcCondenserType","IfcCondition","IfcConditionCriterion","IfcConic","IfcConnectedFaceSet","IfcConnectionCurveGeometry","IfcConnectionGeometry","IfcConnectionPointEccentricity","IfcConnectionPointGeometry","IfcConnectionPortGeometry","IfcConnectionSurfaceGeometry","IfcConstraint","IfcConstraintAggregationRelationship","IfcConstraintClassificationRelationship","IfcConstraintRelationship","IfcConstructionEquipmentResource","IfcConstructionMaterialResource","IfcConstructionProductResource","IfcConstructionResource","IfcContextDependentUnit","IfcControl","IfcControllerType","IfcConversionBasedUnit","IfcCooledBeamType","IfcCoolingTowerType","IfcCoordinatedUniversalTimeOffset","IfcCostItem","IfcCostSchedule","IfcCostValue","IfcCovering","IfcCoveringType","IfcCraneRailAShapeProfileDef","IfcCraneRailFShapeProfileDef","IfcCrewResource","IfcCsgPrimitive3D","IfcCsgSolid","IfcCurrencyRelationship","IfcCurtainWall","IfcCurtainWallType","IfcCurve","IfcCurveBoundedPlane","IfcCurveStyle","IfcCurveStyleFont","IfcCurveStyleFontAndScaling","IfcCurveStyleFontPattern","IfcDamperType","IfcDateAndTime","IfcDefinedSymbol","IfcDerivedProfileDef","IfcDerivedUnit","IfcDerivedUnitElement","IfcDiameterDimension","IfcDimensionCalloutRelationship","IfcDimensionCurve","IfcDimensionCurveDirectedCallout","IfcDimensionCurveTerminator","IfcDimensionPair","IfcDimensionalExponents","IfcDirection","IfcDiscreteAccessory","IfcDiscreteAccessoryType","IfcDistributionChamberElement","IfcDistributionChamberElementType","IfcDistributionControlElement","IfcDistributionControlElementType","IfcDistributionElement","IfcDistributionElementType","IfcDistributionFlowElement","IfcDistributionFlowElementType","IfcDistributionPort","IfcDocumentElectronicFormat","IfcDocumentInformation","IfcDocumentInformationRelationship","IfcDocumentReference","IfcDoor","IfcDoorLiningProperties","IfcDoorPanelProperties","IfcDoorStyle","IfcDraughtingCallout","IfcDraughtingCalloutRelationship","IfcDraughtingPreDefinedColour","IfcDraughtingPreDefinedCurveFont","IfcDraughtingPreDefinedTextFont","IfcDuctFittingType","IfcDuctSegmentType","IfcDuctSilencerType","IfcEdge","IfcEdgeCurve","IfcEdgeFeature","IfcEdgeLoop","IfcElectricApplianceType","IfcElectricDistributionPoint","IfcElectricFlowStorageDeviceType","IfcElectricGeneratorType","IfcElectricHeaterType","IfcElectricMotorType","IfcElectricTimeControlType","IfcElectricalBaseProperties","IfcElectricalCircuit","IfcElectricalElement","IfcElement","IfcElementAssembly","IfcElementComponent","IfcElementComponentType","IfcElementQuantity","IfcElementType","IfcElementarySurface","IfcEllipse","IfcEllipseProfileDef","IfcEnergyConversionDevice","IfcEnergyConversionDeviceType","IfcEnergyProperties","IfcEnvironmentalImpactValue","IfcEquipmentElement","IfcEquipmentStandard","IfcEvaporativeCoolerType","IfcEvaporatorType","IfcExtendedMaterialProperties","IfcExternalReference","IfcExternallyDefinedHatchStyle","IfcExternallyDefinedSurfaceStyle","IfcExternallyDefinedSymbol","IfcExternallyDefinedTextFont","IfcExtrudedAreaSolid","IfcFace","IfcFaceBasedSurfaceModel","IfcFaceBound","IfcFaceOuterBound","IfcFaceSurface","IfcFacetedBrep","IfcFacetedBrepWithVoids","IfcFailureConnectionCondition","IfcFanType","IfcFastener","IfcFastenerType","IfcFeatureElement","IfcFeatureElementAddition","IfcFeatureElementSubtraction","IfcFillAreaStyle","IfcFillAreaStyleHatching","IfcFillAreaStyleTileSymbolWithStyle","IfcFillAreaStyleTiles","IfcFilterType","IfcFireSuppressionTerminalType","IfcFlowController","IfcFlowControllerType","IfcFlowFitting","IfcFlowFittingType","IfcFlowInstrumentType","IfcFlowMeterType","IfcFlowMovingDevice","IfcFlowMovingDeviceType","IfcFlowSegment","IfcFlowSegmentType","IfcFlowStorageDevice","IfcFlowStorageDeviceType","IfcFlowTerminal","IfcFlowTerminalType","IfcFlowTreatmentDevice","IfcFlowTreatmentDeviceType","IfcFluidFlowProperties","IfcFooting","IfcFuelProperties","IfcFurnishingElement","IfcFurnishingElementType","IfcFurnitureStandard","IfcFurnitureType","IfcGasTerminalType","IfcGeneralMaterialProperties","IfcGeneralProfileProperties","IfcGeometricCurveSet","IfcGeometricRepresentationContext","IfcGeometricRepresentationItem","IfcGeometricRepresentationSubContext","IfcGeometricSet","IfcGrid","IfcGridAxis","IfcGridPlacement","IfcGroup","IfcHalfSpaceSolid","IfcHeatExchangerType","IfcHumidifierType","IfcHygroscopicMaterialProperties","IfcIShapeProfileDef","IfcImageTexture","IfcInventory","IfcIrregularTimeSeries","IfcIrregularTimeSeriesValue","IfcJunctionBoxType","IfcLShapeProfileDef","IfcLaborResource","IfcLampType","IfcLibraryInformation","IfcLibraryReference","IfcLightDistributionData","IfcLightFixtureType","IfcLightIntensityDistribution","IfcLightSource","IfcLightSourceAmbient","IfcLightSourceDirectional","IfcLightSourceGoniometric","IfcLightSourcePositional","IfcLightSourceSpot","IfcLine","IfcLinearDimension","IfcLocalPlacement","IfcLocalTime","IfcLoop","IfcManifoldSolidBrep","IfcMappedItem","IfcMaterial","IfcMaterialClassificationRelationship","IfcMaterialDefinitionRepresentation","IfcMaterialLayer","IfcMaterialLayerSet","IfcMaterialLayerSetUsage","IfcMaterialList","IfcMaterialProperties","IfcMeasureWithUnit","IfcMechanicalConcreteMaterialProperties","IfcMechanicalFastener","IfcMechanicalFastenerType","IfcMechanicalMaterialProperties","IfcMechanicalSteelMaterialProperties","IfcMember","IfcMemberType","IfcMetric","IfcMonetaryUnit","IfcMotorConnectionType","IfcMove","IfcNamedUnit","IfcObject","IfcObjectDefinition","IfcObjectPlacement","IfcObjective","IfcOccupant","IfcOffsetCurve2D","IfcOffsetCurve3D","IfcOneDirectionRepeatFactor","IfcOpenShell","IfcOpeningElement","IfcOpticalMaterialProperties","IfcOrderAction","IfcOrganization","IfcOrganizationRelationship","IfcOrientedEdge","IfcOutletType","IfcOwnerHistory","IfcParameterizedProfileDef","IfcPath","IfcPerformanceHistory","IfcPermeableCoveringProperties","IfcPermit","IfcPerson","IfcPersonAndOrganization","IfcPhysicalComplexQuantity","IfcPhysicalQuantity","IfcPhysicalSimpleQuantity","IfcPile","IfcPipeFittingType","IfcPipeSegmentType","IfcPixelTexture","IfcPlacement","IfcPlanarBox","IfcPlanarExtent","IfcPlane","IfcPlate","IfcPlateType","IfcPoint","IfcPointOnCurve","IfcPointOnSurface","IfcPolyLoop","IfcPolygonalBoundedHalfSpace","IfcPolyline","IfcPort","IfcPostalAddress","IfcPreDefinedColour","IfcPreDefinedCurveFont","IfcPreDefinedDimensionSymbol","IfcPreDefinedItem","IfcPreDefinedPointMarkerSymbol","IfcPreDefinedSymbol","IfcPreDefinedTerminatorSymbol","IfcPreDefinedTextFont","IfcPresentationLayerAssignment","IfcPresentationLayerWithStyle","IfcPresentationStyle","IfcPresentationStyleAssignment","IfcProcedure","IfcProcess","IfcProduct","IfcProductDefinitionShape","IfcProductRepresentation","IfcProductsOfCombustionProperties","IfcProfileDef","IfcProfileProperties","IfcProject","IfcProjectOrder","IfcProjectOrderRecord","IfcProjectionCurve","IfcProjectionElement","IfcProperty","IfcPropertyBoundedValue","IfcPropertyConstraintRelationship","IfcPropertyDefinition","IfcPropertyDependencyRelationship","IfcPropertyEnumeratedValue","IfcPropertyEnumeration","IfcPropertyListValue","IfcPropertyReferenceValue","IfcPropertySet","IfcPropertySetDefinition","IfcPropertySingleValue","IfcPropertyTableValue","IfcProtectiveDeviceType","IfcProxy","IfcPumpType","IfcQuantityArea","IfcQuantityCount","IfcQuantityLength","IfcQuantityTime","IfcQuantityVolume","IfcQuantityWeight","IfcRadiusDimension","IfcRailing","IfcRailingType","IfcRamp","IfcRampFlight","IfcRampFlightType","IfcRationalBezierCurve","IfcRectangleHollowProfileDef","IfcRectangleProfileDef","IfcRectangularPyramid","IfcRectangularTrimmedSurface","IfcReferencesValueDocument","IfcRegularTimeSeries","IfcReinforcementBarProperties","IfcReinforcementDefinitionProperties","IfcReinforcingBar","IfcReinforcingElement","IfcReinforcingMesh","IfcRelAggregates","IfcRelAssigns","IfcRelAssignsTasks","IfcRelAssignsToActor","IfcRelAssignsToControl","IfcRelAssignsToGroup","IfcRelAssignsToProcess","IfcRelAssignsToProduct","IfcRelAssignsToProjectOrder","IfcRelAssignsToResource","IfcRelAssociates","IfcRelAssociatesAppliedValue","IfcRelAssociatesApproval","IfcRelAssociatesClassification","IfcRelAssociatesConstraint","IfcRelAssociatesDocument","IfcRelAssociatesLibrary","IfcRelAssociatesMaterial","IfcRelAssociatesProfileProperties","IfcRelConnects","IfcRelConnectsElements","IfcRelConnectsPathElements","IfcRelConnectsPortToElement","IfcRelConnectsPorts","IfcRelConnectsStructuralActivity","IfcRelConnectsStructuralElement","IfcRelConnectsStructuralMember","IfcRelConnectsWithEccentricity","IfcRelConnectsWithRealizingElements","IfcRelContainedInSpatialStructure","IfcRelCoversBldgElements","IfcRelCoversSpaces","IfcRelDecomposes","IfcRelDefines","IfcRelDefinesByProperties","IfcRelDefinesByType","IfcRelFillsElement","IfcRelFlowControlElements","IfcRelInteractionRequirements","IfcRelNests","IfcRelOccupiesSpaces","IfcRelOverridesProperties","IfcRelProjectsElement","IfcRelReferencedInSpatialStructure","IfcRelSchedulesCostItems","IfcRelSequence","IfcRelServicesBuildings","IfcRelSpaceBoundary","IfcRelVoidsElement","IfcRelationship","IfcRelaxation","IfcRepresentation","IfcRepresentationContext","IfcRepresentationItem","IfcRepresentationMap","IfcResource","IfcRevolvedAreaSolid","IfcRibPlateProfileProperties","IfcRightCircularCone","IfcRightCircularCylinder","IfcRoof","IfcRoot","IfcRoundedEdgeFeature","IfcRoundedRectangleProfileDef","IfcSIUnit","IfcSanitaryTerminalType","IfcScheduleTimeControl","IfcSectionProperties","IfcSectionReinforcementProperties","IfcSectionedSpine","IfcSensorType","IfcServiceLife","IfcServiceLifeFactor","IfcShapeAspect","IfcShapeModel","IfcShapeRepresentation","IfcShellBasedSurfaceModel","IfcSimpleProperty","IfcSite","IfcSlab","IfcSlabType","IfcSlippageConnectionCondition","IfcSolidModel","IfcSoundProperties","IfcSoundValue","IfcSpace","IfcSpaceHeaterType","IfcSpaceProgram","IfcSpaceThermalLoadProperties","IfcSpaceType","IfcSpatialStructureElement","IfcSpatialStructureElementType","IfcSphere","IfcStackTerminalType","IfcStair","IfcStairFlight","IfcStairFlightType","IfcStructuralAction","IfcStructuralActivity","IfcStructuralAnalysisModel","IfcStructuralConnection","IfcStructuralConnectionCondition","IfcStructuralCurveConnection","IfcStructuralCurveMember","IfcStructuralCurveMemberVarying","IfcStructuralItem","IfcStructuralLinearAction","IfcStructuralLinearActionVarying","IfcStructuralLoad","IfcStructuralLoadGroup","IfcStructuralLoadLinearForce","IfcStructuralLoadPlanarForce","IfcStructuralLoadSingleDisplacement","IfcStructuralLoadSingleDisplacementDistortion","IfcStructuralLoadSingleForce","IfcStructuralLoadSingleForceWarping","IfcStructuralLoadStatic","IfcStructuralLoadTemperature","IfcStructuralMember","IfcStructuralPlanarAction","IfcStructuralPlanarActionVarying","IfcStructuralPointAction","IfcStructuralPointConnection","IfcStructuralPointReaction","IfcStructuralProfileProperties","IfcStructuralReaction","IfcStructuralResultGroup","IfcStructuralSteelProfileProperties","IfcStructuralSurfaceConnection","IfcStructuralSurfaceMember","IfcStructuralSurfaceMemberVarying","IfcStructuredDimensionCallout","IfcStyleModel","IfcStyledItem","IfcStyledRepresentation","IfcSubContractResource","IfcSubedge","IfcSurface","IfcSurfaceCurveSweptAreaSolid","IfcSurfaceOfLinearExtrusion","IfcSurfaceOfRevolution","IfcSurfaceStyle","IfcSurfaceStyleLighting","IfcSurfaceStyleRefraction","IfcSurfaceStyleRendering","IfcSurfaceStyleShading","IfcSurfaceStyleWithTextures","IfcSurfaceTexture","IfcSweptAreaSolid","IfcSweptDiskSolid","IfcSweptSurface","IfcSwitchingDeviceType","IfcSymbolStyle","IfcSystem","IfcSystemFurnitureElementType","IfcTShapeProfileDef","IfcTable","IfcTableRow","IfcTankType","IfcTask","IfcTelecomAddress","IfcTendon","IfcTendonAnchor","IfcTerminatorSymbol","IfcTextLiteral","IfcTextLiteralWithExtent","IfcTextStyle","IfcTextStyleFontModel","IfcTextStyleForDefinedFont","IfcTextStyleTextModel","IfcTextStyleWithBoxCharacteristics","IfcTextureCoordinate","IfcTextureCoordinateGenerator","IfcTextureMap","IfcTextureVertex","IfcThermalMaterialProperties","IfcTimeSeries","IfcTimeSeriesReferenceRelationship","IfcTimeSeriesSchedule","IfcTimeSeriesValue","IfcTopologicalRepresentationItem","IfcTopologyRepresentation","IfcTransformerType","IfcTransportElement","IfcTransportElementType","IfcTrapeziumProfileDef","IfcTrimmedCurve","IfcTubeBundleType","IfcTwoDirectionRepeatFactor","IfcTypeObject","IfcTypeProduct","IfcUShapeProfileDef","IfcUnitAssignment","IfcUnitaryEquipmentType","IfcValveType","IfcVector","IfcVertex","IfcVertexBasedTextureMap","IfcVertexLoop","IfcVertexPoint","IfcVibrationIsolatorType","IfcVirtualElement","IfcVirtualGridIntersection","IfcWall","IfcWallStandardCase","IfcWallType","IfcWasteTerminalType","IfcWaterProperties","IfcWindow","IfcWindowLiningProperties","IfcWindowPanelProperties","IfcWindowStyle","IfcWorkControl","IfcWorkPlan","IfcWorkSchedule","IfcZShapeProfileDef","IfcZone" };
    return names[v];
}

std::map<std::string,Type::Enum> string_map;
void Ifc2x3::InitStringMap() {
    string_map["IFCABSORBEDDOSEMEASURE"                        ] = Type::IfcAbsorbedDoseMeasure;
    string_map["IFCACCELERATIONMEASURE"                        ] = Type::IfcAccelerationMeasure;
    string_map["IFCAMOUNTOFSUBSTANCEMEASURE"                   ] = Type::IfcAmountOfSubstanceMeasure;
    string_map["IFCANGULARVELOCITYMEASURE"                     ] = Type::IfcAngularVelocityMeasure;
    string_map["IFCAREAMEASURE"                                ] = Type::IfcAreaMeasure;
    string_map["IFCBOOLEAN"                                    ] = Type::IfcBoolean;
    string_map["IFCCOLOUR"                                     ] = Type::IfcColour;
    string_map["IFCCOMPLEXNUMBER"                              ] = Type::IfcComplexNumber;
    string_map["IFCCOMPOUNDPLANEANGLEMEASURE"                  ] = Type::IfcCompoundPlaneAngleMeasure;
    string_map["IFCCONTEXTDEPENDENTMEASURE"                    ] = Type::IfcContextDependentMeasure;
    string_map["IFCCOUNTMEASURE"                               ] = Type::IfcCountMeasure;
    string_map["IFCCURVATUREMEASURE"                           ] = Type::IfcCurvatureMeasure;
    string_map["IFCDATETIMESELECT"                             ] = Type::IfcDateTimeSelect;
    string_map["IFCDERIVEDMEASUREVALUE"                        ] = Type::IfcDerivedMeasureValue;
    string_map["IFCDESCRIPTIVEMEASURE"                         ] = Type::IfcDescriptiveMeasure;
    string_map["IFCDOSEEQUIVALENTMEASURE"                      ] = Type::IfcDoseEquivalentMeasure;
    string_map["IFCDYNAMICVISCOSITYMEASURE"                    ] = Type::IfcDynamicViscosityMeasure;
    string_map["IFCELECTRICCAPACITANCEMEASURE"                 ] = Type::IfcElectricCapacitanceMeasure;
    string_map["IFCELECTRICCHARGEMEASURE"                      ] = Type::IfcElectricChargeMeasure;
    string_map["IFCELECTRICCONDUCTANCEMEASURE"                 ] = Type::IfcElectricConductanceMeasure;
    string_map["IFCELECTRICCURRENTMEASURE"                     ] = Type::IfcElectricCurrentMeasure;
    string_map["IFCELECTRICRESISTANCEMEASURE"                  ] = Type::IfcElectricResistanceMeasure;
    string_map["IFCELECTRICVOLTAGEMEASURE"                     ] = Type::IfcElectricVoltageMeasure;
    string_map["IFCENERGYMEASURE"                              ] = Type::IfcEnergyMeasure;
    string_map["IFCFORCEMEASURE"                               ] = Type::IfcForceMeasure;
    string_map["IFCFREQUENCYMEASURE"                           ] = Type::IfcFrequencyMeasure;
    string_map["IFCHEATFLUXDENSITYMEASURE"                     ] = Type::IfcHeatFluxDensityMeasure;
    string_map["IFCHEATINGVALUEMEASURE"                        ] = Type::IfcHeatingValueMeasure;
    string_map["IFCIDENTIFIER"                                 ] = Type::IfcIdentifier;
    string_map["IFCILLUMINANCEMEASURE"                         ] = Type::IfcIlluminanceMeasure;
    string_map["IFCINDUCTANCEMEASURE"                          ] = Type::IfcInductanceMeasure;
    string_map["IFCINTEGER"                                    ] = Type::IfcInteger;
    string_map["IFCINTEGERCOUNTRATEMEASURE"                    ] = Type::IfcIntegerCountRateMeasure;
    string_map["IFCIONCONCENTRATIONMEASURE"                    ] = Type::IfcIonConcentrationMeasure;
    string_map["IFCISOTHERMALMOISTURECAPACITYMEASURE"          ] = Type::IfcIsothermalMoistureCapacityMeasure;
    string_map["IFCKINEMATICVISCOSITYMEASURE"                  ] = Type::IfcKinematicViscosityMeasure;
    string_map["IFCLABEL"                                      ] = Type::IfcLabel;
    string_map["IFCLENGTHMEASURE"                              ] = Type::IfcLengthMeasure;
    string_map["IFCLINEARFORCEMEASURE"                         ] = Type::IfcLinearForceMeasure;
    string_map["IFCLINEARMOMENTMEASURE"                        ] = Type::IfcLinearMomentMeasure;
    string_map["IFCLINEARSTIFFNESSMEASURE"                     ] = Type::IfcLinearStiffnessMeasure;
    string_map["IFCLINEARVELOCITYMEASURE"                      ] = Type::IfcLinearVelocityMeasure;
    string_map["IFCLOGICAL"                                    ] = Type::IfcLogical;
    string_map["IFCLUMINOUSFLUXMEASURE"                        ] = Type::IfcLuminousFluxMeasure;
    string_map["IFCLUMINOUSINTENSITYDISTRIBUTIONMEASURE"       ] = Type::IfcLuminousIntensityDistributionMeasure;
    string_map["IFCLUMINOUSINTENSITYMEASURE"                   ] = Type::IfcLuminousIntensityMeasure;
    string_map["IFCMAGNETICFLUXDENSITYMEASURE"                 ] = Type::IfcMagneticFluxDensityMeasure;
    string_map["IFCMAGNETICFLUXMEASURE"                        ] = Type::IfcMagneticFluxMeasure;
    string_map["IFCMASSDENSITYMEASURE"                         ] = Type::IfcMassDensityMeasure;
    string_map["IFCMASSFLOWRATEMEASURE"                        ] = Type::IfcMassFlowRateMeasure;
    string_map["IFCMASSMEASURE"                                ] = Type::IfcMassMeasure;
    string_map["IFCMASSPERLENGTHMEASURE"                       ] = Type::IfcMassPerLengthMeasure;
    string_map["IFCMEASUREVALUE"                               ] = Type::IfcMeasureValue;
    string_map["IFCMODULUSOFELASTICITYMEASURE"                 ] = Type::IfcModulusOfElasticityMeasure;
    string_map["IFCMODULUSOFLINEARSUBGRADEREACTIONMEASURE"     ] = Type::IfcModulusOfLinearSubgradeReactionMeasure;
    string_map["IFCMODULUSOFROTATIONALSUBGRADEREACTIONMEASURE" ] = Type::IfcModulusOfRotationalSubgradeReactionMeasure;
    string_map["IFCMODULUSOFSUBGRADEREACTIONMEASURE"           ] = Type::IfcModulusOfSubgradeReactionMeasure;
    string_map["IFCMOISTUREDIFFUSIVITYMEASURE"                 ] = Type::IfcMoistureDiffusivityMeasure;
    string_map["IFCMOLECULARWEIGHTMEASURE"                     ] = Type::IfcMolecularWeightMeasure;
    string_map["IFCMOMENTOFINERTIAMEASURE"                     ] = Type::IfcMomentOfInertiaMeasure;
    string_map["IFCMONETARYMEASURE"                            ] = Type::IfcMonetaryMeasure;
    string_map["IFCNORMALISEDRATIOMEASURE"                     ] = Type::IfcNormalisedRatioMeasure;
    string_map["IFCNULLSTYLE"                                  ] = Type::IfcNullStyle;
    string_map["IFCNUMERICMEASURE"                             ] = Type::IfcNumericMeasure;
    string_map["IFCPHMEASURE"                                  ] = Type::IfcPHMeasure;
    string_map["IFCPARAMETERVALUE"                             ] = Type::IfcParameterValue;
    string_map["IFCPLANARFORCEMEASURE"                         ] = Type::IfcPlanarForceMeasure;
    string_map["IFCPLANEANGLEMEASURE"                          ] = Type::IfcPlaneAngleMeasure;
    string_map["IFCPOSITIVELENGTHMEASURE"                      ] = Type::IfcPositiveLengthMeasure;
    string_map["IFCPOSITIVEPLANEANGLEMEASURE"                  ] = Type::IfcPositivePlaneAngleMeasure;
    string_map["IFCPOSITIVERATIOMEASURE"                       ] = Type::IfcPositiveRatioMeasure;
    string_map["IFCPOWERMEASURE"                               ] = Type::IfcPowerMeasure;
    string_map["IFCPRESSUREMEASURE"                            ] = Type::IfcPressureMeasure;
    string_map["IFCRADIOACTIVITYMEASURE"                       ] = Type::IfcRadioActivityMeasure;
    string_map["IFCRATIOMEASURE"                               ] = Type::IfcRatioMeasure;
    string_map["IFCREAL"                                       ] = Type::IfcReal;
    string_map["IFCROTATIONALFREQUENCYMEASURE"                 ] = Type::IfcRotationalFrequencyMeasure;
    string_map["IFCROTATIONALMASSMEASURE"                      ] = Type::IfcRotationalMassMeasure;
    string_map["IFCROTATIONALSTIFFNESSMEASURE"                 ] = Type::IfcRotationalStiffnessMeasure;
    string_map["IFCSECTIONMODULUSMEASURE"                      ] = Type::IfcSectionModulusMeasure;
    string_map["IFCSECTIONALAREAINTEGRALMEASURE"               ] = Type::IfcSectionalAreaIntegralMeasure;
    string_map["IFCSHEARMODULUSMEASURE"                        ] = Type::IfcShearModulusMeasure;
    string_map["IFCSIMPLEVALUE"                                ] = Type::IfcSimpleValue;
    string_map["IFCSOLIDANGLEMEASURE"                          ] = Type::IfcSolidAngleMeasure;
    string_map["IFCSOUNDPOWERMEASURE"                          ] = Type::IfcSoundPowerMeasure;
    string_map["IFCSOUNDPRESSUREMEASURE"                       ] = Type::IfcSoundPressureMeasure;
    string_map["IFCSPECIFICHEATCAPACITYMEASURE"                ] = Type::IfcSpecificHeatCapacityMeasure;
    string_map["IFCSPECULAREXPONENT"                           ] = Type::IfcSpecularExponent;
    string_map["IFCSPECULARROUGHNESS"                          ] = Type::IfcSpecularRoughness;
    string_map["IFCTEMPERATUREGRADIENTMEASURE"                 ] = Type::IfcTemperatureGradientMeasure;
    string_map["IFCTEXT"                                       ] = Type::IfcText;
    string_map["IFCTHERMALADMITTANCEMEASURE"                   ] = Type::IfcThermalAdmittanceMeasure;
    string_map["IFCTHERMALCONDUCTIVITYMEASURE"                 ] = Type::IfcThermalConductivityMeasure;
    string_map["IFCTHERMALEXPANSIONCOEFFICIENTMEASURE"         ] = Type::IfcThermalExpansionCoefficientMeasure;
    string_map["IFCTHERMALRESISTANCEMEASURE"                   ] = Type::IfcThermalResistanceMeasure;
    string_map["IFCTHERMALTRANSMITTANCEMEASURE"                ] = Type::IfcThermalTransmittanceMeasure;
    string_map["IFCTHERMODYNAMICTEMPERATUREMEASURE"            ] = Type::IfcThermodynamicTemperatureMeasure;
    string_map["IFCTIMEMEASURE"                                ] = Type::IfcTimeMeasure;
    string_map["IFCTIMESTAMP"                                  ] = Type::IfcTimeStamp;
    string_map["IFCTORQUEMEASURE"                              ] = Type::IfcTorqueMeasure;
    string_map["IFCVAPORPERMEABILITYMEASURE"                   ] = Type::IfcVaporPermeabilityMeasure;
    string_map["IFCVOLUMEMEASURE"                              ] = Type::IfcVolumeMeasure;
    string_map["IFCVOLUMETRICFLOWRATEMEASURE"                  ] = Type::IfcVolumetricFlowRateMeasure;
    string_map["IFCWARPINGCONSTANTMEASURE"                     ] = Type::IfcWarpingConstantMeasure;
    string_map["IFCWARPINGMOMENTMEASURE"                       ] = Type::IfcWarpingMomentMeasure;
    string_map["IFC2DCOMPOSITECURVE"                           ] = Type::Ifc2DCompositeCurve;
    string_map["IFCACTIONREQUEST"                              ] = Type::IfcActionRequest;
    string_map["IFCACTOR"                                      ] = Type::IfcActor;
    string_map["IFCACTORROLE"                                  ] = Type::IfcActorRole;
    string_map["IFCACTUATORTYPE"                               ] = Type::IfcActuatorType;
    string_map["IFCADDRESS"                                    ] = Type::IfcAddress;
    string_map["IFCAIRTERMINALBOXTYPE"                         ] = Type::IfcAirTerminalBoxType;
    string_map["IFCAIRTERMINALTYPE"                            ] = Type::IfcAirTerminalType;
    string_map["IFCAIRTOAIRHEATRECOVERYTYPE"                   ] = Type::IfcAirToAirHeatRecoveryType;
    string_map["IFCALARMTYPE"                                  ] = Type::IfcAlarmType;
    string_map["IFCANGULARDIMENSION"                           ] = Type::IfcAngularDimension;
    string_map["IFCANNOTATION"                                 ] = Type::IfcAnnotation;
    string_map["IFCANNOTATIONCURVEOCCURRENCE"                  ] = Type::IfcAnnotationCurveOccurrence;
    string_map["IFCANNOTATIONFILLAREA"                         ] = Type::IfcAnnotationFillArea;
    string_map["IFCANNOTATIONFILLAREAOCCURRENCE"               ] = Type::IfcAnnotationFillAreaOccurrence;
    string_map["IFCANNOTATIONOCCURRENCE"                       ] = Type::IfcAnnotationOccurrence;
    string_map["IFCANNOTATIONSURFACE"                          ] = Type::IfcAnnotationSurface;
    string_map["IFCANNOTATIONSURFACEOCCURRENCE"                ] = Type::IfcAnnotationSurfaceOccurrence;
    string_map["IFCANNOTATIONSYMBOLOCCURRENCE"                 ] = Type::IfcAnnotationSymbolOccurrence;
    string_map["IFCANNOTATIONTEXTOCCURRENCE"                   ] = Type::IfcAnnotationTextOccurrence;
    string_map["IFCAPPLICATION"                                ] = Type::IfcApplication;
    string_map["IFCAPPLIEDVALUE"                               ] = Type::IfcAppliedValue;
    string_map["IFCAPPLIEDVALUERELATIONSHIP"                   ] = Type::IfcAppliedValueRelationship;
    string_map["IFCAPPROVAL"                                   ] = Type::IfcApproval;
    string_map["IFCAPPROVALACTORRELATIONSHIP"                  ] = Type::IfcApprovalActorRelationship;
    string_map["IFCAPPROVALPROPERTYRELATIONSHIP"               ] = Type::IfcApprovalPropertyRelationship;
    string_map["IFCAPPROVALRELATIONSHIP"                       ] = Type::IfcApprovalRelationship;
    string_map["IFCARBITRARYCLOSEDPROFILEDEF"                  ] = Type::IfcArbitraryClosedProfileDef;
    string_map["IFCARBITRARYOPENPROFILEDEF"                    ] = Type::IfcArbitraryOpenProfileDef;
    string_map["IFCARBITRARYPROFILEDEFWITHVOIDS"               ] = Type::IfcArbitraryProfileDefWithVoids;
    string_map["IFCASSET"                                      ] = Type::IfcAsset;
    string_map["IFCASYMMETRICISHAPEPROFILEDEF"                 ] = Type::IfcAsymmetricIShapeProfileDef;
    string_map["IFCAXIS1PLACEMENT"                             ] = Type::IfcAxis1Placement;
    string_map["IFCAXIS2PLACEMENT2D"                           ] = Type::IfcAxis2Placement2D;
    string_map["IFCAXIS2PLACEMENT3D"                           ] = Type::IfcAxis2Placement3D;
    string_map["IFCBSPLINECURVE"                               ] = Type::IfcBSplineCurve;
    string_map["IFCBEAM"                                       ] = Type::IfcBeam;
    string_map["IFCBEAMTYPE"                                   ] = Type::IfcBeamType;
    string_map["IFCBEZIERCURVE"                                ] = Type::IfcBezierCurve;
    string_map["IFCBLOBTEXTURE"                                ] = Type::IfcBlobTexture;
    string_map["IFCBLOCK"                                      ] = Type::IfcBlock;
    string_map["IFCBOILERTYPE"                                 ] = Type::IfcBoilerType;
    string_map["IFCBOOLEANCLIPPINGRESULT"                      ] = Type::IfcBooleanClippingResult;
    string_map["IFCBOOLEANRESULT"                              ] = Type::IfcBooleanResult;
    string_map["IFCBOUNDARYCONDITION"                          ] = Type::IfcBoundaryCondition;
    string_map["IFCBOUNDARYEDGECONDITION"                      ] = Type::IfcBoundaryEdgeCondition;
    string_map["IFCBOUNDARYFACECONDITION"                      ] = Type::IfcBoundaryFaceCondition;
    string_map["IFCBOUNDARYNODECONDITION"                      ] = Type::IfcBoundaryNodeCondition;
    string_map["IFCBOUNDARYNODECONDITIONWARPING"               ] = Type::IfcBoundaryNodeConditionWarping;
    string_map["IFCBOUNDEDCURVE"                               ] = Type::IfcBoundedCurve;
    string_map["IFCBOUNDEDSURFACE"                             ] = Type::IfcBoundedSurface;
    string_map["IFCBOUNDINGBOX"                                ] = Type::IfcBoundingBox;
    string_map["IFCBOXEDHALFSPACE"                             ] = Type::IfcBoxedHalfSpace;
    string_map["IFCBUILDING"                                   ] = Type::IfcBuilding;
    string_map["IFCBUILDINGELEMENT"                            ] = Type::IfcBuildingElement;
    string_map["IFCBUILDINGELEMENTCOMPONENT"                   ] = Type::IfcBuildingElementComponent;
    string_map["IFCBUILDINGELEMENTPART"                        ] = Type::IfcBuildingElementPart;
    string_map["IFCBUILDINGELEMENTPROXY"                       ] = Type::IfcBuildingElementProxy;
    string_map["IFCBUILDINGELEMENTPROXYTYPE"                   ] = Type::IfcBuildingElementProxyType;
    string_map["IFCBUILDINGELEMENTTYPE"                        ] = Type::IfcBuildingElementType;
    string_map["IFCBUILDINGSTOREY"                             ] = Type::IfcBuildingStorey;
    string_map["IFCCSHAPEPROFILEDEF"                           ] = Type::IfcCShapeProfileDef;
    string_map["IFCCABLECARRIERFITTINGTYPE"                    ] = Type::IfcCableCarrierFittingType;
    string_map["IFCCABLECARRIERSEGMENTTYPE"                    ] = Type::IfcCableCarrierSegmentType;
    string_map["IFCCABLESEGMENTTYPE"                           ] = Type::IfcCableSegmentType;
    string_map["IFCCALENDARDATE"                               ] = Type::IfcCalendarDate;
    string_map["IFCCARTESIANPOINT"                             ] = Type::IfcCartesianPoint;
    string_map["IFCCARTESIANTRANSFORMATIONOPERATOR"            ] = Type::IfcCartesianTransformationOperator;
    string_map["IFCCARTESIANTRANSFORMATIONOPERATOR2D"          ] = Type::IfcCartesianTransformationOperator2D;
    string_map["IFCCARTESIANTRANSFORMATIONOPERATOR2DNONUNIFORM"] = Type::IfcCartesianTransformationOperator2DnonUniform;
    string_map["IFCCARTESIANTRANSFORMATIONOPERATOR3D"          ] = Type::IfcCartesianTransformationOperator3D;
    string_map["IFCCARTESIANTRANSFORMATIONOPERATOR3DNONUNIFORM"] = Type::IfcCartesianTransformationOperator3DnonUniform;
    string_map["IFCCENTERLINEPROFILEDEF"                       ] = Type::IfcCenterLineProfileDef;
    string_map["IFCCHAMFEREDGEFEATURE"                         ] = Type::IfcChamferEdgeFeature;
    string_map["IFCCHILLERTYPE"                                ] = Type::IfcChillerType;
    string_map["IFCCIRCLE"                                     ] = Type::IfcCircle;
    string_map["IFCCIRCLEHOLLOWPROFILEDEF"                     ] = Type::IfcCircleHollowProfileDef;
    string_map["IFCCIRCLEPROFILEDEF"                           ] = Type::IfcCircleProfileDef;
    string_map["IFCCLASSIFICATION"                             ] = Type::IfcClassification;
    string_map["IFCCLASSIFICATIONITEM"                         ] = Type::IfcClassificationItem;
    string_map["IFCCLASSIFICATIONITEMRELATIONSHIP"             ] = Type::IfcClassificationItemRelationship;
    string_map["IFCCLASSIFICATIONNOTATION"                     ] = Type::IfcClassificationNotation;
    string_map["IFCCLASSIFICATIONNOTATIONFACET"                ] = Type::IfcClassificationNotationFacet;
    string_map["IFCCLASSIFICATIONREFERENCE"                    ] = Type::IfcClassificationReference;
    string_map["IFCCLOSEDSHELL"                                ] = Type::IfcClosedShell;
    string_map["IFCCOILTYPE"                                   ] = Type::IfcCoilType;
    string_map["IFCCOLOURRGB"                                  ] = Type::IfcColourRgb;
    string_map["IFCCOLOURSPECIFICATION"                        ] = Type::IfcColourSpecification;
    string_map["IFCCOLUMN"                                     ] = Type::IfcColumn;
    string_map["IFCCOLUMNTYPE"                                 ] = Type::IfcColumnType;
    string_map["IFCCOMPLEXPROPERTY"                            ] = Type::IfcComplexProperty;
    string_map["IFCCOMPOSITECURVE"                             ] = Type::IfcCompositeCurve;
    string_map["IFCCOMPOSITECURVESEGMENT"                      ] = Type::IfcCompositeCurveSegment;
    string_map["IFCCOMPOSITEPROFILEDEF"                        ] = Type::IfcCompositeProfileDef;
    string_map["IFCCOMPRESSORTYPE"                             ] = Type::IfcCompressorType;
    string_map["IFCCONDENSERTYPE"                              ] = Type::IfcCondenserType;
    string_map["IFCCONDITION"                                  ] = Type::IfcCondition;
    string_map["IFCCONDITIONCRITERION"                         ] = Type::IfcConditionCriterion;
    string_map["IFCCONIC"                                      ] = Type::IfcConic;
    string_map["IFCCONNECTEDFACESET"                           ] = Type::IfcConnectedFaceSet;
    string_map["IFCCONNECTIONCURVEGEOMETRY"                    ] = Type::IfcConnectionCurveGeometry;
    string_map["IFCCONNECTIONGEOMETRY"                         ] = Type::IfcConnectionGeometry;
    string_map["IFCCONNECTIONPOINTECCENTRICITY"                ] = Type::IfcConnectionPointEccentricity;
    string_map["IFCCONNECTIONPOINTGEOMETRY"                    ] = Type::IfcConnectionPointGeometry;
    string_map["IFCCONNECTIONPORTGEOMETRY"                     ] = Type::IfcConnectionPortGeometry;
    string_map["IFCCONNECTIONSURFACEGEOMETRY"                  ] = Type::IfcConnectionSurfaceGeometry;
    string_map["IFCCONSTRAINT"                                 ] = Type::IfcConstraint;
    string_map["IFCCONSTRAINTAGGREGATIONRELATIONSHIP"          ] = Type::IfcConstraintAggregationRelationship;
    string_map["IFCCONSTRAINTCLASSIFICATIONRELATIONSHIP"       ] = Type::IfcConstraintClassificationRelationship;
    string_map["IFCCONSTRAINTRELATIONSHIP"                     ] = Type::IfcConstraintRelationship;
    string_map["IFCCONSTRUCTIONEQUIPMENTRESOURCE"              ] = Type::IfcConstructionEquipmentResource;
    string_map["IFCCONSTRUCTIONMATERIALRESOURCE"               ] = Type::IfcConstructionMaterialResource;
    string_map["IFCCONSTRUCTIONPRODUCTRESOURCE"                ] = Type::IfcConstructionProductResource;
    string_map["IFCCONSTRUCTIONRESOURCE"                       ] = Type::IfcConstructionResource;
    string_map["IFCCONTEXTDEPENDENTUNIT"                       ] = Type::IfcContextDependentUnit;
    string_map["IFCCONTROL"                                    ] = Type::IfcControl;
    string_map["IFCCONTROLLERTYPE"                             ] = Type::IfcControllerType;
    string_map["IFCCONVERSIONBASEDUNIT"                        ] = Type::IfcConversionBasedUnit;
    string_map["IFCCOOLEDBEAMTYPE"                             ] = Type::IfcCooledBeamType;
    string_map["IFCCOOLINGTOWERTYPE"                           ] = Type::IfcCoolingTowerType;
    string_map["IFCCOORDINATEDUNIVERSALTIMEOFFSET"             ] = Type::IfcCoordinatedUniversalTimeOffset;
    string_map["IFCCOSTITEM"                                   ] = Type::IfcCostItem;
    string_map["IFCCOSTSCHEDULE"                               ] = Type::IfcCostSchedule;
    string_map["IFCCOSTVALUE"                                  ] = Type::IfcCostValue;
    string_map["IFCCOVERING"                                   ] = Type::IfcCovering;
    string_map["IFCCOVERINGTYPE"                               ] = Type::IfcCoveringType;
    string_map["IFCCRANERAILASHAPEPROFILEDEF"                  ] = Type::IfcCraneRailAShapeProfileDef;
    string_map["IFCCRANERAILFSHAPEPROFILEDEF"                  ] = Type::IfcCraneRailFShapeProfileDef;
    string_map["IFCCREWRESOURCE"                               ] = Type::IfcCrewResource;
    string_map["IFCCSGPRIMITIVE3D"                             ] = Type::IfcCsgPrimitive3D;
    string_map["IFCCSGSOLID"                                   ] = Type::IfcCsgSolid;
    string_map["IFCCURRENCYRELATIONSHIP"                       ] = Type::IfcCurrencyRelationship;
    string_map["IFCCURTAINWALL"                                ] = Type::IfcCurtainWall;
    string_map["IFCCURTAINWALLTYPE"                            ] = Type::IfcCurtainWallType;
    string_map["IFCCURVE"                                      ] = Type::IfcCurve;
    string_map["IFCCURVEBOUNDEDPLANE"                          ] = Type::IfcCurveBoundedPlane;
    string_map["IFCCURVESTYLE"                                 ] = Type::IfcCurveStyle;
    string_map["IFCCURVESTYLEFONT"                             ] = Type::IfcCurveStyleFont;
    string_map["IFCCURVESTYLEFONTANDSCALING"                   ] = Type::IfcCurveStyleFontAndScaling;
    string_map["IFCCURVESTYLEFONTPATTERN"                      ] = Type::IfcCurveStyleFontPattern;
    string_map["IFCDAMPERTYPE"                                 ] = Type::IfcDamperType;
    string_map["IFCDATEANDTIME"                                ] = Type::IfcDateAndTime;
    string_map["IFCDEFINEDSYMBOL"                              ] = Type::IfcDefinedSymbol;
    string_map["IFCDERIVEDPROFILEDEF"                          ] = Type::IfcDerivedProfileDef;
    string_map["IFCDERIVEDUNIT"                                ] = Type::IfcDerivedUnit;
    string_map["IFCDERIVEDUNITELEMENT"                         ] = Type::IfcDerivedUnitElement;
    string_map["IFCDIAMETERDIMENSION"                          ] = Type::IfcDiameterDimension;
    string_map["IFCDIMENSIONCALLOUTRELATIONSHIP"               ] = Type::IfcDimensionCalloutRelationship;
    string_map["IFCDIMENSIONCURVE"                             ] = Type::IfcDimensionCurve;
    string_map["IFCDIMENSIONCURVEDIRECTEDCALLOUT"              ] = Type::IfcDimensionCurveDirectedCallout;
    string_map["IFCDIMENSIONCURVETERMINATOR"                   ] = Type::IfcDimensionCurveTerminator;
    string_map["IFCDIMENSIONPAIR"                              ] = Type::IfcDimensionPair;
    string_map["IFCDIMENSIONALEXPONENTS"                       ] = Type::IfcDimensionalExponents;
    string_map["IFCDIRECTION"                                  ] = Type::IfcDirection;
    string_map["IFCDISCRETEACCESSORY"                          ] = Type::IfcDiscreteAccessory;
    string_map["IFCDISCRETEACCESSORYTYPE"                      ] = Type::IfcDiscreteAccessoryType;
    string_map["IFCDISTRIBUTIONCHAMBERELEMENT"                 ] = Type::IfcDistributionChamberElement;
    string_map["IFCDISTRIBUTIONCHAMBERELEMENTTYPE"             ] = Type::IfcDistributionChamberElementType;
    string_map["IFCDISTRIBUTIONCONTROLELEMENT"                 ] = Type::IfcDistributionControlElement;
    string_map["IFCDISTRIBUTIONCONTROLELEMENTTYPE"             ] = Type::IfcDistributionControlElementType;
    string_map["IFCDISTRIBUTIONELEMENT"                        ] = Type::IfcDistributionElement;
    string_map["IFCDISTRIBUTIONELEMENTTYPE"                    ] = Type::IfcDistributionElementType;
    string_map["IFCDISTRIBUTIONFLOWELEMENT"                    ] = Type::IfcDistributionFlowElement;
    string_map["IFCDISTRIBUTIONFLOWELEMENTTYPE"                ] = Type::IfcDistributionFlowElementType;
    string_map["IFCDISTRIBUTIONPORT"                           ] = Type::IfcDistributionPort;
    string_map["IFCDOCUMENTELECTRONICFORMAT"                   ] = Type::IfcDocumentElectronicFormat;
    string_map["IFCDOCUMENTINFORMATION"                        ] = Type::IfcDocumentInformation;
    string_map["IFCDOCUMENTINFORMATIONRELATIONSHIP"            ] = Type::IfcDocumentInformationRelationship;
    string_map["IFCDOCUMENTREFERENCE"                          ] = Type::IfcDocumentReference;
    string_map["IFCDOOR"                                       ] = Type::IfcDoor;
    string_map["IFCDOORLININGPROPERTIES"                       ] = Type::IfcDoorLiningProperties;
    string_map["IFCDOORPANELPROPERTIES"                        ] = Type::IfcDoorPanelProperties;
    string_map["IFCDOORSTYLE"                                  ] = Type::IfcDoorStyle;
    string_map["IFCDRAUGHTINGCALLOUT"                          ] = Type::IfcDraughtingCallout;
    string_map["IFCDRAUGHTINGCALLOUTRELATIONSHIP"              ] = Type::IfcDraughtingCalloutRelationship;
    string_map["IFCDRAUGHTINGPREDEFINEDCOLOUR"                 ] = Type::IfcDraughtingPreDefinedColour;
    string_map["IFCDRAUGHTINGPREDEFINEDCURVEFONT"              ] = Type::IfcDraughtingPreDefinedCurveFont;
    string_map["IFCDRAUGHTINGPREDEFINEDTEXTFONT"               ] = Type::IfcDraughtingPreDefinedTextFont;
    string_map["IFCDUCTFITTINGTYPE"                            ] = Type::IfcDuctFittingType;
    string_map["IFCDUCTSEGMENTTYPE"                            ] = Type::IfcDuctSegmentType;
    string_map["IFCDUCTSILENCERTYPE"                           ] = Type::IfcDuctSilencerType;
    string_map["IFCEDGE"                                       ] = Type::IfcEdge;
    string_map["IFCEDGECURVE"                                  ] = Type::IfcEdgeCurve;
    string_map["IFCEDGEFEATURE"                                ] = Type::IfcEdgeFeature;
    string_map["IFCEDGELOOP"                                   ] = Type::IfcEdgeLoop;
    string_map["IFCELECTRICAPPLIANCETYPE"                      ] = Type::IfcElectricApplianceType;
    string_map["IFCELECTRICDISTRIBUTIONPOINT"                  ] = Type::IfcElectricDistributionPoint;
    string_map["IFCELECTRICFLOWSTORAGEDEVICETYPE"              ] = Type::IfcElectricFlowStorageDeviceType;
    string_map["IFCELECTRICGENERATORTYPE"                      ] = Type::IfcElectricGeneratorType;
    string_map["IFCELECTRICHEATERTYPE"                         ] = Type::IfcElectricHeaterType;
    string_map["IFCELECTRICMOTORTYPE"                          ] = Type::IfcElectricMotorType;
    string_map["IFCELECTRICTIMECONTROLTYPE"                    ] = Type::IfcElectricTimeControlType;
    string_map["IFCELECTRICALBASEPROPERTIES"                   ] = Type::IfcElectricalBaseProperties;
    string_map["IFCELECTRICALCIRCUIT"                          ] = Type::IfcElectricalCircuit;
    string_map["IFCELECTRICALELEMENT"                          ] = Type::IfcElectricalElement;
    string_map["IFCELEMENT"                                    ] = Type::IfcElement;
    string_map["IFCELEMENTASSEMBLY"                            ] = Type::IfcElementAssembly;
    string_map["IFCELEMENTCOMPONENT"                           ] = Type::IfcElementComponent;
    string_map["IFCELEMENTCOMPONENTTYPE"                       ] = Type::IfcElementComponentType;
    string_map["IFCELEMENTQUANTITY"                            ] = Type::IfcElementQuantity;
    string_map["IFCELEMENTTYPE"                                ] = Type::IfcElementType;
    string_map["IFCELEMENTARYSURFACE"                          ] = Type::IfcElementarySurface;
    string_map["IFCELLIPSE"                                    ] = Type::IfcEllipse;
    string_map["IFCELLIPSEPROFILEDEF"                          ] = Type::IfcEllipseProfileDef;
    string_map["IFCENERGYCONVERSIONDEVICE"                     ] = Type::IfcEnergyConversionDevice;
    string_map["IFCENERGYCONVERSIONDEVICETYPE"                 ] = Type::IfcEnergyConversionDeviceType;
    string_map["IFCENERGYPROPERTIES"                           ] = Type::IfcEnergyProperties;
    string_map["IFCENVIRONMENTALIMPACTVALUE"                   ] = Type::IfcEnvironmentalImpactValue;
    string_map["IFCEQUIPMENTELEMENT"                           ] = Type::IfcEquipmentElement;
    string_map["IFCEQUIPMENTSTANDARD"                          ] = Type::IfcEquipmentStandard;
    string_map["IFCEVAPORATIVECOOLERTYPE"                      ] = Type::IfcEvaporativeCoolerType;
    string_map["IFCEVAPORATORTYPE"                             ] = Type::IfcEvaporatorType;
    string_map["IFCEXTENDEDMATERIALPROPERTIES"                 ] = Type::IfcExtendedMaterialProperties;
    string_map["IFCEXTERNALREFERENCE"                          ] = Type::IfcExternalReference;
    string_map["IFCEXTERNALLYDEFINEDHATCHSTYLE"                ] = Type::IfcExternallyDefinedHatchStyle;
    string_map["IFCEXTERNALLYDEFINEDSURFACESTYLE"              ] = Type::IfcExternallyDefinedSurfaceStyle;
    string_map["IFCEXTERNALLYDEFINEDSYMBOL"                    ] = Type::IfcExternallyDefinedSymbol;
    string_map["IFCEXTERNALLYDEFINEDTEXTFONT"                  ] = Type::IfcExternallyDefinedTextFont;
    string_map["IFCEXTRUDEDAREASOLID"                          ] = Type::IfcExtrudedAreaSolid;
    string_map["IFCFACE"                                       ] = Type::IfcFace;
    string_map["IFCFACEBASEDSURFACEMODEL"                      ] = Type::IfcFaceBasedSurfaceModel;
    string_map["IFCFACEBOUND"                                  ] = Type::IfcFaceBound;
    string_map["IFCFACEOUTERBOUND"                             ] = Type::IfcFaceOuterBound;
    string_map["IFCFACESURFACE"                                ] = Type::IfcFaceSurface;
    string_map["IFCFACETEDBREP"                                ] = Type::IfcFacetedBrep;
    string_map["IFCFACETEDBREPWITHVOIDS"                       ] = Type::IfcFacetedBrepWithVoids;
    string_map["IFCFAILURECONNECTIONCONDITION"                 ] = Type::IfcFailureConnectionCondition;
    string_map["IFCFANTYPE"                                    ] = Type::IfcFanType;
    string_map["IFCFASTENER"                                   ] = Type::IfcFastener;
    string_map["IFCFASTENERTYPE"                               ] = Type::IfcFastenerType;
    string_map["IFCFEATUREELEMENT"                             ] = Type::IfcFeatureElement;
    string_map["IFCFEATUREELEMENTADDITION"                     ] = Type::IfcFeatureElementAddition;
    string_map["IFCFEATUREELEMENTSUBTRACTION"                  ] = Type::IfcFeatureElementSubtraction;
    string_map["IFCFILLAREASTYLE"                              ] = Type::IfcFillAreaStyle;
    string_map["IFCFILLAREASTYLEHATCHING"                      ] = Type::IfcFillAreaStyleHatching;
    string_map["IFCFILLAREASTYLETILESYMBOLWITHSTYLE"           ] = Type::IfcFillAreaStyleTileSymbolWithStyle;
    string_map["IFCFILLAREASTYLETILES"                         ] = Type::IfcFillAreaStyleTiles;
    string_map["IFCFILTERTYPE"                                 ] = Type::IfcFilterType;
    string_map["IFCFIRESUPPRESSIONTERMINALTYPE"                ] = Type::IfcFireSuppressionTerminalType;
    string_map["IFCFLOWCONTROLLER"                             ] = Type::IfcFlowController;
    string_map["IFCFLOWCONTROLLERTYPE"                         ] = Type::IfcFlowControllerType;
    string_map["IFCFLOWFITTING"                                ] = Type::IfcFlowFitting;
    string_map["IFCFLOWFITTINGTYPE"                            ] = Type::IfcFlowFittingType;
    string_map["IFCFLOWINSTRUMENTTYPE"                         ] = Type::IfcFlowInstrumentType;
    string_map["IFCFLOWMETERTYPE"                              ] = Type::IfcFlowMeterType;
    string_map["IFCFLOWMOVINGDEVICE"                           ] = Type::IfcFlowMovingDevice;
    string_map["IFCFLOWMOVINGDEVICETYPE"                       ] = Type::IfcFlowMovingDeviceType;
    string_map["IFCFLOWSEGMENT"                                ] = Type::IfcFlowSegment;
    string_map["IFCFLOWSEGMENTTYPE"                            ] = Type::IfcFlowSegmentType;
    string_map["IFCFLOWSTORAGEDEVICE"                          ] = Type::IfcFlowStorageDevice;
    string_map["IFCFLOWSTORAGEDEVICETYPE"                      ] = Type::IfcFlowStorageDeviceType;
    string_map["IFCFLOWTERMINAL"                               ] = Type::IfcFlowTerminal;
    string_map["IFCFLOWTERMINALTYPE"                           ] = Type::IfcFlowTerminalType;
    string_map["IFCFLOWTREATMENTDEVICE"                        ] = Type::IfcFlowTreatmentDevice;
    string_map["IFCFLOWTREATMENTDEVICETYPE"                    ] = Type::IfcFlowTreatmentDeviceType;
    string_map["IFCFLUIDFLOWPROPERTIES"                        ] = Type::IfcFluidFlowProperties;
    string_map["IFCFOOTING"                                    ] = Type::IfcFooting;
    string_map["IFCFUELPROPERTIES"                             ] = Type::IfcFuelProperties;
    string_map["IFCFURNISHINGELEMENT"                          ] = Type::IfcFurnishingElement;
    string_map["IFCFURNISHINGELEMENTTYPE"                      ] = Type::IfcFurnishingElementType;
    string_map["IFCFURNITURESTANDARD"                          ] = Type::IfcFurnitureStandard;
    string_map["IFCFURNITURETYPE"                              ] = Type::IfcFurnitureType;
    string_map["IFCGASTERMINALTYPE"                            ] = Type::IfcGasTerminalType;
    string_map["IFCGENERALMATERIALPROPERTIES"                  ] = Type::IfcGeneralMaterialProperties;
    string_map["IFCGENERALPROFILEPROPERTIES"                   ] = Type::IfcGeneralProfileProperties;
    string_map["IFCGEOMETRICCURVESET"                          ] = Type::IfcGeometricCurveSet;
    string_map["IFCGEOMETRICREPRESENTATIONCONTEXT"             ] = Type::IfcGeometricRepresentationContext;
    string_map["IFCGEOMETRICREPRESENTATIONITEM"                ] = Type::IfcGeometricRepresentationItem;
    string_map["IFCGEOMETRICREPRESENTATIONSUBCONTEXT"          ] = Type::IfcGeometricRepresentationSubContext;
    string_map["IFCGEOMETRICSET"                               ] = Type::IfcGeometricSet;
    string_map["IFCGRID"                                       ] = Type::IfcGrid;
    string_map["IFCGRIDAXIS"                                   ] = Type::IfcGridAxis;
    string_map["IFCGRIDPLACEMENT"                              ] = Type::IfcGridPlacement;
    string_map["IFCGROUP"                                      ] = Type::IfcGroup;
    string_map["IFCHALFSPACESOLID"                             ] = Type::IfcHalfSpaceSolid;
    string_map["IFCHEATEXCHANGERTYPE"                          ] = Type::IfcHeatExchangerType;
    string_map["IFCHUMIDIFIERTYPE"                             ] = Type::IfcHumidifierType;
    string_map["IFCHYGROSCOPICMATERIALPROPERTIES"              ] = Type::IfcHygroscopicMaterialProperties;
    string_map["IFCISHAPEPROFILEDEF"                           ] = Type::IfcIShapeProfileDef;
    string_map["IFCIMAGETEXTURE"                               ] = Type::IfcImageTexture;
    string_map["IFCINVENTORY"                                  ] = Type::IfcInventory;
    string_map["IFCIRREGULARTIMESERIES"                        ] = Type::IfcIrregularTimeSeries;
    string_map["IFCIRREGULARTIMESERIESVALUE"                   ] = Type::IfcIrregularTimeSeriesValue;
    string_map["IFCJUNCTIONBOXTYPE"                            ] = Type::IfcJunctionBoxType;
    string_map["IFCLSHAPEPROFILEDEF"                           ] = Type::IfcLShapeProfileDef;
    string_map["IFCLABORRESOURCE"                              ] = Type::IfcLaborResource;
    string_map["IFCLAMPTYPE"                                   ] = Type::IfcLampType;
    string_map["IFCLIBRARYINFORMATION"                         ] = Type::IfcLibraryInformation;
    string_map["IFCLIBRARYREFERENCE"                           ] = Type::IfcLibraryReference;
    string_map["IFCLIGHTDISTRIBUTIONDATA"                      ] = Type::IfcLightDistributionData;
    string_map["IFCLIGHTFIXTURETYPE"                           ] = Type::IfcLightFixtureType;
    string_map["IFCLIGHTINTENSITYDISTRIBUTION"                 ] = Type::IfcLightIntensityDistribution;
    string_map["IFCLIGHTSOURCE"                                ] = Type::IfcLightSource;
    string_map["IFCLIGHTSOURCEAMBIENT"                         ] = Type::IfcLightSourceAmbient;
    string_map["IFCLIGHTSOURCEDIRECTIONAL"                     ] = Type::IfcLightSourceDirectional;
    string_map["IFCLIGHTSOURCEGONIOMETRIC"                     ] = Type::IfcLightSourceGoniometric;
    string_map["IFCLIGHTSOURCEPOSITIONAL"                      ] = Type::IfcLightSourcePositional;
    string_map["IFCLIGHTSOURCESPOT"                            ] = Type::IfcLightSourceSpot;
    string_map["IFCLINE"                                       ] = Type::IfcLine;
    string_map["IFCLINEARDIMENSION"                            ] = Type::IfcLinearDimension;
    string_map["IFCLOCALPLACEMENT"                             ] = Type::IfcLocalPlacement;
    string_map["IFCLOCALTIME"                                  ] = Type::IfcLocalTime;
    string_map["IFCLOOP"                                       ] = Type::IfcLoop;
    string_map["IFCMANIFOLDSOLIDBREP"                          ] = Type::IfcManifoldSolidBrep;
    string_map["IFCMAPPEDITEM"                                 ] = Type::IfcMappedItem;
    string_map["IFCMATERIAL"                                   ] = Type::IfcMaterial;
    string_map["IFCMATERIALCLASSIFICATIONRELATIONSHIP"         ] = Type::IfcMaterialClassificationRelationship;
    string_map["IFCMATERIALDEFINITIONREPRESENTATION"           ] = Type::IfcMaterialDefinitionRepresentation;
    string_map["IFCMATERIALLAYER"                              ] = Type::IfcMaterialLayer;
    string_map["IFCMATERIALLAYERSET"                           ] = Type::IfcMaterialLayerSet;
    string_map["IFCMATERIALLAYERSETUSAGE"                      ] = Type::IfcMaterialLayerSetUsage;
    string_map["IFCMATERIALLIST"                               ] = Type::IfcMaterialList;
    string_map["IFCMATERIALPROPERTIES"                         ] = Type::IfcMaterialProperties;
    string_map["IFCMEASUREWITHUNIT"                            ] = Type::IfcMeasureWithUnit;
    string_map["IFCMECHANICALCONCRETEMATERIALPROPERTIES"       ] = Type::IfcMechanicalConcreteMaterialProperties;
    string_map["IFCMECHANICALFASTENER"                         ] = Type::IfcMechanicalFastener;
    string_map["IFCMECHANICALFASTENERTYPE"                     ] = Type::IfcMechanicalFastenerType;
    string_map["IFCMECHANICALMATERIALPROPERTIES"               ] = Type::IfcMechanicalMaterialProperties;
    string_map["IFCMECHANICALSTEELMATERIALPROPERTIES"          ] = Type::IfcMechanicalSteelMaterialProperties;
    string_map["IFCMEMBER"                                     ] = Type::IfcMember;
    string_map["IFCMEMBERTYPE"                                 ] = Type::IfcMemberType;
    string_map["IFCMETRIC"                                     ] = Type::IfcMetric;
    string_map["IFCMONETARYUNIT"                               ] = Type::IfcMonetaryUnit;
    string_map["IFCMOTORCONNECTIONTYPE"                        ] = Type::IfcMotorConnectionType;
    string_map["IFCMOVE"                                       ] = Type::IfcMove;
    string_map["IFCNAMEDUNIT"                                  ] = Type::IfcNamedUnit;
    string_map["IFCOBJECT"                                     ] = Type::IfcObject;
    string_map["IFCOBJECTDEFINITION"                           ] = Type::IfcObjectDefinition;
    string_map["IFCOBJECTPLACEMENT"                            ] = Type::IfcObjectPlacement;
    string_map["IFCOBJECTIVE"                                  ] = Type::IfcObjective;
    string_map["IFCOCCUPANT"                                   ] = Type::IfcOccupant;
    string_map["IFCOFFSETCURVE2D"                              ] = Type::IfcOffsetCurve2D;
    string_map["IFCOFFSETCURVE3D"                              ] = Type::IfcOffsetCurve3D;
    string_map["IFCONEDIRECTIONREPEATFACTOR"                   ] = Type::IfcOneDirectionRepeatFactor;
    string_map["IFCOPENSHELL"                                  ] = Type::IfcOpenShell;
    string_map["IFCOPENINGELEMENT"                             ] = Type::IfcOpeningElement;
    string_map["IFCOPTICALMATERIALPROPERTIES"                  ] = Type::IfcOpticalMaterialProperties;
    string_map["IFCORDERACTION"                                ] = Type::IfcOrderAction;
    string_map["IFCORGANIZATION"                               ] = Type::IfcOrganization;
    string_map["IFCORGANIZATIONRELATIONSHIP"                   ] = Type::IfcOrganizationRelationship;
    string_map["IFCORIENTEDEDGE"                               ] = Type::IfcOrientedEdge;
    string_map["IFCOUTLETTYPE"                                 ] = Type::IfcOutletType;
    string_map["IFCOWNERHISTORY"                               ] = Type::IfcOwnerHistory;
    string_map["IFCPARAMETERIZEDPROFILEDEF"                    ] = Type::IfcParameterizedProfileDef;
    string_map["IFCPATH"                                       ] = Type::IfcPath;
    string_map["IFCPERFORMANCEHISTORY"                         ] = Type::IfcPerformanceHistory;
    string_map["IFCPERMEABLECOVERINGPROPERTIES"                ] = Type::IfcPermeableCoveringProperties;
    string_map["IFCPERMIT"                                     ] = Type::IfcPermit;
    string_map["IFCPERSON"                                     ] = Type::IfcPerson;
    string_map["IFCPERSONANDORGANIZATION"                      ] = Type::IfcPersonAndOrganization;
    string_map["IFCPHYSICALCOMPLEXQUANTITY"                    ] = Type::IfcPhysicalComplexQuantity;
    string_map["IFCPHYSICALQUANTITY"                           ] = Type::IfcPhysicalQuantity;
    string_map["IFCPHYSICALSIMPLEQUANTITY"                     ] = Type::IfcPhysicalSimpleQuantity;
    string_map["IFCPILE"                                       ] = Type::IfcPile;
    string_map["IFCPIPEFITTINGTYPE"                            ] = Type::IfcPipeFittingType;
    string_map["IFCPIPESEGMENTTYPE"                            ] = Type::IfcPipeSegmentType;
    string_map["IFCPIXELTEXTURE"                               ] = Type::IfcPixelTexture;
    string_map["IFCPLACEMENT"                                  ] = Type::IfcPlacement;
    string_map["IFCPLANARBOX"                                  ] = Type::IfcPlanarBox;
    string_map["IFCPLANAREXTENT"                               ] = Type::IfcPlanarExtent;
    string_map["IFCPLANE"                                      ] = Type::IfcPlane;
    string_map["IFCPLATE"                                      ] = Type::IfcPlate;
    string_map["IFCPLATETYPE"                                  ] = Type::IfcPlateType;
    string_map["IFCPOINT"                                      ] = Type::IfcPoint;
    string_map["IFCPOINTONCURVE"                               ] = Type::IfcPointOnCurve;
    string_map["IFCPOINTONSURFACE"                             ] = Type::IfcPointOnSurface;
    string_map["IFCPOLYLOOP"                                   ] = Type::IfcPolyLoop;
    string_map["IFCPOLYGONALBOUNDEDHALFSPACE"                  ] = Type::IfcPolygonalBoundedHalfSpace;
    string_map["IFCPOLYLINE"                                   ] = Type::IfcPolyline;
    string_map["IFCPORT"                                       ] = Type::IfcPort;
    string_map["IFCPOSTALADDRESS"                              ] = Type::IfcPostalAddress;
    string_map["IFCPREDEFINEDCOLOUR"                           ] = Type::IfcPreDefinedColour;
    string_map["IFCPREDEFINEDCURVEFONT"                        ] = Type::IfcPreDefinedCurveFont;
    string_map["IFCPREDEFINEDDIMENSIONSYMBOL"                  ] = Type::IfcPreDefinedDimensionSymbol;
    string_map["IFCPREDEFINEDITEM"                             ] = Type::IfcPreDefinedItem;
    string_map["IFCPREDEFINEDPOINTMARKERSYMBOL"                ] = Type::IfcPreDefinedPointMarkerSymbol;
    string_map["IFCPREDEFINEDSYMBOL"                           ] = Type::IfcPreDefinedSymbol;
    string_map["IFCPREDEFINEDTERMINATORSYMBOL"                 ] = Type::IfcPreDefinedTerminatorSymbol;
    string_map["IFCPREDEFINEDTEXTFONT"                         ] = Type::IfcPreDefinedTextFont;
    string_map["IFCPRESENTATIONLAYERASSIGNMENT"                ] = Type::IfcPresentationLayerAssignment;
    string_map["IFCPRESENTATIONLAYERWITHSTYLE"                 ] = Type::IfcPresentationLayerWithStyle;
    string_map["IFCPRESENTATIONSTYLE"                          ] = Type::IfcPresentationStyle;
    string_map["IFCPRESENTATIONSTYLEASSIGNMENT"                ] = Type::IfcPresentationStyleAssignment;
    string_map["IFCPROCEDURE"                                  ] = Type::IfcProcedure;
    string_map["IFCPROCESS"                                    ] = Type::IfcProcess;
    string_map["IFCPRODUCT"                                    ] = Type::IfcProduct;
    string_map["IFCPRODUCTDEFINITIONSHAPE"                     ] = Type::IfcProductDefinitionShape;
    string_map["IFCPRODUCTREPRESENTATION"                      ] = Type::IfcProductRepresentation;
    string_map["IFCPRODUCTSOFCOMBUSTIONPROPERTIES"             ] = Type::IfcProductsOfCombustionProperties;
    string_map["IFCPROFILEDEF"                                 ] = Type::IfcProfileDef;
    string_map["IFCPROFILEPROPERTIES"                          ] = Type::IfcProfileProperties;
    string_map["IFCPROJECT"                                    ] = Type::IfcProject;
    string_map["IFCPROJECTORDER"                               ] = Type::IfcProjectOrder;
    string_map["IFCPROJECTORDERRECORD"                         ] = Type::IfcProjectOrderRecord;
    string_map["IFCPROJECTIONCURVE"                            ] = Type::IfcProjectionCurve;
    string_map["IFCPROJECTIONELEMENT"                          ] = Type::IfcProjectionElement;
    string_map["IFCPROPERTY"                                   ] = Type::IfcProperty;
    string_map["IFCPROPERTYBOUNDEDVALUE"                       ] = Type::IfcPropertyBoundedValue;
    string_map["IFCPROPERTYCONSTRAINTRELATIONSHIP"             ] = Type::IfcPropertyConstraintRelationship;
    string_map["IFCPROPERTYDEFINITION"                         ] = Type::IfcPropertyDefinition;
    string_map["IFCPROPERTYDEPENDENCYRELATIONSHIP"             ] = Type::IfcPropertyDependencyRelationship;
    string_map["IFCPROPERTYENUMERATEDVALUE"                    ] = Type::IfcPropertyEnumeratedValue;
    string_map["IFCPROPERTYENUMERATION"                        ] = Type::IfcPropertyEnumeration;
    string_map["IFCPROPERTYLISTVALUE"                          ] = Type::IfcPropertyListValue;
    string_map["IFCPROPERTYREFERENCEVALUE"                     ] = Type::IfcPropertyReferenceValue;
    string_map["IFCPROPERTYSET"                                ] = Type::IfcPropertySet;
    string_map["IFCPROPERTYSETDEFINITION"                      ] = Type::IfcPropertySetDefinition;
    string_map["IFCPROPERTYSINGLEVALUE"                        ] = Type::IfcPropertySingleValue;
    string_map["IFCPROPERTYTABLEVALUE"                         ] = Type::IfcPropertyTableValue;
    string_map["IFCPROTECTIVEDEVICETYPE"                       ] = Type::IfcProtectiveDeviceType;
    string_map["IFCPROXY"                                      ] = Type::IfcProxy;
    string_map["IFCPUMPTYPE"                                   ] = Type::IfcPumpType;
    string_map["IFCQUANTITYAREA"                               ] = Type::IfcQuantityArea;
    string_map["IFCQUANTITYCOUNT"                              ] = Type::IfcQuantityCount;
    string_map["IFCQUANTITYLENGTH"                             ] = Type::IfcQuantityLength;
    string_map["IFCQUANTITYTIME"                               ] = Type::IfcQuantityTime;
    string_map["IFCQUANTITYVOLUME"                             ] = Type::IfcQuantityVolume;
    string_map["IFCQUANTITYWEIGHT"                             ] = Type::IfcQuantityWeight;
    string_map["IFCRADIUSDIMENSION"                            ] = Type::IfcRadiusDimension;
    string_map["IFCRAILING"                                    ] = Type::IfcRailing;
    string_map["IFCRAILINGTYPE"                                ] = Type::IfcRailingType;
    string_map["IFCRAMP"                                       ] = Type::IfcRamp;
    string_map["IFCRAMPFLIGHT"                                 ] = Type::IfcRampFlight;
    string_map["IFCRAMPFLIGHTTYPE"                             ] = Type::IfcRampFlightType;
    string_map["IFCRATIONALBEZIERCURVE"                        ] = Type::IfcRationalBezierCurve;
    string_map["IFCRECTANGLEHOLLOWPROFILEDEF"                  ] = Type::IfcRectangleHollowProfileDef;
    string_map["IFCRECTANGLEPROFILEDEF"                        ] = Type::IfcRectangleProfileDef;
    string_map["IFCRECTANGULARPYRAMID"                         ] = Type::IfcRectangularPyramid;
    string_map["IFCRECTANGULARTRIMMEDSURFACE"                  ] = Type::IfcRectangularTrimmedSurface;
    string_map["IFCREFERENCESVALUEDOCUMENT"                    ] = Type::IfcReferencesValueDocument;
    string_map["IFCREGULARTIMESERIES"                          ] = Type::IfcRegularTimeSeries;
    string_map["IFCREINFORCEMENTBARPROPERTIES"                 ] = Type::IfcReinforcementBarProperties;
    string_map["IFCREINFORCEMENTDEFINITIONPROPERTIES"          ] = Type::IfcReinforcementDefinitionProperties;
    string_map["IFCREINFORCINGBAR"                             ] = Type::IfcReinforcingBar;
    string_map["IFCREINFORCINGELEMENT"                         ] = Type::IfcReinforcingElement;
    string_map["IFCREINFORCINGMESH"                            ] = Type::IfcReinforcingMesh;
    string_map["IFCRELAGGREGATES"                              ] = Type::IfcRelAggregates;
    string_map["IFCRELASSIGNS"                                 ] = Type::IfcRelAssigns;
    string_map["IFCRELASSIGNSTASKS"                            ] = Type::IfcRelAssignsTasks;
    string_map["IFCRELASSIGNSTOACTOR"                          ] = Type::IfcRelAssignsToActor;
    string_map["IFCRELASSIGNSTOCONTROL"                        ] = Type::IfcRelAssignsToControl;
    string_map["IFCRELASSIGNSTOGROUP"                          ] = Type::IfcRelAssignsToGroup;
    string_map["IFCRELASSIGNSTOPROCESS"                        ] = Type::IfcRelAssignsToProcess;
    string_map["IFCRELASSIGNSTOPRODUCT"                        ] = Type::IfcRelAssignsToProduct;
    string_map["IFCRELASSIGNSTOPROJECTORDER"                   ] = Type::IfcRelAssignsToProjectOrder;
    string_map["IFCRELASSIGNSTORESOURCE"                       ] = Type::IfcRelAssignsToResource;
    string_map["IFCRELASSOCIATES"                              ] = Type::IfcRelAssociates;
    string_map["IFCRELASSOCIATESAPPLIEDVALUE"                  ] = Type::IfcRelAssociatesAppliedValue;
    string_map["IFCRELASSOCIATESAPPROVAL"                      ] = Type::IfcRelAssociatesApproval;
    string_map["IFCRELASSOCIATESCLASSIFICATION"                ] = Type::IfcRelAssociatesClassification;
    string_map["IFCRELASSOCIATESCONSTRAINT"                    ] = Type::IfcRelAssociatesConstraint;
    string_map["IFCRELASSOCIATESDOCUMENT"                      ] = Type::IfcRelAssociatesDocument;
    string_map["IFCRELASSOCIATESLIBRARY"                       ] = Type::IfcRelAssociatesLibrary;
    string_map["IFCRELASSOCIATESMATERIAL"                      ] = Type::IfcRelAssociatesMaterial;
    string_map["IFCRELASSOCIATESPROFILEPROPERTIES"             ] = Type::IfcRelAssociatesProfileProperties;
    string_map["IFCRELCONNECTS"                                ] = Type::IfcRelConnects;
    string_map["IFCRELCONNECTSELEMENTS"                        ] = Type::IfcRelConnectsElements;
    string_map["IFCRELCONNECTSPATHELEMENTS"                    ] = Type::IfcRelConnectsPathElements;
    string_map["IFCRELCONNECTSPORTTOELEMENT"                   ] = Type::IfcRelConnectsPortToElement;
    string_map["IFCRELCONNECTSPORTS"                           ] = Type::IfcRelConnectsPorts;
    string_map["IFCRELCONNECTSSTRUCTURALACTIVITY"              ] = Type::IfcRelConnectsStructuralActivity;
    string_map["IFCRELCONNECTSSTRUCTURALELEMENT"               ] = Type::IfcRelConnectsStructuralElement;
    string_map["IFCRELCONNECTSSTRUCTURALMEMBER"                ] = Type::IfcRelConnectsStructuralMember;
    string_map["IFCRELCONNECTSWITHECCENTRICITY"                ] = Type::IfcRelConnectsWithEccentricity;
    string_map["IFCRELCONNECTSWITHREALIZINGELEMENTS"           ] = Type::IfcRelConnectsWithRealizingElements;
    string_map["IFCRELCONTAINEDINSPATIALSTRUCTURE"             ] = Type::IfcRelContainedInSpatialStructure;
    string_map["IFCRELCOVERSBLDGELEMENTS"                      ] = Type::IfcRelCoversBldgElements;
    string_map["IFCRELCOVERSSPACES"                            ] = Type::IfcRelCoversSpaces;
    string_map["IFCRELDECOMPOSES"                              ] = Type::IfcRelDecomposes;
    string_map["IFCRELDEFINES"                                 ] = Type::IfcRelDefines;
    string_map["IFCRELDEFINESBYPROPERTIES"                     ] = Type::IfcRelDefinesByProperties;
    string_map["IFCRELDEFINESBYTYPE"                           ] = Type::IfcRelDefinesByType;
    string_map["IFCRELFILLSELEMENT"                            ] = Type::IfcRelFillsElement;
    string_map["IFCRELFLOWCONTROLELEMENTS"                     ] = Type::IfcRelFlowControlElements;
    string_map["IFCRELINTERACTIONREQUIREMENTS"                 ] = Type::IfcRelInteractionRequirements;
    string_map["IFCRELNESTS"                                   ] = Type::IfcRelNests;
    string_map["IFCRELOCCUPIESSPACES"                          ] = Type::IfcRelOccupiesSpaces;
    string_map["IFCRELOVERRIDESPROPERTIES"                     ] = Type::IfcRelOverridesProperties;
    string_map["IFCRELPROJECTSELEMENT"                         ] = Type::IfcRelProjectsElement;
    string_map["IFCRELREFERENCEDINSPATIALSTRUCTURE"            ] = Type::IfcRelReferencedInSpatialStructure;
    string_map["IFCRELSCHEDULESCOSTITEMS"                      ] = Type::IfcRelSchedulesCostItems;
    string_map["IFCRELSEQUENCE"                                ] = Type::IfcRelSequence;
    string_map["IFCRELSERVICESBUILDINGS"                       ] = Type::IfcRelServicesBuildings;
    string_map["IFCRELSPACEBOUNDARY"                           ] = Type::IfcRelSpaceBoundary;
    string_map["IFCRELVOIDSELEMENT"                            ] = Type::IfcRelVoidsElement;
    string_map["IFCRELATIONSHIP"                               ] = Type::IfcRelationship;
    string_map["IFCRELAXATION"                                 ] = Type::IfcRelaxation;
    string_map["IFCREPRESENTATION"                             ] = Type::IfcRepresentation;
    string_map["IFCREPRESENTATIONCONTEXT"                      ] = Type::IfcRepresentationContext;
    string_map["IFCREPRESENTATIONITEM"                         ] = Type::IfcRepresentationItem;
    string_map["IFCREPRESENTATIONMAP"                          ] = Type::IfcRepresentationMap;
    string_map["IFCRESOURCE"                                   ] = Type::IfcResource;
    string_map["IFCREVOLVEDAREASOLID"                          ] = Type::IfcRevolvedAreaSolid;
    string_map["IFCRIBPLATEPROFILEPROPERTIES"                  ] = Type::IfcRibPlateProfileProperties;
    string_map["IFCRIGHTCIRCULARCONE"                          ] = Type::IfcRightCircularCone;
    string_map["IFCRIGHTCIRCULARCYLINDER"                      ] = Type::IfcRightCircularCylinder;
    string_map["IFCROOF"                                       ] = Type::IfcRoof;
    string_map["IFCROOT"                                       ] = Type::IfcRoot;
    string_map["IFCROUNDEDEDGEFEATURE"                         ] = Type::IfcRoundedEdgeFeature;
    string_map["IFCROUNDEDRECTANGLEPROFILEDEF"                 ] = Type::IfcRoundedRectangleProfileDef;
    string_map["IFCSIUNIT"                                     ] = Type::IfcSIUnit;
    string_map["IFCSANITARYTERMINALTYPE"                       ] = Type::IfcSanitaryTerminalType;
    string_map["IFCSCHEDULETIMECONTROL"                        ] = Type::IfcScheduleTimeControl;
    string_map["IFCSECTIONPROPERTIES"                          ] = Type::IfcSectionProperties;
    string_map["IFCSECTIONREINFORCEMENTPROPERTIES"             ] = Type::IfcSectionReinforcementProperties;
    string_map["IFCSECTIONEDSPINE"                             ] = Type::IfcSectionedSpine;
    string_map["IFCSENSORTYPE"                                 ] = Type::IfcSensorType;
    string_map["IFCSERVICELIFE"                                ] = Type::IfcServiceLife;
    string_map["IFCSERVICELIFEFACTOR"                          ] = Type::IfcServiceLifeFactor;
    string_map["IFCSHAPEASPECT"                                ] = Type::IfcShapeAspect;
    string_map["IFCSHAPEMODEL"                                 ] = Type::IfcShapeModel;
    string_map["IFCSHAPEREPRESENTATION"                        ] = Type::IfcShapeRepresentation;
    string_map["IFCSHELLBASEDSURFACEMODEL"                     ] = Type::IfcShellBasedSurfaceModel;
    string_map["IFCSIMPLEPROPERTY"                             ] = Type::IfcSimpleProperty;
    string_map["IFCSITE"                                       ] = Type::IfcSite;
    string_map["IFCSLAB"                                       ] = Type::IfcSlab;
    string_map["IFCSLABTYPE"                                   ] = Type::IfcSlabType;
    string_map["IFCSLIPPAGECONNECTIONCONDITION"                ] = Type::IfcSlippageConnectionCondition;
    string_map["IFCSOLIDMODEL"                                 ] = Type::IfcSolidModel;
    string_map["IFCSOUNDPROPERTIES"                            ] = Type::IfcSoundProperties;
    string_map["IFCSOUNDVALUE"                                 ] = Type::IfcSoundValue;
    string_map["IFCSPACE"                                      ] = Type::IfcSpace;
    string_map["IFCSPACEHEATERTYPE"                            ] = Type::IfcSpaceHeaterType;
    string_map["IFCSPACEPROGRAM"                               ] = Type::IfcSpaceProgram;
    string_map["IFCSPACETHERMALLOADPROPERTIES"                 ] = Type::IfcSpaceThermalLoadProperties;
    string_map["IFCSPACETYPE"                                  ] = Type::IfcSpaceType;
    string_map["IFCSPATIALSTRUCTUREELEMENT"                    ] = Type::IfcSpatialStructureElement;
    string_map["IFCSPATIALSTRUCTUREELEMENTTYPE"                ] = Type::IfcSpatialStructureElementType;
    string_map["IFCSPHERE"                                     ] = Type::IfcSphere;
    string_map["IFCSTACKTERMINALTYPE"                          ] = Type::IfcStackTerminalType;
    string_map["IFCSTAIR"                                      ] = Type::IfcStair;
    string_map["IFCSTAIRFLIGHT"                                ] = Type::IfcStairFlight;
    string_map["IFCSTAIRFLIGHTTYPE"                            ] = Type::IfcStairFlightType;
    string_map["IFCSTRUCTURALACTION"                           ] = Type::IfcStructuralAction;
    string_map["IFCSTRUCTURALACTIVITY"                         ] = Type::IfcStructuralActivity;
    string_map["IFCSTRUCTURALANALYSISMODEL"                    ] = Type::IfcStructuralAnalysisModel;
    string_map["IFCSTRUCTURALCONNECTION"                       ] = Type::IfcStructuralConnection;
    string_map["IFCSTRUCTURALCONNECTIONCONDITION"              ] = Type::IfcStructuralConnectionCondition;
    string_map["IFCSTRUCTURALCURVECONNECTION"                  ] = Type::IfcStructuralCurveConnection;
    string_map["IFCSTRUCTURALCURVEMEMBER"                      ] = Type::IfcStructuralCurveMember;
    string_map["IFCSTRUCTURALCURVEMEMBERVARYING"               ] = Type::IfcStructuralCurveMemberVarying;
    string_map["IFCSTRUCTURALITEM"                             ] = Type::IfcStructuralItem;
    string_map["IFCSTRUCTURALLINEARACTION"                     ] = Type::IfcStructuralLinearAction;
    string_map["IFCSTRUCTURALLINEARACTIONVARYING"              ] = Type::IfcStructuralLinearActionVarying;
    string_map["IFCSTRUCTURALLOAD"                             ] = Type::IfcStructuralLoad;
    string_map["IFCSTRUCTURALLOADGROUP"                        ] = Type::IfcStructuralLoadGroup;
    string_map["IFCSTRUCTURALLOADLINEARFORCE"                  ] = Type::IfcStructuralLoadLinearForce;
    string_map["IFCSTRUCTURALLOADPLANARFORCE"                  ] = Type::IfcStructuralLoadPlanarForce;
    string_map["IFCSTRUCTURALLOADSINGLEDISPLACEMENT"           ] = Type::IfcStructuralLoadSingleDisplacement;
    string_map["IFCSTRUCTURALLOADSINGLEDISPLACEMENTDISTORTION" ] = Type::IfcStructuralLoadSingleDisplacementDistortion;
    string_map["IFCSTRUCTURALLOADSINGLEFORCE"                  ] = Type::IfcStructuralLoadSingleForce;
    string_map["IFCSTRUCTURALLOADSINGLEFORCEWARPING"           ] = Type::IfcStructuralLoadSingleForceWarping;
    string_map["IFCSTRUCTURALLOADSTATIC"                       ] = Type::IfcStructuralLoadStatic;
    string_map["IFCSTRUCTURALLOADTEMPERATURE"                  ] = Type::IfcStructuralLoadTemperature;
    string_map["IFCSTRUCTURALMEMBER"                           ] = Type::IfcStructuralMember;
    string_map["IFCSTRUCTURALPLANARACTION"                     ] = Type::IfcStructuralPlanarAction;
    string_map["IFCSTRUCTURALPLANARACTIONVARYING"              ] = Type::IfcStructuralPlanarActionVarying;
    string_map["IFCSTRUCTURALPOINTACTION"                      ] = Type::IfcStructuralPointAction;
    string_map["IFCSTRUCTURALPOINTCONNECTION"                  ] = Type::IfcStructuralPointConnection;
    string_map["IFCSTRUCTURALPOINTREACTION"                    ] = Type::IfcStructuralPointReaction;
    string_map["IFCSTRUCTURALPROFILEPROPERTIES"                ] = Type::IfcStructuralProfileProperties;
    string_map["IFCSTRUCTURALREACTION"                         ] = Type::IfcStructuralReaction;
    string_map["IFCSTRUCTURALRESULTGROUP"                      ] = Type::IfcStructuralResultGroup;
    string_map["IFCSTRUCTURALSTEELPROFILEPROPERTIES"           ] = Type::IfcStructuralSteelProfileProperties;
    string_map["IFCSTRUCTURALSURFACECONNECTION"                ] = Type::IfcStructuralSurfaceConnection;
    string_map["IFCSTRUCTURALSURFACEMEMBER"                    ] = Type::IfcStructuralSurfaceMember;
    string_map["IFCSTRUCTURALSURFACEMEMBERVARYING"             ] = Type::IfcStructuralSurfaceMemberVarying;
    string_map["IFCSTRUCTUREDDIMENSIONCALLOUT"                 ] = Type::IfcStructuredDimensionCallout;
    string_map["IFCSTYLEMODEL"                                 ] = Type::IfcStyleModel;
    string_map["IFCSTYLEDITEM"                                 ] = Type::IfcStyledItem;
    string_map["IFCSTYLEDREPRESENTATION"                       ] = Type::IfcStyledRepresentation;
    string_map["IFCSUBCONTRACTRESOURCE"                        ] = Type::IfcSubContractResource;
    string_map["IFCSUBEDGE"                                    ] = Type::IfcSubedge;
    string_map["IFCSURFACE"                                    ] = Type::IfcSurface;
    string_map["IFCSURFACECURVESWEPTAREASOLID"                 ] = Type::IfcSurfaceCurveSweptAreaSolid;
    string_map["IFCSURFACEOFLINEAREXTRUSION"                   ] = Type::IfcSurfaceOfLinearExtrusion;
    string_map["IFCSURFACEOFREVOLUTION"                        ] = Type::IfcSurfaceOfRevolution;
    string_map["IFCSURFACESTYLE"                               ] = Type::IfcSurfaceStyle;
    string_map["IFCSURFACESTYLELIGHTING"                       ] = Type::IfcSurfaceStyleLighting;
    string_map["IFCSURFACESTYLEREFRACTION"                     ] = Type::IfcSurfaceStyleRefraction;
    string_map["IFCSURFACESTYLERENDERING"                      ] = Type::IfcSurfaceStyleRendering;
    string_map["IFCSURFACESTYLESHADING"                        ] = Type::IfcSurfaceStyleShading;
    string_map["IFCSURFACESTYLEWITHTEXTURES"                   ] = Type::IfcSurfaceStyleWithTextures;
    string_map["IFCSURFACETEXTURE"                             ] = Type::IfcSurfaceTexture;
    string_map["IFCSWEPTAREASOLID"                             ] = Type::IfcSweptAreaSolid;
    string_map["IFCSWEPTDISKSOLID"                             ] = Type::IfcSweptDiskSolid;
    string_map["IFCSWEPTSURFACE"                               ] = Type::IfcSweptSurface;
    string_map["IFCSWITCHINGDEVICETYPE"                        ] = Type::IfcSwitchingDeviceType;
    string_map["IFCSYMBOLSTYLE"                                ] = Type::IfcSymbolStyle;
    string_map["IFCSYSTEM"                                     ] = Type::IfcSystem;
    string_map["IFCSYSTEMFURNITUREELEMENTTYPE"                 ] = Type::IfcSystemFurnitureElementType;
    string_map["IFCTSHAPEPROFILEDEF"                           ] = Type::IfcTShapeProfileDef;
    string_map["IFCTABLE"                                      ] = Type::IfcTable;
    string_map["IFCTABLEROW"                                   ] = Type::IfcTableRow;
    string_map["IFCTANKTYPE"                                   ] = Type::IfcTankType;
    string_map["IFCTASK"                                       ] = Type::IfcTask;
    string_map["IFCTELECOMADDRESS"                             ] = Type::IfcTelecomAddress;
    string_map["IFCTENDON"                                     ] = Type::IfcTendon;
    string_map["IFCTENDONANCHOR"                               ] = Type::IfcTendonAnchor;
    string_map["IFCTERMINATORSYMBOL"                           ] = Type::IfcTerminatorSymbol;
    string_map["IFCTEXTLITERAL"                                ] = Type::IfcTextLiteral;
    string_map["IFCTEXTLITERALWITHEXTENT"                      ] = Type::IfcTextLiteralWithExtent;
    string_map["IFCTEXTSTYLE"                                  ] = Type::IfcTextStyle;
    string_map["IFCTEXTSTYLEFONTMODEL"                         ] = Type::IfcTextStyleFontModel;
    string_map["IFCTEXTSTYLEFORDEFINEDFONT"                    ] = Type::IfcTextStyleForDefinedFont;
    string_map["IFCTEXTSTYLETEXTMODEL"                         ] = Type::IfcTextStyleTextModel;
    string_map["IFCTEXTSTYLEWITHBOXCHARACTERISTICS"            ] = Type::IfcTextStyleWithBoxCharacteristics;
    string_map["IFCTEXTURECOORDINATE"                          ] = Type::IfcTextureCoordinate;
    string_map["IFCTEXTURECOORDINATEGENERATOR"                 ] = Type::IfcTextureCoordinateGenerator;
    string_map["IFCTEXTUREMAP"                                 ] = Type::IfcTextureMap;
    string_map["IFCTEXTUREVERTEX"                              ] = Type::IfcTextureVertex;
    string_map["IFCTHERMALMATERIALPROPERTIES"                  ] = Type::IfcThermalMaterialProperties;
    string_map["IFCTIMESERIES"                                 ] = Type::IfcTimeSeries;
    string_map["IFCTIMESERIESREFERENCERELATIONSHIP"            ] = Type::IfcTimeSeriesReferenceRelationship;
    string_map["IFCTIMESERIESSCHEDULE"                         ] = Type::IfcTimeSeriesSchedule;
    string_map["IFCTIMESERIESVALUE"                            ] = Type::IfcTimeSeriesValue;
    string_map["IFCTOPOLOGICALREPRESENTATIONITEM"              ] = Type::IfcTopologicalRepresentationItem;
    string_map["IFCTOPOLOGYREPRESENTATION"                     ] = Type::IfcTopologyRepresentation;
    string_map["IFCTRANSFORMERTYPE"                            ] = Type::IfcTransformerType;
    string_map["IFCTRANSPORTELEMENT"                           ] = Type::IfcTransportElement;
    string_map["IFCTRANSPORTELEMENTTYPE"                       ] = Type::IfcTransportElementType;
    string_map["IFCTRAPEZIUMPROFILEDEF"                        ] = Type::IfcTrapeziumProfileDef;
    string_map["IFCTRIMMEDCURVE"                               ] = Type::IfcTrimmedCurve;
    string_map["IFCTUBEBUNDLETYPE"                             ] = Type::IfcTubeBundleType;
    string_map["IFCTWODIRECTIONREPEATFACTOR"                   ] = Type::IfcTwoDirectionRepeatFactor;
    string_map["IFCTYPEOBJECT"                                 ] = Type::IfcTypeObject;
    string_map["IFCTYPEPRODUCT"                                ] = Type::IfcTypeProduct;
    string_map["IFCUSHAPEPROFILEDEF"                           ] = Type::IfcUShapeProfileDef;
    string_map["IFCUNITASSIGNMENT"                             ] = Type::IfcUnitAssignment;
    string_map["IFCUNITARYEQUIPMENTTYPE"                       ] = Type::IfcUnitaryEquipmentType;
    string_map["IFCVALVETYPE"                                  ] = Type::IfcValveType;
    string_map["IFCVECTOR"                                     ] = Type::IfcVector;
    string_map["IFCVERTEX"                                     ] = Type::IfcVertex;
    string_map["IFCVERTEXBASEDTEXTUREMAP"                      ] = Type::IfcVertexBasedTextureMap;
    string_map["IFCVERTEXLOOP"                                 ] = Type::IfcVertexLoop;
    string_map["IFCVERTEXPOINT"                                ] = Type::IfcVertexPoint;
    string_map["IFCVIBRATIONISOLATORTYPE"                      ] = Type::IfcVibrationIsolatorType;
    string_map["IFCVIRTUALELEMENT"                             ] = Type::IfcVirtualElement;
    string_map["IFCVIRTUALGRIDINTERSECTION"                    ] = Type::IfcVirtualGridIntersection;
    string_map["IFCWALL"                                       ] = Type::IfcWall;
    string_map["IFCWALLSTANDARDCASE"                           ] = Type::IfcWallStandardCase;
    string_map["IFCWALLTYPE"                                   ] = Type::IfcWallType;
    string_map["IFCWASTETERMINALTYPE"                          ] = Type::IfcWasteTerminalType;
    string_map["IFCWATERPROPERTIES"                            ] = Type::IfcWaterProperties;
    string_map["IFCWINDOW"                                     ] = Type::IfcWindow;
    string_map["IFCWINDOWLININGPROPERTIES"                     ] = Type::IfcWindowLiningProperties;
    string_map["IFCWINDOWPANELPROPERTIES"                      ] = Type::IfcWindowPanelProperties;
    string_map["IFCWINDOWSTYLE"                                ] = Type::IfcWindowStyle;
    string_map["IFCWORKCONTROL"                                ] = Type::IfcWorkControl;
    string_map["IFCWORKPLAN"                                   ] = Type::IfcWorkPlan;
    string_map["IFCWORKSCHEDULE"                               ] = Type::IfcWorkSchedule;
    string_map["IFCZSHAPEPROFILEDEF"                           ] = Type::IfcZShapeProfileDef;
    string_map["IFCZONE"                                       ] = Type::IfcZone;
}
Type::Enum Type::FromString(const std::string& s) {
    std::map<std::string,Type::Enum>::const_iterator it = string_map.find(s);
    if ( it == string_map.end() ) throw IfcException("Unable to find find keyword in schema");
    else return it->second;
}
Type::Enum Type::Parent(Enum v){
    if (v < 0 || v >= 758) return (Enum)-1;
    if(v==Ifc2DCompositeCurve                           ) { return IfcCompositeCurve; }
    if(v==IfcActionRequest                              ) { return IfcControl; }
    if(v==IfcActor                                      ) { return IfcObject; }
    if(v==IfcActuatorType                               ) { return IfcDistributionControlElementType; }
    if(v==IfcAirTerminalBoxType                         ) { return IfcFlowControllerType; }
    if(v==IfcAirTerminalType                            ) { return IfcFlowTerminalType; }
    if(v==IfcAirToAirHeatRecoveryType                   ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcAlarmType                                  ) { return IfcDistributionControlElementType; }
    if(v==IfcAngularDimension                           ) { return IfcDimensionCurveDirectedCallout; }
    if(v==IfcAnnotation                                 ) { return IfcProduct; }
    if(v==IfcAnnotationCurveOccurrence                  ) { return IfcAnnotationOccurrence; }
    if(v==IfcAnnotationFillArea                         ) { return IfcGeometricRepresentationItem; }
    if(v==IfcAnnotationFillAreaOccurrence               ) { return IfcAnnotationOccurrence; }
    if(v==IfcAnnotationOccurrence                       ) { return IfcStyledItem; }
    if(v==IfcAnnotationSurface                          ) { return IfcGeometricRepresentationItem; }
    if(v==IfcAnnotationSurfaceOccurrence                ) { return IfcAnnotationOccurrence; }
    if(v==IfcAnnotationSymbolOccurrence                 ) { return IfcAnnotationOccurrence; }
    if(v==IfcAnnotationTextOccurrence                   ) { return IfcAnnotationOccurrence; }
    if(v==IfcArbitraryClosedProfileDef                  ) { return IfcProfileDef; }
    if(v==IfcArbitraryOpenProfileDef                    ) { return IfcProfileDef; }
    if(v==IfcArbitraryProfileDefWithVoids               ) { return IfcArbitraryClosedProfileDef; }
    if(v==IfcAsset                                      ) { return IfcGroup; }
    if(v==IfcAsymmetricIShapeProfileDef                 ) { return IfcIShapeProfileDef; }
    if(v==IfcAxis1Placement                             ) { return IfcPlacement; }
    if(v==IfcAxis2Placement2D                           ) { return IfcPlacement; }
    if(v==IfcAxis2Placement3D                           ) { return IfcPlacement; }
    if(v==IfcBSplineCurve                               ) { return IfcBoundedCurve; }
    if(v==IfcBeam                                       ) { return IfcBuildingElement; }
    if(v==IfcBeamType                                   ) { return IfcBuildingElementType; }
    if(v==IfcBezierCurve                                ) { return IfcBSplineCurve; }
    if(v==IfcBlobTexture                                ) { return IfcSurfaceTexture; }
    if(v==IfcBlock                                      ) { return IfcCsgPrimitive3D; }
    if(v==IfcBoilerType                                 ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcBooleanClippingResult                      ) { return IfcBooleanResult; }
    if(v==IfcBooleanResult                              ) { return IfcGeometricRepresentationItem; }
    if(v==IfcBoundaryEdgeCondition                      ) { return IfcBoundaryCondition; }
    if(v==IfcBoundaryFaceCondition                      ) { return IfcBoundaryCondition; }
    if(v==IfcBoundaryNodeCondition                      ) { return IfcBoundaryCondition; }
    if(v==IfcBoundaryNodeConditionWarping               ) { return IfcBoundaryNodeCondition; }
    if(v==IfcBoundedCurve                               ) { return IfcCurve; }
    if(v==IfcBoundedSurface                             ) { return IfcSurface; }
    if(v==IfcBoundingBox                                ) { return IfcGeometricRepresentationItem; }
    if(v==IfcBoxedHalfSpace                             ) { return IfcHalfSpaceSolid; }
    if(v==IfcBuilding                                   ) { return IfcSpatialStructureElement; }
    if(v==IfcBuildingElement                            ) { return IfcElement; }
    if(v==IfcBuildingElementComponent                   ) { return IfcBuildingElement; }
    if(v==IfcBuildingElementPart                        ) { return IfcBuildingElementComponent; }
    if(v==IfcBuildingElementProxy                       ) { return IfcBuildingElement; }
    if(v==IfcBuildingElementProxyType                   ) { return IfcBuildingElementType; }
    if(v==IfcBuildingElementType                        ) { return IfcElementType; }
    if(v==IfcBuildingStorey                             ) { return IfcSpatialStructureElement; }
    if(v==IfcCShapeProfileDef                           ) { return IfcParameterizedProfileDef; }
    if(v==IfcCableCarrierFittingType                    ) { return IfcFlowFittingType; }
    if(v==IfcCableCarrierSegmentType                    ) { return IfcFlowSegmentType; }
    if(v==IfcCableSegmentType                           ) { return IfcFlowSegmentType; }
    if(v==IfcCartesianPoint                             ) { return IfcPoint; }
    if(v==IfcCartesianTransformationOperator            ) { return IfcGeometricRepresentationItem; }
    if(v==IfcCartesianTransformationOperator2D          ) { return IfcCartesianTransformationOperator; }
    if(v==IfcCartesianTransformationOperator2DnonUniform) { return IfcCartesianTransformationOperator2D; }
    if(v==IfcCartesianTransformationOperator3D          ) { return IfcCartesianTransformationOperator; }
    if(v==IfcCartesianTransformationOperator3DnonUniform) { return IfcCartesianTransformationOperator3D; }
    if(v==IfcCenterLineProfileDef                       ) { return IfcArbitraryOpenProfileDef; }
    if(v==IfcChamferEdgeFeature                         ) { return IfcEdgeFeature; }
    if(v==IfcChillerType                                ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcCircle                                     ) { return IfcConic; }
    if(v==IfcCircleHollowProfileDef                     ) { return IfcCircleProfileDef; }
    if(v==IfcCircleProfileDef                           ) { return IfcParameterizedProfileDef; }
    if(v==IfcClassificationReference                    ) { return IfcExternalReference; }
    if(v==IfcClosedShell                                ) { return IfcConnectedFaceSet; }
    if(v==IfcCoilType                                   ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcColourRgb                                  ) { return IfcColourSpecification; }
    if(v==IfcColumn                                     ) { return IfcBuildingElement; }
    if(v==IfcColumnType                                 ) { return IfcBuildingElementType; }
    if(v==IfcComplexProperty                            ) { return IfcProperty; }
    if(v==IfcCompositeCurve                             ) { return IfcBoundedCurve; }
    if(v==IfcCompositeCurveSegment                      ) { return IfcGeometricRepresentationItem; }
    if(v==IfcCompositeProfileDef                        ) { return IfcProfileDef; }
    if(v==IfcCompressorType                             ) { return IfcFlowMovingDeviceType; }
    if(v==IfcCondenserType                              ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcCondition                                  ) { return IfcGroup; }
    if(v==IfcConditionCriterion                         ) { return IfcControl; }
    if(v==IfcConic                                      ) { return IfcCurve; }
    if(v==IfcConnectedFaceSet                           ) { return IfcTopologicalRepresentationItem; }
    if(v==IfcConnectionCurveGeometry                    ) { return IfcConnectionGeometry; }
    if(v==IfcConnectionPointEccentricity                ) { return IfcConnectionPointGeometry; }
    if(v==IfcConnectionPointGeometry                    ) { return IfcConnectionGeometry; }
    if(v==IfcConnectionPortGeometry                     ) { return IfcConnectionGeometry; }
    if(v==IfcConnectionSurfaceGeometry                  ) { return IfcConnectionGeometry; }
    if(v==IfcConstructionEquipmentResource              ) { return IfcConstructionResource; }
    if(v==IfcConstructionMaterialResource               ) { return IfcConstructionResource; }
    if(v==IfcConstructionProductResource                ) { return IfcConstructionResource; }
    if(v==IfcConstructionResource                       ) { return IfcResource; }
    if(v==IfcContextDependentUnit                       ) { return IfcNamedUnit; }
    if(v==IfcControl                                    ) { return IfcObject; }
    if(v==IfcControllerType                             ) { return IfcDistributionControlElementType; }
    if(v==IfcConversionBasedUnit                        ) { return IfcNamedUnit; }
    if(v==IfcCooledBeamType                             ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcCoolingTowerType                           ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcCostItem                                   ) { return IfcControl; }
    if(v==IfcCostSchedule                               ) { return IfcControl; }
    if(v==IfcCostValue                                  ) { return IfcAppliedValue; }
    if(v==IfcCovering                                   ) { return IfcBuildingElement; }
    if(v==IfcCoveringType                               ) { return IfcBuildingElementType; }
    if(v==IfcCraneRailAShapeProfileDef                  ) { return IfcParameterizedProfileDef; }
    if(v==IfcCraneRailFShapeProfileDef                  ) { return IfcParameterizedProfileDef; }
    if(v==IfcCrewResource                               ) { return IfcConstructionResource; }
    if(v==IfcCsgPrimitive3D                             ) { return IfcGeometricRepresentationItem; }
    if(v==IfcCsgSolid                                   ) { return IfcSolidModel; }
    if(v==IfcCurtainWall                                ) { return IfcBuildingElement; }
    if(v==IfcCurtainWallType                            ) { return IfcBuildingElementType; }
    if(v==IfcCurve                                      ) { return IfcGeometricRepresentationItem; }
    if(v==IfcCurveBoundedPlane                          ) { return IfcBoundedSurface; }
    if(v==IfcCurveStyle                                 ) { return IfcPresentationStyle; }
    if(v==IfcDamperType                                 ) { return IfcFlowControllerType; }
    if(v==IfcDefinedSymbol                              ) { return IfcGeometricRepresentationItem; }
    if(v==IfcDerivedProfileDef                          ) { return IfcProfileDef; }
    if(v==IfcDiameterDimension                          ) { return IfcDimensionCurveDirectedCallout; }
    if(v==IfcDimensionCalloutRelationship               ) { return IfcDraughtingCalloutRelationship; }
    if(v==IfcDimensionCurve                             ) { return IfcAnnotationCurveOccurrence; }
    if(v==IfcDimensionCurveDirectedCallout              ) { return IfcDraughtingCallout; }
    if(v==IfcDimensionCurveTerminator                   ) { return IfcTerminatorSymbol; }
    if(v==IfcDimensionPair                              ) { return IfcDraughtingCalloutRelationship; }
    if(v==IfcDirection                                  ) { return IfcGeometricRepresentationItem; }
    if(v==IfcDiscreteAccessory                          ) { return IfcElementComponent; }
    if(v==IfcDiscreteAccessoryType                      ) { return IfcElementComponentType; }
    if(v==IfcDistributionChamberElement                 ) { return IfcDistributionFlowElement; }
    if(v==IfcDistributionChamberElementType             ) { return IfcDistributionFlowElementType; }
    if(v==IfcDistributionControlElement                 ) { return IfcDistributionElement; }
    if(v==IfcDistributionControlElementType             ) { return IfcDistributionElementType; }
    if(v==IfcDistributionElement                        ) { return IfcElement; }
    if(v==IfcDistributionElementType                    ) { return IfcElementType; }
    if(v==IfcDistributionFlowElement                    ) { return IfcDistributionElement; }
    if(v==IfcDistributionFlowElementType                ) { return IfcDistributionElementType; }
    if(v==IfcDistributionPort                           ) { return IfcPort; }
    if(v==IfcDocumentReference                          ) { return IfcExternalReference; }
    if(v==IfcDoor                                       ) { return IfcBuildingElement; }
    if(v==IfcDoorLiningProperties                       ) { return IfcPropertySetDefinition; }
    if(v==IfcDoorPanelProperties                        ) { return IfcPropertySetDefinition; }
    if(v==IfcDoorStyle                                  ) { return IfcTypeProduct; }
    if(v==IfcDraughtingCallout                          ) { return IfcGeometricRepresentationItem; }
    if(v==IfcDraughtingPreDefinedColour                 ) { return IfcPreDefinedColour; }
    if(v==IfcDraughtingPreDefinedCurveFont              ) { return IfcPreDefinedCurveFont; }
    if(v==IfcDraughtingPreDefinedTextFont               ) { return IfcPreDefinedTextFont; }
    if(v==IfcDuctFittingType                            ) { return IfcFlowFittingType; }
    if(v==IfcDuctSegmentType                            ) { return IfcFlowSegmentType; }
    if(v==IfcDuctSilencerType                           ) { return IfcFlowTreatmentDeviceType; }
    if(v==IfcEdge                                       ) { return IfcTopologicalRepresentationItem; }
    if(v==IfcEdgeCurve                                  ) { return IfcEdge; }
    if(v==IfcEdgeFeature                                ) { return IfcFeatureElementSubtraction; }
    if(v==IfcEdgeLoop                                   ) { return IfcLoop; }
    if(v==IfcElectricApplianceType                      ) { return IfcFlowTerminalType; }
    if(v==IfcElectricDistributionPoint                  ) { return IfcFlowController; }
    if(v==IfcElectricFlowStorageDeviceType              ) { return IfcFlowStorageDeviceType; }
    if(v==IfcElectricGeneratorType                      ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcElectricHeaterType                         ) { return IfcFlowTerminalType; }
    if(v==IfcElectricMotorType                          ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcElectricTimeControlType                    ) { return IfcFlowControllerType; }
    if(v==IfcElectricalBaseProperties                   ) { return IfcEnergyProperties; }
    if(v==IfcElectricalCircuit                          ) { return IfcSystem; }
    if(v==IfcElectricalElement                          ) { return IfcElement; }
    if(v==IfcElement                                    ) { return IfcProduct; }
    if(v==IfcElementAssembly                            ) { return IfcElement; }
    if(v==IfcElementComponent                           ) { return IfcElement; }
    if(v==IfcElementComponentType                       ) { return IfcElementType; }
    if(v==IfcElementQuantity                            ) { return IfcPropertySetDefinition; }
    if(v==IfcElementType                                ) { return IfcTypeProduct; }
    if(v==IfcElementarySurface                          ) { return IfcSurface; }
    if(v==IfcEllipse                                    ) { return IfcConic; }
    if(v==IfcEllipseProfileDef                          ) { return IfcParameterizedProfileDef; }
    if(v==IfcEnergyConversionDevice                     ) { return IfcDistributionFlowElement; }
    if(v==IfcEnergyConversionDeviceType                 ) { return IfcDistributionFlowElementType; }
    if(v==IfcEnergyProperties                           ) { return IfcPropertySetDefinition; }
    if(v==IfcEnvironmentalImpactValue                   ) { return IfcAppliedValue; }
    if(v==IfcEquipmentElement                           ) { return IfcElement; }
    if(v==IfcEquipmentStandard                          ) { return IfcControl; }
    if(v==IfcEvaporativeCoolerType                      ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcEvaporatorType                             ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcExtendedMaterialProperties                 ) { return IfcMaterialProperties; }
    if(v==IfcExternallyDefinedHatchStyle                ) { return IfcExternalReference; }
    if(v==IfcExternallyDefinedSurfaceStyle              ) { return IfcExternalReference; }
    if(v==IfcExternallyDefinedSymbol                    ) { return IfcExternalReference; }
    if(v==IfcExternallyDefinedTextFont                  ) { return IfcExternalReference; }
    if(v==IfcExtrudedAreaSolid                          ) { return IfcSweptAreaSolid; }
    if(v==IfcFace                                       ) { return IfcTopologicalRepresentationItem; }
    if(v==IfcFaceBasedSurfaceModel                      ) { return IfcGeometricRepresentationItem; }
    if(v==IfcFaceBound                                  ) { return IfcTopologicalRepresentationItem; }
    if(v==IfcFaceOuterBound                             ) { return IfcFaceBound; }
    if(v==IfcFaceSurface                                ) { return IfcFace; }
    if(v==IfcFacetedBrep                                ) { return IfcManifoldSolidBrep; }
    if(v==IfcFacetedBrepWithVoids                       ) { return IfcManifoldSolidBrep; }
    if(v==IfcFailureConnectionCondition                 ) { return IfcStructuralConnectionCondition; }
    if(v==IfcFanType                                    ) { return IfcFlowMovingDeviceType; }
    if(v==IfcFastener                                   ) { return IfcElementComponent; }
    if(v==IfcFastenerType                               ) { return IfcElementComponentType; }
    if(v==IfcFeatureElement                             ) { return IfcElement; }
    if(v==IfcFeatureElementAddition                     ) { return IfcFeatureElement; }
    if(v==IfcFeatureElementSubtraction                  ) { return IfcFeatureElement; }
    if(v==IfcFillAreaStyle                              ) { return IfcPresentationStyle; }
    if(v==IfcFillAreaStyleHatching                      ) { return IfcGeometricRepresentationItem; }
    if(v==IfcFillAreaStyleTileSymbolWithStyle           ) { return IfcGeometricRepresentationItem; }
    if(v==IfcFillAreaStyleTiles                         ) { return IfcGeometricRepresentationItem; }
    if(v==IfcFilterType                                 ) { return IfcFlowTreatmentDeviceType; }
    if(v==IfcFireSuppressionTerminalType                ) { return IfcFlowTerminalType; }
    if(v==IfcFlowController                             ) { return IfcDistributionFlowElement; }
    if(v==IfcFlowControllerType                         ) { return IfcDistributionFlowElementType; }
    if(v==IfcFlowFitting                                ) { return IfcDistributionFlowElement; }
    if(v==IfcFlowFittingType                            ) { return IfcDistributionFlowElementType; }
    if(v==IfcFlowInstrumentType                         ) { return IfcDistributionControlElementType; }
    if(v==IfcFlowMeterType                              ) { return IfcFlowControllerType; }
    if(v==IfcFlowMovingDevice                           ) { return IfcDistributionFlowElement; }
    if(v==IfcFlowMovingDeviceType                       ) { return IfcDistributionFlowElementType; }
    if(v==IfcFlowSegment                                ) { return IfcDistributionFlowElement; }
    if(v==IfcFlowSegmentType                            ) { return IfcDistributionFlowElementType; }
    if(v==IfcFlowStorageDevice                          ) { return IfcDistributionFlowElement; }
    if(v==IfcFlowStorageDeviceType                      ) { return IfcDistributionFlowElementType; }
    if(v==IfcFlowTerminal                               ) { return IfcDistributionFlowElement; }
    if(v==IfcFlowTerminalType                           ) { return IfcDistributionFlowElementType; }
    if(v==IfcFlowTreatmentDevice                        ) { return IfcDistributionFlowElement; }
    if(v==IfcFlowTreatmentDeviceType                    ) { return IfcDistributionFlowElementType; }
    if(v==IfcFluidFlowProperties                        ) { return IfcPropertySetDefinition; }
    if(v==IfcFooting                                    ) { return IfcBuildingElement; }
    if(v==IfcFuelProperties                             ) { return IfcMaterialProperties; }
    if(v==IfcFurnishingElement                          ) { return IfcElement; }
    if(v==IfcFurnishingElementType                      ) { return IfcElementType; }
    if(v==IfcFurnitureStandard                          ) { return IfcControl; }
    if(v==IfcFurnitureType                              ) { return IfcFurnishingElementType; }
    if(v==IfcGasTerminalType                            ) { return IfcFlowTerminalType; }
    if(v==IfcGeneralMaterialProperties                  ) { return IfcMaterialProperties; }
    if(v==IfcGeneralProfileProperties                   ) { return IfcProfileProperties; }
    if(v==IfcGeometricCurveSet                          ) { return IfcGeometricSet; }
    if(v==IfcGeometricRepresentationContext             ) { return IfcRepresentationContext; }
    if(v==IfcGeometricRepresentationItem                ) { return IfcRepresentationItem; }
    if(v==IfcGeometricRepresentationSubContext          ) { return IfcGeometricRepresentationContext; }
    if(v==IfcGeometricSet                               ) { return IfcGeometricRepresentationItem; }
    if(v==IfcGrid                                       ) { return IfcProduct; }
    if(v==IfcGridPlacement                              ) { return IfcObjectPlacement; }
    if(v==IfcGroup                                      ) { return IfcObject; }
    if(v==IfcHalfSpaceSolid                             ) { return IfcGeometricRepresentationItem; }
    if(v==IfcHeatExchangerType                          ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcHumidifierType                             ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcHygroscopicMaterialProperties              ) { return IfcMaterialProperties; }
    if(v==IfcIShapeProfileDef                           ) { return IfcParameterizedProfileDef; }
    if(v==IfcImageTexture                               ) { return IfcSurfaceTexture; }
    if(v==IfcInventory                                  ) { return IfcGroup; }
    if(v==IfcIrregularTimeSeries                        ) { return IfcTimeSeries; }
    if(v==IfcJunctionBoxType                            ) { return IfcFlowFittingType; }
    if(v==IfcLShapeProfileDef                           ) { return IfcParameterizedProfileDef; }
    if(v==IfcLaborResource                              ) { return IfcConstructionResource; }
    if(v==IfcLampType                                   ) { return IfcFlowTerminalType; }
    if(v==IfcLibraryReference                           ) { return IfcExternalReference; }
    if(v==IfcLightFixtureType                           ) { return IfcFlowTerminalType; }
    if(v==IfcLightSource                                ) { return IfcGeometricRepresentationItem; }
    if(v==IfcLightSourceAmbient                         ) { return IfcLightSource; }
    if(v==IfcLightSourceDirectional                     ) { return IfcLightSource; }
    if(v==IfcLightSourceGoniometric                     ) { return IfcLightSource; }
    if(v==IfcLightSourcePositional                      ) { return IfcLightSource; }
    if(v==IfcLightSourceSpot                            ) { return IfcLightSourcePositional; }
    if(v==IfcLine                                       ) { return IfcCurve; }
    if(v==IfcLinearDimension                            ) { return IfcDimensionCurveDirectedCallout; }
    if(v==IfcLocalPlacement                             ) { return IfcObjectPlacement; }
    if(v==IfcLoop                                       ) { return IfcTopologicalRepresentationItem; }
    if(v==IfcManifoldSolidBrep                          ) { return IfcSolidModel; }
    if(v==IfcMappedItem                                 ) { return IfcRepresentationItem; }
    if(v==IfcMaterialDefinitionRepresentation           ) { return IfcProductRepresentation; }
    if(v==IfcMechanicalConcreteMaterialProperties       ) { return IfcMechanicalMaterialProperties; }
    if(v==IfcMechanicalFastener                         ) { return IfcFastener; }
    if(v==IfcMechanicalFastenerType                     ) { return IfcFastenerType; }
    if(v==IfcMechanicalMaterialProperties               ) { return IfcMaterialProperties; }
    if(v==IfcMechanicalSteelMaterialProperties          ) { return IfcMechanicalMaterialProperties; }
    if(v==IfcMember                                     ) { return IfcBuildingElement; }
    if(v==IfcMemberType                                 ) { return IfcBuildingElementType; }
    if(v==IfcMetric                                     ) { return IfcConstraint; }
    if(v==IfcMotorConnectionType                        ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcMove                                       ) { return IfcTask; }
    if(v==IfcObject                                     ) { return IfcObjectDefinition; }
    if(v==IfcObjectDefinition                           ) { return IfcRoot; }
    if(v==IfcObjective                                  ) { return IfcConstraint; }
    if(v==IfcOccupant                                   ) { return IfcActor; }
    if(v==IfcOffsetCurve2D                              ) { return IfcCurve; }
    if(v==IfcOffsetCurve3D                              ) { return IfcCurve; }
    if(v==IfcOneDirectionRepeatFactor                   ) { return IfcGeometricRepresentationItem; }
    if(v==IfcOpenShell                                  ) { return IfcConnectedFaceSet; }
    if(v==IfcOpeningElement                             ) { return IfcFeatureElementSubtraction; }
    if(v==IfcOpticalMaterialProperties                  ) { return IfcMaterialProperties; }
    if(v==IfcOrderAction                                ) { return IfcTask; }
    if(v==IfcOrientedEdge                               ) { return IfcEdge; }
    if(v==IfcOutletType                                 ) { return IfcFlowTerminalType; }
    if(v==IfcParameterizedProfileDef                    ) { return IfcProfileDef; }
    if(v==IfcPath                                       ) { return IfcTopologicalRepresentationItem; }
    if(v==IfcPerformanceHistory                         ) { return IfcControl; }
    if(v==IfcPermeableCoveringProperties                ) { return IfcPropertySetDefinition; }
    if(v==IfcPermit                                     ) { return IfcControl; }
    if(v==IfcPhysicalComplexQuantity                    ) { return IfcPhysicalQuantity; }
    if(v==IfcPhysicalSimpleQuantity                     ) { return IfcPhysicalQuantity; }
    if(v==IfcPile                                       ) { return IfcBuildingElement; }
    if(v==IfcPipeFittingType                            ) { return IfcFlowFittingType; }
    if(v==IfcPipeSegmentType                            ) { return IfcFlowSegmentType; }
    if(v==IfcPixelTexture                               ) { return IfcSurfaceTexture; }
    if(v==IfcPlacement                                  ) { return IfcGeometricRepresentationItem; }
    if(v==IfcPlanarBox                                  ) { return IfcPlanarExtent; }
    if(v==IfcPlanarExtent                               ) { return IfcGeometricRepresentationItem; }
    if(v==IfcPlane                                      ) { return IfcElementarySurface; }
    if(v==IfcPlate                                      ) { return IfcBuildingElement; }
    if(v==IfcPlateType                                  ) { return IfcBuildingElementType; }
    if(v==IfcPoint                                      ) { return IfcGeometricRepresentationItem; }
    if(v==IfcPointOnCurve                               ) { return IfcPoint; }
    if(v==IfcPointOnSurface                             ) { return IfcPoint; }
    if(v==IfcPolyLoop                                   ) { return IfcLoop; }
    if(v==IfcPolygonalBoundedHalfSpace                  ) { return IfcHalfSpaceSolid; }
    if(v==IfcPolyline                                   ) { return IfcBoundedCurve; }
    if(v==IfcPort                                       ) { return IfcProduct; }
    if(v==IfcPostalAddress                              ) { return IfcAddress; }
    if(v==IfcPreDefinedColour                           ) { return IfcPreDefinedItem; }
    if(v==IfcPreDefinedCurveFont                        ) { return IfcPreDefinedItem; }
    if(v==IfcPreDefinedDimensionSymbol                  ) { return IfcPreDefinedSymbol; }
    if(v==IfcPreDefinedPointMarkerSymbol                ) { return IfcPreDefinedSymbol; }
    if(v==IfcPreDefinedSymbol                           ) { return IfcPreDefinedItem; }
    if(v==IfcPreDefinedTerminatorSymbol                 ) { return IfcPreDefinedSymbol; }
    if(v==IfcPreDefinedTextFont                         ) { return IfcPreDefinedItem; }
    if(v==IfcPresentationLayerWithStyle                 ) { return IfcPresentationLayerAssignment; }
    if(v==IfcProcedure                                  ) { return IfcProcess; }
    if(v==IfcProcess                                    ) { return IfcObject; }
    if(v==IfcProduct                                    ) { return IfcObject; }
    if(v==IfcProductDefinitionShape                     ) { return IfcProductRepresentation; }
    if(v==IfcProductsOfCombustionProperties             ) { return IfcMaterialProperties; }
    if(v==IfcProject                                    ) { return IfcObject; }
    if(v==IfcProjectOrder                               ) { return IfcControl; }
    if(v==IfcProjectOrderRecord                         ) { return IfcControl; }
    if(v==IfcProjectionCurve                            ) { return IfcAnnotationCurveOccurrence; }
    if(v==IfcProjectionElement                          ) { return IfcFeatureElementAddition; }
    if(v==IfcPropertyBoundedValue                       ) { return IfcSimpleProperty; }
    if(v==IfcPropertyDefinition                         ) { return IfcRoot; }
    if(v==IfcPropertyEnumeratedValue                    ) { return IfcSimpleProperty; }
    if(v==IfcPropertyListValue                          ) { return IfcSimpleProperty; }
    if(v==IfcPropertyReferenceValue                     ) { return IfcSimpleProperty; }
    if(v==IfcPropertySet                                ) { return IfcPropertySetDefinition; }
    if(v==IfcPropertySetDefinition                      ) { return IfcPropertyDefinition; }
    if(v==IfcPropertySingleValue                        ) { return IfcSimpleProperty; }
    if(v==IfcPropertyTableValue                         ) { return IfcSimpleProperty; }
    if(v==IfcProtectiveDeviceType                       ) { return IfcFlowControllerType; }
    if(v==IfcProxy                                      ) { return IfcProduct; }
    if(v==IfcPumpType                                   ) { return IfcFlowMovingDeviceType; }
    if(v==IfcQuantityArea                               ) { return IfcPhysicalSimpleQuantity; }
    if(v==IfcQuantityCount                              ) { return IfcPhysicalSimpleQuantity; }
    if(v==IfcQuantityLength                             ) { return IfcPhysicalSimpleQuantity; }
    if(v==IfcQuantityTime                               ) { return IfcPhysicalSimpleQuantity; }
    if(v==IfcQuantityVolume                             ) { return IfcPhysicalSimpleQuantity; }
    if(v==IfcQuantityWeight                             ) { return IfcPhysicalSimpleQuantity; }
    if(v==IfcRadiusDimension                            ) { return IfcDimensionCurveDirectedCallout; }
    if(v==IfcRailing                                    ) { return IfcBuildingElement; }
    if(v==IfcRailingType                                ) { return IfcBuildingElementType; }
    if(v==IfcRamp                                       ) { return IfcBuildingElement; }
    if(v==IfcRampFlight                                 ) { return IfcBuildingElement; }
    if(v==IfcRampFlightType                             ) { return IfcBuildingElementType; }
    if(v==IfcRationalBezierCurve                        ) { return IfcBezierCurve; }
    if(v==IfcRectangleHollowProfileDef                  ) { return IfcRectangleProfileDef; }
    if(v==IfcRectangleProfileDef                        ) { return IfcParameterizedProfileDef; }
    if(v==IfcRectangularPyramid                         ) { return IfcCsgPrimitive3D; }
    if(v==IfcRectangularTrimmedSurface                  ) { return IfcBoundedSurface; }
    if(v==IfcRegularTimeSeries                          ) { return IfcTimeSeries; }
    if(v==IfcReinforcementDefinitionProperties          ) { return IfcPropertySetDefinition; }
    if(v==IfcReinforcingBar                             ) { return IfcReinforcingElement; }
    if(v==IfcReinforcingElement                         ) { return IfcBuildingElementComponent; }
    if(v==IfcReinforcingMesh                            ) { return IfcReinforcingElement; }
    if(v==IfcRelAggregates                              ) { return IfcRelDecomposes; }
    if(v==IfcRelAssigns                                 ) { return IfcRelationship; }
    if(v==IfcRelAssignsTasks                            ) { return IfcRelAssignsToControl; }
    if(v==IfcRelAssignsToActor                          ) { return IfcRelAssigns; }
    if(v==IfcRelAssignsToControl                        ) { return IfcRelAssigns; }
    if(v==IfcRelAssignsToGroup                          ) { return IfcRelAssigns; }
    if(v==IfcRelAssignsToProcess                        ) { return IfcRelAssigns; }
    if(v==IfcRelAssignsToProduct                        ) { return IfcRelAssigns; }
    if(v==IfcRelAssignsToProjectOrder                   ) { return IfcRelAssignsToControl; }
    if(v==IfcRelAssignsToResource                       ) { return IfcRelAssigns; }
    if(v==IfcRelAssociates                              ) { return IfcRelationship; }
    if(v==IfcRelAssociatesAppliedValue                  ) { return IfcRelAssociates; }
    if(v==IfcRelAssociatesApproval                      ) { return IfcRelAssociates; }
    if(v==IfcRelAssociatesClassification                ) { return IfcRelAssociates; }
    if(v==IfcRelAssociatesConstraint                    ) { return IfcRelAssociates; }
    if(v==IfcRelAssociatesDocument                      ) { return IfcRelAssociates; }
    if(v==IfcRelAssociatesLibrary                       ) { return IfcRelAssociates; }
    if(v==IfcRelAssociatesMaterial                      ) { return IfcRelAssociates; }
    if(v==IfcRelAssociatesProfileProperties             ) { return IfcRelAssociates; }
    if(v==IfcRelConnects                                ) { return IfcRelationship; }
    if(v==IfcRelConnectsElements                        ) { return IfcRelConnects; }
    if(v==IfcRelConnectsPathElements                    ) { return IfcRelConnectsElements; }
    if(v==IfcRelConnectsPortToElement                   ) { return IfcRelConnects; }
    if(v==IfcRelConnectsPorts                           ) { return IfcRelConnects; }
    if(v==IfcRelConnectsStructuralActivity              ) { return IfcRelConnects; }
    if(v==IfcRelConnectsStructuralElement               ) { return IfcRelConnects; }
    if(v==IfcRelConnectsStructuralMember                ) { return IfcRelConnects; }
    if(v==IfcRelConnectsWithEccentricity                ) { return IfcRelConnectsStructuralMember; }
    if(v==IfcRelConnectsWithRealizingElements           ) { return IfcRelConnectsElements; }
    if(v==IfcRelContainedInSpatialStructure             ) { return IfcRelConnects; }
    if(v==IfcRelCoversBldgElements                      ) { return IfcRelConnects; }
    if(v==IfcRelCoversSpaces                            ) { return IfcRelConnects; }
    if(v==IfcRelDecomposes                              ) { return IfcRelationship; }
    if(v==IfcRelDefines                                 ) { return IfcRelationship; }
    if(v==IfcRelDefinesByProperties                     ) { return IfcRelDefines; }
    if(v==IfcRelDefinesByType                           ) { return IfcRelDefines; }
    if(v==IfcRelFillsElement                            ) { return IfcRelConnects; }
    if(v==IfcRelFlowControlElements                     ) { return IfcRelConnects; }
    if(v==IfcRelInteractionRequirements                 ) { return IfcRelConnects; }
    if(v==IfcRelNests                                   ) { return IfcRelDecomposes; }
    if(v==IfcRelOccupiesSpaces                          ) { return IfcRelAssignsToActor; }
    if(v==IfcRelOverridesProperties                     ) { return IfcRelDefinesByProperties; }
    if(v==IfcRelProjectsElement                         ) { return IfcRelConnects; }
    if(v==IfcRelReferencedInSpatialStructure            ) { return IfcRelConnects; }
    if(v==IfcRelSchedulesCostItems                      ) { return IfcRelAssignsToControl; }
    if(v==IfcRelSequence                                ) { return IfcRelConnects; }
    if(v==IfcRelServicesBuildings                       ) { return IfcRelConnects; }
    if(v==IfcRelSpaceBoundary                           ) { return IfcRelConnects; }
    if(v==IfcRelVoidsElement                            ) { return IfcRelConnects; }
    if(v==IfcRelationship                               ) { return IfcRoot; }
    if(v==IfcResource                                   ) { return IfcObject; }
    if(v==IfcRevolvedAreaSolid                          ) { return IfcSweptAreaSolid; }
    if(v==IfcRibPlateProfileProperties                  ) { return IfcProfileProperties; }
    if(v==IfcRightCircularCone                          ) { return IfcCsgPrimitive3D; }
    if(v==IfcRightCircularCylinder                      ) { return IfcCsgPrimitive3D; }
    if(v==IfcRoof                                       ) { return IfcBuildingElement; }
    if(v==IfcRoundedEdgeFeature                         ) { return IfcEdgeFeature; }
    if(v==IfcRoundedRectangleProfileDef                 ) { return IfcRectangleProfileDef; }
    if(v==IfcSIUnit                                     ) { return IfcNamedUnit; }
    if(v==IfcSanitaryTerminalType                       ) { return IfcFlowTerminalType; }
    if(v==IfcScheduleTimeControl                        ) { return IfcControl; }
    if(v==IfcSectionedSpine                             ) { return IfcGeometricRepresentationItem; }
    if(v==IfcSensorType                                 ) { return IfcDistributionControlElementType; }
    if(v==IfcServiceLife                                ) { return IfcControl; }
    if(v==IfcServiceLifeFactor                          ) { return IfcPropertySetDefinition; }
    if(v==IfcShapeModel                                 ) { return IfcRepresentation; }
    if(v==IfcShapeRepresentation                        ) { return IfcShapeModel; }
    if(v==IfcShellBasedSurfaceModel                     ) { return IfcGeometricRepresentationItem; }
    if(v==IfcSimpleProperty                             ) { return IfcProperty; }
    if(v==IfcSite                                       ) { return IfcSpatialStructureElement; }
    if(v==IfcSlab                                       ) { return IfcBuildingElement; }
    if(v==IfcSlabType                                   ) { return IfcBuildingElementType; }
    if(v==IfcSlippageConnectionCondition                ) { return IfcStructuralConnectionCondition; }
    if(v==IfcSolidModel                                 ) { return IfcGeometricRepresentationItem; }
    if(v==IfcSoundProperties                            ) { return IfcPropertySetDefinition; }
    if(v==IfcSoundValue                                 ) { return IfcPropertySetDefinition; }
    if(v==IfcSpace                                      ) { return IfcSpatialStructureElement; }
    if(v==IfcSpaceHeaterType                            ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcSpaceProgram                               ) { return IfcControl; }
    if(v==IfcSpaceThermalLoadProperties                 ) { return IfcPropertySetDefinition; }
    if(v==IfcSpaceType                                  ) { return IfcSpatialStructureElementType; }
    if(v==IfcSpatialStructureElement                    ) { return IfcProduct; }
    if(v==IfcSpatialStructureElementType                ) { return IfcElementType; }
    if(v==IfcSphere                                     ) { return IfcCsgPrimitive3D; }
    if(v==IfcStackTerminalType                          ) { return IfcFlowTerminalType; }
    if(v==IfcStair                                      ) { return IfcBuildingElement; }
    if(v==IfcStairFlight                                ) { return IfcBuildingElement; }
    if(v==IfcStairFlightType                            ) { return IfcBuildingElementType; }
    if(v==IfcStructuralAction                           ) { return IfcStructuralActivity; }
    if(v==IfcStructuralActivity                         ) { return IfcProduct; }
    if(v==IfcStructuralAnalysisModel                    ) { return IfcSystem; }
    if(v==IfcStructuralConnection                       ) { return IfcStructuralItem; }
    if(v==IfcStructuralCurveConnection                  ) { return IfcStructuralConnection; }
    if(v==IfcStructuralCurveMember                      ) { return IfcStructuralMember; }
    if(v==IfcStructuralCurveMemberVarying               ) { return IfcStructuralCurveMember; }
    if(v==IfcStructuralItem                             ) { return IfcProduct; }
    if(v==IfcStructuralLinearAction                     ) { return IfcStructuralAction; }
    if(v==IfcStructuralLinearActionVarying              ) { return IfcStructuralLinearAction; }
    if(v==IfcStructuralLoadGroup                        ) { return IfcGroup; }
    if(v==IfcStructuralLoadLinearForce                  ) { return IfcStructuralLoadStatic; }
    if(v==IfcStructuralLoadPlanarForce                  ) { return IfcStructuralLoadStatic; }
    if(v==IfcStructuralLoadSingleDisplacement           ) { return IfcStructuralLoadStatic; }
    if(v==IfcStructuralLoadSingleDisplacementDistortion ) { return IfcStructuralLoadSingleDisplacement; }
    if(v==IfcStructuralLoadSingleForce                  ) { return IfcStructuralLoadStatic; }
    if(v==IfcStructuralLoadSingleForceWarping           ) { return IfcStructuralLoadSingleForce; }
    if(v==IfcStructuralLoadStatic                       ) { return IfcStructuralLoad; }
    if(v==IfcStructuralLoadTemperature                  ) { return IfcStructuralLoadStatic; }
    if(v==IfcStructuralMember                           ) { return IfcStructuralItem; }
    if(v==IfcStructuralPlanarAction                     ) { return IfcStructuralAction; }
    if(v==IfcStructuralPlanarActionVarying              ) { return IfcStructuralPlanarAction; }
    if(v==IfcStructuralPointAction                      ) { return IfcStructuralAction; }
    if(v==IfcStructuralPointConnection                  ) { return IfcStructuralConnection; }
    if(v==IfcStructuralPointReaction                    ) { return IfcStructuralReaction; }
    if(v==IfcStructuralProfileProperties                ) { return IfcGeneralProfileProperties; }
    if(v==IfcStructuralReaction                         ) { return IfcStructuralActivity; }
    if(v==IfcStructuralResultGroup                      ) { return IfcGroup; }
    if(v==IfcStructuralSteelProfileProperties           ) { return IfcStructuralProfileProperties; }
    if(v==IfcStructuralSurfaceConnection                ) { return IfcStructuralConnection; }
    if(v==IfcStructuralSurfaceMember                    ) { return IfcStructuralMember; }
    if(v==IfcStructuralSurfaceMemberVarying             ) { return IfcStructuralSurfaceMember; }
    if(v==IfcStructuredDimensionCallout                 ) { return IfcDraughtingCallout; }
    if(v==IfcStyleModel                                 ) { return IfcRepresentation; }
    if(v==IfcStyledItem                                 ) { return IfcRepresentationItem; }
    if(v==IfcStyledRepresentation                       ) { return IfcStyleModel; }
    if(v==IfcSubContractResource                        ) { return IfcConstructionResource; }
    if(v==IfcSubedge                                    ) { return IfcEdge; }
    if(v==IfcSurface                                    ) { return IfcGeometricRepresentationItem; }
    if(v==IfcSurfaceCurveSweptAreaSolid                 ) { return IfcSweptAreaSolid; }
    if(v==IfcSurfaceOfLinearExtrusion                   ) { return IfcSweptSurface; }
    if(v==IfcSurfaceOfRevolution                        ) { return IfcSweptSurface; }
    if(v==IfcSurfaceStyle                               ) { return IfcPresentationStyle; }
    if(v==IfcSurfaceStyleRendering                      ) { return IfcSurfaceStyleShading; }
    if(v==IfcSweptAreaSolid                             ) { return IfcSolidModel; }
    if(v==IfcSweptDiskSolid                             ) { return IfcSolidModel; }
    if(v==IfcSweptSurface                               ) { return IfcSurface; }
    if(v==IfcSwitchingDeviceType                        ) { return IfcFlowControllerType; }
    if(v==IfcSymbolStyle                                ) { return IfcPresentationStyle; }
    if(v==IfcSystem                                     ) { return IfcGroup; }
    if(v==IfcSystemFurnitureElementType                 ) { return IfcFurnishingElementType; }
    if(v==IfcTShapeProfileDef                           ) { return IfcParameterizedProfileDef; }
    if(v==IfcTankType                                   ) { return IfcFlowStorageDeviceType; }
    if(v==IfcTask                                       ) { return IfcProcess; }
    if(v==IfcTelecomAddress                             ) { return IfcAddress; }
    if(v==IfcTendon                                     ) { return IfcReinforcingElement; }
    if(v==IfcTendonAnchor                               ) { return IfcReinforcingElement; }
    if(v==IfcTerminatorSymbol                           ) { return IfcAnnotationSymbolOccurrence; }
    if(v==IfcTextLiteral                                ) { return IfcGeometricRepresentationItem; }
    if(v==IfcTextLiteralWithExtent                      ) { return IfcTextLiteral; }
    if(v==IfcTextStyle                                  ) { return IfcPresentationStyle; }
    if(v==IfcTextStyleFontModel                         ) { return IfcPreDefinedTextFont; }
    if(v==IfcTextureCoordinateGenerator                 ) { return IfcTextureCoordinate; }
    if(v==IfcTextureMap                                 ) { return IfcTextureCoordinate; }
    if(v==IfcThermalMaterialProperties                  ) { return IfcMaterialProperties; }
    if(v==IfcTimeSeriesSchedule                         ) { return IfcControl; }
    if(v==IfcTopologicalRepresentationItem              ) { return IfcRepresentationItem; }
    if(v==IfcTopologyRepresentation                     ) { return IfcShapeModel; }
    if(v==IfcTransformerType                            ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcTransportElement                           ) { return IfcElement; }
    if(v==IfcTransportElementType                       ) { return IfcElementType; }
    if(v==IfcTrapeziumProfileDef                        ) { return IfcParameterizedProfileDef; }
    if(v==IfcTrimmedCurve                               ) { return IfcBoundedCurve; }
    if(v==IfcTubeBundleType                             ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcTwoDirectionRepeatFactor                   ) { return IfcOneDirectionRepeatFactor; }
    if(v==IfcTypeObject                                 ) { return IfcObjectDefinition; }
    if(v==IfcTypeProduct                                ) { return IfcTypeObject; }
    if(v==IfcUShapeProfileDef                           ) { return IfcParameterizedProfileDef; }
    if(v==IfcUnitaryEquipmentType                       ) { return IfcEnergyConversionDeviceType; }
    if(v==IfcValveType                                  ) { return IfcFlowControllerType; }
    if(v==IfcVector                                     ) { return IfcGeometricRepresentationItem; }
    if(v==IfcVertex                                     ) { return IfcTopologicalRepresentationItem; }
    if(v==IfcVertexLoop                                 ) { return IfcLoop; }
    if(v==IfcVertexPoint                                ) { return IfcVertex; }
    if(v==IfcVibrationIsolatorType                      ) { return IfcDiscreteAccessoryType; }
    if(v==IfcVirtualElement                             ) { return IfcElement; }
    if(v==IfcWall                                       ) { return IfcBuildingElement; }
    if(v==IfcWallStandardCase                           ) { return IfcWall; }
    if(v==IfcWallType                                   ) { return IfcBuildingElementType; }
    if(v==IfcWasteTerminalType                          ) { return IfcFlowTerminalType; }
    if(v==IfcWaterProperties                            ) { return IfcMaterialProperties; }
    if(v==IfcWindow                                     ) { return IfcBuildingElement; }
    if(v==IfcWindowLiningProperties                     ) { return IfcPropertySetDefinition; }
    if(v==IfcWindowPanelProperties                      ) { return IfcPropertySetDefinition; }
    if(v==IfcWindowStyle                                ) { return IfcTypeProduct; }
    if(v==IfcWorkControl                                ) { return IfcControl; }
    if(v==IfcWorkPlan                                   ) { return IfcWorkControl; }
    if(v==IfcWorkSchedule                               ) { return IfcWorkControl; }
    if(v==IfcZShapeProfileDef                           ) { return IfcParameterizedProfileDef; }
    if(v==IfcZone                                       ) { return IfcGroup; }
    return (Enum)-1;
}
std::string IfcActionSourceTypeEnum::ToString(IfcActionSourceTypeEnum v) {
    if ( v < 0 || v >= 27 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DEAD_LOAD_G","COMPLETION_G1","LIVE_LOAD_Q","SNOW_S","WIND_W","PRESTRESSING_P","SETTLEMENT_U","TEMPERATURE_T","EARTHQUAKE_E","FIRE","IMPULSE","IMPACT","TRANSPORT","ERECTION","PROPPING","SYSTEM_IMPERFECTION","SHRINKAGE","CREEP","LACK_OF_FIT","BUOYANCY","ICE","CURRENT","WAVE","RAIN","BRAKES","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcActionSourceTypeEnum::IfcActionSourceTypeEnum IfcActionSourceTypeEnum::FromString(const std::string& s) {
    if(s=="DEAD_LOAD_G") return IfcActionSourceTypeEnum::IfcActionSourceType_DEAD_LOAD_G;
    if(s=="COMPLETION_G1") return IfcActionSourceTypeEnum::IfcActionSourceType_COMPLETION_G1;
    if(s=="LIVE_LOAD_Q") return IfcActionSourceTypeEnum::IfcActionSourceType_LIVE_LOAD_Q;
    if(s=="SNOW_S") return IfcActionSourceTypeEnum::IfcActionSourceType_SNOW_S;
    if(s=="WIND_W") return IfcActionSourceTypeEnum::IfcActionSourceType_WIND_W;
    if(s=="PRESTRESSING_P") return IfcActionSourceTypeEnum::IfcActionSourceType_PRESTRESSING_P;
    if(s=="SETTLEMENT_U") return IfcActionSourceTypeEnum::IfcActionSourceType_SETTLEMENT_U;
    if(s=="TEMPERATURE_T") return IfcActionSourceTypeEnum::IfcActionSourceType_TEMPERATURE_T;
    if(s=="EARTHQUAKE_E") return IfcActionSourceTypeEnum::IfcActionSourceType_EARTHQUAKE_E;
    if(s=="FIRE") return IfcActionSourceTypeEnum::IfcActionSourceType_FIRE;
    if(s=="IMPULSE") return IfcActionSourceTypeEnum::IfcActionSourceType_IMPULSE;
    if(s=="IMPACT") return IfcActionSourceTypeEnum::IfcActionSourceType_IMPACT;
    if(s=="TRANSPORT") return IfcActionSourceTypeEnum::IfcActionSourceType_TRANSPORT;
    if(s=="ERECTION") return IfcActionSourceTypeEnum::IfcActionSourceType_ERECTION;
    if(s=="PROPPING") return IfcActionSourceTypeEnum::IfcActionSourceType_PROPPING;
    if(s=="SYSTEM_IMPERFECTION") return IfcActionSourceTypeEnum::IfcActionSourceType_SYSTEM_IMPERFECTION;
    if(s=="SHRINKAGE") return IfcActionSourceTypeEnum::IfcActionSourceType_SHRINKAGE;
    if(s=="CREEP") return IfcActionSourceTypeEnum::IfcActionSourceType_CREEP;
    if(s=="LACK_OF_FIT") return IfcActionSourceTypeEnum::IfcActionSourceType_LACK_OF_FIT;
    if(s=="BUOYANCY") return IfcActionSourceTypeEnum::IfcActionSourceType_BUOYANCY;
    if(s=="ICE") return IfcActionSourceTypeEnum::IfcActionSourceType_ICE;
    if(s=="CURRENT") return IfcActionSourceTypeEnum::IfcActionSourceType_CURRENT;
    if(s=="WAVE") return IfcActionSourceTypeEnum::IfcActionSourceType_WAVE;
    if(s=="RAIN") return IfcActionSourceTypeEnum::IfcActionSourceType_RAIN;
    if(s=="BRAKES") return IfcActionSourceTypeEnum::IfcActionSourceType_BRAKES;
    if(s=="USERDEFINED") return IfcActionSourceTypeEnum::IfcActionSourceType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcActionSourceTypeEnum::IfcActionSourceType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcActionTypeEnum::ToString(IfcActionTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PERMANENT_G","VARIABLE_Q","EXTRAORDINARY_A","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcActionTypeEnum::IfcActionTypeEnum IfcActionTypeEnum::FromString(const std::string& s) {
    if(s=="PERMANENT_G") return IfcActionTypeEnum::IfcActionType_PERMANENT_G;
    if(s=="VARIABLE_Q") return IfcActionTypeEnum::IfcActionType_VARIABLE_Q;
    if(s=="EXTRAORDINARY_A") return IfcActionTypeEnum::IfcActionType_EXTRAORDINARY_A;
    if(s=="USERDEFINED") return IfcActionTypeEnum::IfcActionType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcActionTypeEnum::IfcActionType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcActuatorTypeEnum::ToString(IfcActuatorTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ELECTRICACTUATOR","HANDOPERATEDACTUATOR","HYDRAULICACTUATOR","PNEUMATICACTUATOR","THERMOSTATICACTUATOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcActuatorTypeEnum::IfcActuatorTypeEnum IfcActuatorTypeEnum::FromString(const std::string& s) {
    if(s=="ELECTRICACTUATOR") return IfcActuatorTypeEnum::IfcActuatorType_ELECTRICACTUATOR;
    if(s=="HANDOPERATEDACTUATOR") return IfcActuatorTypeEnum::IfcActuatorType_HANDOPERATEDACTUATOR;
    if(s=="HYDRAULICACTUATOR") return IfcActuatorTypeEnum::IfcActuatorType_HYDRAULICACTUATOR;
    if(s=="PNEUMATICACTUATOR") return IfcActuatorTypeEnum::IfcActuatorType_PNEUMATICACTUATOR;
    if(s=="THERMOSTATICACTUATOR") return IfcActuatorTypeEnum::IfcActuatorType_THERMOSTATICACTUATOR;
    if(s=="USERDEFINED") return IfcActuatorTypeEnum::IfcActuatorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcActuatorTypeEnum::IfcActuatorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAddressTypeEnum::ToString(IfcAddressTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "OFFICE","SITE","HOME","DISTRIBUTIONPOINT","USERDEFINED" };
    return names[v];
}
IfcAddressTypeEnum::IfcAddressTypeEnum IfcAddressTypeEnum::FromString(const std::string& s) {
    if(s=="OFFICE") return IfcAddressTypeEnum::IfcAddressType_OFFICE;
    if(s=="SITE") return IfcAddressTypeEnum::IfcAddressType_SITE;
    if(s=="HOME") return IfcAddressTypeEnum::IfcAddressType_HOME;
    if(s=="DISTRIBUTIONPOINT") return IfcAddressTypeEnum::IfcAddressType_DISTRIBUTIONPOINT;
    if(s=="USERDEFINED") return IfcAddressTypeEnum::IfcAddressType_USERDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAheadOrBehind::ToString(IfcAheadOrBehind v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AHEAD","BEHIND" };
    return names[v];
}
IfcAheadOrBehind::IfcAheadOrBehind IfcAheadOrBehind::FromString(const std::string& s) {
    if(s=="AHEAD") return IfcAheadOrBehind::IfcAheadOrBehind_AHEAD;
    if(s=="BEHIND") return IfcAheadOrBehind::IfcAheadOrBehind_BEHIND;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAirTerminalBoxTypeEnum::ToString(IfcAirTerminalBoxTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CONSTANTFLOW","VARIABLEFLOWPRESSUREDEPENDANT","VARIABLEFLOWPRESSUREINDEPENDANT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxTypeEnum IfcAirTerminalBoxTypeEnum::FromString(const std::string& s) {
    if(s=="CONSTANTFLOW") return IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxType_CONSTANTFLOW;
    if(s=="VARIABLEFLOWPRESSUREDEPENDANT") return IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxType_VARIABLEFLOWPRESSUREDEPENDANT;
    if(s=="VARIABLEFLOWPRESSUREINDEPENDANT") return IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxType_VARIABLEFLOWPRESSUREINDEPENDANT;
    if(s=="USERDEFINED") return IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAirTerminalTypeEnum::ToString(IfcAirTerminalTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "GRILLE","REGISTER","DIFFUSER","EYEBALL","IRIS","LINEARGRILLE","LINEARDIFFUSER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAirTerminalTypeEnum::IfcAirTerminalTypeEnum IfcAirTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="GRILLE") return IfcAirTerminalTypeEnum::IfcAirTerminalType_GRILLE;
    if(s=="REGISTER") return IfcAirTerminalTypeEnum::IfcAirTerminalType_REGISTER;
    if(s=="DIFFUSER") return IfcAirTerminalTypeEnum::IfcAirTerminalType_DIFFUSER;
    if(s=="EYEBALL") return IfcAirTerminalTypeEnum::IfcAirTerminalType_EYEBALL;
    if(s=="IRIS") return IfcAirTerminalTypeEnum::IfcAirTerminalType_IRIS;
    if(s=="LINEARGRILLE") return IfcAirTerminalTypeEnum::IfcAirTerminalType_LINEARGRILLE;
    if(s=="LINEARDIFFUSER") return IfcAirTerminalTypeEnum::IfcAirTerminalType_LINEARDIFFUSER;
    if(s=="USERDEFINED") return IfcAirTerminalTypeEnum::IfcAirTerminalType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcAirTerminalTypeEnum::IfcAirTerminalType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAirToAirHeatRecoveryTypeEnum::ToString(IfcAirToAirHeatRecoveryTypeEnum v) {
    if ( v < 0 || v >= 11 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FIXEDPLATECOUNTERFLOWEXCHANGER","FIXEDPLATECROSSFLOWEXCHANGER","FIXEDPLATEPARALLELFLOWEXCHANGER","ROTARYWHEEL","RUNAROUNDCOILLOOP","HEATPIPE","TWINTOWERENTHALPYRECOVERYLOOPS","THERMOSIPHONSEALEDTUBEHEATEXCHANGERS","THERMOSIPHONCOILTYPEHEATEXCHANGERS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryTypeEnum IfcAirToAirHeatRecoveryTypeEnum::FromString(const std::string& s) {
    if(s=="FIXEDPLATECOUNTERFLOWEXCHANGER") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_FIXEDPLATECOUNTERFLOWEXCHANGER;
    if(s=="FIXEDPLATECROSSFLOWEXCHANGER") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_FIXEDPLATECROSSFLOWEXCHANGER;
    if(s=="FIXEDPLATEPARALLELFLOWEXCHANGER") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_FIXEDPLATEPARALLELFLOWEXCHANGER;
    if(s=="ROTARYWHEEL") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_ROTARYWHEEL;
    if(s=="RUNAROUNDCOILLOOP") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_RUNAROUNDCOILLOOP;
    if(s=="HEATPIPE") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_HEATPIPE;
    if(s=="TWINTOWERENTHALPYRECOVERYLOOPS") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_TWINTOWERENTHALPYRECOVERYLOOPS;
    if(s=="THERMOSIPHONSEALEDTUBEHEATEXCHANGERS") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_THERMOSIPHONSEALEDTUBEHEATEXCHANGERS;
    if(s=="THERMOSIPHONCOILTYPEHEATEXCHANGERS") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_THERMOSIPHONCOILTYPEHEATEXCHANGERS;
    if(s=="USERDEFINED") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAlarmTypeEnum::ToString(IfcAlarmTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BELL","BREAKGLASSBUTTON","LIGHT","MANUALPULLBOX","SIREN","WHISTLE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAlarmTypeEnum::IfcAlarmTypeEnum IfcAlarmTypeEnum::FromString(const std::string& s) {
    if(s=="BELL") return IfcAlarmTypeEnum::IfcAlarmType_BELL;
    if(s=="BREAKGLASSBUTTON") return IfcAlarmTypeEnum::IfcAlarmType_BREAKGLASSBUTTON;
    if(s=="LIGHT") return IfcAlarmTypeEnum::IfcAlarmType_LIGHT;
    if(s=="MANUALPULLBOX") return IfcAlarmTypeEnum::IfcAlarmType_MANUALPULLBOX;
    if(s=="SIREN") return IfcAlarmTypeEnum::IfcAlarmType_SIREN;
    if(s=="WHISTLE") return IfcAlarmTypeEnum::IfcAlarmType_WHISTLE;
    if(s=="USERDEFINED") return IfcAlarmTypeEnum::IfcAlarmType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcAlarmTypeEnum::IfcAlarmType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAnalysisModelTypeEnum::ToString(IfcAnalysisModelTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "IN_PLANE_LOADING_2D","OUT_PLANE_LOADING_2D","LOADING_3D","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAnalysisModelTypeEnum::IfcAnalysisModelTypeEnum IfcAnalysisModelTypeEnum::FromString(const std::string& s) {
    if(s=="IN_PLANE_LOADING_2D") return IfcAnalysisModelTypeEnum::IfcAnalysisModelType_IN_PLANE_LOADING_2D;
    if(s=="OUT_PLANE_LOADING_2D") return IfcAnalysisModelTypeEnum::IfcAnalysisModelType_OUT_PLANE_LOADING_2D;
    if(s=="LOADING_3D") return IfcAnalysisModelTypeEnum::IfcAnalysisModelType_LOADING_3D;
    if(s=="USERDEFINED") return IfcAnalysisModelTypeEnum::IfcAnalysisModelType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcAnalysisModelTypeEnum::IfcAnalysisModelType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAnalysisTheoryTypeEnum::ToString(IfcAnalysisTheoryTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FIRST_ORDER_THEORY","SECOND_ORDER_THEORY","THIRD_ORDER_THEORY","FULL_NONLINEAR_THEORY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryTypeEnum IfcAnalysisTheoryTypeEnum::FromString(const std::string& s) {
    if(s=="FIRST_ORDER_THEORY") return IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryType_FIRST_ORDER_THEORY;
    if(s=="SECOND_ORDER_THEORY") return IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryType_SECOND_ORDER_THEORY;
    if(s=="THIRD_ORDER_THEORY") return IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryType_THIRD_ORDER_THEORY;
    if(s=="FULL_NONLINEAR_THEORY") return IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryType_FULL_NONLINEAR_THEORY;
    if(s=="USERDEFINED") return IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcArithmeticOperatorEnum::ToString(IfcArithmeticOperatorEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ADD","DIVIDE","MULTIPLY","SUBTRACT" };
    return names[v];
}
IfcArithmeticOperatorEnum::IfcArithmeticOperatorEnum IfcArithmeticOperatorEnum::FromString(const std::string& s) {
    if(s=="ADD") return IfcArithmeticOperatorEnum::IfcArithmeticOperator_ADD;
    if(s=="DIVIDE") return IfcArithmeticOperatorEnum::IfcArithmeticOperator_DIVIDE;
    if(s=="MULTIPLY") return IfcArithmeticOperatorEnum::IfcArithmeticOperator_MULTIPLY;
    if(s=="SUBTRACT") return IfcArithmeticOperatorEnum::IfcArithmeticOperator_SUBTRACT;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcAssemblyPlaceEnum::ToString(IfcAssemblyPlaceEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SITE","FACTORY","NOTDEFINED" };
    return names[v];
}
IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum IfcAssemblyPlaceEnum::FromString(const std::string& s) {
    if(s=="SITE") return IfcAssemblyPlaceEnum::IfcAssemblyPlace_SITE;
    if(s=="FACTORY") return IfcAssemblyPlaceEnum::IfcAssemblyPlace_FACTORY;
    if(s=="NOTDEFINED") return IfcAssemblyPlaceEnum::IfcAssemblyPlace_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcBSplineCurveForm::ToString(IfcBSplineCurveForm v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "POLYLINE_FORM","CIRCULAR_ARC","ELLIPTIC_ARC","PARABOLIC_ARC","HYPERBOLIC_ARC","UNSPECIFIED" };
    return names[v];
}
IfcBSplineCurveForm::IfcBSplineCurveForm IfcBSplineCurveForm::FromString(const std::string& s) {
    if(s=="POLYLINE_FORM") return IfcBSplineCurveForm::IfcBSplineCurveForm_POLYLINE_FORM;
    if(s=="CIRCULAR_ARC") return IfcBSplineCurveForm::IfcBSplineCurveForm_CIRCULAR_ARC;
    if(s=="ELLIPTIC_ARC") return IfcBSplineCurveForm::IfcBSplineCurveForm_ELLIPTIC_ARC;
    if(s=="PARABOLIC_ARC") return IfcBSplineCurveForm::IfcBSplineCurveForm_PARABOLIC_ARC;
    if(s=="HYPERBOLIC_ARC") return IfcBSplineCurveForm::IfcBSplineCurveForm_HYPERBOLIC_ARC;
    if(s=="UNSPECIFIED") return IfcBSplineCurveForm::IfcBSplineCurveForm_UNSPECIFIED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcBeamTypeEnum::ToString(IfcBeamTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BEAM","JOIST","LINTEL","T_BEAM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcBeamTypeEnum::IfcBeamTypeEnum IfcBeamTypeEnum::FromString(const std::string& s) {
    if(s=="BEAM") return IfcBeamTypeEnum::IfcBeamType_BEAM;
    if(s=="JOIST") return IfcBeamTypeEnum::IfcBeamType_JOIST;
    if(s=="LINTEL") return IfcBeamTypeEnum::IfcBeamType_LINTEL;
    if(s=="T_BEAM") return IfcBeamTypeEnum::IfcBeamType_T_BEAM;
    if(s=="USERDEFINED") return IfcBeamTypeEnum::IfcBeamType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcBeamTypeEnum::IfcBeamType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcBenchmarkEnum::ToString(IfcBenchmarkEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "GREATERTHAN","GREATERTHANOREQUALTO","LESSTHAN","LESSTHANOREQUALTO","EQUALTO","NOTEQUALTO" };
    return names[v];
}
IfcBenchmarkEnum::IfcBenchmarkEnum IfcBenchmarkEnum::FromString(const std::string& s) {
    if(s=="GREATERTHAN") return IfcBenchmarkEnum::IfcBenchmark_GREATERTHAN;
    if(s=="GREATERTHANOREQUALTO") return IfcBenchmarkEnum::IfcBenchmark_GREATERTHANOREQUALTO;
    if(s=="LESSTHAN") return IfcBenchmarkEnum::IfcBenchmark_LESSTHAN;
    if(s=="LESSTHANOREQUALTO") return IfcBenchmarkEnum::IfcBenchmark_LESSTHANOREQUALTO;
    if(s=="EQUALTO") return IfcBenchmarkEnum::IfcBenchmark_EQUALTO;
    if(s=="NOTEQUALTO") return IfcBenchmarkEnum::IfcBenchmark_NOTEQUALTO;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcBoilerTypeEnum::ToString(IfcBoilerTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "WATER","STEAM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcBoilerTypeEnum::IfcBoilerTypeEnum IfcBoilerTypeEnum::FromString(const std::string& s) {
    if(s=="WATER") return IfcBoilerTypeEnum::IfcBoilerType_WATER;
    if(s=="STEAM") return IfcBoilerTypeEnum::IfcBoilerType_STEAM;
    if(s=="USERDEFINED") return IfcBoilerTypeEnum::IfcBoilerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcBoilerTypeEnum::IfcBoilerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcBooleanOperator::ToString(IfcBooleanOperator v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "UNION","INTERSECTION","DIFFERENCE" };
    return names[v];
}
IfcBooleanOperator::IfcBooleanOperator IfcBooleanOperator::FromString(const std::string& s) {
    if(s=="UNION") return IfcBooleanOperator::IfcBooleanOperator_UNION;
    if(s=="INTERSECTION") return IfcBooleanOperator::IfcBooleanOperator_INTERSECTION;
    if(s=="DIFFERENCE") return IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcBuildingElementProxyTypeEnum::ToString(IfcBuildingElementProxyTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyTypeEnum IfcBuildingElementProxyTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCableCarrierFittingTypeEnum::ToString(IfcCableCarrierFittingTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BEND","CROSS","REDUCER","TEE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingTypeEnum IfcCableCarrierFittingTypeEnum::FromString(const std::string& s) {
    if(s=="BEND") return IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingType_BEND;
    if(s=="CROSS") return IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingType_CROSS;
    if(s=="REDUCER") return IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingType_REDUCER;
    if(s=="TEE") return IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingType_TEE;
    if(s=="USERDEFINED") return IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCableCarrierSegmentTypeEnum::ToString(IfcCableCarrierSegmentTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CABLELADDERSEGMENT","CABLETRAYSEGMENT","CABLETRUNKINGSEGMENT","CONDUITSEGMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentTypeEnum IfcCableCarrierSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="CABLELADDERSEGMENT") return IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentType_CABLELADDERSEGMENT;
    if(s=="CABLETRAYSEGMENT") return IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentType_CABLETRAYSEGMENT;
    if(s=="CABLETRUNKINGSEGMENT") return IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentType_CABLETRUNKINGSEGMENT;
    if(s=="CONDUITSEGMENT") return IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentType_CONDUITSEGMENT;
    if(s=="USERDEFINED") return IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCableSegmentTypeEnum::ToString(IfcCableSegmentTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CABLESEGMENT","CONDUCTORSEGMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCableSegmentTypeEnum::IfcCableSegmentTypeEnum IfcCableSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="CABLESEGMENT") return IfcCableSegmentTypeEnum::IfcCableSegmentType_CABLESEGMENT;
    if(s=="CONDUCTORSEGMENT") return IfcCableSegmentTypeEnum::IfcCableSegmentType_CONDUCTORSEGMENT;
    if(s=="USERDEFINED") return IfcCableSegmentTypeEnum::IfcCableSegmentType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCableSegmentTypeEnum::IfcCableSegmentType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcChangeActionEnum::ToString(IfcChangeActionEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "NOCHANGE","MODIFIED","ADDED","DELETED","MODIFIEDADDED","MODIFIEDDELETED" };
    return names[v];
}
IfcChangeActionEnum::IfcChangeActionEnum IfcChangeActionEnum::FromString(const std::string& s) {
    if(s=="NOCHANGE") return IfcChangeActionEnum::IfcChangeAction_NOCHANGE;
    if(s=="MODIFIED") return IfcChangeActionEnum::IfcChangeAction_MODIFIED;
    if(s=="ADDED") return IfcChangeActionEnum::IfcChangeAction_ADDED;
    if(s=="DELETED") return IfcChangeActionEnum::IfcChangeAction_DELETED;
    if(s=="MODIFIEDADDED") return IfcChangeActionEnum::IfcChangeAction_MODIFIEDADDED;
    if(s=="MODIFIEDDELETED") return IfcChangeActionEnum::IfcChangeAction_MODIFIEDDELETED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcChillerTypeEnum::ToString(IfcChillerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AIRCOOLED","WATERCOOLED","HEATRECOVERY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcChillerTypeEnum::IfcChillerTypeEnum IfcChillerTypeEnum::FromString(const std::string& s) {
    if(s=="AIRCOOLED") return IfcChillerTypeEnum::IfcChillerType_AIRCOOLED;
    if(s=="WATERCOOLED") return IfcChillerTypeEnum::IfcChillerType_WATERCOOLED;
    if(s=="HEATRECOVERY") return IfcChillerTypeEnum::IfcChillerType_HEATRECOVERY;
    if(s=="USERDEFINED") return IfcChillerTypeEnum::IfcChillerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcChillerTypeEnum::IfcChillerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCoilTypeEnum::ToString(IfcCoilTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DXCOOLINGCOIL","WATERCOOLINGCOIL","STEAMHEATINGCOIL","WATERHEATINGCOIL","ELECTRICHEATINGCOIL","GASHEATINGCOIL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCoilTypeEnum::IfcCoilTypeEnum IfcCoilTypeEnum::FromString(const std::string& s) {
    if(s=="DXCOOLINGCOIL") return IfcCoilTypeEnum::IfcCoilType_DXCOOLINGCOIL;
    if(s=="WATERCOOLINGCOIL") return IfcCoilTypeEnum::IfcCoilType_WATERCOOLINGCOIL;
    if(s=="STEAMHEATINGCOIL") return IfcCoilTypeEnum::IfcCoilType_STEAMHEATINGCOIL;
    if(s=="WATERHEATINGCOIL") return IfcCoilTypeEnum::IfcCoilType_WATERHEATINGCOIL;
    if(s=="ELECTRICHEATINGCOIL") return IfcCoilTypeEnum::IfcCoilType_ELECTRICHEATINGCOIL;
    if(s=="GASHEATINGCOIL") return IfcCoilTypeEnum::IfcCoilType_GASHEATINGCOIL;
    if(s=="USERDEFINED") return IfcCoilTypeEnum::IfcCoilType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCoilTypeEnum::IfcCoilType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcColumnTypeEnum::ToString(IfcColumnTypeEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COLUMN","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcColumnTypeEnum::IfcColumnTypeEnum IfcColumnTypeEnum::FromString(const std::string& s) {
    if(s=="COLUMN") return IfcColumnTypeEnum::IfcColumnType_COLUMN;
    if(s=="USERDEFINED") return IfcColumnTypeEnum::IfcColumnType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcColumnTypeEnum::IfcColumnType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCompressorTypeEnum::ToString(IfcCompressorTypeEnum v) {
    if ( v < 0 || v >= 17 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DYNAMIC","RECIPROCATING","ROTARY","SCROLL","TROCHOIDAL","SINGLESTAGE","BOOSTER","OPENTYPE","HERMETIC","SEMIHERMETIC","WELDEDSHELLHERMETIC","ROLLINGPISTON","ROTARYVANE","SINGLESCREW","TWINSCREW","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCompressorTypeEnum::IfcCompressorTypeEnum IfcCompressorTypeEnum::FromString(const std::string& s) {
    if(s=="DYNAMIC") return IfcCompressorTypeEnum::IfcCompressorType_DYNAMIC;
    if(s=="RECIPROCATING") return IfcCompressorTypeEnum::IfcCompressorType_RECIPROCATING;
    if(s=="ROTARY") return IfcCompressorTypeEnum::IfcCompressorType_ROTARY;
    if(s=="SCROLL") return IfcCompressorTypeEnum::IfcCompressorType_SCROLL;
    if(s=="TROCHOIDAL") return IfcCompressorTypeEnum::IfcCompressorType_TROCHOIDAL;
    if(s=="SINGLESTAGE") return IfcCompressorTypeEnum::IfcCompressorType_SINGLESTAGE;
    if(s=="BOOSTER") return IfcCompressorTypeEnum::IfcCompressorType_BOOSTER;
    if(s=="OPENTYPE") return IfcCompressorTypeEnum::IfcCompressorType_OPENTYPE;
    if(s=="HERMETIC") return IfcCompressorTypeEnum::IfcCompressorType_HERMETIC;
    if(s=="SEMIHERMETIC") return IfcCompressorTypeEnum::IfcCompressorType_SEMIHERMETIC;
    if(s=="WELDEDSHELLHERMETIC") return IfcCompressorTypeEnum::IfcCompressorType_WELDEDSHELLHERMETIC;
    if(s=="ROLLINGPISTON") return IfcCompressorTypeEnum::IfcCompressorType_ROLLINGPISTON;
    if(s=="ROTARYVANE") return IfcCompressorTypeEnum::IfcCompressorType_ROTARYVANE;
    if(s=="SINGLESCREW") return IfcCompressorTypeEnum::IfcCompressorType_SINGLESCREW;
    if(s=="TWINSCREW") return IfcCompressorTypeEnum::IfcCompressorType_TWINSCREW;
    if(s=="USERDEFINED") return IfcCompressorTypeEnum::IfcCompressorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCompressorTypeEnum::IfcCompressorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCondenserTypeEnum::ToString(IfcCondenserTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "WATERCOOLEDSHELLTUBE","WATERCOOLEDSHELLCOIL","WATERCOOLEDTUBEINTUBE","WATERCOOLEDBRAZEDPLATE","AIRCOOLED","EVAPORATIVECOOLED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCondenserTypeEnum::IfcCondenserTypeEnum IfcCondenserTypeEnum::FromString(const std::string& s) {
    if(s=="WATERCOOLEDSHELLTUBE") return IfcCondenserTypeEnum::IfcCondenserType_WATERCOOLEDSHELLTUBE;
    if(s=="WATERCOOLEDSHELLCOIL") return IfcCondenserTypeEnum::IfcCondenserType_WATERCOOLEDSHELLCOIL;
    if(s=="WATERCOOLEDTUBEINTUBE") return IfcCondenserTypeEnum::IfcCondenserType_WATERCOOLEDTUBEINTUBE;
    if(s=="WATERCOOLEDBRAZEDPLATE") return IfcCondenserTypeEnum::IfcCondenserType_WATERCOOLEDBRAZEDPLATE;
    if(s=="AIRCOOLED") return IfcCondenserTypeEnum::IfcCondenserType_AIRCOOLED;
    if(s=="EVAPORATIVECOOLED") return IfcCondenserTypeEnum::IfcCondenserType_EVAPORATIVECOOLED;
    if(s=="USERDEFINED") return IfcCondenserTypeEnum::IfcCondenserType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCondenserTypeEnum::IfcCondenserType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcConnectionTypeEnum::ToString(IfcConnectionTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ATPATH","ATSTART","ATEND","NOTDEFINED" };
    return names[v];
}
IfcConnectionTypeEnum::IfcConnectionTypeEnum IfcConnectionTypeEnum::FromString(const std::string& s) {
    if(s=="ATPATH") return IfcConnectionTypeEnum::IfcConnectionType_ATPATH;
    if(s=="ATSTART") return IfcConnectionTypeEnum::IfcConnectionType_ATSTART;
    if(s=="ATEND") return IfcConnectionTypeEnum::IfcConnectionType_ATEND;
    if(s=="NOTDEFINED") return IfcConnectionTypeEnum::IfcConnectionType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcConstraintEnum::ToString(IfcConstraintEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "HARD","SOFT","ADVISORY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcConstraintEnum::IfcConstraintEnum IfcConstraintEnum::FromString(const std::string& s) {
    if(s=="HARD") return IfcConstraintEnum::IfcConstraint_HARD;
    if(s=="SOFT") return IfcConstraintEnum::IfcConstraint_SOFT;
    if(s=="ADVISORY") return IfcConstraintEnum::IfcConstraint_ADVISORY;
    if(s=="USERDEFINED") return IfcConstraintEnum::IfcConstraint_USERDEFINED;
    if(s=="NOTDEFINED") return IfcConstraintEnum::IfcConstraint_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcControllerTypeEnum::ToString(IfcControllerTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FLOATING","PROPORTIONAL","PROPORTIONALINTEGRAL","PROPORTIONALINTEGRALDERIVATIVE","TIMEDTWOPOSITION","TWOPOSITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcControllerTypeEnum::IfcControllerTypeEnum IfcControllerTypeEnum::FromString(const std::string& s) {
    if(s=="FLOATING") return IfcControllerTypeEnum::IfcControllerType_FLOATING;
    if(s=="PROPORTIONAL") return IfcControllerTypeEnum::IfcControllerType_PROPORTIONAL;
    if(s=="PROPORTIONALINTEGRAL") return IfcControllerTypeEnum::IfcControllerType_PROPORTIONALINTEGRAL;
    if(s=="PROPORTIONALINTEGRALDERIVATIVE") return IfcControllerTypeEnum::IfcControllerType_PROPORTIONALINTEGRALDERIVATIVE;
    if(s=="TIMEDTWOPOSITION") return IfcControllerTypeEnum::IfcControllerType_TIMEDTWOPOSITION;
    if(s=="TWOPOSITION") return IfcControllerTypeEnum::IfcControllerType_TWOPOSITION;
    if(s=="USERDEFINED") return IfcControllerTypeEnum::IfcControllerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcControllerTypeEnum::IfcControllerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCooledBeamTypeEnum::ToString(IfcCooledBeamTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ACTIVE","PASSIVE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCooledBeamTypeEnum::IfcCooledBeamTypeEnum IfcCooledBeamTypeEnum::FromString(const std::string& s) {
    if(s=="ACTIVE") return IfcCooledBeamTypeEnum::IfcCooledBeamType_ACTIVE;
    if(s=="PASSIVE") return IfcCooledBeamTypeEnum::IfcCooledBeamType_PASSIVE;
    if(s=="USERDEFINED") return IfcCooledBeamTypeEnum::IfcCooledBeamType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCooledBeamTypeEnum::IfcCooledBeamType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCoolingTowerTypeEnum::ToString(IfcCoolingTowerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "NATURALDRAFT","MECHANICALINDUCEDDRAFT","MECHANICALFORCEDDRAFT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCoolingTowerTypeEnum::IfcCoolingTowerTypeEnum IfcCoolingTowerTypeEnum::FromString(const std::string& s) {
    if(s=="NATURALDRAFT") return IfcCoolingTowerTypeEnum::IfcCoolingTowerType_NATURALDRAFT;
    if(s=="MECHANICALINDUCEDDRAFT") return IfcCoolingTowerTypeEnum::IfcCoolingTowerType_MECHANICALINDUCEDDRAFT;
    if(s=="MECHANICALFORCEDDRAFT") return IfcCoolingTowerTypeEnum::IfcCoolingTowerType_MECHANICALFORCEDDRAFT;
    if(s=="USERDEFINED") return IfcCoolingTowerTypeEnum::IfcCoolingTowerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCoolingTowerTypeEnum::IfcCoolingTowerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCostScheduleTypeEnum::ToString(IfcCostScheduleTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BUDGET","COSTPLAN","ESTIMATE","TENDER","PRICEDBILLOFQUANTITIES","UNPRICEDBILLOFQUANTITIES","SCHEDULEOFRATES","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCostScheduleTypeEnum::IfcCostScheduleTypeEnum IfcCostScheduleTypeEnum::FromString(const std::string& s) {
    if(s=="BUDGET") return IfcCostScheduleTypeEnum::IfcCostScheduleType_BUDGET;
    if(s=="COSTPLAN") return IfcCostScheduleTypeEnum::IfcCostScheduleType_COSTPLAN;
    if(s=="ESTIMATE") return IfcCostScheduleTypeEnum::IfcCostScheduleType_ESTIMATE;
    if(s=="TENDER") return IfcCostScheduleTypeEnum::IfcCostScheduleType_TENDER;
    if(s=="PRICEDBILLOFQUANTITIES") return IfcCostScheduleTypeEnum::IfcCostScheduleType_PRICEDBILLOFQUANTITIES;
    if(s=="UNPRICEDBILLOFQUANTITIES") return IfcCostScheduleTypeEnum::IfcCostScheduleType_UNPRICEDBILLOFQUANTITIES;
    if(s=="SCHEDULEOFRATES") return IfcCostScheduleTypeEnum::IfcCostScheduleType_SCHEDULEOFRATES;
    if(s=="USERDEFINED") return IfcCostScheduleTypeEnum::IfcCostScheduleType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCostScheduleTypeEnum::IfcCostScheduleType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCoveringTypeEnum::ToString(IfcCoveringTypeEnum v) {
    if ( v < 0 || v >= 10 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CEILING","FLOORING","CLADDING","ROOFING","INSULATION","MEMBRANE","SLEEVING","WRAPPING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCoveringTypeEnum::IfcCoveringTypeEnum IfcCoveringTypeEnum::FromString(const std::string& s) {
    if(s=="CEILING") return IfcCoveringTypeEnum::IfcCoveringType_CEILING;
    if(s=="FLOORING") return IfcCoveringTypeEnum::IfcCoveringType_FLOORING;
    if(s=="CLADDING") return IfcCoveringTypeEnum::IfcCoveringType_CLADDING;
    if(s=="ROOFING") return IfcCoveringTypeEnum::IfcCoveringType_ROOFING;
    if(s=="INSULATION") return IfcCoveringTypeEnum::IfcCoveringType_INSULATION;
    if(s=="MEMBRANE") return IfcCoveringTypeEnum::IfcCoveringType_MEMBRANE;
    if(s=="SLEEVING") return IfcCoveringTypeEnum::IfcCoveringType_SLEEVING;
    if(s=="WRAPPING") return IfcCoveringTypeEnum::IfcCoveringType_WRAPPING;
    if(s=="USERDEFINED") return IfcCoveringTypeEnum::IfcCoveringType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCoveringTypeEnum::IfcCoveringType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCurrencyEnum::ToString(IfcCurrencyEnum v) {
    if ( v < 0 || v >= 83 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AED","AES","ATS","AUD","BBD","BEG","BGL","BHD","BMD","BND","BRL","BSD","BWP","BZD","CAD","CBD","CHF","CLP","CNY","CYS","CZK","DDP","DEM","DKK","EGL","EST","EUR","FAK","FIM","FJD","FKP","FRF","GBP","GIP","GMD","GRX","HKD","HUF","ICK","IDR","ILS","INR","IRP","ITL","JMD","JOD","JPY","KES","KRW","KWD","KYD","LKR","LUF","MTL","MUR","MXN","MYR","NLG","NZD","OMR","PGK","PHP","PKR","PLN","PTN","QAR","RUR","SAR","SCR","SEK","SGD","SKP","THB","TRL","TTD","TWD","USD","VEB","VND","XEU","ZAR","ZWD","NOK" };
    return names[v];
}
IfcCurrencyEnum::IfcCurrencyEnum IfcCurrencyEnum::FromString(const std::string& s) {
    if(s=="AED") return IfcCurrencyEnum::IfcCurrency_AED;
    if(s=="AES") return IfcCurrencyEnum::IfcCurrency_AES;
    if(s=="ATS") return IfcCurrencyEnum::IfcCurrency_ATS;
    if(s=="AUD") return IfcCurrencyEnum::IfcCurrency_AUD;
    if(s=="BBD") return IfcCurrencyEnum::IfcCurrency_BBD;
    if(s=="BEG") return IfcCurrencyEnum::IfcCurrency_BEG;
    if(s=="BGL") return IfcCurrencyEnum::IfcCurrency_BGL;
    if(s=="BHD") return IfcCurrencyEnum::IfcCurrency_BHD;
    if(s=="BMD") return IfcCurrencyEnum::IfcCurrency_BMD;
    if(s=="BND") return IfcCurrencyEnum::IfcCurrency_BND;
    if(s=="BRL") return IfcCurrencyEnum::IfcCurrency_BRL;
    if(s=="BSD") return IfcCurrencyEnum::IfcCurrency_BSD;
    if(s=="BWP") return IfcCurrencyEnum::IfcCurrency_BWP;
    if(s=="BZD") return IfcCurrencyEnum::IfcCurrency_BZD;
    if(s=="CAD") return IfcCurrencyEnum::IfcCurrency_CAD;
    if(s=="CBD") return IfcCurrencyEnum::IfcCurrency_CBD;
    if(s=="CHF") return IfcCurrencyEnum::IfcCurrency_CHF;
    if(s=="CLP") return IfcCurrencyEnum::IfcCurrency_CLP;
    if(s=="CNY") return IfcCurrencyEnum::IfcCurrency_CNY;
    if(s=="CYS") return IfcCurrencyEnum::IfcCurrency_CYS;
    if(s=="CZK") return IfcCurrencyEnum::IfcCurrency_CZK;
    if(s=="DDP") return IfcCurrencyEnum::IfcCurrency_DDP;
    if(s=="DEM") return IfcCurrencyEnum::IfcCurrency_DEM;
    if(s=="DKK") return IfcCurrencyEnum::IfcCurrency_DKK;
    if(s=="EGL") return IfcCurrencyEnum::IfcCurrency_EGL;
    if(s=="EST") return IfcCurrencyEnum::IfcCurrency_EST;
    if(s=="EUR") return IfcCurrencyEnum::IfcCurrency_EUR;
    if(s=="FAK") return IfcCurrencyEnum::IfcCurrency_FAK;
    if(s=="FIM") return IfcCurrencyEnum::IfcCurrency_FIM;
    if(s=="FJD") return IfcCurrencyEnum::IfcCurrency_FJD;
    if(s=="FKP") return IfcCurrencyEnum::IfcCurrency_FKP;
    if(s=="FRF") return IfcCurrencyEnum::IfcCurrency_FRF;
    if(s=="GBP") return IfcCurrencyEnum::IfcCurrency_GBP;
    if(s=="GIP") return IfcCurrencyEnum::IfcCurrency_GIP;
    if(s=="GMD") return IfcCurrencyEnum::IfcCurrency_GMD;
    if(s=="GRX") return IfcCurrencyEnum::IfcCurrency_GRX;
    if(s=="HKD") return IfcCurrencyEnum::IfcCurrency_HKD;
    if(s=="HUF") return IfcCurrencyEnum::IfcCurrency_HUF;
    if(s=="ICK") return IfcCurrencyEnum::IfcCurrency_ICK;
    if(s=="IDR") return IfcCurrencyEnum::IfcCurrency_IDR;
    if(s=="ILS") return IfcCurrencyEnum::IfcCurrency_ILS;
    if(s=="INR") return IfcCurrencyEnum::IfcCurrency_INR;
    if(s=="IRP") return IfcCurrencyEnum::IfcCurrency_IRP;
    if(s=="ITL") return IfcCurrencyEnum::IfcCurrency_ITL;
    if(s=="JMD") return IfcCurrencyEnum::IfcCurrency_JMD;
    if(s=="JOD") return IfcCurrencyEnum::IfcCurrency_JOD;
    if(s=="JPY") return IfcCurrencyEnum::IfcCurrency_JPY;
    if(s=="KES") return IfcCurrencyEnum::IfcCurrency_KES;
    if(s=="KRW") return IfcCurrencyEnum::IfcCurrency_KRW;
    if(s=="KWD") return IfcCurrencyEnum::IfcCurrency_KWD;
    if(s=="KYD") return IfcCurrencyEnum::IfcCurrency_KYD;
    if(s=="LKR") return IfcCurrencyEnum::IfcCurrency_LKR;
    if(s=="LUF") return IfcCurrencyEnum::IfcCurrency_LUF;
    if(s=="MTL") return IfcCurrencyEnum::IfcCurrency_MTL;
    if(s=="MUR") return IfcCurrencyEnum::IfcCurrency_MUR;
    if(s=="MXN") return IfcCurrencyEnum::IfcCurrency_MXN;
    if(s=="MYR") return IfcCurrencyEnum::IfcCurrency_MYR;
    if(s=="NLG") return IfcCurrencyEnum::IfcCurrency_NLG;
    if(s=="NZD") return IfcCurrencyEnum::IfcCurrency_NZD;
    if(s=="OMR") return IfcCurrencyEnum::IfcCurrency_OMR;
    if(s=="PGK") return IfcCurrencyEnum::IfcCurrency_PGK;
    if(s=="PHP") return IfcCurrencyEnum::IfcCurrency_PHP;
    if(s=="PKR") return IfcCurrencyEnum::IfcCurrency_PKR;
    if(s=="PLN") return IfcCurrencyEnum::IfcCurrency_PLN;
    if(s=="PTN") return IfcCurrencyEnum::IfcCurrency_PTN;
    if(s=="QAR") return IfcCurrencyEnum::IfcCurrency_QAR;
    if(s=="RUR") return IfcCurrencyEnum::IfcCurrency_RUR;
    if(s=="SAR") return IfcCurrencyEnum::IfcCurrency_SAR;
    if(s=="SCR") return IfcCurrencyEnum::IfcCurrency_SCR;
    if(s=="SEK") return IfcCurrencyEnum::IfcCurrency_SEK;
    if(s=="SGD") return IfcCurrencyEnum::IfcCurrency_SGD;
    if(s=="SKP") return IfcCurrencyEnum::IfcCurrency_SKP;
    if(s=="THB") return IfcCurrencyEnum::IfcCurrency_THB;
    if(s=="TRL") return IfcCurrencyEnum::IfcCurrency_TRL;
    if(s=="TTD") return IfcCurrencyEnum::IfcCurrency_TTD;
    if(s=="TWD") return IfcCurrencyEnum::IfcCurrency_TWD;
    if(s=="USD") return IfcCurrencyEnum::IfcCurrency_USD;
    if(s=="VEB") return IfcCurrencyEnum::IfcCurrency_VEB;
    if(s=="VND") return IfcCurrencyEnum::IfcCurrency_VND;
    if(s=="XEU") return IfcCurrencyEnum::IfcCurrency_XEU;
    if(s=="ZAR") return IfcCurrencyEnum::IfcCurrency_ZAR;
    if(s=="ZWD") return IfcCurrencyEnum::IfcCurrency_ZWD;
    if(s=="NOK") return IfcCurrencyEnum::IfcCurrency_NOK;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcCurtainWallTypeEnum::ToString(IfcCurtainWallTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCurtainWallTypeEnum::IfcCurtainWallTypeEnum IfcCurtainWallTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcCurtainWallTypeEnum::IfcCurtainWallType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcCurtainWallTypeEnum::IfcCurtainWallType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDamperTypeEnum::ToString(IfcDamperTypeEnum v) {
    if ( v < 0 || v >= 13 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CONTROLDAMPER","FIREDAMPER","SMOKEDAMPER","FIRESMOKEDAMPER","BACKDRAFTDAMPER","RELIEFDAMPER","BLASTDAMPER","GRAVITYDAMPER","GRAVITYRELIEFDAMPER","BALANCINGDAMPER","FUMEHOODEXHAUST","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDamperTypeEnum::IfcDamperTypeEnum IfcDamperTypeEnum::FromString(const std::string& s) {
    if(s=="CONTROLDAMPER") return IfcDamperTypeEnum::IfcDamperType_CONTROLDAMPER;
    if(s=="FIREDAMPER") return IfcDamperTypeEnum::IfcDamperType_FIREDAMPER;
    if(s=="SMOKEDAMPER") return IfcDamperTypeEnum::IfcDamperType_SMOKEDAMPER;
    if(s=="FIRESMOKEDAMPER") return IfcDamperTypeEnum::IfcDamperType_FIRESMOKEDAMPER;
    if(s=="BACKDRAFTDAMPER") return IfcDamperTypeEnum::IfcDamperType_BACKDRAFTDAMPER;
    if(s=="RELIEFDAMPER") return IfcDamperTypeEnum::IfcDamperType_RELIEFDAMPER;
    if(s=="BLASTDAMPER") return IfcDamperTypeEnum::IfcDamperType_BLASTDAMPER;
    if(s=="GRAVITYDAMPER") return IfcDamperTypeEnum::IfcDamperType_GRAVITYDAMPER;
    if(s=="GRAVITYRELIEFDAMPER") return IfcDamperTypeEnum::IfcDamperType_GRAVITYRELIEFDAMPER;
    if(s=="BALANCINGDAMPER") return IfcDamperTypeEnum::IfcDamperType_BALANCINGDAMPER;
    if(s=="FUMEHOODEXHAUST") return IfcDamperTypeEnum::IfcDamperType_FUMEHOODEXHAUST;
    if(s=="USERDEFINED") return IfcDamperTypeEnum::IfcDamperType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDamperTypeEnum::IfcDamperType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDataOriginEnum::ToString(IfcDataOriginEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "MEASURED","PREDICTED","SIMULATED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDataOriginEnum::IfcDataOriginEnum IfcDataOriginEnum::FromString(const std::string& s) {
    if(s=="MEASURED") return IfcDataOriginEnum::IfcDataOrigin_MEASURED;
    if(s=="PREDICTED") return IfcDataOriginEnum::IfcDataOrigin_PREDICTED;
    if(s=="SIMULATED") return IfcDataOriginEnum::IfcDataOrigin_SIMULATED;
    if(s=="USERDEFINED") return IfcDataOriginEnum::IfcDataOrigin_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDataOriginEnum::IfcDataOrigin_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDerivedUnitEnum::ToString(IfcDerivedUnitEnum v) {
    if ( v < 0 || v >= 49 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ANGULARVELOCITYUNIT","COMPOUNDPLANEANGLEUNIT","DYNAMICVISCOSITYUNIT","HEATFLUXDENSITYUNIT","INTEGERCOUNTRATEUNIT","ISOTHERMALMOISTURECAPACITYUNIT","KINEMATICVISCOSITYUNIT","LINEARVELOCITYUNIT","MASSDENSITYUNIT","MASSFLOWRATEUNIT","MOISTUREDIFFUSIVITYUNIT","MOLECULARWEIGHTUNIT","SPECIFICHEATCAPACITYUNIT","THERMALADMITTANCEUNIT","THERMALCONDUCTANCEUNIT","THERMALRESISTANCEUNIT","THERMALTRANSMITTANCEUNIT","VAPORPERMEABILITYUNIT","VOLUMETRICFLOWRATEUNIT","ROTATIONALFREQUENCYUNIT","TORQUEUNIT","MOMENTOFINERTIAUNIT","LINEARMOMENTUNIT","LINEARFORCEUNIT","PLANARFORCEUNIT","MODULUSOFELASTICITYUNIT","SHEARMODULUSUNIT","LINEARSTIFFNESSUNIT","ROTATIONALSTIFFNESSUNIT","MODULUSOFSUBGRADEREACTIONUNIT","ACCELERATIONUNIT","CURVATUREUNIT","HEATINGVALUEUNIT","IONCONCENTRATIONUNIT","LUMINOUSINTENSITYDISTRIBUTIONUNIT","MASSPERLENGTHUNIT","MODULUSOFLINEARSUBGRADEREACTIONUNIT","MODULUSOFROTATIONALSUBGRADEREACTIONUNIT","PHUNIT","ROTATIONALMASSUNIT","SECTIONAREAINTEGRALUNIT","SECTIONMODULUSUNIT","SOUNDPOWERUNIT","SOUNDPRESSUREUNIT","TEMPERATUREGRADIENTUNIT","THERMALEXPANSIONCOEFFICIENTUNIT","WARPINGCONSTANTUNIT","WARPINGMOMENTUNIT","USERDEFINED" };
    return names[v];
}
IfcDerivedUnitEnum::IfcDerivedUnitEnum IfcDerivedUnitEnum::FromString(const std::string& s) {
    if(s=="ANGULARVELOCITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_ANGULARVELOCITYUNIT;
    if(s=="COMPOUNDPLANEANGLEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_COMPOUNDPLANEANGLEUNIT;
    if(s=="DYNAMICVISCOSITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_DYNAMICVISCOSITYUNIT;
    if(s=="HEATFLUXDENSITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_HEATFLUXDENSITYUNIT;
    if(s=="INTEGERCOUNTRATEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_INTEGERCOUNTRATEUNIT;
    if(s=="ISOTHERMALMOISTURECAPACITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_ISOTHERMALMOISTURECAPACITYUNIT;
    if(s=="KINEMATICVISCOSITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_KINEMATICVISCOSITYUNIT;
    if(s=="LINEARVELOCITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_LINEARVELOCITYUNIT;
    if(s=="MASSDENSITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MASSDENSITYUNIT;
    if(s=="MASSFLOWRATEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MASSFLOWRATEUNIT;
    if(s=="MOISTUREDIFFUSIVITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MOISTUREDIFFUSIVITYUNIT;
    if(s=="MOLECULARWEIGHTUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MOLECULARWEIGHTUNIT;
    if(s=="SPECIFICHEATCAPACITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_SPECIFICHEATCAPACITYUNIT;
    if(s=="THERMALADMITTANCEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_THERMALADMITTANCEUNIT;
    if(s=="THERMALCONDUCTANCEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_THERMALCONDUCTANCEUNIT;
    if(s=="THERMALRESISTANCEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_THERMALRESISTANCEUNIT;
    if(s=="THERMALTRANSMITTANCEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_THERMALTRANSMITTANCEUNIT;
    if(s=="VAPORPERMEABILITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_VAPORPERMEABILITYUNIT;
    if(s=="VOLUMETRICFLOWRATEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_VOLUMETRICFLOWRATEUNIT;
    if(s=="ROTATIONALFREQUENCYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_ROTATIONALFREQUENCYUNIT;
    if(s=="TORQUEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_TORQUEUNIT;
    if(s=="MOMENTOFINERTIAUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MOMENTOFINERTIAUNIT;
    if(s=="LINEARMOMENTUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_LINEARMOMENTUNIT;
    if(s=="LINEARFORCEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_LINEARFORCEUNIT;
    if(s=="PLANARFORCEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_PLANARFORCEUNIT;
    if(s=="MODULUSOFELASTICITYUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MODULUSOFELASTICITYUNIT;
    if(s=="SHEARMODULUSUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_SHEARMODULUSUNIT;
    if(s=="LINEARSTIFFNESSUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_LINEARSTIFFNESSUNIT;
    if(s=="ROTATIONALSTIFFNESSUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_ROTATIONALSTIFFNESSUNIT;
    if(s=="MODULUSOFSUBGRADEREACTIONUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MODULUSOFSUBGRADEREACTIONUNIT;
    if(s=="ACCELERATIONUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_ACCELERATIONUNIT;
    if(s=="CURVATUREUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_CURVATUREUNIT;
    if(s=="HEATINGVALUEUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_HEATINGVALUEUNIT;
    if(s=="IONCONCENTRATIONUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_IONCONCENTRATIONUNIT;
    if(s=="LUMINOUSINTENSITYDISTRIBUTIONUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_LUMINOUSINTENSITYDISTRIBUTIONUNIT;
    if(s=="MASSPERLENGTHUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MASSPERLENGTHUNIT;
    if(s=="MODULUSOFLINEARSUBGRADEREACTIONUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MODULUSOFLINEARSUBGRADEREACTIONUNIT;
    if(s=="MODULUSOFROTATIONALSUBGRADEREACTIONUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_MODULUSOFROTATIONALSUBGRADEREACTIONUNIT;
    if(s=="PHUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_PHUNIT;
    if(s=="ROTATIONALMASSUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_ROTATIONALMASSUNIT;
    if(s=="SECTIONAREAINTEGRALUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_SECTIONAREAINTEGRALUNIT;
    if(s=="SECTIONMODULUSUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_SECTIONMODULUSUNIT;
    if(s=="SOUNDPOWERUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_SOUNDPOWERUNIT;
    if(s=="SOUNDPRESSUREUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_SOUNDPRESSUREUNIT;
    if(s=="TEMPERATUREGRADIENTUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_TEMPERATUREGRADIENTUNIT;
    if(s=="THERMALEXPANSIONCOEFFICIENTUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_THERMALEXPANSIONCOEFFICIENTUNIT;
    if(s=="WARPINGCONSTANTUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_WARPINGCONSTANTUNIT;
    if(s=="WARPINGMOMENTUNIT") return IfcDerivedUnitEnum::IfcDerivedUnit_WARPINGMOMENTUNIT;
    if(s=="USERDEFINED") return IfcDerivedUnitEnum::IfcDerivedUnit_USERDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDimensionExtentUsage::ToString(IfcDimensionExtentUsage v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ORIGIN","TARGET" };
    return names[v];
}
IfcDimensionExtentUsage::IfcDimensionExtentUsage IfcDimensionExtentUsage::FromString(const std::string& s) {
    if(s=="ORIGIN") return IfcDimensionExtentUsage::IfcDimensionExtentUsage_ORIGIN;
    if(s=="TARGET") return IfcDimensionExtentUsage::IfcDimensionExtentUsage_TARGET;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDirectionSenseEnum::ToString(IfcDirectionSenseEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "POSITIVE","NEGATIVE" };
    return names[v];
}
IfcDirectionSenseEnum::IfcDirectionSenseEnum IfcDirectionSenseEnum::FromString(const std::string& s) {
    if(s=="POSITIVE") return IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE;
    if(s=="NEGATIVE") return IfcDirectionSenseEnum::IfcDirectionSense_NEGATIVE;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDistributionChamberElementTypeEnum::ToString(IfcDistributionChamberElementTypeEnum v) {
    if ( v < 0 || v >= 10 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FORMEDDUCT","INSPECTIONCHAMBER","INSPECTIONPIT","MANHOLE","METERCHAMBER","SUMP","TRENCH","VALVECHAMBER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementTypeEnum IfcDistributionChamberElementTypeEnum::FromString(const std::string& s) {
    if(s=="FORMEDDUCT") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_FORMEDDUCT;
    if(s=="INSPECTIONCHAMBER") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_INSPECTIONCHAMBER;
    if(s=="INSPECTIONPIT") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_INSPECTIONPIT;
    if(s=="MANHOLE") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_MANHOLE;
    if(s=="METERCHAMBER") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_METERCHAMBER;
    if(s=="SUMP") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_SUMP;
    if(s=="TRENCH") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_TRENCH;
    if(s=="VALVECHAMBER") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_VALVECHAMBER;
    if(s=="USERDEFINED") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDocumentConfidentialityEnum::ToString(IfcDocumentConfidentialityEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PUBLIC","RESTRICTED","CONFIDENTIAL","PERSONAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDocumentConfidentialityEnum::IfcDocumentConfidentialityEnum IfcDocumentConfidentialityEnum::FromString(const std::string& s) {
    if(s=="PUBLIC") return IfcDocumentConfidentialityEnum::IfcDocumentConfidentiality_PUBLIC;
    if(s=="RESTRICTED") return IfcDocumentConfidentialityEnum::IfcDocumentConfidentiality_RESTRICTED;
    if(s=="CONFIDENTIAL") return IfcDocumentConfidentialityEnum::IfcDocumentConfidentiality_CONFIDENTIAL;
    if(s=="PERSONAL") return IfcDocumentConfidentialityEnum::IfcDocumentConfidentiality_PERSONAL;
    if(s=="USERDEFINED") return IfcDocumentConfidentialityEnum::IfcDocumentConfidentiality_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDocumentConfidentialityEnum::IfcDocumentConfidentiality_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDocumentStatusEnum::ToString(IfcDocumentStatusEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DRAFT","FINALDRAFT","FINAL","REVISION","NOTDEFINED" };
    return names[v];
}
IfcDocumentStatusEnum::IfcDocumentStatusEnum IfcDocumentStatusEnum::FromString(const std::string& s) {
    if(s=="DRAFT") return IfcDocumentStatusEnum::IfcDocumentStatus_DRAFT;
    if(s=="FINALDRAFT") return IfcDocumentStatusEnum::IfcDocumentStatus_FINALDRAFT;
    if(s=="FINAL") return IfcDocumentStatusEnum::IfcDocumentStatus_FINAL;
    if(s=="REVISION") return IfcDocumentStatusEnum::IfcDocumentStatus_REVISION;
    if(s=="NOTDEFINED") return IfcDocumentStatusEnum::IfcDocumentStatus_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDoorPanelOperationEnum::ToString(IfcDoorPanelOperationEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SWINGING","DOUBLE_ACTING","SLIDING","FOLDING","REVOLVING","ROLLINGUP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDoorPanelOperationEnum::IfcDoorPanelOperationEnum IfcDoorPanelOperationEnum::FromString(const std::string& s) {
    if(s=="SWINGING") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_SWINGING;
    if(s=="DOUBLE_ACTING") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_DOUBLE_ACTING;
    if(s=="SLIDING") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_SLIDING;
    if(s=="FOLDING") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_FOLDING;
    if(s=="REVOLVING") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_REVOLVING;
    if(s=="ROLLINGUP") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_ROLLINGUP;
    if(s=="USERDEFINED") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDoorPanelOperationEnum::IfcDoorPanelOperation_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDoorPanelPositionEnum::ToString(IfcDoorPanelPositionEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "LEFT","MIDDLE","RIGHT","NOTDEFINED" };
    return names[v];
}
IfcDoorPanelPositionEnum::IfcDoorPanelPositionEnum IfcDoorPanelPositionEnum::FromString(const std::string& s) {
    if(s=="LEFT") return IfcDoorPanelPositionEnum::IfcDoorPanelPosition_LEFT;
    if(s=="MIDDLE") return IfcDoorPanelPositionEnum::IfcDoorPanelPosition_MIDDLE;
    if(s=="RIGHT") return IfcDoorPanelPositionEnum::IfcDoorPanelPosition_RIGHT;
    if(s=="NOTDEFINED") return IfcDoorPanelPositionEnum::IfcDoorPanelPosition_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDoorStyleConstructionEnum::ToString(IfcDoorStyleConstructionEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ALUMINIUM","HIGH_GRADE_STEEL","STEEL","WOOD","ALUMINIUM_WOOD","ALUMINIUM_PLASTIC","PLASTIC","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDoorStyleConstructionEnum::IfcDoorStyleConstructionEnum IfcDoorStyleConstructionEnum::FromString(const std::string& s) {
    if(s=="ALUMINIUM") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_ALUMINIUM;
    if(s=="HIGH_GRADE_STEEL") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_HIGH_GRADE_STEEL;
    if(s=="STEEL") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_STEEL;
    if(s=="WOOD") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_WOOD;
    if(s=="ALUMINIUM_WOOD") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_ALUMINIUM_WOOD;
    if(s=="ALUMINIUM_PLASTIC") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_ALUMINIUM_PLASTIC;
    if(s=="PLASTIC") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_PLASTIC;
    if(s=="USERDEFINED") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDoorStyleOperationEnum::ToString(IfcDoorStyleOperationEnum v) {
    if ( v < 0 || v >= 18 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SINGLE_SWING_LEFT","SINGLE_SWING_RIGHT","DOUBLE_DOOR_SINGLE_SWING","DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT","DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT","DOUBLE_SWING_LEFT","DOUBLE_SWING_RIGHT","DOUBLE_DOOR_DOUBLE_SWING","SLIDING_TO_LEFT","SLIDING_TO_RIGHT","DOUBLE_DOOR_SLIDING","FOLDING_TO_LEFT","FOLDING_TO_RIGHT","DOUBLE_DOOR_FOLDING","REVOLVING","ROLLINGUP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDoorStyleOperationEnum::IfcDoorStyleOperationEnum IfcDoorStyleOperationEnum::FromString(const std::string& s) {
    if(s=="SINGLE_SWING_LEFT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_SINGLE_SWING_LEFT;
    if(s=="SINGLE_SWING_RIGHT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_SINGLE_SWING_RIGHT;
    if(s=="DOUBLE_DOOR_SINGLE_SWING") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_DOOR_SINGLE_SWING;
    if(s=="DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT;
    if(s=="DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT;
    if(s=="DOUBLE_SWING_LEFT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_SWING_LEFT;
    if(s=="DOUBLE_SWING_RIGHT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_SWING_RIGHT;
    if(s=="DOUBLE_DOOR_DOUBLE_SWING") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_DOOR_DOUBLE_SWING;
    if(s=="SLIDING_TO_LEFT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_SLIDING_TO_LEFT;
    if(s=="SLIDING_TO_RIGHT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_SLIDING_TO_RIGHT;
    if(s=="DOUBLE_DOOR_SLIDING") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_DOOR_SLIDING;
    if(s=="FOLDING_TO_LEFT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_FOLDING_TO_LEFT;
    if(s=="FOLDING_TO_RIGHT") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_FOLDING_TO_RIGHT;
    if(s=="DOUBLE_DOOR_FOLDING") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_DOUBLE_DOOR_FOLDING;
    if(s=="REVOLVING") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_REVOLVING;
    if(s=="ROLLINGUP") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_ROLLINGUP;
    if(s=="USERDEFINED") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDoorStyleOperationEnum::IfcDoorStyleOperation_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDuctFittingTypeEnum::ToString(IfcDuctFittingTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BEND","CONNECTOR","ENTRY","EXIT","JUNCTION","OBSTRUCTION","TRANSITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDuctFittingTypeEnum::IfcDuctFittingTypeEnum IfcDuctFittingTypeEnum::FromString(const std::string& s) {
    if(s=="BEND") return IfcDuctFittingTypeEnum::IfcDuctFittingType_BEND;
    if(s=="CONNECTOR") return IfcDuctFittingTypeEnum::IfcDuctFittingType_CONNECTOR;
    if(s=="ENTRY") return IfcDuctFittingTypeEnum::IfcDuctFittingType_ENTRY;
    if(s=="EXIT") return IfcDuctFittingTypeEnum::IfcDuctFittingType_EXIT;
    if(s=="JUNCTION") return IfcDuctFittingTypeEnum::IfcDuctFittingType_JUNCTION;
    if(s=="OBSTRUCTION") return IfcDuctFittingTypeEnum::IfcDuctFittingType_OBSTRUCTION;
    if(s=="TRANSITION") return IfcDuctFittingTypeEnum::IfcDuctFittingType_TRANSITION;
    if(s=="USERDEFINED") return IfcDuctFittingTypeEnum::IfcDuctFittingType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDuctFittingTypeEnum::IfcDuctFittingType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDuctSegmentTypeEnum::ToString(IfcDuctSegmentTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "RIGIDSEGMENT","FLEXIBLESEGMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDuctSegmentTypeEnum::IfcDuctSegmentTypeEnum IfcDuctSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="RIGIDSEGMENT") return IfcDuctSegmentTypeEnum::IfcDuctSegmentType_RIGIDSEGMENT;
    if(s=="FLEXIBLESEGMENT") return IfcDuctSegmentTypeEnum::IfcDuctSegmentType_FLEXIBLESEGMENT;
    if(s=="USERDEFINED") return IfcDuctSegmentTypeEnum::IfcDuctSegmentType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDuctSegmentTypeEnum::IfcDuctSegmentType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcDuctSilencerTypeEnum::ToString(IfcDuctSilencerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FLATOVAL","RECTANGULAR","ROUND","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDuctSilencerTypeEnum::IfcDuctSilencerTypeEnum IfcDuctSilencerTypeEnum::FromString(const std::string& s) {
    if(s=="FLATOVAL") return IfcDuctSilencerTypeEnum::IfcDuctSilencerType_FLATOVAL;
    if(s=="RECTANGULAR") return IfcDuctSilencerTypeEnum::IfcDuctSilencerType_RECTANGULAR;
    if(s=="ROUND") return IfcDuctSilencerTypeEnum::IfcDuctSilencerType_ROUND;
    if(s=="USERDEFINED") return IfcDuctSilencerTypeEnum::IfcDuctSilencerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcDuctSilencerTypeEnum::IfcDuctSilencerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricApplianceTypeEnum::ToString(IfcElectricApplianceTypeEnum v) {
    if ( v < 0 || v >= 26 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COMPUTER","DIRECTWATERHEATER","DISHWASHER","ELECTRICCOOKER","ELECTRICHEATER","FACSIMILE","FREESTANDINGFAN","FREEZER","FRIDGE_FREEZER","HANDDRYER","INDIRECTWATERHEATER","MICROWAVE","PHOTOCOPIER","PRINTER","REFRIGERATOR","RADIANTHEATER","SCANNER","TELEPHONE","TUMBLEDRYER","TV","VENDINGMACHINE","WASHINGMACHINE","WATERHEATER","WATERCOOLER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricApplianceTypeEnum::IfcElectricApplianceTypeEnum IfcElectricApplianceTypeEnum::FromString(const std::string& s) {
    if(s=="COMPUTER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_COMPUTER;
    if(s=="DIRECTWATERHEATER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_DIRECTWATERHEATER;
    if(s=="DISHWASHER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_DISHWASHER;
    if(s=="ELECTRICCOOKER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_ELECTRICCOOKER;
    if(s=="ELECTRICHEATER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_ELECTRICHEATER;
    if(s=="FACSIMILE") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_FACSIMILE;
    if(s=="FREESTANDINGFAN") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_FREESTANDINGFAN;
    if(s=="FREEZER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_FREEZER;
    if(s=="FRIDGE_FREEZER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_FRIDGE_FREEZER;
    if(s=="HANDDRYER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_HANDDRYER;
    if(s=="INDIRECTWATERHEATER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_INDIRECTWATERHEATER;
    if(s=="MICROWAVE") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_MICROWAVE;
    if(s=="PHOTOCOPIER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_PHOTOCOPIER;
    if(s=="PRINTER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_PRINTER;
    if(s=="REFRIGERATOR") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_REFRIGERATOR;
    if(s=="RADIANTHEATER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_RADIANTHEATER;
    if(s=="SCANNER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_SCANNER;
    if(s=="TELEPHONE") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_TELEPHONE;
    if(s=="TUMBLEDRYER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_TUMBLEDRYER;
    if(s=="TV") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_TV;
    if(s=="VENDINGMACHINE") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_VENDINGMACHINE;
    if(s=="WASHINGMACHINE") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_WASHINGMACHINE;
    if(s=="WATERHEATER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_WATERHEATER;
    if(s=="WATERCOOLER") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_WATERCOOLER;
    if(s=="USERDEFINED") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElectricApplianceTypeEnum::IfcElectricApplianceType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricCurrentEnum::ToString(IfcElectricCurrentEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ALTERNATING","DIRECT","NOTDEFINED" };
    return names[v];
}
IfcElectricCurrentEnum::IfcElectricCurrentEnum IfcElectricCurrentEnum::FromString(const std::string& s) {
    if(s=="ALTERNATING") return IfcElectricCurrentEnum::IfcElectricCurrent_ALTERNATING;
    if(s=="DIRECT") return IfcElectricCurrentEnum::IfcElectricCurrent_DIRECT;
    if(s=="NOTDEFINED") return IfcElectricCurrentEnum::IfcElectricCurrent_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricDistributionPointFunctionEnum::ToString(IfcElectricDistributionPointFunctionEnum v) {
    if ( v < 0 || v >= 11 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ALARMPANEL","CONSUMERUNIT","CONTROLPANEL","DISTRIBUTIONBOARD","GASDETECTORPANEL","INDICATORPANEL","MIMICPANEL","MOTORCONTROLCENTRE","SWITCHBOARD","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunctionEnum IfcElectricDistributionPointFunctionEnum::FromString(const std::string& s) {
    if(s=="ALARMPANEL") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_ALARMPANEL;
    if(s=="CONSUMERUNIT") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_CONSUMERUNIT;
    if(s=="CONTROLPANEL") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_CONTROLPANEL;
    if(s=="DISTRIBUTIONBOARD") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_DISTRIBUTIONBOARD;
    if(s=="GASDETECTORPANEL") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_GASDETECTORPANEL;
    if(s=="INDICATORPANEL") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_INDICATORPANEL;
    if(s=="MIMICPANEL") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_MIMICPANEL;
    if(s=="MOTORCONTROLCENTRE") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_MOTORCONTROLCENTRE;
    if(s=="SWITCHBOARD") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_SWITCHBOARD;
    if(s=="USERDEFINED") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunction_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricFlowStorageDeviceTypeEnum::ToString(IfcElectricFlowStorageDeviceTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BATTERY","CAPACITORBANK","HARMONICFILTER","INDUCTORBANK","UPS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceTypeEnum IfcElectricFlowStorageDeviceTypeEnum::FromString(const std::string& s) {
    if(s=="BATTERY") return IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceType_BATTERY;
    if(s=="CAPACITORBANK") return IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceType_CAPACITORBANK;
    if(s=="HARMONICFILTER") return IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceType_HARMONICFILTER;
    if(s=="INDUCTORBANK") return IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceType_INDUCTORBANK;
    if(s=="UPS") return IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceType_UPS;
    if(s=="USERDEFINED") return IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricGeneratorTypeEnum::ToString(IfcElectricGeneratorTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricGeneratorTypeEnum::IfcElectricGeneratorTypeEnum IfcElectricGeneratorTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcElectricGeneratorTypeEnum::IfcElectricGeneratorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElectricGeneratorTypeEnum::IfcElectricGeneratorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricHeaterTypeEnum::ToString(IfcElectricHeaterTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ELECTRICPOINTHEATER","ELECTRICCABLEHEATER","ELECTRICMATHEATER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricHeaterTypeEnum::IfcElectricHeaterTypeEnum IfcElectricHeaterTypeEnum::FromString(const std::string& s) {
    if(s=="ELECTRICPOINTHEATER") return IfcElectricHeaterTypeEnum::IfcElectricHeaterType_ELECTRICPOINTHEATER;
    if(s=="ELECTRICCABLEHEATER") return IfcElectricHeaterTypeEnum::IfcElectricHeaterType_ELECTRICCABLEHEATER;
    if(s=="ELECTRICMATHEATER") return IfcElectricHeaterTypeEnum::IfcElectricHeaterType_ELECTRICMATHEATER;
    if(s=="USERDEFINED") return IfcElectricHeaterTypeEnum::IfcElectricHeaterType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElectricHeaterTypeEnum::IfcElectricHeaterType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricMotorTypeEnum::ToString(IfcElectricMotorTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DC","INDUCTION","POLYPHASE","RELUCTANCESYNCHRONOUS","SYNCHRONOUS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricMotorTypeEnum::IfcElectricMotorTypeEnum IfcElectricMotorTypeEnum::FromString(const std::string& s) {
    if(s=="DC") return IfcElectricMotorTypeEnum::IfcElectricMotorType_DC;
    if(s=="INDUCTION") return IfcElectricMotorTypeEnum::IfcElectricMotorType_INDUCTION;
    if(s=="POLYPHASE") return IfcElectricMotorTypeEnum::IfcElectricMotorType_POLYPHASE;
    if(s=="RELUCTANCESYNCHRONOUS") return IfcElectricMotorTypeEnum::IfcElectricMotorType_RELUCTANCESYNCHRONOUS;
    if(s=="SYNCHRONOUS") return IfcElectricMotorTypeEnum::IfcElectricMotorType_SYNCHRONOUS;
    if(s=="USERDEFINED") return IfcElectricMotorTypeEnum::IfcElectricMotorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElectricMotorTypeEnum::IfcElectricMotorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElectricTimeControlTypeEnum::ToString(IfcElectricTimeControlTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "TIMECLOCK","TIMEDELAY","RELAY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricTimeControlTypeEnum::IfcElectricTimeControlTypeEnum IfcElectricTimeControlTypeEnum::FromString(const std::string& s) {
    if(s=="TIMECLOCK") return IfcElectricTimeControlTypeEnum::IfcElectricTimeControlType_TIMECLOCK;
    if(s=="TIMEDELAY") return IfcElectricTimeControlTypeEnum::IfcElectricTimeControlType_TIMEDELAY;
    if(s=="RELAY") return IfcElectricTimeControlTypeEnum::IfcElectricTimeControlType_RELAY;
    if(s=="USERDEFINED") return IfcElectricTimeControlTypeEnum::IfcElectricTimeControlType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElectricTimeControlTypeEnum::IfcElectricTimeControlType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElementAssemblyTypeEnum::ToString(IfcElementAssemblyTypeEnum v) {
    if ( v < 0 || v >= 11 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ACCESSORY_ASSEMBLY","ARCH","BEAM_GRID","BRACED_FRAME","GIRDER","REINFORCEMENT_UNIT","RIGID_FRAME","SLAB_FIELD","TRUSS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElementAssemblyTypeEnum::IfcElementAssemblyTypeEnum IfcElementAssemblyTypeEnum::FromString(const std::string& s) {
    if(s=="ACCESSORY_ASSEMBLY") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_ACCESSORY_ASSEMBLY;
    if(s=="ARCH") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_ARCH;
    if(s=="BEAM_GRID") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_BEAM_GRID;
    if(s=="BRACED_FRAME") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_BRACED_FRAME;
    if(s=="GIRDER") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_GIRDER;
    if(s=="REINFORCEMENT_UNIT") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_REINFORCEMENT_UNIT;
    if(s=="RIGID_FRAME") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_RIGID_FRAME;
    if(s=="SLAB_FIELD") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_SLAB_FIELD;
    if(s=="TRUSS") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_TRUSS;
    if(s=="USERDEFINED") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcElementAssemblyTypeEnum::IfcElementAssemblyType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcElementCompositionEnum::ToString(IfcElementCompositionEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COMPLEX","ELEMENT","PARTIAL" };
    return names[v];
}
IfcElementCompositionEnum::IfcElementCompositionEnum IfcElementCompositionEnum::FromString(const std::string& s) {
    if(s=="COMPLEX") return IfcElementCompositionEnum::IfcElementComposition_COMPLEX;
    if(s=="ELEMENT") return IfcElementCompositionEnum::IfcElementComposition_ELEMENT;
    if(s=="PARTIAL") return IfcElementCompositionEnum::IfcElementComposition_PARTIAL;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcEnergySequenceEnum::ToString(IfcEnergySequenceEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PRIMARY","SECONDARY","TERTIARY","AUXILIARY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEnergySequenceEnum::IfcEnergySequenceEnum IfcEnergySequenceEnum::FromString(const std::string& s) {
    if(s=="PRIMARY") return IfcEnergySequenceEnum::IfcEnergySequence_PRIMARY;
    if(s=="SECONDARY") return IfcEnergySequenceEnum::IfcEnergySequence_SECONDARY;
    if(s=="TERTIARY") return IfcEnergySequenceEnum::IfcEnergySequence_TERTIARY;
    if(s=="AUXILIARY") return IfcEnergySequenceEnum::IfcEnergySequence_AUXILIARY;
    if(s=="USERDEFINED") return IfcEnergySequenceEnum::IfcEnergySequence_USERDEFINED;
    if(s=="NOTDEFINED") return IfcEnergySequenceEnum::IfcEnergySequence_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcEnvironmentalImpactCategoryEnum::ToString(IfcEnvironmentalImpactCategoryEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COMBINEDVALUE","DISPOSAL","EXTRACTION","INSTALLATION","MANUFACTURE","TRANSPORTATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategoryEnum IfcEnvironmentalImpactCategoryEnum::FromString(const std::string& s) {
    if(s=="COMBINEDVALUE") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_COMBINEDVALUE;
    if(s=="DISPOSAL") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_DISPOSAL;
    if(s=="EXTRACTION") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_EXTRACTION;
    if(s=="INSTALLATION") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_INSTALLATION;
    if(s=="MANUFACTURE") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_MANUFACTURE;
    if(s=="TRANSPORTATION") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_TRANSPORTATION;
    if(s=="USERDEFINED") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_USERDEFINED;
    if(s=="NOTDEFINED") return IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategory_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcEvaporativeCoolerTypeEnum::ToString(IfcEvaporativeCoolerTypeEnum v) {
    if ( v < 0 || v >= 11 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER","DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER","DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER","DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER","DIRECTEVAPORATIVEAIRWASHER","INDIRECTEVAPORATIVEPACKAGEAIRCOOLER","INDIRECTEVAPORATIVEWETCOIL","INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER","INDIRECTDIRECTCOMBINATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerTypeEnum IfcEvaporativeCoolerTypeEnum::FromString(const std::string& s) {
    if(s=="DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER;
    if(s=="DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER;
    if(s=="DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER;
    if(s=="DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER;
    if(s=="DIRECTEVAPORATIVEAIRWASHER") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_DIRECTEVAPORATIVEAIRWASHER;
    if(s=="INDIRECTEVAPORATIVEPACKAGEAIRCOOLER") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_INDIRECTEVAPORATIVEPACKAGEAIRCOOLER;
    if(s=="INDIRECTEVAPORATIVEWETCOIL") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_INDIRECTEVAPORATIVEWETCOIL;
    if(s=="INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER;
    if(s=="INDIRECTDIRECTCOMBINATION") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_INDIRECTDIRECTCOMBINATION;
    if(s=="USERDEFINED") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcEvaporatorTypeEnum::ToString(IfcEvaporatorTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DIRECTEXPANSIONSHELLANDTUBE","DIRECTEXPANSIONTUBEINTUBE","DIRECTEXPANSIONBRAZEDPLATE","FLOODEDSHELLANDTUBE","SHELLANDCOIL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEvaporatorTypeEnum::IfcEvaporatorTypeEnum IfcEvaporatorTypeEnum::FromString(const std::string& s) {
    if(s=="DIRECTEXPANSIONSHELLANDTUBE") return IfcEvaporatorTypeEnum::IfcEvaporatorType_DIRECTEXPANSIONSHELLANDTUBE;
    if(s=="DIRECTEXPANSIONTUBEINTUBE") return IfcEvaporatorTypeEnum::IfcEvaporatorType_DIRECTEXPANSIONTUBEINTUBE;
    if(s=="DIRECTEXPANSIONBRAZEDPLATE") return IfcEvaporatorTypeEnum::IfcEvaporatorType_DIRECTEXPANSIONBRAZEDPLATE;
    if(s=="FLOODEDSHELLANDTUBE") return IfcEvaporatorTypeEnum::IfcEvaporatorType_FLOODEDSHELLANDTUBE;
    if(s=="SHELLANDCOIL") return IfcEvaporatorTypeEnum::IfcEvaporatorType_SHELLANDCOIL;
    if(s=="USERDEFINED") return IfcEvaporatorTypeEnum::IfcEvaporatorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcEvaporatorTypeEnum::IfcEvaporatorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcFanTypeEnum::ToString(IfcFanTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CENTRIFUGALFORWARDCURVED","CENTRIFUGALRADIAL","CENTRIFUGALBACKWARDINCLINEDCURVED","CENTRIFUGALAIRFOIL","TUBEAXIAL","VANEAXIAL","PROPELLORAXIAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFanTypeEnum::IfcFanTypeEnum IfcFanTypeEnum::FromString(const std::string& s) {
    if(s=="CENTRIFUGALFORWARDCURVED") return IfcFanTypeEnum::IfcFanType_CENTRIFUGALFORWARDCURVED;
    if(s=="CENTRIFUGALRADIAL") return IfcFanTypeEnum::IfcFanType_CENTRIFUGALRADIAL;
    if(s=="CENTRIFUGALBACKWARDINCLINEDCURVED") return IfcFanTypeEnum::IfcFanType_CENTRIFUGALBACKWARDINCLINEDCURVED;
    if(s=="CENTRIFUGALAIRFOIL") return IfcFanTypeEnum::IfcFanType_CENTRIFUGALAIRFOIL;
    if(s=="TUBEAXIAL") return IfcFanTypeEnum::IfcFanType_TUBEAXIAL;
    if(s=="VANEAXIAL") return IfcFanTypeEnum::IfcFanType_VANEAXIAL;
    if(s=="PROPELLORAXIAL") return IfcFanTypeEnum::IfcFanType_PROPELLORAXIAL;
    if(s=="USERDEFINED") return IfcFanTypeEnum::IfcFanType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcFanTypeEnum::IfcFanType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcFilterTypeEnum::ToString(IfcFilterTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AIRPARTICLEFILTER","ODORFILTER","OILFILTER","STRAINER","WATERFILTER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFilterTypeEnum::IfcFilterTypeEnum IfcFilterTypeEnum::FromString(const std::string& s) {
    if(s=="AIRPARTICLEFILTER") return IfcFilterTypeEnum::IfcFilterType_AIRPARTICLEFILTER;
    if(s=="ODORFILTER") return IfcFilterTypeEnum::IfcFilterType_ODORFILTER;
    if(s=="OILFILTER") return IfcFilterTypeEnum::IfcFilterType_OILFILTER;
    if(s=="STRAINER") return IfcFilterTypeEnum::IfcFilterType_STRAINER;
    if(s=="WATERFILTER") return IfcFilterTypeEnum::IfcFilterType_WATERFILTER;
    if(s=="USERDEFINED") return IfcFilterTypeEnum::IfcFilterType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcFilterTypeEnum::IfcFilterType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcFireSuppressionTerminalTypeEnum::ToString(IfcFireSuppressionTerminalTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BREECHINGINLET","FIREHYDRANT","HOSEREEL","SPRINKLER","SPRINKLERDEFLECTOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalTypeEnum IfcFireSuppressionTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="BREECHINGINLET") return IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalType_BREECHINGINLET;
    if(s=="FIREHYDRANT") return IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalType_FIREHYDRANT;
    if(s=="HOSEREEL") return IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalType_HOSEREEL;
    if(s=="SPRINKLER") return IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalType_SPRINKLER;
    if(s=="SPRINKLERDEFLECTOR") return IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalType_SPRINKLERDEFLECTOR;
    if(s=="USERDEFINED") return IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcFlowDirectionEnum::ToString(IfcFlowDirectionEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SOURCE","SINK","SOURCEANDSINK","NOTDEFINED" };
    return names[v];
}
IfcFlowDirectionEnum::IfcFlowDirectionEnum IfcFlowDirectionEnum::FromString(const std::string& s) {
    if(s=="SOURCE") return IfcFlowDirectionEnum::IfcFlowDirection_SOURCE;
    if(s=="SINK") return IfcFlowDirectionEnum::IfcFlowDirection_SINK;
    if(s=="SOURCEANDSINK") return IfcFlowDirectionEnum::IfcFlowDirection_SOURCEANDSINK;
    if(s=="NOTDEFINED") return IfcFlowDirectionEnum::IfcFlowDirection_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcFlowInstrumentTypeEnum::ToString(IfcFlowInstrumentTypeEnum v) {
    if ( v < 0 || v >= 10 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PRESSUREGAUGE","THERMOMETER","AMMETER","FREQUENCYMETER","POWERFACTORMETER","PHASEANGLEMETER","VOLTMETER_PEAK","VOLTMETER_RMS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFlowInstrumentTypeEnum::IfcFlowInstrumentTypeEnum IfcFlowInstrumentTypeEnum::FromString(const std::string& s) {
    if(s=="PRESSUREGAUGE") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_PRESSUREGAUGE;
    if(s=="THERMOMETER") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_THERMOMETER;
    if(s=="AMMETER") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_AMMETER;
    if(s=="FREQUENCYMETER") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_FREQUENCYMETER;
    if(s=="POWERFACTORMETER") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_POWERFACTORMETER;
    if(s=="PHASEANGLEMETER") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_PHASEANGLEMETER;
    if(s=="VOLTMETER_PEAK") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_VOLTMETER_PEAK;
    if(s=="VOLTMETER_RMS") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_VOLTMETER_RMS;
    if(s=="USERDEFINED") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcFlowInstrumentTypeEnum::IfcFlowInstrumentType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcFlowMeterTypeEnum::ToString(IfcFlowMeterTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ELECTRICMETER","ENERGYMETER","FLOWMETER","GASMETER","OILMETER","WATERMETER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFlowMeterTypeEnum::IfcFlowMeterTypeEnum IfcFlowMeterTypeEnum::FromString(const std::string& s) {
    if(s=="ELECTRICMETER") return IfcFlowMeterTypeEnum::IfcFlowMeterType_ELECTRICMETER;
    if(s=="ENERGYMETER") return IfcFlowMeterTypeEnum::IfcFlowMeterType_ENERGYMETER;
    if(s=="FLOWMETER") return IfcFlowMeterTypeEnum::IfcFlowMeterType_FLOWMETER;
    if(s=="GASMETER") return IfcFlowMeterTypeEnum::IfcFlowMeterType_GASMETER;
    if(s=="OILMETER") return IfcFlowMeterTypeEnum::IfcFlowMeterType_OILMETER;
    if(s=="WATERMETER") return IfcFlowMeterTypeEnum::IfcFlowMeterType_WATERMETER;
    if(s=="USERDEFINED") return IfcFlowMeterTypeEnum::IfcFlowMeterType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcFlowMeterTypeEnum::IfcFlowMeterType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcFootingTypeEnum::ToString(IfcFootingTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FOOTING_BEAM","PAD_FOOTING","PILE_CAP","STRIP_FOOTING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFootingTypeEnum::IfcFootingTypeEnum IfcFootingTypeEnum::FromString(const std::string& s) {
    if(s=="FOOTING_BEAM") return IfcFootingTypeEnum::IfcFootingType_FOOTING_BEAM;
    if(s=="PAD_FOOTING") return IfcFootingTypeEnum::IfcFootingType_PAD_FOOTING;
    if(s=="PILE_CAP") return IfcFootingTypeEnum::IfcFootingType_PILE_CAP;
    if(s=="STRIP_FOOTING") return IfcFootingTypeEnum::IfcFootingType_STRIP_FOOTING;
    if(s=="USERDEFINED") return IfcFootingTypeEnum::IfcFootingType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcFootingTypeEnum::IfcFootingType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcGasTerminalTypeEnum::ToString(IfcGasTerminalTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "GASAPPLIANCE","GASBOOSTER","GASBURNER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcGasTerminalTypeEnum::IfcGasTerminalTypeEnum IfcGasTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="GASAPPLIANCE") return IfcGasTerminalTypeEnum::IfcGasTerminalType_GASAPPLIANCE;
    if(s=="GASBOOSTER") return IfcGasTerminalTypeEnum::IfcGasTerminalType_GASBOOSTER;
    if(s=="GASBURNER") return IfcGasTerminalTypeEnum::IfcGasTerminalType_GASBURNER;
    if(s=="USERDEFINED") return IfcGasTerminalTypeEnum::IfcGasTerminalType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcGasTerminalTypeEnum::IfcGasTerminalType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcGeometricProjectionEnum::ToString(IfcGeometricProjectionEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "GRAPH_VIEW","SKETCH_VIEW","MODEL_VIEW","PLAN_VIEW","REFLECTED_PLAN_VIEW","SECTION_VIEW","ELEVATION_VIEW","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcGeometricProjectionEnum::IfcGeometricProjectionEnum IfcGeometricProjectionEnum::FromString(const std::string& s) {
    if(s=="GRAPH_VIEW") return IfcGeometricProjectionEnum::IfcGeometricProjection_GRAPH_VIEW;
    if(s=="SKETCH_VIEW") return IfcGeometricProjectionEnum::IfcGeometricProjection_SKETCH_VIEW;
    if(s=="MODEL_VIEW") return IfcGeometricProjectionEnum::IfcGeometricProjection_MODEL_VIEW;
    if(s=="PLAN_VIEW") return IfcGeometricProjectionEnum::IfcGeometricProjection_PLAN_VIEW;
    if(s=="REFLECTED_PLAN_VIEW") return IfcGeometricProjectionEnum::IfcGeometricProjection_REFLECTED_PLAN_VIEW;
    if(s=="SECTION_VIEW") return IfcGeometricProjectionEnum::IfcGeometricProjection_SECTION_VIEW;
    if(s=="ELEVATION_VIEW") return IfcGeometricProjectionEnum::IfcGeometricProjection_ELEVATION_VIEW;
    if(s=="USERDEFINED") return IfcGeometricProjectionEnum::IfcGeometricProjection_USERDEFINED;
    if(s=="NOTDEFINED") return IfcGeometricProjectionEnum::IfcGeometricProjection_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcGlobalOrLocalEnum::ToString(IfcGlobalOrLocalEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "GLOBAL_COORDS","LOCAL_COORDS" };
    return names[v];
}
IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum IfcGlobalOrLocalEnum::FromString(const std::string& s) {
    if(s=="GLOBAL_COORDS") return IfcGlobalOrLocalEnum::IfcGlobalOrLocal_GLOBAL_COORDS;
    if(s=="LOCAL_COORDS") return IfcGlobalOrLocalEnum::IfcGlobalOrLocal_LOCAL_COORDS;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcHeatExchangerTypeEnum::ToString(IfcHeatExchangerTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PLATE","SHELLANDTUBE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcHeatExchangerTypeEnum::IfcHeatExchangerTypeEnum IfcHeatExchangerTypeEnum::FromString(const std::string& s) {
    if(s=="PLATE") return IfcHeatExchangerTypeEnum::IfcHeatExchangerType_PLATE;
    if(s=="SHELLANDTUBE") return IfcHeatExchangerTypeEnum::IfcHeatExchangerType_SHELLANDTUBE;
    if(s=="USERDEFINED") return IfcHeatExchangerTypeEnum::IfcHeatExchangerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcHeatExchangerTypeEnum::IfcHeatExchangerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcHumidifierTypeEnum::ToString(IfcHumidifierTypeEnum v) {
    if ( v < 0 || v >= 15 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "STEAMINJECTION","ADIABATICAIRWASHER","ADIABATICPAN","ADIABATICWETTEDELEMENT","ADIABATICATOMIZING","ADIABATICULTRASONIC","ADIABATICRIGIDMEDIA","ADIABATICCOMPRESSEDAIRNOZZLE","ASSISTEDELECTRIC","ASSISTEDNATURALGAS","ASSISTEDPROPANE","ASSISTEDBUTANE","ASSISTEDSTEAM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcHumidifierTypeEnum::IfcHumidifierTypeEnum IfcHumidifierTypeEnum::FromString(const std::string& s) {
    if(s=="STEAMINJECTION") return IfcHumidifierTypeEnum::IfcHumidifierType_STEAMINJECTION;
    if(s=="ADIABATICAIRWASHER") return IfcHumidifierTypeEnum::IfcHumidifierType_ADIABATICAIRWASHER;
    if(s=="ADIABATICPAN") return IfcHumidifierTypeEnum::IfcHumidifierType_ADIABATICPAN;
    if(s=="ADIABATICWETTEDELEMENT") return IfcHumidifierTypeEnum::IfcHumidifierType_ADIABATICWETTEDELEMENT;
    if(s=="ADIABATICATOMIZING") return IfcHumidifierTypeEnum::IfcHumidifierType_ADIABATICATOMIZING;
    if(s=="ADIABATICULTRASONIC") return IfcHumidifierTypeEnum::IfcHumidifierType_ADIABATICULTRASONIC;
    if(s=="ADIABATICRIGIDMEDIA") return IfcHumidifierTypeEnum::IfcHumidifierType_ADIABATICRIGIDMEDIA;
    if(s=="ADIABATICCOMPRESSEDAIRNOZZLE") return IfcHumidifierTypeEnum::IfcHumidifierType_ADIABATICCOMPRESSEDAIRNOZZLE;
    if(s=="ASSISTEDELECTRIC") return IfcHumidifierTypeEnum::IfcHumidifierType_ASSISTEDELECTRIC;
    if(s=="ASSISTEDNATURALGAS") return IfcHumidifierTypeEnum::IfcHumidifierType_ASSISTEDNATURALGAS;
    if(s=="ASSISTEDPROPANE") return IfcHumidifierTypeEnum::IfcHumidifierType_ASSISTEDPROPANE;
    if(s=="ASSISTEDBUTANE") return IfcHumidifierTypeEnum::IfcHumidifierType_ASSISTEDBUTANE;
    if(s=="ASSISTEDSTEAM") return IfcHumidifierTypeEnum::IfcHumidifierType_ASSISTEDSTEAM;
    if(s=="USERDEFINED") return IfcHumidifierTypeEnum::IfcHumidifierType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcHumidifierTypeEnum::IfcHumidifierType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcInternalOrExternalEnum::ToString(IfcInternalOrExternalEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "INTERNAL","EXTERNAL","NOTDEFINED" };
    return names[v];
}
IfcInternalOrExternalEnum::IfcInternalOrExternalEnum IfcInternalOrExternalEnum::FromString(const std::string& s) {
    if(s=="INTERNAL") return IfcInternalOrExternalEnum::IfcInternalOrExternal_INTERNAL;
    if(s=="EXTERNAL") return IfcInternalOrExternalEnum::IfcInternalOrExternal_EXTERNAL;
    if(s=="NOTDEFINED") return IfcInternalOrExternalEnum::IfcInternalOrExternal_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcInventoryTypeEnum::ToString(IfcInventoryTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ASSETINVENTORY","SPACEINVENTORY","FURNITUREINVENTORY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcInventoryTypeEnum::IfcInventoryTypeEnum IfcInventoryTypeEnum::FromString(const std::string& s) {
    if(s=="ASSETINVENTORY") return IfcInventoryTypeEnum::IfcInventoryType_ASSETINVENTORY;
    if(s=="SPACEINVENTORY") return IfcInventoryTypeEnum::IfcInventoryType_SPACEINVENTORY;
    if(s=="FURNITUREINVENTORY") return IfcInventoryTypeEnum::IfcInventoryType_FURNITUREINVENTORY;
    if(s=="USERDEFINED") return IfcInventoryTypeEnum::IfcInventoryType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcInventoryTypeEnum::IfcInventoryType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcJunctionBoxTypeEnum::ToString(IfcJunctionBoxTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcJunctionBoxTypeEnum::IfcJunctionBoxTypeEnum IfcJunctionBoxTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcJunctionBoxTypeEnum::IfcJunctionBoxType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcJunctionBoxTypeEnum::IfcJunctionBoxType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcLampTypeEnum::ToString(IfcLampTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COMPACTFLUORESCENT","FLUORESCENT","HIGHPRESSUREMERCURY","HIGHPRESSURESODIUM","METALHALIDE","TUNGSTENFILAMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcLampTypeEnum::IfcLampTypeEnum IfcLampTypeEnum::FromString(const std::string& s) {
    if(s=="COMPACTFLUORESCENT") return IfcLampTypeEnum::IfcLampType_COMPACTFLUORESCENT;
    if(s=="FLUORESCENT") return IfcLampTypeEnum::IfcLampType_FLUORESCENT;
    if(s=="HIGHPRESSUREMERCURY") return IfcLampTypeEnum::IfcLampType_HIGHPRESSUREMERCURY;
    if(s=="HIGHPRESSURESODIUM") return IfcLampTypeEnum::IfcLampType_HIGHPRESSURESODIUM;
    if(s=="METALHALIDE") return IfcLampTypeEnum::IfcLampType_METALHALIDE;
    if(s=="TUNGSTENFILAMENT") return IfcLampTypeEnum::IfcLampType_TUNGSTENFILAMENT;
    if(s=="USERDEFINED") return IfcLampTypeEnum::IfcLampType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcLampTypeEnum::IfcLampType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcLayerSetDirectionEnum::ToString(IfcLayerSetDirectionEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AXIS1","AXIS2","AXIS3" };
    return names[v];
}
IfcLayerSetDirectionEnum::IfcLayerSetDirectionEnum IfcLayerSetDirectionEnum::FromString(const std::string& s) {
    if(s=="AXIS1") return IfcLayerSetDirectionEnum::IfcLayerSetDirection_AXIS1;
    if(s=="AXIS2") return IfcLayerSetDirectionEnum::IfcLayerSetDirection_AXIS2;
    if(s=="AXIS3") return IfcLayerSetDirectionEnum::IfcLayerSetDirection_AXIS3;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcLightDistributionCurveEnum::ToString(IfcLightDistributionCurveEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "TYPE_A","TYPE_B","TYPE_C","NOTDEFINED" };
    return names[v];
}
IfcLightDistributionCurveEnum::IfcLightDistributionCurveEnum IfcLightDistributionCurveEnum::FromString(const std::string& s) {
    if(s=="TYPE_A") return IfcLightDistributionCurveEnum::IfcLightDistributionCurve_TYPE_A;
    if(s=="TYPE_B") return IfcLightDistributionCurveEnum::IfcLightDistributionCurve_TYPE_B;
    if(s=="TYPE_C") return IfcLightDistributionCurveEnum::IfcLightDistributionCurve_TYPE_C;
    if(s=="NOTDEFINED") return IfcLightDistributionCurveEnum::IfcLightDistributionCurve_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcLightEmissionSourceEnum::ToString(IfcLightEmissionSourceEnum v) {
    if ( v < 0 || v >= 11 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COMPACTFLUORESCENT","FLUORESCENT","HIGHPRESSUREMERCURY","HIGHPRESSURESODIUM","LIGHTEMITTINGDIODE","LOWPRESSURESODIUM","LOWVOLTAGEHALOGEN","MAINVOLTAGEHALOGEN","METALHALIDE","TUNGSTENFILAMENT","NOTDEFINED" };
    return names[v];
}
IfcLightEmissionSourceEnum::IfcLightEmissionSourceEnum IfcLightEmissionSourceEnum::FromString(const std::string& s) {
    if(s=="COMPACTFLUORESCENT") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_COMPACTFLUORESCENT;
    if(s=="FLUORESCENT") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_FLUORESCENT;
    if(s=="HIGHPRESSUREMERCURY") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_HIGHPRESSUREMERCURY;
    if(s=="HIGHPRESSURESODIUM") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_HIGHPRESSURESODIUM;
    if(s=="LIGHTEMITTINGDIODE") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_LIGHTEMITTINGDIODE;
    if(s=="LOWPRESSURESODIUM") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_LOWPRESSURESODIUM;
    if(s=="LOWVOLTAGEHALOGEN") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_LOWVOLTAGEHALOGEN;
    if(s=="MAINVOLTAGEHALOGEN") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_MAINVOLTAGEHALOGEN;
    if(s=="METALHALIDE") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_METALHALIDE;
    if(s=="TUNGSTENFILAMENT") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_TUNGSTENFILAMENT;
    if(s=="NOTDEFINED") return IfcLightEmissionSourceEnum::IfcLightEmissionSource_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcLightFixtureTypeEnum::ToString(IfcLightFixtureTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "POINTSOURCE","DIRECTIONSOURCE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcLightFixtureTypeEnum::IfcLightFixtureTypeEnum IfcLightFixtureTypeEnum::FromString(const std::string& s) {
    if(s=="POINTSOURCE") return IfcLightFixtureTypeEnum::IfcLightFixtureType_POINTSOURCE;
    if(s=="DIRECTIONSOURCE") return IfcLightFixtureTypeEnum::IfcLightFixtureType_DIRECTIONSOURCE;
    if(s=="USERDEFINED") return IfcLightFixtureTypeEnum::IfcLightFixtureType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcLightFixtureTypeEnum::IfcLightFixtureType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcLoadGroupTypeEnum::ToString(IfcLoadGroupTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "LOAD_GROUP","LOAD_CASE","LOAD_COMBINATION_GROUP","LOAD_COMBINATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcLoadGroupTypeEnum::IfcLoadGroupTypeEnum IfcLoadGroupTypeEnum::FromString(const std::string& s) {
    if(s=="LOAD_GROUP") return IfcLoadGroupTypeEnum::IfcLoadGroupType_LOAD_GROUP;
    if(s=="LOAD_CASE") return IfcLoadGroupTypeEnum::IfcLoadGroupType_LOAD_CASE;
    if(s=="LOAD_COMBINATION_GROUP") return IfcLoadGroupTypeEnum::IfcLoadGroupType_LOAD_COMBINATION_GROUP;
    if(s=="LOAD_COMBINATION") return IfcLoadGroupTypeEnum::IfcLoadGroupType_LOAD_COMBINATION;
    if(s=="USERDEFINED") return IfcLoadGroupTypeEnum::IfcLoadGroupType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcLoadGroupTypeEnum::IfcLoadGroupType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcLogicalOperatorEnum::ToString(IfcLogicalOperatorEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "LOGICALAND","LOGICALOR" };
    return names[v];
}
IfcLogicalOperatorEnum::IfcLogicalOperatorEnum IfcLogicalOperatorEnum::FromString(const std::string& s) {
    if(s=="LOGICALAND") return IfcLogicalOperatorEnum::IfcLogicalOperator_LOGICALAND;
    if(s=="LOGICALOR") return IfcLogicalOperatorEnum::IfcLogicalOperator_LOGICALOR;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcMemberTypeEnum::ToString(IfcMemberTypeEnum v) {
    if ( v < 0 || v >= 14 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BRACE","CHORD","COLLAR","MEMBER","MULLION","PLATE","POST","PURLIN","RAFTER","STRINGER","STRUT","STUD","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcMemberTypeEnum::IfcMemberTypeEnum IfcMemberTypeEnum::FromString(const std::string& s) {
    if(s=="BRACE") return IfcMemberTypeEnum::IfcMemberType_BRACE;
    if(s=="CHORD") return IfcMemberTypeEnum::IfcMemberType_CHORD;
    if(s=="COLLAR") return IfcMemberTypeEnum::IfcMemberType_COLLAR;
    if(s=="MEMBER") return IfcMemberTypeEnum::IfcMemberType_MEMBER;
    if(s=="MULLION") return IfcMemberTypeEnum::IfcMemberType_MULLION;
    if(s=="PLATE") return IfcMemberTypeEnum::IfcMemberType_PLATE;
    if(s=="POST") return IfcMemberTypeEnum::IfcMemberType_POST;
    if(s=="PURLIN") return IfcMemberTypeEnum::IfcMemberType_PURLIN;
    if(s=="RAFTER") return IfcMemberTypeEnum::IfcMemberType_RAFTER;
    if(s=="STRINGER") return IfcMemberTypeEnum::IfcMemberType_STRINGER;
    if(s=="STRUT") return IfcMemberTypeEnum::IfcMemberType_STRUT;
    if(s=="STUD") return IfcMemberTypeEnum::IfcMemberType_STUD;
    if(s=="USERDEFINED") return IfcMemberTypeEnum::IfcMemberType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcMemberTypeEnum::IfcMemberType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcMotorConnectionTypeEnum::ToString(IfcMotorConnectionTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BELTDRIVE","COUPLING","DIRECTDRIVE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcMotorConnectionTypeEnum::IfcMotorConnectionTypeEnum IfcMotorConnectionTypeEnum::FromString(const std::string& s) {
    if(s=="BELTDRIVE") return IfcMotorConnectionTypeEnum::IfcMotorConnectionType_BELTDRIVE;
    if(s=="COUPLING") return IfcMotorConnectionTypeEnum::IfcMotorConnectionType_COUPLING;
    if(s=="DIRECTDRIVE") return IfcMotorConnectionTypeEnum::IfcMotorConnectionType_DIRECTDRIVE;
    if(s=="USERDEFINED") return IfcMotorConnectionTypeEnum::IfcMotorConnectionType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcMotorConnectionTypeEnum::IfcMotorConnectionType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcNullStyle::ToString(IfcNullStyle v) {
    if ( v < 0 || v >= 1 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "NULL" };
    return names[v];
}
IfcNullStyle::IfcNullStyle IfcNullStyle::FromString(const std::string& s) {
    if(s=="NULL") return IfcNullStyle::IfcNullStyle_NULL;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcObjectTypeEnum::ToString(IfcObjectTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PRODUCT","PROCESS","CONTROL","RESOURCE","ACTOR","GROUP","PROJECT","NOTDEFINED" };
    return names[v];
}
IfcObjectTypeEnum::IfcObjectTypeEnum IfcObjectTypeEnum::FromString(const std::string& s) {
    if(s=="PRODUCT") return IfcObjectTypeEnum::IfcObjectType_PRODUCT;
    if(s=="PROCESS") return IfcObjectTypeEnum::IfcObjectType_PROCESS;
    if(s=="CONTROL") return IfcObjectTypeEnum::IfcObjectType_CONTROL;
    if(s=="RESOURCE") return IfcObjectTypeEnum::IfcObjectType_RESOURCE;
    if(s=="ACTOR") return IfcObjectTypeEnum::IfcObjectType_ACTOR;
    if(s=="GROUP") return IfcObjectTypeEnum::IfcObjectType_GROUP;
    if(s=="PROJECT") return IfcObjectTypeEnum::IfcObjectType_PROJECT;
    if(s=="NOTDEFINED") return IfcObjectTypeEnum::IfcObjectType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcObjectiveEnum::ToString(IfcObjectiveEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CODECOMPLIANCE","DESIGNINTENT","HEALTHANDSAFETY","REQUIREMENT","SPECIFICATION","TRIGGERCONDITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcObjectiveEnum::IfcObjectiveEnum IfcObjectiveEnum::FromString(const std::string& s) {
    if(s=="CODECOMPLIANCE") return IfcObjectiveEnum::IfcObjective_CODECOMPLIANCE;
    if(s=="DESIGNINTENT") return IfcObjectiveEnum::IfcObjective_DESIGNINTENT;
    if(s=="HEALTHANDSAFETY") return IfcObjectiveEnum::IfcObjective_HEALTHANDSAFETY;
    if(s=="REQUIREMENT") return IfcObjectiveEnum::IfcObjective_REQUIREMENT;
    if(s=="SPECIFICATION") return IfcObjectiveEnum::IfcObjective_SPECIFICATION;
    if(s=="TRIGGERCONDITION") return IfcObjectiveEnum::IfcObjective_TRIGGERCONDITION;
    if(s=="USERDEFINED") return IfcObjectiveEnum::IfcObjective_USERDEFINED;
    if(s=="NOTDEFINED") return IfcObjectiveEnum::IfcObjective_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcOccupantTypeEnum::ToString(IfcOccupantTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ASSIGNEE","ASSIGNOR","LESSEE","LESSOR","LETTINGAGENT","OWNER","TENANT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcOccupantTypeEnum::IfcOccupantTypeEnum IfcOccupantTypeEnum::FromString(const std::string& s) {
    if(s=="ASSIGNEE") return IfcOccupantTypeEnum::IfcOccupantType_ASSIGNEE;
    if(s=="ASSIGNOR") return IfcOccupantTypeEnum::IfcOccupantType_ASSIGNOR;
    if(s=="LESSEE") return IfcOccupantTypeEnum::IfcOccupantType_LESSEE;
    if(s=="LESSOR") return IfcOccupantTypeEnum::IfcOccupantType_LESSOR;
    if(s=="LETTINGAGENT") return IfcOccupantTypeEnum::IfcOccupantType_LETTINGAGENT;
    if(s=="OWNER") return IfcOccupantTypeEnum::IfcOccupantType_OWNER;
    if(s=="TENANT") return IfcOccupantTypeEnum::IfcOccupantType_TENANT;
    if(s=="USERDEFINED") return IfcOccupantTypeEnum::IfcOccupantType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcOccupantTypeEnum::IfcOccupantType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcOutletTypeEnum::ToString(IfcOutletTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AUDIOVISUALOUTLET","COMMUNICATIONSOUTLET","POWEROUTLET","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcOutletTypeEnum::IfcOutletTypeEnum IfcOutletTypeEnum::FromString(const std::string& s) {
    if(s=="AUDIOVISUALOUTLET") return IfcOutletTypeEnum::IfcOutletType_AUDIOVISUALOUTLET;
    if(s=="COMMUNICATIONSOUTLET") return IfcOutletTypeEnum::IfcOutletType_COMMUNICATIONSOUTLET;
    if(s=="POWEROUTLET") return IfcOutletTypeEnum::IfcOutletType_POWEROUTLET;
    if(s=="USERDEFINED") return IfcOutletTypeEnum::IfcOutletType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcOutletTypeEnum::IfcOutletType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPermeableCoveringOperationEnum::ToString(IfcPermeableCoveringOperationEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "GRILL","LOUVER","SCREEN","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperationEnum IfcPermeableCoveringOperationEnum::FromString(const std::string& s) {
    if(s=="GRILL") return IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperation_GRILL;
    if(s=="LOUVER") return IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperation_LOUVER;
    if(s=="SCREEN") return IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperation_SCREEN;
    if(s=="USERDEFINED") return IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperation_USERDEFINED;
    if(s=="NOTDEFINED") return IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperation_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPhysicalOrVirtualEnum::ToString(IfcPhysicalOrVirtualEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PHYSICAL","VIRTUAL","NOTDEFINED" };
    return names[v];
}
IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtualEnum IfcPhysicalOrVirtualEnum::FromString(const std::string& s) {
    if(s=="PHYSICAL") return IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtual_PHYSICAL;
    if(s=="VIRTUAL") return IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtual_VIRTUAL;
    if(s=="NOTDEFINED") return IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtual_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPileConstructionEnum::ToString(IfcPileConstructionEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CAST_IN_PLACE","COMPOSITE","PRECAST_CONCRETE","PREFAB_STEEL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPileConstructionEnum::IfcPileConstructionEnum IfcPileConstructionEnum::FromString(const std::string& s) {
    if(s=="CAST_IN_PLACE") return IfcPileConstructionEnum::IfcPileConstruction_CAST_IN_PLACE;
    if(s=="COMPOSITE") return IfcPileConstructionEnum::IfcPileConstruction_COMPOSITE;
    if(s=="PRECAST_CONCRETE") return IfcPileConstructionEnum::IfcPileConstruction_PRECAST_CONCRETE;
    if(s=="PREFAB_STEEL") return IfcPileConstructionEnum::IfcPileConstruction_PREFAB_STEEL;
    if(s=="USERDEFINED") return IfcPileConstructionEnum::IfcPileConstruction_USERDEFINED;
    if(s=="NOTDEFINED") return IfcPileConstructionEnum::IfcPileConstruction_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPileTypeEnum::ToString(IfcPileTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COHESION","FRICTION","SUPPORT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPileTypeEnum::IfcPileTypeEnum IfcPileTypeEnum::FromString(const std::string& s) {
    if(s=="COHESION") return IfcPileTypeEnum::IfcPileType_COHESION;
    if(s=="FRICTION") return IfcPileTypeEnum::IfcPileType_FRICTION;
    if(s=="SUPPORT") return IfcPileTypeEnum::IfcPileType_SUPPORT;
    if(s=="USERDEFINED") return IfcPileTypeEnum::IfcPileType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcPileTypeEnum::IfcPileType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPipeFittingTypeEnum::ToString(IfcPipeFittingTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BEND","CONNECTOR","ENTRY","EXIT","JUNCTION","OBSTRUCTION","TRANSITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPipeFittingTypeEnum::IfcPipeFittingTypeEnum IfcPipeFittingTypeEnum::FromString(const std::string& s) {
    if(s=="BEND") return IfcPipeFittingTypeEnum::IfcPipeFittingType_BEND;
    if(s=="CONNECTOR") return IfcPipeFittingTypeEnum::IfcPipeFittingType_CONNECTOR;
    if(s=="ENTRY") return IfcPipeFittingTypeEnum::IfcPipeFittingType_ENTRY;
    if(s=="EXIT") return IfcPipeFittingTypeEnum::IfcPipeFittingType_EXIT;
    if(s=="JUNCTION") return IfcPipeFittingTypeEnum::IfcPipeFittingType_JUNCTION;
    if(s=="OBSTRUCTION") return IfcPipeFittingTypeEnum::IfcPipeFittingType_OBSTRUCTION;
    if(s=="TRANSITION") return IfcPipeFittingTypeEnum::IfcPipeFittingType_TRANSITION;
    if(s=="USERDEFINED") return IfcPipeFittingTypeEnum::IfcPipeFittingType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcPipeFittingTypeEnum::IfcPipeFittingType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPipeSegmentTypeEnum::ToString(IfcPipeSegmentTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FLEXIBLESEGMENT","RIGIDSEGMENT","GUTTER","SPOOL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPipeSegmentTypeEnum::IfcPipeSegmentTypeEnum IfcPipeSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="FLEXIBLESEGMENT") return IfcPipeSegmentTypeEnum::IfcPipeSegmentType_FLEXIBLESEGMENT;
    if(s=="RIGIDSEGMENT") return IfcPipeSegmentTypeEnum::IfcPipeSegmentType_RIGIDSEGMENT;
    if(s=="GUTTER") return IfcPipeSegmentTypeEnum::IfcPipeSegmentType_GUTTER;
    if(s=="SPOOL") return IfcPipeSegmentTypeEnum::IfcPipeSegmentType_SPOOL;
    if(s=="USERDEFINED") return IfcPipeSegmentTypeEnum::IfcPipeSegmentType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcPipeSegmentTypeEnum::IfcPipeSegmentType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPlateTypeEnum::ToString(IfcPlateTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CURTAIN_PANEL","SHEET","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPlateTypeEnum::IfcPlateTypeEnum IfcPlateTypeEnum::FromString(const std::string& s) {
    if(s=="CURTAIN_PANEL") return IfcPlateTypeEnum::IfcPlateType_CURTAIN_PANEL;
    if(s=="SHEET") return IfcPlateTypeEnum::IfcPlateType_SHEET;
    if(s=="USERDEFINED") return IfcPlateTypeEnum::IfcPlateType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcPlateTypeEnum::IfcPlateType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcProcedureTypeEnum::ToString(IfcProcedureTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ADVICE_CAUTION","ADVICE_NOTE","ADVICE_WARNING","CALIBRATION","DIAGNOSTIC","SHUTDOWN","STARTUP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProcedureTypeEnum::IfcProcedureTypeEnum IfcProcedureTypeEnum::FromString(const std::string& s) {
    if(s=="ADVICE_CAUTION") return IfcProcedureTypeEnum::IfcProcedureType_ADVICE_CAUTION;
    if(s=="ADVICE_NOTE") return IfcProcedureTypeEnum::IfcProcedureType_ADVICE_NOTE;
    if(s=="ADVICE_WARNING") return IfcProcedureTypeEnum::IfcProcedureType_ADVICE_WARNING;
    if(s=="CALIBRATION") return IfcProcedureTypeEnum::IfcProcedureType_CALIBRATION;
    if(s=="DIAGNOSTIC") return IfcProcedureTypeEnum::IfcProcedureType_DIAGNOSTIC;
    if(s=="SHUTDOWN") return IfcProcedureTypeEnum::IfcProcedureType_SHUTDOWN;
    if(s=="STARTUP") return IfcProcedureTypeEnum::IfcProcedureType_STARTUP;
    if(s=="USERDEFINED") return IfcProcedureTypeEnum::IfcProcedureType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcProcedureTypeEnum::IfcProcedureType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcProfileTypeEnum::ToString(IfcProfileTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CURVE","AREA" };
    return names[v];
}
IfcProfileTypeEnum::IfcProfileTypeEnum IfcProfileTypeEnum::FromString(const std::string& s) {
    if(s=="CURVE") return IfcProfileTypeEnum::IfcProfileType_CURVE;
    if(s=="AREA") return IfcProfileTypeEnum::IfcProfileType_AREA;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcProjectOrderRecordTypeEnum::ToString(IfcProjectOrderRecordTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CHANGE","MAINTENANCE","MOVE","PURCHASE","WORK","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordTypeEnum IfcProjectOrderRecordTypeEnum::FromString(const std::string& s) {
    if(s=="CHANGE") return IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordType_CHANGE;
    if(s=="MAINTENANCE") return IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordType_MAINTENANCE;
    if(s=="MOVE") return IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordType_MOVE;
    if(s=="PURCHASE") return IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordType_PURCHASE;
    if(s=="WORK") return IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordType_WORK;
    if(s=="USERDEFINED") return IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcProjectOrderTypeEnum::ToString(IfcProjectOrderTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CHANGEORDER","MAINTENANCEWORKORDER","MOVEORDER","PURCHASEORDER","WORKORDER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProjectOrderTypeEnum::IfcProjectOrderTypeEnum IfcProjectOrderTypeEnum::FromString(const std::string& s) {
    if(s=="CHANGEORDER") return IfcProjectOrderTypeEnum::IfcProjectOrderType_CHANGEORDER;
    if(s=="MAINTENANCEWORKORDER") return IfcProjectOrderTypeEnum::IfcProjectOrderType_MAINTENANCEWORKORDER;
    if(s=="MOVEORDER") return IfcProjectOrderTypeEnum::IfcProjectOrderType_MOVEORDER;
    if(s=="PURCHASEORDER") return IfcProjectOrderTypeEnum::IfcProjectOrderType_PURCHASEORDER;
    if(s=="WORKORDER") return IfcProjectOrderTypeEnum::IfcProjectOrderType_WORKORDER;
    if(s=="USERDEFINED") return IfcProjectOrderTypeEnum::IfcProjectOrderType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcProjectOrderTypeEnum::IfcProjectOrderType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcProjectedOrTrueLengthEnum::ToString(IfcProjectedOrTrueLengthEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PROJECTED_LENGTH","TRUE_LENGTH" };
    return names[v];
}
IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum IfcProjectedOrTrueLengthEnum::FromString(const std::string& s) {
    if(s=="PROJECTED_LENGTH") return IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLength_PROJECTED_LENGTH;
    if(s=="TRUE_LENGTH") return IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLength_TRUE_LENGTH;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPropertySourceEnum::ToString(IfcPropertySourceEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DESIGN","DESIGNMAXIMUM","DESIGNMINIMUM","SIMULATED","ASBUILT","COMMISSIONING","MEASURED","USERDEFINED","NOTKNOWN" };
    return names[v];
}
IfcPropertySourceEnum::IfcPropertySourceEnum IfcPropertySourceEnum::FromString(const std::string& s) {
    if(s=="DESIGN") return IfcPropertySourceEnum::IfcPropertySource_DESIGN;
    if(s=="DESIGNMAXIMUM") return IfcPropertySourceEnum::IfcPropertySource_DESIGNMAXIMUM;
    if(s=="DESIGNMINIMUM") return IfcPropertySourceEnum::IfcPropertySource_DESIGNMINIMUM;
    if(s=="SIMULATED") return IfcPropertySourceEnum::IfcPropertySource_SIMULATED;
    if(s=="ASBUILT") return IfcPropertySourceEnum::IfcPropertySource_ASBUILT;
    if(s=="COMMISSIONING") return IfcPropertySourceEnum::IfcPropertySource_COMMISSIONING;
    if(s=="MEASURED") return IfcPropertySourceEnum::IfcPropertySource_MEASURED;
    if(s=="USERDEFINED") return IfcPropertySourceEnum::IfcPropertySource_USERDEFINED;
    if(s=="NOTKNOWN") return IfcPropertySourceEnum::IfcPropertySource_NOTKNOWN;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcProtectiveDeviceTypeEnum::ToString(IfcProtectiveDeviceTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FUSEDISCONNECTOR","CIRCUITBREAKER","EARTHFAILUREDEVICE","RESIDUALCURRENTCIRCUITBREAKER","RESIDUALCURRENTSWITCH","VARISTOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceTypeEnum IfcProtectiveDeviceTypeEnum::FromString(const std::string& s) {
    if(s=="FUSEDISCONNECTOR") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_FUSEDISCONNECTOR;
    if(s=="CIRCUITBREAKER") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_CIRCUITBREAKER;
    if(s=="EARTHFAILUREDEVICE") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_EARTHFAILUREDEVICE;
    if(s=="RESIDUALCURRENTCIRCUITBREAKER") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_RESIDUALCURRENTCIRCUITBREAKER;
    if(s=="RESIDUALCURRENTSWITCH") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_RESIDUALCURRENTSWITCH;
    if(s=="VARISTOR") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_VARISTOR;
    if(s=="USERDEFINED") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcPumpTypeEnum::ToString(IfcPumpTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CIRCULATOR","ENDSUCTION","SPLITCASE","VERTICALINLINE","VERTICALTURBINE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPumpTypeEnum::IfcPumpTypeEnum IfcPumpTypeEnum::FromString(const std::string& s) {
    if(s=="CIRCULATOR") return IfcPumpTypeEnum::IfcPumpType_CIRCULATOR;
    if(s=="ENDSUCTION") return IfcPumpTypeEnum::IfcPumpType_ENDSUCTION;
    if(s=="SPLITCASE") return IfcPumpTypeEnum::IfcPumpType_SPLITCASE;
    if(s=="VERTICALINLINE") return IfcPumpTypeEnum::IfcPumpType_VERTICALINLINE;
    if(s=="VERTICALTURBINE") return IfcPumpTypeEnum::IfcPumpType_VERTICALTURBINE;
    if(s=="USERDEFINED") return IfcPumpTypeEnum::IfcPumpType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcPumpTypeEnum::IfcPumpType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcRailingTypeEnum::ToString(IfcRailingTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "HANDRAIL","GUARDRAIL","BALUSTRADE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcRailingTypeEnum::IfcRailingTypeEnum IfcRailingTypeEnum::FromString(const std::string& s) {
    if(s=="HANDRAIL") return IfcRailingTypeEnum::IfcRailingType_HANDRAIL;
    if(s=="GUARDRAIL") return IfcRailingTypeEnum::IfcRailingType_GUARDRAIL;
    if(s=="BALUSTRADE") return IfcRailingTypeEnum::IfcRailingType_BALUSTRADE;
    if(s=="USERDEFINED") return IfcRailingTypeEnum::IfcRailingType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcRailingTypeEnum::IfcRailingType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcRampFlightTypeEnum::ToString(IfcRampFlightTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "STRAIGHT","SPIRAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcRampFlightTypeEnum::IfcRampFlightTypeEnum IfcRampFlightTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT") return IfcRampFlightTypeEnum::IfcRampFlightType_STRAIGHT;
    if(s=="SPIRAL") return IfcRampFlightTypeEnum::IfcRampFlightType_SPIRAL;
    if(s=="USERDEFINED") return IfcRampFlightTypeEnum::IfcRampFlightType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcRampFlightTypeEnum::IfcRampFlightType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcRampTypeEnum::ToString(IfcRampTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "STRAIGHT_RUN_RAMP","TWO_STRAIGHT_RUN_RAMP","QUARTER_TURN_RAMP","TWO_QUARTER_TURN_RAMP","HALF_TURN_RAMP","SPIRAL_RAMP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcRampTypeEnum::IfcRampTypeEnum IfcRampTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT_RUN_RAMP") return IfcRampTypeEnum::IfcRampType_STRAIGHT_RUN_RAMP;
    if(s=="TWO_STRAIGHT_RUN_RAMP") return IfcRampTypeEnum::IfcRampType_TWO_STRAIGHT_RUN_RAMP;
    if(s=="QUARTER_TURN_RAMP") return IfcRampTypeEnum::IfcRampType_QUARTER_TURN_RAMP;
    if(s=="TWO_QUARTER_TURN_RAMP") return IfcRampTypeEnum::IfcRampType_TWO_QUARTER_TURN_RAMP;
    if(s=="HALF_TURN_RAMP") return IfcRampTypeEnum::IfcRampType_HALF_TURN_RAMP;
    if(s=="SPIRAL_RAMP") return IfcRampTypeEnum::IfcRampType_SPIRAL_RAMP;
    if(s=="USERDEFINED") return IfcRampTypeEnum::IfcRampType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcRampTypeEnum::IfcRampType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcReflectanceMethodEnum::ToString(IfcReflectanceMethodEnum v) {
    if ( v < 0 || v >= 10 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BLINN","FLAT","GLASS","MATT","METAL","MIRROR","PHONG","PLASTIC","STRAUSS","NOTDEFINED" };
    return names[v];
}
IfcReflectanceMethodEnum::IfcReflectanceMethodEnum IfcReflectanceMethodEnum::FromString(const std::string& s) {
    if(s=="BLINN") return IfcReflectanceMethodEnum::IfcReflectanceMethod_BLINN;
    if(s=="FLAT") return IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT;
    if(s=="GLASS") return IfcReflectanceMethodEnum::IfcReflectanceMethod_GLASS;
    if(s=="MATT") return IfcReflectanceMethodEnum::IfcReflectanceMethod_MATT;
    if(s=="METAL") return IfcReflectanceMethodEnum::IfcReflectanceMethod_METAL;
    if(s=="MIRROR") return IfcReflectanceMethodEnum::IfcReflectanceMethod_MIRROR;
    if(s=="PHONG") return IfcReflectanceMethodEnum::IfcReflectanceMethod_PHONG;
    if(s=="PLASTIC") return IfcReflectanceMethodEnum::IfcReflectanceMethod_PLASTIC;
    if(s=="STRAUSS") return IfcReflectanceMethodEnum::IfcReflectanceMethod_STRAUSS;
    if(s=="NOTDEFINED") return IfcReflectanceMethodEnum::IfcReflectanceMethod_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcReinforcingBarRoleEnum::ToString(IfcReinforcingBarRoleEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "MAIN","SHEAR","LIGATURE","STUD","PUNCHING","EDGE","RING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum IfcReinforcingBarRoleEnum::FromString(const std::string& s) {
    if(s=="MAIN") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_MAIN;
    if(s=="SHEAR") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_SHEAR;
    if(s=="LIGATURE") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_LIGATURE;
    if(s=="STUD") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_STUD;
    if(s=="PUNCHING") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_PUNCHING;
    if(s=="EDGE") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_EDGE;
    if(s=="RING") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_RING;
    if(s=="USERDEFINED") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_USERDEFINED;
    if(s=="NOTDEFINED") return IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcReinforcingBarSurfaceEnum::ToString(IfcReinforcingBarSurfaceEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PLAIN","TEXTURED" };
    return names[v];
}
IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum IfcReinforcingBarSurfaceEnum::FromString(const std::string& s) {
    if(s=="PLAIN") return IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurface_PLAIN;
    if(s=="TEXTURED") return IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurface_TEXTURED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcResourceConsumptionEnum::ToString(IfcResourceConsumptionEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CONSUMED","PARTIALLYCONSUMED","NOTCONSUMED","OCCUPIED","PARTIALLYOCCUPIED","NOTOCCUPIED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcResourceConsumptionEnum::IfcResourceConsumptionEnum IfcResourceConsumptionEnum::FromString(const std::string& s) {
    if(s=="CONSUMED") return IfcResourceConsumptionEnum::IfcResourceConsumption_CONSUMED;
    if(s=="PARTIALLYCONSUMED") return IfcResourceConsumptionEnum::IfcResourceConsumption_PARTIALLYCONSUMED;
    if(s=="NOTCONSUMED") return IfcResourceConsumptionEnum::IfcResourceConsumption_NOTCONSUMED;
    if(s=="OCCUPIED") return IfcResourceConsumptionEnum::IfcResourceConsumption_OCCUPIED;
    if(s=="PARTIALLYOCCUPIED") return IfcResourceConsumptionEnum::IfcResourceConsumption_PARTIALLYOCCUPIED;
    if(s=="NOTOCCUPIED") return IfcResourceConsumptionEnum::IfcResourceConsumption_NOTOCCUPIED;
    if(s=="USERDEFINED") return IfcResourceConsumptionEnum::IfcResourceConsumption_USERDEFINED;
    if(s=="NOTDEFINED") return IfcResourceConsumptionEnum::IfcResourceConsumption_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcRibPlateDirectionEnum::ToString(IfcRibPlateDirectionEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DIRECTION_X","DIRECTION_Y" };
    return names[v];
}
IfcRibPlateDirectionEnum::IfcRibPlateDirectionEnum IfcRibPlateDirectionEnum::FromString(const std::string& s) {
    if(s=="DIRECTION_X") return IfcRibPlateDirectionEnum::IfcRibPlateDirection_DIRECTION_X;
    if(s=="DIRECTION_Y") return IfcRibPlateDirectionEnum::IfcRibPlateDirection_DIRECTION_Y;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcRoleEnum::ToString(IfcRoleEnum v) {
    if ( v < 0 || v >= 23 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SUPPLIER","MANUFACTURER","CONTRACTOR","SUBCONTRACTOR","ARCHITECT","STRUCTURALENGINEER","COSTENGINEER","CLIENT","BUILDINGOWNER","BUILDINGOPERATOR","MECHANICALENGINEER","ELECTRICALENGINEER","PROJECTMANAGER","FACILITIESMANAGER","CIVILENGINEER","COMISSIONINGENGINEER","ENGINEER","OWNER","CONSULTANT","CONSTRUCTIONMANAGER","FIELDCONSTRUCTIONMANAGER","RESELLER","USERDEFINED" };
    return names[v];
}
IfcRoleEnum::IfcRoleEnum IfcRoleEnum::FromString(const std::string& s) {
    if(s=="SUPPLIER") return IfcRoleEnum::IfcRole_SUPPLIER;
    if(s=="MANUFACTURER") return IfcRoleEnum::IfcRole_MANUFACTURER;
    if(s=="CONTRACTOR") return IfcRoleEnum::IfcRole_CONTRACTOR;
    if(s=="SUBCONTRACTOR") return IfcRoleEnum::IfcRole_SUBCONTRACTOR;
    if(s=="ARCHITECT") return IfcRoleEnum::IfcRole_ARCHITECT;
    if(s=="STRUCTURALENGINEER") return IfcRoleEnum::IfcRole_STRUCTURALENGINEER;
    if(s=="COSTENGINEER") return IfcRoleEnum::IfcRole_COSTENGINEER;
    if(s=="CLIENT") return IfcRoleEnum::IfcRole_CLIENT;
    if(s=="BUILDINGOWNER") return IfcRoleEnum::IfcRole_BUILDINGOWNER;
    if(s=="BUILDINGOPERATOR") return IfcRoleEnum::IfcRole_BUILDINGOPERATOR;
    if(s=="MECHANICALENGINEER") return IfcRoleEnum::IfcRole_MECHANICALENGINEER;
    if(s=="ELECTRICALENGINEER") return IfcRoleEnum::IfcRole_ELECTRICALENGINEER;
    if(s=="PROJECTMANAGER") return IfcRoleEnum::IfcRole_PROJECTMANAGER;
    if(s=="FACILITIESMANAGER") return IfcRoleEnum::IfcRole_FACILITIESMANAGER;
    if(s=="CIVILENGINEER") return IfcRoleEnum::IfcRole_CIVILENGINEER;
    if(s=="COMISSIONINGENGINEER") return IfcRoleEnum::IfcRole_COMISSIONINGENGINEER;
    if(s=="ENGINEER") return IfcRoleEnum::IfcRole_ENGINEER;
    if(s=="OWNER") return IfcRoleEnum::IfcRole_OWNER;
    if(s=="CONSULTANT") return IfcRoleEnum::IfcRole_CONSULTANT;
    if(s=="CONSTRUCTIONMANAGER") return IfcRoleEnum::IfcRole_CONSTRUCTIONMANAGER;
    if(s=="FIELDCONSTRUCTIONMANAGER") return IfcRoleEnum::IfcRole_FIELDCONSTRUCTIONMANAGER;
    if(s=="RESELLER") return IfcRoleEnum::IfcRole_RESELLER;
    if(s=="USERDEFINED") return IfcRoleEnum::IfcRole_USERDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcRoofTypeEnum::ToString(IfcRoofTypeEnum v) {
    if ( v < 0 || v >= 14 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FLAT_ROOF","SHED_ROOF","GABLE_ROOF","HIP_ROOF","HIPPED_GABLE_ROOF","GAMBREL_ROOF","MANSARD_ROOF","BARREL_ROOF","RAINBOW_ROOF","BUTTERFLY_ROOF","PAVILION_ROOF","DOME_ROOF","FREEFORM","NOTDEFINED" };
    return names[v];
}
IfcRoofTypeEnum::IfcRoofTypeEnum IfcRoofTypeEnum::FromString(const std::string& s) {
    if(s=="FLAT_ROOF") return IfcRoofTypeEnum::IfcRoofType_FLAT_ROOF;
    if(s=="SHED_ROOF") return IfcRoofTypeEnum::IfcRoofType_SHED_ROOF;
    if(s=="GABLE_ROOF") return IfcRoofTypeEnum::IfcRoofType_GABLE_ROOF;
    if(s=="HIP_ROOF") return IfcRoofTypeEnum::IfcRoofType_HIP_ROOF;
    if(s=="HIPPED_GABLE_ROOF") return IfcRoofTypeEnum::IfcRoofType_HIPPED_GABLE_ROOF;
    if(s=="GAMBREL_ROOF") return IfcRoofTypeEnum::IfcRoofType_GAMBREL_ROOF;
    if(s=="MANSARD_ROOF") return IfcRoofTypeEnum::IfcRoofType_MANSARD_ROOF;
    if(s=="BARREL_ROOF") return IfcRoofTypeEnum::IfcRoofType_BARREL_ROOF;
    if(s=="RAINBOW_ROOF") return IfcRoofTypeEnum::IfcRoofType_RAINBOW_ROOF;
    if(s=="BUTTERFLY_ROOF") return IfcRoofTypeEnum::IfcRoofType_BUTTERFLY_ROOF;
    if(s=="PAVILION_ROOF") return IfcRoofTypeEnum::IfcRoofType_PAVILION_ROOF;
    if(s=="DOME_ROOF") return IfcRoofTypeEnum::IfcRoofType_DOME_ROOF;
    if(s=="FREEFORM") return IfcRoofTypeEnum::IfcRoofType_FREEFORM;
    if(s=="NOTDEFINED") return IfcRoofTypeEnum::IfcRoofType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSIPrefix::ToString(IfcSIPrefix v) {
    if ( v < 0 || v >= 16 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "EXA","PETA","TERA","GIGA","MEGA","KILO","HECTO","DECA","DECI","CENTI","MILLI","MICRO","NANO","PICO","FEMTO","ATTO" };
    return names[v];
}
IfcSIPrefix::IfcSIPrefix IfcSIPrefix::FromString(const std::string& s) {
    if(s=="EXA") return IfcSIPrefix::IfcSIPrefix_EXA;
    if(s=="PETA") return IfcSIPrefix::IfcSIPrefix_PETA;
    if(s=="TERA") return IfcSIPrefix::IfcSIPrefix_TERA;
    if(s=="GIGA") return IfcSIPrefix::IfcSIPrefix_GIGA;
    if(s=="MEGA") return IfcSIPrefix::IfcSIPrefix_MEGA;
    if(s=="KILO") return IfcSIPrefix::IfcSIPrefix_KILO;
    if(s=="HECTO") return IfcSIPrefix::IfcSIPrefix_HECTO;
    if(s=="DECA") return IfcSIPrefix::IfcSIPrefix_DECA;
    if(s=="DECI") return IfcSIPrefix::IfcSIPrefix_DECI;
    if(s=="CENTI") return IfcSIPrefix::IfcSIPrefix_CENTI;
    if(s=="MILLI") return IfcSIPrefix::IfcSIPrefix_MILLI;
    if(s=="MICRO") return IfcSIPrefix::IfcSIPrefix_MICRO;
    if(s=="NANO") return IfcSIPrefix::IfcSIPrefix_NANO;
    if(s=="PICO") return IfcSIPrefix::IfcSIPrefix_PICO;
    if(s=="FEMTO") return IfcSIPrefix::IfcSIPrefix_FEMTO;
    if(s=="ATTO") return IfcSIPrefix::IfcSIPrefix_ATTO;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSIUnitName::ToString(IfcSIUnitName v) {
    if ( v < 0 || v >= 30 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AMPERE","BECQUEREL","CANDELA","COULOMB","CUBIC_METRE","DEGREE_CELSIUS","FARAD","GRAM","GRAY","HENRY","HERTZ","JOULE","KELVIN","LUMEN","LUX","METRE","MOLE","NEWTON","OHM","PASCAL","RADIAN","SECOND","SIEMENS","SIEVERT","SQUARE_METRE","STERADIAN","TESLA","VOLT","WATT","WEBER" };
    return names[v];
}
IfcSIUnitName::IfcSIUnitName IfcSIUnitName::FromString(const std::string& s) {
    if(s=="AMPERE") return IfcSIUnitName::IfcSIUnitName_AMPERE;
    if(s=="BECQUEREL") return IfcSIUnitName::IfcSIUnitName_BECQUEREL;
    if(s=="CANDELA") return IfcSIUnitName::IfcSIUnitName_CANDELA;
    if(s=="COULOMB") return IfcSIUnitName::IfcSIUnitName_COULOMB;
    if(s=="CUBIC_METRE") return IfcSIUnitName::IfcSIUnitName_CUBIC_METRE;
    if(s=="DEGREE_CELSIUS") return IfcSIUnitName::IfcSIUnitName_DEGREE_CELSIUS;
    if(s=="FARAD") return IfcSIUnitName::IfcSIUnitName_FARAD;
    if(s=="GRAM") return IfcSIUnitName::IfcSIUnitName_GRAM;
    if(s=="GRAY") return IfcSIUnitName::IfcSIUnitName_GRAY;
    if(s=="HENRY") return IfcSIUnitName::IfcSIUnitName_HENRY;
    if(s=="HERTZ") return IfcSIUnitName::IfcSIUnitName_HERTZ;
    if(s=="JOULE") return IfcSIUnitName::IfcSIUnitName_JOULE;
    if(s=="KELVIN") return IfcSIUnitName::IfcSIUnitName_KELVIN;
    if(s=="LUMEN") return IfcSIUnitName::IfcSIUnitName_LUMEN;
    if(s=="LUX") return IfcSIUnitName::IfcSIUnitName_LUX;
    if(s=="METRE") return IfcSIUnitName::IfcSIUnitName_METRE;
    if(s=="MOLE") return IfcSIUnitName::IfcSIUnitName_MOLE;
    if(s=="NEWTON") return IfcSIUnitName::IfcSIUnitName_NEWTON;
    if(s=="OHM") return IfcSIUnitName::IfcSIUnitName_OHM;
    if(s=="PASCAL") return IfcSIUnitName::IfcSIUnitName_PASCAL;
    if(s=="RADIAN") return IfcSIUnitName::IfcSIUnitName_RADIAN;
    if(s=="SECOND") return IfcSIUnitName::IfcSIUnitName_SECOND;
    if(s=="SIEMENS") return IfcSIUnitName::IfcSIUnitName_SIEMENS;
    if(s=="SIEVERT") return IfcSIUnitName::IfcSIUnitName_SIEVERT;
    if(s=="SQUARE_METRE") return IfcSIUnitName::IfcSIUnitName_SQUARE_METRE;
    if(s=="STERADIAN") return IfcSIUnitName::IfcSIUnitName_STERADIAN;
    if(s=="TESLA") return IfcSIUnitName::IfcSIUnitName_TESLA;
    if(s=="VOLT") return IfcSIUnitName::IfcSIUnitName_VOLT;
    if(s=="WATT") return IfcSIUnitName::IfcSIUnitName_WATT;
    if(s=="WEBER") return IfcSIUnitName::IfcSIUnitName_WEBER;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSanitaryTerminalTypeEnum::ToString(IfcSanitaryTerminalTypeEnum v) {
    if ( v < 0 || v >= 12 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BATH","BIDET","CISTERN","SHOWER","SINK","SANITARYFOUNTAIN","TOILETPAN","URINAL","WASHHANDBASIN","WCSEAT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalTypeEnum IfcSanitaryTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="BATH") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_BATH;
    if(s=="BIDET") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_BIDET;
    if(s=="CISTERN") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_CISTERN;
    if(s=="SHOWER") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_SHOWER;
    if(s=="SINK") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_SINK;
    if(s=="SANITARYFOUNTAIN") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_SANITARYFOUNTAIN;
    if(s=="TOILETPAN") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_TOILETPAN;
    if(s=="URINAL") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_URINAL;
    if(s=="WASHHANDBASIN") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_WASHHANDBASIN;
    if(s=="WCSEAT") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_WCSEAT;
    if(s=="USERDEFINED") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSectionTypeEnum::ToString(IfcSectionTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "UNIFORM","TAPERED" };
    return names[v];
}
IfcSectionTypeEnum::IfcSectionTypeEnum IfcSectionTypeEnum::FromString(const std::string& s) {
    if(s=="UNIFORM") return IfcSectionTypeEnum::IfcSectionType_UNIFORM;
    if(s=="TAPERED") return IfcSectionTypeEnum::IfcSectionType_TAPERED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSensorTypeEnum::ToString(IfcSensorTypeEnum v) {
    if ( v < 0 || v >= 15 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CO2SENSOR","FIRESENSOR","FLOWSENSOR","GASSENSOR","HEATSENSOR","HUMIDITYSENSOR","LIGHTSENSOR","MOISTURESENSOR","MOVEMENTSENSOR","PRESSURESENSOR","SMOKESENSOR","SOUNDSENSOR","TEMPERATURESENSOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSensorTypeEnum::IfcSensorTypeEnum IfcSensorTypeEnum::FromString(const std::string& s) {
    if(s=="CO2SENSOR") return IfcSensorTypeEnum::IfcSensorType_CO2SENSOR;
    if(s=="FIRESENSOR") return IfcSensorTypeEnum::IfcSensorType_FIRESENSOR;
    if(s=="FLOWSENSOR") return IfcSensorTypeEnum::IfcSensorType_FLOWSENSOR;
    if(s=="GASSENSOR") return IfcSensorTypeEnum::IfcSensorType_GASSENSOR;
    if(s=="HEATSENSOR") return IfcSensorTypeEnum::IfcSensorType_HEATSENSOR;
    if(s=="HUMIDITYSENSOR") return IfcSensorTypeEnum::IfcSensorType_HUMIDITYSENSOR;
    if(s=="LIGHTSENSOR") return IfcSensorTypeEnum::IfcSensorType_LIGHTSENSOR;
    if(s=="MOISTURESENSOR") return IfcSensorTypeEnum::IfcSensorType_MOISTURESENSOR;
    if(s=="MOVEMENTSENSOR") return IfcSensorTypeEnum::IfcSensorType_MOVEMENTSENSOR;
    if(s=="PRESSURESENSOR") return IfcSensorTypeEnum::IfcSensorType_PRESSURESENSOR;
    if(s=="SMOKESENSOR") return IfcSensorTypeEnum::IfcSensorType_SMOKESENSOR;
    if(s=="SOUNDSENSOR") return IfcSensorTypeEnum::IfcSensorType_SOUNDSENSOR;
    if(s=="TEMPERATURESENSOR") return IfcSensorTypeEnum::IfcSensorType_TEMPERATURESENSOR;
    if(s=="USERDEFINED") return IfcSensorTypeEnum::IfcSensorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcSensorTypeEnum::IfcSensorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSequenceEnum::ToString(IfcSequenceEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "START_START","START_FINISH","FINISH_START","FINISH_FINISH","NOTDEFINED" };
    return names[v];
}
IfcSequenceEnum::IfcSequenceEnum IfcSequenceEnum::FromString(const std::string& s) {
    if(s=="START_START") return IfcSequenceEnum::IfcSequence_START_START;
    if(s=="START_FINISH") return IfcSequenceEnum::IfcSequence_START_FINISH;
    if(s=="FINISH_START") return IfcSequenceEnum::IfcSequence_FINISH_START;
    if(s=="FINISH_FINISH") return IfcSequenceEnum::IfcSequence_FINISH_FINISH;
    if(s=="NOTDEFINED") return IfcSequenceEnum::IfcSequence_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcServiceLifeFactorTypeEnum::ToString(IfcServiceLifeFactorTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "A_QUALITYOFCOMPONENTS","B_DESIGNLEVEL","C_WORKEXECUTIONLEVEL","D_INDOORENVIRONMENT","E_OUTDOORENVIRONMENT","F_INUSECONDITIONS","G_MAINTENANCELEVEL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorTypeEnum IfcServiceLifeFactorTypeEnum::FromString(const std::string& s) {
    if(s=="A_QUALITYOFCOMPONENTS") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_A_QUALITYOFCOMPONENTS;
    if(s=="B_DESIGNLEVEL") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_B_DESIGNLEVEL;
    if(s=="C_WORKEXECUTIONLEVEL") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_C_WORKEXECUTIONLEVEL;
    if(s=="D_INDOORENVIRONMENT") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_D_INDOORENVIRONMENT;
    if(s=="E_OUTDOORENVIRONMENT") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_E_OUTDOORENVIRONMENT;
    if(s=="F_INUSECONDITIONS") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_F_INUSECONDITIONS;
    if(s=="G_MAINTENANCELEVEL") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_G_MAINTENANCELEVEL;
    if(s=="USERDEFINED") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcServiceLifeTypeEnum::ToString(IfcServiceLifeTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ACTUALSERVICELIFE","EXPECTEDSERVICELIFE","OPTIMISTICREFERENCESERVICELIFE","PESSIMISTICREFERENCESERVICELIFE","REFERENCESERVICELIFE" };
    return names[v];
}
IfcServiceLifeTypeEnum::IfcServiceLifeTypeEnum IfcServiceLifeTypeEnum::FromString(const std::string& s) {
    if(s=="ACTUALSERVICELIFE") return IfcServiceLifeTypeEnum::IfcServiceLifeType_ACTUALSERVICELIFE;
    if(s=="EXPECTEDSERVICELIFE") return IfcServiceLifeTypeEnum::IfcServiceLifeType_EXPECTEDSERVICELIFE;
    if(s=="OPTIMISTICREFERENCESERVICELIFE") return IfcServiceLifeTypeEnum::IfcServiceLifeType_OPTIMISTICREFERENCESERVICELIFE;
    if(s=="PESSIMISTICREFERENCESERVICELIFE") return IfcServiceLifeTypeEnum::IfcServiceLifeType_PESSIMISTICREFERENCESERVICELIFE;
    if(s=="REFERENCESERVICELIFE") return IfcServiceLifeTypeEnum::IfcServiceLifeType_REFERENCESERVICELIFE;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSlabTypeEnum::ToString(IfcSlabTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FLOOR","ROOF","LANDING","BASESLAB","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSlabTypeEnum::IfcSlabTypeEnum IfcSlabTypeEnum::FromString(const std::string& s) {
    if(s=="FLOOR") return IfcSlabTypeEnum::IfcSlabType_FLOOR;
    if(s=="ROOF") return IfcSlabTypeEnum::IfcSlabType_ROOF;
    if(s=="LANDING") return IfcSlabTypeEnum::IfcSlabType_LANDING;
    if(s=="BASESLAB") return IfcSlabTypeEnum::IfcSlabType_BASESLAB;
    if(s=="USERDEFINED") return IfcSlabTypeEnum::IfcSlabType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcSlabTypeEnum::IfcSlabType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSoundScaleEnum::ToString(IfcSoundScaleEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DBA","DBB","DBC","NC","NR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSoundScaleEnum::IfcSoundScaleEnum IfcSoundScaleEnum::FromString(const std::string& s) {
    if(s=="DBA") return IfcSoundScaleEnum::IfcSoundScale_DBA;
    if(s=="DBB") return IfcSoundScaleEnum::IfcSoundScale_DBB;
    if(s=="DBC") return IfcSoundScaleEnum::IfcSoundScale_DBC;
    if(s=="NC") return IfcSoundScaleEnum::IfcSoundScale_NC;
    if(s=="NR") return IfcSoundScaleEnum::IfcSoundScale_NR;
    if(s=="USERDEFINED") return IfcSoundScaleEnum::IfcSoundScale_USERDEFINED;
    if(s=="NOTDEFINED") return IfcSoundScaleEnum::IfcSoundScale_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSpaceHeaterTypeEnum::ToString(IfcSpaceHeaterTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SECTIONALRADIATOR","PANELRADIATOR","TUBULARRADIATOR","CONVECTOR","BASEBOARDHEATER","FINNEDTUBEUNIT","UNITHEATER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSpaceHeaterTypeEnum::IfcSpaceHeaterTypeEnum IfcSpaceHeaterTypeEnum::FromString(const std::string& s) {
    if(s=="SECTIONALRADIATOR") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_SECTIONALRADIATOR;
    if(s=="PANELRADIATOR") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_PANELRADIATOR;
    if(s=="TUBULARRADIATOR") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_TUBULARRADIATOR;
    if(s=="CONVECTOR") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_CONVECTOR;
    if(s=="BASEBOARDHEATER") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_BASEBOARDHEATER;
    if(s=="FINNEDTUBEUNIT") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_FINNEDTUBEUNIT;
    if(s=="UNITHEATER") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_UNITHEATER;
    if(s=="USERDEFINED") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcSpaceHeaterTypeEnum::IfcSpaceHeaterType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSpaceTypeEnum::ToString(IfcSpaceTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSpaceTypeEnum::IfcSpaceTypeEnum IfcSpaceTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcSpaceTypeEnum::IfcSpaceType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcSpaceTypeEnum::IfcSpaceType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcStackTerminalTypeEnum::ToString(IfcStackTerminalTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BIRDCAGE","COWL","RAINWATERHOPPER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStackTerminalTypeEnum::IfcStackTerminalTypeEnum IfcStackTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="BIRDCAGE") return IfcStackTerminalTypeEnum::IfcStackTerminalType_BIRDCAGE;
    if(s=="COWL") return IfcStackTerminalTypeEnum::IfcStackTerminalType_COWL;
    if(s=="RAINWATERHOPPER") return IfcStackTerminalTypeEnum::IfcStackTerminalType_RAINWATERHOPPER;
    if(s=="USERDEFINED") return IfcStackTerminalTypeEnum::IfcStackTerminalType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcStackTerminalTypeEnum::IfcStackTerminalType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcStairFlightTypeEnum::ToString(IfcStairFlightTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "STRAIGHT","WINDER","SPIRAL","CURVED","FREEFORM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStairFlightTypeEnum::IfcStairFlightTypeEnum IfcStairFlightTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT") return IfcStairFlightTypeEnum::IfcStairFlightType_STRAIGHT;
    if(s=="WINDER") return IfcStairFlightTypeEnum::IfcStairFlightType_WINDER;
    if(s=="SPIRAL") return IfcStairFlightTypeEnum::IfcStairFlightType_SPIRAL;
    if(s=="CURVED") return IfcStairFlightTypeEnum::IfcStairFlightType_CURVED;
    if(s=="FREEFORM") return IfcStairFlightTypeEnum::IfcStairFlightType_FREEFORM;
    if(s=="USERDEFINED") return IfcStairFlightTypeEnum::IfcStairFlightType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcStairFlightTypeEnum::IfcStairFlightType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcStairTypeEnum::ToString(IfcStairTypeEnum v) {
    if ( v < 0 || v >= 16 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "STRAIGHT_RUN_STAIR","TWO_STRAIGHT_RUN_STAIR","QUARTER_WINDING_STAIR","QUARTER_TURN_STAIR","HALF_WINDING_STAIR","HALF_TURN_STAIR","TWO_QUARTER_WINDING_STAIR","TWO_QUARTER_TURN_STAIR","THREE_QUARTER_WINDING_STAIR","THREE_QUARTER_TURN_STAIR","SPIRAL_STAIR","DOUBLE_RETURN_STAIR","CURVED_RUN_STAIR","TWO_CURVED_RUN_STAIR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStairTypeEnum::IfcStairTypeEnum IfcStairTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT_RUN_STAIR") return IfcStairTypeEnum::IfcStairType_STRAIGHT_RUN_STAIR;
    if(s=="TWO_STRAIGHT_RUN_STAIR") return IfcStairTypeEnum::IfcStairType_TWO_STRAIGHT_RUN_STAIR;
    if(s=="QUARTER_WINDING_STAIR") return IfcStairTypeEnum::IfcStairType_QUARTER_WINDING_STAIR;
    if(s=="QUARTER_TURN_STAIR") return IfcStairTypeEnum::IfcStairType_QUARTER_TURN_STAIR;
    if(s=="HALF_WINDING_STAIR") return IfcStairTypeEnum::IfcStairType_HALF_WINDING_STAIR;
    if(s=="HALF_TURN_STAIR") return IfcStairTypeEnum::IfcStairType_HALF_TURN_STAIR;
    if(s=="TWO_QUARTER_WINDING_STAIR") return IfcStairTypeEnum::IfcStairType_TWO_QUARTER_WINDING_STAIR;
    if(s=="TWO_QUARTER_TURN_STAIR") return IfcStairTypeEnum::IfcStairType_TWO_QUARTER_TURN_STAIR;
    if(s=="THREE_QUARTER_WINDING_STAIR") return IfcStairTypeEnum::IfcStairType_THREE_QUARTER_WINDING_STAIR;
    if(s=="THREE_QUARTER_TURN_STAIR") return IfcStairTypeEnum::IfcStairType_THREE_QUARTER_TURN_STAIR;
    if(s=="SPIRAL_STAIR") return IfcStairTypeEnum::IfcStairType_SPIRAL_STAIR;
    if(s=="DOUBLE_RETURN_STAIR") return IfcStairTypeEnum::IfcStairType_DOUBLE_RETURN_STAIR;
    if(s=="CURVED_RUN_STAIR") return IfcStairTypeEnum::IfcStairType_CURVED_RUN_STAIR;
    if(s=="TWO_CURVED_RUN_STAIR") return IfcStairTypeEnum::IfcStairType_TWO_CURVED_RUN_STAIR;
    if(s=="USERDEFINED") return IfcStairTypeEnum::IfcStairType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcStairTypeEnum::IfcStairType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcStateEnum::ToString(IfcStateEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "READWRITE","READONLY","LOCKED","READWRITELOCKED","READONLYLOCKED" };
    return names[v];
}
IfcStateEnum::IfcStateEnum IfcStateEnum::FromString(const std::string& s) {
    if(s=="READWRITE") return IfcStateEnum::IfcState_READWRITE;
    if(s=="READONLY") return IfcStateEnum::IfcState_READONLY;
    if(s=="LOCKED") return IfcStateEnum::IfcState_LOCKED;
    if(s=="READWRITELOCKED") return IfcStateEnum::IfcState_READWRITELOCKED;
    if(s=="READONLYLOCKED") return IfcStateEnum::IfcState_READONLYLOCKED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcStructuralCurveTypeEnum::ToString(IfcStructuralCurveTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "RIGID_JOINED_MEMBER","PIN_JOINED_MEMBER","CABLE","TENSION_MEMBER","COMPRESSION_MEMBER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStructuralCurveTypeEnum::IfcStructuralCurveTypeEnum IfcStructuralCurveTypeEnum::FromString(const std::string& s) {
    if(s=="RIGID_JOINED_MEMBER") return IfcStructuralCurveTypeEnum::IfcStructuralCurveType_RIGID_JOINED_MEMBER;
    if(s=="PIN_JOINED_MEMBER") return IfcStructuralCurveTypeEnum::IfcStructuralCurveType_PIN_JOINED_MEMBER;
    if(s=="CABLE") return IfcStructuralCurveTypeEnum::IfcStructuralCurveType_CABLE;
    if(s=="TENSION_MEMBER") return IfcStructuralCurveTypeEnum::IfcStructuralCurveType_TENSION_MEMBER;
    if(s=="COMPRESSION_MEMBER") return IfcStructuralCurveTypeEnum::IfcStructuralCurveType_COMPRESSION_MEMBER;
    if(s=="USERDEFINED") return IfcStructuralCurveTypeEnum::IfcStructuralCurveType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcStructuralCurveTypeEnum::IfcStructuralCurveType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcStructuralSurfaceTypeEnum::ToString(IfcStructuralSurfaceTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BENDING_ELEMENT","MEMBRANE_ELEMENT","SHELL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceTypeEnum IfcStructuralSurfaceTypeEnum::FromString(const std::string& s) {
    if(s=="BENDING_ELEMENT") return IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceType_BENDING_ELEMENT;
    if(s=="MEMBRANE_ELEMENT") return IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceType_MEMBRANE_ELEMENT;
    if(s=="SHELL") return IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceType_SHELL;
    if(s=="USERDEFINED") return IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSurfaceSide::ToString(IfcSurfaceSide v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "POSITIVE","NEGATIVE","BOTH" };
    return names[v];
}
IfcSurfaceSide::IfcSurfaceSide IfcSurfaceSide::FromString(const std::string& s) {
    if(s=="POSITIVE") return IfcSurfaceSide::IfcSurfaceSide_POSITIVE;
    if(s=="NEGATIVE") return IfcSurfaceSide::IfcSurfaceSide_NEGATIVE;
    if(s=="BOTH") return IfcSurfaceSide::IfcSurfaceSide_BOTH;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSurfaceTextureEnum::ToString(IfcSurfaceTextureEnum v) {
    if ( v < 0 || v >= 9 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "BUMP","OPACITY","REFLECTION","SELFILLUMINATION","SHININESS","SPECULAR","TEXTURE","TRANSPARENCYMAP","NOTDEFINED" };
    return names[v];
}
IfcSurfaceTextureEnum::IfcSurfaceTextureEnum IfcSurfaceTextureEnum::FromString(const std::string& s) {
    if(s=="BUMP") return IfcSurfaceTextureEnum::IfcSurfaceTexture_BUMP;
    if(s=="OPACITY") return IfcSurfaceTextureEnum::IfcSurfaceTexture_OPACITY;
    if(s=="REFLECTION") return IfcSurfaceTextureEnum::IfcSurfaceTexture_REFLECTION;
    if(s=="SELFILLUMINATION") return IfcSurfaceTextureEnum::IfcSurfaceTexture_SELFILLUMINATION;
    if(s=="SHININESS") return IfcSurfaceTextureEnum::IfcSurfaceTexture_SHININESS;
    if(s=="SPECULAR") return IfcSurfaceTextureEnum::IfcSurfaceTexture_SPECULAR;
    if(s=="TEXTURE") return IfcSurfaceTextureEnum::IfcSurfaceTexture_TEXTURE;
    if(s=="TRANSPARENCYMAP") return IfcSurfaceTextureEnum::IfcSurfaceTexture_TRANSPARENCYMAP;
    if(s=="NOTDEFINED") return IfcSurfaceTextureEnum::IfcSurfaceTexture_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcSwitchingDeviceTypeEnum::ToString(IfcSwitchingDeviceTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CONTACTOR","EMERGENCYSTOP","STARTER","SWITCHDISCONNECTOR","TOGGLESWITCH","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceTypeEnum IfcSwitchingDeviceTypeEnum::FromString(const std::string& s) {
    if(s=="CONTACTOR") return IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceType_CONTACTOR;
    if(s=="EMERGENCYSTOP") return IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceType_EMERGENCYSTOP;
    if(s=="STARTER") return IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceType_STARTER;
    if(s=="SWITCHDISCONNECTOR") return IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceType_SWITCHDISCONNECTOR;
    if(s=="TOGGLESWITCH") return IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceType_TOGGLESWITCH;
    if(s=="USERDEFINED") return IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTankTypeEnum::ToString(IfcTankTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PREFORMED","SECTIONAL","EXPANSION","PRESSUREVESSEL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTankTypeEnum::IfcTankTypeEnum IfcTankTypeEnum::FromString(const std::string& s) {
    if(s=="PREFORMED") return IfcTankTypeEnum::IfcTankType_PREFORMED;
    if(s=="SECTIONAL") return IfcTankTypeEnum::IfcTankType_SECTIONAL;
    if(s=="EXPANSION") return IfcTankTypeEnum::IfcTankType_EXPANSION;
    if(s=="PRESSUREVESSEL") return IfcTankTypeEnum::IfcTankType_PRESSUREVESSEL;
    if(s=="USERDEFINED") return IfcTankTypeEnum::IfcTankType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcTankTypeEnum::IfcTankType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTendonTypeEnum::ToString(IfcTendonTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "STRAND","WIRE","BAR","COATED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTendonTypeEnum::IfcTendonTypeEnum IfcTendonTypeEnum::FromString(const std::string& s) {
    if(s=="STRAND") return IfcTendonTypeEnum::IfcTendonType_STRAND;
    if(s=="WIRE") return IfcTendonTypeEnum::IfcTendonType_WIRE;
    if(s=="BAR") return IfcTendonTypeEnum::IfcTendonType_BAR;
    if(s=="COATED") return IfcTendonTypeEnum::IfcTendonType_COATED;
    if(s=="USERDEFINED") return IfcTendonTypeEnum::IfcTendonType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcTendonTypeEnum::IfcTendonType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTextPath::ToString(IfcTextPath v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "LEFT","RIGHT","UP","DOWN" };
    return names[v];
}
IfcTextPath::IfcTextPath IfcTextPath::FromString(const std::string& s) {
    if(s=="LEFT") return IfcTextPath::IfcTextPath_LEFT;
    if(s=="RIGHT") return IfcTextPath::IfcTextPath_RIGHT;
    if(s=="UP") return IfcTextPath::IfcTextPath_UP;
    if(s=="DOWN") return IfcTextPath::IfcTextPath_DOWN;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcThermalLoadSourceEnum::ToString(IfcThermalLoadSourceEnum v) {
    if ( v < 0 || v >= 13 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "PEOPLE","LIGHTING","EQUIPMENT","VENTILATIONINDOORAIR","VENTILATIONOUTSIDEAIR","RECIRCULATEDAIR","EXHAUSTAIR","AIREXCHANGERATE","DRYBULBTEMPERATURE","RELATIVEHUMIDITY","INFILTRATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcThermalLoadSourceEnum::IfcThermalLoadSourceEnum IfcThermalLoadSourceEnum::FromString(const std::string& s) {
    if(s=="PEOPLE") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_PEOPLE;
    if(s=="LIGHTING") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_LIGHTING;
    if(s=="EQUIPMENT") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_EQUIPMENT;
    if(s=="VENTILATIONINDOORAIR") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_VENTILATIONINDOORAIR;
    if(s=="VENTILATIONOUTSIDEAIR") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_VENTILATIONOUTSIDEAIR;
    if(s=="RECIRCULATEDAIR") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_RECIRCULATEDAIR;
    if(s=="EXHAUSTAIR") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_EXHAUSTAIR;
    if(s=="AIREXCHANGERATE") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_AIREXCHANGERATE;
    if(s=="DRYBULBTEMPERATURE") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_DRYBULBTEMPERATURE;
    if(s=="RELATIVEHUMIDITY") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_RELATIVEHUMIDITY;
    if(s=="INFILTRATION") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_INFILTRATION;
    if(s=="USERDEFINED") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_USERDEFINED;
    if(s=="NOTDEFINED") return IfcThermalLoadSourceEnum::IfcThermalLoadSource_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcThermalLoadTypeEnum::ToString(IfcThermalLoadTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SENSIBLE","LATENT","RADIANT","NOTDEFINED" };
    return names[v];
}
IfcThermalLoadTypeEnum::IfcThermalLoadTypeEnum IfcThermalLoadTypeEnum::FromString(const std::string& s) {
    if(s=="SENSIBLE") return IfcThermalLoadTypeEnum::IfcThermalLoadType_SENSIBLE;
    if(s=="LATENT") return IfcThermalLoadTypeEnum::IfcThermalLoadType_LATENT;
    if(s=="RADIANT") return IfcThermalLoadTypeEnum::IfcThermalLoadType_RADIANT;
    if(s=="NOTDEFINED") return IfcThermalLoadTypeEnum::IfcThermalLoadType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTimeSeriesDataTypeEnum::ToString(IfcTimeSeriesDataTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CONTINUOUS","DISCRETE","DISCRETEBINARY","PIECEWISEBINARY","PIECEWISECONSTANT","PIECEWISECONTINUOUS","NOTDEFINED" };
    return names[v];
}
IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataTypeEnum IfcTimeSeriesDataTypeEnum::FromString(const std::string& s) {
    if(s=="CONTINUOUS") return IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataType_CONTINUOUS;
    if(s=="DISCRETE") return IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataType_DISCRETE;
    if(s=="DISCRETEBINARY") return IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataType_DISCRETEBINARY;
    if(s=="PIECEWISEBINARY") return IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataType_PIECEWISEBINARY;
    if(s=="PIECEWISECONSTANT") return IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataType_PIECEWISECONSTANT;
    if(s=="PIECEWISECONTINUOUS") return IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataType_PIECEWISECONTINUOUS;
    if(s=="NOTDEFINED") return IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTimeSeriesScheduleTypeEnum::ToString(IfcTimeSeriesScheduleTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ANNUAL","MONTHLY","WEEKLY","DAILY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleTypeEnum IfcTimeSeriesScheduleTypeEnum::FromString(const std::string& s) {
    if(s=="ANNUAL") return IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleType_ANNUAL;
    if(s=="MONTHLY") return IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleType_MONTHLY;
    if(s=="WEEKLY") return IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleType_WEEKLY;
    if(s=="DAILY") return IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleType_DAILY;
    if(s=="USERDEFINED") return IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTransformerTypeEnum::ToString(IfcTransformerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CURRENT","FREQUENCY","VOLTAGE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTransformerTypeEnum::IfcTransformerTypeEnum IfcTransformerTypeEnum::FromString(const std::string& s) {
    if(s=="CURRENT") return IfcTransformerTypeEnum::IfcTransformerType_CURRENT;
    if(s=="FREQUENCY") return IfcTransformerTypeEnum::IfcTransformerType_FREQUENCY;
    if(s=="VOLTAGE") return IfcTransformerTypeEnum::IfcTransformerType_VOLTAGE;
    if(s=="USERDEFINED") return IfcTransformerTypeEnum::IfcTransformerType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcTransformerTypeEnum::IfcTransformerType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTransitionCode::ToString(IfcTransitionCode v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "DISCONTINUOUS","CONTINUOUS","CONTSAMEGRADIENT","CONTSAMEGRADIENTSAMECURVATURE" };
    return names[v];
}
IfcTransitionCode::IfcTransitionCode IfcTransitionCode::FromString(const std::string& s) {
    if(s=="DISCONTINUOUS") return IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS;
    if(s=="CONTINUOUS") return IfcTransitionCode::IfcTransitionCode_CONTINUOUS;
    if(s=="CONTSAMEGRADIENT") return IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT;
    if(s=="CONTSAMEGRADIENTSAMECURVATURE") return IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENTSAMECURVATURE;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTransportElementTypeEnum::ToString(IfcTransportElementTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ELEVATOR","ESCALATOR","MOVINGWALKWAY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTransportElementTypeEnum::IfcTransportElementTypeEnum IfcTransportElementTypeEnum::FromString(const std::string& s) {
    if(s=="ELEVATOR") return IfcTransportElementTypeEnum::IfcTransportElementType_ELEVATOR;
    if(s=="ESCALATOR") return IfcTransportElementTypeEnum::IfcTransportElementType_ESCALATOR;
    if(s=="MOVINGWALKWAY") return IfcTransportElementTypeEnum::IfcTransportElementType_MOVINGWALKWAY;
    if(s=="USERDEFINED") return IfcTransportElementTypeEnum::IfcTransportElementType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcTransportElementTypeEnum::IfcTransportElementType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTrimmingPreference::ToString(IfcTrimmingPreference v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "CARTESIAN","PARAMETER","UNSPECIFIED" };
    return names[v];
}
IfcTrimmingPreference::IfcTrimmingPreference IfcTrimmingPreference::FromString(const std::string& s) {
    if(s=="CARTESIAN") return IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN;
    if(s=="PARAMETER") return IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER;
    if(s=="UNSPECIFIED") return IfcTrimmingPreference::IfcTrimmingPreference_UNSPECIFIED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcTubeBundleTypeEnum::ToString(IfcTubeBundleTypeEnum v) {
    if ( v < 0 || v >= 3 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FINNED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTubeBundleTypeEnum::IfcTubeBundleTypeEnum IfcTubeBundleTypeEnum::FromString(const std::string& s) {
    if(s=="FINNED") return IfcTubeBundleTypeEnum::IfcTubeBundleType_FINNED;
    if(s=="USERDEFINED") return IfcTubeBundleTypeEnum::IfcTubeBundleType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcTubeBundleTypeEnum::IfcTubeBundleType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcUnitEnum::ToString(IfcUnitEnum v) {
    if ( v < 0 || v >= 30 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ABSORBEDDOSEUNIT","AMOUNTOFSUBSTANCEUNIT","AREAUNIT","DOSEEQUIVALENTUNIT","ELECTRICCAPACITANCEUNIT","ELECTRICCHARGEUNIT","ELECTRICCONDUCTANCEUNIT","ELECTRICCURRENTUNIT","ELECTRICRESISTANCEUNIT","ELECTRICVOLTAGEUNIT","ENERGYUNIT","FORCEUNIT","FREQUENCYUNIT","ILLUMINANCEUNIT","INDUCTANCEUNIT","LENGTHUNIT","LUMINOUSFLUXUNIT","LUMINOUSINTENSITYUNIT","MAGNETICFLUXDENSITYUNIT","MAGNETICFLUXUNIT","MASSUNIT","PLANEANGLEUNIT","POWERUNIT","PRESSUREUNIT","RADIOACTIVITYUNIT","SOLIDANGLEUNIT","THERMODYNAMICTEMPERATUREUNIT","TIMEUNIT","VOLUMEUNIT","USERDEFINED" };
    return names[v];
}
IfcUnitEnum::IfcUnitEnum IfcUnitEnum::FromString(const std::string& s) {
    if(s=="ABSORBEDDOSEUNIT") return IfcUnitEnum::IfcUnit_ABSORBEDDOSEUNIT;
    if(s=="AMOUNTOFSUBSTANCEUNIT") return IfcUnitEnum::IfcUnit_AMOUNTOFSUBSTANCEUNIT;
    if(s=="AREAUNIT") return IfcUnitEnum::IfcUnit_AREAUNIT;
    if(s=="DOSEEQUIVALENTUNIT") return IfcUnitEnum::IfcUnit_DOSEEQUIVALENTUNIT;
    if(s=="ELECTRICCAPACITANCEUNIT") return IfcUnitEnum::IfcUnit_ELECTRICCAPACITANCEUNIT;
    if(s=="ELECTRICCHARGEUNIT") return IfcUnitEnum::IfcUnit_ELECTRICCHARGEUNIT;
    if(s=="ELECTRICCONDUCTANCEUNIT") return IfcUnitEnum::IfcUnit_ELECTRICCONDUCTANCEUNIT;
    if(s=="ELECTRICCURRENTUNIT") return IfcUnitEnum::IfcUnit_ELECTRICCURRENTUNIT;
    if(s=="ELECTRICRESISTANCEUNIT") return IfcUnitEnum::IfcUnit_ELECTRICRESISTANCEUNIT;
    if(s=="ELECTRICVOLTAGEUNIT") return IfcUnitEnum::IfcUnit_ELECTRICVOLTAGEUNIT;
    if(s=="ENERGYUNIT") return IfcUnitEnum::IfcUnit_ENERGYUNIT;
    if(s=="FORCEUNIT") return IfcUnitEnum::IfcUnit_FORCEUNIT;
    if(s=="FREQUENCYUNIT") return IfcUnitEnum::IfcUnit_FREQUENCYUNIT;
    if(s=="ILLUMINANCEUNIT") return IfcUnitEnum::IfcUnit_ILLUMINANCEUNIT;
    if(s=="INDUCTANCEUNIT") return IfcUnitEnum::IfcUnit_INDUCTANCEUNIT;
    if(s=="LENGTHUNIT") return IfcUnitEnum::IfcUnit_LENGTHUNIT;
    if(s=="LUMINOUSFLUXUNIT") return IfcUnitEnum::IfcUnit_LUMINOUSFLUXUNIT;
    if(s=="LUMINOUSINTENSITYUNIT") return IfcUnitEnum::IfcUnit_LUMINOUSINTENSITYUNIT;
    if(s=="MAGNETICFLUXDENSITYUNIT") return IfcUnitEnum::IfcUnit_MAGNETICFLUXDENSITYUNIT;
    if(s=="MAGNETICFLUXUNIT") return IfcUnitEnum::IfcUnit_MAGNETICFLUXUNIT;
    if(s=="MASSUNIT") return IfcUnitEnum::IfcUnit_MASSUNIT;
    if(s=="PLANEANGLEUNIT") return IfcUnitEnum::IfcUnit_PLANEANGLEUNIT;
    if(s=="POWERUNIT") return IfcUnitEnum::IfcUnit_POWERUNIT;
    if(s=="PRESSUREUNIT") return IfcUnitEnum::IfcUnit_PRESSUREUNIT;
    if(s=="RADIOACTIVITYUNIT") return IfcUnitEnum::IfcUnit_RADIOACTIVITYUNIT;
    if(s=="SOLIDANGLEUNIT") return IfcUnitEnum::IfcUnit_SOLIDANGLEUNIT;
    if(s=="THERMODYNAMICTEMPERATUREUNIT") return IfcUnitEnum::IfcUnit_THERMODYNAMICTEMPERATUREUNIT;
    if(s=="TIMEUNIT") return IfcUnitEnum::IfcUnit_TIMEUNIT;
    if(s=="VOLUMEUNIT") return IfcUnitEnum::IfcUnit_VOLUMEUNIT;
    if(s=="USERDEFINED") return IfcUnitEnum::IfcUnit_USERDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcUnitaryEquipmentTypeEnum::ToString(IfcUnitaryEquipmentTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AIRHANDLER","AIRCONDITIONINGUNIT","SPLITSYSTEM","ROOFTOPUNIT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentTypeEnum IfcUnitaryEquipmentTypeEnum::FromString(const std::string& s) {
    if(s=="AIRHANDLER") return IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentType_AIRHANDLER;
    if(s=="AIRCONDITIONINGUNIT") return IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentType_AIRCONDITIONINGUNIT;
    if(s=="SPLITSYSTEM") return IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentType_SPLITSYSTEM;
    if(s=="ROOFTOPUNIT") return IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentType_ROOFTOPUNIT;
    if(s=="USERDEFINED") return IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcValveTypeEnum::ToString(IfcValveTypeEnum v) {
    if ( v < 0 || v >= 23 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "AIRRELEASE","ANTIVACUUM","CHANGEOVER","CHECK","COMMISSIONING","DIVERTING","DRAWOFFCOCK","DOUBLECHECK","DOUBLEREGULATING","FAUCET","FLUSHING","GASCOCK","GASTAP","ISOLATING","MIXING","PRESSUREREDUCING","PRESSURERELIEF","REGULATING","SAFETYCUTOFF","STEAMTRAP","STOPCOCK","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcValveTypeEnum::IfcValveTypeEnum IfcValveTypeEnum::FromString(const std::string& s) {
    if(s=="AIRRELEASE") return IfcValveTypeEnum::IfcValveType_AIRRELEASE;
    if(s=="ANTIVACUUM") return IfcValveTypeEnum::IfcValveType_ANTIVACUUM;
    if(s=="CHANGEOVER") return IfcValveTypeEnum::IfcValveType_CHANGEOVER;
    if(s=="CHECK") return IfcValveTypeEnum::IfcValveType_CHECK;
    if(s=="COMMISSIONING") return IfcValveTypeEnum::IfcValveType_COMMISSIONING;
    if(s=="DIVERTING") return IfcValveTypeEnum::IfcValveType_DIVERTING;
    if(s=="DRAWOFFCOCK") return IfcValveTypeEnum::IfcValveType_DRAWOFFCOCK;
    if(s=="DOUBLECHECK") return IfcValveTypeEnum::IfcValveType_DOUBLECHECK;
    if(s=="DOUBLEREGULATING") return IfcValveTypeEnum::IfcValveType_DOUBLEREGULATING;
    if(s=="FAUCET") return IfcValveTypeEnum::IfcValveType_FAUCET;
    if(s=="FLUSHING") return IfcValveTypeEnum::IfcValveType_FLUSHING;
    if(s=="GASCOCK") return IfcValveTypeEnum::IfcValveType_GASCOCK;
    if(s=="GASTAP") return IfcValveTypeEnum::IfcValveType_GASTAP;
    if(s=="ISOLATING") return IfcValveTypeEnum::IfcValveType_ISOLATING;
    if(s=="MIXING") return IfcValveTypeEnum::IfcValveType_MIXING;
    if(s=="PRESSUREREDUCING") return IfcValveTypeEnum::IfcValveType_PRESSUREREDUCING;
    if(s=="PRESSURERELIEF") return IfcValveTypeEnum::IfcValveType_PRESSURERELIEF;
    if(s=="REGULATING") return IfcValveTypeEnum::IfcValveType_REGULATING;
    if(s=="SAFETYCUTOFF") return IfcValveTypeEnum::IfcValveType_SAFETYCUTOFF;
    if(s=="STEAMTRAP") return IfcValveTypeEnum::IfcValveType_STEAMTRAP;
    if(s=="STOPCOCK") return IfcValveTypeEnum::IfcValveType_STOPCOCK;
    if(s=="USERDEFINED") return IfcValveTypeEnum::IfcValveType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcValveTypeEnum::IfcValveType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcVibrationIsolatorTypeEnum::ToString(IfcVibrationIsolatorTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "COMPRESSION","SPRING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorTypeEnum IfcVibrationIsolatorTypeEnum::FromString(const std::string& s) {
    if(s=="COMPRESSION") return IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorType_COMPRESSION;
    if(s=="SPRING") return IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorType_SPRING;
    if(s=="USERDEFINED") return IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcWallTypeEnum::ToString(IfcWallTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "STANDARD","POLYGONAL","SHEAR","ELEMENTEDWALL","PLUMBINGWALL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWallTypeEnum::IfcWallTypeEnum IfcWallTypeEnum::FromString(const std::string& s) {
    if(s=="STANDARD") return IfcWallTypeEnum::IfcWallType_STANDARD;
    if(s=="POLYGONAL") return IfcWallTypeEnum::IfcWallType_POLYGONAL;
    if(s=="SHEAR") return IfcWallTypeEnum::IfcWallType_SHEAR;
    if(s=="ELEMENTEDWALL") return IfcWallTypeEnum::IfcWallType_ELEMENTEDWALL;
    if(s=="PLUMBINGWALL") return IfcWallTypeEnum::IfcWallType_PLUMBINGWALL;
    if(s=="USERDEFINED") return IfcWallTypeEnum::IfcWallType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcWallTypeEnum::IfcWallType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcWasteTerminalTypeEnum::ToString(IfcWasteTerminalTypeEnum v) {
    if ( v < 0 || v >= 12 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "FLOORTRAP","FLOORWASTE","GULLYSUMP","GULLYTRAP","GREASEINTERCEPTOR","OILINTERCEPTOR","PETROLINTERCEPTOR","ROOFDRAIN","WASTEDISPOSALUNIT","WASTETRAP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWasteTerminalTypeEnum::IfcWasteTerminalTypeEnum IfcWasteTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="FLOORTRAP") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_FLOORTRAP;
    if(s=="FLOORWASTE") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_FLOORWASTE;
    if(s=="GULLYSUMP") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_GULLYSUMP;
    if(s=="GULLYTRAP") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_GULLYTRAP;
    if(s=="GREASEINTERCEPTOR") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_GREASEINTERCEPTOR;
    if(s=="OILINTERCEPTOR") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_OILINTERCEPTOR;
    if(s=="PETROLINTERCEPTOR") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_PETROLINTERCEPTOR;
    if(s=="ROOFDRAIN") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_ROOFDRAIN;
    if(s=="WASTEDISPOSALUNIT") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_WASTEDISPOSALUNIT;
    if(s=="WASTETRAP") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_WASTETRAP;
    if(s=="USERDEFINED") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcWasteTerminalTypeEnum::IfcWasteTerminalType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcWindowPanelOperationEnum::ToString(IfcWindowPanelOperationEnum v) {
    if ( v < 0 || v >= 14 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SIDEHUNGRIGHTHAND","SIDEHUNGLEFTHAND","TILTANDTURNRIGHTHAND","TILTANDTURNLEFTHAND","TOPHUNG","BOTTOMHUNG","PIVOTHORIZONTAL","PIVOTVERTICAL","SLIDINGHORIZONTAL","SLIDINGVERTICAL","REMOVABLECASEMENT","FIXEDCASEMENT","OTHEROPERATION","NOTDEFINED" };
    return names[v];
}
IfcWindowPanelOperationEnum::IfcWindowPanelOperationEnum IfcWindowPanelOperationEnum::FromString(const std::string& s) {
    if(s=="SIDEHUNGRIGHTHAND") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_SIDEHUNGRIGHTHAND;
    if(s=="SIDEHUNGLEFTHAND") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_SIDEHUNGLEFTHAND;
    if(s=="TILTANDTURNRIGHTHAND") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_TILTANDTURNRIGHTHAND;
    if(s=="TILTANDTURNLEFTHAND") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_TILTANDTURNLEFTHAND;
    if(s=="TOPHUNG") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_TOPHUNG;
    if(s=="BOTTOMHUNG") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_BOTTOMHUNG;
    if(s=="PIVOTHORIZONTAL") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_PIVOTHORIZONTAL;
    if(s=="PIVOTVERTICAL") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_PIVOTVERTICAL;
    if(s=="SLIDINGHORIZONTAL") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_SLIDINGHORIZONTAL;
    if(s=="SLIDINGVERTICAL") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_SLIDINGVERTICAL;
    if(s=="REMOVABLECASEMENT") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_REMOVABLECASEMENT;
    if(s=="FIXEDCASEMENT") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_FIXEDCASEMENT;
    if(s=="OTHEROPERATION") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_OTHEROPERATION;
    if(s=="NOTDEFINED") return IfcWindowPanelOperationEnum::IfcWindowPanelOperation_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcWindowPanelPositionEnum::ToString(IfcWindowPanelPositionEnum v) {
    if ( v < 0 || v >= 6 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "LEFT","MIDDLE","RIGHT","BOTTOM","TOP","NOTDEFINED" };
    return names[v];
}
IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum IfcWindowPanelPositionEnum::FromString(const std::string& s) {
    if(s=="LEFT") return IfcWindowPanelPositionEnum::IfcWindowPanelPosition_LEFT;
    if(s=="MIDDLE") return IfcWindowPanelPositionEnum::IfcWindowPanelPosition_MIDDLE;
    if(s=="RIGHT") return IfcWindowPanelPositionEnum::IfcWindowPanelPosition_RIGHT;
    if(s=="BOTTOM") return IfcWindowPanelPositionEnum::IfcWindowPanelPosition_BOTTOM;
    if(s=="TOP") return IfcWindowPanelPositionEnum::IfcWindowPanelPosition_TOP;
    if(s=="NOTDEFINED") return IfcWindowPanelPositionEnum::IfcWindowPanelPosition_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcWindowStyleConstructionEnum::ToString(IfcWindowStyleConstructionEnum v) {
    if ( v < 0 || v >= 8 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ALUMINIUM","HIGH_GRADE_STEEL","STEEL","WOOD","ALUMINIUM_WOOD","PLASTIC","OTHER_CONSTRUCTION","NOTDEFINED" };
    return names[v];
}
IfcWindowStyleConstructionEnum::IfcWindowStyleConstructionEnum IfcWindowStyleConstructionEnum::FromString(const std::string& s) {
    if(s=="ALUMINIUM") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_ALUMINIUM;
    if(s=="HIGH_GRADE_STEEL") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_HIGH_GRADE_STEEL;
    if(s=="STEEL") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_STEEL;
    if(s=="WOOD") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_WOOD;
    if(s=="ALUMINIUM_WOOD") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_ALUMINIUM_WOOD;
    if(s=="PLASTIC") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_PLASTIC;
    if(s=="OTHER_CONSTRUCTION") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_OTHER_CONSTRUCTION;
    if(s=="NOTDEFINED") return IfcWindowStyleConstructionEnum::IfcWindowStyleConstruction_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcWindowStyleOperationEnum::ToString(IfcWindowStyleOperationEnum v) {
    if ( v < 0 || v >= 11 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "SINGLE_PANEL","DOUBLE_PANEL_VERTICAL","DOUBLE_PANEL_HORIZONTAL","TRIPLE_PANEL_VERTICAL","TRIPLE_PANEL_BOTTOM","TRIPLE_PANEL_TOP","TRIPLE_PANEL_LEFT","TRIPLE_PANEL_RIGHT","TRIPLE_PANEL_HORIZONTAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWindowStyleOperationEnum::IfcWindowStyleOperationEnum IfcWindowStyleOperationEnum::FromString(const std::string& s) {
    if(s=="SINGLE_PANEL") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_SINGLE_PANEL;
    if(s=="DOUBLE_PANEL_VERTICAL") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_DOUBLE_PANEL_VERTICAL;
    if(s=="DOUBLE_PANEL_HORIZONTAL") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_DOUBLE_PANEL_HORIZONTAL;
    if(s=="TRIPLE_PANEL_VERTICAL") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_TRIPLE_PANEL_VERTICAL;
    if(s=="TRIPLE_PANEL_BOTTOM") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_TRIPLE_PANEL_BOTTOM;
    if(s=="TRIPLE_PANEL_TOP") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_TRIPLE_PANEL_TOP;
    if(s=="TRIPLE_PANEL_LEFT") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_TRIPLE_PANEL_LEFT;
    if(s=="TRIPLE_PANEL_RIGHT") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_TRIPLE_PANEL_RIGHT;
    if(s=="TRIPLE_PANEL_HORIZONTAL") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_TRIPLE_PANEL_HORIZONTAL;
    if(s=="USERDEFINED") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_USERDEFINED;
    if(s=="NOTDEFINED") return IfcWindowStyleOperationEnum::IfcWindowStyleOperation_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}
std::string IfcWorkControlTypeEnum::ToString(IfcWorkControlTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw IfcException("Unable to find find keyword in schema");
    const char* names[] = { "ACTUAL","BASELINE","PLANNED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWorkControlTypeEnum::IfcWorkControlTypeEnum IfcWorkControlTypeEnum::FromString(const std::string& s) {
    if(s=="ACTUAL") return IfcWorkControlTypeEnum::IfcWorkControlType_ACTUAL;
    if(s=="BASELINE") return IfcWorkControlTypeEnum::IfcWorkControlType_BASELINE;
    if(s=="PLANNED") return IfcWorkControlTypeEnum::IfcWorkControlType_PLANNED;
    if(s=="USERDEFINED") return IfcWorkControlTypeEnum::IfcWorkControlType_USERDEFINED;
    if(s=="NOTDEFINED") return IfcWorkControlTypeEnum::IfcWorkControlType_NOTDEFINED;
    throw IfcException("Unable to find find keyword in schema");
}

// Function implementations for Ifc2DCompositeCurve
bool Ifc2DCompositeCurve::is(Type::Enum v) const { return v == Type::Ifc2DCompositeCurve || IfcCompositeCurve::is(v); }
Type::Enum Ifc2DCompositeCurve::type() const { return Type::Ifc2DCompositeCurve; }
Type::Enum Ifc2DCompositeCurve::Class() { return Type::Ifc2DCompositeCurve; }
Ifc2DCompositeCurve::Ifc2DCompositeCurve(IfcAbstractEntityPtr e) { if (!is(Type::Ifc2DCompositeCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcActionRequest
IfcIdentifier IfcActionRequest::RequestID() { return *entity->getArgument(5); }
bool IfcActionRequest::is(Type::Enum v) const { return v == Type::IfcActionRequest || IfcControl::is(v); }
Type::Enum IfcActionRequest::type() const { return Type::IfcActionRequest; }
Type::Enum IfcActionRequest::Class() { return Type::IfcActionRequest; }
IfcActionRequest::IfcActionRequest(IfcAbstractEntityPtr e) { if (!is(Type::IfcActionRequest)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcActor
IfcActorSelect IfcActor::TheActor() { return *entity->getArgument(5); }
IfcRelAssignsToActor::list IfcActor::IsActingUpon() { RETURN_INVERSE(IfcRelAssignsToActor) }
bool IfcActor::is(Type::Enum v) const { return v == Type::IfcActor || IfcObject::is(v); }
Type::Enum IfcActor::type() const { return Type::IfcActor; }
Type::Enum IfcActor::Class() { return Type::IfcActor; }
IfcActor::IfcActor(IfcAbstractEntityPtr e) { if (!is(Type::IfcActor)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcActorRole
IfcRoleEnum::IfcRoleEnum IfcActorRole::Role() { return IfcRoleEnum::FromString(*entity->getArgument(0)); }
bool IfcActorRole::hasUserDefinedRole() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcActorRole::UserDefinedRole() { return *entity->getArgument(1); }
bool IfcActorRole::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcActorRole::Description() { return *entity->getArgument(2); }
bool IfcActorRole::is(Type::Enum v) const { return v == Type::IfcActorRole; }
Type::Enum IfcActorRole::type() const { return Type::IfcActorRole; }
Type::Enum IfcActorRole::Class() { return Type::IfcActorRole; }
IfcActorRole::IfcActorRole(IfcAbstractEntityPtr e) { if (!is(Type::IfcActorRole)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcActuatorType
IfcActuatorTypeEnum::IfcActuatorTypeEnum IfcActuatorType::PredefinedType() { return IfcActuatorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcActuatorType::is(Type::Enum v) const { return v == Type::IfcActuatorType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcActuatorType::type() const { return Type::IfcActuatorType; }
Type::Enum IfcActuatorType::Class() { return Type::IfcActuatorType; }
IfcActuatorType::IfcActuatorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcActuatorType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAddress
bool IfcAddress::hasPurpose() { return !entity->getArgument(0)->isNull(); }
IfcAddressTypeEnum::IfcAddressTypeEnum IfcAddress::Purpose() { return IfcAddressTypeEnum::FromString(*entity->getArgument(0)); }
bool IfcAddress::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcAddress::Description() { return *entity->getArgument(1); }
bool IfcAddress::hasUserDefinedPurpose() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcAddress::UserDefinedPurpose() { return *entity->getArgument(2); }
IfcPerson::list IfcAddress::OfPerson() { RETURN_INVERSE(IfcPerson) }
IfcOrganization::list IfcAddress::OfOrganization() { RETURN_INVERSE(IfcOrganization) }
bool IfcAddress::is(Type::Enum v) const { return v == Type::IfcAddress; }
Type::Enum IfcAddress::type() const { return Type::IfcAddress; }
Type::Enum IfcAddress::Class() { return Type::IfcAddress; }
IfcAddress::IfcAddress(IfcAbstractEntityPtr e) { if (!is(Type::IfcAddress)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAirTerminalBoxType
IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxTypeEnum IfcAirTerminalBoxType::PredefinedType() { return IfcAirTerminalBoxTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAirTerminalBoxType::is(Type::Enum v) const { return v == Type::IfcAirTerminalBoxType || IfcFlowControllerType::is(v); }
Type::Enum IfcAirTerminalBoxType::type() const { return Type::IfcAirTerminalBoxType; }
Type::Enum IfcAirTerminalBoxType::Class() { return Type::IfcAirTerminalBoxType; }
IfcAirTerminalBoxType::IfcAirTerminalBoxType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAirTerminalBoxType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAirTerminalType
IfcAirTerminalTypeEnum::IfcAirTerminalTypeEnum IfcAirTerminalType::PredefinedType() { return IfcAirTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAirTerminalType::is(Type::Enum v) const { return v == Type::IfcAirTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcAirTerminalType::type() const { return Type::IfcAirTerminalType; }
Type::Enum IfcAirTerminalType::Class() { return Type::IfcAirTerminalType; }
IfcAirTerminalType::IfcAirTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAirTerminalType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAirToAirHeatRecoveryType
IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryTypeEnum IfcAirToAirHeatRecoveryType::PredefinedType() { return IfcAirToAirHeatRecoveryTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAirToAirHeatRecoveryType::is(Type::Enum v) const { return v == Type::IfcAirToAirHeatRecoveryType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcAirToAirHeatRecoveryType::type() const { return Type::IfcAirToAirHeatRecoveryType; }
Type::Enum IfcAirToAirHeatRecoveryType::Class() { return Type::IfcAirToAirHeatRecoveryType; }
IfcAirToAirHeatRecoveryType::IfcAirToAirHeatRecoveryType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAirToAirHeatRecoveryType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAlarmType
IfcAlarmTypeEnum::IfcAlarmTypeEnum IfcAlarmType::PredefinedType() { return IfcAlarmTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAlarmType::is(Type::Enum v) const { return v == Type::IfcAlarmType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcAlarmType::type() const { return Type::IfcAlarmType; }
Type::Enum IfcAlarmType::Class() { return Type::IfcAlarmType; }
IfcAlarmType::IfcAlarmType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAlarmType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAngularDimension
bool IfcAngularDimension::is(Type::Enum v) const { return v == Type::IfcAngularDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcAngularDimension::type() const { return Type::IfcAngularDimension; }
Type::Enum IfcAngularDimension::Class() { return Type::IfcAngularDimension; }
IfcAngularDimension::IfcAngularDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcAngularDimension)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotation
IfcRelContainedInSpatialStructure::list IfcAnnotation::ContainedInStructure() { RETURN_INVERSE(IfcRelContainedInSpatialStructure) }
bool IfcAnnotation::is(Type::Enum v) const { return v == Type::IfcAnnotation || IfcProduct::is(v); }
Type::Enum IfcAnnotation::type() const { return Type::IfcAnnotation; }
Type::Enum IfcAnnotation::Class() { return Type::IfcAnnotation; }
IfcAnnotation::IfcAnnotation(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationCurveOccurrence
bool IfcAnnotationCurveOccurrence::is(Type::Enum v) const { return v == Type::IfcAnnotationCurveOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationCurveOccurrence::type() const { return Type::IfcAnnotationCurveOccurrence; }
Type::Enum IfcAnnotationCurveOccurrence::Class() { return Type::IfcAnnotationCurveOccurrence; }
IfcAnnotationCurveOccurrence::IfcAnnotationCurveOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationCurveOccurrence)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationFillArea
IfcCurve* IfcAnnotationFillArea::OuterBoundary() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
bool IfcAnnotationFillArea::hasInnerBoundaries() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > IfcAnnotationFillArea::InnerBoundaries() { RETURN_AS_LIST(IfcCurve,1) }
bool IfcAnnotationFillArea::is(Type::Enum v) const { return v == Type::IfcAnnotationFillArea || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcAnnotationFillArea::type() const { return Type::IfcAnnotationFillArea; }
Type::Enum IfcAnnotationFillArea::Class() { return Type::IfcAnnotationFillArea; }
IfcAnnotationFillArea::IfcAnnotationFillArea(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationFillArea)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationFillAreaOccurrence
bool IfcAnnotationFillAreaOccurrence::hasFillStyleTarget() { return !entity->getArgument(3)->isNull(); }
IfcPoint* IfcAnnotationFillAreaOccurrence::FillStyleTarget() { return reinterpret_pointer_cast<IfcBaseClass,IfcPoint>(*entity->getArgument(3)); }
bool IfcAnnotationFillAreaOccurrence::hasGlobalOrLocal() { return !entity->getArgument(4)->isNull(); }
IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum IfcAnnotationFillAreaOccurrence::GlobalOrLocal() { return IfcGlobalOrLocalEnum::FromString(*entity->getArgument(4)); }
bool IfcAnnotationFillAreaOccurrence::is(Type::Enum v) const { return v == Type::IfcAnnotationFillAreaOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationFillAreaOccurrence::type() const { return Type::IfcAnnotationFillAreaOccurrence; }
Type::Enum IfcAnnotationFillAreaOccurrence::Class() { return Type::IfcAnnotationFillAreaOccurrence; }
IfcAnnotationFillAreaOccurrence::IfcAnnotationFillAreaOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationFillAreaOccurrence)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationOccurrence
bool IfcAnnotationOccurrence::is(Type::Enum v) const { return v == Type::IfcAnnotationOccurrence || IfcStyledItem::is(v); }
Type::Enum IfcAnnotationOccurrence::type() const { return Type::IfcAnnotationOccurrence; }
Type::Enum IfcAnnotationOccurrence::Class() { return Type::IfcAnnotationOccurrence; }
IfcAnnotationOccurrence::IfcAnnotationOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationOccurrence)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationSurface
IfcGeometricRepresentationItem* IfcAnnotationSurface::Item() { return reinterpret_pointer_cast<IfcBaseClass,IfcGeometricRepresentationItem>(*entity->getArgument(0)); }
bool IfcAnnotationSurface::hasTextureCoordinates() { return !entity->getArgument(1)->isNull(); }
IfcTextureCoordinate* IfcAnnotationSurface::TextureCoordinates() { return reinterpret_pointer_cast<IfcBaseClass,IfcTextureCoordinate>(*entity->getArgument(1)); }
bool IfcAnnotationSurface::is(Type::Enum v) const { return v == Type::IfcAnnotationSurface || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcAnnotationSurface::type() const { return Type::IfcAnnotationSurface; }
Type::Enum IfcAnnotationSurface::Class() { return Type::IfcAnnotationSurface; }
IfcAnnotationSurface::IfcAnnotationSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationSurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationSurfaceOccurrence
bool IfcAnnotationSurfaceOccurrence::is(Type::Enum v) const { return v == Type::IfcAnnotationSurfaceOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationSurfaceOccurrence::type() const { return Type::IfcAnnotationSurfaceOccurrence; }
Type::Enum IfcAnnotationSurfaceOccurrence::Class() { return Type::IfcAnnotationSurfaceOccurrence; }
IfcAnnotationSurfaceOccurrence::IfcAnnotationSurfaceOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationSurfaceOccurrence)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationSymbolOccurrence
bool IfcAnnotationSymbolOccurrence::is(Type::Enum v) const { return v == Type::IfcAnnotationSymbolOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationSymbolOccurrence::type() const { return Type::IfcAnnotationSymbolOccurrence; }
Type::Enum IfcAnnotationSymbolOccurrence::Class() { return Type::IfcAnnotationSymbolOccurrence; }
IfcAnnotationSymbolOccurrence::IfcAnnotationSymbolOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationSymbolOccurrence)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAnnotationTextOccurrence
bool IfcAnnotationTextOccurrence::is(Type::Enum v) const { return v == Type::IfcAnnotationTextOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationTextOccurrence::type() const { return Type::IfcAnnotationTextOccurrence; }
Type::Enum IfcAnnotationTextOccurrence::Class() { return Type::IfcAnnotationTextOccurrence; }
IfcAnnotationTextOccurrence::IfcAnnotationTextOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationTextOccurrence)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcApplication
IfcOrganization* IfcApplication::ApplicationDeveloper() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(0)); }
IfcLabel IfcApplication::Version() { return *entity->getArgument(1); }
IfcLabel IfcApplication::ApplicationFullName() { return *entity->getArgument(2); }
IfcIdentifier IfcApplication::ApplicationIdentifier() { return *entity->getArgument(3); }
bool IfcApplication::is(Type::Enum v) const { return v == Type::IfcApplication; }
Type::Enum IfcApplication::type() const { return Type::IfcApplication; }
Type::Enum IfcApplication::Class() { return Type::IfcApplication; }
IfcApplication::IfcApplication(IfcAbstractEntityPtr e) { if (!is(Type::IfcApplication)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAppliedValue
bool IfcAppliedValue::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcAppliedValue::Name() { return *entity->getArgument(0); }
bool IfcAppliedValue::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcAppliedValue::Description() { return *entity->getArgument(1); }
bool IfcAppliedValue::hasAppliedValue() { return !entity->getArgument(2)->isNull(); }
IfcAppliedValueSelect IfcAppliedValue::AppliedValue() { return *entity->getArgument(2); }
bool IfcAppliedValue::hasUnitBasis() { return !entity->getArgument(3)->isNull(); }
IfcMeasureWithUnit* IfcAppliedValue::UnitBasis() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(3)); }
bool IfcAppliedValue::hasApplicableDate() { return !entity->getArgument(4)->isNull(); }
IfcDateTimeSelect IfcAppliedValue::ApplicableDate() { return *entity->getArgument(4); }
bool IfcAppliedValue::hasFixedUntilDate() { return !entity->getArgument(5)->isNull(); }
IfcDateTimeSelect IfcAppliedValue::FixedUntilDate() { return *entity->getArgument(5); }
IfcReferencesValueDocument::list IfcAppliedValue::ValuesReferenced() { RETURN_INVERSE(IfcReferencesValueDocument) }
IfcAppliedValueRelationship::list IfcAppliedValue::ValueOfComponents() { RETURN_INVERSE(IfcAppliedValueRelationship) }
IfcAppliedValueRelationship::list IfcAppliedValue::IsComponentIn() { RETURN_INVERSE(IfcAppliedValueRelationship) }
bool IfcAppliedValue::is(Type::Enum v) const { return v == Type::IfcAppliedValue; }
Type::Enum IfcAppliedValue::type() const { return Type::IfcAppliedValue; }
Type::Enum IfcAppliedValue::Class() { return Type::IfcAppliedValue; }
IfcAppliedValue::IfcAppliedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcAppliedValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAppliedValueRelationship
IfcAppliedValue* IfcAppliedValueRelationship::ComponentOfTotal() { return reinterpret_pointer_cast<IfcBaseClass,IfcAppliedValue>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > IfcAppliedValueRelationship::Components() { RETURN_AS_LIST(IfcAppliedValue,1) }
IfcArithmeticOperatorEnum::IfcArithmeticOperatorEnum IfcAppliedValueRelationship::ArithmeticOperator() { return IfcArithmeticOperatorEnum::FromString(*entity->getArgument(2)); }
bool IfcAppliedValueRelationship::hasName() { return !entity->getArgument(3)->isNull(); }
IfcLabel IfcAppliedValueRelationship::Name() { return *entity->getArgument(3); }
bool IfcAppliedValueRelationship::hasDescription() { return !entity->getArgument(4)->isNull(); }
IfcText IfcAppliedValueRelationship::Description() { return *entity->getArgument(4); }
bool IfcAppliedValueRelationship::is(Type::Enum v) const { return v == Type::IfcAppliedValueRelationship; }
Type::Enum IfcAppliedValueRelationship::type() const { return Type::IfcAppliedValueRelationship; }
Type::Enum IfcAppliedValueRelationship::Class() { return Type::IfcAppliedValueRelationship; }
IfcAppliedValueRelationship::IfcAppliedValueRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcAppliedValueRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcApproval
bool IfcApproval::hasDescription() { return !entity->getArgument(0)->isNull(); }
IfcText IfcApproval::Description() { return *entity->getArgument(0); }
IfcDateTimeSelect IfcApproval::ApprovalDateTime() { return *entity->getArgument(1); }
bool IfcApproval::hasApprovalStatus() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcApproval::ApprovalStatus() { return *entity->getArgument(2); }
bool IfcApproval::hasApprovalLevel() { return !entity->getArgument(3)->isNull(); }
IfcLabel IfcApproval::ApprovalLevel() { return *entity->getArgument(3); }
bool IfcApproval::hasApprovalQualifier() { return !entity->getArgument(4)->isNull(); }
IfcText IfcApproval::ApprovalQualifier() { return *entity->getArgument(4); }
IfcLabel IfcApproval::Name() { return *entity->getArgument(5); }
IfcIdentifier IfcApproval::Identifier() { return *entity->getArgument(6); }
IfcApprovalActorRelationship::list IfcApproval::Actors() { RETURN_INVERSE(IfcApprovalActorRelationship) }
IfcApprovalRelationship::list IfcApproval::IsRelatedWith() { RETURN_INVERSE(IfcApprovalRelationship) }
IfcApprovalRelationship::list IfcApproval::Relates() { RETURN_INVERSE(IfcApprovalRelationship) }
bool IfcApproval::is(Type::Enum v) const { return v == Type::IfcApproval; }
Type::Enum IfcApproval::type() const { return Type::IfcApproval; }
Type::Enum IfcApproval::Class() { return Type::IfcApproval; }
IfcApproval::IfcApproval(IfcAbstractEntityPtr e) { if (!is(Type::IfcApproval)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcApprovalActorRelationship
IfcActorSelect IfcApprovalActorRelationship::Actor() { return *entity->getArgument(0); }
IfcApproval* IfcApprovalActorRelationship::Approval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(1)); }
IfcActorRole* IfcApprovalActorRelationship::Role() { return reinterpret_pointer_cast<IfcBaseClass,IfcActorRole>(*entity->getArgument(2)); }
bool IfcApprovalActorRelationship::is(Type::Enum v) const { return v == Type::IfcApprovalActorRelationship; }
Type::Enum IfcApprovalActorRelationship::type() const { return Type::IfcApprovalActorRelationship; }
Type::Enum IfcApprovalActorRelationship::Class() { return Type::IfcApprovalActorRelationship; }
IfcApprovalActorRelationship::IfcApprovalActorRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcApprovalActorRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcApprovalPropertyRelationship
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcApprovalPropertyRelationship::ApprovedProperties() { RETURN_AS_LIST(IfcProperty,0) }
IfcApproval* IfcApprovalPropertyRelationship::Approval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(1)); }
bool IfcApprovalPropertyRelationship::is(Type::Enum v) const { return v == Type::IfcApprovalPropertyRelationship; }
Type::Enum IfcApprovalPropertyRelationship::type() const { return Type::IfcApprovalPropertyRelationship; }
Type::Enum IfcApprovalPropertyRelationship::Class() { return Type::IfcApprovalPropertyRelationship; }
IfcApprovalPropertyRelationship::IfcApprovalPropertyRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcApprovalPropertyRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcApprovalRelationship
IfcApproval* IfcApprovalRelationship::RelatedApproval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(0)); }
IfcApproval* IfcApprovalRelationship::RelatingApproval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(1)); }
bool IfcApprovalRelationship::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcApprovalRelationship::Description() { return *entity->getArgument(2); }
IfcLabel IfcApprovalRelationship::Name() { return *entity->getArgument(3); }
bool IfcApprovalRelationship::is(Type::Enum v) const { return v == Type::IfcApprovalRelationship; }
Type::Enum IfcApprovalRelationship::type() const { return Type::IfcApprovalRelationship; }
Type::Enum IfcApprovalRelationship::Class() { return Type::IfcApprovalRelationship; }
IfcApprovalRelationship::IfcApprovalRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcApprovalRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcArbitraryClosedProfileDef
IfcCurve* IfcArbitraryClosedProfileDef::OuterCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
bool IfcArbitraryClosedProfileDef::is(Type::Enum v) const { return v == Type::IfcArbitraryClosedProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcArbitraryClosedProfileDef::type() const { return Type::IfcArbitraryClosedProfileDef; }
Type::Enum IfcArbitraryClosedProfileDef::Class() { return Type::IfcArbitraryClosedProfileDef; }
IfcArbitraryClosedProfileDef::IfcArbitraryClosedProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcArbitraryClosedProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcArbitraryOpenProfileDef
IfcBoundedCurve* IfcArbitraryOpenProfileDef::Curve() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundedCurve>(*entity->getArgument(2)); }
bool IfcArbitraryOpenProfileDef::is(Type::Enum v) const { return v == Type::IfcArbitraryOpenProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcArbitraryOpenProfileDef::type() const { return Type::IfcArbitraryOpenProfileDef; }
Type::Enum IfcArbitraryOpenProfileDef::Class() { return Type::IfcArbitraryOpenProfileDef; }
IfcArbitraryOpenProfileDef::IfcArbitraryOpenProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcArbitraryOpenProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcArbitraryProfileDefWithVoids
SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > IfcArbitraryProfileDefWithVoids::InnerCurves() { RETURN_AS_LIST(IfcCurve,3) }
bool IfcArbitraryProfileDefWithVoids::is(Type::Enum v) const { return v == Type::IfcArbitraryProfileDefWithVoids || IfcArbitraryClosedProfileDef::is(v); }
Type::Enum IfcArbitraryProfileDefWithVoids::type() const { return Type::IfcArbitraryProfileDefWithVoids; }
Type::Enum IfcArbitraryProfileDefWithVoids::Class() { return Type::IfcArbitraryProfileDefWithVoids; }
IfcArbitraryProfileDefWithVoids::IfcArbitraryProfileDefWithVoids(IfcAbstractEntityPtr e) { if (!is(Type::IfcArbitraryProfileDefWithVoids)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAsset
IfcIdentifier IfcAsset::AssetID() { return *entity->getArgument(5); }
IfcCostValue* IfcAsset::OriginalValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(6)); }
IfcCostValue* IfcAsset::CurrentValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(7)); }
IfcCostValue* IfcAsset::TotalReplacementCost() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(8)); }
IfcActorSelect IfcAsset::Owner() { return *entity->getArgument(9); }
IfcActorSelect IfcAsset::User() { return *entity->getArgument(10); }
IfcPerson* IfcAsset::ResponsiblePerson() { return reinterpret_pointer_cast<IfcBaseClass,IfcPerson>(*entity->getArgument(11)); }
IfcCalendarDate* IfcAsset::IncorporationDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(12)); }
IfcCostValue* IfcAsset::DepreciatedValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(13)); }
bool IfcAsset::is(Type::Enum v) const { return v == Type::IfcAsset || IfcGroup::is(v); }
Type::Enum IfcAsset::type() const { return Type::IfcAsset; }
Type::Enum IfcAsset::Class() { return Type::IfcAsset; }
IfcAsset::IfcAsset(IfcAbstractEntityPtr e) { if (!is(Type::IfcAsset)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAsymmetricIShapeProfileDef
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::TopFlangeWidth() { return *entity->getArgument(8); }
bool IfcAsymmetricIShapeProfileDef::hasTopFlangeThickness() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::TopFlangeThickness() { return *entity->getArgument(9); }
bool IfcAsymmetricIShapeProfileDef::hasTopFlangeFilletRadius() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::TopFlangeFilletRadius() { return *entity->getArgument(10); }
bool IfcAsymmetricIShapeProfileDef::hasCentreOfGravityInY() { return !entity->getArgument(11)->isNull(); }
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::CentreOfGravityInY() { return *entity->getArgument(11); }
bool IfcAsymmetricIShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcAsymmetricIShapeProfileDef || IfcIShapeProfileDef::is(v); }
Type::Enum IfcAsymmetricIShapeProfileDef::type() const { return Type::IfcAsymmetricIShapeProfileDef; }
Type::Enum IfcAsymmetricIShapeProfileDef::Class() { return Type::IfcAsymmetricIShapeProfileDef; }
IfcAsymmetricIShapeProfileDef::IfcAsymmetricIShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcAsymmetricIShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAxis1Placement
bool IfcAxis1Placement::hasAxis() { return !entity->getArgument(1)->isNull(); }
IfcDirection* IfcAxis1Placement::Axis() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
bool IfcAxis1Placement::is(Type::Enum v) const { return v == Type::IfcAxis1Placement || IfcPlacement::is(v); }
Type::Enum IfcAxis1Placement::type() const { return Type::IfcAxis1Placement; }
Type::Enum IfcAxis1Placement::Class() { return Type::IfcAxis1Placement; }
IfcAxis1Placement::IfcAxis1Placement(IfcAbstractEntityPtr e) { if (!is(Type::IfcAxis1Placement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAxis2Placement2D
bool IfcAxis2Placement2D::hasRefDirection() { return !entity->getArgument(1)->isNull(); }
IfcDirection* IfcAxis2Placement2D::RefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
bool IfcAxis2Placement2D::is(Type::Enum v) const { return v == Type::IfcAxis2Placement2D || IfcPlacement::is(v); }
Type::Enum IfcAxis2Placement2D::type() const { return Type::IfcAxis2Placement2D; }
Type::Enum IfcAxis2Placement2D::Class() { return Type::IfcAxis2Placement2D; }
IfcAxis2Placement2D::IfcAxis2Placement2D(IfcAbstractEntityPtr e) { if (!is(Type::IfcAxis2Placement2D)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcAxis2Placement3D
bool IfcAxis2Placement3D::hasAxis() { return !entity->getArgument(1)->isNull(); }
IfcDirection* IfcAxis2Placement3D::Axis() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
bool IfcAxis2Placement3D::hasRefDirection() { return !entity->getArgument(2)->isNull(); }
IfcDirection* IfcAxis2Placement3D::RefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(2)); }
bool IfcAxis2Placement3D::is(Type::Enum v) const { return v == Type::IfcAxis2Placement3D || IfcPlacement::is(v); }
Type::Enum IfcAxis2Placement3D::type() const { return Type::IfcAxis2Placement3D; }
Type::Enum IfcAxis2Placement3D::Class() { return Type::IfcAxis2Placement3D; }
IfcAxis2Placement3D::IfcAxis2Placement3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcAxis2Placement3D)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBSplineCurve
int IfcBSplineCurve::Degree() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcBSplineCurve::ControlPointsList() { RETURN_AS_LIST(IfcCartesianPoint,1) }
IfcBSplineCurveForm::IfcBSplineCurveForm IfcBSplineCurve::CurveForm() { return IfcBSplineCurveForm::FromString(*entity->getArgument(2)); }
bool IfcBSplineCurve::ClosedCurve() { return *entity->getArgument(3); }
bool IfcBSplineCurve::SelfIntersect() { return *entity->getArgument(4); }
bool IfcBSplineCurve::is(Type::Enum v) const { return v == Type::IfcBSplineCurve || IfcBoundedCurve::is(v); }
Type::Enum IfcBSplineCurve::type() const { return Type::IfcBSplineCurve; }
Type::Enum IfcBSplineCurve::Class() { return Type::IfcBSplineCurve; }
IfcBSplineCurve::IfcBSplineCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcBSplineCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBeam
bool IfcBeam::is(Type::Enum v) const { return v == Type::IfcBeam || IfcBuildingElement::is(v); }
Type::Enum IfcBeam::type() const { return Type::IfcBeam; }
Type::Enum IfcBeam::Class() { return Type::IfcBeam; }
IfcBeam::IfcBeam(IfcAbstractEntityPtr e) { if (!is(Type::IfcBeam)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBeamType
IfcBeamTypeEnum::IfcBeamTypeEnum IfcBeamType::PredefinedType() { return IfcBeamTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcBeamType::is(Type::Enum v) const { return v == Type::IfcBeamType || IfcBuildingElementType::is(v); }
Type::Enum IfcBeamType::type() const { return Type::IfcBeamType; }
Type::Enum IfcBeamType::Class() { return Type::IfcBeamType; }
IfcBeamType::IfcBeamType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBeamType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBezierCurve
bool IfcBezierCurve::is(Type::Enum v) const { return v == Type::IfcBezierCurve || IfcBSplineCurve::is(v); }
Type::Enum IfcBezierCurve::type() const { return Type::IfcBezierCurve; }
Type::Enum IfcBezierCurve::Class() { return Type::IfcBezierCurve; }
IfcBezierCurve::IfcBezierCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcBezierCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBlobTexture
IfcIdentifier IfcBlobTexture::RasterFormat() { return *entity->getArgument(4); }
bool IfcBlobTexture::RasterCode() { return *entity->getArgument(5); }
bool IfcBlobTexture::is(Type::Enum v) const { return v == Type::IfcBlobTexture || IfcSurfaceTexture::is(v); }
Type::Enum IfcBlobTexture::type() const { return Type::IfcBlobTexture; }
Type::Enum IfcBlobTexture::Class() { return Type::IfcBlobTexture; }
IfcBlobTexture::IfcBlobTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcBlobTexture)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBlock
IfcPositiveLengthMeasure IfcBlock::XLength() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcBlock::YLength() { return *entity->getArgument(2); }
IfcPositiveLengthMeasure IfcBlock::ZLength() { return *entity->getArgument(3); }
bool IfcBlock::is(Type::Enum v) const { return v == Type::IfcBlock || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcBlock::type() const { return Type::IfcBlock; }
Type::Enum IfcBlock::Class() { return Type::IfcBlock; }
IfcBlock::IfcBlock(IfcAbstractEntityPtr e) { if (!is(Type::IfcBlock)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoilerType
IfcBoilerTypeEnum::IfcBoilerTypeEnum IfcBoilerType::PredefinedType() { return IfcBoilerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcBoilerType::is(Type::Enum v) const { return v == Type::IfcBoilerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcBoilerType::type() const { return Type::IfcBoilerType; }
Type::Enum IfcBoilerType::Class() { return Type::IfcBoilerType; }
IfcBoilerType::IfcBoilerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoilerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBooleanClippingResult
bool IfcBooleanClippingResult::is(Type::Enum v) const { return v == Type::IfcBooleanClippingResult || IfcBooleanResult::is(v); }
Type::Enum IfcBooleanClippingResult::type() const { return Type::IfcBooleanClippingResult; }
Type::Enum IfcBooleanClippingResult::Class() { return Type::IfcBooleanClippingResult; }
IfcBooleanClippingResult::IfcBooleanClippingResult(IfcAbstractEntityPtr e) { if (!is(Type::IfcBooleanClippingResult)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBooleanResult
IfcBooleanOperator::IfcBooleanOperator IfcBooleanResult::Operator() { return IfcBooleanOperator::FromString(*entity->getArgument(0)); }
IfcBooleanOperand IfcBooleanResult::FirstOperand() { return *entity->getArgument(1); }
IfcBooleanOperand IfcBooleanResult::SecondOperand() { return *entity->getArgument(2); }
bool IfcBooleanResult::is(Type::Enum v) const { return v == Type::IfcBooleanResult || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcBooleanResult::type() const { return Type::IfcBooleanResult; }
Type::Enum IfcBooleanResult::Class() { return Type::IfcBooleanResult; }
IfcBooleanResult::IfcBooleanResult(IfcAbstractEntityPtr e) { if (!is(Type::IfcBooleanResult)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundaryCondition
bool IfcBoundaryCondition::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcBoundaryCondition::Name() { return *entity->getArgument(0); }
bool IfcBoundaryCondition::is(Type::Enum v) const { return v == Type::IfcBoundaryCondition; }
Type::Enum IfcBoundaryCondition::type() const { return Type::IfcBoundaryCondition; }
Type::Enum IfcBoundaryCondition::Class() { return Type::IfcBoundaryCondition; }
IfcBoundaryCondition::IfcBoundaryCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundaryEdgeCondition
bool IfcBoundaryEdgeCondition::hasLinearStiffnessByLengthX() { return !entity->getArgument(1)->isNull(); }
IfcModulusOfLinearSubgradeReactionMeasure IfcBoundaryEdgeCondition::LinearStiffnessByLengthX() { return *entity->getArgument(1); }
bool IfcBoundaryEdgeCondition::hasLinearStiffnessByLengthY() { return !entity->getArgument(2)->isNull(); }
IfcModulusOfLinearSubgradeReactionMeasure IfcBoundaryEdgeCondition::LinearStiffnessByLengthY() { return *entity->getArgument(2); }
bool IfcBoundaryEdgeCondition::hasLinearStiffnessByLengthZ() { return !entity->getArgument(3)->isNull(); }
IfcModulusOfLinearSubgradeReactionMeasure IfcBoundaryEdgeCondition::LinearStiffnessByLengthZ() { return *entity->getArgument(3); }
bool IfcBoundaryEdgeCondition::hasRotationalStiffnessByLengthX() { return !entity->getArgument(4)->isNull(); }
IfcModulusOfRotationalSubgradeReactionMeasure IfcBoundaryEdgeCondition::RotationalStiffnessByLengthX() { return *entity->getArgument(4); }
bool IfcBoundaryEdgeCondition::hasRotationalStiffnessByLengthY() { return !entity->getArgument(5)->isNull(); }
IfcModulusOfRotationalSubgradeReactionMeasure IfcBoundaryEdgeCondition::RotationalStiffnessByLengthY() { return *entity->getArgument(5); }
bool IfcBoundaryEdgeCondition::hasRotationalStiffnessByLengthZ() { return !entity->getArgument(6)->isNull(); }
IfcModulusOfRotationalSubgradeReactionMeasure IfcBoundaryEdgeCondition::RotationalStiffnessByLengthZ() { return *entity->getArgument(6); }
bool IfcBoundaryEdgeCondition::is(Type::Enum v) const { return v == Type::IfcBoundaryEdgeCondition || IfcBoundaryCondition::is(v); }
Type::Enum IfcBoundaryEdgeCondition::type() const { return Type::IfcBoundaryEdgeCondition; }
Type::Enum IfcBoundaryEdgeCondition::Class() { return Type::IfcBoundaryEdgeCondition; }
IfcBoundaryEdgeCondition::IfcBoundaryEdgeCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryEdgeCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundaryFaceCondition
bool IfcBoundaryFaceCondition::hasLinearStiffnessByAreaX() { return !entity->getArgument(1)->isNull(); }
IfcModulusOfSubgradeReactionMeasure IfcBoundaryFaceCondition::LinearStiffnessByAreaX() { return *entity->getArgument(1); }
bool IfcBoundaryFaceCondition::hasLinearStiffnessByAreaY() { return !entity->getArgument(2)->isNull(); }
IfcModulusOfSubgradeReactionMeasure IfcBoundaryFaceCondition::LinearStiffnessByAreaY() { return *entity->getArgument(2); }
bool IfcBoundaryFaceCondition::hasLinearStiffnessByAreaZ() { return !entity->getArgument(3)->isNull(); }
IfcModulusOfSubgradeReactionMeasure IfcBoundaryFaceCondition::LinearStiffnessByAreaZ() { return *entity->getArgument(3); }
bool IfcBoundaryFaceCondition::is(Type::Enum v) const { return v == Type::IfcBoundaryFaceCondition || IfcBoundaryCondition::is(v); }
Type::Enum IfcBoundaryFaceCondition::type() const { return Type::IfcBoundaryFaceCondition; }
Type::Enum IfcBoundaryFaceCondition::Class() { return Type::IfcBoundaryFaceCondition; }
IfcBoundaryFaceCondition::IfcBoundaryFaceCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryFaceCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundaryNodeCondition
bool IfcBoundaryNodeCondition::hasLinearStiffnessX() { return !entity->getArgument(1)->isNull(); }
IfcLinearStiffnessMeasure IfcBoundaryNodeCondition::LinearStiffnessX() { return *entity->getArgument(1); }
bool IfcBoundaryNodeCondition::hasLinearStiffnessY() { return !entity->getArgument(2)->isNull(); }
IfcLinearStiffnessMeasure IfcBoundaryNodeCondition::LinearStiffnessY() { return *entity->getArgument(2); }
bool IfcBoundaryNodeCondition::hasLinearStiffnessZ() { return !entity->getArgument(3)->isNull(); }
IfcLinearStiffnessMeasure IfcBoundaryNodeCondition::LinearStiffnessZ() { return *entity->getArgument(3); }
bool IfcBoundaryNodeCondition::hasRotationalStiffnessX() { return !entity->getArgument(4)->isNull(); }
IfcRotationalStiffnessMeasure IfcBoundaryNodeCondition::RotationalStiffnessX() { return *entity->getArgument(4); }
bool IfcBoundaryNodeCondition::hasRotationalStiffnessY() { return !entity->getArgument(5)->isNull(); }
IfcRotationalStiffnessMeasure IfcBoundaryNodeCondition::RotationalStiffnessY() { return *entity->getArgument(5); }
bool IfcBoundaryNodeCondition::hasRotationalStiffnessZ() { return !entity->getArgument(6)->isNull(); }
IfcRotationalStiffnessMeasure IfcBoundaryNodeCondition::RotationalStiffnessZ() { return *entity->getArgument(6); }
bool IfcBoundaryNodeCondition::is(Type::Enum v) const { return v == Type::IfcBoundaryNodeCondition || IfcBoundaryCondition::is(v); }
Type::Enum IfcBoundaryNodeCondition::type() const { return Type::IfcBoundaryNodeCondition; }
Type::Enum IfcBoundaryNodeCondition::Class() { return Type::IfcBoundaryNodeCondition; }
IfcBoundaryNodeCondition::IfcBoundaryNodeCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryNodeCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundaryNodeConditionWarping
bool IfcBoundaryNodeConditionWarping::hasWarpingStiffness() { return !entity->getArgument(7)->isNull(); }
IfcWarpingMomentMeasure IfcBoundaryNodeConditionWarping::WarpingStiffness() { return *entity->getArgument(7); }
bool IfcBoundaryNodeConditionWarping::is(Type::Enum v) const { return v == Type::IfcBoundaryNodeConditionWarping || IfcBoundaryNodeCondition::is(v); }
Type::Enum IfcBoundaryNodeConditionWarping::type() const { return Type::IfcBoundaryNodeConditionWarping; }
Type::Enum IfcBoundaryNodeConditionWarping::Class() { return Type::IfcBoundaryNodeConditionWarping; }
IfcBoundaryNodeConditionWarping::IfcBoundaryNodeConditionWarping(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryNodeConditionWarping)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundedCurve
bool IfcBoundedCurve::is(Type::Enum v) const { return v == Type::IfcBoundedCurve || IfcCurve::is(v); }
Type::Enum IfcBoundedCurve::type() const { return Type::IfcBoundedCurve; }
Type::Enum IfcBoundedCurve::Class() { return Type::IfcBoundedCurve; }
IfcBoundedCurve::IfcBoundedCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundedCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundedSurface
bool IfcBoundedSurface::is(Type::Enum v) const { return v == Type::IfcBoundedSurface || IfcSurface::is(v); }
Type::Enum IfcBoundedSurface::type() const { return Type::IfcBoundedSurface; }
Type::Enum IfcBoundedSurface::Class() { return Type::IfcBoundedSurface; }
IfcBoundedSurface::IfcBoundedSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundedSurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoundingBox
IfcCartesianPoint* IfcBoundingBox::Corner() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(0)); }
IfcPositiveLengthMeasure IfcBoundingBox::XDim() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcBoundingBox::YDim() { return *entity->getArgument(2); }
IfcPositiveLengthMeasure IfcBoundingBox::ZDim() { return *entity->getArgument(3); }
bool IfcBoundingBox::is(Type::Enum v) const { return v == Type::IfcBoundingBox || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcBoundingBox::type() const { return Type::IfcBoundingBox; }
Type::Enum IfcBoundingBox::Class() { return Type::IfcBoundingBox; }
IfcBoundingBox::IfcBoundingBox(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundingBox)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBoxedHalfSpace
IfcBoundingBox* IfcBoxedHalfSpace::Enclosure() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundingBox>(*entity->getArgument(2)); }
bool IfcBoxedHalfSpace::is(Type::Enum v) const { return v == Type::IfcBoxedHalfSpace || IfcHalfSpaceSolid::is(v); }
Type::Enum IfcBoxedHalfSpace::type() const { return Type::IfcBoxedHalfSpace; }
Type::Enum IfcBoxedHalfSpace::Class() { return Type::IfcBoxedHalfSpace; }
IfcBoxedHalfSpace::IfcBoxedHalfSpace(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoxedHalfSpace)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuilding
bool IfcBuilding::hasElevationOfRefHeight() { return !entity->getArgument(9)->isNull(); }
IfcLengthMeasure IfcBuilding::ElevationOfRefHeight() { return *entity->getArgument(9); }
bool IfcBuilding::hasElevationOfTerrain() { return !entity->getArgument(10)->isNull(); }
IfcLengthMeasure IfcBuilding::ElevationOfTerrain() { return *entity->getArgument(10); }
bool IfcBuilding::hasBuildingAddress() { return !entity->getArgument(11)->isNull(); }
IfcPostalAddress* IfcBuilding::BuildingAddress() { return reinterpret_pointer_cast<IfcBaseClass,IfcPostalAddress>(*entity->getArgument(11)); }
bool IfcBuilding::is(Type::Enum v) const { return v == Type::IfcBuilding || IfcSpatialStructureElement::is(v); }
Type::Enum IfcBuilding::type() const { return Type::IfcBuilding; }
Type::Enum IfcBuilding::Class() { return Type::IfcBuilding; }
IfcBuilding::IfcBuilding(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuilding)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuildingElement
bool IfcBuildingElement::is(Type::Enum v) const { return v == Type::IfcBuildingElement || IfcElement::is(v); }
Type::Enum IfcBuildingElement::type() const { return Type::IfcBuildingElement; }
Type::Enum IfcBuildingElement::Class() { return Type::IfcBuildingElement; }
IfcBuildingElement::IfcBuildingElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuildingElementComponent
bool IfcBuildingElementComponent::is(Type::Enum v) const { return v == Type::IfcBuildingElementComponent || IfcBuildingElement::is(v); }
Type::Enum IfcBuildingElementComponent::type() const { return Type::IfcBuildingElementComponent; }
Type::Enum IfcBuildingElementComponent::Class() { return Type::IfcBuildingElementComponent; }
IfcBuildingElementComponent::IfcBuildingElementComponent(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementComponent)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuildingElementPart
bool IfcBuildingElementPart::is(Type::Enum v) const { return v == Type::IfcBuildingElementPart || IfcBuildingElementComponent::is(v); }
Type::Enum IfcBuildingElementPart::type() const { return Type::IfcBuildingElementPart; }
Type::Enum IfcBuildingElementPart::Class() { return Type::IfcBuildingElementPart; }
IfcBuildingElementPart::IfcBuildingElementPart(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementPart)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuildingElementProxy
bool IfcBuildingElementProxy::hasCompositionType() { return !entity->getArgument(8)->isNull(); }
IfcElementCompositionEnum::IfcElementCompositionEnum IfcBuildingElementProxy::CompositionType() { return IfcElementCompositionEnum::FromString(*entity->getArgument(8)); }
bool IfcBuildingElementProxy::is(Type::Enum v) const { return v == Type::IfcBuildingElementProxy || IfcBuildingElement::is(v); }
Type::Enum IfcBuildingElementProxy::type() const { return Type::IfcBuildingElementProxy; }
Type::Enum IfcBuildingElementProxy::Class() { return Type::IfcBuildingElementProxy; }
IfcBuildingElementProxy::IfcBuildingElementProxy(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementProxy)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuildingElementProxyType
IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyTypeEnum IfcBuildingElementProxyType::PredefinedType() { return IfcBuildingElementProxyTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcBuildingElementProxyType::is(Type::Enum v) const { return v == Type::IfcBuildingElementProxyType || IfcBuildingElementType::is(v); }
Type::Enum IfcBuildingElementProxyType::type() const { return Type::IfcBuildingElementProxyType; }
Type::Enum IfcBuildingElementProxyType::Class() { return Type::IfcBuildingElementProxyType; }
IfcBuildingElementProxyType::IfcBuildingElementProxyType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementProxyType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuildingElementType
bool IfcBuildingElementType::is(Type::Enum v) const { return v == Type::IfcBuildingElementType || IfcElementType::is(v); }
Type::Enum IfcBuildingElementType::type() const { return Type::IfcBuildingElementType; }
Type::Enum IfcBuildingElementType::Class() { return Type::IfcBuildingElementType; }
IfcBuildingElementType::IfcBuildingElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcBuildingStorey
bool IfcBuildingStorey::hasElevation() { return !entity->getArgument(9)->isNull(); }
IfcLengthMeasure IfcBuildingStorey::Elevation() { return *entity->getArgument(9); }
bool IfcBuildingStorey::is(Type::Enum v) const { return v == Type::IfcBuildingStorey || IfcSpatialStructureElement::is(v); }
Type::Enum IfcBuildingStorey::type() const { return Type::IfcBuildingStorey; }
Type::Enum IfcBuildingStorey::Class() { return Type::IfcBuildingStorey; }
IfcBuildingStorey::IfcBuildingStorey(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingStorey)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCShapeProfileDef
IfcPositiveLengthMeasure IfcCShapeProfileDef::Depth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::Width() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::WallThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::Girth() { return *entity->getArgument(6); }
bool IfcCShapeProfileDef::hasInternalFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::InternalFilletRadius() { return *entity->getArgument(7); }
bool IfcCShapeProfileDef::hasCentreOfGravityInX() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::CentreOfGravityInX() { return *entity->getArgument(8); }
bool IfcCShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcCShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCShapeProfileDef::type() const { return Type::IfcCShapeProfileDef; }
Type::Enum IfcCShapeProfileDef::Class() { return Type::IfcCShapeProfileDef; }
IfcCShapeProfileDef::IfcCShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCableCarrierFittingType
IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingTypeEnum IfcCableCarrierFittingType::PredefinedType() { return IfcCableCarrierFittingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCableCarrierFittingType::is(Type::Enum v) const { return v == Type::IfcCableCarrierFittingType || IfcFlowFittingType::is(v); }
Type::Enum IfcCableCarrierFittingType::type() const { return Type::IfcCableCarrierFittingType; }
Type::Enum IfcCableCarrierFittingType::Class() { return Type::IfcCableCarrierFittingType; }
IfcCableCarrierFittingType::IfcCableCarrierFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCableCarrierFittingType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCableCarrierSegmentType
IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentTypeEnum IfcCableCarrierSegmentType::PredefinedType() { return IfcCableCarrierSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCableCarrierSegmentType::is(Type::Enum v) const { return v == Type::IfcCableCarrierSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcCableCarrierSegmentType::type() const { return Type::IfcCableCarrierSegmentType; }
Type::Enum IfcCableCarrierSegmentType::Class() { return Type::IfcCableCarrierSegmentType; }
IfcCableCarrierSegmentType::IfcCableCarrierSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCableCarrierSegmentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCableSegmentType
IfcCableSegmentTypeEnum::IfcCableSegmentTypeEnum IfcCableSegmentType::PredefinedType() { return IfcCableSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCableSegmentType::is(Type::Enum v) const { return v == Type::IfcCableSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcCableSegmentType::type() const { return Type::IfcCableSegmentType; }
Type::Enum IfcCableSegmentType::Class() { return Type::IfcCableSegmentType; }
IfcCableSegmentType::IfcCableSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCableSegmentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCalendarDate
IfcDayInMonthNumber IfcCalendarDate::DayComponent() { return *entity->getArgument(0); }
IfcMonthInYearNumber IfcCalendarDate::MonthComponent() { return *entity->getArgument(1); }
IfcYearNumber IfcCalendarDate::YearComponent() { return *entity->getArgument(2); }
bool IfcCalendarDate::is(Type::Enum v) const { return v == Type::IfcCalendarDate; }
Type::Enum IfcCalendarDate::type() const { return Type::IfcCalendarDate; }
Type::Enum IfcCalendarDate::Class() { return Type::IfcCalendarDate; }
IfcCalendarDate::IfcCalendarDate(IfcAbstractEntityPtr e) { if (!is(Type::IfcCalendarDate)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCartesianPoint
std::vector<IfcLengthMeasure> /*[1:3]*/ IfcCartesianPoint::Coordinates() { return *entity->getArgument(0); }
bool IfcCartesianPoint::is(Type::Enum v) const { return v == Type::IfcCartesianPoint || IfcPoint::is(v); }
Type::Enum IfcCartesianPoint::type() const { return Type::IfcCartesianPoint; }
Type::Enum IfcCartesianPoint::Class() { return Type::IfcCartesianPoint; }
IfcCartesianPoint::IfcCartesianPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianPoint)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCartesianTransformationOperator
bool IfcCartesianTransformationOperator::hasAxis1() { return !entity->getArgument(0)->isNull(); }
IfcDirection* IfcCartesianTransformationOperator::Axis1() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(0)); }
bool IfcCartesianTransformationOperator::hasAxis2() { return !entity->getArgument(1)->isNull(); }
IfcDirection* IfcCartesianTransformationOperator::Axis2() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
IfcCartesianPoint* IfcCartesianTransformationOperator::LocalOrigin() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(2)); }
bool IfcCartesianTransformationOperator::hasScale() { return !entity->getArgument(3)->isNull(); }
double IfcCartesianTransformationOperator::Scale() { return *entity->getArgument(3); }
bool IfcCartesianTransformationOperator::is(Type::Enum v) const { return v == Type::IfcCartesianTransformationOperator || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCartesianTransformationOperator::type() const { return Type::IfcCartesianTransformationOperator; }
Type::Enum IfcCartesianTransformationOperator::Class() { return Type::IfcCartesianTransformationOperator; }
IfcCartesianTransformationOperator::IfcCartesianTransformationOperator(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCartesianTransformationOperator2D
bool IfcCartesianTransformationOperator2D::is(Type::Enum v) const { return v == Type::IfcCartesianTransformationOperator2D || IfcCartesianTransformationOperator::is(v); }
Type::Enum IfcCartesianTransformationOperator2D::type() const { return Type::IfcCartesianTransformationOperator2D; }
Type::Enum IfcCartesianTransformationOperator2D::Class() { return Type::IfcCartesianTransformationOperator2D; }
IfcCartesianTransformationOperator2D::IfcCartesianTransformationOperator2D(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator2D)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCartesianTransformationOperator2DnonUniform
bool IfcCartesianTransformationOperator2DnonUniform::hasScale2() { return !entity->getArgument(4)->isNull(); }
double IfcCartesianTransformationOperator2DnonUniform::Scale2() { return *entity->getArgument(4); }
bool IfcCartesianTransformationOperator2DnonUniform::is(Type::Enum v) const { return v == Type::IfcCartesianTransformationOperator2DnonUniform || IfcCartesianTransformationOperator2D::is(v); }
Type::Enum IfcCartesianTransformationOperator2DnonUniform::type() const { return Type::IfcCartesianTransformationOperator2DnonUniform; }
Type::Enum IfcCartesianTransformationOperator2DnonUniform::Class() { return Type::IfcCartesianTransformationOperator2DnonUniform; }
IfcCartesianTransformationOperator2DnonUniform::IfcCartesianTransformationOperator2DnonUniform(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator2DnonUniform)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCartesianTransformationOperator3D
bool IfcCartesianTransformationOperator3D::hasAxis3() { return !entity->getArgument(4)->isNull(); }
IfcDirection* IfcCartesianTransformationOperator3D::Axis3() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(4)); }
bool IfcCartesianTransformationOperator3D::is(Type::Enum v) const { return v == Type::IfcCartesianTransformationOperator3D || IfcCartesianTransformationOperator::is(v); }
Type::Enum IfcCartesianTransformationOperator3D::type() const { return Type::IfcCartesianTransformationOperator3D; }
Type::Enum IfcCartesianTransformationOperator3D::Class() { return Type::IfcCartesianTransformationOperator3D; }
IfcCartesianTransformationOperator3D::IfcCartesianTransformationOperator3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator3D)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCartesianTransformationOperator3DnonUniform
bool IfcCartesianTransformationOperator3DnonUniform::hasScale2() { return !entity->getArgument(5)->isNull(); }
double IfcCartesianTransformationOperator3DnonUniform::Scale2() { return *entity->getArgument(5); }
bool IfcCartesianTransformationOperator3DnonUniform::hasScale3() { return !entity->getArgument(6)->isNull(); }
double IfcCartesianTransformationOperator3DnonUniform::Scale3() { return *entity->getArgument(6); }
bool IfcCartesianTransformationOperator3DnonUniform::is(Type::Enum v) const { return v == Type::IfcCartesianTransformationOperator3DnonUniform || IfcCartesianTransformationOperator3D::is(v); }
Type::Enum IfcCartesianTransformationOperator3DnonUniform::type() const { return Type::IfcCartesianTransformationOperator3DnonUniform; }
Type::Enum IfcCartesianTransformationOperator3DnonUniform::Class() { return Type::IfcCartesianTransformationOperator3DnonUniform; }
IfcCartesianTransformationOperator3DnonUniform::IfcCartesianTransformationOperator3DnonUniform(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator3DnonUniform)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCenterLineProfileDef
IfcPositiveLengthMeasure IfcCenterLineProfileDef::Thickness() { return *entity->getArgument(3); }
bool IfcCenterLineProfileDef::is(Type::Enum v) const { return v == Type::IfcCenterLineProfileDef || IfcArbitraryOpenProfileDef::is(v); }
Type::Enum IfcCenterLineProfileDef::type() const { return Type::IfcCenterLineProfileDef; }
Type::Enum IfcCenterLineProfileDef::Class() { return Type::IfcCenterLineProfileDef; }
IfcCenterLineProfileDef::IfcCenterLineProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCenterLineProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcChamferEdgeFeature
bool IfcChamferEdgeFeature::hasWidth() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcChamferEdgeFeature::Width() { return *entity->getArgument(9); }
bool IfcChamferEdgeFeature::hasHeight() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcChamferEdgeFeature::Height() { return *entity->getArgument(10); }
bool IfcChamferEdgeFeature::is(Type::Enum v) const { return v == Type::IfcChamferEdgeFeature || IfcEdgeFeature::is(v); }
Type::Enum IfcChamferEdgeFeature::type() const { return Type::IfcChamferEdgeFeature; }
Type::Enum IfcChamferEdgeFeature::Class() { return Type::IfcChamferEdgeFeature; }
IfcChamferEdgeFeature::IfcChamferEdgeFeature(IfcAbstractEntityPtr e) { if (!is(Type::IfcChamferEdgeFeature)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcChillerType
IfcChillerTypeEnum::IfcChillerTypeEnum IfcChillerType::PredefinedType() { return IfcChillerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcChillerType::is(Type::Enum v) const { return v == Type::IfcChillerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcChillerType::type() const { return Type::IfcChillerType; }
Type::Enum IfcChillerType::Class() { return Type::IfcChillerType; }
IfcChillerType::IfcChillerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcChillerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCircle
IfcPositiveLengthMeasure IfcCircle::Radius() { return *entity->getArgument(1); }
bool IfcCircle::is(Type::Enum v) const { return v == Type::IfcCircle || IfcConic::is(v); }
Type::Enum IfcCircle::type() const { return Type::IfcCircle; }
Type::Enum IfcCircle::Class() { return Type::IfcCircle; }
IfcCircle::IfcCircle(IfcAbstractEntityPtr e) { if (!is(Type::IfcCircle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCircleHollowProfileDef
IfcPositiveLengthMeasure IfcCircleHollowProfileDef::WallThickness() { return *entity->getArgument(4); }
bool IfcCircleHollowProfileDef::is(Type::Enum v) const { return v == Type::IfcCircleHollowProfileDef || IfcCircleProfileDef::is(v); }
Type::Enum IfcCircleHollowProfileDef::type() const { return Type::IfcCircleHollowProfileDef; }
Type::Enum IfcCircleHollowProfileDef::Class() { return Type::IfcCircleHollowProfileDef; }
IfcCircleHollowProfileDef::IfcCircleHollowProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCircleHollowProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCircleProfileDef
IfcPositiveLengthMeasure IfcCircleProfileDef::Radius() { return *entity->getArgument(3); }
bool IfcCircleProfileDef::is(Type::Enum v) const { return v == Type::IfcCircleProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCircleProfileDef::type() const { return Type::IfcCircleProfileDef; }
Type::Enum IfcCircleProfileDef::Class() { return Type::IfcCircleProfileDef; }
IfcCircleProfileDef::IfcCircleProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCircleProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcClassification
IfcLabel IfcClassification::Source() { return *entity->getArgument(0); }
IfcLabel IfcClassification::Edition() { return *entity->getArgument(1); }
bool IfcClassification::hasEditionDate() { return !entity->getArgument(2)->isNull(); }
IfcCalendarDate* IfcClassification::EditionDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(2)); }
IfcLabel IfcClassification::Name() { return *entity->getArgument(3); }
IfcClassificationItem::list IfcClassification::Contains() { RETURN_INVERSE(IfcClassificationItem) }
bool IfcClassification::is(Type::Enum v) const { return v == Type::IfcClassification; }
Type::Enum IfcClassification::type() const { return Type::IfcClassification; }
Type::Enum IfcClassification::Class() { return Type::IfcClassification; }
IfcClassification::IfcClassification(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassification)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcClassificationItem
IfcClassificationNotationFacet* IfcClassificationItem::Notation() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassificationNotationFacet>(*entity->getArgument(0)); }
bool IfcClassificationItem::hasItemOf() { return !entity->getArgument(1)->isNull(); }
IfcClassification* IfcClassificationItem::ItemOf() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassification>(*entity->getArgument(1)); }
IfcLabel IfcClassificationItem::Title() { return *entity->getArgument(2); }
IfcClassificationItemRelationship::list IfcClassificationItem::IsClassifiedItemIn() { RETURN_INVERSE(IfcClassificationItemRelationship) }
IfcClassificationItemRelationship::list IfcClassificationItem::IsClassifyingItemIn() { RETURN_INVERSE(IfcClassificationItemRelationship) }
bool IfcClassificationItem::is(Type::Enum v) const { return v == Type::IfcClassificationItem; }
Type::Enum IfcClassificationItem::type() const { return Type::IfcClassificationItem; }
Type::Enum IfcClassificationItem::Class() { return Type::IfcClassificationItem; }
IfcClassificationItem::IfcClassificationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcClassificationItemRelationship
IfcClassificationItem* IfcClassificationItemRelationship::RelatingItem() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassificationItem>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > IfcClassificationItemRelationship::RelatedItems() { RETURN_AS_LIST(IfcClassificationItem,1) }
bool IfcClassificationItemRelationship::is(Type::Enum v) const { return v == Type::IfcClassificationItemRelationship; }
Type::Enum IfcClassificationItemRelationship::type() const { return Type::IfcClassificationItemRelationship; }
Type::Enum IfcClassificationItemRelationship::Class() { return Type::IfcClassificationItemRelationship; }
IfcClassificationItemRelationship::IfcClassificationItemRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationItemRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcClassificationNotation
SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotationFacet> > IfcClassificationNotation::NotationFacets() { RETURN_AS_LIST(IfcClassificationNotationFacet,0) }
bool IfcClassificationNotation::is(Type::Enum v) const { return v == Type::IfcClassificationNotation; }
Type::Enum IfcClassificationNotation::type() const { return Type::IfcClassificationNotation; }
Type::Enum IfcClassificationNotation::Class() { return Type::IfcClassificationNotation; }
IfcClassificationNotation::IfcClassificationNotation(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationNotation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcClassificationNotationFacet
IfcLabel IfcClassificationNotationFacet::NotationValue() { return *entity->getArgument(0); }
bool IfcClassificationNotationFacet::is(Type::Enum v) const { return v == Type::IfcClassificationNotationFacet; }
Type::Enum IfcClassificationNotationFacet::type() const { return Type::IfcClassificationNotationFacet; }
Type::Enum IfcClassificationNotationFacet::Class() { return Type::IfcClassificationNotationFacet; }
IfcClassificationNotationFacet::IfcClassificationNotationFacet(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationNotationFacet)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcClassificationReference
bool IfcClassificationReference::hasReferencedSource() { return !entity->getArgument(3)->isNull(); }
IfcClassification* IfcClassificationReference::ReferencedSource() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassification>(*entity->getArgument(3)); }
bool IfcClassificationReference::is(Type::Enum v) const { return v == Type::IfcClassificationReference || IfcExternalReference::is(v); }
Type::Enum IfcClassificationReference::type() const { return Type::IfcClassificationReference; }
Type::Enum IfcClassificationReference::Class() { return Type::IfcClassificationReference; }
IfcClassificationReference::IfcClassificationReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationReference)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcClosedShell
bool IfcClosedShell::is(Type::Enum v) const { return v == Type::IfcClosedShell || IfcConnectedFaceSet::is(v); }
Type::Enum IfcClosedShell::type() const { return Type::IfcClosedShell; }
Type::Enum IfcClosedShell::Class() { return Type::IfcClosedShell; }
IfcClosedShell::IfcClosedShell(IfcAbstractEntityPtr e) { if (!is(Type::IfcClosedShell)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCoilType
IfcCoilTypeEnum::IfcCoilTypeEnum IfcCoilType::PredefinedType() { return IfcCoilTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCoilType::is(Type::Enum v) const { return v == Type::IfcCoilType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCoilType::type() const { return Type::IfcCoilType; }
Type::Enum IfcCoilType::Class() { return Type::IfcCoilType; }
IfcCoilType::IfcCoilType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoilType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcColourRgb
IfcNormalisedRatioMeasure IfcColourRgb::Red() { return *entity->getArgument(1); }
IfcNormalisedRatioMeasure IfcColourRgb::Green() { return *entity->getArgument(2); }
IfcNormalisedRatioMeasure IfcColourRgb::Blue() { return *entity->getArgument(3); }
bool IfcColourRgb::is(Type::Enum v) const { return v == Type::IfcColourRgb || IfcColourSpecification::is(v); }
Type::Enum IfcColourRgb::type() const { return Type::IfcColourRgb; }
Type::Enum IfcColourRgb::Class() { return Type::IfcColourRgb; }
IfcColourRgb::IfcColourRgb(IfcAbstractEntityPtr e) { if (!is(Type::IfcColourRgb)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcColourSpecification
bool IfcColourSpecification::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcColourSpecification::Name() { return *entity->getArgument(0); }
bool IfcColourSpecification::is(Type::Enum v) const { return v == Type::IfcColourSpecification; }
Type::Enum IfcColourSpecification::type() const { return Type::IfcColourSpecification; }
Type::Enum IfcColourSpecification::Class() { return Type::IfcColourSpecification; }
IfcColourSpecification::IfcColourSpecification(IfcAbstractEntityPtr e) { if (!is(Type::IfcColourSpecification)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcColumn
bool IfcColumn::is(Type::Enum v) const { return v == Type::IfcColumn || IfcBuildingElement::is(v); }
Type::Enum IfcColumn::type() const { return Type::IfcColumn; }
Type::Enum IfcColumn::Class() { return Type::IfcColumn; }
IfcColumn::IfcColumn(IfcAbstractEntityPtr e) { if (!is(Type::IfcColumn)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcColumnType
IfcColumnTypeEnum::IfcColumnTypeEnum IfcColumnType::PredefinedType() { return IfcColumnTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcColumnType::is(Type::Enum v) const { return v == Type::IfcColumnType || IfcBuildingElementType::is(v); }
Type::Enum IfcColumnType::type() const { return Type::IfcColumnType; }
Type::Enum IfcColumnType::Class() { return Type::IfcColumnType; }
IfcColumnType::IfcColumnType(IfcAbstractEntityPtr e) { if (!is(Type::IfcColumnType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcComplexProperty
IfcIdentifier IfcComplexProperty::UsageName() { return *entity->getArgument(2); }
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcComplexProperty::HasProperties() { RETURN_AS_LIST(IfcProperty,3) }
bool IfcComplexProperty::is(Type::Enum v) const { return v == Type::IfcComplexProperty || IfcProperty::is(v); }
Type::Enum IfcComplexProperty::type() const { return Type::IfcComplexProperty; }
Type::Enum IfcComplexProperty::Class() { return Type::IfcComplexProperty; }
IfcComplexProperty::IfcComplexProperty(IfcAbstractEntityPtr e) { if (!is(Type::IfcComplexProperty)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCompositeCurve
SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurveSegment> > IfcCompositeCurve::Segments() { RETURN_AS_LIST(IfcCompositeCurveSegment,0) }
bool IfcCompositeCurve::SelfIntersect() { return *entity->getArgument(1); }
bool IfcCompositeCurve::is(Type::Enum v) const { return v == Type::IfcCompositeCurve || IfcBoundedCurve::is(v); }
Type::Enum IfcCompositeCurve::type() const { return Type::IfcCompositeCurve; }
Type::Enum IfcCompositeCurve::Class() { return Type::IfcCompositeCurve; }
IfcCompositeCurve::IfcCompositeCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompositeCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCompositeCurveSegment
IfcTransitionCode::IfcTransitionCode IfcCompositeCurveSegment::Transition() { return IfcTransitionCode::FromString(*entity->getArgument(0)); }
bool IfcCompositeCurveSegment::SameSense() { return *entity->getArgument(1); }
IfcCurve* IfcCompositeCurveSegment::ParentCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
IfcCompositeCurve::list IfcCompositeCurveSegment::UsingCurves() { RETURN_INVERSE(IfcCompositeCurve) }
bool IfcCompositeCurveSegment::is(Type::Enum v) const { return v == Type::IfcCompositeCurveSegment || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCompositeCurveSegment::type() const { return Type::IfcCompositeCurveSegment; }
Type::Enum IfcCompositeCurveSegment::Class() { return Type::IfcCompositeCurveSegment; }
IfcCompositeCurveSegment::IfcCompositeCurveSegment(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompositeCurveSegment)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCompositeProfileDef
SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > IfcCompositeProfileDef::Profiles() { RETURN_AS_LIST(IfcProfileDef,2) }
bool IfcCompositeProfileDef::hasLabel() { return !entity->getArgument(3)->isNull(); }
IfcLabel IfcCompositeProfileDef::Label() { return *entity->getArgument(3); }
bool IfcCompositeProfileDef::is(Type::Enum v) const { return v == Type::IfcCompositeProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcCompositeProfileDef::type() const { return Type::IfcCompositeProfileDef; }
Type::Enum IfcCompositeProfileDef::Class() { return Type::IfcCompositeProfileDef; }
IfcCompositeProfileDef::IfcCompositeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompositeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCompressorType
IfcCompressorTypeEnum::IfcCompressorTypeEnum IfcCompressorType::PredefinedType() { return IfcCompressorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCompressorType::is(Type::Enum v) const { return v == Type::IfcCompressorType || IfcFlowMovingDeviceType::is(v); }
Type::Enum IfcCompressorType::type() const { return Type::IfcCompressorType; }
Type::Enum IfcCompressorType::Class() { return Type::IfcCompressorType; }
IfcCompressorType::IfcCompressorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompressorType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCondenserType
IfcCondenserTypeEnum::IfcCondenserTypeEnum IfcCondenserType::PredefinedType() { return IfcCondenserTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCondenserType::is(Type::Enum v) const { return v == Type::IfcCondenserType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCondenserType::type() const { return Type::IfcCondenserType; }
Type::Enum IfcCondenserType::Class() { return Type::IfcCondenserType; }
IfcCondenserType::IfcCondenserType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCondenserType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCondition
bool IfcCondition::is(Type::Enum v) const { return v == Type::IfcCondition || IfcGroup::is(v); }
Type::Enum IfcCondition::type() const { return Type::IfcCondition; }
Type::Enum IfcCondition::Class() { return Type::IfcCondition; }
IfcCondition::IfcCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConditionCriterion
IfcConditionCriterionSelect IfcConditionCriterion::Criterion() { return *entity->getArgument(5); }
IfcDateTimeSelect IfcConditionCriterion::CriterionDateTime() { return *entity->getArgument(6); }
bool IfcConditionCriterion::is(Type::Enum v) const { return v == Type::IfcConditionCriterion || IfcControl::is(v); }
Type::Enum IfcConditionCriterion::type() const { return Type::IfcConditionCriterion; }
Type::Enum IfcConditionCriterion::Class() { return Type::IfcConditionCriterion; }
IfcConditionCriterion::IfcConditionCriterion(IfcAbstractEntityPtr e) { if (!is(Type::IfcConditionCriterion)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConic
IfcAxis2Placement IfcConic::Position() { return *entity->getArgument(0); }
bool IfcConic::is(Type::Enum v) const { return v == Type::IfcConic || IfcCurve::is(v); }
Type::Enum IfcConic::type() const { return Type::IfcConic; }
Type::Enum IfcConic::Class() { return Type::IfcConic; }
IfcConic::IfcConic(IfcAbstractEntityPtr e) { if (!is(Type::IfcConic)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConnectedFaceSet
SHARED_PTR< IfcTemplatedEntityList<IfcFace> > IfcConnectedFaceSet::CfsFaces() { RETURN_AS_LIST(IfcFace,0) }
bool IfcConnectedFaceSet::is(Type::Enum v) const { return v == Type::IfcConnectedFaceSet || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcConnectedFaceSet::type() const { return Type::IfcConnectedFaceSet; }
Type::Enum IfcConnectedFaceSet::Class() { return Type::IfcConnectedFaceSet; }
IfcConnectedFaceSet::IfcConnectedFaceSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectedFaceSet)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConnectionCurveGeometry
IfcCurveOrEdgeCurve IfcConnectionCurveGeometry::CurveOnRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionCurveGeometry::hasCurveOnRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcCurveOrEdgeCurve IfcConnectionCurveGeometry::CurveOnRelatedElement() { return *entity->getArgument(1); }
bool IfcConnectionCurveGeometry::is(Type::Enum v) const { return v == Type::IfcConnectionCurveGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionCurveGeometry::type() const { return Type::IfcConnectionCurveGeometry; }
Type::Enum IfcConnectionCurveGeometry::Class() { return Type::IfcConnectionCurveGeometry; }
IfcConnectionCurveGeometry::IfcConnectionCurveGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionCurveGeometry)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConnectionGeometry
bool IfcConnectionGeometry::is(Type::Enum v) const { return v == Type::IfcConnectionGeometry; }
Type::Enum IfcConnectionGeometry::type() const { return Type::IfcConnectionGeometry; }
Type::Enum IfcConnectionGeometry::Class() { return Type::IfcConnectionGeometry; }
IfcConnectionGeometry::IfcConnectionGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionGeometry)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConnectionPointEccentricity
bool IfcConnectionPointEccentricity::hasEccentricityInX() { return !entity->getArgument(2)->isNull(); }
IfcLengthMeasure IfcConnectionPointEccentricity::EccentricityInX() { return *entity->getArgument(2); }
bool IfcConnectionPointEccentricity::hasEccentricityInY() { return !entity->getArgument(3)->isNull(); }
IfcLengthMeasure IfcConnectionPointEccentricity::EccentricityInY() { return *entity->getArgument(3); }
bool IfcConnectionPointEccentricity::hasEccentricityInZ() { return !entity->getArgument(4)->isNull(); }
IfcLengthMeasure IfcConnectionPointEccentricity::EccentricityInZ() { return *entity->getArgument(4); }
bool IfcConnectionPointEccentricity::is(Type::Enum v) const { return v == Type::IfcConnectionPointEccentricity || IfcConnectionPointGeometry::is(v); }
Type::Enum IfcConnectionPointEccentricity::type() const { return Type::IfcConnectionPointEccentricity; }
Type::Enum IfcConnectionPointEccentricity::Class() { return Type::IfcConnectionPointEccentricity; }
IfcConnectionPointEccentricity::IfcConnectionPointEccentricity(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionPointEccentricity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConnectionPointGeometry
IfcPointOrVertexPoint IfcConnectionPointGeometry::PointOnRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionPointGeometry::hasPointOnRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcPointOrVertexPoint IfcConnectionPointGeometry::PointOnRelatedElement() { return *entity->getArgument(1); }
bool IfcConnectionPointGeometry::is(Type::Enum v) const { return v == Type::IfcConnectionPointGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionPointGeometry::type() const { return Type::IfcConnectionPointGeometry; }
Type::Enum IfcConnectionPointGeometry::Class() { return Type::IfcConnectionPointGeometry; }
IfcConnectionPointGeometry::IfcConnectionPointGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionPointGeometry)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConnectionPortGeometry
IfcAxis2Placement IfcConnectionPortGeometry::LocationAtRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionPortGeometry::hasLocationAtRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcAxis2Placement IfcConnectionPortGeometry::LocationAtRelatedElement() { return *entity->getArgument(1); }
IfcProfileDef* IfcConnectionPortGeometry::ProfileOfPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(2)); }
bool IfcConnectionPortGeometry::is(Type::Enum v) const { return v == Type::IfcConnectionPortGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionPortGeometry::type() const { return Type::IfcConnectionPortGeometry; }
Type::Enum IfcConnectionPortGeometry::Class() { return Type::IfcConnectionPortGeometry; }
IfcConnectionPortGeometry::IfcConnectionPortGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionPortGeometry)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConnectionSurfaceGeometry
IfcSurfaceOrFaceSurface IfcConnectionSurfaceGeometry::SurfaceOnRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionSurfaceGeometry::hasSurfaceOnRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcSurfaceOrFaceSurface IfcConnectionSurfaceGeometry::SurfaceOnRelatedElement() { return *entity->getArgument(1); }
bool IfcConnectionSurfaceGeometry::is(Type::Enum v) const { return v == Type::IfcConnectionSurfaceGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionSurfaceGeometry::type() const { return Type::IfcConnectionSurfaceGeometry; }
Type::Enum IfcConnectionSurfaceGeometry::Class() { return Type::IfcConnectionSurfaceGeometry; }
IfcConnectionSurfaceGeometry::IfcConnectionSurfaceGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionSurfaceGeometry)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstraint
IfcLabel IfcConstraint::Name() { return *entity->getArgument(0); }
bool IfcConstraint::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcConstraint::Description() { return *entity->getArgument(1); }
IfcConstraintEnum::IfcConstraintEnum IfcConstraint::ConstraintGrade() { return IfcConstraintEnum::FromString(*entity->getArgument(2)); }
bool IfcConstraint::hasConstraintSource() { return !entity->getArgument(3)->isNull(); }
IfcLabel IfcConstraint::ConstraintSource() { return *entity->getArgument(3); }
bool IfcConstraint::hasCreatingActor() { return !entity->getArgument(4)->isNull(); }
IfcActorSelect IfcConstraint::CreatingActor() { return *entity->getArgument(4); }
bool IfcConstraint::hasCreationTime() { return !entity->getArgument(5)->isNull(); }
IfcDateTimeSelect IfcConstraint::CreationTime() { return *entity->getArgument(5); }
bool IfcConstraint::hasUserDefinedGrade() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcConstraint::UserDefinedGrade() { return *entity->getArgument(6); }
IfcConstraintClassificationRelationship::list IfcConstraint::ClassifiedAs() { RETURN_INVERSE(IfcConstraintClassificationRelationship) }
IfcConstraintRelationship::list IfcConstraint::RelatesConstraints() { RETURN_INVERSE(IfcConstraintRelationship) }
IfcConstraintRelationship::list IfcConstraint::IsRelatedWith() { RETURN_INVERSE(IfcConstraintRelationship) }
IfcPropertyConstraintRelationship::list IfcConstraint::PropertiesForConstraint() { RETURN_INVERSE(IfcPropertyConstraintRelationship) }
IfcConstraintAggregationRelationship::list IfcConstraint::Aggregates() { RETURN_INVERSE(IfcConstraintAggregationRelationship) }
IfcConstraintAggregationRelationship::list IfcConstraint::IsAggregatedIn() { RETURN_INVERSE(IfcConstraintAggregationRelationship) }
bool IfcConstraint::is(Type::Enum v) const { return v == Type::IfcConstraint; }
Type::Enum IfcConstraint::type() const { return Type::IfcConstraint; }
Type::Enum IfcConstraint::Class() { return Type::IfcConstraint; }
IfcConstraint::IfcConstraint(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraint)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstraintAggregationRelationship
bool IfcConstraintAggregationRelationship::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcConstraintAggregationRelationship::Name() { return *entity->getArgument(0); }
bool IfcConstraintAggregationRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcConstraintAggregationRelationship::Description() { return *entity->getArgument(1); }
IfcConstraint* IfcConstraintAggregationRelationship::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(2)); }
SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > IfcConstraintAggregationRelationship::RelatedConstraints() { RETURN_AS_LIST(IfcConstraint,3) }
IfcLogicalOperatorEnum::IfcLogicalOperatorEnum IfcConstraintAggregationRelationship::LogicalAggregator() { return IfcLogicalOperatorEnum::FromString(*entity->getArgument(4)); }
bool IfcConstraintAggregationRelationship::is(Type::Enum v) const { return v == Type::IfcConstraintAggregationRelationship; }
Type::Enum IfcConstraintAggregationRelationship::type() const { return Type::IfcConstraintAggregationRelationship; }
Type::Enum IfcConstraintAggregationRelationship::Class() { return Type::IfcConstraintAggregationRelationship; }
IfcConstraintAggregationRelationship::IfcConstraintAggregationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraintAggregationRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstraintClassificationRelationship
IfcConstraint* IfcConstraintClassificationRelationship::ClassifiedConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcConstraintClassificationRelationship::RelatedClassifications() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcConstraintClassificationRelationship::is(Type::Enum v) const { return v == Type::IfcConstraintClassificationRelationship; }
Type::Enum IfcConstraintClassificationRelationship::type() const { return Type::IfcConstraintClassificationRelationship; }
Type::Enum IfcConstraintClassificationRelationship::Class() { return Type::IfcConstraintClassificationRelationship; }
IfcConstraintClassificationRelationship::IfcConstraintClassificationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraintClassificationRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstraintRelationship
bool IfcConstraintRelationship::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcConstraintRelationship::Name() { return *entity->getArgument(0); }
bool IfcConstraintRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcConstraintRelationship::Description() { return *entity->getArgument(1); }
IfcConstraint* IfcConstraintRelationship::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(2)); }
SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > IfcConstraintRelationship::RelatedConstraints() { RETURN_AS_LIST(IfcConstraint,3) }
bool IfcConstraintRelationship::is(Type::Enum v) const { return v == Type::IfcConstraintRelationship; }
Type::Enum IfcConstraintRelationship::type() const { return Type::IfcConstraintRelationship; }
Type::Enum IfcConstraintRelationship::Class() { return Type::IfcConstraintRelationship; }
IfcConstraintRelationship::IfcConstraintRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraintRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstructionEquipmentResource
bool IfcConstructionEquipmentResource::is(Type::Enum v) const { return v == Type::IfcConstructionEquipmentResource || IfcConstructionResource::is(v); }
Type::Enum IfcConstructionEquipmentResource::type() const { return Type::IfcConstructionEquipmentResource; }
Type::Enum IfcConstructionEquipmentResource::Class() { return Type::IfcConstructionEquipmentResource; }
IfcConstructionEquipmentResource::IfcConstructionEquipmentResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionEquipmentResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstructionMaterialResource
bool IfcConstructionMaterialResource::hasSuppliers() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcConstructionMaterialResource::Suppliers() { RETURN_AS_LIST(IfcAbstractSelect,9) }
bool IfcConstructionMaterialResource::hasUsageRatio() { return !entity->getArgument(10)->isNull(); }
IfcRatioMeasure IfcConstructionMaterialResource::UsageRatio() { return *entity->getArgument(10); }
bool IfcConstructionMaterialResource::is(Type::Enum v) const { return v == Type::IfcConstructionMaterialResource || IfcConstructionResource::is(v); }
Type::Enum IfcConstructionMaterialResource::type() const { return Type::IfcConstructionMaterialResource; }
Type::Enum IfcConstructionMaterialResource::Class() { return Type::IfcConstructionMaterialResource; }
IfcConstructionMaterialResource::IfcConstructionMaterialResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionMaterialResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstructionProductResource
bool IfcConstructionProductResource::is(Type::Enum v) const { return v == Type::IfcConstructionProductResource || IfcConstructionResource::is(v); }
Type::Enum IfcConstructionProductResource::type() const { return Type::IfcConstructionProductResource; }
Type::Enum IfcConstructionProductResource::Class() { return Type::IfcConstructionProductResource; }
IfcConstructionProductResource::IfcConstructionProductResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionProductResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConstructionResource
bool IfcConstructionResource::hasResourceIdentifier() { return !entity->getArgument(5)->isNull(); }
IfcIdentifier IfcConstructionResource::ResourceIdentifier() { return *entity->getArgument(5); }
bool IfcConstructionResource::hasResourceGroup() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcConstructionResource::ResourceGroup() { return *entity->getArgument(6); }
bool IfcConstructionResource::hasResourceConsumption() { return !entity->getArgument(7)->isNull(); }
IfcResourceConsumptionEnum::IfcResourceConsumptionEnum IfcConstructionResource::ResourceConsumption() { return IfcResourceConsumptionEnum::FromString(*entity->getArgument(7)); }
bool IfcConstructionResource::hasBaseQuantity() { return !entity->getArgument(8)->isNull(); }
IfcMeasureWithUnit* IfcConstructionResource::BaseQuantity() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(8)); }
bool IfcConstructionResource::is(Type::Enum v) const { return v == Type::IfcConstructionResource || IfcResource::is(v); }
Type::Enum IfcConstructionResource::type() const { return Type::IfcConstructionResource; }
Type::Enum IfcConstructionResource::Class() { return Type::IfcConstructionResource; }
IfcConstructionResource::IfcConstructionResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcContextDependentUnit
IfcLabel IfcContextDependentUnit::Name() { return *entity->getArgument(2); }
bool IfcContextDependentUnit::is(Type::Enum v) const { return v == Type::IfcContextDependentUnit || IfcNamedUnit::is(v); }
Type::Enum IfcContextDependentUnit::type() const { return Type::IfcContextDependentUnit; }
Type::Enum IfcContextDependentUnit::Class() { return Type::IfcContextDependentUnit; }
IfcContextDependentUnit::IfcContextDependentUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcContextDependentUnit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcControl
IfcRelAssignsToControl::list IfcControl::Controls() { RETURN_INVERSE(IfcRelAssignsToControl) }
bool IfcControl::is(Type::Enum v) const { return v == Type::IfcControl || IfcObject::is(v); }
Type::Enum IfcControl::type() const { return Type::IfcControl; }
Type::Enum IfcControl::Class() { return Type::IfcControl; }
IfcControl::IfcControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcControl)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcControllerType
IfcControllerTypeEnum::IfcControllerTypeEnum IfcControllerType::PredefinedType() { return IfcControllerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcControllerType::is(Type::Enum v) const { return v == Type::IfcControllerType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcControllerType::type() const { return Type::IfcControllerType; }
Type::Enum IfcControllerType::Class() { return Type::IfcControllerType; }
IfcControllerType::IfcControllerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcControllerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcConversionBasedUnit
IfcLabel IfcConversionBasedUnit::Name() { return *entity->getArgument(2); }
IfcMeasureWithUnit* IfcConversionBasedUnit::ConversionFactor() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(3)); }
bool IfcConversionBasedUnit::is(Type::Enum v) const { return v == Type::IfcConversionBasedUnit || IfcNamedUnit::is(v); }
Type::Enum IfcConversionBasedUnit::type() const { return Type::IfcConversionBasedUnit; }
Type::Enum IfcConversionBasedUnit::Class() { return Type::IfcConversionBasedUnit; }
IfcConversionBasedUnit::IfcConversionBasedUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcConversionBasedUnit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCooledBeamType
IfcCooledBeamTypeEnum::IfcCooledBeamTypeEnum IfcCooledBeamType::PredefinedType() { return IfcCooledBeamTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCooledBeamType::is(Type::Enum v) const { return v == Type::IfcCooledBeamType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCooledBeamType::type() const { return Type::IfcCooledBeamType; }
Type::Enum IfcCooledBeamType::Class() { return Type::IfcCooledBeamType; }
IfcCooledBeamType::IfcCooledBeamType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCooledBeamType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCoolingTowerType
IfcCoolingTowerTypeEnum::IfcCoolingTowerTypeEnum IfcCoolingTowerType::PredefinedType() { return IfcCoolingTowerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCoolingTowerType::is(Type::Enum v) const { return v == Type::IfcCoolingTowerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCoolingTowerType::type() const { return Type::IfcCoolingTowerType; }
Type::Enum IfcCoolingTowerType::Class() { return Type::IfcCoolingTowerType; }
IfcCoolingTowerType::IfcCoolingTowerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoolingTowerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCoordinatedUniversalTimeOffset
IfcHourInDay IfcCoordinatedUniversalTimeOffset::HourOffset() { return *entity->getArgument(0); }
bool IfcCoordinatedUniversalTimeOffset::hasMinuteOffset() { return !entity->getArgument(1)->isNull(); }
IfcMinuteInHour IfcCoordinatedUniversalTimeOffset::MinuteOffset() { return *entity->getArgument(1); }
IfcAheadOrBehind::IfcAheadOrBehind IfcCoordinatedUniversalTimeOffset::Sense() { return IfcAheadOrBehind::FromString(*entity->getArgument(2)); }
bool IfcCoordinatedUniversalTimeOffset::is(Type::Enum v) const { return v == Type::IfcCoordinatedUniversalTimeOffset; }
Type::Enum IfcCoordinatedUniversalTimeOffset::type() const { return Type::IfcCoordinatedUniversalTimeOffset; }
Type::Enum IfcCoordinatedUniversalTimeOffset::Class() { return Type::IfcCoordinatedUniversalTimeOffset; }
IfcCoordinatedUniversalTimeOffset::IfcCoordinatedUniversalTimeOffset(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoordinatedUniversalTimeOffset)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCostItem
bool IfcCostItem::is(Type::Enum v) const { return v == Type::IfcCostItem || IfcControl::is(v); }
Type::Enum IfcCostItem::type() const { return Type::IfcCostItem; }
Type::Enum IfcCostItem::Class() { return Type::IfcCostItem; }
IfcCostItem::IfcCostItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcCostItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCostSchedule
bool IfcCostSchedule::hasSubmittedBy() { return !entity->getArgument(5)->isNull(); }
IfcActorSelect IfcCostSchedule::SubmittedBy() { return *entity->getArgument(5); }
bool IfcCostSchedule::hasPreparedBy() { return !entity->getArgument(6)->isNull(); }
IfcActorSelect IfcCostSchedule::PreparedBy() { return *entity->getArgument(6); }
bool IfcCostSchedule::hasSubmittedOn() { return !entity->getArgument(7)->isNull(); }
IfcDateTimeSelect IfcCostSchedule::SubmittedOn() { return *entity->getArgument(7); }
bool IfcCostSchedule::hasStatus() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcCostSchedule::Status() { return *entity->getArgument(8); }
bool IfcCostSchedule::hasTargetUsers() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcCostSchedule::TargetUsers() { RETURN_AS_LIST(IfcAbstractSelect,9) }
bool IfcCostSchedule::hasUpdateDate() { return !entity->getArgument(10)->isNull(); }
IfcDateTimeSelect IfcCostSchedule::UpdateDate() { return *entity->getArgument(10); }
IfcIdentifier IfcCostSchedule::ID() { return *entity->getArgument(11); }
IfcCostScheduleTypeEnum::IfcCostScheduleTypeEnum IfcCostSchedule::PredefinedType() { return IfcCostScheduleTypeEnum::FromString(*entity->getArgument(12)); }
bool IfcCostSchedule::is(Type::Enum v) const { return v == Type::IfcCostSchedule || IfcControl::is(v); }
Type::Enum IfcCostSchedule::type() const { return Type::IfcCostSchedule; }
Type::Enum IfcCostSchedule::Class() { return Type::IfcCostSchedule; }
IfcCostSchedule::IfcCostSchedule(IfcAbstractEntityPtr e) { if (!is(Type::IfcCostSchedule)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCostValue
IfcLabel IfcCostValue::CostType() { return *entity->getArgument(6); }
bool IfcCostValue::hasCondition() { return !entity->getArgument(7)->isNull(); }
IfcText IfcCostValue::Condition() { return *entity->getArgument(7); }
bool IfcCostValue::is(Type::Enum v) const { return v == Type::IfcCostValue || IfcAppliedValue::is(v); }
Type::Enum IfcCostValue::type() const { return Type::IfcCostValue; }
Type::Enum IfcCostValue::Class() { return Type::IfcCostValue; }
IfcCostValue::IfcCostValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcCostValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCovering
bool IfcCovering::hasPredefinedType() { return !entity->getArgument(8)->isNull(); }
IfcCoveringTypeEnum::IfcCoveringTypeEnum IfcCovering::PredefinedType() { return IfcCoveringTypeEnum::FromString(*entity->getArgument(8)); }
IfcRelCoversSpaces::list IfcCovering::CoversSpaces() { RETURN_INVERSE(IfcRelCoversSpaces) }
IfcRelCoversBldgElements::list IfcCovering::Covers() { RETURN_INVERSE(IfcRelCoversBldgElements) }
bool IfcCovering::is(Type::Enum v) const { return v == Type::IfcCovering || IfcBuildingElement::is(v); }
Type::Enum IfcCovering::type() const { return Type::IfcCovering; }
Type::Enum IfcCovering::Class() { return Type::IfcCovering; }
IfcCovering::IfcCovering(IfcAbstractEntityPtr e) { if (!is(Type::IfcCovering)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCoveringType
IfcCoveringTypeEnum::IfcCoveringTypeEnum IfcCoveringType::PredefinedType() { return IfcCoveringTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCoveringType::is(Type::Enum v) const { return v == Type::IfcCoveringType || IfcBuildingElementType::is(v); }
Type::Enum IfcCoveringType::type() const { return Type::IfcCoveringType; }
Type::Enum IfcCoveringType::Class() { return Type::IfcCoveringType; }
IfcCoveringType::IfcCoveringType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoveringType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCraneRailAShapeProfileDef
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::OverallHeight() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::BaseWidth2() { return *entity->getArgument(4); }
bool IfcCraneRailAShapeProfileDef::hasRadius() { return !entity->getArgument(5)->isNull(); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::Radius() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::HeadWidth() { return *entity->getArgument(6); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::HeadDepth2() { return *entity->getArgument(7); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::HeadDepth3() { return *entity->getArgument(8); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::WebThickness() { return *entity->getArgument(9); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::BaseWidth4() { return *entity->getArgument(10); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::BaseDepth1() { return *entity->getArgument(11); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::BaseDepth2() { return *entity->getArgument(12); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::BaseDepth3() { return *entity->getArgument(13); }
bool IfcCraneRailAShapeProfileDef::hasCentreOfGravityInY() { return !entity->getArgument(14)->isNull(); }
IfcPositiveLengthMeasure IfcCraneRailAShapeProfileDef::CentreOfGravityInY() { return *entity->getArgument(14); }
bool IfcCraneRailAShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcCraneRailAShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCraneRailAShapeProfileDef::type() const { return Type::IfcCraneRailAShapeProfileDef; }
Type::Enum IfcCraneRailAShapeProfileDef::Class() { return Type::IfcCraneRailAShapeProfileDef; }
IfcCraneRailAShapeProfileDef::IfcCraneRailAShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCraneRailAShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCraneRailFShapeProfileDef
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::OverallHeight() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::HeadWidth() { return *entity->getArgument(4); }
bool IfcCraneRailFShapeProfileDef::hasRadius() { return !entity->getArgument(5)->isNull(); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::Radius() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::HeadDepth2() { return *entity->getArgument(6); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::HeadDepth3() { return *entity->getArgument(7); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::WebThickness() { return *entity->getArgument(8); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::BaseDepth1() { return *entity->getArgument(9); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::BaseDepth2() { return *entity->getArgument(10); }
bool IfcCraneRailFShapeProfileDef::hasCentreOfGravityInY() { return !entity->getArgument(11)->isNull(); }
IfcPositiveLengthMeasure IfcCraneRailFShapeProfileDef::CentreOfGravityInY() { return *entity->getArgument(11); }
bool IfcCraneRailFShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcCraneRailFShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCraneRailFShapeProfileDef::type() const { return Type::IfcCraneRailFShapeProfileDef; }
Type::Enum IfcCraneRailFShapeProfileDef::Class() { return Type::IfcCraneRailFShapeProfileDef; }
IfcCraneRailFShapeProfileDef::IfcCraneRailFShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCraneRailFShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCrewResource
bool IfcCrewResource::is(Type::Enum v) const { return v == Type::IfcCrewResource || IfcConstructionResource::is(v); }
Type::Enum IfcCrewResource::type() const { return Type::IfcCrewResource; }
Type::Enum IfcCrewResource::Class() { return Type::IfcCrewResource; }
IfcCrewResource::IfcCrewResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcCrewResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCsgPrimitive3D
IfcAxis2Placement3D* IfcCsgPrimitive3D::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(0)); }
bool IfcCsgPrimitive3D::is(Type::Enum v) const { return v == Type::IfcCsgPrimitive3D || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCsgPrimitive3D::type() const { return Type::IfcCsgPrimitive3D; }
Type::Enum IfcCsgPrimitive3D::Class() { return Type::IfcCsgPrimitive3D; }
IfcCsgPrimitive3D::IfcCsgPrimitive3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcCsgPrimitive3D)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCsgSolid
IfcCsgSelect IfcCsgSolid::TreeRootExpression() { return *entity->getArgument(0); }
bool IfcCsgSolid::is(Type::Enum v) const { return v == Type::IfcCsgSolid || IfcSolidModel::is(v); }
Type::Enum IfcCsgSolid::type() const { return Type::IfcCsgSolid; }
Type::Enum IfcCsgSolid::Class() { return Type::IfcCsgSolid; }
IfcCsgSolid::IfcCsgSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcCsgSolid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurrencyRelationship
IfcMonetaryUnit* IfcCurrencyRelationship::RelatingMonetaryUnit() { return reinterpret_pointer_cast<IfcBaseClass,IfcMonetaryUnit>(*entity->getArgument(0)); }
IfcMonetaryUnit* IfcCurrencyRelationship::RelatedMonetaryUnit() { return reinterpret_pointer_cast<IfcBaseClass,IfcMonetaryUnit>(*entity->getArgument(1)); }
IfcPositiveRatioMeasure IfcCurrencyRelationship::ExchangeRate() { return *entity->getArgument(2); }
IfcDateAndTime* IfcCurrencyRelationship::RateDateTime() { return reinterpret_pointer_cast<IfcBaseClass,IfcDateAndTime>(*entity->getArgument(3)); }
bool IfcCurrencyRelationship::hasRateSource() { return !entity->getArgument(4)->isNull(); }
IfcLibraryInformation* IfcCurrencyRelationship::RateSource() { return reinterpret_pointer_cast<IfcBaseClass,IfcLibraryInformation>(*entity->getArgument(4)); }
bool IfcCurrencyRelationship::is(Type::Enum v) const { return v == Type::IfcCurrencyRelationship; }
Type::Enum IfcCurrencyRelationship::type() const { return Type::IfcCurrencyRelationship; }
Type::Enum IfcCurrencyRelationship::Class() { return Type::IfcCurrencyRelationship; }
IfcCurrencyRelationship::IfcCurrencyRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurrencyRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurtainWall
bool IfcCurtainWall::is(Type::Enum v) const { return v == Type::IfcCurtainWall || IfcBuildingElement::is(v); }
Type::Enum IfcCurtainWall::type() const { return Type::IfcCurtainWall; }
Type::Enum IfcCurtainWall::Class() { return Type::IfcCurtainWall; }
IfcCurtainWall::IfcCurtainWall(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurtainWall)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurtainWallType
IfcCurtainWallTypeEnum::IfcCurtainWallTypeEnum IfcCurtainWallType::PredefinedType() { return IfcCurtainWallTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCurtainWallType::is(Type::Enum v) const { return v == Type::IfcCurtainWallType || IfcBuildingElementType::is(v); }
Type::Enum IfcCurtainWallType::type() const { return Type::IfcCurtainWallType; }
Type::Enum IfcCurtainWallType::Class() { return Type::IfcCurtainWallType; }
IfcCurtainWallType::IfcCurtainWallType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurtainWallType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurve
bool IfcCurve::is(Type::Enum v) const { return v == Type::IfcCurve || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCurve::type() const { return Type::IfcCurve; }
Type::Enum IfcCurve::Class() { return Type::IfcCurve; }
IfcCurve::IfcCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurveBoundedPlane
IfcPlane* IfcCurveBoundedPlane::BasisSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcPlane>(*entity->getArgument(0)); }
IfcCurve* IfcCurveBoundedPlane::OuterBoundary() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(1)); }
SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > IfcCurveBoundedPlane::InnerBoundaries() { RETURN_AS_LIST(IfcCurve,2) }
bool IfcCurveBoundedPlane::is(Type::Enum v) const { return v == Type::IfcCurveBoundedPlane || IfcBoundedSurface::is(v); }
Type::Enum IfcCurveBoundedPlane::type() const { return Type::IfcCurveBoundedPlane; }
Type::Enum IfcCurveBoundedPlane::Class() { return Type::IfcCurveBoundedPlane; }
IfcCurveBoundedPlane::IfcCurveBoundedPlane(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveBoundedPlane)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurveStyle
bool IfcCurveStyle::hasCurveFont() { return !entity->getArgument(1)->isNull(); }
IfcCurveFontOrScaledCurveFontSelect IfcCurveStyle::CurveFont() { return *entity->getArgument(1); }
bool IfcCurveStyle::hasCurveWidth() { return !entity->getArgument(2)->isNull(); }
IfcSizeSelect IfcCurveStyle::CurveWidth() { return *entity->getArgument(2); }
bool IfcCurveStyle::hasCurveColour() { return !entity->getArgument(3)->isNull(); }
IfcColour IfcCurveStyle::CurveColour() { return *entity->getArgument(3); }
bool IfcCurveStyle::is(Type::Enum v) const { return v == Type::IfcCurveStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcCurveStyle::type() const { return Type::IfcCurveStyle; }
Type::Enum IfcCurveStyle::Class() { return Type::IfcCurveStyle; }
IfcCurveStyle::IfcCurveStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurveStyleFont
bool IfcCurveStyleFont::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcCurveStyleFont::Name() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontPattern> > IfcCurveStyleFont::PatternList() { RETURN_AS_LIST(IfcCurveStyleFontPattern,1) }
bool IfcCurveStyleFont::is(Type::Enum v) const { return v == Type::IfcCurveStyleFont; }
Type::Enum IfcCurveStyleFont::type() const { return Type::IfcCurveStyleFont; }
Type::Enum IfcCurveStyleFont::Class() { return Type::IfcCurveStyleFont; }
IfcCurveStyleFont::IfcCurveStyleFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyleFont)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurveStyleFontAndScaling
bool IfcCurveStyleFontAndScaling::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcCurveStyleFontAndScaling::Name() { return *entity->getArgument(0); }
IfcCurveStyleFontSelect IfcCurveStyleFontAndScaling::CurveFont() { return *entity->getArgument(1); }
IfcPositiveRatioMeasure IfcCurveStyleFontAndScaling::CurveFontScaling() { return *entity->getArgument(2); }
bool IfcCurveStyleFontAndScaling::is(Type::Enum v) const { return v == Type::IfcCurveStyleFontAndScaling; }
Type::Enum IfcCurveStyleFontAndScaling::type() const { return Type::IfcCurveStyleFontAndScaling; }
Type::Enum IfcCurveStyleFontAndScaling::Class() { return Type::IfcCurveStyleFontAndScaling; }
IfcCurveStyleFontAndScaling::IfcCurveStyleFontAndScaling(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyleFontAndScaling)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcCurveStyleFontPattern
IfcLengthMeasure IfcCurveStyleFontPattern::VisibleSegmentLength() { return *entity->getArgument(0); }
IfcPositiveLengthMeasure IfcCurveStyleFontPattern::InvisibleSegmentLength() { return *entity->getArgument(1); }
bool IfcCurveStyleFontPattern::is(Type::Enum v) const { return v == Type::IfcCurveStyleFontPattern; }
Type::Enum IfcCurveStyleFontPattern::type() const { return Type::IfcCurveStyleFontPattern; }
Type::Enum IfcCurveStyleFontPattern::Class() { return Type::IfcCurveStyleFontPattern; }
IfcCurveStyleFontPattern::IfcCurveStyleFontPattern(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyleFontPattern)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDamperType
IfcDamperTypeEnum::IfcDamperTypeEnum IfcDamperType::PredefinedType() { return IfcDamperTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDamperType::is(Type::Enum v) const { return v == Type::IfcDamperType || IfcFlowControllerType::is(v); }
Type::Enum IfcDamperType::type() const { return Type::IfcDamperType; }
Type::Enum IfcDamperType::Class() { return Type::IfcDamperType; }
IfcDamperType::IfcDamperType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDamperType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDateAndTime
IfcCalendarDate* IfcDateAndTime::DateComponent() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(0)); }
IfcLocalTime* IfcDateAndTime::TimeComponent() { return reinterpret_pointer_cast<IfcBaseClass,IfcLocalTime>(*entity->getArgument(1)); }
bool IfcDateAndTime::is(Type::Enum v) const { return v == Type::IfcDateAndTime; }
Type::Enum IfcDateAndTime::type() const { return Type::IfcDateAndTime; }
Type::Enum IfcDateAndTime::Class() { return Type::IfcDateAndTime; }
IfcDateAndTime::IfcDateAndTime(IfcAbstractEntityPtr e) { if (!is(Type::IfcDateAndTime)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDefinedSymbol
IfcDefinedSymbolSelect IfcDefinedSymbol::Definition() { return *entity->getArgument(0); }
IfcCartesianTransformationOperator2D* IfcDefinedSymbol::Target() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator2D>(*entity->getArgument(1)); }
bool IfcDefinedSymbol::is(Type::Enum v) const { return v == Type::IfcDefinedSymbol || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcDefinedSymbol::type() const { return Type::IfcDefinedSymbol; }
Type::Enum IfcDefinedSymbol::Class() { return Type::IfcDefinedSymbol; }
IfcDefinedSymbol::IfcDefinedSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcDefinedSymbol)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDerivedProfileDef
IfcProfileDef* IfcDerivedProfileDef::ParentProfile() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(2)); }
IfcCartesianTransformationOperator2D* IfcDerivedProfileDef::Operator() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator2D>(*entity->getArgument(3)); }
bool IfcDerivedProfileDef::hasLabel() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcDerivedProfileDef::Label() { return *entity->getArgument(4); }
bool IfcDerivedProfileDef::is(Type::Enum v) const { return v == Type::IfcDerivedProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcDerivedProfileDef::type() const { return Type::IfcDerivedProfileDef; }
Type::Enum IfcDerivedProfileDef::Class() { return Type::IfcDerivedProfileDef; }
IfcDerivedProfileDef::IfcDerivedProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcDerivedProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDerivedUnit
SHARED_PTR< IfcTemplatedEntityList<IfcDerivedUnitElement> > IfcDerivedUnit::Elements() { RETURN_AS_LIST(IfcDerivedUnitElement,0) }
IfcDerivedUnitEnum::IfcDerivedUnitEnum IfcDerivedUnit::UnitType() { return IfcDerivedUnitEnum::FromString(*entity->getArgument(1)); }
bool IfcDerivedUnit::hasUserDefinedType() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcDerivedUnit::UserDefinedType() { return *entity->getArgument(2); }
bool IfcDerivedUnit::is(Type::Enum v) const { return v == Type::IfcDerivedUnit; }
Type::Enum IfcDerivedUnit::type() const { return Type::IfcDerivedUnit; }
Type::Enum IfcDerivedUnit::Class() { return Type::IfcDerivedUnit; }
IfcDerivedUnit::IfcDerivedUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcDerivedUnit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDerivedUnitElement
IfcNamedUnit* IfcDerivedUnitElement::Unit() { return reinterpret_pointer_cast<IfcBaseClass,IfcNamedUnit>(*entity->getArgument(0)); }
int IfcDerivedUnitElement::Exponent() { return *entity->getArgument(1); }
bool IfcDerivedUnitElement::is(Type::Enum v) const { return v == Type::IfcDerivedUnitElement; }
Type::Enum IfcDerivedUnitElement::type() const { return Type::IfcDerivedUnitElement; }
Type::Enum IfcDerivedUnitElement::Class() { return Type::IfcDerivedUnitElement; }
IfcDerivedUnitElement::IfcDerivedUnitElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDerivedUnitElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDiameterDimension
bool IfcDiameterDimension::is(Type::Enum v) const { return v == Type::IfcDiameterDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcDiameterDimension::type() const { return Type::IfcDiameterDimension; }
Type::Enum IfcDiameterDimension::Class() { return Type::IfcDiameterDimension; }
IfcDiameterDimension::IfcDiameterDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcDiameterDimension)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDimensionCalloutRelationship
bool IfcDimensionCalloutRelationship::is(Type::Enum v) const { return v == Type::IfcDimensionCalloutRelationship || IfcDraughtingCalloutRelationship::is(v); }
Type::Enum IfcDimensionCalloutRelationship::type() const { return Type::IfcDimensionCalloutRelationship; }
Type::Enum IfcDimensionCalloutRelationship::Class() { return Type::IfcDimensionCalloutRelationship; }
IfcDimensionCalloutRelationship::IfcDimensionCalloutRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCalloutRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDimensionCurve
IfcTerminatorSymbol::list IfcDimensionCurve::AnnotatedBySymbols() { RETURN_INVERSE(IfcTerminatorSymbol) }
bool IfcDimensionCurve::is(Type::Enum v) const { return v == Type::IfcDimensionCurve || IfcAnnotationCurveOccurrence::is(v); }
Type::Enum IfcDimensionCurve::type() const { return Type::IfcDimensionCurve; }
Type::Enum IfcDimensionCurve::Class() { return Type::IfcDimensionCurve; }
IfcDimensionCurve::IfcDimensionCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDimensionCurveDirectedCallout
bool IfcDimensionCurveDirectedCallout::is(Type::Enum v) const { return v == Type::IfcDimensionCurveDirectedCallout || IfcDraughtingCallout::is(v); }
Type::Enum IfcDimensionCurveDirectedCallout::type() const { return Type::IfcDimensionCurveDirectedCallout; }
Type::Enum IfcDimensionCurveDirectedCallout::Class() { return Type::IfcDimensionCurveDirectedCallout; }
IfcDimensionCurveDirectedCallout::IfcDimensionCurveDirectedCallout(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCurveDirectedCallout)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDimensionCurveTerminator
IfcDimensionExtentUsage::IfcDimensionExtentUsage IfcDimensionCurveTerminator::Role() { return IfcDimensionExtentUsage::FromString(*entity->getArgument(4)); }
bool IfcDimensionCurveTerminator::is(Type::Enum v) const { return v == Type::IfcDimensionCurveTerminator || IfcTerminatorSymbol::is(v); }
Type::Enum IfcDimensionCurveTerminator::type() const { return Type::IfcDimensionCurveTerminator; }
Type::Enum IfcDimensionCurveTerminator::Class() { return Type::IfcDimensionCurveTerminator; }
IfcDimensionCurveTerminator::IfcDimensionCurveTerminator(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCurveTerminator)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDimensionPair
bool IfcDimensionPair::is(Type::Enum v) const { return v == Type::IfcDimensionPair || IfcDraughtingCalloutRelationship::is(v); }
Type::Enum IfcDimensionPair::type() const { return Type::IfcDimensionPair; }
Type::Enum IfcDimensionPair::Class() { return Type::IfcDimensionPair; }
IfcDimensionPair::IfcDimensionPair(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionPair)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDimensionalExponents
int IfcDimensionalExponents::LengthExponent() { return *entity->getArgument(0); }
int IfcDimensionalExponents::MassExponent() { return *entity->getArgument(1); }
int IfcDimensionalExponents::TimeExponent() { return *entity->getArgument(2); }
int IfcDimensionalExponents::ElectricCurrentExponent() { return *entity->getArgument(3); }
int IfcDimensionalExponents::ThermodynamicTemperatureExponent() { return *entity->getArgument(4); }
int IfcDimensionalExponents::AmountOfSubstanceExponent() { return *entity->getArgument(5); }
int IfcDimensionalExponents::LuminousIntensityExponent() { return *entity->getArgument(6); }
bool IfcDimensionalExponents::is(Type::Enum v) const { return v == Type::IfcDimensionalExponents; }
Type::Enum IfcDimensionalExponents::type() const { return Type::IfcDimensionalExponents; }
Type::Enum IfcDimensionalExponents::Class() { return Type::IfcDimensionalExponents; }
IfcDimensionalExponents::IfcDimensionalExponents(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionalExponents)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDirection
std::vector<double> /*[2:3]*/ IfcDirection::DirectionRatios() { return *entity->getArgument(0); }
bool IfcDirection::is(Type::Enum v) const { return v == Type::IfcDirection || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcDirection::type() const { return Type::IfcDirection; }
Type::Enum IfcDirection::Class() { return Type::IfcDirection; }
IfcDirection::IfcDirection(IfcAbstractEntityPtr e) { if (!is(Type::IfcDirection)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDiscreteAccessory
bool IfcDiscreteAccessory::is(Type::Enum v) const { return v == Type::IfcDiscreteAccessory || IfcElementComponent::is(v); }
Type::Enum IfcDiscreteAccessory::type() const { return Type::IfcDiscreteAccessory; }
Type::Enum IfcDiscreteAccessory::Class() { return Type::IfcDiscreteAccessory; }
IfcDiscreteAccessory::IfcDiscreteAccessory(IfcAbstractEntityPtr e) { if (!is(Type::IfcDiscreteAccessory)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDiscreteAccessoryType
bool IfcDiscreteAccessoryType::is(Type::Enum v) const { return v == Type::IfcDiscreteAccessoryType || IfcElementComponentType::is(v); }
Type::Enum IfcDiscreteAccessoryType::type() const { return Type::IfcDiscreteAccessoryType; }
Type::Enum IfcDiscreteAccessoryType::Class() { return Type::IfcDiscreteAccessoryType; }
IfcDiscreteAccessoryType::IfcDiscreteAccessoryType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDiscreteAccessoryType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionChamberElement
bool IfcDistributionChamberElement::is(Type::Enum v) const { return v == Type::IfcDistributionChamberElement || IfcDistributionFlowElement::is(v); }
Type::Enum IfcDistributionChamberElement::type() const { return Type::IfcDistributionChamberElement; }
Type::Enum IfcDistributionChamberElement::Class() { return Type::IfcDistributionChamberElement; }
IfcDistributionChamberElement::IfcDistributionChamberElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionChamberElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionChamberElementType
IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementTypeEnum IfcDistributionChamberElementType::PredefinedType() { return IfcDistributionChamberElementTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDistributionChamberElementType::is(Type::Enum v) const { return v == Type::IfcDistributionChamberElementType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcDistributionChamberElementType::type() const { return Type::IfcDistributionChamberElementType; }
Type::Enum IfcDistributionChamberElementType::Class() { return Type::IfcDistributionChamberElementType; }
IfcDistributionChamberElementType::IfcDistributionChamberElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionChamberElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionControlElement
bool IfcDistributionControlElement::hasControlElementId() { return !entity->getArgument(8)->isNull(); }
IfcIdentifier IfcDistributionControlElement::ControlElementId() { return *entity->getArgument(8); }
IfcRelFlowControlElements::list IfcDistributionControlElement::AssignedToFlowElement() { RETURN_INVERSE(IfcRelFlowControlElements) }
bool IfcDistributionControlElement::is(Type::Enum v) const { return v == Type::IfcDistributionControlElement || IfcDistributionElement::is(v); }
Type::Enum IfcDistributionControlElement::type() const { return Type::IfcDistributionControlElement; }
Type::Enum IfcDistributionControlElement::Class() { return Type::IfcDistributionControlElement; }
IfcDistributionControlElement::IfcDistributionControlElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionControlElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionControlElementType
bool IfcDistributionControlElementType::is(Type::Enum v) const { return v == Type::IfcDistributionControlElementType || IfcDistributionElementType::is(v); }
Type::Enum IfcDistributionControlElementType::type() const { return Type::IfcDistributionControlElementType; }
Type::Enum IfcDistributionControlElementType::Class() { return Type::IfcDistributionControlElementType; }
IfcDistributionControlElementType::IfcDistributionControlElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionControlElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionElement
bool IfcDistributionElement::is(Type::Enum v) const { return v == Type::IfcDistributionElement || IfcElement::is(v); }
Type::Enum IfcDistributionElement::type() const { return Type::IfcDistributionElement; }
Type::Enum IfcDistributionElement::Class() { return Type::IfcDistributionElement; }
IfcDistributionElement::IfcDistributionElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionElementType
bool IfcDistributionElementType::is(Type::Enum v) const { return v == Type::IfcDistributionElementType || IfcElementType::is(v); }
Type::Enum IfcDistributionElementType::type() const { return Type::IfcDistributionElementType; }
Type::Enum IfcDistributionElementType::Class() { return Type::IfcDistributionElementType; }
IfcDistributionElementType::IfcDistributionElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionFlowElement
IfcRelFlowControlElements::list IfcDistributionFlowElement::HasControlElements() { RETURN_INVERSE(IfcRelFlowControlElements) }
bool IfcDistributionFlowElement::is(Type::Enum v) const { return v == Type::IfcDistributionFlowElement || IfcDistributionElement::is(v); }
Type::Enum IfcDistributionFlowElement::type() const { return Type::IfcDistributionFlowElement; }
Type::Enum IfcDistributionFlowElement::Class() { return Type::IfcDistributionFlowElement; }
IfcDistributionFlowElement::IfcDistributionFlowElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionFlowElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionFlowElementType
bool IfcDistributionFlowElementType::is(Type::Enum v) const { return v == Type::IfcDistributionFlowElementType || IfcDistributionElementType::is(v); }
Type::Enum IfcDistributionFlowElementType::type() const { return Type::IfcDistributionFlowElementType; }
Type::Enum IfcDistributionFlowElementType::Class() { return Type::IfcDistributionFlowElementType; }
IfcDistributionFlowElementType::IfcDistributionFlowElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionFlowElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDistributionPort
bool IfcDistributionPort::hasFlowDirection() { return !entity->getArgument(7)->isNull(); }
IfcFlowDirectionEnum::IfcFlowDirectionEnum IfcDistributionPort::FlowDirection() { return IfcFlowDirectionEnum::FromString(*entity->getArgument(7)); }
bool IfcDistributionPort::is(Type::Enum v) const { return v == Type::IfcDistributionPort || IfcPort::is(v); }
Type::Enum IfcDistributionPort::type() const { return Type::IfcDistributionPort; }
Type::Enum IfcDistributionPort::Class() { return Type::IfcDistributionPort; }
IfcDistributionPort::IfcDistributionPort(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionPort)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDocumentElectronicFormat
bool IfcDocumentElectronicFormat::hasFileExtension() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcDocumentElectronicFormat::FileExtension() { return *entity->getArgument(0); }
bool IfcDocumentElectronicFormat::hasMimeContentType() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcDocumentElectronicFormat::MimeContentType() { return *entity->getArgument(1); }
bool IfcDocumentElectronicFormat::hasMimeSubtype() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcDocumentElectronicFormat::MimeSubtype() { return *entity->getArgument(2); }
bool IfcDocumentElectronicFormat::is(Type::Enum v) const { return v == Type::IfcDocumentElectronicFormat; }
Type::Enum IfcDocumentElectronicFormat::type() const { return Type::IfcDocumentElectronicFormat; }
Type::Enum IfcDocumentElectronicFormat::Class() { return Type::IfcDocumentElectronicFormat; }
IfcDocumentElectronicFormat::IfcDocumentElectronicFormat(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentElectronicFormat)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDocumentInformation
IfcIdentifier IfcDocumentInformation::DocumentId() { return *entity->getArgument(0); }
IfcLabel IfcDocumentInformation::Name() { return *entity->getArgument(1); }
bool IfcDocumentInformation::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcDocumentInformation::Description() { return *entity->getArgument(2); }
bool IfcDocumentInformation::hasDocumentReferences() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcDocumentReference> > IfcDocumentInformation::DocumentReferences() { RETURN_AS_LIST(IfcDocumentReference,3) }
bool IfcDocumentInformation::hasPurpose() { return !entity->getArgument(4)->isNull(); }
IfcText IfcDocumentInformation::Purpose() { return *entity->getArgument(4); }
bool IfcDocumentInformation::hasIntendedUse() { return !entity->getArgument(5)->isNull(); }
IfcText IfcDocumentInformation::IntendedUse() { return *entity->getArgument(5); }
bool IfcDocumentInformation::hasScope() { return !entity->getArgument(6)->isNull(); }
IfcText IfcDocumentInformation::Scope() { return *entity->getArgument(6); }
bool IfcDocumentInformation::hasRevision() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcDocumentInformation::Revision() { return *entity->getArgument(7); }
bool IfcDocumentInformation::hasDocumentOwner() { return !entity->getArgument(8)->isNull(); }
IfcActorSelect IfcDocumentInformation::DocumentOwner() { return *entity->getArgument(8); }
bool IfcDocumentInformation::hasEditors() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcDocumentInformation::Editors() { RETURN_AS_LIST(IfcAbstractSelect,9) }
bool IfcDocumentInformation::hasCreationTime() { return !entity->getArgument(10)->isNull(); }
IfcDateAndTime* IfcDocumentInformation::CreationTime() { return reinterpret_pointer_cast<IfcBaseClass,IfcDateAndTime>(*entity->getArgument(10)); }
bool IfcDocumentInformation::hasLastRevisionTime() { return !entity->getArgument(11)->isNull(); }
IfcDateAndTime* IfcDocumentInformation::LastRevisionTime() { return reinterpret_pointer_cast<IfcBaseClass,IfcDateAndTime>(*entity->getArgument(11)); }
bool IfcDocumentInformation::hasElectronicFormat() { return !entity->getArgument(12)->isNull(); }
IfcDocumentElectronicFormat* IfcDocumentInformation::ElectronicFormat() { return reinterpret_pointer_cast<IfcBaseClass,IfcDocumentElectronicFormat>(*entity->getArgument(12)); }
bool IfcDocumentInformation::hasValidFrom() { return !entity->getArgument(13)->isNull(); }
IfcCalendarDate* IfcDocumentInformation::ValidFrom() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(13)); }
bool IfcDocumentInformation::hasValidUntil() { return !entity->getArgument(14)->isNull(); }
IfcCalendarDate* IfcDocumentInformation::ValidUntil() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(14)); }
bool IfcDocumentInformation::hasConfidentiality() { return !entity->getArgument(15)->isNull(); }
IfcDocumentConfidentialityEnum::IfcDocumentConfidentialityEnum IfcDocumentInformation::Confidentiality() { return IfcDocumentConfidentialityEnum::FromString(*entity->getArgument(15)); }
bool IfcDocumentInformation::hasStatus() { return !entity->getArgument(16)->isNull(); }
IfcDocumentStatusEnum::IfcDocumentStatusEnum IfcDocumentInformation::Status() { return IfcDocumentStatusEnum::FromString(*entity->getArgument(16)); }
IfcDocumentInformationRelationship::list IfcDocumentInformation::IsPointedTo() { RETURN_INVERSE(IfcDocumentInformationRelationship) }
IfcDocumentInformationRelationship::list IfcDocumentInformation::IsPointer() { RETURN_INVERSE(IfcDocumentInformationRelationship) }
bool IfcDocumentInformation::is(Type::Enum v) const { return v == Type::IfcDocumentInformation; }
Type::Enum IfcDocumentInformation::type() const { return Type::IfcDocumentInformation; }
Type::Enum IfcDocumentInformation::Class() { return Type::IfcDocumentInformation; }
IfcDocumentInformation::IfcDocumentInformation(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentInformation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDocumentInformationRelationship
IfcDocumentInformation* IfcDocumentInformationRelationship::RelatingDocument() { return reinterpret_pointer_cast<IfcBaseClass,IfcDocumentInformation>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > IfcDocumentInformationRelationship::RelatedDocuments() { RETURN_AS_LIST(IfcDocumentInformation,1) }
bool IfcDocumentInformationRelationship::hasRelationshipType() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcDocumentInformationRelationship::RelationshipType() { return *entity->getArgument(2); }
bool IfcDocumentInformationRelationship::is(Type::Enum v) const { return v == Type::IfcDocumentInformationRelationship; }
Type::Enum IfcDocumentInformationRelationship::type() const { return Type::IfcDocumentInformationRelationship; }
Type::Enum IfcDocumentInformationRelationship::Class() { return Type::IfcDocumentInformationRelationship; }
IfcDocumentInformationRelationship::IfcDocumentInformationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentInformationRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDocumentReference
IfcDocumentInformation::list IfcDocumentReference::ReferenceToDocument() { RETURN_INVERSE(IfcDocumentInformation) }
bool IfcDocumentReference::is(Type::Enum v) const { return v == Type::IfcDocumentReference || IfcExternalReference::is(v); }
Type::Enum IfcDocumentReference::type() const { return Type::IfcDocumentReference; }
Type::Enum IfcDocumentReference::Class() { return Type::IfcDocumentReference; }
IfcDocumentReference::IfcDocumentReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentReference)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDoor
bool IfcDoor::hasOverallHeight() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcDoor::OverallHeight() { return *entity->getArgument(8); }
bool IfcDoor::hasOverallWidth() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcDoor::OverallWidth() { return *entity->getArgument(9); }
bool IfcDoor::is(Type::Enum v) const { return v == Type::IfcDoor || IfcBuildingElement::is(v); }
Type::Enum IfcDoor::type() const { return Type::IfcDoor; }
Type::Enum IfcDoor::Class() { return Type::IfcDoor; }
IfcDoor::IfcDoor(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoor)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDoorLiningProperties
bool IfcDoorLiningProperties::hasLiningDepth() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcDoorLiningProperties::LiningDepth() { return *entity->getArgument(4); }
bool IfcDoorLiningProperties::hasLiningThickness() { return !entity->getArgument(5)->isNull(); }
IfcPositiveLengthMeasure IfcDoorLiningProperties::LiningThickness() { return *entity->getArgument(5); }
bool IfcDoorLiningProperties::hasThresholdDepth() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcDoorLiningProperties::ThresholdDepth() { return *entity->getArgument(6); }
bool IfcDoorLiningProperties::hasThresholdThickness() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcDoorLiningProperties::ThresholdThickness() { return *entity->getArgument(7); }
bool IfcDoorLiningProperties::hasTransomThickness() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcDoorLiningProperties::TransomThickness() { return *entity->getArgument(8); }
bool IfcDoorLiningProperties::hasTransomOffset() { return !entity->getArgument(9)->isNull(); }
IfcLengthMeasure IfcDoorLiningProperties::TransomOffset() { return *entity->getArgument(9); }
bool IfcDoorLiningProperties::hasLiningOffset() { return !entity->getArgument(10)->isNull(); }
IfcLengthMeasure IfcDoorLiningProperties::LiningOffset() { return *entity->getArgument(10); }
bool IfcDoorLiningProperties::hasThresholdOffset() { return !entity->getArgument(11)->isNull(); }
IfcLengthMeasure IfcDoorLiningProperties::ThresholdOffset() { return *entity->getArgument(11); }
bool IfcDoorLiningProperties::hasCasingThickness() { return !entity->getArgument(12)->isNull(); }
IfcPositiveLengthMeasure IfcDoorLiningProperties::CasingThickness() { return *entity->getArgument(12); }
bool IfcDoorLiningProperties::hasCasingDepth() { return !entity->getArgument(13)->isNull(); }
IfcPositiveLengthMeasure IfcDoorLiningProperties::CasingDepth() { return *entity->getArgument(13); }
bool IfcDoorLiningProperties::hasShapeAspectStyle() { return !entity->getArgument(14)->isNull(); }
IfcShapeAspect* IfcDoorLiningProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(14)); }
bool IfcDoorLiningProperties::is(Type::Enum v) const { return v == Type::IfcDoorLiningProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcDoorLiningProperties::type() const { return Type::IfcDoorLiningProperties; }
Type::Enum IfcDoorLiningProperties::Class() { return Type::IfcDoorLiningProperties; }
IfcDoorLiningProperties::IfcDoorLiningProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoorLiningProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDoorPanelProperties
bool IfcDoorPanelProperties::hasPanelDepth() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcDoorPanelProperties::PanelDepth() { return *entity->getArgument(4); }
IfcDoorPanelOperationEnum::IfcDoorPanelOperationEnum IfcDoorPanelProperties::PanelOperation() { return IfcDoorPanelOperationEnum::FromString(*entity->getArgument(5)); }
bool IfcDoorPanelProperties::hasPanelWidth() { return !entity->getArgument(6)->isNull(); }
IfcNormalisedRatioMeasure IfcDoorPanelProperties::PanelWidth() { return *entity->getArgument(6); }
IfcDoorPanelPositionEnum::IfcDoorPanelPositionEnum IfcDoorPanelProperties::PanelPosition() { return IfcDoorPanelPositionEnum::FromString(*entity->getArgument(7)); }
bool IfcDoorPanelProperties::hasShapeAspectStyle() { return !entity->getArgument(8)->isNull(); }
IfcShapeAspect* IfcDoorPanelProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(8)); }
bool IfcDoorPanelProperties::is(Type::Enum v) const { return v == Type::IfcDoorPanelProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcDoorPanelProperties::type() const { return Type::IfcDoorPanelProperties; }
Type::Enum IfcDoorPanelProperties::Class() { return Type::IfcDoorPanelProperties; }
IfcDoorPanelProperties::IfcDoorPanelProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoorPanelProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDoorStyle
IfcDoorStyleOperationEnum::IfcDoorStyleOperationEnum IfcDoorStyle::OperationType() { return IfcDoorStyleOperationEnum::FromString(*entity->getArgument(8)); }
IfcDoorStyleConstructionEnum::IfcDoorStyleConstructionEnum IfcDoorStyle::ConstructionType() { return IfcDoorStyleConstructionEnum::FromString(*entity->getArgument(9)); }
bool IfcDoorStyle::ParameterTakesPrecedence() { return *entity->getArgument(10); }
bool IfcDoorStyle::Sizeable() { return *entity->getArgument(11); }
bool IfcDoorStyle::is(Type::Enum v) const { return v == Type::IfcDoorStyle || IfcTypeProduct::is(v); }
Type::Enum IfcDoorStyle::type() const { return Type::IfcDoorStyle; }
Type::Enum IfcDoorStyle::Class() { return Type::IfcDoorStyle; }
IfcDoorStyle::IfcDoorStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoorStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDraughtingCallout
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcDraughtingCallout::Contents() { RETURN_AS_LIST(IfcAbstractSelect,0) }
IfcDraughtingCalloutRelationship::list IfcDraughtingCallout::IsRelatedFromCallout() { RETURN_INVERSE(IfcDraughtingCalloutRelationship) }
IfcDraughtingCalloutRelationship::list IfcDraughtingCallout::IsRelatedToCallout() { RETURN_INVERSE(IfcDraughtingCalloutRelationship) }
bool IfcDraughtingCallout::is(Type::Enum v) const { return v == Type::IfcDraughtingCallout || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcDraughtingCallout::type() const { return Type::IfcDraughtingCallout; }
Type::Enum IfcDraughtingCallout::Class() { return Type::IfcDraughtingCallout; }
IfcDraughtingCallout::IfcDraughtingCallout(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingCallout)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDraughtingCalloutRelationship
bool IfcDraughtingCalloutRelationship::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcDraughtingCalloutRelationship::Name() { return *entity->getArgument(0); }
bool IfcDraughtingCalloutRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcDraughtingCalloutRelationship::Description() { return *entity->getArgument(1); }
IfcDraughtingCallout* IfcDraughtingCalloutRelationship::RelatingDraughtingCallout() { return reinterpret_pointer_cast<IfcBaseClass,IfcDraughtingCallout>(*entity->getArgument(2)); }
IfcDraughtingCallout* IfcDraughtingCalloutRelationship::RelatedDraughtingCallout() { return reinterpret_pointer_cast<IfcBaseClass,IfcDraughtingCallout>(*entity->getArgument(3)); }
bool IfcDraughtingCalloutRelationship::is(Type::Enum v) const { return v == Type::IfcDraughtingCalloutRelationship; }
Type::Enum IfcDraughtingCalloutRelationship::type() const { return Type::IfcDraughtingCalloutRelationship; }
Type::Enum IfcDraughtingCalloutRelationship::Class() { return Type::IfcDraughtingCalloutRelationship; }
IfcDraughtingCalloutRelationship::IfcDraughtingCalloutRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingCalloutRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDraughtingPreDefinedColour
bool IfcDraughtingPreDefinedColour::is(Type::Enum v) const { return v == Type::IfcDraughtingPreDefinedColour || IfcPreDefinedColour::is(v); }
Type::Enum IfcDraughtingPreDefinedColour::type() const { return Type::IfcDraughtingPreDefinedColour; }
Type::Enum IfcDraughtingPreDefinedColour::Class() { return Type::IfcDraughtingPreDefinedColour; }
IfcDraughtingPreDefinedColour::IfcDraughtingPreDefinedColour(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingPreDefinedColour)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDraughtingPreDefinedCurveFont
bool IfcDraughtingPreDefinedCurveFont::is(Type::Enum v) const { return v == Type::IfcDraughtingPreDefinedCurveFont || IfcPreDefinedCurveFont::is(v); }
Type::Enum IfcDraughtingPreDefinedCurveFont::type() const { return Type::IfcDraughtingPreDefinedCurveFont; }
Type::Enum IfcDraughtingPreDefinedCurveFont::Class() { return Type::IfcDraughtingPreDefinedCurveFont; }
IfcDraughtingPreDefinedCurveFont::IfcDraughtingPreDefinedCurveFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingPreDefinedCurveFont)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDraughtingPreDefinedTextFont
bool IfcDraughtingPreDefinedTextFont::is(Type::Enum v) const { return v == Type::IfcDraughtingPreDefinedTextFont || IfcPreDefinedTextFont::is(v); }
Type::Enum IfcDraughtingPreDefinedTextFont::type() const { return Type::IfcDraughtingPreDefinedTextFont; }
Type::Enum IfcDraughtingPreDefinedTextFont::Class() { return Type::IfcDraughtingPreDefinedTextFont; }
IfcDraughtingPreDefinedTextFont::IfcDraughtingPreDefinedTextFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingPreDefinedTextFont)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDuctFittingType
IfcDuctFittingTypeEnum::IfcDuctFittingTypeEnum IfcDuctFittingType::PredefinedType() { return IfcDuctFittingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDuctFittingType::is(Type::Enum v) const { return v == Type::IfcDuctFittingType || IfcFlowFittingType::is(v); }
Type::Enum IfcDuctFittingType::type() const { return Type::IfcDuctFittingType; }
Type::Enum IfcDuctFittingType::Class() { return Type::IfcDuctFittingType; }
IfcDuctFittingType::IfcDuctFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDuctFittingType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDuctSegmentType
IfcDuctSegmentTypeEnum::IfcDuctSegmentTypeEnum IfcDuctSegmentType::PredefinedType() { return IfcDuctSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDuctSegmentType::is(Type::Enum v) const { return v == Type::IfcDuctSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcDuctSegmentType::type() const { return Type::IfcDuctSegmentType; }
Type::Enum IfcDuctSegmentType::Class() { return Type::IfcDuctSegmentType; }
IfcDuctSegmentType::IfcDuctSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDuctSegmentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcDuctSilencerType
IfcDuctSilencerTypeEnum::IfcDuctSilencerTypeEnum IfcDuctSilencerType::PredefinedType() { return IfcDuctSilencerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDuctSilencerType::is(Type::Enum v) const { return v == Type::IfcDuctSilencerType || IfcFlowTreatmentDeviceType::is(v); }
Type::Enum IfcDuctSilencerType::type() const { return Type::IfcDuctSilencerType; }
Type::Enum IfcDuctSilencerType::Class() { return Type::IfcDuctSilencerType; }
IfcDuctSilencerType::IfcDuctSilencerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDuctSilencerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEdge
IfcVertex* IfcEdge::EdgeStart() { return reinterpret_pointer_cast<IfcBaseClass,IfcVertex>(*entity->getArgument(0)); }
IfcVertex* IfcEdge::EdgeEnd() { return reinterpret_pointer_cast<IfcBaseClass,IfcVertex>(*entity->getArgument(1)); }
bool IfcEdge::is(Type::Enum v) const { return v == Type::IfcEdge || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcEdge::type() const { return Type::IfcEdge; }
Type::Enum IfcEdge::Class() { return Type::IfcEdge; }
IfcEdge::IfcEdge(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdge)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEdgeCurve
IfcCurve* IfcEdgeCurve::EdgeGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
bool IfcEdgeCurve::SameSense() { return *entity->getArgument(3); }
bool IfcEdgeCurve::is(Type::Enum v) const { return v == Type::IfcEdgeCurve || IfcEdge::is(v); }
Type::Enum IfcEdgeCurve::type() const { return Type::IfcEdgeCurve; }
Type::Enum IfcEdgeCurve::Class() { return Type::IfcEdgeCurve; }
IfcEdgeCurve::IfcEdgeCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdgeCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEdgeFeature
bool IfcEdgeFeature::hasFeatureLength() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcEdgeFeature::FeatureLength() { return *entity->getArgument(8); }
bool IfcEdgeFeature::is(Type::Enum v) const { return v == Type::IfcEdgeFeature || IfcFeatureElementSubtraction::is(v); }
Type::Enum IfcEdgeFeature::type() const { return Type::IfcEdgeFeature; }
Type::Enum IfcEdgeFeature::Class() { return Type::IfcEdgeFeature; }
IfcEdgeFeature::IfcEdgeFeature(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdgeFeature)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEdgeLoop
SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > IfcEdgeLoop::EdgeList() { RETURN_AS_LIST(IfcOrientedEdge,0) }
bool IfcEdgeLoop::is(Type::Enum v) const { return v == Type::IfcEdgeLoop || IfcLoop::is(v); }
Type::Enum IfcEdgeLoop::type() const { return Type::IfcEdgeLoop; }
Type::Enum IfcEdgeLoop::Class() { return Type::IfcEdgeLoop; }
IfcEdgeLoop::IfcEdgeLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdgeLoop)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricApplianceType
IfcElectricApplianceTypeEnum::IfcElectricApplianceTypeEnum IfcElectricApplianceType::PredefinedType() { return IfcElectricApplianceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricApplianceType::is(Type::Enum v) const { return v == Type::IfcElectricApplianceType || IfcFlowTerminalType::is(v); }
Type::Enum IfcElectricApplianceType::type() const { return Type::IfcElectricApplianceType; }
Type::Enum IfcElectricApplianceType::Class() { return Type::IfcElectricApplianceType; }
IfcElectricApplianceType::IfcElectricApplianceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricApplianceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricDistributionPoint
IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunctionEnum IfcElectricDistributionPoint::DistributionPointFunction() { return IfcElectricDistributionPointFunctionEnum::FromString(*entity->getArgument(8)); }
bool IfcElectricDistributionPoint::hasUserDefinedFunction() { return !entity->getArgument(9)->isNull(); }
IfcLabel IfcElectricDistributionPoint::UserDefinedFunction() { return *entity->getArgument(9); }
bool IfcElectricDistributionPoint::is(Type::Enum v) const { return v == Type::IfcElectricDistributionPoint || IfcFlowController::is(v); }
Type::Enum IfcElectricDistributionPoint::type() const { return Type::IfcElectricDistributionPoint; }
Type::Enum IfcElectricDistributionPoint::Class() { return Type::IfcElectricDistributionPoint; }
IfcElectricDistributionPoint::IfcElectricDistributionPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricDistributionPoint)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricFlowStorageDeviceType
IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceTypeEnum IfcElectricFlowStorageDeviceType::PredefinedType() { return IfcElectricFlowStorageDeviceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricFlowStorageDeviceType::is(Type::Enum v) const { return v == Type::IfcElectricFlowStorageDeviceType || IfcFlowStorageDeviceType::is(v); }
Type::Enum IfcElectricFlowStorageDeviceType::type() const { return Type::IfcElectricFlowStorageDeviceType; }
Type::Enum IfcElectricFlowStorageDeviceType::Class() { return Type::IfcElectricFlowStorageDeviceType; }
IfcElectricFlowStorageDeviceType::IfcElectricFlowStorageDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricFlowStorageDeviceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricGeneratorType
IfcElectricGeneratorTypeEnum::IfcElectricGeneratorTypeEnum IfcElectricGeneratorType::PredefinedType() { return IfcElectricGeneratorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricGeneratorType::is(Type::Enum v) const { return v == Type::IfcElectricGeneratorType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcElectricGeneratorType::type() const { return Type::IfcElectricGeneratorType; }
Type::Enum IfcElectricGeneratorType::Class() { return Type::IfcElectricGeneratorType; }
IfcElectricGeneratorType::IfcElectricGeneratorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricGeneratorType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricHeaterType
IfcElectricHeaterTypeEnum::IfcElectricHeaterTypeEnum IfcElectricHeaterType::PredefinedType() { return IfcElectricHeaterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricHeaterType::is(Type::Enum v) const { return v == Type::IfcElectricHeaterType || IfcFlowTerminalType::is(v); }
Type::Enum IfcElectricHeaterType::type() const { return Type::IfcElectricHeaterType; }
Type::Enum IfcElectricHeaterType::Class() { return Type::IfcElectricHeaterType; }
IfcElectricHeaterType::IfcElectricHeaterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricHeaterType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricMotorType
IfcElectricMotorTypeEnum::IfcElectricMotorTypeEnum IfcElectricMotorType::PredefinedType() { return IfcElectricMotorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricMotorType::is(Type::Enum v) const { return v == Type::IfcElectricMotorType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcElectricMotorType::type() const { return Type::IfcElectricMotorType; }
Type::Enum IfcElectricMotorType::Class() { return Type::IfcElectricMotorType; }
IfcElectricMotorType::IfcElectricMotorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricMotorType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricTimeControlType
IfcElectricTimeControlTypeEnum::IfcElectricTimeControlTypeEnum IfcElectricTimeControlType::PredefinedType() { return IfcElectricTimeControlTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricTimeControlType::is(Type::Enum v) const { return v == Type::IfcElectricTimeControlType || IfcFlowControllerType::is(v); }
Type::Enum IfcElectricTimeControlType::type() const { return Type::IfcElectricTimeControlType; }
Type::Enum IfcElectricTimeControlType::Class() { return Type::IfcElectricTimeControlType; }
IfcElectricTimeControlType::IfcElectricTimeControlType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricTimeControlType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricalBaseProperties
bool IfcElectricalBaseProperties::hasElectricCurrentType() { return !entity->getArgument(6)->isNull(); }
IfcElectricCurrentEnum::IfcElectricCurrentEnum IfcElectricalBaseProperties::ElectricCurrentType() { return IfcElectricCurrentEnum::FromString(*entity->getArgument(6)); }
IfcElectricVoltageMeasure IfcElectricalBaseProperties::InputVoltage() { return *entity->getArgument(7); }
IfcFrequencyMeasure IfcElectricalBaseProperties::InputFrequency() { return *entity->getArgument(8); }
bool IfcElectricalBaseProperties::hasFullLoadCurrent() { return !entity->getArgument(9)->isNull(); }
IfcElectricCurrentMeasure IfcElectricalBaseProperties::FullLoadCurrent() { return *entity->getArgument(9); }
bool IfcElectricalBaseProperties::hasMinimumCircuitCurrent() { return !entity->getArgument(10)->isNull(); }
IfcElectricCurrentMeasure IfcElectricalBaseProperties::MinimumCircuitCurrent() { return *entity->getArgument(10); }
bool IfcElectricalBaseProperties::hasMaximumPowerInput() { return !entity->getArgument(11)->isNull(); }
IfcPowerMeasure IfcElectricalBaseProperties::MaximumPowerInput() { return *entity->getArgument(11); }
bool IfcElectricalBaseProperties::hasRatedPowerInput() { return !entity->getArgument(12)->isNull(); }
IfcPowerMeasure IfcElectricalBaseProperties::RatedPowerInput() { return *entity->getArgument(12); }
int IfcElectricalBaseProperties::InputPhase() { return *entity->getArgument(13); }
bool IfcElectricalBaseProperties::is(Type::Enum v) const { return v == Type::IfcElectricalBaseProperties || IfcEnergyProperties::is(v); }
Type::Enum IfcElectricalBaseProperties::type() const { return Type::IfcElectricalBaseProperties; }
Type::Enum IfcElectricalBaseProperties::Class() { return Type::IfcElectricalBaseProperties; }
IfcElectricalBaseProperties::IfcElectricalBaseProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricalBaseProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricalCircuit
bool IfcElectricalCircuit::is(Type::Enum v) const { return v == Type::IfcElectricalCircuit || IfcSystem::is(v); }
Type::Enum IfcElectricalCircuit::type() const { return Type::IfcElectricalCircuit; }
Type::Enum IfcElectricalCircuit::Class() { return Type::IfcElectricalCircuit; }
IfcElectricalCircuit::IfcElectricalCircuit(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricalCircuit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElectricalElement
bool IfcElectricalElement::is(Type::Enum v) const { return v == Type::IfcElectricalElement || IfcElement::is(v); }
Type::Enum IfcElectricalElement::type() const { return Type::IfcElectricalElement; }
Type::Enum IfcElectricalElement::Class() { return Type::IfcElectricalElement; }
IfcElectricalElement::IfcElectricalElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricalElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElement
bool IfcElement::hasTag() { return !entity->getArgument(7)->isNull(); }
IfcIdentifier IfcElement::Tag() { return *entity->getArgument(7); }
IfcRelConnectsStructuralElement::list IfcElement::HasStructuralMember() { RETURN_INVERSE(IfcRelConnectsStructuralElement) }
IfcRelFillsElement::list IfcElement::FillsVoids() { RETURN_INVERSE(IfcRelFillsElement) }
IfcRelConnectsElements::list IfcElement::ConnectedTo() { RETURN_INVERSE(IfcRelConnectsElements) }
IfcRelCoversBldgElements::list IfcElement::HasCoverings() { RETURN_INVERSE(IfcRelCoversBldgElements) }
IfcRelProjectsElement::list IfcElement::HasProjections() { RETURN_INVERSE(IfcRelProjectsElement) }
IfcRelReferencedInSpatialStructure::list IfcElement::ReferencedInStructures() { RETURN_INVERSE(IfcRelReferencedInSpatialStructure) }
IfcRelConnectsPortToElement::list IfcElement::HasPorts() { RETURN_INVERSE(IfcRelConnectsPortToElement) }
IfcRelVoidsElement::list IfcElement::HasOpenings() { RETURN_INVERSE(IfcRelVoidsElement) }
IfcRelConnectsWithRealizingElements::list IfcElement::IsConnectionRealization() { RETURN_INVERSE(IfcRelConnectsWithRealizingElements) }
IfcRelSpaceBoundary::list IfcElement::ProvidesBoundaries() { RETURN_INVERSE(IfcRelSpaceBoundary) }
IfcRelConnectsElements::list IfcElement::ConnectedFrom() { RETURN_INVERSE(IfcRelConnectsElements) }
IfcRelContainedInSpatialStructure::list IfcElement::ContainedInStructure() { RETURN_INVERSE(IfcRelContainedInSpatialStructure) }
bool IfcElement::is(Type::Enum v) const { return v == Type::IfcElement || IfcProduct::is(v); }
Type::Enum IfcElement::type() const { return Type::IfcElement; }
Type::Enum IfcElement::Class() { return Type::IfcElement; }
IfcElement::IfcElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElementAssembly
bool IfcElementAssembly::hasAssemblyPlace() { return !entity->getArgument(8)->isNull(); }
IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum IfcElementAssembly::AssemblyPlace() { return IfcAssemblyPlaceEnum::FromString(*entity->getArgument(8)); }
IfcElementAssemblyTypeEnum::IfcElementAssemblyTypeEnum IfcElementAssembly::PredefinedType() { return IfcElementAssemblyTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElementAssembly::is(Type::Enum v) const { return v == Type::IfcElementAssembly || IfcElement::is(v); }
Type::Enum IfcElementAssembly::type() const { return Type::IfcElementAssembly; }
Type::Enum IfcElementAssembly::Class() { return Type::IfcElementAssembly; }
IfcElementAssembly::IfcElementAssembly(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementAssembly)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElementComponent
bool IfcElementComponent::is(Type::Enum v) const { return v == Type::IfcElementComponent || IfcElement::is(v); }
Type::Enum IfcElementComponent::type() const { return Type::IfcElementComponent; }
Type::Enum IfcElementComponent::Class() { return Type::IfcElementComponent; }
IfcElementComponent::IfcElementComponent(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementComponent)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElementComponentType
bool IfcElementComponentType::is(Type::Enum v) const { return v == Type::IfcElementComponentType || IfcElementType::is(v); }
Type::Enum IfcElementComponentType::type() const { return Type::IfcElementComponentType; }
Type::Enum IfcElementComponentType::Class() { return Type::IfcElementComponentType; }
IfcElementComponentType::IfcElementComponentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementComponentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElementQuantity
bool IfcElementQuantity::hasMethodOfMeasurement() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcElementQuantity::MethodOfMeasurement() { return *entity->getArgument(4); }
SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > IfcElementQuantity::Quantities() { RETURN_AS_LIST(IfcPhysicalQuantity,5) }
bool IfcElementQuantity::is(Type::Enum v) const { return v == Type::IfcElementQuantity || IfcPropertySetDefinition::is(v); }
Type::Enum IfcElementQuantity::type() const { return Type::IfcElementQuantity; }
Type::Enum IfcElementQuantity::Class() { return Type::IfcElementQuantity; }
IfcElementQuantity::IfcElementQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementQuantity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElementType
bool IfcElementType::hasElementType() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcElementType::ElementType() { return *entity->getArgument(8); }
bool IfcElementType::is(Type::Enum v) const { return v == Type::IfcElementType || IfcTypeProduct::is(v); }
Type::Enum IfcElementType::type() const { return Type::IfcElementType; }
Type::Enum IfcElementType::Class() { return Type::IfcElementType; }
IfcElementType::IfcElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcElementarySurface
IfcAxis2Placement3D* IfcElementarySurface::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(0)); }
bool IfcElementarySurface::is(Type::Enum v) const { return v == Type::IfcElementarySurface || IfcSurface::is(v); }
Type::Enum IfcElementarySurface::type() const { return Type::IfcElementarySurface; }
Type::Enum IfcElementarySurface::Class() { return Type::IfcElementarySurface; }
IfcElementarySurface::IfcElementarySurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementarySurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEllipse
IfcPositiveLengthMeasure IfcEllipse::SemiAxis1() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcEllipse::SemiAxis2() { return *entity->getArgument(2); }
bool IfcEllipse::is(Type::Enum v) const { return v == Type::IfcEllipse || IfcConic::is(v); }
Type::Enum IfcEllipse::type() const { return Type::IfcEllipse; }
Type::Enum IfcEllipse::Class() { return Type::IfcEllipse; }
IfcEllipse::IfcEllipse(IfcAbstractEntityPtr e) { if (!is(Type::IfcEllipse)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEllipseProfileDef
IfcPositiveLengthMeasure IfcEllipseProfileDef::SemiAxis1() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcEllipseProfileDef::SemiAxis2() { return *entity->getArgument(4); }
bool IfcEllipseProfileDef::is(Type::Enum v) const { return v == Type::IfcEllipseProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcEllipseProfileDef::type() const { return Type::IfcEllipseProfileDef; }
Type::Enum IfcEllipseProfileDef::Class() { return Type::IfcEllipseProfileDef; }
IfcEllipseProfileDef::IfcEllipseProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcEllipseProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEnergyConversionDevice
bool IfcEnergyConversionDevice::is(Type::Enum v) const { return v == Type::IfcEnergyConversionDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcEnergyConversionDevice::type() const { return Type::IfcEnergyConversionDevice; }
Type::Enum IfcEnergyConversionDevice::Class() { return Type::IfcEnergyConversionDevice; }
IfcEnergyConversionDevice::IfcEnergyConversionDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnergyConversionDevice)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEnergyConversionDeviceType
bool IfcEnergyConversionDeviceType::is(Type::Enum v) const { return v == Type::IfcEnergyConversionDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcEnergyConversionDeviceType::type() const { return Type::IfcEnergyConversionDeviceType; }
Type::Enum IfcEnergyConversionDeviceType::Class() { return Type::IfcEnergyConversionDeviceType; }
IfcEnergyConversionDeviceType::IfcEnergyConversionDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnergyConversionDeviceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEnergyProperties
bool IfcEnergyProperties::hasEnergySequence() { return !entity->getArgument(4)->isNull(); }
IfcEnergySequenceEnum::IfcEnergySequenceEnum IfcEnergyProperties::EnergySequence() { return IfcEnergySequenceEnum::FromString(*entity->getArgument(4)); }
bool IfcEnergyProperties::hasUserDefinedEnergySequence() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcEnergyProperties::UserDefinedEnergySequence() { return *entity->getArgument(5); }
bool IfcEnergyProperties::is(Type::Enum v) const { return v == Type::IfcEnergyProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcEnergyProperties::type() const { return Type::IfcEnergyProperties; }
Type::Enum IfcEnergyProperties::Class() { return Type::IfcEnergyProperties; }
IfcEnergyProperties::IfcEnergyProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnergyProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEnvironmentalImpactValue
IfcLabel IfcEnvironmentalImpactValue::ImpactType() { return *entity->getArgument(6); }
IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategoryEnum IfcEnvironmentalImpactValue::Category() { return IfcEnvironmentalImpactCategoryEnum::FromString(*entity->getArgument(7)); }
bool IfcEnvironmentalImpactValue::hasUserDefinedCategory() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcEnvironmentalImpactValue::UserDefinedCategory() { return *entity->getArgument(8); }
bool IfcEnvironmentalImpactValue::is(Type::Enum v) const { return v == Type::IfcEnvironmentalImpactValue || IfcAppliedValue::is(v); }
Type::Enum IfcEnvironmentalImpactValue::type() const { return Type::IfcEnvironmentalImpactValue; }
Type::Enum IfcEnvironmentalImpactValue::Class() { return Type::IfcEnvironmentalImpactValue; }
IfcEnvironmentalImpactValue::IfcEnvironmentalImpactValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnvironmentalImpactValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEquipmentElement
bool IfcEquipmentElement::is(Type::Enum v) const { return v == Type::IfcEquipmentElement || IfcElement::is(v); }
Type::Enum IfcEquipmentElement::type() const { return Type::IfcEquipmentElement; }
Type::Enum IfcEquipmentElement::Class() { return Type::IfcEquipmentElement; }
IfcEquipmentElement::IfcEquipmentElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcEquipmentElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEquipmentStandard
bool IfcEquipmentStandard::is(Type::Enum v) const { return v == Type::IfcEquipmentStandard || IfcControl::is(v); }
Type::Enum IfcEquipmentStandard::type() const { return Type::IfcEquipmentStandard; }
Type::Enum IfcEquipmentStandard::Class() { return Type::IfcEquipmentStandard; }
IfcEquipmentStandard::IfcEquipmentStandard(IfcAbstractEntityPtr e) { if (!is(Type::IfcEquipmentStandard)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEvaporativeCoolerType
IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerTypeEnum IfcEvaporativeCoolerType::PredefinedType() { return IfcEvaporativeCoolerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcEvaporativeCoolerType::is(Type::Enum v) const { return v == Type::IfcEvaporativeCoolerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcEvaporativeCoolerType::type() const { return Type::IfcEvaporativeCoolerType; }
Type::Enum IfcEvaporativeCoolerType::Class() { return Type::IfcEvaporativeCoolerType; }
IfcEvaporativeCoolerType::IfcEvaporativeCoolerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcEvaporativeCoolerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcEvaporatorType
IfcEvaporatorTypeEnum::IfcEvaporatorTypeEnum IfcEvaporatorType::PredefinedType() { return IfcEvaporatorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcEvaporatorType::is(Type::Enum v) const { return v == Type::IfcEvaporatorType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcEvaporatorType::type() const { return Type::IfcEvaporatorType; }
Type::Enum IfcEvaporatorType::Class() { return Type::IfcEvaporatorType; }
IfcEvaporatorType::IfcEvaporatorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcEvaporatorType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcExtendedMaterialProperties
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcExtendedMaterialProperties::ExtendedProperties() { RETURN_AS_LIST(IfcProperty,1) }
bool IfcExtendedMaterialProperties::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcExtendedMaterialProperties::Description() { return *entity->getArgument(2); }
IfcLabel IfcExtendedMaterialProperties::Name() { return *entity->getArgument(3); }
bool IfcExtendedMaterialProperties::is(Type::Enum v) const { return v == Type::IfcExtendedMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcExtendedMaterialProperties::type() const { return Type::IfcExtendedMaterialProperties; }
Type::Enum IfcExtendedMaterialProperties::Class() { return Type::IfcExtendedMaterialProperties; }
IfcExtendedMaterialProperties::IfcExtendedMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcExtendedMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcExternalReference
bool IfcExternalReference::hasLocation() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcExternalReference::Location() { return *entity->getArgument(0); }
bool IfcExternalReference::hasItemReference() { return !entity->getArgument(1)->isNull(); }
IfcIdentifier IfcExternalReference::ItemReference() { return *entity->getArgument(1); }
bool IfcExternalReference::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcExternalReference::Name() { return *entity->getArgument(2); }
bool IfcExternalReference::is(Type::Enum v) const { return v == Type::IfcExternalReference; }
Type::Enum IfcExternalReference::type() const { return Type::IfcExternalReference; }
Type::Enum IfcExternalReference::Class() { return Type::IfcExternalReference; }
IfcExternalReference::IfcExternalReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternalReference)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcExternallyDefinedHatchStyle
bool IfcExternallyDefinedHatchStyle::is(Type::Enum v) const { return v == Type::IfcExternallyDefinedHatchStyle || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedHatchStyle::type() const { return Type::IfcExternallyDefinedHatchStyle; }
Type::Enum IfcExternallyDefinedHatchStyle::Class() { return Type::IfcExternallyDefinedHatchStyle; }
IfcExternallyDefinedHatchStyle::IfcExternallyDefinedHatchStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedHatchStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcExternallyDefinedSurfaceStyle
bool IfcExternallyDefinedSurfaceStyle::is(Type::Enum v) const { return v == Type::IfcExternallyDefinedSurfaceStyle || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedSurfaceStyle::type() const { return Type::IfcExternallyDefinedSurfaceStyle; }
Type::Enum IfcExternallyDefinedSurfaceStyle::Class() { return Type::IfcExternallyDefinedSurfaceStyle; }
IfcExternallyDefinedSurfaceStyle::IfcExternallyDefinedSurfaceStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedSurfaceStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcExternallyDefinedSymbol
bool IfcExternallyDefinedSymbol::is(Type::Enum v) const { return v == Type::IfcExternallyDefinedSymbol || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedSymbol::type() const { return Type::IfcExternallyDefinedSymbol; }
Type::Enum IfcExternallyDefinedSymbol::Class() { return Type::IfcExternallyDefinedSymbol; }
IfcExternallyDefinedSymbol::IfcExternallyDefinedSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedSymbol)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcExternallyDefinedTextFont
bool IfcExternallyDefinedTextFont::is(Type::Enum v) const { return v == Type::IfcExternallyDefinedTextFont || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedTextFont::type() const { return Type::IfcExternallyDefinedTextFont; }
Type::Enum IfcExternallyDefinedTextFont::Class() { return Type::IfcExternallyDefinedTextFont; }
IfcExternallyDefinedTextFont::IfcExternallyDefinedTextFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedTextFont)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcExtrudedAreaSolid
IfcDirection* IfcExtrudedAreaSolid::ExtrudedDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(2)); }
IfcPositiveLengthMeasure IfcExtrudedAreaSolid::Depth() { return *entity->getArgument(3); }
bool IfcExtrudedAreaSolid::is(Type::Enum v) const { return v == Type::IfcExtrudedAreaSolid || IfcSweptAreaSolid::is(v); }
Type::Enum IfcExtrudedAreaSolid::type() const { return Type::IfcExtrudedAreaSolid; }
Type::Enum IfcExtrudedAreaSolid::Class() { return Type::IfcExtrudedAreaSolid; }
IfcExtrudedAreaSolid::IfcExtrudedAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcExtrudedAreaSolid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFace
SHARED_PTR< IfcTemplatedEntityList<IfcFaceBound> > IfcFace::Bounds() { RETURN_AS_LIST(IfcFaceBound,0) }
bool IfcFace::is(Type::Enum v) const { return v == Type::IfcFace || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcFace::type() const { return Type::IfcFace; }
Type::Enum IfcFace::Class() { return Type::IfcFace; }
IfcFace::IfcFace(IfcAbstractEntityPtr e) { if (!is(Type::IfcFace)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFaceBasedSurfaceModel
SHARED_PTR< IfcTemplatedEntityList<IfcConnectedFaceSet> > IfcFaceBasedSurfaceModel::FbsmFaces() { RETURN_AS_LIST(IfcConnectedFaceSet,0) }
bool IfcFaceBasedSurfaceModel::is(Type::Enum v) const { return v == Type::IfcFaceBasedSurfaceModel || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFaceBasedSurfaceModel::type() const { return Type::IfcFaceBasedSurfaceModel; }
Type::Enum IfcFaceBasedSurfaceModel::Class() { return Type::IfcFaceBasedSurfaceModel; }
IfcFaceBasedSurfaceModel::IfcFaceBasedSurfaceModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceBasedSurfaceModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFaceBound
IfcLoop* IfcFaceBound::Bound() { return reinterpret_pointer_cast<IfcBaseClass,IfcLoop>(*entity->getArgument(0)); }
bool IfcFaceBound::Orientation() { return *entity->getArgument(1); }
bool IfcFaceBound::is(Type::Enum v) const { return v == Type::IfcFaceBound || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcFaceBound::type() const { return Type::IfcFaceBound; }
Type::Enum IfcFaceBound::Class() { return Type::IfcFaceBound; }
IfcFaceBound::IfcFaceBound(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceBound)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFaceOuterBound
bool IfcFaceOuterBound::is(Type::Enum v) const { return v == Type::IfcFaceOuterBound || IfcFaceBound::is(v); }
Type::Enum IfcFaceOuterBound::type() const { return Type::IfcFaceOuterBound; }
Type::Enum IfcFaceOuterBound::Class() { return Type::IfcFaceOuterBound; }
IfcFaceOuterBound::IfcFaceOuterBound(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceOuterBound)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFaceSurface
IfcSurface* IfcFaceSurface::FaceSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(1)); }
bool IfcFaceSurface::SameSense() { return *entity->getArgument(2); }
bool IfcFaceSurface::is(Type::Enum v) const { return v == Type::IfcFaceSurface || IfcFace::is(v); }
Type::Enum IfcFaceSurface::type() const { return Type::IfcFaceSurface; }
Type::Enum IfcFaceSurface::Class() { return Type::IfcFaceSurface; }
IfcFaceSurface::IfcFaceSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceSurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFacetedBrep
bool IfcFacetedBrep::is(Type::Enum v) const { return v == Type::IfcFacetedBrep || IfcManifoldSolidBrep::is(v); }
Type::Enum IfcFacetedBrep::type() const { return Type::IfcFacetedBrep; }
Type::Enum IfcFacetedBrep::Class() { return Type::IfcFacetedBrep; }
IfcFacetedBrep::IfcFacetedBrep(IfcAbstractEntityPtr e) { if (!is(Type::IfcFacetedBrep)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFacetedBrepWithVoids
SHARED_PTR< IfcTemplatedEntityList<IfcClosedShell> > IfcFacetedBrepWithVoids::Voids() { RETURN_AS_LIST(IfcClosedShell,1) }
bool IfcFacetedBrepWithVoids::is(Type::Enum v) const { return v == Type::IfcFacetedBrepWithVoids || IfcManifoldSolidBrep::is(v); }
Type::Enum IfcFacetedBrepWithVoids::type() const { return Type::IfcFacetedBrepWithVoids; }
Type::Enum IfcFacetedBrepWithVoids::Class() { return Type::IfcFacetedBrepWithVoids; }
IfcFacetedBrepWithVoids::IfcFacetedBrepWithVoids(IfcAbstractEntityPtr e) { if (!is(Type::IfcFacetedBrepWithVoids)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFailureConnectionCondition
bool IfcFailureConnectionCondition::hasTensionFailureX() { return !entity->getArgument(1)->isNull(); }
IfcForceMeasure IfcFailureConnectionCondition::TensionFailureX() { return *entity->getArgument(1); }
bool IfcFailureConnectionCondition::hasTensionFailureY() { return !entity->getArgument(2)->isNull(); }
IfcForceMeasure IfcFailureConnectionCondition::TensionFailureY() { return *entity->getArgument(2); }
bool IfcFailureConnectionCondition::hasTensionFailureZ() { return !entity->getArgument(3)->isNull(); }
IfcForceMeasure IfcFailureConnectionCondition::TensionFailureZ() { return *entity->getArgument(3); }
bool IfcFailureConnectionCondition::hasCompressionFailureX() { return !entity->getArgument(4)->isNull(); }
IfcForceMeasure IfcFailureConnectionCondition::CompressionFailureX() { return *entity->getArgument(4); }
bool IfcFailureConnectionCondition::hasCompressionFailureY() { return !entity->getArgument(5)->isNull(); }
IfcForceMeasure IfcFailureConnectionCondition::CompressionFailureY() { return *entity->getArgument(5); }
bool IfcFailureConnectionCondition::hasCompressionFailureZ() { return !entity->getArgument(6)->isNull(); }
IfcForceMeasure IfcFailureConnectionCondition::CompressionFailureZ() { return *entity->getArgument(6); }
bool IfcFailureConnectionCondition::is(Type::Enum v) const { return v == Type::IfcFailureConnectionCondition || IfcStructuralConnectionCondition::is(v); }
Type::Enum IfcFailureConnectionCondition::type() const { return Type::IfcFailureConnectionCondition; }
Type::Enum IfcFailureConnectionCondition::Class() { return Type::IfcFailureConnectionCondition; }
IfcFailureConnectionCondition::IfcFailureConnectionCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcFailureConnectionCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFanType
IfcFanTypeEnum::IfcFanTypeEnum IfcFanType::PredefinedType() { return IfcFanTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFanType::is(Type::Enum v) const { return v == Type::IfcFanType || IfcFlowMovingDeviceType::is(v); }
Type::Enum IfcFanType::type() const { return Type::IfcFanType; }
Type::Enum IfcFanType::Class() { return Type::IfcFanType; }
IfcFanType::IfcFanType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFanType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFastener
bool IfcFastener::is(Type::Enum v) const { return v == Type::IfcFastener || IfcElementComponent::is(v); }
Type::Enum IfcFastener::type() const { return Type::IfcFastener; }
Type::Enum IfcFastener::Class() { return Type::IfcFastener; }
IfcFastener::IfcFastener(IfcAbstractEntityPtr e) { if (!is(Type::IfcFastener)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFastenerType
bool IfcFastenerType::is(Type::Enum v) const { return v == Type::IfcFastenerType || IfcElementComponentType::is(v); }
Type::Enum IfcFastenerType::type() const { return Type::IfcFastenerType; }
Type::Enum IfcFastenerType::Class() { return Type::IfcFastenerType; }
IfcFastenerType::IfcFastenerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFastenerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFeatureElement
bool IfcFeatureElement::is(Type::Enum v) const { return v == Type::IfcFeatureElement || IfcElement::is(v); }
Type::Enum IfcFeatureElement::type() const { return Type::IfcFeatureElement; }
Type::Enum IfcFeatureElement::Class() { return Type::IfcFeatureElement; }
IfcFeatureElement::IfcFeatureElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcFeatureElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFeatureElementAddition
IfcRelProjectsElement::list IfcFeatureElementAddition::ProjectsElements() { RETURN_INVERSE(IfcRelProjectsElement) }
bool IfcFeatureElementAddition::is(Type::Enum v) const { return v == Type::IfcFeatureElementAddition || IfcFeatureElement::is(v); }
Type::Enum IfcFeatureElementAddition::type() const { return Type::IfcFeatureElementAddition; }
Type::Enum IfcFeatureElementAddition::Class() { return Type::IfcFeatureElementAddition; }
IfcFeatureElementAddition::IfcFeatureElementAddition(IfcAbstractEntityPtr e) { if (!is(Type::IfcFeatureElementAddition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFeatureElementSubtraction
IfcRelVoidsElement::list IfcFeatureElementSubtraction::VoidsElements() { RETURN_INVERSE(IfcRelVoidsElement) }
bool IfcFeatureElementSubtraction::is(Type::Enum v) const { return v == Type::IfcFeatureElementSubtraction || IfcFeatureElement::is(v); }
Type::Enum IfcFeatureElementSubtraction::type() const { return Type::IfcFeatureElementSubtraction; }
Type::Enum IfcFeatureElementSubtraction::Class() { return Type::IfcFeatureElementSubtraction; }
IfcFeatureElementSubtraction::IfcFeatureElementSubtraction(IfcAbstractEntityPtr e) { if (!is(Type::IfcFeatureElementSubtraction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFillAreaStyle
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcFillAreaStyle::FillStyles() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcFillAreaStyle::is(Type::Enum v) const { return v == Type::IfcFillAreaStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcFillAreaStyle::type() const { return Type::IfcFillAreaStyle; }
Type::Enum IfcFillAreaStyle::Class() { return Type::IfcFillAreaStyle; }
IfcFillAreaStyle::IfcFillAreaStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFillAreaStyleHatching
IfcCurveStyle* IfcFillAreaStyleHatching::HatchLineAppearance() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurveStyle>(*entity->getArgument(0)); }
IfcHatchLineDistanceSelect IfcFillAreaStyleHatching::StartOfNextHatchLine() { return *entity->getArgument(1); }
bool IfcFillAreaStyleHatching::hasPointOfReferenceHatchLine() { return !entity->getArgument(2)->isNull(); }
IfcCartesianPoint* IfcFillAreaStyleHatching::PointOfReferenceHatchLine() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(2)); }
bool IfcFillAreaStyleHatching::hasPatternStart() { return !entity->getArgument(3)->isNull(); }
IfcCartesianPoint* IfcFillAreaStyleHatching::PatternStart() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(3)); }
IfcPlaneAngleMeasure IfcFillAreaStyleHatching::HatchLineAngle() { return *entity->getArgument(4); }
bool IfcFillAreaStyleHatching::is(Type::Enum v) const { return v == Type::IfcFillAreaStyleHatching || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFillAreaStyleHatching::type() const { return Type::IfcFillAreaStyleHatching; }
Type::Enum IfcFillAreaStyleHatching::Class() { return Type::IfcFillAreaStyleHatching; }
IfcFillAreaStyleHatching::IfcFillAreaStyleHatching(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyleHatching)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFillAreaStyleTileSymbolWithStyle
IfcAnnotationSymbolOccurrence* IfcFillAreaStyleTileSymbolWithStyle::Symbol() { return reinterpret_pointer_cast<IfcBaseClass,IfcAnnotationSymbolOccurrence>(*entity->getArgument(0)); }
bool IfcFillAreaStyleTileSymbolWithStyle::is(Type::Enum v) const { return v == Type::IfcFillAreaStyleTileSymbolWithStyle || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFillAreaStyleTileSymbolWithStyle::type() const { return Type::IfcFillAreaStyleTileSymbolWithStyle; }
Type::Enum IfcFillAreaStyleTileSymbolWithStyle::Class() { return Type::IfcFillAreaStyleTileSymbolWithStyle; }
IfcFillAreaStyleTileSymbolWithStyle::IfcFillAreaStyleTileSymbolWithStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyleTileSymbolWithStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFillAreaStyleTiles
IfcOneDirectionRepeatFactor* IfcFillAreaStyleTiles::TilingPattern() { return reinterpret_pointer_cast<IfcBaseClass,IfcOneDirectionRepeatFactor>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcFillAreaStyleTiles::Tiles() { RETURN_AS_LIST(IfcAbstractSelect,1) }
IfcPositiveRatioMeasure IfcFillAreaStyleTiles::TilingScale() { return *entity->getArgument(2); }
bool IfcFillAreaStyleTiles::is(Type::Enum v) const { return v == Type::IfcFillAreaStyleTiles || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFillAreaStyleTiles::type() const { return Type::IfcFillAreaStyleTiles; }
Type::Enum IfcFillAreaStyleTiles::Class() { return Type::IfcFillAreaStyleTiles; }
IfcFillAreaStyleTiles::IfcFillAreaStyleTiles(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyleTiles)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFilterType
IfcFilterTypeEnum::IfcFilterTypeEnum IfcFilterType::PredefinedType() { return IfcFilterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFilterType::is(Type::Enum v) const { return v == Type::IfcFilterType || IfcFlowTreatmentDeviceType::is(v); }
Type::Enum IfcFilterType::type() const { return Type::IfcFilterType; }
Type::Enum IfcFilterType::Class() { return Type::IfcFilterType; }
IfcFilterType::IfcFilterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFilterType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFireSuppressionTerminalType
IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalTypeEnum IfcFireSuppressionTerminalType::PredefinedType() { return IfcFireSuppressionTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFireSuppressionTerminalType::is(Type::Enum v) const { return v == Type::IfcFireSuppressionTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcFireSuppressionTerminalType::type() const { return Type::IfcFireSuppressionTerminalType; }
Type::Enum IfcFireSuppressionTerminalType::Class() { return Type::IfcFireSuppressionTerminalType; }
IfcFireSuppressionTerminalType::IfcFireSuppressionTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFireSuppressionTerminalType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowController
bool IfcFlowController::is(Type::Enum v) const { return v == Type::IfcFlowController || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowController::type() const { return Type::IfcFlowController; }
Type::Enum IfcFlowController::Class() { return Type::IfcFlowController; }
IfcFlowController::IfcFlowController(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowController)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowControllerType
bool IfcFlowControllerType::is(Type::Enum v) const { return v == Type::IfcFlowControllerType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowControllerType::type() const { return Type::IfcFlowControllerType; }
Type::Enum IfcFlowControllerType::Class() { return Type::IfcFlowControllerType; }
IfcFlowControllerType::IfcFlowControllerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowControllerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowFitting
bool IfcFlowFitting::is(Type::Enum v) const { return v == Type::IfcFlowFitting || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowFitting::type() const { return Type::IfcFlowFitting; }
Type::Enum IfcFlowFitting::Class() { return Type::IfcFlowFitting; }
IfcFlowFitting::IfcFlowFitting(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowFitting)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowFittingType
bool IfcFlowFittingType::is(Type::Enum v) const { return v == Type::IfcFlowFittingType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowFittingType::type() const { return Type::IfcFlowFittingType; }
Type::Enum IfcFlowFittingType::Class() { return Type::IfcFlowFittingType; }
IfcFlowFittingType::IfcFlowFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowFittingType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowInstrumentType
IfcFlowInstrumentTypeEnum::IfcFlowInstrumentTypeEnum IfcFlowInstrumentType::PredefinedType() { return IfcFlowInstrumentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFlowInstrumentType::is(Type::Enum v) const { return v == Type::IfcFlowInstrumentType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcFlowInstrumentType::type() const { return Type::IfcFlowInstrumentType; }
Type::Enum IfcFlowInstrumentType::Class() { return Type::IfcFlowInstrumentType; }
IfcFlowInstrumentType::IfcFlowInstrumentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowInstrumentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowMeterType
IfcFlowMeterTypeEnum::IfcFlowMeterTypeEnum IfcFlowMeterType::PredefinedType() { return IfcFlowMeterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFlowMeterType::is(Type::Enum v) const { return v == Type::IfcFlowMeterType || IfcFlowControllerType::is(v); }
Type::Enum IfcFlowMeterType::type() const { return Type::IfcFlowMeterType; }
Type::Enum IfcFlowMeterType::Class() { return Type::IfcFlowMeterType; }
IfcFlowMeterType::IfcFlowMeterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowMeterType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowMovingDevice
bool IfcFlowMovingDevice::is(Type::Enum v) const { return v == Type::IfcFlowMovingDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowMovingDevice::type() const { return Type::IfcFlowMovingDevice; }
Type::Enum IfcFlowMovingDevice::Class() { return Type::IfcFlowMovingDevice; }
IfcFlowMovingDevice::IfcFlowMovingDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowMovingDevice)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowMovingDeviceType
bool IfcFlowMovingDeviceType::is(Type::Enum v) const { return v == Type::IfcFlowMovingDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowMovingDeviceType::type() const { return Type::IfcFlowMovingDeviceType; }
Type::Enum IfcFlowMovingDeviceType::Class() { return Type::IfcFlowMovingDeviceType; }
IfcFlowMovingDeviceType::IfcFlowMovingDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowMovingDeviceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowSegment
bool IfcFlowSegment::is(Type::Enum v) const { return v == Type::IfcFlowSegment || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowSegment::type() const { return Type::IfcFlowSegment; }
Type::Enum IfcFlowSegment::Class() { return Type::IfcFlowSegment; }
IfcFlowSegment::IfcFlowSegment(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowSegment)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowSegmentType
bool IfcFlowSegmentType::is(Type::Enum v) const { return v == Type::IfcFlowSegmentType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowSegmentType::type() const { return Type::IfcFlowSegmentType; }
Type::Enum IfcFlowSegmentType::Class() { return Type::IfcFlowSegmentType; }
IfcFlowSegmentType::IfcFlowSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowSegmentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowStorageDevice
bool IfcFlowStorageDevice::is(Type::Enum v) const { return v == Type::IfcFlowStorageDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowStorageDevice::type() const { return Type::IfcFlowStorageDevice; }
Type::Enum IfcFlowStorageDevice::Class() { return Type::IfcFlowStorageDevice; }
IfcFlowStorageDevice::IfcFlowStorageDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowStorageDevice)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowStorageDeviceType
bool IfcFlowStorageDeviceType::is(Type::Enum v) const { return v == Type::IfcFlowStorageDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowStorageDeviceType::type() const { return Type::IfcFlowStorageDeviceType; }
Type::Enum IfcFlowStorageDeviceType::Class() { return Type::IfcFlowStorageDeviceType; }
IfcFlowStorageDeviceType::IfcFlowStorageDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowStorageDeviceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowTerminal
bool IfcFlowTerminal::is(Type::Enum v) const { return v == Type::IfcFlowTerminal || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowTerminal::type() const { return Type::IfcFlowTerminal; }
Type::Enum IfcFlowTerminal::Class() { return Type::IfcFlowTerminal; }
IfcFlowTerminal::IfcFlowTerminal(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTerminal)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowTerminalType
bool IfcFlowTerminalType::is(Type::Enum v) const { return v == Type::IfcFlowTerminalType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowTerminalType::type() const { return Type::IfcFlowTerminalType; }
Type::Enum IfcFlowTerminalType::Class() { return Type::IfcFlowTerminalType; }
IfcFlowTerminalType::IfcFlowTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTerminalType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowTreatmentDevice
bool IfcFlowTreatmentDevice::is(Type::Enum v) const { return v == Type::IfcFlowTreatmentDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowTreatmentDevice::type() const { return Type::IfcFlowTreatmentDevice; }
Type::Enum IfcFlowTreatmentDevice::Class() { return Type::IfcFlowTreatmentDevice; }
IfcFlowTreatmentDevice::IfcFlowTreatmentDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTreatmentDevice)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFlowTreatmentDeviceType
bool IfcFlowTreatmentDeviceType::is(Type::Enum v) const { return v == Type::IfcFlowTreatmentDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowTreatmentDeviceType::type() const { return Type::IfcFlowTreatmentDeviceType; }
Type::Enum IfcFlowTreatmentDeviceType::Class() { return Type::IfcFlowTreatmentDeviceType; }
IfcFlowTreatmentDeviceType::IfcFlowTreatmentDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTreatmentDeviceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFluidFlowProperties
IfcPropertySourceEnum::IfcPropertySourceEnum IfcFluidFlowProperties::PropertySource() { return IfcPropertySourceEnum::FromString(*entity->getArgument(4)); }
bool IfcFluidFlowProperties::hasFlowConditionTimeSeries() { return !entity->getArgument(5)->isNull(); }
IfcTimeSeries* IfcFluidFlowProperties::FlowConditionTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(5)); }
bool IfcFluidFlowProperties::hasVelocityTimeSeries() { return !entity->getArgument(6)->isNull(); }
IfcTimeSeries* IfcFluidFlowProperties::VelocityTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(6)); }
bool IfcFluidFlowProperties::hasFlowrateTimeSeries() { return !entity->getArgument(7)->isNull(); }
IfcTimeSeries* IfcFluidFlowProperties::FlowrateTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(7)); }
IfcMaterial* IfcFluidFlowProperties::Fluid() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(8)); }
bool IfcFluidFlowProperties::hasPressureTimeSeries() { return !entity->getArgument(9)->isNull(); }
IfcTimeSeries* IfcFluidFlowProperties::PressureTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(9)); }
bool IfcFluidFlowProperties::hasUserDefinedPropertySource() { return !entity->getArgument(10)->isNull(); }
IfcLabel IfcFluidFlowProperties::UserDefinedPropertySource() { return *entity->getArgument(10); }
bool IfcFluidFlowProperties::hasTemperatureSingleValue() { return !entity->getArgument(11)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcFluidFlowProperties::TemperatureSingleValue() { return *entity->getArgument(11); }
bool IfcFluidFlowProperties::hasWetBulbTemperatureSingleValue() { return !entity->getArgument(12)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcFluidFlowProperties::WetBulbTemperatureSingleValue() { return *entity->getArgument(12); }
bool IfcFluidFlowProperties::hasWetBulbTemperatureTimeSeries() { return !entity->getArgument(13)->isNull(); }
IfcTimeSeries* IfcFluidFlowProperties::WetBulbTemperatureTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(13)); }
bool IfcFluidFlowProperties::hasTemperatureTimeSeries() { return !entity->getArgument(14)->isNull(); }
IfcTimeSeries* IfcFluidFlowProperties::TemperatureTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(14)); }
bool IfcFluidFlowProperties::hasFlowrateSingleValue() { return !entity->getArgument(15)->isNull(); }
IfcDerivedMeasureValue IfcFluidFlowProperties::FlowrateSingleValue() { return *entity->getArgument(15); }
bool IfcFluidFlowProperties::hasFlowConditionSingleValue() { return !entity->getArgument(16)->isNull(); }
IfcPositiveRatioMeasure IfcFluidFlowProperties::FlowConditionSingleValue() { return *entity->getArgument(16); }
bool IfcFluidFlowProperties::hasVelocitySingleValue() { return !entity->getArgument(17)->isNull(); }
IfcLinearVelocityMeasure IfcFluidFlowProperties::VelocitySingleValue() { return *entity->getArgument(17); }
bool IfcFluidFlowProperties::hasPressureSingleValue() { return !entity->getArgument(18)->isNull(); }
IfcPressureMeasure IfcFluidFlowProperties::PressureSingleValue() { return *entity->getArgument(18); }
bool IfcFluidFlowProperties::is(Type::Enum v) const { return v == Type::IfcFluidFlowProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcFluidFlowProperties::type() const { return Type::IfcFluidFlowProperties; }
Type::Enum IfcFluidFlowProperties::Class() { return Type::IfcFluidFlowProperties; }
IfcFluidFlowProperties::IfcFluidFlowProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcFluidFlowProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFooting
IfcFootingTypeEnum::IfcFootingTypeEnum IfcFooting::PredefinedType() { return IfcFootingTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcFooting::is(Type::Enum v) const { return v == Type::IfcFooting || IfcBuildingElement::is(v); }
Type::Enum IfcFooting::type() const { return Type::IfcFooting; }
Type::Enum IfcFooting::Class() { return Type::IfcFooting; }
IfcFooting::IfcFooting(IfcAbstractEntityPtr e) { if (!is(Type::IfcFooting)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFuelProperties
bool IfcFuelProperties::hasCombustionTemperature() { return !entity->getArgument(1)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcFuelProperties::CombustionTemperature() { return *entity->getArgument(1); }
bool IfcFuelProperties::hasCarbonContent() { return !entity->getArgument(2)->isNull(); }
IfcPositiveRatioMeasure IfcFuelProperties::CarbonContent() { return *entity->getArgument(2); }
bool IfcFuelProperties::hasLowerHeatingValue() { return !entity->getArgument(3)->isNull(); }
IfcHeatingValueMeasure IfcFuelProperties::LowerHeatingValue() { return *entity->getArgument(3); }
bool IfcFuelProperties::hasHigherHeatingValue() { return !entity->getArgument(4)->isNull(); }
IfcHeatingValueMeasure IfcFuelProperties::HigherHeatingValue() { return *entity->getArgument(4); }
bool IfcFuelProperties::is(Type::Enum v) const { return v == Type::IfcFuelProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcFuelProperties::type() const { return Type::IfcFuelProperties; }
Type::Enum IfcFuelProperties::Class() { return Type::IfcFuelProperties; }
IfcFuelProperties::IfcFuelProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcFuelProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFurnishingElement
bool IfcFurnishingElement::is(Type::Enum v) const { return v == Type::IfcFurnishingElement || IfcElement::is(v); }
Type::Enum IfcFurnishingElement::type() const { return Type::IfcFurnishingElement; }
Type::Enum IfcFurnishingElement::Class() { return Type::IfcFurnishingElement; }
IfcFurnishingElement::IfcFurnishingElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnishingElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFurnishingElementType
bool IfcFurnishingElementType::is(Type::Enum v) const { return v == Type::IfcFurnishingElementType || IfcElementType::is(v); }
Type::Enum IfcFurnishingElementType::type() const { return Type::IfcFurnishingElementType; }
Type::Enum IfcFurnishingElementType::Class() { return Type::IfcFurnishingElementType; }
IfcFurnishingElementType::IfcFurnishingElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnishingElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFurnitureStandard
bool IfcFurnitureStandard::is(Type::Enum v) const { return v == Type::IfcFurnitureStandard || IfcControl::is(v); }
Type::Enum IfcFurnitureStandard::type() const { return Type::IfcFurnitureStandard; }
Type::Enum IfcFurnitureStandard::Class() { return Type::IfcFurnitureStandard; }
IfcFurnitureStandard::IfcFurnitureStandard(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnitureStandard)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcFurnitureType
IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum IfcFurnitureType::AssemblyPlace() { return IfcAssemblyPlaceEnum::FromString(*entity->getArgument(9)); }
bool IfcFurnitureType::is(Type::Enum v) const { return v == Type::IfcFurnitureType || IfcFurnishingElementType::is(v); }
Type::Enum IfcFurnitureType::type() const { return Type::IfcFurnitureType; }
Type::Enum IfcFurnitureType::Class() { return Type::IfcFurnitureType; }
IfcFurnitureType::IfcFurnitureType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnitureType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGasTerminalType
IfcGasTerminalTypeEnum::IfcGasTerminalTypeEnum IfcGasTerminalType::PredefinedType() { return IfcGasTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcGasTerminalType::is(Type::Enum v) const { return v == Type::IfcGasTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcGasTerminalType::type() const { return Type::IfcGasTerminalType; }
Type::Enum IfcGasTerminalType::Class() { return Type::IfcGasTerminalType; }
IfcGasTerminalType::IfcGasTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcGasTerminalType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGeneralMaterialProperties
bool IfcGeneralMaterialProperties::hasMolecularWeight() { return !entity->getArgument(1)->isNull(); }
IfcMolecularWeightMeasure IfcGeneralMaterialProperties::MolecularWeight() { return *entity->getArgument(1); }
bool IfcGeneralMaterialProperties::hasPorosity() { return !entity->getArgument(2)->isNull(); }
IfcNormalisedRatioMeasure IfcGeneralMaterialProperties::Porosity() { return *entity->getArgument(2); }
bool IfcGeneralMaterialProperties::hasMassDensity() { return !entity->getArgument(3)->isNull(); }
IfcMassDensityMeasure IfcGeneralMaterialProperties::MassDensity() { return *entity->getArgument(3); }
bool IfcGeneralMaterialProperties::is(Type::Enum v) const { return v == Type::IfcGeneralMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcGeneralMaterialProperties::type() const { return Type::IfcGeneralMaterialProperties; }
Type::Enum IfcGeneralMaterialProperties::Class() { return Type::IfcGeneralMaterialProperties; }
IfcGeneralMaterialProperties::IfcGeneralMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeneralMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGeneralProfileProperties
bool IfcGeneralProfileProperties::hasPhysicalWeight() { return !entity->getArgument(2)->isNull(); }
IfcMassPerLengthMeasure IfcGeneralProfileProperties::PhysicalWeight() { return *entity->getArgument(2); }
bool IfcGeneralProfileProperties::hasPerimeter() { return !entity->getArgument(3)->isNull(); }
IfcPositiveLengthMeasure IfcGeneralProfileProperties::Perimeter() { return *entity->getArgument(3); }
bool IfcGeneralProfileProperties::hasMinimumPlateThickness() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcGeneralProfileProperties::MinimumPlateThickness() { return *entity->getArgument(4); }
bool IfcGeneralProfileProperties::hasMaximumPlateThickness() { return !entity->getArgument(5)->isNull(); }
IfcPositiveLengthMeasure IfcGeneralProfileProperties::MaximumPlateThickness() { return *entity->getArgument(5); }
bool IfcGeneralProfileProperties::hasCrossSectionArea() { return !entity->getArgument(6)->isNull(); }
IfcAreaMeasure IfcGeneralProfileProperties::CrossSectionArea() { return *entity->getArgument(6); }
bool IfcGeneralProfileProperties::is(Type::Enum v) const { return v == Type::IfcGeneralProfileProperties || IfcProfileProperties::is(v); }
Type::Enum IfcGeneralProfileProperties::type() const { return Type::IfcGeneralProfileProperties; }
Type::Enum IfcGeneralProfileProperties::Class() { return Type::IfcGeneralProfileProperties; }
IfcGeneralProfileProperties::IfcGeneralProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeneralProfileProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGeometricCurveSet
bool IfcGeometricCurveSet::is(Type::Enum v) const { return v == Type::IfcGeometricCurveSet || IfcGeometricSet::is(v); }
Type::Enum IfcGeometricCurveSet::type() const { return Type::IfcGeometricCurveSet; }
Type::Enum IfcGeometricCurveSet::Class() { return Type::IfcGeometricCurveSet; }
IfcGeometricCurveSet::IfcGeometricCurveSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricCurveSet)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGeometricRepresentationContext
IfcDimensionCount IfcGeometricRepresentationContext::CoordinateSpaceDimension() { return *entity->getArgument(2); }
bool IfcGeometricRepresentationContext::hasPrecision() { return !entity->getArgument(3)->isNull(); }
double IfcGeometricRepresentationContext::Precision() { return *entity->getArgument(3); }
IfcAxis2Placement IfcGeometricRepresentationContext::WorldCoordinateSystem() { return *entity->getArgument(4); }
bool IfcGeometricRepresentationContext::hasTrueNorth() { return !entity->getArgument(5)->isNull(); }
IfcDirection* IfcGeometricRepresentationContext::TrueNorth() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(5)); }
IfcGeometricRepresentationSubContext::list IfcGeometricRepresentationContext::HasSubContexts() { RETURN_INVERSE(IfcGeometricRepresentationSubContext) }
bool IfcGeometricRepresentationContext::is(Type::Enum v) const { return v == Type::IfcGeometricRepresentationContext || IfcRepresentationContext::is(v); }
Type::Enum IfcGeometricRepresentationContext::type() const { return Type::IfcGeometricRepresentationContext; }
Type::Enum IfcGeometricRepresentationContext::Class() { return Type::IfcGeometricRepresentationContext; }
IfcGeometricRepresentationContext::IfcGeometricRepresentationContext(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricRepresentationContext)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGeometricRepresentationItem
bool IfcGeometricRepresentationItem::is(Type::Enum v) const { return v == Type::IfcGeometricRepresentationItem || IfcRepresentationItem::is(v); }
Type::Enum IfcGeometricRepresentationItem::type() const { return Type::IfcGeometricRepresentationItem; }
Type::Enum IfcGeometricRepresentationItem::Class() { return Type::IfcGeometricRepresentationItem; }
IfcGeometricRepresentationItem::IfcGeometricRepresentationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricRepresentationItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGeometricRepresentationSubContext
IfcGeometricRepresentationContext* IfcGeometricRepresentationSubContext::ParentContext() { return reinterpret_pointer_cast<IfcBaseClass,IfcGeometricRepresentationContext>(*entity->getArgument(6)); }
bool IfcGeometricRepresentationSubContext::hasTargetScale() { return !entity->getArgument(7)->isNull(); }
IfcPositiveRatioMeasure IfcGeometricRepresentationSubContext::TargetScale() { return *entity->getArgument(7); }
IfcGeometricProjectionEnum::IfcGeometricProjectionEnum IfcGeometricRepresentationSubContext::TargetView() { return IfcGeometricProjectionEnum::FromString(*entity->getArgument(8)); }
bool IfcGeometricRepresentationSubContext::hasUserDefinedTargetView() { return !entity->getArgument(9)->isNull(); }
IfcLabel IfcGeometricRepresentationSubContext::UserDefinedTargetView() { return *entity->getArgument(9); }
bool IfcGeometricRepresentationSubContext::is(Type::Enum v) const { return v == Type::IfcGeometricRepresentationSubContext || IfcGeometricRepresentationContext::is(v); }
Type::Enum IfcGeometricRepresentationSubContext::type() const { return Type::IfcGeometricRepresentationSubContext; }
Type::Enum IfcGeometricRepresentationSubContext::Class() { return Type::IfcGeometricRepresentationSubContext; }
IfcGeometricRepresentationSubContext::IfcGeometricRepresentationSubContext(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricRepresentationSubContext)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGeometricSet
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcGeometricSet::Elements() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcGeometricSet::is(Type::Enum v) const { return v == Type::IfcGeometricSet || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcGeometricSet::type() const { return Type::IfcGeometricSet; }
Type::Enum IfcGeometricSet::Class() { return Type::IfcGeometricSet; }
IfcGeometricSet::IfcGeometricSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricSet)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGrid
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcGrid::UAxes() { RETURN_AS_LIST(IfcGridAxis,7) }
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcGrid::VAxes() { RETURN_AS_LIST(IfcGridAxis,8) }
bool IfcGrid::hasWAxes() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcGrid::WAxes() { RETURN_AS_LIST(IfcGridAxis,9) }
IfcRelContainedInSpatialStructure::list IfcGrid::ContainedInStructure() { RETURN_INVERSE(IfcRelContainedInSpatialStructure) }
bool IfcGrid::is(Type::Enum v) const { return v == Type::IfcGrid || IfcProduct::is(v); }
Type::Enum IfcGrid::type() const { return Type::IfcGrid; }
Type::Enum IfcGrid::Class() { return Type::IfcGrid; }
IfcGrid::IfcGrid(IfcAbstractEntityPtr e) { if (!is(Type::IfcGrid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGridAxis
bool IfcGridAxis::hasAxisTag() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcGridAxis::AxisTag() { return *entity->getArgument(0); }
IfcCurve* IfcGridAxis::AxisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(1)); }
IfcBoolean IfcGridAxis::SameSense() { return *entity->getArgument(2); }
IfcGrid::list IfcGridAxis::PartOfW() { RETURN_INVERSE(IfcGrid) }
IfcGrid::list IfcGridAxis::PartOfV() { RETURN_INVERSE(IfcGrid) }
IfcGrid::list IfcGridAxis::PartOfU() { RETURN_INVERSE(IfcGrid) }
IfcVirtualGridIntersection::list IfcGridAxis::HasIntersections() { RETURN_INVERSE(IfcVirtualGridIntersection) }
bool IfcGridAxis::is(Type::Enum v) const { return v == Type::IfcGridAxis; }
Type::Enum IfcGridAxis::type() const { return Type::IfcGridAxis; }
Type::Enum IfcGridAxis::Class() { return Type::IfcGridAxis; }
IfcGridAxis::IfcGridAxis(IfcAbstractEntityPtr e) { if (!is(Type::IfcGridAxis)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGridPlacement
IfcVirtualGridIntersection* IfcGridPlacement::PlacementLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcVirtualGridIntersection>(*entity->getArgument(0)); }
bool IfcGridPlacement::hasPlacementRefDirection() { return !entity->getArgument(1)->isNull(); }
IfcVirtualGridIntersection* IfcGridPlacement::PlacementRefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcVirtualGridIntersection>(*entity->getArgument(1)); }
bool IfcGridPlacement::is(Type::Enum v) const { return v == Type::IfcGridPlacement || IfcObjectPlacement::is(v); }
Type::Enum IfcGridPlacement::type() const { return Type::IfcGridPlacement; }
Type::Enum IfcGridPlacement::Class() { return Type::IfcGridPlacement; }
IfcGridPlacement::IfcGridPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcGridPlacement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcGroup
IfcRelAssignsToGroup::list IfcGroup::IsGroupedBy() { RETURN_INVERSE(IfcRelAssignsToGroup) }
bool IfcGroup::is(Type::Enum v) const { return v == Type::IfcGroup || IfcObject::is(v); }
Type::Enum IfcGroup::type() const { return Type::IfcGroup; }
Type::Enum IfcGroup::Class() { return Type::IfcGroup; }
IfcGroup::IfcGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcGroup)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcHalfSpaceSolid
IfcSurface* IfcHalfSpaceSolid::BaseSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(0)); }
bool IfcHalfSpaceSolid::AgreementFlag() { return *entity->getArgument(1); }
bool IfcHalfSpaceSolid::is(Type::Enum v) const { return v == Type::IfcHalfSpaceSolid || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcHalfSpaceSolid::type() const { return Type::IfcHalfSpaceSolid; }
Type::Enum IfcHalfSpaceSolid::Class() { return Type::IfcHalfSpaceSolid; }
IfcHalfSpaceSolid::IfcHalfSpaceSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcHalfSpaceSolid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcHeatExchangerType
IfcHeatExchangerTypeEnum::IfcHeatExchangerTypeEnum IfcHeatExchangerType::PredefinedType() { return IfcHeatExchangerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcHeatExchangerType::is(Type::Enum v) const { return v == Type::IfcHeatExchangerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcHeatExchangerType::type() const { return Type::IfcHeatExchangerType; }
Type::Enum IfcHeatExchangerType::Class() { return Type::IfcHeatExchangerType; }
IfcHeatExchangerType::IfcHeatExchangerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcHeatExchangerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcHumidifierType
IfcHumidifierTypeEnum::IfcHumidifierTypeEnum IfcHumidifierType::PredefinedType() { return IfcHumidifierTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcHumidifierType::is(Type::Enum v) const { return v == Type::IfcHumidifierType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcHumidifierType::type() const { return Type::IfcHumidifierType; }
Type::Enum IfcHumidifierType::Class() { return Type::IfcHumidifierType; }
IfcHumidifierType::IfcHumidifierType(IfcAbstractEntityPtr e) { if (!is(Type::IfcHumidifierType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcHygroscopicMaterialProperties
bool IfcHygroscopicMaterialProperties::hasUpperVaporResistanceFactor() { return !entity->getArgument(1)->isNull(); }
IfcPositiveRatioMeasure IfcHygroscopicMaterialProperties::UpperVaporResistanceFactor() { return *entity->getArgument(1); }
bool IfcHygroscopicMaterialProperties::hasLowerVaporResistanceFactor() { return !entity->getArgument(2)->isNull(); }
IfcPositiveRatioMeasure IfcHygroscopicMaterialProperties::LowerVaporResistanceFactor() { return *entity->getArgument(2); }
bool IfcHygroscopicMaterialProperties::hasIsothermalMoistureCapacity() { return !entity->getArgument(3)->isNull(); }
IfcIsothermalMoistureCapacityMeasure IfcHygroscopicMaterialProperties::IsothermalMoistureCapacity() { return *entity->getArgument(3); }
bool IfcHygroscopicMaterialProperties::hasVaporPermeability() { return !entity->getArgument(4)->isNull(); }
IfcVaporPermeabilityMeasure IfcHygroscopicMaterialProperties::VaporPermeability() { return *entity->getArgument(4); }
bool IfcHygroscopicMaterialProperties::hasMoistureDiffusivity() { return !entity->getArgument(5)->isNull(); }
IfcMoistureDiffusivityMeasure IfcHygroscopicMaterialProperties::MoistureDiffusivity() { return *entity->getArgument(5); }
bool IfcHygroscopicMaterialProperties::is(Type::Enum v) const { return v == Type::IfcHygroscopicMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcHygroscopicMaterialProperties::type() const { return Type::IfcHygroscopicMaterialProperties; }
Type::Enum IfcHygroscopicMaterialProperties::Class() { return Type::IfcHygroscopicMaterialProperties; }
IfcHygroscopicMaterialProperties::IfcHygroscopicMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcHygroscopicMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcIShapeProfileDef
IfcPositiveLengthMeasure IfcIShapeProfileDef::OverallWidth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::OverallDepth() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::WebThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::FlangeThickness() { return *entity->getArgument(6); }
bool IfcIShapeProfileDef::hasFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::FilletRadius() { return *entity->getArgument(7); }
bool IfcIShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcIShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcIShapeProfileDef::type() const { return Type::IfcIShapeProfileDef; }
Type::Enum IfcIShapeProfileDef::Class() { return Type::IfcIShapeProfileDef; }
IfcIShapeProfileDef::IfcIShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcIShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcImageTexture
IfcIdentifier IfcImageTexture::UrlReference() { return *entity->getArgument(4); }
bool IfcImageTexture::is(Type::Enum v) const { return v == Type::IfcImageTexture || IfcSurfaceTexture::is(v); }
Type::Enum IfcImageTexture::type() const { return Type::IfcImageTexture; }
Type::Enum IfcImageTexture::Class() { return Type::IfcImageTexture; }
IfcImageTexture::IfcImageTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcImageTexture)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcInventory
IfcInventoryTypeEnum::IfcInventoryTypeEnum IfcInventory::InventoryType() { return IfcInventoryTypeEnum::FromString(*entity->getArgument(5)); }
IfcActorSelect IfcInventory::Jurisdiction() { return *entity->getArgument(6); }
SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > IfcInventory::ResponsiblePersons() { RETURN_AS_LIST(IfcPerson,7) }
IfcCalendarDate* IfcInventory::LastUpdateDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(8)); }
bool IfcInventory::hasCurrentValue() { return !entity->getArgument(9)->isNull(); }
IfcCostValue* IfcInventory::CurrentValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(9)); }
bool IfcInventory::hasOriginalValue() { return !entity->getArgument(10)->isNull(); }
IfcCostValue* IfcInventory::OriginalValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(10)); }
bool IfcInventory::is(Type::Enum v) const { return v == Type::IfcInventory || IfcGroup::is(v); }
Type::Enum IfcInventory::type() const { return Type::IfcInventory; }
Type::Enum IfcInventory::Class() { return Type::IfcInventory; }
IfcInventory::IfcInventory(IfcAbstractEntityPtr e) { if (!is(Type::IfcInventory)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcIrregularTimeSeries
SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeriesValue> > IfcIrregularTimeSeries::Values() { RETURN_AS_LIST(IfcIrregularTimeSeriesValue,8) }
bool IfcIrregularTimeSeries::is(Type::Enum v) const { return v == Type::IfcIrregularTimeSeries || IfcTimeSeries::is(v); }
Type::Enum IfcIrregularTimeSeries::type() const { return Type::IfcIrregularTimeSeries; }
Type::Enum IfcIrregularTimeSeries::Class() { return Type::IfcIrregularTimeSeries; }
IfcIrregularTimeSeries::IfcIrregularTimeSeries(IfcAbstractEntityPtr e) { if (!is(Type::IfcIrregularTimeSeries)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcIrregularTimeSeriesValue
IfcDateTimeSelect IfcIrregularTimeSeriesValue::TimeStamp() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcIrregularTimeSeriesValue::ListValues() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcIrregularTimeSeriesValue::is(Type::Enum v) const { return v == Type::IfcIrregularTimeSeriesValue; }
Type::Enum IfcIrregularTimeSeriesValue::type() const { return Type::IfcIrregularTimeSeriesValue; }
Type::Enum IfcIrregularTimeSeriesValue::Class() { return Type::IfcIrregularTimeSeriesValue; }
IfcIrregularTimeSeriesValue::IfcIrregularTimeSeriesValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcIrregularTimeSeriesValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcJunctionBoxType
IfcJunctionBoxTypeEnum::IfcJunctionBoxTypeEnum IfcJunctionBoxType::PredefinedType() { return IfcJunctionBoxTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcJunctionBoxType::is(Type::Enum v) const { return v == Type::IfcJunctionBoxType || IfcFlowFittingType::is(v); }
Type::Enum IfcJunctionBoxType::type() const { return Type::IfcJunctionBoxType; }
Type::Enum IfcJunctionBoxType::Class() { return Type::IfcJunctionBoxType; }
IfcJunctionBoxType::IfcJunctionBoxType(IfcAbstractEntityPtr e) { if (!is(Type::IfcJunctionBoxType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLShapeProfileDef
IfcPositiveLengthMeasure IfcLShapeProfileDef::Depth() { return *entity->getArgument(3); }
bool IfcLShapeProfileDef::hasWidth() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcLShapeProfileDef::Width() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcLShapeProfileDef::Thickness() { return *entity->getArgument(5); }
bool IfcLShapeProfileDef::hasFilletRadius() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcLShapeProfileDef::FilletRadius() { return *entity->getArgument(6); }
bool IfcLShapeProfileDef::hasEdgeRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcLShapeProfileDef::EdgeRadius() { return *entity->getArgument(7); }
bool IfcLShapeProfileDef::hasLegSlope() { return !entity->getArgument(8)->isNull(); }
IfcPlaneAngleMeasure IfcLShapeProfileDef::LegSlope() { return *entity->getArgument(8); }
bool IfcLShapeProfileDef::hasCentreOfGravityInX() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcLShapeProfileDef::CentreOfGravityInX() { return *entity->getArgument(9); }
bool IfcLShapeProfileDef::hasCentreOfGravityInY() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcLShapeProfileDef::CentreOfGravityInY() { return *entity->getArgument(10); }
bool IfcLShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcLShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcLShapeProfileDef::type() const { return Type::IfcLShapeProfileDef; }
Type::Enum IfcLShapeProfileDef::Class() { return Type::IfcLShapeProfileDef; }
IfcLShapeProfileDef::IfcLShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcLShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLaborResource
bool IfcLaborResource::hasSkillSet() { return !entity->getArgument(9)->isNull(); }
IfcText IfcLaborResource::SkillSet() { return *entity->getArgument(9); }
bool IfcLaborResource::is(Type::Enum v) const { return v == Type::IfcLaborResource || IfcConstructionResource::is(v); }
Type::Enum IfcLaborResource::type() const { return Type::IfcLaborResource; }
Type::Enum IfcLaborResource::Class() { return Type::IfcLaborResource; }
IfcLaborResource::IfcLaborResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcLaborResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLampType
IfcLampTypeEnum::IfcLampTypeEnum IfcLampType::PredefinedType() { return IfcLampTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcLampType::is(Type::Enum v) const { return v == Type::IfcLampType || IfcFlowTerminalType::is(v); }
Type::Enum IfcLampType::type() const { return Type::IfcLampType; }
Type::Enum IfcLampType::Class() { return Type::IfcLampType; }
IfcLampType::IfcLampType(IfcAbstractEntityPtr e) { if (!is(Type::IfcLampType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLibraryInformation
IfcLabel IfcLibraryInformation::Name() { return *entity->getArgument(0); }
bool IfcLibraryInformation::hasVersion() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcLibraryInformation::Version() { return *entity->getArgument(1); }
bool IfcLibraryInformation::hasPublisher() { return !entity->getArgument(2)->isNull(); }
IfcOrganization* IfcLibraryInformation::Publisher() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(2)); }
bool IfcLibraryInformation::hasVersionDate() { return !entity->getArgument(3)->isNull(); }
IfcCalendarDate* IfcLibraryInformation::VersionDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(3)); }
bool IfcLibraryInformation::hasLibraryReference() { return !entity->getArgument(4)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcLibraryReference> > IfcLibraryInformation::LibraryReference() { RETURN_AS_LIST(IfcLibraryReference,4) }
bool IfcLibraryInformation::is(Type::Enum v) const { return v == Type::IfcLibraryInformation; }
Type::Enum IfcLibraryInformation::type() const { return Type::IfcLibraryInformation; }
Type::Enum IfcLibraryInformation::Class() { return Type::IfcLibraryInformation; }
IfcLibraryInformation::IfcLibraryInformation(IfcAbstractEntityPtr e) { if (!is(Type::IfcLibraryInformation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLibraryReference
IfcLibraryInformation::list IfcLibraryReference::ReferenceIntoLibrary() { RETURN_INVERSE(IfcLibraryInformation) }
bool IfcLibraryReference::is(Type::Enum v) const { return v == Type::IfcLibraryReference || IfcExternalReference::is(v); }
Type::Enum IfcLibraryReference::type() const { return Type::IfcLibraryReference; }
Type::Enum IfcLibraryReference::Class() { return Type::IfcLibraryReference; }
IfcLibraryReference::IfcLibraryReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcLibraryReference)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightDistributionData
IfcPlaneAngleMeasure IfcLightDistributionData::MainPlaneAngle() { return *entity->getArgument(0); }
std::vector<IfcPlaneAngleMeasure> /*[1:?]*/ IfcLightDistributionData::SecondaryPlaneAngle() { return *entity->getArgument(1); }
std::vector<IfcLuminousIntensityDistributionMeasure> /*[1:?]*/ IfcLightDistributionData::LuminousIntensity() { return *entity->getArgument(2); }
bool IfcLightDistributionData::is(Type::Enum v) const { return v == Type::IfcLightDistributionData; }
Type::Enum IfcLightDistributionData::type() const { return Type::IfcLightDistributionData; }
Type::Enum IfcLightDistributionData::Class() { return Type::IfcLightDistributionData; }
IfcLightDistributionData::IfcLightDistributionData(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightDistributionData)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightFixtureType
IfcLightFixtureTypeEnum::IfcLightFixtureTypeEnum IfcLightFixtureType::PredefinedType() { return IfcLightFixtureTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcLightFixtureType::is(Type::Enum v) const { return v == Type::IfcLightFixtureType || IfcFlowTerminalType::is(v); }
Type::Enum IfcLightFixtureType::type() const { return Type::IfcLightFixtureType; }
Type::Enum IfcLightFixtureType::Class() { return Type::IfcLightFixtureType; }
IfcLightFixtureType::IfcLightFixtureType(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightFixtureType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightIntensityDistribution
IfcLightDistributionCurveEnum::IfcLightDistributionCurveEnum IfcLightIntensityDistribution::LightDistributionCurve() { return IfcLightDistributionCurveEnum::FromString(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcLightDistributionData> > IfcLightIntensityDistribution::DistributionData() { RETURN_AS_LIST(IfcLightDistributionData,1) }
bool IfcLightIntensityDistribution::is(Type::Enum v) const { return v == Type::IfcLightIntensityDistribution; }
Type::Enum IfcLightIntensityDistribution::type() const { return Type::IfcLightIntensityDistribution; }
Type::Enum IfcLightIntensityDistribution::Class() { return Type::IfcLightIntensityDistribution; }
IfcLightIntensityDistribution::IfcLightIntensityDistribution(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightIntensityDistribution)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightSource
bool IfcLightSource::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcLightSource::Name() { return *entity->getArgument(0); }
IfcColourRgb* IfcLightSource::LightColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(1)); }
bool IfcLightSource::hasAmbientIntensity() { return !entity->getArgument(2)->isNull(); }
IfcNormalisedRatioMeasure IfcLightSource::AmbientIntensity() { return *entity->getArgument(2); }
bool IfcLightSource::hasIntensity() { return !entity->getArgument(3)->isNull(); }
IfcNormalisedRatioMeasure IfcLightSource::Intensity() { return *entity->getArgument(3); }
bool IfcLightSource::is(Type::Enum v) const { return v == Type::IfcLightSource || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcLightSource::type() const { return Type::IfcLightSource; }
Type::Enum IfcLightSource::Class() { return Type::IfcLightSource; }
IfcLightSource::IfcLightSource(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightSourceAmbient
bool IfcLightSourceAmbient::is(Type::Enum v) const { return v == Type::IfcLightSourceAmbient || IfcLightSource::is(v); }
Type::Enum IfcLightSourceAmbient::type() const { return Type::IfcLightSourceAmbient; }
Type::Enum IfcLightSourceAmbient::Class() { return Type::IfcLightSourceAmbient; }
IfcLightSourceAmbient::IfcLightSourceAmbient(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceAmbient)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightSourceDirectional
IfcDirection* IfcLightSourceDirectional::Orientation() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(4)); }
bool IfcLightSourceDirectional::is(Type::Enum v) const { return v == Type::IfcLightSourceDirectional || IfcLightSource::is(v); }
Type::Enum IfcLightSourceDirectional::type() const { return Type::IfcLightSourceDirectional; }
Type::Enum IfcLightSourceDirectional::Class() { return Type::IfcLightSourceDirectional; }
IfcLightSourceDirectional::IfcLightSourceDirectional(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceDirectional)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightSourceGoniometric
IfcAxis2Placement3D* IfcLightSourceGoniometric::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(4)); }
bool IfcLightSourceGoniometric::hasColourAppearance() { return !entity->getArgument(5)->isNull(); }
IfcColourRgb* IfcLightSourceGoniometric::ColourAppearance() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(5)); }
IfcThermodynamicTemperatureMeasure IfcLightSourceGoniometric::ColourTemperature() { return *entity->getArgument(6); }
IfcLuminousFluxMeasure IfcLightSourceGoniometric::LuminousFlux() { return *entity->getArgument(7); }
IfcLightEmissionSourceEnum::IfcLightEmissionSourceEnum IfcLightSourceGoniometric::LightEmissionSource() { return IfcLightEmissionSourceEnum::FromString(*entity->getArgument(8)); }
IfcLightDistributionDataSourceSelect IfcLightSourceGoniometric::LightDistributionDataSource() { return *entity->getArgument(9); }
bool IfcLightSourceGoniometric::is(Type::Enum v) const { return v == Type::IfcLightSourceGoniometric || IfcLightSource::is(v); }
Type::Enum IfcLightSourceGoniometric::type() const { return Type::IfcLightSourceGoniometric; }
Type::Enum IfcLightSourceGoniometric::Class() { return Type::IfcLightSourceGoniometric; }
IfcLightSourceGoniometric::IfcLightSourceGoniometric(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceGoniometric)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightSourcePositional
IfcCartesianPoint* IfcLightSourcePositional::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(4)); }
IfcPositiveLengthMeasure IfcLightSourcePositional::Radius() { return *entity->getArgument(5); }
IfcReal IfcLightSourcePositional::ConstantAttenuation() { return *entity->getArgument(6); }
IfcReal IfcLightSourcePositional::DistanceAttenuation() { return *entity->getArgument(7); }
IfcReal IfcLightSourcePositional::QuadricAttenuation() { return *entity->getArgument(8); }
bool IfcLightSourcePositional::is(Type::Enum v) const { return v == Type::IfcLightSourcePositional || IfcLightSource::is(v); }
Type::Enum IfcLightSourcePositional::type() const { return Type::IfcLightSourcePositional; }
Type::Enum IfcLightSourcePositional::Class() { return Type::IfcLightSourcePositional; }
IfcLightSourcePositional::IfcLightSourcePositional(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourcePositional)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLightSourceSpot
IfcDirection* IfcLightSourceSpot::Orientation() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(9)); }
bool IfcLightSourceSpot::hasConcentrationExponent() { return !entity->getArgument(10)->isNull(); }
IfcReal IfcLightSourceSpot::ConcentrationExponent() { return *entity->getArgument(10); }
IfcPositivePlaneAngleMeasure IfcLightSourceSpot::SpreadAngle() { return *entity->getArgument(11); }
IfcPositivePlaneAngleMeasure IfcLightSourceSpot::BeamWidthAngle() { return *entity->getArgument(12); }
bool IfcLightSourceSpot::is(Type::Enum v) const { return v == Type::IfcLightSourceSpot || IfcLightSourcePositional::is(v); }
Type::Enum IfcLightSourceSpot::type() const { return Type::IfcLightSourceSpot; }
Type::Enum IfcLightSourceSpot::Class() { return Type::IfcLightSourceSpot; }
IfcLightSourceSpot::IfcLightSourceSpot(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceSpot)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLine
IfcCartesianPoint* IfcLine::Pnt() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(0)); }
IfcVector* IfcLine::Dir() { return reinterpret_pointer_cast<IfcBaseClass,IfcVector>(*entity->getArgument(1)); }
bool IfcLine::is(Type::Enum v) const { return v == Type::IfcLine || IfcCurve::is(v); }
Type::Enum IfcLine::type() const { return Type::IfcLine; }
Type::Enum IfcLine::Class() { return Type::IfcLine; }
IfcLine::IfcLine(IfcAbstractEntityPtr e) { if (!is(Type::IfcLine)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLinearDimension
bool IfcLinearDimension::is(Type::Enum v) const { return v == Type::IfcLinearDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcLinearDimension::type() const { return Type::IfcLinearDimension; }
Type::Enum IfcLinearDimension::Class() { return Type::IfcLinearDimension; }
IfcLinearDimension::IfcLinearDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcLinearDimension)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLocalPlacement
bool IfcLocalPlacement::hasPlacementRelTo() { return !entity->getArgument(0)->isNull(); }
IfcObjectPlacement* IfcLocalPlacement::PlacementRelTo() { return reinterpret_pointer_cast<IfcBaseClass,IfcObjectPlacement>(*entity->getArgument(0)); }
IfcAxis2Placement IfcLocalPlacement::RelativePlacement() { return *entity->getArgument(1); }
bool IfcLocalPlacement::is(Type::Enum v) const { return v == Type::IfcLocalPlacement || IfcObjectPlacement::is(v); }
Type::Enum IfcLocalPlacement::type() const { return Type::IfcLocalPlacement; }
Type::Enum IfcLocalPlacement::Class() { return Type::IfcLocalPlacement; }
IfcLocalPlacement::IfcLocalPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcLocalPlacement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLocalTime
IfcHourInDay IfcLocalTime::HourComponent() { return *entity->getArgument(0); }
bool IfcLocalTime::hasMinuteComponent() { return !entity->getArgument(1)->isNull(); }
IfcMinuteInHour IfcLocalTime::MinuteComponent() { return *entity->getArgument(1); }
bool IfcLocalTime::hasSecondComponent() { return !entity->getArgument(2)->isNull(); }
IfcSecondInMinute IfcLocalTime::SecondComponent() { return *entity->getArgument(2); }
bool IfcLocalTime::hasZone() { return !entity->getArgument(3)->isNull(); }
IfcCoordinatedUniversalTimeOffset* IfcLocalTime::Zone() { return reinterpret_pointer_cast<IfcBaseClass,IfcCoordinatedUniversalTimeOffset>(*entity->getArgument(3)); }
bool IfcLocalTime::hasDaylightSavingOffset() { return !entity->getArgument(4)->isNull(); }
IfcDaylightSavingHour IfcLocalTime::DaylightSavingOffset() { return *entity->getArgument(4); }
bool IfcLocalTime::is(Type::Enum v) const { return v == Type::IfcLocalTime; }
Type::Enum IfcLocalTime::type() const { return Type::IfcLocalTime; }
Type::Enum IfcLocalTime::Class() { return Type::IfcLocalTime; }
IfcLocalTime::IfcLocalTime(IfcAbstractEntityPtr e) { if (!is(Type::IfcLocalTime)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcLoop
bool IfcLoop::is(Type::Enum v) const { return v == Type::IfcLoop || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcLoop::type() const { return Type::IfcLoop; }
Type::Enum IfcLoop::Class() { return Type::IfcLoop; }
IfcLoop::IfcLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcLoop)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcManifoldSolidBrep
IfcClosedShell* IfcManifoldSolidBrep::Outer() { return reinterpret_pointer_cast<IfcBaseClass,IfcClosedShell>(*entity->getArgument(0)); }
bool IfcManifoldSolidBrep::is(Type::Enum v) const { return v == Type::IfcManifoldSolidBrep || IfcSolidModel::is(v); }
Type::Enum IfcManifoldSolidBrep::type() const { return Type::IfcManifoldSolidBrep; }
Type::Enum IfcManifoldSolidBrep::Class() { return Type::IfcManifoldSolidBrep; }
IfcManifoldSolidBrep::IfcManifoldSolidBrep(IfcAbstractEntityPtr e) { if (!is(Type::IfcManifoldSolidBrep)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMappedItem
IfcRepresentationMap* IfcMappedItem::MappingSource() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentationMap>(*entity->getArgument(0)); }
IfcCartesianTransformationOperator* IfcMappedItem::MappingTarget() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator>(*entity->getArgument(1)); }
bool IfcMappedItem::is(Type::Enum v) const { return v == Type::IfcMappedItem || IfcRepresentationItem::is(v); }
Type::Enum IfcMappedItem::type() const { return Type::IfcMappedItem; }
Type::Enum IfcMappedItem::Class() { return Type::IfcMappedItem; }
IfcMappedItem::IfcMappedItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcMappedItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterial
IfcLabel IfcMaterial::Name() { return *entity->getArgument(0); }
IfcMaterialDefinitionRepresentation::list IfcMaterial::HasRepresentation() { RETURN_INVERSE(IfcMaterialDefinitionRepresentation) }
IfcMaterialClassificationRelationship::list IfcMaterial::ClassifiedAs() { RETURN_INVERSE(IfcMaterialClassificationRelationship) }
bool IfcMaterial::is(Type::Enum v) const { return v == Type::IfcMaterial; }
Type::Enum IfcMaterial::type() const { return Type::IfcMaterial; }
Type::Enum IfcMaterial::Class() { return Type::IfcMaterial; }
IfcMaterial::IfcMaterial(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterial)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterialClassificationRelationship
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcMaterialClassificationRelationship::MaterialClassifications() { RETURN_AS_LIST(IfcAbstractSelect,0) }
IfcMaterial* IfcMaterialClassificationRelationship::ClassifiedMaterial() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(1)); }
bool IfcMaterialClassificationRelationship::is(Type::Enum v) const { return v == Type::IfcMaterialClassificationRelationship; }
Type::Enum IfcMaterialClassificationRelationship::type() const { return Type::IfcMaterialClassificationRelationship; }
Type::Enum IfcMaterialClassificationRelationship::Class() { return Type::IfcMaterialClassificationRelationship; }
IfcMaterialClassificationRelationship::IfcMaterialClassificationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialClassificationRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterialDefinitionRepresentation
IfcMaterial* IfcMaterialDefinitionRepresentation::RepresentedMaterial() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(3)); }
bool IfcMaterialDefinitionRepresentation::is(Type::Enum v) const { return v == Type::IfcMaterialDefinitionRepresentation || IfcProductRepresentation::is(v); }
Type::Enum IfcMaterialDefinitionRepresentation::type() const { return Type::IfcMaterialDefinitionRepresentation; }
Type::Enum IfcMaterialDefinitionRepresentation::Class() { return Type::IfcMaterialDefinitionRepresentation; }
IfcMaterialDefinitionRepresentation::IfcMaterialDefinitionRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialDefinitionRepresentation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterialLayer
bool IfcMaterialLayer::hasMaterial() { return !entity->getArgument(0)->isNull(); }
IfcMaterial* IfcMaterialLayer::Material() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(0)); }
IfcPositiveLengthMeasure IfcMaterialLayer::LayerThickness() { return *entity->getArgument(1); }
bool IfcMaterialLayer::hasIsVentilated() { return !entity->getArgument(2)->isNull(); }
IfcLogical IfcMaterialLayer::IsVentilated() { return *entity->getArgument(2); }
IfcMaterialLayerSet::list IfcMaterialLayer::ToMaterialLayerSet() { RETURN_INVERSE(IfcMaterialLayerSet) }
bool IfcMaterialLayer::is(Type::Enum v) const { return v == Type::IfcMaterialLayer; }
Type::Enum IfcMaterialLayer::type() const { return Type::IfcMaterialLayer; }
Type::Enum IfcMaterialLayer::Class() { return Type::IfcMaterialLayer; }
IfcMaterialLayer::IfcMaterialLayer(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialLayer)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterialLayerSet
SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayer> > IfcMaterialLayerSet::MaterialLayers() { RETURN_AS_LIST(IfcMaterialLayer,0) }
bool IfcMaterialLayerSet::hasLayerSetName() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcMaterialLayerSet::LayerSetName() { return *entity->getArgument(1); }
bool IfcMaterialLayerSet::is(Type::Enum v) const { return v == Type::IfcMaterialLayerSet; }
Type::Enum IfcMaterialLayerSet::type() const { return Type::IfcMaterialLayerSet; }
Type::Enum IfcMaterialLayerSet::Class() { return Type::IfcMaterialLayerSet; }
IfcMaterialLayerSet::IfcMaterialLayerSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialLayerSet)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterialLayerSetUsage
IfcMaterialLayerSet* IfcMaterialLayerSetUsage::ForLayerSet() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterialLayerSet>(*entity->getArgument(0)); }
IfcLayerSetDirectionEnum::IfcLayerSetDirectionEnum IfcMaterialLayerSetUsage::LayerSetDirection() { return IfcLayerSetDirectionEnum::FromString(*entity->getArgument(1)); }
IfcDirectionSenseEnum::IfcDirectionSenseEnum IfcMaterialLayerSetUsage::DirectionSense() { return IfcDirectionSenseEnum::FromString(*entity->getArgument(2)); }
IfcLengthMeasure IfcMaterialLayerSetUsage::OffsetFromReferenceLine() { return *entity->getArgument(3); }
bool IfcMaterialLayerSetUsage::is(Type::Enum v) const { return v == Type::IfcMaterialLayerSetUsage; }
Type::Enum IfcMaterialLayerSetUsage::type() const { return Type::IfcMaterialLayerSetUsage; }
Type::Enum IfcMaterialLayerSetUsage::Class() { return Type::IfcMaterialLayerSetUsage; }
IfcMaterialLayerSetUsage::IfcMaterialLayerSetUsage(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialLayerSetUsage)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterialList
SHARED_PTR< IfcTemplatedEntityList<IfcMaterial> > IfcMaterialList::Materials() { RETURN_AS_LIST(IfcMaterial,0) }
bool IfcMaterialList::is(Type::Enum v) const { return v == Type::IfcMaterialList; }
Type::Enum IfcMaterialList::type() const { return Type::IfcMaterialList; }
Type::Enum IfcMaterialList::Class() { return Type::IfcMaterialList; }
IfcMaterialList::IfcMaterialList(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialList)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMaterialProperties
IfcMaterial* IfcMaterialProperties::Material() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(0)); }
bool IfcMaterialProperties::is(Type::Enum v) const { return v == Type::IfcMaterialProperties; }
Type::Enum IfcMaterialProperties::type() const { return Type::IfcMaterialProperties; }
Type::Enum IfcMaterialProperties::Class() { return Type::IfcMaterialProperties; }
IfcMaterialProperties::IfcMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMeasureWithUnit
IfcValue IfcMeasureWithUnit::ValueComponent() { return *entity->getArgument(0); }
IfcUnit IfcMeasureWithUnit::UnitComponent() { return *entity->getArgument(1); }
bool IfcMeasureWithUnit::is(Type::Enum v) const { return v == Type::IfcMeasureWithUnit; }
Type::Enum IfcMeasureWithUnit::type() const { return Type::IfcMeasureWithUnit; }
Type::Enum IfcMeasureWithUnit::Class() { return Type::IfcMeasureWithUnit; }
IfcMeasureWithUnit::IfcMeasureWithUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcMeasureWithUnit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMechanicalConcreteMaterialProperties
bool IfcMechanicalConcreteMaterialProperties::hasCompressiveStrength() { return !entity->getArgument(6)->isNull(); }
IfcPressureMeasure IfcMechanicalConcreteMaterialProperties::CompressiveStrength() { return *entity->getArgument(6); }
bool IfcMechanicalConcreteMaterialProperties::hasMaxAggregateSize() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcMechanicalConcreteMaterialProperties::MaxAggregateSize() { return *entity->getArgument(7); }
bool IfcMechanicalConcreteMaterialProperties::hasAdmixturesDescription() { return !entity->getArgument(8)->isNull(); }
IfcText IfcMechanicalConcreteMaterialProperties::AdmixturesDescription() { return *entity->getArgument(8); }
bool IfcMechanicalConcreteMaterialProperties::hasWorkability() { return !entity->getArgument(9)->isNull(); }
IfcText IfcMechanicalConcreteMaterialProperties::Workability() { return *entity->getArgument(9); }
bool IfcMechanicalConcreteMaterialProperties::hasProtectivePoreRatio() { return !entity->getArgument(10)->isNull(); }
IfcNormalisedRatioMeasure IfcMechanicalConcreteMaterialProperties::ProtectivePoreRatio() { return *entity->getArgument(10); }
bool IfcMechanicalConcreteMaterialProperties::hasWaterImpermeability() { return !entity->getArgument(11)->isNull(); }
IfcText IfcMechanicalConcreteMaterialProperties::WaterImpermeability() { return *entity->getArgument(11); }
bool IfcMechanicalConcreteMaterialProperties::is(Type::Enum v) const { return v == Type::IfcMechanicalConcreteMaterialProperties || IfcMechanicalMaterialProperties::is(v); }
Type::Enum IfcMechanicalConcreteMaterialProperties::type() const { return Type::IfcMechanicalConcreteMaterialProperties; }
Type::Enum IfcMechanicalConcreteMaterialProperties::Class() { return Type::IfcMechanicalConcreteMaterialProperties; }
IfcMechanicalConcreteMaterialProperties::IfcMechanicalConcreteMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalConcreteMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMechanicalFastener
bool IfcMechanicalFastener::hasNominalDiameter() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcMechanicalFastener::NominalDiameter() { return *entity->getArgument(8); }
bool IfcMechanicalFastener::hasNominalLength() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcMechanicalFastener::NominalLength() { return *entity->getArgument(9); }
bool IfcMechanicalFastener::is(Type::Enum v) const { return v == Type::IfcMechanicalFastener || IfcFastener::is(v); }
Type::Enum IfcMechanicalFastener::type() const { return Type::IfcMechanicalFastener; }
Type::Enum IfcMechanicalFastener::Class() { return Type::IfcMechanicalFastener; }
IfcMechanicalFastener::IfcMechanicalFastener(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalFastener)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMechanicalFastenerType
bool IfcMechanicalFastenerType::is(Type::Enum v) const { return v == Type::IfcMechanicalFastenerType || IfcFastenerType::is(v); }
Type::Enum IfcMechanicalFastenerType::type() const { return Type::IfcMechanicalFastenerType; }
Type::Enum IfcMechanicalFastenerType::Class() { return Type::IfcMechanicalFastenerType; }
IfcMechanicalFastenerType::IfcMechanicalFastenerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalFastenerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMechanicalMaterialProperties
bool IfcMechanicalMaterialProperties::hasDynamicViscosity() { return !entity->getArgument(1)->isNull(); }
IfcDynamicViscosityMeasure IfcMechanicalMaterialProperties::DynamicViscosity() { return *entity->getArgument(1); }
bool IfcMechanicalMaterialProperties::hasYoungModulus() { return !entity->getArgument(2)->isNull(); }
IfcModulusOfElasticityMeasure IfcMechanicalMaterialProperties::YoungModulus() { return *entity->getArgument(2); }
bool IfcMechanicalMaterialProperties::hasShearModulus() { return !entity->getArgument(3)->isNull(); }
IfcModulusOfElasticityMeasure IfcMechanicalMaterialProperties::ShearModulus() { return *entity->getArgument(3); }
bool IfcMechanicalMaterialProperties::hasPoissonRatio() { return !entity->getArgument(4)->isNull(); }
IfcPositiveRatioMeasure IfcMechanicalMaterialProperties::PoissonRatio() { return *entity->getArgument(4); }
bool IfcMechanicalMaterialProperties::hasThermalExpansionCoefficient() { return !entity->getArgument(5)->isNull(); }
IfcThermalExpansionCoefficientMeasure IfcMechanicalMaterialProperties::ThermalExpansionCoefficient() { return *entity->getArgument(5); }
bool IfcMechanicalMaterialProperties::is(Type::Enum v) const { return v == Type::IfcMechanicalMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcMechanicalMaterialProperties::type() const { return Type::IfcMechanicalMaterialProperties; }
Type::Enum IfcMechanicalMaterialProperties::Class() { return Type::IfcMechanicalMaterialProperties; }
IfcMechanicalMaterialProperties::IfcMechanicalMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMechanicalSteelMaterialProperties
bool IfcMechanicalSteelMaterialProperties::hasYieldStress() { return !entity->getArgument(6)->isNull(); }
IfcPressureMeasure IfcMechanicalSteelMaterialProperties::YieldStress() { return *entity->getArgument(6); }
bool IfcMechanicalSteelMaterialProperties::hasUltimateStress() { return !entity->getArgument(7)->isNull(); }
IfcPressureMeasure IfcMechanicalSteelMaterialProperties::UltimateStress() { return *entity->getArgument(7); }
bool IfcMechanicalSteelMaterialProperties::hasUltimateStrain() { return !entity->getArgument(8)->isNull(); }
IfcPositiveRatioMeasure IfcMechanicalSteelMaterialProperties::UltimateStrain() { return *entity->getArgument(8); }
bool IfcMechanicalSteelMaterialProperties::hasHardeningModule() { return !entity->getArgument(9)->isNull(); }
IfcModulusOfElasticityMeasure IfcMechanicalSteelMaterialProperties::HardeningModule() { return *entity->getArgument(9); }
bool IfcMechanicalSteelMaterialProperties::hasProportionalStress() { return !entity->getArgument(10)->isNull(); }
IfcPressureMeasure IfcMechanicalSteelMaterialProperties::ProportionalStress() { return *entity->getArgument(10); }
bool IfcMechanicalSteelMaterialProperties::hasPlasticStrain() { return !entity->getArgument(11)->isNull(); }
IfcPositiveRatioMeasure IfcMechanicalSteelMaterialProperties::PlasticStrain() { return *entity->getArgument(11); }
bool IfcMechanicalSteelMaterialProperties::hasRelaxations() { return !entity->getArgument(12)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcRelaxation> > IfcMechanicalSteelMaterialProperties::Relaxations() { RETURN_AS_LIST(IfcRelaxation,12) }
bool IfcMechanicalSteelMaterialProperties::is(Type::Enum v) const { return v == Type::IfcMechanicalSteelMaterialProperties || IfcMechanicalMaterialProperties::is(v); }
Type::Enum IfcMechanicalSteelMaterialProperties::type() const { return Type::IfcMechanicalSteelMaterialProperties; }
Type::Enum IfcMechanicalSteelMaterialProperties::Class() { return Type::IfcMechanicalSteelMaterialProperties; }
IfcMechanicalSteelMaterialProperties::IfcMechanicalSteelMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalSteelMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMember
bool IfcMember::is(Type::Enum v) const { return v == Type::IfcMember || IfcBuildingElement::is(v); }
Type::Enum IfcMember::type() const { return Type::IfcMember; }
Type::Enum IfcMember::Class() { return Type::IfcMember; }
IfcMember::IfcMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcMember)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMemberType
IfcMemberTypeEnum::IfcMemberTypeEnum IfcMemberType::PredefinedType() { return IfcMemberTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcMemberType::is(Type::Enum v) const { return v == Type::IfcMemberType || IfcBuildingElementType::is(v); }
Type::Enum IfcMemberType::type() const { return Type::IfcMemberType; }
Type::Enum IfcMemberType::Class() { return Type::IfcMemberType; }
IfcMemberType::IfcMemberType(IfcAbstractEntityPtr e) { if (!is(Type::IfcMemberType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMetric
IfcBenchmarkEnum::IfcBenchmarkEnum IfcMetric::Benchmark() { return IfcBenchmarkEnum::FromString(*entity->getArgument(7)); }
bool IfcMetric::hasValueSource() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcMetric::ValueSource() { return *entity->getArgument(8); }
IfcMetricValueSelect IfcMetric::DataValue() { return *entity->getArgument(9); }
bool IfcMetric::is(Type::Enum v) const { return v == Type::IfcMetric || IfcConstraint::is(v); }
Type::Enum IfcMetric::type() const { return Type::IfcMetric; }
Type::Enum IfcMetric::Class() { return Type::IfcMetric; }
IfcMetric::IfcMetric(IfcAbstractEntityPtr e) { if (!is(Type::IfcMetric)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMonetaryUnit
IfcCurrencyEnum::IfcCurrencyEnum IfcMonetaryUnit::Currency() { return IfcCurrencyEnum::FromString(*entity->getArgument(0)); }
bool IfcMonetaryUnit::is(Type::Enum v) const { return v == Type::IfcMonetaryUnit; }
Type::Enum IfcMonetaryUnit::type() const { return Type::IfcMonetaryUnit; }
Type::Enum IfcMonetaryUnit::Class() { return Type::IfcMonetaryUnit; }
IfcMonetaryUnit::IfcMonetaryUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcMonetaryUnit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMotorConnectionType
IfcMotorConnectionTypeEnum::IfcMotorConnectionTypeEnum IfcMotorConnectionType::PredefinedType() { return IfcMotorConnectionTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcMotorConnectionType::is(Type::Enum v) const { return v == Type::IfcMotorConnectionType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcMotorConnectionType::type() const { return Type::IfcMotorConnectionType; }
Type::Enum IfcMotorConnectionType::Class() { return Type::IfcMotorConnectionType; }
IfcMotorConnectionType::IfcMotorConnectionType(IfcAbstractEntityPtr e) { if (!is(Type::IfcMotorConnectionType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcMove
IfcSpatialStructureElement* IfcMove::MoveFrom() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(10)); }
IfcSpatialStructureElement* IfcMove::MoveTo() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(11)); }
bool IfcMove::hasPunchList() { return !entity->getArgument(12)->isNull(); }
std::vector<IfcText> /*[1:?]*/ IfcMove::PunchList() { return *entity->getArgument(12); }
bool IfcMove::is(Type::Enum v) const { return v == Type::IfcMove || IfcTask::is(v); }
Type::Enum IfcMove::type() const { return Type::IfcMove; }
Type::Enum IfcMove::Class() { return Type::IfcMove; }
IfcMove::IfcMove(IfcAbstractEntityPtr e) { if (!is(Type::IfcMove)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcNamedUnit
IfcDimensionalExponents* IfcNamedUnit::Dimensions() { return reinterpret_pointer_cast<IfcBaseClass,IfcDimensionalExponents>(*entity->getArgument(0)); }
IfcUnitEnum::IfcUnitEnum IfcNamedUnit::UnitType() { return IfcUnitEnum::FromString(*entity->getArgument(1)); }
bool IfcNamedUnit::is(Type::Enum v) const { return v == Type::IfcNamedUnit; }
Type::Enum IfcNamedUnit::type() const { return Type::IfcNamedUnit; }
Type::Enum IfcNamedUnit::Class() { return Type::IfcNamedUnit; }
IfcNamedUnit::IfcNamedUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcNamedUnit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcObject
bool IfcObject::hasObjectType() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcObject::ObjectType() { return *entity->getArgument(4); }
IfcRelDefines::list IfcObject::IsDefinedBy() { RETURN_INVERSE(IfcRelDefines) }
bool IfcObject::is(Type::Enum v) const { return v == Type::IfcObject || IfcObjectDefinition::is(v); }
Type::Enum IfcObject::type() const { return Type::IfcObject; }
Type::Enum IfcObject::Class() { return Type::IfcObject; }
IfcObject::IfcObject(IfcAbstractEntityPtr e) { if (!is(Type::IfcObject)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcObjectDefinition
IfcRelAssigns::list IfcObjectDefinition::HasAssignments() { RETURN_INVERSE(IfcRelAssigns) }
IfcRelDecomposes::list IfcObjectDefinition::IsDecomposedBy() { RETURN_INVERSE(IfcRelDecomposes) }
IfcRelDecomposes::list IfcObjectDefinition::Decomposes() { RETURN_INVERSE(IfcRelDecomposes) }
IfcRelAssociates::list IfcObjectDefinition::HasAssociations() { RETURN_INVERSE(IfcRelAssociates) }
bool IfcObjectDefinition::is(Type::Enum v) const { return v == Type::IfcObjectDefinition || IfcRoot::is(v); }
Type::Enum IfcObjectDefinition::type() const { return Type::IfcObjectDefinition; }
Type::Enum IfcObjectDefinition::Class() { return Type::IfcObjectDefinition; }
IfcObjectDefinition::IfcObjectDefinition(IfcAbstractEntityPtr e) { if (!is(Type::IfcObjectDefinition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcObjectPlacement
IfcProduct::list IfcObjectPlacement::PlacesObject() { RETURN_INVERSE(IfcProduct) }
IfcLocalPlacement::list IfcObjectPlacement::ReferencedByPlacements() { RETURN_INVERSE(IfcLocalPlacement) }
bool IfcObjectPlacement::is(Type::Enum v) const { return v == Type::IfcObjectPlacement; }
Type::Enum IfcObjectPlacement::type() const { return Type::IfcObjectPlacement; }
Type::Enum IfcObjectPlacement::Class() { return Type::IfcObjectPlacement; }
IfcObjectPlacement::IfcObjectPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcObjectPlacement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcObjective
bool IfcObjective::hasBenchmarkValues() { return !entity->getArgument(7)->isNull(); }
IfcMetric* IfcObjective::BenchmarkValues() { return reinterpret_pointer_cast<IfcBaseClass,IfcMetric>(*entity->getArgument(7)); }
bool IfcObjective::hasResultValues() { return !entity->getArgument(8)->isNull(); }
IfcMetric* IfcObjective::ResultValues() { return reinterpret_pointer_cast<IfcBaseClass,IfcMetric>(*entity->getArgument(8)); }
IfcObjectiveEnum::IfcObjectiveEnum IfcObjective::ObjectiveQualifier() { return IfcObjectiveEnum::FromString(*entity->getArgument(9)); }
bool IfcObjective::hasUserDefinedQualifier() { return !entity->getArgument(10)->isNull(); }
IfcLabel IfcObjective::UserDefinedQualifier() { return *entity->getArgument(10); }
bool IfcObjective::is(Type::Enum v) const { return v == Type::IfcObjective || IfcConstraint::is(v); }
Type::Enum IfcObjective::type() const { return Type::IfcObjective; }
Type::Enum IfcObjective::Class() { return Type::IfcObjective; }
IfcObjective::IfcObjective(IfcAbstractEntityPtr e) { if (!is(Type::IfcObjective)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOccupant
IfcOccupantTypeEnum::IfcOccupantTypeEnum IfcOccupant::PredefinedType() { return IfcOccupantTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcOccupant::is(Type::Enum v) const { return v == Type::IfcOccupant || IfcActor::is(v); }
Type::Enum IfcOccupant::type() const { return Type::IfcOccupant; }
Type::Enum IfcOccupant::Class() { return Type::IfcOccupant; }
IfcOccupant::IfcOccupant(IfcAbstractEntityPtr e) { if (!is(Type::IfcOccupant)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOffsetCurve2D
IfcCurve* IfcOffsetCurve2D::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcLengthMeasure IfcOffsetCurve2D::Distance() { return *entity->getArgument(1); }
bool IfcOffsetCurve2D::SelfIntersect() { return *entity->getArgument(2); }
bool IfcOffsetCurve2D::is(Type::Enum v) const { return v == Type::IfcOffsetCurve2D || IfcCurve::is(v); }
Type::Enum IfcOffsetCurve2D::type() const { return Type::IfcOffsetCurve2D; }
Type::Enum IfcOffsetCurve2D::Class() { return Type::IfcOffsetCurve2D; }
IfcOffsetCurve2D::IfcOffsetCurve2D(IfcAbstractEntityPtr e) { if (!is(Type::IfcOffsetCurve2D)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOffsetCurve3D
IfcCurve* IfcOffsetCurve3D::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcLengthMeasure IfcOffsetCurve3D::Distance() { return *entity->getArgument(1); }
bool IfcOffsetCurve3D::SelfIntersect() { return *entity->getArgument(2); }
IfcDirection* IfcOffsetCurve3D::RefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(3)); }
bool IfcOffsetCurve3D::is(Type::Enum v) const { return v == Type::IfcOffsetCurve3D || IfcCurve::is(v); }
Type::Enum IfcOffsetCurve3D::type() const { return Type::IfcOffsetCurve3D; }
Type::Enum IfcOffsetCurve3D::Class() { return Type::IfcOffsetCurve3D; }
IfcOffsetCurve3D::IfcOffsetCurve3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcOffsetCurve3D)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOneDirectionRepeatFactor
IfcVector* IfcOneDirectionRepeatFactor::RepeatFactor() { return reinterpret_pointer_cast<IfcBaseClass,IfcVector>(*entity->getArgument(0)); }
bool IfcOneDirectionRepeatFactor::is(Type::Enum v) const { return v == Type::IfcOneDirectionRepeatFactor || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcOneDirectionRepeatFactor::type() const { return Type::IfcOneDirectionRepeatFactor; }
Type::Enum IfcOneDirectionRepeatFactor::Class() { return Type::IfcOneDirectionRepeatFactor; }
IfcOneDirectionRepeatFactor::IfcOneDirectionRepeatFactor(IfcAbstractEntityPtr e) { if (!is(Type::IfcOneDirectionRepeatFactor)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOpenShell
bool IfcOpenShell::is(Type::Enum v) const { return v == Type::IfcOpenShell || IfcConnectedFaceSet::is(v); }
Type::Enum IfcOpenShell::type() const { return Type::IfcOpenShell; }
Type::Enum IfcOpenShell::Class() { return Type::IfcOpenShell; }
IfcOpenShell::IfcOpenShell(IfcAbstractEntityPtr e) { if (!is(Type::IfcOpenShell)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOpeningElement
IfcRelFillsElement::list IfcOpeningElement::HasFillings() { RETURN_INVERSE(IfcRelFillsElement) }
bool IfcOpeningElement::is(Type::Enum v) const { return v == Type::IfcOpeningElement || IfcFeatureElementSubtraction::is(v); }
Type::Enum IfcOpeningElement::type() const { return Type::IfcOpeningElement; }
Type::Enum IfcOpeningElement::Class() { return Type::IfcOpeningElement; }
IfcOpeningElement::IfcOpeningElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcOpeningElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOpticalMaterialProperties
bool IfcOpticalMaterialProperties::hasVisibleTransmittance() { return !entity->getArgument(1)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::VisibleTransmittance() { return *entity->getArgument(1); }
bool IfcOpticalMaterialProperties::hasSolarTransmittance() { return !entity->getArgument(2)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::SolarTransmittance() { return *entity->getArgument(2); }
bool IfcOpticalMaterialProperties::hasThermalIrTransmittance() { return !entity->getArgument(3)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::ThermalIrTransmittance() { return *entity->getArgument(3); }
bool IfcOpticalMaterialProperties::hasThermalIrEmissivityBack() { return !entity->getArgument(4)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::ThermalIrEmissivityBack() { return *entity->getArgument(4); }
bool IfcOpticalMaterialProperties::hasThermalIrEmissivityFront() { return !entity->getArgument(5)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::ThermalIrEmissivityFront() { return *entity->getArgument(5); }
bool IfcOpticalMaterialProperties::hasVisibleReflectanceBack() { return !entity->getArgument(6)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::VisibleReflectanceBack() { return *entity->getArgument(6); }
bool IfcOpticalMaterialProperties::hasVisibleReflectanceFront() { return !entity->getArgument(7)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::VisibleReflectanceFront() { return *entity->getArgument(7); }
bool IfcOpticalMaterialProperties::hasSolarReflectanceFront() { return !entity->getArgument(8)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::SolarReflectanceFront() { return *entity->getArgument(8); }
bool IfcOpticalMaterialProperties::hasSolarReflectanceBack() { return !entity->getArgument(9)->isNull(); }
IfcPositiveRatioMeasure IfcOpticalMaterialProperties::SolarReflectanceBack() { return *entity->getArgument(9); }
bool IfcOpticalMaterialProperties::is(Type::Enum v) const { return v == Type::IfcOpticalMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcOpticalMaterialProperties::type() const { return Type::IfcOpticalMaterialProperties; }
Type::Enum IfcOpticalMaterialProperties::Class() { return Type::IfcOpticalMaterialProperties; }
IfcOpticalMaterialProperties::IfcOpticalMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcOpticalMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOrderAction
IfcIdentifier IfcOrderAction::ActionID() { return *entity->getArgument(10); }
bool IfcOrderAction::is(Type::Enum v) const { return v == Type::IfcOrderAction || IfcTask::is(v); }
Type::Enum IfcOrderAction::type() const { return Type::IfcOrderAction; }
Type::Enum IfcOrderAction::Class() { return Type::IfcOrderAction; }
IfcOrderAction::IfcOrderAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrderAction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOrganization
bool IfcOrganization::hasId() { return !entity->getArgument(0)->isNull(); }
IfcIdentifier IfcOrganization::Id() { return *entity->getArgument(0); }
IfcLabel IfcOrganization::Name() { return *entity->getArgument(1); }
bool IfcOrganization::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcOrganization::Description() { return *entity->getArgument(2); }
bool IfcOrganization::hasRoles() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > IfcOrganization::Roles() { RETURN_AS_LIST(IfcActorRole,3) }
bool IfcOrganization::hasAddresses() { return !entity->getArgument(4)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAddress> > IfcOrganization::Addresses() { RETURN_AS_LIST(IfcAddress,4) }
IfcOrganizationRelationship::list IfcOrganization::IsRelatedBy() { RETURN_INVERSE(IfcOrganizationRelationship) }
IfcOrganizationRelationship::list IfcOrganization::Relates() { RETURN_INVERSE(IfcOrganizationRelationship) }
IfcPersonAndOrganization::list IfcOrganization::Engages() { RETURN_INVERSE(IfcPersonAndOrganization) }
bool IfcOrganization::is(Type::Enum v) const { return v == Type::IfcOrganization; }
Type::Enum IfcOrganization::type() const { return Type::IfcOrganization; }
Type::Enum IfcOrganization::Class() { return Type::IfcOrganization; }
IfcOrganization::IfcOrganization(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrganization)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOrganizationRelationship
IfcLabel IfcOrganizationRelationship::Name() { return *entity->getArgument(0); }
bool IfcOrganizationRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcOrganizationRelationship::Description() { return *entity->getArgument(1); }
IfcOrganization* IfcOrganizationRelationship::RelatingOrganization() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(2)); }
SHARED_PTR< IfcTemplatedEntityList<IfcOrganization> > IfcOrganizationRelationship::RelatedOrganizations() { RETURN_AS_LIST(IfcOrganization,3) }
bool IfcOrganizationRelationship::is(Type::Enum v) const { return v == Type::IfcOrganizationRelationship; }
Type::Enum IfcOrganizationRelationship::type() const { return Type::IfcOrganizationRelationship; }
Type::Enum IfcOrganizationRelationship::Class() { return Type::IfcOrganizationRelationship; }
IfcOrganizationRelationship::IfcOrganizationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrganizationRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOrientedEdge
IfcEdge* IfcOrientedEdge::EdgeElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcEdge>(*entity->getArgument(2)); }
bool IfcOrientedEdge::Orientation() { return *entity->getArgument(3); }
bool IfcOrientedEdge::is(Type::Enum v) const { return v == Type::IfcOrientedEdge || IfcEdge::is(v); }
Type::Enum IfcOrientedEdge::type() const { return Type::IfcOrientedEdge; }
Type::Enum IfcOrientedEdge::Class() { return Type::IfcOrientedEdge; }
IfcOrientedEdge::IfcOrientedEdge(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrientedEdge)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOutletType
IfcOutletTypeEnum::IfcOutletTypeEnum IfcOutletType::PredefinedType() { return IfcOutletTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcOutletType::is(Type::Enum v) const { return v == Type::IfcOutletType || IfcFlowTerminalType::is(v); }
Type::Enum IfcOutletType::type() const { return Type::IfcOutletType; }
Type::Enum IfcOutletType::Class() { return Type::IfcOutletType; }
IfcOutletType::IfcOutletType(IfcAbstractEntityPtr e) { if (!is(Type::IfcOutletType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcOwnerHistory
IfcPersonAndOrganization* IfcOwnerHistory::OwningUser() { return reinterpret_pointer_cast<IfcBaseClass,IfcPersonAndOrganization>(*entity->getArgument(0)); }
IfcApplication* IfcOwnerHistory::OwningApplication() { return reinterpret_pointer_cast<IfcBaseClass,IfcApplication>(*entity->getArgument(1)); }
bool IfcOwnerHistory::hasState() { return !entity->getArgument(2)->isNull(); }
IfcStateEnum::IfcStateEnum IfcOwnerHistory::State() { return IfcStateEnum::FromString(*entity->getArgument(2)); }
IfcChangeActionEnum::IfcChangeActionEnum IfcOwnerHistory::ChangeAction() { return IfcChangeActionEnum::FromString(*entity->getArgument(3)); }
bool IfcOwnerHistory::hasLastModifiedDate() { return !entity->getArgument(4)->isNull(); }
IfcTimeStamp IfcOwnerHistory::LastModifiedDate() { return *entity->getArgument(4); }
bool IfcOwnerHistory::hasLastModifyingUser() { return !entity->getArgument(5)->isNull(); }
IfcPersonAndOrganization* IfcOwnerHistory::LastModifyingUser() { return reinterpret_pointer_cast<IfcBaseClass,IfcPersonAndOrganization>(*entity->getArgument(5)); }
bool IfcOwnerHistory::hasLastModifyingApplication() { return !entity->getArgument(6)->isNull(); }
IfcApplication* IfcOwnerHistory::LastModifyingApplication() { return reinterpret_pointer_cast<IfcBaseClass,IfcApplication>(*entity->getArgument(6)); }
IfcTimeStamp IfcOwnerHistory::CreationDate() { return *entity->getArgument(7); }
bool IfcOwnerHistory::is(Type::Enum v) const { return v == Type::IfcOwnerHistory; }
Type::Enum IfcOwnerHistory::type() const { return Type::IfcOwnerHistory; }
Type::Enum IfcOwnerHistory::Class() { return Type::IfcOwnerHistory; }
IfcOwnerHistory::IfcOwnerHistory(IfcAbstractEntityPtr e) { if (!is(Type::IfcOwnerHistory)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcParameterizedProfileDef
IfcAxis2Placement2D* IfcParameterizedProfileDef::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement2D>(*entity->getArgument(2)); }
bool IfcParameterizedProfileDef::is(Type::Enum v) const { return v == Type::IfcParameterizedProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcParameterizedProfileDef::type() const { return Type::IfcParameterizedProfileDef; }
Type::Enum IfcParameterizedProfileDef::Class() { return Type::IfcParameterizedProfileDef; }
IfcParameterizedProfileDef::IfcParameterizedProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcParameterizedProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPath
SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > IfcPath::EdgeList() { RETURN_AS_LIST(IfcOrientedEdge,0) }
bool IfcPath::is(Type::Enum v) const { return v == Type::IfcPath || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcPath::type() const { return Type::IfcPath; }
Type::Enum IfcPath::Class() { return Type::IfcPath; }
IfcPath::IfcPath(IfcAbstractEntityPtr e) { if (!is(Type::IfcPath)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPerformanceHistory
IfcLabel IfcPerformanceHistory::LifeCyclePhase() { return *entity->getArgument(5); }
bool IfcPerformanceHistory::is(Type::Enum v) const { return v == Type::IfcPerformanceHistory || IfcControl::is(v); }
Type::Enum IfcPerformanceHistory::type() const { return Type::IfcPerformanceHistory; }
Type::Enum IfcPerformanceHistory::Class() { return Type::IfcPerformanceHistory; }
IfcPerformanceHistory::IfcPerformanceHistory(IfcAbstractEntityPtr e) { if (!is(Type::IfcPerformanceHistory)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPermeableCoveringProperties
IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperationEnum IfcPermeableCoveringProperties::OperationType() { return IfcPermeableCoveringOperationEnum::FromString(*entity->getArgument(4)); }
IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum IfcPermeableCoveringProperties::PanelPosition() { return IfcWindowPanelPositionEnum::FromString(*entity->getArgument(5)); }
bool IfcPermeableCoveringProperties::hasFrameDepth() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcPermeableCoveringProperties::FrameDepth() { return *entity->getArgument(6); }
bool IfcPermeableCoveringProperties::hasFrameThickness() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcPermeableCoveringProperties::FrameThickness() { return *entity->getArgument(7); }
bool IfcPermeableCoveringProperties::hasShapeAspectStyle() { return !entity->getArgument(8)->isNull(); }
IfcShapeAspect* IfcPermeableCoveringProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(8)); }
bool IfcPermeableCoveringProperties::is(Type::Enum v) const { return v == Type::IfcPermeableCoveringProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcPermeableCoveringProperties::type() const { return Type::IfcPermeableCoveringProperties; }
Type::Enum IfcPermeableCoveringProperties::Class() { return Type::IfcPermeableCoveringProperties; }
IfcPermeableCoveringProperties::IfcPermeableCoveringProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcPermeableCoveringProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPermit
IfcIdentifier IfcPermit::PermitID() { return *entity->getArgument(5); }
bool IfcPermit::is(Type::Enum v) const { return v == Type::IfcPermit || IfcControl::is(v); }
Type::Enum IfcPermit::type() const { return Type::IfcPermit; }
Type::Enum IfcPermit::Class() { return Type::IfcPermit; }
IfcPermit::IfcPermit(IfcAbstractEntityPtr e) { if (!is(Type::IfcPermit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPerson
bool IfcPerson::hasId() { return !entity->getArgument(0)->isNull(); }
IfcIdentifier IfcPerson::Id() { return *entity->getArgument(0); }
bool IfcPerson::hasFamilyName() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcPerson::FamilyName() { return *entity->getArgument(1); }
bool IfcPerson::hasGivenName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcPerson::GivenName() { return *entity->getArgument(2); }
bool IfcPerson::hasMiddleNames() { return !entity->getArgument(3)->isNull(); }
std::vector<IfcLabel> /*[1:?]*/ IfcPerson::MiddleNames() { return *entity->getArgument(3); }
bool IfcPerson::hasPrefixTitles() { return !entity->getArgument(4)->isNull(); }
std::vector<IfcLabel> /*[1:?]*/ IfcPerson::PrefixTitles() { return *entity->getArgument(4); }
bool IfcPerson::hasSuffixTitles() { return !entity->getArgument(5)->isNull(); }
std::vector<IfcLabel> /*[1:?]*/ IfcPerson::SuffixTitles() { return *entity->getArgument(5); }
bool IfcPerson::hasRoles() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > IfcPerson::Roles() { RETURN_AS_LIST(IfcActorRole,6) }
bool IfcPerson::hasAddresses() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAddress> > IfcPerson::Addresses() { RETURN_AS_LIST(IfcAddress,7) }
IfcPersonAndOrganization::list IfcPerson::EngagedIn() { RETURN_INVERSE(IfcPersonAndOrganization) }
bool IfcPerson::is(Type::Enum v) const { return v == Type::IfcPerson; }
Type::Enum IfcPerson::type() const { return Type::IfcPerson; }
Type::Enum IfcPerson::Class() { return Type::IfcPerson; }
IfcPerson::IfcPerson(IfcAbstractEntityPtr e) { if (!is(Type::IfcPerson)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPersonAndOrganization
IfcPerson* IfcPersonAndOrganization::ThePerson() { return reinterpret_pointer_cast<IfcBaseClass,IfcPerson>(*entity->getArgument(0)); }
IfcOrganization* IfcPersonAndOrganization::TheOrganization() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(1)); }
bool IfcPersonAndOrganization::hasRoles() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > IfcPersonAndOrganization::Roles() { RETURN_AS_LIST(IfcActorRole,2) }
bool IfcPersonAndOrganization::is(Type::Enum v) const { return v == Type::IfcPersonAndOrganization; }
Type::Enum IfcPersonAndOrganization::type() const { return Type::IfcPersonAndOrganization; }
Type::Enum IfcPersonAndOrganization::Class() { return Type::IfcPersonAndOrganization; }
IfcPersonAndOrganization::IfcPersonAndOrganization(IfcAbstractEntityPtr e) { if (!is(Type::IfcPersonAndOrganization)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPhysicalComplexQuantity
SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > IfcPhysicalComplexQuantity::HasQuantities() { RETURN_AS_LIST(IfcPhysicalQuantity,2) }
IfcLabel IfcPhysicalComplexQuantity::Discrimination() { return *entity->getArgument(3); }
bool IfcPhysicalComplexQuantity::hasQuality() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcPhysicalComplexQuantity::Quality() { return *entity->getArgument(4); }
bool IfcPhysicalComplexQuantity::hasUsage() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcPhysicalComplexQuantity::Usage() { return *entity->getArgument(5); }
bool IfcPhysicalComplexQuantity::is(Type::Enum v) const { return v == Type::IfcPhysicalComplexQuantity || IfcPhysicalQuantity::is(v); }
Type::Enum IfcPhysicalComplexQuantity::type() const { return Type::IfcPhysicalComplexQuantity; }
Type::Enum IfcPhysicalComplexQuantity::Class() { return Type::IfcPhysicalComplexQuantity; }
IfcPhysicalComplexQuantity::IfcPhysicalComplexQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcPhysicalComplexQuantity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPhysicalQuantity
IfcLabel IfcPhysicalQuantity::Name() { return *entity->getArgument(0); }
bool IfcPhysicalQuantity::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcPhysicalQuantity::Description() { return *entity->getArgument(1); }
IfcPhysicalComplexQuantity::list IfcPhysicalQuantity::PartOfComplex() { RETURN_INVERSE(IfcPhysicalComplexQuantity) }
bool IfcPhysicalQuantity::is(Type::Enum v) const { return v == Type::IfcPhysicalQuantity; }
Type::Enum IfcPhysicalQuantity::type() const { return Type::IfcPhysicalQuantity; }
Type::Enum IfcPhysicalQuantity::Class() { return Type::IfcPhysicalQuantity; }
IfcPhysicalQuantity::IfcPhysicalQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcPhysicalQuantity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPhysicalSimpleQuantity
bool IfcPhysicalSimpleQuantity::hasUnit() { return !entity->getArgument(2)->isNull(); }
IfcNamedUnit* IfcPhysicalSimpleQuantity::Unit() { return reinterpret_pointer_cast<IfcBaseClass,IfcNamedUnit>(*entity->getArgument(2)); }
bool IfcPhysicalSimpleQuantity::is(Type::Enum v) const { return v == Type::IfcPhysicalSimpleQuantity || IfcPhysicalQuantity::is(v); }
Type::Enum IfcPhysicalSimpleQuantity::type() const { return Type::IfcPhysicalSimpleQuantity; }
Type::Enum IfcPhysicalSimpleQuantity::Class() { return Type::IfcPhysicalSimpleQuantity; }
IfcPhysicalSimpleQuantity::IfcPhysicalSimpleQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcPhysicalSimpleQuantity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPile
IfcPileTypeEnum::IfcPileTypeEnum IfcPile::PredefinedType() { return IfcPileTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcPile::hasConstructionType() { return !entity->getArgument(9)->isNull(); }
IfcPileConstructionEnum::IfcPileConstructionEnum IfcPile::ConstructionType() { return IfcPileConstructionEnum::FromString(*entity->getArgument(9)); }
bool IfcPile::is(Type::Enum v) const { return v == Type::IfcPile || IfcBuildingElement::is(v); }
Type::Enum IfcPile::type() const { return Type::IfcPile; }
Type::Enum IfcPile::Class() { return Type::IfcPile; }
IfcPile::IfcPile(IfcAbstractEntityPtr e) { if (!is(Type::IfcPile)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPipeFittingType
IfcPipeFittingTypeEnum::IfcPipeFittingTypeEnum IfcPipeFittingType::PredefinedType() { return IfcPipeFittingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPipeFittingType::is(Type::Enum v) const { return v == Type::IfcPipeFittingType || IfcFlowFittingType::is(v); }
Type::Enum IfcPipeFittingType::type() const { return Type::IfcPipeFittingType; }
Type::Enum IfcPipeFittingType::Class() { return Type::IfcPipeFittingType; }
IfcPipeFittingType::IfcPipeFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPipeFittingType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPipeSegmentType
IfcPipeSegmentTypeEnum::IfcPipeSegmentTypeEnum IfcPipeSegmentType::PredefinedType() { return IfcPipeSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPipeSegmentType::is(Type::Enum v) const { return v == Type::IfcPipeSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcPipeSegmentType::type() const { return Type::IfcPipeSegmentType; }
Type::Enum IfcPipeSegmentType::Class() { return Type::IfcPipeSegmentType; }
IfcPipeSegmentType::IfcPipeSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPipeSegmentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPixelTexture
IfcInteger IfcPixelTexture::Width() { return *entity->getArgument(4); }
IfcInteger IfcPixelTexture::Height() { return *entity->getArgument(5); }
IfcInteger IfcPixelTexture::ColourComponents() { return *entity->getArgument(6); }
std::vector<char[32]> /*[1:?]*/ IfcPixelTexture::Pixel() { throw; /* Not implemented argument 7 */ }
bool IfcPixelTexture::is(Type::Enum v) const { return v == Type::IfcPixelTexture || IfcSurfaceTexture::is(v); }
Type::Enum IfcPixelTexture::type() const { return Type::IfcPixelTexture; }
Type::Enum IfcPixelTexture::Class() { return Type::IfcPixelTexture; }
IfcPixelTexture::IfcPixelTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcPixelTexture)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPlacement
IfcCartesianPoint* IfcPlacement::Location() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(0)); }
bool IfcPlacement::is(Type::Enum v) const { return v == Type::IfcPlacement || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcPlacement::type() const { return Type::IfcPlacement; }
Type::Enum IfcPlacement::Class() { return Type::IfcPlacement; }
IfcPlacement::IfcPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlacement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPlanarBox
IfcAxis2Placement IfcPlanarBox::Placement() { return *entity->getArgument(2); }
bool IfcPlanarBox::is(Type::Enum v) const { return v == Type::IfcPlanarBox || IfcPlanarExtent::is(v); }
Type::Enum IfcPlanarBox::type() const { return Type::IfcPlanarBox; }
Type::Enum IfcPlanarBox::Class() { return Type::IfcPlanarBox; }
IfcPlanarBox::IfcPlanarBox(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlanarBox)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPlanarExtent
IfcLengthMeasure IfcPlanarExtent::SizeInX() { return *entity->getArgument(0); }
IfcLengthMeasure IfcPlanarExtent::SizeInY() { return *entity->getArgument(1); }
bool IfcPlanarExtent::is(Type::Enum v) const { return v == Type::IfcPlanarExtent || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcPlanarExtent::type() const { return Type::IfcPlanarExtent; }
Type::Enum IfcPlanarExtent::Class() { return Type::IfcPlanarExtent; }
IfcPlanarExtent::IfcPlanarExtent(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlanarExtent)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPlane
bool IfcPlane::is(Type::Enum v) const { return v == Type::IfcPlane || IfcElementarySurface::is(v); }
Type::Enum IfcPlane::type() const { return Type::IfcPlane; }
Type::Enum IfcPlane::Class() { return Type::IfcPlane; }
IfcPlane::IfcPlane(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlane)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPlate
bool IfcPlate::is(Type::Enum v) const { return v == Type::IfcPlate || IfcBuildingElement::is(v); }
Type::Enum IfcPlate::type() const { return Type::IfcPlate; }
Type::Enum IfcPlate::Class() { return Type::IfcPlate; }
IfcPlate::IfcPlate(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlate)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPlateType
IfcPlateTypeEnum::IfcPlateTypeEnum IfcPlateType::PredefinedType() { return IfcPlateTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPlateType::is(Type::Enum v) const { return v == Type::IfcPlateType || IfcBuildingElementType::is(v); }
Type::Enum IfcPlateType::type() const { return Type::IfcPlateType; }
Type::Enum IfcPlateType::Class() { return Type::IfcPlateType; }
IfcPlateType::IfcPlateType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlateType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPoint
bool IfcPoint::is(Type::Enum v) const { return v == Type::IfcPoint || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcPoint::type() const { return Type::IfcPoint; }
Type::Enum IfcPoint::Class() { return Type::IfcPoint; }
IfcPoint::IfcPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcPoint)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPointOnCurve
IfcCurve* IfcPointOnCurve::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcParameterValue IfcPointOnCurve::PointParameter() { return *entity->getArgument(1); }
bool IfcPointOnCurve::is(Type::Enum v) const { return v == Type::IfcPointOnCurve || IfcPoint::is(v); }
Type::Enum IfcPointOnCurve::type() const { return Type::IfcPointOnCurve; }
Type::Enum IfcPointOnCurve::Class() { return Type::IfcPointOnCurve; }
IfcPointOnCurve::IfcPointOnCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcPointOnCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPointOnSurface
IfcSurface* IfcPointOnSurface::BasisSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(0)); }
IfcParameterValue IfcPointOnSurface::PointParameterU() { return *entity->getArgument(1); }
IfcParameterValue IfcPointOnSurface::PointParameterV() { return *entity->getArgument(2); }
bool IfcPointOnSurface::is(Type::Enum v) const { return v == Type::IfcPointOnSurface || IfcPoint::is(v); }
Type::Enum IfcPointOnSurface::type() const { return Type::IfcPointOnSurface; }
Type::Enum IfcPointOnSurface::Class() { return Type::IfcPointOnSurface; }
IfcPointOnSurface::IfcPointOnSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcPointOnSurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPolyLoop
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcPolyLoop::Polygon() { RETURN_AS_LIST(IfcCartesianPoint,0) }
bool IfcPolyLoop::is(Type::Enum v) const { return v == Type::IfcPolyLoop || IfcLoop::is(v); }
Type::Enum IfcPolyLoop::type() const { return Type::IfcPolyLoop; }
Type::Enum IfcPolyLoop::Class() { return Type::IfcPolyLoop; }
IfcPolyLoop::IfcPolyLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcPolyLoop)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPolygonalBoundedHalfSpace
IfcAxis2Placement3D* IfcPolygonalBoundedHalfSpace::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(2)); }
IfcBoundedCurve* IfcPolygonalBoundedHalfSpace::PolygonalBoundary() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundedCurve>(*entity->getArgument(3)); }
bool IfcPolygonalBoundedHalfSpace::is(Type::Enum v) const { return v == Type::IfcPolygonalBoundedHalfSpace || IfcHalfSpaceSolid::is(v); }
Type::Enum IfcPolygonalBoundedHalfSpace::type() const { return Type::IfcPolygonalBoundedHalfSpace; }
Type::Enum IfcPolygonalBoundedHalfSpace::Class() { return Type::IfcPolygonalBoundedHalfSpace; }
IfcPolygonalBoundedHalfSpace::IfcPolygonalBoundedHalfSpace(IfcAbstractEntityPtr e) { if (!is(Type::IfcPolygonalBoundedHalfSpace)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPolyline
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcPolyline::Points() { RETURN_AS_LIST(IfcCartesianPoint,0) }
bool IfcPolyline::is(Type::Enum v) const { return v == Type::IfcPolyline || IfcBoundedCurve::is(v); }
Type::Enum IfcPolyline::type() const { return Type::IfcPolyline; }
Type::Enum IfcPolyline::Class() { return Type::IfcPolyline; }
IfcPolyline::IfcPolyline(IfcAbstractEntityPtr e) { if (!is(Type::IfcPolyline)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPort
IfcRelConnectsPortToElement::list IfcPort::ContainedIn() { RETURN_INVERSE(IfcRelConnectsPortToElement) }
IfcRelConnectsPorts::list IfcPort::ConnectedFrom() { RETURN_INVERSE(IfcRelConnectsPorts) }
IfcRelConnectsPorts::list IfcPort::ConnectedTo() { RETURN_INVERSE(IfcRelConnectsPorts) }
bool IfcPort::is(Type::Enum v) const { return v == Type::IfcPort || IfcProduct::is(v); }
Type::Enum IfcPort::type() const { return Type::IfcPort; }
Type::Enum IfcPort::Class() { return Type::IfcPort; }
IfcPort::IfcPort(IfcAbstractEntityPtr e) { if (!is(Type::IfcPort)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPostalAddress
bool IfcPostalAddress::hasInternalLocation() { return !entity->getArgument(3)->isNull(); }
IfcLabel IfcPostalAddress::InternalLocation() { return *entity->getArgument(3); }
bool IfcPostalAddress::hasAddressLines() { return !entity->getArgument(4)->isNull(); }
std::vector<IfcLabel> /*[1:?]*/ IfcPostalAddress::AddressLines() { return *entity->getArgument(4); }
bool IfcPostalAddress::hasPostalBox() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcPostalAddress::PostalBox() { return *entity->getArgument(5); }
bool IfcPostalAddress::hasTown() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcPostalAddress::Town() { return *entity->getArgument(6); }
bool IfcPostalAddress::hasRegion() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcPostalAddress::Region() { return *entity->getArgument(7); }
bool IfcPostalAddress::hasPostalCode() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcPostalAddress::PostalCode() { return *entity->getArgument(8); }
bool IfcPostalAddress::hasCountry() { return !entity->getArgument(9)->isNull(); }
IfcLabel IfcPostalAddress::Country() { return *entity->getArgument(9); }
bool IfcPostalAddress::is(Type::Enum v) const { return v == Type::IfcPostalAddress || IfcAddress::is(v); }
Type::Enum IfcPostalAddress::type() const { return Type::IfcPostalAddress; }
Type::Enum IfcPostalAddress::Class() { return Type::IfcPostalAddress; }
IfcPostalAddress::IfcPostalAddress(IfcAbstractEntityPtr e) { if (!is(Type::IfcPostalAddress)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedColour
bool IfcPreDefinedColour::is(Type::Enum v) const { return v == Type::IfcPreDefinedColour || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedColour::type() const { return Type::IfcPreDefinedColour; }
Type::Enum IfcPreDefinedColour::Class() { return Type::IfcPreDefinedColour; }
IfcPreDefinedColour::IfcPreDefinedColour(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedColour)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedCurveFont
bool IfcPreDefinedCurveFont::is(Type::Enum v) const { return v == Type::IfcPreDefinedCurveFont || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedCurveFont::type() const { return Type::IfcPreDefinedCurveFont; }
Type::Enum IfcPreDefinedCurveFont::Class() { return Type::IfcPreDefinedCurveFont; }
IfcPreDefinedCurveFont::IfcPreDefinedCurveFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedCurveFont)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedDimensionSymbol
bool IfcPreDefinedDimensionSymbol::is(Type::Enum v) const { return v == Type::IfcPreDefinedDimensionSymbol || IfcPreDefinedSymbol::is(v); }
Type::Enum IfcPreDefinedDimensionSymbol::type() const { return Type::IfcPreDefinedDimensionSymbol; }
Type::Enum IfcPreDefinedDimensionSymbol::Class() { return Type::IfcPreDefinedDimensionSymbol; }
IfcPreDefinedDimensionSymbol::IfcPreDefinedDimensionSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedDimensionSymbol)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedItem
IfcLabel IfcPreDefinedItem::Name() { return *entity->getArgument(0); }
bool IfcPreDefinedItem::is(Type::Enum v) const { return v == Type::IfcPreDefinedItem; }
Type::Enum IfcPreDefinedItem::type() const { return Type::IfcPreDefinedItem; }
Type::Enum IfcPreDefinedItem::Class() { return Type::IfcPreDefinedItem; }
IfcPreDefinedItem::IfcPreDefinedItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedPointMarkerSymbol
bool IfcPreDefinedPointMarkerSymbol::is(Type::Enum v) const { return v == Type::IfcPreDefinedPointMarkerSymbol || IfcPreDefinedSymbol::is(v); }
Type::Enum IfcPreDefinedPointMarkerSymbol::type() const { return Type::IfcPreDefinedPointMarkerSymbol; }
Type::Enum IfcPreDefinedPointMarkerSymbol::Class() { return Type::IfcPreDefinedPointMarkerSymbol; }
IfcPreDefinedPointMarkerSymbol::IfcPreDefinedPointMarkerSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedPointMarkerSymbol)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedSymbol
bool IfcPreDefinedSymbol::is(Type::Enum v) const { return v == Type::IfcPreDefinedSymbol || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedSymbol::type() const { return Type::IfcPreDefinedSymbol; }
Type::Enum IfcPreDefinedSymbol::Class() { return Type::IfcPreDefinedSymbol; }
IfcPreDefinedSymbol::IfcPreDefinedSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedSymbol)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedTerminatorSymbol
bool IfcPreDefinedTerminatorSymbol::is(Type::Enum v) const { return v == Type::IfcPreDefinedTerminatorSymbol || IfcPreDefinedSymbol::is(v); }
Type::Enum IfcPreDefinedTerminatorSymbol::type() const { return Type::IfcPreDefinedTerminatorSymbol; }
Type::Enum IfcPreDefinedTerminatorSymbol::Class() { return Type::IfcPreDefinedTerminatorSymbol; }
IfcPreDefinedTerminatorSymbol::IfcPreDefinedTerminatorSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedTerminatorSymbol)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPreDefinedTextFont
bool IfcPreDefinedTextFont::is(Type::Enum v) const { return v == Type::IfcPreDefinedTextFont || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedTextFont::type() const { return Type::IfcPreDefinedTextFont; }
Type::Enum IfcPreDefinedTextFont::Class() { return Type::IfcPreDefinedTextFont; }
IfcPreDefinedTextFont::IfcPreDefinedTextFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedTextFont)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPresentationLayerAssignment
IfcLabel IfcPresentationLayerAssignment::Name() { return *entity->getArgument(0); }
bool IfcPresentationLayerAssignment::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcPresentationLayerAssignment::Description() { return *entity->getArgument(1); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPresentationLayerAssignment::AssignedItems() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcPresentationLayerAssignment::hasIdentifier() { return !entity->getArgument(3)->isNull(); }
IfcIdentifier IfcPresentationLayerAssignment::Identifier() { return *entity->getArgument(3); }
bool IfcPresentationLayerAssignment::is(Type::Enum v) const { return v == Type::IfcPresentationLayerAssignment; }
Type::Enum IfcPresentationLayerAssignment::type() const { return Type::IfcPresentationLayerAssignment; }
Type::Enum IfcPresentationLayerAssignment::Class() { return Type::IfcPresentationLayerAssignment; }
IfcPresentationLayerAssignment::IfcPresentationLayerAssignment(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationLayerAssignment)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPresentationLayerWithStyle
bool IfcPresentationLayerWithStyle::LayerOn() { return *entity->getArgument(4); }
bool IfcPresentationLayerWithStyle::LayerFrozen() { return *entity->getArgument(5); }
bool IfcPresentationLayerWithStyle::LayerBlocked() { return *entity->getArgument(6); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPresentationLayerWithStyle::LayerStyles() { RETURN_AS_LIST(IfcAbstractSelect,7) }
bool IfcPresentationLayerWithStyle::is(Type::Enum v) const { return v == Type::IfcPresentationLayerWithStyle || IfcPresentationLayerAssignment::is(v); }
Type::Enum IfcPresentationLayerWithStyle::type() const { return Type::IfcPresentationLayerWithStyle; }
Type::Enum IfcPresentationLayerWithStyle::Class() { return Type::IfcPresentationLayerWithStyle; }
IfcPresentationLayerWithStyle::IfcPresentationLayerWithStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationLayerWithStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPresentationStyle
bool IfcPresentationStyle::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcPresentationStyle::Name() { return *entity->getArgument(0); }
bool IfcPresentationStyle::is(Type::Enum v) const { return v == Type::IfcPresentationStyle; }
Type::Enum IfcPresentationStyle::type() const { return Type::IfcPresentationStyle; }
Type::Enum IfcPresentationStyle::Class() { return Type::IfcPresentationStyle; }
IfcPresentationStyle::IfcPresentationStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPresentationStyleAssignment
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPresentationStyleAssignment::Styles() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcPresentationStyleAssignment::is(Type::Enum v) const { return v == Type::IfcPresentationStyleAssignment; }
Type::Enum IfcPresentationStyleAssignment::type() const { return Type::IfcPresentationStyleAssignment; }
Type::Enum IfcPresentationStyleAssignment::Class() { return Type::IfcPresentationStyleAssignment; }
IfcPresentationStyleAssignment::IfcPresentationStyleAssignment(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationStyleAssignment)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProcedure
IfcIdentifier IfcProcedure::ProcedureID() { return *entity->getArgument(5); }
IfcProcedureTypeEnum::IfcProcedureTypeEnum IfcProcedure::ProcedureType() { return IfcProcedureTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcProcedure::hasUserDefinedProcedureType() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcProcedure::UserDefinedProcedureType() { return *entity->getArgument(7); }
bool IfcProcedure::is(Type::Enum v) const { return v == Type::IfcProcedure || IfcProcess::is(v); }
Type::Enum IfcProcedure::type() const { return Type::IfcProcedure; }
Type::Enum IfcProcedure::Class() { return Type::IfcProcedure; }
IfcProcedure::IfcProcedure(IfcAbstractEntityPtr e) { if (!is(Type::IfcProcedure)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProcess
IfcRelAssignsToProcess::list IfcProcess::OperatesOn() { RETURN_INVERSE(IfcRelAssignsToProcess) }
IfcRelSequence::list IfcProcess::IsSuccessorFrom() { RETURN_INVERSE(IfcRelSequence) }
IfcRelSequence::list IfcProcess::IsPredecessorTo() { RETURN_INVERSE(IfcRelSequence) }
bool IfcProcess::is(Type::Enum v) const { return v == Type::IfcProcess || IfcObject::is(v); }
Type::Enum IfcProcess::type() const { return Type::IfcProcess; }
Type::Enum IfcProcess::Class() { return Type::IfcProcess; }
IfcProcess::IfcProcess(IfcAbstractEntityPtr e) { if (!is(Type::IfcProcess)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProduct
bool IfcProduct::hasObjectPlacement() { return !entity->getArgument(5)->isNull(); }
IfcObjectPlacement* IfcProduct::ObjectPlacement() { return reinterpret_pointer_cast<IfcBaseClass,IfcObjectPlacement>(*entity->getArgument(5)); }
bool IfcProduct::hasRepresentation() { return !entity->getArgument(6)->isNull(); }
IfcProductRepresentation* IfcProduct::Representation() { return reinterpret_pointer_cast<IfcBaseClass,IfcProductRepresentation>(*entity->getArgument(6)); }
IfcRelAssignsToProduct::list IfcProduct::ReferencedBy() { RETURN_INVERSE(IfcRelAssignsToProduct) }
bool IfcProduct::is(Type::Enum v) const { return v == Type::IfcProduct || IfcObject::is(v); }
Type::Enum IfcProduct::type() const { return Type::IfcProduct; }
Type::Enum IfcProduct::Class() { return Type::IfcProduct; }
IfcProduct::IfcProduct(IfcAbstractEntityPtr e) { if (!is(Type::IfcProduct)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProductDefinitionShape
IfcProduct::list IfcProductDefinitionShape::ShapeOfProduct() { RETURN_INVERSE(IfcProduct) }
IfcShapeAspect::list IfcProductDefinitionShape::HasShapeAspects() { RETURN_INVERSE(IfcShapeAspect) }
bool IfcProductDefinitionShape::is(Type::Enum v) const { return v == Type::IfcProductDefinitionShape || IfcProductRepresentation::is(v); }
Type::Enum IfcProductDefinitionShape::type() const { return Type::IfcProductDefinitionShape; }
Type::Enum IfcProductDefinitionShape::Class() { return Type::IfcProductDefinitionShape; }
IfcProductDefinitionShape::IfcProductDefinitionShape(IfcAbstractEntityPtr e) { if (!is(Type::IfcProductDefinitionShape)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProductRepresentation
bool IfcProductRepresentation::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcProductRepresentation::Name() { return *entity->getArgument(0); }
bool IfcProductRepresentation::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcProductRepresentation::Description() { return *entity->getArgument(1); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentation> > IfcProductRepresentation::Representations() { RETURN_AS_LIST(IfcRepresentation,2) }
bool IfcProductRepresentation::is(Type::Enum v) const { return v == Type::IfcProductRepresentation; }
Type::Enum IfcProductRepresentation::type() const { return Type::IfcProductRepresentation; }
Type::Enum IfcProductRepresentation::Class() { return Type::IfcProductRepresentation; }
IfcProductRepresentation::IfcProductRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcProductRepresentation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProductsOfCombustionProperties
bool IfcProductsOfCombustionProperties::hasSpecificHeatCapacity() { return !entity->getArgument(1)->isNull(); }
IfcSpecificHeatCapacityMeasure IfcProductsOfCombustionProperties::SpecificHeatCapacity() { return *entity->getArgument(1); }
bool IfcProductsOfCombustionProperties::hasN20Content() { return !entity->getArgument(2)->isNull(); }
IfcPositiveRatioMeasure IfcProductsOfCombustionProperties::N20Content() { return *entity->getArgument(2); }
bool IfcProductsOfCombustionProperties::hasCOContent() { return !entity->getArgument(3)->isNull(); }
IfcPositiveRatioMeasure IfcProductsOfCombustionProperties::COContent() { return *entity->getArgument(3); }
bool IfcProductsOfCombustionProperties::hasCO2Content() { return !entity->getArgument(4)->isNull(); }
IfcPositiveRatioMeasure IfcProductsOfCombustionProperties::CO2Content() { return *entity->getArgument(4); }
bool IfcProductsOfCombustionProperties::is(Type::Enum v) const { return v == Type::IfcProductsOfCombustionProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcProductsOfCombustionProperties::type() const { return Type::IfcProductsOfCombustionProperties; }
Type::Enum IfcProductsOfCombustionProperties::Class() { return Type::IfcProductsOfCombustionProperties; }
IfcProductsOfCombustionProperties::IfcProductsOfCombustionProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcProductsOfCombustionProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProfileDef
IfcProfileTypeEnum::IfcProfileTypeEnum IfcProfileDef::ProfileType() { return IfcProfileTypeEnum::FromString(*entity->getArgument(0)); }
bool IfcProfileDef::hasProfileName() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcProfileDef::ProfileName() { return *entity->getArgument(1); }
bool IfcProfileDef::is(Type::Enum v) const { return v == Type::IfcProfileDef; }
Type::Enum IfcProfileDef::type() const { return Type::IfcProfileDef; }
Type::Enum IfcProfileDef::Class() { return Type::IfcProfileDef; }
IfcProfileDef::IfcProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProfileProperties
bool IfcProfileProperties::hasProfileName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcProfileProperties::ProfileName() { return *entity->getArgument(0); }
bool IfcProfileProperties::hasProfileDefinition() { return !entity->getArgument(1)->isNull(); }
IfcProfileDef* IfcProfileProperties::ProfileDefinition() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(1)); }
bool IfcProfileProperties::is(Type::Enum v) const { return v == Type::IfcProfileProperties; }
Type::Enum IfcProfileProperties::type() const { return Type::IfcProfileProperties; }
Type::Enum IfcProfileProperties::Class() { return Type::IfcProfileProperties; }
IfcProfileProperties::IfcProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcProfileProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProject
bool IfcProject::hasLongName() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcProject::LongName() { return *entity->getArgument(5); }
bool IfcProject::hasPhase() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcProject::Phase() { return *entity->getArgument(6); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationContext> > IfcProject::RepresentationContexts() { RETURN_AS_LIST(IfcRepresentationContext,7) }
IfcUnitAssignment* IfcProject::UnitsInContext() { return reinterpret_pointer_cast<IfcBaseClass,IfcUnitAssignment>(*entity->getArgument(8)); }
bool IfcProject::is(Type::Enum v) const { return v == Type::IfcProject || IfcObject::is(v); }
Type::Enum IfcProject::type() const { return Type::IfcProject; }
Type::Enum IfcProject::Class() { return Type::IfcProject; }
IfcProject::IfcProject(IfcAbstractEntityPtr e) { if (!is(Type::IfcProject)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProjectOrder
IfcIdentifier IfcProjectOrder::ID() { return *entity->getArgument(5); }
IfcProjectOrderTypeEnum::IfcProjectOrderTypeEnum IfcProjectOrder::PredefinedType() { return IfcProjectOrderTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcProjectOrder::hasStatus() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcProjectOrder::Status() { return *entity->getArgument(7); }
bool IfcProjectOrder::is(Type::Enum v) const { return v == Type::IfcProjectOrder || IfcControl::is(v); }
Type::Enum IfcProjectOrder::type() const { return Type::IfcProjectOrder; }
Type::Enum IfcProjectOrder::Class() { return Type::IfcProjectOrder; }
IfcProjectOrder::IfcProjectOrder(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectOrder)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProjectOrderRecord
SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProjectOrder> > IfcProjectOrderRecord::Records() { RETURN_AS_LIST(IfcRelAssignsToProjectOrder,5) }
IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordTypeEnum IfcProjectOrderRecord::PredefinedType() { return IfcProjectOrderRecordTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcProjectOrderRecord::is(Type::Enum v) const { return v == Type::IfcProjectOrderRecord || IfcControl::is(v); }
Type::Enum IfcProjectOrderRecord::type() const { return Type::IfcProjectOrderRecord; }
Type::Enum IfcProjectOrderRecord::Class() { return Type::IfcProjectOrderRecord; }
IfcProjectOrderRecord::IfcProjectOrderRecord(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectOrderRecord)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProjectionCurve
bool IfcProjectionCurve::is(Type::Enum v) const { return v == Type::IfcProjectionCurve || IfcAnnotationCurveOccurrence::is(v); }
Type::Enum IfcProjectionCurve::type() const { return Type::IfcProjectionCurve; }
Type::Enum IfcProjectionCurve::Class() { return Type::IfcProjectionCurve; }
IfcProjectionCurve::IfcProjectionCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectionCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProjectionElement
bool IfcProjectionElement::is(Type::Enum v) const { return v == Type::IfcProjectionElement || IfcFeatureElementAddition::is(v); }
Type::Enum IfcProjectionElement::type() const { return Type::IfcProjectionElement; }
Type::Enum IfcProjectionElement::Class() { return Type::IfcProjectionElement; }
IfcProjectionElement::IfcProjectionElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectionElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProperty
IfcIdentifier IfcProperty::Name() { return *entity->getArgument(0); }
bool IfcProperty::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcProperty::Description() { return *entity->getArgument(1); }
IfcPropertyDependencyRelationship::list IfcProperty::PropertyForDependance() { RETURN_INVERSE(IfcPropertyDependencyRelationship) }
IfcPropertyDependencyRelationship::list IfcProperty::PropertyDependsOn() { RETURN_INVERSE(IfcPropertyDependencyRelationship) }
IfcComplexProperty::list IfcProperty::PartOfComplex() { RETURN_INVERSE(IfcComplexProperty) }
bool IfcProperty::is(Type::Enum v) const { return v == Type::IfcProperty; }
Type::Enum IfcProperty::type() const { return Type::IfcProperty; }
Type::Enum IfcProperty::Class() { return Type::IfcProperty; }
IfcProperty::IfcProperty(IfcAbstractEntityPtr e) { if (!is(Type::IfcProperty)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyBoundedValue
bool IfcPropertyBoundedValue::hasUpperBoundValue() { return !entity->getArgument(2)->isNull(); }
IfcValue IfcPropertyBoundedValue::UpperBoundValue() { return *entity->getArgument(2); }
bool IfcPropertyBoundedValue::hasLowerBoundValue() { return !entity->getArgument(3)->isNull(); }
IfcValue IfcPropertyBoundedValue::LowerBoundValue() { return *entity->getArgument(3); }
bool IfcPropertyBoundedValue::hasUnit() { return !entity->getArgument(4)->isNull(); }
IfcUnit IfcPropertyBoundedValue::Unit() { return *entity->getArgument(4); }
bool IfcPropertyBoundedValue::is(Type::Enum v) const { return v == Type::IfcPropertyBoundedValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyBoundedValue::type() const { return Type::IfcPropertyBoundedValue; }
Type::Enum IfcPropertyBoundedValue::Class() { return Type::IfcPropertyBoundedValue; }
IfcPropertyBoundedValue::IfcPropertyBoundedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyBoundedValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyConstraintRelationship
IfcConstraint* IfcPropertyConstraintRelationship::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcPropertyConstraintRelationship::RelatedProperties() { RETURN_AS_LIST(IfcProperty,1) }
bool IfcPropertyConstraintRelationship::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcPropertyConstraintRelationship::Name() { return *entity->getArgument(2); }
bool IfcPropertyConstraintRelationship::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcPropertyConstraintRelationship::Description() { return *entity->getArgument(3); }
bool IfcPropertyConstraintRelationship::is(Type::Enum v) const { return v == Type::IfcPropertyConstraintRelationship; }
Type::Enum IfcPropertyConstraintRelationship::type() const { return Type::IfcPropertyConstraintRelationship; }
Type::Enum IfcPropertyConstraintRelationship::Class() { return Type::IfcPropertyConstraintRelationship; }
IfcPropertyConstraintRelationship::IfcPropertyConstraintRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyConstraintRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyDefinition
IfcRelAssociates::list IfcPropertyDefinition::HasAssociations() { RETURN_INVERSE(IfcRelAssociates) }
bool IfcPropertyDefinition::is(Type::Enum v) const { return v == Type::IfcPropertyDefinition || IfcRoot::is(v); }
Type::Enum IfcPropertyDefinition::type() const { return Type::IfcPropertyDefinition; }
Type::Enum IfcPropertyDefinition::Class() { return Type::IfcPropertyDefinition; }
IfcPropertyDefinition::IfcPropertyDefinition(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyDefinition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyDependencyRelationship
IfcProperty* IfcPropertyDependencyRelationship::DependingProperty() { return reinterpret_pointer_cast<IfcBaseClass,IfcProperty>(*entity->getArgument(0)); }
IfcProperty* IfcPropertyDependencyRelationship::DependantProperty() { return reinterpret_pointer_cast<IfcBaseClass,IfcProperty>(*entity->getArgument(1)); }
bool IfcPropertyDependencyRelationship::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcPropertyDependencyRelationship::Name() { return *entity->getArgument(2); }
bool IfcPropertyDependencyRelationship::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcPropertyDependencyRelationship::Description() { return *entity->getArgument(3); }
bool IfcPropertyDependencyRelationship::hasExpression() { return !entity->getArgument(4)->isNull(); }
IfcText IfcPropertyDependencyRelationship::Expression() { return *entity->getArgument(4); }
bool IfcPropertyDependencyRelationship::is(Type::Enum v) const { return v == Type::IfcPropertyDependencyRelationship; }
Type::Enum IfcPropertyDependencyRelationship::type() const { return Type::IfcPropertyDependencyRelationship; }
Type::Enum IfcPropertyDependencyRelationship::Class() { return Type::IfcPropertyDependencyRelationship; }
IfcPropertyDependencyRelationship::IfcPropertyDependencyRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyDependencyRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyEnumeratedValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyEnumeratedValue::EnumerationValues() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcPropertyEnumeratedValue::hasEnumerationReference() { return !entity->getArgument(3)->isNull(); }
IfcPropertyEnumeration* IfcPropertyEnumeratedValue::EnumerationReference() { return reinterpret_pointer_cast<IfcBaseClass,IfcPropertyEnumeration>(*entity->getArgument(3)); }
bool IfcPropertyEnumeratedValue::is(Type::Enum v) const { return v == Type::IfcPropertyEnumeratedValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyEnumeratedValue::type() const { return Type::IfcPropertyEnumeratedValue; }
Type::Enum IfcPropertyEnumeratedValue::Class() { return Type::IfcPropertyEnumeratedValue; }
IfcPropertyEnumeratedValue::IfcPropertyEnumeratedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyEnumeratedValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyEnumeration
IfcLabel IfcPropertyEnumeration::Name() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyEnumeration::EnumerationValues() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcPropertyEnumeration::hasUnit() { return !entity->getArgument(2)->isNull(); }
IfcUnit IfcPropertyEnumeration::Unit() { return *entity->getArgument(2); }
bool IfcPropertyEnumeration::is(Type::Enum v) const { return v == Type::IfcPropertyEnumeration; }
Type::Enum IfcPropertyEnumeration::type() const { return Type::IfcPropertyEnumeration; }
Type::Enum IfcPropertyEnumeration::Class() { return Type::IfcPropertyEnumeration; }
IfcPropertyEnumeration::IfcPropertyEnumeration(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyEnumeration)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyListValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyListValue::ListValues() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcPropertyListValue::hasUnit() { return !entity->getArgument(3)->isNull(); }
IfcUnit IfcPropertyListValue::Unit() { return *entity->getArgument(3); }
bool IfcPropertyListValue::is(Type::Enum v) const { return v == Type::IfcPropertyListValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyListValue::type() const { return Type::IfcPropertyListValue; }
Type::Enum IfcPropertyListValue::Class() { return Type::IfcPropertyListValue; }
IfcPropertyListValue::IfcPropertyListValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyListValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyReferenceValue
bool IfcPropertyReferenceValue::hasUsageName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcPropertyReferenceValue::UsageName() { return *entity->getArgument(2); }
IfcObjectReferenceSelect IfcPropertyReferenceValue::PropertyReference() { return *entity->getArgument(3); }
bool IfcPropertyReferenceValue::is(Type::Enum v) const { return v == Type::IfcPropertyReferenceValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyReferenceValue::type() const { return Type::IfcPropertyReferenceValue; }
Type::Enum IfcPropertyReferenceValue::Class() { return Type::IfcPropertyReferenceValue; }
IfcPropertyReferenceValue::IfcPropertyReferenceValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyReferenceValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertySet
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcPropertySet::HasProperties() { RETURN_AS_LIST(IfcProperty,4) }
bool IfcPropertySet::is(Type::Enum v) const { return v == Type::IfcPropertySet || IfcPropertySetDefinition::is(v); }
Type::Enum IfcPropertySet::type() const { return Type::IfcPropertySet; }
Type::Enum IfcPropertySet::Class() { return Type::IfcPropertySet; }
IfcPropertySet::IfcPropertySet(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertySet)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertySetDefinition
IfcRelDefinesByProperties::list IfcPropertySetDefinition::PropertyDefinitionOf() { RETURN_INVERSE(IfcRelDefinesByProperties) }
IfcTypeObject::list IfcPropertySetDefinition::DefinesType() { RETURN_INVERSE(IfcTypeObject) }
bool IfcPropertySetDefinition::is(Type::Enum v) const { return v == Type::IfcPropertySetDefinition || IfcPropertyDefinition::is(v); }
Type::Enum IfcPropertySetDefinition::type() const { return Type::IfcPropertySetDefinition; }
Type::Enum IfcPropertySetDefinition::Class() { return Type::IfcPropertySetDefinition; }
IfcPropertySetDefinition::IfcPropertySetDefinition(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertySetDefinition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertySingleValue
bool IfcPropertySingleValue::hasNominalValue() { return !entity->getArgument(2)->isNull(); }
IfcValue IfcPropertySingleValue::NominalValue() { return *entity->getArgument(2); }
bool IfcPropertySingleValue::hasUnit() { return !entity->getArgument(3)->isNull(); }
IfcUnit IfcPropertySingleValue::Unit() { return *entity->getArgument(3); }
bool IfcPropertySingleValue::is(Type::Enum v) const { return v == Type::IfcPropertySingleValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertySingleValue::type() const { return Type::IfcPropertySingleValue; }
Type::Enum IfcPropertySingleValue::Class() { return Type::IfcPropertySingleValue; }
IfcPropertySingleValue::IfcPropertySingleValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertySingleValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPropertyTableValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyTableValue::DefiningValues() { RETURN_AS_LIST(IfcAbstractSelect,2) }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyTableValue::DefinedValues() { RETURN_AS_LIST(IfcAbstractSelect,3) }
bool IfcPropertyTableValue::hasExpression() { return !entity->getArgument(4)->isNull(); }
IfcText IfcPropertyTableValue::Expression() { return *entity->getArgument(4); }
bool IfcPropertyTableValue::hasDefiningUnit() { return !entity->getArgument(5)->isNull(); }
IfcUnit IfcPropertyTableValue::DefiningUnit() { return *entity->getArgument(5); }
bool IfcPropertyTableValue::hasDefinedUnit() { return !entity->getArgument(6)->isNull(); }
IfcUnit IfcPropertyTableValue::DefinedUnit() { return *entity->getArgument(6); }
bool IfcPropertyTableValue::is(Type::Enum v) const { return v == Type::IfcPropertyTableValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyTableValue::type() const { return Type::IfcPropertyTableValue; }
Type::Enum IfcPropertyTableValue::Class() { return Type::IfcPropertyTableValue; }
IfcPropertyTableValue::IfcPropertyTableValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyTableValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProtectiveDeviceType
IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceTypeEnum IfcProtectiveDeviceType::PredefinedType() { return IfcProtectiveDeviceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcProtectiveDeviceType::is(Type::Enum v) const { return v == Type::IfcProtectiveDeviceType || IfcFlowControllerType::is(v); }
Type::Enum IfcProtectiveDeviceType::type() const { return Type::IfcProtectiveDeviceType; }
Type::Enum IfcProtectiveDeviceType::Class() { return Type::IfcProtectiveDeviceType; }
IfcProtectiveDeviceType::IfcProtectiveDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcProtectiveDeviceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcProxy
IfcObjectTypeEnum::IfcObjectTypeEnum IfcProxy::ProxyType() { return IfcObjectTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcProxy::hasTag() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcProxy::Tag() { return *entity->getArgument(8); }
bool IfcProxy::is(Type::Enum v) const { return v == Type::IfcProxy || IfcProduct::is(v); }
Type::Enum IfcProxy::type() const { return Type::IfcProxy; }
Type::Enum IfcProxy::Class() { return Type::IfcProxy; }
IfcProxy::IfcProxy(IfcAbstractEntityPtr e) { if (!is(Type::IfcProxy)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcPumpType
IfcPumpTypeEnum::IfcPumpTypeEnum IfcPumpType::PredefinedType() { return IfcPumpTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPumpType::is(Type::Enum v) const { return v == Type::IfcPumpType || IfcFlowMovingDeviceType::is(v); }
Type::Enum IfcPumpType::type() const { return Type::IfcPumpType; }
Type::Enum IfcPumpType::Class() { return Type::IfcPumpType; }
IfcPumpType::IfcPumpType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPumpType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcQuantityArea
IfcAreaMeasure IfcQuantityArea::AreaValue() { return *entity->getArgument(3); }
bool IfcQuantityArea::is(Type::Enum v) const { return v == Type::IfcQuantityArea || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityArea::type() const { return Type::IfcQuantityArea; }
Type::Enum IfcQuantityArea::Class() { return Type::IfcQuantityArea; }
IfcQuantityArea::IfcQuantityArea(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityArea)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcQuantityCount
IfcCountMeasure IfcQuantityCount::CountValue() { return *entity->getArgument(3); }
bool IfcQuantityCount::is(Type::Enum v) const { return v == Type::IfcQuantityCount || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityCount::type() const { return Type::IfcQuantityCount; }
Type::Enum IfcQuantityCount::Class() { return Type::IfcQuantityCount; }
IfcQuantityCount::IfcQuantityCount(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityCount)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcQuantityLength
IfcLengthMeasure IfcQuantityLength::LengthValue() { return *entity->getArgument(3); }
bool IfcQuantityLength::is(Type::Enum v) const { return v == Type::IfcQuantityLength || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityLength::type() const { return Type::IfcQuantityLength; }
Type::Enum IfcQuantityLength::Class() { return Type::IfcQuantityLength; }
IfcQuantityLength::IfcQuantityLength(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityLength)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcQuantityTime
IfcTimeMeasure IfcQuantityTime::TimeValue() { return *entity->getArgument(3); }
bool IfcQuantityTime::is(Type::Enum v) const { return v == Type::IfcQuantityTime || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityTime::type() const { return Type::IfcQuantityTime; }
Type::Enum IfcQuantityTime::Class() { return Type::IfcQuantityTime; }
IfcQuantityTime::IfcQuantityTime(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityTime)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcQuantityVolume
IfcVolumeMeasure IfcQuantityVolume::VolumeValue() { return *entity->getArgument(3); }
bool IfcQuantityVolume::is(Type::Enum v) const { return v == Type::IfcQuantityVolume || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityVolume::type() const { return Type::IfcQuantityVolume; }
Type::Enum IfcQuantityVolume::Class() { return Type::IfcQuantityVolume; }
IfcQuantityVolume::IfcQuantityVolume(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityVolume)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcQuantityWeight
IfcMassMeasure IfcQuantityWeight::WeightValue() { return *entity->getArgument(3); }
bool IfcQuantityWeight::is(Type::Enum v) const { return v == Type::IfcQuantityWeight || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityWeight::type() const { return Type::IfcQuantityWeight; }
Type::Enum IfcQuantityWeight::Class() { return Type::IfcQuantityWeight; }
IfcQuantityWeight::IfcQuantityWeight(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityWeight)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRadiusDimension
bool IfcRadiusDimension::is(Type::Enum v) const { return v == Type::IfcRadiusDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcRadiusDimension::type() const { return Type::IfcRadiusDimension; }
Type::Enum IfcRadiusDimension::Class() { return Type::IfcRadiusDimension; }
IfcRadiusDimension::IfcRadiusDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcRadiusDimension)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRailing
bool IfcRailing::hasPredefinedType() { return !entity->getArgument(8)->isNull(); }
IfcRailingTypeEnum::IfcRailingTypeEnum IfcRailing::PredefinedType() { return IfcRailingTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcRailing::is(Type::Enum v) const { return v == Type::IfcRailing || IfcBuildingElement::is(v); }
Type::Enum IfcRailing::type() const { return Type::IfcRailing; }
Type::Enum IfcRailing::Class() { return Type::IfcRailing; }
IfcRailing::IfcRailing(IfcAbstractEntityPtr e) { if (!is(Type::IfcRailing)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRailingType
IfcRailingTypeEnum::IfcRailingTypeEnum IfcRailingType::PredefinedType() { return IfcRailingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcRailingType::is(Type::Enum v) const { return v == Type::IfcRailingType || IfcBuildingElementType::is(v); }
Type::Enum IfcRailingType::type() const { return Type::IfcRailingType; }
Type::Enum IfcRailingType::Class() { return Type::IfcRailingType; }
IfcRailingType::IfcRailingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcRailingType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRamp
IfcRampTypeEnum::IfcRampTypeEnum IfcRamp::ShapeType() { return IfcRampTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcRamp::is(Type::Enum v) const { return v == Type::IfcRamp || IfcBuildingElement::is(v); }
Type::Enum IfcRamp::type() const { return Type::IfcRamp; }
Type::Enum IfcRamp::Class() { return Type::IfcRamp; }
IfcRamp::IfcRamp(IfcAbstractEntityPtr e) { if (!is(Type::IfcRamp)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRampFlight
bool IfcRampFlight::is(Type::Enum v) const { return v == Type::IfcRampFlight || IfcBuildingElement::is(v); }
Type::Enum IfcRampFlight::type() const { return Type::IfcRampFlight; }
Type::Enum IfcRampFlight::Class() { return Type::IfcRampFlight; }
IfcRampFlight::IfcRampFlight(IfcAbstractEntityPtr e) { if (!is(Type::IfcRampFlight)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRampFlightType
IfcRampFlightTypeEnum::IfcRampFlightTypeEnum IfcRampFlightType::PredefinedType() { return IfcRampFlightTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcRampFlightType::is(Type::Enum v) const { return v == Type::IfcRampFlightType || IfcBuildingElementType::is(v); }
Type::Enum IfcRampFlightType::type() const { return Type::IfcRampFlightType; }
Type::Enum IfcRampFlightType::Class() { return Type::IfcRampFlightType; }
IfcRampFlightType::IfcRampFlightType(IfcAbstractEntityPtr e) { if (!is(Type::IfcRampFlightType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRationalBezierCurve
std::vector<double> /*[2:?]*/ IfcRationalBezierCurve::WeightsData() { return *entity->getArgument(5); }
bool IfcRationalBezierCurve::is(Type::Enum v) const { return v == Type::IfcRationalBezierCurve || IfcBezierCurve::is(v); }
Type::Enum IfcRationalBezierCurve::type() const { return Type::IfcRationalBezierCurve; }
Type::Enum IfcRationalBezierCurve::Class() { return Type::IfcRationalBezierCurve; }
IfcRationalBezierCurve::IfcRationalBezierCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcRationalBezierCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRectangleHollowProfileDef
IfcPositiveLengthMeasure IfcRectangleHollowProfileDef::WallThickness() { return *entity->getArgument(5); }
bool IfcRectangleHollowProfileDef::hasInnerFilletRadius() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcRectangleHollowProfileDef::InnerFilletRadius() { return *entity->getArgument(6); }
bool IfcRectangleHollowProfileDef::hasOuterFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcRectangleHollowProfileDef::OuterFilletRadius() { return *entity->getArgument(7); }
bool IfcRectangleHollowProfileDef::is(Type::Enum v) const { return v == Type::IfcRectangleHollowProfileDef || IfcRectangleProfileDef::is(v); }
Type::Enum IfcRectangleHollowProfileDef::type() const { return Type::IfcRectangleHollowProfileDef; }
Type::Enum IfcRectangleHollowProfileDef::Class() { return Type::IfcRectangleHollowProfileDef; }
IfcRectangleHollowProfileDef::IfcRectangleHollowProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangleHollowProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRectangleProfileDef
IfcPositiveLengthMeasure IfcRectangleProfileDef::XDim() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcRectangleProfileDef::YDim() { return *entity->getArgument(4); }
bool IfcRectangleProfileDef::is(Type::Enum v) const { return v == Type::IfcRectangleProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcRectangleProfileDef::type() const { return Type::IfcRectangleProfileDef; }
Type::Enum IfcRectangleProfileDef::Class() { return Type::IfcRectangleProfileDef; }
IfcRectangleProfileDef::IfcRectangleProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangleProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRectangularPyramid
IfcPositiveLengthMeasure IfcRectangularPyramid::XLength() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcRectangularPyramid::YLength() { return *entity->getArgument(2); }
IfcPositiveLengthMeasure IfcRectangularPyramid::Height() { return *entity->getArgument(3); }
bool IfcRectangularPyramid::is(Type::Enum v) const { return v == Type::IfcRectangularPyramid || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcRectangularPyramid::type() const { return Type::IfcRectangularPyramid; }
Type::Enum IfcRectangularPyramid::Class() { return Type::IfcRectangularPyramid; }
IfcRectangularPyramid::IfcRectangularPyramid(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangularPyramid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRectangularTrimmedSurface
IfcSurface* IfcRectangularTrimmedSurface::BasisSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(0)); }
IfcParameterValue IfcRectangularTrimmedSurface::U1() { return *entity->getArgument(1); }
IfcParameterValue IfcRectangularTrimmedSurface::V1() { return *entity->getArgument(2); }
IfcParameterValue IfcRectangularTrimmedSurface::U2() { return *entity->getArgument(3); }
IfcParameterValue IfcRectangularTrimmedSurface::V2() { return *entity->getArgument(4); }
bool IfcRectangularTrimmedSurface::Usense() { return *entity->getArgument(5); }
bool IfcRectangularTrimmedSurface::Vsense() { return *entity->getArgument(6); }
bool IfcRectangularTrimmedSurface::is(Type::Enum v) const { return v == Type::IfcRectangularTrimmedSurface || IfcBoundedSurface::is(v); }
Type::Enum IfcRectangularTrimmedSurface::type() const { return Type::IfcRectangularTrimmedSurface; }
Type::Enum IfcRectangularTrimmedSurface::Class() { return Type::IfcRectangularTrimmedSurface; }
IfcRectangularTrimmedSurface::IfcRectangularTrimmedSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangularTrimmedSurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcReferencesValueDocument
IfcDocumentSelect IfcReferencesValueDocument::ReferencedDocument() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > IfcReferencesValueDocument::ReferencingValues() { RETURN_AS_LIST(IfcAppliedValue,1) }
bool IfcReferencesValueDocument::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcReferencesValueDocument::Name() { return *entity->getArgument(2); }
bool IfcReferencesValueDocument::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcReferencesValueDocument::Description() { return *entity->getArgument(3); }
bool IfcReferencesValueDocument::is(Type::Enum v) const { return v == Type::IfcReferencesValueDocument; }
Type::Enum IfcReferencesValueDocument::type() const { return Type::IfcReferencesValueDocument; }
Type::Enum IfcReferencesValueDocument::Class() { return Type::IfcReferencesValueDocument; }
IfcReferencesValueDocument::IfcReferencesValueDocument(IfcAbstractEntityPtr e) { if (!is(Type::IfcReferencesValueDocument)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRegularTimeSeries
IfcTimeMeasure IfcRegularTimeSeries::TimeStep() { return *entity->getArgument(8); }
SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesValue> > IfcRegularTimeSeries::Values() { RETURN_AS_LIST(IfcTimeSeriesValue,9) }
bool IfcRegularTimeSeries::is(Type::Enum v) const { return v == Type::IfcRegularTimeSeries || IfcTimeSeries::is(v); }
Type::Enum IfcRegularTimeSeries::type() const { return Type::IfcRegularTimeSeries; }
Type::Enum IfcRegularTimeSeries::Class() { return Type::IfcRegularTimeSeries; }
IfcRegularTimeSeries::IfcRegularTimeSeries(IfcAbstractEntityPtr e) { if (!is(Type::IfcRegularTimeSeries)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcReinforcementBarProperties
IfcAreaMeasure IfcReinforcementBarProperties::TotalCrossSectionArea() { return *entity->getArgument(0); }
IfcLabel IfcReinforcementBarProperties::SteelGrade() { return *entity->getArgument(1); }
bool IfcReinforcementBarProperties::hasBarSurface() { return !entity->getArgument(2)->isNull(); }
IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum IfcReinforcementBarProperties::BarSurface() { return IfcReinforcingBarSurfaceEnum::FromString(*entity->getArgument(2)); }
bool IfcReinforcementBarProperties::hasEffectiveDepth() { return !entity->getArgument(3)->isNull(); }
IfcLengthMeasure IfcReinforcementBarProperties::EffectiveDepth() { return *entity->getArgument(3); }
bool IfcReinforcementBarProperties::hasNominalBarDiameter() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcReinforcementBarProperties::NominalBarDiameter() { return *entity->getArgument(4); }
bool IfcReinforcementBarProperties::hasBarCount() { return !entity->getArgument(5)->isNull(); }
IfcCountMeasure IfcReinforcementBarProperties::BarCount() { return *entity->getArgument(5); }
bool IfcReinforcementBarProperties::is(Type::Enum v) const { return v == Type::IfcReinforcementBarProperties; }
Type::Enum IfcReinforcementBarProperties::type() const { return Type::IfcReinforcementBarProperties; }
Type::Enum IfcReinforcementBarProperties::Class() { return Type::IfcReinforcementBarProperties; }
IfcReinforcementBarProperties::IfcReinforcementBarProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcementBarProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcReinforcementDefinitionProperties
bool IfcReinforcementDefinitionProperties::hasDefinitionType() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcReinforcementDefinitionProperties::DefinitionType() { return *entity->getArgument(4); }
SHARED_PTR< IfcTemplatedEntityList<IfcSectionReinforcementProperties> > IfcReinforcementDefinitionProperties::ReinforcementSectionDefinitions() { RETURN_AS_LIST(IfcSectionReinforcementProperties,5) }
bool IfcReinforcementDefinitionProperties::is(Type::Enum v) const { return v == Type::IfcReinforcementDefinitionProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcReinforcementDefinitionProperties::type() const { return Type::IfcReinforcementDefinitionProperties; }
Type::Enum IfcReinforcementDefinitionProperties::Class() { return Type::IfcReinforcementDefinitionProperties; }
IfcReinforcementDefinitionProperties::IfcReinforcementDefinitionProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcementDefinitionProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcReinforcingBar
IfcPositiveLengthMeasure IfcReinforcingBar::NominalDiameter() { return *entity->getArgument(9); }
IfcAreaMeasure IfcReinforcingBar::CrossSectionArea() { return *entity->getArgument(10); }
bool IfcReinforcingBar::hasBarLength() { return !entity->getArgument(11)->isNull(); }
IfcPositiveLengthMeasure IfcReinforcingBar::BarLength() { return *entity->getArgument(11); }
IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum IfcReinforcingBar::BarRole() { return IfcReinforcingBarRoleEnum::FromString(*entity->getArgument(12)); }
bool IfcReinforcingBar::hasBarSurface() { return !entity->getArgument(13)->isNull(); }
IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum IfcReinforcingBar::BarSurface() { return IfcReinforcingBarSurfaceEnum::FromString(*entity->getArgument(13)); }
bool IfcReinforcingBar::is(Type::Enum v) const { return v == Type::IfcReinforcingBar || IfcReinforcingElement::is(v); }
Type::Enum IfcReinforcingBar::type() const { return Type::IfcReinforcingBar; }
Type::Enum IfcReinforcingBar::Class() { return Type::IfcReinforcingBar; }
IfcReinforcingBar::IfcReinforcingBar(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcingBar)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcReinforcingElement
bool IfcReinforcingElement::hasSteelGrade() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcReinforcingElement::SteelGrade() { return *entity->getArgument(8); }
bool IfcReinforcingElement::is(Type::Enum v) const { return v == Type::IfcReinforcingElement || IfcBuildingElementComponent::is(v); }
Type::Enum IfcReinforcingElement::type() const { return Type::IfcReinforcingElement; }
Type::Enum IfcReinforcingElement::Class() { return Type::IfcReinforcingElement; }
IfcReinforcingElement::IfcReinforcingElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcingElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcReinforcingMesh
bool IfcReinforcingMesh::hasMeshLength() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcReinforcingMesh::MeshLength() { return *entity->getArgument(9); }
bool IfcReinforcingMesh::hasMeshWidth() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcReinforcingMesh::MeshWidth() { return *entity->getArgument(10); }
IfcPositiveLengthMeasure IfcReinforcingMesh::LongitudinalBarNominalDiameter() { return *entity->getArgument(11); }
IfcPositiveLengthMeasure IfcReinforcingMesh::TransverseBarNominalDiameter() { return *entity->getArgument(12); }
IfcAreaMeasure IfcReinforcingMesh::LongitudinalBarCrossSectionArea() { return *entity->getArgument(13); }
IfcAreaMeasure IfcReinforcingMesh::TransverseBarCrossSectionArea() { return *entity->getArgument(14); }
IfcPositiveLengthMeasure IfcReinforcingMesh::LongitudinalBarSpacing() { return *entity->getArgument(15); }
IfcPositiveLengthMeasure IfcReinforcingMesh::TransverseBarSpacing() { return *entity->getArgument(16); }
bool IfcReinforcingMesh::is(Type::Enum v) const { return v == Type::IfcReinforcingMesh || IfcReinforcingElement::is(v); }
Type::Enum IfcReinforcingMesh::type() const { return Type::IfcReinforcingMesh; }
Type::Enum IfcReinforcingMesh::Class() { return Type::IfcReinforcingMesh; }
IfcReinforcingMesh::IfcReinforcingMesh(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcingMesh)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAggregates
bool IfcRelAggregates::is(Type::Enum v) const { return v == Type::IfcRelAggregates || IfcRelDecomposes::is(v); }
Type::Enum IfcRelAggregates::type() const { return Type::IfcRelAggregates; }
Type::Enum IfcRelAggregates::Class() { return Type::IfcRelAggregates; }
IfcRelAggregates::IfcRelAggregates(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAggregates)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssigns
SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > IfcRelAssigns::RelatedObjects() { RETURN_AS_LIST(IfcObjectDefinition,4) }
bool IfcRelAssigns::hasRelatedObjectsType() { return !entity->getArgument(5)->isNull(); }
IfcObjectTypeEnum::IfcObjectTypeEnum IfcRelAssigns::RelatedObjectsType() { return IfcObjectTypeEnum::FromString(*entity->getArgument(5)); }
bool IfcRelAssigns::is(Type::Enum v) const { return v == Type::IfcRelAssigns || IfcRelationship::is(v); }
Type::Enum IfcRelAssigns::type() const { return Type::IfcRelAssigns; }
Type::Enum IfcRelAssigns::Class() { return Type::IfcRelAssigns; }
IfcRelAssigns::IfcRelAssigns(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssigns)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsTasks
bool IfcRelAssignsTasks::hasTimeForTask() { return !entity->getArgument(7)->isNull(); }
IfcScheduleTimeControl* IfcRelAssignsTasks::TimeForTask() { return reinterpret_pointer_cast<IfcBaseClass,IfcScheduleTimeControl>(*entity->getArgument(7)); }
bool IfcRelAssignsTasks::is(Type::Enum v) const { return v == Type::IfcRelAssignsTasks || IfcRelAssignsToControl::is(v); }
Type::Enum IfcRelAssignsTasks::type() const { return Type::IfcRelAssignsTasks; }
Type::Enum IfcRelAssignsTasks::Class() { return Type::IfcRelAssignsTasks; }
IfcRelAssignsTasks::IfcRelAssignsTasks(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsTasks)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsToActor
IfcActor* IfcRelAssignsToActor::RelatingActor() { return reinterpret_pointer_cast<IfcBaseClass,IfcActor>(*entity->getArgument(6)); }
bool IfcRelAssignsToActor::hasActingRole() { return !entity->getArgument(7)->isNull(); }
IfcActorRole* IfcRelAssignsToActor::ActingRole() { return reinterpret_pointer_cast<IfcBaseClass,IfcActorRole>(*entity->getArgument(7)); }
bool IfcRelAssignsToActor::is(Type::Enum v) const { return v == Type::IfcRelAssignsToActor || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToActor::type() const { return Type::IfcRelAssignsToActor; }
Type::Enum IfcRelAssignsToActor::Class() { return Type::IfcRelAssignsToActor; }
IfcRelAssignsToActor::IfcRelAssignsToActor(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToActor)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsToControl
IfcControl* IfcRelAssignsToControl::RelatingControl() { return reinterpret_pointer_cast<IfcBaseClass,IfcControl>(*entity->getArgument(6)); }
bool IfcRelAssignsToControl::is(Type::Enum v) const { return v == Type::IfcRelAssignsToControl || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToControl::type() const { return Type::IfcRelAssignsToControl; }
Type::Enum IfcRelAssignsToControl::Class() { return Type::IfcRelAssignsToControl; }
IfcRelAssignsToControl::IfcRelAssignsToControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToControl)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsToGroup
IfcGroup* IfcRelAssignsToGroup::RelatingGroup() { return reinterpret_pointer_cast<IfcBaseClass,IfcGroup>(*entity->getArgument(6)); }
bool IfcRelAssignsToGroup::is(Type::Enum v) const { return v == Type::IfcRelAssignsToGroup || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToGroup::type() const { return Type::IfcRelAssignsToGroup; }
Type::Enum IfcRelAssignsToGroup::Class() { return Type::IfcRelAssignsToGroup; }
IfcRelAssignsToGroup::IfcRelAssignsToGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToGroup)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsToProcess
IfcProcess* IfcRelAssignsToProcess::RelatingProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcProcess>(*entity->getArgument(6)); }
bool IfcRelAssignsToProcess::hasQuantityInProcess() { return !entity->getArgument(7)->isNull(); }
IfcMeasureWithUnit* IfcRelAssignsToProcess::QuantityInProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(7)); }
bool IfcRelAssignsToProcess::is(Type::Enum v) const { return v == Type::IfcRelAssignsToProcess || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToProcess::type() const { return Type::IfcRelAssignsToProcess; }
Type::Enum IfcRelAssignsToProcess::Class() { return Type::IfcRelAssignsToProcess; }
IfcRelAssignsToProcess::IfcRelAssignsToProcess(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToProcess)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsToProduct
IfcProduct* IfcRelAssignsToProduct::RelatingProduct() { return reinterpret_pointer_cast<IfcBaseClass,IfcProduct>(*entity->getArgument(6)); }
bool IfcRelAssignsToProduct::is(Type::Enum v) const { return v == Type::IfcRelAssignsToProduct || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToProduct::type() const { return Type::IfcRelAssignsToProduct; }
Type::Enum IfcRelAssignsToProduct::Class() { return Type::IfcRelAssignsToProduct; }
IfcRelAssignsToProduct::IfcRelAssignsToProduct(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToProduct)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsToProjectOrder
bool IfcRelAssignsToProjectOrder::is(Type::Enum v) const { return v == Type::IfcRelAssignsToProjectOrder || IfcRelAssignsToControl::is(v); }
Type::Enum IfcRelAssignsToProjectOrder::type() const { return Type::IfcRelAssignsToProjectOrder; }
Type::Enum IfcRelAssignsToProjectOrder::Class() { return Type::IfcRelAssignsToProjectOrder; }
IfcRelAssignsToProjectOrder::IfcRelAssignsToProjectOrder(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToProjectOrder)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssignsToResource
IfcResource* IfcRelAssignsToResource::RelatingResource() { return reinterpret_pointer_cast<IfcBaseClass,IfcResource>(*entity->getArgument(6)); }
bool IfcRelAssignsToResource::is(Type::Enum v) const { return v == Type::IfcRelAssignsToResource || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToResource::type() const { return Type::IfcRelAssignsToResource; }
Type::Enum IfcRelAssignsToResource::Class() { return Type::IfcRelAssignsToResource; }
IfcRelAssignsToResource::IfcRelAssignsToResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociates
SHARED_PTR< IfcTemplatedEntityList<IfcRoot> > IfcRelAssociates::RelatedObjects() { RETURN_AS_LIST(IfcRoot,4) }
bool IfcRelAssociates::is(Type::Enum v) const { return v == Type::IfcRelAssociates || IfcRelationship::is(v); }
Type::Enum IfcRelAssociates::type() const { return Type::IfcRelAssociates; }
Type::Enum IfcRelAssociates::Class() { return Type::IfcRelAssociates; }
IfcRelAssociates::IfcRelAssociates(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociates)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesAppliedValue
IfcAppliedValue* IfcRelAssociatesAppliedValue::RelatingAppliedValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcAppliedValue>(*entity->getArgument(5)); }
bool IfcRelAssociatesAppliedValue::is(Type::Enum v) const { return v == Type::IfcRelAssociatesAppliedValue || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesAppliedValue::type() const { return Type::IfcRelAssociatesAppliedValue; }
Type::Enum IfcRelAssociatesAppliedValue::Class() { return Type::IfcRelAssociatesAppliedValue; }
IfcRelAssociatesAppliedValue::IfcRelAssociatesAppliedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesAppliedValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesApproval
IfcApproval* IfcRelAssociatesApproval::RelatingApproval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(5)); }
bool IfcRelAssociatesApproval::is(Type::Enum v) const { return v == Type::IfcRelAssociatesApproval || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesApproval::type() const { return Type::IfcRelAssociatesApproval; }
Type::Enum IfcRelAssociatesApproval::Class() { return Type::IfcRelAssociatesApproval; }
IfcRelAssociatesApproval::IfcRelAssociatesApproval(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesApproval)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesClassification
IfcClassificationNotationSelect IfcRelAssociatesClassification::RelatingClassification() { return *entity->getArgument(5); }
bool IfcRelAssociatesClassification::is(Type::Enum v) const { return v == Type::IfcRelAssociatesClassification || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesClassification::type() const { return Type::IfcRelAssociatesClassification; }
Type::Enum IfcRelAssociatesClassification::Class() { return Type::IfcRelAssociatesClassification; }
IfcRelAssociatesClassification::IfcRelAssociatesClassification(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesClassification)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesConstraint
IfcLabel IfcRelAssociatesConstraint::Intent() { return *entity->getArgument(5); }
IfcConstraint* IfcRelAssociatesConstraint::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(6)); }
bool IfcRelAssociatesConstraint::is(Type::Enum v) const { return v == Type::IfcRelAssociatesConstraint || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesConstraint::type() const { return Type::IfcRelAssociatesConstraint; }
Type::Enum IfcRelAssociatesConstraint::Class() { return Type::IfcRelAssociatesConstraint; }
IfcRelAssociatesConstraint::IfcRelAssociatesConstraint(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesConstraint)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesDocument
IfcDocumentSelect IfcRelAssociatesDocument::RelatingDocument() { return *entity->getArgument(5); }
bool IfcRelAssociatesDocument::is(Type::Enum v) const { return v == Type::IfcRelAssociatesDocument || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesDocument::type() const { return Type::IfcRelAssociatesDocument; }
Type::Enum IfcRelAssociatesDocument::Class() { return Type::IfcRelAssociatesDocument; }
IfcRelAssociatesDocument::IfcRelAssociatesDocument(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesDocument)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesLibrary
IfcLibrarySelect IfcRelAssociatesLibrary::RelatingLibrary() { return *entity->getArgument(5); }
bool IfcRelAssociatesLibrary::is(Type::Enum v) const { return v == Type::IfcRelAssociatesLibrary || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesLibrary::type() const { return Type::IfcRelAssociatesLibrary; }
Type::Enum IfcRelAssociatesLibrary::Class() { return Type::IfcRelAssociatesLibrary; }
IfcRelAssociatesLibrary::IfcRelAssociatesLibrary(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesLibrary)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesMaterial
IfcMaterialSelect IfcRelAssociatesMaterial::RelatingMaterial() { return *entity->getArgument(5); }
bool IfcRelAssociatesMaterial::is(Type::Enum v) const { return v == Type::IfcRelAssociatesMaterial || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesMaterial::type() const { return Type::IfcRelAssociatesMaterial; }
Type::Enum IfcRelAssociatesMaterial::Class() { return Type::IfcRelAssociatesMaterial; }
IfcRelAssociatesMaterial::IfcRelAssociatesMaterial(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesMaterial)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelAssociatesProfileProperties
IfcProfileProperties* IfcRelAssociatesProfileProperties::RelatingProfileProperties() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileProperties>(*entity->getArgument(5)); }
bool IfcRelAssociatesProfileProperties::hasProfileSectionLocation() { return !entity->getArgument(6)->isNull(); }
IfcShapeAspect* IfcRelAssociatesProfileProperties::ProfileSectionLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(6)); }
bool IfcRelAssociatesProfileProperties::hasProfileOrientation() { return !entity->getArgument(7)->isNull(); }
IfcOrientationSelect IfcRelAssociatesProfileProperties::ProfileOrientation() { return *entity->getArgument(7); }
bool IfcRelAssociatesProfileProperties::is(Type::Enum v) const { return v == Type::IfcRelAssociatesProfileProperties || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesProfileProperties::type() const { return Type::IfcRelAssociatesProfileProperties; }
Type::Enum IfcRelAssociatesProfileProperties::Class() { return Type::IfcRelAssociatesProfileProperties; }
IfcRelAssociatesProfileProperties::IfcRelAssociatesProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesProfileProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnects
bool IfcRelConnects::is(Type::Enum v) const { return v == Type::IfcRelConnects || IfcRelationship::is(v); }
Type::Enum IfcRelConnects::type() const { return Type::IfcRelConnects; }
Type::Enum IfcRelConnects::Class() { return Type::IfcRelConnects; }
IfcRelConnects::IfcRelConnects(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnects)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsElements
bool IfcRelConnectsElements::hasConnectionGeometry() { return !entity->getArgument(4)->isNull(); }
IfcConnectionGeometry* IfcRelConnectsElements::ConnectionGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcConnectionGeometry>(*entity->getArgument(4)); }
IfcElement* IfcRelConnectsElements::RelatingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
IfcElement* IfcRelConnectsElements::RelatedElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(6)); }
bool IfcRelConnectsElements::is(Type::Enum v) const { return v == Type::IfcRelConnectsElements || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsElements::type() const { return Type::IfcRelConnectsElements; }
Type::Enum IfcRelConnectsElements::Class() { return Type::IfcRelConnectsElements; }
IfcRelConnectsElements::IfcRelConnectsElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsElements)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsPathElements
std::vector<int> /*[0:?]*/ IfcRelConnectsPathElements::RelatingPriorities() { return *entity->getArgument(7); }
std::vector<int> /*[0:?]*/ IfcRelConnectsPathElements::RelatedPriorities() { return *entity->getArgument(8); }
IfcConnectionTypeEnum::IfcConnectionTypeEnum IfcRelConnectsPathElements::RelatedConnectionType() { return IfcConnectionTypeEnum::FromString(*entity->getArgument(9)); }
IfcConnectionTypeEnum::IfcConnectionTypeEnum IfcRelConnectsPathElements::RelatingConnectionType() { return IfcConnectionTypeEnum::FromString(*entity->getArgument(10)); }
bool IfcRelConnectsPathElements::is(Type::Enum v) const { return v == Type::IfcRelConnectsPathElements || IfcRelConnectsElements::is(v); }
Type::Enum IfcRelConnectsPathElements::type() const { return Type::IfcRelConnectsPathElements; }
Type::Enum IfcRelConnectsPathElements::Class() { return Type::IfcRelConnectsPathElements; }
IfcRelConnectsPathElements::IfcRelConnectsPathElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsPathElements)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsPortToElement
IfcPort* IfcRelConnectsPortToElement::RelatingPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcPort>(*entity->getArgument(4)); }
IfcElement* IfcRelConnectsPortToElement::RelatedElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
bool IfcRelConnectsPortToElement::is(Type::Enum v) const { return v == Type::IfcRelConnectsPortToElement || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsPortToElement::type() const { return Type::IfcRelConnectsPortToElement; }
Type::Enum IfcRelConnectsPortToElement::Class() { return Type::IfcRelConnectsPortToElement; }
IfcRelConnectsPortToElement::IfcRelConnectsPortToElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsPortToElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsPorts
IfcPort* IfcRelConnectsPorts::RelatingPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcPort>(*entity->getArgument(4)); }
IfcPort* IfcRelConnectsPorts::RelatedPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcPort>(*entity->getArgument(5)); }
bool IfcRelConnectsPorts::hasRealizingElement() { return !entity->getArgument(6)->isNull(); }
IfcElement* IfcRelConnectsPorts::RealizingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(6)); }
bool IfcRelConnectsPorts::is(Type::Enum v) const { return v == Type::IfcRelConnectsPorts || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsPorts::type() const { return Type::IfcRelConnectsPorts; }
Type::Enum IfcRelConnectsPorts::Class() { return Type::IfcRelConnectsPorts; }
IfcRelConnectsPorts::IfcRelConnectsPorts(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsPorts)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsStructuralActivity
IfcStructuralActivityAssignmentSelect IfcRelConnectsStructuralActivity::RelatingElement() { return *entity->getArgument(4); }
IfcStructuralActivity* IfcRelConnectsStructuralActivity::RelatedStructuralActivity() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralActivity>(*entity->getArgument(5)); }
bool IfcRelConnectsStructuralActivity::is(Type::Enum v) const { return v == Type::IfcRelConnectsStructuralActivity || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsStructuralActivity::type() const { return Type::IfcRelConnectsStructuralActivity; }
Type::Enum IfcRelConnectsStructuralActivity::Class() { return Type::IfcRelConnectsStructuralActivity; }
IfcRelConnectsStructuralActivity::IfcRelConnectsStructuralActivity(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsStructuralActivity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsStructuralElement
IfcElement* IfcRelConnectsStructuralElement::RelatingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
IfcStructuralMember* IfcRelConnectsStructuralElement::RelatedStructuralMember() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralMember>(*entity->getArgument(5)); }
bool IfcRelConnectsStructuralElement::is(Type::Enum v) const { return v == Type::IfcRelConnectsStructuralElement || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsStructuralElement::type() const { return Type::IfcRelConnectsStructuralElement; }
Type::Enum IfcRelConnectsStructuralElement::Class() { return Type::IfcRelConnectsStructuralElement; }
IfcRelConnectsStructuralElement::IfcRelConnectsStructuralElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsStructuralElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsStructuralMember
IfcStructuralMember* IfcRelConnectsStructuralMember::RelatingStructuralMember() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralMember>(*entity->getArgument(4)); }
IfcStructuralConnection* IfcRelConnectsStructuralMember::RelatedStructuralConnection() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralConnection>(*entity->getArgument(5)); }
bool IfcRelConnectsStructuralMember::hasAppliedCondition() { return !entity->getArgument(6)->isNull(); }
IfcBoundaryCondition* IfcRelConnectsStructuralMember::AppliedCondition() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundaryCondition>(*entity->getArgument(6)); }
bool IfcRelConnectsStructuralMember::hasAdditionalConditions() { return !entity->getArgument(7)->isNull(); }
IfcStructuralConnectionCondition* IfcRelConnectsStructuralMember::AdditionalConditions() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralConnectionCondition>(*entity->getArgument(7)); }
bool IfcRelConnectsStructuralMember::hasSupportedLength() { return !entity->getArgument(8)->isNull(); }
IfcLengthMeasure IfcRelConnectsStructuralMember::SupportedLength() { return *entity->getArgument(8); }
bool IfcRelConnectsStructuralMember::hasConditionCoordinateSystem() { return !entity->getArgument(9)->isNull(); }
IfcAxis2Placement3D* IfcRelConnectsStructuralMember::ConditionCoordinateSystem() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(9)); }
bool IfcRelConnectsStructuralMember::is(Type::Enum v) const { return v == Type::IfcRelConnectsStructuralMember || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsStructuralMember::type() const { return Type::IfcRelConnectsStructuralMember; }
Type::Enum IfcRelConnectsStructuralMember::Class() { return Type::IfcRelConnectsStructuralMember; }
IfcRelConnectsStructuralMember::IfcRelConnectsStructuralMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsStructuralMember)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsWithEccentricity
IfcConnectionGeometry* IfcRelConnectsWithEccentricity::ConnectionConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConnectionGeometry>(*entity->getArgument(10)); }
bool IfcRelConnectsWithEccentricity::is(Type::Enum v) const { return v == Type::IfcRelConnectsWithEccentricity || IfcRelConnectsStructuralMember::is(v); }
Type::Enum IfcRelConnectsWithEccentricity::type() const { return Type::IfcRelConnectsWithEccentricity; }
Type::Enum IfcRelConnectsWithEccentricity::Class() { return Type::IfcRelConnectsWithEccentricity; }
IfcRelConnectsWithEccentricity::IfcRelConnectsWithEccentricity(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsWithEccentricity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelConnectsWithRealizingElements
SHARED_PTR< IfcTemplatedEntityList<IfcElement> > IfcRelConnectsWithRealizingElements::RealizingElements() { RETURN_AS_LIST(IfcElement,7) }
bool IfcRelConnectsWithRealizingElements::hasConnectionType() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcRelConnectsWithRealizingElements::ConnectionType() { return *entity->getArgument(8); }
bool IfcRelConnectsWithRealizingElements::is(Type::Enum v) const { return v == Type::IfcRelConnectsWithRealizingElements || IfcRelConnectsElements::is(v); }
Type::Enum IfcRelConnectsWithRealizingElements::type() const { return Type::IfcRelConnectsWithRealizingElements; }
Type::Enum IfcRelConnectsWithRealizingElements::Class() { return Type::IfcRelConnectsWithRealizingElements; }
IfcRelConnectsWithRealizingElements::IfcRelConnectsWithRealizingElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsWithRealizingElements)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelContainedInSpatialStructure
SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > IfcRelContainedInSpatialStructure::RelatedElements() { RETURN_AS_LIST(IfcProduct,4) }
IfcSpatialStructureElement* IfcRelContainedInSpatialStructure::RelatingStructure() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(5)); }
bool IfcRelContainedInSpatialStructure::is(Type::Enum v) const { return v == Type::IfcRelContainedInSpatialStructure || IfcRelConnects::is(v); }
Type::Enum IfcRelContainedInSpatialStructure::type() const { return Type::IfcRelContainedInSpatialStructure; }
Type::Enum IfcRelContainedInSpatialStructure::Class() { return Type::IfcRelContainedInSpatialStructure; }
IfcRelContainedInSpatialStructure::IfcRelContainedInSpatialStructure(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelContainedInSpatialStructure)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelCoversBldgElements
IfcElement* IfcRelCoversBldgElements::RelatingBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > IfcRelCoversBldgElements::RelatedCoverings() { RETURN_AS_LIST(IfcCovering,5) }
bool IfcRelCoversBldgElements::is(Type::Enum v) const { return v == Type::IfcRelCoversBldgElements || IfcRelConnects::is(v); }
Type::Enum IfcRelCoversBldgElements::type() const { return Type::IfcRelCoversBldgElements; }
Type::Enum IfcRelCoversBldgElements::Class() { return Type::IfcRelCoversBldgElements; }
IfcRelCoversBldgElements::IfcRelCoversBldgElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelCoversBldgElements)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelCoversSpaces
IfcSpace* IfcRelCoversSpaces::RelatedSpace() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpace>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > IfcRelCoversSpaces::RelatedCoverings() { RETURN_AS_LIST(IfcCovering,5) }
bool IfcRelCoversSpaces::is(Type::Enum v) const { return v == Type::IfcRelCoversSpaces || IfcRelConnects::is(v); }
Type::Enum IfcRelCoversSpaces::type() const { return Type::IfcRelCoversSpaces; }
Type::Enum IfcRelCoversSpaces::Class() { return Type::IfcRelCoversSpaces; }
IfcRelCoversSpaces::IfcRelCoversSpaces(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelCoversSpaces)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelDecomposes
IfcObjectDefinition* IfcRelDecomposes::RelatingObject() { return reinterpret_pointer_cast<IfcBaseClass,IfcObjectDefinition>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > IfcRelDecomposes::RelatedObjects() { RETURN_AS_LIST(IfcObjectDefinition,5) }
bool IfcRelDecomposes::is(Type::Enum v) const { return v == Type::IfcRelDecomposes || IfcRelationship::is(v); }
Type::Enum IfcRelDecomposes::type() const { return Type::IfcRelDecomposes; }
Type::Enum IfcRelDecomposes::Class() { return Type::IfcRelDecomposes; }
IfcRelDecomposes::IfcRelDecomposes(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDecomposes)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelDefines
SHARED_PTR< IfcTemplatedEntityList<IfcObject> > IfcRelDefines::RelatedObjects() { RETURN_AS_LIST(IfcObject,4) }
bool IfcRelDefines::is(Type::Enum v) const { return v == Type::IfcRelDefines || IfcRelationship::is(v); }
Type::Enum IfcRelDefines::type() const { return Type::IfcRelDefines; }
Type::Enum IfcRelDefines::Class() { return Type::IfcRelDefines; }
IfcRelDefines::IfcRelDefines(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDefines)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelDefinesByProperties
IfcPropertySetDefinition* IfcRelDefinesByProperties::RelatingPropertyDefinition() { return reinterpret_pointer_cast<IfcBaseClass,IfcPropertySetDefinition>(*entity->getArgument(5)); }
bool IfcRelDefinesByProperties::is(Type::Enum v) const { return v == Type::IfcRelDefinesByProperties || IfcRelDefines::is(v); }
Type::Enum IfcRelDefinesByProperties::type() const { return Type::IfcRelDefinesByProperties; }
Type::Enum IfcRelDefinesByProperties::Class() { return Type::IfcRelDefinesByProperties; }
IfcRelDefinesByProperties::IfcRelDefinesByProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDefinesByProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelDefinesByType
IfcTypeObject* IfcRelDefinesByType::RelatingType() { return reinterpret_pointer_cast<IfcBaseClass,IfcTypeObject>(*entity->getArgument(5)); }
bool IfcRelDefinesByType::is(Type::Enum v) const { return v == Type::IfcRelDefinesByType || IfcRelDefines::is(v); }
Type::Enum IfcRelDefinesByType::type() const { return Type::IfcRelDefinesByType; }
Type::Enum IfcRelDefinesByType::Class() { return Type::IfcRelDefinesByType; }
IfcRelDefinesByType::IfcRelDefinesByType(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDefinesByType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelFillsElement
IfcOpeningElement* IfcRelFillsElement::RelatingOpeningElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcOpeningElement>(*entity->getArgument(4)); }
IfcElement* IfcRelFillsElement::RelatedBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
bool IfcRelFillsElement::is(Type::Enum v) const { return v == Type::IfcRelFillsElement || IfcRelConnects::is(v); }
Type::Enum IfcRelFillsElement::type() const { return Type::IfcRelFillsElement; }
Type::Enum IfcRelFillsElement::Class() { return Type::IfcRelFillsElement; }
IfcRelFillsElement::IfcRelFillsElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelFillsElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelFlowControlElements
SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElement> > IfcRelFlowControlElements::RelatedControlElements() { RETURN_AS_LIST(IfcDistributionControlElement,4) }
IfcDistributionFlowElement* IfcRelFlowControlElements::RelatingFlowElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcDistributionFlowElement>(*entity->getArgument(5)); }
bool IfcRelFlowControlElements::is(Type::Enum v) const { return v == Type::IfcRelFlowControlElements || IfcRelConnects::is(v); }
Type::Enum IfcRelFlowControlElements::type() const { return Type::IfcRelFlowControlElements; }
Type::Enum IfcRelFlowControlElements::Class() { return Type::IfcRelFlowControlElements; }
IfcRelFlowControlElements::IfcRelFlowControlElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelFlowControlElements)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelInteractionRequirements
bool IfcRelInteractionRequirements::hasDailyInteraction() { return !entity->getArgument(4)->isNull(); }
IfcCountMeasure IfcRelInteractionRequirements::DailyInteraction() { return *entity->getArgument(4); }
bool IfcRelInteractionRequirements::hasImportanceRating() { return !entity->getArgument(5)->isNull(); }
IfcNormalisedRatioMeasure IfcRelInteractionRequirements::ImportanceRating() { return *entity->getArgument(5); }
bool IfcRelInteractionRequirements::hasLocationOfInteraction() { return !entity->getArgument(6)->isNull(); }
IfcSpatialStructureElement* IfcRelInteractionRequirements::LocationOfInteraction() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(6)); }
IfcSpaceProgram* IfcRelInteractionRequirements::RelatedSpaceProgram() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpaceProgram>(*entity->getArgument(7)); }
IfcSpaceProgram* IfcRelInteractionRequirements::RelatingSpaceProgram() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpaceProgram>(*entity->getArgument(8)); }
bool IfcRelInteractionRequirements::is(Type::Enum v) const { return v == Type::IfcRelInteractionRequirements || IfcRelConnects::is(v); }
Type::Enum IfcRelInteractionRequirements::type() const { return Type::IfcRelInteractionRequirements; }
Type::Enum IfcRelInteractionRequirements::Class() { return Type::IfcRelInteractionRequirements; }
IfcRelInteractionRequirements::IfcRelInteractionRequirements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelInteractionRequirements)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelNests
bool IfcRelNests::is(Type::Enum v) const { return v == Type::IfcRelNests || IfcRelDecomposes::is(v); }
Type::Enum IfcRelNests::type() const { return Type::IfcRelNests; }
Type::Enum IfcRelNests::Class() { return Type::IfcRelNests; }
IfcRelNests::IfcRelNests(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelNests)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelOccupiesSpaces
bool IfcRelOccupiesSpaces::is(Type::Enum v) const { return v == Type::IfcRelOccupiesSpaces || IfcRelAssignsToActor::is(v); }
Type::Enum IfcRelOccupiesSpaces::type() const { return Type::IfcRelOccupiesSpaces; }
Type::Enum IfcRelOccupiesSpaces::Class() { return Type::IfcRelOccupiesSpaces; }
IfcRelOccupiesSpaces::IfcRelOccupiesSpaces(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelOccupiesSpaces)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelOverridesProperties
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcRelOverridesProperties::OverridingProperties() { RETURN_AS_LIST(IfcProperty,6) }
bool IfcRelOverridesProperties::is(Type::Enum v) const { return v == Type::IfcRelOverridesProperties || IfcRelDefinesByProperties::is(v); }
Type::Enum IfcRelOverridesProperties::type() const { return Type::IfcRelOverridesProperties; }
Type::Enum IfcRelOverridesProperties::Class() { return Type::IfcRelOverridesProperties; }
IfcRelOverridesProperties::IfcRelOverridesProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelOverridesProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelProjectsElement
IfcElement* IfcRelProjectsElement::RelatingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
IfcFeatureElementAddition* IfcRelProjectsElement::RelatedFeatureElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcFeatureElementAddition>(*entity->getArgument(5)); }
bool IfcRelProjectsElement::is(Type::Enum v) const { return v == Type::IfcRelProjectsElement || IfcRelConnects::is(v); }
Type::Enum IfcRelProjectsElement::type() const { return Type::IfcRelProjectsElement; }
Type::Enum IfcRelProjectsElement::Class() { return Type::IfcRelProjectsElement; }
IfcRelProjectsElement::IfcRelProjectsElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelProjectsElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelReferencedInSpatialStructure
SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > IfcRelReferencedInSpatialStructure::RelatedElements() { RETURN_AS_LIST(IfcProduct,4) }
IfcSpatialStructureElement* IfcRelReferencedInSpatialStructure::RelatingStructure() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(5)); }
bool IfcRelReferencedInSpatialStructure::is(Type::Enum v) const { return v == Type::IfcRelReferencedInSpatialStructure || IfcRelConnects::is(v); }
Type::Enum IfcRelReferencedInSpatialStructure::type() const { return Type::IfcRelReferencedInSpatialStructure; }
Type::Enum IfcRelReferencedInSpatialStructure::Class() { return Type::IfcRelReferencedInSpatialStructure; }
IfcRelReferencedInSpatialStructure::IfcRelReferencedInSpatialStructure(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelReferencedInSpatialStructure)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelSchedulesCostItems
bool IfcRelSchedulesCostItems::is(Type::Enum v) const { return v == Type::IfcRelSchedulesCostItems || IfcRelAssignsToControl::is(v); }
Type::Enum IfcRelSchedulesCostItems::type() const { return Type::IfcRelSchedulesCostItems; }
Type::Enum IfcRelSchedulesCostItems::Class() { return Type::IfcRelSchedulesCostItems; }
IfcRelSchedulesCostItems::IfcRelSchedulesCostItems(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelSchedulesCostItems)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelSequence
IfcProcess* IfcRelSequence::RelatingProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcProcess>(*entity->getArgument(4)); }
IfcProcess* IfcRelSequence::RelatedProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcProcess>(*entity->getArgument(5)); }
IfcTimeMeasure IfcRelSequence::TimeLag() { return *entity->getArgument(6); }
IfcSequenceEnum::IfcSequenceEnum IfcRelSequence::SequenceType() { return IfcSequenceEnum::FromString(*entity->getArgument(7)); }
bool IfcRelSequence::is(Type::Enum v) const { return v == Type::IfcRelSequence || IfcRelConnects::is(v); }
Type::Enum IfcRelSequence::type() const { return Type::IfcRelSequence; }
Type::Enum IfcRelSequence::Class() { return Type::IfcRelSequence; }
IfcRelSequence::IfcRelSequence(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelSequence)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelServicesBuildings
IfcSystem* IfcRelServicesBuildings::RelatingSystem() { return reinterpret_pointer_cast<IfcBaseClass,IfcSystem>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElement> > IfcRelServicesBuildings::RelatedBuildings() { RETURN_AS_LIST(IfcSpatialStructureElement,5) }
bool IfcRelServicesBuildings::is(Type::Enum v) const { return v == Type::IfcRelServicesBuildings || IfcRelConnects::is(v); }
Type::Enum IfcRelServicesBuildings::type() const { return Type::IfcRelServicesBuildings; }
Type::Enum IfcRelServicesBuildings::Class() { return Type::IfcRelServicesBuildings; }
IfcRelServicesBuildings::IfcRelServicesBuildings(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelServicesBuildings)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelSpaceBoundary
IfcSpace* IfcRelSpaceBoundary::RelatingSpace() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpace>(*entity->getArgument(4)); }
bool IfcRelSpaceBoundary::hasRelatedBuildingElement() { return !entity->getArgument(5)->isNull(); }
IfcElement* IfcRelSpaceBoundary::RelatedBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
bool IfcRelSpaceBoundary::hasConnectionGeometry() { return !entity->getArgument(6)->isNull(); }
IfcConnectionGeometry* IfcRelSpaceBoundary::ConnectionGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcConnectionGeometry>(*entity->getArgument(6)); }
IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtualEnum IfcRelSpaceBoundary::PhysicalOrVirtualBoundary() { return IfcPhysicalOrVirtualEnum::FromString(*entity->getArgument(7)); }
IfcInternalOrExternalEnum::IfcInternalOrExternalEnum IfcRelSpaceBoundary::InternalOrExternalBoundary() { return IfcInternalOrExternalEnum::FromString(*entity->getArgument(8)); }
bool IfcRelSpaceBoundary::is(Type::Enum v) const { return v == Type::IfcRelSpaceBoundary || IfcRelConnects::is(v); }
Type::Enum IfcRelSpaceBoundary::type() const { return Type::IfcRelSpaceBoundary; }
Type::Enum IfcRelSpaceBoundary::Class() { return Type::IfcRelSpaceBoundary; }
IfcRelSpaceBoundary::IfcRelSpaceBoundary(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelSpaceBoundary)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelVoidsElement
IfcElement* IfcRelVoidsElement::RelatingBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
IfcFeatureElementSubtraction* IfcRelVoidsElement::RelatedOpeningElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcFeatureElementSubtraction>(*entity->getArgument(5)); }
bool IfcRelVoidsElement::is(Type::Enum v) const { return v == Type::IfcRelVoidsElement || IfcRelConnects::is(v); }
Type::Enum IfcRelVoidsElement::type() const { return Type::IfcRelVoidsElement; }
Type::Enum IfcRelVoidsElement::Class() { return Type::IfcRelVoidsElement; }
IfcRelVoidsElement::IfcRelVoidsElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelVoidsElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelationship
bool IfcRelationship::is(Type::Enum v) const { return v == Type::IfcRelationship || IfcRoot::is(v); }
Type::Enum IfcRelationship::type() const { return Type::IfcRelationship; }
Type::Enum IfcRelationship::Class() { return Type::IfcRelationship; }
IfcRelationship::IfcRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRelaxation
IfcNormalisedRatioMeasure IfcRelaxation::RelaxationValue() { return *entity->getArgument(0); }
IfcNormalisedRatioMeasure IfcRelaxation::InitialStress() { return *entity->getArgument(1); }
bool IfcRelaxation::is(Type::Enum v) const { return v == Type::IfcRelaxation; }
Type::Enum IfcRelaxation::type() const { return Type::IfcRelaxation; }
Type::Enum IfcRelaxation::Class() { return Type::IfcRelaxation; }
IfcRelaxation::IfcRelaxation(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelaxation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRepresentation
IfcRepresentationContext* IfcRepresentation::ContextOfItems() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentationContext>(*entity->getArgument(0)); }
bool IfcRepresentation::hasRepresentationIdentifier() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcRepresentation::RepresentationIdentifier() { return *entity->getArgument(1); }
bool IfcRepresentation::hasRepresentationType() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcRepresentation::RepresentationType() { return *entity->getArgument(2); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationItem> > IfcRepresentation::Items() { RETURN_AS_LIST(IfcRepresentationItem,3) }
IfcRepresentationMap::list IfcRepresentation::RepresentationMap() { RETURN_INVERSE(IfcRepresentationMap) }
IfcPresentationLayerAssignment::list IfcRepresentation::LayerAssignments() { RETURN_INVERSE(IfcPresentationLayerAssignment) }
IfcProductRepresentation::list IfcRepresentation::OfProductRepresentation() { RETURN_INVERSE(IfcProductRepresentation) }
bool IfcRepresentation::is(Type::Enum v) const { return v == Type::IfcRepresentation; }
Type::Enum IfcRepresentation::type() const { return Type::IfcRepresentation; }
Type::Enum IfcRepresentation::Class() { return Type::IfcRepresentation; }
IfcRepresentation::IfcRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRepresentationContext
bool IfcRepresentationContext::hasContextIdentifier() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcRepresentationContext::ContextIdentifier() { return *entity->getArgument(0); }
bool IfcRepresentationContext::hasContextType() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcRepresentationContext::ContextType() { return *entity->getArgument(1); }
IfcRepresentation::list IfcRepresentationContext::RepresentationsInContext() { RETURN_INVERSE(IfcRepresentation) }
bool IfcRepresentationContext::is(Type::Enum v) const { return v == Type::IfcRepresentationContext; }
Type::Enum IfcRepresentationContext::type() const { return Type::IfcRepresentationContext; }
Type::Enum IfcRepresentationContext::Class() { return Type::IfcRepresentationContext; }
IfcRepresentationContext::IfcRepresentationContext(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentationContext)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRepresentationItem
IfcPresentationLayerAssignment::list IfcRepresentationItem::LayerAssignments() { RETURN_INVERSE(IfcPresentationLayerAssignment) }
IfcStyledItem::list IfcRepresentationItem::StyledByItem() { RETURN_INVERSE(IfcStyledItem) }
bool IfcRepresentationItem::is(Type::Enum v) const { return v == Type::IfcRepresentationItem; }
Type::Enum IfcRepresentationItem::type() const { return Type::IfcRepresentationItem; }
Type::Enum IfcRepresentationItem::Class() { return Type::IfcRepresentationItem; }
IfcRepresentationItem::IfcRepresentationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentationItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRepresentationMap
IfcAxis2Placement IfcRepresentationMap::MappingOrigin() { return *entity->getArgument(0); }
IfcRepresentation* IfcRepresentationMap::MappedRepresentation() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentation>(*entity->getArgument(1)); }
IfcMappedItem::list IfcRepresentationMap::MapUsage() { RETURN_INVERSE(IfcMappedItem) }
bool IfcRepresentationMap::is(Type::Enum v) const { return v == Type::IfcRepresentationMap; }
Type::Enum IfcRepresentationMap::type() const { return Type::IfcRepresentationMap; }
Type::Enum IfcRepresentationMap::Class() { return Type::IfcRepresentationMap; }
IfcRepresentationMap::IfcRepresentationMap(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentationMap)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcResource
IfcRelAssignsToResource::list IfcResource::ResourceOf() { RETURN_INVERSE(IfcRelAssignsToResource) }
bool IfcResource::is(Type::Enum v) const { return v == Type::IfcResource || IfcObject::is(v); }
Type::Enum IfcResource::type() const { return Type::IfcResource; }
Type::Enum IfcResource::Class() { return Type::IfcResource; }
IfcResource::IfcResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRevolvedAreaSolid
IfcAxis1Placement* IfcRevolvedAreaSolid::Axis() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis1Placement>(*entity->getArgument(2)); }
IfcPlaneAngleMeasure IfcRevolvedAreaSolid::Angle() { return *entity->getArgument(3); }
bool IfcRevolvedAreaSolid::is(Type::Enum v) const { return v == Type::IfcRevolvedAreaSolid || IfcSweptAreaSolid::is(v); }
Type::Enum IfcRevolvedAreaSolid::type() const { return Type::IfcRevolvedAreaSolid; }
Type::Enum IfcRevolvedAreaSolid::Class() { return Type::IfcRevolvedAreaSolid; }
IfcRevolvedAreaSolid::IfcRevolvedAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcRevolvedAreaSolid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRibPlateProfileProperties
bool IfcRibPlateProfileProperties::hasThickness() { return !entity->getArgument(2)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::Thickness() { return *entity->getArgument(2); }
bool IfcRibPlateProfileProperties::hasRibHeight() { return !entity->getArgument(3)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::RibHeight() { return *entity->getArgument(3); }
bool IfcRibPlateProfileProperties::hasRibWidth() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::RibWidth() { return *entity->getArgument(4); }
bool IfcRibPlateProfileProperties::hasRibSpacing() { return !entity->getArgument(5)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::RibSpacing() { return *entity->getArgument(5); }
IfcRibPlateDirectionEnum::IfcRibPlateDirectionEnum IfcRibPlateProfileProperties::Direction() { return IfcRibPlateDirectionEnum::FromString(*entity->getArgument(6)); }
bool IfcRibPlateProfileProperties::is(Type::Enum v) const { return v == Type::IfcRibPlateProfileProperties || IfcProfileProperties::is(v); }
Type::Enum IfcRibPlateProfileProperties::type() const { return Type::IfcRibPlateProfileProperties; }
Type::Enum IfcRibPlateProfileProperties::Class() { return Type::IfcRibPlateProfileProperties; }
IfcRibPlateProfileProperties::IfcRibPlateProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRibPlateProfileProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRightCircularCone
IfcPositiveLengthMeasure IfcRightCircularCone::Height() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcRightCircularCone::BottomRadius() { return *entity->getArgument(2); }
bool IfcRightCircularCone::is(Type::Enum v) const { return v == Type::IfcRightCircularCone || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcRightCircularCone::type() const { return Type::IfcRightCircularCone; }
Type::Enum IfcRightCircularCone::Class() { return Type::IfcRightCircularCone; }
IfcRightCircularCone::IfcRightCircularCone(IfcAbstractEntityPtr e) { if (!is(Type::IfcRightCircularCone)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRightCircularCylinder
IfcPositiveLengthMeasure IfcRightCircularCylinder::Height() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcRightCircularCylinder::Radius() { return *entity->getArgument(2); }
bool IfcRightCircularCylinder::is(Type::Enum v) const { return v == Type::IfcRightCircularCylinder || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcRightCircularCylinder::type() const { return Type::IfcRightCircularCylinder; }
Type::Enum IfcRightCircularCylinder::Class() { return Type::IfcRightCircularCylinder; }
IfcRightCircularCylinder::IfcRightCircularCylinder(IfcAbstractEntityPtr e) { if (!is(Type::IfcRightCircularCylinder)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRoof
IfcRoofTypeEnum::IfcRoofTypeEnum IfcRoof::ShapeType() { return IfcRoofTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcRoof::is(Type::Enum v) const { return v == Type::IfcRoof || IfcBuildingElement::is(v); }
Type::Enum IfcRoof::type() const { return Type::IfcRoof; }
Type::Enum IfcRoof::Class() { return Type::IfcRoof; }
IfcRoof::IfcRoof(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoof)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRoot
IfcGloballyUniqueId IfcRoot::GlobalId() { return *entity->getArgument(0); }
IfcOwnerHistory* IfcRoot::OwnerHistory() { return reinterpret_pointer_cast<IfcBaseClass,IfcOwnerHistory>(*entity->getArgument(1)); }
bool IfcRoot::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcRoot::Name() { return *entity->getArgument(2); }
bool IfcRoot::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcRoot::Description() { return *entity->getArgument(3); }
bool IfcRoot::is(Type::Enum v) const { return v == Type::IfcRoot; }
Type::Enum IfcRoot::type() const { return Type::IfcRoot; }
Type::Enum IfcRoot::Class() { return Type::IfcRoot; }
IfcRoot::IfcRoot(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoot)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRoundedEdgeFeature
bool IfcRoundedEdgeFeature::hasRadius() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcRoundedEdgeFeature::Radius() { return *entity->getArgument(9); }
bool IfcRoundedEdgeFeature::is(Type::Enum v) const { return v == Type::IfcRoundedEdgeFeature || IfcEdgeFeature::is(v); }
Type::Enum IfcRoundedEdgeFeature::type() const { return Type::IfcRoundedEdgeFeature; }
Type::Enum IfcRoundedEdgeFeature::Class() { return Type::IfcRoundedEdgeFeature; }
IfcRoundedEdgeFeature::IfcRoundedEdgeFeature(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoundedEdgeFeature)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcRoundedRectangleProfileDef
IfcPositiveLengthMeasure IfcRoundedRectangleProfileDef::RoundingRadius() { return *entity->getArgument(5); }
bool IfcRoundedRectangleProfileDef::is(Type::Enum v) const { return v == Type::IfcRoundedRectangleProfileDef || IfcRectangleProfileDef::is(v); }
Type::Enum IfcRoundedRectangleProfileDef::type() const { return Type::IfcRoundedRectangleProfileDef; }
Type::Enum IfcRoundedRectangleProfileDef::Class() { return Type::IfcRoundedRectangleProfileDef; }
IfcRoundedRectangleProfileDef::IfcRoundedRectangleProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoundedRectangleProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSIUnit
bool IfcSIUnit::hasPrefix() { return !entity->getArgument(2)->isNull(); }
IfcSIPrefix::IfcSIPrefix IfcSIUnit::Prefix() { return IfcSIPrefix::FromString(*entity->getArgument(2)); }
IfcSIUnitName::IfcSIUnitName IfcSIUnit::Name() { return IfcSIUnitName::FromString(*entity->getArgument(3)); }
bool IfcSIUnit::is(Type::Enum v) const { return v == Type::IfcSIUnit || IfcNamedUnit::is(v); }
Type::Enum IfcSIUnit::type() const { return Type::IfcSIUnit; }
Type::Enum IfcSIUnit::Class() { return Type::IfcSIUnit; }
IfcSIUnit::IfcSIUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcSIUnit)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSanitaryTerminalType
IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalTypeEnum IfcSanitaryTerminalType::PredefinedType() { return IfcSanitaryTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSanitaryTerminalType::is(Type::Enum v) const { return v == Type::IfcSanitaryTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcSanitaryTerminalType::type() const { return Type::IfcSanitaryTerminalType; }
Type::Enum IfcSanitaryTerminalType::Class() { return Type::IfcSanitaryTerminalType; }
IfcSanitaryTerminalType::IfcSanitaryTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSanitaryTerminalType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcScheduleTimeControl
bool IfcScheduleTimeControl::hasActualStart() { return !entity->getArgument(5)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::ActualStart() { return *entity->getArgument(5); }
bool IfcScheduleTimeControl::hasEarlyStart() { return !entity->getArgument(6)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::EarlyStart() { return *entity->getArgument(6); }
bool IfcScheduleTimeControl::hasLateStart() { return !entity->getArgument(7)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::LateStart() { return *entity->getArgument(7); }
bool IfcScheduleTimeControl::hasScheduleStart() { return !entity->getArgument(8)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::ScheduleStart() { return *entity->getArgument(8); }
bool IfcScheduleTimeControl::hasActualFinish() { return !entity->getArgument(9)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::ActualFinish() { return *entity->getArgument(9); }
bool IfcScheduleTimeControl::hasEarlyFinish() { return !entity->getArgument(10)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::EarlyFinish() { return *entity->getArgument(10); }
bool IfcScheduleTimeControl::hasLateFinish() { return !entity->getArgument(11)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::LateFinish() { return *entity->getArgument(11); }
bool IfcScheduleTimeControl::hasScheduleFinish() { return !entity->getArgument(12)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::ScheduleFinish() { return *entity->getArgument(12); }
bool IfcScheduleTimeControl::hasScheduleDuration() { return !entity->getArgument(13)->isNull(); }
IfcTimeMeasure IfcScheduleTimeControl::ScheduleDuration() { return *entity->getArgument(13); }
bool IfcScheduleTimeControl::hasActualDuration() { return !entity->getArgument(14)->isNull(); }
IfcTimeMeasure IfcScheduleTimeControl::ActualDuration() { return *entity->getArgument(14); }
bool IfcScheduleTimeControl::hasRemainingTime() { return !entity->getArgument(15)->isNull(); }
IfcTimeMeasure IfcScheduleTimeControl::RemainingTime() { return *entity->getArgument(15); }
bool IfcScheduleTimeControl::hasFreeFloat() { return !entity->getArgument(16)->isNull(); }
IfcTimeMeasure IfcScheduleTimeControl::FreeFloat() { return *entity->getArgument(16); }
bool IfcScheduleTimeControl::hasTotalFloat() { return !entity->getArgument(17)->isNull(); }
IfcTimeMeasure IfcScheduleTimeControl::TotalFloat() { return *entity->getArgument(17); }
bool IfcScheduleTimeControl::hasIsCritical() { return !entity->getArgument(18)->isNull(); }
bool IfcScheduleTimeControl::IsCritical() { return *entity->getArgument(18); }
bool IfcScheduleTimeControl::hasStatusTime() { return !entity->getArgument(19)->isNull(); }
IfcDateTimeSelect IfcScheduleTimeControl::StatusTime() { return *entity->getArgument(19); }
bool IfcScheduleTimeControl::hasStartFloat() { return !entity->getArgument(20)->isNull(); }
IfcTimeMeasure IfcScheduleTimeControl::StartFloat() { return *entity->getArgument(20); }
bool IfcScheduleTimeControl::hasFinishFloat() { return !entity->getArgument(21)->isNull(); }
IfcTimeMeasure IfcScheduleTimeControl::FinishFloat() { return *entity->getArgument(21); }
bool IfcScheduleTimeControl::hasCompletion() { return !entity->getArgument(22)->isNull(); }
IfcPositiveRatioMeasure IfcScheduleTimeControl::Completion() { return *entity->getArgument(22); }
IfcRelAssignsTasks::list IfcScheduleTimeControl::ScheduleTimeControlAssigned() { RETURN_INVERSE(IfcRelAssignsTasks) }
bool IfcScheduleTimeControl::is(Type::Enum v) const { return v == Type::IfcScheduleTimeControl || IfcControl::is(v); }
Type::Enum IfcScheduleTimeControl::type() const { return Type::IfcScheduleTimeControl; }
Type::Enum IfcScheduleTimeControl::Class() { return Type::IfcScheduleTimeControl; }
IfcScheduleTimeControl::IfcScheduleTimeControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcScheduleTimeControl)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSectionProperties
IfcSectionTypeEnum::IfcSectionTypeEnum IfcSectionProperties::SectionType() { return IfcSectionTypeEnum::FromString(*entity->getArgument(0)); }
IfcProfileDef* IfcSectionProperties::StartProfile() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(1)); }
bool IfcSectionProperties::hasEndProfile() { return !entity->getArgument(2)->isNull(); }
IfcProfileDef* IfcSectionProperties::EndProfile() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(2)); }
bool IfcSectionProperties::is(Type::Enum v) const { return v == Type::IfcSectionProperties; }
Type::Enum IfcSectionProperties::type() const { return Type::IfcSectionProperties; }
Type::Enum IfcSectionProperties::Class() { return Type::IfcSectionProperties; }
IfcSectionProperties::IfcSectionProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSectionProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSectionReinforcementProperties
IfcLengthMeasure IfcSectionReinforcementProperties::LongitudinalStartPosition() { return *entity->getArgument(0); }
IfcLengthMeasure IfcSectionReinforcementProperties::LongitudinalEndPosition() { return *entity->getArgument(1); }
bool IfcSectionReinforcementProperties::hasTransversePosition() { return !entity->getArgument(2)->isNull(); }
IfcLengthMeasure IfcSectionReinforcementProperties::TransversePosition() { return *entity->getArgument(2); }
IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum IfcSectionReinforcementProperties::ReinforcementRole() { return IfcReinforcingBarRoleEnum::FromString(*entity->getArgument(3)); }
IfcSectionProperties* IfcSectionReinforcementProperties::SectionDefinition() { return reinterpret_pointer_cast<IfcBaseClass,IfcSectionProperties>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementBarProperties> > IfcSectionReinforcementProperties::CrossSectionReinforcementDefinitions() { RETURN_AS_LIST(IfcReinforcementBarProperties,5) }
bool IfcSectionReinforcementProperties::is(Type::Enum v) const { return v == Type::IfcSectionReinforcementProperties; }
Type::Enum IfcSectionReinforcementProperties::type() const { return Type::IfcSectionReinforcementProperties; }
Type::Enum IfcSectionReinforcementProperties::Class() { return Type::IfcSectionReinforcementProperties; }
IfcSectionReinforcementProperties::IfcSectionReinforcementProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSectionReinforcementProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSectionedSpine
IfcCompositeCurve* IfcSectionedSpine::SpineCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCompositeCurve>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > IfcSectionedSpine::CrossSections() { RETURN_AS_LIST(IfcProfileDef,1) }
SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement3D> > IfcSectionedSpine::CrossSectionPositions() { RETURN_AS_LIST(IfcAxis2Placement3D,2) }
bool IfcSectionedSpine::is(Type::Enum v) const { return v == Type::IfcSectionedSpine || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcSectionedSpine::type() const { return Type::IfcSectionedSpine; }
Type::Enum IfcSectionedSpine::Class() { return Type::IfcSectionedSpine; }
IfcSectionedSpine::IfcSectionedSpine(IfcAbstractEntityPtr e) { if (!is(Type::IfcSectionedSpine)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSensorType
IfcSensorTypeEnum::IfcSensorTypeEnum IfcSensorType::PredefinedType() { return IfcSensorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSensorType::is(Type::Enum v) const { return v == Type::IfcSensorType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcSensorType::type() const { return Type::IfcSensorType; }
Type::Enum IfcSensorType::Class() { return Type::IfcSensorType; }
IfcSensorType::IfcSensorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSensorType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcServiceLife
IfcServiceLifeTypeEnum::IfcServiceLifeTypeEnum IfcServiceLife::ServiceLifeType() { return IfcServiceLifeTypeEnum::FromString(*entity->getArgument(5)); }
IfcTimeMeasure IfcServiceLife::ServiceLifeDuration() { return *entity->getArgument(6); }
bool IfcServiceLife::is(Type::Enum v) const { return v == Type::IfcServiceLife || IfcControl::is(v); }
Type::Enum IfcServiceLife::type() const { return Type::IfcServiceLife; }
Type::Enum IfcServiceLife::Class() { return Type::IfcServiceLife; }
IfcServiceLife::IfcServiceLife(IfcAbstractEntityPtr e) { if (!is(Type::IfcServiceLife)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcServiceLifeFactor
IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorTypeEnum IfcServiceLifeFactor::PredefinedType() { return IfcServiceLifeFactorTypeEnum::FromString(*entity->getArgument(4)); }
bool IfcServiceLifeFactor::hasUpperValue() { return !entity->getArgument(5)->isNull(); }
IfcMeasureValue IfcServiceLifeFactor::UpperValue() { return *entity->getArgument(5); }
IfcMeasureValue IfcServiceLifeFactor::MostUsedValue() { return *entity->getArgument(6); }
bool IfcServiceLifeFactor::hasLowerValue() { return !entity->getArgument(7)->isNull(); }
IfcMeasureValue IfcServiceLifeFactor::LowerValue() { return *entity->getArgument(7); }
bool IfcServiceLifeFactor::is(Type::Enum v) const { return v == Type::IfcServiceLifeFactor || IfcPropertySetDefinition::is(v); }
Type::Enum IfcServiceLifeFactor::type() const { return Type::IfcServiceLifeFactor; }
Type::Enum IfcServiceLifeFactor::Class() { return Type::IfcServiceLifeFactor; }
IfcServiceLifeFactor::IfcServiceLifeFactor(IfcAbstractEntityPtr e) { if (!is(Type::IfcServiceLifeFactor)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcShapeAspect
SHARED_PTR< IfcTemplatedEntityList<IfcShapeModel> > IfcShapeAspect::ShapeRepresentations() { RETURN_AS_LIST(IfcShapeModel,0) }
bool IfcShapeAspect::hasName() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcShapeAspect::Name() { return *entity->getArgument(1); }
bool IfcShapeAspect::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcShapeAspect::Description() { return *entity->getArgument(2); }
bool IfcShapeAspect::ProductDefinitional() { return *entity->getArgument(3); }
IfcProductDefinitionShape* IfcShapeAspect::PartOfProductDefinitionShape() { return reinterpret_pointer_cast<IfcBaseClass,IfcProductDefinitionShape>(*entity->getArgument(4)); }
bool IfcShapeAspect::is(Type::Enum v) const { return v == Type::IfcShapeAspect; }
Type::Enum IfcShapeAspect::type() const { return Type::IfcShapeAspect; }
Type::Enum IfcShapeAspect::Class() { return Type::IfcShapeAspect; }
IfcShapeAspect::IfcShapeAspect(IfcAbstractEntityPtr e) { if (!is(Type::IfcShapeAspect)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcShapeModel
IfcShapeAspect::list IfcShapeModel::OfShapeAspect() { RETURN_INVERSE(IfcShapeAspect) }
bool IfcShapeModel::is(Type::Enum v) const { return v == Type::IfcShapeModel || IfcRepresentation::is(v); }
Type::Enum IfcShapeModel::type() const { return Type::IfcShapeModel; }
Type::Enum IfcShapeModel::Class() { return Type::IfcShapeModel; }
IfcShapeModel::IfcShapeModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcShapeModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcShapeRepresentation
bool IfcShapeRepresentation::is(Type::Enum v) const { return v == Type::IfcShapeRepresentation || IfcShapeModel::is(v); }
Type::Enum IfcShapeRepresentation::type() const { return Type::IfcShapeRepresentation; }
Type::Enum IfcShapeRepresentation::Class() { return Type::IfcShapeRepresentation; }
IfcShapeRepresentation::IfcShapeRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcShapeRepresentation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcShellBasedSurfaceModel
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcShellBasedSurfaceModel::SbsmBoundary() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcShellBasedSurfaceModel::is(Type::Enum v) const { return v == Type::IfcShellBasedSurfaceModel || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcShellBasedSurfaceModel::type() const { return Type::IfcShellBasedSurfaceModel; }
Type::Enum IfcShellBasedSurfaceModel::Class() { return Type::IfcShellBasedSurfaceModel; }
IfcShellBasedSurfaceModel::IfcShellBasedSurfaceModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcShellBasedSurfaceModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSimpleProperty
bool IfcSimpleProperty::is(Type::Enum v) const { return v == Type::IfcSimpleProperty || IfcProperty::is(v); }
Type::Enum IfcSimpleProperty::type() const { return Type::IfcSimpleProperty; }
Type::Enum IfcSimpleProperty::Class() { return Type::IfcSimpleProperty; }
IfcSimpleProperty::IfcSimpleProperty(IfcAbstractEntityPtr e) { if (!is(Type::IfcSimpleProperty)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSite
bool IfcSite::hasRefLatitude() { return !entity->getArgument(9)->isNull(); }
IfcCompoundPlaneAngleMeasure IfcSite::RefLatitude() { return *entity->getArgument(9); }
bool IfcSite::hasRefLongitude() { return !entity->getArgument(10)->isNull(); }
IfcCompoundPlaneAngleMeasure IfcSite::RefLongitude() { return *entity->getArgument(10); }
bool IfcSite::hasRefElevation() { return !entity->getArgument(11)->isNull(); }
IfcLengthMeasure IfcSite::RefElevation() { return *entity->getArgument(11); }
bool IfcSite::hasLandTitleNumber() { return !entity->getArgument(12)->isNull(); }
IfcLabel IfcSite::LandTitleNumber() { return *entity->getArgument(12); }
bool IfcSite::hasSiteAddress() { return !entity->getArgument(13)->isNull(); }
IfcPostalAddress* IfcSite::SiteAddress() { return reinterpret_pointer_cast<IfcBaseClass,IfcPostalAddress>(*entity->getArgument(13)); }
bool IfcSite::is(Type::Enum v) const { return v == Type::IfcSite || IfcSpatialStructureElement::is(v); }
Type::Enum IfcSite::type() const { return Type::IfcSite; }
Type::Enum IfcSite::Class() { return Type::IfcSite; }
IfcSite::IfcSite(IfcAbstractEntityPtr e) { if (!is(Type::IfcSite)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSlab
bool IfcSlab::hasPredefinedType() { return !entity->getArgument(8)->isNull(); }
IfcSlabTypeEnum::IfcSlabTypeEnum IfcSlab::PredefinedType() { return IfcSlabTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcSlab::is(Type::Enum v) const { return v == Type::IfcSlab || IfcBuildingElement::is(v); }
Type::Enum IfcSlab::type() const { return Type::IfcSlab; }
Type::Enum IfcSlab::Class() { return Type::IfcSlab; }
IfcSlab::IfcSlab(IfcAbstractEntityPtr e) { if (!is(Type::IfcSlab)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSlabType
IfcSlabTypeEnum::IfcSlabTypeEnum IfcSlabType::PredefinedType() { return IfcSlabTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSlabType::is(Type::Enum v) const { return v == Type::IfcSlabType || IfcBuildingElementType::is(v); }
Type::Enum IfcSlabType::type() const { return Type::IfcSlabType; }
Type::Enum IfcSlabType::Class() { return Type::IfcSlabType; }
IfcSlabType::IfcSlabType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSlabType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSlippageConnectionCondition
bool IfcSlippageConnectionCondition::hasSlippageX() { return !entity->getArgument(1)->isNull(); }
IfcLengthMeasure IfcSlippageConnectionCondition::SlippageX() { return *entity->getArgument(1); }
bool IfcSlippageConnectionCondition::hasSlippageY() { return !entity->getArgument(2)->isNull(); }
IfcLengthMeasure IfcSlippageConnectionCondition::SlippageY() { return *entity->getArgument(2); }
bool IfcSlippageConnectionCondition::hasSlippageZ() { return !entity->getArgument(3)->isNull(); }
IfcLengthMeasure IfcSlippageConnectionCondition::SlippageZ() { return *entity->getArgument(3); }
bool IfcSlippageConnectionCondition::is(Type::Enum v) const { return v == Type::IfcSlippageConnectionCondition || IfcStructuralConnectionCondition::is(v); }
Type::Enum IfcSlippageConnectionCondition::type() const { return Type::IfcSlippageConnectionCondition; }
Type::Enum IfcSlippageConnectionCondition::Class() { return Type::IfcSlippageConnectionCondition; }
IfcSlippageConnectionCondition::IfcSlippageConnectionCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcSlippageConnectionCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSolidModel
bool IfcSolidModel::is(Type::Enum v) const { return v == Type::IfcSolidModel || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcSolidModel::type() const { return Type::IfcSolidModel; }
Type::Enum IfcSolidModel::Class() { return Type::IfcSolidModel; }
IfcSolidModel::IfcSolidModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcSolidModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSoundProperties
IfcBoolean IfcSoundProperties::IsAttenuating() { return *entity->getArgument(4); }
bool IfcSoundProperties::hasSoundScale() { return !entity->getArgument(5)->isNull(); }
IfcSoundScaleEnum::IfcSoundScaleEnum IfcSoundProperties::SoundScale() { return IfcSoundScaleEnum::FromString(*entity->getArgument(5)); }
SHARED_PTR< IfcTemplatedEntityList<IfcSoundValue> > IfcSoundProperties::SoundValues() { RETURN_AS_LIST(IfcSoundValue,6) }
bool IfcSoundProperties::is(Type::Enum v) const { return v == Type::IfcSoundProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcSoundProperties::type() const { return Type::IfcSoundProperties; }
Type::Enum IfcSoundProperties::Class() { return Type::IfcSoundProperties; }
IfcSoundProperties::IfcSoundProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSoundProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSoundValue
bool IfcSoundValue::hasSoundLevelTimeSeries() { return !entity->getArgument(4)->isNull(); }
IfcTimeSeries* IfcSoundValue::SoundLevelTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(4)); }
IfcFrequencyMeasure IfcSoundValue::Frequency() { return *entity->getArgument(5); }
bool IfcSoundValue::hasSoundLevelSingleValue() { return !entity->getArgument(6)->isNull(); }
IfcDerivedMeasureValue IfcSoundValue::SoundLevelSingleValue() { return *entity->getArgument(6); }
bool IfcSoundValue::is(Type::Enum v) const { return v == Type::IfcSoundValue || IfcPropertySetDefinition::is(v); }
Type::Enum IfcSoundValue::type() const { return Type::IfcSoundValue; }
Type::Enum IfcSoundValue::Class() { return Type::IfcSoundValue; }
IfcSoundValue::IfcSoundValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcSoundValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSpace
IfcInternalOrExternalEnum::IfcInternalOrExternalEnum IfcSpace::InteriorOrExteriorSpace() { return IfcInternalOrExternalEnum::FromString(*entity->getArgument(9)); }
bool IfcSpace::hasElevationWithFlooring() { return !entity->getArgument(10)->isNull(); }
IfcLengthMeasure IfcSpace::ElevationWithFlooring() { return *entity->getArgument(10); }
IfcRelCoversSpaces::list IfcSpace::HasCoverings() { RETURN_INVERSE(IfcRelCoversSpaces) }
IfcRelSpaceBoundary::list IfcSpace::BoundedBy() { RETURN_INVERSE(IfcRelSpaceBoundary) }
bool IfcSpace::is(Type::Enum v) const { return v == Type::IfcSpace || IfcSpatialStructureElement::is(v); }
Type::Enum IfcSpace::type() const { return Type::IfcSpace; }
Type::Enum IfcSpace::Class() { return Type::IfcSpace; }
IfcSpace::IfcSpace(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpace)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSpaceHeaterType
IfcSpaceHeaterTypeEnum::IfcSpaceHeaterTypeEnum IfcSpaceHeaterType::PredefinedType() { return IfcSpaceHeaterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSpaceHeaterType::is(Type::Enum v) const { return v == Type::IfcSpaceHeaterType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcSpaceHeaterType::type() const { return Type::IfcSpaceHeaterType; }
Type::Enum IfcSpaceHeaterType::Class() { return Type::IfcSpaceHeaterType; }
IfcSpaceHeaterType::IfcSpaceHeaterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceHeaterType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSpaceProgram
IfcIdentifier IfcSpaceProgram::SpaceProgramIdentifier() { return *entity->getArgument(5); }
bool IfcSpaceProgram::hasMaxRequiredArea() { return !entity->getArgument(6)->isNull(); }
IfcAreaMeasure IfcSpaceProgram::MaxRequiredArea() { return *entity->getArgument(6); }
bool IfcSpaceProgram::hasMinRequiredArea() { return !entity->getArgument(7)->isNull(); }
IfcAreaMeasure IfcSpaceProgram::MinRequiredArea() { return *entity->getArgument(7); }
bool IfcSpaceProgram::hasRequestedLocation() { return !entity->getArgument(8)->isNull(); }
IfcSpatialStructureElement* IfcSpaceProgram::RequestedLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(8)); }
IfcAreaMeasure IfcSpaceProgram::StandardRequiredArea() { return *entity->getArgument(9); }
IfcRelInteractionRequirements::list IfcSpaceProgram::HasInteractionReqsFrom() { RETURN_INVERSE(IfcRelInteractionRequirements) }
IfcRelInteractionRequirements::list IfcSpaceProgram::HasInteractionReqsTo() { RETURN_INVERSE(IfcRelInteractionRequirements) }
bool IfcSpaceProgram::is(Type::Enum v) const { return v == Type::IfcSpaceProgram || IfcControl::is(v); }
Type::Enum IfcSpaceProgram::type() const { return Type::IfcSpaceProgram; }
Type::Enum IfcSpaceProgram::Class() { return Type::IfcSpaceProgram; }
IfcSpaceProgram::IfcSpaceProgram(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceProgram)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSpaceThermalLoadProperties
bool IfcSpaceThermalLoadProperties::hasApplicableValueRatio() { return !entity->getArgument(4)->isNull(); }
IfcPositiveRatioMeasure IfcSpaceThermalLoadProperties::ApplicableValueRatio() { return *entity->getArgument(4); }
IfcThermalLoadSourceEnum::IfcThermalLoadSourceEnum IfcSpaceThermalLoadProperties::ThermalLoadSource() { return IfcThermalLoadSourceEnum::FromString(*entity->getArgument(5)); }
IfcPropertySourceEnum::IfcPropertySourceEnum IfcSpaceThermalLoadProperties::PropertySource() { return IfcPropertySourceEnum::FromString(*entity->getArgument(6)); }
bool IfcSpaceThermalLoadProperties::hasSourceDescription() { return !entity->getArgument(7)->isNull(); }
IfcText IfcSpaceThermalLoadProperties::SourceDescription() { return *entity->getArgument(7); }
IfcPowerMeasure IfcSpaceThermalLoadProperties::MaximumValue() { return *entity->getArgument(8); }
bool IfcSpaceThermalLoadProperties::hasMinimumValue() { return !entity->getArgument(9)->isNull(); }
IfcPowerMeasure IfcSpaceThermalLoadProperties::MinimumValue() { return *entity->getArgument(9); }
bool IfcSpaceThermalLoadProperties::hasThermalLoadTimeSeriesValues() { return !entity->getArgument(10)->isNull(); }
IfcTimeSeries* IfcSpaceThermalLoadProperties::ThermalLoadTimeSeriesValues() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(10)); }
bool IfcSpaceThermalLoadProperties::hasUserDefinedThermalLoadSource() { return !entity->getArgument(11)->isNull(); }
IfcLabel IfcSpaceThermalLoadProperties::UserDefinedThermalLoadSource() { return *entity->getArgument(11); }
bool IfcSpaceThermalLoadProperties::hasUserDefinedPropertySource() { return !entity->getArgument(12)->isNull(); }
IfcLabel IfcSpaceThermalLoadProperties::UserDefinedPropertySource() { return *entity->getArgument(12); }
IfcThermalLoadTypeEnum::IfcThermalLoadTypeEnum IfcSpaceThermalLoadProperties::ThermalLoadType() { return IfcThermalLoadTypeEnum::FromString(*entity->getArgument(13)); }
bool IfcSpaceThermalLoadProperties::is(Type::Enum v) const { return v == Type::IfcSpaceThermalLoadProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcSpaceThermalLoadProperties::type() const { return Type::IfcSpaceThermalLoadProperties; }
Type::Enum IfcSpaceThermalLoadProperties::Class() { return Type::IfcSpaceThermalLoadProperties; }
IfcSpaceThermalLoadProperties::IfcSpaceThermalLoadProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceThermalLoadProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSpaceType
IfcSpaceTypeEnum::IfcSpaceTypeEnum IfcSpaceType::PredefinedType() { return IfcSpaceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSpaceType::is(Type::Enum v) const { return v == Type::IfcSpaceType || IfcSpatialStructureElementType::is(v); }
Type::Enum IfcSpaceType::type() const { return Type::IfcSpaceType; }
Type::Enum IfcSpaceType::Class() { return Type::IfcSpaceType; }
IfcSpaceType::IfcSpaceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSpatialStructureElement
bool IfcSpatialStructureElement::hasLongName() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcSpatialStructureElement::LongName() { return *entity->getArgument(7); }
IfcElementCompositionEnum::IfcElementCompositionEnum IfcSpatialStructureElement::CompositionType() { return IfcElementCompositionEnum::FromString(*entity->getArgument(8)); }
IfcRelReferencedInSpatialStructure::list IfcSpatialStructureElement::ReferencesElements() { RETURN_INVERSE(IfcRelReferencedInSpatialStructure) }
IfcRelServicesBuildings::list IfcSpatialStructureElement::ServicedBySystems() { RETURN_INVERSE(IfcRelServicesBuildings) }
IfcRelContainedInSpatialStructure::list IfcSpatialStructureElement::ContainsElements() { RETURN_INVERSE(IfcRelContainedInSpatialStructure) }
bool IfcSpatialStructureElement::is(Type::Enum v) const { return v == Type::IfcSpatialStructureElement || IfcProduct::is(v); }
Type::Enum IfcSpatialStructureElement::type() const { return Type::IfcSpatialStructureElement; }
Type::Enum IfcSpatialStructureElement::Class() { return Type::IfcSpatialStructureElement; }
IfcSpatialStructureElement::IfcSpatialStructureElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpatialStructureElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSpatialStructureElementType
bool IfcSpatialStructureElementType::is(Type::Enum v) const { return v == Type::IfcSpatialStructureElementType || IfcElementType::is(v); }
Type::Enum IfcSpatialStructureElementType::type() const { return Type::IfcSpatialStructureElementType; }
Type::Enum IfcSpatialStructureElementType::Class() { return Type::IfcSpatialStructureElementType; }
IfcSpatialStructureElementType::IfcSpatialStructureElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpatialStructureElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSphere
IfcPositiveLengthMeasure IfcSphere::Radius() { return *entity->getArgument(1); }
bool IfcSphere::is(Type::Enum v) const { return v == Type::IfcSphere || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcSphere::type() const { return Type::IfcSphere; }
Type::Enum IfcSphere::Class() { return Type::IfcSphere; }
IfcSphere::IfcSphere(IfcAbstractEntityPtr e) { if (!is(Type::IfcSphere)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStackTerminalType
IfcStackTerminalTypeEnum::IfcStackTerminalTypeEnum IfcStackTerminalType::PredefinedType() { return IfcStackTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcStackTerminalType::is(Type::Enum v) const { return v == Type::IfcStackTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcStackTerminalType::type() const { return Type::IfcStackTerminalType; }
Type::Enum IfcStackTerminalType::Class() { return Type::IfcStackTerminalType; }
IfcStackTerminalType::IfcStackTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcStackTerminalType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStair
IfcStairTypeEnum::IfcStairTypeEnum IfcStair::ShapeType() { return IfcStairTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcStair::is(Type::Enum v) const { return v == Type::IfcStair || IfcBuildingElement::is(v); }
Type::Enum IfcStair::type() const { return Type::IfcStair; }
Type::Enum IfcStair::Class() { return Type::IfcStair; }
IfcStair::IfcStair(IfcAbstractEntityPtr e) { if (!is(Type::IfcStair)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStairFlight
bool IfcStairFlight::hasNumberOfRiser() { return !entity->getArgument(8)->isNull(); }
int IfcStairFlight::NumberOfRiser() { return *entity->getArgument(8); }
bool IfcStairFlight::hasNumberOfTreads() { return !entity->getArgument(9)->isNull(); }
int IfcStairFlight::NumberOfTreads() { return *entity->getArgument(9); }
bool IfcStairFlight::hasRiserHeight() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcStairFlight::RiserHeight() { return *entity->getArgument(10); }
bool IfcStairFlight::hasTreadLength() { return !entity->getArgument(11)->isNull(); }
IfcPositiveLengthMeasure IfcStairFlight::TreadLength() { return *entity->getArgument(11); }
bool IfcStairFlight::is(Type::Enum v) const { return v == Type::IfcStairFlight || IfcBuildingElement::is(v); }
Type::Enum IfcStairFlight::type() const { return Type::IfcStairFlight; }
Type::Enum IfcStairFlight::Class() { return Type::IfcStairFlight; }
IfcStairFlight::IfcStairFlight(IfcAbstractEntityPtr e) { if (!is(Type::IfcStairFlight)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStairFlightType
IfcStairFlightTypeEnum::IfcStairFlightTypeEnum IfcStairFlightType::PredefinedType() { return IfcStairFlightTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcStairFlightType::is(Type::Enum v) const { return v == Type::IfcStairFlightType || IfcBuildingElementType::is(v); }
Type::Enum IfcStairFlightType::type() const { return Type::IfcStairFlightType; }
Type::Enum IfcStairFlightType::Class() { return Type::IfcStairFlightType; }
IfcStairFlightType::IfcStairFlightType(IfcAbstractEntityPtr e) { if (!is(Type::IfcStairFlightType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralAction
bool IfcStructuralAction::DestabilizingLoad() { return *entity->getArgument(9); }
bool IfcStructuralAction::hasCausedBy() { return !entity->getArgument(10)->isNull(); }
IfcStructuralReaction* IfcStructuralAction::CausedBy() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralReaction>(*entity->getArgument(10)); }
bool IfcStructuralAction::is(Type::Enum v) const { return v == Type::IfcStructuralAction || IfcStructuralActivity::is(v); }
Type::Enum IfcStructuralAction::type() const { return Type::IfcStructuralAction; }
Type::Enum IfcStructuralAction::Class() { return Type::IfcStructuralAction; }
IfcStructuralAction::IfcStructuralAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralAction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralActivity
IfcStructuralLoad* IfcStructuralActivity::AppliedLoad() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralLoad>(*entity->getArgument(7)); }
IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum IfcStructuralActivity::GlobalOrLocal() { return IfcGlobalOrLocalEnum::FromString(*entity->getArgument(8)); }
IfcRelConnectsStructuralActivity::list IfcStructuralActivity::AssignedToStructuralItem() { RETURN_INVERSE(IfcRelConnectsStructuralActivity) }
bool IfcStructuralActivity::is(Type::Enum v) const { return v == Type::IfcStructuralActivity || IfcProduct::is(v); }
Type::Enum IfcStructuralActivity::type() const { return Type::IfcStructuralActivity; }
Type::Enum IfcStructuralActivity::Class() { return Type::IfcStructuralActivity; }
IfcStructuralActivity::IfcStructuralActivity(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralActivity)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralAnalysisModel
IfcAnalysisModelTypeEnum::IfcAnalysisModelTypeEnum IfcStructuralAnalysisModel::PredefinedType() { return IfcAnalysisModelTypeEnum::FromString(*entity->getArgument(5)); }
bool IfcStructuralAnalysisModel::hasOrientationOf2DPlane() { return !entity->getArgument(6)->isNull(); }
IfcAxis2Placement3D* IfcStructuralAnalysisModel::OrientationOf2DPlane() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(6)); }
bool IfcStructuralAnalysisModel::hasLoadedBy() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadGroup> > IfcStructuralAnalysisModel::LoadedBy() { RETURN_AS_LIST(IfcStructuralLoadGroup,7) }
bool IfcStructuralAnalysisModel::hasHasResults() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralResultGroup> > IfcStructuralAnalysisModel::HasResults() { RETURN_AS_LIST(IfcStructuralResultGroup,8) }
bool IfcStructuralAnalysisModel::is(Type::Enum v) const { return v == Type::IfcStructuralAnalysisModel || IfcSystem::is(v); }
Type::Enum IfcStructuralAnalysisModel::type() const { return Type::IfcStructuralAnalysisModel; }
Type::Enum IfcStructuralAnalysisModel::Class() { return Type::IfcStructuralAnalysisModel; }
IfcStructuralAnalysisModel::IfcStructuralAnalysisModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralAnalysisModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralConnection
bool IfcStructuralConnection::hasAppliedCondition() { return !entity->getArgument(7)->isNull(); }
IfcBoundaryCondition* IfcStructuralConnection::AppliedCondition() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundaryCondition>(*entity->getArgument(7)); }
IfcRelConnectsStructuralMember::list IfcStructuralConnection::ConnectsStructuralMembers() { RETURN_INVERSE(IfcRelConnectsStructuralMember) }
bool IfcStructuralConnection::is(Type::Enum v) const { return v == Type::IfcStructuralConnection || IfcStructuralItem::is(v); }
Type::Enum IfcStructuralConnection::type() const { return Type::IfcStructuralConnection; }
Type::Enum IfcStructuralConnection::Class() { return Type::IfcStructuralConnection; }
IfcStructuralConnection::IfcStructuralConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralConnection)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralConnectionCondition
bool IfcStructuralConnectionCondition::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcStructuralConnectionCondition::Name() { return *entity->getArgument(0); }
bool IfcStructuralConnectionCondition::is(Type::Enum v) const { return v == Type::IfcStructuralConnectionCondition; }
Type::Enum IfcStructuralConnectionCondition::type() const { return Type::IfcStructuralConnectionCondition; }
Type::Enum IfcStructuralConnectionCondition::Class() { return Type::IfcStructuralConnectionCondition; }
IfcStructuralConnectionCondition::IfcStructuralConnectionCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralConnectionCondition)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralCurveConnection
bool IfcStructuralCurveConnection::is(Type::Enum v) const { return v == Type::IfcStructuralCurveConnection || IfcStructuralConnection::is(v); }
Type::Enum IfcStructuralCurveConnection::type() const { return Type::IfcStructuralCurveConnection; }
Type::Enum IfcStructuralCurveConnection::Class() { return Type::IfcStructuralCurveConnection; }
IfcStructuralCurveConnection::IfcStructuralCurveConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralCurveConnection)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralCurveMember
IfcStructuralCurveTypeEnum::IfcStructuralCurveTypeEnum IfcStructuralCurveMember::PredefinedType() { return IfcStructuralCurveTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcStructuralCurveMember::is(Type::Enum v) const { return v == Type::IfcStructuralCurveMember || IfcStructuralMember::is(v); }
Type::Enum IfcStructuralCurveMember::type() const { return Type::IfcStructuralCurveMember; }
Type::Enum IfcStructuralCurveMember::Class() { return Type::IfcStructuralCurveMember; }
IfcStructuralCurveMember::IfcStructuralCurveMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralCurveMember)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralCurveMemberVarying
bool IfcStructuralCurveMemberVarying::is(Type::Enum v) const { return v == Type::IfcStructuralCurveMemberVarying || IfcStructuralCurveMember::is(v); }
Type::Enum IfcStructuralCurveMemberVarying::type() const { return Type::IfcStructuralCurveMemberVarying; }
Type::Enum IfcStructuralCurveMemberVarying::Class() { return Type::IfcStructuralCurveMemberVarying; }
IfcStructuralCurveMemberVarying::IfcStructuralCurveMemberVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralCurveMemberVarying)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralItem
IfcRelConnectsStructuralActivity::list IfcStructuralItem::AssignedStructuralActivity() { RETURN_INVERSE(IfcRelConnectsStructuralActivity) }
bool IfcStructuralItem::is(Type::Enum v) const { return v == Type::IfcStructuralItem || IfcProduct::is(v); }
Type::Enum IfcStructuralItem::type() const { return Type::IfcStructuralItem; }
Type::Enum IfcStructuralItem::Class() { return Type::IfcStructuralItem; }
IfcStructuralItem::IfcStructuralItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLinearAction
IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum IfcStructuralLinearAction::ProjectedOrTrue() { return IfcProjectedOrTrueLengthEnum::FromString(*entity->getArgument(11)); }
bool IfcStructuralLinearAction::is(Type::Enum v) const { return v == Type::IfcStructuralLinearAction || IfcStructuralAction::is(v); }
Type::Enum IfcStructuralLinearAction::type() const { return Type::IfcStructuralLinearAction; }
Type::Enum IfcStructuralLinearAction::Class() { return Type::IfcStructuralLinearAction; }
IfcStructuralLinearAction::IfcStructuralLinearAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLinearAction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLinearActionVarying
IfcShapeAspect* IfcStructuralLinearActionVarying::VaryingAppliedLoadLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(12)); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > IfcStructuralLinearActionVarying::SubsequentAppliedLoads() { RETURN_AS_LIST(IfcStructuralLoad,13) }
bool IfcStructuralLinearActionVarying::is(Type::Enum v) const { return v == Type::IfcStructuralLinearActionVarying || IfcStructuralLinearAction::is(v); }
Type::Enum IfcStructuralLinearActionVarying::type() const { return Type::IfcStructuralLinearActionVarying; }
Type::Enum IfcStructuralLinearActionVarying::Class() { return Type::IfcStructuralLinearActionVarying; }
IfcStructuralLinearActionVarying::IfcStructuralLinearActionVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLinearActionVarying)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoad
bool IfcStructuralLoad::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcStructuralLoad::Name() { return *entity->getArgument(0); }
bool IfcStructuralLoad::is(Type::Enum v) const { return v == Type::IfcStructuralLoad; }
Type::Enum IfcStructuralLoad::type() const { return Type::IfcStructuralLoad; }
Type::Enum IfcStructuralLoad::Class() { return Type::IfcStructuralLoad; }
IfcStructuralLoad::IfcStructuralLoad(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoad)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadGroup
IfcLoadGroupTypeEnum::IfcLoadGroupTypeEnum IfcStructuralLoadGroup::PredefinedType() { return IfcLoadGroupTypeEnum::FromString(*entity->getArgument(5)); }
IfcActionTypeEnum::IfcActionTypeEnum IfcStructuralLoadGroup::ActionType() { return IfcActionTypeEnum::FromString(*entity->getArgument(6)); }
IfcActionSourceTypeEnum::IfcActionSourceTypeEnum IfcStructuralLoadGroup::ActionSource() { return IfcActionSourceTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcStructuralLoadGroup::hasCoefficient() { return !entity->getArgument(8)->isNull(); }
IfcRatioMeasure IfcStructuralLoadGroup::Coefficient() { return *entity->getArgument(8); }
bool IfcStructuralLoadGroup::hasPurpose() { return !entity->getArgument(9)->isNull(); }
IfcLabel IfcStructuralLoadGroup::Purpose() { return *entity->getArgument(9); }
IfcStructuralResultGroup::list IfcStructuralLoadGroup::SourceOfResultGroup() { RETURN_INVERSE(IfcStructuralResultGroup) }
IfcStructuralAnalysisModel::list IfcStructuralLoadGroup::LoadGroupFor() { RETURN_INVERSE(IfcStructuralAnalysisModel) }
bool IfcStructuralLoadGroup::is(Type::Enum v) const { return v == Type::IfcStructuralLoadGroup || IfcGroup::is(v); }
Type::Enum IfcStructuralLoadGroup::type() const { return Type::IfcStructuralLoadGroup; }
Type::Enum IfcStructuralLoadGroup::Class() { return Type::IfcStructuralLoadGroup; }
IfcStructuralLoadGroup::IfcStructuralLoadGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadGroup)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadLinearForce
bool IfcStructuralLoadLinearForce::hasLinearForceX() { return !entity->getArgument(1)->isNull(); }
IfcLinearForceMeasure IfcStructuralLoadLinearForce::LinearForceX() { return *entity->getArgument(1); }
bool IfcStructuralLoadLinearForce::hasLinearForceY() { return !entity->getArgument(2)->isNull(); }
IfcLinearForceMeasure IfcStructuralLoadLinearForce::LinearForceY() { return *entity->getArgument(2); }
bool IfcStructuralLoadLinearForce::hasLinearForceZ() { return !entity->getArgument(3)->isNull(); }
IfcLinearForceMeasure IfcStructuralLoadLinearForce::LinearForceZ() { return *entity->getArgument(3); }
bool IfcStructuralLoadLinearForce::hasLinearMomentX() { return !entity->getArgument(4)->isNull(); }
IfcLinearMomentMeasure IfcStructuralLoadLinearForce::LinearMomentX() { return *entity->getArgument(4); }
bool IfcStructuralLoadLinearForce::hasLinearMomentY() { return !entity->getArgument(5)->isNull(); }
IfcLinearMomentMeasure IfcStructuralLoadLinearForce::LinearMomentY() { return *entity->getArgument(5); }
bool IfcStructuralLoadLinearForce::hasLinearMomentZ() { return !entity->getArgument(6)->isNull(); }
IfcLinearMomentMeasure IfcStructuralLoadLinearForce::LinearMomentZ() { return *entity->getArgument(6); }
bool IfcStructuralLoadLinearForce::is(Type::Enum v) const { return v == Type::IfcStructuralLoadLinearForce || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadLinearForce::type() const { return Type::IfcStructuralLoadLinearForce; }
Type::Enum IfcStructuralLoadLinearForce::Class() { return Type::IfcStructuralLoadLinearForce; }
IfcStructuralLoadLinearForce::IfcStructuralLoadLinearForce(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadLinearForce)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadPlanarForce
bool IfcStructuralLoadPlanarForce::hasPlanarForceX() { return !entity->getArgument(1)->isNull(); }
IfcPlanarForceMeasure IfcStructuralLoadPlanarForce::PlanarForceX() { return *entity->getArgument(1); }
bool IfcStructuralLoadPlanarForce::hasPlanarForceY() { return !entity->getArgument(2)->isNull(); }
IfcPlanarForceMeasure IfcStructuralLoadPlanarForce::PlanarForceY() { return *entity->getArgument(2); }
bool IfcStructuralLoadPlanarForce::hasPlanarForceZ() { return !entity->getArgument(3)->isNull(); }
IfcPlanarForceMeasure IfcStructuralLoadPlanarForce::PlanarForceZ() { return *entity->getArgument(3); }
bool IfcStructuralLoadPlanarForce::is(Type::Enum v) const { return v == Type::IfcStructuralLoadPlanarForce || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadPlanarForce::type() const { return Type::IfcStructuralLoadPlanarForce; }
Type::Enum IfcStructuralLoadPlanarForce::Class() { return Type::IfcStructuralLoadPlanarForce; }
IfcStructuralLoadPlanarForce::IfcStructuralLoadPlanarForce(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadPlanarForce)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadSingleDisplacement
bool IfcStructuralLoadSingleDisplacement::hasDisplacementX() { return !entity->getArgument(1)->isNull(); }
IfcLengthMeasure IfcStructuralLoadSingleDisplacement::DisplacementX() { return *entity->getArgument(1); }
bool IfcStructuralLoadSingleDisplacement::hasDisplacementY() { return !entity->getArgument(2)->isNull(); }
IfcLengthMeasure IfcStructuralLoadSingleDisplacement::DisplacementY() { return *entity->getArgument(2); }
bool IfcStructuralLoadSingleDisplacement::hasDisplacementZ() { return !entity->getArgument(3)->isNull(); }
IfcLengthMeasure IfcStructuralLoadSingleDisplacement::DisplacementZ() { return *entity->getArgument(3); }
bool IfcStructuralLoadSingleDisplacement::hasRotationalDisplacementRX() { return !entity->getArgument(4)->isNull(); }
IfcPlaneAngleMeasure IfcStructuralLoadSingleDisplacement::RotationalDisplacementRX() { return *entity->getArgument(4); }
bool IfcStructuralLoadSingleDisplacement::hasRotationalDisplacementRY() { return !entity->getArgument(5)->isNull(); }
IfcPlaneAngleMeasure IfcStructuralLoadSingleDisplacement::RotationalDisplacementRY() { return *entity->getArgument(5); }
bool IfcStructuralLoadSingleDisplacement::hasRotationalDisplacementRZ() { return !entity->getArgument(6)->isNull(); }
IfcPlaneAngleMeasure IfcStructuralLoadSingleDisplacement::RotationalDisplacementRZ() { return *entity->getArgument(6); }
bool IfcStructuralLoadSingleDisplacement::is(Type::Enum v) const { return v == Type::IfcStructuralLoadSingleDisplacement || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadSingleDisplacement::type() const { return Type::IfcStructuralLoadSingleDisplacement; }
Type::Enum IfcStructuralLoadSingleDisplacement::Class() { return Type::IfcStructuralLoadSingleDisplacement; }
IfcStructuralLoadSingleDisplacement::IfcStructuralLoadSingleDisplacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleDisplacement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadSingleDisplacementDistortion
bool IfcStructuralLoadSingleDisplacementDistortion::hasDistortion() { return !entity->getArgument(7)->isNull(); }
IfcCurvatureMeasure IfcStructuralLoadSingleDisplacementDistortion::Distortion() { return *entity->getArgument(7); }
bool IfcStructuralLoadSingleDisplacementDistortion::is(Type::Enum v) const { return v == Type::IfcStructuralLoadSingleDisplacementDistortion || IfcStructuralLoadSingleDisplacement::is(v); }
Type::Enum IfcStructuralLoadSingleDisplacementDistortion::type() const { return Type::IfcStructuralLoadSingleDisplacementDistortion; }
Type::Enum IfcStructuralLoadSingleDisplacementDistortion::Class() { return Type::IfcStructuralLoadSingleDisplacementDistortion; }
IfcStructuralLoadSingleDisplacementDistortion::IfcStructuralLoadSingleDisplacementDistortion(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleDisplacementDistortion)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadSingleForce
bool IfcStructuralLoadSingleForce::hasForceX() { return !entity->getArgument(1)->isNull(); }
IfcForceMeasure IfcStructuralLoadSingleForce::ForceX() { return *entity->getArgument(1); }
bool IfcStructuralLoadSingleForce::hasForceY() { return !entity->getArgument(2)->isNull(); }
IfcForceMeasure IfcStructuralLoadSingleForce::ForceY() { return *entity->getArgument(2); }
bool IfcStructuralLoadSingleForce::hasForceZ() { return !entity->getArgument(3)->isNull(); }
IfcForceMeasure IfcStructuralLoadSingleForce::ForceZ() { return *entity->getArgument(3); }
bool IfcStructuralLoadSingleForce::hasMomentX() { return !entity->getArgument(4)->isNull(); }
IfcTorqueMeasure IfcStructuralLoadSingleForce::MomentX() { return *entity->getArgument(4); }
bool IfcStructuralLoadSingleForce::hasMomentY() { return !entity->getArgument(5)->isNull(); }
IfcTorqueMeasure IfcStructuralLoadSingleForce::MomentY() { return *entity->getArgument(5); }
bool IfcStructuralLoadSingleForce::hasMomentZ() { return !entity->getArgument(6)->isNull(); }
IfcTorqueMeasure IfcStructuralLoadSingleForce::MomentZ() { return *entity->getArgument(6); }
bool IfcStructuralLoadSingleForce::is(Type::Enum v) const { return v == Type::IfcStructuralLoadSingleForce || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadSingleForce::type() const { return Type::IfcStructuralLoadSingleForce; }
Type::Enum IfcStructuralLoadSingleForce::Class() { return Type::IfcStructuralLoadSingleForce; }
IfcStructuralLoadSingleForce::IfcStructuralLoadSingleForce(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleForce)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadSingleForceWarping
bool IfcStructuralLoadSingleForceWarping::hasWarpingMoment() { return !entity->getArgument(7)->isNull(); }
IfcWarpingMomentMeasure IfcStructuralLoadSingleForceWarping::WarpingMoment() { return *entity->getArgument(7); }
bool IfcStructuralLoadSingleForceWarping::is(Type::Enum v) const { return v == Type::IfcStructuralLoadSingleForceWarping || IfcStructuralLoadSingleForce::is(v); }
Type::Enum IfcStructuralLoadSingleForceWarping::type() const { return Type::IfcStructuralLoadSingleForceWarping; }
Type::Enum IfcStructuralLoadSingleForceWarping::Class() { return Type::IfcStructuralLoadSingleForceWarping; }
IfcStructuralLoadSingleForceWarping::IfcStructuralLoadSingleForceWarping(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleForceWarping)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadStatic
bool IfcStructuralLoadStatic::is(Type::Enum v) const { return v == Type::IfcStructuralLoadStatic || IfcStructuralLoad::is(v); }
Type::Enum IfcStructuralLoadStatic::type() const { return Type::IfcStructuralLoadStatic; }
Type::Enum IfcStructuralLoadStatic::Class() { return Type::IfcStructuralLoadStatic; }
IfcStructuralLoadStatic::IfcStructuralLoadStatic(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadStatic)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralLoadTemperature
bool IfcStructuralLoadTemperature::hasDeltaT_Constant() { return !entity->getArgument(1)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcStructuralLoadTemperature::DeltaT_Constant() { return *entity->getArgument(1); }
bool IfcStructuralLoadTemperature::hasDeltaT_Y() { return !entity->getArgument(2)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcStructuralLoadTemperature::DeltaT_Y() { return *entity->getArgument(2); }
bool IfcStructuralLoadTemperature::hasDeltaT_Z() { return !entity->getArgument(3)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcStructuralLoadTemperature::DeltaT_Z() { return *entity->getArgument(3); }
bool IfcStructuralLoadTemperature::is(Type::Enum v) const { return v == Type::IfcStructuralLoadTemperature || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadTemperature::type() const { return Type::IfcStructuralLoadTemperature; }
Type::Enum IfcStructuralLoadTemperature::Class() { return Type::IfcStructuralLoadTemperature; }
IfcStructuralLoadTemperature::IfcStructuralLoadTemperature(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadTemperature)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralMember
IfcRelConnectsStructuralElement::list IfcStructuralMember::ReferencesElement() { RETURN_INVERSE(IfcRelConnectsStructuralElement) }
IfcRelConnectsStructuralMember::list IfcStructuralMember::ConnectedBy() { RETURN_INVERSE(IfcRelConnectsStructuralMember) }
bool IfcStructuralMember::is(Type::Enum v) const { return v == Type::IfcStructuralMember || IfcStructuralItem::is(v); }
Type::Enum IfcStructuralMember::type() const { return Type::IfcStructuralMember; }
Type::Enum IfcStructuralMember::Class() { return Type::IfcStructuralMember; }
IfcStructuralMember::IfcStructuralMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralMember)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralPlanarAction
IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum IfcStructuralPlanarAction::ProjectedOrTrue() { return IfcProjectedOrTrueLengthEnum::FromString(*entity->getArgument(11)); }
bool IfcStructuralPlanarAction::is(Type::Enum v) const { return v == Type::IfcStructuralPlanarAction || IfcStructuralAction::is(v); }
Type::Enum IfcStructuralPlanarAction::type() const { return Type::IfcStructuralPlanarAction; }
Type::Enum IfcStructuralPlanarAction::Class() { return Type::IfcStructuralPlanarAction; }
IfcStructuralPlanarAction::IfcStructuralPlanarAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPlanarAction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralPlanarActionVarying
IfcShapeAspect* IfcStructuralPlanarActionVarying::VaryingAppliedLoadLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(12)); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > IfcStructuralPlanarActionVarying::SubsequentAppliedLoads() { RETURN_AS_LIST(IfcStructuralLoad,13) }
bool IfcStructuralPlanarActionVarying::is(Type::Enum v) const { return v == Type::IfcStructuralPlanarActionVarying || IfcStructuralPlanarAction::is(v); }
Type::Enum IfcStructuralPlanarActionVarying::type() const { return Type::IfcStructuralPlanarActionVarying; }
Type::Enum IfcStructuralPlanarActionVarying::Class() { return Type::IfcStructuralPlanarActionVarying; }
IfcStructuralPlanarActionVarying::IfcStructuralPlanarActionVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPlanarActionVarying)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralPointAction
bool IfcStructuralPointAction::is(Type::Enum v) const { return v == Type::IfcStructuralPointAction || IfcStructuralAction::is(v); }
Type::Enum IfcStructuralPointAction::type() const { return Type::IfcStructuralPointAction; }
Type::Enum IfcStructuralPointAction::Class() { return Type::IfcStructuralPointAction; }
IfcStructuralPointAction::IfcStructuralPointAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPointAction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralPointConnection
bool IfcStructuralPointConnection::is(Type::Enum v) const { return v == Type::IfcStructuralPointConnection || IfcStructuralConnection::is(v); }
Type::Enum IfcStructuralPointConnection::type() const { return Type::IfcStructuralPointConnection; }
Type::Enum IfcStructuralPointConnection::Class() { return Type::IfcStructuralPointConnection; }
IfcStructuralPointConnection::IfcStructuralPointConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPointConnection)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralPointReaction
bool IfcStructuralPointReaction::is(Type::Enum v) const { return v == Type::IfcStructuralPointReaction || IfcStructuralReaction::is(v); }
Type::Enum IfcStructuralPointReaction::type() const { return Type::IfcStructuralPointReaction; }
Type::Enum IfcStructuralPointReaction::Class() { return Type::IfcStructuralPointReaction; }
IfcStructuralPointReaction::IfcStructuralPointReaction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPointReaction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralProfileProperties
bool IfcStructuralProfileProperties::hasTorsionalConstantX() { return !entity->getArgument(7)->isNull(); }
IfcMomentOfInertiaMeasure IfcStructuralProfileProperties::TorsionalConstantX() { return *entity->getArgument(7); }
bool IfcStructuralProfileProperties::hasMomentOfInertiaYZ() { return !entity->getArgument(8)->isNull(); }
IfcMomentOfInertiaMeasure IfcStructuralProfileProperties::MomentOfInertiaYZ() { return *entity->getArgument(8); }
bool IfcStructuralProfileProperties::hasMomentOfInertiaY() { return !entity->getArgument(9)->isNull(); }
IfcMomentOfInertiaMeasure IfcStructuralProfileProperties::MomentOfInertiaY() { return *entity->getArgument(9); }
bool IfcStructuralProfileProperties::hasMomentOfInertiaZ() { return !entity->getArgument(10)->isNull(); }
IfcMomentOfInertiaMeasure IfcStructuralProfileProperties::MomentOfInertiaZ() { return *entity->getArgument(10); }
bool IfcStructuralProfileProperties::hasWarpingConstant() { return !entity->getArgument(11)->isNull(); }
IfcWarpingConstantMeasure IfcStructuralProfileProperties::WarpingConstant() { return *entity->getArgument(11); }
bool IfcStructuralProfileProperties::hasShearCentreZ() { return !entity->getArgument(12)->isNull(); }
IfcLengthMeasure IfcStructuralProfileProperties::ShearCentreZ() { return *entity->getArgument(12); }
bool IfcStructuralProfileProperties::hasShearCentreY() { return !entity->getArgument(13)->isNull(); }
IfcLengthMeasure IfcStructuralProfileProperties::ShearCentreY() { return *entity->getArgument(13); }
bool IfcStructuralProfileProperties::hasShearDeformationAreaZ() { return !entity->getArgument(14)->isNull(); }
IfcAreaMeasure IfcStructuralProfileProperties::ShearDeformationAreaZ() { return *entity->getArgument(14); }
bool IfcStructuralProfileProperties::hasShearDeformationAreaY() { return !entity->getArgument(15)->isNull(); }
IfcAreaMeasure IfcStructuralProfileProperties::ShearDeformationAreaY() { return *entity->getArgument(15); }
bool IfcStructuralProfileProperties::hasMaximumSectionModulusY() { return !entity->getArgument(16)->isNull(); }
IfcSectionModulusMeasure IfcStructuralProfileProperties::MaximumSectionModulusY() { return *entity->getArgument(16); }
bool IfcStructuralProfileProperties::hasMinimumSectionModulusY() { return !entity->getArgument(17)->isNull(); }
IfcSectionModulusMeasure IfcStructuralProfileProperties::MinimumSectionModulusY() { return *entity->getArgument(17); }
bool IfcStructuralProfileProperties::hasMaximumSectionModulusZ() { return !entity->getArgument(18)->isNull(); }
IfcSectionModulusMeasure IfcStructuralProfileProperties::MaximumSectionModulusZ() { return *entity->getArgument(18); }
bool IfcStructuralProfileProperties::hasMinimumSectionModulusZ() { return !entity->getArgument(19)->isNull(); }
IfcSectionModulusMeasure IfcStructuralProfileProperties::MinimumSectionModulusZ() { return *entity->getArgument(19); }
bool IfcStructuralProfileProperties::hasTorsionalSectionModulus() { return !entity->getArgument(20)->isNull(); }
IfcSectionModulusMeasure IfcStructuralProfileProperties::TorsionalSectionModulus() { return *entity->getArgument(20); }
bool IfcStructuralProfileProperties::hasCentreOfGravityInX() { return !entity->getArgument(21)->isNull(); }
IfcLengthMeasure IfcStructuralProfileProperties::CentreOfGravityInX() { return *entity->getArgument(21); }
bool IfcStructuralProfileProperties::hasCentreOfGravityInY() { return !entity->getArgument(22)->isNull(); }
IfcLengthMeasure IfcStructuralProfileProperties::CentreOfGravityInY() { return *entity->getArgument(22); }
bool IfcStructuralProfileProperties::is(Type::Enum v) const { return v == Type::IfcStructuralProfileProperties || IfcGeneralProfileProperties::is(v); }
Type::Enum IfcStructuralProfileProperties::type() const { return Type::IfcStructuralProfileProperties; }
Type::Enum IfcStructuralProfileProperties::Class() { return Type::IfcStructuralProfileProperties; }
IfcStructuralProfileProperties::IfcStructuralProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralProfileProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralReaction
IfcStructuralAction::list IfcStructuralReaction::Causes() { RETURN_INVERSE(IfcStructuralAction) }
bool IfcStructuralReaction::is(Type::Enum v) const { return v == Type::IfcStructuralReaction || IfcStructuralActivity::is(v); }
Type::Enum IfcStructuralReaction::type() const { return Type::IfcStructuralReaction; }
Type::Enum IfcStructuralReaction::Class() { return Type::IfcStructuralReaction; }
IfcStructuralReaction::IfcStructuralReaction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralReaction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralResultGroup
IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryTypeEnum IfcStructuralResultGroup::TheoryType() { return IfcAnalysisTheoryTypeEnum::FromString(*entity->getArgument(5)); }
bool IfcStructuralResultGroup::hasResultForLoadGroup() { return !entity->getArgument(6)->isNull(); }
IfcStructuralLoadGroup* IfcStructuralResultGroup::ResultForLoadGroup() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralLoadGroup>(*entity->getArgument(6)); }
bool IfcStructuralResultGroup::IsLinear() { return *entity->getArgument(7); }
IfcStructuralAnalysisModel::list IfcStructuralResultGroup::ResultGroupFor() { RETURN_INVERSE(IfcStructuralAnalysisModel) }
bool IfcStructuralResultGroup::is(Type::Enum v) const { return v == Type::IfcStructuralResultGroup || IfcGroup::is(v); }
Type::Enum IfcStructuralResultGroup::type() const { return Type::IfcStructuralResultGroup; }
Type::Enum IfcStructuralResultGroup::Class() { return Type::IfcStructuralResultGroup; }
IfcStructuralResultGroup::IfcStructuralResultGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralResultGroup)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralSteelProfileProperties
bool IfcStructuralSteelProfileProperties::hasShearAreaZ() { return !entity->getArgument(23)->isNull(); }
IfcAreaMeasure IfcStructuralSteelProfileProperties::ShearAreaZ() { return *entity->getArgument(23); }
bool IfcStructuralSteelProfileProperties::hasShearAreaY() { return !entity->getArgument(24)->isNull(); }
IfcAreaMeasure IfcStructuralSteelProfileProperties::ShearAreaY() { return *entity->getArgument(24); }
bool IfcStructuralSteelProfileProperties::hasPlasticShapeFactorY() { return !entity->getArgument(25)->isNull(); }
IfcPositiveRatioMeasure IfcStructuralSteelProfileProperties::PlasticShapeFactorY() { return *entity->getArgument(25); }
bool IfcStructuralSteelProfileProperties::hasPlasticShapeFactorZ() { return !entity->getArgument(26)->isNull(); }
IfcPositiveRatioMeasure IfcStructuralSteelProfileProperties::PlasticShapeFactorZ() { return *entity->getArgument(26); }
bool IfcStructuralSteelProfileProperties::is(Type::Enum v) const { return v == Type::IfcStructuralSteelProfileProperties || IfcStructuralProfileProperties::is(v); }
Type::Enum IfcStructuralSteelProfileProperties::type() const { return Type::IfcStructuralSteelProfileProperties; }
Type::Enum IfcStructuralSteelProfileProperties::Class() { return Type::IfcStructuralSteelProfileProperties; }
IfcStructuralSteelProfileProperties::IfcStructuralSteelProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSteelProfileProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralSurfaceConnection
bool IfcStructuralSurfaceConnection::is(Type::Enum v) const { return v == Type::IfcStructuralSurfaceConnection || IfcStructuralConnection::is(v); }
Type::Enum IfcStructuralSurfaceConnection::type() const { return Type::IfcStructuralSurfaceConnection; }
Type::Enum IfcStructuralSurfaceConnection::Class() { return Type::IfcStructuralSurfaceConnection; }
IfcStructuralSurfaceConnection::IfcStructuralSurfaceConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSurfaceConnection)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralSurfaceMember
IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceTypeEnum IfcStructuralSurfaceMember::PredefinedType() { return IfcStructuralSurfaceTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcStructuralSurfaceMember::hasThickness() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcStructuralSurfaceMember::Thickness() { return *entity->getArgument(8); }
bool IfcStructuralSurfaceMember::is(Type::Enum v) const { return v == Type::IfcStructuralSurfaceMember || IfcStructuralMember::is(v); }
Type::Enum IfcStructuralSurfaceMember::type() const { return Type::IfcStructuralSurfaceMember; }
Type::Enum IfcStructuralSurfaceMember::Class() { return Type::IfcStructuralSurfaceMember; }
IfcStructuralSurfaceMember::IfcStructuralSurfaceMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSurfaceMember)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuralSurfaceMemberVarying
std::vector<IfcPositiveLengthMeasure> /*[2:?]*/ IfcStructuralSurfaceMemberVarying::SubsequentThickness() { return *entity->getArgument(9); }
IfcShapeAspect* IfcStructuralSurfaceMemberVarying::VaryingThicknessLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(10)); }
bool IfcStructuralSurfaceMemberVarying::is(Type::Enum v) const { return v == Type::IfcStructuralSurfaceMemberVarying || IfcStructuralSurfaceMember::is(v); }
Type::Enum IfcStructuralSurfaceMemberVarying::type() const { return Type::IfcStructuralSurfaceMemberVarying; }
Type::Enum IfcStructuralSurfaceMemberVarying::Class() { return Type::IfcStructuralSurfaceMemberVarying; }
IfcStructuralSurfaceMemberVarying::IfcStructuralSurfaceMemberVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSurfaceMemberVarying)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStructuredDimensionCallout
bool IfcStructuredDimensionCallout::is(Type::Enum v) const { return v == Type::IfcStructuredDimensionCallout || IfcDraughtingCallout::is(v); }
Type::Enum IfcStructuredDimensionCallout::type() const { return Type::IfcStructuredDimensionCallout; }
Type::Enum IfcStructuredDimensionCallout::Class() { return Type::IfcStructuredDimensionCallout; }
IfcStructuredDimensionCallout::IfcStructuredDimensionCallout(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuredDimensionCallout)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStyleModel
bool IfcStyleModel::is(Type::Enum v) const { return v == Type::IfcStyleModel || IfcRepresentation::is(v); }
Type::Enum IfcStyleModel::type() const { return Type::IfcStyleModel; }
Type::Enum IfcStyleModel::Class() { return Type::IfcStyleModel; }
IfcStyleModel::IfcStyleModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcStyleModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStyledItem
bool IfcStyledItem::hasItem() { return !entity->getArgument(0)->isNull(); }
IfcRepresentationItem* IfcStyledItem::Item() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentationItem>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcPresentationStyleAssignment> > IfcStyledItem::Styles() { RETURN_AS_LIST(IfcPresentationStyleAssignment,1) }
bool IfcStyledItem::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcStyledItem::Name() { return *entity->getArgument(2); }
bool IfcStyledItem::is(Type::Enum v) const { return v == Type::IfcStyledItem || IfcRepresentationItem::is(v); }
Type::Enum IfcStyledItem::type() const { return Type::IfcStyledItem; }
Type::Enum IfcStyledItem::Class() { return Type::IfcStyledItem; }
IfcStyledItem::IfcStyledItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcStyledItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcStyledRepresentation
bool IfcStyledRepresentation::is(Type::Enum v) const { return v == Type::IfcStyledRepresentation || IfcStyleModel::is(v); }
Type::Enum IfcStyledRepresentation::type() const { return Type::IfcStyledRepresentation; }
Type::Enum IfcStyledRepresentation::Class() { return Type::IfcStyledRepresentation; }
IfcStyledRepresentation::IfcStyledRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcStyledRepresentation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSubContractResource
bool IfcSubContractResource::hasSubContractor() { return !entity->getArgument(9)->isNull(); }
IfcActorSelect IfcSubContractResource::SubContractor() { return *entity->getArgument(9); }
bool IfcSubContractResource::hasJobDescription() { return !entity->getArgument(10)->isNull(); }
IfcText IfcSubContractResource::JobDescription() { return *entity->getArgument(10); }
bool IfcSubContractResource::is(Type::Enum v) const { return v == Type::IfcSubContractResource || IfcConstructionResource::is(v); }
Type::Enum IfcSubContractResource::type() const { return Type::IfcSubContractResource; }
Type::Enum IfcSubContractResource::Class() { return Type::IfcSubContractResource; }
IfcSubContractResource::IfcSubContractResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcSubContractResource)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSubedge
IfcEdge* IfcSubedge::ParentEdge() { return reinterpret_pointer_cast<IfcBaseClass,IfcEdge>(*entity->getArgument(2)); }
bool IfcSubedge::is(Type::Enum v) const { return v == Type::IfcSubedge || IfcEdge::is(v); }
Type::Enum IfcSubedge::type() const { return Type::IfcSubedge; }
Type::Enum IfcSubedge::Class() { return Type::IfcSubedge; }
IfcSubedge::IfcSubedge(IfcAbstractEntityPtr e) { if (!is(Type::IfcSubedge)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurface
bool IfcSurface::is(Type::Enum v) const { return v == Type::IfcSurface || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcSurface::type() const { return Type::IfcSurface; }
Type::Enum IfcSurface::Class() { return Type::IfcSurface; }
IfcSurface::IfcSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceCurveSweptAreaSolid
IfcCurve* IfcSurfaceCurveSweptAreaSolid::Directrix() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
IfcParameterValue IfcSurfaceCurveSweptAreaSolid::StartParam() { return *entity->getArgument(3); }
IfcParameterValue IfcSurfaceCurveSweptAreaSolid::EndParam() { return *entity->getArgument(4); }
IfcSurface* IfcSurfaceCurveSweptAreaSolid::ReferenceSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(5)); }
bool IfcSurfaceCurveSweptAreaSolid::is(Type::Enum v) const { return v == Type::IfcSurfaceCurveSweptAreaSolid || IfcSweptAreaSolid::is(v); }
Type::Enum IfcSurfaceCurveSweptAreaSolid::type() const { return Type::IfcSurfaceCurveSweptAreaSolid; }
Type::Enum IfcSurfaceCurveSweptAreaSolid::Class() { return Type::IfcSurfaceCurveSweptAreaSolid; }
IfcSurfaceCurveSweptAreaSolid::IfcSurfaceCurveSweptAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceCurveSweptAreaSolid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceOfLinearExtrusion
IfcDirection* IfcSurfaceOfLinearExtrusion::ExtrudedDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(2)); }
IfcLengthMeasure IfcSurfaceOfLinearExtrusion::Depth() { return *entity->getArgument(3); }
bool IfcSurfaceOfLinearExtrusion::is(Type::Enum v) const { return v == Type::IfcSurfaceOfLinearExtrusion || IfcSweptSurface::is(v); }
Type::Enum IfcSurfaceOfLinearExtrusion::type() const { return Type::IfcSurfaceOfLinearExtrusion; }
Type::Enum IfcSurfaceOfLinearExtrusion::Class() { return Type::IfcSurfaceOfLinearExtrusion; }
IfcSurfaceOfLinearExtrusion::IfcSurfaceOfLinearExtrusion(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceOfLinearExtrusion)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceOfRevolution
IfcAxis1Placement* IfcSurfaceOfRevolution::AxisPosition() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis1Placement>(*entity->getArgument(2)); }
bool IfcSurfaceOfRevolution::is(Type::Enum v) const { return v == Type::IfcSurfaceOfRevolution || IfcSweptSurface::is(v); }
Type::Enum IfcSurfaceOfRevolution::type() const { return Type::IfcSurfaceOfRevolution; }
Type::Enum IfcSurfaceOfRevolution::Class() { return Type::IfcSurfaceOfRevolution; }
IfcSurfaceOfRevolution::IfcSurfaceOfRevolution(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceOfRevolution)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceStyle
IfcSurfaceSide::IfcSurfaceSide IfcSurfaceStyle::Side() { return IfcSurfaceSide::FromString(*entity->getArgument(1)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcSurfaceStyle::Styles() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcSurfaceStyle::is(Type::Enum v) const { return v == Type::IfcSurfaceStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcSurfaceStyle::type() const { return Type::IfcSurfaceStyle; }
Type::Enum IfcSurfaceStyle::Class() { return Type::IfcSurfaceStyle; }
IfcSurfaceStyle::IfcSurfaceStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceStyleLighting
IfcColourRgb* IfcSurfaceStyleLighting::DiffuseTransmissionColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(0)); }
IfcColourRgb* IfcSurfaceStyleLighting::DiffuseReflectionColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(1)); }
IfcColourRgb* IfcSurfaceStyleLighting::TransmissionColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(2)); }
IfcColourRgb* IfcSurfaceStyleLighting::ReflectanceColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(3)); }
bool IfcSurfaceStyleLighting::is(Type::Enum v) const { return v == Type::IfcSurfaceStyleLighting; }
Type::Enum IfcSurfaceStyleLighting::type() const { return Type::IfcSurfaceStyleLighting; }
Type::Enum IfcSurfaceStyleLighting::Class() { return Type::IfcSurfaceStyleLighting; }
IfcSurfaceStyleLighting::IfcSurfaceStyleLighting(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleLighting)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceStyleRefraction
bool IfcSurfaceStyleRefraction::hasRefractionIndex() { return !entity->getArgument(0)->isNull(); }
IfcReal IfcSurfaceStyleRefraction::RefractionIndex() { return *entity->getArgument(0); }
bool IfcSurfaceStyleRefraction::hasDispersionFactor() { return !entity->getArgument(1)->isNull(); }
IfcReal IfcSurfaceStyleRefraction::DispersionFactor() { return *entity->getArgument(1); }
bool IfcSurfaceStyleRefraction::is(Type::Enum v) const { return v == Type::IfcSurfaceStyleRefraction; }
Type::Enum IfcSurfaceStyleRefraction::type() const { return Type::IfcSurfaceStyleRefraction; }
Type::Enum IfcSurfaceStyleRefraction::Class() { return Type::IfcSurfaceStyleRefraction; }
IfcSurfaceStyleRefraction::IfcSurfaceStyleRefraction(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleRefraction)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceStyleRendering
bool IfcSurfaceStyleRendering::hasTransparency() { return !entity->getArgument(1)->isNull(); }
IfcNormalisedRatioMeasure IfcSurfaceStyleRendering::Transparency() { return *entity->getArgument(1); }
bool IfcSurfaceStyleRendering::hasDiffuseColour() { return !entity->getArgument(2)->isNull(); }
IfcColourOrFactor IfcSurfaceStyleRendering::DiffuseColour() { return *entity->getArgument(2); }
bool IfcSurfaceStyleRendering::hasTransmissionColour() { return !entity->getArgument(3)->isNull(); }
IfcColourOrFactor IfcSurfaceStyleRendering::TransmissionColour() { return *entity->getArgument(3); }
bool IfcSurfaceStyleRendering::hasDiffuseTransmissionColour() { return !entity->getArgument(4)->isNull(); }
IfcColourOrFactor IfcSurfaceStyleRendering::DiffuseTransmissionColour() { return *entity->getArgument(4); }
bool IfcSurfaceStyleRendering::hasReflectionColour() { return !entity->getArgument(5)->isNull(); }
IfcColourOrFactor IfcSurfaceStyleRendering::ReflectionColour() { return *entity->getArgument(5); }
bool IfcSurfaceStyleRendering::hasSpecularColour() { return !entity->getArgument(6)->isNull(); }
IfcColourOrFactor IfcSurfaceStyleRendering::SpecularColour() { return *entity->getArgument(6); }
bool IfcSurfaceStyleRendering::hasSpecularHighlight() { return !entity->getArgument(7)->isNull(); }
IfcSpecularHighlightSelect IfcSurfaceStyleRendering::SpecularHighlight() { return *entity->getArgument(7); }
IfcReflectanceMethodEnum::IfcReflectanceMethodEnum IfcSurfaceStyleRendering::ReflectanceMethod() { return IfcReflectanceMethodEnum::FromString(*entity->getArgument(8)); }
bool IfcSurfaceStyleRendering::is(Type::Enum v) const { return v == Type::IfcSurfaceStyleRendering || IfcSurfaceStyleShading::is(v); }
Type::Enum IfcSurfaceStyleRendering::type() const { return Type::IfcSurfaceStyleRendering; }
Type::Enum IfcSurfaceStyleRendering::Class() { return Type::IfcSurfaceStyleRendering; }
IfcSurfaceStyleRendering::IfcSurfaceStyleRendering(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleRendering)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceStyleShading
IfcColourRgb* IfcSurfaceStyleShading::SurfaceColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(0)); }
bool IfcSurfaceStyleShading::is(Type::Enum v) const { return v == Type::IfcSurfaceStyleShading; }
Type::Enum IfcSurfaceStyleShading::type() const { return Type::IfcSurfaceStyleShading; }
Type::Enum IfcSurfaceStyleShading::Class() { return Type::IfcSurfaceStyleShading; }
IfcSurfaceStyleShading::IfcSurfaceStyleShading(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleShading)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceStyleWithTextures
SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceTexture> > IfcSurfaceStyleWithTextures::Textures() { RETURN_AS_LIST(IfcSurfaceTexture,0) }
bool IfcSurfaceStyleWithTextures::is(Type::Enum v) const { return v == Type::IfcSurfaceStyleWithTextures; }
Type::Enum IfcSurfaceStyleWithTextures::type() const { return Type::IfcSurfaceStyleWithTextures; }
Type::Enum IfcSurfaceStyleWithTextures::Class() { return Type::IfcSurfaceStyleWithTextures; }
IfcSurfaceStyleWithTextures::IfcSurfaceStyleWithTextures(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleWithTextures)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSurfaceTexture
bool IfcSurfaceTexture::RepeatS() { return *entity->getArgument(0); }
bool IfcSurfaceTexture::RepeatT() { return *entity->getArgument(1); }
IfcSurfaceTextureEnum::IfcSurfaceTextureEnum IfcSurfaceTexture::TextureType() { return IfcSurfaceTextureEnum::FromString(*entity->getArgument(2)); }
bool IfcSurfaceTexture::hasTextureTransform() { return !entity->getArgument(3)->isNull(); }
IfcCartesianTransformationOperator2D* IfcSurfaceTexture::TextureTransform() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator2D>(*entity->getArgument(3)); }
bool IfcSurfaceTexture::is(Type::Enum v) const { return v == Type::IfcSurfaceTexture; }
Type::Enum IfcSurfaceTexture::type() const { return Type::IfcSurfaceTexture; }
Type::Enum IfcSurfaceTexture::Class() { return Type::IfcSurfaceTexture; }
IfcSurfaceTexture::IfcSurfaceTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceTexture)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSweptAreaSolid
IfcProfileDef* IfcSweptAreaSolid::SweptArea() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(0)); }
IfcAxis2Placement3D* IfcSweptAreaSolid::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(1)); }
bool IfcSweptAreaSolid::is(Type::Enum v) const { return v == Type::IfcSweptAreaSolid || IfcSolidModel::is(v); }
Type::Enum IfcSweptAreaSolid::type() const { return Type::IfcSweptAreaSolid; }
Type::Enum IfcSweptAreaSolid::Class() { return Type::IfcSweptAreaSolid; }
IfcSweptAreaSolid::IfcSweptAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcSweptAreaSolid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSweptDiskSolid
IfcCurve* IfcSweptDiskSolid::Directrix() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcPositiveLengthMeasure IfcSweptDiskSolid::Radius() { return *entity->getArgument(1); }
bool IfcSweptDiskSolid::hasInnerRadius() { return !entity->getArgument(2)->isNull(); }
IfcPositiveLengthMeasure IfcSweptDiskSolid::InnerRadius() { return *entity->getArgument(2); }
IfcParameterValue IfcSweptDiskSolid::StartParam() { return *entity->getArgument(3); }
IfcParameterValue IfcSweptDiskSolid::EndParam() { return *entity->getArgument(4); }
bool IfcSweptDiskSolid::is(Type::Enum v) const { return v == Type::IfcSweptDiskSolid || IfcSolidModel::is(v); }
Type::Enum IfcSweptDiskSolid::type() const { return Type::IfcSweptDiskSolid; }
Type::Enum IfcSweptDiskSolid::Class() { return Type::IfcSweptDiskSolid; }
IfcSweptDiskSolid::IfcSweptDiskSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcSweptDiskSolid)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSweptSurface
IfcProfileDef* IfcSweptSurface::SweptCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(0)); }
IfcAxis2Placement3D* IfcSweptSurface::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(1)); }
bool IfcSweptSurface::is(Type::Enum v) const { return v == Type::IfcSweptSurface || IfcSurface::is(v); }
Type::Enum IfcSweptSurface::type() const { return Type::IfcSweptSurface; }
Type::Enum IfcSweptSurface::Class() { return Type::IfcSweptSurface; }
IfcSweptSurface::IfcSweptSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcSweptSurface)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSwitchingDeviceType
IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceTypeEnum IfcSwitchingDeviceType::PredefinedType() { return IfcSwitchingDeviceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSwitchingDeviceType::is(Type::Enum v) const { return v == Type::IfcSwitchingDeviceType || IfcFlowControllerType::is(v); }
Type::Enum IfcSwitchingDeviceType::type() const { return Type::IfcSwitchingDeviceType; }
Type::Enum IfcSwitchingDeviceType::Class() { return Type::IfcSwitchingDeviceType; }
IfcSwitchingDeviceType::IfcSwitchingDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSwitchingDeviceType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSymbolStyle
IfcSymbolStyleSelect IfcSymbolStyle::StyleOfSymbol() { return *entity->getArgument(1); }
bool IfcSymbolStyle::is(Type::Enum v) const { return v == Type::IfcSymbolStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcSymbolStyle::type() const { return Type::IfcSymbolStyle; }
Type::Enum IfcSymbolStyle::Class() { return Type::IfcSymbolStyle; }
IfcSymbolStyle::IfcSymbolStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcSymbolStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSystem
IfcRelServicesBuildings::list IfcSystem::ServicesBuildings() { RETURN_INVERSE(IfcRelServicesBuildings) }
bool IfcSystem::is(Type::Enum v) const { return v == Type::IfcSystem || IfcGroup::is(v); }
Type::Enum IfcSystem::type() const { return Type::IfcSystem; }
Type::Enum IfcSystem::Class() { return Type::IfcSystem; }
IfcSystem::IfcSystem(IfcAbstractEntityPtr e) { if (!is(Type::IfcSystem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcSystemFurnitureElementType
bool IfcSystemFurnitureElementType::is(Type::Enum v) const { return v == Type::IfcSystemFurnitureElementType || IfcFurnishingElementType::is(v); }
Type::Enum IfcSystemFurnitureElementType::type() const { return Type::IfcSystemFurnitureElementType; }
Type::Enum IfcSystemFurnitureElementType::Class() { return Type::IfcSystemFurnitureElementType; }
IfcSystemFurnitureElementType::IfcSystemFurnitureElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSystemFurnitureElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTShapeProfileDef
IfcPositiveLengthMeasure IfcTShapeProfileDef::Depth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcTShapeProfileDef::FlangeWidth() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcTShapeProfileDef::WebThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcTShapeProfileDef::FlangeThickness() { return *entity->getArgument(6); }
bool IfcTShapeProfileDef::hasFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcTShapeProfileDef::FilletRadius() { return *entity->getArgument(7); }
bool IfcTShapeProfileDef::hasFlangeEdgeRadius() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcTShapeProfileDef::FlangeEdgeRadius() { return *entity->getArgument(8); }
bool IfcTShapeProfileDef::hasWebEdgeRadius() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcTShapeProfileDef::WebEdgeRadius() { return *entity->getArgument(9); }
bool IfcTShapeProfileDef::hasWebSlope() { return !entity->getArgument(10)->isNull(); }
IfcPlaneAngleMeasure IfcTShapeProfileDef::WebSlope() { return *entity->getArgument(10); }
bool IfcTShapeProfileDef::hasFlangeSlope() { return !entity->getArgument(11)->isNull(); }
IfcPlaneAngleMeasure IfcTShapeProfileDef::FlangeSlope() { return *entity->getArgument(11); }
bool IfcTShapeProfileDef::hasCentreOfGravityInY() { return !entity->getArgument(12)->isNull(); }
IfcPositiveLengthMeasure IfcTShapeProfileDef::CentreOfGravityInY() { return *entity->getArgument(12); }
bool IfcTShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcTShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcTShapeProfileDef::type() const { return Type::IfcTShapeProfileDef; }
Type::Enum IfcTShapeProfileDef::Class() { return Type::IfcTShapeProfileDef; }
IfcTShapeProfileDef::IfcTShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcTShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTable
std::string IfcTable::Name() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcTableRow> > IfcTable::Rows() { RETURN_AS_LIST(IfcTableRow,1) }
bool IfcTable::is(Type::Enum v) const { return v == Type::IfcTable; }
Type::Enum IfcTable::type() const { return Type::IfcTable; }
Type::Enum IfcTable::Class() { return Type::IfcTable; }
IfcTable::IfcTable(IfcAbstractEntityPtr e) { if (!is(Type::IfcTable)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTableRow
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTableRow::RowCells() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcTableRow::IsHeading() { return *entity->getArgument(1); }
IfcTable::list IfcTableRow::OfTable() { RETURN_INVERSE(IfcTable) }
bool IfcTableRow::is(Type::Enum v) const { return v == Type::IfcTableRow; }
Type::Enum IfcTableRow::type() const { return Type::IfcTableRow; }
Type::Enum IfcTableRow::Class() { return Type::IfcTableRow; }
IfcTableRow::IfcTableRow(IfcAbstractEntityPtr e) { if (!is(Type::IfcTableRow)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTankType
IfcTankTypeEnum::IfcTankTypeEnum IfcTankType::PredefinedType() { return IfcTankTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTankType::is(Type::Enum v) const { return v == Type::IfcTankType || IfcFlowStorageDeviceType::is(v); }
Type::Enum IfcTankType::type() const { return Type::IfcTankType; }
Type::Enum IfcTankType::Class() { return Type::IfcTankType; }
IfcTankType::IfcTankType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTankType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTask
IfcIdentifier IfcTask::TaskId() { return *entity->getArgument(5); }
bool IfcTask::hasStatus() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcTask::Status() { return *entity->getArgument(6); }
bool IfcTask::hasWorkMethod() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcTask::WorkMethod() { return *entity->getArgument(7); }
bool IfcTask::IsMilestone() { return *entity->getArgument(8); }
bool IfcTask::hasPriority() { return !entity->getArgument(9)->isNull(); }
int IfcTask::Priority() { return *entity->getArgument(9); }
bool IfcTask::is(Type::Enum v) const { return v == Type::IfcTask || IfcProcess::is(v); }
Type::Enum IfcTask::type() const { return Type::IfcTask; }
Type::Enum IfcTask::Class() { return Type::IfcTask; }
IfcTask::IfcTask(IfcAbstractEntityPtr e) { if (!is(Type::IfcTask)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTelecomAddress
bool IfcTelecomAddress::hasTelephoneNumbers() { return !entity->getArgument(3)->isNull(); }
std::vector<IfcLabel> /*[1:?]*/ IfcTelecomAddress::TelephoneNumbers() { return *entity->getArgument(3); }
bool IfcTelecomAddress::hasFacsimileNumbers() { return !entity->getArgument(4)->isNull(); }
std::vector<IfcLabel> /*[1:?]*/ IfcTelecomAddress::FacsimileNumbers() { return *entity->getArgument(4); }
bool IfcTelecomAddress::hasPagerNumber() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcTelecomAddress::PagerNumber() { return *entity->getArgument(5); }
bool IfcTelecomAddress::hasElectronicMailAddresses() { return !entity->getArgument(6)->isNull(); }
std::vector<IfcLabel> /*[1:?]*/ IfcTelecomAddress::ElectronicMailAddresses() { return *entity->getArgument(6); }
bool IfcTelecomAddress::hasWWWHomePageURL() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcTelecomAddress::WWWHomePageURL() { return *entity->getArgument(7); }
bool IfcTelecomAddress::is(Type::Enum v) const { return v == Type::IfcTelecomAddress || IfcAddress::is(v); }
Type::Enum IfcTelecomAddress::type() const { return Type::IfcTelecomAddress; }
Type::Enum IfcTelecomAddress::Class() { return Type::IfcTelecomAddress; }
IfcTelecomAddress::IfcTelecomAddress(IfcAbstractEntityPtr e) { if (!is(Type::IfcTelecomAddress)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTendon
IfcTendonTypeEnum::IfcTendonTypeEnum IfcTendon::PredefinedType() { return IfcTendonTypeEnum::FromString(*entity->getArgument(9)); }
IfcPositiveLengthMeasure IfcTendon::NominalDiameter() { return *entity->getArgument(10); }
IfcAreaMeasure IfcTendon::CrossSectionArea() { return *entity->getArgument(11); }
bool IfcTendon::hasTensionForce() { return !entity->getArgument(12)->isNull(); }
IfcForceMeasure IfcTendon::TensionForce() { return *entity->getArgument(12); }
bool IfcTendon::hasPreStress() { return !entity->getArgument(13)->isNull(); }
IfcPressureMeasure IfcTendon::PreStress() { return *entity->getArgument(13); }
bool IfcTendon::hasFrictionCoefficient() { return !entity->getArgument(14)->isNull(); }
IfcNormalisedRatioMeasure IfcTendon::FrictionCoefficient() { return *entity->getArgument(14); }
bool IfcTendon::hasAnchorageSlip() { return !entity->getArgument(15)->isNull(); }
IfcPositiveLengthMeasure IfcTendon::AnchorageSlip() { return *entity->getArgument(15); }
bool IfcTendon::hasMinCurvatureRadius() { return !entity->getArgument(16)->isNull(); }
IfcPositiveLengthMeasure IfcTendon::MinCurvatureRadius() { return *entity->getArgument(16); }
bool IfcTendon::is(Type::Enum v) const { return v == Type::IfcTendon || IfcReinforcingElement::is(v); }
Type::Enum IfcTendon::type() const { return Type::IfcTendon; }
Type::Enum IfcTendon::Class() { return Type::IfcTendon; }
IfcTendon::IfcTendon(IfcAbstractEntityPtr e) { if (!is(Type::IfcTendon)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTendonAnchor
bool IfcTendonAnchor::is(Type::Enum v) const { return v == Type::IfcTendonAnchor || IfcReinforcingElement::is(v); }
Type::Enum IfcTendonAnchor::type() const { return Type::IfcTendonAnchor; }
Type::Enum IfcTendonAnchor::Class() { return Type::IfcTendonAnchor; }
IfcTendonAnchor::IfcTendonAnchor(IfcAbstractEntityPtr e) { if (!is(Type::IfcTendonAnchor)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTerminatorSymbol
IfcAnnotationCurveOccurrence* IfcTerminatorSymbol::AnnotatedCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcAnnotationCurveOccurrence>(*entity->getArgument(3)); }
bool IfcTerminatorSymbol::is(Type::Enum v) const { return v == Type::IfcTerminatorSymbol || IfcAnnotationSymbolOccurrence::is(v); }
Type::Enum IfcTerminatorSymbol::type() const { return Type::IfcTerminatorSymbol; }
Type::Enum IfcTerminatorSymbol::Class() { return Type::IfcTerminatorSymbol; }
IfcTerminatorSymbol::IfcTerminatorSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcTerminatorSymbol)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextLiteral
IfcPresentableText IfcTextLiteral::Literal() { return *entity->getArgument(0); }
IfcAxis2Placement IfcTextLiteral::Placement() { return *entity->getArgument(1); }
IfcTextPath::IfcTextPath IfcTextLiteral::Path() { return IfcTextPath::FromString(*entity->getArgument(2)); }
bool IfcTextLiteral::is(Type::Enum v) const { return v == Type::IfcTextLiteral || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcTextLiteral::type() const { return Type::IfcTextLiteral; }
Type::Enum IfcTextLiteral::Class() { return Type::IfcTextLiteral; }
IfcTextLiteral::IfcTextLiteral(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextLiteral)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextLiteralWithExtent
IfcPlanarExtent* IfcTextLiteralWithExtent::Extent() { return reinterpret_pointer_cast<IfcBaseClass,IfcPlanarExtent>(*entity->getArgument(3)); }
IfcBoxAlignment IfcTextLiteralWithExtent::BoxAlignment() { return *entity->getArgument(4); }
bool IfcTextLiteralWithExtent::is(Type::Enum v) const { return v == Type::IfcTextLiteralWithExtent || IfcTextLiteral::is(v); }
Type::Enum IfcTextLiteralWithExtent::type() const { return Type::IfcTextLiteralWithExtent; }
Type::Enum IfcTextLiteralWithExtent::Class() { return Type::IfcTextLiteralWithExtent; }
IfcTextLiteralWithExtent::IfcTextLiteralWithExtent(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextLiteralWithExtent)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextStyle
bool IfcTextStyle::hasTextCharacterAppearance() { return !entity->getArgument(1)->isNull(); }
IfcCharacterStyleSelect IfcTextStyle::TextCharacterAppearance() { return *entity->getArgument(1); }
bool IfcTextStyle::hasTextStyle() { return !entity->getArgument(2)->isNull(); }
IfcTextStyleSelect IfcTextStyle::TextStyle() { return *entity->getArgument(2); }
IfcTextFontSelect IfcTextStyle::TextFontStyle() { return *entity->getArgument(3); }
bool IfcTextStyle::is(Type::Enum v) const { return v == Type::IfcTextStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcTextStyle::type() const { return Type::IfcTextStyle; }
Type::Enum IfcTextStyle::Class() { return Type::IfcTextStyle; }
IfcTextStyle::IfcTextStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextStyleFontModel
bool IfcTextStyleFontModel::hasFontFamily() { return !entity->getArgument(1)->isNull(); }
std::vector<IfcTextFontName> /*[1:?]*/ IfcTextStyleFontModel::FontFamily() { return *entity->getArgument(1); }
bool IfcTextStyleFontModel::hasFontStyle() { return !entity->getArgument(2)->isNull(); }
IfcFontStyle IfcTextStyleFontModel::FontStyle() { return *entity->getArgument(2); }
bool IfcTextStyleFontModel::hasFontVariant() { return !entity->getArgument(3)->isNull(); }
IfcFontVariant IfcTextStyleFontModel::FontVariant() { return *entity->getArgument(3); }
bool IfcTextStyleFontModel::hasFontWeight() { return !entity->getArgument(4)->isNull(); }
IfcFontWeight IfcTextStyleFontModel::FontWeight() { return *entity->getArgument(4); }
IfcSizeSelect IfcTextStyleFontModel::FontSize() { return *entity->getArgument(5); }
bool IfcTextStyleFontModel::is(Type::Enum v) const { return v == Type::IfcTextStyleFontModel || IfcPreDefinedTextFont::is(v); }
Type::Enum IfcTextStyleFontModel::type() const { return Type::IfcTextStyleFontModel; }
Type::Enum IfcTextStyleFontModel::Class() { return Type::IfcTextStyleFontModel; }
IfcTextStyleFontModel::IfcTextStyleFontModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleFontModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextStyleForDefinedFont
IfcColour IfcTextStyleForDefinedFont::Colour() { return *entity->getArgument(0); }
bool IfcTextStyleForDefinedFont::hasBackgroundColour() { return !entity->getArgument(1)->isNull(); }
IfcColour IfcTextStyleForDefinedFont::BackgroundColour() { return *entity->getArgument(1); }
bool IfcTextStyleForDefinedFont::is(Type::Enum v) const { return v == Type::IfcTextStyleForDefinedFont; }
Type::Enum IfcTextStyleForDefinedFont::type() const { return Type::IfcTextStyleForDefinedFont; }
Type::Enum IfcTextStyleForDefinedFont::Class() { return Type::IfcTextStyleForDefinedFont; }
IfcTextStyleForDefinedFont::IfcTextStyleForDefinedFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleForDefinedFont)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextStyleTextModel
bool IfcTextStyleTextModel::hasTextIndent() { return !entity->getArgument(0)->isNull(); }
IfcSizeSelect IfcTextStyleTextModel::TextIndent() { return *entity->getArgument(0); }
bool IfcTextStyleTextModel::hasTextAlign() { return !entity->getArgument(1)->isNull(); }
IfcTextAlignment IfcTextStyleTextModel::TextAlign() { return *entity->getArgument(1); }
bool IfcTextStyleTextModel::hasTextDecoration() { return !entity->getArgument(2)->isNull(); }
IfcTextDecoration IfcTextStyleTextModel::TextDecoration() { return *entity->getArgument(2); }
bool IfcTextStyleTextModel::hasLetterSpacing() { return !entity->getArgument(3)->isNull(); }
IfcSizeSelect IfcTextStyleTextModel::LetterSpacing() { return *entity->getArgument(3); }
bool IfcTextStyleTextModel::hasWordSpacing() { return !entity->getArgument(4)->isNull(); }
IfcSizeSelect IfcTextStyleTextModel::WordSpacing() { return *entity->getArgument(4); }
bool IfcTextStyleTextModel::hasTextTransform() { return !entity->getArgument(5)->isNull(); }
IfcTextTransformation IfcTextStyleTextModel::TextTransform() { return *entity->getArgument(5); }
bool IfcTextStyleTextModel::hasLineHeight() { return !entity->getArgument(6)->isNull(); }
IfcSizeSelect IfcTextStyleTextModel::LineHeight() { return *entity->getArgument(6); }
bool IfcTextStyleTextModel::is(Type::Enum v) const { return v == Type::IfcTextStyleTextModel; }
Type::Enum IfcTextStyleTextModel::type() const { return Type::IfcTextStyleTextModel; }
Type::Enum IfcTextStyleTextModel::Class() { return Type::IfcTextStyleTextModel; }
IfcTextStyleTextModel::IfcTextStyleTextModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleTextModel)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextStyleWithBoxCharacteristics
bool IfcTextStyleWithBoxCharacteristics::hasBoxHeight() { return !entity->getArgument(0)->isNull(); }
IfcPositiveLengthMeasure IfcTextStyleWithBoxCharacteristics::BoxHeight() { return *entity->getArgument(0); }
bool IfcTextStyleWithBoxCharacteristics::hasBoxWidth() { return !entity->getArgument(1)->isNull(); }
IfcPositiveLengthMeasure IfcTextStyleWithBoxCharacteristics::BoxWidth() { return *entity->getArgument(1); }
bool IfcTextStyleWithBoxCharacteristics::hasBoxSlantAngle() { return !entity->getArgument(2)->isNull(); }
IfcPlaneAngleMeasure IfcTextStyleWithBoxCharacteristics::BoxSlantAngle() { return *entity->getArgument(2); }
bool IfcTextStyleWithBoxCharacteristics::hasBoxRotateAngle() { return !entity->getArgument(3)->isNull(); }
IfcPlaneAngleMeasure IfcTextStyleWithBoxCharacteristics::BoxRotateAngle() { return *entity->getArgument(3); }
bool IfcTextStyleWithBoxCharacteristics::hasCharacterSpacing() { return !entity->getArgument(4)->isNull(); }
IfcSizeSelect IfcTextStyleWithBoxCharacteristics::CharacterSpacing() { return *entity->getArgument(4); }
bool IfcTextStyleWithBoxCharacteristics::is(Type::Enum v) const { return v == Type::IfcTextStyleWithBoxCharacteristics; }
Type::Enum IfcTextStyleWithBoxCharacteristics::type() const { return Type::IfcTextStyleWithBoxCharacteristics; }
Type::Enum IfcTextStyleWithBoxCharacteristics::Class() { return Type::IfcTextStyleWithBoxCharacteristics; }
IfcTextStyleWithBoxCharacteristics::IfcTextStyleWithBoxCharacteristics(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleWithBoxCharacteristics)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextureCoordinate
IfcAnnotationSurface::list IfcTextureCoordinate::AnnotatedSurface() { RETURN_INVERSE(IfcAnnotationSurface) }
bool IfcTextureCoordinate::is(Type::Enum v) const { return v == Type::IfcTextureCoordinate; }
Type::Enum IfcTextureCoordinate::type() const { return Type::IfcTextureCoordinate; }
Type::Enum IfcTextureCoordinate::Class() { return Type::IfcTextureCoordinate; }
IfcTextureCoordinate::IfcTextureCoordinate(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureCoordinate)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextureCoordinateGenerator
IfcLabel IfcTextureCoordinateGenerator::Mode() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTextureCoordinateGenerator::Parameter() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcTextureCoordinateGenerator::is(Type::Enum v) const { return v == Type::IfcTextureCoordinateGenerator || IfcTextureCoordinate::is(v); }
Type::Enum IfcTextureCoordinateGenerator::type() const { return Type::IfcTextureCoordinateGenerator; }
Type::Enum IfcTextureCoordinateGenerator::Class() { return Type::IfcTextureCoordinateGenerator; }
IfcTextureCoordinateGenerator::IfcTextureCoordinateGenerator(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureCoordinateGenerator)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextureMap
SHARED_PTR< IfcTemplatedEntityList<IfcVertexBasedTextureMap> > IfcTextureMap::TextureMaps() { RETURN_AS_LIST(IfcVertexBasedTextureMap,0) }
bool IfcTextureMap::is(Type::Enum v) const { return v == Type::IfcTextureMap || IfcTextureCoordinate::is(v); }
Type::Enum IfcTextureMap::type() const { return Type::IfcTextureMap; }
Type::Enum IfcTextureMap::Class() { return Type::IfcTextureMap; }
IfcTextureMap::IfcTextureMap(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureMap)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTextureVertex
std::vector<IfcParameterValue> /*[2:2]*/ IfcTextureVertex::Coordinates() { return *entity->getArgument(0); }
bool IfcTextureVertex::is(Type::Enum v) const { return v == Type::IfcTextureVertex; }
Type::Enum IfcTextureVertex::type() const { return Type::IfcTextureVertex; }
Type::Enum IfcTextureVertex::Class() { return Type::IfcTextureVertex; }
IfcTextureVertex::IfcTextureVertex(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureVertex)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcThermalMaterialProperties
bool IfcThermalMaterialProperties::hasSpecificHeatCapacity() { return !entity->getArgument(1)->isNull(); }
IfcSpecificHeatCapacityMeasure IfcThermalMaterialProperties::SpecificHeatCapacity() { return *entity->getArgument(1); }
bool IfcThermalMaterialProperties::hasBoilingPoint() { return !entity->getArgument(2)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcThermalMaterialProperties::BoilingPoint() { return *entity->getArgument(2); }
bool IfcThermalMaterialProperties::hasFreezingPoint() { return !entity->getArgument(3)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcThermalMaterialProperties::FreezingPoint() { return *entity->getArgument(3); }
bool IfcThermalMaterialProperties::hasThermalConductivity() { return !entity->getArgument(4)->isNull(); }
IfcThermalConductivityMeasure IfcThermalMaterialProperties::ThermalConductivity() { return *entity->getArgument(4); }
bool IfcThermalMaterialProperties::is(Type::Enum v) const { return v == Type::IfcThermalMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcThermalMaterialProperties::type() const { return Type::IfcThermalMaterialProperties; }
Type::Enum IfcThermalMaterialProperties::Class() { return Type::IfcThermalMaterialProperties; }
IfcThermalMaterialProperties::IfcThermalMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcThermalMaterialProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTimeSeries
IfcLabel IfcTimeSeries::Name() { return *entity->getArgument(0); }
bool IfcTimeSeries::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcTimeSeries::Description() { return *entity->getArgument(1); }
IfcDateTimeSelect IfcTimeSeries::StartTime() { return *entity->getArgument(2); }
IfcDateTimeSelect IfcTimeSeries::EndTime() { return *entity->getArgument(3); }
IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataTypeEnum IfcTimeSeries::TimeSeriesDataType() { return IfcTimeSeriesDataTypeEnum::FromString(*entity->getArgument(4)); }
IfcDataOriginEnum::IfcDataOriginEnum IfcTimeSeries::DataOrigin() { return IfcDataOriginEnum::FromString(*entity->getArgument(5)); }
bool IfcTimeSeries::hasUserDefinedDataOrigin() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcTimeSeries::UserDefinedDataOrigin() { return *entity->getArgument(6); }
bool IfcTimeSeries::hasUnit() { return !entity->getArgument(7)->isNull(); }
IfcUnit IfcTimeSeries::Unit() { return *entity->getArgument(7); }
IfcTimeSeriesReferenceRelationship::list IfcTimeSeries::DocumentedBy() { RETURN_INVERSE(IfcTimeSeriesReferenceRelationship) }
bool IfcTimeSeries::is(Type::Enum v) const { return v == Type::IfcTimeSeries; }
Type::Enum IfcTimeSeries::type() const { return Type::IfcTimeSeries; }
Type::Enum IfcTimeSeries::Class() { return Type::IfcTimeSeries; }
IfcTimeSeries::IfcTimeSeries(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeries)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTimeSeriesReferenceRelationship
IfcTimeSeries* IfcTimeSeriesReferenceRelationship::ReferencedTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTimeSeriesReferenceRelationship::TimeSeriesReferences() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcTimeSeriesReferenceRelationship::is(Type::Enum v) const { return v == Type::IfcTimeSeriesReferenceRelationship; }
Type::Enum IfcTimeSeriesReferenceRelationship::type() const { return Type::IfcTimeSeriesReferenceRelationship; }
Type::Enum IfcTimeSeriesReferenceRelationship::Class() { return Type::IfcTimeSeriesReferenceRelationship; }
IfcTimeSeriesReferenceRelationship::IfcTimeSeriesReferenceRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeriesReferenceRelationship)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTimeSeriesSchedule
bool IfcTimeSeriesSchedule::hasApplicableDates() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTimeSeriesSchedule::ApplicableDates() { RETURN_AS_LIST(IfcAbstractSelect,5) }
IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleTypeEnum IfcTimeSeriesSchedule::TimeSeriesScheduleType() { return IfcTimeSeriesScheduleTypeEnum::FromString(*entity->getArgument(6)); }
IfcTimeSeries* IfcTimeSeriesSchedule::TimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(7)); }
bool IfcTimeSeriesSchedule::is(Type::Enum v) const { return v == Type::IfcTimeSeriesSchedule || IfcControl::is(v); }
Type::Enum IfcTimeSeriesSchedule::type() const { return Type::IfcTimeSeriesSchedule; }
Type::Enum IfcTimeSeriesSchedule::Class() { return Type::IfcTimeSeriesSchedule; }
IfcTimeSeriesSchedule::IfcTimeSeriesSchedule(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeriesSchedule)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTimeSeriesValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTimeSeriesValue::ListValues() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcTimeSeriesValue::is(Type::Enum v) const { return v == Type::IfcTimeSeriesValue; }
Type::Enum IfcTimeSeriesValue::type() const { return Type::IfcTimeSeriesValue; }
Type::Enum IfcTimeSeriesValue::Class() { return Type::IfcTimeSeriesValue; }
IfcTimeSeriesValue::IfcTimeSeriesValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeriesValue)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTopologicalRepresentationItem
bool IfcTopologicalRepresentationItem::is(Type::Enum v) const { return v == Type::IfcTopologicalRepresentationItem || IfcRepresentationItem::is(v); }
Type::Enum IfcTopologicalRepresentationItem::type() const { return Type::IfcTopologicalRepresentationItem; }
Type::Enum IfcTopologicalRepresentationItem::Class() { return Type::IfcTopologicalRepresentationItem; }
IfcTopologicalRepresentationItem::IfcTopologicalRepresentationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcTopologicalRepresentationItem)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTopologyRepresentation
bool IfcTopologyRepresentation::is(Type::Enum v) const { return v == Type::IfcTopologyRepresentation || IfcShapeModel::is(v); }
Type::Enum IfcTopologyRepresentation::type() const { return Type::IfcTopologyRepresentation; }
Type::Enum IfcTopologyRepresentation::Class() { return Type::IfcTopologyRepresentation; }
IfcTopologyRepresentation::IfcTopologyRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcTopologyRepresentation)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTransformerType
IfcTransformerTypeEnum::IfcTransformerTypeEnum IfcTransformerType::PredefinedType() { return IfcTransformerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTransformerType::is(Type::Enum v) const { return v == Type::IfcTransformerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcTransformerType::type() const { return Type::IfcTransformerType; }
Type::Enum IfcTransformerType::Class() { return Type::IfcTransformerType; }
IfcTransformerType::IfcTransformerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTransformerType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTransportElement
bool IfcTransportElement::hasOperationType() { return !entity->getArgument(8)->isNull(); }
IfcTransportElementTypeEnum::IfcTransportElementTypeEnum IfcTransportElement::OperationType() { return IfcTransportElementTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcTransportElement::hasCapacityByWeight() { return !entity->getArgument(9)->isNull(); }
IfcMassMeasure IfcTransportElement::CapacityByWeight() { return *entity->getArgument(9); }
bool IfcTransportElement::hasCapacityByNumber() { return !entity->getArgument(10)->isNull(); }
IfcCountMeasure IfcTransportElement::CapacityByNumber() { return *entity->getArgument(10); }
bool IfcTransportElement::is(Type::Enum v) const { return v == Type::IfcTransportElement || IfcElement::is(v); }
Type::Enum IfcTransportElement::type() const { return Type::IfcTransportElement; }
Type::Enum IfcTransportElement::Class() { return Type::IfcTransportElement; }
IfcTransportElement::IfcTransportElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcTransportElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTransportElementType
IfcTransportElementTypeEnum::IfcTransportElementTypeEnum IfcTransportElementType::PredefinedType() { return IfcTransportElementTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTransportElementType::is(Type::Enum v) const { return v == Type::IfcTransportElementType || IfcElementType::is(v); }
Type::Enum IfcTransportElementType::type() const { return Type::IfcTransportElementType; }
Type::Enum IfcTransportElementType::Class() { return Type::IfcTransportElementType; }
IfcTransportElementType::IfcTransportElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTransportElementType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTrapeziumProfileDef
IfcPositiveLengthMeasure IfcTrapeziumProfileDef::BottomXDim() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcTrapeziumProfileDef::TopXDim() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcTrapeziumProfileDef::YDim() { return *entity->getArgument(5); }
IfcLengthMeasure IfcTrapeziumProfileDef::TopXOffset() { return *entity->getArgument(6); }
bool IfcTrapeziumProfileDef::is(Type::Enum v) const { return v == Type::IfcTrapeziumProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcTrapeziumProfileDef::type() const { return Type::IfcTrapeziumProfileDef; }
Type::Enum IfcTrapeziumProfileDef::Class() { return Type::IfcTrapeziumProfileDef; }
IfcTrapeziumProfileDef::IfcTrapeziumProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcTrapeziumProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTrimmedCurve
IfcCurve* IfcTrimmedCurve::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTrimmedCurve::Trim1() { RETURN_AS_LIST(IfcAbstractSelect,1) }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTrimmedCurve::Trim2() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcTrimmedCurve::SenseAgreement() { return *entity->getArgument(3); }
IfcTrimmingPreference::IfcTrimmingPreference IfcTrimmedCurve::MasterRepresentation() { return IfcTrimmingPreference::FromString(*entity->getArgument(4)); }
bool IfcTrimmedCurve::is(Type::Enum v) const { return v == Type::IfcTrimmedCurve || IfcBoundedCurve::is(v); }
Type::Enum IfcTrimmedCurve::type() const { return Type::IfcTrimmedCurve; }
Type::Enum IfcTrimmedCurve::Class() { return Type::IfcTrimmedCurve; }
IfcTrimmedCurve::IfcTrimmedCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcTrimmedCurve)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTubeBundleType
IfcTubeBundleTypeEnum::IfcTubeBundleTypeEnum IfcTubeBundleType::PredefinedType() { return IfcTubeBundleTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTubeBundleType::is(Type::Enum v) const { return v == Type::IfcTubeBundleType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcTubeBundleType::type() const { return Type::IfcTubeBundleType; }
Type::Enum IfcTubeBundleType::Class() { return Type::IfcTubeBundleType; }
IfcTubeBundleType::IfcTubeBundleType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTubeBundleType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTwoDirectionRepeatFactor
IfcVector* IfcTwoDirectionRepeatFactor::SecondRepeatFactor() { return reinterpret_pointer_cast<IfcBaseClass,IfcVector>(*entity->getArgument(1)); }
bool IfcTwoDirectionRepeatFactor::is(Type::Enum v) const { return v == Type::IfcTwoDirectionRepeatFactor || IfcOneDirectionRepeatFactor::is(v); }
Type::Enum IfcTwoDirectionRepeatFactor::type() const { return Type::IfcTwoDirectionRepeatFactor; }
Type::Enum IfcTwoDirectionRepeatFactor::Class() { return Type::IfcTwoDirectionRepeatFactor; }
IfcTwoDirectionRepeatFactor::IfcTwoDirectionRepeatFactor(IfcAbstractEntityPtr e) { if (!is(Type::IfcTwoDirectionRepeatFactor)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTypeObject
bool IfcTypeObject::hasApplicableOccurrence() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcTypeObject::ApplicableOccurrence() { return *entity->getArgument(4); }
bool IfcTypeObject::hasHasPropertySets() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcPropertySetDefinition> > IfcTypeObject::HasPropertySets() { RETURN_AS_LIST(IfcPropertySetDefinition,5) }
IfcRelDefinesByType::list IfcTypeObject::ObjectTypeOf() { RETURN_INVERSE(IfcRelDefinesByType) }
bool IfcTypeObject::is(Type::Enum v) const { return v == Type::IfcTypeObject || IfcObjectDefinition::is(v); }
Type::Enum IfcTypeObject::type() const { return Type::IfcTypeObject; }
Type::Enum IfcTypeObject::Class() { return Type::IfcTypeObject; }
IfcTypeObject::IfcTypeObject(IfcAbstractEntityPtr e) { if (!is(Type::IfcTypeObject)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcTypeProduct
bool IfcTypeProduct::hasRepresentationMaps() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationMap> > IfcTypeProduct::RepresentationMaps() { RETURN_AS_LIST(IfcRepresentationMap,6) }
bool IfcTypeProduct::hasTag() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcTypeProduct::Tag() { return *entity->getArgument(7); }
bool IfcTypeProduct::is(Type::Enum v) const { return v == Type::IfcTypeProduct || IfcTypeObject::is(v); }
Type::Enum IfcTypeProduct::type() const { return Type::IfcTypeProduct; }
Type::Enum IfcTypeProduct::Class() { return Type::IfcTypeProduct; }
IfcTypeProduct::IfcTypeProduct(IfcAbstractEntityPtr e) { if (!is(Type::IfcTypeProduct)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcUShapeProfileDef
IfcPositiveLengthMeasure IfcUShapeProfileDef::Depth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcUShapeProfileDef::FlangeWidth() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcUShapeProfileDef::WebThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcUShapeProfileDef::FlangeThickness() { return *entity->getArgument(6); }
bool IfcUShapeProfileDef::hasFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcUShapeProfileDef::FilletRadius() { return *entity->getArgument(7); }
bool IfcUShapeProfileDef::hasEdgeRadius() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcUShapeProfileDef::EdgeRadius() { return *entity->getArgument(8); }
bool IfcUShapeProfileDef::hasFlangeSlope() { return !entity->getArgument(9)->isNull(); }
IfcPlaneAngleMeasure IfcUShapeProfileDef::FlangeSlope() { return *entity->getArgument(9); }
bool IfcUShapeProfileDef::hasCentreOfGravityInX() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcUShapeProfileDef::CentreOfGravityInX() { return *entity->getArgument(10); }
bool IfcUShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcUShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcUShapeProfileDef::type() const { return Type::IfcUShapeProfileDef; }
Type::Enum IfcUShapeProfileDef::Class() { return Type::IfcUShapeProfileDef; }
IfcUShapeProfileDef::IfcUShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcUShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcUnitAssignment
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcUnitAssignment::Units() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcUnitAssignment::is(Type::Enum v) const { return v == Type::IfcUnitAssignment; }
Type::Enum IfcUnitAssignment::type() const { return Type::IfcUnitAssignment; }
Type::Enum IfcUnitAssignment::Class() { return Type::IfcUnitAssignment; }
IfcUnitAssignment::IfcUnitAssignment(IfcAbstractEntityPtr e) { if (!is(Type::IfcUnitAssignment)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcUnitaryEquipmentType
IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentTypeEnum IfcUnitaryEquipmentType::PredefinedType() { return IfcUnitaryEquipmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcUnitaryEquipmentType::is(Type::Enum v) const { return v == Type::IfcUnitaryEquipmentType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcUnitaryEquipmentType::type() const { return Type::IfcUnitaryEquipmentType; }
Type::Enum IfcUnitaryEquipmentType::Class() { return Type::IfcUnitaryEquipmentType; }
IfcUnitaryEquipmentType::IfcUnitaryEquipmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcUnitaryEquipmentType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcValveType
IfcValveTypeEnum::IfcValveTypeEnum IfcValveType::PredefinedType() { return IfcValveTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcValveType::is(Type::Enum v) const { return v == Type::IfcValveType || IfcFlowControllerType::is(v); }
Type::Enum IfcValveType::type() const { return Type::IfcValveType; }
Type::Enum IfcValveType::Class() { return Type::IfcValveType; }
IfcValveType::IfcValveType(IfcAbstractEntityPtr e) { if (!is(Type::IfcValveType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVector
IfcDirection* IfcVector::Orientation() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(0)); }
IfcLengthMeasure IfcVector::Magnitude() { return *entity->getArgument(1); }
bool IfcVector::is(Type::Enum v) const { return v == Type::IfcVector || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcVector::type() const { return Type::IfcVector; }
Type::Enum IfcVector::Class() { return Type::IfcVector; }
IfcVector::IfcVector(IfcAbstractEntityPtr e) { if (!is(Type::IfcVector)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVertex
bool IfcVertex::is(Type::Enum v) const { return v == Type::IfcVertex || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcVertex::type() const { return Type::IfcVertex; }
Type::Enum IfcVertex::Class() { return Type::IfcVertex; }
IfcVertex::IfcVertex(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertex)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVertexBasedTextureMap
SHARED_PTR< IfcTemplatedEntityList<IfcTextureVertex> > IfcVertexBasedTextureMap::TextureVertices() { RETURN_AS_LIST(IfcTextureVertex,0) }
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcVertexBasedTextureMap::TexturePoints() { RETURN_AS_LIST(IfcCartesianPoint,1) }
bool IfcVertexBasedTextureMap::is(Type::Enum v) const { return v == Type::IfcVertexBasedTextureMap; }
Type::Enum IfcVertexBasedTextureMap::type() const { return Type::IfcVertexBasedTextureMap; }
Type::Enum IfcVertexBasedTextureMap::Class() { return Type::IfcVertexBasedTextureMap; }
IfcVertexBasedTextureMap::IfcVertexBasedTextureMap(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertexBasedTextureMap)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVertexLoop
IfcVertex* IfcVertexLoop::LoopVertex() { return reinterpret_pointer_cast<IfcBaseClass,IfcVertex>(*entity->getArgument(0)); }
bool IfcVertexLoop::is(Type::Enum v) const { return v == Type::IfcVertexLoop || IfcLoop::is(v); }
Type::Enum IfcVertexLoop::type() const { return Type::IfcVertexLoop; }
Type::Enum IfcVertexLoop::Class() { return Type::IfcVertexLoop; }
IfcVertexLoop::IfcVertexLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertexLoop)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVertexPoint
IfcPoint* IfcVertexPoint::VertexGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcPoint>(*entity->getArgument(0)); }
bool IfcVertexPoint::is(Type::Enum v) const { return v == Type::IfcVertexPoint || IfcVertex::is(v); }
Type::Enum IfcVertexPoint::type() const { return Type::IfcVertexPoint; }
Type::Enum IfcVertexPoint::Class() { return Type::IfcVertexPoint; }
IfcVertexPoint::IfcVertexPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertexPoint)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVibrationIsolatorType
IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorTypeEnum IfcVibrationIsolatorType::PredefinedType() { return IfcVibrationIsolatorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcVibrationIsolatorType::is(Type::Enum v) const { return v == Type::IfcVibrationIsolatorType || IfcDiscreteAccessoryType::is(v); }
Type::Enum IfcVibrationIsolatorType::type() const { return Type::IfcVibrationIsolatorType; }
Type::Enum IfcVibrationIsolatorType::Class() { return Type::IfcVibrationIsolatorType; }
IfcVibrationIsolatorType::IfcVibrationIsolatorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcVibrationIsolatorType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVirtualElement
bool IfcVirtualElement::is(Type::Enum v) const { return v == Type::IfcVirtualElement || IfcElement::is(v); }
Type::Enum IfcVirtualElement::type() const { return Type::IfcVirtualElement; }
Type::Enum IfcVirtualElement::Class() { return Type::IfcVirtualElement; }
IfcVirtualElement::IfcVirtualElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcVirtualElement)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcVirtualGridIntersection
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcVirtualGridIntersection::IntersectingAxes() { RETURN_AS_LIST(IfcGridAxis,0) }
std::vector<IfcLengthMeasure> /*[2:3]*/ IfcVirtualGridIntersection::OffsetDistances() { return *entity->getArgument(1); }
bool IfcVirtualGridIntersection::is(Type::Enum v) const { return v == Type::IfcVirtualGridIntersection; }
Type::Enum IfcVirtualGridIntersection::type() const { return Type::IfcVirtualGridIntersection; }
Type::Enum IfcVirtualGridIntersection::Class() { return Type::IfcVirtualGridIntersection; }
IfcVirtualGridIntersection::IfcVirtualGridIntersection(IfcAbstractEntityPtr e) { if (!is(Type::IfcVirtualGridIntersection)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWall
bool IfcWall::is(Type::Enum v) const { return v == Type::IfcWall || IfcBuildingElement::is(v); }
Type::Enum IfcWall::type() const { return Type::IfcWall; }
Type::Enum IfcWall::Class() { return Type::IfcWall; }
IfcWall::IfcWall(IfcAbstractEntityPtr e) { if (!is(Type::IfcWall)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWallStandardCase
bool IfcWallStandardCase::is(Type::Enum v) const { return v == Type::IfcWallStandardCase || IfcWall::is(v); }
Type::Enum IfcWallStandardCase::type() const { return Type::IfcWallStandardCase; }
Type::Enum IfcWallStandardCase::Class() { return Type::IfcWallStandardCase; }
IfcWallStandardCase::IfcWallStandardCase(IfcAbstractEntityPtr e) { if (!is(Type::IfcWallStandardCase)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWallType
IfcWallTypeEnum::IfcWallTypeEnum IfcWallType::PredefinedType() { return IfcWallTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcWallType::is(Type::Enum v) const { return v == Type::IfcWallType || IfcBuildingElementType::is(v); }
Type::Enum IfcWallType::type() const { return Type::IfcWallType; }
Type::Enum IfcWallType::Class() { return Type::IfcWallType; }
IfcWallType::IfcWallType(IfcAbstractEntityPtr e) { if (!is(Type::IfcWallType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWasteTerminalType
IfcWasteTerminalTypeEnum::IfcWasteTerminalTypeEnum IfcWasteTerminalType::PredefinedType() { return IfcWasteTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcWasteTerminalType::is(Type::Enum v) const { return v == Type::IfcWasteTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcWasteTerminalType::type() const { return Type::IfcWasteTerminalType; }
Type::Enum IfcWasteTerminalType::Class() { return Type::IfcWasteTerminalType; }
IfcWasteTerminalType::IfcWasteTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcWasteTerminalType)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWaterProperties
bool IfcWaterProperties::hasIsPotable() { return !entity->getArgument(1)->isNull(); }
bool IfcWaterProperties::IsPotable() { return *entity->getArgument(1); }
bool IfcWaterProperties::hasHardness() { return !entity->getArgument(2)->isNull(); }
IfcIonConcentrationMeasure IfcWaterProperties::Hardness() { return *entity->getArgument(2); }
bool IfcWaterProperties::hasAlkalinityConcentration() { return !entity->getArgument(3)->isNull(); }
IfcIonConcentrationMeasure IfcWaterProperties::AlkalinityConcentration() { return *entity->getArgument(3); }
bool IfcWaterProperties::hasAcidityConcentration() { return !entity->getArgument(4)->isNull(); }
IfcIonConcentrationMeasure IfcWaterProperties::AcidityConcentration() { return *entity->getArgument(4); }
bool IfcWaterProperties::hasImpuritiesContent() { return !entity->getArgument(5)->isNull(); }
IfcNormalisedRatioMeasure IfcWaterProperties::ImpuritiesContent() { return *entity->getArgument(5); }
bool IfcWaterProperties::hasPHLevel() { return !entity->getArgument(6)->isNull(); }
IfcPHMeasure IfcWaterProperties::PHLevel() { return *entity->getArgument(6); }
bool IfcWaterProperties::hasDissolvedSolidsContent() { return !entity->getArgument(7)->isNull(); }
IfcNormalisedRatioMeasure IfcWaterProperties::DissolvedSolidsContent() { return *entity->getArgument(7); }
bool IfcWaterProperties::is(Type::Enum v) const { return v == Type::IfcWaterProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcWaterProperties::type() const { return Type::IfcWaterProperties; }
Type::Enum IfcWaterProperties::Class() { return Type::IfcWaterProperties; }
IfcWaterProperties::IfcWaterProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcWaterProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWindow
bool IfcWindow::hasOverallHeight() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcWindow::OverallHeight() { return *entity->getArgument(8); }
bool IfcWindow::hasOverallWidth() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcWindow::OverallWidth() { return *entity->getArgument(9); }
bool IfcWindow::is(Type::Enum v) const { return v == Type::IfcWindow || IfcBuildingElement::is(v); }
Type::Enum IfcWindow::type() const { return Type::IfcWindow; }
Type::Enum IfcWindow::Class() { return Type::IfcWindow; }
IfcWindow::IfcWindow(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindow)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWindowLiningProperties
bool IfcWindowLiningProperties::hasLiningDepth() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcWindowLiningProperties::LiningDepth() { return *entity->getArgument(4); }
bool IfcWindowLiningProperties::hasLiningThickness() { return !entity->getArgument(5)->isNull(); }
IfcPositiveLengthMeasure IfcWindowLiningProperties::LiningThickness() { return *entity->getArgument(5); }
bool IfcWindowLiningProperties::hasTransomThickness() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcWindowLiningProperties::TransomThickness() { return *entity->getArgument(6); }
bool IfcWindowLiningProperties::hasMullionThickness() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcWindowLiningProperties::MullionThickness() { return *entity->getArgument(7); }
bool IfcWindowLiningProperties::hasFirstTransomOffset() { return !entity->getArgument(8)->isNull(); }
IfcNormalisedRatioMeasure IfcWindowLiningProperties::FirstTransomOffset() { return *entity->getArgument(8); }
bool IfcWindowLiningProperties::hasSecondTransomOffset() { return !entity->getArgument(9)->isNull(); }
IfcNormalisedRatioMeasure IfcWindowLiningProperties::SecondTransomOffset() { return *entity->getArgument(9); }
bool IfcWindowLiningProperties::hasFirstMullionOffset() { return !entity->getArgument(10)->isNull(); }
IfcNormalisedRatioMeasure IfcWindowLiningProperties::FirstMullionOffset() { return *entity->getArgument(10); }
bool IfcWindowLiningProperties::hasSecondMullionOffset() { return !entity->getArgument(11)->isNull(); }
IfcNormalisedRatioMeasure IfcWindowLiningProperties::SecondMullionOffset() { return *entity->getArgument(11); }
bool IfcWindowLiningProperties::hasShapeAspectStyle() { return !entity->getArgument(12)->isNull(); }
IfcShapeAspect* IfcWindowLiningProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(12)); }
bool IfcWindowLiningProperties::is(Type::Enum v) const { return v == Type::IfcWindowLiningProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcWindowLiningProperties::type() const { return Type::IfcWindowLiningProperties; }
Type::Enum IfcWindowLiningProperties::Class() { return Type::IfcWindowLiningProperties; }
IfcWindowLiningProperties::IfcWindowLiningProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindowLiningProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWindowPanelProperties
IfcWindowPanelOperationEnum::IfcWindowPanelOperationEnum IfcWindowPanelProperties::OperationType() { return IfcWindowPanelOperationEnum::FromString(*entity->getArgument(4)); }
IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum IfcWindowPanelProperties::PanelPosition() { return IfcWindowPanelPositionEnum::FromString(*entity->getArgument(5)); }
bool IfcWindowPanelProperties::hasFrameDepth() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcWindowPanelProperties::FrameDepth() { return *entity->getArgument(6); }
bool IfcWindowPanelProperties::hasFrameThickness() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcWindowPanelProperties::FrameThickness() { return *entity->getArgument(7); }
bool IfcWindowPanelProperties::hasShapeAspectStyle() { return !entity->getArgument(8)->isNull(); }
IfcShapeAspect* IfcWindowPanelProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(8)); }
bool IfcWindowPanelProperties::is(Type::Enum v) const { return v == Type::IfcWindowPanelProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcWindowPanelProperties::type() const { return Type::IfcWindowPanelProperties; }
Type::Enum IfcWindowPanelProperties::Class() { return Type::IfcWindowPanelProperties; }
IfcWindowPanelProperties::IfcWindowPanelProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindowPanelProperties)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWindowStyle
IfcWindowStyleConstructionEnum::IfcWindowStyleConstructionEnum IfcWindowStyle::ConstructionType() { return IfcWindowStyleConstructionEnum::FromString(*entity->getArgument(8)); }
IfcWindowStyleOperationEnum::IfcWindowStyleOperationEnum IfcWindowStyle::OperationType() { return IfcWindowStyleOperationEnum::FromString(*entity->getArgument(9)); }
bool IfcWindowStyle::ParameterTakesPrecedence() { return *entity->getArgument(10); }
bool IfcWindowStyle::Sizeable() { return *entity->getArgument(11); }
bool IfcWindowStyle::is(Type::Enum v) const { return v == Type::IfcWindowStyle || IfcTypeProduct::is(v); }
Type::Enum IfcWindowStyle::type() const { return Type::IfcWindowStyle; }
Type::Enum IfcWindowStyle::Class() { return Type::IfcWindowStyle; }
IfcWindowStyle::IfcWindowStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindowStyle)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWorkControl
IfcIdentifier IfcWorkControl::Identifier() { return *entity->getArgument(5); }
IfcDateTimeSelect IfcWorkControl::CreationDate() { return *entity->getArgument(6); }
bool IfcWorkControl::hasCreators() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > IfcWorkControl::Creators() { RETURN_AS_LIST(IfcPerson,7) }
bool IfcWorkControl::hasPurpose() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcWorkControl::Purpose() { return *entity->getArgument(8); }
bool IfcWorkControl::hasDuration() { return !entity->getArgument(9)->isNull(); }
IfcTimeMeasure IfcWorkControl::Duration() { return *entity->getArgument(9); }
bool IfcWorkControl::hasTotalFloat() { return !entity->getArgument(10)->isNull(); }
IfcTimeMeasure IfcWorkControl::TotalFloat() { return *entity->getArgument(10); }
IfcDateTimeSelect IfcWorkControl::StartTime() { return *entity->getArgument(11); }
bool IfcWorkControl::hasFinishTime() { return !entity->getArgument(12)->isNull(); }
IfcDateTimeSelect IfcWorkControl::FinishTime() { return *entity->getArgument(12); }
bool IfcWorkControl::hasWorkControlType() { return !entity->getArgument(13)->isNull(); }
IfcWorkControlTypeEnum::IfcWorkControlTypeEnum IfcWorkControl::WorkControlType() { return IfcWorkControlTypeEnum::FromString(*entity->getArgument(13)); }
bool IfcWorkControl::hasUserDefinedControlType() { return !entity->getArgument(14)->isNull(); }
IfcLabel IfcWorkControl::UserDefinedControlType() { return *entity->getArgument(14); }
bool IfcWorkControl::is(Type::Enum v) const { return v == Type::IfcWorkControl || IfcControl::is(v); }
Type::Enum IfcWorkControl::type() const { return Type::IfcWorkControl; }
Type::Enum IfcWorkControl::Class() { return Type::IfcWorkControl; }
IfcWorkControl::IfcWorkControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcWorkControl)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWorkPlan
bool IfcWorkPlan::is(Type::Enum v) const { return v == Type::IfcWorkPlan || IfcWorkControl::is(v); }
Type::Enum IfcWorkPlan::type() const { return Type::IfcWorkPlan; }
Type::Enum IfcWorkPlan::Class() { return Type::IfcWorkPlan; }
IfcWorkPlan::IfcWorkPlan(IfcAbstractEntityPtr e) { if (!is(Type::IfcWorkPlan)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcWorkSchedule
bool IfcWorkSchedule::is(Type::Enum v) const { return v == Type::IfcWorkSchedule || IfcWorkControl::is(v); }
Type::Enum IfcWorkSchedule::type() const { return Type::IfcWorkSchedule; }
Type::Enum IfcWorkSchedule::Class() { return Type::IfcWorkSchedule; }
IfcWorkSchedule::IfcWorkSchedule(IfcAbstractEntityPtr e) { if (!is(Type::IfcWorkSchedule)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcZShapeProfileDef
IfcPositiveLengthMeasure IfcZShapeProfileDef::Depth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::FlangeWidth() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::WebThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::FlangeThickness() { return *entity->getArgument(6); }
bool IfcZShapeProfileDef::hasFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::FilletRadius() { return *entity->getArgument(7); }
bool IfcZShapeProfileDef::hasEdgeRadius() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::EdgeRadius() { return *entity->getArgument(8); }
bool IfcZShapeProfileDef::is(Type::Enum v) const { return v == Type::IfcZShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcZShapeProfileDef::type() const { return Type::IfcZShapeProfileDef; }
Type::Enum IfcZShapeProfileDef::Class() { return Type::IfcZShapeProfileDef; }
IfcZShapeProfileDef::IfcZShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcZShapeProfileDef)) throw IfcException("Unable to find find keyword in schema"); entity = e; } 
// Function implementations for IfcZone
bool IfcZone::is(Type::Enum v) const { return v == Type::IfcZone || IfcGroup::is(v); }
Type::Enum IfcZone::type() const { return Type::IfcZone; }
Type::Enum IfcZone::Class() { return Type::IfcZone; }
IfcZone::IfcZone(IfcAbstractEntityPtr e) { if (!is(Type::IfcZone)) throw IfcException("Unable to find find keyword in schema"); entity = e; }