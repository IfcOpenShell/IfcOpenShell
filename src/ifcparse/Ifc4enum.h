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
 * This file has been generated from IFC4.exp. Do not make modifications        *
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#ifndef IFC4ENUM_H
#define IFC4ENUM_H

#include "../ifcparse/IfcParse_Export.h"

#include <boost/optional.hpp>

#define IfcSchema Ifc4

namespace Ifc4 {

namespace Type {
    typedef enum {
        IfcAbsorbedDoseMeasure, IfcAccelerationMeasure, IfcActionRequest, IfcActionRequestTypeEnum, IfcActionSourceTypeEnum, IfcActionTypeEnum, IfcActor, IfcActorRole, IfcActorSelect, IfcActuator, IfcActuatorType, IfcActuatorTypeEnum, IfcAddress, IfcAddressTypeEnum, IfcAdvancedBrep, IfcAdvancedBrepWithVoids, IfcAdvancedFace, IfcAirTerminal, IfcAirTerminalBox, IfcAirTerminalBoxType, IfcAirTerminalBoxTypeEnum, IfcAirTerminalType, IfcAirTerminalTypeEnum, IfcAirToAirHeatRecovery, IfcAirToAirHeatRecoveryType, IfcAirToAirHeatRecoveryTypeEnum, IfcAlarm, IfcAlarmType, IfcAlarmTypeEnum, IfcAmountOfSubstanceMeasure, IfcAnalysisModelTypeEnum, IfcAnalysisTheoryTypeEnum, IfcAngularVelocityMeasure, IfcAnnotation, IfcAnnotationFillArea, IfcApplication, IfcAppliedValue, IfcAppliedValueSelect, IfcApproval, IfcApprovalRelationship, IfcArbitraryClosedProfileDef, IfcArbitraryOpenProfileDef, IfcArbitraryProfileDefWithVoids, IfcArcIndex, IfcAreaDensityMeasure, IfcAreaMeasure, IfcArithmeticOperatorEnum, IfcAssemblyPlaceEnum, IfcAsset, IfcAsymmetricIShapeProfileDef, IfcAudioVisualAppliance, IfcAudioVisualApplianceType, IfcAudioVisualApplianceTypeEnum, IfcAxis1Placement, IfcAxis2Placement, IfcAxis2Placement2D, IfcAxis2Placement3D, IfcBSplineCurve, IfcBSplineCurveForm, IfcBSplineCurveWithKnots, IfcBSplineSurface, IfcBSplineSurfaceForm, IfcBSplineSurfaceWithKnots, IfcBeam, IfcBeamStandardCase, IfcBeamType, IfcBeamTypeEnum, IfcBenchmarkEnum, IfcBendingParameterSelect, IfcBinary, IfcBlobTexture, IfcBlock, IfcBoiler, IfcBoilerType, IfcBoilerTypeEnum, IfcBoolean, IfcBooleanClippingResult, IfcBooleanOperand, IfcBooleanOperator, IfcBooleanResult, IfcBoundaryCondition, IfcBoundaryCurve, IfcBoundaryEdgeCondition, IfcBoundaryFaceCondition, IfcBoundaryNodeCondition, IfcBoundaryNodeConditionWarping, IfcBoundedCurve, IfcBoundedSurface, IfcBoundingBox, IfcBoxAlignment, IfcBoxedHalfSpace, IfcBuilding, IfcBuildingElement, IfcBuildingElementPart, IfcBuildingElementPartType, IfcBuildingElementPartTypeEnum, IfcBuildingElementProxy, IfcBuildingElementProxyType, IfcBuildingElementProxyTypeEnum, IfcBuildingElementType, IfcBuildingStorey, IfcBuildingSystem, IfcBuildingSystemTypeEnum, IfcBurner, IfcBurnerType, IfcBurnerTypeEnum, IfcCShapeProfileDef, IfcCableCarrierFitting, IfcCableCarrierFittingType, IfcCableCarrierFittingTypeEnum, IfcCableCarrierSegment, IfcCableCarrierSegmentType, IfcCableCarrierSegmentTypeEnum, IfcCableFitting, IfcCableFittingType, IfcCableFittingTypeEnum, IfcCableSegment, IfcCableSegmentType, IfcCableSegmentTypeEnum, IfcCardinalPointReference, IfcCartesianPoint, IfcCartesianPointList, IfcCartesianPointList2D, IfcCartesianPointList3D, IfcCartesianTransformationOperator, IfcCartesianTransformationOperator2D, IfcCartesianTransformationOperator2DnonUniform, IfcCartesianTransformationOperator3D, IfcCartesianTransformationOperator3DnonUniform, IfcCenterLineProfileDef, IfcChangeActionEnum, IfcChiller, IfcChillerType, IfcChillerTypeEnum, IfcChimney, IfcChimneyType, IfcChimneyTypeEnum, IfcCircle, IfcCircleHollowProfileDef, IfcCircleProfileDef, IfcCivilElement, IfcCivilElementType, IfcClassification, IfcClassificationReference, IfcClassificationReferenceSelect, IfcClassificationSelect, IfcClosedShell, IfcCoil, IfcCoilType, IfcCoilTypeEnum, IfcColour, IfcColourOrFactor, IfcColourRgb, IfcColourRgbList, IfcColourSpecification, IfcColumn, IfcColumnStandardCase, IfcColumnType, IfcColumnTypeEnum, IfcCommunicationsAppliance, IfcCommunicationsApplianceType, IfcCommunicationsApplianceTypeEnum, IfcComplexNumber, IfcComplexProperty, IfcComplexPropertyTemplate, IfcComplexPropertyTemplateTypeEnum, IfcCompositeCurve, IfcCompositeCurveOnSurface, IfcCompositeCurveSegment, IfcCompositeProfileDef, IfcCompoundPlaneAngleMeasure, IfcCompressor, IfcCompressorType, IfcCompressorTypeEnum, IfcCondenser, IfcCondenserType, IfcCondenserTypeEnum, IfcConic, IfcConnectedFaceSet, IfcConnectionCurveGeometry, IfcConnectionGeometry, IfcConnectionPointEccentricity, IfcConnectionPointGeometry, IfcConnectionSurfaceGeometry, IfcConnectionTypeEnum, IfcConnectionVolumeGeometry, IfcConstraint, IfcConstraintEnum, IfcConstructionEquipmentResource, IfcConstructionEquipmentResourceType, IfcConstructionEquipmentResourceTypeEnum, IfcConstructionMaterialResource, IfcConstructionMaterialResourceType, IfcConstructionMaterialResourceTypeEnum, IfcConstructionProductResource, IfcConstructionProductResourceType, IfcConstructionProductResourceTypeEnum, IfcConstructionResource, IfcConstructionResourceType, IfcContext, IfcContextDependentMeasure, IfcContextDependentUnit, IfcControl, IfcController, IfcControllerType, IfcControllerTypeEnum, IfcConversionBasedUnit, IfcConversionBasedUnitWithOffset, IfcCooledBeam, IfcCooledBeamType, IfcCooledBeamTypeEnum, IfcCoolingTower, IfcCoolingTowerType, IfcCoolingTowerTypeEnum, IfcCoordinateOperation, IfcCoordinateReferenceSystem, IfcCoordinateReferenceSystemSelect, IfcCostItem, IfcCostItemTypeEnum, IfcCostSchedule, IfcCostScheduleTypeEnum, IfcCostValue, IfcCountMeasure, IfcCovering, IfcCoveringType, IfcCoveringTypeEnum, IfcCrewResource, IfcCrewResourceType, IfcCrewResourceTypeEnum, IfcCsgPrimitive3D, IfcCsgSelect, IfcCsgSolid, IfcCurrencyRelationship, IfcCurtainWall, IfcCurtainWallType, IfcCurtainWallTypeEnum, IfcCurvatureMeasure, IfcCurve, IfcCurveBoundedPlane, IfcCurveBoundedSurface, IfcCurveFontOrScaledCurveFontSelect, IfcCurveInterpolationEnum, IfcCurveOnSurface, IfcCurveOrEdgeCurve, IfcCurveStyle, IfcCurveStyleFont, IfcCurveStyleFontAndScaling, IfcCurveStyleFontPattern, IfcCurveStyleFontSelect, IfcCylindricalSurface, IfcDamper, IfcDamperType, IfcDamperTypeEnum, IfcDataOriginEnum, IfcDate, IfcDateTime, IfcDayInMonthNumber, IfcDayInWeekNumber, IfcDefinitionSelect, IfcDerivedMeasureValue, IfcDerivedProfileDef, IfcDerivedUnit, IfcDerivedUnitElement, IfcDerivedUnitEnum, IfcDescriptiveMeasure, IfcDimensionCount, IfcDimensionalExponents, IfcDirection, IfcDirectionSenseEnum, IfcDiscreteAccessory, IfcDiscreteAccessoryType, IfcDiscreteAccessoryTypeEnum, IfcDistributionChamberElement, IfcDistributionChamberElementType, IfcDistributionChamberElementTypeEnum, IfcDistributionCircuit, IfcDistributionControlElement, IfcDistributionControlElementType, IfcDistributionElement, IfcDistributionElementType, IfcDistributionFlowElement, IfcDistributionFlowElementType, IfcDistributionPort, IfcDistributionPortTypeEnum, IfcDistributionSystem, IfcDistributionSystemEnum, IfcDocumentConfidentialityEnum, IfcDocumentInformation, IfcDocumentInformationRelationship, IfcDocumentReference, IfcDocumentSelect, IfcDocumentStatusEnum, IfcDoor, IfcDoorLiningProperties, IfcDoorPanelOperationEnum, IfcDoorPanelPositionEnum, IfcDoorPanelProperties, IfcDoorStandardCase, IfcDoorStyle, IfcDoorStyleConstructionEnum, IfcDoorStyleOperationEnum, IfcDoorType, IfcDoorTypeEnum, IfcDoorTypeOperationEnum, IfcDoseEquivalentMeasure, IfcDraughtingPreDefinedColour, IfcDraughtingPreDefinedCurveFont, IfcDuctFitting, IfcDuctFittingType, IfcDuctFittingTypeEnum, IfcDuctSegment, IfcDuctSegmentType, IfcDuctSegmentTypeEnum, IfcDuctSilencer, IfcDuctSilencerType, IfcDuctSilencerTypeEnum, IfcDuration, IfcDynamicViscosityMeasure, IfcEdge, IfcEdgeCurve, IfcEdgeLoop, IfcElectricAppliance, IfcElectricApplianceType, IfcElectricApplianceTypeEnum, IfcElectricCapacitanceMeasure, IfcElectricChargeMeasure, IfcElectricConductanceMeasure, IfcElectricCurrentMeasure, IfcElectricDistributionBoard, IfcElectricDistributionBoardType, IfcElectricDistributionBoardTypeEnum, IfcElectricFlowStorageDevice, IfcElectricFlowStorageDeviceType, IfcElectricFlowStorageDeviceTypeEnum, IfcElectricGenerator, IfcElectricGeneratorType, IfcElectricGeneratorTypeEnum, IfcElectricMotor, IfcElectricMotorType, IfcElectricMotorTypeEnum, IfcElectricResistanceMeasure, IfcElectricTimeControl, IfcElectricTimeControlType, IfcElectricTimeControlTypeEnum, IfcElectricVoltageMeasure, IfcElement, IfcElementAssembly, IfcElementAssemblyType, IfcElementAssemblyTypeEnum, IfcElementComponent, IfcElementComponentType, IfcElementCompositionEnum, IfcElementQuantity, IfcElementType, IfcElementarySurface, IfcEllipse, IfcEllipseProfileDef, IfcEnergyConversionDevice, IfcEnergyConversionDeviceType, IfcEnergyMeasure, IfcEngine, IfcEngineType, IfcEngineTypeEnum, IfcEvaporativeCooler, IfcEvaporativeCoolerType, IfcEvaporativeCoolerTypeEnum, IfcEvaporator, IfcEvaporatorType, IfcEvaporatorTypeEnum, IfcEvent, IfcEventTime, IfcEventTriggerTypeEnum, IfcEventType, IfcEventTypeEnum, IfcExtendedProperties, IfcExternalInformation, IfcExternalReference, IfcExternalReferenceRelationship, IfcExternalSpatialElement, IfcExternalSpatialElementTypeEnum, IfcExternalSpatialStructureElement, IfcExternallyDefinedHatchStyle, IfcExternallyDefinedSurfaceStyle, IfcExternallyDefinedTextFont, IfcExtrudedAreaSolid, IfcExtrudedAreaSolidTapered, IfcFace, IfcFaceBasedSurfaceModel, IfcFaceBound, IfcFaceOuterBound, IfcFaceSurface, IfcFacetedBrep, IfcFacetedBrepWithVoids, IfcFailureConnectionCondition, IfcFan, IfcFanType, IfcFanTypeEnum, IfcFastener, IfcFastenerType, IfcFastenerTypeEnum, IfcFeatureElement, IfcFeatureElementAddition, IfcFeatureElementSubtraction, IfcFillAreaStyle, IfcFillAreaStyleHatching, IfcFillAreaStyleTiles, IfcFillStyleSelect, IfcFilter, IfcFilterType, IfcFilterTypeEnum, IfcFireSuppressionTerminal, IfcFireSuppressionTerminalType, IfcFireSuppressionTerminalTypeEnum, IfcFixedReferenceSweptAreaSolid, IfcFlowController, IfcFlowControllerType, IfcFlowDirectionEnum, IfcFlowFitting, IfcFlowFittingType, IfcFlowInstrument, IfcFlowInstrumentType, IfcFlowInstrumentTypeEnum, IfcFlowMeter, IfcFlowMeterType, IfcFlowMeterTypeEnum, IfcFlowMovingDevice, IfcFlowMovingDeviceType, IfcFlowSegment, IfcFlowSegmentType, IfcFlowStorageDevice, IfcFlowStorageDeviceType, IfcFlowTerminal, IfcFlowTerminalType, IfcFlowTreatmentDevice, IfcFlowTreatmentDeviceType, IfcFontStyle, IfcFontVariant, IfcFontWeight, IfcFooting, IfcFootingType, IfcFootingTypeEnum, IfcForceMeasure, IfcFrequencyMeasure, IfcFurnishingElement, IfcFurnishingElementType, IfcFurniture, IfcFurnitureType, IfcFurnitureTypeEnum, IfcGeographicElement, IfcGeographicElementType, IfcGeographicElementTypeEnum, IfcGeometricCurveSet, IfcGeometricProjectionEnum, IfcGeometricRepresentationContext, IfcGeometricRepresentationItem, IfcGeometricRepresentationSubContext, IfcGeometricSet, IfcGeometricSetSelect, IfcGlobalOrLocalEnum, IfcGloballyUniqueId, IfcGrid, IfcGridAxis, IfcGridPlacement, IfcGridPlacementDirectionSelect, IfcGridTypeEnum, IfcGroup, IfcHalfSpaceSolid, IfcHatchLineDistanceSelect, IfcHeatExchanger, IfcHeatExchangerType, IfcHeatExchangerTypeEnum, IfcHeatFluxDensityMeasure, IfcHeatingValueMeasure, IfcHumidifier, IfcHumidifierType, IfcHumidifierTypeEnum, IfcIShapeProfileDef, IfcIdentifier, IfcIlluminanceMeasure, IfcImageTexture, IfcIndexedColourMap, IfcIndexedPolyCurve, IfcIndexedTextureMap, IfcIndexedTriangleTextureMap, IfcInductanceMeasure, IfcInteger, IfcIntegerCountRateMeasure, IfcInterceptor, IfcInterceptorType, IfcInterceptorTypeEnum, IfcInternalOrExternalEnum, IfcInventory, IfcInventoryTypeEnum, IfcIonConcentrationMeasure, IfcIrregularTimeSeries, IfcIrregularTimeSeriesValue, IfcIsothermalMoistureCapacityMeasure, IfcJunctionBox, IfcJunctionBoxType, IfcJunctionBoxTypeEnum, IfcKinematicViscosityMeasure, IfcKnotType, IfcLShapeProfileDef, IfcLabel, IfcLaborResource, IfcLaborResourceType, IfcLaborResourceTypeEnum, IfcLagTime, IfcLamp, IfcLampType, IfcLampTypeEnum, IfcLanguageId, IfcLayerSetDirectionEnum, IfcLayeredItem, IfcLengthMeasure, IfcLibraryInformation, IfcLibraryReference, IfcLibrarySelect, IfcLightDistributionCurveEnum, IfcLightDistributionData, IfcLightDistributionDataSourceSelect, IfcLightEmissionSourceEnum, IfcLightFixture, IfcLightFixtureType, IfcLightFixtureTypeEnum, IfcLightIntensityDistribution, IfcLightSource, IfcLightSourceAmbient, IfcLightSourceDirectional, IfcLightSourceGoniometric, IfcLightSourcePositional, IfcLightSourceSpot, IfcLine, IfcLineIndex, IfcLinearForceMeasure, IfcLinearMomentMeasure, IfcLinearStiffnessMeasure, IfcLinearVelocityMeasure, IfcLoadGroupTypeEnum, IfcLocalPlacement, IfcLogical, IfcLogicalOperatorEnum, IfcLoop, IfcLuminousFluxMeasure, IfcLuminousIntensityDistributionMeasure, IfcLuminousIntensityMeasure, IfcMagneticFluxDensityMeasure, IfcMagneticFluxMeasure, IfcManifoldSolidBrep, IfcMapConversion, IfcMappedItem, IfcMassDensityMeasure, IfcMassFlowRateMeasure, IfcMassMeasure, IfcMassPerLengthMeasure, IfcMaterial, IfcMaterialClassificationRelationship, IfcMaterialConstituent, IfcMaterialConstituentSet, IfcMaterialDefinition, IfcMaterialDefinitionRepresentation, IfcMaterialLayer, IfcMaterialLayerSet, IfcMaterialLayerSetUsage, IfcMaterialLayerWithOffsets, IfcMaterialList, IfcMaterialProfile, IfcMaterialProfileSet, IfcMaterialProfileSetUsage, IfcMaterialProfileSetUsageTapering, IfcMaterialProfileWithOffsets, IfcMaterialProperties, IfcMaterialRelationship, IfcMaterialSelect, IfcMaterialUsageDefinition, IfcMeasureValue, IfcMeasureWithUnit, IfcMechanicalFastener, IfcMechanicalFastenerType, IfcMechanicalFastenerTypeEnum, IfcMedicalDevice, IfcMedicalDeviceType, IfcMedicalDeviceTypeEnum, IfcMember, IfcMemberStandardCase, IfcMemberType, IfcMemberTypeEnum, IfcMetric, IfcMetricValueSelect, IfcMirroredProfileDef, IfcModulusOfElasticityMeasure, IfcModulusOfLinearSubgradeReactionMeasure, IfcModulusOfRotationalSubgradeReactionMeasure, IfcModulusOfRotationalSubgradeReactionSelect, IfcModulusOfSubgradeReactionMeasure, IfcModulusOfSubgradeReactionSelect, IfcModulusOfTranslationalSubgradeReactionSelect, IfcMoistureDiffusivityMeasure, IfcMolecularWeightMeasure, IfcMomentOfInertiaMeasure, IfcMonetaryMeasure, IfcMonetaryUnit, IfcMonthInYearNumber, IfcMotorConnection, IfcMotorConnectionType, IfcMotorConnectionTypeEnum, IfcNamedUnit, IfcNonNegativeLengthMeasure, IfcNormalisedRatioMeasure, IfcNullStyle, IfcNumericMeasure, IfcObject, IfcObjectDefinition, IfcObjectPlacement, IfcObjectReferenceSelect, IfcObjectTypeEnum, IfcObjective, IfcObjectiveEnum, IfcOccupant, IfcOccupantTypeEnum, IfcOffsetCurve2D, IfcOffsetCurve3D, IfcOpenShell, IfcOpeningElement, IfcOpeningElementTypeEnum, IfcOpeningStandardCase, IfcOrganization, IfcOrganizationRelationship, IfcOrientedEdge, IfcOuterBoundaryCurve, IfcOutlet, IfcOutletType, IfcOutletTypeEnum, IfcOwnerHistory, IfcPHMeasure, IfcParameterValue, IfcParameterizedProfileDef, IfcPath, IfcPcurve, IfcPerformanceHistory, IfcPerformanceHistoryTypeEnum, IfcPermeableCoveringOperationEnum, IfcPermeableCoveringProperties, IfcPermit, IfcPermitTypeEnum, IfcPerson, IfcPersonAndOrganization, IfcPhysicalComplexQuantity, IfcPhysicalOrVirtualEnum, IfcPhysicalQuantity, IfcPhysicalSimpleQuantity, IfcPile, IfcPileConstructionEnum, IfcPileType, IfcPileTypeEnum, IfcPipeFitting, IfcPipeFittingType, IfcPipeFittingTypeEnum, IfcPipeSegment, IfcPipeSegmentType, IfcPipeSegmentTypeEnum, IfcPixelTexture, IfcPlacement, IfcPlanarBox, IfcPlanarExtent, IfcPlanarForceMeasure, IfcPlane, IfcPlaneAngleMeasure, IfcPlate, IfcPlateStandardCase, IfcPlateType, IfcPlateTypeEnum, IfcPoint, IfcPointOnCurve, IfcPointOnSurface, IfcPointOrVertexPoint, IfcPolyLoop, IfcPolygonalBoundedHalfSpace, IfcPolyline, IfcPort, IfcPositiveInteger, IfcPositiveLengthMeasure, IfcPositivePlaneAngleMeasure, IfcPositiveRatioMeasure, IfcPostalAddress, IfcPowerMeasure, IfcPreDefinedColour, IfcPreDefinedCurveFont, IfcPreDefinedItem, IfcPreDefinedProperties, IfcPreDefinedPropertySet, IfcPreDefinedTextFont, IfcPresentableText, IfcPresentationItem, IfcPresentationLayerAssignment, IfcPresentationLayerWithStyle, IfcPresentationStyle, IfcPresentationStyleAssignment, IfcPresentationStyleSelect, IfcPressureMeasure, IfcProcedure, IfcProcedureType, IfcProcedureTypeEnum, IfcProcess, IfcProcessSelect, IfcProduct, IfcProductDefinitionShape, IfcProductRepresentation, IfcProductRepresentationSelect, IfcProductSelect, IfcProfileDef, IfcProfileProperties, IfcProfileTypeEnum, IfcProject, IfcProjectLibrary, IfcProjectOrder, IfcProjectOrderTypeEnum, IfcProjectedCRS, IfcProjectedOrTrueLengthEnum, IfcProjectionElement, IfcProjectionElementTypeEnum, IfcProperty, IfcPropertyAbstraction, IfcPropertyBoundedValue, IfcPropertyDefinition, IfcPropertyDependencyRelationship, IfcPropertyEnumeratedValue, IfcPropertyEnumeration, IfcPropertyListValue, IfcPropertyReferenceValue, IfcPropertySet, IfcPropertySetDefinition, IfcPropertySetDefinitionSelect, IfcPropertySetDefinitionSet, IfcPropertySetTemplate, IfcPropertySetTemplateTypeEnum, IfcPropertySingleValue, IfcPropertyTableValue, IfcPropertyTemplate, IfcPropertyTemplateDefinition, IfcProtectiveDevice, IfcProtectiveDeviceTrippingUnit, IfcProtectiveDeviceTrippingUnitType, IfcProtectiveDeviceTrippingUnitTypeEnum, IfcProtectiveDeviceType, IfcProtectiveDeviceTypeEnum, IfcProxy, IfcPump, IfcPumpType, IfcPumpTypeEnum, IfcQuantityArea, IfcQuantityCount, IfcQuantityLength, IfcQuantitySet, IfcQuantityTime, IfcQuantityVolume, IfcQuantityWeight, IfcRadioActivityMeasure, IfcRailing, IfcRailingType, IfcRailingTypeEnum, IfcRamp, IfcRampFlight, IfcRampFlightType, IfcRampFlightTypeEnum, IfcRampType, IfcRampTypeEnum, IfcRatioMeasure, IfcRationalBSplineCurveWithKnots, IfcRationalBSplineSurfaceWithKnots, IfcReal, IfcRectangleHollowProfileDef, IfcRectangleProfileDef, IfcRectangularPyramid, IfcRectangularTrimmedSurface, IfcRecurrencePattern, IfcRecurrenceTypeEnum, IfcReference, IfcReflectanceMethodEnum, IfcRegularTimeSeries, IfcReinforcementBarProperties, IfcReinforcementDefinitionProperties, IfcReinforcingBar, IfcReinforcingBarRoleEnum, IfcReinforcingBarSurfaceEnum, IfcReinforcingBarType, IfcReinforcingBarTypeEnum, IfcReinforcingElement, IfcReinforcingElementType, IfcReinforcingMesh, IfcReinforcingMeshType, IfcReinforcingMeshTypeEnum, IfcRelAggregates, IfcRelAssigns, IfcRelAssignsToActor, IfcRelAssignsToControl, IfcRelAssignsToGroup, IfcRelAssignsToGroupByFactor, IfcRelAssignsToProcess, IfcRelAssignsToProduct, IfcRelAssignsToResource, IfcRelAssociates, IfcRelAssociatesApproval, IfcRelAssociatesClassification, IfcRelAssociatesConstraint, IfcRelAssociatesDocument, IfcRelAssociatesLibrary, IfcRelAssociatesMaterial, IfcRelConnects, IfcRelConnectsElements, IfcRelConnectsPathElements, IfcRelConnectsPortToElement, IfcRelConnectsPorts, IfcRelConnectsStructuralActivity, IfcRelConnectsStructuralMember, IfcRelConnectsWithEccentricity, IfcRelConnectsWithRealizingElements, IfcRelContainedInSpatialStructure, IfcRelCoversBldgElements, IfcRelCoversSpaces, IfcRelDeclares, IfcRelDecomposes, IfcRelDefines, IfcRelDefinesByObject, IfcRelDefinesByProperties, IfcRelDefinesByTemplate, IfcRelDefinesByType, IfcRelFillsElement, IfcRelFlowControlElements, IfcRelInterferesElements, IfcRelNests, IfcRelProjectsElement, IfcRelReferencedInSpatialStructure, IfcRelSequence, IfcRelServicesBuildings, IfcRelSpaceBoundary, IfcRelSpaceBoundary1stLevel, IfcRelSpaceBoundary2ndLevel, IfcRelVoidsElement, IfcRelationship, IfcReparametrisedCompositeCurveSegment, IfcRepresentation, IfcRepresentationContext, IfcRepresentationItem, IfcRepresentationMap, IfcResource, IfcResourceApprovalRelationship, IfcResourceConstraintRelationship, IfcResourceLevelRelationship, IfcResourceObjectSelect, IfcResourceSelect, IfcResourceTime, IfcRevolvedAreaSolid, IfcRevolvedAreaSolidTapered, IfcRightCircularCone, IfcRightCircularCylinder, IfcRoleEnum, IfcRoof, IfcRoofType, IfcRoofTypeEnum, IfcRoot, IfcRotationalFrequencyMeasure, IfcRotationalMassMeasure, IfcRotationalStiffnessMeasure, IfcRotationalStiffnessSelect, IfcRoundedRectangleProfileDef, IfcSIPrefix, IfcSIUnit, IfcSIUnitName, IfcSanitaryTerminal, IfcSanitaryTerminalType, IfcSanitaryTerminalTypeEnum, IfcSchedulingTime, IfcSectionModulusMeasure, IfcSectionProperties, IfcSectionReinforcementProperties, IfcSectionTypeEnum, IfcSectionalAreaIntegralMeasure, IfcSectionedSpine, IfcSegmentIndexSelect, IfcSensor, IfcSensorType, IfcSensorTypeEnum, IfcSequenceEnum, IfcShadingDevice, IfcShadingDeviceType, IfcShadingDeviceTypeEnum, IfcShapeAspect, IfcShapeModel, IfcShapeRepresentation, IfcShearModulusMeasure, IfcShell, IfcShellBasedSurfaceModel, IfcSimpleProperty, IfcSimplePropertyTemplate, IfcSimplePropertyTemplateTypeEnum, IfcSimpleValue, IfcSite, IfcSizeSelect, IfcSlab, IfcSlabElementedCase, IfcSlabStandardCase, IfcSlabType, IfcSlabTypeEnum, IfcSlippageConnectionCondition, IfcSolarDevice, IfcSolarDeviceType, IfcSolarDeviceTypeEnum, IfcSolidAngleMeasure, IfcSolidModel, IfcSolidOrShell, IfcSoundPowerLevelMeasure, IfcSoundPowerMeasure, IfcSoundPressureLevelMeasure, IfcSoundPressureMeasure, IfcSpace, IfcSpaceBoundarySelect, IfcSpaceHeater, IfcSpaceHeaterType, IfcSpaceHeaterTypeEnum, IfcSpaceType, IfcSpaceTypeEnum, IfcSpatialElement, IfcSpatialElementType, IfcSpatialStructureElement, IfcSpatialStructureElementType, IfcSpatialZone, IfcSpatialZoneType, IfcSpatialZoneTypeEnum, IfcSpecificHeatCapacityMeasure, IfcSpecularExponent, IfcSpecularHighlightSelect, IfcSpecularRoughness, IfcSphere, IfcStackTerminal, IfcStackTerminalType, IfcStackTerminalTypeEnum, IfcStair, IfcStairFlight, IfcStairFlightType, IfcStairFlightTypeEnum, IfcStairType, IfcStairTypeEnum, IfcStateEnum, IfcStructuralAction, IfcStructuralActivity, IfcStructuralActivityAssignmentSelect, IfcStructuralAnalysisModel, IfcStructuralConnection, IfcStructuralConnectionCondition, IfcStructuralCurveAction, IfcStructuralCurveActivityTypeEnum, IfcStructuralCurveConnection, IfcStructuralCurveMember, IfcStructuralCurveMemberTypeEnum, IfcStructuralCurveMemberVarying, IfcStructuralCurveReaction, IfcStructuralItem, IfcStructuralLinearAction, IfcStructuralLoad, IfcStructuralLoadCase, IfcStructuralLoadConfiguration, IfcStructuralLoadGroup, IfcStructuralLoadLinearForce, IfcStructuralLoadOrResult, IfcStructuralLoadPlanarForce, IfcStructuralLoadSingleDisplacement, IfcStructuralLoadSingleDisplacementDistortion, IfcStructuralLoadSingleForce, IfcStructuralLoadSingleForceWarping, IfcStructuralLoadStatic, IfcStructuralLoadTemperature, IfcStructuralMember, IfcStructuralPlanarAction, IfcStructuralPointAction, IfcStructuralPointConnection, IfcStructuralPointReaction, IfcStructuralReaction, IfcStructuralResultGroup, IfcStructuralSurfaceAction, IfcStructuralSurfaceActivityTypeEnum, IfcStructuralSurfaceConnection, IfcStructuralSurfaceMember, IfcStructuralSurfaceMemberTypeEnum, IfcStructuralSurfaceMemberVarying, IfcStructuralSurfaceReaction, IfcStyleAssignmentSelect, IfcStyleModel, IfcStyledItem, IfcStyledRepresentation, IfcSubContractResource, IfcSubContractResourceType, IfcSubContractResourceTypeEnum, IfcSubedge, IfcSurface, IfcSurfaceCurveSweptAreaSolid, IfcSurfaceFeature, IfcSurfaceFeatureTypeEnum, IfcSurfaceOfLinearExtrusion, IfcSurfaceOfRevolution, IfcSurfaceOrFaceSurface, IfcSurfaceReinforcementArea, IfcSurfaceSide, IfcSurfaceStyle, IfcSurfaceStyleElementSelect, IfcSurfaceStyleLighting, IfcSurfaceStyleRefraction, IfcSurfaceStyleRendering, IfcSurfaceStyleShading, IfcSurfaceStyleWithTextures, IfcSurfaceTexture, IfcSweptAreaSolid, IfcSweptDiskSolid, IfcSweptDiskSolidPolygonal, IfcSweptSurface, IfcSwitchingDevice, IfcSwitchingDeviceType, IfcSwitchingDeviceTypeEnum, IfcSystem, IfcSystemFurnitureElement, IfcSystemFurnitureElementType, IfcSystemFurnitureElementTypeEnum, IfcTShapeProfileDef, IfcTable, IfcTableColumn, IfcTableRow, IfcTank, IfcTankType, IfcTankTypeEnum, IfcTask, IfcTaskDurationEnum, IfcTaskTime, IfcTaskTimeRecurring, IfcTaskType, IfcTaskTypeEnum, IfcTelecomAddress, IfcTemperatureGradientMeasure, IfcTemperatureRateOfChangeMeasure, IfcTendon, IfcTendonAnchor, IfcTendonAnchorType, IfcTendonAnchorTypeEnum, IfcTendonType, IfcTendonTypeEnum, IfcTessellatedFaceSet, IfcTessellatedItem, IfcText, IfcTextAlignment, IfcTextDecoration, IfcTextFontName, IfcTextFontSelect, IfcTextLiteral, IfcTextLiteralWithExtent, IfcTextPath, IfcTextStyle, IfcTextStyleFontModel, IfcTextStyleForDefinedFont, IfcTextStyleTextModel, IfcTextTransformation, IfcTextureCoordinate, IfcTextureCoordinateGenerator, IfcTextureMap, IfcTextureVertex, IfcTextureVertexList, IfcThermalAdmittanceMeasure, IfcThermalConductivityMeasure, IfcThermalExpansionCoefficientMeasure, IfcThermalResistanceMeasure, IfcThermalTransmittanceMeasure, IfcThermodynamicTemperatureMeasure, IfcTime, IfcTimeMeasure, IfcTimeOrRatioSelect, IfcTimePeriod, IfcTimeSeries, IfcTimeSeriesDataTypeEnum, IfcTimeSeriesValue, IfcTimeStamp, IfcTopologicalRepresentationItem, IfcTopologyRepresentation, IfcTorqueMeasure, IfcTransformer, IfcTransformerType, IfcTransformerTypeEnum, IfcTransitionCode, IfcTranslationalStiffnessSelect, IfcTransportElement, IfcTransportElementType, IfcTransportElementTypeEnum, IfcTrapeziumProfileDef, IfcTriangulatedFaceSet, IfcTrimmedCurve, IfcTrimmingPreference, IfcTrimmingSelect, IfcTubeBundle, IfcTubeBundleType, IfcTubeBundleTypeEnum, IfcTypeObject, IfcTypeProcess, IfcTypeProduct, IfcTypeResource, IfcURIReference, IfcUShapeProfileDef, IfcUnit, IfcUnitAssignment, IfcUnitEnum, IfcUnitaryControlElement, IfcUnitaryControlElementType, IfcUnitaryControlElementTypeEnum, IfcUnitaryEquipment, IfcUnitaryEquipmentType, IfcUnitaryEquipmentTypeEnum, IfcValue, IfcValve, IfcValveType, IfcValveTypeEnum, IfcVaporPermeabilityMeasure, IfcVector, IfcVectorOrDirection, IfcVertex, IfcVertexLoop, IfcVertexPoint, IfcVibrationIsolator, IfcVibrationIsolatorType, IfcVibrationIsolatorTypeEnum, IfcVirtualElement, IfcVirtualGridIntersection, IfcVoidingFeature, IfcVoidingFeatureTypeEnum, IfcVolumeMeasure, IfcVolumetricFlowRateMeasure, IfcWall, IfcWallElementedCase, IfcWallStandardCase, IfcWallType, IfcWallTypeEnum, IfcWarpingConstantMeasure, IfcWarpingMomentMeasure, IfcWarpingStiffnessSelect, IfcWasteTerminal, IfcWasteTerminalType, IfcWasteTerminalTypeEnum, IfcWindow, IfcWindowLiningProperties, IfcWindowPanelOperationEnum, IfcWindowPanelPositionEnum, IfcWindowPanelProperties, IfcWindowStandardCase, IfcWindowStyle, IfcWindowStyleConstructionEnum, IfcWindowStyleOperationEnum, IfcWindowType, IfcWindowTypeEnum, IfcWindowTypePartitioningEnum, IfcWorkCalendar, IfcWorkCalendarTypeEnum, IfcWorkControl, IfcWorkPlan, IfcWorkPlanTypeEnum, IfcWorkSchedule, IfcWorkScheduleTypeEnum, IfcWorkTime, IfcZShapeProfileDef, IfcZone, UNDEFINED
    } Enum;
    IfcParse_EXPORT boost::optional<Enum> Parent(Enum v);
    IfcParse_EXPORT Enum FromString(const std::string& s);
    IfcParse_EXPORT std::string ToString(Enum v);
    IfcParse_EXPORT bool IsSimple(Enum v);
}

}

#endif
