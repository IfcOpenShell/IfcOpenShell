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

using namespace Ifc2x3;

IfcSchemaEntity Ifc2x3::SchemaEntity(IfcAbstractEntityPtr e) {
    if ( e->is(Type::IfcAbsorbedDoseMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcAccelerationMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcAmountOfSubstanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcAngularVelocityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcAreaMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcBoolean) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcColour) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcComplexNumber) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcCompoundPlaneAngleMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcContextDependentMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcCountMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcCurvatureMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcDateTimeSelect) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcDerivedMeasureValue) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcDescriptiveMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcDoseEquivalentMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcDynamicViscosityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcElectricCapacitanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcElectricChargeMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcElectricConductanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcElectricCurrentMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcElectricResistanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcElectricVoltageMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcEnergyMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcForceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcFrequencyMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcHeatFluxDensityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcHeatingValueMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcIdentifier) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcIlluminanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcInductanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcInteger) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcIntegerCountRateMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcIonConcentrationMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcIsothermalMoistureCapacityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcKinematicViscosityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLabel) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLengthMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLinearForceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLinearMomentMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLinearStiffnessMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLinearVelocityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLogical) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLuminousFluxMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLuminousIntensityDistributionMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcLuminousIntensityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMagneticFluxDensityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMagneticFluxMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMassDensityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMassFlowRateMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMassMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMassPerLengthMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMeasureValue) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcModulusOfElasticityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcModulusOfLinearSubgradeReactionMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcModulusOfRotationalSubgradeReactionMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcModulusOfSubgradeReactionMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMoistureDiffusivityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMolecularWeightMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMomentOfInertiaMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcMonetaryMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcNormalisedRatioMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcNullStyle) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcNumericMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPHMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcParameterValue) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPlanarForceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPlaneAngleMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPositiveLengthMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPositivePlaneAngleMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPositiveRatioMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPowerMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcPressureMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcRadioActivityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcRatioMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcReal) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcRotationalFrequencyMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcRotationalMassMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcRotationalStiffnessMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSectionModulusMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSectionalAreaIntegralMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcShearModulusMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSimpleValue) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSolidAngleMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSoundPowerMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSoundPressureMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSpecificHeatCapacityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSpecularExponent) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcSpecularRoughness) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcTemperatureGradientMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcText) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcThermalAdmittanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcThermalConductivityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcThermalExpansionCoefficientMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcThermalResistanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcThermalTransmittanceMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcThermodynamicTemperatureMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcTimeMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcTimeStamp) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcTorqueMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcVaporPermeabilityMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcVolumeMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcVolumetricFlowRateMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcWarpingConstantMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::IfcWarpingMomentMeasure) ) return IfcSchemaEntity(new IfcEntitySelect(e));
    if ( e->is(Type::Ifc2DCompositeCurve) ) return IfcSchemaEntity(new Ifc2DCompositeCurve(e));
    if ( e->is(Type::IfcActionRequest) ) return IfcSchemaEntity(new IfcActionRequest(e));
    if ( e->is(Type::IfcActor) ) return IfcSchemaEntity(new IfcActor(e));
    if ( e->is(Type::IfcActorRole) ) return IfcSchemaEntity(new IfcActorRole(e));
    if ( e->is(Type::IfcActuatorType) ) return IfcSchemaEntity(new IfcActuatorType(e));
    if ( e->is(Type::IfcAddress) ) return IfcSchemaEntity(new IfcAddress(e));
    if ( e->is(Type::IfcAirTerminalBoxType) ) return IfcSchemaEntity(new IfcAirTerminalBoxType(e));
    if ( e->is(Type::IfcAirTerminalType) ) return IfcSchemaEntity(new IfcAirTerminalType(e));
    if ( e->is(Type::IfcAirToAirHeatRecoveryType) ) return IfcSchemaEntity(new IfcAirToAirHeatRecoveryType(e));
    if ( e->is(Type::IfcAlarmType) ) return IfcSchemaEntity(new IfcAlarmType(e));
    if ( e->is(Type::IfcAngularDimension) ) return IfcSchemaEntity(new IfcAngularDimension(e));
    if ( e->is(Type::IfcAnnotation) ) return IfcSchemaEntity(new IfcAnnotation(e));
    if ( e->is(Type::IfcAnnotationCurveOccurrence) ) return IfcSchemaEntity(new IfcAnnotationCurveOccurrence(e));
    if ( e->is(Type::IfcAnnotationFillArea) ) return IfcSchemaEntity(new IfcAnnotationFillArea(e));
    if ( e->is(Type::IfcAnnotationFillAreaOccurrence) ) return IfcSchemaEntity(new IfcAnnotationFillAreaOccurrence(e));
    if ( e->is(Type::IfcAnnotationOccurrence) ) return IfcSchemaEntity(new IfcAnnotationOccurrence(e));
    if ( e->is(Type::IfcAnnotationSurface) ) return IfcSchemaEntity(new IfcAnnotationSurface(e));
    if ( e->is(Type::IfcAnnotationSurfaceOccurrence) ) return IfcSchemaEntity(new IfcAnnotationSurfaceOccurrence(e));
    if ( e->is(Type::IfcAnnotationSymbolOccurrence) ) return IfcSchemaEntity(new IfcAnnotationSymbolOccurrence(e));
    if ( e->is(Type::IfcAnnotationTextOccurrence) ) return IfcSchemaEntity(new IfcAnnotationTextOccurrence(e));
    if ( e->is(Type::IfcApplication) ) return IfcSchemaEntity(new IfcApplication(e));
    if ( e->is(Type::IfcAppliedValue) ) return IfcSchemaEntity(new IfcAppliedValue(e));
    if ( e->is(Type::IfcAppliedValueRelationship) ) return IfcSchemaEntity(new IfcAppliedValueRelationship(e));
    if ( e->is(Type::IfcApproval) ) return IfcSchemaEntity(new IfcApproval(e));
    if ( e->is(Type::IfcApprovalActorRelationship) ) return IfcSchemaEntity(new IfcApprovalActorRelationship(e));
    if ( e->is(Type::IfcApprovalPropertyRelationship) ) return IfcSchemaEntity(new IfcApprovalPropertyRelationship(e));
    if ( e->is(Type::IfcApprovalRelationship) ) return IfcSchemaEntity(new IfcApprovalRelationship(e));
    if ( e->is(Type::IfcArbitraryClosedProfileDef) ) return IfcSchemaEntity(new IfcArbitraryClosedProfileDef(e));
    if ( e->is(Type::IfcArbitraryOpenProfileDef) ) return IfcSchemaEntity(new IfcArbitraryOpenProfileDef(e));
    if ( e->is(Type::IfcArbitraryProfileDefWithVoids) ) return IfcSchemaEntity(new IfcArbitraryProfileDefWithVoids(e));
    if ( e->is(Type::IfcAsset) ) return IfcSchemaEntity(new IfcAsset(e));
    if ( e->is(Type::IfcAsymmetricIShapeProfileDef) ) return IfcSchemaEntity(new IfcAsymmetricIShapeProfileDef(e));
    if ( e->is(Type::IfcAxis1Placement) ) return IfcSchemaEntity(new IfcAxis1Placement(e));
    if ( e->is(Type::IfcAxis2Placement2D) ) return IfcSchemaEntity(new IfcAxis2Placement2D(e));
    if ( e->is(Type::IfcAxis2Placement3D) ) return IfcSchemaEntity(new IfcAxis2Placement3D(e));
    if ( e->is(Type::IfcBSplineCurve) ) return IfcSchemaEntity(new IfcBSplineCurve(e));
    if ( e->is(Type::IfcBeam) ) return IfcSchemaEntity(new IfcBeam(e));
    if ( e->is(Type::IfcBeamType) ) return IfcSchemaEntity(new IfcBeamType(e));
    if ( e->is(Type::IfcBezierCurve) ) return IfcSchemaEntity(new IfcBezierCurve(e));
    if ( e->is(Type::IfcBlobTexture) ) return IfcSchemaEntity(new IfcBlobTexture(e));
    if ( e->is(Type::IfcBlock) ) return IfcSchemaEntity(new IfcBlock(e));
    if ( e->is(Type::IfcBoilerType) ) return IfcSchemaEntity(new IfcBoilerType(e));
    if ( e->is(Type::IfcBooleanClippingResult) ) return IfcSchemaEntity(new IfcBooleanClippingResult(e));
    if ( e->is(Type::IfcBooleanResult) ) return IfcSchemaEntity(new IfcBooleanResult(e));
    if ( e->is(Type::IfcBoundaryCondition) ) return IfcSchemaEntity(new IfcBoundaryCondition(e));
    if ( e->is(Type::IfcBoundaryEdgeCondition) ) return IfcSchemaEntity(new IfcBoundaryEdgeCondition(e));
    if ( e->is(Type::IfcBoundaryFaceCondition) ) return IfcSchemaEntity(new IfcBoundaryFaceCondition(e));
    if ( e->is(Type::IfcBoundaryNodeCondition) ) return IfcSchemaEntity(new IfcBoundaryNodeCondition(e));
    if ( e->is(Type::IfcBoundaryNodeConditionWarping) ) return IfcSchemaEntity(new IfcBoundaryNodeConditionWarping(e));
    if ( e->is(Type::IfcBoundedCurve) ) return IfcSchemaEntity(new IfcBoundedCurve(e));
    if ( e->is(Type::IfcBoundedSurface) ) return IfcSchemaEntity(new IfcBoundedSurface(e));
    if ( e->is(Type::IfcBoundingBox) ) return IfcSchemaEntity(new IfcBoundingBox(e));
    if ( e->is(Type::IfcBoxedHalfSpace) ) return IfcSchemaEntity(new IfcBoxedHalfSpace(e));
    if ( e->is(Type::IfcBuilding) ) return IfcSchemaEntity(new IfcBuilding(e));
    if ( e->is(Type::IfcBuildingElement) ) return IfcSchemaEntity(new IfcBuildingElement(e));
    if ( e->is(Type::IfcBuildingElementComponent) ) return IfcSchemaEntity(new IfcBuildingElementComponent(e));
    if ( e->is(Type::IfcBuildingElementPart) ) return IfcSchemaEntity(new IfcBuildingElementPart(e));
    if ( e->is(Type::IfcBuildingElementProxy) ) return IfcSchemaEntity(new IfcBuildingElementProxy(e));
    if ( e->is(Type::IfcBuildingElementProxyType) ) return IfcSchemaEntity(new IfcBuildingElementProxyType(e));
    if ( e->is(Type::IfcBuildingElementType) ) return IfcSchemaEntity(new IfcBuildingElementType(e));
    if ( e->is(Type::IfcBuildingStorey) ) return IfcSchemaEntity(new IfcBuildingStorey(e));
    if ( e->is(Type::IfcCShapeProfileDef) ) return IfcSchemaEntity(new IfcCShapeProfileDef(e));
    if ( e->is(Type::IfcCableCarrierFittingType) ) return IfcSchemaEntity(new IfcCableCarrierFittingType(e));
    if ( e->is(Type::IfcCableCarrierSegmentType) ) return IfcSchemaEntity(new IfcCableCarrierSegmentType(e));
    if ( e->is(Type::IfcCableSegmentType) ) return IfcSchemaEntity(new IfcCableSegmentType(e));
    if ( e->is(Type::IfcCalendarDate) ) return IfcSchemaEntity(new IfcCalendarDate(e));
    if ( e->is(Type::IfcCartesianPoint) ) return IfcSchemaEntity(new IfcCartesianPoint(e));
    if ( e->is(Type::IfcCartesianTransformationOperator) ) return IfcSchemaEntity(new IfcCartesianTransformationOperator(e));
    if ( e->is(Type::IfcCartesianTransformationOperator2D) ) return IfcSchemaEntity(new IfcCartesianTransformationOperator2D(e));
    if ( e->is(Type::IfcCartesianTransformationOperator2DnonUniform) ) return IfcSchemaEntity(new IfcCartesianTransformationOperator2DnonUniform(e));
    if ( e->is(Type::IfcCartesianTransformationOperator3D) ) return IfcSchemaEntity(new IfcCartesianTransformationOperator3D(e));
    if ( e->is(Type::IfcCartesianTransformationOperator3DnonUniform) ) return IfcSchemaEntity(new IfcCartesianTransformationOperator3DnonUniform(e));
    if ( e->is(Type::IfcCenterLineProfileDef) ) return IfcSchemaEntity(new IfcCenterLineProfileDef(e));
    if ( e->is(Type::IfcChamferEdgeFeature) ) return IfcSchemaEntity(new IfcChamferEdgeFeature(e));
    if ( e->is(Type::IfcChillerType) ) return IfcSchemaEntity(new IfcChillerType(e));
    if ( e->is(Type::IfcCircle) ) return IfcSchemaEntity(new IfcCircle(e));
    if ( e->is(Type::IfcCircleHollowProfileDef) ) return IfcSchemaEntity(new IfcCircleHollowProfileDef(e));
    if ( e->is(Type::IfcCircleProfileDef) ) return IfcSchemaEntity(new IfcCircleProfileDef(e));
    if ( e->is(Type::IfcClassification) ) return IfcSchemaEntity(new IfcClassification(e));
    if ( e->is(Type::IfcClassificationItem) ) return IfcSchemaEntity(new IfcClassificationItem(e));
    if ( e->is(Type::IfcClassificationItemRelationship) ) return IfcSchemaEntity(new IfcClassificationItemRelationship(e));
    if ( e->is(Type::IfcClassificationNotation) ) return IfcSchemaEntity(new IfcClassificationNotation(e));
    if ( e->is(Type::IfcClassificationNotationFacet) ) return IfcSchemaEntity(new IfcClassificationNotationFacet(e));
    if ( e->is(Type::IfcClassificationReference) ) return IfcSchemaEntity(new IfcClassificationReference(e));
    if ( e->is(Type::IfcClosedShell) ) return IfcSchemaEntity(new IfcClosedShell(e));
    if ( e->is(Type::IfcCoilType) ) return IfcSchemaEntity(new IfcCoilType(e));
    if ( e->is(Type::IfcColourRgb) ) return IfcSchemaEntity(new IfcColourRgb(e));
    if ( e->is(Type::IfcColourSpecification) ) return IfcSchemaEntity(new IfcColourSpecification(e));
    if ( e->is(Type::IfcColumn) ) return IfcSchemaEntity(new IfcColumn(e));
    if ( e->is(Type::IfcColumnType) ) return IfcSchemaEntity(new IfcColumnType(e));
    if ( e->is(Type::IfcComplexProperty) ) return IfcSchemaEntity(new IfcComplexProperty(e));
    if ( e->is(Type::IfcCompositeCurve) ) return IfcSchemaEntity(new IfcCompositeCurve(e));
    if ( e->is(Type::IfcCompositeCurveSegment) ) return IfcSchemaEntity(new IfcCompositeCurveSegment(e));
    if ( e->is(Type::IfcCompositeProfileDef) ) return IfcSchemaEntity(new IfcCompositeProfileDef(e));
    if ( e->is(Type::IfcCompressorType) ) return IfcSchemaEntity(new IfcCompressorType(e));
    if ( e->is(Type::IfcCondenserType) ) return IfcSchemaEntity(new IfcCondenserType(e));
    if ( e->is(Type::IfcCondition) ) return IfcSchemaEntity(new IfcCondition(e));
    if ( e->is(Type::IfcConditionCriterion) ) return IfcSchemaEntity(new IfcConditionCriterion(e));
    if ( e->is(Type::IfcConic) ) return IfcSchemaEntity(new IfcConic(e));
    if ( e->is(Type::IfcConnectedFaceSet) ) return IfcSchemaEntity(new IfcConnectedFaceSet(e));
    if ( e->is(Type::IfcConnectionCurveGeometry) ) return IfcSchemaEntity(new IfcConnectionCurveGeometry(e));
    if ( e->is(Type::IfcConnectionGeometry) ) return IfcSchemaEntity(new IfcConnectionGeometry(e));
    if ( e->is(Type::IfcConnectionPointEccentricity) ) return IfcSchemaEntity(new IfcConnectionPointEccentricity(e));
    if ( e->is(Type::IfcConnectionPointGeometry) ) return IfcSchemaEntity(new IfcConnectionPointGeometry(e));
    if ( e->is(Type::IfcConnectionPortGeometry) ) return IfcSchemaEntity(new IfcConnectionPortGeometry(e));
    if ( e->is(Type::IfcConnectionSurfaceGeometry) ) return IfcSchemaEntity(new IfcConnectionSurfaceGeometry(e));
    if ( e->is(Type::IfcConstraint) ) return IfcSchemaEntity(new IfcConstraint(e));
    if ( e->is(Type::IfcConstraintAggregationRelationship) ) return IfcSchemaEntity(new IfcConstraintAggregationRelationship(e));
    if ( e->is(Type::IfcConstraintClassificationRelationship) ) return IfcSchemaEntity(new IfcConstraintClassificationRelationship(e));
    if ( e->is(Type::IfcConstraintRelationship) ) return IfcSchemaEntity(new IfcConstraintRelationship(e));
    if ( e->is(Type::IfcConstructionEquipmentResource) ) return IfcSchemaEntity(new IfcConstructionEquipmentResource(e));
    if ( e->is(Type::IfcConstructionMaterialResource) ) return IfcSchemaEntity(new IfcConstructionMaterialResource(e));
    if ( e->is(Type::IfcConstructionProductResource) ) return IfcSchemaEntity(new IfcConstructionProductResource(e));
    if ( e->is(Type::IfcConstructionResource) ) return IfcSchemaEntity(new IfcConstructionResource(e));
    if ( e->is(Type::IfcContextDependentUnit) ) return IfcSchemaEntity(new IfcContextDependentUnit(e));
    if ( e->is(Type::IfcControl) ) return IfcSchemaEntity(new IfcControl(e));
    if ( e->is(Type::IfcControllerType) ) return IfcSchemaEntity(new IfcControllerType(e));
    if ( e->is(Type::IfcConversionBasedUnit) ) return IfcSchemaEntity(new IfcConversionBasedUnit(e));
    if ( e->is(Type::IfcCooledBeamType) ) return IfcSchemaEntity(new IfcCooledBeamType(e));
    if ( e->is(Type::IfcCoolingTowerType) ) return IfcSchemaEntity(new IfcCoolingTowerType(e));
    if ( e->is(Type::IfcCoordinatedUniversalTimeOffset) ) return IfcSchemaEntity(new IfcCoordinatedUniversalTimeOffset(e));
    if ( e->is(Type::IfcCostItem) ) return IfcSchemaEntity(new IfcCostItem(e));
    if ( e->is(Type::IfcCostSchedule) ) return IfcSchemaEntity(new IfcCostSchedule(e));
    if ( e->is(Type::IfcCostValue) ) return IfcSchemaEntity(new IfcCostValue(e));
    if ( e->is(Type::IfcCovering) ) return IfcSchemaEntity(new IfcCovering(e));
    if ( e->is(Type::IfcCoveringType) ) return IfcSchemaEntity(new IfcCoveringType(e));
    if ( e->is(Type::IfcCraneRailAShapeProfileDef) ) return IfcSchemaEntity(new IfcCraneRailAShapeProfileDef(e));
    if ( e->is(Type::IfcCraneRailFShapeProfileDef) ) return IfcSchemaEntity(new IfcCraneRailFShapeProfileDef(e));
    if ( e->is(Type::IfcCrewResource) ) return IfcSchemaEntity(new IfcCrewResource(e));
    if ( e->is(Type::IfcCsgPrimitive3D) ) return IfcSchemaEntity(new IfcCsgPrimitive3D(e));
    if ( e->is(Type::IfcCsgSolid) ) return IfcSchemaEntity(new IfcCsgSolid(e));
    if ( e->is(Type::IfcCurrencyRelationship) ) return IfcSchemaEntity(new IfcCurrencyRelationship(e));
    if ( e->is(Type::IfcCurtainWall) ) return IfcSchemaEntity(new IfcCurtainWall(e));
    if ( e->is(Type::IfcCurtainWallType) ) return IfcSchemaEntity(new IfcCurtainWallType(e));
    if ( e->is(Type::IfcCurve) ) return IfcSchemaEntity(new IfcCurve(e));
    if ( e->is(Type::IfcCurveBoundedPlane) ) return IfcSchemaEntity(new IfcCurveBoundedPlane(e));
    if ( e->is(Type::IfcCurveStyle) ) return IfcSchemaEntity(new IfcCurveStyle(e));
    if ( e->is(Type::IfcCurveStyleFont) ) return IfcSchemaEntity(new IfcCurveStyleFont(e));
    if ( e->is(Type::IfcCurveStyleFontAndScaling) ) return IfcSchemaEntity(new IfcCurveStyleFontAndScaling(e));
    if ( e->is(Type::IfcCurveStyleFontPattern) ) return IfcSchemaEntity(new IfcCurveStyleFontPattern(e));
    if ( e->is(Type::IfcDamperType) ) return IfcSchemaEntity(new IfcDamperType(e));
    if ( e->is(Type::IfcDateAndTime) ) return IfcSchemaEntity(new IfcDateAndTime(e));
    if ( e->is(Type::IfcDefinedSymbol) ) return IfcSchemaEntity(new IfcDefinedSymbol(e));
    if ( e->is(Type::IfcDerivedProfileDef) ) return IfcSchemaEntity(new IfcDerivedProfileDef(e));
    if ( e->is(Type::IfcDerivedUnit) ) return IfcSchemaEntity(new IfcDerivedUnit(e));
    if ( e->is(Type::IfcDerivedUnitElement) ) return IfcSchemaEntity(new IfcDerivedUnitElement(e));
    if ( e->is(Type::IfcDiameterDimension) ) return IfcSchemaEntity(new IfcDiameterDimension(e));
    if ( e->is(Type::IfcDimensionCalloutRelationship) ) return IfcSchemaEntity(new IfcDimensionCalloutRelationship(e));
    if ( e->is(Type::IfcDimensionCurve) ) return IfcSchemaEntity(new IfcDimensionCurve(e));
    if ( e->is(Type::IfcDimensionCurveDirectedCallout) ) return IfcSchemaEntity(new IfcDimensionCurveDirectedCallout(e));
    if ( e->is(Type::IfcDimensionCurveTerminator) ) return IfcSchemaEntity(new IfcDimensionCurveTerminator(e));
    if ( e->is(Type::IfcDimensionPair) ) return IfcSchemaEntity(new IfcDimensionPair(e));
    if ( e->is(Type::IfcDimensionalExponents) ) return IfcSchemaEntity(new IfcDimensionalExponents(e));
    if ( e->is(Type::IfcDirection) ) return IfcSchemaEntity(new IfcDirection(e));
    if ( e->is(Type::IfcDiscreteAccessory) ) return IfcSchemaEntity(new IfcDiscreteAccessory(e));
    if ( e->is(Type::IfcDiscreteAccessoryType) ) return IfcSchemaEntity(new IfcDiscreteAccessoryType(e));
    if ( e->is(Type::IfcDistributionChamberElement) ) return IfcSchemaEntity(new IfcDistributionChamberElement(e));
    if ( e->is(Type::IfcDistributionChamberElementType) ) return IfcSchemaEntity(new IfcDistributionChamberElementType(e));
    if ( e->is(Type::IfcDistributionControlElement) ) return IfcSchemaEntity(new IfcDistributionControlElement(e));
    if ( e->is(Type::IfcDistributionControlElementType) ) return IfcSchemaEntity(new IfcDistributionControlElementType(e));
    if ( e->is(Type::IfcDistributionElement) ) return IfcSchemaEntity(new IfcDistributionElement(e));
    if ( e->is(Type::IfcDistributionElementType) ) return IfcSchemaEntity(new IfcDistributionElementType(e));
    if ( e->is(Type::IfcDistributionFlowElement) ) return IfcSchemaEntity(new IfcDistributionFlowElement(e));
    if ( e->is(Type::IfcDistributionFlowElementType) ) return IfcSchemaEntity(new IfcDistributionFlowElementType(e));
    if ( e->is(Type::IfcDistributionPort) ) return IfcSchemaEntity(new IfcDistributionPort(e));
    if ( e->is(Type::IfcDocumentElectronicFormat) ) return IfcSchemaEntity(new IfcDocumentElectronicFormat(e));
    if ( e->is(Type::IfcDocumentInformation) ) return IfcSchemaEntity(new IfcDocumentInformation(e));
    if ( e->is(Type::IfcDocumentInformationRelationship) ) return IfcSchemaEntity(new IfcDocumentInformationRelationship(e));
    if ( e->is(Type::IfcDocumentReference) ) return IfcSchemaEntity(new IfcDocumentReference(e));
    if ( e->is(Type::IfcDoor) ) return IfcSchemaEntity(new IfcDoor(e));
    if ( e->is(Type::IfcDoorLiningProperties) ) return IfcSchemaEntity(new IfcDoorLiningProperties(e));
    if ( e->is(Type::IfcDoorPanelProperties) ) return IfcSchemaEntity(new IfcDoorPanelProperties(e));
    if ( e->is(Type::IfcDoorStyle) ) return IfcSchemaEntity(new IfcDoorStyle(e));
    if ( e->is(Type::IfcDraughtingCallout) ) return IfcSchemaEntity(new IfcDraughtingCallout(e));
    if ( e->is(Type::IfcDraughtingCalloutRelationship) ) return IfcSchemaEntity(new IfcDraughtingCalloutRelationship(e));
    if ( e->is(Type::IfcDraughtingPreDefinedColour) ) return IfcSchemaEntity(new IfcDraughtingPreDefinedColour(e));
    if ( e->is(Type::IfcDraughtingPreDefinedCurveFont) ) return IfcSchemaEntity(new IfcDraughtingPreDefinedCurveFont(e));
    if ( e->is(Type::IfcDraughtingPreDefinedTextFont) ) return IfcSchemaEntity(new IfcDraughtingPreDefinedTextFont(e));
    if ( e->is(Type::IfcDuctFittingType) ) return IfcSchemaEntity(new IfcDuctFittingType(e));
    if ( e->is(Type::IfcDuctSegmentType) ) return IfcSchemaEntity(new IfcDuctSegmentType(e));
    if ( e->is(Type::IfcDuctSilencerType) ) return IfcSchemaEntity(new IfcDuctSilencerType(e));
    if ( e->is(Type::IfcEdge) ) return IfcSchemaEntity(new IfcEdge(e));
    if ( e->is(Type::IfcEdgeCurve) ) return IfcSchemaEntity(new IfcEdgeCurve(e));
    if ( e->is(Type::IfcEdgeFeature) ) return IfcSchemaEntity(new IfcEdgeFeature(e));
    if ( e->is(Type::IfcEdgeLoop) ) return IfcSchemaEntity(new IfcEdgeLoop(e));
    if ( e->is(Type::IfcElectricApplianceType) ) return IfcSchemaEntity(new IfcElectricApplianceType(e));
    if ( e->is(Type::IfcElectricDistributionPoint) ) return IfcSchemaEntity(new IfcElectricDistributionPoint(e));
    if ( e->is(Type::IfcElectricFlowStorageDeviceType) ) return IfcSchemaEntity(new IfcElectricFlowStorageDeviceType(e));
    if ( e->is(Type::IfcElectricGeneratorType) ) return IfcSchemaEntity(new IfcElectricGeneratorType(e));
    if ( e->is(Type::IfcElectricHeaterType) ) return IfcSchemaEntity(new IfcElectricHeaterType(e));
    if ( e->is(Type::IfcElectricMotorType) ) return IfcSchemaEntity(new IfcElectricMotorType(e));
    if ( e->is(Type::IfcElectricTimeControlType) ) return IfcSchemaEntity(new IfcElectricTimeControlType(e));
    if ( e->is(Type::IfcElectricalBaseProperties) ) return IfcSchemaEntity(new IfcElectricalBaseProperties(e));
    if ( e->is(Type::IfcElectricalCircuit) ) return IfcSchemaEntity(new IfcElectricalCircuit(e));
    if ( e->is(Type::IfcElectricalElement) ) return IfcSchemaEntity(new IfcElectricalElement(e));
    if ( e->is(Type::IfcElement) ) return IfcSchemaEntity(new IfcElement(e));
    if ( e->is(Type::IfcElementAssembly) ) return IfcSchemaEntity(new IfcElementAssembly(e));
    if ( e->is(Type::IfcElementComponent) ) return IfcSchemaEntity(new IfcElementComponent(e));
    if ( e->is(Type::IfcElementComponentType) ) return IfcSchemaEntity(new IfcElementComponentType(e));
    if ( e->is(Type::IfcElementQuantity) ) return IfcSchemaEntity(new IfcElementQuantity(e));
    if ( e->is(Type::IfcElementType) ) return IfcSchemaEntity(new IfcElementType(e));
    if ( e->is(Type::IfcElementarySurface) ) return IfcSchemaEntity(new IfcElementarySurface(e));
    if ( e->is(Type::IfcEllipse) ) return IfcSchemaEntity(new IfcEllipse(e));
    if ( e->is(Type::IfcEllipseProfileDef) ) return IfcSchemaEntity(new IfcEllipseProfileDef(e));
    if ( e->is(Type::IfcEnergyConversionDevice) ) return IfcSchemaEntity(new IfcEnergyConversionDevice(e));
    if ( e->is(Type::IfcEnergyConversionDeviceType) ) return IfcSchemaEntity(new IfcEnergyConversionDeviceType(e));
    if ( e->is(Type::IfcEnergyProperties) ) return IfcSchemaEntity(new IfcEnergyProperties(e));
    if ( e->is(Type::IfcEnvironmentalImpactValue) ) return IfcSchemaEntity(new IfcEnvironmentalImpactValue(e));
    if ( e->is(Type::IfcEquipmentElement) ) return IfcSchemaEntity(new IfcEquipmentElement(e));
    if ( e->is(Type::IfcEquipmentStandard) ) return IfcSchemaEntity(new IfcEquipmentStandard(e));
    if ( e->is(Type::IfcEvaporativeCoolerType) ) return IfcSchemaEntity(new IfcEvaporativeCoolerType(e));
    if ( e->is(Type::IfcEvaporatorType) ) return IfcSchemaEntity(new IfcEvaporatorType(e));
    if ( e->is(Type::IfcExtendedMaterialProperties) ) return IfcSchemaEntity(new IfcExtendedMaterialProperties(e));
    if ( e->is(Type::IfcExternalReference) ) return IfcSchemaEntity(new IfcExternalReference(e));
    if ( e->is(Type::IfcExternallyDefinedHatchStyle) ) return IfcSchemaEntity(new IfcExternallyDefinedHatchStyle(e));
    if ( e->is(Type::IfcExternallyDefinedSurfaceStyle) ) return IfcSchemaEntity(new IfcExternallyDefinedSurfaceStyle(e));
    if ( e->is(Type::IfcExternallyDefinedSymbol) ) return IfcSchemaEntity(new IfcExternallyDefinedSymbol(e));
    if ( e->is(Type::IfcExternallyDefinedTextFont) ) return IfcSchemaEntity(new IfcExternallyDefinedTextFont(e));
    if ( e->is(Type::IfcExtrudedAreaSolid) ) return IfcSchemaEntity(new IfcExtrudedAreaSolid(e));
    if ( e->is(Type::IfcFace) ) return IfcSchemaEntity(new IfcFace(e));
    if ( e->is(Type::IfcFaceBasedSurfaceModel) ) return IfcSchemaEntity(new IfcFaceBasedSurfaceModel(e));
    if ( e->is(Type::IfcFaceBound) ) return IfcSchemaEntity(new IfcFaceBound(e));
    if ( e->is(Type::IfcFaceOuterBound) ) return IfcSchemaEntity(new IfcFaceOuterBound(e));
    if ( e->is(Type::IfcFaceSurface) ) return IfcSchemaEntity(new IfcFaceSurface(e));
    if ( e->is(Type::IfcFacetedBrep) ) return IfcSchemaEntity(new IfcFacetedBrep(e));
    if ( e->is(Type::IfcFacetedBrepWithVoids) ) return IfcSchemaEntity(new IfcFacetedBrepWithVoids(e));
    if ( e->is(Type::IfcFailureConnectionCondition) ) return IfcSchemaEntity(new IfcFailureConnectionCondition(e));
    if ( e->is(Type::IfcFanType) ) return IfcSchemaEntity(new IfcFanType(e));
    if ( e->is(Type::IfcFastener) ) return IfcSchemaEntity(new IfcFastener(e));
    if ( e->is(Type::IfcFastenerType) ) return IfcSchemaEntity(new IfcFastenerType(e));
    if ( e->is(Type::IfcFeatureElement) ) return IfcSchemaEntity(new IfcFeatureElement(e));
    if ( e->is(Type::IfcFeatureElementAddition) ) return IfcSchemaEntity(new IfcFeatureElementAddition(e));
    if ( e->is(Type::IfcFeatureElementSubtraction) ) return IfcSchemaEntity(new IfcFeatureElementSubtraction(e));
    if ( e->is(Type::IfcFillAreaStyle) ) return IfcSchemaEntity(new IfcFillAreaStyle(e));
    if ( e->is(Type::IfcFillAreaStyleHatching) ) return IfcSchemaEntity(new IfcFillAreaStyleHatching(e));
    if ( e->is(Type::IfcFillAreaStyleTileSymbolWithStyle) ) return IfcSchemaEntity(new IfcFillAreaStyleTileSymbolWithStyle(e));
    if ( e->is(Type::IfcFillAreaStyleTiles) ) return IfcSchemaEntity(new IfcFillAreaStyleTiles(e));
    if ( e->is(Type::IfcFilterType) ) return IfcSchemaEntity(new IfcFilterType(e));
    if ( e->is(Type::IfcFireSuppressionTerminalType) ) return IfcSchemaEntity(new IfcFireSuppressionTerminalType(e));
    if ( e->is(Type::IfcFlowController) ) return IfcSchemaEntity(new IfcFlowController(e));
    if ( e->is(Type::IfcFlowControllerType) ) return IfcSchemaEntity(new IfcFlowControllerType(e));
    if ( e->is(Type::IfcFlowFitting) ) return IfcSchemaEntity(new IfcFlowFitting(e));
    if ( e->is(Type::IfcFlowFittingType) ) return IfcSchemaEntity(new IfcFlowFittingType(e));
    if ( e->is(Type::IfcFlowInstrumentType) ) return IfcSchemaEntity(new IfcFlowInstrumentType(e));
    if ( e->is(Type::IfcFlowMeterType) ) return IfcSchemaEntity(new IfcFlowMeterType(e));
    if ( e->is(Type::IfcFlowMovingDevice) ) return IfcSchemaEntity(new IfcFlowMovingDevice(e));
    if ( e->is(Type::IfcFlowMovingDeviceType) ) return IfcSchemaEntity(new IfcFlowMovingDeviceType(e));
    if ( e->is(Type::IfcFlowSegment) ) return IfcSchemaEntity(new IfcFlowSegment(e));
    if ( e->is(Type::IfcFlowSegmentType) ) return IfcSchemaEntity(new IfcFlowSegmentType(e));
    if ( e->is(Type::IfcFlowStorageDevice) ) return IfcSchemaEntity(new IfcFlowStorageDevice(e));
    if ( e->is(Type::IfcFlowStorageDeviceType) ) return IfcSchemaEntity(new IfcFlowStorageDeviceType(e));
    if ( e->is(Type::IfcFlowTerminal) ) return IfcSchemaEntity(new IfcFlowTerminal(e));
    if ( e->is(Type::IfcFlowTerminalType) ) return IfcSchemaEntity(new IfcFlowTerminalType(e));
    if ( e->is(Type::IfcFlowTreatmentDevice) ) return IfcSchemaEntity(new IfcFlowTreatmentDevice(e));
    if ( e->is(Type::IfcFlowTreatmentDeviceType) ) return IfcSchemaEntity(new IfcFlowTreatmentDeviceType(e));
    if ( e->is(Type::IfcFluidFlowProperties) ) return IfcSchemaEntity(new IfcFluidFlowProperties(e));
    if ( e->is(Type::IfcFooting) ) return IfcSchemaEntity(new IfcFooting(e));
    if ( e->is(Type::IfcFuelProperties) ) return IfcSchemaEntity(new IfcFuelProperties(e));
    if ( e->is(Type::IfcFurnishingElement) ) return IfcSchemaEntity(new IfcFurnishingElement(e));
    if ( e->is(Type::IfcFurnishingElementType) ) return IfcSchemaEntity(new IfcFurnishingElementType(e));
    if ( e->is(Type::IfcFurnitureStandard) ) return IfcSchemaEntity(new IfcFurnitureStandard(e));
    if ( e->is(Type::IfcFurnitureType) ) return IfcSchemaEntity(new IfcFurnitureType(e));
    if ( e->is(Type::IfcGasTerminalType) ) return IfcSchemaEntity(new IfcGasTerminalType(e));
    if ( e->is(Type::IfcGeneralMaterialProperties) ) return IfcSchemaEntity(new IfcGeneralMaterialProperties(e));
    if ( e->is(Type::IfcGeneralProfileProperties) ) return IfcSchemaEntity(new IfcGeneralProfileProperties(e));
    if ( e->is(Type::IfcGeometricCurveSet) ) return IfcSchemaEntity(new IfcGeometricCurveSet(e));
    if ( e->is(Type::IfcGeometricRepresentationContext) ) return IfcSchemaEntity(new IfcGeometricRepresentationContext(e));
    if ( e->is(Type::IfcGeometricRepresentationItem) ) return IfcSchemaEntity(new IfcGeometricRepresentationItem(e));
    if ( e->is(Type::IfcGeometricRepresentationSubContext) ) return IfcSchemaEntity(new IfcGeometricRepresentationSubContext(e));
    if ( e->is(Type::IfcGeometricSet) ) return IfcSchemaEntity(new IfcGeometricSet(e));
    if ( e->is(Type::IfcGrid) ) return IfcSchemaEntity(new IfcGrid(e));
    if ( e->is(Type::IfcGridAxis) ) return IfcSchemaEntity(new IfcGridAxis(e));
    if ( e->is(Type::IfcGridPlacement) ) return IfcSchemaEntity(new IfcGridPlacement(e));
    if ( e->is(Type::IfcGroup) ) return IfcSchemaEntity(new IfcGroup(e));
    if ( e->is(Type::IfcHalfSpaceSolid) ) return IfcSchemaEntity(new IfcHalfSpaceSolid(e));
    if ( e->is(Type::IfcHeatExchangerType) ) return IfcSchemaEntity(new IfcHeatExchangerType(e));
    if ( e->is(Type::IfcHumidifierType) ) return IfcSchemaEntity(new IfcHumidifierType(e));
    if ( e->is(Type::IfcHygroscopicMaterialProperties) ) return IfcSchemaEntity(new IfcHygroscopicMaterialProperties(e));
    if ( e->is(Type::IfcIShapeProfileDef) ) return IfcSchemaEntity(new IfcIShapeProfileDef(e));
    if ( e->is(Type::IfcImageTexture) ) return IfcSchemaEntity(new IfcImageTexture(e));
    if ( e->is(Type::IfcInventory) ) return IfcSchemaEntity(new IfcInventory(e));
    if ( e->is(Type::IfcIrregularTimeSeries) ) return IfcSchemaEntity(new IfcIrregularTimeSeries(e));
    if ( e->is(Type::IfcIrregularTimeSeriesValue) ) return IfcSchemaEntity(new IfcIrregularTimeSeriesValue(e));
    if ( e->is(Type::IfcJunctionBoxType) ) return IfcSchemaEntity(new IfcJunctionBoxType(e));
    if ( e->is(Type::IfcLShapeProfileDef) ) return IfcSchemaEntity(new IfcLShapeProfileDef(e));
    if ( e->is(Type::IfcLaborResource) ) return IfcSchemaEntity(new IfcLaborResource(e));
    if ( e->is(Type::IfcLampType) ) return IfcSchemaEntity(new IfcLampType(e));
    if ( e->is(Type::IfcLibraryInformation) ) return IfcSchemaEntity(new IfcLibraryInformation(e));
    if ( e->is(Type::IfcLibraryReference) ) return IfcSchemaEntity(new IfcLibraryReference(e));
    if ( e->is(Type::IfcLightDistributionData) ) return IfcSchemaEntity(new IfcLightDistributionData(e));
    if ( e->is(Type::IfcLightFixtureType) ) return IfcSchemaEntity(new IfcLightFixtureType(e));
    if ( e->is(Type::IfcLightIntensityDistribution) ) return IfcSchemaEntity(new IfcLightIntensityDistribution(e));
    if ( e->is(Type::IfcLightSource) ) return IfcSchemaEntity(new IfcLightSource(e));
    if ( e->is(Type::IfcLightSourceAmbient) ) return IfcSchemaEntity(new IfcLightSourceAmbient(e));
    if ( e->is(Type::IfcLightSourceDirectional) ) return IfcSchemaEntity(new IfcLightSourceDirectional(e));
    if ( e->is(Type::IfcLightSourceGoniometric) ) return IfcSchemaEntity(new IfcLightSourceGoniometric(e));
    if ( e->is(Type::IfcLightSourcePositional) ) return IfcSchemaEntity(new IfcLightSourcePositional(e));
    if ( e->is(Type::IfcLightSourceSpot) ) return IfcSchemaEntity(new IfcLightSourceSpot(e));
    if ( e->is(Type::IfcLine) ) return IfcSchemaEntity(new IfcLine(e));
    if ( e->is(Type::IfcLinearDimension) ) return IfcSchemaEntity(new IfcLinearDimension(e));
    if ( e->is(Type::IfcLocalPlacement) ) return IfcSchemaEntity(new IfcLocalPlacement(e));
    if ( e->is(Type::IfcLocalTime) ) return IfcSchemaEntity(new IfcLocalTime(e));
    if ( e->is(Type::IfcLoop) ) return IfcSchemaEntity(new IfcLoop(e));
    if ( e->is(Type::IfcManifoldSolidBrep) ) return IfcSchemaEntity(new IfcManifoldSolidBrep(e));
    if ( e->is(Type::IfcMappedItem) ) return IfcSchemaEntity(new IfcMappedItem(e));
    if ( e->is(Type::IfcMaterial) ) return IfcSchemaEntity(new IfcMaterial(e));
    if ( e->is(Type::IfcMaterialClassificationRelationship) ) return IfcSchemaEntity(new IfcMaterialClassificationRelationship(e));
    if ( e->is(Type::IfcMaterialDefinitionRepresentation) ) return IfcSchemaEntity(new IfcMaterialDefinitionRepresentation(e));
    if ( e->is(Type::IfcMaterialLayer) ) return IfcSchemaEntity(new IfcMaterialLayer(e));
    if ( e->is(Type::IfcMaterialLayerSet) ) return IfcSchemaEntity(new IfcMaterialLayerSet(e));
    if ( e->is(Type::IfcMaterialLayerSetUsage) ) return IfcSchemaEntity(new IfcMaterialLayerSetUsage(e));
    if ( e->is(Type::IfcMaterialList) ) return IfcSchemaEntity(new IfcMaterialList(e));
    if ( e->is(Type::IfcMaterialProperties) ) return IfcSchemaEntity(new IfcMaterialProperties(e));
    if ( e->is(Type::IfcMeasureWithUnit) ) return IfcSchemaEntity(new IfcMeasureWithUnit(e));
    if ( e->is(Type::IfcMechanicalConcreteMaterialProperties) ) return IfcSchemaEntity(new IfcMechanicalConcreteMaterialProperties(e));
    if ( e->is(Type::IfcMechanicalFastener) ) return IfcSchemaEntity(new IfcMechanicalFastener(e));
    if ( e->is(Type::IfcMechanicalFastenerType) ) return IfcSchemaEntity(new IfcMechanicalFastenerType(e));
    if ( e->is(Type::IfcMechanicalMaterialProperties) ) return IfcSchemaEntity(new IfcMechanicalMaterialProperties(e));
    if ( e->is(Type::IfcMechanicalSteelMaterialProperties) ) return IfcSchemaEntity(new IfcMechanicalSteelMaterialProperties(e));
    if ( e->is(Type::IfcMember) ) return IfcSchemaEntity(new IfcMember(e));
    if ( e->is(Type::IfcMemberType) ) return IfcSchemaEntity(new IfcMemberType(e));
    if ( e->is(Type::IfcMetric) ) return IfcSchemaEntity(new IfcMetric(e));
    if ( e->is(Type::IfcMonetaryUnit) ) return IfcSchemaEntity(new IfcMonetaryUnit(e));
    if ( e->is(Type::IfcMotorConnectionType) ) return IfcSchemaEntity(new IfcMotorConnectionType(e));
    if ( e->is(Type::IfcMove) ) return IfcSchemaEntity(new IfcMove(e));
    if ( e->is(Type::IfcNamedUnit) ) return IfcSchemaEntity(new IfcNamedUnit(e));
    if ( e->is(Type::IfcObject) ) return IfcSchemaEntity(new IfcObject(e));
    if ( e->is(Type::IfcObjectDefinition) ) return IfcSchemaEntity(new IfcObjectDefinition(e));
    if ( e->is(Type::IfcObjectPlacement) ) return IfcSchemaEntity(new IfcObjectPlacement(e));
    if ( e->is(Type::IfcObjective) ) return IfcSchemaEntity(new IfcObjective(e));
    if ( e->is(Type::IfcOccupant) ) return IfcSchemaEntity(new IfcOccupant(e));
    if ( e->is(Type::IfcOffsetCurve2D) ) return IfcSchemaEntity(new IfcOffsetCurve2D(e));
    if ( e->is(Type::IfcOffsetCurve3D) ) return IfcSchemaEntity(new IfcOffsetCurve3D(e));
    if ( e->is(Type::IfcOneDirectionRepeatFactor) ) return IfcSchemaEntity(new IfcOneDirectionRepeatFactor(e));
    if ( e->is(Type::IfcOpenShell) ) return IfcSchemaEntity(new IfcOpenShell(e));
    if ( e->is(Type::IfcOpeningElement) ) return IfcSchemaEntity(new IfcOpeningElement(e));
    if ( e->is(Type::IfcOpticalMaterialProperties) ) return IfcSchemaEntity(new IfcOpticalMaterialProperties(e));
    if ( e->is(Type::IfcOrderAction) ) return IfcSchemaEntity(new IfcOrderAction(e));
    if ( e->is(Type::IfcOrganization) ) return IfcSchemaEntity(new IfcOrganization(e));
    if ( e->is(Type::IfcOrganizationRelationship) ) return IfcSchemaEntity(new IfcOrganizationRelationship(e));
    if ( e->is(Type::IfcOrientedEdge) ) return IfcSchemaEntity(new IfcOrientedEdge(e));
    if ( e->is(Type::IfcOutletType) ) return IfcSchemaEntity(new IfcOutletType(e));
    if ( e->is(Type::IfcOwnerHistory) ) return IfcSchemaEntity(new IfcOwnerHistory(e));
    if ( e->is(Type::IfcParameterizedProfileDef) ) return IfcSchemaEntity(new IfcParameterizedProfileDef(e));
    if ( e->is(Type::IfcPath) ) return IfcSchemaEntity(new IfcPath(e));
    if ( e->is(Type::IfcPerformanceHistory) ) return IfcSchemaEntity(new IfcPerformanceHistory(e));
    if ( e->is(Type::IfcPermeableCoveringProperties) ) return IfcSchemaEntity(new IfcPermeableCoveringProperties(e));
    if ( e->is(Type::IfcPermit) ) return IfcSchemaEntity(new IfcPermit(e));
    if ( e->is(Type::IfcPerson) ) return IfcSchemaEntity(new IfcPerson(e));
    if ( e->is(Type::IfcPersonAndOrganization) ) return IfcSchemaEntity(new IfcPersonAndOrganization(e));
    if ( e->is(Type::IfcPhysicalComplexQuantity) ) return IfcSchemaEntity(new IfcPhysicalComplexQuantity(e));
    if ( e->is(Type::IfcPhysicalQuantity) ) return IfcSchemaEntity(new IfcPhysicalQuantity(e));
    if ( e->is(Type::IfcPhysicalSimpleQuantity) ) return IfcSchemaEntity(new IfcPhysicalSimpleQuantity(e));
    if ( e->is(Type::IfcPile) ) return IfcSchemaEntity(new IfcPile(e));
    if ( e->is(Type::IfcPipeFittingType) ) return IfcSchemaEntity(new IfcPipeFittingType(e));
    if ( e->is(Type::IfcPipeSegmentType) ) return IfcSchemaEntity(new IfcPipeSegmentType(e));
    if ( e->is(Type::IfcPixelTexture) ) return IfcSchemaEntity(new IfcPixelTexture(e));
    if ( e->is(Type::IfcPlacement) ) return IfcSchemaEntity(new IfcPlacement(e));
    if ( e->is(Type::IfcPlanarBox) ) return IfcSchemaEntity(new IfcPlanarBox(e));
    if ( e->is(Type::IfcPlanarExtent) ) return IfcSchemaEntity(new IfcPlanarExtent(e));
    if ( e->is(Type::IfcPlane) ) return IfcSchemaEntity(new IfcPlane(e));
    if ( e->is(Type::IfcPlate) ) return IfcSchemaEntity(new IfcPlate(e));
    if ( e->is(Type::IfcPlateType) ) return IfcSchemaEntity(new IfcPlateType(e));
    if ( e->is(Type::IfcPoint) ) return IfcSchemaEntity(new IfcPoint(e));
    if ( e->is(Type::IfcPointOnCurve) ) return IfcSchemaEntity(new IfcPointOnCurve(e));
    if ( e->is(Type::IfcPointOnSurface) ) return IfcSchemaEntity(new IfcPointOnSurface(e));
    if ( e->is(Type::IfcPolyLoop) ) return IfcSchemaEntity(new IfcPolyLoop(e));
    if ( e->is(Type::IfcPolygonalBoundedHalfSpace) ) return IfcSchemaEntity(new IfcPolygonalBoundedHalfSpace(e));
    if ( e->is(Type::IfcPolyline) ) return IfcSchemaEntity(new IfcPolyline(e));
    if ( e->is(Type::IfcPort) ) return IfcSchemaEntity(new IfcPort(e));
    if ( e->is(Type::IfcPostalAddress) ) return IfcSchemaEntity(new IfcPostalAddress(e));
    if ( e->is(Type::IfcPreDefinedColour) ) return IfcSchemaEntity(new IfcPreDefinedColour(e));
    if ( e->is(Type::IfcPreDefinedCurveFont) ) return IfcSchemaEntity(new IfcPreDefinedCurveFont(e));
    if ( e->is(Type::IfcPreDefinedDimensionSymbol) ) return IfcSchemaEntity(new IfcPreDefinedDimensionSymbol(e));
    if ( e->is(Type::IfcPreDefinedItem) ) return IfcSchemaEntity(new IfcPreDefinedItem(e));
    if ( e->is(Type::IfcPreDefinedPointMarkerSymbol) ) return IfcSchemaEntity(new IfcPreDefinedPointMarkerSymbol(e));
    if ( e->is(Type::IfcPreDefinedSymbol) ) return IfcSchemaEntity(new IfcPreDefinedSymbol(e));
    if ( e->is(Type::IfcPreDefinedTerminatorSymbol) ) return IfcSchemaEntity(new IfcPreDefinedTerminatorSymbol(e));
    if ( e->is(Type::IfcPreDefinedTextFont) ) return IfcSchemaEntity(new IfcPreDefinedTextFont(e));
    if ( e->is(Type::IfcPresentationLayerAssignment) ) return IfcSchemaEntity(new IfcPresentationLayerAssignment(e));
    if ( e->is(Type::IfcPresentationLayerWithStyle) ) return IfcSchemaEntity(new IfcPresentationLayerWithStyle(e));
    if ( e->is(Type::IfcPresentationStyle) ) return IfcSchemaEntity(new IfcPresentationStyle(e));
    if ( e->is(Type::IfcPresentationStyleAssignment) ) return IfcSchemaEntity(new IfcPresentationStyleAssignment(e));
    if ( e->is(Type::IfcProcedure) ) return IfcSchemaEntity(new IfcProcedure(e));
    if ( e->is(Type::IfcProcess) ) return IfcSchemaEntity(new IfcProcess(e));
    if ( e->is(Type::IfcProduct) ) return IfcSchemaEntity(new IfcProduct(e));
    if ( e->is(Type::IfcProductDefinitionShape) ) return IfcSchemaEntity(new IfcProductDefinitionShape(e));
    if ( e->is(Type::IfcProductRepresentation) ) return IfcSchemaEntity(new IfcProductRepresentation(e));
    if ( e->is(Type::IfcProductsOfCombustionProperties) ) return IfcSchemaEntity(new IfcProductsOfCombustionProperties(e));
    if ( e->is(Type::IfcProfileDef) ) return IfcSchemaEntity(new IfcProfileDef(e));
    if ( e->is(Type::IfcProfileProperties) ) return IfcSchemaEntity(new IfcProfileProperties(e));
    if ( e->is(Type::IfcProject) ) return IfcSchemaEntity(new IfcProject(e));
    if ( e->is(Type::IfcProjectOrder) ) return IfcSchemaEntity(new IfcProjectOrder(e));
    if ( e->is(Type::IfcProjectOrderRecord) ) return IfcSchemaEntity(new IfcProjectOrderRecord(e));
    if ( e->is(Type::IfcProjectionCurve) ) return IfcSchemaEntity(new IfcProjectionCurve(e));
    if ( e->is(Type::IfcProjectionElement) ) return IfcSchemaEntity(new IfcProjectionElement(e));
    if ( e->is(Type::IfcProperty) ) return IfcSchemaEntity(new IfcProperty(e));
    if ( e->is(Type::IfcPropertyBoundedValue) ) return IfcSchemaEntity(new IfcPropertyBoundedValue(e));
    if ( e->is(Type::IfcPropertyConstraintRelationship) ) return IfcSchemaEntity(new IfcPropertyConstraintRelationship(e));
    if ( e->is(Type::IfcPropertyDefinition) ) return IfcSchemaEntity(new IfcPropertyDefinition(e));
    if ( e->is(Type::IfcPropertyDependencyRelationship) ) return IfcSchemaEntity(new IfcPropertyDependencyRelationship(e));
    if ( e->is(Type::IfcPropertyEnumeratedValue) ) return IfcSchemaEntity(new IfcPropertyEnumeratedValue(e));
    if ( e->is(Type::IfcPropertyEnumeration) ) return IfcSchemaEntity(new IfcPropertyEnumeration(e));
    if ( e->is(Type::IfcPropertyListValue) ) return IfcSchemaEntity(new IfcPropertyListValue(e));
    if ( e->is(Type::IfcPropertyReferenceValue) ) return IfcSchemaEntity(new IfcPropertyReferenceValue(e));
    if ( e->is(Type::IfcPropertySet) ) return IfcSchemaEntity(new IfcPropertySet(e));
    if ( e->is(Type::IfcPropertySetDefinition) ) return IfcSchemaEntity(new IfcPropertySetDefinition(e));
    if ( e->is(Type::IfcPropertySingleValue) ) return IfcSchemaEntity(new IfcPropertySingleValue(e));
    if ( e->is(Type::IfcPropertyTableValue) ) return IfcSchemaEntity(new IfcPropertyTableValue(e));
    if ( e->is(Type::IfcProtectiveDeviceType) ) return IfcSchemaEntity(new IfcProtectiveDeviceType(e));
    if ( e->is(Type::IfcProxy) ) return IfcSchemaEntity(new IfcProxy(e));
    if ( e->is(Type::IfcPumpType) ) return IfcSchemaEntity(new IfcPumpType(e));
    if ( e->is(Type::IfcQuantityArea) ) return IfcSchemaEntity(new IfcQuantityArea(e));
    if ( e->is(Type::IfcQuantityCount) ) return IfcSchemaEntity(new IfcQuantityCount(e));
    if ( e->is(Type::IfcQuantityLength) ) return IfcSchemaEntity(new IfcQuantityLength(e));
    if ( e->is(Type::IfcQuantityTime) ) return IfcSchemaEntity(new IfcQuantityTime(e));
    if ( e->is(Type::IfcQuantityVolume) ) return IfcSchemaEntity(new IfcQuantityVolume(e));
    if ( e->is(Type::IfcQuantityWeight) ) return IfcSchemaEntity(new IfcQuantityWeight(e));
    if ( e->is(Type::IfcRadiusDimension) ) return IfcSchemaEntity(new IfcRadiusDimension(e));
    if ( e->is(Type::IfcRailing) ) return IfcSchemaEntity(new IfcRailing(e));
    if ( e->is(Type::IfcRailingType) ) return IfcSchemaEntity(new IfcRailingType(e));
    if ( e->is(Type::IfcRamp) ) return IfcSchemaEntity(new IfcRamp(e));
    if ( e->is(Type::IfcRampFlight) ) return IfcSchemaEntity(new IfcRampFlight(e));
    if ( e->is(Type::IfcRampFlightType) ) return IfcSchemaEntity(new IfcRampFlightType(e));
    if ( e->is(Type::IfcRationalBezierCurve) ) return IfcSchemaEntity(new IfcRationalBezierCurve(e));
    if ( e->is(Type::IfcRectangleHollowProfileDef) ) return IfcSchemaEntity(new IfcRectangleHollowProfileDef(e));
    if ( e->is(Type::IfcRectangleProfileDef) ) return IfcSchemaEntity(new IfcRectangleProfileDef(e));
    if ( e->is(Type::IfcRectangularPyramid) ) return IfcSchemaEntity(new IfcRectangularPyramid(e));
    if ( e->is(Type::IfcRectangularTrimmedSurface) ) return IfcSchemaEntity(new IfcRectangularTrimmedSurface(e));
    if ( e->is(Type::IfcReferencesValueDocument) ) return IfcSchemaEntity(new IfcReferencesValueDocument(e));
    if ( e->is(Type::IfcRegularTimeSeries) ) return IfcSchemaEntity(new IfcRegularTimeSeries(e));
    if ( e->is(Type::IfcReinforcementBarProperties) ) return IfcSchemaEntity(new IfcReinforcementBarProperties(e));
    if ( e->is(Type::IfcReinforcementDefinitionProperties) ) return IfcSchemaEntity(new IfcReinforcementDefinitionProperties(e));
    if ( e->is(Type::IfcReinforcingBar) ) return IfcSchemaEntity(new IfcReinforcingBar(e));
    if ( e->is(Type::IfcReinforcingElement) ) return IfcSchemaEntity(new IfcReinforcingElement(e));
    if ( e->is(Type::IfcReinforcingMesh) ) return IfcSchemaEntity(new IfcReinforcingMesh(e));
    if ( e->is(Type::IfcRelAggregates) ) return IfcSchemaEntity(new IfcRelAggregates(e));
    if ( e->is(Type::IfcRelAssigns) ) return IfcSchemaEntity(new IfcRelAssigns(e));
    if ( e->is(Type::IfcRelAssignsTasks) ) return IfcSchemaEntity(new IfcRelAssignsTasks(e));
    if ( e->is(Type::IfcRelAssignsToActor) ) return IfcSchemaEntity(new IfcRelAssignsToActor(e));
    if ( e->is(Type::IfcRelAssignsToControl) ) return IfcSchemaEntity(new IfcRelAssignsToControl(e));
    if ( e->is(Type::IfcRelAssignsToGroup) ) return IfcSchemaEntity(new IfcRelAssignsToGroup(e));
    if ( e->is(Type::IfcRelAssignsToProcess) ) return IfcSchemaEntity(new IfcRelAssignsToProcess(e));
    if ( e->is(Type::IfcRelAssignsToProduct) ) return IfcSchemaEntity(new IfcRelAssignsToProduct(e));
    if ( e->is(Type::IfcRelAssignsToProjectOrder) ) return IfcSchemaEntity(new IfcRelAssignsToProjectOrder(e));
    if ( e->is(Type::IfcRelAssignsToResource) ) return IfcSchemaEntity(new IfcRelAssignsToResource(e));
    if ( e->is(Type::IfcRelAssociates) ) return IfcSchemaEntity(new IfcRelAssociates(e));
    if ( e->is(Type::IfcRelAssociatesAppliedValue) ) return IfcSchemaEntity(new IfcRelAssociatesAppliedValue(e));
    if ( e->is(Type::IfcRelAssociatesApproval) ) return IfcSchemaEntity(new IfcRelAssociatesApproval(e));
    if ( e->is(Type::IfcRelAssociatesClassification) ) return IfcSchemaEntity(new IfcRelAssociatesClassification(e));
    if ( e->is(Type::IfcRelAssociatesConstraint) ) return IfcSchemaEntity(new IfcRelAssociatesConstraint(e));
    if ( e->is(Type::IfcRelAssociatesDocument) ) return IfcSchemaEntity(new IfcRelAssociatesDocument(e));
    if ( e->is(Type::IfcRelAssociatesLibrary) ) return IfcSchemaEntity(new IfcRelAssociatesLibrary(e));
    if ( e->is(Type::IfcRelAssociatesMaterial) ) return IfcSchemaEntity(new IfcRelAssociatesMaterial(e));
    if ( e->is(Type::IfcRelAssociatesProfileProperties) ) return IfcSchemaEntity(new IfcRelAssociatesProfileProperties(e));
    if ( e->is(Type::IfcRelConnects) ) return IfcSchemaEntity(new IfcRelConnects(e));
    if ( e->is(Type::IfcRelConnectsElements) ) return IfcSchemaEntity(new IfcRelConnectsElements(e));
    if ( e->is(Type::IfcRelConnectsPathElements) ) return IfcSchemaEntity(new IfcRelConnectsPathElements(e));
    if ( e->is(Type::IfcRelConnectsPortToElement) ) return IfcSchemaEntity(new IfcRelConnectsPortToElement(e));
    if ( e->is(Type::IfcRelConnectsPorts) ) return IfcSchemaEntity(new IfcRelConnectsPorts(e));
    if ( e->is(Type::IfcRelConnectsStructuralActivity) ) return IfcSchemaEntity(new IfcRelConnectsStructuralActivity(e));
    if ( e->is(Type::IfcRelConnectsStructuralElement) ) return IfcSchemaEntity(new IfcRelConnectsStructuralElement(e));
    if ( e->is(Type::IfcRelConnectsStructuralMember) ) return IfcSchemaEntity(new IfcRelConnectsStructuralMember(e));
    if ( e->is(Type::IfcRelConnectsWithEccentricity) ) return IfcSchemaEntity(new IfcRelConnectsWithEccentricity(e));
    if ( e->is(Type::IfcRelConnectsWithRealizingElements) ) return IfcSchemaEntity(new IfcRelConnectsWithRealizingElements(e));
    if ( e->is(Type::IfcRelContainedInSpatialStructure) ) return IfcSchemaEntity(new IfcRelContainedInSpatialStructure(e));
    if ( e->is(Type::IfcRelCoversBldgElements) ) return IfcSchemaEntity(new IfcRelCoversBldgElements(e));
    if ( e->is(Type::IfcRelCoversSpaces) ) return IfcSchemaEntity(new IfcRelCoversSpaces(e));
    if ( e->is(Type::IfcRelDecomposes) ) return IfcSchemaEntity(new IfcRelDecomposes(e));
    if ( e->is(Type::IfcRelDefines) ) return IfcSchemaEntity(new IfcRelDefines(e));
    if ( e->is(Type::IfcRelDefinesByProperties) ) return IfcSchemaEntity(new IfcRelDefinesByProperties(e));
    if ( e->is(Type::IfcRelDefinesByType) ) return IfcSchemaEntity(new IfcRelDefinesByType(e));
    if ( e->is(Type::IfcRelFillsElement) ) return IfcSchemaEntity(new IfcRelFillsElement(e));
    if ( e->is(Type::IfcRelFlowControlElements) ) return IfcSchemaEntity(new IfcRelFlowControlElements(e));
    if ( e->is(Type::IfcRelInteractionRequirements) ) return IfcSchemaEntity(new IfcRelInteractionRequirements(e));
    if ( e->is(Type::IfcRelNests) ) return IfcSchemaEntity(new IfcRelNests(e));
    if ( e->is(Type::IfcRelOccupiesSpaces) ) return IfcSchemaEntity(new IfcRelOccupiesSpaces(e));
    if ( e->is(Type::IfcRelOverridesProperties) ) return IfcSchemaEntity(new IfcRelOverridesProperties(e));
    if ( e->is(Type::IfcRelProjectsElement) ) return IfcSchemaEntity(new IfcRelProjectsElement(e));
    if ( e->is(Type::IfcRelReferencedInSpatialStructure) ) return IfcSchemaEntity(new IfcRelReferencedInSpatialStructure(e));
    if ( e->is(Type::IfcRelSchedulesCostItems) ) return IfcSchemaEntity(new IfcRelSchedulesCostItems(e));
    if ( e->is(Type::IfcRelSequence) ) return IfcSchemaEntity(new IfcRelSequence(e));
    if ( e->is(Type::IfcRelServicesBuildings) ) return IfcSchemaEntity(new IfcRelServicesBuildings(e));
    if ( e->is(Type::IfcRelSpaceBoundary) ) return IfcSchemaEntity(new IfcRelSpaceBoundary(e));
    if ( e->is(Type::IfcRelVoidsElement) ) return IfcSchemaEntity(new IfcRelVoidsElement(e));
    if ( e->is(Type::IfcRelationship) ) return IfcSchemaEntity(new IfcRelationship(e));
    if ( e->is(Type::IfcRelaxation) ) return IfcSchemaEntity(new IfcRelaxation(e));
    if ( e->is(Type::IfcRepresentation) ) return IfcSchemaEntity(new IfcRepresentation(e));
    if ( e->is(Type::IfcRepresentationContext) ) return IfcSchemaEntity(new IfcRepresentationContext(e));
    if ( e->is(Type::IfcRepresentationItem) ) return IfcSchemaEntity(new IfcRepresentationItem(e));
    if ( e->is(Type::IfcRepresentationMap) ) return IfcSchemaEntity(new IfcRepresentationMap(e));
    if ( e->is(Type::IfcResource) ) return IfcSchemaEntity(new IfcResource(e));
    if ( e->is(Type::IfcRevolvedAreaSolid) ) return IfcSchemaEntity(new IfcRevolvedAreaSolid(e));
    if ( e->is(Type::IfcRibPlateProfileProperties) ) return IfcSchemaEntity(new IfcRibPlateProfileProperties(e));
    if ( e->is(Type::IfcRightCircularCone) ) return IfcSchemaEntity(new IfcRightCircularCone(e));
    if ( e->is(Type::IfcRightCircularCylinder) ) return IfcSchemaEntity(new IfcRightCircularCylinder(e));
    if ( e->is(Type::IfcRoof) ) return IfcSchemaEntity(new IfcRoof(e));
    if ( e->is(Type::IfcRoot) ) return IfcSchemaEntity(new IfcRoot(e));
    if ( e->is(Type::IfcRoundedEdgeFeature) ) return IfcSchemaEntity(new IfcRoundedEdgeFeature(e));
    if ( e->is(Type::IfcRoundedRectangleProfileDef) ) return IfcSchemaEntity(new IfcRoundedRectangleProfileDef(e));
    if ( e->is(Type::IfcSIUnit) ) return IfcSchemaEntity(new IfcSIUnit(e));
    if ( e->is(Type::IfcSanitaryTerminalType) ) return IfcSchemaEntity(new IfcSanitaryTerminalType(e));
    if ( e->is(Type::IfcScheduleTimeControl) ) return IfcSchemaEntity(new IfcScheduleTimeControl(e));
    if ( e->is(Type::IfcSectionProperties) ) return IfcSchemaEntity(new IfcSectionProperties(e));
    if ( e->is(Type::IfcSectionReinforcementProperties) ) return IfcSchemaEntity(new IfcSectionReinforcementProperties(e));
    if ( e->is(Type::IfcSectionedSpine) ) return IfcSchemaEntity(new IfcSectionedSpine(e));
    if ( e->is(Type::IfcSensorType) ) return IfcSchemaEntity(new IfcSensorType(e));
    if ( e->is(Type::IfcServiceLife) ) return IfcSchemaEntity(new IfcServiceLife(e));
    if ( e->is(Type::IfcServiceLifeFactor) ) return IfcSchemaEntity(new IfcServiceLifeFactor(e));
    if ( e->is(Type::IfcShapeAspect) ) return IfcSchemaEntity(new IfcShapeAspect(e));
    if ( e->is(Type::IfcShapeModel) ) return IfcSchemaEntity(new IfcShapeModel(e));
    if ( e->is(Type::IfcShapeRepresentation) ) return IfcSchemaEntity(new IfcShapeRepresentation(e));
    if ( e->is(Type::IfcShellBasedSurfaceModel) ) return IfcSchemaEntity(new IfcShellBasedSurfaceModel(e));
    if ( e->is(Type::IfcSimpleProperty) ) return IfcSchemaEntity(new IfcSimpleProperty(e));
    if ( e->is(Type::IfcSite) ) return IfcSchemaEntity(new IfcSite(e));
    if ( e->is(Type::IfcSlab) ) return IfcSchemaEntity(new IfcSlab(e));
    if ( e->is(Type::IfcSlabType) ) return IfcSchemaEntity(new IfcSlabType(e));
    if ( e->is(Type::IfcSlippageConnectionCondition) ) return IfcSchemaEntity(new IfcSlippageConnectionCondition(e));
    if ( e->is(Type::IfcSolidModel) ) return IfcSchemaEntity(new IfcSolidModel(e));
    if ( e->is(Type::IfcSoundProperties) ) return IfcSchemaEntity(new IfcSoundProperties(e));
    if ( e->is(Type::IfcSoundValue) ) return IfcSchemaEntity(new IfcSoundValue(e));
    if ( e->is(Type::IfcSpace) ) return IfcSchemaEntity(new IfcSpace(e));
    if ( e->is(Type::IfcSpaceHeaterType) ) return IfcSchemaEntity(new IfcSpaceHeaterType(e));
    if ( e->is(Type::IfcSpaceProgram) ) return IfcSchemaEntity(new IfcSpaceProgram(e));
    if ( e->is(Type::IfcSpaceThermalLoadProperties) ) return IfcSchemaEntity(new IfcSpaceThermalLoadProperties(e));
    if ( e->is(Type::IfcSpaceType) ) return IfcSchemaEntity(new IfcSpaceType(e));
    if ( e->is(Type::IfcSpatialStructureElement) ) return IfcSchemaEntity(new IfcSpatialStructureElement(e));
    if ( e->is(Type::IfcSpatialStructureElementType) ) return IfcSchemaEntity(new IfcSpatialStructureElementType(e));
    if ( e->is(Type::IfcSphere) ) return IfcSchemaEntity(new IfcSphere(e));
    if ( e->is(Type::IfcStackTerminalType) ) return IfcSchemaEntity(new IfcStackTerminalType(e));
    if ( e->is(Type::IfcStair) ) return IfcSchemaEntity(new IfcStair(e));
    if ( e->is(Type::IfcStairFlight) ) return IfcSchemaEntity(new IfcStairFlight(e));
    if ( e->is(Type::IfcStairFlightType) ) return IfcSchemaEntity(new IfcStairFlightType(e));
    if ( e->is(Type::IfcStructuralAction) ) return IfcSchemaEntity(new IfcStructuralAction(e));
    if ( e->is(Type::IfcStructuralActivity) ) return IfcSchemaEntity(new IfcStructuralActivity(e));
    if ( e->is(Type::IfcStructuralAnalysisModel) ) return IfcSchemaEntity(new IfcStructuralAnalysisModel(e));
    if ( e->is(Type::IfcStructuralConnection) ) return IfcSchemaEntity(new IfcStructuralConnection(e));
    if ( e->is(Type::IfcStructuralConnectionCondition) ) return IfcSchemaEntity(new IfcStructuralConnectionCondition(e));
    if ( e->is(Type::IfcStructuralCurveConnection) ) return IfcSchemaEntity(new IfcStructuralCurveConnection(e));
    if ( e->is(Type::IfcStructuralCurveMember) ) return IfcSchemaEntity(new IfcStructuralCurveMember(e));
    if ( e->is(Type::IfcStructuralCurveMemberVarying) ) return IfcSchemaEntity(new IfcStructuralCurveMemberVarying(e));
    if ( e->is(Type::IfcStructuralItem) ) return IfcSchemaEntity(new IfcStructuralItem(e));
    if ( e->is(Type::IfcStructuralLinearAction) ) return IfcSchemaEntity(new IfcStructuralLinearAction(e));
    if ( e->is(Type::IfcStructuralLinearActionVarying) ) return IfcSchemaEntity(new IfcStructuralLinearActionVarying(e));
    if ( e->is(Type::IfcStructuralLoad) ) return IfcSchemaEntity(new IfcStructuralLoad(e));
    if ( e->is(Type::IfcStructuralLoadGroup) ) return IfcSchemaEntity(new IfcStructuralLoadGroup(e));
    if ( e->is(Type::IfcStructuralLoadLinearForce) ) return IfcSchemaEntity(new IfcStructuralLoadLinearForce(e));
    if ( e->is(Type::IfcStructuralLoadPlanarForce) ) return IfcSchemaEntity(new IfcStructuralLoadPlanarForce(e));
    if ( e->is(Type::IfcStructuralLoadSingleDisplacement) ) return IfcSchemaEntity(new IfcStructuralLoadSingleDisplacement(e));
    if ( e->is(Type::IfcStructuralLoadSingleDisplacementDistortion) ) return IfcSchemaEntity(new IfcStructuralLoadSingleDisplacementDistortion(e));
    if ( e->is(Type::IfcStructuralLoadSingleForce) ) return IfcSchemaEntity(new IfcStructuralLoadSingleForce(e));
    if ( e->is(Type::IfcStructuralLoadSingleForceWarping) ) return IfcSchemaEntity(new IfcStructuralLoadSingleForceWarping(e));
    if ( e->is(Type::IfcStructuralLoadStatic) ) return IfcSchemaEntity(new IfcStructuralLoadStatic(e));
    if ( e->is(Type::IfcStructuralLoadTemperature) ) return IfcSchemaEntity(new IfcStructuralLoadTemperature(e));
    if ( e->is(Type::IfcStructuralMember) ) return IfcSchemaEntity(new IfcStructuralMember(e));
    if ( e->is(Type::IfcStructuralPlanarAction) ) return IfcSchemaEntity(new IfcStructuralPlanarAction(e));
    if ( e->is(Type::IfcStructuralPlanarActionVarying) ) return IfcSchemaEntity(new IfcStructuralPlanarActionVarying(e));
    if ( e->is(Type::IfcStructuralPointAction) ) return IfcSchemaEntity(new IfcStructuralPointAction(e));
    if ( e->is(Type::IfcStructuralPointConnection) ) return IfcSchemaEntity(new IfcStructuralPointConnection(e));
    if ( e->is(Type::IfcStructuralPointReaction) ) return IfcSchemaEntity(new IfcStructuralPointReaction(e));
    if ( e->is(Type::IfcStructuralProfileProperties) ) return IfcSchemaEntity(new IfcStructuralProfileProperties(e));
    if ( e->is(Type::IfcStructuralReaction) ) return IfcSchemaEntity(new IfcStructuralReaction(e));
    if ( e->is(Type::IfcStructuralResultGroup) ) return IfcSchemaEntity(new IfcStructuralResultGroup(e));
    if ( e->is(Type::IfcStructuralSteelProfileProperties) ) return IfcSchemaEntity(new IfcStructuralSteelProfileProperties(e));
    if ( e->is(Type::IfcStructuralSurfaceConnection) ) return IfcSchemaEntity(new IfcStructuralSurfaceConnection(e));
    if ( e->is(Type::IfcStructuralSurfaceMember) ) return IfcSchemaEntity(new IfcStructuralSurfaceMember(e));
    if ( e->is(Type::IfcStructuralSurfaceMemberVarying) ) return IfcSchemaEntity(new IfcStructuralSurfaceMemberVarying(e));
    if ( e->is(Type::IfcStructuredDimensionCallout) ) return IfcSchemaEntity(new IfcStructuredDimensionCallout(e));
    if ( e->is(Type::IfcStyleModel) ) return IfcSchemaEntity(new IfcStyleModel(e));
    if ( e->is(Type::IfcStyledItem) ) return IfcSchemaEntity(new IfcStyledItem(e));
    if ( e->is(Type::IfcStyledRepresentation) ) return IfcSchemaEntity(new IfcStyledRepresentation(e));
    if ( e->is(Type::IfcSubContractResource) ) return IfcSchemaEntity(new IfcSubContractResource(e));
    if ( e->is(Type::IfcSubedge) ) return IfcSchemaEntity(new IfcSubedge(e));
    if ( e->is(Type::IfcSurface) ) return IfcSchemaEntity(new IfcSurface(e));
    if ( e->is(Type::IfcSurfaceCurveSweptAreaSolid) ) return IfcSchemaEntity(new IfcSurfaceCurveSweptAreaSolid(e));
    if ( e->is(Type::IfcSurfaceOfLinearExtrusion) ) return IfcSchemaEntity(new IfcSurfaceOfLinearExtrusion(e));
    if ( e->is(Type::IfcSurfaceOfRevolution) ) return IfcSchemaEntity(new IfcSurfaceOfRevolution(e));
    if ( e->is(Type::IfcSurfaceStyle) ) return IfcSchemaEntity(new IfcSurfaceStyle(e));
    if ( e->is(Type::IfcSurfaceStyleLighting) ) return IfcSchemaEntity(new IfcSurfaceStyleLighting(e));
    if ( e->is(Type::IfcSurfaceStyleRefraction) ) return IfcSchemaEntity(new IfcSurfaceStyleRefraction(e));
    if ( e->is(Type::IfcSurfaceStyleRendering) ) return IfcSchemaEntity(new IfcSurfaceStyleRendering(e));
    if ( e->is(Type::IfcSurfaceStyleShading) ) return IfcSchemaEntity(new IfcSurfaceStyleShading(e));
    if ( e->is(Type::IfcSurfaceStyleWithTextures) ) return IfcSchemaEntity(new IfcSurfaceStyleWithTextures(e));
    if ( e->is(Type::IfcSurfaceTexture) ) return IfcSchemaEntity(new IfcSurfaceTexture(e));
    if ( e->is(Type::IfcSweptAreaSolid) ) return IfcSchemaEntity(new IfcSweptAreaSolid(e));
    if ( e->is(Type::IfcSweptDiskSolid) ) return IfcSchemaEntity(new IfcSweptDiskSolid(e));
    if ( e->is(Type::IfcSweptSurface) ) return IfcSchemaEntity(new IfcSweptSurface(e));
    if ( e->is(Type::IfcSwitchingDeviceType) ) return IfcSchemaEntity(new IfcSwitchingDeviceType(e));
    if ( e->is(Type::IfcSymbolStyle) ) return IfcSchemaEntity(new IfcSymbolStyle(e));
    if ( e->is(Type::IfcSystem) ) return IfcSchemaEntity(new IfcSystem(e));
    if ( e->is(Type::IfcSystemFurnitureElementType) ) return IfcSchemaEntity(new IfcSystemFurnitureElementType(e));
    if ( e->is(Type::IfcTShapeProfileDef) ) return IfcSchemaEntity(new IfcTShapeProfileDef(e));
    if ( e->is(Type::IfcTable) ) return IfcSchemaEntity(new IfcTable(e));
    if ( e->is(Type::IfcTableRow) ) return IfcSchemaEntity(new IfcTableRow(e));
    if ( e->is(Type::IfcTankType) ) return IfcSchemaEntity(new IfcTankType(e));
    if ( e->is(Type::IfcTask) ) return IfcSchemaEntity(new IfcTask(e));
    if ( e->is(Type::IfcTelecomAddress) ) return IfcSchemaEntity(new IfcTelecomAddress(e));
    if ( e->is(Type::IfcTendon) ) return IfcSchemaEntity(new IfcTendon(e));
    if ( e->is(Type::IfcTendonAnchor) ) return IfcSchemaEntity(new IfcTendonAnchor(e));
    if ( e->is(Type::IfcTerminatorSymbol) ) return IfcSchemaEntity(new IfcTerminatorSymbol(e));
    if ( e->is(Type::IfcTextLiteral) ) return IfcSchemaEntity(new IfcTextLiteral(e));
    if ( e->is(Type::IfcTextLiteralWithExtent) ) return IfcSchemaEntity(new IfcTextLiteralWithExtent(e));
    if ( e->is(Type::IfcTextStyle) ) return IfcSchemaEntity(new IfcTextStyle(e));
    if ( e->is(Type::IfcTextStyleFontModel) ) return IfcSchemaEntity(new IfcTextStyleFontModel(e));
    if ( e->is(Type::IfcTextStyleForDefinedFont) ) return IfcSchemaEntity(new IfcTextStyleForDefinedFont(e));
    if ( e->is(Type::IfcTextStyleTextModel) ) return IfcSchemaEntity(new IfcTextStyleTextModel(e));
    if ( e->is(Type::IfcTextStyleWithBoxCharacteristics) ) return IfcSchemaEntity(new IfcTextStyleWithBoxCharacteristics(e));
    if ( e->is(Type::IfcTextureCoordinate) ) return IfcSchemaEntity(new IfcTextureCoordinate(e));
    if ( e->is(Type::IfcTextureCoordinateGenerator) ) return IfcSchemaEntity(new IfcTextureCoordinateGenerator(e));
    if ( e->is(Type::IfcTextureMap) ) return IfcSchemaEntity(new IfcTextureMap(e));
    if ( e->is(Type::IfcTextureVertex) ) return IfcSchemaEntity(new IfcTextureVertex(e));
    if ( e->is(Type::IfcThermalMaterialProperties) ) return IfcSchemaEntity(new IfcThermalMaterialProperties(e));
    if ( e->is(Type::IfcTimeSeries) ) return IfcSchemaEntity(new IfcTimeSeries(e));
    if ( e->is(Type::IfcTimeSeriesReferenceRelationship) ) return IfcSchemaEntity(new IfcTimeSeriesReferenceRelationship(e));
    if ( e->is(Type::IfcTimeSeriesSchedule) ) return IfcSchemaEntity(new IfcTimeSeriesSchedule(e));
    if ( e->is(Type::IfcTimeSeriesValue) ) return IfcSchemaEntity(new IfcTimeSeriesValue(e));
    if ( e->is(Type::IfcTopologicalRepresentationItem) ) return IfcSchemaEntity(new IfcTopologicalRepresentationItem(e));
    if ( e->is(Type::IfcTopologyRepresentation) ) return IfcSchemaEntity(new IfcTopologyRepresentation(e));
    if ( e->is(Type::IfcTransformerType) ) return IfcSchemaEntity(new IfcTransformerType(e));
    if ( e->is(Type::IfcTransportElement) ) return IfcSchemaEntity(new IfcTransportElement(e));
    if ( e->is(Type::IfcTransportElementType) ) return IfcSchemaEntity(new IfcTransportElementType(e));
    if ( e->is(Type::IfcTrapeziumProfileDef) ) return IfcSchemaEntity(new IfcTrapeziumProfileDef(e));
    if ( e->is(Type::IfcTrimmedCurve) ) return IfcSchemaEntity(new IfcTrimmedCurve(e));
    if ( e->is(Type::IfcTubeBundleType) ) return IfcSchemaEntity(new IfcTubeBundleType(e));
    if ( e->is(Type::IfcTwoDirectionRepeatFactor) ) return IfcSchemaEntity(new IfcTwoDirectionRepeatFactor(e));
    if ( e->is(Type::IfcTypeObject) ) return IfcSchemaEntity(new IfcTypeObject(e));
    if ( e->is(Type::IfcTypeProduct) ) return IfcSchemaEntity(new IfcTypeProduct(e));
    if ( e->is(Type::IfcUShapeProfileDef) ) return IfcSchemaEntity(new IfcUShapeProfileDef(e));
    if ( e->is(Type::IfcUnitAssignment) ) return IfcSchemaEntity(new IfcUnitAssignment(e));
    if ( e->is(Type::IfcUnitaryEquipmentType) ) return IfcSchemaEntity(new IfcUnitaryEquipmentType(e));
    if ( e->is(Type::IfcValveType) ) return IfcSchemaEntity(new IfcValveType(e));
    if ( e->is(Type::IfcVector) ) return IfcSchemaEntity(new IfcVector(e));
    if ( e->is(Type::IfcVertex) ) return IfcSchemaEntity(new IfcVertex(e));
    if ( e->is(Type::IfcVertexBasedTextureMap) ) return IfcSchemaEntity(new IfcVertexBasedTextureMap(e));
    if ( e->is(Type::IfcVertexLoop) ) return IfcSchemaEntity(new IfcVertexLoop(e));
    if ( e->is(Type::IfcVertexPoint) ) return IfcSchemaEntity(new IfcVertexPoint(e));
    if ( e->is(Type::IfcVibrationIsolatorType) ) return IfcSchemaEntity(new IfcVibrationIsolatorType(e));
    if ( e->is(Type::IfcVirtualElement) ) return IfcSchemaEntity(new IfcVirtualElement(e));
    if ( e->is(Type::IfcVirtualGridIntersection) ) return IfcSchemaEntity(new IfcVirtualGridIntersection(e));
    if ( e->is(Type::IfcWall) ) return IfcSchemaEntity(new IfcWall(e));
    if ( e->is(Type::IfcWallStandardCase) ) return IfcSchemaEntity(new IfcWallStandardCase(e));
    if ( e->is(Type::IfcWallType) ) return IfcSchemaEntity(new IfcWallType(e));
    if ( e->is(Type::IfcWasteTerminalType) ) return IfcSchemaEntity(new IfcWasteTerminalType(e));
    if ( e->is(Type::IfcWaterProperties) ) return IfcSchemaEntity(new IfcWaterProperties(e));
    if ( e->is(Type::IfcWindow) ) return IfcSchemaEntity(new IfcWindow(e));
    if ( e->is(Type::IfcWindowLiningProperties) ) return IfcSchemaEntity(new IfcWindowLiningProperties(e));
    if ( e->is(Type::IfcWindowPanelProperties) ) return IfcSchemaEntity(new IfcWindowPanelProperties(e));
    if ( e->is(Type::IfcWindowStyle) ) return IfcSchemaEntity(new IfcWindowStyle(e));
    if ( e->is(Type::IfcWorkControl) ) return IfcSchemaEntity(new IfcWorkControl(e));
    if ( e->is(Type::IfcWorkPlan) ) return IfcSchemaEntity(new IfcWorkPlan(e));
    if ( e->is(Type::IfcWorkSchedule) ) return IfcSchemaEntity(new IfcWorkSchedule(e));
    if ( e->is(Type::IfcZShapeProfileDef) ) return IfcSchemaEntity(new IfcZShapeProfileDef(e));
    if ( e->is(Type::IfcZone) ) return IfcSchemaEntity(new IfcZone(e));
    throw; 
}

std::string Type::ToString(Enum v) {
    if (v < 0 || v >= 758) throw;
    const char* names[] = { "IfcAbsorbedDoseMeasure","IfcAccelerationMeasure","IfcAmountOfSubstanceMeasure","IfcAngularVelocityMeasure","IfcAreaMeasure","IfcBoolean","IfcColour","IfcComplexNumber","IfcCompoundPlaneAngleMeasure","IfcContextDependentMeasure","IfcCountMeasure","IfcCurvatureMeasure","IfcDateTimeSelect","IfcDerivedMeasureValue","IfcDescriptiveMeasure","IfcDoseEquivalentMeasure","IfcDynamicViscosityMeasure","IfcElectricCapacitanceMeasure","IfcElectricChargeMeasure","IfcElectricConductanceMeasure","IfcElectricCurrentMeasure","IfcElectricResistanceMeasure","IfcElectricVoltageMeasure","IfcEnergyMeasure","IfcForceMeasure","IfcFrequencyMeasure","IfcHeatFluxDensityMeasure","IfcHeatingValueMeasure","IfcIdentifier","IfcIlluminanceMeasure","IfcInductanceMeasure","IfcInteger","IfcIntegerCountRateMeasure","IfcIonConcentrationMeasure","IfcIsothermalMoistureCapacityMeasure","IfcKinematicViscosityMeasure","IfcLabel","IfcLengthMeasure","IfcLinearForceMeasure","IfcLinearMomentMeasure","IfcLinearStiffnessMeasure","IfcLinearVelocityMeasure","IfcLogical","IfcLuminousFluxMeasure","IfcLuminousIntensityDistributionMeasure","IfcLuminousIntensityMeasure","IfcMagneticFluxDensityMeasure","IfcMagneticFluxMeasure","IfcMassDensityMeasure","IfcMassFlowRateMeasure","IfcMassMeasure","IfcMassPerLengthMeasure","IfcMeasureValue","IfcModulusOfElasticityMeasure","IfcModulusOfLinearSubgradeReactionMeasure","IfcModulusOfRotationalSubgradeReactionMeasure","IfcModulusOfSubgradeReactionMeasure","IfcMoistureDiffusivityMeasure","IfcMolecularWeightMeasure","IfcMomentOfInertiaMeasure","IfcMonetaryMeasure","IfcNormalisedRatioMeasure","IfcNullStyle","IfcNumericMeasure","IfcPHMeasure","IfcParameterValue","IfcPlanarForceMeasure","IfcPlaneAngleMeasure","IfcPositiveLengthMeasure","IfcPositivePlaneAngleMeasure","IfcPositiveRatioMeasure","IfcPowerMeasure","IfcPressureMeasure","IfcRadioActivityMeasure","IfcRatioMeasure","IfcReal","IfcRotationalFrequencyMeasure","IfcRotationalMassMeasure","IfcRotationalStiffnessMeasure","IfcSectionModulusMeasure","IfcSectionalAreaIntegralMeasure","IfcShearModulusMeasure","IfcSimpleValue","IfcSolidAngleMeasure","IfcSoundPowerMeasure","IfcSoundPressureMeasure","IfcSpecificHeatCapacityMeasure","IfcSpecularExponent","IfcSpecularRoughness","IfcTemperatureGradientMeasure","IfcText","IfcThermalAdmittanceMeasure","IfcThermalConductivityMeasure","IfcThermalExpansionCoefficientMeasure","IfcThermalResistanceMeasure","IfcThermalTransmittanceMeasure","IfcThermodynamicTemperatureMeasure","IfcTimeMeasure","IfcTimeStamp","IfcTorqueMeasure","IfcVaporPermeabilityMeasure","IfcVolumeMeasure","IfcVolumetricFlowRateMeasure","IfcWarpingConstantMeasure","IfcWarpingMomentMeasure","Ifc2DCompositeCurve","IfcActionRequest","IfcActor","IfcActorRole","IfcActuatorType","IfcAddress","IfcAirTerminalBoxType","IfcAirTerminalType","IfcAirToAirHeatRecoveryType","IfcAlarmType","IfcAngularDimension","IfcAnnotation","IfcAnnotationCurveOccurrence","IfcAnnotationFillArea","IfcAnnotationFillAreaOccurrence","IfcAnnotationOccurrence","IfcAnnotationSurface","IfcAnnotationSurfaceOccurrence","IfcAnnotationSymbolOccurrence","IfcAnnotationTextOccurrence","IfcApplication","IfcAppliedValue","IfcAppliedValueRelationship","IfcApproval","IfcApprovalActorRelationship","IfcApprovalPropertyRelationship","IfcApprovalRelationship","IfcArbitraryClosedProfileDef","IfcArbitraryOpenProfileDef","IfcArbitraryProfileDefWithVoids","IfcAsset","IfcAsymmetricIShapeProfileDef","IfcAxis1Placement","IfcAxis2Placement2D","IfcAxis2Placement3D","IfcBSplineCurve","IfcBeam","IfcBeamType","IfcBezierCurve","IfcBlobTexture","IfcBlock","IfcBoilerType","IfcBooleanClippingResult","IfcBooleanResult","IfcBoundaryCondition","IfcBoundaryEdgeCondition","IfcBoundaryFaceCondition","IfcBoundaryNodeCondition","IfcBoundaryNodeConditionWarping","IfcBoundedCurve","IfcBoundedSurface","IfcBoundingBox","IfcBoxedHalfSpace","IfcBuilding","IfcBuildingElement","IfcBuildingElementComponent","IfcBuildingElementPart","IfcBuildingElementProxy","IfcBuildingElementProxyType","IfcBuildingElementType","IfcBuildingStorey","IfcCShapeProfileDef","IfcCableCarrierFittingType","IfcCableCarrierSegmentType","IfcCableSegmentType","IfcCalendarDate","IfcCartesianPoint","IfcCartesianTransformationOperator","IfcCartesianTransformationOperator2D","IfcCartesianTransformationOperator2DnonUniform","IfcCartesianTransformationOperator3D","IfcCartesianTransformationOperator3DnonUniform","IfcCenterLineProfileDef","IfcChamferEdgeFeature","IfcChillerType","IfcCircle","IfcCircleHollowProfileDef","IfcCircleProfileDef","IfcClassification","IfcClassificationItem","IfcClassificationItemRelationship","IfcClassificationNotation","IfcClassificationNotationFacet","IfcClassificationReference","IfcClosedShell","IfcCoilType","IfcColourRgb","IfcColourSpecification","IfcColumn","IfcColumnType","IfcComplexProperty","IfcCompositeCurve","IfcCompositeCurveSegment","IfcCompositeProfileDef","IfcCompressorType","IfcCondenserType","IfcCondition","IfcConditionCriterion","IfcConic","IfcConnectedFaceSet","IfcConnectionCurveGeometry","IfcConnectionGeometry","IfcConnectionPointEccentricity","IfcConnectionPointGeometry","IfcConnectionPortGeometry","IfcConnectionSurfaceGeometry","IfcConstraint","IfcConstraintAggregationRelationship","IfcConstraintClassificationRelationship","IfcConstraintRelationship","IfcConstructionEquipmentResource","IfcConstructionMaterialResource","IfcConstructionProductResource","IfcConstructionResource","IfcContextDependentUnit","IfcControl","IfcControllerType","IfcConversionBasedUnit","IfcCooledBeamType","IfcCoolingTowerType","IfcCoordinatedUniversalTimeOffset","IfcCostItem","IfcCostSchedule","IfcCostValue","IfcCovering","IfcCoveringType","IfcCraneRailAShapeProfileDef","IfcCraneRailFShapeProfileDef","IfcCrewResource","IfcCsgPrimitive3D","IfcCsgSolid","IfcCurrencyRelationship","IfcCurtainWall","IfcCurtainWallType","IfcCurve","IfcCurveBoundedPlane","IfcCurveStyle","IfcCurveStyleFont","IfcCurveStyleFontAndScaling","IfcCurveStyleFontPattern","IfcDamperType","IfcDateAndTime","IfcDefinedSymbol","IfcDerivedProfileDef","IfcDerivedUnit","IfcDerivedUnitElement","IfcDiameterDimension","IfcDimensionCalloutRelationship","IfcDimensionCurve","IfcDimensionCurveDirectedCallout","IfcDimensionCurveTerminator","IfcDimensionPair","IfcDimensionalExponents","IfcDirection","IfcDiscreteAccessory","IfcDiscreteAccessoryType","IfcDistributionChamberElement","IfcDistributionChamberElementType","IfcDistributionControlElement","IfcDistributionControlElementType","IfcDistributionElement","IfcDistributionElementType","IfcDistributionFlowElement","IfcDistributionFlowElementType","IfcDistributionPort","IfcDocumentElectronicFormat","IfcDocumentInformation","IfcDocumentInformationRelationship","IfcDocumentReference","IfcDoor","IfcDoorLiningProperties","IfcDoorPanelProperties","IfcDoorStyle","IfcDraughtingCallout","IfcDraughtingCalloutRelationship","IfcDraughtingPreDefinedColour","IfcDraughtingPreDefinedCurveFont","IfcDraughtingPreDefinedTextFont","IfcDuctFittingType","IfcDuctSegmentType","IfcDuctSilencerType","IfcEdge","IfcEdgeCurve","IfcEdgeFeature","IfcEdgeLoop","IfcElectricApplianceType","IfcElectricDistributionPoint","IfcElectricFlowStorageDeviceType","IfcElectricGeneratorType","IfcElectricHeaterType","IfcElectricMotorType","IfcElectricTimeControlType","IfcElectricalBaseProperties","IfcElectricalCircuit","IfcElectricalElement","IfcElement","IfcElementAssembly","IfcElementComponent","IfcElementComponentType","IfcElementQuantity","IfcElementType","IfcElementarySurface","IfcEllipse","IfcEllipseProfileDef","IfcEnergyConversionDevice","IfcEnergyConversionDeviceType","IfcEnergyProperties","IfcEnvironmentalImpactValue","IfcEquipmentElement","IfcEquipmentStandard","IfcEvaporativeCoolerType","IfcEvaporatorType","IfcExtendedMaterialProperties","IfcExternalReference","IfcExternallyDefinedHatchStyle","IfcExternallyDefinedSurfaceStyle","IfcExternallyDefinedSymbol","IfcExternallyDefinedTextFont","IfcExtrudedAreaSolid","IfcFace","IfcFaceBasedSurfaceModel","IfcFaceBound","IfcFaceOuterBound","IfcFaceSurface","IfcFacetedBrep","IfcFacetedBrepWithVoids","IfcFailureConnectionCondition","IfcFanType","IfcFastener","IfcFastenerType","IfcFeatureElement","IfcFeatureElementAddition","IfcFeatureElementSubtraction","IfcFillAreaStyle","IfcFillAreaStyleHatching","IfcFillAreaStyleTileSymbolWithStyle","IfcFillAreaStyleTiles","IfcFilterType","IfcFireSuppressionTerminalType","IfcFlowController","IfcFlowControllerType","IfcFlowFitting","IfcFlowFittingType","IfcFlowInstrumentType","IfcFlowMeterType","IfcFlowMovingDevice","IfcFlowMovingDeviceType","IfcFlowSegment","IfcFlowSegmentType","IfcFlowStorageDevice","IfcFlowStorageDeviceType","IfcFlowTerminal","IfcFlowTerminalType","IfcFlowTreatmentDevice","IfcFlowTreatmentDeviceType","IfcFluidFlowProperties","IfcFooting","IfcFuelProperties","IfcFurnishingElement","IfcFurnishingElementType","IfcFurnitureStandard","IfcFurnitureType","IfcGasTerminalType","IfcGeneralMaterialProperties","IfcGeneralProfileProperties","IfcGeometricCurveSet","IfcGeometricRepresentationContext","IfcGeometricRepresentationItem","IfcGeometricRepresentationSubContext","IfcGeometricSet","IfcGrid","IfcGridAxis","IfcGridPlacement","IfcGroup","IfcHalfSpaceSolid","IfcHeatExchangerType","IfcHumidifierType","IfcHygroscopicMaterialProperties","IfcIShapeProfileDef","IfcImageTexture","IfcInventory","IfcIrregularTimeSeries","IfcIrregularTimeSeriesValue","IfcJunctionBoxType","IfcLShapeProfileDef","IfcLaborResource","IfcLampType","IfcLibraryInformation","IfcLibraryReference","IfcLightDistributionData","IfcLightFixtureType","IfcLightIntensityDistribution","IfcLightSource","IfcLightSourceAmbient","IfcLightSourceDirectional","IfcLightSourceGoniometric","IfcLightSourcePositional","IfcLightSourceSpot","IfcLine","IfcLinearDimension","IfcLocalPlacement","IfcLocalTime","IfcLoop","IfcManifoldSolidBrep","IfcMappedItem","IfcMaterial","IfcMaterialClassificationRelationship","IfcMaterialDefinitionRepresentation","IfcMaterialLayer","IfcMaterialLayerSet","IfcMaterialLayerSetUsage","IfcMaterialList","IfcMaterialProperties","IfcMeasureWithUnit","IfcMechanicalConcreteMaterialProperties","IfcMechanicalFastener","IfcMechanicalFastenerType","IfcMechanicalMaterialProperties","IfcMechanicalSteelMaterialProperties","IfcMember","IfcMemberType","IfcMetric","IfcMonetaryUnit","IfcMotorConnectionType","IfcMove","IfcNamedUnit","IfcObject","IfcObjectDefinition","IfcObjectPlacement","IfcObjective","IfcOccupant","IfcOffsetCurve2D","IfcOffsetCurve3D","IfcOneDirectionRepeatFactor","IfcOpenShell","IfcOpeningElement","IfcOpticalMaterialProperties","IfcOrderAction","IfcOrganization","IfcOrganizationRelationship","IfcOrientedEdge","IfcOutletType","IfcOwnerHistory","IfcParameterizedProfileDef","IfcPath","IfcPerformanceHistory","IfcPermeableCoveringProperties","IfcPermit","IfcPerson","IfcPersonAndOrganization","IfcPhysicalComplexQuantity","IfcPhysicalQuantity","IfcPhysicalSimpleQuantity","IfcPile","IfcPipeFittingType","IfcPipeSegmentType","IfcPixelTexture","IfcPlacement","IfcPlanarBox","IfcPlanarExtent","IfcPlane","IfcPlate","IfcPlateType","IfcPoint","IfcPointOnCurve","IfcPointOnSurface","IfcPolyLoop","IfcPolygonalBoundedHalfSpace","IfcPolyline","IfcPort","IfcPostalAddress","IfcPreDefinedColour","IfcPreDefinedCurveFont","IfcPreDefinedDimensionSymbol","IfcPreDefinedItem","IfcPreDefinedPointMarkerSymbol","IfcPreDefinedSymbol","IfcPreDefinedTerminatorSymbol","IfcPreDefinedTextFont","IfcPresentationLayerAssignment","IfcPresentationLayerWithStyle","IfcPresentationStyle","IfcPresentationStyleAssignment","IfcProcedure","IfcProcess","IfcProduct","IfcProductDefinitionShape","IfcProductRepresentation","IfcProductsOfCombustionProperties","IfcProfileDef","IfcProfileProperties","IfcProject","IfcProjectOrder","IfcProjectOrderRecord","IfcProjectionCurve","IfcProjectionElement","IfcProperty","IfcPropertyBoundedValue","IfcPropertyConstraintRelationship","IfcPropertyDefinition","IfcPropertyDependencyRelationship","IfcPropertyEnumeratedValue","IfcPropertyEnumeration","IfcPropertyListValue","IfcPropertyReferenceValue","IfcPropertySet","IfcPropertySetDefinition","IfcPropertySingleValue","IfcPropertyTableValue","IfcProtectiveDeviceType","IfcProxy","IfcPumpType","IfcQuantityArea","IfcQuantityCount","IfcQuantityLength","IfcQuantityTime","IfcQuantityVolume","IfcQuantityWeight","IfcRadiusDimension","IfcRailing","IfcRailingType","IfcRamp","IfcRampFlight","IfcRampFlightType","IfcRationalBezierCurve","IfcRectangleHollowProfileDef","IfcRectangleProfileDef","IfcRectangularPyramid","IfcRectangularTrimmedSurface","IfcReferencesValueDocument","IfcRegularTimeSeries","IfcReinforcementBarProperties","IfcReinforcementDefinitionProperties","IfcReinforcingBar","IfcReinforcingElement","IfcReinforcingMesh","IfcRelAggregates","IfcRelAssigns","IfcRelAssignsTasks","IfcRelAssignsToActor","IfcRelAssignsToControl","IfcRelAssignsToGroup","IfcRelAssignsToProcess","IfcRelAssignsToProduct","IfcRelAssignsToProjectOrder","IfcRelAssignsToResource","IfcRelAssociates","IfcRelAssociatesAppliedValue","IfcRelAssociatesApproval","IfcRelAssociatesClassification","IfcRelAssociatesConstraint","IfcRelAssociatesDocument","IfcRelAssociatesLibrary","IfcRelAssociatesMaterial","IfcRelAssociatesProfileProperties","IfcRelConnects","IfcRelConnectsElements","IfcRelConnectsPathElements","IfcRelConnectsPortToElement","IfcRelConnectsPorts","IfcRelConnectsStructuralActivity","IfcRelConnectsStructuralElement","IfcRelConnectsStructuralMember","IfcRelConnectsWithEccentricity","IfcRelConnectsWithRealizingElements","IfcRelContainedInSpatialStructure","IfcRelCoversBldgElements","IfcRelCoversSpaces","IfcRelDecomposes","IfcRelDefines","IfcRelDefinesByProperties","IfcRelDefinesByType","IfcRelFillsElement","IfcRelFlowControlElements","IfcRelInteractionRequirements","IfcRelNests","IfcRelOccupiesSpaces","IfcRelOverridesProperties","IfcRelProjectsElement","IfcRelReferencedInSpatialStructure","IfcRelSchedulesCostItems","IfcRelSequence","IfcRelServicesBuildings","IfcRelSpaceBoundary","IfcRelVoidsElement","IfcRelationship","IfcRelaxation","IfcRepresentation","IfcRepresentationContext","IfcRepresentationItem","IfcRepresentationMap","IfcResource","IfcRevolvedAreaSolid","IfcRibPlateProfileProperties","IfcRightCircularCone","IfcRightCircularCylinder","IfcRoof","IfcRoot","IfcRoundedEdgeFeature","IfcRoundedRectangleProfileDef","IfcSIUnit","IfcSanitaryTerminalType","IfcScheduleTimeControl","IfcSectionProperties","IfcSectionReinforcementProperties","IfcSectionedSpine","IfcSensorType","IfcServiceLife","IfcServiceLifeFactor","IfcShapeAspect","IfcShapeModel","IfcShapeRepresentation","IfcShellBasedSurfaceModel","IfcSimpleProperty","IfcSite","IfcSlab","IfcSlabType","IfcSlippageConnectionCondition","IfcSolidModel","IfcSoundProperties","IfcSoundValue","IfcSpace","IfcSpaceHeaterType","IfcSpaceProgram","IfcSpaceThermalLoadProperties","IfcSpaceType","IfcSpatialStructureElement","IfcSpatialStructureElementType","IfcSphere","IfcStackTerminalType","IfcStair","IfcStairFlight","IfcStairFlightType","IfcStructuralAction","IfcStructuralActivity","IfcStructuralAnalysisModel","IfcStructuralConnection","IfcStructuralConnectionCondition","IfcStructuralCurveConnection","IfcStructuralCurveMember","IfcStructuralCurveMemberVarying","IfcStructuralItem","IfcStructuralLinearAction","IfcStructuralLinearActionVarying","IfcStructuralLoad","IfcStructuralLoadGroup","IfcStructuralLoadLinearForce","IfcStructuralLoadPlanarForce","IfcStructuralLoadSingleDisplacement","IfcStructuralLoadSingleDisplacementDistortion","IfcStructuralLoadSingleForce","IfcStructuralLoadSingleForceWarping","IfcStructuralLoadStatic","IfcStructuralLoadTemperature","IfcStructuralMember","IfcStructuralPlanarAction","IfcStructuralPlanarActionVarying","IfcStructuralPointAction","IfcStructuralPointConnection","IfcStructuralPointReaction","IfcStructuralProfileProperties","IfcStructuralReaction","IfcStructuralResultGroup","IfcStructuralSteelProfileProperties","IfcStructuralSurfaceConnection","IfcStructuralSurfaceMember","IfcStructuralSurfaceMemberVarying","IfcStructuredDimensionCallout","IfcStyleModel","IfcStyledItem","IfcStyledRepresentation","IfcSubContractResource","IfcSubedge","IfcSurface","IfcSurfaceCurveSweptAreaSolid","IfcSurfaceOfLinearExtrusion","IfcSurfaceOfRevolution","IfcSurfaceStyle","IfcSurfaceStyleLighting","IfcSurfaceStyleRefraction","IfcSurfaceStyleRendering","IfcSurfaceStyleShading","IfcSurfaceStyleWithTextures","IfcSurfaceTexture","IfcSweptAreaSolid","IfcSweptDiskSolid","IfcSweptSurface","IfcSwitchingDeviceType","IfcSymbolStyle","IfcSystem","IfcSystemFurnitureElementType","IfcTShapeProfileDef","IfcTable","IfcTableRow","IfcTankType","IfcTask","IfcTelecomAddress","IfcTendon","IfcTendonAnchor","IfcTerminatorSymbol","IfcTextLiteral","IfcTextLiteralWithExtent","IfcTextStyle","IfcTextStyleFontModel","IfcTextStyleForDefinedFont","IfcTextStyleTextModel","IfcTextStyleWithBoxCharacteristics","IfcTextureCoordinate","IfcTextureCoordinateGenerator","IfcTextureMap","IfcTextureVertex","IfcThermalMaterialProperties","IfcTimeSeries","IfcTimeSeriesReferenceRelationship","IfcTimeSeriesSchedule","IfcTimeSeriesValue","IfcTopologicalRepresentationItem","IfcTopologyRepresentation","IfcTransformerType","IfcTransportElement","IfcTransportElementType","IfcTrapeziumProfileDef","IfcTrimmedCurve","IfcTubeBundleType","IfcTwoDirectionRepeatFactor","IfcTypeObject","IfcTypeProduct","IfcUShapeProfileDef","IfcUnitAssignment","IfcUnitaryEquipmentType","IfcValveType","IfcVector","IfcVertex","IfcVertexBasedTextureMap","IfcVertexLoop","IfcVertexPoint","IfcVibrationIsolatorType","IfcVirtualElement","IfcVirtualGridIntersection","IfcWall","IfcWallStandardCase","IfcWallType","IfcWasteTerminalType","IfcWaterProperties","IfcWindow","IfcWindowLiningProperties","IfcWindowPanelProperties","IfcWindowStyle","IfcWorkControl","IfcWorkPlan","IfcWorkSchedule","IfcZShapeProfileDef","IfcZone" };
    return names[v];
}

Type::Enum Type::FromString(const std::string& s){
    if(s=="IFCABSORBEDDOSEMEASURE"                        ) { return IfcAbsorbedDoseMeasure; }
    if(s=="IFCACCELERATIONMEASURE"                        ) { return IfcAccelerationMeasure; }
    if(s=="IFCAMOUNTOFSUBSTANCEMEASURE"                   ) { return IfcAmountOfSubstanceMeasure; }
    if(s=="IFCANGULARVELOCITYMEASURE"                     ) { return IfcAngularVelocityMeasure; }
    if(s=="IFCAREAMEASURE"                                ) { return IfcAreaMeasure; }
    if(s=="IFCBOOLEAN"                                    ) { return IfcBoolean; }
    if(s=="IFCCOLOUR"                                     ) { return IfcColour; }
    if(s=="IFCCOMPLEXNUMBER"                              ) { return IfcComplexNumber; }
    if(s=="IFCCOMPOUNDPLANEANGLEMEASURE"                  ) { return IfcCompoundPlaneAngleMeasure; }
    if(s=="IFCCONTEXTDEPENDENTMEASURE"                    ) { return IfcContextDependentMeasure; }
    if(s=="IFCCOUNTMEASURE"                               ) { return IfcCountMeasure; }
    if(s=="IFCCURVATUREMEASURE"                           ) { return IfcCurvatureMeasure; }
    if(s=="IFCDATETIMESELECT"                             ) { return IfcDateTimeSelect; }
    if(s=="IFCDERIVEDMEASUREVALUE"                        ) { return IfcDerivedMeasureValue; }
    if(s=="IFCDESCRIPTIVEMEASURE"                         ) { return IfcDescriptiveMeasure; }
    if(s=="IFCDOSEEQUIVALENTMEASURE"                      ) { return IfcDoseEquivalentMeasure; }
    if(s=="IFCDYNAMICVISCOSITYMEASURE"                    ) { return IfcDynamicViscosityMeasure; }
    if(s=="IFCELECTRICCAPACITANCEMEASURE"                 ) { return IfcElectricCapacitanceMeasure; }
    if(s=="IFCELECTRICCHARGEMEASURE"                      ) { return IfcElectricChargeMeasure; }
    if(s=="IFCELECTRICCONDUCTANCEMEASURE"                 ) { return IfcElectricConductanceMeasure; }
    if(s=="IFCELECTRICCURRENTMEASURE"                     ) { return IfcElectricCurrentMeasure; }
    if(s=="IFCELECTRICRESISTANCEMEASURE"                  ) { return IfcElectricResistanceMeasure; }
    if(s=="IFCELECTRICVOLTAGEMEASURE"                     ) { return IfcElectricVoltageMeasure; }
    if(s=="IFCENERGYMEASURE"                              ) { return IfcEnergyMeasure; }
    if(s=="IFCFORCEMEASURE"                               ) { return IfcForceMeasure; }
    if(s=="IFCFREQUENCYMEASURE"                           ) { return IfcFrequencyMeasure; }
    if(s=="IFCHEATFLUXDENSITYMEASURE"                     ) { return IfcHeatFluxDensityMeasure; }
    if(s=="IFCHEATINGVALUEMEASURE"                        ) { return IfcHeatingValueMeasure; }
    if(s=="IFCIDENTIFIER"                                 ) { return IfcIdentifier; }
    if(s=="IFCILLUMINANCEMEASURE"                         ) { return IfcIlluminanceMeasure; }
    if(s=="IFCINDUCTANCEMEASURE"                          ) { return IfcInductanceMeasure; }
    if(s=="IFCINTEGER"                                    ) { return IfcInteger; }
    if(s=="IFCINTEGERCOUNTRATEMEASURE"                    ) { return IfcIntegerCountRateMeasure; }
    if(s=="IFCIONCONCENTRATIONMEASURE"                    ) { return IfcIonConcentrationMeasure; }
    if(s=="IFCISOTHERMALMOISTURECAPACITYMEASURE"          ) { return IfcIsothermalMoistureCapacityMeasure; }
    if(s=="IFCKINEMATICVISCOSITYMEASURE"                  ) { return IfcKinematicViscosityMeasure; }
    if(s=="IFCLABEL"                                      ) { return IfcLabel; }
    if(s=="IFCLENGTHMEASURE"                              ) { return IfcLengthMeasure; }
    if(s=="IFCLINEARFORCEMEASURE"                         ) { return IfcLinearForceMeasure; }
    if(s=="IFCLINEARMOMENTMEASURE"                        ) { return IfcLinearMomentMeasure; }
    if(s=="IFCLINEARSTIFFNESSMEASURE"                     ) { return IfcLinearStiffnessMeasure; }
    if(s=="IFCLINEARVELOCITYMEASURE"                      ) { return IfcLinearVelocityMeasure; }
    if(s=="IFCLOGICAL"                                    ) { return IfcLogical; }
    if(s=="IFCLUMINOUSFLUXMEASURE"                        ) { return IfcLuminousFluxMeasure; }
    if(s=="IFCLUMINOUSINTENSITYDISTRIBUTIONMEASURE"       ) { return IfcLuminousIntensityDistributionMeasure; }
    if(s=="IFCLUMINOUSINTENSITYMEASURE"                   ) { return IfcLuminousIntensityMeasure; }
    if(s=="IFCMAGNETICFLUXDENSITYMEASURE"                 ) { return IfcMagneticFluxDensityMeasure; }
    if(s=="IFCMAGNETICFLUXMEASURE"                        ) { return IfcMagneticFluxMeasure; }
    if(s=="IFCMASSDENSITYMEASURE"                         ) { return IfcMassDensityMeasure; }
    if(s=="IFCMASSFLOWRATEMEASURE"                        ) { return IfcMassFlowRateMeasure; }
    if(s=="IFCMASSMEASURE"                                ) { return IfcMassMeasure; }
    if(s=="IFCMASSPERLENGTHMEASURE"                       ) { return IfcMassPerLengthMeasure; }
    if(s=="IFCMEASUREVALUE"                               ) { return IfcMeasureValue; }
    if(s=="IFCMODULUSOFELASTICITYMEASURE"                 ) { return IfcModulusOfElasticityMeasure; }
    if(s=="IFCMODULUSOFLINEARSUBGRADEREACTIONMEASURE"     ) { return IfcModulusOfLinearSubgradeReactionMeasure; }
    if(s=="IFCMODULUSOFROTATIONALSUBGRADEREACTIONMEASURE" ) { return IfcModulusOfRotationalSubgradeReactionMeasure; }
    if(s=="IFCMODULUSOFSUBGRADEREACTIONMEASURE"           ) { return IfcModulusOfSubgradeReactionMeasure; }
    if(s=="IFCMOISTUREDIFFUSIVITYMEASURE"                 ) { return IfcMoistureDiffusivityMeasure; }
    if(s=="IFCMOLECULARWEIGHTMEASURE"                     ) { return IfcMolecularWeightMeasure; }
    if(s=="IFCMOMENTOFINERTIAMEASURE"                     ) { return IfcMomentOfInertiaMeasure; }
    if(s=="IFCMONETARYMEASURE"                            ) { return IfcMonetaryMeasure; }
    if(s=="IFCNORMALISEDRATIOMEASURE"                     ) { return IfcNormalisedRatioMeasure; }
    if(s=="IFCNULLSTYLE"                                  ) { return IfcNullStyle; }
    if(s=="IFCNUMERICMEASURE"                             ) { return IfcNumericMeasure; }
    if(s=="IFCPHMEASURE"                                  ) { return IfcPHMeasure; }
    if(s=="IFCPARAMETERVALUE"                             ) { return IfcParameterValue; }
    if(s=="IFCPLANARFORCEMEASURE"                         ) { return IfcPlanarForceMeasure; }
    if(s=="IFCPLANEANGLEMEASURE"                          ) { return IfcPlaneAngleMeasure; }
    if(s=="IFCPOSITIVELENGTHMEASURE"                      ) { return IfcPositiveLengthMeasure; }
    if(s=="IFCPOSITIVEPLANEANGLEMEASURE"                  ) { return IfcPositivePlaneAngleMeasure; }
    if(s=="IFCPOSITIVERATIOMEASURE"                       ) { return IfcPositiveRatioMeasure; }
    if(s=="IFCPOWERMEASURE"                               ) { return IfcPowerMeasure; }
    if(s=="IFCPRESSUREMEASURE"                            ) { return IfcPressureMeasure; }
    if(s=="IFCRADIOACTIVITYMEASURE"                       ) { return IfcRadioActivityMeasure; }
    if(s=="IFCRATIOMEASURE"                               ) { return IfcRatioMeasure; }
    if(s=="IFCREAL"                                       ) { return IfcReal; }
    if(s=="IFCROTATIONALFREQUENCYMEASURE"                 ) { return IfcRotationalFrequencyMeasure; }
    if(s=="IFCROTATIONALMASSMEASURE"                      ) { return IfcRotationalMassMeasure; }
    if(s=="IFCROTATIONALSTIFFNESSMEASURE"                 ) { return IfcRotationalStiffnessMeasure; }
    if(s=="IFCSECTIONMODULUSMEASURE"                      ) { return IfcSectionModulusMeasure; }
    if(s=="IFCSECTIONALAREAINTEGRALMEASURE"               ) { return IfcSectionalAreaIntegralMeasure; }
    if(s=="IFCSHEARMODULUSMEASURE"                        ) { return IfcShearModulusMeasure; }
    if(s=="IFCSIMPLEVALUE"                                ) { return IfcSimpleValue; }
    if(s=="IFCSOLIDANGLEMEASURE"                          ) { return IfcSolidAngleMeasure; }
    if(s=="IFCSOUNDPOWERMEASURE"                          ) { return IfcSoundPowerMeasure; }
    if(s=="IFCSOUNDPRESSUREMEASURE"                       ) { return IfcSoundPressureMeasure; }
    if(s=="IFCSPECIFICHEATCAPACITYMEASURE"                ) { return IfcSpecificHeatCapacityMeasure; }
    if(s=="IFCSPECULAREXPONENT"                           ) { return IfcSpecularExponent; }
    if(s=="IFCSPECULARROUGHNESS"                          ) { return IfcSpecularRoughness; }
    if(s=="IFCTEMPERATUREGRADIENTMEASURE"                 ) { return IfcTemperatureGradientMeasure; }
    if(s=="IFCTEXT"                                       ) { return IfcText; }
    if(s=="IFCTHERMALADMITTANCEMEASURE"                   ) { return IfcThermalAdmittanceMeasure; }
    if(s=="IFCTHERMALCONDUCTIVITYMEASURE"                 ) { return IfcThermalConductivityMeasure; }
    if(s=="IFCTHERMALEXPANSIONCOEFFICIENTMEASURE"         ) { return IfcThermalExpansionCoefficientMeasure; }
    if(s=="IFCTHERMALRESISTANCEMEASURE"                   ) { return IfcThermalResistanceMeasure; }
    if(s=="IFCTHERMALTRANSMITTANCEMEASURE"                ) { return IfcThermalTransmittanceMeasure; }
    if(s=="IFCTHERMODYNAMICTEMPERATUREMEASURE"            ) { return IfcThermodynamicTemperatureMeasure; }
    if(s=="IFCTIMEMEASURE"                                ) { return IfcTimeMeasure; }
    if(s=="IFCTIMESTAMP"                                  ) { return IfcTimeStamp; }
    if(s=="IFCTORQUEMEASURE"                              ) { return IfcTorqueMeasure; }
    if(s=="IFCVAPORPERMEABILITYMEASURE"                   ) { return IfcVaporPermeabilityMeasure; }
    if(s=="IFCVOLUMEMEASURE"                              ) { return IfcVolumeMeasure; }
    if(s=="IFCVOLUMETRICFLOWRATEMEASURE"                  ) { return IfcVolumetricFlowRateMeasure; }
    if(s=="IFCWARPINGCONSTANTMEASURE"                     ) { return IfcWarpingConstantMeasure; }
    if(s=="IFCWARPINGMOMENTMEASURE"                       ) { return IfcWarpingMomentMeasure; }
    if(s=="IFC2DCOMPOSITECURVE"                           ) { return Ifc2DCompositeCurve; }
    if(s=="IFCACTIONREQUEST"                              ) { return IfcActionRequest; }
    if(s=="IFCACTOR"                                      ) { return IfcActor; }
    if(s=="IFCACTORROLE"                                  ) { return IfcActorRole; }
    if(s=="IFCACTUATORTYPE"                               ) { return IfcActuatorType; }
    if(s=="IFCADDRESS"                                    ) { return IfcAddress; }
    if(s=="IFCAIRTERMINALBOXTYPE"                         ) { return IfcAirTerminalBoxType; }
    if(s=="IFCAIRTERMINALTYPE"                            ) { return IfcAirTerminalType; }
    if(s=="IFCAIRTOAIRHEATRECOVERYTYPE"                   ) { return IfcAirToAirHeatRecoveryType; }
    if(s=="IFCALARMTYPE"                                  ) { return IfcAlarmType; }
    if(s=="IFCANGULARDIMENSION"                           ) { return IfcAngularDimension; }
    if(s=="IFCANNOTATION"                                 ) { return IfcAnnotation; }
    if(s=="IFCANNOTATIONCURVEOCCURRENCE"                  ) { return IfcAnnotationCurveOccurrence; }
    if(s=="IFCANNOTATIONFILLAREA"                         ) { return IfcAnnotationFillArea; }
    if(s=="IFCANNOTATIONFILLAREAOCCURRENCE"               ) { return IfcAnnotationFillAreaOccurrence; }
    if(s=="IFCANNOTATIONOCCURRENCE"                       ) { return IfcAnnotationOccurrence; }
    if(s=="IFCANNOTATIONSURFACE"                          ) { return IfcAnnotationSurface; }
    if(s=="IFCANNOTATIONSURFACEOCCURRENCE"                ) { return IfcAnnotationSurfaceOccurrence; }
    if(s=="IFCANNOTATIONSYMBOLOCCURRENCE"                 ) { return IfcAnnotationSymbolOccurrence; }
    if(s=="IFCANNOTATIONTEXTOCCURRENCE"                   ) { return IfcAnnotationTextOccurrence; }
    if(s=="IFCAPPLICATION"                                ) { return IfcApplication; }
    if(s=="IFCAPPLIEDVALUE"                               ) { return IfcAppliedValue; }
    if(s=="IFCAPPLIEDVALUERELATIONSHIP"                   ) { return IfcAppliedValueRelationship; }
    if(s=="IFCAPPROVAL"                                   ) { return IfcApproval; }
    if(s=="IFCAPPROVALACTORRELATIONSHIP"                  ) { return IfcApprovalActorRelationship; }
    if(s=="IFCAPPROVALPROPERTYRELATIONSHIP"               ) { return IfcApprovalPropertyRelationship; }
    if(s=="IFCAPPROVALRELATIONSHIP"                       ) { return IfcApprovalRelationship; }
    if(s=="IFCARBITRARYCLOSEDPROFILEDEF"                  ) { return IfcArbitraryClosedProfileDef; }
    if(s=="IFCARBITRARYOPENPROFILEDEF"                    ) { return IfcArbitraryOpenProfileDef; }
    if(s=="IFCARBITRARYPROFILEDEFWITHVOIDS"               ) { return IfcArbitraryProfileDefWithVoids; }
    if(s=="IFCASSET"                                      ) { return IfcAsset; }
    if(s=="IFCASYMMETRICISHAPEPROFILEDEF"                 ) { return IfcAsymmetricIShapeProfileDef; }
    if(s=="IFCAXIS1PLACEMENT"                             ) { return IfcAxis1Placement; }
    if(s=="IFCAXIS2PLACEMENT2D"                           ) { return IfcAxis2Placement2D; }
    if(s=="IFCAXIS2PLACEMENT3D"                           ) { return IfcAxis2Placement3D; }
    if(s=="IFCBSPLINECURVE"                               ) { return IfcBSplineCurve; }
    if(s=="IFCBEAM"                                       ) { return IfcBeam; }
    if(s=="IFCBEAMTYPE"                                   ) { return IfcBeamType; }
    if(s=="IFCBEZIERCURVE"                                ) { return IfcBezierCurve; }
    if(s=="IFCBLOBTEXTURE"                                ) { return IfcBlobTexture; }
    if(s=="IFCBLOCK"                                      ) { return IfcBlock; }
    if(s=="IFCBOILERTYPE"                                 ) { return IfcBoilerType; }
    if(s=="IFCBOOLEANCLIPPINGRESULT"                      ) { return IfcBooleanClippingResult; }
    if(s=="IFCBOOLEANRESULT"                              ) { return IfcBooleanResult; }
    if(s=="IFCBOUNDARYCONDITION"                          ) { return IfcBoundaryCondition; }
    if(s=="IFCBOUNDARYEDGECONDITION"                      ) { return IfcBoundaryEdgeCondition; }
    if(s=="IFCBOUNDARYFACECONDITION"                      ) { return IfcBoundaryFaceCondition; }
    if(s=="IFCBOUNDARYNODECONDITION"                      ) { return IfcBoundaryNodeCondition; }
    if(s=="IFCBOUNDARYNODECONDITIONWARPING"               ) { return IfcBoundaryNodeConditionWarping; }
    if(s=="IFCBOUNDEDCURVE"                               ) { return IfcBoundedCurve; }
    if(s=="IFCBOUNDEDSURFACE"                             ) { return IfcBoundedSurface; }
    if(s=="IFCBOUNDINGBOX"                                ) { return IfcBoundingBox; }
    if(s=="IFCBOXEDHALFSPACE"                             ) { return IfcBoxedHalfSpace; }
    if(s=="IFCBUILDING"                                   ) { return IfcBuilding; }
    if(s=="IFCBUILDINGELEMENT"                            ) { return IfcBuildingElement; }
    if(s=="IFCBUILDINGELEMENTCOMPONENT"                   ) { return IfcBuildingElementComponent; }
    if(s=="IFCBUILDINGELEMENTPART"                        ) { return IfcBuildingElementPart; }
    if(s=="IFCBUILDINGELEMENTPROXY"                       ) { return IfcBuildingElementProxy; }
    if(s=="IFCBUILDINGELEMENTPROXYTYPE"                   ) { return IfcBuildingElementProxyType; }
    if(s=="IFCBUILDINGELEMENTTYPE"                        ) { return IfcBuildingElementType; }
    if(s=="IFCBUILDINGSTOREY"                             ) { return IfcBuildingStorey; }
    if(s=="IFCCSHAPEPROFILEDEF"                           ) { return IfcCShapeProfileDef; }
    if(s=="IFCCABLECARRIERFITTINGTYPE"                    ) { return IfcCableCarrierFittingType; }
    if(s=="IFCCABLECARRIERSEGMENTTYPE"                    ) { return IfcCableCarrierSegmentType; }
    if(s=="IFCCABLESEGMENTTYPE"                           ) { return IfcCableSegmentType; }
    if(s=="IFCCALENDARDATE"                               ) { return IfcCalendarDate; }
    if(s=="IFCCARTESIANPOINT"                             ) { return IfcCartesianPoint; }
    if(s=="IFCCARTESIANTRANSFORMATIONOPERATOR"            ) { return IfcCartesianTransformationOperator; }
    if(s=="IFCCARTESIANTRANSFORMATIONOPERATOR2D"          ) { return IfcCartesianTransformationOperator2D; }
    if(s=="IFCCARTESIANTRANSFORMATIONOPERATOR2DNONUNIFORM") { return IfcCartesianTransformationOperator2DnonUniform; }
    if(s=="IFCCARTESIANTRANSFORMATIONOPERATOR3D"          ) { return IfcCartesianTransformationOperator3D; }
    if(s=="IFCCARTESIANTRANSFORMATIONOPERATOR3DNONUNIFORM") { return IfcCartesianTransformationOperator3DnonUniform; }
    if(s=="IFCCENTERLINEPROFILEDEF"                       ) { return IfcCenterLineProfileDef; }
    if(s=="IFCCHAMFEREDGEFEATURE"                         ) { return IfcChamferEdgeFeature; }
    if(s=="IFCCHILLERTYPE"                                ) { return IfcChillerType; }
    if(s=="IFCCIRCLE"                                     ) { return IfcCircle; }
    if(s=="IFCCIRCLEHOLLOWPROFILEDEF"                     ) { return IfcCircleHollowProfileDef; }
    if(s=="IFCCIRCLEPROFILEDEF"                           ) { return IfcCircleProfileDef; }
    if(s=="IFCCLASSIFICATION"                             ) { return IfcClassification; }
    if(s=="IFCCLASSIFICATIONITEM"                         ) { return IfcClassificationItem; }
    if(s=="IFCCLASSIFICATIONITEMRELATIONSHIP"             ) { return IfcClassificationItemRelationship; }
    if(s=="IFCCLASSIFICATIONNOTATION"                     ) { return IfcClassificationNotation; }
    if(s=="IFCCLASSIFICATIONNOTATIONFACET"                ) { return IfcClassificationNotationFacet; }
    if(s=="IFCCLASSIFICATIONREFERENCE"                    ) { return IfcClassificationReference; }
    if(s=="IFCCLOSEDSHELL"                                ) { return IfcClosedShell; }
    if(s=="IFCCOILTYPE"                                   ) { return IfcCoilType; }
    if(s=="IFCCOLOURRGB"                                  ) { return IfcColourRgb; }
    if(s=="IFCCOLOURSPECIFICATION"                        ) { return IfcColourSpecification; }
    if(s=="IFCCOLUMN"                                     ) { return IfcColumn; }
    if(s=="IFCCOLUMNTYPE"                                 ) { return IfcColumnType; }
    if(s=="IFCCOMPLEXPROPERTY"                            ) { return IfcComplexProperty; }
    if(s=="IFCCOMPOSITECURVE"                             ) { return IfcCompositeCurve; }
    if(s=="IFCCOMPOSITECURVESEGMENT"                      ) { return IfcCompositeCurveSegment; }
    if(s=="IFCCOMPOSITEPROFILEDEF"                        ) { return IfcCompositeProfileDef; }
    if(s=="IFCCOMPRESSORTYPE"                             ) { return IfcCompressorType; }
    if(s=="IFCCONDENSERTYPE"                              ) { return IfcCondenserType; }
    if(s=="IFCCONDITION"                                  ) { return IfcCondition; }
    if(s=="IFCCONDITIONCRITERION"                         ) { return IfcConditionCriterion; }
    if(s=="IFCCONIC"                                      ) { return IfcConic; }
    if(s=="IFCCONNECTEDFACESET"                           ) { return IfcConnectedFaceSet; }
    if(s=="IFCCONNECTIONCURVEGEOMETRY"                    ) { return IfcConnectionCurveGeometry; }
    if(s=="IFCCONNECTIONGEOMETRY"                         ) { return IfcConnectionGeometry; }
    if(s=="IFCCONNECTIONPOINTECCENTRICITY"                ) { return IfcConnectionPointEccentricity; }
    if(s=="IFCCONNECTIONPOINTGEOMETRY"                    ) { return IfcConnectionPointGeometry; }
    if(s=="IFCCONNECTIONPORTGEOMETRY"                     ) { return IfcConnectionPortGeometry; }
    if(s=="IFCCONNECTIONSURFACEGEOMETRY"                  ) { return IfcConnectionSurfaceGeometry; }
    if(s=="IFCCONSTRAINT"                                 ) { return IfcConstraint; }
    if(s=="IFCCONSTRAINTAGGREGATIONRELATIONSHIP"          ) { return IfcConstraintAggregationRelationship; }
    if(s=="IFCCONSTRAINTCLASSIFICATIONRELATIONSHIP"       ) { return IfcConstraintClassificationRelationship; }
    if(s=="IFCCONSTRAINTRELATIONSHIP"                     ) { return IfcConstraintRelationship; }
    if(s=="IFCCONSTRUCTIONEQUIPMENTRESOURCE"              ) { return IfcConstructionEquipmentResource; }
    if(s=="IFCCONSTRUCTIONMATERIALRESOURCE"               ) { return IfcConstructionMaterialResource; }
    if(s=="IFCCONSTRUCTIONPRODUCTRESOURCE"                ) { return IfcConstructionProductResource; }
    if(s=="IFCCONSTRUCTIONRESOURCE"                       ) { return IfcConstructionResource; }
    if(s=="IFCCONTEXTDEPENDENTUNIT"                       ) { return IfcContextDependentUnit; }
    if(s=="IFCCONTROL"                                    ) { return IfcControl; }
    if(s=="IFCCONTROLLERTYPE"                             ) { return IfcControllerType; }
    if(s=="IFCCONVERSIONBASEDUNIT"                        ) { return IfcConversionBasedUnit; }
    if(s=="IFCCOOLEDBEAMTYPE"                             ) { return IfcCooledBeamType; }
    if(s=="IFCCOOLINGTOWERTYPE"                           ) { return IfcCoolingTowerType; }
    if(s=="IFCCOORDINATEDUNIVERSALTIMEOFFSET"             ) { return IfcCoordinatedUniversalTimeOffset; }
    if(s=="IFCCOSTITEM"                                   ) { return IfcCostItem; }
    if(s=="IFCCOSTSCHEDULE"                               ) { return IfcCostSchedule; }
    if(s=="IFCCOSTVALUE"                                  ) { return IfcCostValue; }
    if(s=="IFCCOVERING"                                   ) { return IfcCovering; }
    if(s=="IFCCOVERINGTYPE"                               ) { return IfcCoveringType; }
    if(s=="IFCCRANERAILASHAPEPROFILEDEF"                  ) { return IfcCraneRailAShapeProfileDef; }
    if(s=="IFCCRANERAILFSHAPEPROFILEDEF"                  ) { return IfcCraneRailFShapeProfileDef; }
    if(s=="IFCCREWRESOURCE"                               ) { return IfcCrewResource; }
    if(s=="IFCCSGPRIMITIVE3D"                             ) { return IfcCsgPrimitive3D; }
    if(s=="IFCCSGSOLID"                                   ) { return IfcCsgSolid; }
    if(s=="IFCCURRENCYRELATIONSHIP"                       ) { return IfcCurrencyRelationship; }
    if(s=="IFCCURTAINWALL"                                ) { return IfcCurtainWall; }
    if(s=="IFCCURTAINWALLTYPE"                            ) { return IfcCurtainWallType; }
    if(s=="IFCCURVE"                                      ) { return IfcCurve; }
    if(s=="IFCCURVEBOUNDEDPLANE"                          ) { return IfcCurveBoundedPlane; }
    if(s=="IFCCURVESTYLE"                                 ) { return IfcCurveStyle; }
    if(s=="IFCCURVESTYLEFONT"                             ) { return IfcCurveStyleFont; }
    if(s=="IFCCURVESTYLEFONTANDSCALING"                   ) { return IfcCurveStyleFontAndScaling; }
    if(s=="IFCCURVESTYLEFONTPATTERN"                      ) { return IfcCurveStyleFontPattern; }
    if(s=="IFCDAMPERTYPE"                                 ) { return IfcDamperType; }
    if(s=="IFCDATEANDTIME"                                ) { return IfcDateAndTime; }
    if(s=="IFCDEFINEDSYMBOL"                              ) { return IfcDefinedSymbol; }
    if(s=="IFCDERIVEDPROFILEDEF"                          ) { return IfcDerivedProfileDef; }
    if(s=="IFCDERIVEDUNIT"                                ) { return IfcDerivedUnit; }
    if(s=="IFCDERIVEDUNITELEMENT"                         ) { return IfcDerivedUnitElement; }
    if(s=="IFCDIAMETERDIMENSION"                          ) { return IfcDiameterDimension; }
    if(s=="IFCDIMENSIONCALLOUTRELATIONSHIP"               ) { return IfcDimensionCalloutRelationship; }
    if(s=="IFCDIMENSIONCURVE"                             ) { return IfcDimensionCurve; }
    if(s=="IFCDIMENSIONCURVEDIRECTEDCALLOUT"              ) { return IfcDimensionCurveDirectedCallout; }
    if(s=="IFCDIMENSIONCURVETERMINATOR"                   ) { return IfcDimensionCurveTerminator; }
    if(s=="IFCDIMENSIONPAIR"                              ) { return IfcDimensionPair; }
    if(s=="IFCDIMENSIONALEXPONENTS"                       ) { return IfcDimensionalExponents; }
    if(s=="IFCDIRECTION"                                  ) { return IfcDirection; }
    if(s=="IFCDISCRETEACCESSORY"                          ) { return IfcDiscreteAccessory; }
    if(s=="IFCDISCRETEACCESSORYTYPE"                      ) { return IfcDiscreteAccessoryType; }
    if(s=="IFCDISTRIBUTIONCHAMBERELEMENT"                 ) { return IfcDistributionChamberElement; }
    if(s=="IFCDISTRIBUTIONCHAMBERELEMENTTYPE"             ) { return IfcDistributionChamberElementType; }
    if(s=="IFCDISTRIBUTIONCONTROLELEMENT"                 ) { return IfcDistributionControlElement; }
    if(s=="IFCDISTRIBUTIONCONTROLELEMENTTYPE"             ) { return IfcDistributionControlElementType; }
    if(s=="IFCDISTRIBUTIONELEMENT"                        ) { return IfcDistributionElement; }
    if(s=="IFCDISTRIBUTIONELEMENTTYPE"                    ) { return IfcDistributionElementType; }
    if(s=="IFCDISTRIBUTIONFLOWELEMENT"                    ) { return IfcDistributionFlowElement; }
    if(s=="IFCDISTRIBUTIONFLOWELEMENTTYPE"                ) { return IfcDistributionFlowElementType; }
    if(s=="IFCDISTRIBUTIONPORT"                           ) { return IfcDistributionPort; }
    if(s=="IFCDOCUMENTELECTRONICFORMAT"                   ) { return IfcDocumentElectronicFormat; }
    if(s=="IFCDOCUMENTINFORMATION"                        ) { return IfcDocumentInformation; }
    if(s=="IFCDOCUMENTINFORMATIONRELATIONSHIP"            ) { return IfcDocumentInformationRelationship; }
    if(s=="IFCDOCUMENTREFERENCE"                          ) { return IfcDocumentReference; }
    if(s=="IFCDOOR"                                       ) { return IfcDoor; }
    if(s=="IFCDOORLININGPROPERTIES"                       ) { return IfcDoorLiningProperties; }
    if(s=="IFCDOORPANELPROPERTIES"                        ) { return IfcDoorPanelProperties; }
    if(s=="IFCDOORSTYLE"                                  ) { return IfcDoorStyle; }
    if(s=="IFCDRAUGHTINGCALLOUT"                          ) { return IfcDraughtingCallout; }
    if(s=="IFCDRAUGHTINGCALLOUTRELATIONSHIP"              ) { return IfcDraughtingCalloutRelationship; }
    if(s=="IFCDRAUGHTINGPREDEFINEDCOLOUR"                 ) { return IfcDraughtingPreDefinedColour; }
    if(s=="IFCDRAUGHTINGPREDEFINEDCURVEFONT"              ) { return IfcDraughtingPreDefinedCurveFont; }
    if(s=="IFCDRAUGHTINGPREDEFINEDTEXTFONT"               ) { return IfcDraughtingPreDefinedTextFont; }
    if(s=="IFCDUCTFITTINGTYPE"                            ) { return IfcDuctFittingType; }
    if(s=="IFCDUCTSEGMENTTYPE"                            ) { return IfcDuctSegmentType; }
    if(s=="IFCDUCTSILENCERTYPE"                           ) { return IfcDuctSilencerType; }
    if(s=="IFCEDGE"                                       ) { return IfcEdge; }
    if(s=="IFCEDGECURVE"                                  ) { return IfcEdgeCurve; }
    if(s=="IFCEDGEFEATURE"                                ) { return IfcEdgeFeature; }
    if(s=="IFCEDGELOOP"                                   ) { return IfcEdgeLoop; }
    if(s=="IFCELECTRICAPPLIANCETYPE"                      ) { return IfcElectricApplianceType; }
    if(s=="IFCELECTRICDISTRIBUTIONPOINT"                  ) { return IfcElectricDistributionPoint; }
    if(s=="IFCELECTRICFLOWSTORAGEDEVICETYPE"              ) { return IfcElectricFlowStorageDeviceType; }
    if(s=="IFCELECTRICGENERATORTYPE"                      ) { return IfcElectricGeneratorType; }
    if(s=="IFCELECTRICHEATERTYPE"                         ) { return IfcElectricHeaterType; }
    if(s=="IFCELECTRICMOTORTYPE"                          ) { return IfcElectricMotorType; }
    if(s=="IFCELECTRICTIMECONTROLTYPE"                    ) { return IfcElectricTimeControlType; }
    if(s=="IFCELECTRICALBASEPROPERTIES"                   ) { return IfcElectricalBaseProperties; }
    if(s=="IFCELECTRICALCIRCUIT"                          ) { return IfcElectricalCircuit; }
    if(s=="IFCELECTRICALELEMENT"                          ) { return IfcElectricalElement; }
    if(s=="IFCELEMENT"                                    ) { return IfcElement; }
    if(s=="IFCELEMENTASSEMBLY"                            ) { return IfcElementAssembly; }
    if(s=="IFCELEMENTCOMPONENT"                           ) { return IfcElementComponent; }
    if(s=="IFCELEMENTCOMPONENTTYPE"                       ) { return IfcElementComponentType; }
    if(s=="IFCELEMENTQUANTITY"                            ) { return IfcElementQuantity; }
    if(s=="IFCELEMENTTYPE"                                ) { return IfcElementType; }
    if(s=="IFCELEMENTARYSURFACE"                          ) { return IfcElementarySurface; }
    if(s=="IFCELLIPSE"                                    ) { return IfcEllipse; }
    if(s=="IFCELLIPSEPROFILEDEF"                          ) { return IfcEllipseProfileDef; }
    if(s=="IFCENERGYCONVERSIONDEVICE"                     ) { return IfcEnergyConversionDevice; }
    if(s=="IFCENERGYCONVERSIONDEVICETYPE"                 ) { return IfcEnergyConversionDeviceType; }
    if(s=="IFCENERGYPROPERTIES"                           ) { return IfcEnergyProperties; }
    if(s=="IFCENVIRONMENTALIMPACTVALUE"                   ) { return IfcEnvironmentalImpactValue; }
    if(s=="IFCEQUIPMENTELEMENT"                           ) { return IfcEquipmentElement; }
    if(s=="IFCEQUIPMENTSTANDARD"                          ) { return IfcEquipmentStandard; }
    if(s=="IFCEVAPORATIVECOOLERTYPE"                      ) { return IfcEvaporativeCoolerType; }
    if(s=="IFCEVAPORATORTYPE"                             ) { return IfcEvaporatorType; }
    if(s=="IFCEXTENDEDMATERIALPROPERTIES"                 ) { return IfcExtendedMaterialProperties; }
    if(s=="IFCEXTERNALREFERENCE"                          ) { return IfcExternalReference; }
    if(s=="IFCEXTERNALLYDEFINEDHATCHSTYLE"                ) { return IfcExternallyDefinedHatchStyle; }
    if(s=="IFCEXTERNALLYDEFINEDSURFACESTYLE"              ) { return IfcExternallyDefinedSurfaceStyle; }
    if(s=="IFCEXTERNALLYDEFINEDSYMBOL"                    ) { return IfcExternallyDefinedSymbol; }
    if(s=="IFCEXTERNALLYDEFINEDTEXTFONT"                  ) { return IfcExternallyDefinedTextFont; }
    if(s=="IFCEXTRUDEDAREASOLID"                          ) { return IfcExtrudedAreaSolid; }
    if(s=="IFCFACE"                                       ) { return IfcFace; }
    if(s=="IFCFACEBASEDSURFACEMODEL"                      ) { return IfcFaceBasedSurfaceModel; }
    if(s=="IFCFACEBOUND"                                  ) { return IfcFaceBound; }
    if(s=="IFCFACEOUTERBOUND"                             ) { return IfcFaceOuterBound; }
    if(s=="IFCFACESURFACE"                                ) { return IfcFaceSurface; }
    if(s=="IFCFACETEDBREP"                                ) { return IfcFacetedBrep; }
    if(s=="IFCFACETEDBREPWITHVOIDS"                       ) { return IfcFacetedBrepWithVoids; }
    if(s=="IFCFAILURECONNECTIONCONDITION"                 ) { return IfcFailureConnectionCondition; }
    if(s=="IFCFANTYPE"                                    ) { return IfcFanType; }
    if(s=="IFCFASTENER"                                   ) { return IfcFastener; }
    if(s=="IFCFASTENERTYPE"                               ) { return IfcFastenerType; }
    if(s=="IFCFEATUREELEMENT"                             ) { return IfcFeatureElement; }
    if(s=="IFCFEATUREELEMENTADDITION"                     ) { return IfcFeatureElementAddition; }
    if(s=="IFCFEATUREELEMENTSUBTRACTION"                  ) { return IfcFeatureElementSubtraction; }
    if(s=="IFCFILLAREASTYLE"                              ) { return IfcFillAreaStyle; }
    if(s=="IFCFILLAREASTYLEHATCHING"                      ) { return IfcFillAreaStyleHatching; }
    if(s=="IFCFILLAREASTYLETILESYMBOLWITHSTYLE"           ) { return IfcFillAreaStyleTileSymbolWithStyle; }
    if(s=="IFCFILLAREASTYLETILES"                         ) { return IfcFillAreaStyleTiles; }
    if(s=="IFCFILTERTYPE"                                 ) { return IfcFilterType; }
    if(s=="IFCFIRESUPPRESSIONTERMINALTYPE"                ) { return IfcFireSuppressionTerminalType; }
    if(s=="IFCFLOWCONTROLLER"                             ) { return IfcFlowController; }
    if(s=="IFCFLOWCONTROLLERTYPE"                         ) { return IfcFlowControllerType; }
    if(s=="IFCFLOWFITTING"                                ) { return IfcFlowFitting; }
    if(s=="IFCFLOWFITTINGTYPE"                            ) { return IfcFlowFittingType; }
    if(s=="IFCFLOWINSTRUMENTTYPE"                         ) { return IfcFlowInstrumentType; }
    if(s=="IFCFLOWMETERTYPE"                              ) { return IfcFlowMeterType; }
    if(s=="IFCFLOWMOVINGDEVICE"                           ) { return IfcFlowMovingDevice; }
    if(s=="IFCFLOWMOVINGDEVICETYPE"                       ) { return IfcFlowMovingDeviceType; }
    if(s=="IFCFLOWSEGMENT"                                ) { return IfcFlowSegment; }
    if(s=="IFCFLOWSEGMENTTYPE"                            ) { return IfcFlowSegmentType; }
    if(s=="IFCFLOWSTORAGEDEVICE"                          ) { return IfcFlowStorageDevice; }
    if(s=="IFCFLOWSTORAGEDEVICETYPE"                      ) { return IfcFlowStorageDeviceType; }
    if(s=="IFCFLOWTERMINAL"                               ) { return IfcFlowTerminal; }
    if(s=="IFCFLOWTERMINALTYPE"                           ) { return IfcFlowTerminalType; }
    if(s=="IFCFLOWTREATMENTDEVICE"                        ) { return IfcFlowTreatmentDevice; }
    if(s=="IFCFLOWTREATMENTDEVICETYPE"                    ) { return IfcFlowTreatmentDeviceType; }
    if(s=="IFCFLUIDFLOWPROPERTIES"                        ) { return IfcFluidFlowProperties; }
    if(s=="IFCFOOTING"                                    ) { return IfcFooting; }
    if(s=="IFCFUELPROPERTIES"                             ) { return IfcFuelProperties; }
    if(s=="IFCFURNISHINGELEMENT"                          ) { return IfcFurnishingElement; }
    if(s=="IFCFURNISHINGELEMENTTYPE"                      ) { return IfcFurnishingElementType; }
    if(s=="IFCFURNITURESTANDARD"                          ) { return IfcFurnitureStandard; }
    if(s=="IFCFURNITURETYPE"                              ) { return IfcFurnitureType; }
    if(s=="IFCGASTERMINALTYPE"                            ) { return IfcGasTerminalType; }
    if(s=="IFCGENERALMATERIALPROPERTIES"                  ) { return IfcGeneralMaterialProperties; }
    if(s=="IFCGENERALPROFILEPROPERTIES"                   ) { return IfcGeneralProfileProperties; }
    if(s=="IFCGEOMETRICCURVESET"                          ) { return IfcGeometricCurveSet; }
    if(s=="IFCGEOMETRICREPRESENTATIONCONTEXT"             ) { return IfcGeometricRepresentationContext; }
    if(s=="IFCGEOMETRICREPRESENTATIONITEM"                ) { return IfcGeometricRepresentationItem; }
    if(s=="IFCGEOMETRICREPRESENTATIONSUBCONTEXT"          ) { return IfcGeometricRepresentationSubContext; }
    if(s=="IFCGEOMETRICSET"                               ) { return IfcGeometricSet; }
    if(s=="IFCGRID"                                       ) { return IfcGrid; }
    if(s=="IFCGRIDAXIS"                                   ) { return IfcGridAxis; }
    if(s=="IFCGRIDPLACEMENT"                              ) { return IfcGridPlacement; }
    if(s=="IFCGROUP"                                      ) { return IfcGroup; }
    if(s=="IFCHALFSPACESOLID"                             ) { return IfcHalfSpaceSolid; }
    if(s=="IFCHEATEXCHANGERTYPE"                          ) { return IfcHeatExchangerType; }
    if(s=="IFCHUMIDIFIERTYPE"                             ) { return IfcHumidifierType; }
    if(s=="IFCHYGROSCOPICMATERIALPROPERTIES"              ) { return IfcHygroscopicMaterialProperties; }
    if(s=="IFCISHAPEPROFILEDEF"                           ) { return IfcIShapeProfileDef; }
    if(s=="IFCIMAGETEXTURE"                               ) { return IfcImageTexture; }
    if(s=="IFCINVENTORY"                                  ) { return IfcInventory; }
    if(s=="IFCIRREGULARTIMESERIES"                        ) { return IfcIrregularTimeSeries; }
    if(s=="IFCIRREGULARTIMESERIESVALUE"                   ) { return IfcIrregularTimeSeriesValue; }
    if(s=="IFCJUNCTIONBOXTYPE"                            ) { return IfcJunctionBoxType; }
    if(s=="IFCLSHAPEPROFILEDEF"                           ) { return IfcLShapeProfileDef; }
    if(s=="IFCLABORRESOURCE"                              ) { return IfcLaborResource; }
    if(s=="IFCLAMPTYPE"                                   ) { return IfcLampType; }
    if(s=="IFCLIBRARYINFORMATION"                         ) { return IfcLibraryInformation; }
    if(s=="IFCLIBRARYREFERENCE"                           ) { return IfcLibraryReference; }
    if(s=="IFCLIGHTDISTRIBUTIONDATA"                      ) { return IfcLightDistributionData; }
    if(s=="IFCLIGHTFIXTURETYPE"                           ) { return IfcLightFixtureType; }
    if(s=="IFCLIGHTINTENSITYDISTRIBUTION"                 ) { return IfcLightIntensityDistribution; }
    if(s=="IFCLIGHTSOURCE"                                ) { return IfcLightSource; }
    if(s=="IFCLIGHTSOURCEAMBIENT"                         ) { return IfcLightSourceAmbient; }
    if(s=="IFCLIGHTSOURCEDIRECTIONAL"                     ) { return IfcLightSourceDirectional; }
    if(s=="IFCLIGHTSOURCEGONIOMETRIC"                     ) { return IfcLightSourceGoniometric; }
    if(s=="IFCLIGHTSOURCEPOSITIONAL"                      ) { return IfcLightSourcePositional; }
    if(s=="IFCLIGHTSOURCESPOT"                            ) { return IfcLightSourceSpot; }
    if(s=="IFCLINE"                                       ) { return IfcLine; }
    if(s=="IFCLINEARDIMENSION"                            ) { return IfcLinearDimension; }
    if(s=="IFCLOCALPLACEMENT"                             ) { return IfcLocalPlacement; }
    if(s=="IFCLOCALTIME"                                  ) { return IfcLocalTime; }
    if(s=="IFCLOOP"                                       ) { return IfcLoop; }
    if(s=="IFCMANIFOLDSOLIDBREP"                          ) { return IfcManifoldSolidBrep; }
    if(s=="IFCMAPPEDITEM"                                 ) { return IfcMappedItem; }
    if(s=="IFCMATERIAL"                                   ) { return IfcMaterial; }
    if(s=="IFCMATERIALCLASSIFICATIONRELATIONSHIP"         ) { return IfcMaterialClassificationRelationship; }
    if(s=="IFCMATERIALDEFINITIONREPRESENTATION"           ) { return IfcMaterialDefinitionRepresentation; }
    if(s=="IFCMATERIALLAYER"                              ) { return IfcMaterialLayer; }
    if(s=="IFCMATERIALLAYERSET"                           ) { return IfcMaterialLayerSet; }
    if(s=="IFCMATERIALLAYERSETUSAGE"                      ) { return IfcMaterialLayerSetUsage; }
    if(s=="IFCMATERIALLIST"                               ) { return IfcMaterialList; }
    if(s=="IFCMATERIALPROPERTIES"                         ) { return IfcMaterialProperties; }
    if(s=="IFCMEASUREWITHUNIT"                            ) { return IfcMeasureWithUnit; }
    if(s=="IFCMECHANICALCONCRETEMATERIALPROPERTIES"       ) { return IfcMechanicalConcreteMaterialProperties; }
    if(s=="IFCMECHANICALFASTENER"                         ) { return IfcMechanicalFastener; }
    if(s=="IFCMECHANICALFASTENERTYPE"                     ) { return IfcMechanicalFastenerType; }
    if(s=="IFCMECHANICALMATERIALPROPERTIES"               ) { return IfcMechanicalMaterialProperties; }
    if(s=="IFCMECHANICALSTEELMATERIALPROPERTIES"          ) { return IfcMechanicalSteelMaterialProperties; }
    if(s=="IFCMEMBER"                                     ) { return IfcMember; }
    if(s=="IFCMEMBERTYPE"                                 ) { return IfcMemberType; }
    if(s=="IFCMETRIC"                                     ) { return IfcMetric; }
    if(s=="IFCMONETARYUNIT"                               ) { return IfcMonetaryUnit; }
    if(s=="IFCMOTORCONNECTIONTYPE"                        ) { return IfcMotorConnectionType; }
    if(s=="IFCMOVE"                                       ) { return IfcMove; }
    if(s=="IFCNAMEDUNIT"                                  ) { return IfcNamedUnit; }
    if(s=="IFCOBJECT"                                     ) { return IfcObject; }
    if(s=="IFCOBJECTDEFINITION"                           ) { return IfcObjectDefinition; }
    if(s=="IFCOBJECTPLACEMENT"                            ) { return IfcObjectPlacement; }
    if(s=="IFCOBJECTIVE"                                  ) { return IfcObjective; }
    if(s=="IFCOCCUPANT"                                   ) { return IfcOccupant; }
    if(s=="IFCOFFSETCURVE2D"                              ) { return IfcOffsetCurve2D; }
    if(s=="IFCOFFSETCURVE3D"                              ) { return IfcOffsetCurve3D; }
    if(s=="IFCONEDIRECTIONREPEATFACTOR"                   ) { return IfcOneDirectionRepeatFactor; }
    if(s=="IFCOPENSHELL"                                  ) { return IfcOpenShell; }
    if(s=="IFCOPENINGELEMENT"                             ) { return IfcOpeningElement; }
    if(s=="IFCOPTICALMATERIALPROPERTIES"                  ) { return IfcOpticalMaterialProperties; }
    if(s=="IFCORDERACTION"                                ) { return IfcOrderAction; }
    if(s=="IFCORGANIZATION"                               ) { return IfcOrganization; }
    if(s=="IFCORGANIZATIONRELATIONSHIP"                   ) { return IfcOrganizationRelationship; }
    if(s=="IFCORIENTEDEDGE"                               ) { return IfcOrientedEdge; }
    if(s=="IFCOUTLETTYPE"                                 ) { return IfcOutletType; }
    if(s=="IFCOWNERHISTORY"                               ) { return IfcOwnerHistory; }
    if(s=="IFCPARAMETERIZEDPROFILEDEF"                    ) { return IfcParameterizedProfileDef; }
    if(s=="IFCPATH"                                       ) { return IfcPath; }
    if(s=="IFCPERFORMANCEHISTORY"                         ) { return IfcPerformanceHistory; }
    if(s=="IFCPERMEABLECOVERINGPROPERTIES"                ) { return IfcPermeableCoveringProperties; }
    if(s=="IFCPERMIT"                                     ) { return IfcPermit; }
    if(s=="IFCPERSON"                                     ) { return IfcPerson; }
    if(s=="IFCPERSONANDORGANIZATION"                      ) { return IfcPersonAndOrganization; }
    if(s=="IFCPHYSICALCOMPLEXQUANTITY"                    ) { return IfcPhysicalComplexQuantity; }
    if(s=="IFCPHYSICALQUANTITY"                           ) { return IfcPhysicalQuantity; }
    if(s=="IFCPHYSICALSIMPLEQUANTITY"                     ) { return IfcPhysicalSimpleQuantity; }
    if(s=="IFCPILE"                                       ) { return IfcPile; }
    if(s=="IFCPIPEFITTINGTYPE"                            ) { return IfcPipeFittingType; }
    if(s=="IFCPIPESEGMENTTYPE"                            ) { return IfcPipeSegmentType; }
    if(s=="IFCPIXELTEXTURE"                               ) { return IfcPixelTexture; }
    if(s=="IFCPLACEMENT"                                  ) { return IfcPlacement; }
    if(s=="IFCPLANARBOX"                                  ) { return IfcPlanarBox; }
    if(s=="IFCPLANAREXTENT"                               ) { return IfcPlanarExtent; }
    if(s=="IFCPLANE"                                      ) { return IfcPlane; }
    if(s=="IFCPLATE"                                      ) { return IfcPlate; }
    if(s=="IFCPLATETYPE"                                  ) { return IfcPlateType; }
    if(s=="IFCPOINT"                                      ) { return IfcPoint; }
    if(s=="IFCPOINTONCURVE"                               ) { return IfcPointOnCurve; }
    if(s=="IFCPOINTONSURFACE"                             ) { return IfcPointOnSurface; }
    if(s=="IFCPOLYLOOP"                                   ) { return IfcPolyLoop; }
    if(s=="IFCPOLYGONALBOUNDEDHALFSPACE"                  ) { return IfcPolygonalBoundedHalfSpace; }
    if(s=="IFCPOLYLINE"                                   ) { return IfcPolyline; }
    if(s=="IFCPORT"                                       ) { return IfcPort; }
    if(s=="IFCPOSTALADDRESS"                              ) { return IfcPostalAddress; }
    if(s=="IFCPREDEFINEDCOLOUR"                           ) { return IfcPreDefinedColour; }
    if(s=="IFCPREDEFINEDCURVEFONT"                        ) { return IfcPreDefinedCurveFont; }
    if(s=="IFCPREDEFINEDDIMENSIONSYMBOL"                  ) { return IfcPreDefinedDimensionSymbol; }
    if(s=="IFCPREDEFINEDITEM"                             ) { return IfcPreDefinedItem; }
    if(s=="IFCPREDEFINEDPOINTMARKERSYMBOL"                ) { return IfcPreDefinedPointMarkerSymbol; }
    if(s=="IFCPREDEFINEDSYMBOL"                           ) { return IfcPreDefinedSymbol; }
    if(s=="IFCPREDEFINEDTERMINATORSYMBOL"                 ) { return IfcPreDefinedTerminatorSymbol; }
    if(s=="IFCPREDEFINEDTEXTFONT"                         ) { return IfcPreDefinedTextFont; }
    if(s=="IFCPRESENTATIONLAYERASSIGNMENT"                ) { return IfcPresentationLayerAssignment; }
    if(s=="IFCPRESENTATIONLAYERWITHSTYLE"                 ) { return IfcPresentationLayerWithStyle; }
    if(s=="IFCPRESENTATIONSTYLE"                          ) { return IfcPresentationStyle; }
    if(s=="IFCPRESENTATIONSTYLEASSIGNMENT"                ) { return IfcPresentationStyleAssignment; }
    if(s=="IFCPROCEDURE"                                  ) { return IfcProcedure; }
    if(s=="IFCPROCESS"                                    ) { return IfcProcess; }
    if(s=="IFCPRODUCT"                                    ) { return IfcProduct; }
    if(s=="IFCPRODUCTDEFINITIONSHAPE"                     ) { return IfcProductDefinitionShape; }
    if(s=="IFCPRODUCTREPRESENTATION"                      ) { return IfcProductRepresentation; }
    if(s=="IFCPRODUCTSOFCOMBUSTIONPROPERTIES"             ) { return IfcProductsOfCombustionProperties; }
    if(s=="IFCPROFILEDEF"                                 ) { return IfcProfileDef; }
    if(s=="IFCPROFILEPROPERTIES"                          ) { return IfcProfileProperties; }
    if(s=="IFCPROJECT"                                    ) { return IfcProject; }
    if(s=="IFCPROJECTORDER"                               ) { return IfcProjectOrder; }
    if(s=="IFCPROJECTORDERRECORD"                         ) { return IfcProjectOrderRecord; }
    if(s=="IFCPROJECTIONCURVE"                            ) { return IfcProjectionCurve; }
    if(s=="IFCPROJECTIONELEMENT"                          ) { return IfcProjectionElement; }
    if(s=="IFCPROPERTY"                                   ) { return IfcProperty; }
    if(s=="IFCPROPERTYBOUNDEDVALUE"                       ) { return IfcPropertyBoundedValue; }
    if(s=="IFCPROPERTYCONSTRAINTRELATIONSHIP"             ) { return IfcPropertyConstraintRelationship; }
    if(s=="IFCPROPERTYDEFINITION"                         ) { return IfcPropertyDefinition; }
    if(s=="IFCPROPERTYDEPENDENCYRELATIONSHIP"             ) { return IfcPropertyDependencyRelationship; }
    if(s=="IFCPROPERTYENUMERATEDVALUE"                    ) { return IfcPropertyEnumeratedValue; }
    if(s=="IFCPROPERTYENUMERATION"                        ) { return IfcPropertyEnumeration; }
    if(s=="IFCPROPERTYLISTVALUE"                          ) { return IfcPropertyListValue; }
    if(s=="IFCPROPERTYREFERENCEVALUE"                     ) { return IfcPropertyReferenceValue; }
    if(s=="IFCPROPERTYSET"                                ) { return IfcPropertySet; }
    if(s=="IFCPROPERTYSETDEFINITION"                      ) { return IfcPropertySetDefinition; }
    if(s=="IFCPROPERTYSINGLEVALUE"                        ) { return IfcPropertySingleValue; }
    if(s=="IFCPROPERTYTABLEVALUE"                         ) { return IfcPropertyTableValue; }
    if(s=="IFCPROTECTIVEDEVICETYPE"                       ) { return IfcProtectiveDeviceType; }
    if(s=="IFCPROXY"                                      ) { return IfcProxy; }
    if(s=="IFCPUMPTYPE"                                   ) { return IfcPumpType; }
    if(s=="IFCQUANTITYAREA"                               ) { return IfcQuantityArea; }
    if(s=="IFCQUANTITYCOUNT"                              ) { return IfcQuantityCount; }
    if(s=="IFCQUANTITYLENGTH"                             ) { return IfcQuantityLength; }
    if(s=="IFCQUANTITYTIME"                               ) { return IfcQuantityTime; }
    if(s=="IFCQUANTITYVOLUME"                             ) { return IfcQuantityVolume; }
    if(s=="IFCQUANTITYWEIGHT"                             ) { return IfcQuantityWeight; }
    if(s=="IFCRADIUSDIMENSION"                            ) { return IfcRadiusDimension; }
    if(s=="IFCRAILING"                                    ) { return IfcRailing; }
    if(s=="IFCRAILINGTYPE"                                ) { return IfcRailingType; }
    if(s=="IFCRAMP"                                       ) { return IfcRamp; }
    if(s=="IFCRAMPFLIGHT"                                 ) { return IfcRampFlight; }
    if(s=="IFCRAMPFLIGHTTYPE"                             ) { return IfcRampFlightType; }
    if(s=="IFCRATIONALBEZIERCURVE"                        ) { return IfcRationalBezierCurve; }
    if(s=="IFCRECTANGLEHOLLOWPROFILEDEF"                  ) { return IfcRectangleHollowProfileDef; }
    if(s=="IFCRECTANGLEPROFILEDEF"                        ) { return IfcRectangleProfileDef; }
    if(s=="IFCRECTANGULARPYRAMID"                         ) { return IfcRectangularPyramid; }
    if(s=="IFCRECTANGULARTRIMMEDSURFACE"                  ) { return IfcRectangularTrimmedSurface; }
    if(s=="IFCREFERENCESVALUEDOCUMENT"                    ) { return IfcReferencesValueDocument; }
    if(s=="IFCREGULARTIMESERIES"                          ) { return IfcRegularTimeSeries; }
    if(s=="IFCREINFORCEMENTBARPROPERTIES"                 ) { return IfcReinforcementBarProperties; }
    if(s=="IFCREINFORCEMENTDEFINITIONPROPERTIES"          ) { return IfcReinforcementDefinitionProperties; }
    if(s=="IFCREINFORCINGBAR"                             ) { return IfcReinforcingBar; }
    if(s=="IFCREINFORCINGELEMENT"                         ) { return IfcReinforcingElement; }
    if(s=="IFCREINFORCINGMESH"                            ) { return IfcReinforcingMesh; }
    if(s=="IFCRELAGGREGATES"                              ) { return IfcRelAggregates; }
    if(s=="IFCRELASSIGNS"                                 ) { return IfcRelAssigns; }
    if(s=="IFCRELASSIGNSTASKS"                            ) { return IfcRelAssignsTasks; }
    if(s=="IFCRELASSIGNSTOACTOR"                          ) { return IfcRelAssignsToActor; }
    if(s=="IFCRELASSIGNSTOCONTROL"                        ) { return IfcRelAssignsToControl; }
    if(s=="IFCRELASSIGNSTOGROUP"                          ) { return IfcRelAssignsToGroup; }
    if(s=="IFCRELASSIGNSTOPROCESS"                        ) { return IfcRelAssignsToProcess; }
    if(s=="IFCRELASSIGNSTOPRODUCT"                        ) { return IfcRelAssignsToProduct; }
    if(s=="IFCRELASSIGNSTOPROJECTORDER"                   ) { return IfcRelAssignsToProjectOrder; }
    if(s=="IFCRELASSIGNSTORESOURCE"                       ) { return IfcRelAssignsToResource; }
    if(s=="IFCRELASSOCIATES"                              ) { return IfcRelAssociates; }
    if(s=="IFCRELASSOCIATESAPPLIEDVALUE"                  ) { return IfcRelAssociatesAppliedValue; }
    if(s=="IFCRELASSOCIATESAPPROVAL"                      ) { return IfcRelAssociatesApproval; }
    if(s=="IFCRELASSOCIATESCLASSIFICATION"                ) { return IfcRelAssociatesClassification; }
    if(s=="IFCRELASSOCIATESCONSTRAINT"                    ) { return IfcRelAssociatesConstraint; }
    if(s=="IFCRELASSOCIATESDOCUMENT"                      ) { return IfcRelAssociatesDocument; }
    if(s=="IFCRELASSOCIATESLIBRARY"                       ) { return IfcRelAssociatesLibrary; }
    if(s=="IFCRELASSOCIATESMATERIAL"                      ) { return IfcRelAssociatesMaterial; }
    if(s=="IFCRELASSOCIATESPROFILEPROPERTIES"             ) { return IfcRelAssociatesProfileProperties; }
    if(s=="IFCRELCONNECTS"                                ) { return IfcRelConnects; }
    if(s=="IFCRELCONNECTSELEMENTS"                        ) { return IfcRelConnectsElements; }
    if(s=="IFCRELCONNECTSPATHELEMENTS"                    ) { return IfcRelConnectsPathElements; }
    if(s=="IFCRELCONNECTSPORTTOELEMENT"                   ) { return IfcRelConnectsPortToElement; }
    if(s=="IFCRELCONNECTSPORTS"                           ) { return IfcRelConnectsPorts; }
    if(s=="IFCRELCONNECTSSTRUCTURALACTIVITY"              ) { return IfcRelConnectsStructuralActivity; }
    if(s=="IFCRELCONNECTSSTRUCTURALELEMENT"               ) { return IfcRelConnectsStructuralElement; }
    if(s=="IFCRELCONNECTSSTRUCTURALMEMBER"                ) { return IfcRelConnectsStructuralMember; }
    if(s=="IFCRELCONNECTSWITHECCENTRICITY"                ) { return IfcRelConnectsWithEccentricity; }
    if(s=="IFCRELCONNECTSWITHREALIZINGELEMENTS"           ) { return IfcRelConnectsWithRealizingElements; }
    if(s=="IFCRELCONTAINEDINSPATIALSTRUCTURE"             ) { return IfcRelContainedInSpatialStructure; }
    if(s=="IFCRELCOVERSBLDGELEMENTS"                      ) { return IfcRelCoversBldgElements; }
    if(s=="IFCRELCOVERSSPACES"                            ) { return IfcRelCoversSpaces; }
    if(s=="IFCRELDECOMPOSES"                              ) { return IfcRelDecomposes; }
    if(s=="IFCRELDEFINES"                                 ) { return IfcRelDefines; }
    if(s=="IFCRELDEFINESBYPROPERTIES"                     ) { return IfcRelDefinesByProperties; }
    if(s=="IFCRELDEFINESBYTYPE"                           ) { return IfcRelDefinesByType; }
    if(s=="IFCRELFILLSELEMENT"                            ) { return IfcRelFillsElement; }
    if(s=="IFCRELFLOWCONTROLELEMENTS"                     ) { return IfcRelFlowControlElements; }
    if(s=="IFCRELINTERACTIONREQUIREMENTS"                 ) { return IfcRelInteractionRequirements; }
    if(s=="IFCRELNESTS"                                   ) { return IfcRelNests; }
    if(s=="IFCRELOCCUPIESSPACES"                          ) { return IfcRelOccupiesSpaces; }
    if(s=="IFCRELOVERRIDESPROPERTIES"                     ) { return IfcRelOverridesProperties; }
    if(s=="IFCRELPROJECTSELEMENT"                         ) { return IfcRelProjectsElement; }
    if(s=="IFCRELREFERENCEDINSPATIALSTRUCTURE"            ) { return IfcRelReferencedInSpatialStructure; }
    if(s=="IFCRELSCHEDULESCOSTITEMS"                      ) { return IfcRelSchedulesCostItems; }
    if(s=="IFCRELSEQUENCE"                                ) { return IfcRelSequence; }
    if(s=="IFCRELSERVICESBUILDINGS"                       ) { return IfcRelServicesBuildings; }
    if(s=="IFCRELSPACEBOUNDARY"                           ) { return IfcRelSpaceBoundary; }
    if(s=="IFCRELVOIDSELEMENT"                            ) { return IfcRelVoidsElement; }
    if(s=="IFCRELATIONSHIP"                               ) { return IfcRelationship; }
    if(s=="IFCRELAXATION"                                 ) { return IfcRelaxation; }
    if(s=="IFCREPRESENTATION"                             ) { return IfcRepresentation; }
    if(s=="IFCREPRESENTATIONCONTEXT"                      ) { return IfcRepresentationContext; }
    if(s=="IFCREPRESENTATIONITEM"                         ) { return IfcRepresentationItem; }
    if(s=="IFCREPRESENTATIONMAP"                          ) { return IfcRepresentationMap; }
    if(s=="IFCRESOURCE"                                   ) { return IfcResource; }
    if(s=="IFCREVOLVEDAREASOLID"                          ) { return IfcRevolvedAreaSolid; }
    if(s=="IFCRIBPLATEPROFILEPROPERTIES"                  ) { return IfcRibPlateProfileProperties; }
    if(s=="IFCRIGHTCIRCULARCONE"                          ) { return IfcRightCircularCone; }
    if(s=="IFCRIGHTCIRCULARCYLINDER"                      ) { return IfcRightCircularCylinder; }
    if(s=="IFCROOF"                                       ) { return IfcRoof; }
    if(s=="IFCROOT"                                       ) { return IfcRoot; }
    if(s=="IFCROUNDEDEDGEFEATURE"                         ) { return IfcRoundedEdgeFeature; }
    if(s=="IFCROUNDEDRECTANGLEPROFILEDEF"                 ) { return IfcRoundedRectangleProfileDef; }
    if(s=="IFCSIUNIT"                                     ) { return IfcSIUnit; }
    if(s=="IFCSANITARYTERMINALTYPE"                       ) { return IfcSanitaryTerminalType; }
    if(s=="IFCSCHEDULETIMECONTROL"                        ) { return IfcScheduleTimeControl; }
    if(s=="IFCSECTIONPROPERTIES"                          ) { return IfcSectionProperties; }
    if(s=="IFCSECTIONREINFORCEMENTPROPERTIES"             ) { return IfcSectionReinforcementProperties; }
    if(s=="IFCSECTIONEDSPINE"                             ) { return IfcSectionedSpine; }
    if(s=="IFCSENSORTYPE"                                 ) { return IfcSensorType; }
    if(s=="IFCSERVICELIFE"                                ) { return IfcServiceLife; }
    if(s=="IFCSERVICELIFEFACTOR"                          ) { return IfcServiceLifeFactor; }
    if(s=="IFCSHAPEASPECT"                                ) { return IfcShapeAspect; }
    if(s=="IFCSHAPEMODEL"                                 ) { return IfcShapeModel; }
    if(s=="IFCSHAPEREPRESENTATION"                        ) { return IfcShapeRepresentation; }
    if(s=="IFCSHELLBASEDSURFACEMODEL"                     ) { return IfcShellBasedSurfaceModel; }
    if(s=="IFCSIMPLEPROPERTY"                             ) { return IfcSimpleProperty; }
    if(s=="IFCSITE"                                       ) { return IfcSite; }
    if(s=="IFCSLAB"                                       ) { return IfcSlab; }
    if(s=="IFCSLABTYPE"                                   ) { return IfcSlabType; }
    if(s=="IFCSLIPPAGECONNECTIONCONDITION"                ) { return IfcSlippageConnectionCondition; }
    if(s=="IFCSOLIDMODEL"                                 ) { return IfcSolidModel; }
    if(s=="IFCSOUNDPROPERTIES"                            ) { return IfcSoundProperties; }
    if(s=="IFCSOUNDVALUE"                                 ) { return IfcSoundValue; }
    if(s=="IFCSPACE"                                      ) { return IfcSpace; }
    if(s=="IFCSPACEHEATERTYPE"                            ) { return IfcSpaceHeaterType; }
    if(s=="IFCSPACEPROGRAM"                               ) { return IfcSpaceProgram; }
    if(s=="IFCSPACETHERMALLOADPROPERTIES"                 ) { return IfcSpaceThermalLoadProperties; }
    if(s=="IFCSPACETYPE"                                  ) { return IfcSpaceType; }
    if(s=="IFCSPATIALSTRUCTUREELEMENT"                    ) { return IfcSpatialStructureElement; }
    if(s=="IFCSPATIALSTRUCTUREELEMENTTYPE"                ) { return IfcSpatialStructureElementType; }
    if(s=="IFCSPHERE"                                     ) { return IfcSphere; }
    if(s=="IFCSTACKTERMINALTYPE"                          ) { return IfcStackTerminalType; }
    if(s=="IFCSTAIR"                                      ) { return IfcStair; }
    if(s=="IFCSTAIRFLIGHT"                                ) { return IfcStairFlight; }
    if(s=="IFCSTAIRFLIGHTTYPE"                            ) { return IfcStairFlightType; }
    if(s=="IFCSTRUCTURALACTION"                           ) { return IfcStructuralAction; }
    if(s=="IFCSTRUCTURALACTIVITY"                         ) { return IfcStructuralActivity; }
    if(s=="IFCSTRUCTURALANALYSISMODEL"                    ) { return IfcStructuralAnalysisModel; }
    if(s=="IFCSTRUCTURALCONNECTION"                       ) { return IfcStructuralConnection; }
    if(s=="IFCSTRUCTURALCONNECTIONCONDITION"              ) { return IfcStructuralConnectionCondition; }
    if(s=="IFCSTRUCTURALCURVECONNECTION"                  ) { return IfcStructuralCurveConnection; }
    if(s=="IFCSTRUCTURALCURVEMEMBER"                      ) { return IfcStructuralCurveMember; }
    if(s=="IFCSTRUCTURALCURVEMEMBERVARYING"               ) { return IfcStructuralCurveMemberVarying; }
    if(s=="IFCSTRUCTURALITEM"                             ) { return IfcStructuralItem; }
    if(s=="IFCSTRUCTURALLINEARACTION"                     ) { return IfcStructuralLinearAction; }
    if(s=="IFCSTRUCTURALLINEARACTIONVARYING"              ) { return IfcStructuralLinearActionVarying; }
    if(s=="IFCSTRUCTURALLOAD"                             ) { return IfcStructuralLoad; }
    if(s=="IFCSTRUCTURALLOADGROUP"                        ) { return IfcStructuralLoadGroup; }
    if(s=="IFCSTRUCTURALLOADLINEARFORCE"                  ) { return IfcStructuralLoadLinearForce; }
    if(s=="IFCSTRUCTURALLOADPLANARFORCE"                  ) { return IfcStructuralLoadPlanarForce; }
    if(s=="IFCSTRUCTURALLOADSINGLEDISPLACEMENT"           ) { return IfcStructuralLoadSingleDisplacement; }
    if(s=="IFCSTRUCTURALLOADSINGLEDISPLACEMENTDISTORTION" ) { return IfcStructuralLoadSingleDisplacementDistortion; }
    if(s=="IFCSTRUCTURALLOADSINGLEFORCE"                  ) { return IfcStructuralLoadSingleForce; }
    if(s=="IFCSTRUCTURALLOADSINGLEFORCEWARPING"           ) { return IfcStructuralLoadSingleForceWarping; }
    if(s=="IFCSTRUCTURALLOADSTATIC"                       ) { return IfcStructuralLoadStatic; }
    if(s=="IFCSTRUCTURALLOADTEMPERATURE"                  ) { return IfcStructuralLoadTemperature; }
    if(s=="IFCSTRUCTURALMEMBER"                           ) { return IfcStructuralMember; }
    if(s=="IFCSTRUCTURALPLANARACTION"                     ) { return IfcStructuralPlanarAction; }
    if(s=="IFCSTRUCTURALPLANARACTIONVARYING"              ) { return IfcStructuralPlanarActionVarying; }
    if(s=="IFCSTRUCTURALPOINTACTION"                      ) { return IfcStructuralPointAction; }
    if(s=="IFCSTRUCTURALPOINTCONNECTION"                  ) { return IfcStructuralPointConnection; }
    if(s=="IFCSTRUCTURALPOINTREACTION"                    ) { return IfcStructuralPointReaction; }
    if(s=="IFCSTRUCTURALPROFILEPROPERTIES"                ) { return IfcStructuralProfileProperties; }
    if(s=="IFCSTRUCTURALREACTION"                         ) { return IfcStructuralReaction; }
    if(s=="IFCSTRUCTURALRESULTGROUP"                      ) { return IfcStructuralResultGroup; }
    if(s=="IFCSTRUCTURALSTEELPROFILEPROPERTIES"           ) { return IfcStructuralSteelProfileProperties; }
    if(s=="IFCSTRUCTURALSURFACECONNECTION"                ) { return IfcStructuralSurfaceConnection; }
    if(s=="IFCSTRUCTURALSURFACEMEMBER"                    ) { return IfcStructuralSurfaceMember; }
    if(s=="IFCSTRUCTURALSURFACEMEMBERVARYING"             ) { return IfcStructuralSurfaceMemberVarying; }
    if(s=="IFCSTRUCTUREDDIMENSIONCALLOUT"                 ) { return IfcStructuredDimensionCallout; }
    if(s=="IFCSTYLEMODEL"                                 ) { return IfcStyleModel; }
    if(s=="IFCSTYLEDITEM"                                 ) { return IfcStyledItem; }
    if(s=="IFCSTYLEDREPRESENTATION"                       ) { return IfcStyledRepresentation; }
    if(s=="IFCSUBCONTRACTRESOURCE"                        ) { return IfcSubContractResource; }
    if(s=="IFCSUBEDGE"                                    ) { return IfcSubedge; }
    if(s=="IFCSURFACE"                                    ) { return IfcSurface; }
    if(s=="IFCSURFACECURVESWEPTAREASOLID"                 ) { return IfcSurfaceCurveSweptAreaSolid; }
    if(s=="IFCSURFACEOFLINEAREXTRUSION"                   ) { return IfcSurfaceOfLinearExtrusion; }
    if(s=="IFCSURFACEOFREVOLUTION"                        ) { return IfcSurfaceOfRevolution; }
    if(s=="IFCSURFACESTYLE"                               ) { return IfcSurfaceStyle; }
    if(s=="IFCSURFACESTYLELIGHTING"                       ) { return IfcSurfaceStyleLighting; }
    if(s=="IFCSURFACESTYLEREFRACTION"                     ) { return IfcSurfaceStyleRefraction; }
    if(s=="IFCSURFACESTYLERENDERING"                      ) { return IfcSurfaceStyleRendering; }
    if(s=="IFCSURFACESTYLESHADING"                        ) { return IfcSurfaceStyleShading; }
    if(s=="IFCSURFACESTYLEWITHTEXTURES"                   ) { return IfcSurfaceStyleWithTextures; }
    if(s=="IFCSURFACETEXTURE"                             ) { return IfcSurfaceTexture; }
    if(s=="IFCSWEPTAREASOLID"                             ) { return IfcSweptAreaSolid; }
    if(s=="IFCSWEPTDISKSOLID"                             ) { return IfcSweptDiskSolid; }
    if(s=="IFCSWEPTSURFACE"                               ) { return IfcSweptSurface; }
    if(s=="IFCSWITCHINGDEVICETYPE"                        ) { return IfcSwitchingDeviceType; }
    if(s=="IFCSYMBOLSTYLE"                                ) { return IfcSymbolStyle; }
    if(s=="IFCSYSTEM"                                     ) { return IfcSystem; }
    if(s=="IFCSYSTEMFURNITUREELEMENTTYPE"                 ) { return IfcSystemFurnitureElementType; }
    if(s=="IFCTSHAPEPROFILEDEF"                           ) { return IfcTShapeProfileDef; }
    if(s=="IFCTABLE"                                      ) { return IfcTable; }
    if(s=="IFCTABLEROW"                                   ) { return IfcTableRow; }
    if(s=="IFCTANKTYPE"                                   ) { return IfcTankType; }
    if(s=="IFCTASK"                                       ) { return IfcTask; }
    if(s=="IFCTELECOMADDRESS"                             ) { return IfcTelecomAddress; }
    if(s=="IFCTENDON"                                     ) { return IfcTendon; }
    if(s=="IFCTENDONANCHOR"                               ) { return IfcTendonAnchor; }
    if(s=="IFCTERMINATORSYMBOL"                           ) { return IfcTerminatorSymbol; }
    if(s=="IFCTEXTLITERAL"                                ) { return IfcTextLiteral; }
    if(s=="IFCTEXTLITERALWITHEXTENT"                      ) { return IfcTextLiteralWithExtent; }
    if(s=="IFCTEXTSTYLE"                                  ) { return IfcTextStyle; }
    if(s=="IFCTEXTSTYLEFONTMODEL"                         ) { return IfcTextStyleFontModel; }
    if(s=="IFCTEXTSTYLEFORDEFINEDFONT"                    ) { return IfcTextStyleForDefinedFont; }
    if(s=="IFCTEXTSTYLETEXTMODEL"                         ) { return IfcTextStyleTextModel; }
    if(s=="IFCTEXTSTYLEWITHBOXCHARACTERISTICS"            ) { return IfcTextStyleWithBoxCharacteristics; }
    if(s=="IFCTEXTURECOORDINATE"                          ) { return IfcTextureCoordinate; }
    if(s=="IFCTEXTURECOORDINATEGENERATOR"                 ) { return IfcTextureCoordinateGenerator; }
    if(s=="IFCTEXTUREMAP"                                 ) { return IfcTextureMap; }
    if(s=="IFCTEXTUREVERTEX"                              ) { return IfcTextureVertex; }
    if(s=="IFCTHERMALMATERIALPROPERTIES"                  ) { return IfcThermalMaterialProperties; }
    if(s=="IFCTIMESERIES"                                 ) { return IfcTimeSeries; }
    if(s=="IFCTIMESERIESREFERENCERELATIONSHIP"            ) { return IfcTimeSeriesReferenceRelationship; }
    if(s=="IFCTIMESERIESSCHEDULE"                         ) { return IfcTimeSeriesSchedule; }
    if(s=="IFCTIMESERIESVALUE"                            ) { return IfcTimeSeriesValue; }
    if(s=="IFCTOPOLOGICALREPRESENTATIONITEM"              ) { return IfcTopologicalRepresentationItem; }
    if(s=="IFCTOPOLOGYREPRESENTATION"                     ) { return IfcTopologyRepresentation; }
    if(s=="IFCTRANSFORMERTYPE"                            ) { return IfcTransformerType; }
    if(s=="IFCTRANSPORTELEMENT"                           ) { return IfcTransportElement; }
    if(s=="IFCTRANSPORTELEMENTTYPE"                       ) { return IfcTransportElementType; }
    if(s=="IFCTRAPEZIUMPROFILEDEF"                        ) { return IfcTrapeziumProfileDef; }
    if(s=="IFCTRIMMEDCURVE"                               ) { return IfcTrimmedCurve; }
    if(s=="IFCTUBEBUNDLETYPE"                             ) { return IfcTubeBundleType; }
    if(s=="IFCTWODIRECTIONREPEATFACTOR"                   ) { return IfcTwoDirectionRepeatFactor; }
    if(s=="IFCTYPEOBJECT"                                 ) { return IfcTypeObject; }
    if(s=="IFCTYPEPRODUCT"                                ) { return IfcTypeProduct; }
    if(s=="IFCUSHAPEPROFILEDEF"                           ) { return IfcUShapeProfileDef; }
    if(s=="IFCUNITASSIGNMENT"                             ) { return IfcUnitAssignment; }
    if(s=="IFCUNITARYEQUIPMENTTYPE"                       ) { return IfcUnitaryEquipmentType; }
    if(s=="IFCVALVETYPE"                                  ) { return IfcValveType; }
    if(s=="IFCVECTOR"                                     ) { return IfcVector; }
    if(s=="IFCVERTEX"                                     ) { return IfcVertex; }
    if(s=="IFCVERTEXBASEDTEXTUREMAP"                      ) { return IfcVertexBasedTextureMap; }
    if(s=="IFCVERTEXLOOP"                                 ) { return IfcVertexLoop; }
    if(s=="IFCVERTEXPOINT"                                ) { return IfcVertexPoint; }
    if(s=="IFCVIBRATIONISOLATORTYPE"                      ) { return IfcVibrationIsolatorType; }
    if(s=="IFCVIRTUALELEMENT"                             ) { return IfcVirtualElement; }
    if(s=="IFCVIRTUALGRIDINTERSECTION"                    ) { return IfcVirtualGridIntersection; }
    if(s=="IFCWALL"                                       ) { return IfcWall; }
    if(s=="IFCWALLSTANDARDCASE"                           ) { return IfcWallStandardCase; }
    if(s=="IFCWALLTYPE"                                   ) { return IfcWallType; }
    if(s=="IFCWASTETERMINALTYPE"                          ) { return IfcWasteTerminalType; }
    if(s=="IFCWATERPROPERTIES"                            ) { return IfcWaterProperties; }
    if(s=="IFCWINDOW"                                     ) { return IfcWindow; }
    if(s=="IFCWINDOWLININGPROPERTIES"                     ) { return IfcWindowLiningProperties; }
    if(s=="IFCWINDOWPANELPROPERTIES"                      ) { return IfcWindowPanelProperties; }
    if(s=="IFCWINDOWSTYLE"                                ) { return IfcWindowStyle; }
    if(s=="IFCWORKCONTROL"                                ) { return IfcWorkControl; }
    if(s=="IFCWORKPLAN"                                   ) { return IfcWorkPlan; }
    if(s=="IFCWORKSCHEDULE"                               ) { return IfcWorkSchedule; }
    if(s=="IFCZSHAPEPROFILEDEF"                           ) { return IfcZShapeProfileDef; }
    if(s=="IFCZONE"                                       ) { return IfcZone; }
    throw;
}
Type::Enum Type::Parent(Enum v){
    if (v < 0 || v >= 758) return (Enum) -1;
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
    return (Enum) -1;
}
std::string IfcActionSourceTypeEnum::ToString(IfcActionSourceTypeEnum v) {
    if ( v < 0 || v >= 27 ) throw;
    const char* names[] = { "DEAD_LOAD_G","COMPLETION_G1","LIVE_LOAD_Q","SNOW_S","WIND_W","PRESTRESSING_P","SETTLEMENT_U","TEMPERATURE_T","EARTHQUAKE_E","FIRE","IMPULSE","IMPACT","TRANSPORT","ERECTION","PROPPING","SYSTEM_IMPERFECTION","SHRINKAGE","CREEP","LACK_OF_FIT","BUOYANCY","ICE","CURRENT","WAVE","RAIN","BRAKES","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcActionSourceTypeEnum::IfcActionSourceTypeEnum IfcActionSourceTypeEnum::FromString(const std::string& s) {
    if(s=="DEAD_LOAD_G"        ) return IfcActionSourceTypeEnum::DEAD_LOAD_G;
    if(s=="COMPLETION_G1"      ) return IfcActionSourceTypeEnum::COMPLETION_G1;
    if(s=="LIVE_LOAD_Q"        ) return IfcActionSourceTypeEnum::LIVE_LOAD_Q;
    if(s=="SNOW_S"             ) return IfcActionSourceTypeEnum::SNOW_S;
    if(s=="WIND_W"             ) return IfcActionSourceTypeEnum::WIND_W;
    if(s=="PRESTRESSING_P"     ) return IfcActionSourceTypeEnum::PRESTRESSING_P;
    if(s=="SETTLEMENT_U"       ) return IfcActionSourceTypeEnum::SETTLEMENT_U;
    if(s=="TEMPERATURE_T"      ) return IfcActionSourceTypeEnum::TEMPERATURE_T;
    if(s=="EARTHQUAKE_E"       ) return IfcActionSourceTypeEnum::EARTHQUAKE_E;
    if(s=="FIRE"               ) return IfcActionSourceTypeEnum::FIRE;
    if(s=="IMPULSE"            ) return IfcActionSourceTypeEnum::IMPULSE;
    if(s=="IMPACT"             ) return IfcActionSourceTypeEnum::IMPACT;
    if(s=="TRANSPORT"          ) return IfcActionSourceTypeEnum::TRANSPORT;
    if(s=="ERECTION"           ) return IfcActionSourceTypeEnum::ERECTION;
    if(s=="PROPPING"           ) return IfcActionSourceTypeEnum::PROPPING;
    if(s=="SYSTEM_IMPERFECTION") return IfcActionSourceTypeEnum::SYSTEM_IMPERFECTION;
    if(s=="SHRINKAGE"          ) return IfcActionSourceTypeEnum::SHRINKAGE;
    if(s=="CREEP"              ) return IfcActionSourceTypeEnum::CREEP;
    if(s=="LACK_OF_FIT"        ) return IfcActionSourceTypeEnum::LACK_OF_FIT;
    if(s=="BUOYANCY"           ) return IfcActionSourceTypeEnum::BUOYANCY;
    if(s=="ICE"                ) return IfcActionSourceTypeEnum::ICE;
    if(s=="CURRENT"            ) return IfcActionSourceTypeEnum::CURRENT;
    if(s=="WAVE"               ) return IfcActionSourceTypeEnum::WAVE;
    if(s=="RAIN"               ) return IfcActionSourceTypeEnum::RAIN;
    if(s=="BRAKES"             ) return IfcActionSourceTypeEnum::BRAKES;
    if(s=="USERDEFINED"        ) return IfcActionSourceTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcActionSourceTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcActionTypeEnum::ToString(IfcActionTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "PERMANENT_G","VARIABLE_Q","EXTRAORDINARY_A","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcActionTypeEnum::IfcActionTypeEnum IfcActionTypeEnum::FromString(const std::string& s) {
    if(s=="PERMANENT_G"    ) return IfcActionTypeEnum::PERMANENT_G;
    if(s=="VARIABLE_Q"     ) return IfcActionTypeEnum::VARIABLE_Q;
    if(s=="EXTRAORDINARY_A") return IfcActionTypeEnum::EXTRAORDINARY_A;
    if(s=="USERDEFINED"    ) return IfcActionTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"     ) return IfcActionTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcActuatorTypeEnum::ToString(IfcActuatorTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "ELECTRICACTUATOR","HANDOPERATEDACTUATOR","HYDRAULICACTUATOR","PNEUMATICACTUATOR","THERMOSTATICACTUATOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcActuatorTypeEnum::IfcActuatorTypeEnum IfcActuatorTypeEnum::FromString(const std::string& s) {
    if(s=="ELECTRICACTUATOR"    ) return IfcActuatorTypeEnum::ELECTRICACTUATOR;
    if(s=="HANDOPERATEDACTUATOR") return IfcActuatorTypeEnum::HANDOPERATEDACTUATOR;
    if(s=="HYDRAULICACTUATOR"   ) return IfcActuatorTypeEnum::HYDRAULICACTUATOR;
    if(s=="PNEUMATICACTUATOR"   ) return IfcActuatorTypeEnum::PNEUMATICACTUATOR;
    if(s=="THERMOSTATICACTUATOR") return IfcActuatorTypeEnum::THERMOSTATICACTUATOR;
    if(s=="USERDEFINED"         ) return IfcActuatorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"          ) return IfcActuatorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcAddressTypeEnum::ToString(IfcAddressTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "OFFICE","SITE","HOME","DISTRIBUTIONPOINT","USERDEFINED" };
    return names[v];
}
IfcAddressTypeEnum::IfcAddressTypeEnum IfcAddressTypeEnum::FromString(const std::string& s) {
    if(s=="OFFICE"           ) return IfcAddressTypeEnum::OFFICE;
    if(s=="SITE"             ) return IfcAddressTypeEnum::SITE;
    if(s=="HOME"             ) return IfcAddressTypeEnum::HOME;
    if(s=="DISTRIBUTIONPOINT") return IfcAddressTypeEnum::DISTRIBUTIONPOINT;
    if(s=="USERDEFINED"      ) return IfcAddressTypeEnum::USERDEFINED;
    throw;
}
std::string IfcAheadOrBehind::ToString(IfcAheadOrBehind v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "AHEAD","BEHIND" };
    return names[v];
}
IfcAheadOrBehind::IfcAheadOrBehind IfcAheadOrBehind::FromString(const std::string& s) {
    if(s=="AHEAD" ) return IfcAheadOrBehind::AHEAD;
    if(s=="BEHIND") return IfcAheadOrBehind::BEHIND;
    throw;
}
std::string IfcAirTerminalBoxTypeEnum::ToString(IfcAirTerminalBoxTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "CONSTANTFLOW","VARIABLEFLOWPRESSUREDEPENDANT","VARIABLEFLOWPRESSUREINDEPENDANT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxTypeEnum IfcAirTerminalBoxTypeEnum::FromString(const std::string& s) {
    if(s=="CONSTANTFLOW"                   ) return IfcAirTerminalBoxTypeEnum::CONSTANTFLOW;
    if(s=="VARIABLEFLOWPRESSUREDEPENDANT"  ) return IfcAirTerminalBoxTypeEnum::VARIABLEFLOWPRESSUREDEPENDANT;
    if(s=="VARIABLEFLOWPRESSUREINDEPENDANT") return IfcAirTerminalBoxTypeEnum::VARIABLEFLOWPRESSUREINDEPENDANT;
    if(s=="USERDEFINED"                    ) return IfcAirTerminalBoxTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                     ) return IfcAirTerminalBoxTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcAirTerminalTypeEnum::ToString(IfcAirTerminalTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "GRILLE","REGISTER","DIFFUSER","EYEBALL","IRIS","LINEARGRILLE","LINEARDIFFUSER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAirTerminalTypeEnum::IfcAirTerminalTypeEnum IfcAirTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="GRILLE"        ) return IfcAirTerminalTypeEnum::GRILLE;
    if(s=="REGISTER"      ) return IfcAirTerminalTypeEnum::REGISTER;
    if(s=="DIFFUSER"      ) return IfcAirTerminalTypeEnum::DIFFUSER;
    if(s=="EYEBALL"       ) return IfcAirTerminalTypeEnum::EYEBALL;
    if(s=="IRIS"          ) return IfcAirTerminalTypeEnum::IRIS;
    if(s=="LINEARGRILLE"  ) return IfcAirTerminalTypeEnum::LINEARGRILLE;
    if(s=="LINEARDIFFUSER") return IfcAirTerminalTypeEnum::LINEARDIFFUSER;
    if(s=="USERDEFINED"   ) return IfcAirTerminalTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"    ) return IfcAirTerminalTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcAirToAirHeatRecoveryTypeEnum::ToString(IfcAirToAirHeatRecoveryTypeEnum v) {
    if ( v < 0 || v >= 11 ) throw;
    const char* names[] = { "FIXEDPLATECOUNTERFLOWEXCHANGER","FIXEDPLATECROSSFLOWEXCHANGER","FIXEDPLATEPARALLELFLOWEXCHANGER","ROTARYWHEEL","RUNAROUNDCOILLOOP","HEATPIPE","TWINTOWERENTHALPYRECOVERYLOOPS","THERMOSIPHONSEALEDTUBEHEATEXCHANGERS","THERMOSIPHONCOILTYPEHEATEXCHANGERS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryTypeEnum IfcAirToAirHeatRecoveryTypeEnum::FromString(const std::string& s) {
    if(s=="FIXEDPLATECOUNTERFLOWEXCHANGER"      ) return IfcAirToAirHeatRecoveryTypeEnum::FIXEDPLATECOUNTERFLOWEXCHANGER;
    if(s=="FIXEDPLATECROSSFLOWEXCHANGER"        ) return IfcAirToAirHeatRecoveryTypeEnum::FIXEDPLATECROSSFLOWEXCHANGER;
    if(s=="FIXEDPLATEPARALLELFLOWEXCHANGER"     ) return IfcAirToAirHeatRecoveryTypeEnum::FIXEDPLATEPARALLELFLOWEXCHANGER;
    if(s=="ROTARYWHEEL"                         ) return IfcAirToAirHeatRecoveryTypeEnum::ROTARYWHEEL;
    if(s=="RUNAROUNDCOILLOOP"                   ) return IfcAirToAirHeatRecoveryTypeEnum::RUNAROUNDCOILLOOP;
    if(s=="HEATPIPE"                            ) return IfcAirToAirHeatRecoveryTypeEnum::HEATPIPE;
    if(s=="TWINTOWERENTHALPYRECOVERYLOOPS"      ) return IfcAirToAirHeatRecoveryTypeEnum::TWINTOWERENTHALPYRECOVERYLOOPS;
    if(s=="THERMOSIPHONSEALEDTUBEHEATEXCHANGERS") return IfcAirToAirHeatRecoveryTypeEnum::THERMOSIPHONSEALEDTUBEHEATEXCHANGERS;
    if(s=="THERMOSIPHONCOILTYPEHEATEXCHANGERS"  ) return IfcAirToAirHeatRecoveryTypeEnum::THERMOSIPHONCOILTYPEHEATEXCHANGERS;
    if(s=="USERDEFINED"                         ) return IfcAirToAirHeatRecoveryTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                          ) return IfcAirToAirHeatRecoveryTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcAlarmTypeEnum::ToString(IfcAlarmTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "BELL","BREAKGLASSBUTTON","LIGHT","MANUALPULLBOX","SIREN","WHISTLE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAlarmTypeEnum::IfcAlarmTypeEnum IfcAlarmTypeEnum::FromString(const std::string& s) {
    if(s=="BELL"            ) return IfcAlarmTypeEnum::BELL;
    if(s=="BREAKGLASSBUTTON") return IfcAlarmTypeEnum::BREAKGLASSBUTTON;
    if(s=="LIGHT"           ) return IfcAlarmTypeEnum::LIGHT;
    if(s=="MANUALPULLBOX"   ) return IfcAlarmTypeEnum::MANUALPULLBOX;
    if(s=="SIREN"           ) return IfcAlarmTypeEnum::SIREN;
    if(s=="WHISTLE"         ) return IfcAlarmTypeEnum::WHISTLE;
    if(s=="USERDEFINED"     ) return IfcAlarmTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcAlarmTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcAnalysisModelTypeEnum::ToString(IfcAnalysisModelTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "IN_PLANE_LOADING_2D","OUT_PLANE_LOADING_2D","LOADING_3D","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAnalysisModelTypeEnum::IfcAnalysisModelTypeEnum IfcAnalysisModelTypeEnum::FromString(const std::string& s) {
    if(s=="IN_PLANE_LOADING_2D" ) return IfcAnalysisModelTypeEnum::IN_PLANE_LOADING_2D;
    if(s=="OUT_PLANE_LOADING_2D") return IfcAnalysisModelTypeEnum::OUT_PLANE_LOADING_2D;
    if(s=="LOADING_3D"          ) return IfcAnalysisModelTypeEnum::LOADING_3D;
    if(s=="USERDEFINED"         ) return IfcAnalysisModelTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"          ) return IfcAnalysisModelTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcAnalysisTheoryTypeEnum::ToString(IfcAnalysisTheoryTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "FIRST_ORDER_THEORY","SECOND_ORDER_THEORY","THIRD_ORDER_THEORY","FULL_NONLINEAR_THEORY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryTypeEnum IfcAnalysisTheoryTypeEnum::FromString(const std::string& s) {
    if(s=="FIRST_ORDER_THEORY"   ) return IfcAnalysisTheoryTypeEnum::FIRST_ORDER_THEORY;
    if(s=="SECOND_ORDER_THEORY"  ) return IfcAnalysisTheoryTypeEnum::SECOND_ORDER_THEORY;
    if(s=="THIRD_ORDER_THEORY"   ) return IfcAnalysisTheoryTypeEnum::THIRD_ORDER_THEORY;
    if(s=="FULL_NONLINEAR_THEORY") return IfcAnalysisTheoryTypeEnum::FULL_NONLINEAR_THEORY;
    if(s=="USERDEFINED"          ) return IfcAnalysisTheoryTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"           ) return IfcAnalysisTheoryTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcArithmeticOperatorEnum::ToString(IfcArithmeticOperatorEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "ADD","DIVIDE","MULTIPLY","SUBTRACT" };
    return names[v];
}
IfcArithmeticOperatorEnum::IfcArithmeticOperatorEnum IfcArithmeticOperatorEnum::FromString(const std::string& s) {
    if(s=="ADD"     ) return IfcArithmeticOperatorEnum::ADD;
    if(s=="DIVIDE"  ) return IfcArithmeticOperatorEnum::DIVIDE;
    if(s=="MULTIPLY") return IfcArithmeticOperatorEnum::MULTIPLY;
    if(s=="SUBTRACT") return IfcArithmeticOperatorEnum::SUBTRACT;
    throw;
}
std::string IfcAssemblyPlaceEnum::ToString(IfcAssemblyPlaceEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "SITE","FACTORY","NOTDEFINED" };
    return names[v];
}
IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum IfcAssemblyPlaceEnum::FromString(const std::string& s) {
    if(s=="SITE"      ) return IfcAssemblyPlaceEnum::SITE;
    if(s=="FACTORY"   ) return IfcAssemblyPlaceEnum::FACTORY;
    if(s=="NOTDEFINED") return IfcAssemblyPlaceEnum::NOTDEFINED;
    throw;
}
std::string IfcBSplineCurveForm::ToString(IfcBSplineCurveForm v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "POLYLINE_FORM","CIRCULAR_ARC","ELLIPTIC_ARC","PARABOLIC_ARC","HYPERBOLIC_ARC","UNSPECIFIED" };
    return names[v];
}
IfcBSplineCurveForm::IfcBSplineCurveForm IfcBSplineCurveForm::FromString(const std::string& s) {
    if(s=="POLYLINE_FORM" ) return IfcBSplineCurveForm::POLYLINE_FORM;
    if(s=="CIRCULAR_ARC"  ) return IfcBSplineCurveForm::CIRCULAR_ARC;
    if(s=="ELLIPTIC_ARC"  ) return IfcBSplineCurveForm::ELLIPTIC_ARC;
    if(s=="PARABOLIC_ARC" ) return IfcBSplineCurveForm::PARABOLIC_ARC;
    if(s=="HYPERBOLIC_ARC") return IfcBSplineCurveForm::HYPERBOLIC_ARC;
    if(s=="UNSPECIFIED"   ) return IfcBSplineCurveForm::UNSPECIFIED;
    throw;
}
std::string IfcBeamTypeEnum::ToString(IfcBeamTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "BEAM","JOIST","LINTEL","T_BEAM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcBeamTypeEnum::IfcBeamTypeEnum IfcBeamTypeEnum::FromString(const std::string& s) {
    if(s=="BEAM"       ) return IfcBeamTypeEnum::BEAM;
    if(s=="JOIST"      ) return IfcBeamTypeEnum::JOIST;
    if(s=="LINTEL"     ) return IfcBeamTypeEnum::LINTEL;
    if(s=="T_BEAM"     ) return IfcBeamTypeEnum::T_BEAM;
    if(s=="USERDEFINED") return IfcBeamTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcBeamTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcBenchmarkEnum::ToString(IfcBenchmarkEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "GREATERTHAN","GREATERTHANOREQUALTO","LESSTHAN","LESSTHANOREQUALTO","EQUALTO","NOTEQUALTO" };
    return names[v];
}
IfcBenchmarkEnum::IfcBenchmarkEnum IfcBenchmarkEnum::FromString(const std::string& s) {
    if(s=="GREATERTHAN"         ) return IfcBenchmarkEnum::GREATERTHAN;
    if(s=="GREATERTHANOREQUALTO") return IfcBenchmarkEnum::GREATERTHANOREQUALTO;
    if(s=="LESSTHAN"            ) return IfcBenchmarkEnum::LESSTHAN;
    if(s=="LESSTHANOREQUALTO"   ) return IfcBenchmarkEnum::LESSTHANOREQUALTO;
    if(s=="EQUALTO"             ) return IfcBenchmarkEnum::EQUALTO;
    if(s=="NOTEQUALTO"          ) return IfcBenchmarkEnum::NOTEQUALTO;
    throw;
}
std::string IfcBoilerTypeEnum::ToString(IfcBoilerTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "WATER","STEAM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcBoilerTypeEnum::IfcBoilerTypeEnum IfcBoilerTypeEnum::FromString(const std::string& s) {
    if(s=="WATER"      ) return IfcBoilerTypeEnum::WATER;
    if(s=="STEAM"      ) return IfcBoilerTypeEnum::STEAM;
    if(s=="USERDEFINED") return IfcBoilerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcBoilerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcBooleanOperator::ToString(IfcBooleanOperator v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "UNION","INTERSECTION","DIFFERENCE" };
    return names[v];
}
IfcBooleanOperator::IfcBooleanOperator IfcBooleanOperator::FromString(const std::string& s) {
    if(s=="UNION"       ) return IfcBooleanOperator::UNION;
    if(s=="INTERSECTION") return IfcBooleanOperator::INTERSECTION;
    if(s=="DIFFERENCE"  ) return IfcBooleanOperator::DIFFERENCE;
    throw;
}
std::string IfcBuildingElementProxyTypeEnum::ToString(IfcBuildingElementProxyTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyTypeEnum IfcBuildingElementProxyTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcBuildingElementProxyTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcBuildingElementProxyTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCableCarrierFittingTypeEnum::ToString(IfcCableCarrierFittingTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "BEND","CROSS","REDUCER","TEE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingTypeEnum IfcCableCarrierFittingTypeEnum::FromString(const std::string& s) {
    if(s=="BEND"       ) return IfcCableCarrierFittingTypeEnum::BEND;
    if(s=="CROSS"      ) return IfcCableCarrierFittingTypeEnum::CROSS;
    if(s=="REDUCER"    ) return IfcCableCarrierFittingTypeEnum::REDUCER;
    if(s=="TEE"        ) return IfcCableCarrierFittingTypeEnum::TEE;
    if(s=="USERDEFINED") return IfcCableCarrierFittingTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcCableCarrierFittingTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCableCarrierSegmentTypeEnum::ToString(IfcCableCarrierSegmentTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "CABLELADDERSEGMENT","CABLETRAYSEGMENT","CABLETRUNKINGSEGMENT","CONDUITSEGMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentTypeEnum IfcCableCarrierSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="CABLELADDERSEGMENT"  ) return IfcCableCarrierSegmentTypeEnum::CABLELADDERSEGMENT;
    if(s=="CABLETRAYSEGMENT"    ) return IfcCableCarrierSegmentTypeEnum::CABLETRAYSEGMENT;
    if(s=="CABLETRUNKINGSEGMENT") return IfcCableCarrierSegmentTypeEnum::CABLETRUNKINGSEGMENT;
    if(s=="CONDUITSEGMENT"      ) return IfcCableCarrierSegmentTypeEnum::CONDUITSEGMENT;
    if(s=="USERDEFINED"         ) return IfcCableCarrierSegmentTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"          ) return IfcCableCarrierSegmentTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCableSegmentTypeEnum::ToString(IfcCableSegmentTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "CABLESEGMENT","CONDUCTORSEGMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCableSegmentTypeEnum::IfcCableSegmentTypeEnum IfcCableSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="CABLESEGMENT"    ) return IfcCableSegmentTypeEnum::CABLESEGMENT;
    if(s=="CONDUCTORSEGMENT") return IfcCableSegmentTypeEnum::CONDUCTORSEGMENT;
    if(s=="USERDEFINED"     ) return IfcCableSegmentTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcCableSegmentTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcChangeActionEnum::ToString(IfcChangeActionEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "NOCHANGE","MODIFIED","ADDED","DELETED","MODIFIEDADDED","MODIFIEDDELETED" };
    return names[v];
}
IfcChangeActionEnum::IfcChangeActionEnum IfcChangeActionEnum::FromString(const std::string& s) {
    if(s=="NOCHANGE"       ) return IfcChangeActionEnum::NOCHANGE;
    if(s=="MODIFIED"       ) return IfcChangeActionEnum::MODIFIED;
    if(s=="ADDED"          ) return IfcChangeActionEnum::ADDED;
    if(s=="DELETED"        ) return IfcChangeActionEnum::DELETED;
    if(s=="MODIFIEDADDED"  ) return IfcChangeActionEnum::MODIFIEDADDED;
    if(s=="MODIFIEDDELETED") return IfcChangeActionEnum::MODIFIEDDELETED;
    throw;
}
std::string IfcChillerTypeEnum::ToString(IfcChillerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "AIRCOOLED","WATERCOOLED","HEATRECOVERY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcChillerTypeEnum::IfcChillerTypeEnum IfcChillerTypeEnum::FromString(const std::string& s) {
    if(s=="AIRCOOLED"   ) return IfcChillerTypeEnum::AIRCOOLED;
    if(s=="WATERCOOLED" ) return IfcChillerTypeEnum::WATERCOOLED;
    if(s=="HEATRECOVERY") return IfcChillerTypeEnum::HEATRECOVERY;
    if(s=="USERDEFINED" ) return IfcChillerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"  ) return IfcChillerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCoilTypeEnum::ToString(IfcCoilTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "DXCOOLINGCOIL","WATERCOOLINGCOIL","STEAMHEATINGCOIL","WATERHEATINGCOIL","ELECTRICHEATINGCOIL","GASHEATINGCOIL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCoilTypeEnum::IfcCoilTypeEnum IfcCoilTypeEnum::FromString(const std::string& s) {
    if(s=="DXCOOLINGCOIL"      ) return IfcCoilTypeEnum::DXCOOLINGCOIL;
    if(s=="WATERCOOLINGCOIL"   ) return IfcCoilTypeEnum::WATERCOOLINGCOIL;
    if(s=="STEAMHEATINGCOIL"   ) return IfcCoilTypeEnum::STEAMHEATINGCOIL;
    if(s=="WATERHEATINGCOIL"   ) return IfcCoilTypeEnum::WATERHEATINGCOIL;
    if(s=="ELECTRICHEATINGCOIL") return IfcCoilTypeEnum::ELECTRICHEATINGCOIL;
    if(s=="GASHEATINGCOIL"     ) return IfcCoilTypeEnum::GASHEATINGCOIL;
    if(s=="USERDEFINED"        ) return IfcCoilTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcCoilTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcColumnTypeEnum::ToString(IfcColumnTypeEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "COLUMN","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcColumnTypeEnum::IfcColumnTypeEnum IfcColumnTypeEnum::FromString(const std::string& s) {
    if(s=="COLUMN"     ) return IfcColumnTypeEnum::COLUMN;
    if(s=="USERDEFINED") return IfcColumnTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcColumnTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCompressorTypeEnum::ToString(IfcCompressorTypeEnum v) {
    if ( v < 0 || v >= 17 ) throw;
    const char* names[] = { "DYNAMIC","RECIPROCATING","ROTARY","SCROLL","TROCHOIDAL","SINGLESTAGE","BOOSTER","OPENTYPE","HERMETIC","SEMIHERMETIC","WELDEDSHELLHERMETIC","ROLLINGPISTON","ROTARYVANE","SINGLESCREW","TWINSCREW","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCompressorTypeEnum::IfcCompressorTypeEnum IfcCompressorTypeEnum::FromString(const std::string& s) {
    if(s=="DYNAMIC"            ) return IfcCompressorTypeEnum::DYNAMIC;
    if(s=="RECIPROCATING"      ) return IfcCompressorTypeEnum::RECIPROCATING;
    if(s=="ROTARY"             ) return IfcCompressorTypeEnum::ROTARY;
    if(s=="SCROLL"             ) return IfcCompressorTypeEnum::SCROLL;
    if(s=="TROCHOIDAL"         ) return IfcCompressorTypeEnum::TROCHOIDAL;
    if(s=="SINGLESTAGE"        ) return IfcCompressorTypeEnum::SINGLESTAGE;
    if(s=="BOOSTER"            ) return IfcCompressorTypeEnum::BOOSTER;
    if(s=="OPENTYPE"           ) return IfcCompressorTypeEnum::OPENTYPE;
    if(s=="HERMETIC"           ) return IfcCompressorTypeEnum::HERMETIC;
    if(s=="SEMIHERMETIC"       ) return IfcCompressorTypeEnum::SEMIHERMETIC;
    if(s=="WELDEDSHELLHERMETIC") return IfcCompressorTypeEnum::WELDEDSHELLHERMETIC;
    if(s=="ROLLINGPISTON"      ) return IfcCompressorTypeEnum::ROLLINGPISTON;
    if(s=="ROTARYVANE"         ) return IfcCompressorTypeEnum::ROTARYVANE;
    if(s=="SINGLESCREW"        ) return IfcCompressorTypeEnum::SINGLESCREW;
    if(s=="TWINSCREW"          ) return IfcCompressorTypeEnum::TWINSCREW;
    if(s=="USERDEFINED"        ) return IfcCompressorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcCompressorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCondenserTypeEnum::ToString(IfcCondenserTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "WATERCOOLEDSHELLTUBE","WATERCOOLEDSHELLCOIL","WATERCOOLEDTUBEINTUBE","WATERCOOLEDBRAZEDPLATE","AIRCOOLED","EVAPORATIVECOOLED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCondenserTypeEnum::IfcCondenserTypeEnum IfcCondenserTypeEnum::FromString(const std::string& s) {
    if(s=="WATERCOOLEDSHELLTUBE"  ) return IfcCondenserTypeEnum::WATERCOOLEDSHELLTUBE;
    if(s=="WATERCOOLEDSHELLCOIL"  ) return IfcCondenserTypeEnum::WATERCOOLEDSHELLCOIL;
    if(s=="WATERCOOLEDTUBEINTUBE" ) return IfcCondenserTypeEnum::WATERCOOLEDTUBEINTUBE;
    if(s=="WATERCOOLEDBRAZEDPLATE") return IfcCondenserTypeEnum::WATERCOOLEDBRAZEDPLATE;
    if(s=="AIRCOOLED"             ) return IfcCondenserTypeEnum::AIRCOOLED;
    if(s=="EVAPORATIVECOOLED"     ) return IfcCondenserTypeEnum::EVAPORATIVECOOLED;
    if(s=="USERDEFINED"           ) return IfcCondenserTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"            ) return IfcCondenserTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcConnectionTypeEnum::ToString(IfcConnectionTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "ATPATH","ATSTART","ATEND","NOTDEFINED" };
    return names[v];
}
IfcConnectionTypeEnum::IfcConnectionTypeEnum IfcConnectionTypeEnum::FromString(const std::string& s) {
    if(s=="ATPATH"    ) return IfcConnectionTypeEnum::ATPATH;
    if(s=="ATSTART"   ) return IfcConnectionTypeEnum::ATSTART;
    if(s=="ATEND"     ) return IfcConnectionTypeEnum::ATEND;
    if(s=="NOTDEFINED") return IfcConnectionTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcConstraintEnum::ToString(IfcConstraintEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "HARD","SOFT","ADVISORY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcConstraintEnum::IfcConstraintEnum IfcConstraintEnum::FromString(const std::string& s) {
    if(s=="HARD"       ) return IfcConstraintEnum::HARD;
    if(s=="SOFT"       ) return IfcConstraintEnum::SOFT;
    if(s=="ADVISORY"   ) return IfcConstraintEnum::ADVISORY;
    if(s=="USERDEFINED") return IfcConstraintEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcConstraintEnum::NOTDEFINED;
    throw;
}
std::string IfcControllerTypeEnum::ToString(IfcControllerTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "FLOATING","PROPORTIONAL","PROPORTIONALINTEGRAL","PROPORTIONALINTEGRALDERIVATIVE","TIMEDTWOPOSITION","TWOPOSITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcControllerTypeEnum::IfcControllerTypeEnum IfcControllerTypeEnum::FromString(const std::string& s) {
    if(s=="FLOATING"                      ) return IfcControllerTypeEnum::FLOATING;
    if(s=="PROPORTIONAL"                  ) return IfcControllerTypeEnum::PROPORTIONAL;
    if(s=="PROPORTIONALINTEGRAL"          ) return IfcControllerTypeEnum::PROPORTIONALINTEGRAL;
    if(s=="PROPORTIONALINTEGRALDERIVATIVE") return IfcControllerTypeEnum::PROPORTIONALINTEGRALDERIVATIVE;
    if(s=="TIMEDTWOPOSITION"              ) return IfcControllerTypeEnum::TIMEDTWOPOSITION;
    if(s=="TWOPOSITION"                   ) return IfcControllerTypeEnum::TWOPOSITION;
    if(s=="USERDEFINED"                   ) return IfcControllerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                    ) return IfcControllerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCooledBeamTypeEnum::ToString(IfcCooledBeamTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "ACTIVE","PASSIVE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCooledBeamTypeEnum::IfcCooledBeamTypeEnum IfcCooledBeamTypeEnum::FromString(const std::string& s) {
    if(s=="ACTIVE"     ) return IfcCooledBeamTypeEnum::ACTIVE;
    if(s=="PASSIVE"    ) return IfcCooledBeamTypeEnum::PASSIVE;
    if(s=="USERDEFINED") return IfcCooledBeamTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcCooledBeamTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCoolingTowerTypeEnum::ToString(IfcCoolingTowerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "NATURALDRAFT","MECHANICALINDUCEDDRAFT","MECHANICALFORCEDDRAFT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCoolingTowerTypeEnum::IfcCoolingTowerTypeEnum IfcCoolingTowerTypeEnum::FromString(const std::string& s) {
    if(s=="NATURALDRAFT"          ) return IfcCoolingTowerTypeEnum::NATURALDRAFT;
    if(s=="MECHANICALINDUCEDDRAFT") return IfcCoolingTowerTypeEnum::MECHANICALINDUCEDDRAFT;
    if(s=="MECHANICALFORCEDDRAFT" ) return IfcCoolingTowerTypeEnum::MECHANICALFORCEDDRAFT;
    if(s=="USERDEFINED"           ) return IfcCoolingTowerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"            ) return IfcCoolingTowerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCostScheduleTypeEnum::ToString(IfcCostScheduleTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "BUDGET","COSTPLAN","ESTIMATE","TENDER","PRICEDBILLOFQUANTITIES","UNPRICEDBILLOFQUANTITIES","SCHEDULEOFRATES","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCostScheduleTypeEnum::IfcCostScheduleTypeEnum IfcCostScheduleTypeEnum::FromString(const std::string& s) {
    if(s=="BUDGET"                  ) return IfcCostScheduleTypeEnum::BUDGET;
    if(s=="COSTPLAN"                ) return IfcCostScheduleTypeEnum::COSTPLAN;
    if(s=="ESTIMATE"                ) return IfcCostScheduleTypeEnum::ESTIMATE;
    if(s=="TENDER"                  ) return IfcCostScheduleTypeEnum::TENDER;
    if(s=="PRICEDBILLOFQUANTITIES"  ) return IfcCostScheduleTypeEnum::PRICEDBILLOFQUANTITIES;
    if(s=="UNPRICEDBILLOFQUANTITIES") return IfcCostScheduleTypeEnum::UNPRICEDBILLOFQUANTITIES;
    if(s=="SCHEDULEOFRATES"         ) return IfcCostScheduleTypeEnum::SCHEDULEOFRATES;
    if(s=="USERDEFINED"             ) return IfcCostScheduleTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"              ) return IfcCostScheduleTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCoveringTypeEnum::ToString(IfcCoveringTypeEnum v) {
    if ( v < 0 || v >= 10 ) throw;
    const char* names[] = { "CEILING","FLOORING","CLADDING","ROOFING","INSULATION","MEMBRANE","SLEEVING","WRAPPING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCoveringTypeEnum::IfcCoveringTypeEnum IfcCoveringTypeEnum::FromString(const std::string& s) {
    if(s=="CEILING"    ) return IfcCoveringTypeEnum::CEILING;
    if(s=="FLOORING"   ) return IfcCoveringTypeEnum::FLOORING;
    if(s=="CLADDING"   ) return IfcCoveringTypeEnum::CLADDING;
    if(s=="ROOFING"    ) return IfcCoveringTypeEnum::ROOFING;
    if(s=="INSULATION" ) return IfcCoveringTypeEnum::INSULATION;
    if(s=="MEMBRANE"   ) return IfcCoveringTypeEnum::MEMBRANE;
    if(s=="SLEEVING"   ) return IfcCoveringTypeEnum::SLEEVING;
    if(s=="WRAPPING"   ) return IfcCoveringTypeEnum::WRAPPING;
    if(s=="USERDEFINED") return IfcCoveringTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcCoveringTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcCurrencyEnum::ToString(IfcCurrencyEnum v) {
    if ( v < 0 || v >= 83 ) throw;
    const char* names[] = { "AED","AES","ATS","AUD","BBD","BEG","BGL","BHD","BMD","BND","BRL","BSD","BWP","BZD","CAD","CBD","CHF","CLP","CNY","CYS","CZK","DDP","DEM","DKK","EGL","EST","EUR","FAK","FIM","FJD","FKP","FRF","GBP","GIP","GMD","GRX","HKD","HUF","ICK","IDR","ILS","INR","IRP","ITL","JMD","JOD","JPY","KES","KRW","KWD","KYD","LKR","LUF","MTL","MUR","MXN","MYR","NLG","NZD","OMR","PGK","PHP","PKR","PLN","PTN","QAR","RUR","SAR","SCR","SEK","SGD","SKP","THB","TRL","TTD","TWD","USD","VEB","VND","XEU","ZAR","ZWD","NOK" };
    return names[v];
}
IfcCurrencyEnum::IfcCurrencyEnum IfcCurrencyEnum::FromString(const std::string& s) {
    if(s=="AED") return IfcCurrencyEnum::AED;
    if(s=="AES") return IfcCurrencyEnum::AES;
    if(s=="ATS") return IfcCurrencyEnum::ATS;
    if(s=="AUD") return IfcCurrencyEnum::AUD;
    if(s=="BBD") return IfcCurrencyEnum::BBD;
    if(s=="BEG") return IfcCurrencyEnum::BEG;
    if(s=="BGL") return IfcCurrencyEnum::BGL;
    if(s=="BHD") return IfcCurrencyEnum::BHD;
    if(s=="BMD") return IfcCurrencyEnum::BMD;
    if(s=="BND") return IfcCurrencyEnum::BND;
    if(s=="BRL") return IfcCurrencyEnum::BRL;
    if(s=="BSD") return IfcCurrencyEnum::BSD;
    if(s=="BWP") return IfcCurrencyEnum::BWP;
    if(s=="BZD") return IfcCurrencyEnum::BZD;
    if(s=="CAD") return IfcCurrencyEnum::CAD;
    if(s=="CBD") return IfcCurrencyEnum::CBD;
    if(s=="CHF") return IfcCurrencyEnum::CHF;
    if(s=="CLP") return IfcCurrencyEnum::CLP;
    if(s=="CNY") return IfcCurrencyEnum::CNY;
    if(s=="CYS") return IfcCurrencyEnum::CYS;
    if(s=="CZK") return IfcCurrencyEnum::CZK;
    if(s=="DDP") return IfcCurrencyEnum::DDP;
    if(s=="DEM") return IfcCurrencyEnum::DEM;
    if(s=="DKK") return IfcCurrencyEnum::DKK;
    if(s=="EGL") return IfcCurrencyEnum::EGL;
    if(s=="EST") return IfcCurrencyEnum::EST;
    if(s=="EUR") return IfcCurrencyEnum::EUR;
    if(s=="FAK") return IfcCurrencyEnum::FAK;
    if(s=="FIM") return IfcCurrencyEnum::FIM;
    if(s=="FJD") return IfcCurrencyEnum::FJD;
    if(s=="FKP") return IfcCurrencyEnum::FKP;
    if(s=="FRF") return IfcCurrencyEnum::FRF;
    if(s=="GBP") return IfcCurrencyEnum::GBP;
    if(s=="GIP") return IfcCurrencyEnum::GIP;
    if(s=="GMD") return IfcCurrencyEnum::GMD;
    if(s=="GRX") return IfcCurrencyEnum::GRX;
    if(s=="HKD") return IfcCurrencyEnum::HKD;
    if(s=="HUF") return IfcCurrencyEnum::HUF;
    if(s=="ICK") return IfcCurrencyEnum::ICK;
    if(s=="IDR") return IfcCurrencyEnum::IDR;
    if(s=="ILS") return IfcCurrencyEnum::ILS;
    if(s=="INR") return IfcCurrencyEnum::INR;
    if(s=="IRP") return IfcCurrencyEnum::IRP;
    if(s=="ITL") return IfcCurrencyEnum::ITL;
    if(s=="JMD") return IfcCurrencyEnum::JMD;
    if(s=="JOD") return IfcCurrencyEnum::JOD;
    if(s=="JPY") return IfcCurrencyEnum::JPY;
    if(s=="KES") return IfcCurrencyEnum::KES;
    if(s=="KRW") return IfcCurrencyEnum::KRW;
    if(s=="KWD") return IfcCurrencyEnum::KWD;
    if(s=="KYD") return IfcCurrencyEnum::KYD;
    if(s=="LKR") return IfcCurrencyEnum::LKR;
    if(s=="LUF") return IfcCurrencyEnum::LUF;
    if(s=="MTL") return IfcCurrencyEnum::MTL;
    if(s=="MUR") return IfcCurrencyEnum::MUR;
    if(s=="MXN") return IfcCurrencyEnum::MXN;
    if(s=="MYR") return IfcCurrencyEnum::MYR;
    if(s=="NLG") return IfcCurrencyEnum::NLG;
    if(s=="NZD") return IfcCurrencyEnum::NZD;
    if(s=="OMR") return IfcCurrencyEnum::OMR;
    if(s=="PGK") return IfcCurrencyEnum::PGK;
    if(s=="PHP") return IfcCurrencyEnum::PHP;
    if(s=="PKR") return IfcCurrencyEnum::PKR;
    if(s=="PLN") return IfcCurrencyEnum::PLN;
    if(s=="PTN") return IfcCurrencyEnum::PTN;
    if(s=="QAR") return IfcCurrencyEnum::QAR;
    if(s=="RUR") return IfcCurrencyEnum::RUR;
    if(s=="SAR") return IfcCurrencyEnum::SAR;
    if(s=="SCR") return IfcCurrencyEnum::SCR;
    if(s=="SEK") return IfcCurrencyEnum::SEK;
    if(s=="SGD") return IfcCurrencyEnum::SGD;
    if(s=="SKP") return IfcCurrencyEnum::SKP;
    if(s=="THB") return IfcCurrencyEnum::THB;
    if(s=="TRL") return IfcCurrencyEnum::TRL;
    if(s=="TTD") return IfcCurrencyEnum::TTD;
    if(s=="TWD") return IfcCurrencyEnum::TWD;
    if(s=="USD") return IfcCurrencyEnum::USD;
    if(s=="VEB") return IfcCurrencyEnum::VEB;
    if(s=="VND") return IfcCurrencyEnum::VND;
    if(s=="XEU") return IfcCurrencyEnum::XEU;
    if(s=="ZAR") return IfcCurrencyEnum::ZAR;
    if(s=="ZWD") return IfcCurrencyEnum::ZWD;
    if(s=="NOK") return IfcCurrencyEnum::NOK;
    throw;
}
std::string IfcCurtainWallTypeEnum::ToString(IfcCurtainWallTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcCurtainWallTypeEnum::IfcCurtainWallTypeEnum IfcCurtainWallTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcCurtainWallTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcCurtainWallTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcDamperTypeEnum::ToString(IfcDamperTypeEnum v) {
    if ( v < 0 || v >= 13 ) throw;
    const char* names[] = { "CONTROLDAMPER","FIREDAMPER","SMOKEDAMPER","FIRESMOKEDAMPER","BACKDRAFTDAMPER","RELIEFDAMPER","BLASTDAMPER","GRAVITYDAMPER","GRAVITYRELIEFDAMPER","BALANCINGDAMPER","FUMEHOODEXHAUST","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDamperTypeEnum::IfcDamperTypeEnum IfcDamperTypeEnum::FromString(const std::string& s) {
    if(s=="CONTROLDAMPER"      ) return IfcDamperTypeEnum::CONTROLDAMPER;
    if(s=="FIREDAMPER"         ) return IfcDamperTypeEnum::FIREDAMPER;
    if(s=="SMOKEDAMPER"        ) return IfcDamperTypeEnum::SMOKEDAMPER;
    if(s=="FIRESMOKEDAMPER"    ) return IfcDamperTypeEnum::FIRESMOKEDAMPER;
    if(s=="BACKDRAFTDAMPER"    ) return IfcDamperTypeEnum::BACKDRAFTDAMPER;
    if(s=="RELIEFDAMPER"       ) return IfcDamperTypeEnum::RELIEFDAMPER;
    if(s=="BLASTDAMPER"        ) return IfcDamperTypeEnum::BLASTDAMPER;
    if(s=="GRAVITYDAMPER"      ) return IfcDamperTypeEnum::GRAVITYDAMPER;
    if(s=="GRAVITYRELIEFDAMPER") return IfcDamperTypeEnum::GRAVITYRELIEFDAMPER;
    if(s=="BALANCINGDAMPER"    ) return IfcDamperTypeEnum::BALANCINGDAMPER;
    if(s=="FUMEHOODEXHAUST"    ) return IfcDamperTypeEnum::FUMEHOODEXHAUST;
    if(s=="USERDEFINED"        ) return IfcDamperTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcDamperTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcDataOriginEnum::ToString(IfcDataOriginEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "MEASURED","PREDICTED","SIMULATED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDataOriginEnum::IfcDataOriginEnum IfcDataOriginEnum::FromString(const std::string& s) {
    if(s=="MEASURED"   ) return IfcDataOriginEnum::MEASURED;
    if(s=="PREDICTED"  ) return IfcDataOriginEnum::PREDICTED;
    if(s=="SIMULATED"  ) return IfcDataOriginEnum::SIMULATED;
    if(s=="USERDEFINED") return IfcDataOriginEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcDataOriginEnum::NOTDEFINED;
    throw;
}
std::string IfcDerivedUnitEnum::ToString(IfcDerivedUnitEnum v) {
    if ( v < 0 || v >= 49 ) throw;
    const char* names[] = { "ANGULARVELOCITYUNIT","COMPOUNDPLANEANGLEUNIT","DYNAMICVISCOSITYUNIT","HEATFLUXDENSITYUNIT","INTEGERCOUNTRATEUNIT","ISOTHERMALMOISTURECAPACITYUNIT","KINEMATICVISCOSITYUNIT","LINEARVELOCITYUNIT","MASSDENSITYUNIT","MASSFLOWRATEUNIT","MOISTUREDIFFUSIVITYUNIT","MOLECULARWEIGHTUNIT","SPECIFICHEATCAPACITYUNIT","THERMALADMITTANCEUNIT","THERMALCONDUCTANCEUNIT","THERMALRESISTANCEUNIT","THERMALTRANSMITTANCEUNIT","VAPORPERMEABILITYUNIT","VOLUMETRICFLOWRATEUNIT","ROTATIONALFREQUENCYUNIT","TORQUEUNIT","MOMENTOFINERTIAUNIT","LINEARMOMENTUNIT","LINEARFORCEUNIT","PLANARFORCEUNIT","MODULUSOFELASTICITYUNIT","SHEARMODULUSUNIT","LINEARSTIFFNESSUNIT","ROTATIONALSTIFFNESSUNIT","MODULUSOFSUBGRADEREACTIONUNIT","ACCELERATIONUNIT","CURVATUREUNIT","HEATINGVALUEUNIT","IONCONCENTRATIONUNIT","LUMINOUSINTENSITYDISTRIBUTIONUNIT","MASSPERLENGTHUNIT","MODULUSOFLINEARSUBGRADEREACTIONUNIT","MODULUSOFROTATIONALSUBGRADEREACTIONUNIT","PHUNIT","ROTATIONALMASSUNIT","SECTIONAREAINTEGRALUNIT","SECTIONMODULUSUNIT","SOUNDPOWERUNIT","SOUNDPRESSUREUNIT","TEMPERATUREGRADIENTUNIT","THERMALEXPANSIONCOEFFICIENTUNIT","WARPINGCONSTANTUNIT","WARPINGMOMENTUNIT","USERDEFINED" };
    return names[v];
}
IfcDerivedUnitEnum::IfcDerivedUnitEnum IfcDerivedUnitEnum::FromString(const std::string& s) {
    if(s=="ANGULARVELOCITYUNIT"                    ) return IfcDerivedUnitEnum::ANGULARVELOCITYUNIT;
    if(s=="COMPOUNDPLANEANGLEUNIT"                 ) return IfcDerivedUnitEnum::COMPOUNDPLANEANGLEUNIT;
    if(s=="DYNAMICVISCOSITYUNIT"                   ) return IfcDerivedUnitEnum::DYNAMICVISCOSITYUNIT;
    if(s=="HEATFLUXDENSITYUNIT"                    ) return IfcDerivedUnitEnum::HEATFLUXDENSITYUNIT;
    if(s=="INTEGERCOUNTRATEUNIT"                   ) return IfcDerivedUnitEnum::INTEGERCOUNTRATEUNIT;
    if(s=="ISOTHERMALMOISTURECAPACITYUNIT"         ) return IfcDerivedUnitEnum::ISOTHERMALMOISTURECAPACITYUNIT;
    if(s=="KINEMATICVISCOSITYUNIT"                 ) return IfcDerivedUnitEnum::KINEMATICVISCOSITYUNIT;
    if(s=="LINEARVELOCITYUNIT"                     ) return IfcDerivedUnitEnum::LINEARVELOCITYUNIT;
    if(s=="MASSDENSITYUNIT"                        ) return IfcDerivedUnitEnum::MASSDENSITYUNIT;
    if(s=="MASSFLOWRATEUNIT"                       ) return IfcDerivedUnitEnum::MASSFLOWRATEUNIT;
    if(s=="MOISTUREDIFFUSIVITYUNIT"                ) return IfcDerivedUnitEnum::MOISTUREDIFFUSIVITYUNIT;
    if(s=="MOLECULARWEIGHTUNIT"                    ) return IfcDerivedUnitEnum::MOLECULARWEIGHTUNIT;
    if(s=="SPECIFICHEATCAPACITYUNIT"               ) return IfcDerivedUnitEnum::SPECIFICHEATCAPACITYUNIT;
    if(s=="THERMALADMITTANCEUNIT"                  ) return IfcDerivedUnitEnum::THERMALADMITTANCEUNIT;
    if(s=="THERMALCONDUCTANCEUNIT"                 ) return IfcDerivedUnitEnum::THERMALCONDUCTANCEUNIT;
    if(s=="THERMALRESISTANCEUNIT"                  ) return IfcDerivedUnitEnum::THERMALRESISTANCEUNIT;
    if(s=="THERMALTRANSMITTANCEUNIT"               ) return IfcDerivedUnitEnum::THERMALTRANSMITTANCEUNIT;
    if(s=="VAPORPERMEABILITYUNIT"                  ) return IfcDerivedUnitEnum::VAPORPERMEABILITYUNIT;
    if(s=="VOLUMETRICFLOWRATEUNIT"                 ) return IfcDerivedUnitEnum::VOLUMETRICFLOWRATEUNIT;
    if(s=="ROTATIONALFREQUENCYUNIT"                ) return IfcDerivedUnitEnum::ROTATIONALFREQUENCYUNIT;
    if(s=="TORQUEUNIT"                             ) return IfcDerivedUnitEnum::TORQUEUNIT;
    if(s=="MOMENTOFINERTIAUNIT"                    ) return IfcDerivedUnitEnum::MOMENTOFINERTIAUNIT;
    if(s=="LINEARMOMENTUNIT"                       ) return IfcDerivedUnitEnum::LINEARMOMENTUNIT;
    if(s=="LINEARFORCEUNIT"                        ) return IfcDerivedUnitEnum::LINEARFORCEUNIT;
    if(s=="PLANARFORCEUNIT"                        ) return IfcDerivedUnitEnum::PLANARFORCEUNIT;
    if(s=="MODULUSOFELASTICITYUNIT"                ) return IfcDerivedUnitEnum::MODULUSOFELASTICITYUNIT;
    if(s=="SHEARMODULUSUNIT"                       ) return IfcDerivedUnitEnum::SHEARMODULUSUNIT;
    if(s=="LINEARSTIFFNESSUNIT"                    ) return IfcDerivedUnitEnum::LINEARSTIFFNESSUNIT;
    if(s=="ROTATIONALSTIFFNESSUNIT"                ) return IfcDerivedUnitEnum::ROTATIONALSTIFFNESSUNIT;
    if(s=="MODULUSOFSUBGRADEREACTIONUNIT"          ) return IfcDerivedUnitEnum::MODULUSOFSUBGRADEREACTIONUNIT;
    if(s=="ACCELERATIONUNIT"                       ) return IfcDerivedUnitEnum::ACCELERATIONUNIT;
    if(s=="CURVATUREUNIT"                          ) return IfcDerivedUnitEnum::CURVATUREUNIT;
    if(s=="HEATINGVALUEUNIT"                       ) return IfcDerivedUnitEnum::HEATINGVALUEUNIT;
    if(s=="IONCONCENTRATIONUNIT"                   ) return IfcDerivedUnitEnum::IONCONCENTRATIONUNIT;
    if(s=="LUMINOUSINTENSITYDISTRIBUTIONUNIT"      ) return IfcDerivedUnitEnum::LUMINOUSINTENSITYDISTRIBUTIONUNIT;
    if(s=="MASSPERLENGTHUNIT"                      ) return IfcDerivedUnitEnum::MASSPERLENGTHUNIT;
    if(s=="MODULUSOFLINEARSUBGRADEREACTIONUNIT"    ) return IfcDerivedUnitEnum::MODULUSOFLINEARSUBGRADEREACTIONUNIT;
    if(s=="MODULUSOFROTATIONALSUBGRADEREACTIONUNIT") return IfcDerivedUnitEnum::MODULUSOFROTATIONALSUBGRADEREACTIONUNIT;
    if(s=="PHUNIT"                                 ) return IfcDerivedUnitEnum::PHUNIT;
    if(s=="ROTATIONALMASSUNIT"                     ) return IfcDerivedUnitEnum::ROTATIONALMASSUNIT;
    if(s=="SECTIONAREAINTEGRALUNIT"                ) return IfcDerivedUnitEnum::SECTIONAREAINTEGRALUNIT;
    if(s=="SECTIONMODULUSUNIT"                     ) return IfcDerivedUnitEnum::SECTIONMODULUSUNIT;
    if(s=="SOUNDPOWERUNIT"                         ) return IfcDerivedUnitEnum::SOUNDPOWERUNIT;
    if(s=="SOUNDPRESSUREUNIT"                      ) return IfcDerivedUnitEnum::SOUNDPRESSUREUNIT;
    if(s=="TEMPERATUREGRADIENTUNIT"                ) return IfcDerivedUnitEnum::TEMPERATUREGRADIENTUNIT;
    if(s=="THERMALEXPANSIONCOEFFICIENTUNIT"        ) return IfcDerivedUnitEnum::THERMALEXPANSIONCOEFFICIENTUNIT;
    if(s=="WARPINGCONSTANTUNIT"                    ) return IfcDerivedUnitEnum::WARPINGCONSTANTUNIT;
    if(s=="WARPINGMOMENTUNIT"                      ) return IfcDerivedUnitEnum::WARPINGMOMENTUNIT;
    if(s=="USERDEFINED"                            ) return IfcDerivedUnitEnum::USERDEFINED;
    throw;
}
std::string IfcDimensionExtentUsage::ToString(IfcDimensionExtentUsage v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "ORIGIN","TARGET" };
    return names[v];
}
IfcDimensionExtentUsage::IfcDimensionExtentUsage IfcDimensionExtentUsage::FromString(const std::string& s) {
    if(s=="ORIGIN") return IfcDimensionExtentUsage::ORIGIN;
    if(s=="TARGET") return IfcDimensionExtentUsage::TARGET;
    throw;
}
std::string IfcDirectionSenseEnum::ToString(IfcDirectionSenseEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "POSITIVE","NEGATIVE" };
    return names[v];
}
IfcDirectionSenseEnum::IfcDirectionSenseEnum IfcDirectionSenseEnum::FromString(const std::string& s) {
    if(s=="POSITIVE") return IfcDirectionSenseEnum::POSITIVE;
    if(s=="NEGATIVE") return IfcDirectionSenseEnum::NEGATIVE;
    throw;
}
std::string IfcDistributionChamberElementTypeEnum::ToString(IfcDistributionChamberElementTypeEnum v) {
    if ( v < 0 || v >= 10 ) throw;
    const char* names[] = { "FORMEDDUCT","INSPECTIONCHAMBER","INSPECTIONPIT","MANHOLE","METERCHAMBER","SUMP","TRENCH","VALVECHAMBER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementTypeEnum IfcDistributionChamberElementTypeEnum::FromString(const std::string& s) {
    if(s=="FORMEDDUCT"       ) return IfcDistributionChamberElementTypeEnum::FORMEDDUCT;
    if(s=="INSPECTIONCHAMBER") return IfcDistributionChamberElementTypeEnum::INSPECTIONCHAMBER;
    if(s=="INSPECTIONPIT"    ) return IfcDistributionChamberElementTypeEnum::INSPECTIONPIT;
    if(s=="MANHOLE"          ) return IfcDistributionChamberElementTypeEnum::MANHOLE;
    if(s=="METERCHAMBER"     ) return IfcDistributionChamberElementTypeEnum::METERCHAMBER;
    if(s=="SUMP"             ) return IfcDistributionChamberElementTypeEnum::SUMP;
    if(s=="TRENCH"           ) return IfcDistributionChamberElementTypeEnum::TRENCH;
    if(s=="VALVECHAMBER"     ) return IfcDistributionChamberElementTypeEnum::VALVECHAMBER;
    if(s=="USERDEFINED"      ) return IfcDistributionChamberElementTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"       ) return IfcDistributionChamberElementTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcDocumentConfidentialityEnum::ToString(IfcDocumentConfidentialityEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "PUBLIC","RESTRICTED","CONFIDENTIAL","PERSONAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDocumentConfidentialityEnum::IfcDocumentConfidentialityEnum IfcDocumentConfidentialityEnum::FromString(const std::string& s) {
    if(s=="PUBLIC"      ) return IfcDocumentConfidentialityEnum::PUBLIC;
    if(s=="RESTRICTED"  ) return IfcDocumentConfidentialityEnum::RESTRICTED;
    if(s=="CONFIDENTIAL") return IfcDocumentConfidentialityEnum::CONFIDENTIAL;
    if(s=="PERSONAL"    ) return IfcDocumentConfidentialityEnum::PERSONAL;
    if(s=="USERDEFINED" ) return IfcDocumentConfidentialityEnum::USERDEFINED;
    if(s=="NOTDEFINED"  ) return IfcDocumentConfidentialityEnum::NOTDEFINED;
    throw;
}
std::string IfcDocumentStatusEnum::ToString(IfcDocumentStatusEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "DRAFT","FINALDRAFT","FINAL","REVISION","NOTDEFINED" };
    return names[v];
}
IfcDocumentStatusEnum::IfcDocumentStatusEnum IfcDocumentStatusEnum::FromString(const std::string& s) {
    if(s=="DRAFT"     ) return IfcDocumentStatusEnum::DRAFT;
    if(s=="FINALDRAFT") return IfcDocumentStatusEnum::FINALDRAFT;
    if(s=="FINAL"     ) return IfcDocumentStatusEnum::FINAL;
    if(s=="REVISION"  ) return IfcDocumentStatusEnum::REVISION;
    if(s=="NOTDEFINED") return IfcDocumentStatusEnum::NOTDEFINED;
    throw;
}
std::string IfcDoorPanelOperationEnum::ToString(IfcDoorPanelOperationEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "SWINGING","DOUBLE_ACTING","SLIDING","FOLDING","REVOLVING","ROLLINGUP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDoorPanelOperationEnum::IfcDoorPanelOperationEnum IfcDoorPanelOperationEnum::FromString(const std::string& s) {
    if(s=="SWINGING"     ) return IfcDoorPanelOperationEnum::SWINGING;
    if(s=="DOUBLE_ACTING") return IfcDoorPanelOperationEnum::DOUBLE_ACTING;
    if(s=="SLIDING"      ) return IfcDoorPanelOperationEnum::SLIDING;
    if(s=="FOLDING"      ) return IfcDoorPanelOperationEnum::FOLDING;
    if(s=="REVOLVING"    ) return IfcDoorPanelOperationEnum::REVOLVING;
    if(s=="ROLLINGUP"    ) return IfcDoorPanelOperationEnum::ROLLINGUP;
    if(s=="USERDEFINED"  ) return IfcDoorPanelOperationEnum::USERDEFINED;
    if(s=="NOTDEFINED"   ) return IfcDoorPanelOperationEnum::NOTDEFINED;
    throw;
}
std::string IfcDoorPanelPositionEnum::ToString(IfcDoorPanelPositionEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "LEFT","MIDDLE","RIGHT","NOTDEFINED" };
    return names[v];
}
IfcDoorPanelPositionEnum::IfcDoorPanelPositionEnum IfcDoorPanelPositionEnum::FromString(const std::string& s) {
    if(s=="LEFT"      ) return IfcDoorPanelPositionEnum::LEFT;
    if(s=="MIDDLE"    ) return IfcDoorPanelPositionEnum::MIDDLE;
    if(s=="RIGHT"     ) return IfcDoorPanelPositionEnum::RIGHT;
    if(s=="NOTDEFINED") return IfcDoorPanelPositionEnum::NOTDEFINED;
    throw;
}
std::string IfcDoorStyleConstructionEnum::ToString(IfcDoorStyleConstructionEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "ALUMINIUM","HIGH_GRADE_STEEL","STEEL","WOOD","ALUMINIUM_WOOD","ALUMINIUM_PLASTIC","PLASTIC","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDoorStyleConstructionEnum::IfcDoorStyleConstructionEnum IfcDoorStyleConstructionEnum::FromString(const std::string& s) {
    if(s=="ALUMINIUM"        ) return IfcDoorStyleConstructionEnum::ALUMINIUM;
    if(s=="HIGH_GRADE_STEEL" ) return IfcDoorStyleConstructionEnum::HIGH_GRADE_STEEL;
    if(s=="STEEL"            ) return IfcDoorStyleConstructionEnum::STEEL;
    if(s=="WOOD"             ) return IfcDoorStyleConstructionEnum::WOOD;
    if(s=="ALUMINIUM_WOOD"   ) return IfcDoorStyleConstructionEnum::ALUMINIUM_WOOD;
    if(s=="ALUMINIUM_PLASTIC") return IfcDoorStyleConstructionEnum::ALUMINIUM_PLASTIC;
    if(s=="PLASTIC"          ) return IfcDoorStyleConstructionEnum::PLASTIC;
    if(s=="USERDEFINED"      ) return IfcDoorStyleConstructionEnum::USERDEFINED;
    if(s=="NOTDEFINED"       ) return IfcDoorStyleConstructionEnum::NOTDEFINED;
    throw;
}
std::string IfcDoorStyleOperationEnum::ToString(IfcDoorStyleOperationEnum v) {
    if ( v < 0 || v >= 18 ) throw;
    const char* names[] = { "SINGLE_SWING_LEFT","SINGLE_SWING_RIGHT","DOUBLE_DOOR_SINGLE_SWING","DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT","DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT","DOUBLE_SWING_LEFT","DOUBLE_SWING_RIGHT","DOUBLE_DOOR_DOUBLE_SWING","SLIDING_TO_LEFT","SLIDING_TO_RIGHT","DOUBLE_DOOR_SLIDING","FOLDING_TO_LEFT","FOLDING_TO_RIGHT","DOUBLE_DOOR_FOLDING","REVOLVING","ROLLINGUP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDoorStyleOperationEnum::IfcDoorStyleOperationEnum IfcDoorStyleOperationEnum::FromString(const std::string& s) {
    if(s=="SINGLE_SWING_LEFT"                      ) return IfcDoorStyleOperationEnum::SINGLE_SWING_LEFT;
    if(s=="SINGLE_SWING_RIGHT"                     ) return IfcDoorStyleOperationEnum::SINGLE_SWING_RIGHT;
    if(s=="DOUBLE_DOOR_SINGLE_SWING"               ) return IfcDoorStyleOperationEnum::DOUBLE_DOOR_SINGLE_SWING;
    if(s=="DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT" ) return IfcDoorStyleOperationEnum::DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT;
    if(s=="DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT") return IfcDoorStyleOperationEnum::DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT;
    if(s=="DOUBLE_SWING_LEFT"                      ) return IfcDoorStyleOperationEnum::DOUBLE_SWING_LEFT;
    if(s=="DOUBLE_SWING_RIGHT"                     ) return IfcDoorStyleOperationEnum::DOUBLE_SWING_RIGHT;
    if(s=="DOUBLE_DOOR_DOUBLE_SWING"               ) return IfcDoorStyleOperationEnum::DOUBLE_DOOR_DOUBLE_SWING;
    if(s=="SLIDING_TO_LEFT"                        ) return IfcDoorStyleOperationEnum::SLIDING_TO_LEFT;
    if(s=="SLIDING_TO_RIGHT"                       ) return IfcDoorStyleOperationEnum::SLIDING_TO_RIGHT;
    if(s=="DOUBLE_DOOR_SLIDING"                    ) return IfcDoorStyleOperationEnum::DOUBLE_DOOR_SLIDING;
    if(s=="FOLDING_TO_LEFT"                        ) return IfcDoorStyleOperationEnum::FOLDING_TO_LEFT;
    if(s=="FOLDING_TO_RIGHT"                       ) return IfcDoorStyleOperationEnum::FOLDING_TO_RIGHT;
    if(s=="DOUBLE_DOOR_FOLDING"                    ) return IfcDoorStyleOperationEnum::DOUBLE_DOOR_FOLDING;
    if(s=="REVOLVING"                              ) return IfcDoorStyleOperationEnum::REVOLVING;
    if(s=="ROLLINGUP"                              ) return IfcDoorStyleOperationEnum::ROLLINGUP;
    if(s=="USERDEFINED"                            ) return IfcDoorStyleOperationEnum::USERDEFINED;
    if(s=="NOTDEFINED"                             ) return IfcDoorStyleOperationEnum::NOTDEFINED;
    throw;
}
std::string IfcDuctFittingTypeEnum::ToString(IfcDuctFittingTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "BEND","CONNECTOR","ENTRY","EXIT","JUNCTION","OBSTRUCTION","TRANSITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDuctFittingTypeEnum::IfcDuctFittingTypeEnum IfcDuctFittingTypeEnum::FromString(const std::string& s) {
    if(s=="BEND"       ) return IfcDuctFittingTypeEnum::BEND;
    if(s=="CONNECTOR"  ) return IfcDuctFittingTypeEnum::CONNECTOR;
    if(s=="ENTRY"      ) return IfcDuctFittingTypeEnum::ENTRY;
    if(s=="EXIT"       ) return IfcDuctFittingTypeEnum::EXIT;
    if(s=="JUNCTION"   ) return IfcDuctFittingTypeEnum::JUNCTION;
    if(s=="OBSTRUCTION") return IfcDuctFittingTypeEnum::OBSTRUCTION;
    if(s=="TRANSITION" ) return IfcDuctFittingTypeEnum::TRANSITION;
    if(s=="USERDEFINED") return IfcDuctFittingTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcDuctFittingTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcDuctSegmentTypeEnum::ToString(IfcDuctSegmentTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "RIGIDSEGMENT","FLEXIBLESEGMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDuctSegmentTypeEnum::IfcDuctSegmentTypeEnum IfcDuctSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="RIGIDSEGMENT"   ) return IfcDuctSegmentTypeEnum::RIGIDSEGMENT;
    if(s=="FLEXIBLESEGMENT") return IfcDuctSegmentTypeEnum::FLEXIBLESEGMENT;
    if(s=="USERDEFINED"    ) return IfcDuctSegmentTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"     ) return IfcDuctSegmentTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcDuctSilencerTypeEnum::ToString(IfcDuctSilencerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "FLATOVAL","RECTANGULAR","ROUND","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcDuctSilencerTypeEnum::IfcDuctSilencerTypeEnum IfcDuctSilencerTypeEnum::FromString(const std::string& s) {
    if(s=="FLATOVAL"   ) return IfcDuctSilencerTypeEnum::FLATOVAL;
    if(s=="RECTANGULAR") return IfcDuctSilencerTypeEnum::RECTANGULAR;
    if(s=="ROUND"      ) return IfcDuctSilencerTypeEnum::ROUND;
    if(s=="USERDEFINED") return IfcDuctSilencerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcDuctSilencerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricApplianceTypeEnum::ToString(IfcElectricApplianceTypeEnum v) {
    if ( v < 0 || v >= 26 ) throw;
    const char* names[] = { "COMPUTER","DIRECTWATERHEATER","DISHWASHER","ELECTRICCOOKER","ELECTRICHEATER","FACSIMILE","FREESTANDINGFAN","FREEZER","FRIDGE_FREEZER","HANDDRYER","INDIRECTWATERHEATER","MICROWAVE","PHOTOCOPIER","PRINTER","REFRIGERATOR","RADIANTHEATER","SCANNER","TELEPHONE","TUMBLEDRYER","TV","VENDINGMACHINE","WASHINGMACHINE","WATERHEATER","WATERCOOLER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricApplianceTypeEnum::IfcElectricApplianceTypeEnum IfcElectricApplianceTypeEnum::FromString(const std::string& s) {
    if(s=="COMPUTER"           ) return IfcElectricApplianceTypeEnum::COMPUTER;
    if(s=="DIRECTWATERHEATER"  ) return IfcElectricApplianceTypeEnum::DIRECTWATERHEATER;
    if(s=="DISHWASHER"         ) return IfcElectricApplianceTypeEnum::DISHWASHER;
    if(s=="ELECTRICCOOKER"     ) return IfcElectricApplianceTypeEnum::ELECTRICCOOKER;
    if(s=="ELECTRICHEATER"     ) return IfcElectricApplianceTypeEnum::ELECTRICHEATER;
    if(s=="FACSIMILE"          ) return IfcElectricApplianceTypeEnum::FACSIMILE;
    if(s=="FREESTANDINGFAN"    ) return IfcElectricApplianceTypeEnum::FREESTANDINGFAN;
    if(s=="FREEZER"            ) return IfcElectricApplianceTypeEnum::FREEZER;
    if(s=="FRIDGE_FREEZER"     ) return IfcElectricApplianceTypeEnum::FRIDGE_FREEZER;
    if(s=="HANDDRYER"          ) return IfcElectricApplianceTypeEnum::HANDDRYER;
    if(s=="INDIRECTWATERHEATER") return IfcElectricApplianceTypeEnum::INDIRECTWATERHEATER;
    if(s=="MICROWAVE"          ) return IfcElectricApplianceTypeEnum::MICROWAVE;
    if(s=="PHOTOCOPIER"        ) return IfcElectricApplianceTypeEnum::PHOTOCOPIER;
    if(s=="PRINTER"            ) return IfcElectricApplianceTypeEnum::PRINTER;
    if(s=="REFRIGERATOR"       ) return IfcElectricApplianceTypeEnum::REFRIGERATOR;
    if(s=="RADIANTHEATER"      ) return IfcElectricApplianceTypeEnum::RADIANTHEATER;
    if(s=="SCANNER"            ) return IfcElectricApplianceTypeEnum::SCANNER;
    if(s=="TELEPHONE"          ) return IfcElectricApplianceTypeEnum::TELEPHONE;
    if(s=="TUMBLEDRYER"        ) return IfcElectricApplianceTypeEnum::TUMBLEDRYER;
    if(s=="TV"                 ) return IfcElectricApplianceTypeEnum::TV;
    if(s=="VENDINGMACHINE"     ) return IfcElectricApplianceTypeEnum::VENDINGMACHINE;
    if(s=="WASHINGMACHINE"     ) return IfcElectricApplianceTypeEnum::WASHINGMACHINE;
    if(s=="WATERHEATER"        ) return IfcElectricApplianceTypeEnum::WATERHEATER;
    if(s=="WATERCOOLER"        ) return IfcElectricApplianceTypeEnum::WATERCOOLER;
    if(s=="USERDEFINED"        ) return IfcElectricApplianceTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcElectricApplianceTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricCurrentEnum::ToString(IfcElectricCurrentEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "ALTERNATING","DIRECT","NOTDEFINED" };
    return names[v];
}
IfcElectricCurrentEnum::IfcElectricCurrentEnum IfcElectricCurrentEnum::FromString(const std::string& s) {
    if(s=="ALTERNATING") return IfcElectricCurrentEnum::ALTERNATING;
    if(s=="DIRECT"     ) return IfcElectricCurrentEnum::DIRECT;
    if(s=="NOTDEFINED" ) return IfcElectricCurrentEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricDistributionPointFunctionEnum::ToString(IfcElectricDistributionPointFunctionEnum v) {
    if ( v < 0 || v >= 11 ) throw;
    const char* names[] = { "ALARMPANEL","CONSUMERUNIT","CONTROLPANEL","DISTRIBUTIONBOARD","GASDETECTORPANEL","INDICATORPANEL","MIMICPANEL","MOTORCONTROLCENTRE","SWITCHBOARD","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunctionEnum IfcElectricDistributionPointFunctionEnum::FromString(const std::string& s) {
    if(s=="ALARMPANEL"        ) return IfcElectricDistributionPointFunctionEnum::ALARMPANEL;
    if(s=="CONSUMERUNIT"      ) return IfcElectricDistributionPointFunctionEnum::CONSUMERUNIT;
    if(s=="CONTROLPANEL"      ) return IfcElectricDistributionPointFunctionEnum::CONTROLPANEL;
    if(s=="DISTRIBUTIONBOARD" ) return IfcElectricDistributionPointFunctionEnum::DISTRIBUTIONBOARD;
    if(s=="GASDETECTORPANEL"  ) return IfcElectricDistributionPointFunctionEnum::GASDETECTORPANEL;
    if(s=="INDICATORPANEL"    ) return IfcElectricDistributionPointFunctionEnum::INDICATORPANEL;
    if(s=="MIMICPANEL"        ) return IfcElectricDistributionPointFunctionEnum::MIMICPANEL;
    if(s=="MOTORCONTROLCENTRE") return IfcElectricDistributionPointFunctionEnum::MOTORCONTROLCENTRE;
    if(s=="SWITCHBOARD"       ) return IfcElectricDistributionPointFunctionEnum::SWITCHBOARD;
    if(s=="USERDEFINED"       ) return IfcElectricDistributionPointFunctionEnum::USERDEFINED;
    if(s=="NOTDEFINED"        ) return IfcElectricDistributionPointFunctionEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricFlowStorageDeviceTypeEnum::ToString(IfcElectricFlowStorageDeviceTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "BATTERY","CAPACITORBANK","HARMONICFILTER","INDUCTORBANK","UPS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceTypeEnum IfcElectricFlowStorageDeviceTypeEnum::FromString(const std::string& s) {
    if(s=="BATTERY"       ) return IfcElectricFlowStorageDeviceTypeEnum::BATTERY;
    if(s=="CAPACITORBANK" ) return IfcElectricFlowStorageDeviceTypeEnum::CAPACITORBANK;
    if(s=="HARMONICFILTER") return IfcElectricFlowStorageDeviceTypeEnum::HARMONICFILTER;
    if(s=="INDUCTORBANK"  ) return IfcElectricFlowStorageDeviceTypeEnum::INDUCTORBANK;
    if(s=="UPS"           ) return IfcElectricFlowStorageDeviceTypeEnum::UPS;
    if(s=="USERDEFINED"   ) return IfcElectricFlowStorageDeviceTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"    ) return IfcElectricFlowStorageDeviceTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricGeneratorTypeEnum::ToString(IfcElectricGeneratorTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricGeneratorTypeEnum::IfcElectricGeneratorTypeEnum IfcElectricGeneratorTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcElectricGeneratorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcElectricGeneratorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricHeaterTypeEnum::ToString(IfcElectricHeaterTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "ELECTRICPOINTHEATER","ELECTRICCABLEHEATER","ELECTRICMATHEATER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricHeaterTypeEnum::IfcElectricHeaterTypeEnum IfcElectricHeaterTypeEnum::FromString(const std::string& s) {
    if(s=="ELECTRICPOINTHEATER") return IfcElectricHeaterTypeEnum::ELECTRICPOINTHEATER;
    if(s=="ELECTRICCABLEHEATER") return IfcElectricHeaterTypeEnum::ELECTRICCABLEHEATER;
    if(s=="ELECTRICMATHEATER"  ) return IfcElectricHeaterTypeEnum::ELECTRICMATHEATER;
    if(s=="USERDEFINED"        ) return IfcElectricHeaterTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcElectricHeaterTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricMotorTypeEnum::ToString(IfcElectricMotorTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "DC","INDUCTION","POLYPHASE","RELUCTANCESYNCHRONOUS","SYNCHRONOUS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricMotorTypeEnum::IfcElectricMotorTypeEnum IfcElectricMotorTypeEnum::FromString(const std::string& s) {
    if(s=="DC"                   ) return IfcElectricMotorTypeEnum::DC;
    if(s=="INDUCTION"            ) return IfcElectricMotorTypeEnum::INDUCTION;
    if(s=="POLYPHASE"            ) return IfcElectricMotorTypeEnum::POLYPHASE;
    if(s=="RELUCTANCESYNCHRONOUS") return IfcElectricMotorTypeEnum::RELUCTANCESYNCHRONOUS;
    if(s=="SYNCHRONOUS"          ) return IfcElectricMotorTypeEnum::SYNCHRONOUS;
    if(s=="USERDEFINED"          ) return IfcElectricMotorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"           ) return IfcElectricMotorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElectricTimeControlTypeEnum::ToString(IfcElectricTimeControlTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "TIMECLOCK","TIMEDELAY","RELAY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElectricTimeControlTypeEnum::IfcElectricTimeControlTypeEnum IfcElectricTimeControlTypeEnum::FromString(const std::string& s) {
    if(s=="TIMECLOCK"  ) return IfcElectricTimeControlTypeEnum::TIMECLOCK;
    if(s=="TIMEDELAY"  ) return IfcElectricTimeControlTypeEnum::TIMEDELAY;
    if(s=="RELAY"      ) return IfcElectricTimeControlTypeEnum::RELAY;
    if(s=="USERDEFINED") return IfcElectricTimeControlTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcElectricTimeControlTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElementAssemblyTypeEnum::ToString(IfcElementAssemblyTypeEnum v) {
    if ( v < 0 || v >= 11 ) throw;
    const char* names[] = { "ACCESSORY_ASSEMBLY","ARCH","BEAM_GRID","BRACED_FRAME","GIRDER","REINFORCEMENT_UNIT","RIGID_FRAME","SLAB_FIELD","TRUSS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcElementAssemblyTypeEnum::IfcElementAssemblyTypeEnum IfcElementAssemblyTypeEnum::FromString(const std::string& s) {
    if(s=="ACCESSORY_ASSEMBLY") return IfcElementAssemblyTypeEnum::ACCESSORY_ASSEMBLY;
    if(s=="ARCH"              ) return IfcElementAssemblyTypeEnum::ARCH;
    if(s=="BEAM_GRID"         ) return IfcElementAssemblyTypeEnum::BEAM_GRID;
    if(s=="BRACED_FRAME"      ) return IfcElementAssemblyTypeEnum::BRACED_FRAME;
    if(s=="GIRDER"            ) return IfcElementAssemblyTypeEnum::GIRDER;
    if(s=="REINFORCEMENT_UNIT") return IfcElementAssemblyTypeEnum::REINFORCEMENT_UNIT;
    if(s=="RIGID_FRAME"       ) return IfcElementAssemblyTypeEnum::RIGID_FRAME;
    if(s=="SLAB_FIELD"        ) return IfcElementAssemblyTypeEnum::SLAB_FIELD;
    if(s=="TRUSS"             ) return IfcElementAssemblyTypeEnum::TRUSS;
    if(s=="USERDEFINED"       ) return IfcElementAssemblyTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"        ) return IfcElementAssemblyTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcElementCompositionEnum::ToString(IfcElementCompositionEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "COMPLEX","ELEMENT","PARTIAL" };
    return names[v];
}
IfcElementCompositionEnum::IfcElementCompositionEnum IfcElementCompositionEnum::FromString(const std::string& s) {
    if(s=="COMPLEX") return IfcElementCompositionEnum::COMPLEX;
    if(s=="ELEMENT") return IfcElementCompositionEnum::ELEMENT;
    if(s=="PARTIAL") return IfcElementCompositionEnum::PARTIAL;
    throw;
}
std::string IfcEnergySequenceEnum::ToString(IfcEnergySequenceEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "PRIMARY","SECONDARY","TERTIARY","AUXILIARY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEnergySequenceEnum::IfcEnergySequenceEnum IfcEnergySequenceEnum::FromString(const std::string& s) {
    if(s=="PRIMARY"    ) return IfcEnergySequenceEnum::PRIMARY;
    if(s=="SECONDARY"  ) return IfcEnergySequenceEnum::SECONDARY;
    if(s=="TERTIARY"   ) return IfcEnergySequenceEnum::TERTIARY;
    if(s=="AUXILIARY"  ) return IfcEnergySequenceEnum::AUXILIARY;
    if(s=="USERDEFINED") return IfcEnergySequenceEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcEnergySequenceEnum::NOTDEFINED;
    throw;
}
std::string IfcEnvironmentalImpactCategoryEnum::ToString(IfcEnvironmentalImpactCategoryEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "COMBINEDVALUE","DISPOSAL","EXTRACTION","INSTALLATION","MANUFACTURE","TRANSPORTATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategoryEnum IfcEnvironmentalImpactCategoryEnum::FromString(const std::string& s) {
    if(s=="COMBINEDVALUE" ) return IfcEnvironmentalImpactCategoryEnum::COMBINEDVALUE;
    if(s=="DISPOSAL"      ) return IfcEnvironmentalImpactCategoryEnum::DISPOSAL;
    if(s=="EXTRACTION"    ) return IfcEnvironmentalImpactCategoryEnum::EXTRACTION;
    if(s=="INSTALLATION"  ) return IfcEnvironmentalImpactCategoryEnum::INSTALLATION;
    if(s=="MANUFACTURE"   ) return IfcEnvironmentalImpactCategoryEnum::MANUFACTURE;
    if(s=="TRANSPORTATION") return IfcEnvironmentalImpactCategoryEnum::TRANSPORTATION;
    if(s=="USERDEFINED"   ) return IfcEnvironmentalImpactCategoryEnum::USERDEFINED;
    if(s=="NOTDEFINED"    ) return IfcEnvironmentalImpactCategoryEnum::NOTDEFINED;
    throw;
}
std::string IfcEvaporativeCoolerTypeEnum::ToString(IfcEvaporativeCoolerTypeEnum v) {
    if ( v < 0 || v >= 11 ) throw;
    const char* names[] = { "DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER","DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER","DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER","DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER","DIRECTEVAPORATIVEAIRWASHER","INDIRECTEVAPORATIVEPACKAGEAIRCOOLER","INDIRECTEVAPORATIVEWETCOIL","INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER","INDIRECTDIRECTCOMBINATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerTypeEnum IfcEvaporativeCoolerTypeEnum::FromString(const std::string& s) {
    if(s=="DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER"      ) return IfcEvaporativeCoolerTypeEnum::DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER;
    if(s=="DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER"       ) return IfcEvaporativeCoolerTypeEnum::DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER;
    if(s=="DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER" ) return IfcEvaporativeCoolerTypeEnum::DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER;
    if(s=="DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER"   ) return IfcEvaporativeCoolerTypeEnum::DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER;
    if(s=="DIRECTEVAPORATIVEAIRWASHER"                 ) return IfcEvaporativeCoolerTypeEnum::DIRECTEVAPORATIVEAIRWASHER;
    if(s=="INDIRECTEVAPORATIVEPACKAGEAIRCOOLER"        ) return IfcEvaporativeCoolerTypeEnum::INDIRECTEVAPORATIVEPACKAGEAIRCOOLER;
    if(s=="INDIRECTEVAPORATIVEWETCOIL"                 ) return IfcEvaporativeCoolerTypeEnum::INDIRECTEVAPORATIVEWETCOIL;
    if(s=="INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER") return IfcEvaporativeCoolerTypeEnum::INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER;
    if(s=="INDIRECTDIRECTCOMBINATION"                  ) return IfcEvaporativeCoolerTypeEnum::INDIRECTDIRECTCOMBINATION;
    if(s=="USERDEFINED"                                ) return IfcEvaporativeCoolerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                                 ) return IfcEvaporativeCoolerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcEvaporatorTypeEnum::ToString(IfcEvaporatorTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "DIRECTEXPANSIONSHELLANDTUBE","DIRECTEXPANSIONTUBEINTUBE","DIRECTEXPANSIONBRAZEDPLATE","FLOODEDSHELLANDTUBE","SHELLANDCOIL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcEvaporatorTypeEnum::IfcEvaporatorTypeEnum IfcEvaporatorTypeEnum::FromString(const std::string& s) {
    if(s=="DIRECTEXPANSIONSHELLANDTUBE") return IfcEvaporatorTypeEnum::DIRECTEXPANSIONSHELLANDTUBE;
    if(s=="DIRECTEXPANSIONTUBEINTUBE"  ) return IfcEvaporatorTypeEnum::DIRECTEXPANSIONTUBEINTUBE;
    if(s=="DIRECTEXPANSIONBRAZEDPLATE" ) return IfcEvaporatorTypeEnum::DIRECTEXPANSIONBRAZEDPLATE;
    if(s=="FLOODEDSHELLANDTUBE"        ) return IfcEvaporatorTypeEnum::FLOODEDSHELLANDTUBE;
    if(s=="SHELLANDCOIL"               ) return IfcEvaporatorTypeEnum::SHELLANDCOIL;
    if(s=="USERDEFINED"                ) return IfcEvaporatorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                 ) return IfcEvaporatorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcFanTypeEnum::ToString(IfcFanTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "CENTRIFUGALFORWARDCURVED","CENTRIFUGALRADIAL","CENTRIFUGALBACKWARDINCLINEDCURVED","CENTRIFUGALAIRFOIL","TUBEAXIAL","VANEAXIAL","PROPELLORAXIAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFanTypeEnum::IfcFanTypeEnum IfcFanTypeEnum::FromString(const std::string& s) {
    if(s=="CENTRIFUGALFORWARDCURVED"         ) return IfcFanTypeEnum::CENTRIFUGALFORWARDCURVED;
    if(s=="CENTRIFUGALRADIAL"                ) return IfcFanTypeEnum::CENTRIFUGALRADIAL;
    if(s=="CENTRIFUGALBACKWARDINCLINEDCURVED") return IfcFanTypeEnum::CENTRIFUGALBACKWARDINCLINEDCURVED;
    if(s=="CENTRIFUGALAIRFOIL"               ) return IfcFanTypeEnum::CENTRIFUGALAIRFOIL;
    if(s=="TUBEAXIAL"                        ) return IfcFanTypeEnum::TUBEAXIAL;
    if(s=="VANEAXIAL"                        ) return IfcFanTypeEnum::VANEAXIAL;
    if(s=="PROPELLORAXIAL"                   ) return IfcFanTypeEnum::PROPELLORAXIAL;
    if(s=="USERDEFINED"                      ) return IfcFanTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                       ) return IfcFanTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcFilterTypeEnum::ToString(IfcFilterTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "AIRPARTICLEFILTER","ODORFILTER","OILFILTER","STRAINER","WATERFILTER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFilterTypeEnum::IfcFilterTypeEnum IfcFilterTypeEnum::FromString(const std::string& s) {
    if(s=="AIRPARTICLEFILTER") return IfcFilterTypeEnum::AIRPARTICLEFILTER;
    if(s=="ODORFILTER"       ) return IfcFilterTypeEnum::ODORFILTER;
    if(s=="OILFILTER"        ) return IfcFilterTypeEnum::OILFILTER;
    if(s=="STRAINER"         ) return IfcFilterTypeEnum::STRAINER;
    if(s=="WATERFILTER"      ) return IfcFilterTypeEnum::WATERFILTER;
    if(s=="USERDEFINED"      ) return IfcFilterTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"       ) return IfcFilterTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcFireSuppressionTerminalTypeEnum::ToString(IfcFireSuppressionTerminalTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "BREECHINGINLET","FIREHYDRANT","HOSEREEL","SPRINKLER","SPRINKLERDEFLECTOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalTypeEnum IfcFireSuppressionTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="BREECHINGINLET"    ) return IfcFireSuppressionTerminalTypeEnum::BREECHINGINLET;
    if(s=="FIREHYDRANT"       ) return IfcFireSuppressionTerminalTypeEnum::FIREHYDRANT;
    if(s=="HOSEREEL"          ) return IfcFireSuppressionTerminalTypeEnum::HOSEREEL;
    if(s=="SPRINKLER"         ) return IfcFireSuppressionTerminalTypeEnum::SPRINKLER;
    if(s=="SPRINKLERDEFLECTOR") return IfcFireSuppressionTerminalTypeEnum::SPRINKLERDEFLECTOR;
    if(s=="USERDEFINED"       ) return IfcFireSuppressionTerminalTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"        ) return IfcFireSuppressionTerminalTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcFlowDirectionEnum::ToString(IfcFlowDirectionEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "SOURCE","SINK","SOURCEANDSINK","NOTDEFINED" };
    return names[v];
}
IfcFlowDirectionEnum::IfcFlowDirectionEnum IfcFlowDirectionEnum::FromString(const std::string& s) {
    if(s=="SOURCE"       ) return IfcFlowDirectionEnum::SOURCE;
    if(s=="SINK"         ) return IfcFlowDirectionEnum::SINK;
    if(s=="SOURCEANDSINK") return IfcFlowDirectionEnum::SOURCEANDSINK;
    if(s=="NOTDEFINED"   ) return IfcFlowDirectionEnum::NOTDEFINED;
    throw;
}
std::string IfcFlowInstrumentTypeEnum::ToString(IfcFlowInstrumentTypeEnum v) {
    if ( v < 0 || v >= 10 ) throw;
    const char* names[] = { "PRESSUREGAUGE","THERMOMETER","AMMETER","FREQUENCYMETER","POWERFACTORMETER","PHASEANGLEMETER","VOLTMETER_PEAK","VOLTMETER_RMS","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFlowInstrumentTypeEnum::IfcFlowInstrumentTypeEnum IfcFlowInstrumentTypeEnum::FromString(const std::string& s) {
    if(s=="PRESSUREGAUGE"   ) return IfcFlowInstrumentTypeEnum::PRESSUREGAUGE;
    if(s=="THERMOMETER"     ) return IfcFlowInstrumentTypeEnum::THERMOMETER;
    if(s=="AMMETER"         ) return IfcFlowInstrumentTypeEnum::AMMETER;
    if(s=="FREQUENCYMETER"  ) return IfcFlowInstrumentTypeEnum::FREQUENCYMETER;
    if(s=="POWERFACTORMETER") return IfcFlowInstrumentTypeEnum::POWERFACTORMETER;
    if(s=="PHASEANGLEMETER" ) return IfcFlowInstrumentTypeEnum::PHASEANGLEMETER;
    if(s=="VOLTMETER_PEAK"  ) return IfcFlowInstrumentTypeEnum::VOLTMETER_PEAK;
    if(s=="VOLTMETER_RMS"   ) return IfcFlowInstrumentTypeEnum::VOLTMETER_RMS;
    if(s=="USERDEFINED"     ) return IfcFlowInstrumentTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcFlowInstrumentTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcFlowMeterTypeEnum::ToString(IfcFlowMeterTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "ELECTRICMETER","ENERGYMETER","FLOWMETER","GASMETER","OILMETER","WATERMETER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFlowMeterTypeEnum::IfcFlowMeterTypeEnum IfcFlowMeterTypeEnum::FromString(const std::string& s) {
    if(s=="ELECTRICMETER") return IfcFlowMeterTypeEnum::ELECTRICMETER;
    if(s=="ENERGYMETER"  ) return IfcFlowMeterTypeEnum::ENERGYMETER;
    if(s=="FLOWMETER"    ) return IfcFlowMeterTypeEnum::FLOWMETER;
    if(s=="GASMETER"     ) return IfcFlowMeterTypeEnum::GASMETER;
    if(s=="OILMETER"     ) return IfcFlowMeterTypeEnum::OILMETER;
    if(s=="WATERMETER"   ) return IfcFlowMeterTypeEnum::WATERMETER;
    if(s=="USERDEFINED"  ) return IfcFlowMeterTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"   ) return IfcFlowMeterTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcFootingTypeEnum::ToString(IfcFootingTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "FOOTING_BEAM","PAD_FOOTING","PILE_CAP","STRIP_FOOTING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcFootingTypeEnum::IfcFootingTypeEnum IfcFootingTypeEnum::FromString(const std::string& s) {
    if(s=="FOOTING_BEAM" ) return IfcFootingTypeEnum::FOOTING_BEAM;
    if(s=="PAD_FOOTING"  ) return IfcFootingTypeEnum::PAD_FOOTING;
    if(s=="PILE_CAP"     ) return IfcFootingTypeEnum::PILE_CAP;
    if(s=="STRIP_FOOTING") return IfcFootingTypeEnum::STRIP_FOOTING;
    if(s=="USERDEFINED"  ) return IfcFootingTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"   ) return IfcFootingTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcGasTerminalTypeEnum::ToString(IfcGasTerminalTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "GASAPPLIANCE","GASBOOSTER","GASBURNER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcGasTerminalTypeEnum::IfcGasTerminalTypeEnum IfcGasTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="GASAPPLIANCE") return IfcGasTerminalTypeEnum::GASAPPLIANCE;
    if(s=="GASBOOSTER"  ) return IfcGasTerminalTypeEnum::GASBOOSTER;
    if(s=="GASBURNER"   ) return IfcGasTerminalTypeEnum::GASBURNER;
    if(s=="USERDEFINED" ) return IfcGasTerminalTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"  ) return IfcGasTerminalTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcGeometricProjectionEnum::ToString(IfcGeometricProjectionEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "GRAPH_VIEW","SKETCH_VIEW","MODEL_VIEW","PLAN_VIEW","REFLECTED_PLAN_VIEW","SECTION_VIEW","ELEVATION_VIEW","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcGeometricProjectionEnum::IfcGeometricProjectionEnum IfcGeometricProjectionEnum::FromString(const std::string& s) {
    if(s=="GRAPH_VIEW"         ) return IfcGeometricProjectionEnum::GRAPH_VIEW;
    if(s=="SKETCH_VIEW"        ) return IfcGeometricProjectionEnum::SKETCH_VIEW;
    if(s=="MODEL_VIEW"         ) return IfcGeometricProjectionEnum::MODEL_VIEW;
    if(s=="PLAN_VIEW"          ) return IfcGeometricProjectionEnum::PLAN_VIEW;
    if(s=="REFLECTED_PLAN_VIEW") return IfcGeometricProjectionEnum::REFLECTED_PLAN_VIEW;
    if(s=="SECTION_VIEW"       ) return IfcGeometricProjectionEnum::SECTION_VIEW;
    if(s=="ELEVATION_VIEW"     ) return IfcGeometricProjectionEnum::ELEVATION_VIEW;
    if(s=="USERDEFINED"        ) return IfcGeometricProjectionEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcGeometricProjectionEnum::NOTDEFINED;
    throw;
}
std::string IfcGlobalOrLocalEnum::ToString(IfcGlobalOrLocalEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "GLOBAL_COORDS","LOCAL_COORDS" };
    return names[v];
}
IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum IfcGlobalOrLocalEnum::FromString(const std::string& s) {
    if(s=="GLOBAL_COORDS") return IfcGlobalOrLocalEnum::GLOBAL_COORDS;
    if(s=="LOCAL_COORDS" ) return IfcGlobalOrLocalEnum::LOCAL_COORDS;
    throw;
}
std::string IfcHeatExchangerTypeEnum::ToString(IfcHeatExchangerTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "PLATE","SHELLANDTUBE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcHeatExchangerTypeEnum::IfcHeatExchangerTypeEnum IfcHeatExchangerTypeEnum::FromString(const std::string& s) {
    if(s=="PLATE"       ) return IfcHeatExchangerTypeEnum::PLATE;
    if(s=="SHELLANDTUBE") return IfcHeatExchangerTypeEnum::SHELLANDTUBE;
    if(s=="USERDEFINED" ) return IfcHeatExchangerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"  ) return IfcHeatExchangerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcHumidifierTypeEnum::ToString(IfcHumidifierTypeEnum v) {
    if ( v < 0 || v >= 15 ) throw;
    const char* names[] = { "STEAMINJECTION","ADIABATICAIRWASHER","ADIABATICPAN","ADIABATICWETTEDELEMENT","ADIABATICATOMIZING","ADIABATICULTRASONIC","ADIABATICRIGIDMEDIA","ADIABATICCOMPRESSEDAIRNOZZLE","ASSISTEDELECTRIC","ASSISTEDNATURALGAS","ASSISTEDPROPANE","ASSISTEDBUTANE","ASSISTEDSTEAM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcHumidifierTypeEnum::IfcHumidifierTypeEnum IfcHumidifierTypeEnum::FromString(const std::string& s) {
    if(s=="STEAMINJECTION"              ) return IfcHumidifierTypeEnum::STEAMINJECTION;
    if(s=="ADIABATICAIRWASHER"          ) return IfcHumidifierTypeEnum::ADIABATICAIRWASHER;
    if(s=="ADIABATICPAN"                ) return IfcHumidifierTypeEnum::ADIABATICPAN;
    if(s=="ADIABATICWETTEDELEMENT"      ) return IfcHumidifierTypeEnum::ADIABATICWETTEDELEMENT;
    if(s=="ADIABATICATOMIZING"          ) return IfcHumidifierTypeEnum::ADIABATICATOMIZING;
    if(s=="ADIABATICULTRASONIC"         ) return IfcHumidifierTypeEnum::ADIABATICULTRASONIC;
    if(s=="ADIABATICRIGIDMEDIA"         ) return IfcHumidifierTypeEnum::ADIABATICRIGIDMEDIA;
    if(s=="ADIABATICCOMPRESSEDAIRNOZZLE") return IfcHumidifierTypeEnum::ADIABATICCOMPRESSEDAIRNOZZLE;
    if(s=="ASSISTEDELECTRIC"            ) return IfcHumidifierTypeEnum::ASSISTEDELECTRIC;
    if(s=="ASSISTEDNATURALGAS"          ) return IfcHumidifierTypeEnum::ASSISTEDNATURALGAS;
    if(s=="ASSISTEDPROPANE"             ) return IfcHumidifierTypeEnum::ASSISTEDPROPANE;
    if(s=="ASSISTEDBUTANE"              ) return IfcHumidifierTypeEnum::ASSISTEDBUTANE;
    if(s=="ASSISTEDSTEAM"               ) return IfcHumidifierTypeEnum::ASSISTEDSTEAM;
    if(s=="USERDEFINED"                 ) return IfcHumidifierTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                  ) return IfcHumidifierTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcInternalOrExternalEnum::ToString(IfcInternalOrExternalEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "INTERNAL","EXTERNAL","NOTDEFINED" };
    return names[v];
}
IfcInternalOrExternalEnum::IfcInternalOrExternalEnum IfcInternalOrExternalEnum::FromString(const std::string& s) {
    if(s=="INTERNAL"  ) return IfcInternalOrExternalEnum::INTERNAL;
    if(s=="EXTERNAL"  ) return IfcInternalOrExternalEnum::EXTERNAL;
    if(s=="NOTDEFINED") return IfcInternalOrExternalEnum::NOTDEFINED;
    throw;
}
std::string IfcInventoryTypeEnum::ToString(IfcInventoryTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "ASSETINVENTORY","SPACEINVENTORY","FURNITUREINVENTORY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcInventoryTypeEnum::IfcInventoryTypeEnum IfcInventoryTypeEnum::FromString(const std::string& s) {
    if(s=="ASSETINVENTORY"    ) return IfcInventoryTypeEnum::ASSETINVENTORY;
    if(s=="SPACEINVENTORY"    ) return IfcInventoryTypeEnum::SPACEINVENTORY;
    if(s=="FURNITUREINVENTORY") return IfcInventoryTypeEnum::FURNITUREINVENTORY;
    if(s=="USERDEFINED"       ) return IfcInventoryTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"        ) return IfcInventoryTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcJunctionBoxTypeEnum::ToString(IfcJunctionBoxTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcJunctionBoxTypeEnum::IfcJunctionBoxTypeEnum IfcJunctionBoxTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcJunctionBoxTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcJunctionBoxTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcLampTypeEnum::ToString(IfcLampTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "COMPACTFLUORESCENT","FLUORESCENT","HIGHPRESSUREMERCURY","HIGHPRESSURESODIUM","METALHALIDE","TUNGSTENFILAMENT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcLampTypeEnum::IfcLampTypeEnum IfcLampTypeEnum::FromString(const std::string& s) {
    if(s=="COMPACTFLUORESCENT" ) return IfcLampTypeEnum::COMPACTFLUORESCENT;
    if(s=="FLUORESCENT"        ) return IfcLampTypeEnum::FLUORESCENT;
    if(s=="HIGHPRESSUREMERCURY") return IfcLampTypeEnum::HIGHPRESSUREMERCURY;
    if(s=="HIGHPRESSURESODIUM" ) return IfcLampTypeEnum::HIGHPRESSURESODIUM;
    if(s=="METALHALIDE"        ) return IfcLampTypeEnum::METALHALIDE;
    if(s=="TUNGSTENFILAMENT"   ) return IfcLampTypeEnum::TUNGSTENFILAMENT;
    if(s=="USERDEFINED"        ) return IfcLampTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcLampTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcLayerSetDirectionEnum::ToString(IfcLayerSetDirectionEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "AXIS1","AXIS2","AXIS3" };
    return names[v];
}
IfcLayerSetDirectionEnum::IfcLayerSetDirectionEnum IfcLayerSetDirectionEnum::FromString(const std::string& s) {
    if(s=="AXIS1") return IfcLayerSetDirectionEnum::AXIS1;
    if(s=="AXIS2") return IfcLayerSetDirectionEnum::AXIS2;
    if(s=="AXIS3") return IfcLayerSetDirectionEnum::AXIS3;
    throw;
}
std::string IfcLightDistributionCurveEnum::ToString(IfcLightDistributionCurveEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "TYPE_A","TYPE_B","TYPE_C","NOTDEFINED" };
    return names[v];
}
IfcLightDistributionCurveEnum::IfcLightDistributionCurveEnum IfcLightDistributionCurveEnum::FromString(const std::string& s) {
    if(s=="TYPE_A"    ) return IfcLightDistributionCurveEnum::TYPE_A;
    if(s=="TYPE_B"    ) return IfcLightDistributionCurveEnum::TYPE_B;
    if(s=="TYPE_C"    ) return IfcLightDistributionCurveEnum::TYPE_C;
    if(s=="NOTDEFINED") return IfcLightDistributionCurveEnum::NOTDEFINED;
    throw;
}
std::string IfcLightEmissionSourceEnum::ToString(IfcLightEmissionSourceEnum v) {
    if ( v < 0 || v >= 11 ) throw;
    const char* names[] = { "COMPACTFLUORESCENT","FLUORESCENT","HIGHPRESSUREMERCURY","HIGHPRESSURESODIUM","LIGHTEMITTINGDIODE","LOWPRESSURESODIUM","LOWVOLTAGEHALOGEN","MAINVOLTAGEHALOGEN","METALHALIDE","TUNGSTENFILAMENT","NOTDEFINED" };
    return names[v];
}
IfcLightEmissionSourceEnum::IfcLightEmissionSourceEnum IfcLightEmissionSourceEnum::FromString(const std::string& s) {
    if(s=="COMPACTFLUORESCENT" ) return IfcLightEmissionSourceEnum::COMPACTFLUORESCENT;
    if(s=="FLUORESCENT"        ) return IfcLightEmissionSourceEnum::FLUORESCENT;
    if(s=="HIGHPRESSUREMERCURY") return IfcLightEmissionSourceEnum::HIGHPRESSUREMERCURY;
    if(s=="HIGHPRESSURESODIUM" ) return IfcLightEmissionSourceEnum::HIGHPRESSURESODIUM;
    if(s=="LIGHTEMITTINGDIODE" ) return IfcLightEmissionSourceEnum::LIGHTEMITTINGDIODE;
    if(s=="LOWPRESSURESODIUM"  ) return IfcLightEmissionSourceEnum::LOWPRESSURESODIUM;
    if(s=="LOWVOLTAGEHALOGEN"  ) return IfcLightEmissionSourceEnum::LOWVOLTAGEHALOGEN;
    if(s=="MAINVOLTAGEHALOGEN" ) return IfcLightEmissionSourceEnum::MAINVOLTAGEHALOGEN;
    if(s=="METALHALIDE"        ) return IfcLightEmissionSourceEnum::METALHALIDE;
    if(s=="TUNGSTENFILAMENT"   ) return IfcLightEmissionSourceEnum::TUNGSTENFILAMENT;
    if(s=="NOTDEFINED"         ) return IfcLightEmissionSourceEnum::NOTDEFINED;
    throw;
}
std::string IfcLightFixtureTypeEnum::ToString(IfcLightFixtureTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "POINTSOURCE","DIRECTIONSOURCE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcLightFixtureTypeEnum::IfcLightFixtureTypeEnum IfcLightFixtureTypeEnum::FromString(const std::string& s) {
    if(s=="POINTSOURCE"    ) return IfcLightFixtureTypeEnum::POINTSOURCE;
    if(s=="DIRECTIONSOURCE") return IfcLightFixtureTypeEnum::DIRECTIONSOURCE;
    if(s=="USERDEFINED"    ) return IfcLightFixtureTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"     ) return IfcLightFixtureTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcLoadGroupTypeEnum::ToString(IfcLoadGroupTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "LOAD_GROUP","LOAD_CASE","LOAD_COMBINATION_GROUP","LOAD_COMBINATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcLoadGroupTypeEnum::IfcLoadGroupTypeEnum IfcLoadGroupTypeEnum::FromString(const std::string& s) {
    if(s=="LOAD_GROUP"            ) return IfcLoadGroupTypeEnum::LOAD_GROUP;
    if(s=="LOAD_CASE"             ) return IfcLoadGroupTypeEnum::LOAD_CASE;
    if(s=="LOAD_COMBINATION_GROUP") return IfcLoadGroupTypeEnum::LOAD_COMBINATION_GROUP;
    if(s=="LOAD_COMBINATION"      ) return IfcLoadGroupTypeEnum::LOAD_COMBINATION;
    if(s=="USERDEFINED"           ) return IfcLoadGroupTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"            ) return IfcLoadGroupTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcLogicalOperatorEnum::ToString(IfcLogicalOperatorEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "LOGICALAND","LOGICALOR" };
    return names[v];
}
IfcLogicalOperatorEnum::IfcLogicalOperatorEnum IfcLogicalOperatorEnum::FromString(const std::string& s) {
    if(s=="LOGICALAND") return IfcLogicalOperatorEnum::LOGICALAND;
    if(s=="LOGICALOR" ) return IfcLogicalOperatorEnum::LOGICALOR;
    throw;
}
std::string IfcMemberTypeEnum::ToString(IfcMemberTypeEnum v) {
    if ( v < 0 || v >= 14 ) throw;
    const char* names[] = { "BRACE","CHORD","COLLAR","MEMBER","MULLION","PLATE","POST","PURLIN","RAFTER","STRINGER","STRUT","STUD","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcMemberTypeEnum::IfcMemberTypeEnum IfcMemberTypeEnum::FromString(const std::string& s) {
    if(s=="BRACE"      ) return IfcMemberTypeEnum::BRACE;
    if(s=="CHORD"      ) return IfcMemberTypeEnum::CHORD;
    if(s=="COLLAR"     ) return IfcMemberTypeEnum::COLLAR;
    if(s=="MEMBER"     ) return IfcMemberTypeEnum::MEMBER;
    if(s=="MULLION"    ) return IfcMemberTypeEnum::MULLION;
    if(s=="PLATE"      ) return IfcMemberTypeEnum::PLATE;
    if(s=="POST"       ) return IfcMemberTypeEnum::POST;
    if(s=="PURLIN"     ) return IfcMemberTypeEnum::PURLIN;
    if(s=="RAFTER"     ) return IfcMemberTypeEnum::RAFTER;
    if(s=="STRINGER"   ) return IfcMemberTypeEnum::STRINGER;
    if(s=="STRUT"      ) return IfcMemberTypeEnum::STRUT;
    if(s=="STUD"       ) return IfcMemberTypeEnum::STUD;
    if(s=="USERDEFINED") return IfcMemberTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcMemberTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcMotorConnectionTypeEnum::ToString(IfcMotorConnectionTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "BELTDRIVE","COUPLING","DIRECTDRIVE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcMotorConnectionTypeEnum::IfcMotorConnectionTypeEnum IfcMotorConnectionTypeEnum::FromString(const std::string& s) {
    if(s=="BELTDRIVE"  ) return IfcMotorConnectionTypeEnum::BELTDRIVE;
    if(s=="COUPLING"   ) return IfcMotorConnectionTypeEnum::COUPLING;
    if(s=="DIRECTDRIVE") return IfcMotorConnectionTypeEnum::DIRECTDRIVE;
    if(s=="USERDEFINED") return IfcMotorConnectionTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcMotorConnectionTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcNullStyle::ToString(IfcNullStyle v) {
    if ( v < 0 || v >= 1 ) throw;
    const char* names[] = { "IFC_NULL" };
    return names[v];
}
IfcNullStyle::IfcNullStyle IfcNullStyle::FromString(const std::string& s) {
    if(s=="IFC_NULL") return IfcNullStyle::IFC_NULL;
    throw;
}
std::string IfcObjectTypeEnum::ToString(IfcObjectTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "PRODUCT","PROCESS","CONTROL","RESOURCE","ACTOR","GROUP","PROJECT","NOTDEFINED" };
    return names[v];
}
IfcObjectTypeEnum::IfcObjectTypeEnum IfcObjectTypeEnum::FromString(const std::string& s) {
    if(s=="PRODUCT"   ) return IfcObjectTypeEnum::PRODUCT;
    if(s=="PROCESS"   ) return IfcObjectTypeEnum::PROCESS;
    if(s=="CONTROL"   ) return IfcObjectTypeEnum::CONTROL;
    if(s=="RESOURCE"  ) return IfcObjectTypeEnum::RESOURCE;
    if(s=="ACTOR"     ) return IfcObjectTypeEnum::ACTOR;
    if(s=="GROUP"     ) return IfcObjectTypeEnum::GROUP;
    if(s=="PROJECT"   ) return IfcObjectTypeEnum::PROJECT;
    if(s=="NOTDEFINED") return IfcObjectTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcObjectiveEnum::ToString(IfcObjectiveEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "CODECOMPLIANCE","DESIGNINTENT","HEALTHANDSAFETY","REQUIREMENT","SPECIFICATION","TRIGGERCONDITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcObjectiveEnum::IfcObjectiveEnum IfcObjectiveEnum::FromString(const std::string& s) {
    if(s=="CODECOMPLIANCE"  ) return IfcObjectiveEnum::CODECOMPLIANCE;
    if(s=="DESIGNINTENT"    ) return IfcObjectiveEnum::DESIGNINTENT;
    if(s=="HEALTHANDSAFETY" ) return IfcObjectiveEnum::HEALTHANDSAFETY;
    if(s=="REQUIREMENT"     ) return IfcObjectiveEnum::REQUIREMENT;
    if(s=="SPECIFICATION"   ) return IfcObjectiveEnum::SPECIFICATION;
    if(s=="TRIGGERCONDITION") return IfcObjectiveEnum::TRIGGERCONDITION;
    if(s=="USERDEFINED"     ) return IfcObjectiveEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcObjectiveEnum::NOTDEFINED;
    throw;
}
std::string IfcOccupantTypeEnum::ToString(IfcOccupantTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "ASSIGNEE","ASSIGNOR","LESSEE","LESSOR","LETTINGAGENT","OWNER","TENANT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcOccupantTypeEnum::IfcOccupantTypeEnum IfcOccupantTypeEnum::FromString(const std::string& s) {
    if(s=="ASSIGNEE"    ) return IfcOccupantTypeEnum::ASSIGNEE;
    if(s=="ASSIGNOR"    ) return IfcOccupantTypeEnum::ASSIGNOR;
    if(s=="LESSEE"      ) return IfcOccupantTypeEnum::LESSEE;
    if(s=="LESSOR"      ) return IfcOccupantTypeEnum::LESSOR;
    if(s=="LETTINGAGENT") return IfcOccupantTypeEnum::LETTINGAGENT;
    if(s=="OWNER"       ) return IfcOccupantTypeEnum::OWNER;
    if(s=="TENANT"      ) return IfcOccupantTypeEnum::TENANT;
    if(s=="USERDEFINED" ) return IfcOccupantTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"  ) return IfcOccupantTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcOutletTypeEnum::ToString(IfcOutletTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "AUDIOVISUALOUTLET","COMMUNICATIONSOUTLET","POWEROUTLET","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcOutletTypeEnum::IfcOutletTypeEnum IfcOutletTypeEnum::FromString(const std::string& s) {
    if(s=="AUDIOVISUALOUTLET"   ) return IfcOutletTypeEnum::AUDIOVISUALOUTLET;
    if(s=="COMMUNICATIONSOUTLET") return IfcOutletTypeEnum::COMMUNICATIONSOUTLET;
    if(s=="POWEROUTLET"         ) return IfcOutletTypeEnum::POWEROUTLET;
    if(s=="USERDEFINED"         ) return IfcOutletTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"          ) return IfcOutletTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcPermeableCoveringOperationEnum::ToString(IfcPermeableCoveringOperationEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "GRILL","LOUVER","SCREEN","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperationEnum IfcPermeableCoveringOperationEnum::FromString(const std::string& s) {
    if(s=="GRILL"      ) return IfcPermeableCoveringOperationEnum::GRILL;
    if(s=="LOUVER"     ) return IfcPermeableCoveringOperationEnum::LOUVER;
    if(s=="SCREEN"     ) return IfcPermeableCoveringOperationEnum::SCREEN;
    if(s=="USERDEFINED") return IfcPermeableCoveringOperationEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcPermeableCoveringOperationEnum::NOTDEFINED;
    throw;
}
std::string IfcPhysicalOrVirtualEnum::ToString(IfcPhysicalOrVirtualEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "PHYSICAL","VIRTUAL","NOTDEFINED" };
    return names[v];
}
IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtualEnum IfcPhysicalOrVirtualEnum::FromString(const std::string& s) {
    if(s=="PHYSICAL"  ) return IfcPhysicalOrVirtualEnum::PHYSICAL;
    if(s=="VIRTUAL"   ) return IfcPhysicalOrVirtualEnum::VIRTUAL;
    if(s=="NOTDEFINED") return IfcPhysicalOrVirtualEnum::NOTDEFINED;
    throw;
}
std::string IfcPileConstructionEnum::ToString(IfcPileConstructionEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "CAST_IN_PLACE","COMPOSITE","PRECAST_CONCRETE","PREFAB_STEEL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPileConstructionEnum::IfcPileConstructionEnum IfcPileConstructionEnum::FromString(const std::string& s) {
    if(s=="CAST_IN_PLACE"   ) return IfcPileConstructionEnum::CAST_IN_PLACE;
    if(s=="COMPOSITE"       ) return IfcPileConstructionEnum::COMPOSITE;
    if(s=="PRECAST_CONCRETE") return IfcPileConstructionEnum::PRECAST_CONCRETE;
    if(s=="PREFAB_STEEL"    ) return IfcPileConstructionEnum::PREFAB_STEEL;
    if(s=="USERDEFINED"     ) return IfcPileConstructionEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcPileConstructionEnum::NOTDEFINED;
    throw;
}
std::string IfcPileTypeEnum::ToString(IfcPileTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "COHESION","FRICTION","SUPPORT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPileTypeEnum::IfcPileTypeEnum IfcPileTypeEnum::FromString(const std::string& s) {
    if(s=="COHESION"   ) return IfcPileTypeEnum::COHESION;
    if(s=="FRICTION"   ) return IfcPileTypeEnum::FRICTION;
    if(s=="SUPPORT"    ) return IfcPileTypeEnum::SUPPORT;
    if(s=="USERDEFINED") return IfcPileTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcPileTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcPipeFittingTypeEnum::ToString(IfcPipeFittingTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "BEND","CONNECTOR","ENTRY","EXIT","JUNCTION","OBSTRUCTION","TRANSITION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPipeFittingTypeEnum::IfcPipeFittingTypeEnum IfcPipeFittingTypeEnum::FromString(const std::string& s) {
    if(s=="BEND"       ) return IfcPipeFittingTypeEnum::BEND;
    if(s=="CONNECTOR"  ) return IfcPipeFittingTypeEnum::CONNECTOR;
    if(s=="ENTRY"      ) return IfcPipeFittingTypeEnum::ENTRY;
    if(s=="EXIT"       ) return IfcPipeFittingTypeEnum::EXIT;
    if(s=="JUNCTION"   ) return IfcPipeFittingTypeEnum::JUNCTION;
    if(s=="OBSTRUCTION") return IfcPipeFittingTypeEnum::OBSTRUCTION;
    if(s=="TRANSITION" ) return IfcPipeFittingTypeEnum::TRANSITION;
    if(s=="USERDEFINED") return IfcPipeFittingTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcPipeFittingTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcPipeSegmentTypeEnum::ToString(IfcPipeSegmentTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "FLEXIBLESEGMENT","RIGIDSEGMENT","GUTTER","SPOOL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPipeSegmentTypeEnum::IfcPipeSegmentTypeEnum IfcPipeSegmentTypeEnum::FromString(const std::string& s) {
    if(s=="FLEXIBLESEGMENT") return IfcPipeSegmentTypeEnum::FLEXIBLESEGMENT;
    if(s=="RIGIDSEGMENT"   ) return IfcPipeSegmentTypeEnum::RIGIDSEGMENT;
    if(s=="GUTTER"         ) return IfcPipeSegmentTypeEnum::GUTTER;
    if(s=="SPOOL"          ) return IfcPipeSegmentTypeEnum::SPOOL;
    if(s=="USERDEFINED"    ) return IfcPipeSegmentTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"     ) return IfcPipeSegmentTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcPlateTypeEnum::ToString(IfcPlateTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "CURTAIN_PANEL","SHEET","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPlateTypeEnum::IfcPlateTypeEnum IfcPlateTypeEnum::FromString(const std::string& s) {
    if(s=="CURTAIN_PANEL") return IfcPlateTypeEnum::CURTAIN_PANEL;
    if(s=="SHEET"        ) return IfcPlateTypeEnum::SHEET;
    if(s=="USERDEFINED"  ) return IfcPlateTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"   ) return IfcPlateTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcProcedureTypeEnum::ToString(IfcProcedureTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "ADVICE_CAUTION","ADVICE_NOTE","ADVICE_WARNING","CALIBRATION","DIAGNOSTIC","SHUTDOWN","STARTUP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProcedureTypeEnum::IfcProcedureTypeEnum IfcProcedureTypeEnum::FromString(const std::string& s) {
    if(s=="ADVICE_CAUTION") return IfcProcedureTypeEnum::ADVICE_CAUTION;
    if(s=="ADVICE_NOTE"   ) return IfcProcedureTypeEnum::ADVICE_NOTE;
    if(s=="ADVICE_WARNING") return IfcProcedureTypeEnum::ADVICE_WARNING;
    if(s=="CALIBRATION"   ) return IfcProcedureTypeEnum::CALIBRATION;
    if(s=="DIAGNOSTIC"    ) return IfcProcedureTypeEnum::DIAGNOSTIC;
    if(s=="SHUTDOWN"      ) return IfcProcedureTypeEnum::SHUTDOWN;
    if(s=="STARTUP"       ) return IfcProcedureTypeEnum::STARTUP;
    if(s=="USERDEFINED"   ) return IfcProcedureTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"    ) return IfcProcedureTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcProfileTypeEnum::ToString(IfcProfileTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "CURVE","AREA" };
    return names[v];
}
IfcProfileTypeEnum::IfcProfileTypeEnum IfcProfileTypeEnum::FromString(const std::string& s) {
    if(s=="CURVE") return IfcProfileTypeEnum::CURVE;
    if(s=="AREA" ) return IfcProfileTypeEnum::AREA;
    throw;
}
std::string IfcProjectOrderRecordTypeEnum::ToString(IfcProjectOrderRecordTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "CHANGE","MAINTENANCE","MOVE","PURCHASE","WORK","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordTypeEnum IfcProjectOrderRecordTypeEnum::FromString(const std::string& s) {
    if(s=="CHANGE"     ) return IfcProjectOrderRecordTypeEnum::CHANGE;
    if(s=="MAINTENANCE") return IfcProjectOrderRecordTypeEnum::MAINTENANCE;
    if(s=="MOVE"       ) return IfcProjectOrderRecordTypeEnum::MOVE;
    if(s=="PURCHASE"   ) return IfcProjectOrderRecordTypeEnum::PURCHASE;
    if(s=="WORK"       ) return IfcProjectOrderRecordTypeEnum::WORK;
    if(s=="USERDEFINED") return IfcProjectOrderRecordTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcProjectOrderRecordTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcProjectOrderTypeEnum::ToString(IfcProjectOrderTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "CHANGEORDER","MAINTENANCEWORKORDER","MOVEORDER","PURCHASEORDER","WORKORDER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProjectOrderTypeEnum::IfcProjectOrderTypeEnum IfcProjectOrderTypeEnum::FromString(const std::string& s) {
    if(s=="CHANGEORDER"         ) return IfcProjectOrderTypeEnum::CHANGEORDER;
    if(s=="MAINTENANCEWORKORDER") return IfcProjectOrderTypeEnum::MAINTENANCEWORKORDER;
    if(s=="MOVEORDER"           ) return IfcProjectOrderTypeEnum::MOVEORDER;
    if(s=="PURCHASEORDER"       ) return IfcProjectOrderTypeEnum::PURCHASEORDER;
    if(s=="WORKORDER"           ) return IfcProjectOrderTypeEnum::WORKORDER;
    if(s=="USERDEFINED"         ) return IfcProjectOrderTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"          ) return IfcProjectOrderTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcProjectedOrTrueLengthEnum::ToString(IfcProjectedOrTrueLengthEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "PROJECTED_LENGTH","TRUE_LENGTH" };
    return names[v];
}
IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum IfcProjectedOrTrueLengthEnum::FromString(const std::string& s) {
    if(s=="PROJECTED_LENGTH") return IfcProjectedOrTrueLengthEnum::PROJECTED_LENGTH;
    if(s=="TRUE_LENGTH"     ) return IfcProjectedOrTrueLengthEnum::TRUE_LENGTH;
    throw;
}
std::string IfcPropertySourceEnum::ToString(IfcPropertySourceEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "DESIGN","DESIGNMAXIMUM","DESIGNMINIMUM","SIMULATED","ASBUILT","COMMISSIONING","MEASURED","USERDEFINED","NOTKNOWN" };
    return names[v];
}
IfcPropertySourceEnum::IfcPropertySourceEnum IfcPropertySourceEnum::FromString(const std::string& s) {
    if(s=="DESIGN"       ) return IfcPropertySourceEnum::DESIGN;
    if(s=="DESIGNMAXIMUM") return IfcPropertySourceEnum::DESIGNMAXIMUM;
    if(s=="DESIGNMINIMUM") return IfcPropertySourceEnum::DESIGNMINIMUM;
    if(s=="SIMULATED"    ) return IfcPropertySourceEnum::SIMULATED;
    if(s=="ASBUILT"      ) return IfcPropertySourceEnum::ASBUILT;
    if(s=="COMMISSIONING") return IfcPropertySourceEnum::COMMISSIONING;
    if(s=="MEASURED"     ) return IfcPropertySourceEnum::MEASURED;
    if(s=="USERDEFINED"  ) return IfcPropertySourceEnum::USERDEFINED;
    if(s=="NOTKNOWN"     ) return IfcPropertySourceEnum::NOTKNOWN;
    throw;
}
std::string IfcProtectiveDeviceTypeEnum::ToString(IfcProtectiveDeviceTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "FUSEDISCONNECTOR","CIRCUITBREAKER","EARTHFAILUREDEVICE","RESIDUALCURRENTCIRCUITBREAKER","RESIDUALCURRENTSWITCH","VARISTOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceTypeEnum IfcProtectiveDeviceTypeEnum::FromString(const std::string& s) {
    if(s=="FUSEDISCONNECTOR"             ) return IfcProtectiveDeviceTypeEnum::FUSEDISCONNECTOR;
    if(s=="CIRCUITBREAKER"               ) return IfcProtectiveDeviceTypeEnum::CIRCUITBREAKER;
    if(s=="EARTHFAILUREDEVICE"           ) return IfcProtectiveDeviceTypeEnum::EARTHFAILUREDEVICE;
    if(s=="RESIDUALCURRENTCIRCUITBREAKER") return IfcProtectiveDeviceTypeEnum::RESIDUALCURRENTCIRCUITBREAKER;
    if(s=="RESIDUALCURRENTSWITCH"        ) return IfcProtectiveDeviceTypeEnum::RESIDUALCURRENTSWITCH;
    if(s=="VARISTOR"                     ) return IfcProtectiveDeviceTypeEnum::VARISTOR;
    if(s=="USERDEFINED"                  ) return IfcProtectiveDeviceTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                   ) return IfcProtectiveDeviceTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcPumpTypeEnum::ToString(IfcPumpTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "CIRCULATOR","ENDSUCTION","SPLITCASE","VERTICALINLINE","VERTICALTURBINE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcPumpTypeEnum::IfcPumpTypeEnum IfcPumpTypeEnum::FromString(const std::string& s) {
    if(s=="CIRCULATOR"     ) return IfcPumpTypeEnum::CIRCULATOR;
    if(s=="ENDSUCTION"     ) return IfcPumpTypeEnum::ENDSUCTION;
    if(s=="SPLITCASE"      ) return IfcPumpTypeEnum::SPLITCASE;
    if(s=="VERTICALINLINE" ) return IfcPumpTypeEnum::VERTICALINLINE;
    if(s=="VERTICALTURBINE") return IfcPumpTypeEnum::VERTICALTURBINE;
    if(s=="USERDEFINED"    ) return IfcPumpTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"     ) return IfcPumpTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcRailingTypeEnum::ToString(IfcRailingTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "HANDRAIL","GUARDRAIL","BALUSTRADE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcRailingTypeEnum::IfcRailingTypeEnum IfcRailingTypeEnum::FromString(const std::string& s) {
    if(s=="HANDRAIL"   ) return IfcRailingTypeEnum::HANDRAIL;
    if(s=="GUARDRAIL"  ) return IfcRailingTypeEnum::GUARDRAIL;
    if(s=="BALUSTRADE" ) return IfcRailingTypeEnum::BALUSTRADE;
    if(s=="USERDEFINED") return IfcRailingTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcRailingTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcRampFlightTypeEnum::ToString(IfcRampFlightTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "STRAIGHT","SPIRAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcRampFlightTypeEnum::IfcRampFlightTypeEnum IfcRampFlightTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT"   ) return IfcRampFlightTypeEnum::STRAIGHT;
    if(s=="SPIRAL"     ) return IfcRampFlightTypeEnum::SPIRAL;
    if(s=="USERDEFINED") return IfcRampFlightTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcRampFlightTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcRampTypeEnum::ToString(IfcRampTypeEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "STRAIGHT_RUN_RAMP","TWO_STRAIGHT_RUN_RAMP","QUARTER_TURN_RAMP","TWO_QUARTER_TURN_RAMP","HALF_TURN_RAMP","SPIRAL_RAMP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcRampTypeEnum::IfcRampTypeEnum IfcRampTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT_RUN_RAMP"    ) return IfcRampTypeEnum::STRAIGHT_RUN_RAMP;
    if(s=="TWO_STRAIGHT_RUN_RAMP") return IfcRampTypeEnum::TWO_STRAIGHT_RUN_RAMP;
    if(s=="QUARTER_TURN_RAMP"    ) return IfcRampTypeEnum::QUARTER_TURN_RAMP;
    if(s=="TWO_QUARTER_TURN_RAMP") return IfcRampTypeEnum::TWO_QUARTER_TURN_RAMP;
    if(s=="HALF_TURN_RAMP"       ) return IfcRampTypeEnum::HALF_TURN_RAMP;
    if(s=="SPIRAL_RAMP"          ) return IfcRampTypeEnum::SPIRAL_RAMP;
    if(s=="USERDEFINED"          ) return IfcRampTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"           ) return IfcRampTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcReflectanceMethodEnum::ToString(IfcReflectanceMethodEnum v) {
    if ( v < 0 || v >= 10 ) throw;
    const char* names[] = { "BLINN","FLAT","GLASS","MATT","METAL","MIRROR","PHONG","PLASTIC","STRAUSS","NOTDEFINED" };
    return names[v];
}
IfcReflectanceMethodEnum::IfcReflectanceMethodEnum IfcReflectanceMethodEnum::FromString(const std::string& s) {
    if(s=="BLINN"     ) return IfcReflectanceMethodEnum::BLINN;
    if(s=="FLAT"      ) return IfcReflectanceMethodEnum::FLAT;
    if(s=="GLASS"     ) return IfcReflectanceMethodEnum::GLASS;
    if(s=="MATT"      ) return IfcReflectanceMethodEnum::MATT;
    if(s=="METAL"     ) return IfcReflectanceMethodEnum::METAL;
    if(s=="MIRROR"    ) return IfcReflectanceMethodEnum::MIRROR;
    if(s=="PHONG"     ) return IfcReflectanceMethodEnum::PHONG;
    if(s=="PLASTIC"   ) return IfcReflectanceMethodEnum::PLASTIC;
    if(s=="STRAUSS"   ) return IfcReflectanceMethodEnum::STRAUSS;
    if(s=="NOTDEFINED") return IfcReflectanceMethodEnum::NOTDEFINED;
    throw;
}
std::string IfcReinforcingBarRoleEnum::ToString(IfcReinforcingBarRoleEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "MAIN","SHEAR","LIGATURE","STUD","PUNCHING","EDGE","RING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum IfcReinforcingBarRoleEnum::FromString(const std::string& s) {
    if(s=="MAIN"       ) return IfcReinforcingBarRoleEnum::MAIN;
    if(s=="SHEAR"      ) return IfcReinforcingBarRoleEnum::SHEAR;
    if(s=="LIGATURE"   ) return IfcReinforcingBarRoleEnum::LIGATURE;
    if(s=="STUD"       ) return IfcReinforcingBarRoleEnum::STUD;
    if(s=="PUNCHING"   ) return IfcReinforcingBarRoleEnum::PUNCHING;
    if(s=="EDGE"       ) return IfcReinforcingBarRoleEnum::EDGE;
    if(s=="RING"       ) return IfcReinforcingBarRoleEnum::RING;
    if(s=="USERDEFINED") return IfcReinforcingBarRoleEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcReinforcingBarRoleEnum::NOTDEFINED;
    throw;
}
std::string IfcReinforcingBarSurfaceEnum::ToString(IfcReinforcingBarSurfaceEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "PLAIN","TEXTURED" };
    return names[v];
}
IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum IfcReinforcingBarSurfaceEnum::FromString(const std::string& s) {
    if(s=="PLAIN"   ) return IfcReinforcingBarSurfaceEnum::PLAIN;
    if(s=="TEXTURED") return IfcReinforcingBarSurfaceEnum::TEXTURED;
    throw;
}
std::string IfcResourceConsumptionEnum::ToString(IfcResourceConsumptionEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "CONSUMED","PARTIALLYCONSUMED","NOTCONSUMED","OCCUPIED","PARTIALLYOCCUPIED","NOTOCCUPIED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcResourceConsumptionEnum::IfcResourceConsumptionEnum IfcResourceConsumptionEnum::FromString(const std::string& s) {
    if(s=="CONSUMED"         ) return IfcResourceConsumptionEnum::CONSUMED;
    if(s=="PARTIALLYCONSUMED") return IfcResourceConsumptionEnum::PARTIALLYCONSUMED;
    if(s=="NOTCONSUMED"      ) return IfcResourceConsumptionEnum::NOTCONSUMED;
    if(s=="OCCUPIED"         ) return IfcResourceConsumptionEnum::OCCUPIED;
    if(s=="PARTIALLYOCCUPIED") return IfcResourceConsumptionEnum::PARTIALLYOCCUPIED;
    if(s=="NOTOCCUPIED"      ) return IfcResourceConsumptionEnum::NOTOCCUPIED;
    if(s=="USERDEFINED"      ) return IfcResourceConsumptionEnum::USERDEFINED;
    if(s=="NOTDEFINED"       ) return IfcResourceConsumptionEnum::NOTDEFINED;
    throw;
}
std::string IfcRibPlateDirectionEnum::ToString(IfcRibPlateDirectionEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "DIRECTION_X","DIRECTION_Y" };
    return names[v];
}
IfcRibPlateDirectionEnum::IfcRibPlateDirectionEnum IfcRibPlateDirectionEnum::FromString(const std::string& s) {
    if(s=="DIRECTION_X") return IfcRibPlateDirectionEnum::DIRECTION_X;
    if(s=="DIRECTION_Y") return IfcRibPlateDirectionEnum::DIRECTION_Y;
    throw;
}
std::string IfcRoleEnum::ToString(IfcRoleEnum v) {
    if ( v < 0 || v >= 23 ) throw;
    const char* names[] = { "SUPPLIER","MANUFACTURER","CONTRACTOR","SUBCONTRACTOR","ARCHITECT","STRUCTURALENGINEER","COSTENGINEER","CLIENT","BUILDINGOWNER","BUILDINGOPERATOR","MECHANICALENGINEER","ELECTRICALENGINEER","PROJECTMANAGER","FACILITIESMANAGER","CIVILENGINEER","COMISSIONINGENGINEER","ENGINEER","OWNER","CONSULTANT","CONSTRUCTIONMANAGER","FIELDCONSTRUCTIONMANAGER","RESELLER","USERDEFINED" };
    return names[v];
}
IfcRoleEnum::IfcRoleEnum IfcRoleEnum::FromString(const std::string& s) {
    if(s=="SUPPLIER"                ) return IfcRoleEnum::SUPPLIER;
    if(s=="MANUFACTURER"            ) return IfcRoleEnum::MANUFACTURER;
    if(s=="CONTRACTOR"              ) return IfcRoleEnum::CONTRACTOR;
    if(s=="SUBCONTRACTOR"           ) return IfcRoleEnum::SUBCONTRACTOR;
    if(s=="ARCHITECT"               ) return IfcRoleEnum::ARCHITECT;
    if(s=="STRUCTURALENGINEER"      ) return IfcRoleEnum::STRUCTURALENGINEER;
    if(s=="COSTENGINEER"            ) return IfcRoleEnum::COSTENGINEER;
    if(s=="CLIENT"                  ) return IfcRoleEnum::CLIENT;
    if(s=="BUILDINGOWNER"           ) return IfcRoleEnum::BUILDINGOWNER;
    if(s=="BUILDINGOPERATOR"        ) return IfcRoleEnum::BUILDINGOPERATOR;
    if(s=="MECHANICALENGINEER"      ) return IfcRoleEnum::MECHANICALENGINEER;
    if(s=="ELECTRICALENGINEER"      ) return IfcRoleEnum::ELECTRICALENGINEER;
    if(s=="PROJECTMANAGER"          ) return IfcRoleEnum::PROJECTMANAGER;
    if(s=="FACILITIESMANAGER"       ) return IfcRoleEnum::FACILITIESMANAGER;
    if(s=="CIVILENGINEER"           ) return IfcRoleEnum::CIVILENGINEER;
    if(s=="COMISSIONINGENGINEER"    ) return IfcRoleEnum::COMISSIONINGENGINEER;
    if(s=="ENGINEER"                ) return IfcRoleEnum::ENGINEER;
    if(s=="OWNER"                   ) return IfcRoleEnum::OWNER;
    if(s=="CONSULTANT"              ) return IfcRoleEnum::CONSULTANT;
    if(s=="CONSTRUCTIONMANAGER"     ) return IfcRoleEnum::CONSTRUCTIONMANAGER;
    if(s=="FIELDCONSTRUCTIONMANAGER") return IfcRoleEnum::FIELDCONSTRUCTIONMANAGER;
    if(s=="RESELLER"                ) return IfcRoleEnum::RESELLER;
    if(s=="USERDEFINED"             ) return IfcRoleEnum::USERDEFINED;
    throw;
}
std::string IfcRoofTypeEnum::ToString(IfcRoofTypeEnum v) {
    if ( v < 0 || v >= 14 ) throw;
    const char* names[] = { "FLAT_ROOF","SHED_ROOF","GABLE_ROOF","HIP_ROOF","HIPPED_GABLE_ROOF","GAMBREL_ROOF","MANSARD_ROOF","BARREL_ROOF","RAINBOW_ROOF","BUTTERFLY_ROOF","PAVILION_ROOF","DOME_ROOF","FREEFORM","NOTDEFINED" };
    return names[v];
}
IfcRoofTypeEnum::IfcRoofTypeEnum IfcRoofTypeEnum::FromString(const std::string& s) {
    if(s=="FLAT_ROOF"        ) return IfcRoofTypeEnum::FLAT_ROOF;
    if(s=="SHED_ROOF"        ) return IfcRoofTypeEnum::SHED_ROOF;
    if(s=="GABLE_ROOF"       ) return IfcRoofTypeEnum::GABLE_ROOF;
    if(s=="HIP_ROOF"         ) return IfcRoofTypeEnum::HIP_ROOF;
    if(s=="HIPPED_GABLE_ROOF") return IfcRoofTypeEnum::HIPPED_GABLE_ROOF;
    if(s=="GAMBREL_ROOF"     ) return IfcRoofTypeEnum::GAMBREL_ROOF;
    if(s=="MANSARD_ROOF"     ) return IfcRoofTypeEnum::MANSARD_ROOF;
    if(s=="BARREL_ROOF"      ) return IfcRoofTypeEnum::BARREL_ROOF;
    if(s=="RAINBOW_ROOF"     ) return IfcRoofTypeEnum::RAINBOW_ROOF;
    if(s=="BUTTERFLY_ROOF"   ) return IfcRoofTypeEnum::BUTTERFLY_ROOF;
    if(s=="PAVILION_ROOF"    ) return IfcRoofTypeEnum::PAVILION_ROOF;
    if(s=="DOME_ROOF"        ) return IfcRoofTypeEnum::DOME_ROOF;
    if(s=="FREEFORM"         ) return IfcRoofTypeEnum::FREEFORM;
    if(s=="NOTDEFINED"       ) return IfcRoofTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcSIPrefix::ToString(IfcSIPrefix v) {
    if ( v < 0 || v >= 16 ) throw;
    const char* names[] = { "EXA","PETA","TERA","GIGA","MEGA","KILO","HECTO","DECA","DECI","CENTI","MILLI","MICRO","NANO","PICO","FEMTO","ATTO" };
    return names[v];
}
IfcSIPrefix::IfcSIPrefix IfcSIPrefix::FromString(const std::string& s) {
    if(s=="EXA"  ) return IfcSIPrefix::EXA;
    if(s=="PETA" ) return IfcSIPrefix::PETA;
    if(s=="TERA" ) return IfcSIPrefix::TERA;
    if(s=="GIGA" ) return IfcSIPrefix::GIGA;
    if(s=="MEGA" ) return IfcSIPrefix::MEGA;
    if(s=="KILO" ) return IfcSIPrefix::KILO;
    if(s=="HECTO") return IfcSIPrefix::HECTO;
    if(s=="DECA" ) return IfcSIPrefix::DECA;
    if(s=="DECI" ) return IfcSIPrefix::DECI;
    if(s=="CENTI") return IfcSIPrefix::CENTI;
    if(s=="MILLI") return IfcSIPrefix::MILLI;
    if(s=="MICRO") return IfcSIPrefix::MICRO;
    if(s=="NANO" ) return IfcSIPrefix::NANO;
    if(s=="PICO" ) return IfcSIPrefix::PICO;
    if(s=="FEMTO") return IfcSIPrefix::FEMTO;
    if(s=="ATTO" ) return IfcSIPrefix::ATTO;
    throw;
}
std::string IfcSIUnitName::ToString(IfcSIUnitName v) {
    if ( v < 0 || v >= 30 ) throw;
    const char* names[] = { "AMPERE","BECQUEREL","CANDELA","COULOMB","CUBIC_METRE","DEGREE_CELSIUS","FARAD","GRAM","GRAY","HENRY","HERTZ","JOULE","KELVIN","LUMEN","LUX","METRE","MOLE","NEWTON","OHM","PASCAL","RADIAN","SECOND","SIEMENS","SIEVERT","SQUARE_METRE","STERADIAN","TESLA","VOLT","WATT","WEBER" };
    return names[v];
}
IfcSIUnitName::IfcSIUnitName IfcSIUnitName::FromString(const std::string& s) {
    if(s=="AMPERE"        ) return IfcSIUnitName::AMPERE;
    if(s=="BECQUEREL"     ) return IfcSIUnitName::BECQUEREL;
    if(s=="CANDELA"       ) return IfcSIUnitName::CANDELA;
    if(s=="COULOMB"       ) return IfcSIUnitName::COULOMB;
    if(s=="CUBIC_METRE"   ) return IfcSIUnitName::CUBIC_METRE;
    if(s=="DEGREE_CELSIUS") return IfcSIUnitName::DEGREE_CELSIUS;
    if(s=="FARAD"         ) return IfcSIUnitName::FARAD;
    if(s=="GRAM"          ) return IfcSIUnitName::GRAM;
    if(s=="GRAY"          ) return IfcSIUnitName::GRAY;
    if(s=="HENRY"         ) return IfcSIUnitName::HENRY;
    if(s=="HERTZ"         ) return IfcSIUnitName::HERTZ;
    if(s=="JOULE"         ) return IfcSIUnitName::JOULE;
    if(s=="KELVIN"        ) return IfcSIUnitName::KELVIN;
    if(s=="LUMEN"         ) return IfcSIUnitName::LUMEN;
    if(s=="LUX"           ) return IfcSIUnitName::LUX;
    if(s=="METRE"         ) return IfcSIUnitName::METRE;
    if(s=="MOLE"          ) return IfcSIUnitName::MOLE;
    if(s=="NEWTON"        ) return IfcSIUnitName::NEWTON;
    if(s=="OHM"           ) return IfcSIUnitName::OHM;
    if(s=="PASCAL"        ) return IfcSIUnitName::PASCAL;
    if(s=="RADIAN"        ) return IfcSIUnitName::RADIAN;
    if(s=="SECOND"        ) return IfcSIUnitName::SECOND;
    if(s=="SIEMENS"       ) return IfcSIUnitName::SIEMENS;
    if(s=="SIEVERT"       ) return IfcSIUnitName::SIEVERT;
    if(s=="SQUARE_METRE"  ) return IfcSIUnitName::SQUARE_METRE;
    if(s=="STERADIAN"     ) return IfcSIUnitName::STERADIAN;
    if(s=="TESLA"         ) return IfcSIUnitName::TESLA;
    if(s=="VOLT"          ) return IfcSIUnitName::VOLT;
    if(s=="WATT"          ) return IfcSIUnitName::WATT;
    if(s=="WEBER"         ) return IfcSIUnitName::WEBER;
    throw;
}
std::string IfcSanitaryTerminalTypeEnum::ToString(IfcSanitaryTerminalTypeEnum v) {
    if ( v < 0 || v >= 12 ) throw;
    const char* names[] = { "BATH","BIDET","CISTERN","SHOWER","SINK","SANITARYFOUNTAIN","TOILETPAN","URINAL","WASHHANDBASIN","WCSEAT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalTypeEnum IfcSanitaryTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="BATH"            ) return IfcSanitaryTerminalTypeEnum::BATH;
    if(s=="BIDET"           ) return IfcSanitaryTerminalTypeEnum::BIDET;
    if(s=="CISTERN"         ) return IfcSanitaryTerminalTypeEnum::CISTERN;
    if(s=="SHOWER"          ) return IfcSanitaryTerminalTypeEnum::SHOWER;
    if(s=="SINK"            ) return IfcSanitaryTerminalTypeEnum::SINK;
    if(s=="SANITARYFOUNTAIN") return IfcSanitaryTerminalTypeEnum::SANITARYFOUNTAIN;
    if(s=="TOILETPAN"       ) return IfcSanitaryTerminalTypeEnum::TOILETPAN;
    if(s=="URINAL"          ) return IfcSanitaryTerminalTypeEnum::URINAL;
    if(s=="WASHHANDBASIN"   ) return IfcSanitaryTerminalTypeEnum::WASHHANDBASIN;
    if(s=="WCSEAT"          ) return IfcSanitaryTerminalTypeEnum::WCSEAT;
    if(s=="USERDEFINED"     ) return IfcSanitaryTerminalTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcSanitaryTerminalTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcSectionTypeEnum::ToString(IfcSectionTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "UNIFORM","TAPERED" };
    return names[v];
}
IfcSectionTypeEnum::IfcSectionTypeEnum IfcSectionTypeEnum::FromString(const std::string& s) {
    if(s=="UNIFORM") return IfcSectionTypeEnum::UNIFORM;
    if(s=="TAPERED") return IfcSectionTypeEnum::TAPERED;
    throw;
}
std::string IfcSensorTypeEnum::ToString(IfcSensorTypeEnum v) {
    if ( v < 0 || v >= 15 ) throw;
    const char* names[] = { "CO2SENSOR","FIRESENSOR","FLOWSENSOR","GASSENSOR","HEATSENSOR","HUMIDITYSENSOR","LIGHTSENSOR","MOISTURESENSOR","MOVEMENTSENSOR","PRESSURESENSOR","SMOKESENSOR","SOUNDSENSOR","TEMPERATURESENSOR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSensorTypeEnum::IfcSensorTypeEnum IfcSensorTypeEnum::FromString(const std::string& s) {
    if(s=="CO2SENSOR"        ) return IfcSensorTypeEnum::CO2SENSOR;
    if(s=="FIRESENSOR"       ) return IfcSensorTypeEnum::FIRESENSOR;
    if(s=="FLOWSENSOR"       ) return IfcSensorTypeEnum::FLOWSENSOR;
    if(s=="GASSENSOR"        ) return IfcSensorTypeEnum::GASSENSOR;
    if(s=="HEATSENSOR"       ) return IfcSensorTypeEnum::HEATSENSOR;
    if(s=="HUMIDITYSENSOR"   ) return IfcSensorTypeEnum::HUMIDITYSENSOR;
    if(s=="LIGHTSENSOR"      ) return IfcSensorTypeEnum::LIGHTSENSOR;
    if(s=="MOISTURESENSOR"   ) return IfcSensorTypeEnum::MOISTURESENSOR;
    if(s=="MOVEMENTSENSOR"   ) return IfcSensorTypeEnum::MOVEMENTSENSOR;
    if(s=="PRESSURESENSOR"   ) return IfcSensorTypeEnum::PRESSURESENSOR;
    if(s=="SMOKESENSOR"      ) return IfcSensorTypeEnum::SMOKESENSOR;
    if(s=="SOUNDSENSOR"      ) return IfcSensorTypeEnum::SOUNDSENSOR;
    if(s=="TEMPERATURESENSOR") return IfcSensorTypeEnum::TEMPERATURESENSOR;
    if(s=="USERDEFINED"      ) return IfcSensorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"       ) return IfcSensorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcSequenceEnum::ToString(IfcSequenceEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "START_START","START_FINISH","FINISH_START","FINISH_FINISH","NOTDEFINED" };
    return names[v];
}
IfcSequenceEnum::IfcSequenceEnum IfcSequenceEnum::FromString(const std::string& s) {
    if(s=="START_START"  ) return IfcSequenceEnum::START_START;
    if(s=="START_FINISH" ) return IfcSequenceEnum::START_FINISH;
    if(s=="FINISH_START" ) return IfcSequenceEnum::FINISH_START;
    if(s=="FINISH_FINISH") return IfcSequenceEnum::FINISH_FINISH;
    if(s=="NOTDEFINED"   ) return IfcSequenceEnum::NOTDEFINED;
    throw;
}
std::string IfcServiceLifeFactorTypeEnum::ToString(IfcServiceLifeFactorTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "A_QUALITYOFCOMPONENTS","B_DESIGNLEVEL","C_WORKEXECUTIONLEVEL","D_INDOORENVIRONMENT","E_OUTDOORENVIRONMENT","F_INUSECONDITIONS","G_MAINTENANCELEVEL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorTypeEnum IfcServiceLifeFactorTypeEnum::FromString(const std::string& s) {
    if(s=="A_QUALITYOFCOMPONENTS") return IfcServiceLifeFactorTypeEnum::A_QUALITYOFCOMPONENTS;
    if(s=="B_DESIGNLEVEL"        ) return IfcServiceLifeFactorTypeEnum::B_DESIGNLEVEL;
    if(s=="C_WORKEXECUTIONLEVEL" ) return IfcServiceLifeFactorTypeEnum::C_WORKEXECUTIONLEVEL;
    if(s=="D_INDOORENVIRONMENT"  ) return IfcServiceLifeFactorTypeEnum::D_INDOORENVIRONMENT;
    if(s=="E_OUTDOORENVIRONMENT" ) return IfcServiceLifeFactorTypeEnum::E_OUTDOORENVIRONMENT;
    if(s=="F_INUSECONDITIONS"    ) return IfcServiceLifeFactorTypeEnum::F_INUSECONDITIONS;
    if(s=="G_MAINTENANCELEVEL"   ) return IfcServiceLifeFactorTypeEnum::G_MAINTENANCELEVEL;
    if(s=="USERDEFINED"          ) return IfcServiceLifeFactorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"           ) return IfcServiceLifeFactorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcServiceLifeTypeEnum::ToString(IfcServiceLifeTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "ACTUALSERVICELIFE","EXPECTEDSERVICELIFE","OPTIMISTICREFERENCESERVICELIFE","PESSIMISTICREFERENCESERVICELIFE","REFERENCESERVICELIFE" };
    return names[v];
}
IfcServiceLifeTypeEnum::IfcServiceLifeTypeEnum IfcServiceLifeTypeEnum::FromString(const std::string& s) {
    if(s=="ACTUALSERVICELIFE"              ) return IfcServiceLifeTypeEnum::ACTUALSERVICELIFE;
    if(s=="EXPECTEDSERVICELIFE"            ) return IfcServiceLifeTypeEnum::EXPECTEDSERVICELIFE;
    if(s=="OPTIMISTICREFERENCESERVICELIFE" ) return IfcServiceLifeTypeEnum::OPTIMISTICREFERENCESERVICELIFE;
    if(s=="PESSIMISTICREFERENCESERVICELIFE") return IfcServiceLifeTypeEnum::PESSIMISTICREFERENCESERVICELIFE;
    if(s=="REFERENCESERVICELIFE"           ) return IfcServiceLifeTypeEnum::REFERENCESERVICELIFE;
    throw;
}
std::string IfcSlabTypeEnum::ToString(IfcSlabTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "FLOOR","ROOF","LANDING","BASESLAB","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSlabTypeEnum::IfcSlabTypeEnum IfcSlabTypeEnum::FromString(const std::string& s) {
    if(s=="FLOOR"      ) return IfcSlabTypeEnum::FLOOR;
    if(s=="ROOF"       ) return IfcSlabTypeEnum::ROOF;
    if(s=="LANDING"    ) return IfcSlabTypeEnum::LANDING;
    if(s=="BASESLAB"   ) return IfcSlabTypeEnum::BASESLAB;
    if(s=="USERDEFINED") return IfcSlabTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcSlabTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcSoundScaleEnum::ToString(IfcSoundScaleEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "DBA","DBB","DBC","NC","NR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSoundScaleEnum::IfcSoundScaleEnum IfcSoundScaleEnum::FromString(const std::string& s) {
    if(s=="DBA"        ) return IfcSoundScaleEnum::DBA;
    if(s=="DBB"        ) return IfcSoundScaleEnum::DBB;
    if(s=="DBC"        ) return IfcSoundScaleEnum::DBC;
    if(s=="NC"         ) return IfcSoundScaleEnum::NC;
    if(s=="NR"         ) return IfcSoundScaleEnum::NR;
    if(s=="USERDEFINED") return IfcSoundScaleEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcSoundScaleEnum::NOTDEFINED;
    throw;
}
std::string IfcSpaceHeaterTypeEnum::ToString(IfcSpaceHeaterTypeEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "SECTIONALRADIATOR","PANELRADIATOR","TUBULARRADIATOR","CONVECTOR","BASEBOARDHEATER","FINNEDTUBEUNIT","UNITHEATER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSpaceHeaterTypeEnum::IfcSpaceHeaterTypeEnum IfcSpaceHeaterTypeEnum::FromString(const std::string& s) {
    if(s=="SECTIONALRADIATOR") return IfcSpaceHeaterTypeEnum::SECTIONALRADIATOR;
    if(s=="PANELRADIATOR"    ) return IfcSpaceHeaterTypeEnum::PANELRADIATOR;
    if(s=="TUBULARRADIATOR"  ) return IfcSpaceHeaterTypeEnum::TUBULARRADIATOR;
    if(s=="CONVECTOR"        ) return IfcSpaceHeaterTypeEnum::CONVECTOR;
    if(s=="BASEBOARDHEATER"  ) return IfcSpaceHeaterTypeEnum::BASEBOARDHEATER;
    if(s=="FINNEDTUBEUNIT"   ) return IfcSpaceHeaterTypeEnum::FINNEDTUBEUNIT;
    if(s=="UNITHEATER"       ) return IfcSpaceHeaterTypeEnum::UNITHEATER;
    if(s=="USERDEFINED"      ) return IfcSpaceHeaterTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"       ) return IfcSpaceHeaterTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcSpaceTypeEnum::ToString(IfcSpaceTypeEnum v) {
    if ( v < 0 || v >= 2 ) throw;
    const char* names[] = { "USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSpaceTypeEnum::IfcSpaceTypeEnum IfcSpaceTypeEnum::FromString(const std::string& s) {
    if(s=="USERDEFINED") return IfcSpaceTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcSpaceTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcStackTerminalTypeEnum::ToString(IfcStackTerminalTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "BIRDCAGE","COWL","RAINWATERHOPPER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStackTerminalTypeEnum::IfcStackTerminalTypeEnum IfcStackTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="BIRDCAGE"       ) return IfcStackTerminalTypeEnum::BIRDCAGE;
    if(s=="COWL"           ) return IfcStackTerminalTypeEnum::COWL;
    if(s=="RAINWATERHOPPER") return IfcStackTerminalTypeEnum::RAINWATERHOPPER;
    if(s=="USERDEFINED"    ) return IfcStackTerminalTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"     ) return IfcStackTerminalTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcStairFlightTypeEnum::ToString(IfcStairFlightTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "STRAIGHT","WINDER","SPIRAL","CURVED","FREEFORM","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStairFlightTypeEnum::IfcStairFlightTypeEnum IfcStairFlightTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT"   ) return IfcStairFlightTypeEnum::STRAIGHT;
    if(s=="WINDER"     ) return IfcStairFlightTypeEnum::WINDER;
    if(s=="SPIRAL"     ) return IfcStairFlightTypeEnum::SPIRAL;
    if(s=="CURVED"     ) return IfcStairFlightTypeEnum::CURVED;
    if(s=="FREEFORM"   ) return IfcStairFlightTypeEnum::FREEFORM;
    if(s=="USERDEFINED") return IfcStairFlightTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcStairFlightTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcStairTypeEnum::ToString(IfcStairTypeEnum v) {
    if ( v < 0 || v >= 16 ) throw;
    const char* names[] = { "STRAIGHT_RUN_STAIR","TWO_STRAIGHT_RUN_STAIR","QUARTER_WINDING_STAIR","QUARTER_TURN_STAIR","HALF_WINDING_STAIR","HALF_TURN_STAIR","TWO_QUARTER_WINDING_STAIR","TWO_QUARTER_TURN_STAIR","THREE_QUARTER_WINDING_STAIR","THREE_QUARTER_TURN_STAIR","SPIRAL_STAIR","DOUBLE_RETURN_STAIR","CURVED_RUN_STAIR","TWO_CURVED_RUN_STAIR","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStairTypeEnum::IfcStairTypeEnum IfcStairTypeEnum::FromString(const std::string& s) {
    if(s=="STRAIGHT_RUN_STAIR"         ) return IfcStairTypeEnum::STRAIGHT_RUN_STAIR;
    if(s=="TWO_STRAIGHT_RUN_STAIR"     ) return IfcStairTypeEnum::TWO_STRAIGHT_RUN_STAIR;
    if(s=="QUARTER_WINDING_STAIR"      ) return IfcStairTypeEnum::QUARTER_WINDING_STAIR;
    if(s=="QUARTER_TURN_STAIR"         ) return IfcStairTypeEnum::QUARTER_TURN_STAIR;
    if(s=="HALF_WINDING_STAIR"         ) return IfcStairTypeEnum::HALF_WINDING_STAIR;
    if(s=="HALF_TURN_STAIR"            ) return IfcStairTypeEnum::HALF_TURN_STAIR;
    if(s=="TWO_QUARTER_WINDING_STAIR"  ) return IfcStairTypeEnum::TWO_QUARTER_WINDING_STAIR;
    if(s=="TWO_QUARTER_TURN_STAIR"     ) return IfcStairTypeEnum::TWO_QUARTER_TURN_STAIR;
    if(s=="THREE_QUARTER_WINDING_STAIR") return IfcStairTypeEnum::THREE_QUARTER_WINDING_STAIR;
    if(s=="THREE_QUARTER_TURN_STAIR"   ) return IfcStairTypeEnum::THREE_QUARTER_TURN_STAIR;
    if(s=="SPIRAL_STAIR"               ) return IfcStairTypeEnum::SPIRAL_STAIR;
    if(s=="DOUBLE_RETURN_STAIR"        ) return IfcStairTypeEnum::DOUBLE_RETURN_STAIR;
    if(s=="CURVED_RUN_STAIR"           ) return IfcStairTypeEnum::CURVED_RUN_STAIR;
    if(s=="TWO_CURVED_RUN_STAIR"       ) return IfcStairTypeEnum::TWO_CURVED_RUN_STAIR;
    if(s=="USERDEFINED"                ) return IfcStairTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"                 ) return IfcStairTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcStateEnum::ToString(IfcStateEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "READWRITE","READONLY","LOCKED","READWRITELOCKED","READONLYLOCKED" };
    return names[v];
}
IfcStateEnum::IfcStateEnum IfcStateEnum::FromString(const std::string& s) {
    if(s=="READWRITE"      ) return IfcStateEnum::READWRITE;
    if(s=="READONLY"       ) return IfcStateEnum::READONLY;
    if(s=="LOCKED"         ) return IfcStateEnum::LOCKED;
    if(s=="READWRITELOCKED") return IfcStateEnum::READWRITELOCKED;
    if(s=="READONLYLOCKED" ) return IfcStateEnum::READONLYLOCKED;
    throw;
}
std::string IfcStructuralCurveTypeEnum::ToString(IfcStructuralCurveTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "RIGID_JOINED_MEMBER","PIN_JOINED_MEMBER","CABLE","TENSION_MEMBER","COMPRESSION_MEMBER","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStructuralCurveTypeEnum::IfcStructuralCurveTypeEnum IfcStructuralCurveTypeEnum::FromString(const std::string& s) {
    if(s=="RIGID_JOINED_MEMBER") return IfcStructuralCurveTypeEnum::RIGID_JOINED_MEMBER;
    if(s=="PIN_JOINED_MEMBER"  ) return IfcStructuralCurveTypeEnum::PIN_JOINED_MEMBER;
    if(s=="CABLE"              ) return IfcStructuralCurveTypeEnum::CABLE;
    if(s=="TENSION_MEMBER"     ) return IfcStructuralCurveTypeEnum::TENSION_MEMBER;
    if(s=="COMPRESSION_MEMBER" ) return IfcStructuralCurveTypeEnum::COMPRESSION_MEMBER;
    if(s=="USERDEFINED"        ) return IfcStructuralCurveTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcStructuralCurveTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcStructuralSurfaceTypeEnum::ToString(IfcStructuralSurfaceTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "BENDING_ELEMENT","MEMBRANE_ELEMENT","SHELL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceTypeEnum IfcStructuralSurfaceTypeEnum::FromString(const std::string& s) {
    if(s=="BENDING_ELEMENT" ) return IfcStructuralSurfaceTypeEnum::BENDING_ELEMENT;
    if(s=="MEMBRANE_ELEMENT") return IfcStructuralSurfaceTypeEnum::MEMBRANE_ELEMENT;
    if(s=="SHELL"           ) return IfcStructuralSurfaceTypeEnum::SHELL;
    if(s=="USERDEFINED"     ) return IfcStructuralSurfaceTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcStructuralSurfaceTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcSurfaceSide::ToString(IfcSurfaceSide v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "POSITIVE","NEGATIVE","BOTH" };
    return names[v];
}
IfcSurfaceSide::IfcSurfaceSide IfcSurfaceSide::FromString(const std::string& s) {
    if(s=="POSITIVE") return IfcSurfaceSide::POSITIVE;
    if(s=="NEGATIVE") return IfcSurfaceSide::NEGATIVE;
    if(s=="BOTH"    ) return IfcSurfaceSide::BOTH;
    throw;
}
std::string IfcSurfaceTextureEnum::ToString(IfcSurfaceTextureEnum v) {
    if ( v < 0 || v >= 9 ) throw;
    const char* names[] = { "BUMP","OPACITY","REFLECTION","SELFILLUMINATION","SHININESS","SPECULAR","TEXTURE","TRANSPARENCYMAP","NOTDEFINED" };
    return names[v];
}
IfcSurfaceTextureEnum::IfcSurfaceTextureEnum IfcSurfaceTextureEnum::FromString(const std::string& s) {
    if(s=="BUMP"            ) return IfcSurfaceTextureEnum::BUMP;
    if(s=="OPACITY"         ) return IfcSurfaceTextureEnum::OPACITY;
    if(s=="REFLECTION"      ) return IfcSurfaceTextureEnum::REFLECTION;
    if(s=="SELFILLUMINATION") return IfcSurfaceTextureEnum::SELFILLUMINATION;
    if(s=="SHININESS"       ) return IfcSurfaceTextureEnum::SHININESS;
    if(s=="SPECULAR"        ) return IfcSurfaceTextureEnum::SPECULAR;
    if(s=="TEXTURE"         ) return IfcSurfaceTextureEnum::TEXTURE;
    if(s=="TRANSPARENCYMAP" ) return IfcSurfaceTextureEnum::TRANSPARENCYMAP;
    if(s=="NOTDEFINED"      ) return IfcSurfaceTextureEnum::NOTDEFINED;
    throw;
}
std::string IfcSwitchingDeviceTypeEnum::ToString(IfcSwitchingDeviceTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "CONTACTOR","EMERGENCYSTOP","STARTER","SWITCHDISCONNECTOR","TOGGLESWITCH","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceTypeEnum IfcSwitchingDeviceTypeEnum::FromString(const std::string& s) {
    if(s=="CONTACTOR"         ) return IfcSwitchingDeviceTypeEnum::CONTACTOR;
    if(s=="EMERGENCYSTOP"     ) return IfcSwitchingDeviceTypeEnum::EMERGENCYSTOP;
    if(s=="STARTER"           ) return IfcSwitchingDeviceTypeEnum::STARTER;
    if(s=="SWITCHDISCONNECTOR") return IfcSwitchingDeviceTypeEnum::SWITCHDISCONNECTOR;
    if(s=="TOGGLESWITCH"      ) return IfcSwitchingDeviceTypeEnum::TOGGLESWITCH;
    if(s=="USERDEFINED"       ) return IfcSwitchingDeviceTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"        ) return IfcSwitchingDeviceTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTankTypeEnum::ToString(IfcTankTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "PREFORMED","SECTIONAL","EXPANSION","PRESSUREVESSEL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTankTypeEnum::IfcTankTypeEnum IfcTankTypeEnum::FromString(const std::string& s) {
    if(s=="PREFORMED"     ) return IfcTankTypeEnum::PREFORMED;
    if(s=="SECTIONAL"     ) return IfcTankTypeEnum::SECTIONAL;
    if(s=="EXPANSION"     ) return IfcTankTypeEnum::EXPANSION;
    if(s=="PRESSUREVESSEL") return IfcTankTypeEnum::PRESSUREVESSEL;
    if(s=="USERDEFINED"   ) return IfcTankTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"    ) return IfcTankTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTendonTypeEnum::ToString(IfcTendonTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "STRAND","WIRE","BAR","COATED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTendonTypeEnum::IfcTendonTypeEnum IfcTendonTypeEnum::FromString(const std::string& s) {
    if(s=="STRAND"     ) return IfcTendonTypeEnum::STRAND;
    if(s=="WIRE"       ) return IfcTendonTypeEnum::WIRE;
    if(s=="BAR"        ) return IfcTendonTypeEnum::BAR;
    if(s=="COATED"     ) return IfcTendonTypeEnum::COATED;
    if(s=="USERDEFINED") return IfcTendonTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcTendonTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTextPath::ToString(IfcTextPath v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "LEFT","RIGHT","UP","DOWN" };
    return names[v];
}
IfcTextPath::IfcTextPath IfcTextPath::FromString(const std::string& s) {
    if(s=="LEFT" ) return IfcTextPath::LEFT;
    if(s=="RIGHT") return IfcTextPath::RIGHT;
    if(s=="UP"   ) return IfcTextPath::UP;
    if(s=="DOWN" ) return IfcTextPath::DOWN;
    throw;
}
std::string IfcThermalLoadSourceEnum::ToString(IfcThermalLoadSourceEnum v) {
    if ( v < 0 || v >= 13 ) throw;
    const char* names[] = { "PEOPLE","LIGHTING","EQUIPMENT","VENTILATIONINDOORAIR","VENTILATIONOUTSIDEAIR","RECIRCULATEDAIR","EXHAUSTAIR","AIREXCHANGERATE","DRYBULBTEMPERATURE","RELATIVEHUMIDITY","INFILTRATION","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcThermalLoadSourceEnum::IfcThermalLoadSourceEnum IfcThermalLoadSourceEnum::FromString(const std::string& s) {
    if(s=="PEOPLE"               ) return IfcThermalLoadSourceEnum::PEOPLE;
    if(s=="LIGHTING"             ) return IfcThermalLoadSourceEnum::LIGHTING;
    if(s=="EQUIPMENT"            ) return IfcThermalLoadSourceEnum::EQUIPMENT;
    if(s=="VENTILATIONINDOORAIR" ) return IfcThermalLoadSourceEnum::VENTILATIONINDOORAIR;
    if(s=="VENTILATIONOUTSIDEAIR") return IfcThermalLoadSourceEnum::VENTILATIONOUTSIDEAIR;
    if(s=="RECIRCULATEDAIR"      ) return IfcThermalLoadSourceEnum::RECIRCULATEDAIR;
    if(s=="EXHAUSTAIR"           ) return IfcThermalLoadSourceEnum::EXHAUSTAIR;
    if(s=="AIREXCHANGERATE"      ) return IfcThermalLoadSourceEnum::AIREXCHANGERATE;
    if(s=="DRYBULBTEMPERATURE"   ) return IfcThermalLoadSourceEnum::DRYBULBTEMPERATURE;
    if(s=="RELATIVEHUMIDITY"     ) return IfcThermalLoadSourceEnum::RELATIVEHUMIDITY;
    if(s=="INFILTRATION"         ) return IfcThermalLoadSourceEnum::INFILTRATION;
    if(s=="USERDEFINED"          ) return IfcThermalLoadSourceEnum::USERDEFINED;
    if(s=="NOTDEFINED"           ) return IfcThermalLoadSourceEnum::NOTDEFINED;
    throw;
}
std::string IfcThermalLoadTypeEnum::ToString(IfcThermalLoadTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "SENSIBLE","LATENT","RADIANT","NOTDEFINED" };
    return names[v];
}
IfcThermalLoadTypeEnum::IfcThermalLoadTypeEnum IfcThermalLoadTypeEnum::FromString(const std::string& s) {
    if(s=="SENSIBLE"  ) return IfcThermalLoadTypeEnum::SENSIBLE;
    if(s=="LATENT"    ) return IfcThermalLoadTypeEnum::LATENT;
    if(s=="RADIANT"   ) return IfcThermalLoadTypeEnum::RADIANT;
    if(s=="NOTDEFINED") return IfcThermalLoadTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTimeSeriesDataTypeEnum::ToString(IfcTimeSeriesDataTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "CONTINUOUS","DISCRETE","DISCRETEBINARY","PIECEWISEBINARY","PIECEWISECONSTANT","PIECEWISECONTINUOUS","NOTDEFINED" };
    return names[v];
}
IfcTimeSeriesDataTypeEnum::IfcTimeSeriesDataTypeEnum IfcTimeSeriesDataTypeEnum::FromString(const std::string& s) {
    if(s=="CONTINUOUS"         ) return IfcTimeSeriesDataTypeEnum::CONTINUOUS;
    if(s=="DISCRETE"           ) return IfcTimeSeriesDataTypeEnum::DISCRETE;
    if(s=="DISCRETEBINARY"     ) return IfcTimeSeriesDataTypeEnum::DISCRETEBINARY;
    if(s=="PIECEWISEBINARY"    ) return IfcTimeSeriesDataTypeEnum::PIECEWISEBINARY;
    if(s=="PIECEWISECONSTANT"  ) return IfcTimeSeriesDataTypeEnum::PIECEWISECONSTANT;
    if(s=="PIECEWISECONTINUOUS") return IfcTimeSeriesDataTypeEnum::PIECEWISECONTINUOUS;
    if(s=="NOTDEFINED"         ) return IfcTimeSeriesDataTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTimeSeriesScheduleTypeEnum::ToString(IfcTimeSeriesScheduleTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "ANNUAL","MONTHLY","WEEKLY","DAILY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleTypeEnum IfcTimeSeriesScheduleTypeEnum::FromString(const std::string& s) {
    if(s=="ANNUAL"     ) return IfcTimeSeriesScheduleTypeEnum::ANNUAL;
    if(s=="MONTHLY"    ) return IfcTimeSeriesScheduleTypeEnum::MONTHLY;
    if(s=="WEEKLY"     ) return IfcTimeSeriesScheduleTypeEnum::WEEKLY;
    if(s=="DAILY"      ) return IfcTimeSeriesScheduleTypeEnum::DAILY;
    if(s=="USERDEFINED") return IfcTimeSeriesScheduleTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcTimeSeriesScheduleTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTransformerTypeEnum::ToString(IfcTransformerTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "CURRENT","FREQUENCY","VOLTAGE","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTransformerTypeEnum::IfcTransformerTypeEnum IfcTransformerTypeEnum::FromString(const std::string& s) {
    if(s=="CURRENT"    ) return IfcTransformerTypeEnum::CURRENT;
    if(s=="FREQUENCY"  ) return IfcTransformerTypeEnum::FREQUENCY;
    if(s=="VOLTAGE"    ) return IfcTransformerTypeEnum::VOLTAGE;
    if(s=="USERDEFINED") return IfcTransformerTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcTransformerTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTransitionCode::ToString(IfcTransitionCode v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "DISCONTINUOUS","CONTINUOUS","CONTSAMEGRADIENT","CONTSAMEGRADIENTSAMECURVATURE" };
    return names[v];
}
IfcTransitionCode::IfcTransitionCode IfcTransitionCode::FromString(const std::string& s) {
    if(s=="DISCONTINUOUS"                ) return IfcTransitionCode::DISCONTINUOUS;
    if(s=="CONTINUOUS"                   ) return IfcTransitionCode::CONTINUOUS;
    if(s=="CONTSAMEGRADIENT"             ) return IfcTransitionCode::CONTSAMEGRADIENT;
    if(s=="CONTSAMEGRADIENTSAMECURVATURE") return IfcTransitionCode::CONTSAMEGRADIENTSAMECURVATURE;
    throw;
}
std::string IfcTransportElementTypeEnum::ToString(IfcTransportElementTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "ELEVATOR","ESCALATOR","MOVINGWALKWAY","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTransportElementTypeEnum::IfcTransportElementTypeEnum IfcTransportElementTypeEnum::FromString(const std::string& s) {
    if(s=="ELEVATOR"     ) return IfcTransportElementTypeEnum::ELEVATOR;
    if(s=="ESCALATOR"    ) return IfcTransportElementTypeEnum::ESCALATOR;
    if(s=="MOVINGWALKWAY") return IfcTransportElementTypeEnum::MOVINGWALKWAY;
    if(s=="USERDEFINED"  ) return IfcTransportElementTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"   ) return IfcTransportElementTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcTrimmingPreference::ToString(IfcTrimmingPreference v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "CARTESIAN","PARAMETER","UNSPECIFIED" };
    return names[v];
}
IfcTrimmingPreference::IfcTrimmingPreference IfcTrimmingPreference::FromString(const std::string& s) {
    if(s=="CARTESIAN"  ) return IfcTrimmingPreference::CARTESIAN;
    if(s=="PARAMETER"  ) return IfcTrimmingPreference::PARAMETER;
    if(s=="UNSPECIFIED") return IfcTrimmingPreference::UNSPECIFIED;
    throw;
}
std::string IfcTubeBundleTypeEnum::ToString(IfcTubeBundleTypeEnum v) {
    if ( v < 0 || v >= 3 ) throw;
    const char* names[] = { "FINNED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcTubeBundleTypeEnum::IfcTubeBundleTypeEnum IfcTubeBundleTypeEnum::FromString(const std::string& s) {
    if(s=="FINNED"     ) return IfcTubeBundleTypeEnum::FINNED;
    if(s=="USERDEFINED") return IfcTubeBundleTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcTubeBundleTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcUnitEnum::ToString(IfcUnitEnum v) {
    if ( v < 0 || v >= 30 ) throw;
    const char* names[] = { "ABSORBEDDOSEUNIT","AMOUNTOFSUBSTANCEUNIT","AREAUNIT","DOSEEQUIVALENTUNIT","ELECTRICCAPACITANCEUNIT","ELECTRICCHARGEUNIT","ELECTRICCONDUCTANCEUNIT","ELECTRICCURRENTUNIT","ELECTRICRESISTANCEUNIT","ELECTRICVOLTAGEUNIT","ENERGYUNIT","FORCEUNIT","FREQUENCYUNIT","ILLUMINANCEUNIT","INDUCTANCEUNIT","LENGTHUNIT","LUMINOUSFLUXUNIT","LUMINOUSINTENSITYUNIT","MAGNETICFLUXDENSITYUNIT","MAGNETICFLUXUNIT","MASSUNIT","PLANEANGLEUNIT","POWERUNIT","PRESSUREUNIT","RADIOACTIVITYUNIT","SOLIDANGLEUNIT","THERMODYNAMICTEMPERATUREUNIT","TIMEUNIT","VOLUMEUNIT","USERDEFINED" };
    return names[v];
}
IfcUnitEnum::IfcUnitEnum IfcUnitEnum::FromString(const std::string& s) {
    if(s=="ABSORBEDDOSEUNIT"            ) return IfcUnitEnum::ABSORBEDDOSEUNIT;
    if(s=="AMOUNTOFSUBSTANCEUNIT"       ) return IfcUnitEnum::AMOUNTOFSUBSTANCEUNIT;
    if(s=="AREAUNIT"                    ) return IfcUnitEnum::AREAUNIT;
    if(s=="DOSEEQUIVALENTUNIT"          ) return IfcUnitEnum::DOSEEQUIVALENTUNIT;
    if(s=="ELECTRICCAPACITANCEUNIT"     ) return IfcUnitEnum::ELECTRICCAPACITANCEUNIT;
    if(s=="ELECTRICCHARGEUNIT"          ) return IfcUnitEnum::ELECTRICCHARGEUNIT;
    if(s=="ELECTRICCONDUCTANCEUNIT"     ) return IfcUnitEnum::ELECTRICCONDUCTANCEUNIT;
    if(s=="ELECTRICCURRENTUNIT"         ) return IfcUnitEnum::ELECTRICCURRENTUNIT;
    if(s=="ELECTRICRESISTANCEUNIT"      ) return IfcUnitEnum::ELECTRICRESISTANCEUNIT;
    if(s=="ELECTRICVOLTAGEUNIT"         ) return IfcUnitEnum::ELECTRICVOLTAGEUNIT;
    if(s=="ENERGYUNIT"                  ) return IfcUnitEnum::ENERGYUNIT;
    if(s=="FORCEUNIT"                   ) return IfcUnitEnum::FORCEUNIT;
    if(s=="FREQUENCYUNIT"               ) return IfcUnitEnum::FREQUENCYUNIT;
    if(s=="ILLUMINANCEUNIT"             ) return IfcUnitEnum::ILLUMINANCEUNIT;
    if(s=="INDUCTANCEUNIT"              ) return IfcUnitEnum::INDUCTANCEUNIT;
    if(s=="LENGTHUNIT"                  ) return IfcUnitEnum::LENGTHUNIT;
    if(s=="LUMINOUSFLUXUNIT"            ) return IfcUnitEnum::LUMINOUSFLUXUNIT;
    if(s=="LUMINOUSINTENSITYUNIT"       ) return IfcUnitEnum::LUMINOUSINTENSITYUNIT;
    if(s=="MAGNETICFLUXDENSITYUNIT"     ) return IfcUnitEnum::MAGNETICFLUXDENSITYUNIT;
    if(s=="MAGNETICFLUXUNIT"            ) return IfcUnitEnum::MAGNETICFLUXUNIT;
    if(s=="MASSUNIT"                    ) return IfcUnitEnum::MASSUNIT;
    if(s=="PLANEANGLEUNIT"              ) return IfcUnitEnum::PLANEANGLEUNIT;
    if(s=="POWERUNIT"                   ) return IfcUnitEnum::POWERUNIT;
    if(s=="PRESSUREUNIT"                ) return IfcUnitEnum::PRESSUREUNIT;
    if(s=="RADIOACTIVITYUNIT"           ) return IfcUnitEnum::RADIOACTIVITYUNIT;
    if(s=="SOLIDANGLEUNIT"              ) return IfcUnitEnum::SOLIDANGLEUNIT;
    if(s=="THERMODYNAMICTEMPERATUREUNIT") return IfcUnitEnum::THERMODYNAMICTEMPERATUREUNIT;
    if(s=="TIMEUNIT"                    ) return IfcUnitEnum::TIMEUNIT;
    if(s=="VOLUMEUNIT"                  ) return IfcUnitEnum::VOLUMEUNIT;
    if(s=="USERDEFINED"                 ) return IfcUnitEnum::USERDEFINED;
    throw;
}
std::string IfcUnitaryEquipmentTypeEnum::ToString(IfcUnitaryEquipmentTypeEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "AIRHANDLER","AIRCONDITIONINGUNIT","SPLITSYSTEM","ROOFTOPUNIT","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentTypeEnum IfcUnitaryEquipmentTypeEnum::FromString(const std::string& s) {
    if(s=="AIRHANDLER"         ) return IfcUnitaryEquipmentTypeEnum::AIRHANDLER;
    if(s=="AIRCONDITIONINGUNIT") return IfcUnitaryEquipmentTypeEnum::AIRCONDITIONINGUNIT;
    if(s=="SPLITSYSTEM"        ) return IfcUnitaryEquipmentTypeEnum::SPLITSYSTEM;
    if(s=="ROOFTOPUNIT"        ) return IfcUnitaryEquipmentTypeEnum::ROOFTOPUNIT;
    if(s=="USERDEFINED"        ) return IfcUnitaryEquipmentTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"         ) return IfcUnitaryEquipmentTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcValveTypeEnum::ToString(IfcValveTypeEnum v) {
    if ( v < 0 || v >= 23 ) throw;
    const char* names[] = { "AIRRELEASE","ANTIVACUUM","CHANGEOVER","CHECK","COMMISSIONING","DIVERTING","DRAWOFFCOCK","DOUBLECHECK","DOUBLEREGULATING","FAUCET","FLUSHING","GASCOCK","GASTAP","ISOLATING","MIXING","PRESSUREREDUCING","PRESSURERELIEF","REGULATING","SAFETYCUTOFF","STEAMTRAP","STOPCOCK","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcValveTypeEnum::IfcValveTypeEnum IfcValveTypeEnum::FromString(const std::string& s) {
    if(s=="AIRRELEASE"      ) return IfcValveTypeEnum::AIRRELEASE;
    if(s=="ANTIVACUUM"      ) return IfcValveTypeEnum::ANTIVACUUM;
    if(s=="CHANGEOVER"      ) return IfcValveTypeEnum::CHANGEOVER;
    if(s=="CHECK"           ) return IfcValveTypeEnum::CHECK;
    if(s=="COMMISSIONING"   ) return IfcValveTypeEnum::COMMISSIONING;
    if(s=="DIVERTING"       ) return IfcValveTypeEnum::DIVERTING;
    if(s=="DRAWOFFCOCK"     ) return IfcValveTypeEnum::DRAWOFFCOCK;
    if(s=="DOUBLECHECK"     ) return IfcValveTypeEnum::DOUBLECHECK;
    if(s=="DOUBLEREGULATING") return IfcValveTypeEnum::DOUBLEREGULATING;
    if(s=="FAUCET"          ) return IfcValveTypeEnum::FAUCET;
    if(s=="FLUSHING"        ) return IfcValveTypeEnum::FLUSHING;
    if(s=="GASCOCK"         ) return IfcValveTypeEnum::GASCOCK;
    if(s=="GASTAP"          ) return IfcValveTypeEnum::GASTAP;
    if(s=="ISOLATING"       ) return IfcValveTypeEnum::ISOLATING;
    if(s=="MIXING"          ) return IfcValveTypeEnum::MIXING;
    if(s=="PRESSUREREDUCING") return IfcValveTypeEnum::PRESSUREREDUCING;
    if(s=="PRESSURERELIEF"  ) return IfcValveTypeEnum::PRESSURERELIEF;
    if(s=="REGULATING"      ) return IfcValveTypeEnum::REGULATING;
    if(s=="SAFETYCUTOFF"    ) return IfcValveTypeEnum::SAFETYCUTOFF;
    if(s=="STEAMTRAP"       ) return IfcValveTypeEnum::STEAMTRAP;
    if(s=="STOPCOCK"        ) return IfcValveTypeEnum::STOPCOCK;
    if(s=="USERDEFINED"     ) return IfcValveTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"      ) return IfcValveTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcVibrationIsolatorTypeEnum::ToString(IfcVibrationIsolatorTypeEnum v) {
    if ( v < 0 || v >= 4 ) throw;
    const char* names[] = { "COMPRESSION","SPRING","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorTypeEnum IfcVibrationIsolatorTypeEnum::FromString(const std::string& s) {
    if(s=="COMPRESSION") return IfcVibrationIsolatorTypeEnum::COMPRESSION;
    if(s=="SPRING"     ) return IfcVibrationIsolatorTypeEnum::SPRING;
    if(s=="USERDEFINED") return IfcVibrationIsolatorTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcVibrationIsolatorTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcWallTypeEnum::ToString(IfcWallTypeEnum v) {
    if ( v < 0 || v >= 7 ) throw;
    const char* names[] = { "STANDARD","POLYGONAL","SHEAR","ELEMENTEDWALL","PLUMBINGWALL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWallTypeEnum::IfcWallTypeEnum IfcWallTypeEnum::FromString(const std::string& s) {
    if(s=="STANDARD"     ) return IfcWallTypeEnum::STANDARD;
    if(s=="POLYGONAL"    ) return IfcWallTypeEnum::POLYGONAL;
    if(s=="SHEAR"        ) return IfcWallTypeEnum::SHEAR;
    if(s=="ELEMENTEDWALL") return IfcWallTypeEnum::ELEMENTEDWALL;
    if(s=="PLUMBINGWALL" ) return IfcWallTypeEnum::PLUMBINGWALL;
    if(s=="USERDEFINED"  ) return IfcWallTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"   ) return IfcWallTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcWasteTerminalTypeEnum::ToString(IfcWasteTerminalTypeEnum v) {
    if ( v < 0 || v >= 12 ) throw;
    const char* names[] = { "FLOORTRAP","FLOORWASTE","GULLYSUMP","GULLYTRAP","GREASEINTERCEPTOR","OILINTERCEPTOR","PETROLINTERCEPTOR","ROOFDRAIN","WASTEDISPOSALUNIT","WASTETRAP","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWasteTerminalTypeEnum::IfcWasteTerminalTypeEnum IfcWasteTerminalTypeEnum::FromString(const std::string& s) {
    if(s=="FLOORTRAP"        ) return IfcWasteTerminalTypeEnum::FLOORTRAP;
    if(s=="FLOORWASTE"       ) return IfcWasteTerminalTypeEnum::FLOORWASTE;
    if(s=="GULLYSUMP"        ) return IfcWasteTerminalTypeEnum::GULLYSUMP;
    if(s=="GULLYTRAP"        ) return IfcWasteTerminalTypeEnum::GULLYTRAP;
    if(s=="GREASEINTERCEPTOR") return IfcWasteTerminalTypeEnum::GREASEINTERCEPTOR;
    if(s=="OILINTERCEPTOR"   ) return IfcWasteTerminalTypeEnum::OILINTERCEPTOR;
    if(s=="PETROLINTERCEPTOR") return IfcWasteTerminalTypeEnum::PETROLINTERCEPTOR;
    if(s=="ROOFDRAIN"        ) return IfcWasteTerminalTypeEnum::ROOFDRAIN;
    if(s=="WASTEDISPOSALUNIT") return IfcWasteTerminalTypeEnum::WASTEDISPOSALUNIT;
    if(s=="WASTETRAP"        ) return IfcWasteTerminalTypeEnum::WASTETRAP;
    if(s=="USERDEFINED"      ) return IfcWasteTerminalTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED"       ) return IfcWasteTerminalTypeEnum::NOTDEFINED;
    throw;
}
std::string IfcWindowPanelOperationEnum::ToString(IfcWindowPanelOperationEnum v) {
    if ( v < 0 || v >= 14 ) throw;
    const char* names[] = { "SIDEHUNGRIGHTHAND","SIDEHUNGLEFTHAND","TILTANDTURNRIGHTHAND","TILTANDTURNLEFTHAND","TOPHUNG","BOTTOMHUNG","PIVOTHORIZONTAL","PIVOTVERTICAL","SLIDINGHORIZONTAL","SLIDINGVERTICAL","REMOVABLECASEMENT","FIXEDCASEMENT","OTHEROPERATION","NOTDEFINED" };
    return names[v];
}
IfcWindowPanelOperationEnum::IfcWindowPanelOperationEnum IfcWindowPanelOperationEnum::FromString(const std::string& s) {
    if(s=="SIDEHUNGRIGHTHAND"   ) return IfcWindowPanelOperationEnum::SIDEHUNGRIGHTHAND;
    if(s=="SIDEHUNGLEFTHAND"    ) return IfcWindowPanelOperationEnum::SIDEHUNGLEFTHAND;
    if(s=="TILTANDTURNRIGHTHAND") return IfcWindowPanelOperationEnum::TILTANDTURNRIGHTHAND;
    if(s=="TILTANDTURNLEFTHAND" ) return IfcWindowPanelOperationEnum::TILTANDTURNLEFTHAND;
    if(s=="TOPHUNG"             ) return IfcWindowPanelOperationEnum::TOPHUNG;
    if(s=="BOTTOMHUNG"          ) return IfcWindowPanelOperationEnum::BOTTOMHUNG;
    if(s=="PIVOTHORIZONTAL"     ) return IfcWindowPanelOperationEnum::PIVOTHORIZONTAL;
    if(s=="PIVOTVERTICAL"       ) return IfcWindowPanelOperationEnum::PIVOTVERTICAL;
    if(s=="SLIDINGHORIZONTAL"   ) return IfcWindowPanelOperationEnum::SLIDINGHORIZONTAL;
    if(s=="SLIDINGVERTICAL"     ) return IfcWindowPanelOperationEnum::SLIDINGVERTICAL;
    if(s=="REMOVABLECASEMENT"   ) return IfcWindowPanelOperationEnum::REMOVABLECASEMENT;
    if(s=="FIXEDCASEMENT"       ) return IfcWindowPanelOperationEnum::FIXEDCASEMENT;
    if(s=="OTHEROPERATION"      ) return IfcWindowPanelOperationEnum::OTHEROPERATION;
    if(s=="NOTDEFINED"          ) return IfcWindowPanelOperationEnum::NOTDEFINED;
    throw;
}
std::string IfcWindowPanelPositionEnum::ToString(IfcWindowPanelPositionEnum v) {
    if ( v < 0 || v >= 6 ) throw;
    const char* names[] = { "LEFT","MIDDLE","RIGHT","BOTTOM","TOP","NOTDEFINED" };
    return names[v];
}
IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum IfcWindowPanelPositionEnum::FromString(const std::string& s) {
    if(s=="LEFT"      ) return IfcWindowPanelPositionEnum::LEFT;
    if(s=="MIDDLE"    ) return IfcWindowPanelPositionEnum::MIDDLE;
    if(s=="RIGHT"     ) return IfcWindowPanelPositionEnum::RIGHT;
    if(s=="BOTTOM"    ) return IfcWindowPanelPositionEnum::BOTTOM;
    if(s=="TOP"       ) return IfcWindowPanelPositionEnum::TOP;
    if(s=="NOTDEFINED") return IfcWindowPanelPositionEnum::NOTDEFINED;
    throw;
}
std::string IfcWindowStyleConstructionEnum::ToString(IfcWindowStyleConstructionEnum v) {
    if ( v < 0 || v >= 8 ) throw;
    const char* names[] = { "ALUMINIUM","HIGH_GRADE_STEEL","STEEL","WOOD","ALUMINIUM_WOOD","PLASTIC","OTHER_CONSTRUCTION","NOTDEFINED" };
    return names[v];
}
IfcWindowStyleConstructionEnum::IfcWindowStyleConstructionEnum IfcWindowStyleConstructionEnum::FromString(const std::string& s) {
    if(s=="ALUMINIUM"         ) return IfcWindowStyleConstructionEnum::ALUMINIUM;
    if(s=="HIGH_GRADE_STEEL"  ) return IfcWindowStyleConstructionEnum::HIGH_GRADE_STEEL;
    if(s=="STEEL"             ) return IfcWindowStyleConstructionEnum::STEEL;
    if(s=="WOOD"              ) return IfcWindowStyleConstructionEnum::WOOD;
    if(s=="ALUMINIUM_WOOD"    ) return IfcWindowStyleConstructionEnum::ALUMINIUM_WOOD;
    if(s=="PLASTIC"           ) return IfcWindowStyleConstructionEnum::PLASTIC;
    if(s=="OTHER_CONSTRUCTION") return IfcWindowStyleConstructionEnum::OTHER_CONSTRUCTION;
    if(s=="NOTDEFINED"        ) return IfcWindowStyleConstructionEnum::NOTDEFINED;
    throw;
}
std::string IfcWindowStyleOperationEnum::ToString(IfcWindowStyleOperationEnum v) {
    if ( v < 0 || v >= 11 ) throw;
    const char* names[] = { "SINGLE_PANEL","DOUBLE_PANEL_VERTICAL","DOUBLE_PANEL_HORIZONTAL","TRIPLE_PANEL_VERTICAL","TRIPLE_PANEL_BOTTOM","TRIPLE_PANEL_TOP","TRIPLE_PANEL_LEFT","TRIPLE_PANEL_RIGHT","TRIPLE_PANEL_HORIZONTAL","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWindowStyleOperationEnum::IfcWindowStyleOperationEnum IfcWindowStyleOperationEnum::FromString(const std::string& s) {
    if(s=="SINGLE_PANEL"           ) return IfcWindowStyleOperationEnum::SINGLE_PANEL;
    if(s=="DOUBLE_PANEL_VERTICAL"  ) return IfcWindowStyleOperationEnum::DOUBLE_PANEL_VERTICAL;
    if(s=="DOUBLE_PANEL_HORIZONTAL") return IfcWindowStyleOperationEnum::DOUBLE_PANEL_HORIZONTAL;
    if(s=="TRIPLE_PANEL_VERTICAL"  ) return IfcWindowStyleOperationEnum::TRIPLE_PANEL_VERTICAL;
    if(s=="TRIPLE_PANEL_BOTTOM"    ) return IfcWindowStyleOperationEnum::TRIPLE_PANEL_BOTTOM;
    if(s=="TRIPLE_PANEL_TOP"       ) return IfcWindowStyleOperationEnum::TRIPLE_PANEL_TOP;
    if(s=="TRIPLE_PANEL_LEFT"      ) return IfcWindowStyleOperationEnum::TRIPLE_PANEL_LEFT;
    if(s=="TRIPLE_PANEL_RIGHT"     ) return IfcWindowStyleOperationEnum::TRIPLE_PANEL_RIGHT;
    if(s=="TRIPLE_PANEL_HORIZONTAL") return IfcWindowStyleOperationEnum::TRIPLE_PANEL_HORIZONTAL;
    if(s=="USERDEFINED"            ) return IfcWindowStyleOperationEnum::USERDEFINED;
    if(s=="NOTDEFINED"             ) return IfcWindowStyleOperationEnum::NOTDEFINED;
    throw;
}
std::string IfcWorkControlTypeEnum::ToString(IfcWorkControlTypeEnum v) {
    if ( v < 0 || v >= 5 ) throw;
    const char* names[] = { "ACTUAL","BASELINE","PLANNED","USERDEFINED","NOTDEFINED" };
    return names[v];
}
IfcWorkControlTypeEnum::IfcWorkControlTypeEnum IfcWorkControlTypeEnum::FromString(const std::string& s) {
    if(s=="ACTUAL"     ) return IfcWorkControlTypeEnum::ACTUAL;
    if(s=="BASELINE"   ) return IfcWorkControlTypeEnum::BASELINE;
    if(s=="PLANNED"    ) return IfcWorkControlTypeEnum::PLANNED;
    if(s=="USERDEFINED") return IfcWorkControlTypeEnum::USERDEFINED;
    if(s=="NOTDEFINED" ) return IfcWorkControlTypeEnum::NOTDEFINED;
    throw;
}

// Ifc2DCompositeCurve
bool Ifc2DCompositeCurve::is(Type::Enum v) { return v == Type::Ifc2DCompositeCurve || IfcCompositeCurve::is(v); }
Type::Enum Ifc2DCompositeCurve::type() { return Type::Ifc2DCompositeCurve; }
Type::Enum Ifc2DCompositeCurve::Class() { return Type::Ifc2DCompositeCurve; }
Ifc2DCompositeCurve::Ifc2DCompositeCurve(IfcAbstractEntityPtr e) { if (!is(Type::Ifc2DCompositeCurve)) throw; entity = e; } 
// IfcActionRequest
IfcIdentifier IfcActionRequest::RequestID() { return *entity->getArgument(5); }
bool IfcActionRequest::is(Type::Enum v) { return v == Type::IfcActionRequest || IfcControl::is(v); }
Type::Enum IfcActionRequest::type() { return Type::IfcActionRequest; }
Type::Enum IfcActionRequest::Class() { return Type::IfcActionRequest; }
IfcActionRequest::IfcActionRequest(IfcAbstractEntityPtr e) { if (!is(Type::IfcActionRequest)) throw; entity = e; } 
// IfcActor
IfcActorSelect IfcActor::TheActor() { return *entity->getArgument(5); }
IfcRelAssignsToActor::list IfcActor::IsActingUpon() { RETURN_INVERSE(IfcRelAssignsToActor) }
bool IfcActor::is(Type::Enum v) { return v == Type::IfcActor || IfcObject::is(v); }
Type::Enum IfcActor::type() { return Type::IfcActor; }
Type::Enum IfcActor::Class() { return Type::IfcActor; }
IfcActor::IfcActor(IfcAbstractEntityPtr e) { if (!is(Type::IfcActor)) throw; entity = e; } 
// IfcActorRole
IfcRoleEnum::IfcRoleEnum IfcActorRole::Role() { return IfcRoleEnum::FromString(*entity->getArgument(0)); }
bool IfcActorRole::hasUserDefinedRole() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcActorRole::UserDefinedRole() { return *entity->getArgument(1); }
bool IfcActorRole::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcActorRole::Description() { return *entity->getArgument(2); }
bool IfcActorRole::is(Type::Enum v) { return v == Type::IfcActorRole; }
Type::Enum IfcActorRole::type() { return Type::IfcActorRole; }
Type::Enum IfcActorRole::Class() { return Type::IfcActorRole; }
IfcActorRole::IfcActorRole(IfcAbstractEntityPtr e) { if (!is(Type::IfcActorRole)) throw; entity = e; } 
// IfcActuatorType
IfcActuatorTypeEnum::IfcActuatorTypeEnum IfcActuatorType::PredefinedType() { return IfcActuatorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcActuatorType::is(Type::Enum v) { return v == Type::IfcActuatorType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcActuatorType::type() { return Type::IfcActuatorType; }
Type::Enum IfcActuatorType::Class() { return Type::IfcActuatorType; }
IfcActuatorType::IfcActuatorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcActuatorType)) throw; entity = e; } 
// IfcAddress
bool IfcAddress::hasPurpose() { return !entity->getArgument(0)->isNull(); }
IfcAddressTypeEnum::IfcAddressTypeEnum IfcAddress::Purpose() { return IfcAddressTypeEnum::FromString(*entity->getArgument(0)); }
bool IfcAddress::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcAddress::Description() { return *entity->getArgument(1); }
bool IfcAddress::hasUserDefinedPurpose() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcAddress::UserDefinedPurpose() { return *entity->getArgument(2); }
IfcPerson::list IfcAddress::OfPerson() { RETURN_INVERSE(IfcPerson) }
IfcOrganization::list IfcAddress::OfOrganization() { RETURN_INVERSE(IfcOrganization) }
bool IfcAddress::is(Type::Enum v) { return v == Type::IfcAddress; }
Type::Enum IfcAddress::type() { return Type::IfcAddress; }
Type::Enum IfcAddress::Class() { return Type::IfcAddress; }
IfcAddress::IfcAddress(IfcAbstractEntityPtr e) { if (!is(Type::IfcAddress)) throw; entity = e; } 
// IfcAirTerminalBoxType
IfcAirTerminalBoxTypeEnum::IfcAirTerminalBoxTypeEnum IfcAirTerminalBoxType::PredefinedType() { return IfcAirTerminalBoxTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAirTerminalBoxType::is(Type::Enum v) { return v == Type::IfcAirTerminalBoxType || IfcFlowControllerType::is(v); }
Type::Enum IfcAirTerminalBoxType::type() { return Type::IfcAirTerminalBoxType; }
Type::Enum IfcAirTerminalBoxType::Class() { return Type::IfcAirTerminalBoxType; }
IfcAirTerminalBoxType::IfcAirTerminalBoxType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAirTerminalBoxType)) throw; entity = e; } 
// IfcAirTerminalType
IfcAirTerminalTypeEnum::IfcAirTerminalTypeEnum IfcAirTerminalType::PredefinedType() { return IfcAirTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAirTerminalType::is(Type::Enum v) { return v == Type::IfcAirTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcAirTerminalType::type() { return Type::IfcAirTerminalType; }
Type::Enum IfcAirTerminalType::Class() { return Type::IfcAirTerminalType; }
IfcAirTerminalType::IfcAirTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAirTerminalType)) throw; entity = e; } 
// IfcAirToAirHeatRecoveryType
IfcAirToAirHeatRecoveryTypeEnum::IfcAirToAirHeatRecoveryTypeEnum IfcAirToAirHeatRecoveryType::PredefinedType() { return IfcAirToAirHeatRecoveryTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAirToAirHeatRecoveryType::is(Type::Enum v) { return v == Type::IfcAirToAirHeatRecoveryType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcAirToAirHeatRecoveryType::type() { return Type::IfcAirToAirHeatRecoveryType; }
Type::Enum IfcAirToAirHeatRecoveryType::Class() { return Type::IfcAirToAirHeatRecoveryType; }
IfcAirToAirHeatRecoveryType::IfcAirToAirHeatRecoveryType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAirToAirHeatRecoveryType)) throw; entity = e; } 
// IfcAlarmType
IfcAlarmTypeEnum::IfcAlarmTypeEnum IfcAlarmType::PredefinedType() { return IfcAlarmTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcAlarmType::is(Type::Enum v) { return v == Type::IfcAlarmType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcAlarmType::type() { return Type::IfcAlarmType; }
Type::Enum IfcAlarmType::Class() { return Type::IfcAlarmType; }
IfcAlarmType::IfcAlarmType(IfcAbstractEntityPtr e) { if (!is(Type::IfcAlarmType)) throw; entity = e; } 
// IfcAngularDimension
bool IfcAngularDimension::is(Type::Enum v) { return v == Type::IfcAngularDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcAngularDimension::type() { return Type::IfcAngularDimension; }
Type::Enum IfcAngularDimension::Class() { return Type::IfcAngularDimension; }
IfcAngularDimension::IfcAngularDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcAngularDimension)) throw; entity = e; } 
// IfcAnnotation
IfcRelContainedInSpatialStructure::list IfcAnnotation::ContainedInStructure() { RETURN_INVERSE(IfcRelContainedInSpatialStructure) }
bool IfcAnnotation::is(Type::Enum v) { return v == Type::IfcAnnotation || IfcProduct::is(v); }
Type::Enum IfcAnnotation::type() { return Type::IfcAnnotation; }
Type::Enum IfcAnnotation::Class() { return Type::IfcAnnotation; }
IfcAnnotation::IfcAnnotation(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotation)) throw; entity = e; } 
// IfcAnnotationCurveOccurrence
bool IfcAnnotationCurveOccurrence::is(Type::Enum v) { return v == Type::IfcAnnotationCurveOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationCurveOccurrence::type() { return Type::IfcAnnotationCurveOccurrence; }
Type::Enum IfcAnnotationCurveOccurrence::Class() { return Type::IfcAnnotationCurveOccurrence; }
IfcAnnotationCurveOccurrence::IfcAnnotationCurveOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationCurveOccurrence)) throw; entity = e; } 
// IfcAnnotationFillArea
SHARED_PTR<IfcCurve> IfcAnnotationFillArea::OuterBoundary() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
bool IfcAnnotationFillArea::hasInnerBoundaries() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > IfcAnnotationFillArea::InnerBoundaries() { RETURN_AS_LIST(IfcCurve,1) }
bool IfcAnnotationFillArea::is(Type::Enum v) { return v == Type::IfcAnnotationFillArea || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcAnnotationFillArea::type() { return Type::IfcAnnotationFillArea; }
Type::Enum IfcAnnotationFillArea::Class() { return Type::IfcAnnotationFillArea; }
IfcAnnotationFillArea::IfcAnnotationFillArea(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationFillArea)) throw; entity = e; } 
// IfcAnnotationFillAreaOccurrence
bool IfcAnnotationFillAreaOccurrence::hasFillStyleTarget() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcPoint> IfcAnnotationFillAreaOccurrence::FillStyleTarget() { return reinterpret_pointer_cast<IfcBaseClass,IfcPoint>(*entity->getArgument(3)); }
bool IfcAnnotationFillAreaOccurrence::hasGlobalOrLocal() { return !entity->getArgument(4)->isNull(); }
IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum IfcAnnotationFillAreaOccurrence::GlobalOrLocal() { return IfcGlobalOrLocalEnum::FromString(*entity->getArgument(4)); }
bool IfcAnnotationFillAreaOccurrence::is(Type::Enum v) { return v == Type::IfcAnnotationFillAreaOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationFillAreaOccurrence::type() { return Type::IfcAnnotationFillAreaOccurrence; }
Type::Enum IfcAnnotationFillAreaOccurrence::Class() { return Type::IfcAnnotationFillAreaOccurrence; }
IfcAnnotationFillAreaOccurrence::IfcAnnotationFillAreaOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationFillAreaOccurrence)) throw; entity = e; } 
// IfcAnnotationOccurrence
bool IfcAnnotationOccurrence::is(Type::Enum v) { return v == Type::IfcAnnotationOccurrence || IfcStyledItem::is(v); }
Type::Enum IfcAnnotationOccurrence::type() { return Type::IfcAnnotationOccurrence; }
Type::Enum IfcAnnotationOccurrence::Class() { return Type::IfcAnnotationOccurrence; }
IfcAnnotationOccurrence::IfcAnnotationOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationOccurrence)) throw; entity = e; } 
// IfcAnnotationSurface
SHARED_PTR<IfcGeometricRepresentationItem> IfcAnnotationSurface::Item() { return reinterpret_pointer_cast<IfcBaseClass,IfcGeometricRepresentationItem>(*entity->getArgument(0)); }
bool IfcAnnotationSurface::hasTextureCoordinates() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcTextureCoordinate> IfcAnnotationSurface::TextureCoordinates() { return reinterpret_pointer_cast<IfcBaseClass,IfcTextureCoordinate>(*entity->getArgument(1)); }
bool IfcAnnotationSurface::is(Type::Enum v) { return v == Type::IfcAnnotationSurface || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcAnnotationSurface::type() { return Type::IfcAnnotationSurface; }
Type::Enum IfcAnnotationSurface::Class() { return Type::IfcAnnotationSurface; }
IfcAnnotationSurface::IfcAnnotationSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationSurface)) throw; entity = e; } 
// IfcAnnotationSurfaceOccurrence
bool IfcAnnotationSurfaceOccurrence::is(Type::Enum v) { return v == Type::IfcAnnotationSurfaceOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationSurfaceOccurrence::type() { return Type::IfcAnnotationSurfaceOccurrence; }
Type::Enum IfcAnnotationSurfaceOccurrence::Class() { return Type::IfcAnnotationSurfaceOccurrence; }
IfcAnnotationSurfaceOccurrence::IfcAnnotationSurfaceOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationSurfaceOccurrence)) throw; entity = e; } 
// IfcAnnotationSymbolOccurrence
bool IfcAnnotationSymbolOccurrence::is(Type::Enum v) { return v == Type::IfcAnnotationSymbolOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationSymbolOccurrence::type() { return Type::IfcAnnotationSymbolOccurrence; }
Type::Enum IfcAnnotationSymbolOccurrence::Class() { return Type::IfcAnnotationSymbolOccurrence; }
IfcAnnotationSymbolOccurrence::IfcAnnotationSymbolOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationSymbolOccurrence)) throw; entity = e; } 
// IfcAnnotationTextOccurrence
bool IfcAnnotationTextOccurrence::is(Type::Enum v) { return v == Type::IfcAnnotationTextOccurrence || IfcAnnotationOccurrence::is(v); }
Type::Enum IfcAnnotationTextOccurrence::type() { return Type::IfcAnnotationTextOccurrence; }
Type::Enum IfcAnnotationTextOccurrence::Class() { return Type::IfcAnnotationTextOccurrence; }
IfcAnnotationTextOccurrence::IfcAnnotationTextOccurrence(IfcAbstractEntityPtr e) { if (!is(Type::IfcAnnotationTextOccurrence)) throw; entity = e; } 
// IfcApplication
SHARED_PTR<IfcOrganization> IfcApplication::ApplicationDeveloper() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(0)); }
IfcLabel IfcApplication::Version() { return *entity->getArgument(1); }
IfcLabel IfcApplication::ApplicationFullName() { return *entity->getArgument(2); }
IfcIdentifier IfcApplication::ApplicationIdentifier() { return *entity->getArgument(3); }
bool IfcApplication::is(Type::Enum v) { return v == Type::IfcApplication; }
Type::Enum IfcApplication::type() { return Type::IfcApplication; }
Type::Enum IfcApplication::Class() { return Type::IfcApplication; }
IfcApplication::IfcApplication(IfcAbstractEntityPtr e) { if (!is(Type::IfcApplication)) throw; entity = e; } 
// IfcAppliedValue
bool IfcAppliedValue::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcAppliedValue::Name() { return *entity->getArgument(0); }
bool IfcAppliedValue::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcAppliedValue::Description() { return *entity->getArgument(1); }
bool IfcAppliedValue::hasAppliedValue() { return !entity->getArgument(2)->isNull(); }
IfcAppliedValueSelect IfcAppliedValue::AppliedValue() { return *entity->getArgument(2); }
bool IfcAppliedValue::hasUnitBasis() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcMeasureWithUnit> IfcAppliedValue::UnitBasis() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(3)); }
bool IfcAppliedValue::hasApplicableDate() { return !entity->getArgument(4)->isNull(); }
IfcDateTimeSelect IfcAppliedValue::ApplicableDate() { return *entity->getArgument(4); }
bool IfcAppliedValue::hasFixedUntilDate() { return !entity->getArgument(5)->isNull(); }
IfcDateTimeSelect IfcAppliedValue::FixedUntilDate() { return *entity->getArgument(5); }
IfcReferencesValueDocument::list IfcAppliedValue::ValuesReferenced() { RETURN_INVERSE(IfcReferencesValueDocument) }
IfcAppliedValueRelationship::list IfcAppliedValue::ValueOfComponents() { RETURN_INVERSE(IfcAppliedValueRelationship) }
IfcAppliedValueRelationship::list IfcAppliedValue::IsComponentIn() { RETURN_INVERSE(IfcAppliedValueRelationship) }
bool IfcAppliedValue::is(Type::Enum v) { return v == Type::IfcAppliedValue; }
Type::Enum IfcAppliedValue::type() { return Type::IfcAppliedValue; }
Type::Enum IfcAppliedValue::Class() { return Type::IfcAppliedValue; }
IfcAppliedValue::IfcAppliedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcAppliedValue)) throw; entity = e; } 
// IfcAppliedValueRelationship
SHARED_PTR<IfcAppliedValue> IfcAppliedValueRelationship::ComponentOfTotal() { return reinterpret_pointer_cast<IfcBaseClass,IfcAppliedValue>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > IfcAppliedValueRelationship::Components() { RETURN_AS_LIST(IfcAppliedValue,1) }
IfcArithmeticOperatorEnum::IfcArithmeticOperatorEnum IfcAppliedValueRelationship::ArithmeticOperator() { return IfcArithmeticOperatorEnum::FromString(*entity->getArgument(2)); }
bool IfcAppliedValueRelationship::hasName() { return !entity->getArgument(3)->isNull(); }
IfcLabel IfcAppliedValueRelationship::Name() { return *entity->getArgument(3); }
bool IfcAppliedValueRelationship::hasDescription() { return !entity->getArgument(4)->isNull(); }
IfcText IfcAppliedValueRelationship::Description() { return *entity->getArgument(4); }
bool IfcAppliedValueRelationship::is(Type::Enum v) { return v == Type::IfcAppliedValueRelationship; }
Type::Enum IfcAppliedValueRelationship::type() { return Type::IfcAppliedValueRelationship; }
Type::Enum IfcAppliedValueRelationship::Class() { return Type::IfcAppliedValueRelationship; }
IfcAppliedValueRelationship::IfcAppliedValueRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcAppliedValueRelationship)) throw; entity = e; } 
// IfcApproval
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
bool IfcApproval::is(Type::Enum v) { return v == Type::IfcApproval; }
Type::Enum IfcApproval::type() { return Type::IfcApproval; }
Type::Enum IfcApproval::Class() { return Type::IfcApproval; }
IfcApproval::IfcApproval(IfcAbstractEntityPtr e) { if (!is(Type::IfcApproval)) throw; entity = e; } 
// IfcApprovalActorRelationship
IfcActorSelect IfcApprovalActorRelationship::Actor() { return *entity->getArgument(0); }
SHARED_PTR<IfcApproval> IfcApprovalActorRelationship::Approval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(1)); }
SHARED_PTR<IfcActorRole> IfcApprovalActorRelationship::Role() { return reinterpret_pointer_cast<IfcBaseClass,IfcActorRole>(*entity->getArgument(2)); }
bool IfcApprovalActorRelationship::is(Type::Enum v) { return v == Type::IfcApprovalActorRelationship; }
Type::Enum IfcApprovalActorRelationship::type() { return Type::IfcApprovalActorRelationship; }
Type::Enum IfcApprovalActorRelationship::Class() { return Type::IfcApprovalActorRelationship; }
IfcApprovalActorRelationship::IfcApprovalActorRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcApprovalActorRelationship)) throw; entity = e; } 
// IfcApprovalPropertyRelationship
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcApprovalPropertyRelationship::ApprovedProperties() { RETURN_AS_LIST(IfcProperty,0) }
SHARED_PTR<IfcApproval> IfcApprovalPropertyRelationship::Approval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(1)); }
bool IfcApprovalPropertyRelationship::is(Type::Enum v) { return v == Type::IfcApprovalPropertyRelationship; }
Type::Enum IfcApprovalPropertyRelationship::type() { return Type::IfcApprovalPropertyRelationship; }
Type::Enum IfcApprovalPropertyRelationship::Class() { return Type::IfcApprovalPropertyRelationship; }
IfcApprovalPropertyRelationship::IfcApprovalPropertyRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcApprovalPropertyRelationship)) throw; entity = e; } 
// IfcApprovalRelationship
SHARED_PTR<IfcApproval> IfcApprovalRelationship::RelatedApproval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(0)); }
SHARED_PTR<IfcApproval> IfcApprovalRelationship::RelatingApproval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(1)); }
bool IfcApprovalRelationship::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcApprovalRelationship::Description() { return *entity->getArgument(2); }
IfcLabel IfcApprovalRelationship::Name() { return *entity->getArgument(3); }
bool IfcApprovalRelationship::is(Type::Enum v) { return v == Type::IfcApprovalRelationship; }
Type::Enum IfcApprovalRelationship::type() { return Type::IfcApprovalRelationship; }
Type::Enum IfcApprovalRelationship::Class() { return Type::IfcApprovalRelationship; }
IfcApprovalRelationship::IfcApprovalRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcApprovalRelationship)) throw; entity = e; } 
// IfcArbitraryClosedProfileDef
SHARED_PTR<IfcCurve> IfcArbitraryClosedProfileDef::OuterCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
bool IfcArbitraryClosedProfileDef::is(Type::Enum v) { return v == Type::IfcArbitraryClosedProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcArbitraryClosedProfileDef::type() { return Type::IfcArbitraryClosedProfileDef; }
Type::Enum IfcArbitraryClosedProfileDef::Class() { return Type::IfcArbitraryClosedProfileDef; }
IfcArbitraryClosedProfileDef::IfcArbitraryClosedProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcArbitraryClosedProfileDef)) throw; entity = e; } 
// IfcArbitraryOpenProfileDef
SHARED_PTR<IfcBoundedCurve> IfcArbitraryOpenProfileDef::Curve() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundedCurve>(*entity->getArgument(2)); }
bool IfcArbitraryOpenProfileDef::is(Type::Enum v) { return v == Type::IfcArbitraryOpenProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcArbitraryOpenProfileDef::type() { return Type::IfcArbitraryOpenProfileDef; }
Type::Enum IfcArbitraryOpenProfileDef::Class() { return Type::IfcArbitraryOpenProfileDef; }
IfcArbitraryOpenProfileDef::IfcArbitraryOpenProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcArbitraryOpenProfileDef)) throw; entity = e; } 
// IfcArbitraryProfileDefWithVoids
SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > IfcArbitraryProfileDefWithVoids::InnerCurves() { RETURN_AS_LIST(IfcCurve,3) }
bool IfcArbitraryProfileDefWithVoids::is(Type::Enum v) { return v == Type::IfcArbitraryProfileDefWithVoids || IfcArbitraryClosedProfileDef::is(v); }
Type::Enum IfcArbitraryProfileDefWithVoids::type() { return Type::IfcArbitraryProfileDefWithVoids; }
Type::Enum IfcArbitraryProfileDefWithVoids::Class() { return Type::IfcArbitraryProfileDefWithVoids; }
IfcArbitraryProfileDefWithVoids::IfcArbitraryProfileDefWithVoids(IfcAbstractEntityPtr e) { if (!is(Type::IfcArbitraryProfileDefWithVoids)) throw; entity = e; } 
// IfcAsset
IfcIdentifier IfcAsset::AssetID() { return *entity->getArgument(5); }
SHARED_PTR<IfcCostValue> IfcAsset::OriginalValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(6)); }
SHARED_PTR<IfcCostValue> IfcAsset::CurrentValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(7)); }
SHARED_PTR<IfcCostValue> IfcAsset::TotalReplacementCost() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(8)); }
IfcActorSelect IfcAsset::Owner() { return *entity->getArgument(9); }
IfcActorSelect IfcAsset::User() { return *entity->getArgument(10); }
SHARED_PTR<IfcPerson> IfcAsset::ResponsiblePerson() { return reinterpret_pointer_cast<IfcBaseClass,IfcPerson>(*entity->getArgument(11)); }
SHARED_PTR<IfcCalendarDate> IfcAsset::IncorporationDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(12)); }
SHARED_PTR<IfcCostValue> IfcAsset::DepreciatedValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(13)); }
bool IfcAsset::is(Type::Enum v) { return v == Type::IfcAsset || IfcGroup::is(v); }
Type::Enum IfcAsset::type() { return Type::IfcAsset; }
Type::Enum IfcAsset::Class() { return Type::IfcAsset; }
IfcAsset::IfcAsset(IfcAbstractEntityPtr e) { if (!is(Type::IfcAsset)) throw; entity = e; } 
// IfcAsymmetricIShapeProfileDef
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::TopFlangeWidth() { return *entity->getArgument(8); }
bool IfcAsymmetricIShapeProfileDef::hasTopFlangeThickness() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::TopFlangeThickness() { return *entity->getArgument(9); }
bool IfcAsymmetricIShapeProfileDef::hasTopFlangeFilletRadius() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::TopFlangeFilletRadius() { return *entity->getArgument(10); }
bool IfcAsymmetricIShapeProfileDef::hasCentreOfGravityInY() { return !entity->getArgument(11)->isNull(); }
IfcPositiveLengthMeasure IfcAsymmetricIShapeProfileDef::CentreOfGravityInY() { return *entity->getArgument(11); }
bool IfcAsymmetricIShapeProfileDef::is(Type::Enum v) { return v == Type::IfcAsymmetricIShapeProfileDef || IfcIShapeProfileDef::is(v); }
Type::Enum IfcAsymmetricIShapeProfileDef::type() { return Type::IfcAsymmetricIShapeProfileDef; }
Type::Enum IfcAsymmetricIShapeProfileDef::Class() { return Type::IfcAsymmetricIShapeProfileDef; }
IfcAsymmetricIShapeProfileDef::IfcAsymmetricIShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcAsymmetricIShapeProfileDef)) throw; entity = e; } 
// IfcAxis1Placement
bool IfcAxis1Placement::hasAxis() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcDirection> IfcAxis1Placement::Axis() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
bool IfcAxis1Placement::is(Type::Enum v) { return v == Type::IfcAxis1Placement || IfcPlacement::is(v); }
Type::Enum IfcAxis1Placement::type() { return Type::IfcAxis1Placement; }
Type::Enum IfcAxis1Placement::Class() { return Type::IfcAxis1Placement; }
IfcAxis1Placement::IfcAxis1Placement(IfcAbstractEntityPtr e) { if (!is(Type::IfcAxis1Placement)) throw; entity = e; } 
// IfcAxis2Placement2D
bool IfcAxis2Placement2D::hasRefDirection() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcDirection> IfcAxis2Placement2D::RefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
bool IfcAxis2Placement2D::is(Type::Enum v) { return v == Type::IfcAxis2Placement2D || IfcPlacement::is(v); }
Type::Enum IfcAxis2Placement2D::type() { return Type::IfcAxis2Placement2D; }
Type::Enum IfcAxis2Placement2D::Class() { return Type::IfcAxis2Placement2D; }
IfcAxis2Placement2D::IfcAxis2Placement2D(IfcAbstractEntityPtr e) { if (!is(Type::IfcAxis2Placement2D)) throw; entity = e; } 
// IfcAxis2Placement3D
bool IfcAxis2Placement3D::hasAxis() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcDirection> IfcAxis2Placement3D::Axis() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
bool IfcAxis2Placement3D::hasRefDirection() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR<IfcDirection> IfcAxis2Placement3D::RefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(2)); }
bool IfcAxis2Placement3D::is(Type::Enum v) { return v == Type::IfcAxis2Placement3D || IfcPlacement::is(v); }
Type::Enum IfcAxis2Placement3D::type() { return Type::IfcAxis2Placement3D; }
Type::Enum IfcAxis2Placement3D::Class() { return Type::IfcAxis2Placement3D; }
IfcAxis2Placement3D::IfcAxis2Placement3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcAxis2Placement3D)) throw; entity = e; } 
// IfcBSplineCurve
int IfcBSplineCurve::Degree() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcBSplineCurve::ControlPointsList() { RETURN_AS_LIST(IfcCartesianPoint,1) }
IfcBSplineCurveForm::IfcBSplineCurveForm IfcBSplineCurve::CurveForm() { return IfcBSplineCurveForm::FromString(*entity->getArgument(2)); }
bool IfcBSplineCurve::ClosedCurve() { return *entity->getArgument(3); }
bool IfcBSplineCurve::SelfIntersect() { return *entity->getArgument(4); }
bool IfcBSplineCurve::is(Type::Enum v) { return v == Type::IfcBSplineCurve || IfcBoundedCurve::is(v); }
Type::Enum IfcBSplineCurve::type() { return Type::IfcBSplineCurve; }
Type::Enum IfcBSplineCurve::Class() { return Type::IfcBSplineCurve; }
IfcBSplineCurve::IfcBSplineCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcBSplineCurve)) throw; entity = e; } 
// IfcBeam
bool IfcBeam::is(Type::Enum v) { return v == Type::IfcBeam || IfcBuildingElement::is(v); }
Type::Enum IfcBeam::type() { return Type::IfcBeam; }
Type::Enum IfcBeam::Class() { return Type::IfcBeam; }
IfcBeam::IfcBeam(IfcAbstractEntityPtr e) { if (!is(Type::IfcBeam)) throw; entity = e; } 
// IfcBeamType
IfcBeamTypeEnum::IfcBeamTypeEnum IfcBeamType::PredefinedType() { return IfcBeamTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcBeamType::is(Type::Enum v) { return v == Type::IfcBeamType || IfcBuildingElementType::is(v); }
Type::Enum IfcBeamType::type() { return Type::IfcBeamType; }
Type::Enum IfcBeamType::Class() { return Type::IfcBeamType; }
IfcBeamType::IfcBeamType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBeamType)) throw; entity = e; } 
// IfcBezierCurve
bool IfcBezierCurve::is(Type::Enum v) { return v == Type::IfcBezierCurve || IfcBSplineCurve::is(v); }
Type::Enum IfcBezierCurve::type() { return Type::IfcBezierCurve; }
Type::Enum IfcBezierCurve::Class() { return Type::IfcBezierCurve; }
IfcBezierCurve::IfcBezierCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcBezierCurve)) throw; entity = e; } 
// IfcBlobTexture
IfcIdentifier IfcBlobTexture::RasterFormat() { return *entity->getArgument(4); }
bool IfcBlobTexture::RasterCode() { return *entity->getArgument(5); }
bool IfcBlobTexture::is(Type::Enum v) { return v == Type::IfcBlobTexture || IfcSurfaceTexture::is(v); }
Type::Enum IfcBlobTexture::type() { return Type::IfcBlobTexture; }
Type::Enum IfcBlobTexture::Class() { return Type::IfcBlobTexture; }
IfcBlobTexture::IfcBlobTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcBlobTexture)) throw; entity = e; } 
// IfcBlock
IfcPositiveLengthMeasure IfcBlock::XLength() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcBlock::YLength() { return *entity->getArgument(2); }
IfcPositiveLengthMeasure IfcBlock::ZLength() { return *entity->getArgument(3); }
bool IfcBlock::is(Type::Enum v) { return v == Type::IfcBlock || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcBlock::type() { return Type::IfcBlock; }
Type::Enum IfcBlock::Class() { return Type::IfcBlock; }
IfcBlock::IfcBlock(IfcAbstractEntityPtr e) { if (!is(Type::IfcBlock)) throw; entity = e; } 
// IfcBoilerType
IfcBoilerTypeEnum::IfcBoilerTypeEnum IfcBoilerType::PredefinedType() { return IfcBoilerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcBoilerType::is(Type::Enum v) { return v == Type::IfcBoilerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcBoilerType::type() { return Type::IfcBoilerType; }
Type::Enum IfcBoilerType::Class() { return Type::IfcBoilerType; }
IfcBoilerType::IfcBoilerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoilerType)) throw; entity = e; } 
// IfcBooleanClippingResult
bool IfcBooleanClippingResult::is(Type::Enum v) { return v == Type::IfcBooleanClippingResult || IfcBooleanResult::is(v); }
Type::Enum IfcBooleanClippingResult::type() { return Type::IfcBooleanClippingResult; }
Type::Enum IfcBooleanClippingResult::Class() { return Type::IfcBooleanClippingResult; }
IfcBooleanClippingResult::IfcBooleanClippingResult(IfcAbstractEntityPtr e) { if (!is(Type::IfcBooleanClippingResult)) throw; entity = e; } 
// IfcBooleanResult
IfcBooleanOperator::IfcBooleanOperator IfcBooleanResult::Operator() { return IfcBooleanOperator::FromString(*entity->getArgument(0)); }
IfcBooleanOperand IfcBooleanResult::FirstOperand() { return *entity->getArgument(1); }
IfcBooleanOperand IfcBooleanResult::SecondOperand() { return *entity->getArgument(2); }
bool IfcBooleanResult::is(Type::Enum v) { return v == Type::IfcBooleanResult || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcBooleanResult::type() { return Type::IfcBooleanResult; }
Type::Enum IfcBooleanResult::Class() { return Type::IfcBooleanResult; }
IfcBooleanResult::IfcBooleanResult(IfcAbstractEntityPtr e) { if (!is(Type::IfcBooleanResult)) throw; entity = e; } 
// IfcBoundaryCondition
bool IfcBoundaryCondition::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcBoundaryCondition::Name() { return *entity->getArgument(0); }
bool IfcBoundaryCondition::is(Type::Enum v) { return v == Type::IfcBoundaryCondition; }
Type::Enum IfcBoundaryCondition::type() { return Type::IfcBoundaryCondition; }
Type::Enum IfcBoundaryCondition::Class() { return Type::IfcBoundaryCondition; }
IfcBoundaryCondition::IfcBoundaryCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryCondition)) throw; entity = e; } 
// IfcBoundaryEdgeCondition
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
bool IfcBoundaryEdgeCondition::is(Type::Enum v) { return v == Type::IfcBoundaryEdgeCondition || IfcBoundaryCondition::is(v); }
Type::Enum IfcBoundaryEdgeCondition::type() { return Type::IfcBoundaryEdgeCondition; }
Type::Enum IfcBoundaryEdgeCondition::Class() { return Type::IfcBoundaryEdgeCondition; }
IfcBoundaryEdgeCondition::IfcBoundaryEdgeCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryEdgeCondition)) throw; entity = e; } 
// IfcBoundaryFaceCondition
bool IfcBoundaryFaceCondition::hasLinearStiffnessByAreaX() { return !entity->getArgument(1)->isNull(); }
IfcModulusOfSubgradeReactionMeasure IfcBoundaryFaceCondition::LinearStiffnessByAreaX() { return *entity->getArgument(1); }
bool IfcBoundaryFaceCondition::hasLinearStiffnessByAreaY() { return !entity->getArgument(2)->isNull(); }
IfcModulusOfSubgradeReactionMeasure IfcBoundaryFaceCondition::LinearStiffnessByAreaY() { return *entity->getArgument(2); }
bool IfcBoundaryFaceCondition::hasLinearStiffnessByAreaZ() { return !entity->getArgument(3)->isNull(); }
IfcModulusOfSubgradeReactionMeasure IfcBoundaryFaceCondition::LinearStiffnessByAreaZ() { return *entity->getArgument(3); }
bool IfcBoundaryFaceCondition::is(Type::Enum v) { return v == Type::IfcBoundaryFaceCondition || IfcBoundaryCondition::is(v); }
Type::Enum IfcBoundaryFaceCondition::type() { return Type::IfcBoundaryFaceCondition; }
Type::Enum IfcBoundaryFaceCondition::Class() { return Type::IfcBoundaryFaceCondition; }
IfcBoundaryFaceCondition::IfcBoundaryFaceCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryFaceCondition)) throw; entity = e; } 
// IfcBoundaryNodeCondition
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
bool IfcBoundaryNodeCondition::is(Type::Enum v) { return v == Type::IfcBoundaryNodeCondition || IfcBoundaryCondition::is(v); }
Type::Enum IfcBoundaryNodeCondition::type() { return Type::IfcBoundaryNodeCondition; }
Type::Enum IfcBoundaryNodeCondition::Class() { return Type::IfcBoundaryNodeCondition; }
IfcBoundaryNodeCondition::IfcBoundaryNodeCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryNodeCondition)) throw; entity = e; } 
// IfcBoundaryNodeConditionWarping
bool IfcBoundaryNodeConditionWarping::hasWarpingStiffness() { return !entity->getArgument(7)->isNull(); }
IfcWarpingMomentMeasure IfcBoundaryNodeConditionWarping::WarpingStiffness() { return *entity->getArgument(7); }
bool IfcBoundaryNodeConditionWarping::is(Type::Enum v) { return v == Type::IfcBoundaryNodeConditionWarping || IfcBoundaryNodeCondition::is(v); }
Type::Enum IfcBoundaryNodeConditionWarping::type() { return Type::IfcBoundaryNodeConditionWarping; }
Type::Enum IfcBoundaryNodeConditionWarping::Class() { return Type::IfcBoundaryNodeConditionWarping; }
IfcBoundaryNodeConditionWarping::IfcBoundaryNodeConditionWarping(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundaryNodeConditionWarping)) throw; entity = e; } 
// IfcBoundedCurve
bool IfcBoundedCurve::is(Type::Enum v) { return v == Type::IfcBoundedCurve || IfcCurve::is(v); }
Type::Enum IfcBoundedCurve::type() { return Type::IfcBoundedCurve; }
Type::Enum IfcBoundedCurve::Class() { return Type::IfcBoundedCurve; }
IfcBoundedCurve::IfcBoundedCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundedCurve)) throw; entity = e; } 
// IfcBoundedSurface
bool IfcBoundedSurface::is(Type::Enum v) { return v == Type::IfcBoundedSurface || IfcSurface::is(v); }
Type::Enum IfcBoundedSurface::type() { return Type::IfcBoundedSurface; }
Type::Enum IfcBoundedSurface::Class() { return Type::IfcBoundedSurface; }
IfcBoundedSurface::IfcBoundedSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundedSurface)) throw; entity = e; } 
// IfcBoundingBox
SHARED_PTR<IfcCartesianPoint> IfcBoundingBox::Corner() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(0)); }
IfcPositiveLengthMeasure IfcBoundingBox::XDim() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcBoundingBox::YDim() { return *entity->getArgument(2); }
IfcPositiveLengthMeasure IfcBoundingBox::ZDim() { return *entity->getArgument(3); }
bool IfcBoundingBox::is(Type::Enum v) { return v == Type::IfcBoundingBox || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcBoundingBox::type() { return Type::IfcBoundingBox; }
Type::Enum IfcBoundingBox::Class() { return Type::IfcBoundingBox; }
IfcBoundingBox::IfcBoundingBox(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoundingBox)) throw; entity = e; } 
// IfcBoxedHalfSpace
SHARED_PTR<IfcBoundingBox> IfcBoxedHalfSpace::Enclosure() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundingBox>(*entity->getArgument(2)); }
bool IfcBoxedHalfSpace::is(Type::Enum v) { return v == Type::IfcBoxedHalfSpace || IfcHalfSpaceSolid::is(v); }
Type::Enum IfcBoxedHalfSpace::type() { return Type::IfcBoxedHalfSpace; }
Type::Enum IfcBoxedHalfSpace::Class() { return Type::IfcBoxedHalfSpace; }
IfcBoxedHalfSpace::IfcBoxedHalfSpace(IfcAbstractEntityPtr e) { if (!is(Type::IfcBoxedHalfSpace)) throw; entity = e; } 
// IfcBuilding
bool IfcBuilding::hasElevationOfRefHeight() { return !entity->getArgument(9)->isNull(); }
IfcLengthMeasure IfcBuilding::ElevationOfRefHeight() { return *entity->getArgument(9); }
bool IfcBuilding::hasElevationOfTerrain() { return !entity->getArgument(10)->isNull(); }
IfcLengthMeasure IfcBuilding::ElevationOfTerrain() { return *entity->getArgument(10); }
bool IfcBuilding::hasBuildingAddress() { return !entity->getArgument(11)->isNull(); }
SHARED_PTR<IfcPostalAddress> IfcBuilding::BuildingAddress() { return reinterpret_pointer_cast<IfcBaseClass,IfcPostalAddress>(*entity->getArgument(11)); }
bool IfcBuilding::is(Type::Enum v) { return v == Type::IfcBuilding || IfcSpatialStructureElement::is(v); }
Type::Enum IfcBuilding::type() { return Type::IfcBuilding; }
Type::Enum IfcBuilding::Class() { return Type::IfcBuilding; }
IfcBuilding::IfcBuilding(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuilding)) throw; entity = e; } 
// IfcBuildingElement
bool IfcBuildingElement::is(Type::Enum v) { return v == Type::IfcBuildingElement || IfcElement::is(v); }
Type::Enum IfcBuildingElement::type() { return Type::IfcBuildingElement; }
Type::Enum IfcBuildingElement::Class() { return Type::IfcBuildingElement; }
IfcBuildingElement::IfcBuildingElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElement)) throw; entity = e; } 
// IfcBuildingElementComponent
bool IfcBuildingElementComponent::is(Type::Enum v) { return v == Type::IfcBuildingElementComponent || IfcBuildingElement::is(v); }
Type::Enum IfcBuildingElementComponent::type() { return Type::IfcBuildingElementComponent; }
Type::Enum IfcBuildingElementComponent::Class() { return Type::IfcBuildingElementComponent; }
IfcBuildingElementComponent::IfcBuildingElementComponent(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementComponent)) throw; entity = e; } 
// IfcBuildingElementPart
bool IfcBuildingElementPart::is(Type::Enum v) { return v == Type::IfcBuildingElementPart || IfcBuildingElementComponent::is(v); }
Type::Enum IfcBuildingElementPart::type() { return Type::IfcBuildingElementPart; }
Type::Enum IfcBuildingElementPart::Class() { return Type::IfcBuildingElementPart; }
IfcBuildingElementPart::IfcBuildingElementPart(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementPart)) throw; entity = e; } 
// IfcBuildingElementProxy
bool IfcBuildingElementProxy::hasCompositionType() { return !entity->getArgument(8)->isNull(); }
IfcElementCompositionEnum::IfcElementCompositionEnum IfcBuildingElementProxy::CompositionType() { return IfcElementCompositionEnum::FromString(*entity->getArgument(8)); }
bool IfcBuildingElementProxy::is(Type::Enum v) { return v == Type::IfcBuildingElementProxy || IfcBuildingElement::is(v); }
Type::Enum IfcBuildingElementProxy::type() { return Type::IfcBuildingElementProxy; }
Type::Enum IfcBuildingElementProxy::Class() { return Type::IfcBuildingElementProxy; }
IfcBuildingElementProxy::IfcBuildingElementProxy(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementProxy)) throw; entity = e; } 
// IfcBuildingElementProxyType
IfcBuildingElementProxyTypeEnum::IfcBuildingElementProxyTypeEnum IfcBuildingElementProxyType::PredefinedType() { return IfcBuildingElementProxyTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcBuildingElementProxyType::is(Type::Enum v) { return v == Type::IfcBuildingElementProxyType || IfcBuildingElementType::is(v); }
Type::Enum IfcBuildingElementProxyType::type() { return Type::IfcBuildingElementProxyType; }
Type::Enum IfcBuildingElementProxyType::Class() { return Type::IfcBuildingElementProxyType; }
IfcBuildingElementProxyType::IfcBuildingElementProxyType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementProxyType)) throw; entity = e; } 
// IfcBuildingElementType
bool IfcBuildingElementType::is(Type::Enum v) { return v == Type::IfcBuildingElementType || IfcElementType::is(v); }
Type::Enum IfcBuildingElementType::type() { return Type::IfcBuildingElementType; }
Type::Enum IfcBuildingElementType::Class() { return Type::IfcBuildingElementType; }
IfcBuildingElementType::IfcBuildingElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingElementType)) throw; entity = e; } 
// IfcBuildingStorey
bool IfcBuildingStorey::hasElevation() { return !entity->getArgument(9)->isNull(); }
IfcLengthMeasure IfcBuildingStorey::Elevation() { return *entity->getArgument(9); }
bool IfcBuildingStorey::is(Type::Enum v) { return v == Type::IfcBuildingStorey || IfcSpatialStructureElement::is(v); }
Type::Enum IfcBuildingStorey::type() { return Type::IfcBuildingStorey; }
Type::Enum IfcBuildingStorey::Class() { return Type::IfcBuildingStorey; }
IfcBuildingStorey::IfcBuildingStorey(IfcAbstractEntityPtr e) { if (!is(Type::IfcBuildingStorey)) throw; entity = e; } 
// IfcCShapeProfileDef
IfcPositiveLengthMeasure IfcCShapeProfileDef::Depth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::Width() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::WallThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::Girth() { return *entity->getArgument(6); }
bool IfcCShapeProfileDef::hasInternalFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::InternalFilletRadius() { return *entity->getArgument(7); }
bool IfcCShapeProfileDef::hasCentreOfGravityInX() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcCShapeProfileDef::CentreOfGravityInX() { return *entity->getArgument(8); }
bool IfcCShapeProfileDef::is(Type::Enum v) { return v == Type::IfcCShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCShapeProfileDef::type() { return Type::IfcCShapeProfileDef; }
Type::Enum IfcCShapeProfileDef::Class() { return Type::IfcCShapeProfileDef; }
IfcCShapeProfileDef::IfcCShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCShapeProfileDef)) throw; entity = e; } 
// IfcCableCarrierFittingType
IfcCableCarrierFittingTypeEnum::IfcCableCarrierFittingTypeEnum IfcCableCarrierFittingType::PredefinedType() { return IfcCableCarrierFittingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCableCarrierFittingType::is(Type::Enum v) { return v == Type::IfcCableCarrierFittingType || IfcFlowFittingType::is(v); }
Type::Enum IfcCableCarrierFittingType::type() { return Type::IfcCableCarrierFittingType; }
Type::Enum IfcCableCarrierFittingType::Class() { return Type::IfcCableCarrierFittingType; }
IfcCableCarrierFittingType::IfcCableCarrierFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCableCarrierFittingType)) throw; entity = e; } 
// IfcCableCarrierSegmentType
IfcCableCarrierSegmentTypeEnum::IfcCableCarrierSegmentTypeEnum IfcCableCarrierSegmentType::PredefinedType() { return IfcCableCarrierSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCableCarrierSegmentType::is(Type::Enum v) { return v == Type::IfcCableCarrierSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcCableCarrierSegmentType::type() { return Type::IfcCableCarrierSegmentType; }
Type::Enum IfcCableCarrierSegmentType::Class() { return Type::IfcCableCarrierSegmentType; }
IfcCableCarrierSegmentType::IfcCableCarrierSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCableCarrierSegmentType)) throw; entity = e; } 
// IfcCableSegmentType
IfcCableSegmentTypeEnum::IfcCableSegmentTypeEnum IfcCableSegmentType::PredefinedType() { return IfcCableSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCableSegmentType::is(Type::Enum v) { return v == Type::IfcCableSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcCableSegmentType::type() { return Type::IfcCableSegmentType; }
Type::Enum IfcCableSegmentType::Class() { return Type::IfcCableSegmentType; }
IfcCableSegmentType::IfcCableSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCableSegmentType)) throw; entity = e; } 
// IfcCalendarDate
IfcDayInMonthNumber IfcCalendarDate::DayComponent() { return *entity->getArgument(0); }
IfcMonthInYearNumber IfcCalendarDate::MonthComponent() { return *entity->getArgument(1); }
IfcYearNumber IfcCalendarDate::YearComponent() { return *entity->getArgument(2); }
bool IfcCalendarDate::is(Type::Enum v) { return v == Type::IfcCalendarDate; }
Type::Enum IfcCalendarDate::type() { return Type::IfcCalendarDate; }
Type::Enum IfcCalendarDate::Class() { return Type::IfcCalendarDate; }
IfcCalendarDate::IfcCalendarDate(IfcAbstractEntityPtr e) { if (!is(Type::IfcCalendarDate)) throw; entity = e; } 
// IfcCartesianPoint
std::vector<IfcLengthMeasure> /*[1:3]*/ IfcCartesianPoint::Coordinates() { return *entity->getArgument(0); }
bool IfcCartesianPoint::is(Type::Enum v) { return v == Type::IfcCartesianPoint || IfcPoint::is(v); }
Type::Enum IfcCartesianPoint::type() { return Type::IfcCartesianPoint; }
Type::Enum IfcCartesianPoint::Class() { return Type::IfcCartesianPoint; }
IfcCartesianPoint::IfcCartesianPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianPoint)) throw; entity = e; } 
// IfcCartesianTransformationOperator
bool IfcCartesianTransformationOperator::hasAxis1() { return !entity->getArgument(0)->isNull(); }
SHARED_PTR<IfcDirection> IfcCartesianTransformationOperator::Axis1() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(0)); }
bool IfcCartesianTransformationOperator::hasAxis2() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcDirection> IfcCartesianTransformationOperator::Axis2() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(1)); }
SHARED_PTR<IfcCartesianPoint> IfcCartesianTransformationOperator::LocalOrigin() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(2)); }
bool IfcCartesianTransformationOperator::hasScale() { return !entity->getArgument(3)->isNull(); }
float IfcCartesianTransformationOperator::Scale() { return *entity->getArgument(3); }
bool IfcCartesianTransformationOperator::is(Type::Enum v) { return v == Type::IfcCartesianTransformationOperator || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCartesianTransformationOperator::type() { return Type::IfcCartesianTransformationOperator; }
Type::Enum IfcCartesianTransformationOperator::Class() { return Type::IfcCartesianTransformationOperator; }
IfcCartesianTransformationOperator::IfcCartesianTransformationOperator(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator)) throw; entity = e; } 
// IfcCartesianTransformationOperator2D
bool IfcCartesianTransformationOperator2D::is(Type::Enum v) { return v == Type::IfcCartesianTransformationOperator2D || IfcCartesianTransformationOperator::is(v); }
Type::Enum IfcCartesianTransformationOperator2D::type() { return Type::IfcCartesianTransformationOperator2D; }
Type::Enum IfcCartesianTransformationOperator2D::Class() { return Type::IfcCartesianTransformationOperator2D; }
IfcCartesianTransformationOperator2D::IfcCartesianTransformationOperator2D(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator2D)) throw; entity = e; } 
// IfcCartesianTransformationOperator2DnonUniform
bool IfcCartesianTransformationOperator2DnonUniform::hasScale2() { return !entity->getArgument(4)->isNull(); }
float IfcCartesianTransformationOperator2DnonUniform::Scale2() { return *entity->getArgument(4); }
bool IfcCartesianTransformationOperator2DnonUniform::is(Type::Enum v) { return v == Type::IfcCartesianTransformationOperator2DnonUniform || IfcCartesianTransformationOperator2D::is(v); }
Type::Enum IfcCartesianTransformationOperator2DnonUniform::type() { return Type::IfcCartesianTransformationOperator2DnonUniform; }
Type::Enum IfcCartesianTransformationOperator2DnonUniform::Class() { return Type::IfcCartesianTransformationOperator2DnonUniform; }
IfcCartesianTransformationOperator2DnonUniform::IfcCartesianTransformationOperator2DnonUniform(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator2DnonUniform)) throw; entity = e; } 
// IfcCartesianTransformationOperator3D
bool IfcCartesianTransformationOperator3D::hasAxis3() { return !entity->getArgument(4)->isNull(); }
SHARED_PTR<IfcDirection> IfcCartesianTransformationOperator3D::Axis3() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(4)); }
bool IfcCartesianTransformationOperator3D::is(Type::Enum v) { return v == Type::IfcCartesianTransformationOperator3D || IfcCartesianTransformationOperator::is(v); }
Type::Enum IfcCartesianTransformationOperator3D::type() { return Type::IfcCartesianTransformationOperator3D; }
Type::Enum IfcCartesianTransformationOperator3D::Class() { return Type::IfcCartesianTransformationOperator3D; }
IfcCartesianTransformationOperator3D::IfcCartesianTransformationOperator3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator3D)) throw; entity = e; } 
// IfcCartesianTransformationOperator3DnonUniform
bool IfcCartesianTransformationOperator3DnonUniform::hasScale2() { return !entity->getArgument(5)->isNull(); }
float IfcCartesianTransformationOperator3DnonUniform::Scale2() { return *entity->getArgument(5); }
bool IfcCartesianTransformationOperator3DnonUniform::hasScale3() { return !entity->getArgument(6)->isNull(); }
float IfcCartesianTransformationOperator3DnonUniform::Scale3() { return *entity->getArgument(6); }
bool IfcCartesianTransformationOperator3DnonUniform::is(Type::Enum v) { return v == Type::IfcCartesianTransformationOperator3DnonUniform || IfcCartesianTransformationOperator3D::is(v); }
Type::Enum IfcCartesianTransformationOperator3DnonUniform::type() { return Type::IfcCartesianTransformationOperator3DnonUniform; }
Type::Enum IfcCartesianTransformationOperator3DnonUniform::Class() { return Type::IfcCartesianTransformationOperator3DnonUniform; }
IfcCartesianTransformationOperator3DnonUniform::IfcCartesianTransformationOperator3DnonUniform(IfcAbstractEntityPtr e) { if (!is(Type::IfcCartesianTransformationOperator3DnonUniform)) throw; entity = e; } 
// IfcCenterLineProfileDef
IfcPositiveLengthMeasure IfcCenterLineProfileDef::Thickness() { return *entity->getArgument(3); }
bool IfcCenterLineProfileDef::is(Type::Enum v) { return v == Type::IfcCenterLineProfileDef || IfcArbitraryOpenProfileDef::is(v); }
Type::Enum IfcCenterLineProfileDef::type() { return Type::IfcCenterLineProfileDef; }
Type::Enum IfcCenterLineProfileDef::Class() { return Type::IfcCenterLineProfileDef; }
IfcCenterLineProfileDef::IfcCenterLineProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCenterLineProfileDef)) throw; entity = e; } 
// IfcChamferEdgeFeature
bool IfcChamferEdgeFeature::hasWidth() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcChamferEdgeFeature::Width() { return *entity->getArgument(9); }
bool IfcChamferEdgeFeature::hasHeight() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcChamferEdgeFeature::Height() { return *entity->getArgument(10); }
bool IfcChamferEdgeFeature::is(Type::Enum v) { return v == Type::IfcChamferEdgeFeature || IfcEdgeFeature::is(v); }
Type::Enum IfcChamferEdgeFeature::type() { return Type::IfcChamferEdgeFeature; }
Type::Enum IfcChamferEdgeFeature::Class() { return Type::IfcChamferEdgeFeature; }
IfcChamferEdgeFeature::IfcChamferEdgeFeature(IfcAbstractEntityPtr e) { if (!is(Type::IfcChamferEdgeFeature)) throw; entity = e; } 
// IfcChillerType
IfcChillerTypeEnum::IfcChillerTypeEnum IfcChillerType::PredefinedType() { return IfcChillerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcChillerType::is(Type::Enum v) { return v == Type::IfcChillerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcChillerType::type() { return Type::IfcChillerType; }
Type::Enum IfcChillerType::Class() { return Type::IfcChillerType; }
IfcChillerType::IfcChillerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcChillerType)) throw; entity = e; } 
// IfcCircle
IfcPositiveLengthMeasure IfcCircle::Radius() { return *entity->getArgument(1); }
bool IfcCircle::is(Type::Enum v) { return v == Type::IfcCircle || IfcConic::is(v); }
Type::Enum IfcCircle::type() { return Type::IfcCircle; }
Type::Enum IfcCircle::Class() { return Type::IfcCircle; }
IfcCircle::IfcCircle(IfcAbstractEntityPtr e) { if (!is(Type::IfcCircle)) throw; entity = e; } 
// IfcCircleHollowProfileDef
IfcPositiveLengthMeasure IfcCircleHollowProfileDef::WallThickness() { return *entity->getArgument(4); }
bool IfcCircleHollowProfileDef::is(Type::Enum v) { return v == Type::IfcCircleHollowProfileDef || IfcCircleProfileDef::is(v); }
Type::Enum IfcCircleHollowProfileDef::type() { return Type::IfcCircleHollowProfileDef; }
Type::Enum IfcCircleHollowProfileDef::Class() { return Type::IfcCircleHollowProfileDef; }
IfcCircleHollowProfileDef::IfcCircleHollowProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCircleHollowProfileDef)) throw; entity = e; } 
// IfcCircleProfileDef
IfcPositiveLengthMeasure IfcCircleProfileDef::Radius() { return *entity->getArgument(3); }
bool IfcCircleProfileDef::is(Type::Enum v) { return v == Type::IfcCircleProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCircleProfileDef::type() { return Type::IfcCircleProfileDef; }
Type::Enum IfcCircleProfileDef::Class() { return Type::IfcCircleProfileDef; }
IfcCircleProfileDef::IfcCircleProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCircleProfileDef)) throw; entity = e; } 
// IfcClassification
IfcLabel IfcClassification::Source() { return *entity->getArgument(0); }
IfcLabel IfcClassification::Edition() { return *entity->getArgument(1); }
bool IfcClassification::hasEditionDate() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR<IfcCalendarDate> IfcClassification::EditionDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(2)); }
IfcLabel IfcClassification::Name() { return *entity->getArgument(3); }
IfcClassificationItem::list IfcClassification::Contains() { RETURN_INVERSE(IfcClassificationItem) }
bool IfcClassification::is(Type::Enum v) { return v == Type::IfcClassification; }
Type::Enum IfcClassification::type() { return Type::IfcClassification; }
Type::Enum IfcClassification::Class() { return Type::IfcClassification; }
IfcClassification::IfcClassification(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassification)) throw; entity = e; } 
// IfcClassificationItem
SHARED_PTR<IfcClassificationNotationFacet> IfcClassificationItem::Notation() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassificationNotationFacet>(*entity->getArgument(0)); }
bool IfcClassificationItem::hasItemOf() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcClassification> IfcClassificationItem::ItemOf() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassification>(*entity->getArgument(1)); }
IfcLabel IfcClassificationItem::Title() { return *entity->getArgument(2); }
IfcClassificationItemRelationship::list IfcClassificationItem::IsClassifiedItemIn() { RETURN_INVERSE(IfcClassificationItemRelationship) }
IfcClassificationItemRelationship::list IfcClassificationItem::IsClassifyingItemIn() { RETURN_INVERSE(IfcClassificationItemRelationship) }
bool IfcClassificationItem::is(Type::Enum v) { return v == Type::IfcClassificationItem; }
Type::Enum IfcClassificationItem::type() { return Type::IfcClassificationItem; }
Type::Enum IfcClassificationItem::Class() { return Type::IfcClassificationItem; }
IfcClassificationItem::IfcClassificationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationItem)) throw; entity = e; } 
// IfcClassificationItemRelationship
SHARED_PTR<IfcClassificationItem> IfcClassificationItemRelationship::RelatingItem() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassificationItem>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcClassificationItem> > IfcClassificationItemRelationship::RelatedItems() { RETURN_AS_LIST(IfcClassificationItem,1) }
bool IfcClassificationItemRelationship::is(Type::Enum v) { return v == Type::IfcClassificationItemRelationship; }
Type::Enum IfcClassificationItemRelationship::type() { return Type::IfcClassificationItemRelationship; }
Type::Enum IfcClassificationItemRelationship::Class() { return Type::IfcClassificationItemRelationship; }
IfcClassificationItemRelationship::IfcClassificationItemRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationItemRelationship)) throw; entity = e; } 
// IfcClassificationNotation
SHARED_PTR< IfcTemplatedEntityList<IfcClassificationNotationFacet> > IfcClassificationNotation::NotationFacets() { RETURN_AS_LIST(IfcClassificationNotationFacet,0) }
bool IfcClassificationNotation::is(Type::Enum v) { return v == Type::IfcClassificationNotation; }
Type::Enum IfcClassificationNotation::type() { return Type::IfcClassificationNotation; }
Type::Enum IfcClassificationNotation::Class() { return Type::IfcClassificationNotation; }
IfcClassificationNotation::IfcClassificationNotation(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationNotation)) throw; entity = e; } 
// IfcClassificationNotationFacet
IfcLabel IfcClassificationNotationFacet::NotationValue() { return *entity->getArgument(0); }
bool IfcClassificationNotationFacet::is(Type::Enum v) { return v == Type::IfcClassificationNotationFacet; }
Type::Enum IfcClassificationNotationFacet::type() { return Type::IfcClassificationNotationFacet; }
Type::Enum IfcClassificationNotationFacet::Class() { return Type::IfcClassificationNotationFacet; }
IfcClassificationNotationFacet::IfcClassificationNotationFacet(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationNotationFacet)) throw; entity = e; } 
// IfcClassificationReference
bool IfcClassificationReference::hasReferencedSource() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcClassification> IfcClassificationReference::ReferencedSource() { return reinterpret_pointer_cast<IfcBaseClass,IfcClassification>(*entity->getArgument(3)); }
bool IfcClassificationReference::is(Type::Enum v) { return v == Type::IfcClassificationReference || IfcExternalReference::is(v); }
Type::Enum IfcClassificationReference::type() { return Type::IfcClassificationReference; }
Type::Enum IfcClassificationReference::Class() { return Type::IfcClassificationReference; }
IfcClassificationReference::IfcClassificationReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcClassificationReference)) throw; entity = e; } 
// IfcClosedShell
bool IfcClosedShell::is(Type::Enum v) { return v == Type::IfcClosedShell || IfcConnectedFaceSet::is(v); }
Type::Enum IfcClosedShell::type() { return Type::IfcClosedShell; }
Type::Enum IfcClosedShell::Class() { return Type::IfcClosedShell; }
IfcClosedShell::IfcClosedShell(IfcAbstractEntityPtr e) { if (!is(Type::IfcClosedShell)) throw; entity = e; } 
// IfcCoilType
IfcCoilTypeEnum::IfcCoilTypeEnum IfcCoilType::PredefinedType() { return IfcCoilTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCoilType::is(Type::Enum v) { return v == Type::IfcCoilType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCoilType::type() { return Type::IfcCoilType; }
Type::Enum IfcCoilType::Class() { return Type::IfcCoilType; }
IfcCoilType::IfcCoilType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoilType)) throw; entity = e; } 
// IfcColourRgb
IfcNormalisedRatioMeasure IfcColourRgb::Red() { return *entity->getArgument(1); }
IfcNormalisedRatioMeasure IfcColourRgb::Green() { return *entity->getArgument(2); }
IfcNormalisedRatioMeasure IfcColourRgb::Blue() { return *entity->getArgument(3); }
bool IfcColourRgb::is(Type::Enum v) { return v == Type::IfcColourRgb || IfcColourSpecification::is(v); }
Type::Enum IfcColourRgb::type() { return Type::IfcColourRgb; }
Type::Enum IfcColourRgb::Class() { return Type::IfcColourRgb; }
IfcColourRgb::IfcColourRgb(IfcAbstractEntityPtr e) { if (!is(Type::IfcColourRgb)) throw; entity = e; } 
// IfcColourSpecification
bool IfcColourSpecification::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcColourSpecification::Name() { return *entity->getArgument(0); }
bool IfcColourSpecification::is(Type::Enum v) { return v == Type::IfcColourSpecification; }
Type::Enum IfcColourSpecification::type() { return Type::IfcColourSpecification; }
Type::Enum IfcColourSpecification::Class() { return Type::IfcColourSpecification; }
IfcColourSpecification::IfcColourSpecification(IfcAbstractEntityPtr e) { if (!is(Type::IfcColourSpecification)) throw; entity = e; } 
// IfcColumn
bool IfcColumn::is(Type::Enum v) { return v == Type::IfcColumn || IfcBuildingElement::is(v); }
Type::Enum IfcColumn::type() { return Type::IfcColumn; }
Type::Enum IfcColumn::Class() { return Type::IfcColumn; }
IfcColumn::IfcColumn(IfcAbstractEntityPtr e) { if (!is(Type::IfcColumn)) throw; entity = e; } 
// IfcColumnType
IfcColumnTypeEnum::IfcColumnTypeEnum IfcColumnType::PredefinedType() { return IfcColumnTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcColumnType::is(Type::Enum v) { return v == Type::IfcColumnType || IfcBuildingElementType::is(v); }
Type::Enum IfcColumnType::type() { return Type::IfcColumnType; }
Type::Enum IfcColumnType::Class() { return Type::IfcColumnType; }
IfcColumnType::IfcColumnType(IfcAbstractEntityPtr e) { if (!is(Type::IfcColumnType)) throw; entity = e; } 
// IfcComplexProperty
IfcIdentifier IfcComplexProperty::UsageName() { return *entity->getArgument(2); }
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcComplexProperty::HasProperties() { RETURN_AS_LIST(IfcProperty,3) }
bool IfcComplexProperty::is(Type::Enum v) { return v == Type::IfcComplexProperty || IfcProperty::is(v); }
Type::Enum IfcComplexProperty::type() { return Type::IfcComplexProperty; }
Type::Enum IfcComplexProperty::Class() { return Type::IfcComplexProperty; }
IfcComplexProperty::IfcComplexProperty(IfcAbstractEntityPtr e) { if (!is(Type::IfcComplexProperty)) throw; entity = e; } 
// IfcCompositeCurve
SHARED_PTR< IfcTemplatedEntityList<IfcCompositeCurveSegment> > IfcCompositeCurve::Segments() { RETURN_AS_LIST(IfcCompositeCurveSegment,0) }
bool IfcCompositeCurve::SelfIntersect() { return *entity->getArgument(1); }
bool IfcCompositeCurve::is(Type::Enum v) { return v == Type::IfcCompositeCurve || IfcBoundedCurve::is(v); }
Type::Enum IfcCompositeCurve::type() { return Type::IfcCompositeCurve; }
Type::Enum IfcCompositeCurve::Class() { return Type::IfcCompositeCurve; }
IfcCompositeCurve::IfcCompositeCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompositeCurve)) throw; entity = e; } 
// IfcCompositeCurveSegment
IfcTransitionCode::IfcTransitionCode IfcCompositeCurveSegment::Transition() { return IfcTransitionCode::FromString(*entity->getArgument(0)); }
bool IfcCompositeCurveSegment::SameSense() { return *entity->getArgument(1); }
SHARED_PTR<IfcCurve> IfcCompositeCurveSegment::ParentCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
IfcCompositeCurve::list IfcCompositeCurveSegment::UsingCurves() { RETURN_INVERSE(IfcCompositeCurve) }
bool IfcCompositeCurveSegment::is(Type::Enum v) { return v == Type::IfcCompositeCurveSegment || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCompositeCurveSegment::type() { return Type::IfcCompositeCurveSegment; }
Type::Enum IfcCompositeCurveSegment::Class() { return Type::IfcCompositeCurveSegment; }
IfcCompositeCurveSegment::IfcCompositeCurveSegment(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompositeCurveSegment)) throw; entity = e; } 
// IfcCompositeProfileDef
SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > IfcCompositeProfileDef::Profiles() { RETURN_AS_LIST(IfcProfileDef,2) }
bool IfcCompositeProfileDef::hasLabel() { return !entity->getArgument(3)->isNull(); }
IfcLabel IfcCompositeProfileDef::Label() { return *entity->getArgument(3); }
bool IfcCompositeProfileDef::is(Type::Enum v) { return v == Type::IfcCompositeProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcCompositeProfileDef::type() { return Type::IfcCompositeProfileDef; }
Type::Enum IfcCompositeProfileDef::Class() { return Type::IfcCompositeProfileDef; }
IfcCompositeProfileDef::IfcCompositeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompositeProfileDef)) throw; entity = e; } 
// IfcCompressorType
IfcCompressorTypeEnum::IfcCompressorTypeEnum IfcCompressorType::PredefinedType() { return IfcCompressorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCompressorType::is(Type::Enum v) { return v == Type::IfcCompressorType || IfcFlowMovingDeviceType::is(v); }
Type::Enum IfcCompressorType::type() { return Type::IfcCompressorType; }
Type::Enum IfcCompressorType::Class() { return Type::IfcCompressorType; }
IfcCompressorType::IfcCompressorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCompressorType)) throw; entity = e; } 
// IfcCondenserType
IfcCondenserTypeEnum::IfcCondenserTypeEnum IfcCondenserType::PredefinedType() { return IfcCondenserTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCondenserType::is(Type::Enum v) { return v == Type::IfcCondenserType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCondenserType::type() { return Type::IfcCondenserType; }
Type::Enum IfcCondenserType::Class() { return Type::IfcCondenserType; }
IfcCondenserType::IfcCondenserType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCondenserType)) throw; entity = e; } 
// IfcCondition
bool IfcCondition::is(Type::Enum v) { return v == Type::IfcCondition || IfcGroup::is(v); }
Type::Enum IfcCondition::type() { return Type::IfcCondition; }
Type::Enum IfcCondition::Class() { return Type::IfcCondition; }
IfcCondition::IfcCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcCondition)) throw; entity = e; } 
// IfcConditionCriterion
IfcConditionCriterionSelect IfcConditionCriterion::Criterion() { return *entity->getArgument(5); }
IfcDateTimeSelect IfcConditionCriterion::CriterionDateTime() { return *entity->getArgument(6); }
bool IfcConditionCriterion::is(Type::Enum v) { return v == Type::IfcConditionCriterion || IfcControl::is(v); }
Type::Enum IfcConditionCriterion::type() { return Type::IfcConditionCriterion; }
Type::Enum IfcConditionCriterion::Class() { return Type::IfcConditionCriterion; }
IfcConditionCriterion::IfcConditionCriterion(IfcAbstractEntityPtr e) { if (!is(Type::IfcConditionCriterion)) throw; entity = e; } 
// IfcConic
IfcAxis2Placement IfcConic::Position() { return *entity->getArgument(0); }
bool IfcConic::is(Type::Enum v) { return v == Type::IfcConic || IfcCurve::is(v); }
Type::Enum IfcConic::type() { return Type::IfcConic; }
Type::Enum IfcConic::Class() { return Type::IfcConic; }
IfcConic::IfcConic(IfcAbstractEntityPtr e) { if (!is(Type::IfcConic)) throw; entity = e; } 
// IfcConnectedFaceSet
SHARED_PTR< IfcTemplatedEntityList<IfcFace> > IfcConnectedFaceSet::CfsFaces() { RETURN_AS_LIST(IfcFace,0) }
bool IfcConnectedFaceSet::is(Type::Enum v) { return v == Type::IfcConnectedFaceSet || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcConnectedFaceSet::type() { return Type::IfcConnectedFaceSet; }
Type::Enum IfcConnectedFaceSet::Class() { return Type::IfcConnectedFaceSet; }
IfcConnectedFaceSet::IfcConnectedFaceSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectedFaceSet)) throw; entity = e; } 
// IfcConnectionCurveGeometry
IfcCurveOrEdgeCurve IfcConnectionCurveGeometry::CurveOnRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionCurveGeometry::hasCurveOnRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcCurveOrEdgeCurve IfcConnectionCurveGeometry::CurveOnRelatedElement() { return *entity->getArgument(1); }
bool IfcConnectionCurveGeometry::is(Type::Enum v) { return v == Type::IfcConnectionCurveGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionCurveGeometry::type() { return Type::IfcConnectionCurveGeometry; }
Type::Enum IfcConnectionCurveGeometry::Class() { return Type::IfcConnectionCurveGeometry; }
IfcConnectionCurveGeometry::IfcConnectionCurveGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionCurveGeometry)) throw; entity = e; } 
// IfcConnectionGeometry
bool IfcConnectionGeometry::is(Type::Enum v) { return v == Type::IfcConnectionGeometry; }
Type::Enum IfcConnectionGeometry::type() { return Type::IfcConnectionGeometry; }
Type::Enum IfcConnectionGeometry::Class() { return Type::IfcConnectionGeometry; }
IfcConnectionGeometry::IfcConnectionGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionGeometry)) throw; entity = e; } 
// IfcConnectionPointEccentricity
bool IfcConnectionPointEccentricity::hasEccentricityInX() { return !entity->getArgument(2)->isNull(); }
IfcLengthMeasure IfcConnectionPointEccentricity::EccentricityInX() { return *entity->getArgument(2); }
bool IfcConnectionPointEccentricity::hasEccentricityInY() { return !entity->getArgument(3)->isNull(); }
IfcLengthMeasure IfcConnectionPointEccentricity::EccentricityInY() { return *entity->getArgument(3); }
bool IfcConnectionPointEccentricity::hasEccentricityInZ() { return !entity->getArgument(4)->isNull(); }
IfcLengthMeasure IfcConnectionPointEccentricity::EccentricityInZ() { return *entity->getArgument(4); }
bool IfcConnectionPointEccentricity::is(Type::Enum v) { return v == Type::IfcConnectionPointEccentricity || IfcConnectionPointGeometry::is(v); }
Type::Enum IfcConnectionPointEccentricity::type() { return Type::IfcConnectionPointEccentricity; }
Type::Enum IfcConnectionPointEccentricity::Class() { return Type::IfcConnectionPointEccentricity; }
IfcConnectionPointEccentricity::IfcConnectionPointEccentricity(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionPointEccentricity)) throw; entity = e; } 
// IfcConnectionPointGeometry
IfcPointOrVertexPoint IfcConnectionPointGeometry::PointOnRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionPointGeometry::hasPointOnRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcPointOrVertexPoint IfcConnectionPointGeometry::PointOnRelatedElement() { return *entity->getArgument(1); }
bool IfcConnectionPointGeometry::is(Type::Enum v) { return v == Type::IfcConnectionPointGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionPointGeometry::type() { return Type::IfcConnectionPointGeometry; }
Type::Enum IfcConnectionPointGeometry::Class() { return Type::IfcConnectionPointGeometry; }
IfcConnectionPointGeometry::IfcConnectionPointGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionPointGeometry)) throw; entity = e; } 
// IfcConnectionPortGeometry
IfcAxis2Placement IfcConnectionPortGeometry::LocationAtRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionPortGeometry::hasLocationAtRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcAxis2Placement IfcConnectionPortGeometry::LocationAtRelatedElement() { return *entity->getArgument(1); }
SHARED_PTR<IfcProfileDef> IfcConnectionPortGeometry::ProfileOfPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(2)); }
bool IfcConnectionPortGeometry::is(Type::Enum v) { return v == Type::IfcConnectionPortGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionPortGeometry::type() { return Type::IfcConnectionPortGeometry; }
Type::Enum IfcConnectionPortGeometry::Class() { return Type::IfcConnectionPortGeometry; }
IfcConnectionPortGeometry::IfcConnectionPortGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionPortGeometry)) throw; entity = e; } 
// IfcConnectionSurfaceGeometry
IfcSurfaceOrFaceSurface IfcConnectionSurfaceGeometry::SurfaceOnRelatingElement() { return *entity->getArgument(0); }
bool IfcConnectionSurfaceGeometry::hasSurfaceOnRelatedElement() { return !entity->getArgument(1)->isNull(); }
IfcSurfaceOrFaceSurface IfcConnectionSurfaceGeometry::SurfaceOnRelatedElement() { return *entity->getArgument(1); }
bool IfcConnectionSurfaceGeometry::is(Type::Enum v) { return v == Type::IfcConnectionSurfaceGeometry || IfcConnectionGeometry::is(v); }
Type::Enum IfcConnectionSurfaceGeometry::type() { return Type::IfcConnectionSurfaceGeometry; }
Type::Enum IfcConnectionSurfaceGeometry::Class() { return Type::IfcConnectionSurfaceGeometry; }
IfcConnectionSurfaceGeometry::IfcConnectionSurfaceGeometry(IfcAbstractEntityPtr e) { if (!is(Type::IfcConnectionSurfaceGeometry)) throw; entity = e; } 
// IfcConstraint
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
bool IfcConstraint::is(Type::Enum v) { return v == Type::IfcConstraint; }
Type::Enum IfcConstraint::type() { return Type::IfcConstraint; }
Type::Enum IfcConstraint::Class() { return Type::IfcConstraint; }
IfcConstraint::IfcConstraint(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraint)) throw; entity = e; } 
// IfcConstraintAggregationRelationship
bool IfcConstraintAggregationRelationship::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcConstraintAggregationRelationship::Name() { return *entity->getArgument(0); }
bool IfcConstraintAggregationRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcConstraintAggregationRelationship::Description() { return *entity->getArgument(1); }
SHARED_PTR<IfcConstraint> IfcConstraintAggregationRelationship::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(2)); }
SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > IfcConstraintAggregationRelationship::RelatedConstraints() { RETURN_AS_LIST(IfcConstraint,3) }
IfcLogicalOperatorEnum::IfcLogicalOperatorEnum IfcConstraintAggregationRelationship::LogicalAggregator() { return IfcLogicalOperatorEnum::FromString(*entity->getArgument(4)); }
bool IfcConstraintAggregationRelationship::is(Type::Enum v) { return v == Type::IfcConstraintAggregationRelationship; }
Type::Enum IfcConstraintAggregationRelationship::type() { return Type::IfcConstraintAggregationRelationship; }
Type::Enum IfcConstraintAggregationRelationship::Class() { return Type::IfcConstraintAggregationRelationship; }
IfcConstraintAggregationRelationship::IfcConstraintAggregationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraintAggregationRelationship)) throw; entity = e; } 
// IfcConstraintClassificationRelationship
SHARED_PTR<IfcConstraint> IfcConstraintClassificationRelationship::ClassifiedConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcConstraintClassificationRelationship::RelatedClassifications() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcConstraintClassificationRelationship::is(Type::Enum v) { return v == Type::IfcConstraintClassificationRelationship; }
Type::Enum IfcConstraintClassificationRelationship::type() { return Type::IfcConstraintClassificationRelationship; }
Type::Enum IfcConstraintClassificationRelationship::Class() { return Type::IfcConstraintClassificationRelationship; }
IfcConstraintClassificationRelationship::IfcConstraintClassificationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraintClassificationRelationship)) throw; entity = e; } 
// IfcConstraintRelationship
bool IfcConstraintRelationship::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcConstraintRelationship::Name() { return *entity->getArgument(0); }
bool IfcConstraintRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcConstraintRelationship::Description() { return *entity->getArgument(1); }
SHARED_PTR<IfcConstraint> IfcConstraintRelationship::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(2)); }
SHARED_PTR< IfcTemplatedEntityList<IfcConstraint> > IfcConstraintRelationship::RelatedConstraints() { RETURN_AS_LIST(IfcConstraint,3) }
bool IfcConstraintRelationship::is(Type::Enum v) { return v == Type::IfcConstraintRelationship; }
Type::Enum IfcConstraintRelationship::type() { return Type::IfcConstraintRelationship; }
Type::Enum IfcConstraintRelationship::Class() { return Type::IfcConstraintRelationship; }
IfcConstraintRelationship::IfcConstraintRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstraintRelationship)) throw; entity = e; } 
// IfcConstructionEquipmentResource
bool IfcConstructionEquipmentResource::is(Type::Enum v) { return v == Type::IfcConstructionEquipmentResource || IfcConstructionResource::is(v); }
Type::Enum IfcConstructionEquipmentResource::type() { return Type::IfcConstructionEquipmentResource; }
Type::Enum IfcConstructionEquipmentResource::Class() { return Type::IfcConstructionEquipmentResource; }
IfcConstructionEquipmentResource::IfcConstructionEquipmentResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionEquipmentResource)) throw; entity = e; } 
// IfcConstructionMaterialResource
bool IfcConstructionMaterialResource::hasSuppliers() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcConstructionMaterialResource::Suppliers() { RETURN_AS_LIST(IfcAbstractSelect,9) }
bool IfcConstructionMaterialResource::hasUsageRatio() { return !entity->getArgument(10)->isNull(); }
IfcRatioMeasure IfcConstructionMaterialResource::UsageRatio() { return *entity->getArgument(10); }
bool IfcConstructionMaterialResource::is(Type::Enum v) { return v == Type::IfcConstructionMaterialResource || IfcConstructionResource::is(v); }
Type::Enum IfcConstructionMaterialResource::type() { return Type::IfcConstructionMaterialResource; }
Type::Enum IfcConstructionMaterialResource::Class() { return Type::IfcConstructionMaterialResource; }
IfcConstructionMaterialResource::IfcConstructionMaterialResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionMaterialResource)) throw; entity = e; } 
// IfcConstructionProductResource
bool IfcConstructionProductResource::is(Type::Enum v) { return v == Type::IfcConstructionProductResource || IfcConstructionResource::is(v); }
Type::Enum IfcConstructionProductResource::type() { return Type::IfcConstructionProductResource; }
Type::Enum IfcConstructionProductResource::Class() { return Type::IfcConstructionProductResource; }
IfcConstructionProductResource::IfcConstructionProductResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionProductResource)) throw; entity = e; } 
// IfcConstructionResource
bool IfcConstructionResource::hasResourceIdentifier() { return !entity->getArgument(5)->isNull(); }
IfcIdentifier IfcConstructionResource::ResourceIdentifier() { return *entity->getArgument(5); }
bool IfcConstructionResource::hasResourceGroup() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcConstructionResource::ResourceGroup() { return *entity->getArgument(6); }
bool IfcConstructionResource::hasResourceConsumption() { return !entity->getArgument(7)->isNull(); }
IfcResourceConsumptionEnum::IfcResourceConsumptionEnum IfcConstructionResource::ResourceConsumption() { return IfcResourceConsumptionEnum::FromString(*entity->getArgument(7)); }
bool IfcConstructionResource::hasBaseQuantity() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR<IfcMeasureWithUnit> IfcConstructionResource::BaseQuantity() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(8)); }
bool IfcConstructionResource::is(Type::Enum v) { return v == Type::IfcConstructionResource || IfcResource::is(v); }
Type::Enum IfcConstructionResource::type() { return Type::IfcConstructionResource; }
Type::Enum IfcConstructionResource::Class() { return Type::IfcConstructionResource; }
IfcConstructionResource::IfcConstructionResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcConstructionResource)) throw; entity = e; } 
// IfcContextDependentUnit
IfcLabel IfcContextDependentUnit::Name() { return *entity->getArgument(2); }
bool IfcContextDependentUnit::is(Type::Enum v) { return v == Type::IfcContextDependentUnit || IfcNamedUnit::is(v); }
Type::Enum IfcContextDependentUnit::type() { return Type::IfcContextDependentUnit; }
Type::Enum IfcContextDependentUnit::Class() { return Type::IfcContextDependentUnit; }
IfcContextDependentUnit::IfcContextDependentUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcContextDependentUnit)) throw; entity = e; } 
// IfcControl
IfcRelAssignsToControl::list IfcControl::Controls() { RETURN_INVERSE(IfcRelAssignsToControl) }
bool IfcControl::is(Type::Enum v) { return v == Type::IfcControl || IfcObject::is(v); }
Type::Enum IfcControl::type() { return Type::IfcControl; }
Type::Enum IfcControl::Class() { return Type::IfcControl; }
IfcControl::IfcControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcControl)) throw; entity = e; } 
// IfcControllerType
IfcControllerTypeEnum::IfcControllerTypeEnum IfcControllerType::PredefinedType() { return IfcControllerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcControllerType::is(Type::Enum v) { return v == Type::IfcControllerType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcControllerType::type() { return Type::IfcControllerType; }
Type::Enum IfcControllerType::Class() { return Type::IfcControllerType; }
IfcControllerType::IfcControllerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcControllerType)) throw; entity = e; } 
// IfcConversionBasedUnit
IfcLabel IfcConversionBasedUnit::Name() { return *entity->getArgument(2); }
SHARED_PTR<IfcMeasureWithUnit> IfcConversionBasedUnit::ConversionFactor() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(3)); }
bool IfcConversionBasedUnit::is(Type::Enum v) { return v == Type::IfcConversionBasedUnit || IfcNamedUnit::is(v); }
Type::Enum IfcConversionBasedUnit::type() { return Type::IfcConversionBasedUnit; }
Type::Enum IfcConversionBasedUnit::Class() { return Type::IfcConversionBasedUnit; }
IfcConversionBasedUnit::IfcConversionBasedUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcConversionBasedUnit)) throw; entity = e; } 
// IfcCooledBeamType
IfcCooledBeamTypeEnum::IfcCooledBeamTypeEnum IfcCooledBeamType::PredefinedType() { return IfcCooledBeamTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCooledBeamType::is(Type::Enum v) { return v == Type::IfcCooledBeamType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCooledBeamType::type() { return Type::IfcCooledBeamType; }
Type::Enum IfcCooledBeamType::Class() { return Type::IfcCooledBeamType; }
IfcCooledBeamType::IfcCooledBeamType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCooledBeamType)) throw; entity = e; } 
// IfcCoolingTowerType
IfcCoolingTowerTypeEnum::IfcCoolingTowerTypeEnum IfcCoolingTowerType::PredefinedType() { return IfcCoolingTowerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCoolingTowerType::is(Type::Enum v) { return v == Type::IfcCoolingTowerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcCoolingTowerType::type() { return Type::IfcCoolingTowerType; }
Type::Enum IfcCoolingTowerType::Class() { return Type::IfcCoolingTowerType; }
IfcCoolingTowerType::IfcCoolingTowerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoolingTowerType)) throw; entity = e; } 
// IfcCoordinatedUniversalTimeOffset
IfcHourInDay IfcCoordinatedUniversalTimeOffset::HourOffset() { return *entity->getArgument(0); }
bool IfcCoordinatedUniversalTimeOffset::hasMinuteOffset() { return !entity->getArgument(1)->isNull(); }
IfcMinuteInHour IfcCoordinatedUniversalTimeOffset::MinuteOffset() { return *entity->getArgument(1); }
IfcAheadOrBehind::IfcAheadOrBehind IfcCoordinatedUniversalTimeOffset::Sense() { return IfcAheadOrBehind::FromString(*entity->getArgument(2)); }
bool IfcCoordinatedUniversalTimeOffset::is(Type::Enum v) { return v == Type::IfcCoordinatedUniversalTimeOffset; }
Type::Enum IfcCoordinatedUniversalTimeOffset::type() { return Type::IfcCoordinatedUniversalTimeOffset; }
Type::Enum IfcCoordinatedUniversalTimeOffset::Class() { return Type::IfcCoordinatedUniversalTimeOffset; }
IfcCoordinatedUniversalTimeOffset::IfcCoordinatedUniversalTimeOffset(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoordinatedUniversalTimeOffset)) throw; entity = e; } 
// IfcCostItem
bool IfcCostItem::is(Type::Enum v) { return v == Type::IfcCostItem || IfcControl::is(v); }
Type::Enum IfcCostItem::type() { return Type::IfcCostItem; }
Type::Enum IfcCostItem::Class() { return Type::IfcCostItem; }
IfcCostItem::IfcCostItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcCostItem)) throw; entity = e; } 
// IfcCostSchedule
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
bool IfcCostSchedule::is(Type::Enum v) { return v == Type::IfcCostSchedule || IfcControl::is(v); }
Type::Enum IfcCostSchedule::type() { return Type::IfcCostSchedule; }
Type::Enum IfcCostSchedule::Class() { return Type::IfcCostSchedule; }
IfcCostSchedule::IfcCostSchedule(IfcAbstractEntityPtr e) { if (!is(Type::IfcCostSchedule)) throw; entity = e; } 
// IfcCostValue
IfcLabel IfcCostValue::CostType() { return *entity->getArgument(6); }
bool IfcCostValue::hasCondition() { return !entity->getArgument(7)->isNull(); }
IfcText IfcCostValue::Condition() { return *entity->getArgument(7); }
bool IfcCostValue::is(Type::Enum v) { return v == Type::IfcCostValue || IfcAppliedValue::is(v); }
Type::Enum IfcCostValue::type() { return Type::IfcCostValue; }
Type::Enum IfcCostValue::Class() { return Type::IfcCostValue; }
IfcCostValue::IfcCostValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcCostValue)) throw; entity = e; } 
// IfcCovering
bool IfcCovering::hasPredefinedType() { return !entity->getArgument(8)->isNull(); }
IfcCoveringTypeEnum::IfcCoveringTypeEnum IfcCovering::PredefinedType() { return IfcCoveringTypeEnum::FromString(*entity->getArgument(8)); }
IfcRelCoversSpaces::list IfcCovering::CoversSpaces() { RETURN_INVERSE(IfcRelCoversSpaces) }
IfcRelCoversBldgElements::list IfcCovering::Covers() { RETURN_INVERSE(IfcRelCoversBldgElements) }
bool IfcCovering::is(Type::Enum v) { return v == Type::IfcCovering || IfcBuildingElement::is(v); }
Type::Enum IfcCovering::type() { return Type::IfcCovering; }
Type::Enum IfcCovering::Class() { return Type::IfcCovering; }
IfcCovering::IfcCovering(IfcAbstractEntityPtr e) { if (!is(Type::IfcCovering)) throw; entity = e; } 
// IfcCoveringType
IfcCoveringTypeEnum::IfcCoveringTypeEnum IfcCoveringType::PredefinedType() { return IfcCoveringTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCoveringType::is(Type::Enum v) { return v == Type::IfcCoveringType || IfcBuildingElementType::is(v); }
Type::Enum IfcCoveringType::type() { return Type::IfcCoveringType; }
Type::Enum IfcCoveringType::Class() { return Type::IfcCoveringType; }
IfcCoveringType::IfcCoveringType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCoveringType)) throw; entity = e; } 
// IfcCraneRailAShapeProfileDef
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
bool IfcCraneRailAShapeProfileDef::is(Type::Enum v) { return v == Type::IfcCraneRailAShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCraneRailAShapeProfileDef::type() { return Type::IfcCraneRailAShapeProfileDef; }
Type::Enum IfcCraneRailAShapeProfileDef::Class() { return Type::IfcCraneRailAShapeProfileDef; }
IfcCraneRailAShapeProfileDef::IfcCraneRailAShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCraneRailAShapeProfileDef)) throw; entity = e; } 
// IfcCraneRailFShapeProfileDef
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
bool IfcCraneRailFShapeProfileDef::is(Type::Enum v) { return v == Type::IfcCraneRailFShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcCraneRailFShapeProfileDef::type() { return Type::IfcCraneRailFShapeProfileDef; }
Type::Enum IfcCraneRailFShapeProfileDef::Class() { return Type::IfcCraneRailFShapeProfileDef; }
IfcCraneRailFShapeProfileDef::IfcCraneRailFShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcCraneRailFShapeProfileDef)) throw; entity = e; } 
// IfcCrewResource
bool IfcCrewResource::is(Type::Enum v) { return v == Type::IfcCrewResource || IfcConstructionResource::is(v); }
Type::Enum IfcCrewResource::type() { return Type::IfcCrewResource; }
Type::Enum IfcCrewResource::Class() { return Type::IfcCrewResource; }
IfcCrewResource::IfcCrewResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcCrewResource)) throw; entity = e; } 
// IfcCsgPrimitive3D
SHARED_PTR<IfcAxis2Placement3D> IfcCsgPrimitive3D::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(0)); }
bool IfcCsgPrimitive3D::is(Type::Enum v) { return v == Type::IfcCsgPrimitive3D || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCsgPrimitive3D::type() { return Type::IfcCsgPrimitive3D; }
Type::Enum IfcCsgPrimitive3D::Class() { return Type::IfcCsgPrimitive3D; }
IfcCsgPrimitive3D::IfcCsgPrimitive3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcCsgPrimitive3D)) throw; entity = e; } 
// IfcCsgSolid
IfcCsgSelect IfcCsgSolid::TreeRootExpression() { return *entity->getArgument(0); }
bool IfcCsgSolid::is(Type::Enum v) { return v == Type::IfcCsgSolid || IfcSolidModel::is(v); }
Type::Enum IfcCsgSolid::type() { return Type::IfcCsgSolid; }
Type::Enum IfcCsgSolid::Class() { return Type::IfcCsgSolid; }
IfcCsgSolid::IfcCsgSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcCsgSolid)) throw; entity = e; } 
// IfcCurrencyRelationship
SHARED_PTR<IfcMonetaryUnit> IfcCurrencyRelationship::RelatingMonetaryUnit() { return reinterpret_pointer_cast<IfcBaseClass,IfcMonetaryUnit>(*entity->getArgument(0)); }
SHARED_PTR<IfcMonetaryUnit> IfcCurrencyRelationship::RelatedMonetaryUnit() { return reinterpret_pointer_cast<IfcBaseClass,IfcMonetaryUnit>(*entity->getArgument(1)); }
IfcPositiveRatioMeasure IfcCurrencyRelationship::ExchangeRate() { return *entity->getArgument(2); }
SHARED_PTR<IfcDateAndTime> IfcCurrencyRelationship::RateDateTime() { return reinterpret_pointer_cast<IfcBaseClass,IfcDateAndTime>(*entity->getArgument(3)); }
bool IfcCurrencyRelationship::hasRateSource() { return !entity->getArgument(4)->isNull(); }
SHARED_PTR<IfcLibraryInformation> IfcCurrencyRelationship::RateSource() { return reinterpret_pointer_cast<IfcBaseClass,IfcLibraryInformation>(*entity->getArgument(4)); }
bool IfcCurrencyRelationship::is(Type::Enum v) { return v == Type::IfcCurrencyRelationship; }
Type::Enum IfcCurrencyRelationship::type() { return Type::IfcCurrencyRelationship; }
Type::Enum IfcCurrencyRelationship::Class() { return Type::IfcCurrencyRelationship; }
IfcCurrencyRelationship::IfcCurrencyRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurrencyRelationship)) throw; entity = e; } 
// IfcCurtainWall
bool IfcCurtainWall::is(Type::Enum v) { return v == Type::IfcCurtainWall || IfcBuildingElement::is(v); }
Type::Enum IfcCurtainWall::type() { return Type::IfcCurtainWall; }
Type::Enum IfcCurtainWall::Class() { return Type::IfcCurtainWall; }
IfcCurtainWall::IfcCurtainWall(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurtainWall)) throw; entity = e; } 
// IfcCurtainWallType
IfcCurtainWallTypeEnum::IfcCurtainWallTypeEnum IfcCurtainWallType::PredefinedType() { return IfcCurtainWallTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcCurtainWallType::is(Type::Enum v) { return v == Type::IfcCurtainWallType || IfcBuildingElementType::is(v); }
Type::Enum IfcCurtainWallType::type() { return Type::IfcCurtainWallType; }
Type::Enum IfcCurtainWallType::Class() { return Type::IfcCurtainWallType; }
IfcCurtainWallType::IfcCurtainWallType(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurtainWallType)) throw; entity = e; } 
// IfcCurve
bool IfcCurve::is(Type::Enum v) { return v == Type::IfcCurve || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcCurve::type() { return Type::IfcCurve; }
Type::Enum IfcCurve::Class() { return Type::IfcCurve; }
IfcCurve::IfcCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurve)) throw; entity = e; } 
// IfcCurveBoundedPlane
SHARED_PTR<IfcPlane> IfcCurveBoundedPlane::BasisSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcPlane>(*entity->getArgument(0)); }
SHARED_PTR<IfcCurve> IfcCurveBoundedPlane::OuterBoundary() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(1)); }
SHARED_PTR< IfcTemplatedEntityList<IfcCurve> > IfcCurveBoundedPlane::InnerBoundaries() { RETURN_AS_LIST(IfcCurve,2) }
bool IfcCurveBoundedPlane::is(Type::Enum v) { return v == Type::IfcCurveBoundedPlane || IfcBoundedSurface::is(v); }
Type::Enum IfcCurveBoundedPlane::type() { return Type::IfcCurveBoundedPlane; }
Type::Enum IfcCurveBoundedPlane::Class() { return Type::IfcCurveBoundedPlane; }
IfcCurveBoundedPlane::IfcCurveBoundedPlane(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveBoundedPlane)) throw; entity = e; } 
// IfcCurveStyle
bool IfcCurveStyle::hasCurveFont() { return !entity->getArgument(1)->isNull(); }
IfcCurveFontOrScaledCurveFontSelect IfcCurveStyle::CurveFont() { return *entity->getArgument(1); }
bool IfcCurveStyle::hasCurveWidth() { return !entity->getArgument(2)->isNull(); }
IfcSizeSelect IfcCurveStyle::CurveWidth() { return *entity->getArgument(2); }
bool IfcCurveStyle::hasCurveColour() { return !entity->getArgument(3)->isNull(); }
IfcColour IfcCurveStyle::CurveColour() { return *entity->getArgument(3); }
bool IfcCurveStyle::is(Type::Enum v) { return v == Type::IfcCurveStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcCurveStyle::type() { return Type::IfcCurveStyle; }
Type::Enum IfcCurveStyle::Class() { return Type::IfcCurveStyle; }
IfcCurveStyle::IfcCurveStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyle)) throw; entity = e; } 
// IfcCurveStyleFont
bool IfcCurveStyleFont::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcCurveStyleFont::Name() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcCurveStyleFontPattern> > IfcCurveStyleFont::PatternList() { RETURN_AS_LIST(IfcCurveStyleFontPattern,1) }
bool IfcCurveStyleFont::is(Type::Enum v) { return v == Type::IfcCurveStyleFont; }
Type::Enum IfcCurveStyleFont::type() { return Type::IfcCurveStyleFont; }
Type::Enum IfcCurveStyleFont::Class() { return Type::IfcCurveStyleFont; }
IfcCurveStyleFont::IfcCurveStyleFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyleFont)) throw; entity = e; } 
// IfcCurveStyleFontAndScaling
bool IfcCurveStyleFontAndScaling::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcCurveStyleFontAndScaling::Name() { return *entity->getArgument(0); }
IfcCurveStyleFontSelect IfcCurveStyleFontAndScaling::CurveFont() { return *entity->getArgument(1); }
IfcPositiveRatioMeasure IfcCurveStyleFontAndScaling::CurveFontScaling() { return *entity->getArgument(2); }
bool IfcCurveStyleFontAndScaling::is(Type::Enum v) { return v == Type::IfcCurveStyleFontAndScaling; }
Type::Enum IfcCurveStyleFontAndScaling::type() { return Type::IfcCurveStyleFontAndScaling; }
Type::Enum IfcCurveStyleFontAndScaling::Class() { return Type::IfcCurveStyleFontAndScaling; }
IfcCurveStyleFontAndScaling::IfcCurveStyleFontAndScaling(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyleFontAndScaling)) throw; entity = e; } 
// IfcCurveStyleFontPattern
IfcLengthMeasure IfcCurveStyleFontPattern::VisibleSegmentLength() { return *entity->getArgument(0); }
IfcPositiveLengthMeasure IfcCurveStyleFontPattern::InvisibleSegmentLength() { return *entity->getArgument(1); }
bool IfcCurveStyleFontPattern::is(Type::Enum v) { return v == Type::IfcCurveStyleFontPattern; }
Type::Enum IfcCurveStyleFontPattern::type() { return Type::IfcCurveStyleFontPattern; }
Type::Enum IfcCurveStyleFontPattern::Class() { return Type::IfcCurveStyleFontPattern; }
IfcCurveStyleFontPattern::IfcCurveStyleFontPattern(IfcAbstractEntityPtr e) { if (!is(Type::IfcCurveStyleFontPattern)) throw; entity = e; } 
// IfcDamperType
IfcDamperTypeEnum::IfcDamperTypeEnum IfcDamperType::PredefinedType() { return IfcDamperTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDamperType::is(Type::Enum v) { return v == Type::IfcDamperType || IfcFlowControllerType::is(v); }
Type::Enum IfcDamperType::type() { return Type::IfcDamperType; }
Type::Enum IfcDamperType::Class() { return Type::IfcDamperType; }
IfcDamperType::IfcDamperType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDamperType)) throw; entity = e; } 
// IfcDateAndTime
SHARED_PTR<IfcCalendarDate> IfcDateAndTime::DateComponent() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(0)); }
SHARED_PTR<IfcLocalTime> IfcDateAndTime::TimeComponent() { return reinterpret_pointer_cast<IfcBaseClass,IfcLocalTime>(*entity->getArgument(1)); }
bool IfcDateAndTime::is(Type::Enum v) { return v == Type::IfcDateAndTime; }
Type::Enum IfcDateAndTime::type() { return Type::IfcDateAndTime; }
Type::Enum IfcDateAndTime::Class() { return Type::IfcDateAndTime; }
IfcDateAndTime::IfcDateAndTime(IfcAbstractEntityPtr e) { if (!is(Type::IfcDateAndTime)) throw; entity = e; } 
// IfcDefinedSymbol
IfcDefinedSymbolSelect IfcDefinedSymbol::Definition() { return *entity->getArgument(0); }
SHARED_PTR<IfcCartesianTransformationOperator2D> IfcDefinedSymbol::Target() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator2D>(*entity->getArgument(1)); }
bool IfcDefinedSymbol::is(Type::Enum v) { return v == Type::IfcDefinedSymbol || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcDefinedSymbol::type() { return Type::IfcDefinedSymbol; }
Type::Enum IfcDefinedSymbol::Class() { return Type::IfcDefinedSymbol; }
IfcDefinedSymbol::IfcDefinedSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcDefinedSymbol)) throw; entity = e; } 
// IfcDerivedProfileDef
SHARED_PTR<IfcProfileDef> IfcDerivedProfileDef::ParentProfile() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(2)); }
SHARED_PTR<IfcCartesianTransformationOperator2D> IfcDerivedProfileDef::Operator() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator2D>(*entity->getArgument(3)); }
bool IfcDerivedProfileDef::hasLabel() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcDerivedProfileDef::Label() { return *entity->getArgument(4); }
bool IfcDerivedProfileDef::is(Type::Enum v) { return v == Type::IfcDerivedProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcDerivedProfileDef::type() { return Type::IfcDerivedProfileDef; }
Type::Enum IfcDerivedProfileDef::Class() { return Type::IfcDerivedProfileDef; }
IfcDerivedProfileDef::IfcDerivedProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcDerivedProfileDef)) throw; entity = e; } 
// IfcDerivedUnit
SHARED_PTR< IfcTemplatedEntityList<IfcDerivedUnitElement> > IfcDerivedUnit::Elements() { RETURN_AS_LIST(IfcDerivedUnitElement,0) }
IfcDerivedUnitEnum::IfcDerivedUnitEnum IfcDerivedUnit::UnitType() { return IfcDerivedUnitEnum::FromString(*entity->getArgument(1)); }
bool IfcDerivedUnit::hasUserDefinedType() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcDerivedUnit::UserDefinedType() { return *entity->getArgument(2); }
bool IfcDerivedUnit::is(Type::Enum v) { return v == Type::IfcDerivedUnit; }
Type::Enum IfcDerivedUnit::type() { return Type::IfcDerivedUnit; }
Type::Enum IfcDerivedUnit::Class() { return Type::IfcDerivedUnit; }
IfcDerivedUnit::IfcDerivedUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcDerivedUnit)) throw; entity = e; } 
// IfcDerivedUnitElement
SHARED_PTR<IfcNamedUnit> IfcDerivedUnitElement::Unit() { return reinterpret_pointer_cast<IfcBaseClass,IfcNamedUnit>(*entity->getArgument(0)); }
int IfcDerivedUnitElement::Exponent() { return *entity->getArgument(1); }
bool IfcDerivedUnitElement::is(Type::Enum v) { return v == Type::IfcDerivedUnitElement; }
Type::Enum IfcDerivedUnitElement::type() { return Type::IfcDerivedUnitElement; }
Type::Enum IfcDerivedUnitElement::Class() { return Type::IfcDerivedUnitElement; }
IfcDerivedUnitElement::IfcDerivedUnitElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDerivedUnitElement)) throw; entity = e; } 
// IfcDiameterDimension
bool IfcDiameterDimension::is(Type::Enum v) { return v == Type::IfcDiameterDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcDiameterDimension::type() { return Type::IfcDiameterDimension; }
Type::Enum IfcDiameterDimension::Class() { return Type::IfcDiameterDimension; }
IfcDiameterDimension::IfcDiameterDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcDiameterDimension)) throw; entity = e; } 
// IfcDimensionCalloutRelationship
bool IfcDimensionCalloutRelationship::is(Type::Enum v) { return v == Type::IfcDimensionCalloutRelationship || IfcDraughtingCalloutRelationship::is(v); }
Type::Enum IfcDimensionCalloutRelationship::type() { return Type::IfcDimensionCalloutRelationship; }
Type::Enum IfcDimensionCalloutRelationship::Class() { return Type::IfcDimensionCalloutRelationship; }
IfcDimensionCalloutRelationship::IfcDimensionCalloutRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCalloutRelationship)) throw; entity = e; } 
// IfcDimensionCurve
IfcTerminatorSymbol::list IfcDimensionCurve::AnnotatedBySymbols() { RETURN_INVERSE(IfcTerminatorSymbol) }
bool IfcDimensionCurve::is(Type::Enum v) { return v == Type::IfcDimensionCurve || IfcAnnotationCurveOccurrence::is(v); }
Type::Enum IfcDimensionCurve::type() { return Type::IfcDimensionCurve; }
Type::Enum IfcDimensionCurve::Class() { return Type::IfcDimensionCurve; }
IfcDimensionCurve::IfcDimensionCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCurve)) throw; entity = e; } 
// IfcDimensionCurveDirectedCallout
bool IfcDimensionCurveDirectedCallout::is(Type::Enum v) { return v == Type::IfcDimensionCurveDirectedCallout || IfcDraughtingCallout::is(v); }
Type::Enum IfcDimensionCurveDirectedCallout::type() { return Type::IfcDimensionCurveDirectedCallout; }
Type::Enum IfcDimensionCurveDirectedCallout::Class() { return Type::IfcDimensionCurveDirectedCallout; }
IfcDimensionCurveDirectedCallout::IfcDimensionCurveDirectedCallout(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCurveDirectedCallout)) throw; entity = e; } 
// IfcDimensionCurveTerminator
IfcDimensionExtentUsage::IfcDimensionExtentUsage IfcDimensionCurveTerminator::Role() { return IfcDimensionExtentUsage::FromString(*entity->getArgument(4)); }
bool IfcDimensionCurveTerminator::is(Type::Enum v) { return v == Type::IfcDimensionCurveTerminator || IfcTerminatorSymbol::is(v); }
Type::Enum IfcDimensionCurveTerminator::type() { return Type::IfcDimensionCurveTerminator; }
Type::Enum IfcDimensionCurveTerminator::Class() { return Type::IfcDimensionCurveTerminator; }
IfcDimensionCurveTerminator::IfcDimensionCurveTerminator(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionCurveTerminator)) throw; entity = e; } 
// IfcDimensionPair
bool IfcDimensionPair::is(Type::Enum v) { return v == Type::IfcDimensionPair || IfcDraughtingCalloutRelationship::is(v); }
Type::Enum IfcDimensionPair::type() { return Type::IfcDimensionPair; }
Type::Enum IfcDimensionPair::Class() { return Type::IfcDimensionPair; }
IfcDimensionPair::IfcDimensionPair(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionPair)) throw; entity = e; } 
// IfcDimensionalExponents
int IfcDimensionalExponents::LengthExponent() { return *entity->getArgument(0); }
int IfcDimensionalExponents::MassExponent() { return *entity->getArgument(1); }
int IfcDimensionalExponents::TimeExponent() { return *entity->getArgument(2); }
int IfcDimensionalExponents::ElectricCurrentExponent() { return *entity->getArgument(3); }
int IfcDimensionalExponents::ThermodynamicTemperatureExponent() { return *entity->getArgument(4); }
int IfcDimensionalExponents::AmountOfSubstanceExponent() { return *entity->getArgument(5); }
int IfcDimensionalExponents::LuminousIntensityExponent() { return *entity->getArgument(6); }
bool IfcDimensionalExponents::is(Type::Enum v) { return v == Type::IfcDimensionalExponents; }
Type::Enum IfcDimensionalExponents::type() { return Type::IfcDimensionalExponents; }
Type::Enum IfcDimensionalExponents::Class() { return Type::IfcDimensionalExponents; }
IfcDimensionalExponents::IfcDimensionalExponents(IfcAbstractEntityPtr e) { if (!is(Type::IfcDimensionalExponents)) throw; entity = e; } 
// IfcDirection
std::vector<float> /*[2:3]*/ IfcDirection::DirectionRatios() { return *entity->getArgument(0); }
bool IfcDirection::is(Type::Enum v) { return v == Type::IfcDirection || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcDirection::type() { return Type::IfcDirection; }
Type::Enum IfcDirection::Class() { return Type::IfcDirection; }
IfcDirection::IfcDirection(IfcAbstractEntityPtr e) { if (!is(Type::IfcDirection)) throw; entity = e; } 
// IfcDiscreteAccessory
bool IfcDiscreteAccessory::is(Type::Enum v) { return v == Type::IfcDiscreteAccessory || IfcElementComponent::is(v); }
Type::Enum IfcDiscreteAccessory::type() { return Type::IfcDiscreteAccessory; }
Type::Enum IfcDiscreteAccessory::Class() { return Type::IfcDiscreteAccessory; }
IfcDiscreteAccessory::IfcDiscreteAccessory(IfcAbstractEntityPtr e) { if (!is(Type::IfcDiscreteAccessory)) throw; entity = e; } 
// IfcDiscreteAccessoryType
bool IfcDiscreteAccessoryType::is(Type::Enum v) { return v == Type::IfcDiscreteAccessoryType || IfcElementComponentType::is(v); }
Type::Enum IfcDiscreteAccessoryType::type() { return Type::IfcDiscreteAccessoryType; }
Type::Enum IfcDiscreteAccessoryType::Class() { return Type::IfcDiscreteAccessoryType; }
IfcDiscreteAccessoryType::IfcDiscreteAccessoryType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDiscreteAccessoryType)) throw; entity = e; } 
// IfcDistributionChamberElement
bool IfcDistributionChamberElement::is(Type::Enum v) { return v == Type::IfcDistributionChamberElement || IfcDistributionFlowElement::is(v); }
Type::Enum IfcDistributionChamberElement::type() { return Type::IfcDistributionChamberElement; }
Type::Enum IfcDistributionChamberElement::Class() { return Type::IfcDistributionChamberElement; }
IfcDistributionChamberElement::IfcDistributionChamberElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionChamberElement)) throw; entity = e; } 
// IfcDistributionChamberElementType
IfcDistributionChamberElementTypeEnum::IfcDistributionChamberElementTypeEnum IfcDistributionChamberElementType::PredefinedType() { return IfcDistributionChamberElementTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDistributionChamberElementType::is(Type::Enum v) { return v == Type::IfcDistributionChamberElementType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcDistributionChamberElementType::type() { return Type::IfcDistributionChamberElementType; }
Type::Enum IfcDistributionChamberElementType::Class() { return Type::IfcDistributionChamberElementType; }
IfcDistributionChamberElementType::IfcDistributionChamberElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionChamberElementType)) throw; entity = e; } 
// IfcDistributionControlElement
bool IfcDistributionControlElement::hasControlElementId() { return !entity->getArgument(8)->isNull(); }
IfcIdentifier IfcDistributionControlElement::ControlElementId() { return *entity->getArgument(8); }
IfcRelFlowControlElements::list IfcDistributionControlElement::AssignedToFlowElement() { RETURN_INVERSE(IfcRelFlowControlElements) }
bool IfcDistributionControlElement::is(Type::Enum v) { return v == Type::IfcDistributionControlElement || IfcDistributionElement::is(v); }
Type::Enum IfcDistributionControlElement::type() { return Type::IfcDistributionControlElement; }
Type::Enum IfcDistributionControlElement::Class() { return Type::IfcDistributionControlElement; }
IfcDistributionControlElement::IfcDistributionControlElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionControlElement)) throw; entity = e; } 
// IfcDistributionControlElementType
bool IfcDistributionControlElementType::is(Type::Enum v) { return v == Type::IfcDistributionControlElementType || IfcDistributionElementType::is(v); }
Type::Enum IfcDistributionControlElementType::type() { return Type::IfcDistributionControlElementType; }
Type::Enum IfcDistributionControlElementType::Class() { return Type::IfcDistributionControlElementType; }
IfcDistributionControlElementType::IfcDistributionControlElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionControlElementType)) throw; entity = e; } 
// IfcDistributionElement
bool IfcDistributionElement::is(Type::Enum v) { return v == Type::IfcDistributionElement || IfcElement::is(v); }
Type::Enum IfcDistributionElement::type() { return Type::IfcDistributionElement; }
Type::Enum IfcDistributionElement::Class() { return Type::IfcDistributionElement; }
IfcDistributionElement::IfcDistributionElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionElement)) throw; entity = e; } 
// IfcDistributionElementType
bool IfcDistributionElementType::is(Type::Enum v) { return v == Type::IfcDistributionElementType || IfcElementType::is(v); }
Type::Enum IfcDistributionElementType::type() { return Type::IfcDistributionElementType; }
Type::Enum IfcDistributionElementType::Class() { return Type::IfcDistributionElementType; }
IfcDistributionElementType::IfcDistributionElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionElementType)) throw; entity = e; } 
// IfcDistributionFlowElement
IfcRelFlowControlElements::list IfcDistributionFlowElement::HasControlElements() { RETURN_INVERSE(IfcRelFlowControlElements) }
bool IfcDistributionFlowElement::is(Type::Enum v) { return v == Type::IfcDistributionFlowElement || IfcDistributionElement::is(v); }
Type::Enum IfcDistributionFlowElement::type() { return Type::IfcDistributionFlowElement; }
Type::Enum IfcDistributionFlowElement::Class() { return Type::IfcDistributionFlowElement; }
IfcDistributionFlowElement::IfcDistributionFlowElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionFlowElement)) throw; entity = e; } 
// IfcDistributionFlowElementType
bool IfcDistributionFlowElementType::is(Type::Enum v) { return v == Type::IfcDistributionFlowElementType || IfcDistributionElementType::is(v); }
Type::Enum IfcDistributionFlowElementType::type() { return Type::IfcDistributionFlowElementType; }
Type::Enum IfcDistributionFlowElementType::Class() { return Type::IfcDistributionFlowElementType; }
IfcDistributionFlowElementType::IfcDistributionFlowElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionFlowElementType)) throw; entity = e; } 
// IfcDistributionPort
bool IfcDistributionPort::hasFlowDirection() { return !entity->getArgument(7)->isNull(); }
IfcFlowDirectionEnum::IfcFlowDirectionEnum IfcDistributionPort::FlowDirection() { return IfcFlowDirectionEnum::FromString(*entity->getArgument(7)); }
bool IfcDistributionPort::is(Type::Enum v) { return v == Type::IfcDistributionPort || IfcPort::is(v); }
Type::Enum IfcDistributionPort::type() { return Type::IfcDistributionPort; }
Type::Enum IfcDistributionPort::Class() { return Type::IfcDistributionPort; }
IfcDistributionPort::IfcDistributionPort(IfcAbstractEntityPtr e) { if (!is(Type::IfcDistributionPort)) throw; entity = e; } 
// IfcDocumentElectronicFormat
bool IfcDocumentElectronicFormat::hasFileExtension() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcDocumentElectronicFormat::FileExtension() { return *entity->getArgument(0); }
bool IfcDocumentElectronicFormat::hasMimeContentType() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcDocumentElectronicFormat::MimeContentType() { return *entity->getArgument(1); }
bool IfcDocumentElectronicFormat::hasMimeSubtype() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcDocumentElectronicFormat::MimeSubtype() { return *entity->getArgument(2); }
bool IfcDocumentElectronicFormat::is(Type::Enum v) { return v == Type::IfcDocumentElectronicFormat; }
Type::Enum IfcDocumentElectronicFormat::type() { return Type::IfcDocumentElectronicFormat; }
Type::Enum IfcDocumentElectronicFormat::Class() { return Type::IfcDocumentElectronicFormat; }
IfcDocumentElectronicFormat::IfcDocumentElectronicFormat(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentElectronicFormat)) throw; entity = e; } 
// IfcDocumentInformation
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
SHARED_PTR<IfcDateAndTime> IfcDocumentInformation::CreationTime() { return reinterpret_pointer_cast<IfcBaseClass,IfcDateAndTime>(*entity->getArgument(10)); }
bool IfcDocumentInformation::hasLastRevisionTime() { return !entity->getArgument(11)->isNull(); }
SHARED_PTR<IfcDateAndTime> IfcDocumentInformation::LastRevisionTime() { return reinterpret_pointer_cast<IfcBaseClass,IfcDateAndTime>(*entity->getArgument(11)); }
bool IfcDocumentInformation::hasElectronicFormat() { return !entity->getArgument(12)->isNull(); }
SHARED_PTR<IfcDocumentElectronicFormat> IfcDocumentInformation::ElectronicFormat() { return reinterpret_pointer_cast<IfcBaseClass,IfcDocumentElectronicFormat>(*entity->getArgument(12)); }
bool IfcDocumentInformation::hasValidFrom() { return !entity->getArgument(13)->isNull(); }
SHARED_PTR<IfcCalendarDate> IfcDocumentInformation::ValidFrom() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(13)); }
bool IfcDocumentInformation::hasValidUntil() { return !entity->getArgument(14)->isNull(); }
SHARED_PTR<IfcCalendarDate> IfcDocumentInformation::ValidUntil() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(14)); }
bool IfcDocumentInformation::hasConfidentiality() { return !entity->getArgument(15)->isNull(); }
IfcDocumentConfidentialityEnum::IfcDocumentConfidentialityEnum IfcDocumentInformation::Confidentiality() { return IfcDocumentConfidentialityEnum::FromString(*entity->getArgument(15)); }
bool IfcDocumentInformation::hasStatus() { return !entity->getArgument(16)->isNull(); }
IfcDocumentStatusEnum::IfcDocumentStatusEnum IfcDocumentInformation::Status() { return IfcDocumentStatusEnum::FromString(*entity->getArgument(16)); }
IfcDocumentInformationRelationship::list IfcDocumentInformation::IsPointedTo() { RETURN_INVERSE(IfcDocumentInformationRelationship) }
IfcDocumentInformationRelationship::list IfcDocumentInformation::IsPointer() { RETURN_INVERSE(IfcDocumentInformationRelationship) }
bool IfcDocumentInformation::is(Type::Enum v) { return v == Type::IfcDocumentInformation; }
Type::Enum IfcDocumentInformation::type() { return Type::IfcDocumentInformation; }
Type::Enum IfcDocumentInformation::Class() { return Type::IfcDocumentInformation; }
IfcDocumentInformation::IfcDocumentInformation(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentInformation)) throw; entity = e; } 
// IfcDocumentInformationRelationship
SHARED_PTR<IfcDocumentInformation> IfcDocumentInformationRelationship::RelatingDocument() { return reinterpret_pointer_cast<IfcBaseClass,IfcDocumentInformation>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcDocumentInformation> > IfcDocumentInformationRelationship::RelatedDocuments() { RETURN_AS_LIST(IfcDocumentInformation,1) }
bool IfcDocumentInformationRelationship::hasRelationshipType() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcDocumentInformationRelationship::RelationshipType() { return *entity->getArgument(2); }
bool IfcDocumentInformationRelationship::is(Type::Enum v) { return v == Type::IfcDocumentInformationRelationship; }
Type::Enum IfcDocumentInformationRelationship::type() { return Type::IfcDocumentInformationRelationship; }
Type::Enum IfcDocumentInformationRelationship::Class() { return Type::IfcDocumentInformationRelationship; }
IfcDocumentInformationRelationship::IfcDocumentInformationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentInformationRelationship)) throw; entity = e; } 
// IfcDocumentReference
IfcDocumentInformation::list IfcDocumentReference::ReferenceToDocument() { RETURN_INVERSE(IfcDocumentInformation) }
bool IfcDocumentReference::is(Type::Enum v) { return v == Type::IfcDocumentReference || IfcExternalReference::is(v); }
Type::Enum IfcDocumentReference::type() { return Type::IfcDocumentReference; }
Type::Enum IfcDocumentReference::Class() { return Type::IfcDocumentReference; }
IfcDocumentReference::IfcDocumentReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcDocumentReference)) throw; entity = e; } 
// IfcDoor
bool IfcDoor::hasOverallHeight() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcDoor::OverallHeight() { return *entity->getArgument(8); }
bool IfcDoor::hasOverallWidth() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcDoor::OverallWidth() { return *entity->getArgument(9); }
bool IfcDoor::is(Type::Enum v) { return v == Type::IfcDoor || IfcBuildingElement::is(v); }
Type::Enum IfcDoor::type() { return Type::IfcDoor; }
Type::Enum IfcDoor::Class() { return Type::IfcDoor; }
IfcDoor::IfcDoor(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoor)) throw; entity = e; } 
// IfcDoorLiningProperties
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
SHARED_PTR<IfcShapeAspect> IfcDoorLiningProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(14)); }
bool IfcDoorLiningProperties::is(Type::Enum v) { return v == Type::IfcDoorLiningProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcDoorLiningProperties::type() { return Type::IfcDoorLiningProperties; }
Type::Enum IfcDoorLiningProperties::Class() { return Type::IfcDoorLiningProperties; }
IfcDoorLiningProperties::IfcDoorLiningProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoorLiningProperties)) throw; entity = e; } 
// IfcDoorPanelProperties
bool IfcDoorPanelProperties::hasPanelDepth() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcDoorPanelProperties::PanelDepth() { return *entity->getArgument(4); }
IfcDoorPanelOperationEnum::IfcDoorPanelOperationEnum IfcDoorPanelProperties::PanelOperation() { return IfcDoorPanelOperationEnum::FromString(*entity->getArgument(5)); }
bool IfcDoorPanelProperties::hasPanelWidth() { return !entity->getArgument(6)->isNull(); }
IfcNormalisedRatioMeasure IfcDoorPanelProperties::PanelWidth() { return *entity->getArgument(6); }
IfcDoorPanelPositionEnum::IfcDoorPanelPositionEnum IfcDoorPanelProperties::PanelPosition() { return IfcDoorPanelPositionEnum::FromString(*entity->getArgument(7)); }
bool IfcDoorPanelProperties::hasShapeAspectStyle() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR<IfcShapeAspect> IfcDoorPanelProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(8)); }
bool IfcDoorPanelProperties::is(Type::Enum v) { return v == Type::IfcDoorPanelProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcDoorPanelProperties::type() { return Type::IfcDoorPanelProperties; }
Type::Enum IfcDoorPanelProperties::Class() { return Type::IfcDoorPanelProperties; }
IfcDoorPanelProperties::IfcDoorPanelProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoorPanelProperties)) throw; entity = e; } 
// IfcDoorStyle
IfcDoorStyleOperationEnum::IfcDoorStyleOperationEnum IfcDoorStyle::OperationType() { return IfcDoorStyleOperationEnum::FromString(*entity->getArgument(8)); }
IfcDoorStyleConstructionEnum::IfcDoorStyleConstructionEnum IfcDoorStyle::ConstructionType() { return IfcDoorStyleConstructionEnum::FromString(*entity->getArgument(9)); }
bool IfcDoorStyle::ParameterTakesPrecedence() { return *entity->getArgument(10); }
bool IfcDoorStyle::Sizeable() { return *entity->getArgument(11); }
bool IfcDoorStyle::is(Type::Enum v) { return v == Type::IfcDoorStyle || IfcTypeProduct::is(v); }
Type::Enum IfcDoorStyle::type() { return Type::IfcDoorStyle; }
Type::Enum IfcDoorStyle::Class() { return Type::IfcDoorStyle; }
IfcDoorStyle::IfcDoorStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcDoorStyle)) throw; entity = e; } 
// IfcDraughtingCallout
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcDraughtingCallout::Contents() { RETURN_AS_LIST(IfcAbstractSelect,0) }
IfcDraughtingCalloutRelationship::list IfcDraughtingCallout::IsRelatedFromCallout() { RETURN_INVERSE(IfcDraughtingCalloutRelationship) }
IfcDraughtingCalloutRelationship::list IfcDraughtingCallout::IsRelatedToCallout() { RETURN_INVERSE(IfcDraughtingCalloutRelationship) }
bool IfcDraughtingCallout::is(Type::Enum v) { return v == Type::IfcDraughtingCallout || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcDraughtingCallout::type() { return Type::IfcDraughtingCallout; }
Type::Enum IfcDraughtingCallout::Class() { return Type::IfcDraughtingCallout; }
IfcDraughtingCallout::IfcDraughtingCallout(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingCallout)) throw; entity = e; } 
// IfcDraughtingCalloutRelationship
bool IfcDraughtingCalloutRelationship::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcDraughtingCalloutRelationship::Name() { return *entity->getArgument(0); }
bool IfcDraughtingCalloutRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcDraughtingCalloutRelationship::Description() { return *entity->getArgument(1); }
SHARED_PTR<IfcDraughtingCallout> IfcDraughtingCalloutRelationship::RelatingDraughtingCallout() { return reinterpret_pointer_cast<IfcBaseClass,IfcDraughtingCallout>(*entity->getArgument(2)); }
SHARED_PTR<IfcDraughtingCallout> IfcDraughtingCalloutRelationship::RelatedDraughtingCallout() { return reinterpret_pointer_cast<IfcBaseClass,IfcDraughtingCallout>(*entity->getArgument(3)); }
bool IfcDraughtingCalloutRelationship::is(Type::Enum v) { return v == Type::IfcDraughtingCalloutRelationship; }
Type::Enum IfcDraughtingCalloutRelationship::type() { return Type::IfcDraughtingCalloutRelationship; }
Type::Enum IfcDraughtingCalloutRelationship::Class() { return Type::IfcDraughtingCalloutRelationship; }
IfcDraughtingCalloutRelationship::IfcDraughtingCalloutRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingCalloutRelationship)) throw; entity = e; } 
// IfcDraughtingPreDefinedColour
bool IfcDraughtingPreDefinedColour::is(Type::Enum v) { return v == Type::IfcDraughtingPreDefinedColour || IfcPreDefinedColour::is(v); }
Type::Enum IfcDraughtingPreDefinedColour::type() { return Type::IfcDraughtingPreDefinedColour; }
Type::Enum IfcDraughtingPreDefinedColour::Class() { return Type::IfcDraughtingPreDefinedColour; }
IfcDraughtingPreDefinedColour::IfcDraughtingPreDefinedColour(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingPreDefinedColour)) throw; entity = e; } 
// IfcDraughtingPreDefinedCurveFont
bool IfcDraughtingPreDefinedCurveFont::is(Type::Enum v) { return v == Type::IfcDraughtingPreDefinedCurveFont || IfcPreDefinedCurveFont::is(v); }
Type::Enum IfcDraughtingPreDefinedCurveFont::type() { return Type::IfcDraughtingPreDefinedCurveFont; }
Type::Enum IfcDraughtingPreDefinedCurveFont::Class() { return Type::IfcDraughtingPreDefinedCurveFont; }
IfcDraughtingPreDefinedCurveFont::IfcDraughtingPreDefinedCurveFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingPreDefinedCurveFont)) throw; entity = e; } 
// IfcDraughtingPreDefinedTextFont
bool IfcDraughtingPreDefinedTextFont::is(Type::Enum v) { return v == Type::IfcDraughtingPreDefinedTextFont || IfcPreDefinedTextFont::is(v); }
Type::Enum IfcDraughtingPreDefinedTextFont::type() { return Type::IfcDraughtingPreDefinedTextFont; }
Type::Enum IfcDraughtingPreDefinedTextFont::Class() { return Type::IfcDraughtingPreDefinedTextFont; }
IfcDraughtingPreDefinedTextFont::IfcDraughtingPreDefinedTextFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcDraughtingPreDefinedTextFont)) throw; entity = e; } 
// IfcDuctFittingType
IfcDuctFittingTypeEnum::IfcDuctFittingTypeEnum IfcDuctFittingType::PredefinedType() { return IfcDuctFittingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDuctFittingType::is(Type::Enum v) { return v == Type::IfcDuctFittingType || IfcFlowFittingType::is(v); }
Type::Enum IfcDuctFittingType::type() { return Type::IfcDuctFittingType; }
Type::Enum IfcDuctFittingType::Class() { return Type::IfcDuctFittingType; }
IfcDuctFittingType::IfcDuctFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDuctFittingType)) throw; entity = e; } 
// IfcDuctSegmentType
IfcDuctSegmentTypeEnum::IfcDuctSegmentTypeEnum IfcDuctSegmentType::PredefinedType() { return IfcDuctSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDuctSegmentType::is(Type::Enum v) { return v == Type::IfcDuctSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcDuctSegmentType::type() { return Type::IfcDuctSegmentType; }
Type::Enum IfcDuctSegmentType::Class() { return Type::IfcDuctSegmentType; }
IfcDuctSegmentType::IfcDuctSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDuctSegmentType)) throw; entity = e; } 
// IfcDuctSilencerType
IfcDuctSilencerTypeEnum::IfcDuctSilencerTypeEnum IfcDuctSilencerType::PredefinedType() { return IfcDuctSilencerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcDuctSilencerType::is(Type::Enum v) { return v == Type::IfcDuctSilencerType || IfcFlowTreatmentDeviceType::is(v); }
Type::Enum IfcDuctSilencerType::type() { return Type::IfcDuctSilencerType; }
Type::Enum IfcDuctSilencerType::Class() { return Type::IfcDuctSilencerType; }
IfcDuctSilencerType::IfcDuctSilencerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcDuctSilencerType)) throw; entity = e; } 
// IfcEdge
SHARED_PTR<IfcVertex> IfcEdge::EdgeStart() { return reinterpret_pointer_cast<IfcBaseClass,IfcVertex>(*entity->getArgument(0)); }
SHARED_PTR<IfcVertex> IfcEdge::EdgeEnd() { return reinterpret_pointer_cast<IfcBaseClass,IfcVertex>(*entity->getArgument(1)); }
bool IfcEdge::is(Type::Enum v) { return v == Type::IfcEdge || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcEdge::type() { return Type::IfcEdge; }
Type::Enum IfcEdge::Class() { return Type::IfcEdge; }
IfcEdge::IfcEdge(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdge)) throw; entity = e; } 
// IfcEdgeCurve
SHARED_PTR<IfcCurve> IfcEdgeCurve::EdgeGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
bool IfcEdgeCurve::SameSense() { return *entity->getArgument(3); }
bool IfcEdgeCurve::is(Type::Enum v) { return v == Type::IfcEdgeCurve || IfcEdge::is(v); }
Type::Enum IfcEdgeCurve::type() { return Type::IfcEdgeCurve; }
Type::Enum IfcEdgeCurve::Class() { return Type::IfcEdgeCurve; }
IfcEdgeCurve::IfcEdgeCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdgeCurve)) throw; entity = e; } 
// IfcEdgeFeature
bool IfcEdgeFeature::hasFeatureLength() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcEdgeFeature::FeatureLength() { return *entity->getArgument(8); }
bool IfcEdgeFeature::is(Type::Enum v) { return v == Type::IfcEdgeFeature || IfcFeatureElementSubtraction::is(v); }
Type::Enum IfcEdgeFeature::type() { return Type::IfcEdgeFeature; }
Type::Enum IfcEdgeFeature::Class() { return Type::IfcEdgeFeature; }
IfcEdgeFeature::IfcEdgeFeature(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdgeFeature)) throw; entity = e; } 
// IfcEdgeLoop
SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > IfcEdgeLoop::EdgeList() { RETURN_AS_LIST(IfcOrientedEdge,0) }
bool IfcEdgeLoop::is(Type::Enum v) { return v == Type::IfcEdgeLoop || IfcLoop::is(v); }
Type::Enum IfcEdgeLoop::type() { return Type::IfcEdgeLoop; }
Type::Enum IfcEdgeLoop::Class() { return Type::IfcEdgeLoop; }
IfcEdgeLoop::IfcEdgeLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcEdgeLoop)) throw; entity = e; } 
// IfcElectricApplianceType
IfcElectricApplianceTypeEnum::IfcElectricApplianceTypeEnum IfcElectricApplianceType::PredefinedType() { return IfcElectricApplianceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricApplianceType::is(Type::Enum v) { return v == Type::IfcElectricApplianceType || IfcFlowTerminalType::is(v); }
Type::Enum IfcElectricApplianceType::type() { return Type::IfcElectricApplianceType; }
Type::Enum IfcElectricApplianceType::Class() { return Type::IfcElectricApplianceType; }
IfcElectricApplianceType::IfcElectricApplianceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricApplianceType)) throw; entity = e; } 
// IfcElectricDistributionPoint
IfcElectricDistributionPointFunctionEnum::IfcElectricDistributionPointFunctionEnum IfcElectricDistributionPoint::DistributionPointFunction() { return IfcElectricDistributionPointFunctionEnum::FromString(*entity->getArgument(8)); }
bool IfcElectricDistributionPoint::hasUserDefinedFunction() { return !entity->getArgument(9)->isNull(); }
IfcLabel IfcElectricDistributionPoint::UserDefinedFunction() { return *entity->getArgument(9); }
bool IfcElectricDistributionPoint::is(Type::Enum v) { return v == Type::IfcElectricDistributionPoint || IfcFlowController::is(v); }
Type::Enum IfcElectricDistributionPoint::type() { return Type::IfcElectricDistributionPoint; }
Type::Enum IfcElectricDistributionPoint::Class() { return Type::IfcElectricDistributionPoint; }
IfcElectricDistributionPoint::IfcElectricDistributionPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricDistributionPoint)) throw; entity = e; } 
// IfcElectricFlowStorageDeviceType
IfcElectricFlowStorageDeviceTypeEnum::IfcElectricFlowStorageDeviceTypeEnum IfcElectricFlowStorageDeviceType::PredefinedType() { return IfcElectricFlowStorageDeviceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricFlowStorageDeviceType::is(Type::Enum v) { return v == Type::IfcElectricFlowStorageDeviceType || IfcFlowStorageDeviceType::is(v); }
Type::Enum IfcElectricFlowStorageDeviceType::type() { return Type::IfcElectricFlowStorageDeviceType; }
Type::Enum IfcElectricFlowStorageDeviceType::Class() { return Type::IfcElectricFlowStorageDeviceType; }
IfcElectricFlowStorageDeviceType::IfcElectricFlowStorageDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricFlowStorageDeviceType)) throw; entity = e; } 
// IfcElectricGeneratorType
IfcElectricGeneratorTypeEnum::IfcElectricGeneratorTypeEnum IfcElectricGeneratorType::PredefinedType() { return IfcElectricGeneratorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricGeneratorType::is(Type::Enum v) { return v == Type::IfcElectricGeneratorType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcElectricGeneratorType::type() { return Type::IfcElectricGeneratorType; }
Type::Enum IfcElectricGeneratorType::Class() { return Type::IfcElectricGeneratorType; }
IfcElectricGeneratorType::IfcElectricGeneratorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricGeneratorType)) throw; entity = e; } 
// IfcElectricHeaterType
IfcElectricHeaterTypeEnum::IfcElectricHeaterTypeEnum IfcElectricHeaterType::PredefinedType() { return IfcElectricHeaterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricHeaterType::is(Type::Enum v) { return v == Type::IfcElectricHeaterType || IfcFlowTerminalType::is(v); }
Type::Enum IfcElectricHeaterType::type() { return Type::IfcElectricHeaterType; }
Type::Enum IfcElectricHeaterType::Class() { return Type::IfcElectricHeaterType; }
IfcElectricHeaterType::IfcElectricHeaterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricHeaterType)) throw; entity = e; } 
// IfcElectricMotorType
IfcElectricMotorTypeEnum::IfcElectricMotorTypeEnum IfcElectricMotorType::PredefinedType() { return IfcElectricMotorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricMotorType::is(Type::Enum v) { return v == Type::IfcElectricMotorType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcElectricMotorType::type() { return Type::IfcElectricMotorType; }
Type::Enum IfcElectricMotorType::Class() { return Type::IfcElectricMotorType; }
IfcElectricMotorType::IfcElectricMotorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricMotorType)) throw; entity = e; } 
// IfcElectricTimeControlType
IfcElectricTimeControlTypeEnum::IfcElectricTimeControlTypeEnum IfcElectricTimeControlType::PredefinedType() { return IfcElectricTimeControlTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElectricTimeControlType::is(Type::Enum v) { return v == Type::IfcElectricTimeControlType || IfcFlowControllerType::is(v); }
Type::Enum IfcElectricTimeControlType::type() { return Type::IfcElectricTimeControlType; }
Type::Enum IfcElectricTimeControlType::Class() { return Type::IfcElectricTimeControlType; }
IfcElectricTimeControlType::IfcElectricTimeControlType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricTimeControlType)) throw; entity = e; } 
// IfcElectricalBaseProperties
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
bool IfcElectricalBaseProperties::is(Type::Enum v) { return v == Type::IfcElectricalBaseProperties || IfcEnergyProperties::is(v); }
Type::Enum IfcElectricalBaseProperties::type() { return Type::IfcElectricalBaseProperties; }
Type::Enum IfcElectricalBaseProperties::Class() { return Type::IfcElectricalBaseProperties; }
IfcElectricalBaseProperties::IfcElectricalBaseProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricalBaseProperties)) throw; entity = e; } 
// IfcElectricalCircuit
bool IfcElectricalCircuit::is(Type::Enum v) { return v == Type::IfcElectricalCircuit || IfcSystem::is(v); }
Type::Enum IfcElectricalCircuit::type() { return Type::IfcElectricalCircuit; }
Type::Enum IfcElectricalCircuit::Class() { return Type::IfcElectricalCircuit; }
IfcElectricalCircuit::IfcElectricalCircuit(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricalCircuit)) throw; entity = e; } 
// IfcElectricalElement
bool IfcElectricalElement::is(Type::Enum v) { return v == Type::IfcElectricalElement || IfcElement::is(v); }
Type::Enum IfcElectricalElement::type() { return Type::IfcElectricalElement; }
Type::Enum IfcElectricalElement::Class() { return Type::IfcElectricalElement; }
IfcElectricalElement::IfcElectricalElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcElectricalElement)) throw; entity = e; } 
// IfcElement
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
bool IfcElement::is(Type::Enum v) { return v == Type::IfcElement || IfcProduct::is(v); }
Type::Enum IfcElement::type() { return Type::IfcElement; }
Type::Enum IfcElement::Class() { return Type::IfcElement; }
IfcElement::IfcElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcElement)) throw; entity = e; } 
// IfcElementAssembly
bool IfcElementAssembly::hasAssemblyPlace() { return !entity->getArgument(8)->isNull(); }
IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum IfcElementAssembly::AssemblyPlace() { return IfcAssemblyPlaceEnum::FromString(*entity->getArgument(8)); }
IfcElementAssemblyTypeEnum::IfcElementAssemblyTypeEnum IfcElementAssembly::PredefinedType() { return IfcElementAssemblyTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcElementAssembly::is(Type::Enum v) { return v == Type::IfcElementAssembly || IfcElement::is(v); }
Type::Enum IfcElementAssembly::type() { return Type::IfcElementAssembly; }
Type::Enum IfcElementAssembly::Class() { return Type::IfcElementAssembly; }
IfcElementAssembly::IfcElementAssembly(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementAssembly)) throw; entity = e; } 
// IfcElementComponent
bool IfcElementComponent::is(Type::Enum v) { return v == Type::IfcElementComponent || IfcElement::is(v); }
Type::Enum IfcElementComponent::type() { return Type::IfcElementComponent; }
Type::Enum IfcElementComponent::Class() { return Type::IfcElementComponent; }
IfcElementComponent::IfcElementComponent(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementComponent)) throw; entity = e; } 
// IfcElementComponentType
bool IfcElementComponentType::is(Type::Enum v) { return v == Type::IfcElementComponentType || IfcElementType::is(v); }
Type::Enum IfcElementComponentType::type() { return Type::IfcElementComponentType; }
Type::Enum IfcElementComponentType::Class() { return Type::IfcElementComponentType; }
IfcElementComponentType::IfcElementComponentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementComponentType)) throw; entity = e; } 
// IfcElementQuantity
bool IfcElementQuantity::hasMethodOfMeasurement() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcElementQuantity::MethodOfMeasurement() { return *entity->getArgument(4); }
SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > IfcElementQuantity::Quantities() { RETURN_AS_LIST(IfcPhysicalQuantity,5) }
bool IfcElementQuantity::is(Type::Enum v) { return v == Type::IfcElementQuantity || IfcPropertySetDefinition::is(v); }
Type::Enum IfcElementQuantity::type() { return Type::IfcElementQuantity; }
Type::Enum IfcElementQuantity::Class() { return Type::IfcElementQuantity; }
IfcElementQuantity::IfcElementQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementQuantity)) throw; entity = e; } 
// IfcElementType
bool IfcElementType::hasElementType() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcElementType::ElementType() { return *entity->getArgument(8); }
bool IfcElementType::is(Type::Enum v) { return v == Type::IfcElementType || IfcTypeProduct::is(v); }
Type::Enum IfcElementType::type() { return Type::IfcElementType; }
Type::Enum IfcElementType::Class() { return Type::IfcElementType; }
IfcElementType::IfcElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementType)) throw; entity = e; } 
// IfcElementarySurface
SHARED_PTR<IfcAxis2Placement3D> IfcElementarySurface::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(0)); }
bool IfcElementarySurface::is(Type::Enum v) { return v == Type::IfcElementarySurface || IfcSurface::is(v); }
Type::Enum IfcElementarySurface::type() { return Type::IfcElementarySurface; }
Type::Enum IfcElementarySurface::Class() { return Type::IfcElementarySurface; }
IfcElementarySurface::IfcElementarySurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcElementarySurface)) throw; entity = e; } 
// IfcEllipse
IfcPositiveLengthMeasure IfcEllipse::SemiAxis1() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcEllipse::SemiAxis2() { return *entity->getArgument(2); }
bool IfcEllipse::is(Type::Enum v) { return v == Type::IfcEllipse || IfcConic::is(v); }
Type::Enum IfcEllipse::type() { return Type::IfcEllipse; }
Type::Enum IfcEllipse::Class() { return Type::IfcEllipse; }
IfcEllipse::IfcEllipse(IfcAbstractEntityPtr e) { if (!is(Type::IfcEllipse)) throw; entity = e; } 
// IfcEllipseProfileDef
IfcPositiveLengthMeasure IfcEllipseProfileDef::SemiAxis1() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcEllipseProfileDef::SemiAxis2() { return *entity->getArgument(4); }
bool IfcEllipseProfileDef::is(Type::Enum v) { return v == Type::IfcEllipseProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcEllipseProfileDef::type() { return Type::IfcEllipseProfileDef; }
Type::Enum IfcEllipseProfileDef::Class() { return Type::IfcEllipseProfileDef; }
IfcEllipseProfileDef::IfcEllipseProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcEllipseProfileDef)) throw; entity = e; } 
// IfcEnergyConversionDevice
bool IfcEnergyConversionDevice::is(Type::Enum v) { return v == Type::IfcEnergyConversionDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcEnergyConversionDevice::type() { return Type::IfcEnergyConversionDevice; }
Type::Enum IfcEnergyConversionDevice::Class() { return Type::IfcEnergyConversionDevice; }
IfcEnergyConversionDevice::IfcEnergyConversionDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnergyConversionDevice)) throw; entity = e; } 
// IfcEnergyConversionDeviceType
bool IfcEnergyConversionDeviceType::is(Type::Enum v) { return v == Type::IfcEnergyConversionDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcEnergyConversionDeviceType::type() { return Type::IfcEnergyConversionDeviceType; }
Type::Enum IfcEnergyConversionDeviceType::Class() { return Type::IfcEnergyConversionDeviceType; }
IfcEnergyConversionDeviceType::IfcEnergyConversionDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnergyConversionDeviceType)) throw; entity = e; } 
// IfcEnergyProperties
bool IfcEnergyProperties::hasEnergySequence() { return !entity->getArgument(4)->isNull(); }
IfcEnergySequenceEnum::IfcEnergySequenceEnum IfcEnergyProperties::EnergySequence() { return IfcEnergySequenceEnum::FromString(*entity->getArgument(4)); }
bool IfcEnergyProperties::hasUserDefinedEnergySequence() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcEnergyProperties::UserDefinedEnergySequence() { return *entity->getArgument(5); }
bool IfcEnergyProperties::is(Type::Enum v) { return v == Type::IfcEnergyProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcEnergyProperties::type() { return Type::IfcEnergyProperties; }
Type::Enum IfcEnergyProperties::Class() { return Type::IfcEnergyProperties; }
IfcEnergyProperties::IfcEnergyProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnergyProperties)) throw; entity = e; } 
// IfcEnvironmentalImpactValue
IfcLabel IfcEnvironmentalImpactValue::ImpactType() { return *entity->getArgument(6); }
IfcEnvironmentalImpactCategoryEnum::IfcEnvironmentalImpactCategoryEnum IfcEnvironmentalImpactValue::Category() { return IfcEnvironmentalImpactCategoryEnum::FromString(*entity->getArgument(7)); }
bool IfcEnvironmentalImpactValue::hasUserDefinedCategory() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcEnvironmentalImpactValue::UserDefinedCategory() { return *entity->getArgument(8); }
bool IfcEnvironmentalImpactValue::is(Type::Enum v) { return v == Type::IfcEnvironmentalImpactValue || IfcAppliedValue::is(v); }
Type::Enum IfcEnvironmentalImpactValue::type() { return Type::IfcEnvironmentalImpactValue; }
Type::Enum IfcEnvironmentalImpactValue::Class() { return Type::IfcEnvironmentalImpactValue; }
IfcEnvironmentalImpactValue::IfcEnvironmentalImpactValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcEnvironmentalImpactValue)) throw; entity = e; } 
// IfcEquipmentElement
bool IfcEquipmentElement::is(Type::Enum v) { return v == Type::IfcEquipmentElement || IfcElement::is(v); }
Type::Enum IfcEquipmentElement::type() { return Type::IfcEquipmentElement; }
Type::Enum IfcEquipmentElement::Class() { return Type::IfcEquipmentElement; }
IfcEquipmentElement::IfcEquipmentElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcEquipmentElement)) throw; entity = e; } 
// IfcEquipmentStandard
bool IfcEquipmentStandard::is(Type::Enum v) { return v == Type::IfcEquipmentStandard || IfcControl::is(v); }
Type::Enum IfcEquipmentStandard::type() { return Type::IfcEquipmentStandard; }
Type::Enum IfcEquipmentStandard::Class() { return Type::IfcEquipmentStandard; }
IfcEquipmentStandard::IfcEquipmentStandard(IfcAbstractEntityPtr e) { if (!is(Type::IfcEquipmentStandard)) throw; entity = e; } 
// IfcEvaporativeCoolerType
IfcEvaporativeCoolerTypeEnum::IfcEvaporativeCoolerTypeEnum IfcEvaporativeCoolerType::PredefinedType() { return IfcEvaporativeCoolerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcEvaporativeCoolerType::is(Type::Enum v) { return v == Type::IfcEvaporativeCoolerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcEvaporativeCoolerType::type() { return Type::IfcEvaporativeCoolerType; }
Type::Enum IfcEvaporativeCoolerType::Class() { return Type::IfcEvaporativeCoolerType; }
IfcEvaporativeCoolerType::IfcEvaporativeCoolerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcEvaporativeCoolerType)) throw; entity = e; } 
// IfcEvaporatorType
IfcEvaporatorTypeEnum::IfcEvaporatorTypeEnum IfcEvaporatorType::PredefinedType() { return IfcEvaporatorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcEvaporatorType::is(Type::Enum v) { return v == Type::IfcEvaporatorType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcEvaporatorType::type() { return Type::IfcEvaporatorType; }
Type::Enum IfcEvaporatorType::Class() { return Type::IfcEvaporatorType; }
IfcEvaporatorType::IfcEvaporatorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcEvaporatorType)) throw; entity = e; } 
// IfcExtendedMaterialProperties
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcExtendedMaterialProperties::ExtendedProperties() { RETURN_AS_LIST(IfcProperty,1) }
bool IfcExtendedMaterialProperties::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcExtendedMaterialProperties::Description() { return *entity->getArgument(2); }
IfcLabel IfcExtendedMaterialProperties::Name() { return *entity->getArgument(3); }
bool IfcExtendedMaterialProperties::is(Type::Enum v) { return v == Type::IfcExtendedMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcExtendedMaterialProperties::type() { return Type::IfcExtendedMaterialProperties; }
Type::Enum IfcExtendedMaterialProperties::Class() { return Type::IfcExtendedMaterialProperties; }
IfcExtendedMaterialProperties::IfcExtendedMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcExtendedMaterialProperties)) throw; entity = e; } 
// IfcExternalReference
bool IfcExternalReference::hasLocation() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcExternalReference::Location() { return *entity->getArgument(0); }
bool IfcExternalReference::hasItemReference() { return !entity->getArgument(1)->isNull(); }
IfcIdentifier IfcExternalReference::ItemReference() { return *entity->getArgument(1); }
bool IfcExternalReference::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcExternalReference::Name() { return *entity->getArgument(2); }
bool IfcExternalReference::is(Type::Enum v) { return v == Type::IfcExternalReference; }
Type::Enum IfcExternalReference::type() { return Type::IfcExternalReference; }
Type::Enum IfcExternalReference::Class() { return Type::IfcExternalReference; }
IfcExternalReference::IfcExternalReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternalReference)) throw; entity = e; } 
// IfcExternallyDefinedHatchStyle
bool IfcExternallyDefinedHatchStyle::is(Type::Enum v) { return v == Type::IfcExternallyDefinedHatchStyle || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedHatchStyle::type() { return Type::IfcExternallyDefinedHatchStyle; }
Type::Enum IfcExternallyDefinedHatchStyle::Class() { return Type::IfcExternallyDefinedHatchStyle; }
IfcExternallyDefinedHatchStyle::IfcExternallyDefinedHatchStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedHatchStyle)) throw; entity = e; } 
// IfcExternallyDefinedSurfaceStyle
bool IfcExternallyDefinedSurfaceStyle::is(Type::Enum v) { return v == Type::IfcExternallyDefinedSurfaceStyle || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedSurfaceStyle::type() { return Type::IfcExternallyDefinedSurfaceStyle; }
Type::Enum IfcExternallyDefinedSurfaceStyle::Class() { return Type::IfcExternallyDefinedSurfaceStyle; }
IfcExternallyDefinedSurfaceStyle::IfcExternallyDefinedSurfaceStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedSurfaceStyle)) throw; entity = e; } 
// IfcExternallyDefinedSymbol
bool IfcExternallyDefinedSymbol::is(Type::Enum v) { return v == Type::IfcExternallyDefinedSymbol || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedSymbol::type() { return Type::IfcExternallyDefinedSymbol; }
Type::Enum IfcExternallyDefinedSymbol::Class() { return Type::IfcExternallyDefinedSymbol; }
IfcExternallyDefinedSymbol::IfcExternallyDefinedSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedSymbol)) throw; entity = e; } 
// IfcExternallyDefinedTextFont
bool IfcExternallyDefinedTextFont::is(Type::Enum v) { return v == Type::IfcExternallyDefinedTextFont || IfcExternalReference::is(v); }
Type::Enum IfcExternallyDefinedTextFont::type() { return Type::IfcExternallyDefinedTextFont; }
Type::Enum IfcExternallyDefinedTextFont::Class() { return Type::IfcExternallyDefinedTextFont; }
IfcExternallyDefinedTextFont::IfcExternallyDefinedTextFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcExternallyDefinedTextFont)) throw; entity = e; } 
// IfcExtrudedAreaSolid
SHARED_PTR<IfcDirection> IfcExtrudedAreaSolid::ExtrudedDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(2)); }
IfcPositiveLengthMeasure IfcExtrudedAreaSolid::Depth() { return *entity->getArgument(3); }
bool IfcExtrudedAreaSolid::is(Type::Enum v) { return v == Type::IfcExtrudedAreaSolid || IfcSweptAreaSolid::is(v); }
Type::Enum IfcExtrudedAreaSolid::type() { return Type::IfcExtrudedAreaSolid; }
Type::Enum IfcExtrudedAreaSolid::Class() { return Type::IfcExtrudedAreaSolid; }
IfcExtrudedAreaSolid::IfcExtrudedAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcExtrudedAreaSolid)) throw; entity = e; } 
// IfcFace
SHARED_PTR< IfcTemplatedEntityList<IfcFaceBound> > IfcFace::Bounds() { RETURN_AS_LIST(IfcFaceBound,0) }
bool IfcFace::is(Type::Enum v) { return v == Type::IfcFace || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcFace::type() { return Type::IfcFace; }
Type::Enum IfcFace::Class() { return Type::IfcFace; }
IfcFace::IfcFace(IfcAbstractEntityPtr e) { if (!is(Type::IfcFace)) throw; entity = e; } 
// IfcFaceBasedSurfaceModel
SHARED_PTR< IfcTemplatedEntityList<IfcConnectedFaceSet> > IfcFaceBasedSurfaceModel::FbsmFaces() { RETURN_AS_LIST(IfcConnectedFaceSet,0) }
bool IfcFaceBasedSurfaceModel::is(Type::Enum v) { return v == Type::IfcFaceBasedSurfaceModel || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFaceBasedSurfaceModel::type() { return Type::IfcFaceBasedSurfaceModel; }
Type::Enum IfcFaceBasedSurfaceModel::Class() { return Type::IfcFaceBasedSurfaceModel; }
IfcFaceBasedSurfaceModel::IfcFaceBasedSurfaceModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceBasedSurfaceModel)) throw; entity = e; } 
// IfcFaceBound
SHARED_PTR<IfcLoop> IfcFaceBound::Bound() { return reinterpret_pointer_cast<IfcBaseClass,IfcLoop>(*entity->getArgument(0)); }
bool IfcFaceBound::Orientation() { return *entity->getArgument(1); }
bool IfcFaceBound::is(Type::Enum v) { return v == Type::IfcFaceBound || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcFaceBound::type() { return Type::IfcFaceBound; }
Type::Enum IfcFaceBound::Class() { return Type::IfcFaceBound; }
IfcFaceBound::IfcFaceBound(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceBound)) throw; entity = e; } 
// IfcFaceOuterBound
bool IfcFaceOuterBound::is(Type::Enum v) { return v == Type::IfcFaceOuterBound || IfcFaceBound::is(v); }
Type::Enum IfcFaceOuterBound::type() { return Type::IfcFaceOuterBound; }
Type::Enum IfcFaceOuterBound::Class() { return Type::IfcFaceOuterBound; }
IfcFaceOuterBound::IfcFaceOuterBound(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceOuterBound)) throw; entity = e; } 
// IfcFaceSurface
SHARED_PTR<IfcSurface> IfcFaceSurface::FaceSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(1)); }
bool IfcFaceSurface::SameSense() { return *entity->getArgument(2); }
bool IfcFaceSurface::is(Type::Enum v) { return v == Type::IfcFaceSurface || IfcFace::is(v); }
Type::Enum IfcFaceSurface::type() { return Type::IfcFaceSurface; }
Type::Enum IfcFaceSurface::Class() { return Type::IfcFaceSurface; }
IfcFaceSurface::IfcFaceSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcFaceSurface)) throw; entity = e; } 
// IfcFacetedBrep
bool IfcFacetedBrep::is(Type::Enum v) { return v == Type::IfcFacetedBrep || IfcManifoldSolidBrep::is(v); }
Type::Enum IfcFacetedBrep::type() { return Type::IfcFacetedBrep; }
Type::Enum IfcFacetedBrep::Class() { return Type::IfcFacetedBrep; }
IfcFacetedBrep::IfcFacetedBrep(IfcAbstractEntityPtr e) { if (!is(Type::IfcFacetedBrep)) throw; entity = e; } 
// IfcFacetedBrepWithVoids
SHARED_PTR< IfcTemplatedEntityList<IfcClosedShell> > IfcFacetedBrepWithVoids::Voids() { RETURN_AS_LIST(IfcClosedShell,1) }
bool IfcFacetedBrepWithVoids::is(Type::Enum v) { return v == Type::IfcFacetedBrepWithVoids || IfcManifoldSolidBrep::is(v); }
Type::Enum IfcFacetedBrepWithVoids::type() { return Type::IfcFacetedBrepWithVoids; }
Type::Enum IfcFacetedBrepWithVoids::Class() { return Type::IfcFacetedBrepWithVoids; }
IfcFacetedBrepWithVoids::IfcFacetedBrepWithVoids(IfcAbstractEntityPtr e) { if (!is(Type::IfcFacetedBrepWithVoids)) throw; entity = e; } 
// IfcFailureConnectionCondition
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
bool IfcFailureConnectionCondition::is(Type::Enum v) { return v == Type::IfcFailureConnectionCondition || IfcStructuralConnectionCondition::is(v); }
Type::Enum IfcFailureConnectionCondition::type() { return Type::IfcFailureConnectionCondition; }
Type::Enum IfcFailureConnectionCondition::Class() { return Type::IfcFailureConnectionCondition; }
IfcFailureConnectionCondition::IfcFailureConnectionCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcFailureConnectionCondition)) throw; entity = e; } 
// IfcFanType
IfcFanTypeEnum::IfcFanTypeEnum IfcFanType::PredefinedType() { return IfcFanTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFanType::is(Type::Enum v) { return v == Type::IfcFanType || IfcFlowMovingDeviceType::is(v); }
Type::Enum IfcFanType::type() { return Type::IfcFanType; }
Type::Enum IfcFanType::Class() { return Type::IfcFanType; }
IfcFanType::IfcFanType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFanType)) throw; entity = e; } 
// IfcFastener
bool IfcFastener::is(Type::Enum v) { return v == Type::IfcFastener || IfcElementComponent::is(v); }
Type::Enum IfcFastener::type() { return Type::IfcFastener; }
Type::Enum IfcFastener::Class() { return Type::IfcFastener; }
IfcFastener::IfcFastener(IfcAbstractEntityPtr e) { if (!is(Type::IfcFastener)) throw; entity = e; } 
// IfcFastenerType
bool IfcFastenerType::is(Type::Enum v) { return v == Type::IfcFastenerType || IfcElementComponentType::is(v); }
Type::Enum IfcFastenerType::type() { return Type::IfcFastenerType; }
Type::Enum IfcFastenerType::Class() { return Type::IfcFastenerType; }
IfcFastenerType::IfcFastenerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFastenerType)) throw; entity = e; } 
// IfcFeatureElement
bool IfcFeatureElement::is(Type::Enum v) { return v == Type::IfcFeatureElement || IfcElement::is(v); }
Type::Enum IfcFeatureElement::type() { return Type::IfcFeatureElement; }
Type::Enum IfcFeatureElement::Class() { return Type::IfcFeatureElement; }
IfcFeatureElement::IfcFeatureElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcFeatureElement)) throw; entity = e; } 
// IfcFeatureElementAddition
IfcRelProjectsElement::list IfcFeatureElementAddition::ProjectsElements() { RETURN_INVERSE(IfcRelProjectsElement) }
bool IfcFeatureElementAddition::is(Type::Enum v) { return v == Type::IfcFeatureElementAddition || IfcFeatureElement::is(v); }
Type::Enum IfcFeatureElementAddition::type() { return Type::IfcFeatureElementAddition; }
Type::Enum IfcFeatureElementAddition::Class() { return Type::IfcFeatureElementAddition; }
IfcFeatureElementAddition::IfcFeatureElementAddition(IfcAbstractEntityPtr e) { if (!is(Type::IfcFeatureElementAddition)) throw; entity = e; } 
// IfcFeatureElementSubtraction
IfcRelVoidsElement::list IfcFeatureElementSubtraction::VoidsElements() { RETURN_INVERSE(IfcRelVoidsElement) }
bool IfcFeatureElementSubtraction::is(Type::Enum v) { return v == Type::IfcFeatureElementSubtraction || IfcFeatureElement::is(v); }
Type::Enum IfcFeatureElementSubtraction::type() { return Type::IfcFeatureElementSubtraction; }
Type::Enum IfcFeatureElementSubtraction::Class() { return Type::IfcFeatureElementSubtraction; }
IfcFeatureElementSubtraction::IfcFeatureElementSubtraction(IfcAbstractEntityPtr e) { if (!is(Type::IfcFeatureElementSubtraction)) throw; entity = e; } 
// IfcFillAreaStyle
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcFillAreaStyle::FillStyles() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcFillAreaStyle::is(Type::Enum v) { return v == Type::IfcFillAreaStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcFillAreaStyle::type() { return Type::IfcFillAreaStyle; }
Type::Enum IfcFillAreaStyle::Class() { return Type::IfcFillAreaStyle; }
IfcFillAreaStyle::IfcFillAreaStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyle)) throw; entity = e; } 
// IfcFillAreaStyleHatching
SHARED_PTR<IfcCurveStyle> IfcFillAreaStyleHatching::HatchLineAppearance() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurveStyle>(*entity->getArgument(0)); }
IfcHatchLineDistanceSelect IfcFillAreaStyleHatching::StartOfNextHatchLine() { return *entity->getArgument(1); }
bool IfcFillAreaStyleHatching::hasPointOfReferenceHatchLine() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR<IfcCartesianPoint> IfcFillAreaStyleHatching::PointOfReferenceHatchLine() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(2)); }
bool IfcFillAreaStyleHatching::hasPatternStart() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcCartesianPoint> IfcFillAreaStyleHatching::PatternStart() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(3)); }
IfcPlaneAngleMeasure IfcFillAreaStyleHatching::HatchLineAngle() { return *entity->getArgument(4); }
bool IfcFillAreaStyleHatching::is(Type::Enum v) { return v == Type::IfcFillAreaStyleHatching || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFillAreaStyleHatching::type() { return Type::IfcFillAreaStyleHatching; }
Type::Enum IfcFillAreaStyleHatching::Class() { return Type::IfcFillAreaStyleHatching; }
IfcFillAreaStyleHatching::IfcFillAreaStyleHatching(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyleHatching)) throw; entity = e; } 
// IfcFillAreaStyleTileSymbolWithStyle
SHARED_PTR<IfcAnnotationSymbolOccurrence> IfcFillAreaStyleTileSymbolWithStyle::Symbol() { return reinterpret_pointer_cast<IfcBaseClass,IfcAnnotationSymbolOccurrence>(*entity->getArgument(0)); }
bool IfcFillAreaStyleTileSymbolWithStyle::is(Type::Enum v) { return v == Type::IfcFillAreaStyleTileSymbolWithStyle || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFillAreaStyleTileSymbolWithStyle::type() { return Type::IfcFillAreaStyleTileSymbolWithStyle; }
Type::Enum IfcFillAreaStyleTileSymbolWithStyle::Class() { return Type::IfcFillAreaStyleTileSymbolWithStyle; }
IfcFillAreaStyleTileSymbolWithStyle::IfcFillAreaStyleTileSymbolWithStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyleTileSymbolWithStyle)) throw; entity = e; } 
// IfcFillAreaStyleTiles
SHARED_PTR<IfcOneDirectionRepeatFactor> IfcFillAreaStyleTiles::TilingPattern() { return reinterpret_pointer_cast<IfcBaseClass,IfcOneDirectionRepeatFactor>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcFillAreaStyleTiles::Tiles() { RETURN_AS_LIST(IfcAbstractSelect,1) }
IfcPositiveRatioMeasure IfcFillAreaStyleTiles::TilingScale() { return *entity->getArgument(2); }
bool IfcFillAreaStyleTiles::is(Type::Enum v) { return v == Type::IfcFillAreaStyleTiles || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcFillAreaStyleTiles::type() { return Type::IfcFillAreaStyleTiles; }
Type::Enum IfcFillAreaStyleTiles::Class() { return Type::IfcFillAreaStyleTiles; }
IfcFillAreaStyleTiles::IfcFillAreaStyleTiles(IfcAbstractEntityPtr e) { if (!is(Type::IfcFillAreaStyleTiles)) throw; entity = e; } 
// IfcFilterType
IfcFilterTypeEnum::IfcFilterTypeEnum IfcFilterType::PredefinedType() { return IfcFilterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFilterType::is(Type::Enum v) { return v == Type::IfcFilterType || IfcFlowTreatmentDeviceType::is(v); }
Type::Enum IfcFilterType::type() { return Type::IfcFilterType; }
Type::Enum IfcFilterType::Class() { return Type::IfcFilterType; }
IfcFilterType::IfcFilterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFilterType)) throw; entity = e; } 
// IfcFireSuppressionTerminalType
IfcFireSuppressionTerminalTypeEnum::IfcFireSuppressionTerminalTypeEnum IfcFireSuppressionTerminalType::PredefinedType() { return IfcFireSuppressionTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFireSuppressionTerminalType::is(Type::Enum v) { return v == Type::IfcFireSuppressionTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcFireSuppressionTerminalType::type() { return Type::IfcFireSuppressionTerminalType; }
Type::Enum IfcFireSuppressionTerminalType::Class() { return Type::IfcFireSuppressionTerminalType; }
IfcFireSuppressionTerminalType::IfcFireSuppressionTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFireSuppressionTerminalType)) throw; entity = e; } 
// IfcFlowController
bool IfcFlowController::is(Type::Enum v) { return v == Type::IfcFlowController || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowController::type() { return Type::IfcFlowController; }
Type::Enum IfcFlowController::Class() { return Type::IfcFlowController; }
IfcFlowController::IfcFlowController(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowController)) throw; entity = e; } 
// IfcFlowControllerType
bool IfcFlowControllerType::is(Type::Enum v) { return v == Type::IfcFlowControllerType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowControllerType::type() { return Type::IfcFlowControllerType; }
Type::Enum IfcFlowControllerType::Class() { return Type::IfcFlowControllerType; }
IfcFlowControllerType::IfcFlowControllerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowControllerType)) throw; entity = e; } 
// IfcFlowFitting
bool IfcFlowFitting::is(Type::Enum v) { return v == Type::IfcFlowFitting || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowFitting::type() { return Type::IfcFlowFitting; }
Type::Enum IfcFlowFitting::Class() { return Type::IfcFlowFitting; }
IfcFlowFitting::IfcFlowFitting(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowFitting)) throw; entity = e; } 
// IfcFlowFittingType
bool IfcFlowFittingType::is(Type::Enum v) { return v == Type::IfcFlowFittingType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowFittingType::type() { return Type::IfcFlowFittingType; }
Type::Enum IfcFlowFittingType::Class() { return Type::IfcFlowFittingType; }
IfcFlowFittingType::IfcFlowFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowFittingType)) throw; entity = e; } 
// IfcFlowInstrumentType
IfcFlowInstrumentTypeEnum::IfcFlowInstrumentTypeEnum IfcFlowInstrumentType::PredefinedType() { return IfcFlowInstrumentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFlowInstrumentType::is(Type::Enum v) { return v == Type::IfcFlowInstrumentType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcFlowInstrumentType::type() { return Type::IfcFlowInstrumentType; }
Type::Enum IfcFlowInstrumentType::Class() { return Type::IfcFlowInstrumentType; }
IfcFlowInstrumentType::IfcFlowInstrumentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowInstrumentType)) throw; entity = e; } 
// IfcFlowMeterType
IfcFlowMeterTypeEnum::IfcFlowMeterTypeEnum IfcFlowMeterType::PredefinedType() { return IfcFlowMeterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcFlowMeterType::is(Type::Enum v) { return v == Type::IfcFlowMeterType || IfcFlowControllerType::is(v); }
Type::Enum IfcFlowMeterType::type() { return Type::IfcFlowMeterType; }
Type::Enum IfcFlowMeterType::Class() { return Type::IfcFlowMeterType; }
IfcFlowMeterType::IfcFlowMeterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowMeterType)) throw; entity = e; } 
// IfcFlowMovingDevice
bool IfcFlowMovingDevice::is(Type::Enum v) { return v == Type::IfcFlowMovingDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowMovingDevice::type() { return Type::IfcFlowMovingDevice; }
Type::Enum IfcFlowMovingDevice::Class() { return Type::IfcFlowMovingDevice; }
IfcFlowMovingDevice::IfcFlowMovingDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowMovingDevice)) throw; entity = e; } 
// IfcFlowMovingDeviceType
bool IfcFlowMovingDeviceType::is(Type::Enum v) { return v == Type::IfcFlowMovingDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowMovingDeviceType::type() { return Type::IfcFlowMovingDeviceType; }
Type::Enum IfcFlowMovingDeviceType::Class() { return Type::IfcFlowMovingDeviceType; }
IfcFlowMovingDeviceType::IfcFlowMovingDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowMovingDeviceType)) throw; entity = e; } 
// IfcFlowSegment
bool IfcFlowSegment::is(Type::Enum v) { return v == Type::IfcFlowSegment || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowSegment::type() { return Type::IfcFlowSegment; }
Type::Enum IfcFlowSegment::Class() { return Type::IfcFlowSegment; }
IfcFlowSegment::IfcFlowSegment(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowSegment)) throw; entity = e; } 
// IfcFlowSegmentType
bool IfcFlowSegmentType::is(Type::Enum v) { return v == Type::IfcFlowSegmentType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowSegmentType::type() { return Type::IfcFlowSegmentType; }
Type::Enum IfcFlowSegmentType::Class() { return Type::IfcFlowSegmentType; }
IfcFlowSegmentType::IfcFlowSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowSegmentType)) throw; entity = e; } 
// IfcFlowStorageDevice
bool IfcFlowStorageDevice::is(Type::Enum v) { return v == Type::IfcFlowStorageDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowStorageDevice::type() { return Type::IfcFlowStorageDevice; }
Type::Enum IfcFlowStorageDevice::Class() { return Type::IfcFlowStorageDevice; }
IfcFlowStorageDevice::IfcFlowStorageDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowStorageDevice)) throw; entity = e; } 
// IfcFlowStorageDeviceType
bool IfcFlowStorageDeviceType::is(Type::Enum v) { return v == Type::IfcFlowStorageDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowStorageDeviceType::type() { return Type::IfcFlowStorageDeviceType; }
Type::Enum IfcFlowStorageDeviceType::Class() { return Type::IfcFlowStorageDeviceType; }
IfcFlowStorageDeviceType::IfcFlowStorageDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowStorageDeviceType)) throw; entity = e; } 
// IfcFlowTerminal
bool IfcFlowTerminal::is(Type::Enum v) { return v == Type::IfcFlowTerminal || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowTerminal::type() { return Type::IfcFlowTerminal; }
Type::Enum IfcFlowTerminal::Class() { return Type::IfcFlowTerminal; }
IfcFlowTerminal::IfcFlowTerminal(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTerminal)) throw; entity = e; } 
// IfcFlowTerminalType
bool IfcFlowTerminalType::is(Type::Enum v) { return v == Type::IfcFlowTerminalType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowTerminalType::type() { return Type::IfcFlowTerminalType; }
Type::Enum IfcFlowTerminalType::Class() { return Type::IfcFlowTerminalType; }
IfcFlowTerminalType::IfcFlowTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTerminalType)) throw; entity = e; } 
// IfcFlowTreatmentDevice
bool IfcFlowTreatmentDevice::is(Type::Enum v) { return v == Type::IfcFlowTreatmentDevice || IfcDistributionFlowElement::is(v); }
Type::Enum IfcFlowTreatmentDevice::type() { return Type::IfcFlowTreatmentDevice; }
Type::Enum IfcFlowTreatmentDevice::Class() { return Type::IfcFlowTreatmentDevice; }
IfcFlowTreatmentDevice::IfcFlowTreatmentDevice(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTreatmentDevice)) throw; entity = e; } 
// IfcFlowTreatmentDeviceType
bool IfcFlowTreatmentDeviceType::is(Type::Enum v) { return v == Type::IfcFlowTreatmentDeviceType || IfcDistributionFlowElementType::is(v); }
Type::Enum IfcFlowTreatmentDeviceType::type() { return Type::IfcFlowTreatmentDeviceType; }
Type::Enum IfcFlowTreatmentDeviceType::Class() { return Type::IfcFlowTreatmentDeviceType; }
IfcFlowTreatmentDeviceType::IfcFlowTreatmentDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFlowTreatmentDeviceType)) throw; entity = e; } 
// IfcFluidFlowProperties
IfcPropertySourceEnum::IfcPropertySourceEnum IfcFluidFlowProperties::PropertySource() { return IfcPropertySourceEnum::FromString(*entity->getArgument(4)); }
bool IfcFluidFlowProperties::hasFlowConditionTimeSeries() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR<IfcTimeSeries> IfcFluidFlowProperties::FlowConditionTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(5)); }
bool IfcFluidFlowProperties::hasVelocityTimeSeries() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcTimeSeries> IfcFluidFlowProperties::VelocityTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(6)); }
bool IfcFluidFlowProperties::hasFlowrateTimeSeries() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR<IfcTimeSeries> IfcFluidFlowProperties::FlowrateTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(7)); }
SHARED_PTR<IfcMaterial> IfcFluidFlowProperties::Fluid() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(8)); }
bool IfcFluidFlowProperties::hasPressureTimeSeries() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR<IfcTimeSeries> IfcFluidFlowProperties::PressureTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(9)); }
bool IfcFluidFlowProperties::hasUserDefinedPropertySource() { return !entity->getArgument(10)->isNull(); }
IfcLabel IfcFluidFlowProperties::UserDefinedPropertySource() { return *entity->getArgument(10); }
bool IfcFluidFlowProperties::hasTemperatureSingleValue() { return !entity->getArgument(11)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcFluidFlowProperties::TemperatureSingleValue() { return *entity->getArgument(11); }
bool IfcFluidFlowProperties::hasWetBulbTemperatureSingleValue() { return !entity->getArgument(12)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcFluidFlowProperties::WetBulbTemperatureSingleValue() { return *entity->getArgument(12); }
bool IfcFluidFlowProperties::hasWetBulbTemperatureTimeSeries() { return !entity->getArgument(13)->isNull(); }
SHARED_PTR<IfcTimeSeries> IfcFluidFlowProperties::WetBulbTemperatureTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(13)); }
bool IfcFluidFlowProperties::hasTemperatureTimeSeries() { return !entity->getArgument(14)->isNull(); }
SHARED_PTR<IfcTimeSeries> IfcFluidFlowProperties::TemperatureTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(14)); }
bool IfcFluidFlowProperties::hasFlowrateSingleValue() { return !entity->getArgument(15)->isNull(); }
IfcDerivedMeasureValue IfcFluidFlowProperties::FlowrateSingleValue() { return *entity->getArgument(15); }
bool IfcFluidFlowProperties::hasFlowConditionSingleValue() { return !entity->getArgument(16)->isNull(); }
IfcPositiveRatioMeasure IfcFluidFlowProperties::FlowConditionSingleValue() { return *entity->getArgument(16); }
bool IfcFluidFlowProperties::hasVelocitySingleValue() { return !entity->getArgument(17)->isNull(); }
IfcLinearVelocityMeasure IfcFluidFlowProperties::VelocitySingleValue() { return *entity->getArgument(17); }
bool IfcFluidFlowProperties::hasPressureSingleValue() { return !entity->getArgument(18)->isNull(); }
IfcPressureMeasure IfcFluidFlowProperties::PressureSingleValue() { return *entity->getArgument(18); }
bool IfcFluidFlowProperties::is(Type::Enum v) { return v == Type::IfcFluidFlowProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcFluidFlowProperties::type() { return Type::IfcFluidFlowProperties; }
Type::Enum IfcFluidFlowProperties::Class() { return Type::IfcFluidFlowProperties; }
IfcFluidFlowProperties::IfcFluidFlowProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcFluidFlowProperties)) throw; entity = e; } 
// IfcFooting
IfcFootingTypeEnum::IfcFootingTypeEnum IfcFooting::PredefinedType() { return IfcFootingTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcFooting::is(Type::Enum v) { return v == Type::IfcFooting || IfcBuildingElement::is(v); }
Type::Enum IfcFooting::type() { return Type::IfcFooting; }
Type::Enum IfcFooting::Class() { return Type::IfcFooting; }
IfcFooting::IfcFooting(IfcAbstractEntityPtr e) { if (!is(Type::IfcFooting)) throw; entity = e; } 
// IfcFuelProperties
bool IfcFuelProperties::hasCombustionTemperature() { return !entity->getArgument(1)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcFuelProperties::CombustionTemperature() { return *entity->getArgument(1); }
bool IfcFuelProperties::hasCarbonContent() { return !entity->getArgument(2)->isNull(); }
IfcPositiveRatioMeasure IfcFuelProperties::CarbonContent() { return *entity->getArgument(2); }
bool IfcFuelProperties::hasLowerHeatingValue() { return !entity->getArgument(3)->isNull(); }
IfcHeatingValueMeasure IfcFuelProperties::LowerHeatingValue() { return *entity->getArgument(3); }
bool IfcFuelProperties::hasHigherHeatingValue() { return !entity->getArgument(4)->isNull(); }
IfcHeatingValueMeasure IfcFuelProperties::HigherHeatingValue() { return *entity->getArgument(4); }
bool IfcFuelProperties::is(Type::Enum v) { return v == Type::IfcFuelProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcFuelProperties::type() { return Type::IfcFuelProperties; }
Type::Enum IfcFuelProperties::Class() { return Type::IfcFuelProperties; }
IfcFuelProperties::IfcFuelProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcFuelProperties)) throw; entity = e; } 
// IfcFurnishingElement
bool IfcFurnishingElement::is(Type::Enum v) { return v == Type::IfcFurnishingElement || IfcElement::is(v); }
Type::Enum IfcFurnishingElement::type() { return Type::IfcFurnishingElement; }
Type::Enum IfcFurnishingElement::Class() { return Type::IfcFurnishingElement; }
IfcFurnishingElement::IfcFurnishingElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnishingElement)) throw; entity = e; } 
// IfcFurnishingElementType
bool IfcFurnishingElementType::is(Type::Enum v) { return v == Type::IfcFurnishingElementType || IfcElementType::is(v); }
Type::Enum IfcFurnishingElementType::type() { return Type::IfcFurnishingElementType; }
Type::Enum IfcFurnishingElementType::Class() { return Type::IfcFurnishingElementType; }
IfcFurnishingElementType::IfcFurnishingElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnishingElementType)) throw; entity = e; } 
// IfcFurnitureStandard
bool IfcFurnitureStandard::is(Type::Enum v) { return v == Type::IfcFurnitureStandard || IfcControl::is(v); }
Type::Enum IfcFurnitureStandard::type() { return Type::IfcFurnitureStandard; }
Type::Enum IfcFurnitureStandard::Class() { return Type::IfcFurnitureStandard; }
IfcFurnitureStandard::IfcFurnitureStandard(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnitureStandard)) throw; entity = e; } 
// IfcFurnitureType
IfcAssemblyPlaceEnum::IfcAssemblyPlaceEnum IfcFurnitureType::AssemblyPlace() { return IfcAssemblyPlaceEnum::FromString(*entity->getArgument(9)); }
bool IfcFurnitureType::is(Type::Enum v) { return v == Type::IfcFurnitureType || IfcFurnishingElementType::is(v); }
Type::Enum IfcFurnitureType::type() { return Type::IfcFurnitureType; }
Type::Enum IfcFurnitureType::Class() { return Type::IfcFurnitureType; }
IfcFurnitureType::IfcFurnitureType(IfcAbstractEntityPtr e) { if (!is(Type::IfcFurnitureType)) throw; entity = e; } 
// IfcGasTerminalType
IfcGasTerminalTypeEnum::IfcGasTerminalTypeEnum IfcGasTerminalType::PredefinedType() { return IfcGasTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcGasTerminalType::is(Type::Enum v) { return v == Type::IfcGasTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcGasTerminalType::type() { return Type::IfcGasTerminalType; }
Type::Enum IfcGasTerminalType::Class() { return Type::IfcGasTerminalType; }
IfcGasTerminalType::IfcGasTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcGasTerminalType)) throw; entity = e; } 
// IfcGeneralMaterialProperties
bool IfcGeneralMaterialProperties::hasMolecularWeight() { return !entity->getArgument(1)->isNull(); }
IfcMolecularWeightMeasure IfcGeneralMaterialProperties::MolecularWeight() { return *entity->getArgument(1); }
bool IfcGeneralMaterialProperties::hasPorosity() { return !entity->getArgument(2)->isNull(); }
IfcNormalisedRatioMeasure IfcGeneralMaterialProperties::Porosity() { return *entity->getArgument(2); }
bool IfcGeneralMaterialProperties::hasMassDensity() { return !entity->getArgument(3)->isNull(); }
IfcMassDensityMeasure IfcGeneralMaterialProperties::MassDensity() { return *entity->getArgument(3); }
bool IfcGeneralMaterialProperties::is(Type::Enum v) { return v == Type::IfcGeneralMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcGeneralMaterialProperties::type() { return Type::IfcGeneralMaterialProperties; }
Type::Enum IfcGeneralMaterialProperties::Class() { return Type::IfcGeneralMaterialProperties; }
IfcGeneralMaterialProperties::IfcGeneralMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeneralMaterialProperties)) throw; entity = e; } 
// IfcGeneralProfileProperties
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
bool IfcGeneralProfileProperties::is(Type::Enum v) { return v == Type::IfcGeneralProfileProperties || IfcProfileProperties::is(v); }
Type::Enum IfcGeneralProfileProperties::type() { return Type::IfcGeneralProfileProperties; }
Type::Enum IfcGeneralProfileProperties::Class() { return Type::IfcGeneralProfileProperties; }
IfcGeneralProfileProperties::IfcGeneralProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeneralProfileProperties)) throw; entity = e; } 
// IfcGeometricCurveSet
bool IfcGeometricCurveSet::is(Type::Enum v) { return v == Type::IfcGeometricCurveSet || IfcGeometricSet::is(v); }
Type::Enum IfcGeometricCurveSet::type() { return Type::IfcGeometricCurveSet; }
Type::Enum IfcGeometricCurveSet::Class() { return Type::IfcGeometricCurveSet; }
IfcGeometricCurveSet::IfcGeometricCurveSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricCurveSet)) throw; entity = e; } 
// IfcGeometricRepresentationContext
IfcDimensionCount IfcGeometricRepresentationContext::CoordinateSpaceDimension() { return *entity->getArgument(2); }
bool IfcGeometricRepresentationContext::hasPrecision() { return !entity->getArgument(3)->isNull(); }
float IfcGeometricRepresentationContext::Precision() { return *entity->getArgument(3); }
IfcAxis2Placement IfcGeometricRepresentationContext::WorldCoordinateSystem() { return *entity->getArgument(4); }
bool IfcGeometricRepresentationContext::hasTrueNorth() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR<IfcDirection> IfcGeometricRepresentationContext::TrueNorth() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(5)); }
IfcGeometricRepresentationSubContext::list IfcGeometricRepresentationContext::HasSubContexts() { RETURN_INVERSE(IfcGeometricRepresentationSubContext) }
bool IfcGeometricRepresentationContext::is(Type::Enum v) { return v == Type::IfcGeometricRepresentationContext || IfcRepresentationContext::is(v); }
Type::Enum IfcGeometricRepresentationContext::type() { return Type::IfcGeometricRepresentationContext; }
Type::Enum IfcGeometricRepresentationContext::Class() { return Type::IfcGeometricRepresentationContext; }
IfcGeometricRepresentationContext::IfcGeometricRepresentationContext(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricRepresentationContext)) throw; entity = e; } 
// IfcGeometricRepresentationItem
bool IfcGeometricRepresentationItem::is(Type::Enum v) { return v == Type::IfcGeometricRepresentationItem || IfcRepresentationItem::is(v); }
Type::Enum IfcGeometricRepresentationItem::type() { return Type::IfcGeometricRepresentationItem; }
Type::Enum IfcGeometricRepresentationItem::Class() { return Type::IfcGeometricRepresentationItem; }
IfcGeometricRepresentationItem::IfcGeometricRepresentationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricRepresentationItem)) throw; entity = e; } 
// IfcGeometricRepresentationSubContext
SHARED_PTR<IfcGeometricRepresentationContext> IfcGeometricRepresentationSubContext::ParentContext() { return reinterpret_pointer_cast<IfcBaseClass,IfcGeometricRepresentationContext>(*entity->getArgument(6)); }
bool IfcGeometricRepresentationSubContext::hasTargetScale() { return !entity->getArgument(7)->isNull(); }
IfcPositiveRatioMeasure IfcGeometricRepresentationSubContext::TargetScale() { return *entity->getArgument(7); }
IfcGeometricProjectionEnum::IfcGeometricProjectionEnum IfcGeometricRepresentationSubContext::TargetView() { return IfcGeometricProjectionEnum::FromString(*entity->getArgument(8)); }
bool IfcGeometricRepresentationSubContext::hasUserDefinedTargetView() { return !entity->getArgument(9)->isNull(); }
IfcLabel IfcGeometricRepresentationSubContext::UserDefinedTargetView() { return *entity->getArgument(9); }
bool IfcGeometricRepresentationSubContext::is(Type::Enum v) { return v == Type::IfcGeometricRepresentationSubContext || IfcGeometricRepresentationContext::is(v); }
Type::Enum IfcGeometricRepresentationSubContext::type() { return Type::IfcGeometricRepresentationSubContext; }
Type::Enum IfcGeometricRepresentationSubContext::Class() { return Type::IfcGeometricRepresentationSubContext; }
IfcGeometricRepresentationSubContext::IfcGeometricRepresentationSubContext(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricRepresentationSubContext)) throw; entity = e; } 
// IfcGeometricSet
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcGeometricSet::Elements() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcGeometricSet::is(Type::Enum v) { return v == Type::IfcGeometricSet || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcGeometricSet::type() { return Type::IfcGeometricSet; }
Type::Enum IfcGeometricSet::Class() { return Type::IfcGeometricSet; }
IfcGeometricSet::IfcGeometricSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcGeometricSet)) throw; entity = e; } 
// IfcGrid
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcGrid::UAxes() { RETURN_AS_LIST(IfcGridAxis,7) }
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcGrid::VAxes() { RETURN_AS_LIST(IfcGridAxis,8) }
bool IfcGrid::hasWAxes() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcGrid::WAxes() { RETURN_AS_LIST(IfcGridAxis,9) }
IfcRelContainedInSpatialStructure::list IfcGrid::ContainedInStructure() { RETURN_INVERSE(IfcRelContainedInSpatialStructure) }
bool IfcGrid::is(Type::Enum v) { return v == Type::IfcGrid || IfcProduct::is(v); }
Type::Enum IfcGrid::type() { return Type::IfcGrid; }
Type::Enum IfcGrid::Class() { return Type::IfcGrid; }
IfcGrid::IfcGrid(IfcAbstractEntityPtr e) { if (!is(Type::IfcGrid)) throw; entity = e; } 
// IfcGridAxis
bool IfcGridAxis::hasAxisTag() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcGridAxis::AxisTag() { return *entity->getArgument(0); }
SHARED_PTR<IfcCurve> IfcGridAxis::AxisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(1)); }
IfcBoolean IfcGridAxis::SameSense() { return *entity->getArgument(2); }
IfcGrid::list IfcGridAxis::PartOfW() { RETURN_INVERSE(IfcGrid) }
IfcGrid::list IfcGridAxis::PartOfV() { RETURN_INVERSE(IfcGrid) }
IfcGrid::list IfcGridAxis::PartOfU() { RETURN_INVERSE(IfcGrid) }
IfcVirtualGridIntersection::list IfcGridAxis::HasIntersections() { RETURN_INVERSE(IfcVirtualGridIntersection) }
bool IfcGridAxis::is(Type::Enum v) { return v == Type::IfcGridAxis; }
Type::Enum IfcGridAxis::type() { return Type::IfcGridAxis; }
Type::Enum IfcGridAxis::Class() { return Type::IfcGridAxis; }
IfcGridAxis::IfcGridAxis(IfcAbstractEntityPtr e) { if (!is(Type::IfcGridAxis)) throw; entity = e; } 
// IfcGridPlacement
SHARED_PTR<IfcVirtualGridIntersection> IfcGridPlacement::PlacementLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcVirtualGridIntersection>(*entity->getArgument(0)); }
bool IfcGridPlacement::hasPlacementRefDirection() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcVirtualGridIntersection> IfcGridPlacement::PlacementRefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcVirtualGridIntersection>(*entity->getArgument(1)); }
bool IfcGridPlacement::is(Type::Enum v) { return v == Type::IfcGridPlacement || IfcObjectPlacement::is(v); }
Type::Enum IfcGridPlacement::type() { return Type::IfcGridPlacement; }
Type::Enum IfcGridPlacement::Class() { return Type::IfcGridPlacement; }
IfcGridPlacement::IfcGridPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcGridPlacement)) throw; entity = e; } 
// IfcGroup
IfcRelAssignsToGroup::list IfcGroup::IsGroupedBy() { RETURN_INVERSE(IfcRelAssignsToGroup) }
bool IfcGroup::is(Type::Enum v) { return v == Type::IfcGroup || IfcObject::is(v); }
Type::Enum IfcGroup::type() { return Type::IfcGroup; }
Type::Enum IfcGroup::Class() { return Type::IfcGroup; }
IfcGroup::IfcGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcGroup)) throw; entity = e; } 
// IfcHalfSpaceSolid
SHARED_PTR<IfcSurface> IfcHalfSpaceSolid::BaseSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(0)); }
bool IfcHalfSpaceSolid::AgreementFlag() { return *entity->getArgument(1); }
bool IfcHalfSpaceSolid::is(Type::Enum v) { return v == Type::IfcHalfSpaceSolid || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcHalfSpaceSolid::type() { return Type::IfcHalfSpaceSolid; }
Type::Enum IfcHalfSpaceSolid::Class() { return Type::IfcHalfSpaceSolid; }
IfcHalfSpaceSolid::IfcHalfSpaceSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcHalfSpaceSolid)) throw; entity = e; } 
// IfcHeatExchangerType
IfcHeatExchangerTypeEnum::IfcHeatExchangerTypeEnum IfcHeatExchangerType::PredefinedType() { return IfcHeatExchangerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcHeatExchangerType::is(Type::Enum v) { return v == Type::IfcHeatExchangerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcHeatExchangerType::type() { return Type::IfcHeatExchangerType; }
Type::Enum IfcHeatExchangerType::Class() { return Type::IfcHeatExchangerType; }
IfcHeatExchangerType::IfcHeatExchangerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcHeatExchangerType)) throw; entity = e; } 
// IfcHumidifierType
IfcHumidifierTypeEnum::IfcHumidifierTypeEnum IfcHumidifierType::PredefinedType() { return IfcHumidifierTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcHumidifierType::is(Type::Enum v) { return v == Type::IfcHumidifierType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcHumidifierType::type() { return Type::IfcHumidifierType; }
Type::Enum IfcHumidifierType::Class() { return Type::IfcHumidifierType; }
IfcHumidifierType::IfcHumidifierType(IfcAbstractEntityPtr e) { if (!is(Type::IfcHumidifierType)) throw; entity = e; } 
// IfcHygroscopicMaterialProperties
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
bool IfcHygroscopicMaterialProperties::is(Type::Enum v) { return v == Type::IfcHygroscopicMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcHygroscopicMaterialProperties::type() { return Type::IfcHygroscopicMaterialProperties; }
Type::Enum IfcHygroscopicMaterialProperties::Class() { return Type::IfcHygroscopicMaterialProperties; }
IfcHygroscopicMaterialProperties::IfcHygroscopicMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcHygroscopicMaterialProperties)) throw; entity = e; } 
// IfcIShapeProfileDef
IfcPositiveLengthMeasure IfcIShapeProfileDef::OverallWidth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::OverallDepth() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::WebThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::FlangeThickness() { return *entity->getArgument(6); }
bool IfcIShapeProfileDef::hasFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcIShapeProfileDef::FilletRadius() { return *entity->getArgument(7); }
bool IfcIShapeProfileDef::is(Type::Enum v) { return v == Type::IfcIShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcIShapeProfileDef::type() { return Type::IfcIShapeProfileDef; }
Type::Enum IfcIShapeProfileDef::Class() { return Type::IfcIShapeProfileDef; }
IfcIShapeProfileDef::IfcIShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcIShapeProfileDef)) throw; entity = e; } 
// IfcImageTexture
IfcIdentifier IfcImageTexture::UrlReference() { return *entity->getArgument(4); }
bool IfcImageTexture::is(Type::Enum v) { return v == Type::IfcImageTexture || IfcSurfaceTexture::is(v); }
Type::Enum IfcImageTexture::type() { return Type::IfcImageTexture; }
Type::Enum IfcImageTexture::Class() { return Type::IfcImageTexture; }
IfcImageTexture::IfcImageTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcImageTexture)) throw; entity = e; } 
// IfcInventory
IfcInventoryTypeEnum::IfcInventoryTypeEnum IfcInventory::InventoryType() { return IfcInventoryTypeEnum::FromString(*entity->getArgument(5)); }
IfcActorSelect IfcInventory::Jurisdiction() { return *entity->getArgument(6); }
SHARED_PTR< IfcTemplatedEntityList<IfcPerson> > IfcInventory::ResponsiblePersons() { RETURN_AS_LIST(IfcPerson,7) }
SHARED_PTR<IfcCalendarDate> IfcInventory::LastUpdateDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(8)); }
bool IfcInventory::hasCurrentValue() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR<IfcCostValue> IfcInventory::CurrentValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(9)); }
bool IfcInventory::hasOriginalValue() { return !entity->getArgument(10)->isNull(); }
SHARED_PTR<IfcCostValue> IfcInventory::OriginalValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcCostValue>(*entity->getArgument(10)); }
bool IfcInventory::is(Type::Enum v) { return v == Type::IfcInventory || IfcGroup::is(v); }
Type::Enum IfcInventory::type() { return Type::IfcInventory; }
Type::Enum IfcInventory::Class() { return Type::IfcInventory; }
IfcInventory::IfcInventory(IfcAbstractEntityPtr e) { if (!is(Type::IfcInventory)) throw; entity = e; } 
// IfcIrregularTimeSeries
SHARED_PTR< IfcTemplatedEntityList<IfcIrregularTimeSeriesValue> > IfcIrregularTimeSeries::Values() { RETURN_AS_LIST(IfcIrregularTimeSeriesValue,8) }
bool IfcIrregularTimeSeries::is(Type::Enum v) { return v == Type::IfcIrregularTimeSeries || IfcTimeSeries::is(v); }
Type::Enum IfcIrregularTimeSeries::type() { return Type::IfcIrregularTimeSeries; }
Type::Enum IfcIrregularTimeSeries::Class() { return Type::IfcIrregularTimeSeries; }
IfcIrregularTimeSeries::IfcIrregularTimeSeries(IfcAbstractEntityPtr e) { if (!is(Type::IfcIrregularTimeSeries)) throw; entity = e; } 
// IfcIrregularTimeSeriesValue
IfcDateTimeSelect IfcIrregularTimeSeriesValue::TimeStamp() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcIrregularTimeSeriesValue::ListValues() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcIrregularTimeSeriesValue::is(Type::Enum v) { return v == Type::IfcIrregularTimeSeriesValue; }
Type::Enum IfcIrregularTimeSeriesValue::type() { return Type::IfcIrregularTimeSeriesValue; }
Type::Enum IfcIrregularTimeSeriesValue::Class() { return Type::IfcIrregularTimeSeriesValue; }
IfcIrregularTimeSeriesValue::IfcIrregularTimeSeriesValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcIrregularTimeSeriesValue)) throw; entity = e; } 
// IfcJunctionBoxType
IfcJunctionBoxTypeEnum::IfcJunctionBoxTypeEnum IfcJunctionBoxType::PredefinedType() { return IfcJunctionBoxTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcJunctionBoxType::is(Type::Enum v) { return v == Type::IfcJunctionBoxType || IfcFlowFittingType::is(v); }
Type::Enum IfcJunctionBoxType::type() { return Type::IfcJunctionBoxType; }
Type::Enum IfcJunctionBoxType::Class() { return Type::IfcJunctionBoxType; }
IfcJunctionBoxType::IfcJunctionBoxType(IfcAbstractEntityPtr e) { if (!is(Type::IfcJunctionBoxType)) throw; entity = e; } 
// IfcLShapeProfileDef
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
bool IfcLShapeProfileDef::is(Type::Enum v) { return v == Type::IfcLShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcLShapeProfileDef::type() { return Type::IfcLShapeProfileDef; }
Type::Enum IfcLShapeProfileDef::Class() { return Type::IfcLShapeProfileDef; }
IfcLShapeProfileDef::IfcLShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcLShapeProfileDef)) throw; entity = e; } 
// IfcLaborResource
bool IfcLaborResource::hasSkillSet() { return !entity->getArgument(9)->isNull(); }
IfcText IfcLaborResource::SkillSet() { return *entity->getArgument(9); }
bool IfcLaborResource::is(Type::Enum v) { return v == Type::IfcLaborResource || IfcConstructionResource::is(v); }
Type::Enum IfcLaborResource::type() { return Type::IfcLaborResource; }
Type::Enum IfcLaborResource::Class() { return Type::IfcLaborResource; }
IfcLaborResource::IfcLaborResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcLaborResource)) throw; entity = e; } 
// IfcLampType
IfcLampTypeEnum::IfcLampTypeEnum IfcLampType::PredefinedType() { return IfcLampTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcLampType::is(Type::Enum v) { return v == Type::IfcLampType || IfcFlowTerminalType::is(v); }
Type::Enum IfcLampType::type() { return Type::IfcLampType; }
Type::Enum IfcLampType::Class() { return Type::IfcLampType; }
IfcLampType::IfcLampType(IfcAbstractEntityPtr e) { if (!is(Type::IfcLampType)) throw; entity = e; } 
// IfcLibraryInformation
IfcLabel IfcLibraryInformation::Name() { return *entity->getArgument(0); }
bool IfcLibraryInformation::hasVersion() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcLibraryInformation::Version() { return *entity->getArgument(1); }
bool IfcLibraryInformation::hasPublisher() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR<IfcOrganization> IfcLibraryInformation::Publisher() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(2)); }
bool IfcLibraryInformation::hasVersionDate() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcCalendarDate> IfcLibraryInformation::VersionDate() { return reinterpret_pointer_cast<IfcBaseClass,IfcCalendarDate>(*entity->getArgument(3)); }
bool IfcLibraryInformation::hasLibraryReference() { return !entity->getArgument(4)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcLibraryReference> > IfcLibraryInformation::LibraryReference() { RETURN_AS_LIST(IfcLibraryReference,4) }
bool IfcLibraryInformation::is(Type::Enum v) { return v == Type::IfcLibraryInformation; }
Type::Enum IfcLibraryInformation::type() { return Type::IfcLibraryInformation; }
Type::Enum IfcLibraryInformation::Class() { return Type::IfcLibraryInformation; }
IfcLibraryInformation::IfcLibraryInformation(IfcAbstractEntityPtr e) { if (!is(Type::IfcLibraryInformation)) throw; entity = e; } 
// IfcLibraryReference
IfcLibraryInformation::list IfcLibraryReference::ReferenceIntoLibrary() { RETURN_INVERSE(IfcLibraryInformation) }
bool IfcLibraryReference::is(Type::Enum v) { return v == Type::IfcLibraryReference || IfcExternalReference::is(v); }
Type::Enum IfcLibraryReference::type() { return Type::IfcLibraryReference; }
Type::Enum IfcLibraryReference::Class() { return Type::IfcLibraryReference; }
IfcLibraryReference::IfcLibraryReference(IfcAbstractEntityPtr e) { if (!is(Type::IfcLibraryReference)) throw; entity = e; } 
// IfcLightDistributionData
IfcPlaneAngleMeasure IfcLightDistributionData::MainPlaneAngle() { return *entity->getArgument(0); }
std::vector<IfcPlaneAngleMeasure> /*[1:?]*/ IfcLightDistributionData::SecondaryPlaneAngle() { return *entity->getArgument(1); }
std::vector<IfcLuminousIntensityDistributionMeasure> /*[1:?]*/ IfcLightDistributionData::LuminousIntensity() { return *entity->getArgument(2); }
bool IfcLightDistributionData::is(Type::Enum v) { return v == Type::IfcLightDistributionData; }
Type::Enum IfcLightDistributionData::type() { return Type::IfcLightDistributionData; }
Type::Enum IfcLightDistributionData::Class() { return Type::IfcLightDistributionData; }
IfcLightDistributionData::IfcLightDistributionData(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightDistributionData)) throw; entity = e; } 
// IfcLightFixtureType
IfcLightFixtureTypeEnum::IfcLightFixtureTypeEnum IfcLightFixtureType::PredefinedType() { return IfcLightFixtureTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcLightFixtureType::is(Type::Enum v) { return v == Type::IfcLightFixtureType || IfcFlowTerminalType::is(v); }
Type::Enum IfcLightFixtureType::type() { return Type::IfcLightFixtureType; }
Type::Enum IfcLightFixtureType::Class() { return Type::IfcLightFixtureType; }
IfcLightFixtureType::IfcLightFixtureType(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightFixtureType)) throw; entity = e; } 
// IfcLightIntensityDistribution
IfcLightDistributionCurveEnum::IfcLightDistributionCurveEnum IfcLightIntensityDistribution::LightDistributionCurve() { return IfcLightDistributionCurveEnum::FromString(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcLightDistributionData> > IfcLightIntensityDistribution::DistributionData() { RETURN_AS_LIST(IfcLightDistributionData,1) }
bool IfcLightIntensityDistribution::is(Type::Enum v) { return v == Type::IfcLightIntensityDistribution; }
Type::Enum IfcLightIntensityDistribution::type() { return Type::IfcLightIntensityDistribution; }
Type::Enum IfcLightIntensityDistribution::Class() { return Type::IfcLightIntensityDistribution; }
IfcLightIntensityDistribution::IfcLightIntensityDistribution(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightIntensityDistribution)) throw; entity = e; } 
// IfcLightSource
bool IfcLightSource::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcLightSource::Name() { return *entity->getArgument(0); }
SHARED_PTR<IfcColourRgb> IfcLightSource::LightColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(1)); }
bool IfcLightSource::hasAmbientIntensity() { return !entity->getArgument(2)->isNull(); }
IfcNormalisedRatioMeasure IfcLightSource::AmbientIntensity() { return *entity->getArgument(2); }
bool IfcLightSource::hasIntensity() { return !entity->getArgument(3)->isNull(); }
IfcNormalisedRatioMeasure IfcLightSource::Intensity() { return *entity->getArgument(3); }
bool IfcLightSource::is(Type::Enum v) { return v == Type::IfcLightSource || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcLightSource::type() { return Type::IfcLightSource; }
Type::Enum IfcLightSource::Class() { return Type::IfcLightSource; }
IfcLightSource::IfcLightSource(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSource)) throw; entity = e; } 
// IfcLightSourceAmbient
bool IfcLightSourceAmbient::is(Type::Enum v) { return v == Type::IfcLightSourceAmbient || IfcLightSource::is(v); }
Type::Enum IfcLightSourceAmbient::type() { return Type::IfcLightSourceAmbient; }
Type::Enum IfcLightSourceAmbient::Class() { return Type::IfcLightSourceAmbient; }
IfcLightSourceAmbient::IfcLightSourceAmbient(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceAmbient)) throw; entity = e; } 
// IfcLightSourceDirectional
SHARED_PTR<IfcDirection> IfcLightSourceDirectional::Orientation() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(4)); }
bool IfcLightSourceDirectional::is(Type::Enum v) { return v == Type::IfcLightSourceDirectional || IfcLightSource::is(v); }
Type::Enum IfcLightSourceDirectional::type() { return Type::IfcLightSourceDirectional; }
Type::Enum IfcLightSourceDirectional::Class() { return Type::IfcLightSourceDirectional; }
IfcLightSourceDirectional::IfcLightSourceDirectional(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceDirectional)) throw; entity = e; } 
// IfcLightSourceGoniometric
SHARED_PTR<IfcAxis2Placement3D> IfcLightSourceGoniometric::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(4)); }
bool IfcLightSourceGoniometric::hasColourAppearance() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR<IfcColourRgb> IfcLightSourceGoniometric::ColourAppearance() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(5)); }
IfcThermodynamicTemperatureMeasure IfcLightSourceGoniometric::ColourTemperature() { return *entity->getArgument(6); }
IfcLuminousFluxMeasure IfcLightSourceGoniometric::LuminousFlux() { return *entity->getArgument(7); }
IfcLightEmissionSourceEnum::IfcLightEmissionSourceEnum IfcLightSourceGoniometric::LightEmissionSource() { return IfcLightEmissionSourceEnum::FromString(*entity->getArgument(8)); }
IfcLightDistributionDataSourceSelect IfcLightSourceGoniometric::LightDistributionDataSource() { return *entity->getArgument(9); }
bool IfcLightSourceGoniometric::is(Type::Enum v) { return v == Type::IfcLightSourceGoniometric || IfcLightSource::is(v); }
Type::Enum IfcLightSourceGoniometric::type() { return Type::IfcLightSourceGoniometric; }
Type::Enum IfcLightSourceGoniometric::Class() { return Type::IfcLightSourceGoniometric; }
IfcLightSourceGoniometric::IfcLightSourceGoniometric(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceGoniometric)) throw; entity = e; } 
// IfcLightSourcePositional
SHARED_PTR<IfcCartesianPoint> IfcLightSourcePositional::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(4)); }
IfcPositiveLengthMeasure IfcLightSourcePositional::Radius() { return *entity->getArgument(5); }
IfcReal IfcLightSourcePositional::ConstantAttenuation() { return *entity->getArgument(6); }
IfcReal IfcLightSourcePositional::DistanceAttenuation() { return *entity->getArgument(7); }
IfcReal IfcLightSourcePositional::QuadricAttenuation() { return *entity->getArgument(8); }
bool IfcLightSourcePositional::is(Type::Enum v) { return v == Type::IfcLightSourcePositional || IfcLightSource::is(v); }
Type::Enum IfcLightSourcePositional::type() { return Type::IfcLightSourcePositional; }
Type::Enum IfcLightSourcePositional::Class() { return Type::IfcLightSourcePositional; }
IfcLightSourcePositional::IfcLightSourcePositional(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourcePositional)) throw; entity = e; } 
// IfcLightSourceSpot
SHARED_PTR<IfcDirection> IfcLightSourceSpot::Orientation() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(9)); }
bool IfcLightSourceSpot::hasConcentrationExponent() { return !entity->getArgument(10)->isNull(); }
IfcReal IfcLightSourceSpot::ConcentrationExponent() { return *entity->getArgument(10); }
IfcPositivePlaneAngleMeasure IfcLightSourceSpot::SpreadAngle() { return *entity->getArgument(11); }
IfcPositivePlaneAngleMeasure IfcLightSourceSpot::BeamWidthAngle() { return *entity->getArgument(12); }
bool IfcLightSourceSpot::is(Type::Enum v) { return v == Type::IfcLightSourceSpot || IfcLightSourcePositional::is(v); }
Type::Enum IfcLightSourceSpot::type() { return Type::IfcLightSourceSpot; }
Type::Enum IfcLightSourceSpot::Class() { return Type::IfcLightSourceSpot; }
IfcLightSourceSpot::IfcLightSourceSpot(IfcAbstractEntityPtr e) { if (!is(Type::IfcLightSourceSpot)) throw; entity = e; } 
// IfcLine
SHARED_PTR<IfcCartesianPoint> IfcLine::Pnt() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(0)); }
SHARED_PTR<IfcVector> IfcLine::Dir() { return reinterpret_pointer_cast<IfcBaseClass,IfcVector>(*entity->getArgument(1)); }
bool IfcLine::is(Type::Enum v) { return v == Type::IfcLine || IfcCurve::is(v); }
Type::Enum IfcLine::type() { return Type::IfcLine; }
Type::Enum IfcLine::Class() { return Type::IfcLine; }
IfcLine::IfcLine(IfcAbstractEntityPtr e) { if (!is(Type::IfcLine)) throw; entity = e; } 
// IfcLinearDimension
bool IfcLinearDimension::is(Type::Enum v) { return v == Type::IfcLinearDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcLinearDimension::type() { return Type::IfcLinearDimension; }
Type::Enum IfcLinearDimension::Class() { return Type::IfcLinearDimension; }
IfcLinearDimension::IfcLinearDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcLinearDimension)) throw; entity = e; } 
// IfcLocalPlacement
bool IfcLocalPlacement::hasPlacementRelTo() { return !entity->getArgument(0)->isNull(); }
SHARED_PTR<IfcObjectPlacement> IfcLocalPlacement::PlacementRelTo() { return reinterpret_pointer_cast<IfcBaseClass,IfcObjectPlacement>(*entity->getArgument(0)); }
IfcAxis2Placement IfcLocalPlacement::RelativePlacement() { return *entity->getArgument(1); }
bool IfcLocalPlacement::is(Type::Enum v) { return v == Type::IfcLocalPlacement || IfcObjectPlacement::is(v); }
Type::Enum IfcLocalPlacement::type() { return Type::IfcLocalPlacement; }
Type::Enum IfcLocalPlacement::Class() { return Type::IfcLocalPlacement; }
IfcLocalPlacement::IfcLocalPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcLocalPlacement)) throw; entity = e; } 
// IfcLocalTime
IfcHourInDay IfcLocalTime::HourComponent() { return *entity->getArgument(0); }
bool IfcLocalTime::hasMinuteComponent() { return !entity->getArgument(1)->isNull(); }
IfcMinuteInHour IfcLocalTime::MinuteComponent() { return *entity->getArgument(1); }
bool IfcLocalTime::hasSecondComponent() { return !entity->getArgument(2)->isNull(); }
IfcSecondInMinute IfcLocalTime::SecondComponent() { return *entity->getArgument(2); }
bool IfcLocalTime::hasZone() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcCoordinatedUniversalTimeOffset> IfcLocalTime::Zone() { return reinterpret_pointer_cast<IfcBaseClass,IfcCoordinatedUniversalTimeOffset>(*entity->getArgument(3)); }
bool IfcLocalTime::hasDaylightSavingOffset() { return !entity->getArgument(4)->isNull(); }
IfcDaylightSavingHour IfcLocalTime::DaylightSavingOffset() { return *entity->getArgument(4); }
bool IfcLocalTime::is(Type::Enum v) { return v == Type::IfcLocalTime; }
Type::Enum IfcLocalTime::type() { return Type::IfcLocalTime; }
Type::Enum IfcLocalTime::Class() { return Type::IfcLocalTime; }
IfcLocalTime::IfcLocalTime(IfcAbstractEntityPtr e) { if (!is(Type::IfcLocalTime)) throw; entity = e; } 
// IfcLoop
bool IfcLoop::is(Type::Enum v) { return v == Type::IfcLoop || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcLoop::type() { return Type::IfcLoop; }
Type::Enum IfcLoop::Class() { return Type::IfcLoop; }
IfcLoop::IfcLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcLoop)) throw; entity = e; } 
// IfcManifoldSolidBrep
SHARED_PTR<IfcClosedShell> IfcManifoldSolidBrep::Outer() { return reinterpret_pointer_cast<IfcBaseClass,IfcClosedShell>(*entity->getArgument(0)); }
bool IfcManifoldSolidBrep::is(Type::Enum v) { return v == Type::IfcManifoldSolidBrep || IfcSolidModel::is(v); }
Type::Enum IfcManifoldSolidBrep::type() { return Type::IfcManifoldSolidBrep; }
Type::Enum IfcManifoldSolidBrep::Class() { return Type::IfcManifoldSolidBrep; }
IfcManifoldSolidBrep::IfcManifoldSolidBrep(IfcAbstractEntityPtr e) { if (!is(Type::IfcManifoldSolidBrep)) throw; entity = e; } 
// IfcMappedItem
SHARED_PTR<IfcRepresentationMap> IfcMappedItem::MappingSource() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentationMap>(*entity->getArgument(0)); }
SHARED_PTR<IfcCartesianTransformationOperator> IfcMappedItem::MappingTarget() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator>(*entity->getArgument(1)); }
bool IfcMappedItem::is(Type::Enum v) { return v == Type::IfcMappedItem || IfcRepresentationItem::is(v); }
Type::Enum IfcMappedItem::type() { return Type::IfcMappedItem; }
Type::Enum IfcMappedItem::Class() { return Type::IfcMappedItem; }
IfcMappedItem::IfcMappedItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcMappedItem)) throw; entity = e; } 
// IfcMaterial
IfcLabel IfcMaterial::Name() { return *entity->getArgument(0); }
IfcMaterialDefinitionRepresentation::list IfcMaterial::HasRepresentation() { RETURN_INVERSE(IfcMaterialDefinitionRepresentation) }
IfcMaterialClassificationRelationship::list IfcMaterial::ClassifiedAs() { RETURN_INVERSE(IfcMaterialClassificationRelationship) }
bool IfcMaterial::is(Type::Enum v) { return v == Type::IfcMaterial; }
Type::Enum IfcMaterial::type() { return Type::IfcMaterial; }
Type::Enum IfcMaterial::Class() { return Type::IfcMaterial; }
IfcMaterial::IfcMaterial(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterial)) throw; entity = e; } 
// IfcMaterialClassificationRelationship
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcMaterialClassificationRelationship::MaterialClassifications() { RETURN_AS_LIST(IfcAbstractSelect,0) }
SHARED_PTR<IfcMaterial> IfcMaterialClassificationRelationship::ClassifiedMaterial() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(1)); }
bool IfcMaterialClassificationRelationship::is(Type::Enum v) { return v == Type::IfcMaterialClassificationRelationship; }
Type::Enum IfcMaterialClassificationRelationship::type() { return Type::IfcMaterialClassificationRelationship; }
Type::Enum IfcMaterialClassificationRelationship::Class() { return Type::IfcMaterialClassificationRelationship; }
IfcMaterialClassificationRelationship::IfcMaterialClassificationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialClassificationRelationship)) throw; entity = e; } 
// IfcMaterialDefinitionRepresentation
SHARED_PTR<IfcMaterial> IfcMaterialDefinitionRepresentation::RepresentedMaterial() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(3)); }
bool IfcMaterialDefinitionRepresentation::is(Type::Enum v) { return v == Type::IfcMaterialDefinitionRepresentation || IfcProductRepresentation::is(v); }
Type::Enum IfcMaterialDefinitionRepresentation::type() { return Type::IfcMaterialDefinitionRepresentation; }
Type::Enum IfcMaterialDefinitionRepresentation::Class() { return Type::IfcMaterialDefinitionRepresentation; }
IfcMaterialDefinitionRepresentation::IfcMaterialDefinitionRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialDefinitionRepresentation)) throw; entity = e; } 
// IfcMaterialLayer
bool IfcMaterialLayer::hasMaterial() { return !entity->getArgument(0)->isNull(); }
SHARED_PTR<IfcMaterial> IfcMaterialLayer::Material() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(0)); }
IfcPositiveLengthMeasure IfcMaterialLayer::LayerThickness() { return *entity->getArgument(1); }
bool IfcMaterialLayer::hasIsVentilated() { return !entity->getArgument(2)->isNull(); }
IfcLogical IfcMaterialLayer::IsVentilated() { return *entity->getArgument(2); }
IfcMaterialLayerSet::list IfcMaterialLayer::ToMaterialLayerSet() { RETURN_INVERSE(IfcMaterialLayerSet) }
bool IfcMaterialLayer::is(Type::Enum v) { return v == Type::IfcMaterialLayer; }
Type::Enum IfcMaterialLayer::type() { return Type::IfcMaterialLayer; }
Type::Enum IfcMaterialLayer::Class() { return Type::IfcMaterialLayer; }
IfcMaterialLayer::IfcMaterialLayer(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialLayer)) throw; entity = e; } 
// IfcMaterialLayerSet
SHARED_PTR< IfcTemplatedEntityList<IfcMaterialLayer> > IfcMaterialLayerSet::MaterialLayers() { RETURN_AS_LIST(IfcMaterialLayer,0) }
bool IfcMaterialLayerSet::hasLayerSetName() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcMaterialLayerSet::LayerSetName() { return *entity->getArgument(1); }
bool IfcMaterialLayerSet::is(Type::Enum v) { return v == Type::IfcMaterialLayerSet; }
Type::Enum IfcMaterialLayerSet::type() { return Type::IfcMaterialLayerSet; }
Type::Enum IfcMaterialLayerSet::Class() { return Type::IfcMaterialLayerSet; }
IfcMaterialLayerSet::IfcMaterialLayerSet(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialLayerSet)) throw; entity = e; } 
// IfcMaterialLayerSetUsage
SHARED_PTR<IfcMaterialLayerSet> IfcMaterialLayerSetUsage::ForLayerSet() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterialLayerSet>(*entity->getArgument(0)); }
IfcLayerSetDirectionEnum::IfcLayerSetDirectionEnum IfcMaterialLayerSetUsage::LayerSetDirection() { return IfcLayerSetDirectionEnum::FromString(*entity->getArgument(1)); }
IfcDirectionSenseEnum::IfcDirectionSenseEnum IfcMaterialLayerSetUsage::DirectionSense() { return IfcDirectionSenseEnum::FromString(*entity->getArgument(2)); }
IfcLengthMeasure IfcMaterialLayerSetUsage::OffsetFromReferenceLine() { return *entity->getArgument(3); }
bool IfcMaterialLayerSetUsage::is(Type::Enum v) { return v == Type::IfcMaterialLayerSetUsage; }
Type::Enum IfcMaterialLayerSetUsage::type() { return Type::IfcMaterialLayerSetUsage; }
Type::Enum IfcMaterialLayerSetUsage::Class() { return Type::IfcMaterialLayerSetUsage; }
IfcMaterialLayerSetUsage::IfcMaterialLayerSetUsage(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialLayerSetUsage)) throw; entity = e; } 
// IfcMaterialList
SHARED_PTR< IfcTemplatedEntityList<IfcMaterial> > IfcMaterialList::Materials() { RETURN_AS_LIST(IfcMaterial,0) }
bool IfcMaterialList::is(Type::Enum v) { return v == Type::IfcMaterialList; }
Type::Enum IfcMaterialList::type() { return Type::IfcMaterialList; }
Type::Enum IfcMaterialList::Class() { return Type::IfcMaterialList; }
IfcMaterialList::IfcMaterialList(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialList)) throw; entity = e; } 
// IfcMaterialProperties
SHARED_PTR<IfcMaterial> IfcMaterialProperties::Material() { return reinterpret_pointer_cast<IfcBaseClass,IfcMaterial>(*entity->getArgument(0)); }
bool IfcMaterialProperties::is(Type::Enum v) { return v == Type::IfcMaterialProperties; }
Type::Enum IfcMaterialProperties::type() { return Type::IfcMaterialProperties; }
Type::Enum IfcMaterialProperties::Class() { return Type::IfcMaterialProperties; }
IfcMaterialProperties::IfcMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMaterialProperties)) throw; entity = e; } 
// IfcMeasureWithUnit
IfcValue IfcMeasureWithUnit::ValueComponent() { return *entity->getArgument(0); }
IfcUnit IfcMeasureWithUnit::UnitComponent() { return *entity->getArgument(1); }
bool IfcMeasureWithUnit::is(Type::Enum v) { return v == Type::IfcMeasureWithUnit; }
Type::Enum IfcMeasureWithUnit::type() { return Type::IfcMeasureWithUnit; }
Type::Enum IfcMeasureWithUnit::Class() { return Type::IfcMeasureWithUnit; }
IfcMeasureWithUnit::IfcMeasureWithUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcMeasureWithUnit)) throw; entity = e; } 
// IfcMechanicalConcreteMaterialProperties
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
bool IfcMechanicalConcreteMaterialProperties::is(Type::Enum v) { return v == Type::IfcMechanicalConcreteMaterialProperties || IfcMechanicalMaterialProperties::is(v); }
Type::Enum IfcMechanicalConcreteMaterialProperties::type() { return Type::IfcMechanicalConcreteMaterialProperties; }
Type::Enum IfcMechanicalConcreteMaterialProperties::Class() { return Type::IfcMechanicalConcreteMaterialProperties; }
IfcMechanicalConcreteMaterialProperties::IfcMechanicalConcreteMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalConcreteMaterialProperties)) throw; entity = e; } 
// IfcMechanicalFastener
bool IfcMechanicalFastener::hasNominalDiameter() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcMechanicalFastener::NominalDiameter() { return *entity->getArgument(8); }
bool IfcMechanicalFastener::hasNominalLength() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcMechanicalFastener::NominalLength() { return *entity->getArgument(9); }
bool IfcMechanicalFastener::is(Type::Enum v) { return v == Type::IfcMechanicalFastener || IfcFastener::is(v); }
Type::Enum IfcMechanicalFastener::type() { return Type::IfcMechanicalFastener; }
Type::Enum IfcMechanicalFastener::Class() { return Type::IfcMechanicalFastener; }
IfcMechanicalFastener::IfcMechanicalFastener(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalFastener)) throw; entity = e; } 
// IfcMechanicalFastenerType
bool IfcMechanicalFastenerType::is(Type::Enum v) { return v == Type::IfcMechanicalFastenerType || IfcFastenerType::is(v); }
Type::Enum IfcMechanicalFastenerType::type() { return Type::IfcMechanicalFastenerType; }
Type::Enum IfcMechanicalFastenerType::Class() { return Type::IfcMechanicalFastenerType; }
IfcMechanicalFastenerType::IfcMechanicalFastenerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalFastenerType)) throw; entity = e; } 
// IfcMechanicalMaterialProperties
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
bool IfcMechanicalMaterialProperties::is(Type::Enum v) { return v == Type::IfcMechanicalMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcMechanicalMaterialProperties::type() { return Type::IfcMechanicalMaterialProperties; }
Type::Enum IfcMechanicalMaterialProperties::Class() { return Type::IfcMechanicalMaterialProperties; }
IfcMechanicalMaterialProperties::IfcMechanicalMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalMaterialProperties)) throw; entity = e; } 
// IfcMechanicalSteelMaterialProperties
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
bool IfcMechanicalSteelMaterialProperties::is(Type::Enum v) { return v == Type::IfcMechanicalSteelMaterialProperties || IfcMechanicalMaterialProperties::is(v); }
Type::Enum IfcMechanicalSteelMaterialProperties::type() { return Type::IfcMechanicalSteelMaterialProperties; }
Type::Enum IfcMechanicalSteelMaterialProperties::Class() { return Type::IfcMechanicalSteelMaterialProperties; }
IfcMechanicalSteelMaterialProperties::IfcMechanicalSteelMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcMechanicalSteelMaterialProperties)) throw; entity = e; } 
// IfcMember
bool IfcMember::is(Type::Enum v) { return v == Type::IfcMember || IfcBuildingElement::is(v); }
Type::Enum IfcMember::type() { return Type::IfcMember; }
Type::Enum IfcMember::Class() { return Type::IfcMember; }
IfcMember::IfcMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcMember)) throw; entity = e; } 
// IfcMemberType
IfcMemberTypeEnum::IfcMemberTypeEnum IfcMemberType::PredefinedType() { return IfcMemberTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcMemberType::is(Type::Enum v) { return v == Type::IfcMemberType || IfcBuildingElementType::is(v); }
Type::Enum IfcMemberType::type() { return Type::IfcMemberType; }
Type::Enum IfcMemberType::Class() { return Type::IfcMemberType; }
IfcMemberType::IfcMemberType(IfcAbstractEntityPtr e) { if (!is(Type::IfcMemberType)) throw; entity = e; } 
// IfcMetric
IfcBenchmarkEnum::IfcBenchmarkEnum IfcMetric::Benchmark() { return IfcBenchmarkEnum::FromString(*entity->getArgument(7)); }
bool IfcMetric::hasValueSource() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcMetric::ValueSource() { return *entity->getArgument(8); }
IfcMetricValueSelect IfcMetric::DataValue() { return *entity->getArgument(9); }
bool IfcMetric::is(Type::Enum v) { return v == Type::IfcMetric || IfcConstraint::is(v); }
Type::Enum IfcMetric::type() { return Type::IfcMetric; }
Type::Enum IfcMetric::Class() { return Type::IfcMetric; }
IfcMetric::IfcMetric(IfcAbstractEntityPtr e) { if (!is(Type::IfcMetric)) throw; entity = e; } 
// IfcMonetaryUnit
IfcCurrencyEnum::IfcCurrencyEnum IfcMonetaryUnit::Currency() { return IfcCurrencyEnum::FromString(*entity->getArgument(0)); }
bool IfcMonetaryUnit::is(Type::Enum v) { return v == Type::IfcMonetaryUnit; }
Type::Enum IfcMonetaryUnit::type() { return Type::IfcMonetaryUnit; }
Type::Enum IfcMonetaryUnit::Class() { return Type::IfcMonetaryUnit; }
IfcMonetaryUnit::IfcMonetaryUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcMonetaryUnit)) throw; entity = e; } 
// IfcMotorConnectionType
IfcMotorConnectionTypeEnum::IfcMotorConnectionTypeEnum IfcMotorConnectionType::PredefinedType() { return IfcMotorConnectionTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcMotorConnectionType::is(Type::Enum v) { return v == Type::IfcMotorConnectionType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcMotorConnectionType::type() { return Type::IfcMotorConnectionType; }
Type::Enum IfcMotorConnectionType::Class() { return Type::IfcMotorConnectionType; }
IfcMotorConnectionType::IfcMotorConnectionType(IfcAbstractEntityPtr e) { if (!is(Type::IfcMotorConnectionType)) throw; entity = e; } 
// IfcMove
SHARED_PTR<IfcSpatialStructureElement> IfcMove::MoveFrom() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(10)); }
SHARED_PTR<IfcSpatialStructureElement> IfcMove::MoveTo() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(11)); }
bool IfcMove::hasPunchList() { return !entity->getArgument(12)->isNull(); }
std::vector<IfcText> /*[1:?]*/ IfcMove::PunchList() { return *entity->getArgument(12); }
bool IfcMove::is(Type::Enum v) { return v == Type::IfcMove || IfcTask::is(v); }
Type::Enum IfcMove::type() { return Type::IfcMove; }
Type::Enum IfcMove::Class() { return Type::IfcMove; }
IfcMove::IfcMove(IfcAbstractEntityPtr e) { if (!is(Type::IfcMove)) throw; entity = e; } 
// IfcNamedUnit
SHARED_PTR<IfcDimensionalExponents> IfcNamedUnit::Dimensions() { return reinterpret_pointer_cast<IfcBaseClass,IfcDimensionalExponents>(*entity->getArgument(0)); }
IfcUnitEnum::IfcUnitEnum IfcNamedUnit::UnitType() { return IfcUnitEnum::FromString(*entity->getArgument(1)); }
bool IfcNamedUnit::is(Type::Enum v) { return v == Type::IfcNamedUnit; }
Type::Enum IfcNamedUnit::type() { return Type::IfcNamedUnit; }
Type::Enum IfcNamedUnit::Class() { return Type::IfcNamedUnit; }
IfcNamedUnit::IfcNamedUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcNamedUnit)) throw; entity = e; } 
// IfcObject
bool IfcObject::hasObjectType() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcObject::ObjectType() { return *entity->getArgument(4); }
IfcRelDefines::list IfcObject::IsDefinedBy() { RETURN_INVERSE(IfcRelDefines) }
bool IfcObject::is(Type::Enum v) { return v == Type::IfcObject || IfcObjectDefinition::is(v); }
Type::Enum IfcObject::type() { return Type::IfcObject; }
Type::Enum IfcObject::Class() { return Type::IfcObject; }
IfcObject::IfcObject(IfcAbstractEntityPtr e) { if (!is(Type::IfcObject)) throw; entity = e; } 
// IfcObjectDefinition
IfcRelAssigns::list IfcObjectDefinition::HasAssignments() { RETURN_INVERSE(IfcRelAssigns) }
IfcRelDecomposes::list IfcObjectDefinition::IsDecomposedBy() { RETURN_INVERSE(IfcRelDecomposes) }
IfcRelDecomposes::list IfcObjectDefinition::Decomposes() { RETURN_INVERSE(IfcRelDecomposes) }
IfcRelAssociates::list IfcObjectDefinition::HasAssociations() { RETURN_INVERSE(IfcRelAssociates) }
bool IfcObjectDefinition::is(Type::Enum v) { return v == Type::IfcObjectDefinition || IfcRoot::is(v); }
Type::Enum IfcObjectDefinition::type() { return Type::IfcObjectDefinition; }
Type::Enum IfcObjectDefinition::Class() { return Type::IfcObjectDefinition; }
IfcObjectDefinition::IfcObjectDefinition(IfcAbstractEntityPtr e) { if (!is(Type::IfcObjectDefinition)) throw; entity = e; } 
// IfcObjectPlacement
IfcProduct::list IfcObjectPlacement::PlacesObject() { RETURN_INVERSE(IfcProduct) }
IfcLocalPlacement::list IfcObjectPlacement::ReferencedByPlacements() { RETURN_INVERSE(IfcLocalPlacement) }
bool IfcObjectPlacement::is(Type::Enum v) { return v == Type::IfcObjectPlacement; }
Type::Enum IfcObjectPlacement::type() { return Type::IfcObjectPlacement; }
Type::Enum IfcObjectPlacement::Class() { return Type::IfcObjectPlacement; }
IfcObjectPlacement::IfcObjectPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcObjectPlacement)) throw; entity = e; } 
// IfcObjective
bool IfcObjective::hasBenchmarkValues() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR<IfcMetric> IfcObjective::BenchmarkValues() { return reinterpret_pointer_cast<IfcBaseClass,IfcMetric>(*entity->getArgument(7)); }
bool IfcObjective::hasResultValues() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR<IfcMetric> IfcObjective::ResultValues() { return reinterpret_pointer_cast<IfcBaseClass,IfcMetric>(*entity->getArgument(8)); }
IfcObjectiveEnum::IfcObjectiveEnum IfcObjective::ObjectiveQualifier() { return IfcObjectiveEnum::FromString(*entity->getArgument(9)); }
bool IfcObjective::hasUserDefinedQualifier() { return !entity->getArgument(10)->isNull(); }
IfcLabel IfcObjective::UserDefinedQualifier() { return *entity->getArgument(10); }
bool IfcObjective::is(Type::Enum v) { return v == Type::IfcObjective || IfcConstraint::is(v); }
Type::Enum IfcObjective::type() { return Type::IfcObjective; }
Type::Enum IfcObjective::Class() { return Type::IfcObjective; }
IfcObjective::IfcObjective(IfcAbstractEntityPtr e) { if (!is(Type::IfcObjective)) throw; entity = e; } 
// IfcOccupant
IfcOccupantTypeEnum::IfcOccupantTypeEnum IfcOccupant::PredefinedType() { return IfcOccupantTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcOccupant::is(Type::Enum v) { return v == Type::IfcOccupant || IfcActor::is(v); }
Type::Enum IfcOccupant::type() { return Type::IfcOccupant; }
Type::Enum IfcOccupant::Class() { return Type::IfcOccupant; }
IfcOccupant::IfcOccupant(IfcAbstractEntityPtr e) { if (!is(Type::IfcOccupant)) throw; entity = e; } 
// IfcOffsetCurve2D
SHARED_PTR<IfcCurve> IfcOffsetCurve2D::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcLengthMeasure IfcOffsetCurve2D::Distance() { return *entity->getArgument(1); }
bool IfcOffsetCurve2D::SelfIntersect() { return *entity->getArgument(2); }
bool IfcOffsetCurve2D::is(Type::Enum v) { return v == Type::IfcOffsetCurve2D || IfcCurve::is(v); }
Type::Enum IfcOffsetCurve2D::type() { return Type::IfcOffsetCurve2D; }
Type::Enum IfcOffsetCurve2D::Class() { return Type::IfcOffsetCurve2D; }
IfcOffsetCurve2D::IfcOffsetCurve2D(IfcAbstractEntityPtr e) { if (!is(Type::IfcOffsetCurve2D)) throw; entity = e; } 
// IfcOffsetCurve3D
SHARED_PTR<IfcCurve> IfcOffsetCurve3D::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcLengthMeasure IfcOffsetCurve3D::Distance() { return *entity->getArgument(1); }
bool IfcOffsetCurve3D::SelfIntersect() { return *entity->getArgument(2); }
SHARED_PTR<IfcDirection> IfcOffsetCurve3D::RefDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(3)); }
bool IfcOffsetCurve3D::is(Type::Enum v) { return v == Type::IfcOffsetCurve3D || IfcCurve::is(v); }
Type::Enum IfcOffsetCurve3D::type() { return Type::IfcOffsetCurve3D; }
Type::Enum IfcOffsetCurve3D::Class() { return Type::IfcOffsetCurve3D; }
IfcOffsetCurve3D::IfcOffsetCurve3D(IfcAbstractEntityPtr e) { if (!is(Type::IfcOffsetCurve3D)) throw; entity = e; } 
// IfcOneDirectionRepeatFactor
SHARED_PTR<IfcVector> IfcOneDirectionRepeatFactor::RepeatFactor() { return reinterpret_pointer_cast<IfcBaseClass,IfcVector>(*entity->getArgument(0)); }
bool IfcOneDirectionRepeatFactor::is(Type::Enum v) { return v == Type::IfcOneDirectionRepeatFactor || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcOneDirectionRepeatFactor::type() { return Type::IfcOneDirectionRepeatFactor; }
Type::Enum IfcOneDirectionRepeatFactor::Class() { return Type::IfcOneDirectionRepeatFactor; }
IfcOneDirectionRepeatFactor::IfcOneDirectionRepeatFactor(IfcAbstractEntityPtr e) { if (!is(Type::IfcOneDirectionRepeatFactor)) throw; entity = e; } 
// IfcOpenShell
bool IfcOpenShell::is(Type::Enum v) { return v == Type::IfcOpenShell || IfcConnectedFaceSet::is(v); }
Type::Enum IfcOpenShell::type() { return Type::IfcOpenShell; }
Type::Enum IfcOpenShell::Class() { return Type::IfcOpenShell; }
IfcOpenShell::IfcOpenShell(IfcAbstractEntityPtr e) { if (!is(Type::IfcOpenShell)) throw; entity = e; } 
// IfcOpeningElement
IfcRelFillsElement::list IfcOpeningElement::HasFillings() { RETURN_INVERSE(IfcRelFillsElement) }
bool IfcOpeningElement::is(Type::Enum v) { return v == Type::IfcOpeningElement || IfcFeatureElementSubtraction::is(v); }
Type::Enum IfcOpeningElement::type() { return Type::IfcOpeningElement; }
Type::Enum IfcOpeningElement::Class() { return Type::IfcOpeningElement; }
IfcOpeningElement::IfcOpeningElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcOpeningElement)) throw; entity = e; } 
// IfcOpticalMaterialProperties
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
bool IfcOpticalMaterialProperties::is(Type::Enum v) { return v == Type::IfcOpticalMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcOpticalMaterialProperties::type() { return Type::IfcOpticalMaterialProperties; }
Type::Enum IfcOpticalMaterialProperties::Class() { return Type::IfcOpticalMaterialProperties; }
IfcOpticalMaterialProperties::IfcOpticalMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcOpticalMaterialProperties)) throw; entity = e; } 
// IfcOrderAction
IfcIdentifier IfcOrderAction::ActionID() { return *entity->getArgument(10); }
bool IfcOrderAction::is(Type::Enum v) { return v == Type::IfcOrderAction || IfcTask::is(v); }
Type::Enum IfcOrderAction::type() { return Type::IfcOrderAction; }
Type::Enum IfcOrderAction::Class() { return Type::IfcOrderAction; }
IfcOrderAction::IfcOrderAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrderAction)) throw; entity = e; } 
// IfcOrganization
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
bool IfcOrganization::is(Type::Enum v) { return v == Type::IfcOrganization; }
Type::Enum IfcOrganization::type() { return Type::IfcOrganization; }
Type::Enum IfcOrganization::Class() { return Type::IfcOrganization; }
IfcOrganization::IfcOrganization(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrganization)) throw; entity = e; } 
// IfcOrganizationRelationship
IfcLabel IfcOrganizationRelationship::Name() { return *entity->getArgument(0); }
bool IfcOrganizationRelationship::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcOrganizationRelationship::Description() { return *entity->getArgument(1); }
SHARED_PTR<IfcOrganization> IfcOrganizationRelationship::RelatingOrganization() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(2)); }
SHARED_PTR< IfcTemplatedEntityList<IfcOrganization> > IfcOrganizationRelationship::RelatedOrganizations() { RETURN_AS_LIST(IfcOrganization,3) }
bool IfcOrganizationRelationship::is(Type::Enum v) { return v == Type::IfcOrganizationRelationship; }
Type::Enum IfcOrganizationRelationship::type() { return Type::IfcOrganizationRelationship; }
Type::Enum IfcOrganizationRelationship::Class() { return Type::IfcOrganizationRelationship; }
IfcOrganizationRelationship::IfcOrganizationRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrganizationRelationship)) throw; entity = e; } 
// IfcOrientedEdge
SHARED_PTR<IfcEdge> IfcOrientedEdge::EdgeElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcEdge>(*entity->getArgument(2)); }
bool IfcOrientedEdge::Orientation() { return *entity->getArgument(3); }
bool IfcOrientedEdge::is(Type::Enum v) { return v == Type::IfcOrientedEdge || IfcEdge::is(v); }
Type::Enum IfcOrientedEdge::type() { return Type::IfcOrientedEdge; }
Type::Enum IfcOrientedEdge::Class() { return Type::IfcOrientedEdge; }
IfcOrientedEdge::IfcOrientedEdge(IfcAbstractEntityPtr e) { if (!is(Type::IfcOrientedEdge)) throw; entity = e; } 
// IfcOutletType
IfcOutletTypeEnum::IfcOutletTypeEnum IfcOutletType::PredefinedType() { return IfcOutletTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcOutletType::is(Type::Enum v) { return v == Type::IfcOutletType || IfcFlowTerminalType::is(v); }
Type::Enum IfcOutletType::type() { return Type::IfcOutletType; }
Type::Enum IfcOutletType::Class() { return Type::IfcOutletType; }
IfcOutletType::IfcOutletType(IfcAbstractEntityPtr e) { if (!is(Type::IfcOutletType)) throw; entity = e; } 
// IfcOwnerHistory
SHARED_PTR<IfcPersonAndOrganization> IfcOwnerHistory::OwningUser() { return reinterpret_pointer_cast<IfcBaseClass,IfcPersonAndOrganization>(*entity->getArgument(0)); }
SHARED_PTR<IfcApplication> IfcOwnerHistory::OwningApplication() { return reinterpret_pointer_cast<IfcBaseClass,IfcApplication>(*entity->getArgument(1)); }
bool IfcOwnerHistory::hasState() { return !entity->getArgument(2)->isNull(); }
IfcStateEnum::IfcStateEnum IfcOwnerHistory::State() { return IfcStateEnum::FromString(*entity->getArgument(2)); }
IfcChangeActionEnum::IfcChangeActionEnum IfcOwnerHistory::ChangeAction() { return IfcChangeActionEnum::FromString(*entity->getArgument(3)); }
bool IfcOwnerHistory::hasLastModifiedDate() { return !entity->getArgument(4)->isNull(); }
IfcTimeStamp IfcOwnerHistory::LastModifiedDate() { return *entity->getArgument(4); }
bool IfcOwnerHistory::hasLastModifyingUser() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR<IfcPersonAndOrganization> IfcOwnerHistory::LastModifyingUser() { return reinterpret_pointer_cast<IfcBaseClass,IfcPersonAndOrganization>(*entity->getArgument(5)); }
bool IfcOwnerHistory::hasLastModifyingApplication() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcApplication> IfcOwnerHistory::LastModifyingApplication() { return reinterpret_pointer_cast<IfcBaseClass,IfcApplication>(*entity->getArgument(6)); }
IfcTimeStamp IfcOwnerHistory::CreationDate() { return *entity->getArgument(7); }
bool IfcOwnerHistory::is(Type::Enum v) { return v == Type::IfcOwnerHistory; }
Type::Enum IfcOwnerHistory::type() { return Type::IfcOwnerHistory; }
Type::Enum IfcOwnerHistory::Class() { return Type::IfcOwnerHistory; }
IfcOwnerHistory::IfcOwnerHistory(IfcAbstractEntityPtr e) { if (!is(Type::IfcOwnerHistory)) throw; entity = e; } 
// IfcParameterizedProfileDef
SHARED_PTR<IfcAxis2Placement2D> IfcParameterizedProfileDef::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement2D>(*entity->getArgument(2)); }
bool IfcParameterizedProfileDef::is(Type::Enum v) { return v == Type::IfcParameterizedProfileDef || IfcProfileDef::is(v); }
Type::Enum IfcParameterizedProfileDef::type() { return Type::IfcParameterizedProfileDef; }
Type::Enum IfcParameterizedProfileDef::Class() { return Type::IfcParameterizedProfileDef; }
IfcParameterizedProfileDef::IfcParameterizedProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcParameterizedProfileDef)) throw; entity = e; } 
// IfcPath
SHARED_PTR< IfcTemplatedEntityList<IfcOrientedEdge> > IfcPath::EdgeList() { RETURN_AS_LIST(IfcOrientedEdge,0) }
bool IfcPath::is(Type::Enum v) { return v == Type::IfcPath || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcPath::type() { return Type::IfcPath; }
Type::Enum IfcPath::Class() { return Type::IfcPath; }
IfcPath::IfcPath(IfcAbstractEntityPtr e) { if (!is(Type::IfcPath)) throw; entity = e; } 
// IfcPerformanceHistory
IfcLabel IfcPerformanceHistory::LifeCyclePhase() { return *entity->getArgument(5); }
bool IfcPerformanceHistory::is(Type::Enum v) { return v == Type::IfcPerformanceHistory || IfcControl::is(v); }
Type::Enum IfcPerformanceHistory::type() { return Type::IfcPerformanceHistory; }
Type::Enum IfcPerformanceHistory::Class() { return Type::IfcPerformanceHistory; }
IfcPerformanceHistory::IfcPerformanceHistory(IfcAbstractEntityPtr e) { if (!is(Type::IfcPerformanceHistory)) throw; entity = e; } 
// IfcPermeableCoveringProperties
IfcPermeableCoveringOperationEnum::IfcPermeableCoveringOperationEnum IfcPermeableCoveringProperties::OperationType() { return IfcPermeableCoveringOperationEnum::FromString(*entity->getArgument(4)); }
IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum IfcPermeableCoveringProperties::PanelPosition() { return IfcWindowPanelPositionEnum::FromString(*entity->getArgument(5)); }
bool IfcPermeableCoveringProperties::hasFrameDepth() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcPermeableCoveringProperties::FrameDepth() { return *entity->getArgument(6); }
bool IfcPermeableCoveringProperties::hasFrameThickness() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcPermeableCoveringProperties::FrameThickness() { return *entity->getArgument(7); }
bool IfcPermeableCoveringProperties::hasShapeAspectStyle() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR<IfcShapeAspect> IfcPermeableCoveringProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(8)); }
bool IfcPermeableCoveringProperties::is(Type::Enum v) { return v == Type::IfcPermeableCoveringProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcPermeableCoveringProperties::type() { return Type::IfcPermeableCoveringProperties; }
Type::Enum IfcPermeableCoveringProperties::Class() { return Type::IfcPermeableCoveringProperties; }
IfcPermeableCoveringProperties::IfcPermeableCoveringProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcPermeableCoveringProperties)) throw; entity = e; } 
// IfcPermit
IfcIdentifier IfcPermit::PermitID() { return *entity->getArgument(5); }
bool IfcPermit::is(Type::Enum v) { return v == Type::IfcPermit || IfcControl::is(v); }
Type::Enum IfcPermit::type() { return Type::IfcPermit; }
Type::Enum IfcPermit::Class() { return Type::IfcPermit; }
IfcPermit::IfcPermit(IfcAbstractEntityPtr e) { if (!is(Type::IfcPermit)) throw; entity = e; } 
// IfcPerson
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
bool IfcPerson::is(Type::Enum v) { return v == Type::IfcPerson; }
Type::Enum IfcPerson::type() { return Type::IfcPerson; }
Type::Enum IfcPerson::Class() { return Type::IfcPerson; }
IfcPerson::IfcPerson(IfcAbstractEntityPtr e) { if (!is(Type::IfcPerson)) throw; entity = e; } 
// IfcPersonAndOrganization
SHARED_PTR<IfcPerson> IfcPersonAndOrganization::ThePerson() { return reinterpret_pointer_cast<IfcBaseClass,IfcPerson>(*entity->getArgument(0)); }
SHARED_PTR<IfcOrganization> IfcPersonAndOrganization::TheOrganization() { return reinterpret_pointer_cast<IfcBaseClass,IfcOrganization>(*entity->getArgument(1)); }
bool IfcPersonAndOrganization::hasRoles() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcActorRole> > IfcPersonAndOrganization::Roles() { RETURN_AS_LIST(IfcActorRole,2) }
bool IfcPersonAndOrganization::is(Type::Enum v) { return v == Type::IfcPersonAndOrganization; }
Type::Enum IfcPersonAndOrganization::type() { return Type::IfcPersonAndOrganization; }
Type::Enum IfcPersonAndOrganization::Class() { return Type::IfcPersonAndOrganization; }
IfcPersonAndOrganization::IfcPersonAndOrganization(IfcAbstractEntityPtr e) { if (!is(Type::IfcPersonAndOrganization)) throw; entity = e; } 
// IfcPhysicalComplexQuantity
SHARED_PTR< IfcTemplatedEntityList<IfcPhysicalQuantity> > IfcPhysicalComplexQuantity::HasQuantities() { RETURN_AS_LIST(IfcPhysicalQuantity,2) }
IfcLabel IfcPhysicalComplexQuantity::Discrimination() { return *entity->getArgument(3); }
bool IfcPhysicalComplexQuantity::hasQuality() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcPhysicalComplexQuantity::Quality() { return *entity->getArgument(4); }
bool IfcPhysicalComplexQuantity::hasUsage() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcPhysicalComplexQuantity::Usage() { return *entity->getArgument(5); }
bool IfcPhysicalComplexQuantity::is(Type::Enum v) { return v == Type::IfcPhysicalComplexQuantity || IfcPhysicalQuantity::is(v); }
Type::Enum IfcPhysicalComplexQuantity::type() { return Type::IfcPhysicalComplexQuantity; }
Type::Enum IfcPhysicalComplexQuantity::Class() { return Type::IfcPhysicalComplexQuantity; }
IfcPhysicalComplexQuantity::IfcPhysicalComplexQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcPhysicalComplexQuantity)) throw; entity = e; } 
// IfcPhysicalQuantity
IfcLabel IfcPhysicalQuantity::Name() { return *entity->getArgument(0); }
bool IfcPhysicalQuantity::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcPhysicalQuantity::Description() { return *entity->getArgument(1); }
IfcPhysicalComplexQuantity::list IfcPhysicalQuantity::PartOfComplex() { RETURN_INVERSE(IfcPhysicalComplexQuantity) }
bool IfcPhysicalQuantity::is(Type::Enum v) { return v == Type::IfcPhysicalQuantity; }
Type::Enum IfcPhysicalQuantity::type() { return Type::IfcPhysicalQuantity; }
Type::Enum IfcPhysicalQuantity::Class() { return Type::IfcPhysicalQuantity; }
IfcPhysicalQuantity::IfcPhysicalQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcPhysicalQuantity)) throw; entity = e; } 
// IfcPhysicalSimpleQuantity
bool IfcPhysicalSimpleQuantity::hasUnit() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR<IfcNamedUnit> IfcPhysicalSimpleQuantity::Unit() { return reinterpret_pointer_cast<IfcBaseClass,IfcNamedUnit>(*entity->getArgument(2)); }
bool IfcPhysicalSimpleQuantity::is(Type::Enum v) { return v == Type::IfcPhysicalSimpleQuantity || IfcPhysicalQuantity::is(v); }
Type::Enum IfcPhysicalSimpleQuantity::type() { return Type::IfcPhysicalSimpleQuantity; }
Type::Enum IfcPhysicalSimpleQuantity::Class() { return Type::IfcPhysicalSimpleQuantity; }
IfcPhysicalSimpleQuantity::IfcPhysicalSimpleQuantity(IfcAbstractEntityPtr e) { if (!is(Type::IfcPhysicalSimpleQuantity)) throw; entity = e; } 
// IfcPile
IfcPileTypeEnum::IfcPileTypeEnum IfcPile::PredefinedType() { return IfcPileTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcPile::hasConstructionType() { return !entity->getArgument(9)->isNull(); }
IfcPileConstructionEnum::IfcPileConstructionEnum IfcPile::ConstructionType() { return IfcPileConstructionEnum::FromString(*entity->getArgument(9)); }
bool IfcPile::is(Type::Enum v) { return v == Type::IfcPile || IfcBuildingElement::is(v); }
Type::Enum IfcPile::type() { return Type::IfcPile; }
Type::Enum IfcPile::Class() { return Type::IfcPile; }
IfcPile::IfcPile(IfcAbstractEntityPtr e) { if (!is(Type::IfcPile)) throw; entity = e; } 
// IfcPipeFittingType
IfcPipeFittingTypeEnum::IfcPipeFittingTypeEnum IfcPipeFittingType::PredefinedType() { return IfcPipeFittingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPipeFittingType::is(Type::Enum v) { return v == Type::IfcPipeFittingType || IfcFlowFittingType::is(v); }
Type::Enum IfcPipeFittingType::type() { return Type::IfcPipeFittingType; }
Type::Enum IfcPipeFittingType::Class() { return Type::IfcPipeFittingType; }
IfcPipeFittingType::IfcPipeFittingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPipeFittingType)) throw; entity = e; } 
// IfcPipeSegmentType
IfcPipeSegmentTypeEnum::IfcPipeSegmentTypeEnum IfcPipeSegmentType::PredefinedType() { return IfcPipeSegmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPipeSegmentType::is(Type::Enum v) { return v == Type::IfcPipeSegmentType || IfcFlowSegmentType::is(v); }
Type::Enum IfcPipeSegmentType::type() { return Type::IfcPipeSegmentType; }
Type::Enum IfcPipeSegmentType::Class() { return Type::IfcPipeSegmentType; }
IfcPipeSegmentType::IfcPipeSegmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPipeSegmentType)) throw; entity = e; } 
// IfcPixelTexture
IfcInteger IfcPixelTexture::Width() { return *entity->getArgument(4); }
IfcInteger IfcPixelTexture::Height() { return *entity->getArgument(5); }
IfcInteger IfcPixelTexture::ColourComponents() { return *entity->getArgument(6); }
std::vector<char[32]> /*[1:?]*/ IfcPixelTexture::Pixel() { throw; /* Not implemented argument 7 */ }
bool IfcPixelTexture::is(Type::Enum v) { return v == Type::IfcPixelTexture || IfcSurfaceTexture::is(v); }
Type::Enum IfcPixelTexture::type() { return Type::IfcPixelTexture; }
Type::Enum IfcPixelTexture::Class() { return Type::IfcPixelTexture; }
IfcPixelTexture::IfcPixelTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcPixelTexture)) throw; entity = e; } 
// IfcPlacement
SHARED_PTR<IfcCartesianPoint> IfcPlacement::Location() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianPoint>(*entity->getArgument(0)); }
bool IfcPlacement::is(Type::Enum v) { return v == Type::IfcPlacement || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcPlacement::type() { return Type::IfcPlacement; }
Type::Enum IfcPlacement::Class() { return Type::IfcPlacement; }
IfcPlacement::IfcPlacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlacement)) throw; entity = e; } 
// IfcPlanarBox
IfcAxis2Placement IfcPlanarBox::Placement() { return *entity->getArgument(2); }
bool IfcPlanarBox::is(Type::Enum v) { return v == Type::IfcPlanarBox || IfcPlanarExtent::is(v); }
Type::Enum IfcPlanarBox::type() { return Type::IfcPlanarBox; }
Type::Enum IfcPlanarBox::Class() { return Type::IfcPlanarBox; }
IfcPlanarBox::IfcPlanarBox(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlanarBox)) throw; entity = e; } 
// IfcPlanarExtent
IfcLengthMeasure IfcPlanarExtent::SizeInX() { return *entity->getArgument(0); }
IfcLengthMeasure IfcPlanarExtent::SizeInY() { return *entity->getArgument(1); }
bool IfcPlanarExtent::is(Type::Enum v) { return v == Type::IfcPlanarExtent || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcPlanarExtent::type() { return Type::IfcPlanarExtent; }
Type::Enum IfcPlanarExtent::Class() { return Type::IfcPlanarExtent; }
IfcPlanarExtent::IfcPlanarExtent(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlanarExtent)) throw; entity = e; } 
// IfcPlane
bool IfcPlane::is(Type::Enum v) { return v == Type::IfcPlane || IfcElementarySurface::is(v); }
Type::Enum IfcPlane::type() { return Type::IfcPlane; }
Type::Enum IfcPlane::Class() { return Type::IfcPlane; }
IfcPlane::IfcPlane(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlane)) throw; entity = e; } 
// IfcPlate
bool IfcPlate::is(Type::Enum v) { return v == Type::IfcPlate || IfcBuildingElement::is(v); }
Type::Enum IfcPlate::type() { return Type::IfcPlate; }
Type::Enum IfcPlate::Class() { return Type::IfcPlate; }
IfcPlate::IfcPlate(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlate)) throw; entity = e; } 
// IfcPlateType
IfcPlateTypeEnum::IfcPlateTypeEnum IfcPlateType::PredefinedType() { return IfcPlateTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPlateType::is(Type::Enum v) { return v == Type::IfcPlateType || IfcBuildingElementType::is(v); }
Type::Enum IfcPlateType::type() { return Type::IfcPlateType; }
Type::Enum IfcPlateType::Class() { return Type::IfcPlateType; }
IfcPlateType::IfcPlateType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPlateType)) throw; entity = e; } 
// IfcPoint
bool IfcPoint::is(Type::Enum v) { return v == Type::IfcPoint || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcPoint::type() { return Type::IfcPoint; }
Type::Enum IfcPoint::Class() { return Type::IfcPoint; }
IfcPoint::IfcPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcPoint)) throw; entity = e; } 
// IfcPointOnCurve
SHARED_PTR<IfcCurve> IfcPointOnCurve::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcParameterValue IfcPointOnCurve::PointParameter() { return *entity->getArgument(1); }
bool IfcPointOnCurve::is(Type::Enum v) { return v == Type::IfcPointOnCurve || IfcPoint::is(v); }
Type::Enum IfcPointOnCurve::type() { return Type::IfcPointOnCurve; }
Type::Enum IfcPointOnCurve::Class() { return Type::IfcPointOnCurve; }
IfcPointOnCurve::IfcPointOnCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcPointOnCurve)) throw; entity = e; } 
// IfcPointOnSurface
SHARED_PTR<IfcSurface> IfcPointOnSurface::BasisSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(0)); }
IfcParameterValue IfcPointOnSurface::PointParameterU() { return *entity->getArgument(1); }
IfcParameterValue IfcPointOnSurface::PointParameterV() { return *entity->getArgument(2); }
bool IfcPointOnSurface::is(Type::Enum v) { return v == Type::IfcPointOnSurface || IfcPoint::is(v); }
Type::Enum IfcPointOnSurface::type() { return Type::IfcPointOnSurface; }
Type::Enum IfcPointOnSurface::Class() { return Type::IfcPointOnSurface; }
IfcPointOnSurface::IfcPointOnSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcPointOnSurface)) throw; entity = e; } 
// IfcPolyLoop
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcPolyLoop::Polygon() { RETURN_AS_LIST(IfcCartesianPoint,0) }
bool IfcPolyLoop::is(Type::Enum v) { return v == Type::IfcPolyLoop || IfcLoop::is(v); }
Type::Enum IfcPolyLoop::type() { return Type::IfcPolyLoop; }
Type::Enum IfcPolyLoop::Class() { return Type::IfcPolyLoop; }
IfcPolyLoop::IfcPolyLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcPolyLoop)) throw; entity = e; } 
// IfcPolygonalBoundedHalfSpace
SHARED_PTR<IfcAxis2Placement3D> IfcPolygonalBoundedHalfSpace::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(2)); }
SHARED_PTR<IfcBoundedCurve> IfcPolygonalBoundedHalfSpace::PolygonalBoundary() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundedCurve>(*entity->getArgument(3)); }
bool IfcPolygonalBoundedHalfSpace::is(Type::Enum v) { return v == Type::IfcPolygonalBoundedHalfSpace || IfcHalfSpaceSolid::is(v); }
Type::Enum IfcPolygonalBoundedHalfSpace::type() { return Type::IfcPolygonalBoundedHalfSpace; }
Type::Enum IfcPolygonalBoundedHalfSpace::Class() { return Type::IfcPolygonalBoundedHalfSpace; }
IfcPolygonalBoundedHalfSpace::IfcPolygonalBoundedHalfSpace(IfcAbstractEntityPtr e) { if (!is(Type::IfcPolygonalBoundedHalfSpace)) throw; entity = e; } 
// IfcPolyline
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcPolyline::Points() { RETURN_AS_LIST(IfcCartesianPoint,0) }
bool IfcPolyline::is(Type::Enum v) { return v == Type::IfcPolyline || IfcBoundedCurve::is(v); }
Type::Enum IfcPolyline::type() { return Type::IfcPolyline; }
Type::Enum IfcPolyline::Class() { return Type::IfcPolyline; }
IfcPolyline::IfcPolyline(IfcAbstractEntityPtr e) { if (!is(Type::IfcPolyline)) throw; entity = e; } 
// IfcPort
IfcRelConnectsPortToElement::list IfcPort::ContainedIn() { RETURN_INVERSE(IfcRelConnectsPortToElement) }
IfcRelConnectsPorts::list IfcPort::ConnectedFrom() { RETURN_INVERSE(IfcRelConnectsPorts) }
IfcRelConnectsPorts::list IfcPort::ConnectedTo() { RETURN_INVERSE(IfcRelConnectsPorts) }
bool IfcPort::is(Type::Enum v) { return v == Type::IfcPort || IfcProduct::is(v); }
Type::Enum IfcPort::type() { return Type::IfcPort; }
Type::Enum IfcPort::Class() { return Type::IfcPort; }
IfcPort::IfcPort(IfcAbstractEntityPtr e) { if (!is(Type::IfcPort)) throw; entity = e; } 
// IfcPostalAddress
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
bool IfcPostalAddress::is(Type::Enum v) { return v == Type::IfcPostalAddress || IfcAddress::is(v); }
Type::Enum IfcPostalAddress::type() { return Type::IfcPostalAddress; }
Type::Enum IfcPostalAddress::Class() { return Type::IfcPostalAddress; }
IfcPostalAddress::IfcPostalAddress(IfcAbstractEntityPtr e) { if (!is(Type::IfcPostalAddress)) throw; entity = e; } 
// IfcPreDefinedColour
bool IfcPreDefinedColour::is(Type::Enum v) { return v == Type::IfcPreDefinedColour || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedColour::type() { return Type::IfcPreDefinedColour; }
Type::Enum IfcPreDefinedColour::Class() { return Type::IfcPreDefinedColour; }
IfcPreDefinedColour::IfcPreDefinedColour(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedColour)) throw; entity = e; } 
// IfcPreDefinedCurveFont
bool IfcPreDefinedCurveFont::is(Type::Enum v) { return v == Type::IfcPreDefinedCurveFont || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedCurveFont::type() { return Type::IfcPreDefinedCurveFont; }
Type::Enum IfcPreDefinedCurveFont::Class() { return Type::IfcPreDefinedCurveFont; }
IfcPreDefinedCurveFont::IfcPreDefinedCurveFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedCurveFont)) throw; entity = e; } 
// IfcPreDefinedDimensionSymbol
bool IfcPreDefinedDimensionSymbol::is(Type::Enum v) { return v == Type::IfcPreDefinedDimensionSymbol || IfcPreDefinedSymbol::is(v); }
Type::Enum IfcPreDefinedDimensionSymbol::type() { return Type::IfcPreDefinedDimensionSymbol; }
Type::Enum IfcPreDefinedDimensionSymbol::Class() { return Type::IfcPreDefinedDimensionSymbol; }
IfcPreDefinedDimensionSymbol::IfcPreDefinedDimensionSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedDimensionSymbol)) throw; entity = e; } 
// IfcPreDefinedItem
IfcLabel IfcPreDefinedItem::Name() { return *entity->getArgument(0); }
bool IfcPreDefinedItem::is(Type::Enum v) { return v == Type::IfcPreDefinedItem; }
Type::Enum IfcPreDefinedItem::type() { return Type::IfcPreDefinedItem; }
Type::Enum IfcPreDefinedItem::Class() { return Type::IfcPreDefinedItem; }
IfcPreDefinedItem::IfcPreDefinedItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedItem)) throw; entity = e; } 
// IfcPreDefinedPointMarkerSymbol
bool IfcPreDefinedPointMarkerSymbol::is(Type::Enum v) { return v == Type::IfcPreDefinedPointMarkerSymbol || IfcPreDefinedSymbol::is(v); }
Type::Enum IfcPreDefinedPointMarkerSymbol::type() { return Type::IfcPreDefinedPointMarkerSymbol; }
Type::Enum IfcPreDefinedPointMarkerSymbol::Class() { return Type::IfcPreDefinedPointMarkerSymbol; }
IfcPreDefinedPointMarkerSymbol::IfcPreDefinedPointMarkerSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedPointMarkerSymbol)) throw; entity = e; } 
// IfcPreDefinedSymbol
bool IfcPreDefinedSymbol::is(Type::Enum v) { return v == Type::IfcPreDefinedSymbol || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedSymbol::type() { return Type::IfcPreDefinedSymbol; }
Type::Enum IfcPreDefinedSymbol::Class() { return Type::IfcPreDefinedSymbol; }
IfcPreDefinedSymbol::IfcPreDefinedSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedSymbol)) throw; entity = e; } 
// IfcPreDefinedTerminatorSymbol
bool IfcPreDefinedTerminatorSymbol::is(Type::Enum v) { return v == Type::IfcPreDefinedTerminatorSymbol || IfcPreDefinedSymbol::is(v); }
Type::Enum IfcPreDefinedTerminatorSymbol::type() { return Type::IfcPreDefinedTerminatorSymbol; }
Type::Enum IfcPreDefinedTerminatorSymbol::Class() { return Type::IfcPreDefinedTerminatorSymbol; }
IfcPreDefinedTerminatorSymbol::IfcPreDefinedTerminatorSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedTerminatorSymbol)) throw; entity = e; } 
// IfcPreDefinedTextFont
bool IfcPreDefinedTextFont::is(Type::Enum v) { return v == Type::IfcPreDefinedTextFont || IfcPreDefinedItem::is(v); }
Type::Enum IfcPreDefinedTextFont::type() { return Type::IfcPreDefinedTextFont; }
Type::Enum IfcPreDefinedTextFont::Class() { return Type::IfcPreDefinedTextFont; }
IfcPreDefinedTextFont::IfcPreDefinedTextFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcPreDefinedTextFont)) throw; entity = e; } 
// IfcPresentationLayerAssignment
IfcLabel IfcPresentationLayerAssignment::Name() { return *entity->getArgument(0); }
bool IfcPresentationLayerAssignment::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcPresentationLayerAssignment::Description() { return *entity->getArgument(1); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPresentationLayerAssignment::AssignedItems() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcPresentationLayerAssignment::hasIdentifier() { return !entity->getArgument(3)->isNull(); }
IfcIdentifier IfcPresentationLayerAssignment::Identifier() { return *entity->getArgument(3); }
bool IfcPresentationLayerAssignment::is(Type::Enum v) { return v == Type::IfcPresentationLayerAssignment; }
Type::Enum IfcPresentationLayerAssignment::type() { return Type::IfcPresentationLayerAssignment; }
Type::Enum IfcPresentationLayerAssignment::Class() { return Type::IfcPresentationLayerAssignment; }
IfcPresentationLayerAssignment::IfcPresentationLayerAssignment(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationLayerAssignment)) throw; entity = e; } 
// IfcPresentationLayerWithStyle
bool IfcPresentationLayerWithStyle::LayerOn() { return *entity->getArgument(4); }
bool IfcPresentationLayerWithStyle::LayerFrozen() { return *entity->getArgument(5); }
bool IfcPresentationLayerWithStyle::LayerBlocked() { return *entity->getArgument(6); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPresentationLayerWithStyle::LayerStyles() { RETURN_AS_LIST(IfcAbstractSelect,7) }
bool IfcPresentationLayerWithStyle::is(Type::Enum v) { return v == Type::IfcPresentationLayerWithStyle || IfcPresentationLayerAssignment::is(v); }
Type::Enum IfcPresentationLayerWithStyle::type() { return Type::IfcPresentationLayerWithStyle; }
Type::Enum IfcPresentationLayerWithStyle::Class() { return Type::IfcPresentationLayerWithStyle; }
IfcPresentationLayerWithStyle::IfcPresentationLayerWithStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationLayerWithStyle)) throw; entity = e; } 
// IfcPresentationStyle
bool IfcPresentationStyle::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcPresentationStyle::Name() { return *entity->getArgument(0); }
bool IfcPresentationStyle::is(Type::Enum v) { return v == Type::IfcPresentationStyle; }
Type::Enum IfcPresentationStyle::type() { return Type::IfcPresentationStyle; }
Type::Enum IfcPresentationStyle::Class() { return Type::IfcPresentationStyle; }
IfcPresentationStyle::IfcPresentationStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationStyle)) throw; entity = e; } 
// IfcPresentationStyleAssignment
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPresentationStyleAssignment::Styles() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcPresentationStyleAssignment::is(Type::Enum v) { return v == Type::IfcPresentationStyleAssignment; }
Type::Enum IfcPresentationStyleAssignment::type() { return Type::IfcPresentationStyleAssignment; }
Type::Enum IfcPresentationStyleAssignment::Class() { return Type::IfcPresentationStyleAssignment; }
IfcPresentationStyleAssignment::IfcPresentationStyleAssignment(IfcAbstractEntityPtr e) { if (!is(Type::IfcPresentationStyleAssignment)) throw; entity = e; } 
// IfcProcedure
IfcIdentifier IfcProcedure::ProcedureID() { return *entity->getArgument(5); }
IfcProcedureTypeEnum::IfcProcedureTypeEnum IfcProcedure::ProcedureType() { return IfcProcedureTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcProcedure::hasUserDefinedProcedureType() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcProcedure::UserDefinedProcedureType() { return *entity->getArgument(7); }
bool IfcProcedure::is(Type::Enum v) { return v == Type::IfcProcedure || IfcProcess::is(v); }
Type::Enum IfcProcedure::type() { return Type::IfcProcedure; }
Type::Enum IfcProcedure::Class() { return Type::IfcProcedure; }
IfcProcedure::IfcProcedure(IfcAbstractEntityPtr e) { if (!is(Type::IfcProcedure)) throw; entity = e; } 
// IfcProcess
IfcRelAssignsToProcess::list IfcProcess::OperatesOn() { RETURN_INVERSE(IfcRelAssignsToProcess) }
IfcRelSequence::list IfcProcess::IsSuccessorFrom() { RETURN_INVERSE(IfcRelSequence) }
IfcRelSequence::list IfcProcess::IsPredecessorTo() { RETURN_INVERSE(IfcRelSequence) }
bool IfcProcess::is(Type::Enum v) { return v == Type::IfcProcess || IfcObject::is(v); }
Type::Enum IfcProcess::type() { return Type::IfcProcess; }
Type::Enum IfcProcess::Class() { return Type::IfcProcess; }
IfcProcess::IfcProcess(IfcAbstractEntityPtr e) { if (!is(Type::IfcProcess)) throw; entity = e; } 
// IfcProduct
bool IfcProduct::hasObjectPlacement() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR<IfcObjectPlacement> IfcProduct::ObjectPlacement() { return reinterpret_pointer_cast<IfcBaseClass,IfcObjectPlacement>(*entity->getArgument(5)); }
bool IfcProduct::hasRepresentation() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcProductRepresentation> IfcProduct::Representation() { return reinterpret_pointer_cast<IfcBaseClass,IfcProductRepresentation>(*entity->getArgument(6)); }
IfcRelAssignsToProduct::list IfcProduct::ReferencedBy() { RETURN_INVERSE(IfcRelAssignsToProduct) }
bool IfcProduct::is(Type::Enum v) { return v == Type::IfcProduct || IfcObject::is(v); }
Type::Enum IfcProduct::type() { return Type::IfcProduct; }
Type::Enum IfcProduct::Class() { return Type::IfcProduct; }
IfcProduct::IfcProduct(IfcAbstractEntityPtr e) { if (!is(Type::IfcProduct)) throw; entity = e; } 
// IfcProductDefinitionShape
IfcProduct::list IfcProductDefinitionShape::ShapeOfProduct() { RETURN_INVERSE(IfcProduct) }
IfcShapeAspect::list IfcProductDefinitionShape::HasShapeAspects() { RETURN_INVERSE(IfcShapeAspect) }
bool IfcProductDefinitionShape::is(Type::Enum v) { return v == Type::IfcProductDefinitionShape || IfcProductRepresentation::is(v); }
Type::Enum IfcProductDefinitionShape::type() { return Type::IfcProductDefinitionShape; }
Type::Enum IfcProductDefinitionShape::Class() { return Type::IfcProductDefinitionShape; }
IfcProductDefinitionShape::IfcProductDefinitionShape(IfcAbstractEntityPtr e) { if (!is(Type::IfcProductDefinitionShape)) throw; entity = e; } 
// IfcProductRepresentation
bool IfcProductRepresentation::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcProductRepresentation::Name() { return *entity->getArgument(0); }
bool IfcProductRepresentation::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcProductRepresentation::Description() { return *entity->getArgument(1); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentation> > IfcProductRepresentation::Representations() { RETURN_AS_LIST(IfcRepresentation,2) }
bool IfcProductRepresentation::is(Type::Enum v) { return v == Type::IfcProductRepresentation; }
Type::Enum IfcProductRepresentation::type() { return Type::IfcProductRepresentation; }
Type::Enum IfcProductRepresentation::Class() { return Type::IfcProductRepresentation; }
IfcProductRepresentation::IfcProductRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcProductRepresentation)) throw; entity = e; } 
// IfcProductsOfCombustionProperties
bool IfcProductsOfCombustionProperties::hasSpecificHeatCapacity() { return !entity->getArgument(1)->isNull(); }
IfcSpecificHeatCapacityMeasure IfcProductsOfCombustionProperties::SpecificHeatCapacity() { return *entity->getArgument(1); }
bool IfcProductsOfCombustionProperties::hasN20Content() { return !entity->getArgument(2)->isNull(); }
IfcPositiveRatioMeasure IfcProductsOfCombustionProperties::N20Content() { return *entity->getArgument(2); }
bool IfcProductsOfCombustionProperties::hasCOContent() { return !entity->getArgument(3)->isNull(); }
IfcPositiveRatioMeasure IfcProductsOfCombustionProperties::COContent() { return *entity->getArgument(3); }
bool IfcProductsOfCombustionProperties::hasCO2Content() { return !entity->getArgument(4)->isNull(); }
IfcPositiveRatioMeasure IfcProductsOfCombustionProperties::CO2Content() { return *entity->getArgument(4); }
bool IfcProductsOfCombustionProperties::is(Type::Enum v) { return v == Type::IfcProductsOfCombustionProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcProductsOfCombustionProperties::type() { return Type::IfcProductsOfCombustionProperties; }
Type::Enum IfcProductsOfCombustionProperties::Class() { return Type::IfcProductsOfCombustionProperties; }
IfcProductsOfCombustionProperties::IfcProductsOfCombustionProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcProductsOfCombustionProperties)) throw; entity = e; } 
// IfcProfileDef
IfcProfileTypeEnum::IfcProfileTypeEnum IfcProfileDef::ProfileType() { return IfcProfileTypeEnum::FromString(*entity->getArgument(0)); }
bool IfcProfileDef::hasProfileName() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcProfileDef::ProfileName() { return *entity->getArgument(1); }
bool IfcProfileDef::is(Type::Enum v) { return v == Type::IfcProfileDef; }
Type::Enum IfcProfileDef::type() { return Type::IfcProfileDef; }
Type::Enum IfcProfileDef::Class() { return Type::IfcProfileDef; }
IfcProfileDef::IfcProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcProfileDef)) throw; entity = e; } 
// IfcProfileProperties
bool IfcProfileProperties::hasProfileName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcProfileProperties::ProfileName() { return *entity->getArgument(0); }
bool IfcProfileProperties::hasProfileDefinition() { return !entity->getArgument(1)->isNull(); }
SHARED_PTR<IfcProfileDef> IfcProfileProperties::ProfileDefinition() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(1)); }
bool IfcProfileProperties::is(Type::Enum v) { return v == Type::IfcProfileProperties; }
Type::Enum IfcProfileProperties::type() { return Type::IfcProfileProperties; }
Type::Enum IfcProfileProperties::Class() { return Type::IfcProfileProperties; }
IfcProfileProperties::IfcProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcProfileProperties)) throw; entity = e; } 
// IfcProject
bool IfcProject::hasLongName() { return !entity->getArgument(5)->isNull(); }
IfcLabel IfcProject::LongName() { return *entity->getArgument(5); }
bool IfcProject::hasPhase() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcProject::Phase() { return *entity->getArgument(6); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationContext> > IfcProject::RepresentationContexts() { RETURN_AS_LIST(IfcRepresentationContext,7) }
SHARED_PTR<IfcUnitAssignment> IfcProject::UnitsInContext() { return reinterpret_pointer_cast<IfcBaseClass,IfcUnitAssignment>(*entity->getArgument(8)); }
bool IfcProject::is(Type::Enum v) { return v == Type::IfcProject || IfcObject::is(v); }
Type::Enum IfcProject::type() { return Type::IfcProject; }
Type::Enum IfcProject::Class() { return Type::IfcProject; }
IfcProject::IfcProject(IfcAbstractEntityPtr e) { if (!is(Type::IfcProject)) throw; entity = e; } 
// IfcProjectOrder
IfcIdentifier IfcProjectOrder::ID() { return *entity->getArgument(5); }
IfcProjectOrderTypeEnum::IfcProjectOrderTypeEnum IfcProjectOrder::PredefinedType() { return IfcProjectOrderTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcProjectOrder::hasStatus() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcProjectOrder::Status() { return *entity->getArgument(7); }
bool IfcProjectOrder::is(Type::Enum v) { return v == Type::IfcProjectOrder || IfcControl::is(v); }
Type::Enum IfcProjectOrder::type() { return Type::IfcProjectOrder; }
Type::Enum IfcProjectOrder::Class() { return Type::IfcProjectOrder; }
IfcProjectOrder::IfcProjectOrder(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectOrder)) throw; entity = e; } 
// IfcProjectOrderRecord
SHARED_PTR< IfcTemplatedEntityList<IfcRelAssignsToProjectOrder> > IfcProjectOrderRecord::Records() { RETURN_AS_LIST(IfcRelAssignsToProjectOrder,5) }
IfcProjectOrderRecordTypeEnum::IfcProjectOrderRecordTypeEnum IfcProjectOrderRecord::PredefinedType() { return IfcProjectOrderRecordTypeEnum::FromString(*entity->getArgument(6)); }
bool IfcProjectOrderRecord::is(Type::Enum v) { return v == Type::IfcProjectOrderRecord || IfcControl::is(v); }
Type::Enum IfcProjectOrderRecord::type() { return Type::IfcProjectOrderRecord; }
Type::Enum IfcProjectOrderRecord::Class() { return Type::IfcProjectOrderRecord; }
IfcProjectOrderRecord::IfcProjectOrderRecord(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectOrderRecord)) throw; entity = e; } 
// IfcProjectionCurve
bool IfcProjectionCurve::is(Type::Enum v) { return v == Type::IfcProjectionCurve || IfcAnnotationCurveOccurrence::is(v); }
Type::Enum IfcProjectionCurve::type() { return Type::IfcProjectionCurve; }
Type::Enum IfcProjectionCurve::Class() { return Type::IfcProjectionCurve; }
IfcProjectionCurve::IfcProjectionCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectionCurve)) throw; entity = e; } 
// IfcProjectionElement
bool IfcProjectionElement::is(Type::Enum v) { return v == Type::IfcProjectionElement || IfcFeatureElementAddition::is(v); }
Type::Enum IfcProjectionElement::type() { return Type::IfcProjectionElement; }
Type::Enum IfcProjectionElement::Class() { return Type::IfcProjectionElement; }
IfcProjectionElement::IfcProjectionElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcProjectionElement)) throw; entity = e; } 
// IfcProperty
IfcIdentifier IfcProperty::Name() { return *entity->getArgument(0); }
bool IfcProperty::hasDescription() { return !entity->getArgument(1)->isNull(); }
IfcText IfcProperty::Description() { return *entity->getArgument(1); }
IfcPropertyDependencyRelationship::list IfcProperty::PropertyForDependance() { RETURN_INVERSE(IfcPropertyDependencyRelationship) }
IfcPropertyDependencyRelationship::list IfcProperty::PropertyDependsOn() { RETURN_INVERSE(IfcPropertyDependencyRelationship) }
IfcComplexProperty::list IfcProperty::PartOfComplex() { RETURN_INVERSE(IfcComplexProperty) }
bool IfcProperty::is(Type::Enum v) { return v == Type::IfcProperty; }
Type::Enum IfcProperty::type() { return Type::IfcProperty; }
Type::Enum IfcProperty::Class() { return Type::IfcProperty; }
IfcProperty::IfcProperty(IfcAbstractEntityPtr e) { if (!is(Type::IfcProperty)) throw; entity = e; } 
// IfcPropertyBoundedValue
bool IfcPropertyBoundedValue::hasUpperBoundValue() { return !entity->getArgument(2)->isNull(); }
IfcValue IfcPropertyBoundedValue::UpperBoundValue() { return *entity->getArgument(2); }
bool IfcPropertyBoundedValue::hasLowerBoundValue() { return !entity->getArgument(3)->isNull(); }
IfcValue IfcPropertyBoundedValue::LowerBoundValue() { return *entity->getArgument(3); }
bool IfcPropertyBoundedValue::hasUnit() { return !entity->getArgument(4)->isNull(); }
IfcUnit IfcPropertyBoundedValue::Unit() { return *entity->getArgument(4); }
bool IfcPropertyBoundedValue::is(Type::Enum v) { return v == Type::IfcPropertyBoundedValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyBoundedValue::type() { return Type::IfcPropertyBoundedValue; }
Type::Enum IfcPropertyBoundedValue::Class() { return Type::IfcPropertyBoundedValue; }
IfcPropertyBoundedValue::IfcPropertyBoundedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyBoundedValue)) throw; entity = e; } 
// IfcPropertyConstraintRelationship
SHARED_PTR<IfcConstraint> IfcPropertyConstraintRelationship::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcPropertyConstraintRelationship::RelatedProperties() { RETURN_AS_LIST(IfcProperty,1) }
bool IfcPropertyConstraintRelationship::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcPropertyConstraintRelationship::Name() { return *entity->getArgument(2); }
bool IfcPropertyConstraintRelationship::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcPropertyConstraintRelationship::Description() { return *entity->getArgument(3); }
bool IfcPropertyConstraintRelationship::is(Type::Enum v) { return v == Type::IfcPropertyConstraintRelationship; }
Type::Enum IfcPropertyConstraintRelationship::type() { return Type::IfcPropertyConstraintRelationship; }
Type::Enum IfcPropertyConstraintRelationship::Class() { return Type::IfcPropertyConstraintRelationship; }
IfcPropertyConstraintRelationship::IfcPropertyConstraintRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyConstraintRelationship)) throw; entity = e; } 
// IfcPropertyDefinition
IfcRelAssociates::list IfcPropertyDefinition::HasAssociations() { RETURN_INVERSE(IfcRelAssociates) }
bool IfcPropertyDefinition::is(Type::Enum v) { return v == Type::IfcPropertyDefinition || IfcRoot::is(v); }
Type::Enum IfcPropertyDefinition::type() { return Type::IfcPropertyDefinition; }
Type::Enum IfcPropertyDefinition::Class() { return Type::IfcPropertyDefinition; }
IfcPropertyDefinition::IfcPropertyDefinition(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyDefinition)) throw; entity = e; } 
// IfcPropertyDependencyRelationship
SHARED_PTR<IfcProperty> IfcPropertyDependencyRelationship::DependingProperty() { return reinterpret_pointer_cast<IfcBaseClass,IfcProperty>(*entity->getArgument(0)); }
SHARED_PTR<IfcProperty> IfcPropertyDependencyRelationship::DependantProperty() { return reinterpret_pointer_cast<IfcBaseClass,IfcProperty>(*entity->getArgument(1)); }
bool IfcPropertyDependencyRelationship::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcPropertyDependencyRelationship::Name() { return *entity->getArgument(2); }
bool IfcPropertyDependencyRelationship::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcPropertyDependencyRelationship::Description() { return *entity->getArgument(3); }
bool IfcPropertyDependencyRelationship::hasExpression() { return !entity->getArgument(4)->isNull(); }
IfcText IfcPropertyDependencyRelationship::Expression() { return *entity->getArgument(4); }
bool IfcPropertyDependencyRelationship::is(Type::Enum v) { return v == Type::IfcPropertyDependencyRelationship; }
Type::Enum IfcPropertyDependencyRelationship::type() { return Type::IfcPropertyDependencyRelationship; }
Type::Enum IfcPropertyDependencyRelationship::Class() { return Type::IfcPropertyDependencyRelationship; }
IfcPropertyDependencyRelationship::IfcPropertyDependencyRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyDependencyRelationship)) throw; entity = e; } 
// IfcPropertyEnumeratedValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyEnumeratedValue::EnumerationValues() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcPropertyEnumeratedValue::hasEnumerationReference() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcPropertyEnumeration> IfcPropertyEnumeratedValue::EnumerationReference() { return reinterpret_pointer_cast<IfcBaseClass,IfcPropertyEnumeration>(*entity->getArgument(3)); }
bool IfcPropertyEnumeratedValue::is(Type::Enum v) { return v == Type::IfcPropertyEnumeratedValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyEnumeratedValue::type() { return Type::IfcPropertyEnumeratedValue; }
Type::Enum IfcPropertyEnumeratedValue::Class() { return Type::IfcPropertyEnumeratedValue; }
IfcPropertyEnumeratedValue::IfcPropertyEnumeratedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyEnumeratedValue)) throw; entity = e; } 
// IfcPropertyEnumeration
IfcLabel IfcPropertyEnumeration::Name() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyEnumeration::EnumerationValues() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcPropertyEnumeration::hasUnit() { return !entity->getArgument(2)->isNull(); }
IfcUnit IfcPropertyEnumeration::Unit() { return *entity->getArgument(2); }
bool IfcPropertyEnumeration::is(Type::Enum v) { return v == Type::IfcPropertyEnumeration; }
Type::Enum IfcPropertyEnumeration::type() { return Type::IfcPropertyEnumeration; }
Type::Enum IfcPropertyEnumeration::Class() { return Type::IfcPropertyEnumeration; }
IfcPropertyEnumeration::IfcPropertyEnumeration(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyEnumeration)) throw; entity = e; } 
// IfcPropertyListValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyListValue::ListValues() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcPropertyListValue::hasUnit() { return !entity->getArgument(3)->isNull(); }
IfcUnit IfcPropertyListValue::Unit() { return *entity->getArgument(3); }
bool IfcPropertyListValue::is(Type::Enum v) { return v == Type::IfcPropertyListValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyListValue::type() { return Type::IfcPropertyListValue; }
Type::Enum IfcPropertyListValue::Class() { return Type::IfcPropertyListValue; }
IfcPropertyListValue::IfcPropertyListValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyListValue)) throw; entity = e; } 
// IfcPropertyReferenceValue
bool IfcPropertyReferenceValue::hasUsageName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcPropertyReferenceValue::UsageName() { return *entity->getArgument(2); }
IfcObjectReferenceSelect IfcPropertyReferenceValue::PropertyReference() { return *entity->getArgument(3); }
bool IfcPropertyReferenceValue::is(Type::Enum v) { return v == Type::IfcPropertyReferenceValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyReferenceValue::type() { return Type::IfcPropertyReferenceValue; }
Type::Enum IfcPropertyReferenceValue::Class() { return Type::IfcPropertyReferenceValue; }
IfcPropertyReferenceValue::IfcPropertyReferenceValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyReferenceValue)) throw; entity = e; } 
// IfcPropertySet
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcPropertySet::HasProperties() { RETURN_AS_LIST(IfcProperty,4) }
bool IfcPropertySet::is(Type::Enum v) { return v == Type::IfcPropertySet || IfcPropertySetDefinition::is(v); }
Type::Enum IfcPropertySet::type() { return Type::IfcPropertySet; }
Type::Enum IfcPropertySet::Class() { return Type::IfcPropertySet; }
IfcPropertySet::IfcPropertySet(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertySet)) throw; entity = e; } 
// IfcPropertySetDefinition
IfcRelDefinesByProperties::list IfcPropertySetDefinition::PropertyDefinitionOf() { RETURN_INVERSE(IfcRelDefinesByProperties) }
IfcTypeObject::list IfcPropertySetDefinition::DefinesType() { RETURN_INVERSE(IfcTypeObject) }
bool IfcPropertySetDefinition::is(Type::Enum v) { return v == Type::IfcPropertySetDefinition || IfcPropertyDefinition::is(v); }
Type::Enum IfcPropertySetDefinition::type() { return Type::IfcPropertySetDefinition; }
Type::Enum IfcPropertySetDefinition::Class() { return Type::IfcPropertySetDefinition; }
IfcPropertySetDefinition::IfcPropertySetDefinition(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertySetDefinition)) throw; entity = e; } 
// IfcPropertySingleValue
bool IfcPropertySingleValue::hasNominalValue() { return !entity->getArgument(2)->isNull(); }
IfcValue IfcPropertySingleValue::NominalValue() { return *entity->getArgument(2); }
bool IfcPropertySingleValue::hasUnit() { return !entity->getArgument(3)->isNull(); }
IfcUnit IfcPropertySingleValue::Unit() { return *entity->getArgument(3); }
bool IfcPropertySingleValue::is(Type::Enum v) { return v == Type::IfcPropertySingleValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertySingleValue::type() { return Type::IfcPropertySingleValue; }
Type::Enum IfcPropertySingleValue::Class() { return Type::IfcPropertySingleValue; }
IfcPropertySingleValue::IfcPropertySingleValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertySingleValue)) throw; entity = e; } 
// IfcPropertyTableValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyTableValue::DefiningValues() { RETURN_AS_LIST(IfcAbstractSelect,2) }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcPropertyTableValue::DefinedValues() { RETURN_AS_LIST(IfcAbstractSelect,3) }
bool IfcPropertyTableValue::hasExpression() { return !entity->getArgument(4)->isNull(); }
IfcText IfcPropertyTableValue::Expression() { return *entity->getArgument(4); }
bool IfcPropertyTableValue::hasDefiningUnit() { return !entity->getArgument(5)->isNull(); }
IfcUnit IfcPropertyTableValue::DefiningUnit() { return *entity->getArgument(5); }
bool IfcPropertyTableValue::hasDefinedUnit() { return !entity->getArgument(6)->isNull(); }
IfcUnit IfcPropertyTableValue::DefinedUnit() { return *entity->getArgument(6); }
bool IfcPropertyTableValue::is(Type::Enum v) { return v == Type::IfcPropertyTableValue || IfcSimpleProperty::is(v); }
Type::Enum IfcPropertyTableValue::type() { return Type::IfcPropertyTableValue; }
Type::Enum IfcPropertyTableValue::Class() { return Type::IfcPropertyTableValue; }
IfcPropertyTableValue::IfcPropertyTableValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcPropertyTableValue)) throw; entity = e; } 
// IfcProtectiveDeviceType
IfcProtectiveDeviceTypeEnum::IfcProtectiveDeviceTypeEnum IfcProtectiveDeviceType::PredefinedType() { return IfcProtectiveDeviceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcProtectiveDeviceType::is(Type::Enum v) { return v == Type::IfcProtectiveDeviceType || IfcFlowControllerType::is(v); }
Type::Enum IfcProtectiveDeviceType::type() { return Type::IfcProtectiveDeviceType; }
Type::Enum IfcProtectiveDeviceType::Class() { return Type::IfcProtectiveDeviceType; }
IfcProtectiveDeviceType::IfcProtectiveDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcProtectiveDeviceType)) throw; entity = e; } 
// IfcProxy
IfcObjectTypeEnum::IfcObjectTypeEnum IfcProxy::ProxyType() { return IfcObjectTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcProxy::hasTag() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcProxy::Tag() { return *entity->getArgument(8); }
bool IfcProxy::is(Type::Enum v) { return v == Type::IfcProxy || IfcProduct::is(v); }
Type::Enum IfcProxy::type() { return Type::IfcProxy; }
Type::Enum IfcProxy::Class() { return Type::IfcProxy; }
IfcProxy::IfcProxy(IfcAbstractEntityPtr e) { if (!is(Type::IfcProxy)) throw; entity = e; } 
// IfcPumpType
IfcPumpTypeEnum::IfcPumpTypeEnum IfcPumpType::PredefinedType() { return IfcPumpTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcPumpType::is(Type::Enum v) { return v == Type::IfcPumpType || IfcFlowMovingDeviceType::is(v); }
Type::Enum IfcPumpType::type() { return Type::IfcPumpType; }
Type::Enum IfcPumpType::Class() { return Type::IfcPumpType; }
IfcPumpType::IfcPumpType(IfcAbstractEntityPtr e) { if (!is(Type::IfcPumpType)) throw; entity = e; } 
// IfcQuantityArea
IfcAreaMeasure IfcQuantityArea::AreaValue() { return *entity->getArgument(3); }
bool IfcQuantityArea::is(Type::Enum v) { return v == Type::IfcQuantityArea || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityArea::type() { return Type::IfcQuantityArea; }
Type::Enum IfcQuantityArea::Class() { return Type::IfcQuantityArea; }
IfcQuantityArea::IfcQuantityArea(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityArea)) throw; entity = e; } 
// IfcQuantityCount
IfcCountMeasure IfcQuantityCount::CountValue() { return *entity->getArgument(3); }
bool IfcQuantityCount::is(Type::Enum v) { return v == Type::IfcQuantityCount || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityCount::type() { return Type::IfcQuantityCount; }
Type::Enum IfcQuantityCount::Class() { return Type::IfcQuantityCount; }
IfcQuantityCount::IfcQuantityCount(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityCount)) throw; entity = e; } 
// IfcQuantityLength
IfcLengthMeasure IfcQuantityLength::LengthValue() { return *entity->getArgument(3); }
bool IfcQuantityLength::is(Type::Enum v) { return v == Type::IfcQuantityLength || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityLength::type() { return Type::IfcQuantityLength; }
Type::Enum IfcQuantityLength::Class() { return Type::IfcQuantityLength; }
IfcQuantityLength::IfcQuantityLength(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityLength)) throw; entity = e; } 
// IfcQuantityTime
IfcTimeMeasure IfcQuantityTime::TimeValue() { return *entity->getArgument(3); }
bool IfcQuantityTime::is(Type::Enum v) { return v == Type::IfcQuantityTime || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityTime::type() { return Type::IfcQuantityTime; }
Type::Enum IfcQuantityTime::Class() { return Type::IfcQuantityTime; }
IfcQuantityTime::IfcQuantityTime(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityTime)) throw; entity = e; } 
// IfcQuantityVolume
IfcVolumeMeasure IfcQuantityVolume::VolumeValue() { return *entity->getArgument(3); }
bool IfcQuantityVolume::is(Type::Enum v) { return v == Type::IfcQuantityVolume || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityVolume::type() { return Type::IfcQuantityVolume; }
Type::Enum IfcQuantityVolume::Class() { return Type::IfcQuantityVolume; }
IfcQuantityVolume::IfcQuantityVolume(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityVolume)) throw; entity = e; } 
// IfcQuantityWeight
IfcMassMeasure IfcQuantityWeight::WeightValue() { return *entity->getArgument(3); }
bool IfcQuantityWeight::is(Type::Enum v) { return v == Type::IfcQuantityWeight || IfcPhysicalSimpleQuantity::is(v); }
Type::Enum IfcQuantityWeight::type() { return Type::IfcQuantityWeight; }
Type::Enum IfcQuantityWeight::Class() { return Type::IfcQuantityWeight; }
IfcQuantityWeight::IfcQuantityWeight(IfcAbstractEntityPtr e) { if (!is(Type::IfcQuantityWeight)) throw; entity = e; } 
// IfcRadiusDimension
bool IfcRadiusDimension::is(Type::Enum v) { return v == Type::IfcRadiusDimension || IfcDimensionCurveDirectedCallout::is(v); }
Type::Enum IfcRadiusDimension::type() { return Type::IfcRadiusDimension; }
Type::Enum IfcRadiusDimension::Class() { return Type::IfcRadiusDimension; }
IfcRadiusDimension::IfcRadiusDimension(IfcAbstractEntityPtr e) { if (!is(Type::IfcRadiusDimension)) throw; entity = e; } 
// IfcRailing
bool IfcRailing::hasPredefinedType() { return !entity->getArgument(8)->isNull(); }
IfcRailingTypeEnum::IfcRailingTypeEnum IfcRailing::PredefinedType() { return IfcRailingTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcRailing::is(Type::Enum v) { return v == Type::IfcRailing || IfcBuildingElement::is(v); }
Type::Enum IfcRailing::type() { return Type::IfcRailing; }
Type::Enum IfcRailing::Class() { return Type::IfcRailing; }
IfcRailing::IfcRailing(IfcAbstractEntityPtr e) { if (!is(Type::IfcRailing)) throw; entity = e; } 
// IfcRailingType
IfcRailingTypeEnum::IfcRailingTypeEnum IfcRailingType::PredefinedType() { return IfcRailingTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcRailingType::is(Type::Enum v) { return v == Type::IfcRailingType || IfcBuildingElementType::is(v); }
Type::Enum IfcRailingType::type() { return Type::IfcRailingType; }
Type::Enum IfcRailingType::Class() { return Type::IfcRailingType; }
IfcRailingType::IfcRailingType(IfcAbstractEntityPtr e) { if (!is(Type::IfcRailingType)) throw; entity = e; } 
// IfcRamp
IfcRampTypeEnum::IfcRampTypeEnum IfcRamp::ShapeType() { return IfcRampTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcRamp::is(Type::Enum v) { return v == Type::IfcRamp || IfcBuildingElement::is(v); }
Type::Enum IfcRamp::type() { return Type::IfcRamp; }
Type::Enum IfcRamp::Class() { return Type::IfcRamp; }
IfcRamp::IfcRamp(IfcAbstractEntityPtr e) { if (!is(Type::IfcRamp)) throw; entity = e; } 
// IfcRampFlight
bool IfcRampFlight::is(Type::Enum v) { return v == Type::IfcRampFlight || IfcBuildingElement::is(v); }
Type::Enum IfcRampFlight::type() { return Type::IfcRampFlight; }
Type::Enum IfcRampFlight::Class() { return Type::IfcRampFlight; }
IfcRampFlight::IfcRampFlight(IfcAbstractEntityPtr e) { if (!is(Type::IfcRampFlight)) throw; entity = e; } 
// IfcRampFlightType
IfcRampFlightTypeEnum::IfcRampFlightTypeEnum IfcRampFlightType::PredefinedType() { return IfcRampFlightTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcRampFlightType::is(Type::Enum v) { return v == Type::IfcRampFlightType || IfcBuildingElementType::is(v); }
Type::Enum IfcRampFlightType::type() { return Type::IfcRampFlightType; }
Type::Enum IfcRampFlightType::Class() { return Type::IfcRampFlightType; }
IfcRampFlightType::IfcRampFlightType(IfcAbstractEntityPtr e) { if (!is(Type::IfcRampFlightType)) throw; entity = e; } 
// IfcRationalBezierCurve
std::vector<float> /*[2:?]*/ IfcRationalBezierCurve::WeightsData() { return *entity->getArgument(5); }
bool IfcRationalBezierCurve::is(Type::Enum v) { return v == Type::IfcRationalBezierCurve || IfcBezierCurve::is(v); }
Type::Enum IfcRationalBezierCurve::type() { return Type::IfcRationalBezierCurve; }
Type::Enum IfcRationalBezierCurve::Class() { return Type::IfcRationalBezierCurve; }
IfcRationalBezierCurve::IfcRationalBezierCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcRationalBezierCurve)) throw; entity = e; } 
// IfcRectangleHollowProfileDef
IfcPositiveLengthMeasure IfcRectangleHollowProfileDef::WallThickness() { return *entity->getArgument(5); }
bool IfcRectangleHollowProfileDef::hasInnerFilletRadius() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcRectangleHollowProfileDef::InnerFilletRadius() { return *entity->getArgument(6); }
bool IfcRectangleHollowProfileDef::hasOuterFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcRectangleHollowProfileDef::OuterFilletRadius() { return *entity->getArgument(7); }
bool IfcRectangleHollowProfileDef::is(Type::Enum v) { return v == Type::IfcRectangleHollowProfileDef || IfcRectangleProfileDef::is(v); }
Type::Enum IfcRectangleHollowProfileDef::type() { return Type::IfcRectangleHollowProfileDef; }
Type::Enum IfcRectangleHollowProfileDef::Class() { return Type::IfcRectangleHollowProfileDef; }
IfcRectangleHollowProfileDef::IfcRectangleHollowProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangleHollowProfileDef)) throw; entity = e; } 
// IfcRectangleProfileDef
IfcPositiveLengthMeasure IfcRectangleProfileDef::XDim() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcRectangleProfileDef::YDim() { return *entity->getArgument(4); }
bool IfcRectangleProfileDef::is(Type::Enum v) { return v == Type::IfcRectangleProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcRectangleProfileDef::type() { return Type::IfcRectangleProfileDef; }
Type::Enum IfcRectangleProfileDef::Class() { return Type::IfcRectangleProfileDef; }
IfcRectangleProfileDef::IfcRectangleProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangleProfileDef)) throw; entity = e; } 
// IfcRectangularPyramid
IfcPositiveLengthMeasure IfcRectangularPyramid::XLength() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcRectangularPyramid::YLength() { return *entity->getArgument(2); }
IfcPositiveLengthMeasure IfcRectangularPyramid::Height() { return *entity->getArgument(3); }
bool IfcRectangularPyramid::is(Type::Enum v) { return v == Type::IfcRectangularPyramid || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcRectangularPyramid::type() { return Type::IfcRectangularPyramid; }
Type::Enum IfcRectangularPyramid::Class() { return Type::IfcRectangularPyramid; }
IfcRectangularPyramid::IfcRectangularPyramid(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangularPyramid)) throw; entity = e; } 
// IfcRectangularTrimmedSurface
SHARED_PTR<IfcSurface> IfcRectangularTrimmedSurface::BasisSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(0)); }
IfcParameterValue IfcRectangularTrimmedSurface::U1() { return *entity->getArgument(1); }
IfcParameterValue IfcRectangularTrimmedSurface::V1() { return *entity->getArgument(2); }
IfcParameterValue IfcRectangularTrimmedSurface::U2() { return *entity->getArgument(3); }
IfcParameterValue IfcRectangularTrimmedSurface::V2() { return *entity->getArgument(4); }
bool IfcRectangularTrimmedSurface::Usense() { return *entity->getArgument(5); }
bool IfcRectangularTrimmedSurface::Vsense() { return *entity->getArgument(6); }
bool IfcRectangularTrimmedSurface::is(Type::Enum v) { return v == Type::IfcRectangularTrimmedSurface || IfcBoundedSurface::is(v); }
Type::Enum IfcRectangularTrimmedSurface::type() { return Type::IfcRectangularTrimmedSurface; }
Type::Enum IfcRectangularTrimmedSurface::Class() { return Type::IfcRectangularTrimmedSurface; }
IfcRectangularTrimmedSurface::IfcRectangularTrimmedSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcRectangularTrimmedSurface)) throw; entity = e; } 
// IfcReferencesValueDocument
IfcDocumentSelect IfcReferencesValueDocument::ReferencedDocument() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAppliedValue> > IfcReferencesValueDocument::ReferencingValues() { RETURN_AS_LIST(IfcAppliedValue,1) }
bool IfcReferencesValueDocument::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcReferencesValueDocument::Name() { return *entity->getArgument(2); }
bool IfcReferencesValueDocument::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcReferencesValueDocument::Description() { return *entity->getArgument(3); }
bool IfcReferencesValueDocument::is(Type::Enum v) { return v == Type::IfcReferencesValueDocument; }
Type::Enum IfcReferencesValueDocument::type() { return Type::IfcReferencesValueDocument; }
Type::Enum IfcReferencesValueDocument::Class() { return Type::IfcReferencesValueDocument; }
IfcReferencesValueDocument::IfcReferencesValueDocument(IfcAbstractEntityPtr e) { if (!is(Type::IfcReferencesValueDocument)) throw; entity = e; } 
// IfcRegularTimeSeries
IfcTimeMeasure IfcRegularTimeSeries::TimeStep() { return *entity->getArgument(8); }
SHARED_PTR< IfcTemplatedEntityList<IfcTimeSeriesValue> > IfcRegularTimeSeries::Values() { RETURN_AS_LIST(IfcTimeSeriesValue,9) }
bool IfcRegularTimeSeries::is(Type::Enum v) { return v == Type::IfcRegularTimeSeries || IfcTimeSeries::is(v); }
Type::Enum IfcRegularTimeSeries::type() { return Type::IfcRegularTimeSeries; }
Type::Enum IfcRegularTimeSeries::Class() { return Type::IfcRegularTimeSeries; }
IfcRegularTimeSeries::IfcRegularTimeSeries(IfcAbstractEntityPtr e) { if (!is(Type::IfcRegularTimeSeries)) throw; entity = e; } 
// IfcReinforcementBarProperties
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
bool IfcReinforcementBarProperties::is(Type::Enum v) { return v == Type::IfcReinforcementBarProperties; }
Type::Enum IfcReinforcementBarProperties::type() { return Type::IfcReinforcementBarProperties; }
Type::Enum IfcReinforcementBarProperties::Class() { return Type::IfcReinforcementBarProperties; }
IfcReinforcementBarProperties::IfcReinforcementBarProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcementBarProperties)) throw; entity = e; } 
// IfcReinforcementDefinitionProperties
bool IfcReinforcementDefinitionProperties::hasDefinitionType() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcReinforcementDefinitionProperties::DefinitionType() { return *entity->getArgument(4); }
SHARED_PTR< IfcTemplatedEntityList<IfcSectionReinforcementProperties> > IfcReinforcementDefinitionProperties::ReinforcementSectionDefinitions() { RETURN_AS_LIST(IfcSectionReinforcementProperties,5) }
bool IfcReinforcementDefinitionProperties::is(Type::Enum v) { return v == Type::IfcReinforcementDefinitionProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcReinforcementDefinitionProperties::type() { return Type::IfcReinforcementDefinitionProperties; }
Type::Enum IfcReinforcementDefinitionProperties::Class() { return Type::IfcReinforcementDefinitionProperties; }
IfcReinforcementDefinitionProperties::IfcReinforcementDefinitionProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcementDefinitionProperties)) throw; entity = e; } 
// IfcReinforcingBar
IfcPositiveLengthMeasure IfcReinforcingBar::NominalDiameter() { return *entity->getArgument(9); }
IfcAreaMeasure IfcReinforcingBar::CrossSectionArea() { return *entity->getArgument(10); }
bool IfcReinforcingBar::hasBarLength() { return !entity->getArgument(11)->isNull(); }
IfcPositiveLengthMeasure IfcReinforcingBar::BarLength() { return *entity->getArgument(11); }
IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum IfcReinforcingBar::BarRole() { return IfcReinforcingBarRoleEnum::FromString(*entity->getArgument(12)); }
bool IfcReinforcingBar::hasBarSurface() { return !entity->getArgument(13)->isNull(); }
IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum IfcReinforcingBar::BarSurface() { return IfcReinforcingBarSurfaceEnum::FromString(*entity->getArgument(13)); }
bool IfcReinforcingBar::is(Type::Enum v) { return v == Type::IfcReinforcingBar || IfcReinforcingElement::is(v); }
Type::Enum IfcReinforcingBar::type() { return Type::IfcReinforcingBar; }
Type::Enum IfcReinforcingBar::Class() { return Type::IfcReinforcingBar; }
IfcReinforcingBar::IfcReinforcingBar(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcingBar)) throw; entity = e; } 
// IfcReinforcingElement
bool IfcReinforcingElement::hasSteelGrade() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcReinforcingElement::SteelGrade() { return *entity->getArgument(8); }
bool IfcReinforcingElement::is(Type::Enum v) { return v == Type::IfcReinforcingElement || IfcBuildingElementComponent::is(v); }
Type::Enum IfcReinforcingElement::type() { return Type::IfcReinforcingElement; }
Type::Enum IfcReinforcingElement::Class() { return Type::IfcReinforcingElement; }
IfcReinforcingElement::IfcReinforcingElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcingElement)) throw; entity = e; } 
// IfcReinforcingMesh
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
bool IfcReinforcingMesh::is(Type::Enum v) { return v == Type::IfcReinforcingMesh || IfcReinforcingElement::is(v); }
Type::Enum IfcReinforcingMesh::type() { return Type::IfcReinforcingMesh; }
Type::Enum IfcReinforcingMesh::Class() { return Type::IfcReinforcingMesh; }
IfcReinforcingMesh::IfcReinforcingMesh(IfcAbstractEntityPtr e) { if (!is(Type::IfcReinforcingMesh)) throw; entity = e; } 
// IfcRelAggregates
bool IfcRelAggregates::is(Type::Enum v) { return v == Type::IfcRelAggregates || IfcRelDecomposes::is(v); }
Type::Enum IfcRelAggregates::type() { return Type::IfcRelAggregates; }
Type::Enum IfcRelAggregates::Class() { return Type::IfcRelAggregates; }
IfcRelAggregates::IfcRelAggregates(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAggregates)) throw; entity = e; } 
// IfcRelAssigns
SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > IfcRelAssigns::RelatedObjects() { RETURN_AS_LIST(IfcObjectDefinition,4) }
bool IfcRelAssigns::hasRelatedObjectsType() { return !entity->getArgument(5)->isNull(); }
IfcObjectTypeEnum::IfcObjectTypeEnum IfcRelAssigns::RelatedObjectsType() { return IfcObjectTypeEnum::FromString(*entity->getArgument(5)); }
bool IfcRelAssigns::is(Type::Enum v) { return v == Type::IfcRelAssigns || IfcRelationship::is(v); }
Type::Enum IfcRelAssigns::type() { return Type::IfcRelAssigns; }
Type::Enum IfcRelAssigns::Class() { return Type::IfcRelAssigns; }
IfcRelAssigns::IfcRelAssigns(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssigns)) throw; entity = e; } 
// IfcRelAssignsTasks
bool IfcRelAssignsTasks::hasTimeForTask() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR<IfcScheduleTimeControl> IfcRelAssignsTasks::TimeForTask() { return reinterpret_pointer_cast<IfcBaseClass,IfcScheduleTimeControl>(*entity->getArgument(7)); }
bool IfcRelAssignsTasks::is(Type::Enum v) { return v == Type::IfcRelAssignsTasks || IfcRelAssignsToControl::is(v); }
Type::Enum IfcRelAssignsTasks::type() { return Type::IfcRelAssignsTasks; }
Type::Enum IfcRelAssignsTasks::Class() { return Type::IfcRelAssignsTasks; }
IfcRelAssignsTasks::IfcRelAssignsTasks(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsTasks)) throw; entity = e; } 
// IfcRelAssignsToActor
SHARED_PTR<IfcActor> IfcRelAssignsToActor::RelatingActor() { return reinterpret_pointer_cast<IfcBaseClass,IfcActor>(*entity->getArgument(6)); }
bool IfcRelAssignsToActor::hasActingRole() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR<IfcActorRole> IfcRelAssignsToActor::ActingRole() { return reinterpret_pointer_cast<IfcBaseClass,IfcActorRole>(*entity->getArgument(7)); }
bool IfcRelAssignsToActor::is(Type::Enum v) { return v == Type::IfcRelAssignsToActor || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToActor::type() { return Type::IfcRelAssignsToActor; }
Type::Enum IfcRelAssignsToActor::Class() { return Type::IfcRelAssignsToActor; }
IfcRelAssignsToActor::IfcRelAssignsToActor(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToActor)) throw; entity = e; } 
// IfcRelAssignsToControl
SHARED_PTR<IfcControl> IfcRelAssignsToControl::RelatingControl() { return reinterpret_pointer_cast<IfcBaseClass,IfcControl>(*entity->getArgument(6)); }
bool IfcRelAssignsToControl::is(Type::Enum v) { return v == Type::IfcRelAssignsToControl || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToControl::type() { return Type::IfcRelAssignsToControl; }
Type::Enum IfcRelAssignsToControl::Class() { return Type::IfcRelAssignsToControl; }
IfcRelAssignsToControl::IfcRelAssignsToControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToControl)) throw; entity = e; } 
// IfcRelAssignsToGroup
SHARED_PTR<IfcGroup> IfcRelAssignsToGroup::RelatingGroup() { return reinterpret_pointer_cast<IfcBaseClass,IfcGroup>(*entity->getArgument(6)); }
bool IfcRelAssignsToGroup::is(Type::Enum v) { return v == Type::IfcRelAssignsToGroup || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToGroup::type() { return Type::IfcRelAssignsToGroup; }
Type::Enum IfcRelAssignsToGroup::Class() { return Type::IfcRelAssignsToGroup; }
IfcRelAssignsToGroup::IfcRelAssignsToGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToGroup)) throw; entity = e; } 
// IfcRelAssignsToProcess
SHARED_PTR<IfcProcess> IfcRelAssignsToProcess::RelatingProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcProcess>(*entity->getArgument(6)); }
bool IfcRelAssignsToProcess::hasQuantityInProcess() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR<IfcMeasureWithUnit> IfcRelAssignsToProcess::QuantityInProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcMeasureWithUnit>(*entity->getArgument(7)); }
bool IfcRelAssignsToProcess::is(Type::Enum v) { return v == Type::IfcRelAssignsToProcess || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToProcess::type() { return Type::IfcRelAssignsToProcess; }
Type::Enum IfcRelAssignsToProcess::Class() { return Type::IfcRelAssignsToProcess; }
IfcRelAssignsToProcess::IfcRelAssignsToProcess(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToProcess)) throw; entity = e; } 
// IfcRelAssignsToProduct
SHARED_PTR<IfcProduct> IfcRelAssignsToProduct::RelatingProduct() { return reinterpret_pointer_cast<IfcBaseClass,IfcProduct>(*entity->getArgument(6)); }
bool IfcRelAssignsToProduct::is(Type::Enum v) { return v == Type::IfcRelAssignsToProduct || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToProduct::type() { return Type::IfcRelAssignsToProduct; }
Type::Enum IfcRelAssignsToProduct::Class() { return Type::IfcRelAssignsToProduct; }
IfcRelAssignsToProduct::IfcRelAssignsToProduct(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToProduct)) throw; entity = e; } 
// IfcRelAssignsToProjectOrder
bool IfcRelAssignsToProjectOrder::is(Type::Enum v) { return v == Type::IfcRelAssignsToProjectOrder || IfcRelAssignsToControl::is(v); }
Type::Enum IfcRelAssignsToProjectOrder::type() { return Type::IfcRelAssignsToProjectOrder; }
Type::Enum IfcRelAssignsToProjectOrder::Class() { return Type::IfcRelAssignsToProjectOrder; }
IfcRelAssignsToProjectOrder::IfcRelAssignsToProjectOrder(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToProjectOrder)) throw; entity = e; } 
// IfcRelAssignsToResource
SHARED_PTR<IfcResource> IfcRelAssignsToResource::RelatingResource() { return reinterpret_pointer_cast<IfcBaseClass,IfcResource>(*entity->getArgument(6)); }
bool IfcRelAssignsToResource::is(Type::Enum v) { return v == Type::IfcRelAssignsToResource || IfcRelAssigns::is(v); }
Type::Enum IfcRelAssignsToResource::type() { return Type::IfcRelAssignsToResource; }
Type::Enum IfcRelAssignsToResource::Class() { return Type::IfcRelAssignsToResource; }
IfcRelAssignsToResource::IfcRelAssignsToResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssignsToResource)) throw; entity = e; } 
// IfcRelAssociates
SHARED_PTR< IfcTemplatedEntityList<IfcRoot> > IfcRelAssociates::RelatedObjects() { RETURN_AS_LIST(IfcRoot,4) }
bool IfcRelAssociates::is(Type::Enum v) { return v == Type::IfcRelAssociates || IfcRelationship::is(v); }
Type::Enum IfcRelAssociates::type() { return Type::IfcRelAssociates; }
Type::Enum IfcRelAssociates::Class() { return Type::IfcRelAssociates; }
IfcRelAssociates::IfcRelAssociates(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociates)) throw; entity = e; } 
// IfcRelAssociatesAppliedValue
SHARED_PTR<IfcAppliedValue> IfcRelAssociatesAppliedValue::RelatingAppliedValue() { return reinterpret_pointer_cast<IfcBaseClass,IfcAppliedValue>(*entity->getArgument(5)); }
bool IfcRelAssociatesAppliedValue::is(Type::Enum v) { return v == Type::IfcRelAssociatesAppliedValue || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesAppliedValue::type() { return Type::IfcRelAssociatesAppliedValue; }
Type::Enum IfcRelAssociatesAppliedValue::Class() { return Type::IfcRelAssociatesAppliedValue; }
IfcRelAssociatesAppliedValue::IfcRelAssociatesAppliedValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesAppliedValue)) throw; entity = e; } 
// IfcRelAssociatesApproval
SHARED_PTR<IfcApproval> IfcRelAssociatesApproval::RelatingApproval() { return reinterpret_pointer_cast<IfcBaseClass,IfcApproval>(*entity->getArgument(5)); }
bool IfcRelAssociatesApproval::is(Type::Enum v) { return v == Type::IfcRelAssociatesApproval || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesApproval::type() { return Type::IfcRelAssociatesApproval; }
Type::Enum IfcRelAssociatesApproval::Class() { return Type::IfcRelAssociatesApproval; }
IfcRelAssociatesApproval::IfcRelAssociatesApproval(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesApproval)) throw; entity = e; } 
// IfcRelAssociatesClassification
IfcClassificationNotationSelect IfcRelAssociatesClassification::RelatingClassification() { return *entity->getArgument(5); }
bool IfcRelAssociatesClassification::is(Type::Enum v) { return v == Type::IfcRelAssociatesClassification || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesClassification::type() { return Type::IfcRelAssociatesClassification; }
Type::Enum IfcRelAssociatesClassification::Class() { return Type::IfcRelAssociatesClassification; }
IfcRelAssociatesClassification::IfcRelAssociatesClassification(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesClassification)) throw; entity = e; } 
// IfcRelAssociatesConstraint
IfcLabel IfcRelAssociatesConstraint::Intent() { return *entity->getArgument(5); }
SHARED_PTR<IfcConstraint> IfcRelAssociatesConstraint::RelatingConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConstraint>(*entity->getArgument(6)); }
bool IfcRelAssociatesConstraint::is(Type::Enum v) { return v == Type::IfcRelAssociatesConstraint || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesConstraint::type() { return Type::IfcRelAssociatesConstraint; }
Type::Enum IfcRelAssociatesConstraint::Class() { return Type::IfcRelAssociatesConstraint; }
IfcRelAssociatesConstraint::IfcRelAssociatesConstraint(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesConstraint)) throw; entity = e; } 
// IfcRelAssociatesDocument
IfcDocumentSelect IfcRelAssociatesDocument::RelatingDocument() { return *entity->getArgument(5); }
bool IfcRelAssociatesDocument::is(Type::Enum v) { return v == Type::IfcRelAssociatesDocument || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesDocument::type() { return Type::IfcRelAssociatesDocument; }
Type::Enum IfcRelAssociatesDocument::Class() { return Type::IfcRelAssociatesDocument; }
IfcRelAssociatesDocument::IfcRelAssociatesDocument(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesDocument)) throw; entity = e; } 
// IfcRelAssociatesLibrary
IfcLibrarySelect IfcRelAssociatesLibrary::RelatingLibrary() { return *entity->getArgument(5); }
bool IfcRelAssociatesLibrary::is(Type::Enum v) { return v == Type::IfcRelAssociatesLibrary || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesLibrary::type() { return Type::IfcRelAssociatesLibrary; }
Type::Enum IfcRelAssociatesLibrary::Class() { return Type::IfcRelAssociatesLibrary; }
IfcRelAssociatesLibrary::IfcRelAssociatesLibrary(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesLibrary)) throw; entity = e; } 
// IfcRelAssociatesMaterial
IfcMaterialSelect IfcRelAssociatesMaterial::RelatingMaterial() { return *entity->getArgument(5); }
bool IfcRelAssociatesMaterial::is(Type::Enum v) { return v == Type::IfcRelAssociatesMaterial || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesMaterial::type() { return Type::IfcRelAssociatesMaterial; }
Type::Enum IfcRelAssociatesMaterial::Class() { return Type::IfcRelAssociatesMaterial; }
IfcRelAssociatesMaterial::IfcRelAssociatesMaterial(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesMaterial)) throw; entity = e; } 
// IfcRelAssociatesProfileProperties
SHARED_PTR<IfcProfileProperties> IfcRelAssociatesProfileProperties::RelatingProfileProperties() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileProperties>(*entity->getArgument(5)); }
bool IfcRelAssociatesProfileProperties::hasProfileSectionLocation() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcShapeAspect> IfcRelAssociatesProfileProperties::ProfileSectionLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(6)); }
bool IfcRelAssociatesProfileProperties::hasProfileOrientation() { return !entity->getArgument(7)->isNull(); }
IfcOrientationSelect IfcRelAssociatesProfileProperties::ProfileOrientation() { return *entity->getArgument(7); }
bool IfcRelAssociatesProfileProperties::is(Type::Enum v) { return v == Type::IfcRelAssociatesProfileProperties || IfcRelAssociates::is(v); }
Type::Enum IfcRelAssociatesProfileProperties::type() { return Type::IfcRelAssociatesProfileProperties; }
Type::Enum IfcRelAssociatesProfileProperties::Class() { return Type::IfcRelAssociatesProfileProperties; }
IfcRelAssociatesProfileProperties::IfcRelAssociatesProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelAssociatesProfileProperties)) throw; entity = e; } 
// IfcRelConnects
bool IfcRelConnects::is(Type::Enum v) { return v == Type::IfcRelConnects || IfcRelationship::is(v); }
Type::Enum IfcRelConnects::type() { return Type::IfcRelConnects; }
Type::Enum IfcRelConnects::Class() { return Type::IfcRelConnects; }
IfcRelConnects::IfcRelConnects(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnects)) throw; entity = e; } 
// IfcRelConnectsElements
bool IfcRelConnectsElements::hasConnectionGeometry() { return !entity->getArgument(4)->isNull(); }
SHARED_PTR<IfcConnectionGeometry> IfcRelConnectsElements::ConnectionGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcConnectionGeometry>(*entity->getArgument(4)); }
SHARED_PTR<IfcElement> IfcRelConnectsElements::RelatingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
SHARED_PTR<IfcElement> IfcRelConnectsElements::RelatedElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(6)); }
bool IfcRelConnectsElements::is(Type::Enum v) { return v == Type::IfcRelConnectsElements || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsElements::type() { return Type::IfcRelConnectsElements; }
Type::Enum IfcRelConnectsElements::Class() { return Type::IfcRelConnectsElements; }
IfcRelConnectsElements::IfcRelConnectsElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsElements)) throw; entity = e; } 
// IfcRelConnectsPathElements
std::vector<int> /*[0:?]*/ IfcRelConnectsPathElements::RelatingPriorities() { return *entity->getArgument(7); }
std::vector<int> /*[0:?]*/ IfcRelConnectsPathElements::RelatedPriorities() { return *entity->getArgument(8); }
IfcConnectionTypeEnum::IfcConnectionTypeEnum IfcRelConnectsPathElements::RelatedConnectionType() { return IfcConnectionTypeEnum::FromString(*entity->getArgument(9)); }
IfcConnectionTypeEnum::IfcConnectionTypeEnum IfcRelConnectsPathElements::RelatingConnectionType() { return IfcConnectionTypeEnum::FromString(*entity->getArgument(10)); }
bool IfcRelConnectsPathElements::is(Type::Enum v) { return v == Type::IfcRelConnectsPathElements || IfcRelConnectsElements::is(v); }
Type::Enum IfcRelConnectsPathElements::type() { return Type::IfcRelConnectsPathElements; }
Type::Enum IfcRelConnectsPathElements::Class() { return Type::IfcRelConnectsPathElements; }
IfcRelConnectsPathElements::IfcRelConnectsPathElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsPathElements)) throw; entity = e; } 
// IfcRelConnectsPortToElement
SHARED_PTR<IfcPort> IfcRelConnectsPortToElement::RelatingPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcPort>(*entity->getArgument(4)); }
SHARED_PTR<IfcElement> IfcRelConnectsPortToElement::RelatedElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
bool IfcRelConnectsPortToElement::is(Type::Enum v) { return v == Type::IfcRelConnectsPortToElement || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsPortToElement::type() { return Type::IfcRelConnectsPortToElement; }
Type::Enum IfcRelConnectsPortToElement::Class() { return Type::IfcRelConnectsPortToElement; }
IfcRelConnectsPortToElement::IfcRelConnectsPortToElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsPortToElement)) throw; entity = e; } 
// IfcRelConnectsPorts
SHARED_PTR<IfcPort> IfcRelConnectsPorts::RelatingPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcPort>(*entity->getArgument(4)); }
SHARED_PTR<IfcPort> IfcRelConnectsPorts::RelatedPort() { return reinterpret_pointer_cast<IfcBaseClass,IfcPort>(*entity->getArgument(5)); }
bool IfcRelConnectsPorts::hasRealizingElement() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcElement> IfcRelConnectsPorts::RealizingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(6)); }
bool IfcRelConnectsPorts::is(Type::Enum v) { return v == Type::IfcRelConnectsPorts || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsPorts::type() { return Type::IfcRelConnectsPorts; }
Type::Enum IfcRelConnectsPorts::Class() { return Type::IfcRelConnectsPorts; }
IfcRelConnectsPorts::IfcRelConnectsPorts(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsPorts)) throw; entity = e; } 
// IfcRelConnectsStructuralActivity
IfcStructuralActivityAssignmentSelect IfcRelConnectsStructuralActivity::RelatingElement() { return *entity->getArgument(4); }
SHARED_PTR<IfcStructuralActivity> IfcRelConnectsStructuralActivity::RelatedStructuralActivity() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralActivity>(*entity->getArgument(5)); }
bool IfcRelConnectsStructuralActivity::is(Type::Enum v) { return v == Type::IfcRelConnectsStructuralActivity || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsStructuralActivity::type() { return Type::IfcRelConnectsStructuralActivity; }
Type::Enum IfcRelConnectsStructuralActivity::Class() { return Type::IfcRelConnectsStructuralActivity; }
IfcRelConnectsStructuralActivity::IfcRelConnectsStructuralActivity(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsStructuralActivity)) throw; entity = e; } 
// IfcRelConnectsStructuralElement
SHARED_PTR<IfcElement> IfcRelConnectsStructuralElement::RelatingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
SHARED_PTR<IfcStructuralMember> IfcRelConnectsStructuralElement::RelatedStructuralMember() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralMember>(*entity->getArgument(5)); }
bool IfcRelConnectsStructuralElement::is(Type::Enum v) { return v == Type::IfcRelConnectsStructuralElement || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsStructuralElement::type() { return Type::IfcRelConnectsStructuralElement; }
Type::Enum IfcRelConnectsStructuralElement::Class() { return Type::IfcRelConnectsStructuralElement; }
IfcRelConnectsStructuralElement::IfcRelConnectsStructuralElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsStructuralElement)) throw; entity = e; } 
// IfcRelConnectsStructuralMember
SHARED_PTR<IfcStructuralMember> IfcRelConnectsStructuralMember::RelatingStructuralMember() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralMember>(*entity->getArgument(4)); }
SHARED_PTR<IfcStructuralConnection> IfcRelConnectsStructuralMember::RelatedStructuralConnection() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralConnection>(*entity->getArgument(5)); }
bool IfcRelConnectsStructuralMember::hasAppliedCondition() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcBoundaryCondition> IfcRelConnectsStructuralMember::AppliedCondition() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundaryCondition>(*entity->getArgument(6)); }
bool IfcRelConnectsStructuralMember::hasAdditionalConditions() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR<IfcStructuralConnectionCondition> IfcRelConnectsStructuralMember::AdditionalConditions() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralConnectionCondition>(*entity->getArgument(7)); }
bool IfcRelConnectsStructuralMember::hasSupportedLength() { return !entity->getArgument(8)->isNull(); }
IfcLengthMeasure IfcRelConnectsStructuralMember::SupportedLength() { return *entity->getArgument(8); }
bool IfcRelConnectsStructuralMember::hasConditionCoordinateSystem() { return !entity->getArgument(9)->isNull(); }
SHARED_PTR<IfcAxis2Placement3D> IfcRelConnectsStructuralMember::ConditionCoordinateSystem() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(9)); }
bool IfcRelConnectsStructuralMember::is(Type::Enum v) { return v == Type::IfcRelConnectsStructuralMember || IfcRelConnects::is(v); }
Type::Enum IfcRelConnectsStructuralMember::type() { return Type::IfcRelConnectsStructuralMember; }
Type::Enum IfcRelConnectsStructuralMember::Class() { return Type::IfcRelConnectsStructuralMember; }
IfcRelConnectsStructuralMember::IfcRelConnectsStructuralMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsStructuralMember)) throw; entity = e; } 
// IfcRelConnectsWithEccentricity
SHARED_PTR<IfcConnectionGeometry> IfcRelConnectsWithEccentricity::ConnectionConstraint() { return reinterpret_pointer_cast<IfcBaseClass,IfcConnectionGeometry>(*entity->getArgument(10)); }
bool IfcRelConnectsWithEccentricity::is(Type::Enum v) { return v == Type::IfcRelConnectsWithEccentricity || IfcRelConnectsStructuralMember::is(v); }
Type::Enum IfcRelConnectsWithEccentricity::type() { return Type::IfcRelConnectsWithEccentricity; }
Type::Enum IfcRelConnectsWithEccentricity::Class() { return Type::IfcRelConnectsWithEccentricity; }
IfcRelConnectsWithEccentricity::IfcRelConnectsWithEccentricity(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsWithEccentricity)) throw; entity = e; } 
// IfcRelConnectsWithRealizingElements
SHARED_PTR< IfcTemplatedEntityList<IfcElement> > IfcRelConnectsWithRealizingElements::RealizingElements() { RETURN_AS_LIST(IfcElement,7) }
bool IfcRelConnectsWithRealizingElements::hasConnectionType() { return !entity->getArgument(8)->isNull(); }
IfcLabel IfcRelConnectsWithRealizingElements::ConnectionType() { return *entity->getArgument(8); }
bool IfcRelConnectsWithRealizingElements::is(Type::Enum v) { return v == Type::IfcRelConnectsWithRealizingElements || IfcRelConnectsElements::is(v); }
Type::Enum IfcRelConnectsWithRealizingElements::type() { return Type::IfcRelConnectsWithRealizingElements; }
Type::Enum IfcRelConnectsWithRealizingElements::Class() { return Type::IfcRelConnectsWithRealizingElements; }
IfcRelConnectsWithRealizingElements::IfcRelConnectsWithRealizingElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelConnectsWithRealizingElements)) throw; entity = e; } 
// IfcRelContainedInSpatialStructure
SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > IfcRelContainedInSpatialStructure::RelatedElements() { RETURN_AS_LIST(IfcProduct,4) }
SHARED_PTR<IfcSpatialStructureElement> IfcRelContainedInSpatialStructure::RelatingStructure() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(5)); }
bool IfcRelContainedInSpatialStructure::is(Type::Enum v) { return v == Type::IfcRelContainedInSpatialStructure || IfcRelConnects::is(v); }
Type::Enum IfcRelContainedInSpatialStructure::type() { return Type::IfcRelContainedInSpatialStructure; }
Type::Enum IfcRelContainedInSpatialStructure::Class() { return Type::IfcRelContainedInSpatialStructure; }
IfcRelContainedInSpatialStructure::IfcRelContainedInSpatialStructure(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelContainedInSpatialStructure)) throw; entity = e; } 
// IfcRelCoversBldgElements
SHARED_PTR<IfcElement> IfcRelCoversBldgElements::RelatingBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > IfcRelCoversBldgElements::RelatedCoverings() { RETURN_AS_LIST(IfcCovering,5) }
bool IfcRelCoversBldgElements::is(Type::Enum v) { return v == Type::IfcRelCoversBldgElements || IfcRelConnects::is(v); }
Type::Enum IfcRelCoversBldgElements::type() { return Type::IfcRelCoversBldgElements; }
Type::Enum IfcRelCoversBldgElements::Class() { return Type::IfcRelCoversBldgElements; }
IfcRelCoversBldgElements::IfcRelCoversBldgElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelCoversBldgElements)) throw; entity = e; } 
// IfcRelCoversSpaces
SHARED_PTR<IfcSpace> IfcRelCoversSpaces::RelatedSpace() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpace>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcCovering> > IfcRelCoversSpaces::RelatedCoverings() { RETURN_AS_LIST(IfcCovering,5) }
bool IfcRelCoversSpaces::is(Type::Enum v) { return v == Type::IfcRelCoversSpaces || IfcRelConnects::is(v); }
Type::Enum IfcRelCoversSpaces::type() { return Type::IfcRelCoversSpaces; }
Type::Enum IfcRelCoversSpaces::Class() { return Type::IfcRelCoversSpaces; }
IfcRelCoversSpaces::IfcRelCoversSpaces(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelCoversSpaces)) throw; entity = e; } 
// IfcRelDecomposes
SHARED_PTR<IfcObjectDefinition> IfcRelDecomposes::RelatingObject() { return reinterpret_pointer_cast<IfcBaseClass,IfcObjectDefinition>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcObjectDefinition> > IfcRelDecomposes::RelatedObjects() { RETURN_AS_LIST(IfcObjectDefinition,5) }
bool IfcRelDecomposes::is(Type::Enum v) { return v == Type::IfcRelDecomposes || IfcRelationship::is(v); }
Type::Enum IfcRelDecomposes::type() { return Type::IfcRelDecomposes; }
Type::Enum IfcRelDecomposes::Class() { return Type::IfcRelDecomposes; }
IfcRelDecomposes::IfcRelDecomposes(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDecomposes)) throw; entity = e; } 
// IfcRelDefines
SHARED_PTR< IfcTemplatedEntityList<IfcObject> > IfcRelDefines::RelatedObjects() { RETURN_AS_LIST(IfcObject,4) }
bool IfcRelDefines::is(Type::Enum v) { return v == Type::IfcRelDefines || IfcRelationship::is(v); }
Type::Enum IfcRelDefines::type() { return Type::IfcRelDefines; }
Type::Enum IfcRelDefines::Class() { return Type::IfcRelDefines; }
IfcRelDefines::IfcRelDefines(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDefines)) throw; entity = e; } 
// IfcRelDefinesByProperties
SHARED_PTR<IfcPropertySetDefinition> IfcRelDefinesByProperties::RelatingPropertyDefinition() { return reinterpret_pointer_cast<IfcBaseClass,IfcPropertySetDefinition>(*entity->getArgument(5)); }
bool IfcRelDefinesByProperties::is(Type::Enum v) { return v == Type::IfcRelDefinesByProperties || IfcRelDefines::is(v); }
Type::Enum IfcRelDefinesByProperties::type() { return Type::IfcRelDefinesByProperties; }
Type::Enum IfcRelDefinesByProperties::Class() { return Type::IfcRelDefinesByProperties; }
IfcRelDefinesByProperties::IfcRelDefinesByProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDefinesByProperties)) throw; entity = e; } 
// IfcRelDefinesByType
SHARED_PTR<IfcTypeObject> IfcRelDefinesByType::RelatingType() { return reinterpret_pointer_cast<IfcBaseClass,IfcTypeObject>(*entity->getArgument(5)); }
bool IfcRelDefinesByType::is(Type::Enum v) { return v == Type::IfcRelDefinesByType || IfcRelDefines::is(v); }
Type::Enum IfcRelDefinesByType::type() { return Type::IfcRelDefinesByType; }
Type::Enum IfcRelDefinesByType::Class() { return Type::IfcRelDefinesByType; }
IfcRelDefinesByType::IfcRelDefinesByType(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelDefinesByType)) throw; entity = e; } 
// IfcRelFillsElement
SHARED_PTR<IfcOpeningElement> IfcRelFillsElement::RelatingOpeningElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcOpeningElement>(*entity->getArgument(4)); }
SHARED_PTR<IfcElement> IfcRelFillsElement::RelatedBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
bool IfcRelFillsElement::is(Type::Enum v) { return v == Type::IfcRelFillsElement || IfcRelConnects::is(v); }
Type::Enum IfcRelFillsElement::type() { return Type::IfcRelFillsElement; }
Type::Enum IfcRelFillsElement::Class() { return Type::IfcRelFillsElement; }
IfcRelFillsElement::IfcRelFillsElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelFillsElement)) throw; entity = e; } 
// IfcRelFlowControlElements
SHARED_PTR< IfcTemplatedEntityList<IfcDistributionControlElement> > IfcRelFlowControlElements::RelatedControlElements() { RETURN_AS_LIST(IfcDistributionControlElement,4) }
SHARED_PTR<IfcDistributionFlowElement> IfcRelFlowControlElements::RelatingFlowElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcDistributionFlowElement>(*entity->getArgument(5)); }
bool IfcRelFlowControlElements::is(Type::Enum v) { return v == Type::IfcRelFlowControlElements || IfcRelConnects::is(v); }
Type::Enum IfcRelFlowControlElements::type() { return Type::IfcRelFlowControlElements; }
Type::Enum IfcRelFlowControlElements::Class() { return Type::IfcRelFlowControlElements; }
IfcRelFlowControlElements::IfcRelFlowControlElements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelFlowControlElements)) throw; entity = e; } 
// IfcRelInteractionRequirements
bool IfcRelInteractionRequirements::hasDailyInteraction() { return !entity->getArgument(4)->isNull(); }
IfcCountMeasure IfcRelInteractionRequirements::DailyInteraction() { return *entity->getArgument(4); }
bool IfcRelInteractionRequirements::hasImportanceRating() { return !entity->getArgument(5)->isNull(); }
IfcNormalisedRatioMeasure IfcRelInteractionRequirements::ImportanceRating() { return *entity->getArgument(5); }
bool IfcRelInteractionRequirements::hasLocationOfInteraction() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcSpatialStructureElement> IfcRelInteractionRequirements::LocationOfInteraction() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(6)); }
SHARED_PTR<IfcSpaceProgram> IfcRelInteractionRequirements::RelatedSpaceProgram() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpaceProgram>(*entity->getArgument(7)); }
SHARED_PTR<IfcSpaceProgram> IfcRelInteractionRequirements::RelatingSpaceProgram() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpaceProgram>(*entity->getArgument(8)); }
bool IfcRelInteractionRequirements::is(Type::Enum v) { return v == Type::IfcRelInteractionRequirements || IfcRelConnects::is(v); }
Type::Enum IfcRelInteractionRequirements::type() { return Type::IfcRelInteractionRequirements; }
Type::Enum IfcRelInteractionRequirements::Class() { return Type::IfcRelInteractionRequirements; }
IfcRelInteractionRequirements::IfcRelInteractionRequirements(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelInteractionRequirements)) throw; entity = e; } 
// IfcRelNests
bool IfcRelNests::is(Type::Enum v) { return v == Type::IfcRelNests || IfcRelDecomposes::is(v); }
Type::Enum IfcRelNests::type() { return Type::IfcRelNests; }
Type::Enum IfcRelNests::Class() { return Type::IfcRelNests; }
IfcRelNests::IfcRelNests(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelNests)) throw; entity = e; } 
// IfcRelOccupiesSpaces
bool IfcRelOccupiesSpaces::is(Type::Enum v) { return v == Type::IfcRelOccupiesSpaces || IfcRelAssignsToActor::is(v); }
Type::Enum IfcRelOccupiesSpaces::type() { return Type::IfcRelOccupiesSpaces; }
Type::Enum IfcRelOccupiesSpaces::Class() { return Type::IfcRelOccupiesSpaces; }
IfcRelOccupiesSpaces::IfcRelOccupiesSpaces(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelOccupiesSpaces)) throw; entity = e; } 
// IfcRelOverridesProperties
SHARED_PTR< IfcTemplatedEntityList<IfcProperty> > IfcRelOverridesProperties::OverridingProperties() { RETURN_AS_LIST(IfcProperty,6) }
bool IfcRelOverridesProperties::is(Type::Enum v) { return v == Type::IfcRelOverridesProperties || IfcRelDefinesByProperties::is(v); }
Type::Enum IfcRelOverridesProperties::type() { return Type::IfcRelOverridesProperties; }
Type::Enum IfcRelOverridesProperties::Class() { return Type::IfcRelOverridesProperties; }
IfcRelOverridesProperties::IfcRelOverridesProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelOverridesProperties)) throw; entity = e; } 
// IfcRelProjectsElement
SHARED_PTR<IfcElement> IfcRelProjectsElement::RelatingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
SHARED_PTR<IfcFeatureElementAddition> IfcRelProjectsElement::RelatedFeatureElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcFeatureElementAddition>(*entity->getArgument(5)); }
bool IfcRelProjectsElement::is(Type::Enum v) { return v == Type::IfcRelProjectsElement || IfcRelConnects::is(v); }
Type::Enum IfcRelProjectsElement::type() { return Type::IfcRelProjectsElement; }
Type::Enum IfcRelProjectsElement::Class() { return Type::IfcRelProjectsElement; }
IfcRelProjectsElement::IfcRelProjectsElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelProjectsElement)) throw; entity = e; } 
// IfcRelReferencedInSpatialStructure
SHARED_PTR< IfcTemplatedEntityList<IfcProduct> > IfcRelReferencedInSpatialStructure::RelatedElements() { RETURN_AS_LIST(IfcProduct,4) }
SHARED_PTR<IfcSpatialStructureElement> IfcRelReferencedInSpatialStructure::RelatingStructure() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(5)); }
bool IfcRelReferencedInSpatialStructure::is(Type::Enum v) { return v == Type::IfcRelReferencedInSpatialStructure || IfcRelConnects::is(v); }
Type::Enum IfcRelReferencedInSpatialStructure::type() { return Type::IfcRelReferencedInSpatialStructure; }
Type::Enum IfcRelReferencedInSpatialStructure::Class() { return Type::IfcRelReferencedInSpatialStructure; }
IfcRelReferencedInSpatialStructure::IfcRelReferencedInSpatialStructure(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelReferencedInSpatialStructure)) throw; entity = e; } 
// IfcRelSchedulesCostItems
bool IfcRelSchedulesCostItems::is(Type::Enum v) { return v == Type::IfcRelSchedulesCostItems || IfcRelAssignsToControl::is(v); }
Type::Enum IfcRelSchedulesCostItems::type() { return Type::IfcRelSchedulesCostItems; }
Type::Enum IfcRelSchedulesCostItems::Class() { return Type::IfcRelSchedulesCostItems; }
IfcRelSchedulesCostItems::IfcRelSchedulesCostItems(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelSchedulesCostItems)) throw; entity = e; } 
// IfcRelSequence
SHARED_PTR<IfcProcess> IfcRelSequence::RelatingProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcProcess>(*entity->getArgument(4)); }
SHARED_PTR<IfcProcess> IfcRelSequence::RelatedProcess() { return reinterpret_pointer_cast<IfcBaseClass,IfcProcess>(*entity->getArgument(5)); }
IfcTimeMeasure IfcRelSequence::TimeLag() { return *entity->getArgument(6); }
IfcSequenceEnum::IfcSequenceEnum IfcRelSequence::SequenceType() { return IfcSequenceEnum::FromString(*entity->getArgument(7)); }
bool IfcRelSequence::is(Type::Enum v) { return v == Type::IfcRelSequence || IfcRelConnects::is(v); }
Type::Enum IfcRelSequence::type() { return Type::IfcRelSequence; }
Type::Enum IfcRelSequence::Class() { return Type::IfcRelSequence; }
IfcRelSequence::IfcRelSequence(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelSequence)) throw; entity = e; } 
// IfcRelServicesBuildings
SHARED_PTR<IfcSystem> IfcRelServicesBuildings::RelatingSystem() { return reinterpret_pointer_cast<IfcBaseClass,IfcSystem>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcSpatialStructureElement> > IfcRelServicesBuildings::RelatedBuildings() { RETURN_AS_LIST(IfcSpatialStructureElement,5) }
bool IfcRelServicesBuildings::is(Type::Enum v) { return v == Type::IfcRelServicesBuildings || IfcRelConnects::is(v); }
Type::Enum IfcRelServicesBuildings::type() { return Type::IfcRelServicesBuildings; }
Type::Enum IfcRelServicesBuildings::Class() { return Type::IfcRelServicesBuildings; }
IfcRelServicesBuildings::IfcRelServicesBuildings(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelServicesBuildings)) throw; entity = e; } 
// IfcRelSpaceBoundary
SHARED_PTR<IfcSpace> IfcRelSpaceBoundary::RelatingSpace() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpace>(*entity->getArgument(4)); }
bool IfcRelSpaceBoundary::hasRelatedBuildingElement() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR<IfcElement> IfcRelSpaceBoundary::RelatedBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(5)); }
bool IfcRelSpaceBoundary::hasConnectionGeometry() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcConnectionGeometry> IfcRelSpaceBoundary::ConnectionGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcConnectionGeometry>(*entity->getArgument(6)); }
IfcPhysicalOrVirtualEnum::IfcPhysicalOrVirtualEnum IfcRelSpaceBoundary::PhysicalOrVirtualBoundary() { return IfcPhysicalOrVirtualEnum::FromString(*entity->getArgument(7)); }
IfcInternalOrExternalEnum::IfcInternalOrExternalEnum IfcRelSpaceBoundary::InternalOrExternalBoundary() { return IfcInternalOrExternalEnum::FromString(*entity->getArgument(8)); }
bool IfcRelSpaceBoundary::is(Type::Enum v) { return v == Type::IfcRelSpaceBoundary || IfcRelConnects::is(v); }
Type::Enum IfcRelSpaceBoundary::type() { return Type::IfcRelSpaceBoundary; }
Type::Enum IfcRelSpaceBoundary::Class() { return Type::IfcRelSpaceBoundary; }
IfcRelSpaceBoundary::IfcRelSpaceBoundary(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelSpaceBoundary)) throw; entity = e; } 
// IfcRelVoidsElement
SHARED_PTR<IfcElement> IfcRelVoidsElement::RelatingBuildingElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcElement>(*entity->getArgument(4)); }
SHARED_PTR<IfcFeatureElementSubtraction> IfcRelVoidsElement::RelatedOpeningElement() { return reinterpret_pointer_cast<IfcBaseClass,IfcFeatureElementSubtraction>(*entity->getArgument(5)); }
bool IfcRelVoidsElement::is(Type::Enum v) { return v == Type::IfcRelVoidsElement || IfcRelConnects::is(v); }
Type::Enum IfcRelVoidsElement::type() { return Type::IfcRelVoidsElement; }
Type::Enum IfcRelVoidsElement::Class() { return Type::IfcRelVoidsElement; }
IfcRelVoidsElement::IfcRelVoidsElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelVoidsElement)) throw; entity = e; } 
// IfcRelationship
bool IfcRelationship::is(Type::Enum v) { return v == Type::IfcRelationship || IfcRoot::is(v); }
Type::Enum IfcRelationship::type() { return Type::IfcRelationship; }
Type::Enum IfcRelationship::Class() { return Type::IfcRelationship; }
IfcRelationship::IfcRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelationship)) throw; entity = e; } 
// IfcRelaxation
IfcNormalisedRatioMeasure IfcRelaxation::RelaxationValue() { return *entity->getArgument(0); }
IfcNormalisedRatioMeasure IfcRelaxation::InitialStress() { return *entity->getArgument(1); }
bool IfcRelaxation::is(Type::Enum v) { return v == Type::IfcRelaxation; }
Type::Enum IfcRelaxation::type() { return Type::IfcRelaxation; }
Type::Enum IfcRelaxation::Class() { return Type::IfcRelaxation; }
IfcRelaxation::IfcRelaxation(IfcAbstractEntityPtr e) { if (!is(Type::IfcRelaxation)) throw; entity = e; } 
// IfcRepresentation
SHARED_PTR<IfcRepresentationContext> IfcRepresentation::ContextOfItems() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentationContext>(*entity->getArgument(0)); }
bool IfcRepresentation::hasRepresentationIdentifier() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcRepresentation::RepresentationIdentifier() { return *entity->getArgument(1); }
bool IfcRepresentation::hasRepresentationType() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcRepresentation::RepresentationType() { return *entity->getArgument(2); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationItem> > IfcRepresentation::Items() { RETURN_AS_LIST(IfcRepresentationItem,3) }
IfcRepresentationMap::list IfcRepresentation::RepresentationMap() { RETURN_INVERSE(IfcRepresentationMap) }
IfcPresentationLayerAssignment::list IfcRepresentation::LayerAssignments() { RETURN_INVERSE(IfcPresentationLayerAssignment) }
IfcProductRepresentation::list IfcRepresentation::OfProductRepresentation() { RETURN_INVERSE(IfcProductRepresentation) }
bool IfcRepresentation::is(Type::Enum v) { return v == Type::IfcRepresentation; }
Type::Enum IfcRepresentation::type() { return Type::IfcRepresentation; }
Type::Enum IfcRepresentation::Class() { return Type::IfcRepresentation; }
IfcRepresentation::IfcRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentation)) throw; entity = e; } 
// IfcRepresentationContext
bool IfcRepresentationContext::hasContextIdentifier() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcRepresentationContext::ContextIdentifier() { return *entity->getArgument(0); }
bool IfcRepresentationContext::hasContextType() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcRepresentationContext::ContextType() { return *entity->getArgument(1); }
IfcRepresentation::list IfcRepresentationContext::RepresentationsInContext() { RETURN_INVERSE(IfcRepresentation) }
bool IfcRepresentationContext::is(Type::Enum v) { return v == Type::IfcRepresentationContext; }
Type::Enum IfcRepresentationContext::type() { return Type::IfcRepresentationContext; }
Type::Enum IfcRepresentationContext::Class() { return Type::IfcRepresentationContext; }
IfcRepresentationContext::IfcRepresentationContext(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentationContext)) throw; entity = e; } 
// IfcRepresentationItem
IfcPresentationLayerAssignment::list IfcRepresentationItem::LayerAssignments() { RETURN_INVERSE(IfcPresentationLayerAssignment) }
IfcStyledItem::list IfcRepresentationItem::StyledByItem() { RETURN_INVERSE(IfcStyledItem) }
bool IfcRepresentationItem::is(Type::Enum v) { return v == Type::IfcRepresentationItem; }
Type::Enum IfcRepresentationItem::type() { return Type::IfcRepresentationItem; }
Type::Enum IfcRepresentationItem::Class() { return Type::IfcRepresentationItem; }
IfcRepresentationItem::IfcRepresentationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentationItem)) throw; entity = e; } 
// IfcRepresentationMap
IfcAxis2Placement IfcRepresentationMap::MappingOrigin() { return *entity->getArgument(0); }
SHARED_PTR<IfcRepresentation> IfcRepresentationMap::MappedRepresentation() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentation>(*entity->getArgument(1)); }
IfcMappedItem::list IfcRepresentationMap::MapUsage() { RETURN_INVERSE(IfcMappedItem) }
bool IfcRepresentationMap::is(Type::Enum v) { return v == Type::IfcRepresentationMap; }
Type::Enum IfcRepresentationMap::type() { return Type::IfcRepresentationMap; }
Type::Enum IfcRepresentationMap::Class() { return Type::IfcRepresentationMap; }
IfcRepresentationMap::IfcRepresentationMap(IfcAbstractEntityPtr e) { if (!is(Type::IfcRepresentationMap)) throw; entity = e; } 
// IfcResource
IfcRelAssignsToResource::list IfcResource::ResourceOf() { RETURN_INVERSE(IfcRelAssignsToResource) }
bool IfcResource::is(Type::Enum v) { return v == Type::IfcResource || IfcObject::is(v); }
Type::Enum IfcResource::type() { return Type::IfcResource; }
Type::Enum IfcResource::Class() { return Type::IfcResource; }
IfcResource::IfcResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcResource)) throw; entity = e; } 
// IfcRevolvedAreaSolid
SHARED_PTR<IfcAxis1Placement> IfcRevolvedAreaSolid::Axis() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis1Placement>(*entity->getArgument(2)); }
IfcPlaneAngleMeasure IfcRevolvedAreaSolid::Angle() { return *entity->getArgument(3); }
bool IfcRevolvedAreaSolid::is(Type::Enum v) { return v == Type::IfcRevolvedAreaSolid || IfcSweptAreaSolid::is(v); }
Type::Enum IfcRevolvedAreaSolid::type() { return Type::IfcRevolvedAreaSolid; }
Type::Enum IfcRevolvedAreaSolid::Class() { return Type::IfcRevolvedAreaSolid; }
IfcRevolvedAreaSolid::IfcRevolvedAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcRevolvedAreaSolid)) throw; entity = e; } 
// IfcRibPlateProfileProperties
bool IfcRibPlateProfileProperties::hasThickness() { return !entity->getArgument(2)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::Thickness() { return *entity->getArgument(2); }
bool IfcRibPlateProfileProperties::hasRibHeight() { return !entity->getArgument(3)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::RibHeight() { return *entity->getArgument(3); }
bool IfcRibPlateProfileProperties::hasRibWidth() { return !entity->getArgument(4)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::RibWidth() { return *entity->getArgument(4); }
bool IfcRibPlateProfileProperties::hasRibSpacing() { return !entity->getArgument(5)->isNull(); }
IfcPositiveLengthMeasure IfcRibPlateProfileProperties::RibSpacing() { return *entity->getArgument(5); }
IfcRibPlateDirectionEnum::IfcRibPlateDirectionEnum IfcRibPlateProfileProperties::Direction() { return IfcRibPlateDirectionEnum::FromString(*entity->getArgument(6)); }
bool IfcRibPlateProfileProperties::is(Type::Enum v) { return v == Type::IfcRibPlateProfileProperties || IfcProfileProperties::is(v); }
Type::Enum IfcRibPlateProfileProperties::type() { return Type::IfcRibPlateProfileProperties; }
Type::Enum IfcRibPlateProfileProperties::Class() { return Type::IfcRibPlateProfileProperties; }
IfcRibPlateProfileProperties::IfcRibPlateProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcRibPlateProfileProperties)) throw; entity = e; } 
// IfcRightCircularCone
IfcPositiveLengthMeasure IfcRightCircularCone::Height() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcRightCircularCone::BottomRadius() { return *entity->getArgument(2); }
bool IfcRightCircularCone::is(Type::Enum v) { return v == Type::IfcRightCircularCone || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcRightCircularCone::type() { return Type::IfcRightCircularCone; }
Type::Enum IfcRightCircularCone::Class() { return Type::IfcRightCircularCone; }
IfcRightCircularCone::IfcRightCircularCone(IfcAbstractEntityPtr e) { if (!is(Type::IfcRightCircularCone)) throw; entity = e; } 
// IfcRightCircularCylinder
IfcPositiveLengthMeasure IfcRightCircularCylinder::Height() { return *entity->getArgument(1); }
IfcPositiveLengthMeasure IfcRightCircularCylinder::Radius() { return *entity->getArgument(2); }
bool IfcRightCircularCylinder::is(Type::Enum v) { return v == Type::IfcRightCircularCylinder || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcRightCircularCylinder::type() { return Type::IfcRightCircularCylinder; }
Type::Enum IfcRightCircularCylinder::Class() { return Type::IfcRightCircularCylinder; }
IfcRightCircularCylinder::IfcRightCircularCylinder(IfcAbstractEntityPtr e) { if (!is(Type::IfcRightCircularCylinder)) throw; entity = e; } 
// IfcRoof
IfcRoofTypeEnum::IfcRoofTypeEnum IfcRoof::ShapeType() { return IfcRoofTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcRoof::is(Type::Enum v) { return v == Type::IfcRoof || IfcBuildingElement::is(v); }
Type::Enum IfcRoof::type() { return Type::IfcRoof; }
Type::Enum IfcRoof::Class() { return Type::IfcRoof; }
IfcRoof::IfcRoof(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoof)) throw; entity = e; } 
// IfcRoot
IfcGloballyUniqueId IfcRoot::GlobalId() { return *entity->getArgument(0); }
SHARED_PTR<IfcOwnerHistory> IfcRoot::OwnerHistory() { return reinterpret_pointer_cast<IfcBaseClass,IfcOwnerHistory>(*entity->getArgument(1)); }
bool IfcRoot::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcRoot::Name() { return *entity->getArgument(2); }
bool IfcRoot::hasDescription() { return !entity->getArgument(3)->isNull(); }
IfcText IfcRoot::Description() { return *entity->getArgument(3); }
bool IfcRoot::is(Type::Enum v) { return v == Type::IfcRoot; }
Type::Enum IfcRoot::type() { return Type::IfcRoot; }
Type::Enum IfcRoot::Class() { return Type::IfcRoot; }
IfcRoot::IfcRoot(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoot)) throw; entity = e; } 
// IfcRoundedEdgeFeature
bool IfcRoundedEdgeFeature::hasRadius() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcRoundedEdgeFeature::Radius() { return *entity->getArgument(9); }
bool IfcRoundedEdgeFeature::is(Type::Enum v) { return v == Type::IfcRoundedEdgeFeature || IfcEdgeFeature::is(v); }
Type::Enum IfcRoundedEdgeFeature::type() { return Type::IfcRoundedEdgeFeature; }
Type::Enum IfcRoundedEdgeFeature::Class() { return Type::IfcRoundedEdgeFeature; }
IfcRoundedEdgeFeature::IfcRoundedEdgeFeature(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoundedEdgeFeature)) throw; entity = e; } 
// IfcRoundedRectangleProfileDef
IfcPositiveLengthMeasure IfcRoundedRectangleProfileDef::RoundingRadius() { return *entity->getArgument(5); }
bool IfcRoundedRectangleProfileDef::is(Type::Enum v) { return v == Type::IfcRoundedRectangleProfileDef || IfcRectangleProfileDef::is(v); }
Type::Enum IfcRoundedRectangleProfileDef::type() { return Type::IfcRoundedRectangleProfileDef; }
Type::Enum IfcRoundedRectangleProfileDef::Class() { return Type::IfcRoundedRectangleProfileDef; }
IfcRoundedRectangleProfileDef::IfcRoundedRectangleProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcRoundedRectangleProfileDef)) throw; entity = e; } 
// IfcSIUnit
bool IfcSIUnit::hasPrefix() { return !entity->getArgument(2)->isNull(); }
IfcSIPrefix::IfcSIPrefix IfcSIUnit::Prefix() { return IfcSIPrefix::FromString(*entity->getArgument(2)); }
IfcSIUnitName::IfcSIUnitName IfcSIUnit::Name() { return IfcSIUnitName::FromString(*entity->getArgument(3)); }
bool IfcSIUnit::is(Type::Enum v) { return v == Type::IfcSIUnit || IfcNamedUnit::is(v); }
Type::Enum IfcSIUnit::type() { return Type::IfcSIUnit; }
Type::Enum IfcSIUnit::Class() { return Type::IfcSIUnit; }
IfcSIUnit::IfcSIUnit(IfcAbstractEntityPtr e) { if (!is(Type::IfcSIUnit)) throw; entity = e; } 
// IfcSanitaryTerminalType
IfcSanitaryTerminalTypeEnum::IfcSanitaryTerminalTypeEnum IfcSanitaryTerminalType::PredefinedType() { return IfcSanitaryTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSanitaryTerminalType::is(Type::Enum v) { return v == Type::IfcSanitaryTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcSanitaryTerminalType::type() { return Type::IfcSanitaryTerminalType; }
Type::Enum IfcSanitaryTerminalType::Class() { return Type::IfcSanitaryTerminalType; }
IfcSanitaryTerminalType::IfcSanitaryTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSanitaryTerminalType)) throw; entity = e; } 
// IfcScheduleTimeControl
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
bool IfcScheduleTimeControl::is(Type::Enum v) { return v == Type::IfcScheduleTimeControl || IfcControl::is(v); }
Type::Enum IfcScheduleTimeControl::type() { return Type::IfcScheduleTimeControl; }
Type::Enum IfcScheduleTimeControl::Class() { return Type::IfcScheduleTimeControl; }
IfcScheduleTimeControl::IfcScheduleTimeControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcScheduleTimeControl)) throw; entity = e; } 
// IfcSectionProperties
IfcSectionTypeEnum::IfcSectionTypeEnum IfcSectionProperties::SectionType() { return IfcSectionTypeEnum::FromString(*entity->getArgument(0)); }
SHARED_PTR<IfcProfileDef> IfcSectionProperties::StartProfile() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(1)); }
bool IfcSectionProperties::hasEndProfile() { return !entity->getArgument(2)->isNull(); }
SHARED_PTR<IfcProfileDef> IfcSectionProperties::EndProfile() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(2)); }
bool IfcSectionProperties::is(Type::Enum v) { return v == Type::IfcSectionProperties; }
Type::Enum IfcSectionProperties::type() { return Type::IfcSectionProperties; }
Type::Enum IfcSectionProperties::Class() { return Type::IfcSectionProperties; }
IfcSectionProperties::IfcSectionProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSectionProperties)) throw; entity = e; } 
// IfcSectionReinforcementProperties
IfcLengthMeasure IfcSectionReinforcementProperties::LongitudinalStartPosition() { return *entity->getArgument(0); }
IfcLengthMeasure IfcSectionReinforcementProperties::LongitudinalEndPosition() { return *entity->getArgument(1); }
bool IfcSectionReinforcementProperties::hasTransversePosition() { return !entity->getArgument(2)->isNull(); }
IfcLengthMeasure IfcSectionReinforcementProperties::TransversePosition() { return *entity->getArgument(2); }
IfcReinforcingBarRoleEnum::IfcReinforcingBarRoleEnum IfcSectionReinforcementProperties::ReinforcementRole() { return IfcReinforcingBarRoleEnum::FromString(*entity->getArgument(3)); }
SHARED_PTR<IfcSectionProperties> IfcSectionReinforcementProperties::SectionDefinition() { return reinterpret_pointer_cast<IfcBaseClass,IfcSectionProperties>(*entity->getArgument(4)); }
SHARED_PTR< IfcTemplatedEntityList<IfcReinforcementBarProperties> > IfcSectionReinforcementProperties::CrossSectionReinforcementDefinitions() { RETURN_AS_LIST(IfcReinforcementBarProperties,5) }
bool IfcSectionReinforcementProperties::is(Type::Enum v) { return v == Type::IfcSectionReinforcementProperties; }
Type::Enum IfcSectionReinforcementProperties::type() { return Type::IfcSectionReinforcementProperties; }
Type::Enum IfcSectionReinforcementProperties::Class() { return Type::IfcSectionReinforcementProperties; }
IfcSectionReinforcementProperties::IfcSectionReinforcementProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSectionReinforcementProperties)) throw; entity = e; } 
// IfcSectionedSpine
SHARED_PTR<IfcCompositeCurve> IfcSectionedSpine::SpineCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCompositeCurve>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcProfileDef> > IfcSectionedSpine::CrossSections() { RETURN_AS_LIST(IfcProfileDef,1) }
SHARED_PTR< IfcTemplatedEntityList<IfcAxis2Placement3D> > IfcSectionedSpine::CrossSectionPositions() { RETURN_AS_LIST(IfcAxis2Placement3D,2) }
bool IfcSectionedSpine::is(Type::Enum v) { return v == Type::IfcSectionedSpine || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcSectionedSpine::type() { return Type::IfcSectionedSpine; }
Type::Enum IfcSectionedSpine::Class() { return Type::IfcSectionedSpine; }
IfcSectionedSpine::IfcSectionedSpine(IfcAbstractEntityPtr e) { if (!is(Type::IfcSectionedSpine)) throw; entity = e; } 
// IfcSensorType
IfcSensorTypeEnum::IfcSensorTypeEnum IfcSensorType::PredefinedType() { return IfcSensorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSensorType::is(Type::Enum v) { return v == Type::IfcSensorType || IfcDistributionControlElementType::is(v); }
Type::Enum IfcSensorType::type() { return Type::IfcSensorType; }
Type::Enum IfcSensorType::Class() { return Type::IfcSensorType; }
IfcSensorType::IfcSensorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSensorType)) throw; entity = e; } 
// IfcServiceLife
IfcServiceLifeTypeEnum::IfcServiceLifeTypeEnum IfcServiceLife::ServiceLifeType() { return IfcServiceLifeTypeEnum::FromString(*entity->getArgument(5)); }
IfcTimeMeasure IfcServiceLife::ServiceLifeDuration() { return *entity->getArgument(6); }
bool IfcServiceLife::is(Type::Enum v) { return v == Type::IfcServiceLife || IfcControl::is(v); }
Type::Enum IfcServiceLife::type() { return Type::IfcServiceLife; }
Type::Enum IfcServiceLife::Class() { return Type::IfcServiceLife; }
IfcServiceLife::IfcServiceLife(IfcAbstractEntityPtr e) { if (!is(Type::IfcServiceLife)) throw; entity = e; } 
// IfcServiceLifeFactor
IfcServiceLifeFactorTypeEnum::IfcServiceLifeFactorTypeEnum IfcServiceLifeFactor::PredefinedType() { return IfcServiceLifeFactorTypeEnum::FromString(*entity->getArgument(4)); }
bool IfcServiceLifeFactor::hasUpperValue() { return !entity->getArgument(5)->isNull(); }
IfcMeasureValue IfcServiceLifeFactor::UpperValue() { return *entity->getArgument(5); }
IfcMeasureValue IfcServiceLifeFactor::MostUsedValue() { return *entity->getArgument(6); }
bool IfcServiceLifeFactor::hasLowerValue() { return !entity->getArgument(7)->isNull(); }
IfcMeasureValue IfcServiceLifeFactor::LowerValue() { return *entity->getArgument(7); }
bool IfcServiceLifeFactor::is(Type::Enum v) { return v == Type::IfcServiceLifeFactor || IfcPropertySetDefinition::is(v); }
Type::Enum IfcServiceLifeFactor::type() { return Type::IfcServiceLifeFactor; }
Type::Enum IfcServiceLifeFactor::Class() { return Type::IfcServiceLifeFactor; }
IfcServiceLifeFactor::IfcServiceLifeFactor(IfcAbstractEntityPtr e) { if (!is(Type::IfcServiceLifeFactor)) throw; entity = e; } 
// IfcShapeAspect
SHARED_PTR< IfcTemplatedEntityList<IfcShapeModel> > IfcShapeAspect::ShapeRepresentations() { RETURN_AS_LIST(IfcShapeModel,0) }
bool IfcShapeAspect::hasName() { return !entity->getArgument(1)->isNull(); }
IfcLabel IfcShapeAspect::Name() { return *entity->getArgument(1); }
bool IfcShapeAspect::hasDescription() { return !entity->getArgument(2)->isNull(); }
IfcText IfcShapeAspect::Description() { return *entity->getArgument(2); }
bool IfcShapeAspect::ProductDefinitional() { return *entity->getArgument(3); }
SHARED_PTR<IfcProductDefinitionShape> IfcShapeAspect::PartOfProductDefinitionShape() { return reinterpret_pointer_cast<IfcBaseClass,IfcProductDefinitionShape>(*entity->getArgument(4)); }
bool IfcShapeAspect::is(Type::Enum v) { return v == Type::IfcShapeAspect; }
Type::Enum IfcShapeAspect::type() { return Type::IfcShapeAspect; }
Type::Enum IfcShapeAspect::Class() { return Type::IfcShapeAspect; }
IfcShapeAspect::IfcShapeAspect(IfcAbstractEntityPtr e) { if (!is(Type::IfcShapeAspect)) throw; entity = e; } 
// IfcShapeModel
IfcShapeAspect::list IfcShapeModel::OfShapeAspect() { RETURN_INVERSE(IfcShapeAspect) }
bool IfcShapeModel::is(Type::Enum v) { return v == Type::IfcShapeModel || IfcRepresentation::is(v); }
Type::Enum IfcShapeModel::type() { return Type::IfcShapeModel; }
Type::Enum IfcShapeModel::Class() { return Type::IfcShapeModel; }
IfcShapeModel::IfcShapeModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcShapeModel)) throw; entity = e; } 
// IfcShapeRepresentation
bool IfcShapeRepresentation::is(Type::Enum v) { return v == Type::IfcShapeRepresentation || IfcShapeModel::is(v); }
Type::Enum IfcShapeRepresentation::type() { return Type::IfcShapeRepresentation; }
Type::Enum IfcShapeRepresentation::Class() { return Type::IfcShapeRepresentation; }
IfcShapeRepresentation::IfcShapeRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcShapeRepresentation)) throw; entity = e; } 
// IfcShellBasedSurfaceModel
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcShellBasedSurfaceModel::SbsmBoundary() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcShellBasedSurfaceModel::is(Type::Enum v) { return v == Type::IfcShellBasedSurfaceModel || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcShellBasedSurfaceModel::type() { return Type::IfcShellBasedSurfaceModel; }
Type::Enum IfcShellBasedSurfaceModel::Class() { return Type::IfcShellBasedSurfaceModel; }
IfcShellBasedSurfaceModel::IfcShellBasedSurfaceModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcShellBasedSurfaceModel)) throw; entity = e; } 
// IfcSimpleProperty
bool IfcSimpleProperty::is(Type::Enum v) { return v == Type::IfcSimpleProperty || IfcProperty::is(v); }
Type::Enum IfcSimpleProperty::type() { return Type::IfcSimpleProperty; }
Type::Enum IfcSimpleProperty::Class() { return Type::IfcSimpleProperty; }
IfcSimpleProperty::IfcSimpleProperty(IfcAbstractEntityPtr e) { if (!is(Type::IfcSimpleProperty)) throw; entity = e; } 
// IfcSite
bool IfcSite::hasRefLatitude() { return !entity->getArgument(9)->isNull(); }
IfcCompoundPlaneAngleMeasure IfcSite::RefLatitude() { return *entity->getArgument(9); }
bool IfcSite::hasRefLongitude() { return !entity->getArgument(10)->isNull(); }
IfcCompoundPlaneAngleMeasure IfcSite::RefLongitude() { return *entity->getArgument(10); }
bool IfcSite::hasRefElevation() { return !entity->getArgument(11)->isNull(); }
IfcLengthMeasure IfcSite::RefElevation() { return *entity->getArgument(11); }
bool IfcSite::hasLandTitleNumber() { return !entity->getArgument(12)->isNull(); }
IfcLabel IfcSite::LandTitleNumber() { return *entity->getArgument(12); }
bool IfcSite::hasSiteAddress() { return !entity->getArgument(13)->isNull(); }
SHARED_PTR<IfcPostalAddress> IfcSite::SiteAddress() { return reinterpret_pointer_cast<IfcBaseClass,IfcPostalAddress>(*entity->getArgument(13)); }
bool IfcSite::is(Type::Enum v) { return v == Type::IfcSite || IfcSpatialStructureElement::is(v); }
Type::Enum IfcSite::type() { return Type::IfcSite; }
Type::Enum IfcSite::Class() { return Type::IfcSite; }
IfcSite::IfcSite(IfcAbstractEntityPtr e) { if (!is(Type::IfcSite)) throw; entity = e; } 
// IfcSlab
bool IfcSlab::hasPredefinedType() { return !entity->getArgument(8)->isNull(); }
IfcSlabTypeEnum::IfcSlabTypeEnum IfcSlab::PredefinedType() { return IfcSlabTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcSlab::is(Type::Enum v) { return v == Type::IfcSlab || IfcBuildingElement::is(v); }
Type::Enum IfcSlab::type() { return Type::IfcSlab; }
Type::Enum IfcSlab::Class() { return Type::IfcSlab; }
IfcSlab::IfcSlab(IfcAbstractEntityPtr e) { if (!is(Type::IfcSlab)) throw; entity = e; } 
// IfcSlabType
IfcSlabTypeEnum::IfcSlabTypeEnum IfcSlabType::PredefinedType() { return IfcSlabTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSlabType::is(Type::Enum v) { return v == Type::IfcSlabType || IfcBuildingElementType::is(v); }
Type::Enum IfcSlabType::type() { return Type::IfcSlabType; }
Type::Enum IfcSlabType::Class() { return Type::IfcSlabType; }
IfcSlabType::IfcSlabType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSlabType)) throw; entity = e; } 
// IfcSlippageConnectionCondition
bool IfcSlippageConnectionCondition::hasSlippageX() { return !entity->getArgument(1)->isNull(); }
IfcLengthMeasure IfcSlippageConnectionCondition::SlippageX() { return *entity->getArgument(1); }
bool IfcSlippageConnectionCondition::hasSlippageY() { return !entity->getArgument(2)->isNull(); }
IfcLengthMeasure IfcSlippageConnectionCondition::SlippageY() { return *entity->getArgument(2); }
bool IfcSlippageConnectionCondition::hasSlippageZ() { return !entity->getArgument(3)->isNull(); }
IfcLengthMeasure IfcSlippageConnectionCondition::SlippageZ() { return *entity->getArgument(3); }
bool IfcSlippageConnectionCondition::is(Type::Enum v) { return v == Type::IfcSlippageConnectionCondition || IfcStructuralConnectionCondition::is(v); }
Type::Enum IfcSlippageConnectionCondition::type() { return Type::IfcSlippageConnectionCondition; }
Type::Enum IfcSlippageConnectionCondition::Class() { return Type::IfcSlippageConnectionCondition; }
IfcSlippageConnectionCondition::IfcSlippageConnectionCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcSlippageConnectionCondition)) throw; entity = e; } 
// IfcSolidModel
bool IfcSolidModel::is(Type::Enum v) { return v == Type::IfcSolidModel || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcSolidModel::type() { return Type::IfcSolidModel; }
Type::Enum IfcSolidModel::Class() { return Type::IfcSolidModel; }
IfcSolidModel::IfcSolidModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcSolidModel)) throw; entity = e; } 
// IfcSoundProperties
IfcBoolean IfcSoundProperties::IsAttenuating() { return *entity->getArgument(4); }
bool IfcSoundProperties::hasSoundScale() { return !entity->getArgument(5)->isNull(); }
IfcSoundScaleEnum::IfcSoundScaleEnum IfcSoundProperties::SoundScale() { return IfcSoundScaleEnum::FromString(*entity->getArgument(5)); }
SHARED_PTR< IfcTemplatedEntityList<IfcSoundValue> > IfcSoundProperties::SoundValues() { RETURN_AS_LIST(IfcSoundValue,6) }
bool IfcSoundProperties::is(Type::Enum v) { return v == Type::IfcSoundProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcSoundProperties::type() { return Type::IfcSoundProperties; }
Type::Enum IfcSoundProperties::Class() { return Type::IfcSoundProperties; }
IfcSoundProperties::IfcSoundProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSoundProperties)) throw; entity = e; } 
// IfcSoundValue
bool IfcSoundValue::hasSoundLevelTimeSeries() { return !entity->getArgument(4)->isNull(); }
SHARED_PTR<IfcTimeSeries> IfcSoundValue::SoundLevelTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(4)); }
IfcFrequencyMeasure IfcSoundValue::Frequency() { return *entity->getArgument(5); }
bool IfcSoundValue::hasSoundLevelSingleValue() { return !entity->getArgument(6)->isNull(); }
IfcDerivedMeasureValue IfcSoundValue::SoundLevelSingleValue() { return *entity->getArgument(6); }
bool IfcSoundValue::is(Type::Enum v) { return v == Type::IfcSoundValue || IfcPropertySetDefinition::is(v); }
Type::Enum IfcSoundValue::type() { return Type::IfcSoundValue; }
Type::Enum IfcSoundValue::Class() { return Type::IfcSoundValue; }
IfcSoundValue::IfcSoundValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcSoundValue)) throw; entity = e; } 
// IfcSpace
IfcInternalOrExternalEnum::IfcInternalOrExternalEnum IfcSpace::InteriorOrExteriorSpace() { return IfcInternalOrExternalEnum::FromString(*entity->getArgument(9)); }
bool IfcSpace::hasElevationWithFlooring() { return !entity->getArgument(10)->isNull(); }
IfcLengthMeasure IfcSpace::ElevationWithFlooring() { return *entity->getArgument(10); }
IfcRelCoversSpaces::list IfcSpace::HasCoverings() { RETURN_INVERSE(IfcRelCoversSpaces) }
IfcRelSpaceBoundary::list IfcSpace::BoundedBy() { RETURN_INVERSE(IfcRelSpaceBoundary) }
bool IfcSpace::is(Type::Enum v) { return v == Type::IfcSpace || IfcSpatialStructureElement::is(v); }
Type::Enum IfcSpace::type() { return Type::IfcSpace; }
Type::Enum IfcSpace::Class() { return Type::IfcSpace; }
IfcSpace::IfcSpace(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpace)) throw; entity = e; } 
// IfcSpaceHeaterType
IfcSpaceHeaterTypeEnum::IfcSpaceHeaterTypeEnum IfcSpaceHeaterType::PredefinedType() { return IfcSpaceHeaterTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSpaceHeaterType::is(Type::Enum v) { return v == Type::IfcSpaceHeaterType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcSpaceHeaterType::type() { return Type::IfcSpaceHeaterType; }
Type::Enum IfcSpaceHeaterType::Class() { return Type::IfcSpaceHeaterType; }
IfcSpaceHeaterType::IfcSpaceHeaterType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceHeaterType)) throw; entity = e; } 
// IfcSpaceProgram
IfcIdentifier IfcSpaceProgram::SpaceProgramIdentifier() { return *entity->getArgument(5); }
bool IfcSpaceProgram::hasMaxRequiredArea() { return !entity->getArgument(6)->isNull(); }
IfcAreaMeasure IfcSpaceProgram::MaxRequiredArea() { return *entity->getArgument(6); }
bool IfcSpaceProgram::hasMinRequiredArea() { return !entity->getArgument(7)->isNull(); }
IfcAreaMeasure IfcSpaceProgram::MinRequiredArea() { return *entity->getArgument(7); }
bool IfcSpaceProgram::hasRequestedLocation() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR<IfcSpatialStructureElement> IfcSpaceProgram::RequestedLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcSpatialStructureElement>(*entity->getArgument(8)); }
IfcAreaMeasure IfcSpaceProgram::StandardRequiredArea() { return *entity->getArgument(9); }
IfcRelInteractionRequirements::list IfcSpaceProgram::HasInteractionReqsFrom() { RETURN_INVERSE(IfcRelInteractionRequirements) }
IfcRelInteractionRequirements::list IfcSpaceProgram::HasInteractionReqsTo() { RETURN_INVERSE(IfcRelInteractionRequirements) }
bool IfcSpaceProgram::is(Type::Enum v) { return v == Type::IfcSpaceProgram || IfcControl::is(v); }
Type::Enum IfcSpaceProgram::type() { return Type::IfcSpaceProgram; }
Type::Enum IfcSpaceProgram::Class() { return Type::IfcSpaceProgram; }
IfcSpaceProgram::IfcSpaceProgram(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceProgram)) throw; entity = e; } 
// IfcSpaceThermalLoadProperties
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
SHARED_PTR<IfcTimeSeries> IfcSpaceThermalLoadProperties::ThermalLoadTimeSeriesValues() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(10)); }
bool IfcSpaceThermalLoadProperties::hasUserDefinedThermalLoadSource() { return !entity->getArgument(11)->isNull(); }
IfcLabel IfcSpaceThermalLoadProperties::UserDefinedThermalLoadSource() { return *entity->getArgument(11); }
bool IfcSpaceThermalLoadProperties::hasUserDefinedPropertySource() { return !entity->getArgument(12)->isNull(); }
IfcLabel IfcSpaceThermalLoadProperties::UserDefinedPropertySource() { return *entity->getArgument(12); }
IfcThermalLoadTypeEnum::IfcThermalLoadTypeEnum IfcSpaceThermalLoadProperties::ThermalLoadType() { return IfcThermalLoadTypeEnum::FromString(*entity->getArgument(13)); }
bool IfcSpaceThermalLoadProperties::is(Type::Enum v) { return v == Type::IfcSpaceThermalLoadProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcSpaceThermalLoadProperties::type() { return Type::IfcSpaceThermalLoadProperties; }
Type::Enum IfcSpaceThermalLoadProperties::Class() { return Type::IfcSpaceThermalLoadProperties; }
IfcSpaceThermalLoadProperties::IfcSpaceThermalLoadProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceThermalLoadProperties)) throw; entity = e; } 
// IfcSpaceType
IfcSpaceTypeEnum::IfcSpaceTypeEnum IfcSpaceType::PredefinedType() { return IfcSpaceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSpaceType::is(Type::Enum v) { return v == Type::IfcSpaceType || IfcSpatialStructureElementType::is(v); }
Type::Enum IfcSpaceType::type() { return Type::IfcSpaceType; }
Type::Enum IfcSpaceType::Class() { return Type::IfcSpaceType; }
IfcSpaceType::IfcSpaceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpaceType)) throw; entity = e; } 
// IfcSpatialStructureElement
bool IfcSpatialStructureElement::hasLongName() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcSpatialStructureElement::LongName() { return *entity->getArgument(7); }
IfcElementCompositionEnum::IfcElementCompositionEnum IfcSpatialStructureElement::CompositionType() { return IfcElementCompositionEnum::FromString(*entity->getArgument(8)); }
IfcRelReferencedInSpatialStructure::list IfcSpatialStructureElement::ReferencesElements() { RETURN_INVERSE(IfcRelReferencedInSpatialStructure) }
IfcRelServicesBuildings::list IfcSpatialStructureElement::ServicedBySystems() { RETURN_INVERSE(IfcRelServicesBuildings) }
IfcRelContainedInSpatialStructure::list IfcSpatialStructureElement::ContainsElements() { RETURN_INVERSE(IfcRelContainedInSpatialStructure) }
bool IfcSpatialStructureElement::is(Type::Enum v) { return v == Type::IfcSpatialStructureElement || IfcProduct::is(v); }
Type::Enum IfcSpatialStructureElement::type() { return Type::IfcSpatialStructureElement; }
Type::Enum IfcSpatialStructureElement::Class() { return Type::IfcSpatialStructureElement; }
IfcSpatialStructureElement::IfcSpatialStructureElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpatialStructureElement)) throw; entity = e; } 
// IfcSpatialStructureElementType
bool IfcSpatialStructureElementType::is(Type::Enum v) { return v == Type::IfcSpatialStructureElementType || IfcElementType::is(v); }
Type::Enum IfcSpatialStructureElementType::type() { return Type::IfcSpatialStructureElementType; }
Type::Enum IfcSpatialStructureElementType::Class() { return Type::IfcSpatialStructureElementType; }
IfcSpatialStructureElementType::IfcSpatialStructureElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSpatialStructureElementType)) throw; entity = e; } 
// IfcSphere
IfcPositiveLengthMeasure IfcSphere::Radius() { return *entity->getArgument(1); }
bool IfcSphere::is(Type::Enum v) { return v == Type::IfcSphere || IfcCsgPrimitive3D::is(v); }
Type::Enum IfcSphere::type() { return Type::IfcSphere; }
Type::Enum IfcSphere::Class() { return Type::IfcSphere; }
IfcSphere::IfcSphere(IfcAbstractEntityPtr e) { if (!is(Type::IfcSphere)) throw; entity = e; } 
// IfcStackTerminalType
IfcStackTerminalTypeEnum::IfcStackTerminalTypeEnum IfcStackTerminalType::PredefinedType() { return IfcStackTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcStackTerminalType::is(Type::Enum v) { return v == Type::IfcStackTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcStackTerminalType::type() { return Type::IfcStackTerminalType; }
Type::Enum IfcStackTerminalType::Class() { return Type::IfcStackTerminalType; }
IfcStackTerminalType::IfcStackTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcStackTerminalType)) throw; entity = e; } 
// IfcStair
IfcStairTypeEnum::IfcStairTypeEnum IfcStair::ShapeType() { return IfcStairTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcStair::is(Type::Enum v) { return v == Type::IfcStair || IfcBuildingElement::is(v); }
Type::Enum IfcStair::type() { return Type::IfcStair; }
Type::Enum IfcStair::Class() { return Type::IfcStair; }
IfcStair::IfcStair(IfcAbstractEntityPtr e) { if (!is(Type::IfcStair)) throw; entity = e; } 
// IfcStairFlight
bool IfcStairFlight::hasNumberOfRiser() { return !entity->getArgument(8)->isNull(); }
int IfcStairFlight::NumberOfRiser() { return *entity->getArgument(8); }
bool IfcStairFlight::hasNumberOfTreads() { return !entity->getArgument(9)->isNull(); }
int IfcStairFlight::NumberOfTreads() { return *entity->getArgument(9); }
bool IfcStairFlight::hasRiserHeight() { return !entity->getArgument(10)->isNull(); }
IfcPositiveLengthMeasure IfcStairFlight::RiserHeight() { return *entity->getArgument(10); }
bool IfcStairFlight::hasTreadLength() { return !entity->getArgument(11)->isNull(); }
IfcPositiveLengthMeasure IfcStairFlight::TreadLength() { return *entity->getArgument(11); }
bool IfcStairFlight::is(Type::Enum v) { return v == Type::IfcStairFlight || IfcBuildingElement::is(v); }
Type::Enum IfcStairFlight::type() { return Type::IfcStairFlight; }
Type::Enum IfcStairFlight::Class() { return Type::IfcStairFlight; }
IfcStairFlight::IfcStairFlight(IfcAbstractEntityPtr e) { if (!is(Type::IfcStairFlight)) throw; entity = e; } 
// IfcStairFlightType
IfcStairFlightTypeEnum::IfcStairFlightTypeEnum IfcStairFlightType::PredefinedType() { return IfcStairFlightTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcStairFlightType::is(Type::Enum v) { return v == Type::IfcStairFlightType || IfcBuildingElementType::is(v); }
Type::Enum IfcStairFlightType::type() { return Type::IfcStairFlightType; }
Type::Enum IfcStairFlightType::Class() { return Type::IfcStairFlightType; }
IfcStairFlightType::IfcStairFlightType(IfcAbstractEntityPtr e) { if (!is(Type::IfcStairFlightType)) throw; entity = e; } 
// IfcStructuralAction
bool IfcStructuralAction::DestabilizingLoad() { return *entity->getArgument(9); }
bool IfcStructuralAction::hasCausedBy() { return !entity->getArgument(10)->isNull(); }
SHARED_PTR<IfcStructuralReaction> IfcStructuralAction::CausedBy() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralReaction>(*entity->getArgument(10)); }
bool IfcStructuralAction::is(Type::Enum v) { return v == Type::IfcStructuralAction || IfcStructuralActivity::is(v); }
Type::Enum IfcStructuralAction::type() { return Type::IfcStructuralAction; }
Type::Enum IfcStructuralAction::Class() { return Type::IfcStructuralAction; }
IfcStructuralAction::IfcStructuralAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralAction)) throw; entity = e; } 
// IfcStructuralActivity
SHARED_PTR<IfcStructuralLoad> IfcStructuralActivity::AppliedLoad() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralLoad>(*entity->getArgument(7)); }
IfcGlobalOrLocalEnum::IfcGlobalOrLocalEnum IfcStructuralActivity::GlobalOrLocal() { return IfcGlobalOrLocalEnum::FromString(*entity->getArgument(8)); }
IfcRelConnectsStructuralActivity::list IfcStructuralActivity::AssignedToStructuralItem() { RETURN_INVERSE(IfcRelConnectsStructuralActivity) }
bool IfcStructuralActivity::is(Type::Enum v) { return v == Type::IfcStructuralActivity || IfcProduct::is(v); }
Type::Enum IfcStructuralActivity::type() { return Type::IfcStructuralActivity; }
Type::Enum IfcStructuralActivity::Class() { return Type::IfcStructuralActivity; }
IfcStructuralActivity::IfcStructuralActivity(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralActivity)) throw; entity = e; } 
// IfcStructuralAnalysisModel
IfcAnalysisModelTypeEnum::IfcAnalysisModelTypeEnum IfcStructuralAnalysisModel::PredefinedType() { return IfcAnalysisModelTypeEnum::FromString(*entity->getArgument(5)); }
bool IfcStructuralAnalysisModel::hasOrientationOf2DPlane() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcAxis2Placement3D> IfcStructuralAnalysisModel::OrientationOf2DPlane() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(6)); }
bool IfcStructuralAnalysisModel::hasLoadedBy() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoadGroup> > IfcStructuralAnalysisModel::LoadedBy() { RETURN_AS_LIST(IfcStructuralLoadGroup,7) }
bool IfcStructuralAnalysisModel::hasHasResults() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralResultGroup> > IfcStructuralAnalysisModel::HasResults() { RETURN_AS_LIST(IfcStructuralResultGroup,8) }
bool IfcStructuralAnalysisModel::is(Type::Enum v) { return v == Type::IfcStructuralAnalysisModel || IfcSystem::is(v); }
Type::Enum IfcStructuralAnalysisModel::type() { return Type::IfcStructuralAnalysisModel; }
Type::Enum IfcStructuralAnalysisModel::Class() { return Type::IfcStructuralAnalysisModel; }
IfcStructuralAnalysisModel::IfcStructuralAnalysisModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralAnalysisModel)) throw; entity = e; } 
// IfcStructuralConnection
bool IfcStructuralConnection::hasAppliedCondition() { return !entity->getArgument(7)->isNull(); }
SHARED_PTR<IfcBoundaryCondition> IfcStructuralConnection::AppliedCondition() { return reinterpret_pointer_cast<IfcBaseClass,IfcBoundaryCondition>(*entity->getArgument(7)); }
IfcRelConnectsStructuralMember::list IfcStructuralConnection::ConnectsStructuralMembers() { RETURN_INVERSE(IfcRelConnectsStructuralMember) }
bool IfcStructuralConnection::is(Type::Enum v) { return v == Type::IfcStructuralConnection || IfcStructuralItem::is(v); }
Type::Enum IfcStructuralConnection::type() { return Type::IfcStructuralConnection; }
Type::Enum IfcStructuralConnection::Class() { return Type::IfcStructuralConnection; }
IfcStructuralConnection::IfcStructuralConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralConnection)) throw; entity = e; } 
// IfcStructuralConnectionCondition
bool IfcStructuralConnectionCondition::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcStructuralConnectionCondition::Name() { return *entity->getArgument(0); }
bool IfcStructuralConnectionCondition::is(Type::Enum v) { return v == Type::IfcStructuralConnectionCondition; }
Type::Enum IfcStructuralConnectionCondition::type() { return Type::IfcStructuralConnectionCondition; }
Type::Enum IfcStructuralConnectionCondition::Class() { return Type::IfcStructuralConnectionCondition; }
IfcStructuralConnectionCondition::IfcStructuralConnectionCondition(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralConnectionCondition)) throw; entity = e; } 
// IfcStructuralCurveConnection
bool IfcStructuralCurveConnection::is(Type::Enum v) { return v == Type::IfcStructuralCurveConnection || IfcStructuralConnection::is(v); }
Type::Enum IfcStructuralCurveConnection::type() { return Type::IfcStructuralCurveConnection; }
Type::Enum IfcStructuralCurveConnection::Class() { return Type::IfcStructuralCurveConnection; }
IfcStructuralCurveConnection::IfcStructuralCurveConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralCurveConnection)) throw; entity = e; } 
// IfcStructuralCurveMember
IfcStructuralCurveTypeEnum::IfcStructuralCurveTypeEnum IfcStructuralCurveMember::PredefinedType() { return IfcStructuralCurveTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcStructuralCurveMember::is(Type::Enum v) { return v == Type::IfcStructuralCurveMember || IfcStructuralMember::is(v); }
Type::Enum IfcStructuralCurveMember::type() { return Type::IfcStructuralCurveMember; }
Type::Enum IfcStructuralCurveMember::Class() { return Type::IfcStructuralCurveMember; }
IfcStructuralCurveMember::IfcStructuralCurveMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralCurveMember)) throw; entity = e; } 
// IfcStructuralCurveMemberVarying
bool IfcStructuralCurveMemberVarying::is(Type::Enum v) { return v == Type::IfcStructuralCurveMemberVarying || IfcStructuralCurveMember::is(v); }
Type::Enum IfcStructuralCurveMemberVarying::type() { return Type::IfcStructuralCurveMemberVarying; }
Type::Enum IfcStructuralCurveMemberVarying::Class() { return Type::IfcStructuralCurveMemberVarying; }
IfcStructuralCurveMemberVarying::IfcStructuralCurveMemberVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralCurveMemberVarying)) throw; entity = e; } 
// IfcStructuralItem
IfcRelConnectsStructuralActivity::list IfcStructuralItem::AssignedStructuralActivity() { RETURN_INVERSE(IfcRelConnectsStructuralActivity) }
bool IfcStructuralItem::is(Type::Enum v) { return v == Type::IfcStructuralItem || IfcProduct::is(v); }
Type::Enum IfcStructuralItem::type() { return Type::IfcStructuralItem; }
Type::Enum IfcStructuralItem::Class() { return Type::IfcStructuralItem; }
IfcStructuralItem::IfcStructuralItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralItem)) throw; entity = e; } 
// IfcStructuralLinearAction
IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum IfcStructuralLinearAction::ProjectedOrTrue() { return IfcProjectedOrTrueLengthEnum::FromString(*entity->getArgument(11)); }
bool IfcStructuralLinearAction::is(Type::Enum v) { return v == Type::IfcStructuralLinearAction || IfcStructuralAction::is(v); }
Type::Enum IfcStructuralLinearAction::type() { return Type::IfcStructuralLinearAction; }
Type::Enum IfcStructuralLinearAction::Class() { return Type::IfcStructuralLinearAction; }
IfcStructuralLinearAction::IfcStructuralLinearAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLinearAction)) throw; entity = e; } 
// IfcStructuralLinearActionVarying
SHARED_PTR<IfcShapeAspect> IfcStructuralLinearActionVarying::VaryingAppliedLoadLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(12)); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > IfcStructuralLinearActionVarying::SubsequentAppliedLoads() { RETURN_AS_LIST(IfcStructuralLoad,13) }
bool IfcStructuralLinearActionVarying::is(Type::Enum v) { return v == Type::IfcStructuralLinearActionVarying || IfcStructuralLinearAction::is(v); }
Type::Enum IfcStructuralLinearActionVarying::type() { return Type::IfcStructuralLinearActionVarying; }
Type::Enum IfcStructuralLinearActionVarying::Class() { return Type::IfcStructuralLinearActionVarying; }
IfcStructuralLinearActionVarying::IfcStructuralLinearActionVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLinearActionVarying)) throw; entity = e; } 
// IfcStructuralLoad
bool IfcStructuralLoad::hasName() { return !entity->getArgument(0)->isNull(); }
IfcLabel IfcStructuralLoad::Name() { return *entity->getArgument(0); }
bool IfcStructuralLoad::is(Type::Enum v) { return v == Type::IfcStructuralLoad; }
Type::Enum IfcStructuralLoad::type() { return Type::IfcStructuralLoad; }
Type::Enum IfcStructuralLoad::Class() { return Type::IfcStructuralLoad; }
IfcStructuralLoad::IfcStructuralLoad(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoad)) throw; entity = e; } 
// IfcStructuralLoadGroup
IfcLoadGroupTypeEnum::IfcLoadGroupTypeEnum IfcStructuralLoadGroup::PredefinedType() { return IfcLoadGroupTypeEnum::FromString(*entity->getArgument(5)); }
IfcActionTypeEnum::IfcActionTypeEnum IfcStructuralLoadGroup::ActionType() { return IfcActionTypeEnum::FromString(*entity->getArgument(6)); }
IfcActionSourceTypeEnum::IfcActionSourceTypeEnum IfcStructuralLoadGroup::ActionSource() { return IfcActionSourceTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcStructuralLoadGroup::hasCoefficient() { return !entity->getArgument(8)->isNull(); }
IfcRatioMeasure IfcStructuralLoadGroup::Coefficient() { return *entity->getArgument(8); }
bool IfcStructuralLoadGroup::hasPurpose() { return !entity->getArgument(9)->isNull(); }
IfcLabel IfcStructuralLoadGroup::Purpose() { return *entity->getArgument(9); }
IfcStructuralResultGroup::list IfcStructuralLoadGroup::SourceOfResultGroup() { RETURN_INVERSE(IfcStructuralResultGroup) }
IfcStructuralAnalysisModel::list IfcStructuralLoadGroup::LoadGroupFor() { RETURN_INVERSE(IfcStructuralAnalysisModel) }
bool IfcStructuralLoadGroup::is(Type::Enum v) { return v == Type::IfcStructuralLoadGroup || IfcGroup::is(v); }
Type::Enum IfcStructuralLoadGroup::type() { return Type::IfcStructuralLoadGroup; }
Type::Enum IfcStructuralLoadGroup::Class() { return Type::IfcStructuralLoadGroup; }
IfcStructuralLoadGroup::IfcStructuralLoadGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadGroup)) throw; entity = e; } 
// IfcStructuralLoadLinearForce
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
bool IfcStructuralLoadLinearForce::is(Type::Enum v) { return v == Type::IfcStructuralLoadLinearForce || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadLinearForce::type() { return Type::IfcStructuralLoadLinearForce; }
Type::Enum IfcStructuralLoadLinearForce::Class() { return Type::IfcStructuralLoadLinearForce; }
IfcStructuralLoadLinearForce::IfcStructuralLoadLinearForce(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadLinearForce)) throw; entity = e; } 
// IfcStructuralLoadPlanarForce
bool IfcStructuralLoadPlanarForce::hasPlanarForceX() { return !entity->getArgument(1)->isNull(); }
IfcPlanarForceMeasure IfcStructuralLoadPlanarForce::PlanarForceX() { return *entity->getArgument(1); }
bool IfcStructuralLoadPlanarForce::hasPlanarForceY() { return !entity->getArgument(2)->isNull(); }
IfcPlanarForceMeasure IfcStructuralLoadPlanarForce::PlanarForceY() { return *entity->getArgument(2); }
bool IfcStructuralLoadPlanarForce::hasPlanarForceZ() { return !entity->getArgument(3)->isNull(); }
IfcPlanarForceMeasure IfcStructuralLoadPlanarForce::PlanarForceZ() { return *entity->getArgument(3); }
bool IfcStructuralLoadPlanarForce::is(Type::Enum v) { return v == Type::IfcStructuralLoadPlanarForce || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadPlanarForce::type() { return Type::IfcStructuralLoadPlanarForce; }
Type::Enum IfcStructuralLoadPlanarForce::Class() { return Type::IfcStructuralLoadPlanarForce; }
IfcStructuralLoadPlanarForce::IfcStructuralLoadPlanarForce(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadPlanarForce)) throw; entity = e; } 
// IfcStructuralLoadSingleDisplacement
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
bool IfcStructuralLoadSingleDisplacement::is(Type::Enum v) { return v == Type::IfcStructuralLoadSingleDisplacement || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadSingleDisplacement::type() { return Type::IfcStructuralLoadSingleDisplacement; }
Type::Enum IfcStructuralLoadSingleDisplacement::Class() { return Type::IfcStructuralLoadSingleDisplacement; }
IfcStructuralLoadSingleDisplacement::IfcStructuralLoadSingleDisplacement(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleDisplacement)) throw; entity = e; } 
// IfcStructuralLoadSingleDisplacementDistortion
bool IfcStructuralLoadSingleDisplacementDistortion::hasDistortion() { return !entity->getArgument(7)->isNull(); }
IfcCurvatureMeasure IfcStructuralLoadSingleDisplacementDistortion::Distortion() { return *entity->getArgument(7); }
bool IfcStructuralLoadSingleDisplacementDistortion::is(Type::Enum v) { return v == Type::IfcStructuralLoadSingleDisplacementDistortion || IfcStructuralLoadSingleDisplacement::is(v); }
Type::Enum IfcStructuralLoadSingleDisplacementDistortion::type() { return Type::IfcStructuralLoadSingleDisplacementDistortion; }
Type::Enum IfcStructuralLoadSingleDisplacementDistortion::Class() { return Type::IfcStructuralLoadSingleDisplacementDistortion; }
IfcStructuralLoadSingleDisplacementDistortion::IfcStructuralLoadSingleDisplacementDistortion(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleDisplacementDistortion)) throw; entity = e; } 
// IfcStructuralLoadSingleForce
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
bool IfcStructuralLoadSingleForce::is(Type::Enum v) { return v == Type::IfcStructuralLoadSingleForce || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadSingleForce::type() { return Type::IfcStructuralLoadSingleForce; }
Type::Enum IfcStructuralLoadSingleForce::Class() { return Type::IfcStructuralLoadSingleForce; }
IfcStructuralLoadSingleForce::IfcStructuralLoadSingleForce(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleForce)) throw; entity = e; } 
// IfcStructuralLoadSingleForceWarping
bool IfcStructuralLoadSingleForceWarping::hasWarpingMoment() { return !entity->getArgument(7)->isNull(); }
IfcWarpingMomentMeasure IfcStructuralLoadSingleForceWarping::WarpingMoment() { return *entity->getArgument(7); }
bool IfcStructuralLoadSingleForceWarping::is(Type::Enum v) { return v == Type::IfcStructuralLoadSingleForceWarping || IfcStructuralLoadSingleForce::is(v); }
Type::Enum IfcStructuralLoadSingleForceWarping::type() { return Type::IfcStructuralLoadSingleForceWarping; }
Type::Enum IfcStructuralLoadSingleForceWarping::Class() { return Type::IfcStructuralLoadSingleForceWarping; }
IfcStructuralLoadSingleForceWarping::IfcStructuralLoadSingleForceWarping(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadSingleForceWarping)) throw; entity = e; } 
// IfcStructuralLoadStatic
bool IfcStructuralLoadStatic::is(Type::Enum v) { return v == Type::IfcStructuralLoadStatic || IfcStructuralLoad::is(v); }
Type::Enum IfcStructuralLoadStatic::type() { return Type::IfcStructuralLoadStatic; }
Type::Enum IfcStructuralLoadStatic::Class() { return Type::IfcStructuralLoadStatic; }
IfcStructuralLoadStatic::IfcStructuralLoadStatic(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadStatic)) throw; entity = e; } 
// IfcStructuralLoadTemperature
bool IfcStructuralLoadTemperature::hasDeltaT_Constant() { return !entity->getArgument(1)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcStructuralLoadTemperature::DeltaT_Constant() { return *entity->getArgument(1); }
bool IfcStructuralLoadTemperature::hasDeltaT_Y() { return !entity->getArgument(2)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcStructuralLoadTemperature::DeltaT_Y() { return *entity->getArgument(2); }
bool IfcStructuralLoadTemperature::hasDeltaT_Z() { return !entity->getArgument(3)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcStructuralLoadTemperature::DeltaT_Z() { return *entity->getArgument(3); }
bool IfcStructuralLoadTemperature::is(Type::Enum v) { return v == Type::IfcStructuralLoadTemperature || IfcStructuralLoadStatic::is(v); }
Type::Enum IfcStructuralLoadTemperature::type() { return Type::IfcStructuralLoadTemperature; }
Type::Enum IfcStructuralLoadTemperature::Class() { return Type::IfcStructuralLoadTemperature; }
IfcStructuralLoadTemperature::IfcStructuralLoadTemperature(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralLoadTemperature)) throw; entity = e; } 
// IfcStructuralMember
IfcRelConnectsStructuralElement::list IfcStructuralMember::ReferencesElement() { RETURN_INVERSE(IfcRelConnectsStructuralElement) }
IfcRelConnectsStructuralMember::list IfcStructuralMember::ConnectedBy() { RETURN_INVERSE(IfcRelConnectsStructuralMember) }
bool IfcStructuralMember::is(Type::Enum v) { return v == Type::IfcStructuralMember || IfcStructuralItem::is(v); }
Type::Enum IfcStructuralMember::type() { return Type::IfcStructuralMember; }
Type::Enum IfcStructuralMember::Class() { return Type::IfcStructuralMember; }
IfcStructuralMember::IfcStructuralMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralMember)) throw; entity = e; } 
// IfcStructuralPlanarAction
IfcProjectedOrTrueLengthEnum::IfcProjectedOrTrueLengthEnum IfcStructuralPlanarAction::ProjectedOrTrue() { return IfcProjectedOrTrueLengthEnum::FromString(*entity->getArgument(11)); }
bool IfcStructuralPlanarAction::is(Type::Enum v) { return v == Type::IfcStructuralPlanarAction || IfcStructuralAction::is(v); }
Type::Enum IfcStructuralPlanarAction::type() { return Type::IfcStructuralPlanarAction; }
Type::Enum IfcStructuralPlanarAction::Class() { return Type::IfcStructuralPlanarAction; }
IfcStructuralPlanarAction::IfcStructuralPlanarAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPlanarAction)) throw; entity = e; } 
// IfcStructuralPlanarActionVarying
SHARED_PTR<IfcShapeAspect> IfcStructuralPlanarActionVarying::VaryingAppliedLoadLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(12)); }
SHARED_PTR< IfcTemplatedEntityList<IfcStructuralLoad> > IfcStructuralPlanarActionVarying::SubsequentAppliedLoads() { RETURN_AS_LIST(IfcStructuralLoad,13) }
bool IfcStructuralPlanarActionVarying::is(Type::Enum v) { return v == Type::IfcStructuralPlanarActionVarying || IfcStructuralPlanarAction::is(v); }
Type::Enum IfcStructuralPlanarActionVarying::type() { return Type::IfcStructuralPlanarActionVarying; }
Type::Enum IfcStructuralPlanarActionVarying::Class() { return Type::IfcStructuralPlanarActionVarying; }
IfcStructuralPlanarActionVarying::IfcStructuralPlanarActionVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPlanarActionVarying)) throw; entity = e; } 
// IfcStructuralPointAction
bool IfcStructuralPointAction::is(Type::Enum v) { return v == Type::IfcStructuralPointAction || IfcStructuralAction::is(v); }
Type::Enum IfcStructuralPointAction::type() { return Type::IfcStructuralPointAction; }
Type::Enum IfcStructuralPointAction::Class() { return Type::IfcStructuralPointAction; }
IfcStructuralPointAction::IfcStructuralPointAction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPointAction)) throw; entity = e; } 
// IfcStructuralPointConnection
bool IfcStructuralPointConnection::is(Type::Enum v) { return v == Type::IfcStructuralPointConnection || IfcStructuralConnection::is(v); }
Type::Enum IfcStructuralPointConnection::type() { return Type::IfcStructuralPointConnection; }
Type::Enum IfcStructuralPointConnection::Class() { return Type::IfcStructuralPointConnection; }
IfcStructuralPointConnection::IfcStructuralPointConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPointConnection)) throw; entity = e; } 
// IfcStructuralPointReaction
bool IfcStructuralPointReaction::is(Type::Enum v) { return v == Type::IfcStructuralPointReaction || IfcStructuralReaction::is(v); }
Type::Enum IfcStructuralPointReaction::type() { return Type::IfcStructuralPointReaction; }
Type::Enum IfcStructuralPointReaction::Class() { return Type::IfcStructuralPointReaction; }
IfcStructuralPointReaction::IfcStructuralPointReaction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralPointReaction)) throw; entity = e; } 
// IfcStructuralProfileProperties
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
bool IfcStructuralProfileProperties::is(Type::Enum v) { return v == Type::IfcStructuralProfileProperties || IfcGeneralProfileProperties::is(v); }
Type::Enum IfcStructuralProfileProperties::type() { return Type::IfcStructuralProfileProperties; }
Type::Enum IfcStructuralProfileProperties::Class() { return Type::IfcStructuralProfileProperties; }
IfcStructuralProfileProperties::IfcStructuralProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralProfileProperties)) throw; entity = e; } 
// IfcStructuralReaction
IfcStructuralAction::list IfcStructuralReaction::Causes() { RETURN_INVERSE(IfcStructuralAction) }
bool IfcStructuralReaction::is(Type::Enum v) { return v == Type::IfcStructuralReaction || IfcStructuralActivity::is(v); }
Type::Enum IfcStructuralReaction::type() { return Type::IfcStructuralReaction; }
Type::Enum IfcStructuralReaction::Class() { return Type::IfcStructuralReaction; }
IfcStructuralReaction::IfcStructuralReaction(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralReaction)) throw; entity = e; } 
// IfcStructuralResultGroup
IfcAnalysisTheoryTypeEnum::IfcAnalysisTheoryTypeEnum IfcStructuralResultGroup::TheoryType() { return IfcAnalysisTheoryTypeEnum::FromString(*entity->getArgument(5)); }
bool IfcStructuralResultGroup::hasResultForLoadGroup() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR<IfcStructuralLoadGroup> IfcStructuralResultGroup::ResultForLoadGroup() { return reinterpret_pointer_cast<IfcBaseClass,IfcStructuralLoadGroup>(*entity->getArgument(6)); }
bool IfcStructuralResultGroup::IsLinear() { return *entity->getArgument(7); }
IfcStructuralAnalysisModel::list IfcStructuralResultGroup::ResultGroupFor() { RETURN_INVERSE(IfcStructuralAnalysisModel) }
bool IfcStructuralResultGroup::is(Type::Enum v) { return v == Type::IfcStructuralResultGroup || IfcGroup::is(v); }
Type::Enum IfcStructuralResultGroup::type() { return Type::IfcStructuralResultGroup; }
Type::Enum IfcStructuralResultGroup::Class() { return Type::IfcStructuralResultGroup; }
IfcStructuralResultGroup::IfcStructuralResultGroup(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralResultGroup)) throw; entity = e; } 
// IfcStructuralSteelProfileProperties
bool IfcStructuralSteelProfileProperties::hasShearAreaZ() { return !entity->getArgument(23)->isNull(); }
IfcAreaMeasure IfcStructuralSteelProfileProperties::ShearAreaZ() { return *entity->getArgument(23); }
bool IfcStructuralSteelProfileProperties::hasShearAreaY() { return !entity->getArgument(24)->isNull(); }
IfcAreaMeasure IfcStructuralSteelProfileProperties::ShearAreaY() { return *entity->getArgument(24); }
bool IfcStructuralSteelProfileProperties::hasPlasticShapeFactorY() { return !entity->getArgument(25)->isNull(); }
IfcPositiveRatioMeasure IfcStructuralSteelProfileProperties::PlasticShapeFactorY() { return *entity->getArgument(25); }
bool IfcStructuralSteelProfileProperties::hasPlasticShapeFactorZ() { return !entity->getArgument(26)->isNull(); }
IfcPositiveRatioMeasure IfcStructuralSteelProfileProperties::PlasticShapeFactorZ() { return *entity->getArgument(26); }
bool IfcStructuralSteelProfileProperties::is(Type::Enum v) { return v == Type::IfcStructuralSteelProfileProperties || IfcStructuralProfileProperties::is(v); }
Type::Enum IfcStructuralSteelProfileProperties::type() { return Type::IfcStructuralSteelProfileProperties; }
Type::Enum IfcStructuralSteelProfileProperties::Class() { return Type::IfcStructuralSteelProfileProperties; }
IfcStructuralSteelProfileProperties::IfcStructuralSteelProfileProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSteelProfileProperties)) throw; entity = e; } 
// IfcStructuralSurfaceConnection
bool IfcStructuralSurfaceConnection::is(Type::Enum v) { return v == Type::IfcStructuralSurfaceConnection || IfcStructuralConnection::is(v); }
Type::Enum IfcStructuralSurfaceConnection::type() { return Type::IfcStructuralSurfaceConnection; }
Type::Enum IfcStructuralSurfaceConnection::Class() { return Type::IfcStructuralSurfaceConnection; }
IfcStructuralSurfaceConnection::IfcStructuralSurfaceConnection(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSurfaceConnection)) throw; entity = e; } 
// IfcStructuralSurfaceMember
IfcStructuralSurfaceTypeEnum::IfcStructuralSurfaceTypeEnum IfcStructuralSurfaceMember::PredefinedType() { return IfcStructuralSurfaceTypeEnum::FromString(*entity->getArgument(7)); }
bool IfcStructuralSurfaceMember::hasThickness() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcStructuralSurfaceMember::Thickness() { return *entity->getArgument(8); }
bool IfcStructuralSurfaceMember::is(Type::Enum v) { return v == Type::IfcStructuralSurfaceMember || IfcStructuralMember::is(v); }
Type::Enum IfcStructuralSurfaceMember::type() { return Type::IfcStructuralSurfaceMember; }
Type::Enum IfcStructuralSurfaceMember::Class() { return Type::IfcStructuralSurfaceMember; }
IfcStructuralSurfaceMember::IfcStructuralSurfaceMember(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSurfaceMember)) throw; entity = e; } 
// IfcStructuralSurfaceMemberVarying
std::vector<IfcPositiveLengthMeasure> /*[2:?]*/ IfcStructuralSurfaceMemberVarying::SubsequentThickness() { return *entity->getArgument(9); }
SHARED_PTR<IfcShapeAspect> IfcStructuralSurfaceMemberVarying::VaryingThicknessLocation() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(10)); }
bool IfcStructuralSurfaceMemberVarying::is(Type::Enum v) { return v == Type::IfcStructuralSurfaceMemberVarying || IfcStructuralSurfaceMember::is(v); }
Type::Enum IfcStructuralSurfaceMemberVarying::type() { return Type::IfcStructuralSurfaceMemberVarying; }
Type::Enum IfcStructuralSurfaceMemberVarying::Class() { return Type::IfcStructuralSurfaceMemberVarying; }
IfcStructuralSurfaceMemberVarying::IfcStructuralSurfaceMemberVarying(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuralSurfaceMemberVarying)) throw; entity = e; } 
// IfcStructuredDimensionCallout
bool IfcStructuredDimensionCallout::is(Type::Enum v) { return v == Type::IfcStructuredDimensionCallout || IfcDraughtingCallout::is(v); }
Type::Enum IfcStructuredDimensionCallout::type() { return Type::IfcStructuredDimensionCallout; }
Type::Enum IfcStructuredDimensionCallout::Class() { return Type::IfcStructuredDimensionCallout; }
IfcStructuredDimensionCallout::IfcStructuredDimensionCallout(IfcAbstractEntityPtr e) { if (!is(Type::IfcStructuredDimensionCallout)) throw; entity = e; } 
// IfcStyleModel
bool IfcStyleModel::is(Type::Enum v) { return v == Type::IfcStyleModel || IfcRepresentation::is(v); }
Type::Enum IfcStyleModel::type() { return Type::IfcStyleModel; }
Type::Enum IfcStyleModel::Class() { return Type::IfcStyleModel; }
IfcStyleModel::IfcStyleModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcStyleModel)) throw; entity = e; } 
// IfcStyledItem
bool IfcStyledItem::hasItem() { return !entity->getArgument(0)->isNull(); }
SHARED_PTR<IfcRepresentationItem> IfcStyledItem::Item() { return reinterpret_pointer_cast<IfcBaseClass,IfcRepresentationItem>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcPresentationStyleAssignment> > IfcStyledItem::Styles() { RETURN_AS_LIST(IfcPresentationStyleAssignment,1) }
bool IfcStyledItem::hasName() { return !entity->getArgument(2)->isNull(); }
IfcLabel IfcStyledItem::Name() { return *entity->getArgument(2); }
bool IfcStyledItem::is(Type::Enum v) { return v == Type::IfcStyledItem || IfcRepresentationItem::is(v); }
Type::Enum IfcStyledItem::type() { return Type::IfcStyledItem; }
Type::Enum IfcStyledItem::Class() { return Type::IfcStyledItem; }
IfcStyledItem::IfcStyledItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcStyledItem)) throw; entity = e; } 
// IfcStyledRepresentation
bool IfcStyledRepresentation::is(Type::Enum v) { return v == Type::IfcStyledRepresentation || IfcStyleModel::is(v); }
Type::Enum IfcStyledRepresentation::type() { return Type::IfcStyledRepresentation; }
Type::Enum IfcStyledRepresentation::Class() { return Type::IfcStyledRepresentation; }
IfcStyledRepresentation::IfcStyledRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcStyledRepresentation)) throw; entity = e; } 
// IfcSubContractResource
bool IfcSubContractResource::hasSubContractor() { return !entity->getArgument(9)->isNull(); }
IfcActorSelect IfcSubContractResource::SubContractor() { return *entity->getArgument(9); }
bool IfcSubContractResource::hasJobDescription() { return !entity->getArgument(10)->isNull(); }
IfcText IfcSubContractResource::JobDescription() { return *entity->getArgument(10); }
bool IfcSubContractResource::is(Type::Enum v) { return v == Type::IfcSubContractResource || IfcConstructionResource::is(v); }
Type::Enum IfcSubContractResource::type() { return Type::IfcSubContractResource; }
Type::Enum IfcSubContractResource::Class() { return Type::IfcSubContractResource; }
IfcSubContractResource::IfcSubContractResource(IfcAbstractEntityPtr e) { if (!is(Type::IfcSubContractResource)) throw; entity = e; } 
// IfcSubedge
SHARED_PTR<IfcEdge> IfcSubedge::ParentEdge() { return reinterpret_pointer_cast<IfcBaseClass,IfcEdge>(*entity->getArgument(2)); }
bool IfcSubedge::is(Type::Enum v) { return v == Type::IfcSubedge || IfcEdge::is(v); }
Type::Enum IfcSubedge::type() { return Type::IfcSubedge; }
Type::Enum IfcSubedge::Class() { return Type::IfcSubedge; }
IfcSubedge::IfcSubedge(IfcAbstractEntityPtr e) { if (!is(Type::IfcSubedge)) throw; entity = e; } 
// IfcSurface
bool IfcSurface::is(Type::Enum v) { return v == Type::IfcSurface || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcSurface::type() { return Type::IfcSurface; }
Type::Enum IfcSurface::Class() { return Type::IfcSurface; }
IfcSurface::IfcSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurface)) throw; entity = e; } 
// IfcSurfaceCurveSweptAreaSolid
SHARED_PTR<IfcCurve> IfcSurfaceCurveSweptAreaSolid::Directrix() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(2)); }
IfcParameterValue IfcSurfaceCurveSweptAreaSolid::StartParam() { return *entity->getArgument(3); }
IfcParameterValue IfcSurfaceCurveSweptAreaSolid::EndParam() { return *entity->getArgument(4); }
SHARED_PTR<IfcSurface> IfcSurfaceCurveSweptAreaSolid::ReferenceSurface() { return reinterpret_pointer_cast<IfcBaseClass,IfcSurface>(*entity->getArgument(5)); }
bool IfcSurfaceCurveSweptAreaSolid::is(Type::Enum v) { return v == Type::IfcSurfaceCurveSweptAreaSolid || IfcSweptAreaSolid::is(v); }
Type::Enum IfcSurfaceCurveSweptAreaSolid::type() { return Type::IfcSurfaceCurveSweptAreaSolid; }
Type::Enum IfcSurfaceCurveSweptAreaSolid::Class() { return Type::IfcSurfaceCurveSweptAreaSolid; }
IfcSurfaceCurveSweptAreaSolid::IfcSurfaceCurveSweptAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceCurveSweptAreaSolid)) throw; entity = e; } 
// IfcSurfaceOfLinearExtrusion
SHARED_PTR<IfcDirection> IfcSurfaceOfLinearExtrusion::ExtrudedDirection() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(2)); }
IfcLengthMeasure IfcSurfaceOfLinearExtrusion::Depth() { return *entity->getArgument(3); }
bool IfcSurfaceOfLinearExtrusion::is(Type::Enum v) { return v == Type::IfcSurfaceOfLinearExtrusion || IfcSweptSurface::is(v); }
Type::Enum IfcSurfaceOfLinearExtrusion::type() { return Type::IfcSurfaceOfLinearExtrusion; }
Type::Enum IfcSurfaceOfLinearExtrusion::Class() { return Type::IfcSurfaceOfLinearExtrusion; }
IfcSurfaceOfLinearExtrusion::IfcSurfaceOfLinearExtrusion(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceOfLinearExtrusion)) throw; entity = e; } 
// IfcSurfaceOfRevolution
SHARED_PTR<IfcAxis1Placement> IfcSurfaceOfRevolution::AxisPosition() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis1Placement>(*entity->getArgument(2)); }
bool IfcSurfaceOfRevolution::is(Type::Enum v) { return v == Type::IfcSurfaceOfRevolution || IfcSweptSurface::is(v); }
Type::Enum IfcSurfaceOfRevolution::type() { return Type::IfcSurfaceOfRevolution; }
Type::Enum IfcSurfaceOfRevolution::Class() { return Type::IfcSurfaceOfRevolution; }
IfcSurfaceOfRevolution::IfcSurfaceOfRevolution(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceOfRevolution)) throw; entity = e; } 
// IfcSurfaceStyle
IfcSurfaceSide::IfcSurfaceSide IfcSurfaceStyle::Side() { return IfcSurfaceSide::FromString(*entity->getArgument(1)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcSurfaceStyle::Styles() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcSurfaceStyle::is(Type::Enum v) { return v == Type::IfcSurfaceStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcSurfaceStyle::type() { return Type::IfcSurfaceStyle; }
Type::Enum IfcSurfaceStyle::Class() { return Type::IfcSurfaceStyle; }
IfcSurfaceStyle::IfcSurfaceStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyle)) throw; entity = e; } 
// IfcSurfaceStyleLighting
SHARED_PTR<IfcColourRgb> IfcSurfaceStyleLighting::DiffuseTransmissionColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(0)); }
SHARED_PTR<IfcColourRgb> IfcSurfaceStyleLighting::DiffuseReflectionColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(1)); }
SHARED_PTR<IfcColourRgb> IfcSurfaceStyleLighting::TransmissionColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(2)); }
SHARED_PTR<IfcColourRgb> IfcSurfaceStyleLighting::ReflectanceColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(3)); }
bool IfcSurfaceStyleLighting::is(Type::Enum v) { return v == Type::IfcSurfaceStyleLighting; }
Type::Enum IfcSurfaceStyleLighting::type() { return Type::IfcSurfaceStyleLighting; }
Type::Enum IfcSurfaceStyleLighting::Class() { return Type::IfcSurfaceStyleLighting; }
IfcSurfaceStyleLighting::IfcSurfaceStyleLighting(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleLighting)) throw; entity = e; } 
// IfcSurfaceStyleRefraction
bool IfcSurfaceStyleRefraction::hasRefractionIndex() { return !entity->getArgument(0)->isNull(); }
IfcReal IfcSurfaceStyleRefraction::RefractionIndex() { return *entity->getArgument(0); }
bool IfcSurfaceStyleRefraction::hasDispersionFactor() { return !entity->getArgument(1)->isNull(); }
IfcReal IfcSurfaceStyleRefraction::DispersionFactor() { return *entity->getArgument(1); }
bool IfcSurfaceStyleRefraction::is(Type::Enum v) { return v == Type::IfcSurfaceStyleRefraction; }
Type::Enum IfcSurfaceStyleRefraction::type() { return Type::IfcSurfaceStyleRefraction; }
Type::Enum IfcSurfaceStyleRefraction::Class() { return Type::IfcSurfaceStyleRefraction; }
IfcSurfaceStyleRefraction::IfcSurfaceStyleRefraction(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleRefraction)) throw; entity = e; } 
// IfcSurfaceStyleRendering
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
bool IfcSurfaceStyleRendering::is(Type::Enum v) { return v == Type::IfcSurfaceStyleRendering || IfcSurfaceStyleShading::is(v); }
Type::Enum IfcSurfaceStyleRendering::type() { return Type::IfcSurfaceStyleRendering; }
Type::Enum IfcSurfaceStyleRendering::Class() { return Type::IfcSurfaceStyleRendering; }
IfcSurfaceStyleRendering::IfcSurfaceStyleRendering(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleRendering)) throw; entity = e; } 
// IfcSurfaceStyleShading
SHARED_PTR<IfcColourRgb> IfcSurfaceStyleShading::SurfaceColour() { return reinterpret_pointer_cast<IfcBaseClass,IfcColourRgb>(*entity->getArgument(0)); }
bool IfcSurfaceStyleShading::is(Type::Enum v) { return v == Type::IfcSurfaceStyleShading; }
Type::Enum IfcSurfaceStyleShading::type() { return Type::IfcSurfaceStyleShading; }
Type::Enum IfcSurfaceStyleShading::Class() { return Type::IfcSurfaceStyleShading; }
IfcSurfaceStyleShading::IfcSurfaceStyleShading(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleShading)) throw; entity = e; } 
// IfcSurfaceStyleWithTextures
SHARED_PTR< IfcTemplatedEntityList<IfcSurfaceTexture> > IfcSurfaceStyleWithTextures::Textures() { RETURN_AS_LIST(IfcSurfaceTexture,0) }
bool IfcSurfaceStyleWithTextures::is(Type::Enum v) { return v == Type::IfcSurfaceStyleWithTextures; }
Type::Enum IfcSurfaceStyleWithTextures::type() { return Type::IfcSurfaceStyleWithTextures; }
Type::Enum IfcSurfaceStyleWithTextures::Class() { return Type::IfcSurfaceStyleWithTextures; }
IfcSurfaceStyleWithTextures::IfcSurfaceStyleWithTextures(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceStyleWithTextures)) throw; entity = e; } 
// IfcSurfaceTexture
bool IfcSurfaceTexture::RepeatS() { return *entity->getArgument(0); }
bool IfcSurfaceTexture::RepeatT() { return *entity->getArgument(1); }
IfcSurfaceTextureEnum::IfcSurfaceTextureEnum IfcSurfaceTexture::TextureType() { return IfcSurfaceTextureEnum::FromString(*entity->getArgument(2)); }
bool IfcSurfaceTexture::hasTextureTransform() { return !entity->getArgument(3)->isNull(); }
SHARED_PTR<IfcCartesianTransformationOperator2D> IfcSurfaceTexture::TextureTransform() { return reinterpret_pointer_cast<IfcBaseClass,IfcCartesianTransformationOperator2D>(*entity->getArgument(3)); }
bool IfcSurfaceTexture::is(Type::Enum v) { return v == Type::IfcSurfaceTexture; }
Type::Enum IfcSurfaceTexture::type() { return Type::IfcSurfaceTexture; }
Type::Enum IfcSurfaceTexture::Class() { return Type::IfcSurfaceTexture; }
IfcSurfaceTexture::IfcSurfaceTexture(IfcAbstractEntityPtr e) { if (!is(Type::IfcSurfaceTexture)) throw; entity = e; } 
// IfcSweptAreaSolid
SHARED_PTR<IfcProfileDef> IfcSweptAreaSolid::SweptArea() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(0)); }
SHARED_PTR<IfcAxis2Placement3D> IfcSweptAreaSolid::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(1)); }
bool IfcSweptAreaSolid::is(Type::Enum v) { return v == Type::IfcSweptAreaSolid || IfcSolidModel::is(v); }
Type::Enum IfcSweptAreaSolid::type() { return Type::IfcSweptAreaSolid; }
Type::Enum IfcSweptAreaSolid::Class() { return Type::IfcSweptAreaSolid; }
IfcSweptAreaSolid::IfcSweptAreaSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcSweptAreaSolid)) throw; entity = e; } 
// IfcSweptDiskSolid
SHARED_PTR<IfcCurve> IfcSweptDiskSolid::Directrix() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
IfcPositiveLengthMeasure IfcSweptDiskSolid::Radius() { return *entity->getArgument(1); }
bool IfcSweptDiskSolid::hasInnerRadius() { return !entity->getArgument(2)->isNull(); }
IfcPositiveLengthMeasure IfcSweptDiskSolid::InnerRadius() { return *entity->getArgument(2); }
IfcParameterValue IfcSweptDiskSolid::StartParam() { return *entity->getArgument(3); }
IfcParameterValue IfcSweptDiskSolid::EndParam() { return *entity->getArgument(4); }
bool IfcSweptDiskSolid::is(Type::Enum v) { return v == Type::IfcSweptDiskSolid || IfcSolidModel::is(v); }
Type::Enum IfcSweptDiskSolid::type() { return Type::IfcSweptDiskSolid; }
Type::Enum IfcSweptDiskSolid::Class() { return Type::IfcSweptDiskSolid; }
IfcSweptDiskSolid::IfcSweptDiskSolid(IfcAbstractEntityPtr e) { if (!is(Type::IfcSweptDiskSolid)) throw; entity = e; } 
// IfcSweptSurface
SHARED_PTR<IfcProfileDef> IfcSweptSurface::SweptCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcProfileDef>(*entity->getArgument(0)); }
SHARED_PTR<IfcAxis2Placement3D> IfcSweptSurface::Position() { return reinterpret_pointer_cast<IfcBaseClass,IfcAxis2Placement3D>(*entity->getArgument(1)); }
bool IfcSweptSurface::is(Type::Enum v) { return v == Type::IfcSweptSurface || IfcSurface::is(v); }
Type::Enum IfcSweptSurface::type() { return Type::IfcSweptSurface; }
Type::Enum IfcSweptSurface::Class() { return Type::IfcSweptSurface; }
IfcSweptSurface::IfcSweptSurface(IfcAbstractEntityPtr e) { if (!is(Type::IfcSweptSurface)) throw; entity = e; } 
// IfcSwitchingDeviceType
IfcSwitchingDeviceTypeEnum::IfcSwitchingDeviceTypeEnum IfcSwitchingDeviceType::PredefinedType() { return IfcSwitchingDeviceTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcSwitchingDeviceType::is(Type::Enum v) { return v == Type::IfcSwitchingDeviceType || IfcFlowControllerType::is(v); }
Type::Enum IfcSwitchingDeviceType::type() { return Type::IfcSwitchingDeviceType; }
Type::Enum IfcSwitchingDeviceType::Class() { return Type::IfcSwitchingDeviceType; }
IfcSwitchingDeviceType::IfcSwitchingDeviceType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSwitchingDeviceType)) throw; entity = e; } 
// IfcSymbolStyle
IfcSymbolStyleSelect IfcSymbolStyle::StyleOfSymbol() { return *entity->getArgument(1); }
bool IfcSymbolStyle::is(Type::Enum v) { return v == Type::IfcSymbolStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcSymbolStyle::type() { return Type::IfcSymbolStyle; }
Type::Enum IfcSymbolStyle::Class() { return Type::IfcSymbolStyle; }
IfcSymbolStyle::IfcSymbolStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcSymbolStyle)) throw; entity = e; } 
// IfcSystem
IfcRelServicesBuildings::list IfcSystem::ServicesBuildings() { RETURN_INVERSE(IfcRelServicesBuildings) }
bool IfcSystem::is(Type::Enum v) { return v == Type::IfcSystem || IfcGroup::is(v); }
Type::Enum IfcSystem::type() { return Type::IfcSystem; }
Type::Enum IfcSystem::Class() { return Type::IfcSystem; }
IfcSystem::IfcSystem(IfcAbstractEntityPtr e) { if (!is(Type::IfcSystem)) throw; entity = e; } 
// IfcSystemFurnitureElementType
bool IfcSystemFurnitureElementType::is(Type::Enum v) { return v == Type::IfcSystemFurnitureElementType || IfcFurnishingElementType::is(v); }
Type::Enum IfcSystemFurnitureElementType::type() { return Type::IfcSystemFurnitureElementType; }
Type::Enum IfcSystemFurnitureElementType::Class() { return Type::IfcSystemFurnitureElementType; }
IfcSystemFurnitureElementType::IfcSystemFurnitureElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcSystemFurnitureElementType)) throw; entity = e; } 
// IfcTShapeProfileDef
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
bool IfcTShapeProfileDef::is(Type::Enum v) { return v == Type::IfcTShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcTShapeProfileDef::type() { return Type::IfcTShapeProfileDef; }
Type::Enum IfcTShapeProfileDef::Class() { return Type::IfcTShapeProfileDef; }
IfcTShapeProfileDef::IfcTShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcTShapeProfileDef)) throw; entity = e; } 
// IfcTable
std::string IfcTable::Name() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcTableRow> > IfcTable::Rows() { RETURN_AS_LIST(IfcTableRow,1) }
bool IfcTable::is(Type::Enum v) { return v == Type::IfcTable; }
Type::Enum IfcTable::type() { return Type::IfcTable; }
Type::Enum IfcTable::Class() { return Type::IfcTable; }
IfcTable::IfcTable(IfcAbstractEntityPtr e) { if (!is(Type::IfcTable)) throw; entity = e; } 
// IfcTableRow
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTableRow::RowCells() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcTableRow::IsHeading() { return *entity->getArgument(1); }
IfcTable::list IfcTableRow::OfTable() { RETURN_INVERSE(IfcTable) }
bool IfcTableRow::is(Type::Enum v) { return v == Type::IfcTableRow; }
Type::Enum IfcTableRow::type() { return Type::IfcTableRow; }
Type::Enum IfcTableRow::Class() { return Type::IfcTableRow; }
IfcTableRow::IfcTableRow(IfcAbstractEntityPtr e) { if (!is(Type::IfcTableRow)) throw; entity = e; } 
// IfcTankType
IfcTankTypeEnum::IfcTankTypeEnum IfcTankType::PredefinedType() { return IfcTankTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTankType::is(Type::Enum v) { return v == Type::IfcTankType || IfcFlowStorageDeviceType::is(v); }
Type::Enum IfcTankType::type() { return Type::IfcTankType; }
Type::Enum IfcTankType::Class() { return Type::IfcTankType; }
IfcTankType::IfcTankType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTankType)) throw; entity = e; } 
// IfcTask
IfcIdentifier IfcTask::TaskId() { return *entity->getArgument(5); }
bool IfcTask::hasStatus() { return !entity->getArgument(6)->isNull(); }
IfcLabel IfcTask::Status() { return *entity->getArgument(6); }
bool IfcTask::hasWorkMethod() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcTask::WorkMethod() { return *entity->getArgument(7); }
bool IfcTask::IsMilestone() { return *entity->getArgument(8); }
bool IfcTask::hasPriority() { return !entity->getArgument(9)->isNull(); }
int IfcTask::Priority() { return *entity->getArgument(9); }
bool IfcTask::is(Type::Enum v) { return v == Type::IfcTask || IfcProcess::is(v); }
Type::Enum IfcTask::type() { return Type::IfcTask; }
Type::Enum IfcTask::Class() { return Type::IfcTask; }
IfcTask::IfcTask(IfcAbstractEntityPtr e) { if (!is(Type::IfcTask)) throw; entity = e; } 
// IfcTelecomAddress
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
bool IfcTelecomAddress::is(Type::Enum v) { return v == Type::IfcTelecomAddress || IfcAddress::is(v); }
Type::Enum IfcTelecomAddress::type() { return Type::IfcTelecomAddress; }
Type::Enum IfcTelecomAddress::Class() { return Type::IfcTelecomAddress; }
IfcTelecomAddress::IfcTelecomAddress(IfcAbstractEntityPtr e) { if (!is(Type::IfcTelecomAddress)) throw; entity = e; } 
// IfcTendon
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
bool IfcTendon::is(Type::Enum v) { return v == Type::IfcTendon || IfcReinforcingElement::is(v); }
Type::Enum IfcTendon::type() { return Type::IfcTendon; }
Type::Enum IfcTendon::Class() { return Type::IfcTendon; }
IfcTendon::IfcTendon(IfcAbstractEntityPtr e) { if (!is(Type::IfcTendon)) throw; entity = e; } 
// IfcTendonAnchor
bool IfcTendonAnchor::is(Type::Enum v) { return v == Type::IfcTendonAnchor || IfcReinforcingElement::is(v); }
Type::Enum IfcTendonAnchor::type() { return Type::IfcTendonAnchor; }
Type::Enum IfcTendonAnchor::Class() { return Type::IfcTendonAnchor; }
IfcTendonAnchor::IfcTendonAnchor(IfcAbstractEntityPtr e) { if (!is(Type::IfcTendonAnchor)) throw; entity = e; } 
// IfcTerminatorSymbol
SHARED_PTR<IfcAnnotationCurveOccurrence> IfcTerminatorSymbol::AnnotatedCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcAnnotationCurveOccurrence>(*entity->getArgument(3)); }
bool IfcTerminatorSymbol::is(Type::Enum v) { return v == Type::IfcTerminatorSymbol || IfcAnnotationSymbolOccurrence::is(v); }
Type::Enum IfcTerminatorSymbol::type() { return Type::IfcTerminatorSymbol; }
Type::Enum IfcTerminatorSymbol::Class() { return Type::IfcTerminatorSymbol; }
IfcTerminatorSymbol::IfcTerminatorSymbol(IfcAbstractEntityPtr e) { if (!is(Type::IfcTerminatorSymbol)) throw; entity = e; } 
// IfcTextLiteral
IfcPresentableText IfcTextLiteral::Literal() { return *entity->getArgument(0); }
IfcAxis2Placement IfcTextLiteral::Placement() { return *entity->getArgument(1); }
IfcTextPath::IfcTextPath IfcTextLiteral::Path() { return IfcTextPath::FromString(*entity->getArgument(2)); }
bool IfcTextLiteral::is(Type::Enum v) { return v == Type::IfcTextLiteral || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcTextLiteral::type() { return Type::IfcTextLiteral; }
Type::Enum IfcTextLiteral::Class() { return Type::IfcTextLiteral; }
IfcTextLiteral::IfcTextLiteral(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextLiteral)) throw; entity = e; } 
// IfcTextLiteralWithExtent
SHARED_PTR<IfcPlanarExtent> IfcTextLiteralWithExtent::Extent() { return reinterpret_pointer_cast<IfcBaseClass,IfcPlanarExtent>(*entity->getArgument(3)); }
IfcBoxAlignment IfcTextLiteralWithExtent::BoxAlignment() { return *entity->getArgument(4); }
bool IfcTextLiteralWithExtent::is(Type::Enum v) { return v == Type::IfcTextLiteralWithExtent || IfcTextLiteral::is(v); }
Type::Enum IfcTextLiteralWithExtent::type() { return Type::IfcTextLiteralWithExtent; }
Type::Enum IfcTextLiteralWithExtent::Class() { return Type::IfcTextLiteralWithExtent; }
IfcTextLiteralWithExtent::IfcTextLiteralWithExtent(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextLiteralWithExtent)) throw; entity = e; } 
// IfcTextStyle
bool IfcTextStyle::hasTextCharacterAppearance() { return !entity->getArgument(1)->isNull(); }
IfcCharacterStyleSelect IfcTextStyle::TextCharacterAppearance() { return *entity->getArgument(1); }
bool IfcTextStyle::hasTextStyle() { return !entity->getArgument(2)->isNull(); }
IfcTextStyleSelect IfcTextStyle::TextStyle() { return *entity->getArgument(2); }
IfcTextFontSelect IfcTextStyle::TextFontStyle() { return *entity->getArgument(3); }
bool IfcTextStyle::is(Type::Enum v) { return v == Type::IfcTextStyle || IfcPresentationStyle::is(v); }
Type::Enum IfcTextStyle::type() { return Type::IfcTextStyle; }
Type::Enum IfcTextStyle::Class() { return Type::IfcTextStyle; }
IfcTextStyle::IfcTextStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyle)) throw; entity = e; } 
// IfcTextStyleFontModel
bool IfcTextStyleFontModel::hasFontFamily() { return !entity->getArgument(1)->isNull(); }
std::vector<IfcTextFontName> /*[1:?]*/ IfcTextStyleFontModel::FontFamily() { return *entity->getArgument(1); }
bool IfcTextStyleFontModel::hasFontStyle() { return !entity->getArgument(2)->isNull(); }
IfcFontStyle IfcTextStyleFontModel::FontStyle() { return *entity->getArgument(2); }
bool IfcTextStyleFontModel::hasFontVariant() { return !entity->getArgument(3)->isNull(); }
IfcFontVariant IfcTextStyleFontModel::FontVariant() { return *entity->getArgument(3); }
bool IfcTextStyleFontModel::hasFontWeight() { return !entity->getArgument(4)->isNull(); }
IfcFontWeight IfcTextStyleFontModel::FontWeight() { return *entity->getArgument(4); }
IfcSizeSelect IfcTextStyleFontModel::FontSize() { return *entity->getArgument(5); }
bool IfcTextStyleFontModel::is(Type::Enum v) { return v == Type::IfcTextStyleFontModel || IfcPreDefinedTextFont::is(v); }
Type::Enum IfcTextStyleFontModel::type() { return Type::IfcTextStyleFontModel; }
Type::Enum IfcTextStyleFontModel::Class() { return Type::IfcTextStyleFontModel; }
IfcTextStyleFontModel::IfcTextStyleFontModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleFontModel)) throw; entity = e; } 
// IfcTextStyleForDefinedFont
IfcColour IfcTextStyleForDefinedFont::Colour() { return *entity->getArgument(0); }
bool IfcTextStyleForDefinedFont::hasBackgroundColour() { return !entity->getArgument(1)->isNull(); }
IfcColour IfcTextStyleForDefinedFont::BackgroundColour() { return *entity->getArgument(1); }
bool IfcTextStyleForDefinedFont::is(Type::Enum v) { return v == Type::IfcTextStyleForDefinedFont; }
Type::Enum IfcTextStyleForDefinedFont::type() { return Type::IfcTextStyleForDefinedFont; }
Type::Enum IfcTextStyleForDefinedFont::Class() { return Type::IfcTextStyleForDefinedFont; }
IfcTextStyleForDefinedFont::IfcTextStyleForDefinedFont(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleForDefinedFont)) throw; entity = e; } 
// IfcTextStyleTextModel
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
bool IfcTextStyleTextModel::is(Type::Enum v) { return v == Type::IfcTextStyleTextModel; }
Type::Enum IfcTextStyleTextModel::type() { return Type::IfcTextStyleTextModel; }
Type::Enum IfcTextStyleTextModel::Class() { return Type::IfcTextStyleTextModel; }
IfcTextStyleTextModel::IfcTextStyleTextModel(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleTextModel)) throw; entity = e; } 
// IfcTextStyleWithBoxCharacteristics
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
bool IfcTextStyleWithBoxCharacteristics::is(Type::Enum v) { return v == Type::IfcTextStyleWithBoxCharacteristics; }
Type::Enum IfcTextStyleWithBoxCharacteristics::type() { return Type::IfcTextStyleWithBoxCharacteristics; }
Type::Enum IfcTextStyleWithBoxCharacteristics::Class() { return Type::IfcTextStyleWithBoxCharacteristics; }
IfcTextStyleWithBoxCharacteristics::IfcTextStyleWithBoxCharacteristics(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextStyleWithBoxCharacteristics)) throw; entity = e; } 
// IfcTextureCoordinate
IfcAnnotationSurface::list IfcTextureCoordinate::AnnotatedSurface() { RETURN_INVERSE(IfcAnnotationSurface) }
bool IfcTextureCoordinate::is(Type::Enum v) { return v == Type::IfcTextureCoordinate; }
Type::Enum IfcTextureCoordinate::type() { return Type::IfcTextureCoordinate; }
Type::Enum IfcTextureCoordinate::Class() { return Type::IfcTextureCoordinate; }
IfcTextureCoordinate::IfcTextureCoordinate(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureCoordinate)) throw; entity = e; } 
// IfcTextureCoordinateGenerator
IfcLabel IfcTextureCoordinateGenerator::Mode() { return *entity->getArgument(0); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTextureCoordinateGenerator::Parameter() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcTextureCoordinateGenerator::is(Type::Enum v) { return v == Type::IfcTextureCoordinateGenerator || IfcTextureCoordinate::is(v); }
Type::Enum IfcTextureCoordinateGenerator::type() { return Type::IfcTextureCoordinateGenerator; }
Type::Enum IfcTextureCoordinateGenerator::Class() { return Type::IfcTextureCoordinateGenerator; }
IfcTextureCoordinateGenerator::IfcTextureCoordinateGenerator(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureCoordinateGenerator)) throw; entity = e; } 
// IfcTextureMap
SHARED_PTR< IfcTemplatedEntityList<IfcVertexBasedTextureMap> > IfcTextureMap::TextureMaps() { RETURN_AS_LIST(IfcVertexBasedTextureMap,0) }
bool IfcTextureMap::is(Type::Enum v) { return v == Type::IfcTextureMap || IfcTextureCoordinate::is(v); }
Type::Enum IfcTextureMap::type() { return Type::IfcTextureMap; }
Type::Enum IfcTextureMap::Class() { return Type::IfcTextureMap; }
IfcTextureMap::IfcTextureMap(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureMap)) throw; entity = e; } 
// IfcTextureVertex
std::vector<IfcParameterValue> /*[2:2]*/ IfcTextureVertex::Coordinates() { return *entity->getArgument(0); }
bool IfcTextureVertex::is(Type::Enum v) { return v == Type::IfcTextureVertex; }
Type::Enum IfcTextureVertex::type() { return Type::IfcTextureVertex; }
Type::Enum IfcTextureVertex::Class() { return Type::IfcTextureVertex; }
IfcTextureVertex::IfcTextureVertex(IfcAbstractEntityPtr e) { if (!is(Type::IfcTextureVertex)) throw; entity = e; } 
// IfcThermalMaterialProperties
bool IfcThermalMaterialProperties::hasSpecificHeatCapacity() { return !entity->getArgument(1)->isNull(); }
IfcSpecificHeatCapacityMeasure IfcThermalMaterialProperties::SpecificHeatCapacity() { return *entity->getArgument(1); }
bool IfcThermalMaterialProperties::hasBoilingPoint() { return !entity->getArgument(2)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcThermalMaterialProperties::BoilingPoint() { return *entity->getArgument(2); }
bool IfcThermalMaterialProperties::hasFreezingPoint() { return !entity->getArgument(3)->isNull(); }
IfcThermodynamicTemperatureMeasure IfcThermalMaterialProperties::FreezingPoint() { return *entity->getArgument(3); }
bool IfcThermalMaterialProperties::hasThermalConductivity() { return !entity->getArgument(4)->isNull(); }
IfcThermalConductivityMeasure IfcThermalMaterialProperties::ThermalConductivity() { return *entity->getArgument(4); }
bool IfcThermalMaterialProperties::is(Type::Enum v) { return v == Type::IfcThermalMaterialProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcThermalMaterialProperties::type() { return Type::IfcThermalMaterialProperties; }
Type::Enum IfcThermalMaterialProperties::Class() { return Type::IfcThermalMaterialProperties; }
IfcThermalMaterialProperties::IfcThermalMaterialProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcThermalMaterialProperties)) throw; entity = e; } 
// IfcTimeSeries
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
bool IfcTimeSeries::is(Type::Enum v) { return v == Type::IfcTimeSeries; }
Type::Enum IfcTimeSeries::type() { return Type::IfcTimeSeries; }
Type::Enum IfcTimeSeries::Class() { return Type::IfcTimeSeries; }
IfcTimeSeries::IfcTimeSeries(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeries)) throw; entity = e; } 
// IfcTimeSeriesReferenceRelationship
SHARED_PTR<IfcTimeSeries> IfcTimeSeriesReferenceRelationship::ReferencedTimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTimeSeriesReferenceRelationship::TimeSeriesReferences() { RETURN_AS_LIST(IfcAbstractSelect,1) }
bool IfcTimeSeriesReferenceRelationship::is(Type::Enum v) { return v == Type::IfcTimeSeriesReferenceRelationship; }
Type::Enum IfcTimeSeriesReferenceRelationship::type() { return Type::IfcTimeSeriesReferenceRelationship; }
Type::Enum IfcTimeSeriesReferenceRelationship::Class() { return Type::IfcTimeSeriesReferenceRelationship; }
IfcTimeSeriesReferenceRelationship::IfcTimeSeriesReferenceRelationship(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeriesReferenceRelationship)) throw; entity = e; } 
// IfcTimeSeriesSchedule
bool IfcTimeSeriesSchedule::hasApplicableDates() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTimeSeriesSchedule::ApplicableDates() { RETURN_AS_LIST(IfcAbstractSelect,5) }
IfcTimeSeriesScheduleTypeEnum::IfcTimeSeriesScheduleTypeEnum IfcTimeSeriesSchedule::TimeSeriesScheduleType() { return IfcTimeSeriesScheduleTypeEnum::FromString(*entity->getArgument(6)); }
SHARED_PTR<IfcTimeSeries> IfcTimeSeriesSchedule::TimeSeries() { return reinterpret_pointer_cast<IfcBaseClass,IfcTimeSeries>(*entity->getArgument(7)); }
bool IfcTimeSeriesSchedule::is(Type::Enum v) { return v == Type::IfcTimeSeriesSchedule || IfcControl::is(v); }
Type::Enum IfcTimeSeriesSchedule::type() { return Type::IfcTimeSeriesSchedule; }
Type::Enum IfcTimeSeriesSchedule::Class() { return Type::IfcTimeSeriesSchedule; }
IfcTimeSeriesSchedule::IfcTimeSeriesSchedule(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeriesSchedule)) throw; entity = e; } 
// IfcTimeSeriesValue
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTimeSeriesValue::ListValues() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcTimeSeriesValue::is(Type::Enum v) { return v == Type::IfcTimeSeriesValue; }
Type::Enum IfcTimeSeriesValue::type() { return Type::IfcTimeSeriesValue; }
Type::Enum IfcTimeSeriesValue::Class() { return Type::IfcTimeSeriesValue; }
IfcTimeSeriesValue::IfcTimeSeriesValue(IfcAbstractEntityPtr e) { if (!is(Type::IfcTimeSeriesValue)) throw; entity = e; } 
// IfcTopologicalRepresentationItem
bool IfcTopologicalRepresentationItem::is(Type::Enum v) { return v == Type::IfcTopologicalRepresentationItem || IfcRepresentationItem::is(v); }
Type::Enum IfcTopologicalRepresentationItem::type() { return Type::IfcTopologicalRepresentationItem; }
Type::Enum IfcTopologicalRepresentationItem::Class() { return Type::IfcTopologicalRepresentationItem; }
IfcTopologicalRepresentationItem::IfcTopologicalRepresentationItem(IfcAbstractEntityPtr e) { if (!is(Type::IfcTopologicalRepresentationItem)) throw; entity = e; } 
// IfcTopologyRepresentation
bool IfcTopologyRepresentation::is(Type::Enum v) { return v == Type::IfcTopologyRepresentation || IfcShapeModel::is(v); }
Type::Enum IfcTopologyRepresentation::type() { return Type::IfcTopologyRepresentation; }
Type::Enum IfcTopologyRepresentation::Class() { return Type::IfcTopologyRepresentation; }
IfcTopologyRepresentation::IfcTopologyRepresentation(IfcAbstractEntityPtr e) { if (!is(Type::IfcTopologyRepresentation)) throw; entity = e; } 
// IfcTransformerType
IfcTransformerTypeEnum::IfcTransformerTypeEnum IfcTransformerType::PredefinedType() { return IfcTransformerTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTransformerType::is(Type::Enum v) { return v == Type::IfcTransformerType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcTransformerType::type() { return Type::IfcTransformerType; }
Type::Enum IfcTransformerType::Class() { return Type::IfcTransformerType; }
IfcTransformerType::IfcTransformerType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTransformerType)) throw; entity = e; } 
// IfcTransportElement
bool IfcTransportElement::hasOperationType() { return !entity->getArgument(8)->isNull(); }
IfcTransportElementTypeEnum::IfcTransportElementTypeEnum IfcTransportElement::OperationType() { return IfcTransportElementTypeEnum::FromString(*entity->getArgument(8)); }
bool IfcTransportElement::hasCapacityByWeight() { return !entity->getArgument(9)->isNull(); }
IfcMassMeasure IfcTransportElement::CapacityByWeight() { return *entity->getArgument(9); }
bool IfcTransportElement::hasCapacityByNumber() { return !entity->getArgument(10)->isNull(); }
IfcCountMeasure IfcTransportElement::CapacityByNumber() { return *entity->getArgument(10); }
bool IfcTransportElement::is(Type::Enum v) { return v == Type::IfcTransportElement || IfcElement::is(v); }
Type::Enum IfcTransportElement::type() { return Type::IfcTransportElement; }
Type::Enum IfcTransportElement::Class() { return Type::IfcTransportElement; }
IfcTransportElement::IfcTransportElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcTransportElement)) throw; entity = e; } 
// IfcTransportElementType
IfcTransportElementTypeEnum::IfcTransportElementTypeEnum IfcTransportElementType::PredefinedType() { return IfcTransportElementTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTransportElementType::is(Type::Enum v) { return v == Type::IfcTransportElementType || IfcElementType::is(v); }
Type::Enum IfcTransportElementType::type() { return Type::IfcTransportElementType; }
Type::Enum IfcTransportElementType::Class() { return Type::IfcTransportElementType; }
IfcTransportElementType::IfcTransportElementType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTransportElementType)) throw; entity = e; } 
// IfcTrapeziumProfileDef
IfcPositiveLengthMeasure IfcTrapeziumProfileDef::BottomXDim() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcTrapeziumProfileDef::TopXDim() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcTrapeziumProfileDef::YDim() { return *entity->getArgument(5); }
IfcLengthMeasure IfcTrapeziumProfileDef::TopXOffset() { return *entity->getArgument(6); }
bool IfcTrapeziumProfileDef::is(Type::Enum v) { return v == Type::IfcTrapeziumProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcTrapeziumProfileDef::type() { return Type::IfcTrapeziumProfileDef; }
Type::Enum IfcTrapeziumProfileDef::Class() { return Type::IfcTrapeziumProfileDef; }
IfcTrapeziumProfileDef::IfcTrapeziumProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcTrapeziumProfileDef)) throw; entity = e; } 
// IfcTrimmedCurve
SHARED_PTR<IfcCurve> IfcTrimmedCurve::BasisCurve() { return reinterpret_pointer_cast<IfcBaseClass,IfcCurve>(*entity->getArgument(0)); }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTrimmedCurve::Trim1() { RETURN_AS_LIST(IfcAbstractSelect,1) }
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcTrimmedCurve::Trim2() { RETURN_AS_LIST(IfcAbstractSelect,2) }
bool IfcTrimmedCurve::SenseAgreement() { return *entity->getArgument(3); }
IfcTrimmingPreference::IfcTrimmingPreference IfcTrimmedCurve::MasterRepresentation() { return IfcTrimmingPreference::FromString(*entity->getArgument(4)); }
bool IfcTrimmedCurve::is(Type::Enum v) { return v == Type::IfcTrimmedCurve || IfcBoundedCurve::is(v); }
Type::Enum IfcTrimmedCurve::type() { return Type::IfcTrimmedCurve; }
Type::Enum IfcTrimmedCurve::Class() { return Type::IfcTrimmedCurve; }
IfcTrimmedCurve::IfcTrimmedCurve(IfcAbstractEntityPtr e) { if (!is(Type::IfcTrimmedCurve)) throw; entity = e; } 
// IfcTubeBundleType
IfcTubeBundleTypeEnum::IfcTubeBundleTypeEnum IfcTubeBundleType::PredefinedType() { return IfcTubeBundleTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcTubeBundleType::is(Type::Enum v) { return v == Type::IfcTubeBundleType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcTubeBundleType::type() { return Type::IfcTubeBundleType; }
Type::Enum IfcTubeBundleType::Class() { return Type::IfcTubeBundleType; }
IfcTubeBundleType::IfcTubeBundleType(IfcAbstractEntityPtr e) { if (!is(Type::IfcTubeBundleType)) throw; entity = e; } 
// IfcTwoDirectionRepeatFactor
SHARED_PTR<IfcVector> IfcTwoDirectionRepeatFactor::SecondRepeatFactor() { return reinterpret_pointer_cast<IfcBaseClass,IfcVector>(*entity->getArgument(1)); }
bool IfcTwoDirectionRepeatFactor::is(Type::Enum v) { return v == Type::IfcTwoDirectionRepeatFactor || IfcOneDirectionRepeatFactor::is(v); }
Type::Enum IfcTwoDirectionRepeatFactor::type() { return Type::IfcTwoDirectionRepeatFactor; }
Type::Enum IfcTwoDirectionRepeatFactor::Class() { return Type::IfcTwoDirectionRepeatFactor; }
IfcTwoDirectionRepeatFactor::IfcTwoDirectionRepeatFactor(IfcAbstractEntityPtr e) { if (!is(Type::IfcTwoDirectionRepeatFactor)) throw; entity = e; } 
// IfcTypeObject
bool IfcTypeObject::hasApplicableOccurrence() { return !entity->getArgument(4)->isNull(); }
IfcLabel IfcTypeObject::ApplicableOccurrence() { return *entity->getArgument(4); }
bool IfcTypeObject::hasHasPropertySets() { return !entity->getArgument(5)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcPropertySetDefinition> > IfcTypeObject::HasPropertySets() { RETURN_AS_LIST(IfcPropertySetDefinition,5) }
IfcRelDefinesByType::list IfcTypeObject::ObjectTypeOf() { RETURN_INVERSE(IfcRelDefinesByType) }
bool IfcTypeObject::is(Type::Enum v) { return v == Type::IfcTypeObject || IfcObjectDefinition::is(v); }
Type::Enum IfcTypeObject::type() { return Type::IfcTypeObject; }
Type::Enum IfcTypeObject::Class() { return Type::IfcTypeObject; }
IfcTypeObject::IfcTypeObject(IfcAbstractEntityPtr e) { if (!is(Type::IfcTypeObject)) throw; entity = e; } 
// IfcTypeProduct
bool IfcTypeProduct::hasRepresentationMaps() { return !entity->getArgument(6)->isNull(); }
SHARED_PTR< IfcTemplatedEntityList<IfcRepresentationMap> > IfcTypeProduct::RepresentationMaps() { RETURN_AS_LIST(IfcRepresentationMap,6) }
bool IfcTypeProduct::hasTag() { return !entity->getArgument(7)->isNull(); }
IfcLabel IfcTypeProduct::Tag() { return *entity->getArgument(7); }
bool IfcTypeProduct::is(Type::Enum v) { return v == Type::IfcTypeProduct || IfcTypeObject::is(v); }
Type::Enum IfcTypeProduct::type() { return Type::IfcTypeProduct; }
Type::Enum IfcTypeProduct::Class() { return Type::IfcTypeProduct; }
IfcTypeProduct::IfcTypeProduct(IfcAbstractEntityPtr e) { if (!is(Type::IfcTypeProduct)) throw; entity = e; } 
// IfcUShapeProfileDef
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
bool IfcUShapeProfileDef::is(Type::Enum v) { return v == Type::IfcUShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcUShapeProfileDef::type() { return Type::IfcUShapeProfileDef; }
Type::Enum IfcUShapeProfileDef::Class() { return Type::IfcUShapeProfileDef; }
IfcUShapeProfileDef::IfcUShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcUShapeProfileDef)) throw; entity = e; } 
// IfcUnitAssignment
SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > IfcUnitAssignment::Units() { RETURN_AS_LIST(IfcAbstractSelect,0) }
bool IfcUnitAssignment::is(Type::Enum v) { return v == Type::IfcUnitAssignment; }
Type::Enum IfcUnitAssignment::type() { return Type::IfcUnitAssignment; }
Type::Enum IfcUnitAssignment::Class() { return Type::IfcUnitAssignment; }
IfcUnitAssignment::IfcUnitAssignment(IfcAbstractEntityPtr e) { if (!is(Type::IfcUnitAssignment)) throw; entity = e; } 
// IfcUnitaryEquipmentType
IfcUnitaryEquipmentTypeEnum::IfcUnitaryEquipmentTypeEnum IfcUnitaryEquipmentType::PredefinedType() { return IfcUnitaryEquipmentTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcUnitaryEquipmentType::is(Type::Enum v) { return v == Type::IfcUnitaryEquipmentType || IfcEnergyConversionDeviceType::is(v); }
Type::Enum IfcUnitaryEquipmentType::type() { return Type::IfcUnitaryEquipmentType; }
Type::Enum IfcUnitaryEquipmentType::Class() { return Type::IfcUnitaryEquipmentType; }
IfcUnitaryEquipmentType::IfcUnitaryEquipmentType(IfcAbstractEntityPtr e) { if (!is(Type::IfcUnitaryEquipmentType)) throw; entity = e; } 
// IfcValveType
IfcValveTypeEnum::IfcValveTypeEnum IfcValveType::PredefinedType() { return IfcValveTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcValveType::is(Type::Enum v) { return v == Type::IfcValveType || IfcFlowControllerType::is(v); }
Type::Enum IfcValveType::type() { return Type::IfcValveType; }
Type::Enum IfcValveType::Class() { return Type::IfcValveType; }
IfcValveType::IfcValveType(IfcAbstractEntityPtr e) { if (!is(Type::IfcValveType)) throw; entity = e; } 
// IfcVector
SHARED_PTR<IfcDirection> IfcVector::Orientation() { return reinterpret_pointer_cast<IfcBaseClass,IfcDirection>(*entity->getArgument(0)); }
IfcLengthMeasure IfcVector::Magnitude() { return *entity->getArgument(1); }
bool IfcVector::is(Type::Enum v) { return v == Type::IfcVector || IfcGeometricRepresentationItem::is(v); }
Type::Enum IfcVector::type() { return Type::IfcVector; }
Type::Enum IfcVector::Class() { return Type::IfcVector; }
IfcVector::IfcVector(IfcAbstractEntityPtr e) { if (!is(Type::IfcVector)) throw; entity = e; } 
// IfcVertex
bool IfcVertex::is(Type::Enum v) { return v == Type::IfcVertex || IfcTopologicalRepresentationItem::is(v); }
Type::Enum IfcVertex::type() { return Type::IfcVertex; }
Type::Enum IfcVertex::Class() { return Type::IfcVertex; }
IfcVertex::IfcVertex(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertex)) throw; entity = e; } 
// IfcVertexBasedTextureMap
SHARED_PTR< IfcTemplatedEntityList<IfcTextureVertex> > IfcVertexBasedTextureMap::TextureVertices() { RETURN_AS_LIST(IfcTextureVertex,0) }
SHARED_PTR< IfcTemplatedEntityList<IfcCartesianPoint> > IfcVertexBasedTextureMap::TexturePoints() { RETURN_AS_LIST(IfcCartesianPoint,1) }
bool IfcVertexBasedTextureMap::is(Type::Enum v) { return v == Type::IfcVertexBasedTextureMap; }
Type::Enum IfcVertexBasedTextureMap::type() { return Type::IfcVertexBasedTextureMap; }
Type::Enum IfcVertexBasedTextureMap::Class() { return Type::IfcVertexBasedTextureMap; }
IfcVertexBasedTextureMap::IfcVertexBasedTextureMap(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertexBasedTextureMap)) throw; entity = e; } 
// IfcVertexLoop
SHARED_PTR<IfcVertex> IfcVertexLoop::LoopVertex() { return reinterpret_pointer_cast<IfcBaseClass,IfcVertex>(*entity->getArgument(0)); }
bool IfcVertexLoop::is(Type::Enum v) { return v == Type::IfcVertexLoop || IfcLoop::is(v); }
Type::Enum IfcVertexLoop::type() { return Type::IfcVertexLoop; }
Type::Enum IfcVertexLoop::Class() { return Type::IfcVertexLoop; }
IfcVertexLoop::IfcVertexLoop(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertexLoop)) throw; entity = e; } 
// IfcVertexPoint
SHARED_PTR<IfcPoint> IfcVertexPoint::VertexGeometry() { return reinterpret_pointer_cast<IfcBaseClass,IfcPoint>(*entity->getArgument(0)); }
bool IfcVertexPoint::is(Type::Enum v) { return v == Type::IfcVertexPoint || IfcVertex::is(v); }
Type::Enum IfcVertexPoint::type() { return Type::IfcVertexPoint; }
Type::Enum IfcVertexPoint::Class() { return Type::IfcVertexPoint; }
IfcVertexPoint::IfcVertexPoint(IfcAbstractEntityPtr e) { if (!is(Type::IfcVertexPoint)) throw; entity = e; } 
// IfcVibrationIsolatorType
IfcVibrationIsolatorTypeEnum::IfcVibrationIsolatorTypeEnum IfcVibrationIsolatorType::PredefinedType() { return IfcVibrationIsolatorTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcVibrationIsolatorType::is(Type::Enum v) { return v == Type::IfcVibrationIsolatorType || IfcDiscreteAccessoryType::is(v); }
Type::Enum IfcVibrationIsolatorType::type() { return Type::IfcVibrationIsolatorType; }
Type::Enum IfcVibrationIsolatorType::Class() { return Type::IfcVibrationIsolatorType; }
IfcVibrationIsolatorType::IfcVibrationIsolatorType(IfcAbstractEntityPtr e) { if (!is(Type::IfcVibrationIsolatorType)) throw; entity = e; } 
// IfcVirtualElement
bool IfcVirtualElement::is(Type::Enum v) { return v == Type::IfcVirtualElement || IfcElement::is(v); }
Type::Enum IfcVirtualElement::type() { return Type::IfcVirtualElement; }
Type::Enum IfcVirtualElement::Class() { return Type::IfcVirtualElement; }
IfcVirtualElement::IfcVirtualElement(IfcAbstractEntityPtr e) { if (!is(Type::IfcVirtualElement)) throw; entity = e; } 
// IfcVirtualGridIntersection
SHARED_PTR< IfcTemplatedEntityList<IfcGridAxis> > IfcVirtualGridIntersection::IntersectingAxes() { RETURN_AS_LIST(IfcGridAxis,0) }
std::vector<IfcLengthMeasure> /*[2:3]*/ IfcVirtualGridIntersection::OffsetDistances() { return *entity->getArgument(1); }
bool IfcVirtualGridIntersection::is(Type::Enum v) { return v == Type::IfcVirtualGridIntersection; }
Type::Enum IfcVirtualGridIntersection::type() { return Type::IfcVirtualGridIntersection; }
Type::Enum IfcVirtualGridIntersection::Class() { return Type::IfcVirtualGridIntersection; }
IfcVirtualGridIntersection::IfcVirtualGridIntersection(IfcAbstractEntityPtr e) { if (!is(Type::IfcVirtualGridIntersection)) throw; entity = e; } 
// IfcWall
bool IfcWall::is(Type::Enum v) { return v == Type::IfcWall || IfcBuildingElement::is(v); }
Type::Enum IfcWall::type() { return Type::IfcWall; }
Type::Enum IfcWall::Class() { return Type::IfcWall; }
IfcWall::IfcWall(IfcAbstractEntityPtr e) { if (!is(Type::IfcWall)) throw; entity = e; } 
// IfcWallStandardCase
bool IfcWallStandardCase::is(Type::Enum v) { return v == Type::IfcWallStandardCase || IfcWall::is(v); }
Type::Enum IfcWallStandardCase::type() { return Type::IfcWallStandardCase; }
Type::Enum IfcWallStandardCase::Class() { return Type::IfcWallStandardCase; }
IfcWallStandardCase::IfcWallStandardCase(IfcAbstractEntityPtr e) { if (!is(Type::IfcWallStandardCase)) throw; entity = e; } 
// IfcWallType
IfcWallTypeEnum::IfcWallTypeEnum IfcWallType::PredefinedType() { return IfcWallTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcWallType::is(Type::Enum v) { return v == Type::IfcWallType || IfcBuildingElementType::is(v); }
Type::Enum IfcWallType::type() { return Type::IfcWallType; }
Type::Enum IfcWallType::Class() { return Type::IfcWallType; }
IfcWallType::IfcWallType(IfcAbstractEntityPtr e) { if (!is(Type::IfcWallType)) throw; entity = e; } 
// IfcWasteTerminalType
IfcWasteTerminalTypeEnum::IfcWasteTerminalTypeEnum IfcWasteTerminalType::PredefinedType() { return IfcWasteTerminalTypeEnum::FromString(*entity->getArgument(9)); }
bool IfcWasteTerminalType::is(Type::Enum v) { return v == Type::IfcWasteTerminalType || IfcFlowTerminalType::is(v); }
Type::Enum IfcWasteTerminalType::type() { return Type::IfcWasteTerminalType; }
Type::Enum IfcWasteTerminalType::Class() { return Type::IfcWasteTerminalType; }
IfcWasteTerminalType::IfcWasteTerminalType(IfcAbstractEntityPtr e) { if (!is(Type::IfcWasteTerminalType)) throw; entity = e; } 
// IfcWaterProperties
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
bool IfcWaterProperties::is(Type::Enum v) { return v == Type::IfcWaterProperties || IfcMaterialProperties::is(v); }
Type::Enum IfcWaterProperties::type() { return Type::IfcWaterProperties; }
Type::Enum IfcWaterProperties::Class() { return Type::IfcWaterProperties; }
IfcWaterProperties::IfcWaterProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcWaterProperties)) throw; entity = e; } 
// IfcWindow
bool IfcWindow::hasOverallHeight() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcWindow::OverallHeight() { return *entity->getArgument(8); }
bool IfcWindow::hasOverallWidth() { return !entity->getArgument(9)->isNull(); }
IfcPositiveLengthMeasure IfcWindow::OverallWidth() { return *entity->getArgument(9); }
bool IfcWindow::is(Type::Enum v) { return v == Type::IfcWindow || IfcBuildingElement::is(v); }
Type::Enum IfcWindow::type() { return Type::IfcWindow; }
Type::Enum IfcWindow::Class() { return Type::IfcWindow; }
IfcWindow::IfcWindow(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindow)) throw; entity = e; } 
// IfcWindowLiningProperties
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
SHARED_PTR<IfcShapeAspect> IfcWindowLiningProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(12)); }
bool IfcWindowLiningProperties::is(Type::Enum v) { return v == Type::IfcWindowLiningProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcWindowLiningProperties::type() { return Type::IfcWindowLiningProperties; }
Type::Enum IfcWindowLiningProperties::Class() { return Type::IfcWindowLiningProperties; }
IfcWindowLiningProperties::IfcWindowLiningProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindowLiningProperties)) throw; entity = e; } 
// IfcWindowPanelProperties
IfcWindowPanelOperationEnum::IfcWindowPanelOperationEnum IfcWindowPanelProperties::OperationType() { return IfcWindowPanelOperationEnum::FromString(*entity->getArgument(4)); }
IfcWindowPanelPositionEnum::IfcWindowPanelPositionEnum IfcWindowPanelProperties::PanelPosition() { return IfcWindowPanelPositionEnum::FromString(*entity->getArgument(5)); }
bool IfcWindowPanelProperties::hasFrameDepth() { return !entity->getArgument(6)->isNull(); }
IfcPositiveLengthMeasure IfcWindowPanelProperties::FrameDepth() { return *entity->getArgument(6); }
bool IfcWindowPanelProperties::hasFrameThickness() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcWindowPanelProperties::FrameThickness() { return *entity->getArgument(7); }
bool IfcWindowPanelProperties::hasShapeAspectStyle() { return !entity->getArgument(8)->isNull(); }
SHARED_PTR<IfcShapeAspect> IfcWindowPanelProperties::ShapeAspectStyle() { return reinterpret_pointer_cast<IfcBaseClass,IfcShapeAspect>(*entity->getArgument(8)); }
bool IfcWindowPanelProperties::is(Type::Enum v) { return v == Type::IfcWindowPanelProperties || IfcPropertySetDefinition::is(v); }
Type::Enum IfcWindowPanelProperties::type() { return Type::IfcWindowPanelProperties; }
Type::Enum IfcWindowPanelProperties::Class() { return Type::IfcWindowPanelProperties; }
IfcWindowPanelProperties::IfcWindowPanelProperties(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindowPanelProperties)) throw; entity = e; } 
// IfcWindowStyle
IfcWindowStyleConstructionEnum::IfcWindowStyleConstructionEnum IfcWindowStyle::ConstructionType() { return IfcWindowStyleConstructionEnum::FromString(*entity->getArgument(8)); }
IfcWindowStyleOperationEnum::IfcWindowStyleOperationEnum IfcWindowStyle::OperationType() { return IfcWindowStyleOperationEnum::FromString(*entity->getArgument(9)); }
bool IfcWindowStyle::ParameterTakesPrecedence() { return *entity->getArgument(10); }
bool IfcWindowStyle::Sizeable() { return *entity->getArgument(11); }
bool IfcWindowStyle::is(Type::Enum v) { return v == Type::IfcWindowStyle || IfcTypeProduct::is(v); }
Type::Enum IfcWindowStyle::type() { return Type::IfcWindowStyle; }
Type::Enum IfcWindowStyle::Class() { return Type::IfcWindowStyle; }
IfcWindowStyle::IfcWindowStyle(IfcAbstractEntityPtr e) { if (!is(Type::IfcWindowStyle)) throw; entity = e; } 
// IfcWorkControl
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
bool IfcWorkControl::is(Type::Enum v) { return v == Type::IfcWorkControl || IfcControl::is(v); }
Type::Enum IfcWorkControl::type() { return Type::IfcWorkControl; }
Type::Enum IfcWorkControl::Class() { return Type::IfcWorkControl; }
IfcWorkControl::IfcWorkControl(IfcAbstractEntityPtr e) { if (!is(Type::IfcWorkControl)) throw; entity = e; } 
// IfcWorkPlan
bool IfcWorkPlan::is(Type::Enum v) { return v == Type::IfcWorkPlan || IfcWorkControl::is(v); }
Type::Enum IfcWorkPlan::type() { return Type::IfcWorkPlan; }
Type::Enum IfcWorkPlan::Class() { return Type::IfcWorkPlan; }
IfcWorkPlan::IfcWorkPlan(IfcAbstractEntityPtr e) { if (!is(Type::IfcWorkPlan)) throw; entity = e; } 
// IfcWorkSchedule
bool IfcWorkSchedule::is(Type::Enum v) { return v == Type::IfcWorkSchedule || IfcWorkControl::is(v); }
Type::Enum IfcWorkSchedule::type() { return Type::IfcWorkSchedule; }
Type::Enum IfcWorkSchedule::Class() { return Type::IfcWorkSchedule; }
IfcWorkSchedule::IfcWorkSchedule(IfcAbstractEntityPtr e) { if (!is(Type::IfcWorkSchedule)) throw; entity = e; } 
// IfcZShapeProfileDef
IfcPositiveLengthMeasure IfcZShapeProfileDef::Depth() { return *entity->getArgument(3); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::FlangeWidth() { return *entity->getArgument(4); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::WebThickness() { return *entity->getArgument(5); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::FlangeThickness() { return *entity->getArgument(6); }
bool IfcZShapeProfileDef::hasFilletRadius() { return !entity->getArgument(7)->isNull(); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::FilletRadius() { return *entity->getArgument(7); }
bool IfcZShapeProfileDef::hasEdgeRadius() { return !entity->getArgument(8)->isNull(); }
IfcPositiveLengthMeasure IfcZShapeProfileDef::EdgeRadius() { return *entity->getArgument(8); }
bool IfcZShapeProfileDef::is(Type::Enum v) { return v == Type::IfcZShapeProfileDef || IfcParameterizedProfileDef::is(v); }
Type::Enum IfcZShapeProfileDef::type() { return Type::IfcZShapeProfileDef; }
Type::Enum IfcZShapeProfileDef::Class() { return Type::IfcZShapeProfileDef; }
IfcZShapeProfileDef::IfcZShapeProfileDef(IfcAbstractEntityPtr e) { if (!is(Type::IfcZShapeProfileDef)) throw; entity = e; } 
// IfcZone
bool IfcZone::is(Type::Enum v) { return v == Type::IfcZone || IfcGroup::is(v); }
Type::Enum IfcZone::type() { return Type::IfcZone; }
Type::Enum IfcZone::Class() { return Type::IfcZone; }
IfcZone::IfcZone(IfcAbstractEntityPtr e) { if (!is(Type::IfcZone)) throw; entity = e; }