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

#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/Ifc2x3.h"

using namespace IfcParse;
using namespace Ifc2x3;

entity* Ifc2DCompositeCurve_type = 0;
entity* IfcActionRequest_type = 0;
entity* IfcActor_type = 0;
entity* IfcActorRole_type = 0;
entity* IfcActuatorType_type = 0;
entity* IfcAddress_type = 0;
entity* IfcAirTerminalBoxType_type = 0;
entity* IfcAirTerminalType_type = 0;
entity* IfcAirToAirHeatRecoveryType_type = 0;
entity* IfcAlarmType_type = 0;
entity* IfcAngularDimension_type = 0;
entity* IfcAnnotation_type = 0;
entity* IfcAnnotationCurveOccurrence_type = 0;
entity* IfcAnnotationFillArea_type = 0;
entity* IfcAnnotationFillAreaOccurrence_type = 0;
entity* IfcAnnotationOccurrence_type = 0;
entity* IfcAnnotationSurface_type = 0;
entity* IfcAnnotationSurfaceOccurrence_type = 0;
entity* IfcAnnotationSymbolOccurrence_type = 0;
entity* IfcAnnotationTextOccurrence_type = 0;
entity* IfcApplication_type = 0;
entity* IfcAppliedValue_type = 0;
entity* IfcAppliedValueRelationship_type = 0;
entity* IfcApproval_type = 0;
entity* IfcApprovalActorRelationship_type = 0;
entity* IfcApprovalPropertyRelationship_type = 0;
entity* IfcApprovalRelationship_type = 0;
entity* IfcArbitraryClosedProfileDef_type = 0;
entity* IfcArbitraryOpenProfileDef_type = 0;
entity* IfcArbitraryProfileDefWithVoids_type = 0;
entity* IfcAsset_type = 0;
entity* IfcAsymmetricIShapeProfileDef_type = 0;
entity* IfcAxis1Placement_type = 0;
entity* IfcAxis2Placement2D_type = 0;
entity* IfcAxis2Placement3D_type = 0;
entity* IfcBSplineCurve_type = 0;
entity* IfcBeam_type = 0;
entity* IfcBeamType_type = 0;
entity* IfcBezierCurve_type = 0;
entity* IfcBlobTexture_type = 0;
entity* IfcBlock_type = 0;
entity* IfcBoilerType_type = 0;
entity* IfcBooleanClippingResult_type = 0;
entity* IfcBooleanResult_type = 0;
entity* IfcBoundaryCondition_type = 0;
entity* IfcBoundaryEdgeCondition_type = 0;
entity* IfcBoundaryFaceCondition_type = 0;
entity* IfcBoundaryNodeCondition_type = 0;
entity* IfcBoundaryNodeConditionWarping_type = 0;
entity* IfcBoundedCurve_type = 0;
entity* IfcBoundedSurface_type = 0;
entity* IfcBoundingBox_type = 0;
entity* IfcBoxedHalfSpace_type = 0;
entity* IfcBuilding_type = 0;
entity* IfcBuildingElement_type = 0;
entity* IfcBuildingElementComponent_type = 0;
entity* IfcBuildingElementPart_type = 0;
entity* IfcBuildingElementProxy_type = 0;
entity* IfcBuildingElementProxyType_type = 0;
entity* IfcBuildingElementType_type = 0;
entity* IfcBuildingStorey_type = 0;
entity* IfcCShapeProfileDef_type = 0;
entity* IfcCableCarrierFittingType_type = 0;
entity* IfcCableCarrierSegmentType_type = 0;
entity* IfcCableSegmentType_type = 0;
entity* IfcCalendarDate_type = 0;
entity* IfcCartesianPoint_type = 0;
entity* IfcCartesianTransformationOperator_type = 0;
entity* IfcCartesianTransformationOperator2D_type = 0;
entity* IfcCartesianTransformationOperator2DnonUniform_type = 0;
entity* IfcCartesianTransformationOperator3D_type = 0;
entity* IfcCartesianTransformationOperator3DnonUniform_type = 0;
entity* IfcCenterLineProfileDef_type = 0;
entity* IfcChamferEdgeFeature_type = 0;
entity* IfcChillerType_type = 0;
entity* IfcCircle_type = 0;
entity* IfcCircleHollowProfileDef_type = 0;
entity* IfcCircleProfileDef_type = 0;
entity* IfcClassification_type = 0;
entity* IfcClassificationItem_type = 0;
entity* IfcClassificationItemRelationship_type = 0;
entity* IfcClassificationNotation_type = 0;
entity* IfcClassificationNotationFacet_type = 0;
entity* IfcClassificationReference_type = 0;
entity* IfcClosedShell_type = 0;
entity* IfcCoilType_type = 0;
entity* IfcColourRgb_type = 0;
entity* IfcColourSpecification_type = 0;
entity* IfcColumn_type = 0;
entity* IfcColumnType_type = 0;
entity* IfcComplexProperty_type = 0;
entity* IfcCompositeCurve_type = 0;
entity* IfcCompositeCurveSegment_type = 0;
entity* IfcCompositeProfileDef_type = 0;
entity* IfcCompressorType_type = 0;
entity* IfcCondenserType_type = 0;
entity* IfcCondition_type = 0;
entity* IfcConditionCriterion_type = 0;
entity* IfcConic_type = 0;
entity* IfcConnectedFaceSet_type = 0;
entity* IfcConnectionCurveGeometry_type = 0;
entity* IfcConnectionGeometry_type = 0;
entity* IfcConnectionPointEccentricity_type = 0;
entity* IfcConnectionPointGeometry_type = 0;
entity* IfcConnectionPortGeometry_type = 0;
entity* IfcConnectionSurfaceGeometry_type = 0;
entity* IfcConstraint_type = 0;
entity* IfcConstraintAggregationRelationship_type = 0;
entity* IfcConstraintClassificationRelationship_type = 0;
entity* IfcConstraintRelationship_type = 0;
entity* IfcConstructionEquipmentResource_type = 0;
entity* IfcConstructionMaterialResource_type = 0;
entity* IfcConstructionProductResource_type = 0;
entity* IfcConstructionResource_type = 0;
entity* IfcContextDependentUnit_type = 0;
entity* IfcControl_type = 0;
entity* IfcControllerType_type = 0;
entity* IfcConversionBasedUnit_type = 0;
entity* IfcCooledBeamType_type = 0;
entity* IfcCoolingTowerType_type = 0;
entity* IfcCoordinatedUniversalTimeOffset_type = 0;
entity* IfcCostItem_type = 0;
entity* IfcCostSchedule_type = 0;
entity* IfcCostValue_type = 0;
entity* IfcCovering_type = 0;
entity* IfcCoveringType_type = 0;
entity* IfcCraneRailAShapeProfileDef_type = 0;
entity* IfcCraneRailFShapeProfileDef_type = 0;
entity* IfcCrewResource_type = 0;
entity* IfcCsgPrimitive3D_type = 0;
entity* IfcCsgSolid_type = 0;
entity* IfcCurrencyRelationship_type = 0;
entity* IfcCurtainWall_type = 0;
entity* IfcCurtainWallType_type = 0;
entity* IfcCurve_type = 0;
entity* IfcCurveBoundedPlane_type = 0;
entity* IfcCurveStyle_type = 0;
entity* IfcCurveStyleFont_type = 0;
entity* IfcCurveStyleFontAndScaling_type = 0;
entity* IfcCurveStyleFontPattern_type = 0;
entity* IfcDamperType_type = 0;
entity* IfcDateAndTime_type = 0;
entity* IfcDefinedSymbol_type = 0;
entity* IfcDerivedProfileDef_type = 0;
entity* IfcDerivedUnit_type = 0;
entity* IfcDerivedUnitElement_type = 0;
entity* IfcDiameterDimension_type = 0;
entity* IfcDimensionCalloutRelationship_type = 0;
entity* IfcDimensionCurve_type = 0;
entity* IfcDimensionCurveDirectedCallout_type = 0;
entity* IfcDimensionCurveTerminator_type = 0;
entity* IfcDimensionPair_type = 0;
entity* IfcDimensionalExponents_type = 0;
entity* IfcDirection_type = 0;
entity* IfcDiscreteAccessory_type = 0;
entity* IfcDiscreteAccessoryType_type = 0;
entity* IfcDistributionChamberElement_type = 0;
entity* IfcDistributionChamberElementType_type = 0;
entity* IfcDistributionControlElement_type = 0;
entity* IfcDistributionControlElementType_type = 0;
entity* IfcDistributionElement_type = 0;
entity* IfcDistributionElementType_type = 0;
entity* IfcDistributionFlowElement_type = 0;
entity* IfcDistributionFlowElementType_type = 0;
entity* IfcDistributionPort_type = 0;
entity* IfcDocumentElectronicFormat_type = 0;
entity* IfcDocumentInformation_type = 0;
entity* IfcDocumentInformationRelationship_type = 0;
entity* IfcDocumentReference_type = 0;
entity* IfcDoor_type = 0;
entity* IfcDoorLiningProperties_type = 0;
entity* IfcDoorPanelProperties_type = 0;
entity* IfcDoorStyle_type = 0;
entity* IfcDraughtingCallout_type = 0;
entity* IfcDraughtingCalloutRelationship_type = 0;
entity* IfcDraughtingPreDefinedColour_type = 0;
entity* IfcDraughtingPreDefinedCurveFont_type = 0;
entity* IfcDraughtingPreDefinedTextFont_type = 0;
entity* IfcDuctFittingType_type = 0;
entity* IfcDuctSegmentType_type = 0;
entity* IfcDuctSilencerType_type = 0;
entity* IfcEdge_type = 0;
entity* IfcEdgeCurve_type = 0;
entity* IfcEdgeFeature_type = 0;
entity* IfcEdgeLoop_type = 0;
entity* IfcElectricApplianceType_type = 0;
entity* IfcElectricDistributionPoint_type = 0;
entity* IfcElectricFlowStorageDeviceType_type = 0;
entity* IfcElectricGeneratorType_type = 0;
entity* IfcElectricHeaterType_type = 0;
entity* IfcElectricMotorType_type = 0;
entity* IfcElectricTimeControlType_type = 0;
entity* IfcElectricalBaseProperties_type = 0;
entity* IfcElectricalCircuit_type = 0;
entity* IfcElectricalElement_type = 0;
entity* IfcElement_type = 0;
entity* IfcElementAssembly_type = 0;
entity* IfcElementComponent_type = 0;
entity* IfcElementComponentType_type = 0;
entity* IfcElementQuantity_type = 0;
entity* IfcElementType_type = 0;
entity* IfcElementarySurface_type = 0;
entity* IfcEllipse_type = 0;
entity* IfcEllipseProfileDef_type = 0;
entity* IfcEnergyConversionDevice_type = 0;
entity* IfcEnergyConversionDeviceType_type = 0;
entity* IfcEnergyProperties_type = 0;
entity* IfcEnvironmentalImpactValue_type = 0;
entity* IfcEquipmentElement_type = 0;
entity* IfcEquipmentStandard_type = 0;
entity* IfcEvaporativeCoolerType_type = 0;
entity* IfcEvaporatorType_type = 0;
entity* IfcExtendedMaterialProperties_type = 0;
entity* IfcExternalReference_type = 0;
entity* IfcExternallyDefinedHatchStyle_type = 0;
entity* IfcExternallyDefinedSurfaceStyle_type = 0;
entity* IfcExternallyDefinedSymbol_type = 0;
entity* IfcExternallyDefinedTextFont_type = 0;
entity* IfcExtrudedAreaSolid_type = 0;
entity* IfcFace_type = 0;
entity* IfcFaceBasedSurfaceModel_type = 0;
entity* IfcFaceBound_type = 0;
entity* IfcFaceOuterBound_type = 0;
entity* IfcFaceSurface_type = 0;
entity* IfcFacetedBrep_type = 0;
entity* IfcFacetedBrepWithVoids_type = 0;
entity* IfcFailureConnectionCondition_type = 0;
entity* IfcFanType_type = 0;
entity* IfcFastener_type = 0;
entity* IfcFastenerType_type = 0;
entity* IfcFeatureElement_type = 0;
entity* IfcFeatureElementAddition_type = 0;
entity* IfcFeatureElementSubtraction_type = 0;
entity* IfcFillAreaStyle_type = 0;
entity* IfcFillAreaStyleHatching_type = 0;
entity* IfcFillAreaStyleTileSymbolWithStyle_type = 0;
entity* IfcFillAreaStyleTiles_type = 0;
entity* IfcFilterType_type = 0;
entity* IfcFireSuppressionTerminalType_type = 0;
entity* IfcFlowController_type = 0;
entity* IfcFlowControllerType_type = 0;
entity* IfcFlowFitting_type = 0;
entity* IfcFlowFittingType_type = 0;
entity* IfcFlowInstrumentType_type = 0;
entity* IfcFlowMeterType_type = 0;
entity* IfcFlowMovingDevice_type = 0;
entity* IfcFlowMovingDeviceType_type = 0;
entity* IfcFlowSegment_type = 0;
entity* IfcFlowSegmentType_type = 0;
entity* IfcFlowStorageDevice_type = 0;
entity* IfcFlowStorageDeviceType_type = 0;
entity* IfcFlowTerminal_type = 0;
entity* IfcFlowTerminalType_type = 0;
entity* IfcFlowTreatmentDevice_type = 0;
entity* IfcFlowTreatmentDeviceType_type = 0;
entity* IfcFluidFlowProperties_type = 0;
entity* IfcFooting_type = 0;
entity* IfcFuelProperties_type = 0;
entity* IfcFurnishingElement_type = 0;
entity* IfcFurnishingElementType_type = 0;
entity* IfcFurnitureStandard_type = 0;
entity* IfcFurnitureType_type = 0;
entity* IfcGasTerminalType_type = 0;
entity* IfcGeneralMaterialProperties_type = 0;
entity* IfcGeneralProfileProperties_type = 0;
entity* IfcGeometricCurveSet_type = 0;
entity* IfcGeometricRepresentationContext_type = 0;
entity* IfcGeometricRepresentationItem_type = 0;
entity* IfcGeometricRepresentationSubContext_type = 0;
entity* IfcGeometricSet_type = 0;
entity* IfcGrid_type = 0;
entity* IfcGridAxis_type = 0;
entity* IfcGridPlacement_type = 0;
entity* IfcGroup_type = 0;
entity* IfcHalfSpaceSolid_type = 0;
entity* IfcHeatExchangerType_type = 0;
entity* IfcHumidifierType_type = 0;
entity* IfcHygroscopicMaterialProperties_type = 0;
entity* IfcIShapeProfileDef_type = 0;
entity* IfcImageTexture_type = 0;
entity* IfcInventory_type = 0;
entity* IfcIrregularTimeSeries_type = 0;
entity* IfcIrregularTimeSeriesValue_type = 0;
entity* IfcJunctionBoxType_type = 0;
entity* IfcLShapeProfileDef_type = 0;
entity* IfcLaborResource_type = 0;
entity* IfcLampType_type = 0;
entity* IfcLibraryInformation_type = 0;
entity* IfcLibraryReference_type = 0;
entity* IfcLightDistributionData_type = 0;
entity* IfcLightFixtureType_type = 0;
entity* IfcLightIntensityDistribution_type = 0;
entity* IfcLightSource_type = 0;
entity* IfcLightSourceAmbient_type = 0;
entity* IfcLightSourceDirectional_type = 0;
entity* IfcLightSourceGoniometric_type = 0;
entity* IfcLightSourcePositional_type = 0;
entity* IfcLightSourceSpot_type = 0;
entity* IfcLine_type = 0;
entity* IfcLinearDimension_type = 0;
entity* IfcLocalPlacement_type = 0;
entity* IfcLocalTime_type = 0;
entity* IfcLoop_type = 0;
entity* IfcManifoldSolidBrep_type = 0;
entity* IfcMappedItem_type = 0;
entity* IfcMaterial_type = 0;
entity* IfcMaterialClassificationRelationship_type = 0;
entity* IfcMaterialDefinitionRepresentation_type = 0;
entity* IfcMaterialLayer_type = 0;
entity* IfcMaterialLayerSet_type = 0;
entity* IfcMaterialLayerSetUsage_type = 0;
entity* IfcMaterialList_type = 0;
entity* IfcMaterialProperties_type = 0;
entity* IfcMeasureWithUnit_type = 0;
entity* IfcMechanicalConcreteMaterialProperties_type = 0;
entity* IfcMechanicalFastener_type = 0;
entity* IfcMechanicalFastenerType_type = 0;
entity* IfcMechanicalMaterialProperties_type = 0;
entity* IfcMechanicalSteelMaterialProperties_type = 0;
entity* IfcMember_type = 0;
entity* IfcMemberType_type = 0;
entity* IfcMetric_type = 0;
entity* IfcMonetaryUnit_type = 0;
entity* IfcMotorConnectionType_type = 0;
entity* IfcMove_type = 0;
entity* IfcNamedUnit_type = 0;
entity* IfcObject_type = 0;
entity* IfcObjectDefinition_type = 0;
entity* IfcObjectPlacement_type = 0;
entity* IfcObjective_type = 0;
entity* IfcOccupant_type = 0;
entity* IfcOffsetCurve2D_type = 0;
entity* IfcOffsetCurve3D_type = 0;
entity* IfcOneDirectionRepeatFactor_type = 0;
entity* IfcOpenShell_type = 0;
entity* IfcOpeningElement_type = 0;
entity* IfcOpticalMaterialProperties_type = 0;
entity* IfcOrderAction_type = 0;
entity* IfcOrganization_type = 0;
entity* IfcOrganizationRelationship_type = 0;
entity* IfcOrientedEdge_type = 0;
entity* IfcOutletType_type = 0;
entity* IfcOwnerHistory_type = 0;
entity* IfcParameterizedProfileDef_type = 0;
entity* IfcPath_type = 0;
entity* IfcPerformanceHistory_type = 0;
entity* IfcPermeableCoveringProperties_type = 0;
entity* IfcPermit_type = 0;
entity* IfcPerson_type = 0;
entity* IfcPersonAndOrganization_type = 0;
entity* IfcPhysicalComplexQuantity_type = 0;
entity* IfcPhysicalQuantity_type = 0;
entity* IfcPhysicalSimpleQuantity_type = 0;
entity* IfcPile_type = 0;
entity* IfcPipeFittingType_type = 0;
entity* IfcPipeSegmentType_type = 0;
entity* IfcPixelTexture_type = 0;
entity* IfcPlacement_type = 0;
entity* IfcPlanarBox_type = 0;
entity* IfcPlanarExtent_type = 0;
entity* IfcPlane_type = 0;
entity* IfcPlate_type = 0;
entity* IfcPlateType_type = 0;
entity* IfcPoint_type = 0;
entity* IfcPointOnCurve_type = 0;
entity* IfcPointOnSurface_type = 0;
entity* IfcPolyLoop_type = 0;
entity* IfcPolygonalBoundedHalfSpace_type = 0;
entity* IfcPolyline_type = 0;
entity* IfcPort_type = 0;
entity* IfcPostalAddress_type = 0;
entity* IfcPreDefinedColour_type = 0;
entity* IfcPreDefinedCurveFont_type = 0;
entity* IfcPreDefinedDimensionSymbol_type = 0;
entity* IfcPreDefinedItem_type = 0;
entity* IfcPreDefinedPointMarkerSymbol_type = 0;
entity* IfcPreDefinedSymbol_type = 0;
entity* IfcPreDefinedTerminatorSymbol_type = 0;
entity* IfcPreDefinedTextFont_type = 0;
entity* IfcPresentationLayerAssignment_type = 0;
entity* IfcPresentationLayerWithStyle_type = 0;
entity* IfcPresentationStyle_type = 0;
entity* IfcPresentationStyleAssignment_type = 0;
entity* IfcProcedure_type = 0;
entity* IfcProcess_type = 0;
entity* IfcProduct_type = 0;
entity* IfcProductDefinitionShape_type = 0;
entity* IfcProductRepresentation_type = 0;
entity* IfcProductsOfCombustionProperties_type = 0;
entity* IfcProfileDef_type = 0;
entity* IfcProfileProperties_type = 0;
entity* IfcProject_type = 0;
entity* IfcProjectOrder_type = 0;
entity* IfcProjectOrderRecord_type = 0;
entity* IfcProjectionCurve_type = 0;
entity* IfcProjectionElement_type = 0;
entity* IfcProperty_type = 0;
entity* IfcPropertyBoundedValue_type = 0;
entity* IfcPropertyConstraintRelationship_type = 0;
entity* IfcPropertyDefinition_type = 0;
entity* IfcPropertyDependencyRelationship_type = 0;
entity* IfcPropertyEnumeratedValue_type = 0;
entity* IfcPropertyEnumeration_type = 0;
entity* IfcPropertyListValue_type = 0;
entity* IfcPropertyReferenceValue_type = 0;
entity* IfcPropertySet_type = 0;
entity* IfcPropertySetDefinition_type = 0;
entity* IfcPropertySingleValue_type = 0;
entity* IfcPropertyTableValue_type = 0;
entity* IfcProtectiveDeviceType_type = 0;
entity* IfcProxy_type = 0;
entity* IfcPumpType_type = 0;
entity* IfcQuantityArea_type = 0;
entity* IfcQuantityCount_type = 0;
entity* IfcQuantityLength_type = 0;
entity* IfcQuantityTime_type = 0;
entity* IfcQuantityVolume_type = 0;
entity* IfcQuantityWeight_type = 0;
entity* IfcRadiusDimension_type = 0;
entity* IfcRailing_type = 0;
entity* IfcRailingType_type = 0;
entity* IfcRamp_type = 0;
entity* IfcRampFlight_type = 0;
entity* IfcRampFlightType_type = 0;
entity* IfcRationalBezierCurve_type = 0;
entity* IfcRectangleHollowProfileDef_type = 0;
entity* IfcRectangleProfileDef_type = 0;
entity* IfcRectangularPyramid_type = 0;
entity* IfcRectangularTrimmedSurface_type = 0;
entity* IfcReferencesValueDocument_type = 0;
entity* IfcRegularTimeSeries_type = 0;
entity* IfcReinforcementBarProperties_type = 0;
entity* IfcReinforcementDefinitionProperties_type = 0;
entity* IfcReinforcingBar_type = 0;
entity* IfcReinforcingElement_type = 0;
entity* IfcReinforcingMesh_type = 0;
entity* IfcRelAggregates_type = 0;
entity* IfcRelAssigns_type = 0;
entity* IfcRelAssignsTasks_type = 0;
entity* IfcRelAssignsToActor_type = 0;
entity* IfcRelAssignsToControl_type = 0;
entity* IfcRelAssignsToGroup_type = 0;
entity* IfcRelAssignsToProcess_type = 0;
entity* IfcRelAssignsToProduct_type = 0;
entity* IfcRelAssignsToProjectOrder_type = 0;
entity* IfcRelAssignsToResource_type = 0;
entity* IfcRelAssociates_type = 0;
entity* IfcRelAssociatesAppliedValue_type = 0;
entity* IfcRelAssociatesApproval_type = 0;
entity* IfcRelAssociatesClassification_type = 0;
entity* IfcRelAssociatesConstraint_type = 0;
entity* IfcRelAssociatesDocument_type = 0;
entity* IfcRelAssociatesLibrary_type = 0;
entity* IfcRelAssociatesMaterial_type = 0;
entity* IfcRelAssociatesProfileProperties_type = 0;
entity* IfcRelConnects_type = 0;
entity* IfcRelConnectsElements_type = 0;
entity* IfcRelConnectsPathElements_type = 0;
entity* IfcRelConnectsPortToElement_type = 0;
entity* IfcRelConnectsPorts_type = 0;
entity* IfcRelConnectsStructuralActivity_type = 0;
entity* IfcRelConnectsStructuralElement_type = 0;
entity* IfcRelConnectsStructuralMember_type = 0;
entity* IfcRelConnectsWithEccentricity_type = 0;
entity* IfcRelConnectsWithRealizingElements_type = 0;
entity* IfcRelContainedInSpatialStructure_type = 0;
entity* IfcRelCoversBldgElements_type = 0;
entity* IfcRelCoversSpaces_type = 0;
entity* IfcRelDecomposes_type = 0;
entity* IfcRelDefines_type = 0;
entity* IfcRelDefinesByProperties_type = 0;
entity* IfcRelDefinesByType_type = 0;
entity* IfcRelFillsElement_type = 0;
entity* IfcRelFlowControlElements_type = 0;
entity* IfcRelInteractionRequirements_type = 0;
entity* IfcRelNests_type = 0;
entity* IfcRelOccupiesSpaces_type = 0;
entity* IfcRelOverridesProperties_type = 0;
entity* IfcRelProjectsElement_type = 0;
entity* IfcRelReferencedInSpatialStructure_type = 0;
entity* IfcRelSchedulesCostItems_type = 0;
entity* IfcRelSequence_type = 0;
entity* IfcRelServicesBuildings_type = 0;
entity* IfcRelSpaceBoundary_type = 0;
entity* IfcRelVoidsElement_type = 0;
entity* IfcRelationship_type = 0;
entity* IfcRelaxation_type = 0;
entity* IfcRepresentation_type = 0;
entity* IfcRepresentationContext_type = 0;
entity* IfcRepresentationItem_type = 0;
entity* IfcRepresentationMap_type = 0;
entity* IfcResource_type = 0;
entity* IfcRevolvedAreaSolid_type = 0;
entity* IfcRibPlateProfileProperties_type = 0;
entity* IfcRightCircularCone_type = 0;
entity* IfcRightCircularCylinder_type = 0;
entity* IfcRoof_type = 0;
entity* IfcRoot_type = 0;
entity* IfcRoundedEdgeFeature_type = 0;
entity* IfcRoundedRectangleProfileDef_type = 0;
entity* IfcSIUnit_type = 0;
entity* IfcSanitaryTerminalType_type = 0;
entity* IfcScheduleTimeControl_type = 0;
entity* IfcSectionProperties_type = 0;
entity* IfcSectionReinforcementProperties_type = 0;
entity* IfcSectionedSpine_type = 0;
entity* IfcSensorType_type = 0;
entity* IfcServiceLife_type = 0;
entity* IfcServiceLifeFactor_type = 0;
entity* IfcShapeAspect_type = 0;
entity* IfcShapeModel_type = 0;
entity* IfcShapeRepresentation_type = 0;
entity* IfcShellBasedSurfaceModel_type = 0;
entity* IfcSimpleProperty_type = 0;
entity* IfcSite_type = 0;
entity* IfcSlab_type = 0;
entity* IfcSlabType_type = 0;
entity* IfcSlippageConnectionCondition_type = 0;
entity* IfcSolidModel_type = 0;
entity* IfcSoundProperties_type = 0;
entity* IfcSoundValue_type = 0;
entity* IfcSpace_type = 0;
entity* IfcSpaceHeaterType_type = 0;
entity* IfcSpaceProgram_type = 0;
entity* IfcSpaceThermalLoadProperties_type = 0;
entity* IfcSpaceType_type = 0;
entity* IfcSpatialStructureElement_type = 0;
entity* IfcSpatialStructureElementType_type = 0;
entity* IfcSphere_type = 0;
entity* IfcStackTerminalType_type = 0;
entity* IfcStair_type = 0;
entity* IfcStairFlight_type = 0;
entity* IfcStairFlightType_type = 0;
entity* IfcStructuralAction_type = 0;
entity* IfcStructuralActivity_type = 0;
entity* IfcStructuralAnalysisModel_type = 0;
entity* IfcStructuralConnection_type = 0;
entity* IfcStructuralConnectionCondition_type = 0;
entity* IfcStructuralCurveConnection_type = 0;
entity* IfcStructuralCurveMember_type = 0;
entity* IfcStructuralCurveMemberVarying_type = 0;
entity* IfcStructuralItem_type = 0;
entity* IfcStructuralLinearAction_type = 0;
entity* IfcStructuralLinearActionVarying_type = 0;
entity* IfcStructuralLoad_type = 0;
entity* IfcStructuralLoadGroup_type = 0;
entity* IfcStructuralLoadLinearForce_type = 0;
entity* IfcStructuralLoadPlanarForce_type = 0;
entity* IfcStructuralLoadSingleDisplacement_type = 0;
entity* IfcStructuralLoadSingleDisplacementDistortion_type = 0;
entity* IfcStructuralLoadSingleForce_type = 0;
entity* IfcStructuralLoadSingleForceWarping_type = 0;
entity* IfcStructuralLoadStatic_type = 0;
entity* IfcStructuralLoadTemperature_type = 0;
entity* IfcStructuralMember_type = 0;
entity* IfcStructuralPlanarAction_type = 0;
entity* IfcStructuralPlanarActionVarying_type = 0;
entity* IfcStructuralPointAction_type = 0;
entity* IfcStructuralPointConnection_type = 0;
entity* IfcStructuralPointReaction_type = 0;
entity* IfcStructuralProfileProperties_type = 0;
entity* IfcStructuralReaction_type = 0;
entity* IfcStructuralResultGroup_type = 0;
entity* IfcStructuralSteelProfileProperties_type = 0;
entity* IfcStructuralSurfaceConnection_type = 0;
entity* IfcStructuralSurfaceMember_type = 0;
entity* IfcStructuralSurfaceMemberVarying_type = 0;
entity* IfcStructuredDimensionCallout_type = 0;
entity* IfcStyleModel_type = 0;
entity* IfcStyledItem_type = 0;
entity* IfcStyledRepresentation_type = 0;
entity* IfcSubContractResource_type = 0;
entity* IfcSubedge_type = 0;
entity* IfcSurface_type = 0;
entity* IfcSurfaceCurveSweptAreaSolid_type = 0;
entity* IfcSurfaceOfLinearExtrusion_type = 0;
entity* IfcSurfaceOfRevolution_type = 0;
entity* IfcSurfaceStyle_type = 0;
entity* IfcSurfaceStyleLighting_type = 0;
entity* IfcSurfaceStyleRefraction_type = 0;
entity* IfcSurfaceStyleRendering_type = 0;
entity* IfcSurfaceStyleShading_type = 0;
entity* IfcSurfaceStyleWithTextures_type = 0;
entity* IfcSurfaceTexture_type = 0;
entity* IfcSweptAreaSolid_type = 0;
entity* IfcSweptDiskSolid_type = 0;
entity* IfcSweptSurface_type = 0;
entity* IfcSwitchingDeviceType_type = 0;
entity* IfcSymbolStyle_type = 0;
entity* IfcSystem_type = 0;
entity* IfcSystemFurnitureElementType_type = 0;
entity* IfcTShapeProfileDef_type = 0;
entity* IfcTable_type = 0;
entity* IfcTableRow_type = 0;
entity* IfcTankType_type = 0;
entity* IfcTask_type = 0;
entity* IfcTelecomAddress_type = 0;
entity* IfcTendon_type = 0;
entity* IfcTendonAnchor_type = 0;
entity* IfcTerminatorSymbol_type = 0;
entity* IfcTextLiteral_type = 0;
entity* IfcTextLiteralWithExtent_type = 0;
entity* IfcTextStyle_type = 0;
entity* IfcTextStyleFontModel_type = 0;
entity* IfcTextStyleForDefinedFont_type = 0;
entity* IfcTextStyleTextModel_type = 0;
entity* IfcTextStyleWithBoxCharacteristics_type = 0;
entity* IfcTextureCoordinate_type = 0;
entity* IfcTextureCoordinateGenerator_type = 0;
entity* IfcTextureMap_type = 0;
entity* IfcTextureVertex_type = 0;
entity* IfcThermalMaterialProperties_type = 0;
entity* IfcTimeSeries_type = 0;
entity* IfcTimeSeriesReferenceRelationship_type = 0;
entity* IfcTimeSeriesSchedule_type = 0;
entity* IfcTimeSeriesValue_type = 0;
entity* IfcTopologicalRepresentationItem_type = 0;
entity* IfcTopologyRepresentation_type = 0;
entity* IfcTransformerType_type = 0;
entity* IfcTransportElement_type = 0;
entity* IfcTransportElementType_type = 0;
entity* IfcTrapeziumProfileDef_type = 0;
entity* IfcTrimmedCurve_type = 0;
entity* IfcTubeBundleType_type = 0;
entity* IfcTwoDirectionRepeatFactor_type = 0;
entity* IfcTypeObject_type = 0;
entity* IfcTypeProduct_type = 0;
entity* IfcUShapeProfileDef_type = 0;
entity* IfcUnitAssignment_type = 0;
entity* IfcUnitaryEquipmentType_type = 0;
entity* IfcValveType_type = 0;
entity* IfcVector_type = 0;
entity* IfcVertex_type = 0;
entity* IfcVertexBasedTextureMap_type = 0;
entity* IfcVertexLoop_type = 0;
entity* IfcVertexPoint_type = 0;
entity* IfcVibrationIsolatorType_type = 0;
entity* IfcVirtualElement_type = 0;
entity* IfcVirtualGridIntersection_type = 0;
entity* IfcWall_type = 0;
entity* IfcWallStandardCase_type = 0;
entity* IfcWallType_type = 0;
entity* IfcWasteTerminalType_type = 0;
entity* IfcWaterProperties_type = 0;
entity* IfcWindow_type = 0;
entity* IfcWindowLiningProperties_type = 0;
entity* IfcWindowPanelProperties_type = 0;
entity* IfcWindowStyle_type = 0;
entity* IfcWorkControl_type = 0;
entity* IfcWorkPlan_type = 0;
entity* IfcWorkSchedule_type = 0;
entity* IfcZShapeProfileDef_type = 0;
entity* IfcZone_type = 0;
type_declaration* IfcAbsorbedDoseMeasure_type = 0;
type_declaration* IfcAccelerationMeasure_type = 0;
type_declaration* IfcAmountOfSubstanceMeasure_type = 0;
type_declaration* IfcAngularVelocityMeasure_type = 0;
type_declaration* IfcAreaMeasure_type = 0;
type_declaration* IfcBoolean_type = 0;
type_declaration* IfcBoxAlignment_type = 0;
type_declaration* IfcComplexNumber_type = 0;
type_declaration* IfcCompoundPlaneAngleMeasure_type = 0;
type_declaration* IfcContextDependentMeasure_type = 0;
type_declaration* IfcCountMeasure_type = 0;
type_declaration* IfcCurvatureMeasure_type = 0;
type_declaration* IfcDayInMonthNumber_type = 0;
type_declaration* IfcDaylightSavingHour_type = 0;
type_declaration* IfcDescriptiveMeasure_type = 0;
type_declaration* IfcDimensionCount_type = 0;
type_declaration* IfcDoseEquivalentMeasure_type = 0;
type_declaration* IfcDynamicViscosityMeasure_type = 0;
type_declaration* IfcElectricCapacitanceMeasure_type = 0;
type_declaration* IfcElectricChargeMeasure_type = 0;
type_declaration* IfcElectricConductanceMeasure_type = 0;
type_declaration* IfcElectricCurrentMeasure_type = 0;
type_declaration* IfcElectricResistanceMeasure_type = 0;
type_declaration* IfcElectricVoltageMeasure_type = 0;
type_declaration* IfcEnergyMeasure_type = 0;
type_declaration* IfcFontStyle_type = 0;
type_declaration* IfcFontVariant_type = 0;
type_declaration* IfcFontWeight_type = 0;
type_declaration* IfcForceMeasure_type = 0;
type_declaration* IfcFrequencyMeasure_type = 0;
type_declaration* IfcGloballyUniqueId_type = 0;
type_declaration* IfcHeatFluxDensityMeasure_type = 0;
type_declaration* IfcHeatingValueMeasure_type = 0;
type_declaration* IfcHourInDay_type = 0;
type_declaration* IfcIdentifier_type = 0;
type_declaration* IfcIlluminanceMeasure_type = 0;
type_declaration* IfcInductanceMeasure_type = 0;
type_declaration* IfcInteger_type = 0;
type_declaration* IfcIntegerCountRateMeasure_type = 0;
type_declaration* IfcIonConcentrationMeasure_type = 0;
type_declaration* IfcIsothermalMoistureCapacityMeasure_type = 0;
type_declaration* IfcKinematicViscosityMeasure_type = 0;
type_declaration* IfcLabel_type = 0;
type_declaration* IfcLengthMeasure_type = 0;
type_declaration* IfcLinearForceMeasure_type = 0;
type_declaration* IfcLinearMomentMeasure_type = 0;
type_declaration* IfcLinearStiffnessMeasure_type = 0;
type_declaration* IfcLinearVelocityMeasure_type = 0;
type_declaration* IfcLogical_type = 0;
type_declaration* IfcLuminousFluxMeasure_type = 0;
type_declaration* IfcLuminousIntensityDistributionMeasure_type = 0;
type_declaration* IfcLuminousIntensityMeasure_type = 0;
type_declaration* IfcMagneticFluxDensityMeasure_type = 0;
type_declaration* IfcMagneticFluxMeasure_type = 0;
type_declaration* IfcMassDensityMeasure_type = 0;
type_declaration* IfcMassFlowRateMeasure_type = 0;
type_declaration* IfcMassMeasure_type = 0;
type_declaration* IfcMassPerLengthMeasure_type = 0;
type_declaration* IfcMinuteInHour_type = 0;
type_declaration* IfcModulusOfElasticityMeasure_type = 0;
type_declaration* IfcModulusOfLinearSubgradeReactionMeasure_type = 0;
type_declaration* IfcModulusOfRotationalSubgradeReactionMeasure_type = 0;
type_declaration* IfcModulusOfSubgradeReactionMeasure_type = 0;
type_declaration* IfcMoistureDiffusivityMeasure_type = 0;
type_declaration* IfcMolecularWeightMeasure_type = 0;
type_declaration* IfcMomentOfInertiaMeasure_type = 0;
type_declaration* IfcMonetaryMeasure_type = 0;
type_declaration* IfcMonthInYearNumber_type = 0;
type_declaration* IfcNormalisedRatioMeasure_type = 0;
type_declaration* IfcNumericMeasure_type = 0;
type_declaration* IfcPHMeasure_type = 0;
type_declaration* IfcParameterValue_type = 0;
type_declaration* IfcPlanarForceMeasure_type = 0;
type_declaration* IfcPlaneAngleMeasure_type = 0;
type_declaration* IfcPositiveLengthMeasure_type = 0;
type_declaration* IfcPositivePlaneAngleMeasure_type = 0;
type_declaration* IfcPositiveRatioMeasure_type = 0;
type_declaration* IfcPowerMeasure_type = 0;
type_declaration* IfcPresentableText_type = 0;
type_declaration* IfcPressureMeasure_type = 0;
type_declaration* IfcRadioActivityMeasure_type = 0;
type_declaration* IfcRatioMeasure_type = 0;
type_declaration* IfcReal_type = 0;
type_declaration* IfcRotationalFrequencyMeasure_type = 0;
type_declaration* IfcRotationalMassMeasure_type = 0;
type_declaration* IfcRotationalStiffnessMeasure_type = 0;
type_declaration* IfcSecondInMinute_type = 0;
type_declaration* IfcSectionModulusMeasure_type = 0;
type_declaration* IfcSectionalAreaIntegralMeasure_type = 0;
type_declaration* IfcShearModulusMeasure_type = 0;
type_declaration* IfcSolidAngleMeasure_type = 0;
type_declaration* IfcSoundPowerMeasure_type = 0;
type_declaration* IfcSoundPressureMeasure_type = 0;
type_declaration* IfcSpecificHeatCapacityMeasure_type = 0;
type_declaration* IfcSpecularExponent_type = 0;
type_declaration* IfcSpecularRoughness_type = 0;
type_declaration* IfcTemperatureGradientMeasure_type = 0;
type_declaration* IfcText_type = 0;
type_declaration* IfcTextAlignment_type = 0;
type_declaration* IfcTextDecoration_type = 0;
type_declaration* IfcTextFontName_type = 0;
type_declaration* IfcTextTransformation_type = 0;
type_declaration* IfcThermalAdmittanceMeasure_type = 0;
type_declaration* IfcThermalConductivityMeasure_type = 0;
type_declaration* IfcThermalExpansionCoefficientMeasure_type = 0;
type_declaration* IfcThermalResistanceMeasure_type = 0;
type_declaration* IfcThermalTransmittanceMeasure_type = 0;
type_declaration* IfcThermodynamicTemperatureMeasure_type = 0;
type_declaration* IfcTimeMeasure_type = 0;
type_declaration* IfcTimeStamp_type = 0;
type_declaration* IfcTorqueMeasure_type = 0;
type_declaration* IfcVaporPermeabilityMeasure_type = 0;
type_declaration* IfcVolumeMeasure_type = 0;
type_declaration* IfcVolumetricFlowRateMeasure_type = 0;
type_declaration* IfcWarpingConstantMeasure_type = 0;
type_declaration* IfcWarpingMomentMeasure_type = 0;
type_declaration* IfcYearNumber_type = 0;
select_type* IfcActorSelect_type = 0;
select_type* IfcAppliedValueSelect_type = 0;
select_type* IfcAxis2Placement_type = 0;
select_type* IfcBooleanOperand_type = 0;
select_type* IfcCharacterStyleSelect_type = 0;
select_type* IfcClassificationNotationSelect_type = 0;
select_type* IfcColour_type = 0;
select_type* IfcColourOrFactor_type = 0;
select_type* IfcConditionCriterionSelect_type = 0;
select_type* IfcCsgSelect_type = 0;
select_type* IfcCurveFontOrScaledCurveFontSelect_type = 0;
select_type* IfcCurveOrEdgeCurve_type = 0;
select_type* IfcCurveStyleFontSelect_type = 0;
select_type* IfcDateTimeSelect_type = 0;
select_type* IfcDefinedSymbolSelect_type = 0;
select_type* IfcDerivedMeasureValue_type = 0;
select_type* IfcDocumentSelect_type = 0;
select_type* IfcDraughtingCalloutElement_type = 0;
select_type* IfcFillAreaStyleTileShapeSelect_type = 0;
select_type* IfcFillStyleSelect_type = 0;
select_type* IfcGeometricSetSelect_type = 0;
select_type* IfcHatchLineDistanceSelect_type = 0;
select_type* IfcLayeredItem_type = 0;
select_type* IfcLibrarySelect_type = 0;
select_type* IfcLightDistributionDataSourceSelect_type = 0;
select_type* IfcMaterialSelect_type = 0;
select_type* IfcMeasureValue_type = 0;
select_type* IfcMetricValueSelect_type = 0;
select_type* IfcObjectReferenceSelect_type = 0;
select_type* IfcOrientationSelect_type = 0;
select_type* IfcPointOrVertexPoint_type = 0;
select_type* IfcPresentationStyleSelect_type = 0;
select_type* IfcShell_type = 0;
select_type* IfcSimpleValue_type = 0;
select_type* IfcSizeSelect_type = 0;
select_type* IfcSpecularHighlightSelect_type = 0;
select_type* IfcStructuralActivityAssignmentSelect_type = 0;
select_type* IfcSurfaceOrFaceSurface_type = 0;
select_type* IfcSurfaceStyleElementSelect_type = 0;
select_type* IfcSymbolStyleSelect_type = 0;
select_type* IfcTextFontSelect_type = 0;
select_type* IfcTextStyleSelect_type = 0;
select_type* IfcTrimmingSelect_type = 0;
select_type* IfcUnit_type = 0;
select_type* IfcValue_type = 0;
select_type* IfcVectorOrDirection_type = 0;
enumeration_type* IfcActionSourceTypeEnum_type = 0;
enumeration_type* IfcActionTypeEnum_type = 0;
enumeration_type* IfcActuatorTypeEnum_type = 0;
enumeration_type* IfcAddressTypeEnum_type = 0;
enumeration_type* IfcAheadOrBehind_type = 0;
enumeration_type* IfcAirTerminalBoxTypeEnum_type = 0;
enumeration_type* IfcAirTerminalTypeEnum_type = 0;
enumeration_type* IfcAirToAirHeatRecoveryTypeEnum_type = 0;
enumeration_type* IfcAlarmTypeEnum_type = 0;
enumeration_type* IfcAnalysisModelTypeEnum_type = 0;
enumeration_type* IfcAnalysisTheoryTypeEnum_type = 0;
enumeration_type* IfcArithmeticOperatorEnum_type = 0;
enumeration_type* IfcAssemblyPlaceEnum_type = 0;
enumeration_type* IfcBSplineCurveForm_type = 0;
enumeration_type* IfcBeamTypeEnum_type = 0;
enumeration_type* IfcBenchmarkEnum_type = 0;
enumeration_type* IfcBoilerTypeEnum_type = 0;
enumeration_type* IfcBooleanOperator_type = 0;
enumeration_type* IfcBuildingElementProxyTypeEnum_type = 0;
enumeration_type* IfcCableCarrierFittingTypeEnum_type = 0;
enumeration_type* IfcCableCarrierSegmentTypeEnum_type = 0;
enumeration_type* IfcCableSegmentTypeEnum_type = 0;
enumeration_type* IfcChangeActionEnum_type = 0;
enumeration_type* IfcChillerTypeEnum_type = 0;
enumeration_type* IfcCoilTypeEnum_type = 0;
enumeration_type* IfcColumnTypeEnum_type = 0;
enumeration_type* IfcCompressorTypeEnum_type = 0;
enumeration_type* IfcCondenserTypeEnum_type = 0;
enumeration_type* IfcConnectionTypeEnum_type = 0;
enumeration_type* IfcConstraintEnum_type = 0;
enumeration_type* IfcControllerTypeEnum_type = 0;
enumeration_type* IfcCooledBeamTypeEnum_type = 0;
enumeration_type* IfcCoolingTowerTypeEnum_type = 0;
enumeration_type* IfcCostScheduleTypeEnum_type = 0;
enumeration_type* IfcCoveringTypeEnum_type = 0;
enumeration_type* IfcCurrencyEnum_type = 0;
enumeration_type* IfcCurtainWallTypeEnum_type = 0;
enumeration_type* IfcDamperTypeEnum_type = 0;
enumeration_type* IfcDataOriginEnum_type = 0;
enumeration_type* IfcDerivedUnitEnum_type = 0;
enumeration_type* IfcDimensionExtentUsage_type = 0;
enumeration_type* IfcDirectionSenseEnum_type = 0;
enumeration_type* IfcDistributionChamberElementTypeEnum_type = 0;
enumeration_type* IfcDocumentConfidentialityEnum_type = 0;
enumeration_type* IfcDocumentStatusEnum_type = 0;
enumeration_type* IfcDoorPanelOperationEnum_type = 0;
enumeration_type* IfcDoorPanelPositionEnum_type = 0;
enumeration_type* IfcDoorStyleConstructionEnum_type = 0;
enumeration_type* IfcDoorStyleOperationEnum_type = 0;
enumeration_type* IfcDuctFittingTypeEnum_type = 0;
enumeration_type* IfcDuctSegmentTypeEnum_type = 0;
enumeration_type* IfcDuctSilencerTypeEnum_type = 0;
enumeration_type* IfcElectricApplianceTypeEnum_type = 0;
enumeration_type* IfcElectricCurrentEnum_type = 0;
enumeration_type* IfcElectricDistributionPointFunctionEnum_type = 0;
enumeration_type* IfcElectricFlowStorageDeviceTypeEnum_type = 0;
enumeration_type* IfcElectricGeneratorTypeEnum_type = 0;
enumeration_type* IfcElectricHeaterTypeEnum_type = 0;
enumeration_type* IfcElectricMotorTypeEnum_type = 0;
enumeration_type* IfcElectricTimeControlTypeEnum_type = 0;
enumeration_type* IfcElementAssemblyTypeEnum_type = 0;
enumeration_type* IfcElementCompositionEnum_type = 0;
enumeration_type* IfcEnergySequenceEnum_type = 0;
enumeration_type* IfcEnvironmentalImpactCategoryEnum_type = 0;
enumeration_type* IfcEvaporativeCoolerTypeEnum_type = 0;
enumeration_type* IfcEvaporatorTypeEnum_type = 0;
enumeration_type* IfcFanTypeEnum_type = 0;
enumeration_type* IfcFilterTypeEnum_type = 0;
enumeration_type* IfcFireSuppressionTerminalTypeEnum_type = 0;
enumeration_type* IfcFlowDirectionEnum_type = 0;
enumeration_type* IfcFlowInstrumentTypeEnum_type = 0;
enumeration_type* IfcFlowMeterTypeEnum_type = 0;
enumeration_type* IfcFootingTypeEnum_type = 0;
enumeration_type* IfcGasTerminalTypeEnum_type = 0;
enumeration_type* IfcGeometricProjectionEnum_type = 0;
enumeration_type* IfcGlobalOrLocalEnum_type = 0;
enumeration_type* IfcHeatExchangerTypeEnum_type = 0;
enumeration_type* IfcHumidifierTypeEnum_type = 0;
enumeration_type* IfcInternalOrExternalEnum_type = 0;
enumeration_type* IfcInventoryTypeEnum_type = 0;
enumeration_type* IfcJunctionBoxTypeEnum_type = 0;
enumeration_type* IfcLampTypeEnum_type = 0;
enumeration_type* IfcLayerSetDirectionEnum_type = 0;
enumeration_type* IfcLightDistributionCurveEnum_type = 0;
enumeration_type* IfcLightEmissionSourceEnum_type = 0;
enumeration_type* IfcLightFixtureTypeEnum_type = 0;
enumeration_type* IfcLoadGroupTypeEnum_type = 0;
enumeration_type* IfcLogicalOperatorEnum_type = 0;
enumeration_type* IfcMemberTypeEnum_type = 0;
enumeration_type* IfcMotorConnectionTypeEnum_type = 0;
enumeration_type* IfcNullStyle_type = 0;
enumeration_type* IfcObjectTypeEnum_type = 0;
enumeration_type* IfcObjectiveEnum_type = 0;
enumeration_type* IfcOccupantTypeEnum_type = 0;
enumeration_type* IfcOutletTypeEnum_type = 0;
enumeration_type* IfcPermeableCoveringOperationEnum_type = 0;
enumeration_type* IfcPhysicalOrVirtualEnum_type = 0;
enumeration_type* IfcPileConstructionEnum_type = 0;
enumeration_type* IfcPileTypeEnum_type = 0;
enumeration_type* IfcPipeFittingTypeEnum_type = 0;
enumeration_type* IfcPipeSegmentTypeEnum_type = 0;
enumeration_type* IfcPlateTypeEnum_type = 0;
enumeration_type* IfcProcedureTypeEnum_type = 0;
enumeration_type* IfcProfileTypeEnum_type = 0;
enumeration_type* IfcProjectOrderRecordTypeEnum_type = 0;
enumeration_type* IfcProjectOrderTypeEnum_type = 0;
enumeration_type* IfcProjectedOrTrueLengthEnum_type = 0;
enumeration_type* IfcPropertySourceEnum_type = 0;
enumeration_type* IfcProtectiveDeviceTypeEnum_type = 0;
enumeration_type* IfcPumpTypeEnum_type = 0;
enumeration_type* IfcRailingTypeEnum_type = 0;
enumeration_type* IfcRampFlightTypeEnum_type = 0;
enumeration_type* IfcRampTypeEnum_type = 0;
enumeration_type* IfcReflectanceMethodEnum_type = 0;
enumeration_type* IfcReinforcingBarRoleEnum_type = 0;
enumeration_type* IfcReinforcingBarSurfaceEnum_type = 0;
enumeration_type* IfcResourceConsumptionEnum_type = 0;
enumeration_type* IfcRibPlateDirectionEnum_type = 0;
enumeration_type* IfcRoleEnum_type = 0;
enumeration_type* IfcRoofTypeEnum_type = 0;
enumeration_type* IfcSIPrefix_type = 0;
enumeration_type* IfcSIUnitName_type = 0;
enumeration_type* IfcSanitaryTerminalTypeEnum_type = 0;
enumeration_type* IfcSectionTypeEnum_type = 0;
enumeration_type* IfcSensorTypeEnum_type = 0;
enumeration_type* IfcSequenceEnum_type = 0;
enumeration_type* IfcServiceLifeFactorTypeEnum_type = 0;
enumeration_type* IfcServiceLifeTypeEnum_type = 0;
enumeration_type* IfcSlabTypeEnum_type = 0;
enumeration_type* IfcSoundScaleEnum_type = 0;
enumeration_type* IfcSpaceHeaterTypeEnum_type = 0;
enumeration_type* IfcSpaceTypeEnum_type = 0;
enumeration_type* IfcStackTerminalTypeEnum_type = 0;
enumeration_type* IfcStairFlightTypeEnum_type = 0;
enumeration_type* IfcStairTypeEnum_type = 0;
enumeration_type* IfcStateEnum_type = 0;
enumeration_type* IfcStructuralCurveTypeEnum_type = 0;
enumeration_type* IfcStructuralSurfaceTypeEnum_type = 0;
enumeration_type* IfcSurfaceSide_type = 0;
enumeration_type* IfcSurfaceTextureEnum_type = 0;
enumeration_type* IfcSwitchingDeviceTypeEnum_type = 0;
enumeration_type* IfcTankTypeEnum_type = 0;
enumeration_type* IfcTendonTypeEnum_type = 0;
enumeration_type* IfcTextPath_type = 0;
enumeration_type* IfcThermalLoadSourceEnum_type = 0;
enumeration_type* IfcThermalLoadTypeEnum_type = 0;
enumeration_type* IfcTimeSeriesDataTypeEnum_type = 0;
enumeration_type* IfcTimeSeriesScheduleTypeEnum_type = 0;
enumeration_type* IfcTransformerTypeEnum_type = 0;
enumeration_type* IfcTransitionCode_type = 0;
enumeration_type* IfcTransportElementTypeEnum_type = 0;
enumeration_type* IfcTrimmingPreference_type = 0;
enumeration_type* IfcTubeBundleTypeEnum_type = 0;
enumeration_type* IfcUnitEnum_type = 0;
enumeration_type* IfcUnitaryEquipmentTypeEnum_type = 0;
enumeration_type* IfcValveTypeEnum_type = 0;
enumeration_type* IfcVibrationIsolatorTypeEnum_type = 0;
enumeration_type* IfcWallTypeEnum_type = 0;
enumeration_type* IfcWasteTerminalTypeEnum_type = 0;
enumeration_type* IfcWindowPanelOperationEnum_type = 0;
enumeration_type* IfcWindowPanelPositionEnum_type = 0;
enumeration_type* IfcWindowStyleConstructionEnum_type = 0;
enumeration_type* IfcWindowStyleOperationEnum_type = 0;
enumeration_type* IfcWorkControlTypeEnum_type = 0;

class IFC2X3_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const {
        switch(data->type()->index_in_schema()) {
            case 0: return new Ifc2DCompositeCurve(data);
            case 1: return new IfcAbsorbedDoseMeasure(data);
            case 2: return new IfcAccelerationMeasure(data);
            case 3: return new IfcActionRequest(data);
            case 6: return new IfcActor(data);
            case 7: return new IfcActorRole(data);
            case 9: return new IfcActuatorType(data);
            case 11: return new IfcAddress(data);
            case 14: return new IfcAirTerminalBoxType(data);
            case 16: return new IfcAirTerminalType(data);
            case 18: return new IfcAirToAirHeatRecoveryType(data);
            case 20: return new IfcAlarmType(data);
            case 22: return new IfcAmountOfSubstanceMeasure(data);
            case 25: return new IfcAngularDimension(data);
            case 26: return new IfcAngularVelocityMeasure(data);
            case 27: return new IfcAnnotation(data);
            case 28: return new IfcAnnotationCurveOccurrence(data);
            case 29: return new IfcAnnotationFillArea(data);
            case 30: return new IfcAnnotationFillAreaOccurrence(data);
            case 31: return new IfcAnnotationOccurrence(data);
            case 32: return new IfcAnnotationSurface(data);
            case 33: return new IfcAnnotationSurfaceOccurrence(data);
            case 34: return new IfcAnnotationSymbolOccurrence(data);
            case 35: return new IfcAnnotationTextOccurrence(data);
            case 36: return new IfcApplication(data);
            case 37: return new IfcAppliedValue(data);
            case 38: return new IfcAppliedValueRelationship(data);
            case 40: return new IfcApproval(data);
            case 41: return new IfcApprovalActorRelationship(data);
            case 42: return new IfcApprovalPropertyRelationship(data);
            case 43: return new IfcApprovalRelationship(data);
            case 44: return new IfcArbitraryClosedProfileDef(data);
            case 45: return new IfcArbitraryOpenProfileDef(data);
            case 46: return new IfcArbitraryProfileDefWithVoids(data);
            case 47: return new IfcAreaMeasure(data);
            case 50: return new IfcAsset(data);
            case 51: return new IfcAsymmetricIShapeProfileDef(data);
            case 52: return new IfcAxis1Placement(data);
            case 54: return new IfcAxis2Placement2D(data);
            case 55: return new IfcAxis2Placement3D(data);
            case 56: return new IfcBSplineCurve(data);
            case 58: return new IfcBeam(data);
            case 59: return new IfcBeamType(data);
            case 62: return new IfcBezierCurve(data);
            case 63: return new IfcBlobTexture(data);
            case 64: return new IfcBlock(data);
            case 65: return new IfcBoilerType(data);
            case 67: return new IfcBoolean(data);
            case 68: return new IfcBooleanClippingResult(data);
            case 71: return new IfcBooleanResult(data);
            case 72: return new IfcBoundaryCondition(data);
            case 73: return new IfcBoundaryEdgeCondition(data);
            case 74: return new IfcBoundaryFaceCondition(data);
            case 75: return new IfcBoundaryNodeCondition(data);
            case 76: return new IfcBoundaryNodeConditionWarping(data);
            case 77: return new IfcBoundedCurve(data);
            case 78: return new IfcBoundedSurface(data);
            case 79: return new IfcBoundingBox(data);
            case 80: return new IfcBoxAlignment(data);
            case 81: return new IfcBoxedHalfSpace(data);
            case 82: return new IfcBuilding(data);
            case 83: return new IfcBuildingElement(data);
            case 84: return new IfcBuildingElementComponent(data);
            case 85: return new IfcBuildingElementPart(data);
            case 86: return new IfcBuildingElementProxy(data);
            case 87: return new IfcBuildingElementProxyType(data);
            case 89: return new IfcBuildingElementType(data);
            case 90: return new IfcBuildingStorey(data);
            case 91: return new IfcCShapeProfileDef(data);
            case 92: return new IfcCableCarrierFittingType(data);
            case 94: return new IfcCableCarrierSegmentType(data);
            case 96: return new IfcCableSegmentType(data);
            case 98: return new IfcCalendarDate(data);
            case 99: return new IfcCartesianPoint(data);
            case 100: return new IfcCartesianTransformationOperator(data);
            case 101: return new IfcCartesianTransformationOperator2D(data);
            case 102: return new IfcCartesianTransformationOperator2DnonUniform(data);
            case 103: return new IfcCartesianTransformationOperator3D(data);
            case 104: return new IfcCartesianTransformationOperator3DnonUniform(data);
            case 105: return new IfcCenterLineProfileDef(data);
            case 106: return new IfcChamferEdgeFeature(data);
            case 109: return new IfcChillerType(data);
            case 111: return new IfcCircle(data);
            case 112: return new IfcCircleHollowProfileDef(data);
            case 113: return new IfcCircleProfileDef(data);
            case 114: return new IfcClassification(data);
            case 115: return new IfcClassificationItem(data);
            case 116: return new IfcClassificationItemRelationship(data);
            case 117: return new IfcClassificationNotation(data);
            case 118: return new IfcClassificationNotationFacet(data);
            case 120: return new IfcClassificationReference(data);
            case 121: return new IfcClosedShell(data);
            case 122: return new IfcCoilType(data);
            case 126: return new IfcColourRgb(data);
            case 127: return new IfcColourSpecification(data);
            case 128: return new IfcColumn(data);
            case 129: return new IfcColumnType(data);
            case 131: return new IfcComplexNumber(data);
            case 132: return new IfcComplexProperty(data);
            case 133: return new IfcCompositeCurve(data);
            case 134: return new IfcCompositeCurveSegment(data);
            case 135: return new IfcCompositeProfileDef(data);
            case 136: return new IfcCompoundPlaneAngleMeasure(data);
            case 137: return new IfcCompressorType(data);
            case 139: return new IfcCondenserType(data);
            case 141: return new IfcCondition(data);
            case 142: return new IfcConditionCriterion(data);
            case 144: return new IfcConic(data);
            case 145: return new IfcConnectedFaceSet(data);
            case 146: return new IfcConnectionCurveGeometry(data);
            case 147: return new IfcConnectionGeometry(data);
            case 148: return new IfcConnectionPointEccentricity(data);
            case 149: return new IfcConnectionPointGeometry(data);
            case 150: return new IfcConnectionPortGeometry(data);
            case 151: return new IfcConnectionSurfaceGeometry(data);
            case 153: return new IfcConstraint(data);
            case 154: return new IfcConstraintAggregationRelationship(data);
            case 155: return new IfcConstraintClassificationRelationship(data);
            case 157: return new IfcConstraintRelationship(data);
            case 158: return new IfcConstructionEquipmentResource(data);
            case 159: return new IfcConstructionMaterialResource(data);
            case 160: return new IfcConstructionProductResource(data);
            case 161: return new IfcConstructionResource(data);
            case 162: return new IfcContextDependentMeasure(data);
            case 163: return new IfcContextDependentUnit(data);
            case 164: return new IfcControl(data);
            case 165: return new IfcControllerType(data);
            case 167: return new IfcConversionBasedUnit(data);
            case 168: return new IfcCooledBeamType(data);
            case 170: return new IfcCoolingTowerType(data);
            case 172: return new IfcCoordinatedUniversalTimeOffset(data);
            case 173: return new IfcCostItem(data);
            case 174: return new IfcCostSchedule(data);
            case 176: return new IfcCostValue(data);
            case 177: return new IfcCountMeasure(data);
            case 178: return new IfcCovering(data);
            case 179: return new IfcCoveringType(data);
            case 181: return new IfcCraneRailAShapeProfileDef(data);
            case 182: return new IfcCraneRailFShapeProfileDef(data);
            case 183: return new IfcCrewResource(data);
            case 184: return new IfcCsgPrimitive3D(data);
            case 186: return new IfcCsgSolid(data);
            case 188: return new IfcCurrencyRelationship(data);
            case 189: return new IfcCurtainWall(data);
            case 190: return new IfcCurtainWallType(data);
            case 192: return new IfcCurvatureMeasure(data);
            case 193: return new IfcCurve(data);
            case 194: return new IfcCurveBoundedPlane(data);
            case 197: return new IfcCurveStyle(data);
            case 198: return new IfcCurveStyleFont(data);
            case 199: return new IfcCurveStyleFontAndScaling(data);
            case 200: return new IfcCurveStyleFontPattern(data);
            case 202: return new IfcDamperType(data);
            case 205: return new IfcDateAndTime(data);
            case 207: return new IfcDayInMonthNumber(data);
            case 208: return new IfcDaylightSavingHour(data);
            case 209: return new IfcDefinedSymbol(data);
            case 212: return new IfcDerivedProfileDef(data);
            case 213: return new IfcDerivedUnit(data);
            case 214: return new IfcDerivedUnitElement(data);
            case 216: return new IfcDescriptiveMeasure(data);
            case 217: return new IfcDiameterDimension(data);
            case 218: return new IfcDimensionCalloutRelationship(data);
            case 219: return new IfcDimensionCount(data);
            case 220: return new IfcDimensionCurve(data);
            case 221: return new IfcDimensionCurveDirectedCallout(data);
            case 222: return new IfcDimensionCurveTerminator(data);
            case 224: return new IfcDimensionPair(data);
            case 225: return new IfcDimensionalExponents(data);
            case 226: return new IfcDirection(data);
            case 228: return new IfcDiscreteAccessory(data);
            case 229: return new IfcDiscreteAccessoryType(data);
            case 230: return new IfcDistributionChamberElement(data);
            case 231: return new IfcDistributionChamberElementType(data);
            case 233: return new IfcDistributionControlElement(data);
            case 234: return new IfcDistributionControlElementType(data);
            case 235: return new IfcDistributionElement(data);
            case 236: return new IfcDistributionElementType(data);
            case 237: return new IfcDistributionFlowElement(data);
            case 238: return new IfcDistributionFlowElementType(data);
            case 239: return new IfcDistributionPort(data);
            case 241: return new IfcDocumentElectronicFormat(data);
            case 242: return new IfcDocumentInformation(data);
            case 243: return new IfcDocumentInformationRelationship(data);
            case 244: return new IfcDocumentReference(data);
            case 247: return new IfcDoor(data);
            case 248: return new IfcDoorLiningProperties(data);
            case 251: return new IfcDoorPanelProperties(data);
            case 252: return new IfcDoorStyle(data);
            case 255: return new IfcDoseEquivalentMeasure(data);
            case 256: return new IfcDraughtingCallout(data);
            case 258: return new IfcDraughtingCalloutRelationship(data);
            case 259: return new IfcDraughtingPreDefinedColour(data);
            case 260: return new IfcDraughtingPreDefinedCurveFont(data);
            case 261: return new IfcDraughtingPreDefinedTextFont(data);
            case 262: return new IfcDuctFittingType(data);
            case 264: return new IfcDuctSegmentType(data);
            case 266: return new IfcDuctSilencerType(data);
            case 268: return new IfcDynamicViscosityMeasure(data);
            case 269: return new IfcEdge(data);
            case 270: return new IfcEdgeCurve(data);
            case 271: return new IfcEdgeFeature(data);
            case 272: return new IfcEdgeLoop(data);
            case 273: return new IfcElectricApplianceType(data);
            case 275: return new IfcElectricCapacitanceMeasure(data);
            case 276: return new IfcElectricChargeMeasure(data);
            case 277: return new IfcElectricConductanceMeasure(data);
            case 279: return new IfcElectricCurrentMeasure(data);
            case 280: return new IfcElectricDistributionPoint(data);
            case 282: return new IfcElectricFlowStorageDeviceType(data);
            case 284: return new IfcElectricGeneratorType(data);
            case 286: return new IfcElectricHeaterType(data);
            case 288: return new IfcElectricMotorType(data);
            case 290: return new IfcElectricResistanceMeasure(data);
            case 291: return new IfcElectricTimeControlType(data);
            case 293: return new IfcElectricVoltageMeasure(data);
            case 294: return new IfcElectricalBaseProperties(data);
            case 295: return new IfcElectricalCircuit(data);
            case 296: return new IfcElectricalElement(data);
            case 297: return new IfcElement(data);
            case 298: return new IfcElementAssembly(data);
            case 300: return new IfcElementComponent(data);
            case 301: return new IfcElementComponentType(data);
            case 303: return new IfcElementQuantity(data);
            case 304: return new IfcElementType(data);
            case 305: return new IfcElementarySurface(data);
            case 306: return new IfcEllipse(data);
            case 307: return new IfcEllipseProfileDef(data);
            case 308: return new IfcEnergyConversionDevice(data);
            case 309: return new IfcEnergyConversionDeviceType(data);
            case 310: return new IfcEnergyMeasure(data);
            case 311: return new IfcEnergyProperties(data);
            case 314: return new IfcEnvironmentalImpactValue(data);
            case 315: return new IfcEquipmentElement(data);
            case 316: return new IfcEquipmentStandard(data);
            case 317: return new IfcEvaporativeCoolerType(data);
            case 319: return new IfcEvaporatorType(data);
            case 321: return new IfcExtendedMaterialProperties(data);
            case 322: return new IfcExternalReference(data);
            case 323: return new IfcExternallyDefinedHatchStyle(data);
            case 324: return new IfcExternallyDefinedSurfaceStyle(data);
            case 325: return new IfcExternallyDefinedSymbol(data);
            case 326: return new IfcExternallyDefinedTextFont(data);
            case 327: return new IfcExtrudedAreaSolid(data);
            case 328: return new IfcFace(data);
            case 329: return new IfcFaceBasedSurfaceModel(data);
            case 330: return new IfcFaceBound(data);
            case 331: return new IfcFaceOuterBound(data);
            case 332: return new IfcFaceSurface(data);
            case 333: return new IfcFacetedBrep(data);
            case 334: return new IfcFacetedBrepWithVoids(data);
            case 335: return new IfcFailureConnectionCondition(data);
            case 336: return new IfcFanType(data);
            case 338: return new IfcFastener(data);
            case 339: return new IfcFastenerType(data);
            case 340: return new IfcFeatureElement(data);
            case 341: return new IfcFeatureElementAddition(data);
            case 342: return new IfcFeatureElementSubtraction(data);
            case 343: return new IfcFillAreaStyle(data);
            case 344: return new IfcFillAreaStyleHatching(data);
            case 346: return new IfcFillAreaStyleTileSymbolWithStyle(data);
            case 347: return new IfcFillAreaStyleTiles(data);
            case 349: return new IfcFilterType(data);
            case 351: return new IfcFireSuppressionTerminalType(data);
            case 353: return new IfcFlowController(data);
            case 354: return new IfcFlowControllerType(data);
            case 356: return new IfcFlowFitting(data);
            case 357: return new IfcFlowFittingType(data);
            case 358: return new IfcFlowInstrumentType(data);
            case 360: return new IfcFlowMeterType(data);
            case 362: return new IfcFlowMovingDevice(data);
            case 363: return new IfcFlowMovingDeviceType(data);
            case 364: return new IfcFlowSegment(data);
            case 365: return new IfcFlowSegmentType(data);
            case 366: return new IfcFlowStorageDevice(data);
            case 367: return new IfcFlowStorageDeviceType(data);
            case 368: return new IfcFlowTerminal(data);
            case 369: return new IfcFlowTerminalType(data);
            case 370: return new IfcFlowTreatmentDevice(data);
            case 371: return new IfcFlowTreatmentDeviceType(data);
            case 372: return new IfcFluidFlowProperties(data);
            case 373: return new IfcFontStyle(data);
            case 374: return new IfcFontVariant(data);
            case 375: return new IfcFontWeight(data);
            case 376: return new IfcFooting(data);
            case 378: return new IfcForceMeasure(data);
            case 379: return new IfcFrequencyMeasure(data);
            case 380: return new IfcFuelProperties(data);
            case 381: return new IfcFurnishingElement(data);
            case 382: return new IfcFurnishingElementType(data);
            case 383: return new IfcFurnitureStandard(data);
            case 384: return new IfcFurnitureType(data);
            case 385: return new IfcGasTerminalType(data);
            case 387: return new IfcGeneralMaterialProperties(data);
            case 388: return new IfcGeneralProfileProperties(data);
            case 389: return new IfcGeometricCurveSet(data);
            case 391: return new IfcGeometricRepresentationContext(data);
            case 392: return new IfcGeometricRepresentationItem(data);
            case 393: return new IfcGeometricRepresentationSubContext(data);
            case 394: return new IfcGeometricSet(data);
            case 397: return new IfcGloballyUniqueId(data);
            case 398: return new IfcGrid(data);
            case 399: return new IfcGridAxis(data);
            case 400: return new IfcGridPlacement(data);
            case 401: return new IfcGroup(data);
            case 402: return new IfcHalfSpaceSolid(data);
            case 404: return new IfcHeatExchangerType(data);
            case 406: return new IfcHeatFluxDensityMeasure(data);
            case 407: return new IfcHeatingValueMeasure(data);
            case 408: return new IfcHourInDay(data);
            case 409: return new IfcHumidifierType(data);
            case 411: return new IfcHygroscopicMaterialProperties(data);
            case 412: return new IfcIShapeProfileDef(data);
            case 413: return new IfcIdentifier(data);
            case 414: return new IfcIlluminanceMeasure(data);
            case 415: return new IfcImageTexture(data);
            case 416: return new IfcInductanceMeasure(data);
            case 417: return new IfcInteger(data);
            case 418: return new IfcIntegerCountRateMeasure(data);
            case 420: return new IfcInventory(data);
            case 422: return new IfcIonConcentrationMeasure(data);
            case 423: return new IfcIrregularTimeSeries(data);
            case 424: return new IfcIrregularTimeSeriesValue(data);
            case 425: return new IfcIsothermalMoistureCapacityMeasure(data);
            case 426: return new IfcJunctionBoxType(data);
            case 428: return new IfcKinematicViscosityMeasure(data);
            case 429: return new IfcLShapeProfileDef(data);
            case 430: return new IfcLabel(data);
            case 431: return new IfcLaborResource(data);
            case 432: return new IfcLampType(data);
            case 436: return new IfcLengthMeasure(data);
            case 437: return new IfcLibraryInformation(data);
            case 438: return new IfcLibraryReference(data);
            case 441: return new IfcLightDistributionData(data);
            case 444: return new IfcLightFixtureType(data);
            case 446: return new IfcLightIntensityDistribution(data);
            case 447: return new IfcLightSource(data);
            case 448: return new IfcLightSourceAmbient(data);
            case 449: return new IfcLightSourceDirectional(data);
            case 450: return new IfcLightSourceGoniometric(data);
            case 451: return new IfcLightSourcePositional(data);
            case 452: return new IfcLightSourceSpot(data);
            case 453: return new IfcLine(data);
            case 454: return new IfcLinearDimension(data);
            case 455: return new IfcLinearForceMeasure(data);
            case 456: return new IfcLinearMomentMeasure(data);
            case 457: return new IfcLinearStiffnessMeasure(data);
            case 458: return new IfcLinearVelocityMeasure(data);
            case 460: return new IfcLocalPlacement(data);
            case 461: return new IfcLocalTime(data);
            case 462: return new IfcLogical(data);
            case 464: return new IfcLoop(data);
            case 465: return new IfcLuminousFluxMeasure(data);
            case 466: return new IfcLuminousIntensityDistributionMeasure(data);
            case 467: return new IfcLuminousIntensityMeasure(data);
            case 468: return new IfcMagneticFluxDensityMeasure(data);
            case 469: return new IfcMagneticFluxMeasure(data);
            case 470: return new IfcManifoldSolidBrep(data);
            case 471: return new IfcMappedItem(data);
            case 472: return new IfcMassDensityMeasure(data);
            case 473: return new IfcMassFlowRateMeasure(data);
            case 474: return new IfcMassMeasure(data);
            case 475: return new IfcMassPerLengthMeasure(data);
            case 476: return new IfcMaterial(data);
            case 477: return new IfcMaterialClassificationRelationship(data);
            case 478: return new IfcMaterialDefinitionRepresentation(data);
            case 479: return new IfcMaterialLayer(data);
            case 480: return new IfcMaterialLayerSet(data);
            case 481: return new IfcMaterialLayerSetUsage(data);
            case 482: return new IfcMaterialList(data);
            case 483: return new IfcMaterialProperties(data);
            case 486: return new IfcMeasureWithUnit(data);
            case 487: return new IfcMechanicalConcreteMaterialProperties(data);
            case 488: return new IfcMechanicalFastener(data);
            case 489: return new IfcMechanicalFastenerType(data);
            case 490: return new IfcMechanicalMaterialProperties(data);
            case 491: return new IfcMechanicalSteelMaterialProperties(data);
            case 492: return new IfcMember(data);
            case 493: return new IfcMemberType(data);
            case 495: return new IfcMetric(data);
            case 497: return new IfcMinuteInHour(data);
            case 498: return new IfcModulusOfElasticityMeasure(data);
            case 499: return new IfcModulusOfLinearSubgradeReactionMeasure(data);
            case 500: return new IfcModulusOfRotationalSubgradeReactionMeasure(data);
            case 501: return new IfcModulusOfSubgradeReactionMeasure(data);
            case 502: return new IfcMoistureDiffusivityMeasure(data);
            case 503: return new IfcMolecularWeightMeasure(data);
            case 504: return new IfcMomentOfInertiaMeasure(data);
            case 505: return new IfcMonetaryMeasure(data);
            case 506: return new IfcMonetaryUnit(data);
            case 507: return new IfcMonthInYearNumber(data);
            case 508: return new IfcMotorConnectionType(data);
            case 510: return new IfcMove(data);
            case 511: return new IfcNamedUnit(data);
            case 512: return new IfcNormalisedRatioMeasure(data);
            case 514: return new IfcNumericMeasure(data);
            case 515: return new IfcObject(data);
            case 516: return new IfcObjectDefinition(data);
            case 517: return new IfcObjectPlacement(data);
            case 520: return new IfcObjective(data);
            case 522: return new IfcOccupant(data);
            case 524: return new IfcOffsetCurve2D(data);
            case 525: return new IfcOffsetCurve3D(data);
            case 526: return new IfcOneDirectionRepeatFactor(data);
            case 527: return new IfcOpenShell(data);
            case 528: return new IfcOpeningElement(data);
            case 529: return new IfcOpticalMaterialProperties(data);
            case 530: return new IfcOrderAction(data);
            case 531: return new IfcOrganization(data);
            case 532: return new IfcOrganizationRelationship(data);
            case 534: return new IfcOrientedEdge(data);
            case 535: return new IfcOutletType(data);
            case 537: return new IfcOwnerHistory(data);
            case 538: return new IfcPHMeasure(data);
            case 539: return new IfcParameterValue(data);
            case 540: return new IfcParameterizedProfileDef(data);
            case 541: return new IfcPath(data);
            case 542: return new IfcPerformanceHistory(data);
            case 544: return new IfcPermeableCoveringProperties(data);
            case 545: return new IfcPermit(data);
            case 546: return new IfcPerson(data);
            case 547: return new IfcPersonAndOrganization(data);
            case 548: return new IfcPhysicalComplexQuantity(data);
            case 550: return new IfcPhysicalQuantity(data);
            case 551: return new IfcPhysicalSimpleQuantity(data);
            case 552: return new IfcPile(data);
            case 555: return new IfcPipeFittingType(data);
            case 557: return new IfcPipeSegmentType(data);
            case 559: return new IfcPixelTexture(data);
            case 560: return new IfcPlacement(data);
            case 561: return new IfcPlanarBox(data);
            case 562: return new IfcPlanarExtent(data);
            case 563: return new IfcPlanarForceMeasure(data);
            case 564: return new IfcPlane(data);
            case 565: return new IfcPlaneAngleMeasure(data);
            case 566: return new IfcPlate(data);
            case 567: return new IfcPlateType(data);
            case 569: return new IfcPoint(data);
            case 570: return new IfcPointOnCurve(data);
            case 571: return new IfcPointOnSurface(data);
            case 573: return new IfcPolyLoop(data);
            case 574: return new IfcPolygonalBoundedHalfSpace(data);
            case 575: return new IfcPolyline(data);
            case 576: return new IfcPort(data);
            case 577: return new IfcPositiveLengthMeasure(data);
            case 578: return new IfcPositivePlaneAngleMeasure(data);
            case 579: return new IfcPositiveRatioMeasure(data);
            case 580: return new IfcPostalAddress(data);
            case 581: return new IfcPowerMeasure(data);
            case 582: return new IfcPreDefinedColour(data);
            case 583: return new IfcPreDefinedCurveFont(data);
            case 584: return new IfcPreDefinedDimensionSymbol(data);
            case 585: return new IfcPreDefinedItem(data);
            case 586: return new IfcPreDefinedPointMarkerSymbol(data);
            case 587: return new IfcPreDefinedSymbol(data);
            case 588: return new IfcPreDefinedTerminatorSymbol(data);
            case 589: return new IfcPreDefinedTextFont(data);
            case 590: return new IfcPresentableText(data);
            case 591: return new IfcPresentationLayerAssignment(data);
            case 592: return new IfcPresentationLayerWithStyle(data);
            case 593: return new IfcPresentationStyle(data);
            case 594: return new IfcPresentationStyleAssignment(data);
            case 596: return new IfcPressureMeasure(data);
            case 597: return new IfcProcedure(data);
            case 599: return new IfcProcess(data);
            case 600: return new IfcProduct(data);
            case 601: return new IfcProductDefinitionShape(data);
            case 602: return new IfcProductRepresentation(data);
            case 603: return new IfcProductsOfCombustionProperties(data);
            case 604: return new IfcProfileDef(data);
            case 605: return new IfcProfileProperties(data);
            case 607: return new IfcProject(data);
            case 608: return new IfcProjectOrder(data);
            case 609: return new IfcProjectOrderRecord(data);
            case 613: return new IfcProjectionCurve(data);
            case 614: return new IfcProjectionElement(data);
            case 615: return new IfcProperty(data);
            case 616: return new IfcPropertyBoundedValue(data);
            case 617: return new IfcPropertyConstraintRelationship(data);
            case 618: return new IfcPropertyDefinition(data);
            case 619: return new IfcPropertyDependencyRelationship(data);
            case 620: return new IfcPropertyEnumeratedValue(data);
            case 621: return new IfcPropertyEnumeration(data);
            case 622: return new IfcPropertyListValue(data);
            case 623: return new IfcPropertyReferenceValue(data);
            case 624: return new IfcPropertySet(data);
            case 625: return new IfcPropertySetDefinition(data);
            case 626: return new IfcPropertySingleValue(data);
            case 628: return new IfcPropertyTableValue(data);
            case 629: return new IfcProtectiveDeviceType(data);
            case 631: return new IfcProxy(data);
            case 632: return new IfcPumpType(data);
            case 634: return new IfcQuantityArea(data);
            case 635: return new IfcQuantityCount(data);
            case 636: return new IfcQuantityLength(data);
            case 637: return new IfcQuantityTime(data);
            case 638: return new IfcQuantityVolume(data);
            case 639: return new IfcQuantityWeight(data);
            case 640: return new IfcRadioActivityMeasure(data);
            case 641: return new IfcRadiusDimension(data);
            case 642: return new IfcRailing(data);
            case 643: return new IfcRailingType(data);
            case 645: return new IfcRamp(data);
            case 646: return new IfcRampFlight(data);
            case 647: return new IfcRampFlightType(data);
            case 650: return new IfcRatioMeasure(data);
            case 651: return new IfcRationalBezierCurve(data);
            case 652: return new IfcReal(data);
            case 653: return new IfcRectangleHollowProfileDef(data);
            case 654: return new IfcRectangleProfileDef(data);
            case 655: return new IfcRectangularPyramid(data);
            case 656: return new IfcRectangularTrimmedSurface(data);
            case 657: return new IfcReferencesValueDocument(data);
            case 659: return new IfcRegularTimeSeries(data);
            case 660: return new IfcReinforcementBarProperties(data);
            case 661: return new IfcReinforcementDefinitionProperties(data);
            case 662: return new IfcReinforcingBar(data);
            case 665: return new IfcReinforcingElement(data);
            case 666: return new IfcReinforcingMesh(data);
            case 667: return new IfcRelAggregates(data);
            case 668: return new IfcRelAssigns(data);
            case 669: return new IfcRelAssignsTasks(data);
            case 670: return new IfcRelAssignsToActor(data);
            case 671: return new IfcRelAssignsToControl(data);
            case 672: return new IfcRelAssignsToGroup(data);
            case 673: return new IfcRelAssignsToProcess(data);
            case 674: return new IfcRelAssignsToProduct(data);
            case 675: return new IfcRelAssignsToProjectOrder(data);
            case 676: return new IfcRelAssignsToResource(data);
            case 677: return new IfcRelAssociates(data);
            case 678: return new IfcRelAssociatesAppliedValue(data);
            case 679: return new IfcRelAssociatesApproval(data);
            case 680: return new IfcRelAssociatesClassification(data);
            case 681: return new IfcRelAssociatesConstraint(data);
            case 682: return new IfcRelAssociatesDocument(data);
            case 683: return new IfcRelAssociatesLibrary(data);
            case 684: return new IfcRelAssociatesMaterial(data);
            case 685: return new IfcRelAssociatesProfileProperties(data);
            case 686: return new IfcRelConnects(data);
            case 687: return new IfcRelConnectsElements(data);
            case 688: return new IfcRelConnectsPathElements(data);
            case 689: return new IfcRelConnectsPortToElement(data);
            case 690: return new IfcRelConnectsPorts(data);
            case 691: return new IfcRelConnectsStructuralActivity(data);
            case 692: return new IfcRelConnectsStructuralElement(data);
            case 693: return new IfcRelConnectsStructuralMember(data);
            case 694: return new IfcRelConnectsWithEccentricity(data);
            case 695: return new IfcRelConnectsWithRealizingElements(data);
            case 696: return new IfcRelContainedInSpatialStructure(data);
            case 697: return new IfcRelCoversBldgElements(data);
            case 698: return new IfcRelCoversSpaces(data);
            case 699: return new IfcRelDecomposes(data);
            case 700: return new IfcRelDefines(data);
            case 701: return new IfcRelDefinesByProperties(data);
            case 702: return new IfcRelDefinesByType(data);
            case 703: return new IfcRelFillsElement(data);
            case 704: return new IfcRelFlowControlElements(data);
            case 705: return new IfcRelInteractionRequirements(data);
            case 706: return new IfcRelNests(data);
            case 707: return new IfcRelOccupiesSpaces(data);
            case 708: return new IfcRelOverridesProperties(data);
            case 709: return new IfcRelProjectsElement(data);
            case 710: return new IfcRelReferencedInSpatialStructure(data);
            case 711: return new IfcRelSchedulesCostItems(data);
            case 712: return new IfcRelSequence(data);
            case 713: return new IfcRelServicesBuildings(data);
            case 714: return new IfcRelSpaceBoundary(data);
            case 715: return new IfcRelVoidsElement(data);
            case 716: return new IfcRelationship(data);
            case 717: return new IfcRelaxation(data);
            case 718: return new IfcRepresentation(data);
            case 719: return new IfcRepresentationContext(data);
            case 720: return new IfcRepresentationItem(data);
            case 721: return new IfcRepresentationMap(data);
            case 722: return new IfcResource(data);
            case 724: return new IfcRevolvedAreaSolid(data);
            case 726: return new IfcRibPlateProfileProperties(data);
            case 727: return new IfcRightCircularCone(data);
            case 728: return new IfcRightCircularCylinder(data);
            case 730: return new IfcRoof(data);
            case 732: return new IfcRoot(data);
            case 733: return new IfcRotationalFrequencyMeasure(data);
            case 734: return new IfcRotationalMassMeasure(data);
            case 735: return new IfcRotationalStiffnessMeasure(data);
            case 736: return new IfcRoundedEdgeFeature(data);
            case 737: return new IfcRoundedRectangleProfileDef(data);
            case 739: return new IfcSIUnit(data);
            case 741: return new IfcSanitaryTerminalType(data);
            case 743: return new IfcScheduleTimeControl(data);
            case 744: return new IfcSecondInMinute(data);
            case 745: return new IfcSectionModulusMeasure(data);
            case 746: return new IfcSectionProperties(data);
            case 747: return new IfcSectionReinforcementProperties(data);
            case 749: return new IfcSectionalAreaIntegralMeasure(data);
            case 750: return new IfcSectionedSpine(data);
            case 751: return new IfcSensorType(data);
            case 754: return new IfcServiceLife(data);
            case 755: return new IfcServiceLifeFactor(data);
            case 758: return new IfcShapeAspect(data);
            case 759: return new IfcShapeModel(data);
            case 760: return new IfcShapeRepresentation(data);
            case 761: return new IfcShearModulusMeasure(data);
            case 763: return new IfcShellBasedSurfaceModel(data);
            case 764: return new IfcSimpleProperty(data);
            case 766: return new IfcSite(data);
            case 768: return new IfcSlab(data);
            case 769: return new IfcSlabType(data);
            case 771: return new IfcSlippageConnectionCondition(data);
            case 772: return new IfcSolidAngleMeasure(data);
            case 773: return new IfcSolidModel(data);
            case 774: return new IfcSoundPowerMeasure(data);
            case 775: return new IfcSoundPressureMeasure(data);
            case 776: return new IfcSoundProperties(data);
            case 778: return new IfcSoundValue(data);
            case 779: return new IfcSpace(data);
            case 780: return new IfcSpaceHeaterType(data);
            case 782: return new IfcSpaceProgram(data);
            case 783: return new IfcSpaceThermalLoadProperties(data);
            case 784: return new IfcSpaceType(data);
            case 786: return new IfcSpatialStructureElement(data);
            case 787: return new IfcSpatialStructureElementType(data);
            case 788: return new IfcSpecificHeatCapacityMeasure(data);
            case 789: return new IfcSpecularExponent(data);
            case 791: return new IfcSpecularRoughness(data);
            case 792: return new IfcSphere(data);
            case 793: return new IfcStackTerminalType(data);
            case 795: return new IfcStair(data);
            case 796: return new IfcStairFlight(data);
            case 797: return new IfcStairFlightType(data);
            case 801: return new IfcStructuralAction(data);
            case 802: return new IfcStructuralActivity(data);
            case 804: return new IfcStructuralAnalysisModel(data);
            case 805: return new IfcStructuralConnection(data);
            case 806: return new IfcStructuralConnectionCondition(data);
            case 807: return new IfcStructuralCurveConnection(data);
            case 808: return new IfcStructuralCurveMember(data);
            case 809: return new IfcStructuralCurveMemberVarying(data);
            case 811: return new IfcStructuralItem(data);
            case 812: return new IfcStructuralLinearAction(data);
            case 813: return new IfcStructuralLinearActionVarying(data);
            case 814: return new IfcStructuralLoad(data);
            case 815: return new IfcStructuralLoadGroup(data);
            case 816: return new IfcStructuralLoadLinearForce(data);
            case 817: return new IfcStructuralLoadPlanarForce(data);
            case 818: return new IfcStructuralLoadSingleDisplacement(data);
            case 819: return new IfcStructuralLoadSingleDisplacementDistortion(data);
            case 820: return new IfcStructuralLoadSingleForce(data);
            case 821: return new IfcStructuralLoadSingleForceWarping(data);
            case 822: return new IfcStructuralLoadStatic(data);
            case 823: return new IfcStructuralLoadTemperature(data);
            case 824: return new IfcStructuralMember(data);
            case 825: return new IfcStructuralPlanarAction(data);
            case 826: return new IfcStructuralPlanarActionVarying(data);
            case 827: return new IfcStructuralPointAction(data);
            case 828: return new IfcStructuralPointConnection(data);
            case 829: return new IfcStructuralPointReaction(data);
            case 830: return new IfcStructuralProfileProperties(data);
            case 831: return new IfcStructuralReaction(data);
            case 832: return new IfcStructuralResultGroup(data);
            case 833: return new IfcStructuralSteelProfileProperties(data);
            case 834: return new IfcStructuralSurfaceConnection(data);
            case 835: return new IfcStructuralSurfaceMember(data);
            case 836: return new IfcStructuralSurfaceMemberVarying(data);
            case 838: return new IfcStructuredDimensionCallout(data);
            case 839: return new IfcStyleModel(data);
            case 840: return new IfcStyledItem(data);
            case 841: return new IfcStyledRepresentation(data);
            case 842: return new IfcSubContractResource(data);
            case 843: return new IfcSubedge(data);
            case 844: return new IfcSurface(data);
            case 845: return new IfcSurfaceCurveSweptAreaSolid(data);
            case 846: return new IfcSurfaceOfLinearExtrusion(data);
            case 847: return new IfcSurfaceOfRevolution(data);
            case 850: return new IfcSurfaceStyle(data);
            case 852: return new IfcSurfaceStyleLighting(data);
            case 853: return new IfcSurfaceStyleRefraction(data);
            case 854: return new IfcSurfaceStyleRendering(data);
            case 855: return new IfcSurfaceStyleShading(data);
            case 856: return new IfcSurfaceStyleWithTextures(data);
            case 857: return new IfcSurfaceTexture(data);
            case 859: return new IfcSweptAreaSolid(data);
            case 860: return new IfcSweptDiskSolid(data);
            case 861: return new IfcSweptSurface(data);
            case 862: return new IfcSwitchingDeviceType(data);
            case 864: return new IfcSymbolStyle(data);
            case 866: return new IfcSystem(data);
            case 867: return new IfcSystemFurnitureElementType(data);
            case 868: return new IfcTShapeProfileDef(data);
            case 869: return new IfcTable(data);
            case 870: return new IfcTableRow(data);
            case 871: return new IfcTankType(data);
            case 873: return new IfcTask(data);
            case 874: return new IfcTelecomAddress(data);
            case 875: return new IfcTemperatureGradientMeasure(data);
            case 876: return new IfcTendon(data);
            case 877: return new IfcTendonAnchor(data);
            case 879: return new IfcTerminatorSymbol(data);
            case 880: return new IfcText(data);
            case 881: return new IfcTextAlignment(data);
            case 882: return new IfcTextDecoration(data);
            case 883: return new IfcTextFontName(data);
            case 885: return new IfcTextLiteral(data);
            case 886: return new IfcTextLiteralWithExtent(data);
            case 888: return new IfcTextStyle(data);
            case 889: return new IfcTextStyleFontModel(data);
            case 890: return new IfcTextStyleForDefinedFont(data);
            case 892: return new IfcTextStyleTextModel(data);
            case 893: return new IfcTextStyleWithBoxCharacteristics(data);
            case 894: return new IfcTextTransformation(data);
            case 895: return new IfcTextureCoordinate(data);
            case 896: return new IfcTextureCoordinateGenerator(data);
            case 897: return new IfcTextureMap(data);
            case 898: return new IfcTextureVertex(data);
            case 899: return new IfcThermalAdmittanceMeasure(data);
            case 900: return new IfcThermalConductivityMeasure(data);
            case 901: return new IfcThermalExpansionCoefficientMeasure(data);
            case 904: return new IfcThermalMaterialProperties(data);
            case 905: return new IfcThermalResistanceMeasure(data);
            case 906: return new IfcThermalTransmittanceMeasure(data);
            case 907: return new IfcThermodynamicTemperatureMeasure(data);
            case 908: return new IfcTimeMeasure(data);
            case 909: return new IfcTimeSeries(data);
            case 911: return new IfcTimeSeriesReferenceRelationship(data);
            case 912: return new IfcTimeSeriesSchedule(data);
            case 914: return new IfcTimeSeriesValue(data);
            case 915: return new IfcTimeStamp(data);
            case 916: return new IfcTopologicalRepresentationItem(data);
            case 917: return new IfcTopologyRepresentation(data);
            case 918: return new IfcTorqueMeasure(data);
            case 919: return new IfcTransformerType(data);
            case 922: return new IfcTransportElement(data);
            case 923: return new IfcTransportElementType(data);
            case 925: return new IfcTrapeziumProfileDef(data);
            case 926: return new IfcTrimmedCurve(data);
            case 929: return new IfcTubeBundleType(data);
            case 931: return new IfcTwoDirectionRepeatFactor(data);
            case 932: return new IfcTypeObject(data);
            case 933: return new IfcTypeProduct(data);
            case 934: return new IfcUShapeProfileDef(data);
            case 936: return new IfcUnitAssignment(data);
            case 938: return new IfcUnitaryEquipmentType(data);
            case 941: return new IfcValveType(data);
            case 943: return new IfcVaporPermeabilityMeasure(data);
            case 944: return new IfcVector(data);
            case 946: return new IfcVertex(data);
            case 947: return new IfcVertexBasedTextureMap(data);
            case 948: return new IfcVertexLoop(data);
            case 949: return new IfcVertexPoint(data);
            case 950: return new IfcVibrationIsolatorType(data);
            case 952: return new IfcVirtualElement(data);
            case 953: return new IfcVirtualGridIntersection(data);
            case 954: return new IfcVolumeMeasure(data);
            case 955: return new IfcVolumetricFlowRateMeasure(data);
            case 956: return new IfcWall(data);
            case 957: return new IfcWallStandardCase(data);
            case 958: return new IfcWallType(data);
            case 960: return new IfcWarpingConstantMeasure(data);
            case 961: return new IfcWarpingMomentMeasure(data);
            case 962: return new IfcWasteTerminalType(data);
            case 964: return new IfcWaterProperties(data);
            case 965: return new IfcWindow(data);
            case 966: return new IfcWindowLiningProperties(data);
            case 969: return new IfcWindowPanelProperties(data);
            case 970: return new IfcWindowStyle(data);
            case 973: return new IfcWorkControl(data);
            case 975: return new IfcWorkPlan(data);
            case 976: return new IfcWorkSchedule(data);
            case 977: return new IfcYearNumber(data);
            case 978: return new IfcZShapeProfileDef(data);
            case 979: return new IfcZone(data);
            default: throw IfcParse::IfcException(data->type()->name() + " cannot be instantiated");
        }

    }
};


#ifdef _MSC_VER
#pragma optimize("", off)
#endif
        
IfcParse::schema_definition* populate_schema() {
    IfcAbsorbedDoseMeasure_type = new type_declaration("IfcAbsorbedDoseMeasure", 1, new simple_type(simple_type::real_type));
    IfcAccelerationMeasure_type = new type_declaration("IfcAccelerationMeasure", 2, new simple_type(simple_type::real_type));
    IfcAmountOfSubstanceMeasure_type = new type_declaration("IfcAmountOfSubstanceMeasure", 22, new simple_type(simple_type::real_type));
    IfcAngularVelocityMeasure_type = new type_declaration("IfcAngularVelocityMeasure", 26, new simple_type(simple_type::real_type));
    IfcAreaMeasure_type = new type_declaration("IfcAreaMeasure", 47, new simple_type(simple_type::real_type));
    IfcBoolean_type = new type_declaration("IfcBoolean", 67, new simple_type(simple_type::boolean_type));
    IfcComplexNumber_type = new type_declaration("IfcComplexNumber", 131, new aggregation_type(aggregation_type::array_type, 1, 2, new simple_type(simple_type::real_type)));
    IfcCompoundPlaneAngleMeasure_type = new type_declaration("IfcCompoundPlaneAngleMeasure", 136, new aggregation_type(aggregation_type::list_type, 3, 4, new simple_type(simple_type::integer_type)));
    IfcContextDependentMeasure_type = new type_declaration("IfcContextDependentMeasure", 162, new simple_type(simple_type::real_type));
    IfcCountMeasure_type = new type_declaration("IfcCountMeasure", 177, new simple_type(simple_type::number_type));
    IfcCurvatureMeasure_type = new type_declaration("IfcCurvatureMeasure", 192, new simple_type(simple_type::real_type));
    IfcDayInMonthNumber_type = new type_declaration("IfcDayInMonthNumber", 207, new simple_type(simple_type::integer_type));
    IfcDaylightSavingHour_type = new type_declaration("IfcDaylightSavingHour", 208, new simple_type(simple_type::integer_type));
    IfcDescriptiveMeasure_type = new type_declaration("IfcDescriptiveMeasure", 216, new simple_type(simple_type::string_type));
    IfcDimensionCount_type = new type_declaration("IfcDimensionCount", 219, new simple_type(simple_type::integer_type));
    IfcDoseEquivalentMeasure_type = new type_declaration("IfcDoseEquivalentMeasure", 255, new simple_type(simple_type::real_type));
    IfcDynamicViscosityMeasure_type = new type_declaration("IfcDynamicViscosityMeasure", 268, new simple_type(simple_type::real_type));
    IfcElectricCapacitanceMeasure_type = new type_declaration("IfcElectricCapacitanceMeasure", 275, new simple_type(simple_type::real_type));
    IfcElectricChargeMeasure_type = new type_declaration("IfcElectricChargeMeasure", 276, new simple_type(simple_type::real_type));
    IfcElectricConductanceMeasure_type = new type_declaration("IfcElectricConductanceMeasure", 277, new simple_type(simple_type::real_type));
    IfcElectricCurrentMeasure_type = new type_declaration("IfcElectricCurrentMeasure", 279, new simple_type(simple_type::real_type));
    IfcElectricResistanceMeasure_type = new type_declaration("IfcElectricResistanceMeasure", 290, new simple_type(simple_type::real_type));
    IfcElectricVoltageMeasure_type = new type_declaration("IfcElectricVoltageMeasure", 293, new simple_type(simple_type::real_type));
    IfcEnergyMeasure_type = new type_declaration("IfcEnergyMeasure", 310, new simple_type(simple_type::real_type));
    IfcFontStyle_type = new type_declaration("IfcFontStyle", 373, new simple_type(simple_type::string_type));
    IfcFontVariant_type = new type_declaration("IfcFontVariant", 374, new simple_type(simple_type::string_type));
    IfcFontWeight_type = new type_declaration("IfcFontWeight", 375, new simple_type(simple_type::string_type));
    IfcForceMeasure_type = new type_declaration("IfcForceMeasure", 378, new simple_type(simple_type::real_type));
    IfcFrequencyMeasure_type = new type_declaration("IfcFrequencyMeasure", 379, new simple_type(simple_type::real_type));
    IfcGloballyUniqueId_type = new type_declaration("IfcGloballyUniqueId", 397, new simple_type(simple_type::string_type));
    IfcHeatFluxDensityMeasure_type = new type_declaration("IfcHeatFluxDensityMeasure", 406, new simple_type(simple_type::real_type));
    IfcHeatingValueMeasure_type = new type_declaration("IfcHeatingValueMeasure", 407, new simple_type(simple_type::real_type));
    IfcHourInDay_type = new type_declaration("IfcHourInDay", 408, new simple_type(simple_type::integer_type));
    IfcIdentifier_type = new type_declaration("IfcIdentifier", 413, new simple_type(simple_type::string_type));
    IfcIlluminanceMeasure_type = new type_declaration("IfcIlluminanceMeasure", 414, new simple_type(simple_type::real_type));
    IfcInductanceMeasure_type = new type_declaration("IfcInductanceMeasure", 416, new simple_type(simple_type::real_type));
    IfcInteger_type = new type_declaration("IfcInteger", 417, new simple_type(simple_type::integer_type));
    IfcIntegerCountRateMeasure_type = new type_declaration("IfcIntegerCountRateMeasure", 418, new simple_type(simple_type::integer_type));
    IfcIonConcentrationMeasure_type = new type_declaration("IfcIonConcentrationMeasure", 422, new simple_type(simple_type::real_type));
    IfcIsothermalMoistureCapacityMeasure_type = new type_declaration("IfcIsothermalMoistureCapacityMeasure", 425, new simple_type(simple_type::real_type));
    IfcKinematicViscosityMeasure_type = new type_declaration("IfcKinematicViscosityMeasure", 428, new simple_type(simple_type::real_type));
    IfcLabel_type = new type_declaration("IfcLabel", 430, new simple_type(simple_type::string_type));
    IfcLengthMeasure_type = new type_declaration("IfcLengthMeasure", 436, new simple_type(simple_type::real_type));
    IfcLinearForceMeasure_type = new type_declaration("IfcLinearForceMeasure", 455, new simple_type(simple_type::real_type));
    IfcLinearMomentMeasure_type = new type_declaration("IfcLinearMomentMeasure", 456, new simple_type(simple_type::real_type));
    IfcLinearStiffnessMeasure_type = new type_declaration("IfcLinearStiffnessMeasure", 457, new simple_type(simple_type::real_type));
    IfcLinearVelocityMeasure_type = new type_declaration("IfcLinearVelocityMeasure", 458, new simple_type(simple_type::real_type));
    IfcLogical_type = new type_declaration("IfcLogical", 462, new simple_type(simple_type::logical_type));
    IfcLuminousFluxMeasure_type = new type_declaration("IfcLuminousFluxMeasure", 465, new simple_type(simple_type::real_type));
    IfcLuminousIntensityDistributionMeasure_type = new type_declaration("IfcLuminousIntensityDistributionMeasure", 466, new simple_type(simple_type::real_type));
    IfcLuminousIntensityMeasure_type = new type_declaration("IfcLuminousIntensityMeasure", 467, new simple_type(simple_type::real_type));
    IfcMagneticFluxDensityMeasure_type = new type_declaration("IfcMagneticFluxDensityMeasure", 468, new simple_type(simple_type::real_type));
    IfcMagneticFluxMeasure_type = new type_declaration("IfcMagneticFluxMeasure", 469, new simple_type(simple_type::real_type));
    IfcMassDensityMeasure_type = new type_declaration("IfcMassDensityMeasure", 472, new simple_type(simple_type::real_type));
    IfcMassFlowRateMeasure_type = new type_declaration("IfcMassFlowRateMeasure", 473, new simple_type(simple_type::real_type));
    IfcMassMeasure_type = new type_declaration("IfcMassMeasure", 474, new simple_type(simple_type::real_type));
    IfcMassPerLengthMeasure_type = new type_declaration("IfcMassPerLengthMeasure", 475, new simple_type(simple_type::real_type));
    IfcMinuteInHour_type = new type_declaration("IfcMinuteInHour", 497, new simple_type(simple_type::integer_type));
    IfcModulusOfElasticityMeasure_type = new type_declaration("IfcModulusOfElasticityMeasure", 498, new simple_type(simple_type::real_type));
    IfcModulusOfLinearSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfLinearSubgradeReactionMeasure", 499, new simple_type(simple_type::real_type));
    IfcModulusOfRotationalSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfRotationalSubgradeReactionMeasure", 500, new simple_type(simple_type::real_type));
    IfcModulusOfSubgradeReactionMeasure_type = new type_declaration("IfcModulusOfSubgradeReactionMeasure", 501, new simple_type(simple_type::real_type));
    IfcMoistureDiffusivityMeasure_type = new type_declaration("IfcMoistureDiffusivityMeasure", 502, new simple_type(simple_type::real_type));
    IfcMolecularWeightMeasure_type = new type_declaration("IfcMolecularWeightMeasure", 503, new simple_type(simple_type::real_type));
    IfcMomentOfInertiaMeasure_type = new type_declaration("IfcMomentOfInertiaMeasure", 504, new simple_type(simple_type::real_type));
    IfcMonetaryMeasure_type = new type_declaration("IfcMonetaryMeasure", 505, new simple_type(simple_type::real_type));
    IfcMonthInYearNumber_type = new type_declaration("IfcMonthInYearNumber", 507, new simple_type(simple_type::integer_type));
    IfcNumericMeasure_type = new type_declaration("IfcNumericMeasure", 514, new simple_type(simple_type::number_type));
    IfcPHMeasure_type = new type_declaration("IfcPHMeasure", 538, new simple_type(simple_type::real_type));
    IfcParameterValue_type = new type_declaration("IfcParameterValue", 539, new simple_type(simple_type::real_type));
    IfcPlanarForceMeasure_type = new type_declaration("IfcPlanarForceMeasure", 563, new simple_type(simple_type::real_type));
    IfcPlaneAngleMeasure_type = new type_declaration("IfcPlaneAngleMeasure", 565, new simple_type(simple_type::real_type));
    IfcPositiveLengthMeasure_type = new type_declaration("IfcPositiveLengthMeasure", 577, new named_type(IfcLengthMeasure_type));
    IfcPositivePlaneAngleMeasure_type = new type_declaration("IfcPositivePlaneAngleMeasure", 578, new named_type(IfcPlaneAngleMeasure_type));
    IfcPowerMeasure_type = new type_declaration("IfcPowerMeasure", 581, new simple_type(simple_type::real_type));
    IfcPresentableText_type = new type_declaration("IfcPresentableText", 590, new simple_type(simple_type::string_type));
    IfcPressureMeasure_type = new type_declaration("IfcPressureMeasure", 596, new simple_type(simple_type::real_type));
    IfcRadioActivityMeasure_type = new type_declaration("IfcRadioActivityMeasure", 640, new simple_type(simple_type::real_type));
    IfcRatioMeasure_type = new type_declaration("IfcRatioMeasure", 650, new simple_type(simple_type::real_type));
    IfcReal_type = new type_declaration("IfcReal", 652, new simple_type(simple_type::real_type));
    IfcRotationalFrequencyMeasure_type = new type_declaration("IfcRotationalFrequencyMeasure", 733, new simple_type(simple_type::real_type));
    IfcRotationalMassMeasure_type = new type_declaration("IfcRotationalMassMeasure", 734, new simple_type(simple_type::real_type));
    IfcRotationalStiffnessMeasure_type = new type_declaration("IfcRotationalStiffnessMeasure", 735, new simple_type(simple_type::real_type));
    IfcSecondInMinute_type = new type_declaration("IfcSecondInMinute", 744, new simple_type(simple_type::real_type));
    IfcSectionModulusMeasure_type = new type_declaration("IfcSectionModulusMeasure", 745, new simple_type(simple_type::real_type));
    IfcSectionalAreaIntegralMeasure_type = new type_declaration("IfcSectionalAreaIntegralMeasure", 749, new simple_type(simple_type::real_type));
    IfcShearModulusMeasure_type = new type_declaration("IfcShearModulusMeasure", 761, new simple_type(simple_type::real_type));
    IfcSolidAngleMeasure_type = new type_declaration("IfcSolidAngleMeasure", 772, new simple_type(simple_type::real_type));
    IfcSoundPowerMeasure_type = new type_declaration("IfcSoundPowerMeasure", 774, new simple_type(simple_type::real_type));
    IfcSoundPressureMeasure_type = new type_declaration("IfcSoundPressureMeasure", 775, new simple_type(simple_type::real_type));
    IfcSpecificHeatCapacityMeasure_type = new type_declaration("IfcSpecificHeatCapacityMeasure", 788, new simple_type(simple_type::real_type));
    IfcSpecularExponent_type = new type_declaration("IfcSpecularExponent", 789, new simple_type(simple_type::real_type));
    IfcSpecularRoughness_type = new type_declaration("IfcSpecularRoughness", 791, new simple_type(simple_type::real_type));
    IfcTemperatureGradientMeasure_type = new type_declaration("IfcTemperatureGradientMeasure", 875, new simple_type(simple_type::real_type));
    IfcText_type = new type_declaration("IfcText", 880, new simple_type(simple_type::string_type));
    IfcTextAlignment_type = new type_declaration("IfcTextAlignment", 881, new simple_type(simple_type::string_type));
    IfcTextDecoration_type = new type_declaration("IfcTextDecoration", 882, new simple_type(simple_type::string_type));
    IfcTextFontName_type = new type_declaration("IfcTextFontName", 883, new simple_type(simple_type::string_type));
    IfcTextTransformation_type = new type_declaration("IfcTextTransformation", 894, new simple_type(simple_type::string_type));
    IfcThermalAdmittanceMeasure_type = new type_declaration("IfcThermalAdmittanceMeasure", 899, new simple_type(simple_type::real_type));
    IfcThermalConductivityMeasure_type = new type_declaration("IfcThermalConductivityMeasure", 900, new simple_type(simple_type::real_type));
    IfcThermalExpansionCoefficientMeasure_type = new type_declaration("IfcThermalExpansionCoefficientMeasure", 901, new simple_type(simple_type::real_type));
    IfcThermalResistanceMeasure_type = new type_declaration("IfcThermalResistanceMeasure", 905, new simple_type(simple_type::real_type));
    IfcThermalTransmittanceMeasure_type = new type_declaration("IfcThermalTransmittanceMeasure", 906, new simple_type(simple_type::real_type));
    IfcThermodynamicTemperatureMeasure_type = new type_declaration("IfcThermodynamicTemperatureMeasure", 907, new simple_type(simple_type::real_type));
    IfcTimeMeasure_type = new type_declaration("IfcTimeMeasure", 908, new simple_type(simple_type::real_type));
    IfcTimeStamp_type = new type_declaration("IfcTimeStamp", 915, new simple_type(simple_type::integer_type));
    IfcTorqueMeasure_type = new type_declaration("IfcTorqueMeasure", 918, new simple_type(simple_type::real_type));
    IfcVaporPermeabilityMeasure_type = new type_declaration("IfcVaporPermeabilityMeasure", 943, new simple_type(simple_type::real_type));
    IfcVolumeMeasure_type = new type_declaration("IfcVolumeMeasure", 954, new simple_type(simple_type::real_type));
    IfcVolumetricFlowRateMeasure_type = new type_declaration("IfcVolumetricFlowRateMeasure", 955, new simple_type(simple_type::real_type));
    IfcWarpingConstantMeasure_type = new type_declaration("IfcWarpingConstantMeasure", 960, new simple_type(simple_type::real_type));
    IfcWarpingMomentMeasure_type = new type_declaration("IfcWarpingMomentMeasure", 961, new simple_type(simple_type::real_type));
    IfcYearNumber_type = new type_declaration("IfcYearNumber", 977, new simple_type(simple_type::integer_type));
    IfcBoxAlignment_type = new type_declaration("IfcBoxAlignment", 80, new named_type(IfcLabel_type));
    IfcNormalisedRatioMeasure_type = new type_declaration("IfcNormalisedRatioMeasure", 512, new named_type(IfcRatioMeasure_type));
    IfcPositiveRatioMeasure_type = new type_declaration("IfcPositiveRatioMeasure", 579, new named_type(IfcRatioMeasure_type));
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
        IfcActionSourceTypeEnum_type = new enumeration_type("IfcActionSourceTypeEnum", 4, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("EXTRAORDINARY_A");
        items.push_back("NOTDEFINED");
        items.push_back("PERMANENT_G");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLE_Q");
        IfcActionTypeEnum_type = new enumeration_type("IfcActionTypeEnum", 5, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("ELECTRICACTUATOR");
        items.push_back("HANDOPERATEDACTUATOR");
        items.push_back("HYDRAULICACTUATOR");
        items.push_back("NOTDEFINED");
        items.push_back("PNEUMATICACTUATOR");
        items.push_back("THERMOSTATICACTUATOR");
        items.push_back("USERDEFINED");
        IfcActuatorTypeEnum_type = new enumeration_type("IfcActuatorTypeEnum", 10, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DISTRIBUTIONPOINT");
        items.push_back("HOME");
        items.push_back("OFFICE");
        items.push_back("SITE");
        items.push_back("USERDEFINED");
        IfcAddressTypeEnum_type = new enumeration_type("IfcAddressTypeEnum", 12, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AHEAD");
        items.push_back("BEHIND");
        IfcAheadOrBehind_type = new enumeration_type("IfcAheadOrBehind", 13, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CONSTANTFLOW");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VARIABLEFLOWPRESSUREDEPENDANT");
        items.push_back("VARIABLEFLOWPRESSUREINDEPENDANT");
        IfcAirTerminalBoxTypeEnum_type = new enumeration_type("IfcAirTerminalBoxTypeEnum", 15, items);
    }
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
        IfcAirTerminalTypeEnum_type = new enumeration_type("IfcAirTerminalTypeEnum", 17, items);
    }
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
        IfcAirToAirHeatRecoveryTypeEnum_type = new enumeration_type("IfcAirToAirHeatRecoveryTypeEnum", 19, items);
    }
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
        IfcAlarmTypeEnum_type = new enumeration_type("IfcAlarmTypeEnum", 21, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("IN_PLANE_LOADING_2D");
        items.push_back("LOADING_3D");
        items.push_back("NOTDEFINED");
        items.push_back("OUT_PLANE_LOADING_2D");
        items.push_back("USERDEFINED");
        IfcAnalysisModelTypeEnum_type = new enumeration_type("IfcAnalysisModelTypeEnum", 23, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FIRST_ORDER_THEORY");
        items.push_back("FULL_NONLINEAR_THEORY");
        items.push_back("NOTDEFINED");
        items.push_back("SECOND_ORDER_THEORY");
        items.push_back("THIRD_ORDER_THEORY");
        items.push_back("USERDEFINED");
        IfcAnalysisTheoryTypeEnum_type = new enumeration_type("IfcAnalysisTheoryTypeEnum", 24, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ADD");
        items.push_back("DIVIDE");
        items.push_back("MULTIPLY");
        items.push_back("SUBTRACT");
        IfcArithmeticOperatorEnum_type = new enumeration_type("IfcArithmeticOperatorEnum", 48, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FACTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SITE");
        IfcAssemblyPlaceEnum_type = new enumeration_type("IfcAssemblyPlaceEnum", 49, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CIRCULAR_ARC");
        items.push_back("ELLIPTIC_ARC");
        items.push_back("HYPERBOLIC_ARC");
        items.push_back("PARABOLIC_ARC");
        items.push_back("POLYLINE_FORM");
        items.push_back("UNSPECIFIED");
        IfcBSplineCurveForm_type = new enumeration_type("IfcBSplineCurveForm", 57, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEAM");
        items.push_back("JOIST");
        items.push_back("LINTEL");
        items.push_back("NOTDEFINED");
        items.push_back("T_BEAM");
        items.push_back("USERDEFINED");
        IfcBeamTypeEnum_type = new enumeration_type("IfcBeamTypeEnum", 60, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EQUALTO");
        items.push_back("GREATERTHAN");
        items.push_back("GREATERTHANOREQUALTO");
        items.push_back("LESSTHAN");
        items.push_back("LESSTHANOREQUALTO");
        items.push_back("NOTEQUALTO");
        IfcBenchmarkEnum_type = new enumeration_type("IfcBenchmarkEnum", 61, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("STEAM");
        items.push_back("USERDEFINED");
        items.push_back("WATER");
        IfcBoilerTypeEnum_type = new enumeration_type("IfcBoilerTypeEnum", 66, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("DIFFERENCE");
        items.push_back("INTERSECTION");
        items.push_back("UNION");
        IfcBooleanOperator_type = new enumeration_type("IfcBooleanOperator", 70, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcBuildingElementProxyTypeEnum_type = new enumeration_type("IfcBuildingElementProxyTypeEnum", 88, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BEND");
        items.push_back("CROSS");
        items.push_back("NOTDEFINED");
        items.push_back("REDUCER");
        items.push_back("TEE");
        items.push_back("USERDEFINED");
        IfcCableCarrierFittingTypeEnum_type = new enumeration_type("IfcCableCarrierFittingTypeEnum", 93, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CABLELADDERSEGMENT");
        items.push_back("CABLETRAYSEGMENT");
        items.push_back("CABLETRUNKINGSEGMENT");
        items.push_back("CONDUITSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCableCarrierSegmentTypeEnum_type = new enumeration_type("IfcCableCarrierSegmentTypeEnum", 95, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CABLESEGMENT");
        items.push_back("CONDUCTORSEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCableSegmentTypeEnum_type = new enumeration_type("IfcCableSegmentTypeEnum", 97, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ADDED");
        items.push_back("DELETED");
        items.push_back("MODIFIED");
        items.push_back("MODIFIEDADDED");
        items.push_back("MODIFIEDDELETED");
        items.push_back("NOCHANGE");
        IfcChangeActionEnum_type = new enumeration_type("IfcChangeActionEnum", 107, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AIRCOOLED");
        items.push_back("HEATRECOVERY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WATERCOOLED");
        IfcChillerTypeEnum_type = new enumeration_type("IfcChillerTypeEnum", 110, items);
    }
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
        IfcCoilTypeEnum_type = new enumeration_type("IfcCoilTypeEnum", 123, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COLUMN");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcColumnTypeEnum_type = new enumeration_type("IfcColumnTypeEnum", 130, items);
    }
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
        IfcCompressorTypeEnum_type = new enumeration_type("IfcCompressorTypeEnum", 138, items);
    }
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
        IfcCondenserTypeEnum_type = new enumeration_type("IfcCondenserTypeEnum", 140, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ATEND");
        items.push_back("ATPATH");
        items.push_back("ATSTART");
        items.push_back("NOTDEFINED");
        IfcConnectionTypeEnum_type = new enumeration_type("IfcConnectionTypeEnum", 152, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ADVISORY");
        items.push_back("HARD");
        items.push_back("NOTDEFINED");
        items.push_back("SOFT");
        items.push_back("USERDEFINED");
        IfcConstraintEnum_type = new enumeration_type("IfcConstraintEnum", 156, items);
    }
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
        IfcControllerTypeEnum_type = new enumeration_type("IfcControllerTypeEnum", 166, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("ACTIVE");
        items.push_back("NOTDEFINED");
        items.push_back("PASSIVE");
        items.push_back("USERDEFINED");
        IfcCooledBeamTypeEnum_type = new enumeration_type("IfcCooledBeamTypeEnum", 169, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MECHANICALFORCEDDRAFT");
        items.push_back("MECHANICALINDUCEDDRAFT");
        items.push_back("NATURALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCoolingTowerTypeEnum_type = new enumeration_type("IfcCoolingTowerTypeEnum", 171, items);
    }
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
        IfcCostScheduleTypeEnum_type = new enumeration_type("IfcCostScheduleTypeEnum", 175, items);
    }
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
        IfcCoveringTypeEnum_type = new enumeration_type("IfcCoveringTypeEnum", 180, items);
    }
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
        IfcCurrencyEnum_type = new enumeration_type("IfcCurrencyEnum", 187, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcCurtainWallTypeEnum_type = new enumeration_type("IfcCurtainWallTypeEnum", 191, items);
    }
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
        IfcDamperTypeEnum_type = new enumeration_type("IfcDamperTypeEnum", 203, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("MEASURED");
        items.push_back("NOTDEFINED");
        items.push_back("PREDICTED");
        items.push_back("SIMULATED");
        items.push_back("USERDEFINED");
        IfcDataOriginEnum_type = new enumeration_type("IfcDataOriginEnum", 204, items);
    }
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
        IfcDerivedUnitEnum_type = new enumeration_type("IfcDerivedUnitEnum", 215, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("ORIGIN");
        items.push_back("TARGET");
        IfcDimensionExtentUsage_type = new enumeration_type("IfcDimensionExtentUsage", 223, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IfcDirectionSenseEnum_type = new enumeration_type("IfcDirectionSenseEnum", 227, items);
    }
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
        IfcDistributionChamberElementTypeEnum_type = new enumeration_type("IfcDistributionChamberElementTypeEnum", 232, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CONFIDENTIAL");
        items.push_back("NOTDEFINED");
        items.push_back("PERSONAL");
        items.push_back("PUBLIC");
        items.push_back("RESTRICTED");
        items.push_back("USERDEFINED");
        IfcDocumentConfidentialityEnum_type = new enumeration_type("IfcDocumentConfidentialityEnum", 240, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("DRAFT");
        items.push_back("FINAL");
        items.push_back("FINALDRAFT");
        items.push_back("NOTDEFINED");
        items.push_back("REVISION");
        IfcDocumentStatusEnum_type = new enumeration_type("IfcDocumentStatusEnum", 246, items);
    }
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
        IfcDoorPanelOperationEnum_type = new enumeration_type("IfcDoorPanelOperationEnum", 249, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        IfcDoorPanelPositionEnum_type = new enumeration_type("IfcDoorPanelPositionEnum", 250, items);
    }
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
        IfcDoorStyleConstructionEnum_type = new enumeration_type("IfcDoorStyleConstructionEnum", 253, items);
    }
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
        IfcDoorStyleOperationEnum_type = new enumeration_type("IfcDoorStyleOperationEnum", 254, items);
    }
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
        IfcDuctFittingTypeEnum_type = new enumeration_type("IfcDuctFittingTypeEnum", 263, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("USERDEFINED");
        IfcDuctSegmentTypeEnum_type = new enumeration_type("IfcDuctSegmentTypeEnum", 265, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FLATOVAL");
        items.push_back("NOTDEFINED");
        items.push_back("RECTANGULAR");
        items.push_back("ROUND");
        items.push_back("USERDEFINED");
        IfcDuctSilencerTypeEnum_type = new enumeration_type("IfcDuctSilencerTypeEnum", 267, items);
    }
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
        IfcElectricApplianceTypeEnum_type = new enumeration_type("IfcElectricApplianceTypeEnum", 274, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("ALTERNATING");
        items.push_back("DIRECT");
        items.push_back("NOTDEFINED");
        IfcElectricCurrentEnum_type = new enumeration_type("IfcElectricCurrentEnum", 278, items);
    }
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
        IfcElectricDistributionPointFunctionEnum_type = new enumeration_type("IfcElectricDistributionPointFunctionEnum", 281, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("BATTERY");
        items.push_back("CAPACITORBANK");
        items.push_back("HARMONICFILTER");
        items.push_back("INDUCTORBANK");
        items.push_back("NOTDEFINED");
        items.push_back("UPS");
        items.push_back("USERDEFINED");
        IfcElectricFlowStorageDeviceTypeEnum_type = new enumeration_type("IfcElectricFlowStorageDeviceTypeEnum", 283, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcElectricGeneratorTypeEnum_type = new enumeration_type("IfcElectricGeneratorTypeEnum", 285, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELECTRICCABLEHEATER");
        items.push_back("ELECTRICMATHEATER");
        items.push_back("ELECTRICPOINTHEATER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcElectricHeaterTypeEnum_type = new enumeration_type("IfcElectricHeaterTypeEnum", 287, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DC");
        items.push_back("INDUCTION");
        items.push_back("NOTDEFINED");
        items.push_back("POLYPHASE");
        items.push_back("RELUCTANCESYNCHRONOUS");
        items.push_back("SYNCHRONOUS");
        items.push_back("USERDEFINED");
        IfcElectricMotorTypeEnum_type = new enumeration_type("IfcElectricMotorTypeEnum", 289, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("NOTDEFINED");
        items.push_back("RELAY");
        items.push_back("TIMECLOCK");
        items.push_back("TIMEDELAY");
        items.push_back("USERDEFINED");
        IfcElectricTimeControlTypeEnum_type = new enumeration_type("IfcElectricTimeControlTypeEnum", 292, items);
    }
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
        IfcElementAssemblyTypeEnum_type = new enumeration_type("IfcElementAssemblyTypeEnum", 299, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("COMPLEX");
        items.push_back("ELEMENT");
        items.push_back("PARTIAL");
        IfcElementCompositionEnum_type = new enumeration_type("IfcElementCompositionEnum", 302, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AUXILIARY");
        items.push_back("NOTDEFINED");
        items.push_back("PRIMARY");
        items.push_back("SECONDARY");
        items.push_back("TERTIARY");
        items.push_back("USERDEFINED");
        IfcEnergySequenceEnum_type = new enumeration_type("IfcEnergySequenceEnum", 312, items);
    }
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
        IfcEnvironmentalImpactCategoryEnum_type = new enumeration_type("IfcEnvironmentalImpactCategoryEnum", 313, items);
    }
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
        IfcEvaporativeCoolerTypeEnum_type = new enumeration_type("IfcEvaporativeCoolerTypeEnum", 318, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DIRECTEXPANSIONBRAZEDPLATE");
        items.push_back("DIRECTEXPANSIONSHELLANDTUBE");
        items.push_back("DIRECTEXPANSIONTUBEINTUBE");
        items.push_back("FLOODEDSHELLANDTUBE");
        items.push_back("NOTDEFINED");
        items.push_back("SHELLANDCOIL");
        items.push_back("USERDEFINED");
        IfcEvaporatorTypeEnum_type = new enumeration_type("IfcEvaporatorTypeEnum", 320, items);
    }
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
        IfcFanTypeEnum_type = new enumeration_type("IfcFanTypeEnum", 337, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("AIRPARTICLEFILTER");
        items.push_back("NOTDEFINED");
        items.push_back("ODORFILTER");
        items.push_back("OILFILTER");
        items.push_back("STRAINER");
        items.push_back("USERDEFINED");
        items.push_back("WATERFILTER");
        IfcFilterTypeEnum_type = new enumeration_type("IfcFilterTypeEnum", 350, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("BREECHINGINLET");
        items.push_back("FIREHYDRANT");
        items.push_back("HOSEREEL");
        items.push_back("NOTDEFINED");
        items.push_back("SPRINKLER");
        items.push_back("SPRINKLERDEFLECTOR");
        items.push_back("USERDEFINED");
        IfcFireSuppressionTerminalTypeEnum_type = new enumeration_type("IfcFireSuppressionTerminalTypeEnum", 352, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SINK");
        items.push_back("SOURCE");
        items.push_back("SOURCEANDSINK");
        IfcFlowDirectionEnum_type = new enumeration_type("IfcFlowDirectionEnum", 355, items);
    }
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
        IfcFlowInstrumentTypeEnum_type = new enumeration_type("IfcFlowInstrumentTypeEnum", 359, items);
    }
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
        IfcFlowMeterTypeEnum_type = new enumeration_type("IfcFlowMeterTypeEnum", 361, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FOOTING_BEAM");
        items.push_back("NOTDEFINED");
        items.push_back("PAD_FOOTING");
        items.push_back("PILE_CAP");
        items.push_back("STRIP_FOOTING");
        items.push_back("USERDEFINED");
        IfcFootingTypeEnum_type = new enumeration_type("IfcFootingTypeEnum", 377, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GASAPPLIANCE");
        items.push_back("GASBOOSTER");
        items.push_back("GASBURNER");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcGasTerminalTypeEnum_type = new enumeration_type("IfcGasTerminalTypeEnum", 386, items);
    }
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
        IfcGeometricProjectionEnum_type = new enumeration_type("IfcGeometricProjectionEnum", 390, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("GLOBAL_COORDS");
        items.push_back("LOCAL_COORDS");
        IfcGlobalOrLocalEnum_type = new enumeration_type("IfcGlobalOrLocalEnum", 396, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("PLATE");
        items.push_back("SHELLANDTUBE");
        items.push_back("USERDEFINED");
        IfcHeatExchangerTypeEnum_type = new enumeration_type("IfcHeatExchangerTypeEnum", 405, items);
    }
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
        IfcHumidifierTypeEnum_type = new enumeration_type("IfcHumidifierTypeEnum", 410, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("EXTERNAL");
        items.push_back("INTERNAL");
        items.push_back("NOTDEFINED");
        IfcInternalOrExternalEnum_type = new enumeration_type("IfcInternalOrExternalEnum", 419, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ASSETINVENTORY");
        items.push_back("FURNITUREINVENTORY");
        items.push_back("NOTDEFINED");
        items.push_back("SPACEINVENTORY");
        items.push_back("USERDEFINED");
        IfcInventoryTypeEnum_type = new enumeration_type("IfcInventoryTypeEnum", 421, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcJunctionBoxTypeEnum_type = new enumeration_type("IfcJunctionBoxTypeEnum", 427, items);
    }
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
        IfcLampTypeEnum_type = new enumeration_type("IfcLampTypeEnum", 433, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("AXIS1");
        items.push_back("AXIS2");
        items.push_back("AXIS3");
        IfcLayerSetDirectionEnum_type = new enumeration_type("IfcLayerSetDirectionEnum", 434, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("TYPE_A");
        items.push_back("TYPE_B");
        items.push_back("TYPE_C");
        IfcLightDistributionCurveEnum_type = new enumeration_type("IfcLightDistributionCurveEnum", 440, items);
    }
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
        IfcLightEmissionSourceEnum_type = new enumeration_type("IfcLightEmissionSourceEnum", 443, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DIRECTIONSOURCE");
        items.push_back("NOTDEFINED");
        items.push_back("POINTSOURCE");
        items.push_back("USERDEFINED");
        IfcLightFixtureTypeEnum_type = new enumeration_type("IfcLightFixtureTypeEnum", 445, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("LOAD_CASE");
        items.push_back("LOAD_COMBINATION");
        items.push_back("LOAD_COMBINATION_GROUP");
        items.push_back("LOAD_GROUP");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcLoadGroupTypeEnum_type = new enumeration_type("IfcLoadGroupTypeEnum", 459, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("LOGICALAND");
        items.push_back("LOGICALOR");
        IfcLogicalOperatorEnum_type = new enumeration_type("IfcLogicalOperatorEnum", 463, items);
    }
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
        IfcMemberTypeEnum_type = new enumeration_type("IfcMemberTypeEnum", 494, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BELTDRIVE");
        items.push_back("COUPLING");
        items.push_back("DIRECTDRIVE");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcMotorConnectionTypeEnum_type = new enumeration_type("IfcMotorConnectionTypeEnum", 509, items);
    }
    {
        std::vector<std::string> items; items.reserve(1);
        items.push_back("NULL");
        IfcNullStyle_type = new enumeration_type("IfcNullStyle", 513, items);
    }
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
        IfcObjectTypeEnum_type = new enumeration_type("IfcObjectTypeEnum", 519, items);
    }
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
        IfcObjectiveEnum_type = new enumeration_type("IfcObjectiveEnum", 521, items);
    }
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
        IfcOccupantTypeEnum_type = new enumeration_type("IfcOccupantTypeEnum", 523, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("AUDIOVISUALOUTLET");
        items.push_back("COMMUNICATIONSOUTLET");
        items.push_back("NOTDEFINED");
        items.push_back("POWEROUTLET");
        items.push_back("USERDEFINED");
        IfcOutletTypeEnum_type = new enumeration_type("IfcOutletTypeEnum", 536, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("GRILL");
        items.push_back("LOUVER");
        items.push_back("NOTDEFINED");
        items.push_back("SCREEN");
        items.push_back("USERDEFINED");
        IfcPermeableCoveringOperationEnum_type = new enumeration_type("IfcPermeableCoveringOperationEnum", 543, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("NOTDEFINED");
        items.push_back("PHYSICAL");
        items.push_back("VIRTUAL");
        IfcPhysicalOrVirtualEnum_type = new enumeration_type("IfcPhysicalOrVirtualEnum", 549, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("CAST_IN_PLACE");
        items.push_back("COMPOSITE");
        items.push_back("NOTDEFINED");
        items.push_back("PRECAST_CONCRETE");
        items.push_back("PREFAB_STEEL");
        items.push_back("USERDEFINED");
        IfcPileConstructionEnum_type = new enumeration_type("IfcPileConstructionEnum", 553, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("COHESION");
        items.push_back("FRICTION");
        items.push_back("NOTDEFINED");
        items.push_back("SUPPORT");
        items.push_back("USERDEFINED");
        IfcPileTypeEnum_type = new enumeration_type("IfcPileTypeEnum", 554, items);
    }
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
        IfcPipeFittingTypeEnum_type = new enumeration_type("IfcPipeFittingTypeEnum", 556, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("FLEXIBLESEGMENT");
        items.push_back("GUTTER");
        items.push_back("NOTDEFINED");
        items.push_back("RIGIDSEGMENT");
        items.push_back("SPOOL");
        items.push_back("USERDEFINED");
        IfcPipeSegmentTypeEnum_type = new enumeration_type("IfcPipeSegmentTypeEnum", 558, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CURTAIN_PANEL");
        items.push_back("NOTDEFINED");
        items.push_back("SHEET");
        items.push_back("USERDEFINED");
        IfcPlateTypeEnum_type = new enumeration_type("IfcPlateTypeEnum", 568, items);
    }
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
        IfcProcedureTypeEnum_type = new enumeration_type("IfcProcedureTypeEnum", 598, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("AREA");
        items.push_back("CURVE");
        IfcProfileTypeEnum_type = new enumeration_type("IfcProfileTypeEnum", 606, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CHANGE");
        items.push_back("MAINTENANCE");
        items.push_back("MOVE");
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASE");
        items.push_back("USERDEFINED");
        items.push_back("WORK");
        IfcProjectOrderRecordTypeEnum_type = new enumeration_type("IfcProjectOrderRecordTypeEnum", 610, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CHANGEORDER");
        items.push_back("MAINTENANCEWORKORDER");
        items.push_back("MOVEORDER");
        items.push_back("NOTDEFINED");
        items.push_back("PURCHASEORDER");
        items.push_back("USERDEFINED");
        items.push_back("WORKORDER");
        IfcProjectOrderTypeEnum_type = new enumeration_type("IfcProjectOrderTypeEnum", 611, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PROJECTED_LENGTH");
        items.push_back("TRUE_LENGTH");
        IfcProjectedOrTrueLengthEnum_type = new enumeration_type("IfcProjectedOrTrueLengthEnum", 612, items);
    }
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
        IfcPropertySourceEnum_type = new enumeration_type("IfcPropertySourceEnum", 627, items);
    }
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
        IfcProtectiveDeviceTypeEnum_type = new enumeration_type("IfcProtectiveDeviceTypeEnum", 630, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CIRCULATOR");
        items.push_back("ENDSUCTION");
        items.push_back("NOTDEFINED");
        items.push_back("SPLITCASE");
        items.push_back("USERDEFINED");
        items.push_back("VERTICALINLINE");
        items.push_back("VERTICALTURBINE");
        IfcPumpTypeEnum_type = new enumeration_type("IfcPumpTypeEnum", 633, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BALUSTRADE");
        items.push_back("GUARDRAIL");
        items.push_back("HANDRAIL");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcRailingTypeEnum_type = new enumeration_type("IfcRailingTypeEnum", 644, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        IfcRampFlightTypeEnum_type = new enumeration_type("IfcRampFlightTypeEnum", 648, items);
    }
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
        IfcRampTypeEnum_type = new enumeration_type("IfcRampTypeEnum", 649, items);
    }
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
        IfcReflectanceMethodEnum_type = new enumeration_type("IfcReflectanceMethodEnum", 658, items);
    }
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
        IfcReinforcingBarRoleEnum_type = new enumeration_type("IfcReinforcingBarRoleEnum", 663, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("PLAIN");
        items.push_back("TEXTURED");
        IfcReinforcingBarSurfaceEnum_type = new enumeration_type("IfcReinforcingBarSurfaceEnum", 664, items);
    }
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
        IfcResourceConsumptionEnum_type = new enumeration_type("IfcResourceConsumptionEnum", 723, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("DIRECTION_X");
        items.push_back("DIRECTION_Y");
        IfcRibPlateDirectionEnum_type = new enumeration_type("IfcRibPlateDirectionEnum", 725, items);
    }
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
        IfcRoleEnum_type = new enumeration_type("IfcRoleEnum", 729, items);
    }
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
        IfcRoofTypeEnum_type = new enumeration_type("IfcRoofTypeEnum", 731, items);
    }
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
        IfcSIPrefix_type = new enumeration_type("IfcSIPrefix", 738, items);
    }
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
        IfcSIUnitName_type = new enumeration_type("IfcSIUnitName", 740, items);
    }
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
        IfcSanitaryTerminalTypeEnum_type = new enumeration_type("IfcSanitaryTerminalTypeEnum", 742, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("TAPERED");
        items.push_back("UNIFORM");
        IfcSectionTypeEnum_type = new enumeration_type("IfcSectionTypeEnum", 748, items);
    }
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
        IfcSensorTypeEnum_type = new enumeration_type("IfcSensorTypeEnum", 752, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("FINISH_FINISH");
        items.push_back("FINISH_START");
        items.push_back("NOTDEFINED");
        items.push_back("START_FINISH");
        items.push_back("START_START");
        IfcSequenceEnum_type = new enumeration_type("IfcSequenceEnum", 753, items);
    }
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
        IfcServiceLifeFactorTypeEnum_type = new enumeration_type("IfcServiceLifeFactorTypeEnum", 756, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUALSERVICELIFE");
        items.push_back("EXPECTEDSERVICELIFE");
        items.push_back("OPTIMISTICREFERENCESERVICELIFE");
        items.push_back("PESSIMISTICREFERENCESERVICELIFE");
        items.push_back("REFERENCESERVICELIFE");
        IfcServiceLifeTypeEnum_type = new enumeration_type("IfcServiceLifeTypeEnum", 757, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BASESLAB");
        items.push_back("FLOOR");
        items.push_back("LANDING");
        items.push_back("NOTDEFINED");
        items.push_back("ROOF");
        items.push_back("USERDEFINED");
        IfcSlabTypeEnum_type = new enumeration_type("IfcSlabTypeEnum", 770, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("DBA");
        items.push_back("DBB");
        items.push_back("DBC");
        items.push_back("NC");
        items.push_back("NOTDEFINED");
        items.push_back("NR");
        items.push_back("USERDEFINED");
        IfcSoundScaleEnum_type = new enumeration_type("IfcSoundScaleEnum", 777, items);
    }
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
        IfcSpaceHeaterTypeEnum_type = new enumeration_type("IfcSpaceHeaterTypeEnum", 781, items);
    }
    {
        std::vector<std::string> items; items.reserve(2);
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcSpaceTypeEnum_type = new enumeration_type("IfcSpaceTypeEnum", 785, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BIRDCAGE");
        items.push_back("COWL");
        items.push_back("NOTDEFINED");
        items.push_back("RAINWATERHOPPER");
        items.push_back("USERDEFINED");
        IfcStackTerminalTypeEnum_type = new enumeration_type("IfcStackTerminalTypeEnum", 794, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CURVED");
        items.push_back("FREEFORM");
        items.push_back("NOTDEFINED");
        items.push_back("SPIRAL");
        items.push_back("STRAIGHT");
        items.push_back("USERDEFINED");
        items.push_back("WINDER");
        IfcStairFlightTypeEnum_type = new enumeration_type("IfcStairFlightTypeEnum", 798, items);
    }
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
        IfcStairTypeEnum_type = new enumeration_type("IfcStairTypeEnum", 799, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("LOCKED");
        items.push_back("READONLY");
        items.push_back("READONLYLOCKED");
        items.push_back("READWRITE");
        items.push_back("READWRITELOCKED");
        IfcStateEnum_type = new enumeration_type("IfcStateEnum", 800, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CABLE");
        items.push_back("COMPRESSION_MEMBER");
        items.push_back("NOTDEFINED");
        items.push_back("PIN_JOINED_MEMBER");
        items.push_back("RIGID_JOINED_MEMBER");
        items.push_back("TENSION_MEMBER");
        items.push_back("USERDEFINED");
        IfcStructuralCurveTypeEnum_type = new enumeration_type("IfcStructuralCurveTypeEnum", 810, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("BENDING_ELEMENT");
        items.push_back("MEMBRANE_ELEMENT");
        items.push_back("NOTDEFINED");
        items.push_back("SHELL");
        items.push_back("USERDEFINED");
        IfcStructuralSurfaceTypeEnum_type = new enumeration_type("IfcStructuralSurfaceTypeEnum", 837, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("BOTH");
        items.push_back("NEGATIVE");
        items.push_back("POSITIVE");
        IfcSurfaceSide_type = new enumeration_type("IfcSurfaceSide", 849, items);
    }
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
        IfcSurfaceTextureEnum_type = new enumeration_type("IfcSurfaceTextureEnum", 858, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CONTACTOR");
        items.push_back("EMERGENCYSTOP");
        items.push_back("NOTDEFINED");
        items.push_back("STARTER");
        items.push_back("SWITCHDISCONNECTOR");
        items.push_back("TOGGLESWITCH");
        items.push_back("USERDEFINED");
        IfcSwitchingDeviceTypeEnum_type = new enumeration_type("IfcSwitchingDeviceTypeEnum", 863, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("EXPANSION");
        items.push_back("NOTDEFINED");
        items.push_back("PREFORMED");
        items.push_back("PRESSUREVESSEL");
        items.push_back("SECTIONAL");
        items.push_back("USERDEFINED");
        IfcTankTypeEnum_type = new enumeration_type("IfcTankTypeEnum", 872, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BAR");
        items.push_back("COATED");
        items.push_back("NOTDEFINED");
        items.push_back("STRAND");
        items.push_back("USERDEFINED");
        items.push_back("WIRE");
        IfcTendonTypeEnum_type = new enumeration_type("IfcTendonTypeEnum", 878, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("DOWN");
        items.push_back("LEFT");
        items.push_back("RIGHT");
        items.push_back("UP");
        IfcTextPath_type = new enumeration_type("IfcTextPath", 887, items);
    }
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
        IfcThermalLoadSourceEnum_type = new enumeration_type("IfcThermalLoadSourceEnum", 902, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("LATENT");
        items.push_back("NOTDEFINED");
        items.push_back("RADIANT");
        items.push_back("SENSIBLE");
        IfcThermalLoadTypeEnum_type = new enumeration_type("IfcThermalLoadTypeEnum", 903, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("CONTINUOUS");
        items.push_back("DISCRETE");
        items.push_back("DISCRETEBINARY");
        items.push_back("NOTDEFINED");
        items.push_back("PIECEWISEBINARY");
        items.push_back("PIECEWISECONSTANT");
        items.push_back("PIECEWISECONTINUOUS");
        IfcTimeSeriesDataTypeEnum_type = new enumeration_type("IfcTimeSeriesDataTypeEnum", 910, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("ANNUAL");
        items.push_back("DAILY");
        items.push_back("MONTHLY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("WEEKLY");
        IfcTimeSeriesScheduleTypeEnum_type = new enumeration_type("IfcTimeSeriesScheduleTypeEnum", 913, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("CURRENT");
        items.push_back("FREQUENCY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        items.push_back("VOLTAGE");
        IfcTransformerTypeEnum_type = new enumeration_type("IfcTransformerTypeEnum", 920, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("CONTINUOUS");
        items.push_back("CONTSAMEGRADIENT");
        items.push_back("CONTSAMEGRADIENTSAMECURVATURE");
        items.push_back("DISCONTINUOUS");
        IfcTransitionCode_type = new enumeration_type("IfcTransitionCode", 921, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ELEVATOR");
        items.push_back("ESCALATOR");
        items.push_back("MOVINGWALKWAY");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcTransportElementTypeEnum_type = new enumeration_type("IfcTransportElementTypeEnum", 924, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("CARTESIAN");
        items.push_back("PARAMETER");
        items.push_back("UNSPECIFIED");
        IfcTrimmingPreference_type = new enumeration_type("IfcTrimmingPreference", 927, items);
    }
    {
        std::vector<std::string> items; items.reserve(3);
        items.push_back("FINNED");
        items.push_back("NOTDEFINED");
        items.push_back("USERDEFINED");
        IfcTubeBundleTypeEnum_type = new enumeration_type("IfcTubeBundleTypeEnum", 930, items);
    }
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
        IfcUnitEnum_type = new enumeration_type("IfcUnitEnum", 937, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("AIRCONDITIONINGUNIT");
        items.push_back("AIRHANDLER");
        items.push_back("NOTDEFINED");
        items.push_back("ROOFTOPUNIT");
        items.push_back("SPLITSYSTEM");
        items.push_back("USERDEFINED");
        IfcUnitaryEquipmentTypeEnum_type = new enumeration_type("IfcUnitaryEquipmentTypeEnum", 939, items);
    }
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
        IfcValveTypeEnum_type = new enumeration_type("IfcValveTypeEnum", 942, items);
    }
    {
        std::vector<std::string> items; items.reserve(4);
        items.push_back("COMPRESSION");
        items.push_back("NOTDEFINED");
        items.push_back("SPRING");
        items.push_back("USERDEFINED");
        IfcVibrationIsolatorTypeEnum_type = new enumeration_type("IfcVibrationIsolatorTypeEnum", 951, items);
    }
    {
        std::vector<std::string> items; items.reserve(7);
        items.push_back("ELEMENTEDWALL");
        items.push_back("NOTDEFINED");
        items.push_back("PLUMBINGWALL");
        items.push_back("POLYGONAL");
        items.push_back("SHEAR");
        items.push_back("STANDARD");
        items.push_back("USERDEFINED");
        IfcWallTypeEnum_type = new enumeration_type("IfcWallTypeEnum", 959, items);
    }
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
        IfcWasteTerminalTypeEnum_type = new enumeration_type("IfcWasteTerminalTypeEnum", 963, items);
    }
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
        IfcWindowPanelOperationEnum_type = new enumeration_type("IfcWindowPanelOperationEnum", 967, items);
    }
    {
        std::vector<std::string> items; items.reserve(6);
        items.push_back("BOTTOM");
        items.push_back("LEFT");
        items.push_back("MIDDLE");
        items.push_back("NOTDEFINED");
        items.push_back("RIGHT");
        items.push_back("TOP");
        IfcWindowPanelPositionEnum_type = new enumeration_type("IfcWindowPanelPositionEnum", 968, items);
    }
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
        IfcWindowStyleConstructionEnum_type = new enumeration_type("IfcWindowStyleConstructionEnum", 971, items);
    }
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
        IfcWindowStyleOperationEnum_type = new enumeration_type("IfcWindowStyleOperationEnum", 972, items);
    }
    {
        std::vector<std::string> items; items.reserve(5);
        items.push_back("ACTUAL");
        items.push_back("BASELINE");
        items.push_back("NOTDEFINED");
        items.push_back("PLANNED");
        items.push_back("USERDEFINED");
        IfcWorkControlTypeEnum_type = new enumeration_type("IfcWorkControlTypeEnum", 974, items);
    }
    IfcActorRole_type = new entity("IfcActorRole", 7, 0);
    IfcAddress_type = new entity("IfcAddress", 11, 0);
    IfcApplication_type = new entity("IfcApplication", 36, 0);
    IfcAppliedValue_type = new entity("IfcAppliedValue", 37, 0);
    IfcAppliedValueRelationship_type = new entity("IfcAppliedValueRelationship", 38, 0);
    IfcApproval_type = new entity("IfcApproval", 40, 0);
    IfcApprovalActorRelationship_type = new entity("IfcApprovalActorRelationship", 41, 0);
    IfcApprovalPropertyRelationship_type = new entity("IfcApprovalPropertyRelationship", 42, 0);
    IfcApprovalRelationship_type = new entity("IfcApprovalRelationship", 43, 0);
    IfcBoundaryCondition_type = new entity("IfcBoundaryCondition", 72, 0);
    IfcBoundaryEdgeCondition_type = new entity("IfcBoundaryEdgeCondition", 73, IfcBoundaryCondition_type);
    IfcBoundaryFaceCondition_type = new entity("IfcBoundaryFaceCondition", 74, IfcBoundaryCondition_type);
    IfcBoundaryNodeCondition_type = new entity("IfcBoundaryNodeCondition", 75, IfcBoundaryCondition_type);
    IfcBoundaryNodeConditionWarping_type = new entity("IfcBoundaryNodeConditionWarping", 76, IfcBoundaryNodeCondition_type);
    IfcCalendarDate_type = new entity("IfcCalendarDate", 98, 0);
    IfcClassification_type = new entity("IfcClassification", 114, 0);
    IfcClassificationItem_type = new entity("IfcClassificationItem", 115, 0);
    IfcClassificationItemRelationship_type = new entity("IfcClassificationItemRelationship", 116, 0);
    IfcClassificationNotation_type = new entity("IfcClassificationNotation", 117, 0);
    IfcClassificationNotationFacet_type = new entity("IfcClassificationNotationFacet", 118, 0);
    IfcColourSpecification_type = new entity("IfcColourSpecification", 127, 0);
    IfcConnectionGeometry_type = new entity("IfcConnectionGeometry", 147, 0);
    IfcConnectionPointGeometry_type = new entity("IfcConnectionPointGeometry", 149, IfcConnectionGeometry_type);
    IfcConnectionPortGeometry_type = new entity("IfcConnectionPortGeometry", 150, IfcConnectionGeometry_type);
    IfcConnectionSurfaceGeometry_type = new entity("IfcConnectionSurfaceGeometry", 151, IfcConnectionGeometry_type);
    IfcConstraint_type = new entity("IfcConstraint", 153, 0);
    IfcConstraintAggregationRelationship_type = new entity("IfcConstraintAggregationRelationship", 154, 0);
    IfcConstraintClassificationRelationship_type = new entity("IfcConstraintClassificationRelationship", 155, 0);
    IfcConstraintRelationship_type = new entity("IfcConstraintRelationship", 157, 0);
    IfcCoordinatedUniversalTimeOffset_type = new entity("IfcCoordinatedUniversalTimeOffset", 172, 0);
    IfcCostValue_type = new entity("IfcCostValue", 176, IfcAppliedValue_type);
    IfcCurrencyRelationship_type = new entity("IfcCurrencyRelationship", 188, 0);
    IfcCurveStyleFont_type = new entity("IfcCurveStyleFont", 198, 0);
    IfcCurveStyleFontAndScaling_type = new entity("IfcCurveStyleFontAndScaling", 199, 0);
    IfcCurveStyleFontPattern_type = new entity("IfcCurveStyleFontPattern", 200, 0);
    IfcDateAndTime_type = new entity("IfcDateAndTime", 205, 0);
    IfcDerivedUnit_type = new entity("IfcDerivedUnit", 213, 0);
    IfcDerivedUnitElement_type = new entity("IfcDerivedUnitElement", 214, 0);
    IfcDimensionalExponents_type = new entity("IfcDimensionalExponents", 225, 0);
    IfcDocumentElectronicFormat_type = new entity("IfcDocumentElectronicFormat", 241, 0);
    IfcDocumentInformation_type = new entity("IfcDocumentInformation", 242, 0);
    IfcDocumentInformationRelationship_type = new entity("IfcDocumentInformationRelationship", 243, 0);
    IfcDraughtingCalloutRelationship_type = new entity("IfcDraughtingCalloutRelationship", 258, 0);
    IfcEnvironmentalImpactValue_type = new entity("IfcEnvironmentalImpactValue", 314, IfcAppliedValue_type);
    IfcExternalReference_type = new entity("IfcExternalReference", 322, 0);
    IfcExternallyDefinedHatchStyle_type = new entity("IfcExternallyDefinedHatchStyle", 323, IfcExternalReference_type);
    IfcExternallyDefinedSurfaceStyle_type = new entity("IfcExternallyDefinedSurfaceStyle", 324, IfcExternalReference_type);
    IfcExternallyDefinedSymbol_type = new entity("IfcExternallyDefinedSymbol", 325, IfcExternalReference_type);
    IfcExternallyDefinedTextFont_type = new entity("IfcExternallyDefinedTextFont", 326, IfcExternalReference_type);
    IfcGridAxis_type = new entity("IfcGridAxis", 399, 0);
    IfcIrregularTimeSeriesValue_type = new entity("IfcIrregularTimeSeriesValue", 424, 0);
    IfcLibraryInformation_type = new entity("IfcLibraryInformation", 437, 0);
    IfcLibraryReference_type = new entity("IfcLibraryReference", 438, IfcExternalReference_type);
    IfcLightDistributionData_type = new entity("IfcLightDistributionData", 441, 0);
    IfcLightIntensityDistribution_type = new entity("IfcLightIntensityDistribution", 446, 0);
    IfcLocalTime_type = new entity("IfcLocalTime", 461, 0);
    IfcMaterial_type = new entity("IfcMaterial", 476, 0);
    IfcMaterialClassificationRelationship_type = new entity("IfcMaterialClassificationRelationship", 477, 0);
    IfcMaterialLayer_type = new entity("IfcMaterialLayer", 479, 0);
    IfcMaterialLayerSet_type = new entity("IfcMaterialLayerSet", 480, 0);
    IfcMaterialLayerSetUsage_type = new entity("IfcMaterialLayerSetUsage", 481, 0);
    IfcMaterialList_type = new entity("IfcMaterialList", 482, 0);
    IfcMaterialProperties_type = new entity("IfcMaterialProperties", 483, 0);
    IfcMeasureWithUnit_type = new entity("IfcMeasureWithUnit", 486, 0);
    IfcMechanicalMaterialProperties_type = new entity("IfcMechanicalMaterialProperties", 490, IfcMaterialProperties_type);
    IfcMechanicalSteelMaterialProperties_type = new entity("IfcMechanicalSteelMaterialProperties", 491, IfcMechanicalMaterialProperties_type);
    IfcMetric_type = new entity("IfcMetric", 495, IfcConstraint_type);
    IfcMonetaryUnit_type = new entity("IfcMonetaryUnit", 506, 0);
    IfcNamedUnit_type = new entity("IfcNamedUnit", 511, 0);
    IfcObjectPlacement_type = new entity("IfcObjectPlacement", 517, 0);
    IfcObjective_type = new entity("IfcObjective", 520, IfcConstraint_type);
    IfcOpticalMaterialProperties_type = new entity("IfcOpticalMaterialProperties", 529, IfcMaterialProperties_type);
    IfcOrganization_type = new entity("IfcOrganization", 531, 0);
    IfcOrganizationRelationship_type = new entity("IfcOrganizationRelationship", 532, 0);
    IfcOwnerHistory_type = new entity("IfcOwnerHistory", 537, 0);
    IfcPerson_type = new entity("IfcPerson", 546, 0);
    IfcPersonAndOrganization_type = new entity("IfcPersonAndOrganization", 547, 0);
    IfcPhysicalQuantity_type = new entity("IfcPhysicalQuantity", 550, 0);
    IfcPhysicalSimpleQuantity_type = new entity("IfcPhysicalSimpleQuantity", 551, IfcPhysicalQuantity_type);
    IfcPostalAddress_type = new entity("IfcPostalAddress", 580, IfcAddress_type);
    IfcPreDefinedItem_type = new entity("IfcPreDefinedItem", 585, 0);
    IfcPreDefinedSymbol_type = new entity("IfcPreDefinedSymbol", 587, IfcPreDefinedItem_type);
    IfcPreDefinedTerminatorSymbol_type = new entity("IfcPreDefinedTerminatorSymbol", 588, IfcPreDefinedSymbol_type);
    IfcPreDefinedTextFont_type = new entity("IfcPreDefinedTextFont", 589, IfcPreDefinedItem_type);
    IfcPresentationLayerAssignment_type = new entity("IfcPresentationLayerAssignment", 591, 0);
    IfcPresentationLayerWithStyle_type = new entity("IfcPresentationLayerWithStyle", 592, IfcPresentationLayerAssignment_type);
    IfcPresentationStyle_type = new entity("IfcPresentationStyle", 593, 0);
    IfcPresentationStyleAssignment_type = new entity("IfcPresentationStyleAssignment", 594, 0);
    IfcProductRepresentation_type = new entity("IfcProductRepresentation", 602, 0);
    IfcProductsOfCombustionProperties_type = new entity("IfcProductsOfCombustionProperties", 603, IfcMaterialProperties_type);
    IfcProfileDef_type = new entity("IfcProfileDef", 604, 0);
    IfcProfileProperties_type = new entity("IfcProfileProperties", 605, 0);
    IfcProperty_type = new entity("IfcProperty", 615, 0);
    IfcPropertyConstraintRelationship_type = new entity("IfcPropertyConstraintRelationship", 617, 0);
    IfcPropertyDependencyRelationship_type = new entity("IfcPropertyDependencyRelationship", 619, 0);
    IfcPropertyEnumeration_type = new entity("IfcPropertyEnumeration", 621, 0);
    IfcQuantityArea_type = new entity("IfcQuantityArea", 634, IfcPhysicalSimpleQuantity_type);
    IfcQuantityCount_type = new entity("IfcQuantityCount", 635, IfcPhysicalSimpleQuantity_type);
    IfcQuantityLength_type = new entity("IfcQuantityLength", 636, IfcPhysicalSimpleQuantity_type);
    IfcQuantityTime_type = new entity("IfcQuantityTime", 637, IfcPhysicalSimpleQuantity_type);
    IfcQuantityVolume_type = new entity("IfcQuantityVolume", 638, IfcPhysicalSimpleQuantity_type);
    IfcQuantityWeight_type = new entity("IfcQuantityWeight", 639, IfcPhysicalSimpleQuantity_type);
    IfcReferencesValueDocument_type = new entity("IfcReferencesValueDocument", 657, 0);
    IfcReinforcementBarProperties_type = new entity("IfcReinforcementBarProperties", 660, 0);
    IfcRelaxation_type = new entity("IfcRelaxation", 717, 0);
    IfcRepresentation_type = new entity("IfcRepresentation", 718, 0);
    IfcRepresentationContext_type = new entity("IfcRepresentationContext", 719, 0);
    IfcRepresentationItem_type = new entity("IfcRepresentationItem", 720, 0);
    IfcRepresentationMap_type = new entity("IfcRepresentationMap", 721, 0);
    IfcRibPlateProfileProperties_type = new entity("IfcRibPlateProfileProperties", 726, IfcProfileProperties_type);
    IfcRoot_type = new entity("IfcRoot", 732, 0);
    IfcSIUnit_type = new entity("IfcSIUnit", 739, IfcNamedUnit_type);
    IfcSectionProperties_type = new entity("IfcSectionProperties", 746, 0);
    IfcSectionReinforcementProperties_type = new entity("IfcSectionReinforcementProperties", 747, 0);
    IfcShapeAspect_type = new entity("IfcShapeAspect", 758, 0);
    IfcShapeModel_type = new entity("IfcShapeModel", 759, IfcRepresentation_type);
    IfcShapeRepresentation_type = new entity("IfcShapeRepresentation", 760, IfcShapeModel_type);
    IfcSimpleProperty_type = new entity("IfcSimpleProperty", 764, IfcProperty_type);
    IfcStructuralConnectionCondition_type = new entity("IfcStructuralConnectionCondition", 806, 0);
    IfcStructuralLoad_type = new entity("IfcStructuralLoad", 814, 0);
    IfcStructuralLoadStatic_type = new entity("IfcStructuralLoadStatic", 822, IfcStructuralLoad_type);
    IfcStructuralLoadTemperature_type = new entity("IfcStructuralLoadTemperature", 823, IfcStructuralLoadStatic_type);
    IfcStyleModel_type = new entity("IfcStyleModel", 839, IfcRepresentation_type);
    IfcStyledItem_type = new entity("IfcStyledItem", 840, IfcRepresentationItem_type);
    IfcStyledRepresentation_type = new entity("IfcStyledRepresentation", 841, IfcStyleModel_type);
    IfcSurfaceStyle_type = new entity("IfcSurfaceStyle", 850, IfcPresentationStyle_type);
    IfcSurfaceStyleLighting_type = new entity("IfcSurfaceStyleLighting", 852, 0);
    IfcSurfaceStyleRefraction_type = new entity("IfcSurfaceStyleRefraction", 853, 0);
    IfcSurfaceStyleShading_type = new entity("IfcSurfaceStyleShading", 855, 0);
    IfcSurfaceStyleWithTextures_type = new entity("IfcSurfaceStyleWithTextures", 856, 0);
    IfcSurfaceTexture_type = new entity("IfcSurfaceTexture", 857, 0);
    IfcSymbolStyle_type = new entity("IfcSymbolStyle", 864, IfcPresentationStyle_type);
    IfcTable_type = new entity("IfcTable", 869, 0);
    IfcTableRow_type = new entity("IfcTableRow", 870, 0);
    IfcTelecomAddress_type = new entity("IfcTelecomAddress", 874, IfcAddress_type);
    IfcTextStyle_type = new entity("IfcTextStyle", 888, IfcPresentationStyle_type);
    IfcTextStyleFontModel_type = new entity("IfcTextStyleFontModel", 889, IfcPreDefinedTextFont_type);
    IfcTextStyleForDefinedFont_type = new entity("IfcTextStyleForDefinedFont", 890, 0);
    IfcTextStyleTextModel_type = new entity("IfcTextStyleTextModel", 892, 0);
    IfcTextStyleWithBoxCharacteristics_type = new entity("IfcTextStyleWithBoxCharacteristics", 893, 0);
    IfcTextureCoordinate_type = new entity("IfcTextureCoordinate", 895, 0);
    IfcTextureCoordinateGenerator_type = new entity("IfcTextureCoordinateGenerator", 896, IfcTextureCoordinate_type);
    IfcTextureMap_type = new entity("IfcTextureMap", 897, IfcTextureCoordinate_type);
    IfcTextureVertex_type = new entity("IfcTextureVertex", 898, 0);
    IfcThermalMaterialProperties_type = new entity("IfcThermalMaterialProperties", 904, IfcMaterialProperties_type);
    IfcTimeSeries_type = new entity("IfcTimeSeries", 909, 0);
    IfcTimeSeriesReferenceRelationship_type = new entity("IfcTimeSeriesReferenceRelationship", 911, 0);
    IfcTimeSeriesValue_type = new entity("IfcTimeSeriesValue", 914, 0);
    IfcTopologicalRepresentationItem_type = new entity("IfcTopologicalRepresentationItem", 916, IfcRepresentationItem_type);
    IfcTopologyRepresentation_type = new entity("IfcTopologyRepresentation", 917, IfcShapeModel_type);
    IfcUnitAssignment_type = new entity("IfcUnitAssignment", 936, 0);
    IfcVertex_type = new entity("IfcVertex", 946, IfcTopologicalRepresentationItem_type);
    IfcVertexBasedTextureMap_type = new entity("IfcVertexBasedTextureMap", 947, 0);
    IfcVertexPoint_type = new entity("IfcVertexPoint", 949, IfcVertex_type);
    IfcVirtualGridIntersection_type = new entity("IfcVirtualGridIntersection", 953, 0);
    IfcWaterProperties_type = new entity("IfcWaterProperties", 964, IfcMaterialProperties_type);
    IfcAnnotationOccurrence_type = new entity("IfcAnnotationOccurrence", 31, IfcStyledItem_type);
    IfcAnnotationSurfaceOccurrence_type = new entity("IfcAnnotationSurfaceOccurrence", 33, IfcAnnotationOccurrence_type);
    IfcAnnotationSymbolOccurrence_type = new entity("IfcAnnotationSymbolOccurrence", 34, IfcAnnotationOccurrence_type);
    IfcAnnotationTextOccurrence_type = new entity("IfcAnnotationTextOccurrence", 35, IfcAnnotationOccurrence_type);
    IfcArbitraryClosedProfileDef_type = new entity("IfcArbitraryClosedProfileDef", 44, IfcProfileDef_type);
    IfcArbitraryOpenProfileDef_type = new entity("IfcArbitraryOpenProfileDef", 45, IfcProfileDef_type);
    IfcArbitraryProfileDefWithVoids_type = new entity("IfcArbitraryProfileDefWithVoids", 46, IfcArbitraryClosedProfileDef_type);
    IfcBlobTexture_type = new entity("IfcBlobTexture", 63, IfcSurfaceTexture_type);
    IfcCenterLineProfileDef_type = new entity("IfcCenterLineProfileDef", 105, IfcArbitraryOpenProfileDef_type);
    IfcClassificationReference_type = new entity("IfcClassificationReference", 120, IfcExternalReference_type);
    IfcColourRgb_type = new entity("IfcColourRgb", 126, IfcColourSpecification_type);
    IfcComplexProperty_type = new entity("IfcComplexProperty", 132, IfcProperty_type);
    IfcCompositeProfileDef_type = new entity("IfcCompositeProfileDef", 135, IfcProfileDef_type);
    IfcConnectedFaceSet_type = new entity("IfcConnectedFaceSet", 145, IfcTopologicalRepresentationItem_type);
    IfcConnectionCurveGeometry_type = new entity("IfcConnectionCurveGeometry", 146, IfcConnectionGeometry_type);
    IfcConnectionPointEccentricity_type = new entity("IfcConnectionPointEccentricity", 148, IfcConnectionPointGeometry_type);
    IfcContextDependentUnit_type = new entity("IfcContextDependentUnit", 163, IfcNamedUnit_type);
    IfcConversionBasedUnit_type = new entity("IfcConversionBasedUnit", 167, IfcNamedUnit_type);
    IfcCurveStyle_type = new entity("IfcCurveStyle", 197, IfcPresentationStyle_type);
    IfcDerivedProfileDef_type = new entity("IfcDerivedProfileDef", 212, IfcProfileDef_type);
    IfcDimensionCalloutRelationship_type = new entity("IfcDimensionCalloutRelationship", 218, IfcDraughtingCalloutRelationship_type);
    IfcDimensionPair_type = new entity("IfcDimensionPair", 224, IfcDraughtingCalloutRelationship_type);
    IfcDocumentReference_type = new entity("IfcDocumentReference", 244, IfcExternalReference_type);
    IfcDraughtingPreDefinedTextFont_type = new entity("IfcDraughtingPreDefinedTextFont", 261, IfcPreDefinedTextFont_type);
    IfcEdge_type = new entity("IfcEdge", 269, IfcTopologicalRepresentationItem_type);
    IfcEdgeCurve_type = new entity("IfcEdgeCurve", 270, IfcEdge_type);
    IfcExtendedMaterialProperties_type = new entity("IfcExtendedMaterialProperties", 321, IfcMaterialProperties_type);
    IfcFace_type = new entity("IfcFace", 328, IfcTopologicalRepresentationItem_type);
    IfcFaceBound_type = new entity("IfcFaceBound", 330, IfcTopologicalRepresentationItem_type);
    IfcFaceOuterBound_type = new entity("IfcFaceOuterBound", 331, IfcFaceBound_type);
    IfcFaceSurface_type = new entity("IfcFaceSurface", 332, IfcFace_type);
    IfcFailureConnectionCondition_type = new entity("IfcFailureConnectionCondition", 335, IfcStructuralConnectionCondition_type);
    IfcFillAreaStyle_type = new entity("IfcFillAreaStyle", 343, IfcPresentationStyle_type);
    IfcFuelProperties_type = new entity("IfcFuelProperties", 380, IfcMaterialProperties_type);
    IfcGeneralMaterialProperties_type = new entity("IfcGeneralMaterialProperties", 387, IfcMaterialProperties_type);
    IfcGeneralProfileProperties_type = new entity("IfcGeneralProfileProperties", 388, IfcProfileProperties_type);
    IfcGeometricRepresentationContext_type = new entity("IfcGeometricRepresentationContext", 391, IfcRepresentationContext_type);
    IfcGeometricRepresentationItem_type = new entity("IfcGeometricRepresentationItem", 392, IfcRepresentationItem_type);
    IfcGeometricRepresentationSubContext_type = new entity("IfcGeometricRepresentationSubContext", 393, IfcGeometricRepresentationContext_type);
    IfcGeometricSet_type = new entity("IfcGeometricSet", 394, IfcGeometricRepresentationItem_type);
    IfcGridPlacement_type = new entity("IfcGridPlacement", 400, IfcObjectPlacement_type);
    IfcHalfSpaceSolid_type = new entity("IfcHalfSpaceSolid", 402, IfcGeometricRepresentationItem_type);
    IfcHygroscopicMaterialProperties_type = new entity("IfcHygroscopicMaterialProperties", 411, IfcMaterialProperties_type);
    IfcImageTexture_type = new entity("IfcImageTexture", 415, IfcSurfaceTexture_type);
    IfcIrregularTimeSeries_type = new entity("IfcIrregularTimeSeries", 423, IfcTimeSeries_type);
    IfcLightSource_type = new entity("IfcLightSource", 447, IfcGeometricRepresentationItem_type);
    IfcLightSourceAmbient_type = new entity("IfcLightSourceAmbient", 448, IfcLightSource_type);
    IfcLightSourceDirectional_type = new entity("IfcLightSourceDirectional", 449, IfcLightSource_type);
    IfcLightSourceGoniometric_type = new entity("IfcLightSourceGoniometric", 450, IfcLightSource_type);
    IfcLightSourcePositional_type = new entity("IfcLightSourcePositional", 451, IfcLightSource_type);
    IfcLightSourceSpot_type = new entity("IfcLightSourceSpot", 452, IfcLightSourcePositional_type);
    IfcLocalPlacement_type = new entity("IfcLocalPlacement", 460, IfcObjectPlacement_type);
    IfcLoop_type = new entity("IfcLoop", 464, IfcTopologicalRepresentationItem_type);
    IfcMappedItem_type = new entity("IfcMappedItem", 471, IfcRepresentationItem_type);
    IfcMaterialDefinitionRepresentation_type = new entity("IfcMaterialDefinitionRepresentation", 478, IfcProductRepresentation_type);
    IfcMechanicalConcreteMaterialProperties_type = new entity("IfcMechanicalConcreteMaterialProperties", 487, IfcMechanicalMaterialProperties_type);
    IfcObjectDefinition_type = new entity("IfcObjectDefinition", 516, IfcRoot_type);
    IfcOneDirectionRepeatFactor_type = new entity("IfcOneDirectionRepeatFactor", 526, IfcGeometricRepresentationItem_type);
    IfcOpenShell_type = new entity("IfcOpenShell", 527, IfcConnectedFaceSet_type);
    IfcOrientedEdge_type = new entity("IfcOrientedEdge", 534, IfcEdge_type);
    IfcParameterizedProfileDef_type = new entity("IfcParameterizedProfileDef", 540, IfcProfileDef_type);
    IfcPath_type = new entity("IfcPath", 541, IfcTopologicalRepresentationItem_type);
    IfcPhysicalComplexQuantity_type = new entity("IfcPhysicalComplexQuantity", 548, IfcPhysicalQuantity_type);
    IfcPixelTexture_type = new entity("IfcPixelTexture", 559, IfcSurfaceTexture_type);
    IfcPlacement_type = new entity("IfcPlacement", 560, IfcGeometricRepresentationItem_type);
    IfcPlanarExtent_type = new entity("IfcPlanarExtent", 562, IfcGeometricRepresentationItem_type);
    IfcPoint_type = new entity("IfcPoint", 569, IfcGeometricRepresentationItem_type);
    IfcPointOnCurve_type = new entity("IfcPointOnCurve", 570, IfcPoint_type);
    IfcPointOnSurface_type = new entity("IfcPointOnSurface", 571, IfcPoint_type);
    IfcPolyLoop_type = new entity("IfcPolyLoop", 573, IfcLoop_type);
    IfcPolygonalBoundedHalfSpace_type = new entity("IfcPolygonalBoundedHalfSpace", 574, IfcHalfSpaceSolid_type);
    IfcPreDefinedColour_type = new entity("IfcPreDefinedColour", 582, IfcPreDefinedItem_type);
    IfcPreDefinedCurveFont_type = new entity("IfcPreDefinedCurveFont", 583, IfcPreDefinedItem_type);
    IfcPreDefinedDimensionSymbol_type = new entity("IfcPreDefinedDimensionSymbol", 584, IfcPreDefinedSymbol_type);
    IfcPreDefinedPointMarkerSymbol_type = new entity("IfcPreDefinedPointMarkerSymbol", 586, IfcPreDefinedSymbol_type);
    IfcProductDefinitionShape_type = new entity("IfcProductDefinitionShape", 601, IfcProductRepresentation_type);
    IfcPropertyBoundedValue_type = new entity("IfcPropertyBoundedValue", 616, IfcSimpleProperty_type);
    IfcPropertyDefinition_type = new entity("IfcPropertyDefinition", 618, IfcRoot_type);
    IfcPropertyEnumeratedValue_type = new entity("IfcPropertyEnumeratedValue", 620, IfcSimpleProperty_type);
    IfcPropertyListValue_type = new entity("IfcPropertyListValue", 622, IfcSimpleProperty_type);
    IfcPropertyReferenceValue_type = new entity("IfcPropertyReferenceValue", 623, IfcSimpleProperty_type);
    IfcPropertySetDefinition_type = new entity("IfcPropertySetDefinition", 625, IfcPropertyDefinition_type);
    IfcPropertySingleValue_type = new entity("IfcPropertySingleValue", 626, IfcSimpleProperty_type);
    IfcPropertyTableValue_type = new entity("IfcPropertyTableValue", 628, IfcSimpleProperty_type);
    IfcRectangleProfileDef_type = new entity("IfcRectangleProfileDef", 654, IfcParameterizedProfileDef_type);
    IfcRegularTimeSeries_type = new entity("IfcRegularTimeSeries", 659, IfcTimeSeries_type);
    IfcReinforcementDefinitionProperties_type = new entity("IfcReinforcementDefinitionProperties", 661, IfcPropertySetDefinition_type);
    IfcRelationship_type = new entity("IfcRelationship", 716, IfcRoot_type);
    IfcRoundedRectangleProfileDef_type = new entity("IfcRoundedRectangleProfileDef", 737, IfcRectangleProfileDef_type);
    IfcSectionedSpine_type = new entity("IfcSectionedSpine", 750, IfcGeometricRepresentationItem_type);
    IfcServiceLifeFactor_type = new entity("IfcServiceLifeFactor", 755, IfcPropertySetDefinition_type);
    IfcShellBasedSurfaceModel_type = new entity("IfcShellBasedSurfaceModel", 763, IfcGeometricRepresentationItem_type);
    IfcSlippageConnectionCondition_type = new entity("IfcSlippageConnectionCondition", 771, IfcStructuralConnectionCondition_type);
    IfcSolidModel_type = new entity("IfcSolidModel", 773, IfcGeometricRepresentationItem_type);
    IfcSoundProperties_type = new entity("IfcSoundProperties", 776, IfcPropertySetDefinition_type);
    IfcSoundValue_type = new entity("IfcSoundValue", 778, IfcPropertySetDefinition_type);
    IfcSpaceThermalLoadProperties_type = new entity("IfcSpaceThermalLoadProperties", 783, IfcPropertySetDefinition_type);
    IfcStructuralLoadLinearForce_type = new entity("IfcStructuralLoadLinearForce", 816, IfcStructuralLoadStatic_type);
    IfcStructuralLoadPlanarForce_type = new entity("IfcStructuralLoadPlanarForce", 817, IfcStructuralLoadStatic_type);
    IfcStructuralLoadSingleDisplacement_type = new entity("IfcStructuralLoadSingleDisplacement", 818, IfcStructuralLoadStatic_type);
    IfcStructuralLoadSingleDisplacementDistortion_type = new entity("IfcStructuralLoadSingleDisplacementDistortion", 819, IfcStructuralLoadSingleDisplacement_type);
    IfcStructuralLoadSingleForce_type = new entity("IfcStructuralLoadSingleForce", 820, IfcStructuralLoadStatic_type);
    IfcStructuralLoadSingleForceWarping_type = new entity("IfcStructuralLoadSingleForceWarping", 821, IfcStructuralLoadSingleForce_type);
    IfcStructuralProfileProperties_type = new entity("IfcStructuralProfileProperties", 830, IfcGeneralProfileProperties_type);
    IfcStructuralSteelProfileProperties_type = new entity("IfcStructuralSteelProfileProperties", 833, IfcStructuralProfileProperties_type);
    IfcSubedge_type = new entity("IfcSubedge", 843, IfcEdge_type);
    IfcSurface_type = new entity("IfcSurface", 844, IfcGeometricRepresentationItem_type);
    IfcSurfaceStyleRendering_type = new entity("IfcSurfaceStyleRendering", 854, IfcSurfaceStyleShading_type);
    IfcSweptAreaSolid_type = new entity("IfcSweptAreaSolid", 859, IfcSolidModel_type);
    IfcSweptDiskSolid_type = new entity("IfcSweptDiskSolid", 860, IfcSolidModel_type);
    IfcSweptSurface_type = new entity("IfcSweptSurface", 861, IfcSurface_type);
    IfcTShapeProfileDef_type = new entity("IfcTShapeProfileDef", 868, IfcParameterizedProfileDef_type);
    IfcTerminatorSymbol_type = new entity("IfcTerminatorSymbol", 879, IfcAnnotationSymbolOccurrence_type);
    IfcTextLiteral_type = new entity("IfcTextLiteral", 885, IfcGeometricRepresentationItem_type);
    IfcTextLiteralWithExtent_type = new entity("IfcTextLiteralWithExtent", 886, IfcTextLiteral_type);
    IfcTrapeziumProfileDef_type = new entity("IfcTrapeziumProfileDef", 925, IfcParameterizedProfileDef_type);
    IfcTwoDirectionRepeatFactor_type = new entity("IfcTwoDirectionRepeatFactor", 931, IfcOneDirectionRepeatFactor_type);
    IfcTypeObject_type = new entity("IfcTypeObject", 932, IfcObjectDefinition_type);
    IfcTypeProduct_type = new entity("IfcTypeProduct", 933, IfcTypeObject_type);
    IfcUShapeProfileDef_type = new entity("IfcUShapeProfileDef", 934, IfcParameterizedProfileDef_type);
    IfcVector_type = new entity("IfcVector", 944, IfcGeometricRepresentationItem_type);
    IfcVertexLoop_type = new entity("IfcVertexLoop", 948, IfcLoop_type);
    IfcWindowLiningProperties_type = new entity("IfcWindowLiningProperties", 966, IfcPropertySetDefinition_type);
    IfcWindowPanelProperties_type = new entity("IfcWindowPanelProperties", 969, IfcPropertySetDefinition_type);
    IfcWindowStyle_type = new entity("IfcWindowStyle", 970, IfcTypeProduct_type);
    IfcZShapeProfileDef_type = new entity("IfcZShapeProfileDef", 978, IfcParameterizedProfileDef_type);
    IfcAnnotationCurveOccurrence_type = new entity("IfcAnnotationCurveOccurrence", 28, IfcAnnotationOccurrence_type);
    IfcAnnotationFillArea_type = new entity("IfcAnnotationFillArea", 29, IfcGeometricRepresentationItem_type);
    IfcAnnotationFillAreaOccurrence_type = new entity("IfcAnnotationFillAreaOccurrence", 30, IfcAnnotationOccurrence_type);
    IfcAnnotationSurface_type = new entity("IfcAnnotationSurface", 32, IfcGeometricRepresentationItem_type);
    IfcAxis1Placement_type = new entity("IfcAxis1Placement", 52, IfcPlacement_type);
    IfcAxis2Placement2D_type = new entity("IfcAxis2Placement2D", 54, IfcPlacement_type);
    IfcAxis2Placement3D_type = new entity("IfcAxis2Placement3D", 55, IfcPlacement_type);
    IfcBooleanResult_type = new entity("IfcBooleanResult", 71, IfcGeometricRepresentationItem_type);
    IfcBoundedSurface_type = new entity("IfcBoundedSurface", 78, IfcSurface_type);
    IfcBoundingBox_type = new entity("IfcBoundingBox", 79, IfcGeometricRepresentationItem_type);
    IfcBoxedHalfSpace_type = new entity("IfcBoxedHalfSpace", 81, IfcHalfSpaceSolid_type);
    IfcCShapeProfileDef_type = new entity("IfcCShapeProfileDef", 91, IfcParameterizedProfileDef_type);
    IfcCartesianPoint_type = new entity("IfcCartesianPoint", 99, IfcPoint_type);
    IfcCartesianTransformationOperator_type = new entity("IfcCartesianTransformationOperator", 100, IfcGeometricRepresentationItem_type);
    IfcCartesianTransformationOperator2D_type = new entity("IfcCartesianTransformationOperator2D", 101, IfcCartesianTransformationOperator_type);
    IfcCartesianTransformationOperator2DnonUniform_type = new entity("IfcCartesianTransformationOperator2DnonUniform", 102, IfcCartesianTransformationOperator2D_type);
    IfcCartesianTransformationOperator3D_type = new entity("IfcCartesianTransformationOperator3D", 103, IfcCartesianTransformationOperator_type);
    IfcCartesianTransformationOperator3DnonUniform_type = new entity("IfcCartesianTransformationOperator3DnonUniform", 104, IfcCartesianTransformationOperator3D_type);
    IfcCircleProfileDef_type = new entity("IfcCircleProfileDef", 113, IfcParameterizedProfileDef_type);
    IfcClosedShell_type = new entity("IfcClosedShell", 121, IfcConnectedFaceSet_type);
    IfcCompositeCurveSegment_type = new entity("IfcCompositeCurveSegment", 134, IfcGeometricRepresentationItem_type);
    IfcCraneRailAShapeProfileDef_type = new entity("IfcCraneRailAShapeProfileDef", 181, IfcParameterizedProfileDef_type);
    IfcCraneRailFShapeProfileDef_type = new entity("IfcCraneRailFShapeProfileDef", 182, IfcParameterizedProfileDef_type);
    IfcCsgPrimitive3D_type = new entity("IfcCsgPrimitive3D", 184, IfcGeometricRepresentationItem_type);
    IfcCsgSolid_type = new entity("IfcCsgSolid", 186, IfcSolidModel_type);
    IfcCurve_type = new entity("IfcCurve", 193, IfcGeometricRepresentationItem_type);
    IfcCurveBoundedPlane_type = new entity("IfcCurveBoundedPlane", 194, IfcBoundedSurface_type);
    IfcDefinedSymbol_type = new entity("IfcDefinedSymbol", 209, IfcGeometricRepresentationItem_type);
    IfcDimensionCurve_type = new entity("IfcDimensionCurve", 220, IfcAnnotationCurveOccurrence_type);
    IfcDimensionCurveTerminator_type = new entity("IfcDimensionCurveTerminator", 222, IfcTerminatorSymbol_type);
    IfcDirection_type = new entity("IfcDirection", 226, IfcGeometricRepresentationItem_type);
    IfcDoorLiningProperties_type = new entity("IfcDoorLiningProperties", 248, IfcPropertySetDefinition_type);
    IfcDoorPanelProperties_type = new entity("IfcDoorPanelProperties", 251, IfcPropertySetDefinition_type);
    IfcDoorStyle_type = new entity("IfcDoorStyle", 252, IfcTypeProduct_type);
    IfcDraughtingCallout_type = new entity("IfcDraughtingCallout", 256, IfcGeometricRepresentationItem_type);
    IfcDraughtingPreDefinedColour_type = new entity("IfcDraughtingPreDefinedColour", 259, IfcPreDefinedColour_type);
    IfcDraughtingPreDefinedCurveFont_type = new entity("IfcDraughtingPreDefinedCurveFont", 260, IfcPreDefinedCurveFont_type);
    IfcEdgeLoop_type = new entity("IfcEdgeLoop", 272, IfcLoop_type);
    IfcElementQuantity_type = new entity("IfcElementQuantity", 303, IfcPropertySetDefinition_type);
    IfcElementType_type = new entity("IfcElementType", 304, IfcTypeProduct_type);
    IfcElementarySurface_type = new entity("IfcElementarySurface", 305, IfcSurface_type);
    IfcEllipseProfileDef_type = new entity("IfcEllipseProfileDef", 307, IfcParameterizedProfileDef_type);
    IfcEnergyProperties_type = new entity("IfcEnergyProperties", 311, IfcPropertySetDefinition_type);
    IfcExtrudedAreaSolid_type = new entity("IfcExtrudedAreaSolid", 327, IfcSweptAreaSolid_type);
    IfcFaceBasedSurfaceModel_type = new entity("IfcFaceBasedSurfaceModel", 329, IfcGeometricRepresentationItem_type);
    IfcFillAreaStyleHatching_type = new entity("IfcFillAreaStyleHatching", 344, IfcGeometricRepresentationItem_type);
    IfcFillAreaStyleTileSymbolWithStyle_type = new entity("IfcFillAreaStyleTileSymbolWithStyle", 346, IfcGeometricRepresentationItem_type);
    IfcFillAreaStyleTiles_type = new entity("IfcFillAreaStyleTiles", 347, IfcGeometricRepresentationItem_type);
    IfcFluidFlowProperties_type = new entity("IfcFluidFlowProperties", 372, IfcPropertySetDefinition_type);
    IfcFurnishingElementType_type = new entity("IfcFurnishingElementType", 382, IfcElementType_type);
    IfcFurnitureType_type = new entity("IfcFurnitureType", 384, IfcFurnishingElementType_type);
    IfcGeometricCurveSet_type = new entity("IfcGeometricCurveSet", 389, IfcGeometricSet_type);
    IfcIShapeProfileDef_type = new entity("IfcIShapeProfileDef", 412, IfcParameterizedProfileDef_type);
    IfcLShapeProfileDef_type = new entity("IfcLShapeProfileDef", 429, IfcParameterizedProfileDef_type);
    IfcLine_type = new entity("IfcLine", 453, IfcCurve_type);
    IfcManifoldSolidBrep_type = new entity("IfcManifoldSolidBrep", 470, IfcSolidModel_type);
    IfcObject_type = new entity("IfcObject", 515, IfcObjectDefinition_type);
    IfcOffsetCurve2D_type = new entity("IfcOffsetCurve2D", 524, IfcCurve_type);
    IfcOffsetCurve3D_type = new entity("IfcOffsetCurve3D", 525, IfcCurve_type);
    IfcPermeableCoveringProperties_type = new entity("IfcPermeableCoveringProperties", 544, IfcPropertySetDefinition_type);
    IfcPlanarBox_type = new entity("IfcPlanarBox", 561, IfcPlanarExtent_type);
    IfcPlane_type = new entity("IfcPlane", 564, IfcElementarySurface_type);
    IfcProcess_type = new entity("IfcProcess", 599, IfcObject_type);
    IfcProduct_type = new entity("IfcProduct", 600, IfcObject_type);
    IfcProject_type = new entity("IfcProject", 607, IfcObject_type);
    IfcProjectionCurve_type = new entity("IfcProjectionCurve", 613, IfcAnnotationCurveOccurrence_type);
    IfcPropertySet_type = new entity("IfcPropertySet", 624, IfcPropertySetDefinition_type);
    IfcProxy_type = new entity("IfcProxy", 631, IfcProduct_type);
    IfcRectangleHollowProfileDef_type = new entity("IfcRectangleHollowProfileDef", 653, IfcRectangleProfileDef_type);
    IfcRectangularPyramid_type = new entity("IfcRectangularPyramid", 655, IfcCsgPrimitive3D_type);
    IfcRectangularTrimmedSurface_type = new entity("IfcRectangularTrimmedSurface", 656, IfcBoundedSurface_type);
    IfcRelAssigns_type = new entity("IfcRelAssigns", 668, IfcRelationship_type);
    IfcRelAssignsToActor_type = new entity("IfcRelAssignsToActor", 670, IfcRelAssigns_type);
    IfcRelAssignsToControl_type = new entity("IfcRelAssignsToControl", 671, IfcRelAssigns_type);
    IfcRelAssignsToGroup_type = new entity("IfcRelAssignsToGroup", 672, IfcRelAssigns_type);
    IfcRelAssignsToProcess_type = new entity("IfcRelAssignsToProcess", 673, IfcRelAssigns_type);
    IfcRelAssignsToProduct_type = new entity("IfcRelAssignsToProduct", 674, IfcRelAssigns_type);
    IfcRelAssignsToProjectOrder_type = new entity("IfcRelAssignsToProjectOrder", 675, IfcRelAssignsToControl_type);
    IfcRelAssignsToResource_type = new entity("IfcRelAssignsToResource", 676, IfcRelAssigns_type);
    IfcRelAssociates_type = new entity("IfcRelAssociates", 677, IfcRelationship_type);
    IfcRelAssociatesAppliedValue_type = new entity("IfcRelAssociatesAppliedValue", 678, IfcRelAssociates_type);
    IfcRelAssociatesApproval_type = new entity("IfcRelAssociatesApproval", 679, IfcRelAssociates_type);
    IfcRelAssociatesClassification_type = new entity("IfcRelAssociatesClassification", 680, IfcRelAssociates_type);
    IfcRelAssociatesConstraint_type = new entity("IfcRelAssociatesConstraint", 681, IfcRelAssociates_type);
    IfcRelAssociatesDocument_type = new entity("IfcRelAssociatesDocument", 682, IfcRelAssociates_type);
    IfcRelAssociatesLibrary_type = new entity("IfcRelAssociatesLibrary", 683, IfcRelAssociates_type);
    IfcRelAssociatesMaterial_type = new entity("IfcRelAssociatesMaterial", 684, IfcRelAssociates_type);
    IfcRelAssociatesProfileProperties_type = new entity("IfcRelAssociatesProfileProperties", 685, IfcRelAssociates_type);
    IfcRelConnects_type = new entity("IfcRelConnects", 686, IfcRelationship_type);
    IfcRelConnectsElements_type = new entity("IfcRelConnectsElements", 687, IfcRelConnects_type);
    IfcRelConnectsPathElements_type = new entity("IfcRelConnectsPathElements", 688, IfcRelConnectsElements_type);
    IfcRelConnectsPortToElement_type = new entity("IfcRelConnectsPortToElement", 689, IfcRelConnects_type);
    IfcRelConnectsPorts_type = new entity("IfcRelConnectsPorts", 690, IfcRelConnects_type);
    IfcRelConnectsStructuralActivity_type = new entity("IfcRelConnectsStructuralActivity", 691, IfcRelConnects_type);
    IfcRelConnectsStructuralElement_type = new entity("IfcRelConnectsStructuralElement", 692, IfcRelConnects_type);
    IfcRelConnectsStructuralMember_type = new entity("IfcRelConnectsStructuralMember", 693, IfcRelConnects_type);
    IfcRelConnectsWithEccentricity_type = new entity("IfcRelConnectsWithEccentricity", 694, IfcRelConnectsStructuralMember_type);
    IfcRelConnectsWithRealizingElements_type = new entity("IfcRelConnectsWithRealizingElements", 695, IfcRelConnectsElements_type);
    IfcRelContainedInSpatialStructure_type = new entity("IfcRelContainedInSpatialStructure", 696, IfcRelConnects_type);
    IfcRelCoversBldgElements_type = new entity("IfcRelCoversBldgElements", 697, IfcRelConnects_type);
    IfcRelCoversSpaces_type = new entity("IfcRelCoversSpaces", 698, IfcRelConnects_type);
    IfcRelDecomposes_type = new entity("IfcRelDecomposes", 699, IfcRelationship_type);
    IfcRelDefines_type = new entity("IfcRelDefines", 700, IfcRelationship_type);
    IfcRelDefinesByProperties_type = new entity("IfcRelDefinesByProperties", 701, IfcRelDefines_type);
    IfcRelDefinesByType_type = new entity("IfcRelDefinesByType", 702, IfcRelDefines_type);
    IfcRelFillsElement_type = new entity("IfcRelFillsElement", 703, IfcRelConnects_type);
    IfcRelFlowControlElements_type = new entity("IfcRelFlowControlElements", 704, IfcRelConnects_type);
    IfcRelInteractionRequirements_type = new entity("IfcRelInteractionRequirements", 705, IfcRelConnects_type);
    IfcRelNests_type = new entity("IfcRelNests", 706, IfcRelDecomposes_type);
    IfcRelOccupiesSpaces_type = new entity("IfcRelOccupiesSpaces", 707, IfcRelAssignsToActor_type);
    IfcRelOverridesProperties_type = new entity("IfcRelOverridesProperties", 708, IfcRelDefinesByProperties_type);
    IfcRelProjectsElement_type = new entity("IfcRelProjectsElement", 709, IfcRelConnects_type);
    IfcRelReferencedInSpatialStructure_type = new entity("IfcRelReferencedInSpatialStructure", 710, IfcRelConnects_type);
    IfcRelSchedulesCostItems_type = new entity("IfcRelSchedulesCostItems", 711, IfcRelAssignsToControl_type);
    IfcRelSequence_type = new entity("IfcRelSequence", 712, IfcRelConnects_type);
    IfcRelServicesBuildings_type = new entity("IfcRelServicesBuildings", 713, IfcRelConnects_type);
    IfcRelSpaceBoundary_type = new entity("IfcRelSpaceBoundary", 714, IfcRelConnects_type);
    IfcRelVoidsElement_type = new entity("IfcRelVoidsElement", 715, IfcRelConnects_type);
    IfcResource_type = new entity("IfcResource", 722, IfcObject_type);
    IfcRevolvedAreaSolid_type = new entity("IfcRevolvedAreaSolid", 724, IfcSweptAreaSolid_type);
    IfcRightCircularCone_type = new entity("IfcRightCircularCone", 727, IfcCsgPrimitive3D_type);
    IfcRightCircularCylinder_type = new entity("IfcRightCircularCylinder", 728, IfcCsgPrimitive3D_type);
    IfcSpatialStructureElement_type = new entity("IfcSpatialStructureElement", 786, IfcProduct_type);
    IfcSpatialStructureElementType_type = new entity("IfcSpatialStructureElementType", 787, IfcElementType_type);
    IfcSphere_type = new entity("IfcSphere", 792, IfcCsgPrimitive3D_type);
    IfcStructuralActivity_type = new entity("IfcStructuralActivity", 802, IfcProduct_type);
    IfcStructuralItem_type = new entity("IfcStructuralItem", 811, IfcProduct_type);
    IfcStructuralMember_type = new entity("IfcStructuralMember", 824, IfcStructuralItem_type);
    IfcStructuralReaction_type = new entity("IfcStructuralReaction", 831, IfcStructuralActivity_type);
    IfcStructuralSurfaceMember_type = new entity("IfcStructuralSurfaceMember", 835, IfcStructuralMember_type);
    IfcStructuralSurfaceMemberVarying_type = new entity("IfcStructuralSurfaceMemberVarying", 836, IfcStructuralSurfaceMember_type);
    IfcStructuredDimensionCallout_type = new entity("IfcStructuredDimensionCallout", 838, IfcDraughtingCallout_type);
    IfcSurfaceCurveSweptAreaSolid_type = new entity("IfcSurfaceCurveSweptAreaSolid", 845, IfcSweptAreaSolid_type);
    IfcSurfaceOfLinearExtrusion_type = new entity("IfcSurfaceOfLinearExtrusion", 846, IfcSweptSurface_type);
    IfcSurfaceOfRevolution_type = new entity("IfcSurfaceOfRevolution", 847, IfcSweptSurface_type);
    IfcSystemFurnitureElementType_type = new entity("IfcSystemFurnitureElementType", 867, IfcFurnishingElementType_type);
    IfcTask_type = new entity("IfcTask", 873, IfcProcess_type);
    IfcTransportElementType_type = new entity("IfcTransportElementType", 923, IfcElementType_type);
    IfcActor_type = new entity("IfcActor", 6, IfcObject_type);
    IfcAnnotation_type = new entity("IfcAnnotation", 27, IfcProduct_type);
    IfcAsymmetricIShapeProfileDef_type = new entity("IfcAsymmetricIShapeProfileDef", 51, IfcIShapeProfileDef_type);
    IfcBlock_type = new entity("IfcBlock", 64, IfcCsgPrimitive3D_type);
    IfcBooleanClippingResult_type = new entity("IfcBooleanClippingResult", 68, IfcBooleanResult_type);
    IfcBoundedCurve_type = new entity("IfcBoundedCurve", 77, IfcCurve_type);
    IfcBuilding_type = new entity("IfcBuilding", 82, IfcSpatialStructureElement_type);
    IfcBuildingElementType_type = new entity("IfcBuildingElementType", 89, IfcElementType_type);
    IfcBuildingStorey_type = new entity("IfcBuildingStorey", 90, IfcSpatialStructureElement_type);
    IfcCircleHollowProfileDef_type = new entity("IfcCircleHollowProfileDef", 112, IfcCircleProfileDef_type);
    IfcColumnType_type = new entity("IfcColumnType", 129, IfcBuildingElementType_type);
    IfcCompositeCurve_type = new entity("IfcCompositeCurve", 133, IfcBoundedCurve_type);
    IfcConic_type = new entity("IfcConic", 144, IfcCurve_type);
    IfcConstructionResource_type = new entity("IfcConstructionResource", 161, IfcResource_type);
    IfcControl_type = new entity("IfcControl", 164, IfcObject_type);
    IfcCostItem_type = new entity("IfcCostItem", 173, IfcControl_type);
    IfcCostSchedule_type = new entity("IfcCostSchedule", 174, IfcControl_type);
    IfcCoveringType_type = new entity("IfcCoveringType", 179, IfcBuildingElementType_type);
    IfcCrewResource_type = new entity("IfcCrewResource", 183, IfcConstructionResource_type);
    IfcCurtainWallType_type = new entity("IfcCurtainWallType", 190, IfcBuildingElementType_type);
    IfcDimensionCurveDirectedCallout_type = new entity("IfcDimensionCurveDirectedCallout", 221, IfcDraughtingCallout_type);
    IfcDistributionElementType_type = new entity("IfcDistributionElementType", 236, IfcElementType_type);
    IfcDistributionFlowElementType_type = new entity("IfcDistributionFlowElementType", 238, IfcDistributionElementType_type);
    IfcElectricalBaseProperties_type = new entity("IfcElectricalBaseProperties", 294, IfcEnergyProperties_type);
    IfcElement_type = new entity("IfcElement", 297, IfcProduct_type);
    IfcElementAssembly_type = new entity("IfcElementAssembly", 298, IfcElement_type);
    IfcElementComponent_type = new entity("IfcElementComponent", 300, IfcElement_type);
    IfcElementComponentType_type = new entity("IfcElementComponentType", 301, IfcElementType_type);
    IfcEllipse_type = new entity("IfcEllipse", 306, IfcConic_type);
    IfcEnergyConversionDeviceType_type = new entity("IfcEnergyConversionDeviceType", 309, IfcDistributionFlowElementType_type);
    IfcEquipmentElement_type = new entity("IfcEquipmentElement", 315, IfcElement_type);
    IfcEquipmentStandard_type = new entity("IfcEquipmentStandard", 316, IfcControl_type);
    IfcEvaporativeCoolerType_type = new entity("IfcEvaporativeCoolerType", 317, IfcEnergyConversionDeviceType_type);
    IfcEvaporatorType_type = new entity("IfcEvaporatorType", 319, IfcEnergyConversionDeviceType_type);
    IfcFacetedBrep_type = new entity("IfcFacetedBrep", 333, IfcManifoldSolidBrep_type);
    IfcFacetedBrepWithVoids_type = new entity("IfcFacetedBrepWithVoids", 334, IfcManifoldSolidBrep_type);
    IfcFastener_type = new entity("IfcFastener", 338, IfcElementComponent_type);
    IfcFastenerType_type = new entity("IfcFastenerType", 339, IfcElementComponentType_type);
    IfcFeatureElement_type = new entity("IfcFeatureElement", 340, IfcElement_type);
    IfcFeatureElementAddition_type = new entity("IfcFeatureElementAddition", 341, IfcFeatureElement_type);
    IfcFeatureElementSubtraction_type = new entity("IfcFeatureElementSubtraction", 342, IfcFeatureElement_type);
    IfcFlowControllerType_type = new entity("IfcFlowControllerType", 354, IfcDistributionFlowElementType_type);
    IfcFlowFittingType_type = new entity("IfcFlowFittingType", 357, IfcDistributionFlowElementType_type);
    IfcFlowMeterType_type = new entity("IfcFlowMeterType", 360, IfcFlowControllerType_type);
    IfcFlowMovingDeviceType_type = new entity("IfcFlowMovingDeviceType", 363, IfcDistributionFlowElementType_type);
    IfcFlowSegmentType_type = new entity("IfcFlowSegmentType", 365, IfcDistributionFlowElementType_type);
    IfcFlowStorageDeviceType_type = new entity("IfcFlowStorageDeviceType", 367, IfcDistributionFlowElementType_type);
    IfcFlowTerminalType_type = new entity("IfcFlowTerminalType", 369, IfcDistributionFlowElementType_type);
    IfcFlowTreatmentDeviceType_type = new entity("IfcFlowTreatmentDeviceType", 371, IfcDistributionFlowElementType_type);
    IfcFurnishingElement_type = new entity("IfcFurnishingElement", 381, IfcElement_type);
    IfcFurnitureStandard_type = new entity("IfcFurnitureStandard", 383, IfcControl_type);
    IfcGasTerminalType_type = new entity("IfcGasTerminalType", 385, IfcFlowTerminalType_type);
    IfcGrid_type = new entity("IfcGrid", 398, IfcProduct_type);
    IfcGroup_type = new entity("IfcGroup", 401, IfcObject_type);
    IfcHeatExchangerType_type = new entity("IfcHeatExchangerType", 404, IfcEnergyConversionDeviceType_type);
    IfcHumidifierType_type = new entity("IfcHumidifierType", 409, IfcEnergyConversionDeviceType_type);
    IfcInventory_type = new entity("IfcInventory", 420, IfcGroup_type);
    IfcJunctionBoxType_type = new entity("IfcJunctionBoxType", 426, IfcFlowFittingType_type);
    IfcLaborResource_type = new entity("IfcLaborResource", 431, IfcConstructionResource_type);
    IfcLampType_type = new entity("IfcLampType", 432, IfcFlowTerminalType_type);
    IfcLightFixtureType_type = new entity("IfcLightFixtureType", 444, IfcFlowTerminalType_type);
    IfcLinearDimension_type = new entity("IfcLinearDimension", 454, IfcDimensionCurveDirectedCallout_type);
    IfcMechanicalFastener_type = new entity("IfcMechanicalFastener", 488, IfcFastener_type);
    IfcMechanicalFastenerType_type = new entity("IfcMechanicalFastenerType", 489, IfcFastenerType_type);
    IfcMemberType_type = new entity("IfcMemberType", 493, IfcBuildingElementType_type);
    IfcMotorConnectionType_type = new entity("IfcMotorConnectionType", 508, IfcEnergyConversionDeviceType_type);
    IfcMove_type = new entity("IfcMove", 510, IfcTask_type);
    IfcOccupant_type = new entity("IfcOccupant", 522, IfcActor_type);
    IfcOpeningElement_type = new entity("IfcOpeningElement", 528, IfcFeatureElementSubtraction_type);
    IfcOrderAction_type = new entity("IfcOrderAction", 530, IfcTask_type);
    IfcOutletType_type = new entity("IfcOutletType", 535, IfcFlowTerminalType_type);
    IfcPerformanceHistory_type = new entity("IfcPerformanceHistory", 542, IfcControl_type);
    IfcPermit_type = new entity("IfcPermit", 545, IfcControl_type);
    IfcPipeFittingType_type = new entity("IfcPipeFittingType", 555, IfcFlowFittingType_type);
    IfcPipeSegmentType_type = new entity("IfcPipeSegmentType", 557, IfcFlowSegmentType_type);
    IfcPlateType_type = new entity("IfcPlateType", 567, IfcBuildingElementType_type);
    IfcPolyline_type = new entity("IfcPolyline", 575, IfcBoundedCurve_type);
    IfcPort_type = new entity("IfcPort", 576, IfcProduct_type);
    IfcProcedure_type = new entity("IfcProcedure", 597, IfcProcess_type);
    IfcProjectOrder_type = new entity("IfcProjectOrder", 608, IfcControl_type);
    IfcProjectOrderRecord_type = new entity("IfcProjectOrderRecord", 609, IfcControl_type);
    IfcProjectionElement_type = new entity("IfcProjectionElement", 614, IfcFeatureElementAddition_type);
    IfcProtectiveDeviceType_type = new entity("IfcProtectiveDeviceType", 629, IfcFlowControllerType_type);
    IfcPumpType_type = new entity("IfcPumpType", 632, IfcFlowMovingDeviceType_type);
    IfcRadiusDimension_type = new entity("IfcRadiusDimension", 641, IfcDimensionCurveDirectedCallout_type);
    IfcRailingType_type = new entity("IfcRailingType", 643, IfcBuildingElementType_type);
    IfcRampFlightType_type = new entity("IfcRampFlightType", 647, IfcBuildingElementType_type);
    IfcRelAggregates_type = new entity("IfcRelAggregates", 667, IfcRelDecomposes_type);
    IfcRelAssignsTasks_type = new entity("IfcRelAssignsTasks", 669, IfcRelAssignsToControl_type);
    IfcSanitaryTerminalType_type = new entity("IfcSanitaryTerminalType", 741, IfcFlowTerminalType_type);
    IfcScheduleTimeControl_type = new entity("IfcScheduleTimeControl", 743, IfcControl_type);
    IfcServiceLife_type = new entity("IfcServiceLife", 754, IfcControl_type);
    IfcSite_type = new entity("IfcSite", 766, IfcSpatialStructureElement_type);
    IfcSlabType_type = new entity("IfcSlabType", 769, IfcBuildingElementType_type);
    IfcSpace_type = new entity("IfcSpace", 779, IfcSpatialStructureElement_type);
    IfcSpaceHeaterType_type = new entity("IfcSpaceHeaterType", 780, IfcEnergyConversionDeviceType_type);
    IfcSpaceProgram_type = new entity("IfcSpaceProgram", 782, IfcControl_type);
    IfcSpaceType_type = new entity("IfcSpaceType", 784, IfcSpatialStructureElementType_type);
    IfcStackTerminalType_type = new entity("IfcStackTerminalType", 793, IfcFlowTerminalType_type);
    IfcStairFlightType_type = new entity("IfcStairFlightType", 797, IfcBuildingElementType_type);
    IfcStructuralAction_type = new entity("IfcStructuralAction", 801, IfcStructuralActivity_type);
    IfcStructuralConnection_type = new entity("IfcStructuralConnection", 805, IfcStructuralItem_type);
    IfcStructuralCurveConnection_type = new entity("IfcStructuralCurveConnection", 807, IfcStructuralConnection_type);
    IfcStructuralCurveMember_type = new entity("IfcStructuralCurveMember", 808, IfcStructuralMember_type);
    IfcStructuralCurveMemberVarying_type = new entity("IfcStructuralCurveMemberVarying", 809, IfcStructuralCurveMember_type);
    IfcStructuralLinearAction_type = new entity("IfcStructuralLinearAction", 812, IfcStructuralAction_type);
    IfcStructuralLinearActionVarying_type = new entity("IfcStructuralLinearActionVarying", 813, IfcStructuralLinearAction_type);
    IfcStructuralLoadGroup_type = new entity("IfcStructuralLoadGroup", 815, IfcGroup_type);
    IfcStructuralPlanarAction_type = new entity("IfcStructuralPlanarAction", 825, IfcStructuralAction_type);
    IfcStructuralPlanarActionVarying_type = new entity("IfcStructuralPlanarActionVarying", 826, IfcStructuralPlanarAction_type);
    IfcStructuralPointAction_type = new entity("IfcStructuralPointAction", 827, IfcStructuralAction_type);
    IfcStructuralPointConnection_type = new entity("IfcStructuralPointConnection", 828, IfcStructuralConnection_type);
    IfcStructuralPointReaction_type = new entity("IfcStructuralPointReaction", 829, IfcStructuralReaction_type);
    IfcStructuralResultGroup_type = new entity("IfcStructuralResultGroup", 832, IfcGroup_type);
    IfcStructuralSurfaceConnection_type = new entity("IfcStructuralSurfaceConnection", 834, IfcStructuralConnection_type);
    IfcSubContractResource_type = new entity("IfcSubContractResource", 842, IfcConstructionResource_type);
    IfcSwitchingDeviceType_type = new entity("IfcSwitchingDeviceType", 862, IfcFlowControllerType_type);
    IfcSystem_type = new entity("IfcSystem", 866, IfcGroup_type);
    IfcTankType_type = new entity("IfcTankType", 871, IfcFlowStorageDeviceType_type);
    IfcTimeSeriesSchedule_type = new entity("IfcTimeSeriesSchedule", 912, IfcControl_type);
    IfcTransformerType_type = new entity("IfcTransformerType", 919, IfcEnergyConversionDeviceType_type);
    IfcTransportElement_type = new entity("IfcTransportElement", 922, IfcElement_type);
    IfcTrimmedCurve_type = new entity("IfcTrimmedCurve", 926, IfcBoundedCurve_type);
    IfcTubeBundleType_type = new entity("IfcTubeBundleType", 929, IfcEnergyConversionDeviceType_type);
    IfcUnitaryEquipmentType_type = new entity("IfcUnitaryEquipmentType", 938, IfcEnergyConversionDeviceType_type);
    IfcValveType_type = new entity("IfcValveType", 941, IfcFlowControllerType_type);
    IfcVirtualElement_type = new entity("IfcVirtualElement", 952, IfcElement_type);
    IfcWallType_type = new entity("IfcWallType", 958, IfcBuildingElementType_type);
    IfcWasteTerminalType_type = new entity("IfcWasteTerminalType", 962, IfcFlowTerminalType_type);
    IfcWorkControl_type = new entity("IfcWorkControl", 973, IfcControl_type);
    IfcWorkPlan_type = new entity("IfcWorkPlan", 975, IfcWorkControl_type);
    IfcWorkSchedule_type = new entity("IfcWorkSchedule", 976, IfcWorkControl_type);
    IfcZone_type = new entity("IfcZone", 979, IfcGroup_type);
    Ifc2DCompositeCurve_type = new entity("Ifc2DCompositeCurve", 0, IfcCompositeCurve_type);
    IfcActionRequest_type = new entity("IfcActionRequest", 3, IfcControl_type);
    IfcAirTerminalBoxType_type = new entity("IfcAirTerminalBoxType", 14, IfcFlowControllerType_type);
    IfcAirTerminalType_type = new entity("IfcAirTerminalType", 16, IfcFlowTerminalType_type);
    IfcAirToAirHeatRecoveryType_type = new entity("IfcAirToAirHeatRecoveryType", 18, IfcEnergyConversionDeviceType_type);
    IfcAngularDimension_type = new entity("IfcAngularDimension", 25, IfcDimensionCurveDirectedCallout_type);
    IfcAsset_type = new entity("IfcAsset", 50, IfcGroup_type);
    IfcBSplineCurve_type = new entity("IfcBSplineCurve", 56, IfcBoundedCurve_type);
    IfcBeamType_type = new entity("IfcBeamType", 59, IfcBuildingElementType_type);
    IfcBezierCurve_type = new entity("IfcBezierCurve", 62, IfcBSplineCurve_type);
    IfcBoilerType_type = new entity("IfcBoilerType", 65, IfcEnergyConversionDeviceType_type);
    IfcBuildingElement_type = new entity("IfcBuildingElement", 83, IfcElement_type);
    IfcBuildingElementComponent_type = new entity("IfcBuildingElementComponent", 84, IfcBuildingElement_type);
    IfcBuildingElementPart_type = new entity("IfcBuildingElementPart", 85, IfcBuildingElementComponent_type);
    IfcBuildingElementProxy_type = new entity("IfcBuildingElementProxy", 86, IfcBuildingElement_type);
    IfcBuildingElementProxyType_type = new entity("IfcBuildingElementProxyType", 87, IfcBuildingElementType_type);
    IfcCableCarrierFittingType_type = new entity("IfcCableCarrierFittingType", 92, IfcFlowFittingType_type);
    IfcCableCarrierSegmentType_type = new entity("IfcCableCarrierSegmentType", 94, IfcFlowSegmentType_type);
    IfcCableSegmentType_type = new entity("IfcCableSegmentType", 96, IfcFlowSegmentType_type);
    IfcChillerType_type = new entity("IfcChillerType", 109, IfcEnergyConversionDeviceType_type);
    IfcCircle_type = new entity("IfcCircle", 111, IfcConic_type);
    IfcCoilType_type = new entity("IfcCoilType", 122, IfcEnergyConversionDeviceType_type);
    IfcColumn_type = new entity("IfcColumn", 128, IfcBuildingElement_type);
    IfcCompressorType_type = new entity("IfcCompressorType", 137, IfcFlowMovingDeviceType_type);
    IfcCondenserType_type = new entity("IfcCondenserType", 139, IfcEnergyConversionDeviceType_type);
    IfcCondition_type = new entity("IfcCondition", 141, IfcGroup_type);
    IfcConditionCriterion_type = new entity("IfcConditionCriterion", 142, IfcControl_type);
    IfcConstructionEquipmentResource_type = new entity("IfcConstructionEquipmentResource", 158, IfcConstructionResource_type);
    IfcConstructionMaterialResource_type = new entity("IfcConstructionMaterialResource", 159, IfcConstructionResource_type);
    IfcConstructionProductResource_type = new entity("IfcConstructionProductResource", 160, IfcConstructionResource_type);
    IfcCooledBeamType_type = new entity("IfcCooledBeamType", 168, IfcEnergyConversionDeviceType_type);
    IfcCoolingTowerType_type = new entity("IfcCoolingTowerType", 170, IfcEnergyConversionDeviceType_type);
    IfcCovering_type = new entity("IfcCovering", 178, IfcBuildingElement_type);
    IfcCurtainWall_type = new entity("IfcCurtainWall", 189, IfcBuildingElement_type);
    IfcDamperType_type = new entity("IfcDamperType", 202, IfcFlowControllerType_type);
    IfcDiameterDimension_type = new entity("IfcDiameterDimension", 217, IfcDimensionCurveDirectedCallout_type);
    IfcDiscreteAccessory_type = new entity("IfcDiscreteAccessory", 228, IfcElementComponent_type);
    IfcDiscreteAccessoryType_type = new entity("IfcDiscreteAccessoryType", 229, IfcElementComponentType_type);
    IfcDistributionChamberElementType_type = new entity("IfcDistributionChamberElementType", 231, IfcDistributionFlowElementType_type);
    IfcDistributionControlElementType_type = new entity("IfcDistributionControlElementType", 234, IfcDistributionElementType_type);
    IfcDistributionElement_type = new entity("IfcDistributionElement", 235, IfcElement_type);
    IfcDistributionFlowElement_type = new entity("IfcDistributionFlowElement", 237, IfcDistributionElement_type);
    IfcDistributionPort_type = new entity("IfcDistributionPort", 239, IfcPort_type);
    IfcDoor_type = new entity("IfcDoor", 247, IfcBuildingElement_type);
    IfcDuctFittingType_type = new entity("IfcDuctFittingType", 262, IfcFlowFittingType_type);
    IfcDuctSegmentType_type = new entity("IfcDuctSegmentType", 264, IfcFlowSegmentType_type);
    IfcDuctSilencerType_type = new entity("IfcDuctSilencerType", 266, IfcFlowTreatmentDeviceType_type);
    IfcEdgeFeature_type = new entity("IfcEdgeFeature", 271, IfcFeatureElementSubtraction_type);
    IfcElectricApplianceType_type = new entity("IfcElectricApplianceType", 273, IfcFlowTerminalType_type);
    IfcElectricFlowStorageDeviceType_type = new entity("IfcElectricFlowStorageDeviceType", 282, IfcFlowStorageDeviceType_type);
    IfcElectricGeneratorType_type = new entity("IfcElectricGeneratorType", 284, IfcEnergyConversionDeviceType_type);
    IfcElectricHeaterType_type = new entity("IfcElectricHeaterType", 286, IfcFlowTerminalType_type);
    IfcElectricMotorType_type = new entity("IfcElectricMotorType", 288, IfcEnergyConversionDeviceType_type);
    IfcElectricTimeControlType_type = new entity("IfcElectricTimeControlType", 291, IfcFlowControllerType_type);
    IfcElectricalCircuit_type = new entity("IfcElectricalCircuit", 295, IfcSystem_type);
    IfcElectricalElement_type = new entity("IfcElectricalElement", 296, IfcElement_type);
    IfcEnergyConversionDevice_type = new entity("IfcEnergyConversionDevice", 308, IfcDistributionFlowElement_type);
    IfcFanType_type = new entity("IfcFanType", 336, IfcFlowMovingDeviceType_type);
    IfcFilterType_type = new entity("IfcFilterType", 349, IfcFlowTreatmentDeviceType_type);
    IfcFireSuppressionTerminalType_type = new entity("IfcFireSuppressionTerminalType", 351, IfcFlowTerminalType_type);
    IfcFlowController_type = new entity("IfcFlowController", 353, IfcDistributionFlowElement_type);
    IfcFlowFitting_type = new entity("IfcFlowFitting", 356, IfcDistributionFlowElement_type);
    IfcFlowInstrumentType_type = new entity("IfcFlowInstrumentType", 358, IfcDistributionControlElementType_type);
    IfcFlowMovingDevice_type = new entity("IfcFlowMovingDevice", 362, IfcDistributionFlowElement_type);
    IfcFlowSegment_type = new entity("IfcFlowSegment", 364, IfcDistributionFlowElement_type);
    IfcFlowStorageDevice_type = new entity("IfcFlowStorageDevice", 366, IfcDistributionFlowElement_type);
    IfcFlowTerminal_type = new entity("IfcFlowTerminal", 368, IfcDistributionFlowElement_type);
    IfcFlowTreatmentDevice_type = new entity("IfcFlowTreatmentDevice", 370, IfcDistributionFlowElement_type);
    IfcFooting_type = new entity("IfcFooting", 376, IfcBuildingElement_type);
    IfcMember_type = new entity("IfcMember", 492, IfcBuildingElement_type);
    IfcPile_type = new entity("IfcPile", 552, IfcBuildingElement_type);
    IfcPlate_type = new entity("IfcPlate", 566, IfcBuildingElement_type);
    IfcRailing_type = new entity("IfcRailing", 642, IfcBuildingElement_type);
    IfcRamp_type = new entity("IfcRamp", 645, IfcBuildingElement_type);
    IfcRampFlight_type = new entity("IfcRampFlight", 646, IfcBuildingElement_type);
    IfcRationalBezierCurve_type = new entity("IfcRationalBezierCurve", 651, IfcBezierCurve_type);
    IfcReinforcingElement_type = new entity("IfcReinforcingElement", 665, IfcBuildingElementComponent_type);
    IfcReinforcingMesh_type = new entity("IfcReinforcingMesh", 666, IfcReinforcingElement_type);
    IfcRoof_type = new entity("IfcRoof", 730, IfcBuildingElement_type);
    IfcRoundedEdgeFeature_type = new entity("IfcRoundedEdgeFeature", 736, IfcEdgeFeature_type);
    IfcSensorType_type = new entity("IfcSensorType", 751, IfcDistributionControlElementType_type);
    IfcSlab_type = new entity("IfcSlab", 768, IfcBuildingElement_type);
    IfcStair_type = new entity("IfcStair", 795, IfcBuildingElement_type);
    IfcStairFlight_type = new entity("IfcStairFlight", 796, IfcBuildingElement_type);
    IfcStructuralAnalysisModel_type = new entity("IfcStructuralAnalysisModel", 804, IfcSystem_type);
    IfcTendon_type = new entity("IfcTendon", 876, IfcReinforcingElement_type);
    IfcTendonAnchor_type = new entity("IfcTendonAnchor", 877, IfcReinforcingElement_type);
    IfcVibrationIsolatorType_type = new entity("IfcVibrationIsolatorType", 950, IfcDiscreteAccessoryType_type);
    IfcWall_type = new entity("IfcWall", 956, IfcBuildingElement_type);
    IfcWallStandardCase_type = new entity("IfcWallStandardCase", 957, IfcWall_type);
    IfcWindow_type = new entity("IfcWindow", 965, IfcBuildingElement_type);
    IfcActuatorType_type = new entity("IfcActuatorType", 9, IfcDistributionControlElementType_type);
    IfcAlarmType_type = new entity("IfcAlarmType", 20, IfcDistributionControlElementType_type);
    IfcBeam_type = new entity("IfcBeam", 58, IfcBuildingElement_type);
    IfcChamferEdgeFeature_type = new entity("IfcChamferEdgeFeature", 106, IfcEdgeFeature_type);
    IfcControllerType_type = new entity("IfcControllerType", 165, IfcDistributionControlElementType_type);
    IfcDistributionChamberElement_type = new entity("IfcDistributionChamberElement", 230, IfcDistributionFlowElement_type);
    IfcDistributionControlElement_type = new entity("IfcDistributionControlElement", 233, IfcDistributionElement_type);
    IfcElectricDistributionPoint_type = new entity("IfcElectricDistributionPoint", 280, IfcFlowController_type);
    IfcReinforcingBar_type = new entity("IfcReinforcingBar", 662, IfcReinforcingElement_type);
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcOrganization_type);
        items.push_back(IfcPerson_type);
        items.push_back(IfcPersonAndOrganization_type);
        IfcActorSelect_type = new select_type("IfcActorSelect", 8, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcMeasureWithUnit_type);
        items.push_back(IfcMonetaryMeasure_type);
        items.push_back(IfcRatioMeasure_type);
        IfcAppliedValueSelect_type = new select_type("IfcAppliedValueSelect", 39, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcAxis2Placement2D_type);
        items.push_back(IfcAxis2Placement3D_type);
        IfcAxis2Placement_type = new select_type("IfcAxis2Placement", 53, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IfcBooleanResult_type);
        items.push_back(IfcCsgPrimitive3D_type);
        items.push_back(IfcHalfSpaceSolid_type);
        items.push_back(IfcSolidModel_type);
        IfcBooleanOperand_type = new select_type("IfcBooleanOperand", 69, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IfcTextStyleForDefinedFont_type);
        IfcCharacterStyleSelect_type = new select_type("IfcCharacterStyleSelect", 108, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClassificationNotation_type);
        items.push_back(IfcClassificationReference_type);
        IfcClassificationNotationSelect_type = new select_type("IfcClassificationNotationSelect", 119, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcColourSpecification_type);
        items.push_back(IfcPreDefinedColour_type);
        IfcColour_type = new select_type("IfcColour", 124, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcColourRgb_type);
        items.push_back(IfcNormalisedRatioMeasure_type);
        IfcColourOrFactor_type = new select_type("IfcColourOrFactor", 125, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcLabel_type);
        items.push_back(IfcMeasureWithUnit_type);
        IfcConditionCriterionSelect_type = new select_type("IfcConditionCriterionSelect", 143, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBooleanResult_type);
        items.push_back(IfcCsgPrimitive3D_type);
        IfcCsgSelect_type = new select_type("IfcCsgSelect", 185, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcBoundedCurve_type);
        items.push_back(IfcEdgeCurve_type);
        IfcCurveOrEdgeCurve_type = new select_type("IfcCurveOrEdgeCurve", 196, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCurveStyleFont_type);
        items.push_back(IfcPreDefinedCurveFont_type);
        IfcCurveStyleFontSelect_type = new select_type("IfcCurveStyleFontSelect", 201, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcCalendarDate_type);
        items.push_back(IfcDateAndTime_type);
        items.push_back(IfcLocalTime_type);
        IfcDateTimeSelect_type = new select_type("IfcDateTimeSelect", 206, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternallyDefinedSymbol_type);
        items.push_back(IfcPreDefinedSymbol_type);
        IfcDefinedSymbolSelect_type = new select_type("IfcDefinedSymbolSelect", 210, items);
    }
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
        IfcDerivedMeasureValue_type = new select_type("IfcDerivedMeasureValue", 211, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDocumentInformation_type);
        items.push_back(IfcDocumentReference_type);
        IfcDocumentSelect_type = new select_type("IfcDocumentSelect", 245, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcAnnotationCurveOccurrence_type);
        items.push_back(IfcAnnotationSymbolOccurrence_type);
        items.push_back(IfcAnnotationTextOccurrence_type);
        IfcDraughtingCalloutElement_type = new select_type("IfcDraughtingCalloutElement", 257, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IfcFillAreaStyleTileSymbolWithStyle_type);
        IfcFillAreaStyleTileShapeSelect_type = new select_type("IfcFillAreaStyleTileShapeSelect", 345, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(4);
        items.push_back(IfcColour_type);
        items.push_back(IfcExternallyDefinedHatchStyle_type);
        items.push_back(IfcFillAreaStyleHatching_type);
        items.push_back(IfcFillAreaStyleTiles_type);
        IfcFillStyleSelect_type = new select_type("IfcFillStyleSelect", 348, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcCurve_type);
        items.push_back(IfcPoint_type);
        items.push_back(IfcSurface_type);
        IfcGeometricSetSelect_type = new select_type("IfcGeometricSetSelect", 395, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcOneDirectionRepeatFactor_type);
        items.push_back(IfcPositiveLengthMeasure_type);
        IfcHatchLineDistanceSelect_type = new select_type("IfcHatchLineDistanceSelect", 403, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcRepresentation_type);
        items.push_back(IfcRepresentationItem_type);
        IfcLayeredItem_type = new select_type("IfcLayeredItem", 435, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcLibraryInformation_type);
        items.push_back(IfcLibraryReference_type);
        IfcLibrarySelect_type = new select_type("IfcLibrarySelect", 439, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternalReference_type);
        items.push_back(IfcLightIntensityDistribution_type);
        IfcLightDistributionDataSourceSelect_type = new select_type("IfcLightDistributionDataSourceSelect", 442, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IfcMaterial_type);
        items.push_back(IfcMaterialLayer_type);
        items.push_back(IfcMaterialLayerSet_type);
        items.push_back(IfcMaterialLayerSetUsage_type);
        items.push_back(IfcMaterialList_type);
        IfcMaterialSelect_type = new select_type("IfcMaterialSelect", 484, items);
    }
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
        IfcMeasureValue_type = new select_type("IfcMeasureValue", 485, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcCostValue_type);
        items.push_back(IfcDateTimeSelect_type);
        items.push_back(IfcMeasureWithUnit_type);
        items.push_back(IfcTable_type);
        items.push_back(IfcText_type);
        items.push_back(IfcTimeSeries_type);
        IfcMetricValueSelect_type = new select_type("IfcMetricValueSelect", 496, items);
    }
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
        IfcObjectReferenceSelect_type = new select_type("IfcObjectReferenceSelect", 518, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDirection_type);
        items.push_back(IfcPlaneAngleMeasure_type);
        IfcOrientationSelect_type = new select_type("IfcOrientationSelect", 533, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcPoint_type);
        items.push_back(IfcVertexPoint_type);
        IfcPointOrVertexPoint_type = new select_type("IfcPointOrVertexPoint", 572, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcCurveStyle_type);
        items.push_back(IfcFillAreaStyle_type);
        items.push_back(IfcNullStyle_type);
        items.push_back(IfcSurfaceStyle_type);
        items.push_back(IfcSymbolStyle_type);
        items.push_back(IfcTextStyle_type);
        IfcPresentationStyleSelect_type = new select_type("IfcPresentationStyleSelect", 595, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcClosedShell_type);
        items.push_back(IfcOpenShell_type);
        IfcShell_type = new select_type("IfcShell", 762, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(7);
        items.push_back(IfcBoolean_type);
        items.push_back(IfcIdentifier_type);
        items.push_back(IfcInteger_type);
        items.push_back(IfcLabel_type);
        items.push_back(IfcLogical_type);
        items.push_back(IfcReal_type);
        items.push_back(IfcText_type);
        IfcSimpleValue_type = new select_type("IfcSimpleValue", 765, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(6);
        items.push_back(IfcDescriptiveMeasure_type);
        items.push_back(IfcLengthMeasure_type);
        items.push_back(IfcNormalisedRatioMeasure_type);
        items.push_back(IfcPositiveLengthMeasure_type);
        items.push_back(IfcPositiveRatioMeasure_type);
        items.push_back(IfcRatioMeasure_type);
        IfcSizeSelect_type = new select_type("IfcSizeSelect", 767, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcSpecularExponent_type);
        items.push_back(IfcSpecularRoughness_type);
        IfcSpecularHighlightSelect_type = new select_type("IfcSpecularHighlightSelect", 790, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcElement_type);
        items.push_back(IfcStructuralItem_type);
        IfcStructuralActivityAssignmentSelect_type = new select_type("IfcStructuralActivityAssignmentSelect", 803, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcFaceBasedSurfaceModel_type);
        items.push_back(IfcFaceSurface_type);
        items.push_back(IfcSurface_type);
        IfcSurfaceOrFaceSurface_type = new select_type("IfcSurfaceOrFaceSurface", 848, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(5);
        items.push_back(IfcExternallyDefinedSurfaceStyle_type);
        items.push_back(IfcSurfaceStyleLighting_type);
        items.push_back(IfcSurfaceStyleRefraction_type);
        items.push_back(IfcSurfaceStyleShading_type);
        items.push_back(IfcSurfaceStyleWithTextures_type);
        IfcSurfaceStyleElementSelect_type = new select_type("IfcSurfaceStyleElementSelect", 851, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(1);
        items.push_back(IfcColour_type);
        IfcSymbolStyleSelect_type = new select_type("IfcSymbolStyleSelect", 865, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcExternallyDefinedTextFont_type);
        items.push_back(IfcPreDefinedTextFont_type);
        IfcTextFontSelect_type = new select_type("IfcTextFontSelect", 884, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcTextStyleTextModel_type);
        items.push_back(IfcTextStyleWithBoxCharacteristics_type);
        IfcTextStyleSelect_type = new select_type("IfcTextStyleSelect", 891, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCartesianPoint_type);
        items.push_back(IfcParameterValue_type);
        IfcTrimmingSelect_type = new select_type("IfcTrimmingSelect", 928, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcDerivedUnit_type);
        items.push_back(IfcMonetaryUnit_type);
        items.push_back(IfcNamedUnit_type);
        IfcUnit_type = new select_type("IfcUnit", 935, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(3);
        items.push_back(IfcDerivedMeasureValue_type);
        items.push_back(IfcMeasureValue_type);
        items.push_back(IfcSimpleValue_type);
        IfcValue_type = new select_type("IfcValue", 940, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcDirection_type);
        items.push_back(IfcVector_type);
        IfcVectorOrDirection_type = new select_type("IfcVectorOrDirection", 945, items);
    }
    {
        std::vector<const declaration*> items; items.reserve(2);
        items.push_back(IfcCurveStyleFontAndScaling_type);
        items.push_back(IfcCurveStyleFontSelect_type);
        IfcCurveFontOrScaledCurveFontSelect_type = new select_type("IfcCurveFontOrScaledCurveFontSelect", 195, items);
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
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsActingUpon", entity::inverse_attribute::set_type, 0, -1, IfcRelAssignsToActor_type, IfcRelAssignsToActor_type->attributes()[0]));
        IfcActor_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("OfPerson", entity::inverse_attribute::set_type, 0, -1, IfcPerson_type, IfcPerson_type->attributes()[7]));
        attributes.push_back(new entity::inverse_attribute("OfOrganization", entity::inverse_attribute::set_type, 0, -1, IfcOrganization_type, IfcOrganization_type->attributes()[4]));
        IfcAddress_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IfcRelContainedInSpatialStructure_type, IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IfcAnnotation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ValuesReferenced", entity::inverse_attribute::set_type, 0, -1, IfcReferencesValueDocument_type, IfcReferencesValueDocument_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ValueOfComponents", entity::inverse_attribute::set_type, 0, -1, IfcAppliedValueRelationship_type, IfcAppliedValueRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsComponentIn", entity::inverse_attribute::set_type, 0, -1, IfcAppliedValueRelationship_type, IfcAppliedValueRelationship_type->attributes()[1]));
        IfcAppliedValue_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("Actors", entity::inverse_attribute::set_type, 0, -1, IfcApprovalActorRelationship_type, IfcApprovalActorRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedWith", entity::inverse_attribute::set_type, 0, -1, IfcApprovalRelationship_type, IfcApprovalRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Relates", entity::inverse_attribute::set_type, 0, -1, IfcApprovalRelationship_type, IfcApprovalRelationship_type->attributes()[1]));
        IfcApproval_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Contains", entity::inverse_attribute::set_type, 0, -1, IfcClassificationItem_type, IfcClassificationItem_type->attributes()[1]));
        IfcClassification_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsClassifiedItemIn", entity::inverse_attribute::set_type, 0, 1, IfcClassificationItemRelationship_type, IfcClassificationItemRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsClassifyingItemIn", entity::inverse_attribute::set_type, 0, 1, IfcClassificationItemRelationship_type, IfcClassificationItemRelationship_type->attributes()[0]));
        IfcClassificationItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("UsingCurves", entity::inverse_attribute::set_type, 1, -1, IfcCompositeCurve_type, IfcCompositeCurve_type->attributes()[0]));
        IfcCompositeCurveSegment_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(6);
        attributes.push_back(new entity::inverse_attribute("ClassifiedAs", entity::inverse_attribute::set_type, 0, -1, IfcConstraintClassificationRelationship_type, IfcConstraintClassificationRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("RelatesConstraints", entity::inverse_attribute::set_type, 0, -1, IfcConstraintRelationship_type, IfcConstraintRelationship_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedWith", entity::inverse_attribute::set_type, 0, -1, IfcConstraintRelationship_type, IfcConstraintRelationship_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("PropertiesForConstraint", entity::inverse_attribute::set_type, 0, -1, IfcPropertyConstraintRelationship_type, IfcPropertyConstraintRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Aggregates", entity::inverse_attribute::set_type, 0, -1, IfcConstraintAggregationRelationship_type, IfcConstraintAggregationRelationship_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("IsAggregatedIn", entity::inverse_attribute::set_type, 0, -1, IfcConstraintAggregationRelationship_type, IfcConstraintAggregationRelationship_type->attributes()[3]));
        IfcConstraint_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Controls", entity::inverse_attribute::set_type, 0, -1, IfcRelAssignsToControl_type, IfcRelAssignsToControl_type->attributes()[0]));
        IfcControl_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("CoversSpaces", entity::inverse_attribute::set_type, 0, 1, IfcRelCoversSpaces_type, IfcRelCoversSpaces_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("Covers", entity::inverse_attribute::set_type, 0, 1, IfcRelCoversBldgElements_type, IfcRelCoversBldgElements_type->attributes()[1]));
        IfcCovering_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AnnotatedBySymbols", entity::inverse_attribute::set_type, 0, 2, IfcTerminatorSymbol_type, IfcTerminatorSymbol_type->attributes()[0]));
        IfcDimensionCurve_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedToFlowElement", entity::inverse_attribute::set_type, 0, 1, IfcRelFlowControlElements_type, IfcRelFlowControlElements_type->attributes()[0]));
        IfcDistributionControlElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasControlElements", entity::inverse_attribute::set_type, 0, 1, IfcRelFlowControlElements_type, IfcRelFlowControlElements_type->attributes()[1]));
        IfcDistributionFlowElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsPointedTo", entity::inverse_attribute::set_type, 0, -1, IfcDocumentInformationRelationship_type, IfcDocumentInformationRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsPointer", entity::inverse_attribute::set_type, 0, 1, IfcDocumentInformationRelationship_type, IfcDocumentInformationRelationship_type->attributes()[0]));
        IfcDocumentInformation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferenceToDocument", entity::inverse_attribute::set_type, 0, 1, IfcDocumentInformation_type, IfcDocumentInformation_type->attributes()[3]));
        IfcDocumentReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("IsRelatedFromCallout", entity::inverse_attribute::set_type, 0, -1, IfcDraughtingCalloutRelationship_type, IfcDraughtingCalloutRelationship_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("IsRelatedToCallout", entity::inverse_attribute::set_type, 0, -1, IfcDraughtingCalloutRelationship_type, IfcDraughtingCalloutRelationship_type->attributes()[2]));
        IfcDraughtingCallout_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(12);
        attributes.push_back(new entity::inverse_attribute("HasStructuralMember", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsStructuralElement_type, IfcRelConnectsStructuralElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("FillsVoids", entity::inverse_attribute::set_type, 0, 1, IfcRelFillsElement_type, IfcRelFillsElement_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedTo", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsElements_type, IfcRelConnectsElements_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasCoverings", entity::inverse_attribute::set_type, 0, -1, IfcRelCoversBldgElements_type, IfcRelCoversBldgElements_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasProjections", entity::inverse_attribute::set_type, 0, -1, IfcRelProjectsElement_type, IfcRelProjectsElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ReferencedInStructures", entity::inverse_attribute::set_type, 0, -1, IfcRelReferencedInSpatialStructure_type, IfcRelReferencedInSpatialStructure_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasPorts", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsPortToElement_type, IfcRelConnectsPortToElement_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasOpenings", entity::inverse_attribute::set_type, 0, -1, IfcRelVoidsElement_type, IfcRelVoidsElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsConnectionRealization", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsWithRealizingElements_type, IfcRelConnectsWithRealizingElements_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ProvidesBoundaries", entity::inverse_attribute::set_type, 0, -1, IfcRelSpaceBoundary_type, IfcRelSpaceBoundary_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedFrom", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsElements_type, IfcRelConnectsElements_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IfcRelContainedInSpatialStructure_type, IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IfcElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ProjectsElements", entity::inverse_attribute::unspecified_type, -1, -1, IfcRelProjectsElement_type, IfcRelProjectsElement_type->attributes()[1]));
        IfcFeatureElementAddition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("VoidsElements", entity::inverse_attribute::unspecified_type, -1, -1, IfcRelVoidsElement_type, IfcRelVoidsElement_type->attributes()[1]));
        IfcFeatureElementSubtraction_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasSubContexts", entity::inverse_attribute::set_type, 0, -1, IfcGeometricRepresentationSubContext_type, IfcGeometricRepresentationSubContext_type->attributes()[0]));
        IfcGeometricRepresentationContext_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ContainedInStructure", entity::inverse_attribute::set_type, 0, 1, IfcRelContainedInSpatialStructure_type, IfcRelContainedInSpatialStructure_type->attributes()[0]));
        IfcGrid_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::inverse_attribute("PartOfW", entity::inverse_attribute::set_type, 0, 1, IfcGrid_type, IfcGrid_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("PartOfV", entity::inverse_attribute::set_type, 0, 1, IfcGrid_type, IfcGrid_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PartOfU", entity::inverse_attribute::set_type, 0, 1, IfcGrid_type, IfcGrid_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("HasIntersections", entity::inverse_attribute::set_type, 0, -1, IfcVirtualGridIntersection_type, IfcVirtualGridIntersection_type->attributes()[0]));
        IfcGridAxis_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsGroupedBy", entity::inverse_attribute::unspecified_type, -1, -1, IfcRelAssignsToGroup_type, IfcRelAssignsToGroup_type->attributes()[0]));
        IfcGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferenceIntoLibrary", entity::inverse_attribute::set_type, 0, 1, IfcLibraryInformation_type, IfcLibraryInformation_type->attributes()[4]));
        IfcLibraryReference_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasRepresentation", entity::inverse_attribute::set_type, 0, 1, IfcMaterialDefinitionRepresentation_type, IfcMaterialDefinitionRepresentation_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ClassifiedAs", entity::inverse_attribute::set_type, 0, 1, IfcMaterialClassificationRelationship_type, IfcMaterialClassificationRelationship_type->attributes()[1]));
        IfcMaterial_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ToMaterialLayerSet", entity::inverse_attribute::unspecified_type, -1, -1, IfcMaterialLayerSet_type, IfcMaterialLayerSet_type->attributes()[0]));
        IfcMaterialLayer_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("IsDefinedBy", entity::inverse_attribute::set_type, 0, -1, IfcRelDefines_type, IfcRelDefines_type->attributes()[0]));
        IfcObject_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(4);
        attributes.push_back(new entity::inverse_attribute("HasAssignments", entity::inverse_attribute::set_type, 0, -1, IfcRelAssigns_type, IfcRelAssigns_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsDecomposedBy", entity::inverse_attribute::set_type, 0, -1, IfcRelDecomposes_type, IfcRelDecomposes_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("Decomposes", entity::inverse_attribute::set_type, 0, 1, IfcRelDecomposes_type, IfcRelDecomposes_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasAssociations", entity::inverse_attribute::set_type, 0, -1, IfcRelAssociates_type, IfcRelAssociates_type->attributes()[0]));
        IfcObjectDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("PlacesObject", entity::inverse_attribute::set_type, 1, 1, IfcProduct_type, IfcProduct_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ReferencedByPlacements", entity::inverse_attribute::set_type, 0, -1, IfcLocalPlacement_type, IfcLocalPlacement_type->attributes()[0]));
        IfcObjectPlacement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasFillings", entity::inverse_attribute::set_type, 0, -1, IfcRelFillsElement_type, IfcRelFillsElement_type->attributes()[0]));
        IfcOpeningElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("IsRelatedBy", entity::inverse_attribute::set_type, 0, -1, IfcOrganizationRelationship_type, IfcOrganizationRelationship_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("Relates", entity::inverse_attribute::set_type, 0, -1, IfcOrganizationRelationship_type, IfcOrganizationRelationship_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("Engages", entity::inverse_attribute::set_type, 0, -1, IfcPersonAndOrganization_type, IfcPersonAndOrganization_type->attributes()[1]));
        IfcOrganization_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("EngagedIn", entity::inverse_attribute::set_type, 0, -1, IfcPersonAndOrganization_type, IfcPersonAndOrganization_type->attributes()[0]));
        IfcPerson_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("PartOfComplex", entity::inverse_attribute::set_type, 0, 1, IfcPhysicalComplexQuantity_type, IfcPhysicalComplexQuantity_type->attributes()[0]));
        IfcPhysicalQuantity_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ContainedIn", entity::inverse_attribute::unspecified_type, -1, -1, IfcRelConnectsPortToElement_type, IfcRelConnectsPortToElement_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("ConnectedFrom", entity::inverse_attribute::set_type, 0, 1, IfcRelConnectsPorts_type, IfcRelConnectsPorts_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedTo", entity::inverse_attribute::set_type, 0, 1, IfcRelConnectsPorts_type, IfcRelConnectsPorts_type->attributes()[0]));
        IfcPort_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("OperatesOn", entity::inverse_attribute::set_type, 0, -1, IfcRelAssignsToProcess_type, IfcRelAssignsToProcess_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("IsSuccessorFrom", entity::inverse_attribute::set_type, 0, -1, IfcRelSequence_type, IfcRelSequence_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("IsPredecessorTo", entity::inverse_attribute::set_type, 0, -1, IfcRelSequence_type, IfcRelSequence_type->attributes()[0]));
        IfcProcess_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ReferencedBy", entity::inverse_attribute::set_type, 0, -1, IfcRelAssignsToProduct_type, IfcRelAssignsToProduct_type->attributes()[0]));
        IfcProduct_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("ShapeOfProduct", entity::inverse_attribute::set_type, 1, 1, IfcProduct_type, IfcProduct_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("HasShapeAspects", entity::inverse_attribute::set_type, 0, -1, IfcShapeAspect_type, IfcShapeAspect_type->attributes()[4]));
        IfcProductDefinitionShape_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("PropertyForDependance", entity::inverse_attribute::set_type, 0, -1, IfcPropertyDependencyRelationship_type, IfcPropertyDependencyRelationship_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("PropertyDependsOn", entity::inverse_attribute::set_type, 0, -1, IfcPropertyDependencyRelationship_type, IfcPropertyDependencyRelationship_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("PartOfComplex", entity::inverse_attribute::set_type, 0, 1, IfcComplexProperty_type, IfcComplexProperty_type->attributes()[1]));
        IfcProperty_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("HasAssociations", entity::inverse_attribute::set_type, 0, -1, IfcRelAssociates_type, IfcRelAssociates_type->attributes()[0]));
        IfcPropertyDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("PropertyDefinitionOf", entity::inverse_attribute::set_type, 0, 1, IfcRelDefinesByProperties_type, IfcRelDefinesByProperties_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("DefinesType", entity::inverse_attribute::set_type, 0, 1, IfcTypeObject_type, IfcTypeObject_type->attributes()[1]));
        IfcPropertySetDefinition_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("RepresentationMap", entity::inverse_attribute::set_type, 0, 1, IfcRepresentationMap_type, IfcRepresentationMap_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("LayerAssignments", entity::inverse_attribute::set_type, 0, -1, IfcPresentationLayerAssignment_type, IfcPresentationLayerAssignment_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("OfProductRepresentation", entity::inverse_attribute::set_type, 0, 1, IfcProductRepresentation_type, IfcProductRepresentation_type->attributes()[2]));
        IfcRepresentation_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("RepresentationsInContext", entity::inverse_attribute::set_type, 0, -1, IfcRepresentation_type, IfcRepresentation_type->attributes()[0]));
        IfcRepresentationContext_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("LayerAssignments", entity::inverse_attribute::set_type, 0, -1, IfcPresentationLayerAssignment_type, IfcPresentationLayerAssignment_type->attributes()[2]));
        attributes.push_back(new entity::inverse_attribute("StyledByItem", entity::inverse_attribute::set_type, 0, 1, IfcStyledItem_type, IfcStyledItem_type->attributes()[0]));
        IfcRepresentationItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("MapUsage", entity::inverse_attribute::set_type, 0, -1, IfcMappedItem_type, IfcMappedItem_type->attributes()[0]));
        IfcRepresentationMap_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ResourceOf", entity::inverse_attribute::set_type, 0, -1, IfcRelAssignsToResource_type, IfcRelAssignsToResource_type->attributes()[0]));
        IfcResource_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ScheduleTimeControlAssigned", entity::inverse_attribute::unspecified_type, -1, -1, IfcRelAssignsTasks_type, IfcRelAssignsTasks_type->attributes()[0]));
        IfcScheduleTimeControl_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("OfShapeAspect", entity::inverse_attribute::set_type, 0, 1, IfcShapeAspect_type, IfcShapeAspect_type->attributes()[0]));
        IfcShapeModel_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasCoverings", entity::inverse_attribute::set_type, 0, -1, IfcRelCoversSpaces_type, IfcRelCoversSpaces_type->attributes()[0]));
        attributes.push_back(new entity::inverse_attribute("BoundedBy", entity::inverse_attribute::set_type, 0, -1, IfcRelSpaceBoundary_type, IfcRelSpaceBoundary_type->attributes()[0]));
        IfcSpace_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("HasInteractionReqsFrom", entity::inverse_attribute::set_type, 0, -1, IfcRelInteractionRequirements_type, IfcRelInteractionRequirements_type->attributes()[3]));
        attributes.push_back(new entity::inverse_attribute("HasInteractionReqsTo", entity::inverse_attribute::set_type, 0, -1, IfcRelInteractionRequirements_type, IfcRelInteractionRequirements_type->attributes()[4]));
        IfcSpaceProgram_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(3);
        attributes.push_back(new entity::inverse_attribute("ReferencesElements", entity::inverse_attribute::set_type, 0, -1, IfcRelReferencedInSpatialStructure_type, IfcRelReferencedInSpatialStructure_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ServicedBySystems", entity::inverse_attribute::set_type, 0, -1, IfcRelServicesBuildings_type, IfcRelServicesBuildings_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ContainsElements", entity::inverse_attribute::set_type, 0, -1, IfcRelContainedInSpatialStructure_type, IfcRelContainedInSpatialStructure_type->attributes()[1]));
        IfcSpatialStructureElement_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedToStructuralItem", entity::inverse_attribute::unspecified_type, -1, -1, IfcRelConnectsStructuralActivity_type, IfcRelConnectsStructuralActivity_type->attributes()[1]));
        IfcStructuralActivity_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ConnectsStructuralMembers", entity::inverse_attribute::set_type, 1, -1, IfcRelConnectsStructuralMember_type, IfcRelConnectsStructuralMember_type->attributes()[1]));
        IfcStructuralConnection_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AssignedStructuralActivity", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsStructuralActivity_type, IfcRelConnectsStructuralActivity_type->attributes()[0]));
        IfcStructuralItem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("SourceOfResultGroup", entity::inverse_attribute::set_type, 0, 1, IfcStructuralResultGroup_type, IfcStructuralResultGroup_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("LoadGroupFor", entity::inverse_attribute::set_type, 0, -1, IfcStructuralAnalysisModel_type, IfcStructuralAnalysisModel_type->attributes()[2]));
        IfcStructuralLoadGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(2);
        attributes.push_back(new entity::inverse_attribute("ReferencesElement", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsStructuralElement_type, IfcRelConnectsStructuralElement_type->attributes()[1]));
        attributes.push_back(new entity::inverse_attribute("ConnectedBy", entity::inverse_attribute::set_type, 0, -1, IfcRelConnectsStructuralMember_type, IfcRelConnectsStructuralMember_type->attributes()[0]));
        IfcStructuralMember_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("Causes", entity::inverse_attribute::set_type, 0, -1, IfcStructuralAction_type, IfcStructuralAction_type->attributes()[1]));
        IfcStructuralReaction_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ResultGroupFor", entity::inverse_attribute::set_type, 0, 1, IfcStructuralAnalysisModel_type, IfcStructuralAnalysisModel_type->attributes()[3]));
        IfcStructuralResultGroup_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ServicesBuildings", entity::inverse_attribute::set_type, 0, 1, IfcRelServicesBuildings_type, IfcRelServicesBuildings_type->attributes()[0]));
        IfcSystem_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("OfTable", entity::inverse_attribute::unspecified_type, -1, -1, IfcTable_type, IfcTable_type->attributes()[1]));
        IfcTableRow_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("AnnotatedSurface", entity::inverse_attribute::set_type, 1, 1, IfcAnnotationSurface_type, IfcAnnotationSurface_type->attributes()[1]));
        IfcTextureCoordinate_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("DocumentedBy", entity::inverse_attribute::set_type, 0, 1, IfcTimeSeriesReferenceRelationship_type, IfcTimeSeriesReferenceRelationship_type->attributes()[0]));
        IfcTimeSeries_type->set_inverse_attributes(attributes);
    }
    {
        std::vector<const entity::inverse_attribute*> attributes; attributes.reserve(1);
        attributes.push_back(new entity::inverse_attribute("ObjectTypeOf", entity::inverse_attribute::set_type, 0, 1, IfcRelDefinesByType_type, IfcRelDefinesByType_type->attributes()[0]));
        IfcTypeObject_type->set_inverse_attributes(attributes);
    }

    std::vector<const declaration*> declarations; declarations.reserve(980);
    declarations.push_back(IfcAbsorbedDoseMeasure_type);
    declarations.push_back(IfcAccelerationMeasure_type);
    declarations.push_back(IfcAmountOfSubstanceMeasure_type);
    declarations.push_back(IfcAngularVelocityMeasure_type);
    declarations.push_back(IfcAreaMeasure_type);
    declarations.push_back(IfcBoolean_type);
    declarations.push_back(IfcComplexNumber_type);
    declarations.push_back(IfcCompoundPlaneAngleMeasure_type);
    declarations.push_back(IfcContextDependentMeasure_type);
    declarations.push_back(IfcCountMeasure_type);
    declarations.push_back(IfcCurvatureMeasure_type);
    declarations.push_back(IfcDayInMonthNumber_type);
    declarations.push_back(IfcDaylightSavingHour_type);
    declarations.push_back(IfcDescriptiveMeasure_type);
    declarations.push_back(IfcDimensionCount_type);
    declarations.push_back(IfcDoseEquivalentMeasure_type);
    declarations.push_back(IfcDynamicViscosityMeasure_type);
    declarations.push_back(IfcElectricCapacitanceMeasure_type);
    declarations.push_back(IfcElectricChargeMeasure_type);
    declarations.push_back(IfcElectricConductanceMeasure_type);
    declarations.push_back(IfcElectricCurrentMeasure_type);
    declarations.push_back(IfcElectricResistanceMeasure_type);
    declarations.push_back(IfcElectricVoltageMeasure_type);
    declarations.push_back(IfcEnergyMeasure_type);
    declarations.push_back(IfcFontStyle_type);
    declarations.push_back(IfcFontVariant_type);
    declarations.push_back(IfcFontWeight_type);
    declarations.push_back(IfcForceMeasure_type);
    declarations.push_back(IfcFrequencyMeasure_type);
    declarations.push_back(IfcGloballyUniqueId_type);
    declarations.push_back(IfcHeatFluxDensityMeasure_type);
    declarations.push_back(IfcHeatingValueMeasure_type);
    declarations.push_back(IfcHourInDay_type);
    declarations.push_back(IfcIdentifier_type);
    declarations.push_back(IfcIlluminanceMeasure_type);
    declarations.push_back(IfcInductanceMeasure_type);
    declarations.push_back(IfcInteger_type);
    declarations.push_back(IfcIntegerCountRateMeasure_type);
    declarations.push_back(IfcIonConcentrationMeasure_type);
    declarations.push_back(IfcIsothermalMoistureCapacityMeasure_type);
    declarations.push_back(IfcKinematicViscosityMeasure_type);
    declarations.push_back(IfcLabel_type);
    declarations.push_back(IfcLengthMeasure_type);
    declarations.push_back(IfcLinearForceMeasure_type);
    declarations.push_back(IfcLinearMomentMeasure_type);
    declarations.push_back(IfcLinearStiffnessMeasure_type);
    declarations.push_back(IfcLinearVelocityMeasure_type);
    declarations.push_back(IfcLogical_type);
    declarations.push_back(IfcLuminousFluxMeasure_type);
    declarations.push_back(IfcLuminousIntensityDistributionMeasure_type);
    declarations.push_back(IfcLuminousIntensityMeasure_type);
    declarations.push_back(IfcMagneticFluxDensityMeasure_type);
    declarations.push_back(IfcMagneticFluxMeasure_type);
    declarations.push_back(IfcMassDensityMeasure_type);
    declarations.push_back(IfcMassFlowRateMeasure_type);
    declarations.push_back(IfcMassMeasure_type);
    declarations.push_back(IfcMassPerLengthMeasure_type);
    declarations.push_back(IfcMinuteInHour_type);
    declarations.push_back(IfcModulusOfElasticityMeasure_type);
    declarations.push_back(IfcModulusOfLinearSubgradeReactionMeasure_type);
    declarations.push_back(IfcModulusOfRotationalSubgradeReactionMeasure_type);
    declarations.push_back(IfcModulusOfSubgradeReactionMeasure_type);
    declarations.push_back(IfcMoistureDiffusivityMeasure_type);
    declarations.push_back(IfcMolecularWeightMeasure_type);
    declarations.push_back(IfcMomentOfInertiaMeasure_type);
    declarations.push_back(IfcMonetaryMeasure_type);
    declarations.push_back(IfcMonthInYearNumber_type);
    declarations.push_back(IfcNumericMeasure_type);
    declarations.push_back(IfcPHMeasure_type);
    declarations.push_back(IfcParameterValue_type);
    declarations.push_back(IfcPlanarForceMeasure_type);
    declarations.push_back(IfcPlaneAngleMeasure_type);
    declarations.push_back(IfcPositiveLengthMeasure_type);
    declarations.push_back(IfcPositivePlaneAngleMeasure_type);
    declarations.push_back(IfcPowerMeasure_type);
    declarations.push_back(IfcPresentableText_type);
    declarations.push_back(IfcPressureMeasure_type);
    declarations.push_back(IfcRadioActivityMeasure_type);
    declarations.push_back(IfcRatioMeasure_type);
    declarations.push_back(IfcReal_type);
    declarations.push_back(IfcRotationalFrequencyMeasure_type);
    declarations.push_back(IfcRotationalMassMeasure_type);
    declarations.push_back(IfcRotationalStiffnessMeasure_type);
    declarations.push_back(IfcSecondInMinute_type);
    declarations.push_back(IfcSectionModulusMeasure_type);
    declarations.push_back(IfcSectionalAreaIntegralMeasure_type);
    declarations.push_back(IfcShearModulusMeasure_type);
    declarations.push_back(IfcSolidAngleMeasure_type);
    declarations.push_back(IfcSoundPowerMeasure_type);
    declarations.push_back(IfcSoundPressureMeasure_type);
    declarations.push_back(IfcSpecificHeatCapacityMeasure_type);
    declarations.push_back(IfcSpecularExponent_type);
    declarations.push_back(IfcSpecularRoughness_type);
    declarations.push_back(IfcTemperatureGradientMeasure_type);
    declarations.push_back(IfcText_type);
    declarations.push_back(IfcTextAlignment_type);
    declarations.push_back(IfcTextDecoration_type);
    declarations.push_back(IfcTextFontName_type);
    declarations.push_back(IfcTextTransformation_type);
    declarations.push_back(IfcThermalAdmittanceMeasure_type);
    declarations.push_back(IfcThermalConductivityMeasure_type);
    declarations.push_back(IfcThermalExpansionCoefficientMeasure_type);
    declarations.push_back(IfcThermalResistanceMeasure_type);
    declarations.push_back(IfcThermalTransmittanceMeasure_type);
    declarations.push_back(IfcThermodynamicTemperatureMeasure_type);
    declarations.push_back(IfcTimeMeasure_type);
    declarations.push_back(IfcTimeStamp_type);
    declarations.push_back(IfcTorqueMeasure_type);
    declarations.push_back(IfcVaporPermeabilityMeasure_type);
    declarations.push_back(IfcVolumeMeasure_type);
    declarations.push_back(IfcVolumetricFlowRateMeasure_type);
    declarations.push_back(IfcWarpingConstantMeasure_type);
    declarations.push_back(IfcWarpingMomentMeasure_type);
    declarations.push_back(IfcYearNumber_type);
    declarations.push_back(IfcBoxAlignment_type);
    declarations.push_back(IfcNormalisedRatioMeasure_type);
    declarations.push_back(IfcPositiveRatioMeasure_type);
    declarations.push_back(IfcActionSourceTypeEnum_type);
    declarations.push_back(IfcActionTypeEnum_type);
    declarations.push_back(IfcActuatorTypeEnum_type);
    declarations.push_back(IfcAddressTypeEnum_type);
    declarations.push_back(IfcAheadOrBehind_type);
    declarations.push_back(IfcAirTerminalBoxTypeEnum_type);
    declarations.push_back(IfcAirTerminalTypeEnum_type);
    declarations.push_back(IfcAirToAirHeatRecoveryTypeEnum_type);
    declarations.push_back(IfcAlarmTypeEnum_type);
    declarations.push_back(IfcAnalysisModelTypeEnum_type);
    declarations.push_back(IfcAnalysisTheoryTypeEnum_type);
    declarations.push_back(IfcArithmeticOperatorEnum_type);
    declarations.push_back(IfcAssemblyPlaceEnum_type);
    declarations.push_back(IfcBSplineCurveForm_type);
    declarations.push_back(IfcBeamTypeEnum_type);
    declarations.push_back(IfcBenchmarkEnum_type);
    declarations.push_back(IfcBoilerTypeEnum_type);
    declarations.push_back(IfcBooleanOperator_type);
    declarations.push_back(IfcBuildingElementProxyTypeEnum_type);
    declarations.push_back(IfcCableCarrierFittingTypeEnum_type);
    declarations.push_back(IfcCableCarrierSegmentTypeEnum_type);
    declarations.push_back(IfcCableSegmentTypeEnum_type);
    declarations.push_back(IfcChangeActionEnum_type);
    declarations.push_back(IfcChillerTypeEnum_type);
    declarations.push_back(IfcCoilTypeEnum_type);
    declarations.push_back(IfcColumnTypeEnum_type);
    declarations.push_back(IfcCompressorTypeEnum_type);
    declarations.push_back(IfcCondenserTypeEnum_type);
    declarations.push_back(IfcConnectionTypeEnum_type);
    declarations.push_back(IfcConstraintEnum_type);
    declarations.push_back(IfcControllerTypeEnum_type);
    declarations.push_back(IfcCooledBeamTypeEnum_type);
    declarations.push_back(IfcCoolingTowerTypeEnum_type);
    declarations.push_back(IfcCostScheduleTypeEnum_type);
    declarations.push_back(IfcCoveringTypeEnum_type);
    declarations.push_back(IfcCurrencyEnum_type);
    declarations.push_back(IfcCurtainWallTypeEnum_type);
    declarations.push_back(IfcDamperTypeEnum_type);
    declarations.push_back(IfcDataOriginEnum_type);
    declarations.push_back(IfcDerivedUnitEnum_type);
    declarations.push_back(IfcDimensionExtentUsage_type);
    declarations.push_back(IfcDirectionSenseEnum_type);
    declarations.push_back(IfcDistributionChamberElementTypeEnum_type);
    declarations.push_back(IfcDocumentConfidentialityEnum_type);
    declarations.push_back(IfcDocumentStatusEnum_type);
    declarations.push_back(IfcDoorPanelOperationEnum_type);
    declarations.push_back(IfcDoorPanelPositionEnum_type);
    declarations.push_back(IfcDoorStyleConstructionEnum_type);
    declarations.push_back(IfcDoorStyleOperationEnum_type);
    declarations.push_back(IfcDuctFittingTypeEnum_type);
    declarations.push_back(IfcDuctSegmentTypeEnum_type);
    declarations.push_back(IfcDuctSilencerTypeEnum_type);
    declarations.push_back(IfcElectricApplianceTypeEnum_type);
    declarations.push_back(IfcElectricCurrentEnum_type);
    declarations.push_back(IfcElectricDistributionPointFunctionEnum_type);
    declarations.push_back(IfcElectricFlowStorageDeviceTypeEnum_type);
    declarations.push_back(IfcElectricGeneratorTypeEnum_type);
    declarations.push_back(IfcElectricHeaterTypeEnum_type);
    declarations.push_back(IfcElectricMotorTypeEnum_type);
    declarations.push_back(IfcElectricTimeControlTypeEnum_type);
    declarations.push_back(IfcElementAssemblyTypeEnum_type);
    declarations.push_back(IfcElementCompositionEnum_type);
    declarations.push_back(IfcEnergySequenceEnum_type);
    declarations.push_back(IfcEnvironmentalImpactCategoryEnum_type);
    declarations.push_back(IfcEvaporativeCoolerTypeEnum_type);
    declarations.push_back(IfcEvaporatorTypeEnum_type);
    declarations.push_back(IfcFanTypeEnum_type);
    declarations.push_back(IfcFilterTypeEnum_type);
    declarations.push_back(IfcFireSuppressionTerminalTypeEnum_type);
    declarations.push_back(IfcFlowDirectionEnum_type);
    declarations.push_back(IfcFlowInstrumentTypeEnum_type);
    declarations.push_back(IfcFlowMeterTypeEnum_type);
    declarations.push_back(IfcFootingTypeEnum_type);
    declarations.push_back(IfcGasTerminalTypeEnum_type);
    declarations.push_back(IfcGeometricProjectionEnum_type);
    declarations.push_back(IfcGlobalOrLocalEnum_type);
    declarations.push_back(IfcHeatExchangerTypeEnum_type);
    declarations.push_back(IfcHumidifierTypeEnum_type);
    declarations.push_back(IfcInternalOrExternalEnum_type);
    declarations.push_back(IfcInventoryTypeEnum_type);
    declarations.push_back(IfcJunctionBoxTypeEnum_type);
    declarations.push_back(IfcLampTypeEnum_type);
    declarations.push_back(IfcLayerSetDirectionEnum_type);
    declarations.push_back(IfcLightDistributionCurveEnum_type);
    declarations.push_back(IfcLightEmissionSourceEnum_type);
    declarations.push_back(IfcLightFixtureTypeEnum_type);
    declarations.push_back(IfcLoadGroupTypeEnum_type);
    declarations.push_back(IfcLogicalOperatorEnum_type);
    declarations.push_back(IfcMemberTypeEnum_type);
    declarations.push_back(IfcMotorConnectionTypeEnum_type);
    declarations.push_back(IfcNullStyle_type);
    declarations.push_back(IfcObjectTypeEnum_type);
    declarations.push_back(IfcObjectiveEnum_type);
    declarations.push_back(IfcOccupantTypeEnum_type);
    declarations.push_back(IfcOutletTypeEnum_type);
    declarations.push_back(IfcPermeableCoveringOperationEnum_type);
    declarations.push_back(IfcPhysicalOrVirtualEnum_type);
    declarations.push_back(IfcPileConstructionEnum_type);
    declarations.push_back(IfcPileTypeEnum_type);
    declarations.push_back(IfcPipeFittingTypeEnum_type);
    declarations.push_back(IfcPipeSegmentTypeEnum_type);
    declarations.push_back(IfcPlateTypeEnum_type);
    declarations.push_back(IfcProcedureTypeEnum_type);
    declarations.push_back(IfcProfileTypeEnum_type);
    declarations.push_back(IfcProjectOrderRecordTypeEnum_type);
    declarations.push_back(IfcProjectOrderTypeEnum_type);
    declarations.push_back(IfcProjectedOrTrueLengthEnum_type);
    declarations.push_back(IfcPropertySourceEnum_type);
    declarations.push_back(IfcProtectiveDeviceTypeEnum_type);
    declarations.push_back(IfcPumpTypeEnum_type);
    declarations.push_back(IfcRailingTypeEnum_type);
    declarations.push_back(IfcRampFlightTypeEnum_type);
    declarations.push_back(IfcRampTypeEnum_type);
    declarations.push_back(IfcReflectanceMethodEnum_type);
    declarations.push_back(IfcReinforcingBarRoleEnum_type);
    declarations.push_back(IfcReinforcingBarSurfaceEnum_type);
    declarations.push_back(IfcResourceConsumptionEnum_type);
    declarations.push_back(IfcRibPlateDirectionEnum_type);
    declarations.push_back(IfcRoleEnum_type);
    declarations.push_back(IfcRoofTypeEnum_type);
    declarations.push_back(IfcSIPrefix_type);
    declarations.push_back(IfcSIUnitName_type);
    declarations.push_back(IfcSanitaryTerminalTypeEnum_type);
    declarations.push_back(IfcSectionTypeEnum_type);
    declarations.push_back(IfcSensorTypeEnum_type);
    declarations.push_back(IfcSequenceEnum_type);
    declarations.push_back(IfcServiceLifeFactorTypeEnum_type);
    declarations.push_back(IfcServiceLifeTypeEnum_type);
    declarations.push_back(IfcSlabTypeEnum_type);
    declarations.push_back(IfcSoundScaleEnum_type);
    declarations.push_back(IfcSpaceHeaterTypeEnum_type);
    declarations.push_back(IfcSpaceTypeEnum_type);
    declarations.push_back(IfcStackTerminalTypeEnum_type);
    declarations.push_back(IfcStairFlightTypeEnum_type);
    declarations.push_back(IfcStairTypeEnum_type);
    declarations.push_back(IfcStateEnum_type);
    declarations.push_back(IfcStructuralCurveTypeEnum_type);
    declarations.push_back(IfcStructuralSurfaceTypeEnum_type);
    declarations.push_back(IfcSurfaceSide_type);
    declarations.push_back(IfcSurfaceTextureEnum_type);
    declarations.push_back(IfcSwitchingDeviceTypeEnum_type);
    declarations.push_back(IfcTankTypeEnum_type);
    declarations.push_back(IfcTendonTypeEnum_type);
    declarations.push_back(IfcTextPath_type);
    declarations.push_back(IfcThermalLoadSourceEnum_type);
    declarations.push_back(IfcThermalLoadTypeEnum_type);
    declarations.push_back(IfcTimeSeriesDataTypeEnum_type);
    declarations.push_back(IfcTimeSeriesScheduleTypeEnum_type);
    declarations.push_back(IfcTransformerTypeEnum_type);
    declarations.push_back(IfcTransitionCode_type);
    declarations.push_back(IfcTransportElementTypeEnum_type);
    declarations.push_back(IfcTrimmingPreference_type);
    declarations.push_back(IfcTubeBundleTypeEnum_type);
    declarations.push_back(IfcUnitEnum_type);
    declarations.push_back(IfcUnitaryEquipmentTypeEnum_type);
    declarations.push_back(IfcValveTypeEnum_type);
    declarations.push_back(IfcVibrationIsolatorTypeEnum_type);
    declarations.push_back(IfcWallTypeEnum_type);
    declarations.push_back(IfcWasteTerminalTypeEnum_type);
    declarations.push_back(IfcWindowPanelOperationEnum_type);
    declarations.push_back(IfcWindowPanelPositionEnum_type);
    declarations.push_back(IfcWindowStyleConstructionEnum_type);
    declarations.push_back(IfcWindowStyleOperationEnum_type);
    declarations.push_back(IfcWorkControlTypeEnum_type);
    declarations.push_back(IfcActorRole_type);
    declarations.push_back(IfcAddress_type);
    declarations.push_back(IfcApplication_type);
    declarations.push_back(IfcAppliedValue_type);
    declarations.push_back(IfcAppliedValueRelationship_type);
    declarations.push_back(IfcApproval_type);
    declarations.push_back(IfcApprovalActorRelationship_type);
    declarations.push_back(IfcApprovalPropertyRelationship_type);
    declarations.push_back(IfcApprovalRelationship_type);
    declarations.push_back(IfcBoundaryCondition_type);
    declarations.push_back(IfcBoundaryEdgeCondition_type);
    declarations.push_back(IfcBoundaryFaceCondition_type);
    declarations.push_back(IfcBoundaryNodeCondition_type);
    declarations.push_back(IfcBoundaryNodeConditionWarping_type);
    declarations.push_back(IfcCalendarDate_type);
    declarations.push_back(IfcClassification_type);
    declarations.push_back(IfcClassificationItem_type);
    declarations.push_back(IfcClassificationItemRelationship_type);
    declarations.push_back(IfcClassificationNotation_type);
    declarations.push_back(IfcClassificationNotationFacet_type);
    declarations.push_back(IfcColourSpecification_type);
    declarations.push_back(IfcConnectionGeometry_type);
    declarations.push_back(IfcConnectionPointGeometry_type);
    declarations.push_back(IfcConnectionPortGeometry_type);
    declarations.push_back(IfcConnectionSurfaceGeometry_type);
    declarations.push_back(IfcConstraint_type);
    declarations.push_back(IfcConstraintAggregationRelationship_type);
    declarations.push_back(IfcConstraintClassificationRelationship_type);
    declarations.push_back(IfcConstraintRelationship_type);
    declarations.push_back(IfcCoordinatedUniversalTimeOffset_type);
    declarations.push_back(IfcCostValue_type);
    declarations.push_back(IfcCurrencyRelationship_type);
    declarations.push_back(IfcCurveStyleFont_type);
    declarations.push_back(IfcCurveStyleFontAndScaling_type);
    declarations.push_back(IfcCurveStyleFontPattern_type);
    declarations.push_back(IfcDateAndTime_type);
    declarations.push_back(IfcDerivedUnit_type);
    declarations.push_back(IfcDerivedUnitElement_type);
    declarations.push_back(IfcDimensionalExponents_type);
    declarations.push_back(IfcDocumentElectronicFormat_type);
    declarations.push_back(IfcDocumentInformation_type);
    declarations.push_back(IfcDocumentInformationRelationship_type);
    declarations.push_back(IfcDraughtingCalloutRelationship_type);
    declarations.push_back(IfcEnvironmentalImpactValue_type);
    declarations.push_back(IfcExternalReference_type);
    declarations.push_back(IfcExternallyDefinedHatchStyle_type);
    declarations.push_back(IfcExternallyDefinedSurfaceStyle_type);
    declarations.push_back(IfcExternallyDefinedSymbol_type);
    declarations.push_back(IfcExternallyDefinedTextFont_type);
    declarations.push_back(IfcGridAxis_type);
    declarations.push_back(IfcIrregularTimeSeriesValue_type);
    declarations.push_back(IfcLibraryInformation_type);
    declarations.push_back(IfcLibraryReference_type);
    declarations.push_back(IfcLightDistributionData_type);
    declarations.push_back(IfcLightIntensityDistribution_type);
    declarations.push_back(IfcLocalTime_type);
    declarations.push_back(IfcMaterial_type);
    declarations.push_back(IfcMaterialClassificationRelationship_type);
    declarations.push_back(IfcMaterialLayer_type);
    declarations.push_back(IfcMaterialLayerSet_type);
    declarations.push_back(IfcMaterialLayerSetUsage_type);
    declarations.push_back(IfcMaterialList_type);
    declarations.push_back(IfcMaterialProperties_type);
    declarations.push_back(IfcMeasureWithUnit_type);
    declarations.push_back(IfcMechanicalMaterialProperties_type);
    declarations.push_back(IfcMechanicalSteelMaterialProperties_type);
    declarations.push_back(IfcMetric_type);
    declarations.push_back(IfcMonetaryUnit_type);
    declarations.push_back(IfcNamedUnit_type);
    declarations.push_back(IfcObjectPlacement_type);
    declarations.push_back(IfcObjective_type);
    declarations.push_back(IfcOpticalMaterialProperties_type);
    declarations.push_back(IfcOrganization_type);
    declarations.push_back(IfcOrganizationRelationship_type);
    declarations.push_back(IfcOwnerHistory_type);
    declarations.push_back(IfcPerson_type);
    declarations.push_back(IfcPersonAndOrganization_type);
    declarations.push_back(IfcPhysicalQuantity_type);
    declarations.push_back(IfcPhysicalSimpleQuantity_type);
    declarations.push_back(IfcPostalAddress_type);
    declarations.push_back(IfcPreDefinedItem_type);
    declarations.push_back(IfcPreDefinedSymbol_type);
    declarations.push_back(IfcPreDefinedTerminatorSymbol_type);
    declarations.push_back(IfcPreDefinedTextFont_type);
    declarations.push_back(IfcPresentationLayerAssignment_type);
    declarations.push_back(IfcPresentationLayerWithStyle_type);
    declarations.push_back(IfcPresentationStyle_type);
    declarations.push_back(IfcPresentationStyleAssignment_type);
    declarations.push_back(IfcProductRepresentation_type);
    declarations.push_back(IfcProductsOfCombustionProperties_type);
    declarations.push_back(IfcProfileDef_type);
    declarations.push_back(IfcProfileProperties_type);
    declarations.push_back(IfcProperty_type);
    declarations.push_back(IfcPropertyConstraintRelationship_type);
    declarations.push_back(IfcPropertyDependencyRelationship_type);
    declarations.push_back(IfcPropertyEnumeration_type);
    declarations.push_back(IfcQuantityArea_type);
    declarations.push_back(IfcQuantityCount_type);
    declarations.push_back(IfcQuantityLength_type);
    declarations.push_back(IfcQuantityTime_type);
    declarations.push_back(IfcQuantityVolume_type);
    declarations.push_back(IfcQuantityWeight_type);
    declarations.push_back(IfcReferencesValueDocument_type);
    declarations.push_back(IfcReinforcementBarProperties_type);
    declarations.push_back(IfcRelaxation_type);
    declarations.push_back(IfcRepresentation_type);
    declarations.push_back(IfcRepresentationContext_type);
    declarations.push_back(IfcRepresentationItem_type);
    declarations.push_back(IfcRepresentationMap_type);
    declarations.push_back(IfcRibPlateProfileProperties_type);
    declarations.push_back(IfcRoot_type);
    declarations.push_back(IfcSIUnit_type);
    declarations.push_back(IfcSectionProperties_type);
    declarations.push_back(IfcSectionReinforcementProperties_type);
    declarations.push_back(IfcShapeAspect_type);
    declarations.push_back(IfcShapeModel_type);
    declarations.push_back(IfcShapeRepresentation_type);
    declarations.push_back(IfcSimpleProperty_type);
    declarations.push_back(IfcStructuralConnectionCondition_type);
    declarations.push_back(IfcStructuralLoad_type);
    declarations.push_back(IfcStructuralLoadStatic_type);
    declarations.push_back(IfcStructuralLoadTemperature_type);
    declarations.push_back(IfcStyleModel_type);
    declarations.push_back(IfcStyledItem_type);
    declarations.push_back(IfcStyledRepresentation_type);
    declarations.push_back(IfcSurfaceStyle_type);
    declarations.push_back(IfcSurfaceStyleLighting_type);
    declarations.push_back(IfcSurfaceStyleRefraction_type);
    declarations.push_back(IfcSurfaceStyleShading_type);
    declarations.push_back(IfcSurfaceStyleWithTextures_type);
    declarations.push_back(IfcSurfaceTexture_type);
    declarations.push_back(IfcSymbolStyle_type);
    declarations.push_back(IfcTable_type);
    declarations.push_back(IfcTableRow_type);
    declarations.push_back(IfcTelecomAddress_type);
    declarations.push_back(IfcTextStyle_type);
    declarations.push_back(IfcTextStyleFontModel_type);
    declarations.push_back(IfcTextStyleForDefinedFont_type);
    declarations.push_back(IfcTextStyleTextModel_type);
    declarations.push_back(IfcTextStyleWithBoxCharacteristics_type);
    declarations.push_back(IfcTextureCoordinate_type);
    declarations.push_back(IfcTextureCoordinateGenerator_type);
    declarations.push_back(IfcTextureMap_type);
    declarations.push_back(IfcTextureVertex_type);
    declarations.push_back(IfcThermalMaterialProperties_type);
    declarations.push_back(IfcTimeSeries_type);
    declarations.push_back(IfcTimeSeriesReferenceRelationship_type);
    declarations.push_back(IfcTimeSeriesValue_type);
    declarations.push_back(IfcTopologicalRepresentationItem_type);
    declarations.push_back(IfcTopologyRepresentation_type);
    declarations.push_back(IfcUnitAssignment_type);
    declarations.push_back(IfcVertex_type);
    declarations.push_back(IfcVertexBasedTextureMap_type);
    declarations.push_back(IfcVertexPoint_type);
    declarations.push_back(IfcVirtualGridIntersection_type);
    declarations.push_back(IfcWaterProperties_type);
    declarations.push_back(IfcAnnotationOccurrence_type);
    declarations.push_back(IfcAnnotationSurfaceOccurrence_type);
    declarations.push_back(IfcAnnotationSymbolOccurrence_type);
    declarations.push_back(IfcAnnotationTextOccurrence_type);
    declarations.push_back(IfcArbitraryClosedProfileDef_type);
    declarations.push_back(IfcArbitraryOpenProfileDef_type);
    declarations.push_back(IfcArbitraryProfileDefWithVoids_type);
    declarations.push_back(IfcBlobTexture_type);
    declarations.push_back(IfcCenterLineProfileDef_type);
    declarations.push_back(IfcClassificationReference_type);
    declarations.push_back(IfcColourRgb_type);
    declarations.push_back(IfcComplexProperty_type);
    declarations.push_back(IfcCompositeProfileDef_type);
    declarations.push_back(IfcConnectedFaceSet_type);
    declarations.push_back(IfcConnectionCurveGeometry_type);
    declarations.push_back(IfcConnectionPointEccentricity_type);
    declarations.push_back(IfcContextDependentUnit_type);
    declarations.push_back(IfcConversionBasedUnit_type);
    declarations.push_back(IfcCurveStyle_type);
    declarations.push_back(IfcDerivedProfileDef_type);
    declarations.push_back(IfcDimensionCalloutRelationship_type);
    declarations.push_back(IfcDimensionPair_type);
    declarations.push_back(IfcDocumentReference_type);
    declarations.push_back(IfcDraughtingPreDefinedTextFont_type);
    declarations.push_back(IfcEdge_type);
    declarations.push_back(IfcEdgeCurve_type);
    declarations.push_back(IfcExtendedMaterialProperties_type);
    declarations.push_back(IfcFace_type);
    declarations.push_back(IfcFaceBound_type);
    declarations.push_back(IfcFaceOuterBound_type);
    declarations.push_back(IfcFaceSurface_type);
    declarations.push_back(IfcFailureConnectionCondition_type);
    declarations.push_back(IfcFillAreaStyle_type);
    declarations.push_back(IfcFuelProperties_type);
    declarations.push_back(IfcGeneralMaterialProperties_type);
    declarations.push_back(IfcGeneralProfileProperties_type);
    declarations.push_back(IfcGeometricRepresentationContext_type);
    declarations.push_back(IfcGeometricRepresentationItem_type);
    declarations.push_back(IfcGeometricRepresentationSubContext_type);
    declarations.push_back(IfcGeometricSet_type);
    declarations.push_back(IfcGridPlacement_type);
    declarations.push_back(IfcHalfSpaceSolid_type);
    declarations.push_back(IfcHygroscopicMaterialProperties_type);
    declarations.push_back(IfcImageTexture_type);
    declarations.push_back(IfcIrregularTimeSeries_type);
    declarations.push_back(IfcLightSource_type);
    declarations.push_back(IfcLightSourceAmbient_type);
    declarations.push_back(IfcLightSourceDirectional_type);
    declarations.push_back(IfcLightSourceGoniometric_type);
    declarations.push_back(IfcLightSourcePositional_type);
    declarations.push_back(IfcLightSourceSpot_type);
    declarations.push_back(IfcLocalPlacement_type);
    declarations.push_back(IfcLoop_type);
    declarations.push_back(IfcMappedItem_type);
    declarations.push_back(IfcMaterialDefinitionRepresentation_type);
    declarations.push_back(IfcMechanicalConcreteMaterialProperties_type);
    declarations.push_back(IfcObjectDefinition_type);
    declarations.push_back(IfcOneDirectionRepeatFactor_type);
    declarations.push_back(IfcOpenShell_type);
    declarations.push_back(IfcOrientedEdge_type);
    declarations.push_back(IfcParameterizedProfileDef_type);
    declarations.push_back(IfcPath_type);
    declarations.push_back(IfcPhysicalComplexQuantity_type);
    declarations.push_back(IfcPixelTexture_type);
    declarations.push_back(IfcPlacement_type);
    declarations.push_back(IfcPlanarExtent_type);
    declarations.push_back(IfcPoint_type);
    declarations.push_back(IfcPointOnCurve_type);
    declarations.push_back(IfcPointOnSurface_type);
    declarations.push_back(IfcPolyLoop_type);
    declarations.push_back(IfcPolygonalBoundedHalfSpace_type);
    declarations.push_back(IfcPreDefinedColour_type);
    declarations.push_back(IfcPreDefinedCurveFont_type);
    declarations.push_back(IfcPreDefinedDimensionSymbol_type);
    declarations.push_back(IfcPreDefinedPointMarkerSymbol_type);
    declarations.push_back(IfcProductDefinitionShape_type);
    declarations.push_back(IfcPropertyBoundedValue_type);
    declarations.push_back(IfcPropertyDefinition_type);
    declarations.push_back(IfcPropertyEnumeratedValue_type);
    declarations.push_back(IfcPropertyListValue_type);
    declarations.push_back(IfcPropertyReferenceValue_type);
    declarations.push_back(IfcPropertySetDefinition_type);
    declarations.push_back(IfcPropertySingleValue_type);
    declarations.push_back(IfcPropertyTableValue_type);
    declarations.push_back(IfcRectangleProfileDef_type);
    declarations.push_back(IfcRegularTimeSeries_type);
    declarations.push_back(IfcReinforcementDefinitionProperties_type);
    declarations.push_back(IfcRelationship_type);
    declarations.push_back(IfcRoundedRectangleProfileDef_type);
    declarations.push_back(IfcSectionedSpine_type);
    declarations.push_back(IfcServiceLifeFactor_type);
    declarations.push_back(IfcShellBasedSurfaceModel_type);
    declarations.push_back(IfcSlippageConnectionCondition_type);
    declarations.push_back(IfcSolidModel_type);
    declarations.push_back(IfcSoundProperties_type);
    declarations.push_back(IfcSoundValue_type);
    declarations.push_back(IfcSpaceThermalLoadProperties_type);
    declarations.push_back(IfcStructuralLoadLinearForce_type);
    declarations.push_back(IfcStructuralLoadPlanarForce_type);
    declarations.push_back(IfcStructuralLoadSingleDisplacement_type);
    declarations.push_back(IfcStructuralLoadSingleDisplacementDistortion_type);
    declarations.push_back(IfcStructuralLoadSingleForce_type);
    declarations.push_back(IfcStructuralLoadSingleForceWarping_type);
    declarations.push_back(IfcStructuralProfileProperties_type);
    declarations.push_back(IfcStructuralSteelProfileProperties_type);
    declarations.push_back(IfcSubedge_type);
    declarations.push_back(IfcSurface_type);
    declarations.push_back(IfcSurfaceStyleRendering_type);
    declarations.push_back(IfcSweptAreaSolid_type);
    declarations.push_back(IfcSweptDiskSolid_type);
    declarations.push_back(IfcSweptSurface_type);
    declarations.push_back(IfcTShapeProfileDef_type);
    declarations.push_back(IfcTerminatorSymbol_type);
    declarations.push_back(IfcTextLiteral_type);
    declarations.push_back(IfcTextLiteralWithExtent_type);
    declarations.push_back(IfcTrapeziumProfileDef_type);
    declarations.push_back(IfcTwoDirectionRepeatFactor_type);
    declarations.push_back(IfcTypeObject_type);
    declarations.push_back(IfcTypeProduct_type);
    declarations.push_back(IfcUShapeProfileDef_type);
    declarations.push_back(IfcVector_type);
    declarations.push_back(IfcVertexLoop_type);
    declarations.push_back(IfcWindowLiningProperties_type);
    declarations.push_back(IfcWindowPanelProperties_type);
    declarations.push_back(IfcWindowStyle_type);
    declarations.push_back(IfcZShapeProfileDef_type);
    declarations.push_back(IfcAnnotationCurveOccurrence_type);
    declarations.push_back(IfcAnnotationFillArea_type);
    declarations.push_back(IfcAnnotationFillAreaOccurrence_type);
    declarations.push_back(IfcAnnotationSurface_type);
    declarations.push_back(IfcAxis1Placement_type);
    declarations.push_back(IfcAxis2Placement2D_type);
    declarations.push_back(IfcAxis2Placement3D_type);
    declarations.push_back(IfcBooleanResult_type);
    declarations.push_back(IfcBoundedSurface_type);
    declarations.push_back(IfcBoundingBox_type);
    declarations.push_back(IfcBoxedHalfSpace_type);
    declarations.push_back(IfcCShapeProfileDef_type);
    declarations.push_back(IfcCartesianPoint_type);
    declarations.push_back(IfcCartesianTransformationOperator_type);
    declarations.push_back(IfcCartesianTransformationOperator2D_type);
    declarations.push_back(IfcCartesianTransformationOperator2DnonUniform_type);
    declarations.push_back(IfcCartesianTransformationOperator3D_type);
    declarations.push_back(IfcCartesianTransformationOperator3DnonUniform_type);
    declarations.push_back(IfcCircleProfileDef_type);
    declarations.push_back(IfcClosedShell_type);
    declarations.push_back(IfcCompositeCurveSegment_type);
    declarations.push_back(IfcCraneRailAShapeProfileDef_type);
    declarations.push_back(IfcCraneRailFShapeProfileDef_type);
    declarations.push_back(IfcCsgPrimitive3D_type);
    declarations.push_back(IfcCsgSolid_type);
    declarations.push_back(IfcCurve_type);
    declarations.push_back(IfcCurveBoundedPlane_type);
    declarations.push_back(IfcDefinedSymbol_type);
    declarations.push_back(IfcDimensionCurve_type);
    declarations.push_back(IfcDimensionCurveTerminator_type);
    declarations.push_back(IfcDirection_type);
    declarations.push_back(IfcDoorLiningProperties_type);
    declarations.push_back(IfcDoorPanelProperties_type);
    declarations.push_back(IfcDoorStyle_type);
    declarations.push_back(IfcDraughtingCallout_type);
    declarations.push_back(IfcDraughtingPreDefinedColour_type);
    declarations.push_back(IfcDraughtingPreDefinedCurveFont_type);
    declarations.push_back(IfcEdgeLoop_type);
    declarations.push_back(IfcElementQuantity_type);
    declarations.push_back(IfcElementType_type);
    declarations.push_back(IfcElementarySurface_type);
    declarations.push_back(IfcEllipseProfileDef_type);
    declarations.push_back(IfcEnergyProperties_type);
    declarations.push_back(IfcExtrudedAreaSolid_type);
    declarations.push_back(IfcFaceBasedSurfaceModel_type);
    declarations.push_back(IfcFillAreaStyleHatching_type);
    declarations.push_back(IfcFillAreaStyleTileSymbolWithStyle_type);
    declarations.push_back(IfcFillAreaStyleTiles_type);
    declarations.push_back(IfcFluidFlowProperties_type);
    declarations.push_back(IfcFurnishingElementType_type);
    declarations.push_back(IfcFurnitureType_type);
    declarations.push_back(IfcGeometricCurveSet_type);
    declarations.push_back(IfcIShapeProfileDef_type);
    declarations.push_back(IfcLShapeProfileDef_type);
    declarations.push_back(IfcLine_type);
    declarations.push_back(IfcManifoldSolidBrep_type);
    declarations.push_back(IfcObject_type);
    declarations.push_back(IfcOffsetCurve2D_type);
    declarations.push_back(IfcOffsetCurve3D_type);
    declarations.push_back(IfcPermeableCoveringProperties_type);
    declarations.push_back(IfcPlanarBox_type);
    declarations.push_back(IfcPlane_type);
    declarations.push_back(IfcProcess_type);
    declarations.push_back(IfcProduct_type);
    declarations.push_back(IfcProject_type);
    declarations.push_back(IfcProjectionCurve_type);
    declarations.push_back(IfcPropertySet_type);
    declarations.push_back(IfcProxy_type);
    declarations.push_back(IfcRectangleHollowProfileDef_type);
    declarations.push_back(IfcRectangularPyramid_type);
    declarations.push_back(IfcRectangularTrimmedSurface_type);
    declarations.push_back(IfcRelAssigns_type);
    declarations.push_back(IfcRelAssignsToActor_type);
    declarations.push_back(IfcRelAssignsToControl_type);
    declarations.push_back(IfcRelAssignsToGroup_type);
    declarations.push_back(IfcRelAssignsToProcess_type);
    declarations.push_back(IfcRelAssignsToProduct_type);
    declarations.push_back(IfcRelAssignsToProjectOrder_type);
    declarations.push_back(IfcRelAssignsToResource_type);
    declarations.push_back(IfcRelAssociates_type);
    declarations.push_back(IfcRelAssociatesAppliedValue_type);
    declarations.push_back(IfcRelAssociatesApproval_type);
    declarations.push_back(IfcRelAssociatesClassification_type);
    declarations.push_back(IfcRelAssociatesConstraint_type);
    declarations.push_back(IfcRelAssociatesDocument_type);
    declarations.push_back(IfcRelAssociatesLibrary_type);
    declarations.push_back(IfcRelAssociatesMaterial_type);
    declarations.push_back(IfcRelAssociatesProfileProperties_type);
    declarations.push_back(IfcRelConnects_type);
    declarations.push_back(IfcRelConnectsElements_type);
    declarations.push_back(IfcRelConnectsPathElements_type);
    declarations.push_back(IfcRelConnectsPortToElement_type);
    declarations.push_back(IfcRelConnectsPorts_type);
    declarations.push_back(IfcRelConnectsStructuralActivity_type);
    declarations.push_back(IfcRelConnectsStructuralElement_type);
    declarations.push_back(IfcRelConnectsStructuralMember_type);
    declarations.push_back(IfcRelConnectsWithEccentricity_type);
    declarations.push_back(IfcRelConnectsWithRealizingElements_type);
    declarations.push_back(IfcRelContainedInSpatialStructure_type);
    declarations.push_back(IfcRelCoversBldgElements_type);
    declarations.push_back(IfcRelCoversSpaces_type);
    declarations.push_back(IfcRelDecomposes_type);
    declarations.push_back(IfcRelDefines_type);
    declarations.push_back(IfcRelDefinesByProperties_type);
    declarations.push_back(IfcRelDefinesByType_type);
    declarations.push_back(IfcRelFillsElement_type);
    declarations.push_back(IfcRelFlowControlElements_type);
    declarations.push_back(IfcRelInteractionRequirements_type);
    declarations.push_back(IfcRelNests_type);
    declarations.push_back(IfcRelOccupiesSpaces_type);
    declarations.push_back(IfcRelOverridesProperties_type);
    declarations.push_back(IfcRelProjectsElement_type);
    declarations.push_back(IfcRelReferencedInSpatialStructure_type);
    declarations.push_back(IfcRelSchedulesCostItems_type);
    declarations.push_back(IfcRelSequence_type);
    declarations.push_back(IfcRelServicesBuildings_type);
    declarations.push_back(IfcRelSpaceBoundary_type);
    declarations.push_back(IfcRelVoidsElement_type);
    declarations.push_back(IfcResource_type);
    declarations.push_back(IfcRevolvedAreaSolid_type);
    declarations.push_back(IfcRightCircularCone_type);
    declarations.push_back(IfcRightCircularCylinder_type);
    declarations.push_back(IfcSpatialStructureElement_type);
    declarations.push_back(IfcSpatialStructureElementType_type);
    declarations.push_back(IfcSphere_type);
    declarations.push_back(IfcStructuralActivity_type);
    declarations.push_back(IfcStructuralItem_type);
    declarations.push_back(IfcStructuralMember_type);
    declarations.push_back(IfcStructuralReaction_type);
    declarations.push_back(IfcStructuralSurfaceMember_type);
    declarations.push_back(IfcStructuralSurfaceMemberVarying_type);
    declarations.push_back(IfcStructuredDimensionCallout_type);
    declarations.push_back(IfcSurfaceCurveSweptAreaSolid_type);
    declarations.push_back(IfcSurfaceOfLinearExtrusion_type);
    declarations.push_back(IfcSurfaceOfRevolution_type);
    declarations.push_back(IfcSystemFurnitureElementType_type);
    declarations.push_back(IfcTask_type);
    declarations.push_back(IfcTransportElementType_type);
    declarations.push_back(IfcActor_type);
    declarations.push_back(IfcAnnotation_type);
    declarations.push_back(IfcAsymmetricIShapeProfileDef_type);
    declarations.push_back(IfcBlock_type);
    declarations.push_back(IfcBooleanClippingResult_type);
    declarations.push_back(IfcBoundedCurve_type);
    declarations.push_back(IfcBuilding_type);
    declarations.push_back(IfcBuildingElementType_type);
    declarations.push_back(IfcBuildingStorey_type);
    declarations.push_back(IfcCircleHollowProfileDef_type);
    declarations.push_back(IfcColumnType_type);
    declarations.push_back(IfcCompositeCurve_type);
    declarations.push_back(IfcConic_type);
    declarations.push_back(IfcConstructionResource_type);
    declarations.push_back(IfcControl_type);
    declarations.push_back(IfcCostItem_type);
    declarations.push_back(IfcCostSchedule_type);
    declarations.push_back(IfcCoveringType_type);
    declarations.push_back(IfcCrewResource_type);
    declarations.push_back(IfcCurtainWallType_type);
    declarations.push_back(IfcDimensionCurveDirectedCallout_type);
    declarations.push_back(IfcDistributionElementType_type);
    declarations.push_back(IfcDistributionFlowElementType_type);
    declarations.push_back(IfcElectricalBaseProperties_type);
    declarations.push_back(IfcElement_type);
    declarations.push_back(IfcElementAssembly_type);
    declarations.push_back(IfcElementComponent_type);
    declarations.push_back(IfcElementComponentType_type);
    declarations.push_back(IfcEllipse_type);
    declarations.push_back(IfcEnergyConversionDeviceType_type);
    declarations.push_back(IfcEquipmentElement_type);
    declarations.push_back(IfcEquipmentStandard_type);
    declarations.push_back(IfcEvaporativeCoolerType_type);
    declarations.push_back(IfcEvaporatorType_type);
    declarations.push_back(IfcFacetedBrep_type);
    declarations.push_back(IfcFacetedBrepWithVoids_type);
    declarations.push_back(IfcFastener_type);
    declarations.push_back(IfcFastenerType_type);
    declarations.push_back(IfcFeatureElement_type);
    declarations.push_back(IfcFeatureElementAddition_type);
    declarations.push_back(IfcFeatureElementSubtraction_type);
    declarations.push_back(IfcFlowControllerType_type);
    declarations.push_back(IfcFlowFittingType_type);
    declarations.push_back(IfcFlowMeterType_type);
    declarations.push_back(IfcFlowMovingDeviceType_type);
    declarations.push_back(IfcFlowSegmentType_type);
    declarations.push_back(IfcFlowStorageDeviceType_type);
    declarations.push_back(IfcFlowTerminalType_type);
    declarations.push_back(IfcFlowTreatmentDeviceType_type);
    declarations.push_back(IfcFurnishingElement_type);
    declarations.push_back(IfcFurnitureStandard_type);
    declarations.push_back(IfcGasTerminalType_type);
    declarations.push_back(IfcGrid_type);
    declarations.push_back(IfcGroup_type);
    declarations.push_back(IfcHeatExchangerType_type);
    declarations.push_back(IfcHumidifierType_type);
    declarations.push_back(IfcInventory_type);
    declarations.push_back(IfcJunctionBoxType_type);
    declarations.push_back(IfcLaborResource_type);
    declarations.push_back(IfcLampType_type);
    declarations.push_back(IfcLightFixtureType_type);
    declarations.push_back(IfcLinearDimension_type);
    declarations.push_back(IfcMechanicalFastener_type);
    declarations.push_back(IfcMechanicalFastenerType_type);
    declarations.push_back(IfcMemberType_type);
    declarations.push_back(IfcMotorConnectionType_type);
    declarations.push_back(IfcMove_type);
    declarations.push_back(IfcOccupant_type);
    declarations.push_back(IfcOpeningElement_type);
    declarations.push_back(IfcOrderAction_type);
    declarations.push_back(IfcOutletType_type);
    declarations.push_back(IfcPerformanceHistory_type);
    declarations.push_back(IfcPermit_type);
    declarations.push_back(IfcPipeFittingType_type);
    declarations.push_back(IfcPipeSegmentType_type);
    declarations.push_back(IfcPlateType_type);
    declarations.push_back(IfcPolyline_type);
    declarations.push_back(IfcPort_type);
    declarations.push_back(IfcProcedure_type);
    declarations.push_back(IfcProjectOrder_type);
    declarations.push_back(IfcProjectOrderRecord_type);
    declarations.push_back(IfcProjectionElement_type);
    declarations.push_back(IfcProtectiveDeviceType_type);
    declarations.push_back(IfcPumpType_type);
    declarations.push_back(IfcRadiusDimension_type);
    declarations.push_back(IfcRailingType_type);
    declarations.push_back(IfcRampFlightType_type);
    declarations.push_back(IfcRelAggregates_type);
    declarations.push_back(IfcRelAssignsTasks_type);
    declarations.push_back(IfcSanitaryTerminalType_type);
    declarations.push_back(IfcScheduleTimeControl_type);
    declarations.push_back(IfcServiceLife_type);
    declarations.push_back(IfcSite_type);
    declarations.push_back(IfcSlabType_type);
    declarations.push_back(IfcSpace_type);
    declarations.push_back(IfcSpaceHeaterType_type);
    declarations.push_back(IfcSpaceProgram_type);
    declarations.push_back(IfcSpaceType_type);
    declarations.push_back(IfcStackTerminalType_type);
    declarations.push_back(IfcStairFlightType_type);
    declarations.push_back(IfcStructuralAction_type);
    declarations.push_back(IfcStructuralConnection_type);
    declarations.push_back(IfcStructuralCurveConnection_type);
    declarations.push_back(IfcStructuralCurveMember_type);
    declarations.push_back(IfcStructuralCurveMemberVarying_type);
    declarations.push_back(IfcStructuralLinearAction_type);
    declarations.push_back(IfcStructuralLinearActionVarying_type);
    declarations.push_back(IfcStructuralLoadGroup_type);
    declarations.push_back(IfcStructuralPlanarAction_type);
    declarations.push_back(IfcStructuralPlanarActionVarying_type);
    declarations.push_back(IfcStructuralPointAction_type);
    declarations.push_back(IfcStructuralPointConnection_type);
    declarations.push_back(IfcStructuralPointReaction_type);
    declarations.push_back(IfcStructuralResultGroup_type);
    declarations.push_back(IfcStructuralSurfaceConnection_type);
    declarations.push_back(IfcSubContractResource_type);
    declarations.push_back(IfcSwitchingDeviceType_type);
    declarations.push_back(IfcSystem_type);
    declarations.push_back(IfcTankType_type);
    declarations.push_back(IfcTimeSeriesSchedule_type);
    declarations.push_back(IfcTransformerType_type);
    declarations.push_back(IfcTransportElement_type);
    declarations.push_back(IfcTrimmedCurve_type);
    declarations.push_back(IfcTubeBundleType_type);
    declarations.push_back(IfcUnitaryEquipmentType_type);
    declarations.push_back(IfcValveType_type);
    declarations.push_back(IfcVirtualElement_type);
    declarations.push_back(IfcWallType_type);
    declarations.push_back(IfcWasteTerminalType_type);
    declarations.push_back(IfcWorkControl_type);
    declarations.push_back(IfcWorkPlan_type);
    declarations.push_back(IfcWorkSchedule_type);
    declarations.push_back(IfcZone_type);
    declarations.push_back(Ifc2DCompositeCurve_type);
    declarations.push_back(IfcActionRequest_type);
    declarations.push_back(IfcAirTerminalBoxType_type);
    declarations.push_back(IfcAirTerminalType_type);
    declarations.push_back(IfcAirToAirHeatRecoveryType_type);
    declarations.push_back(IfcAngularDimension_type);
    declarations.push_back(IfcAsset_type);
    declarations.push_back(IfcBSplineCurve_type);
    declarations.push_back(IfcBeamType_type);
    declarations.push_back(IfcBezierCurve_type);
    declarations.push_back(IfcBoilerType_type);
    declarations.push_back(IfcBuildingElement_type);
    declarations.push_back(IfcBuildingElementComponent_type);
    declarations.push_back(IfcBuildingElementPart_type);
    declarations.push_back(IfcBuildingElementProxy_type);
    declarations.push_back(IfcBuildingElementProxyType_type);
    declarations.push_back(IfcCableCarrierFittingType_type);
    declarations.push_back(IfcCableCarrierSegmentType_type);
    declarations.push_back(IfcCableSegmentType_type);
    declarations.push_back(IfcChillerType_type);
    declarations.push_back(IfcCircle_type);
    declarations.push_back(IfcCoilType_type);
    declarations.push_back(IfcColumn_type);
    declarations.push_back(IfcCompressorType_type);
    declarations.push_back(IfcCondenserType_type);
    declarations.push_back(IfcCondition_type);
    declarations.push_back(IfcConditionCriterion_type);
    declarations.push_back(IfcConstructionEquipmentResource_type);
    declarations.push_back(IfcConstructionMaterialResource_type);
    declarations.push_back(IfcConstructionProductResource_type);
    declarations.push_back(IfcCooledBeamType_type);
    declarations.push_back(IfcCoolingTowerType_type);
    declarations.push_back(IfcCovering_type);
    declarations.push_back(IfcCurtainWall_type);
    declarations.push_back(IfcDamperType_type);
    declarations.push_back(IfcDiameterDimension_type);
    declarations.push_back(IfcDiscreteAccessory_type);
    declarations.push_back(IfcDiscreteAccessoryType_type);
    declarations.push_back(IfcDistributionChamberElementType_type);
    declarations.push_back(IfcDistributionControlElementType_type);
    declarations.push_back(IfcDistributionElement_type);
    declarations.push_back(IfcDistributionFlowElement_type);
    declarations.push_back(IfcDistributionPort_type);
    declarations.push_back(IfcDoor_type);
    declarations.push_back(IfcDuctFittingType_type);
    declarations.push_back(IfcDuctSegmentType_type);
    declarations.push_back(IfcDuctSilencerType_type);
    declarations.push_back(IfcEdgeFeature_type);
    declarations.push_back(IfcElectricApplianceType_type);
    declarations.push_back(IfcElectricFlowStorageDeviceType_type);
    declarations.push_back(IfcElectricGeneratorType_type);
    declarations.push_back(IfcElectricHeaterType_type);
    declarations.push_back(IfcElectricMotorType_type);
    declarations.push_back(IfcElectricTimeControlType_type);
    declarations.push_back(IfcElectricalCircuit_type);
    declarations.push_back(IfcElectricalElement_type);
    declarations.push_back(IfcEnergyConversionDevice_type);
    declarations.push_back(IfcFanType_type);
    declarations.push_back(IfcFilterType_type);
    declarations.push_back(IfcFireSuppressionTerminalType_type);
    declarations.push_back(IfcFlowController_type);
    declarations.push_back(IfcFlowFitting_type);
    declarations.push_back(IfcFlowInstrumentType_type);
    declarations.push_back(IfcFlowMovingDevice_type);
    declarations.push_back(IfcFlowSegment_type);
    declarations.push_back(IfcFlowStorageDevice_type);
    declarations.push_back(IfcFlowTerminal_type);
    declarations.push_back(IfcFlowTreatmentDevice_type);
    declarations.push_back(IfcFooting_type);
    declarations.push_back(IfcMember_type);
    declarations.push_back(IfcPile_type);
    declarations.push_back(IfcPlate_type);
    declarations.push_back(IfcRailing_type);
    declarations.push_back(IfcRamp_type);
    declarations.push_back(IfcRampFlight_type);
    declarations.push_back(IfcRationalBezierCurve_type);
    declarations.push_back(IfcReinforcingElement_type);
    declarations.push_back(IfcReinforcingMesh_type);
    declarations.push_back(IfcRoof_type);
    declarations.push_back(IfcRoundedEdgeFeature_type);
    declarations.push_back(IfcSensorType_type);
    declarations.push_back(IfcSlab_type);
    declarations.push_back(IfcStair_type);
    declarations.push_back(IfcStairFlight_type);
    declarations.push_back(IfcStructuralAnalysisModel_type);
    declarations.push_back(IfcTendon_type);
    declarations.push_back(IfcTendonAnchor_type);
    declarations.push_back(IfcVibrationIsolatorType_type);
    declarations.push_back(IfcWall_type);
    declarations.push_back(IfcWallStandardCase_type);
    declarations.push_back(IfcWindow_type);
    declarations.push_back(IfcActuatorType_type);
    declarations.push_back(IfcAlarmType_type);
    declarations.push_back(IfcBeam_type);
    declarations.push_back(IfcChamferEdgeFeature_type);
    declarations.push_back(IfcControllerType_type);
    declarations.push_back(IfcDistributionChamberElement_type);
    declarations.push_back(IfcDistributionControlElement_type);
    declarations.push_back(IfcElectricDistributionPoint_type);
    declarations.push_back(IfcReinforcingBar_type);
    declarations.push_back(IfcActorSelect_type);
    declarations.push_back(IfcAppliedValueSelect_type);
    declarations.push_back(IfcAxis2Placement_type);
    declarations.push_back(IfcBooleanOperand_type);
    declarations.push_back(IfcCharacterStyleSelect_type);
    declarations.push_back(IfcClassificationNotationSelect_type);
    declarations.push_back(IfcColour_type);
    declarations.push_back(IfcColourOrFactor_type);
    declarations.push_back(IfcConditionCriterionSelect_type);
    declarations.push_back(IfcCsgSelect_type);
    declarations.push_back(IfcCurveOrEdgeCurve_type);
    declarations.push_back(IfcCurveStyleFontSelect_type);
    declarations.push_back(IfcDateTimeSelect_type);
    declarations.push_back(IfcDefinedSymbolSelect_type);
    declarations.push_back(IfcDerivedMeasureValue_type);
    declarations.push_back(IfcDocumentSelect_type);
    declarations.push_back(IfcDraughtingCalloutElement_type);
    declarations.push_back(IfcFillAreaStyleTileShapeSelect_type);
    declarations.push_back(IfcFillStyleSelect_type);
    declarations.push_back(IfcGeometricSetSelect_type);
    declarations.push_back(IfcHatchLineDistanceSelect_type);
    declarations.push_back(IfcLayeredItem_type);
    declarations.push_back(IfcLibrarySelect_type);
    declarations.push_back(IfcLightDistributionDataSourceSelect_type);
    declarations.push_back(IfcMaterialSelect_type);
    declarations.push_back(IfcMeasureValue_type);
    declarations.push_back(IfcMetricValueSelect_type);
    declarations.push_back(IfcObjectReferenceSelect_type);
    declarations.push_back(IfcOrientationSelect_type);
    declarations.push_back(IfcPointOrVertexPoint_type);
    declarations.push_back(IfcPresentationStyleSelect_type);
    declarations.push_back(IfcShell_type);
    declarations.push_back(IfcSimpleValue_type);
    declarations.push_back(IfcSizeSelect_type);
    declarations.push_back(IfcSpecularHighlightSelect_type);
    declarations.push_back(IfcStructuralActivityAssignmentSelect_type);
    declarations.push_back(IfcSurfaceOrFaceSurface_type);
    declarations.push_back(IfcSurfaceStyleElementSelect_type);
    declarations.push_back(IfcSymbolStyleSelect_type);
    declarations.push_back(IfcTextFontSelect_type);
    declarations.push_back(IfcTextStyleSelect_type);
    declarations.push_back(IfcTrimmingSelect_type);
    declarations.push_back(IfcUnit_type);
    declarations.push_back(IfcValue_type);
    declarations.push_back(IfcVectorOrDirection_type);
    declarations.push_back(IfcCurveFontOrScaledCurveFontSelect_type);
    return new schema_definition("IFC2X3", declarations, new IFC2X3_instance_factory());
}


#ifdef _MSC_VER
#pragma optimize("", on)
#endif
        
namespace IFC2X3 {
const schema_definition& get_schema() {

    static const schema_definition* s = populate_schema();
    return *s;
}
}

